#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""sheet.py <videoId> <out.jpg> [dur_seg]  — baixa 2 trechos de 60s (inicio+meio) em ~360p e gera UM contact-sheet 6x5.
Nao guarda frames soltos; apaga o mp4 depois."""
import subprocess, sys, os, tempfile, glob, shutil

def main():
    vid, out = sys.argv[1], sys.argv[2]
    dur = int(sys.argv[3]) if len(sys.argv) > 3 else 900
    tmp = tempfile.mkdtemp(prefix="sh_")
    a0, a1 = 25, 85
    mid = max(120, min(dur // 2, dur - 70)) if dur > 200 else 85
    secs = ["--download-sections", f"*{a0}-{a1}"]
    if dur > 200: secs += ["--download-sections", f"*{mid}-{mid+60}"]
    for att in range(3):
        r = subprocess.run(["yt-dlp", "--no-warnings", "--extractor-args", "youtube:player_client=mweb", "-f", "18/worst[height>=360][ext=mp4]/worst[height>=360]/worst",
                            "--force-keyframes-at-cuts", *secs, "-o", os.path.join(tmp, "p%(section_start)05d.%(ext)s"),
                            f"https://www.youtube.com/watch?v={vid}"], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
        parts = sorted(glob.glob(os.path.join(tmp, "p*.*")))
        if parts: break
        import time; time.sleep(45)
    if not parts:
        print("FALHOU", vid, r.stderr[-300:]); shutil.rmtree(tmp, ignore_errors=True); sys.exit(1)
    lst = os.path.join(tmp, "l.txt")
    with open(lst, "w", encoding="utf-8") as f:
        for p in parts: f.write(f"file '{p.replace(chr(92), '/')}'\n")
    n = len(parts)
    # 30 frames: fps = 30 / (60*n)
    fps = 30 / (60 * n)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst,
                    "-vf", f"fps={fps:.4f},scale=320:-2,tile=6x5", "-frames:v", "1", "-q:v", "4", out], check=False)
    shutil.rmtree(tmp, ignore_errors=True)
    print("OK", out, os.path.getsize(out) if os.path.exists(out) else 0)

if __name__ == "__main__":
    main()
