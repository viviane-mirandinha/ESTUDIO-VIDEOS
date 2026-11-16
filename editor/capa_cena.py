# capa_cena.py — acha NO VÍDEO o quadro que mostra o que a pessoa pediu (ex.: "a cama", "a casa vista de frente").
# Tudo local: ffmpeg tira os quadros e um modelo de VISÃO do Ollama (qwen2.5vl, gemma3, llava, moondream…) dá nota a cada um.
# Passo 1: ~16 quadros espalhados pelo vídeo → nota 0-10. Passo 2: refaz com mais quadros em volta dos 3 melhores momentos.
# Se não houver modelo de visão instalado ou nada se parecer com o pedido, devolve None + um aviso (a capa segue no modo automático).
import base64
import json
import re
import subprocess
import urllib.request
from pathlib import Path

PREFERIDOS = ("qwen2.5vl", "qwen3-vl", "gemma3", "minicpm-v", "llava", "llama3.2-vision", "moondream", "bakllava")
NOTA_MINIMA = 4.0   # abaixo disso o quadro "não parece" o que foi pedido


def _ol():
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent / "fabrica"))
    from lib import ollama as OL
    return OL


def modelo_visao():
    """Primeiro modelo instalado que enxerga imagens (Ajustes/ENV → ESTUDIO_OLLAMA_VISAO; senão o mais indicado da lista). None = nenhum."""
    import os
    OL = _ol()
    if os.environ.get("ESTUDIO_OLLAMA_VISAO"):
        return os.environ["ESTUDIO_OLLAMA_VISAO"]
    try:
        OL.ligar()
        with urllib.request.urlopen(OL.base() + "/api/tags", timeout=8) as r:
            ms = json.load(r).get("models") or []
    except Exception:
        return None
    ve = [m["name"] for m in ms if "vision" in (m.get("capabilities") or []) or any(m["name"].startswith(p) for p in PREFERIDOS)]
    for p in PREFERIDOS:
        for n in ve:
            if n.startswith(p):
                return n
    return ve[0] if ve else None


def _em_ingles(pedido, modelo_texto):
    """Os modelos de visão pequenos entendem muito melhor em inglês: traduz o pedido numa descrição curta."""
    if not re.search(r"[À-ÿ]|\b(a|o|as|os|de|da|do|um|uma|com|vista|visto|casa|cama|ângulo|angulo)\b", pedido, re.I):
        return pedido
    try:
        OL = _ol()
        t = OL.gerar("Translate to English as a short visual description of what should be visible in a photo. "
                     "Keep camera angle words (front view, from above, close-up, side view...). Reply ONLY the translation, no quotes.\n"
                     f"Text: {pedido}", modelo_texto, temperatura=0.1, num_predict=60, timeout=300)
        t = t.strip().strip('"\'').splitlines()[0].strip()
        return t if 2 <= len(t) <= 200 else pedido
    except Exception:
        return pedido


def _quadro_bytes(video, t, largura=448):
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{max(t, 0):.2f}", "-i", str(video), "-frames:v", "1",
                        "-vf", f"scale={largura}:-2", "-q:v", "4", "-f", "image2pipe", "-vcodec", "mjpeg", "-"],
                       capture_output=True, timeout=90)
    return r.stdout if len(r.stdout) > 1500 else None


def _nitidez(jpg):
    """Quadro nítido (não borrado/em transição): variância do laplaciano numa miniatura."""
    try:
        import io

        import numpy as np
        from PIL import Image
        a = np.asarray(Image.open(io.BytesIO(jpg)).convert("L").resize((224, 224)), dtype="float32")
        lap = a[1:-1, 1:-1] * 4 - a[:-2, 1:-1] - a[2:, 1:-1] - a[1:-1, :-2] - a[1:-1, 2:]
        return float(min(1.0, lap.var() / 400.0))
    except Exception:
        return 0.5


def _nota(jpg, desc, modelo):
    """0-10: o quanto o quadro mostra o que foi pedido (o modelo responde só um número)."""
    OL = _ol()
    prompt = (f'Target: "{desc}"\nHow well does this image show the target (including the camera angle, if one is mentioned)? '
              "Rate from 0 (not visible at all) to 10 (clearly and prominently shown). Answer with ONLY the number.")
    body = {"model": modelo, "prompt": prompt, "images": [base64.b64encode(jpg).decode()], "stream": False,
            "options": {"temperature": 0, "num_predict": 6, "num_ctx": 4096}, "keep_alive": OL.KEEP}
    req = urllib.request.Request(OL.base() + "/api/generate", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=900) as r:
        txt = json.load(r).get("response", "")
    m = re.search(r"\d+(?:[.,]\d+)?", txt)
    return min(10.0, float(m.group(0).replace(",", "."))) if m else 0.0


def achar(pasta, duracao, pedido, modelo_texto, prog=None, n_grosso=16):
    """Retorna (caminho_do_quadro_em_alta, aviso). caminho None = não achou (aviso explica)."""
    prog = prog or (lambda p, m: None)
    pasta = Path(pasta)
    vid = next((pasta / x for x in ("final.mp4", "leve.mp4") if (pasta / x).exists()), None)
    duracao = float(duracao or 0)
    if not vid:
        return None, "Não achei o vídeo pronto para procurar a cena."
    if duracao < 3:
        try:
            duracao = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(vid)],
                                           capture_output=True, text=True, timeout=30).stdout.strip())
        except Exception:
            return None, "Não consegui medir a duração do vídeo."
    modelo = modelo_visao()
    if not modelo:
        return None, ("Nenhum modelo de visão do Ollama está instalado, então usei o modo automático. "
                      "Para procurar cenas, rode no terminal:  ollama pull qwen2.5vl:3b  (uns 3 GB) e crie a capa de novo.")
    prog(20, f"Traduzindo o pedido para a IA de visão ({modelo})…")
    desc = _em_ingles(pedido, modelo_texto)

    notas = {}   # segundo → (nota final, nota do modelo, jpg)

    def avaliar(t):
        t = round(min(max(t, 0.3), duracao - 0.3), 1)
        if t in notas:
            return notas[t][0]
        jpg = _quadro_bytes(vid, t)
        if not jpg:
            return 0.0
        n = _nota(jpg, desc, modelo)
        notas[t] = (n + 0.8 * _nitidez(jpg), n, jpg)   # a nitidez só desempata (não deixa quadro borrado vencer)
        return notas[t][0]

    try:
        grosso = [duracao * (0.03 + 0.94 * i / (n_grosso - 1)) for i in range(n_grosso)]
        for i, t in enumerate(grosso):
            prog(25 + int(25 * i / n_grosso), f"Olhando o vídeo atrás de “{pedido[:40]}” ({i + 1}/{n_grosso})…")
            avaliar(t)
        topo = []
        for t, v in sorted(notas.items(), key=lambda kv: -kv[1][0]):   # 3 melhores momentos, separados entre si
            if all(abs(t - u) > duracao / n_grosso * 1.5 for u in topo):
                topo.append(t)
            if len(topo) == 3:
                break
        passo = max(0.5, duracao / n_grosso / 4)
        extras = [t + k * passo for t in topo for k in (-3, -2, -1, 1, 2, 3)]
        for i, t in enumerate(extras):
            prog(50 + int(22 * i / max(1, len(extras))), f"Refinando o melhor ponto ({i + 1}/{len(extras)})…")
            avaliar(t)
    except Exception as e:
        return None, f"A IA de visão falhou ({type(e).__name__}); usei o modo automático."
    if not notas:
        return None, "Não consegui tirar quadros do vídeo."
    t, (_, bruta, _) = max(notas.items(), key=lambda kv: kv[1][0])
    if bruta < NOTA_MINIMA:
        return None, f"Não encontrei no vídeo nada parecido com “{pedido}” (melhor nota {bruta:.0f}/10); usei o modo automático."
    out = pasta / "_capa_cena.jpg"   # em qualidade total (o de 448 px era só para a IA)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(vid), "-frames:v", "1", "-q:v", "2", str(out)],
                   capture_output=True, timeout=120)
    if not out.exists():
        return None, "Não consegui salvar o quadro escolhido."
    return out, f"Cena escolhida: {t:.1f}s do vídeo (nota {bruta:.0f}/10)."
