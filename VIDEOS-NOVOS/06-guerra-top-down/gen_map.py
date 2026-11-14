import os
# map_data.json: costas do Pacifico (countries50m) em km, origem Ford Island (-157.96, 21.36)
import json,math
from shapely.geometry import shape,box,Polygon
from shapely import affinity
LON0,LAT0=-157.96,21.36; KY=110.6; KX=110.6*math.cos(math.radians(LAT0))
def P(lon,lat): return (lon-LON0)*KX, -(lat-LAT0)*KY   # y para baixo (SVG)
d=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "recursos", "mapas", "countries50m.geojson"),encoding='utf-8'))
clip=box(-250,-8,-95,64); oahu=box(-158.4,21.1,-157.5,21.8)
out={}
for f in d['features']:
    g=shape(f['geometry']); a3=f['properties']['ADM0_A3']
    ps=[g] if g.geom_type=='Polygon' else list(g.geoms)
    paths=[]
    for p in ps:
        if p.centroid.x>0: p=affinity.translate(p,-360)
        if p.centroid.within(oahu): continue
        q=p.intersection(clip)
        if q.is_empty: continue
        for r in ([q] if q.geom_type=='Polygon' else [x for x in getattr(q,'geoms',[]) if x.geom_type=='Polygon']):
            if r.area<0.0004: continue
            tol=0.004 if r.area<0.5 else 0.03
            r=r.simplify(tol,preserve_topology=True)
            paths.append("M"+"L".join("%.1f,%.1f"%P(x,y) for x,y in r.exterior.coords)+"Z")
    if paths: out[a3]="".join(paths)
# Oahu desenhado a mao (lon,lat) - mais detalhe que o 50m
O=[(-158.28,21.575),(-158.2,21.585),(-158.105,21.595),(-158.065,21.64),(-158.04,21.675),(-158.0,21.70),(-157.985,21.712),(-157.95,21.685),(-157.92,21.645),(-157.905,21.61),(-157.87,21.575),(-157.85,21.555),(-157.835,21.515),(-157.84,21.465),(-157.81,21.43),(-157.785,21.425),(-157.76,21.44),(-157.735,21.46),(-157.72,21.452),(-157.735,21.435),(-157.745,21.415),(-157.73,21.40),(-157.715,21.385),(-157.705,21.36),(-157.70,21.33),(-157.66,21.315),(-157.648,21.305),(-157.665,21.29),(-157.69,21.272),(-157.705,21.258),(-157.72,21.275),(-157.745,21.27),(-157.77,21.268),(-157.80,21.255),(-157.815,21.26),(-157.83,21.272),(-157.85,21.285),(-157.875,21.298),(-157.91,21.305),(-157.94,21.31),(-157.965,21.316),(-158.0,21.305),(-158.05,21.298),(-158.105,21.296),(-158.125,21.32),(-158.135,21.355),(-158.16,21.385),(-158.19,21.43),(-158.215,21.465),(-158.23,21.51),(-158.25,21.545)]
out['_oahu']=[[round(v,2) for v in P(*c)] for c in O]
json.dump(out,open('map_data.json','w'))
print({k:len(v) for k,v in out.items()})
