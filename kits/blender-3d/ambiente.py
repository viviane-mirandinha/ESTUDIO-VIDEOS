# ambiente.py — o "diretor de arte" do vídeo Blender: projeta o AMBIENTE de cada vídeo a partir do roteiro.
#   python kits/blender-3d/ambiente.py <pasta-do-video> [--sem-ia] [--ficha ficha.json]
# 1) projetar(): a IA (Ollama por padrão, ou o Claude se o usuário escolheu) escreve a "ficha do ambiente"
#    (ambiente.json na pasta do vídeo): onde se passa, tamanho da sala, materiais, céu, luz e os objetos.
# 2) empacotar(): baixa os materiais/céus/modelos (Poly Haven e Poly Pizza, tudo CC0), decide onde cada objeto fica
#    e escreve blender/ambiente.json (o que o Blender lê). Nada de cenário pré-montado: cada vídeo ganha o seu.
import hashlib, json, math, re, shutil, sys
from pathlib import Path

KIT = Path(__file__).resolve().parent
RAIZ = KIT.parent.parent
sys.path.insert(0, str(RAIZ / "editor" / "fabrica"))
sys.path.insert(0, str(KIT))

FUNDO_Y = 4.5          # parede do fundo (coordenada Y do Blender; o personagem fica perto de Y=-0,9 e a câmera em Y negativo)
FRENTE_Y = -9.0        # até onde vão o piso e as paredes laterais (a câmera fica fora, mais atrás)
ONDE = ("fundo", "esq", "dir", "chao")
LUZES = {"dia": "#fff3e0", "quente": "#ffd2a0", "fria": "#d8e8ff", "noite": "#9fb4ff"}
ALTURA_PADRAO = {"shelf": 2.0, "bookshelf": 1.9, "fridge": 1.9, "refrigerator": 1.9, "counter": 1.1, "desk": 0.8, "table": 0.8, "chair": 0.95, "sofa": 0.9,
                 "bed": 0.6, "lamp": 1.6, "plant": 1.0, "tree": 4.0, "car": 1.5, "door": 2.1, "window": 1.3, "tv": 0.7, "television": 0.7, "stove": 0.95,
                 "building": 8.0, "house": 5.0, "bench": 0.5, "cabinet": 1.4, "box": 0.5, "barrel": 0.9, "crate": 0.6, "rock": 0.8, "fence": 1.2}


def _num(v, lo, hi, pad):
    try:
        return min(max(float(v), lo), hi)
    except (TypeError, ValueError):
        return pad


def _cor(v, pad):
    return v if isinstance(v, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", v) else pad


def _slug(t):
    return re.sub(r"[^a-z0-9]+", "-", str(t).lower()).strip("-")[:30] or "x"


def _alea(*partes) -> float:
    """Número fixo entre 0 e 1 a partir de textos (o mesmo vídeo sempre sai igual)."""
    return int(hashlib.md5("|".join(map(str, partes)).encode()).hexdigest()[:8], 16) / 0xFFFFFFFF


# ------------------------------------------------------------------ 1) a ficha

def normalizar(d: dict) -> dict:
    """Aceita o que a IA devolveu e deixa a ficha dentro de limites sensatos (nunca quebra o render)."""
    lugares = []
    for i, l in enumerate((d or {}).get("lugares") or []):
        if not isinstance(l, dict):
            continue
        tipo = "exterior" if str(l.get("tipo", "interior")).lower().startswith("ext") else "interior"
        sala = l.get("sala") if isinstance(l.get("sala"), dict) else {}
        piso, parede, ceu = (l.get(k) if isinstance(l.get(k), dict) else {} for k in ("piso", "parede", "ceu"))
        objs = []
        for o in (l.get("objetos") or [])[:9]:
            if not isinstance(o, dict) or not str(o.get("termo", "")).strip():
                continue
            termo = str(o["termo"]).strip().lower().replace("_", " ")[:40]
            onde = str(o.get("onde", "fundo")).lower()
            base = next((v for k, v in ALTURA_PADRAO.items() if k in termo), 1.2)
            objs.append({"termo": termo, "onde": onde if onde in ONDE else "fundo", "qtd": int(_num(o.get("qtd", 1), 1, 4, 1)),
                         "altura": _num(o.get("altura", base), 0.15, 12.0, base), "cor": _cor(o.get("cor"), "#b8b0a4")})
        lugares.append({
            "id": _slug(l.get("id") or f"lugar{i + 1}"), "descricao": str(l.get("descricao", ""))[:120], "tipo": tipo,
            "sala": {"largura": _num(sala.get("largura"), 8, 10, 8.5), "profundidade": _num(sala.get("profundidade"), 5, 14, 9), "altura": _num(sala.get("altura"), 2.6, 6, 3.4)},
            "piso": {"termo": str(piso.get("termo") or "floor").lower()[:40], "cor": _cor(piso.get("cor"), "#b9a98f")},
            "parede": {"termo": str(parede.get("termo") or "plaster wall").lower()[:40], "cor": _cor(parede.get("cor"), "#e6dfd0")},
            "ceu": {"termo": str(ceu.get("termo") or ("sunset sky" if tipo == "exterior" else "indoor room")).lower()[:40]},
            "luz": str(l.get("luz", "dia")).lower() if str(l.get("luz", "dia")).lower() in LUZES else "dia",
            "janelas": int(_num(l.get("janelas", 1 if tipo == "interior" else 0), 0, 4, 1)),
            "objetos": objs,
        })
    ids = [l["id"] for l in lugares[:3]]
    lugares = lugares[:3]
    cenas = {}
    for k, v in ((d or {}).get("cenas") or {}).items():
        if str(k).isdigit() and _slug(v) in ids:
            cenas[str(int(k))] = _slug(v)
    return {"lugares": lugares, "cenas": cenas, "origem": (d or {}).get("origem", "")}


PROIBIDOS = {"light", "luz", "lights", "sky", "air", "wall", "floor", "ceiling", "product", "products", "item", "items", "thing", "decoration", "decor", "object", "stuff"}


def traduzir_termos(ficha: dict, modelo: str) -> dict:
    """Os modelos pequenos às vezes respondem em português: pede a tradução de todos os termos de busca para o inglês (1 chamada curta)."""
    refs = []
    for l in ficha["lugares"]:
        for chave in ("piso", "parede", "ceu"):
            refs.append((l[chave], "termo"))
        for o in l["objetos"]:
            refs.append((o, "termo"))
    termos = [r[0][r[1]] for r in refs]
    if not termos:
        return ficha
    try:
        from lib import ollama
        prompt = ("Translate each search term to simple English (1-2 words, a concrete noun for a 3D model or material library; keep it if it is already English). "
                  'Answer ONLY JSON {"termos":[...]} with exactly ' + str(len(termos)) + " items in the same order. Terms: " + json.dumps(termos, ensure_ascii=False))
        d = ollama._json_seguro(ollama.gerar(prompt, modelo, json_mode=True, temperatura=0.0, num_predict=600, timeout=180)) or {}
        novos = d.get("termos") if isinstance(d, dict) else None
        if isinstance(novos, list) and len(novos) == len(termos):
            for (obj, k), n in zip(refs, novos):
                if isinstance(n, str) and 1 < len(n.strip()) <= 40:
                    obj[k] = re.sub(r"[^a-z0-9 ]", "", n.lower()).strip() or obj[k]
    except Exception as e:   # noqa: BLE001
        print(f"(tradução dos termos falhou: {str(e)[:80]})", flush=True)
    for l in ficha["lugares"]:
        l["objetos"] = [o for o in l["objetos"] if o["termo"] not in PROIBIDOS]
    return ficha


def ficha_reserva(texto: str) -> dict:
    """Sem IA: um quarto simples e neutro, só para o vídeo nunca ficar sem cenário."""
    return normalizar({"origem": "reserva", "lugares": [{
        "id": "sala", "descricao": "sala simples", "tipo": "interior", "sala": {"largura": 12, "profundidade": 9, "altura": 3.4},
        "piso": {"termo": "wood floor", "cor": "#b79b78"}, "parede": {"termo": "plaster wall", "cor": "#e7e0d2"}, "ceu": {"termo": "indoor room"}, "luz": "dia", "janelas": 1,
        "objetos": [{"termo": "plant", "onde": "esq"}, {"termo": "lamp", "onde": "dir"}, {"termo": "table", "onde": "fundo"}]}]})


PROMPT = """You are the art director of a short 3D animated video. A character stands in the middle of the frame, the camera looks at him from the front,
so the WHOLE place must be a believable set built behind and around him. Read the narration (Portuguese) and design the place(s) where it happens.
Answer ONLY a JSON object:
{"lugares":[{"id":"short-id","descricao":"one line in Portuguese","tipo":"interior or exterior",
 "sala":{"largura":8-20,"profundidade":6-12,"altura":2.8-5},
 "piso":{"termo":"english search words for the floor/ground material","cor":"#rrggbb"},
 "parede":{"termo":"english search words for the wall material","cor":"#rrggbb"},
 "ceu":{"termo":"english search words for the sky/ambient light, e.g. supermarket, sunset, night city, forest"},
 "luz":"dia|quente|fria|noite","janelas":0-4,
 "objetos":[{"termo":"1-2 english words, a concrete object","onde":"fundo|esq|dir|chao","altura":metros,"qtd":1-4}]}],
 "cenas":{"1":"id","2":"id"}}
Rules: 1 place is enough; use 2 or 3 only when the story really changes place (e.g. inside / outside). 6-9 objects per place, concrete things that belong
there and fill the walls and floor (shelves, counter, fridge, sofa, plants, lamps, boxes, posters…), no people, nothing abstract. ALL search terms (piso, parede, ceu, objetos) MUST be written in English. Every object must be something you would really see in that place. "fundo" = against the back wall,
"esq"/"dir" = against the side walls, "chao" = standing free on the floor. altura = real height in meters. For exterior places there are no walls:
use piso for the ground, objects like buildings, trees, cars, fences. "cenas" maps the scene numbers below to a place id (only needed when there is more than one place).
"""


def _json_do_texto(txt: str):
    i, j = txt.find("{"), txt.rfind("}")
    if i < 0 or j <= i:
        return None
    try:
        return json.loads(txt[i:j + 1])
    except Exception:   # noqa: BLE001
        return None


def pedir_ao_claude(prompt: str):
    """Chama o Claude Code (claude -p) só para escrever a ficha (poucos tokens). Devolve o JSON ou None."""
    import os, subprocess
    exe = os.environ.get("CLAUDE_EXE", "").strip().strip('"') or shutil.which("claude")
    if not exe:
        print("(Claude não encontrado neste PC: usei o Ollama para o ambiente)", flush=True)
        return None
    modelo = (os.environ.get("ESTUDIO_CLAUDE_MODELO") or "sonnet").strip()
    import tempfile
    # o prompt vai pelo stdin (atalho .cmd do Windows corta prompts de várias linhas) e roda numa pasta neutra, sem o CLAUDE.md do projeto
    r = subprocess.run([exe, "-p", "--model", modelo, "--output-format", "text",
                        "--system-prompt", "You are a JSON generator for a 3D video pipeline. Reply with exactly one JSON object and nothing else."],
                       input=prompt, capture_output=True, text=True, cwd=tempfile.gettempdir(),
                       encoding="utf-8", errors="replace", timeout=420, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    d = _json_do_texto(r.stdout or "")
    if not d:
        print(f"(Claude não devolveu a ficha: {(r.stdout or r.stderr or '')[-120:].strip()})", flush=True)
    return d


def projetar(pasta: Path, usar_ia: bool = True, ficha_pronta: dict | None = None, por: str = "ollama") -> dict:
    """Escreve <pasta>/ambiente.json (a ficha) e marca o plano para não usar os cenários prontos."""
    ped = {}
    if (pasta / "pedido.json").exists():
        ped = json.loads((pasta / "pedido.json").read_text(encoding="utf-8"))
    plano = json.loads((pasta / "plano.json").read_text(encoding="utf-8")) if (pasta / "plano.json").exists() else {"cenas": []}
    texto = (pasta / "roteiro.txt").read_text(encoding="utf-8") if (pasta / "roteiro.txt").exists() else " ".join(c.get("texto", "") for c in plano["cenas"])
    ficha = None
    if ficha_pronta:
        ficha = normalizar({**ficha_pronta, "origem": ficha_pronta.get("origem") or "claude"})
    elif por == "claude":
        cenas_txt = "\n".join(f"{c.get('id', i + 1)}: {c.get('texto', '')[:70]}" for i, c in enumerate(plano["cenas"][:60]))
        bruto = pedir_ao_claude(PROMPT + "\nNarration:\n" + texto[:4000] + "\n\nScenes:\n" + cenas_txt + "\n\nAnswer with the JSON only, no explanation.")
        if isinstance(bruto, dict):
            ficha = normalizar({**bruto, "origem": "claude"})
    if not ficha and usar_ia:
        try:
            from lib import ollama
            cenas_txt = "\n".join(f"{c.get('id', i + 1)}: {c.get('texto', '')[:70]}" for i, c in enumerate(plano["cenas"][:60]))
            prompt = PROMPT + "\nNarration:\n" + texto[:2500] + "\n\nScenes:\n" + cenas_txt
            bruto = ollama._json_seguro(ollama.gerar(prompt, ped.get("modelo_ollama") or "qwen2.5:7b", json_mode=True, temperatura=0.5, num_predict=1500, timeout=300)) or {}
            ficha = normalizar({**bruto, "origem": "ollama"}) if isinstance(bruto, dict) else None
            if ficha:
                ficha = traduzir_termos(ficha, ped.get("modelo_ollama") or "qwen2.5:7b")
        except Exception as e:   # noqa: BLE001
            print(f"(ambiente sem Ollama: {str(e)[:90]})", flush=True)
    if not ficha or not ficha["lugares"]:
        ficha = ficha_reserva(texto)
    (pasta / "ambiente.json").write_text(json.dumps(ficha, ensure_ascii=False, indent=2), encoding="utf-8")
    # o ambiente novo substitui o cenário pronto (garagem/ateliê/infinito) em todas as cenas
    if plano.get("cenas"):
        padrao = ficha["lugares"][0]["id"]
        for c in plano["cenas"]:
            c["cenario"] = "nenhum"
            c["lugar"] = ficha["cenas"].get(str(c.get("id")), padrao)
        (pasta / "plano.json").write_text(json.dumps(plano, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"ambiente.json: {len(ficha['lugares'])} lugar(es) ({ficha['origem']}): " + ", ".join(l["descricao"] or l["id"] for l in ficha["lugares"]), flush=True)
    return ficha


# ------------------------------------------------------------------ 2) onde cada coisa fica

# O quadro é vertical (1080x1920): a câmera mostra só ~±3,3 m de largura no fundo da sala. Por isso os objetos ficam em "vagas" dentro dessa faixa
# (x, y em metros; o personagem fica em x ≈ -1,5…1,5 e y ≈ -0,9, então a frente dele fica livre).
VAGAS_INT = {
    "fundo": [(-2.3, 3.9), (0.0, 4.0), (2.3, 3.9)],
    "esq": [(-2.4, 1.8), (-2.6, 0.5)],
    "dir": [(2.4, 1.8), (2.6, 0.5)],
    "chao": [(-1.1, 2.5), (1.1, 2.6), (-2.4, 3.0), (2.4, 3.0), (-2.5, -0.9), (2.5, -0.9)],
}
VAGAS_EXT = {
    "fundo": [(-3.6, 7.0), (3.6, 7.5), (0.0, 9.5), (-6.0, 11.0), (6.0, 11.5)],
    "esq": [(-3.4, 2.5), (-3.4, -2.5)],
    "dir": [(3.4, 2.5), (3.4, -2.5)],
    "chao": [(-2.2, 4.0), (2.2, 4.2), (-5.0, 5.0), (5.0, 5.0)],
}
GIRO_VAGA = {"fundo": 0.0, "esq": 0.45, "dir": -0.45, "chao": 0.0}


def _posicoes(l: dict, itens: list) -> list:
    """Dá a cada objeto (já expandido por qtd) uma vaga [x,y,z] e um giro (Blender: Z para cima, a câmera em Y negativo).
    O que não cabe na vaga do tipo pedido vai para qualquer vaga livre; o que passar de todas as vagas fica de fora."""
    vagas = VAGAS_EXT if l["tipo"] == "exterior" else VAGAS_INT
    livres = {k: list(v) for k, v in vagas.items()}
    colocados, sobra = [], []
    for it in itens:
        if livres[it["onde"]]:
            colocados.append((it, it["onde"], livres[it["onde"]].pop(0)))
        else:
            sobra.append(it)
    for it in sobra:
        for k in ("chao", "esq", "dir", "fundo"):
            if livres[k]:
                colocados.append((it, k, livres[k].pop(0)))
                break
    out = []
    for it, k, (x, y) in colocados:
        jit = (_alea(it["termo"], it.get("j", 0), "x") - 0.5) * 0.3
        it["pos"] = [round(x + jit, 2), y, 0.0]
        it["giro"] = GIRO_VAGA[k] + (_alea(it["termo"], it.get("j", 0), "g") - 0.5) * 0.3
        out.append(it)
    return out


def _expandir(l: dict) -> list:
    itens = []
    for o in l["objetos"]:
        for j in range(o["qtd"]):
            itens.append({**o, "j": j})
    return itens


# gosto por tipo de lugar: dentro de casa/loja, nada de rocha, terra e areia; fora, nada de piso de sala
EVITAR_INT = ["rock", "terrain", "sand", "cobblestone", "gravel", "snow", "bark", "aerial", "dirty", "roofing", "road", "asphalt"]
PREFERIR_INT = ["indoor", "clean", "plaster", "tiles"]
EVITAR_EXT = ["indoor", "fabric", "cotton", "wool", "leather", "denim"]
RESERVA = {"piso": ["floor", "tiles", "concrete floor"], "parede": ["wall", "plaster", "painted wall"], "ceu_in": ["indoor", "room", "studio"], "ceu_ex": ["sky", "sunset", "clouds"]}


def _achar(polyhaven, tipo: str, termo: str, reservas: list, categorias=None, **kw):
    for t in [termo] + reservas:
        pid, r = polyhaven.achar_e_baixar(tipo, t, categorias=categorias, **kw)
        if r:
            return pid, r
    return None, None


def empacotar(pasta: Path, plano: dict | None = None, fps: int = 30):
    """Baixa o que a ficha pede e escreve blender/ambiente.json + os arquivos em blender/modelos/ (nomes simples, sem pastas)."""
    fich = pasta / "ambiente.json"
    bl = pasta / "blender"
    (bl / "ambiente.json").unlink(missing_ok=True)
    if not fich.exists():
        return
    import polyhaven
    try:
        import buscar_modelos
    except Exception:   # noqa: BLE001
        buscar_modelos = None
    ficha = normalizar(json.loads(fich.read_text(encoding="utf-8")))
    pm = bl / "modelos"
    pm.mkdir(parents=True, exist_ok=True)
    for velho in pm.glob("amb_*"):
        velho.unlink()
    saida = {"lugares": [], "cenas": []}
    semmodelo = []

    def copiar(src: Path, nome: str) -> str:
        shutil.copy(src, pm / nome)
        return f"modelos/{nome}"

    for l in ficha["lugares"]:
        lid = l["id"]
        print(f"  Ambiente '{lid}': baixando materiais, céu e objetos…", flush=True)
        reg = {"id": lid, "tipo": l["tipo"], "sala": {**l["sala"], "parede_altura": max(l["sala"]["altura"], 10.0)}, "luz": l["luz"], "luz_cor": LUZES[l["luz"]], "janelas": l["janelas"], "descricao": l["descricao"]}
        for chave in ("piso", "parede"):
            mat = l[chave]
            reg[chave] = {"cor": mat["cor"], "tile": (5.0 if l["tipo"] == "exterior" else 2.0) if chave == "piso" else 3.0, "termo": mat["termo"]}
            if chave == "parede" and l["tipo"] == "exterior":
                continue
            pid, arqs = _achar(polyhaven, "material", mat["termo"], RESERVA[chave], categorias=["floor"] if chave == "piso" else ["wall"], evitar=EVITAR_EXT if l["tipo"] == "exterior" else EVITAR_INT, preferir=None if l["tipo"] == "exterior" else PREFERIR_INT)
            if arqs:
                reg[chave]["id"] = pid
                for k, p in arqs.items():
                    reg[chave][k] = copiar(p, f"amb_{lid}_{chave}_{k}{p.suffix}")
        pid, hdr = _achar(polyhaven, "ceu", l["ceu"]["termo"], RESERVA["ceu_ex" if l["tipo"] == "exterior" else "ceu_in"], res="2k" if l["tipo"] == "exterior" else "1k", categorias=["outdoor"] if l["tipo"] == "exterior" else ["indoor", "studio"])
        if hdr:
            reg["ceu"] = {"id": pid, "arquivo": copiar(hdr, f"amb_{lid}_ceu.hdr")}
        itens = _posicoes(l, _expandir(l))
        reg["objetos"] = []
        cache_termo = {}
        for k, it in enumerate(itens):
            t = it["termo"]
            if t not in cache_termo:
                glb, fonte = None, ""
                pid, p = polyhaven.achar_e_baixar("modelo", t)
                if p:
                    glb, fonte = p, f"Poly Haven {pid} (CC0)"
                elif buscar_modelos:
                    meta = buscar_modelos.baixar(t)
                    if meta:
                        glb, fonte = buscar_modelos.CACHE / meta["arquivo"], f"Poly Pizza: {meta.get('titulo', '')} ({meta.get('licenca', '')})"
                cache_termo[t] = (glb, fonte)
            glb, fonte = cache_termo[t]
            o = {"termo": t, "pos": it["pos"], "giro": round(it["giro"], 3), "altura": it["altura"], "cor": it["cor"]}
            if glb:
                o["arquivo"] = copiar(glb, f"amb_{lid}_{_slug(t)}{Path(glb).suffix}")
                o["fonte"] = fonte
            else:
                semmodelo.append(t)    # sem modelo: o Blender monta uma peça simples no lugar, para a cena nunca ficar vazia
            reg["objetos"].append(o)
        saida["lugares"].append(reg)
    ids = {r["id"]: i for i, r in enumerate(saida["lugares"])}
    if plano:
        ult = None
        for c in plano["cenas"]:
            lg = c.get("lugar") if c.get("lugar") in ids else saida["lugares"][0]["id"]
            if lg != ult or not saida["cenas"]:
                saida["cenas"].append({"f0": int(round(c["de"] * fps)), "lugar": lg})
                ult = lg
    else:
        saida["cenas"] = [{"f0": 0, "lugar": saida["lugares"][0]["id"]}]
    saida["cenas"][0]["f0"] = 0
    (bl / "ambiente.json").write_text(json.dumps(saida, ensure_ascii=False, indent=2), encoding="utf-8")
    if semmodelo:
        print(f"  (sem modelo 3D para: {', '.join(sorted(set(semmodelo)))} — usei peças simples no lugar)", flush=True)
    with open(pasta / "CREDITOS-3D.txt", "w", encoding="utf-8") as f:
        f.write("Materiais, céus e modelos do ambiente: Poly Haven (CC0) e Poly Pizza (CC0). Não exigem crédito.\n")
        for r in saida["lugares"]:
            for o in r["objetos"]:
                if o.get("fonte"):
                    f.write(f"- {r['id']} / {o['termo']}: {o['fonte']}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    pasta = Path(sys.argv[1]).resolve()
    pronta = None
    if "--ficha" in sys.argv:
        pronta = json.loads(Path(sys.argv[sys.argv.index("--ficha") + 1]).read_text(encoding="utf-8"))
    if "--so-empacotar" not in sys.argv:
        projetar(pasta, usar_ia="--sem-ia" not in sys.argv, ficha_pronta=pronta, por="claude" if "--claude" in sys.argv else "ollama")
    plano = json.loads((pasta / "plano.json").read_text(encoding="utf-8")) if (pasta / "plano.json").exists() else None
    empacotar(pasta, plano)
