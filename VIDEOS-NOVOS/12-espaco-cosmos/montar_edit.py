import json, os
O = os.path.dirname(os.path.abspath(__file__))
NAME = "12 - ESPACO COSMOS - O que existe no centro da Via Láctea"
DUR = 66.0
items = []

def foto(id, s, e, src, motion="zoom_in", amount=0.08, nome="", sub="", credito="", pos="50% 50%", fo=0, label=""):
    items.append({"id": id, "type": "scene", "track": "fundo", "label": label or f"Foto {src}", "start": s, "dur": round(e - s, 2),
                  "props": {"scene": "cosmos_foto", "params": {"src": "img/" + src, "motion": motion, "amount": amount, "pos": pos,
                            "nome": nome, "sub": sub, "credito": credito, "fade_in": 1.0, "fade_out": fo}}})

def three(id, s, e, modo, seed=1, nome="", sub="", credito="Simulação ilustrativa", label=""):
    items.append({"id": id, "type": "scene", "track": "fundo", "label": label or f"3D {modo}", "start": s, "dur": round(e - s, 2),
                  "props": {"scene": "cosmos_three", "params": {"modo": modo, "seed": seed, "nome": nome, "sub": sub,
                            "credito": credito if nome else "", "fade_in": 1.0 if s > 0 else 0, "fade_out": 0}}})

def cap(id, s, e, titulo, sub=""):
    items.append({"id": id, "type": "scene", "track": "textos", "label": f"Capítulo: {titulo}", "start": s, "dur": round(e - s, 2),
                  "props": {"scene": "cosmos_capitulo", "params": {"titulo": titulo, "sub": sub, "fade": 1.5}}})

EHT = "EHT Collaboration · CC BY 4.0"
ESO = "ESO · CC BY 4.0"
three("s01", 0.0, 4.6, "voo", 1, label="3D galáxia (voo ao centro)")
foto("s02", 3.6, 8.7, "eht_1.jpg", "zoom_in", 0.10, "Sagitário A*", "buraco negro supermassivo", EHT)
items.append({"id": "s03", "type": "scene", "track": "fundo", "label": "Número 4 milhões", "start": 8.1, "dur": 3.5,
              "props": {"scene": "cosmos_numero", "params": {"valor": "4", "unidade": "milhões", "legenda": "de massas solares", "seed": 5}}})
three("s04", 11.0, 14.0, "buraco", 3, "Sagitário A*", "a luz não escapa dele", label="3D buraco negro + disco")
foto("s05", 13.4, 16.6, "gc_1.jpg", "zoom_out", 0.09, "Centro da galáxia", "", "NASA/JPL-Caltech/ESA/CXC/STScI")
three("s06", 16.0, 22.8, "orbitas", 4, "Estrelas jovens", "órbitas em elipses ao redor do gigante", label="3D órbitas estrelas S")
foto("s07", 22.2, 30.8, "chandra_0.jpg", "zoom_in", 0.12, "Gás interestelar", "brilhando em raios-X", "NASA/CXC/Caltech/M. Muno et al.", pos="50% 45%")
foto("s08", 30.2, 34.6, "meerkat_1.jpg", "pan_left", 0.10, "Campos magnéticos", "", "NASA, ESA, CSA, STScI, SARAO")
three("s09", 34.0, 38.6, "jato", 5, "Jatos de energia", "por anos-luz", label="3D jatos")
foto("s10", 38.0, 41.9, "alma_1.jpg", "zoom_in", 0.08, "Event Horizon Telescope", "", "ESO/C. Malin · CC BY 4.0")
foto("s11", 41.3, 45.0, "eht_0.jpg", "zoom_in", 0.10, "A sombra do horizonte de eventos", "Sagitário A*", EHT)
foto("s12", 44.4, 48.6, "vlt_1.jpg", "pan_right", 0.08, "Very Large Telescope", "", "ESO/Y. Beletsky · CC BY 4.0")
three("s13", 48.0, 50.9, "s2", 6, "Estrela S2", "trinta anos de observação", label="3D órbita S2")
foto("s14", 50.3, 53.0, "einst_0.jpg", "zoom_in", 0.06, "Albert Einstein", "relatividade geral", "Herman Mishkin · domínio público", pos="50% 22%")
foto("s15", 52.4, 57.6, "gc_0.jpg", "zoom_in", 0.10, "", "", "NASA/JPL-Caltech/S. Stolovy")
three("s16", 57.0, 62.3, "voo", 2, label="3D galáxia (CTA)")
foto("s17", 61.7, DUR, "mw_0.jpg", "zoom_out", 0.10, "", "", "ESO/Y. Beletsky · CC BY 4.0", fo=1.2)
cap("c1", 0.3, 3.7, "O centro da Via Láctea", "um monstro silencioso")
cap("c2", 52.8, 57.2, "Uma pergunta aberta", "o que alimenta o gigante?")
cap("c3", 57.5, 61.7, "Inscreva-se", "números que desafiam a imaginação")
cap("c4", 62.1, 65.3, "Mais segredos", "do que contamos")

fundo = sorted([i for i in items if i["track"] == "fundo"], key=lambda i: i["start"])
for a, b in zip(fundo, fundo[1:]):
    a["dur"] = round(max(a["dur"], b["start"] + 1.05 - a["start"]), 2)

edit = {
    "version": 1, "name": NAME, "estilo": "12-espaco-cosmos", "grupo": "ESTILOS NOVOS",
    "canvas": {"w": 1280, "h": 720, "fps": 30, "bg": "#000000"}, "duration": DUR, "template": "generic",
    "fonts": {"Outfit": "fonts/Outfit.ttf", "Cormorant": "fonts/CormorantGaramond.ttf"},
    "head": '<script src="https://cdn.jsdelivr.net/npm/three@0.150.1/build/three.min.js"></script>',
    "referencia": {"canal": "Astrum", "canal_url": "https://www.youtube.com/@astrumspace", "video": "https://youtu.be/T9HLYPn59S4",
                   "titulo": "Euclid Studied Our Galactic Centre. This Is What It Found.",
                   "nota": "Imagens reais NASA/ESA/ESO/EHT com pan/zoom lento + 3D Three.js, nome do objeto no canto, crédito, capítulos em serifa (History of the Universe)."},
    "audio": {"voice": {"src": "voz.wav", "volume": 1.0, "start": 0},
              "music": {"src": "musica.mp3", "volume": 0.14, "start": 0, "fade_out": 2.0, "duck": True}, "extra": []},
    "tracks": [{"id": "fundo", "name": "Cenas / mídia"}, {"id": "textos", "name": "Textos"}],
    "items": items,
}
json.dump(edit, open(os.path.join(O, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("itens", len(items))
