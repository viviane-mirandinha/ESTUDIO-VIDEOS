import json,sys
from faster_whisper import WhisperModel
m=WhisperModel("small",device="cpu",compute_type="int8",cpu_threads=2)
segs,_=m.transcribe(__import__("numpy").fromfile("a.raw",dtype="int16").astype("float32")/32768,language="pt",word_timestamps=True)
out=[]
for s in segs:
    for w in s.words: out.append({"w":w.word.strip(),"s":round(w.start,2),"e":round(w.end,2)})
json.dump(out,open("words.json","w",encoding="utf-8"),ensure_ascii=False)
print(len(out),out[-1])
