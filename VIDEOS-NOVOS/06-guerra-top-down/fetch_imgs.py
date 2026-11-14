import json,time,urllib.request,urllib.parse,os,sys
UA={"User-Agent":"EstilosNovosTest/1.0 (contato local; video teste)"}
def get(url,binary=False):
    for k in range(5):
        try:
            r=urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=60).read()
            time.sleep(1.5); return r if binary else json.loads(r)
        except Exception as e:
            print("retry",str(e)[:60],flush=True); time.sleep(20)
Q={"ward":"USS Ward DD-139 1941","radar":"SCR-270 radar Opana","arizona":"USS Arizona burning Pearl Harbor","oklahoma":"USS Oklahoma capsized Pearl Harbor",
   "zero":"A6M2 Zero Pearl Harbor","decolagem":"Japanese aircraft carrier Shokaku Pearl Harbor take off","enterprise":"USS Enterprise CV-6 1941","kaneohe":"Kaneohe Naval Air Station December 7 1941"}
os.makedirs("raw/cand",exist_ok=True); meta={}
for k,q in Q.items():
    u="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","format":"json","generator":"search","gsrsearch":q+" filetype:bitmap","gsrnamespace":6,"gsrlimit":3,"prop":"imageinfo","iiprop":"url|size","iiurlwidth":1280})
    d=get(u); pages=sorted((d or {}).get("query",{}).get("pages",{}).values(),key=lambda p:p.get("index",9))
    for i,p in enumerate(pages):
        ii=p["imageinfo"][0]; fn=f"raw/cand/{k}_{i}.jpg"
        b=get(ii.get("thumburl",ii["url"]),True)
        if b: open(fn,"wb").write(b); meta[f"{k}_{i}"]={"title":p["title"],"url":ii["descriptionurl"]}
        print(k,i,p["title"][:70],flush=True)
json.dump(meta,open("raw/cand/meta.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
