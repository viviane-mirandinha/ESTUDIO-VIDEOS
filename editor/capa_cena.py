# capa_cena.py — acha NO VÍDEO o quadro que mostra o que a pessoa pediu (ex.: "a cama", "a casa vista de frente").
# Tudo local: ffmpeg tira os quadros e um modelo de VISÃO do Ollama (qwen2.5vl, gemma3, llava, moondream…) avalia cada um.
# 1) O pedido é separado em ASSUNTO (traduzido p/ inglês pela IA de texto) e ÂNGULO (reconhecido por regras: de cima, de frente…).
# 2) ~16 quadros espalhados pelo vídeo → a IA de visão dá nota ao assunto e ao foco, descreve o ângulo (comparado ao pedido) e diz se há legenda.
# 3) Mais quadros em volta dos 3 melhores momentos.  4) Os 3 finalistas são reavaliados em resolução maior; o melhor vence.
# Legenda por cima só desempata (o pedido manda). Sem modelo de visão ou nada parecido com o pedido → None + aviso (capa automática).
import base64
import json
import re
import subprocess
import urllib.request
from pathlib import Path

PREFERIDOS = ("qwen2.5vl", "qwen3-vl", "gemma3", "minicpm-v", "llava", "llama3.2-vision", "moondream", "bakllava")
NOTA_MINIMA = 4.0   # abaixo disso (nota 0-10 ponderada) o quadro "não parece" o que foi pedido


def _ol():
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent / "fabrica"))
    from lib import ollama as OL
    return OL


def modelo_visao():
    """Primeiro modelo instalado que enxerga imagens (ENV ESTUDIO_OLLAMA_VISAO, senão o mais indicado da lista). None = nenhum."""
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


# ângulo pedido → rótulos aceitos (o modelo de visão escolhe UM rótulo ao descrever o quadro; o 1º da lista vale nota máxima)
_ANGULOS = (
    (r"de cima|por cima|do alto|de topo|aere[oa]|from above|top.?down|bird|overhead|aerial|\bcima\b", "de cima", ["top-down", "high-angle"]),
    (r"de frente|frontal|front", "de frente", ["front"]),
    (r"de lado|lateral|\bside\b", "de lado", ["side"]),
    (r"de tras|por tras|traseira|\bback\b|\brear\b", "de trás", ["back"]),
    (r"de baixo|por baixo|from below|low.?angle", "de baixo", ["low-angle"]),
    (r"de perto|close.?up|detalhe|zoom", "de perto", ["close-up"]),
    (r"por dentro|interior|\bdentro\b|inside", "por dentro", ["inside"]),
)
ROTULOS = "top-down, high-angle, front, side, back, low-angle, close-up, inside"


def _entender(pedido, modelo_texto):
    """Pedido (PT) → (assunto_en, nome_do_angulo, rotulos_aceitos). O ângulo é reconhecido por regras; o assunto é traduzido
    para inglês pela IA de texto (os modelos de visão entendem melhor), sem as palavras de ângulo. Plano B: o pedido como está."""
    import unicodedata
    norm = "".join(c for c in unicodedata.normalize("NFD", pedido.lower()) if unicodedata.category(c) != "Mn")
    angulo, aceitos, resto = "", [], pedido
    for rx, nome, rot in _ANGULOS:
        m = re.search(rx, norm)
        if m:
            angulo, aceitos = nome, rot
            resto = norm[:m.start()] + " " + norm[m.end():]
            resto = re.sub(r"\b(vist[oa]s?|visao|imagem|foto|quadro|cena|angulo|ponto de vista)\b", " ", resto)
            resto = re.sub(r"\s+", " ", resto).strip()
            resto = re.sub(r"\b(de|do|da|por|em|com|um|uma|a|o)$", "", resto).strip() or pedido
            break
    sujeito = resto
    try:
        OL = _ol()
        t = OL.gerar("Translate this Portuguese phrase into English. Reply with ONLY the English phrase, nothing else, no quotes.\n"
                     "Example: a cama do quarto -> the bed in the bedroom\n"
                     f"Phrase: {resto}", modelo_texto, temperatura=0.0, num_predict=40, timeout=300)
        t = t.strip().strip("\"'").splitlines()[0].strip().rstrip(".")
        if 2 <= len(t) <= 100:
            sujeito = t
    except Exception:
        pass
    return sujeito, angulo, aceitos


def _quadro_bytes(video, t, largura=448):
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{max(t, 0):.2f}", "-i", str(video), "-frames:v", "1",
                        "-vf", f"scale={largura}:-2", "-q:v", "3", "-f", "image2pipe", "-vcodec", "mjpeg", "-"],
                       capture_output=True, timeout=90)
    return r.stdout if len(r.stdout) > 1500 else None


def _nitidez(jpg):
    """Quadro nítido (não borrado/em transição): variância do laplaciano numa miniatura, 0..1."""
    try:
        import io

        import numpy as np
        from PIL import Image
        a = np.asarray(Image.open(io.BytesIO(jpg)).convert("L").resize((224, 224)), dtype="float32")
        lap = a[1:-1, 1:-1] * 4 - a[:-2, 1:-1] - a[2:, 1:-1] - a[1:-1, :-2] - a[1:-1, 2:]
        return float(min(1.0, lap.var() / 400.0))
    except Exception:
        return 0.5


def _num(v, padrao=0.0):
    try:
        return max(0.0, min(10.0, float(v)))
    except Exception:
        return padrao


def _avaliar_ia(jpg, sujeito, aceitos, modelo):
    """(assunto, angulo, foco, tem_legenda). O modelo dá notas 0-10 de assunto e foco e DESCREVE o ângulo com um rótulo fixo;
    a nota de ângulo = 10 se bate com o pedido (8 se é o 2º rótulo aceito), 1,5 se não bate (10 se nenhum ângulo foi pedido)."""
    OL = _ol()
    prompt = (f'Target to find in this image: "{sujeito}".\n'
              "Look carefully at the image and reply ONLY with JSON:\n"
              '{"subject": number 0-10, how clearly the target is visible (0 = not there at all, 10 = unmistakable), '
              '"viewpoint": the camera viewpoint, exactly ONE of: ' + ROTULOS + " "
              "(top-down = looking straight down like a map; high-angle = looking down from above at an angle; front/side/back = of the target itself; "
              "low-angle = looking up; close-up = very near; inside = interior view), "
              '"focus": number 0-10, how much the target is the main thing in the picture (0 = tiny or hidden, 10 = it fills the frame), '
              '"caption": true if large subtitle/caption text is written over the picture, else false}')
    body = {"model": modelo, "prompt": prompt, "images": [base64.b64encode(jpg).decode()], "stream": False, "format": "json",
            "options": {"temperature": 0, "num_predict": 90, "num_ctx": 4096}, "keep_alive": OL.KEEP}
    req = urllib.request.Request(OL.base() + "/api/generate", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=900) as r:
        txt = json.load(r).get("response", "")
    d = OL._json_seguro(txt)
    cap = d.get("caption")
    cap = cap if isinstance(cap, bool) else str(cap).strip().lower() in ("true", "yes", "1")
    vp = str(d.get("viewpoint") or "").strip().lower()
    ang = 10.0 if not aceitos else (10.0 if vp == aceitos[0] else 8.0 if vp in aceitos else 1.5)
    return _num(d.get("subject")), ang, _num(d.get("focus")), cap


def _pontos(s, a, f, cap, nit, tem_angulo):
    """Nota 0-10 do pedido (base) e nota final (base + bônus pequenos que só desempatam)."""
    base = (0.45 * s + 0.30 * a + 0.25 * f) if tem_angulo else (0.65 * s + 0.35 * f)
    return base, base + (0.0 if cap else 1.0) + 0.3 * nit   # sem legenda por cima ganha até 1 ponto: desempata quadros que já batem com o pedido


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
                      "Para procurar cenas, rode no terminal:  ollama pull qwen2.5vl:7b  e crie a capa de novo.")
    prog(20, f"Entendendo o pedido “{pedido[:40]}”…")
    sujeito, angulo, aceitos = _entender(pedido, modelo_texto)
    entendi = f"Entendi: «{sujeito}»" + (f", visto «{angulo}»" if angulo else " (sem ângulo específico)")

    notas = {}   # segundo → dict(base, final, jpg, grosso)

    def avaliar(t, largura=448):
        t = round(min(max(t, 0.3), duracao - 0.3), 1)
        if t in notas:
            return notas[t]["final"]
        jpg = _quadro_bytes(vid, t, largura)
        if not jpg:
            return 0.0
        s, a, f, cap = _avaliar_ia(jpg, sujeito, aceitos, modelo)
        base, fin = _pontos(s, a, f, cap, _nitidez(jpg), bool(angulo))
        notas[t] = {"base": base, "final": fin, "cap": cap}
        return fin

    try:
        grosso = [duracao * (0.03 + 0.94 * i / (n_grosso - 1)) for i in range(n_grosso)]
        for i, t in enumerate(grosso):
            prog(25 + int(25 * i / n_grosso), f"Olhando o vídeo atrás de “{pedido[:40]}” ({i + 1}/{n_grosso})…")
            avaliar(t)
        topo = []
        for t, v in sorted(notas.items(), key=lambda kv: -kv[1]["final"]):   # 3 melhores momentos, separados entre si
            if all(abs(t - u) > duracao / n_grosso * 1.5 for u in topo):
                topo.append(t)
            if len(topo) == 3:
                break
        passo = max(0.5, duracao / n_grosso / 4)
        extras = [t + k * passo for t in topo for k in (-3, -2, -1, 1, 2, 3)]
        for i, t in enumerate(extras):
            prog(50 + int(20 * i / max(1, len(extras))), f"Refinando o melhor ponto ({i + 1}/{len(extras)})…")
            avaliar(t)
        # finalistas: os 3 melhores quadros de todos, reavaliados em resolução maior (média das duas olhadas = menos erro)
        final = sorted(notas.items(), key=lambda kv: -kv[1]["final"])[:3]
        for i, (t, v) in enumerate(final):
            prog(72 + i * 2, f"Conferindo os finalistas ({i + 1}/{len(final)})…")
            jpg = _quadro_bytes(vid, t, 896)
            if jpg:
                s, a, f, cap = _avaliar_ia(jpg, sujeito, aceitos, modelo)
                base, fin = _pontos(s, a, f, cap, _nitidez(jpg), bool(angulo))
                v["base"], v["final"], v["cap"] = (v["base"] + base) / 2, (v["final"] + fin) / 2, cap
        vencedor = max((kv for kv in final), key=lambda kv: kv[1]["final"])
    except Exception as e:
        return None, f"A IA de visão falhou ({type(e).__name__}); usei o modo automático."
    t, v = vencedor
    if v["base"] < NOTA_MINIMA:
        return None, f"{entendi}. Não encontrei no vídeo nada parecido (melhor nota {v['base']:.1f}/10); usei o modo automático."
    out = pasta / "_capa_cena.jpg"   # em qualidade total (o de 448/896 px era só para a IA)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(vid), "-frames:v", "1", "-q:v", "2", str(out)],
                   capture_output=True, timeout=120)
    if not out.exists():
        return None, "Não consegui salvar o quadro escolhido."
    leg = " Atenção: este quadro tem legenda por cima (não achei um parecido sem legenda)." if v["cap"] else ""
    return out, f"{entendi}. Cena escolhida: {t:.1f}s do vídeo (nota {v['base']:.1f}/10).{leg}"
