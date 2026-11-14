import os
# Gera img/brasil_mg.svg (Brasil cinza + MG destacado) e img/mg_pontos.svg (pontos amarelos). MG = contorno aproximado (sem GeoJSON de estados local).
import json, math, random
G = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "recursos", "mapas", "countries50m.geojson"), encoding="utf-8"))
br = next(f for f in G["features"] if any(str(v) in ("Brazil", "BRA") for v in f["properties"].values()))
MG = [(-46.0,-15.2),(-45.0,-14.9),(-44.2,-14.25),(-43.0,-14.6),(-41.9,-15.0),(-41.0,-15.7),(-40.3,-16.4),(-40.25,-17.5),(-40.9,-18.0),(-41.0,-19.0),(-41.5,-20.0),(-41.8,-20.8),(-42.3,-21.2),(-42.6,-21.9),(-43.5,-22.0),(-44.2,-22.4),(-44.8,-22.8),(-45.8,-22.8),(-46.5,-22.6),(-46.6,-21.8),(-47.2,-21.0),(-47.8,-20.4),(-48.7,-20.0),(-49.8,-19.9),(-50.9,-19.9),(-50.9,-19.4),(-50.0,-18.8),(-49.3,-18.6),(-48.5,-18.4),(-47.8,-17.6),(-47.3,-16.4),(-46.8,-16.0),(-46.3,-15.6)]
W = 900; L0, L1, T0, T1 = -74.5, -34.0, 5.6, -34.2
k = W / ((L1 - L0) * math.cos(math.radians(14)))
H = round((T0 - T1) * k)
def P(lo, la): return ((lo - L0) * math.cos(math.radians(14)) * k, (T0 - la) * k)
def path(ring): return "M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in (P(*c) for c in ring)) + "Z"
geom = br["geometry"]; polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
dbr = "".join(path(p[0]) for p in polys)
dmg = path(MG)
open("img/brasil_mg.svg", "w", encoding="utf-8").write(
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
    f'<path d="{dbr}" fill="#1c1c1e" stroke="#4a4a4e" stroke-width="2"/>'
    f'<path d="{dmg}" fill="#2a2a1c" stroke="#F5C518" stroke-width="3"/></svg>')
def inside(lo, la):
    c = False; n = len(MG)
    for i in range(n):
        x1, y1 = MG[i]; x2, y2 = MG[(i + 1) % n]
        if (y1 > la) != (y2 > la) and lo < (x2 - x1) * (la - y1) / (y2 - y1) + x1: c = not c
    return c
random.seed(6); dots = []
CID = [(-43.94,-19.92,1.0),(-48.28,-18.92,.5),(-44.0,-16.7,.4),(-43.2,-20.5,.5),(-47.9,-19.75,.4),(-42.0,-19.5,.35),(-45.5,-21.5,.5)]
while len(dots) < 260:
    lo, la = random.uniform(-51, -40.2), random.uniform(-22.9, -14.2)
    if not inside(lo, la): continue
    w = max(math.exp(-((lo-a)**2+(la-b)**2)/0.9)*s for a, b, s in CID)
    if random.random() > 0.18 + w: continue
    x, y = P(lo, la); dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{1.6 + 3.2*random.random()*(0.5+w):.1f}" fill="#F5C518" fill-opacity="{0.55+0.45*random.random():.2f}"/>')
open("img/mg_pontos.svg", "w", encoding="utf-8").write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">' + "".join(dots) + "</svg>")
cx, cy = P(-45.4, -18.6)
print(W, H, "centro MG %", round(cx / W * 100, 1), round(cy / H * 100, 1))
