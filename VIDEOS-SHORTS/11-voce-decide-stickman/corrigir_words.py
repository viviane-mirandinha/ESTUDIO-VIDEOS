# corrige erros do whisper (piso "range", "Comenta A pra ... B pra")
import json,os
D=os.path.dirname(os.path.abspath(__file__));f=os.path.join(D,"words.json")
W=json.load(open(f,encoding="utf-8"));o=[]
i=0
while i<len(W):
    w=W[i]
    if w["w"].lower().startswith("rende"): w["w"]="range."
    if w["w"]=="Comenta" and i+1<len(W) and W[i+1]["w"].lower()=="para":
        p=W[i+1];m=round(p["s"]+0.12,2)
        o+= [w,{"w":"A","s":p["s"],"e":m},{"w":"pra","s":m,"e":p["e"]}];i+=2;continue
    if w["w"].lower().startswith("d") and len(w["w"])<=3 and i+1<len(W) and W[i+1]["w"].lower()=="para" and W[i-1]["w"].startswith("acender"):
        p=W[i+1];o+=[{"w":"B","s":w["s"],"e":w["e"]},{"w":"pra","s":p["s"],"e":p["e"]}];i+=2;continue
    o.append(w);i+=1
json.dump(o,open(f,"w",encoding="utf-8"),ensure_ascii=False)
print(" ".join(x["w"] for x in o[118:]))
