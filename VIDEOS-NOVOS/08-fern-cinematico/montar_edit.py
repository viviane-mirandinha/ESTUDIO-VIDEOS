import json, os, pathlib
D = pathlib.Path(__file__).parent
NAME = "08 - FERN CINEMATICO - Silk Road o mercado secreto da internet"
END = 59.2
items = []

def sc(id, s, e, scene, track="fundo", label="", **params):
    items.append({"id": id, "type": "scene", "track": track, "label": label or scene, "start": round(s, 2), "dur": round(e - s, 2),
                  "props": {"scene": scene, "params": params}})

def img(f):
    return "img/" + f if (D / "img" / f).exists() else None

def plano(id, s, e, f, mov="push", amt=0.1, fb=None, **kw):
    src = img(f) or (img(fb) if fb else None)
    if src:
        sc(id, s, e, "fern_plano", label="plano " + f, src=src, mov=mov, amt=amt, **kw)
    else:
        sc(id, s, e, "fern_three", label="3D terreno (fallback)", modo="terreno", seed=len(id) * 5)

def tit(id, s, e, texto, **kw):
    sc(id, s, e, "fern_titulo3d", track="textos", label="título " + texto.replace("|", " "), texto=texto, **kw)

# 1. 2011 / Ross Ulbricht
sc("th1", 0, 2.75, "fern_three", label="3D terreno noite", modo="terreno", seed=3)
tit("ti1", 0, 2.75, "2011", fonte="serif", cor="#f2b740", tam=140, y=46, sub="Ross Ulbricht", t_sub=1.2)
# 2. Silk Road, mercado anonimo
plano("pl1", 2.75, 4.95, "f_laptop.jpg", "push", .1)
tit("ti2", 2.75, 4.95, "SILK ROAD", tam=112, y=48, sub="um mercado anônimo", t_sub=.85)
# 3. drogas, armas, bitcoin
plano("pl2", 4.95, 7.55, "f_contrabando.jpg", "pan_r", .1, brilho=1.35, luz="55% 70%")
tit("ti3", 4.95, 7.55, "DROGAS|ARMAS|BITCOIN", tam=84, y=50, passos="0.15,0.8,2.0")
# 4. liberdade total
plano("pl3", 7.55, 9.72, "f_liberdade.jpg", "push", .08)
tit("ti4", 7.55, 9.72, "LIBERDADE TOTAL", tam=84, y=80, sub="a promessa", t_sub=.2)
# 5. a realidade foi outra (cartela branca)
tit("ti5", 9.72, 11.25, "A REALIDADE FOI OUTRA", tam=86, y=50, fundo="branco")
# 6. agente federal
plano("pl4", 11.25, 14.45, "f_agente.jpg", "pan_l", .1)
tit("ti6", 11.25, 14.45, "AGENTE FEDERAL", tam=84, y=80, sub="infiltrado como moderador do site", t_sub=1.85)
# 7. 2013 San Francisco
plano("pl5", 14.45, 16.6, "f_cidade2011.jpg", "pan_r", .1, brilho=1.3)
tit("ti7", 14.45, 16.6, "2013", fonte="serif", cor="#f2b740", tam=140, y=46, sub="San Francisco", t_sub=.6)
# 8. biblioteca publica (foto real)
sc("mo1", 16.6, 18.7, "fern_moldura3d", label="moldura biblioteca", src="img/w_glenpark.jpg", legenda="BIBLIOTECA PÚBLICA",
   sub="Glen Park, San Francisco", lado="esq", ang=-20, larg=560, t_txt=.5)
# 9. laptop aberto e desbloqueado
plano("pl6", 18.7, 21.0, "f_biblioteca.jpg", "push", .1)
tit("ti8", 18.7, 21.0, "LAPTOP ABERTO|E DESBLOQUEADO", tam=72, y=76, empilhar=1, passos="0.45,1.5")
# 10. 1 bilhao
sc("nu1", 21.0, 24.75, "fern_numero", label="número 1 bilhão", valor=1000000000, prefixo="US$ ", antes="MAIS DE", sub="em vendas", t_conta=2.0)
# 11. prisao perpetua
plano("pl7", 24.75, 30.0, "f_prisao.jpg", "push", .08)
tit("ti9", 25.9, 30.0, "PRISÃO PERPÉTUA", tam=88, y=78, sub="sem liberdade condicional", t_sub=1.6)
# 12. nao acabou ali
tit("ti10", 30.0, 32.1, "MAS NÃO ACABOU ALI", tam=88, y=50, fundo="nevoa")
# 13. 2024 candidato
sc("th2", 32.1, 34.0, "fern_three", label="3D terreno 2024", modo="terreno", seed=11)
tit("ti11", 32.1, 34.0, "2024", fonte="serif", cor="#f2b740", tam=140, y=46, sub="eleição nos EUA", t_sub=.6)
sc("mo2", 34.0, 36.9, "fern_moldura3d", label="moldura candidato", src="img/w_trump.jpg", legenda="DONALD TRUMP",
   sub="candidato à presidência promete libertá-lo", lado="dir", ang=-18, larg=380, t_txt=.3)
# 14. janeiro 2025 perdao
plano("pl8", 36.9, 42.22, "f_saida.jpg", "push", .1)
tit("ti12", 36.9, 39.85, "JANEIRO 2025", fonte="serif", cor="#f2b740", tam=104, y=22)
tit("ti13", 39.85, 42.22, "PERDÃO TOTAL", tam=88, y=22, sub="e fora da prisão", t_sub=1.3)
# 15. inscreva-se
sc("in1", 42.22, 44.75, "fern_inscreva", track="textos", label="inscreva-se", t_click=1.9)
# 16. site caiu (foto real da apreensao) + copias (3D)
sc("mo3", 44.75, 46.45, "fern_moldura3d", label="moldura site apreendido", src="img/w_seized.jpg", legenda="O SITE ORIGINAL CAIU",
   lado="centro", ang=-10, larg=560, t_txt=.3)
sc("th3", 46.45, 48.35, "fern_three", label="3D servidores copias", modo="racks", t1=0.0, t2=0.25)
tit("ti14", 46.45, 48.35, "CÓPIAS EM SEMANAS", tam=64, y=14, passos="0.5")
# 17. guerra contra a criptografia
plano("pl9", 48.35, 51.4, "f_guerra.jpg", "pan_r", .1, brilho=1.45)
tit("ti15", 48.35, 51.4, "CRIPTOGRAFIA ANÔNIMA", tam=72, y=80, passos="1.0", sub="a guerra nunca parou", t_sub=2.2)
# 18. hoje supera o auge
sc("ba1", 51.4, 55.56, "fern_barras", label="barras hoje x auge", t_b=1.1, t_a=3.0)
# 19. fecho
plano("pl10", 55.56, END, "f_final.jpg", "push", .12, brilho=1.25, saida=1)
tit("ti16", 55.56, END, "A TECNOLOGIA MUDOU|O JOGO CONTINUA", tam=76, y=50, empilhar=1, passos="0.3,1.55")

edit = {
    "version": 1, "name": NAME, "estilo": "08-fern-cinematico", "grupo": "ESTILOS NOVOS",
    "canvas": {"w": 1280, "h": 720, "fps": 30, "bg": "#05070a"},
    "duration": END, "template": "generic",
    "head": '<script src="https://cdn.jsdelivr.net/npm/three@0.150.1/build/three.min.js"></script>',
    "referencia": {"canal": "Fern", "canal_url": "https://www.youtube.com/@Fern-TV", "video": "https://youtu.be/JN_d89-FEKk",
                   "titulo": "The Stoner Kids Dealing Guns to the Army", "nota": "também Not What You Think / RealLifeLore; ver ESTILOS-NOVOS/08-fern-cinematico/REFERENCIA.txt"},
    "audio": {
        "voice": {"src": "voz.wav", "volume": 1.0, "start": 0},
        "music": {"src": "musica.mp3", "volume": 0.13, "start": 0, "fade_out": 2.0, "duck": True},
        "extra": [{"id": f"wh{i}", "src": "sfx/whoosh.wav", "start": t, "volume": 0.14, "label": "whoosh"}
                  for i, t in enumerate([9.62, 29.9, 42.12, 51.3])],
    },
    "tracks": [{"id": "fundo", "name": "Cenas 3D / planos"}, {"id": "textos", "name": "Títulos"}],
    "items": items,
}
(D / "edit.json").write_text(json.dumps(edit, ensure_ascii=False, indent=1), encoding="utf-8")
print("itens", len(items), "faltando:", [f for f in ["f_prisao.jpg", "f_saida.jpg", "f_guerra.jpg", "f_final.jpg", "f_sf2013.jpg"] if not (D / "img" / f).exists()])
