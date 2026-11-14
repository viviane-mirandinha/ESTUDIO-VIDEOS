import json,urllib.request,urllib.parse,os,time
from PIL import Image
KEY=__import__("os").environ.get("KEY", "")
D=os.path.join(os.path.dirname(os.path.abspath(__file__)),"img")
Q={"cidade":"city night bokeh","homeoffice":"home office laptop couch","digitando":"typing laptop night","mouse":"computer mouse hand office"}
def get(u): return urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"estilos-novos-18/1.0"}),timeout=60).read()
cred={}
for k,q in Q.items():
    r=json.loads(get("https://pixabay.com/api/?"+urllib.parse.urlencode({"key":KEY,"q":q,"per_page":6,"safesearch":"true","orientation":"horizontal","image_type":"photo"})))
    for i,h in enumerate(r["hits"][:3]):
        open(D+"/t.tmp","wb").write(get(h["largeImageURL"]))
        im=Image.open(D+"/t.tmp").convert("RGB"); w,hh=im.size; s=max(1280/w,720/hh); im=im.resize((int(w*s)+1,int(hh*s)+1))
        W,H=im.size; im.crop(((W-1280)//2,(H-720)//2,(W-1280)//2+1280,(H-720)//2+720)).save(f"{D}/{k}{i}.jpg",quality=88)
        cred[f"{k}{i}"]=h["pageURL"]
    print(k,len(r["hits"]))
os.remove(D+"/t.tmp")
json.dump(cred,open(D+"/creditos_pixabay.json","w"),indent=1)
