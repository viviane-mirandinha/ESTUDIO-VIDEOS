import json,time,urllib.request,urllib.parse,os,re
UA={"User-Agent":"ShortsTeste/1.0 (contato local)"}
def get(url):
    for k in range(4):
        try:
            return urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=30).read()
        except Exception as e:
            print(" erro",e); time.sleep(5*(k+1))
PESSOAS={"nikolas":"Nikolas Ferreira","lula":"Lula da Silva 2023 official portrait","flavio":"Flávio Bolsonaro senador","macron":"Emmanuel Macron 2022 portrait","sheinbaum":"Claudia Sheinbaum Pardo"}
cred={}
for k,q in PESSOAS.items():
    u="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","format":"json","generator":"search","gsrnamespace":6,"gsrsearch":q+" filetype:bitmap","gsrlimit":8,"prop":"imageinfo","iiprop":"url|extmetadata|size","iiurlwidth":420})
    d=json.loads(get(u)); time.sleep(1.5)
    pages=sorted((d.get("query") or {}).get("pages",{}).values(),key=lambda p:p.get("index",99))
    ok=None
    for p in pages:
        ii=p["imageinfo"][0]; md=ii.get("extmetadata",{})
        lic=md.get("LicenseShortName",{}).get("value","")
        if ii["height"]<ii["width"]*0.7: continue
        ok=(p["title"],ii["thumburl"],lic,re.sub("<[^>]+>","",md.get("Artist",{}).get("value",""))[:80]); break
    print(k,"->",ok and ok[0],ok and ok[2])
    if ok:
        open(f"img/{k}.jpg","wb").write(get(ok[1])); time.sleep(1.5)
        cred[k]={"arquivo":ok[0],"licenca":ok[2],"autor":ok[3]}
json.dump(cred,open("img/creditos.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
