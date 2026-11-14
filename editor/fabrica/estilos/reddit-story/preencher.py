# preencher.py — estilo "reddit-story" (replica 12-reddit/mk_edit.py)
# Regras herdadas do 12: gameplay no-copyright em tela cheia (mudo), card branco do post (pop) enquanto
# o narrador lê o título, depois legenda 1 palavra por vez Montserrat Black 92px com contorno preto e
# palavras-chave em amarelo; aviso "História fictícia" no fim. Sem SFX, sem música.
# 9:16 (ctx["vertical"], pedido em pé): canvas 1080x1920, gameplay cobrindo a tela, card no topo, legenda grande no
# centro e tudo dentro da safe zone de Reels/TikTok (fora dos ~220 px de cima, ~420 px de baixo e ~140 px da direita).
import html as H
import random

from lib import texto

CARD_CSS = """.rd{width:100%;height:100%;box-sizing:border-box;background:#fff;border-radius:26px;padding:30px 38px;font-family:'Inter',Arial,sans-serif;color:#1c1c1c;box-shadow:0 18px 60px rgba(0,0,0,.55)}
.rd-top{display:flex;align-items:center;gap:16px}.rd-av{width:62px;height:62px;border-radius:50%;background:#ff4500;color:#fff;font:900 26px 'Inter';display:flex;align-items:center;justify-content:center}
.rd-sub{font-weight:800;font-size:24px}.rd-user{font-size:19px;color:#6b6f73}.rd-join{margin-left:auto;background:#0045ac;color:#fff;font-weight:800;font-size:19px;padding:10px 22px;border-radius:30px}
.rd-title{font-weight:800;font-size:40px;line-height:1.18;margin:22px 0 14px}.rd-flair{background:#e8ecef;color:#333;font-weight:700;font-size:18px;padding:6px 14px;border-radius:20px}
.rd-bot{display:flex;gap:14px;margin-top:22px}.rd-pill{display:flex;align-items:center;gap:8px;background:#eef1f3;border-radius:30px;padding:9px 18px;font-weight:700;font-size:19px;color:#333}.rd-pill svg{width:24px;height:24px}"""


def card_html(titulo, sub, user, votos, comentarios, flair):
    return f"""<div class="rd">
 <div class="rd-top"><div class="rd-av">r/</div><div><div class="rd-sub">{H.escape(sub)}</div><div class="rd-user">{H.escape(user)} · 7 h</div></div><div class="rd-join">Participar</div></div>
 <div class="rd-title">{H.escape(titulo)}</div>
 <div class="rd-tags"><span class="rd-flair">{H.escape(flair)}</span></div>
 <div class="rd-bot"><span class="rd-pill"><svg viewBox="0 0 20 20"><path d="M10 3l7 8h-4v6H7v-6H3z" fill="#ff4500"/></svg><b>{votos}</b><svg viewBox="0 0 20 20"><path d="M10 17l7-8h-4V3H7v6H3z" fill="#878a8c"/></svg></span>
 <span class="rd-pill"><svg viewBox="0 0 20 20"><path d="M3 4h14v9H8l-4 3v-3H3z" fill="none" stroke="#555" stroke-width="1.8"/></svg>{comentarios}</span>
 <span class="rd-pill"><svg viewBox="0 0 20 20"><circle cx="10" cy="10" r="6" fill="#ffd635"/><path d="M7 10l2 2 4-4" stroke="#b8860b" stroke-width="1.8" fill="none"/></svg>Prêmio</span>
 <span class="rd-pill">Compartilhar</span></div></div>"""


def preencher(ctx):
    DUR = round(float(ctx["duracao"]), 2)
    words = ctx["words"]
    fr = texto.frases(words)
    # card fica enquanto o narrador lê a 1ª frase (o título); mínimo 3,5 s
    fim_card = round(max(3.5, fr[0]["e"] + 0.4), 2) if fr else 4.0
    rnd = random.Random(len(words))
    votos = f"{rnd.randint(8, 40)},{rnd.randint(1, 9)} mil"
    coms = f"{rnd.randint(1, 6)},{rnd.randint(1, 9)} mil"
    titulo = ctx["titulo"]
    if fr and len(fr[0]["texto"].split()) <= 22:
        titulo = fr[0]["texto"]          # o card mostra a pergunta exatamente como foi lida
    kw = []
    try:
        kw = ctx["ollama"].palavras_chave(ctx["roteiro"], 10, modelo=ctx.get("modelo") or ctx["ollama"].MODELO_PADRAO)
    except Exception:
        pass
    if not kw:
        kw = sorted({w["w"].lower().strip(".,!?") for w in words if len(w["w"]) >= 8})[:10]
    clip = ctx["shots"][0].get("clip", "clips/gameplay.mp4") if ctx["shots"] else "clips/gameplay.mp4"
    cta = ctx.get("cta_tempos") or []
    vert = bool(ctx.get("vertical"))
    W, H = (1080, 1920) if vert else (1280, 720)
    # posições (16:9 = as originais do 12-reddit; 9:16 = safe zone; x um pouco à esquerda por causa dos botões da direita)
    P = ({"card": (520, 590, 920, 400), "leg": (520, 960, 116, 14), "fim": (520, 1400, 40), "cta": (520, 330, 46)} if vert else
         {"card": (640, 340, 860, 330), "leg": (640, 360, 92, 12), "fim": (640, 650, 28), "cta": (640, 110, 34)})
    items = [
        {"id": "gp", "type": "video", "track": "fundo", "label": "Gameplay", "start": 0, "dur": DUR,
         "props": {"src": clip, "fill": True, "fit": "cover", "volume": 0, "motion": "none"}},
        {"id": "card", "type": "html", "track": "visual", "label": "Post do Reddit", "start": 0, "dur": fim_card, "in": "pop", "out": "fade",
         "props": {"html": card_html(titulo, "r/EuSouOBabaca", ("u/" + ctx["canal"].lower().replace(" ", "_")[:18]) if ctx["canal"] else "", votos, coms, "Família"),
                   "css": CARD_CSS, "x": P["card"][0], "y": P["card"][1], "w": P["card"][2], "h": P["card"][3]}},
        {"id": "leg", "type": "caption", "track": "legenda", "label": "Legenda palavra-por-palavra", "start": fim_card, "dur": round(DUR - fim_card, 2),
         "props": {"words_file": "words.json", "per_group": 1, "x": P["leg"][0], "y": P["leg"][1], "size": P["leg"][2], "color": "#ffffff", "dim": "#ffffff",
                   "hl_color": "#ffd400", "keywords": kw, "font": "Montserrat", "weight": 900, "stroke": "#000", "stroke_w": P["leg"][3], "shadow": True}},
        {"id": "fim", "type": "text", "track": "legenda", "label": "Aviso final", "start": round(DUR - 2.6, 2), "dur": 2.4, "in": "fade",
         "props": {"text": "História fictícia", "x": P["fim"][0], "y": P["fim"][1], "size": P["fim"][2], "color": "#ffffff", "font": "Inter", "weight": 700,
                   "bg": "rgba(0,0,0,.55)", "pad": 10}},
    ]
    if cta:
        items.append({"id": "cta", "type": "text", "track": "legenda", "label": "CTA comentário", "start": round(cta[-1], 2), "dur": 3.0,
                      "in": "slide_up", "out": "fade",
                      "props": {"text": "Comenta: quem está certo?", "x": P["cta"][0], "y": P["cta"][1], "size": P["cta"][2], "color": "#ffffff", "font": "Inter",
                                "weight": 800, "bg": "rgba(0,0,0,.6)", "pad": 12, "radius": 10}})
    return {"version": 1, "name": ctx["nome"], "estilo": "História do Reddit",
            "canvas": {"w": W, "h": H, "fps": 30, "bg": "#000"}, "duration": DUR, "template": "generic",
            "fonts": {"Montserrat": "fonts/Montserrat-Black.ttf", "Inter": "fonts/Inter.ttf"},
            "audio": {"voice": {"src": ctx["voz"], "volume": 1.0, "start": 0}},
            "tracks": [{"id": "fundo", "name": "Gameplay"}, {"id": "visual", "name": "Card Reddit"}, {"id": "legenda", "name": "Legenda"}],
            "items": items, "_origem": {"fabrica": "EDITOR VIDEOS/fabrica/estilos/reddit-story/preencher.py"}}
