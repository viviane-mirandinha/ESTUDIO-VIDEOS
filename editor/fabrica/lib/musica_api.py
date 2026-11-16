"""musica_api.py — busca música de fundo ONLINE, sem biblioteca local e SEM obrigação de crédito.

Fonte: Internet Archive (archive.org). Só entram itens cuja licença cadastrada é CC0 1.0 (domínio público),
que permite uso comercial e NÃO exige crédito. Nada fica guardado: a faixa escolhida é baixada direto para
a pasta do vídeo e um comprovante (link, licença, data) é gravado ao lado.

Cuidados (a licença no Internet Archive é preenchida pelo próprio autor do envio, então conferimos de novo):
  - licenseurl tem que ser exatamente creativecommons.org/publicdomain/zero/1.0
  - descarta podcast, audiolivro, palestra, fala e rádio
  - só aceita faixas de 60 s a 15 min, em mp3, até 30 MB
Sem chave de API. A API não publica cota fixa; usamos poucas chamadas por vídeo, com pausa e nova tentativa.
"""
import json
import random
import re
import time
import urllib.parse
import urllib.request
from datetime import date

UA = {"User-Agent": "EstudioVideos-local/1.0 (musica de fundo CC0)"}
ADV = "https://archive.org/advancedsearch.php"
META = "https://archive.org/metadata/"
DL = "https://archive.org/download/"
CC0 = re.compile(r"creativecommons\.org/publicdomain/zero/1\.0", re.I)
RUIM = re.compile(r"podcast|audiobook|audio book|audiolivro|speech|sermon|lecture|interview|radio show|talk|spoken|news|"
                  r"episode|episodio|ep\.|chapter|capitulo|voice|vocal samples|asmr|sound effect|sfx|field recording", re.I)
MIN_S, MAX_S, MAX_MB = 60, 900, 30

# SÓ a coleção "netlabels" (gravadoras independentes que publicam o próprio material). Busca geral no archive.org
# traz músicas famosas enviadas por terceiros com licença CC0 FALSA (testado: apareceram artistas comerciais).
COLECAO = "netlabels"

# clima -> palavras no assunto ou no título (inglês, como as netlabels etiquetam)
ASSUNTOS = {
    "terror": ["dark", "drone", "horror", "creepy", "noise"],
    "suspense": ["dark", "ambient", "drone", "experimental", "tension"],
    "epico": ["orchestral", "classical", "cinematic", "epic", "strings"],
    "triste": ["piano", "sad", "melancholy", "classical", "ambient"],
    "calmo": ["ambient", "chill", "calm", "relax", "soundscape"],
    "tecnologia": ["electronic", "techno", "electro", "idm", "synth"],
    "acao": ["rock", "techno", "breakbeat", "drum", "industrial"],
    "leve": ["happy", "funk", "jazz", "chiptune", "pop"],
}
# se o clima pedido não tiver faixas boas, tenta o parecido
VIZINHO = {"epico": ["suspense", "triste"], "triste": ["calmo"], "leve": ["calmo", "tecnologia"], "terror": ["suspense"],
           "acao": ["tecnologia"], "tecnologia": ["calmo"], "suspense": ["calmo"], "calmo": ["suspense"]}


def _get_json(url, tentativas=3):
    ult = None
    for i in range(tentativas):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
                d = json.load(r)
            if isinstance(d, dict) and d.get("error"):   # o backend do archive.org falha de vez em quando
                raise RuntimeError(d["error"])
            return d
        except Exception as e:
            ult = e
            time.sleep(1.2 * (i + 1))
    raise ult


def _busca(clima, rows=100, pagina=1):
    """Devolve (itens, total). Sem ordenar por downloads (isso favorece uploads piratas)."""
    ws = ASSUNTOS.get(clima, ASSUNTOS["calmo"])
    termos = " OR ".join(f'subject:"{s}" OR title:"{s}"' for s in ws)
    q = f"mediatype:audio AND collection:{COLECAO} AND licenseurl:*zero* AND ({termos})"
    p = {"q": q, "fl[]": ["identifier", "title", "creator", "licenseurl", "subject"],
         "rows": rows, "page": pagina, "output": "json"}
    r = _get_json(ADV + "?" + urllib.parse.urlencode(p, doseq=True)).get("response", {})
    return r.get("docs", []), int(r.get("numFound") or 0)


def _texto(s):
    """Conserta títulos com acento quebrado (UTF-8 lido como latin-1), que o archive.org tem às vezes."""
    s = str(s)
    try:
        return s.encode("latin-1").decode("utf-8")
    except Exception:
        return s


def _segundos(v):
    try:
        if ":" in str(v):
            r = 0
            for x in str(v).split(":"):
                r = r * 60 + float(x)
            return r
        return float(v)
    except Exception:
        return 0


def _faixa_boa(ident, ja_usadas):
    """Abre o item e devolve a melhor faixa mp3 dele (ou None). Confere a licença de novo."""
    m = _get_json(META + urllib.parse.quote(ident))
    md = m.get("metadata", {})
    if not CC0.search(str(md.get("licenseurl", ""))):
        return None
    if md.get("mediatype") != "audio":
        return None
    texto = " ".join(str(md.get(k, "")) for k in ("title", "subject", "collection", "description"))[:1500]
    if RUIM.search(texto):
        return None
    boas = []
    for f in m.get("files", []):
        nome = f.get("name", "")
        if not nome.lower().endswith(".mp3") or "/" in nome:
            continue
        dur, mb = _segundos(f.get("length")), int(f.get("size") or 0) / 1e6
        if MIN_S <= dur <= MAX_S and 0.3 < mb <= MAX_MB and f"{ident}/{nome}" not in ja_usadas:
            boas.append((dur, nome))
    if not boas:
        return None
    dur, nome = random.choice(boas)
    creator = md.get("creator") or "autor desconhecido"
    if isinstance(creator, list):
        creator = ", ".join(creator)
    return {"identificador": ident, "arquivo_remoto": nome, "duracao": round(dur),
            "titulo": _texto(md.get("title") or nome)[:120], "autor": _texto(creator)[:120],
            "licenca_url": str(md.get("licenseurl")), "pagina": f"https://archive.org/details/{ident}",
            "url": DL + urllib.parse.quote(ident) + "/" + urllib.parse.quote(nome)}


# ── 2ª fonte: Wikimedia Commons (via Openverse). Gravações clássicas CC0 → bom pra épico e triste. ──────────────
OPENVERSE = "https://api.openverse.org/v1/audio/"
WIKI_RUIM = re.compile(r"recitation|murattal|quran|koran|surah|chapter|anthem|himno|hymne|himne|hino |national|"
                       r"pronunciation|spoken|reading|lecture|speech|interview|prayer|chant|sermon|mass for", re.I)
WIKI_TERMOS = {   # clima -> buscas (o Openverse devolve no máximo 240 por busca, então variamos)
    "epico": ["symphony", "orchestra", "overture", "march", "fanfare", "brass"],
    "triste": ["piano", "sonata", "nocturne", "elegy", "violin", "requiem"],
    "calmo": ["piano", "nocturne", "lullaby", "violin", "prelude"],
    "suspense": ["toccata", "requiem", "fugue", "dark"],
    "tecnologia": ["8-bit", "chiptune", "synth"],
    "acao": ["chiptune", "8-bit", "game", "rock"],
    "leve": ["chiptune", "8-bit", "waltz", "polka"],
}
WIKI_PRIMEIRO = {"epico", "triste"}   # nesses climas o Wikimedia vem antes das netlabels


def _openverse(termo, pagina=1):
    p = {"source": "wikimedia_audio", "license": "cc0", "page_size": 20, "page": pagina, "q": termo, "mature": "false"}
    return _get_json(OPENVERSE + "?" + urllib.parse.urlencode(p))


def _buscar_wiki(clima, ja_usadas):
    termos = WIKI_TERMOS.get(clima)
    if not termos:
        return None
    termo = random.choice(termos)
    try:
        d = _openverse(termo)
        paginas = int(d.get("page_count") or 1)
        if paginas > 1:
            d = _openverse(termo, random.randint(1, min(paginas, 12)))
    except Exception:
        return None
    itens = d.get("results", [])
    random.shuffle(itens)
    for x in itens:
        dur, mb = (x.get("duration") or 0) / 1000, (x.get("filesize") and int(x["filesize"]) or 0) / 1e6
        texto = " ".join(str(x.get(k) or "") for k in ("title", "creator")) + " " + " ".join(
            (t.get("name", "") if isinstance(t, dict) else str(t)) for t in (x.get("tags") or []))
        if x.get("license") != "cc0" or not x.get("url") or f"wm/{x['id']}" in ja_usadas:
            continue
        if not (MIN_S <= dur <= MAX_S) or (mb and mb > MAX_MB):
            continue
        if WIKI_RUIM.search(texto) or RUIM.search(texto):
            continue
        return {"identificador": "wm", "arquivo_remoto": x["id"], "duracao": round(dur), "fonte": "Wikimedia Commons",
                "titulo": _texto(x.get("title") or "sem título")[:120], "autor": _texto(x.get("creator") or "autor desconhecido")[:120],
                "licenca_url": x.get("license_url") or "https://creativecommons.org/publicdomain/zero/1.0/",
                "pagina": x.get("foreign_landing_url") or "", "url": x["url"], "clima": clima}
    return None


def buscar(climas, ja_usadas=(), max_itens=12):
    """Procura uma faixa CC0 para os climas (do melhor para o pior). Devolve dict ou None."""
    ordem = []
    for c in climas:   # climas pedidos + vizinhos, sem repetir
        for x in [c] + VIZINHO.get(c, []):
            if x not in ordem:
                ordem.append(x)
    for clima in ordem:
        if clima in WIKI_PRIMEIRO:
            f = _buscar_wiki(clima, ja_usadas)
            if f:
                return f
        f = _buscar_netlabels(clima, ja_usadas, max_itens)
        if f:
            return f
        if clima not in WIKI_PRIMEIRO:
            f = _buscar_wiki(clima, ja_usadas)
            if f:
                return f
    return None


def _buscar_netlabels(clima, ja_usadas, max_itens):
    """Internet Archive, só a coleção netlabels. Devolve dict ou None."""
    try:
        docs, total = _busca(clima)
        if total > 100:   # mais de uma página: sorteia uma, pra não repetir sempre as mesmas
            docs, _ = _busca(clima, pagina=random.randint(1, (total + 99) // 100))
    except Exception:
        return None
    docs = [d for d in docs if CC0.search(str(d.get("licenseurl", "")))]
    random.shuffle(docs)
    for d in docs[:max_itens]:
        try:
            f = _faixa_boa(d["identifier"], ja_usadas)
        except Exception:
            continue
        if f:
            f.update(clima=clima, fonte="Internet Archive")
            return f
    return None


def comprovante(f):
    """Texto do comprovante de licença gravado na pasta do vídeo (prova em caso de reivindicação)."""
    return (f"Música de fundo — comprovante de licença (gerado em {date.today().isoformat()})\n\n"
            f"Faixa: {f['titulo']}\nAutor: {f['autor']}\nFonte: {f.get('fonte', 'Internet Archive')}\nPágina: {f['pagina']}\nArquivo: {f['arquivo_remoto']}\n"
            f"Licença: CC0 1.0 (domínio público) — {f['licenca_url']}\n"
            "Crédito: NÃO é obrigatório. Uso comercial permitido.\n"
            "Guarde este arquivo: se o YouTube/Instagram reivindicar a música, ele mostra a licença registrada na fonte.\n")
