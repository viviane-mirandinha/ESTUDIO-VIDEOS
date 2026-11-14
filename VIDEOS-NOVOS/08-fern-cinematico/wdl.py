import urllib.request, urllib.parse, json, time, sys, os
UA={"User-Agent":"EstilosNovos08/1.0 (contato local; teste)"}
def get(u):
    for t in range(4):
        try: return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60).read()
        except Exception as e: print("retry",str(e)[:60]); time.sleep(20)
cred={}
for a in sys.argv[1:]:
    name,title=a.split("=",1)
    u="https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=imageinfo&iiprop=url|extmetadata&iiurlwidth=1280&titles="+urllib.parse.quote(title)
    d=json.loads(get(u)); time.sleep(1.5)
    p=list(d["query"]["pages"].values())[0]; ii=p["imageinfo"][0]
    open("img/"+name,"wb").write(get(ii["thumburl"])); time.sleep(1.5)
    em=ii.get("extmetadata",{}); cred[name]={"titulo":title,"url":ii["descriptionurl"],"autor":em.get("Artist",{}).get("value","")[:120],"licenca":em.get("LicenseShortName",{}).get("value","")}
    print("ok",name)
json.dump(cred,open("img/creditos.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
