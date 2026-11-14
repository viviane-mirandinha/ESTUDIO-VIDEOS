r"""encode.py - junta frames PNG + legenda.ass + mix.wav no MP4 final e gera a contact sheet de conferencia (12 quadros).
Encode aprovado: libx264 crf 19, maxrate 8M, bufsize 12M, profile high, level 4.1, g 60, yuv420p, 30 fps, AAC 256k, +faststart.
Uso:  python -X utf8 pipeline\encode.py PASTA "SAIDA\NN - TITULO.mp4" [--teste 3]
Precisa: PASTA\frames\f0000.png..., PASTA\legenda.ass, PASTA\audio\mix.wav
Saida: o MP4 + PASTA\conferencia_final.jpg (12 quadros 4x3, 270 px) -> olhar SO essa folha, nunca frame a frame.
"""
import argparse, os, shutil, subprocess

ap = argparse.ArgumentParser(); ap.add_argument("pasta"); ap.add_argument("saida")
ap.add_argument("--teste", type=float, default=0, help="so os N primeiros segundos (teste rapido)")
a = ap.parse_args()
W = os.path.abspath(a.pasta); OUT = os.path.abspath(a.saida)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
# libass no Windows: rodar com cwd = PASTA e caminhos relativos (evita escapar o "D:")
shutil.copy(os.path.join(FONTS, "Montserrat-ExtraBold.otf"), os.path.join(W, "_fonte.otf")) if not os.path.exists(os.path.join(W, "_fonte.otf")) else None
cmd = ["ffmpeg", "-y", "-v", "error", "-stats", "-framerate", "30", "-i", os.path.join("frames", "f%04d.png"),
       "-i", os.path.join("audio", "mix.wav")]
if a.teste: cmd += ["-t", str(a.teste)]
cmd += ["-vf", "ass=legenda.ass:fontsdir=.", "-map", "0:v", "-map", "1:a",
        "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-maxrate", "8M", "-bufsize", "12M",
        "-profile:v", "high", "-level", "4.1", "-g", "60", "-pix_fmt", "yuv420p", "-r", "30",
        "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-shortest", "-movflags", "+faststart", OUT]
subprocess.run(cmd, cwd=W, check=True)
os.remove(os.path.join(W, "_fonte.otf"))

dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", OUT],
                           capture_output=True, text=True).stdout.strip())
sheet = os.path.join(W, "conferencia_final.jpg")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", OUT, "-vf",
                f"fps=12/{dur:.3f},scale=270:-1,tile=4x3", "-frames:v", "1", sheet], check=True)
print("OK", OUT, f"{dur:.2f}s", "| folha:", sheet)
