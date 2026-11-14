# ideias.py — aba "💡 Ideias" do Estúdio: Caçador de nicho, Nicho tá saturado?, O que o público pede, Placar de ideias.
# Escrito do zero. Só páginas públicas do YouTube via yt-dlp (sem API paga) + Ollama local. Zero token Claude.
# Anti bot-check (memória do usuário): busca/canais com --flat-playlist + youtubetab:approximate_date (não abre página de vídeo),
# devagar de propósito (pausa entre canais), cache 1 dia (buscas) e 3 dias (canais). Título de vídeo por oEmbed.
import json
import re
import statistics
import subprocess
import time
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

from . import ollama, rede_yt
from .util import log

NOWIN = getattr(subprocess, "CREATE_NO_WINDOW", 0)
CACHE = Path(__file__).resolve().parent.parent.parent / ".cache" / "ideias"
FILTRO = {"todos": "", "shorts": "EgIYAQ%3D%3D", "longos": "EgIYAg%3D%3D"}   # sp= da busca (curto <4 min / longo >20 min)
STOP = set("""a o os as um uma uns umas de da do das dos e é em no na nos nas por para pra com sem que se seu sua seus suas ao aos à às
mais menos muito como quando onde porque por que qual quais isso esse essa este esta aquele the of and to in is for on with you your how why what
el la los las y en por para con su sus del al lo que es como""".split())


def _sl(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:60] or "x"


def _cache_get(nome, horas):
    f = CACHE / f"{nome}.json"
    if f.exists() and time.time() - f.stat().st_mtime < horas * 3600:
        try:
            return json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            pass
    return None


def _cache_put(nome, d):
    CACHE.mkdir(parents=True, exist_ok=True)
    (CACHE / f"{nome}.json").write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    return d


def _ytdlp_json_linhas(args, timeout=180):
    r = subprocess.run([*rede_yt.cmd(),"--ignore-errors", "--no-warnings"] + args, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=timeout, creationflags=NOWIN)
    out = []
    for ln in (r.stdout or "").splitlines():
        ln = ln.strip()
        if ln.startswith("{"):
            try:
                out.append(json.loads(ln))
            except Exception:
                pass
    if not out and r.returncode:
        err = ((r.stderr or "").strip().splitlines() or [""])[-1]
        if "confirm you" in err.lower() or "bot" in err.lower():
            raise RuntimeError("O YouTube pediu verificação (bot-check). Espere uns minutos e tente de novo.")
    return out


def _vph(views, ts, agora=None):
    if not views or not ts:
        return None
    horas = max(6.0, ((agora or time.time()) - float(ts)) / 3600)
    return round(float(views) / horas, 1)


def _num(x):
    try:
        return int(float(x))
    except Exception:
        return None


# ------------------------------------------------------------------ busca + canais
def buscar_videos(kw, n=40, formato="todos", atualizar=False):
    nome = f"busca-{_sl(kw)}-{formato}-{n}"
    if not atualizar:
        c = _cache_get(nome, 24)
        if c is not None:
            return c
    url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote(kw)
    if FILTRO.get(formato):
        url += "&sp=" + FILTRO[formato]
    vids = []
    for d in _ytdlp_json_linhas(["--flat-playlist", "--playlist-end", str(n), "--extractor-args", "youtubetab:approximate_date", "-j", url]):
        if d.get("ie_key") not in (None, "Youtube") or not d.get("id"):
            continue
        views, ts = _num(d.get("view_count")), d.get("timestamp")
        vids.append({"id": d["id"], "titulo": d.get("title") or "", "canal": d.get("channel") or d.get("uploader") or "",
                     "canal_url": d.get("uploader_url") or d.get("channel_url") or "", "views": views, "duracao": _num(d.get("duration")),
                     "ts": ts, "vph": _vph(views, ts), "url": f"https://www.youtube.com/watch?v={d['id']}",
                     "short": (_num(d.get("duration")) or 999) <= 180})
    return _cache_put(nome, vids)


def info_canal(canal_url, atualizar=False):
    """Últimos 15 vídeos do canal (flat, 1 requisição): inscritos, mediana de views, views/hora, outliers, ritmo."""
    if not canal_url:
        return None
    nome = "canal-" + _sl(canal_url.rstrip("/").split("/")[-1])
    if not atualizar:
        c = _cache_get(nome, 72)
        if c is not None:
            return c
    url = canal_url.rstrip("/")
    if not re.search(r"/(videos|shorts|streams)$", url):
        url += "/videos"
    r = subprocess.run([*rede_yt.cmd(),"--flat-playlist", "--playlist-end", "15", "--extractor-args", "youtubetab:approximate_date", "-J",
                        "--no-warnings", url], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180, creationflags=NOWIN)
    try:
        d = json.loads(r.stdout or "{}") or {}
    except Exception:
        d = {}
    ents = [e for e in (d.get("entries") or []) if e and e.get("id")]
    if not ents:
        return None
    agora = time.time()
    vs = [_num(e.get("view_count")) or 0 for e in ents]
    tss = [e.get("timestamp") for e in ents if e.get("timestamp")]
    vphs = [v for v in (_vph(_num(e.get("view_count")), e.get("timestamp"), agora) for e in ents) if v]
    med = statistics.median(vs) if vs else 0
    subs = _num(d.get("channel_follower_count"))
    outl = [{"titulo": e.get("title"), "views": _num(e.get("view_count")), "x": round((_num(e.get("view_count")) or 0) / med, 1) if med else None,
             "url": f"https://www.youtube.com/watch?v={e['id']}"} for e in ents if med and (_num(e.get("view_count")) or 0) >= 3 * med]
    info = {"canal": d.get("channel") or d.get("uploader") or d.get("title"), "canal_url": canal_url, "inscritos": subs,
            "mediana_views": int(med), "mediana_vph": round(statistics.median(vphs), 1) if vphs else None,
            "views_por_inscrito": round(med / subs, 2) if subs else None, "outliers": outl[:5], "n_videos": len(ents),
            "uploads_30d": sum(1 for t in tss if agora - t < 30 * 86400),
            "mais_antigo_dias": int((agora - min(tss)) / 86400) if tss else None}
    return _cache_put(nome, info)


def cacar(kw, formato="todos", n_canais=8, atualizar=False, prog=None):
    prog = prog or (lambda p, m: None)
    prog(5, f"Buscando “{kw}” no YouTube…")
    vids = buscar_videos(kw, 40, formato, atualizar)
    if not vids:
        raise RuntimeError("A busca não trouxe nada. Tente outra palavra (ou espere uns minutos, o YouTube pode ter bloqueado).")
    vph_ok = [v["vph"] for v in vids if v["vph"]]
    med_vph = statistics.median(vph_ok) if vph_ok else 0
    for v in vids:
        v["outlier"] = bool(med_vph and v["vph"] and v["vph"] >= 3 * med_vph)
    por_canal = {}
    for v in vids:
        if v["canal_url"]:
            c = por_canal.setdefault(v["canal_url"], {"canal": v["canal"], "canal_url": v["canal_url"], "vph_soma": 0, "videos": 0})
            c["vph_soma"] += v["vph"] or 0
            c["videos"] += 1
    top = sorted(por_canal.values(), key=lambda c: -c["vph_soma"])[:n_canais]
    canais = []
    for k, c in enumerate(top):
        prog(15 + 80 * k / max(1, len(top)), f"Olhando o canal {k + 1} de {len(top)}: {c['canal']}…")
        cache_hit = _cache_get("canal-" + _sl(c["canal_url"].rstrip("/").split("/")[-1]), 72) is not None and not atualizar
        try:
            inf = info_canal(c["canal_url"], atualizar)
        except Exception as e:
            log(f"canal falhou: {str(e)[:100]}")
            inf = None
        if inf:
            canais.append({**inf, "na_busca": c["videos"], "vph_na_busca": round(c["vph_soma"], 1)})
        if not cache_hit:
            time.sleep(2.0)   # devagar de propósito (evita bot-check)
    for v in vids:   # outlier comparado com o próprio canal
        ci = next((c for c in canais if c["canal_url"] == v["canal_url"]), None)
        if ci and ci.get("mediana_views") and v["views"]:
            v["x_canal"] = round(v["views"] / ci["mediana_views"], 1)
    vids.sort(key=lambda v: -(v["vph"] or 0))
    return {"kw": kw, "formato": formato, "videos": vids[:25], "canais": canais, "mediana_vph": round(med_vph, 1),
            "quando": time.strftime("%d/%m/%Y %H:%M")}


# ------------------------------------------------------------------ nicho tá saturado?
def _oembed(url):
    try:
        q = "https://www.youtube.com/oembed?format=json&url=" + urllib.parse.quote(url, safe="")
        with urllib.request.urlopen(urllib.request.Request(q, headers={"User-Agent": "Mozilla/5.0"}), timeout=20) as r:
            return json.load(r)
    except Exception:
        return {}


def _palavras_nicho(textos, modelo=None):
    """2-4 palavras que descrevem o nicho (Ollama; sem Ollama, palavras mais repetidas)."""
    txt = "\n".join(textos[:15])
    try:
        d = ollama._json_seguro(ollama.gerar(
            f"""Estes são títulos de vídeos do YouTube. Diga o NICHO em 2 a 4 palavras de busca (no mesmo idioma dos títulos), do jeito que alguém digitaria
na busca do YouTube pra achar vídeos parecidos.
{txt}
Responda SOMENTE JSON: {{"nicho": "..."}}""", modelo or ollama.MODELO_PADRAO, json_mode=True, temperatura=0.1, num_predict=40, timeout=90))
        n = str(d.get("nicho") or "").strip()
        if 1 <= len(n.split()) <= 6:
            return n
    except Exception:
        pass
    cont = {}
    for t in textos:
        for w in re.findall(r"[\wÀ-ÿ]{4,}", t.lower()):
            if w not in STOP:
                cont[w] = cont.get(w, 0) + 1
    return " ".join(w for w, _ in sorted(cont.items(), key=lambda x: -x[1])[:3]) or (textos[0] if textos else "")


def saturacao(entrada, modelo=None, prog=None):
    prog = prog or (lambda p, m: None)
    entrada = entrada.strip()
    kw, origem = entrada, "tema"
    if re.match(r"^https?://", entrada):
        prog(3, "Lendo o link…")
        if re.search(r"(watch\?v=|youtu\.be/|/shorts/)", entrada):
            o = _oembed(entrada)
            if not o:
                raise RuntimeError("Não consegui ler esse vídeo. Confira o link.")
            kw, origem = _palavras_nicho([o.get("title", "")], modelo), "vídeo: " + o.get("title", "")[:80]
        else:
            inf = info_canal(entrada)
            r = subprocess.run([*rede_yt.cmd(),"--flat-playlist", "--playlist-end", "15", "--print", "%(title)s", "--no-warnings",
                                entrada.rstrip("/") + ("" if entrada.rstrip("/").endswith("/videos") else "/videos")],
                               capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120, creationflags=NOWIN)
            tits = [t for t in (r.stdout or "").splitlines() if t.strip()]
            if not tits:
                raise RuntimeError("Não consegui ler esse canal. Confira o link (ex.: https://www.youtube.com/@canal).")
            kw, origem = _palavras_nicho(tits, modelo), "canal: " + ((inf or {}).get("canal") or entrada)
    prog(10, f"Nicho: “{kw}” — medindo a concorrência…")
    res = cacar(kw, "todos", 6, prog=lambda p, m: prog(10 + p * 0.85, m))
    vids, canais = res["videos"], res["canais"]
    agora = time.time()
    recentes = [v for v in vids if v["ts"] and agora - v["ts"] < 30 * 86400]
    distintos = len({v["canal_url"] for v in vids if v["canal_url"]})
    pequenos = [c for c in canais if c.get("inscritos") and c["inscritos"] < 50_000 and (c.get("mediana_views") or 0) >= 5_000]
    grandes = [c for c in canais if c.get("inscritos") and c["inscritos"] >= 1_000_000]
    vph_rec = statistics.median([v["vph"] for v in recentes if v["vph"]]) if [v for v in recentes if v["vph"]] else 0
    nota, linhas = 5.0, []
    if distintos >= 18:
        nota += 1.5
        linhas.append(f"Muita gente fazendo: {distintos} canais diferentes nos 25 primeiros resultados.")
    elif distintos <= 10:
        nota -= 1.5
        linhas.append(f"Poucos canais disputando: só {distintos} canais diferentes nos primeiros resultados.")
    if len(recentes) >= 10:
        nota += 1.5
        linhas.append(f"{len(recentes)} vídeos novos do último mês aparecem na busca — o nicho está sendo muito postado.")
    elif len(recentes) <= 3:
        nota -= 1
        linhas.append(f"Só {len(recentes)} vídeo(s) do último mês na busca — pouca gente postando agora (ou o tema esfriou).")
    if pequenos:
        nota -= 2
        linhas.append(f"{len(pequenos)} canal(is) pequeno(s) (menos de 50 mil inscritos) com mediana de 5 mil+ views: dá pra crescer do zero.")
    else:
        linhas.append("Nenhum canal pequeno com boas views entre os olhados — quem pega views aqui já é grande.")
        nota += 1
    if len(grandes) >= 3:
        nota += 1
        linhas.append(f"{len(grandes)} canais com mais de 1 milhão de inscritos dominam a busca.")
    if vph_rec and vph_rec >= 300:
        nota -= 1
        linhas.append(f"Tem procura: vídeos recentes fazem em média {int(vph_rec)} views por hora.")
    elif recentes:
        linhas.append(f"Vídeos recentes fazem em média {int(vph_rec)} views por hora.")
    nota = round(max(0, min(10, nota)), 1)
    veredito = ("ABERTO — dá pra entrar" if nota <= 3.5 else "DISPUTADO, MAS DÁ — entre com um jeito diferente" if nota <= 6.5
                else "SATURADO — só entre se tiver um diferencial forte")
    return {"entrada": entrada, "origem": origem, "nicho": kw, "nota": nota, "veredito": veredito, "explicacao": linhas,
            "numeros": {"canais_distintos": distintos, "videos_ultimo_mes": len(recentes), "vph_recentes": int(vph_rec),
                        "canais_pequenos_fortes": len(pequenos), "canais_gigantes": len(grandes)},
            "canais": canais, "videos": vids[:10], "quando": time.strftime("%d/%m/%Y %H:%M")}


# ------------------------------------------------------------------ o que o público pede
def comentarios(url, limite=500):
    nome = "coment-" + _sl(url)
    c = _cache_get(nome, 24)
    if c is not None:
        return c
    lim = max(20, min(500, int(limite)))
    base = [*rede_yt.cmd(), "--skip-download", "--write-comments", "--no-warnings", "-J",
            "--extractor-args", f"youtube:comment_sort=top;max_comments={lim},all,0,0"]
    d = {}
    for extra in ([], ["--extractor-args", "youtube:player_client=mweb"]):
        r = subprocess.run(base + extra + [url], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600, creationflags=NOWIN)
        try:
            d = json.loads(r.stdout or "{}") or {}   # yt-dlp imprime "null" quando o vídeo não existe
        except Exception:
            d = {}
        if d.get("comments"):
            break
    cs = [{"texto": re.sub(r"\s+", " ", c.get("text") or "")[:300], "likes": _num(c.get("like_count")) or 0}
          for c in (d.get("comments") or []) if c.get("parent") in (None, "root")]
    if not cs:
        if not d:
            raise RuntimeError("Não achei esse vídeo. Confira se o link abre no navegador (o vídeo pode ter sido apagado ou estar privado).")
        raise RuntimeError("Não consegui ler os comentários desse vídeo (comentários desligados ou o YouTube bloqueou agora).")
    return _cache_put(nome, {"titulo": d.get("title"), "canal": d.get("channel"), "views": d.get("view_count"), "comentarios": cs[:lim]})


def publico(url, limite=500, modelo=None, prog=None, idioma=None):
    prog = prog or (lambda p, m: None)
    prog(5, "Lendo os comentários (até {} — pode levar 1-3 min)…".format(limite))
    d = comentarios(url, limite)
    top = sorted(d["comentarios"], key=lambda c: -c["likes"])[:140]
    txt = "\n".join(f"- ({c['likes']} likes) {c['texto'][:220]}" for c in top)
    prog(60, f"A IA local está lendo {len(top)} comentários mais curtidos…")
    prompt = f"""Estes são os comentários mais curtidos do vídeo "{d.get('titulo') or ''}".
Resuma O QUE O PÚBLICO QUER, em {_lingua(idioma)}, frases curtas e simples, sem inventar nada que não esteja nos comentários:
- "pedidos": o que eles pedem (próximos vídeos, partes 2, temas) — até 6
- "reclamacoes": do que reclamam (áudio, tamanho, erro, propaganda...) — até 5
- "elogios": o que mais gostaram — até 4
- "ideias_video": até 6 ideias de vídeo novas tiradas dos comentários, cada uma {{"titulo": "...", "porque": "..."}}
- "resumo": 2 frases
{txt}
Responda SOMENTE JSON com essas chaves."""
    r = ollama._json_seguro(ollama.gerar(prompt, modelo or ollama.MODELO_PADRAO, json_mode=True, temperatura=0.3, num_predict=1200, timeout=600))
    prog(100, "Pronto!")
    return {"url": url, "titulo": d.get("titulo"), "canal": d.get("canal"), "views": d.get("views"), "lidos": len(d["comentarios"]),
            "resumo": " ".join(map(str, r["resumo"])) if isinstance(r.get("resumo"), list) else (r.get("resumo") or ""), "pedidos": r.get("pedidos") or [], "reclamacoes": r.get("reclamacoes") or [],
            "elogios": r.get("elogios") or [], "ideias_video": r.get("ideias_video") or [],
            "exemplos": top[:8], "idioma": idioma or "pt-BR", "quando": time.strftime("%d/%m/%Y %H:%M")}


# ------------------------------------------------------------------ placar de ideias
def _lingua(idioma):
    """pt-BR / en-US / es-MX → nome do idioma para o prompt (mesma tabela dos Ajustes)."""
    try:
        from . import ajustes
        return ajustes.IDIOMAS.get(idioma or "pt-BR", ajustes.IDIOMAS["pt-BR"])["llm"]
    except Exception:
        return "português do Brasil"



def notas_ideias(ideias, nicho="", modelo=None, _de_novo=True, idioma=None):
    """Nota 0-10 por ideia (gancho/curiosidade, clareza, procura provável, encaixe no nicho) + título melhor + porquê."""
    out = []
    for k in range(0, len(ideias), 6):
        lote = ideias[k:k + 6]
        lista = "\n".join(f"{n + 1}. {t}" for n, t in enumerate(lote))
        prompt = f"""Você avalia ideias de vídeo do YouTube{(' para o nicho ' + nicho) if nicho else ''}. Para cada ideia dê:
"nota" de 0 a 10 (seja exigente: curiosidade/gancho, clareza do que o vídeo entrega, se as pessoas procuram isso, se cabe no nicho),
"porque" (1 frase curta em português do Brasil) e "titulo" (uma versão mais chamativa do título, ESCRITA EM {_lingua(idioma)}, fiel à ideia, sem inventar fato).
{lista}
Responda SOMENTE JSON: {{"ideias": [{{"n": 1, "nota": 0, "porque": "...", "titulo": "..."}}]}}"""
        try:
            d = ollama._json_seguro(ollama.gerar(prompt, modelo or ollama.MODELO_PADRAO, json_mode=True, temperatura=0.2, num_predict=900, timeout=300))
        except Exception as e:
            log(f"Ollama (placar) falhou: {str(e)[:100]}")
            d = {}
        itens = d.get("ideias") or next((v for v in d.values() if isinstance(v, list)), []) if isinstance(d, dict) else []
        por_n = {}
        for k, x in enumerate(itens):
            if not isinstance(x, dict):
                continue
            try:
                por_n[int(x.get("n")) - 1] = x
            except Exception:
                por_n.setdefault(k, x)   # sem "n": vale a ordem
        if not por_n:
            log(f"placar: resposta sem notas: {str(d)[:200]}")
        faltam = [t for n, t in enumerate(lote) if n not in por_n]
        refeitas = {x["ideia"]: x for x in notas_ideias(faltam, nicho, modelo, False, idioma)} if faltam and _de_novo else {}
        for n, t in enumerate(lote):
            if t in refeitas:
                out.append(refeitas[t])
                continue
            x = por_n.get(n, {})
            try:
                nota = max(0.0, min(10.0, float(x.get("nota"))))
            except Exception:
                nota = None
            out.append({"ideia": t, "nota": nota, "porque": str(x.get("porque") or "")[:200], "titulo": str(x.get("titulo") or "")[:120],
                        "idioma": idioma or "pt-BR"})
    return out
