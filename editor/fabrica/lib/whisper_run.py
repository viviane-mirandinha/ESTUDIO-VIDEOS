# whisper_run.py — RODA DENTRO do venv do whisper (.venv do pacote).
# Uso: python whisper_run.py <audio> <saida words.json> [modelo]
# Saída: [{"w": "palavra", "s": 1.23, "e": 1.60}, ...]  (tempos absolutos em segundos)
import json
import os
import subprocess
import sys
from pathlib import Path


def _register_cuda_dlls():
    if not hasattr(os, "add_dll_directory"):
        return
    import importlib.util
    for mod in ("nvidia.cublas", "nvidia.cudnn", "nvidia.cuda_nvrtc"):
        try:
            spec = importlib.util.find_spec(mod)
        except (ImportError, ValueError):
            spec = None
        locs = list(spec.submodule_search_locations) if spec and spec.submodule_search_locations else []
        for base in locs:
            bindir = Path(base) / "bin"
            if bindir.is_dir():
                try:
                    os.add_dll_directory(str(bindir))
                except OSError:
                    pass
                os.environ["PATH"] = str(bindir) + os.pathsep + os.environ.get("PATH", "")


def main():
    audio, saida = sys.argv[1], sys.argv[2]
    modelo = sys.argv[3] if len(sys.argv) > 3 else "large-v3"
    lang = sys.argv[4] if len(sys.argv) > 4 else "pt"
    lang = None if lang in ("auto", "") else lang   # auto = whisper detecta o idioma
    _register_cuda_dlls()
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    import numpy as np
    from faster_whisper import WhisperModel
    # decodifica com ffmpeg (PyAV quebra com mp3 em algumas versões)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", audio, "-f", "f32le", "-ac", "1", "-ar", "16000", "-"],
                         capture_output=True).stdout
    pcm = np.frombuffer(raw, dtype=np.float32)
    try:
        m = WhisperModel(modelo, device="cuda", compute_type="float16")
        segs, info = m.transcribe(pcm, language=lang, word_timestamps=True, vad_filter=False)
        out = [{"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2)} for s in segs for w in s.words]
    except Exception as e:
        print("GPU falhou, caindo pra CPU small:", str(e)[:200], flush=True)
        m = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=4)
        segs, info = m.transcribe(pcm, language=lang, word_timestamps=True)
        out = [{"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2)} for s in segs for w in s.words]
    out = [w for w in out if w["w"]]
    Path(saida).write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    print(len(out), "palavras", flush=True)


if __name__ == "__main__":
    main()
