# Gera edit.json do short 06 (dados/ranking escuro amarelo). TODO tempo vem de words.json (trocar voz = whisper + rodar de novo).
import json, os, re, unicodedata
D = os.path.dirname(os.path.abspath(__file__))
NAME = "06 - DADOS RANKING ESCURO - O deputado que nao cabe no grafico"
WJ = json.load(open(os.path.join(D, "words.json"), encoding="utf-8"))
RAW = WJ["words"]
DUR = round(WJ["duration"] + 0.6, 2)
ROT = open(os.path.join(D, "roteiro.txt"), encoding="utf-8").read().strip()

# junta fragmentos numéricos do whisper ("3" ",1" -> "3,1"; "69" "%" -> "69%"; "1" ".327." -> "1.327.")
W = []
for w in RAW:
    if W and re.match(r"^([.,]\d|%)", w["w"]):
        W[-1] = {"w": W[-1]["w"] + w["w"], "s": W[-1]["s"], "e": w["e"]}
    else:
        W.append(dict(w))

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

items = []
def scene(nome, s, e, params, label):
    items.append({"id": f"sc{len(items)}", "type": "scene", "track": "visual", "label": label, "start": round(s, 2), "dur": round(e - s, 2),
                  "props": {"scene": nome, "params": params}})

AM, CZ = "#F5C518", "#5a5a5e"
NIK = "img/nikolas.jpg"; LULA = "img/lula.jpg"; FLA = "img/flavio.jpg"

# ---- cortes de cena (início de cada frase)
c = [0.0, at("Nikolas") - .25, at("recorde") - .4, at("Nikolas", 2) - .3, at("Instagram") - .3, at("mundo") - .3, at("Lula") - .3,
     at("11") - .5, at("TikTok") - .3, at("Lula", 2) - .3, at("curtidas") - .5, at("30") - .3, at("Por") - .3, at("aí") - .4, DUR]

# 1 gancho: barra do Nikolas estoura o gráfico
scene("dr_barras", c[0], c[1], {"titulo": "Deputado federal", "sub": "os mais votados da história", "icone": "urna", "linhas": [
    {"nome": "Recorde anterior", "sub": "São Paulo", "valor": 1.84, "txt": "", "ini": "SP", "cor": CZ, "t": 0.25},
    {"nome": "Nikolas Ferreira", "sub": "Minas Gerais", "foto": NIK, "over": True, "dest": True, "t": at("cabe")},
], "max": 3.1}, "gancho: não cabe no gráfico")
# 2 número gigante 3,1 milhões
scene("dr_numero", c[1], c[2], {"rotulo": "Nikolas Ferreira · votos na urna", "foto": NIK, "valor": "3,1", "unidade": "milhões",
                                "sub": "de votos", "t_valor": at("3,1"), "t_sub": at("votos")}, "3,1 milhões")
# 3 recorde anterior x Nikolas
scene("dr_barras", c[2], c[3], {"titulo": "Recorde de votos", "sub": "votos na urna", "icone": "urna", "linhas": [
    {"nome": "Recorde anterior", "sub": "SP · maior eleitorado", "ini": "SP", "valor": 1.84, "txt": "1,84 MI", "cor": "#9a9aa0", "t": at("1,84")},
    {"nome": "Nikolas Ferreira", "sub": "Minas Gerais", "foto": NIK, "valor": 3.1, "txt": "3,1 MI", "dest": True, "t": at("Paulo")},
]}, "recorde 1,84 x 3,1")
# 4 mapa MG +69%
scene("dr_mapa", c[3], c[4], {"titulo": "Votos em Minas Gerais", "sub": "Nikolas Ferreira", "t_pontos": c[3] + .3,
                              "valor": "+69%", "t_valor": at("69%"), "rot_valor": "a mais que o recorde",
                              "nota": "com menos da metade dos eleitores", "t_nota": at("menos")}, "mapa MG +69%")
# 5 instagram 25 milhões
scene("dr_numero", c[4], c[5], {"rotulo": "Instagram", "icone": "ig", "valor": "25", "unidade": "milhões", "sub": "de seguidores",
                                "t_valor": at("25"), "t_sub": at("seguidores")}, "IG 25 milhões")
# 6 ranking mundial IG
t6 = at("seis")
scene("dr_barras", c[5], c[7], {"titulo": "Mais seguidos no Instagram", "sub": "políticos no mundo", "icone": "ig", "linhas": [
    {"pos": "1º–6º", "grupo": 6, "nome": "6 políticos à frente", "t": t6},
    {"pos": "7º", "nome": "Nikolas Ferreira", "sub": "Brasil", "foto": NIK, "valor": 25, "txt": "25 MI", "dest": True, "sobe": True, "t": t6 + .7},
    {"nome": "Lula", "sub": "Brasil", "foto": LULA, "valor": 18, "txt": "18 MI", "cor": "#e04848", "t": at("18")},
    {"nome": "Flávio Bolsonaro", "sub": "Brasil", "foto": FLA, "valor": 15, "txt": "15 MI", "cor": "#3f7fe0", "t": at("15")},
]}, "ranking IG mundo")
# 7 linha crescendo 11 meses
scene("dr_linha", c[7], c[8], {"titulo": "Seguidores no Instagram", "sub": "ganho acumulado · 11 meses", "icone": "ig",
                               "valores": [0, .35, .7, 1.05, 1.4, 1.75, 2.1, 2.45, 2.8, 3.15, 3.5, 6.2],
                               "labels": ["11 meses atrás", "", "", "", "", "", "", "", "", "", "", "outubro"],
                               "t_ini": at("11"), "t_fim": at("6,2") + .2, "rot_fim": "+6,2 MI", "t_rot": at("6,2"),
                               "dest_ini": 10, "t_dest": at("outubro") - .1, "rot_dest": "+2,7 MI EM OUTUBRO", "t_dest2": at("2,7")}, "linha +6,2 mi")
# 8 ranking TikTok
t8 = at("quinto")
scene("dr_barras", c[8], c[9], {"titulo": "Mais seguidos no TikTok", "sub": "políticos no mundo", "icone": "tt", "linhas": [
    {"pos": "1º–4º", "grupo": 4, "nome": "4 políticos à frente", "t": t8 - .2},
    {"pos": "5º", "nome": "Nikolas Ferreira", "sub": "Brasil", "foto": NIK, "dest": True, "sobe": True, "t": t8 + .3},
    {"nome": "Emmanuel Macron", "sub": "presidente da França", "foto": "img/macron.jpg", "t": at("França")},
    {"nome": "Claudia Sheinbaum", "sub": "presidenta do México", "foto": "img/sheinbaum.jpg", "t": at("México")},
]}, "ranking TikTok mundo")
# 9 TikTok Lula x Flávio
scene("dr_barras", c[9], c[10], {"titulo": "Seguidores no TikTok", "sub": "brasileiros", "icone": "tt", "linhas": [
    {"nome": "Nikolas Ferreira", "sub": "5º político do mundo", "foto": NIK, "dest": True, "t": c[9] + .2},
    {"nome": "Lula", "sub": "presidente", "foto": LULA, "valor": 6.2, "txt": "6,2 MI", "cor": "#e04848", "t": at("6,2", 2)},
    {"nome": "Flávio Bolsonaro", "sub": "senador", "foto": FLA, "valor": 2.5, "txt": "2,5 MI", "cor": "#3f7fe0", "t": at("2,5", 1, c[9])},
]}, "TikTok Lula x Flávio")
# 10 curtidas acumuladas
scene("dr_barras", c[10], c[11], {"titulo": "Curtidas acumuladas", "sub": "no TikTok", "icone": "tt", "linhas": [
    {"nome": "Nikolas Ferreira", "sub": "em 705 vídeos", "foto": NIK, "valor": 205, "txt": "205 MI", "dest": True, "t": at("205"), "t_sub": at("705")},
    {"nome": "Lula", "sub": "em 1.327 vídeos", "foto": LULA, "valor": 87, "txt": "87 MI", "cor": "#e04848", "t": at("87"), "t_sub": at("1.327")},
    {"nome": "Flávio Bolsonaro", "sub": "em 1.712 vídeos", "foto": FLA, "valor": 36, "txt": "36 MI", "cor": "#3f7fe0", "t": at("36"), "t_sub": at("1.712")},
]}, "curtidas 205/87/36")
# 11 mosaico 23 posts + 58,8 mi
scene("dr_mosaico", c[11], c[12], {"titulo": "30 dias no Instagram", "sub": "setembro → outubro", "icone": "ig", "n": 23,
                                   "t_ini": at("30") + .2, "t_cont": at("23"), "rot": "POSTS", "valor": "58,8 MILHÕES", "t_valor": at("58,8"),
                                   "sub_valor": "de curtidas e comentários", "t_sub": at("curtidas", 2)}, "23 posts / 58,8 mi")
# 12 por post 2,5 milhões
scene("dr_numero", c[12], c[13], {"rotulo": "Por post · em média", "icone": "ig", "valor": "2,5", "unidade": "milhões",
                                  "sub": "de curtidas e comentários", "t_valor": at("2,5", 1, c[12]), "t_sub": at("média")}, "por post 2,5 mi")
# 13 fecho
scene("dr_numero", c[13], c[14], {"rotulo": "Esses números te surpreenderam?", "icone": "chat", "valor": "COMENTA", "tam": 210,
                                  "t_rot": at("esses"), "t_valor": at("Comenta")}, "fecho comenta")

# ---- legenda-frase (texto exato do roteiro) abaixo do gráfico, números em amarelo
sent = re.split(r"(?<=[.?!])\s+", ROT)
parts = []
for s in sent:
    if len(s) > 78 and ", " in s:  # frase longa: quebra na vírgula mais perto do meio
        cs = [m.start() for m in re.finditer(", ", s)]
        k = min(cs, key=lambda x: abs(x - len(s) / 2))
        parts += [s[:k + 1], s[k + 1:].strip()]
    else:
        parts.append(s)
import difflib
RW = [x for p in parts for x in p.split()]
sm = difflib.SequenceMatcher(None, [norm(x) for x in RW], [norm(w["w"]) for w in W], autojunk=False)
mp = {}
for a, b, n in sm.get_matching_blocks():
    for j in range(n):
        mp[a + j] = b + j
def wi(r, d):  # índice whisper mais próximo da palavra r do roteiro
    while r not in mp:
        r += d
    return mp[r]
i = 0; caps = []
for p in parts:
    n = len(p.split())
    caps.append((p, W[wi(i, 1)]["s"], W[wi(i + n - 1, -1)]["e"])); i += n
i = len(W)
for k, (p, s, e) in enumerate(caps):
    fim = caps[k + 1][1] - .05 if k + 1 < len(caps) else DUR
    hl = sorted(set(re.findall(r"\+?\d[\d.,]*\d%?(?:\s+(?:milhões|milhão))?|\b\d+%?(?:\s+(?:milhões|milhão|meses|dias|vezes))?|\b(?:seis|quinto)\b", p)), key=len, reverse=True)
    items.append({"id": f"lg{k}", "type": "text", "track": "legenda", "label": p[:30], "start": round(s - .08, 2), "dur": round(fim - s + .08, 2),
                  "in": "fade", "out": "none", "props": {"text": p, "x": 540, "y": 1330, "w": 960, "size": 56, "color": "#ffffff", "font": "Inter", "weight": 600,
                  "align": "center", "shadow": False, "highlight": [h.rstrip(".,") for h in hl], "hl_color": AM, "line": 1.25}})
if i != len(W):
    print(f"AVISO: roteiro tem {i} palavras e whisper {len(W)} — confira a legenda")

bg = {"id": "bg", "type": "html", "track": "fundo", "label": "fundo preto", "start": 0, "dur": DUR,
      "props": {"fill": True, "html": "<div class='drbg'></div>",
                "css": ".drbg{width:100%;height:100%;background:radial-gradient(ellipse at 50% 35%,#151517 0%,#0B0B0C 65%)}"}}
edit = {"version": 1, "name": NAME, "canvas": {"w": 1080, "h": 1920, "fps": 30, "bg": "#0B0B0C"}, "duration": DUR, "template": "generic",
        "grupo": "ESTILOS SHORTS", "estilo": "Dados ranking escuro amarelo",
        "referencia": {"canal": "@nikolasferreirabr", "canal_url": "https://www.instagram.com/nikolasferreirabr/",
                       "video": "https://www.instagram.com/reel/DezYwoNydqk/", "nota": "só o formato visual (infográfico preto/amarelo); logo do canto não copiado"},
        "fonts": {"Inter": "fonts/Inter.ttf", "Oswald": "fonts/Oswald-Bold.ttf"},
        "audio": {"voice": {"src": "voz.mp3", "volume": 1.0, "start": 0}},
        "tracks": [{"id": "fundo", "name": "Fundo"}, {"id": "visual", "name": "Gráficos"}, {"id": "legenda", "name": "Legenda"}],
        "items": [bg] + items}
json.dump(edit, open(os.path.join(D, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("cenas", [round(x, 2) for x in c])
print("legendas", len(caps), "dur", DUR)
