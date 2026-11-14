# Mascara de agua do porto a partir da linha de costa do OpenStreetMap (ODbL) + relevo terrarium
import json,math,numpy as np
from PIL import Image,ImageDraw,ImageFilter
from shapely.geometry import LineString,box,Point
from shapely.ops import linemerge,unary_union,split,polygonize
d=json.load(open('costa.json',encoding='utf-8'))
M=json.load(open('mapas.json'))['porto']
z,sc=M['z'],M['scale']
def px(lon,lat):
    X=(lon+180)/360*256*2**z; r=math.radians(lat); Y=(1-math.log(math.tan(r)+1/math.cos(r))/math.pi)/2*256*2**z
    return ((X-M['x0'])*sc,(Y-M['y0'])*sc)
W,H=M['w'],M['h']
lines=[LineString([px(p['lon'],p['lat']) for p in e['geometry']]) for e in d['elements'] if len(e['geometry'])>1]
bb=box(-50,-50,W+50,H+50)
merged=unary_union(lines+[bb.exterior])
polys=list(polygonize(merged))
sea_pts=[px(-157.95,21.285),px(-157.97,21.33),px(-157.975,21.36)]
mask=Image.new('L',(W,H),0); dr=ImageDraw.Draw(mask)
nw=0
for p in polys:
    if any(p.contains(Point(*s)) for s in sea_pts):
        nw+=1; dr.polygon(list(p.exterior.coords),fill=255)
        for i in p.interiors: dr.polygon(list(i.coords),fill=0)
print('pecas',len(polys),'agua',nw)
mask=mask.filter(ImageFilter.GaussianBlur(1.5))
m=np.asarray(mask).astype(np.float32)[...,None]/255
land=np.asarray(Image.open('img/porto.jpg').convert('RGB')).astype(np.float32)
# agua: azul com faixa clara na margem
edge=np.asarray(mask.filter(ImageFilter.MinFilter(15)).filter(ImageFilter.GaussianBlur(8))).astype(np.float32)[...,None]/255
sea=np.array([52,118,150])*edge+np.array([96,160,180])*(1-edge)
out=land*(1-m)+sea*m
Image.fromarray(np.clip(out,0,255).astype(np.uint8)).save('img/porto.jpg',quality=90)
