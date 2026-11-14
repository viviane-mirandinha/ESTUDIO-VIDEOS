# preencher_preset.py — monta o edit.json de um estilo "por preset" (escrito do zero pro Estúdio de Vídeos).
# Usado pelo estilo "short-documentario" (Fábrica de Shorts) e pelos estilos salvos no "Copiar estilo de edição — modo rápido"
# e pelos Extras instalados. Cada estilo só guarda números/cores no estilo.json → "preset"; o desenho fica aqui.
#
# Entrada: ctx = {nome, titulo, canal, duracao, words, shots:[{s,e,texto,img|clip}], voz, cta_tempos, pasta, idioma, ollama, modelo, roteiro}
# Saída: edit.json (template generic, FORMATO.md). Regras do usuário: sem SFX de impacto; títulos ≥ 48 px em 1280x720
# (proporcional no 9:16: legenda ≥ 84 px, título ≥ 72 px em 1080x1920).
import shutil
from pathlib import Path

try:
    from . import elementos as ELEM
except ImportError:   # rodando solto
    import elementos as ELEM

FONTES_PC = [Path.home() / "AppData" / "Local" / "Microsoft" / "Windows" / "Fonts", Path(r"C:\Windows\Fonts"),
             Path.home() / "Library" / "Fonts", Path("/Library/Fonts"), Path("/System/Library/Fonts"),   # macOS
             Path.home() / ".local" / "share" / "fonts", Path("/usr/share/fonts")]                          # Linux
FONTES = {   # nome no preset → (arquivo no PC, família CSS de reserva)
    "condensada": ("burbank-big-condensed-black.otf", "Impact"),
    "impact": ("impact.ttf", "Impact"),
    "arial": ("arialbd.ttf", "Arial"),
    "georgia": ("georgiab.ttf", "Georgia"),
}
MOTIONS = ["zoom_in", "pan_right", "zoom_out", "pan_left", "zoom_in", "pan_up", "zoom_out", "pan_down"]
PADRAO = {
    "formato": "longo",            # longo (1280x720) | short (1080x1920)
    "cor_destaque": "#ffd400",
    "cor_texto": "#ffffff",
    "fundo": "#05060a",
    "fonte": "condensada",
    "legenda": True,
    "legenda_pos": "baixo",        # baixo | centro | topo
    "legenda_palavras": 3,
    "legenda_tamanho": 0,          # 0 = automático
    "legenda_caixa": False,        # caixa escura atrás da legenda
    "titulo_fixo": False,          # título fica no topo o vídeo todo (shorts)
    "zoom": 0.12,                  # força do Ken Burns
    "flash_cada": 4,               # flash suave a cada N trocas (0 = nunca)
    "vinheta": True,
    "cartao_final": True,
    "cta": True,
    "transicao": 0.4,
}
TXT = {
    "pt-BR": {"like": "Deixa o like se está curtindo", "insc": "Inscreva-se para o próximo", "segue": "Segue para mais"},
    "en-US": {"like": "Hit like if you're enjoying this", "insc": "Subscribe for the next one", "segue": "Follow for more"},
    "es-MX": {"like": "Dale like si te está gustando", "insc": "Suscríbete para el próximo", "segue": "Sígueme para más"},
}


def _fonte(pasta: Path, nome):
    arq, reserva = FONTES.get(nome, FONTES["condensada"])
    for base in FONTES_PC:
        src = base / arq
        if src.exists():
            (pasta / "fonts").mkdir(exist_ok=True)
            dst = pasta / "fonts" / arq
            if not dst.exists():
                shutil.copy2(src, dst)
            return {"Preset": f"fonts/{arq}"}, "Preset"
    return {}, reserva


def preencher(ctx, preset=None):
    P = {**PADRAO, **(preset or {})}
    short = P["formato"] == "short"
    W, H = (1080, 1920) if short else (1280, 720)
    DUR = round(float(ctx["duracao"]), 2)
    FIM = (1.6 if short else 3.4) if P["cartao_final"] else 0
    pasta = Path(ctx["pasta"])
    fonts, F = _fonte(pasta, P["fonte"])
    tx = TXT.get(ctx.get("idioma") or "pt-BR", TXT["pt-BR"])
    AC, TC = P["cor_destaque"], P["cor_texto"]
    X = float(P["transicao"])
    shots = [s for s in ctx["shots"] if s.get("img") or s.get("clip")]
    items = []
    for i, sh in enumerate(shots):
        st = round(sh["s"] if i else 0.0, 2)
        en = round(shots[i + 1]["s"], 2) + X if i + 1 < len(shots) else DUR
        base = {"id": f"c{i}", "track": "fundo", "label": sh["texto"][:40], "start": st, "dur": round(en - st, 3),
                "in": "fade" if i and X > 0 else "none", "out": "none"}
        z = float(P["zoom"])
        if sh.get("clip"):
            items.append({**base, "type": "video", "props": {"src": sh["clip"], "fill": True, "fit": "cover", "volume": 0,
                                                             "motion": "zoom_in" if z > 0 else "none", "motion_amount": round(z / 2, 3)}})
        else:
            items.append({**base, "type": "image", "props": {"src": sh["img"], "fill": True, "fit": "cover",
                                                             "motion": MOTIONS[i % len(MOTIONS)] if z > 0 else "none",
                                                             "motion_amount": round(z * [1, 1.3, 0.85, 1.5][i % 4], 3)}})
        n = int(P["flash_cada"] or 0)
        if n and i and i % n == 0:
            items.append({"id": f"fl{i}", "type": "html", "track": "visual", "label": "Flash", "start": round(st - 0.05, 2), "dur": 0.32,
                          "in": "fade", "out": "fade", "props": {"html": "<div class='fl'></div>", "css": f".fl{{width:{W}px;height:{H}px;background:#fff;opacity:.5}}",
                                                                 "fill": True}})
    if P["vinheta"]:
        items.append({"id": "vinheta", "type": "html", "track": "visual", "label": "Vinheta + degradê", "start": 0, "dur": DUR, "in": "none", "out": "none",
                      "props": {"html": "<div class='vg'></div>", "fill": True,
                                "css": f".vg{{width:{W}px;height:{H}px;background:radial-gradient(ellipse at center,rgba(0,0,0,0) 55%,rgba(0,0,0,.55) 100%),"
                                       "linear-gradient(to top,rgba(0,0,0,.55) 0%,rgba(0,0,0,0) 30%),linear-gradient(to bottom,rgba(0,0,0,.45) 0%,rgba(0,0,0,0) 22%)}"}})
    # ---- peças copiadas da referência (Copiar estilo): cores/posição do título, etiquetas de nome/lugar
    EL = P.get("elementos") or []
    el_tit, el_etq = ELEM.por_tipo(EL, "titulo"), ELEM.por_tipo(EL, "etiqueta")
    # ---- título
    fim_txt = round(DUR - FIM, 2)
    if short:
        if P["titulo_fixo"]:
            items.append({"id": "titulo", "type": "text", "track": "textos", "label": "Título (topo)", "start": 0, "dur": fim_txt, "in": "pop", "out": "fade",
                          "props": {"text": ctx["titulo"], "x": W / 2, "y": 250, "w": 960, "size": 76, "color": TC, "font": F, "weight": 900,
                                    "align": "center", "upper": True, "bg": "rgba(0,0,0,.62)", "pad": 18, "radius": 22, "shadow": False, "line": 1.05,
                                    "highlight": [], "hl_color": AC}})
        else:
            items.append({"id": "titulo", "type": "text", "track": "textos", "label": "Título (gancho)", "start": 0.1, "dur": 2.6, "in": "pop", "out": "fade",
                          "props": {"text": ctx["titulo"], "x": W / 2, "y": 520, "w": 980, "size": 92, "color": TC, "font": F, "weight": 900,
                                    "align": "center", "upper": True, "shadow": True, "stroke": "#000000", "stroke_w": 6, "line": 1.05}})
        selo_y, selo_x, selo_w = 1760, W / 2, 700
    else:
        items.append({"id": "titulo", "type": "text", "track": "textos", "label": "Título de abertura", "start": 0.3, "dur": 3.6, "in": "slide_up", "out": "fade",
                      "props": {"text": ctx["titulo"], "x": 640, "y": 330, "w": 1120, "size": 76, "color": TC, "font": F, "weight": 900,
                                "align": "center", "upper": True, "shadow": True, "stroke": "#000000", "stroke_w": 4, "line": 1.05}})
        selo_y, selo_x, selo_w = 46, 150, 260
    if el_tit:   # título no jeito da referência: cor do texto, caixa colorida atrás (se tinha) e altura
        tp = next(i for i in items if i["id"] == "titulo")["props"]
        bg = el_tit.get("cor_fundo") if el_tit.get("caixa") else None
        tp["color"] = ELEM._legivel(el_tit.get("cor_texto") or TC, bg or "#000000")
        if bg:
            tp.update({"bg": bg, "pad": 16, "radius": 12, "shadow": False, "stroke": None})
        if not P["titulo_fixo"] and 0.15 < (el_tit.get("y") or 0) < 0.75:
            tp["y"] = round(H * el_tit["y"])
            leg_y = ({"baixo": 1480, "centro": 1080, "topo": 560} if short else {"baixo": 628, "centro": 380, "topo": 120}).get(P["legenda_pos"], 0)
            if P["legenda"] and abs(tp["y"] - leg_y) < H * 0.2:   # nunca em cima da legenda
                tp["y"] = round(H * (0.27 if leg_y > H * 0.45 else 0.62))
    el_selo = ELEM.por_tipo(EL, "selo")
    if el_selo and not short:
        selo_x = 150 if (el_selo.get("x") or 0) < 0.5 else W - 150
        selo_y = 46 if (el_selo.get("y") or 0) < 0.5 else H - 40
    items.append({"id": "selo", "type": "text", "track": "textos", "label": "Selo do canal", "start": 0, "dur": fim_txt, "in": "fade", "out": "fade",
                  "props": {"text": ctx["canal"], "x": selo_x, "y": selo_y, "w": selo_w, "size": 40 if short else 24, "color": TC, "font": F, "weight": 900,
                            "align": "center" if short else "left", "upper": True, "bg": "rgba(0,0,0,.45)", "pad": 6, "radius": 8, "shadow": False}})
    if P["cta"]:
        for k, t in enumerate((ctx.get("cta_tempos") or [])[:2]):
            items.append({"id": f"cta{k}", "type": "text", "track": "textos", "label": f"CTA like {k + 1}", "start": round(t, 2), "dur": 2.6,
                          "in": "pop", "out": "fade",
                          "props": {"text": "👍 " + tx["like"], "x": W / 2, "y": 470 if short else 92, "w": 940 if short else 760, "size": 52 if short else 32,
                                    "color": "#111111", "font": F, "weight": 900, "align": "center", "bg": AC, "pad": 12, "radius": 40, "shadow": False}})
    if el_etq:
        ocup = [0.0, *(ctx.get("cta_tempos") or [])[:2]]
        items += ELEM.itens_etiquetas(ctx.get("words") or [], W, H, F, AC, el_etq, ocupados=ocup)
    # ---- legenda
    if P["legenda"]:
        kws = []
        try:
            kws = ctx["ollama"].palavras_chave(ctx.get("roteiro", ""), 10, modelo=ctx.get("modelo")) if ctx.get("ollama") else []
        except Exception:
            kws = []
        tam = int(P["legenda_tamanho"] or (108 if short else 60))
        ys = {"baixo": 1480, "centro": 1080, "topo": 560} if short else {"baixo": 628, "centro": 380, "topo": 120}
        cap = {"words_file": "words.json", "per_group": int(P["legenda_palavras"]), "x": W / 2, "y": ys.get(P["legenda_pos"], ys["baixo"]), "size": tam,
               "color": TC, "dim": "rgba(255,255,255,.62)" if int(P["legenda_palavras"]) > 1 else TC, "hl_color": AC, "keywords": kws, "font": F,
               "weight": 900, "stroke": "#000000", "stroke_w": 7 if short else 5, "upper": True}
        if P["legenda_caixa"]:
            cap["bg"] = "rgba(0,0,0,.6)"
        items.append({"id": "legenda", "type": "caption", "track": "legenda", "label": "Legenda", "start": 0, "dur": fim_txt, "in": "none", "out": "none",
                      "props": cap})
    # ---- cartão final
    if FIM:
        items.append({"id": "fim_fundo", "type": "html", "track": "visual", "label": "Cartão final (fundo)", "start": fim_txt, "dur": FIM, "in": "fade", "out": "none",
                      "props": {"html": "<div class='ff'></div>", "css": f".ff{{width:{W}px;height:{H}px;background:rgba(5,6,10,.8)}}", "fill": True}})
        items.append({"id": "fim_canal", "type": "text", "track": "textos", "label": "Cartão final: canal", "start": round(fim_txt + 0.2, 2), "dur": round(FIM - 0.2, 2),
                      "in": "pop", "out": "none",
                      "props": {"text": ctx["canal"], "x": W / 2, "y": H * 0.44, "w": W - 120, "size": 96 if short else 84, "color": TC, "font": F, "weight": 900,
                                "align": "center", "upper": True, "shadow": True}})
        items.append({"id": "fim_insc", "type": "text", "track": "textos", "label": "Cartão final: chamada", "start": round(fim_txt + 0.4, 2), "dur": round(FIM - 0.4, 2),
                      "in": "slide_up", "out": "none",
                      "props": {"text": tx["segue"] if short else tx["insc"], "x": W / 2, "y": H * 0.44 + (150 if short else 100), "w": 860 if short else 800,
                                "size": 56 if short else 34, "color": "#111111", "font": F, "weight": 900, "align": "center",
                                "bg": AC, "pad": 12, "radius": 40, "shadow": False, "upper": True}})
    return {"version": 1, "name": ctx["nome"], "canvas": {"w": W, "h": H, "fps": 30, "bg": P["fundo"]}, "duration": DUR, "template": "generic",
            "fonts": fonts,
            "audio": {"voice": {"src": ctx["voz"], "volume": 1.0, "start": 0},
                      **({"music": {"src": ctx["musica"], "volume": 0.12, "start": 0, "fade_out": 2.0, "duck": True}} if ctx.get("musica") else {})},
            "tracks": [{"id": "fundo", "name": "Cenas (fotos / clipes)"}, {"id": "visual", "name": "Vinheta / flash"},
                       {"id": "legenda", "name": "Legenda"}, {"id": "textos", "name": "Textos"}],
            "items": items, "_origem": {"fabrica": "EDITOR VIDEOS/fabrica/lib/preencher_preset.py", "preset": P, "creditos": "img/creditos.json"}}


# ---------------------------------------------------------------- estilos "por preset" (pasta com estilo.json + este stub)
STUB = '''# preencher.py — estilo por preset (gerado pelo Estúdio de Vídeos). O desenho está em fabrica/lib/preencher_preset.py;
# aqui só se lê o "preset" do estilo.json desta pasta. Pode editar o estilo.json à vontade.
import json
import sys
from pathlib import Path

_AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(_AQUI.parent.parent))   # pasta fabrica
from lib import preencher_preset as _PP  # noqa: E402


def preencher(ctx):
    cfg = json.loads((_AQUI / "estilo.json").read_text(encoding="utf-8-sig"))
    ed = _PP.preencher(ctx, cfg.get("preset"))
    ed["estilo"] = cfg.get("nome_curto") or cfg.get("nome", _AQUI.name).split(" (")[0]
    return ed
'''


def criar_estilo(pasta: Path, cfg: dict):
    """Cria/atualiza uma pasta de estilo por preset (estilo.json + preencher.py stub). Nunca copia código de fora."""
    pasta.mkdir(parents=True, exist_ok=True)
    import json
    (pasta / "estilo.json").write_text(json.dumps(cfg, ensure_ascii=False, indent=1), encoding="utf-8")
    (pasta / "preencher.py").write_text(STUB, encoding="utf-8")
    return pasta
