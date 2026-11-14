import json,os,sys,time,subprocess,urllib.request,urllib.parse
O=os.path.dirname(os.path.abspath(__file__)); K=""
UA={"User-Agent":"TesteEstilos/1.0 (contato local)"}
def get(u):
    return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=30))
Q=[("b01","storm clouds dark"),("b02","trees wind storm"),("b03","sailboat sea"),("b04","traffic night city"),
   ("b05","rain window"),("b06","crowd people walking"),("b07","hospital corridor"),("b08","man silhouette thinking"),
   ("b09","stress anxiety man"),("b10","bird flying sky"),("b11","businessman office stress"),("b12","man sad alone"),
   ("b13","sunrise"),("b14","theater stage"),("b15","meditation"),("b16","man standing sea sunset"),("b17","walking forward road")]
cred={}
for n,q in Q:
    out=f"{O}/clips/{n}.mp4"
    if os.path.exists(out): continue
    try:
        r=get("https://pixabay.com/api/videos/?"+urllib.parse.urlencode({"key":K,"q":q,"per_page":10,"safesearch":"true"}))
        h=[x for x in r["hits"] if x["duration"]>=6] or r["hits"]
        v=h[0]; vs=v["videos"]; u=(vs.get("medium") or vs.get("small"))["url"]
        tmp=f"{O}/clips/_{n}.mp4"; open(tmp,"wb").write(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0"}),timeout=120).read())
        subprocess.run(["ffmpeg","-v","error","-y","-i",tmp,"-t","14","-an","-vf",
          "scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,fps=30,hue=s=0.12,eq=brightness=-0.04:contrast=1.08,gblur=sigma=1.2",
          "-c:v","libx264","-crf","26","-preset","veryfast","-pix_fmt","yuv420p",out],check=True)
        os.remove(tmp); cred[n]={"q":q,"pixabay":v["pageURL"],"dur":v["duration"]}; print(n,"ok",v["duration"])
    except Exception as e: print(n,"ERRO",e)
    time.sleep(1)
W=[("epicteto","File:Epicteti Enchiridion Latinis versibus adumbratum (Oxford 1715) frontispiece.jpg"),
   ("marco","File:Marcus Aurelius Glyptothek Munich.jpg")]
for n,f in W:
    out=f"{O}/img/{n}.jpg"
    if os.path.exists(out): continue
    for tent in range(3):
        try:
            r=get("https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","titles":f,"prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":1600,"format":"json"}))
            p=list(r["query"]["pages"].values())[0]; ii=p["imageinfo"][0]
            urllib.request.urlretrieve(urllib.request.Request(ii["thumburl"],headers=UA).full_url,out) if False else open(out,"wb").write(urllib.request.urlopen(urllib.request.Request(ii["thumburl"],headers=UA),timeout=60).read())
            md=ii.get("extmetadata",{}); cred[n]={"arquivo":f,"autor":md.get("Artist",{}).get("value","")[:120],"licenca":md.get("LicenseShortName",{}).get("value","")}
            print(n,"ok",cred[n]["licenca"]); break
        except Exception as e: print(n,"erro",e); time.sleep(20)
    time.sleep(1.5)
old={}
if os.path.exists(f"{O}/img/creditos.json"): old=json.load(open(f"{O}/img/creditos.json",encoding="utf-8"))
old.update(cred); json.dump(old,open(f"{O}/img/creditos.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
