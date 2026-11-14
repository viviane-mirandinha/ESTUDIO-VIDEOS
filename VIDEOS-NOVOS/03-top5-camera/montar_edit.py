# Escreve edit.json do vídeo 03 (TOP 5 CAPTADO EM CÂMERA)
import json

R = "#e8101a"
items = []
n = 0


def add(typ, track, start, dur, props, label=None, **kw):
    global n
    n += 1
    it = {"id": f"{typ[:3]}{n}", "type": typ, "track": track, "start": round(start, 2), "dur": round(dur, 2), "props": props}
    if label:
        it["label"] = label
    it.update(kw)
    items.append(it)


def video(src, s, e, label):
    add("video", "fundo", s, e - s, {"src": f"clips/{src}.mp4", "fill": True, "fit": "cover", "volume": 0}, label)


def hud(s, e, cam, local, hora, data="14/03/2024"):
    add("scene", "visual", s, e - s, {"scene": "cctv_hud", "params": {"cam": cam, "local": local, "data": data, "hora": hora, "cor": R}}, f"HUD {cam}")


def marca(s, e, tipo, x, y, ang=-45, r=70, lab=""):
    add("scene", "visual", s, e - s, {"scene": "cctv_marca", "params": {"tipo": tipo, "x": x, "y": y, "ang": ang, "r": r, "label": lab, "cor": R}}, f"{tipo} {lab}")


def card(s, num, titulo):
    add("scene", "cards", s, 1.5, {"scene": "cctv_numero", "params": {"n": str(num), "titulo": titulo, "cor": R, "fundo": "#000000"}}, f"Número {num}")


def texto(s, e, t, y=600, size=52, bg="rgba(0,0,0,.78)", color="#ffffff", hl=None, font="Impact", w=1100, x=640, inn="fade", weight=400):
    p = {"text": t, "x": x, "y": y, "w": w, "size": size, "color": color, "font": font, "weight": weight, "align": "center",
         "bg": bg, "pad": 14, "radius": 4, "shadow": True}
    if hl:
        p.update({"highlight": hl, "hl_color": R})
    add("text", "textos", s, e - s, p, t[:28], **{"in": inn, "out": "fade"})


def replay(s, e):
    add("text", "textos", s, e - s, {"text": "▶ REPLAY · CÂMERA LENTA", "x": 420, "y": 82, "w": 460, "size": 30, "color": R,
                                     "font": "Consolas", "weight": 700, "align": "left", "bg": "", "shadow": True}, "Replay")


# INTRO
video("intro", 0, 6.9, "Intro multi-câmera")
hud(0, 6.9, "DVR", "4 CÂMERAS", "03:00:00")
texto(0.2, 3.85, "ALGO QUE NÃO DEVERIA EXISTIR", y=360, size=60)
texto(3.9, 6.9, "5 REGISTROS ONDE A LÓGICA FALHA", y=360, size=60, hl=["5"])

# 5 — corredor
card(6.9, 5, "O CORREDOR VAZIO")
video("c5_live", 8.4, 12.9, "#5 corredor")
video("c5_replay", 12.9, 15.4, "#5 replay")
hud(8.4, 15.4, "CAM 02", "CORREDOR B", "03:12:07")
marca(10.8, 12.9, "seta", 668, 290, ang=-40, r=80, lab="ABRE SOZINHA")
marca(13.0, 15.4, "circulo", 640, 360, r=190)
replay(12.9, 15.4)
texto(13.3, 15.4, "SENSOR DE MOVIMENTO: NADA", y=600, size=48, hl=["NADA"])

# 4 — garagem
card(15.4, 4, "A FIGURA NA GARAGEM")
video("c4_live", 16.9, 20.4, "#4 garagem")
video("c4_replay", 20.4, 24.1, "#4 replay")
hud(16.9, 24.1, "CAM 07", "GARAGEM -1", "02:47:31")
marca(17.4, 19.6, "seta", 700, 420, ang=-55, r=80, lab="UMA FIGURA")
texto(19.4, 20.4, "SEM SOM · SEM DISTORÇÃO", y=600, size=48)
marca(21.8, 24.1, "circulo", 640, 400, r=200, lab="ATRAVESSA O CONCRETO")
replay(20.4, 24.1)

# 3 — carro
card(24.1, 3, "O CARRO QUE BALANÇA")
video("c3_live", 25.6, 30.8, "#3 carro")
video("c3_replay", 30.8, 33.7, "#3 replay")
hud(25.6, 33.7, "CAM 04", "ESTACIONAMENTO", "01:05:44")
marca(26.6, 29.4, "seta", 715, 470, ang=-60, r=80, lab="10 SEGUNDOS")
texto(29.6, 30.8, "SEM VENTO · SEM TERREMOTO", y=620, size=48)
marca(31.0, 33.7, "circulo", 640, 360, r=220, lab="O DO LADO FICA PARADO")
replay(30.8, 33.7)

# 2 — cozinha
card(33.7, 2, "A COZINHA VAZIA")
video("c2_live", 35.2, 42.2, "#2 cozinha")
video("c2_replay", 42.2, 45.4, "#2 replay")
hud(35.2, 45.4, "CAM 01", "APTO 304 · VAZIO", "04:18:02")
marca(37.2, 39.4, "seta", 690, 250, ang=-30, r=80, lab="OBJETOS VOAM")
marca(39.5, 42.2, "circulo", 678, 268, r=150, lab="MÃOS INVISÍVEIS")
replay(42.2, 45.4)
texto(43.2, 45.4, "IMÓVEL VENDIDO NA SEMANA SEGUINTE", y=600, size=50, hl=["VENDIDO"])

# 1 — babá eletrônica
card(45.4, 1, "A BABÁ ELETRÔNICA")
video("c1_live", 46.9, 53.8, "#1 babá eletrônica")
hud(46.9, 53.8, "BABÁ CAM", "QUARTO", "03:33:10")
marca(49.4, 51.0, "circulo", 518, 260, r=110, lab="ELA SENTA")
marca(51.2, 53.0, "seta", 245, 78, ang=45, r=90, lab="CANTO ESCURO")
marca(53.1, 53.8, "circulo", 518, 247, r=90, lab="SORRI")
video("c1_real", 53.8, 58.9, "#1 quarto real")
texto(53.9, 58.9, "NO QUARTO, AO MESMO TEMPO", y=60, size=30, bg="rgba(0,0,0,.6)", font="Consolas", weight=700)
texto(55.4, 58.9, "DORMINDO DE BRUÇOS, VIRADA PRO LADO OPOSTO", y=610, size=48, hl=["DE BRUÇOS"])
video("c1_replay", 58.9, 62.0, "#1 replay monitor")
hud(58.9, 62.0, "BABÁ CAM", "QUARTO", "03:33:16")
marca(59.3, 62.0, "circulo", 640, 360, r=170, lab="O SORRISO NA TELA")
replay(58.9, 62.0)

# OUTRO
add("html", "fundo", 62.0, 10.5, {"html": "<div class='ofd'></div>", "css": ".ofd{position:absolute;inset:0;background:radial-gradient(ellipse at 35% 50%,#1a0204 0%,#000 65%)}",
                                    "fill": True, "x": 640, "y": 360, "w": 1280, "h": 720}, "Fundo final")
add("html", "visual", 62.2, 10.3, {"html": "<div class='ofr'></div>", "css": ".ofr{position:absolute;inset:0;border:6px solid #e8101a;box-shadow:0 0 40px rgba(232,16,26,.5)}",
                                    "x": 380, "y": 360, "w": 632, "h": 478}, "Moldura próximo")
add("image", "visual", 62.2, 10.3, {"src": "img/proximo.jpg", "x": 380, "y": 360, "w": 620, "h": 466, "fit": "cover", "motion": "zoom_in", "motion_amount": 0.06}, "Próximo vídeo", **{"in": "fade"})
texto(62.4, 72.5, "PRÓXIMO CASO", x=950, y=210, w=520, size=34, font="Consolas", weight=700, color=R, bg="")
texto(63.0, 72.5, "ÁUDIOS QUE O OUVIDO HUMANO NÃO CAPTA", x=950, y=330, w=520, size=52, bg="")
marca(63.9, 66.5, "seta", 700, 360, ang=0, r=80)
texto(69.3, 72.5, "INSCREVA-SE", x=950, y=520, w=420, size=60, bg=R, inn="pop")

whoosh = [{"id": f"wh{i}", "src": "sfx/whoosh.wav", "start": round(t - 0.2, 2), "volume": 0.22, "label": "whoosh"} for i, t in
          enumerate([6.9, 15.4, 24.1, 33.7, 45.4, 62.0])]

edit = {
    "version": 1,
    "name": "03 - TOP 5 CAPTADO EM CAMERA - 5 coisas inexplicaveis captadas por cameras de seguranca",
    "estilo": "Top 5 captado em câmera (Doc Tops / ROOM 13)",
    "canvas": {"w": 1280, "h": 720, "fps": 30, "bg": "#000000"},
    "duration": 72.5,
    "template": "generic",
    "audio": {"voice": {"src": "voz.wav", "volume": 1.0, "start": 0}, "extra": whoosh},
    "tracks": [{"id": "fundo", "name": "Clipes de câmera"}, {"id": "visual", "name": "HUD / setas / círculos"},
               {"id": "textos", "name": "Textos"}, {"id": "cards", "name": "Cards de número"}],
    "items": items,
    "referencia": {"canal": "DocTops", "canal_url": "https://www.youtube.com/@DocTops", "video": "https://youtu.be/UJym69tx8fM",
                   "titulo": "Top 10 Fantasmas ESCALOFRIANTES Captados En Cámara",
                   "nota": "Também ROOM 13 (https://youtu.be/FgyDQXeHIGI). Clipes: frames de vídeos/fotos Pixabay + evento simulado (gerar_clipes.py)."},
}
json.dump(edit, open("edit.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(items), "itens")
