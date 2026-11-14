import json,time,urllib.request,urllib.parse,os,sys
UA={"User-Agent":"EstudoVideos/1.0 (contato local; teste)"}
Q={"great_eastern":"Great Eastern steamship","celtic":"RMS Celtic 1901 White Star","lusitania":"RMS Lusitania","olympic_titanic":"Olympic Titanic Belfast","imperator":"SS Imperator 1913","vaterland":"SS Vaterland 1914","normandie":"SS Normandie","queen_mary":"RMS Queen Mary 1936","queen_elizabeth":"RMS Queen Elizabeth liner","seawise":"Knock Nevis tanker","icon":"Icon of the Seas","pioneering":"Pioneering Spirit vessel"}
D=os.path.join(os.path.dirname(os.path.abspath(__file__)),"img","cand")
def get(url,bin=False):
    for k in range(4):
        try:
            r=urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=40).read()
            return r if bin else json.loads(r)
        except Exception as e:
            print("retry",e); time.sleep(20)
meta={}
for k,q in Q.items():
    u="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","format":"json","generator":"search","gsrnamespace":6,"gsrsearch":q+" filetype:bitmap","gsrlimit":12,"prop":"imageinfo","iiprop":"url|mime|size|extmetadata","iiurlwidth":1280})
    j=get(u); time.sleep(1.5)
    ps=sorted((j or {}).get("query",{}).get("pages",{}).values(),key=lambda p:p.get("index",99))
    n=0
    for p in ps:
        ii=p.get("imageinfo",[{}])[0]
        if ii.get("mime")!="image/jpeg" or ii.get("width",0)<900: continue
        b=get(ii["thumburl"],True); time.sleep(1.5)
        if not b or len(b)<30000: continue
        fn=f"{k}_{n}.jpg"; open(os.path.join(D,fn),"wb").write(b)
        em=ii.get("extmetadata",{})
        meta[fn]={"title":p["title"],"url":ii.get("descriptionurl"),"artist":em.get("Artist",{}).get("value","")[:120],"license":em.get("LicenseShortName",{}).get("value","")}
        n+=1
        if n>=4: break
    print(k,n)
json.dump(meta,open(os.path.join(D,"meta.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
