import json,sys,os,time,urllib.request,urllib.parse
KEY=sys.argv[1]; O=os.path.dirname(os.path.abspath(__file__))
UA={"User-Agent":"estudio-teste/1.0"}
def get(u):
    return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=30))
def dl(u,p):
    if os.path.exists(p): return
    open(p,"wb").write(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=120).read())
VID={"traf":"car traffic aerial","dealer":"car dealership","fab":"car factory robot","lot":"parking lot cars aerial","money":"money bills counting","night":"city traffic night aerial","exh":"car exhaust smoke","dash":"car dashboard screen"}
IMG={"chip":"microchip","parts":"car parts engine","real":"brazilian real money","empty":"empty parking lot","cam":"rear view camera car","sun":"car sunroof","touch":"car touchscreen","hatch":"hatchback car","dolar":"dollar bills","crash":"car crash test"}
cred={}
for k,q in VID.items():
    r=get("https://pixabay.com/api/videos/?"+urllib.parse.urlencode({"key":KEY,"q":q,"per_page":5,"safesearch":"true"}))
    for i,h in enumerate(r["hits"][:2]):
        v=h["videos"]; u=(v.get("medium") or {}).get("url") or v["small"]["url"]
        p=f"clips/{k}{i}.mp4"; dl(u,os.path.join(O,p)); cred[p]=f"Pixabay {h['id']} {h['user']}"
for k,q in IMG.items():
    r=get("https://pixabay.com/api/?"+urllib.parse.urlencode({"key":KEY,"q":q,"per_page":5,"image_type":"photo","safesearch":"true"}))
    for i,h in enumerate(r["hits"][:3]):
        p=f"img/{k}{i}.jpg"; dl(h["largeImageURL"],os.path.join(O,p)); cred[p]=f"Pixabay {h['id']} {h['user']}"
json.dump(cred,open(os.path.join(O,"img","creditos.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
print(len(cred))
