# util.py — funções comuns da fábrica (zero token: só Python local)
import json
import re
import subprocess
import sys
import time
import unicodedata
from datetime import datetime
from pathlib import Path

FABRICA = Path(__file__).resolve().parent.parent          # EDITOR VIDEOS/fabrica
EDITOR = FABRICA.parent                                   # EDITOR VIDEOS
BUILD = EDITOR / "build_from_edit.py"
ESTILOS = FABRICA / "estilos"


def _print_seguro(linha):
    try:
        print(linha, flush=True)
    except UnicodeEncodeError:   # console do Windows (cp1252) não imprime certos caracteres → troca por '?'
        enc = getattr(sys.stdout, "encoding", None) or "ascii"
        print(linha.encode(enc, "replace").decode(enc, "replace"), flush=True)


def log(msg):
    _print_seguro(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


class Cronometro:
    """Mede minutos de máquina por etapa (vai pro RELATORIO.json)."""

    def __init__(self):
        self.etapas = {}
        self.inicio = datetime.now().astimezone()

    def marca(self, nome, t0):
        self.etapas[nome] = round((time.time() - t0) / 60, 2)
        log(f"{nome}: {self.etapas[nome]} min")

    def total(self):
        return round(sum(self.etapas.values()), 2)


def slug(s, maxlen=40):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()
    return s[:maxlen].rstrip("-")


def limpa_nome_arquivo(s):
    s = re.sub(r'[\\/:*?"<>|]+', "", s)
    return re.sub(r"\s+", " ", s).strip()


def proximo_numero(out_dir: Path):
    n = 0
    for p in out_dir.iterdir():
        m = re.match(r"^(\d{2,3})", p.name)
        if m and p.is_dir():
            n = max(n, int(m.group(1)))
    return n + 1


def nome_video(nn, canal, titulo):
    """Padrão do usuário: 'NN - DD-MM-AAAA - CANAL - TITULO' (≤200 chars)."""
    base = " - ".join(x for x in (f"{nn:02d}", datetime.now().strftime('%d-%m-%Y'), str(canal or "").strip().upper(), titulo) if x)
    return limpa_nome_arquivo(base)[:200]


def canal_na_tela(canal, marca=""):
    """Nome do canal DESENHADO no vídeo: só o que o aluno escreveu no campo. Vazio = nada na tela."""
    return str(canal or "").strip()


def run(cmd, cwd=None, timeout=None, check=True, quiet=False):
    """Roda comando mostrando a saída ao vivo (tail guardado pro erro)."""
    if not quiet:
        log("$ " + " ".join(str(c) for c in cmd[:6]) + (" ..." if len(cmd) > 6 else ""))
    p = subprocess.Popen([str(c) for c in cmd], cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         text=True, encoding="utf-8", errors="replace")
    tail = []
    t0 = time.time()
    for line in p.stdout:
        line = line.rstrip()
        if line:
            tail = (tail + [line])[-30:]
            if not quiet:
                _print_seguro("   " + line[:160])
        if timeout and time.time() - t0 > timeout:
            p.kill()
            raise RuntimeError(f"Timeout ({timeout}s): {cmd[0]}")
    p.wait()
    if check and p.returncode != 0:
        raise RuntimeError("Falhou: " + " ".join(map(str, cmd[:4])) + "\n" + "\n".join(tail[-12:]))
    return tail


_NVENC = None


def tem_nvenc():
    global _NVENC
    if _NVENC is None:
        try:
            r = subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "color=black:s=256x256:d=0.2", "-c:v", "h264_nvenc",
                                "-f", "null", "-"], capture_output=True, timeout=30, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            _NVENC = r.returncode == 0
        except Exception:
            _NVENC = False
    return _NVENC


def run_venc(antes, depois, crf=22, quiet=True):
    """ffmpeg com H.264 na placa NVIDIA (NVENC) quando houver; se falhar (sem NVIDIA, sessões esgotadas) refaz em libx264."""
    x264 = ["-c:v", "libx264", "-preset", "veryfast", "-crf", str(crf)]
    if tem_nvenc():
        try:
            return run([*antes, "-c:v", "h264_nvenc", "-preset", "p4", "-rc", "vbr", "-cq", str(crf), "-b:v", "0", *depois], quiet=quiet)
        except RuntimeError:
            pass
    return run([*antes, *x264, *depois], quiet=quiet)


def duracao_audio(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True)
    return float(out.stdout.strip() or 0)


def ler_json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def salvar_json(p, obj):
    Path(p).write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")


def frases_do_texto(texto):
    """Quebra o roteiro em frases (. ! ? …)."""
    t = re.sub(r"\s+", " ", texto.strip())
    partes = re.split(r"(?<=[.!?…])\s+", t)
    return [p.strip() for p in partes if p.strip()]
