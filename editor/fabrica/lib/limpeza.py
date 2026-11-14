# limpeza.py — "takes limpos" (escrito do zero pro Estúdio de Vídeos).
# Antes de usar um clipe de banco, olha 3 quadros e descarta se tiver:
#   • rosto grande (entrevista / pessoa falando pra câmera)  → detector de rosto local (modelo SCRFD, se o PC tiver)
#   • legenda queimada (texto centralizado embaixo, mudando)  → leitor de texto local (rapidocr, opcional)
#   • logo / marca d'água com texto no canto (fixo)           → mesmo leitor
# Tudo local, sem internet e sem token. Se faltar o modelo de rosto ou o leitor, só pula aquela checagem (nunca trava o vídeo).
import subprocess
from pathlib import Path

NOWIN = getattr(subprocess, "CREATE_NO_WINDOW", 0)
MOTIVOS = {"rosto": "pessoa falando (rosto grande)", "legenda": "legenda gravada no vídeo", "logo": "logo ou marca d'água"}
_FACE = None
# Detector de rosto: modelo SCRFD (det_10g.onnx) que já vem com o insightface/ComfyUI em muitos PCs. Sem ele, pula a checagem de rosto.
MODELOS_ROSTO = [Path.home() / ".insightface" / "models" / "buffalo_l" / "det_10g.onnx",
                 Path(__file__).resolve().parent.parent.parent / "modelos" / "det_10g.onnx"]


def _face():
    global _FACE
    if _FACE is None:
        import onnxruntime as ort
        m = next((x for x in MODELOS_ROSTO if x.exists()), None)
        if not m:
            raise RuntimeError("sem modelo de rosto")
        so = ort.SessionOptions()
        so.intra_op_num_threads = 4
        _FACE = ort.InferenceSession(str(m), so, providers=["CPUExecutionProvider"])
    return _FACE


def _rostos(f, limiar=0.6):
    """Maior rosto do quadro, em fração da altura (0 = nenhum)."""
    import numpy as np
    from PIL import Image
    im = Image.open(f).convert("RGB")
    W, H = im.size
    r = 640 / max(W, H)
    nw, nh = int(W * r), int(H * r)
    cv = Image.new("RGB", (640, 640))
    cv.paste(im.resize((nw, nh)), (0, 0))
    x = (np.asarray(cv, dtype=np.float32) - 127.5) / 128.0
    x = x.transpose(2, 0, 1)[None]
    sess = _face()
    outs = sess.run(None, {sess.get_inputs()[0].name: x})
    maior = 0.0
    for k, st in enumerate((8, 16, 32)):
        sc, bb = outs[k].reshape(-1), outs[k + 3].reshape(-1, 4)
        ok = sc >= limiar
        if not ok.any():
            continue
        d = bb[ok] * st
        alt = (d[:, 1] + d[:, 3]) / r
        maior = max(maior, float(alt.max()) / H)
    return maior


def _quadros(video: Path, n=3):
    try:
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)],
                           capture_output=True, text=True, creationflags=NOWIN, timeout=30)
        dur = float(r.stdout.strip() or 0)
    except Exception:
        dur = 0
    out = []
    for k in range(n):
        t = max(0.1, dur * (k + 1) / (n + 1)) if dur else 0.5 * (k + 1)
        f = video.parent / f"_lmp-{video.stem}-{k}.jpg"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(video), "-frames:v", "1", "-vf", "scale=480:-2,format=yuvj420p", str(f)],
                       capture_output=True, creationflags=NOWIN)
        if f.exists():
            out.append(f)
    return out


def _tem_rosto(f):
    """Rosto grande = pessoa falando/entrevista (rosto ocupa 25%+ da altura)."""
    return _rostos(f) >= 0.25


def _textos(f):
    from . import elementos
    try:
        res, _ = elementos._ocr()(str(f), use_cls=False)
    except Exception:
        return []
    from PIL import Image
    W, H = Image.open(f).size
    out = []
    for pts, txt, sc in res or []:
        if float(sc) < 0.65 or len(txt.strip()) < 3:
            continue
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        out.append({"txt": txt.strip(), "cx": (min(xs) + max(xs)) / 2 / W, "cy": (min(ys) + max(ys)) / 2 / H, "w": (max(xs) - min(xs)) / W})
    return out


def checar(video) -> str:
    """'' = clipe limpo; senão o motivo em português (pra log e pra tela)."""
    video = Path(video)
    fs = _quadros(video)
    try:
        if not fs:
            return ""
        try:
            if sum(_tem_rosto(f) for f in fs) >= 2:
                return MOTIVOS["rosto"]
        except Exception:
            pass
        try:
            from . import elementos
            elementos._ocr()
        except Exception:
            return ""   # sem leitor de texto neste PC: fica só a checagem de rosto
        leg, cantos = 0, []
        for f in fs:
            tx = _textos(f)
            if any(t["cy"] > 0.62 and abs(t["cx"] - 0.5) < 0.2 and len(t["txt"].split()) >= 2 and t["w"] > 0.2 for t in tx):
                leg += 1
            cantos.append([t for t in tx if (t["cx"] < 0.25 or t["cx"] > 0.75) and (t["cy"] < 0.2 or t["cy"] > 0.8)])
        if leg >= 2:
            return MOTIVOS["legenda"]
        # logo: texto no mesmo canto em pelo menos 2 dos 3 quadros
        for i, a in enumerate(cantos):
            for t in a:
                if sum(1 for b in cantos[i + 1:] if any(abs(o["cx"] - t["cx"]) < 0.08 and abs(o["cy"] - t["cy"]) < 0.06 for o in b)) >= 1:
                    return MOTIVOS["logo"]
        return ""
    finally:
        for f in fs:
            f.unlink(missing_ok=True)
