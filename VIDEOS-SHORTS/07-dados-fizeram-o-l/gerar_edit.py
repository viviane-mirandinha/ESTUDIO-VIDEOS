# Gera edit.json do short 07 (dados/ranking escuro amarelo, "fizeram o L"). TODO tempo vem de words.json (trocar voz = whisper + rodar de novo).
import json, os, re, unicodedata, difflib
D = os.path.dirname(os.path.abspath(__file__))
NAME = "07 - DADOS RANKING ESCURO - Fizeram o L e nao foram votar"
WJ = json.load(open(os.path.join(D, "words.json"), encoding="utf-8"))
W = [dict(w) for w in WJ["words"]]
DUR = round(WJ["duration"] + 0.6, 2)
ROT = open(os.path.join(D, "roteiro.txt"), encoding="utf-8").read().strip()

def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return re.sub(r"[^\w%]", "", "".join(c for c in s if unicodedata.category(c) != "Mn")).replace("_", "")

def at(palavra, oc=1, depois=0.0):
    """início da palavra (oc-ésima ocorrência após `depois`)"""
    alvo, k = norm(palavra), 0
    for w in W:
        if w["s"] < depois:
            continue
        if norm(w["w"]) == alvo or (len(alvo) > 3 and norm(w["w"]).startswith(alvo)):
            k += 1
            if k == oc:
                return w["s"]
    raise SystemExit(f"palavra não achada: {palavra} #{oc} depois de {depois}")

for w in W:  # whisper escreve "casé" -> "Cazé"
    if norm(w["w"]) == "case":
        w["w"] = re.sub(r"(?i)cas[eé]", "Cazé", w["w"])

items = []
def scene(nome, s, e, params, label):
    # sem buraco preto: 1º elemento de frase entra logo no início da cena; cena dura +0,35 s (cobre o fade-in da próxima)
    if nome == "dr_frase" and params.get("linhas"):
        params["linhas"][0]["t"] = min(params["linhas"][0]["t"], s + .05)
    if e < DUR - .01:
        e = e + .35
    items.append({"id": f"sc{len(items)}", "type": "scene", "track": "visual", "label": label, "start": round(s, 2), "dur": round(e - s, 2),
                  "props": {"scene": nome, "params": params}})

AM, VM = "#F5C518", "#ff3b3b"
F = {k: f"img/foto_{k}.jpg" for k in ("anitta", "wagner", "bruna", "caze")}
CD = {k: f"img/card_{k}.png" for k in ("anitta", "wagner", "bruna", "caze")}
RY = {"anitta": .76, "wagner": .626, "bruna": .741, "caze": .619}   # altura da linha vermelha em cada card (fração)
RX = {"anitta": .08, "wagner": .08, "bruna": .095, "caze": .047}
NOME = {"anitta": "Anitta", "wagner": "Wagner Moura", "bruna": "Bruna Marquezine", "caze": "Casimiro (Cazé)"}
SUB = "consulta · situação eleitoral"
def pessoa(k, s, e, **kw):
    p = {"titulo": NOME[k], "sub": SUB, "icone": "urna", "foto": F[k], "card": CD[k], "ry": RY[k], "rx": RX[k], "rw": .6}
    p.update(kw); scene("dr_pessoa", s, e, p, NOME[k])

# ---- cortes de cena (início de cada frase)
c = [0.0, at("Mas") - .25, at("Pensa") - .3, at("Já") - .3, at("Anitta", 2) - .3, at("Aí") - .25, at("Mas", 2) - .3,
     at("Bruna", 2) - .3, at("Aí", 2) - .25]
c += [at("eu", 1, c[8] + 3) - .25]
c += [at("dizendo", 2) - .45, at("Fazer", 1, at("mostra")) - .3, at("Domingo") - .25, DUR]

# 1 gancho: os 4 fizeram o L (2x2)
scene("dr_grade", c[0], c[1], {"titulo": "Fizeram o L", "sub": "quatro famosos", "icone": "", "cols": 2,
      "pessoas": [{"foto": F["anitta"], "nome": "Anitta", "t": 0.05}, {"foto": F["wagner"], "nome": "Wagner Moura", "t": at("Wagner")},
                  {"foto": F["bruna"], "nome": "Bruna Marquezine", "t": at("Bruna")}, {"foto": F["caze"], "nome": "Casimiro", "t": at("Casimiro")}],
      "t_l": at("L") - .1}, "gancho 4 fizeram o L")
# 2 consulta da Justiça Eleitoral: 4 cards empilhados abrem
scene("dr_cartas", c[1], c[2], {"titulo": "Justiça Eleitoral", "sub": SUB, "icone": "urna", "cards": [CD[k] for k in CD],
                                "t_fan": at("cada") - .2}, "consulta de cada um")
# 3 gesto rápido
scene("dr_frase", c[2], c[3], {"fotos": list(F.values()), "t_fotos": c[2] + .15, "linhas": [
    {"txt": "O gesto é rápido", "cor": "#fff", "t": at("gesto") - .1, "tam": 112},
    {"txt": "sorriso pra foto", "cor": AM, "t": at("sorriso") - .1, "tam": 112},
    {"txt": "e pronto.", "cor": "#fff", "t": at("pronto") - .15, "tam": 112}]}, "gesto rápido")
# 4 consulta é outra conversa
scene("dr_frase", c[3], c[4], {"linhas": [
    {"txt": "A consulta", "cor": AM, "t": at("consulta", 2) - .15, "tam": 150},
    {"txt": "é outra conversa", "cor": "#fff", "t": at("outra") - .1, "tam": 112},
    {"txt": "uma por uma", "cor": AM, "t": at("uma", 1, c[3]) - .1, "tam": 130}]}, "outra conversa")
# 5 Anitta
pessoa("anitta", c[4], c[5], t_l=c[4] + .6, t_card=at("linha") - .15, t_red=at("vermelha") + .05)
# 6 Wagner
pessoa("wagner", c[5], c[6], t_l=at("Wagner", 2) + .2, t_card=at("cara") - .1, t_red=at("vermelha", 2) - .1)
# 7 a lista não acabou
scene("dr_barras", c[6], c[7], {"titulo": "A lista", "sub": SUB, "icone": "urna", "linhas": [
    {"nome": "Anitta", "sub": "linha vermelha", "foto": F["anitta"], "txt": "X", "cor": VM, "barra": False, "t": c[6] + .2},
    {"nome": "Wagner Moura", "sub": "linha vermelha", "foto": F["wagner"], "txt": "X", "cor": VM, "barra": False, "t": c[6] + .45},
    {"nome": "Bruna Marquezine", "sub": "a conferir", "foto": F["bruna"], "txt": "?", "cor": "#5a5a5e", "barra": False, "t": at("lista")},
    {"nome": "Casimiro", "sub": "a conferir", "foto": F["caze"], "txt": "?", "cor": "#5a5a5e", "barra": False, "t": at("lista") + .25},
]}, "a lista não acabou")
# 8 Bruna
pessoa("bruna", c[7], c[8], t_l=c[7] + .6, t_card=at("aviso") - .35, t_red=at("vermelho") - .05)
# 9 Cazé (pulso em cada "Cazé")
pessoa("caze", c[8], c[9], t_l=c[8] + .5, q="Escapou?", t_q=at("escapou"),
       pulsos=[at("Cazé"), at("Cazé", 2)], t_card=at("nada") - .2, t_red=at("cumprimento", 2) - .05)
# 10 não tô dizendo
scene("dr_frase", c[9], c[10], {"linhas": [
    {"txt": "Não tô dizendo", "cor": "#fff", "t": at("dizendo") - .3, "tam": 120},
    {"txt": "o que cada um fez", "cor": AM, "t": at("cada", 2) - .1, "tam": 110},
    {"txt": "ou deixou de fazer", "cor": "#fff", "t": at("deixou") - .1, "tam": 96}]}, "não tô dizendo")
# 11 o que a consulta mostra: 4 lado a lado
scene("dr_grade", c[10], c[11], {"titulo": "O que a consulta mostra", "sub": "", "icone": "urna", "cols": 4,
      "pessoas": [{"foto": F[k], "nome": n, "card": CD[k], "ry": RY[k], "rx": RX[k], "rw": .6, "t": c[10] + .15 + i * .12}
                  for i, (k, n) in enumerate([("anitta", "Anitta"), ("wagner", "Wagner"), ("bruna", "Bruna"), ("caze", "Cazé")])],
      "t_l": at("quatro", 2, c[10]) - .05, "t_cards": at("consulta", 1, c[10]) + .1, "t_red": at("linhas", 1, c[10]) - .05,
      "linhas": [{"txt": "4 famosos", "cor": "#fff", "t": at("quatro", 1, c[10]) - .05, "tam": 96},
                 {"txt": "4 L", "cor": AM, "t": at("quatro", 2, c[10]) - .05, "tam": 96},
                 {"txt": "4 linhas vermelhas", "cor": VM, "t": at("quatro", 3, c[10]) - .05, "tam": 96}]}, "4 lado a lado")
# 12 fazer o L é fácil
scene("dr_frase", c[11], c[12], {"linhas": [
    {"txt": "Fazer o L pra câmera", "cor": "#fff", "t": c[11] + .3, "tam": 100},
    {"txt": "é fácil", "cor": AM, "t": at("fácil") - .1, "tam": 130},
    {"txt": "o difícil é", "cor": "#fff", "t": at("difícil") - .2, "tam": 100},
    {"txt": "a consulta sair limpa", "cor": AM, "t": at("consulta", 1, c[11]) - .1, "tam": 110}]}, "consulta sair limpa")
# 13 domingo é dia 22
scene("dr_numero", c[12], c[13], {"rotulo": "Domingo é dia", "icone": "urna", "valor": "22", "tam": 440,
                                  "t_rot": at("Domingo"), "t_valor": at("dia", 1, c[12]) - .05}, "22")

# ---- legenda-frase (texto exato do roteiro) abaixo do gráfico, palavras-chave em amarelo
sent = re.split(r"(?<=[.?!])\s+", ROT)
parts = []
for s in sent:
    if len(s) > 78 and ", " in s:
        cs = [m.start() for m in re.finditer(r"[,:] ", s)]
        k = min(cs, key=lambda x: abs(x - len(s) / 2))
        parts += [s[:k + 1], s[k + 1:].strip()]
    else:
        parts.append(s)
RW = [x for p in parts for x in p.split()]
sm = difflib.SequenceMatcher(None, [norm(x) for x in RW], [norm(w["w"]) for w in W], autojunk=False)
mp = {}
for a, b, n in sm.get_matching_blocks():
    for j in range(n):
        mp[a + j] = b + j
def wi(r, d):
    while r not in mp and 0 <= r < len(RW):
        r += d
    return mp.get(r, 0 if d > 0 else len(W) - 1)
KW = ["Anitta", "Wagner Moura", "Bruna Marquezine", "Casimiro", "Cazé", "quatro L", "o L", "linha vermelha", "linhas vermelhas", "vermelho",
      "não cumprimento de obrigação eleitoral", "quatro famosos", "vinte e dois", "Justiça Eleitoral"]
i = 0; caps = []
for p in parts:
    n = len(p.split())
    caps.append((p, W[wi(i, 1)]["s"], W[wi(i + n - 1, -1)]["e"])); i += n
for k, (p, s, e) in enumerate(caps):
    fim = caps[k + 1][1] - .05 if k + 1 < len(caps) else DUR
    hl = sorted({h for h in KW if h in p}, key=len, reverse=True)
    items.append({"id": f"lg{k}", "type": "text", "track": "legenda", "label": p[:30], "start": round(max(0, s - .08), 2), "dur": round(fim - s + .08, 2),
                  "in": "fade", "out": "none", "props": {"text": p, "x": 540, "y": 1440, "w": 960, "size": 56, "color": "#ffffff", "font": "Inter", "weight": 600,
                  "align": "center", "shadow": False, "highlight": hl, "hl_color": AM, "line": 1.25}})

bg = {"id": "bg", "type": "html", "track": "fundo", "label": "fundo preto", "start": 0, "dur": DUR,
      "props": {"fill": True, "html": "<div class='drbg'></div>",
                "css": ".drbg{width:100%;height:100%;background:radial-gradient(ellipse at 50% 35%,#151517 0%,#0B0B0C 65%)}"}}
edit = {"version": 1, "name": NAME, "canvas": {"w": 1080, "h": 1920, "fps": 30, "bg": "#0B0B0C"}, "duration": DUR, "template": "generic",
        "grupo": "ESTILOS SHORTS", "estilo": "Dados ranking escuro amarelo",
        "referencia": {"canal": "@guustavolazaro", "canal_url": "https://www.instagram.com/guustavolazaro/",
                       "video": "https://www.instagram.com/p/Dez-WhwxoRp/", "nota": "fotos com o L e cards eleitorais recortados do reel; rosto do apresentador e @ não usados"},
        "fonts": {"Inter": "fonts/Inter.ttf", "Oswald": "fonts/Oswald-Bold.ttf"},
        "audio": {"voice": {"src": "voz.mp3", "volume": 1.0, "start": 0}},
        "tracks": [{"id": "fundo", "name": "Fundo"}, {"id": "visual", "name": "Gráficos"}, {"id": "legenda", "name": "Legenda"}],
        "items": [bg] + items}
json.dump(edit, open(os.path.join(D, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("cenas", [round(x, 2) for x in c])
print("legendas", len(caps), "dur", DUR, "roteiro", len(RW), "whisper", len(W))
