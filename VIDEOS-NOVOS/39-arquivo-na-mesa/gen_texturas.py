# texturas 100% por código (numpy): mesa de madeira escura + grão de filme
import numpy as np
from PIL import Image, ImageFilter
rng=np.random.default_rng(39)
W,H=3200,2000
def noise(w,h,s,seed):
    r=np.random.default_rng(seed); a=r.random((h//s+2,w//s+2)).astype(np.float32)
    im=Image.fromarray((a*255).astype(np.uint8)).resize((w,h),Image.BICUBIC); return np.asarray(im,np.float32)/255
y=np.arange(H,dtype=np.float32)[:,None]; x=np.arange(W,dtype=np.float32)[None,:]
n1=noise(W,H,160,1); n2=noise(W,H,40,2); n3=noise(W,H,8,3)
plank=(y//330).astype(int)
off=(plank*977)%W
g=np.sin((y*0.05)+n1*5+n2*1.5+x*0.0004+(plank*1.7))  # veios
g2=np.sin(y*0.9+n2*6)*0.5
v=0.56+0.08*g+0.04*g2+0.10*(n3-0.5)+0.10*(n1-0.5)
v=v*(0.88+0.24*noise(W,H,600,4))
gap=(np.abs((y%330)-0)<3)|(np.abs((y%330)-329)<2)
v[gap[:,0] if gap.ndim==2 and gap.shape[1]==1 else gap]=0.18 if False else v[gap[:,0]] if False else 0.2
base=np.array([86,52,30],np.float32)/255
img=np.clip(v[...,None]*base[None,None,:]*1.5,0,1)
# juntas verticais nas tábuas
for p in range(H//330+1):
    xs=(p*1310+400)%W
    img[p*330:(p+1)*330, xs:xs+3]*=0.35
Image.fromarray((img*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6)).save("img/mesa.jpg",quality=88)
# grão (tile 640x360)
gr=(rng.normal(0.5,0.18,(360,640))).clip(0,1)
a=Image.fromarray((gr*255).astype(np.uint8)).convert("L")
rgba=Image.merge("RGBA",[a,a,a,Image.new("L",a.size,60)])
rgba.save("img/grao.png")
print("ok")
