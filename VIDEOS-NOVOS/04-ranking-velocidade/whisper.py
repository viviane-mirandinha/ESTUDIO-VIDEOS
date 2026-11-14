import json,sys,wave,numpy as np
from faster_whisper import WhisperModel
wf=wave.open(sys.argv[1]);a=np.frombuffer(wf.readframes(wf.getnframes()),np.int16).astype(np.float32)/32768
m=WhisperModel(sys.argv[3] if len(sys.argv)>3 else "small",device="cpu",compute_type="int8",cpu_threads=4)
segs,info=m.transcribe(a,language="pt",word_timestamps=True)
w=[]
for s in segs:
    for x in s.words: w.append({"w":x.word.strip(),"s":round(x.start,2),"e":round(x.end,2)})
json.dump({"duration":len(a)/16000,"words":w},open(sys.argv[2],"w",encoding="utf-8"),ensure_ascii=False)
print(len(a)/16000,len(w))
