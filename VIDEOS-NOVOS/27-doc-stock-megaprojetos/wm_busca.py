import json,urllib.request,urllib.parse,sys,time,os
UA={"User-Agent":"estilos-novos-27/1.0 (contato.local)"}
def get(u):
    for i in range(4):
        try: return json.loads(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60).read())
        except Exception as e: print("retry",str(e)[:60]); time.sleep(20)
out={}
for q in sys.argv[1:]:
    u="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","format":"json","generator":"search","gsrsearch":q+" filetype:bitmap","gsrnamespace":6,"gsrlimit":8,"prop":"imageinfo","iiprop":"url|extmetadata|size","iiurlwidth":1280})
    r=get(u); time.sleep(1.5); print("##",q)
    for p in (r or {}).get("query",{}).get("pages",{}).values():
        ii=p["imageinfo"][0]; lic=ii.get("extmetadata",{}).get("LicenseShortName",{}).get("value","?")
        out[p["title"]]={"thumb":ii.get("thumburl"),"page":ii["descriptionurl"],"lic":lic,"w":ii["width"]}
        print(" ",p["title"][5:70],"|",lic,"|",ii["width"])
json.dump(out,open("raw/wm.json","a",encoding="utf-8"),ensure_ascii=False); open("raw/wm.json","a").write("\n")
