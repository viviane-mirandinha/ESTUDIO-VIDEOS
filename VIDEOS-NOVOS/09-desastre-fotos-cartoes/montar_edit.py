# 09 desastre fotos+cartoes: trata fotos (sepia leve + vinheta) e escreve edit.json
import json, os
from PIL import Image, ImageOps, ImageFilter, ImageDraw
P = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(P, "img")
W, H = 1280, 720

def vinheta(w, h):
    m = Image.new("L", (w, h), 0); d = ImageDraw.Draw(m)
    d.ellipse([-w * .15, -h * .2, w * 1.15, h * 1.2], fill=255)
    return m.filter(ImageFilter.GaussianBlur(min(w, h) * .18))

def tratar(nome, modo="cover"):
    src = os.path.join(IMG, nome + ".jpg")
    if not os.path.exists(src) or os.path.getsize(src) < 1000: return None
    im = Image.open(src).convert("RGB")
    g = ImageOps.grayscale(im)
    sep = ImageOps.colorize(g, black=(18, 14, 10), white=(246, 236, 218))
    im = Image.blend(im, sep, .55)  # cor desbotada / sepia leve (Fascinating Horror)
    if modo == "cover":
        im = ImageOps.fit(im, (W, H), Image.LANCZOS)
    else:  # documento/retrato: centralizado sobre preto (pillarbox)
        im.thumbnail((W - 200, H - 90), Image.LANCZOS)
        bg = Image.new("RGB", (W, H), (6, 6, 6)); bg.paste(im, ((W - im.width) // 2, (H - im.height) // 2)); im = bg
    preto = Image.new("RGB", (W, H), (0, 0, 0))
    im = Image.composite(im, preto, vinheta(W, H).point(lambda v: 90 + v * 165 // 255))
    out = "img/p_" + nome + ".jpg"; im.save(os.path.join(P, out), quality=90)
    return out

def pick(*nomes, modo="cover"):
    for n in nomes:
        r = tratar(n, modo)
        if r: return r
    raise SystemExit("sem imagem: " + str(nomes))

I = {
 "estadio1991": pick("estadio1991"),
 "arquibancada": pick("arquibancada"),
 "painel": pick("rel_painel", modo="doc"),
 "taylor": pick("rel_taylor", modo="doc"),
 "lista_bg": pick("policia_hq", "justica"),
 "mural": pick("mural", "justica"),
 "estadio_hoje": pick("estadio_hoje"),
 "memorial": pick("memorial_anfield"),
 "fim_bg": pick("estadio_2024"),
}
items = []
def img(id, src, s, e, mo="zoom_in", amt=.06, label=""):
    items.append({"id": id, "type": "image", "track": "fundo", "label": label or id, "start": s, "dur": round(e - s, 2),
                  "in": "fade", "out": "fade", "props": {"src": src, "fill": True, "fit": "cover", "motion": mo, "motion_amount": amt}})
def txt(id, t, s, e, y=640, size=40, italic=False, x=640, w=1100, label=""):
    items.append({"id": id, "type": "text", "track": "textos", "label": label or t[:24], "start": s, "dur": round(e - s, 2),
                  "in": "fade", "out": "fade", "props": {"text": t, "x": x, "y": y, "w": min(w, int(len(t) * size * .5) + 80), "size": size, "color": "#f2ede4",
                  "font": "Georgia", "weight": 400, "align": "center", "bg": "rgba(0,0,0,.55)", "pad": 12, "radius": 4, "shadow": True}})
def cena(id, nome, s, e, params, label=""):
    items.append({"id": id, "type": "scene", "track": "fundo", "label": label or nome, "start": s, "dur": round(e - s, 2),
                  "props": {"scene": nome, "params": params}})

cena("c1", "fh-cartao", 0.0, 5.75, {"linha1": "15 de abril de 1989", "linha2": "Sheffield · Inglaterra", "linha3": "15h06", "t2": 2.1, "t3": 3.7}, "Cartão data")
img("f1", I["estadio1991"], 5.45, 11.6, label="Estádio Hillsborough")
txt("t1", "Semifinal da Copa da Inglaterra · Liverpool x Nottingham Forest", 6.4, 11.3, size=34)
cena("n1", "fh-numero", 11.3, 15.95, {"numero": "97", "texto": "torcedores do Liverpool morreram", "sub": "esmagados nas arquibancadas", "t_texto": .7, "t_sub": 2.4, "bg": I["estadio1991"]}, "Cartão 97")
cena("d1", "fh-planta", 15.85, 28.0, {"t_portao": 1.35, "t_tunel": 4.1, "t_setores": 6.35, "t_grades": 9.25}, "Diagrama Leppings Lane")
cena("n2", "fh-numero", 27.9, 33.15, {"numero": "6", "texto": "minutos de jogo", "sub": "enquanto gente morria encostada na grade", "t_texto": 1.6, "t_sub": 3.0, "bg": I["estadio1991"]}, "Cartão 6 minutos")
cena("c2", "fh-cartao", 33.0, 37.3, {"linha1": "O inquérito inicial", "linha2": "culpou os torcedores: embriaguez e invasão", "linha3": "", "t2": 1.1}, "Cartão inquérito")
cena("c3", "fh-cartao", 37.2, 39.95, {"linha1": "23 anos depois", "linha2": "Painel Independente · 2012", "linha3": "", "t2": 1.3}, "Cartão 23 anos")
img("f3", I["painel"], 39.85, 42.0, amt=.04, label="Relatório do Painel 2012")
cena("l1", "fh-lista", 41.85, 48.35, {"titulo": "O que o painel provou", "item1": "164 depoimentos da polícia foram alterados", "item2": "o socorro demorou a chegar", "item3": "até 41 vítimas tinham chance de sobreviver", "t1": .6, "t2": 2.6, "t3": 4.3, "bg": I["lista_bg"]}, "Lista painel")
img("f4", I["mural"], 48.25, 50.35, amt=.05, label="Mural / justiça")
txt("t4", "A mentira oficial caiu", 48.6, 50.2, y=600, size=52)
img("f5", I["estadio_hoje"], 50.2, 52.25, mo="pan_left", amt=.06, label="Estádio hoje")
txt("t5a", "Fim das grades", 51.1, 52.15, y=630, size=44)
img("f5b", I["arquibancada"], 52.1, 54.05, amt=.05, label="Assentos numerados")
txt("t5b", "Assentos numerados", 52.6, 53.95, y=630, size=44)
img("f6", I["taylor"], 53.9, 55.75, amt=.04, label="Relatório Taylor")
txt("t6", "Relatório Taylor · 1989-1990", 54.3, 55.6, y=655, size=36)
img("f7", I["memorial"], 55.6, 58.65, amt=.06, label="Memorial")
txt("t7", "97 vidas", 57.2, 58.5, y=590, size=72)
cena("fim", "fh-fim", 58.5, 66.31, {"bg": I["fim_bg"], "capa": I["taylor"], "t_inscreva": 5.0}, "Tela final")
items.append({"id": "vinheta", "type": "html", "track": "visual", "label": "Vinheta", "start": 0, "dur": 66.31,
              "props": {"fill": True, "html": "<div class='vh'></div>", "css": ".vh{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 50%,rgba(0,0,0,0) 55%,rgba(0,0,0,.55) 100%)}"}})

name = "09 - DESASTRE FOTOS CARTOES - Hillsborough 1989 o desastre que mudou os estádios"
edit = {"version": 1, "name": name, "estilo": "09-desastre-fotos-cartoes", "grupo": "ESTILOS NOVOS",
        "canvas": {"w": W, "h": H, "fps": 30, "bg": "#000000"}, "duration": 66.31, "template": "generic",
        "audio": {"voice": {"src": "voz.wav", "volume": 1.0, "start": 0},
                  "music": {"src": "musica.mp3", "volume": 0.08, "start": 0, "fade_out": 2.5, "duck": True}, "extra": []},
        "tracks": [{"id": "fundo", "name": "Fotos / cartões"}, {"id": "visual", "name": "Vinheta"}, {"id": "textos", "name": "Textos"}],
        "items": items,
        "referencia": {"canal": "Fascinating Horror", "canal_url": "https://www.youtube.com/@FascinatingHorror", "video": "https://youtu.be/u0zpUOe8q_o",
                       "titulo": "New Zealand's Costliest Earthquake | Fascinating Horror", "nota": "Também Scary Interesting / Plainly Difficult (diagrama). Fotos Wikimedia Commons (img/creditos.json)."}}
json.dump(edit, open(os.path.join(P, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok", len(items), I)
