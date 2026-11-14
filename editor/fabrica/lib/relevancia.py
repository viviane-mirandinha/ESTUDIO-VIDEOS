# relevancia.py — confere se a imagem/clipe BATE com a cena antes de entrar no vídeo.
#   1) texto: palavras da busca + nomes próprios da cena no título/descrição/tags do banco;
#   2) CLIP local (open_clip ViT-B-32, CPU ou GPU) olhando a miniatura, se estiver instalado.
# Nada passa só porque "foi o primeiro resultado": sem nota mínima a cena cai no fallback do TEMA
# (busca geral do assunto do vídeo) e, se nem isso, repete a última imagem boa. Nunca mídia aleatória.
# Sem CLIP (PC fraco / pacote sem torch) funciona só com o texto — mais rígido, mesma regra.
import difflib
import io
import os
import re
import subprocess
import threading
import unicodedata
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .util import log

UA = {"User-Agent": "EstudioVideos/1.0 (uso pessoal)"}
CLIP_MODEL, CLIP_PRE = "ViT-B-32", "laion2b_s34b_b79k"
LIM_CLIP = 0.215        # cos(miniatura, "a photo of <busca>") mínimo pra cena valer (ViT-B-32 laion: casa ~0.26-0.35, nada a ver ~0.10-0.19)
LIM_CLIP_ENT = 0.19     # mais folgado quando o nome próprio da cena está no título do arquivo
LIM_CLIP_SO_IMAGEM = 0.27   # título/tags sem NENHUMA palavra da busca: só entra se a imagem casar forte
NEG = ["a map of {q}", "a page of text about {q}", "a logo of {q}", "a diagram or chart about {q}", "a coat of arms of {q}",
       "a blank white image", "a screenshot of a website"]   # com o assunto: "mapa do Brasil" vence "foto do Brasil"
NEG_OK = re.compile(r"\b(map|chart|diagram|graph|logo|document|text|letter|newspaper|flag|coat|seal|screenshot|website|app)\b", re.I)

STOP = set("""the and of in a an on at to for with from by is are was were be this that these those it its as or into over under about
old ancient photo photograph image picture view historical history vintage century early late portrait city general topic
de da do das dos e o a os as um uma uns umas no na nos nas em para por com sem que se mais muito muita sobre entre ate
el la los las del con por para una uno sus""".split())
CAP_STOP = set("""eu ele ela eles elas nos voce voces isso isto aquilo esse essa este esta mas porque quando entao depois antes
hoje ontem amanha sim nao o a os as um uma de do da no na e se que como onde quem qual por para com muito mais agora
tudo nada todo toda cada primeiro segunda segundo terceiro i you he she we they it this that but and the a an in on so
if when then now yes no my your our his her their there here what who why how el la los las y pero muy cuando""".split())

_lock = threading.Lock()
_M = {"model": None, "pre": None, "tok": None, "dev": "cpu", "falhou": False}
_cache_img, _cache_txt = {}, {}


def _fold(s):
    return unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().lower()


def tokens(s):
    return {t for t in re.findall(r"[a-z0-9]+", _fold(s)) if len(t) >= 3 and t not in STOP}


def entidades(texto, max_n=6):
    """Nomes próprios da frase (sequência de Palavras Maiúsculas que não é só início de frase)."""
    out = []
    for frase in re.split(r"(?<=[.!?])\s+|\n+", str(texto or "")):
        ws = re.findall(r"[\wÀ-ÿ'’-]+", frase)
        k = 0
        while k < len(ws):
            if ws[k][:1].isupper() and _fold(ws[k]) not in CAP_STOP and len(ws[k]) >= 3:
                j = k
                while j + 1 < len(ws) and (ws[j + 1][:1].isupper() or (_fold(ws[j + 1]) in ("de", "da", "do", "of", "von", "van", "del")
                                                                       and j + 2 < len(ws) and ws[j + 2][:1].isupper())):
                    j += 1
                nome = " ".join(ws[k:j + 1])
                if (k > 0 or j > k or nome.isupper()) and nome not in out:   # 1ª palavra da frase sozinha = pode ser só maiúscula de início
                    out.append(nome)
                k = j + 1
            else:
                k += 1
    return out[:max_n]


def texto_cand(c):
    pag = urllib.parse.unquote(urllib.parse.urlparse(c.get("pagina") or "").path)
    return " ".join(str(c.get(k) or "") for k in ("titulo", "title", "desc", "tags")) + " " + re.sub(r"[-_/.]+", " ", pag)


def nota_texto(c, query, ents=()):
    """(palavras da busca encontradas, achou nome próprio?)"""
    tc = tokens(texto_cand(c))
    n = sum(1 for t in tokens(query) if t in tc or (t.endswith("s") and t[:-1] in tc) or (t + "s") in tc)
    ent = any(tokens(e) and tokens(e) <= tc for e in ents)
    return n, ent


def _thumb(c):
    u = c.get("thumb") or ""
    if not u and c.get("tipo", "image") == "image" and c.get("url"):
        u = c["url"]
    if "/thumb/" in u:
        u = re.sub(r"/(\d+)px-", "/330px-", u)
    else:   # original do Commons (sem /thumb/): pede a miniatura padrão de 330px em vez do arquivo inteiro
        m = re.match(r"(https://upload\.wikimedia\.org/wikipedia/commons)/(\w/\w\w)/([^?]+)", u)
        if m:
            u = f"{m.group(1)}/thumb/{m.group(2)}/{m.group(3)}/330px-{m.group(3)}"
    return u if u.startswith("http") else ""


# ------------------------------------------------------------------ CLIP (opcional)
def clip_ok():
    if os.environ.get("ESTUDIO_SEM_CLIP") or _M["falhou"]:
        return False
    if _M["model"] is not None:
        return True
    with _lock:
        if _M["model"] is not None:
            return True
        try:
            import open_clip
            import torch
            dev = "cuda" if torch.cuda.is_available() else "cpu"
            m, _, pre = open_clip.create_model_and_transforms(CLIP_MODEL, pretrained=CLIP_PRE, device=dev)
            m.eval()
            _M.update(model=m, pre=pre, tok=open_clip.get_tokenizer(CLIP_MODEL), dev=dev)
            log(f"CLIP ligado ({dev}) — imagens conferidas contra a cena")
            return True
        except Exception as e:
            _M["falhou"] = True
            log(f"CLIP indisponível ({type(e).__name__}) — conferindo só pelo texto")
            return False


def _emb_txt(frases):
    import torch
    falta = [f for f in frases if f not in _cache_txt]
    if falta:
        with torch.no_grad():
            e = _M["model"].encode_text(_M["tok"](falta).to(_M["dev"])).float()
            e = e / e.norm(dim=-1, keepdim=True)
        for f, v in zip(falta, e):
            _cache_txt[f] = v
    return torch.stack([_cache_txt[f] for f in frases])


def _baixar_thumb(u):
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=10) as r:
            return r.read()
    except Exception:
        return None


def _emb_imgs(urls):
    import torch
    from PIL import Image
    falta = [u for u in dict.fromkeys(urls) if u and u not in _cache_img]
    if falta:
        with ThreadPoolExecutor(max_workers=8) as pool:
            dados = list(pool.map(_baixar_thumb, falta))
        ims, ok = [], []
        for u, b in zip(falta, dados):
            try:
                ims.append(_M["pre"](Image.open(io.BytesIO(b)).convert("RGB")))
                ok.append(u)
            except Exception:
                _cache_img[u] = None
        if ims:
            with torch.no_grad():
                e = _M["model"].encode_image(torch.stack(ims).to(_M["dev"])).float()
                e = e / e.norm(dim=-1, keepdim=True)
            for u, v in zip(ok, e):
                _cache_img[u] = v
    return [_cache_img.get(u) for u in urls]


LIM_TEMA = 0.22          # arquivo real × assunto do vídeo (teste 07/11 pirâmides: no tema 0,29-0,31; fora 0,15-0,21)
LIM_TEMA_VISUAL = 0.26   # assunto conta como critério só se 3+ cenas o mostram bem (tema abstrato não reprova)
LIM_CHECA = 0.22   # arquivo real × busca da cena (teste 07/11 no projeto 99: 0,203 trocou por 0,331 bem melhor)


def _quadros_arquivo(arq):
    """Imagem → ela mesma; clipe → 2 quadros (1 s e 3 s), pra pegar clipe que muda de assunto no meio."""
    from PIL import Image
    arq = Path(arq)
    if arq.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp", ".gif"):
        return [Image.open(arq).convert("RGB")]
    out = []
    for t in ("1", "3"):
        r = subprocess.run(["ffmpeg", "-v", "error", "-ss", t, "-i", str(arq), "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"],
                           capture_output=True, timeout=60, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        if r.stdout:
            out.append(Image.open(io.BytesIO(r.stdout)).convert("RGB"))
    return out


def notas_arquivos(itens):
    """itens = [(arquivo, busca)] → nota CLIP do que o vídeo vai MOSTRAR (média dos quadros) contra 'a photo of <busca>'.
    None = sem CLIP no PC ou arquivo ilegível."""
    if not clip_ok():
        return [None] * len(itens)
    import torch
    out = []
    for arq, q in itens:
        try:
            ims = _quadros_arquivo(arq)
            if not ims:
                out.append(None)
                continue
            with torch.no_grad():
                e = _M["model"].encode_image(torch.stack([_M["pre"](im) for im in ims]).to(_M["dev"])).float()
                e = e / e.norm(dim=-1, keepdim=True)
            out.append(float((e @ _emb_txt([f"a photo of {q}"])[0]).mean()))
        except Exception as ex:
            log(f"checagem: não li {Path(arq).name} ({type(ex).__name__})")
            out.append(None)
    return out


# ------------------------------------------------------------------ escolha
RUIDOSAS =("YouTube CC", "Archive.org")   # qualquer um sobe vídeo lá: título casa com palavra solta ("Orc Tower demolition")


def avaliar(cands, query, ents=(), assunto="", querer_video=False, tema=""):
    """Anota cada candidato com c["relev"] (ordem) e c["passa"] (bate com a cena?).
    tema = nomes/assunto do vídeo inteiro: fonte ruidosa só passa se o título citar o tema ou o nome da cena."""
    tt = tokens(tema)
    usa_clip = clip_ok() and bool(cands)
    embs = [None] * len(cands)
    if usa_clip:
        try:
            embs = _emb_imgs([_thumb(c) for c in cands])
            frases = [f"a photo of {query}", f"a photo of {assunto or query}"] + [n.format(q=query) for n in NEG]
            T = _emb_txt(frases)
        except Exception as e:
            log(f"CLIP falhou nesta cena ({type(e).__name__}) — só texto")
            usa_clip, embs = False, [None] * len(cands)
    pode_neg = not NEG_OK.search(query or "")
    for c, e in zip(cands, embs):
        n, ent = nota_texto(c, query, ents)
        if c.get("fonte") in RUIDOSAS and tt and not ent and not (tt & tokens(texto_cand(c))):
            c["nota"], c["passa"], c["relev"] = n, False, -9.0
            continue
        c["nota"] = n + (2 if ent else 0)
        bonus = (0.25 if querer_video and c.get("tipo") == "video" else 0.0)
        if usa_clip and e is not None:
            s = (T @ e).tolist()
            sq, sa, neg = s[0], s[1], max(s[2:])
            ruim = pode_neg and n == 0 and neg > sq   # título sem palavra da busca e parece mais mapa/texto/logo DAQUELE assunto do que foto dele
            c["clip"] = round(sq, 3)
            c["passa"] = (not ruim) and ((ent and sq >= LIM_CLIP_ENT) or (n >= 1 and sq >= LIM_CLIP) or sq >= LIM_CLIP_SO_IMAGEM)
            c["relev"] = round((0.75 * sq + 0.25 * sa) * 10 + min(n, 3) * 0.25 + (0.6 if ent else 0) + bonus - (1.0 if ruim else 0), 3)
        elif usa_clip:   # CLIP ligado mas a miniatura não baixou: sem ver a imagem, não entra (foi assim que um mapa de dengue passou)
            c["passa"], c["relev"] = False, -5.0
        else:
            # sem CLIP no PC: só aceita se o banco descreve a coisa (palavra da busca ou o nome próprio)
            c["passa"] = n >= 1 or ent
            c["relev"] = round(min(n, 4) * 1.0 + (2 if ent else 0) + bonus, 3)
    return cands


def aprovados(cands, usados, query, ents=(), assunto="", querer_video=False, tema=""):
    """Candidatos que BATEM com a cena, do melhor pro pior ([] = quem chama cai no fallback do tema)."""
    livres = [c for c in cands if c.get("url") not in usados]
    if not livres or not (query or "").strip():
        return []
    avaliar(livres, query, ents, assunto, querer_video, tema)
    return sorted((c for c in livres if c.get("passa")), key=lambda c: -c["relev"])


def escolher(cands, usados, query, ents=(), assunto="", querer_video=False, tema=""):
    bons = aprovados(cands, usados, query, ents, assunto, querer_video, tema)
    return bons[0] if bons else None


def reforcar_busca(q, ents):
    """Se a cena cita um nome próprio e a busca não tem, põe o nome na busca (Ollama às vezes troca por algo genérico).
    `ents` = nomes próprios citados na cena (lista) ou o texto da frase."""
    if not q:
        return q
    if isinstance(ents, str):
        ents = entidades(ents)
    tq = tokens(q)

    def ja_tem(e):   # "Brasil" x "Brazil", "Napoleão" x "Napoleon": grafia parecida conta como presente
        return all(any(difflib.SequenceMatcher(None, t, x).ratio() >= 0.72 for x in tq) for t in tokens(e))
    falta = [e for e in ents if tokens(e) and not ja_tem(e)]
    if not falta:
        return q
    e = max(falta, key=len)
    # tira da busca as palavras que já estão no nome (evita "Vanderbilt Cornelius Vanderbilt")
    resto = " ".join(w for w in q.split() if _fold(w) not in {_fold(x) for x in e.split()})
    return f"{e} {resto}".strip()[:60]
