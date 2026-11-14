# preencher.py — estilo "historia-simples" (replica as regras do 04-dinheiro-antigo/build.py + make_edit.py)
# Entrada: ctx = {nome, titulo, canal, duracao, words, shots:[{s,e,texto,img}], voz, cta_tempos}
# Saída: edit.json completo (template generic) no formato de EDITOR VIDEOS/FORMATO.md
#
# Regras herdadas do 04:
#  - 1 foto a cada ~3-5 s (um shot por trecho falado), só a câmera se move (Ken Burns), crossfade 0,5 s
#  - moldura 1236x684 com cantos 22px, vinheta, grão SVG, fade p/ preto no fim
#  - tint alternando sépia / verde-acinzentado; "dark" (mais contraste) a cada 7º shot (momento dramático)
#  - sem SFX. Textos (novos, regra do usuário: título ≥48px, apoio ≥24px): título no início, CTA like, inscreva-se
#  - 9:16 (ctx["vertical"], pedido em pé): canvas 1080x1920, moldura 1000x1560, textos dentro da safe zone de Reels/TikTok

TINT = {"sep": "grayscale(1) sepia(.55) contrast(1.1) brightness(.92)",
        "grn": "grayscale(1) sepia(.35) hue-rotate(40deg) contrast(1.08) brightness(.9)",
        "dark": "grayscale(1) sepia(.5) contrast(1.25) brightness(.75)"}
MOTIONS = ["zoom_in", "pan_right", "zoom_out", "pan_left", "zoom_in", "pan_up", "zoom_out", "pan_down"]
X = 0.5   # crossfade
COR_TXT = "#eadfc4"


def preencher(ctx):
    DUR = round(float(ctx["duracao"]), 2)
    shots = [s for s in ctx["shots"] if s.get("img")]
    vert = bool(ctx.get("vertical"))
    W, H = (1080, 1920) if vert else (1280, 720)
    CX, CY = W // 2, H // 2
    FW, FH = (1000, 1560) if vert else (1236, 684)   # moldura das fotos
    T = ({"tit": (1250, 900, 66), "cta": (1390, 860, 36), "fim": (60, 900)} if vert else   # (y, largura, tamanho) dos textos
         {"tit": (560, 1100, 56), "cta": (640, 900, 28), "fim": (48, 1000)})
    items, css = [], []
    for i, sh in enumerate(shots):
        st = round(sh["s"] if i else 0.0, 2)
        en = round(shots[i + 1]["s"], 2) + X if i + 1 < len(shots) else DUR
        tint = "dark" if (i % 7 == 6) else ("sep" if i % 2 == 0 else "grn")
        mo = MOTIONS[i % len(MOTIONS)]
        amt = [0.14, 0.18, 0.12, 0.2][i % 4]
        items.append({"id": f"s{i}", "type": "image", "track": "fundo", "label": sh["texto"][:40],
                      "start": st, "dur": round(en - st, 3), "in": "fade" if i else "none", "out": "none",
                      "props": {"src": sh["img"], "fit": "cover", "x": CX, "y": CY, "w": FW, "h": FH,
                                "radius": 22, "motion": mo, "motion_amount": amt, "opacity": 1}})
        css.append(f"#s{i} img,#s{i}{{filter:{TINT[tint]}}}")
    vig = ("<div class='vig'></div>",
           f".vig{{width:{FW}px;height:{FH}px;border-radius:22px;box-shadow:inset 0 0 140px 40px rgba(0,0,0,.75);"
           "background:radial-gradient(ellipse at center,rgba(0,0,0,0) 55%,rgba(0,0,0,.45) 100%)}")
    grain = (f"<svg width='{W}' height='{H}' style='opacity:.16;mix-blend-mode:overlay'><filter id='n'>"
             "<feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/></filter>"
             "<rect width='100%' height='100%' filter='url(#n)'/></svg>")
    items.append({"id": "vinheta", "type": "html", "track": "visual", "label": "Vinheta + moldura", "start": 0, "dur": DUR,
                  "in": "none", "out": "none", "props": {"html": vig[0], "css": vig[1], "x": CX, "y": CY, "w": FW, "h": FH}})
    items.append({"id": "grao", "type": "html", "track": "visual", "label": "Grão de filme", "start": 0, "dur": DUR,
                  "in": "none", "out": "none", "props": {"html": grain, "css": "", "x": CX, "y": CY, "w": W, "h": H}})
    items.append({"id": "fade_final", "type": "html", "track": "visual", "label": "Fade p/ preto", "start": round(DUR - 1.3, 2),
                  "dur": 1.3, "in": "fade", "out": "none",
                  "props": {"html": f"<div style='width:{W}px;height:{H}px;background:#000'></div>", "css": "", "x": CX, "y": CY, "w": W, "h": H}})
    # textos editáveis (título ≥48px, apoio ≥24px)
    items.append({"id": "titulo", "type": "text", "track": "textos", "label": "Título", "start": 0.4, "dur": 3.6, "in": "fade", "out": "fade",
                  "props": {"text": ctx["titulo"], "x": CX, "y": T["tit"][0], "w": T["tit"][1], "size": T["tit"][2], "color": COR_TXT, "font": "Cormorant",
                            "weight": 600, "align": "center", "bg": "rgba(0,0,0,.5)", "pad": 16, "radius": 6, "shadow": True, "upper": True}})
    for k, t in enumerate(ctx.get("cta_tempos", [])[:2]):
        items.append({"id": f"cta{k}", "type": "text", "track": "textos", "label": f"CTA like {k+1}", "start": round(t, 2), "dur": 3.0,
                      "in": "slide_up", "out": "fade",
                      "props": {"text": "Deixa o like pra apoiar o canal", "x": CX, "y": T["cta"][0], "w": T["cta"][1], "size": T["cta"][2], "color": COR_TXT,
                                "font": "CormorantI", "weight": 600, "align": "center", "bg": "rgba(0,0,0,.55)", "pad": 10, "radius": 6, "shadow": True}})
    items.append({"id": "fim", "type": "text", "track": "textos", "label": "Encerramento", "start": round(DUR - 4.2, 2), "dur": 2.9, "in": "fade", "out": "fade",
                  "props": {"text": ctx["canal"], "x": CX, "y": CY, "w": T["fim"][1], "size": T["fim"][0], "color": COR_TXT, "font": "Cormorant",
                            "weight": 600, "align": "center", "shadow": True, "upper": True}})
    return {"version": 1, "name": ctx["nome"], "estilo": "Canal de história simples",
            "canvas": {"w": W, "h": H, "fps": 30, "bg": "#0b0a08"}, "duration": DUR, "template": "generic",
            "fonts": {"Cormorant": "fonts/Cormorant.ttf", "CormorantI": "fonts/CormorantItalic.ttf"},
            "head": "<style>" + "\n".join(css) + "</style>",
            "audio": {"voice": {"src": ctx["voz"], "volume": 1.0, "start": 0}},
            "tracks": [{"id": "fundo", "name": "Fotos de arquivo (Ken Burns)"}, {"id": "visual", "name": "Vinheta / grão"},
                       {"id": "textos", "name": "Textos"}],
            "items": items, "_origem": {"fabrica": "EDITOR VIDEOS/fabrica/estilos/historia-simples/preencher.py", "creditos": "img/creditos.json"}}
