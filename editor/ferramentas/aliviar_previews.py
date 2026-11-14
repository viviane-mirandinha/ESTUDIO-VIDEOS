"""Deixa os vídeos de exemplo (skills_ia/previews/*.mp4) leves: 720p, ~2-6 MB. O original fica em previews/_original/."""
import shutil
import subprocess
from pathlib import Path

PREV = Path(__file__).resolve().parent.parent / "skills_ia" / "previews"
ORIG = PREV / "_original"
LIMITE = 6_000_000

ORIG.mkdir(exist_ok=True)
for f in sorted(PREV.glob("*.mp4")):
    if f.stat().st_size <= LIMITE:
        continue
    bk = ORIG / f.name
    if not bk.exists():
        shutil.copy2(f, bk)
    tmp = f.with_suffix(".tmp.mp4")
    r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(bk),
                        "-vf", "scale='if(gt(iw,ih),1280,720)':-2", "-c:v", "libx264", "-preset", "medium", "-crf", "27",
                        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", str(tmp)])
    if r.returncode == 0 and tmp.exists() and tmp.stat().st_size > 50_000:
        tmp.replace(f)
        print(f"{f.name}: {bk.stat().st_size / 1e6:.0f} MB -> {f.stat().st_size / 1e6:.1f} MB")
    else:
        tmp.unlink(missing_ok=True)
        print(f"{f.name}: ERRO, mantido o original")
