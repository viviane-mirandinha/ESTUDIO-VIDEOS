"""Gera edit.json do short 05 — TODO tempo sai do words.json (whisper) via at()."""
import json, os, sys, subprocess
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, D)
from alinhar import Falas
F = Falas(D, os.path.join(D, "..", "..", "ROTEIROS-SHORTS", "05 - *.txt"))
at = F.at
NAME = "05 - CIDADE LOWPOLY SEGUIDORES - Cada seguidor ganha uma casa"
DUR = round(F.dur_audio + 0.5, 2)

items = [{"id": "cor_rotulo", "type": "param", "label": "Cor dos rótulos", "props": {"value": "#ffd21f"}}]
def shot(i, a, b, label):
    items.append({"id": i, "type": "html", "track": "fundo", "label": label, "by": "template", "start": round(a, 2), "dur": round(b - a, 2), "props": {"html": ""}})
def lab(i, txt, a, b, kind="tag", **p):
    items.append({"id": i, "type": "text", "track": "rotulos", "label": txt[:30], "by": "template", "start": round(a, 2), "dur": round(b - a, 2),
                  "props": dict(text=txt, kind=kind, **p)})

tQ, tV, tP, tR = at("Quem"), at("Tá"), at("Por enquanto"), at("Pra virar")
tY, tC, tG, tF = at("Você"), at("Cada seguidor", 2), at("A cidade cresce"), at("Então")
shot("sh_abre", 0, tQ, "3D: prefeitura (abertura)")
shot("sh_quem", tQ, tV, "3D: morador no tapete")
shot("sh_vazia", tV, tP, "3D: lotes vazios (de cima)")
shot("sh_pref", tP, tR, "3D: prefeitura + seguranças")
shot("sh_rua", tR, tY, "3D: drone desce na rua")
shot("sh_voce", tY, tC, "3D: casa branca vazia")
shot("sh_casa", tC, tG, "3D: casa / rua / número")
shot("sh_cresce", tG, tF, "3D: cidade cresce")
shot("sh_fim", tF, DUR, "3D: cidade enorme (afasta)")

lab("st_titulo", "1 SEGUIDOR = 1 CASA", 0.15, tQ - 0.05, "sticker", y=420, size=88, rot=-4)
lab("tg_morador1", "MORADOR Nº 1?", at("primeiro") - 0.1, tV - 0.05, "tag", anchor="morador", dy=-60, size=60)
lab("st_vazia", "MEIO VAZIA...", at("vazia") - 0.1, tP - 0.05, "sticker", y=430, size=96, rot=-3)
lab("tg_morador", "1 MORADOR", at("morador", 2) - 0.1, tR - 0.05, "tag", anchor="morador", dy=-230, size=56)
lab("tg_pref", "PREFEITURA VAZIA", at("prefeitura") - 0.1, tR - 0.05, "tag", anchor="prefeitura", dy=-40, size=56)
lab("tg_seg", "SEGURANÇAS", at("seguranças") - 0.1, tR - 0.05, "tag", anchor="seguranca", dx=-150, dy=-10, size=56)
lab("st_falta", "FALTA UMA COISA...", at("falta") - 0.1, tY - 0.05, "sticker", y=430, size=84, rot=-3)
lab("st_voce", "VOCÊ!", tY - 0.05, tC - 0.05, "big", y=560, size=190, rot=-6)
lab("tg_casa", "CASA", at("casa", 2) - 0.1, tG + 0.3, "tag", anchor="casa", dx=-260, dy=-120, size=64)
lab("tg_rua", "RUA", at("rua") - 0.1, tG + 0.3, "tag", anchor="casa", dx=-260, dy=-20, size=64)
lab("tg_num", "NÚMERO", at("número") - 0.1, tG + 0.3, "tag", anchor="casa", dx=-260, dy=80, size=64)
lab("st_cresce", "CRESCE TODO DIA", at("cresce") - 0.1, at("comentário") - 0.1, "sticker", y=430, size=84, rot=-3)
card = ("<div style=\"width:800px;background:#fff;border-radius:28px;padding:26px 32px;box-shadow:0 14px 40px rgba(0,0,0,.35);"
        "font-family:'Montserrat',sans-serif;color:#1d2330;border:5px solid #1b1b1b\">"
        "<div style=\"display:flex;align-items:center;gap:20px\"><div style=\"width:84px;height:84px;border-radius:50%;background:#ffd21f;border:4px solid #1b1b1b\"></div>"
        "<div><div style=\"font-size:34px;font-weight:800;color:#6b7280\">COMENTÁRIO MAIS CURTIDO</div>"
        "<div style=\"font-size:46px;font-weight:800\">“Constrói um estádio!”</div></div></div>"
        "<div style=\"margin-top:14px;font-size:40px;font-weight:800;color:#e0344b\">&#9829; 2.481 curtidas</div></div>")
lab("card_coment", "comentário mais curtido", at("comentário") - 0.1, tF - 0.05, "html", html=card, y=470)
lab("tg_amanha", "DECIDE A OBRA DE AMANHÃ", at("decide") - 0.1, tF - 0.05, "tag", y=740, size=56)
lab("st_fim", "QUEM SE MUDA PRIMEIRO?", tF - 0.05, DUR, "sticker", y=430, size=84, rot=-3)
lab("tg_sua", "SUA CASA?", at("mudar") - 0.1, DUR, "tag", anchor="pin", dy=-90, size=60)

items.append({"id": "leg", "type": "caption", "track": "legenda", "label": "Legenda (frase inteira)", "by": "template", "start": 0, "dur": DUR,
              "props": {"words": F.words, "mode": "frase", "per_group": 7, "size": 60, "y": 1250, "font": "Montserrat", "weight": 800,
                        "color": "#ffffff", "stroke": "#000000", "stroke_k": 0.09, "maxw": 960}})

edit = {"version": 1, "name": NAME, "grupo": "ESTILOS SHORTS", "estilo": "Cidade lowpoly seguidores",
        "canvas": {"w": 1080, "h": 1920, "fps": 30, "bg": "#cfe9fb"}, "duration": DUR, "template": "local",
        "fonts": {"Lilita One": "fonts/LilitaOne-Regular.ttf", "Montserrat": "fonts/Montserrat-ExtraBold.ttf"},
        "build_script": "template.html (Three.js + kit low-poly; câmera e cidade em renderAt) — gerar_edit.py recria a partir de words.json",
        "referencia": {"canal": "@homietown.city", "canal_url": "https://www.instagram.com/homietown.city/",
                       "video": "https://www.instagram.com/reel/Derns2LOquU/", "nota": "cidade isométrica low-poly; 1 seguidor = 1 casa; drone prefeitura -> casa -> cidade"},
        "audio": {"voice": {"src": "voz.mp3", "volume": 1.0, "start": 0}},
        "tracks": [{"id": "fundo", "name": "Cenas 3D"}, {"id": "rotulos", "name": "Rótulos"}, {"id": "legenda", "name": "Legenda"}],
        "items": items}
json.dump(edit, open(os.path.join(D, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
subprocess.run([sys.executable, os.path.join(D, "..", "_kit", "montar.py"), D], check=True)
print("edit.json ok", DUR, len(items))
