import os
import json,math
g=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "recursos", "mapas", "countries50m.geojson"),encoding="utf-8"))
print(list(g["features"][0]["properties"].keys())[:12])
L0,L1,B0,B1=-12,24,36,58; k=math.cos(math.radians(47))
sx=1280/((L1-L0)*k); sy=720/(B1-B0); s=min(sx,sy)
ox=(1280-(L1-L0)*k*s)/2
def P(lo,la): return (ox+(lo-L0)*k*s, (B1-la)*s)
out={"fra":"","oth":""}
for f in g["features"]:
    pr=f["properties"]; iso=pr.get("ADM0_A3")
    geom=f["geometry"]; polys=geom["coordinates"] if geom["type"]=="MultiPolygon" else [geom["coordinates"]]
    d=""
    for poly in polys:
        ring=poly[0]
        if not any(L0-5<lo<L1+5 and B0-5<la<B1+5 for lo,la in ring): continue
        if iso=="FRA" and all(lo<-20 or lo>45 for lo,la in ring): continue
        pts=[P(lo,la) for lo,la in ring[::2]]
        d+="M"+"L".join(f"{x:.0f},{y:.0f}" for x,y in pts)+"Z"
    if not d: continue
    out["fra" if iso=="FRA" else "oth"]+=d
px,py=P(2.35,48.86); out["paris"]=[round(px),round(py)]
for n,(lo,la) in {"lehavre":(0.1,49.5),"fos":(4.9,43.4),"donges":(-2.1,47.3)}.items(): out[n]=[round(v) for v in P(lo,la)]
json.dump(out,open("europa.json","w"),separators=(",",":"))
print(len(out["fra"]),len(out["oth"]),out["paris"])
