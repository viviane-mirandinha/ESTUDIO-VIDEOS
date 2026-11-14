r"""tempos.py - tempo de cada PALAVRA do roteiro (faster-whisper large-v3-turbo, CPU int8) casado com o texto via difflib.
Uso:  python -X utf8 pipeline\tempos.py PASTA
Precisa: PASTA\linhas.txt, PASTA\linhas_t.json, PASTA\audio\voz.wav (saidas do voz.py)
Saida:   PASTA\palavras.json  [{"w": palavra, "line": n, "s": inicio, "e": fim}, ...]  -> TUDO (corte, pose, rosto, puf, SFX) e chaveado pelo INDICE
Obs: GPU falta cublas -> CPU int8. Audio lido via ffmpeg->float32 (o decoder `av` quebra aqui).
"""
import json, os, re, subprocess, sys, difflib, unicodedata
import numpy as np
from faster_whisper import WhisperModel

W = sys.argv[1]
lines = open(os.path.join(W, "linhas.txt"), encoding="utf8").read().splitlines()
lt = json.load(open(os.path.join(W, "linhas_t.json")))
def norm(w): return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFD", w.lower()).encode("ascii", "ignore").decode())
words = [{"w": w, "line": li} for li, l in enumerate(lines) for w in l.split()]

aud = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(W, "audio", "voz.wav"),
                                    "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True, check=True).stdout, np.float32)
m = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8")
segs, _ = m.transcribe(aud, language="pt", word_timestamps=True, initial_prompt=" ".join(lines))
ww = [(x.word.strip(), x.start, x.end) for s in segs for x in s.words]
a = [norm(x["w"]) for x in words]; b = [norm(x[0]) for x in ww]
for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
    if tag == "equal":
        for k in range(i2 - i1):
            words[i1 + k]["s"] = ww[j1 + k][1]; words[i1 + k]["e"] = ww[j1 + k][2]
print("casadas", sum("s" in w for w in words), "/", len(words))
# inicio de cada linha e exato (voz.py sabe onde colou): 1a palavra de cada linha = inicio da linha + 35 ms
for li in range(len(lines)):
    idx = [i for i, w in enumerate(words) if w["line"] == li]
    if idx: words[idx[0]]["s"] = lt[li] + 0.035
# interpola as que o whisper nao casou
for i, w in enumerate(words):
    if "s" not in w:
        p = max(j for j in range(i) if "s" in words[j]); n = next((j for j in range(i + 1, len(words)) if "s" in words[j]), None)
        ns = words[n]["s"] if n else words[p]["s"] + 0.4
        w["s"] = words[p]["s"] + (ns - words[p]["s"]) * (i - p) / ((n or i + 1) - p)
for i in range(1, len(words)):
    if words[i]["s"] <= words[i - 1]["s"]: words[i]["s"] = words[i - 1]["s"] + 0.05
json.dump(words, open(os.path.join(W, "palavras.json"), "w", encoding="utf8"), ensure_ascii=False, indent=0)
for i, w in enumerate(words): print(i, round(w["s"], 2), w["w"], end=" | ")
print()
