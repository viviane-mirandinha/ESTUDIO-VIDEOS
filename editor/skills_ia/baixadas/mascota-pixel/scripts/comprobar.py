#!/usr/bin/env python3
"""Comprueba que el ordenador tiene lo necesario y lo instala si falta.

Uso:  python3 comprobar.py
"""
import importlib, os, subprocess, sys

ok = True


def instala(paquete):
    for extra in (["--break-system-packages"], []):
        r = subprocess.run([sys.executable, "-m", "pip", "install", "-q", *extra, paquete], capture_output=True, text=True)
        if r.returncode == 0:
            return True
    return False


print(f"Python {sys.version.split()[0]}")
if sys.version_info < (3, 9):
    print("  ✗ Hace falta Python 3.9 o más nuevo."); ok = False
for mod, pkg in (("PIL", "pillow"), ("numpy", "numpy")):
    try:
        m = importlib.import_module(mod)
        print(f"  ✓ {pkg} {getattr(m, '__version__', '')}")
    except ImportError:
        print(f"  … instalando {pkg}")
        if not instala(pkg):
            print(f"  ✗ No se pudo instalar {pkg}."); ok = False
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from comun import FFMPEG, fuente
    r = subprocess.run([FFMPEG, "-version"], capture_output=True, text=True)
    print("  ✓ ffmpeg:", r.stdout.split("\n")[0][:60])
    tiene_x264 = "libx264" in subprocess.run([FFMPEG, "-hide_banner", "-encoders"], capture_output=True, text=True).stdout
    print("  ✓ codificador H.264" if tiene_x264 else "  ✗ ffmpeg sin libx264"); ok = ok and tiene_x264
    fuente("extrabold", 40); fuente("mono", 30)
    print("  ✓ fuentes Poppins y JetBrains Mono")
except SystemExit as e:
    print("  ✗", e); ok = False
try:
    import faster_whisper  # noqa: F401
    print("  ✓ faster-whisper (reconocimiento de voz)")
except ImportError:
    print("  · faster-whisper no está: alinear.py lo instalará si hay voz (sin voz no hace falta).")
try:
    import scipy  # noqa: F401
except ImportError:
    print("  · scipy no está (opcional; el recorte del fondo irá algo más lento).")
print("TODO LISTO" if ok else "FALTA ALGO: mira los ✗ de arriba.")
sys.exit(0 if ok else 1)
