#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Lote 2 (lista do usuario): stats flat por canal + resolve videos soltos via mweb. Saida: lote2.json + lote2.md"""
import json, subprocess, os, sys, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mine2 import channel, run, MIN_DUR
from concurrent.futures import ThreadPoolExecutor
OUT = os.path.dirname(os.path.abspath(__file__))

CHANNELS = {  # handle/url -> nota do usuario
 "@onesmallif": "avatar animado (consistencia)", "@GlenPritchardBuilds": "avatar, pode ser evergreen", "@nomadedigitalraiam": "vlog normal; mesmos assuntos, edicao simples",
 "@PeoplePatternsPsych": "", "@ryoga.training": "academia exercicios", "@bonafillorelatos": "", "@deskstandard": "", "@SilasMercerYT": "",
 "@MilitaryStorm-Official": "militar", "@AlabamaRevealed": "", "@ProsecutorMatthewHanson": "", "@YourVibeChoice": "", "@KnownMatter-s5q": "filmes (precisa cenas de filme)",
 "@theapprenticesguide": "", "@criticallatitudetv": "", "@Americaunderconstruction1": "", "@AgentFlappy": "animacao", "@Healoloogy": "",
 "channel/UCUmCVRNy7wEOjgbteKyiUZw": "", "@mikinoyarinaoshi": "japones, pouca edicao", "@genel_ai": "japones, pouca edicao",
}
VIDEOS = {"Wap9PO01fUc": "avatar animado", "hVMYsqfp6hA": "AVATAR", "T_fqnsc9quM": "", "nXLxwFnBRNY": "", "gLtO6ZfKt3c": "FILMES"}

def resolve(vid):
    out, err = run(["--extractor-args", "youtube:player_client=mweb", "-j", "--no-download", f"https://www.youtube.com/watch?v={vid}"], timeout=90)
    try: d = json.loads(out.strip().splitlines()[-1])
    except Exception: return {"id": vid, "erro": err[-150:]}
    return {"id": vid, "title": d.get("title"), "views": d.get("view_count"), "dur": d.get("duration"), "upload": d.get("upload_date"),
            "channel": d.get("channel"), "channel_id": d.get("channel_id"), "subs": d.get("channel_follower_count"), "lang": d.get("language")}

def main():
    vids = {}
    with ThreadPoolExecutor(2) as ex:
        for r in ex.map(resolve, VIDEOS): vids[r["id"]] = {**r, "nota": VIDEOS[r["id"]]}
    targets = dict(CHANNELS)
    for v in vids.values():
        if v.get("channel_id") and not any(v["channel_id"] in k for k in targets):
            targets[f"channel/{v['channel_id']}"] = f"(do vídeo {v['id']}) {v['nota']}"
    def one(k):
        v, meta, err = channel(f"https://www.youtube.com/{k}/videos")
        longs = [x for x in v if (x["dur"] or 0) >= 180 and x["views"]]
        med = statistics.median([x["views"] for x in longs]) if longs else 0
        rec = [x for x in longs if x["hours"] and x["hours"] <= 24 * 45]
        mv = statistics.median([x["vph"] for x in rec if x["vph"]]) if rec else 0
        return {"key": k, "nota": targets[k], "name": meta.get("name") or (v[0]["channel"] if v else k), "channel_id": meta.get("channel_id") or (v[0]["channel_id"] if v else None),
                "n": len(v), "n_long": len(longs), "median_views": med, "med_vph_45d": mv, "best_vph": max([x["vph"] or 0 for x in longs] or [0]),
                "med_dur": statistics.median([x["dur"] for x in longs]) if longs else 0, "videos": sorted(longs, key=lambda x: -(x["vph"] or 0))[:5], "err": err}
    res = []
    with ThreadPoolExecutor(4) as ex:
        for r in ex.map(one, list(targets)): res.append(r); print(r["key"], r["name"], r["n"], r["med_vph_45d"], flush=True)
    json.dump({"canais": res, "videos": vids}, open(os.path.join(OUT, "lote2.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()
