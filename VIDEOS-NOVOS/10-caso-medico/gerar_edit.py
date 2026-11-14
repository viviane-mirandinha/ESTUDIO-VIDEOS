import json, os
D = os.path.dirname(os.path.abspath(__file__))
NAME = "10 - CASO MEDICO - Um homem bebeu 3 litros de energetico por dia"
DUR = 68.3
items = []
n = [0]
def nid(p):
    n[0] += 1; return f"{p}{n[0]}"
def img(src, s, e, motion="zoom_in", amt=0.08, label="", opacity=1):
    items.append({"id": nid("im"), "type": "image", "track": "fundo", "label": label or src, "start": s, "dur": round(e - s, 2),
                  "in": "fade", "out": "none", "props": {"src": src, "fill": True, "fit": "cover", "motion": motion, "motion_amount": amt, "opacity": opacity}})
def vid(src, s, e, trim=0, label="", speed=1):
    items.append({"id": nid("vd"), "type": "video", "track": "fundo", "label": label or src, "start": s, "dur": round(e - s, 2),
                  "in": "fade", "out": "none", "props": {"src": src, "fill": True, "fit": "cover", "trim": trim, "volume": 0, "speed": speed, "motion": "zoom_in", "motion_amount": 0.05}})
def scene(name, s, e, params, label="", track="visual"):
    items.append({"id": nid("sc"), "type": "scene", "track": track, "label": label or name, "start": s, "dur": round(e - s, 2),
                  "props": {"scene": name, "params": params}})
def txt(t, s, e, x, y, size=56, color="#ffffff", font="Oswald", weight=700, w=1100, bg="", ani="slide_up", label="", align="center", upper=False):
    items.append({"id": nid("tx"), "type": "text", "track": "textos", "label": label or t[:30], "start": s, "dur": round(e - s, 2),
                  "in": ani, "out": "fade", "props": {"text": t, "x": x, "y": y, "w": w, "size": size, "color": color, "font": font, "weight": weight,
                  "align": align, "bg": bg, "pad": 14 if bg else 0, "radius": 8, "shadow": True, "upper": upper}})
def dim(s, e, a=0.45):
    items.append({"id": nid("dm"), "type": "html", "track": "visual", "label": "escurecer", "start": s, "dur": round(e - s, 2), "in": "fade", "out": "none",
                  "props": {"html": f"<div style='width:100%;height:100%;background:rgba(8,8,10,{a})'></div>", "css": "", "fill": True, "x": 640, "y": 360, "w": 1280, "h": 720}})
BOX = "rgba(10,10,12,.78)"
RED, BLUE, GREY = "#e3342f", "#5bc0eb", "#c9ccd4"

# 1. abertura
img("img/xray_corpo.jpg", 0.0, 2.1, "zoom_in", 0.1, "corpo raio-X")
scene("card-termo", 0.0, 2.1, {"rotulo": "", "termo": "CASO ILUSTRATIVO", "expansao": "relatório clínico", "nota": "", "t_termo": 0.1, "t_exp": 0.85}, "card abertura")
# 2. paciente
scene("paciente", 2.1, 6.0, {"rotulo": "PACIENTE", "iniciais": "M.", "idade": "36 anos", "sexo": "masculino", "img": "img/corpo_azul.jpg",
                              "t_idade": 1.3, "t_sexo": 2.6}, "card paciente", track="fundo")
# 3. energetico
img("img/lata.jpg", 6.0, 11.0, "zoom_in", 0.12, "lata energético")
dim(6.0, 11.0, 0.45)
txt("3 LITROS / DIA", 6.85, 11.0, 900, 300, 92, "#ffffff", w=640, bg=BOX, label="3 litros")
txt("de energético", 7.75, 11.0, 900, 395, 40, BLUE, "Inter", 600, w=640, bg=BOX, ani="fade")
txt("DURANTE 2 ANOS", 9.0, 11.0, 900, 480, 56, RED, w=640, bg=BOX, label="2 anos")
# 4. queixa
img("img/corpo_coracao.jpg", 11.0, 17.15, "zoom_in", 0.1, "corpo coração ECG")
dim(11.0, 17.15, 0.35)
txt("QUEIXA PRINCIPAL", 11.0, 17.15, 640, 80, 60, "#ffffff", label="queixa")
txt("PALPITAÇÕES", 11.95, 17.15, 330, 250, 50, "#ffffff", bg=BOX, w=520, ani="slide_left")
txt("coração disparado", 12.3, 17.15, 330, 312, 26, BLUE, "Inter", 600, w=520, ani="fade")
txt("DISPNEIA", 13.0, 17.15, 330, 400, 50, "#ffffff", bg=BOX, w=520, ani="slide_left")
txt("falta de ar aos mínimos esforços", 13.4, 17.15, 330, 462, 26, BLUE, "Inter", 600, w=520, ani="fade")
txt("DOR TORÁCICA NOTURNA", 15.1, 17.15, 330, 550, 50, "#ffffff", bg="rgba(227,52,47,.88)", w=560, ani="slide_left")
txt("dor no peito à noite", 15.5, 17.15, 330, 612, 26, GREY, "Inter", 600, w=520, ani="fade")
# 5. ECG
scene("ecg-traco", 17.15, 23.25, {"titulo": "ELETROCARDIOGRAMA", "sub": "ECG · atividade elétrica do coração", "extras": [4, 6],
                                   "t_alerta": 3.0, "varredura": 4.6}, "ECG", track="fundo")
scene("card-termo", 18.3, 20.9, {"termo": "BLOQUEIO DE RAMO DIREITO", "expansao": "o sinal elétrico chega atrasado ao lado direito",
                                  "t_termo": 0.1, "t_exp": 0.7}, "card bloqueio")
scene("card-termo", 20.9, 23.25, {"termo": "EXTRASSÍSTOLES VENTRICULARES", "expansao": "batimentos extras, fora de hora, vindos dos ventrículos",
                                   "cor": "#ff5a52", "t_termo": 0.1, "t_exp": 0.6}, "card extrassístoles")
# 6. eco
scene("tabela-exame", 23.25, 29.45, {"titulo": "ECOCARDIOGRAMA", "sub": "ultrassom do coração", "cab": ["EXAME", "RESULTADO", ""],
    "linhas": [
        {"nome": "FE", "det": "fração de ejeção: quanto sangue sai a cada batida", "valor": "35%", "normal": "", "status": "ruim", "flag": "BAIXA", "t": 1.6},
        {"nome": "Contração", "det": "hipocinesia global", "valor": "fraca", "normal": "", "status": "ruim", "flag": "", "t": 3.35},
        {"nome": "Cavidades", "det": "câmaras do coração", "valor": "dilatadas", "normal": "", "status": "ruim", "flag": "", "t": 4.95}]},
      "tabela eco", track="fundo")
# 7. ressonancia
img("img/rm_cardiaca.jpg", 29.45, 35.75, "zoom_in", 0.03, "ressonância cardíaca (ilustração)")
items.append({"id": nid("rt"), "type": "html", "track": "visual", "label": "realce difuso (manchas)", "start": 31.6, "dur": 4.15, "in": "fade", "out": "none",
              "props": {"html": "<div class='rt'><i style='left:560px;top:380px'></i><i style='left:690px;top:450px'></i><i style='left:600px;top:520px'></i><i style='left:740px;top:330px'></i></div>",
                        "css": ".rt{position:absolute;inset:0}.rt i{position:absolute;width:120px;height:120px;margin:-60px 0 0 -60px;border-radius:50%;background:radial-gradient(circle,rgba(227,52,47,.75),rgba(227,52,47,0) 70%);mix-blend-mode:screen}",
                        "fill": True, "x": 640, "y": 360, "w": 1280, "h": 720}})
txt("RESSONÂNCIA CARDÍACA", 29.5, 31.4, 640, 90, 60, "#ffffff", bg=BOX, w=900, label="ressonância")
scene("card-termo", 31.4, 35.75, {"rotulo": "", "termo": "REALCE TARDIO DIFUSO", "expansao": "lesão espalhada pelo músculo do coração (miocárdio)",
                                   "nota": "padrão NÃO isquêmico: não foi infarto", "t_termo": 0.1, "t_exp": 0.9, "t_nota": 2.45}, "card realce")
# 8. toxicologico
img("img/cafeina.jpg", 35.75, 40.95, "zoom_in", 0.12, "molécula cafeína")
txt("EXAME TOXICOLÓGICO", 35.8, 40.95, 640, 80, 60, "#ffffff", label="toxicológico")
txt("CAFEÍNA", 37.4, 40.95, 640, 560, 88, RED, bg=BOX, w=520, label="cafeína")
txt("muito acima do normal", 37.9, 40.95, 640, 650, 36, "#ffffff", "Inter", 600, w=700, ani="fade")
# 9. diagnostico
vid("clips/coracao3d.mp4", 40.95, 46.8, 0, "coração 3D")
scene("card-termo", 40.95, 46.8, {"rotulo": "DIAGNÓSTICO", "termo": "CARDIOMIOPATIA DILATADA TÓXICA", "expansao": "o músculo do coração dilatou e ficou fraco",
                                   "nota": "induzida por estimulantes", "t_termo": 0.7, "t_exp": 1.6, "t_nota": 2.95}, "card diagnóstico")
# 10. tratamento
vid("clips/uti.mp4", 46.8, 51.85, 0, "UTI b-roll")
dim(46.8, 51.85, 0.5)
txt("TRATAMENTO", 46.85, 51.85, 640, 80, 60, "#ffffff", label="tratamento")
txt("INTERNAÇÃO EM UTI", 46.9, 51.85, 640, 200, 50, "#ffffff", bg=BOX, w=760, ani="slide_left")
txt("SUPORTE INOTRÓPICO  ·  remédio que reforça a batida", 47.9, 51.85, 640, 300, 34, "#ffffff", "Inter", 700, bg=BOX, w=1000, ani="slide_left")
txt("BETABLOQUEADOR EM ALTA DOSE", 49.0, 51.85, 640, 400, 50, BLUE, bg=BOX, w=860, ani="slide_left")
txt("DESMAME RIGOROSO", 50.55, 51.85, 640, 500, 50, RED, bg=BOX, w=900, ani="slide_left")
# 11. FE recupera
scene("fe-barra", 51.85, 56.3, {"titulo": "FRAÇÃO DE EJEÇÃO", "sub": "6 meses de abstinência total", "de": 35, "para": 50,
                                 "rot_de": "internação", "t_sobe": 2.0}, "barra FE", track="fundo")
# 12. desfecho
vid("clips/coracao_ecg.mp4", 56.3, 61.45, 0, "coração ECG normal")
txt("ARRITMIAS CONTROLADAS", 56.35, 58.2, 830, 120, 56, BLUE, bg=BOX, w=760)
txt("O CORAÇÃO SE RECUPERA", 58.2, 61.45, 830, 480, 64, "#ffffff", bg=BOX, w=780, label="se recupera")
txt("se a agressão parar a tempo", 59.7, 61.45, 830, 575, 36, BLUE, "Inter", 600, w=760, bg=BOX, ani="fade")
# 13. CTA
img("img/lata.jpg", 61.45, 65.5, "zoom_out", 0.1, "lata (CTA)")
dim(61.45, 65.5, 0.55)
txt("CONHECE ALGUÉM QUE EXAGERA NO ENERGÉTICO?", 61.5, 65.5, 900, 280, 52, "#ffffff", w=640, bg=BOX, label="CTA 1")
txt("MANDE ESTE VÍDEO", 64.45, 65.5, 900, 470, 60, BLUE, bg=BOX, w=600, label="CTA 2")
scene("card-termo", 65.5, DUR, {"termo": "INSCREVA-SE", "expansao": "para mais relatórios clínicos", "pos": "centro", "fundo": "#111114",
                                 "t_termo": 0.1, "t_exp": 0.6}, "card inscreva-se", track="fundo")
# vinheta global
items.append({"id": "vinheta", "type": "html", "track": "visual", "label": "vinheta", "start": 0, "dur": DUR, "in": "none", "out": "none",
              "props": {"html": "<div class='vin'></div>", "css": ".vin{position:absolute;inset:0;background:radial-gradient(ellipse at center,rgba(0,0,0,0) 55%,rgba(0,0,0,.55) 100%)}",
                        "fill": True, "x": 640, "y": 360, "w": 1280, "h": 720}})

edit = {"version": 1, "name": NAME, "estilo": "10-caso-medico", "grupo": "ESTILOS NOVOS",
        "canvas": {"w": 1280, "h": 720, "fps": 30, "bg": "#111114"}, "duration": DUR, "template": "generic",
        "fonts": {"Oswald": "fonts/Oswald-Bold.ttf", "Inter": "fonts/Inter.ttf"},
        "referencia": {"canal": "Chubbyemu", "canal_url": "https://www.youtube.com/@chubbyemu", "video": "https://youtu.be/FwdamxI2OSU",
                       "titulo": "Gas Station Egg Salad Sandwich Ruins A Mom's Life", "nota": "também Cabedark (ES) https://youtu.be/xIC3Nd1K3Lg"},
        "audio": {"voice": {"src": "voz.mp3", "volume": 1.0, "start": 0}},
        "tracks": [{"id": "fundo", "name": "Cenas / mídia"}, {"id": "visual", "name": "Gráficos"}, {"id": "textos", "name": "Textos"}],
        "items": items}
json.dump(edit, open(os.path.join(D, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(items), "itens")
