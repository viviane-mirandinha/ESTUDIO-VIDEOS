# imagens.py — fotos livres do Wikimedia Commons (mesma fonte dos testes 04/08/02) + gameplay local
import json
import random
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

from . import relevancia
from .util import log, run, run_venc

UA = {"User-Agent": "FabricaVideos/0.1 (uso pessoal; python-urllib)"}
API = "https://commons.wikimedia.org/w/api.php?"
RUIM = (".svg", ".pdf", ".gif", ".webm", ".ogv", ".djvu", ".mid", ".tif", ".tiff")
ROBLOX_DIR = Path(str(__import__("pathlib").Path(__file__).resolve().parents[3] / "estoque" / "gameplay" / "clips_raw"))


def _get(url, timeout=30, tentativas=4):
    for t in range(tentativas):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(3 + 3 * t)
                continue
            raise
        except Exception:
            if t == tentativas - 1:
                raise
            time.sleep(1.5)
    return None


STOP = {"the", "and", "of", "in", "a", "an", "ancient", "old", "photo", "photograph", "image", "picture", "with", "from", "for",
        "historical", "history", "vintage", "century", "early", "late", "portrait", "view", "city", "map", "coin", "coins"}


def _tokens(q):
    return {t for t in re.findall(r"[a-z0-9]+", q.lower()) if len(t) >= 3 and t not in STOP}


def pontuar(cand, query, preferir=()):
    """Quantas palavras da busca aparecem no título/descrição (0 = provavelmente não tem a ver).
    `preferir` = palavras do estilo que valem bônus (ex.: painting, engraving)."""
    toks = _tokens(query)
    if not toks:
        return 0
    texto = (cand["title"] + " " + cand.get("desc", "")).lower()
    n = sum(1 for t in toks if t in texto)
    if n and any(p in texto for p in preferir):
        n += 2
    return n


def buscar(query, n=20, min_w=700, extra=""):
    """Lista de candidatos {title, url, w, h, licenca, desc}."""
    q = query + " " + extra + " filetype:bitmap"
    u = API + urllib.parse.urlencode({"action": "query", "format": "json", "generator": "search", "gsrnamespace": 6,
                                      "gsrsearch": q, "gsrlimit": n, "prop": "imageinfo",
                                      "iiprop": "url|size|extmetadata", "iiurlwidth": 1280})   # 1280 = tamanho padrão do Commons (fora da lista ele devolve 429)
    try:
        r = json.loads(_get(u))
    except Exception as e:
        log(f"wikimedia erro '{query}': {str(e)[:80]}")
        return []
    out = []
    for p in (r.get("query", {}).get("pages", {}) or {}).values():
        ii = (p.get("imageinfo") or [{}])[0]
        t = p.get("title", "")
        if t.lower().endswith(RUIM) or not ii.get("thumburl"):
            continue
        w, h = ii.get("width", 0), ii.get("height", 0)
        if w < min_w or h < 400 or w / max(h, 1) > 3.2 or h / max(w, 1) > 2.2:
            continue
        em = ii.get("extmetadata", {}) or {}
        lic = (em.get("LicenseShortName", {}) or {}).get("value", "")
        desc = re.sub(r"<[^>]+>", " ", str((em.get("ImageDescription", {}) or {}).get("value", "")))[:400]
        out.append({"title": t[5:], "url": ii["thumburl"], "w": w, "h": h, "licenca": lic, "desc": desc,
                    "pagina": ii.get("descriptionurl", "")})
    return out


def baixar_para_shots(queries, pasta_img: Path, fallback_queries=(), extra="", sleep=0.7, preferir=()):
    """Para cada query baixa 1 imagem nova em img/NN.ext. Devolve lista de caminhos relativos (ou None).
    Reutiliza a imagem anterior quando a busca não acha nada (igual o 04 repetia fotos)."""
    pasta_img.mkdir(parents=True, exist_ok=True)
    usados, creditos, saida = set(), [], []
    cache = {}
    for i, q in enumerate(queries):
        escolhido = None
        q = (q or "").strip()
        if not q:   # trecho sem busca (ex.: fala de CTA) → repete a foto anterior de propósito
            saida.append(saida[-1] if saida else None)
            continue
        for tentativa in [q] + list(fallback_queries):
            if tentativa not in cache:
                cache[tentativa] = buscar(tentativa, extra=extra)
                time.sleep(sleep)
            livres = [c for c in cache[tentativa] if c["url"] not in usados and pontuar(c, tentativa, preferir) >= 1]
            if not livres:
                continue
            # texto + CLIP: só entra se bater com a frase (relevancia.py); senão tenta o fallback do tema
            melhor = relevancia.escolher(livres, usados, tentativa, relevancia.entidades(tentativa))
            if melhor:
                escolhido = melhor
                break
        if not escolhido:
            saida.append(saida[-1] if saida else None)
            log(f"img {i+1:02d}: nada p/ '{q}' → repete anterior")
            continue
        ext = Path(urllib.parse.urlparse(escolhido["url"]).path).suffix.lower() or ".jpg"
        if ext not in (".jpg", ".jpeg", ".png", ".webp"):
            ext = ".jpg"
        dest = pasta_img / f"{i+1:02d}{ext}"
        try:
            dest.write_bytes(_get(escolhido["url"], timeout=60))
            usados.add(escolhido["url"])
            creditos.append({"arquivo": dest.name, "query": q, "titulo": escolhido["title"], "licenca": escolhido["licenca"],
                             "pagina": escolhido["pagina"]})
            saida.append(f"img/{dest.name}")
            log(f"img {i+1:02d}: '{q}' → {escolhido['title'][:60]} [{escolhido['licenca']}]")
        except Exception as e:
            log(f"img {i+1:02d}: download falhou ({str(e)[:60]}) → repete anterior")
            saida.append(saida[-1] if saida else None)
        time.sleep(sleep)
    (pasta_img / "creditos.json").write_text(json.dumps(creditos, ensure_ascii=False, indent=1), encoding="utf-8")
    return saida


# ------------------------------------------------------------------ B-ROLL DE VÍDEO (Pexels Videos / Pixabay Videos)
# Só roda com a chave do PRÓPRIO usuário em Ajustes (ajustes.json: pexels_key / pixabay_key). A chave nunca é
# gravada em arquivo do projeto, log ou cache. Sem chave → o caminho de sempre (fotos do Wikimedia).
CACHE_BROLL = Path(__file__).resolve().parent.parent.parent / ".cache" / "broll"


def _json_api(url, headers=None, timeout=25):
    req = urllib.request.Request(url, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def _cache_json(nome, fn):
    """Guarda a resposta da busca em .cache/broll/busca-<hash>.json (sem a chave) por 7 dias."""
    import hashlib
    CACHE_BROLL.mkdir(parents=True, exist_ok=True)
    f = CACHE_BROLL / f"busca-{hashlib.sha1(nome.encode('utf-8')).hexdigest()[:16]}.json"
    if f.exists() and time.time() - f.stat().st_mtime < 7 * 86400:
        try:
            return json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            pass
    d = fn()
    f.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    return d


def clipes_pexels(q, chave, vertical=False, n=8):
    def fn():
        d = _json_api("https://api.pexels.com/videos/search?" + urllib.parse.urlencode(
            {"query": q, "per_page": n, "orientation": "portrait" if vertical else "landscape", "size": "medium"}), {"Authorization": chave})
        out = []
        for v in d.get("videos", []):
            lado = (lambda f: f.get("height") or 0) if vertical else (lambda f: f.get("width") or 0)
            fs = [f for f in v.get("video_files", []) if f.get("file_type") == "video/mp4" and lado(f) >= 720]
            if not fs:
                continue
            f = min(fs, key=lambda f: abs(lado(f) - (1920 if vertical else 1280)))
            slug_ = re.sub(r"[-_/]+", " ", urllib.parse.urlparse(v.get("url", "")).path)   # /video/man-walking-on-beach-12345/
            out.append({"id": f"pexels-{v.get('id')}", "fonte": "Pexels", "url": f["link"], "w": f.get("width"), "h": f.get("height"),
                        "dur": v.get("duration") or 0, "tags": slug_, "pagina": v.get("url", ""), "thumb": v.get("image", ""),
                        "autor": (v.get("user") or {}).get("name", ""), "licenca": "Pexels License"})
        return out
    return _cache_json(f"pexels|{q}|{vertical}|{n}", fn)


def clipes_pixabay(q, chave, vertical=False, n=8):
    def fn():
        d = _json_api("https://pixabay.com/api/videos/?" + urllib.parse.urlencode(
            {"key": chave, "q": q[:95], "per_page": max(3, n), "safesearch": "true"}))
        out = []
        for h in d.get("hits", []):
            vs = h.get("videos") or {}
            f = vs.get("medium") or vs.get("large") or vs.get("small") or {}
            if not f.get("url"):
                continue
            w, hh = f.get("width") or 0, f.get("height") or 0
            out.append({"id": f"pixabay-{h.get('id')}", "fonte": "Pixabay", "url": f["url"], "w": w, "h": hh,
                        "dur": h.get("duration") or 0, "tags": h.get("tags", ""), "pagina": h.get("pageURL", ""), "thumb": f.get("thumbnail", ""),
                        "autor": h.get("user", ""), "licenca": "Pixabay Content License"})
        return out
    return _cache_json(f"pixabay|{q}|{n}", fn)


def nota_clipe(c, query, vertical=False):
    """Relevância = palavras da busca que aparecem nas tags/título do clipe (+ bônus de formato certo)."""
    toks = _tokens(query)
    texto_ = (c.get("tags", "") + " ").lower()
    n = sum(1 for t in toks if re.search(r"\b" + re.escape(t) + r"s?\b", texto_))
    if n and c.get("w") and c.get("h"):
        if (c["h"] > c["w"]) == bool(vertical):
            n += 0.5
    return n


def baixar_clipe(c, destino: Path):
    """Baixa (ou pega do cache .cache/broll/<id>.mp4) e liga/copia em destino."""
    import shutil
    CACHE_BROLL.mkdir(parents=True, exist_ok=True)
    cache = CACHE_BROLL / (re.sub(r"[^\w-]", "", c["id"]) + ".mp4")
    if not cache.exists() or cache.stat().st_size < 10_000:
        tmp = cache.with_suffix(".part")
        tmp.write_bytes(_get(c["url"], timeout=120))
        tmp.replace(cache)
    destino.parent.mkdir(parents=True, exist_ok=True)
    if destino.exists():
        destino.unlink()
    try:
        import os
        os.link(cache, destino)
    except OSError:
        shutil.copy2(cache, destino)
    return destino


def clipes_para_shots(queries, shots, pasta_clips: Path, chaves: dict, vertical=False, sleep=0.3, min_nota=1):
    """B-roll de VÍDEO por frase: para cada shot (trecho do words.json, com s/e em segundos) busca clipes no
    Pexels/Pixabay com a query daquele trecho, escolhe o mais relevante (termos da busca × tags), que dure o
    trecho inteiro e que ainda não foi usado. Devolve lista paralela a `shots`: "clips/NN.mp4" ou None
    (None = esse trecho fica com foto do Wikimedia). Créditos em clips/creditos.json."""
    chaves = {k: (v or "").strip() for k, v in (chaves or {}).items()}
    if not (chaves.get("pexels") or chaves.get("pixabay")):
        return [None] * len(shots)
    usados, creditos, saida = set(), [], []
    for i, (q, sh) in enumerate(zip(queries, shots)):
        q = (q or "").strip()
        precisa = max(0.5, float(sh.get("e", 0)) - float(sh.get("s", 0)))
        if not q:
            saida.append(None)
            continue
        cands = []
        for nome, fn in (("pexels", clipes_pexels), ("pixabay", clipes_pixabay)):
            if chaves.get(nome):
                try:
                    cands += fn(q, chaves[nome], vertical=vertical)
                except Exception as e:   # nunca loga a URL (tem a chave do Pixabay)
                    log(f"clipe {i+1:02d}: {nome} falhou ({type(e).__name__})")
                time.sleep(sleep)
        livres = [c for c in cands if c["id"] not in usados and (c.get("dur") or 0) >= precisa]
        if not livres:
            saida.append(None)
            continue
        livres = [c for c in livres if nota_clipe(c, q, vertical) >= min_nota]
        melhor = relevancia.escolher([{**c, "tipo": "video"} for c in livres], usados, q, relevancia.entidades(q))
        if not melhor:
            log(f"clipe {i+1:02d}: nada relevante p/ '{q}' → foto")
            saida.append(None)
            continue
        dest = pasta_clips / f"{i+1:02d}.mp4"
        try:
            baixar_clipe(melhor, dest)
        except Exception as e:
            log(f"clipe {i+1:02d}: download falhou ({type(e).__name__}) → foto")
            saida.append(None)
            continue
        usados.add(melhor["id"])
        creditos.append({"arquivo": dest.name, "query": q, "fonte": melhor["fonte"], "autor": melhor.get("autor", ""),
                         "pagina": melhor.get("pagina", ""), "licenca": melhor["licenca"], "tags": melhor.get("tags", "")[:120],
                         "inicio": round(float(sh.get("s", 0)), 3), "fim": round(float(sh.get("e", 0)), 3)})
        saida.append(f"clips/{dest.name}")
        log(f"clipe {i+1:02d}: '{q}' → {melhor['fonte']} {melhor.get('tags', '')[:50]} ({melhor.get('dur')}s)")
    if creditos:
        pasta_clips.mkdir(parents=True, exist_ok=True)
        (pasta_clips / "creditos.json").write_text(json.dumps(creditos, ensure_ascii=False, indent=1), encoding="utf-8")
    return saida


def gameplay(pasta_clips: Path, dur, seed=None):
    """Corta um trecho aleatório de gameplay sem copyright (estoque local) em 1280x720."""
    vids = sorted(ROBLOX_DIR.glob("*.mp4")) if ROBLOX_DIR.exists() else []
    if not vids:
        raise RuntimeError(f"sem gameplay em {ROBLOX_DIR}")
    rnd = random.Random(seed)
    v = rnd.choice(vids)
    from .util import duracao_audio
    total = duracao_audio(v)
    ini = rnd.uniform(30, max(31, total - dur - 10))
    pasta_clips.mkdir(parents=True, exist_ok=True)
    out = pasta_clips / "gameplay.mp4"
    run_venc(["ffmpeg", "-y", "-v", "error", "-ss", f"{ini:.2f}", "-t", f"{dur + 1:.2f}", "-i", str(v), "-an",
              "-vf", "scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720", "-r", "30"],
             ["-pix_fmt", "yuv420p", str(out)], crf=22)
    log(f"gameplay: {v.name[:50]} @ {ini:.0f}s")
    return "clips/gameplay.mp4"
