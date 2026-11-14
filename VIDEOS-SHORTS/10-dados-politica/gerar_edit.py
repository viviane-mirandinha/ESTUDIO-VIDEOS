# Gera edit.json do short 10 (dados ranking escuro amarelo, política). TODO tempo vem de words.json (trocar voz = whisper + rodar de novo).
import json, os, re, unicodedata, difflib
D = os.path.dirname(os.path.abspath(__file__))
NAME = "10 - DADOS RANKING ESCURO - Ouve o que falaram do Nordeste"
WJ = json.load(open(os.path.join(D, "words.json"), encoding="utf-8"))
W = WJ["words"]
DUR = round(WJ["duration"] + 0.6, 2)
ROT = open(os.path.join(D, "roteiro.txt"), encoding="utf-8").read().strip()
AM, BR, VM = "#F5C518", "#ffffff", "#E02424"

def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return re.sub(r"[^\w%]", "", "".join(c for c in s if unicodedata.category(c) != "Mn")).replace("_", "")

def _find(palavra, oc, depois):
    alts = palavra if isinstance(palavra, list) else [palavra]
    alvos, k = [norm(a) for a in alts], 0
    for w in W:
        if w["s"] < depois:
            continue
        n = norm(w["w"])
        if any(n == a or (len(a) > 3 and n.startswith(a)) for a in alvos):
            k += 1
            if k == oc:
                return w
    raise SystemExit(f"palavra não achada: {palavra} #{oc} depois de {depois}")

def at(p, oc=1, depois=0.0): return _find(p, oc, depois)["s"]
def fim(p, oc=1, depois=0.0): return _find(p, oc, depois)["e"]

items = []
def add(it): items.append(it); return it
def scene(nome, s, e, params, label, track="visual"):
    add({"id": f"sc{len(items)}", "type": "scene", "track": track, "label": label, "start": round(s, 2), "dur": round(e - s, 2),
         "props": {"scene": nome, "params": params}})
def palavra(s, e, linhas, label, y=820, rotulo="", t_rot=0):
    # sem buraco preto: a 1ª linha gigante entra junto com a cena (colada no fim da cena anterior)
    linhas = [(t, c, z, min(tt, s + .05) if k == 0 else tt) for k, (t, c, z, tt) in enumerate(linhas)]
    t_rot = min(t_rot, s + .05) if t_rot else t_rot
    scene("dr_palavra", s, e, {"rotulo": rotulo, "t_rot": t_rot, "y": y, "zoom": 1.04,
                               "linhas": [{"txt": t, "cor": c, "tam": z, "t": round(tt, 2)} for t, c, z, tt in linhas]}, label)

# ---- cortes (início de cada bloco)
B = {}
B["q1"] = at(["Ouve", "Ouvi"], 1, 1.5) - .2
B["r1"] = at("Preguiçoso", 2) - .15
B["r2"] = at("Eu") - .15
B["r3"] = at("Mas") - .15
B["q2"] = at("Escuta") - .2
B["r4"] = at("Isso", 1, at("arara")) - .15
B["q3"] = at("Agora") - .2
B["r5"] = at("Câncer", 2) - .15
B["r5b"] = at("Nordeste", 1, B["r5"]) - .4
B["q4"] = at("Tem") - .2
B["r6"] = at("vergonha", 2) - .15
B["q5"] = at("esta") - .3
B["r7"] = at("Inferiores", 2) - .15
B["r8"] = at("Nordeste", 1, at("Nunca")) - .45
B["r9"] = at("Essas") - .15
B["r10"] = at("tenho") - .35
B["r11"] = at("Quem", 1, B["r10"]) - .15
B["r12"] = at("Proteja") - .15
B["r13"] = at("Vote") - .15
ordem = sorted(B.items(), key=lambda kv: kv[1])
def nxt(k):
    ks = [x for x, _ in ordem]
    i = ks.index(k)
    return ordem[i + 1][1] if i + 1 < len(ordem) else DUR

# ---- grade 3x2 (gancho e "foram ditas")
CW, CH, GX = 316, 380, [206, 540, 874]
def grade(s, e, srcs, ys, cor, borda, pref, video=False, stagger=.1):
    cells = [(x, y) for y in ys for x in GX]
    for k, ((x, y), src) in enumerate(zip(cells, srcs)):
        st = s + k * stagger
        it = {"id": f"{pref}{k}", "type": "video" if video else "image", "track": "clipe", "label": f"{pref} {k + 1}", "start": round(st, 2),
              "dur": round(e - st, 2), "in": "pop", "out": "fade",
              "props": {"src": src, "x": x, "y": y, "w": CW - 2 * borda, "h": CH - 2 * borda, "fit": "cover",
                        "motion": "zoom_in", "motion_amount": .08}}
        if video:
            it["props"].update({"volume": 0, "speed": 1})
        else:
            it["props"]["radius"] = 10
        add(it)
    cel = "".join(f"<div style='position:absolute;left:{x - CW // 2}px;top:{y - CH // 2}px;width:{CW}px;height:{CH}px;"
                  f"box-sizing:border-box;border:{borda}px solid {cor};border-radius:14px'></div>" for x, y in cells[:len(srcs)])
    add({"id": f"{pref}b", "type": "html", "track": "tag", "label": f"{pref} molduras", "start": round(s, 2), "dur": round(e - s, 2),
         "in": "fade", "out": "fade", "props": {"fill": True, "html": cel, "css": ""}})

# ---- citações: card borda vermelha + "OUVE ISSO:" + clipe mudo + citação em aspas
CY, CARD_W, CARD_H = 700, 640, 760
CITS = [  # (bloco, clipe, palavra inicial, palavra final)
    ("q1", "clips/11_20.1s_viver-da-migalha.mp4", "Nordestino", "migalha"),
    ("q2", "clips/16_30.4s_cheio-pau-arara.mp4", "Cheio", "aqui"),
    ("q3", "clips/20_34.3s_bahia-cancer-brasil.mp4", "Bahia", "Brasil"),
    ("q4", "clips/25_43.1s_vergonha-pro-brasil.mp4", "Vocês", "Brasil"),
    ("q5", "clips/28_49.8s_inferiores-outras-regioes.mp4", "falta", "inferiores"),
]
CDUR = {"clips/11_20.1s_viver-da-migalha.mp4": 2.23, "clips/16_30.4s_cheio-pau-arara.mp4": 1.0, "clips/20_34.3s_bahia-cancer-brasil.mp4": 1.37,
        "clips/25_43.1s_vergonha-pro-brasil.mp4": 1.5, "clips/28_49.8s_inferiores-outras-regioes.mp4": 2.3}
QTXT = re.findall(r'"([^"]+)"', ROT)  # texto exato das 5 citações
QS = {}
for n, (b, clip, w0, w1) in enumerate(CITS, 1):
    s, e = B[b], nxt(b)
    qs = at(w0, 1, s) - (.2 if b == "q3" else 0)
    qe = fim(w1, 1, qs)
    QS[b] = qs
    add({"id": f"q{n}card", "type": "html", "track": "card", "label": f"card citação {n}", "start": round(s, 2), "dur": round(e - s, 2),
         "in": "zoom", "out": "fade", "props": {"x": 540, "y": CY, "w": CARD_W, "h": CARD_H, "html": "<div class='cardq'></div>",
         "css": f".cardq{{width:100%;height:100%;box-sizing:border-box;border:8px solid {VM};border-radius:24px;background:#000;"
                f"box-shadow:0 0 60px rgba(224,36,36,.35)}} #q{n}v_mv{{border-radius:16px}}"}})
    box = {"x": 540, "y": CY, "w": CARD_W - 20, "h": CARD_H - 20, "fit": "cover"}
    sp = max(.6, min(1.0, CDUR[clip] / max(.3, qe - qs)))
    vd = min(CDUR[clip] / sp, e - qs)
    if qs - s > .1:
        add({"id": f"q{n}a", "type": "image", "track": "clipe", "label": f"clipe {n} (antes)", "start": round(s, 2), "dur": round(qs - s, 2),
             "in": "zoom", "out": "none", "props": dict(box, src=f"img/q{n}_a.jpg", radius=16)})
    add({"id": f"q{n}v", "type": "video", "track": "clipe", "label": f"clipe {n} (mudo)", "start": round(qs, 2), "dur": round(vd, 2),
         "in": "none", "out": "none", "props": dict(box, src=clip, volume=0, speed=round(sp, 2), trim=0)})
    if e - (qs + vd) > .05:
        add({"id": f"q{n}b", "type": "image", "track": "clipe", "label": f"clipe {n} (depois)", "start": round(qs + vd, 2), "dur": round(e - qs - vd, 2),
             "in": "none", "out": "fade", "props": dict(box, src=f"img/q{n}_b.jpg", radius=16, motion="zoom_in", motion_amount=.05)})
    add({"id": f"q{n}tag", "type": "text", "track": "tag", "label": f"OUVE ISSO {n}", "start": round(s + .1, 2), "dur": round(e - s - .1, 2),
         "in": "slide_up", "out": "fade", "props": {"text": "OUVE ISSO:", "x": 540, "y": CY - CARD_H // 2, "size": 56, "color": "#ffffff",
         "font": "Oswald", "weight": 700, "bg": VM, "pad": 14, "radius": 10, "shadow": False, "align": "center"}})
    add({"id": f"q{n}txt", "type": "html", "track": "legenda", "label": f"citação {n}", "start": round(qs - .08, 2), "dur": round(e - qs + .08, 2),
         "in": "fade", "out": "fade", "props": {"x": 540, "y": 1290, "w": 980, "h": 380,
         "html": f"<div class='qt'><div class='qm'>&ldquo;</div><div class='qx'>{QTXT[n - 1]}<span class='qe'>&rdquo;</span></div></div>",
         "css": f".qt{{width:100%;height:100%;display:flex;flex-direction:column;align-items:center;text-align:center}}"
                f".qm{{font:700 200px/1 Oswald,serif;color:{AM};height:105px;overflow:visible}}"
                f".qx{{font-family:Inter,sans-serif;font-weight:800;font-style:italic;font-size:66px;line-height:1.16;color:#fff}}"
                f".qe{{color:{AM};font-family:Oswald,serif;font-style:normal}}"}})

# ---- gancho: grade de clipes mudos + NORDESTE gigante
grade(0, B["q1"], ["clips/22_36.6s_presidio-pedrinhas.mp4", "clips/13_24.5s_meninas-nordeste.mp4", "clips/10_17.3s_dez-filhos-estado.mp4",
                   "clips/23_39.0s_maranhao-cabecudo.mp4", "clips/27_47.1s_taxa-analfabetismo.mp4", "clips/12_22.3s_bolsa-familia.mp4"],
      [455, 855], "#3a3a3f", 5, "hk", video=True, stagger=.06)
palavra(.05, B["q1"], [("NORDESTE", AM, 200, at("Nordeste"))], "gancho NORDESTE", y=1165)

# ---- respostas do narrador: tipografia gigante amarelo/branco
palavra(B["r1"], B["r2"], [("PREGUIÇOSO?", AM, 190, at("Preguiçoso", 2)), ("QUEM TRABALHA", BR, 120, at("trabalha")),
                           ("DURO TODO DIA", BR, 120, at("duro"))], "preguiçoso?")
palavra(B["r2"], B["r3"], [("SANGUE", BR, 250, at("sangue")), ("FERVENDO", AM, 230, at("fervendo"))], "sangue fervendo")
palavra(B["r3"], B["q2"], [("NÃO PARA", BR, 230, at("Mas")), ("POR AÍ", AM, 230, at("por", 1, B["r3"]))], "não para por aí")
palavra(B["r4"], B["q3"], [("JEITO DE FALAR", BR, 140, at("jeito")), ("DE GENTE?", AM, 230, at("gente"))], "de gente?")
palavra(B["r5"], B["r5b"], [("CÂNCER", BR, 250, at("Câncer", 2)), ("DO BRASIL?", BR, 170, at("Brasil", 1, B["r5"]))], "câncer do Brasil?")
palavra(B["r5b"], B["q4"], [("O NORDESTE É A", BR, 110, at("Nordeste", 1, B["r5"])), ("ALMA", AM, 330, at("alma")),
                            ("DESSE PAÍS", BR, 130, at("desse"))], "alma desse país")
palavra(B["r6"], B["q5"], [("VERGONHA", AM, 230, at("vergonha", 2)), ("É QUEM HUMILHA", BR, 130, at("humilha")),
                           ("PELO LUGAR ONDE NASCEU", BR, 90, at("lugar"))], "vergonha é quem humilha")
palavra(B["r7"], B["r8"], [("INFERIORES?", BR, 170, at("Inferiores", 2)), ("NUNCA.", AM, 330, at("Nunca"))], "inferiores? nunca")
palavra(B["r8"], B["r9"], [("CULTURA", BR, 170, at("cultura", 2)), ("HISTÓRIA", AM, 170, at("história")),
                           ("FORÇA", BR, 170, at("força")), ("ORGULHO", AM, 170, at("orgulho"))], "cultura história força orgulho",
        rotulo="O Nordeste tem", t_rot=at("Nordeste", 1, B["r8"]))
grade(B["r9"], B["r10"], [f"img/q{k}_b.jpg" for k in (1, 2, 3, 4, 5)] + ["clips/frames/27_47.1s_taxa-analfabetismo.jpg"], [455, 855], VM, 6, "fd", stagger=.1)
palavra(B["r9"], B["r10"], [("FORAM DITAS.", AM, 160, at("ditas"))], "foram ditas", y=1165)
palavra(B["r10"], B["r11"], [("ORGULHO", AM, 260, at("orgulho", 2)), ("DE CADA NORDESTINO", BR, 100, at("nordestino", 1, B["r10"])),
                             ("CABEÇA ERGUIDA", BR, 130, at("cabeça"))], "orgulho cabeça erguida")
palavra(B["r11"], B["r12"], [("QUEM ATACA O NORDESTE", BR, 95, at("Quem", 1, B["r10"])), ("ATACA O", BR, 120, at("ataca", 2, B["r10"])),
                             ("BRASIL INTEIRO", AM, 170, at("Brasil", 1, B["r11"]))], "ataca o Brasil inteiro")
palavra(B["r12"], B["r13"], [("PROTEJA", AM, 260, at("Proteja")), ("O NORDESTE", AM, 190, at("Nordeste", 1, B["r12"]))], "proteja o Nordeste")
palavra(B["r13"], DUR, [("VOTE LULA", BR, 170, at("Vote")), ("13", AM, 560, at(["treze", "13"], 1, B["r13"]))], "vote Lula 13", y=780)

# ---- legenda-frase (texto exato do roteiro) y=1330; citações ficam no bloco de aspas
parts = [p for p in re.split(r'(?<=[.?!:])\s+|(?<=[.?!]")\s+', ROT) if p]
RW = [x for p in parts for x in p.split()]
sm = difflib.SequenceMatcher(None, [norm(x) for x in RW], [norm(w["w"]) for w in W], autojunk=False)
mp = {}
for a, b, n in sm.get_matching_blocks():
    for j in range(n):
        mp[a + j] = b + j
def wi(r, d):
    while r not in mp:
        r += d
    return mp[r]
i = 0; caps = []
for p in parts:
    n = len(p.split())
    caps.append((p, W[wi(i, 1)]["s"], W[wi(i + n - 1, -1)]["e"])); i += n
KW = ["Nordeste", "nordestino", "trabalha duro", "sangue fervendo", "não para por aí", "de gente", "alma", "não aceito calado", "vergonha",
      "humilha", "Nunca", "cultura", "história", "força", "orgulho", "cabeça erguida", "Brasil inteiro", "Proteja", "Lula treze", "Vergonha", "Inferiores", "Preguiçoso", "Câncer do Brasil", "o pior"]
for k, (p, s, e) in enumerate(caps):
    if p.startswith('"'):
        continue
    f = caps[k + 1][1] - .05 if k + 1 < len(caps) else DUR
    hl = [h for h in KW if h in p]
    add({"id": f"lg{k}", "type": "text", "track": "legenda", "label": p[:30], "start": round(s - .08, 2), "dur": round(f - s + .08, 2),
         "in": "fade", "out": "none", "props": {"text": p, "x": 540, "y": 1330, "w": 960, "size": 56, "color": "#ffffff", "font": "Inter",
         "weight": 600, "align": "center", "shadow": False, "highlight": hl, "hl_color": AM, "line": 1.25}})

bg = {"id": "bg", "type": "html", "track": "fundo", "label": "fundo preto", "start": 0, "dur": DUR,
      "props": {"fill": True, "html": "<div class='drbg'></div>",
                "css": ".drbg{width:100%;height:100%;background:radial-gradient(ellipse at 50% 35%,#151517 0%,#0B0B0C 65%)}"}}
edit = {"version": 1, "name": NAME, "canvas": {"w": 1080, "h": 1920, "fps": 30, "bg": "#0B0B0C"}, "duration": DUR, "template": "generic",
        "grupo": "ESTILOS SHORTS", "estilo": "Dados ranking escuro amarelo",
        "referencia": {"canal": "@hilton_erika", "canal_url": "https://www.instagram.com/hilton_erika/",
                       "video": "https://www.instagram.com/reel/DexmT1TJlge/",
                       "nota": "clipes das falas vêm da referência (mudos); visual = estilo do short 06 (preto/amarelo)"},
        "fonts": {"Inter": "fonts/Inter.ttf", "Oswald": "fonts/Oswald-Bold.ttf"},
        "audio": {"voice": {"src": "voz.mp3", "volume": 1.0, "start": 0}},
        "tracks": [{"id": "fundo", "name": "Fundo"}, {"id": "visual", "name": "Tipografia"}, {"id": "card", "name": "Card citação"},
                   {"id": "clipe", "name": "Clipes (mudos)"}, {"id": "tag", "name": "Rótulos"}, {"id": "legenda", "name": "Legenda"}],
        "items": [bg] + items}
json.dump(edit, open(os.path.join(D, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("blocos", {k: round(v, 2) for k, v in ordem})
print("legendas", len(caps), "itens", len(items), "dur", DUR, "roteiro/whisper", len(RW), len(W))
