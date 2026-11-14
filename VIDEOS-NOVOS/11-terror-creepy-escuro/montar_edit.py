import json, pathlib
D = pathlib.Path(__file__).parent
NAME = "11 - TERROR CREEPY ESCURO - Três noites numa casa no fim da estrada"
END = 59.88
items = []
def sc(id, s, e, scene, track="fundo", label="", **params):
    items.append({"id": id, "type": "scene", "track": track, "label": label or scene, "start": round(s, 2), "dur": round(e - s, 2),
                  "props": {"scene": scene, "params": params}})
def img(f): return "img/" + f if (D / "img" / f).exists() else None
def plano(id, s, e, f, fb, mov="push", amt=0.08, brilho=0.82, nevoa=0.45):
    src = img(f) or img(fb)
    sc(id, s, e, "fern_plano", label="plano " + src.split("/")[-1], src=src, mov=mov, amt=amt, brilho=brilho, nevoa=nevoa, tint="rgba(11,16,32,.35)")
def tit(id, s, e, num, titulo="", fundo="nenhum", y=50, tam=88, tam_tit=52, t_tit=0.7):
    sc(id, s, e, "terror_titulo", track="textos", label="título " + num, numero=num, titulo=titulo, cor="#c1121f", fundo=fundo, y=y, tam=tam, tam_tit=tam_tit, t_tit=t_tit)

plano("pl1", 0, 6.1, "f_estrada.jpg", "p_floresta.jpg", "push", .08)
tit("ti1", 0.15, 5.95, "RELATO #1", "Três noites na casa do fim da estrada", fundo="escuro", tam=96, tam_tit=54)
plano("pl2", 6.1, 11.0, "f_casa.jpg", "p_casa.jpg", "pan_r", .08, brilho=.55)
sc("fo1", 6.1, 11.0, "terror_forum", track="textos", label="print relato fórum", usuario="u/anonimo_rural", data="postado às 03:12",
   sub="r/relatosreais", titulo="Três noites numa casa no fim da estrada", texto="Cheguei na sexta, cansado, achando que o silêncio ia curar a insônia.", votos="4,1 mil", t_cursor=1.2)
plano("pl3", 11.0, 14.35, "f_janela.jpg", "p_casa.jpg", "push", .07)
tit("ti2", 11.05, 14.3, "NOITE 1", "só o vento nas frestas", y=74, t_tit=1.9)
plano("pl4", 14.35, 18.6, "f_corredor.jpg", "p_porao.jpg", "push", .12)
tit("ti3", 14.4, 18.55, "NOITE 2", "03:00 da manhã", y=50, t_tit=2.8)
plano("pl5", 18.6, 22.0, "f_lanterna.jpg", "p_porao.jpg", "pan_r", .1)
plano("pl6", 22.0, 28.3, "f_pegadas.jpg", "p_porao.jpg", "push", .14)
tit("ti4", 24.2, 28.2, "PEGADAS DESCALÇAS", "vindo do porão", y=80, tam=64, tam_tit=40, t_tit=1.8)
plano("pl7", 28.3, 33.75, "f_cadeira.jpg", "p_cadeira.jpg", "pan_l", .1)
tit("ti4b", 30.4, 33.65, "TRANQUEI O PORÃO", "com a cadeira da cozinha", y=80, tam=64, tam_tit=40, t_tit=1.9)
plano("pl8", 33.75, 37.9, "f_porao.jpg", "p_porao2.jpg", "push", .1, brilho=.5)
tit("ti5", 33.8, 37.85, "NOITE 3", "", fundo="escuro", y=50, tam=110)
plano("pl9", 37.9, 41.65, "f_fresta.jpg", "p_portaluz.jpg", "push", .1)
tit("ti6", 38.4, 41.6, "PODRE. DOCE.", "", y=80, tam=72)
plano("pl10", 41.65, 45.0, "f_macaneta.jpg", "p_porao.jpg", "push", .16)
plano("pl11", 45.0, 49.8, "f_sombra.jpg", "p_floresta.jpg", "push", .06, brilho=.85, nevoa=.3)
tit("ti7", 46.7, 49.75, "O MEU PRÓPRIO ROSTO", "usando a minha camiseta", y=84, tam=60, tam_tit=36, t_tit=2.3)
plano("pl12", 49.8, 55.35, "f_fuga.jpg", "p_floresta.jpg", "pull", .1)
tit("ti8", 53.0, 55.35, "NÃO TRANQUE A PORTA", "CORRA.", fundo="escuro", y=50, tam=84, tam_tit=76, t_tit=1.6)
sc("in1", 55.35, END, "fern_inscreva", track="textos", label="inscreva-se", linha1="MAIS RELATOS QUE NÃO DEIXAM VOCÊ DORMIR",
   botao="INSCREVA-SE", feito="INSCRITO", cor="#c1121f", t_click=1.6)
sc("fx1", 0, END, "terror_flicker", track="overlay", label="vinheta + flicker VHS", forca=0.14, passo=0.08)

edit = {
    "version": 1, "name": NAME, "estilo": "11-terror-creepy-escuro", "grupo": "ESTILOS NOVOS",
    "canvas": {"w": 1280, "h": 720, "fps": 30, "bg": "#05070a"}, "duration": END, "template": "generic",
    "fonts": {"Anton": "fonts/Anton-Regular.ttf", "Oswald": "fonts/Oswald-Bold.ttf"},
    "referencia": {"canal": "Mr. Nightmare", "canal_url": "https://www.youtube.com/@MrNightmare", "video": "https://youtu.be/LPrD0f-bP2k",
                   "titulo": "3 Terrifying TRUE Fall Camping Horror Stories", "nota": "também Chilling Scares (-fAZza2tUU0) e Marcos Campos; ver ESTILOS-NOVOS/11-terror-creepy-escuro/REFERENCIA.txt"},
    "audio": {"voice": {"src": "voz.wav", "volume": 1.0, "start": 0},
              "music": {"src": "musica.mp3", "volume": 0.08, "start": 0, "fade_out": 2.0, "duck": False},
              "extra": [{"id": f"wh{i}", "src": "sfx/whoosh.wav", "start": t, "volume": 0.12, "label": "whoosh suave"} for i, t in enumerate([33.6, 55.25])]},
    "tracks": [{"id": "fundo", "name": "Planos escuros"}, {"id": "textos", "name": "Títulos / print"}, {"id": "overlay", "name": "Vinheta/flicker"}],
    "items": items,
}
(D / "edit.json").write_text(json.dumps(edit, ensure_ascii=False, indent=1), encoding="utf-8")
print("itens", len(items), "faltando flux:", [f for f in ["f_casa","f_lanterna","f_pegadas","f_cadeira","f_porao","f_fresta","f_macaneta","f_sombra","f_fuga"] if not (D/"img"/(f+".jpg")).exists()])
