#!/usr/bin/env python3
"""Local Whisper runner (faster-whisper / CTranslate2).

Runs INSIDE the dedicated whisper venv, not the skill's interpreter. Reads an
audio file, transcribes with faster-whisper, prints {"segments":[...]} JSON on
stdout in the same {start, end, text} shape the API path uses.

Usage:
    python local_whisper.py <audio-path> [--model large-v3] [--device auto]
                            [--language xx] [--compute-type auto]

On Windows the CUDA runtime libs (cuBLAS, cuDNN) ship as pip wheels
(nvidia-cublas-cu12, nvidia-cudnn-cu12) but their DLLs are not on PATH by
default; we register their bin dirs via os.add_dll_directory before importing
ctranslate2 so GPU mode works without touching system PATH.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


def _register_cuda_dlls() -> None:
    """Add pip-installed NVIDIA lib dirs to the DLL search path (Windows).

    The nvidia-*-cu12 wheels drop DLLs under site-packages/nvidia/<lib>/bin but
    don't put them on PATH. Locate each namespace package via importlib and
    register its bin/ dir so ctranslate2 can lazy-load cublas/cudnn at runtime.
    """
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
                # ctranslate2 delay-loads cublas via plain LoadLibrary, which
                # searches PATH but not add_dll_directory dirs — prepend too.
                os.environ["PATH"] = str(bindir) + os.pathsep + os.environ.get("PATH", "")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("audio")
    ap.add_argument("--model", default="large-v3")
    ap.add_argument("--device", default="auto", choices=["auto", "cuda", "cpu"])
    ap.add_argument("--language", default=None)
    ap.add_argument("--compute-type", default="auto")
    args = ap.parse_args()

    _register_cuda_dlls()

    from faster_whisper import WhisperModel

    device = args.device
    compute = args.compute_type

    def _load(dev: str, comp: str):
        if comp == "auto":
            comp = "float16" if dev == "cuda" else "int8"
        return WhisperModel(args.model, device=dev, compute_type=comp), dev, comp

    # Try GPU first when device=auto; fall back to CPU on any CUDA/load error.
    order = [device] if device != "auto" else ["cuda", "cpu"]
    model = used_device = used_compute = None
    last_err = None
    for dev in order:
        try:
            model, used_device, used_compute = _load(dev, compute)
            break
        except Exception as exc:  # noqa: BLE001 - report and try next device
            last_err = exc
            print(f"[local-whisper] load on {dev} failed: {exc}", file=sys.stderr)
    if model is None:
        print(f"[local-whisper] could not load model: {last_err}", file=sys.stderr)
        return 1

    print(
        f"[local-whisper] model={args.model} device={used_device} "
        f"compute={used_compute} — transcribing…",
        file=sys.stderr,
    )

    segments_iter, info = model.transcribe(
        args.audio,
        language=args.language,
        vad_filter=True,
        beam_size=5,
    )

    out = []
    for seg in segments_iter:
        text = (seg.text or "").strip()
        if not text:
            continue
        out.append({
            "start": round(float(seg.start), 2),
            "end": round(float(seg.end), 2),
            "text": text,
        })

    print(
        f"[local-whisper] language={info.language} "
        f"({info.language_probability:.2f}) → {len(out)} segments",
        file=sys.stderr,
    )
    print(json.dumps({"segments": out, "language": info.language}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
