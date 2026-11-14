r"""voz.py - narracao Kokoro (pm_alex, speed 1.25, +1.5 semitom) linha por linha, cortada em silencio real.
Uso (python com kokoro-onnx; ver SKILL.md):
  PYTHON_DO_KOKORO -X utf8 pipeline\voz.py ROTEIRO.txt PASTA [--virada N] [--voz pm_alex] [--speed 1.25] [--pitch 1.5]
ROTEIRO.txt: ou o formato com bloco "NARRAÇÃO (pronta pro TTS) ================" ... "Palavras:",
             ou um .txt simples com 1 fala por linha.
--virada N : indice (0-based) da linha ANTES da qual entra a pausa maior (0,30 s) - a virada / "música corta".
Saida: PASTA\linhas.txt, PASTA\linhas_t.json (inicio de cada linha), PASTA\audio\voz_raw.wav, PASTA\audio\voz.wav (48 kHz mono)
"""
import argparse, json, os, subprocess, sys
import numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import falar

p = argparse.ArgumentParser()
p.add_argument("roteiro"); p.add_argument("pasta")
p.add_argument("--virada", type=int, default=-1)
p.add_argument("--voz", default="pm_alex"); p.add_argument("--speed", type=float, default=1.25)
p.add_argument("--pitch", type=float, default=1.5)
a = p.parse_args()

W = a.pasta; os.makedirs(os.path.join(W, "audio"), exist_ok=True)
txt = open(a.roteiro, encoding="utf8").read()
MARK = "NARRAÇÃO (pronta pro TTS) ================"
blk = txt.split(MARK)[1].split("Palavras:")[0].split("================")[0] if MARK in txt else txt
lines = [l.strip() for l in blk.splitlines() if l.strip()]
open(os.path.join(W, "linhas.txt"), "w", encoding="utf8").write("\n".join(lines))

# pausas entre falas: 0,08-0,18 s (padrao do video aprovado); 0,30 s antes da virada
base = [0.10, 0.12, 0.10, 0.14, 0.12, 0.08, 0.10, 0.12, 0.10, 0.12, 0.14, 0.10, 0.12, 0.12, 0.16, 0.10, 0.12, 0.14, 0.18]
gaps = [base[i % len(base)] for i in range(len(lines) - 1)]
if 0 < a.virada < len(lines): gaps[a.virada - 1] = 0.30

k = falar.kokoro()
out = []; starts = []; sr = 24000
thr = 10 ** (-44 / 20)
for i, l in enumerate(lines):
    s, sr = k.create(l, voice=a.voz, speed=a.speed, lang="pt-br")
    s = np.asarray(s, dtype=np.float32)
    idx = np.where(np.abs(s) > thr)[0]
    b0 = max(0, idx[0] - int(0.035 * sr)); b1 = min(len(s), idx[-1] + int(0.035 * sr))
    starts.append(sum(len(o) for o in out) / sr); out.append(s[b0:b1])
    if i < len(gaps): out.append(np.zeros(int(gaps[i] * sr), np.float32))
    print(i, round((b1 - b0) / sr, 2), l)
y = np.concatenate(out)
raw = os.path.join(W, "audio", "voz_raw.wav"); sf.write(raw, y, sr)
f = 2 ** (a.pitch / 12)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af",
                f"asetrate={sr}*{f:.5f},aresample=48000,atempo={1/f:.5f}", "-ar", "48000", "-ac", "1",
                os.path.join(W, "audio", "voz.wav")], check=True)
json.dump(starts, open(os.path.join(W, "linhas_t.json"), "w"))
print("linhas", len(lines), "dur", round(len(y) / sr, 2))
