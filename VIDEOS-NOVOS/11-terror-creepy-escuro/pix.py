import json,urllib.request,urllib.parse,os,sys
from PIL import Image
KEY=__import__("os").environ.get("KEY", "")
D=os.path.join(os.path.dirname(os.path.abspath(__file__)),"img")
Q={"p_casa":"abandoned house dusk","p_lua":"full moon night clouds","p_porao":"dark basement stairs","p_floresta":"dark forest night fog"}
def get(u): return urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"estilos-novos-11/1.0"}),timeout=60).read()
cred={}
for k,q in Q.items():
    r=json.loads(get("https://pixabay.com/api/?"+urllib.parse.urlencode({"key":KEY,"q":q,"per_page":5,"safesearch":"true","orientation":"horizontal","image_type":"photo"})))
    h=r["hits"][0]; open(D+"/"+k+".tmp","wb").write(get(h["largeImageURL"]))
    im=Image.open(D+"/"+k+".tmp").convert("RGB"); w,hh=im.size; s=max(1280/w,720/hh); im=im.resize((int(w*s)+1,int(hh*s)+1))
    W,H=im.size; im.crop(((W-1280)//2,(H-720)//2,(W-1280)//2+1280,(H-720)//2+720)).save(D+"/"+k+".jpg",quality=90); os.remove(D+"/"+k+".tmp")
    cred[k]=h["pageURL"]; print(k,h["tags"][:50])
json.dump(cred,open(D+"/creditos_pixabay.json","w"),indent=1)
