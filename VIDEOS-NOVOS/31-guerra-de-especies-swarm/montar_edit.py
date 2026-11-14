import json, os
O = os.path.dirname(os.path.abspath(__file__))
NAME = "31 - GUERRA DE ESPECIES SWARM - Por que as vespas têm medo das libélulas"
DUR = 44.0
items = []

def sw(id, s, e, modo, label, **p):
    params = {"modo": modo, "seed": len(items) + 3, "fade_in": 0.4 if s > 0 else 0}
    params.update(p)
    items.append({"id": id, "type": "scene", "track": "fundo", "label": label, "start": s, "dur": round(e - s, 2),
                  "props": {"scene": "sw_swarm", "params": params}})

def vid(id, s, e, src, label):
    items.append({"id": id, "type": "video", "track": "fundo", "label": label, "start": s, "dur": round(e - s, 2),
                  "in": "fade" if s > 0 else "none",
                  "props": {"src": "clips/" + src, "fill": True, "fit": "cover", "trim": 0, "volume": 0, "speed": 1, "opacity": 1, "motion": "zoom_in"}})

def foto(id, s, e, src, nome, sub, cred, motion="zoom_in"):
    items.append({"id": id, "type": "scene", "track": "fundo", "label": f"Foto {nome}", "start": s, "dur": round(e - s, 2),
                  "props": {"scene": "cosmos_foto", "params": {"src": "img/" + src, "motion": motion, "amount": 0.10, "pos": "50% 50%",
                            "nome": nome, "sub": sub, "credito": cred, "fade_in": 0.4, "fade_out": 0}}})

def rot(id, s, e, txt):  # rótulo de lugar/espécie no canto (estilo SwarmTheory)
    items.append({"id": id, "type": "text", "track": "textos", "label": f"Rótulo {txt}", "start": s, "dur": round(e - s, 2), "in": "fade", "out": "fade",
                  "props": {"text": txt, "x": 330, "y": 64, "w": 600, "size": 36, "color": "#f2f2ea", "font": "Outfit", "weight": 500,
                            "align": "left", "bg": "", "shadow": True}})

def tit(id, s, e, txt, y=600, size=56):
    items.append({"id": id, "type": "text", "track": "textos", "label": f"Texto {txt[:24]}", "start": s, "dur": round(e - s, 2), "in": "slide_up", "out": "fade",
                  "props": {"text": txt, "x": 640, "y": y, "w": 1150, "size": size, "color": "#ffffff", "font": "Outfit", "weight": 700,
                            "align": "center", "bg": "rgba(6,22,21,.55)", "pad": 16, "radius": 10, "shadow": True}})

vid("s01", 0.0, 2.4, "vwasp1.mp4", "Vídeo vespas no ninho")
rot("r01", 0.2, 2.3, "Vespa")
tit("x01", 0.3, 2.3, "O terror dos céus?")
vid("s02", 2.35, 4.0, "vdfly1.mp4", "Vídeo libélula")
rot("r02", 2.5, 3.9, "Libélula")
sw("s03", 3.95, 5.7, "caca", "Enxame: libélulas caçando vespas", rotulo="Caça no ar")
items.append({"id": "s04", "type": "scene", "track": "fundo", "label": "Número 95%", "start": 5.6, "dur": 2.2,
              "props": {"scene": "sw_stat", "params": {"valor": 95, "prefixo": "", "sufixo": "%", "legenda": "de sucesso na caça",
                                                        "rotulo": "", "cor": "#5cc8ff", "seed": 5, "t_conta": 0.1, "conta_dur": 0.8, "fade_in": 0.3}}})
foto("s05", 7.7, 10.5, "ieye1.jpg", "Processamento", "não é força", "Pixabay / Pexels")
sw("s06", 10.4, 15.5, "intercepta", "Prevê trajetória e intercepta", rotulo="Cérebro da libélula",
   l1="prevê a trajetória", l2="intercepta", l3="não persegue")
sw("s07", 15.45, 18.6, "asas", "4 asas independentes", titulo="4 asas", sub="batem de forma independente", t_titulo=0.4)
sw("s08", 18.55, 21.6, "virada", "Virada de 90 graus", l1="90°", l2="em décimos de segundo")
foto("s09", 21.5, 23.4, "iwasp3.jpg", "Ferrão", "a arma da vespa", "Pixabay / DerWeg", "pan_left")
sw("s10", 23.3, 27.15, "captura", "Agarra pelo tórax, asas caem", l1="tórax", l2="asas", titulo="", sub="antes que a vítima reaja", t_titulo=2.9)
sw("s11", 27.1, 30.9, "devora", "Uma libélula devora dezenas", titulo="dezenas de insetos", sub="por dia", t_titulo=1.5)
vid("s12", 30.8, 33.8, "vwasp2.mp4", "Vídeo vespa comendo")
rot("r12", 31.0, 33.7, "Vespa: presas paradas")
vid("s13", 33.7, 36.3, "vdfly0.mp4", "Vídeo libélula asas abertas")
rot("r13", 33.9, 36.2, "Libélula: mata no voo")
sw("s14", 36.2, 39.6, "frente", "Frente de batalha", titulo="Quem vence?", t_titulo=0.1, titulo_fim=1.1)
tit("x14", 37.3, 39.4, "Inscreva-se para ver o próximo duelo", y=360, size=54)
vid("s15", 39.5, DUR, "vforest0.mp4", "Drone floresta e rio")
tit("x15", 39.7, 43.2, "A natureza não perdoa erro de cálculo.", y=600, size=52)

fundo = sorted([i for i in items if i["track"] == "fundo"], key=lambda i: i["start"])
for a, b in zip(fundo, fundo[1:]):
    a["dur"] = round(max(a["dur"], b["start"] + 0.5 - a["start"]), 2)

edit = {
    "version": 1, "name": NAME, "estilo": "31-guerra-de-especies-swarm", "grupo": "ESTILOS NOVOS",
    "canvas": {"w": 1280, "h": 720, "fps": 30, "bg": "#0a1f1d"}, "duration": DUR, "template": "generic",
    "fonts": {"Outfit": "fonts/Outfit.ttf"}, "head": "",
    "referencia": {"canal": "SwarmTheory", "canal_url": "https://www.youtube.com/channel/UCnQGQTq_hH7h7v84eApwcUA",
                   "video": "https://youtu.be/18gEjxdSuxc", "titulo": "The Biggest War Between Species on Planet Earth",
                   "nota": "Fundo verde-petróleo texturizado + enxames de partículas laranja x azul (canvas seeded), macro stock real Pixabay, rótulos no canto, pouco texto. Tema = 'Why Wasps are Terrified of Dragonflies'."},
    "audio": {"voice": {"src": "voz.mp3", "volume": 1.0, "start": 0},
              "music": {"src": "musica.mp3", "volume": 0.10, "start": 0, "fade_out": 2.0, "duck": True}, "extra": []},
    "tracks": [{"id": "fundo", "name": "Cenas / mídia"}, {"id": "textos", "name": "Textos"}],
    "items": items,
}
json.dump(edit, open(os.path.join(O, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("itens", len(items))
