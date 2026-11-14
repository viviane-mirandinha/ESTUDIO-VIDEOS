import json
DUR = 67.6
# (start, end, img, motion)
S = [
 (0.0, 4.2, "g_01_nightmare.jpg", "zoom_in"),
 (4.0, 9.6, "g_14_seneca_bust.jpg", "pan_up"),
 (9.4, 13.8, "g_03_letters.jpg", "pan_left"),
 (13.6, 17.6, "g_04_goya.jpg", "zoom_in"),
 (17.4, 22.0, "g_05_triumph.jpg", "pan_right"),
 (21.8, 26.6, "g_06_monk.jpg", "zoom_out"),
 (26.4, 32.0, "g_07_wanderer.jpg", "pan_up"),
 (31.8, 37.2, "g_08_medusa.jpg", "pan_left"),
 (37.0, 44.6, "g_09_socrates.jpg", "zoom_in"),
 (44.4, 47.8, "g_10_moon.jpg", "zoom_out"),
 (47.6, 52.4, "g_11_isle.jpg", "pan_right"),
 (52.2, 61.8, "g_12_melencolia.jpg", "pan_up"),
 (61.6, DUR, "g_13_sunset.jpg", "zoom_in"),
]
C = "#ece4d4"; ACC = "#c9a96e"
# (start, end, text, x, y, size, font)
T = [
 (0.3, 3.9, "Quantos desastres você já viveu hoje,", 640, 330, 50, "Cormorant"),
 (2.5, 3.9, "só na sua cabeça?", 760, 395, 54, "CormorantI"),
 (4.6, 9.2, "SÊNECA", 640, 560, 92, "Cormorant"),
 (5.4, 9.2, "filósofo estoico  ·  4 a.C. – 65 d.C.", 640, 640, 32, "CormorantI"),
 (9.6, 13.4, "Cartas a Lucílio", 640, 600, 44, "CormorantI"),
 (13.8, 17.3, "“Sofremos mais na imaginação", 640, 320, 58, "CormorantI"),
 (14.6, 17.3, "do que na realidade.”", 700, 390, 58, "CormorantI"),
 (15.6, 17.3, "— Sêneca", 860, 460, 30, "Cormorant"),
 (22.9, 26.2, "um sofrimento que ainda não existe", 640, 600, 44, "CormorantI"),
 (27.0, 31.6, "o que depende de nós", 560, 300, 50, "Cormorant"),
 (28.8, 31.6, "o que não depende", 740, 370, 50, "CormorantI"),
 (37.8, 44.2, "PREMEDITATIO MALORUM", 640, 560, 56, "Cormorant"),
 (39.6, 44.2, "imaginar o pior — com calma — e se preparar", 640, 620, 30, "CormorantI"),
 (45.4, 47.5, "voltar ao presente", 640, 600, 48, "CormorantI"),
 (47.7, 52.2, "O medo vive no futuro.", 600, 320, 58, "Cormorant"),
 (50.0, 52.2, "A vida acontece agora.", 700, 395, 58, "CormorantI"),
 (57.3, 61.5, "Isso está acontecendo agora…", 600, 320, 52, "Cormorant"),
 (58.9, 61.5, "ou só na minha cabeça?", 720, 390, 56, "CormorantI"),
 (63.0, 67.4, "inscreva-se", 640, 600, 40, "CormorantI"),
]
items = []
for i, (s, e, src, mo) in enumerate(S):
    items.append({"id": f"img{i+1:02d}", "type": "image", "track": "fundo", "label": src[2:-4],
                  "start": s, "dur": round(e - s, 2), "in": "none" if i == 0 else "fade", "out": "fade",
                  "props": {"src": "img/" + src, "fill": True, "fit": "cover", "motion": mo, "motion_amount": 0.07}})
# dark gradient + vignette + static grain over every painting (Einzelganger look)
items.append({"id": "grade", "type": "html", "track": "visual", "label": "vinheta + grão",
              "start": 0, "dur": DUR, "in": "none", "out": "none",
              "props": {"x": 640, "y": 360, "w": 1280, "h": 720,
                        "html": "<div class='vg'></div><div class='gr'></div>",
                        "css": ".vg{position:absolute;inset:0;background:radial-gradient(ellipse at center,rgba(0,0,0,0) 35%,rgba(0,0,0,.78) 100%),linear-gradient(rgba(5,6,10,.25),rgba(5,6,10,.25))}"
                               ".gr{position:absolute;inset:0;opacity:.10;mix-blend-mode:overlay;background-image:url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>\")}"}})
for i, (s, e, txt, x, y, size, font) in enumerate(T):
    items.append({"id": f"t{i+1:02d}", "type": "text", "track": "textos", "label": txt[:24],
                  "start": s, "dur": round(e - s, 2), "in": "fade", "out": "fade",
                  "props": {"text": txt, "x": x, "y": y, "w": 1100, "size": size, "color": ACC if txt.isupper() else C,
                            "font": font, "weight": 500, "align": "center", "shadow": True, "upper": False,
                            **({"bg": "rgba(0,0,0,.55)", "pad": 12, "radius": 4} if 13 < s < 17.5 else {})}})
edit = {"version": 1, "name": "08 - Psicologia Filosofia Sombria - Você sofre mais na imaginação",
        "canvas": {"w": 1280, "h": 720, "fps": 30, "bg": "#07080b"}, "duration": DUR, "template": "generic",
        "fonts": {"Cormorant": "fonts/Cormorant.ttf", "CormorantI": "fonts/CormorantItalic.ttf"},
        "audio": {"voice": {"src": "voz.mp3", "volume": 1.0, "start": 0}},
        "tracks": [{"id": "fundo", "name": "Pinturas"}, {"id": "visual", "name": "Vinheta/grão"}, {"id": "textos", "name": "Textos"}],
        "items": items, "build_script": "tools/make_edit.py",
        "creditos": "img/creditos.json (Wikimedia Commons, domínio público)"}
json.dump(edit, open("edit.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(items), "items")
