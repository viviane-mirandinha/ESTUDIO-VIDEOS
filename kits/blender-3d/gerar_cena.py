# gerar_cena.py — transforma o PLANO DE CENAS (plano.json) em cena3d.tsx (modo grátis, sem escrever código 3D).
#   python kits/blender-3d/gerar_cena.py <pasta-do-video>
# plano.json: {"cenas": [{"id":1,"de":0,"ate":3.4,"texto":"...","cenario":"garagem","pose":"parado","expressao":"feliz",
#              "objeto":"nenhum","enquadramento":"medio","lado":"centro"}, ...]}
# Valores aceitos: veja ENUMS abaixo. Campos que faltarem usam o padrão. O words.json (se existir) dá a boca falando.
import json, sys
from pathlib import Path

MARCA = "// GERADO DO PLANO (plano.json) — não edite à mão: mude o plano e rode gerar_cena.py. Para cena sob medida, apague esta linha."
ENUMS = {
    "cenario": ["garagem", "atelie", "infinito"],
    "pose": ["parado", "pensando", "apontando", "comemorando", "andando"],
    "expressao": ["feliz", "orgulhoso", "triste", "surpreso", "cansado", "bravo", "pensativo", "animado"],
    "objeto": ["nenhum", "carro", "galao", "gato"],
    "enquadramento": ["geral", "medio", "close", "lado", "alto"],
    "lado": ["esq", "centro", "dir"],
}
PADRAO = {"cenario": "garagem", "pose": "parado", "expressao": "feliz", "objeto": "nenhum", "enquadramento": "medio", "lado": "centro"}


def carregar_plano(pasta: Path) -> dict:
    f = pasta / "plano.json"
    if not f.exists():
        sys.exit(f"Falta {f}")
    p = json.loads(f.read_text(encoding="utf-8"))
    cenas = p.get("cenas")
    if not isinstance(cenas, list) or not cenas:
        sys.exit("plano.json precisa de uma lista 'cenas' com pelo menos 1 cena.")
    erros, fim_anterior = [], 0.0
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
    (pasta / "plano.json").write_text(json.dumps(plano, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    print("cena3d.tsx gerado:", gerar(Path(sys.argv[1]).resolve()))
