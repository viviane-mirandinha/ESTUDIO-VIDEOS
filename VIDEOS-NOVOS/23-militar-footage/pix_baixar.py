import json,urllib.request,os,subprocess
B=os.path.dirname(os.path.abspath(__file__))
sel={"truck1":217279,"truck2":217278,"humvee":218919,"aerial":266987,"aerial2":149466,"sniper1":61418,"sniper2":61419,"sniper3":61420,"sniper4":61421,"nato":375,"forest":164099,"ammo":84556,"ammo2":79759,"smoke":306,"burn":252053,"fog":367528,"tank":16393,"soldiers":446}
idx={}
for line in open(B+"/raw/busca.json",encoding="utf-8").read().replace("}{","}\n{").splitlines():
    for q,hs in json.loads(line).items():
        for h in hs: idx[h["id"]]=h
cred={}
for k,i in sel.items():
    h=idx[i]; raw=B+f"/raw/{k}.mp4"
    if not os.path.exists(raw):
        open(raw,"wb").write(urllib.request.urlopen(urllib.request.Request(h["url"],headers={"User-Agent":"estilos-novos-23/1.0"}),timeout=120).read())
    subprocess.run(["ffmpeg","-v","error","-y","-i",raw,"-t","16","-an","-vf","scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,fps=30","-c:v","libx264","-crf","22","-preset","veryfast","-pix_fmt","yuv420p",B+f"/clips/{k}.mp4"],check=True)
    cred[k]={"fonte":"Pixabay (licença Pixabay, uso livre)","pagina":h["page"],"tags":h["tags"]}
    print(k,"ok")
json.dump(cred,open(B+"/clips/creditos.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
