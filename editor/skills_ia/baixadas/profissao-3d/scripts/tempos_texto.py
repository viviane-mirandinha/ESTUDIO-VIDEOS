r"""tempos_texto.py - MODO SEM FALA (ref so com musica + texto): cria palavras.json com tempos por LINHA, sem voz.
Uso: python -I -X utf8 tempos_texto.py PROJETO
Cada linha do roteiro.txt vira um "cartao" de texto. Duracao = leitura (0,7 s + 0,05 s/caractere, entre 1,6 e 2,8 s);
linha 0 (gancho) minimo 2,8 s; ultima linha (CTA) 4,0 s. projeto.json "duracoes": {"L": seg} sobrescreve.
As ancoras "L:k" continuam funcionando (palavras espalhadas igualmente dentro do cartao).
"""
import json, os, sys
W = sys.argv[1]
lines = [l.strip() for l in open(os.path.join(W, "roteiro.txt"), encoding="utf8") if l.strip() and not l.startswith("#")]
cfg = json.load(open(os.path.join(W, "projeto.json"), encoding="utf8")) if os.path.exists(os.path.join(W, "projeto.json")) else {}
fix = {int(k): v for k, v in cfg.get("duracoes", {}).items()}
t = 0.0; words = []
for L, l in enumerate(lines):
    d = min(2.8, max(1.6, 0.7 + 0.05 * len(l)))
    if L == 0: d = max(d, 2.8)
    if L == len(lines) - 1: d = 4.0
    d = fix.get(L, d); ws = l.split()
    for k, w in enumerate(ws):
        s = t + d * k / len(ws); words.append({"w": w, "line": L, "s": round(s, 3), "e": round(t + d * (k + 1) / len(ws), 3)})
    t += d
json.dump({"dur": round(t, 3), "words": words, "modo": "texto"}, open(os.path.join(W, "palavras.json"), "w", encoding="utf8"), ensure_ascii=False, indent=0)
print("linhas", len(lines), "dur", round(t, 2))
