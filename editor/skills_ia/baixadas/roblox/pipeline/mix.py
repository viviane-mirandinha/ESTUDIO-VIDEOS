r"""mix.py - mixagem no padrao do autor (@finnardley) aprovada no video ESTATUA.
Voz pico -15 dB | musica -27 dB RMS (corta 1-2 s antes do som-chave e some na virada final) |
SFX 1 por evento, aparado no ataque: whoosh -21..-25, impacto -19, pop -17 + sparkle -24, gasp -22, som-chave -16, sting -17 |
master -14 LUFS + soft clip tanh 0.89.
Uso:  python -X utf8 pipeline\mix.py PASTA
Precisa: PASTA\palavras.json, PASTA\audio\voz.wav, PASTA\sfx.json  (modelo: exemplo_estatua\sfx.json)
sfx.json:
{
  "musica": "musica.mp3",  "musica_ss": 8.0,
  "corte_musica": [108, 115],     # indices de palavra: musica some ~0,12 s antes da 1a e volta na 2a (som-chave entra no meio)
  "fade_final": 140,               # indice da palavra onde a musica some de vez (virada final)
  "eventos": [ ["whooshes/whoosh-fast-soft", 0, -0.05, -23], ... ]   # [categoria/nome do SFX Kit, indice_palavra, deslocamento_s, pico_dB]
}
SFX: pipeline\sfx\<categoria>\<nome>.wav (SFX Kit, CC0)  (NAO tem som de pedra: usar impacts/impact-light-hard + pops)
Musica: qualquer mp3 SEM DIREITOS (ex.: Biblioteca de Audio do YouTube). "musica": "" = sem musica. Caminho relativo = relativo a PASTA.
Saida: PASTA\audio\mix.wav (duracao = config.json "end" ou fim da voz + 1.45 s, igual ao roblox_lib)
"""
import json, math, os, re, subprocess, sys
import numpy as np, soundfile as sf

W = sys.argv[1]
K = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sfx")
cfg = json.load(open(os.path.join(W, "sfx.json"), encoding="utf8"))
words = json.load(open(os.path.join(W, "palavras.json"), encoding="utf8"))
SR = 48000
def fim_video():
    c = os.path.join(W, "config.json")
    if os.path.exists(c) and "end" in json.load(open(c, encoding="utf8")): return float(json.load(open(c, encoding="utf8"))["end"])
    return math.ceil((sf.info(os.path.join(W, "audio", "voz.wav")).duration + 1.45) * 2) / 2
END = fim_video(); N = int(END * SR)
def T(i): return words[i]["s"]
def load(p, ss=0, dur=None):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(ss), "-i", p]
    if dur: cmd += ["-t", str(dur)]
    cmd += ["-ac", "1", "-ar", str(SR), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).copy()
def db(x): return 10 ** (x / 20)
def peak_to(x, d): p = np.abs(x).max(); return x * (db(d) / p if p > 0 else 1)
def rms_to(x, d): r = np.sqrt(np.mean(x ** 2)); return x * (db(d) / r)
def trim_hit(x, thr=0.1):
    i = np.argmax(np.abs(x) > thr * np.abs(x).max()); return x[max(0, i - int(0.005 * SR)):]

out = np.zeros(N, np.float32)
voice = peak_to(load(os.path.join(W, "audio", "voz.wav")), -15)
out[:min(N, len(voice))] += voice[:N]

for nome, wi, off, d in cfg["eventos"]:
    p = nome if os.path.isabs(nome) else os.path.join(K, *nome.split("/")) + ".wav"
    x = peak_to(trim_hit(load(p)), d)
    i = int(max(0, T(wi) + off) * SR); n = min(len(x), N - i)
    if n > 0: out[i:i + n] += x[:n]

mus = cfg.get("musica") or ""
if mus and not os.path.isabs(mus): mus = os.path.join(W, mus)
if mus and os.path.exists(mus):
    m = load(mus, cfg.get("musica_ss", 0), END + 1)[:N]
    m = np.pad(m, (0, max(0, N - len(m))))
    m = rms_to(m, cfg.get("musica_db", -27))
else:
    print("aviso: sem musica (campo musica vazio no sfx.json ou arquivo nao existe)")
    m = np.zeros(N, np.float32)
g = np.ones(N, np.float32); tt = np.arange(N) / SR
def ramp(a, b, v0, v1):
    i0, i1 = int(a * SR), int(b * SR); g[i0:i1] = np.linspace(v0, v1, i1 - i0)
if cfg.get("corte_musica"):
    a_, b_ = cfg["corte_musica"]; c0 = T(a_) - 0.12; c1 = T(b_) - 0.05
    g[(tt >= c0) & (tt < c1)] = 0; ramp(c0 - 0.15, c0, 1, 0); ramp(c1, c1 + 0.08, 0, 1)
if cfg.get("fade_final") is not None:
    f0 = T(cfg["fade_final"]) - 0.25
    ramp(f0, f0 + 0.25, 1, 0); g[tt >= f0 + 0.25] = 0
out += m * g

raw = os.path.join(W, "audio", "mix_pre.wav"); sf.write(raw, out, SR)
r = subprocess.run(["ffmpeg", "-hide_banner", "-i", raw, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1])
out *= db(-14 - I)
out = (0.89 * np.tanh(out / 0.89)).astype(np.float32)
sf.write(os.path.join(W, "audio", "mix.wav"), out, SR)
print("END", END, "LUFS pre", round(I, 1), "pico", round(20 * np.log10(np.abs(out).max()), 1))
