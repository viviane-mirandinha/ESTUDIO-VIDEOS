"""Alinha o TEXTO EXATO do roteiro com os tempos do whisper (words.json) e dá at("palavra", n)."""
import json, re, unicodedata, difflib, glob, os

def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", s)

def alinhar(texto, words):
    toks = texto.split()
    A = [norm(t) for t in toks]; B = [norm(w["w"]) for w in words]
    sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
    out = [None] * len(toks)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1): out[i1 + k] = (words[j1 + k]["s"], words[j1 + k]["e"])
        elif tag == "replace":
            ni, nj = i2 - i1, j2 - j1
            for k in range(ni):
                js = j1 + k * nj // ni; je = max(js, j1 + (k + 1) * nj // ni - 1)
                out[i1 + k] = (words[js]["s"], words[je]["e"])
    i = 0
    while i < len(out):
        if out[i] is None:
            j = i
            while j < len(out) and out[j] is None: j += 1
            a = out[i - 1][1] if i > 0 else 0.0
            b = out[j][0] if j < len(out) else a + 0.35 * (j - i)
            st = (b - a) / (j - i)
            for k in range(i, j): out[k] = (round(a + st * (k - i), 2), round(a + st * (k - i + 1), 2))
            i = j
        else: i += 1
    return [{"w": t, "s": s, "e": e} for t, (s, e) in zip(toks, out)]

class Falas:
    def __init__(self, pasta, roteiro_glob):
        d = json.load(open(os.path.join(pasta, "words.json"), encoding="utf-8"))
        self.dur_audio = d["duration"]
        txt = open(glob.glob(roteiro_glob)[0], encoding="utf-8").read().strip()
        self.words = alinhar(txt, d["words"])
    def at(self, palavra, n=1, fim=False):
        p = palavra.split(); alvo = [norm(x) for x in p]; c = 0
        for i in range(len(self.words) - len(alvo) + 1):
            if all(norm(self.words[i + k]["w"]) == alvo[k] for k in range(len(alvo))):
                c += 1
                if c == n: return self.words[i + len(alvo) - 1]["e"] if fim else self.words[i]["s"]
        raise KeyError(f"palavra nao achada: {palavra} #{n}")
