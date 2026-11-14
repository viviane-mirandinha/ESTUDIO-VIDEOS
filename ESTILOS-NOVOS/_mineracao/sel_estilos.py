#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Seleciona estilos novos -> pastas ESTILOS-NOVOS/NN-nome/REFERENCIA.txt + fila de contact-sheets (sheets.txt)."""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
DEST = str(__import__("pathlib").Path(__file__).resolve().parents[2] / "ESTILOS-NOVOS")
ch = json.load(open(os.path.join(HERE, "channels2.json"), encoding="utf-8"))
for r in ch:
    if not r["name"]: r["name"] = r["key"].lstrip("@")
    r["url"] = r["url"].replace("/videos", "")

def find(k):
    for r in ch:
        if r["key"] == k or (r["name"] or "").lower().startswith(k.lower()): return r
    raise SystemExit("nao achei " + k)

# pasta -> [(canal, n_videos, idioma)]
SEL = [
 ("01-whiteboard-quadro", [("@AcademiaPlay", 2, "ES"), ("@AfterSkool", 1, "EN"), ("@BullyMagnets", 1, "ES")]),
 ("02-true-crime-arquivo", [("Dr Insanity", 1, "EN"), ("Dieck Docs", 1, "ES"), ("Ossos Perdidos", 1, "PT"), ("Marcos Campos", 1, "PT")]),
 ("03-top10-contagem", [("@DocTops", 2, "ES"), ("ROOM 13", 1, "EN"), ("Hiper Cabuloso", 1, "PT")]),
 ("04-comparacao-ranking", [("@RedSideOfficial", 2, "EN"), ("@TheInfographicsShow", 1, "EN"), ("@DataIsBeautifulOfficial", 1, "EN")]),
 ("05-timeline-ano-a-ano", [("Atlas Unfolded", 1, "EN"), ("AtlasNumbers", 1, "EN"), ("@HistoryMatters", 1, "EN"), ("ENMINUTOS", 1, "ES")]),
 ("06-guerra-top-down", [("@TheOperationsRoom", 2, "EN"), ("@KingsandGenerals", 1, "EN"), ("Two Sides of War", 1, "EN")]),
 ("07-colagem-cartoon-memoriasdepez", [("@MemoriasdePez", 2, "ES"), ("@ElRobotdePlaton", 1, "ES"), ("@CuriosaMente", 1, "ES")]),
 ("08-fern-cinematico", [("@Fern-TV", 2, "EN"), ("@NotWhatYouThink", 1, "EN"), ("@RealLifeLore", 1, "EN")]),
 ("09-desastre-fotos-cartoes", [("@FascinatingHorror", 2, "EN"), ("@ScaryInteresting", 1, "EN"), ("@PlainlyDifficult", 1, "EN")]),
 ("10-caso-medico", [("@chubbyemu", 2, "EN"), ("Cabedark", 1, "ES")]),
 ("11-terror-creepy-escuro", [("@MrNightmare", 2, "EN"), ("Chilling Scares", 1, "EN"), ("Marcos Campos", 1, "PT")]),
 ("12-espaco-cosmos", [("@astrumspace", 2, "EN"), ("@HistoryoftheUniverse", 1, "EN"), ("Oniverse", 1, "PT"), ("Costa Norte", 1, "ES")]),
 ("13-economia-graficos", [("@EconomicsExplained", 1, "EN"), ("@HowMoneyWorks", 1, "EN"), ("Los Ecomonos", 1, "ES"), ("NOTICIAS ILUSTRADAS", 1, "ES")]),
 ("14-tipografia-cinetica-filosofia", [("@PursuitofWonder", 2, "EN"), ("@Einzelganger", 1, "EN"), ("Raquel de la Morena", 1, "ES")]),
 ("15-kurzgesagt-vetor", [("@kurzgesagt", 2, "EN"), ("@RealScience", 1, "EN"), ("@MinuteEarth", 1, "EN")]),
]

queue = []
summary = {}
for folder, chans in SEL:
    d = os.path.join(DEST, folder); os.makedirs(d, exist_ok=True)
    lines = [f"# {folder} — referências (minerado 22/10/2026 via yt-dlp, views/hora = views ÷ horas desde upload; mediana = 15 últimos vídeos longos)", ""]
    best_vph = 0
    for k, n, lang in chans:
        r = find(k)
        vids = sorted([v for v in r["videos"] if v["vph"]], key=lambda v: -v["vph"])[:n]
        lines.append(f"## {r['name'] or k} [{lang}] — {r['url']}")
        lines.append(f"   mediana views (15 últimos longos): {int(r['median_views']):,} · mediana views/hora (45 d): {int(r['med_vph_45d'] or 0):,} · melhor views/hora: {int(r['best_vph']):,}".replace(",", "."))
        for v in vids:
            lines.append(f"   - {v['id']} | https://youtu.be/{v['id']} | {v['vph']:,} views/h | {v['views']:,} views | {v['hours']} h | {(v['dur'] or 0)//60} min | {v['title']}".replace(",", "."))
            queue.append((folder, v["id"], v["dur"] or 900, re.sub(r"[^a-z0-9]+", "-", (r['name'] or k).lower()).strip("-")))
            best_vph = max(best_vph, r["med_vph_45d"] or 0)
        lines.append("")
    summary[folder] = {"best_med_vph": best_vph, "canais": [(find(k)["name"] or k, lang) for k, _, lang in chans]}
    open(os.path.join(d, "REFERENCIA.txt"), "w", encoding="utf-8").write("\n".join(lines))
json.dump(summary, open(os.path.join(HERE, "summary.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
with open(os.path.join(HERE, "sheets.txt"), "w", encoding="utf-8") as f:
    for folder, vid, dur, nm in queue:
        f.write(f"{vid}\t{os.path.join(DEST, folder, f'sheet-{nm}-{vid}.jpg')}\t{int(dur)}\n")
print(len(queue), "sheets na fila")
