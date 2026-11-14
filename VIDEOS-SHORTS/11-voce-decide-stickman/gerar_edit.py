# Gera edit.json do short 11 (VOCE DECIDE STICKMAN). Todo tempo sai do words.json (trocar voz = whisper + corrigir_words + rodar de novo).
import json, os, re, unicodedata
D = os.path.dirname(os.path.abspath(__file__))
WORDS = json.load(open(os.path.join(D, "words.json"), encoding="utf-8"))
NAME = "11 - 24-10-2026 - VOCE DECIDE STICKMAN - Mensagem de voce mesmo as 3h07 - Parte 1"


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in s if unicodedata.category(c) != "Mn"))


cur = [-1.0]


def at(p, ocorrencia=1, end=False):
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


HUD = {"noite": "NOITE 1", "parte": "PARTE 1"}
sc("quarto", 0, "Quarto escuro 3:07", {"hora": "3:07", "ampm": "AM", "local": "QUARTO"}, {"vibra": at("vibra")})
sc("celular", at("uma"), "Mensagem de você mesmo",
   {"hora": "3:07", "ampm": "AM", "local": "QUARTO", "remetente": "VOCÊ", "numero": "+55 (11) 9 8471-2207",
    "msg": "Não acende a luz.", "selo": "MENSAGEM 1"},
   {"voce": at("voce"), "numero": at("numero"), "foto": at("foto"), "msg": at("nao")})
sc("rindo", at("voce"), "Você ri: golpe?", {"hora": "3:07", "ampm": "AM", "local": "QUARTO", "balao": "GOLPE?"},
   {"golpe": at("golpe")})
sc("celular2", at("ai"), "2ª mensagem: corredor",
   {"hora": "3:08", "ampm": "AM", "local": "QUARTO", "remetente": "VOCÊ", "msg": "Tem alguém no corredor.", "selo": "MENSAGEM 2"},
   {"msg": at("tem")})
sc("porta", at("voce"), "Piso range / sombra na porta", {"hora": "3:08", "ampm": "AM", "local": "CORREDOR", "som": "CREEK"},
   {"range": at(["range", "rende"]), "uma": at("vez"), "duas": at("duas")})
sc("macaneta", at("macaneta"), "Maçaneta gira e para", {"hora": "3:08", "ampm": "AM", "local": "PORTA DO QUARTO"},
   {"girar": at("girar"), "para": at("para")})
sc("celular3", at("terceira"), "3ª mensagem: não te viu",
   {"hora": "3:08", "ampm": "AM", "local": "QUARTO", "remetente": "VOCÊ", "msg": "Ele ainda não te viu.",
    "msg2": "No escuro, ele não te encontra.", "selo": "MENSAGEM 3"},
   {"msg": at("ele"), "msg2": at("escuro")})
sc("relogio", at("tres"), "3:09 relógio", {"hora": "3:09", "ampm": "AM", "local": "QUARTO", "grande": "3:09"},
   {"tela": at("tela")})
sc("celular4", at("ultima"), "Última: acende a luz. Agora.",
   {"hora": "3:09", "ampm": "AM", "local": "QUARTO", "remetente": "VOCÊ", "msg": "Acende a luz.", "msg2": "AGORA.", "selo": "ÚLTIMA MENSAGEM"},
   {"msg": at("acende"), "agora": at("agora")})
sc("duas", at("duas"), "Duas ordens, mesmo número",
   {"hora": "3:09", "ampm": "AM", "local": "QUARTO", "a": "Não acende a luz.", "b": "Acende a luz. Agora.", "num": "MESMO NÚMERO",
    "selo": "UMA DELAS NÃO É VOCÊ"},
   {"numero": at("numero"), "delas": at("delas")})
s = at("entao")
sc("escolha", s, "Escolha A ou B",
   {"hora": "3:09", "ampm": "AM", "local": "QUARTO", "titulo": "VOCÊ DECIDE", "a": "ACENDE A LUZ", "b": "FICA NO ESCURO",
    "fim": "PARTE 2 DEPENDE DE VOCÊ"},
   {"comenta": at("comenta"), "A": at("a"), "B": at("b"), "parte": at("parte")})
fim = round(WORDS[-1]["e"] + 0.2, 2)
DUR = round(fim + 1.6, 2)

items = []
for i, c in enumerate(scenes):
    e = scenes[i + 1]["start"] if i + 1 < len(scenes) else DUR
    items.append({"id": f"c{i + 1:02d}", "type": "html", "track": "fundo", "by": "template", "label": c["label"],
                  "start": c["start"], "dur": round(e - c["start"], 2),
                  "props": {"cena": c["cena"], "textos": c["textos"], "t": c["t"], "html": "", "fill": True}})
items.append({"id": "hud_noite", "type": "param", "label": "HUD: dia/noite", "props": {"value": HUD["noite"]}})
items.append({"id": "hud_parte", "type": "param", "label": "HUD: parte", "props": {"value": HUD["parte"]}})
items.append({"id": "leg", "type": "caption", "track": "legenda", "label": "Legenda", "start": 0, "dur": DUR,
              "props": {"words_file": "words.json", "per_group": 3, "x": 540, "y": 1290, "size": 84, "font": "Montserrat", "weight": 900,
                        "color": "#ffffff", "dim": "#ffffff", "hl_color": "#FFD23F", "shadow": True, "upper": True,
                        "keywords": ["escuro", "mesmo", "foto", "luz", "golpe", "corredor", "respira", "range", "duas", "maçaneta",
                                     "girar", "devagar", "para.", "viu", "encontra", "nove", "agora", "ordens", "delas", "dois"]}})
items.append({"id": "leg_verde", "type": "param", "label": "Legenda: palavras em verde",
              "props": {"value": "acende,acender,luz"}})

# whoosh baixo só nas viradas de mensagem (sem impact/pop)
wh = [it["start"] for it in items if it.get("props", {}).get("cena") in ("celular", "celular2", "celular3", "relogio", "duas", "escolha")]
extra = [{"id": f"w{k}", "src": "sfx/whoosh.wav", "start": round(max(0, t - 0.15), 2), "volume": 0.16, "label": "whoosh"} for k, t in enumerate(wh)]

edit = {"version": 1, "name": NAME, "grupo": "ESTILOS SHORTS", "estilo": "Você decide stickman (história interativa)",
        "canvas": {"w": 1080, "h": 1920, "fps": 30, "bg": "#0d1014"}, "duration": DUR, "template": "local",
        "fonts": {"Montserrat": "fonts/Montserrat-Black.ttf", "Inter": "fonts/Inter.ttf"},
        "referencia": {"canal": "@stickmanstorys22", "video": "https://www.tiktok.com/@stickmanstorys22/video/7699365027945532690",
                       "nota": "também @stickitoutstories https://www.youtube.com/shorts/sY5gfQ6btLM ; boneco e cenários originais em SVG"},
        "audio": {"voice": {"src": "voz.mp3", "volume": 1.0, "start": 0},
                  "music": {"src": "musica.mp3", "volume": 0.22, "start": 0, "fade_out": 1.5, "duck": True},
                  "extra": extra},
        "tracks": [{"id": "fundo", "name": "Cenas 2D"}, {"id": "legenda", "name": "Legenda"}],
        "items": items}
json.dump(edit, open(os.path.join(D, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("cenas", len(scenes), "dur", DUR)
for it in items:
    if it["type"] == "html":
        print(it["id"], it["start"], it["dur"], it["props"]["cena"], it["props"]["t"])
