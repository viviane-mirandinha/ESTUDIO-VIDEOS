#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Fase 2 sem watch page: flat + approximate_date (1 req/canal) -> views/hora por video; meta do canal via playlist-items 0."""
import json, subprocess, time, statistics, os, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mine import SEEDS, MIN_DUR

OUT = os.path.dirname(os.path.abspath(__file__))
NOW = datetime.now(timezone.utc).timestamp()

def run(args, timeout=120):
    for att in range(3):
        try:
            p = subprocess.run(["yt-dlp", "--no-warnings", "--ignore-errors"] + args, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
            if "429" in (p.stderr or ""): time.sleep(30 * (att + 1)); continue
            return p.stdout, p.stderr
        except subprocess.TimeoutExpired: time.sleep(5)
    return "", "timeout"

def channel(url):
    out, err = run(["--flat-playlist", "--playlist-end", "15", "--extractor-args", "youtubetab:approximate_date", "-j", url])
    vids = []
    for line in out.splitlines():
        try: d = json.loads(line)
        except Exception: continue
        if d.get("live_status") in ("is_live", "was_live"): continue
        ts = d.get("timestamp")
        hours = max((NOW - ts) / 3600, 12) if ts else None
        vc = d.get("view_count")
        vids.append({"id": d.get("id"), "title": d.get("title"), "views": vc, "dur": d.get("duration"), "upload": d.get("upload_date"),
                     "hours": round(hours) if hours else None, "vph": round(vc / hours) if (hours and vc) else None,
                     "channel": d.get("channel") or d.get("uploader"), "channel_id": d.get("channel_id")})
    meta = {}
    out2, _ = run(["--flat-playlist", "--playlist-items", "0", "-j", url.replace("/videos", "")])
    for line in out2.splitlines():
        try: d = json.loads(line)
        except Exception: continue
        if d.get("_type") == "playlist" or d.get("channel_follower_count") is not None:
            meta = {"subs": d.get("channel_follower_count"), "name": d.get("channel") or d.get("title"), "channel_id": d.get("channel_id"), "desc": (d.get("description") or "")[:200]}
    return vids, meta, err[-200:]

def main():
    cands = json.load(open(os.path.join(OUT, "search_channels.json"), encoding="utf-8"))
    targets = []
    for st, hs in SEEDS.items():
        for h in hs: targets.append({"key": h, "url": f"https://www.youtube.com/{h}/videos", "styles": [st], "src": "seed", "lang": "?"})
    for cid, c in sorted(cands.items(), key=lambda kv: -kv[1]["best"])[:90]:
        targets.append({"key": cid, "url": c["url"].rstrip("/") + "/videos", "styles": c["styles"], "src": c["src"], "lang": c["lang"], "name": c["name"]})
    results = []
    log = open(os.path.join(OUT, "mine2.log"), "a", encoding="utf-8")
    with ThreadPoolExecutor(4) as ex:
        futs = {ex.submit(channel, t["url"]): t for t in targets}
        for f in as_completed(futs):
            t = futs[f]
            try: vids, meta, err = f.result()
            except Exception as e: log.write(f"[erro] {t['key']} {e}\n"); continue
            longs = [v for v in vids if (v["dur"] or 0) >= MIN_DUR and v["views"]]
            if not longs: log.write(f"[canal] {t['key']}: sem longos ({len(vids)} vids) {err}\n"); log.flush(); continue
            med = statistics.median([v["views"] for v in longs])
            best = max(longs, key=lambda v: v["vph"] or 0)
            recent = [v for v in longs if v["hours"] and v["hours"] <= 24 * 45]
            med_vph_recent = statistics.median([v["vph"] for v in recent if v["vph"]]) if recent else 0
            r = {"key": t["key"], "name": meta.get("name") or longs[0]["channel"] or t.get("name"), "channel_id": meta.get("channel_id") or longs[0]["channel_id"],
                 "styles": t["styles"], "src": t["src"], "lang": t["lang"], "subs": meta.get("subs"), "desc": meta.get("desc", ""),
                 "median_views": med, "best_vph": best["vph"] or 0, "med_vph_45d": med_vph_recent, "n_long": len(longs), "videos": longs}
            r["url"] = f"https://www.youtube.com/channel/{r['channel_id']}" if r["channel_id"] else t["url"]
            results.append(r)
            log.write(f"[canal] {r['name']} subs={r['subs']} med={med} best_vph={r['best_vph']} med_vph45={med_vph_recent}\n"); log.flush()
            json.dump(results, open(os.path.join(OUT, "channels2.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    log.write("[fim]\n")

if __name__ == "__main__":
    main()
