# Gera edit.json do short 01. TODO tempo sai do words.json (trocar voz = whisper + rodar de novo).
import json, os, re, unicodedata
D = os.path.dirname(os.path.abspath(__file__))
WORDS = json.load(open(os.path.join(D, "words.json"), encoding="utf-8"))
NAME = "01 - SAGA SOBREVIVENCIA 2D - Ataque nuclear - o bunker do avo - Parte 1"


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in s if unicodedata.category(c) != "Mn"))


cur = [-1.0]


def at(p, ocorrencia=1, end=False):
    """Início da palavra p (ou lista de alternativas), procurando a partir do cursor (ordem do roteiro)."""
    alts = [norm(x) for x in (p if isinstance(p, list) else [p])]
    n = 0
    for w in WORDS:
        if w["s"] <= cur[0]:
            continue
        if norm(w["w"]) in alts:
            n += 1
            if n == ocorrencia:
                cur[0] = w["s"]
                return round(w["e"] if end else w["s"], 2)
    print("AVISO palavra nao achada:", p, "depois de", cur[0])
    cur[0] += 0.4
    return round(cur[0], 2)


scenes = []


def sc(cena, start, label, textos=None, t=None):
    scenes.append({"cena": cena, "start": max(0.0, round(start - 0.08, 2)) if start > 0 else 0.0, "label": label,
                   "textos": textos or {}, "t": t or {}})


sc("rua_sirene", 0, "Sirene / rua", {"selo": "15 MIN"}, {"min15": at(["15", "quinze"])})
sc("cronometro", at("eles"), "15 min x estrada", {"selo": "15 MIN • QUALQUER ESTRADA", "relogio": "15:00"})
sc("encruzilhada", at("mas"), "Pra onde correr", {"p1": "ESTRADA", "p2": "CENTRO", "p3": "ABRIGO?"}, {"onde": at("onde")})
s = at("alerta")
sc("alerta", s, "Alerta no celular",
   {"topo": "ALERTA DE EMERGÊNCIA", "titulo": "ATAQUE NUCLEAR", "sub": "PROCURE ABRIGO IMEDIATAMENTE", "hora": "18:40"},
   {"hora": at(["6", "18", "seis", "6h40", "18h40"])})
sc("avenida", at("em"), "Avenida parada", {"selo": "AVENIDA TRAVADA", "selo2": "+10 MIN"}, {"parada": at("parada")})
sc("carro", at("carro"), "Carro = caixa de lata", {"rotulo": "CAIXA DE LATA"}, {"lata": at("lata"), "chuva": at("chuva")})
sc("corrida", at("rafa"), "Rafa corre pro quintal")
sc("bunker", at("embaixo"), "Bunker do avô 1982", {"ano": "1982", "rotulo": "BUNKER DO AVÔ"},
   {"bunker": at("bunker"), "ano": at(["1982", "mil"])})
sc("muro", at("caminho"), "Rafa olha o muro", {}, {"muro": at("muro")})
s = at("luz")
sc("janela", s - 0.2, "Janela acesa da vizinha", {}, {"luz": s})
sc("espiada", at("nunca"), "Coragem de falar", {}, {"coragem": at("coragem")})
sc("pular", at("por"), "Pensa em pular", {}, {"pular": at("pular")})
sc("flash", at("entao"), "Clarão", {}, {"clarao": at("clarao")})
sc("nao_olhe", at("nao"), "Não olhe. Conte.", {"t1": "NÃO OLHE.", "t2": "CONTE."}, {"conte": at("conte")})
s = at("luz")
sc("cogumelo", s, "Luz vs som", {"a": "0 S", "a2": "LUZ", "b": "+30 S", "b2": "SOM"}, {"luz": s, "estrondo": at("estrondo")})
sc("regra3s", at("cada"), "3 s = 1 km", {"f1": "3 S", "f2": "1 KM", "rodape": "SILÊNCIO = DISTÂNCIA"})
sc("contagem", at("rafa"), "Conta 31 = 10 km", {"n": "31", "km": "= 10 KM", "rotulo": "SEGUNDOS"},
   {"n31": at(["31", "trinta"]), "km": at(["10", "dez"])})
sc("escotilha", at("fecha"), "Fecha a escotilha", {"selo": "TRAVADO"}, {"gira": at("gira"), "travas": at("travas")})
sc("poeira", at("poeira"), "Poeira cai", {"selo1": "POEIRA EM ~20 MIN", "selo2": "REGRA DO BUNKER"},
   {"min20": at(["20", "vinte"]), "regra": at("regra")})
sc("grafico", at("depois"), "Gráfico radiação",
   {"l1": "7 H • ÷10", "l2": "2 DIAS • ÷100", "eixo": "TEMPO DEPOIS DA EXPLOSÃO", "topo": "100%"},
   {"h7": at(["7", "sete"]), "depois2": at("depois"), "d2": at(["2", "dois"]), "c100": at(["100", "cem"])})
sc("calendario", at("entao"), "14 dias", {"cab": "14 DIAS", "topo": "NÃO PODE SAIR"}, {"d14": at(["14", "quatorze", "catorze"])})
sc("estoque", at("papel"), "Estoque 16 dias", {"titulo": "ESTOQUE", "l1": "ÁGUA", "l2": "COMIDA", "dias": "16 DIAS", "so": "SÓ PRA ELE"},
   {"d16": at(["16", "dezesseis"]), "so": at("so")})
sc("problema", at("so"), "Um problema", {"t": "UM PROBLEMA."})
sc("batidas", at(["as", "a"]), "3 batidas na escotilha", {"hora": "23:00", "b": "3×", "b2": "BATIDAS"},
   {"hora": at(["11", "onze", "23"]), "bateu": at("bateu"), "b3": at(["3", "tres"])})
sc("medidor", at("la"), "Medidor letal", {"r": "LETAL", "topo": "RADIAÇÃO"}, {"letal": at("letal")})
fim = round(WORDS[-1]["e"] + 0.3, 2)  # fim da última palavra
sc("fim", fim + 0.08, "Parte 2", {"t": "PARTE 2", "s": "QUEM ESTÁ LÁ FORA?"})
DUR = round(fim + 3.2, 2)

items = []
for i, c in enumerate(scenes):
    e = scenes[i + 1]["start"] if i + 1 < len(scenes) else DUR
    items.append({"id": f"c{i + 1:02d}", "type": "html", "track": "fundo", "by": "template", "label": c["label"],
                  "start": c["start"], "dur": round(e - c["start"], 2),
                  "props": {"cena": c["cena"], "textos": c["textos"], "t": c["t"], "html": "", "fill": True}})
items.append({"id": "leg", "type": "caption", "track": "legenda", "label": "Legenda", "start": 0, "dur": DUR,
              "props": {"words_file": "words.json", "per_group": 3, "x": 540, "y": 1330, "size": 70, "font": "Oswald", "weight": 400,
                        "color": "#ffffff", "dim": "#ffffff", "hl_color": "#E8B23A", "bg": "rgba(12,12,12,.74)", "shadow": False,
                        "keywords": ["sirene", "15", "estrada", "alerta", "parada", "chuva", "radioativa", "bunker", "1982", "muro",
                                     "vizinha", "coragem", "clarão", "olhe", "conte", "estrondo", "silêncio", "31", "km", "quilômetro", "escotilha",
                                     "travas", "poeira", "regra", "radiação", "vezes", "14", "16", "problema", "bateu", "letal"]}})
items.append({"id": "leg_vermelho", "type": "param", "label": "Legenda: palavras em vermelho",
              "props": {"value": "sirene,alerta,parada,chuva,radioativa,clarão,olhe,estrondo,radiação,problema,bateu,letal"}})

edit = {"version": 1, "name": NAME, "grupo": "ESTILOS SHORTS", "estilo": "Saga sobrevivência 2D (série)",
        "canvas": {"w": 1080, "h": 1920, "fps": 30, "bg": "#E9C9A0"}, "duration": DUR, "template": "local",
        "fonts": {"Oswald": "fonts/Oswald-Bold.ttf"},
        "referencia": {"canal": "@sobreviventeend", "canal_url": "https://www.instagram.com/sobreviventeend/",
                       "video": "https://www.instagram.com/reel/Dep0Ev7xo79/", "titulo": "Ataque nuclear — ep. 1 (270 mil views)",
                       "nota": "também https://www.instagram.com/reel/Dep0Nj7xizD/ ; personagem e cenários originais em SVG"},
        "audio": {"voice": {"src": "voz.mp3", "volume": 1.0, "start": 0}},
        "tracks": [{"id": "fundo", "name": "Cenas 2D"}, {"id": "legenda", "name": "Legenda"}],
        "items": items}
json.dump(edit, open(os.path.join(D, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("cenas", len(scenes), "dur", DUR)
for it in items[:-2]:
    print(it["id"], it["start"], it["dur"], it["props"]["cena"], it["props"]["t"])
