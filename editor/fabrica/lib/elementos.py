# elementos.py — "peças" de um estilo (escrito do zero pro Estúdio de Vídeos).
# 1) detectar(): olha quadros da referência com OCR local (rapidocr, grátis) e descobre quais peças gráficas ela usa
#    (título de abertura, etiqueta de nome/lugar, caixinha de número/data, crédito da imagem, marca do canal, legenda,
#    tipo de transição) + cor de fundo, cor do texto e posição de cada uma. Só guarda números e cores, nunca texto da referência.
# 2) itens_*(): desenha essas peças no edit.json com as cores do estilo (usado por preencher_preset.py e video_imagens.py).
# 3) previa(): imagem "assim vai ficar" pro cartão do estilo (lado a lado com os quadros da referência).
import colorsys
import re
import subprocess
from pathlib import Path
from urllib.parse import urlparse

import numpy as np
from PIL import Image, ImageDraw, ImageFont

NOWIN = getattr(subprocess, "CREATE_NO_WINDOW", 0)

NOMES = {   # tipo → (nome na tela, explicação curta pro leigo)
    "titulo": ("Título de abertura", "Texto grande no começo do vídeo"),
    "etiqueta": ("Etiqueta de nome/lugar", "Plaquinha com o nome de uma pessoa ou lugar citado"),
    "numero": ("Caixinha de número/data", "Aparece quando a narração fala um ano, preço ou número"),
    "credito": ("Crédito da imagem", "Letrinha no canto dizendo de onde veio a foto"),
    "selo": ("Marca do canal", "Nome do canal fixo num canto"),
    "legenda": ("Legenda", "As palavras da narração na tela"),
    "transicao": ("Transição", "Como uma cena passa pra outra"),
}
TRANSICOES = {"flash": "Piscada branca", "seco": "Corte seco", "suave": "Suave (esmaece)"}


# ------------------------------------------------------------------ detecção
_OCR = None


def _ocr():
    global _OCR
    if _OCR is None:
        from rapidocr_onnxruntime import RapidOCR   # opcional: sem ele a detecção só devolve legenda/transição
        _OCR = RapidOCR()
    return _OCR


def _quadro(video, t, dst: Path, largura=640):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(video), "-frames:v", "1", "-vf", f"scale={largura}:-2,format=yuvj420p", str(dst)],
                   capture_output=True, creationflags=NOWIN)
    return dst if dst.exists() else None


def _hex(rgb):
    r, g, b = [int(max(0, min(255, v))) for v in rgb]
    return f"#{r:02x}{g:02x}{b:02x}"


def _cores_caixa(arr, x0, y0, x1, y1):
    """Fundo (anel em volta do texto) e cor do texto. Anel uniforme = o texto está numa caixa/etiqueta."""
    H, W, _ = arr.shape
    m = max(3, int((y1 - y0) * 0.35))
    X0, Y0, X1, Y1 = max(0, x0 - m), max(0, y0 - m), min(W, x1 + m), min(H, y1 + m)
    reg = arr[Y0:Y1, X0:X1].reshape(-1, 3).astype(np.float32)
    dentro = np.zeros((Y1 - Y0, X1 - X0), bool)
    dentro[y0 - Y0:y1 - Y0, x0 - X0:x1 - X0] = True
    anel = reg[~dentro.reshape(-1)]
    if len(anel) < 10:
        return None, "#ffffff", False
    fundo = np.median(anel, axis=0)
    unif = float(np.mean(np.std(anel, axis=0))) < 22
    txt = arr[y0:y1, x0:x1].reshape(-1, 3).astype(np.float32)
    if not len(txt):
        return _hex(fundo), "#ffffff", unif
    dist = np.linalg.norm(txt - fundo, axis=1)
    longe = txt[dist >= np.percentile(dist, 80)]
    return _hex(fundo), _hex(np.median(longe, axis=0)), unif


def _transicao(video, dur):
    """Piscadas brancas = flash; troca brusca = seco; troca espalhada por vários quadros = suave."""
    fps, W, H = 8, 32, 18
    r = subprocess.run(["ffmpeg", "-v", "error", "-t", f"{min(dur, 120):.1f}", "-i", str(video), "-an", "-vf", f"fps={fps},scale={W}:{H},format=gray",
                        "-f", "rawvideo", "-"], capture_output=True, creationflags=NOWIN)
    n = len(r.stdout) // (W * H)
    if n < 10:
        return None
    f = np.frombuffer(r.stdout[: n * W * H], dtype=np.uint8).reshape(n, H, W).astype(np.float32)
    lum = f.mean(axis=(1, 2))
    flashes = sum(1 for i in range(1, n - 1) if lum[i] > 200 and lum[i] - lum[i - 1] > 50)
    d = np.abs(np.diff(f, axis=0)).mean(axis=(1, 2))
    thr = max(12.0, float(np.median(d)) * 4)
    picos = [i for i in range(len(d)) if d[i] >= thr]
    if flashes >= 3:
        return "flash"
    if not picos:
        return "seco"
    espalhado = sum(1 for i in picos if (i > 0 and d[i - 1] >= thr * 0.45) or (i + 1 < len(d) and d[i + 1] >= thr * 0.45))
    return "suave" if espalhado / len(picos) > 0.5 else "seco"


def detectar(video, dur, pasta: Path, vertical=False, prog=None):
    """Lista de peças da referência: [{tipo, nome, dica, vezes, cor_fundo, cor_texto, caixa, x, y, tam, ligado}]."""
    pasta.mkdir(exist_ok=True)
    tempos = [0.5, 1.6, 3.2] + [dur * (k + 0.5) / 18 for k in range(18)]
    caixas, n_q = [], 0
    try:
        ocr = _ocr()
    except Exception:
        ocr = None
    if ocr:
        for k, t in enumerate(tempos):
            if t >= dur:
                continue
            if prog and k % 6 == 0:
                prog(k / len(tempos))
            f = _quadro(video, t, pasta / f"e{k:02d}.jpg", 480 if not vertical else 360)
            if not f:
                continue
            n_q += 1
            arr = np.asarray(Image.open(f).convert("RGB"))
            H, W, _ = arr.shape
            try:
                res, _ = ocr(str(f), use_cls=False)
            except Exception:
                res = None
            for pts, txt, sc in res or []:
                if float(sc) < 0.6 or len(txt.strip()) < 2:
                    continue
                xs, ys = [p[0] for p in pts], [p[1] for p in pts]
                x0, y0, x1, y1 = int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))
                fundo, cor_txt, unif = _cores_caixa(arr, x0, y0, x1, y1)
                caixas.append({"q": k, "t": t, "intro": t <= 4, "txt": txt.strip(), "cx": (x0 + x1) / 2 / W, "cy": (y0 + y1) / 2 / H,
                               "h": (y1 - y0) / H, "w": (x1 - x0) / W, "fundo": fundo, "cor": cor_txt, "caixa": unif})
            f.unlink(missing_ok=True)
    pecas = {}
    if caixas:
        # legenda = texto centralizado que aparece em muitos quadros na mesma altura
        cent = [c for c in caixas if abs(c["cx"] - 0.5) < 0.14 and not c["intro"]]
        leg_y = None
        if cent:
            ys = np.array([c["cy"] for c in cent])
            hist = np.histogram(ys, bins=10, range=(0, 1))[0]
            b = int(np.argmax(hist))
            if len({c["q"] for c in cent if b / 10 <= c["cy"] < (b + 1) / 10}) >= max(3, n_q * 0.25):
                leg_y = (b + 0.5) / 10
        contagem = {}
        for c in caixas:
            contagem[c["txt"].lower()] = contagem.get(c["txt"].lower(), set()) | {c["q"]}
        peq = 0.028 if vertical else 0.045
        for c in caixas:
            digitos = bool(re.search(r"\d", c["txt"]))
            palavras = len(c["txt"].split())
            fixo = len(contagem[c["txt"].lower()]) >= max(3, n_q * 0.4)
            borda = c["cy"] > 0.85 or c["cy"] < 0.13 or c["cx"] < 0.2 or c["cx"] > 0.8
            mesmo_lugar = sum(1 for o in caixas if abs(o["cx"] - c["cx"]) < 0.06 and abs(o["cy"] - c["cy"]) < 0.04) >= max(3, n_q * 0.6)
            centro_leg = leg_y is not None and abs(c["cy"] - leg_y) < 0.08 and abs(c["cx"] - 0.5) < 0.16
            if centro_leg and not c["intro"]:
                tipo = "legenda"
            elif (fixo or mesmo_lugar) and borda and abs(c["cx"] - 0.5) > 0.12:
                tipo = "selo"
            elif c["h"] < peq and borda:
                tipo = "credito"
            elif c["intro"] and c["h"] >= peq * 1.3 and abs(c["cx"] - 0.5) < 0.22:
                tipo = "titulo"
            elif leg_y is not None and abs(c["cy"] - leg_y) < 0.08 and abs(c["cx"] - 0.5) < 0.16:
                tipo = "legenda"
            elif digitos and palavras <= 4:
                tipo = "numero"
            elif abs(c["cx"] - 0.5) > 0.12 and palavras <= 5:
                tipo = "etiqueta"
            else:
                continue
            pecas.setdefault(tipo, []).append(c)
    out = []
    minimo = {"titulo": 1, "selo": 3, "legenda": 3}
    for tipo, L in pecas.items():
        quadros_ = {c["q"] for c in L}
        if len(quadros_) < minimo.get(tipo, 2):
            continue
        caixa = sum(c["caixa"] for c in L) >= len(L) / 2
        Lc = [c for c in L if c["caixa"] == caixa] or L
        med = lambda k: float(np.median([c[k] for c in Lc]))   # noqa: E731
        def cor_med(k):
            a = np.array([[int(c[k][i:i + 2], 16) for i in (1, 3, 5)] for c in Lc])
            return _hex(np.median(a, axis=0))
        out.append({"tipo": tipo, "nome": NOMES[tipo][0], "dica": NOMES[tipo][1], "vezes": len(quadros_),
                    "cor_fundo": cor_med("fundo") if caixa else None, "cor_texto": cor_med("cor"), "caixa": bool(caixa),
                    "x": round(med("cx"), 3), "y": round(med("cy"), 3), "tam": round(med("h"), 3), "ligado": True})
    tr = _transicao(video, dur)
    if tr:
        out.append({"tipo": "transicao", "nome": NOMES["transicao"][0], "dica": TRANSICOES[tr], "modo": tr, "vezes": 0, "ligado": True})
    ordem = list(NOMES)
    out.sort(key=lambda e: ordem.index(e["tipo"]))
    return out, bool(ocr)


def por_tipo(elementos, tipo, so_ligados=True):
    return next((e for e in elementos or [] if e.get("tipo") == tipo and (e.get("ligado", True) or not so_ligados)), None)


# ------------------------------------------------------------------ desenho no edit.json
def _legivel(cor_txt, cor_fundo):
    """Garante contraste: se texto e fundo ficaram parecidos, texto vira preto ou branco."""
    def lum(h):
        r, g, b = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        return 0.299 * r + 0.587 * g + 0.114 * b
    try:
        if cor_fundo and abs(lum(cor_txt) - lum(cor_fundo)) < 0.35:
            return "#111111" if lum(cor_fundo) > 0.55 else "#ffffff"
    except Exception:
        pass
    return cor_txt or "#ffffff"


def _viva(h, padrao):
    """Cor de destaque precisa ser viva; se a referência deu um cinza, usa o destaque do estilo."""
    try:
        r, g, b = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        _, l, s = colorsys.rgb_to_hls(r, g, b)
        return h if s >= 0.35 and 0.25 <= l <= 0.8 else padrao
    except Exception:
        return padrao


_UNID = r"(mil|milh(ão|ões|oes)|bilh(ão|ões|oes)|trilh(ão|ões|oes)|thousand|million|billion|mil(l)?ones|metros|km|quil[oô]metros|toneladas|anos|years|años|" \
        r"d[oó]lares|dollars|reais|pesos|por\s?cento|percent|%|a\.?c\.?|d\.?c\.?|bc|ad)"


def _limpa(w):
    return re.sub(r"^[\"'“”‘’(\[]+|[\"'“”‘’)\],;:!?]+$", "", w)


def achar_numeros(words, inicio=1.5, gap=8.0, maximo=12):
    """Datas, preços e números ditos na narração → [{s, e, texto}] (tempo da palavra, do words.json)."""
    from .texto import colar_partidos
    words = colar_partidos(words)   # "0" ",40" → "0,40"; "a" ".C.," → "a.C.,"
    out, i, n = [], 0, len(words)
    while i < n:
        w = _limpa(words[i]["w"])
        if re.search(r"\d", w) and words[i]["s"] >= inicio:
            j = i + 1
            while j < n and re.fullmatch(r"[.,]\d+[.,]?", words[j]["w"]):   # Whisper separa "0" ",40"
                w += _limpa(words[j]["w"]).rstrip(".,")
                j += 1
            partes = [w.rstrip(".")]
            if i > 0 and re.fullmatch(r"(R|US|U\$|MX)?\$", _limpa(words[i - 1]["w"])):
                partes.insert(0, _limpa(words[i - 1]["w"]))
            k0 = j
            while j < n and j <= k0 + 1 and re.fullmatch(_UNID, _limpa(words[j]["w"]).lower().strip(".")):
                partes.append(_limpa(words[j]["w"]).rstrip(".,"))
                j += 1
            txt = re.sub(r"\s+([,.])(?=\d)", r"\1", " ".join(partes).replace(" %", "%"))
            txt = re.sub(r"(?i)\b([ad])\.?c\.?$", lambda m: m.group(1).lower() + ".C.", txt)
            if len(re.sub(r"\D", "", txt)) >= 2 or len(partes) > 1:   # "1" ou "2" soltos não viram caixinha
                if not out or words[i]["s"] - out[-1]["s"] >= gap:
                    out.append({"s": round(words[i]["s"], 2), "e": round(words[j - 1]["e"], 2), "texto": txt})
            i = j
            continue
        i += 1
    return out[:maximo]


def _livre(t, ocupados, folga=3.0):
    return all(abs(t - o) > folga for o in ocupados)


def itens_numeros(words, W, H, fonte, cor_destaque, estilo_el=None, ocupados=()):
    """Caixinha de fato: pílula com o número/data no instante em que a narração fala."""
    short = H > W
    el = estilo_el or {}
    if not el:
        bg = cor_destaque
    else:
        bg = (el.get("cor_fundo") or cor_destaque) if el.get("caixa") else None
    cor = _legivel(el.get("cor_texto") or "#111111", bg) if bg else _viva(el.get("cor_texto") or cor_destaque, cor_destaque)
    y = (el.get("y") if el.get("y") and 0.2 < el["y"] < 0.75 else None)
    y = round(H * y) if y else (720 if short else 150)
    out = []
    for k, n in enumerate(achar_numeros(words)):
        if not _livre(n["s"], ocupados):
            continue
        props = {"text": n["texto"], "x": W / 2, "y": y, "size": 86 if short else 54, "color": cor, "font": fonte, "weight": 900,
                 "align": "center", "upper": True, "shadow": not bg, "line": 1.0}
        if bg:
            props.update({"bg": bg, "pad": 14 if short else 10, "radius": 16})
        else:
            props.update({"stroke": "#000000", "stroke_w": 5})
        out.append({"id": f"fato{k}", "type": "text", "track": "textos", "label": f"Caixinha de número: {n['texto']}", "start": round(max(0, n["s"] - 0.1), 2),
                    "dur": round(max(2.0, n["e"] - n["s"] + 1.6), 2), "in": "pop", "out": "fade", "props": props})
    return out


def _fonte_curta(e):
    pg = e.get("pagina") or e.get("url") or ""
    host = urlparse(pg).netloc.lower().replace("www.", "") if pg.startswith("http") else ""
    nomes = {"commons.wikimedia.org": "Wikimedia Commons", "upload.wikimedia.org": "Wikimedia Commons", "flickr.com": "Flickr",
             "pexels.com": "Pexels", "pixabay.com": "Pixabay", "unsplash.com": "Unsplash", "archive.org": "Internet Archive",
             "nasa.gov": "NASA", "images.nasa.gov": "NASA", "loc.gov": "Library of Congress"}
    for k, v in nomes.items():
        if host.endswith(k):
            return v
    return host or (e.get("fonte") or "")


def itens_creditos(cenas, W, H, fonte, estilo_el=None, idioma="pt-BR"):
    """Etiqueta pequena de crédito no canto, no início de cada cena com imagem/clipe de banco."""
    short = H > W
    el = estilo_el or {}
    rot = {"pt-BR": ("Foto", "Vídeo"), "en-US": ("Photo", "Video"), "es-MX": ("Foto", "Video")}.get(idioma, ("Foto", "Vídeo"))
    size = 26 if short else 17
    canto_dir = (el.get("x") or 0) > 0.6
    y = H - (70 if short else 26)
    out = []
    for c in cenas:
        e = c.get("escolha") or {}
        if not e.get("src") or e.get("repetida"):
            continue
        f = _fonte_curta(e)
        if not f or re.search(r"\b(pc|upload|ia|gerad|ai)\b", f.lower()):
            continue
        lic = re.sub(r"^CC\s+(?=CC|PDM)", "", str(e.get("licenca") or "").strip())
        if re.search(r"public\s*domain|^pdm|^cc0", lic, re.I):
            lic = {"pt-BR": "domínio público", "es-MX": "dominio público"}.get(idioma, "public domain")
        txt = f"{rot[1] if e.get('tipo') == 'video' else rot[0]}: {f}" + (f" · {lic}" if lic and len(lic) < 22 else "")
        largura = len(txt) * size * 0.56
        x = (W - 24 - largura / 2) if canto_dir else (24 + largura / 2)
        dur = round(min(3.5, max(1.2, c["e"] - c["s"])), 2)
        out.append({"id": f"cred{c['i']}", "type": "text", "track": "textos", "label": "Crédito da imagem", "start": round(c["s"], 2) + (0.3 if c["s"] < 1 else 0),
                    "dur": dur, "in": "fade", "out": "fade",
                    "props": {"text": txt, "x": round(x), "y": y, "size": size, "color": _legivel(el.get("cor_texto") or "#ffffff", "#202020"), "font": "Arial", "weight": 600,
                              "align": "left", "shadow": True, "opacity": 0.85, **({"bg": "rgba(0,0,0,.45)", "pad": 4, "radius": 6} if el.get("caixa") else {})}})
    return out


_NAO_NOME = {"o", "a", "os", "as", "um", "uma", "no", "na", "em", "de", "do", "da", "e", "mas", "só", "ele", "ela", "eles", "elas", "isso", "isto", "esse",
             "essa", "the", "a", "an", "in", "on", "and", "but", "he", "she", "they", "it", "this", "that", "el", "la", "los", "las", "en", "y", "pero",
             "quando", "when", "cuando", "por", "porque", "why", "como", "how", "eu", "i", "você", "you", "nós", "we", "hoje", "today", "agora", "now",
             "deixa", "inscreva", "segue", "subscribe", "follow", "like", "se", "if", "si", "mas", "então", "so", "entonces", "foi", "was", "fue"}


def achar_nomes(words, maximo=4, gap=40.0):
    """Nomes próprios no meio da frase (Paris, Gustave Eiffel) → [{s, texto}] pra etiqueta de nome/lugar."""
    out, i, n = [], 1, len(words)
    vistos = set()
    while i < n:
        w = _limpa(words[i]["w"])
        anterior = words[i - 1]["w"]
        inicio_frase = anterior.endswith((".", "!", "?", ":"))
        if w[:1].isupper() and len(w) > 2 and not inicio_frase and w.lower() not in _NAO_NOME and not re.search(r"\d", w):
            partes, j = [w], i + 1
            while j < n and len(partes) < 3:
                nx = _limpa(words[j]["w"])
                if nx[:1].isupper() and len(nx) > 1 and not words[j - 1]["w"].endswith((".", ",", "!", "?")):
                    partes.append(nx)
                    j += 1
                else:
                    break
            nome = " ".join(partes)
            if nome.lower() not in vistos and (not out or words[i]["s"] - out[-1]["s"] >= gap):
                vistos.add(nome.lower())
                out.append({"s": round(words[i]["s"], 2), "texto": nome})
            i = j
            continue
        i += 1
    return out[:maximo]


def itens_etiquetas(words, W, H, fonte, cor_destaque, el, ocupados=()):
    """Etiqueta de nome/lugar no canto de baixo (cores da referência)."""
    short = H > W
    bg = el.get("cor_fundo") if el.get("caixa") else None
    bg = bg or cor_destaque
    cor = _legivel(el.get("cor_texto") or "#111111", bg)
    if short:
        x, y, size = W / 2, round(H * 0.62), 64
    else:
        lado_dir = (el.get("x") or 0.3) > 0.5
        y = round(H * min(0.8, max(0.15, el.get("y") or 0.78)))
        x, size = (W - 280) if lado_dir else 280, 40
    out = []
    for k, n in enumerate(achar_nomes(words)):
        if not _livre(n["s"], ocupados, 2.5):
            continue
        out.append({"id": f"etq{k}", "type": "text", "track": "textos", "label": f"Etiqueta: {n['texto']}", "start": n["s"], "dur": 3.2,
                    "in": "slide_up", "out": "fade",
                    "props": {"text": n["texto"], "x": x, "y": y, "size": size, "color": cor, "font": fonte, "weight": 900, "align": "center",
                              "upper": True, "bg": bg, "pad": 10, "radius": 8, "shadow": False}})
    return out


# ------------------------------------------------------------------ prévia "assim vai ficar"
def _fnt(tam, nome="burbank-big-condensed-black.otf"):
    for base in [Path.home() / "AppData" / "Local" / "Microsoft" / "Windows" / "Fonts", Path(r"C:\Windows\Fonts")]:
        for arq in (nome, "impact.ttf", "arialbd.ttf"):
            if (base / arq).exists():
                return ImageFont.truetype(str(base / arq), tam)
    return ImageFont.load_default()


def previa(elementos, preset, dst: Path, fundo_img: Path = None):
    """Desenha um quadro de exemplo com as peças ligadas, nas cores do estilo."""
    short = preset.get("formato") == "short"
    W, H = (360, 640) if short else (640, 360)
    if fundo_img and Path(fundo_img).exists():
        im = Image.open(fundo_img).convert("RGB")
        r = max(W / im.width, H / im.height)
        im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1)).crop((0, 0, W, H))
        im = Image.blend(im, Image.new("RGB", (W, H), "#000"), 0.55)
    else:
        im = Image.new("RGB", (W, H), preset.get("fundo") or "#101218")
        g = ImageDraw.Draw(im)
        for y in range(H):
            v = int(30 + 40 * y / H)
            g.line([(0, y), (W, y)], fill=(v // 2, v // 2 + 4, v))
    d = ImageDraw.Draw(im)
    AC = preset.get("cor_destaque") or "#ffd400"

    def pilula(txt, cx, cy, tam, bg, cor):
        f = _fnt(tam)
        b = d.textbbox((0, 0), txt, font=f)
        w, h = b[2] - b[0], b[3] - b[1]
        if bg:
            d.rounded_rectangle([cx - w / 2 - 10, cy - h / 2 - 7, cx + w / 2 + 10, cy + h / 2 + 9], radius=8, fill=bg)
        else:
            d.text((cx - w / 2 + 2, cy - h / 2 - b[1] + 2), txt, font=f, fill="#000")
        d.text((cx - w / 2, cy - h / 2 - b[1]), txt, font=f, fill=cor)

    def get(t):
        return por_tipo(elementos, t)
    t = get("titulo")
    if t or not elementos:
        bg = t.get("cor_fundo") if t and t.get("caixa") else None
        pilula("TÍTULO DO SEU VÍDEO", W / 2, H * (0.3 if not short else 0.2), 34 if not short else 30, bg, _legivel((t or {}).get("cor_texto") or "#fff", bg))
    n = get("numero")
    if n:
        bg = (n.get("cor_fundo") or AC) if n.get("caixa") else None
        pilula("1889", W / 2, H * (0.42 if not short else 0.38), 30, bg, _legivel(n.get("cor_texto") or "#111", bg) if bg else _viva(n.get("cor_texto") or AC, AC))
    e = get("etiqueta")
    if e:
        bg = (e.get("cor_fundo") if e.get("caixa") else None) or AC
        pilula("PARIS, FRANÇA", W * (0.25 if (e.get("x") or 0.3) < 0.5 else 0.75) if not short else W / 2, H * (0.7 if not short else 0.62), 20, bg,
               _legivel(e.get("cor_texto") or "#111", bg))
    lg = get("legenda")
    if preset.get("legenda", True):
        bg = "#000000" if (lg and lg.get("caixa")) or preset.get("legenda_caixa") else None
        ys = {"baixo": 0.86, "centro": 0.55, "topo": 0.16}
        pilula("ASSIM FICA A LEGENDA", W / 2, H * ys.get(preset.get("legenda_pos", "baixo"), 0.86), 26 if not short else 30, bg,
               (lg or {}).get("cor_texto") or "#ffffff")
    c = get("credito")
    if c:
        f = _fnt(11, "arialbd.ttf")
        txt = "Foto: Wikimedia Commons"
        b = d.textbbox((0, 0), txt, font=f)
        x = W - 10 - (b[2] - b[0]) if (c.get("x") or 0) > 0.6 else 10
        d.text((x, H - 18), txt, font=f, fill=_legivel(c.get("cor_texto") or "#fff", "#202020"))
    s = get("selo")
    if s:
        f = _fnt(14)
        sx = W * min(0.85, max(0.15, s.get("x") or 0.15))
        sy = H * min(0.92, max(0.06, s.get("y") or 0.08))
        b = d.textbbox((0, 0), "SEU CANAL", font=f)
        d.text((sx - (b[2] - b[0]) / 2, sy - 8), "SEU CANAL", font=f, fill=s.get("cor_texto") or "#fff")
    im.save(dst, quality=88)
    return dst
