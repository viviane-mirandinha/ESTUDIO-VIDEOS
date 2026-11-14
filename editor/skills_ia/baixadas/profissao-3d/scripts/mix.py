r"""mix.py - voz + musica ambiente (>=18 dB abaixo da voz, com ducking) + SFX discretos chaveados por ancora.
Uso: python -X utf8 mix.py PROJETO      (precisa audio\voz.wav, palavras.json, dados.json)
dados.json "sfx": [ ["kit:categoria/nome" | "synth:zumbido|faisca|passarinho", "L:k", deslocamento_s, pico_dB, duracao_s(synth)] ]
Saida: PROJETO\audio\mix.wav (-14 LUFS, pico < -1 dBTP aprox.)
"""
import json, os, re, subprocess, sys
import numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import anc
W = sys.argv[1]; SR = 48000
words, END, T, cfg = anc.carregar(W)
D = json.load(open(os.path.join(W, "dados.json"), encoding="utf8"))
KIT = r"kits\FERRAMENTAS\sfx-kit\sounds"
N = int(END * SR); rng = np.random.default_rng(3)
def load(p, ss=0, dur=None):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(ss), "-i", p] + (["-t", str(dur)] if dur else []) + ["-ac", "1", "-ar", str(SR), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).copy()
def db(x): return 10 ** (x / 20)
def peak_to(x, d): p = np.abs(x).max(); return x * (db(d) / p if p > 0 else 1)
def lp(x, a): # passa-baixa 1 polo
    y = np.empty_like(x); s = 0.0
    for i in range(len(x)): s += a * (x[i] - s); y[i] = s
    return y
def env(n, att=0.05, rel=0.2):
    e = np.ones(n, np.float32); a = int(att * SR); r = int(rel * SR)
    e[:a] = np.linspace(0, 1, a); e[-r:] *= np.linspace(1, 0, r); return e
def synth(kind, dur):
    n = int(max(dur, 0.2) * SR); t = np.arange(n) / SR
    if kind == "zumbido":   # 60 Hz + harmonicos + chiado fino
        x = sum(a * np.sin(2 * np.pi * f * t) for f, a in ((60, 1), (120, .6), (180, .35), (240, .2), (360, .1)))
        x = x * (0.85 + 0.15 * np.sin(2 * np.pi * 3.1 * t)) + 0.05 * rng.standard_normal(n)
        return (x * env(n, 0.25, 0.4)).astype(np.float32)
    if kind == "faisca":    # estalos curtos
        x = np.zeros(n, np.float32)
        for _ in range(int(14 * dur) + 3):
            i = rng.integers(0, max(1, n - 2400)); L = rng.integers(200, 1800)
            b = rng.standard_normal(L) * np.exp(-np.arange(L) / (L / 5)); x[i:i + L] += b * rng.uniform(0.3, 1)
        x = x - lp(x, 0.25); return x * env(n, 0.005, 0.1)
    if kind == "passarinho":
        x = np.zeros(int(0.7 * SR), np.float32)
        for k, t0 in enumerate((0.0, 0.16, 0.42)):
            L = int(0.09 * SR); tt = np.arange(L) / SR; f = 3200 + 1800 * (tt / 0.09) + 300 * np.sin(2 * np.pi * 40 * tt)
            ph = 2 * np.pi * np.cumsum(f) / SR; s = np.sin(ph) * np.sin(np.pi * tt / 0.09) ** 2
            i = int(t0 * SR); x[i:i + L] += s * (1 - 0.2 * k)
        return x
    raise SystemExit("synth desconhecido: " + kind)

voz = load(os.path.join(W, "audio", "voz.wav"))[:N]
voz = peak_to(voz, -3.0); out = np.zeros(N, np.float32); out[:len(voz)] += voz
# envelope da voz (pra ducking) e RMS da voz ativa
fr = SR // 50; e = np.sqrt(np.convolve(np.pad(voz, (0, N - len(voz))) ** 2, np.ones(fr) / fr, "same"))
ativo = e > db(-40); voz_rms = 20 * np.log10(np.sqrt(np.mean(voz[ativo[:len(voz)]] ** 2)) + 1e-9)
# musica: RMS = voz_rms - 22 dB, duck -5 dB com a voz (suavizado) -> sempre >= 18 dB abaixo
m = load(D["musica"], D.get("musica_ss", 4), END + 1)[:N]; m = np.pad(m, (0, max(0, N - len(m))))
m = m * db(voz_rms - 22) / (np.sqrt(np.mean(m ** 2)) + 1e-9)
duck = np.where(ativo, db(-5), 1.0).astype(np.float32)
k = int(0.25 * SR); duck = np.convolve(duck, np.ones(k) / k, "same")
fade = np.ones(N, np.float32); fi = int(1.0 * SR); fo = int(2.0 * SR); fade[:fi] = np.linspace(0, 1, fi); fade[-fo:] = np.linspace(1, 0, fo)
out += m * duck * fade
for nome, a, off, pk, *rest in D["sfx"]:
    if nome.startswith("synth:"): x = synth(nome[6:], rest[0] if rest else 1.0)
    else: x = load(os.path.join(KIT, *nome[4:].split("/")) + ".wav")
    x = peak_to(x, pk + (voz_rms + 20))     # pico relativo: -30 = 30 dB abaixo de uma voz a -20 RMS
    i = int(max(0, T(a) + off) * SR); n = min(len(x), N - i)
    if n > 0: out[i:i + n] += x[:n]
raw = os.path.join(W, "audio", "_mix_pre.wav"); sf.write(raw, out, SR)
r = subprocess.run(["ffmpeg", "-hide_banner", "-i", raw, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1]); out *= db(-14 - I)
out = (0.93 * np.tanh(out / 0.93)).astype(np.float32)
sf.write(os.path.join(W, "audio", "mix.wav"), out, SR); os.remove(raw)
print("mix OK", round(END, 2), "s | voz RMS", round(voz_rms, 1), "| musica", round(voz_rms - 22, 1), "(-5 no duck) | LUFS pre", round(I, 1))
