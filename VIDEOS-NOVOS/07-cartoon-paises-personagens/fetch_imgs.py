import requests,time,json,os,sys
UA={"User-Agent":"EstilosNovosTeste/1.0 (contato local; video test)"}
API="https://commons.wikimedia.org/w/api.php"
def get(url,**kw):
    for i in range(5):
        r=requests.get(url,headers=UA,timeout=60,**kw)
        if r.status_code==429: time.sleep(30+15*i); continue
        r.raise_for_status(); time.sleep(2.5); return r
    raise Exception("429")
Q=json.loads(sys.argv[1]) if len(sys.argv)>1 else {}
os.makedirs("img/cand",exist_ok=True); cred={}
for k,q in Q.items():
    r=get(API,params={"action":"query","format":"json","generator":"search","gsrsearch":q+" filetype:bitmap","gsrnamespace":6,"gsrlimit":3,"prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":1280})
    pages=sorted(r.json().get("query",{}).get("pages",{}).values(),key=lambda p:p.get("index",0))
    for n,p in enumerate(pages):
        ii=p["imageinfo"][0]; fn=f"img/cand/{k}_{n}.jpg"
        try: open(fn,"wb").write(get(ii["thumburl"]).content)
        except Exception as e: print("fail",fn); continue
        md=ii.get("extmetadata",{})
        cred[fn]={"title":p["title"],"autor":md.get("Artist",{}).get("value","")[:120],"lic":md.get("LicenseShortName",{}).get("value","")}
        print(fn,p["title"][:70])
old=json.load(open("img/cand/creditos.json",encoding="utf-8")) if os.path.exists("img/cand/creditos.json") else {}; old.update(cred); cred=old
json.dump(cred,open("img/cand/creditos.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
