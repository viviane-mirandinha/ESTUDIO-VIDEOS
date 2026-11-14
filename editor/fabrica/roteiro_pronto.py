# roteiro_pronto.py — ferramenta "Roteiro pronto" do Estúdio (copiar e melhorar roteiros). Escrita do zero, 100% local:
# yt-dlp (título, descrição, legenda automática) → [faster-whisper se não tiver legenda] → Ollama local.
#
#   python roteiro_pronto.py <pasta>      (lê <pasta>\pedido.json e grava <pasta>\resultado.json)
#   pedido.json = {"acao": "transcrever"|"estrutura"|"escrever"|"melhorar", "url": "...", "tema": "...",
#                  "duracao": 300 | "igual", "texto": "...(melhorar)", "notas": "...", "idioma": "pt-BR", "modelo": "qwen2.5:7b"}
# Progresso no stdout: "@@<pct>|<mensagem>".
import json
import re
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import ajustes, fatos, ollama, rede_yt  # noqa: E402
from lib.util import ler_json, log, salvar_json  # noqa: E402

CACHE = Path(__file__).resolve().parent.parent / "roteiros" / "_cache"
NOWIN = getattr(subprocess, "CREATE_NO_WINDOW", 0)
WPM_PADRAO = 150
MAX_PALAVRAS = 2300          # ~15 min de narração (limite do modelo local escrevendo bloco a bloco)


def prog(pct, msg):
    print(f"@@{int(pct)}|{msg}", flush=True)


def mmss(t):
    t = max(0, int(t or 0))
    return f"{t // 3600}:{t % 3600 // 60:02d}:{t % 60:02d}" if t >= 3600 else f"{t // 60}:{t % 60:02d}"


def gerar(prompt, modelo, json_mode=False, temp=0.6, n=900, ctx=12288):
    body = {"model": modelo, "prompt": prompt, "stream": False, "options": {"temperature": temp, "num_predict": n, "num_ctx": ctx}}
    if json_mode:
        body["format"] = "json"
    req = urllib.request.Request(ollama.URL, data=json.dumps(body).encode("utf-8"), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=900) as r:
        return json.load(r).get("response", "")


# ------------------------------------------------------------------ 1) baixar dados + transcrição
def yt_id(url):
    m = re.search(r"(?:v=|youtu\.be/|shorts/|embed/|live/)([\w-]{11})", url)
    return m.group(1) if m else re.sub(r"\W+", "_", url)[-40:]


def _ytdlp_json(url):
    for extra in ([], ["--extractor-args", "youtube:player_client=mweb"]):
        r = subprocess.run([*rede_yt.cmd(),"--no-warnings", "--no-playlist", "-J", *extra, url], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=120, creationflags=NOWIN)
        if r.returncode == 0 and r.stdout.strip().startswith("{"):
            return json.loads(r.stdout)
        err = (r.stderr or "").strip().splitlines()
        log("yt-dlp -J falhou: " + (err[-1][:200] if err else ""))
    raise RuntimeError("Não consegui ler esse link. Confira se o vídeo é público e se o link está certo.")


def _pega_trilha(info):
    """Escolhe UMA trilha de legenda (manual > automática no idioma original) e devolve a URL json3."""
    lang = (info.get("language") or "").split("-")[0]
    subs, auto = info.get("subtitles") or {}, info.get("automatic_captions") or {}
    ordem = []
    for base in [lang, "pt", "en", "es"]:
        if not base:
            continue
        ordem += [(subs, k) for k in subs if k.split("-")[0] == base]
        ordem += [(auto, f"{base}-orig"), (auto, base)]
    for fonte, k in ordem:
        for f in fonte.get(k) or []:
            if f.get("ext") == "json3" and f.get("url"):
                return k, f["url"]
    return None, None


def _baixar_legenda(url):
    for t in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429 and t < 3:
                time.sleep(6 + 6 * t)
                continue
            raise
    return {}


def _segmentos_json3(d):
    segs = []
    for ev in d.get("events") or []:
        if not ev.get("segs"):
            continue
        txt = "".join(s.get("utf8", "") for s in ev["segs"]).replace("\n", " ").strip()
        if txt:
            segs.append({"t": ev.get("tStartMs", 0) / 1000, "x": txt})
    return segs


def _whisper(url, pasta: Path):
    from lib.transcrever import transcrever
    prog(20, "Vídeo sem legenda: baixando o áudio pra transcrever (pode levar alguns minutos)…")
    aud = pasta / "audio.m4a"
    subprocess.run([*rede_yt.cmd(),"--no-warnings", "--no-playlist", "-f", "bestaudio[ext=m4a]/bestaudio/18", "-o", str(aud), url],
                   capture_output=True, timeout=1800, creationflags=NOWIN)
    if not aud.exists():
        raise RuntimeError("Não consegui baixar o áudio desse vídeo.")
    prog(35, "Transcrevendo o áudio no seu PC (Whisper)…")
    words = transcrever(aud, pasta / "words.json")
    return [{"t": w["s"], "x": w["w"]} for w in words]


def limpar_segmentos(segs):
    """Legenda automática → lista de frases {t, x} sem duplicatas, sem [Música]."""
    out = []
    for s in segs:
        x = re.sub(r"\[[^\]]*\]|\([^)]*música[^)]*\)", " ", s["x"], flags=re.I)
        x = re.sub(r"\s+", " ", x).strip()
        if x:
            out.append({"t": s["t"], "x": x})
    return out


def texto_corrido(segs, por_par=4):
    """Junta tudo em parágrafos legíveis (quebra a cada ~4 frases ou pausa longa)."""
    pal = []
    for s in segs:
        for w in s["x"].split():
            pal.append((s["t"], w))
    frases, atual, t0 = [], [], None
    for t, w in pal:
        if not atual:
            t0 = t
        atual.append(w)
        if re.search(r"[.!?…]$", w) or len(atual) > 45:
            frases.append((t0, " ".join(atual)))
            atual = []
    if atual:
        frases.append((t0, " ".join(atual)))
    pars, cur = [], []
    for t, f in frases:
        cur.append(f)
        if len(cur) >= por_par:
            pars.append(" ".join(cur))
            cur = []
    if cur:
        pars.append(" ".join(cur))
    pars = [p[0].upper() + p[1:] if p else p for p in pars]
    return "\n\n".join(pars), frases


def obter_video(url, pasta: Path):
    CACHE.mkdir(parents=True, exist_ok=True)
    cf = CACHE / f"{yt_id(url)}.json"
    if cf.exists():
        prog(18, "Usando a transcrição já baixada antes…")
        return ler_json(cf)
    prog(5, "Lendo os dados do vídeo (título, descrição, legenda)…")
    info = _ytdlp_json(url)
    lang_trilha, u = _pega_trilha(info)
    segs, fonte = [], ""
    if u:
        prog(12, "Baixando a legenda automática…")
        try:
            segs = _segmentos_json3(_baixar_legenda(u))
            fonte = f"legenda do YouTube ({lang_trilha})"
        except Exception as e:
            log(f"legenda falhou: {str(e)[:120]}")
    if not segs:
        segs = _whisper(url, pasta)
        fonte = "transcrito pelo Whisper no seu PC"
    segs = limpar_segmentos(segs)
    corrido, frases = texto_corrido(segs)
    n_pal = len(corrido.split())
    dur = float(info.get("duration") or (segs[-1]["t"] if segs else 0) or 1)
    v = {"url": url, "id": yt_id(url), "titulo": info.get("title", ""), "canal": info.get("channel") or info.get("uploader", ""),
         "canal_url": info.get("channel_url", ""), "descricao": info.get("description", ""), "duracao": dur, "views": info.get("view_count"),
         "idioma": info.get("language") or "", "capitulos": [{"t": c.get("start_time", 0), "titulo": c.get("title", "")} for c in info.get("chapters") or []],
         "tags": (info.get("tags") or [])[:30], "fonte_transcricao": fonte, "transcricao": corrido, "frases": frases,
         "palavras": n_pal, "ppm": round(n_pal / max(dur / 60, 0.1))}
    salvar_json(cf, v)
    return v


# ------------------------------------------------------------------ 2) estrutura (molde)
def amostra(v, janelas=10, chars=420):
    frases, D = v["frases"], v["duracao"]
    ini = " ".join(f for t, f in frases if t < 75)[:1400]
    fim = " ".join(f for t, f in frases if t > D - 60)[-700:]
    meio = []
    for k in range(janelas):
        a, b = D * k / janelas, D * (k + 1) / janelas
        txt = " ".join(f for t, f in frases if a <= t < b)
        if txt:
            meio.append(f"[{mmss(a)} · {round(100 * k / janelas)}% do vídeo] {txt[:chars]}")
    return ini, "\n".join(meio), fim


def estrutura(v, modelo, idioma):
    lang = ajustes.idioma_llm(idioma)
    ini, meio, fim = amostra(v)
    caps = "\n".join(f"{mmss(c['t'])} {c['titulo']}" for c in v.get("capitulos") or [])
    prompt = f"""Você é um analista de roteiros do YouTube. Analise a ESTRUTURA (não o assunto) deste vídeo que deu certo.
Título: {v['titulo']}
Canal: {v['canal']} · Duração: {mmss(v['duracao'])} · Ritmo: {v['ppm']} palavras por minuto
{('Capítulos do vídeo:' + chr(10) + caps) if caps else ''}

COMEÇO (primeiros segundos):
{ini}

TRECHOS AO LONGO DO VÍDEO:
{meio}

FINAL:
{fim}

Responda SOMENTE JSON, com textos em {lang}, neste formato:
{{"nome_formato": "nome curto do formato (ex.: 'Ascensão e queda em ordem cronológica')",
 "promessa": "o que o vídeo promete ao espectador logo no início",
 "gancho": {{"tempo": "0:00-0:30", "como_funciona": "como os primeiros segundos prendem", "modelo_de_frase": "um molde de frase de gancho com [lacunas], sem copiar o original"}},
 "blocos": [{{"inicio": "m:ss", "nome": "nome do bloco", "o_que_acontece": "função do bloco na história", "pct": 15}}],
 "viradas": [{{"tempo": "m:ss", "o_que_muda": "revelação/virada que segura a atenção"}}],
 "cta": {{"onde": "em que momento pede like/inscrição", "como": "como pede"}},
 "tom": "tom de voz do narrador", "ritmo": "como é o ritmo das frases",
 "padrao_titulo": "molde do título com [lacunas]",
 "pontos_fracos": ["o que dá pra fazer melhor que o original"]}}
Use de 4 a 8 blocos que somam 100%. Tempos devem estar entre 0:00 e {mmss(v['duracao'])}."""
    for _ in range(2):
        d = ollama._json_seguro(gerar(prompt, modelo, json_mode=True, temp=0.3, n=1600))
        if isinstance(d.get("blocos"), list) and d["blocos"]:
            break
    else:
        raise RuntimeError("A IA local não conseguiu montar a estrutura. Tente de novo (ou troque o modelo em Ajustes).")
    bl = [b for b in d["blocos"] if isinstance(b, dict) and b.get("nome")]
    tot = sum(float(b.get("pct") or 0) for b in bl) or 1
    acc = 0.0
    for b in bl:   # normaliza % e recalcula o início pelo acumulado (o 7B erra conta)
        b["pct"] = round(100 * float(b.get("pct") or (100 / len(bl))) / tot, 1)
        b["inicio"] = mmss(v["duracao"] * acc / 100)
        acc += b["pct"]
    d["blocos"] = bl
    d.setdefault("viradas", [])
    d.setdefault("gancho", {})
    d.setdefault("cta", {})
    return d


# ------------------------------------------------------------------ 3) escrever / melhorar
REGRAS = """REGRAS (obrigatórias):
- Gancho nos primeiros 3-5 segundos: a 1ª frase já quebra o padrão (pergunta forte, fato surpreendente ou conflito). Zero "olá", zero apresentação.
- ZERO fato inventado: não invente nomes, números, datas nem citações. Se não tiver certeza, fale de forma geral, sem número.
- Sem loop: cada parágrafo avança a história; nunca repita uma ideia já dita nem recomece a explicação.
- Frases curtas, boas de narrar em voz alta. Linguagem simples.
- Não copie frases do vídeo original: use só a estrutura.
- Nunca escreva "clique aqui", "link na descrição" ou "assista mais": o único pedido ao espectador é o like/inscrição, e só onde for indicado.
- Não preencha lacunas do molde com ano ou lugar inventado: use só datas e lugares que estão nos fatos de referência.
- Só o texto da narração: sem títulos, marcadores, emojis, colchetes ou indicações de cena."""


def _limpa(t):
    t = re.sub(r"^\s*(#+|\*\*|bloco\s*\d+[:.)-]).*$", "", t, flags=re.M | re.I)
    t = re.sub(r"\[[^\]]*\]|\*+|^[-•]\s*", "", t, flags=re.M)
    t = re.sub(r"[ \t]+", " ", t)
    return re.sub(r"\n{3,}", "\n\n", t).strip()


def _norm(s):
    return set(re.findall(r"\w{4,}", s.lower()))


def sem_loop(texto):
    """Remove frases repetidas/quase iguais (anti-loop em código)."""
    vistos, out_pars, cortadas = [], [], 0
    for par in texto.split("\n\n"):
        fr_ok = []
        for f in re.split(r"(?<=[.!?…])\s+", par.strip()):
            n = _norm(f)
            if len(n) >= 4 and any(len(n & v) / max(1, len(n | v)) > 0.6 for v in vistos):
                cortadas += 1
                continue
            vistos.append(n)
            fr_ok.append(f)
        if fr_ok:
            out_pars.append(" ".join(fr_ok))
    return "\n\n".join(out_pars), cortadas


def escrever(v, molde, tema, palavras, modelo, idioma, notas="", ref=None):
    lang = ajustes.idioma_llm(idioma)
    base_fatos = fatos.bloco_prompt(ref)
    blocos = molde["blocos"]
    mapa = "\n".join(f"{k + 1}. {b['nome']} ({b['pct']}%): {b.get('o_que_acontece', '')}" for k, b in enumerate(blocos))
    meio_cta = min(range(len(blocos)), key=lambda k: abs(sum(b["pct"] for b in blocos[:k + 1]) - 50))
    partes = []
    for k, b in enumerate(blocos):
        prog(45 + 40 * k / len(blocos), f"Escrevendo o bloco {k + 1} de {len(blocos)}: {b['nome']}…")
        alvo = max(35, int(palavras * b["pct"] / 100))
        ja = " | ".join(p["texto"].split(".")[0][:90] for p in partes[-4:])
        extra = []
        if k == 0:
            g = molde.get("gancho") or {}
            extra.append(f"Este é o COMEÇO do vídeo: abra com o gancho. Como o original prende: {g.get('como_funciona', '')}. Molde (troque CADA [lacuna] por informação real do tema; nunca escreva o nome da lacuna): {g.get('modelo_de_frase', '')}")
        if k == meio_cta:
            extra.append("No fim deste bloco, peça o like de forma natural, ligada ao que acabou de ser contado (uma frase só).")
        if k == len(blocos) - 1:
            extra.append("Este é o FINAL: feche a história com uma conclusão forte e peça like e inscrição numa frase natural.")
        prompt = f"""Você é um roteirista de vídeos do YouTube. Escreva em {lang}.
Tema do vídeo: {tema}
{('Observações do criador: ' + notas) if notas else ''}
Tom do narrador: {molde.get('tom', '')}. Ritmo: {molde.get('ritmo', '')}.
Estrutura completa do vídeo (siga a ordem):
{mapa}

Agora escreva SOMENTE o bloco {k + 1} — "{b['nome']}": {b.get('o_que_acontece', '')}
Tamanho: cerca de {alvo} palavras.
{chr(10).join(extra)}
{('Já foi dito antes (NÃO repita): ' + ja) if ja else ''}
Último trecho escrito: "{partes[-1]['texto'][-300:] if partes else ''}"

{REGRAS}{base_fatos}"""
        txt = ""
        for _ in range(2):
            txt = _limpa(gerar(prompt, modelo, temp=0.7, n=int(alvo * 3.2) + 200))
            if len(txt.split()) >= alvo * 0.5:
                break
        partes.append({"bloco": b["nome"], "texto": txt})
    corpo = "\n\n".join(p["texto"] for p in partes)
    limpo, cortadas = sem_loop(corpo)
    return partes, limpo, cortadas


def melhorar(texto, modelo, idioma, notas=""):
    lang = ajustes.idioma_llm(idioma)
    n = len(texto.split())
    prompt = f"""Você é um editor de roteiros do YouTube especialista em retenção. Reescreva o roteiro abaixo em {lang}, MELHORADO:
- Gancho bem mais forte nos primeiros 3-5 segundos (1ª frase quebra o padrão).
- Corte enrolação, repetição e loop (ideias repetidas ou recomeços).
- Frases curtas, boas de narrar em voz alta.
- Peça o like de forma natural UMA vez no meio e UMA vez no final.
- Mantenha TODOS os fatos do original; NÃO acrescente fato, número, nome ou data que não estejam no texto.
- Tamanho parecido (cerca de {int(n * 0.85)} a {int(n * 1.05)} palavras). Só o texto da narração, sem títulos nem marcadores.
{('Observações do criador: ' + notas) if notas else ''}

ROTEIRO ORIGINAL:
{texto[:9000]}"""
    out = _limpa(gerar(prompt, modelo, temp=0.5, n=int(n * 3) + 400, ctx=16384))
    limpo, cortadas = sem_loop(out)
    return limpo, cortadas


def kit(roteiro, tema, molde, modelo, idioma, partes=None, ppm=WPM_PADRAO):
    lang = ajustes.idioma_llm(idioma)
    pt = idioma == "pt-BR"
    prompt = f"""Crie o kit de publicação do YouTube para o roteiro abaixo, em {lang}.
Tema: {tema}
{('Molde de título que funcionou: ' + molde.get('padrao_titulo', '')) if molde else ''}
Roteiro:
{roteiro[:5000]}

Responda SOMENTE JSON:
{{"titulos": ["título principal", "alternativo 1", "alternativo 2"],
 {'' if pt else '"titulos_pt": ["tradução PT-BR do 1", "do 2", "do 3"],'}
 "descricao": "descrição de 2 parágrafos curtos, sem inventar fatos, com chamada para inscrição",
 "tags": ["10 a 15 tags"],
 "fatos_a_conferir": ["cada nome, número, data ou afirmação do roteiro que precisa ser conferida antes de publicar"]}}
Títulos: apelativos, máximo 70 caracteres, gerando curiosidade, sem mentir."""
    d = ollama._json_seguro(gerar(prompt, modelo, json_mode=True, temp=0.6, n=1200))
    d["titulos"] = [re.sub(r"[\"“”]", "", str(t)).strip() for t in (d.get("titulos") or []) if str(t).strip()][:3]
    d["tags"] = [str(t).strip().lstrip("#") for t in (d.get("tags") or []) if str(t).strip()][:15]
    d["fatos_a_conferir"] = [str(t).strip() for t in (d.get("fatos_a_conferir") or []) if str(t).strip()][:15]
    if partes:   # capítulos com o tempo estimado de cada bloco (ritmo de narração)
        acc, caps = 0, []
        for p in partes:
            caps.append(f"{mmss(acc / ppm * 60)} {p['bloco']}")
            acc += len(p["texto"].split())
        d["capitulos"] = caps
        d["descricao"] = str(d.get("descricao") or "").strip() + "\n\n" + "\n".join(caps)
    return d


def checar_idioma(texto, idioma):
    """Aviso simples se aparecer muita palavra de outro idioma (regra: roteiro 100% no idioma do canal)."""
    ing = {"the", "and", "with", "this", "that", "you", "your", "what", "about", "from", "they", "have", "will"}
    pal = re.findall(r"[a-zA-Z']+", texto.lower())
    if idioma.startswith("en") or not pal:
        return ""
    n = sum(1 for p in pal if p in ing)
    return f"Achei {n} palavras em inglês no roteiro — revise." if n >= 3 else ""


# ------------------------------------------------------------------ main
def main():
    pasta = Path(sys.argv[1])
    ped = ler_json(pasta / "pedido.json")
    aj = ajustes.ler()
    modelo = ped.get("modelo") or aj["modelo_ollama"]
    idioma = ped.get("idioma") or aj["idioma"]
    acao = ped.get("acao", "escrever")
    t0 = time.time()
    res = {"acao": acao, "criado": datetime.now().astimezone().isoformat(timespec="seconds"), "modelo": modelo, "idioma": idioma, "tokens_claude": 0}
    if acao == "melhorar":
        prog(10, "Melhorando o seu roteiro com a IA local…")
        antes = (ped.get("texto") or "").strip()
        depois, cortadas = melhorar(antes, modelo, idioma, ped.get("notas", ""))
        prog(75, "Criando títulos, descrição e tags…")
        res.update(antes=antes, roteiro=depois, frases_cortadas=cortadas, tema=ped.get("tema") or "",
                   kit=kit(depois, ped.get("tema") or antes[:120], None, modelo, idioma))
    else:
        v = obter_video(ped["url"], pasta)
        res["video"] = {k: v[k] for k in ("url", "titulo", "canal", "canal_url", "duracao", "views", "palavras", "ppm", "fonte_transcricao", "capitulos")}
        res["transcricao"] = v["transcricao"]
        if acao in ("estrutura", "escrever"):
            prog(25, "Descobrindo a estrutura do vídeo (gancho, blocos, viradas)…")
            res["estrutura"] = estrutura(v, modelo, idioma)
        if acao == "escrever":
            dur = ped.get("duracao") or 300
            ppm = v["ppm"] if 90 <= v["ppm"] <= 200 else WPM_PADRAO
            palavras = int((v["duracao"] if dur == "igual" else float(dur)) / 60 * ppm)
            if palavras > MAX_PALAVRAS:
                res["aviso_tamanho"] = f"O original tem {mmss(v['duracao'])}; escrevi a versão de até ~15 min (o limite da IA local)."
            palavras = max(80, min(MAX_PALAVRAS, palavras))
            prog(42, "Procurando fatos reais sobre o seu tema (Wikipedia)…")
            ref = fatos.buscar(ped["tema"], idioma, modelo=modelo)
            if ref:
                res["fonte_fatos"] = {"titulo": ref["titulo"], "url": ref["url"]}
            partes, rot, cortadas = escrever(v, res["estrutura"], ped["tema"], palavras, modelo, idioma, ped.get("notas", ""), ref)
            prog(88, "Criando títulos, descrição e tags…")
            res.update(tema=ped["tema"], partes=partes, roteiro=rot, frases_cortadas=cortadas, palavras_alvo=palavras,
                       duracao_estimada=round(len(rot.split()) / ppm * 60), kit=kit(rot, ped["tema"], res["estrutura"], modelo, idioma, partes, ppm))
    if res.get("roteiro"):
        res["aviso_idioma"] = checar_idioma(res["roteiro"], idioma)
        (pasta / "ROTEIRO.txt").write_text(res["roteiro"], encoding="utf-8")
    if res.get("transcricao"):
        (pasta / "TRANSCRICAO.txt").write_text(res["transcricao"], encoding="utf-8")
    res["segundos"] = round(time.time() - t0)
    salvar_json(pasta / "resultado.json", res)
    prog(100, "Pronto!")
    print("RESULTADO_OK", flush=True)


if __name__ == "__main__":
    main()
