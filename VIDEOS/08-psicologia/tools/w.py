import json,sys
from faster_whisper import WhisperModel
m=WhisperModel("small",device="cpu",compute_type="int8")
segs,info=m.transcribe(sys.argv[1],language="pt",word_timestamps=True)
out=[]
for s in segs:
    for w in s.words: out.append({"w":w.word.strip(),"s":round(w.start,2),"e":round(w.end,2)})
json.dump(out,open(sys.argv[2],"w",encoding="utf-8"),ensure_ascii=False)
print(len(out),info.duration)
