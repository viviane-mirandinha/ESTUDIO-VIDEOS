# cortes.py — ferramenta "Fábrica de cortes" do Estúdio (vídeo longo falado → cortes 9:16 com legenda). Escrito do zero.
# 100% local, zero token Claude: yt-dlp (link) → ffmpeg (áudio) → faster-whisper (palavras com tempo) → escolha dos trechos
# (modo "ia": regras pré-selecionam e o Ollama dá nota + título; modo "regras": energia da voz + gancho/pergunta/número)
# → cada corte vira um projeto do editor (edit.json 1080x1920) → build_from_edit --render.
#
#   python cortes.py --pasta <projeto>     (lê <projeto>\pedido.json)
# Progresso: linhas "@@<pct>|<mensagem>".
import argparse
import json
import re
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import ajustes, fala, ollama  # noqa: E402
from lib.transcrever import transcrever  # noqa: E402
from lib.util import BUILD, ler_json, log, run, salvar_json, slug  # noqa: E402

W, H = 1080, 1920
AMARELO = "#ffd400"
FONTES_PC = Path.home() / "AppData" / "Local" / "Microsoft" / "Windows" / "Fonts"
FONTE = "burbank-big-condensed-black.otf"


def prog(pct, msg):
    print(f"@@{int(pct)}|{msg}", flush=True)


def _fonte(pasta: Path):
    src = FONTES_PC / FONTE
    if not src.exists():   # sem a fonte do PC: Anton (Google Fonts, OFL; condensada e pesada) que vai no pacote
        src = next((p / "recursos" / "fontes" / "Anton-Regular.ttf" for p in Path(__file__).resolve().parents
                    if (p / "recursos" / "fontes" / "Anton-Regular.ttf").is_file()), src)
    if src.exists():
        (pasta / "fonts").mkdir(exist_ok=True)
        if not (pasta / "fonts" / src.name).exists():
            shutil.copy2(src, pasta / "fonts" / src.name)
        return {"Corte": f"fonts/{src.name}"}, "Corte"
    return {}, "Impact"


def partir_segmentos(manter, words, max_seg=4.0):
    """Divide trechos longos (sem cortar o vídeo: o pedaço seguinte continua de onde o outro parou) pra o zoom poder mudar de tempos em tempos.
    Corta só no vão entre duas palavras."""
    out = []
    for a, b in manter:
        while b - a > max_seg * 1.45:
            alvo = a + max_seg
            melhor = None
            for i, w in enumerate(words[:-1]):
                if a + 2.0 < w["e"] < b - 1.6:
                    meio = (w["e"] + words[i + 1]["s"]) / 2
                    if melhor is None or abs(meio - alvo) < abs(melhor - alvo):
                        melhor = meio
            corte = melhor if melhor is not None else alvo
            out.append((round(a, 3), round(corte, 3)))
            a = corte
        out.append((round(a, 3), round(b, 3)))
    return out


def edit_corte(pasta: Path, clip: str, info: dict, dur: float, titulo: str, enquadramento: str, canal: str, nome: str, kws=None, manter=None, zoom=False):
    """edit.json 9:16 de um corte. 'desfocado' = vídeo inteiro no meio + o mesmo vídeo desfocado no fundo;
    'centro' = recorte do centro ocupando a tela toda. Legenda 2 palavras por vez, grande (≥ 84 px).
    manter = trechos [(início, fim)] do clip que ficam (silêncio e repetição já tirados); zoom = aproxima/afasta a cada trecho."""
    fonts, F = _fonte(pasta)
    items = []
    ar = (info["h"] / info["w"]) if info.get("w") else 9 / 16
    manter = manter or [(0.0, dur)]
    cheia = enquadramento == "centro" or ar >= 1.2   # vídeo já em pé → tela cheia
    vh = round(W * ar)
    t = 0.0
    for k, (a, b) in enumerate(manter):
        d = round(b - a, 3)
        mo, amt = "none", 0.0
        if zoom:
            mo, amt = ("zoom_in", 0.04) if k % 2 == 0 else (("pan_left" if (k // 2) % 2 == 0 else "pan_right"), 0.13)
        trim = round(a, 3)
        if cheia:
            items.append({"id": f"v{k}", "type": "video", "track": "fundo", "label": f"Trecho {k + 1}", "start": round(t, 3), "dur": d, "in": "none", "out": "none",
                          "props": {"src": clip, "fill": True, "fit": "cover", "volume": 1, "trim": trim, "motion": mo, "motion_amount": amt}})
        else:
            items.append({"id": f"bg{k}", "type": "video", "track": "fundo", "label": f"Fundo {k + 1}", "start": round(t, 3), "dur": d, "in": "none", "out": "none",
                          "props": {"src": clip, "fill": True, "fit": "cover", "volume": 0, "blur": 34, "brilho": 0.5, "trim": trim}})
            items.append({"id": f"v{k}", "type": "video", "track": "video", "label": f"Trecho {k + 1}", "start": round(t, 3), "dur": d, "in": "none", "out": "none",
                          "props": {"src": clip, "x": W / 2, "y": H / 2, "w": W, "h": vh, "fit": "cover", "volume": 1, "trim": trim, "motion": mo, "motion_amount": amt}})
        t += d
    dur = round(t, 3)
    if cheia:
        tit_y, cap_y = 300, 1380
    else:
        tit_y = max(330, round(H / 2 - vh / 2 - 210))
        cap_y = min(1560, round(H / 2 + vh / 2 + 190))
    items.append({"id": "titulo", "type": "text", "track": "textos", "label": "Título do corte", "start": 0, "dur": dur, "in": "pop", "out": "none",
                  "props": {"text": titulo, "x": W / 2, "y": tit_y, "w": 980, "size": 78, "color": "#ffffff", "font": F, "weight": 900, "align": "center",
                            "upper": True, "bg": "rgba(0,0,0,.6)", "pad": 18, "radius": 22, "shadow": False, "line": 1.05}})
    items.append({"id": "legenda", "type": "caption", "track": "legenda", "label": "Legenda", "start": 0, "dur": dur, "in": "none", "out": "none",
                  "props": {"words_file": "words.json", "per_group": 2, "x": W / 2, "y": cap_y, "size": 92, "color": "#ffffff", "dim": "#ffffff",
                            "hl_color": AMARELO, "keywords": kws or [], "font": F, "weight": 900, "stroke": "#000000", "stroke_w": 7, "upper": True}})
    if canal:
        items.append({"id": "selo", "type": "text", "track": "textos", "label": "Selo do canal", "start": 0, "dur": dur, "in": "fade", "out": "none",
                      "props": {"text": canal, "x": W / 2, "y": 1800, "w": 700, "size": 40, "color": "#ffffff", "font": F, "weight": 900,
                                "align": "center", "upper": True, "bg": "rgba(0,0,0,.45)", "pad": 6, "radius": 8, "shadow": False}})
    return {"version": 1, "name": nome, "canvas": {"w": W, "h": H, "fps": 30, "bg": "#000000"}, "duration": round(dur, 2), "template": "generic",
            "estilo": "Fábrica de cortes · " + ("tela cheia" if enquadramento == "centro" else "fundo desfocado"), "ferramenta": "Fábrica de cortes",
            "fonts": fonts, "audio": {}, "tracks": [{"id": "fundo", "name": "Fundo"}, {"id": "video", "name": "Vídeo"}, {"id": "legenda", "name": "Legenda"},
                                                     {"id": "textos", "name": "Textos"}], "items": items}


def notas_ia(cands, modelo, idioma):
    """Ollama dá nota 0-10 (gancho sem contexto, ideia completa, fecho) + título curto. Em lotes de 4 (cabe no qwen 7b)."""
    lingua = ajustes.idioma_llm(idioma if idioma in ajustes.IDIOMAS else "pt-BR")
    for k in range(0, len(cands), 4):
        lote = cands[k:k + 4]
        txt = "\n\n".join(f"TRECHO {n + 1} ({int(c['e'] - c['s'])} s):\n{c['texto'][:1400]}" for n, c in enumerate(lote))
        prompt = f"""Você é editor de cortes virais (Shorts/Reels/TikTok) de podcasts e lives.
Avalie cada trecho abaixo como um corte vertical independente. Critérios:
- a PRIMEIRA frase prende sozinha, sem precisar do contexto do episódio (gancho);
- a ideia é completa: começa e termina, não para no meio;
- termina com uma conclusão, virada ou frase de efeito;
- é interessante para quem não conhece o programa.
Para cada trecho dê "nota" de 0 a 10 (seja exigente), "titulo" (até 7 palavras, chamativo, fiel ao que é dito, em {lingua}, sem inventar)
e "motivo" (1 frase curta em português do Brasil explicando a nota).

{txt}

Responda SOMENTE JSON: {{"trechos": [{{"n": 1, "nota": 0, "titulo": "...", "motivo": "..."}}, ...]}}"""
        try:
            d = ollama._json_seguro(ollama.gerar(prompt, modelo, json_mode=True, temperatura=0.2, num_predict=700, timeout=300))
        except Exception as e:
            log(f"Ollama falhou na nota dos trechos: {str(e)[:120]}")
            continue
        for t in d.get("trechos") or []:
            try:
                n = int(t.get("n")) - 1
            except Exception:
                continue
            if 0 <= n < len(lote):
                c = lote[n]
                try:
                    c["nota_ia"] = max(0.0, min(10.0, float(t.get("nota"))))
                except Exception:
                    pass
                tit = re.sub(r'["“”]', "", str(t.get("titulo") or "")).strip().rstrip(".")
                if tit:
                    c["titulo"] = tit[:70]
                if t.get("motivo"):
                    c["motivo_ia"] = str(t["motivo"])[:200]


def titulo_regra(texto):
    p = re.split(r"(?<=[.!?…])\s+", texto.strip())[0]
    w = p.split()
    t = " ".join(w[:7]).rstrip(",.;:")
    return t + ("…" if len(w) > 7 else "")


def preparar_fonte(proj, ped, t_ini_min, precisa_wav=True):
    """Baixa/copia o vídeo e transcreve (pula o que já existe). Devolve (fonte, info, words, wav)."""
    aj = ajustes.ler()
    t0 = time.time()
    fonte = proj / "fonte.mp4"
    if not fonte.exists():
        if ped.get("url"):
            prog(2, "Baixando o vídeo do link (pode levar alguns minutos)…")
            secao = None
            if ped.get("de") or ped.get("ate"):
                secao = f"*{ped.get('de') or 0}-{ped.get('ate') or 'inf'}"
            fala.baixar_link(ped["url"], fonte, secao)
        else:
            prog(2, "Copiando o seu vídeo…")
            src = Path(ped["arquivo"])
            try:
                shutil.move(str(src), str(fonte))
            except Exception:
                shutil.copy2(src, fonte)
    info = fala.probe(fonte)
    if not info["audio"]:
        raise SystemExit("Esse vídeo não tem som — a Fábrica de cortes precisa de fala.")
    log(f"fonte: {info}")
    t_ini_min["baixar"] = round((time.time() - t0) / 60, 2)

    t0 = time.time()
    wav = proj / "audio.wav"
    if not (proj / "words.json").exists():
        prog(8, "Separando o áudio…")
        fala.extrair_audio(fonte, wav)
        prog(12, f"Transcrevendo {int(info['dur'] // 60)} min de fala (Whisper na placa de vídeo)…" if info['dur'] >= 60 else f"Transcrevendo {int(info['dur'])} s de fala (Whisper na placa de vídeo)…")
        idioma = ped.get("idioma") or aj["idioma"]
        transcrever(wav, proj / "words.json", idioma=fala.WHISPER_LANG.get(idioma, "pt"))
    elif precisa_wav and not wav.exists():
        fala.extrair_audio(fonte, wav)
    t_ini_min["transcrever"] = round((time.time() - t0) / 60, 2)
    return fonte, info, ler_json(proj / "words.json"), wav


def escolher(proj, ped, info, words, wav, modelo, minutos):
    """Acha os melhores momentos. Devolve a lista de candidatos (melhores primeiro), já com 'marcado' nos N pedidos."""
    aj = ajustes.ler()
    t0 = time.time()
    prog(40, "Procurando os melhores momentos…")
    n_cortes = max(1, min(10, int(ped.get("n") or 3)))
    dmin, dmax = float(ped.get("dur_min") or 30), float(ped.get("dur_max") or 60)
    fr = fala.frases(words)
    if not fr:
        raise SystemExit("Não ouvi fala nesse vídeo — a Fábrica de cortes precisa de gente falando.")
    ener, passo = fala.energia(wav)
    base_db = float(sorted(ener)[len(ener) // 2]) if ener else -30
    cands = []
    for i, j in fala.janelas(fr, dmin, dmax):
        jan = fr[i:j + 1]
        nota, motivos = fala.nota_regras(jan, ener, passo, base_db)
        cands.append({"s": jan[0]["s"], "e": jan[-1]["e"], "texto": " ".join(f["texto"] for f in jan), "nota_regras": nota, "nota": nota,
                      "motivos": motivos, "titulo": titulo_regra(jan[0]["texto"])})
    if not cands:   # vídeo curto demais pra janela pedida → usa o vídeo todo (ou o que der)
        jan = fr
        nota, motivos = fala.nota_regras(jan, ener, passo, base_db)
        cands = [{"s": jan[0]["s"], "e": jan[-1]["e"], "texto": " ".join(f["texto"] for f in jan), "nota_regras": nota, "nota": nota,
                  "motivos": motivos, "titulo": titulo_regra(jan[0]["texto"])}]
    modo = ped.get("modo") or "ia"
    pool = cands
    if modo == "ia":
        pre = fala.sem_sobrepor(cands, min(14, n_cortes * 3 + 3))
        prog(46, f"A IA local está avaliando {len(pre)} trechos (gancho, ideia completa, fecho)…")
        notas_ia(pre, modelo, ped.get("idioma") or aj["idioma"])
        for c in pre:
            if "nota_ia" in c:
                c["nota"] = round(0.7 * c["nota_ia"] + 0.3 * c["nota_regras"], 1)
        pool = pre
    # na revisão a pessoa vê mais opções do que pediu (os N melhores já vêm marcados)
    revisar = ped.get("revisar", True)
    lista = fala.sem_sobrepor(pool, min(12, n_cortes * 2 + 2) if revisar else n_cortes)
    lista.sort(key=lambda c: -c["nota"])
    for k, c in enumerate(lista):
        c["marcado"] = k < n_cortes
        c["motivo"] = c.get("motivo_ia") or (", ".join(c.get("motivos") or []) or "trecho completo")
    minutos["escolher"] = round((time.time() - t0) / 60, 2)
    log("candidatos: " + "; ".join(f"{c['s']:.0f}-{c['e']:.0f}s nota {c['nota']}" for c in lista))
    return lista, modo


def ajustar_trecho(words, s, e):
    """Gruda o início e o fim nas palavras (nunca corta no meio de uma palavra). Devolve (s, e) ou None se não tem fala."""
    ws = [w for w in words if w["s"] >= s - 0.05 and w["e"] <= e + 0.3]
    if not ws:
        return None
    return ws[0]["s"], ws[-1]["e"]


def tirar_pausas(clip, words_clip, dur, repetidas=True):
    """Trechos [(ini, fim)] do corte que ficam: silêncios longos e frases repetidas saem (usa a mesma regra do Editor de vídeo falado)."""
    import falado
    sils, _ = fala.silencios(clip, 0.35)
    fr = fala.frases(words_clip)
    rt = fala.retakes(fr) if repetidas and fr else []
    manter = falado.trechos_mantidos(words_clip, dur, sils, rt, fr, min_sil=0.5)
    if rt:   # a regra de "frase repetida" pode confundir uma repetição de ênfase com erro → se tirar demais, não usa
        sem = falado.trechos_mantidos(words_clip, dur, sils, [], fr, min_sil=0.5)
        if sum(b - a for a, b in manter) < 0.85 * sum(b - a for a, b in sem):
            manter, rt = sem, []
    return manter or [(0.0, dur)], [fr[k]["texto"] for k in rt]


def montar_cortes(proj, ped, info, words, fonte, selecao, modelo, modo, minutos, t_ini):
    """Cada trecho escolhido vira um corte: recorta, tira pausas/repetições, põe zoom, legenda e título, renderiza."""
    import falado
    t0 = time.time()
    canal = (ped.get("canal") or "").strip()
    enq = ped.get("enquadramento") or "desfocado"
    tirar = bool(ped.get("silencio", True))
    zoom = bool(ped.get("zoom", True))
    # refazendo os cortes: some o que saiu da vez anterior
    try:
        ant = ler_json(proj / "cortes.json")
        for c in ant.get("cortes") or []:
            shutil.rmtree(proj / c["pasta"], ignore_errors=True)
        if ant.get("intro"):
            shutil.rmtree(proj / ant["intro"], ignore_errors=True)
    except Exception:
        pass
    (proj / "cortes.json").unlink(missing_ok=True)
    lista = []
    for k, c in enumerate(selecao):
        base_pct = 6 + 88 * k / len(selecao)
        ab = ajustar_trecho(words, float(c["s"]), float(c["e"]))
        if not ab:
            log(f"trecho {c['s']}-{c['e']} sem fala, pulado")
            continue
        s, e = ab
        prog(base_pct, f"Corte {k + 1} de {len(selecao)}: recortando…")
        titulo = (c.get("titulo") or "").strip() or titulo_regra(" ".join(w["w"] for w in words if s <= w["s"] <= e))
        d = proj / f"corte-{k + 1:02d}-{slug(titulo, 30) or 'corte'}"
        d.mkdir(exist_ok=True)
        ini = max(0.0, s - 0.2)
        dur = round(min(info["dur"], e + 0.45) - ini, 3)
        fala.cortar(fonte, d / "clip.mp4", ini, dur)
        ws = fala.palavras_no_trecho(words, s, e, ini)
        salvar_json(d / "words_clip.json", ws)
        texto = " ".join(w["w"] for w in ws)
        repetidas = []
        if tirar:
            prog(base_pct + 1, f"Corte {k + 1} de {len(selecao)}: tirando pausas e repetições…")
            try:
                manter, repetidas = tirar_pausas(d / "clip.mp4", ws, dur)
            except Exception as ex:
                log(f"pausas: {str(ex)[:150]}")
                manter = [(0.0, dur)]
        else:
            manter = [(0.0, dur)]
        novo = round(sum(b - a for a, b in manter), 2)
        salvar_json(d / "words.json", falado.remapear(ws, manter))
        segs = partir_segmentos(manter, ws) if zoom else manter
        kws = []
        try:
            kws = ollama.palavras_chave(texto, 5, modelo=modelo) if modo == "ia" else []
        except Exception:
            kws = []
        nome = f"Corte {k + 1:02d} - {titulo}"
        salvar_json(d / "edit.json", edit_corte(d, "clip.mp4", info, dur, titulo, enq, canal, nome, kws, manter=segs, zoom=zoom))
        prog(base_pct + 3, f"Corte {k + 1} de {len(selecao)}: renderizando (legenda + título)…")
        run([sys.executable, BUILD, str(d), "--render"], timeout=3600)
        lista.append({"n": len(lista) + 1, "pasta": d.name, "titulo": titulo, "nota": c.get("nota"), "nota_regras": c.get("nota_regras"), "nota_ia": c.get("nota_ia"),
                      "motivo": c.get("motivo") or "trecho escolhido por você", "inicio": round(s, 2), "fim": round(e, 2), "duracao": novo,
                      "tirou_s": round(max(0.0, dur - novo), 1), "repeticoes": len(repetidas), "trechos": len(segs), "zoom": zoom, "texto": texto[:600]})
        salvar_json(proj / "cortes.json", {"cortes": lista, "modo": modo, "enquadramento": enq})
    if not lista:
        raise SystemExit("Nenhum dos trechos escolhidos tem fala. Escolha outros momentos.")
    minutos["montar_render"] = round((time.time() - t0) / 60, 2)

    # intro-gancho (opcional): começo dos 3 melhores cortes em sequência ---------------------
    if ped.get("intro") and len(lista) >= 2:
        t0 = time.time()
        prog(96, "Montando a intro com os melhores momentos…")
        d = proj / "intro-melhores-momentos"
        shutil.rmtree(d, ignore_errors=True)
        d.mkdir(exist_ok=True)
        fonts, F = _fonte(d)
        items, ws_all, t = [], [], 0.0
        for k, c in enumerate(lista[:3]):
            cw = ler_json(proj / c["pasta"] / "words_clip.json")
            fr_c = fala.frases(cw)
            fim = min(5.0, max(3.0, fr_c[0]["e"] + 0.25 if fr_c else 4.0))
            shutil.copy2(proj / c["pasta"] / "clip.mp4", d / f"m{k + 1}.mp4")
            items.append({"id": f"m{k + 1}", "type": "video", "track": "fundo", "label": f"Momento {k + 1}", "start": round(t, 3), "dur": round(fim, 3),
                          "in": "fade" if k else "none", "out": "none", "props": {"src": f"m{k + 1}.mp4", "fill": True, "fit": "cover", "volume": 1, "trim": 0}})
            ws_all += [{"w": w["w"], "s": round(w["s"] + t, 2), "e": round(min(w["e"], fim) + t, 2)} for w in cw if w["e"] <= fim]
            t += fim
        salvar_json(d / "words.json", ws_all)
        titulo_intro = (ped.get("programa") or "Os melhores momentos").strip()
        items.append({"id": "titulo", "type": "text", "track": "textos", "label": "Título", "start": 0, "dur": round(t, 2), "in": "pop", "out": "none",
                      "props": {"text": titulo_intro, "x": W / 2, "y": 300, "w": 980, "size": 80, "color": "#ffffff", "font": F, "weight": 900,
                                "align": "center", "upper": True, "bg": "rgba(0,0,0,.6)", "pad": 18, "radius": 22, "shadow": False}})
        items.append({"id": "legenda", "type": "caption", "track": "legenda", "label": "Legenda", "start": 0, "dur": round(t, 2), "in": "none", "out": "none",
                      "props": {"words_file": "words.json", "per_group": 2, "x": W / 2, "y": 1380, "size": 92, "color": "#ffffff", "dim": "#ffffff",
                                "hl_color": AMARELO, "keywords": [], "font": F, "weight": 900, "stroke": "#000000", "stroke_w": 7, "upper": True}})
        salvar_json(d / "edit.json", {"version": 1, "name": "Intro - " + titulo_intro, "canvas": {"w": W, "h": H, "fps": 30, "bg": "#000"},
                                      "duration": round(t, 2), "template": "generic", "estilo": "Fábrica de cortes · intro", "ferramenta": "Fábrica de cortes",
                                      "fonts": fonts, "audio": {}, "tracks": [{"id": "fundo", "name": "Momentos"}, {"id": "legenda", "name": "Legenda"},
                                                                              {"id": "textos", "name": "Textos"}], "items": items})
        run([sys.executable, BUILD, str(d), "--render"], timeout=3600)
        minutos["intro"] = round((time.time() - t0) / 60, 2)
        salvar_json(proj / "cortes.json", {"cortes": lista, "modo": modo, "enquadramento": enq, "intro": d.name})
    (proj / "audio.wav").unlink(missing_ok=True)
    tirou = sum(c["tirou_s"] for c in lista)
    rel = {"ferramenta": "Fábrica de cortes", "estilo": "Fábrica de cortes", "titulo": ped.get("titulo") or proj.name,
           "inicio": datetime.fromtimestamp(t_ini).astimezone().isoformat(timespec="seconds"), "fim": datetime.now().astimezone().isoformat(timespec="seconds"),
           "minutos": round((time.time() - t_ini) / 60, 2), "minutos_por_etapa": minutos, "duracao_fonte": round(info["dur"], 1),
           "cortes": len(lista), "tokens": 0, "custo_usd": 0,
           "observacoes": f"FÁBRICA DE CORTES (zero token Claude): whisper local + escolha por {'Ollama ' + modelo + ' + regras' if modo == 'ia' else 'regras (energia, gancho, pergunta, número)'}; "
                          f"{len(lista)} cortes 9:16 ({enq}); pausas/repetições {'tiradas (' + str(round(tirou)) + ' s)' if tirar else 'mantidas'}; zoom {'ligado' if zoom else 'desligado'}; render HyperFrames"}
    salvar_json(proj / "RELATORIO.json", rel)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pasta", required=True)
    ap.add_argument("--fase", choices=["tudo", "analisar", "renderizar"], default="tudo")
    a = ap.parse_args()
    proj = Path(a.pasta)
    ped = ler_json(proj / "pedido.json")
    aj = ajustes.ler()
    modelo = ped.get("modelo") or aj["modelo_ollama"]
    t_ini = time.time()
    minutos = {}
    fase = a.fase
    if fase == "tudo" and ped.get("revisar", True):
        fase = "analisar"   # com revisão ligada, o pedido novo para depois de escolher e espera a pessoa conferir

    fonte, info, words, wav = preparar_fonte(proj, ped, minutos, precisa_wav=fase != "renderizar")

    if fase in ("analisar", "tudo"):
        lista, modo = escolher(proj, ped, info, words, wav, modelo, minutos)
        if fase == "analisar":
            plano = {"fonte": {"w": info.get("w"), "h": info.get("h"), "dur": round(info["dur"], 1)}, "origem": "link" if ped.get("url") else "arquivo",
                     "modo": modo, "n": max(1, min(10, int(ped.get("n") or 3))), "dur_min": ped.get("dur_min"), "dur_max": ped.get("dur_max"),
                     "candidatos": [{"id": k + 1, "s": round(c["s"], 2), "e": round(c["e"], 2), "titulo": c["titulo"], "nota": c["nota"], "nota_ia": c.get("nota_ia"),
                                     "nota_regras": c["nota_regras"], "motivo": c["motivo"], "texto": c["texto"][:1500], "marcado": c["marcado"]}
                                    for k, c in enumerate(lista)]}
            salvar_json(proj / "plano.json", plano)
            prog(100, "Momentos escolhidos — falta você conferir.")
            print("PLANO PRONTO", flush=True)
            return
        selecao = [{"s": c["s"], "e": c["e"], "titulo": c["titulo"], "nota": c["nota"], "nota_regras": c["nota_regras"], "nota_ia": c.get("nota_ia"),
                    "motivo": c["motivo"]} for c in lista]
    else:   # renderizar o que a pessoa conferiu
        selecao = ler_json(proj / "selecao.json")
        modo = ped.get("modo") or "ia"
        prog(4, "Montando os cortes que você escolheu…")
    montar_cortes(proj, ped, info, words, fonte, selecao, modelo, modo, minutos, t_ini)
    prog(100, "Pronto!")
    print("CORTES PRONTOS", flush=True)


if __name__ == "__main__":
    main()
