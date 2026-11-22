# planejar.py — escreve o plano de cenas (plano.json) a partir do roteiro falado (words.json). Modo grátis.
#   python kits/blender-3d/planejar.py <pasta-do-video> [--sem-ia] [--refazer]
# Divide a fala em cenas de ~2,5–6 s (sem cortar frase) e escolhe, por cena, expressão, pose, enquadramento,
# objeto e lado. Usa o Ollama (local, zero token) quando está no ar; sem ele (ou se ele errar) usa regras simples.
# pedido.json (opcional) pode trazer: predefinicao, cenario, modelo_ollama.
import json, re, sys
from pathlib import Path

KIT = Path(__file__).resolve().parent
RAIZ = KIT.parent.parent
sys.path.insert(0, str(RAIZ / "editor" / "fabrica"))

from gerar_cena import ENUMS   # noqa: E402  (valores aceitos pelo plano)

CHAVES_GARAGEM = r"carro|motor|oficina|mec[aâ]nic|combust|gasolina|pneu|pe[cç]a|freio|ve[ií]culo|autom[oó]vel|garagem"
CHAVES_ATELIE = r"arte|artista|criativ|desenh|pintur|design|estúdio|estudio|ateli[eê]|projeto|casa"
EXPR_TRISTE = r"erro|problema|ruim|falha|difícil|dificil|medo|perd|quebr|fracass|dor|cansa|triste"
EXPR_FELIZ = r"incr[ií]vel|melhor|sucesso|ganh|funciona|conseg|ótimo|otimo|alegria|feliz|vit[oó]ria"
POSE_APONTA = r"olha|veja|aqui|este|esta|isso|repare|note"


def cenario_do_texto(texto: str, pedido: dict) -> str:
    if pedido.get("cenario") in ENUMS["cenario"]:
        return pedido["cenario"]
    t = texto.lower()
    if re.search(CHAVES_GARAGEM, t):
        return "garagem"
    if re.search(CHAVES_ATELIE, t):
        return "atelie"
    return "infinito"


def por_regras(i: int, texto: str, total: int) -> dict:
    t = texto.lower()
    pergunta, exclama = "?" in texto, "!" in texto
    if re.search(EXPR_TRISTE, t):
        expr = "cansado" if "cansa" in t else "triste"
    elif pergunta:
        expr = "pensativo"
    elif exclama or re.search(EXPR_FELIZ, t):
        expr = "animado"
    else:
        expr = "feliz"
    pose = "pensando" if pergunta else "comemorando" if (exclama and re.search(EXPR_FELIZ, t)) else "apontando" if re.search(POSE_APONTA, t) else "parado"
    enq = "close" if (pergunta or exclama) else ["medio", "medio", "lado", "geral", "medio", "alto"][i % 6]
    objeto = "carro" if re.search(r"carro|motor|ve[ií]culo", t) else "gato" if "gato" in t else "galao" if re.search(r"combust|gasolina|gal[aã]o", t) else "nenhum"
    lado = "esq" if objeto in ("carro", "gato") else "centro"
    if i == 0:
        enq = "medio"
    if i == total - 1 and not exclama:
        expr = "feliz" if expr in ("triste", "cansado") else expr
    return {"expressao": expr, "pose": pose, "enquadramento": enq, "objeto": objeto, "lado": lado}


def por_ia(lote: list, modelo: str) -> dict:
    """Pede ao Ollama as escolhas de um lote de cenas. Devolve {numero: {campos}}; qualquer erro → {}."""
    from lib import ollama
    lista = "\n".join(f'{n}. "{c["texto"]}"' for n, c in lote)
    valores = {k: ENUMS[k] for k in ("expressao", "pose", "enquadramento", "objeto", "lado")}
    prompt = (
        "You direct a short 3D animated video with ONE cartoon character who narrates. For each numbered scene (Portuguese narration) choose how the "
        "character looks and how the camera frames it. Use ONLY these values:\n"
        + "\n".join(f"- {k}: {', '.join(v)}" for k, v in valores.items())
        + "\nRules: vary the camera between scenes; use 'close' for emotional lines; use objeto only if the narration mentions it (carro=car, gato=cat, "
        "galao=fuel can), otherwise 'nenhum'; lado 'esq' when an object is shown, else 'centro'.\n"
        f"Scenes:\n{lista}\n"
        'Answer ONLY JSON: {"cenas":[{"n":1,"expressao":"...","pose":"...","enquadramento":"...","objeto":"...","lado":"..."}]}'
    )
    try:
        d = ollama._json_seguro(ollama.gerar(prompt, modelo, json_mode=True, temperatura=0.4, num_predict=900, timeout=240)) or {}
    except Exception as e:
        print(f"(Ollama indisponível ou falhou: {str(e)[:120]} — uso as regras)", flush=True)
        return {}
    r = {}
    for c in d.get("cenas", []) if isinstance(d, dict) else []:
        try:
            n = int(c["n"])
        except (KeyError, TypeError, ValueError):
            continue
        ok = {k: c[k] for k in valores if c.get(k) in valores[k]}
        if ok:
            r[n] = ok
    return r


def planejar(pasta: Path, usar_ia: bool = True, refazer: bool = False) -> Path:
    destino = pasta / "plano.json"
    if destino.exists() and not refazer:
        print(f"plano.json já existe ({destino}); use --refazer para escrever de novo.")
        return destino
    wf = pasta / "words.json"
    if not wf.exists():
        sys.exit(f"Falta {wf} (rode o preparo da voz antes).")
    from lib.texto import shots
    palavras = json.loads(wf.read_text(encoding="utf-8"))
    cenas_fala = shots(palavras, min_dur=2.5, max_dur=6.0)
    if not cenas_fala:
        sys.exit("Não achei fala em words.json.")
    pedido = {}
    if (pasta / "pedido.json").exists():
        pedido = json.loads((pasta / "pedido.json").read_text(encoding="utf-8"))
    cenario = cenario_do_texto(" ".join(c["texto"] for c in cenas_fala), pedido)
    n = len(cenas_fala)
    escolhas = {}
    if usar_ia:
        modelo = pedido.get("modelo_ollama") or pedido.get("modelo") or "qwen2.5:7b"
        for ini in range(0, n, 8):
            lote = [(i + 1, cenas_fala[i]) for i in range(ini, min(n, ini + 8))]
            escolhas.update(por_ia(lote, modelo))
    cenas = []
    fim_anterior = 0.0
    for i, c in enumerate(cenas_fala):
        base = por_regras(i, c["texto"], n)
        base.update(escolhas.get(i + 1, {}))
        if base["objeto"] in ("carro", "gato") and base["lado"] == "centro":
            base["lado"] = "esq"   # com objeto em cena o personagem sai do centro, para os dois caberem no quadro vertical
        # cena começa onde a anterior terminou (sem buraco na fala) e a última vai até o fim da voz
        de = fim_anterior if i else 0.0
        ate = cenas_fala[i + 1]["s"] if i + 1 < n else c["e"] + 0.6
        fim_anterior = ate
        cenas.append({"id": i + 1, "de": round(de, 2), "ate": round(ate, 2), "texto": c["texto"], "cenario": cenario, **base})
    plano = {"cenas": cenas}
    if pedido.get("predefinicao"):
        plano["predefinicao"] = pedido["predefinicao"]
    for k in ("personagem", "render"):   # ajustes feitos na tela de criar (por cima da predefinição)
        if isinstance(pedido.get(k), dict) and pedido[k]:
            plano[k] = pedido[k]
    destino.write_text(json.dumps(plano, ensure_ascii=False, indent=2), encoding="utf-8")
    origem = "Ollama + regras" if escolhas else "regras"
    print(f"plano.json: {n} cenas ({origem}), cenário '{cenario}' -> {destino}")
    return destino


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    planejar(Path(a[0]).resolve(), usar_ia="--sem-ia" not in a, refazer="--refazer" in a)
