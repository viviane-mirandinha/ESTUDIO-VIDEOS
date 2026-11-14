r"""compor.py - junta frames do Blender + brilho (bloom) + etiquetas/selos/check + legenda 1 palavra + mix -> MP4 final.
Uso: python -X utf8 compor.py PROJETO SAIDA.mp4 [--teste SEG]
Legenda: Montserrat ExtraBold ~124 px, branca, contorno preto, keyword amarela, centro a 70% da altura (y=1344), "pop" de entrada.
Etiqueta: retangulo escuro + barra amarela a esquerda + texto branco CAIXA ALTA, y~300 (v2, igual a ref). Selo: canto sup. esquerdo, y=250, bolinha colorida.
Area segura IG: nada nos 220 px de cima, 380 de baixo, 120 da direita (e 60 da esquerda).
Saida extra: PROJETO\conferencia.jpg (12 quadros 4x3) -> conferir SO essa folha.
"""
import argparse, json, os, re, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import anc
ap = argparse.ArgumentParser(); ap.add_argument("projeto"); ap.add_argument("saida"); ap.add_argument("--teste", type=float, default=0)
a = ap.parse_args(); W = a.projeto
words, END, T, cfg = anc.carregar(W)
D = json.load(open(os.path.join(W, "dados.json"), encoding="utf8"))
FONT = r"kits\FERRAMENTAS\ROBLOX\fonts\Montserrat-ExtraBold.otf"
WID, HEI, FPS = 1080, 1920, 30
SAFE_L, SAFE_R, SAFE_T, SAFE_B = 60, WID - 120, 220, HEI - 380
YEL = (255, 210, 63); WHITE = (255, 255, 255)
AMAR = {x.lower() for x in D.get("amarelas", [])}
def clean(w): return re.sub(r"[^\w+\-]", "", w)
_fc = {}
def font(sz):
    if sz not in _fc: _fc[sz] = ImageFont.truetype(FONT, sz)
    return _fc[sz]

# ---------- legenda (pre-render de cada palavra) ----------
CAP = {}
def cap_img(i):
    if i in CAP: return CAP[i]
    txt = clean(words[i]["w"]); col = YEL if txt.lower() in AMAR else WHITE
    sz = 124
    while True:
        f = font(sz); bb = f.getbbox(txt, stroke_width=11)
        if bb[2] - bb[0] <= (SAFE_R - SAFE_L) - 60 or sz < 70: break
        sz -= 4
    w_, h_ = bb[2] - bb[0] + 40, bb[3] - bb[1] + 50
    im = Image.new("RGBA", (w_, h_), (0, 0, 0, 0))
    sh = Image.new("RGBA", (w_, h_), (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((20 - bb[0] + 4, 20 - bb[1] + 8), txt, font=f, fill=(0, 0, 0, 150), stroke_width=11, stroke_fill=(0, 0, 0, 150))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    ImageDraw.Draw(im).text((20 - bb[0], 20 - bb[1]), txt, font=f, fill=col + (255,), stroke_width=11, stroke_fill=(10, 10, 14, 255))
    CAP[i] = im; return im
CAP_CX = (SAFE_L + SAFE_R) // 2; CAP_CY = int(HEI * 0.70)

# ---------- etiquetas / selos / check ----------
def pill(txt, big=False):
    f = font(64 if big else 46); bb = f.getbbox(txt); tw, th = bb[2] - bb[0], bb[3] - bb[1]
    px, py = (48, 28) if big else (36, 22)
    w_, h_ = min(tw + 2 * px + 16, SAFE_R - SAFE_L - 20), th + 2 * py
    im = Image.new("RGBA", (w_ + 20, h_ + 26), (0, 0, 0, 0))
    # v2 (igual a ref): retangulo escuro de canto pouco arredondado + barra amarela na esquerda + contorno amarelo fino
    rr = 16
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((10, 16, w_ + 10, h_ + 16), rr, fill=(0, 0, 0, 120))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(7)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((10, 8, w_ + 10, h_ + 8), rr, fill=(22, 24, 30, 228), outline=YEL + (150,), width=2)
    d.rounded_rectangle((10, 8, 22, h_ + 8), 6, fill=YEL + (255,))
    d.text((10 + (w_ - tw) // 2 + 9 - bb[0], 8 + py - bb[1]), txt, font=f, fill=WHITE + (255,))
    return im
def selo(txt, cor):
    f = font(34); bb = f.getbbox(txt); tw, th = bb[2] - bb[0], bb[3] - bb[1]
    w_, h_ = tw + 86, th + 30
    im = Image.new("RGBA", (w_, h_), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    rgb = tuple(int(cor[i:i + 2], 16) for i in (1, 3, 5))
    d.rounded_rectangle((0, 0, w_ - 1, h_ - 1), 12, fill=(16, 16, 20, 215), outline=rgb + (180,), width=2)
    d.ellipse((22, h_ // 2 - 10, 42, h_ // 2 + 10), fill=rgb + (255,))
    d.text((58 - bb[0], 15 - bb[1]), txt, font=f, fill=rgb + (255,)); return im
def check_img():
    s = 150; im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((6, 6, s - 6, s - 6), fill=(18, 24, 22, 225), outline=(61, 220, 132, 255), width=6)
    d.line([(42, 78), (66, 102), (110, 52)], fill=(61, 220, 132, 255), width=15, joint="curve"); return im
ETQ = [(T(e["de"]) - 0.03, T(e["ate"]) - 0.06, pill(e["texto"], e.get("grande"))) for e in D.get("etiquetas", [])]
SEL = [(T(e["de"]) - 0.05, T(e["ate"]) - 0.06, selo(e["texto"], e["cor"])) for e in D.get("selos", [])]
CHK = [(T(e["de"]) - 0.03, T(e["ate"]) - 0.06, e["x"], e["y"]) for e in D.get("checks", [])]
TIN = [(T(e["de"]) - 0.05, T(e["ate"]) - 0.05, e["tipo"]) for e in D.get("tintas", [])]
CHKI = check_img()
def pop(t, t0, t1, d=0.14):
    """escala/opacidade: entrada com backease, saida rapida"""
    if t < t0 or t >= t1: return 0, 0
    x = min(1, (t - t0) / d); c1 = 1.7; c3 = c1 + 1; s = 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
    o = min(1, x * 2) * min(1, (t1 - t) / 0.08); return 0.7 + 0.3 * s, o
def paste(base, im, cx, cy, sc=1.0, op=1.0):
    if op <= 0: return
    if abs(sc - 1) > 0.01: im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BICUBIC)
    if op < 0.999: im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * op)))
    x = int(cx - im.width / 2); y = int(cy - im.height / 2)
    x = max(SAFE_L - 10, min(x, SAFE_R + 10 - im.width)); base.alpha_composite(im, (x, max(0, y)))
yy, xx = np.ogrid[:HEI, :WID]
VIG = (1 - 0.22 * (((xx - WID / 2) / (WID * 0.75)) ** 2 + ((yy - HEI / 2) / (HEI * 0.75)) ** 2)).astype(np.float32)[..., None]
def bloom(img):
    a_ = np.asarray(img).astype(np.float32) / 255
    lum = a_.max(axis=2); m = np.clip((lum - 0.78) / 0.22, 0, 1)[..., None] * a_
    sm = Image.fromarray((m * 255).astype(np.uint8)).resize((WID // 4, HEI // 4), Image.BILINEAR)
    b = (np.asarray(sm.filter(ImageFilter.GaussianBlur(5))).astype(np.float32) * 0.9 + np.asarray(sm.filter(ImageFilter.GaussianBlur(16))).astype(np.float32) * 0.8) / 255
    b = np.asarray(Image.fromarray((np.clip(b, 0, 1) * 255).astype(np.uint8)).resize((WID, HEI), Image.BILINEAR)).astype(np.float32) / 255
    return (1 - (1 - a_) * (1 - b * 0.85)) * VIG
def raiox(o):
    """v2: tinta fria SUAVE (a ref quase nao tinge; o que brilha sao as pernas do passarinho)"""
    g = o.mean(axis=2, keepdims=True); return np.clip(0.78 * o + 0.22 * g * np.array([0.6, 0.85, 1.2], np.float32), 0, 1)

NF = int(END * FPS) if not a.teste else int(a.teste * FPS)
fr_dir = os.path.join(W, "frames")
cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{WID}x{HEI}", "-r", str(FPS), "-i", "-",
       "-i", os.path.join(W, "audio", "mix.wav"), "-map", "0:v", "-map", "1:a",
       "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-maxrate", "10M", "-bufsize", "16M", "-profile:v", "high", "-level", "4.1",
       "-g", "60", "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-shortest", "-movflags", "+faststart", a.saida]
os.makedirs(os.path.dirname(os.path.abspath(a.saida)), exist_ok=True)
ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
wi = 0; last = None; faltando = 0
for f in range(NF):
    t = f / FPS; p = os.path.join(fr_dir, f"f{f:04d}.png")
    if os.path.exists(p): last = p
    else: faltando += 1
    o = bloom(Image.open(last).convert("RGB"))
    if any(t0 <= t < t1 and k == "raiox" for t0, t1, k in TIN): o = raiox(o)
    base = Image.fromarray((np.clip(o, 0, 1) * 255).astype(np.uint8)).convert("RGBA")
    for t0, t1, im in SEL:
        sc, op = pop(t, t0, t1, 0.12)
        if op > 0:
            im2 = im if op >= 0.999 else im.copy()
            if op < 0.999: im2.putalpha(im.getchannel("A").point(lambda v: int(v * op)))
            base.alpha_composite(im2, (SAFE_L + 10, 250))
    for t0, t1, im in ETQ:
        sc, op = pop(t, t0, t1); paste(base, im, (SAFE_L + SAFE_R) // 2, 300 + im.height // 2, sc, op)
    for t0, t1, x, y in CHK:
        sc, op = pop(t, t0, t1, 0.2); paste(base, CHKI, x, y, sc, op)
    while wi + 1 < len(words) and t >= words[wi + 1]["s"] - 0.03: wi += 1
    t0 = words[wi]["s"] - 0.03; nxt = words[wi + 1]["s"] - 0.03 if wi + 1 < len(words) else words[-1]["e"] + 0.35
    if t0 <= t < nxt:
        sc, op = pop(t, t0, nxt + 0.2, 0.1); paste(base, cap_img(wi), CAP_CX, CAP_CY, sc, 1.0)
    ff.stdin.write(base.convert("RGB").tobytes())
    if f % 300 == 0: print("compor", f, "/", NF, flush=True)
ff.stdin.close(); ff.wait()
if faltando: print("AVISO:", faltando, "quadros faltando (repetiu o anterior)")
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", a.saida], capture_output=True, text=True).stdout)
sheet = os.path.join(W, "conferencia.jpg")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", a.saida, "-vf", f"fps=12/{dur:.3f},scale=270:-1,tile=4x3", "-frames:v", "1", sheet], check=True)
print("OK", a.saida, round(dur, 2), "s | folha:", sheet)
