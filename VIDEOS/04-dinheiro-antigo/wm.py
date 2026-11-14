import json,sys,urllib.request,urllib.parse
q=sys.argv[1]
u="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","format":"json","generator":"search","gsrnamespace":6,"gsrsearch":q+" filetype:bitmap","gsrlimit":8,"prop":"imageinfo","iiprop":"url|size","iiurlwidth":1400})
r=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"DarkStyleTest/0.1 (personal research; python-urllib)"})))
for p in r.get("query",{}).get("pages",{}).values():
    ii=p["imageinfo"][0]; print(ii["width"],ii["height"],p["title"][5:80],"|",ii.get("thumburl"))
