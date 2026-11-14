import sys, json, os, importlib.util
spec = importlib.util.spec_from_file_location("lw", __import__("os").path.expanduser(r"~\.claude\skills\watch\scripts\local_whisper.py"))
lw = importlib.util.module_from_spec(spec); spec.loader.exec_module(lw); lw._register_cuda_dlls()
from faster_whisper import WhisperModel
wav, out, prompt = sys.argv[1], sys.argv[2], (open(sys.argv[3], encoding="utf-8").read()[:900] if len(sys.argv) > 3 else None)
m = WhisperModel("large-v3", device="cuda", compute_type="float16")
segs, _ = m.transcribe(wav, language="pt", word_timestamps=True, initial_prompt=prompt, vad_filter=False)
W = [{"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3)} for s in segs for w in s.words]
json.dump(W, open(out, "w", encoding="utf-8"), ensure_ascii=False); print(len(W))
