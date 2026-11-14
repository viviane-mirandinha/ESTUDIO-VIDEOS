import json,urllib.request,urllib.parse,sys,os
KEY=open(os.path.join(os.path.dirname(__file__),"raw",".pixkey")).read().strip()
def get(u): return urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"estilos-novos-23/1.0"}),timeout=60).read()
out={}
for q in sys.argv[1:]:
    r=json.loads(get("https://pixabay.com/api/videos/?"+urllib.parse.urlencode({"key":KEY,"q":q,"per_page":8,"safesearch":"true"})))
    out[q]=[{"id":h["id"],"tags":h["tags"],"dur":h["duration"],"url":h["videos"]["medium"]["url"],"w":h["videos"]["medium"]["width"],"page":h["pageURL"]} for h in r["hits"]]
    print("##",q,r["totalHits"]); [print(" ",x["id"],x["dur"],x["w"],x["tags"][:60]) for x in out[q]]
json.dump(out,open(os.path.join(os.path.dirname(__file__),"raw","busca.json"),"a"),ensure_ascii=False)
