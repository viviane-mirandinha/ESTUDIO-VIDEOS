# claude_rev.py — "Revisar roteiro com o Claude" (opcional, GASTA TOKENS da conta do usuário).
# Sem chave: o painel só monta e copia o pedido pra colar no chat do Claude. Com chave (Ajustes): chama a API.
import anthropic

MODELO = "claude-sonnet-5-5"          # Sonnet mais recente (pedido do dono)
PRECO_IN, PRECO_OUT = 2.00, 10.00     # US$ por milhão de tokens (entrada / saída)

INSTRUCOES = """Revise o roteiro de narração abaixo para um vídeo do YouTube, em {idioma}. Regras:
1. Gancho forte nos primeiros 3-5 segundos (a 1ª frase quebra o padrão; sem "olá", sem apresentação).
2. Corte enrolação, repetição e loop (ideias repetidas ou recomeços da explicação).
3. Frases curtas, boas de narrar em voz alta.
4. CTA de like espalhado: uma vez perto do meio e uma no final, de forma natural e ligada ao conteúdo.
5. Confira os fatos: não invente nada. Tudo que for duvidoso, marque no fim numa lista "FATOS A CONFERIR".
Responda com o roteiro revisado (só a narração, sem títulos nem marcadores) e, depois de uma linha "---", a lista FATOS A CONFERIR."""


def pedido(roteiro, idioma="português do Brasil", tema=""):
    cab = INSTRUCOES.format(idioma=idioma)
    return cab + (f"\n\nTema do vídeo: {tema}" if tema else "") + "\n\nROTEIRO:\n" + roteiro.strip()


def estimar(chave, texto_pedido, palavras_roteiro):
    c = anthropic.Anthropic(api_key=chave)
    r = c.messages.count_tokens(model=MODELO, messages=[{"role": "user", "content": texto_pedido}])
    tin = r.input_tokens
    tout = int(palavras_roteiro * 1.9) + 1500          # roteiro revisado + lista + raciocínio (estimativa)
    return {"tokens_entrada": tin, "tokens_saida_estimados": tout, "tokens": tin + tout,
            "custo_usd": round(tin / 1e6 * PRECO_IN + tout / 1e6 * PRECO_OUT, 4), "modelo": MODELO}


def revisar(chave, texto_pedido):
    c = anthropic.Anthropic(api_key=chave, timeout=600)
    r = c.beta.messages.create(model=MODELO, max_tokens=16000, betas=["server-side-fallback-2026-07-01"], fallbacks="default",
                               messages=[{"role": "user", "content": texto_pedido}])
    if r.stop_reason == "refusal":
        raise RuntimeError("O Claude recusou esse pedido.")
    txt = "".join(b.text for b in r.content if getattr(b, "type", "") == "text").strip()
    rot, _, fatos = txt.partition("\n---")
    u = r.usage
    custo = (u.input_tokens / 1e6 * PRECO_IN) + (u.output_tokens / 1e6 * PRECO_OUT)
    return {"roteiro": rot.strip(), "fatos": [l.strip(" -•*") for l in fatos.splitlines() if l.strip(" -•*") and "FATOS A CONFERIR" not in l.upper()],
            "tokens": u.input_tokens + u.output_tokens, "custo_usd": round(custo, 4), "modelo": MODELO}
