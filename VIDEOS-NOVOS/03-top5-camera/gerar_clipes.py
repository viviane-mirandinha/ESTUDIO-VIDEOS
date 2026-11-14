# Gera os clipes "câmera de segurança" do vídeo 03 (look CCTV + evento simulado).
# Fontes: frames de vídeos/fotos Pixabay (raw/*.jpg). Saída: clips/*.mp4 + clips/coords.json
import json, math, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FPS = 15
PW, PH = 940, 705           # área da "câmera" 4:3 dentro do quadro 1280x720
PX, PY = 170, 7
OUT = "clips"
FONT = ImageFont.truetype(r"C:\Windows\Fonts\consolab.ttf", 26)


def load(name, crop_cx=0.5):
    im = Image.open(f"raw/{name}.jpg").convert("RGB")
    W, H = im.size
    tw = int(H * 4 / 3)
    if tw <= W:
        x0 = int(min(max(crop_cx * W - tw / 2, 0), W - tw)); im = im.crop((x0, 0, x0 + tw, H))
    else:
        th = int(W * 3 / 4); y0 = (H - th) // 2; im = im.crop((0, y0, W, y0 + th))
    return im.resize((PW, PH), Image.LANCZOS)


BASE = {
    "corredor": load("corredor"),
    "garagem": load("garagem"),
    "carro": load("carro", crop_cx=(633 + 323) / 1280),
    "cozinha": load("cozinha"),
    "crianca": load("crianca"),
}

# pontos de interesse (normalizados na área da câmera)
POI = {"porta": (0.474, 0.396), "parede": (0.50, 0.55), "carro": (0.58, 0.70),
       "prateleira": (0.54, 0.37), "rosto": (0.37, 0.34), "canto": (0.08, 0.10)}


def silhueta(h, pale=False):
    """silhueta humana borrada RGBA (altura h)."""
    w = int(h * 0.42)
    im = Image.new("L", (w, h), 0); d = ImageDraw.Draw(im)
    hr = h * 0.09
    d.ellipse((w / 2 - hr, 0, w / 2 + hr, 2 * hr), fill=255)
    d.polygon([(w * .22, h * .2), (w * .78, h * .2), (w * .86, h * .55), (w * .7, h * .56), (w * .66, h),
               (w * .52, h), (w * .5, h * .62), (w * .48, h), (w * .34, h), (w * .3, h * .56), (w * .14, h * .55)], fill=255)
    a = im.filter(ImageFilter.GaussianBlur(h * 0.02))
    col = (215, 215, 215) if pale else (12, 12, 12)
    rgba = Image.new("RGBA", (w, h), col + (0,)); rgba.putalpha(a)
    return rgba


SIL = silhueta(330)


def figura_crianca(alpha, turn, smile):
    """figura pálida sentada (cabeça+tronco) com olhos e sorriso."""
    w, h = 190, 250
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    hx = w / 2 - 28 * turn; hy = 55
    d.ellipse((w * .18, 95, w * .82, h + 40), fill=(225, 230, 225, int(95 * alpha)))      # tronco
    d.ellipse((hx - 42, hy - 48, hx + 42, hy + 48), fill=(235, 240, 235, int(120 * alpha)))  # cabeça
    ex = hx - 14 - 10 * turn
    for dx in (0, 30):
        d.ellipse((ex + dx - 5, hy - 12, ex + dx + 5, hy), fill=(0, 0, 0, int(200 * alpha)))
    if smile > 0:
        d.arc((ex - 6, hy + 2, ex + 36, hy + 30), 15, 165, fill=(0, 0, 0, int(190 * alpha * smile)), width=3)
    return im.filter(ImageFilter.GaussianBlur(3.5))


def ramp(t, a, b):
    return min(max((t - a) / (b - a), 0.0), 1.0)


def cena(nome, t):
    """composição da cena no tempo de história t (PIL RGB, PWxPH)."""
    if nome == "corredor":
        im = BASE["corredor"].copy()
        o = ramp(t, 2.6, 3.1) * (1 - ramp(t, 3.8, 4.2))
        if o > 0:
            cx, cy = POI["porta"][0] * PW, POI["porta"][1] * PH; dw, dh = 85, 211
            x0 = cx - dw / 2; y0 = cy - dh / 2
            ov = Image.new("RGBA", (PW, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
            d.rectangle((x0, y0, x0 + dw * o, y0 + dh), fill=(250, 250, 240, int(230 * o)))
            d.polygon([(x0, y0 + dh), (x0 + dw * o, y0 + dh), (x0 + dw * o * 1.9 + 30, y0 + dh + 120), (x0 - 30, y0 + dh + 120)],
                      fill=(240, 240, 230, int(70 * o)))
            im = Image.alpha_composite(im.convert("RGBA"), ov.filter(ImageFilter.GaussianBlur(3))).convert("RGB")
        return im
    if nome == "garagem":
        im = BASE["garagem"].copy()
        k = ramp(t, 0.3, 2.5)
        if 0 < k < 1:
            a = math.sin(math.pi * k) ** 0.6
            s = SIL.copy(); s.putalpha(s.getchannel("A").point(lambda v: int(v * 0.62 * a)))
            x = int(PW * (0.78 - 0.5 * k)); y = int(PH * 0.82) - s.size[1]
            im = im.convert("RGBA"); im.alpha_composite(s, (x - s.size[0] // 2, y)); im = im.convert("RGB")
        return im
    if nome == "carro":
        im = BASE["carro"].copy()
        if 1.2 <= t <= 4.0:
            cx, cy = POI["carro"][0] * PW, POI["carro"][1] * PH; bw, bh = 0.40 * PW, 0.22 * PH
            box = tuple(int(v) for v in (cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2))
            reg = im.crop(box)
            env = math.sin(math.pi * ramp(t, 1.2, 4.0)) ** 0.4
            dx = int(7 * env * math.sin(2 * math.pi * 6.5 * t)); dy = int(4 * env * math.sin(2 * math.pi * 4.7 * t + 1))
            im.paste(reg, (box[0] + dx, box[1] + dy))
        return im
    if nome == "cozinha":
        im = BASE["cozinha"].copy().convert("RGBA"); d = ImageDraw.Draw(im)
        sx, sy = POI["prateleira"][0] * PW, POI["prateleira"][1] * PH
        for i, (t0, off, vx) in enumerate([(2.2, -70, -380), (3.3, 0, 300), (4.6, 70, -260)]):
            px, py = sx + off, sy
            if t < t0:
                x, y, ang = px, py, 0
            else:
                u = t - t0
                if u > 1.2:
                    continue
                x = px + vx * u; y = py - 220 * u + 900 * u * u; ang = 540 * u
            obj = Image.new("RGBA", (44, 52), (0, 0, 0, 0)); od = ImageDraw.Draw(obj)
            od.rounded_rectangle((4, 4, 40, 48), 8, fill=(205, 205, 200, 255), outline=(60, 60, 60, 255), width=3)
            obj = obj.rotate(ang, expand=True)
            if t >= t0:
                obj = obj.filter(ImageFilter.GaussianBlur(1.6))
            im.alpha_composite(obj, (int(x - obj.size[0] / 2), int(y - obj.size[1] / 2)))
        return im.convert("RGB")
    if nome in ("crianca", "crianca_real"):
        im = BASE["crianca"].copy()
        if nome == "crianca":
            a = ramp(t, 3.1, 3.7)
            if a > 0:
                f = figura_crianca(a, ramp(t, 4.3, 4.9), ramp(t, 6.3, 6.7))
                fx = POI["rosto"][0] * PW - f.size[0] / 2; fy = POI["rosto"][1] * PH - 55
                im = im.convert("RGBA"); im.alpha_composite(f, (int(fx), int(fy))); im = im.convert("RGB")
        return im
    raise ValueError(nome)


def glitch_windows(nome):
    return {"corredor": [(2.55, 2.75), (3.75, 3.95)], "garagem": [(0.25, 0.4)], "carro": [(1.15, 1.3)],
            "cozinha": [(2.15, 2.3), (4.55, 4.7)], "crianca": [(2.5, 2.95), (6.3, 6.45)]}.get(nome, [])


def cctv(arr, k, verde=False, glitch=False, rng=None):
    g = arr.mean(axis=2) if arr.ndim == 3 else arr
    g = (g - 128) * 0.85 + 118
    g = g * (1 + 0.035 * math.sin(k * 1.7))
    g = g + rng.normal(0, 16, g.shape)
    g[::3] *= 0.86
    if glitch:
        for _ in range(7):
            y0 = rng.integers(0, g.shape[0] - 40); hh = rng.integers(6, 40)
            g[y0:y0 + hh] = np.roll(g[y0:y0 + hh], rng.integers(-90, 90), axis=1) + rng.normal(0, 40)
    v = VIG if g.shape == VIG.shape else np.asarray(Image.fromarray((VIG * 255).astype(np.uint8)).resize(g.shape[::-1]), np.float32) / 255
    g = g * v
    g = np.clip(g, 0, 255)
    if verde:
        return np.stack([g * .38, g * 1.0, g * .45], axis=2).astype(np.uint8)
    return np.stack([g, g, g * 0.98], axis=2).astype(np.uint8)


yy, xx = np.mgrid[0:PH, 0:PW]
VIG = 1 - 0.55 * (((xx - PW / 2) / (PW / 2)) ** 2 + ((yy - PH / 2) / (PH / 2)) ** 2) ** 1.3 * 0.55
VIG = np.clip(VIG, 0.3, 1)


def view(im, z, poi):
    """zoom z centrado no poi (normalizado); devolve imagem e posição do poi na tela (canvas)."""
    if z <= 1.001:
        return im, (PX + poi[0] * PW, PY + poi[1] * PH)
    w, h = PW / z, PH / z
    cx = min(max(poi[0] * PW, w / 2), PW - w / 2); cy = min(max(poi[1] * PH, h / 2), PH - h / 2)
    box = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
    sx = PX + (poi[0] * PW - box[0]) * z; sy = PY + (poi[1] * PH - box[1]) * z
    return im.resize((PW, PH), Image.BICUBIC, box=box), (sx, sy)


def render(nome_out, frames_fn, dur):
    n = int(round(dur * FPS))
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1280x720", "-r", str(FPS),
                          "-i", "-", "-vf", "fps=30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                          f"{OUT}/{nome_out}.mp4"], stdin=subprocess.PIPE)
    info = None
    for k in range(n):
        fr, info = frames_fn(k)
        p.stdin.write(fr.tobytes())
    p.stdin.close(); p.wait()
    return info


def clip(nome_out, cena_nome, t0, dur, speed=1.0, z=(1.0, 1.0), poi=None, verde=False, seed=1, sway=False):
    rng = np.random.default_rng(seed)
    gw = glitch_windows(cena_nome)

    def fn(k):
        t = t0 + k / FPS * speed
        zz = z[0] + (z[1] - z[0]) * k / max(1, dur * FPS - 1)
        im = cena(cena_nome, t)
        if sway:
            im = im.rotate(1.2 * math.sin(k / FPS * 2.1), resample=Image.BICUBIC, expand=False)
            zz = max(zz, 1.08)
        im, pos = view(im, zz, poi or (0.5, 0.5))
        arr = np.asarray(im, dtype=np.float32)
        if cena_nome == "crianca_real":
            body = np.clip((arr - 128) * 0.9 + 110 + rng.normal(0, 7, arr.shape), 0, 255) * VIG[..., None]
            body = body.astype(np.uint8)
        else:
            body = cctv(arr, k, verde=verde, glitch=any(a <= t <= b for a, b in gw), rng=rng)
        fr = np.zeros((720, 1280, 3), np.uint8); fr[PY:PY + PH, PX:PX + PW] = body
        return fr, pos
    pos = render(nome_out, fn, dur)
    return [round(pos[0]), round(pos[1])] if pos else None


def intro(dur=6.9):
    rng = np.random.default_rng(7)
    names = ["corredor", "garagem", "carro", "cozinha"]
    smalls = [cena(n, 0).resize((PW // 2 - 4, PH // 2 - 4)) for n in names]

    def fn(k):
        fr = np.zeros((720, 1280, 3), np.uint8)
        for i, im in enumerate(smalls):
            arr = np.asarray(im, dtype=np.float32)
            g = cctv(arr, k + i * 3, glitch=(k % 30) in (i * 7, i * 7 + 1), rng=rng)
            lab = Image.fromarray(g); ImageDraw.Draw(lab).text((12, lab.size[1] - 40), f"CAM 0{i + 1}", font=FONT, fill=(240, 240, 240))
            x = PX + (i % 2) * (PW // 2) + 2; y = PY + (i // 2) * (PH // 2) + 2
            fr[y:y + lab.size[1], x:x + lab.size[0]] = np.asarray(lab)
        return fr, None
    render("intro", fn, dur)


if __name__ == "__main__":
    only = sys.argv[1:]
    C = {}
    jobs = {
        "intro": lambda: intro(),
        "c5_live": lambda: clip("c5_live", "corredor", 0, 4.5, poi=POI["porta"], seed=5),
        "c5_replay": lambda: clip("c5_replay", "corredor", 2.3, 2.5, speed=0.8, z=(1.6, 2.0), poi=POI["porta"], seed=6),
        "c4_live": lambda: clip("c4_live", "garagem", 0, 3.5, poi=POI["parede"], seed=7),
        "c4_replay": lambda: clip("c4_replay", "garagem", 0.6, 3.7, speed=0.5, z=(1.3, 1.6), poi=POI["parede"], seed=8),
        "c3_live": lambda: clip("c3_live", "carro", 0, 5.2, poi=POI["carro"], seed=9),
        "c3_replay": lambda: clip("c3_replay", "carro", 1.5, 2.9, speed=0.6, z=(1.4, 1.8), poi=POI["carro"], seed=10),
        "c2_live": lambda: clip("c2_live", "cozinha", 0, 7.0, poi=POI["prateleira"], seed=11),
        "c2_replay": lambda: clip("c2_replay", "cozinha", 2.0, 3.2, speed=0.5, z=(1.5, 1.8), poi=POI["prateleira"], seed=12),
        "c1_live": lambda: clip("c1_live", "crianca", 0, 6.9, poi=POI["rosto"], verde=True, seed=13),
        "c1_real": lambda: clip("c1_real", "crianca_real", 0, 5.1, poi=(0.4, 0.5), seed=14, sway=True),
        "c1_replay": lambda: clip("c1_replay", "crianca", 6.0, 3.1, speed=0.5, z=(1.6, 2.1), poi=POI["rosto"], verde=True, seed=15),
    }
    try:
        C = json.load(open(f"{OUT}/coords.json"))
    except Exception:
        C = {}
    C["poi_canvas"] = {k: [round(PX + v[0] * PW), round(PY + v[1] * PH)] for k, v in POI.items()}
    for k, f in jobs.items():
        if only and k not in only:
            continue
        r = f()
        if r:
            C[k] = r
        print(k, r, flush=True)
    json.dump(C, open(f"{OUT}/coords.json", "w"), indent=1)
