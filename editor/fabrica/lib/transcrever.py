# transcrever.py — chama o faster-whisper (GPU) no venv dedicado e devolve words.json
from pathlib import Path

from .util import run, ler_json, log

WHISPER_PY = Path(__import__("os").environ.get("ESTUDIO_WHISPER_PY") or __import__("sys").executable)
RUNNER = Path(__file__).resolve().parent / "whisper_run.py"


def transcrever(audio: Path, saida: Path, modelo="large-v3", idioma="pt"):
    """idioma: código whisper (pt/en/es) ou "auto"."""
    if not WHISPER_PY.exists():
        raise RuntimeError(f"venv do whisper não encontrado: {WHISPER_PY}")
    import time
    for tent in range(3):
        try:
            run([WHISPER_PY, RUNNER, str(audio), str(saida), modelo, idioma or "pt"], timeout=3600)
            break
        except RuntimeError as e:   # falta de RAM/pagefile na máquina compartilhada (mkl_malloc, cublas dll)
            if tent == 2:
                raise
            log(f"whisper falhou ({str(e)[-120:]}), tentando de novo em 20 s…")
            time.sleep(20)
    words = ler_json(saida)
    if not words:
        raise RuntimeError("whisper não devolveu palavras")
    log(f"whisper: {len(words)} palavras, última termina em {words[-1]['e']}s")
    return words
