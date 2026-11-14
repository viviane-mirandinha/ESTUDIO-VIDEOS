# preencher.py — estilo "broll-documentario" (estilo novo, genérico, escrito do zero para o Estúdio de Vídeos)
# Entrada: ctx = {nome, titulo, canal, duracao, words, shots:[{s,e,texto,img|clip}], voz, cta_tempos, pasta, idioma, ollama, modelo}
# Saída: edit.json (template generic, FORMATO.md)
#
# Regras do estilo:
#  - 1 cena por trecho falado (~2,5-5 s): foto em tela cheia com Ken Burns (zoom/pan alternando) ou clipe com zoom leve
#  - troca com fade de 0,4 s; "flash" branco suave a cada 4ª troca; vinheta + degradê embaixo p/ ler a legenda
#  - legenda palavra por palavra (3 palavras), fonte condensada, palavras-chave em amarelo
#  - título de abertura grande, selo do canal no canto, CTA de like nas falas de CTA, cartão final com o canal
#  - letra: títulos ≥ 48 px, apoio ≥ 24 px (regra do editor)
import shutil
from pathlib import Path

FONTES_PC = Path.home() / "AppData" / "Local" / "Microsoft" / "Windows" / "Fonts"
FONTE_ARQ = "burbank-big-condensed-black.otf"
MOTIONS = ["zoom_in", "pan_right", "zoom_out", "pan_left", "zoom_in", "pan_up", "zoom_out", "pan_down"]
X = 0.4   # sobreposição do fade entre cenas
AMARELO = "#ffd400"
TXT = {
    "pt-BR": {"like": "Deixa o like se está curtindo", "insc": "Inscreva-se para o próximo"},
    "en-US": {"like": "Hit like if you're enjoying this", "insc": "Subscribe for the next one"},
    "es-MX": {"like": "Dale like si te está gustando", "insc": "Suscríbete para el próximo"},
}


def _fonte(pasta: Path):
    """Copia a fonte condensada do PC para o projeto (se existir). Sem ela, cai para Arial Black."""
    src = FONTES_PC / FONTE_ARQ
    if not src.exists():   # sem a fonte do PC: Anton (Google Fonts, OFL; condensada e pesada) que vai no pacote
        src = next((p / "recursos" / "fontes" / "Anton-Regular.ttf" for p in Path(__file__).resolve().parents
                    if (p / "recursos" / "fontes" / "Anton-Regular.ttf").is_file()), src)
    if src.exists():
        (pasta / "fonts").mkdir(exist_ok=True)
        dst = pasta / "fonts" / src.name
        if not dst.exists():
            shutil.copy2(src, dst)
        return {"Doc": f"fonts/{src.name}"}, "Doc"
    return {}, "Arial Black"


def preencher(ctx):
    DUR = round(float(ctx["duracao"]), 2)
    pasta = Path(ctx["pasta"])
    fonts, F = _fonte(pasta)
    tx = TXT.get(ctx.get("idioma") or "pt-BR", TXT["pt-BR"])
    shots = [s for s in ctx["shots"] if s.get("img") or s.get("clip")]
    items = []
    for i, sh in enumerate(shots):
        st = round(sh["s"] if i else 0.0, 2)
        en = round(shots[i + 1]["s"], 2) + X if i + 1 < len(shots) else DUR
        base = {"id": f"c{i}", "track": "fundo", "label": sh["texto"][:40], "start": st, "dur": round(en - st, 3),
                "in": "fade" if i else "none", "out": "none"}
        if sh.get("clip"):
            items.append({**base, "type": "video", "props": {"src": sh["clip"], "fill": True, "fit": "cover", "volume": 0,
                                                             "motion": "zoom_in", "motion_amount": 0.06}})
        else:
            items.append({**base, "type": "image", "props": {"src": sh["img"], "fill": True, "fit": "cover",
                                                             "motion": MOTIONS[i % len(MOTIONS)], "motion_amount": [0.12, 0.16, 0.1, 0.18][i % 4]}})
        if i and i % 4 == 0:
            items.append({"id": f"fl{i}", "type": "html", "track": "visual", "label": "Flash", "start": round(st - 0.05, 2), "dur": 0.32,
                          "in": "fade", "out": "fade", "props": {"html": "<div class='fl'></div>", "css": ".fl{width:1280px;height:720px;background:#fff;opacity:.55}",
                                                                 "fill": True}})
    items.append({"id": "vinheta", "type": "html", "track": "visual", "label": "Vinheta + degradê", "start": 0, "dur": DUR, "in": "none", "out": "none",
                  "props": {"html": "<div class='vg'></div>", "fill": True,
                            "css": ".vg{width:1280px;height:720px;background:radial-gradient(ellipse at center,rgba(0,0,0,0) 58%,rgba(0,0,0,.55) 100%),"
                                   "linear-gradient(to top,rgba(0,0,0,.62) 0%,rgba(0,0,0,0) 34%)}"}})
    # textos
    items.append({"id": "titulo", "type": "text", "track": "textos", "label": "Título de abertura", "start": 0.3, "dur": 3.6, "in": "slide_up", "out": "fade",
                  "props": {"text": ctx["titulo"], "x": 640, "y": 330, "w": 1120, "size": 76, "color": "#ffffff", "font": F, "weight": 900,
                            "align": "center", "upper": True, "shadow": True, "stroke": "#000000", "stroke_w": 4, "line": 1.05}})
    items.append({"id": "selo", "type": "text", "track": "textos", "label": "Selo do canal", "start": 0, "dur": round(DUR - 3.4, 2), "in": "fade", "out": "fade",
                  "props": {"text": ctx["canal"], "x": 150, "y": 46, "w": 260, "size": 24, "color": "#ffffff", "font": F, "weight": 900, "align": "left",
                            "upper": True, "bg": "rgba(0,0,0,.45)", "pad": 6, "radius": 8, "shadow": False}})
    for k, t in enumerate((ctx.get("cta_tempos") or [])[:2]):
        items.append({"id": f"cta{k}", "type": "text", "track": "textos", "label": f"CTA like {k + 1}", "start": round(t, 2), "dur": 3.0,
                      "in": "pop", "out": "fade",
                      "props": {"text": "👍 " + tx["like"], "x": 640, "y": 92, "w": 760, "size": 32, "color": "#111111", "font": F, "weight": 900,
                                "align": "center", "bg": AMARELO, "pad": 10, "radius": 40, "shadow": False}})
    kws = []
    try:
        kws = ctx["ollama"].palavras_chave(ctx.get("roteiro", ""), 10, modelo=ctx.get("modelo")) if ctx.get("ollama") else []
    except Exception:
        kws = []
    items.append({"id": "legenda", "type": "caption", "track": "legenda", "label": "Legenda", "start": 0, "dur": round(DUR - 3.4, 2), "in": "none", "out": "none",
                  "props": {"words_file": "words.json", "per_group": 3, "x": 640, "y": 628, "size": 58, "color": "#ffffff", "dim": "rgba(255,255,255,.62)",
                            "hl_color": AMARELO, "keywords": kws, "font": F, "weight": 900, "stroke": "#000000", "stroke_w": 5, "upper": True}})
    items.append({"id": "fim_fundo", "type": "html", "track": "visual", "label": "Cartão final (fundo)", "start": round(DUR - 3.4, 2), "dur": 3.4, "in": "fade", "out": "none",
                  "props": {"html": "<div class='ff'></div>", "css": ".ff{width:1280px;height:720px;background:rgba(5,6,10,.78)}", "fill": True}})
    items.append({"id": "fim_canal", "type": "text", "track": "textos", "label": "Cartão final: canal", "start": round(DUR - 3.1, 2), "dur": 2.9, "in": "pop", "out": "none",
                  "props": {"text": ctx["canal"], "x": 640, "y": 330, "w": 1100, "size": 84, "color": "#ffffff", "font": F, "weight": 900, "align": "center",
                            "upper": True, "shadow": True}})
    items.append({"id": "fim_insc", "type": "text", "track": "textos", "label": "Cartão final: inscreva-se", "start": round(DUR - 2.8, 2), "dur": 2.6, "in": "slide_up", "out": "none",
                  "props": {"text": tx["insc"], "x": 640, "y": 430, "w": 800, "size": 34, "color": "#111111", "font": F, "weight": 900, "align": "center",
                            "bg": AMARELO, "pad": 10, "radius": 40, "shadow": False, "upper": True}})
    return {"version": 1, "name": ctx["nome"], "estilo": "B-roll documentário",
            "canvas": {"w": 1280, "h": 720, "fps": 30, "bg": "#05060a"}, "duration": DUR, "template": "generic", "fonts": fonts,
            "audio": {"voice": {"src": ctx["voz"], "volume": 1.0, "start": 0},
                      **({"music": {"src": ctx["musica"], "volume": 0.12, "start": 0, "fade_out": 2.0, "duck": True}} if ctx.get("musica") else {})},
            "tracks": [{"id": "fundo", "name": "Cenas (fotos / clipes)"}, {"id": "visual", "name": "Vinheta / flash"},
                       {"id": "legenda", "name": "Legenda"}, {"id": "textos", "name": "Textos"}],
            "items": items, "_origem": {"fabrica": "EDITOR VIDEOS/fabrica/estilos/broll-documentario/preencher.py", "creditos": "img/creditos.json"}}
