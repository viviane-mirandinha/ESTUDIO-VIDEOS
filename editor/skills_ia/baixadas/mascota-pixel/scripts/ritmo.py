#!/usr/bin/env python3
"""Control de ritmo: comprueba que el vídeo nunca se quede quieto demasiado tiempo.

Uso:  python3 ritmo.py PROYECTO/salida/reel.mp4 [--max 0.6]

Mide qué fotogramas cambian respecto al anterior, en total y por zonas (titular, tarjeta, personaje).
Avisa de cada tramo de más de --max segundos sin ningún cambio en pantalla.
"""
import argparse, os, subprocess, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comun import FFMPEG  # noqa: E402

ZONAS = {"titular": (290, 640, 0, 1080), "tarjeta": (640, 1230, 0, 1080), "personaje": (1230, 1920, 0, 720)}


def huecos(cambia, fps):
    idx = np.where(cambia)[0]
    bordes = np.concatenate([[-1], idx, [len(cambia)]])
    salida = []
    for a, b in zip(bordes[:-1], bordes[1:]):
        if b - a - 1 > 0:
            salida.append(((a + 1) / fps, (b - a) / fps))
    return salida


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("--max", type=float, default=0.6)
    a = ap.parse_args()
    fps = 30
    w, h = 180, 320
    raw = subprocess.run([FFMPEG, "-v", "error", "-i", a.video, "-vf", f"fps={fps},scale={w}:{h},format=gray",
                          "-f", "rawvideo", "-"], capture_output=True).stdout
    f = np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.int16)
    if len(f) < 2:
        sys.exit("No he podido leer el vídeo.")
    d = np.abs(np.diff(f, axis=0)) > 10
    total = d.mean(axis=(1, 2)) > 0.0006
    print(f"Duración: {len(f) / fps:.1f} s · fotogramas con cambio: {total.mean() * 100:.0f} %")
    for nombre, (y0, y1, x0, x1) in ZONAS.items():
        z = d[:, y0 * h // 1920:y1 * h // 1920, x0 * w // 1080:x1 * w // 1080].mean(axis=(1, 2)) > 0.002
        largo = max((g for _, g in huecos(z, fps)), default=0)
        print(f"  {nombre:10s} activo {z.mean() * 100:3.0f} % · quieto como mucho {largo:.2f} s")
    malos = [(t, g) for t, g in huecos(total, fps) if g > a.max]
    if malos:
        print(f"AVISO: {len(malos)} tramo(s) de más de {a.max} s sin nada que se mueva:")
        for t, g in malos:
            print(f"  en el segundo {t:.1f}: {g:.2f} s quieto → añade un cambio (titular nuevo, elemento que entra, pose)")
    else:
        largo = max((g for _, g in huecos(total, fps)), default=0)
        print(f"OK: ningún tramo quieto de más de {a.max} s (el más largo: {largo:.2f} s).")


if __name__ == "__main__":
    main()
