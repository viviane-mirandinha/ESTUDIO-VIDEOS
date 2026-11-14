# gera edit.json do vídeo 02 (true crime arquivo)
import json, os
D = 60.6
R43 = (600, 450); R169 = (680, 383)
FY = 340
shots = [  # start, end, img, frame, motion, nome, sub
 (0.0, 3.4, "wentworth_0", R43, "zoom_in", "WHITECHAPEL, 1888", "Londres"),
 (3.4, 6.3, "ipn_1", R43, "pan_down", "SETEMBRO DE 1888", "The Illustrated Police News"),
 (6.3, 8.3, "ipn_2", R43, "zoom_in", "PERFIL PSICOLÓGICO", ""),
 (8.3, 11.5, "buff_0", R43, "zoom_out", "JACK, O ESTRIPADOR", "Punch, 22 de setembro de 1888"),
 (11.5, 12.7, "dudley_0", R169, "pan_left", "", ""),
 (14.6, 17.2, "warren_x", R43, "pan_up", "SIR CHARLES WARREN", "chefe da Polícia Metropolitana"),
 (24.4, 27.4, "herschel_1", R169, "pan_right", "IMPRESSÃO DIGITAL", "a Scotland Yard só adotou em 1901"),
 (27.4, 31.4, "phillips_0", R43, "zoom_in", "DR. GEORGE BAGSTER PHILLIPS", "cirurgião da polícia"),
 (33.7, 36.0, "fromhell_0", R43, "zoom_in", "\"FROM HELL\"", "outubro de 1888"),
 (36.0, 39.1, "lusk_0", R43, "zoom_in", "GEORGE LUSK", "Comitê de Vigilância de Whitechapel"),
 (39.1, 43.2, "swanson_0", R43, "zoom_out", "DONALD SWANSON", "inspetor-chefe"),
 (43.2, 45.8, "wentworth_2", R43, "pan_right", "AARON KOSMINSKI", "imigrante polonês · sem foto conhecida"),
 (45.8, 47.4, "colney_0", R169, "zoom_in", "COLNEY HATCH", "internado em 1891"),
 (47.4, 50.5, "ipn_1", R43, "pan_up", "SEM DNA", "só restou a suspeita"),
 (50.5, 55.3, "nemesis_x", R43, "zoom_in", "", ""),
 (55.3, 58.4, "dudley_0", R169, "pan_right", "INSCREVA-SE", "mais mistérios não resolvidos"),
]
caps = [(12.7, 14.6, "PRIMEIRO", "A JURISDIÇÃO"), (22.5, 24.4, "SEGUNDO", "A CIÊNCIA"),
        (31.4, 33.7, "TERCEIRO", "A CARTA \"FROM HELL\""), (58.4, D, "", "O ARQUIVO CONTINUA ABERTO")]
items, css = [], []
for i, (s, e, img, (w, h), mo, nome, sub) in enumerate(shots):
    items.append({"id": f"s{i}", "type": "image", "track": "fundo", "label": f"{img} · {nome or 'foto'}", "start": s, "dur": round(e - s, 2),
                  "in": "none", "out": "none",
                  "props": {"src": f"img/{img}.jpg", "fit": "cover", "x": 640, "y": FY, "w": w, "h": h, "motion": mo,
                            "motion_amount": 0.1, "opacity": 1}})
    pos = {"warren_x": "50% 8%", "lusk_0": "50% 15%", "swanson_0": "50% 30%"}.get(img)
    if pos: css.append(f"#s{i}{{object-position:{pos}}}")
    css.append(f"#s{i}{{filter:grayscale(.9) sepia(.12) contrast(1.15) brightness(.9)}}")
    items.append({"id": f"m{i}", "type": "html", "track": "moldura", "label": "moldura", "start": s, "dur": round(e - s, 2),
                  "in": "none", "out": "none",
                  "props": {"html": "<div class='fr'></div>", "css": "", "x": 640, "y": FY, "w": w, "h": h}})
    if nome:
        items.append({"id": f"n{i}", "type": "text", "track": "textos", "label": f"Nome: {nome}", "start": round(s + .25, 2),
                      "dur": round(e - s - .35, 2), "in": "fade", "out": "none",
                      "props": {"text": nome, "x": 640, "y": FY + h / 2 - 70, "w": 1100, "size": 54, "color": "#ffffff",
                                "font": "Oswald", "weight": 700, "align": "center", "shadow": True, "upper": True}})
    if sub:
        items.append({"id": f"d{i}", "type": "text", "track": "textos", "label": f"Data/sub: {sub}", "start": round(s + .45, 2),
                      "dur": round(e - s - .55, 2), "in": "fade", "out": "none",
                      "props": {"text": sub, "x": 640, "y": FY + h / 2 + 34, "w": 1100, "size": 28, "color": "#d8d8d8",
                                "font": "Oswald", "weight": 700, "align": "center", "shadow": False}})
for k, (s, e, num, tx) in enumerate(caps):
    items.append({"id": f"cap{k}", "type": "scene", "track": "capitulos", "label": f"Capítulo: {num} {tx}", "start": s, "dur": round(e - s, 2),
                  "props": {"fill": True, "scene": "capitulo-vermelho", "params": {"numero": num, "texto": tx, "cor": "#b3121a", "fonte": "Anton"}}})
items.append({"id": "mapa", "type": "scene", "track": "capitulos", "label": "Mapa Londres 1888", "start": 17.2, "dur": 5.3,
              "props": {"fill": True, "scene": "mapa-whitechapel", "params": {"titulo": "LONDRES, 1888", "city": "CITY OF LONDON",
                        "whitechapel": "WHITECHAPEL", "rio": "RIO TÂMISA", "nota": "Mitre Square: jurisdição da City"}}})
grain = ("<svg width='1280' height='720' style='opacity:.22;mix-blend-mode:screen'><filter id='n'>"
         "<feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='2' stitchTiles='stitch'/><feColorMatrix type='saturate' values='0'/></filter>"
         "<rect width='100%' height='100%' filter='url(#n)' opacity='.5'/></svg>")
items.append({"id": "vinheta", "type": "html", "track": "efeitos", "label": "Vinheta", "start": 0, "dur": D, "in": "none", "out": "none",
              "props": {"html": "<div class='vig'></div>", "css": ".vig{width:1280px;height:720px;background:radial-gradient(ellipse at center,rgba(0,0,0,0) 40%,rgba(0,0,0,.75) 100%)}",
                        "x": 640, "y": 360, "w": 1280, "h": 720}})
items.append({"id": "grao", "type": "html", "track": "efeitos", "label": "Grão de filme", "start": 0, "dur": D, "in": "none", "out": "none",
              "props": {"html": grain, "css": "", "x": 640, "y": 360, "w": 1280, "h": 720}})
edit = {"version": 1, "name": "02 - TRUE CRIME ARQUIVO - O caso Jack, o Estripador", "estilo": "True crime arquivo (Dieck Docs / Ossos Perdidos)",
        "canvas": {"w": 1280, "h": 720, "fps": 30, "bg": "#000000"}, "duration": D, "template": "generic",
        "fonts": {"Oswald": "fonts/Oswald-Bold.ttf", "Anton": "fonts/Anton-Regular.ttf"},
        "head": "<style>" + "\n".join(css) + "\n.fr{width:100%;height:100%;box-sizing:border-box;border:1px solid #333;box-shadow:0 0 40px rgba(0,0,0,.9)}</style>",
        "audio": {"voice": {"src": "voz.mp3", "volume": 1.0, "start": 0},
                  "music": {"src": "musica.mp3", "volume": 0.10, "start": 0, "fade_out": 2.0, "duck": True}},
        "tracks": [{"id": "fundo", "name": "Fotos de arquivo (moldura pequena)"}, {"id": "moldura", "name": "Borda da moldura"},
                   {"id": "textos", "name": "Nomes / datas"}, {"id": "capitulos", "name": "Capítulos vermelhos / mapa"},
                   {"id": "efeitos", "name": "Vinheta / grão"}],
        "items": items,
        "referencia": {"canal": "Dieck Docs / Ossos Perdidos", "canal_url": "", "video": "https://youtu.be/s62OAyw77XQ",
                       "titulo": "", "nota": "estilo 02 true crime arquivo; ver ESTILOS-NOVOS/02-true-crime-arquivo/REFERENCIA.txt"}}
json.dump(edit, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(items))
