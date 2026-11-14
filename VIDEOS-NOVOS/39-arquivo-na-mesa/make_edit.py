# Gera edit.json + template.html do estilo 39 "ARQUIVO NA MESA" (rodar de novo após mudar dados)
import json, os, glob, wave
from PIL import Image
NAME = "39 - 24-10-2026 - ARQUIVO NA MESA - O roubo da Mona Lisa em 1911"
w = wave.open("voz.wav"); VOZ = w.getnframes() / w.getframerate()
DUR = round(VOZ + 1.6, 2)

def foto_h(src, w, pad=28, base=58):
    im = Image.open(src); iw, ih = im.size
    return round(w * ih / iw + base)  # altura total da foto com borda (14 em cima, 44 em baixo)

# ---------------- objetos na mesa (coordenadas do mundo 3200x2000, centro do objeto) ----------------
O = []
def obj(id, t, label, **p):
    O.append({"id": id, "type": "scene", "track": "mesa", "label": label, "start": t, "dur": round(DUR - t, 2),
              "by": "template", "props": {"scene": "mesa", "params": p}})

obj("pasta", 0.0, "Pasta do dossiê", kind="pasta", x=720, y=560, w=780, h=540, rot=-4,
    aba="DOSSIÊ 1911/08", texto="MUSEU DO LOUVRE\nOCORRÊNCIA: FURTO\nOBRA: LA GIOCONDA\n(MONA LISA)")
obj("st_conf", 1.0, "Carimbo CONFIDENCIAL", kind="carimbo", x=800, y=700, rot=-13, texto="CONFIDENCIAL", size=70)
obj("ficha1", 2.0, "Ficha: Paris, 21 ago 1911", kind="ficha", x=520, y=1020, w=600, h=300, rot=3,
    texto="PARIS - SEG., 21 AGO 1911\nLOUVRE FECHADO AO PÚBLICO", t_tipo=0.3)
obj("mona", 7.3, "Foto: Mona Lisa", kind="foto", x=1330, y=470, w=320, h=foto_h("img/mona.jpg", 292), rot=5,
    src="img/mona.jpg", legenda="La Gioconda", fita=1)
obj("beroud", 13.9, "Foto: Louis Béroud", kind="foto", x=1780, y=390, w=280, h=foto_h("img/beroud.jpg", 252), rot=-6,
    src="img/beroud.jpg", legenda="Louis Béroud, pintor", fita=1)
obj("vazio", 16.6, "Foto: parede vazia (1911)", kind="foto", x=1960, y=860, w=330, h=foto_h("img/vazio.jpg", 302), rot=3,
    src="img/vazio.jpg", legenda="Salon Carré, 1911", fita=0)
obj("circ", 18.9, "Círculo nos ganchos", kind="circulo", x=1960, y=800, w=190, h=150, rot=0)
obj("n_ganchos", 19.2, "Nota: 4 ganchos de ferro", kind="nota", x=2280, y=640, rot=-7, texto="só 4 ganchos de ferro!", cor="#c0171f", size=46)
obj("ficha2", 21.4, "Ficha: museu fechado 1 semana", kind="ficha", x=1560, y=1100, w=520, h=230, rot=-3,
    texto="LOUVRE FECHADO\nPOR 1 SEMANA", t_tipo=0.1)
obj("moldura", 23.6, "Moldura vazia", kind="moldura", x=1110, y=1160, w=300, h=380, rot=-8)
obj("n_moldura", 24.6, "Nota: moldura na escada", kind="nota", x=1110, y=1405, rot=-4, texto="achada numa escada do Louvre", cor="#1b2a6b", size=38)
obj("picasso", 27.8, "Foto: Picasso", kind="foto", x=560, y=1450, w=250, h=foto_h("img/picasso.jpg", 222), rot=-5,
    src="img/picasso.jpg", legenda="Pablo Picasso", fita=1)
obj("apollinaire", 29.8, "Foto: Apollinaire", kind="foto", x=900, y=1480, w=250, h=foto_h("img/apollinaire.jpg", 222), rot=4,
    src="img/apollinaire.jpg", legenda="Guillaume Apollinaire", fita=1)
obj("n_interr", 28.6, "Nota: interrogado", kind="nota", x=560, y=1215, rot=-3, texto="interrogado", cor="#1b2a6b", size=40)
obj("n_preso", 30.9, "Nota: preso", kind="nota", x=930, y=1245, rot=3, texto="chegou a ser preso", cor="#1b2a6b", size=40)
obj("st_ino1", 33.0, "Carimbo INOCENTE 1", kind="carimbo", x=560, y=1520, rot=-16, texto="INOCENTE", size=50)
obj("st_ino2", 33.25, "Carimbo INOCENTE 2", kind="carimbo", x=900, y=1550, rot=10, texto="INOCENTE", size=50)
obj("peruggia", 35.1, "Foto: Vincenzo Peruggia (ficha 1909)", kind="foto", x=1640, y=1520, w=380, h=foto_h("img/peruggia.jpg", 352), rot=-2,
    src="img/peruggia.jpg", legenda="Vincenzo Peruggia", fita=1)
obj("n_peru", 37.0, "Nota: ex-funcionário", kind="nota", x=2030, y=1340, rot=-5, texto="trabalhou no Louvre", cor="#c0171f", size=44)
obj("n_vidro", 38.7, "Nota: vidros de proteção", kind="nota", x=2060, y=1420, rot=-5, texto="instalava vidros de proteção", cor="#c0171f", size=38)
obj("tempo", 41.4, "Linha do tempo 1911 -> 1913", kind="tempo", x=2500, y=1180, w=560, h=250, rot=2,
    a="AGO 1911", b="DEZ 1913", texto="+ DE 2 ANOS", sub="escondida no quarto dele, em Paris", t_linha=0.9, t_sub=3.2)
obj("excelsior", 46.4, "Recorte: Excelsior, dez 1913", kind="recorte", x=2620, y=560, w=430, h=627, rot=-3, src="img/excelsior.jpg")
obj("n_flor", 48.6, "Nota: Florença", kind="nota", x=2220, y=330, rot=-6, texto="dez. 1913 - Florença", cor="#1b2a6b", size=44)
obj("n_geri", 51.9, "Nota: Alfredo Geri", kind="nota", x=2240, y=420, rot=-4, texto="negociante: Alfredo Geri", cor="#1b2a6b", size=38)
obj("uffizi", 54.3, "Foto: Mona Lisa na Uffizi (1913)", kind="foto", x=2860, y=1560, w=360, h=foto_h("img/uffizi.jpg", 332), rot=4,
    src="img/uffizi.jpg", legenda="Galeria Uffizi, 1913", fita=1)
obj("st_aut", 57.0, "Carimbo VERDADEIRO", kind="carimbo", x=2860, y=1650, rot=-12, texto="VERDADEIRO", size=56)
obj("st_preso", 58.6, "Carimbo PRESO", kind="carimbo", x=1640, y=1600, rot=-9, texto="PRESO", size=84)
obj("recuperada", 60.4, "Foto: Mona Lisa recuperada", kind="foto", x=960, y=330, w=300, h=foto_h("img/recuperada.jpg", 272), rot=-7,
    src="img/recuperada.jpg", legenda="Mona Lisa recuperada", fita=1)
obj("ficha3", 61.0, "Ficha: jan 1914 de volta ao Louvre", kind="ficha", x=1180, y=760, w=520, h=230, rot=-2,
    texto="JAN 1914\nDE VOLTA AO LOUVRE", t_tipo=0.1)
obj("lupa1", 8.4, "Lupa na Mona Lisa", kind="lupa", alvo="mona", r=105, zoom=2.1,
    x0=1250, y0=360, x1=1400, y1=560, t0=0.0, t1=3.2, fim=3.9)
obj("lupa2", 19.6, "Lupa nos ganchos", kind="lupa", alvo="vazio", r=100, zoom=2.0,
    x0=2080, y0=930, x1=1960, y1=800, t0=0.0, t1=1.2, fim=1.9)
for o in O:
    if o["props"]["params"]["kind"] == "lupa":
        o["dur"] = o["props"]["params"]["fim"]

# fios vermelhos (de objeto a objeto)
def fio(id, t, a, b):
    O.append({"id": id, "type": "scene", "track": "fios", "label": f"Fio {a} -> {b}", "start": t, "dur": round(DUR - t, 2),
              "by": "template", "props": {"scene": "fio", "params": {"a": a, "b": b}}})
fio("f1", 30.6, "picasso", "apollinaire")
fio("f2", 39.8, "peruggia", "mona")
fio("f3", 40.2, "peruggia", "vazio")
fio("f4", 40.5, "peruggia", "moldura")
fio("f5", 49.0, "excelsior", "n_flor")
fio("f6", 55.0, "excelsior", "uffizi")
fio("f7", 59.0, "uffizi", "peruggia")
fio("f8", 62.6, "recuperada", "mona")

# câmera: (tempo, cx, cy, zoom, rot, mov)
CAM = [(0.0, 760, 640, 1.30, -2, 0.1), (4.5, 560, 1000, 1.45, 1, 1.3), (7.0, 1330, 480, 1.25, 2, 1.4),
       (13.4, 1800, 420, 1.45, -1, 1.1), (16.4, 2020, 800, 1.30, 1, 1.2), (21.1, 1360, 1140, 1.10, -1, 1.4),
       (26.9, 760, 1420, 1.15, 0, 1.4), (34.4, 1720, 1480, 1.25, -1, 1.3), (39.4, 1500, 1050, 0.62, 0, 1.3),
       (41.3, 2500, 1200, 1.35, 1, 1.4), (46.2, 2450, 520, 1.12, -2, 1.4), (54.0, 2700, 1560, 1.15, 2, 1.3),
       (58.1, 1700, 1520, 1.25, -1, 1.0), (60.2, 1100, 480, 0.95, 1, 1.4), (64.6, 1600, 1000, 0.41, 0, 3.2)]
for k, (t, x, y, z, r, m) in enumerate(CAM):
    O.append({"id": f"cam{k:02d}", "type": "scene", "track": "camera", "label": f"Câmera {k}", "start": t,
              "dur": round((CAM[k + 1][0] if k + 1 < len(CAM) else DUR) - t, 2), "by": "template",
              "props": {"scene": "camera", "params": {"x": x, "y": y, "zoom": z, "rot": r, "mov": m}}})

# legendas (frases do roteiro; tempos do faster-whisper em words.json)
SUB = [(0.0, 4.6, "Paris, segunda-feira, 21 de agosto de 1911."), (4.82, 7.0, "O Louvre está fechado ao público."),
       (7.18, 11.9, "E um homem sai do museu com a Mona Lisa escondida debaixo do avental."), (12.2, 13.3, "Ninguém percebe."),
       (13.46, 16.5, "Só no dia seguinte o pintor Louis Béroud chega para pintar a sala"),
       (16.56, 21.0, "e encontra, no lugar do quadro, apenas quatro ganchos de ferro na parede."),
       (21.26, 23.4, "O museu fecha por uma semana."), (23.52, 26.6, "A moldura vazia aparece numa escada do próprio Louvre."),
       (26.9, 29.3, "A polícia chega a interrogar Pablo Picasso,"), (29.36, 32.2, "e o poeta Guillaume Apollinaire chega a ser preso."),
       (32.38, 34.4, "Os dois eram inocentes."), (34.56, 36.35, "O ladrão era Vincenzo Peruggia,"),
       (36.42, 41.1, "um italiano que tinha trabalhado no Louvre, instalando vidros de proteção nos quadros."),
       (41.34, 46.0, "Por mais de dois anos, a Mona Lisa ficou escondida no quarto dele, em Paris."),
       (46.3, 48.35, "Em dezembro de 1913,"), (48.46, 52.65, "Peruggia levou o quadro para Florença e tentou vendê-lo ao negociante Alfredo Geri."),
       (52.74, 56.1, "Geri chamou o diretor da Galeria Uffizi."), (56.26, 58.2, "O quadro era verdadeiro."),
       (58.3, 60.1, "E Peruggia foi preso."), (60.28, 62.45, "Em janeiro de 1914,"), (62.56, 64.7, "a Mona Lisa voltou ao Louvre."),
       (64.82, 68.6, "E o roubo ajudou a transformá-la no quadro mais famoso do mundo.")]
for k, (a, b, t) in enumerate(SUB):
    O.append({"id": f"lg{k:02d}", "type": "text", "track": "legenda", "label": t[:30], "start": a, "dur": round(b - a, 2),
              "by": "template", "props": {"text": t}})

O.append({"id": "final", "type": "scene", "track": "tela", "label": "Cartão final", "start": 65.6, "dur": round(DUR - 65.6, 2), "by": "template",
          "props": {"scene": "final", "params": {"titulo": "O ROUBO DA MONA LISA", "sub": "PARIS · 1911 – 1914", "carimbo": "CASO ENCERRADO"}}})
O.append({"id": "canto", "type": "param", "label": "Rótulo do canto", "props": {"value": "ARQUIVO 1911/08 · CONFIDENCIAL"}})
O.append({"id": "cor_fio", "type": "param", "label": "Cor do fio/carimbo", "props": {"value": "#b3121b"}})

WH = [4.5, 7.0, 13.4, 21.1, 26.9, 34.4, 41.3, 46.2, 54.0, 60.2, 64.6]
E = {"version": 1, "name": NAME, "estilo": "39-arquivo-na-mesa", "grupo": "ESTILOS NOVOS",
     "canvas": {"w": 1280, "h": 720, "fps": 30, "bg": "#120c08"}, "duration": DUR, "template": "local",
     "fonts": {"Courier Prime": "fonts/CourierPrime-Bold.ttf", "Caveat": "fonts/Caveat.ttf", "Oswald": "fonts/Oswald-Bold.ttf",
               "Inter": "fonts/Inter.ttf", "Cormorant Garamond": "fonts/CormorantGaramond-700.ttf"},
     "referencia": {"canal": "Red File", "canal_url": "https://www.youtube.com/channel/UCNpjH9MosivtBOa45Hbu39g",
                    "video": "https://youtu.be/udbDpAkUh10",
                    "titulo": "56-Year-Old Man Has No Idea Police Just Connected His DNA to a 1996 Murder",
                    "canal2": "Dead Signal Investigation", "canal2_url": "https://www.youtube.com/channel/UC-WT_x7Tpo-C1_XNJFik4ag",
                    "video2": "https://youtu.be/zAoOy28kpqo", "titulo2": "Long Island File Zero",
                    "nota": "dossiê de investigação: mesa escura à luz de luminária, pastas, fotos reais, lupa, fichas datilografadas, legenda pequena centralizada embaixo, cortes lentos"},
     "audio": {"voice": {"src": "voz.wav", "volume": 1.0, "start": 0},
               "music": {"src": "musica.wav", "volume": 0.13, "start": 0, "fade_out": 2.0, "duck": True},
               "extra": [{"id": f"w{k}", "src": "sfx/whoosh.wav", "start": round(t - 0.1, 2), "volume": 0.12, "label": "whoosh"} for k, t in enumerate(WH)]},
     "tracks": [{"id": "camera", "name": "Câmera"}, {"id": "mesa", "name": "Objetos na mesa"}, {"id": "fios", "name": "Fios vermelhos"},
                {"id": "tela", "name": "Cartão final"}, {"id": "legenda", "name": "Legenda"}],
     "items": O}
json.dump(E, open("edit.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
# template.html = template_src.html + pré-carga de toda imagem de img/ (o builder espelha só src= literais)
pre = "".join(f'<img src="img/{os.path.basename(f)}" alt="">' for f in sorted(glob.glob("img/*.jpg") + glob.glob("img/*.png")))
src = open("template_src.html", encoding="utf-8").read().replace("<!--PRELOAD-->", f'<div id="preload" style="display:none">{pre}</div>')
open("template.html", "w", encoding="utf-8").write(src)
print("itens", len(O), "dur", DUR)
