# planejador.py — transforma QUALQUER narração (words.json do Whisper) em cenas do kit animacao-2d.
# Entrada: words [{w,s,e}], título, tema, canal, idioma → itens de edit.json (type "scene", by "template").
# Garante POR CONSTRUÇÃO as mesmas regras do checar_variedade.py (tipo não repete em 3, mesmo plano só depois de 12, ≤2 caminhadas em 5,
# ≤2 cortes em 8 s, cena entre 3,4 e 6 s...). O texto na tela vem sempre da fala; nada é inventado.
import json, re, pathlib, unicodedata

K = pathlib.Path(__file__).parent
CAT = {k: v for k, v in json.loads((K / "catalogo.json").read_text(encoding="utf-8")).items() if not k.startswith("_")}
LOCAIS = ["biblioteca", "rua", "portico", "noite", "palacio", "mercado", "montanha", "papel"]
ICONES = ("alerta atitude balanca balao bandeira bateria bau calendario casa celular coracao coracaoPartido coroa curativo discussao economia escolhas "
          "escudo espadas estrela fantasma gema globo lagrima laptop livro martelo multidao olho opiniao pao passado pedra pensam pergaminho peste polegar "
          "porta relogio resposta resultado sacola senado sino sofa sol solo sorriso").split()


def norm(s):
    return re.sub(r"[^a-z0-9 ]", "", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode())


# palavra-chave (já sem acento) → ícone
MAP_IC = [(r"tempo|hora|relogio|minuto|segundo|time|clock", "relogio"), (r"\bano|seculo|calendario|data|year|century", "calendario"),
          (r"livro|ler\b|leitura|escrev|texto|book|read", "livro"), (r"carta|diario|pergaminho|registro|letter", "pergaminho"),
          (r"dinheiro|rico|riqueza|ouro|salario|econom|preco|money|rich", "economia"), (r"coroa|imperador|rei\b|poder|governo|lider|emperor|king|power", "coroa"),
          (r"senado|lei\b|politic|law|senate", "senado"), (r"coracao|amor|amar|paixao|love|heart", "coracao"),
          (r"triste|chora|dor\b|sofr|luto|perda|pain|cry|loss|sad", "lagrima"), (r"raiva|odio|ira\b|furia|anger|rage", "raiva"),
          (r"medo|ansied|preocup|panico|fear|anxi|worr", "alerta"), (r"morte|morrer|morre|fim\b|death|die", "fantasma"),
          (r"mente|pensa|ideia|razao|filosof|mind|think|idea", "pensam"), (r"mundo|global|planeta|sociedade|world|society", "globo"),
          (r"pessoas|gente|multidao|outros|people|crowd|others", "multidao"), (r"celular|redes|internet|notific|telefone|phone|social", "celular"),
          (r"computador|trabalho|projeto|tela|emprego|work|job|screen", "laptop"), (r"escolh|decis|caminho|dilema|choice|decide|path", "escolhas"),
          (r"justica|equilibr|balanc|moral|justice|balance", "balanca"), (r"forca|forte|coragem|resilien|protec|defesa|strong|courage", "escudo"),
          (r"guerra|batalha|conflito|lutar|luta|war|battle|fight", "espadas"), (r"feliz|alegria|sorri|prazer|happy|joy|smile", "sorriso"),
          (r"\bsol\b|luz|manha|sun|light|morning", "sol"), (r"casa|lar\b|familia|home|family|house", "casa"),
          (r"olhar|ver\b|observ|perceb|olho|look|see|watch", "olho"), (r"pedra|obstaculo|muro|barreira|problema|stone|obstacle|problem", "pedra"),
          (r"porta|oportunidade|comeco|entrar|door|opportunity|begin", "porta"), (r"futuro|passado|memoria|lembr|past|future|memory", "passado"),
          (r"resultado|resposta|conclus|answer|result", "resposta"), (r"estrela|sonho|destino|star|dream|destiny", "estrela"),
          (r"doenca|saude|peste|health|disease", "peste"), (r"bandeira|pais|nacao|country|nation", "bandeira"),
          (r"valios|tesouro|joia|treasure", "gema"), (r"vida|viver|life|live", "solo")]
NOMES = [(r"marco aurelio|marcus aurelius", "marco", "Marco Aurélio"), (r"seneca", "seneca", "Sêneca"), (r"epicteto|epictetus", "epicteto", "Epicteto"),
         (r"zenao|zeno", "zenao", "Zenão"), (r"crates", "crates", "Crates")]
LOCAL_RX = [(r"livro|ler\b|leitura|estud|escola|biblioteca|book|read|study|library", "biblioteca"), (r"rua|cidade|praca|encontr|vizinh|street|city|square", "rua"),
            (r"templo|portico|ensin|disciplin|temple|teach|lesson", "portico"), (r"noite|sono|dormir|escuro|morte|sonho|night|sleep|dark|death|dream", "noite"),
            (r"palacio|imperador|imperio|poder|governo|rei\b|palace|emperor|king|power", "palacio"), (r"mercado|dinheiro|comprar|vender|ganhar|market|money|buy|sell", "mercado"),
            (r"montanha|natureza|mar\b|rio\b|caminho|jornada|mountain|nature|sea|journey", "montanha")]
STOP = set("para como mais mas porque quando entao tambem sobre ainda mesmo muito depois antes essa esse esta este isso aquilo seus suas dele dela eles elas voce voces nossa nosso pelos pelas where which would could should there their about because".split())
SEGUNDA = re.compile(r"\b(voce|voces|seu|sua|seus|suas|te|contigo|you|your|tu|tus)\b", re.I)


def fala_de(ws):
    return " ".join(w["w"] for w in ws)


def limpa(t):
    return re.sub(r"^[\W_]+|[\W_]+$", "", t)


def chave(ws, maxc=22, n=2):
    """1–2 palavras fortes DA FALA (número + unidade, senão as mais longas, na ordem em que aparecem)."""
    toks = [limpa(w["w"]) for w in ws]
    for i, t in enumerate(toks):
        if re.fullmatch(r"\d[\d.,]*", t) and i + 1 < len(toks):
            return f"{t} {toks[i+1]}"[:maxc].strip()
    cand = [(len(t), i, t) for i, t in enumerate(toks) if len(t) >= 6 and norm(t) not in STOP and not t.isdigit()]
    if not cand:
        cand = [(len(t), i, t) for i, t in enumerate(toks) if len(t) >= 4 and norm(t) not in STOP]
    top = sorted(cand, reverse=True)[:n]
    out = " ".join(t for _, _, t in sorted(top, key=lambda x: x[1]))
    return out[:maxc].rstrip() if out else (limpa(ws[0]["w"]) if ws else "")


def icone(txt, k=0):
    t = norm(txt)
    for rx, ic in MAP_IC:
        if re.search(rx, t):
            return ic
    return ["pensam", "livro", "estrela", "olho", "balao", "escolhas", "gema", "porta"][k % 8]


def tempo_de(ws, palavra, ini):
    p = norm(palavra).split(" ")[0] if palavra else ""
    for w in ws:
        if p and norm(limpa(w["w"])).startswith(p[:5]):
            return round(max(0.3, w["s"] - ini), 2)
    return round(min(1.2, (ws[0]["s"] - ini) + 0.6), 2) if ws else 0.8


def agrupar(words, mn=3.6, mx=6.0):
    """cortes nos finais de frase/oração: cena entre mn e mx segundos (a última nunca fica curta demais)"""
    grupos, atual = [], []
    for w in words:
        atual.append(w)
        el = w["e"] - atual[0]["s"]
        fim = bool(re.search(r"[.!?…:;]$", w["w"]))
        vir = bool(re.search(r",$", w["w"]))
        if (el >= mn and (fim or (vir and el >= mn + 0.8))) or el >= mx:
            grupos.append(atual)
            atual = []
    if atual:
        if grupos and atual[-1]["e"] - atual[0]["s"] < 3.0 and (atual[-1]["e"] + 1.2 - grupos[-1][0]["s"]) <= 6.8:
            grupos[-1] += atual       # sobra curta cabe na última cena
        else:
            grupos.append(atual)      # senão fica como cena própria (curta, mas dentro das regras)
    return grupos


class Plano:
    """mesmas regras do checar_variedade.py, aplicadas ANTES de escolher cada cena"""

    def __init__(self):
        self.h = []

    def ok(self, t):
        f, h = CAT[t], self.h
        if t in h[-3:]:
            return False
        for x in h[-12:]:
            g = CAT[x]
            if x != t and (g["local"], g["vista"], g["acao"]) == (f["local"], f["vista"], f["acao"]):
                return False
        if h:
            g = CAT[h[-1]]
            if g["local"] == f["local"] and sum(g[k] == f[k] for k in ("vista", "acao", "camera")) > 1:
                return False
        if len(h) >= 4 and all(CAT[x]["vista"] == f["vista"] for x in h[-4:]):
            return False
        if sum(CAT[x]["acao"] == "andar" for x in h[-4:]) + (f["acao"] == "andar") > 2:
            return False
        return True


def planejar(words, titulo, tema="", canal="", idioma="pt-BR", ia=None, semente=0, sem_anda=False, dur=None):
    words = [w for w in words if limpa(w.get("w", ""))]
    dur = round(dur or (words[-1]["e"] + 1.2), 2)
    nt = norm(" ".join(w["w"] for w in words))
    prot = "zenao"
    for rx, q, _ in NOMES:
        if re.search(rx, nt):
            prot = q
            break
    grupos = agrupar(words)
    ini = [0.0]
    for gi, g in enumerate(grupos[1:], 1):       # pausa longa: a próxima cena entra durante o silêncio (nenhuma cena passa de ~8 s)
        ini.append(round(max(ini[-1] + 3.4, min(g[0]["s"] - 0.15, grupos[gi - 1][-1]["e"] + 2.4)), 2))
    fim = ini[1:] + [dur]
    n = len(grupos)
    pl = Plano()
    itens = []
    idx_local = semente
    pens = {}
    if ia:
        try:
            pens = ia(grupos) or {}
        except Exception:
            pens = {}
    ultimo_local = None
    for k, g in enumerate(grupos):
        s, e = ini[k], fim[k]
        D = round(e - s, 2)
        ws = g
        fala = fala_de(ws)
        nf = norm(fala)
        q = pens.get(k, {})
        L = q.get("local") if q.get("local") in LOCAIS else None
        if not L:
            L = next((loc for rx, loc in LOCAL_RX if re.search(rx, nf)), None)
        quem = prot
        if SEGUNDA.search(fala) and k % 3 != 0:
            quem = "voce" if k % 2 else "homem"
        for rx, qq, _ in NOMES:
            if re.search(rx, nf):
                quem = qq
                break
        txt = q.get("txt") if isinstance(q.get("txt"), str) and 2 <= len(q["txt"]) <= 24 else chave(ws)
        ic = q.get("ic") if q.get("ic") in ICONES else icone(fala, k)
        t0 = tempo_de(ws, txt, s)
        pergunta = "?" in fala
        numero = re.search(r"\d[\d.,]*\s+\S", fala)
        aspas = re.findall(r"[“\"«]([^”\"»]{12,120})[”\"»]", fala)
        contra = re.split(r"\b(?:mas|porém|porem|contudo|entretanto|but|however|pero)\b", fala, maxsplit=1, flags=re.I)
        partes = [limpa(p) for p in re.split(r",| e ", fala) if len(limpa(p).split()) <= 3 and limpa(p)]
        cands = []   # (tipo, params), em ordem de preferência
        if k == 0:
            cands = [("abertura", {"quem": prot, "titulo": titulo, "sub": canal or ""})]
        elif k == n - 1:
            cands = [("cartao", {"l1": (canal or "").upper(), "l2": titulo[:44], "fs": 64 if len(titulo) > 20 else 90, "ic": "livro", "t": [0.8, 2.2]})]
        else:
            if aspas:
                cands.append(("citacao", {"frase": aspas[0], "tam": 96 if len(aspas[0]) <= 40 else 72 if len(aspas[0]) <= 70 else 56}))
            if len(contra) == 2 and len(contra[0].split()) >= 2 and len(contra[1].split()) >= 2:
                a = chave([{"w": x} for x in contra[0].split()], 18, 2)
                b = chave([{"w": x} for x in contra[1].split()], 18, 2)
                nao, sim = {"pt": ("NÃO", "SIM"), "en": ("NO", "YES"), "es": ("NO", "SÍ")}.get(idioma[:2], ("NÃO", "SIM"))
                cands.append(("contraste2", {"tA": nao, "tB": sim, "icA": icone(contra[0], k), "icB": icone(contra[1], k + 3), "a": a, "b": b,
                                              "mA": "x", "mB": "ok", "t": [0.6, round(max(1.5, D * .5), 2)]}))
            if numero:
                m = re.search(r"(\d[\d.,]*)\s+(\S+)", fala)
                nm = f"{m.group(1)} {limpa(m.group(2))}"[:20]
                cands.append(("cartao", {"l2": nm.upper(), "fs": 110 if len(nm) <= 10 else 80, "sub": chave(ws, 24, 2), "ic": ic, "t": [0.8, round(D * .5, 2)]}))
            if len(partes) >= 3 and all(len(p.split()) <= 3 for p in partes[:3]):
                its = [{"ic": icone(p, j + k), "txt": " ".join(p.split()[:2])} for j, p in enumerate(partes[:4])]
                cands.append(("listaChar", {"quem": quem if quem in ("zenao", "marco", "epicteto", "seneca", "crates", "voce") else prot, "items": its,
                                            "t": [tempo_de(ws, p, s) for p in partes[:4]]}))
            nome_enc = next(((qq, nn) for rx, qq, nn in NOMES if re.search(rx, nf)), None)
            if nome_enc and k % 2 == 0:
                cands.append(("retrato", {"quem": nome_enc[0], "nome": nome_enc[1], "t": [t0, t0 + 1.2]}))
            if pergunta:
                cands.append(("pergunta2", {"ic": ic, "txt": "\n".join(x.strip() for x in re.findall(r".{1,14}(?:\s|$)", txt)) or txt, "mark": "", "t": [t0]}))
        # famílias por local (sempre disponíveis: garantem que existe um candidato válido)
        seen = []
        for x in ([L] if L else []) + [LOCAIS[(idx_local + j) % len(LOCAIS)] for j in range(len(LOCAIS))]:
            if x not in seen:
                seen.append(x)
        pos = "d" if k % 2 else "e"
        para = f"vai até o fundo do cenário enquanto fala: {fala[:60]}"
        for loc in seen:
            if loc == ultimo_local and len(seen) > 1:
                continue
            base = {"quem": quem, "txt": txt, "pos": pos, "t": [t0], "por": para}
            fam = ["pos_%s_frente", "expl_%s_lado", "cost_%s", "pos_%s_lado", "anda_%s", "expl_%s_frente"]
            if sem_anda:
                fam = [f for f in fam if not f.startswith("anda")]
            if pergunta and k % 2 == 0:
                fam = ["dial_%s"] + fam
            for f in fam[(k % 3):] + fam[:(k % 3)]:
                t = f % loc
                if t in CAT:
                    p = dict(base)
                    if f.startswith("dial"):
                        p.update({"quem2": "voce", "a": txt, "b": chave(ws[len(ws) // 2:], 20, 1), "t": [t0, round(max(1.2, D * .55), 2)]})
                    if f.startswith("anda") and quem in ("voce", "homem"):
                        p["quem"] = prot
                    if f.startswith("cost"):
                        p.pop("quem", None)
                    cands.append((t, p))
        escolhido = next(((t, p) for t, p in cands if t in CAT and pl.ok(t)), None)
        if not escolhido:
            escolhido = next(((t, p) for t, p in cands if t in CAT and t not in pl.h[-3:]), cands[0])
        t, p = escolhido
        pl.h.append(t)
        idx_local += 1
        partes_t = t.split("_")
        if len(partes_t) >= 2 and partes_t[1] in LOCAIS:
            ultimo_local = partes_t[1]
        it = {"id": f"c{k+1:02d}", "type": "scene", "track": "fundo", "by": "template", "label": t, "start": round(s, 2), "dur": D, "fala": fala,
              "porque": "", "props": {"scene": t, "params": p}}
        if CAT[t]["acao"] == "andar":
            it["porque"] = p.get("por", para)
        if D > 6.0:
            it["longa"] = "plano calmo com revelação em sequência no ritmo da fala"
        itens.append(it)
    return itens, dur


def legendas(words, por=4):
    """grupos de até 4 palavras com tempo (para o formato vertical)"""
    out, g = [], []
    for w in words:
        g.append(w)
        if len(g) >= por or re.search(r"[.!?,;:]$", w["w"]):
            out.append({"s": round(g[0]["s"], 2), "e": round(g[-1]["e"] + 0.15, 2), "t": " ".join(x["w"] for x in g)})
            g = []
    if g:
        out.append({"s": round(g[0]["s"], 2), "e": round(g[-1]["e"] + 0.15, 2), "t": " ".join(x["w"] for x in g)})
    for i in range(len(out) - 1):
        out[i]["e"] = min(out[i]["e"], out[i + 1]["s"])
    return out
