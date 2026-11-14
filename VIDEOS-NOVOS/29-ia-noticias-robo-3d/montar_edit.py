import json, pathlib
D = pathlib.Path(__file__).parent
NAME = "29 - IA NOTICIAS ROBO 3D - Agora podemos falar com os animais"
END = 58.3
items = []

def sc(id, s, e, scene, track="fundo", label="", **params):
    items.append({"id": id, "type": "scene", "track": track, "label": label or scene, "start": round(s, 2), "dur": round(e - s, 2),
                  "props": {"scene": scene, "params": params}})

def vid(id, s, e, src, trim=0, label="", tv=False):
    p = {"src": src, "fit": "cover", "trim": trim, "volume": 0, "speed": 1, "opacity": 1, "motion": "zoom_in", "motion_amount": 0.06}
    if tv: p.update({"x": 640, "y": 345.5, "w": 980, "h": 551, "radius": 46})
    else: p["fill"] = True
    items.append({"id": id, "type": "video", "track": "fundo", "label": label or src, "start": round(s, 2), "dur": round(e - s, 2), "in": "fade", "props": p})

def foto(id, s, e, src, mov="zoom_in", label=""):
    items.append({"id": id, "type": "image", "track": "fundo", "label": label or src, "start": round(s, 2), "dur": round(e - s, 2), "in": "fade",
                  "props": {"src": src, "fill": True, "fit": "cover", "motion": mov, "motion_amount": 0.08}})

def tag(id, s, e, texto, **kw):
    sc(id, s, e, "ia29_tag", track="textos", label="rótulo " + texto, texto=texto, **kw)

# 1. Cientistas usaram IA (robô mascote no ar)
sc("rb1", 0, 2.7, "ia29_robo", label="robô LIVE", pose="centro", bonsai=0, live=1, t_robo=0.4, rotulo="Inteligência artificial", t_rot=1.2)
# 2. baleias-cachalote
foto("ft1", 2.7, 5.6, "img/w_sperm1.jpg", "zoom_in", "foto cachalotes (Wikimedia)")
tag("tg1", 2.7, 5.6, "Baleias-cachalote", sub="decifrar a comunicação", t_in=1.4, t_sub=0.9)
# 3. Project CETI
sc("cd1", 5.6, 8.0, "ia29_card", label="card CETI", cor="azul", pre="Project", texto="CETI", tam=150, t_txt=0.7)
# 4. alfabeto fonético
sc("cd2", 8.0, 9.3, "ia29_card", label="card alfabeto", cor="dourado", texto="Alfabeto fonético", tam=100, t_txt=0.05)
# 5. cliques curtos e longos -> códigos -> sílabas
sc("bp1", 9.3, 14.3, "ia29_blueprint", label="blueprint cliques", modo="cliques", src="img/cut_sperm.png",
   rot1="Cliques curtos", rot2="Longos", rot3="Códigos combinatórios", rot4="Semelhantes a sílabas", t1=0.45, t2=1.05, t3=2.0, t4=3.45)
# 6. isso muda tudo (close do robô)
sc("rb2", 14.3, 15.56, "ia29_robo", label="robô close", pose="close", bonsai=0, titulo="Isso muda tudo", t_tit=0.05)
# 7. não é apenas som -> estrutura linguística
sc("cd3", 15.56, 18.18, "ia29_card", label="card som x estrutura", cor="preto", texto="Não é apenas som", texto2="É estrutura linguística", t2=1.1, tam=88, t_txt=0.05)
# 8. o avanço não para no oceano
vid("vd1", 18.18, 20.3, "clips/oceano.mp4", 2, "oceano")
tag("tg2", 18.18, 20.3, "Não para no oceano", t_in=0.9)
# 9. NatureLM-audio / Earth Species Project
sc("bs1", 20.3, 23.48, "ia29_busca", label="busca NatureLM", consulta="NatureLM-audio", t_dig=0.3, vel=12, res_tit="NatureLM-audio", res_sub="Earth Species Project", t_res=1.55)
# 10. pássaros, morcegos, primatas, sem treinamento prévio
sc("bp2", 23.48, 29.5, "ia29_blueprint", label="blueprint espécies", modo="especies", titulo="Classifica vocalizações", t0=0.3,
   src1="img/p_bird2.jpg", rot1="Pássaros", t1=1.8, src2="img/p_bat.jpg", rot2="Morcegos", t2=2.42, src3="img/p_chimp.jpg", rot3="Primatas", t3=3.2,
   rot4="Sem treinamento prévio", t4=3.9)
# 11. padrões universais (robô + pássaro + balões)
sc("rb3", 29.5, 34.18, "ia29_robo", label="robô + pássaro balões", pose="largo", bonsai=1, passaro="img/cut_bird.png", t_robo=0.6, t_ave=1.5, arco=1,
   titulo="Padrões universais", t_tit=2.15)
# 12. estresse em fazendas
vid("vd2", 34.18, 37.12, "clips/fazenda.mp4", 1, "fazenda")
tag("tg3", 34.18, 37.12, "Sinais de estresse", sub="em fazendas", t_in=1.2, t_sub=2.45)
# 13. caça furtiva em tempo real
vid("vd3", 37.12, 39.62, "clips/elefantes.mp4", 1, "elefantes")
tag("tg4", 37.12, 39.62, "Alerta de caça furtiva", sub="em tempo real", cor="vermelho", live=1, pos="esq-topo", t_in=0.15, t_sub=1.75)
# 14. o próximo passo: a resposta
sc("cd4", 39.62, 41.62, "ia29_card", label="card resposta", cor="preto", pre="O próximo passo", texto="A resposta", tam=110, t_txt=0.2)
# 15. cliques sintéticos que as baleias entendam
sc("rb4", 41.62, 44.5, "ia29_robo", label="robô cliques sintéticos", pose="centro", bonsai=0, t_robo=0.2, rotulo="Cliques sintéticos", t_rot=0.75,
   titulo="Que as baleias entendam", t_tit=1.65)
# 16. deixar de apenas observar
vid("vd4", 44.5, 47.9, "clips/mergulho.mp4", 0, "mergulho TV", tv=True)
tag("tg5", 44.5, 47.9, "Observar a natureza", crt=1, pos="esq-baixo", t_in=1.95)
# 17. negociar com ela
sc("cd5", 47.9, 49.34, "ia29_card", label="card negociar", cor="dourado", texto="Negociar", sub="com a natureza", tam=120, t_txt=0.1, t_sub=0.6)
# 18. acompanhar a fronteira, inscreva-se
sc("rb5", 49.34, 52.28, "ia29_robo", label="robô inscreva-se", pose="largo", bonsai=1, passaro="img/cut_bird.png", titulo="Acompanhe essa fronteira", t_tit=0.45,
   botao="INSCREVA-SE", t_botao=2.1)
# 19. primeiro diálogo entre espécies
sc("rb6", 52.28, END, "ia29_robo", label="robô diálogo final", pose="largo", bonsai=1, passaro="img/cut_bird.png", t_robo=0.35, t_ave=1.1, arco=1,
   titulo="O primeiro diálogo entre espécies", t_tit=0.4)

edit = {
    "version": 1, "name": NAME, "estilo": "29-ia-noticias-robo-3d", "grupo": "ESTILOS NOVOS",
    "canvas": {"w": 1280, "h": 720, "fps": 30, "bg": "#000000"},
    "duration": END, "template": "generic",
    "head": '<script src="https://cdn.jsdelivr.net/npm/three@0.150.1/build/three.min.js"></script>'
            '<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;900&display=swap" rel="stylesheet">',
    "referencia": {"canal": "There's An AI For That", "canal_url": "https://www.youtube.com/channel/UCHCCGSnjLpHwL2bv-d4yz7g",
                   "video": "https://youtu.be/bs0qWWztyP8", "titulo": "We Can Finally Talk To Animals",
                   "nota": "robô 3D original procedural (Three.js), não o modelo do canal; ver ESTILOS-NOVOS/29-ia-noticias-robo-3d/REFERENCIA.txt"},
    "audio": {
        "voice": {"src": "voz.mp3", "volume": 1.0, "start": 0},
        "music": {"src": "musica.mp3", "volume": 0.1, "start": 0, "fade_out": 2.0, "duck": True},
        "extra": [],
    },
    "tracks": [{"id": "fundo", "name": "Cenas / mídia"}, {"id": "textos", "name": "Rótulos"}],
    "items": items,
}
(D / "edit.json").write_text(json.dumps(edit, ensure_ascii=False, indent=1), encoding="utf-8")
print("itens", len(items))
