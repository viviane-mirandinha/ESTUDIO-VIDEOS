# build.py — gera edit.json (v1, EDITOR VIDEOS/FORMATO.md) do vídeo 03 (estilo Economics Explained)
# cenas usadas: EDITOR VIDEOS/templates/scenes/ee_capitulo.html, ee_linha.html, ee_barras.html
import json
DUR = 64.49
AM, AZ = "#d8c34a", "#3f8fb0"
items = []

def vid(i, src, s, e, mo="zoom_in", a=0.06, trim=0):
    items.append({"id": i, "type": "video", "track": "fundo", "label": src, "start": s, "dur": round(e - s, 3), "in": "none", "out": "none",
                  "props": {"src": f"clips/{src}.mp4", "fill": True, "fit": "cover", "trim": trim, "volume": 0, "motion": mo, "motion_amount": a}})

def img(i, src, s, e, mo="zoom_in", a=0.1):
    items.append({"id": i, "type": "image", "track": "fundo", "label": src, "start": s, "dur": round(e - s, 3), "in": "none", "out": "none",
                  "props": {"src": f"img/{src}.jpg", "fill": True, "fit": "cover", "motion": mo, "motion_amount": a}})

def scene(i, name, s, e, label, **params):
    items.append({"id": i, "type": "scene", "track": "visual", "label": label, "start": s, "dur": round(e - s, 3),
                  "props": {"scene": name, "params": params}})

def text(i, t, s, e, x, y, size, color="#ffffff", bg="", font="Barlow Condensed", w=1100, a_in="fade", **kw):
    p = {"text": t, "x": x, "y": y, "w": w, "size": size, "color": color, "font": font, "weight": 700, "align": "center",
         "bg": bg, "pad": 14 if bg else 0, "radius": 0, "shadow": not bg}
    p.update(kw)
    items.append({"id": i, "type": "text", "track": "textos", "label": t[:30], "start": s, "dur": round(e - s, 3), "in": a_in, "out": "fade", "props": p})

# 0 — gancho
vid("v_dinheiro", "paying-money-stocks", 0, 3.66)
vid("v_notas", "money-overlays-6", 3.62, 6.05, "zoom_out", 0.08)
text("t_inflacao", "INFLAÇÃO", 4.4, 6.0, 640, 360, 170, upper=True)
# 1 — o que é
img("i_mercado", "supermarket", 6.0, 13.55, "zoom_in", 0.12)
scene("cap1", "ee_capitulo", 6.0, 10.35, "Capítulo 1", cap="Capítulo 1",
      texto="O que é inflação? É o aumento geral e contínuo dos preços.", escuro=0.5, x=300, y=220)
text("t_preco", "R$ 100", 12.3, 13.5, 640, 380, 110, color="#111111", bg=AM, w=360, a_in="slide_up")
scene("g_preco", "ee_linha", 13.5, 24.45, "Gráfico preço x poder de compra",
      titulo="R$ 100 com inflação de 5% ao ano", fonte="Simulação: inflação constante de 5% a.a.",
      xlabels=["Hoje"] + [f"Ano {n}" for n in range(1, 11)], ymin=50, ymax=170,
      series=[{"nome": "Preço do mesmo item", "cor": AM, "valores": [round(100 * 1.05 ** n, 1) for n in range(11)]},
              {"nome": "O que R$ 100 compram", "cor": AZ, "valores": [round(100 / 1.05 ** n, 1) for n in range(11)]}],
      etapas=[[19.9, 0.1], [23.4, 1.0]],
      marcas=[{"i": 0, "t": 14.1, "texto": "R$ 100"}, {"i": 1, "t": 19.9, "texto": "R$ 105"},
              {"i": 10, "t": 23.4, "texto": "R$ 163"}, {"i": 10, "serie": 1, "t": 23.6, "texto": "R$ 61", "baixo": True}])
vid("v_preocupado", "dollars-money-stocks", 24.4, 26.85, "zoom_in", 0.08)
text("t_perda", "−4,8%", 24.5, 26.8, 640, 320, 190, color=AM)
text("t_perda2", "de poder de compra em 1 ano", 24.7, 26.8, 640, 450, 48)
# 2 — causas
img("i_feira", "feira", 26.8, 34.45, "pan_right", 0.12)
scene("cap2", "ee_capitulo", 26.8, 34.45, "Capítulo 2", cap="Capítulo 2", texto="O que causa a inflação?",
      itens="Custos de produção mais altos|Demanda maior do que a oferta|Muito dinheiro circulando",
      tempos="27.86|30.24|32.46", escuro=0.45, x=300, y=170)
# 3 — juros
vid("v_mercado", "market-background-clips", 34.4, 38.85, "zoom_in", 0.06)
scene("cap3", "ee_capitulo", 34.4, 38.85, "Capítulo 3", cap="Capítulo 3",
      texto="Como combater? Os bancos centrais aumentam os juros.", escuro=0.5, x=300, y=220)
scene("g_selic", "ee_linha", 38.8, 43.45, "Gráfico Selic",
      titulo="Taxa Selic", fonte="Fonte: Banco Central do Brasil (Copom)", yfmt="%",
      xlabels=["jan/21", "dez/21", "ago/22", "dez/23", "mai/24", "dez/24", "jun/25"], ymin=0, ymax=16,
      series=[{"nome": "Meta da taxa Selic (% ao ano)", "cor": AM, "valores": [2, 9.25, 13.75, 11.75, 10.5, 12.25, 15]}],
      etapas=[[42.4, 1.0]], marcas=[{"i": 0, "t": 39.6, "texto": "2%", "baixo": False}, {"i": 6, "t": 42.4, "texto": "15%"}])
vid("v_credito", "credit-bills-atm-money", 43.4, 45.75, "zoom_in", 0.06)
text("t_credito", "Crédito mais caro → consumo esfria", 43.5, 45.7, 640, 610, 46, color="#111111", bg=AM, w=760)
# 4 — Plano Real
scene("g_ipca", "ee_barras", 45.7, 51.25, "Gráfico IPCA 1993-97",
      titulo="Inflação anual no Brasil (IPCA)", fonte="Fonte: IBGE", labels=["1993", "1994", "1995", "1996", "1997"],
      valores=[2477, 916, 22.4, 9.6, 5.2], fmt="%", cor=AM, cor_base=AZ, destaque=1, nota="PLANO REAL · JUL/1994", t_nota=47.9)
# 5 — dinheiro parado
vid("v_relogio", "clock-rotating-business-real", 51.2, 54.95, "zoom_in", 0.06)
text("t_parado", "Dinheiro parado perde valor", 52.2, 54.9, 640, 610, 54, color="#111111", bg=AM, w=700)
scene("g_parado", "ee_linha", 54.9, 59.55, "Gráfico parado x investido",
      titulo="Poder de compra de R$ 100 em 10 anos", fonte="Simulação: inflação de 5% a.a.; investimento rendendo 4% a.a. acima da inflação",
      xlabels=["Hoje", "Ano 2", "Ano 4", "Ano 6", "Ano 8", "Ano 10"], ymin=50, ymax=160,
      series=[{"nome": "Investido", "cor": AM, "valores": [round(100 * 1.04 ** n, 1) for n in range(0, 11, 2)]},
              {"nome": "Dinheiro parado", "cor": AZ, "valores": [round(100 / 1.05 ** n, 1) for n in range(0, 11, 2)]}],
      etapas=[[58.3, 1.0]], marcas=[{"i": 5, "t": 58.3, "texto": "R$ 148"}, {"i": 5, "serie": 1, "t": 58.5, "texto": "R$ 61", "baixo": True}])
# 6 — CTA
img("i_reais", "reais", 59.5, DUR, "zoom_in", 0.1)
scene("cap_fim", "ee_capitulo", 59.5, DUR + 0.6, "Fim / CTA", cap="Inscreva-se",
      texto="Quer entender mais de economia? Inscreva-se no canal e comente sua dúvida!", escuro=0.5, x=300, y=220)

E = {"version": 1, "name": "03 - Finanças Stock Footage - O que é inflação e por que seu dinheiro vale menos",
     "canvas": {"w": 1280, "h": 720, "fps": 30, "bg": "#0b0e12"}, "duration": DUR, "template": "generic",
     "fonts": {"Inter": "fonts/Inter.ttf", "Barlow Condensed": "fonts/BarlowCondensed-Bold.ttf"},
     "audio": {"voice": {"src": "voz.mp3", "volume": 1.0, "start": 0},
               "extra": [{"id": f"wh{k}", "src": "sfx/whoosh.wav", "start": t, "volume": 0.15, "label": "whoosh suave"}
                         for k, t in enumerate([5.9, 26.7, 34.3, 59.4])]},
     "tracks": [{"id": "fundo", "name": "Stock footage / fotos"}, {"id": "visual", "name": "Gráficos e capítulos"},
                {"id": "textos", "name": "Textos"}],
     "items": items, "_origem": {"build_script": "build.py", "cenas": ["ee_capitulo", "ee_linha", "ee_barras"]}}
json.dump(E, open("edit.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(items), "itens")
