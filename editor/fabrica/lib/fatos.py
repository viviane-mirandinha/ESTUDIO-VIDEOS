# fatos.py — fatos de referência pro roteiro (Wikipedia, grátis, sem chave). O modelo local pequeno inventa
# nomes/datas quando escreve "de cabeça"; com o resumo do artigo no prompt ele fica preso a fatos reais.
import json
import re
import urllib.parse
import urllib.error
import urllib.request

from .util import log

UA = {"User-Agent": "EstudioVideos/1.0 (uso pessoal)"}
STOP = {"por", "que", "como", "quase", "foi", "uma", "um", "the", "why", "how", "was", "de", "da", "do", "das", "dos", "a", "o", "e", "em",
        "para", "com", "sobre", "historia", "história", "verdade", "segredo", "misterio", "mistério"}


def _get(url):
    import time
    for t in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25) as r:
                time.sleep(0.4)
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code != 429 or t == 3:
                raise
            time.sleep(3 + 3 * t)


def _palavras(t):
    return {w[:5] for w in re.findall(r"\w{3,}", t.lower()) if w not in STOP}   # radical (demolida ~ demolição)


def buscar(tema, idioma="pt-BR", max_chars=4200, modelo=None):
    """Devolve {"titulo", "url", "texto"} com os parágrafos do artigo mais ligados ao tema (ou None)."""
    lang = (idioma or "pt-BR").split("-")[0]
    api = f"https://{lang}.wikipedia.org/w/api.php?"
    try:
        nomes = re.findall(r"(?:[A-ZÁÉÍÓÚÂÊÔÃÕÇ][\wÀ-ÿ]+(?:\s+(?:de|da|do|dos|das|of|the)?\s*[A-ZÁÉÍÓÚÂÊÔÃÕÇ][\wÀ-ÿ]+)*)", tema[1:] if tema[:1].isupper() else tema)
        curto = " ".join(w for w in re.findall(r"\w+", tema) if w.lower() not in STOP)
        hits, alvo_t = [], _palavras(tema)
        for q in [n for n in nomes if len(n) > 3][:2] + [curto, tema]:
            r = _get(api + urllib.parse.urlencode({"action": "query", "list": "search", "srsearch": q, "srlimit": 5, "format": "json"}))
            for h in r.get("query", {}).get("search", []):
                if h["title"] not in hits:
                    hits.append(h["title"])
        if not hits:
            return None
        sujeito = next((w.lower()[:5] for w in re.findall(r"\w{4,}", curto) if w.lower() not in STOP), "")   # 1º substantivo ≈ assunto principal
        # título que mais bate com o tema; bônus pro que tem o assunto principal ("flamingos" > "cor-de-rosa")
        hits.sort(key=lambda t: -(len(_palavras(t) & alvo_t) + (3 if sujeito and sujeito in _palavras(t) else 0)))
        pars, pg, titulo = [], {}, hits[0]
        for titulo in hits[:4]:   # pula página de desambiguação / muito curta
            r = _get(api + urllib.parse.urlencode({"action": "query", "prop": "extracts", "explaintext": 1, "titles": titulo, "format": "json",
                                                   "redirects": 1}))
            pg = next(iter(r.get("query", {}).get("pages", {}).values()), {})
            txt = pg.get("extract") or ""
            pars = [p.strip() for p in re.split(r"\n+", txt) if len(p.strip()) > 80 and not p.strip().startswith("=")]
            if len(pars) >= 3 and len(txt) > 1500:
                break
    except Exception as e:
        log(f"wikipedia falhou: {str(e)[:100]}")
        return None
    if not pars:
        return None
    alvo = _palavras(tema) | _sinonimos(tema, idioma, modelo)
    # 1º parágrafo (introdução) + os mais parecidos com o tema, na ordem do artigo
    nota = [(len(alvo & _palavras(p)), -k) for k, p in enumerate(pars)]
    ordem = sorted(range(len(pars)), key=lambda k: nota[k], reverse=True)
    esc, tot = {0}, len(pars[0])
    for k in ordem:
        if k in esc:
            continue
        if tot + len(pars[k]) > max_chars:
            continue
        esc.add(k)
        tot += len(pars[k])
    texto = "\n".join(pars[k] for k in sorted(esc))
    return {"titulo": pg.get("title") or titulo, "url": f"https://{lang}.wikipedia.org/wiki/" + urllib.parse.quote((pg.get("title") or titulo).replace(" ", "_")),
            "texto": texto[:max_chars]}


def _sinonimos(tema, idioma, modelo):
    """Palavras parecidas com o tema (ex.: demolida → derrubar, desmontar), pra achar o trecho certo do artigo."""
    try:
        from . import ollama
        d = ollama._json_seguro(ollama.gerar(
            f'Liste 10 palavras (no idioma {idioma}) que um artigo de enciclopédia usaria ao falar deste assunto: "{tema}". '
            'Inclua sinônimos e verbos relacionados (ex.: demolida → demolir, derrubar, desmontar, desmantelar). Responda só JSON {"palavras": ["..."]}',
            modelo or "qwen2.5:7b", json_mode=True, temperatura=0.2, num_predict=120, timeout=90))
        return _palavras(" ".join(str(x) for x in d.get("palavras") or []))
    except Exception:
        return set()


def bloco_prompt(f):
    if not f:
        return ""
    return (f"\n\nFATOS DE REFERÊNCIA (Wikipedia, artigo \"{f['titulo']}\"):\n{f['texto']}\n\n"
            "Use SOMENTE fatos que aparecem neste texto de referência. Não invente nomes, datas, números nem acontecimentos que não estejam nele. "
            "Se o tema pedir algo que o texto não traz, fale de forma geral, sem detalhe inventado.")
