import json
w=json.load(open("words.json",encoding="utf-8"))
out=[]
i=0
while i<len(w):
    x=w[i]
    if x["w"].lower()=="dar" and i+1<len(w) and w[i+1]["w"].lower().startswith("que"):
        out.append({"w":"dark"+w[i+1]["w"][3:],"s":x["s"],"e":w[i+1]["e"]}); i+=2; continue
    if x["w"].lower()=="a" and i+1<len(w) and w[i+1]["w"].lower().startswith("reten") and x["s"]>36:
        i+=1; continue
    if x["w"].lower().startswith("reten") and x["s"]>36: x=dict(x,w="RETENÇÃO")
    out.append(x); i+=1
DUR=42.5
h=open("template.html",encoding="utf-8").read().replace("__DUR__",str(DUR)).replace("__WORDS__",json.dumps(out,ensure_ascii=False))
open("hf/index.html","w",encoding="utf-8").write(h)
print(len(out)," ".join(o["w"] for o in out)[-120:])
