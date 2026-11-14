r"""tex.py - texturas desenhadas em Pillow (zero IA): rostos 1024x578 (traco preto, mapeados nos 130 graus frontais
da cabeca), mostrador de relogio, rachadura e (opcional) placa de pedestal com texto.
Rostos: smile grin angry scared shock determined sleep yawn tired blink look_l look_r look_up frozen_yawn
Rosto novo que a historia pedir: acrescente um bloco  d = face("nome"); ...  abaixo (mesmo traco preto 9-17 px).
Uso:  python -X utf8 pipeline\tex.py PASTA [--placa "1996"]
Saida: PASTA\tex\face_*.png, dial.png, crack.png, plaque.png
"""
from PIL import Image, ImageDraw, ImageFont
import math, os, argparse
ap = argparse.ArgumentParser(); ap.add_argument("pasta"); ap.add_argument("--placa", default="")
A = ap.parse_args()
FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "Montserrat-ExtraBold.otf")
T = os.path.join(A.pasta, "tex"); os.makedirs(T, exist_ok=True)
Wd, Hd = 1024, 578
K = (0, 0, 0, 255)
def new(): return Image.new("RGBA", (Wd, Hd), (0, 0, 0, 0))
EX, EY = 92, 255   # eye offset x, eye y
def eye_dot(d, cx, cy, w=34, h=50):
    d.ellipse([cx-w/2, cy-h/2, cx+w/2, cy+h/2], fill=K)
    d.ellipse([cx-w/2+7, cy-h/2+8, cx-w/2+17, cy-h/2+19], fill=(255,255,255,255))
def eye_ring(d, cx, cy, r=34, p=11, dx=0, dy=0):
    d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(255,255,255,255), outline=K, width=10)
    d.ellipse([cx-p+dx, cy-p+dy, cx+p+dx, cy+p+dy], fill=K)
def closed(d, cx, cy, w=30, up=False):
    if up: d.arc([cx-w, cy-22, cx+w, cy+22], 200, 340, fill=K, width=12)
    else: d.arc([cx-w, cy-28, cx+w, cy+12], 20, 160, fill=K, width=12)
def mouth_smile(d, w=70, y=360): d.arc([512-w, y-55, 512+w, y+25], 20, 160, fill=K, width=12)
def mouth_flat(d, w=40, y=365): d.line([512-w, y, 512+w, y], fill=K, width=12)
def mouth_o(d, r=26, y=370): d.ellipse([512-r, y-r*1.2, 512+r, y+r*1.2], fill=K)
def mouth_yawn(d, y=375): d.ellipse([512-46, y-58, 512+46, y+58], fill=(70,10,10,255), outline=K, width=11); d.ellipse([512-24, y+12, 512+24, y+44], fill=(200,60,70,255))
def mouth_grin(d, y=350):
    d.chord([512-80, y-40, 512+80, y+70], 0, 180, fill=K)
    d.rectangle([512-60, y+15, 512+60, y+28], fill=(255,255,255,255))
def brows(d, ang, y=185, w=44):
    for s in (-1, 1):
        cx = 512 + s*EX; a = math.radians(ang)*s
        dx, dy = w*math.cos(a), w*math.sin(a)
        d.line([cx-dx, y+dy, cx+dx, y-dy], fill=K, width=13)
F = {}
def face(name):
    im = new(); d = ImageDraw.Draw(im); F[name] = im; return d
d = face("smile"); [eye_dot(d, 512+s*EX, EY) for s in (-1,1)]; mouth_smile(d)
d = face("grin"); [eye_dot(d, 512+s*EX, EY) for s in (-1,1)]; mouth_grin(d)
d = face("angry"); [eye_dot(d, 512+s*EX, EY+8, 32, 40) for s in (-1,1)]; brows(d, -22); mouth_flat(d)
d = face("scared"); [eye_ring(d, 512+s*EX, EY) for s in (-1,1)]; brows(d, 20, 175)
d.line([512-55,372,512-28,358,512,372,512+28,358,512+55,372], fill=K, width=11, joint="curve")
d = face("shock"); [eye_ring(d, 512+s*EX, EY, 38, 10) for s in (-1,1)]; brows(d, 12, 170); mouth_o(d)
d = face("determined"); [eye_dot(d, 512+s*EX, EY+10, 32, 38) for s in (-1,1)]; brows(d, -16, 200)
d.arc([512-60, 300, 512+70, 380], 30, 150, fill=K, width=12)
d = face("sleep"); [closed(d, 512+s*EX, EY) for s in (-1,1)]; d.arc([512-22, 350, 512+22, 380], 0, 180, fill=K, width=10)
d = face("yawn"); [closed(d, 512+s*EX, EY-5, up=True) for s in (-1,1)]; mouth_yawn(d)
d = face("tired"); [eye_ring(d, 512+s*EX, EY, 36, 9) for s in (-1,1)]
for s in (-1,1): d.arc([512+s*EX-36, EY+14, 512+s*EX+36, EY+62], 20, 160, fill=(90,70,110,255), width=9)
mouth_flat(d, 30, 380)
d = face("blink"); eye_dot(d, 512-EX, EY); closed(d, 512+EX, EY); mouth_smile(d, 60)
for nm, dx, dy in (("look_l", -14, 0), ("look_r", 14, 0), ("look_up", 0, -14)):
    d = face(nm); [eye_ring(d, 512+s*EX, EY, 32, 12, dx, dy) for s in (-1,1)]; mouth_flat(d, 26, 372)
d = face("frozen_yawn"); [eye_ring(d, 512+s*EX, EY, 30, 8) for s in (-1,1)]; mouth_yawn(d)
for n, im in F.items(): im.save(os.path.join(T, f"face_{n}.png"))
# clock dial
S = 512; im = Image.new("RGBA", (S, S), (0,0,0,0)); d = ImageDraw.Draw(im)
d.ellipse([6,6,S-6,S-6], fill=(250,248,240,255), outline=(20,20,20,255), width=22)
f = ImageFont.truetype(FONT, 58)
for h in range(1, 13):
    a = math.radians(h*30); x = S/2 + 185*math.sin(a); y = S/2 - 185*math.cos(a)
    d.text((x, y), str(h), font=f, fill=(20,20,20,255), anchor="mm")
im.save(os.path.join(T, "dial.png"))
# plaque (placa do pedestal, so se --placa)
if A.placa:
    im = Image.new("RGBA", (512, 256), (176,141,60,255)); d = ImageDraw.Draw(im)
    d.rectangle([8,8,503,247], outline=(90,66,20,255), width=14)
    fs = 150 if len(A.placa) <= 4 else max(50, int(600 / len(A.placa)))
    d.text((256,128), A.placa, font=ImageFont.truetype(FONT, fs), fill=(60,40,10,255), anchor="mm")
    im.save(os.path.join(T, "plaque.png"))
# crack decal
im = Image.new("RGBA", (512,512), (0,0,0,0)); d = ImageDraw.Draw(im)
import random; random.seed(3)
def br(x,y,a,l,w,dep):
    if dep==0 or l<15: return
    pts=[(x,y)]
    for _ in range(4):
        a += random.uniform(-0.6,0.6); x += math.cos(a)*l/4; y += math.sin(a)*l/4; pts.append((x,y))
    d.line(pts, fill=(25,25,25,255), width=w, joint="curve")
    br(x,y,a+random.uniform(0.3,0.9),l*0.6,max(4,w-4),dep-1); br(x,y,a-random.uniform(0.3,0.9),l*0.6,max(4,w-4),dep-1)
for k in range(5): br(256,256,k*1.26+0.3,170,16,3)
im.save(os.path.join(T, "crack.png"))
print("ok", len(F))
