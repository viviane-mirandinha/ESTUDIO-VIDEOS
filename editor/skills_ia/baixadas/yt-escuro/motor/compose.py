# compose.py <key> <saida.mp4>  -> trilha de overlays + legenda + SFX + loudnorm
import sys, json, os, subprocess, re
key, OUT = sys.argv[1], sys.argv[2]
FPS = 30
SRC = key
tl = json.load(open(f"{key}/timeline.json"))
edl = json.load(open(f"{SRC}/edl.json")); total = edl[-1]["out_b"]
words = json.load(open(f"{SRC}/words_cut.json", encoding="utf-8"))
CFG = {
 "a00": dict(font="Montserrat Black", size=84, hl="&H003FD2FF", base="&H00FFFFFF", upper=True, italic=1, outline=6, mv=60, pip=[(24.9,35.3,"528:297:1376:62","TR"),(35.5,999,"540:302:2:2","TL")]),
 "rs": dict(font="Figtree ExtraBold", size=72, hl="&H003D8AFF", base="&H00F6F1EA", upper=False, italic=0, outline=5, mv=55, pip=None),
 "a1": dict(font="Figtree ExtraBold", size=72, hl="&H003FD2FF", base="&H00F6F1EA", upper=False, italic=0, outline=5, mv=55, pip=None, hidefull=True, music=True),
 "a2": dict(font="Figtree ExtraBold", size=72, hl="&H003FD2FF", base="&H00F6F1EA", upper=False, italic=0, outline=5, mv=55, pip=None, hidefull=True, music=True),
 "a3": dict(font="Figtree ExtraBold", size=72, hl="&H003FD2FF", base="&H00F6F1EA", upper=False, italic=0, outline=5, mv=55, pip=None, hidefull=True, music=True),
 "a1s": dict(font="Figtree ExtraBold", size=72, hl="&H003FD2FF", base="&H00F6F1EA", upper=False, italic=0, outline=5, mv=55, pip=None, hidefull=True, music=True),
 "rs2": dict(font="Figtree ExtraBold", size=72, hl="&H003D8AFF", base="&H00F6F1EA", upper=False, italic=0, outline=5, mv=55, pip=None, hidefull=True, music=True),
}[key]
run = lambda a: subprocess.run(a, check=True)
os.makedirs(f"{key}/gap", exist_ok=True)
# 1) trilha de overlays (qtrle argb) = lacunas transparentes + inserts
def gap(n):
    fn = f"{key}/gap/g{n}.mov"
    if not os.path.exists(fn):
        run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c=black@0.0:s=1920x1080:r={FPS},format=argb", "-frames:v", str(n), "-c:v", "qtrle", "-pix_fmt", "argb", fn])
    return os.path.basename(fn)
lines, f = [], 0
NT = round(total * FPS)
for i, it in enumerate(tl):
    s = round(it["start"] * FPS); n = round(it["dur"] * FPS)
    if s > f: lines.append("file 'gap/" + gap(s - f) + "'")
    if s < f: raise SystemExit(f"sobreposicao em {i}")
    lines.append(f"file 'ins/ins_{i:03d}.mov'"); f = s + n
if NT > f: lines.append("file 'gap/" + gap(NT - f) + "'")
open(f"{key}/track.txt", "w").write("\n".join(lines))
run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{key}/track.txt", "-c", "copy", f"{key}/track.mov"])
# 2) legenda ASS karaokê (palavra atual destacada)
def ts(t):
    t = max(0, t); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"
chunks, cur = [], []
for w in words:
    tx = w["w"].strip()
    if not tx: continue
    if tx.startswith("-") and cur: cur[-1]["w"] += tx; cur[-1]["e"] = w["e"]; continue
    if cur and (len(cur) >= 3 or w["s"] - cur[-1]["e"] > 0.35 or len(" ".join(x["w"] for x in cur) + tx) > 20 or re.search(r"[.?!,]$", cur[-1]["w"])):
        chunks.append(cur); cur = []
    cur.append({**w, "w": tx})
if cur: chunks.append(cur)
full = [(i["start"], i["start"] + i["dur"]) for i in tl if i["full"]]
C = CFG
ev = []
for ci, ch in enumerate(chunks):
    end_ch = ch[-1]["e"]
    if ci + 1 < len(chunks) and chunks[ci + 1][0]["s"] - end_ch < 0.4: end_ch = chunks[ci + 1][0]["s"]
    for wi, w in enumerate(ch):
        a = w["s"]; b = ch[wi + 1]["s"] if wi + 1 < len(ch) else end_ch
        if b - a < 0.02: continue
        def fmt(x):
            s = re.sub(r"[.,!?;:…]+$", "", x["w"]) ; return s.upper() if C["upper"] else s.lower()
        parts = []
        for k, x in enumerate(ch):
            col = C["hl"] if k == wi else C["base"]
            sc = "\\fscx108\\fscy108" if k == wi else "\\fscx100\\fscy100"
            parts.append("{\\c" + col + sc + "}" + fmt(x))
        pop = "{\\t(0,80,\\fscx100\\fscy100)}" if wi == 0 else ""
        segs_ = [(a, b)]
        if C.get("hidefull"):
            for fa, fb in full:
                segs_ = [q for (x, y) in segs_ for q in ([(x, y)] if fb <= x or fa >= y else [(x, fa), (fb, y)]) if q[1] - q[0] > .12]
        for (x, y) in segs_: ev.append(f"Dialogue: 0,{ts(x)},{ts(y)},Cap,,0,0,0,,{pop}" + " ".join(parts))
ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{C['font']},{C['size']},{C['base']},&H000000FF,&H00000000,&H96000000,0,{C['italic']},0,0,100,100,1,0,1,{C['outline']},3,2,80,80,{C['mv']},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(ev) + "\n"
open(f"{key}/caps.ass", "w", encoding="utf-8").write(ass)
# 3) SFX
SFX = {"whoosh": ("whoosh", .10, .16), "impact": ("impact", .32, 0), "coin": ("coin", .20, 0), "blip": ("blip", .30, 0), "paper": ("paper", .22, .08), "stamp": ("stamp", .45, -0.05), "pop": ("pop", .35, 0), "ding": ("ding", .16, 0)}
ins, flt = [], []
ev_ = [(i, *SFX.get(it.get("sfx", "whoosh"), SFX["whoosh"]), it) for i, it in enumerate(tl)]
names = sorted({e[1] for e in ev_}); cnt = {n: sum(1 for e in ev_ if e[1] == n) for n in names}; used = {n: 0 for n in names}
for k, n in enumerate(names):
    ins += ["-i", f"sfx/{n}.wav"]; flt.append(f"[{k}:a]aresample=48000,asplit={cnt[n]}" + "".join(f"[{n}{j}]" for j in range(cnt[n])) if cnt[n] > 1 else f"[{k}:a]aresample=48000[{n}0]")
for i, nm, vol, lead, it in ev_:
    at = max(0, it["start"] - lead + (0.05 if nm == "stamp" else 0)); j = used[nm]; used[nm] += 1
    flt.append(f"[{nm}{j}]volume={vol},adelay={int(at*1000)}:all=1[s{i}]")
flt.append("".join(f"[s{i}]" for i in range(len(tl))) + f"amix=inputs={len(tl)}:normalize=0,apad=whole_dur={total:.3f}[o]")
run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(flt), "-map", "[o]", "-t", f"{total:.3f}", f"{key}/sfx.wav"])
# 4) final
vf = "[0:v]setpts=PTS-STARTPTS[b0];"
camL = [(i["start"], i["start"] + i["dur"]) for i in tl if i.get("cam") == "L"]
camR = [(i["start"], i["start"] + i["dur"]) for i in tl if i.get("cam") == "R"]
if camL or camR:
    en = lambda iv: "+".join(f"between(t,{a:.3f},{b - 0.001:.3f})" for a, b in iv) or "0"
    vf += "[b0]split=2[bm][bc];[bc]crop=810:1080:455:0,scale=600:800:flags=lanczos,split=2[cl][cr];"
    vf += f"[bm][cl]overlay=90:140:enable='{en(camL)}'[bl];[bl][cr]overlay=1230:140:enable='{en(camR)}'[b0];"
def s2o(t):
    for e in edl:
        if e["src_a"] <= t < e["src_b"]: return e["out_a"] + t - e["src_a"]
        if t < e["src_a"]: return e["out_a"]
    return total
if C["pip"]:
    n = len(C["pip"]); vf += f"[b0]split={n+1}" + "".join(f"[p{k}]" for k in range(n+1)) + ";"
    last = "p0"
    for k, (a, b, cr, pos) in enumerate(C["pip"]):
        oa, ob = s2o(a), s2o(b); x = 22 if pos == "TL" else 1920 - 720 - 22
        vf += f"[p{k+1}]crop={cr.replace(':',':',3)},scale=720:404:flags=lanczos,drawbox=x=0:y=0:w=iw:h=ih:color=0xFF2E93:t=7[q{k}];[{last}][q{k}]overlay={x}:22:enable='between(t,{oa:.3f},{ob:.3f})'[m{k}];"
        last = f"m{k}"
    vf += f"[{last}]null[b0];"
vf += "[b0][1:v]overlay=0:0:format=auto[v1];[v1]subtitles=" + f"{key}/caps.ass:fontsdir=ov/fonts".replace(":", "\\:", 0) + ",format=yuv420p[v]"
af = "[0:a]aresample=48000[va];[2:a]aresample=48000[sa];[va][sa]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-16:TP=-1.5:LRA=11[a]"
extra = []
if C.get("music"):
    MD = "kits/CURSOS-MENTORIAS/MENTORIA CANAL DARK/MUSICAS SEM DIREITOS-20260118T055900Z-1-001/MUSICAS SEM DIREITOS/"
    TR = ["New Day - Patrick Patrikios.mp3", "Blue Dream - Cheel.mp3", "Know Myself - Patrick Patrikios.mp3", "Like That - Anno Domini Beats.mp3", "Better - Anno Domini Beats.mp3", "Love Aside - Patrick Patrikios.mp3", "Blind Memories - Cheel.mp3", "Oh My - Patrick Patrikios.mp3", "Bella Bella Beat - Nana Kwabena.mp3", "Positive Fuse - French Fuse.mp3"]
    mw = f"{key}/music.wav"
    if not os.path.exists(mw):
        mi, mf = [], []
        for k, f in enumerate(TR):
            mi += ["-i", MD + f]; mf.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo,loudnorm=I=-16:TP=-2:LRA=9[t{k}]")
        lab = "t0"
        for k in range(1, len(TR)):
            mf.append(f"[{lab}][t{k}]acrossfade=d=4:c1=tri:c2=tri[x{k}]"); lab = f"x{k}"
        mf.append(f"[{lab}]atrim=0:{total:.3f},afade=t=in:d=2,afade=t=out:st={total - 5:.3f}:d=5[m]")
        run(["ffmpeg", "-v", "error", "-y", *mi, "-filter_complex", ";".join(mf), "-map", "[m]", "-ar", "48000", mw])
    extra = ["-i", mw]
    # voz manda: música ~22 dB abaixo e com ducking pela própria voz (sobe um pouco nos respiros)
    af = ("[0:a]aresample=48000,asplit=2[va][vk];[2:a]aresample=48000[sa];"
          "[3:a]volume=-16.5dB[mb];[mb][vk]sidechaincompress=threshold=0.02:ratio=3:attack=15:release=450:makeup=1[mu];"
          "[va][sa][mu]amix=inputs=3:normalize=0:duration=first,loudnorm=I=-16:TP=-1.5:LRA=11[a]")
run(["ffmpeg", "-v", "error", "-stats", "-y", "-i", f"{SRC}/base.mkv", "-i", f"{key}/track.mov", "-i", f"{key}/sfx.wav", *extra, "-filter_complex", vf + ";" + af,
     "-map", "[v]", "-map", "[a]", "-r", "30", "-c:v", "h264_nvenc", "-preset", "p6", "-rc", "vbr", "-cq", "20", "-b:v", "8M", "-maxrate", "14M", "-bufsize", "20M", "-profile:v", "high",
     "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUT])
print("ok", OUT)
