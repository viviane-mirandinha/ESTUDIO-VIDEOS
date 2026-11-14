# Gera edit.json do short 08 (dados ranking escuro amarelo, política). TODO tempo vem de words.json (trocar voz = whisper + rodar de novo).
import json, os, re, unicodedata, difflib
from PIL import Image
D = os.path.dirname(os.path.abspath(__file__))
NAME = "08 - DADOS RANKING ESCURO - Votar contra o Lula nao e torcer por ninguem"
WJ = json.load(open(os.path.join(D, "words.json"), encoding="utf-8"))
RAW = WJ["words"]
DUR = round(WJ["duration"] + 0.8, 2)
ROT = open(os.path.join(D, "roteiro.txt"), encoding="utf-8").read().strip()

W = []
for w in RAW:
    if W and re.match(r"^([.,]\d|%)", w["w"]):
        W[-1] = {"w": W[-1]["w"] + w["w"], "s": W[-1]["s"], "e": w["e"]}
    else:
        W.append(dict(w))

def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return re.sub(r"[^\w%]", "", "".join(c for c in s if unicodedata.category(c) != "Mn")).replace("_", "")

NUM = {"20": "vinte", "4": "quatro"}
def at(palavra, oc=1, depois=0.0):
    """início da palavra (oc-ésima ocorrência a partir de `depois`)"""
    alvo, k = norm(palavra), 0
    alts = {alvo} | {norm(v) for kk, v in NUM.items() if norm(kk) == alvo} | {norm(kk) for kk, v in NUM.items() if norm(v) == alvo}
    for w in W:
        if w["s"] < depois - 0.01:
            continue
        n = norm(w["w"])
        if n in alts or (len(alvo) > 3 and n.startswith(alvo)):
            k += 1
            if k == oc:
                return w["s"]
    raise SystemExit(f"palavra não achada: {palavra} #{oc} depois de {depois}")

def ar(f):
    with Image.open(os.path.join(D, f)) as im:
        return round(im.width / im.height, 3)

def fit(txt, tam, maxw=960):  # Oswald bold caixa-alta ~0.5 em por letra
    return int(min(tam, maxw / (0.5 * max(1, len(txt)))))

items = []
def scene(nome, s, e, params, label):
    items.append({"id": f"sc{len(items)}", "type": "scene", "track": "visual", "label": label, "start": round(s, 2), "dur": round(e - s, 2),
                  "props": {"scene": nome, "params": params}})
def L(txt, t, cor="#ffffff", tam=150, caixa=False):
    d = {"txt": txt, "t": round(t, 2), "cor": cor, "tam": fit(txt, tam)}
    if caixa:
        d["caixa"] = True; d["tam"] = fit(txt, tam, 900)
    return d

AM = "#F5C518"
def moldura(s, e, img, titulo, sub, t_tit, t_img=None, t_sub=0, label="", **kw):
    p = {"titulo": titulo, "sub": sub, "t_tit": round(t_tit, 2), "img": img, "ar": ar(img), "t_img": round(t_img if t_img else s + .05, 2)}
    if t_sub: p["t_sub"] = round(t_sub, 2)
    p.update(kw); scene("dr_moldura", s, e, p, label or titulo)
def manchetes(s, e, imgs, titulo, sub, t_tit, t0, passo=.38, t_sub=0, label=""):
    p = {"titulo": titulo, "sub": sub, "t_tit": round(t_tit, 2), "imgs": [{"src": f, "ar": ar(f), "t": round(t0 + i * passo, 2)} for i, f in enumerate(imgs)]}
    if t_sub: p["t_sub"] = round(t_sub, 2)
    scene("dr_moldura", s, e, p, label or titulo)
def frase(s, e, linhas, label, **kw):
    p = {"frase": linhas}; p.update(kw); scene("dr_moldura", s, e, p, label)

# ---- cortes (início de cada frase)
c = {}
c["mas"] = at("Mas") - .15
c["entao"] = at("Então") - .2
c["fem"] = at("Eu", 1, c["entao"]) - .15
c["est"] = at("Eu", 1, at("feminicídio")) - .15
c["veg"] = at("Eu", 1, at("estatais")) - .15
c["ama"] = at("Tem") - .2
c["conv"] = at("Conveniente") - .2
c["olha"] = at("Mas", 1, at("Conveniente")) - .15
c["fac"] = at("Eu", 1, at("olha")) - .15
c["jur"] = at("Eu", 1, at("Vermelho")) - .15
c["imp"] = at("Eu", 1, at("juro")) - .15
c["gas"] = at("gasta") - .15
c["cade"] = at("Aí") - .15
c["cor"] = at("Eu", 1, at("dinheiro")) - .15
c["emp"] = at("Eu", 1, at("impunidade")) - .15
c["pior"] = at("pior") - .45
c["stf"] = at("Os") - .2
c["pt"] = at("Eu", 1, at("ele")) - .15
c["arv"] = at("Uma") - .2
c["planta"] = at("Só", 1, at("sombra")) - .15

# 1 voto contra o Lula
scene("dr_numero", 0, c["mas"], {"rotulo": "Meu voto", "foto": "img/lula.jpg", "valor": "CONTRA", "tam": 230, "unidade": "o Lula",
                                 "t_rot": 0.05, "t_valor": at("contra")}, "voto contra o Lula")
# 2 não torço por Flávio nem Bolsonaro
frase(c["mas"], c["entao"], [L("FLÁVIO", at("Flávio"), "#ffffff", 200), L("NEM", at("nem"), AM, 120), L("BOLSONARO", at("Bolsonaro"), "#ffffff", 200)],
      "não torço por Flávio nem Bolsonaro", titulo="NÃO TORÇO POR", t_tit=round(c["mas"] + .05, 2),
      bgimg="img/flavio.jpg", bg_fit="topo", bg_top=230, bg_op=.38)
# 3 por quê? pensa comigo
frase(c["entao"], c["fem"], [L("POR QUÊ?", at("por", 1, c["entao"]), AM, 240), L("PENSA COMIGO", at("Pensa"), "#ffffff", 120)], "por quê?",
      bgimg="img/01_feminicidio.jpg", bg_op=.24)
# 4-6 recortes
moldura(c["fem"], c["est"], "img/01_feminicidio.jpg", "FEMINICÍDIO", "aumentando", at("feminicídio") - .1, t_sub=at("aumentando"))
moldura(c["est"], c["veg"], "img/02_estatais.jpg", "ESTATAIS", "prejuízo recorde", at("estatais") - .1, t_sub=at("prejuízo"))
moldura(c["veg"], c["ama"], "img/03_queimadas.jpg", "QUEIMADAS", "vegetação pegando fogo", at("vegetação") - .1, t_sub=at("pegando"))
# 7 Amazônia (sem recorte: queimadas escurecido + tipografia)
frase(c["ama"], c["conv"], [L("SÓ QUANDO", at("quando"), "#ffffff", 170), L("O ANO VIRAR", at("ano", 1, at("quando")), AM, 170)], "Amazônia",
      titulo="AMAZÔNIA", t_tit=round(at("Amazônia") - .1, 2), bgimg="img/03_queimadas.jpg", bg_op=.28)
# 8 conveniente, né?
frase(c["conv"], c["olha"], [L("CONVENIENTE,", at("Conveniente"), AM, 170), L("NÉ?", at("né"), "#ffffff", 200)], "conveniente",
      bgimg="img/03_queimadas.jpg", bg_op=.24)
# 9 olha só o que vem agora
frase(c["olha"], c["fac"], [L("OLHA SÓ", at("olha"), "#ffffff", 140), L("O QUE VEM AGORA", at("vem", 1, at("olha")), AM, 140)], "o que vem agora", escurecer=.75)
# 10 facções: b-roll + manchete
items.append({"id": "br_fac", "type": "video", "track": "midia", "label": "b-roll facções", "start": round(c["olha"], 2), "dur": round(c["jur"] - c["olha"], 2),
              "in": "fade", "out": "none", "props": {"src": "img/04_faccoes_lento.mp4", "fill": True, "fit": "cover", "volume": 0}})
moldura(c["fac"], c["jur"], "img/05_faccoes_oglobo_manchete.jpg", "FACÇÕES", "PCC e Comando Vermelho", at("mão") - .2, t_img=at("PCC"),
        t_sub=at("PCC"), escurecer=.6, area_top=600, area_h=760)
# 11-13 juros / impostos / gastos
moldura(c["jur"], c["imp"], "img/06_juros.jpg", "JUROS", "maior juro real do mundo", at("endividada") - .1, t_sub=at("maior"))
moldura(c["imp"], c["gas"], "img/07_impostos.jpg", "IMPOSTOS", "cobra mais imposto", at("cobra") - .1, t_sub=at("imposto"))
moldura(c["gas"], c["cade"], "img/08_gastos.jpg", "GASTOS", "até quebrar o país", at("gasta") - .05, t_sub=at("quebrar"))
# 14 cadê o dinheiro?
frase(c["cade"], c["cor"], [L("AÍ ME EXPLICA", at("Aí"), "#ffffff", 110), L("CADÊ O", at("cadê"), AM, 190), L("DINHEIRO?", at("dinheiro"), AM, 190, caixa=True)], "cadê o dinheiro",
      bgimg="img/09_corrupcao.jpg", bg_op=.22)
# 15 corrupção: manchetes empilhadas
manchetes(c["cor"], c["emp"], [f"img/09_corrupcao_{x}.jpg" for x in "abcde"], "CORRUPÇÃO", "e impunidade", at("corrupção") - .1,
          c["cor"] + .15, .4, t_sub=at("impunidade"))
# 16 empresas
moldura(c["emp"], c["pior"], "img/10_empresas.jpg", "EMPRESAS", "morrendo", at("empresa") - .1, t_sub=at("morrendo"))
# 17 o pior vem agora
frase(c["pior"], c["stf"], [L("O PIOR", at("pior"), AM, 240), L("VEM AGORA", at("vem", 1, at("pior")), "#ffffff", 150)], "o pior vem agora",
      bgimg="img/11_stf.jpg", bg_op=.25)
# 18 4 ministros do STF
scene("dr_numero", c["stf"], c["pt"], {"rotulo": "Os próximos", "foto": "img/lula.jpg", "valor": "4", "tam": 300, "unidade": "ministros",
                                       "sub": "do STF · escolhidos por ele", "t_rot": round(c["stf"] + .1, 2), "t_valor": at("quatro"), "t_sub": at("STF")}, "4 ministros STF")
# 19 STF manchetes
manchetes(c["pt"], c["arv"], [f"img/11_stf_{x}.jpg" for x in "abc"], "STF", "mais ao PT do que ao Brasil", c["pt"] + .1, c["pt"] + .1, .45, t_sub=at("PT"))
# 20 árvore de 20 anos
moldura(c["arv"], c["planta"], "img/12_arvore.jpg", "20 ANOS", "já devia dar sombra", at("20") - .1, t_img=c["arv"] + .05, t_sub=at("devia"))
# 21 não tô falando de planta
frase(c["planta"], DUR, [L("NÃO TÔ FALANDO", at("não", 1, c["planta"]), "#ffffff", 140), L("DE PLANTA.", at("planta"), AM, 170, caixa=True)],
      "não tô falando de planta", bgimg="img/13_arvore_lula_chapeu.jpg", bg_fit="topo", bg_top=250, bg_op=.42, area_top=800, area_h=440)

# ---- legenda-frase (texto exato do roteiro), palavras-chave amarelas
KW = ["contra o Lula", "Flávio", "Bolsonaro", "feminicídio", "estatais", "prejuízo recorde", "vegetação", "fogo", "Amazônia", "Conveniente",
      "PCC", "Comando Vermelho", "endividada", "maior juro real do mundo", "imposto", "sem responsabilidade", "cadê o dinheiro", "corrupção",
      "impunidade", "empresa morrendo", "o pior", "quatro ministros", "STF", "PT", "Brasil", "árvore de vinte anos", "sombra", "planta"]
sent = re.split(r"(?<=[.?!])\s+", ROT)
parts = []
for s in sent:
    if len(s) > 70 and ", " in s:
        cs = [m.start() for m in re.finditer(", ", s)]
        k = min(cs, key=lambda x: abs(x - len(s) / 2))
        parts += [s[:k + 1], s[k + 1:].strip()]
    elif len(s) > 70:  # quebra no espaço mais perto do meio
        cs = [m.start() for m in re.finditer(" ", s)]
        k = min(cs, key=lambda x: abs(x - len(s) / 2))
        parts += [s[:k], s[k + 1:]]
    else:
        parts.append(s)
RW = [x for p in parts for x in p.split()]
sm = difflib.SequenceMatcher(None, [norm(x) for x in RW], [norm(w["w"]) for w in W], autojunk=False)
mp = {}
for a, b, n in sm.get_matching_blocks():
    for j in range(n):
        mp[a + j] = b + j
def wi(r, d):
    while r not in mp and 0 <= r < len(RW):
        r += d
    return mp.get(r, 0 if d > 0 else len(W) - 1)
i = 0; caps = []
for p in parts:
    n = len(p.split())
    caps.append((p, W[wi(i, 1)]["s"], W[wi(i + n - 1, -1)]["e"])); i += n
for k, (p, s, e) in enumerate(caps):
    fim = caps[k + 1][1] - .05 if k + 1 < len(caps) else DUR
    hl = [x for x in KW if x.lower() in p.lower()]
    items.append({"id": f"lg{k}", "type": "text", "track": "legenda", "label": p[:30], "start": round(max(0, s - .08), 2), "dur": round(fim - max(0, s - .08), 2),
                  "in": "fade", "out": "none", "props": {"text": p, "x": 540, "y": 1340, "w": 960, "size": 56, "color": "#ffffff", "font": "Inter", "weight": 700,
                  "align": "center", "shadow": True, "highlight": hl, "hl_color": AM, "line": 1.25}})

bg = {"id": "bg", "type": "html", "track": "fundo", "label": "fundo preto", "start": 0, "dur": DUR,
      "props": {"fill": True, "html": "<div class='drbg'></div>",
                "css": ".drbg{width:100%;height:100%;background:radial-gradient(ellipse at 50% 35%,#151517 0%,#0B0B0C 65%)}"}}
edit = {"version": 1, "name": NAME, "canvas": {"w": 1080, "h": 1920, "fps": 30, "bg": "#0B0B0C"}, "duration": DUR, "template": "generic",
        "grupo": "ESTILOS SHORTS", "estilo": "Dados ranking escuro amarelo",
        "referencia": {"canal": "@nikolasferreiradm", "canal_url": "https://www.instagram.com/nikolasferreiradm/",
                       "video": "https://www.instagram.com/p/De0HLIExn-n/", "nota": "formato preto/amarelo do short 06 + recortes de gráficos/manchetes da referência em moldura amarela; sem logo/@ do perfil"},
        "fonts": {"Inter": "fonts/Inter.ttf", "Oswald": "fonts/Oswald-Bold.ttf"},
        "audio": {"voice": {"src": "voz.mp3", "volume": 1.0, "start": 0}},
        "tracks": [{"id": "fundo", "name": "Fundo"}, {"id": "midia", "name": "B-roll"}, {"id": "visual", "name": "Gráficos"}, {"id": "legenda", "name": "Legenda"}],
        "items": [bg] + items}
json.dump(edit, open(os.path.join(D, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("cenas", {k: round(v, 2) for k, v in c.items()})
print("legendas", len(caps), "dur", DUR, "palavras roteiro", len(RW), "whisper", len(W))
