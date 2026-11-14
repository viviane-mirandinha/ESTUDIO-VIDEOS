"""Baixa a referência (primeiros ~3 min) de cada projeto que ainda não tem <proj>/ref/ref.mp4.
Uso: python baixar_refs.py [pasta ...]   (padrão: VIDEOS-NOVOS). 1 download por vez. Log em baixar_refs.log."""
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "fabrica"))
from lib import rede_yt  # noqa: E402

PASTAS =[Path(a) for a in sys.argv[1:]] or [Path(str(__import__("pathlib").Path(__file__).resolve().parents[2] / "VIDEOS-NOVOS"))]
LOG = Path(__file__).with_name("baixar_refs.log")
EXTS = ("ref.mp4", "ref.webm", "ref.mp4.webm")


def log(msg):
    print(msg, flush=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(time.strftime("%H:%M:%S ") + msg + "\n")


def tem_ref(p: Path):
    return any((p / "ref" / n).exists() and (p / "ref" / n).stat().st_size > 50_000 for n in EXTS)


def baixar(url: str, dest: Path):
    dest.parent.mkdir(exist_ok=True)
    base = [*rede_yt.cmd(), "--no-playlist", "--no-part", "--force-overwrites", "--download-sections", "*0-180",
            "-o", str(dest), url]
    tentativas = [
        ["--extractor-args", "youtube:player_client=mweb", "-f", "18"],
        ["--extractor-args", "youtube:player_client=mweb", "-f", "b[ext=mp4][height<=480]/18/b"],
        ["-f", "18/b[ext=mp4][height<=480]/bv*[height<=480]+ba/b", "--merge-output-format", "mp4"],   # QA: YouTube sem formato único (só vídeo+áudio separados)
    ]
    err = ""
    for t in tentativas:
        r = subprocess.run(base[:1] + t + base[1:], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
        if dest.exists() and dest.stat().st_size > 50_000:
            return True, ""
        err = (r.stderr or r.stdout or "").strip().splitlines()
        err = next((l for l in reversed(err) if "ERROR" in l), err[-1] if err else "sem saída")
    return False, err


def main():
    for base in PASTAS:
        for p in sorted(x for x in base.iterdir() if (x / "edit.json").exists()):
            if tem_ref(p):
                log(f"OK (já tinha) {p.name}")
                continue
            try:
                ed = json.loads((p / "edit.json").read_text(encoding="utf-8-sig"))
            except Exception as e:
                log(f"FALHOU {p.name}: edit.json ilegível ({e})")
                continue
            url = (ed.get("referencia") or {}).get("video")
            if not url:
                log(f"FALHOU {p.name}: edit.json sem referencia.video")
                continue
            ok, err = baixar(url, p / "ref" / "ref.mp4")
            log(f"{'BAIXOU' if ok else 'FALHOU'} {p.name} {url} {'' if ok else err[:300]}")


if __name__ == "__main__":
    main()
