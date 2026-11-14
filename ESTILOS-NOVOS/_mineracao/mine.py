#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Minera canais dark/faceless por ESTILO de edicao. Saida: channels.json + report.md.
Fase 1: buscas (filtro mes) flat -> candidatos. Fase 2: por canal, flat 12 videos + full extract top 2 -> views/hora."""
import json, subprocess, sys, time, statistics, os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

OUT = os.path.dirname(os.path.abspath(__file__))
MIN_DUR = 420
NOW = datetime.now(timezone.utc).timestamp()

# estilo -> canais seed (handles)
SEEDS = {
 "whiteboard": ["@sprouts", "@AfterSkool", "@AcademiaPlay", "@BullyMagnets", "@TikTakDraw", "@DrawCuriosity"],
 "truecrime": ["@CoffeehouseCrime", "@Dreading", "@ExploreWithUs", "@TheCasualCriminalist", "@LazyMasquerade"],
 "top10": ["@Top5s", "@BeAmazed", "@ChillsYT", "@alux", "@DocTops", "@MostAmazingTop10"],
 "infographics-comparacao": ["@TheInfographicsShow", "@Ridddle", "@DataIsBeautifulOfficial", "@RedSideOfficial", "@BRIGHTSIDEOFFICIAL"],
 "timeline-historia": ["@HistoryMatters", "@EpicHistoryTV", "@KingsandGenerals", "@historiacivilis", "@Knowledgia", "@TheArmchairHistorian", "@CanalHistoryBrasil", "@ThatIsHistory"],
 "texto-cinetico-filosofia": ["@PursuitofWonder", "@Einzelganger", "@Aperture", "@TheSchoolofLifeTV", "@RefugioMental", "@Freedom_in_Thought"],
 "guerra-doc": ["@TheOperationsRoom", "@Montemayor1", "@DarkDocs", "@Yarnhub", "@SimpleHistory", "@TheIntelReport"],
 "curiosidades-personagem": ["@ZackDFilms", "@SamONellaAcademy", "@CasuallyExplained", "@MemoriasdePez", "@CuriosaMente", "@ElRobotdePlaton", "@Nerdologia"],
 "kurzgesagt": ["@kurzgesagt", "@KurzgesagtES", "@MinuteEarth", "@TEDEd", "@RealScience", "@Vsauce2"],
 "fern-cinematic-3d": ["@Fern-TV", "@neo", "@NotWhatYouThink", "@RealLifeLore", "@Wendoverproductions", "@HalfAsInteresting"],
 "magnates-negocios": ["@MagnatesMedia", "@LogicallyAnswered", "@ColdFusion", "@CompanyMan", "@ModernMBA", "@slidebean", "@JakeTran"],
 "desastre-fotos": ["@FascinatingHorror", "@PlainlyDifficult", "@ScaryInteresting", "@DisasterBreakdown", "@BrickImmortar", "@WaterlineStories"],
 "medico-caso": ["@chubbyemu", "@MedicalSecrets"],
 "3d-isometrico-engenharia": ["@KentoBento", "@MustardChannel", "@PrimalSpace", "@FoundAndExplained", "@RealEngineering", "@LesicsEN"],
 "horror-creepy": ["@MrNightmare", "@Nexpo", "@BarelySociable", "@DrossRotzank", "@Lemmino", "@Wendigoon"],
 "espaco-cinematic": ["@astrumspace", "@SEA_space", "@HistoryoftheUniverse", "@CoolWorldsLab", "@Infinito.Oficial"],
 "economia-cartoon": ["@EconomicsExplained", "@PolyMatter", "@MoneyMacro", "@Hoog", "@HowMoneyWorks"],
 "foto-arquivo-weird": ["@WeirdHistory", "@MysteryScoop", "@TodayIFoundOut", "@Voicesofthepast", "@HistoryTime", "@FallofCivilizations"],
 "mapas-geo-es-pt": ["@UnMundoInmenso", "@Terranea", "@GeografiaIrreal", "@CosasDelMundo"],
 "pixel-retro": ["@bill_wurtz", "@suibhne", "@OverSimplified", "@PrimeTimeHistory", "@extracredits"],
}

# (estilo, idioma, query)
SEARCHES = [
 ("whiteboard","pt","animação quadro branco história desenhada"),
 ("whiteboard","es","historia dibujada animada pizarra"),
 ("whiteboard","en","whiteboard animation history explained"),
 ("truecrime","pt","caso real crime documentário completo"),
 ("truecrime","es","caso real crimen documental completo"),
 ("truecrime","en","true crime documentary case solved narrated"),
 ("top10","pt","top 10 lugares mais misteriosos do mundo"),
 ("top10","es","top 10 lugares más misteriosos del mundo"),
 ("top10","en","top 10 most mysterious places caught on camera"),
 ("timeline-historia","pt","história completa linha do tempo animada"),
 ("timeline-historia","es","historia completa línea de tiempo animada"),
 ("timeline-historia","en","entire history timeline animated map"),
 ("texto-cinetico-filosofia","pt","estoicismo filosofia vídeo motivacional escuro"),
 ("texto-cinetico-filosofia","es","estoicismo filosofía video oscuro"),
 ("texto-cinetico-filosofia","en","stoic philosophy kinetic typography dark"),
 ("guerra-doc","pt","guerra documentário completo batalha animado"),
 ("guerra-doc","es","guerra documental completo batalla animado"),
 ("guerra-doc","en","battle documentary animated map ww2"),
 ("curiosidades-personagem","pt","curiosidades que você não sabia animação"),
 ("curiosidades-personagem","es","curiosidades que no sabías animación"),
 ("desastre-fotos","pt","tragédia desastre o que deu errado documentário"),
 ("desastre-fotos","es","tragedia desastre qué salió mal documental"),
 ("desastre-fotos","en","disaster documentary what went wrong"),
 ("magnates-negocios","pt","a história da empresa bilionária documentário"),
 ("magnates-negocios","es","la historia de la empresa millonaria documental"),
 ("magnates-negocios","en","rise and fall company documentary"),
 ("horror-creepy","pt","casos inexplicáveis mistério internet documentário"),
 ("horror-creepy","es","misterios sin resolver internet documental"),
 ("horror-creepy","en","internet mystery documentary unsolved"),
 ("economia-cartoon","pt","economia explicada animação por que"),
 ("economia-cartoon","es","economía explicada animación por qué"),
 ("espaco-cinematic","pt","universo espaço documentário o que existe"),
 ("espaco-cinematic","es","universo espacio documental qué hay"),
 ("pixel-retro","en","pixel art history documentary"),
 ("pixel-retro","es","historia pixel art documental"),
 ("medico-caso","pt","um homem comeu e isso aconteceu com seus órgãos"),
 ("medico-caso","es","un hombre comió y esto pasó con sus órganos"),
 ("3d-isometrico-engenharia","pt","como funciona engenharia animação 3d"),
 ("3d-isometrico-engenharia","es","cómo funciona ingeniería animación 3d"),
 ("foto-arquivo-weird","pt","como era a vida fotos antigas história"),
 ("foto-arquivo-weird","es","cómo era la vida fotos antiguas historia"),
]

def run(args, timeout=120):
    for att in range(3):
        try:
            p = subprocess.run(["yt-dlp", "--no-warnings", "--ignore-errors"] + args,
                               capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
            if "429" in (p.stderr or "") or "Too Many" in (p.stderr or ""):
                time.sleep(30 * (att + 1)); continue
            return p.stdout
        except subprocess.TimeoutExpired:
            time.sleep(5)
    return ""

def flat(url, n):
    out = run(["--flat-playlist", "--playlist-end", str(n), "-j", url])
    vids = []
    for line in out.splitlines():
        try: d = json.loads(line)
        except Exception: continue
        if d.get("_type") not in (None, "url", "video"): continue
        vids.append({"id": d.get("id"), "title": d.get("title"), "views": d.get("view_count"),
                     "dur": d.get("duration"), "channel": d.get("channel") or d.get("uploader"),
                     "channel_id": d.get("channel_id"), "channel_url": d.get("channel_url") or d.get("uploader_url"),
                     "live": d.get("live_status") in ("is_live", "was_live")})
    return vids

def full(vid):
    out = run(["-j", "--no-download", "--no-playlist", f"https://www.youtube.com/watch?v={vid}"], timeout=90)
    try: d = json.loads(out.strip().splitlines()[-1])
    except Exception: return None
    ts = d.get("timestamp") or d.get("release_timestamp")
    if not ts and d.get("upload_date"):
        ts = datetime.strptime(d["upload_date"], "%Y%m%d").replace(tzinfo=timezone.utc).timestamp()
    hours = max((NOW - ts) / 3600, 1) if ts else None
    return {"id": vid, "title": d.get("title"), "views": d.get("view_count"), "dur": d.get("duration"),
            "upload": d.get("upload_date"), "hours": round(hours, 1) if hours else None,
            "vph": round(d["view_count"] / hours, 1) if (hours and d.get("view_count")) else None,
            "subs": d.get("channel_follower_count"), "channel": d.get("channel"), "channel_id": d.get("channel_id"),
            "channel_url": d.get("channel_url"), "lang": d.get("language"), "live": d.get("live_status") in ("is_live","was_live")}

def main():
    log = open(os.path.join(OUT, "mine.log"), "a", encoding="utf-8")
    def L(s): log.write(s + "\n"); log.flush()

    # ---- Fase 1: buscas
    cands = {}  # channel_id -> {styles:set, best:int, name, url, src}
    def do_search(item):
        st, lang, q = item
        url = "https://www.youtube.com/results?search_query=" + q.replace(" ", "+") + "&sp=EgIIBA%253D%253D"
        return st, lang, q, flat(url, 20)
    with ThreadPoolExecutor(6) as ex:
        for st, lang, q, vids in ex.map(do_search, SEARCHES):
            L(f"[busca] {lang} {q}: {len(vids)}")
            for v in vids:
                if not v["channel_id"] or v["live"] or (v["dur"] or 0) < MIN_DUR or (v["views"] or 0) < 20000: continue
                c = cands.setdefault(v["channel_id"], {"styles": set(), "best": 0, "name": v["channel"], "url": v["channel_url"] or f"https://www.youtube.com/channel/{v['channel_id']}", "src": f"busca:{lang}", "lang": lang})
                c["styles"].add(st); c["best"] = max(c["best"], v["views"] or 0)
    json.dump({k: {**v, "styles": sorted(v["styles"])} for k, v in cands.items()}, open(os.path.join(OUT, "search_channels.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    L(f"[fase1] {len(cands)} canais candidatos")

    # ---- Fase 2: canais
    targets = []
    for st, hs in SEEDS.items():
        for h in hs: targets.append({"key": h, "url": f"https://www.youtube.com/{h}/videos", "styles": [st], "src": "seed", "lang": "?"})
    # top candidatos de busca por views
    for cid, c in sorted(cands.items(), key=lambda kv: -kv[1]["best"])[:70]:
        targets.append({"key": cid, "url": c["url"].rstrip("/") + "/videos", "styles": sorted(c["styles"]), "src": c["src"], "lang": c["lang"], "name": c["name"]})

    def do_channel(t):
        vids = [v for v in flat(t["url"], 12) if not v["live"]]
        longs = [v for v in vids if (v["dur"] or 0) >= MIN_DUR and v["views"]]
        if not longs: return t, vids, [], None
        med = statistics.median([v["views"] for v in longs])
        top = sorted(longs, key=lambda v: -(v["views"] or 0))[:2]
        fulls = [f for f in (full(v["id"]) for v in top) if f]
        # tambem o mais recente (views/hora "vivo")
        rec = full(longs[0]["id"]) if longs and longs[0]["id"] not in [f["id"] for f in fulls] else None
        if rec: fulls.append(rec)
        return t, vids, fulls, med

    results = []
    with ThreadPoolExecutor(5) as ex:
        futs = [ex.submit(do_channel, t) for t in targets]
        for f in as_completed(futs):
            try: t, vids, fulls, med = f.result()
            except Exception as e: L(f"[erro] {e}"); continue
            if not vids: L(f"[canal] {t['key']}: vazio"); continue
            subs = next((x["subs"] for x in fulls if x.get("subs")), None)
            name = next((x["channel"] for x in fulls if x.get("channel")), vids[0]["channel"]) or t.get("name")
            cid = next((x["channel_id"] for x in fulls if x.get("channel_id")), vids[0]["channel_id"])
            best_vph = max([x["vph"] or 0 for x in fulls] or [0])
            results.append({"key": t["key"], "name": name, "channel_id": cid, "url": f"https://www.youtube.com/channel/{cid}" if cid else t["url"],
                            "styles": t["styles"], "src": t["src"], "lang": t["lang"], "subs": subs, "median_views_12": med,
                            "best_vph": best_vph, "n_long": sum(1 for v in vids if (v["dur"] or 0) >= MIN_DUR), "videos": fulls})
            L(f"[canal] {name} subs={subs} med={med} vph={best_vph}")
            json.dump(results, open(os.path.join(OUT, "channels.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # ---- report
    results.sort(key=lambda r: -(r["best_vph"] or 0))
    with open(os.path.join(OUT, "report.md"), "w", encoding="utf-8") as f:
        f.write(f"# Mineração estilos dark — {datetime.now():%Y-%m-%d %H:%M}\n\n| canal | estilos | src | subs | mediana 12 | melhor v/h | vídeo | horas | views | dur |\n|---|---|---|---|---|---|---|---|---|---|\n")
        for r in results:
            v = max(r["videos"], key=lambda x: x["vph"] or 0) if r["videos"] else {}
            f.write(f"| [{r['name']}]({r['url']}) | {','.join(r['styles'])} | {r['src']} | {r['subs']} | {r['median_views_12']} | {r['best_vph']} | [{(v.get('title') or '')[:45]}](https://youtu.be/{v.get('id')}) | {v.get('hours')} | {v.get('views')} | {v.get('dur')} |\n")
    L("[fim]")

if __name__ == "__main__":
    main()
