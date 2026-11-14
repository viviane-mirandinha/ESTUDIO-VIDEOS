import urllib.request,urllib.parse,json,time,os
UA={"User-Agent":"EstudioTesteBot/1.0 (uso pessoal; contato local)"}
OUT="raw/cand2";os.makedirs(OUT,exist_ok=True)
def get(u,tries=4):
    for t in range(tries):
        try: return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60).read()
        except Exception as e:
            if "429" in str(e): time.sleep(25)
            else: raise
    raise Exception("falhou "+u)
cred={}
for k,q in {"mri":"cardiac MRI late gadolinium enhancement","mri2":"cardiac magnetic resonance short axis","dcm":"dilated cardiomyopathy"}.items():
    r=json.loads(get("https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","format":"json","generator":"search","gsrsearch":"filetype:bitmap "+q,"gsrnamespace":6,"gsrlimit":4,"prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":1280})))
    time.sleep(1.5)
    for i,p in enumerate((r.get("query") or {}).get("pages",{}).values()):
        ii=p["imageinfo"][0]; f=f"{OUT}/{k}{i}.jpg"
        try: open(f,"wb").write(get(ii["thumburl"].split("?")[0]))
        except Exception as e: print("skip",f); continue
        cred[f]={"titulo":p["title"],"url":ii["descriptionurl"],"licenca":ii.get("extmetadata",{}).get("LicenseShortName",{}).get("value","")}
        time.sleep(1.5)
json.dump(cred,open(OUT+"/creditos.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
KEY=__import__("os").environ.get("KEY", "")
for k,q in {"vicu":"hospital patient monitor","vbed":"hospital bed","vdrink":"energy drink"}.items():
    r=json.loads(get("https://pixabay.com/api/videos/?"+urllib.parse.urlencode({"key":KEY,"q":q,"per_page":10,"safesearch":"true"})))
    for i,h in enumerate(r.get("hits",[])[:3]):
        v=h["videos"]; fm=v.get("medium") or v.get("small")
        open(f"{OUT}/{k}{i}.mp4","wb").write(get(fm["url"]))
print(len(os.listdir(OUT)))
