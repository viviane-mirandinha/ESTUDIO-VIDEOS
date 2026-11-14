# Relevo procedural a partir de tiles de elevacao abertas (AWS Terrain Tiles / terrarium, dominio publico/USGS)
import math,os,json,io,time,urllib.request,numpy as np
from PIL import Image,ImageFilter
from concurrent.futures import ThreadPoolExecutor
UA={'User-Agent':'EstudioVideos-teste/1.0 (contato local)'}
def lon2x(lon,z): return (lon+180)/360*256*2**z
def lat2y(lat,z): r=math.radians(lat); return (1-math.log(math.tan(r)+1/math.cos(r))/math.pi)/2*256*2**z
def tile(z,x,y):
    f=f'tiles/{z}_{x}_{y}.png'
    if not os.path.exists(f):
        for k in range(4):
            try:
                d=urllib.request.urlopen(urllib.request.Request(f'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png',headers=UA),timeout=30).read();open(f,'wb').write(d);break
            except Exception as e: time.sleep(3)
    a=np.asarray(Image.open(f).convert('RGB')).astype(np.float32)
    return a[...,0]*256+a[...,1]+a[...,2]/256-32768
def elev(b,z):
    lo0,la0,lo1,la1=b; X0,X1=lon2x(lo0,z),lon2x(lo1,z); Y0,Y1=lat2y(la1,z),lat2y(la0,z)
    tx=range(int(X0//256),int(X1//256)+1); ty=range(int(Y0//256),int(Y1//256)+1)
    with ThreadPoolExecutor(6) as ex: T={(x,y):r for (x,y),r in zip([(x,y) for y in ty for x in tx],ex.map(lambda p:tile(z,*p),[(x,y) for y in ty for x in tx]))}
    big=np.vstack([np.hstack([T[(x,y)] for x in tx]) for y in ty])
    ox,oy=tx[0]*256,ty[0]*256
    c=big[int(Y0-oy):int(Y1-oy),int(X0-ox):int(X1-ox)]
    return c,int(X0),int(Y0)
def gblur(a,sg):
    r=int(3*sg);k=np.exp(-np.arange(-r,r+1)**2/(2*sg*sg));k/=k.sum()
    a=np.pad(a,r,mode='edge')
    a=np.apply_along_axis(lambda v:np.convolve(v,k,'valid'),0,a)
    return np.apply_along_axis(lambda v:np.convolve(v,k,'valid'),1,a)
def render(c,scale,cell):
    if scale!=1:
        im=Image.fromarray(c,'F'); c=np.asarray(im.resize((int(c.shape[1]*scale),int(c.shape[0]*scale)),Image.BICUBIC))
    c=gblur(c.astype(np.float32),1.2)
    gy,gx=np.gradient(c,cell); az,alt=math.radians(315),math.radians(40)
    slope=np.arctan(np.hypot(gx,gy)); aspect=np.arctan2(-gx,gy)
    hs=np.sin(alt)*np.cos(slope)+np.cos(alt)*np.sin(slope)*np.cos(az-aspect); hs=np.clip(hs,0,1)
    land=c>0.5
    # hipsometria estilo "atlas": verde baixo -> oliva -> marrom no alto
    stops=[(0,(86,140,58)),(80,(104,152,64)),(300,(140,150,72)),(600,(150,124,74)),(1000,(128,100,70))]
    e=np.clip(c,0,1000); col=np.zeros(c.shape+(3,),np.float32)
    for i in range(len(stops)-1):
        (a0,c0),(a1,c1)=stops[i],stops[i+1]; m=(e>=a0)&(e<=a1); t=((e-a0)/(a1-a0))[...,None]
        col[m]=(np.array(c0)*(1-t)+np.array(c1)*t)[m]
    shade=(0.55+0.75*hs)[...,None]; col=col*shade
    d=np.clip(-c,0,3000)/3000; d=np.sqrt(d)[...,None]
    sea=np.array([62,128,160])*(1-d)+np.array([16,46,78])*d
    # faixa clara na costa
    lm=Image.fromarray((land*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(4))
    coast=np.asarray(lm).astype(np.float32)[...,None]/255*(~land[...,None])
    sea=sea*(1-0.35*coast)+np.array([120,175,190])*0.35*coast
    out=np.where(land[...,None],col,sea)
    # vinheta + leve textura de papel
    h,w=c.shape; yy,xx=np.mgrid[0:h,0:w]; rng=np.random.default_rng(1)
    out=out*(1+0.04*(rng.random((h,w,1))-0.5))
    return Image.fromarray(np.clip(out,0,255).astype(np.uint8))
import sys
meta=json.load(open('mapas.json')) if os.path.exists('mapas.json') else {}
SO=sys.argv[1:]
for nome,b,z,sc in [('ilha',(-158.85,21.10,-157.10,22.50),12,1.0),('porto',(-158.005,21.288,-157.915,21.395),14,2.5)]:
    if SO and nome not in SO: continue
    c,X0,Y0=elev(b,z); cell=(156543*math.cos(math.radians(21.4))/2**z)/sc
    im=render(c,sc,cell); im.save(f'img/{nome}.jpg',quality=90)
    meta[nome]={'z':z,'x0':X0,'y0':Y0,'scale':sc,'w':im.width,'h':im.height}
    print(nome,im.size,round(float(c.min())),round(float(c.max())))
json.dump(meta,open('mapas.json','w'))
