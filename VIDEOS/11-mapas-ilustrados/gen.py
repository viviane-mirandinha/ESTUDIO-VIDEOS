"""gera edit.json + template.html do video 11 (mapas ilustrados / whiteboard)."""
import json, shutil
from pathlib import Path
H = Path(__file__).parent
M = json.load(open(H / "map.json"))
shutil.copy2(r"voz.mp3", H / "voz.mp3")
DUR = 74.0
RED, TEAL, INK, BLUE = "#d93a3a", "#1f9e8f", "#2a2a2a", "#2f6fb5"

items = []
def note(id, s, e, text, x, y, size=40, color=INK, kind="note", label=None):
    items.append({"id": id, "type": "text", "track": "textos", "by": "template", "label": label or text,
                  "start": s, "dur": round(e - s, 2),
                  "props": {"text": text, "x": x, "y": y, "size": size, "color": color, "kind": kind}})
def cap(id, s, e, text):
    items.append({"id": id, "type": "caption", "track": "legenda", "by": "template", "label": text,
                  "start": s, "dur": round(e - s, 2), "props": {"text": text}})
def scene(id, s, e, label, **p):
    items.append({"id": id, "type": "scene", "track": "fundo", "by": "template", "label": label,
                  "start": s, "dur": round(e - s, 2), "props": p})

# cenas do mapa (tempos lidos pelo template)
scene("s_map", 0.2, DUR, "Mapa desenhado")
scene("s_fusos", 1.0, 6.4, "11 fusos")
scene("s_fill", 6.9, DUR, "Mapa colorido")
scene("s_people", 15.3, 22.2, "Pessoas espalhadas")
scene("s_cam_w", 23.9, 33.0, "Zoom no oeste", scale=1.75, cx=470, cy=440)
scene("s_dense", 24.9, 33.0, "Oeste cheio")
scene("s_ural", 28.2, 33.0, "Montes Urais")
scene("s_pins", 30.6, 33.0, "Moscou / S. Petersburgo")
scene("s_cam_s", 33.2, 44.9, "Zoom Sibéria", scale=1.45, cx=860, cy=400)
scene("s_sib", 33.6, 44.9, "Sibéria + neve")
scene("s_rail", 48.3, 63.6, "Transiberiana")
scene("s_expand", 55.6, 63.6, "Expansão p/ leste")
scene("s_end", 67.9, DUR, "CTA final")

# notas (mind-map manuscrito)
note("n1", 0.0, 6.5, "RÚSSIA", 40, 22, 78, RED, "title")
note("n2", 1.3, 6.5, "11 fusos horários", 70, 120, 44, TEAL, "branch")
note("n3", 3.1, 6.5, "...mas pouca gente?", 70, 178, 40, INK, "branch")
note("n4", 6.7, 13.1, "Maior país do mundo", 40, 22, 66, RED, "title")
note("n5", 9.5, 13.1, "≈ 17 milhões de km²", 70, 112, 46, INK, "branch")
note("n6", 13.2, 22.2, "População", 40, 22, 66, RED, "title")
note("n7", 15.2, 22.2, "≈ 146 milhões de pessoas", 70, 112, 44, INK, "branch")
note("n8", 18.8, 22.2, "território: GIGANTE", 70, 168, 44, TEAL, "branch")
note("n9", 19.8, 22.2, "população: pequena", 70, 220, 30, TEAL, "branch")
note("n10", 22.4, 24.6, "O MOTIVO?", 470, 270, 110, RED, "bubble")
note("n11", 24.0, 33.0, "A maioria vive no OESTE", 40, 22, 60, RED, "title")
note("n12", 28.3, 33.0, "a oeste dos Montes Urais", 70, 104, 40, TEAL, "branch")
note("n13", 33.4, 44.9, "Sibéria", 40, 22, 70, BLUE, "title")
note("n14", 35.9, 44.9, "frio extremo", 70, 112, 42, INK, "branch")
note("n15", 38.1, 44.9, "PERMAFROST = solo congelado", 70, 172, 36, INK, "card")
note("n16", 41.3, 44.9, "construir e viver: difícil e caro $$$", 70, 250, 34, RED, "branch")
note("n17", 45.0, 55.4, "Ferrovia Transiberiana", 40, 22, 64, RED, "title")
note("n18", 50.4, 55.4, "Moscou → Vladivostok", 70, 112, 42, TEAL, "branch")
note("n19", 53.3, 55.4, "+ 9.000 km", 70, 168, 52, INK, "branch")
note("n20", 55.6, 63.6, "Expansão para o leste", 40, 22, 64, RED, "title")
note("n21", 58.1, 63.6, "a partir do séc. XVI", 70, 104, 40, INK, "card")
note("n22", 60.6, 63.6, "em busca de peles e recursos", 70, 178, 38, TEAL, "branch")
note("n23", 63.8, 67.8, "País gigante", 470, 230, 96, RED, "center")
note("n24", 65.3, 67.8, "muito espaço", 330, 400, 52, TEAL, "center")
note("n25", 66.6, 67.8, "pouca gente", 860, 400, 52, TEAL, "center")
note("n26", 68.2, DUR, "INSCREVA-SE", 640, 300, 72, "#ffffff", "button")
note("n27", 69.8, DUR, "Qual país no próximo mapa?", 640, 450, 56, INK, "center")

# legendas grandes (estilo da referência: branca, contorno escuro, sombra teal)
cap("c1", 9.6, 12.9, "17 MILHÕES DE KM²")
cap("c2", 15.2, 18.6, "146 MILHÕES DE HABITANTES")
cap("c3", 38.2, 41.0, "SOLO CONGELADO")
cap("c4", 53.4, 55.4, "MAIS DE 9 MIL KM")
cap("c5", 63.8, 67.6, "MUITO ESPAÇO, POUCA GENTE")

edit = {
    "version": 1, "name": "11 - Mapas Ilustrados - Por que a Rússia é tão grande e tão vazia",
    "canvas": {"w": 1280, "h": 720, "fps": 30, "bg": "#fdfdfa"}, "duration": DUR, "template": "local",
    "fonts": {"Caveat": "fonts/Caveat.ttf", "PatrickHand": "fonts/PatrickHand.ttf"},
    "audio": {"voice": {"src": "voz.mp3", "volume": 1.0, "start": 0}},
    "tracks": [{"id": "fundo", "name": "Cenas do mapa"}, {"id": "textos", "name": "Notas manuscritas"},
               {"id": "legenda", "name": "Legenda grande"}],
    "items": items,
    "build_script": "gen.py (gera template.html) -> EDITOR VIDEOS/build_from_edit.py",
}
json.dump(edit, open(H / "edit.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

paths = "\n".join(f'<path class="land" d="{d}"/>' for d in M["paths"])
tpl = (H / "tpl_src.html").read_text(encoding="utf-8")
tpl = tpl.replace("%%LAND%%", paths).replace("%%MAP%%", json.dumps(M))
(H / "template.html").write_text(tpl, encoding="utf-8")
print("ok", len(items))
