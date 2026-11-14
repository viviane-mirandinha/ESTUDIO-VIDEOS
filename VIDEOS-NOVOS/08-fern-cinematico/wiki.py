import urllib.request, urllib.parse, json, time, sys
UA={"User-Agent":"EstilosNovos08/1.0 (contato local; teste)"}
def get(u):
    for t in range(4):
        try: return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60).read()
        except Exception as e:
            print("retry",str(e)[:60]); time.sleep(20)
for q in sys.argv[1:]:
    u="https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrnamespace=6&gsrlimit=6&gsrsearch="+urllib.parse.quote(q)+"&prop=imageinfo&iiprop=url|size"
    d=json.loads(get(u)); time.sleep(1.5)
    for p in (d.get("query",{}).get("pages",{}) or {}).values():
        ii=p["imageinfo"][0]; print(q,"|",p["title"],ii["width"],ii["height"])
