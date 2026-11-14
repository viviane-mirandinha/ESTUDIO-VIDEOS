# gera edit.json (template local) + template.html do vídeo 06 — tempos tirados do words.json
# coordenadas dos itens: km, origem Ford Island (-157.96, 21.36), x = leste, y = NORTE (positivo para cima)
import json, math, re
from pathlib import Path
P = Path(__file__).parent
DUR = 85.3
LON0, LAT0 = -157.96, 21.36
KY = 110.6; KX = KY * math.cos(math.radians(LAT0))
def LL(lon, lat): return [round((lon - LON0) * KX, 2), round((lat - LAT0) * KY, 2)]
def SHIP(u, v):  # posição (km, norte+) de um navio no Battleship Row (eixo da ilha a 35°)
    a = math.radians(35); X = u * math.cos(a) + v * math.sin(a); Ys = -u * math.sin(a) + v * math.cos(a)
    return [round(X, 3), round(-Ys, 3)]
ARIZ = SHIP(0.18, 0.58); OKLA = SHIP(-0.42, 0.627); ROW = SHIP(-0.12, 0.6)
OPANA = LL(-157.985, 21.705); KANE = LL(-157.735, 21.448); HICKAM = [2.4, -3.9]; WHEELER = LL(-158.04, 21.48)
ENT = LL(-161.2, 21.6); LEX = LL(-172.5, 24.0); SARA = LL(-117.17, 32.7); MIDWAY = LL(-177.37, 28.21)
JAPAO = LL(138.5 - 360, 36.5); HAVAI = LL(-157.5, 20.2)

def T(id, label, start, dur, text, track="textos", **kw):
    return {"id": id, "type": "text", "track": track, "label": label, "start": round(start, 2), "dur": round(dur, 2),
            "by": "template", "props": dict(text=text, **kw)}
def IMG(id, label, start, dur, src, modo, legenda, pos="tl"):
    return {"id": id, "type": "image", "track": "fotos", "label": label, "start": start, "dur": dur, "by": "template",
            "props": {"src": src, "modo": modo, "pos": pos, "legenda": legenda}}

items = [
    {"id": "camera", "type": "param", "label": "Câmera do mapa [t, x_km, y_km(norte), largura_km]", "props": {"value": [
        [0, -0.7, -5.9, 6.6], [8.3, -0.8, -5.75, 5.6], [12.6, -0.8, -5.75, 5.4], [14.7, 0, 34, 190], [17.8, 0, 42, 172],
        [22.4, 3, 17, 100], [24.6, 6, 15, 90], [27.4, 2, 14, 88], [31.0, 0, 12, 80], [33.8, -1, 6, 60],
        [36.0, ROW[0] + 0.2, ROW[1] + 0.1, 5.0], [37.5, ARIZ[0] - 0.45, ARIZ[1] + 0.12, 3.4], [44.3, ARIZ[0] - 0.42, ARIZ[1] + 0.1, 2.9],
        [46.0, OKLA[0] - 0.25, OKLA[1] + 0.1, 2.5], [51.4, OKLA[0] - 0.4, OKLA[1] + 0.1, 2.2], [53.6, 4, 17, 105], [59.4, 1, 18, 95],
        [62.0, 0, 28, 150], [64.5, 0, 32, 165], [65.6, ROW[0] + 0.3, ROW[1] - 0.15, 4.4], [70.4, ROW[0] + 0.3, ROW[1] - 0.15, 3.8],
        [72.8, -1100, 900, 13000], [75.4, -1150, 900, 12600], [78.3, -2200, 1000, 10000], [85.3, -3000, 1100, 8200]]}},
    {"id": "cor_azul", "type": "param", "label": "Cor EUA", "props": {"value": "#3b7dd8"}},
    {"id": "cor_vermelho", "type": "param", "label": "Cor Japão", "props": {"value": "#d23b3b"}},
    # relógio
    T("h1", "Relógio 06:37", 0.0, 12.75, "06:37", "relogio", sub="7 DEZ 1941"),
    T("h2", "Relógio 07:02", 12.75, 9.85, "07:02", "relogio", sub="7 DEZ 1941"),
    T("h3", "Relógio 07:48", 22.6, 4.8, "07:48", "relogio", sub="7 DEZ 1941"),
    T("h4", "Relógio 07:55", 27.4, 8.75, "07:55", "relogio", sub="7 DEZ 1941"),
    T("h5", "Relógio 08:06", 36.15, 8.45, "08:06", "relogio", sub="7 DEZ 1941"),
    T("h6", "Relógio 08:10", 44.6, 7.0, "08:10", "relogio", sub="7 DEZ 1941"),
    T("h7", "Relógio 08:54", 51.6, 8.0, "08:54", "relogio", sub="7 DEZ 1941"),
    T("h8", "Relógio 09:45", 59.6, 11.0, "09:45", "relogio", sub="7 DEZ 1941"),
    # títulos de fase (>=48px)
    T("f1", "Título data", 0.2, 3.0, "7 DE DEZEMBRO DE 1941", size=58, sub="PEARL HARBOR, HAVAÍ"),
    T("f2", "Título alarme", 8.6, 4.0, "O ALARME SOA", size=58, sub="MAS A CADEIA DE COMANDO HESITA"),
    T("f3", "Título primeira onda", 27.5, 3.8, "PRIMEIRA ONDA", size=60, sub="07:55"),
    T("f4", "Título segunda onda", 54.0, 3.0, "SEGUNDA ONDA", size=60, sub="08:54"),
    T("f5", "Título porta-aviões", 71.4, 4.0, "OS PORTA-AVIÕES ESTAVAM AUSENTES", size=56, sub="OS ALVOS PRINCIPAIS"),
    T("f6", "Título erro", 75.5, 2.9, "ESSE ERRO MUDOU A GUERRA", size=60, sub=""),
    T("f7", "Título Midway", 79.2, 6.1, "PRÓXIMA BATALHA: MIDWAY", size=58, sub="HORA A HORA"),
    T("f8", "Botão inscreva-se", 78.5, 6.8, "INSCREVA-SE", size=48, bg="#d23b3b"),
    T("q1", "Citação tenente", 19.9, 2.6, "“NÃO SE PREOCUPE COM ISSO.”", size=62, sub="— TENENTE DE PLANTÃO, 7:02"),
    # números
    T("n1", "183 aviões", 31.2, 4.9, "183", "numeros", size=96, sub="AVIÕES"),
    T("n2", "1.177 marinheiros", 39.1, 5.3, "1.177", "numeros", size=96, sub="MARINHEIROS MORTOS NO ARIZONA"),
    T("n3", "167 aviões", 56.5, 3.0, "167", "numeros", size=96, sub="AVIÕES"),
    T("n4", "2.403 mortos", 64.7, 5.9, "2.403", "numeros", size=96, sub="AMERICANOS MORTOS", pos="l"),
    T("n5", "8 encouraçados", 68.3, 2.3, "8", "numeros", size=96, sub="ENCOURAÇADOS ATINGIDOS", pos="r"),
    # rótulos de unidade (x,y km norte+)
    T("l1", "Rótulo USS Ward", 2.7, 5.6, "USS WARD", "rotulos", x=-1.9, y=-7.0, lado="azul"),
    T("l2", "Rótulo submarino", 5.2, 3.1, "SUBMARINO ANÃO", "rotulos", x=-0.75, y=-6.25, lado="vermelho"),
    T("l3", "Rótulo Pearl Harbor 1", 0.4, 7.9, "PEARL HARBOR", "rotulos", x=0.4, y=-2.6, lado="neutro"),
    T("l4", "Rótulo radar Opana", 14.3, 3.5, "RADAR DE OPANA", "rotulos", x=OPANA[0], y=OPANA[1], lado="azul"),
    T("l5", "Rótulo nuvem", 15.8, 2.0, "NUVEM DE AVIÕES", "rotulos", x=22, y=72, lado="vermelho"),
    T("l6", "Rótulo Kaneohe", 23.6, 3.8, "KANEOHE", "rotulos", x=KANE[0], y=KANE[1], lado="azul"),
    T("l7", "Rótulo Pearl Harbor 2", 27.6, 6.2, "PEARL HARBOR", "rotulos", x=0, y=0, lado="azul"),
    T("l8", "Rótulo Arizona", 36.6, 7.8, "USS ARIZONA", "rotulos", x=ARIZ[0], y=ARIZ[1], lado="azul"),
    T("l9", "Rótulo Oklahoma", 44.8, 6.7, "USS OKLAHOMA", "rotulos", x=OKLA[0], y=OKLA[1], lado="azul"),
    T("l10", "Rótulo Pearl Harbor 3", 53.2, 6.2, "PEARL HARBOR", "rotulos", x=0, y=0, lado="azul"),
    T("l11", "Rótulo Enterprise", 72.0, 3.3, "ENTERPRISE", "rotulos", x=ENT[0], y=ENT[1], lado="azul", icone="porta", abaixo=True),
    T("l12", "Rótulo Lexington", 72.4, 2.9, "LEXINGTON", "rotulos", x=LEX[0], y=LEX[1], lado="azul", icone="porta"),
    T("l13", "Rótulo Saratoga", 72.8, 2.5, "SARATOGA", "rotulos", x=SARA[0], y=SARA[1], lado="azul", icone="porta"),
    T("l14", "Rótulo Pearl Harbor 4", 71.0, 4.3, "PEARL HARBOR", "rotulos", x=0, y=0, lado="vermelho", icone="alvo"),
    T("l15", "Rótulo Japão", 78.6, 6.7, "JAPÃO", "rotulos", x=JAPAO[0], y=JAPAO[1], lado="vermelho"),
    T("l16", "Rótulo Havaí", 78.6, 6.7, "HAVAÍ", "rotulos", x=HAVAI[0], y=HAVAI[1], lado="azul"),
    T("l17", "Rótulo Midway", 82.6, 2.7, "MIDWAY", "rotulos", x=MIDWAY[0], y=MIDWAY[1], lado="amarelo", icone="alvo"),
    # eventos do mapa
    T("e_ward", "Ward x submarino (tiro em 'afunda')", 2.7, 5.6, "USS Ward", "eventos", tipo="ward", tiro=5.0),
    T("e_radar", "Radar + nuvem", 14.0, 3.9, "Radar", "eventos", tipo="radar", x=OPANA[0], y=OPANA[1], nuvem=15.6),
    T("e_kane", "Onda Kaneohe", 23.4, 4.0, "Kaneohe", "eventos", tipo="onda", pts=[[34, 72], [36, 40], KANE], avioes=9, desenho=2.0, alvo=1),
    T("e_w1a", "1ª onda → Pearl", 28.6, 7.5, "Onda 1", "eventos", tipo="onda", pts=[[-12, 78], [-22, 30], [0, 0]], avioes=12, desenho=3.2, alvo=0),
    T("e_w1b", "1ª onda → Wheeler", 29.0, 5.0, "Onda 1b", "eventos", tipo="onda", pts=[[2, 80], [-6, 45], WHEELER], avioes=8, desenho=2.8, alvo=1),
    T("e_w1c", "1ª onda → Hickam", 29.4, 6.7, "Onda 1c", "eventos", tipo="onda", pts=[[-30, 70], [-34, 10], HICKAM], avioes=8, desenho=3.4, alvo=0),
    T("e_ariz", "Arizona explode", 37.75, 47.5, "USS Arizona", "eventos", tipo="explode", navio="arizona"),
    T("e_okla", "Oklahoma vira", 46.5, 38.8, "USS Oklahoma", "eventos", tipo="vira", navio="oklahoma", duracao=1.9),
    T("e_w2a", "2ª onda → Pearl", 54.6, 5.0, "Onda 2", "eventos", tipo="onda", pts=[[44, 64], [30, 22], [0, 0]], avioes=12, desenho=2.6, alvo=0),
    T("e_w2b", "2ª onda → Kaneohe", 54.9, 4.7, "Onda 2b", "eventos", tipo="onda", pts=[[52, 60], [40, 30], KANE], avioes=8, desenho=2.4, alvo=1),
    T("e_w2c", "2ª onda → Hickam", 55.3, 4.3, "Onda 2c", "eventos", tipo="onda", pts=[[60, 50], [30, 0], HICKAM], avioes=8, desenho=2.6, alvo=0),
    T("e_ret", "Retirada para o norte", 60.6, 4.1, "Retirada", "eventos", tipo="retirada", pts=[[0, 0], [-10, 40], [-14, 90]], avioes=14, desenho=3.4),
    T("e_dano", "8 encouraçados destacados", 68.3, 2.4, "Danos", "eventos", tipo="destaque"),
    T("e_porta", "Linhas porta-aviões", 72.0, 3.4, "Porta-aviões", "eventos", tipo="porta"),
    # fotos de arquivo (P&B)
    IMG("p1", "Foto USS Ward", 8.3, 4.35, "img/ward.jpg", "full", "USS WARD (DD-139) — TRIPULAÇÃO DO CANHÃO Nº 3"),
    IMG("p2", "Foto radar Opana", 17.8, 4.75, "img/radar.jpg", "full", "RADAR SCR-270 DE OPANA, 7:02"),
    IMG("p3", "Foto primeira onda", 31.4, 4.5, "img/decolagem.jpg", "inset", "AVIÕES JAPONESES DECOLAM DO PORTA-AVIÕES", "tl"),
    IMG("p8", "Foto Kaneohe", 25.4, 1.95, "img/kaneohe.jpg", "inset", "BASE DE KANEOHE EM CHAMAS", "tl"),
    IMG("p4", "Foto Arizona", 38.7, 5.6, "img/arizona.jpg", "inset", "USS ARIZONA EM CHAMAS", "tl"),
    IMG("p5", "Foto Oklahoma", 48.7, 2.85, "img/oklahoma.jpg", "inset", "USS OKLAHOMA DE CABEÇA PARA BAIXO", "tl"),
    IMG("p6", "Foto Zero", 61.1, 3.5, "img/zero.jpg", "inset", "CAÇA ZERO JAPONÊS (A6M2)", "bl"),
    IMG("p7", "Foto porta-aviões", 75.4, 3.0, "img/enterprise.jpg", "full", "USS ENTERPRISE (CV-6)"),
    {"id": "vinheta", "type": "param", "label": "Vinheta do mapa (0-1)", "props": {"value": 0.55}},
]
edit = {
    "version": 1, "name": "06 - GUERRA TOP-DOWN - Pearl Harbor hora a hora",
    "estilo": "06-guerra-top-down", "grupo": "ESTILOS NOVOS",
    "canvas": {"w": 1280, "h": 720, "fps": 30, "bg": "#2c6470"}, "duration": DUR, "template": "local",
    "fonts": {"Oswald": "fonts/Oswald-Bold.ttf"},
    "referencia": {"canal": "The Operations Room", "canal_url": "https://www.youtube.com/@TheOperationsRoom",
                   "video": "https://youtu.be/25v3B2TUXFo", "titulo": "Pearl Harbor (2/3) - Battleship Row - Animated",
                   "nota": "mapa top-down (água azul-petróleo, terra oliva), navios vistos de cima, setas vermelhas, relógio, fotos P&B em inserto"},
    "audio": {"voice": {"src": "voz.mp3", "volume": 1.0, "start": 0},
              "music": {"src": "musica.mp3", "volume": 0.07, "start": 0, "fade_out": 2.0, "duck": True},
              "extra": [{"id": "w1", "src": "sfx/whoosh.wav", "start": 12.7, "volume": 0.12, "label": "whoosh zoom out"},
                        {"id": "w2", "src": "sfx/whoosh.wav", "start": 33.9, "volume": 0.12, "label": "whoosh mergulho"},
                        {"id": "w3", "src": "sfx/whoosh.wav", "start": 70.7, "volume": 0.12, "label": "whoosh Pacífico"}]},
    "tracks": [{"id": "fundo", "name": "Mapa"}, {"id": "eventos", "name": "Movimentos / eventos"}, {"id": "fotos", "name": "Fotos de arquivo"},
               {"id": "rotulos", "name": "Rótulos de unidade"}, {"id": "numeros", "name": "Números"}, {"id": "textos", "name": "Títulos"},
               {"id": "relogio", "name": "Relógio"}],
    "items": items,
}
json.dump(edit, open(P / "edit.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
src = (P / "template_src.html").read_text(encoding="utf-8")
pre = "".join(f'<img src="{i["props"]["src"]}">' for i in items if i["type"] == "image")
src = src.replace("__MAPDATA__", (P / "map_data.json").read_text()).replace("__PRELOAD__", pre)
(P / "template.html").write_text(src, encoding="utf-8")
print("ok", len(items), "ARIZ", ARIZ, "OKLA", OKLA)
