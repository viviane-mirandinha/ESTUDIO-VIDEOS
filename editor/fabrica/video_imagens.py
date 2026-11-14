# video_imagens.py — ferramenta "Vídeo com imagens" do Estúdio (roteiro / narração / tema → vídeo 16:9 com b-roll).
# 100% local, zero token Claude: Ollama (roteiro e buscas) → TTS → faster-whisper → frases → Wikimedia (+ Pexels/Pixabay
# com chave do usuário) → [Conferir imagens no painel] → edit.json do estilo → build_from_edit --render.
#
#   python video_imagens.py preparar --pasta <projeto>    (lê <projeto>\pedido.json, para em "conferir")
#   python video_imagens.py montar   --pasta <projeto>    (lê cenas.json, escreve edit.json e renderiza)
#
# Progresso no stdout: linhas "@@<pct>|<mensagem>" (lidas pelo painel).
import argparse
import json
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import ajustes, bancos, curto, fatos, ollama, relevancia, texto, tts  # noqa: E402
from lib.transcrever import transcrever  # noqa: E402
from lib.util import BUILD, canal_na_tela, duracao_audio, frases_do_texto, ler_json, log, nome_video, run, salvar_json  # noqa: E402
import fabrica as FAB  # noqa: E402  (reaproveita carregar_estilo)


def prog(pct, msg):
    print(f"@@{int(pct)}|{msg}", flush=True)


def cenario_visual(tema, modelo):
    """Lugar/época que TODA imagem do vídeo deve mostrar, em inglês (CLIP só entende inglês). Vazio se o tema não tiver cenário."""
    try:
        d = ollama._json_seguro(ollama.gerar(
            f'Video topic: "{tema}". In ENGLISH, 2 to 4 words, name the place, era or setting that every image of this video should show '
            f'(examples: "ancient Egypt", "World War II", "modern Japan", "deep ocean"). If there is no visual setting, answer "". '
            f'Answer only JSON {{"setting": "..."}}', modelo, json_mode=True, temperatura=0.1, num_predict=30, timeout=60))
        c = str(d.get("setting") or "").strip().lower()[:40]
    except Exception:
        return ""
    return c if c.isascii() and 1 <= len(c.split()) <= 4 else ""


def checar_cenas(proj, cenas, usados, vertical, prog, assunto="", max_trocas=3):
    """Checagem do arquivo REAL de cada cena (CLIP no quadro da imagem/clipe) contra a busca da cena E o assunto do vídeo.
    Busca genérica ("copper tools") deixava passar foto fora do tema (ferramenta asteca num vídeo do Egito).
    Abaixo do limite: baixa os próximos candidatos aprovados, recheca cada um e fica com o melhor."""
    alvo = [c for c in cenas if c.get("escolha") and not c["escolha"].get("repetida") and c.get("query")]
    if not alvo or not relevancia.clip_ok():
        return None

    def medir(src, q):
        n = relevancia.notas_arquivos([(proj / src, q)])[0]
        t = relevancia.notas_arquivos([(proj / src, assunto)])[0] if assunto else None
        return n, t

    medidas = [medir(c["escolha"]["src"], c["query"]) for c in alvo]
    # tema só vale como critério se for "fotografável" (3+ cenas mostram bem o assunto); tema abstrato não reprova ninguém
    tema_on = bool(assunto) and sum(1 for _, t in medidas if t is not None and t >= relevancia.LIM_TEMA_VISUAL) >= 3

    def boa(n, t):
        return n >= relevancia.LIM_CHECA and (not tema_on or (t or 0) >= relevancia.LIM_TEMA)

    def peso(n, t):
        return n + ((t or 0) if tema_on else 0)

    trocadas = fracas = 0
    for k, (c, (nota, nt)) in enumerate(zip(alvo, medidas)):
        prog(96 + 3 * k / len(alvo), f"Checando cena {c['i'] + 1} contra a fala…")
        if nota is None:
            continue
        c["escolha"]["checagem"] = round(nota, 3)
        if nt is not None:
            c["escolha"]["checagem_tema"] = round(nt, 3)
        if boa(nota, nt):
            continue
        melhor_ok, melhor_peso, melhor = False, peso(nota, nt), c["escolha"]
        for cand in [x for x in c.get("candidatos", []) if x.get("passa") and x["url"] not in usados][:max_trocas]:
            usados.add(cand["url"])
            try:
                src = bancos.baixar(cand, proj, c["i"], c["e"] - c["s"], vertical=vertical)
            except Exception:
                continue
            n2, t2 = medir(src, c["query"])
            n2 = n2 or 0.0
            if (boa(n2, t2), peso(n2, t2)) > (melhor_ok, melhor_peso):
                if melhor is not c["escolha"]:
                    (proj / melhor["src"]).unlink(missing_ok=True)
                melhor_ok, melhor_peso = boa(n2, t2), peso(n2, t2)
                melhor = {**{x: cand.get(x) for x in ("tipo", "fonte", "titulo", "licenca", "pagina", "url", "thumb")},
                          "nota_clip": cand.get("clip"), "src": src, "checagem": round(n2, 3),
                          **({"checagem_tema": round(t2, 3)} if t2 is not None else {})}
            else:
                (proj / src).unlink(missing_ok=True)
            if melhor_ok:
                break
        if melhor is not c["escolha"]:
            log(f"checagem {c['i'] + 1:02d}: trocou '{str(c['escolha'].get('titulo'))[:40]}' por '{str(melhor.get('titulo'))[:40]}'")
            velha = c["escolha"].get("url")
            c["escolha"] = {**melhor, "trocou_de": c["escolha"].get("titulo")}
            trocadas += 1
            for r in cenas:   # cenas que repetem a imagem trocada passam a repetir a nova
                if r is not c and (r.get("escolha") or {}).get("repetida") and r["escolha"].get("url") == velha:
                    r["escolha"] = {**c["escolha"], "repetida": True}
        if not melhor_ok:
            c["escolha"]["fraca"] = True
            fracas += 1
    return {"checadas": len(alvo), "trocadas": trocadas, "fracas": fracas, "assunto": assunto if tema_on else ""}


def _creditos_txt(proj, creditos):
    """CREDITOS.txt pronto pra colar na descrição: 1 linha por imagem/clipe, agrupado por banco, sem repetir."""
    por_fonte, vistos = {}, set()
    for c in creditos:
        chave = c.get("pagina") or c.get("titulo") or c.get("arquivo")
        if chave in vistos:
            continue
        vistos.add(chave)
        linha = " — ".join(x for x in ((c.get("titulo") or "")[:90], c.get("licenca"), c.get("pagina")) if x)
        por_fonte.setdefault(c.get("fonte") or "Outros", []).append(linha or c.get("arquivo", ""))
    if not por_fonte:
        return
    partes = ["Créditos das imagens e clipes:"]
    for fonte, linhas in por_fonte.items():
        partes += ["", f"[{fonte}]", *(f"• {l}" for l in linhas)]
    (proj / "CREDITOS.txt").write_text("\n".join(partes) + "\n", encoding="utf-8")


def _regras_idioma(idioma):
    lang = ajustes.idioma_llm(idioma)
    r = ollama.REGRAS_COPY.replace("português do Brasil", lang)
    if not idioma.startswith("en"):
        return r
    return r.replace("7. Sem palavras em inglês.", "7.")


def _grafia_do_roteiro(words, roteiro):
    """Alinha as palavras do Whisper com o roteiro que a voz leu: onde o Whisper errou a grafia (nomes, números),
    usa a palavra do roteiro mantendo o tempo do áudio. Só troca 1 por 1 (mesma quantidade), nunca inventa tempo."""
    import difflib
    import re
    norm = lambda t: re.sub(r"[^\w]", "", t.lower())
    R = roteiro.split()
    a, b = [norm(w.get("w", "")) for w in words], [norm(x) for x in R]
    trocas = 0
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == "replace" and i2 - i1 == j2 - j1 and i2 - i1 <= 3:
            for k in range(i2 - i1):
                if difflib.SequenceMatcher(None, a[i1 + k], b[j1 + k]).ratio() >= 0.5:   # parecida = erro de grafia, não fala diferente
                    words[i1 + k]["w"] = R[j1 + k]
                    trocas += 1
        elif op == "equal":
            for k in range(i2 - i1):
                if words[i1 + k].get("w") != R[j1 + k]:
                    words[i1 + k]["w"] = R[j1 + k]   # mesma palavra: pega a pontuação/maiúscula do roteiro
    return words, trocas


def preparar(proj: Path):
    t_ini = time.time()
    ped = ler_json(proj / "pedido.json")
    aj = ajustes.ler()
    modelo = ped.get("modelo") or aj["modelo_ollama"]
    idioma = ped.get("idioma") or aj["idioma"]
    estilo_dir, cfg, _mod = FAB.carregar_estilo(ped["estilo"])
    vertical = bool(cfg.get("vertical"))   # Fábrica de Shorts (9:16)
    if cfg.get("formato_livre"):           # estilo que serve pros dois (ex.: Stickman Studio): o pedido escolhe
        vertical = ped.get("formato") == "9:16"
    minutos = {}
    obs = []

    # 1) texto ---------------------------------------------------------------
    t0 = time.time()
    modo = ped.get("modo", "tema")
    titulo = (ped.get("titulo") or "").strip()
    rot = ""
    if modo == "tema":
        palavras = max(60, int(float(ped.get("duracao") or 60) / 60 * cfg.get("palavras_por_minuto", 150)))
        prog(3, "Procurando fatos reais sobre o tema (Wikipedia)…")
        ref = fatos.buscar(ped["tema"], idioma, modelo=modelo) if cfg.get("fatos", True) else None
        if ref and cfg.get("fatos") == "conferir":
            try:
                d = ollama._json_seguro(ollama.gerar(
                    f'Tema do vídeo: "{ped["tema"]}". Artigo da Wikipedia: "{ref["titulo"]}". Início do artigo: "{ref.get("texto", "")[:600]}". '
                    'Esse artigo explica o ASSUNTO do tema (não só tem uma palavra parecida, ex.: uma cidade com o mesmo nome)? '
                    'Responda só JSON {"sobre_o_tema": true|false}', modelo, json_mode=True, temperatura=0.0, num_predict=20, timeout=90))
                if d.get("sobre_o_tema") is False:
                    obs.append(f"Wikipedia “{ref['titulo']}” descartada (não é sobre o tema)")
                    log(f"fatos: '{ref['titulo']}' não é sobre '{ped['tema']}' — sem referência")
                    ref = None
            except Exception:
                pass
        if ref:
            salvar_json(proj / "fontes.json", ref)
            obs.append(f"fatos de referência: Wikipedia “{ref['titulo']}” ({ref['url']})")
        else:
            obs.append("sem fatos de referência (Wikipedia não respondeu) — conferir tudo")
        prog(5, "Escrevendo o roteiro com a IA local (1-2 min)…")
        if vertical:
            r = curto.roteiro_short(ped["tema"], float(ped.get("duracao") or 45), ped.get("canal", ""), modelo=modelo, idioma=idioma,
                                    fatos=fatos.bloco_prompt(ref))
        else:
            r = ollama.roteiro(ped["tema"], palavras, ped.get("canal", ""), cfg.get("roteiro_prompt", ""), modelo=modelo,
                               regras=_regras_idioma(idioma) + fatos.bloco_prompt(ref))
        rot, titulo = r["roteiro"], titulo or r["titulo"]
        obs.append(f"roteiro pelo Ollama {modelo} ({len(rot.split())} palavras) — CONFIRA OS FATOS antes de publicar")
    elif modo == "roteiro":
        rot = (ped.get("roteiro") or "").strip()
        obs.append("roteiro colado pelo usuário")
    rot_ref = (ped.get("roteiro_ref") or "").strip() if modo == "audio" else ""
    if rot_ref:   # narração feita em outra IA + o roteiro que ela leu: referência pras buscas e pra grafia da legenda
        rot = rot_ref
        obs.append("narração do usuário + roteiro de referência (legenda e tempos saem do áudio)")
    if rot:
        (proj / "roteiro.txt").write_text(rot, encoding="utf-8")
    minutos["roteiro"] = round((time.time() - t0) / 60, 2)
    if ped.get("so_roteiro"):   # “gerar a voz em outra IA”: só escreve o roteiro e para aqui
        if not titulo:
            fr = frases_do_texto(rot)
            titulo = " ".join(fr[0].split()[:8]).rstrip(".,!?") if fr else ped.get("tema", "")
        (proj / "titulo.txt").write_text(titulo, encoding="utf-8")
        prog(100, "Roteiro pronto!")
        return

    # 2) voz -----------------------------------------------------------------
    t0 = time.time()
    if modo == "audio":
        prog(16, "Copiando a sua narração…")
        src = Path(ped["audio"])
        voz_rel = "voz" + src.suffix.lower()
        shutil.copy2(src, proj / voz_rel)
        motor = "áudio do usuário"
    else:
        prog(16, "Gravando a narração (voz)…")
        motor_voz, _, nome_voz = (ped.get("voz") or aj["voz"]).partition(":")
        p, motor = tts.falar(rot, proj, motor_voz or "auto", nome_voz or None)
        voz_rel = p.name
    dur_voz = duracao_audio(proj / voz_rel)
    obs.append(f"voz: {motor} ({dur_voz:.1f}s)")
    minutos["voz"] = round((time.time() - t0) / 60, 2)

    # 3) whisper -------------------------------------------------------------
    t0 = time.time()
    prog(34, "Sincronizando a legenda com a voz (Whisper)…")
    words = transcrever(proj / voz_rel, proj / "words.json")
    if rot_ref:
        words, trocas = _grafia_do_roteiro(words, rot_ref)
        if trocas:
            salvar_json(proj / "words.json", words)
            obs.append(f"legenda: {trocas} palavra(s) do Whisper corrigidas pela grafia do roteiro")
    if not rot:
        rot = " ".join(w["w"] for w in words)
        (proj / "roteiro.txt").write_text(rot, encoding="utf-8")
    if not titulo:
        if modo == "audio" and ped.get("tema"):
            titulo = ped["tema"]
        else:
            fr = frases_do_texto(rot)
            titulo = " ".join(fr[0].split()[:8]).rstrip(".,!?") if fr else "Vídeo"
    (proj / "titulo.txt").write_text(titulo, encoding="utf-8")
    minutos["whisper"] = round((time.time() - t0) / 60, 2)

    # 4) frases → buscas → imagens -------------------------------------------
    t0 = time.time()
    shots = texto.shots(words, cfg.get("shot_min", 2.6), cfg.get("shot_max", 5.0))
    if cfg.get("sem_imagens"):   # estilo desenhado em código (Stickman): sem banco de imagens, sem "conferir"
        cenas = [{"i": i, "s": round(s["s"], 2), "e": round(s["e"], 2), "texto": s["texto"], "query": "", "candidatos": [], "escolha": None}
                 for i, s in enumerate(shots)]
        obs.append(f"{len(cenas)} cenas desenhadas em código (sem banco de imagens)")
        salvar_json(proj / "cenas.json", {"estado": "montar", "estilo": ped["estilo"], "titulo": titulo, "voz": voz_rel, "duracao_voz": dur_voz,
                                          "permite_video": False, "vertical": vertical, "cenas": cenas, "minutos": minutos, "obs": obs,
                                          "inicio": datetime.fromtimestamp(t_ini).astimezone().isoformat(timespec="seconds")})
        prog(100, "Roteiro, voz e legenda prontos")
        print("PREPARADO", flush=True)
        return
    prog(48, f"Escolhendo o que mostrar em cada uma das {len(shots)} cenas…")
    tema = ped.get("tema") or titulo
    q = bancos.queries([s["texto"] for s in shots] + [f"(the topic in general: {tema})"], tema, cfg.get("dica_busca", ""), modelo=modelo)
    geral = q[-1]
    q = q[:-1]
    # mesma busca em cenas seguidas = o modelo "travou" no tema: refaz a busca dessas cenas uma a uma
    for i in range(1, len(q)):
        if q[i] and q[i].lower() == q[i - 1].lower() and not texto.acha_cta(shots[i]["words"]):
            novo = bancos.query_unica(shots[i]["texto"], tema, evitar=[q[i - 1]], modelo=modelo)
            if novo and novo.lower() != q[i - 1].lower():
                log(f"busca {i + 1:02d}: repetida '{q[i]}' → '{novo}'")
                q[i] = novo
    # assunto principal (vale pros dois formatos): peso extra no CLIP e base do fallback neutro
    assunto = ""
    try:
        d = ollama._json_seguro(ollama.gerar(f'What is the main concrete subject (the thing that should appear in every image) of this video topic? '
                                             f'Answer in English, 1 or 2 words, singular. Topic: "{tema}". Answer only JSON {{"subject": "..."}}',
                                             modelo, json_mode=True, temperatura=0.1, num_predict=30, timeout=60))
        assunto = str(d.get("subject") or "").strip().lower()[:30]
    except Exception:
        pass
    if len(assunto.split()) > 3:
        assunto = ""
    if vertical and assunto:   # short = 1 assunto só: toda busca leva o assunto (evita "grey juveniles" → foto de outro bicho)
        base = assunto.split()[-1][:5]
        q = [x if not x or base in x.lower() else f"{assunto} {x}"[:60] for x in q]
        log(f"assunto do short em toda busca: {assunto}")
    # nome próprio citado na cena tem peso maior: entra na busca e conta ponto na conferência
    ents_video = relevancia.entidades(f"{titulo}. {tema}. {rot}", max_n=40)
    # fallback do tema = nome mais citado no roteiro (+ assunto); a busca "geral" do Ollama às vezes sai genérica demais
    txt_fold = relevancia._fold(f"{titulo} {tema} {rot}")
    ents_video.sort(key=lambda e: -txt_fold.count(relevancia._fold(e)))
    if ents_video:
        geral = f"{ents_video[0]} {assunto}".strip() if assunto and not relevancia.tokens(assunto) <= relevancia.tokens(ents_video[0]) else ents_video[0]
        log(f"fallback do tema: '{geral}'")
    tema_video = " ".join([assunto, tema] + ents_video[:8])   # fonte ruidosa (YouTube CC/Archive) precisa citar isso no título
    ents_cena = []
    for i, s in enumerate(shots):
        tk = relevancia.tokens(s["texto"])
        ents_cena.append([e for e in ents_video if relevancia.tokens(e) and relevancia.tokens(e) <= tk])
        if q[i] and ents_cena[i]:
            q2 = relevancia.reforcar_busca(q[i], ents_cena[i])
            if q2 != q[i]:
                log(f"busca {i + 1:02d}: '{q[i]}' → '{q2}' (nome citado na cena)")
                q[i] = q2
    for i, s in enumerate(shots):
        if i and texto.acha_cta(s["words"]):
            q[i] = ""   # fala de CTA: repete a cena anterior
    # cenário do vídeo na busca genérica: "copper tools" → "ancient egypt copper tools" (teste 07/11 trazia ferramenta asteca)
    cenario = cenario_visual(tema, modelo)
    if cenario:
        tk_cen = relevancia.tokens(cenario)
        for i in range(len(q)):
            if q[i] and not ents_cena[i] and not (tk_cen & relevancia.tokens(q[i])):
                q[i] = f"{cenario} {q[i]}"[:60]
        log(f"cenário do vídeo nas buscas genéricas: {cenario}")
    chaves = {"pexels": aj.get("pexels_key"), "pixabay": aj.get("pixabay_key")}
    # clipe de vídeo só dos bancos curados (Pexels/Pixabay, chave opcional). Sem chave = só fotos: no teste de 01/11 os clipes
    # "livres" do YouTube CC/Archive entraram fora do assunto (vlog com "coffee" no título, logo de loja) — não vale o risco.
    com_video = bool(cfg.get("clipes")) and any(chaves.values())
    usados, cenas = set(), []
    geral_cands = None     # fallback NEUTRO do tema (busca geral), baixado 1 vez só
    cache_nome = {}        # busca só pelo nome próprio citado (1 vez por nome)
    n_fallback = n_repete = 0
    for i, s in enumerate(shots):
        prog(52 + 44 * i / max(1, len(shots)), f"Buscando imagens… cena {i + 1} de {len(shots)}")
        cena = {"i": i, "s": round(s["s"], 2), "e": round(s["e"], 2), "texto": s["texto"], "query": q[i] or "", "candidatos": [], "escolha": None}
        if q[i]:
            cands = bancos.candidatos(q[i], chaves, videos=com_video, preferir=cfg.get("preferir_titulo", []), extra=cfg.get("extra_busca", ""),
                                      vertical=vertical)
            opcoes = relevancia.aprovados(cands, usados, q[i], ents_cena[i], assunto, querer_video=com_video and i % 2 == 0, tema=tema_video)
            if not opcoes and ents_cena[i]:   # a cena cita alguém/algum lugar: busca só o nome (retrato, foto do lugar)
                nome = max(ents_cena[i], key=len)
                if nome not in cache_nome:
                    cache_nome[nome] = bancos.candidatos(nome, chaves, preferir=cfg.get("preferir_titulo", []), vertical=vertical)
                # confere contra a FRASE da cena (com o nome), não só o nome: "Brasil" sozinho trazia mapa de dengue
                opcoes = relevancia.aprovados(cache_nome[nome], usados, q[i], [nome], assunto, tema=tema_video)
                if opcoes:
                    log(f"img {i + 1:02d}: nada bateu com '{q[i]}' → busca pelo nome citado ('{nome}')")
                    cands = cands + [c for c in cache_nome[nome] if c not in cands][:6]
            if not opcoes:   # a melhor imagem da cena já foi usada mais atrás (não nas 2 últimas cenas)? reaproveita
                recentes = {c["escolha"]["url"] for c in cenas[-2:] if c.get("escolha")}
                extra = cache_nome.get(max(ents_cena[i], key=len), []) if ents_cena[i] else []
                opcoes = [c for c in relevancia.aprovados(cands + extra, recentes, q[i], ents_cena[i], assunto) if c["url"] in usados][:1]
                if opcoes:
                    log(f"img {i + 1:02d}: reaproveita imagem que bate com '{q[i]}'")
            if not opcoes:   # nada bateu com a frase → imagem neutra do TEMA (nunca o 1º resultado qualquer)
                if geral_cands is None:
                    geral_cands = bancos.candidatos(geral, chaves, videos=com_video, preferir=cfg.get("preferir_titulo", []), vertical=vertical)
                    if assunto and relevancia.tokens(assunto) - relevancia.tokens(geral):
                        geral_cands += bancos.candidatos(assunto, chaves, preferir=cfg.get("preferir_titulo", []), vertical=vertical)
                opcoes = relevancia.aprovados(geral_cands, usados, geral, ents_video[:3], assunto, tema=tema_video)
                if not opcoes:   # todas as do tema já usadas: reaproveita uma do tema (nunca a cena anterior fora de contexto)
                    recentes = {c["escolha"]["url"] for c in cenas[-2:] if c.get("escolha")}
                    opcoes = relevancia.aprovados(geral_cands, recentes, geral, ents_video[:3], assunto, tema=tema_video)[:1]
                if opcoes:
                    n_fallback += 1
                    log(f"img {i + 1:02d}: nada bateu com '{q[i]}' → imagem do tema ('{geral}')")
                    cands = cands + [c for c in geral_cands if c not in cands][:6]
            cena["candidatos"] = sorted(cands, key=lambda c: -c.get("relev", -99))
            for esc in opcoes[:3]:   # download falhou (Wikimedia às vezes devolve vazio) → próxima opção que também bate
                ja = next((c["escolha"] for c in cenas if c.get("escolha") and c["escolha"].get("url") == esc["url"]), None)
                if ja:   # reaproveitada: mesmo arquivo, sem baixar de novo
                    cena["escolha"] = {**ja, "repetida": True}
                    break
                try:
                    src = bancos.baixar(esc, proj, i, s["e"] - s["s"], vertical=vertical)
                    usados.add(esc["url"])
                    cena["escolha"] = {**{k: esc.get(k) for k in ("tipo", "fonte", "titulo", "licenca", "pagina", "url", "thumb")}, "nota_clip": esc.get("clip"), "src": src}
                    log(f"img {i + 1:02d}: '{q[i]}' → {esc['fonte']}: {str(esc['titulo'])[:60]} (clip={esc.get('clip')})")
                    break
                except Exception as e:
                    usados.add(esc["url"])
                    log(f"img {i + 1:02d}: download falhou ({str(e)[:80]}) → tenta a próxima")
        if not cena["escolha"] and cenas:
            ant = next((c["escolha"] for c in reversed(cenas) if c["escolha"]), None)
            if ant:
                cena["escolha"] = {**ant, "repetida": True}
                n_repete += 1
        cenas.append(cena)
    t_chk = time.time()
    checagem = checar_cenas(proj, cenas, usados, vertical, prog, assunto=cenario)
    if checagem:
        minutos["checagem"] = round((time.time() - t_chk) / 60, 2)
        obs.append(f"Checagem: {checagem['checadas']} cenas conferidas no arquivo real, {checagem['trocadas']} trocadas"
                   + (f", {checagem['fracas']} ainda fracas (marcadas ⚠ em 'Conferir imagens')" if checagem["fracas"] else ""))
    if bancos.DESCARTADOS:
        mot = {}
        for d in bancos.DESCARTADOS:
            mot[d["motivo"]] = mot.get(d["motivo"], 0) + 1
        obs.append(f"Clipes limpos: {len(bancos.DESCARTADOS)} descartado(s) — " + ", ".join(f"{n}× {m}" for m, n in mot.items()))
    if n_fallback or n_repete:
        obs.append(f"{n_fallback} cena(s) sem imagem que batesse com a frase → imagem do tema; {n_repete} repetiram a anterior (confira em 'Conferir imagens')")
    if not any(c["escolha"] for c in cenas):
        raise RuntimeError("Nenhuma imagem encontrada — a internet ou o Wikimedia está fora do ar?")
    # 1ª cena sem imagem (busca falhou) → usa a primeira que existir
    prim = next(c["escolha"] for c in cenas if c["escolha"])
    for c in cenas:
        if not c["escolha"]:
            c["escolha"] = {**prim, "repetida": True}
        else:
            break
    minutos["imagens"] = round((time.time() - t0) / 60, 2)
    obs.append(f"{len(usados)} imagens/clipes para {len(cenas)} cenas (bancos livres: Wikimedia, Openverse, Archive.org{' + Pexels/Pixabay' if any(chaves.values()) else ''})")
    salvar_json(proj / "cenas.json", {"estado": "conferir", "estilo": ped["estilo"], "titulo": titulo, "voz": voz_rel, "duracao_voz": dur_voz,
                                      "permite_video": bool(cfg.get("clipes")), "vertical": vertical, "cenas": cenas, "minutos": minutos, "obs": obs,
                                      "checagem": checagem,
                                      "inicio": datetime.fromtimestamp(t_ini).astimezone().isoformat(timespec="seconds")})
    if not (proj / "edit.json").exists():   # card em "Meus vídeos" (⏳ conferir imagens) até o render
        nn = int(proj.name[:2]) if proj.name[:2].isdigit() else 1
        salvar_json(proj / "edit.json", {"version": 1, "name": nome_video(nn, ped.get("canal") or "", titulo),
                                         "canvas": {"w": 1080, "h": 1920, "fps": 30, "bg": "#05060a"} if vertical else {"w": 1280, "h": 720, "fps": 30, "bg": "#05060a"},
                                         "duration": round(dur_voz + 1.2, 2), "template": "generic",
                                         "estilo": f"{'Fábrica de Shorts' if vertical else 'Vídeo com imagens'} · {cfg.get('nome', ped['estilo']).split(' (')[0]}",
                                         "ferramenta": "Fábrica de Shorts" if vertical else "Vídeo com imagens", "audio": {"voice": {"src": voz_rel, "volume": 1.0, "start": 0}},
                                         "tracks": [{"id": "fundo", "name": "Cenas"}], "items": []})
    prog(100, "Imagens prontas — falta conferir")
    print("PREPARADO", flush=True)


def _pecas_extras(edit, ped, cfg, cenas, words, ctx):
    """'Extras na tela' do formulário: caixinha de número/data (tempo de cada palavra) e crédito da imagem por cena.
    Ligados por padrão; cores vêm das peças do estilo copiado, se tiver."""
    op = {"numeros": True, "credito": True, **(ped.get("extras_tela") or {})}
    try:
        from lib import elementos as ELEM
        W, H = edit["canvas"]["w"], edit["canvas"]["h"]
        its = edit.setdefault("items", [])
        if any(str(i.get("id", "")).startswith(("fato", "cred")) for i in its):
            return
        EL = (cfg.get("preset") or {}).get("elementos") or []
        tit = next((i for i in its if i.get("type") == "text" and i.get("props", {}).get("font")), None)
        fonte = tit["props"]["font"] if tit else "Impact"
        dest = (cfg.get("preset") or {}).get("cor_destaque") or "#ffd400"
        if not any(t["id"] == "textos" for t in edit.get("tracks", [])):
            edit.setdefault("tracks", []).append({"id": "textos", "name": "Textos"})
        if op["numeros"]:
            ocup = [0.0, *(ctx.get("cta_tempos") or [])[:2]] + [i["start"] for i in its if str(i.get("id", "")).startswith(("etq", "cta"))]
            novos = ELEM.itens_numeros(words, W, H, fonte, dest, ELEM.por_tipo(EL, "numero"), ocupados=ocup)
            its += novos
            log(f"caixinhas de número: {len(novos)}")
        if op["credito"]:
            novos = ELEM.itens_creditos(cenas, W, H, fonte, ELEM.por_tipo(EL, "credito"), ped.get("idioma") or "pt-BR")
            its += novos
            log(f"créditos por cena: {len(novos)}")
    except Exception as e:   # extra nunca derruba o vídeo
        log(f"extras na tela: pulei ({str(e)[:150]})")


def montar(proj: Path, amostra=0.0):
    """amostra > 0: renderiza só os primeiros N segundos numa pasta à parte (não mexe no projeto)."""
    t_ini = time.time()
    ped = ler_json(proj / "pedido.json")
    aj = ajustes.ler()
    modelo = ped.get("modelo") or aj["modelo_ollama"]
    cj = ler_json(proj / "cenas.json")
    words = ler_json(proj / "words.json")
    estilo_dir, cfg, mod = FAB.carregar_estilo(cj.get("estilo") or ped["estilo"])
    prog(5, "Montando as cenas…")
    pad = cfg.get("pad_fim", 2.4 if ped["estilo"] == "broll-documentario" else 0)
    DUR = round(max(cj.get("duracao_voz") or 0, words[-1]["e"]) + 1.2 + float(pad), 2)
    vertical = bool(cj.get("vertical")) if cfg.get("formato_livre") else bool(cfg.get("vertical"))
    ferramenta = cfg.get("ferramenta") or ("Fábrica de Shorts" if vertical else "Vídeo com imagens")
    shots, creditos = [], []
    for c in cj["cenas"]:
        e = c.get("escolha") or {}
        sh = {"s": c["s"], "e": c["e"], "texto": c["texto"], "words": [w for w in words if c["s"] - 0.01 <= w["s"] <= c["e"] + 0.01]}
        if e.get("tipo") == "video" and cfg.get("clipes"):
            sh["clip"] = e["src"]
        elif e.get("src"):
            sh["img"] = e["src"] if e.get("tipo") != "video" else None
        shots.append(sh)
        if e.get("src") and not e.get("repetida"):
            creditos.append({"arquivo": Path(e["src"]).name, "query": c.get("query", ""), "titulo": e.get("titulo", ""), "fonte": e.get("fonte", ""),
                             "licenca": e.get("licenca", ""), "pagina": e.get("pagina", "")})
    for k, sh in enumerate(shots):   # clipe num estilo só de fotos → foto anterior
        if not sh.get("img") and not sh.get("clip"):
            ant = next((x for x in reversed(shots[:k]) if x.get("img") or x.get("clip")), None) or next((x for x in shots if x.get("img") or x.get("clip")), None)
            if ant:
                sh["img"], sh["clip"] = ant.get("img"), ant.get("clip")
    (proj / "img").mkdir(exist_ok=True)
    salvar_json(proj / "img" / "creditos.json", creditos)
    _creditos_txt(proj, creditos)
    for item in cfg.get("copiar", []):
        src = estilo_dir / item
        if src.is_dir():
            shutil.copytree(src, proj / item, dirs_exist_ok=True)
        elif src.exists():
            shutil.copy2(src, proj / item)
    nn = int(proj.name[:2]) if proj.name[:2].isdigit() else 1
    titulo = cj.get("titulo") or "Vídeo"
    nome = nome_video(nn, ped.get("canal") or "", titulo)
    rot = (proj / "roteiro.txt").read_text(encoding="utf-8") if (proj / "roteiro.txt").exists() else ""
    ctx = {"nome": nome, "titulo": titulo, "canal": canal_na_tela(ped.get("canal")), "tema": ped.get("tema", ""), "duracao": DUR, "words": words,
           "shots": shots, "voz": cj["voz"], "cta_tempos": texto.acha_cta(words), "roteiro": rot, "pasta": proj, "musica": None,
           "modelo": modelo, "ollama": ollama, "idioma": ped.get("idioma") or aj["idioma"], "vertical": vertical}
    edit = mod.preencher(ctx)
    _pecas_extras(edit, ped, cfg, cj["cenas"], words, ctx)
    edit.setdefault("name", nome)
    edit["ferramenta"] = ferramenta
    if amostra:
        return _amostra(proj, edit, float(amostra))
    salvar_json(proj / "edit.json", edit)
    log(f"edit.json: {len(edit['items'])} itens")
    cj["estado"] = "renderizando"
    salvar_json(proj / "cenas.json", cj)

    prog(12, "Renderizando o vídeo…")
    t0 = time.time()
    try:
        run([sys.executable, BUILD, str(proj), "--render"], timeout=3600)
    except RuntimeError as e:
        log(f"render falhou ({str(e)[-200:]}), tentando de novo em 30 s…")
        time.sleep(30)
        run([sys.executable, BUILD, str(proj), "--render"], timeout=3600)
    render_s = int(time.time() - t0)
    final = proj / "final.mp4"
    if final.exists():
        shutil.copy2(final, proj / f"{nome}.mp4")
    cj["estado"] = "pronto"
    salvar_json(proj / "cenas.json", cj)
    minutos = dict(cj.get("minutos") or {})
    minutos["montar_render"] = round((time.time() - t_ini) / 60, 2)
    rel = {"video": nn, "estilo": cfg.get("nome", ped["estilo"]), "ferramenta": ferramenta, "titulo": titulo, "canal": ped.get("canal"),
           "inicio": cj.get("inicio"), "fim": datetime.now().astimezone().isoformat(timespec="seconds"),
           "minutos": round(sum(minutos.values()), 2), "minutos_por_etapa": minutos, "render_segundos": render_s,
           "duracao_video": DUR, "tokens": 0, "custo_usd": 0,
           "observacoes": "VÍDEO COM IMAGENS (zero token Claude, só Python local): " + "; ".join(cj.get("obs") or []) +
                          f"; {len(shots)} cenas; edit.json por estilos/{ped['estilo']}/preencher.py"}
    if cfg.get("ferramenta"):
        rel["observacoes"] = rel["observacoes"].replace("VÍDEO COM IMAGENS", cfg["ferramenta"].upper() + (" (9:16)" if vertical else " (16:9)"))
    elif vertical:
        rel["observacoes"] = rel["observacoes"].replace("VÍDEO COM IMAGENS", "FÁBRICA DE SHORTS (9:16)")
    salvar_json(proj / "RELATORIO.json", rel)
    prog(100, "Pronto!")
    print("MONTADO", flush=True)


AMOSTRAS = Path(__file__).resolve().parent.parent / ".cache" / "amostras"


def _amostra(proj: Path, edit: dict, segs: float):
    """Render rápido só do começo (ver o estilo antes do vídeo inteiro). Vai pra EDITOR VIDEOS/.cache/amostras/<pasta>/,
    com caminhos absolutos pras mídias do projeto (nada muda na pasta do vídeo)."""
    dst = AMOSTRAS / proj.name
    if dst.exists():
        shutil.rmtree(dst, ignore_errors=True)
    dst.mkdir(parents=True, exist_ok=True)
    ab = lambda v: str((proj / v).resolve()) if isinstance(v, str) and v and not Path(v).is_absolute() else v
    segs = min(segs, float(edit.get("duration") or segs))
    novos = []
    for it in edit["items"]:
        st = float(it.get("start") or 0)
        if it.get("type") != "param" and st >= segs:
            continue
        it = json.loads(json.dumps(it))
        if it.get("dur") is not None:
            it["dur"] = round(min(float(it["dur"]), segs - st), 3)
        pr = it.get("props") or {}
        for k in ("src", "words_file"):
            if k in pr:
                pr[k] = ab(pr[k])
        novos.append(it)
    edit["items"] = novos
    edit["duration"] = round(segs, 2)
    edit["fonts"] = {k: ab(v) for k, v in (edit.get("fonts") or {}).items()}
    for k in ("voice", "music"):
        if (edit.get("audio") or {}).get(k):
            edit["audio"][k]["src"] = ab(edit["audio"][k]["src"])
    edit["name"] = "AMOSTRA - " + str(edit.get("name") or proj.name)
    salvar_json(dst / "edit.json", edit)
    prog(15, f"Renderizando a amostra de {int(segs)} s…")
    run([sys.executable, BUILD, str(dst), "--render"], timeout=1800)
    prog(100, "Amostra pronta!")
    print("AMOSTRA " + str(dst / "final.mp4"), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("acao", choices=["preparar", "montar", "roteiro"])
    ap.add_argument("--pasta", required=True)
    ap.add_argument("--amostra", type=float, default=0, help="só monta os primeiros N segundos (pré-visualização)")
    a = ap.parse_args()
    proj = Path(a.pasta)
    if a.acao in ("preparar", "roteiro"):
        preparar(proj)
    else:
        montar(proj, a.amostra)


if __name__ == "__main__":
    main()
