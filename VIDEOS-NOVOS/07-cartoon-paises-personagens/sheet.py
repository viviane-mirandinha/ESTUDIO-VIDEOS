import os
from PIL import Image,ImageDraw,ImageFont;import glob,os,sys
fs=sorted(glob.glob(sys.argv[1]));W=int(sys.argv[3]) if len(sys.argv)>3 else 3;H=(len(fs)+W-1)//W
sh=Image.new('RGB',(W*320,H*200));d=ImageDraw.Draw(sh);ft=ImageFont.truetype('arial.ttf',18)
for k,f in enumerate(fs):
  try: im=Image.open(f).convert('RGB')
  except Exception: continue
  im=im;im.thumbnail((320,200));x,y=(k%W)*320,(k//W)*200;sh.paste(im,(x,y));d.text((x+4,y+4),os.path.basename(f),fill='yellow',font=ft,stroke_width=2,stroke_fill='black')
sh.save(sys.argv[2],quality=80)
