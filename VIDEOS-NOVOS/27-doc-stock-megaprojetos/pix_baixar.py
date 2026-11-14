import json,urllib.request,os,subprocess
B=os.path.dirname(os.path.abspath(__file__))
sel={"takeoff":176930,"window":995,"cabin":162756,"airport":3586,"airport2":47339,"wing":142647,"engine":52536,"flight":15271,"sky":3966}
idx={}
for line in open(B+"/raw/busca.json",encoding="utf-8").read().replace("}{","}\n{").splitlines():
    for q,hs in json.loads(line).items():
        for h in hs: idx[h["id"]]=h
cred={}
for k,i in sel.items():
    h=idx[i]; raw=B+f"/raw/{k}.mp4"
    if not os.path.exists(raw):
        open(raw,"wb").write(urllib.request.urlopen(urllib.request.Request(h["url"],headers={"User-Agent":"estilos-novos-27/1.0"}),timeout=120).read())
    subprocess.run(["ffmpeg","-v","error","-y","-i",raw,"-t","16","-an","-vf","scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,fps=30","-c:v","libx264","-crf","22","-preset","veryfast","-pix_fmt","yuv420p",B+f"/clips/{k}.mp4"],check=True)
    cred[k]={"fonte":"Pixabay (licença Pixabay, uso livre)","pagina":h["page"],"tags":h["tags"]}
    print(k,"ok")
json.dump(cred,open(B+"/clips/creditos.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
