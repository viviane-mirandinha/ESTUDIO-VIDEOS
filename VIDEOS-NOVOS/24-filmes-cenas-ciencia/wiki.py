import json,sys,time,urllib.request,urllib.parse,os
# uso: wiki.py busca '["q1","q2"]' [N]   -> lista titulos+licenca
#      wiki.py baixa '[["key","File:Titulo.jpg"],...]'  -> baixa thumb 1280 em img/key.jpg
UA={"User-Agent":"EstilosNovosTeste/1.0 (contato local; teste video)"}
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"img")
def get(url,tries=4):
    for i in range(tries):
        try:
            r=urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=60); return r.read()
        except Exception as e:
            print("retry",e,flush=True); time.sleep(20)
    print("FALHOU",url[:90]); return None
API="https://commons.wikimedia.org/w/api.php?"
mode=sys.argv[1]; Q=json.loads(sys.argv[2]); N=int(sys.argv[3]) if len(sys.argv)>3 else 8
if mode=="busca":
    for q in Q:
        u=API+urllib.parse.urlencode({"action":"query","format":"json","generator":"search","gsrsearch":"filetype:bitmap "+q,"gsrnamespace":6,"gsrlimit":N,"prop":"imageinfo","iiprop":"extmetadata|size"})
        d=json.loads(get(u)); time.sleep(1.5)
        print("##",q)
        for p in sorted(d.get("query",{}).get("pages",{}).values(),key=lambda p:p.get("index",0)):
            ii=p["imageinfo"][0]; md=ii.get("extmetadata",{})
            print(" ",p["title"][5:],"|",md.get("LicenseShortName",{}).get("value",""),"|",ii.get("width"),"x",ii.get("height"))
else:
    cp=os.path.join(OUT,"creditos.json"); cred=json.load(open(cp,encoding="utf-8")) if os.path.exists(cp) else {}
    for it in Q:
        key,title=it[0],it[1]; W=it[2] if len(it)>2 else 1280
        u=API+urllib.parse.urlencode({"action":"query","format":"json","titles":title,"prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":W})
        d=json.loads(get(u)); time.sleep(1.5)
        p=list(d["query"]["pages"].values())[0]
        if "imageinfo" not in p: print("NAO ACHEI",title); continue
        ii=p["imageinfo"][0]; md=ii.get("extmetadata",{})
        fn=key+".jpg"
        b=get(ii.get("thumburl") or ii["url"]); time.sleep(1.5)
        if not b: continue
        open(os.path.join(OUT,fn),"wb").write(b)
        import re
        art=re.sub("<[^>]+>","",md.get("Artist",{}).get("value",""))[:80]
        cred[fn]={"title":p["title"],"artist":art,"license":md.get("LicenseShortName",{}).get("value","")}
        print(fn,"|",cred[fn]["license"],"|",art[:40],flush=True)
    json.dump(cred,open(cp,"w",encoding="utf-8"),ensure_ascii=False,indent=1)
