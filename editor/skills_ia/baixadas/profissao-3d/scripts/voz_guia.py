r"""voz_guia.py - VOZ GUIA Kokoro (pm_alex adulto, speed 1.15, SEM pitch) frase por frase, cortada em silencio real.
Uso (python do Kokoro):
  kits\FERRAMENTAS\KOKORO\venv\Scripts\python.exe -X utf8 voz_guia.py PROJETO [--voz pm_alex] [--speed 1.1]
Le PROJETO\roteiro.txt (1 frase por linha; linhas vazias e '#' ignoradas).
Saida: PROJETO\audio\voz_guia.wav (48 kHz mono) - e' a voz padrao; a do Yuri entra pelo refazer.py --voz.
"""
import argparse, os, re, subprocess, sys
import numpy as np, soundfile as sf
sys.path.insert(0, r"kits\FERRAMENTAS\KOKORO")
import falar

p = argparse.ArgumentParser(); p.add_argument("projeto")
p.add_argument("--voz", default="pm_alex"); p.add_argument("--speed", type=float, default=1.15)
a = p.parse_args()
W = a.projeto; os.makedirs(os.path.join(W, "audio"), exist_ok=True)
lines = [l.strip() for l in open(os.path.join(W, "roteiro.txt"), encoding="utf8") if l.strip() and not l.startswith("#")]
k = falar.kokoro(); out = []; sr = 24000; thr = 10 ** (-44 / 20)
for i, l in enumerate(lines):
    s, sr = k.create(re.sub(r"[A-ZÁÉÍÓÚÂÊÔÃÕÇ]{4,}", lambda m_: m_.group(0).lower(), l),  # PALAVRA do CTA em caixa alta -> minuscula (senao soletra)
                      voice=a.voz, speed=a.speed, lang="pt-br")
    s = np.asarray(s, dtype=np.float32); idx = np.where(np.abs(s) > thr)[0]
    out.append(s[max(0, idx[0] - int(0.03 * sr)):idx[-1] + int(0.05 * sr)])
    # pausa: fim de frase com ponto = 0,20 s; interrogacao = 0,15 s
    out.append(np.zeros(int((0.20 if l.endswith(".") else 0.15) * sr), np.float32))
y = np.concatenate([np.zeros(int(0.15 * sr), np.float32)] + out)
raw = os.path.join(W, "audio", "_voz_raw.wav"); sf.write(raw, y, sr)
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", raw, "-ar", "48000", "-ac", "1", os.path.join(W, "audio", "voz_guia.wav")], check=True)
os.remove(raw); print("frases", len(lines), "dur", round(len(y) / sr, 2))
