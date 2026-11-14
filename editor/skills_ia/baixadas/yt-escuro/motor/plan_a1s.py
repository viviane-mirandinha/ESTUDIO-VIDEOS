# Amostra 1 min — Aula 01 (Brecha Viral). Tempos fixos (s) pelo words_full.json.
G = "graphite"
GAP, MAXD, MIND = 0.05, 20, 0.8
PLAN = []
def Tt(t, type, sfx="whoosh", dur=None, **p):
    PLAN.append({"t": t, "type": type, "p": p, "sfx": sfx, **({"dur": dur} if dur else {})})
O = "A1_esconderijos_ORIGINAL_616k_WesTucker.jpg"
TIT = "25 Hiding Spots Burglars Never Check (Retired Cops Use Every One)"
Tt(0.0, "yt_card", "impact", dur=4.4, img=O, title=TIT, ch="Wes Tucker", views=616161, tag="VÍDEO ORIGINAL")
Tt(4.5, "yt_vs", "pop", dur=4.65, top="MESMO TÍTULO, *PALAVRA POR PALAVRA*", tb=1.0,
   a={"img": O, "title": TIT, "ch": "Wes Tucker", "views": 616161, "tag": "ORIGINAL"},
   b={"img": "A1_esconderijos_copia_32views_WesSecures.jpg", "title": TIT, "ch": "Wes Secures", "views": 32, "tag": "CÓPIA"})
Tt(9.24, "yt_text", dur=4.65, chip="A DIFERENÇA", text="mesmo título. mesmo assunto. *19.000x* menos.", size=104)
Tt(13.98, "yt_text", "impact", dur=2.2, text="por *quê?*", size=180)
Tt(16.22, "yt_text", "impact", dur=4.9, chip="AULA 01", text="o erro que *mata* canais", sub="antes do primeiro vídeo", size=130)
Tt(21.22, "yt_text", dur=2.9, chip="MÓDULO 01", text="*90%* dos canais fracassam", sub="sem enrolação: o porquê", size=120)
Tt(24.2, "yt_text", "pop", dur=6.15, chip="ANTES DO MÉTODO", text="o *erro* que quase todo mundo comete", size=116)
Tt(30.48, "yt_text", "pop", dur=1.85, text="já fez isso? *relaxa.*", size=130)
Tt(32.38, "yt_list", "pop", dur=4.5, chip="NESTA AULA", title="números *reais*", items=["por que não funciona", "o que fazer no lugar"])
Tt(36.98, "yt_text", "impact", dur=0.95, text="o erro é *esse:*", size=150)
# 38.0-41.8 = gravação da busca no YouTube (base)
Tt(41.9, "yt_list", "pop", dur=3.15, chip="CTRL+C COMPLETO", title="você *copia*:", items=["o título", "o assunto", "até a capa"], step=.5)
Tt(45.12, "yt_keys", "impact", dur=3.1, img=O, tv=1.5)
Tt(48.32, "yt_text", dur=3.6, chip="PARECE LÓGICO", text="se deu certo pra ele, vai dar certo *pra mim*", size=110)
Tt(52.02, "yt_text", "impact", dur=0.95, text="só que *não dá.*", hlc="red", size=150)
Tt(53.0, "yt_text", "stamp", dur=2.5, chip="NÚMEROS, NÃO OPINIÃO", text="eu fui atrás dos *números*", size=120)
# 55.6-58.1 = gravação do vídeo original rodando (base)
Tt(58.2, "yt_title", "whoosh", dur=12.35, en=TIT, pt="25 esconderijos que ladrões nunca verificam (policiais aposentados usam todos eles)", tpt=6.4, ten=4.6)
Tt(70.7, "yt_card", "coin", dur=5.1, img=O, title=TIT, ch="Wes Tucker", views=616161, tag="QUANDO EU GRAVEI", tagc="yel")
# 75.9-79.3 = vídeo original rodando (base)
