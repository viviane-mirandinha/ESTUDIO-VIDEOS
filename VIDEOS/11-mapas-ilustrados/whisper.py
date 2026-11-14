import json,sys,numpy as np
from faster_whisper import WhisperModel
a=np.fromfile(sys.argv[1],dtype=np.float32)
m=WhisperModel("small",device="cpu",compute_type="int8",cpu_threads=2)
segs,info=m.transcribe(a,language="pt",word_timestamps=True)
w=[]
for s in segs:
    for x in s.words: w.append({"w":x.word.strip(),"s":round(x.start,2),"e":round(x.end,2)})
json.dump({"duration":info.duration,"words":w},open(sys.argv[2],"w",encoding="utf-8"),ensure_ascii=False)
print(info.duration,len(w))
