import json
D = 79.0
tpl = open('template_src.html', encoding='utf-8').read().replace('/*__MAPA__*/', open('mapa_path.js', encoding='utf-8').read())
open('template.html', 'w', encoding='utf-8').write(tpl)
B = {"UTAH": [-1.18, 49.42], "OMAHA": [-0.87, 49.37], "GOLD": [-0.57, 49.34], "JUNO": [-0.43, 49.335], "SWORD": [-0.30, 49.295]}
def praia(n, at, cor='k', dy=-18): return {"p": B[n], "t": n, "at": at, "cor": cor, "dy": dy}
def seta(n, t, dur=0.8):
    b = B[n]; return {"de": [b[0] + 0.02, b[1] + 0.13], "para": [b[0], b[1] + 0.012], "t": t, "dur": dur}
nomes = [{"t": "CANAL DA MANCHA", "p": [-0.9, 49.68], "size": 24, "cor": "#3e4d52", "it": 1},
         {"t": "NORMANDIA", "p": [-0.75, 49.12], "size": 30, "cor": "#2a3020"},
         {"t": "COTENTIN", "p": [-1.55, 49.5], "size": 20, "cor": "#2a3020"}]
def S(id, label, a, b, props):
    return {"id": id, "type": "scene", "track": "visual", "label": label, "by": "template", "start": a, "dur": round(b - a, 2), "props": props}
ORIG = "FRENTE OCIDENTAL · NORMANDIA"
items = [
 S("s00", "Título", 0, 9.0, {"cena": "titulo", "kicker": "BOLETIM DE GUERRA", "linha": "06 JUN 1944 — NORMANDIA, FRANÇA", "titulo": "DIA D: AS PRIMEIRAS 24 HORAS", "t_titulo": 3.4, "rodape": "RELATO EM DESPACHOS · HORA A HORA", "t_rodape": 6.3, "carimbo": "URGENTE", "t_carimbo": 7.7}),
 S("d1", "Despacho 1", 9.0, 12.6, {"cena": "despacho", "origem": ORIG, "numero": "DESPACHO Nº 1", "texto": "PLANADORES BRITÂNICOS NA PONTE DO CANAL DE CAEN.", "hora": "00h16", "t_hora": 3.05}),
 S("m1", "Mapa — ponte do canal de Caen", 12.6, 19.5, {"cena": "mapa", "centro0": [-0.6, 49.33], "zoom0": 1.2, "centro": [-0.31, 49.23], "zoom": 2.1, "nomes": nomes,
   "setas": [{"de": [-0.02, 49.45], "para": [-0.265, 49.25], "t": 0.5, "dur": 1.0, "curva": -1, "w": 7}],
   "marcas": [{"p": [-0.274, 49.242], "t": "PONTE DO CANAL DE CAEN", "at": 1.0, "ancora": "start", "dx": 14, "dy": 6}, {"p": [-0.37, 49.183], "t": "CAEN", "at": 2.4, "cor": "r"}],
   "foto": {"src": "img/pegasus.jpg", "x": 70, "y": 70, "w": 400, "h": 280, "rot": -3, "at": 2.6, "legenda": "Ponte do canal · junho 1944"},
   "carimbo": "TOMADA", "t_carimbo": 5.7, "car_x": 760, "car_y": 470}),
 S("m2", "Mapa — paraquedistas", 19.5, 24.9, {"cena": "mapa", "centro0": [-0.7, 49.32], "zoom0": 1.3, "centro": [-1.25, 49.37], "zoom": 1.9, "nomes": nomes,
   "paras": [{"c": [-1.3, 49.37], "r": [0.13, 0.07], "n": 34, "t": 1.2, "spread": 2.6, "seed": 11}],
   "marcas": [praia("UTAH", 0.2, 'k', -22)],
   "foto": {"src": "img/eisenhower.jpg", "x": 830, "y": 80, "w": 380, "h": 280, "rot": 3, "at": 1.6, "legenda": "Eisenhower e paraquedistas · 5 jun"}}),
 S("d2", "Despacho 2", 24.9, 28.4, {"cena": "despacho", "origem": ORIG, "numero": "DESPACHO Nº 2", "texto": "FROTA ALIADA DIANTE DA COSTA. NAVIOS ABREM FOGO.", "hora": "AMANHECER", "t_hora": 2.75}),
 S("f1", "Foto — frota", 28.4, 32.2, {"cena": "foto", "src": "img/navios.jpg", "legenda": "Normandia · 6 de junho de 1944", "rot": -1.5, "destaque": "≈ 7.000 EMBARCAÇÕES", "t_dest": 0.5, "dest_x": 640, "dest_y": 440, "dest_size": 46}),
 S("m3", "Mapa — hora H", 32.2, 39.8, {"cena": "mapa", "centro0": [-0.75, 49.36], "zoom0": 1.02, "centro": [-0.95, 49.38], "zoom": 1.35, "nomes": nomes,
   "navios": [{"de": [-1.25, 49.62], "ate": [-0.2, 49.5], "n": 46, "t": 0.0, "fogo": 0.2, "seed": 21}],
   "setas": [seta("UTAH", 6.0), seta("OMAHA", 6.4)],
   "marcas": [praia("UTAH", 6.3), praia("OMAHA", 6.7)],
   "carimbo": "06h30 · HORA H", "t_carimbo": 2.4, "car_x": 90, "car_y": 500}),
 S("f2", "Foto — Omaha", 39.8, 43.5, {"cena": "foto", "src": "img/omaha.jpg", "legenda": "Praia de Omaha · 6 de junho de 1944", "rot": 1.8, "carimbo": "RESISTÊNCIA MAIS DURA", "t_carimbo": 2.0, "car_x": 110, "car_y": 470}),
 S("d3", "Despacho 3", 43.5, 47.4, {"cena": "despacho", "origem": ORIG, "numero": "DESPACHO Nº 3", "texto": "BRITÂNICOS E CANADENSES EM GOLD, JUNO E SWORD.", "hora": "07h25", "t_hora": 2.75}),
 S("m4", "Mapa — Gold, Juno, Sword", 47.4, 51.0, {"cena": "mapa", "centro0": [-0.8, 49.36], "zoom0": 1.2, "centro": [-0.6, 49.34], "zoom": 1.5, "nomes": nomes,
   "setas": [seta("GOLD", 1.5, 0.6), seta("JUNO", 1.8, 0.6), seta("SWORD", 2.5, 0.6)],
   "marcas": [praia("UTAH", 0, 'g'), praia("OMAHA", 0, 'g'), praia("GOLD", 1.9), praia("JUNO", 2.2), praia("SWORD", 2.9)]}),
 S("tg", "Telegrama — Rommel", 51.0, 57.5, {"cena": "telegrama", "titulo": "TELEGRAMA", "sub": "06 JUN 1944 · DEFESA ALEMÃ",
   "tiras": [{"t": "COMANDANTE ALEMÃO DA COSTA: ERWIN ROMMEL", "at": 0.3, "cps": 30}, {"t": "NÃO ESTÁ NA FRENTE", "at": 2.6}, {"t": "FOI À ALEMANHA · ANIVERSÁRIO DA ESPOSA", "at": 3.6, "cps": 30}],
   "carimbo": "AUSENTE", "t_carimbo": 3.0}),
 S("d4", "Despacho 4", 57.5, 61.2, {"cena": "despacho", "origem": ORIG, "numero": "DESPACHO Nº 4", "texto": "BALANÇO DAS PRIMEIRAS 24 HORAS.", "hora": "FIM DO DIA", "t_hora": 2.3}),
 S("f3", "Foto — Sword", 61.2, 65.3, {"cena": "foto", "src": "img/sword.jpg", "legenda": "Praia de Sword · 6 jun 1944", "rot": -2, "w": 520, "h": 470, "dx": -170, "destaque": "156.000\nSOLDADOS\nNA FRANÇA", "t_dest": 0.6, "dest_x": 760, "dest_y": 170, "dest_size": 48, "dest_min": 280}),
 S("f4", "Foto — Juno", 65.3, 68.3, {"cena": "foto", "src": "img/juno.jpg", "legenda": "Praia de Juno · 6 de junho de 1944", "rot": 1.5, "destaque": "≈ 10.000 BAIXAS ALIADAS", "t_dest": 0.4, "dest_x": 520, "dest_y": 440, "dest_size": 44}),
 S("m5", "Mapa — Caen", 68.3, 72.1, {"cena": "mapa", "centro0": [-0.6, 49.3], "zoom0": 1.3, "centro": [-0.45, 49.25], "zoom": 1.75, "nomes": nomes,
   "marcas": [praia("GOLD", 0, 'g'), praia("JUNO", 0, 'g'), praia("SWORD", 0, 'g'), {"p": [-0.37, 49.183], "t": "CAEN · AINDA ALEMÃ", "at": 0.3, "cor": "r", "anel": 1, "dy": -34}],
   "carimbo": "NÃO TOMADA", "t_carimbo": 1.8, "car_x": 820, "car_y": 480}),
 S("fim", "Encerramento", 72.1, D, {"cena": "fim", "kicker": "BOLETIM DE GUERRA · ENCERRAMENTO", "frase": "A PORTA DA EUROPA OCUPADA ESTAVA ABERTA.", "fecho": "FIM DA TRANSMISSÃO", "t_fecho": 3.1, "carimbo": "06 JUN 1944", "t_carimbo": 4.6}),
 {"id": "tag", "type": "text", "track": "textos", "label": "Etiqueta fixa", "by": "template", "start": 9.0, "dur": 63.1, "props": {"text": "NORMANDIA · 06 JUN 1944"}},
 {"id": "regua", "type": "scene", "track": "textos", "label": "Régua 24 h", "by": "template", "start": 9.0, "dur": 63.1, "props": {"marcas": [
   {"t": 11.9, "h": 0.27, "rotulo": "00h16"}, {"t": 27.5, "h": 5.9, "rotulo": "AMANHECER"}, {"t": 34.4, "h": 6.5, "rotulo": "06h30 · HORA H"},
   {"t": 46.0, "h": 7.42, "rotulo": "07h25"}, {"t": 59.6, "h": 24, "rotulo": "FIM DO DIA"}]}},
]
edit = {"version": 1, "name": "40 - 24-10-2026 - DESPACHO DE GUERRA - Dia D as primeiras 24 horas", "estilo": "40-despacho-de-guerra", "grupo": "ESTILOS NOVOS",
 "canvas": {"w": 1280, "h": 720, "fps": 30, "bg": "#2c3026"}, "duration": D, "template": "local",
 "fonts": {"Courier Prime": "fonts/CourierPrime-Bold.ttf", "Oswald": "fonts/Oswald-Bold.ttf", "Bebas Neue": "fonts/BebasNeue-Regular.ttf"},
 "referencia": {"canal": "Kings and Generals", "canal_url": "https://www.youtube.com/channel/UCMmaBzfCCwZ2KqaBJjkj0fw", "video": "https://youtu.be/hHqJ6pgdE-c",
   "titulo": "Six-Day War (1967) - Third Arab–Israeli War DOCUMENTARY",
   "canais": ["Kings and Generals", "Real Time History"], "videos": ["https://youtu.be/hHqJ6pgdE-c", "https://youtu.be/h7wiiKSYrv8"],
   "nota": "guerra contada por dias/horas: mapa de front com setas e ícones, fotos de arquivo P&B pousadas sobre papel com vinheta, etiqueta de lugar+data no canto, cartões de citação em papel, dissolves; aqui virou despacho datilografado com carimbos de hora"},
 "audio": {"voice": {"src": "voz.wav", "volume": 1.0, "start": 0}, "music": {"src": "musica.wav", "volume": 0.10, "start": 0, "fade_out": 2.5, "duck": True},
   "extra": [{"id": f"w{i}", "src": "sfx/whoosh.wav", "start": t, "volume": 0.16, "label": "whoosh"} for i, t in enumerate([8.85, 24.75, 43.35, 57.35, 71.95])]},
 "tracks": [{"id": "visual", "name": "Cenas"}, {"id": "textos", "name": "Textos fixos"}],
 "items": items}
json.dump(edit, open('edit.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print("ok", len(items))
