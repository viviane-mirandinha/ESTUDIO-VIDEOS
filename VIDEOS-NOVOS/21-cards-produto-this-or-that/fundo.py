# Fundo papel off-white com rabiscos vermelhos (SVG determinístico) -> img/fundo.svg
import math, random, os
random.seed(21)
W, H = 1280, 720
o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
     '<defs><radialGradient id="g" cx="50%" cy="45%" r="75%"><stop offset="0" stop-color="#fbf8f3"/><stop offset="1" stop-color="#efe9e1"/></radialGradient>',
     '<filter id="n"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="4"/><feColorMatrix values="0 0 0 0 .45  0 0 0 0 .38  0 0 0 0 .32  0 0 0 .07 0"/></filter></defs>',
     f'<rect width="{W}" height="{H}" fill="url(#g)"/><rect width="{W}" height="{H}" filter="url(#n)"/>']
# linhas onduladas suaves (como o fundo da referência)
for i in range(16):
    x, y = random.uniform(-100, W), random.uniform(-100, H)
    a = random.uniform(0, 6.28); pts = []
    for s in range(9):
        pts.append((x, y)); a += random.uniform(-1.1, 1.1); x += 70 * math.cos(a); y += 70 * math.sin(a)
    d = f"M{pts[0][0]:.0f},{pts[0][1]:.0f} " + " ".join(f"Q{(pts[j][0]+pts[j+1][0])/2+random.uniform(-30,30):.0f},{(pts[j][1]+pts[j+1][1])/2+random.uniform(-30,30):.0f} {pts[j+1][0]:.0f},{pts[j+1][1]:.0f}" for j in range(len(pts)-1))
    o.append(f'<path d="{d}" fill="none" stroke="#d9a4a4" stroke-opacity=".45" stroke-width="5" stroke-linecap="round"/>')
def estrela(cx, cy, r, rot):
    p = []
    for k in range(10):
        rr = r if k % 2 == 0 else r * .45; t = rot + k * math.pi / 5
        p.append(f"{cx+rr*math.sin(t):.0f},{cy-rr*math.cos(t):.0f}")
    return f'<polygon points="{" ".join(p)}" fill="none" stroke="#b3202a" stroke-width="4" stroke-linejoin="round" opacity=".8"/>'
def coracao(cx, cy, s):
    return f'<path d="M{cx},{cy+s*.9} C{cx-s*1.4},{cy} {cx-s*.8},{cy-s*1.1} {cx},{cy-s*.35} C{cx+s*.8},{cy-s*1.1} {cx+s*1.4},{cy} {cx},{cy+s*.9}Z" fill="#c8102e" opacity=".85"/>'
for cx, cy, r, rot in [(70, 640, 34, .2), (1215, 655, 28, -.3), (95, 120, 22, .5), (1190, 300, 20, .1)]:
    o.append(estrela(cx, cy, r, rot))
for cx, cy, s in [(150, 690, 14), (1240, 140, 12), (40, 380, 11), (1150, 600, 10)]:
    o.append(coracao(cx, cy, s))
o.append('</svg>')
os.makedirs("img", exist_ok=True)
open("img/fundo.svg", "w", encoding="utf-8").write("\n".join(o))
print("ok")
