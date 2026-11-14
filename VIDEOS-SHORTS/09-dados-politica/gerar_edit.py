# Gera edit.json do short 09 (estilo dados ranking escuro amarelo, do 06). TODO tempo vem de words.json (trocar voz = whisper + rodar de novo).
import json, os, re, unicodedata, difflib, subprocess
D = os.path.dirname(os.path.abspath(__file__))
NAME = "09 - DADOS RANKING ESCURO - Por que essa santa assusta tanto"
WJ = json.load(open(os.path.join(D, "words.json"), encoding="utf-8"))
W = WJ["words"]
DUR = round(WJ["duration"] + 0.6, 2)
ROT = open(os.path.join(D, "roteiro.txt"), encoding="utf-8").read().strip()
AM = "#F5C518"

def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return re.sub(r"[^\w%]", "", "".join(c for c in s if unicodedata.category(c) != "Mn")).replace("_", "")

def at(palavra, oc=1, depois=0.0):
    """início da palavra (oc-ésima ocorrência após `depois`)"""
    alvo, k = norm(palavra), 0
    for w in W:
        if w["s"] < depois:
            continue
        if norm(w["w"]) == alvo or (len(alvo) > 3 and norm(w["w"]).startswith(alvo)):
            k += 1
            if k == oc:
                return w["s"]
    raise SystemExit(f"palavra não achada: {palavra} #{oc} depois de {depois}")

def tam(src):  # largura/altura da mídia
    o = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0",
                        os.path.join(D, src)], capture_output=True, text=True).stdout.strip().split(",")
    return int(o[0]), int(o[1])

def caixa(src, bw=960, bh=800, minw=660):
    """quadro que respeita o formato da mídia dentro de bw x bh (retrato estreito demais -> minw, recorta)"""
    w, h = tam(src)
    r = w / h
    fw, fh = (bw, bw / r) if bw / r <= bh else (bh * r, bh)
    if fw < minw:
        fw = minw
    return {"x": 540, "y": 840, "w": round(fw), "h": round(fh)}

items = []
def midia(src, s, e, q, motion="zoom_in", label=""):
    tipo = "video" if src.endswith(".mp4") else "image"
    items.append({"id": f"md{len(items)}", "type": tipo, "track": "midia", "label": label or os.path.basename(src)[:28], "start": round(s, 2),
                  "dur": round(e - s, 2), "in": "fade", "out": "fade",
                  "props": {"src": src, "fit": "cover", "x": q["x"], "y": q["y"], "w": q["w"], "h": q["h"], "volume": 0,
                            "motion": motion, "motion_amount": 0.07}})

def scene(nome, s, e, params, label):
    items.append({"id": f"sc{len(items)}", "type": "scene", "track": "visual", "label": label, "start": round(s, 2), "dur": round(e - s, 2),
                  "props": {"scene": nome, "params": params}})

def cena_midia(src, s, e, titulo, sub="", tags=(), aspas="", t_aspas=0, t_tit=0, label="", motion="zoom_in"):
    q = caixa(src)
    midia(src, s, e, q, motion, label)
    scene("dr_midia", s, e, {"titulo": titulo, "sub": sub, "t_tit": t_tit, "quadros": [q], "borda": AM,
                             "tags": [{"txt": a, "t": b} for a, b in tags], "aspas": aspas, "t_aspas": t_aspas}, label)

C01, C02, C03, C04, C05, C11 = ("clips/01_homem_quebrando_imagem_santa.mp4", "clips/02_santa_aparecida_manto_azul_dourado.mp4",
                                "clips/03_santa_manto_bordado_closeup.mp4", "clips/04_tv_antiga_chute_na_santa.mp4",
                                "clips/05_incendio_noite.mp4", "clips/11_pregador_video_antigo_igreja.mp4")

# ---- cortes (início de cada frase)
c = {"olha": at("Olha") - .2, "uma": at("imagem") - .35, "nascida": at("nascida") - .1, "pra": at("Pra") - .2, "mas": at("Mas") - .2,
     "e1": at("ainda") - .3, "eu": at("respeito") - .5, "entao": at("Então") - .2, "foi": at("alimentada") - .3,
     "repara": at("repara") - .3, "flavio": at("Flávio") - .2, "entre": at("tantos") - .45, "porq": at("ficar") - .3,
     "quem": at("sonha") - .7, "porque": at("Porque") - .2, "mesmo": at("mesmo", 1, at("começo")) - .3}

# 1 gancho: manto da santa
cena_midia(C03, 0, c["olha"], "Por que uma santa", "assusta quem quer mandar no país?",
           tags=[("ASSUSTA?", at("assusta"))], label="gancho santa")
# 2 palavra gigante: você (qualquer religião)
scene("dr_numero", c["olha"], c["uma"], {"rotulo": "Não importa a sua religião", "valor": "VOCÊ", "tam": 300,
                                         "sub": "católico · evangélico · espírita · sem religião", "t_valor": c["olha"] + .05,
                                         "t_rot": at("importa"), "t_sub": at("religião")}, "você / religião")
# 3 imagem frágil (pedaços) -> nascida partida em duas (mãos com as 2 partes)
cena_midia("img/06_imagem_santa_quebrada_pedacos.jpg", c["uma"], c["nascida"], "Uma imagem frágil", label="imagem frágil")
cena_midia(C01, c["nascida"], c["pra"], "Nascida", tags=[("PARTIDA EM DUAS", at("partida"))], label="partida em duas", motion="none")
# 4 Nossa Senhora Aparecida, padroeira, mãe de Jesus
cena_midia(C02, c["pra"], c["mas"], "Nossa Senhora Aparecida", t_tit=at("Nossa"),
           tags=[("PADROEIRA DO BRASIL", at("padroeira")), ("MÃE DE JESUS", at("mãe"))], label="Aparecida")
# 5 bispo JB Carvalho: citação em aspas grandes
cena_midia(C11, c["mas"], c["e1"], "Bispo JB Carvalho", "chamou a santa de", t_tit=at("bispo"),
           aspas="Braço direito de Satanás", t_aspas=at("braço"), label="citação bispo", motion="none")
# 6 pediu que deixasse de ser padroeira
cena_midia("img/09_pastor_comunidade_das_nacoes.jpg", c["e1"], c["eu"], "E ainda pediu", t_tit=c["e1"] + .1,
           tags=[("TIRAR O TÍTULO DE PADROEIRA", at("padroeira", 2))], label="pediu tirar padroeira")
# 7 respeito toda fé
scene("dr_numero", c["eu"], c["entao"], {"rotulo": "Toda fé", "valor": "RESPEITO", "tam": 210,
                                         "sub": "e quem não tem fé nenhuma também", "t_rot": at("toda"), "t_valor": c["eu"] + .05,
                                         "t_sub": at("nenhuma")}, "respeito")
# 8 de onde vem tanta raiva (chute na TV)
cena_midia(C04, c["entao"], c["foi"], "De onde vem", "tanta raiva?", t_tit=at("onde"),
           tags=[("NÃO NASCEU ENTRE OS FIÉIS", at("nasceu"))], label="raiva / chute", motion="none")
# 9 alimentada de cima (incêndio)
cena_midia(C05, c["foi"], c["repara"], "Alimentada de cima", "por gente poderosa", t_tit=at("alimentada"),
           tags=[("DIVIDIR O POVO USANDO A FÉ", at("dividir"))], label="alimentada de cima")
# 10 igreja desse bispo -> manchete; Flávio batizado -> foto batismo
cena_midia("img/13_manchete_fundador_igreja_flavio.jpg", c["repara"], c["flavio"], "Repara numa coisa", "a igreja desse bispo",
           t_tit=at("repara"), label="manchete igreja", motion="zoom_in")
cena_midia("img/12_foto_batismo_rio.jpg", c["flavio"], c["entre"], "Flávio Bolsonaro", "escolheu ser batizado ali",
           tags=[("BATIZADO", at("batizado"))], label="batismo")
# 11 entre tantos pastores (2 fotos, sem nome) -> manchete
q1 = {"x": 300, "y": 840, "w": 450, "h": 640}; q2 = {"x": 780, "y": 840, "w": 450, "h": 640}
midia("img/09_pastor_comunidade_das_nacoes.jpg", c["entre"], c["porq"], q1, "zoom_in", "pastor A")
midia("img/10_pastor_jaqueta_verde.jpg", c["entre"] + .15, c["porq"], q2, "zoom_in", "pastor B")
scene("dr_midia", c["entre"], c["porq"], {"titulo": "Entre tantos pastores", "quadros": [q1, q2], "borda": AM, "tags": [], "aspas": ""}, "tantos pastores")
cena_midia("img/14_manchete_metropoles_pastor_flavio.jpg", c["porq"], c["quem"], "Por que ficar perto", "de quem espalha ódio?",
           t_tit=at("ficar"), label="manchete metrópoles")
# 12 país de uma só igreja x mãe que não escolhe lado
scene("dr_numero", c["quem"], c["porque"], {"rotulo": "Quem sonha com um país de", "valor": "UMA SÓ IGREJA", "tam": 150,
                                            "sub": "não aguenta uma mãe que não escolhe lado", "t_rot": at("sonha"),
                                            "t_valor": c["quem"] + .05, "t_sub": at("aguenta")}, "uma só igreja")
# 13 senta todo mundo na mesma mesa
cena_midia(C02, c["porque"], c["mesmo"], "Todo mundo", "na mesma mesa", t_tit=at("senta"),
           tags=[("NA MESMA MESA", at("mesma")), ("PARTIDA EM DUAS DESDE O COMEÇO", at("partida", 2))], label="mesma mesa")
# 14 fecho: frase gigante
# fecho: a santa 02 continua atrás da frase final até o último quadro (escurecida)
md = items[-2]; md["dur"] = round(DUR - md["start"], 2); md["out"] = "none"
items.append({"id": "escuro", "type": "html", "track": "visual", "label": "escurece santa no fecho", "start": round(c["mesmo"] - .1, 2),
              "dur": round(DUR - c["mesmo"] + .1, 2), "in": "fade", "out": "none",
              "props": {"x": md["props"]["x"], "y": md["props"]["y"], "w": md["props"]["w"], "h": md["props"]["h"],
                        "html": "<div class='esc'></div>", "css": ".esc{width:100%;height:100%;background:rgba(11,11,12,.55)}"}})
scene("dr_numero", c["mesmo"], DUR, {"rotulo": "E mesmo assim, é ela que", "valor": "JUNTA", "unidade": "A GENTE", "tam": 280,
                                     "t_rot": at("mesmo", 1, at("começo")), "t_valor": c["mesmo"] + .1}, "fecho junta a gente")

# ---- legenda-frase (texto exato do roteiro) abaixo do quadro, palavras-chave em amarelo
KW = ["santa", "mandar no país", "religião", "imagem frágil", "partida em duas", "Nossa Senhora Aparecida", "padroeira do Brasil", "mãe de Jesus",
      "JB Carvalho", "braço direito de Satanás", "toda fé", "fé nenhuma", "tanta raiva", "fiéis", "de cima", "gente poderosa", "dividir o povo",
      "Flávio Bolsonaro", "batizado", "tantos pastores", "ódio", "uma só igreja", "uma mãe", "lado", "mesma mesa", "junta a gente"]
sent = re.split(r"(?<=[.?!:])\s+", ROT)
parts = []
for s in sent:
    if len(s) > 70 and ", " in s:
        cs = [m.start() for m in re.finditer(", ", s)]
        k = min(cs, key=lambda x: abs(x - len(s) / 2))
        parts += [s[:k + 1], s[k + 1:].strip()]
    else:
        parts.append(s)
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
for k, (p, s, e) in enumerate(caps):
    fim = caps[k + 1][1] - .05 if k + 1 < len(caps) else DUR
    hl = []
    for kw in sorted(KW, key=len, reverse=True):
        if kw in p and not any(kw in h for h in hl):
            hl.append(kw)
    items.append({"id": f"lg{k}", "type": "text", "track": "legenda", "label": p[:30], "start": round(s - .08, 2), "dur": round(fim - s + .08, 2),
                  "in": "fade", "out": "none", "props": {"text": p, "x": 540, "y": 1370, "w": 980, "size": 56, "color": "#ffffff", "font": "Inter",
                  "weight": 600, "align": "center", "shadow": True, "highlight": hl, "hl_color": AM, "line": 1.22}})

bg = {"id": "bg", "type": "html", "track": "fundo", "label": "fundo preto", "start": 0, "dur": DUR,
      "props": {"fill": True, "html": "<div class='drbg'></div>",
                "css": ".drbg{width:100%;height:100%;background:radial-gradient(ellipse at 50% 35%,#151517 0%,#0B0B0C 65%)}"}}
edit = {"version": 1, "name": NAME, "canvas": {"w": 1080, "h": 1920, "fps": 30, "bg": "#0B0B0C"}, "duration": DUR, "template": "generic",
        "grupo": "ESTILOS SHORTS", "estilo": "Dados ranking escuro amarelo",
        "referencia": {"canal": "@juliette", "canal_url": "https://www.instagram.com/juliette/", "video": "https://www.instagram.com/reel/DeZLBrHROWg/",
                       "nota": "tema/recortes do reel; visual = estilo do short 06 (preto/amarelo, cenas dr_*); sem logo/nome do perfil"},
        "fonts": {"Inter": "fonts/Inter.ttf", "Oswald": "fonts/Oswald-Bold.ttf"},
        "audio": {"voice": {"src": "voz.mp3", "volume": 1.0, "start": 0}},
        "tracks": [{"id": "fundo", "name": "Fundo"}, {"id": "midia", "name": "Imagens / vídeos"}, {"id": "visual", "name": "Gráficos"},
                   {"id": "legenda", "name": "Legenda"}],
        "items": [bg] + items}
json.dump(edit, open(os.path.join(D, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("cortes", {k: round(v, 2) for k, v in c.items()})
print("legendas", len(caps), "itens", len(items), "dur", DUR)
