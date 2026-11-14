import sys,glob
from PIL import Image
fs=sorted(glob.glob(sys.argv[1]));cols=int(sys.argv[3]) if len(sys.argv)>3 else 5;w=240
ims=[Image.open(f).convert("RGB") for f in fs];h=int(ims[0].height*w/ims[0].width);rows=(len(ims)+cols-1)//cols
S=Image.new("RGB",(cols*w,rows*h),"black")
for i,im in enumerate(ims):S.paste(im.resize((w,h)),((i%cols)*w,(i//cols)*h))
S.save(sys.argv[2],quality=85);print(S.size)
