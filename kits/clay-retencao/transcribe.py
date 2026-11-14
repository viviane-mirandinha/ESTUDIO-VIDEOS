import json,sys
from faster_whisper import WhisperModel
m=WhisperModel("medium",device="cpu",compute_type="int8")
import subprocess,numpy as np
raw=subprocess.run(["ffmpeg","-v","error","-i",sys.argv[1],"-ac","1","-ar","16000","-f","f32le","-"],capture_output=True).stdout
aud=np.frombuffer(raw,np.float32)
segs,_=m.transcribe(aud,language="pt",word_timestamps=True)
w=[]
for s in segs:
    for x in s.words: w.append({"w":x.word.strip(),"s":round(x.start,3),"e":round(x.end,3)})
json.dump(w,open("words.json","w",encoding="utf-8"),ensure_ascii=False,indent=0)
print(len(w)); print(" ".join(x["w"] for x in w))
