# claude_api.py — "terceirizar" para o Claude duas etapas lentas do modo fábrica: ROTEIRO e BUSCA DE IMAGENS.
# Dois jeitos (opcional), escolhidos sozinhos:
#   • com chave da Anthropic em Ajustes (anthropic_key) → API, paga por uso (centavos por vídeo);
#   • sem chave, mas com o Claude (Claude Code / app Claude) instalado e logado neste PC → usa o seu PLANO (sem chave, sem cobrança extra).
# Se algo falhar (sem internet, limite do plano, erro), a fábrica volta sozinha para o Ollama local.
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from . import ollama
from .util import log

try:   # preços e modelo ficam num lugar só (claude_rev.py)
    from .claude_rev import MODELO, PRECO_IN, PRECO_OUT
except Exception:   # biblioteca anthropic ausente: só o cálculo de estimativa continua funcionando
    MODELO, PRECO_IN, PRECO_OUT = "claude-sonnet-5-5", 2.00, 10.00   # US$ por milhão de tokens (entrada / saída)

CAMBIO_REF = 5.5      # R$ por US$ — só pra dar uma noção no painel (não é cotação)
TOK_POR_PALAVRA = 1.9  # português: estimativa conservadora de tokens por palavra falada


# ---------------------------------------------------------------- estimativa (sem chamar a API)
def _usd(tin, tout):
    return tin / 1e6 * PRECO_IN + tout / 1e6 * PRECO_OUT


def estimar(duracao_s, palavras_por_min=150, shot_medio=5.5):
    """Quanto custaria terceirizar roteiro e/ou busca de imagens para um vídeo de `duracao_s` segundos."""
    palavras = max(1, int(duracao_s / 60 * palavras_por_min))
    shots = max(2, int(duracao_s / max(1.0, shot_medio)) + 1)
    r_in, r_out = 700, int(palavras * TOK_POR_PALAVRA) + 60
    b_in, b_out = 350 + shots * 26, shots * 11 + 40
    r, b = _usd(r_in, r_out), _usd(b_in, b_out)
    f = lambda usd, tokens: {"usd": round(usd, 4), "brl": round(usd * CAMBIO_REF, 2), "tokens": tokens}
    return {"modelo": MODELO, "palavras": palavras, "shots": shots, "roteiro": f(r, r_in + r_out), "busca": f(b, b_in + b_out),
            "total": f(r + b, r_in + r_out + b_in + b_out), "usd_por_minuto": round((r + b) / max(duracao_s / 60, 0.1), 4),
            "preco_in": PRECO_IN, "preco_out": PRECO_OUT, "cambio_ref": CAMBIO_REF}


# ---------------------------------------------------------------- chamada à API
def achar_claude_exe():
    """Acha o Claude instalado neste PC (mesma busca do painel): PATH, instalações comuns e o app Claude do Windows."""
    w = shutil.which("claude")
    if w:
        return w
    home = Path.home()
    cands = [home / ".local" / "bin" / "claude.exe", home / ".local" / "bin" / "claude", home / ".claude" / "local" / "claude.exe",
             Path(os.environ.get("APPDATA", "")) / "npm" / "claude.cmd"]
    achados = []
    for base in (os.environ.get("LOCALAPPDATA"), os.environ.get("APPDATA")):
        if not base:
            continue
        for pat in ("Claude-Data/*/claude-code/*/*/claude.exe", "Claude-Data/*/claude-code/*/claude.exe", "Claude/claude-code/*/claude.exe",
                    "Claude/claude-code/*/*/claude.exe", "Packages/Claude_*/LocalCache/Roaming/Claude/claude-code/*/*/claude.exe"):
            try:
                achados += [p for p in Path(base).glob(pat) if p.is_file()]
            except Exception:
                pass
    achados.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return next((str(c) for c in cands + achados if str(c) and Path(c).exists()), None)


def modo(chave=""):
    """'api' (tem chave), 'plano' (Claude instalado neste PC) ou None (nenhum dos dois)."""
    if str(chave or "").strip():
        return "api"
    return "plano" if achar_claude_exe() else None


def _chamar(chave, prompt, max_tokens):
    """Texto + uso. Com chave → API; sem chave → Claude instalado no PC (plano)."""
    if str(chave or "").strip():
        return _chamar_api(chave, prompt, max_tokens)
    return _chamar_plano(prompt)


def _chamar_plano(prompt, timeout=900):
    """`claude -p` com o prompt pela entrada padrão. Sem ferramentas e com prompt de sistema mínimo: ~900 tokens de sobra em vez de ~40 mil."""
    exe = achar_claude_exe()
    if not exe:
        raise RuntimeError("o Claude não está instalado neste PC")
    try:
        from .ajustes import ler as _ler
        modelo = (os.environ.get("ESTUDIO_CLAUDE_MODELO") or _ler().get("modelo_claude") or "sonnet").strip()
    except Exception:
        modelo = "sonnet"
    pasta = Path(tempfile.gettempdir()) / "estudio-claude"
    pasta.mkdir(exist_ok=True)
    cmd = [exe, "-p", "--output-format", "json", "--model", modelo, "--tools", "",
           "--system-prompt", "Você é um redator e pesquisador de imagens. Responda exatamente o que o usuário pedir, no formato pedido, sem usar ferramentas e sem comentários extras."]
    p = subprocess.Popen(cmd, cwd=str(pasta), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8",
                         errors="replace", creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    try:
        out, _ = p.communicate(input=prompt, timeout=timeout)
    except subprocess.TimeoutExpired:
        p.kill()
        p.communicate()
        raise RuntimeError("o Claude passou de 15 minutos sem responder")
    r = None
    for cand in [out.strip()] + [l for l in reversed(out.strip().splitlines()) if l.strip().startswith(("{", "["))]:
        try:
            r = json.loads(cand)
            break
        except Exception:
            continue
    if isinstance(r, list):
        r = next((x for x in reversed(r) if isinstance(x, dict) and x.get("type") == "result"), None)
    if not isinstance(r, dict):
        raise RuntimeError("resposta inesperada do Claude: " + out.strip()[-200:])
    if r.get("is_error") or not r.get("result"):   # ex.: "Not logged in", "You've hit your 5-hour limit"
        raise RuntimeError(str(r.get("result") or out)[:200])
    u = r.get("usage") or {}
    tin = int(u.get("input_tokens") or 0) + int(u.get("cache_creation_input_tokens") or 0) + int(u.get("cache_read_input_tokens") or 0)
    return str(r["result"]).strip(), {"tokens_in": tin, "tokens_out": int(u.get("output_tokens") or 0), "usd": 0.0,
                                      "usd_equiv": float(r.get("total_cost_usd") or 0)}   # plano: sem cobrança; usd_equiv = quanto seria na API


def _chamar_api(chave, prompt, max_tokens):
    """Streaming: aguenta roteiros longos sem estourar o limite de 10 min das chamadas normais."""
    import anthropic
    c = anthropic.Anthropic(api_key=chave, timeout=900, max_retries=2)
    with c.messages.stream(model=MODELO, max_tokens=max_tokens, messages=[{"role": "user", "content": prompt}]) as s:
        m = s.get_final_message()
    if m.stop_reason == "refusal":
        raise RuntimeError("o Claude recusou o pedido")
    txt = "".join(b.text for b in m.content if getattr(b, "type", "") == "text").strip()
    return txt, {"tokens_in": m.usage.input_tokens, "tokens_out": m.usage.output_tokens,
                 "usd": _usd(m.usage.input_tokens, m.usage.output_tokens), "usd_equiv": 0.0}


def _soma(*us):
    return {k: sum(u.get(k, 0) for u in us) for k in ("tokens_in", "tokens_out", "usd", "usd_equiv")}


# ---------------------------------------------------------------- 1) roteiro
def roteiro(chave, tema, palavras, canal, estilo_prompt="", regras=None, idioma="português do Brasil"):
    """{"titulo", "roteiro", "uso"} — roteiro inteiro numa chamada só (até ~60 min)."""
    base = f"""{regras or ollama.REGRAS_COPY}

Idioma da locução: {idioma}. Canal: {canal}. Estilo do vídeo: {estilo_prompt or 'documentário'}.
Tema: {tema}

Escreva a locução completa com {palavras} a {int(palavras * 1.1)} palavras (conte; menos de {int(palavras * 0.85)} é inaceitável).
Se o vídeo for longo, avance sempre a história: cada trecho traz algo NOVO, nunca recomeça nem repete a explicação.
Formato da resposta (nada além disto):
TITULO: <título apelativo do YouTube, até 9 palavras, sem aspas nem emoji>

<a locução pura, em parágrafos curtos>"""
    usos, melhor, titulo_ = [], "", ""
    prompt = base
    for tent in range(2):
        txt, u = _chamar(chave, prompt, max_tokens=min(60000, int(palavras * 3.2) + 1500))
        usos.append(u)
        corpo = txt
        m = re.match(r"\s*T[ÍI]TULO:\s*(.+?)\s*\n+(.*)", txt, re.S | re.I)
        tit = ""
        if m:
            tit, corpo = m.group(1).strip().strip('"“”*#'), m.group(2)
        corpo = ollama._limpa_roteiro(corpo)
        if len(corpo.split()) > len(melhor.split()):
            melhor, titulo_ = corpo, tit
        if len(corpo.split()) >= palavras * 0.8:
            break
        log(f"roteiro Claude curto ({len(corpo.split())} palavras de {palavras}), tentando de novo…")
        prompt = base + f"\n\nATENÇÃO: sua tentativa anterior veio com só {len(corpo.split())} palavras. Escreva MAIS, com pelo menos {palavras} palavras."
    if len(melhor.split()) < palavras * 0.5:
        raise RuntimeError(f"o Claude devolveu um roteiro curto demais ({len(melhor.split())} palavras)")
    fr, acc, out = re.split(r"(?<=[.!?…])\s+", melhor), 0, []   # corta sobra grande mantendo frases inteiras
    for f in fr:
        if acc + len(f.split()) > palavras * 1.3 and out:
            break
        out.append(f)
        acc += len(f.split())
    melhor = " ".join(out)
    uso = _soma(*usos)
    log(f"roteiro Claude ({MODELO}): {len(melhor.split())} palavras, {uso['tokens_in'] + uso['tokens_out']} tokens, ~US$ {max(uso['usd'], uso['usd_equiv']):.3f}")
    return {"titulo": (titulo_ or tema[:60]), "roteiro": melhor, "uso": uso}


# ---------------------------------------------------------------- 2) busca de imagens
def queries(chave, trechos, tema, dica="historical photograph", lote=120):
    """Uma busca em inglês por trecho (mesma lista e mesma ordem da entrada). Devolve (lista, uso)."""
    out, usos = [], []
    for i in range(0, len(trechos), lote):
        parte = trechos[i:i + lote]
        lista = "\n".join(f"{k + 1}. {s}" for k, s in enumerate(parte))
        prompt = f"""You choose search queries for Wikimedia Commons (free images). Video topic: {tema}.
Image style wanted: {dica}.
For EACH numbered narration excerpt below, write ONE short English search query (2 to 5 words) for a concrete thing that really exists as an image on Wikimedia Commons: a named painting, artist, person, place, building, object or event that fits the mood and meaning of that excerpt. When the excerpt is abstract (emotions, ideas), pick a fitting famous artwork or artist from the style wanted. Every query must contain a proper noun or a specific object name. Do not repeat a query and avoid reusing the same artist more than twice in a row.

Excerpts:
{lista}

Answer ONLY with JSON: {{"queries": ["query for 1", "query for 2", ...]}} with exactly {len(parte)} items in order."""
        q = None
        for _ in range(2):
            txt, u = _chamar(chave, prompt, max_tokens=len(parte) * 40 + 400)
            usos.append(u)
            d = ollama._json_seguro(txt)
            cand = d.get("queries") if isinstance(d, dict) else None
            if isinstance(cand, list) and len(cand) >= len(parte) * 0.9:
                q = [str(x).strip().strip('"') for x in cand]
                break
        if q is None:
            raise RuntimeError("o Claude não devolveu a lista de buscas no formato esperado")
        while len(q) < len(parte):
            q.append(q[-1])
        out += q[:len(parte)]
    uso = _soma(*usos)
    log(f"buscas de imagem Claude ({MODELO}): {len(out)} buscas, {uso['tokens_in'] + uso['tokens_out']} tokens, ~US$ {max(uso['usd'], uso['usd_equiv']):.3f}")
    return out, uso
