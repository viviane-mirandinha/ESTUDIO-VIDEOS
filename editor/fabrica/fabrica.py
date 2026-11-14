# fabrica.py — MODO FÁBRICA: gera um vídeo novo completo num estilo já pronto, 100% local (zero token Claude).
#
# python fabrica.py --estilo historia-simples --tema "..." --canal "NOME" [--roteiro arq.txt] [--voz arq.mp3]
#                   [--duracao 60] [--tts auto|qwen3|chatterbox|edge] [--modelo qwen2.5:7b] [--sem-render]
#                   [--out str(__import__("pathlib").Path(__file__).resolve().parents[2] / "VIDEOS")] [--pasta <pasta existente p/ retomar>]
#
# Etapas: roteiro (Ollama) → voz (TTS local) → words.json (faster-whisper GPU) → imagens (Wikimedia/estoque)
#         → preencher.py do estilo → edit.json → build_from_edit.py --render → RELATORIO.json
import argparse
import importlib.util
import json
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import ollama, tts, texto, imagens  # noqa: E402
from lib import ajustes as AJ  # noqa: E402
from lib import claude_api  # noqa: E402
from lib import musica as MUS  # noqa: E402
from lib.transcrever import transcrever  # noqa: E402
from lib.util import canal_na_tela  # noqa: E402
from lib.util import (BUILD, ESTILOS, Cronometro, duracao_audio, frases_do_texto, ler_json, log,  # noqa: E402
                      nome_video, proximo_numero, run, salvar_json, slug)

OUT_PADRAO = next((d for d in (str(__import__("pathlib").Path(__file__).resolve().parents[2] / "VIDEOS"),) if Path(d).exists()),
                  str(__import__("pathlib").Path(__file__).resolve().parents[2] / "VIDEOS"))   # migração C→D (23/10)


def carregar_estilo(nome):
    pasta = ESTILOS / nome
    if not (pasta / "preencher.py").exists():
        disp = ", ".join(p.name for p in ESTILOS.iterdir() if (p / "preencher.py").exists())
        raise SystemExit(f"Estilo '{nome}' não existe. Disponíveis: {disp}")
    cfg = ler_json(pasta / "estilo.json") if (pasta / "estilo.json").exists() else {}
    spec = importlib.util.spec_from_file_location(f"estilo_{slug(nome)}", pasta / "preencher.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return pasta, cfg, mod


def main():
    ap = argparse.ArgumentParser(description="Modo fábrica — vídeo novo num estilo pronto, sem tokens")
    ap.add_argument("--estilo", required=True)
    ap.add_argument("--tema", default="")
    ap.add_argument("--roteiro", help="arquivo .txt com a locução pronta (pula o Ollama)")
    ap.add_argument("--voz", help="áudio da locução pronto (pula o TTS)")
    ap.add_argument("--titulo", default="")
    ap.add_argument("--canal", required=True)
    ap.add_argument("--duracao", type=float, default=60, help="segundos alvo (só quando o roteiro é gerado)")
    ap.add_argument("--tts", default="auto", choices=["auto", "qwen3", "chatterbox", "edge", "fish", "clone", "vsremoto"])
    ap.add_argument("--voz-nome", default=None, help="voz do TTS (ex.: sohee, pt-BR-FranciscaNeural)")
    ap.add_argument("--modelo", default=ollama.MODELO_PADRAO, help="modelo Ollama")
    ap.add_argument("--musica", help="música de fundo: 'auto' (escolhe na biblioteca pelo assunto) ou o caminho de um mp3/wav (opcional, com ducking)")
    ap.add_argument("--musica-nivel", default="baixa", choices=["baixa", "presente"], help="baixa = bem baixinha · presente = se faz notar sem cobrir a voz")
    ap.add_argument("--musica-sem-duck", action="store_true", help="não abaixar a música quando o narrador fala (só vale com --musica-nivel presente)")
    ap.add_argument("--out", default=OUT_PADRAO)
    ap.add_argument("--pasta", help="pasta de projeto existente (retoma etapas já feitas)")
    ap.add_argument("--sem-render", action="store_true")
    ap.add_argument("--formato", default="longo", choices=["longo", "short"], help="short = em pé 9:16 (só estilos com \"formatos\": [..., \"short\"] no estilo.json)")
    ap.add_argument("--regras-json", default="", help="'Suas regras' (guarda de densidade) em JSON: entram no edit.json ANTES do render")
    ap.add_argument("--marca", default="", help="marca d'água deste vídeo (texto discreto, ex.: @meucanal)")
    ap.add_argument("--ref-canal", default="", help="referência: nome do canal copiado (vai pro edit.json)")
    ap.add_argument("--ref-canal-url", default="", help="referência: link do canal copiado")
    ap.add_argument("--ref-video", default="", help="referência: link do vídeo copiado")
    ap.add_argument("--ref-titulo", default="", help="referência: título do vídeo copiado")
    ap.add_argument("--claude-roteiro", action="store_true", help="o Claude escreve o roteiro (chave em Ajustes; gasta centavos; se falhar, usa o Ollama)")
    ap.add_argument("--claude-busca", action="store_true", help="o Claude escolhe as buscas de imagem (chave em Ajustes; se falhar, usa o Ollama)")
    a = ap.parse_args()
    if not a.tema and not a.roteiro:
        raise SystemExit("Informe --tema ou --roteiro")

    cron = Cronometro()
    estilo_dir, cfg, mod = carregar_estilo(a.estilo)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    if a.pasta:
        proj = Path(a.pasta)
        nn = int(proj.name[:2]) if proj.name[:2].isdigit() else proximo_numero(out)
    else:
        nn = proximo_numero(out)
        proj = out / f"{nn:02d}-fabrica-{slug(a.estilo, 20)}-{slug(a.tema or a.titulo or 'video', 28)}"
    proj.mkdir(parents=True, exist_ok=True)
    if a.marca.strip():
        (proj / "marca_dagua.txt").write_text(a.marca.strip()[:60], encoding="utf-8")
    log(f"Projeto: {proj}")
    print(f"PASTA: {proj}", flush=True)   # lido pelo editor (/api/pedido) para achar a pasta criada
    obs = []
    chave_claude = str(AJ.ler().get("anthropic_key") or "").strip()
    modo_claude = claude_api.modo(chave_claude)   # "api" (chave em Ajustes) | "plano" (Claude instalado neste PC) | None
    if (a.claude_roteiro or a.claude_busca) and not modo_claude:
        log("Claude pedido, mas não há chave em Ajustes nem o Claude instalado neste PC — usando o Ollama local")
        a.claude_roteiro = a.claude_busca = False
    elif a.claude_roteiro or a.claude_busca:
        log("Claude: " + ("usando a chave da API (Ajustes)" if modo_claude == "api" else "usando o Claude instalado neste PC (seu plano, sem cobrança extra)"))
    uso_claude = {"tokens_in": 0, "tokens_out": 0, "usd": 0.0, "usd_equiv": 0.0}

    def _soma_uso(u):
        for k in uso_claude:
            uso_claude[k] += u.get(k, 0)

    # (a) roteiro -----------------------------------------------------------
    t0 = time.time()
    rot_path = proj / "roteiro.txt"
    titulo = a.titulo
    if a.roteiro:
        rot = Path(a.roteiro).read_text(encoding="utf-8").strip()
        obs.append("roteiro fornecido pelo usuário")
    elif rot_path.exists() and a.pasta:
        rot = rot_path.read_text(encoding="utf-8").strip()
        if not titulo and (proj / "titulo.txt").exists():
            titulo = (proj / "titulo.txt").read_text(encoding="utf-8").strip()
        obs.append("roteiro reaproveitado da pasta")
    else:
        palavras = int(a.duracao / 60 * cfg.get("palavras_por_minuto", 150))
        r = None
        if a.claude_roteiro:
            try:
                r = claude_api.roteiro(chave_claude, a.tema, palavras, a.canal, cfg.get("roteiro_prompt", ""), regras=cfg.get("regras_roteiro"),
                                       idioma=AJ.idioma_llm())
                _soma_uso(r["uso"])
                obs.append(f"roteiro pelo Claude {claude_api.MODELO} ({len(r['roteiro'].split())} palavras) — revisar fatos antes de publicar")
            except Exception as e:
                log(f"Claude falhou no roteiro ({type(e).__name__}: {str(e)[:160]}) — usando o Ollama local")
                r = None
        if r is None:
            r = ollama.roteiro(a.tema, palavras, a.canal, cfg.get("roteiro_prompt", ""), modelo=a.modelo,
                               regras=cfg.get("regras_roteiro"))
            obs.append(f"roteiro pelo Ollama {a.modelo} ({len(r['roteiro'].split())} palavras) — revisar fatos antes de publicar")
        rot, titulo = r["roteiro"], titulo or r["titulo"]
    if not titulo:
        fr = frases_do_texto(rot)
        titulo = " ".join(fr[0].split()[:9]).rstrip(".,!?") if fr else (a.tema or "Video")
    rot_path.write_text(rot, encoding="utf-8")
    (proj / "titulo.txt").write_text(titulo, encoding="utf-8")
    cron.marca("roteiro", t0)

    # (b) voz ---------------------------------------------------------------
    t0 = time.time()
    voz_rel, motor = None, "pronta"
    if a.voz:
        src = Path(a.voz)
        voz_rel = "voz" + src.suffix.lower()
        shutil.copy2(src, proj / voz_rel)
    else:
        existente = [p for p in ("voz.wav", "voz.mp3") if (proj / p).exists()]
        if existente and a.pasta:
            voz_rel, motor = existente[0], "reaproveitada"
        else:
            p, motor = tts.falar(rot, proj, a.tts, a.voz_nome)
            voz_rel = p.name
    dur_voz = duracao_audio(proj / voz_rel)
    obs.append(f"voz: {motor} ({dur_voz:.1f}s)")
    cron.marca("tts", t0)

    # (c) whisper → words.json ---------------------------------------------
    t0 = time.time()
    wpath = proj / "words.json"
    if wpath.exists() and a.pasta:
        words = ler_json(wpath)
    else:
        words = transcrever(proj / voz_rel, wpath)
    DUR = round(max(dur_voz, words[-1]["e"]) + 1.2, 2)
    cron.marca("whisper", t0)

    # (d) shots + imagens ----------------------------------------------------
    t0 = time.time()
    shots = texto.shots(words, cfg.get("shot_min", 2.4), cfg.get("shot_max", 5.5))
    log(f"{len(shots)} shots de {DUR}s")
    fonte = cfg.get("imagens", "nenhuma")
    if fonte == "wikimedia":
        qpath = proj / "queries.json"
        if qpath.exists() and a.pasta and (proj / "img" / "creditos.json").exists():
            q = ler_json(qpath)
            imgs = [f"img/{c['arquivo']}" for c in ler_json(proj / "img" / "creditos.json")]
            while len(imgs) < len(shots):
                imgs.append(imgs[-1] if imgs else None)
        else:
            trechos = [s["texto"] for s in shots] + [f"(the topic in general: {a.tema or titulo})"]
            q = None
            if a.claude_busca:
                try:
                    q, u = claude_api.queries(chave_claude, trechos, a.tema or titulo, cfg.get("dica_busca", ""))
                    _soma_uso(u)
                    obs.append(f"buscas de imagem pelo Claude {claude_api.MODELO}")
                except Exception as e:
                    log(f"Claude falhou nas buscas de imagem ({type(e).__name__}: {str(e)[:160]}) — usando o Ollama local")
                    q = None
            if q is None:
                q = ollama.queries_imagens(trechos, a.tema or titulo, cfg.get("dica_busca", ""), modelo=a.modelo)
            for i, s in enumerate(shots):   # fala de CTA (like/inscreve) não vira busca: repete a foto anterior
                if i and texto.acha_cta(s["words"]):
                    q[i] = ""
            salvar_json(qpath, q)
            imgs = imagens.baixar_para_shots(q[:-1], proj / "img", fallback_queries=[q[-1]], extra=cfg.get("extra_busca", ""),
                                             preferir=cfg.get("preferir_titulo", []))
        for s, im in zip(shots, imgs):
            s["img"] = im
        n_ok = len({i for i in imgs if i})
        obs.append(f"{n_ok} imagens Wikimedia Commons (img/creditos.json) para {len(shots)} shots")
        # b-roll de VÍDEO (Pexels/Pixabay) quando o estilo aceita clipes e o usuário pôs a chave em Ajustes
        n_clip = 0
        if cfg.get("clipes"):
            try:
                from lib import ajustes as _AJ
                _aj = _AJ.ler()
                chaves = {"pexels": _aj.get("pexels_key"), "pixabay": _aj.get("pixabay_key")}
                if any(chaves.values()):
                    clips = imagens.clipes_para_shots(q[:len(shots)], shots, proj / "clips", chaves, vertical=bool(cfg.get("vertical")))
                    for s, c in zip(shots, clips):
                        if c:
                            s["clip"] = c
                    n_clip = sum(1 for c in clips if c)
                    obs.append(f"{n_clip} clipes de vídeo Pexels/Pixabay (clips/creditos.json); o resto ficou com foto")
            except Exception as e:
                log(f"b-roll de vídeo falhou ({type(e).__name__}) — segue só com fotos")
        if n_ok == 0 and n_clip == 0:
            raise RuntimeError("nenhuma imagem baixada — Wikimedia fora do ar?")
    elif fonte == "gameplay":
        clip = imagens.gameplay(proj / "clips", DUR, seed=nn)
        for s in shots:
            s["clip"] = clip
        obs.append("gameplay sem copyright do estoque estoque/gameplay")
    cron.marca("imagens", t0)

    # (e) preencher → edit.json ---------------------------------------------
    t0 = time.time()
    for item in cfg.get("copiar", []):
        src = estilo_dir / item
        if src.is_dir():
            shutil.copytree(src, proj / item, dirs_exist_ok=True)
        elif src.exists():
            shutil.copy2(src, proj / item)
    mus = None
    if a.musica:   # 🎵 música de fundo: 'auto' escolhe pelo tema+roteiro; senão usa o arquivo enviado. Entra normalizada e com volume seguro.
        try:
            mus = MUS.preparar(proj, "auto" if a.musica == "auto" else "minha", texto=f"{a.tema} {a.titulo} {rot}", estilo=a.estilo,
                               nivel=a.musica_nivel, duck=not a.musica_sem_duck, arquivo=None if a.musica == "auto" else a.musica, duracao=DUR)
        except Exception as e:
            log(f"música de fundo falhou ({type(e).__name__}: {e}) — segue sem música")
        if mus:
            log(f"MUSICA: {mus['titulo']} ({mus['motivo']}) · nível {a.musica_nivel}")
        else:
            log("sem música de fundo (não consegui preparar)")
    nome = nome_video(nn, a.canal, titulo)
    ctx = {"nome": nome, "titulo": titulo, "canal": canal_na_tela(a.canal), "tema": a.tema, "duracao": DUR, "words": words,
           "shots": shots, "voz": voz_rel, "cta_tempos": texto.acha_cta(words), "roteiro": rot, "pasta": proj,
           "musica": mus["arquivo"] if mus else None,
           "modelo": a.modelo, "ollama": ollama,
           "vertical": a.formato == "short" and "short" in cfg.get("formatos", [])}   # 9:16: o preencher.py do estilo monta o canvas em pé
    edit = mod.preencher(ctx)
    edit.setdefault("name", nome)
    if mus:   # vale o que a pessoa escolheu no pedido (volume/abaixar), por cima do que o estilo pôs
        edit.setdefault("audio", {})["music"] = mus["music"]
    if a.regras_json:
        try:
            edit["regras"] = json.loads(a.regras_json)
        except ValueError:
            pass
    if a.ref_canal or a.ref_video or a.ref_canal_url:   # referência obrigatória (FORMATO.md) — vem do pedido
        edit["referencia"] = {"canal": a.ref_canal, "canal_url": a.ref_canal_url, "video": a.ref_video, "titulo": a.ref_titulo}
    salvar_json(proj / "edit.json", edit)
    log(f"edit.json: {len(edit['items'])} itens")
    cron.marca("edit_json", t0)

    # (f) render ------------------------------------------------------------
    t0 = time.time()
    render_s = 0
    if not a.sem_render:
        try:
            run([sys.executable, BUILD, str(proj), "--render"], timeout=3600)
        except RuntimeError as e:   # máquina compartilhada: render cai por falta de memória → espera e tenta de novo
            log(f"render falhou ({str(e)[-200:]}), tentando de novo em 30 s…")
            time.sleep(30)
            run([sys.executable, BUILD, str(proj), "--render"], timeout=3600)
        render_s = int(time.time() - t0)
        final = proj / "final.mp4"
        if final.exists():
            shutil.copy2(final, proj / f"{nome}.mp4")
            log(f"vídeo: {proj / (nome + '.mp4')}")
    else:
        run([sys.executable, BUILD, str(proj)], timeout=600)
    cron.marca("render", t0)

    # (g) relatório ----------------------------------------------------------
    if a.pasta and (proj / "RELATORIO.json").exists():   # retomada: mantém os minutos das etapas já feitas antes
        try:
            antigo = ler_json(proj / "RELATORIO.json").get("minutos_por_etapa", {})
            for k, v in antigo.items():
                if cron.etapas.get(k, 0) < 0.05 and v:
                    cron.etapas[k] = v
        except Exception:
            pass
    tokens = uso_claude["tokens_in"] + uso_claude["tokens_out"]
    custo = round(uso_claude["usd"], 4)   # só a API cobra; pelo plano o custo é 0 (usd_equiv = quanto seria na API)
    equiv = round(uso_claude["usd_equiv"], 4)
    if a.pasta and (proj / "RELATORIO.json").exists():   # retomada: soma o que o Claude já tinha gasto nas etapas feitas antes
        try:
            ant = ler_json(proj / "RELATORIO.json")
            tokens += int(ant.get("tokens") or 0)
            custo = round(custo + float(ant.get("custo_usd") or 0), 4)
        except Exception:
            pass
    if tokens and equiv and not custo:
        modo = f"MODO FÁBRICA (Claude pelo seu plano só no roteiro/busca de imagens: {tokens} tokens, sem cobrança extra — equivaleria a ~US$ {equiv:.3f} na API; o resto é local)"
    elif tokens:
        modo = f"MODO FÁBRICA (Claude só no roteiro/busca de imagens: {tokens} tokens, ~US$ {custo:.3f}; o resto é local)"
    else:
        modo = "MODO FÁBRICA (zero token Claude, só Python local)"
    rel = {"video": nn, "estilo": cfg.get("nome", a.estilo), "fabrica": a.estilo, "titulo": titulo, "canal": a.canal,
           "inicio": cron.inicio.isoformat(timespec="seconds"), "fim": datetime.now().astimezone().isoformat(timespec="seconds"),
           "minutos": cron.total(), "minutos_por_etapa": cron.etapas, "render_segundos": render_s,
           "duracao_video": DUR, "tokens": tokens, "custo_usd": custo,
           "observacoes": modo + ": " + "; ".join(obs) +
                          f"; {len(shots)} shots; edit.json por estilos/{a.estilo}/preencher.py; render build_from_edit.py"}
    salvar_json(proj / "RELATORIO.json", rel)
    log(f"PRONTO em {cron.total()} min de máquina — {proj}")
    print(json.dumps(rel, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
