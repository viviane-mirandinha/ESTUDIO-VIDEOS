# bancos.py — busca de imagens/clipes grátis por frase em múltiplas fontes:
#   Wikimedia Commons (sempre), Openverse (sem chave), YouTube Creative Commons (yt-dlp, sem chave),
#   Archive.org (sem chave), Pexels/Pixabay (só com chave do próprio usuário em Ajustes).
# Busca paralela nas fontes gratuitas + download da opção escolhida.
# Usado pelo "Vídeo com imagens" e pela tela "Conferir imagens" do painel. Zero token.
import hashlib
import json
import re
import shutil
import subprocess
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from . import imagens, ollama, rede_yt, relevancia
from .util import log, run, run_venc

UA = {"User-Agent": "EstudioVideos/1.0 (uso pessoal)"}
_NOWIN = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def _json(url, headers=None, timeout=25):
    req = urllib.request.Request(url, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def _thumb_wm(url):
    """Miniatura menor do Commons para a grade (troca /1280px- por /330px-)."""
    return re.sub(r"/(\d+)px-", "/330px-", url) if "/thumb/" in url else url


# ------------------------------------------------------------------ fontes
def wikimedia(q, n=6, preferir=(), extra=""):
    cands = imagens.buscar(q, n=24, extra=extra)
    cands.sort(key=lambda c: -imagens.pontuar(c, q, preferir))   # sort estável: empate mantém relevância do Commons
    out = []
    for c in cands[:n]:
        out.append({"tipo": "image", "fonte": "Wikimedia", "url": c["url"], "thumb": _thumb_wm(c["url"]), "titulo": c["title"],
                    "licenca": c.get("licenca", ""), "pagina": c.get("pagina", ""), "w": c["w"], "h": c["h"],
                    "nota": imagens.pontuar(c, q, preferir)})
    return out


def openverse(q, n=8):
    """Openverse (WordPress/Creative Commons): fotos livres de Flickr, museus etc. SEM chave (limite anônimo por IP).
    Fora do ar/limite estourado → lista vazia (as outras fontes seguem)."""
    try:
        d = _json("https://api.openverse.org/v1/images/?" + urllib.parse.urlencode({"q": q[:180], "page_size": n, "mature": "false"}), timeout=12)
    except Exception as e:
        log(f"Openverse indisponível para '{q}': {type(e).__name__}")
        return []
    out = []
    for r in d.get("results", []):
        w, h = r.get("width") or 0, r.get("height") or 0
        if not r.get("url") or (w and w < 640):
            continue
        tags = " ".join(t.get("name", "") for t in (r.get("tags") or [])[:15])
        lic = f"CC {str(r.get('license') or '').upper()} {r.get('license_version') or ''}".strip()
        out.append({"tipo": "image", "fonte": "Openverse", "url": r["url"], "thumb": r.get("thumbnail") or r["url"], "titulo": r.get("title") or q,
                    "tags": tags, "licenca": lic, "licenca_url": r.get("license_url", ""), "autor": r.get("creator") or "",
                    "pagina": r.get("foreign_landing_url") or "", "w": w, "h": h, "nota": 2})
    return out


def pexels_fotos(q, chave, n=4, vertical=False):
    d = _json("https://api.pexels.com/v1/search?" + urllib.parse.urlencode({"query": q, "per_page": n, "orientation": "portrait" if vertical else "landscape"}),
              {"Authorization": chave})
    return [{"tipo": "image", "fonte": "Pexels", "url": p["src"].get("large2x") or p["src"]["original"], "thumb": p["src"].get("medium"),
             "titulo": p.get("alt") or q, "licenca": "Pexels (grátis)", "pagina": p.get("url", ""), "w": p.get("width"), "h": p.get("height"),
             "nota": 2} for p in d.get("photos", [])]


def pexels_videos(q, chave, n=3, vertical=False):
    d = _json("https://api.pexels.com/videos/search?" + urllib.parse.urlencode({"query": q, "per_page": n, "orientation": "portrait" if vertical else "landscape", "size": "medium"}),
              {"Authorization": chave})
    out = []
    for v in d.get("videos", []):
        lado = (lambda f: f.get("height") or 0) if vertical else (lambda f: f.get("width") or 0)
        fs = [f for f in v.get("video_files", []) if f.get("file_type") == "video/mp4" and lado(f) >= 960]
        if not fs:
            continue
        f = min(fs, key=lambda f: abs(lado(f) - (1920 if vertical else 1280)))
        slug_ = re.sub(r"[-_/]+|\d{4,}", " ", urllib.parse.urlparse(v.get("url", "")).path).replace(" video ", " ").strip()
        out.append({"tipo": "video", "fonte": "Pexels", "url": f["link"], "thumb": v.get("image"), "titulo": slug_ or q, "licenca": "Pexels (grátis)",
                    "pagina": v.get("url", ""), "w": f.get("width"), "h": f.get("height"), "dur": v.get("duration"), "nota": 2})
    return out


def pixabay_fotos(q, chave, n=4, vertical=False):
    d = _json("https://pixabay.com/api/?" + urllib.parse.urlencode({"key": chave, "q": q[:95], "image_type": "photo", "orientation": "vertical" if vertical else "horizontal",
                                                                     "per_page": max(3, n), "safesearch": "true"}))
    return [{"tipo": "image", "fonte": "Pixabay", "url": h.get("largeImageURL") or h["webformatURL"], "thumb": h.get("webformatURL"),
             "titulo": h.get("tags") or q, "licenca": "Pixabay (grátis)", "pagina": h.get("pageURL", ""), "w": h.get("imageWidth"),
             "h": h.get("imageHeight"), "nota": 2} for h in d.get("hits", [])[:n]]


# ------------------------------------------------------------------ YouTube CC
def _verificar_licenca_yt(vid):
    """Confirma que o vídeo é Creative Commons (extract completo do vídeo escolhido).
    Retorna (True, canal) ou (False, '')."""
    try:
        import yt_dlp
        opts = {"quiet": True, "no_warnings": True, "skip_download": True}
        with yt_dlp.YoutubeDL(rede_yt.opts(opts)) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={vid}", download=False)
        lic = (info or {}).get("license") or ""
        canal = (info or {}).get("uploader") or (info or {}).get("channel") or ""
        return ("creative commons" in lic.lower() or "reuse allowed" in lic.lower()), canal
    except Exception:
        return False, ""


def youtube_cc(q, n=4, min_dur=3):
    """Busca vídeos Creative Commons no YouTube via yt-dlp (sem API key).
    Confirma licença CC de cada vídeo antes de incluir. Retorna até n resultados."""
    try:
        import yt_dlp
    except ImportError:
        log("yt-dlp não instalado — YouTube CC desativado")
        return []
    try:
        url = ("https://www.youtube.com/results?search_query="
               + urllib.parse.quote(q) + "&sp=EgIwAQ%253D%253D")  # filtro Creative Commons
        opts = {"quiet": True, "no_warnings": True, "extract_flat": True,
                "playlistend": 15, "skip_download": True}
        with yt_dlp.YoutubeDL(rede_yt.opts(opts)) as ydl:
            info = ydl.extract_info(url, download=False)
        out = []
        for entry in (info or {}).get("entries", []):
            dur = entry.get("duration") or 0
            if dur < min_dur:
                continue
            vid = entry.get("id") or entry.get("url", "")
            # Confirma licença CC com extract completo (só dos que passam o filtro)
            ok, canal = _verificar_licenca_yt(vid)
            if not ok:
                log(f"YouTube CC: '{vid}' rejeitado (licença não confirmada)")
                continue
            thumb = entry.get("thumbnail") or f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"
            out.append({"tipo": "video", "fonte": "YouTube CC",
                        "url": f"https://www.youtube.com/watch?v={vid}",
                        "thumb": thumb, "titulo": entry.get("title") or q,
                        "licenca": "CC BY (Creative Commons Attribution)",
                        "autor": canal, "licenca_url": "https://creativecommons.org/licenses/by/3.0/",
                        "pagina": f"https://www.youtube.com/watch?v={vid}", "w": 1920, "h": 1080,
                        "dur": dur, "nota": 3, "_ytcc": True})
            if len(out) >= n:
                break
        return out
    except Exception as e:
        log(f"YouTube CC falhou para '{q}': {str(e)[:120]}")
        return []


# ------------------------------------------------------------------ Archive.org
# Licenças permitidas para uso comercial (monetização): CC0, CC-BY, CC-BY-SA, domínio público.
# Rejeitamos NC (uso não-comercial proibido) e ND (sem derivados — não pode cortar/editar).
_ARCHIVE_LICENCAS_OK = {"publicdomain", "cc0", "cc-by", "cc-by-sa"}

def _licenca_ok_archive(lic_url):
    """True se licenseurl do Archive.org permite uso comercial + edição."""
    if not lic_url:
        return False
    lic = lic_url.lower()
    if "publicdomain" in lic or "/zero/" in lic or "/mark/" in lic:
        return True
    if "-nc" in lic or "-nd" in lic:
        return False
    if "creativecommons.org/licenses/by-sa/" in lic:
        return True
    if "creativecommons.org/licenses/by/" in lic:
        return True
    return False

def _nome_licenca_archive(lic_url):
    if not lic_url:
        return "Desconhecida"
    lic = lic_url.lower()
    if "publicdomain" in lic or "/zero/" in lic or "/mark/" in lic:
        return "Domínio Público"
    if "by-sa" in lic:
        return "CC BY-SA"
    if "by/" in lic:
        return "CC BY (atribuição obrigatória)"
    return "Creative Commons"

def archive_org(q, n=4, media="video"):
    """Busca no Internet Archive — vídeos ou imagens com licença livre confirmada. Sem API key.
    Filtra para aceitar SÓ: domínio público, CC0, CC-BY, CC-BY-SA. Rejeita NC e ND."""
    mt = "movies" if media == "video" else "image"
    params = urllib.parse.urlencode({
        "q": f"{q} mediatype:{mt} licenseurl:*creativecommons*",
        "fl[]": "identifier,title,description,mediatype,licenseurl,creator",
        "rows": min(25, n * 5), "output": "json"
    })
    try:
        d = _json(f"https://archive.org/advancedsearch.php?{params}")
        out = []
        for doc in (d.get("response") or {}).get("docs", []):
            lic_url = doc.get("licenseurl") or ""
            if not _licenca_ok_archive(lic_url):
                continue
            ident = doc.get("identifier") or ""
            titulo = doc.get("title") or q
            autor = doc.get("creator") or ""
            if isinstance(autor, list):
                autor = ", ".join(str(a) for a in autor)
            lic_nome = _nome_licenca_archive(lic_url)
            base = {"titulo": titulo, "licenca": lic_nome, "licenca_url": lic_url, "autor": str(autor),
                    "pagina": f"https://archive.org/details/{ident}", "nota": 2, "_archive": True}
            if media == "video":
                url = f"https://archive.org/download/{ident}/{ident}.mp4"
                thumb = f"https://archive.org/services/img/{ident}"
                out.append({**base, "tipo": "video", "fonte": "Archive.org", "url": url, "thumb": thumb,
                            "w": 1280, "h": 720, "dur": 0})
            else:
                url = f"https://archive.org/download/{ident}/{ident}.jpg"
                thumb = f"https://archive.org/services/img/{ident}"
                out.append({**base, "tipo": "image", "fonte": "Archive.org", "url": url, "thumb": thumb,
                            "w": 0, "h": 0})
            if len(out) >= n:
                break
        return out
    except Exception as e:
        log(f"Archive.org falhou para '{q}': {str(e)[:120]}")
        return []


def pixabay_videos(q, chave, n=3):
    d = _json("https://pixabay.com/api/videos/?" + urllib.parse.urlencode({"key": chave, "q": q[:95], "per_page": max(3, n), "safesearch": "true"}))
    out = []
    for h in d.get("hits", [])[:n]:
        vs = h.get("videos") or {}
        f = vs.get("medium") or vs.get("large") or vs.get("small") or {}
        if not f.get("url"):
            continue
        th = f.get("thumbnail") or (f"https://i.vimeocdn.com/video/{h['picture_id']}_640x360.jpg" if h.get("picture_id") else "")
        out.append({"tipo": "video", "fonte": "Pixabay", "url": f["url"], "thumb": th, "titulo": h.get("tags") or q, "licenca": "Pixabay (grátis)",
                    "pagina": h.get("pageURL", ""), "w": f.get("width"), "h": f.get("height"), "dur": h.get("duration"), "nota": 2})
    return out


def candidatos(q, chaves=None, videos=False, preferir=(), extra="", vertical=False):
    """Todas as opções para uma busca em múltiplas fontes (paralelo nas gratuitas).
    chaves = {"pexels": "...", "pixabay": "..."} (opcionais). vertical = shorts 9:16."""
    chaves = chaves or {}
    out = []

    # --- Fontes gratuitas (sem chave) — rodam em paralelo ---
    gratis = [
        ("Wikimedia", lambda: wikimedia(q, preferir=preferir, extra=extra)),
        ("Archive.org", lambda: archive_org(q, n=4, media="video" if videos else "image")),
        ("Openverse", lambda: openverse(q)),
    ]
    if videos:
        gratis.append(("YouTube CC", lambda: youtube_cc(q, n=4)))

    resultados_paralelos = {}
    with ThreadPoolExecutor(max_workers=len(gratis)) as pool:
        futures = {pool.submit(fn): nome for nome, fn in gratis}
        for future in as_completed(futures):
            nome = futures[future]
            try:
                resultados_paralelos[nome] = future.result()
            except Exception as e:
                log(f"{nome} falhou para '{q}': {str(e)[:100]}")
                resultados_paralelos[nome] = []

    # Ordem de prioridade: Wikimedia > Openverse > Archive.org > YouTube CC (a escolha final é por relevância, ver relevancia.py)
    for nome in ["Wikimedia", "Openverse", "Archive.org", "YouTube CC"]:
        out += resultados_paralelos.get(nome, [])

    # --- Fontes com chave do usuário (sequencial) ---
    fontes_chave = []
    if chaves.get("pexels"):
        fontes_chave.append(lambda: pexels_fotos(q, chaves["pexels"], vertical=vertical))
        if videos:
            fontes_chave.append(lambda: pexels_videos(q, chaves["pexels"], vertical=vertical))
    if chaves.get("pixabay"):
        fontes_chave.append(lambda: pixabay_fotos(q, chaves["pixabay"], vertical=vertical))
        if videos:
            fontes_chave.append(lambda: pixabay_videos(q, chaves["pixabay"]))
    for f in fontes_chave:
        try:
            out += f()
        except Exception as e:
            log(f"banco falhou para '{q}': {str(e)[:100]}")

    return out


def melhor(cands, usados, querer_video=False, query="", ents=(), assunto=""):
    """Melhor opção que BATE com a cena (texto + CLIP, ver relevancia.py) ou None.
    Antes pegava o 1º vídeo da lista / qualquer foto quando nada casava → mídia nada a ver (reembolso 30/10)."""
    if query:
        return relevancia.escolher(cands, usados, query, ents, assunto, querer_video)
    livres = [c for c in cands if c["url"] not in usados and c.get("nota", 0) >= 1 and c.get("fonte") == "Wikimedia"]
    return livres[0] if livres else None


# ------------------------------------------------------------------ download
def _baixar_archive_fallback(c, dest: Path):
    """Tenta achar o arquivo .mp4 real nos metadados do Archive.org item."""
    ident = c.get("pagina", "").split("/details/")[-1].split("/")[0].split("?")[0]
    if not ident:
        raise RuntimeError("Archive.org: sem identifier")
    meta = _json(f"https://archive.org/metadata/{ident}/files")
    mp4s = [f for f in (meta or []) if isinstance(f, dict) and str(f.get("name", "")).lower().endswith(".mp4")]
    if not mp4s:
        raise RuntimeError(f"Archive.org: nenhum .mp4 em {ident}")
    # Pega o menor .mp4 (mais rápido de baixar)
    mp4s.sort(key=lambda f: int(f.get("size") or 999999999))
    nome = mp4s[0]["name"]
    url = f"https://archive.org/download/{ident}/{urllib.parse.quote(nome)}"
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=180) as r:
        dest.write_bytes(r.read())


def _baixar_ytcc(url, raw: Path, dur_max=30.0):
    """Baixa vídeo do YouTube CC via yt-dlp (até dur_max segundos, 720p)."""
    try:
        import yt_dlp
        opts = {"quiet": True, "no_warnings": True, "outtmpl": str(raw),
                "format": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best",
                "merge_output_format": "mp4",
                "download_ranges": yt_dlp.utils.download_range_func(None, [(0, dur_max)]),
                "force_keyframes_at_cuts": True}
        with yt_dlp.YoutubeDL(rede_yt.opts(opts)) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        log(f"yt-dlp download falhou: {str(e)[:120]}")
        return False


def _gravar_credito(proj: Path, subpasta, arquivo, c):
    """Grava atribuição CC-BY em creditos.json (obrigatório para licenças que exigem crédito)."""
    lic = (c.get("licenca") or "").lower()
    if "cc" not in lic and "creative commons" not in lic and "domínio" not in lic:
        return  # Pexels/Pixabay não exigem crédito formal
    cred_path = proj / subpasta / "creditos.json"
    try:
        creds = json.loads(cred_path.read_text("utf-8")) if cred_path.exists() else []
    except Exception:
        creds = []
    creds.append({
        "arquivo": arquivo,
        "titulo": c.get("titulo", ""),
        "autor": c.get("autor", ""),
        "fonte": c.get("fonte", ""),
        "licenca": c.get("licenca", ""),
        "licenca_url": c.get("licenca_url", ""),
        "pagina": c.get("pagina", ""),
    })
    cred_path.write_text(json.dumps(creds, ensure_ascii=False, indent=2), "utf-8")


DESCARTADOS = []   # clipes jogados fora pela limpeza nesta execução: [{"titulo", "motivo"}]


def baixar(c, proj: Path, i, dur=6.0, vertical=False, limpar=True):
    """Baixa a opção escolhida para a cena i. Imagem → img/NN-hash.ext ; vídeo → clips/NN-hash.mp4 (1280x720 ou 1080x1920, mudo).
    limpar=True: clipe com pessoa falando, legenda gravada ou logo é apagado e dá erro (quem chamou tenta a próxima opção).
    Escolha manual do usuário (Conferir imagens) passa limpar=False."""
    cw, ch = (1080, 1920) if vertical else (1280, 720)
    h = hashlib.md5(c["url"].encode()).hexdigest()[:6]
    if c["tipo"] == "video":
        d = proj / "clips"
        d.mkdir(parents=True, exist_ok=True)
        raw = d / f"_raw-{h}.mp4"
        dest = d / f"{i + 1:02d}-{h}{'-v' if vertical else ''}.mp4"
        if not dest.exists():
            # YouTube CC e Archive.org: download especial
            if c.get("_ytcc"):
                if not _baixar_ytcc(c["url"], raw, dur_max=max(8.0, dur + 3)):
                    raise RuntimeError(f"Falha no download YouTube CC: {c['url']}")
            else:
                req = urllib.request.Request(c["url"], headers=UA)
                try:
                    with urllib.request.urlopen(req, timeout=120) as r:
                        raw.write_bytes(r.read())
                except Exception:
                    # Archive.org pode ter URL errada (nem todo item tem .mp4 no nome)
                    if c.get("_archive"):
                        log(f"Archive.org download direto falhou, tentando via metadados")
                        _baixar_archive_fallback(c, raw)
                    else:
                        raise
            run_venc(["ffmpeg", "-y", "-v", "error", "-i", str(raw), "-t", f"{max(4.0, dur + 1.5):.2f}", "-an",
                      "-vf", f"scale={cw}:{ch}:force_original_aspect_ratio=increase,crop={cw}:{ch},fps=30"],
                     ["-pix_fmt", "yuv420p", str(dest)], crf=22)
            raw.unlink(missing_ok=True)
            if limpar:
                try:
                    from . import limpeza
                    motivo = limpeza.checar(dest)
                except Exception as e:
                    motivo = ""
                    log(f"limpeza: pulei ({str(e)[:80]})")
                if motivo:
                    dest.unlink(missing_ok=True)
                    DESCARTADOS.append({"titulo": str(c.get("titulo") or "")[:60], "motivo": motivo})
                    raise RuntimeError(f"clipe descartado: {motivo}")
        _gravar_credito(proj, "clips", dest.name, c)
        return f"clips/{dest.name}"
    d = proj / "img"
    d.mkdir(parents=True, exist_ok=True)
    ext = Path(urllib.parse.urlparse(c["url"]).path).suffix.lower()
    if ext not in (".jpg", ".jpeg", ".png", ".webp"):
        ext = ".jpg"
    dest = d / f"{i + 1:02d}-{h}{ext}"
    if not dest.exists():
        data = imagens._get(c["url"], timeout=60)
        if not data or len(data) < 2000:
            raise RuntimeError("download vazio")
        dest.write_bytes(data)
    _gravar_credito(proj, "img", dest.name, c)
    return f"img/{dest.name}"


# ------------------------------------------------------------------ buscas (Ollama)
def queries(trechos, tema, dica="", modelo=None):
    """Uma busca curta em inglês por trecho (coisa concreta e fotografável). Último item = busca geral do tema."""
    modelo = modelo or ollama.MODELO_PADRAO
    lista = "\n".join(f"{k + 1}. {t}" for k, t in enumerate(trechos))
    prompt = f"""You choose stock-photo / stock-video search terms for a documentary video. Topic: {tema}.
Visual style: {dica or 'real photographs and footage'}.
For EACH numbered narration line below write ONE English search term of 1 to 4 words that shows something concrete and visible
for that line: a named person, place, building, object, animal, machine or scene (e.g. "Eiffel Tower construction", "coffee beans roasting",
"Panama Canal locks"). Prefer proper nouns from the topic when the line is about them. No abstract words (history, economy, concept, idea).
Do not repeat the same term twice in a row.

Lines:
{lista}

Answer ONLY JSON: {{"queries": ["term 1", "term 2", ...]}} with exactly {len(trechos)} items in order."""
    for _ in range(2):
        try:
            d = ollama._json_seguro(ollama.gerar(prompt, modelo, json_mode=True, temperatura=0.3, num_predict=40 * len(trechos) + 200))
        except Exception as e:
            log(f"Ollama (buscas) falhou: {str(e)[:120]}")
            break
        q = d.get("queries")
        if isinstance(q, list) and q:
            q = [re.sub(r"[\"“”]", "", str(x)).strip()[:60] for x in q]
            while len(q) < len(trechos):
                q.append(q[-1])
            return q[:len(trechos)]
    return ollama._queries_regra(trechos, tema)


def query_unica(linha, tema, evitar=(), modelo=None):
    """Refaz a busca de UMA cena quando o lote devolveu a mesma busca pra várias seguidas (modelo pequeno faz isso)."""
    ev = ", ".join(f'"{e}"' for e in evitar if e)
    try:
        d = ollama._json_seguro(ollama.gerar(
            f'Video topic: {tema}. Narration line: "{linha}". Write ONE English stock-photo search term (1-4 words) showing something '
            f'concrete and visible that THIS line talks about (a named person, place, animal, object or action). '
            f'{"It must be different from: " + ev + ". " if ev else ""}Answer only JSON {{"q": "..."}}',
            modelo or ollama.MODELO_PADRAO, json_mode=True, temperatura=0.4, num_predict=30, timeout=60))
        return re.sub(r"[\"“”]", "", str(d.get("q") or "")).strip()[:60]
    except Exception:
        return ""


def traduzir_busca(q, modelo=None):
    """Palavra digitada pelo usuário (PT) → busca em inglês para os bancos. Se falhar, usa a própria palavra."""
    if not re.search(r"[áéíóúâêôãõçà]|\b(de|da|do|das|dos|com|uma?|para)\b", q.lower()):
        return q
    try:
        d = ollama._json_seguro(ollama.gerar(
            f'Translate this stock photo search to short English (1-4 words). Answer only JSON {{"q": "..."}}.\nSearch: {q}',
            modelo or ollama.MODELO_PADRAO, json_mode=True, temperatura=0.1, num_predict=30, timeout=60))
        t = str(d.get("q") or "").strip()
        return t[:60] or q
    except Exception:
        return q
