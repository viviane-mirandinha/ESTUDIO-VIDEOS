r"""compor_texto.py - MODO SEM FALA (ref so com musica + texto, formato "E se X dobrasse a cada vez?").
Junta frames do Blender + bloom + HUD de contador exponencial + cartao de texto por linha + gancho + CTA em texto -> MP4.
Uso: python -I -X utf8 compor_texto.py PROJETO SAIDA.mp4 [--teste SEG]
dados.json:
  "hud": [["L:k", n], ...]  contador (sobe do anterior ate n em 55% do cartao) | "hud_fim": "L:k" (some no CTA)
  "hud_base": valor na contagem 1 (dobra a cada contagem) | "hud_unidade": "km/h" | "hud_titulo": "ARRASTADA"
  "hud_tag": "x2 A CADA ARRASTADA" | "hud_rotulos": [[limite, "TEXTO"], ...] (primeiro limite > valor)
  "gancho": {"linha": 0, "destaques": [palavras com caixa vermelha]} | "cta": {"linha": N, "palavra": "RAPIDO"}
Layout (area segura IG): HUD x=70, y 270-480 | texto (Georgia negrito italico 74 px) y 545+ | nada abaixo de 1540.
Saida extra: PROJETO\conferencia.jpg (12 quadros 4x3).
"""
import argparse, json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import anc
ap = argparse.ArgumentParser(); ap.add_argument("projeto"); ap.add_argument("saida"); ap.add_argument("--teste", type=float, default=0)
a = ap.parse_args(); W = a.projeto
words, END, T, cfg = anc.carregar(W)
D = json.load(open(os.path.join(W, "dados.json"), encoding="utf8"))
MONT = r"kits\FERRAMENTAS\ROBLOX\fonts\Montserrat-ExtraBold.otf"
SERIF_BI = r"C:\Windows\Fonts\georgiaz.ttf"; SERIF_B = r"C:\Windows\Fonts\georgiab.ttf"
WID, HEI, FPS = 1080, 1920, 30
SAFE_L, SAFE_R = 70, WID - 130
RED = (226, 54, 54); YEL = (255, 210, 63); WHITE = (255, 255, 255)
_fc = {}
def font(p, sz):
    if (p, sz) not in _fc: _fc[(p, sz)] = ImageFont.truetype(p, sz)
    return _fc[(p, sz)]
def shadowed(im, blur=7, alpha=170, off=(0, 5)):
    a_ = im.getchannel("A"); sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sh.putalpha(a_.point(lambda v: v * alpha // 255))
    sh = sh.filter(ImageFilter.GaussianBlur(blur)); out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.alpha_composite(sh, off); out.alpha_composite(im); return out
def wrap(txt, f, maxw):
    ls, cur = [], ""
    for w in txt.split():
        t = (cur + " " + w).strip()
        if f.getlength(t) <= maxw or not cur: cur = t
        else: ls.append(cur); cur = w
    return ls + [cur]

# ---------------- linhas ----------------
LINES = {}
for w in words: LINES.setdefault(w["line"], []).append(w)
LST = sorted((L, ws[0]["s"], ws[-1]["e"]) for L, ws in LINES.items())
TXT = {L: " ".join(w["w"] for w in ws) for L, ws in LINES.items()}
G = D.get("gancho", {"linha": 0, "destaques": []}); CTA = D.get("cta", {"linha": LST[-1][0]})

def card_texto(txt):
    f = font(SERIF_BI, 74); ls = wrap(txt, f, SAFE_R - SAFE_L)
    lh = 92; im = Image.new("RGBA", (SAFE_R - SAFE_L + 40, lh * len(ls) + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i, l in enumerate(ls): d.text((20, 14 + i * lh), l, font=f, fill=WHITE + (255,), stroke_width=2, stroke_fill=(0, 0, 0, 120))
    return shadowed(im, 8, 200)
def card_gancho(txt, dest):
    f = font(MONT, 96); dest = {x.lower().strip("?.,!") for x in dest}
    ls = wrap(txt, f, SAFE_R - SAFE_L - 40); lh = 128
    im = Image.new("RGBA", (WID, lh * len(ls) + 60), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i, l in enumerate(ls):
        x = (WID - f.getlength(l)) / 2; y = 20 + i * lh
        for w in l.split():
            wl = f.getlength(w); bb = f.getbbox(w)
            if w.lower().strip("?.,!") in dest:
                d.rounded_rectangle((x - 14, y + bb[1] - 14, x + wl + 14, y + bb[3] + 14), 14, fill=RED + (255,))
                d.text((x, y), w, font=f, fill=WHITE + (255,))
            else:
                d.text((x, y), w, font=f, fill=WHITE + (255,), stroke_width=9, stroke_fill=(12, 12, 16, 255))
            x += wl + f.getlength(" ")
    return shadowed(im, 9, 190)
def card_cta(txt):
    pal = CTA.get("palavra") or txt.split()[-1]
    perg = txt[:txt.rfind("COMENTA")].strip() if "COMENTA" in txt else txt
    f = font(MONT, 70); ls = wrap(perg, f, SAFE_R - SAFE_L - 40); lh = 92
    f2 = font(MONT, 92); lab = f"COMENTA {pal}"; tw = f2.getlength(lab)
    H = lh * len(ls) + 210; im = Image.new("RGBA", (WID, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i, l in enumerate(ls):
        d.text(((WID - f.getlength(l)) / 2, 10 + i * lh), l, font=f, fill=WHITE + (255,), stroke_width=8, stroke_fill=(12, 12, 16, 255))
    y = 10 + lh * len(ls) + 34; x = (WID - tw) / 2
    d.rounded_rectangle((x - 34, y - 12, x + tw + 34, y + 122), 26, fill=YEL + (255,))
    d.text((x, y), lab, font=f2, fill=(16, 16, 20, 255))
    return shadowed(im, 10, 200)
CARD = {}
for L, s, e in LST:
    if L == G.get("linha"): CARD[L] = ("gancho", card_gancho(TXT[L], G.get("destaques", [])))
    elif L == CTA.get("linha"): CARD[L] = ("cta", card_cta(TXT[L]))
    else: CARD[L] = ("texto", card_texto(TXT[L]))
def line_at(t):
    cur = LST[0]
    for x in LST:
        if t >= x[1] - 1e-6: cur = x
    return cur

# ---------------- HUD ----------------
HUD = [(T(x), n) for x, n in D.get("hud", [])]
HUD_FIM = T(D["hud_fim"]) if D.get("hud_fim") else END + 1
BASE = D.get("hud_base", 1); UNI = D.get("hud_unidade", "km/h"); TIT = D.get("hud_titulo", "ARRASTADA")
TAG = D.get("hud_tag", "x2 A CADA ARRASTADA"); ROT = D.get("hud_rotulos", [])
def line_end(t0):
    nx = [s for _, s, _ in LST if s > t0 + 1e-3]; return nx[0] if nx else END
def count(t):
    prev = 0; c = 0.0
    for t0, n in HUD:
        if t < t0: break
        d = (line_end(t0) - t0) * 0.55; x = max(0.0, min(1.0, (t - t0) / max(d, 1e-3))); x = x * x * (3 - 2 * x)
        c = prev + (n - prev) * x if n > prev else n; prev = n
    return c
def fmt(v):
    if v < 1e6:
        s = f"{v:,.0f}".replace(",", "."); return f"{s} {UNI}"
    for lim, nome in ((1e12, "trilhões"), (1e9, "bilhões"), (1e6, "milhões")):
        if v >= lim:
            x = v / lim; s = (f"{x:.2f}" if x < 10 else f"{x:.1f}" if x < 100 else f"{x:.0f}").replace(".", ",")
            if nome == "milhões" and s == "1,00": nome = "milhão"
            return f"{s} {nome} de {UNI}"
def rotulo(v):
    for lim, txt in ROT:
        if v < lim: return txt
    return ROT[-1][1] if ROT else ""
_hc = {}
def hud_img(n):
    if n in _hc: return _hc[n]
    v = BASE * 2 ** (n - 1)
    im = Image.new("RGBA", (SAFE_R - SAFE_L + 30, 270), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text((6, 0), f"{TIT} {n}", font=font(MONT, 34), fill=(255, 255, 255, 215))
    fv = font(SERIF_B, 96); txt = fmt(v); sz = 96
    while fv.getlength(txt) > SAFE_R - SAFE_L - 10 and sz > 50: sz -= 4; fv = font(SERIF_B, sz)
    d.text((2, 40), txt, font=fv, fill=WHITE + (255,))
    d.text((6, 156), rotulo(v), font=font(MONT, 34), fill=(255, 255, 255, 235))
    ft = font(MONT, 26); tw = ft.getlength(TAG)
    d.rounded_rectangle((4, 206, 4 + tw + 28, 250), 9, fill=RED + (255,)); d.text((18, 212), TAG, font=ft, fill=WHITE + (255,))
    _hc[n] = shadowed(im, 6, 190, (0, 3)); return _hc[n]

# ---------------- bloom / vinheta ----------------
yy, xx = np.ogrid[:HEI, :WID]
VIG = (1 - 0.22 * (((xx - WID / 2) / (WID * 0.75)) ** 2 + ((yy - HEI / 2) / (HEI * 0.75)) ** 2)).astype(np.float32)[..., None]
GRAD = np.clip(1 - 0.45 * np.clip((620 - yy) / 620, 0, 1), 0, 1).astype(np.float32)[..., None]   # escurece o topo (leitura do HUD)
def bloom(img):
    a_ = np.asarray(img).astype(np.float32) / 255
    lum = a_.max(axis=2); m = np.clip((lum - 0.78) / 0.22, 0, 1)[..., None] * a_
    sm = Image.fromarray((m * 255).astype(np.uint8)).resize((WID // 4, HEI // 4), Image.BILINEAR)
    b = (np.asarray(sm.filter(ImageFilter.GaussianBlur(5))).astype(np.float32) * 0.9 + np.asarray(sm.filter(ImageFilter.GaussianBlur(16))).astype(np.float32) * 0.8) / 255
    b = np.asarray(Image.fromarray((np.clip(b, 0, 1) * 255).astype(np.uint8)).resize((WID, HEI), Image.BILINEAR)).astype(np.float32) / 255
    return (1 - (1 - a_) * (1 - b * 0.85)) * VIG
def fade(im, op):
    if op >= 0.999: return im
    im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * op))); return im

NF = int(END * FPS) if not a.teste else int(a.teste * FPS)
fr_dir = os.path.join(W, "frames")
os.makedirs(os.path.dirname(os.path.abspath(a.saida)), exist_ok=True)
# encode em PEDACOS de 240 quadros (se o ffmpeg morrer no meio - ex.: outra sessao matando ffmpeg.exe - refaz so o pedaco)
SEG = 240; segdir = os.path.join(W, "_seg"); os.makedirs(segdir, exist_ok=True)
def seg_cmd(out):
    return ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{WID}x{HEI}", "-r", str(FPS), "-i", "-",
            "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-maxrate", "10M", "-bufsize", "16M", "-profile:v", "high", "-level", "4.1",
            "-g", "60", "-pix_fmt", "yuv420p", "-r", "30", out]
last = None; faltando = 0; prev_n = -1; pulse_t = -9
def frame_img(f):
    global last, faltando, prev_n, pulse_t
    t = f / FPS; p = os.path.join(fr_dir, f"f{f:04d}.png")
    if os.path.exists(p): last = p
    else: faltando += 1
    L, s0, e0 = line_at(t); kind, card = CARD[L]
    o = bloom(Image.open(last).convert("RGB"))
    if HUD and HUD[0][0] <= t < HUD_FIM: o = o * GRAD
    base = Image.fromarray((np.clip(o, 0, 1) * 255).astype(np.uint8)).convert("RGBA")
    if HUD and HUD[0][0] <= t < HUD_FIM:
        n = max(1, int(count(t) + 1e-6))
        if n != prev_n: pulse_t = t; prev_n = n
        op = min(1.0, (t - HUD[0][0]) / 0.2) * min(1.0, (HUD_FIM - t) / 0.15)
        base.alpha_composite(fade(hud_img(n), op), (SAFE_L - 6, 262))
    k = min(1.0, (t - s0) / 0.18); op = k * k * (3 - 2 * k)
    if kind == "gancho":
        sc = 0.86 + 0.14 * (1 - (1 - k) ** 3); im = card if sc > 0.999 else card.resize((int(card.width * sc), int(card.height * sc)), Image.BICUBIC)
        base.alpha_composite(fade(im, op), ((WID - im.width) // 2, 300 + (card.height - im.height) // 2))
    elif kind == "cta":
        sc = 0.8 + 0.2 * (1 - (1 - k) ** 3) + 0.02 * math.sin(max(0, t - s0 - 0.4) * 5)
        im = card.resize((int(card.width * sc), int(card.height * sc)), Image.BICUBIC)
        base.alpha_composite(fade(im, op), ((WID - im.width) // 2, 300 + (card.height - im.height) // 2))
    else:
        base.alpha_composite(fade(card, op), (SAFE_L - 20, 555 + int(10 * (1 - op))))
    return base.convert("RGB").tobytes()
segs = []
for si, f0 in enumerate(range(0, NF, SEG)):
    f1 = min(NF, f0 + SEG); out = os.path.join(segdir, f"s{si:03d}.mp4"); segs.append(out)
    for tent in range(5):
        try:
            ff = subprocess.Popen(seg_cmd(out), stdin=subprocess.PIPE)
            for f in range(f0, f1): ff.stdin.write(frame_img(f))
            ff.stdin.close()
            if ff.wait() == 0: break
        except OSError:
            try: ff.kill()
            except Exception: pass
        print("pedaco", si, "falhou, refazendo", flush=True)
    else: raise SystemExit("encode falhou 5x no pedaco %d" % si)
    print("compor", f1, "/", NF, flush=True)
lst = os.path.join(segdir, "lista.txt"); open(lst, "w").write("".join(f"file '{x}'\n" for x in segs))
subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", os.path.join(W, "audio", "mix.wav"),
                "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-shortest", "-movflags", "+faststart", a.saida], check=True)
if faltando: print("AVISO:", faltando, "quadros faltando (repetiu o anterior)")
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", a.saida], capture_output=True, text=True).stdout)
sheet = os.path.join(W, "conferencia.jpg")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", a.saida, "-vf", f"fps=12/{dur:.3f},scale=270:-1,tile=4x3", "-frames:v", "1", sheet], check=True)
print("OK", a.saida, round(dur, 2), "s | folha:", sheet)
