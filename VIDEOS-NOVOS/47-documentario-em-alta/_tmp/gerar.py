# gera edit.json do 47 - documentario em alta (pinturas classicas + cartoes serifados)
import json, os
os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")
w = json.load(open("words.json", encoding="utf-8"))
for x in w:
    if x["w"] == "abrigou?":
        x["w"] = "abrigou."
json.dump(w, open("words.json", "w", encoding="utf-8"), ensure_ascii=False)

DUR = 75.6
CREAM, DIM, FAINT = "#e9e2d4", "#a39a8a", "#7d7566"
items = []


def img(id, src, s, d, motion="zoom_in", amt=0.06, lab="", **k):
    p = {"src": src, "fill": True, "fit": "cover", "motion": motion, "motion_amount": amt}
    p.update(k)
    items.append({"id": id, "type": "image", "track": "fundo", "label": lab, "start": s, "dur": d,
                  "in": "fade", "out": "fade", "props": p})


def html(id, s, d, h, css, lab, track="visual", x=640, y=360, ww=1280, hh=720, io=("fade", "fade")):
    items.append({"id": id, "type": "html", "track": track, "label": lab, "start": s, "dur": d,
                  "in": io[0], "out": io[1], "props": {"html": h, "css": css, "x": x, "y": y, "w": ww, "h": hh}})


def txt(id, t, s, d, x, y, size, font="Cinzel", color=CREAM, weight=400, letter=".32em", ww=1100, lab="", line=1.35):
    items.append({"id": id, "type": "text", "track": "textos", "label": lab or t[:30], "start": s, "dur": d,
                  "in": "fade", "out": "fade",
                  "props": {"text": t, "x": x, "y": y, "w": ww, "size": size, "font": font, "color": color,
                            "weight": weight, "letter": letter, "align": "center", "shadow": True, "line": line}})


def framed(n, s, d, src, lab, ix, iw, ih, nome, desc, credito, tx=930):
    """cartao de retrato: fundo preto, quadro com moldura fina a esquerda, nome em serifa espacada a direita"""
    html(f"bg{n}", s, d, BLACK, BCSS, f"Fundo cartão {nome}", track="fundo")
    html(f"fr{n}", s, d, '<div class="fr"></div>', FCSS, "Moldura", x=ix, y=345, ww=iw + 22, hh=ih + 22)
    items.append({"id": f"i{n}", "type": "image", "track": "fundo", "label": lab, "start": s, "dur": d,
                  "in": "fade", "out": "fade",
                  "props": {"src": src, "x": ix, "y": 345, "w": iw, "h": ih, "fit": "cover",
                            "motion": "zoom_in", "motion_amount": 0.035}})
    txt(f"n{n}", nome, s + .5, d - .5, tx, 325, 40, letter=".3em", ww=560, lab="Nome")
    txt(f"s{n}", desc, s + .8, d - .8, tx, 385, 30, font="Cormorant", color=DIM, letter=".04em", ww=560, lab="Descrição")
    txt(f"c{n}", credito, s + .8, d - .8, ix, 345 + ih / 2 + 42, 24, font="Cormorant", color=FAINT,
        letter=".05em", ww=640, lab="Crédito do quadro")


def capitulo(n, s, d, num, titulo):
    html(f"cap{n}", s, d, BLACK, BCSS, f"Fundo capítulo {num}", track="fundo")
    txt(f"cap{n}a", f"PARTE {num}", s + .15, d - .15, 640, 318, 26, color=DIM, letter=".5em", lab=f"Capítulo {num} — número")
    txt(f"cap{n}b", titulo, s + .3, d - .3, 640, 376, 50, letter=".42em", lab=f"Capítulo {num} — título")


BLACK = '<div class="pr"></div>'
BCSS = '.pr{position:absolute;inset:0;background:radial-gradient(ellipse at center,#161512 0%,#060606 78%)}'
FCSS = ('.fr{position:absolute;inset:0;border:2px solid #b9ad92;'
        'box-shadow:0 18px 60px rgba(0,0,0,.85),inset 0 0 0 8px #0d0c0b,inset 0 0 0 9px #6f6656}')

# --- abertura (voz 0.4-10.4)
img("i1", "img/a_volaire.jpg", 0, 10.9, "zoom_in", 0.07, "Volaire — Vesúvio em erupção")
txt("t1", "GOLFO DE NÁPOLES  ·  ANO 79", 1.4, 8.4, 640, 640, 26, color=DIM, lab="Local e ano")
# --- PARTE I (silêncio 10.4-13.0)
capitulo(1, 10.6, 2.6, "I", "A NUVEM")
# --- Plínio, o Jovem (voz 12.9-16)
framed(2, 13.1, 6.2, "img/c_kauffman.jpg", "Kauffman — Plínio, o Jovem e a mãe em Miseno", 390, 520, 421,
       "PLÍNIO, O JOVEM", "o narrador, aos 17 anos", "Angelica Kauffmann, 1785", tx=950)
# --- a nuvem-pinheiro (voz 16-24)
img("i3", "img/b_wright_erupcao.jpg", 19.2, 6.6, "zoom_in", 0.10, "Wright of Derby — erupção à noite")
txt("q3", "“UM TRONCO ALTÍSSIMO,\nQUE SE ABRIA EM GALHOS”", 20.3, 5.2, 640, 590, 28, letter=".22em", lab="Citação — a nuvem")
# --- Plínio, o Velho (voz 25.3-31)
framed(4, 25.7, 6.0, "img/d_plinio_velho.jpg", "Gravura — Plínio, o Velho", 430, 400, 494,
       "PLÍNIO, O VELHO", "comandante da frota em Miseno", "gravura do século XIX")
# --- navios (voz 31.8-34.9)
img("i5", "img/e_wright_baia.jpg", 31.6, 5.4, "pan_right", 0.08, "Wright of Derby — baía de Nápoles")
# --- rumo ao vulcão (voz 36.7-40.9)
img("i6", "img/g_volaire_noite.jpg", 36.9, 4.9, "zoom_in", 0.08, "Volaire — o vulcão visto do mar")
# --- citação (voz 41.6-46.4)
img("i7", "img/g_volaire_noite.jpg", 41.6, 6.3, "zoom_in", 0.04, "Fundo escurecido da citação", brilho=0.28, blur=3)
txt("q7", "“A SORTE AJUDA\nOS CORAJOSOS.”", 42.0, 5.7, 640, 300, 52, letter=".26em", lab="Citação")
txt("q7c", "PLÍNIO, O JOVEM  —  CARTAS, LIVRO VI, 16", 42.6, 5.1, 640, 470, 24, color=DIM, letter=".28em", lab="Fonte da citação")
# --- PARTE II (silêncio 47.4-49.5)
capitulo(8, 47.75, 2.25, "II", "ESTÁBIA")
# --- Estábia (voz 49.5-58.6)
img("i9", "img/f_bryullov.jpg", 49.9, 9.4, "pan_left", 0.10, "Bryullov — O último dia de Pompeia")
txt("t9", "ESTÁBIA  ·  GOLFO DE NÁPOLES", 50.6, 4.4, 640, 650, 26, color=CREAM, letter=".32em", lab="Local")
# --- as cartas (voz 60.7-65.8)
img("i10", "img/c_kauffman.jpg", 59.3, 7.0, "pan_up", 0.12, "Kauffman — detalhe do jovem com o livro")
txt("t10", "DUAS CARTAS  ·  A TÁCITO", 61.3, 4.8, 640, 640, 26, color=CREAM, letter=".32em", lab="Legenda cartas")
# --- pliniana (voz 66.7-71.6)
img("i11", "img/a_volaire.jpg", 66.3, 6.9, "pan_left", 0.10, "Volaire — final")
txt("t11", "ERUPÇÃO PLINIANA", 68.4, 4.7, 640, 360, 54, letter=".42em", lab="Termo final")
# --- fecho (72.9-75.6)
html("fim", 72.9, 2.7, BLACK, BCSS, "Fundo final", track="fundo", io=("fade", "none"))
txt("fim1", "O HOMEM QUE NAVEGOU RUMO AO VESÚVIO", 73.1, 2.5, 640, 360, 30, color=DIM, letter=".34em", lab="Título final")

html("rodape", 0, DUR, '<div class="rd"></div>',
     '.rd{position:absolute;inset:0;background:linear-gradient(to top,rgba(0,0,0,.72) 0%,rgba(0,0,0,.35) 18%,rgba(0,0,0,0) 34%)}',
     "Escurecer rodapé (legibilidade)", track="visual", io=("none", "none"))
# --- camadas de acabamento (vinheta + grão leve), o vídeo todo
html("vinheta", 0, DUR, '<div class="vg"></div>',
     '.vg{position:absolute;inset:0;background:radial-gradient(ellipse at center,rgba(0,0,0,0) 52%,rgba(0,0,0,.62) 100%)}',
     "Vinheta", track="legenda", io=("none", "none"))
GRAIN = ("<svg class='gr' viewBox='0 0 1280 720' preserveAspectRatio='none'><filter id='gn'><feTurbulence type='fractalNoise' "
         "baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/><feColorMatrix type='saturate' values='0'/></filter>"
         "<rect width='1280' height='720' filter='url(#gn)'/></svg>")
html("grao", 0, DUR, GRAIN, ".gr{position:absolute;inset:0;width:100%;height:100%;opacity:.06;mix-blend-mode:overlay}",
     "Grão de filme", track="legenda", io=("none", "none"))

edit = {
    "version": 1,
    "name": "47 - Documentário em alta - O homem que navegou rumo ao Vesúvio",
    "estilo": "Documentário em alta — pinturas clássicas + cartões serifados (Deep Dive History)",
    "canvas": {"w": 1280, "h": 720, "fps": 30, "bg": "#060606"},
    "duration": DUR,
    "template": "generic",
    "fonts": {"Cinzel": "fonts/Cinzel.ttf", "Cormorant": "fonts/Cormorant.ttf"},
    "referencia": {"canal": "Deep Dive History", "canal_url": "https://www.youtube.com/channel/UCnTb3--OJOzlPYdmRGmxQdA",
                   "video": "https://youtu.be/DTGFWd2WKdg", "titulo": "6. THE BOOK OF ENOCH - The Entire Story",
                   "nota": "2,5 mi views em 28 dias (~3.700 views/h). Clonado só o estilo: pinturas clássicas em Ken Burns lento, "
                           "cartões pretos com serifa espaçada (PARTE N / título), quadro emoldurado + nome, citação com fonte, só voz grave."},
    "audio": {"voice": {"src": "voz.wav", "volume": 1.0, "start": 0}},
    "tracks": [{"id": "fundo", "name": "Pinturas / cartões"}, {"id": "visual", "name": "Molduras"},
               {"id": "textos", "name": "Textos serifados"}, {"id": "legenda", "name": "Acabamento"}],
    "items": items,
}
json.dump(edit, open("edit.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(items), "itens")
