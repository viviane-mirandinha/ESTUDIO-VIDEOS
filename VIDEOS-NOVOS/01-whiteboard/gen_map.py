import os
# Gera map_paths.json: Inglaterra/Escocia/Gales/Irl.Norte/Irlanda (countries50m + fronteiras internas aproximadas)
import json,math
from shapely.geometry import shape,Polygon,box
from shapely.ops import unary_union
d=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "recursos", "mapas", "countries50m.geojson"),encoding='utf-8'))
F={f['properties']['ADM0_A3']:shape(f['geometry']) for f in d['features'] if f['properties']['ADM0_A3'] in('GBR','IRL','FRA')}
clip=box(-11,49.8,2.2,61)
gbr=F['GBR'].intersection(clip); irl=F['IRL'].intersection(clip)
parts=list(gbr.geoms)
nir=unary_union([p for p in parts if p.centroid.x<-5.5 and p.centroid.y<55.45])
gb=unary_union([p for p in parts if not(p.centroid.x<-5.5 and p.centroid.y<55.45)])
sco_poly=Polygon([(-7,54.5),(-3.6,54.85),(-3.05,54.98),(-2.6,55.15),(-2.2,55.45),(-2.03,55.81),(2,55.9),(2,61.5),(-9,61.5),(-9,55.6),(-7,55.6)])
wal_poly=Polygon([(-3.2,53.45),(-3.1,53.3),(-3.0,53.1),(-3.1,52.9),(-3.0,52.55),(-3.15,52.3),(-3.0,52.0),(-2.85,51.85),(-2.65,51.6),(-3.0,51.2),(-6,51.2),(-6,53.6)])
sco=gb.intersection(sco_poly); wal=gb.difference(sco_poly).intersection(wal_poly); eng=gb.difference(sco_poly).difference(wal_poly)
# projecao: equiretangular com cos(54.5), 1 grau lon = K*cos px
K=46.0; C=math.cos(math.radians(54.5))
def P(lon,lat): return ((lon+11)*K*C, (61-lat)*K)
def path(g,tol=0.02):
    g=g.simplify(tol,preserve_topology=True)
    ps=[g] if g.geom_type=='Polygon' else [p for p in g.geoms if p.geom_type=='Polygon']
    ps=sorted(ps,key=lambda p:-p.exterior.length); ps=[p for p in ps if p.area>0.004]
    return "".join("M"+"L".join("%.1f,%.1f"%P(x,y) for x,y in p.exterior.coords)+"Z" for p in ps)
out={k:path(g) for k,g in dict(eng=eng,sco=sco,wal=wal,nir=nir,irl=irl).items()}
W,H=P(2.2,49.8); out['_size']=[round(W,1),round(H,1)]
cap={'londres':(-0.13,51.5),'edimburgo':(-3.19,55.95),'cardiff':(-3.18,51.48),'belfast':(-5.93,54.6),'dublin':(-6.26,53.35)}
out['_pts']={k:[round(v,1) for v in P(*c)] for k,c in cap.items()}
json.dump(out,open('map_paths.json','w'))
print(out['_size'],{k:len(v) for k,v in out.items() if not k.startswith('_')})
