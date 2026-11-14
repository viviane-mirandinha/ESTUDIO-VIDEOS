import subprocess,sys,io
from PIL import Image,ImageStat
v=sys.argv[1]
for t in sys.argv[2:]:
    b=subprocess.run(["ffmpeg","-v","error","-ss",t,"-i",v,"-frames:v","1","-f","image2pipe","-vcodec","png","-"],capture_output=True).stdout
    im=Image.open(io.BytesIO(b)).convert("L"); w,h=im.size
    print(t, round(ImageStat.Stat(im).mean[0],1), "centro", round(ImageStat.Stat(im.crop((w//4,h//6,3*w//4,5*h//6))).mean[0],1))
