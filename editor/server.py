"""Editor de Vídeos Local — servidor (http://localhost:8780)."""
import base64
import json
import os
import re
import shutil
import subprocess
import threading
import time
import traceback
import urllib.error
import uuid
from pathlib import Path

# O Windows não põe .venv\Scripts no PATH sozinho: sem isto, "yt-dlp" (instalado no .venv) não era achado em máquina nova.
_BIN_VENV = str(Path(__file__).resolve().parent.parent / (".venv/Scripts" if os.name == "nt" else ".venv/bin"))
if os.path.isdir(_BIN_VENV) and _BIN_VENV not in os.environ.get("PATH", "").split(os.pathsep):
    os.environ["PATH"] = _BIN_VENV + os.pathsep + os.environ.get("PATH", "")

from fastapi import Body, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

import build_from_edit as B


def abrir(path):
    """Abre pasta/arquivo no sistema (Windows, Mac ou Linux)."""
    if hasattr(os, "startfile"):
        os.startfile(str(path))
    else:
        import sys
        subprocess.Popen(["open" if sys.platform == "darwin" else "xdg-open", str(path)])
import medico_render as MED
import guarda_densidade as DENS
import som_livre as SOM
import autopilot as AP

ROOT = Path(__file__).resolve().parent
CONF = ROOT / "config.json"
# migração C→D (23/10/2026): as pastas foram pro kits e o Desktop ficou com atalho (junction).
# Usamos o caminho REAL quando ele existe (o caminho antigo continua funcionando como reserva).
MIGRA = [
    (str(__import__("pathlib").Path(__file__).resolve().parents[1]), str(__import__("pathlib").Path(__file__).resolve().parents[1])),
    (str(__import__("pathlib").Path(__file__).resolve().parents[1] / "editor"), str(ROOT)),
]


def _mig(p) -> str:
    s = str(p or "")
    for a, b in MIGRA:
        if s.lower().startswith(a.lower()):
            alt = b + s[len(a):]
            if Path(alt).exists():
                return alt
    return s


DEFAULT_FOLDERS = [_mig(f) for f in (
    str(__import__("pathlib").Path(__file__).resolve().parents[1] / "VIDEOS"),
    str(__import__("pathlib").Path(__file__).resolve().parents[1] / "VIDEOS-NOVOS"),
    str(__import__("pathlib").Path(__file__).resolve().parents[1] / "VIDEOS-SHORTS"),
    str(__import__("pathlib").Path(__file__).resolve().parents[1] / "kits"),
)]
# origem do card (filtro da lista) a partir da pasta de varredura
ORIGENS = [
    (r"TESTE ESTILOS DARK[\\/]VIDEOS", "Estilos YouTube"),
]
# mp4 soltos que NÃO viram card (renders intermediários)
SKIP_STEMS = {"render_mudo", "silent", "leve", "base", "render", "mudo", "fundo", "thumb"}
SKIP_DIRS = re.compile(r"^(\.|_tmp|work$|hf\d*$|midia$|clips?$|img$|b-?roll$|assets$|ref$|sfx$)", re.I)
PORT = int(os.environ.get("ESTUDIO_PORTA") or 8780)  # ESTUDIO_PORTA=8795 → instância de teste sem derrubar a 8780
app = FastAPI()
# compressão gzip só pra texto (json/html/js/css); vídeo/imagem/áudio e respostas parciais (Range) ficam de fora
from starlette.middleware.gzip import DEFAULT_EXCLUDED_CONTENT_TYPES, GZipMiddleware  # noqa: E402
app.add_middleware(GZipMiddleware, minimum_size=1200, compresslevel=5,
                   exclude_content_types=DEFAULT_EXCLUDED_CONTENT_TYPES + ("video/*", "image/*", "audio/*", "font/*", "application/octet-stream", "application/zip"))
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")
JOBS = {}

# ------------------------------------------------------------------ cache em memória (painel rápido)
# Devolve na hora o último resultado se a "assinatura" (mtime das pastas) não mudou. Passou do TTL com a mesma
# assinatura → devolve o que tem e recalcula em segundo plano. Assinatura mudou → recalcula na hora.
_MEMO, _MEMO_LOCK, _MEMO_RUN, _MEMO_LOCKS = {}, threading.Lock(), set(), {}


def memo(key, fn, ttl=30, sig=None):
    s = sig() if sig else None
    e, now = _MEMO.get(key), time.time()
    if e and e["sig"] == s:
        if now - e["t"] >= ttl and key not in _MEMO_RUN:
            _MEMO_RUN.add(key)

            def bg():
                try:
                    _MEMO[key] = {"v": fn(), "t": time.time(), "sig": s}
                except Exception:
                    pass
                finally:
                    _MEMO_RUN.discard(key)
            threading.Thread(target=bg, daemon=True).start()
        return e["v"]
    with _MEMO_LOCK:
        lk = _MEMO_LOCKS.setdefault(key, threading.RLock())
    # QA 24/10: trava POR CHAVE. Com 1 trava só, /api/relatorios (que chama projects() por dentro) travava a si mesmo
    # e congelava Meus vídeos, Pedir vídeo, vozes e o checklist até reiniciar o painel.
    with lk:   # 2 abas pedindo ao mesmo tempo → 1 cálculo só
        e = _MEMO.get(key)
        if e and e["sig"] == s and time.time() - e["t"] < ttl:
            return e["v"]
        v = fn()
        _MEMO[key] = {"v": v, "t": time.time(), "sig": s}
        return v


def memo_limpar(*keys):
    for k in (keys or list(_MEMO)):
        _MEMO.pop(k, None)


def _sig_dirs(dirs):
    """mtime de cada pasta + das subpastas (os.scandir no Windows já traz o mtime: custa ~1 ms)."""
    out = []
    for f in dirs:
        try:
            with os.scandir(f) as it:
                subs = tuple(sorted((x.name, x.stat().st_mtime) for x in it if x.is_dir()))
            out.append((str(f), os.stat(f).st_mtime, subs))
        except OSError:
            out.append((str(f), None))
    return tuple(out)


def conf():
    c = None
    if CONF.exists():
        try:
            c = json.loads(CONF.read_text(encoding="utf-8"))
        except Exception:
            c = None
    c = c or {"folders": DEFAULT_FOLDERS}
    fs, vistos = [], set()
    for f in c.get("folders") or []:
        r = _mig(f)
        if r.lower() not in vistos:
            vistos.add(r.lower())
            fs.append(r)
    c["folders"] = fs
    return c


def pid_of(p: Path):
    return base64.urlsafe_b64encode(str(p).encode("utf-8")).decode().rstrip("=")


def _decode_pid(pid: str) -> Path:
    try:
        return Path(base64.urlsafe_b64decode(pid + "=" * (-len(pid) % 4)).decode("utf-8"))
    except Exception:
        raise HTTPException(400, "id inválido")


def path_of(pid: str) -> Path:
    p = _decode_pid(pid)
    if not (p / "edit.json").exists():
        raise HTTPException(404, "projeto não encontrado")
    return p


def resolve_any(pid: str):
    """id de projeto (pasta com edit.json) OU de um .mp4 solto → ("proj", pasta) | ("video", arquivo)."""
    p = _decode_pid(pid)
    if (p / "edit.json").exists():
        return "proj", p
    if p.suffix.lower() == ".mp4" and p.is_file():
        return "video", p
    raise HTTPException(404, "projeto não encontrado")


_SAIDAS = {"t": 0, "dirs": []}


def _saidas():
    """Pastas onde o painel cria vídeos (padrão + a escolhida em Ajustes). No pacote dos amigos não existe “TESTE ESTILOS DARK”."""
    if time.time() - _SAIDAS["t"] > 5:
        ds = []
        for d in (globals().get("OUT_PEDIDOS"), (AJ.ler().get("pasta_saida") if "AJ" in globals() else None)):
            try:
                if d:
                    ds.append(str(Path(d).resolve()).lower().rstrip(os.sep))
            except Exception:
                pass
        _SAIDAS.update(t=time.time(), dirs=ds)
    return _SAIDAS["dirs"]


def origem_of(base: str) -> str:
    for rx, nome in ORIGENS:
        if re.search(rx, base, re.I):
            return nome
    try:
        b = str(Path(base).resolve()).lower()
        if any(b == d or b.startswith(d + os.sep) for d in _saidas()):
            return "Estilos YouTube"
    except Exception:
        pass
    return "Outros"


# ------------------------------------------------------------------ mp4 soltos (cards "só vídeo")
PROBE_LOCK = threading.Lock()
THUMB_Q, THUMB_SEEN = [], set()


def probe_full(path: Path):
    """w/h/fps/dur de um vídeo via ffprobe (None se falhar)."""
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                              "stream=width,height,r_frame_rate:format=duration", "-of", "json", str(path)],
                             capture_output=True, text=True, timeout=20, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)).stdout
        j = json.loads(out)
        st = (j.get("streams") or [{}])[0]
        num, _, den = str(st.get("r_frame_rate", "30/1")).partition("/")
        fps = round(float(num) / float(den or 1), 3) if num else 30
        return {"w": st.get("width"), "h": st.get("height"), "fps": fps or 30, "dur": float(j.get("format", {}).get("duration") or 0)}
    except Exception:
        return None


def _probe_cache(d: Path):
    f = d / ".editor_cache" / "probe.json"
    try:
        return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
    except Exception:
        return {}


def _probe_cached(files):
    """Lê o cache probe.json de cada pasta; roda ffprobe (em paralelo) só nos arquivos novos/alterados."""
    from concurrent.futures import ThreadPoolExecutor
    by_dir = {}
    for f in files:
        by_dir.setdefault(f.parent, []).append(f)
    res, todo = {}, []
    caches = {d: _probe_cache(d) for d in by_dir}
    for d, fs in by_dir.items():
        for f in fs:
            st = f.stat()
            c = caches[d].get(f.name)
            if c and c.get("mtime") == st.st_mtime and c.get("size") == st.st_size:
                res[f] = c
            else:
                todo.append(f)
    if todo:
        with ThreadPoolExecutor(8) as ex:
            for f, info in zip(todo, ex.map(probe_full, todo)):
                if not info:
                    continue
                st = f.stat()
                info.update(mtime=st.st_mtime, size=st.st_size)
                res[f] = info
                caches[f.parent][f.name] = info
        with PROBE_LOCK:
            for d in {f.parent for f in todo}:
                try:
                    cd = d / ".editor_cache"
                    cd.mkdir(exist_ok=True)
                    (cd / "probe.json").write_text(json.dumps(caches[d], ensure_ascii=False), encoding="utf-8")
                except Exception:
                    pass
    return res


def video_thumb_path(f: Path) -> Path:
    return f.parent / ".editor_cache" / (f.stem + ".jpg")


THUMB_LOCK, THUMB_RUN = threading.Lock(), [False]


def _thumb_worker():
    while True:
        with THUMB_LOCK:   # leve 01/11: a fila só fecha com a trava → nunca 2 workers (2 ffmpeg) ao mesmo tempo
            if not THUMB_Q:
                THUMB_RUN[0] = False
                break
            f, out, ss = THUMB_Q.pop(0)
        if out.exists() or not f.exists():
            continue
        try:
            out.parent.mkdir(exist_ok=True)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-i", str(f), "-frames:v", "1", "-vf", "scale=480:-2",
                            "-q:v", "4", str(out)], timeout=60, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        except Exception:
            pass
    THUMB_SEEN.clear()
    memo_limpar("projects", "relatorios")


def queue_thumb(f: Path, out: Path = None, ss=1):
    """Gera a miniatura em thread de fundo (a lista não espera; o card mostra 🎞 e troca quando ficar pronta)."""
    out = out or video_thumb_path(f)
    if out in THUMB_SEEN:
        return
    THUMB_SEEN.add(out)
    with THUMB_LOCK:
        THUMB_Q.append((f, out, ss))
        start = not THUMB_RUN[0]
        THUMB_RUN[0] = True
    if start:
        threading.Thread(target=_thumb_worker, daemon=True).start()


def loose_videos(base: Path, seen_dirs):
    """mp4 soltos SÓ nas pastas de criativos (origem 'Criativos ...'): a própria pasta + 1 subpasta, fora de pastas de projeto
    (edit.json) e de pastas de trabalho (clips/broll/assets/hf/...). Pastas de estilos e kits nunca são varridas."""
    if not origem_of(str(base)).startswith("Criativos"):
        return []
    out = []
    for f in list(base.glob("*.mp4")) + list(base.glob("*/*.mp4")):
        if f.stem.lower() in SKIP_STEMS or f.parent in seen_dirs or (f.parent / "edit.json").exists():
            continue
        if f.parent != base and SKIP_DIRS.match(f.parent.name):
            continue
        out.append(f)
    if len(out) > 200:  # limite de segurança: só os 200 mais recentes
        out = sorted(out, key=lambda x: x.stat().st_mtime, reverse=True)[:200]
    return out


def safe_join(base: Path, rel: str) -> Path:
    p = (base / rel).resolve()
    if base.resolve() not in p.parents and p != base.resolve():
        raise HTTPException(403, "fora do projeto")
    return p


_DUR_CACHE = {}


def probe_dur(path: Path):
    """duração com cache (arquivo + mtime + tamanho) — abrir o editor não roda mais ffprobe toda vez."""
    try:
        st = path.stat()
    except OSError:
        return None
    k = (str(path), st.st_mtime, st.st_size)
    if k not in _DUR_CACHE:
        _DUR_CACHE[k] = probe(path)
    return _DUR_CACHE[k]


def probe(path: Path):
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                             capture_output=True, text=True, timeout=15,
                             creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)).stdout.strip()
        return float(out)
    except Exception:
        return None


# ------------------------------------------------------------------ páginas
def _versao_front():
    return int(max((ROOT / "static" / f).stat().st_mtime for f in ("app.js", "style.css", "index.html")))


@app.get("/api/versao")
def versao_front():
    return {"v": _versao_front()}


@app.get("/", response_class=HTMLResponse)
def home():
    html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
    v = _versao_front()
    return html.replace("/static/app.js", f"/static/app.js?v={v}").replace("/static/style.css", f"/static/style.css?v={v}")


@app.get("/api/config")
def get_conf():
    return conf()


@app.post("/api/config")
def set_conf(data: dict = Body(...)):
    folders = [f.strip() for f in data.get("folders", []) if f.strip()]
    CONF.write_text(json.dumps({**conf(), "folders": folders}, ensure_ascii=False, indent=1), encoding="utf-8")   # guarda as outras opções (rede_local)
    return {"ok": True}


def find_video(p: Path):
    if (p / "final.mp4").exists():
        return p / "final.mp4"
    vids = [f for f in p.glob("*.mp4") if f.stem.lower() not in ("render_mudo", "silent", "leve", "render", "base")]
    return max(vids, key=lambda f: f.stat().st_mtime) if vids else None


def estilo_of(ed, p: Path):
    if ed.get("estilo"):
        return ed["estilo"]
    parts = [x.strip() for x in str(ed.get("name") or "").split(" - ")]
    if len(parts) >= 3 and parts[0].isdigit():
        return parts[1].title()
    return re.sub(r"^\d+[-_ ]*", "", p.name).replace("-", " ").title()


def edit_duration(ed):
    d = ed.get("duration")
    if d:
        return float(d)
    ends = [float(i.get("start", 0)) + float(i.get("dur", 0)) for i in ed.get("items", []) if i.get("dur")]
    return max(ends) if ends else 0


@app.get("/api/projects")
def projects():
    return memo("projects", _projects, ttl=30, sig=lambda: _sig_dirs(pastas_varredura()))


def _projects():
    res, seen = [], set()
    ridx = _ref_index()
    for f in pastas_varredura():
        base = Path(f)
        if not base.exists():
            continue
        cands = list(base.glob("edit.json")) + list(base.glob("*/edit.json")) + list(base.glob("*/*/edit.json"))
        for e in cands:
            p = e.parent
            if p in seen:
                continue
            seen.add(p)
            try:
                ed = B.load_edit(p)
            except Exception:
                ed = {}
            vid = find_video(p)
            th = p / "thumb.jpg"
            if vid and not th.exists():
                queue_thumb(vid, th, 3)   # em segundo plano (antes travava a lista rodando ffmpeg)
            res.append({"id": pid_of(p), "tipo": "projeto", "origem": origem_of(str(base)), "name": ed.get("name") or p.name, "estilo": estilo_of(ed, p), "referencia": ed.get("referencia") or {}, "folder": str(p), "group": str(base),
                        "w": ed.get("canvas", {}).get("w"), "h": ed.get("canvas", {}).get("h"),
                        "dur": edit_duration(ed), "mtime": e.stat().st_mtime,
                        "thumb": th.exists(), "rendered": bool(vid), "video": str(vid) if vid else None,
                        "mb": round(vid.stat().st_size / 1048576, 1) if vid else None,
                        "leve_mb": round((p / "leve.mp4").stat().st_size / 1048576, 1) if (p / "leve.mp4").exists() else None, "conferir": _estado_vi(p) == "conferir",
                        "ajustavel": bool(vid) and (p / "PEDIDO.md").exists(),
                        "tem_ref": bool(vid) and bool(find_ref(p, {"referencia": ed.get("referencia") or {}}, ridx))})
        # ---- mp4 soltos (sem edit.json) → cards "só vídeo"
        loose = loose_videos(base, seen)
        infos = _probe_cached(loose)
        for f in loose:
            info = infos.get(f) or {}
            th = video_thumb_path(f)
            if not th.exists():
                queue_thumb(f)
            res.append({"id": pid_of(f), "tipo": "video", "origem": origem_of(str(base)), "name": f.stem, "estilo": "", "referencia": {},
                        "folder": str(f.parent), "group": str(base), "w": info.get("w"), "h": info.get("h"), "fps": info.get("fps"),
                        "dur": info.get("dur") or 0, "mtime": f.stat().st_mtime, "thumb": th.exists(), "rendered": True, "video": str(f),
                        "mb": round(f.stat().st_size / 1048576, 1)})
    order = pastas_varredura()
    res.sort(key=lambda r: (order.index(r["group"]) if r["group"] in order else 99, p_name_key(r)))
    return res


def _estado_vi(p: Path):
    f = p / "cenas.json"
    if not f.exists():
        return None
    try:
        return json.loads(f.read_text(encoding="utf-8")).get("estado")
    except Exception:
        return None


def p_name_key(r):
    return (Path(r["video"]).name if r.get("tipo") == "video" else Path(r["folder"]).name).lower()


@app.post("/api/importar/{pid}")
def importar(pid: str):
    """mp4 solto → pasta <mesmo diretório>\\<nome>\\ com edit.json mínimo; MOVE o mp4 para dentro. Só roda no clique em Importar."""
    kind, f = resolve_any(pid)
    if kind == "proj":
        return {"ok": True, "pid": pid, "folder": str(f), "ja_existia": True}
    dest = f.parent / f.stem
    if (dest / "edit.json").exists():
        return {"ok": True, "pid": pid_of(dest), "folder": str(dest), "ja_existia": True}
    info = _probe_cached([f]).get(f) or probe_full(f) or {}
    w, h, fps, dur = info.get("w") or 1920, info.get("h") or 1080, info.get("fps") or 30, float(info.get("dur") or 0)
    dest.mkdir(parents=True, exist_ok=True)
    novo = dest / f.name
    shutil.move(str(f), str(novo))
    th = video_thumb_path(f)
    if th.exists():
        try:
            shutil.move(str(th), str(dest / "thumb.jpg"))
        except Exception:
            pass
    cache = f.parent / ".editor_cache" / "probe.json"
    if cache.exists():  # tira do cache da pasta de origem
        try:
            c = json.loads(cache.read_text(encoding="utf-8"))
            c.pop(f.name, None)
            cache.write_text(json.dumps(c, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass
    edit = {"version": 1, "name": f.stem, "canvas": {"w": w, "h": h, "fps": fps, "bg": "#000000"}, "duration": dur, "template": "generic",
            "estilo": "Vídeo importado", "origem": origem_of(str(f.parent)), "audio": {},
            "tracks": [{"id": "fundo", "name": "Cenas / mídia"}, {"id": "textos", "name": "Textos"}],
            "items": [{"id": "v1", "type": "video", "track": "fundo", "label": f.stem[:40], "start": 0, "dur": dur,
                       "props": {"src": f.name, "fill": True, "fit": "cover", "volume": 1}}]}
    (dest / "edit.json").write_text(json.dumps(edit, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"ok": True, "pid": pid_of(dest), "folder": str(dest), "ja_existia": False}


@app.get("/api/project/{pid}")
def get_project(pid: str):
    p = path_of(pid)
    ed = B.load_edit(p)
    dur = {}
    srcs = []
    a = ed.get("audio") or {}
    for k in ("voice", "music"):
        if a.get(k, {}).get("src"):
            srcs.append(a[k]["src"])
    srcs += [x["src"] for x in a.get("extra") or [] if x.get("src")]
    srcs += [it["props"]["src"] for it in ed.get("items", []) if it.get("type") == "video" and it.get("props", {}).get("src")]
    for s in set(srcs):
        sp = Path(s) if Path(s).is_absolute() else p / s
        dur[s] = probe_dur(sp) if sp.exists() else None
    for it in ed.get("items", []):  # legenda com words_file: traz as palavras para o editor poder mexer
        pr = it.get("props") or {}
        if it.get("type") == "caption" and not pr.get("words") and pr.get("words_file"):
            try:
                pr["words"] = B.words_of(p, pr)
            except Exception:
                pass
    scenes = sorted(f.stem for f in B.SCENES.glob("*.html")) if B.SCENES.exists() else []
    return {"id": pid, "folder": str(p), "pasta_nome": amigavel(p), "estilo": estilo_of(ed, p), "conferir": _estado_vi(p) == "conferir", "edit": ed, "durations": dur, "scenes": scenes,
            "final": (p / "final.mp4").exists(), "leve": (p / "leve.mp4").exists()}


@app.put("/api/project/{pid}")
def save_project(pid: str, edit: dict = Body(...)):
    p = path_of(pid)
    hist = p / ".editor_hist"
    hist.mkdir(exist_ok=True)
    shutil.copy2(p / "edit.json", hist / f"edit-{time.strftime('%Y%m%d-%H%M%S')}.json")
    old = sorted(hist.glob("edit-*.json"))
    for f in old[:-40]:
        f.unlink()
    B.save_edit(p, edit)
    memo_limpar("projects", "relatorios", "estilos")
    return {"ok": True}


@app.post("/api/preview/{pid}")
def preview(pid: str, edit: dict = Body(...)):
    p = path_of(pid)
    tmp = p / ".editor_preview"
    tmp.mkdir(exist_ok=True)
    try:
        f = B.build(p, out_dir=tmp, edit=edit)
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, 500)
    if edit.get("template") in ("prebuilt", "auto"):
        rel = Path(f).relative_to(p).as_posix()
        return {"ok": True, "url": f"/p/{pid}/{rel}?ed=1&v={int(time.time() * 1000)}"}
    return {"ok": True, "url": f"/p/{pid}/.editor_preview/index.html?v={int(time.time() * 1000)}"}


@app.get("/api/baixar/{pid}/{which}")
def baixar(pid: str, which: str, inline: int = 0):
    """Baixa o vídeo pronto (which = final | leve) como anexo — usado pelos botões ⬇ da lista Meus vídeos (funciona no celular)."""
    kind, p = resolve_any(pid)
    if which in ("capa", "descricao"):   # 🖼 capa do Instagram e 📝 descricao.txt (criados pelo botão "Criar capa")
        if kind != "proj":
            raise HTTPException(404)
        arq, mt, ext = (("capa_instagram.jpg", "image/jpeg", ".jpg") if which == "capa" else ("descricao.txt", "text/plain; charset=utf-8", ".txt"))
        f = p / arq
        if not f.is_file():
            raise HTTPException(404, "a capa ainda não foi criada")
        nome = re.sub(r'[\\/:*?"<>|]+', " ", (B.load_edit(p).get("name") or p.name) + (" - capa" if which == "capa" else " - descricao")).strip()[:120]
        return FileResponse(f, media_type=mt, filename=nome + ext, content_disposition_type="attachment", headers={"Cache-Control": "no-cache"})
    if kind == "video":   # mp4 solto: só existe a versão "final"; precisa estar dentro de uma das pastas do painel
        if which != "final" or not any(Path(b).resolve() in p.resolve().parents for b in pastas_varredura()):
            raise HTTPException(404)
        f, nome = p, p.stem
    else:
        f = find_video(p) if which == "final" else (p / "leve.mp4" if which == "leve" else None)
        if f is None:
            raise HTTPException(404)
        if which == "leve" and not f.is_file():   # vídeo sem versão leve (feito antes dela existir): cria na hora a partir do final
            fin = find_video(p)
            if fin and fin.is_file():
                try:
                    dur = float(probe(fin) or 60)
                except Exception:
                    dur = 60.0
                B.make_light(fin, f, dur)
        nome = (B.load_edit(p).get("name") or p.name) + (" - leve" if which == "leve" else " - final")
    if not f or not f.is_file():
        raise HTTPException(404, "esse vídeo ainda não foi gerado")
    nome = re.sub(r'[\\/:*?"<>|]+', " ", nome).strip()[:120] or "video"
    # inline=1 → toca dentro da página (botão ▶ Assistir); sem isso → baixa como anexo
    return FileResponse(f, media_type="video/mp4", filename=nome + ".mp4", content_disposition_type="inline" if inline else "attachment",
                        headers={"Cache-Control": "no-cache"})


@app.get("/p/{pid}/{rel:path}")
def files(pid: str, rel: str):
    p = path_of(pid)
    f = safe_join(p, rel)
    if not f.exists() or not f.is_file():
        raise HTTPException(404)
    if f.suffix == ".html":
        html = f.read_text(encoding="utf-8")
        html = html.replace("</body>", '<script src="/static/shim.js"></script>\n</body>')
        return HTMLResponse(html, headers={"Cache-Control": "no-store"})
    return FileResponse(f, headers={"Cache-Control": "no-cache"})


# ------------------------------------------------------------------ ✨ ANIMAÇÕES PRONTAS (blocos do registry HyperFrames, templates/blocos/)
@app.get("/api/blocos")
def blocos_lista():
    out = []
    for j in sorted(B.BLOCOS.glob("*/bloco.json")) if B.BLOCOS.exists() else []:
        m = B.bloco_meta(j.parent.name)
        if not m:
            continue
        simples = [v for v in m.get("variables") or [] if v.get("type") in ("string", "number", "color", "boolean")]
        out.append({"name": m["name"], "titulo": m.get("titulo") or m["name"], "categoria": m.get("categoria", "Outros"),
                    "descricao": m.get("descricao", ""), "duration": m.get("duration", 5), "width": m.get("width", 1920),
                    "height": m.get("height", 1080), "textos": m.get("textos", []), "variables": simples,
                    "licenca": m.get("licenca", ""), "thumb": f"/api/blocos/{m['name']}/thumb.jpg" if (j.parent / "thumb.jpg").exists() else ""})
    return {"blocos": out}


@app.get("/api/blocos/{nome}/thumb.jpg")
def blocos_thumb(nome: str):
    f = B.BLOCOS / re.sub(r"[^\w.-]", "", nome) / "thumb.jpg"
    if not f.is_file():
        raise HTTPException(404)
    return FileResponse(f, headers={"Cache-Control": "max-age=3600"})


# ------------------------------------------------------------------ COMPARAR (referência x nosso vídeo)
import mimetypes
mimetypes.add_type("video/webm", ".webm")
mimetypes.add_type("video/mp4", ".mp4")
ESTILOS_NOVOS_DIR = Path(_mig(str(__import__("pathlib").Path(__file__).resolve().parents[1] / "ESTILOS-NOVOS")))
REF_EXTS = (".mp4", ".webm", ".mkv", ".mov")


def yt_id(url: str):
    m = re.search(r"(?:youtu\.be/|v=|shorts/|embed/)([\w-]{11})", str(url or ""))
    return m.group(1) if m else None


def _ref_in_dir(d: Path, vid_id=None):
    """vídeo de referência dentro de d: ref.mp4 / ref.webm / ref.mp4.webm / qualquer vídeo (com o id do YouTube no nome, se houver)."""
    if not d.is_dir():
        return None
    for n in ("ref.mp4", "ref.webm", "ref.mp4.webm"):
        f = d / n
        if f.is_file() and f.stat().st_size > 50_000:
            return f
    vids = [f for f in d.iterdir() if f.is_file() and f.suffix.lower() in REF_EXTS and f.stat().st_size > 50_000]
    if vid_id:
        hit = [f for f in vids if vid_id in f.name]
        if hit:
            return hit[0]
        return None
    return vids[0] if len(vids) == 1 else None


def _ref_index():
    """id do YouTube → arquivo de referência já baixado em qualquer projeto (pra reaproveitar entre projetos)."""
    idx = {}
    for base in conf()["folders"]:
        b = Path(base)
        if not b.exists():
            continue
        for e in b.glob("*/edit.json"):
            r = _ref_in_dir(e.parent / "ref")
            if not r:
                continue
            try:
                vid = yt_id((json.loads(e.read_text(encoding="utf-8-sig")).get("referencia") or {}).get("video"))
            except Exception:
                vid = None
            if vid:
                idx.setdefault(vid, (e.parent, r))
    return idx


def find_ref(p: Path, ed=None, idx=None):
    """→ (pasta_dona, arquivo) ou None."""
    r = _ref_in_dir(p / "ref")
    if r:
        return p, r
    if ed is None:
        try:
            ed = json.loads((p / "edit.json").read_text(encoding="utf-8-sig"))
        except Exception:
            ed = {}
    vid = yt_id((ed.get("referencia") or {}).get("video"))
    m = re.match(r"^(\d+)-", p.name)
    if m and ESTILOS_NOVOS_DIR.exists() and re.search(r"VIDEOS-NOVOS", str(p), re.I):
        for d in ESTILOS_NOVOS_DIR.glob(m.group(1) + "-*"):
            for dd in (d, d / "ref"):
                r = _ref_in_dir(dd, vid)
                if r:
                    return d, r
        if vid:
            for f in (ESTILOS_NOVOS_DIR / "_mineracao").rglob("*"):
                if f.is_file() and f.suffix.lower() in REF_EXTS and vid in f.name:
                    return f.parent, f
    if vid:
        hit = (idx if idx is not None else _ref_index()).get(vid)
        if hit:
            return hit
    return None


def _url_of(owner: Path, f: Path):
    """URL servível: /p/<pid>/<rel> se o dono tem edit.json, senão /api/abs."""
    if (owner / "edit.json").exists():
        try:
            return f"/p/{pid_of(owner)}/" + "/".join(urllib.parse.quote(x) for x in f.relative_to(owner).parts)
        except ValueError:
            pass
    return "/api/abs?path=" + urllib.parse.quote(str(f))


@app.get("/api/comparar/{pid}")
def comparar(pid: str):
    p = path_of(pid)
    try:
        raw = json.loads((p / "edit.json").read_text(encoding="utf-8-sig"))
    except Exception:
        raw = {}
    nosso = find_video(p)
    ref = find_ref(p, raw)
    return {"id": pid, "name": raw.get("name") or p.name, "estilo": estilo_of(raw, p), "referencia": raw.get("referencia") or {},
            "nosso_url": _url_of(p, nosso) if nosso else None, "ref_url": _url_of(*ref) if ref else None,
            "ref_arquivo": str(ref[1]) if ref else None, "ref_inicio": float(raw.get("ref_inicio") or 0)}


@app.post("/api/comparar/{pid}")
def comparar_salvar(pid: str, data: dict = Body(...)):
    """Salva só o campo ref_inicio (segundos) no edit.json, sem mexer no resto."""
    p = path_of(pid)
    raw = json.loads((p / "edit.json").read_text(encoding="utf-8-sig"))
    raw["ref_inicio"] = round(max(0.0, float(data.get("ref_inicio") or 0)), 2)
    B.save_edit(p, raw)
    return {"ok": True, "ref_inicio": raw["ref_inicio"]}


@app.get("/api/ref-thumb/{pid}")
def ref_thumb(pid: str, t: float = 40):
    """Quadro do vídeo de referência (original) em 480px — prévia "Original × Nosso" da tela inicial."""
    p = path_of(pid)
    r = find_ref(p)
    if not r:
        raise HTTPException(404)
    out = p / ".editor_cache" / f"refthumb-{int(t)}.jpg"
    if not out.exists():
        out.parent.mkdir(exist_ok=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(int(t)), "-i", str(r[1]), "-frames:v", "1", "-vf", "scale=480:-2",
                        "-q:v", "4", str(out)], timeout=60, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    if not out.exists():
        raise HTTPException(404)
    return FileResponse(out, headers={"Cache-Control": "max-age=86400"})


@app.get("/api/abs")
def abs_file(path: str, request: Request):
    """Mídia com caminho absoluto (ex.: SFX da biblioteca) — só tipos de mídia e só pra quem está no próprio PC."""
    if (request.client.host if request.client else "") not in ("127.0.0.1", "::1", "localhost"):
        raise HTTPException(403)
    f = Path(path)
    if f.suffix.lower() not in (".wav", ".mp3", ".m4a", ".aac", ".ogg", ".mp4", ".webm", ".mov", ".png", ".jpg", ".jpeg", ".webp", ".gif"):
        raise HTTPException(403)
    if not f.exists():
        raise HTTPException(404)
    return FileResponse(f)


def _media_path(p: Path, src: str) -> Path:
    f = Path(src)
    f = f if f.is_absolute() else safe_join(p, src)
    if not f.exists():
        raise HTTPException(404)
    return f


def _cache(p: Path, src: str, tag: str, ext: str) -> Path:
    import hashlib
    f = _media_path(p, src)
    h = hashlib.md5(f"{f}|{f.stat().st_mtime}|{tag}".encode()).hexdigest()[:16]
    d = p / ".editor_cache"
    d.mkdir(exist_ok=True)
    return d / f"{h}.{ext}"


@app.get("/api/wave/{pid}")
def wave(pid: str, src: str):
    """Desenho da onda do áudio (PNG transparente) para a linha do tempo."""
    p = path_of(pid)
    out = _cache(p, src, "wave", "png")
    if not out.exists():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(_media_path(p, src)), "-filter_complex",
                        "aformat=channel_layouts=mono,showwavespic=s=3000x60:colors=#d9ffe9:scale=sqrt", "-frames:v", "1", str(out)],
                       timeout=60, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    if not out.exists():
        raise HTTPException(404)
    return FileResponse(out, headers={"Cache-Control": "max-age=86400"})


@app.get("/api/frame/{pid}")
def frame(pid: str, src: str, t: float = 0.5):
    """Miniatura de um vídeo/imagem para os blocos da linha do tempo."""
    p = path_of(pid)
    out = _cache(p, src, f"frame{t:.1f}", "jpg")
    if not out.exists():
        f = _media_path(p, src)
        seek = [] if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp") else ["-ss", f"{t:.2f}"]  # imagem: -ss dava 404
        subprocess.run(["ffmpeg", "-v", "error", "-y", *seek, "-i", str(f), "-frames:v", "1",
                        "-vf", "scale=-2:64", "-q:v", "5", str(out)], timeout=60,
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    if not out.exists():
        raise HTTPException(404)
    return FileResponse(out, headers={"Cache-Control": "max-age=86400"})


def relatorio_of(p: Path, ed=None):
    """Lê RELATORIO.json (+ tamanho do vídeo) de um projeto; tolera BOM e campos faltando."""
    r = {}
    f = p / "RELATORIO.json"
    if f.exists():
        try:
            r = json.loads(f.read_text(encoding="utf-8-sig"))
        except Exception:
            r = {"observacoes": "RELATORIO.json inválido"}
    rs = r.get("render_segundos")
    if isinstance(rs, dict):
        nums = [v for v in rs.values() if isinstance(v, (int, float))]
        r["render_segundos"] = sum(nums) if nums else None
    tk = r.get("tokens")
    if isinstance(tk, dict):
        r["tokens_detalhe"] = tk
        r["tokens"] = tk.get("totais") or tk.get("novos")
    vid = find_video(p)
    r["tamanho_mb"] = round(vid.stat().st_size / 1e6, 1) if vid else None
    if ed is None:
        try:
            ed = B.load_edit(p, convert=False)
        except Exception:
            ed = {}
    r.update({"id": pid_of(p), "name": ed.get("name") or p.name, "estilo": estilo_of(ed, p), "dur": edit_duration(ed), "folder": str(p)})
    r["local"] = r.get("tokens") == 0 or bool(r.get("ferramenta"))   # feito pelas ferramentas do PC (sem Claude)
    return r


@app.get("/api/relatorios")
def relatorios():
    return memo("relatorios", lambda: [relatorio_of(Path(pr["folder"])) for pr in projects() if pr.get("tipo") != "video"],
                ttl=30, sig=lambda: _sig_dirs(pastas_varredura()))


@app.get("/api/relatorio/{pid}")
def relatorio(pid: str):
    return relatorio_of(path_of(pid))


@app.get("/relatorio", response_class=HTMLResponse)
def relatorio_page():
    return (ROOT / "static" / "relatorio.html").read_text(encoding="utf-8")


@app.api_route("/api/thumb/{pid}", methods=["GET", "HEAD"])   # QA: a lista confere com HEAD se a miniatura ficou pronta (antes: 405 → miniatura só aparecia dando F5)
def thumb(pid: str):
    kind, p = resolve_any(pid)
    t = video_thumb_path(p) if kind == "video" else p / "thumb.jpg"
    if t.exists():
        return FileResponse(t, headers={"Cache-Control": "max-age=3600"})   # a URL já leva ?mtime
    return Response(status_code=404)


@app.post("/api/upload/{pid}")
async def upload(pid: str, file: UploadFile = File(...)):
    p = path_of(pid)
    d = p / "midia"
    d.mkdir(exist_ok=True)
    name = "".join(c for c in Path(file.filename).name if c.isalnum() or c in "._- ") or "arquivo"
    dst = d / name
    i = 1
    while dst.exists():
        dst = d / f"{Path(name).stem}_{i}{Path(name).suffix}"
        i += 1
    with open(dst, "wb") as fh:
        while True:
            chunk = await file.read(1 << 20)
            if not chunk:
                break
            fh.write(chunk)
    rel = dst.relative_to(p).as_posix()
    return {"src": rel, "dur": probe(dst)}


@app.post("/api/capa/{pid}")
def capa_criar(pid: str, data: dict = Body(default={})):
    """Botão "🖼 Criar capa" da tela "Vídeo pronto": capa 9:16 (capa_instagram.jpg) + descricao.txt na pasta do vídeo."""
    p = path_of(pid)
    import importlib
    import capa as CAPA
    import capa_arte as _CA
    importlib.reload(_CA)
    import capa_cena as _CC
    importlib.reload(_CC)
    importlib.reload(CAPA)   # pega mudanças no código de capa sem precisar reiniciar o editor

    def fazer(prog):
        aj = AJ.ler()
        r = CAPA.criar(p, aj["modelo_ollama"], aj["idioma"], prog, titulo=(data or {}).get("titulo"), canal=(data or {}).get("canal"), tipo=(data or {}).get("tipo"), cena=(data or {}).get("cena"))
        return {"pid": pid, "folder": str(p), "capa_url": f"/p/{pid}/capa_instagram.jpg", "texto": r["texto"], "aviso_cena": r.get("aviso_cena", "")}
    return start_job(fazer, tipo="capa", titulo="🖼 Criando a capa", pesado=False)


@app.post("/api/open/{pid}")
def open_thing(pid: str, what: str = "folder"):
    kind, p = resolve_any(pid)
    if kind == "video":  # mp4 solto: "folder" abre a pasta dele; o resto abre o próprio vídeo
        target = p.parent if what == "folder" else p
    else:
        target = {"folder": p, "final": find_video(p) or p / "final.mp4", "leve": p / "leve.mp4", "capa": p / "capa_instagram.jpg", "descricao": p / "descricao.txt"}.get(what, p)
    if target.exists():
        abrir(target)
        return {"ok": True}
    return {"ok": False}


# ------------------------------------------------------------------ jobs (fila de trabalhos: render / fábrica / pedido / vídeo com imagens / roteiro)
JOBS_FILE = ROOT / ("jobs.json" if PORT == 8780 else f"jobs-{PORT}.json")   # instância de teste não mexe na fila da principal


class Cancelado(Exception):
    pass


def _job_eta(j):
    """Segundos que faltam, só quando dá pra estimar de verdade (≥ 15 s rodando e ≥ 5 pontos de progresso medidos)."""
    p0 = j.get("_p0")
    if j.get("status") != "rodando" or not p0 or j.get("done"):
        return None
    dt, dp = time.time() - p0[0], float(j.get("pct") or 0) - p0[1]
    if dt < 15 or dp < 5:
        return None
    return int(dt * (100 - float(j["pct"])) / dp)


def _job_pub(j):
    d = {k: v for k, v in j.items() if not k.startswith("_")}
    d["eta"] = _job_eta(j)
    return d


def _salvar_jobs(force=False):
    now = time.time()
    if not force and now - _salvar_jobs.t < 3:
        return
    _salvar_jobs.t = now
    try:
        lst = sorted(JOBS.values(), key=lambda j: j.get("criado") or 0, reverse=True)[:80]
        tmp = JOBS_FILE.with_suffix(".tmp")   # grava inteiro e troca (queda de energia não deixa o arquivo vazio)
        tmp.write_text(json.dumps([_job_pub(j) for j in lst], ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, JOBS_FILE)
    except Exception:
        pass


_salvar_jobs.t = 0


def _carregar_jobs():
    try:
        for j in json.loads(JOBS_FILE.read_text(encoding="utf-8")):
            if not j.get("done"):
                j.update(done=True, status="erro", error="O painel foi fechado no meio deste trabalho. Mande fazer de novo.", fim=time.time())
            j["_cancel"], j["_proc"] = False, None
            JOBS[j["id"]] = j
    except Exception:
        pass


def start_job(fn, *args, tipo="render", titulo="", pesado=False, pid=None):
    """Cria um trabalho na fila. pesado=True → espera a vez (1 trabalho pesado por vez: render, fábrica, IA local)."""
    jid = uuid.uuid4().hex[:10]
    J = {"id": jid, "tipo": tipo, "titulo": titulo, "status": "fila" if pesado else "rodando", "pct": 0, "msg": "Começando…",
         "done": False, "error": None, "result": None, "criado": time.time(), "inicio": None, "fim": None, "pesado": pesado, "pid": pid,
         "_cancel": False, "_proc": None}
    JOBS[jid] = J

    def prog(pct, msg):
        if J["_cancel"]:
            raise Cancelado()
        J.update(pct=round(pct, 1), msg=msg)
        if J["status"] == "rodando" and "_p0" not in J and pct > 0:
            J["_p0"] = (time.time(), float(pct))   # QA: ETA conta a partir do 1º progresso (render começa em 12% → antes dava "faltam 10 s")
        _salvar_jobs()
    prog.job = J

    def runner():
        tem_vez = False
        try:
            if pesado:
                _esperar_vez(prog)
                tem_vez = True
            J["status"], J["inicio"] = "rodando", time.time()
            J["result"] = fn(*args, prog)
            J["status"], J["pct"] = "pronto", 100
        except Cancelado:
            J.update(status="cancelado", error="Cancelado.", msg="Cancelado")
        except Exception as e:
            if J["_cancel"]:
                J.update(status="cancelado", error="Cancelado.", msg="Cancelado")
            else:
                traceback.print_exc()
                err = str(e)
                J.update(status="erro", error=err if len(err) <= 12000 else err[:6000] + "\n…\n" + err[-6000:])
        finally:
            if tem_vez:
                _liberar_vez()
            J["done"], J["fim"], J["_proc"] = True, time.time(), None
            memo_limpar()   # trabalho terminou → lista/estilos/relatórios refeitos no próximo pedido
            _salvar_jobs(True)

    threading.Thread(target=runner, daemon=True).start()
    _salvar_jobs(True)
    return {"job": jid}


def _matar(p):
    try:
        subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"], capture_output=True, timeout=20,
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    except Exception:
        try:
            p.kill()
        except Exception:
            pass


def rodar_proc(cmd, prog, cwd=None, lo=0, hi=100, render=None):
    """Roda um script ligado ao trabalho: linhas "@@pct|msg" viram progresso (escala lo..hi);
    linhas "  12.0%  msg" do build_from_edit viram progresso de render dentro de render=(a,b) (escala local 0-100)."""
    env = AJ.env_chaves({**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUNBUFFERED": "1"})
    p = subprocess.Popen([str(c) for c in cmd], cwd=str(cwd) if cwd else None, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                         encoding="utf-8", errors="replace", env=env, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    J = getattr(prog, "job", None)
    if J is not None:
        J["_proc"] = p
    tail, loc = [], 0.0
    escala = lambda x: lo + x * (hi - lo) / 100
    try:
        for line in p.stdout:
            line = line.rstrip()
            if not line:
                continue
            tail = (tail + [line])[-30:]
            if "RENDER_ERRO_LOG:" in line:
                prog._render_log = line.split("RENDER_ERRO_LOG:", 1)[1].strip()
            m = re.match(r"^@@(\d+)\|(.*)", line)
            if m:
                loc = float(m.group(1))
                prog(escala(loc), m.group(2))
                continue
            m = re.match(r"^\s*(\d+(?:\.\d+)?)%\s+(.*)", line)
            if m and render and loc >= render[0]:
                loc = max(loc, render[0] + float(m.group(1)) * (render[1] - render[0]) / 100)
                prog(escala(loc), "Renderizando: " + m.group(2))
    except BaseException:   # leve 01/11: cancelado OU qualquer erro no meio → mata a árvore (antes só no Cancelado)
        if p.poll() is None:
            _matar(p)
        raise
    p.wait()
    if J is not None:
        J["_proc"] = None
        if J["_cancel"]:
            raise Cancelado()
    if p.returncode != 0:
        log_f = getattr(prog, "_render_log", None)
        if log_f and Path(log_f).exists():   # render do HyperFrames caiu todas as vezes → começo + fim do log
            raise RuntimeError(Path(log_f).read_text(encoding="utf-8", errors="replace")[-12000:])
        raise RuntimeError("\n".join(tail[-12:]))
    return tail


def _job_orfao(r):
    try:
        if r.get("estilo_id") and not (ESTILOS_FAB / Path(str(r["estilo_id"])).name).exists():
            return True
        if r.get("pid") and not _decode_pid(str(r["pid"])).exists():
            return True
    except Exception:
        return False
    return False


@app.get("/api/jobs")
def jobs_list():
    now = time.time()
    with FAB_COND:
        fila_ids = [getattr(t, "jid", None) for t in FAB_QUEUE]
    out = []
    for j in sorted(JOBS.values(), key=lambda j: j.get("criado") or 0, reverse=True)[:60]:
        d = _job_pub(j)
        r = d.pop("result", None) or {}
        d["resultado"] = {k: r.get(k) for k in ("pid", "name", "rendered", "conferir", "rid", "precisa_claude", "cid", "fid", "estilo_id", "amostra_url", "leve_mb") if k in r} if r else None
        if j.get("done") and r and _job_orfao(r):   # 07/11: estilo/projeto apagado → o botão levaria a nada; some da fila
            continue
        if r.get("folder"):
            d["resultado"]["pasta_nome"] = amigavel(r["folder"])
        d["decorrido"] = int((j.get("fim") or now) - j["inicio"]) if j.get("inicio") else 0
        d["total"] = int(j["fim"] - j["criado"]) if j.get("fim") and j.get("criado") else None   # do clique em "fazer vídeo" até ficar pronto (inclui a espera na fila)
        if j["status"] == "fila" and j["id"] in fila_ids:
            d["posicao"] = fila_ids.index(j["id"]) + 1
        out.append(d)
    return out


@app.post("/api/jobs/{jid}/cancelar")
def job_cancelar(jid: str):
    j = JOBS.get(jid)
    if not j:
        raise HTTPException(404)
    if j["done"]:
        return {"ok": False, "msg": "Esse trabalho já terminou."}
    j["_cancel"] = True
    j["msg"] = "Cancelando…"
    if j.get("_proc"):
        _matar(j["_proc"])
    return {"ok": True}


@app.post("/api/jobs/limpar")
def jobs_limpar():
    for k in [k for k, j in JOBS.items() if j.get("done")]:
        JOBS.pop(k, None)
    _salvar_jobs(True)
    return {"ok": True}


@app.post("/api/render/{pid}")
def render(pid: str):
    p = path_of(pid)

    def job(proj, prog):
        rodar_proc([sys.executable, ROOT / "build_from_edit.py", proj, "--render"], prog, cwd=ROOT, render=(0, 100))
        f = proj / "final.mp4"
        sz = lambda x: round(x.stat().st_size / 1e6, 1) if x.exists() else None
        r = {"pid": pid_of(proj), "folder": str(proj), "name": proj.name, "rendered": f.exists(), "final": str(f), "final_mb": sz(f),
             "leve": str(proj / "leve.mp4"), "leve_mb": sz(proj / "leve.mp4")}
        if f.exists() and not os.environ.get("MEDICO_OFF"):   # médico do render: confere o vídeo e avisa (não conserta sozinho)
            try:
                prog(99, "Conferindo tela preta e frames congelados…")
                diag = MED.diagnosticar(proj)
                try:
                    (proj / "medico.md").write_text(MED._relatorio(diag), encoding="utf-8")
                except Exception:
                    pass
                r["medico"] = {"problemas": len(diag.get("problemas", [])), "corrigiveis": diag.get("corrigiveis", 0)}
            except Exception:
                pass
        return r
    try:
        nome = B.load_edit(p, convert=False).get("name") or p.name
    except Exception:
        nome = p.name
    return start_job(job, p, tipo="render", titulo=nome, pesado=True, pid=pid)


@app.get("/api/job/{jid}")
def job(jid: str):
    if jid not in JOBS:
        raise HTTPException(404)
    return _job_pub(JOBS[jid])


def _chave_freesound():
    try:
        return (conf().get("freesound") or "").strip() or None
    except Exception:
        return None


@app.get("/api/som/buscar")
def som_buscar(q: str, n: int = 12):
    """Busca som livre (CC0/CC BY) no Openverse (+ Freesound se tiver chave). Só leitura, não baixa."""
    if not (q or "").strip():
        return {"itens": []}
    try:
        return {"itens": SOM.buscar(q.strip(), max(1, min(24, n)), {"freesound": _chave_freesound()})}
    except Exception as e:
        raise HTTPException(502, f"Não consegui buscar sons agora: {e}")


@app.post("/api/som/baixar/{pid}")
def som_baixar(pid: str, item: dict = Body(...)):
    """Baixa um som escolhido pro projeto (sons/) e registra o crédito. Devolve o src pro editor."""
    if not item.get("download"):
        raise HTTPException(400, "Som sem link de download.")
    try:
        return SOM.baixar(item, path_of(pid))
    except Exception as e:
        raise HTTPException(502, f"Não consegui baixar o som: {e}")


@app.get("/api/densidade/{pid}")
def densidade(pid: str):
    """Mede quanto do vídeo é gráfico e diz quais 'Suas regras' estão ligadas."""
    p = path_of(pid)
    try:
        edit = B.load_edit(p, convert=False)
    except Exception:
        raise HTTPException(404)
    return {"medida": DENS.medir(edit), "regras": DENS.regras_densidade(edit)}


@app.post("/api/densidade/{pid}/aplicar")
def densidade_aplicar(pid: str):
    """Derruba o excesso de gráfico no edit.json conforme as regras (reversível; guarda .bak-densidade)."""
    return DENS.aplicar_em_disco(path_of(pid))


@app.get("/api/medico/{pid}")
def medico(pid: str):
    """Diagnóstico do médico do render (tela preta / frame congelado) do vídeo pronto."""
    p = path_of(pid)
    return MED.diagnosticar(p, video=find_video(p))


@app.post("/api/medico/{pid}/corrigir")
def medico_corrigir(pid: str):
    """Conserta o que dá sozinho e re-renderiza (como trabalho pesado na fila)."""
    p = path_of(pid)

    def job(proj, prog):
        prog(2, "Lendo o que precisa consertar…")
        res = MED.corrigir(proj, render=False)
        if not res.get("mudou"):
            return {"pid": pid, "mudou": False, "consertos": [], "medico": {"problemas": len(res.get("antes", {}).get("problemas", [])), "corrigiveis": 0}}
        prog(8, "Renderizando de novo com os consertos…")
        rodar_proc([sys.executable, ROOT / "build_from_edit.py", proj, "--render"], prog, cwd=ROOT, render=(8, 96))
        prog(97, "Conferindo de novo…")
        depois = MED.diagnosticar(proj)
        try:
            (proj / "medico.md").write_text(MED._relatorio(depois) + "\n\n## Consertos aplicados\n"
                                            + "\n".join(f"- {c}" for c in res["consertos"]), encoding="utf-8")
        except Exception:
            pass
        return {"pid": pid, "mudou": True, "consertos": res["consertos"],
                "medico": {"problemas": len(depois.get("problemas", [])), "corrigiveis": depois.get("corrigiveis", 0)}}

    try:
        nome = B.load_edit(p, convert=False).get("name") or p.name
    except Exception:
        nome = p.name
    return start_job(job, p, tipo="medico", titulo="Consertar vídeo: " + nome, pesado=True, pid=pid)


# ------------------------------------------------------------------ PEDIR VÍDEO (catálogo de estilos + fila da fábrica)
import sys
import unicodedata
import urllib.parse
import urllib.request
from datetime import datetime

FABRICA = ROOT / "fabrica"
ESTILOS_FAB = FABRICA / "estilos"
TESTE_DIR = Path(_mig(str(__import__("pathlib").Path(__file__).resolve().parents[1])))
VIDEOS_TESTE = TESTE_DIR / "VIDEOS"
ESTILOS_NOVOS = TESTE_DIR / "ESTILOS-NOVOS"
OUT_PEDIDOS = VIDEOS_TESTE                      # onde a fábrica e os pedidos criam pastas
PEDIDOS_TMP = ROOT / ".pedidos"                 # roteiros enviados pelo usuário (arquivo p/ --roteiro)
DESC_FAB = {
    "historia-simples": "Documentário de história com fotos antigas em sépia e câmera lenta (Ken Burns). Narração em terceira pessoa.",
    "reddit-story": "História de Reddit ('Eu sou o babaca?') com o card do post e legenda palavra por palavra sobre gameplay.",
    "psicologia-sombria": "Ensaio de psicologia/filosofia com pinturas clássicas, ritmo lento e perguntas ao espectador.",
}
FAB_COND = threading.Condition()
FAB_QUEUE = []          # tickets esperando a vez (1 render por vez)
FAB_BUSY = [False]


def slug(s, maxlen=40):
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode()
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()
    return s[:maxlen].rstrip("-")


def proximo_numero(out_dir: Path):
    n = 0
    for p in out_dir.iterdir():
        m = re.match(r"^(\d{2,3})", p.name)
        if m and p.is_dir():
            n = max(n, int(m.group(1)))
    return n + 1


def _ref_of_dir(p: Path):
    try:
        return B.load_edit(p, convert=False).get("referencia") or {}
    except Exception:
        return {}


def _ler_md(p: Path):
    try:
        return p.read_text(encoding="utf-8-sig")
    except Exception:
        return ""


def _estilo_novo(d: Path):
    """Pasta NN-nome de ESTILOS-NOVOS → item 'em breve' (nome do ESTILO.md, referência do REFERENCIA.txt, 1ª sheet)."""
    md = _ler_md(d / "ESTILO.md")
    m = re.search(r"^#\s*\d*\s*[—-]?\s*(.+)$", md, re.M)
    nome = (m.group(1).strip() if m else d.name).strip()
    desc = ""
    for par in re.split(r"\n\s*\n", md)[1:]:
        t = re.sub(r"[*#`]", "", par).strip()
        if t and not t.startswith("##"):
            desc = t
            break
    ref = {}
    rt = _ler_md(d / "REFERENCIA.txt")
    m = re.search(r"^##\s*(.+?)\s+[—-]+\s+(https?://\S+)", rt, re.M)
    if m:
        ref = {"canal": re.sub(r"\s*\[.*?\]\s*$", "", m.group(1)).strip(), "canal_url": m.group(2)}
    m = re.search(r"^\s*-\s*\S+\s*\|\s*(https?://\S+)\s*\|.*\|\s*(.+)$", rt, re.M)
    if m:
        ref.update(video=m.group(1), titulo=m.group(2).strip())
    sheets = sorted(d.glob("sheet-*.jpg")) or sorted(d.glob("*.jpg"))
    return {"id": "novo:" + d.name, "nome": nome, "tipo": "em_breve", "descricao": desc[:220],
            "thumb_url": "/api/estilo-img?path=" + urllib.parse.quote(str(sheets[0])) if sheets else None, "referencia": ref, "pasta": str(d)}


def _galerias():
    """Pastas de projetos-exemplo de estilos: VIDEOS (+ VIDEOS-NOVOS e VIDEOS-SHORTS ao lado, se existirem) → (pasta, prefixo do id)."""
    out = [(VIDEOS_TESTE, "")]
    for nome, pre in (("VIDEOS-NOVOS", "novos:"), ("VIDEOS-SHORTS", "shorts:")):
        d = VIDEOS_TESTE.parent / nome
        if d.exists():
            out.append((d, pre))
    return out


def _exemplo(d: Path, ed: dict, ridx):
    """Dados do vídeo-exemplo de um estilo (pra galeria da tela inicial): pid, vídeo, formato, se tem referência baixada."""
    vid = find_video(d)
    cv = ed.get("canvas") or {}
    short = (cv.get("h") or 0) > (cv.get("w") or 0)
    return {"pid": pid_of(d), "video_url": _url_of(d, vid) if vid else None, "formato": "short" if short else "longo",
            "dur": edit_duration(ed), "tem_ref": bool(vid) and bool(find_ref(d, ed, ridx)), "pasta": str(d),
            "thumb_url": f"/api/thumb/{pid_of(d)}" if (d / "thumb.jpg").exists() else None}


def catalogo_estilos():
    """Lista unificada: fábrica (0 token) + projetos-teste que precisam do Claude + catálogo 'em breve'."""
    res, origens = [], set()
    ridx = _ref_index()
    if ESTILOS_FAB.exists():
        for d in sorted(ESTILOS_FAB.iterdir()):
            if not (d / "preencher.py").exists():
                continue
            try:
                cfg = json.loads((d / "estilo.json").read_text(encoding="utf-8-sig"))
            except Exception:
                cfg = {}
            if cfg.get("so_ferramenta"):   # estilo usado só pela ferramenta "Vídeo com imagens"
                continue
            m = re.search(r"VIDEOS[\\/]([^\s(\\/]+)", cfg.get("origem", ""))
            orig = VIDEOS_TESTE / m.group(1) if m else None
            thumb, ref, ex = None, {}, {}
            if orig and (orig / "edit.json").exists():
                origens.add(orig.name)
                ref = _ref_of_dir(orig)
                if (orig / "thumb.jpg").exists():
                    thumb = f"/api/thumb/{pid_of(orig)}"
                try:
                    ex = _exemplo(orig, B.load_edit(orig, convert=False), ridx)
                except Exception:
                    ex = {}
            res.append({**ex, "id": d.name, "nome": cfg.get("nome") or d.name, "tipo": "fabrica", "thumb_url": thumb, "referencia": ref,
                        "galeria": "VIDEOS", "descricao": cfg.get("descricao") or DESC_FAB.get(d.name) or cfg.get("roteiro_prompt", "")[:200],
                        "formatos": cfg.get("formatos") or ["longo"], "bom_para": cfg.get("bom_para") or []})
    novos_nums = set()
    for base, pre in _galerias():
        for d in sorted(base.iterdir()):
            if not d.is_dir() or not re.match(r"^\d{2}-", d.name) or "-fabrica-" in d.name or "-pedido-" in d.name or "-imagens-" in d.name:
                continue
            if (not pre and d.name in origens) or not (d / "edit.json").exists():
                continue
            try:
                ed = B.load_edit(d, convert=False)
            except Exception:
                ed = {}
            nome_v = re.sub(r"^\d+\s*-\s*[^-]+-\s*", "", str(ed.get("name") or d.name))
            desc = f"Exemplo pronto: “{nome_v}”. Precisa do Claude para montar as cenas."
            nome_e = estilo_of(ed, d)
            if pre == "novos:":
                novos_nums.add(d.name[:2])
                cat = next(iter(sorted(ESTILOS_NOVOS.glob(d.name[:2] + "-*"))), None) if ESTILOS_NOVOS.exists() else None
                if cat and (cat / "ESTILO.md").exists():
                    info = _estilo_novo(cat)
                    desc = info.get("descricao") or desc
                    if re.match(r"^\d{2}-", nome_e):   # edit.json com "estilo" = nome da pasta → nome do catálogo
                        nome_e = info.get("nome") or nome_e
            if re.match(r"^\d{2}-", nome_e):
                nome_e = estilo_of({"name": ed.get("name")}, d)
            res.append({**_exemplo(d, ed, ridx), "id": "claude:" + pre + d.name, "nome": nome_e, "tipo": "claude",
                        "referencia": ed.get("referencia") or {}, "galeria": base.name, "exemplo": nome_v, "descricao": desc})
    if ESTILOS_NOVOS.exists():
        for d in sorted(ESTILOS_NOVOS.iterdir()):
            if d.is_dir() and re.match(r"^\d{2}-", d.name) and (d / "ESTILO.md").exists() and d.name[:2] not in novos_nums:
                res.append(_estilo_novo(d))
    # dedup: 1 card por estilo (nome), prefere o que tem vídeo
    seen = {}
    for x in res:
        n = x.get("nome", "")
        if n not in seen or (not seen[n].get("video_url") and x.get("video_url")):
            seen[n] = x
    return list(seen.values())


@app.get("/api/estilos")
def estilos():
    return memo("estilos", catalogo_estilos, ttl=60,
                sig=lambda: _sig_dirs([ESTILOS_FAB] + [g for g, _ in _galerias()] + ([ESTILOS_NOVOS] if ESTILOS_NOVOS.exists() else [])))


@app.get("/api/estilo-img")
def estilo_img(path: str):
    """Miniatura de estilo (só .jpg/.png dentro de ESTILOS-NOVOS ou VIDEOS de teste)."""
    f = Path(path).resolve()
    if f.suffix.lower() not in (".jpg", ".jpeg", ".png", ".webp"):
        raise HTTPException(403)
    if not any(base.resolve() in f.parents for base in (ESTILOS_NOVOS, VIDEOS_TESTE)):
        raise HTTPException(403)
    if not f.exists():
        raise HTTPException(404)
    return FileResponse(f, headers={"Cache-Control": "max-age=3600"})


def yt_info(url: str):
    """yt-dlp --print canal_url|canal|titulo (40 s, falha silenciosa)."""
    try:
        out = subprocess.run([*RYT.cmd(),"--no-warnings", "--skip-download", "--print", "%(channel_url)s|%(channel)s|%(title)s", url],
                             capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=40,
                             creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)).stdout.strip().splitlines()
        parts = (out[-1] if out else "").split("|", 2)
        if len(parts) == 3 and parts[0].startswith("http"):
            return {"canal_url": parts[0], "canal": parts[1], "titulo": parts[2]}
    except Exception:
        pass
    return {}


def completar_referencia(ref, prog=None):
    if ref.get("video"):
        if prog:
            prog(2, "Lendo os dados do vídeo de referência…")
        info = yt_info(ref["video"])
        for k, v in info.items():
            if v and not ref.get(k):
                ref[k] = v
    elif ref.get("canal_url") and not ref.get("canal"):
        m = re.search(r"youtube\.com/(@[^/?#]+)", ref["canal_url"])
        if m:
            ref["canal"] = m.group(1)
    return ref


ETAPAS = [  # (regex na linha do fabrica.py, %, mensagem em PT)
    (r"Projeto:", 3, "Preparando a pasta do vídeo…"),
    (r"roteiro", 10, "Escrevendo o roteiro (IA local, pode levar 1-2 min)…"),
    (r"TTS|voz", 30, "Gravando a narração (voz)…"),
    (r"whisper|transcri", 45, "Sincronizando a legenda com a voz…"),
    (r"shots de", 52, "Dividindo o vídeo em cenas…"),
    (r"img \d+|wikimedia|gameplay", 55, "Buscando imagens…"),
    (r"edit\.json", 72, "Montando as cenas…"),
    (r"build_from_edit", 75, "Renderizando o vídeo…"),
    (r"PRONTO em", 99, "Finalizando…"),
]


class _Ticket:
    def __init__(self, jid):
        self.jid = jid


def _esperar_vez(prog):
    J = getattr(prog, "job", None) or {}
    ticket = _Ticket(J.get("id"))
    with FAB_COND:
        FAB_QUEUE.append(ticket)
    try:
        while True:
            with FAB_COND:
                pos = FAB_QUEUE.index(ticket)
                if pos == 0 and not FAB_BUSY[0]:
                    FAB_BUSY[0] = True
                    FAB_QUEUE.pop(0)
                    return
            prog(0, f"Na fila, posição {pos + 1} — esperando o trabalho anterior terminar (1 por vez)…")
            time.sleep(2)
    except BaseException:
        with FAB_COND:
            if ticket in FAB_QUEUE:
                FAB_QUEUE.remove(ticket)
        raise


def _liberar_vez():
    with FAB_COND:
        FAB_BUSY[0] = False


def _gravar_marca(pasta, texto):
    """Guarda a marca d'água DESTE vídeo na pasta dele (o render lê de lá). Vazio apaga."""
    f = Path(pasta) / "marca_dagua.txt"
    t = str(texto or "").strip()[:60]
    try:
        if t:
            f.write_text(t, encoding="utf-8")
        elif f.exists():
            f.unlink()
    except OSError:
        pass


def job_fabrica(ped, prog):
    if True:   # a vez na fila (1 pesado por vez) é pega pelo start_job(pesado=True)
        aj = AJ.ler()
        ref = completar_referencia(ped["referencia"], prog)
        cmd = [sys.executable, "fabrica.py", "--estilo", ped["estilo"], "--canal", ped["canal_nome"], "--duracao", str(ped["duracao"]),
               "--out", str(out_dir()), "--modelo", aj["modelo_ollama"], "--ref-canal", ref.get("canal", ""), "--ref-canal-url", ref.get("canal_url", ""),
               "--ref-video", ref.get("video", ""), "--ref-titulo", ref.get("titulo", "")]
        if ped.get("marca"):
            cmd += ["--marca", ped["marca"]]
        if ped.get("regras"):
            cmd += ["--regras-json", json.dumps(ped["regras"], ensure_ascii=False)]
        if ped.get("formato") == "short":   # estilo de fábrica com 9:16 (estilo.json "formatos")
            cmd += ["--formato", "short"]
        mu = ped.get("musica") or {}
        if mu.get("modo") in ("auto", "minha"):
            cmd += ["--musica", "auto" if mu["modo"] == "auto" else mu["arquivo"], "--musica-nivel", mu.get("nivel") or "baixa"]
            if mu.get("nivel") == "presente" and mu.get("duck") is False:
                cmd += ["--musica-sem-duck"]
        if ped.get("claude_roteiro"):
            cmd += ["--claude-roteiro"]
        if ped.get("claude_busca"):
            cmd += ["--claude-busca"]
        if ped.get("roteiro"):
            PEDIDOS_TMP.mkdir(exist_ok=True)
            rp = PEDIDOS_TMP / f"roteiro-{time.strftime('%Y%m%d-%H%M%S')}.txt"
            rp.write_text(ped["roteiro"], encoding="utf-8")
            cmd += ["--roteiro", str(rp), "--tema", ped.get("tema") or ped["roteiro"][:60]]
            if (ped.get("tema") or "").strip():   # QA: com tema + roteiro próprio, o título é o tema (antes pegava a 1ª frase do roteiro)
                cmd += ["--titulo", ped["tema"].strip()[:120]]
        else:
            cmd += ["--tema", ped["tema"]]
        voz = ped.get("voz") or aj.get("voz")
        if ped.get("audio"):   # narração pronta: pula o TTS (a fábrica sincroniza pelo Whisper)
            cmd += ["--voz", ped["audio"]]
        elif voz:
            motor, _, nome = voz.partition(":")
            cmd += ["--tts", motor]
            if nome:
                cmd += ["--voz-nome", nome]
        env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUNBUFFERED": "1"}
        prog(3, "Começando a fábrica…")

        def rodar(cmd, pasta=None):
            p = subprocess.Popen(cmd, cwd=str(FABRICA), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                 encoding="utf-8", errors="replace", env=env, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            prog.job["_proc"] = p
            pct, tail, n_img = 3, [], 0
            try:
                return _ler_fabrica(p, pasta, pct, tail, n_img)
            except BaseException:   # leve 01/11: Cancelado/erro no meio da leitura → mata a fábrica (antes ficava rodando órfã)
                if p.poll() is None:
                    _matar(p)
                raise

        def _ler_fabrica(p, pasta, pct, tail, n_img):
            for line in p.stdout:
                line = line.rstrip()
                if not line:
                    continue
                tail = (tail + [line])[-25:]
                if line.startswith("PASTA: "):
                    pasta = Path(line[7:].strip())
                m = re.match(r"^\s*(\d+(?:\.\d+)?)%\s+(.*)", line)   # progresso do build_from_edit --render
                if m and pct >= 75:
                    pct = max(pct, 75 + float(m.group(1)) * 0.24)
                    prog(pct, "Renderizando: " + m.group(2))
                    continue
                for rx, p_, msg in ETAPAS:
                    if re.search(rx, line, re.I) and p_ > pct:
                        pct = p_
                        prog(pct, msg)
                        break
                if re.search(r"img \d+", line) and pct < 72:
                    n_img += 1
                    pct = min(71, 55 + n_img * 0.8)
                    prog(pct, f"Buscando imagens… ({n_img})")
            p.wait()
            prog.job["_proc"] = None
            if prog.job["_cancel"]:
                raise Cancelado()
            return p.returncode, tail, pasta

        rc, tail, pasta = rodar(cmd)
        if rc != 0 and re.search(r"out of memory|HTTP Error 500|cudaMalloc", "\n".join(tail), re.I) and "--modelo" not in cmd:
            # modelo Ollama padrão não coube na placa (outra coisa usando a GPU) → tenta o menor, retomando a mesma pasta
            prog(5, "A IA principal não coube na memória da placa — tentando com o modelo menor (qwen)…")
            rc, tail, pasta = rodar(cmd + ["--modelo", "qwen2.5:7b"] + (["--pasta", str(pasta)] if pasta else []), pasta)
        if rc != 0:
            raise RuntimeError("A fábrica parou com erro:\n" + "\n".join(tail[-12:]))
        if not pasta or not (pasta / "edit.json").exists():
            dirs = [d for d in out_dir().iterdir() if d.is_dir() and (d / "edit.json").exists()]
            pasta = max(dirs, key=lambda d: (d / "edit.json").stat().st_mtime)
        ed = B.load_edit(pasta, convert=False)
        mudou = False
        if not ed.get("referencia") and any(ref.values()):
            ed["referencia"] = ref
            mudou = True
        if ped.get("regras") and not ed.get("regras"):   # "Suas regras" pedidas no formulário → valem já no 1º render
            ed["regras"] = ped["regras"]
            mudou = True
        if mudou:
            B.save_edit(pasta, ed)
        vid = find_video(pasta)
        prog(100, "Pronto!")
        return {"pid": pid_of(pasta), "folder": str(pasta), "name": ed.get("name") or pasta.name, "rendered": bool(vid),
                "video": str(vid) if vid else None, "precisa_claude": False}


def _baixar_ref(url: str, dest: Path):
    """Baixa os primeiros ~3 min da referência (reaproveita ferramentas/baixar_refs.py; senão, yt-dlp direto)."""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("baixar_refs", ROOT / "ferramentas" / "baixar_refs.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.baixar(url, dest)
    except FileNotFoundError:
        pass
    except Exception as e:
        return False, str(e)[:300]
    dest.parent.mkdir(exist_ok=True)
    r = subprocess.run([*RYT.cmd(),"--no-playlist", "--no-part", "--force-overwrites", "--download-sections", "*0-180",
                        "-f", "18/b[ext=mp4][height<=480]/bv*[height<=480]+ba/b", "--merge-output-format", "mp4", "-o", str(dest), url], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=600, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    ok = dest.exists() and dest.stat().st_size > 50_000
    return ok, "" if ok else ((r.stderr or r.stdout or "").strip().splitlines() or ["sem saída"])[-1]


CLONE_REGRAS = [
    "## Como CLONAR (obrigatório — o resultado tem que ter as MESMAS edições do vídeo de referência)",
    "1. **Analisar com o ReelMimic primeiro** (mais preciso): rode `~/.claude/skills/reelmimic/.venv/Scripts/python.exe -X utf8 "
    "~/.claude/skills/reelmimic/scripts/analyze.py ref/ref.mp4 --out analise_ref` e use o `analise_ref/report.json` (cortes, duração de cada plano, "
    "BPM e batidas, movimento de câmera e luz/cor por plano, clímax) como base da tabela de cenas; faça também a folha de quadros com "
    "`scripts/clip_strip.py` da mesma skill. Se o `.venv` não existir, crie (`python -m venv .venv` + `pip install -r requirements.txt` dentro da "
    "pasta da skill). Só se o ReelMimic falhar de vez, meça na mão como abaixo. "
    "Depois complete a análise do vídeo inteiro (`ref/ref.mp4`): duração, formato, folha de quadros a cada ~1 s (ffmpeg tile, NÃO abrir frame por frame), "
    "transcrição com tempos (faster-whisper / skill `watch`), tempos de corte (ffmpeg `select='gt(scene,0.3)'`), legenda (fonte, tamanho, cor, "
    "contorno, posição, palavra a palavra ou frase), zooms/punch-ins, transições, textos na tela, b-roll, música e SFX (onde e quais), ritmo. "
    "Escrever tudo em `ANALISE.md` com uma tabela de cenas (início, fim, o que aparece, efeito).",
    "2. **Escolher a ferramenta mais parecida**: listar as skills instaladas (`~/.claude/skills/*/SKILL.md`, ler as descrições) e os estilos do painel "
    "(`{root}/FORMATO.md`, `templates/`). Se alguma cobre ~70% do visual, usar ela e completar o resto por código.",
    "3. **Se nada for parecido, procurar na internet** uma skill/template que faça esse tipo de edição: GitHub (busca por `SKILL.md` + o estilo, "
    "\"claude skill\", \"hyperframes\", \"remotion template\"), o registro do HyperFrames (skill `hyperframes-registry`) e posts no X. "
    "Regras de SEGURANÇA pra instalar coisa de fora (sem exceção): só repositório público com licença MIT/Apache-2.0/BSD/CC0/ISC; ler o SKILL.md e "
    "TODOS os scripts antes; recusar se baixa e executa binário desconhecido, usa `curl | bash`, código ofuscado, pede senha/chave/token, manda dados "
    "pra fora ou mexe fora da própria pasta. Instalar em `~/.claude/skills/<nome>` e guardar uma cópia com o LICENSE em "
    "`{root}/skills_ia/baixadas/<nome>/`, anotando fonte, licença e commit em `{root}/skills_ia/baixadas/FONTES.md`.",
    "4. **Recriar fiel**: mesma duração e formato, cortes nos mesmos tempos, mesma legenda (fonte parecida do Google Fonts se a original não for livre), "
    "mesmas cores, posições, zooms, transições, textos na tela, SFX nos mesmos pontos e música no mesmo clima. O CONTEÚDO é o do aluno (tema/roteiro "
    "abaixo): não copiar o texto palavra por palavra nem usar imagem/música com direito autoral da referência (usar banco livre ou gerar).",
    "5. **Conferir**: montar `COMPARACAO.jpg` (folha de quadros da referência em cima, do seu vídeo embaixo, mesmos tempos) e corrigir o que estiver "
    "diferente até ficar igual. Anotar em `ANALISE.md` o que ficou igual e o que não deu.",
    "6. **Virar estilo do painel**: se usou/baixou uma skill que ainda não está no painel, escrever `{root}/skills_ia/baixadas/<nome>/painel.json` "
    "({{\"id\",\"nome\",\"emoji\",\"entrada\":\"texto|video|ambos\",\"formato\":\"short|longo\",\"quando\",\"exemplo\"}}) e copiar o vídeo pronto pra "
    "`{root}/skills_ia/previews/<id>.mp4` — assim o estilo aparece sozinho na aba 🤖 Estilos IA pros próximos vídeos.",
    "",
]


def _tts_instrucao(voz, pasta):
    """Linha do PEDIDO.md: como gerar a narração com a voz escolhida no painel (inclusive voz clonada)."""
    motor, _, nome = (voz or AJ.ler()["voz"]).partition(":")
    return ("- Narração: gere com o TTS do PRÓPRIO painel pra usar a voz escolhida (" + (voz or "padrão dos Ajustes") + "): escreva o texto da fala em "
            "`narracao.txt` e rode `python -X utf8 -c \"import sys, pathlib; sys.path.insert(0, r'" + str(FABRICA) + "'); from lib import tts; "
            "pathlib.Path(r'" + str(Path(pasta) / "voz") + "').mkdir(exist_ok=True); "
            "print(tts.falar(open('narracao.txt', encoding='utf-8').read(), r'" + str(Path(pasta) / "voz") + "', '" + (motor or "auto") + "', "
            + (repr(nome) if nome else "None") + "))\"` (o áudio sai na pasta `voz/`). Não troque por outra voz.")


PED_FALHAS = {}   # (pedido, estilo, tema) → pasta da última tentativa que não gerou vídeo


def _canvas_modelo(est, fonte, short):
    """(w, h, (w_nativo, h_nativo)): para 'projeto-teste pronto' usa o formato nativo do modelo (o 39 é 1280x720);
    nos outros casos, o formato pedido."""
    pedido = (1080, 1920) if short else (1280, 720)
    try:
        if est.get("tipo") == "claude" and fonte:
            c = json.loads((Path(fonte) / "edit.json").read_text(encoding="utf-8-sig")).get("canvas") or {}
            nat = (int(c["w"]), int(c["h"]))
            if short != (nat[1] > nat[0]):   # o aluno pediu outro formato (ex.: 9:16 num modelo 16:9): vale o pedido
                return pedido[0], pedido[1], nat
            return nat[0], nat[1], nat
    except Exception:
        pass
    return pedido[0], pedido[1], pedido


def _regras_fidelidade(est, fonte, cw, ch, nativo):
    """Regras extras do PEDIDO.md quando o estilo é um 'projeto-teste pronto' (tipo claude): o vídeo TEM que usar o
    template e o visual do modelo — nunca cair no template 'generic' (fica só foto escurecida + texto)."""
    f = Path(fonte) if fonte else None
    if est.get("tipo") != "claude" or not f or not f.is_dir():
        return []
    try:
        tmpl_modelo = str(json.loads((f / "edit.json").read_text(encoding="utf-8-sig")).get("template") or "generic")
    except Exception:
        tmpl_modelo = "generic"
    scripts = [n for n in ("make_edit.py", "gerar_edit.py", "build.py", "gen_texturas.py") if (f / n).exists()]
    scripts_txt = ", ".join(f"`{f / n}`" for n in scripts) or "(o modelo não tem script: use o `edit.json` dele como guia)"
    docs = [n for n in ("ESTILO.md", "BREAKDOWN.md") if (f / n).exists()]
    docs_txt = " e ".join(f"`{f / n}`" for n in docs) or f"`{f / 'edit.json'}`"
    L = ["## FIDELIDADE AO MODELO (obrigatório)"]
    if tmpl_modelo == "generic":
        L += [f"- O resultado tem que ficar com o MESMO visual, ritmo e DENSIDADE de cenas do vídeo-exemplo da pasta `{f}` (o `thumb.jpg`/`sheet.jpg` dele mostram o alvo). "
              "Este modelo é feito com o template `generic`, então use `generic` — mas SEM simplificar: o exemplo usa foto em moldura/movimento, textos sobre a foto, cenas (`scene`) de capítulo, "
              "`html` de vinheta/grão etc. Se o vídeo ficar como 'foto escurecida + texto' e menos elaborado que o exemplo, está errado.",
              f"- Primeiro leia {docs_txt} e o `edit.json` do modelo (conte os itens por tipo: `image`, `text`, `scene`, `html`, `caption` e copie a mesma proporção por minuto), e o(s) script(s) dele: {scripts_txt}.",
              "- Copie para a pasta do projeto o que o modelo usa (`fonts/`, música/sfx, `hf/` se houver) e adapte o script do modelo para gerar um `edit.json` NOVO com o roteiro novo. NÃO copie as fotos do assunto antigo.",
              "- Se o tema pedido for outro, mantenha a estrutura do modelo (ex.: abertura/gancho → capítulos com cartão de capítulo → desfecho) e o mesmo número de elementos por cena."]
    else:
        L += [f"- O resultado tem que ficar com o MESMO visual e movimento do vídeo-exemplo da pasta `{f}`. É PROIBIDO usar `\"template\": \"generic\"` "
              "(foto escurecida + texto) ou simplificar o estilo por falta de tempo. Se o vídeo ficar como 'fundo estático com textos', está errado.",
              f"- Primeiro leia {docs_txt}, `{f / 'template_src.html'}` (ou `template.html`) e `{f / 'edit.json'}` do modelo, e o(s) script(s): {scripts_txt}.",
              "- Copie para a pasta do projeto o que o modelo usa: `template.html`/`template_src.html`, `fonts/`, `sfx/`, a música (se houver), as texturas (ex.: mesa, grão, moldura) e os scripts do modelo. NÃO copie as fotos do assunto antigo.",
              f"- No `edit.json` use o mesmo `template` do modelo (`\"{tmpl_modelo}\"`) e a mesma estrutura de itens/objetos/câmera/fios/carimbos; escreva um script NOVO com os objetos e a câmera do roteiro novo, cena por cena (uma 'prova' diferente por frase, câmera em movimento contínuo, carimbos, fios, lupa, etc., como no modelo)."]
    L += ["- RITMO E ANIMAÇÃO (a checagem automática reprova se não cumprir): o vídeo não pode ser mais lento nem mais 'seco' que o modelo — "
          "no mínimo os mesmos cortes por minuto, nenhuma cena parada (só 'aparecer'), e em cada cena pelo menos 1 elemento ANIMADO que mostre o dado da frase "
          "(número contando, nível subindo, ponteiro, risco, linha desenhando, barra, relógio…). Cena que passar de ~4 s: divida em duas.",
          f"- ANTES de renderizar e de entregar rode: `python {ROOT / 'checar_ritmo.py'} \"<pasta do projeto>\"` (depois do render: com `--final`). "
          "Se aparecer ✗ ERRO, corrija o edit.json/cenas e rode de novo até dar APROVADO. O `build_from_edit.py --render` recusa a 1ª versão reprovada."]
    if "saga-sobrevivencia" in f.name and (ROOT.parent / "kits" / "saga-2d" / "widgets.js").exists():
        k = ROOT.parent / "kits" / "saga-2d"
        L += [f"- KIT PRONTO deste estilo (use em vez de desenhar SVG novo): leia `{k / 'README.md'}`. Resumo: depois de copiar o `template.html` do modelo, rode "
              f"`python {k / 'embutir.py'} \"<pasta do projeto>\"` e, no `gerar_edit.py`, use `from lib_edit import Video` (em `{k}`) com `v.cena_w(...)` e as peças "
              "animadas prontas (garrafa, relogio, bateria, sinal, calendario, medidor, grafico, barra, contador, lista, carimbo, pulso, rafa). "
              "Os segundos vêm sempre da fala (`v.at(\"palavra\")`)."]
    L += ["- Fotos: reais de domínio público/CC (Wikimedia) com créditos em `img/creditos.json`. Música baixa + whoosh suave como no modelo; nunca 'impact' nem 'pop'.",
          (f"- Formato: o modelo foi feito em {nativo[0]}x{nativo[1]}, mas o aluno pediu {cw}x{ch}. FAÇA NO FORMATO PEDIDO ({cw}x{ch}, `canvas` do edit.json já está assim): "
           "adapte o template/script do modelo para esse enquadramento (reposicione HUD, rótulos, painéis e câmera; textos maiores; nada cortado nas bordas/zona segura de Reels), "
           "sem simplificar o estilo. O `data-width`/`data-height` do template também precisam ser " + f"{cw}x{ch}." if (cw, ch) != tuple(nativo) else
           f"- Formato: este estilo foi feito em {nativo[0]}x{nativo[1]}. Mantenha o formato nativo do modelo (a pasta já foi criada com {cw}x{ch})."),
          "- Antes de entregar: gere o contact-sheet do mp4 e compare com `sheet.jpg` do modelo. Se não parecer o mesmo estilo, refaça até parecer."]
    return L + [""]


def job_pedido_claude(ped, est, prog):
    ref = completar_referencia(ped["referencia"], prog)
    prog(40, "Criando a pasta do pedido…")
    OUT = out_dir()
    copiar = est["tipo"] == "copiar"
    titulo = (ped.get("tema") or ped.get("roteiro") or "video").strip().splitlines()[0][:80]
    sig = ("pedido", est.get("id") or est["nome"], titulo)
    antiga = PED_FALHAS.get(sig)
    if antiga and Path(antiga).is_dir() and not (Path(antiga) / "final.mp4").exists():
        pasta = Path(antiga)   # tentar de novo depois de uma falha: reaproveita a pasta (não deixa uma pasta vazia pra trás)
        m = re.match(r"(\d+)-", pasta.name); nn = int(m.group(1)) if m else proximo_numero(OUT)
    else:
        nn = proximo_numero(OUT)
        pasta = OUT / f"{nn:02d}-pedido-{slug(est['nome'], 22)}-{slug(titulo, 28)}"
    pasta.mkdir(parents=True, exist_ok=True)
    PED_FALHAS[sig] = str(pasta)
    _gravar_marca(pasta, ped.get("marca"))
    if ped.get("audio") and Path(ped["audio"]).exists():
        shutil.copy2(ped["audio"], pasta / ("narracao" + Path(ped["audio"]).suffix.lower()))
    else:
        ped["audio"] = ""
    mus_cfg, mus_linha = None, "- Música de fundo: **nenhuma** — NÃO adicione música de fundo (`audio.music` fica vazio). Só whoosh suave, se quiser."
    mu = ped.get("musica") or {}
    if mu.get("modo") in ("auto", "minha"):
        try:
            from lib import musica as MUS
            mus_cfg = MUS.preparar(pasta, mu["modo"], texto=f"{ped.get('tema', '')} {ped.get('roteiro', '')}", estilo=est.get("id", ""),
                                   nivel=mu.get("nivel") or "baixa", duck=mu.get("duck") is not False, arquivo=mu.get("arquivo") or None, duracao=ped["duracao"])
        except Exception as e:
            print("música de fundo falhou:", type(e).__name__, e)
        if mus_cfg:
            mus_linha = (f"- Música de fundo: **já escolhida e preparada** — `{mus_cfg['arquivo']}` ({mus_cfg['titulo']}; {mus_cfg['motivo']}). "
                         "O `edit.json` desta pasta já tem `audio.music` com o volume certo (normalizado, abaixa quando o narrador fala): "
                         "**mantenha esse bloco exatamente como está** (não troque a música, não aumente o volume, não ponha outra música por cima).")
        else:
            mus_linha = "- Música de fundo: o painel não conseguiu preparar a música — siga SEM música de fundo."
    nome = " - ".join(x for x in (f"{nn:02d}", datetime.now().strftime('%d-%m-%Y'), ped['canal_nome'].strip().upper(), titulo) if x)
    nome = re.sub(r'[<>:"/\\|?*]', "", nome)[:200]
    fonte = est.get("pasta") or ""
    short = (ped.get("formato") or est.get("formato")) == "short"
    msg_claude = f"faz o vídeo do PEDIDO.md em {pasta}"
    tipo_txt = ("ESTILO NOVO copiado do vídeo de referência: assistir `ref/ref.mp4` (frames + transcrição) e recriar o visual, "
                "o ritmo dos cortes, as legendas, a música e a narração no mesmo jeito" if copiar else
                'projeto-teste pronto (reusar o template, o visual e o movimento do modelo — ver FIDELIDADE AO MODELO abaixo)' if est['tipo'] == 'claude' else 'estilo novo do catálogo (ler o ESTILO.md)')
    linhas = [
        f"# PEDIDO DE VÍDEO — {nome}", "",
        "> Este vídeo foi pedido pelo Estúdio de Vídeos (Editor de Vídeos Local) e precisa do Claude para ser montado.",
        "> **Como usar:** abra o Claude Code e mande: `" + msg_claude + "` (seguindo o CLAUDE.md do ESTUDIO-VIDEOS)", "",
        "## Estilo",
        f"- Nome: **{est['nome']}**",
        f"- Tipo: {tipo_txt}",
        f"- Formato: {'📱 short vertical 1080x1920' if short else '🎬 vídeo longo horizontal 1280x720'}",
        f"- Onde está o modelo do estilo: `{fonte or (pasta / 'ref' / 'ref.mp4')}`", "",
        "## Referência (canal/vídeo que o aluno quer copiar)",
        f"- Canal: {ref.get('canal') or '—'}",
        f"- Link do canal: {ref.get('canal_url') or '—'}",
        f"- Vídeo copiado: {ref.get('video') or '—'}",
        f"- Título do vídeo copiado: {ref.get('titulo') or '—'}", "",
        "## O que fazer",
        (f"- Nome do canal ESCRITO PELO ALUNO: **{ped['canal_nome']}** — escreva exatamente esse nome na tela do vídeo (e só ele)."
         if ped["canal_nome"].strip() else
         "- Nome do canal: **vazio** — NÃO escreva nenhum nome de canal, logo ou assinatura na imagem do vídeo."),
        (f"- Marca d'água: **{ped['marca']}** — o painel coloca sozinho no render final; NÃO desenhe esse texto no vídeo." if ped.get("marca") else
         "- Marca d'água: nenhuma. Não coloque logo, assinatura nem nome de canal por cima do vídeo."),
        f"- Tema / título: {ped.get('tema') or '(usar o roteiro abaixo)'}",
        f"- Duração alvo: {int(ped['duracao'])} segundos",
        f"- Voz: {ped.get('voz') or 'padrão (TTS local)'}",
        mus_linha,
        (f"- NARRAÇÃO PRONTA (voz já gravada pelo aluno): `{pasta / ('narracao' + Path(ped['audio']).suffix.lower())}` — use EXATAMENTE este áudio como locução "
         "do vídeo inteiro (NÃO gere TTS, não regrave, não corte frases). Ele diz o mesmo que o roteiro abaixo: transcreva com tempos (Whisper: "
         f"`{FABRICA / 'lib' / 'whisper_run.py'}`) e sincronize cenas, textos e legenda com a fala. Duração do vídeo = duração do áudio (+ respiro curto no fim). "
         "Coloque o áudio em `audio.voice` do edit.json." if ped.get("audio") else _tts_instrucao(ped.get("voz"), pasta)),
        f"- Pasta do projeto: `{pasta}`",
        *([f"- Suas regras (guarda de densidade): {json.dumps(ped['regras'], ensure_ascii=False)} — respeite no edit.json (menos gráfico/animação; legenda e footage intactos)."] if ped.get("regras") else []), "",
        "## Roteiro APROVADO pelo aluno (texto fixo — NÃO reescreva)" if ped.get("roteiro") else "## Roteiro",
        *(["> Use este texto EXATAMENTE como narração, palavra por palavra. Não reescreva, não resuma, não acrescente nem tire frases "
           "(só pode ajustar a pontuação pra voz ler bem). As cenas seguem o texto.", ""] if ped.get("roteiro") else []),
        ped["roteiro"] if ped.get("roteiro") else "(não enviado — escrever roteiro no idioma do canal, gancho nos 3-5 s, zero fato inventado, CTA de like espalhado)", "",
        *([x.format(root=ROOT) for x in CLONE_REGRAS] if copiar else []),
        *_regras_fidelidade(est, fonte, *_canvas_modelo(est, fonte, short)),
        "## Regras",
        "- Rodando SOZINHO pelo painel: NÃO faça perguntas; decida o melhor e anote em `DECISOES.md`. Instale o que faltar sem pedir.",
        "- Escrever o `edit.json` nesta pasta (FORMATO.md), mídias dentro da pasta, `referencia` preenchida como acima.",
        "- Renderizar com `build_from_edit.py <pasta> --render` e gravar `RELATORIO.json` (tokens e custo).",
        "- Depois disso o card na lista do editor troca de ⏳ para ✅ sozinho.",
    ]
    (pasta / "PEDIDO.md").write_text("\n".join(linhas), encoding="utf-8")
    cw, ch, *_ = _canvas_modelo(est, fonte, short)
    edit = {"version": 1, "name": nome, "canvas": {"w": cw, "h": ch, "fps": 30, "bg": "#0b0c10"}, "duration": float(ped["duracao"]),
            "template": "generic", "estilo": est["nome"], "referencia": ref,
            "pedido": {"tema": ped.get("tema", ""), "canal": ped["canal_nome"], "duracao": ped["duracao"], "voz": ped.get("voz", ""),
                       "estilo_id": est["id"], "criado": datetime.now().isoformat(timespec="seconds"), "arquivo": "PEDIDO.md"},
            **({"regras": ped["regras"]} if ped.get("regras") else {}),
            "audio": ({"music": mus_cfg["music"]} if mus_cfg else {}), "tracks": [{"id": "fundo", "name": "Cenas / mídia"}, {"id": "textos", "name": "Textos"}], "items": []}
    (pasta / "edit.json").write_text(json.dumps(edit, ensure_ascii=False, indent=1), encoding="utf-8")
    ref_ok, ref_erro = None, ""
    if copiar and ref.get("video"):
        prog(55, "Baixando o vídeo que você quer copiar (pode levar 1-3 min)…")
        try:
            ref_ok, ref_erro = _baixar_ref(ref["video"], pasta / "ref" / "ref.mp4")
        except Exception as e:
            ref_ok, ref_erro = False, str(e)[:300]
    base = {"pid": pid_of(pasta), "folder": str(pasta), "name": nome, "pedido_md": str(pasta / "PEDIDO.md"), "mensagem_claude": msg_claude,
            "ref_baixada": ref_ok, "ref_erro": ref_erro}
    if not _claude_exe() or ped.get("so_pedido"):
        prog(100, "Pedido criado!")
        PED_FALHAS.pop(sig, None)
        return {**base, "rendered": False, "precisa_claude": True, "sem_claude": not _claude_exe()}
    memo_limpar()
    r = _claude_rodar(pasta, prog, f"Claude montando o vídeo no estilo {est['nome']}…",
                      f"Faça o vídeo do PEDIDO.md desta pasta ({pasta}), seguindo o FORMATO.md do editor ({ROOT / 'FORMATO.md'}). "
                      "Você está rodando sozinho pelo painel: não faça perguntas, decida e siga até renderizar o final.mp4 com build_from_edit.py.")
    fim = r["fim"]
    if not find_video(pasta):
        raise RuntimeError("O Claude terminou mas não renderizou o vídeo.\n" + (str(fim.get("result") or "") or "\n".join(r["resto"]))[-3000:]
                           + "\n\n(Detalhes técnicos: claude-log.jsonl na pasta do vídeo.)")
    try:
        rel_f = pasta / "RELATORIO.json"
        rel = json.loads(rel_f.read_text(encoding="utf-8-sig")) if rel_f.exists() else {}
        us = fim.get("usage") or {}
        rel.setdefault("tokens", sum(int(us.get(k) or 0) for k in ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")) or None)
        rel.setdefault("custo_usd", fim.get("total_cost_usd"))
        rel.setdefault("minutos", r["minutos"])
        rel_f.write_text(json.dumps(rel, ensure_ascii=False, indent=1), encoding="utf-8")
    except Exception:
        pass
    memo_limpar()
    prog(100, f"Pronto em {r['minutos']} min!")
    PED_FALHAS.pop(sig, None)
    return {**base, "rendered": True, "precisa_claude": False}


def _limpar_regras(r):
    """Normaliza as 'Suas regras' do formulário de pedido para o dict que o guarda_densidade lê.
    Só aceita chaves/valores conhecidos (não confia no cliente). None se não houver nada."""
    if not isinstance(r, dict):
        return None
    out = {}
    if r.get("broll_primeiro"):
        out["broll_primeiro"] = True
    if r.get("sem_animacao"):
        out["sem_animacao"] = True
    try:
        if r.get("intervalo_min"):
            out["intervalo_min"] = max(1.0, min(30.0, float(r["intervalo_min"])))
    except Exception:
        pass
    try:
        if r.get("max_pct"):
            out["max_pct"] = max(5.0, min(100.0, float(r["max_pct"])))
    except Exception:
        pass
    return out or None


@app.post("/api/pedido")
def pedido(data: dict = Body(...)):
    """Pedido de vídeo novo. Devolve {job, tipo, precisa_claude}; o resultado do job traz {pid, folder, name, rendered}."""
    g = lambda k: str(data.get(k) or "").strip()
    if g("estilo") == "copiar":   # tela "🔗 Copiar o estilo de um vídeo novo"
        if not g("ref_video"):
            raise HTTPException(400, "Cole o link do vídeo que você quer copiar.")
        est = {"id": "copiar", "nome": "Copiar estilo", "tipo": "copiar", "formato": "short" if g("formato") == "short" else "longo"}
    else:
        est = next((e for e in catalogo_estilos() if e["id"] == g("estilo")), None)
    if not est:
        raise HTTPException(400, "Escolha um estilo da galeria.")
    tema, roteiro, canal = g("tema"), g("roteiro"), g("canal_nome")
    if not tema and not roteiro:
        raise HTTPException(400, "Escreva o tema do vídeo (ou cole seu roteiro).")
    try:
        dur = float(data.get("duracao") or 60)
    except Exception:
        raise HTTPException(400, "Duração inválida.")
    if not 15 <= dur <= 10800:
        raise HTTPException(400, "Duração precisa ficar entre 15 segundos e 3 horas.")
    audio = ""
    if g("audio_id"):   # narração pronta subida pelo aluno (mp3/wav/m4a): vale no lugar da voz do PC
        a = PEDIDOS_TMP / Path(g("audio_id")).name
        if not a.exists():
            raise HTTPException(400, "O áudio que você enviou não está mais aqui. Suba o arquivo de novo.")
        audio = str(a)
        dur = float(probe(a) or dur)
    url_ok = lambda u: not u or re.match(r"^https?://\S+\.\S+", u)
    if not url_ok(g("ref_video")) or not url_ok(g("ref_canal")):
        raise HTTPException(400, "Link inválido — cole o link completo (começa com https://).")
    ref = dict(est.get("referencia") or {}) if not (g("ref_video") or g("ref_canal")) else {}
    if g("ref_video"):
        ref["video"] = g("ref_video")
    if g("ref_canal"):
        ref["canal_url"] = g("ref_canal")
    ped = {"estilo": est["id"], "tema": tema, "roteiro": roteiro, "canal_nome": canal, "duracao": dur, "voz": g("voz"), "referencia": ref,
           "formato": g("formato") or est.get("formato") or "longo", "so_pedido": bool(data.get("so_pedido")),
           "marca": g("marca")[:60],   # QA: só cria a pasta/PEDIDO.md, sem rodar o Claude
           # 🧠 opcional (só fábrica, precisa da chave em Ajustes): o Claude escreve o roteiro / escolhe as buscas de imagem
           "claude_roteiro": bool(data.get("claude_roteiro")) and not roteiro, "claude_busca": bool(data.get("claude_busca")),
           "audio": audio}
    ped["musica"] = _musica_do_pedido(data.get("musica"))   # 🎵 nenhuma / automática / a minha (+ volume + abaixar quando o narrador fala)
    rg = _limpar_regras(data.get("regras"))   # "Suas regras" do formulário → viram edit["regras"] (guarda de densidade) antes de gerar
    if rg:
        ped["regras"] = rg
    if g("formato") in ("short", "longo"):
        est = {**est, "formato": g("formato")}
    if est["tipo"] == "fabrica":
        r = start_job(job_fabrica, ped, tipo="fabrica", titulo=(tema or roteiro[:60]) + f" · {est['nome'][:40]}", pesado=True)
        with FAB_COND:
            fila = len(FAB_QUEUE) + (1 if FAB_BUSY[0] else 0)
        return {**r, "tipo": "fabrica", "precisa_claude": False, "fila": fila}
    r = start_job(job_pedido_claude, ped, est, tipo="pedido", titulo=(tema or roteiro[:60]) + f" · {est['nome'][:40]}")
    return {**r, "tipo": est["tipo"], "precisa_claude": True}


def _musica_do_pedido(m):
    """Escolha de música do formulário → {"modo": nenhuma|auto|minha, "nivel": baixa|presente, "duck": bool, "arquivo": caminho}."""
    m = m if isinstance(m, dict) else {}
    modo = m.get("modo") if m.get("modo") in ("auto", "minha") else "nenhuma"
    nivel = "presente" if m.get("nivel") == "presente" else "baixa"
    out = {"modo": modo, "nivel": nivel, "duck": m.get("duck") is not False, "arquivo": ""}
    if modo == "minha":
        f = PEDIDOS_TMP / Path(str(m.get("arquivo_id") or "")).name
        if not m.get("arquivo_id") or not f.exists():
            raise HTTPException(400, "Você escolheu \"minha música\", mas ainda não enviou o arquivo. Envie o áudio (ou escolha Automática/Nenhuma).")
        out["arquivo"] = str(f)
    return out


@app.post("/api/musica/subir")
async def musica_subir(file: UploadFile = File(...)):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in (".mp3", ".wav", ".m4a", ".ogg", ".opus", ".flac", ".aac"):
        raise HTTPException(400, "Envie um arquivo de música (mp3, wav, m4a…).")
    PEDIDOS_TMP.mkdir(exist_ok=True)
    dst = PEDIDOS_TMP / f"mus-{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:4]}{ext}"
    with open(dst, "wb") as fh:
        while True:
            ch = await file.read(4 << 20)
            if not ch:
                break
            fh.write(ch)
    d = probe(dst)
    if not d:
        dst.unlink(missing_ok=True)
        raise HTTPException(400, "Não consegui ler esse arquivo de áudio.")
    return {"arquivo_id": dst.name, "nome": file.filename, "dur": d}


@app.get("/api/musica/sugerir")
def musica_sugerir(tema: str = "", roteiro: str = "", estilo: str = ""):
    """Qual música o modo Automática escolheria agora (só mostra; a escolha final é feita na hora de criar o vídeo)."""
    from lib import musica as MUS
    e = MUS.escolher(f"{tema} {roteiro}", estilo)
    if not e:
        return {"ok": False}
    return {"ok": True, "titulo": e["titulo"], "motivo": e["motivo"],
            "url": e["url"] if e.get("remoto") else "/api/musica/ouvir/" + e["arquivo"]}


@app.get("/api/musica/ouvir/{arq}")
def musica_ouvir(arq: str):
    from lib import musica as MUS
    f = MUS.BIB / Path(arq).name
    if f.suffix.lower() != ".mp3" or not f.exists():
        raise HTTPException(404)
    return FileResponse(f, media_type="audio/mpeg")


@app.get("/api/claude-custo")
def claude_custo(duracao: float = 60, estilo: str = ""):
    """Quanto custa (média estimada) deixar o Claude escrever o roteiro / escolher as buscas de imagem num vídeo de `duracao` segundos."""
    from lib import claude_api
    cfg = {}
    f = FABRICA / "estilos" / re.sub(r"[^\w\-]", "", estilo) / "estilo.json"
    if estilo and f.exists():
        try:
            cfg = json.loads(f.read_text(encoding="utf-8-sig"))
        except Exception:
            cfg = {}
    shot_medio = (float(cfg.get("shot_min", 2.4)) + float(cfg.get("shot_max", 5.5))) / 2 if cfg else 5.5
    est = claude_api.estimar(max(15.0, min(float(duracao), 10800.0)), cfg.get("palavras_por_minuto", 150), max(shot_medio, 1.0))
    chave = str(AJ.ler().get("anthropic_key") or "").strip()
    est["tem_chave"] = bool(chave)
    est["modo"] = claude_api.modo(chave)   # "api" (chave) | "plano" (Claude instalado neste PC) | None
    return est


@app.post("/api/open-path")
def open_path(data: dict = Body(...)):
    """Abre pasta/arquivo de um pedido (só dentro das pastas configuradas)."""
    f = Path(str(data.get("path") or "")).resolve()
    bases = [Path(x).resolve() for x in pastas_varredura()] + [OUT_PEDIDOS.resolve(), out_dir().resolve()]
    if not f.exists() or not any(b == f or b in f.parents for b in bases):
        raise HTTPException(403)
    abrir(f)
    return {"ok": True}


# ================================================================== FERRAMENTAS (fase 1): Ajustes · Vídeo com imagens · Conferir imagens · Roteiro pronto
sys.path.insert(0, str(FABRICA))
from lib import ajustes as AJ  # noqa: E402
from lib import bancos as BANCOS  # noqa: E402
from lib import rede_yt as RYT  # noqa: E402

ROTEIROS_DIR = ROOT / "roteiros"
CACHE_DIR = ROOT / ".cache"
_carregar_jobs()


def out_dir() -> Path:
    d = Path(_mig(AJ.ler().get("pasta_saida")) or OUT_PEDIDOS)
    try:
        d.mkdir(parents=True, exist_ok=True)
        return d
    except Exception:
        return OUT_PEDIDOS


def pastas_varredura():
    fs = list(conf()["folders"])
    o = str(out_dir())
    if all(Path(f).resolve() != Path(o).resolve() for f in fs):
        fs.append(o)
    return fs


def amigavel(path) -> str:
    """Caminho do PC → nome amigável (a interface nunca mostra C:\\Users\\...)."""
    s = str(path or "")
    home = str(Path.home())
    for pre, nome in ((str(Path.home() / "Desktop"), "Área de Trabalho"), (str(Path.home() / "Documents"), "Documentos"),
                      (str(Path.home() / "Downloads"), "Downloads"), (str(Path.home() / "Videos"), "Vídeos"), (home, "Sua pasta")):
        if s.lower().startswith(pre.lower()):
            resto = [x for x in re.split(r"[\\/]+", s[len(pre):]) if x]
            return " › ".join([nome] + resto)
    m = re.match(r"^([A-Za-z]):[\\/]*(.*)$", s)
    if m:
        resto = [x for x in re.split(r"[\\/]+", m.group(2)) if x]
        return " › ".join([f"Disco {m.group(1).upper()}"] + resto)
    return Path(s).name


@app.get("/api/info")
def info():
    """Dados pro balão "Quer mudar alguma coisa?" (o caminho só vai no texto copiado pro Claude)."""
    return {"pasta_estudio": str(ROOT)}


@app.get("/api/pastas")
def pastas_get():
    return [{"i": i, "nome": amigavel(f), "existe": Path(f).exists()} for i, f in enumerate(conf()["folders"])]


def _escolher_pasta_dialogo(titulo="Escolha a pasta"):
    code = ("import tkinter as tk;from tkinter import filedialog;r=tk.Tk();r.withdraw();r.attributes('-topmost',True);"
            f"p=filedialog.askdirectory(title={titulo!r});print(p or '')")
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, encoding="utf-8", timeout=600)
    return (r.stdout or "").strip()


@app.post("/api/pastas")
def pastas_post(data: dict = Body(...)):
    """{acao: "adicionar"} abre a janela do Windows pra escolher a pasta; {acao: "remover", i} tira da lista."""
    c = conf()
    fs = list(c["folders"])
    if data.get("acao") == "adicionar":
        p = _escolher_pasta_dialogo("Escolha uma pasta com vídeos")
        if not p:
            return {"ok": False, "msg": "Nenhuma pasta escolhida."}
        p = str(Path(p))
        if p not in fs:
            fs.append(p)
    elif data.get("acao") == "remover":
        i = int(data.get("i", -1))
        if 0 <= i < len(fs):
            fs.pop(i)
    c["folders"] = fs
    CONF.write_text(json.dumps(c, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"ok": True, "pastas": pastas_get()}


# ------------------------------------------------------------------ AJUSTES
_VOZES_EDGE = {}


def _vozes_edge():
    if not _VOZES_EDGE.get("lista"):
        import asyncio
        import edge_tts
        _VOZES_EDGE["lista"] = asyncio.run(edge_tts.list_voices())
    return _VOZES_EDGE["lista"]


QWEN_VOZES = [("sohee", "feminina"), ("serena", "feminina"), ("vivian", "feminina"), ("ono_anna", "feminina"),
              ("aiden", "masculina"), ("dylan", "masculina"), ("eric", "masculina"), ("ryan", "masculina"), ("uncle_fu", "masculina")]


def _ajustes_pub():
    a = AJ.ler()
    from lib import tts as TTS
    return {**a, "pasta_saida_nome": amigavel(a["pasta_saida"]), "pasta_saida": None,
            "idiomas": [{"id": k, "nome": v["nome"]} for k, v in AJ.IDIOMAS.items()],
            "qwen3": TTS.QWEN_PY.exists(), "tem_anthropic": bool(a.get("anthropic_key")), "chaves_ok": {k: bool(str(a.get(k) or "").strip()) for k in AJ.ENV_CHAVES}, **{k: "" for k in AJ.ENV_CHAVES if k not in ("pexels_key", "pixabay_key")}}


def _http_json(url, headers=None, body=None, timeout=20):
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"User-Agent": "EstudioVideos/1.0", **({"Content-Type": "application/json"} if body is not None else {}), **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace") or "{}")


CHAVE_TESTE = {
    "gemini": lambda k: _http_json(f"https://generativelanguage.googleapis.com/v1beta/models?key={urllib.parse.quote(k)}") and "Gemini ok.",
    "fish": lambda k: "Fish Audio ok — crédito: " + str(_http_json("https://api.fish.audio/wallet/self/api-credit", {"Authorization": "Bearer " + k}).get("credit", "conta")),
    "elevenlabs": lambda k: "ElevenLabs ok — " + str(_http_json("https://api.elevenlabs.io/v1/user/subscription", {"xi-api-key": k}).get("tier", "conta")),
    "serper": lambda k: _http_json("https://google.serper.dev/search", {"X-API-KEY": k}, {"q": "teste", "num": 1}) and "Serper ok (busca do Google).",
    "youtube": lambda k: _http_json(f"https://www.googleapis.com/youtube/v3/search?part=id&maxResults=1&q=teste&key={urllib.parse.quote(k)}") and "YouTube ok.",
    "europeana": lambda k: "Europeana ok — " + str(_http_json(f"https://api.europeana.eu/record/v2/search.json?rows=1&query=teste&wskey={urllib.parse.quote(k)}").get("totalResults", 0)) + " resultados de teste.",
    "vimeo": lambda k: "Vimeo ok — " + str(_http_json("https://api.vimeo.com/me", {"Authorization": "bearer " + k}).get("name", "conta")),
    "serpapi": lambda k: "SerpAPI ok — " + str(_http_json(f"https://serpapi.com/account.json?api_key={urllib.parse.quote(k)}").get("plan_searches_left", "?")) + " buscas sobrando.",
    "hf": lambda k: "Hugging Face ok — " + str(_http_json("https://huggingface.co/api/whoami-v2", {"Authorization": "Bearer " + k}).get("name", "conta")),
}


def _testar_chave(item, k):
    try:
        return {"ok": True, "msg": CHAVE_TESTE[item](k)}
    except urllib.error.HTTPError as e:
        return {"ok": False, "msg": f"A chave foi recusada ({e.code}). Confira se copiou inteira."}
    except Exception as e:
        return {"ok": False, "msg": "Não consegui testar agora: " + str(e)[:150]}


@app.get("/api/ajustes")
def ajustes_get():
    return _ajustes_pub()


@app.post("/api/ajustes")
def ajustes_post(data: dict = Body(...)):
    data = {k: v for k, v in (data or {}).items() if k != "pasta_saida"}   # pasta só muda pelo botão "Escolher pasta"
    data = {k: v for k, v in data.items() if not (k in AJ.ENV_CHAVES and k not in ("pexels_key", "pixabay_key") and not str(v or "").strip())}   # chave escondida na tela: vazio = manter
    AJ.salvar(data)
    return _ajustes_pub()


@app.post("/api/ajustes/pasta")
def ajustes_pasta():
    p = _escolher_pasta_dialogo("Onde salvar os vídeos novos?")
    if not p:
        return {"ok": False, "msg": "Nenhuma pasta escolhida.", **_ajustes_pub()}
    AJ.salvar({"pasta_saida": str(Path(p))})
    return {"ok": True, **_ajustes_pub()}


# ===================== ⬇ Downloads do YouTube: proxies (lanes) + login por cookies.txt
# Senha do proxy só fica no proxies.json local; a tela recebe a senha mascarada.
@app.get("/api/proxies")
def proxies_get():
    return RYT.publico()


@app.post("/api/proxies")
def proxies_post(data: dict = Body(...)):
    r = RYT.salvar_lista(data.get("texto", ""))
    return {**r, **RYT.publico()}


@app.post("/api/proxies/testar")
def proxies_testar():
    return {**RYT.testar_todos(), **RYT.publico()}


@app.post("/api/proxies/login")
def proxies_login(data: dict = Body(...)):
    """{lane: 0..N, caminho?} — sem caminho abre a janela do Windows pra escolher o cookies.txt."""
    lane = int(data.get("lane") or 0)
    if data.get("remover"):
        RYT.tirar_login(lane)
        return {"ok": True, **RYT.publico()}
    cam = (data.get("caminho") or "").strip()
    if not cam:
        code = ("import tkinter as tk;from tkinter import filedialog;r=tk.Tk();r.withdraw();r.attributes('-topmost',True);"
                "p=filedialog.askopenfilename(title='Escolha o cookies.txt do YouTube',filetypes=[('cookies','*.txt'),('todos','*.*')]);print(p or '')")
        cam = (subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, encoding="utf-8", timeout=600).stdout or "").strip()
        if not cam:
            return {"ok": False, "msg": "Nenhum arquivo escolhido.", **RYT.publico()}
    try:
        RYT.ligar_login(cam, lane)
    except ValueError as e:
        return {"ok": False, "msg": str(e), **RYT.publico()}
    return {"ok": True, "msg": "Login ligado. Apague o cookies.txt da pasta Downloads (o Estúdio guardou uma cópia).", **RYT.publico()}


# Mantém o PC acordado enquanto houver trabalho na fila (o Windows não dorme no meio de um render/lote).
def _manter_acordado():
    import ctypes
    ES_CONTINUOUS, ES_SYSTEM_REQUIRED = 0x80000000, 0x00000001
    ligado = False
    while True:
        ativo = any(not j.get("done") for j in list(JOBS.values()))
        if ativo != ligado:
            ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | (ES_SYSTEM_REQUIRED if ativo else 0))
            ligado = ativo
        time.sleep(20)


if sys.platform == "win32":
    threading.Thread(target=_manter_acordado, daemon=True).start()


# ===================== 🤖 Piloto automático do canal — fatia (a): rastrear + aprender
# Leitura pública do canal do próprio aluno (yt-dlp, sem login). NUNCA posta nem loga no YouTube.
def job_autopilot(url, prog):
    prog(8, "Lendo os vídeos públicos do seu canal…")
    st = AP.rastrear(url)
    prog(100, "Pronto!")
    s = st.get("stats") or {}
    return {"n": s.get("n", 0), "mediana_vph": s.get("mediana_vph"), "winners": s.get("winners", 0),
            "flops": s.get("flops", 0), "resumo": (st.get("aprendido") or {}).get("resumo", "")}


@app.get("/api/autopilot")
def autopilot_estado():
    """Estado salvo: canal, último rastreio (vídeos classificados), perfil aprendido. Só leitura."""
    return AP.status()


@app.post("/api/autopilot/canal")
def autopilot_canal(data: dict = Body(...)):
    url = str((data or {}).get("url") or "").strip()
    try:
        st = AP.definir_canal(url)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {"ok": True, "canal": st.get("canal", "")}


@app.post("/api/autopilot/rastrear")
def autopilot_rastrear(data: dict = Body(...)):
    """Rastreia agora (trabalho em segundo plano): lê o canal, mede views vs mediana e aprende o que funciona."""
    url = str((data or {}).get("url") or "").strip()
    if url:
        try:
            AP.definir_canal(url)
        except ValueError as e:
            raise HTTPException(400, str(e))
    elif not (AP.status().get("canal")):
        raise HTTPException(400, "Defina o link do seu canal do YouTube primeiro.")
    return start_job(job_autopilot, url or None, tipo="autopilot", titulo="🤖 Rastreando o canal", pesado=False)


# ----- fatia (b): loop de 1 vídeo/dia (feeds → ideia faceless → roteiro → voz → render → pronto)
def _ideia_faceless(titulo_ref, nicho, modelo):
    """Vira o ASSUNTO de um winner num tema faceless NOVO (nunca o título 1:1). Ollama; cai num heurístico se falhar."""
    try:
        from lib import ollama as OL
        d = OL._json_seguro(OL.gerar(
            f'Um vídeo faceless (sem rosto, só narração + imagens) do nicho "{nicho}" bombou com este título:\n'
            f'"{titulo_ref}"\n'
            "Crie uma IDEIA NOVA sobre o MESMO assunto para OUTRO vídeo faceless — NÃO copie o título, mude o ângulo, "
            "nada de nome de canal nem de pessoa.\n"
            'Responda SOMENTE JSON: {"tema": "assunto curto pra roteiro", "titulo": "título chamativo no idioma do original"}',
            modelo, json_mode=True, temperatura=0.8, num_predict=120, timeout=120))
        tema = str(d.get("tema") or "").strip()
        tit = str(d.get("titulo") or "").strip()
        if tema:
            return {"tema": tema, "titulo": tit or tema}
    except Exception:
        pass
    base = re.sub(r"^\s*\d+\s+", "", titulo_ref or "").strip()
    return {"tema": base[:80] or (nicho or "curiosidades"), "titulo": ""}


def _autopilot_estilo_faceless(pedido):
    st = AP.status()
    cand = [e for e in catalogo_estilos() if e.get("tipo") == "fabrica"]
    ids = {e["id"] for e in cand}
    for v in ((pedido or {}).get("estilo"), st.get("estilo")):
        if v in ids:
            return v
    return cand[0]["id"] if cand else "historia-simples"


def job_autopilot_loop(data, prog):
    data = data or {}
    st = AP.status()
    fs = FEEDS.listar()
    if not fs:
        raise RuntimeError("Crie um Feed do seu nicho primeiro (💡 Ideação → Meus Feeds).")
    feed_id = data.get("feed_id") or st.get("feed_id") or fs[0]["id"]
    feed = next((f for f in fs if f["id"] == feed_id), None)
    if not feed:
        raise RuntimeError("Feed não encontrado. Escolha outro no Piloto automático.")
    prog(4, "Vendo o que está bombando no seu nicho…")
    vids = (FEEDS.resultado(feed_id) or {}).get("videos") or []
    if not vids:
        prog(6, "Atualizando o feed…")
        FEEDS.atualizar(feed_id, prog=lambda p, m: prog(6 + p * 0.08, m))
        vids = (FEEDS.resultado(feed_id) or {}).get("videos") or []
    usados = [p.get("titulo_ref") or p.get("tema") for p in st.get("producoes", [])]
    winner = AP.escolher_assunto(vids, usados)
    if not winner:
        raise RuntimeError("Não achei um vídeo em alta nesse feed pra inspirar a ideia de hoje.")
    prog(16, "Criando uma ideia faceless nova (sem copiar o título)…")
    aj = AJ.ler()
    ideia = _ideia_faceless(winner.get("titulo", ""), feed.get("nome") or "", aj["modelo_ollama"])
    plano = AP.plano_do_dia()
    estilo = _autopilot_estilo_faceless(data)
    ped = {"estilo": estilo, "tema": ideia["tema"], "roteiro": "",
           "canal_nome": data.get("canal_nome") or st.get("canal_nome") or aj.get("canal") or "",
           "duracao": float(data.get("duracao") or plano["duracao"]), "voz": st.get("voz") or aj.get("voz") or "",
           "referencia": {}, "formato": "longo", "regras": plano["regras"]}
    prog(22, f"Fazendo o vídeo: {ideia['tema'][:50]}…")
    r = job_fabrica(ped, prog)       # encadeia roteiro → voz → imagens → render no MESMO trabalho
    kit = None
    try:                              # fatia (c): já deixa o kit de publicação pronto junto com o vídeo
        prog(99, "Escrevendo o kit de publicação…")
        kit = kit_publicacao(Path(r["folder"]), prog=lambda p, m: None)
    except Exception:
        kit = None
    AP.registrar_producao({"t": time.time(), "tema": ideia["tema"], "titulo": ideia.get("titulo"),
                           "titulo_ref": winner.get("titulo"), "origem_url": winner.get("url"),
                           "estilo": estilo, "feed": feed.get("nome"), "pid": r.get("pid"),
                           "folder": r.get("folder"), "rendered": r.get("rendered"), "tem_kit": bool(kit)})
    return {**r, "ideia": ideia, "assunto_de": winner.get("titulo"), "feed": feed.get("nome"), "kit": kit}


@app.post("/api/autopilot/config")
def autopilot_config(data: dict = Body(...)):
    """Guarda as escolhas do loop (feed, estilo faceless, voz, nome do canal)."""
    return {"ok": True, **{k: v for k, v in AP.definir_config(data or {}).items() if k in ("feed_id", "estilo", "voz", "canal_nome")}}


@app.post("/api/autopilot/loop")
def autopilot_loop(data: dict = Body(...)):
    """Faz o vídeo de hoje: escolhe um assunto em alta do nicho, cria uma ideia faceless e renderiza. 1/dia (salvo 'forcar')."""
    data = data or {}
    if not data.get("forcar") and AP.ja_feito_hoje():
        raise HTTPException(409, "O vídeo de hoje já foi feito. Marque “fazer mesmo assim” pra fazer outro.")
    return start_job(job_autopilot_loop, data, tipo="autopilot_loop", titulo="🤖 Vídeo do dia", pesado=True)


# ----- fatia (c): kit de publicação (título + variações A/B, descrição, tags, ideia de thumb). O Yuri posta sozinho.
def _ler_txt(p, limite=2000):
    try:
        return p.read_text(encoding="utf-8-sig").strip()[:limite]
    except Exception:
        return ""


def kit_publicacao(proj: Path, prog=None):
    prog = prog or (lambda p, m: None)
    ed = B.load_edit(proj, convert=False) if (proj / "edit.json").exists() else {}
    titulo = _ler_txt(proj / "titulo.txt", 200) or ed.get("name") or proj.name
    roteiro = _ler_txt(proj / "roteiro.txt", 1800)
    aj = AJ.ler()
    idioma = aj.get("idioma") or "pt-BR"
    palavras = ", ".join(w["palavra"] for w in ((AP.status().get("aprendido") or {}).get("palavras_titulo") or [])[:8])
    prog(20, "Escrevendo o kit de publicação…")
    from lib import ollama as OL
    dica = f"\nPalavras que costumam dar views neste canal: {palavras}." if palavras else ""
    prompt = (
        f'Você é especialista em YouTube. Escreva um kit de publicação no idioma {idioma} para o vídeo faceless abaixo.{dica}\n'
        f'Título atual: "{titulo}"\nInício do roteiro: {roteiro[:1200]}\n\n'
        "Responda SOMENTE JSON:\n"
        '{"titulos": ["5 títulos chamativos pra teste A/B, até 70 caracteres, sem clickbait mentiroso"],'
        ' "descricao": "2 a 3 parágrafos; 1ª linha é um gancho; hashtags no fim",'
        ' "tags": ["12 a 18 tags curtas de busca"],'
        ' "thumbnail": {"texto": "3 a 5 palavras BEM grandes pra thumbnail", "ideia": "o que mostrar na imagem"}}')
    try:
        d = OL._json_seguro(OL.gerar(prompt, aj["modelo_ollama"], json_mode=True, temperatura=0.8, num_predict=700, timeout=180))
    except Exception as e:
        raise RuntimeError("A IA não conseguiu escrever o kit: " + str(e)[:200])
    th = d.get("thumbnail") or {}
    kit = {"titulos": [str(t).strip() for t in (d.get("titulos") or []) if str(t).strip()][:6] or [titulo],
           "descricao": str(d.get("descricao") or "").strip(),
           "tags": [str(t).strip() for t in (d.get("tags") or []) if str(t).strip()][:20],
           "thumbnail": {"texto": str(th.get("texto") or "").strip(), "ideia": str(th.get("ideia") or "").strip()},
           "titulo_base": titulo, "criado": datetime.now().isoformat(timespec="seconds")}
    (proj / "kit-publicacao.json").write_text(json.dumps(kit, ensure_ascii=False, indent=1), encoding="utf-8")
    L = [f"# Kit de publicação — {titulo}", "", "## Títulos (teste A/B — o 1º é o principal)"]
    L += [f"{i + 1}. {t}" for i, t in enumerate(kit["titulos"])]
    L += ["", "## Descrição", kit["descricao"], "", "## Tags", ", ".join(kit["tags"]), "",
          "## Thumbnail", f"Texto grande: {kit['thumbnail']['texto']}", f"Ideia: {kit['thumbnail']['ideia']}",
          "", "> Você posta no YouTube. O painel nunca entra na sua conta."]
    (proj / "KIT-PUBLICACAO.md").write_text("\n".join(L), encoding="utf-8")
    prog(100, "Kit pronto!")
    return kit


@app.get("/api/autopilot/kit/{pid}")
def autopilot_kit_ler(pid: str):
    f = path_of(pid) / "kit-publicacao.json"
    if not f.exists():
        return {}
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except Exception:
        return {}


@app.post("/api/autopilot/kit/{pid}")
def autopilot_kit_gerar(pid: str):
    proj = path_of(pid)
    if not (proj / "edit.json").exists():
        raise HTTPException(404, "Projeto não encontrado.")
    return start_job(lambda prog: kit_publicacao(proj, prog), tipo="kit", titulo="📋 Kit de publicação", pesado=False)


# ----- fatia (d): "por que floppou" (views públicas; CSV do Studio enriquece) + import do CSV
@app.post("/api/autopilot/csv")
async def autopilot_csv(file: UploadFile = File(...)):
    """Importa o CSV de 'Conteúdo' do YouTube Studio (impressões, CTR, retenção) pra enriquecer a análise."""
    raw = await file.read()
    for enc in ("utf-8-sig", "utf-16", "latin-1"):
        try:
            texto = raw.decode(enc)
            break
        except Exception:
            texto = None
    if not texto:
        raise HTTPException(400, "Não consegui ler o arquivo. Exporte o CSV da tabela 'Conteúdo' do YouTube Studio.")
    try:
        r = AP.importar_csv(texto)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {"ok": True, **r}


def _porque_floppou(video, prog=None):
    prog = prog or (lambda p, m: None)
    sinais = AP.sinais_flop(video)
    aj = AJ.ler()
    prog(30, "Analisando com a IA…")
    from lib import ollama as OL
    pedido = (
        "Você é um analista honesto de YouTube. Com os números abaixo de UM vídeo do canal, diga SEM "
        "suavizar por que ele foi bem ou mal, comparando com o que funciona no nicho. Se não houver dados "
        "do YouTube Studio (CSV), deixe claro que a análise usa só VIEWS PÚBLICAS e que impressões/CTR/"
        "retenção dariam certeza.\n"
        f"Sinais (JSON): {json.dumps(sinais, ensure_ascii=False)}\n"
        f"Idioma da resposta: {aj.get('idioma') or 'pt-BR'}.\n"
        'Responda SOMENTE JSON: {"veredito": "1 frase direta", "motivos": ["2 a 4 motivos concretos"], '
        '"o_que_mudar": ["2 a 4 ações pro próximo vídeo"]}')
    out = {"veredito": "", "motivos": [], "o_que_mudar": []}
    try:
        d = OL._json_seguro(OL.gerar(pedido, aj["modelo_ollama"], json_mode=True, temperatura=0.5, num_predict=500, timeout=150))
        out = {"veredito": str(d.get("veredito") or "").strip(),
               "motivos": [str(x).strip() for x in (d.get("motivos") or []) if str(x).strip()][:5],
               "o_que_mudar": [str(x).strip() for x in (d.get("o_que_mudar") or []) if str(x).strip()][:5]}
    except Exception:
        pass
    if not out["veredito"]:
        out["veredito"] = ("Sem análise da IA agora — veja os números." if sinais.get("tem_csv")
                           else "Sem análise da IA agora. Só com views públicas: compare a razão vs mediana acima.")
    return {**out, "sinais": sinais, "tem_csv": sinais.get("tem_csv", False)}


@app.post("/api/autopilot/flop")
def autopilot_flop(data: dict = Body(...)):
    """Por que o vídeo (da tabela do rastreio) foi bem/mal. Sem CSV = só views públicas."""
    vid = str((data or {}).get("id") or "").strip()
    st = AP.status()
    video = next((v for v in (st.get("videos") or []) if v.get("id") == vid), None)
    if not video:
        raise HTTPException(404, "Vídeo não está no último rastreio. Rastreie o canal de novo.")
    return start_job(lambda prog: _porque_floppou(video, prog), tipo="flop", titulo="🔍 Por que foi assim", pesado=False)


@app.get("/api/ajustes/modelos")
def ajustes_modelos():
    try:
        with urllib.request.urlopen(__import__("lib.ollama", fromlist=["x"]).base() + "/api/tags", timeout=5) as r:
            ms = json.load(r).get("models", [])
        return [{"nome": m["name"], "gb": round((m.get("size") or 0) / 1e9, 1), "nuvem": ":cloud" in m["name"]} for m in ms]
    except Exception:
        return []


_FISH_VOZES = {"t": 0, "v": []}


def _vozes_fish():
    from lib import tts as TTS
    k = TTS.fish_chave()
    if not k:
        return []
    if time.time() - _FISH_VOZES["t"] < 300 and _FISH_VOZES["v"]:
        return _FISH_VOZES["v"]
    v = []
    vistos = set()
    for vid in AJ.ler().get("fish_vozes") or []:   # suas favoritas fixas no topo
        try:
            m = _http_json(f"{TTS.FISH_URL}/model/{vid}", {"Authorization": "Bearer " + k})
            v.append({"id": "fish:" + vid, "nome": str(m.get("title") or vid)[:60] + " ⭐", "grupo": "Fish Audio (suas vozes)"})
            vistos.add(vid)
        except Exception:
            v.append({"id": "fish:" + vid, "nome": vid[:8] + "… (favorita)", "grupo": "Fish Audio (suas vozes)"})
            vistos.add(vid)
    for q in ("self=true", "language=pt&title=&sort_by=score"):   # 1º: as suas (criadas/clonadas); 2º: as mais usadas da biblioteca
        try:
            j = _http_json(f"{TTS.FISH_URL}/model?page_size=40&page_number=1&{q}", {"Authorization": "Bearer " + k})
        except Exception:
            continue
        for m in j.get("items", []):
            if m.get("_id") and m["_id"] not in vistos and m.get("type", "tts") == "tts":
                vistos.add(m["_id"])
                v.append({"id": "fish:" + m["_id"], "nome": str(m.get("title") or m["_id"])[:60],
                          "grupo": "Fish Audio (suas vozes)" if q == "self=true" else "Fish Audio (biblioteca)"})
    _FISH_VOZES.update(t=time.time(), v=v)
    return v


@app.get("/api/ajustes/vozes")
def ajustes_vozes(idioma: str = "pt-BR"):
    out = [{"id": "auto", "nome": "Automática (a melhor que funcionar no seu PC)", "grupo": "Automática"}]
    try:
        for v in _vozes_edge():
            if v.get("Locale", "").lower() == idioma.lower():
                if v["ShortName"] in ("pt-BR-AntonioNeural", "pt-BR-FranciscaNeural"):   # robóticas: proibidas (07/11)
                    continue
                nome = re.sub(r"^.*-([A-Za-z]+?)(Multilingual)?Neural$", r"\1", v["ShortName"])
                out.append({"id": "edge:" + v["ShortName"], "grupo": "Microsoft (grátis, internet)",
                            "nome": f"{nome} ({'feminina' if v.get('Gender') == 'Female' else 'masculina'})"})
    except Exception:
        out += [{"id": "edge:pt-BR-ThalitaMultilingualNeural", "nome": "Thalita (feminina)", "grupo": "Microsoft (grátis, internet)"}]
    from lib import tts as TTS
    try:   # vozes do Fish Audio (as suas e as favoritas): só aparecem com a chave colocada em Ajustes
        out += _vozes_fish()
    except Exception:
        pass
    if TTS.QWEN_PY.exists():
        out += [{"id": f"qwen3:{n}", "nome": f"{n} ({g}, sotaque estrangeiro)", "grupo": "Qwen3 (no seu PC, mais lenta)"} for n, g in QWEN_VOZES]
    try:   # VoiceStudio em outro PC (Ajustes → Vozes extras): vozes pela placa de vídeo de lá
        if TTS.vs_remoto_url():
            g = "VoiceStudio no outro PC (placa de vídeo)"
            nomes = {"fem": "Feminina jovem", "fem-calma": "Feminina madura, grave", "masc": "Masculina jovem", "masc-grave": "Masculina madura, grave",
                     "sombrio": "Narrador sombrio (idoso, muito grave)", "sussurro": "Narrador sussurrado (idoso, muito grave)",
                     "grave": "Narrador grave (maduro, muito grave)", "idosa": "Mulher idosa, grave"}
            out += [{"id": "vsremoto:" + k, "nome": v + " (voz criada)", "grupo": g} for k, v in nomes.items()]
            try:
                with urllib.request.urlopen(TTS.vs_remoto_url() + "/profiles", timeout=3) as r:
                    out += [{"id": "vsremoto:perfil_" + str(x["id"]), "nome": str(x.get("name") or x["id"])[:50] + " (salva lá)", "grupo": g}
                            for x in json.load(r) if x.get("id") and re.fullmatch(r"[\w-]+", str(x["id"]))]
            except Exception:
                pass
    except Exception:
        pass
    try:   # vozes clonadas na aba 🎙 Minhas vozes → aparecem em toda lista de voz (Vídeo com imagens, Shorts, Roteiro, Ajustes)
        from lib import vozes as _VZ
        out += [{"id": "clone:" + v["id"], "nome": v["nome"] + (" (VoiceStudio)" if v.get("origem") == "VoiceStudio" else ""),
                 "grupo": "🎙 Minhas vozes (clonadas, no seu PC)"} for v in _VZ.clones()
                if not str(v.get("nome", "")).lower().startswith("teste") or AJ.ler().get("voz") == "clone:" + v["id"]]   # vozes de teste: só na aba Minhas vozes
    except Exception:
        pass
    return out


FRASE_TESTE = {"pt-BR": "Olá! Esta é a voz que vai narrar os seus vídeos.", "en-US": "Hi! This is the voice that will narrate your videos.",
               "es-MX": "¡Hola! Esta es la voz que va a narrar tus videos."}


@app.post("/api/ajustes/testar")
def ajustes_testar(data: dict = Body(...)):
    item = data.get("item")
    a = AJ.ler()
    t0 = time.time()
    try:
        if item == "ollama":
            modelo = data.get("valor") or a["modelo_ollama"]
            from lib import ollama as OL
            r = OL.gerar("Responda só com a palavra OK.", modelo, temperatura=0, num_predict=5, timeout=180).strip()
            return {"ok": bool(r), "msg": f"A IA respondeu “{r[:30]}” em {time.time() - t0:.0f} s ({modelo})."}
        if item == "ollama_url":
            u = str(data.get("valor") or "").strip().rstrip("/")
            if u and not re.match(r"^https?://[^\s/]+(:\d+)?$", u):
                return {"ok": False, "msg": "Escreva o endereço, ex.: http://100.107.205.27:11434 (ou deixe vazio para usar o Ollama deste PC)."}
            try:
                with urllib.request.urlopen((u or "http://127.0.0.1:11434") + "/api/tags", timeout=6) as r:
                    nomes = [m["name"] for m in json.load(r).get("models", [])]
            except Exception:
                return {"ok": False, "msg": "Não respondeu. Veja se o outro PC está ligado, com o Tailscale e o Ollama abertos, e se rodou o comando tailscale serve da porta 11434."}
            return {"ok": True, "msg": f"Conectado. Modelos lá: {', '.join(nomes) or 'nenhum ainda'}. Clique em Salvar ajustes."}
        if item == "vsremoto":
            u = str(data.get("valor") or a.get("vs_remoto_url") or "").strip().rstrip("/")
            if not re.match(r"^https?://[^\s/]+(:\d+)?$", u):
                return {"ok": False, "msg": "Escreva o endereço, ex.: http://100.107.205.27:3900 (começa com http:// e termina na porta)."}
            try:
                with urllib.request.urlopen(u + "/health", timeout=6) as r:
                    h = json.load(r)
            except Exception:
                return {"ok": False, "msg": "Não respondeu. Veja se o outro PC está ligado, com o Tailscale e o VoiceStudio abertos."}
            dev = str(h.get("device") or "?")
            return {"ok": True, "msg": f"Conectado ({dev}). Clique em Salvar ajustes." + ("" if "cuda" in dev else " ⚠ Não está usando a placa NVIDIA (ficará lento).")}
        if item == "voz":
            voz = data.get("valor") or a["voz"]
            ja = _previa_arq(voz, a["idioma"])
            if not ja:
                _previa_gerar(voz, a["idioma"])
            return {"ok": True, "msg": "Prévia da voz:" if ja else f"Voz pronta ({time.time() - t0:.0f} s):",
                    "audio": "/api/vozes/previa?" + urllib.parse.urlencode({"voz": voz, "i": a["idioma"], "t": int(time.time())})}
        if item == "pasta":
            d = Path(a["pasta_saida"])
            d.mkdir(parents=True, exist_ok=True)
            tf = d / ".teste-estudio"
            tf.write_text("ok", encoding="utf-8")
            tf.unlink()
            livre = shutil.disk_usage(d).free / 1e9
            return {"ok": True, "msg": f"Pasta ok: dá pra salvar ({livre:.0f} GB livres no disco)."}
        if item in ("pexels", "pixabay"):
            k = (data.get("valor") or a.get(f"{item}_key") or "").strip()
            if not k:
                return {"ok": None, "msg": "Sem chave ainda. Funciona sem ela (só com fotos do Wikimedia), mas com a chave grátis vêm muito mais fotos e clipes: clique em “Pegar chave grátis”, cole aqui e Salve."}
            c = (BANCOS.pexels_fotos if item == "pexels" else BANCOS.pixabay_fotos)("coffee", k, n=3)
            return {"ok": bool(c), "msg": f"Chave ok: achou {len(c)} fotos de teste." if c else "A chave respondeu, mas sem fotos."}
        if item in CHAVE_TESTE:
            k = (data.get("valor") or a.get(item + ("_token" if item in ("vimeo", "hf") else "_key")) or "").strip()
            if not k:
                return {"ok": None, "msg": "Sem chave ainda. Clique em “Pegar chave grátis”, crie a sua e cole aqui."}
            return _testar_chave(item, k)
        if item == "anthropic":
            k = (data.get("valor") or a.get("anthropic_key") or "").strip()
            if not k:
                return {"ok": None, "msg": "Sem chave — tudo bem, é opcional. Sem ela, o botão do Claude só copia o pedido pra você colar no chat."}
            from lib import claude_rev
            e = claude_rev.estimar(k, "teste", 1)
            return {"ok": True, "msg": f"Chave ok ({claude_rev.MODELO}). Teste de contagem: {e['tokens_entrada']} tokens."}
        if item == "idioma":
            cod = data.get("valor") or a["idioma"]
            n = sum(1 for v in _vozes_edge() if v.get("Locale", "").lower() == cod.lower())
            return {"ok": n > 0, "msg": f"{AJ.IDIOMAS.get(cod, {}).get('nome', cod)}: {n} vozes Microsoft disponíveis; roteiros e buscas saem nesse idioma."}
    except Exception as e:
        if re.search(r"HTTP Error (400|401|403)\b", str(e)):   # QA: novato não entende "401 Unauthorized"
            return {"ok": False, "msg": "Chave recusada pelo site. Confira se copiou a chave inteira (sem espaço no começo/fim) e se ela está ativa. (" + str(e)[-60:] + ")"}
        return {"ok": False, "msg": "Não funcionou: " + str(e)[-300:]}
    raise HTTPException(400, "item desconhecido")


PREVIAS = ROOT / "previas_vozes"   # pasta normal (vai no pacote): prévia pronta de cada voz, sem gerar de novo


def _previa_arq(voz, idioma):
    """Prévia já pronta: clone usa o teste.wav dele; as outras ficam em .cache/previas/<voz>-<idioma>/voz.*"""
    if voz.startswith("clone:"):
        f = ROOT / "vozes" / Path(voz[6:]).name / "teste.wav"
        if f.exists():
            return f
    d = PREVIAS / slug(f"{voz}-{idioma}", 80)
    return next((x for x in (d / "voz.mp3", d / "voz.wav") if x.exists()), None)


def _previa_gerar(voz, idioma):
    from lib import tts as TTS
    motor, _, nome = voz.partition(":")
    d = PREVIAS / slug(f"{voz}-{idioma}", 80)
    d.mkdir(parents=True, exist_ok=True)
    TTS.falar(FRASE_TESTE.get(idioma, FRASE_TESTE["pt-BR"]), d, motor or "auto", nome or None)
    return _previa_arq(voz, idioma)


@app.get("/api/vozes/previa")
def vozes_previa(voz: str, i: str = "pt-BR"):
    f = _previa_arq(voz, i)
    if not f:
        raise HTTPException(404)
    return FileResponse(f, headers={"Cache-Control": "no-store"})


def _previas_fundo():
    """Ao ligar: deixa prontas as prévias das vozes grátis (Microsoft) do idioma escolhido — 1 por vez, sem pressa."""
    time.sleep(20)
    try:
        idi = AJ.ler()["idioma"]
        ids = [v["id"] for v in ajustes_vozes(idi) if v.get("id") and ":" in v["id"]]
        ordem = sorted(ids, key=lambda i: (not i.startswith("edge:"), not i.startswith("clone:")))   # rápidas primeiro, Qwen3 por último
        for voz in ordem:
            if not _previa_arq(voz, idi):
                try:
                    _previa_gerar(voz, idi)
                except Exception:
                    pass
    except Exception:
        traceback.print_exc()


threading.Thread(target=_previas_fundo, daemon=True).start()


@app.get("/api/ajustes/audio-teste")
def ajustes_audio_teste():
    d = CACHE_DIR / "teste-voz"
    f = next((x for x in (d / "voz.mp3", d / "voz.wav") if x.exists()), None)
    if not f:
        raise HTTPException(404)
    return FileResponse(f, headers={"Cache-Control": "no-store"})


# ------------------------------------------------------------------ VÍDEO COM IMAGENS
DESC_VI = {
    "broll-documentario": "Fotos e clipes reais de bancos livres com zoom lento, legenda palavra por palavra, título e cartão do canal.",
}


def _cfg_estilo(nome):
    try:
        return json.loads((ESTILOS_FAB / nome / "estilo.json").read_text(encoding="utf-8-sig"))
    except Exception:
        return {}


# ---- aulas 07/11: quantas vezes cada estilo já virou vídeo/amostra (estilo "novo" = 0 → amostra primeiro)
def _desc_estilo(cfg):
    """Estilo copiado antigo tinha 'Aproximado de uma referência: 19.3 cortes/min…' → frase simples."""
    d = cfg.get("descricao") or ""
    if cfg.get("aproximado") and d.startswith("Aproximado de uma refer"):
        try:
            from lib.texto import descricao_estilo_copiado
            return descricao_estilo_copiado({**(cfg.get("analise") or {}), "formato": cfg.get("formato")})
        except Exception:
            return "Copiado de um vídeo: mesmo ritmo de cortes, cores e legenda."
    return d


def _usos_estilo():
    def calc():
        n = {}
        amos = CACHE_DIR / "amostras"
        try:
            pastas = [d for d in out_dir().iterdir() if d.is_dir()]
        except Exception:
            pastas = []
        for d in pastas:
            pj = d / "pedido.json"
            if not pj.exists():
                continue
            if not ((d / "final.mp4").exists() or (amos / d.name / "final.mp4").exists()):
                continue
            try:
                e = json.loads(pj.read_text(encoding="utf-8-sig")).get("estilo") or ""
            except Exception:
                continue
            if e:
                n[e] = n.get(e, 0) + 1
        return n
    return memo("usos_estilo", calc, ttl=30)


COMECE_F = ROOT / "comece.json"   # estado do cartão "Comece aqui" (só deste PC; fora do pacote)


def _comece_ler():
    try:
        return json.loads(COMECE_F.read_text(encoding="utf-8"))
    except Exception:
        return {}


@app.get("/api/comece")
def comece_get():
    """Checklist do 1º dia: marca sozinho olhando o que já existe no PC."""
    st = _comece_ler()
    try:
        sd = saude()
    except Exception:
        sd = {}
    pc_ok = bool(sd.get("ollama") and sd.get("modelo_ok") and sd.get("voz") and sd.get("ffmpeg"))
    amos = CACHE_DIR / "amostras"
    amostra = amos.exists() and any((d / "final.mp4").exists() for d in amos.iterdir() if d.is_dir())
    try:
        copiado = any(e.get("aproximado") for e in _estilos_meus())
    except Exception:
        copiado = False
    passos = [{"id": "ajustes", "ok": bool(st.get("ajustes_testado") or pc_ok)},
              {"id": "amostra", "ok": bool(amostra or st.get("amostra"))},
              {"id": "video", "ok": bool(sd.get("videos_feitos"))},
              {"id": "copiado", "ok": bool(copiado)}]
    return {"passos": passos, "escondido": bool(st.get("escondido")), "pc_ok": pc_ok}


@app.post("/api/comece")
def comece_set(data: dict = Body(...)):
    st = _comece_ler()
    for k in ("escondido", "ajustes_testado"):
        if k in data:
            st[k] = bool(data[k])
    COMECE_F.write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding="utf-8")
    return comece_get()


@app.get("/api/revisar/{pid}")
def revisar(pid: str):
    """Relatório honesto do vídeo pronto: imagens marcadas ⚠ que ficaram, créditos a pôr na descrição."""
    p = _decode_pid(pid)
    if not p.is_dir():
        raise HTTPException(404, "Vídeo não encontrado.")
    out = {"tem_cenas": (p / "cenas.json").exists(), "fracas": [], "cenas": 0, "checagem": None,
           "creditos": 0, "pedem_credito": 0, "creditos_txt": "", "pronto": bool(find_video(p))}
    if out["tem_cenas"]:
        try:
            cj = _vi_ler(p)
            cenas = cj.get("cenas") or []
            out["cenas"] = len(cenas)
            out["fracas"] = [i + 1 for i, c in enumerate(cenas) if (c.get("escolha") or {}).get("fraca")]
            out["checagem"] = cj.get("checagem")
        except Exception:
            pass
    cf = p / "CREDITOS.txt"
    if cf.exists():
        t = cf.read_text(encoding="utf-8", errors="replace")
        linhas = [l for l in t.splitlines() if l.strip().startswith("•")]
        out["creditos"] = len(linhas)
        out["pedem_credito"] = sum(1 for l in linhas if re.search(r"\bBY\b", l))
        out["creditos_txt"] = t[:8000]
    return out


@app.get("/api/novidades")
def novidades():
    """O que mudou nesta versão do painel (NOVIDADES.json vai no pacote)."""
    try:
        return json.loads((ROOT / "NOVIDADES.json").read_text(encoding="utf-8-sig"))
    except Exception:
        return {"versao": "", "itens": []}


@app.get("/api/vi/estilos")
def vi_estilos(formato: str = "longo"):
    """Estilos do Vídeo com imagens (formato=longo, 16:9) ou da Fábrica de Shorts (formato=short, 9:16)."""
    thumbs = {e["id"]: e for e in estilos() if e.get("tipo") == "fabrica"}   # leve 01/11: usa o catálogo em cache (antes refazia a varredura toda: ~100 ms por chamada)
    out = []
    primeiro = "short-documentario" if formato == "short" else "broll-documentario"
    usos = _usos_estilo()
    for d in sorted(ESTILOS_FAB.iterdir(), key=lambda d: (d.name != primeiro, d.name)):
        cfg = _cfg_estilo(d.name)
        if not (d / "preencher.py").exists() or cfg.get("imagens") != "wikimedia":
            continue
        if bool(cfg.get("vertical")) != (formato == "short"):
            continue
        ex = thumbs.get(d.name, {})
        nome = re.sub(r"\s*\(.*\)\s*$", "", cfg.get("nome") or d.name)
        capa = next((f for f in (d / "capa.jpg", d / "capa.png") if f.exists()), None)
        out.append({"id": d.name, "nome": nome, "descricao": _desc_estilo(cfg) or DESC_VI.get(d.name) or DESC_FAB.get(d.name, ""),
                    "thumb_url": ex.get("thumb_url") or (f"/api/estilo-capa/{d.name}?v={int(capa.stat().st_mtime)}" if capa else None),
                    "video_url": ex.get("video_url"), "clipes": bool(cfg.get("clipes")),
                    "novo": d.name == primeiro, "aproximado": bool(cfg.get("aproximado")), "extra": bool(cfg.get("extra_de")),
                    "bom_para": cfg.get("bom_para") or [], "palavras": cfg.get("palavras_tema") or [], "usado": usos.get(d.name, 0)})
    return out


@app.get("/api/estilo-capa/{eid}")
def estilo_capa(eid: str):
    d = ESTILOS_FAB / Path(eid).name
    f = next((x for x in (d / "capa.jpg", d / "capa.png") if x.exists()), None)
    if not f:
        raise HTTPException(404)
    return FileResponse(f, headers={"Cache-Control": "no-store"})


@app.post("/api/vi/audio")
async def vi_audio(file: UploadFile = File(...)):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in (".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac"):
        raise HTTPException(400, "Envie um áudio mp3, wav ou m4a.")
    PEDIDOS_TMP.mkdir(exist_ok=True)
    dst = PEDIDOS_TMP / f"audio-{time.strftime('%Y%m%d-%H%M%S')}{ext}"
    with open(dst, "wb") as fh:
        while True:
            ch = await file.read(1 << 20)
            if not ch:
                break
            fh.write(ch)
    dur = probe(dst)
    if not dur:
        dst.unlink(missing_ok=True)
        raise HTTPException(400, "Não consegui ler esse áudio.")
    return {"audio_id": dst.name, "dur": dur}


def job_vi(proj: Path, conferir: bool, prog):
    py = [sys.executable, FABRICA / "video_imagens.py"]
    if not (proj / "cenas.json").exists() or json.loads((proj / "cenas.json").read_text(encoding="utf-8")).get("estado") is None:
        rodar_proc(py + ["preparar", "--pasta", proj], prog, cwd=FABRICA, lo=0, hi=100 if conferir else 55)
    pid = pid_of(proj)
    if conferir:
        return {"pid": pid, "folder": str(proj), "name": proj.name, "conferir": True, "rendered": False}
    rodar_proc(py + ["montar", "--pasta", proj], prog, cwd=FABRICA, lo=55, hi=100, render=(12, 98))
    return _vi_resultado(proj)


def job_vi_montar(proj: Path, prog):
    rodar_proc([sys.executable, FABRICA / "video_imagens.py", "montar", "--pasta", proj], prog, cwd=FABRICA, render=(12, 98))
    return _vi_resultado(proj)


def _vi_resultado(proj):
    ed = B.load_edit(proj, convert=False)
    vid = find_video(proj)
    rel = {}
    try:
        rel = json.loads((proj / "RELATORIO.json").read_text(encoding="utf-8"))
    except Exception:
        pass
    return {"pid": pid_of(proj), "folder": str(proj), "name": ed.get("name") or proj.name, "rendered": bool(vid), "conferir": False,
            "minutos": rel.get("minutos"), "duracao": rel.get("duracao_video"), "tokens": 0}


@app.post("/api/vi/criar")
def vi_criar(data: dict = Body(...)):
    g = lambda k: str(data.get(k) or "").strip()
    modo, estilo = g("modo") or "tema", g("estilo") or "broll-documentario"
    if not (ESTILOS_FAB / estilo / "preencher.py").exists():
        raise HTTPException(400, "Escolha um estilo.")
    if modo == "tema" and not g("tema"):
        raise HTTPException(400, "Escreva o tema do vídeo.")
    if modo == "roteiro" and len(g("roteiro").split()) < 15:
        raise HTTPException(400, "Cole o roteiro (pelo menos algumas frases).")
    audio = None
    if modo == "audio":
        a = PEDIDOS_TMP / Path(g("audio_id")).name
        if not g("audio_id") or not a.exists():
            raise HTTPException(400, "Envie o arquivo de áudio da narração.")
        audio = str(a)
    try:
        dur = float(data.get("duracao") or 60)
    except Exception:
        dur = 60
    if not 15 <= dur <= 10800:
        raise HTTPException(400, "Duração precisa ficar entre 15 segundos e 3 horas.")
    aj = AJ.ler()
    OUT = out_dir()
    nn = proximo_numero(OUT)
    cfg_e = _cfg_estilo(estilo)
    short = bool(cfg_e.get("vertical")) or (bool(cfg_e.get("formato_livre")) and g("formato") == "9:16")
    if short and modo == "tema" and not 20 <= dur <= 90:
        raise HTTPException(400, "Short precisa ter entre 20 e 90 segundos.")
    base = g("titulo") or g("tema") or (g("roteiro").split(".")[0] if modo in ("roteiro", "audio") and g("roteiro") else "narracao")
    pref = "stickman" if estilo == "stickman" else ("short" if short else "imagens")
    proj = OUT / f"{nn:02d}-{pref}-{slug(base, 34) or 'video'}"
    proj.mkdir(parents=True, exist_ok=True)
    _gravar_marca(proj, g("marca"))
    ped = {"modo": modo, "tema": g("tema"), "roteiro": g("roteiro") if modo == "roteiro" else "", "audio": audio, "estilo": estilo,
           "roteiro_ref": g("roteiro") if modo == "audio" else "",
           "duracao": dur, "voz": g("voz") or aj["voz"], "canal": g("canal"), "titulo": g("titulo"), "modelo": aj["modelo_ollama"],
           "idioma": aj["idioma"], "conferir": bool(data.get("conferir", True)) and not cfg_e.get("sem_imagens"),
           "formato": "9:16" if short else "16:9", "criado": datetime.now().isoformat(timespec="seconds"),
           "extras_tela": {"numeros": data.get("numeros") is not False, "credito": data.get("credito") is not False}}
    (proj / "pedido.json").write_text(json.dumps(ped, ensure_ascii=False, indent=1), encoding="utf-8")
    titulo = base[:70] + f" · {estilo}"
    r = start_job(job_vi, proj, ped["conferir"], tipo="stickman" if estilo == "stickman" else ("short" if short else "video_imagens"),
                  titulo=titulo, pesado=True, pid=pid_of(proj))
    return {**r, "pid": pid_of(proj)}


@app.post("/api/vi/roteiro")
def vi_so_roteiro(data: dict = Body(...)):
    """“Gerar a voz em outra IA”: a IA do PC escreve só o roteiro (sem voz, sem imagens) pra copiar e levar pro Dark Planner/ElevenLabs."""
    g = lambda k: str(data.get(k) or "").strip()
    estilo = g("estilo") or "broll-documentario"
    if not (ESTILOS_FAB / estilo / "preencher.py").exists():
        estilo = "broll-documentario"
    if not g("tema"):
        raise HTTPException(400, "Escreva o tema do vídeo.")
    try:
        dur = max(15.0, min(10800.0, float(data.get("duracao") or 60)))
    except Exception:
        dur = 60.0
    aj = AJ.ler()
    proj = PEDIDOS_TMP / f"roteiro-{uuid.uuid4().hex[:8]}"
    proj.mkdir(parents=True, exist_ok=True)
    ped = {"modo": "tema", "tema": g("tema"), "estilo": estilo, "duracao": dur, "canal": g("canal"), "titulo": g("titulo"),
           "modelo": aj["modelo_ollama"], "idioma": aj["idioma"], "so_roteiro": True}
    (proj / "pedido.json").write_text(json.dumps(ped, ensure_ascii=False, indent=1), encoding="utf-8")

    def job(prog):
        rodar_proc([sys.executable, FABRICA / "video_imagens.py", "roteiro", "--pasta", proj], prog, cwd=FABRICA)
        rd = lambda n: (proj / n).read_text(encoding="utf-8").strip() if (proj / n).exists() else ""
        if not rd("roteiro.txt"):
            raise RuntimeError("A IA do PC não devolveu o roteiro. Tente de novo.")
        fonte = {}
        try:
            f = json.loads(rd("fontes.json") or "{}")
            fonte = {"titulo": f.get("titulo"), "url": f.get("url")} if f.get("url") else {}
        except Exception:
            pass
        return {"roteiro": rd("roteiro.txt"), "titulo": rd("titulo.txt"), "fonte_fatos": fonte}
    return start_job(job, tipo="roteiro", titulo="Roteiro (só texto) · " + g("tema")[:50], pesado=True)


def _vi_proj(pid: str) -> Path:
    p = _decode_pid(pid)
    if not (p / "cenas.json").exists():
        raise HTTPException(404, "As imagens desse vídeo ainda não foram buscadas.")
    return p


def _vi_ler(p):
    return json.loads((p / "cenas.json").read_text(encoding="utf-8"))


def _vi_gravar(p, cj):
    (p / "cenas.json").write_text(json.dumps(cj, ensure_ascii=False, indent=1), encoding="utf-8")


@app.get("/api/vi/{pid}")
def vi_get(pid: str):
    p = _vi_proj(pid)
    cj = _vi_ler(p)
    ped = json.loads((p / "pedido.json").read_text(encoding="utf-8")) if (p / "pedido.json").exists() else {}
    for c in cj["cenas"]:
        e = c.get("escolha") or {}
        if e.get("src"):
            e["url_local"] = f"/p/{pid}/{e['src']}"
    return {"pid": pid, "titulo": cj.get("titulo"), "estado": cj.get("estado"), "estilo": cj.get("estilo"),
            "estilo_nome": (str(_cfg_estilo(cj.get("estilo") or "").get("nome") or "").split(" (")[0] or cj.get("estilo")), "permite_video": cj.get("permite_video"),
            "vertical": bool(cj.get("vertical")), "amostra": (CACHE_DIR / "amostras" / p.name / "final.mp4").exists(),
            "canal": ped.get("canal"), "cenas": cj["cenas"], "checagem": cj.get("checagem"),
            "estilo_usado": _usos_estilo().get(cj.get("estilo") or ped.get("estilo") or "", 0),
            "pedido": {k: ped.get(k) for k in ("modo", "tema", "roteiro", "titulo", "duracao", "voz")},
            "tem_chaves": bool(AJ.ler().get("pexels_key") or AJ.ler().get("pixabay_key"))}


def _vi_escolher(p, cj, i, cand, prog_src=None):
    c = cj["cenas"][i]
    src = prog_src or BANCOS.baixar(cand, p, i, c["e"] - c["s"], vertical=bool(cj.get("vertical")), limpar=False)
    if c.get("escolha") and not _vi_escolher.desfazendo:   # guarda a anterior pro "↩ Desfazer"
        c["antes"] = ((c.get("antes") or []) + [{k: v for k, v in c["escolha"].items() if k != "url_local"}])[-6:]
    c["escolha"] = {**{k: cand.get(k) for k in ("tipo", "fonte", "titulo", "licenca", "pagina", "url", "thumb")}, "src": src}
    # cenas seguintes que só repetiam esta imagem continuam repetindo a nova
    for k in range(i + 1, len(cj["cenas"])):
        e = cj["cenas"][k].get("escolha") or {}
        if not e.get("repetida"):
            break
        cj["cenas"][k]["escolha"] = {**c["escolha"], "repetida": True}
    _vi_gravar(p, cj)
    pid = pid_of(p)
    for x in cj["cenas"]:
        e = x.get("escolha") or {}
        if e.get("src"):
            e["url_local"] = f"/p/{pid}/{e['src']}"
    return cj["cenas"]


@app.post("/api/vi/{pid}/escolher")
def vi_escolher(pid: str, data: dict = Body(...)):
    p = _vi_proj(pid)
    cj = _vi_ler(p)
    i, ci = int(data["i"]), int(data["c"])
    cand = cj["cenas"][i]["candidatos"][ci]
    try:
        return {"cenas": _vi_escolher(p, cj, i, cand)}
    except Exception as e:
        raise HTTPException(502, "Não consegui baixar essa opção: " + str(e)[:160])


@app.post("/api/vi/{pid}/buscar")
def vi_buscar(pid: str, data: dict = Body(...)):
    p = _vi_proj(pid)
    cj = _vi_ler(p)
    i, q = int(data["i"]), str(data.get("q") or "").strip()
    if not q:
        raise HTTPException(400, "Escreva uma palavra pra buscar.")
    aj = AJ.ler()
    q_en = BANCOS.traduzir_busca(q, aj["modelo_ollama"])
    cfg = _cfg_estilo(cj.get("estilo") or "")
    chaves = {"pexels": aj.get("pexels_key"), "pixabay": aj.get("pixabay_key")}
    cands = BANCOS.candidatos(q_en, chaves, videos=bool(cfg.get("clipes")), preferir=cfg.get("preferir_titulo", []),
                              vertical=bool(cj.get("vertical")))
    if q_en != q:
        cands += [c for c in BANCOS.candidatos(q, {}, preferir=cfg.get("preferir_titulo", [])) if c["url"] not in {x["url"] for x in cands}][:4]
    if not cands:
        return {"ok": False, "msg": f"Nada encontrado para “{q}”. Tente outra palavra (de preferência coisa concreta: lugar, objeto, pessoa)."}
    try:   # o que mais bate com a busca primeiro (texto + CLIP)
        BANCOS.relevancia.avaliar(cands, q_en)
        cands.sort(key=lambda x: -x.get("relev", -99))
    except Exception:
        pass
    c = cj["cenas"][i]
    c["candidatos"], c["query"] = cands, q_en
    _vi_gravar(p, cj)
    return {"ok": True, "cena": c, "busca": q_en}


@app.post("/api/vi/{pid}/subir/{i}")
async def vi_subir(pid: str, i: int, file: UploadFile = File(...)):
    p = _vi_proj(pid)
    cj = _vi_ler(p)
    ext = Path(file.filename or "").suffix.lower()
    video = ext in (".mp4", ".mov", ".webm", ".mkv")
    if ext not in (".jpg", ".jpeg", ".png", ".webp") and not video:
        raise HTTPException(400, "Envie uma foto (jpg/png/webp) ou um vídeo (mp4/mov).")
    if video and not cj.get("permite_video"):
        raise HTTPException(400, "Esse estilo usa só fotos. Envie uma imagem (jpg/png).")
    d = p / ("clips" if video else "img")
    d.mkdir(exist_ok=True)
    raw = d / f"{i + 1:02d}-meu-{int(time.time())}{ext}"
    with open(raw, "wb") as fh:
        while True:
            ch = await file.read(1 << 20)
            if not ch:
                break
            fh.write(ch)
    src = f"{d.name}/{raw.name}"
    if video:   # normaliza pra 1280x720 (ou 1080x1920 nos shorts) mudo (render mais seguro)
        c = cj["cenas"][i]
        dst = raw.with_name(raw.stem + "-n.mp4")
        cw, chh = (1080, 1920) if cj.get("vertical") else (1280, 720)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(raw), "-t", f"{max(4.0, c['e'] - c['s'] + 1.5):.2f}", "-an",
                        "-vf", f"scale={cw}:{chh}:force_original_aspect_ratio=increase,crop={cw}:{chh},fps=30", "-c:v", "libx264",
                        "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p", str(dst)], capture_output=True, timeout=300,
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        if dst.exists():
            raw.unlink(missing_ok=True)
            src = f"clips/{dst.name}"
    cand = {"tipo": "video" if video else "image", "fonte": "Seu PC", "titulo": file.filename, "licenca": "sua", "pagina": "", "url": "pc:" + raw.name, "thumb": ""}
    return {"cenas": _vi_escolher(p, cj, i, cand, prog_src=src)}


@app.post("/api/vi/{pid}/renderizar")
def vi_renderizar(pid: str):
    p = _vi_proj(pid)
    titulo = _vi_ler(p).get("titulo") or p.name
    return start_job(job_vi_montar, p, tipo="short" if _vi_ler(p).get("vertical") else "video_imagens", titulo=titulo[:70] + " · render", pesado=True, pid=pid)


_vi_escolher.desfazendo = False


@app.post("/api/vi/{pid}/desfazer")
def vi_desfazer(pid: str, data: dict = Body(...)):
    """Volta a cena i pra imagem que estava antes da última troca."""
    p = _vi_proj(pid)
    cj = _vi_ler(p)
    i = int(data["i"])
    c = cj["cenas"][i]
    if not c.get("antes"):
        raise HTTPException(400, "Essa cena não tem troca pra desfazer.")
    ant = c["antes"].pop()
    _vi_escolher.desfazendo = True
    try:
        return {"cenas": _vi_escolher(p, cj, i, ant, prog_src=ant.get("src"))}
    finally:
        _vi_escolher.desfazendo = False


def job_vi_amostra(proj: Path, segs, prog):
    rodar_proc([sys.executable, FABRICA / "video_imagens.py", "montar", "--pasta", proj, "--amostra", str(segs)], prog, cwd=FABRICA, render=(15, 98))
    f = CACHE_DIR / "amostras" / proj.name / "final.mp4"
    if not f.exists():
        raise RuntimeError("A amostra não foi gerada.")
    return {"pid": pid_of(proj), "amostra_url": f"/api/vi/{pid_of(proj)}/amostra.mp4?v={int(f.stat().st_mtime)}", "name": proj.name, "conferir": True}


@app.post("/api/vi/{pid}/amostra")
def vi_amostra(pid: str, data: dict = Body(default={})):
    """Render só dos primeiros 20 s (ver o estilo antes de gastar tempo no vídeo inteiro)."""
    p = _vi_proj(pid)
    segs = max(8, min(40, float((data or {}).get("segundos") or 20)))
    titulo = (_vi_ler(p).get("titulo") or p.name)[:60] + f" · amostra {int(segs)} s"
    return start_job(job_vi_amostra, p, segs, tipo="amostra", titulo=titulo, pesado=True, pid=pid)


@app.get("/api/vi/{pid}/amostra.mp4")
def vi_amostra_arquivo(pid: str):
    p = _decode_pid(pid)
    f = CACHE_DIR / "amostras" / p.name / "final.mp4"
    if not f.exists():
        raise HTTPException(404)
    return FileResponse(f, media_type="video/mp4", headers={"Cache-Control": "no-store"})


# ------------------------------------------------------------------ ROTEIRO PRONTO
def job_roteiro(pasta: Path, prog):
    rodar_proc([sys.executable, FABRICA / "roteiro_pronto.py", pasta], prog, cwd=FABRICA)
    r = json.loads((pasta / "resultado.json").read_text(encoding="utf-8"))
    r["rid"] = pasta.name
    return r


@app.post("/api/roteiro")
def roteiro_criar(data: dict = Body(...)):
    g = lambda k: str(data.get(k) or "").strip()
    acao = g("acao") or "escrever"
    if acao not in ("transcrever", "estrutura", "escrever", "melhorar"):
        raise HTTPException(400, "Ação inválida.")
    if acao != "melhorar":
        if not re.match(r"^https?://\S+\.\S+", g("url")):
            raise HTTPException(400, "Cole o link completo do vídeo (começa com https://).")
    if acao == "escrever" and not g("tema"):
        raise HTTPException(400, "Escreva o tema do SEU vídeo.")
    if acao == "melhorar" and len(g("texto").split()) < 30:
        raise HTTPException(400, "Cole o seu roteiro (pelo menos um parágrafo).")
    dur = data.get("duracao") or 300
    if dur != "igual":
        try:
            dur = max(30, min(10800, float(dur)))
        except Exception:
            dur = 300
    aj = AJ.ler()
    ROTEIROS_DIR.mkdir(exist_ok=True)
    nome = f"{time.strftime('%Y%m%d-%H%M%S')}-{acao}-{slug(g('tema') or g('url') or 'roteiro', 30)}"
    pasta = ROTEIROS_DIR / nome
    pasta.mkdir()
    ped = {"acao": acao, "url": g("url"), "tema": g("tema"), "duracao": dur, "texto": g("texto"), "notas": g("notas"),
           "modelo": aj["modelo_ollama"], "idioma": aj["idioma"]}
    (pasta / "pedido.json").write_text(json.dumps(ped, ensure_ascii=False, indent=1), encoding="utf-8")
    rot = {"transcrever": "Pegar roteiro", "estrutura": "Ver estrutura", "escrever": "Roteiro novo", "melhorar": "Melhorar roteiro"}[acao]
    return start_job(job_roteiro, pasta, tipo="roteiro", titulo=f"{rot}: {(g('tema') or g('url') or g('texto')[:50])[:70]}", pesado=True)


@app.get("/api/roteiros")
def roteiros_lista():
    out = []
    if ROTEIROS_DIR.exists():
        for d in sorted((d for d in ROTEIROS_DIR.iterdir() if (d / "resultado.json").exists()), reverse=True)[:15]:
            try:
                r = json.loads((d / "resultado.json").read_text(encoding="utf-8"))
            except Exception:
                continue
            out.append({"rid": d.name, "acao": r.get("acao"), "tema": r.get("tema") or "", "video": (r.get("video") or {}).get("titulo", ""),
                        "criado": r.get("criado")})
    return out


@app.get("/api/roteiro/{rid}")
def roteiro_get(rid: str):
    f = ROTEIROS_DIR / Path(rid).name / "resultado.json"
    if not f.exists():
        raise HTTPException(404)
    r = json.loads(f.read_text(encoding="utf-8"))
    r["rid"] = Path(rid).name
    return r


@app.post("/api/roteiro/claude/pedido")
def roteiro_claude_pedido(data: dict = Body(...)):
    from lib import claude_rev
    rot = str(data.get("roteiro") or "").strip()
    if not rot:
        raise HTTPException(400, "Não há roteiro pra revisar.")
    a = AJ.ler()
    txt = claude_rev.pedido(rot, AJ.idioma_llm(a["idioma"]), str(data.get("tema") or ""))
    out = {"texto": txt, "tem_chave": bool(a.get("anthropic_key")), "modelo": claude_rev.MODELO}
    if a.get("anthropic_key"):
        try:
            out["estimativa"] = claude_rev.estimar(a["anthropic_key"], txt, len(rot.split()))
        except Exception as e:
            out["erro_estimativa"] = str(e)[:200]
    return out


@app.post("/api/roteiro/claude/revisar")
def roteiro_claude_revisar(data: dict = Body(...)):
    from lib import claude_rev
    a = AJ.ler()
    if not a.get("anthropic_key"):
        raise HTTPException(400, "Coloque a chave da API Anthropic em Ajustes (ou use o botão de copiar o pedido).")
    rot = str(data.get("roteiro") or "").strip()
    txt = claude_rev.pedido(rot, AJ.idioma_llm(a["idioma"]), str(data.get("tema") or ""))
    try:
        return claude_rev.revisar(a["anthropic_key"], txt)
    except Exception as e:
        raise HTTPException(502, "O Claude não respondeu: " + str(e)[:300])


@app.get("/api/saude")
def saude():
    return memo("saude", _saude, ttl=60)


def _saude():
    """Checklist do primeiro uso (rápido, sem gerar nada)."""
    a = AJ.ler()
    ms = [m["nome"] for m in ajustes_modelos()]
    from lib import tts as TTS
    from lib.transcrever import WHISPER_PY
    d = memo("tts_disp", TTS.disponiveis, ttl=60)   # leve 01/11: mesma conferência das vozes (porta 8020 fechada custa ~2 s)
    feitos = sum(1 for x in out_dir().glob("*-imagens-*") if (x / "final.mp4").exists()) + sum(1 for x in out_dir().glob("*-fabrica-*") if (x / "final.mp4").exists())
    return {"ollama": bool(ms), "modelo_ok": a["modelo_ollama"] in ms, "modelo": a["modelo_ollama"],
            "voz": bool(d.get("edge") or d.get("qwen3") or d.get("chatterbox")), "whisper": WHISPER_PY.exists(),
            "ffmpeg": bool(shutil.which("ffmpeg")), "videos_feitos": feitos}


# ------------------------------------------------------------------ ESTILOS QUE ESTÃO BOMBANDO (ranking com os NOSSOS dados)
MEDIDAS_F = CACHE_DIR / "bombando-medidas.json"
VIDEOS_NOVOS = VIDEOS_TESTE.parent / "VIDEOS-NOVOS"
VIDEOS_SHORTS = VIDEOS_TESTE.parent / "VIDEOS-SHORTS"


def _num_br(s):
    """'11.148' → 11148 ; '1,2M' → 1200000 ; '68k' → 68000 ; '—' → None"""
    s = str(s or "").strip().lower()
    m = re.match(r"^([\d.,]+)\s*([km]?)", s)
    if not m:
        return None
    n = m.group(1)
    mult = {"k": 1e3, "m": 1e6}.get(m.group(2), 1)
    n = n.replace(".", "").replace(",", ".") if mult == 1 else n.replace(",", ".")
    try:
        return int(float(n) * mult)
    except Exception:
        return None


def _resumo_novos():
    """Lê as tabelas do ESTILOS-NOVOS/RESUMO.md → {NN: {vph, facil, idiomas, canal_ref, dificuldade}}."""
    md = _ler_md(ESTILOS_NOVOS / "RESUMO.md")
    out = {}
    for ln in md.splitlines():
        c = [x.strip() for x in ln.strip().strip("|").split("|")]
        if len(c) < 7 or not c[0].isdigit():
            continue
        m = re.search(r"\*\*(\d{2})\s+(.+?)\*\*", c[1])
        if not m:
            continue
        nn = m.group(1)
        ref = c[2]
        if "·" in ref:   # tabela 2: "Canal (mediana · v/h · pico)"
            canal = ref.split("(")[0].strip()
            partes = [p.strip() for p in ref.split("(", 1)[1].split(")")[0].split("·")] if "(" in ref else []
            vph = _num_br(partes[1]) if len(partes) > 1 else None
        else:            # tabela 1: "11.148 (Dieck Docs)"
            vph = _num_br(ref.split("(")[0])
            canal = ref.split("(")[1].rstrip(")").strip() if "(" in ref else ""
        idi = [x.strip() for x in re.sub(r"\(.*?\)", "", c[6]).replace("*", "").split("·") if x.strip()]
        out[nn] = {"nome_resumo": m.group(2).strip(), "vph": vph, "facil": _num_br(c[3]) or 3, "idiomas": [i for i in idi if len(i) <= 3],
                   "canal_ref": canal, "dificuldade": re.sub(r"\*+", "", c[5])}
    return out


def _ref_txt(pasta: Path, canal_nome=""):
    """REFERENCIA.txt → (canal, canal_url, video_url, idioma) do canal citado no RESUMO (ou o 1º)."""
    t = _ler_md(pasta / "REFERENCIA.txt")
    secs = re.split(r"^##\s+", t, flags=re.M)[1:]
    escolha = None
    for s in secs:
        if canal_nome and canal_nome.lower()[:12] in s.splitlines()[0].lower():
            escolha = s
            break
    escolha = escolha or (secs[0] if secs else "")
    if not escolha:
        return {}
    h = escolha.splitlines()[0]
    m = re.match(r"(.+?)\s*(?:\[(\w+)\])?\s*[—-]+\s*(https?://\S+)", h)
    v = re.search(r"\|\s*(https?://youtu\S+)\s*\|", escolha)
    return {"canal": (m.group(1) if m else h).strip(), "idioma": (m.group(2) or "") if m else "", "canal_url": m.group(3) if m else "",
            "video": v.group(1) if v else ""}


def _medidas():
    try:
        return json.loads(MEDIDAS_F.read_text(encoding="utf-8"))
    except Exception:
        return {}


def medir_canal(url):
    """Views/hora (mediana dos últimos vídeos, 45 d, mín. 12 h de idade) só com --flat-playlist + approximate_date (sem abrir vídeo)."""
    u = url.rstrip("/")
    if "youtube.com" not in u:
        return None
    if not re.search(r"/(videos|shorts|streams)$", u):
        u += "/videos"
    r = subprocess.run([*RYT.cmd(),"--no-warnings", "--flat-playlist", "--extractor-args", "youtubetab:approximate_date", "-I", "1:15",
                        "--print", "%(view_count)s|%(timestamp)s", u], capture_output=True, text=True, encoding="utf-8", errors="replace",
                       timeout=120, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    now, vphs, todos = time.time(), [], []
    for ln in r.stdout.splitlines():
        a, _, b = ln.partition("|")
        if not a.isdigit() or not b.split(".")[0].isdigit():
            continue
        horas = max(12, (now - float(b)) / 3600)
        v = int(a) / horas
        todos.append(v)
        if horas <= 45 * 24:
            vphs.append(v)
    base = vphs or todos
    if not base:
        return None
    base.sort()
    return int(base[len(base) // 2])


def _fac_cat(facil, fabrica=False):
    if fabrica:
        return "auto"
    return "medio" if (facil or 0) >= 3 else "dificil"


ORIG_FACIL = {"01": 2, "02": 3, "03": 3, "04": 5, "05": 3, "06": 2, "07": 2, "08": 5, "09": 1, "10": 2, "11": 2, "12": 5, "13": 1}


def bombando_dados():
    med = _medidas()
    ridx = _ref_index()
    fab_orig = {}
    for e in catalogo_estilos():
        if e.get("tipo") == "fabrica" and e.get("pasta"):
            fab_orig[Path(e["pasta"]).name] = e["id"]
    itens = []

    def projeto(d: Path):
        try:
            ed = B.load_edit(d, convert=False)
        except Exception:
            return {}, {}
        vid = find_video(d)
        return ed, {"pid": pid_of(d), "thumb_url": f"/api/thumb/{pid_of(d)}" if (d / "thumb.jpg").exists() else None,
                    "tem_ref": bool(vid) and bool(find_ref(d, ed, ridx))}

    # 13 estilos originais (VIDEOS/01..13)
    for d in sorted(VIDEOS_TESTE.glob("[0-1][0-9]-*")):
        if not re.match(r"^(0[1-9]|1[0-3])-", d.name) or not (d / "edit.json").exists():
            continue
        ed, pj = projeto(d)
        ref = ed.get("referencia") or {}
        nn = d.name[:2]
        fab = fab_orig.get(d.name)
        m = med.get(ref.get("canal_url") or "", {})
        itens.append({**pj, "id": "orig:" + d.name, "nome": estilo_of(ed, d), "formato": "longo", "canal": ref.get("canal", ""), "canal_url": ref.get("canal_url", ""),
                      "video_url": ref.get("video", ""), "vph": m.get("vph"), "idiomas": [], "facil": 5 if fab else ORIG_FACIL.get(nn, 3),
                      "facilidade": _fac_cat(ORIG_FACIL.get(nn, 3), bool(fab)), "estilo_id": fab or "claude:" + d.name,
                      "nota": "Estilo original do catálogo" + (" · a fábrica faz sozinho" if fab else "")})
    # estilos novos (ESTILOS-NOVOS + vídeo-teste em VIDEOS-NOVOS)
    res = _resumo_novos()
    if ESTILOS_NOVOS.exists():
        for cat in sorted(ESTILOS_NOVOS.iterdir()):
            if not cat.is_dir() or not re.match(r"^\d{2}-", cat.name):
                continue
            nn = cat.name[:2]
            r = res.get(nn, {})
            ref = _ref_txt(cat, r.get("canal_ref", ""))
            info = _estilo_novo(cat) if (cat / "ESTILO.md").exists() else {"nome": cat.name}
            dv = next(iter(sorted(VIDEOS_NOVOS.glob(nn + "-*"))), None) if VIDEOS_NOVOS.exists() else None
            ed, pj = projeto(dv) if dv and (dv / "edit.json").exists() else ({}, {})
            m = med.get(ref.get("canal_url") or "", {})
            vph = m.get("vph") or r.get("vph")
            idi = r.get("idiomas") or ([ref["idioma"]] if ref.get("idioma") else [])
            itens.append({**pj, "id": "novo:" + cat.name, "nome": re.sub(r"\s*\(.*\)\s*$", "", info.get("nome") or cat.name), "formato": "longo",
                          "canal": ref.get("canal") or r.get("canal_ref", ""), "canal_url": ref.get("canal_url", ""), "video_url": ref.get("video", ""),
                          "vph": vph, "idiomas": idi, "facil": r.get("facil", 3), "facilidade": _fac_cat(r.get("facil", 3)),
                          "estilo_id": ("claude:novos:" + dv.name) if dv else "novo:" + cat.name, "nota": r.get("dificuldade", "")[:140]})
    # shorts (VIDEOS-SHORTS, referências do Instagram: views/hora não medível)
    if VIDEOS_SHORTS.exists():
        for d in sorted(VIDEOS_SHORTS.iterdir()):
            if not d.is_dir() or not (d / "edit.json").exists():
                continue
            ed, pj = projeto(d)
            ref = ed.get("referencia") or {}
            m = med.get(ref.get("canal_url") or "", {})
            itens.append({**pj, "id": "short:" + d.name, "nome": estilo_of(ed, d), "formato": "short", "canal": ref.get("canal", ""),
                          "canal_url": ref.get("canal_url", ""), "video_url": ref.get("video", ""), "vph": m.get("vph"), "idiomas": ["PT"] if ref else [],
                          "facil": 2, "facilidade": "dificil", "estilo_id": "claude:shorts:" + d.name, "nota": "Referência do Instagram: views/hora não dá pra medir de fora"})
    itens.sort(key=lambda x: (-(x["vph"] or 0) * (x["facil"] or 1), x["nome"]))
    medido = (med.get("_quando") or "22/10/2026 (mineração do catálogo)")
    return {"medido_em": medido, "itens": itens}


@app.get("/api/bombando")
def bombando():
    return memo("bombando", bombando_dados, ttl=60, sig=lambda: (MEDIDAS_F.stat().st_mtime if MEDIDAS_F.exists() else 0))


def job_medir(prog):
    urls = []
    for x in bombando_dados()["itens"]:
        u = x.get("canal_url") or ""
        if "youtube.com" in u and u not in urls:
            urls.append(u)
    med = _medidas()
    for k, u in enumerate(urls):
        prog(100 * k / max(1, len(urls)), f"Medindo canal {k + 1} de {len(urls)}…")
        try:
            v = medir_canal(u)
            if v:
                med[u] = {"vph": v, "quando": datetime.now().strftime("%d/%m/%Y %H:%M")}
        except Exception:
            pass
        time.sleep(2.5)   # devagar de propósito (evita bot-check do YouTube)
    med["_quando"] = datetime.now().strftime("%d/%m/%Y %H:%M")
    CACHE_DIR.mkdir(exist_ok=True)
    MEDIDAS_F.write_text(json.dumps(med, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"medidos": len(urls)}


@app.post("/api/bombando/atualizar")
def bombando_atualizar():
    return start_job(job_medir, tipo="medir", titulo="Atualizar views/hora dos estilos", pesado=False)


# ================================================================== FERRAMENTAS (fase 2): Fábrica de cortes · Editor de vídeo falado · Ideias
# ·  Copiar estilo (modo rápido) · Extras.  Tudo local, zero token Claude. Scripts em fabrica\ falam com a fila por "@@pct|msg".
from lib import ideias as IDEIAS  # noqa: E402
from lib import preencher_preset as PRESET  # noqa: E402
from lib import emalta as EMALTA  # noqa: E402


# ------------------------------------------------------------------ 🔥 BOMBANDO AGORA (vídeos faceless em alta; .cache/bombando.json)
@app.get("/api/emalta")
def emalta():
    return EMALTA.ler()


@app.get("/api/emalta/nichos")
def emalta_nichos(formato: str = "longo"):
    return EMALTA.ranking_nichos("short" if formato == "short" else "longo")


@app.post("/api/emalta/atualizar")
def emalta_atualizar():
    for j in JOBS.values():   # já tem uma busca rodando → acompanha a mesma
        if j.get("tipo") == "emalta" and not j.get("done"):
            return {"job": j["id"]}
    return start_job(lambda prog: EMALTA.coletar(prog, ESTILOS_NOVOS), tipo="emalta", titulo="Atualizar 🔥 Bombando", pesado=False)

EXTRAS_DIR = ROOT / "extras"
IDEIAS_DIR = ROOT / "ideias"
VID_EXTS = (".mp4", ".mov", ".mkv", ".webm", ".m4v", ".avi")


@app.post("/api/arquivo")
async def arquivo_subir(file: UploadFile = File(...)):
    """Recebe um vídeo do PC (cortes, vídeo falado, copiar estilo). Fica em .pedidos até o trabalho começar."""
    ext = Path(file.filename or "").suffix.lower()
    if ext not in VID_EXTS:
        raise HTTPException(400, "Envie um vídeo (mp4, mov, mkv ou webm).")
    PEDIDOS_TMP.mkdir(exist_ok=True)
    dst = PEDIDOS_TMP / f"video-{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:4]}{ext}"
    with open(dst, "wb") as fh:
        while True:
            ch = await file.read(4 << 20)
            if not ch:
                break
            fh.write(ch)
    info = probe_full(dst) or {}
    if not info.get("dur"):
        dst.unlink(missing_ok=True)
        raise HTTPException(400, "Não consegui ler esse vídeo.")
    return {"arquivo_id": dst.name, "nome": file.filename, "dur": info.get("dur"), "w": info.get("w"), "h": info.get("h")}


def _arquivo(aid):
    a = PEDIDOS_TMP / Path(str(aid or "")).name
    if not aid or not a.exists():
        raise HTTPException(400, "Envie o vídeo (e espere aparecer ✅) ou cole um link.")
    return a


def _url_video(u):
    u = str(u or "").strip()
    if u and not re.match(r"^https?://\S+\.\S+", u):
        raise HTTPException(400, "Link inválido — cole o link completo (começa com https://).")
    return u


def _segundos(v):
    """'1:30', '90', '01:02:03' → segundos (ou None)."""
    v = str(v or "").strip()
    if not v:
        return None
    try:
        p = [float(x) for x in v.split(":")]
    except Exception:
        raise HTTPException(400, f"Tempo inválido: {v} (use 1:30 ou 90).")
    s = 0
    for x in p:
        s = s * 60 + x
    return int(s)


def _projeto_info(p: Path):
    vid = find_video(p)
    pid = pid_of(p)
    return {"pid": pid, "pasta": p.name, "rendered": bool(vid), "video_url": f"/p/{pid}/final.mp4" if (p / "final.mp4").exists() else None,
            "leve_url": f"/p/{pid}/leve.mp4" if (p / "leve.mp4").exists() else None, "thumb_url": f"/p/{pid}/thumb.jpg" if (p / "thumb.jpg").exists() else None}


# ------------------------------------------------------------------ ✂ FÁBRICA DE CORTES
def job_cortes(proj: Path, prog):
    rodar_proc([sys.executable, FABRICA / "cortes.py", "--pasta", proj], prog, cwd=FABRICA)
    d = cortes_get(pid_of(proj))
    primeiro = d["cortes"][0] if d["cortes"] else {}
    return {"cid": pid_of(proj), "pid": primeiro.get("pid"), "folder": str(proj), "name": proj.name, "rendered": bool(primeiro.get("rendered")),
            "n": len(d["cortes"]), "minutos": d.get("minutos"), "tokens": 0}


@app.post("/api/cortes/criar")
def cortes_criar(data: dict = Body(...)):
    g = lambda k: str(data.get(k) or "").strip()
    url = _url_video(g("url"))
    arq = None if url else _arquivo(g("arquivo_id"))
    n = int(data.get("n") or 3)
    if not 1 <= n <= 10:
        raise HTTPException(400, "Escolha de 1 a 10 cortes.")
    dmin, dmax = float(data.get("dur_min") or 30), float(data.get("dur_max") or 60)
    if not (10 <= dmin < dmax <= 180):
        raise HTTPException(400, "Duração dos cortes inválida (entre 10 s e 3 min, mínimo menor que o máximo).")
    aj = AJ.ler()
    OUT = out_dir()
    nn = proximo_numero(OUT)
    base = g("titulo") or (Path(g("arquivo_nome")).stem if g("arquivo_nome") else "") or ("link" if url else "video")
    proj = OUT / f"{nn:02d}-cortes-{slug(base, 34) or 'video'}"
    proj.mkdir(parents=True, exist_ok=True)
    ped = {"url": url, "arquivo": str(arq) if arq else "", "de": _segundos(g("de")), "ate": _segundos(g("ate")), "n": n,
           "modo": "regras" if g("modo") == "regras" else "ia", "enquadramento": "centro" if g("enquadramento") == "centro" else "desfocado",
           "dur_min": dmin, "dur_max": dmax, "intro": bool(data.get("intro")), "canal": g("canal"), "programa": g("programa"), "titulo": base,
           "idioma": g("idioma") or aj["idioma"], "modelo": aj["modelo_ollama"], "criado": datetime.now().isoformat(timespec="seconds")}
    (proj / "pedido.json").write_text(json.dumps(ped, ensure_ascii=False, indent=1), encoding="utf-8")
    return {**start_job(job_cortes, proj, tipo="cortes", titulo=f"{base[:60]} · {n} {'corte' if n == 1 else 'cortes'}", pesado=True), "cid": pid_of(proj)}


@app.get("/api/cortes/{cid}")
def cortes_get(cid: str):
    p = _decode_pid(cid)
    f = p / "cortes.json"
    if not f.exists():
        raise HTTPException(404, "Esses cortes ainda não ficaram prontos.")
    cj = json.loads(f.read_text(encoding="utf-8"))
    out = []
    for c in cj.get("cortes") or []:
        d = p / c["pasta"]
        out.append({**c, **_projeto_info(d)})
    rel = {}
    try:
        rel = json.loads((p / "RELATORIO.json").read_text(encoding="utf-8"))
    except Exception:
        pass
    intro = _projeto_info(p / cj["intro"]) if cj.get("intro") and (p / cj["intro"]).exists() else None
    return {"cid": cid, "nome": p.name, "pasta_nome": amigavel(p), "modo": cj.get("modo"), "enquadramento": cj.get("enquadramento"), "cortes": out,
            "intro": intro, "minutos": rel.get("minutos"), "duracao_fonte": rel.get("duracao_fonte"), "tokens": 0, "pronto": bool(rel)}


@app.get("/api/cortes")
def cortes_lista():
    out = []
    for f in sorted(out_dir().glob("*/cortes.json"), key=lambda f: -f.stat().st_mtime)[:12]:
        if (f.parent / "pedido.json").exists() and "cortes" in f.parent.name:
            try:
                n = len(json.loads(f.read_text(encoding="utf-8")).get("cortes") or [])
            except Exception:
                n = 0
            out.append({"cid": pid_of(f.parent), "nome": f.parent.name, "n": n, "quando": datetime.fromtimestamp(f.stat().st_mtime).strftime("%d/%m %H:%M")})
    return out


# ------------------------------------------------------------------ 🎙 EDITOR DE VÍDEO FALADO
def job_falado(proj: Path, prog):
    rodar_proc([sys.executable, FABRICA / "falado.py", "--pasta", proj], prog, cwd=FABRICA, render=(60, 99))
    return {**falado_get(pid_of(proj)), "folder": str(proj), "tokens": 0}


@app.post("/api/falado/criar")
def falado_criar(data: dict = Body(...)):
    g = lambda k: str(data.get(k) or "").strip()
    arq = _arquivo(g("arquivo_id"))
    saida = g("saida") if g("saida") in ("16:9", "9:16", "ambos") else "16:9"
    aj = AJ.ler()
    OUT = out_dir()
    nn = proximo_numero(OUT)
    base = g("titulo") or Path(g("arquivo_nome") or arq.stem).stem
    proj = OUT / f"{nn:02d}-falado-{slug(base, 34) or 'video'}"
    proj.mkdir(parents=True, exist_ok=True)
    ped = {"arquivo": str(arq), "saida": saida, "legenda": bool(data.get("legenda", True)), "broll": bool(data.get("broll")),
           "n_broll": int(data.get("n_broll") or 0), "silencio": bool(data.get("silencio", True)), "retakes": bool(data.get("retakes", True)),
           "min_sil": float(data.get("min_sil") or 0.6), "titulo": g("titulo"), "idioma": g("idioma") or aj["idioma"], "modelo": aj["modelo_ollama"],
           "criado": datetime.now().isoformat(timespec="seconds")}
    (proj / "pedido.json").write_text(json.dumps(ped, ensure_ascii=False, indent=1), encoding="utf-8")
    return {**start_job(job_falado, proj, tipo="falado", titulo=f"{base[:60]} · {saida}", pesado=True, pid=pid_of(proj)), "fid": pid_of(proj)}


@app.get("/api/falado/{fid}")
def falado_get(fid: str):
    p = _decode_pid(fid)
    rel, cj = {}, {}
    try:
        rel = json.loads((p / "RELATORIO.json").read_text(encoding="utf-8"))
        cj = json.loads((p / "cortes.json").read_text(encoding="utf-8"))
    except Exception:
        pass
    saidas = [{"formato": s["formato"], **_projeto_info(Path(s["pasta"]))} for s in rel.get("saidas") or [] if Path(s["pasta"]).exists()]
    pr = saidas[0] if saidas else {}
    return {"fid": fid, "pid": pr.get("pid"), "rendered": bool(pr.get("rendered")), "name": p.name, "pasta_nome": amigavel(p), "saidas": saidas,
            "duracao_original": rel.get("duracao_original"), "duracao": rel.get("duracao_video"), "trechos": rel.get("trechos"),
            "retakes": cj.get("retakes") or [], "silencios": rel.get("silencios_tirados"), "brolls": rel.get("brolls"), "minutos": rel.get("minutos")}


# ------------------------------------------------------------------ 💡 IDEIAS
def _ideias_salvar(nome, d):
    IDEIAS_DIR.mkdir(exist_ok=True)
    tmp = IDEIAS_DIR / f"{nome}.json.tmp"
    tmp.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, IDEIAS_DIR / f"{nome}.json")
    return d


def _ideias_ler(nome, padrao=None):
    try:
        return json.loads((IDEIAS_DIR / f"{nome}.json").read_text(encoding="utf-8"))
    except Exception:
        return padrao


def _idioma_ok(i):
    """Idioma das Ideias (pt-BR / en-US / es-MX); vazio = o idioma dos Ajustes."""
    return i if i in AJ.IDIOMAS else AJ.ler()["idioma"]


@app.post("/api/ideias/cacar")
def ideias_cacar(data: dict = Body(...)):
    kw = str(data.get("kw") or "").strip()
    if len(kw) < 2:
        raise HTTPException(400, "Escreva uma palavra-chave (ex.: curiosidades).")
    fmt = data.get("formato") if data.get("formato") in IDEIAS.FILTRO else "todos"

    def job(prog):
        r = IDEIAS.cacar(kw, fmt, int(data.get("canais") or 8), bool(data.get("atualizar")), prog=prog, idioma=_idioma_ok(data.get("idioma")))
        _ideias_salvar("ultimo-cacar", r)
        return r
    return start_job(job, tipo="ideias", titulo=f"Caçador de nicho: {kw[:50]}", pesado=False)


@app.post("/api/ideias/saturado")
def ideias_saturado(data: dict = Body(...)):
    e = str(data.get("entrada") or "").strip()
    if len(e) < 2:
        raise HTTPException(400, "Cole o link de um vídeo/canal ou escreva o tema.")

    def job(prog):
        r = IDEIAS.saturacao(e, AJ.ler()["modelo_ollama"], prog=prog, idioma=_idioma_ok(data.get("idioma")))
        _ideias_salvar("ultimo-saturado", r)
        return r
    return start_job(job, tipo="ideias", titulo=f"Nicho tá saturado? {e[:50]}", pesado=False)


@app.post("/api/ideias/publico")
def ideias_publico(data: dict = Body(...)):
    u = _url_video(data.get("url"))
    if not u:
        raise HTTPException(400, "Cole o link do vídeo.")
    lim = max(20, min(500, int(data.get("limite") or 500)))

    def job(prog):
        r = IDEIAS.publico(u, lim, AJ.ler()["modelo_ollama"], prog=prog, idioma=_idioma_ok(data.get("idioma")))
        _ideias_salvar("ultimo-publico", r)
        return r
    return start_job(job, tipo="ideias", titulo=f"O que o público pede: {u[-24:]}", pesado=True)


@app.get("/api/ideias/ultimos")
def ideias_ultimos():
    return {k: _ideias_ler("ultimo-" + k) for k in ("cacar", "saturado", "publico")}


@app.get("/api/ideias/placar")
def placar_get():
    return _ideias_ler("placar", {"ideias": []})


@app.post("/api/ideias/placar")
def placar_add(data: dict = Body(...)):
    lst = [x.strip(" -•\t") for x in str(data.get("ideias") or "").splitlines() if len(x.strip()) > 4][:30]
    if not lst:
        raise HTTPException(400, "Escreva pelo menos 1 ideia (uma por linha).")
    nicho = str(data.get("nicho") or "").strip()

    def job(prog):
        prog(10, f"A IA local está dando nota pra {len(lst)} ideia(s)…")
        notas = IDEIAS.notas_ideias(lst, nicho, AJ.ler()["modelo_ollama"], idioma=_idioma_ok(data.get("idioma")))
        pl = _ideias_ler("placar", {"ideias": []})
        for x in notas:
            pl["ideias"].insert(0, {"id": uuid.uuid4().hex[:8], **x, "nicho": nicho, "criado": datetime.now().strftime("%d/%m/%Y"), "views": None,
                                    "status": "ideia"})
        _ideias_salvar("placar", pl)
        return {"n": len(notas)}
    return start_job(job, tipo="ideias", titulo=f"Placar de ideias: {len(lst)} ideia(s)", pesado=True)


@app.put("/api/ideias/placar/{iid}")
def placar_put(iid: str, data: dict = Body(...)):
    pl = _ideias_ler("placar", {"ideias": []})
    for x in pl["ideias"]:
        if x["id"] == iid:
            if "views" in data:
                v = str(data.get("views") or "").replace(".", "").replace(",", "").strip()
                x["views"] = int(v) if v.isdigit() else None
            if data.get("status") in ("ideia", "feita", "publicada", "descartada"):
                x["status"] = data["status"]
    return _ideias_salvar("placar", pl)


@app.delete("/api/ideias/placar/{iid}")
def placar_del(iid: str):
    pl = _ideias_ler("placar", {"ideias": []})
    pl["ideias"] = [x for x in pl["ideias"] if x["id"] != iid]
    return _ideias_salvar("placar", pl)


# ------------------------------------------------------------------ 🎨 COPIAR ESTILO — MODO RÁPIDO (aproximado, grátis)
def job_copiar_rapido(pasta: Path, prog):
    rodar_proc([sys.executable, FABRICA / "copiar_estilo.py", "--pasta", pasta], prog, cwd=FABRICA)
    return json.loads((pasta / "resultado.json").read_text(encoding="utf-8"))


@app.post("/api/copiar-rapido")
def copiar_rapido(data: dict = Body(...)):
    g = lambda k: str(data.get(k) or "").strip()
    url = _url_video(g("url"))
    arq = None if url else _arquivo(g("arquivo_id"))
    pasta = CACHE_DIR / "copiar" / time.strftime("%Y%m%d-%H%M%S")
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / "pedido.json").write_text(json.dumps({"url": url, "arquivo": str(arq) if arq else "", "nome": g("nome")}, ensure_ascii=False), encoding="utf-8")
    return start_job(job_copiar_rapido, pasta, tipo="copiar", titulo=f"Copiar estilo (rápido): {g('nome') or url[-30:]}", pesado=True)


def _estilos_meus():
    out = []
    for d in sorted(ESTILOS_FAB.iterdir(), key=lambda d: -d.stat().st_mtime):
        cfg = _cfg_estilo(d.name)
        if not (cfg.get("aproximado") or cfg.get("extra_de")):
            continue
        capa = d / "capa.jpg"
        out.append({"id": d.name, "nome": cfg.get("nome") or d.name, "descricao": _desc_estilo(cfg), "formato": cfg.get("formato") or "longo",
                    "aproximado": bool(cfg.get("aproximado")), "extra": cfg.get("extra_de"), "preset": cfg.get("preset") or {},
                    "analise": cfg.get("analise") or {}, "capa_url": f"/api/estilo-capa/{d.name}?v={int(capa.stat().st_mtime)}" if capa.exists() else None,
                    "previa_url": f"/api/estilo-previa/{d.name}?v={int((d / 'previa.jpg').stat().st_mtime)}" if (d / "previa.jpg").exists() else None,
                    "exportado": (EXTRAS_DIR / d.name / "estilo.json").exists()})
    return out


@app.get("/api/estilos-meus")
def estilos_meus():
    return _estilos_meus()


@app.get("/api/estilo-previa/{eid}")
def estilo_previa(eid: str):
    f = ESTILOS_FAB / Path(eid).name / "previa.jpg"
    if not f.exists():
        raise HTTPException(404, "Esse estilo ainda não tem prévia.")
    return FileResponse(f, headers={"Cache-Control": "no-store"})


@app.post("/api/estilos-meus/{eid}/pecas")
def estilos_meus_pecas(eid: str, data: dict = Body(...)):
    """Liga/desliga uma peça do estilo copiado ou troca a cor de destaque, e redesenha a prévia."""
    from lib import elementos as ELEM
    d = ESTILOS_FAB / Path(eid).name
    cfg = _cfg_estilo(d.name)
    if not d.exists() or not cfg.get("aproximado"):
        raise HTTPException(400, "Só dá pra mudar estilos copiados por você.")
    pr = cfg.setdefault("preset", {})
    if data.get("tipo"):
        el = next((e for e in pr.get("elementos") or [] if e.get("tipo") == data["tipo"]), None)
        if not el:
            raise HTTPException(400, "Essa peça não existe neste estilo.")
        el["ligado"] = bool(data.get("ligado"))
        if el["tipo"] == "legenda":
            pr["legenda"] = el["ligado"]
    if data.get("cor_destaque"):
        cor = str(data["cor_destaque"]).strip()
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", cor):
            raise HTTPException(400, "Cor inválida — escolha no quadradinho de cor.")
        pr["cor_destaque"], pr["destaque_padrao"] = cor, False
    (d / "estilo.json").write_text(json.dumps(cfg, ensure_ascii=False, indent=1), encoding="utf-8")
    try:
        ELEM.previa(pr.get("elementos") or [], pr, d / "previa.jpg", d / "previa_fundo.jpg")
    except Exception:
        pass
    return {"ok": True, "preset": pr}


@app.delete("/api/estilos-meus/{eid}")
def estilos_meus_apagar(eid: str):
    d = ESTILOS_FAB / Path(eid).name
    cfg = _cfg_estilo(d.name)
    if not d.exists() or not (cfg.get("aproximado") or cfg.get("extra_de")):
        raise HTTPException(400, "Só dá pra apagar estilos copiados por você ou instalados dos Extras.")
    shutil.rmtree(d)
    return {"ok": True}


# ------------------------------------------------------------------ 🧩 EXTRAS (pasta local extras\, sem rede)
EXTRA_OK = {".json", ".mp4", ".jpg", ".jpeg", ".png", ".webp", ".txt", ".md"}   # só dados/mídia: nunca código de fora


def _extra_cfg(d: Path):
    try:
        return json.loads((d / "estilo.json").read_text(encoding="utf-8-sig"))
    except Exception:
        return None


@app.get("/api/extras")
def extras_lista():
    EXTRAS_DIR.mkdir(exist_ok=True)
    out = []
    for d in sorted(x for x in EXTRAS_DIR.iterdir() if x.is_dir()):
        cfg = _extra_cfg(d)
        if not cfg:
            continue
        inst = ESTILOS_FAB / d.name
        icfg = _cfg_estilo(d.name) if inst.exists() else {}
        out.append({"id": d.name, "nome": cfg.get("nome") or d.name, "descricao": cfg.get("descricao", ""), "formato": cfg.get("formato") or
                    (cfg.get("preset") or {}).get("formato") or "longo", "autor": cfg.get("autor") or "",
                    "preview_url": f"/api/extras/{d.name}/preview.mp4" if (d / "preview.mp4").exists() else None,
                    "capa_url": f"/api/extras/{d.name}/capa.jpg" if (d / "capa.jpg").exists() else None,
                    "instalado": inst.exists() and icfg.get("extra_de") == d.name, "conflito": inst.exists() and icfg.get("extra_de") != d.name})
    return out


@app.get("/api/extras/{eid}/{arq}")
def extras_arquivo(eid: str, arq: str):
    if arq not in ("preview.mp4", "capa.jpg"):
        raise HTTPException(404)
    f = EXTRAS_DIR / Path(eid).name / arq
    if not f.exists():
        raise HTTPException(404)
    return FileResponse(f, headers={"Cache-Control": "no-store"})


@app.post("/api/extras/{eid}/instalar")
def extras_instalar(eid: str):
    src = EXTRAS_DIR / Path(eid).name
    cfg = _extra_cfg(src)
    if not cfg:
        raise HTTPException(404, "Esse extra não tem estilo.json válido.")
    dst = ESTILOS_FAB / src.name
    if dst.exists() and _cfg_estilo(dst.name).get("extra_de") != src.name:
        raise HTTPException(400, "Já existe um estilo com esse nome no seu Estúdio.")
    if not isinstance(cfg.get("preset"), dict):
        raise HTTPException(400, "Esse extra não é um estilo por preset (falta o \"preset\").")
    cfg.update({"extra_de": src.name, "imagens": "wikimedia", "so_ferramenta": True, "vertical": (cfg["preset"].get("formato") == "short")})
    PRESET.criar_estilo(dst, cfg)   # o preencher.py é sempre o nosso (código do extra nunca é copiado)
    for f in src.iterdir():
        if f.is_file() and f.suffix.lower() in EXTRA_OK and f.name not in ("estilo.json",):
            shutil.copy2(f, dst / f.name)
    return {"ok": True}


@app.post("/api/extras/{eid}/remover")
def extras_remover(eid: str):
    d = ESTILOS_FAB / Path(eid).name
    if not d.exists() or _cfg_estilo(d.name).get("extra_de") != Path(eid).name:
        raise HTTPException(400, "Esse extra não está instalado.")
    shutil.rmtree(d)
    return {"ok": True}


@app.post("/api/extras/abrir")
def extras_abrir():
    EXTRAS_DIR.mkdir(exist_ok=True)
    abrir(EXTRAS_DIR)
    return {"ok": True}


@app.post("/api/extras/exportar")
def extras_exportar(data: dict = Body(...)):
    """Copia um estilo seu (copiado/aproximado) pra pasta extras\\ — pronto pra passar pra um amigo (só estilo.json + prévia)."""
    eid = Path(str(data.get("estilo") or "")).name
    d = ESTILOS_FAB / eid
    cfg = _cfg_estilo(eid)
    if not d.exists() or not cfg.get("preset"):
        raise HTTPException(400, "Escolha um estilo copiado por você.")
    dst = EXTRAS_DIR / eid
    dst.mkdir(parents=True, exist_ok=True)
    limpo = {k: v for k, v in cfg.items() if k not in ("analise", "referencia", "extra_de", "criado")}   # nada da referência vai junto
    limpo["autor"] = data.get("autor") or "eu"
    (dst / "estilo.json").write_text(json.dumps(limpo, ensure_ascii=False, indent=1), encoding="utf-8")
    prev = d / "preview.mp4"
    if prev.exists():
        shutil.copy2(prev, dst / "preview.mp4")
    return {"ok": True, "pasta_nome": amigavel(dst)}


# ------------------------------------------------------------------ 📡 MEUS FEEDS (vídeos novos do nicho, ordenados por views/hora)
from lib import feeds as FEEDS  # noqa: E402

_FEED_RODANDO = {}   # feed → job (não puxa o mesmo feed 2x ao mesmo tempo)


@app.get("/api/feeds")
def feeds_lista():
    out = []
    for f in FEEDS.listar():
        r = FEEDS.resultado(f["id"]) or {}
        jid = _FEED_RODANDO.get(f["id"])
        rodando = bool(jid and jid in JOBS and not JOBS[jid]["done"])
        out.append({**f, "quando": r.get("quando"), "n": r.get("total"), "fora": sum(1 for v in r.get("videos") or [] if v.get("fora_da_curva")),
                    "job": jid if rodando else None})
    return sorted(out, key=lambda f: f.get("criado") or 0)


@app.post("/api/feeds")
def feeds_salvar(data: dict = Body(...)):
    try:
        f = FEEDS.salvar(data)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {"ok": True, "feed": f}


@app.delete("/api/feeds/{fid}")
def feeds_apagar(fid: str):
    FEEDS.apagar(fid)
    return {"ok": True}


@app.get("/api/feeds/{fid}")
def feeds_get(fid: str):
    f = next((x for x in FEEDS.listar() if x["id"] == fid), None)
    if not f:
        raise HTTPException(404, "Feed não encontrado.")
    jid = _FEED_RODANDO.get(fid)
    return {"feed": f, "res": FEEDS.resultado(fid), "job": jid if (jid and jid in JOBS and not JOBS[jid]["done"]) else None}


@app.post("/api/feeds/{fid}/atualizar")
def feeds_atualizar(fid: str):
    f = next((x for x in FEEDS.listar() if x["id"] == fid), None)
    if not f:
        raise HTTPException(404, "Feed não encontrado.")
    jid = _FEED_RODANDO.get(fid)
    if jid and jid in JOBS and not JOBS[jid]["done"]:
        return {"job": jid}

    def job(prog):
        r = FEEDS.atualizar(fid, prog=prog)
        return {"feed": fid, "n": r["total"], "name": f["nome"]}   # resultado pequeno (o feed fica em .cache\feeds)
    r = start_job(job, tipo="feed", titulo=f"Feed: {f['nome'][:50]}", pesado=False)
    _FEED_RODANDO[fid] = r["job"]
    return r


# ------------------------------------------------------------------ 🎙 MINHAS VOZES (ouvir, clonar a sua, escolher a padrão)
from lib import vozes as VZ  # noqa: E402

VOZ_CACHE = CACHE_DIR / "vozes"
AUD_EXTS = (".mp3", ".wav", ".m4a", ".ogg", ".opus", ".flac", ".aac", ".webm") + VID_EXTS
FRASE_AMOSTRA = "Olá! Eu sou uma das vozes do Estúdio. Você sabia que o polvo tem três corações?"


def _voz_cache_nome(voz):
    return re.sub(r"[^A-Za-z0-9_-]+", "_", voz)[:80]


@app.get("/api/vozes")
def vozes_lista():
    a = AJ.ler()
    prontas = [v for v in ajustes_vozes(a.get("idioma") or "pt-BR") if v["id"] != "auto" and not v["id"].startswith("clone:")]
    for v in prontas:
        f = VOZ_CACHE / (_voz_cache_nome(v["id"]) + (".mp3" if v["id"].startswith("edge:") else ".wav"))
        v["amostra_url"] = f"/api/vozes/arq/cache/{f.name}" if f.exists() else None
    ok, motivo = VZ.motor_clone()
    from lib import tts as TTS
    cl = [{**v, "voz": "clone:" + v["id"], "teste_url": f"/api/vozes/arq/{v['id']}/teste.wav" if v.get("tem_teste") else None,
           "ref_url": f"/api/vozes/arq/{v['id']}/ref.wav"} for v in VZ.clones()]
    vs = [{k: x[k] for k in ("id", "nome", "idioma", "genero", "importada")} | {"ref_url": f"/api/vozes/arq/vs/{x['id']}.wav"} for x in VZ.voicestudio()]
    return {"padrao": a.get("voz"), "prontas": prontas, "clones": cl, "voicestudio": vs, "clone_ok": ok, "clone_motivo": motivo,
            "chatterbox": memo("tts_disp", TTS.disponiveis, ttl=60).get("chatterbox")}   # porta 8020 fechada leva ~2 s pra responder


@app.get("/api/vozes/arq/{a}/{b}")
def vozes_arquivo(a: str, b: str):
    if a == "cache":
        f = VOZ_CACHE / Path(b).name
    elif a == "vs":
        x = next((v for v in VZ.voicestudio() if v["id"] == Path(b).stem), None)
        f = Path(x["arquivo"]) if x else None
    else:
        f = VZ.VOZES / Path(a).name / Path(b).name if Path(b).name in ("teste.wav", "ref.wav") else None
    if not f or not f.exists():
        raise HTTPException(404)
    return FileResponse(f, headers={"Cache-Control": "no-cache"})


def _falar_amostra(voz, texto, saida: Path):
    from lib import tts as TTS
    motor, _, nome = voz.partition(":")
    tmp = saida.parent / ("_tmp_" + saida.stem)
    tmp.mkdir(parents=True, exist_ok=True)
    try:
        p, _ = TTS.falar(texto, tmp, motor, nome or None)
        if p.suffix.lower() == saida.suffix.lower():
            shutil.move(str(p), saida)
        else:
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(p), str(saida)], check=True, timeout=120, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return saida


@app.post("/api/vozes/amostra")
def vozes_amostra(data: dict = Body(...)):
    """Ouvir uma voz pronta: Microsoft sai na hora (~2 s); Qwen3/clone vira trabalho (placa de vídeo, 1 por vez)."""
    voz = str(data.get("voz") or "")
    texto = str(data.get("texto") or "").strip()[:400]
    if ":" not in voz:
        raise HTTPException(400, "Escolha uma voz.")
    VOZ_CACHE.mkdir(parents=True, exist_ok=True)
    ext = ".mp3" if voz.startswith("edge:") else ".wav"
    if texto:   # frase escrita pelo usuário: arquivo próprio (não sobrescreve a amostra padrão)
        f = VOZ_CACHE / (_voz_cache_nome(voz) + "-" + uuid.uuid4().hex[:6] + ext)
    else:
        f = VOZ_CACHE / (_voz_cache_nome(voz) + ext)
        if f.exists():
            return {"url": f"/api/vozes/arq/cache/{f.name}"}
    if voz.startswith("edge:"):
        try:
            _falar_amostra(voz, texto or FRASE_AMOSTRA, f)
        except Exception as e:
            raise HTTPException(500, "A voz da Microsoft não respondeu (precisa de internet): " + str(e)[:200])
        return {"url": f"/api/vozes/arq/cache/{f.name}?{int(time.time())}"}

    def job(prog):
        prog(10, "Gerando a amostra na placa de vídeo (a 1ª vez carrega o modelo, ~1 min)…")
        _falar_amostra(voz, texto or (VZ.FRASE_TESTE if voz.startswith("clone:") else FRASE_AMOSTRA), f)
        return {"amostra_url": f"/api/vozes/arq/cache/{f.name}?{int(time.time())}", "name": voz}
    return start_job(job, tipo="voz", titulo=f"Ouvir voz: {voz.split(':', 1)[1][:40]}", pesado=True)


@app.post("/api/vozes/subir")
async def vozes_subir(file: UploadFile = File(...)):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in AUD_EXTS:
        raise HTTPException(400, "Envie um áudio (mp3, wav, m4a…) ou um vídeo seu falando.")
    PEDIDOS_TMP.mkdir(exist_ok=True)
    dst = PEDIDOS_TMP / f"voz-{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:4]}{ext}"
    with open(dst, "wb") as fh:
        while True:
            ch = await file.read(4 << 20)
            if not ch:
                break
            fh.write(ch)
    d = probe(dst)
    if not d:
        dst.unlink(missing_ok=True)
        raise HTTPException(400, "Não consegui ler esse arquivo de áudio.")
    return {"arquivo_id": dst.name, "nome": file.filename, "dur": d}


@app.post("/api/vozes/clonar")
def vozes_clonar(data: dict = Body(...)):
    nome = str(data.get("nome") or "").strip()
    if not nome:
        raise HTTPException(400, "Dê um nome pra voz (ex.: Minha voz).")
    if not data.get("consentimento"):
        raise HTTPException(400, "Marque que a voz é sua (ou de quem te autorizou por escrito).")
    if data.get("caminho"):   # teste interno: áudio que já está no PC
        src = Path(str(data["caminho"]))
        if not src.exists():
            raise HTTPException(400, "Arquivo não encontrado.")
    else:
        src = PEDIDOS_TMP / Path(str(data.get("arquivo_id") or "")).name
        if not data.get("arquivo_id") or not src.exists():
            raise HTTPException(400, "Envie o áudio primeiro (e espere aparecer ✅).")
    ok, motivo = VZ.motor_clone()
    if not ok:
        raise HTTPException(400, "Clonar voz ainda não funciona neste PC: " + motivo)

    def job(prog):
        v = VZ.criar_clone(nome, src, prog=prog, inicio=float(data.get("inicio") or 0), consentimento=True)
        return {"name": v["nome"], "voz": "clone:" + v["id"]}
    return start_job(job, tipo="voz", titulo=f"Clonar voz: {nome[:40]}", pesado=True)


@app.post("/api/vozes/importar")
def vozes_importar(data: dict = Body(...)):
    try:
        v = VZ.importar_voicestudio(str(data.get("id") or ""))
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {"ok": True, "voz": "clone:" + v["id"], "nome": v["nome"]}


# ------------------------------------------------------------------ VOICESTUDIO (Ajustes): baixar/instalar + ajuda do Claude
from lib import vs_instalar as VSI  # noqa: E402


@app.get("/api/voicestudio")
def voicestudio_status():
    return {**VSI.status(), "claude": bool(_claude_exe())}


@app.post("/api/voicestudio/instalar")
def voicestudio_instalar():
    return start_job(lambda prog: VSI.instalar(prog), tipo="voicestudio", titulo="Instalando o VoiceStudio")


def _job_vs_ajuda(extra, prog):
    VSI.PASTA.mkdir(parents=True, exist_ok=True)
    VSI.log("=== Pedido de ajuda ao Claude ===")
    # sem bypassPermissions: só as ferramentas listadas, e o prompt limita o que mexer (ver vs_instalar.prompt_ajuda)
    r = _claude_rodar(VSI.PASTA, prog, "Claude olhando o log da instalação…", VSI.prompt_ajuda(extra),
                      perm_args=["--permission-mode", "acceptEdits", "--allowedTools", "Bash", "Read", "Glob", "Grep", "WebFetch", "Write", "Edit"])
    texto = str(r["fim"].get("result") or "").strip() or "O Claude terminou sem escrever um resumo. Veja o log abaixo."
    VSI.log("Claude terminou: " + texto[:300].replace("\n", " "))
    return {"texto": texto, "instalado": bool(VSI.achar_instalado()), "minutos": r.get("minutos")}


@app.post("/api/voicestudio/ajuda")
def voicestudio_ajuda(data: dict = Body(default={})):
    if not _claude_exe():
        raise HTTPException(400, "Falta o app do Claude neste PC (claude.ai/download).")
    return start_job(_job_vs_ajuda, str((data or {}).get("texto") or ""), tipo="voicestudio", titulo="Claude ajudando na instalação do VoiceStudio")


@app.post("/api/voicestudio/abrir")
def voicestudio_abrir():
    try:
        VSI.abrir()
    except Exception as e:
        raise HTTPException(400, str(e))
    return {"ok": True}


@app.delete("/api/vozes/{vid}")
def vozes_apagar(vid: str):
    VZ.apagar(vid)
    if AJ.ler().get("voz") == "clone:" + vid:
        AJ.salvar({"voz": "edge:pt-BR-ThalitaMultilingualNeural"})
    return {"ok": True}


@app.post("/api/vozes/padrao")
def vozes_padrao(data: dict = Body(...)):
    voz = str(data.get("voz") or "")
    if ":" not in voz and voz != "auto":
        raise HTTPException(400, "Voz inválida.")
    AJ.salvar({"voz": voz})
    return {"ok": True}


def _ollama_aquecer():
    """Deixa o modelo do Ollama carregado na placa de vídeo (keep_alive): a 1ª ideia/roteiro sai em segundos."""
    try:
        from lib import ollama as OL
        m = AJ.ler().get("modelo_ollama") or "qwen2.5:7b"
        if ":cloud" not in m and OL._no_ar():   # só se o Ollama já estiver ligado (não liga nada sozinho)
            OL.aquecer(m)
    except Exception:
        pass


def _aquecer():
    """Ao ligar o painel: já deixa lista, estilos e checklist calculados (a 1ª tela abre na hora)."""
    threading.Thread(target=_ollama_aquecer, daemon=True).start()
    # leve 01/11: + lista de vozes Microsoft (1ª abertura de 🎙 Vozes/Ajustes custava ~1,3 s de internet)
    for f in [globals().get(n) for n in ("projects", "estilos", "saude", "bombando", "estimativas", "_vozes_edge")]:   # estimativas fica mais abaixo no arquivo
        try:
            f()
        except Exception:
            pass


threading.Thread(target=_aquecer, daemon=True).start()


# ======================================================= SUGERIR IDEIAS (Ollama rápido)
@app.post("/api/sugerir-ideias")
def sugerir_ideias(data: dict = Body(...)):
    """Gera 5 ideias de vídeo com Ollama (grátis, 0 token Claude)."""
    contexto = str(data.get("contexto") or "").strip()
    formato = str(data.get("formato") or "longo").strip()
    nicho = str(data.get("nicho") or "").strip()
    estilo = str(data.get("estilo") or "").strip()
    aj = AJ.ler()
    modelo = aj["modelo_ollama"]

    dica_formato = "vídeo curto (short de 30-60 segundos)" if formato == "short" else "vídeo longo (5-30 minutos para YouTube)"
    prompt = f"""Gere exatamente 5 ideias de {dica_formato} para um canal faceless no YouTube.
{f'Nicho/tema do canal: {nicho}.' if nicho else ''}
{f'Estilo de edição: {estilo}.' if estilo else ''}
{f'Contexto extra: {contexto}.' if contexto else ''}

Regras:
- Cada ideia deve ser um TÍTULO chamativo de no máximo 12 palavras
- Ideias variadas: misture curiosidade, polêmica leve, listas e "por que"
- Português do Brasil, sem emoji, sem numeração
- Responda APENAS em JSON: {{"ideias": ["titulo1", "titulo2", "titulo3", "titulo4", "titulo5"]}}"""

    from lib import ollama as OL
    try:
        raw = OL.gerar(prompt, modelo, json_mode=True, temperatura=0.8, num_predict=400, timeout=120)
        d = json.loads(raw)
        ideias = d.get("ideias", [])[:5]
        if not ideias:
            raise ValueError("Nenhuma ideia gerada")
        return {"ideias": [str(i).strip() for i in ideias if str(i).strip()]}
    except Exception as e:
        # fallback: tenta parsear linhas soltas
        try:
            linhas = [l.strip().lstrip("0123456789.-) ").strip('"') for l in raw.split("\n") if l.strip() and len(l.strip()) > 5]
            if linhas:
                return {"ideias": linhas[:5]}
        except Exception:
            pass
        raise HTTPException(500, f"Ollama não respondeu: {str(e)[:200]}")


@app.post("/api/sugerir-nome-estilo")
def sugerir_nome_estilo(data: dict = Body(...)):
    """Dado um link de vídeo, sugere um nome curto pro estilo (via Ollama)."""
    url = str(data.get("url") or "").strip()
    if not url:
        raise HTTPException(400, "Cole o link do vídeo.")
    aj = AJ.ler()
    info = _ski_ref_info(url) if re.match(r"^https?://", url) else {}   # QA: a IA não abre link — passa título/canal reais
    dados = (f"Título: {info.get('titulo')} | Canal: {info.get('canal') or '?'} | Descrição: {(info.get('descricao') or '-')[:300]}"
             if info else f"Link: {url}")
    prompt = f"""Dados de um vídeo (YouTube/TikTok/Instagram):
{dados}
Sugira UM nome curto (2-4 palavras) em português do Brasil para o ESTILO DE EDIÇÃO desse vídeo (pelo tipo de canal/assunto).
Não use o título do vídeo, mas sim o estilo visual (ex: "Mapas ilustrados", "Documentário escuro", "Cartoon colorido", "Infográfico dourado").
Responda APENAS em JSON: {{"nome": "Nome do Estilo"}}"""
    from lib import ollama as OL
    try:
        raw = OL.gerar(prompt, aj["modelo_ollama"], json_mode=True, temperatura=0.5, num_predict=100, timeout=90)
        d = json.loads(raw)
        return {"nome": str(d.get("nome", "")).strip()[:50]}
    except Exception:
        return {"nome": ""}



# ------------------------------------------------------------------ 🤖 ESTILOS IA (skills do Claude Code: Moldura Pop, Jarvis, Kinetic…)
# O painel monta a pasta do vídeo (entrada/ + PEDIDO.md) e roda o Claude Code sozinho (claude -p), 1 por vez.
# Resultado: resultado.mp4 na raiz da pasta → o card em Meus vídeos fica ✅ e abre no editor como vídeo normal.
SKI_DIR = ROOT / "skills_ia"
SKILLS_HOME = Path.home() / ".claude" / "skills"
SKI_VEZ = threading.Semaphore(1)
SKI_PASTA = threading.Lock()
SKI_LIMITE_MIN = 120


def _ski_cat():
    try:
        cat = json.loads((SKI_DIR / "catalogo.json").read_text(encoding="utf-8"))
    except Exception:
        cat = {"skills": [], "ajudantes": [], "quiz": []}
    ids = {x["id"] for x in cat["skills"]}
    # baixadas = estilos achados/baixados pela clonagem (vão no pacote); pessoais = só deste PC (NUNCA vão no pacote)
    for pj in sorted((SKI_DIR / "baixadas").glob("*/painel.json")) + sorted((SKI_DIR / "pessoais").glob("*/painel.json")):
        try:
            x = json.loads(pj.read_text(encoding="utf-8-sig"))
            if x.get("id") and x["id"] not in ids and x.get("nome"):
                x.setdefault("emoji", "🧬"); x.setdefault("entrada", "texto"); x.setdefault("formato", "short")
                x.setdefault("quando", "Estilo clonado de um vídeo."); x.setdefault("exemplo", "")
                cat["skills"].append(x); ids.add(x["id"])
        except Exception:
            pass
    return cat


def _ski_fonte():
    """Pasta com as skills pra instalar (skills_ia\\fonte\\ ou o caminho escrito em skills_ia\\fonte.txt)."""
    cands = [SKI_DIR / "fonte"]
    try:
        cands.append(Path((SKI_DIR / "fonte.txt").read_text(encoding="utf-8").strip()))
    except Exception:
        pass
    return next((c for c in cands if str(c) and c.is_dir() and any(c.glob("*/SKILL.md"))), None)


def _claude_exe():
    """Acha o Claude Code (CLI) sozinho: PATH, instalações comuns e o que vem com o app Claude do Windows."""
    ov = os.environ.get("CLAUDE_EXE", "").strip().strip('"')   # escape manual: set CLAUDE_EXE=C:\caminho\claude.exe
    if ov and Path(ov).is_file():
        return ov
    w = shutil.which("claude")
    if w:
        return w
    # o painel pode ter sido aberto ANTES da instalação (PATH velho): lê o PATH atual do Windows (máquina + usuário)
    if os.name == "nt":
        try:
            import winreg
            partes = []
            for raiz, sub in ((winreg.HKEY_CURRENT_USER, "Environment"),
                              (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment")):
                try:
                    with winreg.OpenKey(raiz, sub) as k:
                        partes.append(os.path.expandvars(winreg.QueryValueEx(k, "Path")[0]))
                except OSError:
                    pass
            w = shutil.which("claude", path=os.pathsep.join(partes))
            if w:
                return w
        except Exception:
            pass
    cands = [Path.home() / ".local" / "bin" / "claude.exe",
             Path(os.environ.get("ProgramFiles", "")) / "nodejs" / "claude.cmd", Path(os.environ.get("ProgramFiles", "")) / "Claude" / "claude.exe",
             Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "claude" / "claude.exe",
             Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Links" / "claude.exe",
             Path.home() / "scoop" / "shims" / "claude.exe", Path("/opt/homebrew/bin/claude"), Path("/usr/local/bin/claude"), Path.home() / ".local" / "bin" / "claude",
             Path.home() / ".claude" / "local" / "claude.exe", Path.home() / ".claude" / "local" / "claude",
             Path(os.environ.get("APPDATA", "")) / "npm" / "claude.cmd"]
    # App Claude (desktop/Store): ...\Claude-Data\claude_xxx\claude-code\<versão>\<hash>\claude.exe  (pega a versão mais nova)
    achados = []
    for base in (os.environ.get("LOCALAPPDATA"), os.environ.get("APPDATA")):
        if not base:
            continue
        b = Path(base)
        for pat in ("Claude-Data/*/claude-code/*/*/claude.exe", "Claude-Data/*/claude-code/*/claude.exe",
                    "Claude/claude-code/*/claude.exe", "Claude/claude-code/*/*/claude.exe",
                    "Packages/Claude_*/LocalCache/Roaming/Claude/claude-code/*/claude.exe",
                    "Packages/Claude_*/LocalCache/Roaming/Claude/claude-code/*/*/claude.exe",
                    "AnthropicClaude/**/claude-code/**/claude.exe"):
            try:
                achados += [p for p in b.glob(pat) if p.is_file()]
            except Exception:
                pass
    achados.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    for c in cands + achados:
        if c.exists():
            return str(c)
    return None


FAV_JSON = ROOT / "favoritos.json"
FAV_DIR = ROOT / "static" / "favoritos"
FAV_PADRAO = ["mg-cel-boil", "mascote-apresentador", "mascote-yuri", "mg-pixel"]
FAV_LOCK = threading.Lock()


def _fav_ler():
    try:
        d = json.loads(FAV_JSON.read_text(encoding="utf-8"))
        return [str(x) for x in d.get("favoritos", [])]
    except Exception:
        return list(FAV_PADRAO)


def _fav_preview(sid):
    f = FAV_DIR / (Path(sid).name + ".mp4")
    return f"/static/favoritos/{f.name}?v={int(f.stat().st_mtime)}" if f.exists() else None


@app.post("/api/skills-ia/favorito")
def ski_favorito(body: dict):
    sid = str(body.get("id") or "").strip()
    if not sid:
        raise HTTPException(400, "id vazio")
    with FAV_LOCK:
        fav = [x for x in _fav_ler() if x != sid]
        if body.get("fav"):
            fav.append(sid)
        tmp = FAV_JSON.with_suffix(".tmp")
        tmp.write_text(json.dumps({"favoritos": fav}, ensure_ascii=False, indent=1), encoding="utf-8")
        os.replace(tmp, FAV_JSON)
    return {"favoritos": fav}


@app.get("/api/skills-ia")
def ski_lista():
    cat = _ski_cat()
    ok = lambda i: (SKILLS_HOME / i / "SKILL.md").exists()
    fonte = _ski_fonte()
    na_fonte = lambda i: bool(fonte and (fonte / i / "SKILL.md").exists()) or (SKI_DIR / "baixadas" / i / "SKILL.md").exists()
    fav = _fav_ler()
    sk = [{**s, "instalada": ok(s["id"]), "na_fonte": na_fonte(s["id"]),
           "favorito": s["id"] in fav, "fav_preview": _fav_preview(s["id"]),
           "preview_url": f"/api/skills-ia/preview/{s['id']}" if (SKI_DIR / "previews" / f"{s['id']}.mp4").exists() else None,
           "capa_url": f"/api/skills-ia/capa/{s['id']}?v={int((SKI_DIR / 'previews' / (s['id'] + '.mp4')).stat().st_mtime)}" if (SKI_DIR / "previews" / f"{s['id']}.mp4").exists() else None}
          for s in cat.get("skills", [])]
    return {"skills": sk, "quiz": cat.get("quiz", []), "claude": bool(_claude_exe()), "pode_instalar": any(x["na_fonte"] for x in sk),
            "ajudantes": [{"id": a, "instalada": ok(a)} for a in cat.get("ajudantes", [])],
            "ferramentas": cat.get("ferramentas", []),
            "fila": sum(1 for j in JOBS.values() if j.get("tipo") == "skill" and not j["done"])}


@app.get("/api/skills-ia/preview/{sid}")
def ski_preview(sid: str):
    f = SKI_DIR / "previews" / (Path(sid).name + ".mp4")
    if not f.exists():
        raise HTTPException(404)
    return FileResponse(f, media_type="video/mp4")


_SKI_CAPA_LOCKS = {}


def _ski_capa(sid):
    """Capa do card: quadro representativo do MEIO do vídeo (o começo costuma ser preto/fade). Refaz se o vídeo mudou."""
    v = SKI_DIR / "previews" / (Path(sid).name + ".mp4")
    c = SKI_DIR / "previews" / (Path(sid).name + ".jpg")
    if not v.exists():
        return None
    if c.exists() and c.stat().st_mtime >= v.stat().st_mtime:
        return c
    with _MEMO_LOCK:
        lk = _SKI_CAPA_LOCKS.setdefault(Path(sid).name, threading.Lock())
    with lk:   # leve 01/11: 2 pedidos da mesma capa → 1 ffmpeg só (antes rodavam juntos gravando o mesmo .jpg)
        if c.exists() and c.stat().st_mtime >= v.stat().st_mtime:
            return c
        return _ski_capa_gerar(v, c)


def _ski_capa_gerar(v, c):
    dur = probe(v) or 4
    for frac in (0.4, 0.6, 0.25, 0.8):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{dur * frac:.2f}", "-i", str(v), "-vf", "thumbnail=45,scale=540:-2",
                        "-frames:v", "1", "-q:v", "3", str(c)], capture_output=True, timeout=60,
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        if not c.exists():
            continue
        st = subprocess.run(["ffmpeg", "-v", "error", "-i", str(c), "-vf", "signalstats,metadata=print:key=lavfi.signalstats.YAVG", "-f", "null", "-"],
                            capture_output=True, text=True, timeout=30, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        m = re.search(r"YAVG=([\d.]+)", st.stdout + st.stderr)
        if not m or float(m.group(1)) > 28:   # claro o bastante (0-255)
            break
    return c if c.exists() else None


@app.get("/api/skills-ia/capa/{sid}")
def ski_capa(sid: str):
    c = _ski_capa(sid)
    if not c:
        raise HTTPException(404)
    return FileResponse(c, media_type="image/jpeg", headers={"Cache-Control": "max-age=86400"})


@app.post("/api/skills-ia/instalar")
def ski_instalar():
    """Copia as skills da pasta-fonte pro ~/.claude/skills (guarda config.json/sfx_pasta.txt de quem já tinha)."""
    fontes = [f for f in (_ski_fonte(), SKI_DIR / "baixadas") if f and f.is_dir()]
    srcs = sorted((d for f in fontes for d in f.iterdir() if (d / "SKILL.md").exists()), key=lambda d: d.name)
    if not srcs:
        raise HTTPException(400, "Não achei o pacote das skills neste PC. Coloque a pasta 'skills' do pacote em skills_ia\\fonte.")
    SKILLS_HOME.mkdir(parents=True, exist_ok=True)
    feitas = []
    for src in srcs:
        dst = SKILLS_HOME / src.name
        if dst.is_symlink() or (hasattr(dst, "is_junction") and dst.is_junction()):
            continue   # skill instalada como link/junction (repo do usuário): nunca apagar nem sobrescrever
        if dst.exists() and not (dst / ".do-painel").exists():
            continue   # skill que o usuário já tinha (não foi o painel que instalou): não troca pela cópia do pacote
        guarda = {n: (dst / n).read_bytes() for n in ("config.json", "sfx_pasta.txt") if (dst / n).exists()}
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        for n, b in guarda.items():
            (dst / n).write_bytes(b)
        (dst / ".do-painel").write_text("instalada pelo painel — o botão Instalar pode atualizar", encoding="utf-8")
        feitas.append(src.name)
    return {"ok": True, "instaladas": feitas}


def _ski_pedido_md(ped, sk, pasta, tem_video, tem_ref, audio=None):
    fmt = "vertical 1080x1920 (Reels/TikTok/Shorts)" if (ped.get("formato") or sk.get("formato")) != "longo" else "horizontal 1920x1080 (YouTube)"
    var = ped.get("variacao")
    L = [f"# PEDIDO DE VÍDEO — {ped['nome']}", "",
         "> Feito pelo painel Estúdio de Vídeos (aba 🤖 Estilos IA). O Claude roda SOZINHO, ninguém está olhando a conversa.", "",
         "## Estilo",
         f"- Use a skill **`{sk['id']}`** ({sk['nome']}): leia o SKILL.md dela e siga o fluxo inteiro dela.",
         "- Use também as skills ajudantes que existirem: `ganchos-reels` (gancho forte nos 1,5 s), `safe-zone-reels`, `marca-dagua`.",
         f"- Formato: {fmt}", "",
         "## Material",
         "- Vídeo do aluno (pessoa falando): `entrada/video" + ped.get("ext", ".mp4") + "`" if tem_video else
         "- Sem vídeo do aluno: criar o vídeo inteiro a partir do texto abaixo (narração TTS se a skill pedir voz).",
         ]
    if audio:
        L += [f"- NARRAÇÃO PRONTA (voz já gravada pelo aluno): `entrada/{audio}` — use EXATAMENTE este áudio como locução do vídeo inteiro "
              "(não gere TTS, não regrave, não corte frases). O texto abaixo é o roteiro dele: transcreva o áudio com tempos e sincronize "
              "cenas, textos e legenda com a fala. A duração do vídeo = duração do áudio (+ respiro curto no fim)."]
    if not audio and not tem_video:
        L += [_tts_instrucao(ped.get("voz"), pasta)]
    if tem_ref:
        L += ["- Vídeo de REFERÊNCIA pra copiar: `entrada/ref.mp4` — assista (frames + transcrição) e copie o gancho, o ritmo, a estrutura "
              "e o tipo de cena, MAS no estilo da skill e sem copiar o texto palavra por palavra."]
    fixo = bool(ped.get("texto_fixo") and ped.get("texto") and not tem_video and not audio)
    L += ["", "## Conteúdo",
          (f"- NARRAÇÃO APROVADA pelo aluno (texto fixo):\n\n{ped.get('texto')}\n\n"
           "- ⚠ Use EXATAMENTE este texto como fala, palavra por palavra. NÃO reescreva, não resuma, não acrescente nem tire frases "
           "(só pode ajustar a pontuação pra voz ler bem). O aluno já revisou e aprovou." if fixo else
           f"- Tema / copy:\n\n{ped.get('texto') or '(sem texto — usar só o que é falado no vídeo)'}\n"),
          f"- Duração alvo: ~{int(ped.get('duracao') or 45)} segundos" + (" (ou a duração do vídeo do aluno)" if tem_video else ""),
          f"- Idioma: {ped.get('idioma') or 'português do Brasil'}",
          f"- Marca d'água: {('@' + ped['marca'].lstrip('@')) if ped.get('marca') else 'nenhuma'}"]
    if var and fixo:
        L += [f"- Esta é a VERSÃO {var[0]} de {var[1]}: o texto é o MESMO (aprovado) — varie só o visual (cores, cenas, abertura visual)."]
    elif var:
        L += [f"- Esta é a VERSÃO {var[0]} de {var[1]} do mesmo tema: use um gancho e uma abertura DIFERENTES das outras versões "
              f"(versão 1 = gancho de curiosidade, 2 = de dor/erro, 3 = de número/lista, 4 = de polêmica, 5 = de história)."]
    if ped.get("obs"):
        L += [f"- Observações do aluno: {ped['obs']}"]
    L += ["", "## Regras (rodando pelo painel, sem ninguém olhando)",
          "- NÃO faça perguntas. Quando a skill mandar perguntar ou escolher, escolha o padrão mais bonito e anote a escolha em `DECISOES.md`.",
          "- Instale sozinho o que faltar (ffmpeg, pip, npm, Blender, modelos) sem pedir autorização.",
          "- Trabalhe só dentro desta pasta. Não apague a pasta `entrada/`.",
          "- NÃO coloque logo, assinatura ou nome do autor da skill (ex.: \"AI LAB\", \"AI LAB/ motion\") em nenhum lugar do vídeo; a única marca permitida é a marca d'água do aluno, se ele pediu.",
          "- No fim, salve o vídeo final como **`resultado.mp4`** na raiz desta pasta (mp4 H.264 + AAC).",
          f"- Pasta: `{pasta}`"]
    return "\n".join(L)


def _ski_progresso(ev, n):
    """Evento do claude --output-format stream-json → frase curta pro usuário."""
    for c in (ev.get("message") or {}).get("content") or []:
        if c.get("type") != "tool_use":
            continue
        nome, inp = c.get("name") or "", c.get("input") or {}
        if nome == "Bash":
            return "Claude: " + (inp.get("description") or "rodando um comando")[:90]
        if nome in ("Write", "Edit"):
            return "Claude: escrevendo " + Path(str(inp.get("file_path") or "")).name
        if nome == "Read":
            return "Claude: lendo " + Path(str(inp.get("file_path") or "")).name
        if nome == "Skill":
            return "Claude: abrindo o estilo " + str(inp.get("skill") or "")
        return f"Claude: {nome} (passo {n})"
    return None


def _ski_resultado(pasta: Path):
    f = pasta / "resultado.mp4"
    if f.exists():
        return f
    cands = [x for x in pasta.rglob("*.mp4") if "entrada" not in x.relative_to(pasta).parts and "node_modules" not in x.parts
             and x.stat().st_size > 50_000]
    if not cands:
        return None
    best = max(cands, key=lambda x: x.stat().st_mtime)
    shutil.copy2(best, f)
    return f


def _claude_rodar(pasta: Path, prog, msg_ini, prompt, cwd=None, perm_args=None):
    """Roda o Claude Code sozinho (claude -p) dentro da pasta, 1 por vez no PC. Progresso = passos do Claude."""
    exe = _claude_exe()
    if not exe:
        raise RuntimeError("Falta o app do Claude neste PC (claude.ai/download).")
    prog(6, "Na fila do Claude (faz 1 vídeo por vez)…")
    J = prog.job
    while not SKI_VEZ.acquire(timeout=2):
        prog(6, "Na fila do Claude (faz 1 vídeo por vez)…")
    t0 = time.time()
    log = open(pasta / "claude-log.jsonl", "w", encoding="utf-8")
    try:
        prog(8, msg_ini)
        # Modelo do Claude Code nos pedidos: padrão "sonnet" (bem mais barato que o Fable). Troque com a variável
        # ESTUDIO_CLAUDE_MODELO = sonnet | opus | haiku (ou um nome completo, ex.: claude-sonnet-5-5).
        _mod = (os.environ.get("ESTUDIO_CLAUDE_MODELO") or AJ.ler().get("modelo_claude") or "sonnet").strip()
        cmd = [exe, "-p", prompt, "--model", _mod, "--output-format", "stream-json", "--verbose", *(perm_args or ["--permission-mode", "bypassPermissions"])]
        env = AJ.env_chaves({**os.environ, "PYTHONIOENCODING": "utf-8"})   # chaves do ⚙ Ajustes (Gemini, ElevenLabs, Pexels…)
        p = subprocess.Popen(cmd, cwd=str(cwd or pasta), stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                             encoding="utf-8", errors="replace", env=env, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        J["_proc"] = p
        vigia = threading.Timer(SKI_LIMITE_MIN * 60, lambda: _matar(p))
        vigia.daemon = True
        vigia.start()
        n, fim, resto = 0, {}, []
        try:
            for line in p.stdout:
                log.write(line)
                s = line.strip()
                if not s.startswith("{"):
                    resto = (resto + [s])[-10:]
                    continue
                try:
                    ev = json.loads(s)
                except Exception:
                    continue
                if ev.get("type") == "result":
                    fim = ev
                    continue
                frase = _ski_progresso(ev, n + 1)
                if frase:
                    n += 1
                    prog(min(95, 8 + 87 * (1 - pow(2.718, -n / 45))), frase)
        except Cancelado:
            _matar(p)
            raise
        finally:
            vigia.cancel()
        p.wait()
        J["_proc"] = None
        if J["_cancel"]:
            raise Cancelado()
    finally:
        log.close()
        SKI_VEZ.release()
    return {"fim": fim, "n": n, "resto": resto, "minutos": round((time.time() - t0) / 60, 1)}


SKI_FALHAS = {}   # (skill, título, variação) → pasta da última tentativa que não gerou vídeo


def job_skill(ped, sk, prog):
    OUT = out_dir()
    titulo = (ped.get("texto") or ped.get("video_nome") or sk["nome"]).strip().splitlines()[0][:60] or sk["nome"]
    sig = (sk["id"], titulo, tuple(ped.get("variacao") or ()))
    with SKI_PASTA:   # lote: vários trabalhos começam juntos → um número por pasta
        antiga = SKI_FALHAS.get(sig)
        if antiga and Path(antiga).is_dir() and not _ski_resultado(Path(antiga)):
            pasta = Path(antiga)   # "Tentar de novo" depois de uma falha: reaproveita a pasta (não cria uma 2ª pasta vazia)
            nn = int(re.match(r"\d+", pasta.name).group(0)) if re.match(r"\d+", pasta.name) else proximo_numero(OUT)
        else:
            nn = proximo_numero(OUT)
            pasta = OUT / (f"{nn:02d}-ia-{slug(sk['id'], 20)}-{slug(titulo, 28)}" + (f"-v{ped['variacao'][0]}" if ped.get("variacao") else ""))
        (pasta / "entrada").mkdir(parents=True, exist_ok=True)
        SKI_FALHAS[sig] = str(pasta)
    nome = re.sub(r'[<>:"/\\|?*]', "", f"{nn:02d} - {datetime.now().strftime('%d-%m-%Y')} - {(ped.get('canal') or 'IA').upper()} - {titulo}")[:200]
    ped["nome"] = nome
    tem_video = False
    if ped.get("arquivo_id"):
        a = PEDIDOS_TMP / Path(ped["arquivo_id"]).name
        if a.exists():
            ped["ext"] = a.suffix.lower()
            shutil.copy2(a, pasta / "entrada" / ("video" + ped["ext"]))
            tem_video = True
    audio = None
    if ped.get("audio_id"):
        a = PEDIDOS_TMP / Path(ped["audio_id"]).name
        if a.exists():
            audio = "narracao" + a.suffix.lower()
            shutil.copy2(a, pasta / "entrada" / audio)
            ped["duracao"] = round(probe(a) or ped.get("duracao") or 45)
    tem_ref = False
    if ped.get("ref"):
        prog(4, "Baixando o vídeo de referência…")
        try:
            ok, _ = _baixar_ref(ped["ref"], pasta / "entrada" / "ref.mp4")
            tem_ref = bool(ok)
        except Exception:
            tem_ref = False
    md = _ski_pedido_md(ped, sk, pasta, tem_video, tem_ref, audio)
    (pasta / "PEDIDO.md").write_text(md, encoding="utf-8")
    vert = (ped.get("formato") or sk.get("formato")) != "longo"
    edit = {"version": 1, "name": nome, "canvas": {"w": 1080 if vert else 1920, "h": 1920 if vert else 1080, "fps": 30, "bg": "#000000"},
            "duration": float(ped.get("duracao") or 45), "template": "generic", "estilo": f"🤖 {sk['nome']}",
            "referencia": {"video": ped["ref"]} if ped.get("ref") else {},
            "pedido": {"skill": sk["id"], "tema": ped.get("texto", "")[:500], "criado": datetime.now().isoformat(timespec="seconds"),
                       "arquivo": "PEDIDO.md"},
            "audio": {}, "tracks": [{"id": "fundo", "name": "Vídeo"}, {"id": "textos", "name": "Textos"}], "items": []}
    (pasta / "edit.json").write_text(json.dumps(edit, ensure_ascii=False, indent=1), encoding="utf-8")
    memo_limpar()
    msg = f"faz o vídeo do PEDIDO.md em {pasta}"
    base = {"pid": pid_of(pasta), "folder": str(pasta), "name": nome, "mensagem_claude": msg}
    exe = _claude_exe()
    if ped.get("so_pedido") or not exe:
        prog(100, "Pedido criado!")
        SKI_FALHAS.pop(sig, None)
        return {**base, "rendered": False, "precisa_claude": True, "sem_claude": not exe}

    r = _claude_rodar(pasta, prog, f"Claude abrindo o estilo {sk['nome']}…",
                      "Leia o PEDIDO.md desta pasta e faça o vídeo exatamente como está pedido, usando a skill indicada. "
                      "Você está rodando sozinho pelo painel: não faça perguntas, decida e siga até salvar resultado.mp4.")
    fim, n, resto, minutos = r["fim"], r["n"], r["resto"], r["minutos"]
    us = fim.get("usage") or {}
    tok = sum(int(us.get(k) or 0) for k in ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
    rel = {"ferramenta_ia": f"Claude Code + skill {sk['id']}", "minutos": minutos, "tokens": tok or None,
           "custo_usd": fim.get("total_cost_usd"), "passos": n, "observacoes": str(fim.get("result") or "")[:1500]}
    (pasta / "RELATORIO.json").write_text(json.dumps(rel, ensure_ascii=False, indent=1), encoding="utf-8")
    vid = _ski_resultado(pasta)
    if not vid:
        raise RuntimeError("O Claude terminou mas não salvou o vídeo.\n" + (str(fim.get("result") or "") or "\n".join(resto))[-3000:]
                           + "\n\n(Clique em 🔁 Tentar de novo. Detalhes técnicos: claude-log.jsonl na pasta do vídeo.)")
    info = probe_full(vid) or {}
    edit.update(duration=float(info.get("dur") or edit["duration"]),
                items=[{"id": "v1", "type": "video", "track": "fundo", "start": 0, "dur": float(info.get("dur") or edit["duration"]),
                        "props": {"src": "resultado.mp4", "fill": True, "fit": "cover", "volume": 1}}])
    if info.get("w") and info.get("h"):
        edit["canvas"].update(w=int(info["w"]), h=int(info["h"]))
    (pasta / "edit.json").write_text(json.dumps(edit, ensure_ascii=False, indent=1), encoding="utf-8")
    memo_limpar()
    prog(100, f"Pronto em {minutos} min!")
    SKI_FALHAS.pop(sig, None)
    return {**base, "rendered": True, "precisa_claude": False}


@app.post("/api/skills-ia/pedido")
def ski_pedido(data: dict = Body(...)):
    """Um ou vários vídeos (lote) numa skill. itens=[{texto, arquivo_id, video_nome}], versoes=1..5 por item."""
    g = lambda k: str(data.get(k) or "").strip()
    sk = next((s for s in _ski_cat().get("skills", []) if s["id"] == g("skill")), None)
    if not sk:
        raise HTTPException(400, "Escolha um estilo.")
    if not (SKILLS_HOME / sk["id"] / "SKILL.md").exists():
        raise HTTPException(400, f"O estilo {sk['nome']} não está instalado neste PC. Clique em ⬇ Instalar skills.")
    itens = [i for i in (data.get("itens") or []) if str(i.get("texto") or "").strip() or i.get("arquivo_id") or i.get("audio_id")]
    if not itens:
        raise HTTPException(400, "Envie seu vídeo ou escreva o tema/copy." if sk["entrada"] != "texto" else "Escreva o tema ou a copy do vídeo.")
    if sk["entrada"] == "video" and any(not i.get("arquivo_id") for i in itens):
        raise HTTPException(400, f"{sk['nome']} edita um vídeo seu falando — envie o vídeo.")
    for i in itens:
        if i.get("arquivo_id"):
            _arquivo(i["arquivo_id"])
        if i.get("audio_id") and not (PEDIDOS_TMP / Path(str(i["audio_id"])).name).exists():
            raise HTTPException(400, "Envie a narração de novo (e espere aparecer ✅).")
    ref = g("ref")
    if ref and not re.match(r"^https?://\S+\.\S+", ref):
        raise HTTPException(400, "Link de referência inválido — cole o link completo (começa com https://).")
    try:
        versoes = max(1, min(5, int(data.get("versoes") or 1)))
        dur = float(data.get("duracao") or 45)
    except Exception:
        raise HTTPException(400, "Número inválido.")
    if len(itens) * versoes > 30:
        raise HTTPException(400, "Máximo 30 vídeos por vez.")
    jobs = []
    for it in itens:
        for v in range(1, versoes + 1):
            ped = {"texto": str(it.get("texto") or "").strip(), "arquivo_id": it.get("arquivo_id"), "video_nome": it.get("video_nome") or "",
                   "audio_id": it.get("audio_id"), "voz": g("voz"), "formato": g("formato") if g("formato") in ("short", "longo") else "",
                   "ref": ref, "marca": g("marca"), "canal": g("canal"), "duracao": dur, "obs": g("obs"), "idioma": g("idioma"),
                   "so_pedido": bool(data.get("so_pedido")), "variacao": (v, versoes) if versoes > 1 else None,
                   "texto_fixo": bool(data.get("texto_fixo"))}
            tit = (ped["texto"].splitlines()[0][:50] if ped["texto"] else ped["video_nome"][:50]) or sk["nome"]
            jobs.append(start_job(job_skill, ped, sk, tipo="skill", titulo=f"🤖 {sk['nome']} · {tit}" + (f" (v{v})" if versoes > 1 else ""))["job"])
    return {"jobs": jobs, "n": len(jobs), "claude": bool(_claude_exe())}



SKI_REF_CACHE = {}


def _ski_ref_info(url):
    """Título, descrição e canal de um vídeo (yt-dlp, 45 s). Cacheado por link."""
    if url in SKI_REF_CACHE:
        return SKI_REF_CACHE[url]
    info = {}
    try:
        out = subprocess.run([*RYT.cmd(),"--no-warnings", "--skip-download", "--no-playlist", "--print",
                              "%(title)s␞%(channel,uploader)s␞%(description).600s", url],
                             capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=45,
                             creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)).stdout.strip()
        p = out.split("␞")
        if len(p) >= 3 and p[0] and p[0] != "NA":
            info = {"titulo": p[0].strip(), "canal": p[1].strip(), "descricao": " ".join(p[2].split())[:600]}
    except Exception:
        pass
    SKI_REF_CACHE[url] = info
    return info


@app.post("/api/skills-ia/ideias")
def ski_ideias(data: dict = Body(...)):
    """8 ideias de tema pro estilo escolhido (Ollama local, grátis). Com ref → temas parecidos com aquele vídeo."""
    g = lambda k: str(data.get(k) or "").strip()
    sk = next((s for s in _ski_cat().get("skills", []) if s["id"] == g("skill")), None)
    longo = g("formato") == "longo"
    if not sk:   # chamado das outras telas (Shorts, Vídeo com imagens, Copiar…) sem estilo de skill
        sk = {"id": "", "nome": "vídeo longo do YouTube" if longo else "vídeo curto vertical",
              "quando": "canal faceless (sem aparecer), narração + imagens/animação", "entrada": "texto"}
    assunto = g("assunto")[:200]
    ref, nicho, evitar = g("ref"), g("nicho")[:120], [str(x)[:120] for x in (data.get("evitar") or [])][:30]
    info = _ski_ref_info(ref) if ref else {}
    if ref and not info:
        raise HTTPException(400, "Não consegui ler esse link. Confira se o vídeo é público (YouTube, TikTok ou Instagram).")
    aj = AJ.ler()
    tipo = ("temas de vídeo LONGO pro YouTube (8 a 20 minutos), canal sem aparecer" if longo and not sk["id"] else
            "temas pra pessoa GRAVAR falando pra câmera (ela mesma vai falar)" if sk["entrada"] == "video" else
            "historinhas infantis curtas (personagem + problema + lição)" if sk["id"] == "cartoon" else
            "temas de vídeo curto vertical (Reels/TikTok/Shorts) feitos só com animação e narração")
    if assunto and not info:
        info_assunto = f"O aluno quer um vídeo sobre: “{assunto}”. TODOS os temas têm que ser sobre ISSO (ângulos diferentes do mesmo assunto)."
    base = (f"O aluno quer COPIAR este vídeo que deu certo:\n- Título: {info['titulo']}\n- Canal: {info.get('canal') or '?'}\n"
            f"- Descrição: {info.get('descricao') or '-'}\nGere temas PARECIDOS (mesmo assunto/ângulo/emoção que fez ele dar certo), "
            "mas com título e abordagem próprios — nada de copiar o título.") if info else (info_assunto if assunto else "Gere temas NOVOS com chance alta de viralizar agora.")
    prompt = f"""Você é roteirista de vídeos virais. Estilo do vídeo: {sk['nome']} — {sk['quando']}
Gere exatamente 8 {tipo}.
{f'Nicho do canal: {nicho}.' if nicho else ('Nicho: o MESMO assunto do vídeo copiado (não misture outros nichos).' if info or assunto else 'Nicho livre (dinheiro, tecnologia/IA, curiosidades, psicologia, produtividade, saúde).')}
{base}
{('Não repita estes: ' + ' | '.join(evitar)) if evitar else ''}

Regras:
- "titulo": tema claro e chamativo, até 12 palavras
- "gancho": a primeira frase do vídeo (até 14 palavras), que prende nos 2 primeiros segundos
- variar: curiosidade, erro comum, lista com número, polêmica leve, antes/depois, história; não cite ano nem data
- {AJ.idioma_llm(aj.get('idioma'))}, sem emoji, sem numeração, nada de fato inventado
Responda APENAS JSON: {{"ideias": [{{"titulo": "...", "gancho": "..."}}]}}"""
    from lib import ollama as OL
    raw = ""
    try:
        for m in dict.fromkeys([aj["modelo_ollama"], "qwen2.5:7b"]):   # o melhor em português, se estiver instalado
            try:
                raw = OL.gerar(prompt, m, json_mode=True, temperatura=0.9, num_predict=900, timeout=150)
                break
            except urllib.error.HTTPError:
                continue
        d = json.loads(raw)
        lst = d.get("ideias") if isinstance(d, dict) else d
        ideias = []
        for x in lst or []:
            if isinstance(x, dict) and str(x.get("titulo") or "").strip():
                ideias.append({"titulo": str(x["titulo"]).strip()[:140], "gancho": str(x.get("gancho") or "").strip()[:180]})
            elif isinstance(x, str) and x.strip():
                ideias.append({"titulo": x.strip()[:140], "gancho": ""})
        if not ideias:
            raise ValueError("vazio")
    except Exception as e:
        raise HTTPException(500, f"A IA do PC (Ollama) não respondeu agora. Confira em ⚙ Ajustes se ela está ligada. ({str(e)[:120]})")
    return {"ideias": ideias[:8], "ref": info or None}



# ------------------------------------------------------------------ ✍️ ASSISTENTE DE ROTEIRO (tema → roteiro pronto, IA do PC ou Claude)
RT_TIPOS = {
    "historia": "Conte como uma HISTÓRIA: personagem, situação, conflito, virada e desfecho. Nada de lista nem tom de aula.",
    "primeira": "Narrado em PRIMEIRA PESSOA, como se tivesse acontecido comigo (\"eu\", \"minha\"), tom de desabafo/conversa sincera.",
    "gancho": "Gancho MUITO forte na primeira frase (quebra de padrão, curiosidade aberta) e micro-ganchos a cada ~20 segundos pra segurar até o fim.",
    "cta": "O ÚLTIMO pedido do vídeo DEVE ser: comentar exatamente a palavra “{palavra}” (amarrado ao assunto, nunca jogado do nada). Não troque essa palavra por outra pergunta.",
    "lista": "Formato LISTA/curiosidades: itens numerados na fala (\"número um...\"), do mais fraco pro mais forte, o melhor por último.",
    "tutorial": "Formato PASSO A PASSO prático: cada passo claro, curto e fácil de aplicar hoje.",
}


def _rt_prompt(tema, dur, tipos, palavra, idioma):
    palavras = max(60, int(dur * 2.5))
    regras = "\n".join("- " + RT_TIPOS[t].format(palavra=palavra or "EU QUERO") for t in tipos if t in RT_TIPOS)
    return f"""Escreva o ROTEIRO de narração de um vídeo sobre: {tema}
TAMANHO OBRIGATÓRIO: entre {int(palavras * 0.9)} e {int(palavras * 1.1)} palavras (duração {int(dur)} segundos a 150 palavras por minuto). Conte as palavras: passar de {int(palavras * 1.15)} ou ficar abaixo de {int(palavras * 0.85)} é erro. Corte assunto em vez de estourar o tamanho.
{regras}
Regras sempre:
- Narrativa linear, sem repetir a mesma ideia com outras palavras; frases curtas, coloquiais, tom de gente falando (nada robótico).
- Primeiros 3 segundos magnéticos, zero saudação ("olá", "fala galera").
- Nada de fato, número, nome ou data inventados: se não tiver certeza, fale de forma geral.
- Idioma: {idioma}. Sem emoji, sem títulos, sem marcação, sem colchetes, sem "narrador:" — SÓ o texto que a voz vai ler.
- NÃO escreva nenhuma observação, aviso, nota ou explicação antes ou depois do roteiro: a resposta inteira será lida em voz alta."""


def _rt_limpar(t):
    t = str(t or "")
    t = re.split(r"\n\s*(?:-{3,}|\*{3,}|_{3,})\s*\n", t, maxsplit=1)[0]   # Claude às vezes põe "---" e uma nota depois do roteiro
    t = re.sub(r"^\s*(#+.*|\*\*.*\*\*\s*|roteiro:?|narra(ção|dor):?)\s*$", "", t, flags=re.I | re.M)
    return re.sub(r"\n{3,}", "\n\n", t.replace("**", "")).strip()


def _claude_texto(exe, prompt, prog, modelo):
    """Roda o Claude uma vez e devolve (texto, custo). Aceita resposta em JSON ou em texto puro."""
    pasta = CACHE_DIR / "roteiros-claude"
    pasta.mkdir(parents=True, exist_ok=True)
    cmd = [exe, "-p", "--output-format", "json", "--model", modelo, "--allowedTools", "WebSearch,WebFetch"]   # o pedido vai pela entrada padrão: pela linha de comando do Windows só chegava a 1ª linha
    p = subprocess.Popen(cmd, cwd=str(pasta), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                         encoding="utf-8", errors="replace", env=AJ.env_chaves({**os.environ, "PYTHONIOENCODING": "utf-8"}),
                         creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    prog.job["_proc"] = p
    try:
        out, _ = p.communicate(input=prompt, timeout=900)
    except subprocess.TimeoutExpired:   # communicate não mata sozinho → o claude.exe ficava vivo pra sempre
        _matar(p)
        p.communicate()
        raise RuntimeError("O Claude passou de 15 minutos sem responder. Tente de novo ou use a IA do PC.")
    finally:
        prog.job["_proc"] = None
    for cand in [out.strip()] + [l for l in reversed(out.strip().splitlines()) if l.strip().startswith(("{", "["))]:
        try:
            r = json.loads(cand)
        except Exception:
            continue
        if isinstance(r, list):   # versões novas podem devolver uma lista de eventos
            r = next((x for x in reversed(r) if isinstance(x, dict) and x.get("type") == "result"), {})
        if isinstance(r, dict) and r.get("result"):
            return r.get("result") or "", r.get("total_cost_usd")
    plano = out.strip()   # às vezes devolve o roteiro em texto puro (sem JSON)
    if len(plano) > 200 and not plano.startswith(("{", "[")) and "Error" not in plano[:80]:
        return plano, None
    raise RuntimeError("O Claude não respondeu direito: " + out[-500:])


def job_roteiro_ia(d, prog):   # QA: chamava-se job_roteiro e apagava o do "Roteiro pronto" (mesmo nome) → aquela tela dava erro
    aj = AJ.ler()
    prompt = _rt_prompt(d["tema"], d["dur"], d["tipos"], d["palavra"], AJ.idioma_llm(aj.get("idioma")))
    if d["motor"] == "claude":
        exe = _claude_exe()
        if not exe:
            raise RuntimeError("Falta o app do Claude neste PC (claude.ai/download). Use a IA do PC (grátis).")
        modelo = (os.environ.get("ESTUDIO_CLAUDE_MODELO") or aj.get("modelo_claude") or "sonnet").strip()
        alvo = max(60, int(d["dur"] * 2.5))
        prog(15, "O Claude está pesquisando e escrevendo…")
        txt, custo = _claude_texto(exe, prompt + "\n\nSe precisar, pesquise fatos rápidos na internet antes de escrever. Responda SÓ com o roteiro.", prog, modelo)
        txt = _rt_limpar(txt)
        for tent in range(2):   # o Claude costuma errar o tamanho: pede pra ajustar até ficar dentro de ±25%
            n = len(txt.split())
            if alvo * 0.75 <= n <= alvo * 1.25:
                break
            prog(70 + tent * 12, f"Ajustando o tamanho ({n} → ~{alvo} palavras)…")
            ajuste = (f"Abaixo está um roteiro de narração com {n} palavras. Reescreva-o com {alvo} palavras (aceito de {int(alvo * 0.9)} a {int(alvo * 1.1)}), "
                      f"{'cortando os trechos menos importantes' if n > alvo else 'desenvolvendo mais os pontos principais, sem inventar fatos'}, mantendo o gancho inicial, "
                      "o tom, a ordem e o fechamento. Responda SÓ com o novo roteiro, sem nota nem comentário.\n\n" + txt)
            t2, c2 = _claude_texto(exe, ajuste, prog, modelo)
            t2 = _rt_limpar(t2)
            if abs(len(t2.split()) - alvo) < abs(n - alvo):
                txt = t2
            custo = ((custo or 0) + (c2 or 0)) if (custo or c2) else None
        prog(100, "Pronto!")
        return {"roteiro": txt, "motor": "claude", "custo_usd": custo}
    from lib import ollama as OL
    palavras = max(60, int(d["dur"] * 2.5))
    if palavras > 900:   # 6 min ou mais: escreve em partes (uma chamada só estoura a memória do modelo e sai curto)
        prog(10, f"A IA do seu PC está escrevendo em partes (~{palavras} palavras; roteiro longo leva vários minutos)…")
        regras = "\n".join("- " + RT_TIPOS[t].format(palavra=d["palavra"] or "EU QUERO") for t in d["tipos"] if t in RT_TIPOS)
        regras += ("\n- Narrativa linear, sem repetir a mesma ideia; frases curtas e coloquiais; zero saudação."
                   "\n- Nada de fato, número, nome ou data inventados: se não tiver certeza, fale de forma geral."
                   f"\n- Idioma: {AJ.idioma_llm(aj.get('idioma'))}. Sem emoji, sem títulos, sem marcação, sem colchetes: SÓ o texto que a voz vai ler.")
        r = None
        for m in dict.fromkeys([aj["modelo_ollama"], "qwen2.5:7b"]):
            try:
                r = OL.roteiro_longo(d["tema"], palavras, "", "", modelo=m, regras=regras, progresso=prog)
                break
            except urllib.error.HTTPError:
                continue
        if not r:
            raise RuntimeError("A IA do PC não escreveu nada. Tente de novo ou use o Claude.")
        prog(100, "Pronto!")
        return {"roteiro": _rt_limpar(r["roteiro"]), "motor": "pc"}
    prog(20, "A IA do seu PC está escrevendo (grátis)…")
    raw = ""
    for m in dict.fromkeys([aj["modelo_ollama"], "qwen2.5:7b"]):
        try:
            raw = OL.gerar(prompt, m, temperatura=0.8, num_predict=max(900, int(d["dur"] * 2.5 * 2.2)), timeout=900)
            break
        except urllib.error.HTTPError:
            continue
    if not raw.strip():
        raise RuntimeError("A IA do PC não escreveu nada. Tente de novo ou use o Claude.")
    prog(100, "Pronto!")
    return {"roteiro": _rt_limpar(raw), "motor": "pc"}


@app.post("/api/roteiro/gerar")
def roteiro_gerar(data: dict = Body(...)):
    g = lambda k: str(data.get(k) or "").strip()
    if not g("tema"):
        raise HTTPException(400, "Escolha um tema (ou escreva o assunto).")
    try:
        dur = max(15.0, min(3600.0, float(data.get("duracao") or 60)))
    except Exception:
        dur = 60.0
    tipos = [t for t in (data.get("tipos") or []) if t in RT_TIPOS] or ["gancho"]
    d = {"tema": g("tema")[:300], "dur": dur, "tipos": tipos, "palavra": g("palavra")[:40], "motor": "claude" if g("motor") == "claude" else "pc"}
    return start_job(job_roteiro_ia, d, tipo="roteiro", titulo="✍️ Roteiro · " + d["tema"][:50])



# ======================================================= 🩺 DIAGNÓSTICO (verde/vermelho de cada peça + como resolver)
def _versao_de(cmd, timeout=10):
    """(caminho, versão) de um programa; (None, None) se não existe."""
    exe = cmd[0] if os.path.isabs(cmd[0]) else shutil.which(cmd[0])
    if not exe or not os.path.exists(exe):
        return None, None
    try:
        o = subprocess.run([exe] + cmd[1:], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout,
                           stdin=subprocess.DEVNULL, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        m = re.search(r"(\d+(?:\.\d+)+)", (o.stdout or "") + (o.stderr or ""))
        return exe, (m.group(1) if m else "?")
    except Exception:
        return exe, "?"


def _diag_itens():
    from concurrent.futures import ThreadPoolExecutor
    aj = AJ.ler()
    W = "Rode o INSTALAR.bat (na pasta do painel) — ele instala o que falta sozinho."
    with ThreadPoolExecutor(6) as ex:
        f_node = ex.submit(_versao_de, ["node", "--version"])
        f_ff = ex.submit(_versao_de, ["ffmpeg", "-version"])
        f_fp = ex.submit(_versao_de, ["ffprobe", "-version"])
        f_cl = ex.submit(lambda: _versao_de([_claude_exe(), "--version"], 20) if _claude_exe() else (None, None))
        f_ol = ex.submit(ajustes_modelos)
        f_tts = ex.submit(lambda: memo("tts_disp", __import__("lib.tts", fromlist=["x"]).disponiveis, ttl=60))   # leve 01/11: ~2 s → cache
    out = []

    def item(i, nome, ok, detalhe, dica="", nivel=None):
        out.append({"id": i, "nome": nome, "ok": bool(ok), "nivel": nivel or ("ok" if ok else "erro"), "detalhe": detalhe, "dica": "" if ok else dica})

    pv = sys.version_info
    item("python", "🐍 Python", pv >= (3, 10), f"versão {pv.major}.{pv.minor}.{pv.micro}", "Instale o Python 3.12: " + W)
    exe, v = f_node.result()
    maj = int(v.split(".")[0]) if v and v[0].isdigit() else 0
    item("node", "🟩 Node.js (22 ou mais novo)", maj >= 22, f"versão {v}" if exe else "não encontrado",
         ("Atualize o Node.js pra versão 22+. " if exe else "") + W + " (ou: winget install OpenJS.NodeJS.LTS)")
    (e1, v1), (e2, _) = f_ff.result(), f_fp.result()
    item("ffmpeg", "🎞 ffmpeg (corta e junta vídeo)", e1 and e2, f"versão {v1}" if e1 else "não encontrado", W + " (ou: winget install Gyan.FFmpeg)")
    try:
        import yt_dlp  # noqa: F401
        ytv = getattr(__import__("yt_dlp.version", fromlist=["x"]), "__version__", "?")
        yt = True
    except Exception:
        ytv, yt = "", bool(shutil.which("yt-dlp") or Path(RYT.ytdlp_exe()).exists())
    item("ytdlp", "⬇ yt-dlp (baixa vídeos de referência)", yt, f"versão {ytv}" if ytv else ("ok" if yt else "não encontrado"),
         "Abra o terminal e rode: python -m pip install -U yt-dlp")
    exe, v = f_cl.result()
    item("claude", "🧠 Claude Code (Estilos IA e pedidos)", exe, f"versão {v}" if exe else "não encontrado",
         "Instale o Claude Code e entre na sua conta (plano Pro ou superior): " + W)
    ms = [m["nome"] for m in (f_ol.result() or [])]
    item("ollama", "🤖 Ollama ligado (IA grátis do PC)", ms, f"{len(ms)} modelo(s) instalado(s)" if ms else "desligado ou não instalado",
         "Abra o app do Ollama (ícone da lhama perto do relógio). Se não tiver: " + W)
    mo = aj.get("modelo_ollama") or "qwen2.5:7b"
    item("modelo", f"🧩 Modelo {mo} baixado", mo in ms, "pronto" if mo in ms else "não baixado",
         f"Abra o terminal e rode: ollama pull {mo}  (uns 5 GB, uma vez só)")
    d = f_tts.result() or {}
    item("voz", "🎙 Voz (narração)", d.get("edge") or d.get("qwen3") or d.get("chatterbox"),
         ", ".join(k for k in ("edge", "qwen3", "chatterbox") if d.get(k)) or "nenhuma", "Abra o terminal e rode: python -m pip install edge-tts")
    try:
        pasta = Path(aj.get("pasta_saida") or out_dir())
        livre = shutil.disk_usage(pasta if pasta.exists() else pasta.anchor).free / 1e9
        item("pasta", "📁 Pasta dos vídeos", pasta.exists() and livre > 5, f"{amigavel(pasta)} · {livre:.0f} GB livres",
             "Escolha outra pasta em ⚙ Ajustes" if not pasta.exists() else "Pouco espaço no disco: libere pelo menos 5 GB.")
    except Exception as e:
        item("pasta", "📁 Pasta dos vídeos", False, str(e)[:120], "Escolha a pasta em ⚙ Ajustes.")
    try:
        cat = _ski_cat().get("skills", [])
        n = sum(1 for s in cat if (SKILLS_HOME / s["id"] / "SKILL.md").exists())
        item("skills", "🎨 Estilos IA instalados", n > 0, f"{n} de {len(cat)}", "Vá em 🤖 Estilos IA e clique em ⬇ Instalar skills.",
             nivel="ok" if n == len(cat) else ("aviso" if n else "erro"))
    except Exception:
        pass
    for k, nome in (("gemini_key", "✨ Chave Gemini"), ("pexels_key", "📷 Chave Pexels"), ("pixabay_key", "🖼 Chave Pixabay"),
                    ("elevenlabs_key", "🗣 Chave ElevenLabs")):
        # chaves são opcionais (01/11: painel 100% sem chave). Só aparecem no diagnóstico se a pessoa colocou — nunca cobram.
        if str(aj.get(k) or "").strip():
            item(k, nome + " (opcional)", True, "configurada", "")
    return out


@app.get("/api/diagnostico")
def diagnostico(fresco: bool = False):
    t0 = time.time()
    if fresco:   # "🔄 Conferir de novo" → confere a voz na hora (sem o cache de 60 s)
        memo_limpar("tts_disp")
    its = _diag_itens()
    return {"itens": its, "erros": sum(1 for x in its if x["nivel"] == "erro"), "avisos": sum(1 for x in its if x["nivel"] == "aviso"),
            "segundos": round(time.time() - t0, 1)}


# ======================================================= ⏱💲 ESTIMATIVA (tempo e custo médios dos vídeos já feitos pelo Claude)
def _estimativas():
    por, ger, por_pasta = {}, {"skill": [], "claude": []}, {}
    real = lambda x: os.path.normcase(os.path.realpath(str(x)))
    for base in pastas_varredura():
        b = Path(base)
        if not b.exists():
            continue
        for rf in b.glob("*/RELATORIO.json"):
            p = rf.parent
            try:
                r = json.loads(rf.read_text(encoding="utf-8-sig"))
                usd, mins = float(r.get("custo_usd") or 0), float(r.get("minutos") or 0)
            except Exception:
                continue
            if usd <= 0 or mins <= 0:   # só o que o Claude fez (as ferramentas grátis do PC gravam custo 0)
                continue
            try:
                ped = json.loads((p / "edit.json").read_text(encoding="utf-8-sig")).get("pedido") or {}
            except Exception:
                ped = {}
            x = (mins, usd)
            if ped.get("skill"):
                por.setdefault("skill:" + ped["skill"], []).append(x)
                ger["skill"].append(x)
            else:
                if ped.get("estilo_id"):
                    por.setdefault(ped["estilo_id"], []).append(x)
                por_pasta.setdefault(real(p), []).append(x)
                ger["claude"].append(x)
    try:   # estilo "🧠 Precisa do Claude" da galeria → o próprio vídeo-exemplo também conta
        for e in estilos():
            if e.get("tipo") == "claude" and e.get("pasta") and real(e["pasta"]) in por_pasta:
                por.setdefault(e["id"], []).extend(por_pasta[real(e["pasta"])])
    except Exception:
        pass
    med = lambda l: {"min": round(sum(a for a, _ in l) / len(l), 1), "usd": round(sum(b for _, b in l) / len(l), 2), "n": len(l)}
    return {"por": {k: med(v) for k, v in por.items()}, "geral": {k: med(v) for k, v in ger.items() if v}}


@app.get("/api/estimativas")
def estimativas():
    return memo("estimativas", _estimativas, ttl=120, sig=lambda: _sig_dirs(pastas_varredura()))


# ======================================================= 🔧 PEDIR AJUSTE (vídeo feito pelo Claude → AJUSTE-N.md → Claude aplica na mesma pasta)
def _ajuste_alvo(pasta: Path):
    return pasta / "resultado.mp4" if (pasta / "resultado.mp4").exists() else pasta / "final.mp4"


def job_ajuste(pasta: Path, n, seco, prog):
    alvo = _ajuste_alvo(pasta)
    base = {"pid": pid_of(pasta), "folder": str(pasta), "name": pasta.name, "ajuste": f"AJUSTE-{n}.md"}
    if seco:
        prog(100, f"AJUSTE-{n}.md criado (o Claude não rodou)")
        return {**base, "rendered": alvo.exists(), "precisa_claude": not _claude_exe(), "seco": True}
    antes = alvo.stat().st_mtime if alvo.exists() else 0
    if alvo.exists():
        (pasta / "versoes").mkdir(exist_ok=True)
        shutil.copy2(alvo, pasta / "versoes" / f"antes-ajuste-{n}.mp4")   # dá pra voltar se não gostar
    skill = alvo.name == "resultado.mp4"
    r = _claude_rodar(pasta, prog, f"Claude aplicando o ajuste {n}…",
                      f"Leia o AJUSTE-{n}.md desta pasta ({pasta}) e aplique SÓ esse ajuste no vídeo que já está pronto aqui. "
                      "Mantenha todo o resto igual (texto, voz, estilo, cenas, música, legenda) e reaproveite os arquivos que já existem. "
                      + ("No fim, regrave o vídeo como resultado.mp4 na raiz da pasta. " if skill else
                         f"Edite o edit.json (formato em {ROOT / 'FORMATO.md'}) e renderize de novo com build_from_edit.py pra regravar o final.mp4. ")
                      + "Você está rodando sozinho pelo painel: não faça perguntas, decida e siga até regravar o vídeo.")
    fim = r["fim"]
    if not alvo.exists() or alvo.stat().st_mtime <= antes:
        raise RuntimeError(f"O Claude terminou mas não regravou o {alvo.name}.\n" + (str(fim.get("result") or "") or "\n".join(r["resto"]))[-2500:]
                           + f"\n\n(O vídeo antigo continua lá. Detalhes: claude-log.jsonl na pasta.)")
    try:
        rel_f = pasta / "RELATORIO.json"
        rel = json.loads(rel_f.read_text(encoding="utf-8-sig")) if rel_f.exists() else {}
        rel.setdefault("ajustes", []).append({"n": n, "minutos": r["minutos"], "custo_usd": fim.get("total_cost_usd")})
        rel_f.write_text(json.dumps(rel, ensure_ascii=False, indent=1), encoding="utf-8")
        if skill:   # duração/medidas do vídeo novo no edit.json (o card e o editor usam)
            ef = pasta / "edit.json"
            ed = json.loads(ef.read_text(encoding="utf-8-sig"))
            info = probe_full(alvo) or {}
            if info.get("dur"):
                ed["duration"] = float(info["dur"])
                for it in ed.get("items") or []:
                    if (it.get("props") or {}).get("src") == "resultado.mp4":
                        it["dur"] = float(info["dur"])
            ef.write_text(json.dumps(ed, ensure_ascii=False, indent=1), encoding="utf-8")
    except Exception:
        pass
    th = pasta / "thumb.jpg"
    if th.exists():
        try:
            th.unlink()   # miniatura refeita com o vídeo novo
        except OSError:
            pass
    memo_limpar()
    prog(100, f"Ajuste {n} pronto em {r['minutos']} min!")
    return {**base, "rendered": True, "precisa_claude": False}


@app.post("/api/ajuste/{pid}")
def ajuste_pedir(pid: str, data: dict = Body(...)):
    p = path_of(pid)
    texto = str(data.get("texto") or "").strip()[:4000]
    if len(texto) < 4:
        raise HTTPException(400, "Escreva o que você quer mudar (ex.: troca a cor do título pra amarelo).")
    if not (p / "PEDIDO.md").exists():
        raise HTTPException(400, "Este vídeo não foi feito pelo Claude — pra mudar, abra no editor.")
    if not find_video(p) and not (p / "resultado.mp4").exists():
        raise HTTPException(400, "Este vídeo ainda não ficou pronto. Espere terminar pra pedir ajuste.")
    if any(j.get("pid") == pid and j.get("tipo") == "ajuste" and not j["done"] for j in JOBS.values()):
        raise HTTPException(400, "Já tem um ajuste deste vídeo na fila. Espere ele terminar.")
    nums = [int(m.group(1)) for f in p.glob("AJUSTE-*.md") for m in [re.match(r"AJUSTE-(\d+)\.md$", f.name)] if m]
    n = max(nums or [0]) + 1
    alvo = _ajuste_alvo(p)
    try:
        nome = B.load_edit(p, convert=False).get("name") or p.name
    except Exception:
        nome = p.name
    md = "\n".join([
        f"# AJUSTE {n} — {nome}", "",
        f"> Pedido pelo painel Estúdio de Vídeos (🔧 Pedir ajuste) em {datetime.now().strftime('%d/%m/%Y %H:%M')}. "
        "O vídeo já está pronto nesta pasta: aplique SÓ o que está abaixo.", "",
        "## O que o aluno quer mudar", "", texto, "",
        "## Regras",
        "- Mantenha TODO o resto igual: texto/narração, voz, estilo, cenas, música e legenda. Mude só o que foi pedido.",
        "- Reaproveite o que já existe na pasta (não refaça do zero; só gere a narração de novo se o ajuste for nela).",
        f"- A versão anterior fica guardada em `versoes/antes-ajuste-{n}.mp4` (não apague).",
        f"- No fim, regrave `{alvo.name}` na raiz desta pasta.",
        "- Rodando sozinho pelo painel: NÃO faça perguntas; anote as decisões em `DECISOES.md`.",
        f"- Pasta: `{p}`"])
    (p / f"AJUSTE-{n}.md").write_text(md, encoding="utf-8")
    seco = bool(data.get("seco")) or not _claude_exe()   # seco = só grava o AJUSTE-N.md (teste, ou PC sem Claude)
    r = start_job(job_ajuste, p, n, seco, tipo="ajuste", titulo=f"🔧 Ajuste {n} · {str(nome)[:60]}", pid=pid)
    return {**r, "n": n, "arquivo": f"AJUSTE-{n}.md", "seco": seco, "claude": bool(_claude_exe())}


# ======================================================= 🛠 CORRIGIR COM CLAUDE (botão no aviso de erro)
# Roda o Claude Code já instalado (claude -p) na pasta do pacote, com as permissões da pasta. Antes tira uma cópia dos arquivos de código
# (não depende de git) pra dar "Desfazer". Sem chave de API: usa o login do Claude que já está no PC.
PKG = ROOT.parent
CORR_DIR = ROOT / ".cache" / "correcoes"
_CORR_EXT = {".py", ".js", ".html", ".css", ".bat", ".sh", ".ps1", ".txt", ".md"}
_CORR_SKIP = {"skills_ia", ".cache", "node_modules", "__pycache__", ".venv", ".git", "VIDEOS", "VIDEOS-NOVOS", "VIDEOS-SHORTS", "kits", "estoque",
              "VIDEOAULAS", "recursos", ".cookies", ".pedidos", "ref", "img", "audio"}
_CORR_MAX = 1_500_000   # arquivos maiores que isso (dados/vídeos) ficam de fora da cópia


def _corr_arquivos():
    """Arquivos de código do pacote (relativos a PKG) que o Claude pode mexer e que entram na cópia de segurança."""
    out = []
    for raiz, dirs, files in os.walk(PKG):
        dirs[:] = [d for d in dirs if d not in _CORR_SKIP]
        for f in files:
            fp = Path(raiz) / f
            if fp.suffix.lower() in _CORR_EXT:
                try:
                    if fp.stat().st_size <= _CORR_MAX:
                        out.append(fp.relative_to(PKG))
                except OSError:
                    pass
    return out


def _corr_foto(destino: Path):
    destino.mkdir(parents=True, exist_ok=True)
    lista = _corr_arquivos()
    for rel in lista:
        t = destino / rel
        t.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(PKG / rel, t)
    (destino.parent / "lista.json").write_text(json.dumps([r.as_posix() for r in lista]), encoding="utf-8")


def _corr_mudancas(cid):
    """Compara o pacote agora com a cópia de antes → {mudou:[...], novo:[...], sumiu:[...]}."""
    base = CORR_DIR / cid
    antes = base / "antes"
    ant = set(json.loads((base / "lista.json").read_text(encoding="utf-8")))
    agora = {r.as_posix() for r in _corr_arquivos()}
    mudou = []
    for r in sorted(ant & agora):
        try:
            if (PKG / r).read_bytes() != (antes / r).read_bytes():
                mudou.append(r)
        except OSError:
            pass
    return {"mudou": mudou, "novo": sorted(agora - ant), "sumiu": sorted(ant - agora)}


def _corr_prompt(acao, erro, log_cauda):
    return "\n".join([
        "Você está dentro do pacote 'Estúdio de Vídeos' (painel local FastAPI em editor/, fábrica em editor/fabrica/). Leia o CLAUDE.md da raiz.",
        "O usuário clicou numa ação do painel e deu erro. Descubra a CAUSA RAIZ e corrija no código do pacote.", "",
        f"## Ação que falhou\n{acao or '(não informada)'}", "", f"## Mensagem de erro\n```\n{erro[:6000]}\n```", "",
        f"## Final do log do painel (se houver)\n```\n{log_cauda[-3000:] or '(vazio)'}\n```", "",
        "## Regras",
        "- Corrija a causa, não só o sintoma, e pense em outra máquina Windows/Mac/Linux (caminhos, PATH, programas ausentes). Mudança mínima, no estilo do código existente.",
        "- Pode ler tudo; edite só código do pacote (editor/, setup/iniciar, etc). NÃO mexa em VIDEOS*/, vídeos, chaves, ajustes.json nem em arquivos de outras pessoas.",
        "- Se for erro do usuário/internet/limite de serviço (não do código), não invente código: explique no resumo o que a pessoa deve fazer.",
        "- Se possível teste a correção (ex.: rode o trecho com .venv/Scripts/python.exe, `py_compile`). NÃO reinicie o painel nem mate processos: ele está rodando este trabalho.",
        "- Rodando sozinho: NÃO faça perguntas. Não apague arquivos. Não faça git commit/push.",
        "- Termine com um RESUMO em português simples, até 5 linhas: o que estava errado, o que mudou, e se o painel precisa ser reiniciado "
        "(precisa se mudou .py do servidor/fábrica; página web só precisa F5)."])


def job_corrigir(cid, acao, erro, log_cauda, prog):
    exe = _claude_exe()
    if not exe:
        raise RuntimeError("Falta o Claude Code neste PC. Instale o app do Claude (claude.ai/download) e entre na sua conta.")
    base = CORR_DIR / cid
    prog(3, "Guardando uma cópia de segurança (pra poder desfazer)…")
    _corr_foto(base / "antes")
    permitido = ["Read", "Edit", "Write", "Glob", "Grep", "Bash(python:*)", "Bash(.venv/Scripts/python.exe:*)", "Bash(.venv/bin/python:*)",
                 "Bash(py:*)", "Bash(pip:*)", "Bash(node:*)", "Bash(npm:*)", "Bash(npx:*)", "Bash(ffmpeg:*)", "Bash(ffprobe:*)",
                 "Bash(yt-dlp:*)", "Bash(where:*)", "Bash(which:*)", "Bash(ls:*)", "Bash(cat:*)", "Bash(curl:*)", "Bash(git status:*)", "Bash(git diff:*)"]
    negado = ["Bash(rm:*)", "Bash(del:*)", "Bash(rmdir:*)", "Bash(rd:*)", "Bash(git push:*)", "Bash(git commit:*)", "Bash(git reset:*)",
              "Bash(taskkill:*)", "Bash(kill:*)", "Bash(pkill:*)", "Bash(shutdown:*)", "Bash(powershell:*)", "Bash(reg:*)", "Bash(format:*)"]
    # Pedido e permissões vão por ARQUIVO: no Windows o claude.cmd corta texto com quebra de linha e estraga parênteses/asteriscos nos argumentos.
    cfg = base / "permissoes.json"
    cfg.write_text(json.dumps({"permissions": {"allow": permitido, "deny": negado}}, ensure_ascii=False, indent=1), encoding="utf-8")
    pedido = base / "PEDIDO-CORRECAO.md"
    pedido.write_text(_corr_prompt(acao, erro, log_cauda), encoding="utf-8")
    perm = ["--permission-mode", "acceptEdits", "--settings", str(cfg)]
    r = _claude_rodar(base, prog, "Claude investigando o erro…",
                      f"Leia o arquivo {pedido} e faça exatamente o que ele pede (corrigir um erro do painel Estúdio de Vídeos). Siga as regras dele.",
                      cwd=PKG, perm_args=perm)
    fim = r.get("fim") or {}
    resumo = str(fim.get("result") or "").strip()
    if not resumo and fim.get("is_error"):
        raise RuntimeError("O Claude não conseguiu terminar: " + (" ".join(r.get("resto") or [])[-300:] or "sem detalhes"))
    ch = _corr_mudancas(cid)
    precisa_reiniciar = any(x.endswith(".py") for x in ch["mudou"] + ch["novo"])
    memo_limpar()
    prog(100, "Pronto!")
    return {"cid": cid, "resumo": resumo or "O Claude terminou, mas não deixou resumo.", **ch, "reiniciar": precisa_reiniciar, "minutos": r.get("minutos")}


@app.post("/api/corrigir")
def corrigir(data: dict = Body(...)):
    if not _claude_exe():
        raise HTTPException(400, "Não achei o Claude Code neste PC. Instale o app do Claude (claude.ai/download) e entre na sua conta.")
    if any(j.get("tipo") == "corrigir" and not j.get("done") for j in JOBS.values()):
        raise HTTPException(400, "Já tem uma correção rodando. Espere ela terminar.")
    acao = str(data.get("acao") or "")[:400]
    erro = str(data.get("erro") or "")[:12000]
    if len(erro.strip()) < 3:
        raise HTTPException(400, "Sem mensagem de erro pra corrigir.")
    cid = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_cauda = ""
    try:
        for f in sorted(ROOT.glob("*.log"), key=lambda x: x.stat().st_mtime)[-1:]:
            log_cauda = f.read_text(encoding="utf-8", errors="replace")[-3000:]
    except Exception:
        pass
    return start_job(job_corrigir, cid, acao, erro, log_cauda, tipo="corrigir", titulo="🛠 Corrigir com Claude · " + (acao or "erro")[:60])


@app.post("/api/corrigir/{cid}/desfazer")
def corrigir_desfazer(cid: str):
    if not re.fullmatch(r"\d{8}-\d{6}", cid) or not (CORR_DIR / cid / "lista.json").exists():
        raise HTTPException(404, "Não achei essa correção.")
    if any(j.get("tipo") == "corrigir" and not j.get("done") for j in JOBS.values()):
        raise HTTPException(400, "Espere a correção terminar.")
    ch = _corr_mudancas(cid)
    antes = CORR_DIR / cid / "antes"
    for r in ch["mudou"] + ch["sumiu"]:
        (PKG / r).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(antes / r, PKG / r)
    for r in ch["novo"]:   # arquivo criado pelo Claude: vai pra "lixeira" da própria correção (não apaga de vez)
        dst = CORR_DIR / cid / "criados" / r
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(PKG / r), str(dst))
    memo_limpar()
    return {"ok": True, "desfeito": len(ch["mudou"]) + len(ch["sumiu"]) + len(ch["novo"]),
            "reiniciar": any(x.endswith(".py") for x in ch["mudou"] + ch["novo"] + ch["sumiu"])}


@app.post("/api/reiniciar")
def reiniciar_painel():
    """Reabre o próprio painel (usado depois de uma correção em arquivo .py). Espera o aviso chegar na tela e sobe de novo."""
    def _vai():
        time.sleep(1.5)
        exe, srv = sys.executable, str(Path(__file__).resolve())
        if os.name == "nt":
            subprocess.Popen(f'cmd /c ping -n 4 127.0.0.1 >nul & "{exe}" "{srv}"', shell=True, cwd=str(PKG),
                             creationflags=0x00000008 | 0x00000200)   # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
        else:
            subprocess.Popen(["sh", "-c", f'sleep 3; exec "{exe}" "{srv}"'], cwd=str(PKG), start_new_session=True)
        os._exit(0)
    threading.Thread(target=_vai, daemon=True).start()
    return {"ok": True}


# ======================================================= 📒 RECEITAS (estilo + voz + formato + duração + @ + obs, com nome)
RECEITAS_F = ROOT / "receitas.json"
RECEITA_CAMPOS = ("estilo", "voz", "formato", "duracao", "marca", "canal", "obs", "versoes", "nicho")


def _receitas_ler():
    try:
        l = json.loads(RECEITAS_F.read_text(encoding="utf-8"))
        return l if isinstance(l, list) else []
    except Exception:
        return []


@app.get("/api/receitas")
def receitas_lista():
    return _receitas_ler()


@app.post("/api/receitas")
def receitas_salvar(data: dict = Body(...)):
    nome = str(data.get("nome") or "").strip()[:60]
    tela = str(data.get("tela") or "").strip()
    if not nome:
        raise HTTPException(400, "Dê um nome pra receita (ex.: Reels de finanças).")
    if tela not in ("ia", "pedido"):
        raise HTTPException(400, "Tela inválida.")
    dados = {k: str(v)[:300] for k, v in (data.get("dados") or {}).items() if k in RECEITA_CAMPOS and v not in (None, "")}
    l = [x for x in _receitas_ler() if not (x.get("tela") == tela and str(x.get("nome", "")).lower() == nome.lower())]
    l.insert(0, {"id": uuid.uuid4().hex[:8], "nome": nome, "tela": tela, "dados": dados, "criado": datetime.now().isoformat(timespec="seconds")})
    tmp = RECEITAS_F.with_suffix(".tmp")
    tmp.write_text(json.dumps(l[:100], ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, RECEITAS_F)
    return l[:100]


@app.delete("/api/receitas/{rid}")
def receitas_apagar(rid: str):
    l = [x for x in _receitas_ler() if x.get("id") != rid]
    RECEITAS_F.write_text(json.dumps(l, ensure_ascii=False, indent=1), encoding="utf-8")
    return l


# ======================================================= 📱 ABRIR NO CELULAR (QR code com o endereço na rede de casa)
REDE = {"liberada": False}   # preenchido no __main__ (o painel só escuta na rede se "rede_local" estiver ligado no config.json)


def _ip_lan():
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))   # UDP: não manda nada, só descobre qual placa de rede sai pra rede de casa
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "127.0.0.1"


@app.get("/api/rede")
def rede_info():
    ip = _ip_lan()
    try:
        import qrcode  # noqa: F401
        tem_qr = True
    except Exception:
        tem_qr = False
    return {"ip": ip, "porta": PORT, "url": f"http://{ip}:{PORT}", "liberada": REDE["liberada"],
            "pedida": bool(conf().get("rede_local")), "qr": tem_qr}


@app.get("/api/rede/qr.svg")
def rede_qr():
    try:
        import qrcode
        import qrcode.image.svg
    except Exception:
        raise HTTPException(404, "Sem o pacote qrcode (python -m pip install qrcode).")
    import io
    buf = io.BytesIO()
    qrcode.make(f"http://{_ip_lan()}:{PORT}", image_factory=qrcode.image.svg.SvgPathFillImage, box_size=12, border=2).save(buf)
    return Response(buf.getvalue(), media_type="image/svg+xml", headers={"Cache-Control": "no-store"})


@app.post("/api/rede/liberar")
def rede_liberar(data: dict = Body(...)):
    c = conf()
    c["rede_local"] = bool(data.get("on"))
    CONF.write_text(json.dumps(c, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"ok": True, "pedida": c["rede_local"], "liberada": REDE["liberada"]}


if __name__ == "__main__":
    import socket

    import uvicorn
    # escuta em 127.0.0.1 E em ::1 — o navegador tenta "localhost" primeiro pelo IPv6; sem isso cada conexão
    # nova esperava ~200 ms o Windows desistir do ::1 antes de cair no 127.0.0.1.
    socks = []
    REDE["liberada"] = bool(conf().get("rede_local"))   # 📱 Abrir no celular: só quando o aluno liga (fica visível na rede de casa)
    for fam, addr in ((socket.AF_INET, "0.0.0.0" if REDE["liberada"] else "127.0.0.1"), (socket.AF_INET6, "::1")):
        try:
            sk = socket.socket(fam, socket.SOCK_STREAM)
            if fam == socket.AF_INET6:
                sk.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
            sk.bind((addr, PORT))
            sk.listen(2048)
            sk.set_inheritable(True)
            socks.append(sk)
        except OSError as e:
            if fam == socket.AF_INET:
                raise
            print("IPv6 ::1 indisponível:", e)
    uvicorn.Server(uvicorn.Config(app, log_level="warning")).run(sockets=socks)
