"""som_livre.py — Busca de som livre (CC0 / CC BY) no Openverse e, opcional, no Freesound.

Feito do zero pro painel (nada do Auto B-Roll Studio). Reimplementa a IDEIA de sonorizar com sons
livres: procura o som EXATO (whoosh, aplauso, chuva, moeda…) em bancos de licença livre e baixa com
CRÉDITO, em vez de depender de YouTube (risco de Content ID). Padrão: Openverse (sem chave nenhuma);
se o aluno puser a chave do Freesound em Ajustes, também procura lá.

Só traz CC0 e CC BY (as que podem ir em vídeo monetizado). Toda escolha guarda o crédito em
`<projeto>/sons/creditos.json` (fonte, autor, licença, link) — CC BY precisa do crédito na descrição.

Uso:
  python som_livre.py "<termo>"                 # lista candidatos (Openverse)
  python som_livre.py "<termo>" --json
Como biblioteca: buscar(termo, n, chaves) -> [itens]; baixar(item, proj, nome) -> {src, dur, credito}.
"""
import json
import re
import sys
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

UA = {"User-Agent": "EditorVideos/1.0 (painel local do aluno)"}
OPENVERSE = "https://api.openverse.org/v1/audio/"
FREESOUND = "https://freesound.org/apiv2/search/text/"
TIMEOUT = 25


def _get(url, headers=None):
    req = urllib.request.Request(url, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.load(r)


def _slug(s, n=40):
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode()
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()
    return s[:n] or "som"


def _openverse(q, n):
    url = OPENVERSE + "?" + urllib.parse.urlencode({"q": q, "license": "cc0,by", "page_size": n, "peaks": "false"})
    out = []
    try:
        d = _get(url)
    except Exception:
        return out
    for r in d.get("results", []):
        if not r.get("url"):
            continue
        lic = (r.get("license") or "").lower()
        if lic not in ("cc0", "by"):            # só CC0 e CC BY
            continue
        out.append({
            "fonte": "Openverse (" + (r.get("source") or "") + ")",
            "id": r.get("id"), "titulo": r.get("title") or "som",
            "autor": r.get("creator") or "", "licenca": ("CC0" if lic == "cc0" else "CC BY") + " " + (r.get("license_version") or ""),
            "dur": round((r.get("duration") or 0) / 1000.0, 1), "ext": (r.get("filetype") or "mp3").lower(),
            "preview": r.get("url"), "download": r.get("url"), "pagina": r.get("foreign_landing_url") or "",
            "credito": r.get("attribution") or f"{r.get('title','')} — {r.get('creator','')} ({lic.upper()})",
        })
    return out


def _freesound(q, n, token):
    filtro = 'license:("Creative Commons 0" OR "Attribution")'
    url = FREESOUND + "?" + urllib.parse.urlencode(
        {"query": q, "filter": filtro, "page_size": n, "token": token,
         "fields": "id,name,username,license,previews,duration,url,license"})
    out = []
    try:
        d = _get(url)
    except Exception:
        return out
    for r in d.get("results", []):
        pv = (r.get("previews") or {}).get("preview-hq-mp3") or (r.get("previews") or {}).get("preview-lq-mp3")
        if not pv:
            continue
        lic = r.get("license") or ""
        short = "CC0" if "zero" in lic.lower() or "/0/" in lic else "CC BY"
        out.append({
            "fonte": "Freesound", "id": "fs" + str(r.get("id")), "titulo": r.get("name") or "som",
            "autor": r.get("username") or "", "licenca": short, "dur": round(r.get("duration") or 0, 1),
            "ext": "mp3", "preview": pv, "download": pv, "pagina": r.get("url") or "",
            "credito": f"{r.get('name','')} — {r.get('username','')} (Freesound, {short})",
        })
    return out


def buscar(termo, n=12, chaves=None):
    """Lista candidatos CC0/CC BY. Openverse sempre; Freesound se houver chave."""
    chaves = chaves or {}
    itens = _openverse(termo, n)
    tok = chaves.get("freesound") or chaves.get("FREESOUND")
    if tok:
        itens = _freesound(termo, max(4, n // 2), tok) + itens
    return itens[:n]


def baixar(item, proj, nome=None):
    """Baixa o som pro projeto em sons/ e registra o crédito. Devolve {src, dur, credito, arquivo}."""
    proj = Path(proj)
    pasta = proj / "sons"
    pasta.mkdir(parents=True, exist_ok=True)
    ext = (item.get("ext") or "mp3").lstrip(".")
    base = _slug(nome or item.get("titulo") or "som")
    dest = pasta / f"{base}.{ext}"
    i = 2
    while dest.exists():
        dest = pasta / f"{base}-{i}.{ext}"
        i += 1
    req = urllib.request.Request(item["download"], headers=UA)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r, open(dest, "wb") as f:
        f.write(r.read())
    cred = {"arquivo": dest.name, "titulo": item.get("titulo"), "autor": item.get("autor"),
            "fonte": item.get("fonte"), "licenca": item.get("licenca"), "pagina": item.get("pagina"),
            "credito": item.get("credito")}
    credf = pasta / "creditos.json"
    lista = []
    if credf.exists():
        try:
            lista = json.loads(credf.read_text(encoding="utf-8"))
        except Exception:
            lista = []
    lista.append(cred)
    credf.write_text(json.dumps(lista, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"src": f"sons/{dest.name}", "arquivo": dest.name, "dur": item.get("dur"), "credito": item.get("credito")}


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        sys.exit(1)
    itens = buscar(args[0], 12)
    if "--json" in sys.argv:
        print(json.dumps(itens, ensure_ascii=False))
    else:
        for it in itens:
            print(f"- {it['titulo'][:50]:50} {it['dur']:>5}s  {it['licenca']:8} {it['fonte']}")
        print(f"\n{len(itens)} resultado(s).")


if __name__ == "__main__":
    main()
