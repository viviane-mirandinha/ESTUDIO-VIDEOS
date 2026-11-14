"""Mix narration + music + sound effects -> film/assets/mix.wav (the film's only audio track).
usage: python3 audio/mix.py narration.mp3 --dur 37 [--music audio/groove.wav] [--vo-at 0] [--sfx sfx/boing.mp3@22.6 sfx/swish.mp3@3.4 ...]
- The voice is levelled to a steady loudness; the music ducks under the voice; effects sit at 45%.
- Keep --vo-at at 0 when src/words.json was made from this exact narration file (the word times then match the film)."""
import argparse, os, subprocess, wave
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("narration"); ap.add_argument("--dur", type=float, required=True)
ap.add_argument("--music", default=None); ap.add_argument("--vo-at", type=float, default=0.0)
ap.add_argument("--sfx", nargs="*", default=[], help="file@seconds")
a = ap.parse_args()
SR = 48000; N = int(SR * a.dur)
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "film", "assets", "mix.wav")


def load(p):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, "<f4").reshape(-1, 2).copy()


def place(bus, s, t0, g=1.0):
    i = int(t0 * SR); j = min(N, i + len(s))
    if 0 <= i < N: bus[i:j] += g * s[: j - i]


vo = np.zeros((N, 2), np.float32)
place(vo, load(a.narration), a.vo_at)
vo *= 0.125 / (np.sqrt(np.mean(vo[np.abs(vo).max(1) > 0.01] ** 2)) + 1e-9)
music = np.zeros((N, 2), np.float32)
if a.music:
    m = load(a.music)[:N]; music[: len(m)] = m
sfx = np.zeros((N, 2), np.float32)
for item in a.sfx:
    f, t = item.rsplit("@", 1); place(sfx, load(f), float(t), 0.9)
lvl = np.abs(vo).max(1); win = int(0.2 * SR)
duck = np.convolve(lvl > 0.02, np.ones(win) / win, mode="same")[:, None]
mix = vo + music * (0.5 - 0.22 * np.clip(duck * 2, 0, 1)) + 0.45 * sfx
mix = 0.89 * mix / (np.abs(mix).max() + 1e-9)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with wave.open(OUT, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype("<i2").tobytes())
print("wrote", os.path.normpath(OUT))
