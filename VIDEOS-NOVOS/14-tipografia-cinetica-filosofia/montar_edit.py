import json, os, unicodedata, re
O = os.path.dirname(os.path.abspath(__file__))
NAME = "14 - TIPOGRAFIA CINETICA FILOSOFIA - Você não controla o que acontece, só a sua resposta"
W = json.load(open(os.path.join(O, "words.json"), encoding="utf-8"))["words"]
DUR = 69.6
def nz(s): return re.sub(r"[^\w]", "", unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode()).lower()
# (texto exibido, destaque, tipo)   tipo: k=kinetic sans, s=serifa centro, se=serifa esquerda (com retrato à direita)
G = [("Você não controla","controla","k"),("o que acontece.","","k"),("Controla apenas","","k"),("a sua resposta.","resposta","k"),
("A maioria das pessoas","","k"),("gasta energia","energia","k"),("lutando contra o vento.","vento","k"),("O estoico","estoico","k"),("ajusta a vela.","vela","k"),
("Epicteto ensinou:","Epicteto","k"),("Há coisas que dependem de nós, e coisas que não dependem.","Epicteto","se"),
("O trânsito,","","k"),("a chuva,","","k"),("a opinião alheia,","","k"),("a doença —","","k"),("tudo isso é externo.","externo","k"),
("Seu julgamento,","julgamento","k"),("sua ação,","ação","k"),("seu silêncio —","silêncio","k"),("isso é interno.","interno","k"),
("Quando você confunde","confunde","k"),("as duas categorias,","","k"),("nasce a ansiedade.","ansiedade","k"),
("Quando você separa,","separa","k"),("nasce a liberdade.","liberdade","k"),
("Imagine perder o emprego.","","s"),("O fato é externo.","externo","k"),("O desespero","desespero","k"),("é uma escolha sua.","escolha","k"),
("A coragem de recomeçar","recomeçar","k"),("também.","","k"),("Marco Aurélio escreveu:","Marco Aurélio","k"),
("Se algo externo te perturba, a dor não vem da coisa, mas do seu julgamento sobre ela.","Marco Aurélio","se"),
("E esse julgamento","julgamento","k"),("você muda agora.","agora","k"),("A vida te dá","","k"),("o cenário.","cenário","k"),("O roteiro é seu.","seu","k"),
("Se você gostou dessa clareza,","clareza","k"),("se inscreva","inscreva","k"),("para treinar a mente todo dia.","mente","k"),
("O controle que você busca","controle","k"),("não está lá fora.","","k"),("Está no próximo pensamento","pensamento","k"),("que você escolher ter.","escolher","k")]
tw = [x for g in G for x in g[0].split() if nz(x)]
assert [nz(x) for x in tw] == [nz(w["w"]) for w in W], "desalinhado"
items = []; i = 0; groups = []
for txt, hl, kind in G:
    ws = [x for x in txt.split() if nz(x)]; ww = W[i:i + len(ws)]; i += len(ws)
    groups.append((txt, hl, kind, ww))
EF = ["scale", "blur", "slide"]
for n, (txt, hl, kind, ww) in enumerate(groups):
    s = max(0, round(ww[0]["s"] - 0.08, 2))
    e = round(groups[n + 1][3][0]["s"] - 0.08, 2) if n + 1 < len(groups) else DUR
    toks = txt.split(); tempos = []; j = 0
    for t in toks:  # travessão herda o tempo da palavra anterior
        if nz(t): tempos.append(round(ww[j]["s"] - s, 2)); j += 1
        else: tempos.append(tempos[-1] if tempos else 0)
    if kind == "k":
        items.append({"id": f"k{n:02d}", "type": "scene", "track": "textos", "label": f"Texto: {txt}", "start": s, "dur": round(e - s, 2),
            "props": {"scene": "kin_grupo", "params": {"texto": txt, "tempos": ",".join(map(str, tempos)), "destaque": hl,
                      "efeito": EF[n % 3], "tamanho": 104, "cor": "#f4f1ea", "cor_destaque": "#e8b547", "y": 360}}})
    else:
        autor = hl if kind == "se" else ""
        items.append({"id": f"q{n:02d}", "type": "scene", "track": "textos", "label": f"Citação: {txt[:30]}", "start": s, "dur": round(e - s, 2),
            "props": {"scene": "kin_serifa", "params": {"texto": txt, "tempos": ",".join(map(str, tempos)), "autor": autor,
                      "alinhar": "esquerda" if kind == "se" else "centro", "tamanho": (74 if len(toks) > 12 else 84) if kind == "se" else 96, "cor": "#f4f1ea", "cor_autor": "#e8b547"}}})
# fundo: (id, inicio, fim, arquivo, trim, label)
B = [("v01",0,4.5,"b01",2,"Tempestade (o que acontece)"),("v02",4.5,8.7,"b02",3,"Vento nas árvores"),("v03",8.7,11.2,"b03",4,"Veleiro (ajusta a vela)"),
     ("v04",16.5,17.6,"b04",1,"Trânsito"),("v05",17.6,18.4,"b05",4,"Chuva na janela"),("v06",18.4,19.7,"b06",2,"Multidão (opinião alheia)"),
     ("v07",19.7,22.2,"b07",1,"Hospital (doença)"),("v08",22.2,26.7,"b08",2,"Silhueta (interno)"),("v09",26.7,31.2,"b09",2,"Homem ansioso"),
     ("v10",31.2,34.2,"b10",3,"Pássaros (liberdade)"),("v12",37.8,40.2,"b12",3,"Homem desesperado"),("v13",40.2,42.4,"b13",3,"Nascer do sol (recomeçar)"),
     ("v17",50.1,53.2,"b17",2,"Caminhando (muda agora)"),("v14",53.2,57.3,"b14",1,"Cortina de teatro (cenário)"),("v15",57.3,62.5,"b15",3,"Mar (treinar a mente)"),
     ("v16",62.5,DUR,"b16",2,"Homem diante do mar (final)")]
for vid, s, e, f, tr, lb in B:
    items.append({"id": vid, "type": "video", "track": "fundo", "label": lb, "start": s, "dur": round(min(e + 0.4, DUR) - s, 2), "in": "fade" if s > 0 else "none",
                  "props": {"src": f"clips/{f}.mp4", "fill": True, "fit": "cover", "trim": tr, "volume": 0, "speed": 1, "opacity": 0.55, "motion": "zoom_in", "motion_amount": 0.06}})
for iid, s, e, src, lb in [("i01", 11.1, 16.9, "img/epicteto.jpg", "Epicteto (gravura 1715)"), ("i02", 42.4, 50.5, "img/marco.jpg", "Marco Aurélio (busto, Munique)")]:
    items.append({"id": iid, "type": "image", "track": "fundo", "label": lb, "start": s, "dur": round(e - s, 2), "in": "fade", "out": "fade",
                  "props": {"src": src, "fit": "cover", "x": 1010, "y": 360, "w": 540, "h": 720, "opacity": 0.6, "motion": "zoom_in", "motion_amount": 0.07}})
GRAIN = ("background-image:url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='256' height='256'>"
         "<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/></filter>"
         "<rect width='256' height='256' filter='url(%23n)'/></svg>\")")
items.append({"id": "grade", "type": "html", "track": "grade", "label": "Vinheta + grão", "start": 0, "dur": DUR,
    "props": {"x": 640, "y": 360, "w": 1280, "h": 720, "html": "<div class='vg'></div><div class='gr'></div>",
              "css": ".vg{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 50%,rgba(0,0,0,0) 35%,rgba(0,0,0,.85) 100%)}"
                     ".gr{position:absolute;inset:0;opacity:.12;mix-blend-mode:screen;" + GRAIN + "}"}})
edit = {
    "version": 1, "name": NAME, "estilo": "14-tipografia-cinetica-filosofia", "grupo": "ESTILOS NOVOS",
    "canvas": {"w": 1280, "h": 720, "fps": 30, "bg": "#000000"}, "duration": DUR, "template": "generic",
    "fonts": {"Montserrat": "fonts/Montserrat-Black.ttf", "Cormorant": "fonts/CormorantGaramond.ttf"},
    "referencia": {"canal": "Pursuit of Wonder", "canal_url": "https://www.youtube.com/@PursuitofWonder", "video": "https://youtu.be/jDU6kdoBegc",
                   "titulo": "The Andromeda Paradox: A Theory That Proves Your Future Self Already Exists",
                   "nota": "Tipografia cinética sobre preto/b-roll escuro dessaturado (Pursuit of Wonder + canais stoic): 1-4 palavras por vez sincronizadas ao whisper, destaque dourado, citações em serifa com autor (Einzelgänger), piano baixo."},
    "audio": {"voice": {"src": "voz.wav", "volume": 1.0, "start": 0},
              "music": {"src": "musica.mp3", "volume": 0.12, "start": 0, "fade_out": 2.5, "duck": True}, "extra": []},
    "tracks": [{"id": "fundo", "name": "B-roll / retratos"}, {"id": "grade", "name": "Vinheta + grão"}, {"id": "textos", "name": "Tipografia"}],
    "items": items,
}
json.dump(edit, open(os.path.join(O, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("itens", len(items), "grupos", len(groups))
