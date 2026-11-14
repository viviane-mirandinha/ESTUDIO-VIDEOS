import json, os
O = os.path.dirname(os.path.abspath(__file__))
FOTO = json.load(open(os.path.join(O, "fotos.json"), encoding="utf-8"))  # chave -> {"src":..., "pos":...}
NAME = "28 - INFOGRAFICO ESCURO DOURADO - Todo navio que já foi o maior do mundo"
DUR = 71.0

def foto(k, **p):
    f = FOTO[k]; d = {"src": f["src"], "pos": f.get("pos", "50% 50%"), "tom": f.get("tom", 0.7)}; d.update(p); return ("kr_foto", d)
def lineup(navios, **p):
    d = {"cabecalho": "PERFIS EM ESCALA", "navios": navios}; d.update(p); return ("kr_lineup", d)
def card(**p): return ("kr_card", p)

GE = {"nome": "GREAT EASTERN", "m": 211, "tipo": "liner", "funis": 5, "mastros": 6, "baixo": True}
LU = {"nome": "LUSITÂNIA", "m": 240, "tipo": "liner", "funis": 4, "mastros": 2}
OT = {"nome": "OLYMPIC / TITANIC", "m": 269, "tipo": "liner", "funis": 4, "mastros": 2}
VA = {"nome": "VATERLAND", "m": 290, "tipo": "liner", "funis": 3, "mastros": 2}
NO = {"nome": "NORMANDIE", "m": 313, "tipo": "liner", "funis": 3, "mastros": 1}
QM = {"nome": "QUEEN MARY", "m": 310, "tipo": "liner", "funis": 3, "mastros": 2}
QE = {"nome": "QUEEN ELIZABETH", "m": 314, "tipo": "liner", "funis": 2, "mastros": 2}
SG = {"nome": "SEAWISE GIANT", "m": 458, "tipo": "tanker"}
IC = {"nome": "ICON OF THE SEAS", "m": 365, "tipo": "cruise"}
PS = {"nome": "PIONEERING SPIRIT", "m": 382, "tipo": "crane"}
def st(n, e): return dict(n, estado=e)

# (inicio, rótulo, cena)
S = [
 (0.0,  "Great Eastern 1858", foto("great_eastern", tag="1858", titulo="GREAT EASTERN", t_titulo=1.8, numero="211 M", t_num=3.4)),
 (4.9,  "40 anos sem rival", card(valor="40", unidade="ANOS", contar=True, t_valor=0.8, sub="NINGUÉM O SUPEROU", t_sub=0.2)),
 (7.2,  "Celtic 1901", foto("celtic", tag="1901", t_tag=0.4, titulo="CELTIC", t_titulo=1.5, sub="O MAIS PESADO DO MUNDO", t_sub=2.6)),
 (11.2, "Lusitânia 240 m", lineup([st(GE, "antigo"), st(LU, "novo")], titulo="· SEIS ANOS DEPOIS", t_titulo=0.1, de=211, valor=240, t_num=2.3)),
 (15.2, "Olympic & Titanic", foto("olympic_titanic", titulo="OLYMPIC & TITANIC", t_titulo=0.4, numero="269 M", t_num=2.5)),
 (18.6, "Empate 269 m", lineup([st(LU, "antigo"), st(OT, "novo")], titulo="· 1911 · 1912", t_titulo=1.1, de=240, valor=269, t_num=0.4, sub="EMPATADOS", t_sub=1.6)),
 (22.2, "Imperator 1913", foto("imperator", titulo="IMPERATOR", t_titulo=0.5, numero="277 M", t_num=1.65, tag="1913", t_tag=3.2)),
 (26.3, "Vaterland 290 m", foto("vaterland", tag="NO ANO SEGUINTE", t_tag=0.2, titulo="VATERLAND", t_titulo=1.6, numero="290 M", t_num=2.8)),
 (30.5, "Normandie 313 m", lineup([st(VA, "antigo"), st(NO, "novo")], titulo="· 1935", t_titulo=2.9, de=290, valor=313, t_num=1.7)),
 (35.1, "Queen Mary 310 m", lineup([st(NO, "antigo"), st(QM, "novo")], de=0, valor=310, t_num=1.3, sub="MAS MAIS PESADA", t_sub=2.6)),
 (38.9, "Queen Elizabeth 1940", foto("queen_elizabeth", titulo="QUEEN ELIZABETH", t_titulo=0.4, numero="314 M", t_num=1.65, tag="1940", t_tag=2.9)),
 (43.2, "Quase 40 anos", card(kicker="QUASE", valor="40", unidade="ANOS", contar=True, t_valor=0.6, sub="DE SILÊNCIO", t_sub=1.5)),
 (45.4, "Seawise Giant", foto("seawise", titulo="SEAWISE GIANT", t_titulo=0.3, numero="458 M", t_num=1.9)),
 (48.9, "Seawise 458 m escala", lineup([st(QE, "antigo"), st(SG, "novo")], de=314, valor=458, t_num=0.1, sub="O MAIOR NAVIO JÁ CONSTRUÍDO", t_sub=0.3, sub2="DESMONTADO EM 2010", t_sub2=2.0)),
 (52.5, "Icon of the Seas", foto("icon", tag="HOJE", t_tag=0.1, titulo="ICON OF THE SEAS", t_titulo=0.8, numero="365 M", t_num=2.1, sub="MAIOR NAVIO DE PASSAGEIROS", t_sub=4.2)),
 (58.6, "Pioneering Spirit 382 m", lineup([st(SG, "fantasma"), st(IC, "antigo"), st(PS, "novo")], de=365, valor=382, t_num=2.0, sub="PIONEERING SPIRIT", t_sub=0.5, sub2="LÍDER EM TONELAGEM", t_sub2=3.9)),
 (63.8, "Registro + CTA", ("kr_registro", {"titulo": "SE GOSTOU DA COMPARAÇÃO, INSCREVA-SE", "t_titulo": 0.3, "titulo2": "QUAL DESSES GIGANTES VOCÊ EMBARCARIA?", "t_titulo2": 2.5, "rodape": "COMENTE", "t_rodape": 5.1,
   "linhas": [{"nome": "GREAT EASTERN", "m": 211}, {"nome": "CELTIC", "nota": "O MAIS PESADO DO MUNDO"}, {"nome": "LUSITÂNIA", "m": 240}, {"nome": "OLYMPIC / TITANIC", "m": 269},
              {"nome": "IMPERATOR", "m": 277}, {"nome": "VATERLAND", "m": 290}, {"nome": "NORMANDIE", "m": 313}, {"nome": "QUEEN MARY", "m": 310}, {"nome": "QUEEN ELIZABETH", "m": 314},
              {"nome": "SEAWISE GIANT", "m": 458}, {"nome": "ICON OF THE SEAS", "m": 365}, {"nome": "PIONEERING SPIRIT", "m": 382}]})),
]
items = []
for i, (t, lab, (sc, par)) in enumerate(S):
    end = (S[i + 1][0] + 0.45) if i + 1 < len(S) else DUR
    items.append({"id": f"s{i+1:02d}", "type": "scene", "track": "fundo", "label": lab, "start": t, "dur": round(end - t, 2),
                  "props": {"scene": sc, "params": par}})
E = {"version": 1, "name": NAME, "estilo": "28-infografico-escuro-dourado", "grupo": "ESTILOS NOVOS",
     "canvas": {"w": 1280, "h": 720, "fps": 30, "bg": "#0d1623"}, "duration": DUR, "template": "generic",
     "fonts": {"Barlow": "fonts/BarlowCondensed-Bold.ttf"},
     "referencia": {"canal": "KNOT & RAIL", "canal_url": "https://www.youtube.com/channel/UC2Rp-Mg68qFRCtDIz89R7BQ", "video": "https://youtu.be/hhLnlTQFcNk",
                    "titulo": "Every Ship That Was the Biggest in the World. Explained",
                    "nota": "Infográfico azul-marinho + dourado: silhuetas em escala crescendo da anterior, número gigante dourado, fotos históricas em sépia com tag mono, cards de tese."},
     "audio": {"voice": {"src": "voz.wav", "volume": 1.0, "start": 0},
               "music": {"src": "musica.mp3", "volume": 0.10, "start": 0, "fade_out": 2.0, "duck": True}, "extra": []},
     "tracks": [{"id": "fundo", "name": "Cenas / mídia"}], "items": items}
json.dump(E, open(os.path.join(O, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok", len(items))
