r"""alinhar.py - tempo de cada PALAVRA do roteiro na voz (guia Kokoro OU gravada pelo Yuri).
faster-whisper large-v3, CPU int8, word_timestamps=True; audio passado como numpy (caminho de arquivo quebra com PyAV aqui; cuda sem cublas).
Casa as palavras do Whisper com as do roteiro (difflib) -> o texto da legenda e' SEMPRE o do roteiro, o tempo e' o da voz.
Uso:  python -X utf8 alinhar.py PROJETO VOZ.wav
Saida: PROJETO\palavras.json [{"w","line","s","e"}]  -> cortes, etiquetas, legenda e SFX sao chaveados por palavra (ancora), nunca por segundo.
"""
import json, os, re, subprocess, sys, difflib, unicodedata
import numpy as np

W, VOZ = sys.argv[1], sys.argv[2]
lines = [l.strip() for l in open(os.path.join(W, "roteiro.txt"), encoding="utf8") if l.strip() and not l.startswith("#")]
def norm(w): return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFD", w.lower()).encode("ascii", "ignore").decode())
words = [{"w": w, "line": li} for li, l in enumerate(lines) for w in l.split()]
aud = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", VOZ, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                                   capture_output=True, check=True).stdout, np.float32)
from faster_whisper import WhisperModel
m = WhisperModel("large-v3", device="cpu", compute_type="int8")
# SEM initial_prompt: com o roteiro como prompt o large-v3 pulou os primeiros 5 s da voz (31-10)
segs, _ = m.transcribe(aud, language="pt", word_timestamps=True, vad_filter=False)
ww = [(x.word.strip(), x.start, x.end) for s in segs for x in s.words]
# whisper junta/separa numeros e siglas: expande cada palavra dele em pedacos normalizados
a = [norm(x["w"]) for x in words]; b = [norm(x[0]) for x in ww]
for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
    if tag == "equal":
        for k in range(i2 - i1): words[i1 + k]["s"] = ww[j1 + k][1]; words[i1 + k]["e"] = ww[j1 + k][2]
    elif tag == "replace" and i2 - i1 == j2 - j1:      # ex.: "treze" x "13"
        for k in range(i2 - i1): words[i1 + k]["s"] = ww[j1 + k][1]; words[i1 + k]["e"] = ww[j1 + k][2]
    elif tag == "replace":                               # blocos de tamanhos diferentes: reparte o trecho
        t0, t1 = ww[j1][1], ww[j2 - 1][2]; n = i2 - i1
        for k in range(n): words[i1 + k]["s"] = t0 + (t1 - t0) * k / n; words[i1 + k]["e"] = t0 + (t1 - t0) * (k + 1) / n
ok = sum("s" in w for w in words)
for i, w in enumerate(words):   # interpola as que nao casaram
    if "s" not in w:
        p = max([j for j in range(i) if "s" in words[j]], default=None)
        n = next((j for j in range(i + 1, len(words)) if "s" in words[j]), None)
        ps = words[p]["s"] if p is not None else 0.1; pi = p if p is not None else -1
        ns = words[n]["s"] if n is not None else ps + 0.4 * (i - pi + 1); ni = n if n is not None else i + 1
        w["s"] = ps + (ns - ps) * (i - pi) / (ni - pi); w["e"] = w["s"] + 0.25
for i in range(1, len(words)):
    if words[i]["s"] <= words[i - 1]["s"]: words[i]["s"] = words[i - 1]["s"] + 0.05
dur = len(aud) / 16000
json.dump({"dur": dur, "words": words}, open(os.path.join(W, "palavras.json"), "w", encoding="utf8"), ensure_ascii=False, indent=0)
print("casadas", ok, "/", len(words), "| voz", round(dur, 2), "s")
