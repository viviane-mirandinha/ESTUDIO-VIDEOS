import json,time,urllib.request,urllib.parse,sys,os
UA={"User-Agent":"EstudoVideos/1.0 (contato local; teste)"}
D="img/cand"; meta={}
J=[("seawise_a","Seawise Giant Singapore 1990","Singapore, 1990"),("seawise_b","MT Jahre Viking","Jahre Viking"),("olympic_titanic_a","Olympic and Titanic","Olympic and Titanic.jpg"),
   ("great_eastern_a","SS Great Eastern painting","Great Eastern painting"),("great_eastern_b","Homeward Bound The Great Eastern MET","Homeward Bound"),("queen_elizabeth_a","Queen Elizabeth and Queen Mary in Southampton September","Southampton September")]
def get(u,b=False):
    for k in range(3):
        try:
            r=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=40).read(); return r if b else json.loads(r)
        except Exception as e: print("retry",e); time.sleep(20)
for key,q,sub in J:
    u="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","format":"json","generator":"search","gsrnamespace":6,"gsrsearch":q,"gsrlimit":8,"prop":"imageinfo","iiprop":"url|mime|size|extmetadata","iiurlwidth":1280})
    j=get(u); time.sleep(1.5)
    ps=sorted(j.get("query",{}).get("pages",{}).values(),key=lambda p:p.get("index",99))
    for p in ps:
        if sub not in p["title"]: continue
        ii=p["imageinfo"][0]; b=get(ii["thumburl"],True) or get(ii["thumburl"].replace("/1280px-","/960px-"),True); time.sleep(3)
        if not b: print("falhou",key); break
        ext=".png" if ii["thumburl"].lower().endswith(".png") else ".jpg"
        open(f"{D}/{key}{ext}","wb").write(b); em=ii.get("extmetadata",{})
        meta[key+ext]={"title":p["title"],"url":ii.get("descriptionurl"),"artist":em.get("Artist",{}).get("value","")[:120],"license":em.get("LicenseShortName",{}).get("value",""),"w":ii.get("width")}
        print(key,p["title"][:60],ii.get("width"),len(b)); break
json.dump(meta,open(f"{D}/meta3.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
