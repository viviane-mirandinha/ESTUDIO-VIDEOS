import urllib.request,urllib.parse,json,os,sys
KEY=__import__("os").environ.get("KEY", "")
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"raw","cand")
UA={"User-Agent":"EstudioTeste/1.0 (contato local)"}
def get(u): return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=90).read()
IMG={"iwhale":"sperm whale","ibird":"zebra finch","ibat":"bat flying","iprim":"chimpanzee","isong":"songbird branch"}
VID={"vsperm":"sperm whale","vwhale":"whale underwater","vocean":"underwater ocean blue","vcow":"cows farm barn","velep":"elephant savanna","vdiver":"diver whale","vbirds":"birds singing"}
cred={}
for k,q in IMG.items():
    r=json.loads(get("https://pixabay.com/api/?"+urllib.parse.urlencode({"key":KEY,"q":q,"per_page":10,"safesearch":"true","orientation":"horizontal","image_type":"photo"})))
    for i,h in enumerate(r.get("hits",[])[:3]):
        open(f"{OUT}/{k}{i}.jpg","wb").write(get(h["largeImageURL"])); cred[f"{k}{i}"]=h["pageURL"]
    print(k,len(r.get("hits",[])))
for k,q in VID.items():
    r=json.loads(get("https://pixabay.com/api/videos/?"+urllib.parse.urlencode({"key":KEY,"q":q,"per_page":10,"safesearch":"true"})))
    for i,h in enumerate(r.get("hits",[])[:3]):
        v=h["videos"]; f=v.get("medium") or v.get("small")
        if not f or not f.get("url"): continue
        open(f"{OUT}/{k}{i}.mp4","wb").write(get(f["url"])); cred[f"{k}{i}"]=h["pageURL"]
    print(k,len(r.get("hits",[])))
json.dump(cred,open(os.path.join(OUT,"creditos.json"),"w"),indent=0)
