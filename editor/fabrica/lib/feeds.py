# feeds.py — aba "📡 Meus Feeds" do Estúdio: um "algoritmo" seu por nicho.
# Escrito do zero. Só páginas públicas do YouTube via yt-dlp (sem API paga), zero token Claude.
# Anti bot-check (memória do usuário): tudo com --flat-playlist + youtubetab:approximate_date (nunca abre página de vídeo),
# pausa entre requisições, cache do canal 3 dias (reaproveita o do Caçador de nicho).
import json
import os
import re
import statistics
import time
import urllib.parse
import uuid
from pathlib import Path

from . import ideias as ID

EDITOR = Path(__file__).resolve().parent.parent.parent
ARQ = EDITOR / "feeds" / "feeds.json"
CACHE = EDITOR / ".cache" / "feeds"
# sp= "data de envio + só vídeos" da busca (o filtro só de data vem como "lockup" e o yt-dlp 2026.09 lê 0 itens)
RECENTE = {"hoje": "EgQIAhAB", "semana": "EgQIAxAB", "mes": "EgQIBBAB"}
FORA_DA_CURVA = 2.0   # views/hora >= 2x a mediana de views/hora do próprio canal


def _gravar(f: Path, d):
    f.parent.mkdir(parents=True, exist_ok=True)
    tmp = f.with_suffix(".tmp")
    tmp.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, f)


def listar():
    try:
        return json.loads(ARQ.read_text(encoding="utf-8"))
    except Exception:
        return []


def _lista_txt(x):
    if isinstance(x, list):
        return [str(i).strip() for i in x if str(i).strip()]
    return [i.strip() for i in re.split(r"[\n,;]+", str(x or "")) if i.strip()]


def _canal_url(c):
    c = c.strip()
    if c.startswith("@"):
        return "https://www.youtube.com/" + c
    if re.match(r"^https?://", c):
        return re.sub(r"/(videos|shorts|streams|featured)/?$", "", c.rstrip("/"))
    return "https://www.youtube.com/@" + c.lstrip("@")


def salvar(d):
    fs = listar()
    fid = d.get("id") or uuid.uuid4().hex[:8]
    novo = {"id": fid, "nome": str(d.get("nome") or "").strip()[:60] or "Meu feed",
            "palavras": _lista_txt(d.get("palavras"))[:8], "canais": [_canal_url(c) for c in _lista_txt(d.get("canais"))][:12],
            "formato": d.get("formato") if d.get("formato") in ("todos", "shorts", "longos") else "todos",
            "periodo": d.get("periodo") if d.get("periodo") in RECENTE else "semana",
            "criado": next((f.get("criado") for f in fs if f["id"] == fid), time.time())}
    if not novo["palavras"] and not novo["canais"]:
        raise ValueError("Escreva pelo menos uma palavra-chave ou um canal de referência.")
    fs = [f for f in fs if f["id"] != fid] + [novo]
    _gravar(ARQ, fs)
    return novo


def apagar(fid):
    _gravar(ARQ, [f for f in listar() if f["id"] != fid])
    try:
        (CACHE / f"{fid}.json").unlink()
    except Exception:
        pass


def resultado(fid):
    try:
        return json.loads((CACHE / f"{fid}.json").read_text(encoding="utf-8"))
    except Exception:
        return None


def _v(d, canal="", canal_url=""):
    views, ts, dur = ID._num(d.get("view_count")), d.get("timestamp"), ID._num(d.get("duration"))
    return {"id": d["id"], "titulo": d.get("title") or "", "canal": d.get("channel") or d.get("uploader") or canal,
            "canal_url": d.get("uploader_url") or d.get("channel_url") or canal_url, "views": views, "duracao": dur,
            "ts": ts, "vph": ID._vph(views, ts), "url": f"https://www.youtube.com/watch?v={d['id']}",
            "thumb": f"https://i.ytimg.com/vi/{d['id']}/mqdefault.jpg", "short": (dur or 999) <= 180}


def _busca(kw, periodo, n=30):
    url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote(kw) + "&sp=" + RECENTE.get(periodo, RECENTE["semana"])
    return [_v(d) for d in ID._ytdlp_json_linhas(["--flat-playlist", "--playlist-end", str(n), "--extractor-args",
                                                  "youtubetab:approximate_date", "-j", url])
            if d.get("id") and d.get("ie_key") in (None, "Youtube")]


def _canal(url, formato):
    """últimos vídeos do canal (flat, 1 requisição por aba): /videos e/ou /shorts."""
    abas = {"todos": ["videos", "shorts"], "shorts": ["shorts"], "longos": ["videos"]}[formato]
    out = []
    for aba in abas:
        for d in ID._ytdlp_json_linhas(["--flat-playlist", "--playlist-end", "15", "--extractor-args", "youtubetab:approximate_date",
                                        "-j", url.rstrip("/") + "/" + aba]):
            if d.get("id"):
                v = _v(d, canal=d.get("playlist_uploader") or d.get("channel") or "", canal_url=url)
                v["short"] = v["short"] or aba == "shorts"
                out.append(v)
        time.sleep(1.5)
    return out


def atualizar(fid, prog=None, n_canais_medir=10):
    prog = prog or (lambda p, m: None)
    f = next((x for x in listar() if x["id"] == fid), None)
    if not f:
        raise ValueError("Feed não encontrado.")
    dias = {"hoje": 2, "semana": 8, "mes": 31}[f.get("periodo", "semana")]
    agora, vids, erros = time.time(), {}, []
    passos = len(f["palavras"]) + len(f["canais"]) + 1
    k = 0
    for kw in f["palavras"]:
        k += 1
        prog(5 + 55 * k / passos, f"Procurando vídeos novos de “{kw}”…")
        try:
            for v in _busca(kw, f.get("periodo", "semana")):
                v["de"] = "busca: " + kw
                vids.setdefault(v["id"], v)
        except Exception as e:
            erros.append(f"{kw}: {str(e)[:120]}")
        time.sleep(1.5)
    for c in f["canais"]:
        k += 1
        prog(5 + 55 * k / passos, f"Olhando o canal {c.rstrip('/').split('/')[-1]}…")
        try:
            for v in _canal(c, f["formato"]):
                v["de"] = "canal de referência"
                v["ref"] = True
                vids[v["id"]] = {**vids.get(v["id"], {}), **v}
        except Exception as e:
            erros.append(f"{c}: {str(e)[:120]}")
    lst = [v for v in vids.values() if not v.get("ts") or agora - float(v["ts"]) <= dias * 86400]
    if f["formato"] == "shorts":
        lst = [v for v in lst if v["short"]]
    elif f["formato"] == "longos":
        lst = [v for v in lst if not v["short"]]
    # mediana de views/hora de cada canal (cache de 3 dias do Caçador de nicho) → selo "fora da curva"
    por_canal = {}
    for v in lst:
        if v.get("canal_url"):
            por_canal.setdefault(v["canal_url"], []).append(v)
    top = sorted(por_canal, key=lambda u: -max((x["vph"] or 0) for x in por_canal[u]))[:n_canais_medir]
    medianas = {}
    for i, u in enumerate(top):
        prog(62 + 33 * (i + 1) / max(1, len(top)), f"Comparando com a média do canal ({i + 1} de {len(top)})…")
        hit = ID._cache_get("canal-" + ID._sl(u.rstrip("/").split("/")[-1]), 72) is not None
        try:
            inf = ID.info_canal(u)
            if inf and inf.get("mediana_vph"):
                medianas[u] = inf["mediana_vph"]
        except Exception as e:
            erros.append(f"canal {u}: {str(e)[:80]}")
        if not hit:
            time.sleep(2.0)
    vph_ok = [v["vph"] for v in lst if v["vph"]]
    med_feed = statistics.median(vph_ok) if vph_ok else 0
    for v in lst:
        m = medianas.get(v.get("canal_url"))
        v["mediana_canal_vph"] = m
        v["x_canal"] = round(v["vph"] / m, 1) if (m and v["vph"]) else None
        v["fora_da_curva"] = bool(v["x_canal"] and v["x_canal"] >= FORA_DA_CURVA)
        v["idade_h"] = round((agora - float(v["ts"])) / 3600, 1) if v.get("ts") else None
    lst.sort(key=lambda v: -(v["vph"] or 0))
    res = {"id": fid, "nome": f["nome"], "quando": time.strftime("%d/%m/%Y %H:%M"), "ts": agora, "videos": lst[:80],
           "total": len(lst), "mediana_vph": round(med_feed, 1), "erros": erros[:6]}
    if not lst and erros:
        raise RuntimeError("Não consegui puxar nada agora: " + erros[0])
    _gravar(CACHE / f"{fid}.json", res)
    prog(100, f"{len(lst)} vídeos no feed")
    return res
