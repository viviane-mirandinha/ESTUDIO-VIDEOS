# Mascara do musculo: pixels coloridos da versao pintada (Kontext) onde a imagem base e P&B -> PNG RGBA (overlay nosso) + centroides
import numpy as np, json
from PIL import Image, ImageFilter
R={}
for base,cor in [("a_biceps","a_biceps_cor"),("a_costas","a_costas_cor"),("a_braco","a_braco_cor"),("a_cotovelo","a_cotovelo_cor")]:
    b=np.asarray(Image.open(f"img/{base}.jpg").convert("HSV")).astype(float)
    c=Image.open(f"img/{cor}.jpg").convert("RGB"); ch=np.asarray(c.convert("HSV")).astype(float); cr=np.asarray(c)
    hue=ch[...,0]*360/255; sat=ch[...,1]/255; val=ch[...,2]/255
    bh=b[...,0]*360/255; pur=Image.fromarray((((b[...,1]/255>0.25)&(bh>190)&(bh<270))*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(31))
    m=(np.asarray(pur)<128)&(sat>0.45)&(val>0.3)&~((hue>190)&(hue<270))&(b[...,1]/255<0.3)
    a=Image.fromarray((m*255).astype(np.uint8)).filter(ImageFilter.MedianFilter(5)).filter(ImageFilter.GaussianBlur(1.5))
    rgba=np.dstack([cr,np.asarray(a)]); Image.fromarray(rgba.astype(np.uint8),"RGBA").save(f"img/{base}_mask.png")
    cls={}
    for nome,(h0,h1) in {"vermelho":(-1,15),"laranja":(15,50),"verde":(70,170)}.items():
        mm=m&(((hue>h0)&(hue<h1))|((hue>340) if nome=="vermelho" else False))
        if mm.sum()>400:
            ys,xs=np.nonzero(mm); cls[nome]={"n":int(mm.sum()),"cx":int(xs.mean()),"cy":int(ys.mean()),"x0":int(xs.min()),"x1":int(xs.max()),"y0":int(ys.min()),"y1":int(ys.max()),
              "low_cx":int(xs[ys>np.percentile(ys,70)].mean()),"low_cy":int(ys[ys>np.percentile(ys,70)].mean()),
              "left_cx":int(xs[xs<np.median(xs)].mean()),"left_cy":int(ys[xs<np.median(xs)].mean()),"right_cx":int(xs[xs>=np.median(xs)].mean()),"right_cy":int(ys[xs>=np.median(xs)].mean())}
    R[base]=cls
json.dump(R,open("masks.json","w"),indent=0); print(json.dumps(R))
