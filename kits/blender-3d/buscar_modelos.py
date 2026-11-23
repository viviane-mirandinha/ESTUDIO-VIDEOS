# buscar_modelos.py — procura modelos 3D livres (só licença CC0) no Poly Pizza para o tema do vídeo e põe no plano.
#   python kits/blender-3d/buscar_modelos.py <pasta-do-video> [--sem-ia] [--termo "fridge"]
# Para cada cena escolhe até 2 objetos concretos (em inglês), busca no poly.pizza, baixa o .glb (guardado em
# kits/blender-3d/modelos/_poly/ para reaproveitar em outros vídeos) e escreve em plano.json: "modelos" + "modelos" por cena.
# Só aceita licença CC0 (domínio público, sem crédito). Se estiver sem internet, o vídeo segue sem os modelos.
import json, re, sys, time, urllib.parse, urllib.request
from pathlib import Path

KIT = Path(__file__).resolve().parent
RAIZ = KIT.parent.parent
sys.path.insert(0, str(RAIZ / "editor" / "fabrica"))
CACHE = KIT / "modelos" / "_poly"
UA = {"User-Agent": "Mozilla/5.0 (EstudioVideos; modelos CC0)"}
MAX_POR_CENA = 2

# palavras comuns em português → termo de busca (usado quando o Ollama não está no ar)
DICIO = {
    "loja": "shop", "mercado": "shop", "conveni": "shelf", "prateleira": "shelf", "estante": "bookshelf", "geladeira": "fridge",
    "refrigerador": "fridge", "caixa": "cash register", "carrinho": "shopping cart", "produto": "box", "cozinha": "stove", "fogão": "stove",
    "mesa": "table", "cadeira": "chair", "sofá": "sofa", "cama": "bed", "computador": "computer", "notebook": "laptop", "celular": "phone",
    "telefone": "phone", "livro": "book", "dinheiro": "coin", "moeda": "coin", "carro": "car", "bicicleta": "bicycle", "casa": "house",
    "prédio": "building", "predio": "building", "cidade": "building", "árvore": "tree", "arvore": "tree", "planta": "plant", "flor": "flower",
    "relógio": "clock", "relogio": "clock", "lâmpada": "lamp", "lampada": "lamp", "ideia": "lamp", "foguete": "rocket", "avião": "airplane",
    "aviao": "airplane", "barco": "boat", "café": "coffee cup", "cafe": "coffee cup", "comida": "burger", "pizza": "pizza", "pão": "bread",
    "pao": "bread", "bolo": "cake", "música": "guitar", "musica": "guitar", "guitarra": "guitar", "câmera": "camera", "camera": "camera",
    "bola": "ball", "trofeu": "trophy", "troféu": "trophy", "chave": "key", "porta": "door", "janela": "window", "escada": "stairs",
    "ferramenta": "wrench", "martelo": "hammer", "robô": "robot", "robo": "robot", "gato": "cat", "cachorro": "dog", "cão": "dog",
    "gráfico": "chart", "grafico": "chart", "tv": "television", "televisão": "television", "tesouro": "chest", "mapa": "map",
}
# altura aproximada (m) dos objetos, para o tamanho ficar coerente com o personagem (~1,7 m)
ALTURAS = {"fridge": 2.2, "shelf": 2.2, "bookshelf": 1.8, "shop": 3.0, "building": 6.0, "house": 4.0, "tree": 3.5, "car": 1.5, "door": 2.0,
           "stairs": 2.5, "table": 0.8, "chair": 1.0, "sofa": 0.9, "bed": 0.7, "stove": 1.0, "boat": 2.0, "airplane": 3.0, "rocket": 3.0,
           "robot": 1.6, "cash register": 0.5, "shopping cart": 0.9, "lamp": 0.6, "plant": 0.7, "clock": 0.5, "computer": 0.5, "laptop": 0.3,
           "bicycle": 1.0, "chest": 0.6, "television": 0.7, "dog": 0.6, "cat": 0.4, "trophy": 0.5, "cake": 0.4, "window": 1.2}


def _get(url: str, tentativas: int = 3, binario: bool = False):
    for i in range(tentativas):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                d = r.read()
            return d if binario else d.decode("utf-8", "replace")
        except Exception as e:
            if i == tentativas - 1:
                raise
            time.sleep(1.5 * (i + 1))


def _slug(t: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")[:40] or "modelo"


def pesquisar(termo: str) -> list:
    """[(id, titulo)] dos resultados do Poly Pizza para o termo (em inglês)."""
    html = _get("https://poly.pizza/search/" + urllib.parse.quote(termo))
    achados, vistos = [], set()
    for m in re.finditer(r'<a href="/m/([A-Za-z0-9_-]+)"><div class="MuiCardMedia-root" title="([^"]*)"', html):
        if m.group(1) not in vistos:
            vistos.add(m.group(1))
            achados.append((m.group(1), m.group(2)))
    return achados


def detalhe(mid: str) -> dict:
    html = _get("https://poly.pizza/m/" + mid)
    lic = re.search(r'"Licence":"([^"]*)"', html)
    glb = re.search(r'https://static\.poly\.pizza/[0-9a-f-]+\.glb', html)
    tit = re.search(r'property="og:title" content="([^"]*)"', html)
    titulo = tit.group(1) if tit else mid
    autor = re.search(r"Free Model By (.+)$", titulo)
    return {"id": mid, "licenca": lic.group(1) if lic else "", "glb": glb.group(0) if glb else "",
            "titulo": re.sub(r" - Free Model By .*$", "", titulo), "autor": autor.group(1) if autor else ""}


def baixar(termo: str) -> dict | None:
    """Acha o 1º modelo CC0 do termo e baixa (ou reaproveita do cache). Devolve {arquivo, titulo, altura…} ou None."""
    CACHE.mkdir(parents=True, exist_ok=True)
    meta_f = CACHE / f"{_slug(termo)}.json"
    if meta_f.exists():
        meta = json.loads(meta_f.read_text(encoding="utf-8"))
        if (CACHE / meta["arquivo"]).exists():
            return meta
    from concurrent.futures import ThreadPoolExecutor
    cands = pesquisar(termo)[:30]

    def ver(mid):
        try:
            return detalhe(mid)
        except Exception:
            return None
    with ThreadPoolExecutor(6) as ex:
        dets = list(ex.map(ver, [m for m, _ in cands]))
    for d in dets:
        if not d or not d["licenca"].upper().startswith("CC0") or not d["glb"]:
            continue
        mid = d["id"]
        dados = _get(d["glb"], binario=True)
        if len(dados) < 500 or len(dados) > 25_000_000 or dados[:4] != b"glTF":
            continue
        nome = f"{_slug(termo)}.glb"
        (CACHE / nome).write_bytes(dados)
        meta = {"termo": termo, "arquivo": nome, "titulo": d["titulo"], "autor": d["autor"], "licenca": d["licenca"],
                "fonte": "https://poly.pizza/m/" + mid}
        meta_f.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        return meta
    return None


# ---------------------------------------------------------------------------------- o que procurar em cada cena
def termos_por_regras(texto: str) -> list:
    t = texto.lower()
    achados = []
    for pt, en in DICIO.items():
        if pt in t and en not in achados:
            achados.append(en)
    return achados[:MAX_POR_CENA]


def termos_por_ia(cenas: list, modelo: str) -> dict:
    """Ollama escolhe, por cena, até 2 objetos concretos e simples de achar num banco de modelos. Erro → {}."""
    try:
        from lib import ollama
        lista = "\n".join(f'{i}. "{c["texto"]}"' for i, c in enumerate(cenas, 1))
        prompt = (
            "For each numbered line of a short video narration (Portuguese), pick up to 2 concrete physical OBJECTS or PLACES' props that could be shown "
            "as simple 3D models next to a cartoon narrator. Answer each with 1-2 English search words for a free 3D model library "
            "(e.g. 'fridge', 'shelf', 'cash register', 'shopping cart', 'laptop', 'tree', 'building'). Prefer common nouns that exist as low-poly models. "
            "Single common nouns only, lowercase words separated by spaces (no underscores, no abstract words like 'logistics' or 'organization'); never people; use [] when nothing fits.\n" + lista
            + '\nAnswer ONLY JSON: {"cenas":[{"n":1,"objetos":["fridge","shelf"]}]}'
        )
        d = ollama._json_seguro(ollama.gerar(prompt, modelo, json_mode=True, temperatura=0.3, num_predict=900, timeout=240)) or {}
    except Exception as e:
        print(f"(Ollama indisponível ou falhou: {str(e)[:100]} — uso o dicionário)", flush=True)
        return {}
    r = {}
    for c in d.get("cenas", []) if isinstance(d, dict) else []:
        try:
            n = int(c["n"])
        except (KeyError, TypeError, ValueError):
            continue
        objs = [str(o).strip().lower().replace("_", " ") for o in (c.get("objetos") or []) if isinstance(o, str) and 2 < len(o.strip()) <= 30]
        r[n] = objs[:MAX_POR_CENA]
    return r


def cenografia_por_ia(texto: str, modelo: str) -> dict:
    """Ollama descreve o LUGAR do vídeo: cor do fundo e 3 móveis/objetos grandes que ficam atrás do personagem. Erro → {}."""
    try:
        from lib import ollama
        prompt = (
            "A short 3D cartoon video takes place in ONE place. From the narration below (Portuguese) decide the place and answer ONLY JSON: "
            '{"fundo":"#rrggbb pastel color for the room","moveis":["a","b","c"]} where moveis are exactly 3 big concrete props/furniture typical of that place, '
            "1-2 lowercase English words each, common nouns that exist in low-poly model libraries (e.g. shelf, fridge, counter, bed, tree, car, bookshelf, desk, stove). "
            "No people, nothing abstract. Narration: " + texto[:1500]
        )
        d = ollama._json_seguro(ollama.gerar(prompt, modelo, json_mode=True, temperatura=0.3, num_predict=300, timeout=180)) or {}
    except Exception as e:
        print(f"(cenografia sem Ollama: {str(e)[:80]})", flush=True)
        return {}
    if not isinstance(d, dict):
        return {}
    mov = [str(m).strip().lower().replace("_", " ") for m in (d.get("moveis") or []) if isinstance(m, str) and 2 < len(m.strip()) <= 30][:3]
    fundo = d.get("fundo") if isinstance(d.get("fundo"), str) and re.fullmatch(r"#[0-9a-fA-F]{6}", d["fundo"]) else None
    return {"moveis": mov, "fundo": fundo}


def posicoes_fundo(lado: str, n: int) -> list:
    """Móveis grandes atrás do personagem, espalhados pela largura que a câmera mostra."""
    px = {"esq": -1.5, "dir": 1.5}.get(lado, 0.0)
    d = 1.0 if lado != "dir" else -1.0
    cx = px + 0.85 * d
    return [[cx - 2.3, 0.0, -2.6], [cx + 0.2, 0.0, -3.4], [cx + 2.5, 0.0, -2.6]][:n]


# ---------------------------------------------------------------------------------- aplica ao plano
def posicoes(lado: str, n: int) -> list:
    """Onde cada objeto fica (coordenadas do kit; o personagem fica em x=-1,5 / 0 / 1,5 e z=0,9):
    o 1º ao lado dele, do lado de dentro do quadro; o 2º atrás."""
    px = {"esq": -1.5, "dir": 1.5}.get(lado, 0.0)
    d = 1.0 if lado != "dir" else -1.0
    return [[px + 1.7 * d, 0.0, 0.6], [px + 0.9 * d, 0.0, -1.8]][:n]


def aplicar(pasta: Path, usar_ia: bool = True, so_termo: str | None = None) -> dict:
    pf = pasta / "plano.json"
    plano = json.loads(pf.read_text(encoding="utf-8"))
    cenas = plano["cenas"]
    pedido = json.loads((pasta / "pedido.json").read_text(encoding="utf-8")) if (pasta / "pedido.json").exists() else {}
    por_cena = {}
    if so_termo:
        por_cena = {i: [so_termo] for i in range(1, len(cenas) + 1)}
    else:
        if usar_ia:
            modelo = pedido.get("modelo_ollama") or pedido.get("modelo") or "qwen2.5:7b"
            for ini in range(0, len(cenas), 8):
                lote = cenas[ini:ini + 8]
                for n, objs in termos_por_ia(lote, modelo).items():
                    por_cena[ini + n] = objs
        for i, c in enumerate(cenas, 1):
            if not por_cena.get(i):
                por_cena[i] = termos_por_regras(c["texto"])
    fundo_cor, moveis = None, []
    if not so_termo and pedido.get("cenografia", True) and not (pasta / "ambiente.json").exists():   # com ambiente próprio, os móveis vêm da ficha dele
        if usar_ia:
            cg = cenografia_por_ia(" ".join(c["texto"] for c in cenas), pedido.get("modelo_ollama") or pedido.get("modelo") or "qwen2.5:7b")
            moveis, fundo_cor = cg.get("moveis", []), cg.get("fundo")
        if not moveis:
            moveis = list(dict.fromkeys(t for ts in por_cena.values() for t in ts))[:3]
    arquivos, falhou = {}, []
    for termo in dict.fromkeys([t for ts in por_cena.values() for t in ts] + moveis):
        try:
            meta = baixar(termo)
        except Exception as e:
            print(f"  ✗ '{termo}': sem acesso ({str(e)[:80]})", flush=True)
            meta = None
        if meta:
            arquivos[termo] = meta
            print(f"  ✓ '{termo}' → {meta['titulo']} ({meta['licenca']}, {meta['autor']})", flush=True)
        else:
            falhou.append(termo)
            print(f"  ✗ '{termo}': nenhum modelo CC0 achado", flush=True)
    # só mexe nos modelos que vieram do buscador; os que o usuário pôs à mão ficam
    manuais = [m for m in plano.get("modelos") or [] if not m.get("auto")]
    ids_manuais = {m["id"] for m in manuais}
    modelos = list(manuais)
    for c in cenas:
        c["modelos"] = [it for it in (c.get("modelos") or []) if (it if isinstance(it, str) else it.get("id")) in ids_manuais]
    for termo, meta in arquivos.items():
        mid = "p-" + _slug(termo)
        modelos.append({"id": mid, "arquivo": str(CACHE / meta["arquivo"]), "escala": 1.0, "pos": [0, 0, 0], "giro": 0.0, "estilizar": True,
                        "auto": True, "base": True, "altura": ALTURAS.get(termo, ALTURAS.get(termo.split()[-1], 1.4)),
                        "nome": meta["titulo"], "termo": termo, "licenca": meta["licenca"], "autor": meta["autor"], "fonte": meta["fonte"]})
    for i, c in enumerate(cenas, 1):
        alvo = [t for t in por_cena.get(i, []) if t in arquivos]
        if alvo:   # a câmera precisa abrir para o personagem e os objetos caberem juntos no quadro vertical
            c["enquadramento"] = "geral"
            if c.get("lado", "centro") == "centro":
                c["lado"] = "esq"
        c.pop("alvo_x", None)
        if alvo:
            c["alvo_x"] = posicoes(c.get("lado", "centro"), 1)[0][0]
        for pos, termo in zip(posicoes(c.get("lado", "centro"), len(alvo)), alvo):
            c["modelos"].append({"id": "p-" + _slug(termo), "pos": pos, "giro": -0.45 if c.get("lado") != "dir" else 0.45})
    # cenografia: os móveis grandes ficam atrás do personagem em todas as cenas com enquadramento aberto
    fundo_ids = [t for t in moveis if t in arquivos]
    for c in cenas:
        if c.get("enquadramento") != "geral" or not fundo_ids:
            continue
        usados = {it["id"] for it in c["modelos"] if isinstance(it, dict)}
        livres = [t for t in fundo_ids if "p-" + _slug(t) not in usados]
        for pos, termo in zip(posicoes_fundo(c.get("lado", "centro"), len(livres)), livres):
            c["modelos"].append({"id": "p-" + _slug(termo), "pos": pos, "giro": 0.0, "escala": 1.0, "fundo": True})
        if not c.get("cenario_fixo") and fundo_cor and c.get("cenario") == "infinito":
            c["fundo"] = fundo_cor
    plano["modelos"] = modelos
    pf.write_text(json.dumps(plano, ensure_ascii=False, indent=2), encoding="utf-8")
    usados = len([m for m in modelos if m.get("auto")])
    print(f"modelos 3D: {usados} achados para {len(cenas)} cenas" + (f"; sem modelo para: {', '.join(falhou)}" if falhou else ""), flush=True)
    return {"achados": usados, "sem_modelo": falhou}


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    t = a[a.index("--termo") + 1] if "--termo" in a else None
    aplicar(Path(a[0]).resolve(), usar_ia="--sem-ia" not in a, so_termo=t)
