"""Upbeat marimba groove for The Paper Rocket (120 bpm), synthesized from scratch, timed to the film.

Marks (s): countdown 10.1 (beeps 10.28/10.92/11.92) · BLAST OFF hit 12.75 · landing 21.75 (bump 22.72) ·
proud 24.3 · card 26.4 · CTA 29.2 (Comment 29.35, S-T-O-R-Y 29.65+0.15i, strip 30.6) · end 37.0
python3 groove.py groove.wav
"""
import sys
import wave

import numpy as np

SR, DUR = 48000, 37.0
N = int(SR * DUR)
out = np.zeros(N)
BEAT = 0.5
A4 = 440.0
NAMES = {"C": -9, "D": -7, "E": -5, "F": -4, "G": -2, "A": 0, "B": 2}


def hz(n):
    return A4 * 2 ** ((NAMES[n[0]] + (1 if "#" in n else 0) + (int(n[-1]) - 4) * 12) / 12)


def add(t0, sig, g=1.0):
    i = int(t0 * SR)
    j = min(N, i + len(sig))
    if 0 <= i < N:
        out[i:j] += g * sig[: j - i]


def marimba(t0, n, v=0.3, d=0.35):
    f = hz(n)
    t = np.arange(int(SR * d * 4)) / SR
    e = np.exp(-t / d) * np.minimum(1, t / 0.002)
    add(t0, v * e * (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t / 0.04)))


def bass(t0, n, v=0.35, d=0.4):
    f = hz(n)
    t = np.arange(int(SR * d * 2)) / SR
    e = np.exp(-t / d) * np.minimum(1, t / 0.005)
    add(t0, v * e * (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)))


def kick(t0, v=0.55):
    t = np.arange(int(SR * 0.3)) / SR
    f = 50 + 90 * np.exp(-t / 0.03)
    add(t0, v * np.exp(-t / 0.12) * np.sin(2 * np.pi * np.cumsum(f) / SR))


rng = np.random.default_rng(3)


def hat(t0, v=0.06, d=0.03):
    t = np.arange(int(SR * d * 5)) / SR
    noise = rng.standard_normal(len(t))
    noise = noise - np.convolve(noise, np.ones(8) / 8, mode="same")
    add(t0, v * np.exp(-t / d) * noise)


def clap(t0, v=0.16):
    for k in range(3):
        hat(t0 + k * 0.011, v, 0.05)


def beep(t0, n, v=0.22, d=0.28):
    f = hz(n)
    t = np.arange(int(SR * d)) / SR
    add(t0, v * np.minimum(1, (d - t) / 0.05) * np.minimum(1, t / 0.004) * np.sign(np.sin(2 * np.pi * f * t)) * 0.5)


def riser(t0, t1, v=0.12):
    t = np.arange(int(SR * (t1 - t0))) / SR
    f = 200 * (8 ** (t / t[-1]))
    noise = rng.standard_normal(len(t)) * 0.3
    add(t0, v * (t / t[-1]) ** 2 * (np.sin(2 * np.pi * np.cumsum(f) / SR) + noise))


def crash(t0, v=0.35):
    t = np.arange(int(SR * 1.6)) / SR
    noise = rng.standard_normal(len(t))
    noise = noise - np.convolve(noise, np.ones(4) / 4, mode="same")
    add(t0, v * np.exp(-t / 0.5) * noise)
    kick(t0, 0.9)


CHORDS = [("C3", ["C5", "E5", "G5", "E5"]), ("G2", ["B4", "D5", "G5", "D5"]),
          ("A2", ["C5", "E5", "A5", "E5"]), ("F2", ["A4", "C5", "F5", "C5"])]


def groove(t0, t1, full=False, light=False):
    b = 0
    t = t0
    while t < t1 - 1e-6:
        root, arp = CHORDS[(b // 4) % 4]
        beat_in_bar = b % 4
        if beat_in_bar in (0, 2) or full:
            bass(t, root, 0.32 if full else 0.26)
        if not light and (beat_in_bar in (0, 2) or (full and beat_in_bar == 3)):
            kick(t, 0.5 if full else 0.35)
        if full and beat_in_bar in (1, 3):
            clap(t)
        hat(t + BEAT / 2, 0.07 if full else 0.045)
        marimba(t, arp[beat_in_bar], 0.26)
        marimba(t + BEAT / 2, arp[(beat_in_bar + 2) % 4], 0.17 if not full else 0.22)
        if full:
            marimba(t + BEAT * 0.75, arp[(beat_in_bar + 1) % 4], 0.12)
        b += 1
        t += BEAT


groove(0.0, 10.0)                       # backyard → paint
for t, n in ((10.28, "C5"), (10.92, "C5"), (11.92, "G5")):  # 3 · 2 · 1
    beep(t, n)
riser(10.1, 12.75)
crash(12.75)                            # BLAST OFF
groove(12.75, 21.75, full=True)         # clouds → birds → rainbow → stars → Saturn
groove(21.75, 24.3, light=True)         # landing
for k, n in enumerate(("C5", "E5", "G5", "C6")):  # proud moment
    marimba(24.35 + k * 0.12, n, 0.3, 0.6)
groove(24.5, 36.0, light=True)          # card + CTA bed
marimba(26.7, "G5", 0.3, 0.6)           # card lands
marimba(29.35, "E5", 0.28, 0.5)         # "Comment"
for i, n in enumerate(("C6", "D6", "E6", "G6", "A6")):  # S T O R Y
    marimba(29.65 + 0.15 * i, n, 0.32, 0.5)
for n in ("C6", "G5", "E5"):            # strip pops
    marimba(30.6, n, 0.22, 0.7)
marimba(35.9, "C5", 0.25, 1.2)
marimba(35.9, "G5", 0.2, 1.2)

fade = np.ones(N)
fade[-int(1.0 * SR):] = np.linspace(1, 0, int(1.0 * SR))
out *= fade
out = 0.85 * out / np.abs(out).max()
st = np.stack([out, np.roll(out, int(0.008 * SR)) * 0.95], 1)
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((st * 32767).astype("<i2").tobytes())
print("wrote", sys.argv[1])
