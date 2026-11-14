import os
import json,math
from shapely.geometry import shape,Polygon
G=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "recursos", "mapas", "countries50m.geojson"),encoding="utf-8"))
def name(f):
    p=f["properties"]; return p.get("ADMIN") or p.get("NAME") or p.get("name")
F=[f for f in G["features"] if name(f) in("Russia","Russian Federation")][0]
g=shape(F["geometry"])
def proj(lon,lat):
    if lon<0: lon+=360
    return ((lon-100)*math.cos(math.radians(lat))*0.95, -lat)
polys=list(g.geoms) if g.geom_type=="MultiPolygon" else [g]
P=[]
for p in polys:
    pts=[proj(x,y) for x,y in p.exterior.coords]
    q=Polygon(pts).buffer(0)
    if q.area<1.5: continue
    P.append(q.simplify(0.12))
xs=[x for q in P for x,_ in q.exterior.coords]; ys=[y for q in P for _,y in q.exterior.coords]
bx0,bx1,by0,by1=min(xs),max(xs),min(ys),max(ys)
X0,Y0,X1,Y1=300,190,1250,660
s=min((X1-X0)/(bx1-bx0),(Y1-Y0)/(by1-by0))
ox=X0+((X1-X0)-(bx1-bx0)*s)/2; oy=Y0+((Y1-Y0)-(by1-by0)*s)/2
T=lambda x,y:(round(ox+(x-bx0)*s,1),round(oy+(y-by0)*s,1))
P.sort(key=lambda q:-q.area)
paths=[]
for q in P:
    c=[T(x,y) for x,y in q.exterior.coords]
    paths.append("M"+" L".join(f"{a},{b}" for a,b in c)+"Z")
def pt(lon,lat): return T(*proj(lon,lat))
cities={"moscou":(37.6,55.75),"spb":(30.3,59.9),"vlad":(131.9,43.1),"ekat":(60.6,56.8),"omsk":(73.4,55),"novo":(82.9,55),"kras":(92.9,56),"irk":(104.3,52.3),"chita":(113.5,52),"khab":(135,48.5)}
C={k:pt(*v) for k,v in cities.items()}
ural=[pt(59,68.5),pt(60,64),pt(59.5,60),pt(59,56),pt(58.5,52)]
rail=[C[k] for k in ["moscou","ekat","omsk","novo","kras","irk","chita","khab","vlad"]]
# fusos: longitudes 30..180 a cada ~15
fus=[]
for lon in range(30,181,15):
    fus.append([pt(lon,74),pt(lon,50)])
json.dump({"paths":paths,"cities":C,"ural":ural,"rail":rail,"fusos":fus,"bbox":[min(T(*c)[0] for c in [(bx0,by0)]),0]},open("map.json","w"))
print(len(paths),sum(len(p) for p in paths),C["moscou"],C["vlad"])
import random
from shapely.geometry import Point
from shapely.ops import unary_union
from shapely import affinity
S=unary_union([Polygon([T(x,y) for x,y in q.exterior.coords]) for q in P])
random.seed(7)
ux=C["ekat"][0]
west=[];east=[]
mx,my=C["moscou"]
while len(west)<34:
    x=random.gauss(mx+10,45);y=random.gauss(my-15,40)
    if x<ux+5 and S.contains(Point(x,y)): west.append((round(x,1),round(y,1)))
tries=0
while len(east)<9 and tries<20000:
    tries+=1
    x=random.uniform(ux+40,1230);y=random.uniform(200,660)
    if S.buffer(-12).contains(Point(x,y)) and all(((x-a)**2+(y-b)**2)>55**2 for a,b in east): east.append((round(x,1),round(y,1)))
d=json.load(open("map.json"));d["west"]=west;d["east"]=east;d["bounds"]=S.bounds
json.dump(d,open("map.json","w"));print(S.bounds,ux)
