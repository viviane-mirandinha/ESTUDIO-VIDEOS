# ollama.py — roteiro e palavras-chave pelo Ollama local (qwen na 4090). Zero token Claude.
import json
import re
import urllib.error
import urllib.request

from .util import log

_LOCAL = "http://localhost:11434"


def base():
    """Endereço do Ollama: o do outro PC (Ajustes → ollama_url, ex.: http://100.x.x.x:11434) ou o deste PC."""
    try:
        from . import ajustes as AJ
        u = str(AJ.ler().get("ollama_url") or "").strip().rstrip("/")
    except Exception:
        u = ""
    return u if re.match(r"^https?://[^\s/]+(:\d+)?$", u) else _LOCAL


def remoto():
    return base() != _LOCAL


def __getattr__(nome):   # compatibilidade: ollama.URL (usado em roteiro_pronto.py) sempre reflete o Ajustes
    if nome == "URL":
        return base() + "/api/generate"
    raise AttributeError(nome)

KEEP = "30m"   # modelo fica na placa 30 min depois do último uso (antes: 5 min → toda ideia/roteiro esperava recarregar)
MODELO_PADRAO = __import__("os").environ.get("ESTUDIO_OLLAMA_MODELO") or "mistral-small3.1:latest"   # PT melhor que o qwen2.5:7b (memória canais-roblox); qwen = --modelo qwen2.5:7b

REGRAS_COPY = """Você é um Copywriter Multimídia Sênior especialista em retenção. Regras obrigatórias:
1. Narrativa 100% linear e progressiva. PROIBIDO repetir informação, reiniciar a história ou re-explicar.
2. Gancho visceral nos primeiros 3-5 segundos (quebra de padrão). ZERO saudação, zero "olá", zero introdução lenta.
3. Frases curtas e diretas, linguagem coloquial persuasiva, ritmo dinâmico.
4. CTA orgânico: pedir o like de forma contextual UMA vez no meio e UMA vez no encerramento (ex.: "se essa parte te surpreendeu, deixa o like"). Nunca jogado do nada.
5. Fidelidade factual: use SOMENTE fatos reais e amplamente conhecidos sobre o tema. NUNCA invente nome, número, data ou citação. Se não tiver certeza de um número, não cite número.
6. Narrador em terceira pessoa, português do Brasil. Nada de "eu". Nada de títulos, marcadores, emojis ou colchetes no texto: só a locução pura.
7. Sem palavras em inglês. Nenhum texto fora do JSON pedido."""


def gerar(prompt, modelo=MODELO_PADRAO, json_mode=False, temperatura=0.6, num_predict=1200, timeout=600):
    body = {"model": modelo, "prompt": prompt, "stream": False,
            "options": {"temperature": temperatura, "num_predict": num_predict, "num_ctx": 8192}, "keep_alive": KEEP}
    if json_mode:
        body["format"] = "json"
    req = urllib.request.Request(base() + "/api/generate", data=json.dumps(body).encode("utf-8"),
                                 headers={"Content-Type": "application/json"})
    try:
        r = urllib.request.urlopen(req, timeout=timeout)
    except urllib.error.URLError as e:
        if not isinstance(getattr(e, "reason", None), ConnectionRefusedError) or not ligar():
            raise
        r = urllib.request.urlopen(req, timeout=timeout)
    with r:
        d = json.load(r)
    return d.get("response", "")


def aquecer(modelo=MODELO_PADRAO, timeout=180):
    """Só carrega o modelo na placa (sem gerar nada) e deixa lá por KEEP. Usado quando o painel liga."""
    body = {"model": modelo, "keep_alive": KEEP, "options": {"num_ctx": 8192}}
    req = urllib.request.Request(base() + "/api/generate", data=json.dumps(body).encode("utf-8"), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        r.read()
    return True


def _no_ar():
    try:
        with urllib.request.urlopen(base() + "/api/tags", timeout=3):
            return True
    except Exception:
        return False


def ligar(espera=30):
    """Ollama desligado → sobe o 'ollama serve' escondido e espera ficar no ar. True se subiu."""
    import os
    import shutil
    import subprocess
    import time
    if _no_ar():
        return True
    if remoto():   # Ollama do outro PC: não adianta subir o deste
        return False
    exe = shutil.which("ollama") or next((p for p in (os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Ollama", "ollama.exe"),
                                                      "/usr/local/bin/ollama", "/opt/homebrew/bin/ollama") if os.path.exists(p)), None)
    if not exe:
        return False
    subprocess.Popen([exe, "serve"], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0) | getattr(subprocess, "DETACHED_PROCESS", 0))
    fim = time.time() + espera
    while time.time() < fim:
        if _no_ar():
            return True
        time.sleep(1)
    return False


def _json_seguro(txt):
    try:
        return json.loads(txt)
    except Exception:
        m = re.search(r"\{.*\}", txt, re.S)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                pass
    return {}


def roteiro(tema, palavras, canal, estilo_prompt="", modelo=MODELO_PADRAO, regras=None):
    """Devolve {"titulo": str, "roteiro": str}. ~150 palavras por minuto."""
    if palavras > 900:   # vídeo de ~6 min ou mais: uma chamada só não aguenta (janela do modelo) → escreve em partes
        return roteiro_longo(tema, palavras, canal, estilo_prompt, modelo, regras)
    prompt = f"""{regras or REGRAS_COPY}

Canal: {canal}. Estilo do vídeo: {estilo_prompt or 'documentário curto'}.
Tema: {tema}

Escreva a locução completa com {palavras} a {int(palavras*1.15)} palavras (conte as palavras; menos de {int(palavras*0.85)} é inaceitável).
Responda SOMENTE com o texto da locução: sem título, sem JSON, sem comentários."""
    melhor = ""
    for tent in range(3):
        r = _limpa_roteiro(gerar(prompt, modelo, temperatura=0.7, num_predict=int(palavras * 4) + 400))
        n = len(r.split())
        if n > len(melhor.split()):
            melhor = r
        if n >= palavras * 0.7:
            break
        log(f"roteiro curto ({n} palavras), tentando de novo…")
    if len(melhor.split()) < palavras * 0.4:
        raise RuntimeError("Ollama não devolveu roteiro válido (3 tentativas)")
    # corta sobra (mantendo frases inteiras) se passou muito do alvo
    fr, acc, out = re.split(r"(?<=[.!?…])\s+", melhor), 0, []
    for f in fr:
        if acc + len(f.split()) > palavras * 1.3 and out:
            break
        out.append(f)
        acc += len(f.split())
    melhor = " ".join(out)
    log(f"roteiro Ollama ({modelo}): {len(melhor.split())} palavras")
    return {"titulo": titulo(melhor, tema, modelo), "roteiro": melhor}


def roteiro_longo(tema, palavras, canal, estilo_prompt="", modelo=MODELO_PADRAO, regras=None, progresso=None):
    """Roteiro de 6 a 60 min: plano em partes (JSON) e cada parte escrita à parte (~450 palavras), vendo o final da anterior."""
    por_parte = 450
    n = max(3, round(palavras / por_parte))
    base = f"""{regras or REGRAS_COPY}

Canal: {canal}. Estilo do vídeo: {estilo_prompt or 'documentário'}.
Tema: {tema}"""
    plano = []
    for _ in range(3):
        d = _json_seguro(gerar(base + f"""

Monte o PLANO de um vídeo longo em exatamente {n} partes, em ordem, cada uma avançando a história sem repetir a anterior
(a 1ª abre com gancho forte; a última fecha o assunto). Uma linha curta por parte, dizendo o que ela cobre.
Responda SÓ JSON: {{"partes": ["...", "..."]}}""", modelo, json_mode=True, temperatura=0.5, num_predict=60 * n + 300))
        p = d.get("partes") if isinstance(d, dict) else None
        if isinstance(p, list) and len(p) >= max(3, n - 2):
            plano = [str(x).strip() for x in p if str(x).strip()][:n]
            break
    if len(plano) < 3:   # sem plano da IA: divide em fases genéricas
        fases = ["abertura com gancho e contexto", "origem e primeiros fatos", "desenvolvimento do assunto", "o ponto de virada",
                 "consequências e impacto", "curiosidades e detalhes pouco conhecidos", "o que isso significa hoje", "fechamento"]
        plano = [fases[min(i * len(fases) // n, len(fases) - 1)] for i in range(n)]
    n = len(plano)
    alvo = max(150, palavras // n)
    lista = "\n".join(f"{i + 1}. {t}" for i, t in enumerate(plano))
    partes, total = [], 0
    for i, t in enumerate(plano):
        ult = i == n - 1
        extra = ("É a PARTE FINAL: feche o assunto e termine com UM pedido de like/inscrição natural." if ult else
                 "NÃO conclua nem se despeça: o vídeo continua na próxima parte." if i else
                 "É a ABERTURA: gancho visceral nos 3 primeiros segundos, sem saudação, e NÃO conclua: o vídeo continua.")
        if i == n // 2 and not ult:
            extra += " Inclua aqui UM pedido de like de forma contextual."
        ant = " ".join(partes[-1].split()[-120:]) if partes else ""
        prompt = f"""{base}

PLANO COMPLETO do vídeo:
{lista}

{('Final do trecho anterior (continue a partir dele, SEM repetir nada): ' + ant) if ant else ''}
Escreva AGORA somente a PARTE {i + 1} de {n}: «{t}». {extra}
Tamanho: {alvo} a {int(alvo * 1.2)} palavras (menos de {int(alvo * 0.8)} é inaceitável). Só a locução, sem título, sem numeração, sem JSON."""
        melhor = ""
        for tent in range(3):
            r = _limpa_roteiro(gerar(prompt, modelo, temperatura=0.7, num_predict=int(alvo * 4) + 400))
            if len(r.split()) > len(melhor.split()):
                melhor = r
            if len(r.split()) >= alvo * 0.7:
                break
            log(f"parte {i + 1}/{n} curta ({len(r.split())} palavras), tentando de novo…")
        if len(melhor.split()) < 40:
            raise RuntimeError(f"Ollama não escreveu a parte {i + 1} de {n} do roteiro.")
        partes.append(melhor)
        total += len(melhor.split())
        log(f"roteiro: parte {i + 1}/{n} pronta ({total} palavras até aqui)")
        if progresso:
            progresso(10 + 85 * (i + 1) / n, f"Parte {i + 1} de {n} pronta ({total} palavras)…")
    texto = "\n\n".join(partes)
    log(f"roteiro Ollama ({modelo}): {total} palavras em {n} partes")
    return {"titulo": titulo(texto, tema, modelo), "roteiro": texto}


def titulo(roteiro_txt, tema, modelo=MODELO_PADRAO):
    prompt = f"""Crie UM título apelativo de vídeo do YouTube (máximo 9 palavras, português do Brasil, sem ponto final, sem aspas, sem emoji). O título deve citar o nome ou o fato mais forte do tema e gerar curiosidade (ex.: "O rei que inventou o dinheiro e perdeu tudo"). Locução sobre "{tema}":
{roteiro_txt[:1500]}
Responda só JSON: {{"titulo": "..."}}"""
    d = _json_seguro(gerar(prompt, modelo, json_mode=True, temperatura=0.5, num_predict=80))
    t = re.sub(r"[\"“”*#]", "", str(d.get("titulo") or "")).strip().rstrip(".")
    return t[:90] if t else tema[:60]


def _limpa_roteiro(r):
    r = re.sub(r"\[[^\]]*\]|\([^)]*\)", "", r)        # remove [AUDIO] (pausa) etc.
    r = re.sub(r"[*#_>]+", "", r)
    r = re.sub(r"\s+", " ", r).strip()
    return r


def queries_imagens(shots, tema, dica="historical photograph", modelo=MODELO_PADRAO, lote=10):
    """Em lotes (CPU lenta estoura o timeout com muitos trechos numa chamada só)."""
    def seguro(parte):   # timeout/queda do Ollama num lote não derruba o vídeo: esse lote usa a busca por regra (sem IA)
        try:
            return _queries_lote(parte, tema, dica, modelo)
        except Exception as e:
            log(f"Ollama falhou nas buscas de imagem ({type(e).__name__}) — este lote usa a busca por regra")
            return _queries_regra(parte, tema)
    if len(shots) <= lote:
        return seguro(shots)
    out = []
    for i in range(0, len(shots), lote):
        out += seguro(shots[i:i + lote])
    return out


def _queries_lote(shots, tema, dica="historical photograph", modelo=MODELO_PADRAO):
    """Uma busca em inglês (Wikimedia Commons) por trecho falado. Devolve lista de strings (len == len(shots))."""
    lista = "\n".join(f"{i+1}. {s}" for i, s in enumerate(shots))
    prompt = f"""You pick search queries for Wikimedia Commons (free images). Video topic: {tema}.
Image style wanted: {dica}.
For EACH numbered narration excerpt below, write ONE short English search query (2 to 4 words) naming a concrete, literal thing that exists as a photo/painting/engraving on Wikimedia Commons: a named person, place, building, object, coin, document or event. EVERY query MUST contain at least one proper noun or specific object name from the topic (e.g. "Croesus", "Sardis", "Lydian stater"), never only generic words like "ancient economy artifacts" or "first world currency". Never repeat a query.

Excerpts:
{lista}

Answer ONLY with JSON: {{"queries": ["query for 1", "query for 2", ...]}} with exactly {len(shots)} items in order."""
    for _ in range(2):
        d = _json_seguro(gerar(prompt, modelo, json_mode=True, temperatura=0.3, num_predict=60 * len(shots) + 200))
        q = d.get("queries")
        if isinstance(q, list) and q:
            q = [str(x).strip().strip('"') for x in q]
            while len(q) < len(shots):
                q.append(q[-1])
            return q[:len(shots)]
    return _queries_regra(shots, tema)


def _queries_regra(shots, tema):
    """Fallback sem IA: nomes próprios + números do trecho, senão o tema."""
    out = []
    for s in shots:
        caps = re.findall(r"\b[A-ZÁÉÍÓÚÂÊÔÃÕÇ][\wÁ-ú]+(?:\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ][\wÁ-ú]+)?", s[1:])
        anos = re.findall(r"\b1[0-9]{3}\b|\b20[0-9]{2}\b", s)
        q = " ".join((caps[:2] + anos[:1])) or tema
        out.append(q)
    return out


def palavras_chave(roteiro, n=10, modelo=MODELO_PADRAO):
    """Palavras fortes pra destacar na legenda (amarelo)."""
    prompt = f"""Do texto abaixo, liste as {n} palavras mais impactantes/emocionais (uma palavra cada, exatamente como aparecem no texto, minúsculas, sem pontuação).
Texto: {roteiro}
Responda só JSON: {{"palavras": ["...", "..."]}}"""
    d = _json_seguro(gerar(prompt, modelo, json_mode=True, temperatura=0.2, num_predict=200))
    p = d.get("palavras")
    if isinstance(p, list):
        return [str(x).lower().strip(".,!?") for x in p if str(x).strip()][:n]
    return []
