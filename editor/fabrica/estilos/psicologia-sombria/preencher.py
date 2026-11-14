# preencher.py — estilo "psicologia-sombria" (replica 08-psicologia/tools/make_edit.py)
# Regras herdadas do 08: pinturas clássicas em tela cheia, Ken Burns lento (0.07), holds longos (4-8 s),
# crossfade 0,2 s, grade escuro/dessaturado + vinheta + grão, textos Cormorant (reta/itálica) em 2 linhas
# escalonadas, MAIÚSCULAS em dourado, citações com faixa escura. Sem SFX, sem música.
import re

C, ACC = "#ece4d4", "#c9a96e"
MOTIONS = ["zoom_in", "pan_up", "pan_left", "zoom_in", "pan_right", "zoom_out", "pan_up", "pan_left"]
GRADE = "grayscale(.5) sepia(.12) contrast(1.08) brightness(.82) saturate(.85)"
GRADE_PB = "grayscale(1) contrast(1.15) brightness(.75)"


def _duas_linhas(t):
    w = t.split()
    if len(w) < 4:
        return [t]
    k = (len(w) + 1) // 2
    # tenta quebrar numa vírgula perto do meio
    for i in range(max(1, k - 2), min(len(w) - 1, k + 2)):
        if w[i - 1].endswith((",", ";", ":")):
            k = i
            break
    return [" ".join(w[:k]), " ".join(w[k:])]


def preencher(ctx):
    DUR = round(float(ctx["duracao"]), 2)
    shots = [s for s in ctx["shots"] if s.get("img")]
    items, css = [], []
    for i, sh in enumerate(shots):
        s = round(sh["s"] - 0.2, 2) if i else 0.0
        e = round(shots[i + 1]["s"], 2) if i + 1 < len(shots) else DUR
        pb = (i % 5 == 3)   # "imaginação/lembrança" em P&B (regra do 08)
        items.append({"id": f"img{i+1:02d}", "type": "image", "track": "fundo", "label": sh["texto"][:40],
                      "start": max(0, s), "dur": round(e - max(0, s), 2), "in": "none" if i == 0 else "fade", "out": "fade",
                      "props": {"src": sh["img"], "fill": True, "fit": "cover", "motion": MOTIONS[i % len(MOTIONS)], "motion_amount": 0.07}})
        css.append(f"#img{i+1:02d} img,#img{i+1:02d}{{filter:{GRADE_PB if pb else GRADE}}}")
    items.append({"id": "grade", "type": "html", "track": "visual", "label": "vinheta + grão", "start": 0, "dur": DUR, "in": "none", "out": "none",
                  "props": {"x": 640, "y": 360, "w": 1280, "h": 720, "html": "<div class='vg'></div><div class='gr'></div>",
                            "css": ".vg{position:absolute;inset:0;background:radial-gradient(ellipse at center,rgba(0,0,0,0) 35%,rgba(0,0,0,.78) 100%),linear-gradient(rgba(5,6,10,.25),rgba(5,6,10,.25))}"
                                   ".gr{position:absolute;inset:0;opacity:.10;mix-blend-mode:overlay;background-image:url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>\")}"}})

    # textos: título em 2 linhas escalonadas no 1º shot; frases curtas/citações nos shots; CTA; inscreva-se
    T = []
    lin = _duas_linhas(ctx["titulo"])
    T.append((0.4, min(5.0, shots[1]["s"] if len(shots) > 1 else 5.0), lin[0], 640, 320, 54, "Cormorant", False))
    if len(lin) > 1:
        T.append((1.6, min(5.0, shots[1]["s"] if len(shots) > 1 else 5.0), lin[1], 760, 395, 56, "CormorantI", False))
    for i, sh in enumerate(shots[1:], 1):
        txt = sh["texto"].strip()
        m = re.search(r"[\"“]([^\"”]{8,90})[\"”]", txt)
        if m:   # citação → 2 linhas itálicas com faixa escura (regra do 08)
            l2 = _duas_linhas("“" + m.group(1).strip() + "”")
            T.append((sh["s"] + 0.2, sh["e"] + 0.3, l2[0], 640, 320, 52, "CormorantI", True))
            if len(l2) > 1:
                T.append((sh["s"] + 0.9, sh["e"] + 0.3, l2[1], 700, 390, 52, "CormorantI", True))
        elif len(txt.split()) <= 6 and not re.search(r"like|inscrev|coment", txt.lower()):
            # frase curta inteira em caixa-alta dourada (nunca trecho cortado no meio)
            T.append((sh["s"] + 0.3, sh["e"] + 0.3, txt.rstrip(".,;:!?").upper(), 640, 560, 50, "Cormorant", False))
        elif i % 2 == 0 and len(txt.split()) <= 10:
            T.append((sh["s"] + 0.3, sh["e"] + 0.2, txt.rstrip(".,"), 640, 600, 48, "CormorantI", False))
    for k, t in enumerate(ctx.get("cta_tempos", [])[:1]):
        T.append((t, t + 3.0, "deixa o like se fez sentido", 640, 640, 30, "CormorantI", False))
    T.append((DUR - 4.0, DUR - 0.6, "inscreva-se", 640, 600, 44, "CormorantI", False))
    for i, (s, e, txt, x, y, size, font, faixa) in enumerate(T):
        if e - s < 0.8:
            continue
        items.append({"id": f"t{i+1:02d}", "type": "text", "track": "textos", "label": txt[:24], "start": round(s, 2), "dur": round(e - s, 2),
                      "in": "fade", "out": "fade",
                      "props": {"text": txt, "x": x, "y": y, "w": 1100, "size": size, "color": ACC if txt.isupper() else C, "font": font,
                                "weight": 500, "align": "center", "shadow": True, "upper": False,
                                **({"bg": "rgba(0,0,0,.55)", "pad": 12, "radius": 4} if faixa else {})}})
    return {"version": 1, "name": ctx["nome"], "estilo": "Psicologia sombria",
            "canvas": {"w": 1280, "h": 720, "fps": 30, "bg": "#07080b"}, "duration": DUR, "template": "generic",
            "fonts": {"Cormorant": "fonts/Cormorant.ttf", "CormorantI": "fonts/CormorantItalic.ttf"},
            "head": "<style>" + "\n".join(css) + "</style>",
            "audio": {"voice": {"src": ctx["voz"], "volume": 1.0, "start": 0}},
            "tracks": [{"id": "fundo", "name": "Pinturas"}, {"id": "visual", "name": "Vinheta/grão"}, {"id": "textos", "name": "Textos"}],
            "items": items, "_origem": {"fabrica": "EDITOR VIDEOS/fabrica/estilos/psicologia-sombria/preencher.py", "creditos": "img/creditos.json"}}
