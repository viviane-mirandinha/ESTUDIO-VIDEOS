# rede_yt.py — proxies + login do YouTube (cookies) para TODO download do yt-dlp do Estúdio.
# Escrito do zero. Config em EDITOR VIDEOS\proxies.json; cópia dos cookies em EDITOR VIDEOS\.cookies\.
# Sem proxy e sem cookies tudo segue igual (download direto, um por vez).
import json
import random
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import quote, urlsplit

EDITOR = Path(__file__).resolve().parent.parent.parent
ARQ = EDITOR / "proxies.json"
PASTA_COOKIES = EDITOR / ".cookies"
VIDEO_TESTE = "https://www.youtube.com/watch?v=aqz-KE-bpKQ"   # Big Buck Bunny (Blender), tem até 4K


def ytdlp_exe():
    """Acha o yt-dlp: primeiro no PATH, senão ao lado do Python do .venv (o Windows não põe .venv/Scripts no PATH)."""
    achou = shutil.which("yt-dlp")
    if achou:
        return achou
    for nome in ("yt-dlp.exe", "yt-dlp"):
        c = Path(sys.executable).parent / nome
        if c.exists():
            return str(c)
    return "yt-dlp"


SEM_JANELA = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def ler():
    d = {"lanes": [], "cookies_geral": ""}
    if ARQ.exists():
        try:
            d.update(json.loads(ARQ.read_text(encoding="utf-8-sig")))
        except Exception:
            pass
    d["lanes"] = [l for l in d.get("lanes") or [] if l.get("proxy")]
    return d


def _gravar(d):
    tmp = ARQ.with_suffix(".tmp")
    tmp.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(ARQ)


def normalizar(linha):
    """Aceita http://u:p@h:porta, socks5://u:p@h:porta, h:porta, h:porta:u:p ou 'IP porta usuário senha'."""
    s = (linha or "").strip()
    if not s or s.startswith("#"):
        return ""
    if "://" in s:
        return s
    partes = s.split()
    if len(partes) == 1:
        partes = s.split(":")
    if len(partes) == 2:
        return f"http://{partes[0]}:{partes[1]}"
    if len(partes) == 4:
        h, p, u, w = partes
        return f"http://{quote(u, safe='')}:{quote(w, safe='')}@{h}:{p}"
    return ""


def _host(proxy):
    try:
        u = urlsplit(proxy)
        return f"{u.hostname}:{u.port}"
    except Exception:
        return proxy


def mascarar(proxy):
    try:
        u = urlsplit(proxy)
        if u.password:
            return f"{u.scheme}://{u.username}:***@{u.hostname}:{u.port}"
    except Exception:
        pass
    return proxy


def publico():
    d = ler()
    return {"lanes": [{"n": i + 1, "proxy": mascarar(l["proxy"]), "login": bool(l.get("cookies") and Path(l["cookies"]).exists()),
                       "teste": l.get("teste")} for i, l in enumerate(d["lanes"])],
            "cookies_geral": bool(d.get("cookies_geral") and Path(d["cookies_geral"]).exists())}


def salvar_lista(texto):
    """Recebe o texto da caixa (1 proxy por linha). Linha com *** = mantém a senha já salva daquele host."""
    d = ler()
    antigos = {_host(l["proxy"]): l for l in d["lanes"]}
    novas, ruins = [], []
    for linha in (texto or "").splitlines():
        if not linha.strip():
            continue
        if "***" in linha:
            velho = antigos.get(_host(linha.strip()))
            if velho:
                novas.append(velho)
            else:
                ruins.append(linha.strip())
            continue
        p = normalizar(linha)
        if not p:
            ruins.append(mascarar(linha.strip()))
            continue
        velho = antigos.get(_host(p))
        novas.append({"proxy": p, "cookies": (velho or {}).get("cookies", "")})
    d["lanes"] = novas[:10]
    _gravar(d)
    return {"ok": True, "salvos": len(d["lanes"]), "ignorados": ruins}


def ligar_login(origem, lane=0):
    """Copia um cookies.txt (exportado com 'Get cookies.txt LOCALLY') pra pasta do Estúdio. lane=0 → login geral (sem proxy)."""
    src = Path(str(origem).strip().strip('"'))
    if not src.is_file():
        raise ValueError("Arquivo de cookies não encontrado.")
    txt = src.read_text(encoding="utf-8", errors="ignore")
    if "youtube.com" not in txt or "\t" not in txt:
        raise ValueError("Esse arquivo não parece um cookies.txt do YouTube (formato Netscape).")
    PASTA_COOKIES.mkdir(exist_ok=True)
    d = ler()
    if lane:
        if not 1 <= lane <= len(d["lanes"]):
            raise ValueError(f"Não existe a lane {lane}.")
        dst = PASTA_COOKIES / f"lane{lane}.txt"
        shutil.copyfile(src, dst)
        d["lanes"][lane - 1]["cookies"] = str(dst)
    else:
        dst = PASTA_COOKIES / "geral.txt"
        shutil.copyfile(src, dst)
        d["cookies_geral"] = str(dst)
    _gravar(d)
    return {"ok": True, "lane": lane}


def tirar_login(lane=0):
    d = ler()
    if lane and 1 <= lane <= len(d["lanes"]):
        p = d["lanes"][lane - 1].get("cookies")
        d["lanes"][lane - 1]["cookies"] = ""
    else:
        p, d["cookies_geral"] = d.get("cookies_geral"), ""
    if p:
        Path(p).unlink(missing_ok=True)
    _gravar(d)
    return {"ok": True}


def _escolher(d, lane=None):
    """Lane escolhida (1..N) ou sorteada entre as que passaram no teste; sem lanes → None."""
    ls = d["lanes"]
    if not ls:
        return None
    if lane and 1 <= lane <= len(ls):
        return ls[lane - 1]
    boas = [l for l in ls if (l.get("teste") or {}).get("ok")] or ls
    return random.choice(boas)


def _par(d, lane=None):
    l = _escolher(d, lane)
    if l:
        ck = l.get("cookies") if l.get("cookies") and Path(l["cookies"]).exists() else ""
        return l["proxy"], ck
    ck = d.get("cookies_geral") if d.get("cookies_geral") and Path(d["cookies_geral"]).exists() else ""
    return "", ck


def args(lane=None):
    """Argumentos extras pro yt-dlp de linha de comando."""
    proxy, ck = _par(ler(), lane)
    a = []
    if proxy:
        a += ["--proxy", proxy]
    if ck:
        a += ["--cookies", ck]
    return a


def cmd(*resto, lane=None):
    return [ytdlp_exe(), *args(lane), *resto]


def opts(o=None, lane=None):
    """Mesmo, pro yt_dlp.YoutubeDL(opts) em Python."""
    o = dict(o or {})
    proxy, ck = _par(ler(), lane)
    if proxy:
        o["proxy"] = proxy
    if ck:
        o["cookiefile"] = ck
    return o


def _ip_por(proxy):
    """IP de saída do proxy, perguntando a 3 sites em redes diferentes (só http/https)."""
    if not proxy.startswith("http"):
        return ""
    import urllib.request
    op = urllib.request.build_opener(urllib.request.ProxyHandler({"http": proxy, "https": proxy}))
    for url in ("https://api.ipify.org", "https://icanhazip.com", "https://ifconfig.me/ip"):
        try:
            ip = op.open(url, timeout=12).read().decode().strip()
            if re.match(r"^[\d.:a-fA-F]+$", ip):
                return ip
        except Exception:
            continue
    return ""


def _yt(proxy, ck):
    a = [ytdlp_exe(), "--no-warnings", "--no-playlist", "--simulate", "--socket-timeout", "20", "--print", "%(height)s",
         "-f", "bv*", VIDEO_TESTE]
    if proxy:
        a[1:1] = ["--proxy", proxy]
    if ck:
        a[1:1] = ["--cookies", ck]
    try:
        r = subprocess.run(a, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=90, creationflags=SEM_JANELA)
    except subprocess.TimeoutExpired:
        return False, "Tempo esgotado (proxy lento ou morto)."
    if r.returncode == 0 and r.stdout.strip():
        return True, f"{r.stdout.strip().splitlines()[-1]}p"
    err = (r.stderr or "").lower()
    if "407" in err or "proxy authentication" in err:
        return False, "Senha/usuário do proxy errado (407)."
    if "sign in to confirm" in err or "not a bot" in err:
        return False, "YouTube bloqueia este proxy (pede login). Ligue um login do YouTube nesta lane."
    if "unable to connect" in err or "proxyerror" in err or "connection refused" in err or "timed out" in err:
        return False, "Proxy não responde (morto, plano vencido ou endereço errado)."
    return False, (r.stderr or "falhou").strip().splitlines()[-1][:160]


def testar_todos():
    d = ler()
    res = []
    if not d["lanes"]:
        ok, msg = _yt("", d.get("cookies_geral") if d.get("cookies_geral") and Path(d["cookies_geral"]).exists() else "")
        return {"lanes": [], "direto": {"ok": ok, "msg": ("funciona " + msg) if ok else msg}}
    for i, l in enumerate(d["lanes"]):
        ip = _ip_por(l["proxy"])
        ck = l.get("cookies") if l.get("cookies") and Path(l["cookies"]).exists() else ""
        ok, msg = _yt(l["proxy"], ck)
        if ok:
            msg = f"funciona {msg}" + (" (com o login do YouTube desta lane)" if ck else " (sem login — ligue um pra não tomar bloqueio)")
        elif not ip and l["proxy"].startswith("http") and "bloqueia" not in msg and "não responde" not in msg:
            msg = "Proxy não respondeu em nenhum dos 3 sites de IP. " + msg
        l["teste"] = {"ok": ok, "msg": msg, "ip": ip, "quando": int(time.time())}
        res.append({"n": i + 1, "proxy": mascarar(l["proxy"]), **l["teste"]})
    _gravar(d)
    return {"lanes": res}
