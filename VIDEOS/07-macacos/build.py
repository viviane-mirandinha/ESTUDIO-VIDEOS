# Gera hf/index.html a partir de index.src.html + words.json (âncoras de fala -> cenas)
import json, unicodedata, re, difflib, pathlib
D = pathlib.Path(__file__).parent
DUR = 60.88
def n(s): return re.sub(r'[^a-z ]', '', unicodedata.normalize('NFD', s.lower()).encode('ascii','ignore').decode())
W = [dict(x, n=n(x['w'])) for x in json.load(open(D/'words.json', encoding='utf-8'))]
ANC = [('s1','e se um macaco'),('s2','sem voce fazer'),('s3','conheca o macaco'),('s4','bento chega na'),
 ('s5','quem entrar no'),('s6','mas tem um'),('s7','para ganhar cada'),('s8','so que nao existe'),
 ('s9','nao ha produto'),('s10','o dinheiro dos'),('s11','quem esta no topo'),('s12','quem esta na base'),
 ('s13','e a piramide precisa'),('s14','so que a floresta'),('s15','quando os novos'),('s16','e a maioria'),
 ('s17','fique atento'),('s18','promessas de ganho'),('s19','e ganhar mais'),('s20','no brasil'),('s21','inscrevase e')]
starts, i = {}, 0
for sid, a in ANC:
    k = len(a.split()); best = (0, None)
    for j in range(i, len(W)-k+1):
        r = difflib.SequenceMatcher(None, ' '.join(w['n'] for w in W[j:j+k]), a).ratio()
        if r > best[0]: best = (r, j)
        if r > 0.92: break
    j = best[1]; starts[sid] = 0 if sid == 's1' else round(max(0, W[j]['s'] - 0.08), 2); i = j + 1
    print(sid, round(best[0], 2), starts[sid], ' '.join(w['w'] for w in W[j:j+k]))
ids = [s for s, _ in ANC]
T = {s: [starts[s], round((starts[ids[k+1]] if k+1 < len(ids) else DUR) - starts[s], 2)] for k, s in enumerate(ids)}
html = (D/'index.src.html').read_text(encoding='utf-8').replace('__TIMES__', json.dumps(T)).replace('__DUR__', str(DUR))
(D/'hf/index.html').write_text(html, encoding='utf-8')
json.dump(T, open(D/'times.json','w'))
