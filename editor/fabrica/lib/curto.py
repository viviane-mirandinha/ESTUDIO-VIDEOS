# curto.py — roteiro de SHORT (30-90 s) pelo Ollama local. Escrito do zero pro Estúdio de Vídeos. Zero token Claude.
# Regras: gancho nos 1-2 primeiros segundos (frase de até 8 palavras), frases curtas, 1 ideia só, fecho com virada,
# nada de fato inventado, sem saudação, sem CTA no meio (short é curto demais).
# Obs.: o qwen2.5:7b escreve curto em modo JSON → a locução sai em texto puro, o título numa 2ª chamada pequena,
# e se faltar tamanho ele completa (sem repetir: frases parecidas são cortadas em código).
import re
from difflib import SequenceMatcher

from . import ollama
from .util import log

LINGUA = {"pt-BR": "português do Brasil", "en-US": "American English", "es-MX": "español de México"}


def _limpa(t):
    linhas = [re.sub(r"^\s*(\d+[.)-]|[-•])\s*", "", x).strip() for x in str(t or "").splitlines()]
    linhas = [x if re.search(r"[.!?…]$", x) else x + "." for x in linhas if x]
    t = " ".join(linhas)
    t = re.sub(r"[\[\]#*_\"“”]", "", t)
    t = re.sub(r"^\s*(aqui (vai|está|segue)[^:]{0,40}:|(roteiro|locução|narração|texto|continuação)\s*:)\s*", "", t, flags=re.I)
    return re.sub(r"\s+", " ", t).strip()


def _sem_repeticao(texto):
    frs = [f.strip() for f in re.split(r"(?<=[.!?…])\s+", texto) if f.strip()]
    out = []
    for f in frs:
        if any(SequenceMatcher(None, f.lower(), g.lower()).ratio() >= 0.75 for g in out):
            continue
        out.append(f)
    return " ".join(out)


def roteiro_short(tema, segundos, canal="", modelo=None, idioma="pt-BR", fatos=""):
    """Devolve {"titulo": str (≤ 6 palavras, vai no topo do vídeo), "roteiro": str (só a locução)}."""
    modelo = modelo or ollama.MODELO_PADRAO
    lingua = LINGUA.get(idioma, LINGUA["pt-BR"])
    # QA 24/10: medido no painel — edge-tts pt-BR fala ~2,1 palavras/s + ~0,8 s de pausa entre frases
    # (short de 30 s saía com 53 s). Cada frase de ~10 palavras ≈ 5,6 s de vídeo.
    palavras = max(40, int(float(segundos) * 1.9))
    frases_alvo = max(5, round(float(segundos) / 5.6))
    regras = f"""Regras obrigatórias:
1. A PRIMEIRA frase é o gancho: no máximo 8 palavras, dita em 1-2 segundos, quebra de padrão (afirmação surpreendente ou pergunta curiosa). Nada de "olá" ou introdução.
2. Depois, 1 ideia só, linear, cada frase traz informação NOVA (nunca repita uma frase ou ideia). Frases curtas (até 14 palavras), ritmo rápido.
3. Termine com uma virada ou conclusão forte em 1 frase. Sem pedir like, sem "inscreva-se".
4. Use SOMENTE fatos reais e amplamente conhecidos. NUNCA invente número, data, nome ou citação. Se não tiver certeza de um número, não use número.
5. Idioma: {lingua}. Narrador em terceira pessoa. Sem emojis, títulos, marcadores, aspas ou colchetes: só a locução pura."""
    prompt = f"""Você escreve roteiros de SHORTS virais (YouTube Shorts / Reels / TikTok) sem rosto, narrados por voz.
Tema: {tema}

{regras}
6. Tamanho: EXATAMENTE {frases_alvo} frases, cada uma com 8 a 13 palavras, TODAS sobre "{tema}" (vídeo de ~{int(segundos)} segundos).
{fatos}
Responda SOMENTE com as {frases_alvo} frases numeradas, uma por linha (1. ... 2. ... ), nada mais."""
    melhor = ""
    for tent in range(3):
        try:
            r = _sem_repeticao(_limpa(ollama.gerar(prompt, modelo, temperatura=0.75, num_predict=palavras * 4 + 300)))
        except Exception as e:
            log(f"Ollama (short) falhou: {str(e)[:120]}")
            continue
        n = len(r.split())
        log(f"short: tentativa {tent + 1}: {n} palavras (alvo {palavras})")
        if n > len(melhor.split()):
            melhor = r
        if n >= palavras * 0.85:
            break
    for _ in range(2):   # o modelo pequeno costuma escrever curto → pede a continuação, sem repetir
        n = len(melhor.split())
        if n < 20 or n >= palavras * 0.85:
            break
        falta = palavras - n
        p2 = f"""Roteiro de um short sobre "{tema}" (começo já escrito):
{melhor}

Escreva SÓ a continuação: mais {max(3, round(falta / 9))} frases curtas (8 a 13 palavras cada, em {lingua}) com informações NOVAS sobre "{tema}" que ainda
não apareceram acima, e a última frase é uma virada ou conclusão forte. Não mude de assunto. {regras}
Responda SOMENTE com as frases novas numeradas, uma por linha."""
        try:
            cont = _limpa(ollama.gerar(p2, modelo, temperatura=0.65, num_predict=falta * 4 + 200))
            novo = _sem_repeticao(melhor + " " + cont)
            if len(novo.split()) > n + 6:
                melhor = novo
                log(f"short: completado para {len(melhor.split())} palavras")
        except Exception as e:
            log(f"Ollama (completar short) falhou: {str(e)[:120]}")
            break
    frs = [f for f in re.split(r"(?<=[.!?…])\s+", melhor.strip()) if f.strip()]
    if len(frs) > frases_alvo + 1 and len(melhor.split()) > palavras * 1.2:   # QA: passou muito do tempo → corta o meio, mantém o fecho
        melhor = " ".join(frs[:frases_alvo] + frs[-1:])
        log(f"short: cortado para {len(melhor.split())} palavras (alvo {palavras})")
    if len(melhor.split()) < 25:
        raise RuntimeError("A IA local não conseguiu escrever o roteiro do short. Confira se o Ollama está aberto e tente de novo.")
    titulo = ""
    try:
        d = ollama._json_seguro(ollama.gerar(
            f"""Crie o título curto que fica fixo no topo deste short (até 6 palavras, em {lingua}, desperta curiosidade, fiel ao texto,
sem ponto final, sem emoji, sem aspas).
Texto: {melhor[:900]}
Responda SOMENTE JSON: {{"titulo": "..."}}""", modelo, json_mode=True, temperatura=0.5, num_predict=60, timeout=120))
        titulo = re.sub(r"[\"“”.]+$", "", _limpa(d.get("titulo")))[:60]
    except Exception:
        pass
    if not titulo or len(titulo.split()) > 9:
        titulo = " ".join(tema.split()[:7])
    return {"titulo": titulo, "roteiro": melhor}
