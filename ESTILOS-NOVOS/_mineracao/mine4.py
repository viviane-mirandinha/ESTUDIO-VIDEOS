#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Lote 3: videos soltos -> canal -> stats flat -> sheet por video enviado -> composto."""
import json, os, sys, subprocess, statistics, re, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mine3 import resolve
from mine2 import channel
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "lote3"); os.makedirs(OUT, exist_ok=True)
VIDS = ["jgK_1M4UboY", "hhLnlTQFcNk", "O63gU42dQAs", "H9LincTauEU", "3aQcZlj8XaM", "P7zBuMusbi4"]
res = []
for vid in VIDS:
    v = resolve(vid)
    cid = v.get("channel_id")
    r = {"video": v, "canal": None}
    if cid:
        vs, meta, err = channel(f"https://www.youtube.com/channel/{cid}/videos")
        longs = [x for x in vs if (x["dur"] or 0) >= 180 and x["views"]]
        rec = [x for x in longs if x["hours"] and x["hours"] <= 24 * 45]
        r["canal"] = {"channel_id": cid, "name": v.get("channel"), "n": len(vs), "median_views": statistics.median([x["views"] for x in longs]) if longs else 0,
                      "med_vph_45d": statistics.median([x["vph"] for x in rec if x["vph"]]) if rec else 0, "best_vph": max([x["vph"] or 0 for x in longs] or [0]),
                      "med_dur": statistics.median([x["dur"] for x in longs]) if longs else 0, "videos": sorted(longs, key=lambda x: -(x["vph"] or 0))[:3]}
    res.append(r); print(vid, v.get("channel"), v.get("views"), v.get("dur"), (r["canal"] or {}).get("med_vph_45d"), flush=True)
    out = os.path.join(OUT, f"{re.sub(r'[^a-z0-9]+', '-', (v.get('channel') or 'x').lower()).strip('-')[:24]}-{vid}.jpg")
    subprocess.run([sys.executable, "-I", "-X", "utf8", os.path.join(HERE, "sheet.py"), vid, out, str(int(v.get("dur") or 600))], capture_output=True)
json.dump(res, open(os.path.join(HERE, "lote3.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
fs = sorted(glob.glob(os.path.join(OUT, "*.jpg")))
fs = [f for f in fs if "comp" not in os.path.basename(f)]
while len(fs) < 6: fs.append(fs[-1])
args = ["ffmpeg", "-y", "-v", "error"]
for f in fs[:6]: args += ["-i", f]
fc = "".join(f"[{k}:v]scale=960:450[v{k}];" for k in range(6)) + "[v0][v1]hstack[r0];[v2][v3]hstack[r1];[v4][v5]hstack[r2];[r0][r1][r2]vstack=inputs=3[o]"
subprocess.run(args + ["-filter_complex", fc, "-map", "[o]", "-q:v", "5", os.path.join(OUT, "comp0.jpg")], capture_output=True)
print("ordem:", [os.path.basename(f) for f in fs[:6]])
