"""ancoras "L:k" (k-esima palavra da linha L do roteiro, 0-based; k negativo conta do fim) -> tempo, igual ao prof_lib."""
import json, os
def carregar(W):
    pj = json.load(open(os.path.join(W, "palavras.json"), encoding="utf8"))
    cfg = json.load(open(os.path.join(W, "projeto.json"), encoding="utf8")) if os.path.exists(os.path.join(W, "projeto.json")) else {}
    words = pj["words"]; end = round(pj["dur"] + cfg.get("cauda", 1.2), 2)
    def idx(a):
        if isinstance(a, int): return a
        L, k = (int(x) for x in str(a).split(":")); ii = [i for i, w in enumerate(words) if w["line"] == L]
        return ii[min(k, len(ii) - 1)] if k >= 0 else ii[k]
    def T(a):
        if a == "fim": return end
        return words[idx(a)]["s"]
    return words, end, T, cfg
