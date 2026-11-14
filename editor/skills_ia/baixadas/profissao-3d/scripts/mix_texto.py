r"""mix_texto.py - MODO SEM FALA: musica (protagonista) + SFX chaveados por ancora -> audio\mix.wav (-14 LUFS).
Uso: python -I -X utf8 mix_texto.py PROJETO
dados.json: "musica", "musica_ss" (inicio em s), "sfx": [["categoria/nome", "L:k", deslocamento_s, pico_dBFS], ...]
Musica com RMS -20 dBFS (abaixa 4 dB em volta de cada SFX forte), fade in 0,3 s / fade out 1,5 s.
"""
import json, os, re, subprocess, sys
import numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import anc
W = sys.argv[1]; SR = 48000
words, END, T, cfg = anc.carregar(W)
D = json.load(open(os.path.join(W, "dados.json"), encoding="utf8"))
KIT = r"kits\FERRAMENTAS\sfx-kit\sounds"
N = int(END * SR)
def load(p, ss=0, dur=None):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(ss), "-i", p] + (["-t", str(dur)] if dur else []) + ["-ac", "1", "-ar", str(SR), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).copy()
def db(x): return 10 ** (x / 20)
m = load(D["musica"], D.get("musica_ss", 0), END + 1)[:N]; m = np.pad(m, (0, max(0, N - len(m))))
m = m * db(-20) / (np.sqrt(np.mean(m ** 2)) + 1e-9)
duck = np.ones(N, np.float32); sfx = np.zeros(N, np.float32)
for nome, an, off, pk in D.get("sfx", []):
    x = load(os.path.join(KIT, *nome.split("/")) + ".wav"); x = x * db(pk) / (np.abs(x).max() + 1e-9)
    i = int(max(0, T(an) + off) * SR); n = min(len(x), N - i)
    if n <= 0: continue
    sfx[i:i + n] += x[:n]
    if pk > -12: duck[max(0, i - SR // 20):i + min(n, SR)] = db(-4)
k = int(0.15 * SR); duck = np.convolve(duck, np.ones(k) / k, "same").astype(np.float32)
fd = np.ones(N, np.float32); fi = int(0.3 * SR); fo = int(1.5 * SR); fd[:fi] = np.linspace(0, 1, fi); fd[-fo:] = np.linspace(1, 0, fo)
out = m * duck * fd + sfx
raw = os.path.join(W, "audio", "_mix_pre.wav"); os.makedirs(os.path.dirname(raw), exist_ok=True); sf.write(raw, out, SR)
r = subprocess.run(["ffmpeg", "-hide_banner", "-i", raw, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1]); out *= db(-14 - I)
out = (0.93 * np.tanh(out / 0.93)).astype(np.float32)
sf.write(os.path.join(W, "audio", "mix.wav"), out, SR); os.remove(raw)
print("mix OK", round(END, 2), "s | LUFS pre", round(I, 1), "| sfx", len(D.get("sfx", [])))
