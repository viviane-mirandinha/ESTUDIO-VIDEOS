"""montar_edit.py — gera edit.json (v2: mapa explícito cena a cena)
Cada linha do TSV (tempo original) recebe um FUNDO (mapa 3D, foto, corte, escala...)
e, se tiver texto na tela, um OVERLAY (uw_numero se começar com número, senão uw_rotulo).
Tempos reais vêm de roteiro_tempos.json (voz gravada).
"""
import json, re, unicodedata, os, math

BASE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE, "roteiro_tempos.json"), encoding="utf-8") as f:
    RT = json.load(f)
RWORDS, RTIMES = RT["words"], RT["t"]
RDUR = RTIMES[-1][1]

TSV = str(__import__("pathlib").Path(__file__).resolve().parents[2] / "ROTEIROS-NOVOS" / "32 - MAPA CENAS EN-ES.tsv")
rows = []
with open(TSV, encoding="utf-8") as f:
    for line in f:
        p = line.rstrip("\n").split("\t")
        if not p or not p[0].strip():
            continue
        rows.append({"t_orig": float(p[0]), "frase": p[1].strip() if len(p) > 1 else "",
                     "texto": p[2].strip() if len(p) > 2 else ""})


# ── alinhamento frase -> tempo real ─────────────────────────────────────────
def norm(s):
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", s.lower())

RWN = [norm(w) for w in RWORDS]

def find_time(frase, i0):
    ws = [norm(w) for w in frase.split()[:5] if norm(w)]
    if not ws:
        return None
    for n in (len(ws), 3, 2):
        for i in range(i0, min(len(RWN), i0 + 400)):
            if all(i + j < len(RWN) and RWN[i + j] == ws[j] for j in range(min(n, len(ws)))):
                return i, RTIMES[i][0]
    return None

idx = 0
for r in rows:
    res = find_time(r["frase"], idx)
    r["t_real"] = None
    if res:
        idx, r["t_real"] = res
for i, r in enumerate(rows):
    if r["t_real"] is None:
        pb = next((rows[j] for j in range(i - 1, -1, -1) if rows[j]["t_real"] is not None), None)
        pa = next((rows[j] for j in range(i + 1, len(rows)) if rows[j]["t_real"] is not None), None)
        b, tb = (pb["t_real"], pb["t_orig"]) if pb else (0.0, 0.0)
        a, ta = (pa["t_real"], pa["t_orig"]) if pa else (RDUR, rows[-1]["t_orig"] + 3)
        r["t_real"] = b + (r["t_orig"] - tb) / max(.01, ta - tb) * (a - b)
rows[0]["t_real"] = 0.0
for i, r in enumerate(rows):
    nxt = rows[i + 1]["t_real"] if i + 1 < len(rows) else RDUR + 1
    r["dur"] = max(1.2, nxt - r["t_real"])

# ── regiões (lat, lon) ───────────────────────────────────────────────────────
POLO = [-82, 0]; EAST = [-75, 95]; WEST = [-80, -115]; WILKES = [-70, 120]; GAMB = [-80.5, 76]
VOSTOK = [-77.5, 106]; DENMAN = [-66.75, 99.5]; WHIL = [-84.24, -153.6]; KAMB = [-82.5, -145]
EREBUS = [-77.53, 167.15]; TAYLOR = [-77.72, 162.27]; THW = [-75.5, -106.75]; WED = [-75, -45]
ALLAN = [-76.7, 159.7]; PEN = [-68, -63]; FILCH = [-80, -50]
RIFT = [[-77, -165], [-79, -140], [-80, -115], [-78, -95], [-74, -80]]
SETORES = [{"lon0": -20, "lon1": 45, "cor": "#4477ff", "op": .35},     # Noruega
           {"lon0": 45, "lon1": 136, "cor": "#ffaa00", "op": .35},     # Austrália
           {"lon0": 136, "lon1": 142, "cor": "#8844ff", "op": .35},    # França
           {"lon0": 142, "lon1": 160, "cor": "#ffaa00", "op": .35},    # Austrália
           {"lon0": 160, "lon1": 210, "cor": "#44bb44", "op": .35},    # NZ
           {"lon0": -90, "lon1": -53, "cor": "#ff3333", "op": .30},    # Chile
           {"lon0": -80, "lon1": -20, "cor": "#ee6600", "op": .25},    # Reino Unido
           {"lon0": -74, "lon1": -25, "cor": "#33ccff", "op": .25}]    # Argentina
ZOOM = {"wide": (0.88, 0.76), "reg": (0.62, 0.55), "close": (0.5, 0.44)}

def R(foco, modo="sem-gelo", z="reg", **kw):
    return ("R", dict(foco=foco, modo=modo, z=z, **kw))
def P(name, **kw):
    return ("P", dict(src=f"img/cand/w_{name}.jpg", **kw))
def CORTE(**kw):
    return ("C", kw)
X = ("X", {})  # estende o fundo anterior

def pin(c, label, t=0.4):
    return {"c": c, "label": label, "t": t}

# ── MAPA EXPLÍCITO: t_orig -> fundo ──────────────────────────────────────────
V = {
 5.2:  R(POLO, "gelo", "wide", contorno={"rot": 0, "dx": 0, "dy": -10}),
 9.7:  R(POLO, "gelo", "wide"),
 13.3: P("denman_0"),
 18.6: R(POLO, "gelo", "reg"),
 20.5: CORTE(modo="bloco", valor="+2 KM DE HIELO"),
 24.5: P("twinotter_1"),
 31.4: R(POLO, "derrete", "wide"),
 37.4: ("CAP", {}),
 42.0: R(POLO, "gelo", "wide"),
 45.4: P("thwaites_0"),
 50.8: P("burj_0"),
 56.6: R(WILKES, "sem-gelo", "reg", rot="TIERRA DE WILKES"),
 64.3: ("ESC", {"n": 5.7, "valor": "4,757 M DE HIELO"}),
 70.3: CORTE(modo="bloco", valor="PROMEDIO: 2.1 KM"),
 74.3: ("ESC", {"n": 2.5, "valor": "2,100 M DE HIELO"}),
 79.6: R(VOSTOK, "gelo", "reg"),
 83.5: P("vostokst_0"),
 89.7: P("dryvalley_2"),
 95.0: P("curiosity_0"),
 100.3: R(POLO, "gelo", "reg"),
 104.6: P("twinotter_1", motion="pan_right"),
 109.6: CORTE(modo="radar"),
 113.4: X,
 117.0: P("twinotter_2"),
 121.2: R(POLO, "sem-gelo", "wide"),
 128.9: ("CARIMBO", {"pergunta": "¿90% SIN MAPEAR?", "carimbo": "NO EXACTAMENTE"}),
 133.1: X,
 135.9: R(EAST, "sem-gelo", "reg"),
 140.5: R(WEST, "sem-gelo", "reg"),
 144.6: R(POLO, "sem-gelo", "wide"),
 153.7: R(POLO, "derrete", "wide"),
 155.5: R(POLO, "sem-gelo", "wide"),
 158.9: R(POLO, "sem-gelo", "wide"),
 165.4: R(WEST, "sem-gelo", "reg", rot="ANTÁRTIDA OCCIDENTAL"),
 169.0: R(WEST, "sem-gelo", "close"),
 173.5: R(WEST, "sem-gelo", "reg", linhas=[{"pts": RIFT, "cor": "#ff6b35", "w": 4}]),
 178.4: R(EAST, "sem-gelo", "reg", rot="ANTÁRTIDA ORIENTAL"),
 180.2: R(EAST, "sem-gelo", "close"),
 184.5: CORTE(modo="rebote", valor="~2 KM DE HIELO", a="LA ROCA SE LEVANTA HASTA 900 M"),
 187.8: X,
 194.6: R(DENMAN, "sem-gelo", "reg", pinos=[pin(DENMAN, "GLACIAR DENMAN")]),
 201.4: P("denman_1", motion="zoom_in"),
 205.1: P("marmuerto_1"),
 210.7: CORTE(modo="fosa"),
 217.4: P("twinotter_1", motion="pan_left"),
 221.6: P("denman_1", motion="pan_right"),
 226.2: R(DENMAN, "sem-gelo", "close", pinos=[pin(DENMAN, "DENMAN")]),
 232.3: P("denman_0", motion="pan_left"),
 233.8: R(DENMAN, "gelo", "close", pinos=[pin(DENMAN, "LÍNEA DE APOYO")]),
 239.8: P("vostokst_0"),
 245.1: R(GAMB, "gelo", "reg"),
 248.2: R(GAMB, "derrete", "reg"),
 249.9: R(GAMB, "sem-gelo", "reg"),
 254.8: R(GAMB, "sem-gelo", "close", pinos=[pin(GAMB, "MONTES GAMBURTSEV")]),
 258.8: CORTE(modo="bloco", valor="+600 M DE HIELO"),
 262.3: P("twinotter_0"),
 263.8: X,
 270.7: R(GAMB, "sem-gelo", "reg"),
 273.3: R(GAMB, "sem-gelo", "close"),
 278.1: R(GAMB, "sem-gelo", "reg"),
 280.8: P("gondwana_0", motion="zoom_out"),
 283.8: R(POLO, "gelo", "wide"),
 288.6: P("glossopteris_1"),
 291.1: P("glossopteris_2"),
 292.7: P("glossopteris_0"),
 296.4: P("icecore_1"),
 302.6: R(POLO, "gelo", "wide"),
 308.1: R(EAST, "gelo", "reg"),
 310.2: P("putorana_2"),
 315.6: CORTE(modo="bloco", valor="~2 KM DE HIELO"),
 318.5: R([-68, 110], "sem-gelo", "reg"),
 322.7: R([-70, 80], "sem-gelo", "reg"),
 328.2: P("denman_0", motion="zoom_in"),
 333.3: R(POLO, "sem-gelo", "wide"),
 336.5: R(EAST, "sem-gelo", "reg"),
 341.3: R(WEST, "gelo", "reg"),
 344.1: R(WEST, "sem-gelo", "reg"),
 350.1: R(VOSTOK, "sem-gelo", "reg", pinos=[pin(VOSTOK, "LAGO VOSTOK")]),
 351.6: R(VOSTOK, "gelo", "close", pinos=[pin(VOSTOK, "VOSTOK")]),
 352.6: R(VOSTOK, "sem-gelo", "close"),
 359.1: P("michigan_1"),
 362.9: CORTE(modo="lago", valor="LAGO VOSTOK · ≈ -3 °C", a="EL HIELO AÍSLA DESDE ARRIBA",
             b="PRESIÓN", c="LA TIERRA CALIENTA DESDE ABAJO"),
 365.4: X,
 372.9: P("europa_0"),
 375.7: P("europa_1", motion="zoom_out"),
 379.4: P("europa_2"),
 382.6: P("vostokst_1"),
 387.5: CORTE(modo="perforacion", a="POZO CON QUEROSENO · ≈3.8 KM"),
 390.3: P("icecore_1", motion="pan_left"),
 393.7: R(VOSTOK, "sem-gelo", "close"),
 396.8: P("icecore_1", motion="zoom_in"),
 402.4: R(WHIL, "sem-gelo", "reg", pinos=[pin(WHIL, "LAGO WHILLANS")]),
 405.4: CORTE(modo="whillans", valor="LAGO WHILLANS", a="TALADRO ESTÉRIL DE AGUA CALIENTE"),
 408.4: R(WHIL, "gelo", "close"),
 412.9: R(WHIL, "sem-gelo", "close"),
 417.6: CORTE(modo="plataforma", valor="≈900 M DE HIELO FLOTANTE", a="ROCA EN EL FONDO MARINO"),
 422.8: X,
 426.0: P("anfipodo_0"),
 427.9: R(FILCH, "gelo", "reg", pinos=[pin(FILCH, "260 KM DEL MAR")]),
 430.5: R(FILCH, "sem-gelo", "close"),
 434.5: P("anfipodo_0", motion="zoom_out"),
 437.4: R(KAMB, "gelo", "reg", pinos=[pin(KAMB, "KAMB")]),
 441.4: R(KAMB, "sem-gelo", "close"),
 442.5: P("anfipodo_0", motion="pan_right"),
 446.4: ("CAP", {}),
 448.2: P("erebuslava_1"),
 452.9: P("erebus_2"),
 458.2: P("bloodfalls_1"),
 462.3: P("bloodfalls_0", motion="zoom_in"),
 467.2: P("bloodfalls_0", motion="pan_right", amount=.12),
 469.6: P("bloodfalls_2"),
 471.8: R(TAYLOR, "sem-gelo", "close", pinos=[pin(TAYLOR, "CATARATAS DE SANGRE")]),
 475.1: R(EREBUS, "sem-gelo", "reg", pinos=[pin(EREBUS, "MONTE EREBUS")]),
 477.9: P("erebuslava_2"),
 479.8: P("erebus_1"),
 483.8: P("erebuslava_1", motion="zoom_out"),
 486.4: P("erebus_1", motion="pan_left"),
 489.0: R(WEST, "gelo", "reg"),
 491.1: R(WEST, "sem-gelo", "reg"),
 493.1: ("GRADE", {}),
 497.2: X,
 500.8: R(WILKES, "gelo", "reg"),
 504.4: R(WILKES, "sem-gelo", "reg", circulos=[{"c": WILKES, "r_km": 250, "cor": "#ff4444"}]),
 506.8: X,
 511.4: P("meteorito_0"),
 514.3: P("glossopteris_0", motion="zoom_out"),
 515.9: X,
 518.3: P("glossopteris_2", motion="pan_left"),
 521.4: R(WILKES, "gelo", "reg", circulos=[{"c": WILKES, "r_km": 250, "cor": "#ff4444"}]),
 524.6: ("CARIMBO", {"pergunta": "¿MUESTRAS DE ROCA?", "carimbo": "NINGUNA"}),
 527.9: P("putorana_0"),
 532.2: ("CARIMBO", {"pergunta": "¿UN CRÁTER GIGANTE?", "carimbo": "HIPÓTESIS"}),
 536.7: ("CAP", {}),
 540.9: R(POLO, "sem-gelo", "wide", setores=SETORES),
 542.9: R(PEN, "sem-gelo", "reg", setores=SETORES),
 547.4: P("tratado_0"),
 551.4: R(POLO, "sem-gelo", "wide"),
 555.6: R(POLO, "gelo", "wide", setores=SETORES),
 557.9: ("LINHA", {"itens": [{"ano": "1959", "txt": "12 PAÍSES FIRMAN"},
                            {"ano": "1991", "txt": "SE PROHÍBE LA MINERÍA"}]}),
 561.5: X,
 564.4: ("CARIMBO", {"pergunta": "¿LA PROHIBICIÓN VENCE EN 2048?", "carimbo": "FALSO"}),
 567.8: X,
 569.8: ("LINHA", {"itens": [{"ano": "1959", "txt": "TRATADO"}, {"ano": "1991", "txt": "MINERÍA PROHIBIDA"},
                            {"ano": "2048", "txt": "SOLO SE PUEDE REVISAR"}]}),
 573.2: P("tratado_0", motion="pan_left"),
 578.1: R(WED, "sem-gelo", "reg", pinos=[pin(WED, "MAR DE WEDDELL")]),
 581.6: R(WED, "gelo", "reg"),
 585.1: R(WED, "sem-gelo", "close"),
 587.5: R(WEST, "gelo", "reg"),
 590.0: P("thwaites_0", motion="pan_right"),
 591.5: R(THW, "gelo", "reg", pinos=[pin(THW, "GLACIAR THWAITES")]),
 595.6: CORTE(modo="corcho", valor="GLACIAR THWAITES", a="AGUA TIBIA DEL MAR"),
 600.3: P("thwaites_0", motion="zoom_in"),
 602.6: CORTE(modo="corcho", valor="GLACIAR THWAITES", a="AGUA TIBIA DEL MAR", seed=3),
 606.0: R(THW, "sem-gelo", "reg"),
 610.9: R(WEST, "gelo", "reg"),
 612.0: R(WEST, "derrete", "reg"),
 614.4: P("icecore_1"),
 617.8: CORTE(modo="perforacion", a="HASTA LA ROCA MADRE"),
 620.8: X,
 621.7: P("icecore_1", motion="zoom_out"),
 625.3: P("meteorito_0", motion="zoom_in"),
 629.6: R(ALLAN, "sem-gelo", "reg", pinos=[pin(ALLAN, "COLINAS ALLAN")]),
 635.2: P("alh84001_0"),
 640.1: P("curiosity_2"),
 645.4: P("meteorito_1"),
 650.3: X,
 651.7: R(GAMB, "sem-gelo", "close"),
 655.9: P("putorana_2", motion="zoom_out"),
 658.8: R(VOSTOK, "sem-gelo", "reg"),
 661.5: R(POLO, "gelo", "wide"),
 663.8: R(POLO, "sem-gelo", "wide"),
 666.9: R(POLO, "sem-gelo", "wide"),
 670.0: R(POLO, "gelo", "wide"),
 672.3: R(POLO, "gelo", "wide"),
}

# ── items ────────────────────────────────────────────────────────────────────
items, _n = [], [0]
def scene(start, dur, name, params, z=None):
    _n[0] += 1
    it = {"id": f"c{_n[0]}", "type": "scene", "start": round(start, 2), "dur": round(max(dur, .8), 2),
          "props": {"scene": name, "params": params, "fill": True}}
    if z is not None:
        it["props"]["z"] = z
    items.append(it)
    return it

NUM = re.compile(r'^([+\-−~<>≈]?\s*\d[\d,.]*\s*(?:MILLONES|KM³|KM²|KM|CM|M|G|%|°C)?)(?=\s|$)\s*(?:·\s*)?(.*)$')

def overlay(start, dur, T):
    if not T:
        return
    m = NUM.match(T)
    if m and len(m.group(1)) <= 16:
        num, sub = m.group(1).strip(), m.group(2).strip()
        conta = not re.fullmatch(r"(19|20)\d\d", num)
        scene(start, dur, "uw_numero", {"numero": num, "sub": sub, "escurecer": .4, "conta": conta})
    else:
        parts = [s.strip() for s in T.split("·")]
        scene(start, dur, "uw_rotulo", {"texto": parts[0], "sub": " · ".join(parts[1:]), "canto": "bl"})

missing, last_bg, ri = [], None, 0
for i, r in enumerate(rows):
    S, D, T = r["t_real"], r["dur"], r["texto"]
    kind, a = V.get(round(r["t_orig"], 1), (None, None))
    if kind is None:
        missing.append(r["t_orig"])
        kind, a = R(POLO, "sem-gelo", "wide")
    over = True
    if kind == "X" and last_bg is not None:
        last_bg["dur"] = round(S + D - last_bg["start"], 2)
    elif kind == "R":
        ri += 1
    if kind == "P":
        a.setdefault("motion", ["zoom_in", "zoom_out", "pan_right", "pan_left"][i % 4])
        a.setdefault("amount", .07)
        a.update(escurecer=.15, fade_in=.12)
        last_bg = scene(S, D, "uw_foto", a)
    elif kind == "C":
        last_bg = scene(S, D, "uw_corte", a)
    elif kind == "ESC":
        last_bg = scene(S, D, "uw_escala", dict(a, burj="BURJ KHALIFA · 828 M"))
        over = False
    elif kind == "GRADE":
        last_bg = scene(S, D, "uw_grade", {"n": 138, "destaque": 91, "titulo": "138",
                        "sub": "PICOS VOLCÁNICOS BAJO EL HIELO", "sub2": "91 DESCONOCIDOS HASTA 2017", "por_linha": 23})
        over = False
    elif kind == "LINHA":
        last_bg = scene(S, D, "uw_linha", dict(a, titulo="TRATADO ANTÁRTICO"))
        over = False
    elif kind == "CARIMBO":
        last_bg = scene(S, D, "uw_carimbo", a)
        over = False
    elif kind == "CAP":
        parts = [s.strip() for s in T.split("·")]
        last_bg = scene(S, D, "uw_capitulo", {"n": parts[0], "titulo": parts[1] if len(parts) > 1 else ""})
        over = False
    if kind == "R":
        cfg = dict(a)
        foco = cfg.pop("foco")
        z0, z1 = ZOOM[cfg.pop("z")]
        rot = cfg.pop("rot", "")
        az0 = (ri * 53) % 360
        params = {"modo": cfg.pop("modo"), "foco": foco, "zoom0": z0, "zoom1": z1,
                  "el": 34 + (ri % 3) * 6, "az0": az0, "az1": az0 - 22, "rotulo": rot, "fade_in": .35}
        if params["modo"] == "derrete":
            params.update(derrete_ini=.15, derrete_fim=.85)
        params.update(cfg)
        last_bg = scene(S, D, "uw_relevo", params)
    if over and T and kind != "X" or (kind == "X" and T):
        overlay(S + .15, D - .3, T)

# primeiro fundo começa em 0 e o último vai até o fim
items_bg = [it for it in items if it["props"]["scene"] not in ("uw_numero", "uw_rotulo")]
items_bg[0]["dur"] = round(items_bg[0]["dur"] + items_bg[0]["start"], 2); items_bg[0]["start"] = 0
items_bg[-1]["dur"] = round(RDUR + 1 - items_bg[-1]["start"], 2)
# overlays ficam por cima
for it in items:
    it["props"]["z"] = 5 if it["props"]["scene"] in ("uw_numero", "uw_rotulo") else 1

edit = {
    "name": "32 - DOCUMENTARIO MAPA 3D - Así se ve la Antártida sin hielo",
    "estilo": "32-documentario-mapa-3d-sem-gelo",
    "grupo": "ESTILOS NOVOS",
    "referencia": {"canal": "Unseen Works",
                   "canal_url": "https://www.youtube.com/channel/UCVZp2VFWV4mUJOjhklymJKQ",
                   "video": "https://youtu.be/TudM_lSW8WA",
                   "titulo": "What Antarctica Looks Like Without Ice"},
    "canvas": {"w": 1280, "h": 720, "fps": 30, "bg": "#0c1726"},
    "duration": math.ceil(RDUR + 1),
    "template": "generic",
    "fonts": {"Montserrat": "fonts/Montserrat-Black.ttf", "Inter": "fonts/Inter.ttf"},
    "head": '<script src="https://cdn.jsdelivr.net/npm/three@0.150.1/build/three.min.js"></script>',
    "audio": {"voice": {"src": "voz.wav", "volume": 1.0, "start": 0}},
    "tracks": [{"id": "fundo", "name": "Fundo"}, {"id": "texto", "name": "Texto"}],
    "items": items,
}
for it in items:
    it["track"] = "texto" if it["props"]["z"] == 5 else "fundo"
with open(os.path.join(BASE, "edit.json"), "w", encoding="utf-8") as f:
    json.dump(edit, f, ensure_ascii=False, indent=1)
cnt = {}
for it in items:
    cnt[it["props"]["scene"]] = cnt.get(it["props"]["scene"], 0) + 1
print(f"{len(items)} items | sem mapa explícito: {missing}")
print(cnt)
