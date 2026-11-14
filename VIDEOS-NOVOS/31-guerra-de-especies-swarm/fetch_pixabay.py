import urllib.request,urllib.parse,json,os,sys
KEY=__import__("os").environ.get("KEY", "")
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"raw","cand")
os.makedirs(OUT,exist_ok=True)
UA={"User-Agent":"EstudioTeste/1.0 (contato local)"}
def get(u): return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=90).read()
IMG={"ieye":"dragonfly eyes macro","iwasp":"wasp macro","idfly":"dragonfly macro","iwing":"dragonfly wings"}
VID={"vwasp":"wasp","vdfly":"dragonfly","vdflyfly":"dragonfly flying","vforest":"forest river aerial"}
cred={}
n=4
for k,q in IMG.items():
    r=json.loads(get("https://pixabay.com/api/?"+urllib.parse.urlencode({"key":KEY,"q":q,"per_page":20,"safesearch":"true","orientation":"horizontal","image_type":"photo"})))
    for i,h in enumerate(r.get("hits",[])[:n]):
        p=f"{OUT}/{k}{i}.jpg"; open(p,"wb").write(get(h["largeImageURL"])); cred[f"{k}{i}.jpg"]="Pixabay / "+h.get("user","")
    print(k,len(r.get("hits",[])))
for k,q in VID.items():
    r=json.loads(get("https://pixabay.com/api/videos/?"+urllib.parse.urlencode({"key":KEY,"q":q,"per_page":20,"safesearch":"true"})))
    c=0
    for h in r.get("hits",[]):
        v=h["videos"]; f=v.get("medium") or v.get("small")
        if not f or not f.get("url") or f.get("width",0)<=f.get("height",1): continue
        p=f"{OUT}/{k}{c}.mp4"; open(p,"wb").write(get(f["url"])); cred[f"{k}{c}.mp4"]="Pixabay / "+h.get("user","")
        c+=1
        if c>=n: break
    print(k,len(r.get("hits",[])),c)
json.dump(cred,open(os.path.join(OUT,"creditos.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
