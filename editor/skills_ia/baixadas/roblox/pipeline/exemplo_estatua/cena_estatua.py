# cena_estatua.py - EXEMPLO COMPLETO (video aprovado 31/10/2026: "Nessa cidade, quem nao dorme vira estatua").
# Copie pra pasta do video novo como cena.py e troque cenarios / personagens / planos (@shot(indice_da_palavra)).
# Rodar:  BLENDER -b --factory-startup --python cena.py -- PASTA list|stills|frames [OUT|-] [f0 f1]
# Precisa em PASTA\tex: face_*.png, dial.png, crack.png e plaque.png (tex.py --placa 1996).
import os, sys
# acha o roblox_lib.py: variavel ROBLOX_PIPELINE (definida no SKILL.md) ou pasta vizinha
for _p in [os.environ.get("ROBLOX_PIPELINE", ""), os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."), os.path.dirname(os.path.abspath(__file__))]:
    if _p and os.path.exists(os.path.join(_p, "roblox_lib.py")): sys.path.insert(0, os.path.abspath(_p)); break
else:
    raise SystemExit("roblox_lib.py nao encontrado: defina ROBLOX_PIPELINE=<pasta da skill>/pipeline")
from roblox_lib import *

# STREET (0,0)
C = "street"
ground(C, 0, 20, 160, 140)
box(C + "_road", C, (0, 12, 0.02), (160, 8, 0.06), "#4A4D52")
for k in range(-8, 9): box(C + "_line", C, (k * 8, 12, 0.07), (3, 0.3, 0.02), "#F2E25A")
box(C + "_walk", C, (0, 6.5, 0.1), (160, 3, 0.2), "#D9D4CC")
box(C + "_walk2", C, (0, 17.5, 0.1), (160, 3, 0.2), "#D9D4CC")
HCOL = [("#F2F0EA", "#B8442F"), ("#BFD9F2", "#4A5A78"), ("#F7E3B5", "#8A3B2A"), ("#E6F2D9", "#5A4636"), ("#F2D0D0", "#5B5F6B")]
for i, x in enumerate(range(-32, 33, 16)):
    w, r_ = HCOL[i % 5]; house(C, x, 25, wall=w, roof=r_)
for i, x in enumerate(range(-24, 25, 16)):
    w, r_ = HCOL[(i + 2) % 5]; house(C, x, 42, wall=w, roof=r_, h=7)
for x in (-40, -8, 8, 40): tree(C, x, 20.5, 0.9)
tree(C, -14, 3, 1.0); tree(C, 18, 2, 1.1)
lamp_post(C, 8, 6)
# clock tower
box(C + "_tw", C, (0, 60, 14), (8, 8, 28), "#C9B79A"); box(C + "_twr", C, (0, 60, 29), (9, 9, 2), "#8A3B2A")
cone(C + "_twc", C, (0, 60, 33), (12, 12, 6), "#8A3B2A", rot=(0, 0, 45))
CLK_T, CLK_TH, CLK_TM = clock(C, (0, 55.7, 22), 3.0)
SUNDISC = obj("sundisc", M_SPH, C, (0, 120, -5), (14, 14, 14), (0, 0, 0), mat("#FFB347", emis=6.0, key="sundisc"))
NIGHTSKY_STARS = []
# stone boy (street)
STONEBOY = Char("stoneboy", C, "#F2C9A0", "#3BB54A", "#2B3A67", "short", "#5B3A1E")

# NEIGHBOR ROOM (100,0)  + phone kid
C = "neighbor"
box(C + "_floor", C, (100, 0, -0.25), (30, 30, 0.5), "#B07A4A", noise=0.1)
box(C + "_wallB", C, (100, 8, 6), (30, 0.5, 12), "#C7B3E6")
box(C + "_wallL", C, (90, 0, 6), (0.5, 30, 12), "#B9A2DA")
box(C + "_bed", C, (100, 3, 0.8), (6, 9, 1.6), "#7A4E2A"); box(C + "_matt", C, (100, 3, 1.9), (5.6, 8.6, 0.8), "#FFFFFF")
box(C + "_head", C, (100, 7.6, 2.8), (6, 0.5, 3.6), "#7A4E2A")
box(C + "_pillow", C, (100, 6.4, 2.5), (3.4, 1.6, 0.6), "#F5F5F5")
box(C + "_blanket", C, (100, 0.3, 2.35), (5.8, 4.6, 0.3), "#3E6FD8")
box(C + "_wwin", C, (104, 7.7, 7), (4, 0.2, 3.4), "#0E1630", emis=0.4); box(C + "_moon", C, (104.8, 7.6, 7.6), (0.8, 0.1, 0.8), "#F5F0C8", emis=3)
NEIGH = Char("neigh", C, "#E0AC7E", "#9B4DE0", "#9B4DE0", "long", "#5B3A1E")
AL_ROOT, AL_H, AL_M = clock(C, (100, 0, 3.4), 1.05, frame="#D8282E")
for s in (-1, 1): sph(C + "_bell", C, (s * 0.8, 0.2, 1.25), (0.65, 0.65, 0.65), "#E0B030", AL_ROOT)
BELLS = [o for o in COLL[C].objects if o.name.startswith(C + "_bell")]
ZS = []
def ztext(c, n):
    out = []
    for i in range(n):
        cu = bpy.data.curves.new(f"z{c}{i}", "FONT"); cu.body = "Z"; cu.align_x = "CENTER"; cu.extrude = 0.05
        o = bpy.data.objects.new(f"z{c}{i}", cu); coll(c).objects.link(o)
        o.data.materials.append(mat("#FFFFFF", emis=1.2, key="zmat")); o.rotation_euler = (R(90), 0, 0); out.append(o)
    return out
Z_NEIGH = ztext(C, 3)
C = "phonekid"
box(C + "_wall", C, (150, 6, 6), (20, 0.5, 14), "#26304F")
box(C + "_bed", C, (150, 2, 1), (8, 6, 2), "#3E6FD8")
PKID = Char("pkid", C, "#C68A5E", "#F2C230", "#2B3A67", "spiky", "#1A1A1A")
PHONE = empty(C + "_phone", C)
box(C + "_phb", C, (0, 0, 0), (0.7, 0.1, 1.2), "#111111", PHONE)
PHSCR = box(C + "_phs", C, (0, 0.06, 0), (0.6, 0.02, 1.05), "#9FD8FF", PHONE, emis=4.0)

# BAKERY (200,0)
C = "bakery"
box(C + "_floor", C, (200, 0, -0.25), (30, 30, 0.5), "#E8DCC8")
box(C + "_wallB", C, (200, 7, 6), (30, 0.5, 12), "#F2C8A0")
for z in (3.5, 6.5, 9.5):
    box(C + "_shelf", C, (200, 6.3, z), (14, 1.2, 0.3), "#7A4E2A")
    for k in range(6): sph(C + "_bread", C, (194.5 + k * 2.2, 6.3, z + 0.55), (1.8, 0.9, 0.8), "#C98A3A")
box(C + "_counter", C, (200, -1.8, 1.6), (12, 2.4, 3.2), "#8A5A30"); box(C + "_ctop", C, (200, -1.8, 3.3), (12.4, 2.8, 0.25), "#FFFFFF")
for k in range(4): sph(C + "_cb", C, (196 + k * 2.5, -2.2, 3.85), (1.6, 0.9, 0.7), "#D19A4A")
BAKER = Char("baker", C, "#F2C9A0", "#FFFFFF", "#444A55", "none", armcol="#FFFFFF")
BHAT = cyl(C + "_hat", C, (0, 0, 1.6), (1.3, 1.3, 1.0), "#FFFFFF", BAKER.neck); sph(C + "_hatt", C, (0, 0, 2.2), (1.9, 1.9, 1.1), "#FFFFFF", BAKER.neck)
BAG = sph(C + "_bag", C, (0, -0.2, -2.0), (0.6, 0.6, 2.6), "#C98A3A", BAKER.sh["R"])
Z_BAKER = ztext(C, 3)

# LEO ROOM (300,0)
C = "room"
box(C + "_floor", C, (300, 0, -0.25), (40, 40, 0.5), "#A8774E", noise=0.1)
box(C + "_rug", C, (300, -1, 0.02), (12, 8, 0.05), "#D84B4B")
box(C + "_wallB", C, (300, 9, 7), (40, 0.5, 14), "#5C8FD6")
box(C + "_wallR", C, (314, 0, 7), (0.5, 40, 14), "#4F7FC4")
box(C + "_wallL", C, (286, 0, 7), (0.5, 40, 14), "#4F7FC4")
# window on back wall
box(C + "_winf", C, (306, 8.7, 7), (6.4, 0.3, 5.2), "#FFFFFF")
ROOMWIN = box(C + "_win", C, (306, 8.55, 7), (5.6, 0.2, 4.4), "#9CC8FF", emis=1.0, key="roomwin")
box(C + "_winx", C, (306, 8.4, 7), (0.2, 0.1, 4.4), "#FFFFFF"); box(C + "_winy", C, (306, 8.4, 7), (5.6, 0.1, 0.2), "#FFFFFF")
# sofa facing -Y? sofa at back, facing camera (-Y); TV at front (y=-8) facing +Y
box(C + "_sofa", C, (300, 4, 0.9), (8, 3.2, 1.8), "#E07A2E"); box(C + "_sofab", C, (300, 5.4, 2.6), (8, 0.8, 3.0), "#D06A22")
box(C + "_sofaa", C, (295.6, 4, 1.6), (0.9, 3.2, 2.2), "#D06A22"); box(C + "_sofaa", C, (304.4, 4, 1.6), (0.9, 3.2, 2.2), "#D06A22")
box(C + "_stand", C, (300, -9, 1.0), (7, 2, 2.0), "#5A3A22")
box(C + "_tv", C, (300, -9, 4.4), (8, 0.5, 4.6), "#111111")
TVSCR = box(C + "_tvs", C, (300, -8.72, 4.4), (7.4, 0.1, 4.0), "#55AAFF", emis=2.5, key="tvscr")
box(C + "_cons", C, (298, -9, 2.2), (2.2, 1.4, 0.5), "#EEEEEE")
RC_ROOT, RC_H, RC_M = clock(C, (293, 8.6, 9), 1.6)
LEO = Char("leo", "leo", "#F2C9A0", "#3E7BD8", "#3E7BD8", "none", nose=True, cap="#D8282E", shoes="#FFFFFF")
# pajama stripes on torso
CTRL = box("leo_ctrl", "leo", (0, -1.9, 1.3), (2.3, 0.7, 0.45), "#2A2A2A", LEO.body)
for s in (-1, 1): box("leo_ctrlb", "leo", (s * 0.6, -0.05, 0.25), (0.2, 0.2, 0.12), "#E33" if s < 0 else "#3C3", CTRL) if False else None
LEO.prop("ctrl", CTRL)
THUMB = box("leo_thumb", "leo", (0.3, -0.1, 0.62), (0.14, 0.55, 0.4), "#F2C9A0", CTRL); LEO.prop("thumb", THUMB)
CROWN = empty("leo_crown", "leo", (0, 0, 1.55), LEO.neck)
cyl("leo_crb", "leo", (0, 0, 0), (1.4, 1.4, 0.45), "#F2C230", CROWN)
for k in range(6):
    a = k * 60; cone("leo_crs", "leo", (0.62 * math.sin(R(a)), -0.62 * math.cos(R(a)), 0.45), (0.4, 0.4, 0.5), "#F2C230", CROWN)
NEST = empty("leo_nest", "leo", (0, 0, 1.85), LEO.neck)
for k in range(14):
    a = k * 360 / 14
    box("leo_twig", "leo", (0.75 * math.cos(R(a)), 0.75 * math.sin(R(a)), 0.12 * (k % 2)), (0.95, 0.16, 0.16), "#6B4423", NEST, rot=(0, (k % 3) * 8, a + 90))
cyl("leo_nestb", "leo", (0, 0, -0.05), (1.5, 1.5, 0.2), "#7A5230", NEST)
EGG = sph("leo_egg", "leo", (0.15, 0.1, 0.25), (0.42, 0.42, 0.55), "#F4F1E6", NEST)
# pigeon
C = "pigeon"
PIG = empty("pig", C)
sph("pig_b", C, (0, 0.2, 0), (0.9, 1.4, 0.8), "#8C93A3", PIG); sph("pig_h", C, (0, -0.6, 0.55), (0.6, 0.6, 0.6), "#6E7A8F", PIG)
cone("pig_k", C, (0, -0.95, 0.5), (0.18, 0.18, 0.35), "#E8A030", PIG, rot=(90, 0, 0))
for s in (-1, 1): sph("pig_e", C, (s * 0.2, -0.82, 0.68), (0.13,) * 3, "#111111", PIG)
PIGW = []
for s in (-1, 1):
    wp = empty("pig_wp", C, (s * 0.4, 0.2, 0.2), PIG)
    box("pig_w", C, (s * 0.6, 0.1, 0), (1.2, 1.1, 0.12), "#7C8495", wp); PIGW.append((s, wp))
box("pig_t", C, (0, 1.0, 0.1), (0.6, 0.7, 0.12), "#6E7A8F", PIG, rot=(-20, 0, 0))

# PLAZA (500,0)
C = "plaza"
ground(C, 500, 20, 200, 160)
PAVE = mat_two("#D8B07A", "#CFA56E", 4, "pave")
box(C + "_pave", C, (500, 18, 0.02), (90, 60, 0.06), "#CFC8B8") ; COLL[C].objects[C + "_pave"].material_slots[0].material = PAVE
for i, x in enumerate(range(-40, 41, 16)):
    w, r_ = HCOL[i % 5]; house(C, 500 + x, 58, wall=w, roof=r_, h=7)
for x in (-46, 46): tree(C, 500 + x, 30, 1.1); tree(C, 500 + x, 8, 1.0)
PED_LEO = box(C + "_pedL", C, (500, 0, 0.75), (3.2, 3.2, 1.5), "#B8B2A6")
# old statue (dad)
PED_DAD = box(C + "_pedD", C, (500, 32, 1.6), (4, 4, 3.2), "#A8A296")
box(C + "_pedDt", C, (500, 32, 3.3), (4.4, 4.4, 0.3), "#9A9488")
PLAQ = obj(C + "_plaq", M_PLANE, C, (500, 29.96, 1.7), (2.4, 1, 1.2), (0, 0, 0), mat_img(os.path.join(TEX, "plaque.png"), "plaqm", 0.3, alpha=False))
DAD = Char("dad", "dad", "#F2C9A0", "#3BB54A", "#3BB54A", "none", nose=True, cap="#2E7BE8", shoes="#FFFFFF")
DCTRL = box("dad_ctrl", "dad", (0, -1.9, 1.3), (2.6, 1.0, 0.7), "#6A6A6A", DAD.body); DAD.prop("ctrl", DCTRL)
box("dad_cbtn", "dad", (0.5, -0.05, 0.4), (0.3, 0.3, 0.15), "#AA2222", DCTRL);
MOSSO = []
random.seed(11)
for k in range(26):
    tgt = random.choice(["torso", "torso", "legL", "legR", "armL", "armR", "head"])
    p = DAD.parts[tgt]
    lx = random.uniform(-0.45, 0.45); lz = random.uniform(-0.45, 0.45)
    o = obj("dad_moss", M_SPH, "dad", (lx, -0.5, lz), (0.32, 0.12, 0.32), (0, 0, 0), MOSS)
    o.parent = p; o.scale = (0.32 / p.scale[0] * random.uniform(0.7, 1.6), 0.25, 0.32 / p.scale[2] * random.uniform(0.7, 1.6)); MOSSO.append(o)
for k in range(10):
    o = sph("dad_moss2", "dad", (random.uniform(-1, 1), random.uniform(-0.3, 0.3), random.uniform(0.2, 1.8)), (0.5, 0.5, 0.35), "#4E8A2A", DAD.body); MOSSO.append(o)
# crowd of kid statues
CROWD = []
random.seed(5)
slots = []
for row in range(6):
    for colx in range(9):
        x = 500 + (colx - 4) * 7.5 + random.uniform(-1.2, 1.2) + (3.7 if row % 2 else 0)
        y = 8 + row * 7.0 + random.uniform(-1, 1)
        if abs(x - 500) < 7 and y > 22: continue  # keep space around old statue
        if abs(x - 500) < 4 and y < 12: continue  # space around leo
        if abs(x - 500) < 5: continue
        slots.append((x, y))
random.shuffle(slots)
HSTY = ["short", "spiky", "bun", "long", "afro", "none"]
for i, (x, y) in enumerate(slots[:46]):
    hs = HSTY[i % 6]
    ch = Char(f"k{i}", "crowd", random.choice(SKINS), random.choice(SHIRTS), random.choice(PANTS), hs, random.choice(HAIRS),
              cap=random.choice(SHIRTS) if hs == "none" else None)
    ped = box(f"k{i}_ped", "crowd", (x, y, 0.3), (3.0, 3.0, 0.6), "#B8B2A6")
    ch.place((x, y, 0.6), random.uniform(-15, 15))
    kind = random.choice(["ctrl", "phone", "book", "ctrl"])
    if kind == "ctrl": pr = box(f"k{i}_p", "crowd", (0, -1.9, 1.3), (2.2, 0.7, 0.45), "#2A2A2A", ch.body)
    elif kind == "phone": pr = box(f"k{i}_p", "crowd", (1.5, -1.95, 1.6), (0.7, 0.15, 1.2), "#111111", ch.body)
    else: pr = box(f"k{i}_p", "crowd", (0, -1.9, 1.4), (2.0, 1.4, 0.35), random.choice(["#C0392B", "#2980B9", "#27AE60"]), ch.body, rot=(-30, 0, 0))
    ch.prop("p", pr); ch.kind = kind; ch.ped = ped
    ch.base_yaw = ch.pose["yaw"]; ch.dist = 0
    CROWD.append(ch)


def street_base(night_=False):
    STONEBOY.place((2, 6.6, 0.2), -10); STONEBOY.stone(True); STONEBOY.face("frozen_yawn")
    STONEBOY.pose.update(aL=-20, aR=-160, sR=10, hp=10)

def reset_all():
    for ch in [STONEBOY, NEIGH, PKID, BAKER, LEO, DAD] + CROWD:
        ch.reset()
    LEO.stone(False); DAD.stone(False); hide(CROWN); hide(NEST); EGG.hide_render = True
    hide(CTRL); THUMB.hide_render = True; hide(DCTRL, False)
    for o in MOSSO: o.hide_render = False
    PUFFS.clear(); CRACKEV.clear()
    set_pt((0, 0, -100), e=0); set_pt2((0, 0, -100), e=0)
    ROOMWIN.material_slots[0].material.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 0.12
    for z in Z_NEIGH + Z_BAKER: z.location = (0, 0, -50)

def zzz(zs, t, base, ph=0):
    for k, z in enumerate(zs):
        u = ((t * 0.7 + k / 3 + ph) % 1.0)
        z.location = Vector(base) + Vector((0.6 * u + 0.3 * math.sin(u * 6), 0, 2.2 * u))
        s = 0.9 * math.sin(u * math.pi) + 0.1; z.scale = (s, s, s)

# S1: wide street, stone boy on sidewalk
@shot(0)
def s1(t, lt):
    show_colls(["street"]); day(); street_base()
    set_cam(push((7, -6, 4.0), (2, 6.6, 3.5), 1.4, lt / 0.8), (1.0, 10, 4.2), 62)

@shot(2)
def s2(t, lt):
    show_colls(["phonekid"]); night()
    PKID.place((150, 2, 0.3), 0); PKID.face("tired"); PKID.pose.update(aR=-80, aL=-20, sit=True)
    PHONE.parent = PKID.body; PHONE.location = (0.5, -2.2, 1.6); PHONE.rotation_euler = (R(-15), 0, R(15))
    set_pt((150.4, -0.6, 4.3), "#9FD8FF", 450 + 80 * math.sin(t * 25)); set_pt2((146, -4, 8), "#6070C0", 500)
    set_cam(push((150.9, -2.6, 5.2), (150, 2, 4.85), 0.8, lt / 0.9), (150.1, 2, 4.85), 36)

@shot(6)
def s3(t, lt):
    show_colls(["street"]); day(); street_base()
    set_cam(push((3.2, -0.6, 5.0), (2, 6.6, 4.6), 0.8, lt / 1.0), (2.1, 6.6, 4.4), 40)

@shot(9)
def s4(t, lt):
    show_colls(["street"]); day(); street_base()
    tb = T(12)
    mins = snapv(t, tb, 59, 60, 0.12, 0.05); hrs = 8 if t < tb else 9
    set_clock(CLK_TH, CLK_TM, hrs if mins < 60 else 9, mins % 60 if mins < 60 else 0)
    if t >= tb - 0.05: set_clock(CLK_TH, CLK_TM, 9, 0)
    else: set_clock(CLK_TH, CLK_TM, 8, 59 + 0.0)
    shake = 0.12 * math.sin((t - tb) * 60) * math.exp(-(t - tb) * 6) if t > tb else 0
    set_cam(push((1.2 + shake, 44, 21), (0, 55.7, 22), 1.0, lt / 1.4), (0, 55.7, 22), 40)

@shot(15)
def s5(t, lt):
    show_colls(["street"]); night(); set_sky("#2A3A70", "#0A1430", 1.6); street_base()
    order = sorted(range(len(WINDOWS)), key=lambda k: (WINDOWS[k].location.x, -WINDOWS[k].location.z))
    t0, t1 = T(15) + 0.05, T(17) + 0.35
    for r_, k in enumerate(order):
        tk = t0 + (t1 - t0) * r_ / max(1, len(order) - 1)
        win_light(WINDOWS[k], t < tk)
    set_pt((0, 0, -100), e=0)
    set_cam(push((0, -16, 7), (0, 30, 6), 1.4, lt / 0.95), (0, 30, 7), 66)

@shot(18)
def s6(t, lt):
    show_colls(["neighbor"]); night(); set_sky("#2A3560", "#101830", 1.0)
    NEIGH.pose.update(lie=True); NEIGH.place((100, 1.0, 2.8), 0); NEIGH.face("sleep")
    NEIGH.pose.update(aL=-95, aR=-95, sL=-28, sR=-28)
    AL_ROOT.location = (100, 3.2, 4.3); AL_ROOT.rotation_euler = (R(-55), 0, 0)
    set_clock(AL_H, AL_M, 9, 0)
    NEIGH.pose["bob"] = 0.06 * math.sin(t * 3)
    zzz(Z_NEIGH, t, (101.5, 6.0, 4.5))
    set_pt((96, -2, 9), "#FFC27A", 1400); set_pt2((104, 6, 8), "#8FA8FF", 300)
    if t < T(21) - 0.04:
        set_cam(push((100, -8.5, 14.5), (100, 3, 3), 1.3, lt / 1.2), (100, 3.4, 3.2), 56)
    else:
        set_cam(push((101.4, -2.6, 10.6), (100, 4.2, 3.8), 0.8, (t - T(21)) / 1.0), (100, 4.4, 3.6), 46)

@shot(24)
def s7(t, lt):
    show_colls(["bakery"]); day(0.9)
    BAKER.place((200, 0.6, 0), 0); BAKER.face("sleep")
    nod = 6 + 5 * math.sin(t * 2.8)
    BAKER.pose.update(hp=-nod, aR=-35, aL=-5, lean=-3)
    BAG.rotation_euler = (R(60), 0, 0); BAG.location = (0, -0.6, -2.0)
    zzz(Z_BAKER, t, (201.2, -0.5, 6.2))
    set_pt((200, -8, 10), "#FFE2B0", 2500)
    set_cam(push((201.5, -9.5, 6.6), (200, 0.6, 5.2), 1.2, lt / 1.8), (200.2, 0.6, 5.0), 46)

@shot(30)
def s8(t, lt):
    show_colls(["room", "leo"]); night(); set_sky("#2A3560", "#101830", 1.0)
    LEO.place((300, 1.2, 0), 0)
    tw = T(35)
    a = snapv(t, tw, -10, -165); b = snapv(t, tw, -10, -60)
    LEO.pose.update(aR=a, aL=b, sL=snapv(t, tw, 0, 20), hr=snapv(t, tw, 0, -8))
    LEO.face("smile" if t < tw - 0.07 else "grin")
    idle(LEO, t)
    TVSCR.material_slots[0].material.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 2.5
    set_pt((300, -6, 5), "#7FB8FF", 600); set_pt2((297, -3, 10), "#FFC27A", 1800)
    set_cam(push((300.8, -8.0, 5.4), (300, 1.2, 4.6), 1.0, lt / 1.0), (300, 1.2, 4.6), 46)

def tv_flash(t):
    cols = ["#55AAFF", "#FF5A8A", "#7CFF6B", "#FFD84A"]
    k = int(t * 6) % 4
    b = TVSCR.material_slots[0].material.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = hexc(cols[k]); b.inputs["Emission Color"].default_value = hexc(cols[k])
    b.inputs["Emission Strength"].default_value = 2.5 + 0.8 * math.sin(t * 30)
    return cols[k]

def leo_on_sofa(t, arms=-70):
    LEO.place((300, 3.6, 1.8 - 2 + 0.0), 0); LEO.pose.update(sit=True)
    LEO.root.location.z = 0.1
    LEO.pose.update(aL=arms, aR=arms)
    hide(CTRL, False); THUMB.hide_render = False
    a = R(arms)
    CTRL.location = (0, 2 * math.sin(a) - 0.25, 2 - 2 * math.cos(a) + 0.15); CTRL.rotation_euler = (a + R(70), 0, 0)

@shot(36)
def s9(t, lt):
    show_colls(["room", "leo"]); night(); set_sky("#2A3560", "#101830", 1.0)
    tw = T(39)
    leo_on_sofa(t, snapv(t, tw, -75, -150)); hide(CROWN, False)
    LEO.face("grin"); idle(LEO, t, 0.05)
    c = tv_flash(t)
    set_pt((300, -5, 5), c, 900); set_pt2((297, -3, 10), "#FFC27A", 1400)
    set_cam(push((307, -6.5, 7.5), (300, 3, 4), 1.2, lt / 1.1), (300.5, 0, 4.3), 54)

@shot(40)
def s10(t, lt):
    show_colls(["room", "leo"]); night(); set_sky("#2A3560", "#101830", 1.0)
    leo_on_sofa(t, -72); LEO.face("determined" if t > T(43) - 0.07 else "smile"); idle(LEO, t, 0.03)
    LEO.pose["hy"] = 4 * math.sin(t * 2)
    c = tv_flash(t)
    set_pt((300, -1.5, 4.8), c, 300); set_pt2((299, -1.5, 7.5), "#FFC27A", 700)
    set_cam(push((300.5, -3.4, 5.0), (300, 3.6, 4.4), 0.6, lt / 1.9), (300, 3.6, 4.2), 40)

@shot(47)
def s11(t, lt):
    show_colls(["room"]); night(); set_sky("#2A3560", "#101830", 1.0)
    # minute hand jumps each word
    m = 0
    for k, wi in enumerate((47, 48, 49)):
        if t >= T(wi) - 0.05: m = k + 1
    set_clock(RC_H, RC_M, 3, m * 5 - 5 if m else 55)
    if m == 0: set_clock(RC_H, RC_M, 2, 55)
    set_pt((293, 2, 9), "#7FB8FF", 600); set_pt2((290, 4, 11), "#FFC27A", 200)
    set_cam(push((293.3, 3.5, 9.1), (293, 8.6, 9), 0.6, lt / 0.95), (293, 8.6, 9), 40)

@shot(50)
def s12(t, lt):
    show_colls(["street"]); day(); street_base()
    u = smooth(lt / 1.05)
    set_sky(("#FFB070"), "#5A7FD0", 0.9); set_sun(1.5 + 2.0 * u, 8 + 14 * u, 180, "#FFC48A")
    SUNDISC.location = (14, 110, 2 + 22 * u)
    for o in WINDOWS: win_light(o, False)
    set_cam(push((0, -4, 3), (0, 60, 8), 1.0, lt / 1.05), (5, 60, 12), 62)

def leo_close_base(t):
    show_colls(["room", "leo", "fx"]); day(); set_sky("#FFD7A8", "#6A9AE8", 1.0); set_sun(3.0, 25, 160, "#FFD4A0")
    ROOMWIN.material_slots[0].material.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 3.0
    set_pt((306, 6, 8), "#FFD4A0", 1500)
    TVSCR.material_slots[0].material.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 1.0
    leo_on_sofa(t, -72)

@shot(54)
def s13(t, lt):
    leo_close_base(t); LEO.face("shock")
    tw = T(54)
    if t >= tw - 0.02: LEO.stone(True, ["thumb"])
    # world pos of thumb
    bpy.context.view_layer.update()
    tp = THUMB.matrix_world.translation.copy()
    CRACKEV.append((tw, CTRL, (0.15, -0.52, 0), 0.7, 10))
    PUFFS.append((tw, tp + Vector((0.2, -0.5, 0.3)), 0.22, True, False))
    tremble = 0.02 * math.sin(t * 50)
    set_cam(push(tp + Vector((1.3 + tremble, -3.4, 2.2)), tp, 0.5, lt / 1.4), tp + Vector((-0.3, 0, 0.2)), 36)

def stone_hits(t):
    if t >= T(54): LEO.stone(True, ["thumb"])
    if t >= T(62) - 0.02: LEO.stone(True, ["armR", "handR"])
    if t >= T(64) - 0.02: LEO.stone(True, ["legR", "shoeR"])
    if t >= T(66) - 0.02: LEO.stone(True, ["nose"])

@shot(59)
def s14a(t, lt):
    leo_close_base(t); LEO.face("scared"); stone_hits(t)
    bpy.context.view_layer.update()
    ap = LEO.parts["armR"].matrix_world.translation.copy()
    for wi in (59, 60): CRACKEV.append((T(wi), LEO.parts["armR"], (0, -0.51, 0.25 - 0.5 * (wi - 59)), 0.9, 25 * (wi - 59)))
    PUFFS.append((T(62), ap + Vector((0.6, -0.9, 0.5)), 0.3, True, False))
    set_cam(push(ap + Vector((2.6, -4.6, 1.2)), ap, 0.5, lt / 1.0), ap + Vector((0, 0, 0.2)), 40)

@shot(63)
def s14b(t, lt):
    leo_close_base(t); LEO.face("scared"); stone_hits(t)
    bpy.context.view_layer.update()
    lp = LEO.parts["legR"].matrix_world.translation.copy()
    CRACKEV.append((T(64), LEO.parts["legR"], (0, -0.51, 0.0), 0.9, 40))
    PUFFS.append((T(64), lp + Vector((0.7, -0.8, 0.8)), 0.3, True, False))
    set_cam(push(lp + Vector((1.4, -5.0, 1.6)), lp, 0.5, lt / 0.4), lp + Vector((0, 0, 0.5)), 40)

@shot(65)
def s14c(t, lt):
    leo_close_base(t); LEO.face("scared" if t < T(66) else "shock"); stone_hits(t)
    bpy.context.view_layer.update()
    hp_ = LEO.parts["head"].matrix_world.translation.copy()
    PUFFS.append((T(66), hp_ + Vector((0.5, -0.9, -0.2)), 0.22, True, False))
    CRACKEV.append((T(66), LEO.parts["head"], (0.22, -0.64, 0.2), 0.5, -30))
    set_cam(push(hp_ + Vector((0.6, -4.4, 0.3)), hp_, 0.4, lt / 0.7), hp_ + Vector((0, 0, -0.3)), 38)

def leo_statue(t, face="shock", stone=True):
    LEO.place((500, 0, 1.5), 0); LEO.stone(stone); LEO.face(face)
    LEO.pose.update(aL=-72, aR=-72); hide(CTRL, False); THUMB.hide_render = False
    a = R(-72); CTRL.location = (0, 2 * math.sin(a) - 0.25, 2 - 2 * math.cos(a) + 0.15); CTRL.rotation_euler = (a + R(70), 0, 0)

def dad_statue(face="sleep", stone=True, moss=True):
    DAD.place((500, 32, 3.45), 0); DAD.stone(stone); DAD.face(face)
    DAD.pose.update(aL=-70, aR=-70)
    a = R(-70); DCTRL.location = (0, 2 * math.sin(a) - 0.3, 2 - 2 * math.cos(a) + 0.15); DCTRL.rotation_euler = (a + R(70), 0, 0)
    for o in MOSSO: o.hide_render = not moss
    if stone:
        for o in DAD.parts.values(): o.material_slots[0].material = STONE_D
        DCTRL.material_slots[0].material = STONE_D

def crowd_stone(on=True, face="frozen_yawn"):
    for ch in CROWD:
        ch.stone(on); ch.face(face)
        a = -70 if ch.kind != "phone" else -10
        ch.pose.update(aL=a, aR=-80 if ch.kind == "phone" else a, yaw=ch.base_yaw)

def plaza(t, extra=()):
    show_colls(["plaza", "leo", "dad", "crowd", "fx"] + list(extra)); day()
    crowd_stone(True); dad_statue()

@shot(67)
def s15(t, lt):
    plaza(t); leo_statue(t, "shock")
    PUFFS.append((T(67), (500, -0.6, 5.0), 2.2, False, True))
    set_cam(push((505, -11, 6.5), (500, 0, 5), 1.4, lt / 2.1), (500, 0, 5.2), 52)

@shot(74)
def s16a(t, lt):
    plaza(t); leo_statue(t, "look_r")
    u = smooth(lt / 2.6)
    x = lerp(478, 492, u)
    set_cam((x, -6, 7), (x + 6, 22, 3.5), 58)

@shot(79)
def s16b(t, lt):
    plaza(t); leo_statue(t, "look_r")
    u = lt / 1.3
    x = lerp(505, 515, u)
    set_cam((x, -3, 3.8), (x + 10, 14, 3.2), 50)

def leo_head_pos():
    bpy.context.view_layer.update(); return LEO.parts["head"].matrix_world.translation.copy()

@shot(83)
def s17(t, lt):
    plaza(t, ["pigeon"]); leo_statue(t, "look_up" if t > T(85) - 0.05 else "look_r")
    hp_ = leo_head_pos()
    land = T(85) + 0.1
    u = min(1, (t - cut(83)) / (land - cut(83)))
    top = hp_ + Vector((0, 0, 0.95))
    PIG.location = top + Vector((2.5 * (1 - u), -0.6 * (1 - u), 3.5 * (1 - u) ** 1.5))
    PIG.rotation_euler = (0, 0, R(-25 * (1 - u)))
    PIG.scale = (0.75,) * 3
    flap = 40 * math.sin(t * 40) if u < 1 else 0
    for s_, wp in PIGW: wp.rotation_euler = (0, R(s_ * flap), 0)
    set_cam(push(hp_ + Vector((1.4, -6.4, 1.4)), hp_, 0.6, lt / 1.6), hp_ + Vector((0, 0, 1.3)), 46)

@shot(89)
def s18(t, lt):
    plaza(t, ["pigeon"]); leo_statue(t, "look_up")
    hide(NEST, False); hp_ = leo_head_pos()
    NEST.scale = (snapv(t, T(90), 0.5, 1.0, 0.16),) * 3
    PIG.location = hp_ + Vector((0, 0.3, 1.55 + 0.04 * math.sin(t * 12))); PIG.scale = (0.75,) * 3; PIG.rotation_euler = (0, 0, R(-20))
    egg_t = T(92)
    if t >= egg_t - 0.05:
        PIG.location = hp_ + Vector((1.4, 0.4, 1.5)); PIG.rotation_euler = (0, 0, R(-60))
        EGG.hide_render = False; EGG.scale = Vector((0.42, 0.42, 0.55)) * snapv(t, egg_t, 0.01, 1.0, 0.14, 0.05)
        PUFFS.append((egg_t, hp_ + Vector((0.1, -0.5, 1.3)), 0.35, False, True))
    for s_, wp in PIGW: wp.rotation_euler = (0, 0, 0)
    set_cam(push(hp_ + Vector((0.8, -3.6, 2.6)), hp_ + Vector((0, 0, 0.9)), 0.4, lt / 1.0), hp_ + Vector((0, 0, 1.1)), 38)

def leo_full_nest(t):
    hide(NEST, False); EGG.hide_render = False; EGG.scale = (0.42, 0.42, 0.55)
    hp_ = leo_head_pos(); PIG.location = hp_ + Vector((0.3, 0.3, 1.6)); PIG.scale = (0.75,) * 3; PIG.rotation_euler = (0, 0, R(-30))
    for s_, wp in PIGW: wp.rotation_euler = (0, 0, 0)
    return hp_

@shot(93)
def s19a(t, lt):
    plaza(t, ["pigeon"]); leo_statue(t, "look_r" if t < T(95) else "look_l"); hp_ = leo_full_nest(t)
    set_cam(push(hp_ + Vector((-0.3, -4.8, 0.6)), hp_, 0.4, lt / 0.8), hp_ + Vector((0, 0, 0.1)), 40)

@shot(98)
def s19b(t, lt):
    plaza(t, ["pigeon"]); leo_statue(t, "look_l"); leo_full_nest(t)
    set_cam(push((500, 14, 6.0), (500, 32, 7.5), 1.2, lt / 1.3), (500, 32, 6.8), 58)

@shot(102)
def s20a(t, lt):
    plaza(t); leo_statue(t)
    set_cam(push((502.4, 24.6, 7.4), (500, 32, 6.5), 0.8, lt / 0.85), (500.2, 32, 6.4), 44)

@shot(105)
def s20b(t, lt):
    plaza(t); leo_statue(t)
    bpy.context.view_layer.update(); cp = DCTRL.matrix_world.translation.copy()
    set_cam(push(cp + Vector((1.2, -4.6, 2.0)), cp, 0.6, lt / 1.2), cp + Vector((0, 0, 0.4)), 40)

@shot(108)
def s21a(t, lt):
    plaza(t); leo_statue(t)
    set_cam(push((500.6, 24.5, 2.0), (500, 32, 4.6), 0.5, lt / 0.7), (500, 32, 4.6), 56)

@shot(112)
def s21b(t, lt):
    plaza(t, ["pigeon"]); leo_statue(t, "shock"); hp_ = leo_full_nest(t)
    set_cam(push(hp_ + Vector((0.2, -4.6, 0.4)), hp_, 0.5, lt / 0.9), hp_ + Vector((0, 0, 0.2)), 40)

def dad_head():
    bpy.context.view_layer.update(); return DAD.parts["head"].matrix_world.translation.copy()

@shot(115)
def s22(t, lt):
    plaza(t)
    f = "sleep"
    if t >= T(117) - 0.07: f = "blink"
    if t >= T(119) + 0.05: f = "sleep"
    if t >= T(121) - 0.07: f = "yawn"
    dad_statue(f); hp_ = dad_head()
    PUFFS.append((T(115), hp_ + Vector((0, -1.2, 0)), 1.0, False, True))
    set_cam(push(hp_ + Vector((0.3, -5.2, 0.3)), hp_, 0.6, lt / 1.8), hp_ + Vector((0, 0, 0.0)), 40)

@shot(122)
def s23(t, lt):
    plaza(t, ["pigeon"]); leo_statue(t, "yawn" if t >= T(123) - 0.07 else "look_l"); hp_ = leo_full_nest(t)
    LEO.pose["hp"] = snapv(t, T(123), 0, -8, 0.16)
    set_cam(push(hp_ + Vector((-0.4, -4.6, 0.4)), hp_, 0.5, lt / 1.3), hp_ + Vector((0, 0, 0.2)), 40)

@shot(125)
def s24a(t, lt):
    plaza(t, ["pigeon"]); tw = T(125)
    stone = t < tw - 0.03
    leo_statue(t, "shock" if not stone else "yawn", stone); leo_full_nest(t)
    if not stone:
        LEO.pose.update(aL=snapv(t, tw, -72, -150), aR=snapv(t, tw, -72, -150)); hide(CTRL); THUMB.hide_render = True
    PUFFS.append((tw, (500, -0.8, 4.4), 2.8, False, True))
    PUFFS.append((tw + 0.08, (500, -0.8, 2.6), 2.2, True, False))
    set_cam(push((504, -10.5, 6.0), (500, 0, 4.8), 1.0, lt / 1.0), (500, 0, 5.0), 52)

@shot(129)
def s24b(t, lt):
    plaza(t, ["pigeon"])
    LEO.place((498.3, 12, 0), 90); LEO.stone(False); LEO.face("smile")
    dad_statue("smile", False, False); DAD.place((501.7, 12, 0), -90)
    tw = T(131)
    LEO.pose.update(aL=snapv(t, tw, -10, -160), aR=-10); DAD.pose.update(aR=snapv(t, tw, -10, -160), aL=-10)
    LEO.face("grin" if t > tw - 0.07 else "smile"); DAD.face("grin" if t > tw - 0.07 else "smile")
    hide(DCTRL); idle(LEO, t, 0.05); idle(DAD, t, 0.05, 1)
    hp_ = leo_full_nest(t)
    set_cam(push((500, -6.5, 6.0), (500, 12, 3.8), 1.0, lt / 1.6), (500, 12, 3.6), 54)

def awake_pair():
    LEO.place((497.2, 12, 0), 0); LEO.stone(False); dad_statue("smile", False, False); DAD.place((502.8, 12, 0), 0)
    hide(DCTRL); leo_full_nest(0)

@shot(134)
def s25(t, lt):
    plaza(t, ["pigeon"]); awake_pair(); LEO.face("smile"); DAD.face("smile")
    order = sorted(CROWD, key=lambda c: c.root.location.x)
    for k, ch in enumerate(order):
        tk = T(134) + 0.05 + k * 0.035
        ch.face("yawn" if t >= tk else "sleep")
        if t >= tk: ch.pose["hp"] = -8
    u = smooth(lt / 2.1)
    set_cam(push((500, -14, 13), (500, 22, 3), 1.6, u), (500, 22, 3.2), 64)

@shot(140)
def s26(t, lt):
    plaza(t, ["pigeon"]); awake_pair()
    camp = Vector((500, -11.5, 8.5))
    tw = T(142)
    for ch in CROWD + [LEO, DAD]:
        loc = ch.root.location
        d = (camp - loc); target = math.degrees(math.atan2(-d.x, d.y)) * -1
        target = math.degrees(math.atan2(d.x, -d.y))
        dist = (camp - loc).length
        tk = tw + 0.012 * dist
        side = 75 if (hash(ch.name) % 2) else -75
        ch.pose["yaw"] = snapv(t, tk, target + side, target, 0.14, 0.07)
        if ch in CROWD: ch.face("frozen_yawn" if t < tk - 0.07 else "shock")
    LEO.face("smile" if t < tw else "shock"); DAD.face("smile" if t < tw else "shock")
    set_cam(push(camp, (500, 18, 3), 1.2, lt / 2.4), (500, 18, 3.4), 60)

@shot(148)
def s27(t, lt):
    plaza(t, ["pigeon"]); dad_statue("sleep", False, False); hide(DCTRL)
    LEO.place((500, 0, 1.5), 0); LEO.stone(False); LEO.face("sleep"); LEO.pose.update(aL=-8, aR=-8)
    hp_ = leo_full_nest(t); idle(LEO, t, 0.04)
    for ch in CROWD: ch.face("sleep")
    zs = Z_NEIGH
    set_cam(push(hp_ + Vector((0.6, -5.6, 0.6)), hp_, 0.9, lt / 2.2), hp_ + Vector((0, 0, 0.6)), 42)

DAY_HOOKS.append(lambda: setattr(SUNDISC, "location", (0, 140, -40)))
ALL = [STONEBOY, NEIGH, PKID, BAKER, LEO, DAD] + CROWD
def reset_frame():
    reset_all()
    for ch in [STONEBOY, NEIGH, PKID, BAKER]: ch.stone(False)
    PHONE.parent = PKID.body

run(ALL, reset_frame)
