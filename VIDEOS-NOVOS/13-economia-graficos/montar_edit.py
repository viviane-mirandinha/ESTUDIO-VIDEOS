import json, os
O = os.path.dirname(os.path.abspath(__file__))
NAME = "13 - ECONOMIA GRAFICOS - Por que o carro novo ficou tão caro"
DUR = 79.5
items = []
def add(id, typ, track, s, e, props, label="", i="fade", o="fade"):
    items.append({"id": id, "type": typ, "track": track, "label": label or id, "start": s, "dur": round(e - s, 2), "in": i, "out": o, "props": props})
def vid(id, s, e, src, op=0.7, mo="zoom_in", label=""):
    add(id, "video", "fundo", s, e, {"src": "clips/" + src, "fill": True, "fit": "cover", "volume": 0, "opacity": op, "motion": mo, "motion_amount": 0.06}, label or "B-roll " + src)
def img(id, s, e, src, op=0.7, mo="zoom_in", label=""):
    add(id, "image", "fundo", s, e, {"src": "img/" + src, "fill": True, "fit": "cover", "opacity": op, "motion": mo, "motion_amount": 0.08}, label or "Foto " + src)
def scene(id, s, e, name, params, label, track="visual"):
    add(id, "scene", track, s, e, {"scene": name, "params": params}, label, "none", "none")
def txt(id, s, e, text, y, size=60, hl=None, hl_color="#efe08f", x=640, color="#ffffff", bg="rgba(0,0,0,.6)", font="Inter", w=1100):
    add(id, "text", "textos", s, e, {"text": text, "x": x, "y": y, "w": w, "size": size, "color": color, "font": font, "weight": 800, "align": "center",
        "bg": bg, "pad": 14, "radius": 6, "shadow": True, "highlight": hl or [], "hl_color": hl_color}, "Texto: " + text, "slide_up", "fade")
def foto(id, s, e, src, leg, x, y, w, h, rot, t_in=0):
    scene(id, s, e, "eco_foto", {"src": "img/" + src, "legenda": leg, "x": x, "y": y, "w": w, "h": h, "rot": rot, "t_in": t_in or s}, "Foto-cartão: " + leg)
def cap(id, s, e, c, t, itens="", tempos="", x=300, y=230):
    scene(id, s, e, "eco_capitulo", {"cap": c, "texto": t, "itens": itens, "tempos": tempos, "escuro": 0.45, "x": x, "y": y}, "Capítulo: " + c, "textos")

# ---- fundo (b-roll escurecido / fotos)
vid("f01", 0.0, 9.3, "dash1_720.mp4", 0.7)
img("f02", 9.0, 15.0, "real1.jpg", 0.75)
vid("f03", 14.7, 18.9, "traf1_720.mp4", 0.7)
vid("f04", 18.6, 22.3, "fab0_720.mp4", 0.5, "none")
img("f05", 22.0, 27.6, "patio.jpg", 0.7)
img("f06", 27.3, 30.7, "real0.jpg", 0.5, "pan_left")
vid("f07", 30.3, 34.4, "money0_720.mp4", 0.7, "none")
img("f08", 34.1, 37.6, "parts0.jpg", 0.55)
img("f09", 37.3, 42.2, "escap.jpg", 0.75)
img("f10", 41.8, 46.3, "crash1.jpg", 0.7, "pan_left")
img("f11", 46.0, 50.6, "loja.jpg", 0.7)
vid("f12", 50.3, 54.6, "dash0_720.mp4", 0.7)
img("f13", 54.2, 59.3, "touch2.jpg", 0.75)
vid("f14", 58.9, 63.2, "show_720.mp4", 0.8, "none")
vid("f15", 62.9, 68.0, "night1_720.mp4", 0.7)
vid("f16", 67.8, 71.9, "dealer0_720.mp4", 0.85, "none")
vid("f17", 71.6, DUR, "night0_720.mp4", 0.6)

# ---- gráficos / cartões
txt("t01", 0.15, 3.8, "2019", 330, size=130, x=300, color="#efe08f", bg="", font="Barlow Condensed", w=400)
foto("p01", 0.3, 3.8, "hatch2.jpg", "Hatch compacto", 820, 330, 540, 330, -3)
scene("g01", 3.6, 9.2, "eco_barras", {"titulo": "Preço de um hatch compacto", "labels": ["2019", "Hoje"], "valores": [55, 90],
      "textos": ["R$ 55 mil", "+ de R$ 90 mil"], "tempos": [4.3, 8.3], "destaque": 1}, "Barras: preço do hatch")
scene("g02", 9.0, 14.95, "eco_tabela", {"titulo": "Quanto subiu", "colunas": ["", "Alta"], "linhas": [["Salário mínimo", "cerca de 50%"], ["Carro", "mais de 60%"]],
      "tempos": [10.9, 13.9], "destaque": 1, "t_destaque": 14.25}, "Tabela: salário x carro")
txt("t02", 14.85, 15.9, "Por quê?", 360, size=110, color="#efe08f", bg="", font="Barlow Condensed")
cap("c1", 15.8, 18.8, "Primeiro", "A cadeia quebrou na pandemia.")
foto("p02", 18.75, 22.3, "chip2.jpg", "Faltou chip", 270, 330, 340, 240, -5, 19.2)
foto("p03", 18.75, 22.3, "linha.jpg", "Parou a linha", 650, 370, 340, 240, 3, 19.85)
foto("p04", 18.75, 22.3, "empty0.jpg", "Estoque zerou", 1020, 320, 340, 240, -2, 20.85)
txt("t03", 22.3, 27.5, "As montadoras", 170, size=64, bg="", font="Barlow Condensed")
txt("t04", 24.0, 27.5, "▲ MAIS LUCRO", 310, size=56, hl=["▲"], hl_color="#3ddc84")
txt("t05", 25.5, 27.5, "▼ MENOS CARROS", 420, size=56, hl=["▼"], hl_color="#ff5a4f")
txt("t06", 26.5, 27.5, "▲ MAIS CAROS", 530, size=56, hl=["▲"], hl_color="#3ddc84")
cap("c2", 27.3, 30.5, "Segundo", "O real desvalorizou.")
scene("g03", 30.3, 34.3, "eco_linha", {"titulo": "Dólar em reais", "xlabels": ["antes", "depois"], "ymin": 3, "ymax": 6, "valores": [4, 5.5],
      "rotulos": ["R$ 4,00", "R$ 5,50"], "tempos": [32.4, 33.3]}, "Linha: dólar 4 → 5,50")
foto("p05", 34.15, 37.5, "parts2.jpg", "Peças importadas", 640, 300, 520, 320, -3)
txt("t07", 35.6, 37.4, "▲ ENCARECERAM NA HORA", 640, size=52, hl=["▲"], hl_color="#ff5a4f")
cap("c3", 37.3, 46.0, "Terceiro", "A lei mudou.", "Novas regras de emissões|Controle de estabilidade obrigatório|Produção mais cara", "39.5|41.95|44.1", x=70, y=140)
txt("t08", 46.2, 50.3, "Tecnologia custa caro", 280, size=64, hl=["caro"])
txt("t09", 48.2, 50.3, "e o consumidor pagou a conta", 390, size=56, hl=["pagou a conta"])
cap("c4", 50.3, 59.0, "Quarto", "O gosto mudou. Ninguém quer mais carro “pelado”.", "Central multimídia|Câmera de ré|Teto solar", "54.36|55.76|56.74", x=70, y=110)
scene("g04", 59.0, 62.95, "eco_manchete", {"veiculo": "GAZETA DO MERCADO", "secao": "AUTOMÓVEIS", "titulo": "O carro de entrada virou carro de luxo disfarçado",
      "destaque": "carro de luxo disfarçado", "t_destaque": 61.0}, "Manchete: luxo disfarçado")
txt("t10", 63.0, 64.2, "Resultado", 360, size=96, color="#efe08f", bg="", font="Barlow Condensed")
scene("g05", 64.1, 67.9, "contador", {"numero": 72, "sufixo": "", "legenda": "meses de parcela: a nova normalidade", "cor": "#efe08f", "fundo": "rgba(6,9,12,.72)"}, "Número: 72 meses")
txt("t11", 68.0, 71.6, "Acha que vai baixar?", 520, size=60)
txt("t12", 69.7, 71.6, "A indústria agradece.", 620, size=60, hl=["agradece."])
cap("c5", 71.7, 79.3, "Inscreva-se", "para ver o gráfico da depreciação real.", "Próximo vídeo: quais modelos ainda valem a pena", "75.1")

edit = {
    "version": 1, "name": NAME, "estilo": "13-economia-graficos", "grupo": "ESTILOS NOVOS",
    "canvas": {"w": 1280, "h": 720, "fps": 30, "bg": "#000000"}, "duration": DUR, "template": "generic",
    "fonts": {"Inter": "fonts/Inter.ttf", "Barlow Condensed": "fonts/BarlowCondensed-Bold.ttf"},
    "referencia": {"canal": "Economics Explained", "canal_url": "https://www.youtube.com/@EconomicsExplained", "video": "https://youtu.be/2a0veEb3znU",
                   "titulo": "How Old Money Kills Economies",
                   "nota": "B-roll escurecido + tabelas/barras/linha com título amarelo-claro, cartões de capítulo em papel rasgado com fita amarela, fotos em cartão caindo, manchete com marca-texto (How Money Works)."},
    "audio": {"voice": {"src": "voz.wav", "volume": 1.0, "start": 0},
              "music": {"src": "musica.mp3", "volume": 0.10, "start": 0, "fade_out": 2.0, "duck": True}, "extra": []},
    "tracks": [{"id": "fundo", "name": "B-roll / fotos"}, {"id": "visual", "name": "Gráficos"}, {"id": "textos", "name": "Textos"}],
    "items": items,
}
json.dump(edit, open(os.path.join(O, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("itens", len(items))
