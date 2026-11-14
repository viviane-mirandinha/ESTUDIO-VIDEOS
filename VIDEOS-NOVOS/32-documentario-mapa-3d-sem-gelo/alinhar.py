# alinha o roteiro (texto exato) com words.json do Whisper -> tempo de cada palavra do roteiro
import json,re,difflib,unicodedata
R=str(__import__("pathlib").Path(__file__).resolve().parents[2] / "ROTEIROS-NOVOS" / "32 - ASI SE VE LA ANTARTIDA SIN HIELO.txt")
def norm(w): w=unicodedata.normalize("NFD",w.lower()); w="".join(c for c in w if unicodedata.category(c)!="Mn"); return re.sub(r"[^a-z0-9]","",w)
txt=open(R,encoding="utf-8").read()
sw=txt.split(); W=json.load(open("words.json",encoding="utf-8"))
a=[norm(x) for x in sw]; b=[norm(x["w"]) for x in W]
sm=difflib.SequenceMatcher(None,a,b,autojunk=False); T=[None]*len(sw)
for blk in sm.get_matching_blocks():
    for k in range(blk.size): T[blk.a+k]=(W[blk.b+k]["s"],W[blk.b+k]["e"])
# interpola buracos
last=0.0
for i in range(len(T)):
    if T[i] is None:
        j=i
        while j<len(T) and T[j] is None: j+=1
        nxt=T[j][0] if j<len(T) else W[-1]["e"]
        T[i]=(last,last)
        if j<len(T): T[i]=(last+(nxt-last)*(1/(j-i+1)),)*2
    last=T[i][1]
json.dump({"words":sw,"t":T},open("roteiro_tempos.json","w",encoding="utf-8"),ensure_ascii=False)
print("casadas",sum(b.size for b in sm.get_matching_blocks()),"de",len(sw))
