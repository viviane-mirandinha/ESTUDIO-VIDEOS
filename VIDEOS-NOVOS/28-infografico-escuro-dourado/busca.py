import json,time,urllib.request,urllib.parse,sys
UA={"User-Agent":"EstudoVideos/1.0 (contato local; teste)"}
for q in sys.argv[1:]:
    u="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","format":"json","list":"search","srnamespace":6,"srsearch":q,"srlimit":10})
    for k in range(3):
        try: j=json.loads(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=30).read()); break
        except Exception as e: print("retry",e); time.sleep(20)
    print("##",q,"::"," | ".join(x["title"][5:60] for x in j["query"]["search"]))
    time.sleep(1.5)
