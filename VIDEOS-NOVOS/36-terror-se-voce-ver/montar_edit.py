import json, os
O = os.path.dirname(os.path.abspath(__file__))
NAME = "36 - 24-10-2026 - TERROR SE VOCE VER - Se o seu celular tocar sem chip às 3 da manhã... NÃO ATENDA"
DUR = 70.6
items = []

def cena(id, s, e, modo, label, **p):
    params = {"modo": modo, "rotulo": "PROTOCOLO 03:00 · FICÇÃO", "fade_in": 0.25 if s > 0 else 0}
    params.update(p)
    items.append({"id": id, "type": "scene", "track": "fundo", "label": label, "start": s, "dur": round(e - s, 2),
                  "props": {"scene": "sv_protocolo", "params": params}})

cena("c01", 0.0, 6.0, "aviso", "Aviso: história de ficção", t1=1.86, total=4)
cena("c02", 6.0, 11.5, "quarto", "Quarto 03:00, celular toca", t1=0.88, t2=3.1, hora="03:00", ordem="NÃO ATENDA", t_ordem=4.2)
cena("c03", 11.5, 19.45, "tela", "Tela: número desconhecido", t1=2.78, t2=4.44, t3=5.8)
cena("c04", 19.45, 22.3, "regra", "Regra 1", n=1, total=4, texto="NÃO ATENDA", t1=1.55)
cena("c05", 22.3, 26.55, "contagem", "Contagem 7-8-9", valores="7,8,9", t1=0.1, t2=0.82, t3=1.4, ordem="DEIXE TOCAR", t_ordem=2.82)
cena("c06", 26.55, 29.9, "regra", "Regra 2", n=2, total=4, texto="NÃO DESLIGUE O APARELHO", t1=1.39)
cena("c07", 29.9, 35.4, "mensagem", "Tela não apaga + mensagem", hora="03:04", t1=0.3, t2=3.6, texto="POR QUE|VOCÊ NÃO|ATENDE?")
cena("c08", 35.4, 38.5, "regra", "Regra 3", n=3, total=4, texto="NÃO OLHE PARA A PORTA", t1=1.42)
cena("c09", 38.5, 46.05, "porta", "Toque vem do corredor", t1=1.88, t2=3.88, p1="10ª LIGAÇÃO", p2="DO CORREDOR")
cena("c10", 46.05, 49.85, "regra", "Regra 4", n=4, total=4, texto="FIQUE NA CAMA", t1=1.55)
cena("c11", 49.85, 54.6, "cobrir", "Coberto, 03:13, passos", hora="03:12", hora2="03:13", t1=0.57, t2=1.69, t3=3.35)
cena("c12", 54.6, 62.0, "voz", "A voz é a sua", t1=3.44, t2=5.38, texto="AGORA É A SUA VEZ|DE LIGAR.")
cena("c13", 62.0, DUR, "fim", "CTA final", t1=2.68, t2=4.6, texto="VOCÊ ATENDERIA?", sub="COMENTA AQUI EMBAIXO", p1="INSCREVA-SE")

# legenda palavra a palavra (estilo referência: frase em caixa alta embaixo)
W = json.load(open(os.path.join(O, "words.json"), encoding="utf-8"))["words"]
FIX = {"3": "três", "1.": "um.", "2.": "dois.", "3.": "três.", "4.": "quatro.", "7,": "sete,", "8,": "oito,", "9": "nove", "3h13,": "três e treze,"}
words = [{"w": FIX.get(w["w"], w["w"]), "s": w["s"], "e": w["e"]} for w in W]
items.append({"id": "leg", "type": "caption", "track": "legenda", "label": "Legenda", "start": 6.0, "dur": 56.0,
              "props": {"words": words, "per_group": 5, "x": 640, "y": 652, "size": 30, "color": "#f2f2f2", "dim": "#7a7a7a",
                        "hl_color": "#e0182d", "keywords": ["NÃO", "ATENDA", "REGRA", "PORTA", "SUA"], "bg": "", "font": "MontEB",
                        "weight": 700, "upper": True}})

extra = []
for i, t in enumerate([19.45, 26.55, 35.4, 46.05]):
    extra.append({"id": f"wh{i}", "src": "sfx/whoosh.wav", "start": t - 0.1, "volume": 0.22, "label": "whoosh regra"})
for i, t in enumerate([6.9, 9.9, 11.6, 14.6, 17.6, 22.3, 25.3, 62.2]):
    extra.append({"id": f"tq{i}", "src": "sfx/toque.wav", "start": t, "volume": 0.10, "label": "toque celular (ffmpeg)"})
for i, (t, v) in enumerate([(40.4, 0.22), (43.4, 0.22), (49.9, 0.10)]):
    extra.append({"id": f"ta{i}", "src": "sfx/toque_abafado.wav", "start": t, "volume": v, "label": "toque abafado (ffmpeg)"})

edit = {
    "version": 1, "name": NAME, "estilo": "36-terror-se-voce-ver", "grupo": "ESTILOS NOVOS",
    "canvas": {"w": 1280, "h": 720, "fps": 30, "bg": "#050505"}, "duration": DUR, "template": "generic",
    "fonts": {"MontEB": "fonts/Montserrat-ExtraBold.ttf", "MontMd": "fonts/Montserrat-Medium.ttf"}, "head": "",
    "referencia": {"canal": "Bradikinin / Final Sight", "canal_url": "https://www.youtube.com/@BradikininVideos",
                   "video": "https://youtu.be/-SXNp5h58vQ", "titulo": "If Your Dog Ever Throws The Ball For You... GO GET IT",
                   "nota": "2ª ref: Final Sight https://youtu.be/vCPqDB1FYew (If You Ever See Your Dog Scream At 3AM... HIDE RIGHT NOW). Protocolo de sobrevivência fictício: pictogramas flat brancos no preto, vermelho de destaque, cartões REGRA N, frase em caixa alta embaixo."},
    "audio": {"voice": {"src": "voz.mp3", "volume": 1.0, "start": 0},
              "music": {"src": "musica.mp3", "volume": 0.16, "start": 0, "fade_out": 2.0, "duck": True}, "extra": extra},
    "tracks": [{"id": "fundo", "name": "Cenas ilustradas"}, {"id": "legenda", "name": "Legenda"}],
    "items": items,
}
json.dump(edit, open(os.path.join(O, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("itens", len(items), "extras", len(extra))
