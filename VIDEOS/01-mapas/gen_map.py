import os
import json,math
from shapely.geometry import shape,box
from shapely.ops import transform
d=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "recursos", "mapas", "countries50m.geojson"),encoding='utf-8'))
K=20.0
def merc(lon,lat):
    x=(lon+180)*K
    y=-math.degrees(math.log(math.tan(math.pi/4+math.radians(max(min(lat,80),-80))/2)))*K
    return x,y
clip=box(-150,-62,-5,72)
out=[]
def pts(ring):
    return "M"+"L".join(f"{merc(x,y)[0]:.1f},{merc(x,y)[1]:.1f}" for x,y in ring.coords)+"Z"
for f in d['features']:
    g=shape(f['geometry'])
    if not g.intersects(clip): continue
    g=g.intersection(clip).simplify(0.015,preserve_topology=True)
    polys=[g] if g.geom_type=='Polygon' else [p for p in getattr(g,'geoms',[]) if p.geom_type=='Polygon']
    path="".join(pts(p.exterior)+"".join(pts(i) for i in p.interiors) for p in polys)
    if path: out.append({"id":f['properties']['ADM0_A3'],"name":f['properties']['ADMIN'],"d":path})
json.dump(out,open('map_paths.json','w',encoding='utf-8'))
P={"ny":(-74.0,40.7),"sf":(-122.4,37.8),"horn":(-67.3,-55.98),"colon":(-79.9,9.36),"balboa":(-79.55,8.95),"gatun":(-79.92,9.2)}
json.dump({k:merc(*v) for k,v in P.items()},open('map_points.json','w'))
print(len(out),sum(len(o['d']) for o in out))
