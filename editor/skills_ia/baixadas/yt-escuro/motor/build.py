# build.py <key>  -> resolve plan_<key>.py (ancoras por frase) no tempo cortado; escreve ov/plan_<key>.js e <key>/timeline.json
import sys, json, re, os, unicodedata, importlib.util
key = sys.argv[1]
SRC = key  # rs2 usa base/words/edl de rs/
os.makedirs(key, exist_ok=True)
spec = importlib.util.spec_from_file_location("pl", f"plan_{key}.py"); pl = importlib.util.module_from_spec(spec); spec.loader.exec_module(pl)
words = json.load(open(f"{SRC}/words_cut.json", encoding="utf-8"))
edl = json.load(open(f"{SRC}/edl.json"))
total = edl[-1]["out_b"]
norm = lambda s: re.sub(r"[^a-z0-9 ]", "", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode())
W = [norm(w["w"]) for w in words]
def find(phrase, after):
    toks = norm(phrase).split()
    for i in range(len(W) - len(toks) + 1):
        if words[i]["s"] < after: continue
        if all(W[i + j] == toks[j] for j in range(len(toks))): return words[i]["s"]
    return None
GAP, MAXD, MIND = getattr(pl, "GAP", .1), getattr(pl, "MAXD", 99), getattr(pl, "MIND", .8)
cur, items, errs = 0.0, [], []
for it in pl.PLAN:
    if "t" in it: t = it["t"]
    else:
        t = find(it["at"], cur - 0.01)
        if t is None: t = find(it["at"], 0); print("FORA DE ORDEM:", it["at"]) if t is not None else None
        if t is None: errs.append(it["at"]); continue
    t = max(0, t + it.get("off", 0))
    cur = t
    p = {("from" if k == "from_" else k): v for k, v in it.get("p", {}).items()}
    d = it.get("dur")
    items.append({**it, "p": p, "dur": d * getattr(pl, "DUR_MULT", 1) if d else None, "start": round(t * 30) / 30})
items.sort(key=lambda x: x["start"])
for a, b in zip(items, items[1:] + [None]):
    nxt = b["start"] if b else total
    if a["dur"] is None: a["dur"] = min(MAXD, nxt - a["start"] - GAP)
    if a["start"] + a["dur"] > nxt - GAP: a["dur"] = nxt - a["start"] - GAP
    if a["dur"] < MIND: a["dur"] = max(.8, min(MIND, nxt - a["start"] - .1))
    a["dur"] = round(a["dur"] * 30) / 30
for it in items:
    it["dur"] = round(min(it["dur"], total - it["start"]) * 30) / 30
    if it["p"].get("words") is True:  # etiquetas sincronizadas com a fala (tempo relativo)
        it["p"]["words"] = [{"w": w["w"], "s": round(w["s"] - it["start"], 3)} for w in words if it["start"] <= w["s"] < it["start"] + it["dur"] - .2]
if errs: print("NAO ACHOU:", errs)
FULLT = {"yt_bars", "yt_steps", "yt_text", "yt_list", "yt_card", "yt_vs", "yt_grid", "yt_title", "yt_keys", "px_title", "kn_type", "hd_write", "mq_tela", "bh_grid", "cl_cut", "fv_pop", "la_draw", "sw_title", "pc_board", "lq_blob", "mo_chain", "kc_words", "kc_panel", "mf_essay", "er_head", "eb_tags", "mp_frame", "px_steps", "sm_scene"}
isfull = lambda i: bool(i["p"].get("full") or i["p"].get("bg") or i["p"].get("cam")) or i["type"] in FULLT or (i["type"] == "mq_card" and i["p"].get("style") in ("simples", "lime-split", "papel-split"))
js = "PLAN=" + json.dumps([{"type": i["type"], "dur": i["dur"], "p": i.get("p", {})} for i in items], ensure_ascii=False) + ";"
open(f"ov/plan_{key}.js", "w", encoding="utf-8").write(js)
json.dump([{"start": i["start"], "dur": i["dur"], "type": i["type"], "full": isfull(i), "cam": i["p"].get("cam"), "sfx": i.get("sfx", "whoosh")} for i in items], open(f"{key}/timeline.json", "w"), indent=0)
cov = sum(i["dur"] for i in items); fullc = sum(i["dur"] for i in items if isfull(i))
print(key, "inserts", len(items), "total", round(total, 1), "cobertura", round(cov, 1), f"{cov / total:.1%}", "tela cheia", f"{fullc / total:.1%}")
gaps = [(round(a["start"] + a["dur"], 1), round(b["start"] - a["start"] - a["dur"], 1)) for a, b in zip(items, items[1:]) if b["start"] - a["start"] - a["dur"] > 3]
if items[0]["start"] > 3: gaps.insert(0, (0, items[0]["start"]))
if total - items[-1]["start"] - items[-1]["dur"] > 3: gaps.append((round(items[-1]["start"] + items[-1]["dur"], 1), round(total - items[-1]["start"] - items[-1]["dur"], 1)))
if gaps: print("LACUNAS >3s:", gaps)
short = [(round(i["start"], 1), i["type"], i["dur"]) for i in items if i["dur"] < 2.2]
if short: print("CURTAS:", short)
