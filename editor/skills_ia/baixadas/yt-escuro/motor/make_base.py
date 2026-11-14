# make_base.py <key> : fundo escuro + gravações (RECS do plan_<key>.py) + voz -> <key>/base.mkv ; cria words_cut/edl
import sys, json, subprocess, importlib.util
key = sys.argv[1]
spec = importlib.util.spec_from_file_location("pl", f"plan_{key}.py"); pl = importlib.util.module_from_spec(spec); spec.loader.exec_module(pl)
W = json.load(open(f"{pl.WORDS}", encoding="utf-8")); T = round(W[-1]["e"] + 1.2, 2)
json.dump(W, open(f"{key}/words_cut.json", "w", encoding="utf-8"), ensure_ascii=False)
json.dump([{"src_a": 0, "src_b": T, "out_a": 0, "out_b": T}], open(f"{key}/edl.json", "w"))
recs = getattr(pl, "RECS", [])
clips = sorted({r[2] for r in recs}); idx = {c: i + 1 for i, c in enumerate(clips)}
inp = ["-f", "lavfi", "-i", f"color=c=0x0F0F0F:s=1920x1080:r=30:d={T}"]
for c in clips: inp += ["-i", f"rec/{c}.webm"]
inp += ["-t", str(T), "-i", pl.AUDIO]
f = []; uses = {c: [r for r in recs if r[2] == c] for c in clips}
for c in clips:
    n = len(uses[c]); f.append(f"[{idx[c]}:v]fps=30,scale=1920:1080,split={n}" + "".join(f"[{c}_{k}]" for k in range(n)) if n > 1 else f"[{idx[c]}:v]fps=30,scale=1920:1080[{c}_0]")
last = "0:v"; k_of = {c: 0 for c in clips}
for j, (t, d, c, ss) in enumerate(sorted(recs)):
    k = k_of[c]; k_of[c] += 1
    f.append(f"[{c}_{k}]trim={ss}:{ss + d},setpts=PTS-STARTPTS+{t}/TB[r{j}]")
    f.append(f"[{last}][r{j}]overlay=eof_action=pass[b{j}]"); last = f"b{j}"
f.append(f"[{last}]format=yuv420p[v]")
subprocess.run(["ffmpeg", "-v", "error", "-y", *inp, "-filter_complex", ";".join(f), "-map", "[v]", "-map", f"{len(clips) + 1}:a",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-c:a", "pcm_s16le", "-t", str(T), f"{key}/base.mkv"], check=True)
print(key, "base ok", T, "recs", len(recs))
