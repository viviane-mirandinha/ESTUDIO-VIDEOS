import json,subprocess,sys
from PIL import Image
import io
v=sys.argv[1]; e=json.load(open("edit.json",encoding="utf-8"))
for it in e["items"]:
    if it["track"]!="fundo": continue
    t=it["start"]+it["dur"]*0.55
    b=subprocess.run(["ffmpeg","-v","error","-ss",str(t),"-i",v,"-frames:v","1","-f","image2pipe","-vcodec","png","-"],capture_output=True).stdout
    im=Image.open(io.BytesIO(b)).convert("L"); w,h=im.size
    c=im.crop((w//4,h//6,3*w//4,5*h//6))
    print(f"{it['id']:5} {it['label'][:26]:26} t={t:5.1f} Y={sum(im.getdata())/(w*h):5.1f} centro={sum(c.getdata())/(c.size[0]*c.size[1]):5.1f}")
