import json,os,subprocess,numpy as np
os.environ["HF_HUB_OFFLINE"]="1"
from faster_whisper import WhisperModel
try: m=WhisperModel("large-v3",device="cuda",compute_type="float16")
except Exception as e: print("gpu fail",e); m=WhisperModel("small",device="cpu",compute_type="int8")
aud=np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i","voz.wav","-f","s16le","-ac","1","-ar","16000","-"],capture_output=True).stdout,np.int16).astype(np.float32)/32768
segs,_=m.transcribe(aud,language="es",word_timestamps=True,vad_filter=False,initial_prompt="La Antártida, Burj Khalifa, Bedmap, Gamburtsev, Vostok, Whillans, Erebus, Thwaites, Denman, Wilkes.")
W=[]; S=[]
for s in segs:
    S.append({"s":round(s.start,2),"e":round(s.end,2),"t":s.text.strip()})
    for w in s.words: W.append({"w":w.word.strip(),"s":round(w.start,3),"e":round(w.end,3)})
json.dump(W,open("words.json","w",encoding="utf-8"),ensure_ascii=False)
json.dump(S,open("segs.json","w",encoding="utf-8"),ensure_ascii=False,indent=0)
print("ok",len(W),len(S),W[-1]["e"])
