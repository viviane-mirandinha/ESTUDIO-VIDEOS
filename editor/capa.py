# capa.py — capa 9:16 pro Instagram + descricao.txt (títulos, descrição e 5 hashtags) de um vídeo pronto.
# Formato da capa = formato do vídeo (16:9 → 1920x1080, 9:16 → 1080x1920).
# Capa: a foto do ASSUNTO (imagem do próprio vídeo ou da Wikipédia); se não achar, o quadro do vídeo onde a narração fala do ponto-chave (inteiro, sem cortar) na parte de baixo, fundo escuro em degradê no topo,
# selo "@canal" no canto, etiqueta de categoria e título grande branco com UMA palavra em amarelo.
# Texto: Ollama local (zero token); se estiver desligado, usa um texto simples feito a partir do tema.
import json
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

RAIZ = Path(__file__).resolve().parent.parent
FONTES = RAIZ / "recursos" / "fontes"
W, H = 1080, 1920
BG = (11, 12, 16)
AMARELO = (255, 205, 60)
BRANCO = (255, 255, 255)
CATEGORIAS = ("CURIOSIDADE", "COMO FUNCIONA", "HISTÓRIA", "MISTÉRIO", "CIÊNCIA", "VOCÊ SABIA")


def _fonte(nomes, tam):
    for n in nomes:
        f = FONTES / n
        if f.exists():
            try:
                return ImageFont.truetype(str(f), tam)
            except Exception:
                pass
    return ImageFont.load_default()


def _titulo_font(t):
    return _fonte(["Montserrat-Black.ttf", "Montserrat-ExtraBold.ttf", "Inter-ExtraBold.ttf"], t)


# ------------------------------------------------------------------ texto (IA local + plano B)
def _ler_texto(pasta: Path, ed: dict):
    tema = str((ed.get("pedido") or {}).get("tema") or "").strip()
    if not tema:
        nome = str(ed.get("name") or pasta.name)
        tema = nome.split(" - ")[-1].strip() if " - " in nome else re.sub(r"^\d+[-_ ]*", "", nome).replace("-", " ")
    roteiro = ""
    for n in ("narracao.txt", "roteiro.txt"):
        f = pasta / n
        if f.exists():
            roteiro = f.read_text(encoding="utf-8", errors="ignore").strip()
            break
    return tema, roteiro


def _canal(ed: dict):
    c = str((ed.get("pedido") or {}).get("canal") or "").strip()
    if not c:
        return ""
    return c if c.startswith("@") else "@" + re.sub(r"\s+", "", c).lower()


def _canal_digitado(c):
    return str(c or "").strip()   # exatamente como a pessoa digitou (sem @, sem juntar palavras)


def _validar_fatos(lista, roteiro):
    """Só aceita ficha cujo número/data realmente aparece no roteiro (a IA pequena inventa)."""
    rt = _norm(roteiro)
    out = []
    for f in lista or []:
        if not isinstance(f, dict):
            continue
        dest = re.sub(r"\s+", " ", str(f.get("destaque") or "")).strip()
        rot = re.sub(r"\s+", " ", str(f.get("rotulo") or "")).strip()
        if not dest or not rot or len(dest) > 16 or len(rot) > 34:
            continue
        nums = re.findall(r"\d+", dest)
        if nums:
            if not all(re.search(r"(?<!\d)" + n + r"(?!\d)", roteiro) for n in nums):
                continue
        else:   # ficha só com número/data (nome solto vira ficha fraca)
            continue
        if dest.lower() not in [x["destaque"].lower() for x in out]:
            out.append({"destaque": dest, "rotulo": rot})
    return out[:3]


def _fatos_regex(roteiro):
    """Plano B sem IA: números/anos do roteiro. Legenda = palavras do trecho em volta ('1971 · Construiu uma cabana')."""
    out, vistos = [], set()
    ruins = _STOP | {"que", "uns", "uma", "num", "numa", "dele", "dela", "foi", "era", "tem", "mas", "so", "depois", "ainda"}
    for m in re.finditer(r"(?<![\w/])((?:1[5-9]|20)\d\d|\d{1,3}(?:[.,]\d+)?)(\s+(?:%|mil|milh[õo]es|bilh[õo]es|anos|meses|dias|km|metros|mil[ií]metros|mortos|bombas|pessoas|vezes|graus|toneladas))?", roteiro):
        n, un = m.group(1), (m.group(2) or "").strip()
        if n in vistos:
            continue
        ano = len(n) == 4 and n[:2] in ("15", "16", "17", "18", "19", "20") and not un
        if not ano and not un:
            continue
        vistos.add(n)
        if ano:   # o que aconteceu: palavras depois do ano, até a pontuação
            resto = re.split(r"[.;:!?\n]|,\s", roteiro[m.end():m.end() + 80].lstrip(" ,;:-–"))[0]
            ps = [w for w in re.findall(r"[A-Za-zÀ-ÿ]+", resto) if _norm(w) not in ruins or w[0].isupper()][:3]
            rot = " ".join(ps)
            dest = n
        else:     # quantidade: o que foi contado (palavras antes do número)
            antes = re.split(r"[.;:!?\n]|,\s", roteiro[max(0, m.start() - 60):m.start()])[-1]
            ps = [w for w in re.findall(r"[A-Za-zÀ-ÿ]+", antes) if _norm(w) not in ruins][-2:]
            rot = " ".join(ps)
            dest = f"{n} {un}"
        if len(dest) > 16 or len(rot) < 3:
            continue
        out.append({"destaque": dest, "rotulo": rot.capitalize()[:30]})
        if len(out) >= 3:
            break
    return out


def _canal_digitado(c):
    return str(c or "").strip()   # exatamente como a pessoa digitou (sem @, sem juntar palavras)


def _validar_fatos(lista, roteiro):
    """Só aceita ficha cujo número/data realmente aparece no roteiro (a IA pequena inventa)."""
    rt = _norm(roteiro)
    out = []
    for f in lista or []:
        if not isinstance(f, dict):
            continue
        dest = re.sub(r"\s+", " ", str(f.get("destaque") or "")).strip()
        rot = re.sub(r"\s+", " ", str(f.get("rotulo") or "")).strip()
        if not dest or not rot or len(dest) > 16 or len(rot) > 34:
            continue
        nums = re.findall(r"\d+", dest)
        if nums:
            if not all(re.search(r"(?<!\d)" + n + r"(?!\d)", roteiro) for n in nums):
                continue
        elif _norm(dest) not in rt:
            continue
        if dest.lower() not in [x["destaque"].lower() for x in out]:
            out.append({"destaque": dest, "rotulo": rot})
    return out[:3]


def _plano_b(tema, roteiro):
    t = tema.strip().rstrip(".") or "Você sabia?"
    if not t.endswith("?"):
        t += "?"
    palavras = t.rstrip("?").split()
    destaque = max(palavras, key=len) if palavras else ""
    tags = []
    for p in re.findall(r"[A-Za-zÀ-ÿ]{5,}", tema):
        tags.append("#" + p.lower())
    for extra in ("#curiosidades", "#vocesabia", "#aprendanoinstagram", "#fatos", "#conhecimento"):
        tags.append(extra)
    return {
        "categoria": "CURIOSIDADE", "titulo_capa": t, "destaque": destaque,
        "titulos": [t, f"A verdade sobre: {t.rstrip('?')}", f"{t.rstrip('?')} — você sabia?"],
        "descricao": (roteiro.split("\n")[0][:220] if roteiro else t) + "\n\nSalve e compartilhe com quem curte curiosidades!",
        "hashtags": list(dict.fromkeys(tags))[:5],
    }


def _gerar_texto(tema, roteiro, modelo, idioma, prog):
    base = _plano_b(tema, roteiro)
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent / "fabrica"))
        from lib import ollama as OL
        pedido = (
            "Você cuida do Instagram de um canal de curiosidades. Com base no vídeo abaixo, crie o material de postagem.\n"
            f"TEMA: {tema}\nROTEIRO: {roteiro[:2500]}\nIdioma: {idioma}. NÃO invente fatos que não estejam no roteiro.\n"
            'Responda SOMENTE JSON: {"categoria": "uma de: CURIOSIDADE, COMO FUNCIONA, HISTÓRIA, MISTÉRIO, CIÊNCIA, VOCÊ SABIA", '
            '"titulo_capa": "título curto e curioso pra capa, 4 a 8 palavras, geralmente uma pergunta", '
            '"destaque": "UMA palavra do titulo_capa que merece destaque", '
            '"sujeito_pt": "a pessoa, animal, objeto ou lugar ESPECÍFICO de que o vídeo trata, com as palavras EXATAS que aparecem no roteiro; deixe vazio se o vídeo é sobre um evento, tema geral ou vários assuntos", '
            '"sujeito_en": "o mesmo assunto como título da Wikipédia em inglês (vazio se sujeito_pt estiver vazio), ex.: Ted Kaczynski, Turritopsis dohrnii, Wind turbine", '
            '"fatos": [{"destaque": "número, data ou nome CURTO (até 14 caracteres) copiado do roteiro, ex.: 1978–1995, 16 bombas, 3 mortos", "rotulo": "o que é, até 4 palavras"}] (exatamente 3 itens, só com informação que está no roteiro), '
            '"trecho_chave": "copie do roteiro, SEM mudar, a frase curta (até 15 palavras) que mostra o ponto principal / o momento mais impactante do vídeo", '
            '"titulos": ["3 títulos diferentes pro vídeo, até 70 caracteres cada"], '
            '"descricao": "legenda do post, 2 a 4 frases com gancho e chamada pra curtir/seguir, sem hashtags", '
            '"hashtags": ["exatamente 5 hashtags relacionadas ao tema, começando com #"]}')
        prog(40, "Escrevendo títulos, descrição e hashtags…")
        d = OL._json_seguro(OL.gerar(pedido, modelo, json_mode=True, temperatura=0.7, num_predict=900, timeout=1800))   # 30 min: modelo grande em PC fraco demora, mas termina (de madrugada tudo bem)
        cat = str(d.get("categoria") or "").upper().strip()
        if cat in CATEGORIAS:
            base["categoria"] = cat
        tc = str(d.get("titulo_capa") or "").strip()
        if 2 <= len(tc.split()) <= 12:
            base["titulo_capa"] = tc
            dest = str(d.get("destaque") or "").strip().strip("?.,!")
            pals = [w.lower().strip("?.,!:") for w in tc.split()]
            base["destaque"] = dest if len(dest) > 2 and dest.lower() in pals else max(tc.rstrip("?").split(), key=len).strip("?.,!:")
        sj = re.sub(r"[^\w\s.\-À-ÿ]", "", str(d.get("sujeito_en") or "")).strip()
        spt = re.sub(r"[^\w\s.\-À-ÿ]", "", str(d.get("sujeito_pt") or "")).strip()
        # a IA pequena inventa assunto: só vale se alguma palavra do assunto está MESMO no roteiro
        corpo = _norm(roteiro + " " + tema)
        tk = [w for w in re.findall(r"[a-z0-9]{4,}", _norm(spt + " " + sj)) if w not in _STOP]
        if 2 <= len(sj) <= 60 and spt and any(w in corpo for w in tk):
            base["sujeito_en"], base["sujeito_pt"] = sj, spt
        elif 2 <= len(sj) <= 60 and not spt and any(w in corpo for w in tk):
            base["sujeito_en"] = sj
        fl = _validar_fatos(d.get("fatos"), roteiro)
        if fl:
            base["fatos"] = fl
        tk = str(d.get("trecho_chave") or "").strip()
        if tk:
            base["trecho_chave"] = tk[:240]
        ts = [str(x).strip() for x in (d.get("titulos") or []) if str(x).strip()][:3]
        if ts:
            base["titulos"] = ts
        ds = str(d.get("descricao") or "").strip()
        if ds:
            base["descricao"] = ds
        hs = []
        for h in d.get("hashtags") or []:
            h = "#" + re.sub(r"[^\wÀ-ÿ]", "", str(h)).lower()
            if len(h) > 2 and h not in hs:
                hs.append(h)
        for h in _plano_b(tema, roteiro)["hashtags"]:
            if len(hs) < 5 and h not in hs:
                hs.append(h)
        base["hashtags"] = hs[:5]
    except Exception:
        pass   # IA desligada: fica o texto simples
    if not base.get("fatos"):
        base["fatos"] = _fatos_regex(roteiro)
    return base


# ------------------------------------------------------------------ imagem
_STOP = set("para como mais muito essa esse isso esta este pelo pela mas por que uma uns umas dos das com sem sobre entre quando onde qual quais ainda tambem depois antes porque seus suas ele ela eles elas nao sim tem ter foi era sao ser the and with that this from".split())


def _norm(t):
    import unicodedata
    t = unicodedata.normalize("NFD", str(t).lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


def _toks(t):
    return [w for w in re.findall(r"[a-z0-9]{4,}", _norm(t)) if w not in _STOP]


def _pesos(d, tema):
    """Palavras que definem o ponto-chave → peso (destaque > trecho-chave/título > tema)."""
    pw = {}
    for txt, peso in ((tema, 1.0), (d.get("titulo_capa", ""), 2.0), (d.get("trecho_chave", ""), 2.5), (d.get("destaque", ""), 4.0)):
        for w in _toks(txt):
            pw[w] = max(pw.get(w, 0), peso)
    return pw


def _momento_chave(pasta: Path, ed: dict, d: dict, tema: str):
    """Segundo do vídeo em que a narração fala do ponto-chave (janela de ~4 s com mais palavras importantes).
    Usa words.json (Whisper) ou, se não houver, os textos/cenas do edit.json. None = não achou."""
    pw = _pesos(d, tema)
    if not pw:
        return None
    dur = float(ed.get("duration") or 0)
    # 1) palavra por palavra
    try:
        ws = json.loads((pasta / "words.json").read_text(encoding="utf-8-sig"))
        ws = [w for w in ws if isinstance(w, dict) and "s" in w]
    except Exception:
        ws = []
    if len(ws) >= 8:
        melhor, ts = 0.0, None
        for i, w in enumerate(ws):
            t0 = float(w["s"])
            if dur and t0 > dur * 0.92:
                break
            sc, vistos = 0.0, set()
            for w2 in ws[i:]:
                if float(w2["s"]) - t0 > 4.0:
                    break
                for tk in _toks(w2.get("w", "")):
                    if tk in pw and tk not in vistos:
                        vistos.add(tk)
                        sc += pw[tk]
            sc -= t0 * 0.004   # empate: prefere o que aparece mais cedo
            if sc > melhor:
                melhor, ts = sc, t0
        if ts is not None and melhor >= 2.0:
            return ts + 1.2   # um pouco depois de a frase começar: a imagem já está no ar
    # 2) cenas do edit.json
    melhor, ts = 0.0, None
    for it in ed.get("items") or []:
        lab, st, du = it.get("label"), it.get("start"), it.get("dur")
        if not lab or st is None or not du or it.get("type") == "param":
            continue
        sc = sum(pw[t] for t in set(_toks(lab)) if t in pw) - float(st) * 0.004
        if sc > melhor:
            melhor, ts = sc, float(st) + float(du) * 0.5
    return ts if melhor >= 2.0 else None


def _relevancia(pasta: Path, ed: dict, d: dict, tema: str):
    """Lista de (segundo, nota): onde a narração/cenas falam das palavras do ponto-chave."""
    pw = _pesos(d, tema)
    out = []
    if not pw:
        return out
    try:
        ws = [w for w in json.loads((pasta / "words.json").read_text(encoding="utf-8-sig")) if isinstance(w, dict) and "s" in w]
    except Exception:
        ws = []
    for i, w in enumerate(ws):
        t0, sc, vistos = float(w["s"]), 0.0, set()
        for w2 in ws[i:i + 14]:
            if float(w2["s"]) - t0 > 4.0:
                break
            for tk in _toks(w2.get("w", "")):
                if tk in pw and tk not in vistos:
                    vistos.add(tk)
                    sc += pw[tk]
        if sc > 0:
            out.append((t0 + 1.5, sc))
    for it in ed.get("items") or []:
        lab, st, du = it.get("label"), it.get("start"), it.get("dur")
        if lab and st is not None and du and it.get("type") != "param":
            sc = sum(pw[t] for t in set(_toks(lab)) if t in pw)
            if sc > 0:
                out.append((float(st) + float(du) * 0.5, sc))
    return out


def _nota_visual(a, b):
    """Nota 0..1 de 'capa chamativa' para um quadro (a) e outro 0,35 s depois (b), arrays RGB 96x96:
    cobertura do assunto sobre o fundo, contraste, cor viva e ESTABILIDADE (não pode estar no meio de uma transição/fade)."""
    a = a.astype("float32")
    lum = a @ [0.299, 0.587, 0.114]
    q = (a // 32).astype("int32")
    chave = q[..., 0] * 64 + q[..., 1] * 8 + q[..., 2]
    fundo = int(np_bincount_max(chave))
    nao_fundo = chave != fundo
    cob = float(nao_fundo.mean())
    s_cob = max(0.0, 1 - abs(cob - 0.45) / 0.45)
    contraste = min(1.0, float(lum.std()) / 60.0)
    mx, mn = a.max(2), a.min(2)
    sat = (mx - mn) / (mx + 1)
    s_sat = min(1.0, float(sat[nao_fundo].mean() if nao_fundo.any() else 0) / 0.55)
    dif = float(abs(a - b.astype("float32")).mean()) / 255.0
    estavel = 1 - min(1.0, dif * 14)
    claro = 1.0 if lum.mean() > 45 or contraste > 0.5 else 0.5
    return (0.3 * s_cob + 0.3 * contraste + 0.2 * s_sat + 0.2 * estavel) * (0.25 + 0.75 * estavel) * claro


def np_bincount_max(x):
    import numpy as _np
    return _np.bincount(x.ravel()).argmax()


def _melhor_quadro(pasta: Path, ed: dict, d: dict, tema: str, n=42):
    """Escolhe o instante do vídeo mais CHAMATIVO e ligado ao ponto-chave: analisa ~42 quadros espalhados
    (nota visual: assunto grande, contraste, cor, quadro parado) e soma a relevância da narração naquele ponto."""
    import numpy as _np
    vid = next((pasta / x for x in ("leve.mp4", "final.mp4") if (pasta / x).exists()), None)
    dur = float(ed.get("duration") or 0)
    if not vid or dur < 5:
        return None
    rel = _relevancia(pasta, ed, d, tema)
    rmax = max([r[1] for r in rel], default=0.0)
    tempos = [dur * (0.06 + 0.88 * i / (n - 1)) for i in range(n)]
    tempos += [t for t, _ in sorted(rel, key=lambda x: -x[1])[:8]]   # e os momentos mais ligados ao tema
    melhor, ts = -1.0, None
    for t in tempos:
        try:
            r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{max(t - 0.1, 0):.2f}", "-i", str(vid), "-t", "0.6", "-vf", "fps=3,scale=96:96",
                                "-frames:v", "2", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, timeout=60)
            buf = r.stdout
            if len(buf) < 2 * 96 * 96 * 3:
                continue
            a = _np.frombuffer(buf[:96 * 96 * 3], dtype=_np.uint8).reshape(96, 96, 3)
            b = _np.frombuffer(buf[96 * 96 * 3:2 * 96 * 96 * 3], dtype=_np.uint8).reshape(96, 96, 3)
        except Exception:
            continue
        vis = _nota_visual(a, b)
        rs = max([sc * max(0.0, 1 - abs(t - tt) / 5.0) for tt, sc in rel], default=0.0)
        rn = rs / rmax if rmax else 0.0
        tot = 0.5 * vis + 0.5 * rn if rmax else vis
        if tot > melhor:
            melhor, ts = tot, t
    return ts


# ------------------------------------------------------------------ foto do ASSUNTO principal
def _toks_sujeito(*textos):
    out = set()
    for t in textos:
        out |= {w for w in re.findall(r"[a-z0-9]{3,}", _norm(t)) if w not in _STOP and w not in ("the", "and", "van", "von")}
    return out


def _img_local(pasta: Path, d: dict, tema: str):
    """Procura, entre as imagens que o próprio vídeo já usa (img/), a que mostra o assunto principal
    (pelo nome do arquivo e pelos créditos/buscas gravados). None = não achou."""
    sj = _toks_sujeito(d.get("sujeito_en", ""))
    sec = _toks_sujeito(d.get("destaque", ""), d.get("titulo_capa", ""), tema) - sj
    if not sj and not sec:
        return None
    meta = {}
    try:
        for c in json.loads((pasta / "img" / "creditos.json").read_text(encoding="utf-8-sig")):
            meta[str(c.get("arquivo", "")).lower()] = f'{c.get("titulo", "")} {c.get("query", "")}'
    except Exception:
        pass
    melhor, arq = 0.0, None
    for f in (pasta / "img").glob("*") if (pasta / "img").is_dir() else []:
        if f.suffix.lower() not in (".jpg", ".jpeg", ".png", ".webp") or f.name.startswith(("_", "capa_")):
            continue
        txt = _norm(f.stem + " " + meta.get(f.name.lower(), ""))
        palavras = set(re.findall(r"[a-z0-9]{3,}", txt))
        sc = 3.0 * len(sj & palavras) + 1.0 * len(sec & palavras)
        if not (sj & palavras):   # sem nenhuma palavra do sujeito: só vale se bater 2+ palavras do tema
            sc = sc if len(sec & palavras) >= 2 else 0
        if sc <= 0:
            continue
        try:
            with Image.open(f) as im:
                w, h = im.size
        except Exception:
            continue
        if w < 500 or h < 400:
            continue
        sc += min(w * h / 4e6, 1.0) * 0.5   # desempate: mais resolução
        if sc > melhor:
            melhor, arq = sc, f
    return arq


def _wiki_sujeito(pasta: Path, assunto: str):
    """Baixa a foto principal (imagem da abertura) do artigo da Wikipédia sobre o assunto → img/capa_sujeito.jpg."""
    import urllib.parse
    sys.path.insert(0, str(Path(__file__).resolve().parent / "fabrica"))
    from lib import imagens
    for lang in ("en", "pt"):
        try:
            u = (f"https://{lang}.wikipedia.org/w/api.php?" + urllib.parse.urlencode({
                "action": "query", "format": "json", "generator": "search", "gsrsearch": assunto, "gsrlimit": 3,
                "prop": "pageimages", "piprop": "original|name", "redirects": 1}))
            pg = (json.loads(imagens._get(u, timeout=20)).get("query") or {}).get("pages") or {}
            for p in sorted(pg.values(), key=lambda x: x.get("index", 9)):
                if not (_toks_sujeito(assunto) & _toks_sujeito(p.get("title", ""))):
                    continue   # artigo que não tem a ver com o assunto pedido
                src, nome = ((p.get("original") or {}).get("source") or "").split("?")[0], p.get("pageimage")
                if not src or not re.search(r"\.(jpe?g|png)$", src, re.I):
                    continue
                if (p.get("original") or {}).get("width", 0) < 500:
                    continue
                lic, autor, pagina = "", "", ""
                try:
                    cu = ("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({
                        "action": "query", "format": "json", "prop": "imageinfo", "iiprop": "extmetadata|url",
                        "titles": "File:" + nome}))
                    ii = next(iter((json.loads(imagens._get(cu, timeout=20)).get("query") or {}).get("pages", {}).values()))["imageinfo"][0]
                    em = ii.get("extmetadata") or {}
                    lic = (em.get("LicenseShortName") or {}).get("value", "")
                    autor = re.sub(r"<[^>]+>", "", (em.get("Artist") or {}).get("value", ""))
                    pagina = ii.get("descriptionurl", "")
                except Exception:
                    pass
                if lic and re.search(r"non.?commercial|nc|fair use|copyrighted", lic, re.I):
                    continue
                dados = imagens._get(src, timeout=60)
                if not dados or len(dados) < 15000:
                    continue
                (pasta / "img").mkdir(exist_ok=True)
                dest = pasta / "img" / "capa_sujeito.jpg"
                tmp = pasta / "img" / "_capa_sujeito.bin"
                tmp.write_bytes(dados)
                Image.open(tmp).convert("RGB").save(dest, "JPEG", quality=93)
                tmp.unlink()
                try:   # crédito obrigatório (CC-BY etc.)
                    from lib import bancos
                    bancos._gravar_credito(pasta, "img", "capa_sujeito.jpg", {"titulo": p.get("title", ""), "autor": autor,
                                           "fonte": f"Wikipédia ({lang})", "licenca": lic or "Wikimedia Commons", "pagina": pagina})
                except Exception:
                    pass
                return dest
        except Exception:
            continue
    return None


def _tem_fotos(pasta: Path):
    """O vídeo usa fotos próprias (pasta img/)? Só então vale completar com uma foto da Wikipédia do mesmo estilo."""
    n = 0
    for f in (pasta / "img").glob("*") if (pasta / "img").is_dir() else []:
        if f.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp") and not f.name.startswith(("_", "capa_")):
            try:
                with Image.open(f) as im:
                    n += im.width >= 400 and im.height >= 300
            except Exception:
                pass
    return n >= 1


def _limpar_sujeito(pasta: Path):
    """Apaga a foto baixada numa criação anterior (e o crédito dela) para nunca reaproveitar uma foto errada."""
    try:
        (pasta / "img" / "capa_sujeito.jpg").unlink()
    except Exception:
        pass
    try:
        cp = pasta / "img" / "creditos.json"
        if cp.exists():
            cr = [c for c in json.loads(cp.read_text(encoding="utf-8-sig")) if c.get("arquivo") != "capa_sujeito.jpg"]
            cp.write_text(json.dumps(cr, ensure_ascii=False, indent=2), "utf-8")
    except Exception:
        pass


def _foto_sujeito(pasta: Path, d: dict, tema: str, prog):
    """Foto principal = SEMPRE algo que está no vídeo: uma imagem da pasta img/ do próprio vídeo que mostre o assunto.
    Se não houver, retorna None e a capa usa um QUADRO do vídeo no momento do ponto-chave. Nunca baixa foto de fora."""
    prog(55, "Procurando no vídeo a imagem do assunto principal…")
    _limpar_sujeito(pasta)   # apaga foto baixada por versões antigas (e o crédito dela)
    return _img_local(pasta, d, tema)


def _apoio(pasta: Path, ed: dict, d: dict, tema: str, hero, n=3):
    """Imagens de apoio da montagem: as do próprio vídeo mais ligadas ao tema (sem repetir a foto principal);
    se o vídeo não tiver imagens (motion graphics), usa quadros tirados do vídeo. Retorna (lista, temporarios)."""
    pw = _pesos(d, tema)
    rot = {}
    for it in ed.get("items") or []:
        src = ((it.get("props") or {}).get("src") or "")
        if isinstance(src, str) and src and it.get("label"):
            rot[Path(src).name.lower()] = str(it["label"])
    meta = {}
    try:
        for c in json.loads((pasta / "img" / "creditos.json").read_text(encoding="utf-8-sig")):
            meta[str(c.get("arquivo", "")).lower()] = f'{c.get("titulo", "")} {c.get("query", "")}'
    except Exception:
        pass
    cands = []
    pasta_img = pasta / "img"
    for f in sorted(pasta_img.glob("*")) if pasta_img.is_dir() else []:
        if f.suffix.lower() not in (".jpg", ".jpeg", ".png", ".webp") or f.name.startswith(("_", "capa_")):
            continue
        if hero and Path(hero).resolve() == f.resolve():
            continue
        try:
            with Image.open(f) as im:
                w, h = im.size
        except Exception:
            continue
        if w < 400 or h < 300:
            continue
        try:   # descarta texturas/telas lisas (pouco contraste = não é uma foto que conta algo)
            import numpy as _np
            with Image.open(f) as im:
                if float(_np.asarray(im.convert("L").resize((64, 64)), dtype=_np.float32).std()) < 38:
                    continue
        except Exception:
            pass
        txt = _norm(f.stem + " " + meta.get(f.name.lower(), "") + " " + rot.get(f.name.lower(), ""))
        sc = sum(pw[t] for t in set(re.findall(r"[a-z0-9]{4,}", txt)) if t in pw)
        cands.append((sc, w * h, f))
    cands.sort(key=lambda x: (-x[0], -x[1]))
    pick = [c[2] for c in cands[:n]]
    temp = []
    if len(pick) < 2:   # vídeo sem imagens próprias: 2-3 quadros do vídeo (clean) em momentos diferentes
        vid = next((pasta / x for x in ("final.mp4", "leve.mp4") if (pasta / x).exists()), None)
        dur = float(ed.get("duration") or 0)
        if vid and dur > 6:
            for i, fr in enumerate((0.22, 0.5, 0.78)):
                if len(pick) >= n:
                    break
                out = pasta / f"_capa_ap{i}.jpg"
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{dur * fr:.2f}", "-i", str(vid), "-frames:v", "1", "-q:v", "2", str(out)],
                               capture_output=True, timeout=120)
                if out.exists():
                    pick.append(out)
                    temp.append(out)
    return pick, temp


def _quadro(pasta: Path, dur, ss=None):
    vid = next((pasta / n for n in ("final.mp4", "leve.mp4") if (pasta / n).exists()), None)
    if not vid:
        mp4 = [f for f in pasta.glob("*.mp4")]
        vid = max(mp4, key=lambda f: f.stat().st_mtime) if mp4 else None
    if not vid:
        return None
    out = pasta / "_capa_quadro.jpg"
    dur = float(dur or 20)
    if ss is None:
        ss = dur * 0.3
    ss = min(max(1.0, float(ss)), max(1.0, dur - 1.0))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ss:.2f}", "-i", str(vid), "-frames:v", "1", "-q:v", "2", str(out)],
                   capture_output=True, timeout=120)
    return out if out.exists() else None


def _cobrir(img, w, h):
    r = max(w / img.width, h / img.height)
    img = img.resize((int(img.width * r) + 1, int(img.height * r) + 1), Image.LANCZOS)
    x, y = (img.width - w) // 2, (img.height - h) // 2
    return img.crop((x, y, x + w, y + h))


def _quebrar(draw, palavras, fonte, largura):
    linhas, atual = [], []
    for p in palavras:
        teste = " ".join(atual + [p])
        if atual and draw.textlength(teste, font=fonte) > largura:
            linhas.append(atual)
            atual = [p]
        else:
            atual.append(p)
    if atual:
        linhas.append(atual)
    return linhas


def _desenhar_horizontal(quadro, d, canal, destino: Path):
    """Capa 16:9 (1920x1080): título à esquerda, foto do assunto inteira à direita."""
    Wh, Hh = 1920, 1080
    cv = Image.new("RGB", (Wh, Hh), BG)
    if quadro:
        im = Image.open(quadro).convert("RGB")
        cv.paste(_cobrir(im, Wh, Hh).filter(ImageFilter.GaussianBlur(30)).point(lambda v: int(v * 0.5)), (0, 0))
        zx0, zx1, zy0, zy1 = 1000, Wh - 70, 135, Hh - 60
        r = min((zx1 - zx0) / im.width, (zy1 - zy0) / im.height)
        fw, fh = max(1, int(im.width * r)), max(1, int(im.height * r))
        fr = im.resize((fw, fh), Image.LANCZOS)
        fx, fy = zx0 + (zx1 - zx0 - fw) // 2, zy0 + (zy1 - zy0 - fh) // 2
        m = Image.new("L", (fw, fh), 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, fw - 1, fh - 1), 26, fill=255)
        cv.paste(fr, (fx, fy), m)
    # degradê lateral: esquerda escura sólida → transparente
    grad = Image.new("L", (Wh, 1), 0)
    for x in range(Wh):
        grad.putpixel((x, 0), 255 if x < Wh * 0.30 else max(0, int(255 * (1 - (x - Wh * 0.30) / (Wh * 0.20)))))
    cv.paste(Image.new("RGB", (Wh, Hh), BG), (0, 0), grad.resize((Wh, Hh)))
    dr = ImageDraw.Draw(cv, "RGBA")
    if canal:
        f = _fonte(["Inter-Bold.ttf", "Inter-ExtraBold.ttf"], 30)
        tw = dr.textlength(canal, font=f)
        x1, y0 = Wh - 50, 45
        dr.rounded_rectangle((x1 - tw - 52, y0, x1, y0 + 64), 16, fill=(24, 26, 34, 235))
        dr.text((x1 - 26 - tw, y0 + 32), canal, font=f, fill=BRANCO, anchor="lm")
    f = _fonte(["JetBrainsMono-Bold.woff", "JetBrainsMono.ttf", "Inter-Bold.ttf"], 28)
    cat, trilho = d["categoria"], 7
    tw = sum(dr.textlength(c, font=f) + trilho for c in cat)
    dr.rounded_rectangle((80, 150, 80 + tw + 90, 210), 30, fill=(34, 36, 48, 245))
    dr.ellipse((102, 166, 132, 196), fill=AMARELO)
    cx = 148
    for c in cat:
        dr.text((cx, 180), c, font=f, fill=(230, 232, 240), anchor="lm")
        cx += dr.textlength(c, font=f) + trilho
    titulo = d["titulo_capa"].strip()
    destaque = d["destaque"].lower().strip("?.,!:")
    palavras = titulo.split()
    for tam in (124, 112, 104, 96, 88, 80, 72, 64):
        fonte = _titulo_font(tam)
        linhas = _quebrar(dr, palavras, fonte, 860)
        if len(linhas) <= 5 and len(linhas) * tam * 1.07 <= 600:
            break
    y = 250
    for ln in linhas:
        x = 80
        for p in ln:
            amarelo = p.lower().strip("?.,!:") == destaque
            if amarelo:
                brilho = Image.new("RGBA", (Wh, Hh), (0, 0, 0, 0))
                ImageDraw.Draw(brilho).text((x, y), p, font=fonte, fill=AMARELO + (150,))
                cv.paste(Image.new("RGB", (Wh, Hh), AMARELO), (0, 0), brilho.filter(ImageFilter.GaussianBlur(16)).split()[3].point(lambda v: int(v * 0.55)))
                dr = ImageDraw.Draw(cv, "RGBA")
            dr.text((x + 3, y + 5), p, font=fonte, fill=(0, 0, 0, 110))
            dr.text((x, y), p, font=fonte, fill=AMARELO if amarelo else BRANCO)
            x += dr.textlength(p + " ", font=fonte)
        y += int(tam * 1.07)
    cv.save(destino, "JPEG", quality=94)


def _desenhar(quadro, d, canal, destino: Path, horizontal=False):
    if horizontal:
        return _desenhar_horizontal(quadro, d, canal, destino)
    cv = Image.new("RGB", (W, H), BG)
    if quadro:
        im = Image.open(quadro).convert("RGB")
        # fundo: o próprio quadro ampliado e desfocado (preenche a capa toda)
        cv.paste(_cobrir(im, W, H).filter(ImageFilter.GaussianBlur(28)).point(lambda v: int(v * 0.55)), (0, 0))
        # quadro INTEIRO (sem cortar o assunto) na área livre, embaixo do título
        zona_y0, zona_y1 = 900, H - 60
        if im.width / im.height >= 1.2:   # horizontal: ocupa a largura toda
            fw = W
            fh = int(im.height * fw / im.width)
        else:                              # vertical/quadrado: ocupa a altura da zona
            fh = zona_y1 - zona_y0
            fw = int(im.width * fh / im.height)
        fh = min(fh, zona_y1 - zona_y0)
        fw = min(fw, W)
        fr = im.resize((fw, fh), Image.LANCZOS)
        fx, fy = (W - fw) // 2, zona_y0 + (zona_y1 - zona_y0 - fh) // 2
        cv.paste(fr, (fx, fy))
    # degradê: topo escuro sólido → transparente (~45% da altura)
    grad = Image.new("L", (1, H), 0)
    for y in range(H):
        a = 255 if y < H * 0.30 else max(0, int(255 * (1 - (y - H * 0.30) / (H * 0.17))))
        grad.putpixel((0, y), a)
    cv.paste(Image.new("RGB", (W, H), BG), (0, 0), grad.resize((W, H)))
    dr = ImageDraw.Draw(cv, "RGBA")

    # selo @canal (canto superior direito)
    if canal:
        f = _fonte(["Inter-Bold.ttf", "Inter-ExtraBold.ttf"], 28)
        tw = dr.textlength(canal, font=f)
        x1, y0 = W - 30, 50
        dr.rounded_rectangle((x1 - tw - 52, y0, x1, y0 + 62), 16, fill=(24, 26, 34, 235))
        dr.text((x1 - 26 - tw, y0 + 31), canal, font=f, fill=BRANCO, anchor="lm")

    # etiqueta de categoria
    f = _fonte(["JetBrainsMono-Bold.woff", "JetBrainsMono.ttf", "Inter-Bold.ttf"], 27)
    cat, trilho = d["categoria"], 7   # letras com espaçamento
    tw = sum(dr.textlength(c, font=f) + trilho for c in cat)
    dr.rounded_rectangle((70, 250, 70 + tw + 90, 308), 29, fill=(34, 36, 48, 245))
    dr.ellipse((92, 266, 120, 294), fill=AMARELO)
    cx = 136
    for c in cat:
        dr.text((cx, 279), c, font=f, fill=(230, 232, 240), anchor="lm")
        cx += dr.textlength(c, font=f) + trilho

    # título (palavra de destaque em amarelo) — reduz a fonte até caber em 4 linhas
    titulo = d["titulo_capa"].strip()
    destaque = d["destaque"].lower().strip("?.,!:")
    palavras = titulo.split()
    for tam in (112, 104, 96, 88, 80, 72, 64):
        fonte = _titulo_font(tam)
        linhas = _quebrar(dr, palavras, fonte, W - 150)
        if len(linhas) <= 4:
            break
    y = 365
    for ln in linhas:
        x = 74
        for p in ln:
            amarelo = p.lower().strip("?.,!:") == destaque
            if amarelo:   # brilho suave atrás da palavra
                brilho = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                ImageDraw.Draw(brilho).text((x, y), p, font=fonte, fill=AMARELO + (150,))
                cv.paste(Image.new("RGB", (W, H), AMARELO), (0, 0), brilho.filter(ImageFilter.GaussianBlur(16)).split()[3].point(lambda v: int(v * 0.55)))
                dr = ImageDraw.Draw(cv, "RGBA")
            dr.text((x + 3, y + 5), p, font=fonte, fill=(0, 0, 0, 110))
            dr.text((x, y), p, font=fonte, fill=AMARELO if amarelo else BRANCO)
            x += dr.textlength(p + " ", font=fonte)
        y += int(tam * 1.07)
    cv.save(destino, "JPEG", quality=94)


def criar(pasta, modelo="llama3.2:3b", idioma="pt-BR", prog=None, titulo=None, canal=None, tipo="investigacao"):
    """titulo: texto da capa digitado pela pessoa (vazio/None = automático). canal: @ no canto (vazio/None = nada)."""
    prog = prog or (lambda p, m: None)
    pasta = Path(pasta)
    ed = json.loads((pasta / "edit.json").read_text(encoding="utf-8-sig"))
    tema, roteiro = _ler_texto(pasta, ed)
    prog(10, "Pegando um quadro do vídeo…")
    d = _gerar_texto(tema, roteiro, modelo, idioma, prog)
    titulo = re.sub(r"\s+", " ", str(titulo or "")).strip()[:140]
    if titulo:   # título escolhido pela pessoa
        d["titulo_capa"] = titulo
        pal = [w.strip("?.,!:;") for w in titulo.split()]
        d["destaque"] = max(pal, key=len) if pal else ""
    quadro, temp = None, False
    try:
        quadro = _foto_sujeito(pasta, d, tema, prog)   # 1º: foto do assunto (a água-viva, o Ted, o gerador…)
    except Exception:
        quadro = None
    if not quadro:                                      # 2º: quadro do momento em que a narração fala do ponto-chave
        prog(66, "Achando o momento principal do vídeo…")
        try:
            ss = _melhor_quadro(pasta, ed, d, tema)
            if ss is None:
                ss = _momento_chave(pasta, ed, d, tema)
        except Exception:
            ss = None
        quadro, temp = _quadro(pasta, ed.get("duration"), ss), True
    if (tipo or "investigacao") == "investigacao":   # a etiqueta acompanha o tipo escolhido (igual ao exemplo do modal)
        d["categoria"] = "INVESTIGAÇÃO"
    prog(75, "Montando a capa…")
    capa = pasta / "capa_instagram.jpg"
    cvs = ed.get("canvas") or {}
    horiz = float(cvs.get("w") or 0) > float(cvs.get("h") or 0)
    canal_t = _canal_digitado(canal)
    apoio, temps = [], []
    try:
        apoio, temps = _apoio(pasta, ed, d, tema, quadro if (quadro and not temp) else None)
        import capa_arte
        capa_arte.TIPOS.get(tipo or "investigacao", capa_arte.render)(capa, quadro, apoio, d, canal_t, horizontal=horiz)
    except Exception as e:   # plano B: capa simples de antes
        print("capa_arte falhou:", repr(e))
        _desenhar(quadro, d, canal_t, capa, horizontal=horiz)
    for t in temps + ([quadro] if (quadro and temp) else []):
        try:
            Path(t).unlink()
        except Exception:
            pass
    prog(92, "Salvando descricao.txt…")
    txt = ("TÍTULOS PARA O VÍDEO\n" + "\n".join(f"{i}. {t}" for i, t in enumerate(d["titulos"], 1)) +
           "\n\nDESCRIÇÃO\n" + d["descricao"] + "\n\nHASHTAGS\n" + " ".join(d["hashtags"]) + "\n")
    (pasta / "descricao.txt").write_text(txt, encoding="utf-8")
    return {"capa": str(capa), "descricao": str(pasta / "descricao.txt"), "texto": d}


if __name__ == "__main__":
    print(criar(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "llama3.2:3b"))
