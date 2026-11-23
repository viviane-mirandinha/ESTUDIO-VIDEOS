# polyhaven.py — busca e baixa materiais, céus (HDRI) e modelos 3D do Poly Haven (api.polyhaven.com).
# Tudo no Poly Haven é CC0 (domínio público): pode usar em vídeo comercial sem dar crédito.
# Os arquivos ficam em cache em kits/blender-3d/modelos/_ph/ (essa pasta não vai para o git).
#   python kits/blender-3d/polyhaven.py modelo "shelf"      -> acha e baixa um modelo
#   python kits/blender-3d/polyhaven.py material "tiles"    -> acha e baixa um material de piso/parede
#   python kits/blender-3d/polyhaven.py ceu "supermarket"   -> acha e baixa um céu/ambiente (HDRI)
import json, re, struct, sys, time, urllib.request
from pathlib import Path

KIT = Path(__file__).resolve().parent
CACHE = KIT / "modelos" / "_ph"
API = "https://api.polyhaven.com"
UA = {"User-Agent": "EstudioVideos-Blender/1.0"}
TIPOS = {"modelo": "models", "material": "textures", "ceu": "hdris"}


def _get(url: str, tentativas: int = 3, binario: bool = False, timeout: int = 60):
    ultimo = None
    for i in range(tentativas):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                dados = r.read()
            return dados if binario else json.loads(dados.decode("utf-8"))
        except Exception as e:   # noqa: BLE001
            ultimo = e
            time.sleep(1.5 * (i + 1))
    raise RuntimeError(f"Poly Haven não respondeu ({url[:80]}): {str(ultimo)[:100]}")


def _baixar(url: str, destino: Path) -> Path:
    if destino.exists() and destino.stat().st_size > 0:
        return destino
    destino.parent.mkdir(parents=True, exist_ok=True)
    tmp = destino.with_suffix(destino.suffix + ".part")
    tmp.write_bytes(_get(url, binario=True, timeout=180))
    tmp.replace(destino)
    return destino


def catalogo(tipo: str) -> dict:
    """Lista de tudo que existe (id -> info). Fica 7 dias em cache."""
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / f"catalogo-{TIPOS[tipo]}.json"
    if f.exists() and time.time() - f.stat().st_mtime < 7 * 86400:
        return json.loads(f.read_text(encoding="utf-8"))
    d = _get(f"{API}/assets?t={TIPOS[tipo]}")
    f.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    return d


def _palavras(t: str) -> list:
    return [p for p in re.split(r"[^a-z0-9]+", t.lower()) if len(p) > 1]


def buscar(tipo: str, termo: str, n: int = 5, categorias: list | None = None, evitar: list | None = None, preferir: list | None = None) -> list:
    """Devolve até n ids, do que mais combina com o termo (em inglês) para o que menos combina."""
    cat = catalogo(tipo)
    alvo = _palavras(termo)
    if not alvo:
        return []
    pontos = []
    for pid, info in cat.items():
        nome = set(_palavras(info.get("name", "") + " " + pid))
        tags = set(_palavras(" ".join(info.get("tags", []))))
        cats = set(_palavras(" ".join(info.get("categories", []))))
        p = 0.0
        for w in alvo:
            if w in nome:
                p += 3
            elif any((x.startswith(w) or w.startswith(x)) and min(len(x), len(w)) >= max(4, len(w) - 2) for x in nome):
                p += 1.5   # plural e variações (shelf/shelves não; chair/chairs sim), sem casar "port" com "portable"
            if w in tags:
                p += 2
            if w in cats:
                p += 1.5
        if len(alvo) > 1 and p > 0:   # termo com várias palavras: tem que casar com todas, senão é outra coisa ("bottled water" ≠ tampa de bueiro com "water")
            casadas = sum(1 for w in alvo if w in nome or w in tags or w in cats)
            if casadas < len(alvo):
                p = p * 0.25 if casadas / len(alvo) >= 0.67 else 0
        if categorias and not (set(categorias) & set(info.get("categories", []))):
            p *= 0.3
        if evitar and (set(evitar) & set(info.get("categories", []))):
            p *= 0.3
        if preferir and p > 0 and (set(preferir) & set(info.get("categories", []))):
            p += 2.5
        if p > 0:
            pontos.append((p, -len(pid), pid))
    pontos.sort(reverse=True)
    return [pid for _, _, pid in pontos[:n]]


def info(tipo: str, pid: str) -> dict:
    return catalogo(tipo).get(pid, {})


# ------------------------------------------------------------- modelo (.gltf + .bin + texturas -> um .glb só)

def _gltf_para_glb(gltf_path: Path, saida: Path):
    """Junta .gltf, .bin e imagens num único .glb (fica fácil de mandar para a máquina de render)."""
    pasta = gltf_path.parent
    g = json.loads(gltf_path.read_text(encoding="utf-8"))
    bin_total = bytearray()
    mapa_buf = {}   # índice do buffer antigo -> deslocamento no bin novo
    for i, b in enumerate(g.get("buffers", [])):
        while len(bin_total) % 4:
            bin_total.append(0)
        mapa_buf[i] = len(bin_total)
        bin_total += (pasta / b["uri"]).read_bytes()
    for bv in g.get("bufferViews", []):
        bv["byteOffset"] = bv.get("byteOffset", 0) + mapa_buf[bv.get("buffer", 0)]
        bv["buffer"] = 0
    for im in g.get("images", []):
        if "uri" in im:
            dados = (pasta / im["uri"]).read_bytes()
            while len(bin_total) % 4:
                bin_total.append(0)
            g.setdefault("bufferViews", []).append({"buffer": 0, "byteOffset": len(bin_total), "byteLength": len(dados)})
            im["bufferView"] = len(g["bufferViews"]) - 1
            im["mimeType"] = "image/png" if im["uri"].lower().endswith(".png") else "image/jpeg"
            del im["uri"]
            bin_total += dados
    while len(bin_total) % 4:
        bin_total.append(0)
    g["buffers"] = [{"byteLength": len(bin_total)}]
    js = json.dumps(g, separators=(",", ":")).encode("utf-8")
    js += b" " * ((4 - len(js) % 4) % 4)
    total = 12 + 8 + len(js) + 8 + len(bin_total)
    with open(saida, "wb") as f:
        f.write(struct.pack("<4sII", b"glTF", 2, total))
        f.write(struct.pack("<I4s", len(js), b"JSON") + js)
        f.write(struct.pack("<I4s", len(bin_total), b"BIN\x00") + bytes(bin_total))


def baixar_modelo(pid: str, res: str = "1k") -> Path:
    """Baixa o modelo e devolve o caminho de um .glb único."""
    glb = CACHE / "modelos" / f"{pid}.glb"
    if glb.exists() and glb.stat().st_size > 0:
        return glb
    arqs = _get(f"{API}/files/{pid}")
    g = arqs.get("gltf") or {}
    r = res if res in g else (sorted(g)[0] if g else None)
    if not r or "gltf" not in g[r]:
        raise RuntimeError(f"{pid}: sem versão gltf")
    pasta = CACHE / "modelos" / f"_{pid}"
    principal = g[r]["gltf"]
    gl = _baixar(principal["url"], pasta / f"{pid}.gltf")
    for rel, it in (principal.get("include") or {}).items():
        _baixar(it["url"], pasta / rel)
    _gltf_para_glb(gl, glb)
    return glb


# ------------------------------------------------------------- material (piso, parede) e céu

def baixar_material(pid: str, res: str = "1k") -> dict:
    """Baixa cor + relevo + (ambiente/rugosidade/metal) e devolve {'diff': Path, 'nor': Path, 'arm': Path}."""
    arqs = _get(f"{API}/files/{pid}")
    out = {}
    for chave, mapa in (("diff", "Diffuse"), ("nor", "nor_gl"), ("arm", "arm")):
        porres = arqs.get(mapa) or {}
        r = res if res in porres else (sorted(porres)[0] if porres else None)
        if not r:
            continue
        fmt = porres[r].get("jpg") or porres[r].get("png")
        if fmt:
            ext = ".jpg" if "jpg" in porres[r] else ".png"
            out[chave] = _baixar(fmt["url"], CACHE / "materiais" / pid / f"{chave}{ext}")
    if "diff" not in out:
        raise RuntimeError(f"{pid}: sem textura de cor")
    return out


def baixar_ceu(pid: str, res: str = "1k") -> Path:
    arqs = _get(f"{API}/files/{pid}")
    h = (arqs.get("hdri") or {})
    r = res if res in h else (sorted(h)[0] if h else None)
    if not r or "hdr" not in h[r]:
        raise RuntimeError(f"{pid}: sem HDRI")
    return _baixar(h[r]["hdr"]["url"], CACHE / "ceus" / f"{pid}_{r}.hdr")


def achar_e_baixar(tipo: str, termo: str, tentativas: int = 4, **kw):
    """Tenta os melhores resultados até um baixar direito. Devolve (id, arquivo(s)) ou (None, None)."""
    cats, ev, pref = kw.pop("categorias", None), kw.pop("evitar", None), kw.pop("preferir", None)
    for pid in buscar(tipo, termo, n=tentativas, categorias=cats, evitar=ev, preferir=pref):
        try:
            if tipo == "modelo":
                return pid, baixar_modelo(pid)
            if tipo == "material":
                return pid, baixar_material(pid, kw.get("res", "1k"))
            return pid, baixar_ceu(pid, kw.get("res", "1k"))
        except Exception as e:   # noqa: BLE001
            print(f"  (Poly Haven: {pid} falhou: {str(e)[:80]})", flush=True)
    return None, None


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in TIPOS:
        sys.exit(__doc__)
    pid, arq = achar_e_baixar(sys.argv[1], " ".join(sys.argv[2:]))
    print(pid, arq)
