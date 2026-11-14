import json,sys,time,urllib.request,urllib.parse,os
UA={"User-Agent":"EstilosNovosTeste/1.0 (contato local; teste video)"}
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"img")
def get(url,tries=3):
    for i in range(tries):
        try:
            r=urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=60); return r.read()
        except Exception as e:
            print("retry",e); time.sleep(20)
    print("FALHOU",url[:90]); return None
Q=json.loads(sys.argv[1]); N=int(sys.argv[2]) if len(sys.argv)>2 else 2
cred={}
cp=os.path.join(OUT,"creditos.json")
if os.path.exists(cp): cred=json.load(open(cp,encoding="utf-8"))
for key,q in Q:
    u="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","format":"json","generator":"search","gsrsearch":"filetype:bitmap "+q,"gsrnamespace":6,"gsrlimit":N,"prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":1280})
    d=json.loads(get(u)); time.sleep(1.5)
    pages=sorted(d.get("query",{}).get("pages",{}).values(),key=lambda p:p.get("index",0))
    for k,p in enumerate(pages):
        ii=p["imageinfo"][0]; tu=ii.get("thumburl") or ii["url"]
        fn=f"{key}_{k}.jpg"
        if not os.path.exists(os.path.join(OUT,fn)):
            b=get(tu); time.sleep(1.5)
            if not b: continue
            open(os.path.join(OUT,fn),"wb").write(b)
        md=ii.get("extmetadata",{})
        cred[fn]={"title":p["title"],"artist":md.get("Artist",{}).get("value","")[:120],"license":md.get("LicenseShortName",{}).get("value","")}
        print(fn,"|",p["title"][:80],"|",cred[fn]["license"],flush=True)
        json.dump(cred,open(cp,"w",encoding="utf-8"),ensure_ascii=False,indent=1)
json.dump(cred,open(cp,"w",encoding="utf-8"),ensure_ascii=False,indent=1)
