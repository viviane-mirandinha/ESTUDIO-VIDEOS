# texto.py — frases e "shots" (trechos de ~3-6 s) a partir do words.json do whisper
import re


def colar_partidos(words):
    """O Whisper às vezes parte uma palavra: "0" ",40" → "0,40"; "a" ".C.," → "a.C.,". Junta (tempo do 1º ao último)."""
    out = []
    for w in words:
        t = str(w.get("w", ""))
        if out and ((re.match(r"^[.,]\d", t) and re.search(r"\d$", out[-1]["w"])) or
                    (re.match(r"^\.[A-Za-z]\.", t) and re.fullmatch(r"[A-Za-z]", out[-1]["w"]))):
            p = dict(out[-1]); p["w"] = p["w"] + t; p["e"] = w.get("e", p["e"]); out[-1] = p
            continue
        out.append(w)
    return out


def descricao_estilo_copiado(an):
    """Frase simples pro cartão do estilo copiado (sem números técnicos)."""
    an = an or {}
    plano = an.get("plano_medio_s") or 0
    ritmo = f"troca de cena a cada ~{max(1, round(plano))} s" if plano else "mesmo ritmo de cortes"
    leg = ("com legenda" + (" no centro" if an.get("legenda_pos") == "centro" else " embaixo" if an.get("legenda_pos") == "baixo" else "")) if an.get("tem_legenda") else "sem legenda"
    voz = "com narração" if an.get("tem_narracao") else "sem narração"
    txt = f"Copiado de um {'short' if an.get('formato') == 'short' else 'vídeo'}: {ritmo}, {leg} e {voz}."
    pecas = [str(e.get("nome", "")).lower() for e in an.get("pecas") or [] if e.get("nome")]
    return txt + (" Na tela: " + ", ".join(pecas) + "." if pecas else "")


def frases(words):
    """Agrupa palavras em frases (termina em . ! ? …). Cada frase: {texto, s, e, words}."""
    words = colar_partidos(words)
    out, g = [], []
    for i, w in enumerate(words):
        g.append(w)
        fim = re.search(r"[.!?…]$", w["w"]) or i == len(words) - 1
        if fim:
            out.append({"texto": " ".join(x["w"] for x in g), "s": g[0]["s"], "e": g[-1]["e"], "words": g})
            g = []
    return out


def shots(words, min_dur=2.2, max_dur=6.0):
    """Trechos de ~3-6 s respeitando frases: frase longa é dividida (na vírgula ou no meio),
    frase curtinha é colada na seguinte. Cada shot: {texto, s, e, words}."""
    out = []
    for f in frases(words):
        partes = _dividir(f["words"], max_dur)
        for p in partes:
            out.append({"texto": " ".join(x["w"] for x in p), "s": p[0]["s"], "e": p[-1]["e"], "words": p})
    # cola shots curtos no seguinte
    merged = []
    for s in out:
        if merged and (merged[-1]["e"] - merged[-1]["s"]) < min_dur:
            m = merged[-1]
            m["words"] += s["words"]
            m["texto"] += " " + s["texto"]
            m["e"] = s["e"]
        else:
            merged.append(dict(s))
    return merged


def _dividir(ws, max_dur):
    dur = ws[-1]["e"] - ws[0]["s"]
    if dur <= max_dur or len(ws) < 4:
        return [ws]
    n = max(2, round(dur / (max_dur * 0.8)))
    alvo = dur / n
    partes, atual, t0 = [], [], ws[0]["s"]
    for i, w in enumerate(ws):
        atual.append(w)
        virgula = w["w"].endswith((",", ";", ":"))
        passou = w["e"] - t0 >= alvo
        if (virgula and w["e"] - t0 >= alvo * 0.6) or (passou and len(atual) >= 3):
            if i < len(ws) - 2 and len(partes) < n - 1 and not re.match(r"(?i)^[ad]\.c\.", ws[i + 1]["w"]):   # não separa "2630" de "a.C."
                partes.append(atual)
                atual, t0 = [], ws[i + 1]["s"]
    if atual:
        partes.append(atual)
    return partes


def acha_cta(words, chaves=("like", "curt", "inscrev", "comenta")):
    """Tempo (s) das falas de CTA (pra colocar texto de apoio na tela)."""
    t = []
    for w in words:
        lw = w["w"].lower()
        if any(k in lw for k in chaves):
            if not t or w["s"] - t[-1] > 8:
                t.append(w["s"])
    return t
