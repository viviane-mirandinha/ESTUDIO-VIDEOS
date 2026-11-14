import json,math,os
from shapely.geometry import shape,mapping
from shapely.ops import unary_union
O=os.path.dirname(os.path.abspath(__file__))
mun=json.load(open(os.path.join(O,"geo/sp_mun.json"),encoding="utf-8"))["features"]
uf=json.load(open(os.path.join(O,"geo/br_uf.json"),encoding="utf-8"))["features"]
C=math.cos(math.radians(22.3))
geoms={f["properties"]["codarea"]:shape(f["geometry"]) for f in mun}
sp=unary_union(list(geoms.values()))
x0,y0,x1,y1=sp.bounds
W=(x1-x0)*C; H=(y1-y0)
k=min(1120/W,620/H)
cx,cy=640,372
def P(lon,lat): return (cx+((lon-(x0+x1)/2)*C)*k, cy-(lat-(y0+y1)/2)*k)
def path(g,tol=0.3,f=P):
    from shapely.ops import transform
    g=transform(lambda xs,ys,z=None:tuple(zip(*[f(a,b) for a,b in zip(xs,ys)])),g).simplify(tol)
    polys=[g] if g.geom_type=="Polygon" else list(getattr(g,"geoms",[]))
    out=[]
    for p in polys:
        for ring in [p.exterior]+list(p.interiors):
            cs=list(ring.coords)
            if len(cs)<3: continue
            out.append("M"+"L".join(f"{a:.1f},{b:.1f}" for a,b in cs)+"Z")
    return "".join(out)
cities={"3550308":"São Paulo","3509502":"Campinas","3518800":"Guarulhos","3552205":"Sorocaba","3543402":"Ribeirão Preto","3549904":"São José dos Campos"}
D={"mun":[[c,path(g,0.25)] for c,g in geoms.items()],"sp":path(sp,0.3),"nb":[],"cities":{},"br":[]}
for c in cities:
    p=geoms[c].centroid; D["cities"][c]=[round(v,1) for v in P(p.x,p.y)]
D["oc"]=[round(v) for v in P(-45.6,-25.0)]
names={"50":"MATO GROSSO DO SUL","31":"MINAS GERAIS","33":"RIO DE JANEIRO","41":"PARANÁ","52":""}
LL={"50":(-53.7,-21.2),"31":(-45.2,-21.0),"33":(-43.7,-22.35),"41":(-51.3,-24.3),"52":(-50,-18)}
for f in uf:
    c=f["properties"]["codarea"]
    if c in names:
        g=shape(f["geometry"]); D["nb"].append([c,path(g,0.6),names[c]]+[round(v) for v in P(*LL[c])])
# Brasil (CTA)
bs=unary_union([shape(f["geometry"]) for f in uf]); bx0,by0,bx1,by1=bs.bounds
C2=math.cos(math.radians(15)); k2=600/(by1-by0)
def P2(lon,lat): return (400+((lon-(bx0+bx1)/2)*C2)*k2, 360-(lat-(by0+by1)/2)*k2)
for f in uf: D["br"].append([f["properties"]["codarea"],path(shape(f["geometry"]),0.6,P2)])
json.dump(D,open(os.path.join(O,"map_data.json"),"w",encoding="utf-8"),ensure_ascii=False,separators=(",",":"))
print("k",round(k,1),"size",os.path.getsize(os.path.join(O,"map_data.json")),D["cities"])
