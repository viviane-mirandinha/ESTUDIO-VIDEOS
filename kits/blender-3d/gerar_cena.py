# gerar_cena.py — transforma o PLANO DE CENAS (plano.json) em cena3d.tsx (modo grátis, sem escrever código 3D).
#   python kits/blender-3d/gerar_cena.py <pasta-do-video>
# plano.json: {"cenas": [{"id":1,"de":0,"ate":3.4,"texto":"...","cenario":"garagem","pose":"parado","expressao":"feliz",
#              "objeto":"nenhum","enquadramento":"medio","lado":"centro"}, ...]}
# Valores aceitos: veja ENUMS abaixo. Campos que faltarem usam o padrão. O words.json (se existir) dá a boca falando.
import json, re, sys
from pathlib import Path

KIT = Path(__file__).resolve().parent

MARCA = "// GERADO DO PLANO (plano.json) — não edite à mão: mude o plano e rode gerar_cena.py. Para cena sob medida, apague esta linha."
ENUMS = {
    "cenario": ["garagem", "atelie", "infinito"],
    "pose": ["parado", "pensando", "apontando", "comemorando", "andando"],
    "expressao": ["feliz", "orgulhoso", "triste", "surpreso", "cansado", "bravo", "pensativo", "animado"],
    "objeto": ["nenhum", "carro", "galao", "gato"],
    "enquadramento": ["geral", "medio", "close", "lado", "alto"],
    "lado": ["esq", "centro", "dir"],
}
PERSONAGEM_ENUMS = {
    "estilo": ["massinha", "vinil", "desenho"],
    "roupa": ["camiseta", "moletom", "jardineira", "jaqueta", "varsity"],
    "cabelo": ["tigela", "topete", "cacheado", "mullet"],
    "barba": ["nenhuma", "cavanhaque"],
}
CORES_CHAVES = ["pele", "roupa", "baixo", "calca", "tenis", "sola", "cabelo", "listraA", "listraB", "cadarco"]
RENDER_ENUMS = {"material": ["vinil", "massinha", "desenho"], "luz": ["suave", "dura", "neutra"]}
PADRAO = {"cenario": "garagem", "pose": "parado", "expressao": "feliz", "objeto": "nenhum", "enquadramento": "medio", "lado": "centro"}


def juntar(base: dict, extra: dict) -> dict:
    """Mistura dicionários (o de baixo manda); cores, acessórios e render se somam."""
    r = {**base}
    for k, v in (extra or {}).items():
        r[k] = juntar(r[k], v) if isinstance(v, dict) and isinstance(r.get(k), dict) else v
    return r


def carregar_predefinicao(pasta: Path, nome: str) -> dict:
    for base in (pasta / "predefinicoes", KIT / "predefinicoes"):
        f = base / f"{nome}.json"
        if f.exists():
            return json.loads(f.read_text(encoding="utf-8"))
    achadas = sorted(x.stem for x in (KIT / "predefinicoes").glob("*.json"))
    sys.exit(f"Predefinição '{nome}' não existe. Disponíveis: {', '.join(achadas)}")


def validar_personagem(cfg: dict, onde: str, erros: list):
    for campo, validos in PERSONAGEM_ENUMS.items():
        if campo in cfg and cfg[campo] not in validos:
            erros.append(f"{onde}: {campo}='{cfg[campo]}' não existe. Use: {', '.join(validos)}")
    for k, v in (cfg.get("cores") or {}).items():
        if k not in CORES_CHAVES:
            erros.append(f"{onde}: cor '{k}' não existe. Use: {', '.join(CORES_CHAVES)}")
        elif not (isinstance(v, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", v)):
            erros.append(f"{onde}: cor '{k}'='{v}' precisa ser hexadecimal (#rrggbb).")
    if "escala" in cfg and not (isinstance(cfg["escala"], (int, float)) and 0.3 <= cfg["escala"] <= 3):
        erros.append(f"{onde}: escala deve ficar entre 0.3 e 3.")


def validar_modelos(pasta: Path, p: dict, cenas: list, erros: list) -> list:
    """modelos: [{id, arquivo (.glb), escala, pos, giro, estilizar}] — arquivo relativo à pasta do vídeo ou a kits/blender-3d/modelos."""
    modelos = p.get("modelos") or []
    ids = set()
    for m in modelos:
        mid = str(m.get("id", ""))
        if not re.fullmatch(r"[a-zA-Z0-9_-]+", mid):
            erros.append(f"modelo '{mid}': o id só pode ter letras, números, _ e -.")
        if mid in ids:
            erros.append(f"modelo '{mid}' repetido.")
        ids.add(mid)
        arq = None
        for base in (pasta, KIT / "modelos"):
            cand = (base / str(m.get("arquivo", ""))).resolve()
            if cand.is_file():
                arq = cand
                break
        if not arq or arq.suffix.lower() not in (".glb", ".gltf"):
            erros.append(f"modelo '{mid}': arquivo '{m.get('arquivo')}' não achado (precisa ser .glb ou .gltf, na pasta do vídeo ou em kits/blender-3d/modelos).")
        m["_arquivo_abs"] = str(arq) if arq else ""
        m.setdefault("escala", 1.0)
        m.setdefault("pos", [0, 0, 0])
        m.setdefault("giro", 0.0)
        m.setdefault("estilizar", True)
    for i, c in enumerate(cenas, 1):
        novos = []
        for it in c.get("modelos") or []:
            it = {"id": it} if isinstance(it, str) else dict(it)
            if it.get("id") not in ids:
                erros.append(f"cena {i}: modelo '{it.get('id')}' não está na lista 'modelos' do plano.")
                continue
            novos.append(it)
        c["modelos"] = novos
    return modelos


def preparar_modelos(pasta: Path, plano: dict, fps: int = 30):
    """Copia os .glb para blender/modelos e escreve blender/modelos.json (o que entra em cada cena, em quadros)."""
    import shutil
    bl = pasta / "blender"
    bl.mkdir(exist_ok=True)
    pm = bl / "modelos"
    if pm.exists():
        for velho in pm.glob("*"):
            velho.unlink()
    (bl / "modelos.json").unlink(missing_ok=True)
    if not plano.get("modelos"):
        return
    pm.mkdir(exist_ok=True)
    lista = []
    for m in plano["modelos"]:
        nome = f"{m['id']}{Path(m['_arquivo_abs']).suffix.lower()}"
        shutil.copy(m["_arquivo_abs"], pm / nome)
        lista.append({"id": m["id"], "arquivo": f"modelos/{nome}", "escala": m["escala"], "pos": m["pos"], "giro": m["giro"], "estilizar": m["estilizar"]})
    por_id = {m["id"]: m for m in plano["modelos"]}
    cenas = []
    for c in plano["cenas"]:
        itens = []
        for it in c["modelos"]:
            base = por_id[it["id"]]
            itens.append({"id": it["id"], "pos": it.get("pos", base["pos"]), "giro": it.get("giro", base["giro"]), "escala": it.get("escala", base["escala"])})
        cenas.append({"f0": int(round(c["de"] * fps)), "itens": itens})
    (bl / "modelos.json").write_text(json.dumps({"modelos": lista, "cenas": cenas}, ensure_ascii=False, indent=2), encoding="utf-8")


def carregar_plano(pasta: Path) -> dict:
    f = pasta / "plano.json"
    if not f.exists():
        sys.exit(f"Falta {f}")
    p = json.loads(f.read_text(encoding="utf-8"))
    if p.get("predefinicao"):
        pre = carregar_predefinicao(pasta, p["predefinicao"])
        p["personagem"] = juntar(pre.get("personagem", {}), p.get("personagem", {}))
        p["render"] = juntar(pre.get("render", {}), p.get("render", {}))
    cenas = p.get("cenas")
    if not isinstance(cenas, list) or not cenas:
        sys.exit("plano.json precisa de uma lista 'cenas' com pelo menos 1 cena.")
    erros, fim_anterior = [], 0.0
    validar_personagem(p.get("personagem") or {}, "personagem", erros)
    for campo, validos in RENDER_ENUMS.items():
        v = (p.get("render") or {}).get(campo)
        if v is not None and v not in validos:
            erros.append(f"render: {campo}='{v}' não existe. Use: {', '.join(validos)}")
    for i, c in enumerate(sorted(cenas, key=lambda c: c.get("de", 0)), 1):
        for campo, validos in ENUMS.items():
            v = c.get(campo)
            if v is None:
                c[campo] = PADRAO[campo]
            elif v not in validos:
                erros.append(f"cena {i}: {campo}='{v}' não existe. Use: {', '.join(validos)}")
        try:
            c["de"], c["ate"] = float(c["de"]), float(c["ate"])
        except (KeyError, TypeError, ValueError):
            erros.append(f"cena {i}: faltam 'de' e 'ate' (segundos).")
            continue
        if c["ate"] <= c["de"]:
            erros.append(f"cena {i}: 'ate' ({c['ate']}) precisa ser maior que 'de' ({c['de']}).")
        # cenas coladas: o começo de cada uma é o fim da anterior
        if i > 1 and abs(c["de"] - fim_anterior) > 0.05:
            c["de"] = fim_anterior
        fim_anterior = c["ate"]
        c["id"] = i
        if c.get("personagem"):
            validar_personagem(c["personagem"], f"cena {i} personagem", erros)
    p["modelos"] = validar_modelos(pasta, p, cenas, erros)
    if erros:
        sys.exit("Plano inválido:\n- " + "\n- ".join(erros))
    p["cenas"] = sorted(cenas, key=lambda c: c["de"])
    return p


def gerar(pasta: Path) -> Path:
    plano = carregar_plano(pasta)
    wf = pasta / "words.json"
    palavras = []
    if wf.exists():
        palavras = [{"s": round(float(w["s"]), 3), "e": round(float(w["e"]), 3)} for w in json.loads(wf.read_text(encoding="utf-8")) if "s" in w and "e" in w]
    out = pasta / "cena3d.tsx"
    if out.exists() and MARCA not in out.read_text(encoding="utf-8"):
        sys.exit(f"{out} foi escrito à mão (não tem a marca do gerador); não vou sobrescrever. Apague o arquivo para gerar do plano.")
    texto = f"""{MARCA}
import {{criarCena}} from '@estudio3d';

const PLANO = {json.dumps(plano, ensure_ascii=False)};
const PALAVRAS = {json.dumps(palavras)};

const cena = criarCena(PLANO, PALAVRAS);
export const DURACAO = cena.duracao;
export const quadro3D = cena.quadro3D;
"""
    out.write_text(texto, encoding="utf-8")
    preparar_modelos(pasta, plano)
    # plano.json é seu e não é reescrito. A versão arrumada (cenas coladas, predefinição aplicada) vai para blender/
    (pasta / "blender").mkdir(exist_ok=True)
    (pasta / "blender" / "plano.normalizado.json").write_text(json.dumps(plano, ensure_ascii=False, indent=2), encoding="utf-8")
    # estilo do render (material/luz/contorno) vai para o Blender
    (pasta / "blender" / "render.json").write_text(json.dumps(plano.get("render") or {"material": "vinil", "luz": "suave"}, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    print("cena3d.tsx gerado:", gerar(Path(sys.argv[1]).resolve()))
