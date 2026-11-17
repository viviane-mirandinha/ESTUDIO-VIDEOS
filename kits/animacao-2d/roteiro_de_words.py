# roteiro_de_words.py — transforma words.json (whisper: [{"w","s","e"}]) em frases com tempo (zero token).
# Uso: python kits/animacao-2d/roteiro_de_words.py <pasta>   → grava <pasta>/frases.json e <pasta>/roteiro.txt
# frases.json: [{"n":1,"s":0.0,"e":3.2,"texto":"..."}]   (frase = termina em . ? ! … ; pausa longa também separa)
import json, sys, pathlib, re
pasta = pathlib.Path(sys.argv[1]); W = json.loads((pasta / "words.json").read_text(encoding="utf-8"))
frases, atual = [], []
def fecha():
    global atual
    if atual:
        frases.append({"n": len(frases) + 1, "s": round(atual[0]["s"], 2), "e": round(atual[-1]["e"], 2), "texto": " ".join(x["w"].strip() for x in atual).strip()}); atual = []
for i, w in enumerate(W):
    atual.append(w); t = w["w"].strip()
    pausa = (W[i + 1]["s"] - w["e"]) if i + 1 < len(W) else 9
    if re.search(r"[.!?…]$", t) or pausa > 1.4: fecha()
fecha()
(pasta / "frases.json").write_text(json.dumps(frases, ensure_ascii=False, indent=1), encoding="utf-8")
def mmss(x): return f"{int(x//60):02d}:{x%60:04.1f}"
(pasta / "roteiro.txt").write_text("\n".join(f"[{mmss(f['s'])}–{mmss(f['e'])}] {f['texto']}" for f in frases), encoding="utf-8")
n = sum(len(f['texto'].split()) for f in frases)
print(f"{len(frases)} frases, {n} palavras, {W[-1]['e']/60:.1f} min")
