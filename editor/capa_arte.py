# capa_arte.py — desenha a capa como uma MONTAGEM (colagem editorial sutil), em 9:16 ou 16:9:
#   fundo = foto principal desfocada + cor dominante + brilho + vinheta + granulado
#   atrás  = 2-3 imagens de apoio do próprio vídeo (levemente inclinadas, dessaturadas, "fotos presas")
#   frente = a foto do ASSUNTO principal (inteira, moldura fina, sombra)
#   texto  = categoria, título com UMA palavra em destaque, 3 "fichas" de fatos reais do vídeo, @canal
import math
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

RAIZ = Path(__file__).resolve().parent.parent
FONTES = RAIZ / "recursos" / "fontes"
AMARELO = (255, 205, 60)
BRANCO = (255, 255, 255)
BG = (11, 12, 16)


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


def _cobrir(img, w, h):
    r = max(w / img.width, h / img.height)
    img = img.resize((int(img.width * r) + 1, int(img.height * r) + 1), Image.LANCZOS)
    x, y = (img.width - w) // 2, (img.height - h) // 2
    return img.crop((x, y, x + w, y + h))


def _caber(img, mw, mh):
    r = min(mw / img.width, mh / img.height)
    return img.resize((max(1, int(img.width * r)), max(1, int(img.height * r))), Image.LANCZOS)


def _cor_dominante(img):
    p = np.asarray(img.convert("RGB").resize((48, 48)), dtype=np.float32).reshape(-1, 3)
    mx, mn = p.max(1), p.min(1)
    sat = (mx - mn) / (mx + 1)
    pesos = sat * (0.4 + mx / 255.0) + 0.02   # prefere cores vivas e claras
    c = (p * pesos[:, None]).sum(0) / pesos.sum()
    c = np.clip(c * (1.0 + 0.5 * (1 - (c.max() - c.min()) / 255.0)), 0, 255)   # um pouco mais viva
    return tuple(int(v) for v in c)


def _sombra(cartao, raio=26, desloc=(0, 18), alfa=150):
    """Cartão RGBA → (imagem com sombra, margem). """
    m = raio * 3
    base = Image.new("RGBA", (cartao.width + 2 * m, cartao.height + 2 * m), (0, 0, 0, 0))
    a = cartao.split()[3].point(lambda v: int(v * alfa / 255))
    sh = Image.new("RGBA", cartao.size, (0, 0, 0, 255))
    sh.putalpha(a)
    base.paste(sh, (m + desloc[0], m + desloc[1]), sh)
    base = base.filter(ImageFilter.GaussianBlur(raio))
    base.alpha_composite(cartao, (m, m))
    return base, m


def _cartao(img, borda=0, raio=18, cor_borda=(238, 236, 228), dessat=0.0, escurecer=1.0, tinta=None):
    im = img.convert("RGB")
    if dessat > 0:
        cinza = im.convert("L").convert("RGB")
        im = Image.blend(im, cinza, dessat)
    if tinta is not None:
        im = Image.blend(im, Image.new("RGB", im.size, tinta), 0.18)
    if escurecer != 1.0:
        im = im.point(lambda v: int(v * escurecer))
    w, h = im.width + 2 * borda, im.height + 2 * borda
    cart = Image.new("RGBA", (w, h), cor_borda + (255,) if borda else (0, 0, 0, 0))
    cart.paste(im, (borda, borda))
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), raio, fill=255)
    cart.putalpha(m)
    return cart


def _colar_inclinado(cv, cart, centro, graus, raio_sombra=22, alfa=150):
    cs, m = _sombra(cart, raio_sombra, (0, 14), alfa)
    cs = cs.rotate(graus, resample=Image.BICUBIC, expand=True)
    x, y = int(centro[0] - cs.width / 2), int(centro[1] - cs.height / 2)
    cv.alpha_composite(cs, (x, y))


def _fundo(W, H, hero, cor):
    cv = Image.new("RGBA", (W, H), BG + (255,))
    if hero is not None:
        bl = _cobrir(hero.convert("RGB"), W, H).filter(ImageFilter.GaussianBlur(38)).point(lambda v: int(v * 0.42))
        cv.paste(bl, (0, 0))
    # lavagem de cor (cor dominante da foto) em degradê diagonal
    ar = np.zeros((H, W, 4), dtype=np.uint8)
    yy, xx = np.mgrid[0:H, 0:W]
    t = np.clip((xx / W * 0.45 + yy / H * 0.55), 0, 1)
    ar[..., 0], ar[..., 1], ar[..., 2] = cor
    ar[..., 3] = (np.sin(t * math.pi) * 70).astype(np.uint8)
    cv.alpha_composite(Image.fromarray(ar, "RGBA"))
    return cv


def _brilho(cv, centro, raio, cor, forca=0.55):
    W, H = cv.size
    g = Image.new("L", (W, H), 0)
    ImageDraw.Draw(g).ellipse((centro[0] - raio, centro[1] - raio, centro[0] + raio, centro[1] + raio), fill=int(255 * forca))
    g = g.filter(ImageFilter.GaussianBlur(raio * 0.55))
    cv.paste(Image.new("RGB", (W, H), cor), (0, 0), g)


def _acabamento(cv):
    """vinheta + granulado fino (cara de capa de documentário)."""
    W, H = cv.size
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    vig = np.clip(1.0 - 0.34 * np.clip(d - 0.55, 0, None) ** 1.4, 0.55, 1.0)
    a = np.asarray(cv.convert("RGB"), dtype=np.float32) * vig[..., None]
    rng = np.random.default_rng(7)
    a += rng.normal(0, 4.5, (H, W, 1)).astype(np.float32)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB")


def _quebrar(draw, palavras, fonte, largura):
    linhas, atual = [], []
    for p in palavras:
        if atual and draw.textlength(" ".join(atual + [p]), font=fonte) > largura:
            linhas.append(atual)
            atual = [p]
        else:
            atual.append(p)
    if atual:
        linhas.append(atual)
    return linhas


def _titulo(cv, d, x0, y0, largura, tams, max_linhas, max_h=None):
    """Desenha o título (uma palavra em amarelo com brilho). Retorna o y onde terminou."""
    dr = ImageDraw.Draw(cv, "RGBA")
    palavras = d["titulo_capa"].strip().split()
    destaque = d["destaque"].lower().strip("?.,!:")
    for tam in tams:
        fonte = _titulo_font(tam)
        linhas = _quebrar(dr, palavras, fonte, largura)
        if len(linhas) <= max_linhas and (max_h is None or len(linhas) * tam * 1.07 <= max_h):
            break
    W, H = cv.size
    y = y0
    for ln in linhas:
        x = x0
        for p in ln:
            amarelo = p.lower().strip("?.,!:") == destaque
            if amarelo:
                br = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                ImageDraw.Draw(br).text((x, y), p, font=fonte, fill=AMARELO + (150,))
                al = br.filter(ImageFilter.GaussianBlur(16)).split()[3].point(lambda v: int(v * 0.55))
                cv.paste(Image.new("RGB", (W, H), AMARELO), (0, 0), al)
                dr = ImageDraw.Draw(cv, "RGBA")
            dr.text((x + 3, y + 5), p, font=fonte, fill=(0, 0, 0, 120))
            dr.text((x, y), p, font=fonte, fill=AMARELO if amarelo else BRANCO)
            x += dr.textlength(p + " ", font=fonte)
        y += int(tam * 1.07)
    return y


def _etiqueta(cv, cat, x, y, escala=1.0):
    dr = ImageDraw.Draw(cv, "RGBA")
    f = _fonte(["JetBrainsMono-Bold.woff", "JetBrainsMono.ttf", "Inter-Bold.ttf"], int(27 * escala))
    trilho = int(7 * escala)
    tw = sum(dr.textlength(c, font=f) + trilho for c in cat)
    h = int(58 * escala)
    dr.rounded_rectangle((x, y, x + tw + 90 * escala, y + h), h // 2, fill=(34, 36, 48, 245))
    r = int(14 * escala)
    dr.ellipse((x + 22 * escala, y + h / 2 - r, x + 22 * escala + 2 * r, y + h / 2 + r), fill=AMARELO)
    cx = x + 22 * escala + 2 * r + 16 * escala
    for c in cat:
        dr.text((cx, y + h / 2), c, font=f, fill=(230, 232, 240), anchor="lm")
        cx += dr.textlength(c, font=f) + trilho


def _selo_canal(cv, canal, x1, y0, escala=1.0):
    if not canal:
        return
    dr = ImageDraw.Draw(cv, "RGBA")
    f = _fonte(["Inter-Bold.ttf", "Inter-ExtraBold.ttf"], int(28 * escala))
    tw = dr.textlength(canal, font=f)
    h = int(62 * escala)
    dr.rounded_rectangle((x1 - tw - 52 * escala, y0, x1, y0 + h), 16, fill=(24, 26, 34, 235))
    dr.text((x1 - 26 * escala - tw, y0 + h / 2), canal, font=f, fill=BRANCO, anchor="lm")


def _ficha(cv, fato, x, y, w, escala=1.0):
    """Ficha de fato: número/data grande em amarelo + legenda curta. Retorna altura."""
    dest, rot = str(fato["destaque"]).upper(), str(fato["rotulo"])
    h = int(112 * escala)
    fa = _fonte(["Anton-Regular.ttf", "Montserrat-Black.ttf"], int(52 * escala))
    fb = _fonte(["Inter-Bold.ttf", "Inter-ExtraBold.ttf"], int(23 * escala))
    glass = Image.new("RGBA", (int(w), h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glass)
    gd.rounded_rectangle((0, 0, w - 1, h - 1), int(18 * escala), fill=(14, 15, 20, 214), outline=(255, 255, 255, 40), width=2)
    gd.rounded_rectangle((0, int(14 * escala), int(7 * escala), h - int(14 * escala)), 4, fill=AMARELO + (255,))
    tamw = w - 44 * escala
    while fa.getlength(dest) > tamw and fa.size > 24:
        fa = ImageFont.truetype(fa.path, fa.size - 2)
    gd.text((int(26 * escala), int(10 * escala)), dest, font=fa, fill=AMARELO)
    while fb.getlength(rot) > tamw and fb.size > 14:
        fb = ImageFont.truetype(fb.path, fb.size - 1)
    gd.text((int(26 * escala), h - int(36 * escala)), rot, font=fb, fill=(226, 228, 236))
    cs, m = _sombra(glass, 14, (0, 8), 120)
    cv.alpha_composite(cs, (int(x - m), int(y - m)))
    return h


def render(destino: Path, hero_path, apoio_paths, d, canal, horizontal=False):
    W, H = (1920, 1080) if horizontal else (1080, 1920)
    esc = 1.0
    hero = Image.open(hero_path).convert("RGB") if hero_path else None
    apoio = []
    for p in apoio_paths or []:
        try:
            apoio.append(Image.open(p).convert("RGB"))
        except Exception:
            pass
    cor = _cor_dominante(hero) if hero is not None else (60, 70, 100)
    fatos = [f for f in (d.get("fatos") or []) if f.get("destaque") and f.get("rotulo")][:3]
    rnd = random.Random(sum(map(ord, d.get("titulo_capa", "x"))))

    cv = _fundo(W, H, hero, cor)

    if not horizontal:
        # ------------------------------------------------------------ 9:16
        _brilho(cv, (W // 2, 1250), 520, cor, 0.42)
        # degradê do topo (área do título)
        g = Image.new("L", (1, H), 0)
        for y in range(H):
            g.putpixel((0, y), 235 if y < H * 0.22 else max(0, int(235 * (1 - (y - H * 0.22) / (H * 0.2)))))
        cv.paste(Image.new("RGB", (W, H), BG), (0, 0), g.resize((W, H)))
        cv = cv.convert("RGBA")
        _etiqueta(cv, d["categoria"], 70, 220)
        y_fim = _titulo(cv, d, 74, 310, W - 150, (112, 104, 96, 88, 80, 72), 4)
        zona_top = y_fim + 70
        zona_bot = H - (210 if fatos else 90)
        # imagens de apoio atrás do herói (inclinadas, apagadas)
        pos = [(190, zona_top + 290, -8), (W - 175, zona_top + 255, 6), (W - 215, zona_bot - 230, -5)]
        for im, (cx, cy, gr) in zip(apoio[:3], pos):
            c = _cartao(_caber(im, 380, 470), borda=9, raio=12, dessat=0.55, escurecer=0.72, tinta=cor)
            _colar_inclinado(cv, c, (cx, cy), gr, 18, 170)
        if hero is not None:
            hi = _caber(hero, 860, max(300, zona_bot - zona_top))
            c = _cartao(hi, borda=8, raio=20)
            cy = zona_top + (zona_bot - zona_top) / 2
            _colar_inclinado(cv, c, (W / 2, cy), -1.6, 30, 190)
        # fichas de fatos (faixa inferior)
        if fatos:
            n = len(fatos)
            gap = 22
            wf = (W - 2 * 56 - gap * (n - 1)) / n
            yb = H - 150
            for i, f in enumerate(fatos):
                _ficha(cv, f, 56 + i * (wf + gap), yb, wf, 0.92)
        _selo_canal(cv, canal, W - 30, 50)
    else:
        # ------------------------------------------------------------ 16:9
        _brilho(cv, (1430, 540), 520, cor, 0.42)
        g = Image.new("L", (W, 1), 0)
        for x in range(W):
            g.putpixel((x, 0), 240 if x < W * 0.30 else max(0, int(240 * (1 - (x - W * 0.30) / (W * 0.22)))))
        cv.paste(Image.new("RGB", (W, H), BG), (0, 0), g.resize((W, H)))
        cv = cv.convert("RGBA")
        _etiqueta(cv, d["categoria"], 80, 130)
        y_fim = _titulo(cv, d, 80, 215, 880, (124, 112, 104, 96, 88, 80, 72), 5, max_h=520 if fatos else 640)
        pos = [(1090, 300, -8), (1830, 330, 7), (1800, 880, -5)]
        for im, (cx, cy, gr) in zip(apoio[:3], pos):
            c = _cartao(_caber(im, 330, 270), borda=8, raio=12, dessat=0.55, escurecer=0.72, tinta=cor)
            _colar_inclinado(cv, c, (cx, cy), gr, 18, 170)
        if hero is not None:
            hi = _caber(hero, 760, 800)
            c = _cartao(hi, borda=8, raio=20)
            _colar_inclinado(cv, c, (1400, 560), -1.6, 30, 190)
        if fatos:
            n = len(fatos)
            gap = 20
            wf = min(300, (900 - gap * (n - 1)) / n)
            for i, f in enumerate(fatos):
                _ficha(cv, f, 80 + i * (wf + gap), H - 190, wf, 0.9)
        _selo_canal(cv, canal, W - 50, 45)

    out = _acabamento(cv.convert("RGB"))
    out.save(destino, "JPEG", quality=94, subsampling=0)
    return destino


# ============================================================ tipo "curiosidade"
# Só o título sobre fundo preto; o rosto/foco do vídeo vai surgindo do escuro num degradê suave.
def _foco(img):
    """Onde está o 'assunto' da foto (fração x, y): centro de massa da energia de bordas (sem IA)."""
    g = np.asarray(img.convert("L").resize((96, 96)), dtype=np.float32)
    e = np.hypot(np.diff(g, axis=1)[:-1, :], np.diff(g, axis=0)[:, :-1])
    yy, xx = np.mgrid[0:e.shape[0], 0:e.shape[1]]
    c = 1.0 - 0.5 * (np.hypot((xx / e.shape[1] - 0.5), (yy / e.shape[0] - 0.5)) / 0.7071)   # leve preferência pelo centro
    e = e * c + 1e-3
    return float((e.sum(0) * np.arange(e.shape[1])).sum() / e.sum() / e.shape[1]), float((e.sum(1) * np.arange(e.shape[0])).sum() / e.sum() / e.shape[0])


def _cobrir_foco(img, w, h):
    fx, fy = _foco(img)
    r = max(w / img.width, h / img.height)
    im = img.resize((int(img.width * r) + 1, int(img.height * r) + 1), Image.LANCZOS)
    x = int(min(max(fx * im.width - w / 2, 0), im.width - w))
    y = int(min(max(fy * im.height - h / 2, 0), im.height - h))
    return im.crop((x, y, x + w, y + h))


def _suave(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)


def render_curiosidade(destino: Path, hero_path, apoio_paths, d, canal, horizontal=False):
    W, H = (1920, 1080) if horizontal else (1080, 1920)
    cv = Image.new("RGB", (W, H), (0, 0, 0))
    if hero_path:
        hero = Image.open(hero_path).convert("RGB")
        if horizontal:
            zw, zh = 1000, H
            foto = _cobrir_foco(hero, zw, zh)
            t = np.linspace(0, 1, zw)[None, :].repeat(zh, 0)
            alfa = _suave(t / 0.55)                       # some no preto à esquerda, aparece aos poucos
            alfa *= _suave(np.linspace(0, 1, zh) / 0.06)[:, None] * _suave((1 - np.linspace(0, 1, zh)) / 0.06)[:, None]
            pos = (W - zw, 0)
        else:
            zw, zh = W, 1420
            foto = _cobrir_foco(hero, zw, zh)
            t = np.linspace(0, 1, zh)[:, None].repeat(zw, 1)
            alfa = _suave(t / 0.6)
            pos = (0, H - zh)
        foto = foto.point(lambda v: int(v * 0.92))
        m = Image.fromarray((alfa * 255).astype(np.uint8), "L")
        cv.paste(foto, pos, m)
    cv = cv.convert("RGBA")
    if horizontal:
        scratch = Image.new("RGB", (W, H))
        alt = _titulo(scratch, d, 80, 0, 760, (130, 120, 110, 100, 90, 80, 72), 5, max_h=760) - 0
        y0 = max(90, int((H - alt) / 2))
        _titulo(cv, d, 80, y0, 760, (130, 120, 110, 100, 90, 80, 72), 5, max_h=760)
        _selo_canal(cv, canal, W - 50, 45)
    else:
        _titulo(cv, d, 74, 150, W - 150, (118, 108, 100, 92, 84, 76, 68), 4)
        _selo_canal(cv, canal, W - 30, 50)
    _acabamento(cv.convert("RGB")).save(destino, "JPEG", quality=94, subsampling=0)
    return destino


# tipos de capa disponíveis (id usado no modal "Criar capa"); novos tipos entram aqui
TIPOS = {"investigacao": render, "curiosidade": render_curiosidade}
