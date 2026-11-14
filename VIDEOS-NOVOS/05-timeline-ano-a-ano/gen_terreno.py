# Relevo procedural (base: versao Pearl Harbor) - Franca + sul da Inglaterra
# Elevacao: AWS Terrain Tiles (terrarium, dominio publico/USGS). Mascara terra/mar: countries50m.geojson (Natural Earth)
import math,os,json,time,urllib.request,numpy as np
from PIL import Image,ImageFilter,ImageDraw
from concurrent.futures import ThreadPoolExecutor
UA={'User-Agent':'EstudioVideos-teste/1.0 (contato local)'}
GEO=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "recursos", "mapas", "countries50m.geojson")
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
    P=[(x,y) for y in ty for x in tx]
    with ThreadPoolExecutor(6) as ex: T=dict(zip(P,ex.map(lambda p:tile(z,*p),P)))
    big=np.vstack([np.hstack([T[(x,y)] for x in tx]) for y in ty])
    ox,oy=tx[0]*256,ty[0]*256
    return big[int(Y0-oy):int(Y1-oy),int(X0-ox):int(X1-ox)],int(X0),int(Y0)
def landmask(shape,z,X0,Y0,b):
    im=Image.new('L',(shape[1],shape[0]),0); d=ImageDraw.Draw(im)
    for f in json.load(open(GEO,encoding='utf-8'))['features']:
        g=f['geometry']; polys=g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
        for pl in polys:
            ring=pl[0]
            if max(p[0] for p in ring)<b[0]-2 or min(p[0] for p in ring)>b[2]+2 or max(p[1] for p in ring)<b[1]-2 or min(p[1] for p in ring)>b[3]+2: continue
            d.polygon([(lon2x(p[0],z)-X0,lat2y(p[1],z)-Y0) for p in ring],fill=255)
            for h in pl[1:]: d.polygon([(lon2x(p[0],z)-X0,lat2y(p[1],z)-Y0) for p in h],fill=0)
    return np.asarray(im)>127
def gblur(a,sg):
    r=int(3*sg);k=np.exp(-np.arange(-r,r+1)**2/(2*sg*sg));k/=k.sum()
    a=np.pad(a,r,mode='edge')
    a=np.apply_along_axis(lambda v:np.convolve(v,k,'valid'),0,a)
    return np.apply_along_axis(lambda v:np.convolve(v,k,'valid'),1,a)
def render(c,land,cell):
    c=gblur(c.astype(np.float32),1.0)
    gy,gx=np.gradient(c,cell); az,alt=math.radians(315),math.radians(40)
    slope=np.arctan(np.hypot(gx,gy)*2.2); aspect=np.arctan2(-gx,gy)
    hs=np.sin(alt)*np.cos(slope)+np.cos(alt)*np.sin(slope)*np.cos(az-aspect); hs=np.clip(hs,0,1)
    stops=[(0,(92,142,60)),(120,(110,152,66)),(350,(142,150,74)),(800,(152,126,76)),(1600,(130,104,74)),(3000,(220,214,206))]
    e=np.clip(c,0,3000); col=np.zeros(c.shape+(3,),np.float32)
    for i in range(len(stops)-1):
        (a0,c0),(a1,c1)=stops[i],stops[i+1]; m=(e>=a0)&(e<=a1); t=((e-a0)/(a1-a0))[...,None]
        col[m]=(np.array(c0)*(1-t)+np.array(c1)*t)[m]
    col=col*(0.55+0.75*hs)[...,None]
    d=np.clip(-c,0,3000)/3000; d=np.sqrt(d)[...,None]
    sea=np.array([62,128,160])*(1-d)+np.array([16,46,78])*d
    lm=Image.fromarray((land*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.GaussianBlur(3))
    coast=np.asarray(lm).astype(np.float32)[...,None]/255*(~land[...,None])
    sea=sea*(1-0.35*coast)+np.array([120,175,190])*0.35*coast
    out=np.where(land[...,None],col,sea)
    h,w=c.shape; rng=np.random.default_rng(1)
    out=out*(1+0.04*(rng.random((h,w,1))-0.5))
    return Image.fromarray(np.clip(out,0,255).astype(np.uint8))
meta={}
for nome,b,z in [('europa',(-12.0,41.5,16.0,55.2),8)]:
    c,X0,Y0=elev(b,z); land=landmask(c.shape,z,X0,Y0,b)
    cell=156543*math.cos(math.radians(47.5))/2**z
    im=render(c,land,cell); im.save(f'img/{nome}.jpg',quality=88)
    meta[nome]={'z':z,'x0':X0,'y0':Y0,'scale':1.0,'w':im.width,'h':im.height}
    print(nome,im.size,round(float(c.min())),round(float(c.max())))
json.dump(meta,open('mapas.json','w'))
