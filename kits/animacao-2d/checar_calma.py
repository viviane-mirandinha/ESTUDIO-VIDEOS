# checar_calma.py — mede o RITMO de movimento do vídeo renderizado (zero token) e compara com o original de referência.
# O original "Sócrates/Instagram" é CALMO: ~44 % das janelas de 1 s ficam quase paradas e só ~1,6 % da tela se mexe.
# Vídeo que vive em movimento (tudo andando, câmera em toda cena) parece amador. Aviso se < 25 % de janelas quase paradas
# ou > 3 % da tela em movimento. Uso: python kits/animacao-2d/checar_calma.py <video.mp4>
import subprocess, sys, numpy as np
path = sys.argv[1]; W, H, FPS = 320, 180, 10
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps={FPS},scale={W}:{H},format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
f = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.float32)
d = np.abs(np.diff(f, axis=0)); m = d.mean(axis=(1, 2)); corte = m > 12
dm = m[~corte]; area = (d > 12).mean(axis=(1, 2))[~corte].mean() * 100
jan = [dm[i:i + FPS].mean() for i in range(0, len(dm) - FPS + 1, FPS)] or [0]
paradas = float(np.mean(np.array(jan) < 0.3) * 100)
print(f"calma: {paradas:.0f}% das janelas de 1 s quase paradas (original 44%) | {area:.1f}% da tela em movimento (original 1,6%)")
aviso = []
if paradas < 25: aviso.append("movimento demais: menos de 25% de momentos de calma — deixe mais cenas só com respiração/revelação")
if area > 3.0: aviso.append("área em movimento alta (>3% da tela) — poucas coisas devem se mexer ao mesmo tempo")
print("AVISO: " + "; ".join(aviso) if aviso else "OK (ritmo calmo como o original)")
