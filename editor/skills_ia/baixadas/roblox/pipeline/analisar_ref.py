r"""analisar_ref.py - analise de um reel Roblox de referencia (modo B "clonar" ou pra estudar estrutura).
Uso:  python -X utf8 pipeline\analisar_ref.py "URL ou caminho.mp4" PASTA_REF
Faz: 1) baixa com yt-dlp (se for URL) -> PASTA_REF\ref.mp4 (+ ref.info.json)
     2) faster-whisper large-v3-turbo CPU int8 com tempo por palavra -> TRANSCRICAO.txt + ref_palavras.json
     3) cortes de cena (ffmpeg scene>0.3) -> cortes.txt (tempo de cada corte = ritmo de edicao)
     4) contact sheets 5x4 com 1 quadro a cada 0,9 s -> sheet1.jpg, sheet2.jpg... (olhar SO as folhas)
"""
import json, os, re, subprocess, sys
import numpy as np

src, W = sys.argv[1], sys.argv[2]
os.makedirs(W, exist_ok=True)
ref = os.path.join(W, "ref.mp4")
if re.match(r"https?://", src):
    subprocess.run(["yt-dlp", "-f", "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/b", "--merge-output-format", "mp4",
                    "--write-info-json", "-o", os.path.join(W, "ref.%(ext)s"), src], check=True)
elif os.path.abspath(src) != os.path.abspath(ref):
    import shutil; shutil.copy(src, ref)

dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", ref],
                           capture_output=True, text=True).stdout.strip())
print("duracao", round(dur, 2))

aud = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", ref, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                                   capture_output=True, check=True).stdout, np.float32)
from faster_whisper import WhisperModel
m = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8")
segs, info = m.transcribe(aud, word_timestamps=True)
segs = list(segs)
open(os.path.join(W, "TRANSCRICAO.txt"), "w", encoding="utf8").write(
    f"idioma: {info.language}\n" + "\n".join(f"[{s.start:6.2f}-{s.end:6.2f}] {s.text.strip()}" for s in segs))
json.dump([{"w": x.word.strip(), "s": round(x.start, 3), "e": round(x.end, 3)} for s in segs for x in s.words],
          open(os.path.join(W, "ref_palavras.json"), "w", encoding="utf8"), ensure_ascii=False, indent=0)

r = subprocess.run(["ffmpeg", "-hide_banner", "-i", ref, "-vf", "select='gt(scene,0.3)',showinfo", "-an", "-f", "null", "-"],
                   capture_output=True, text=True).stderr
cuts = [float(x) for x in re.findall(r"pts_time:([\d.]+)", r)]
gaps = np.diff([0] + cuts + [dur])
open(os.path.join(W, "cortes.txt"), "w").write(
    f"{len(cuts)} cortes | plano mediano {np.median(gaps):.2f}s | min {gaps.min():.2f} | max {gaps.max():.2f}\n" +
    "\n".join(f"{c:.2f}" for c in cuts))

per = 20 * 0.9
n = int(np.ceil(dur / per))
for k in range(n):
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(k * per), "-t", str(per), "-i", ref, "-vf",
                    "fps=1/0.9,scale=216:-1,tile=5x4", "-frames:v", "1", os.path.join(W, f"sheet{k + 1}.jpg")], check=True)
print("OK", W, "| folhas:", n, "| cortes:", len(cuts))
