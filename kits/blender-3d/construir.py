# construir.py — pipeline do kit Blender 3D do Estúdio (cena em código -> Blender -> vídeo com voz e legenda).
#
#   python kits/blender-3d/construir.py <pasta-do-video> --preparar     # voz -> words.json (para escrever a cena no tempo da fala)
#   python kits/blender-3d/construir.py <pasta-do-video> --teste        # assa e renderiza só 3 quadros (confere antes de gastar tempo)
#   python kits/blender-3d/construir.py <pasta-do-video>                # assa + renderiza tudo + monta blender.mp4 e edit.json
#   python kits/blender-3d/construir.py <pasta-do-video> --render       # idem + renderiza o vídeo final (voz + legenda)
#   opções: --local (render neste PC, bem mais lento) · --so-assar · --sem-assar (reusa blender/cena.glb)
#
# A pasta do vídeo tem: cena3d.tsx (obrigatório; exporta DURACAO e quadro3D), voz.mp3/wav (opcional),
# words.json (gerado do áudio). Veja o README.md deste kit.
import json, os, shutil, subprocess, sys, time
from pathlib import Path

KIT = Path(__file__).resolve().parent
RAIZ = KIT.parent.parent
CONFIG = json.loads((KIT / "config.json").read_text(encoding="utf-8"))
PY = sys.executable
ENV = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}


def passo(nome, cmd, **kw):
    print(f"\n==> {nome}", flush=True)
    r = subprocess.run(cmd, cwd=kw.pop("cwd", RAIZ), env=ENV, **kw)
    if r.returncode:
        print(f"\nPARADO em «{nome}». Corrija e rode de novo.")
        sys.exit(r.returncode)


def duracao(arq: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(arq)], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def achar_voz(pasta: Path):
    for n in ("voz.mp3", "voz.wav", "voz.m4a"):
        if (pasta / n).exists():
            return pasta / n
    return None


def preparar(pasta: Path):
    voz = achar_voz(pasta)
    if not voz:
        print("Sem voz.mp3/voz.wav nesta pasta: nada para preparar. (A legenda só aparece quando há voz.)")
        return
    w = pasta / "words.json"
    if w.exists():
        print(f"words.json já existe ({w}).")
        return
    print("\n==> transcrevendo a voz (tempo de cada palavra)", flush=True)
    sys.path.insert(0, str(RAIZ / "editor" / "fabrica"))
    from lib.transcrever import transcrever
    transcrever(voz, w, idioma=os.environ.get("ESTUDIO_IDIOMA", "pt"))
    print(f"words.json pronto: {w}")


def instalar_deps():
    if not (KIT / "node_modules" / "three").exists():
        passo("instalando as peças do kit (npm install, uma vez só)", ["npm", "install", "--no-audit", "--no-fund"], cwd=KIT, shell=(os.name == "nt"))


def montar_edit(pasta: Path, dur_cena: float, largura: int, altura: int):
    voz = achar_voz(pasta)
    dur = max(dur_cena, duracao(voz) if voz else 0)
    ed = pasta / "edit.json"
    if ed.exists():
        d = json.loads(ed.read_text(encoding="utf-8"))
        print("edit.json já existe: mantido (só o vídeo blender.mp4 foi atualizado).")
        d["duration"] = round(dur, 2)
        ed.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
        return
    items = [{"id": "blender", "type": "video", "track": "fundo", "label": "Cena 3D (Blender)", "start": 0, "dur": round(dur_cena, 2),
              "props": {"src": "blender.mp4", "fill": True, "fit": "cover", "volume": 0}}]
    if (pasta / "words.json").exists():
        items.append({"id": "legenda", "type": "caption", "track": "legenda", "label": "Legenda", "start": 0, "dur": round(dur, 2),
                      "props": {"words_file": "words.json", "per_group": 2, "x": largura // 2, "y": int(altura * 0.78), "size": 84,
                                "color": "#ffffff", "dim": "#ffffff", "hl_color": "#ffd400", "bg": "rgba(0,0,0,.45)", "font": "Inter", "weight": 800}})
    audio = {}
    if voz:
        audio["voice"] = {"src": voz.name, "volume": 1.0, "start": 0}
    d = {"version": 1, "name": pasta.name, "canvas": {"w": largura, "h": altura, "fps": 30, "bg": "#101010"}, "duration": round(dur, 2),
         "template": "generic", "audio": audio,
         "tracks": [{"id": "fundo", "name": "Cena 3D"}, {"id": "legenda", "name": "Legenda"}],
         "items": items, "estilo": "Blender 3D (personagem e objetos em 3D)"}
    ed.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    print("edit.json criado (o vídeo aparece no editor).")


def previa_cenas(pasta: Path, bl: Path, info: dict, extra: list):
    """Um quadro de cada cena do plano (o do meio da cena) -> previa/cena-NN.jpg + previa/previas.json."""
    pj = pasta / "plano.json"
    if not pj.exists():
        sys.exit("--previa-cenas precisa de plano.json (modo por cenas).")
    cenas = json.loads(pj.read_text(encoding="utf-8"))["cenas"]
    fps, total = info["fps"], info["total"]
    alvo = []   # (cena, número do quadro 1..total)
    for c in cenas:
        f = min(total, max(1, int(round((c["de"] + c["ate"]) / 2 * fps)) + 1))
        alvo.append((c, f))
    lista = ",".join(str(f) for _, f in alvo)
    passo(f"2/2 quadros de teste das {len(cenas)} cenas", [PY, str(KIT / "render_quadros.py"), str(bl), "--quadros", lista, *extra])
    pv = pasta / "previa"
    pv.mkdir(exist_ok=True)
    for velho in pv.glob("*"):   # limpa as prévias antigas (sem apagar a pasta: no Windows ela pode estar aberta)
        if velho.is_file():
            velho.unlink()
    itens = []
    for c, f in alvo:
        src = next((bl / "quadros").glob(f"q{f:04d}.*"), None)
        if not src:
            sys.exit(f"Faltou o quadro {f} da cena {c['id']}.")
        dst = pv / f"cena-{c['id']:02d}{src.suffix}"
        shutil.copy(src, dst)
        itens.append({"cena": c["id"], "quadro": f, "arquivo": dst.name, "de": c["de"], "ate": c["ate"], "texto": c.get("texto", "")})
    (pv / "previas.json").write_text(json.dumps(itens, ensure_ascii=False, indent=2), encoding="utf-8")
    shutil.rmtree(bl / "quadros", ignore_errors=True)
    print(f"\nPrévias das cenas em {pv} ({len(itens)} imagens).")


def main():
    a = sys.argv[1:]
    if not a or a[0].startswith("--"):
        sys.exit(__doc__)
    pasta = Path(a[0]).resolve()
    if (pasta / "plano.json").exists():
        sys.path.insert(0, str(KIT))
        import gerar_cena
        print("\n==> plano.json -> cena3d.tsx", flush=True)
        gerar_cena.gerar(pasta)
    if not (pasta / "cena3d.tsx").exists():
        sys.exit(f"Falta {pasta / 'cena3d.tsx'} (ou plano.json). Copie e adapte kits/blender-3d/exemplos/vitrine/cena3d.tsx.")
    if "--preparar" in a:
        return preparar(pasta)
    preparar(pasta)
    instalar_deps()
    bl = pasta / "blender"
    bl.mkdir(exist_ok=True)
    if "--sem-assar" not in a:
        passo("1/4 assar a cena 3D (.glb)", ["node", str(KIT / "bake" / "assar.mjs"), str(pasta / "cena3d.tsx"), str(bl), pasta.name])
    if "--so-assar" in a:
        return print("\nCena assada em", bl)
    info = json.loads((bl / "quadros.json").read_text(encoding="utf-8"))
    total = info["total"]
    extra = []
    if "--local" in a:
        extra.append("--local")
    if "--previa-cenas" in a:
        return previa_cenas(pasta, bl, info, extra)
    if "--teste" in a:
        qs = f"{max(1, total // 8)},{total // 2},{max(1, total - total // 8)}"
        passo("2/4 render de teste (3 quadros)", [PY, str(KIT / "render_quadros.py"), str(bl), "--quadros", qs, *extra])
        sheet = bl / "teste.jpg"
        fs = sorted((bl / "quadros").glob("q*.*"))
        if fs:
            ins = sum([["-i", str(f)] for f in fs], [])
            filt = "".join(f"[{i}]scale=360:-1[v{i}];" for i in range(len(fs))) + "".join(f"[v{i}]" for i in range(len(fs))) + f"hstack={len(fs)}"
            subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", filt, str(sheet)])
            print("\nCONFIRA OLHANDO:", sheet, "\n(peças no lugar? nada faltando? Se estiver bom, rode sem --teste.)")
        return
    passo(f"2/4 renderizar {total} quadros no Blender", [PY, str(KIT / "render_quadros.py"), str(bl), *extra])
    n = len(list((bl / "quadros").glob("q*.*")))
    if n != total:
        sys.exit(f"Faltam quadros: {n} de {total}. Rode de novo (nada foi montado).")
    ext = next((bl / "quadros").glob("q0001.*")).suffix
    print("\n==> 3/4 montar blender.mp4", flush=True)
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(info["fps"]), "-i", str(bl / "quadros" / f"q%04d{ext}"),
                        "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(pasta / "blender.mp4")], env=ENV)
    if r.returncode:
        sys.exit("ffmpeg falhou ao montar blender.mp4")
    q = CONFIG["quadros"]
    print("\n==> 4/4 montar edit.json", flush=True)
    montar_edit(pasta, total / info["fps"], q["largura"], q["altura"])
    if "--manter-quadros" not in a:
        shutil.rmtree(bl / "quadros", ignore_errors=True)
    if "--render" in a:
        passo("render final (voz + legenda)", [PY, str(RAIZ / "editor" / "build_from_edit.py"), str(pasta), "--render"])
    else:
        print("\nPronto: blender.mp4 e edit.json em", pasta)
        print("Para o vídeo final com voz e legenda: abra no editor e clique Renderizar, ou rode: python editor/build_from_edit.py", pasta, "--render")


if __name__ == "__main__":
    main()
