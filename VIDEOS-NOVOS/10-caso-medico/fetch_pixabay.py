import urllib.request,urllib.parse,json,os,sys,time
KEY=__import__("os").environ.get("KEY", "")
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"raw","cand")
UA={"User-Agent":"EstudioTeste/1.0 (contato local)"}
def get(u):
    return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60).read()
IMG={"xray":"human heart anatomy x-ray","energy":"energy drink cans","ecg":"electrocardiogram heart rate",
     "heart3d":"human heart 3d","caffeine":"caffeine molecule","echo":"ultrasound heart","body":"human body anatomy blue","pills":"medicine pills"}
VID={"vhosp":"hospital intensive care","vheart":"heart anatomy 3d","vecg":"heart rate monitor","vlab":"laboratory blood test"}
n=int(sys.argv[1]) if len(sys.argv)>1 else 3
for k,q in IMG.items():
    r=json.loads(get("https://pixabay.com/api/?"+urllib.parse.urlencode({"key":KEY,"q":q,"per_page":10,"safesearch":"true","orientation":"horizontal"})))
    for i,h in enumerate(r.get("hits",[])[:n]):
        p=f"{OUT}/{k}{i}.jpg"; open(p,"wb").write(get(h["largeImageURL"]))
    print(k,len(r.get("hits",[])))
for k,q in VID.items():
    r=json.loads(get("https://pixabay.com/api/videos/?"+urllib.parse.urlencode({"key":KEY,"q":q,"per_page":10,"safesearch":"true"})))
    for i,h in enumerate(r.get("hits",[])[:n]):
        v=h["videos"]; f=v.get("medium") or v.get("small")
        if not f or not f.get("url"): continue
        p=f"{OUT}/{k}{i}.mp4"; open(p,"wb").write(get(f["url"]))
    print(k,len(r.get("hits",[])))
