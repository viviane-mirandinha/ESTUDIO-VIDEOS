import json,time,urllib.request,urllib.parse,os,sys
O=os.path.dirname(os.path.abspath(__file__)); C=os.path.join(O,"cand")
UA={"User-Agent":"TesteEstilos/1.0 (contato local)"}
Q={"sp":"São Paulo skyline","campinas":"Campinas skyline","guarulhos":"Guarulhos vista aérea","sorocaba":"Sorocaba vista cidade","ribeirao":"Ribeirão Preto skyline","sjc":"São José dos Campos vista","transito":"Marginal Tietê congestionamento","bandeirantes":"Rodovia dos Bandeirantes","paulista":"Avenida Paulista noite","gx":"Guarulhos skyline","sx":"Sorocaba skyline","rx":"Ribeirão Preto vista aérea","tx":"São Paulo traffic jam","gy":"Guarulhos São Paulo","sy":"Sorocaba São Paulo cidade"}
if len(sys.argv)>1: Q={k:Q[k] for k in sys.argv[1:]}
def get(u):
    for t in range(4):
        try:
            return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=40).read()
        except Exception as e:
            print("retry",e); time.sleep(20)
cred={}
for k,q in Q.items():
    u="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","format":"json","generator":"search","gsrsearch":"filetype:bitmap "+q,"gsrnamespace":6,"gsrlimit":6,"prop":"imageinfo","iiprop":"url|size","iiurlwidth":1600})
    d=json.loads(get(u)); time.sleep(1.5)
    ps=sorted(d.get("query",{}).get("pages",{}).values(),key=lambda p:p["index"])
    n=0
    for p in ps:
        ii=p["imageinfo"][0]
        if ii["width"]<1000 or ii["width"]<ii["height"]: continue
        b=get(ii["thumburl"]); time.sleep(1.5)
        if not b: continue
        fn=f"{k}{n}.jpg"; open(os.path.join(C,fn),"wb").write(b); cred[fn]=p["title"]; n+=1
        if n>=3: break
    print(k,n)
old=json.load(open(os.path.join(C,"creditos.json"),encoding="utf-8")) if os.path.exists(os.path.join(C,"creditos.json")) else {}
old.update(cred); json.dump(old,open(os.path.join(C,"creditos.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=0)
