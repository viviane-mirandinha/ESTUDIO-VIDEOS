"""teste_saude.py — confere a instalação do Estúdio de Vídeos e grava RELATORIO-INSTALACAO.txt.

Uso (o setup chama sozinho no fim):  .venv/Scripts/python.exe teste_saude.py   [--sem-video]
Faz um vídeo de teste de ~10 s pela fábrica (roteiro fixo, sem depender do Ollama) para provar que voz, whisper e render funcionam.
"""
import json
import os
import platform
import shutil
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

PKG = Path(__file__).resolve().parent
WIN = os.name == "nt"
HF = PKG / "node_modules" / ".bin" / ("hyperframes.cmd" if WIN else "hyperframes")
R = []   # (ok, item, detalhe)


def checa(item, fn):
    try:
        det = fn()
        R.append((True, item, str(det or "ok")))
        return True
    except Exception as e:
        R.append((False, item, str(e).strip().splitlines()[-1][:160] if str(e).strip() else type(e).__name__))
        return False


def cmd(*a, timeout=60):
    p = subprocess.run([str(x) for x in a], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
    if p.returncode != 0:
        raise RuntimeError((p.stderr or p.stdout or f"código {p.returncode}").strip()[-300:])
    return (p.stdout or p.stderr).strip().splitlines()[0][:80] if (p.stdout or p.stderr).strip() else "ok"


def gpu():
    if not shutil.which("nvidia-smi"):
        return "sem NVIDIA (whisper na CPU, mais lento)"
    return cmd("nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader")


def ollama():
    modelo = os.environ.get("ESTUDIO_OLLAMA_MODELO", "qwen2.5:7b")
    with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=5) as r:
        nomes = [m["name"] for m in json.load(r).get("models", [])]
    if not any(n.startswith(modelo.split(":")[0]) for n in nomes):
        raise RuntimeError(f"Ollama no ar, mas sem o modelo {modelo} (rode: ollama pull {modelo})")
    return f"{modelo} ok"


def edge():
    import asyncio
    import edge_tts
    out = PKG / ".teste_voz.mp3"
    asyncio.run(edge_tts.Communicate("Teste de voz.", "pt-BR-AntonioNeural").save(str(out)))
    ok = out.exists() and out.stat().st_size > 1000
    out.unlink(missing_ok=True)
    if not ok:
        raise RuntimeError("voz vazia (sem internet?)")
    return "voz Microsoft ok (precisa de internet)"


def video():
    rot = PKG / ".teste_roteiro.txt"
    rot.write_text("Este é um vídeo de teste do Estúdio. Se você está ouvindo esta voz, a instalação funcionou.", encoding="utf-8")
    antes = set((PKG / "VIDEOS").glob("*")) if (PKG / "VIDEOS").exists() else set()
    t0 = time.time()
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
    p = subprocess.run([sys.executable, "fabrica.py", "--estilo", "historia-simples", "--tema", "Teste de instalação",
                        "--canal", "TESTE", "--roteiro", str(rot), "--tts", "edge"],
                       cwd=PKG / "editor" / "fabrica", capture_output=True, text=True, encoding="utf-8", errors="replace",
                       timeout=1800, env=env)
    rot.unlink(missing_ok=True)
    novas = [d for d in (PKG / "VIDEOS").glob("*") if d not in antes and d.is_dir()]
    mp4 = [f for d in novas for f in d.glob("*.mp4") if f.stem not in ("leve", "final")] or [f for d in novas for f in d.glob("*.mp4")]
    if p.returncode != 0 or not mp4:
        raise RuntimeError("fábrica falhou: " + (p.stdout + p.stderr).strip()[-300:])
    return f"{mp4[0]} ({time.time() - t0:.0f} s)"


def main():
    sem_video = "--sem-video" in sys.argv
    checa("Sistema", lambda: f"{platform.system()} {platform.release()} {platform.machine()}")
    checa("Python do pacote", lambda: f"{sys.version.split()[0]} em {sys.executable}")
    checa("Bibliotecas Python", lambda: __import__("fastapi") and __import__("faster_whisper") and __import__("edge_tts") and "ok")
    checa("ffmpeg", lambda: cmd("ffmpeg", "-version"))
    checa("yt-dlp (Bombando / referências)", lambda: cmd(str(Path(sys.executable).parent / ("yt-dlp.exe" if os.name == "nt" else "yt-dlp")), "--version"))
    checa("Node.js", lambda: cmd("node", "--version"))
    checa("HyperFrames (render)", lambda: cmd(HF, "--version", timeout=120))
    checa("Chrome do render", lambda: cmd(HF, "browser", "path", timeout=120).splitlines()[-1])
    checa("Placa de vídeo", gpu)
    checa("Ollama (roteiro grátis)", ollama)
    checa("Voz edge-tts", edge)
    if not sem_video:
        checa("Vídeo de teste (voz + whisper + render)", video)
    linhas = ["RELATÓRIO DA INSTALAÇÃO — Estúdio de Vídeos", f"Data: {datetime.now():%d/%m/%Y %H:%M}", f"Pasta: {PKG}", ""]
    linhas += [f"{'✅' if ok else '❌'} {item}: {det}" for ok, item, det in R]
    falhas = [i for ok, i, _ in R if not ok]
    linhas += ["", "RESULTADO: " + ("TUDO OK — abra o editor com iniciar.bat / bash iniciar.sh" if not falhas
                                    else "faltou: " + ", ".join(falhas) + " — peça ao Claude: 'deu erro na instalação, resolve' e mostre este arquivo")]
    txt = "\n".join(linhas)
    (PKG / "RELATORIO-INSTALACAO.txt").write_text(txt, encoding="utf-8")
    print(txt)
    sys.exit(1 if any(not ok and item.startswith(("Python", "Bibliotecas", "ffmpeg", "Node", "HyperFrames", "Vídeo")) for ok, item, _ in R) else 0)


if __name__ == "__main__":
    main()
