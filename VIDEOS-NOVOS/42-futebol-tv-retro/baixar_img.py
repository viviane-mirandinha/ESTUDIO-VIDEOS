import json,urllib.request,urllib.parse,os,time
T={"pele":"File:Pele con brasil (cropped).jpg","jair":"File:Jairzinho México 70.jpg","jair2":"File:Jairzinho 1970s.jpg","ca":"File:Carlos Alberto (1970).jpg","zag":"File:Zagalo, Fundo Correio da Manhã - 3.tif","time":"File:Brazil national team 1970.jpg"}
H={"User-Agent":"EstudioVideosLocal/1.0 (contato pessoal)"}
cred=json.load(open("creditos.json",encoding="utf-8")) if os.path.exists("creditos.json") else {}
def get(u):
  for k in range(6):
    try: return urllib.request.urlopen(urllib.request.Request(u,headers=H)).read()
    except Exception as e: print("retry",e); time.sleep(8*(k+1))
for k,t in T.items():
  u="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","format":"json","titles":t,"prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":900})
  p=list(json.loads(get(u))["query"]["pages"].values())[0]; ii=p["imageinfo"][0]; m=ii["extmetadata"]
  if not os.path.exists(k+".jpg"): open(k+".jpg","wb").write(get(ii["thumburl"])); time.sleep(4)
  cred[k]={"arquivo":t,"pagina":ii["descriptionurl"],"licenca":m.get("LicenseShortName",{}).get("value"),"autor":m.get("Artist",{}).get("value","")[:160]}
  print(k,cred[k]["licenca"])
json.dump(cred,open("creditos.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
