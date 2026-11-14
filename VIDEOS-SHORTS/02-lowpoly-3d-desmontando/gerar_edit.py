"""Gera edit.json do short 02 — TODO tempo sai do words.json (whisper) via at()."""
import json, os, sys, subprocess
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, D)
from alinhar import Falas
F = Falas(D, os.path.join(D, "..", "..", "ROTEIROS-SHORTS", "02 - *.txt"))
at = F.at
NAME = "02 - LOWPOLY 3D DESMONTANDO - O ar-condicionado nao fabrica frio"
DUR = round(F.dur_audio + 0.6, 2)

items = []
def shot(i, a, b, label):
    items.append({"id": i, "type": "html", "track": "fundo", "label": label, "by": "template", "start": round(a, 2), "dur": round(b - a, 2), "props": {"html": ""}})
def tempo(i, v, label):
    items.append({"id": i, "type": "param", "label": "tempo: " + label, "props": {"value": round(v, 2)}})
def lab(i, txt, a, b, kind="pill", **p):
    items.append({"id": i, "type": "text", "track": "rotulos", "label": txt[:30], "by": "template", "start": round(a, 2), "dur": round(b - a, 2),
                  "props": dict(text=txt, kind=kind, **p)})

S = [("sh_abre", 0, "3D: sala, boneco com calor, balde na frente do ventilador"),
     ("sh_balde", at("Pra derreter"), "3D: gelo rouba calor"),
     ("sh_liquido", at("Então você troca"), "3D: troca por líquido especial"),
     ("sh_ferve", at("Ele ferve"), "3D: ferve a -50 °C"),
     ("sh_fluido", at("Esse é o fluido"), "3D: fluido refrigerante"),
     ("sh_serp", at("Você põe"), "3D: serpentina + ventilador"),
     ("sh_evap", at("Esse é o evaporador"), "3D: evaporador"),
     ("sh_gas", at("Mas"), "3D: vira gás e escapa"),
     ("sh_acaba", at("E desse jeito"), "3D: líquido acabando"),
     ("sh_ciclo", at("O truque"), "3D: ciclo (seta)"),
     ("sh_soltar", at("Pra isso"), "3D: soltar o calor"),
     ("sh_fora", at("Só que mesmo"), "3D: casa por fora (temperaturas)"),
     ("sh_bomba", at("Então você liga"), "3D: bomba espreme o gás"),
     ("sh_fim", at("Quer"), "3D: final COMENTE FRIO")]
for k, (i, a, l) in enumerate(S):
    shot(i, a, S[k + 1][1] if k + 1 < len(S) else DUR, l)
tempo("k_troca", at("troca"), "balde some"); tempo("k_jarra", at("líquido"), "recipiente aparece")
tempo("k_fervendo", at("fervendo"), "ferve forte"); tempo("k_serpentina", at("serpentina"), "serpentina cresce")
tempo("k_ventilador", at("ventilador"), "ventilador liga"); tempo("k_vento", at("vento"), "vento gelado")
tempo("k_vira_gas", at("vira gás"), "gás sai da ponta"); tempo("k_evaporando", at("evaporando"), "líquido acaba")
tempo("k_espreme", at("espreme"), "pistão espreme"); tempo("k_esquenta", at("esquenta"), "gás esquenta")
tempo("k_pneu", at("igual"), "bomba de pneu")
T = dict((i, a) for i, a, _ in S)
def fim(i): ks = [x[0] for x in S]; j = ks.index(i); return (S[j + 1][1] if j + 1 < len(S) else DUR) - 0.05

lab("p_quarto", "QUARTO: 30 °C", 0.3, fim("sh_abre"), "pill", anchor="quarto", dot="#ff8a1f", size=50)
lab("st_tira", "TIRA CALOR", at("tirando") - 0.05, fim("sh_abre"), "sticker", y=430, size=92, rot=-6)
lab("st_nao", "NÃO PÕE FRIO", at("não") - 0.05, fim("sh_abre"), "sticker", y=560, size=84, rot=-6, color="#7fd0ff")
lab("p_rouba", "GELO: ROUBA CALOR", at("rouba") - 0.05, fim("sh_balde"), "pill", anchor="balde", dy=-80, dot="#ff8a1f", size=50)
lab("p_liquido", "LÍQUIDO ESPECIAL", at("líquido") - 0.05, fim("sh_liquido"), "pill", anchor="jarra", dy=-90, dot="#3d8fe8", size=50)
lab("st_fervendo", "FERVENDO!", at("fervendo") - 0.05, fim("sh_liquido"), "sticker", y=430, size=100, rot=-6)
lab("st_ferve", "FERVE A -50 °C", at("ferve") - 0.05, fim("sh_ferve"), "sticker", y=430, size=104, rot=-6)
lab("st_fluido", "FLUIDO\nREFRIGERANTE", T["sh_fluido"], fim("sh_fluido"), "sticker", y=470, size=92, rot=-5)
lab("st_serp", "SERPENTINA", at("serpentina") - 0.05, at("ventilador") - 0.1, "sticker", y=430, size=96, rot=-6)
lab("p_vent", "VENTILADOR", at("ventilador") - 0.05, fim("sh_serp"), "pill", anchor="vent", dy=-60, dot="#8fd0e8", size=50)
lab("p_vento", "VENTO: GELADO", at("vento") - 0.05, fim("sh_serp"), "pill", y=560, dot="#3d8fe8", size=50)
lab("st_evap", "EVAPORADOR", T["sh_evap"], fim("sh_evap"), "sticker", y=430, size=104, rot=-6)
lab("p_gas", "VIRA GÁS", at("vira gás") - 0.05, at("famoso") - 0.1, "pill", anchor="ponta", dx=-40, dy=-70, dot="#cfd8e3", size=50)
lab("st_gasref", "GÁS\nREFRIGERANTE", at("famoso") - 0.05, fim("sh_gas"), "sticker", y=430, size=92, rot=-6)
lab("p_acaba", "LÍQUIDO: ACABANDO", at("evaporando") - 0.05, fim("sh_acaba"), "pill", anchor="jarra", dy=-90, dot="#e0344b", size=50)
lab("p_volta", "GÁS → LÍQUIDO DE NOVO", at("virar") - 0.05, fim("sh_ciclo"), "pill", y=430, dot="#3d8fe8", size=50)
lab("st_ciclo", "CICLO", at("ciclo") - 0.05, fim("sh_ciclo"), "sticker", y=560, size=120, rot=-6)
lab("st_soltar", "SOLTAR O CALOR", at("soltar") - 0.05, fim("sh_soltar"), "sticker", y=430, size=96, rot=-6)
lab("p_gasgel", "GÁS: GELADO", at("gás ainda") - 0.05, fim("sh_fora"), "pill", anchor="ponta", dx=170, dy=-170, dot="#3d8fe8", size=50)
lab("p_quarto2", "QUARTO: 30 °C", at("tudo em volta") - 0.05, fim("sh_fora"), "pill", anchor="quarto2", dot="#ff8a1f", size=50)
lab("p_rua", "RUA: 35 °C", at("volta") - 0.05, fim("sh_fora"), "pill", anchor="rua", dot="#e0344b", size=50)
lab("st_pra", "PRA ONDE?", at("Não tem") - 0.05, fim("sh_fora"), "sticker", y=430, size=104, rot=-6)
lab("p_bomba", "BOMBA", at("bomba") - 0.05, at("espreme") - 0.1, "pill", anchor="comp", dy=-60, dot="#3b3f4a", size=50)
lab("p_esp", "ESPREMIDO", at("espreme") - 0.05, fim("sh_bomba"), "pill", anchor="pistao", dy=-70, dot="#3d8fe8", size=50)
lab("st_esquenta", "ESQUENTA!", at("esquenta") - 0.05, fim("sh_bomba"), "sticker", y=430, size=104, rot=-6, color="#ff9a3c")
lab("p_pneu", "BOMBA DE PNEU", at("igual") - 0.05, fim("sh_bomba"), "pill", anchor="pneu", dy=-70, dot="#e2453c", size=50)
lab("p_parte2", "PARTE 2: COMPRESSOR", at("parte") - 0.05, DUR, "pill", y=600, dot="#ffd21f", size=48)
lab("st_frio", "COMENTE “FRIO”", at("Comenta") - 0.05, DUR, "big", y=430, size=120, rot=-5)

items.append({"id": "leg", "type": "caption", "track": "legenda", "label": "Legenda (1 palavra por vez)", "by": "template", "start": 0, "dur": DUR,
              "props": {"words": F.words, "mode": "palavra", "size": 96, "y": 1310, "font": "Lilita One", "color": "#ffffff", "stroke": "#1b1b1b", "stroke_k": 0.08, "maxw": 1000}})

edit = {"version": 1, "name": NAME, "grupo": "ESTILOS SHORTS", "estilo": "Lowpoly 3D desmontando",
        "canvas": {"w": 1080, "h": 1920, "fps": 30, "bg": "#cfe9fb"}, "duration": DUR, "template": "local",
        "fonts": {"Lilita One": "fonts/LilitaOne-Regular.ttf"},
        "build_script": "template.html (Three.js + kit low-poly em ../_kit) — gerar_edit.py recria a partir de words.json",
        "referencia": {"canal": "@desmontandoomundo", "canal_url": "https://www.instagram.com/desmontandoomundo/",
                       "video": "https://www.instagram.com/reel/DewJ1whAl3p/", "nota": "3D low-poly de dia; monta o ar-condicionado do zero; legenda 1 palavra; CTA COMENTE FRIO"},
        "audio": {"voice": {"src": "voz.mp3", "volume": 1.0, "start": 0}},
        "tracks": [{"id": "fundo", "name": "Cenas 3D"}, {"id": "rotulos", "name": "Rótulos"}, {"id": "legenda", "name": "Legenda"}],
        "items": items}
json.dump(edit, open(os.path.join(D, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
subprocess.run([sys.executable, os.path.join(D, "..", "_kit", "montar.py"), D], check=True)
print("edit.json ok", DUR, len(items))
