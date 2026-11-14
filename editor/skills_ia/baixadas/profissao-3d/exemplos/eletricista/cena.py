# cena.py - "Voce e eletricista: linha viva" (profissao-3d). Planos = blocos de DADOS chaveados por ancora "linha:palavra".
import sys, os, math, random
sys.path.insert(0, __import__("os").path.expanduser(r"~\.claude\skills\profissao-3d\scripts"))
from prof_lib import *

# ======================= CENARIO =======================
B = "bairro"
street(B)
POLES = [-72, -36, 0, 36, 72]
for px in POLES:
    pole(B, px, insulators=(px != 0))
WIRES = wires(B, POLES)
W1 = WIRES[0]                       # fio do isolador rachado (y = 2.7)
for x in (-24, 12, 48, -60):
    street_lamp(B, x, -5.6, face=1)
random.seed(4)
x = -70
while x < 70:
    w = random.choice((6.5, 7.0, 7.5)); h = random.choice((5.6, 6.2, 6.8, 7.6, 8.4))
    if not (x + w / 2 > 4.0 and x - w / 2 < 13.0):        # vaga da padaria (lado sul)
        house(B, x, -12.2, w, 7, h, face=1, floors=2 if h > 6 else 1)
    house(B, x + 2, 12.2, w, 7, h + random.choice((-0.6, 0, 0.6)), face=-1, floors=2 if h > 6 else 1)
    house(B, x + 1, 26, w, 7, h + 1.5, face=-1); house(B, x + 3, -26, w, 7, h + 1, face=1)
    x += w + 0.9
for tx in (-30, -18, -6, 6, 20, 30, 44, 58, -46, -58):
    tree(B, tx, 6.1 if tx % 4 else -6.0, 1.0 + 0.12 * ((tx // 6) % 3))

# ---- padaria (aberta: da pra ver a geladeira acesa la dentro) ----
PX, PY = 8.5, -12.2
box("pad_back", B, (PX, PY - 3.4, 3.1), (8, 0.3, 6.6), "#E8C9A8")
for s_ in (-1, 1): box("pad_side", B, (PX + s_ * 3.9, PY, 3.1), (0.3, 7, 6.6), "#E8C9A8")
box("pad_roof", B, (PX, PY, 6.5), (8.3, 7.3, 0.35), "#3A2A2A")
box("pad_floor", B, (PX, PY, 0.17), (7.6, 6.6, 0.06), "#C8B8A0")
box("pad_top", B, (PX, PY + 3.5, 4.4), (8, 0.3, 4.0), "#E8C9A8")           # frente de cima
for s_ in (-1, 1): box("pad_col", B, (PX + s_ * 3.4, PY + 3.5, 1.2), (1.2, 0.3, 2.4), "#E8C9A8")
box("pad_low", B, (PX, PY + 3.5, 0.45), (5.6, 0.3, 0.9), "#E8C9A8")
glass = mat("#CFE3F0", 0.05, alpha=0.18, key="vidro", spec=0.8)
box("pad_glass", B, (PX, PY + 3.52, 1.65), (5.6, 0.05, 1.5), glass, bevel=0.0)
for k in range(7):
    box("pad_awn", B, (PX - 3.6 + k * 1.2, PY + 4.3, 2.95), (1.2, 1.7, 0.08), "#C8342A" if k % 2 == 0 else "#F2E6D8", rot=(-22, 0, 0), bevel=0.02)
text3d("pad_sign", B, "PADARIA", (PX, PY + 3.68, 4.6), 0.95, "#F7EAD2", rot=(90, 0, 180), emis=1.2)
FRIDGE_L = mat("#E9F4FF", 0.3, emis=0.0, key="geladeira_luz")
box("fr_body", B, (PX + 2.2, PY - 2.6, 1.3), (1.5, 0.9, 2.3), "#F2F2F2", bevel=0.06)
box("fr_door", B, (PX + 2.2, PY - 2.13, 1.3), (1.3, 0.06, 2.1), FRIDGE_L, bevel=0.02)
for zz in (0.8, 1.4, 2.0):
    box("fr_shelf", B, (PX + 2.2, PY - 2.09, zz), (1.2, 0.04, 0.04), "#BFC8D0", bevel=0.0)
box("fr_handle", B, (PX + 1.65, PY - 2.06, 1.4), (0.06, 0.08, 0.6), "#9AA0A8", bevel=0.01)
box("counter", B, (PX - 1.2, PY - 0.2, 0.6), (3.6, 1.0, 1.0), "#B0703A", bevel=0.05)
for k in range(5):
    caps("pao", B, (PX - 2.6 + k * 0.7, PY - 0.2, 1.2), 0.13, 0.5, "#D9973F", rot=(0, 90, 15 * k))
point((PX, PY - 0.5, 4.5), "#FFC98A", 900, 1.0)
point((PX + 2.2, PY - 1.5, 1.6), "#DDEBFF", 120, 0.3, shadow=False)

# ---- caminhao com cesto (braco de fibra) ----
TR = "caminhao"
TX, TY = 4.2, 0.6
box("tr_cab", TR, (TX + 3.2, TY, 1.55), (2.2, 2.3, 2.1), "#F2F2EE", bevel=0.12)
box("tr_win", TR, (TX + 4.31, TY, 2.0), (0.05, 2.0, 0.8), "#25324A", bevel=0.0, rough=0.2)
box("tr_stripe", TR, (TX + 3.2, TY, 1.1), (2.22, 2.32, 0.18), "#E8681E", bevel=0.02)
box("tr_bed", TR, (TX - 0.4, TY, 1.15), (5.2, 2.4, 1.3), "#D8D8D4", bevel=0.08)
box("tr_chassis", TR, (TX + 0.8, TY, 0.55), (7.4, 2.0, 0.3), "#2A2A2E", bevel=0.03)
for wx in (TX + 3.0, TX - 1.6, TX - 0.2):
    for s_ in (-1, 1):
        cyl("tr_wh", TR, (wx, TY + s_ * 1.05, 0.48), (0.95, 0.95, 0.36), "#1C1C20", rot=(90, 0, 0))
        cyl("tr_hub", TR, (wx, TY + s_ * 1.24, 0.48), (0.4, 0.4, 0.04), "#A0A0A8", rot=(90, 0, 0))
for s_ in (-1, 1):
    cone("tr_cone", TR, (TX - 3.8, TY + s_ * 1.5, 0.35), (0.4, 0.4, 0.7), "#F26A1B")
PIV = Vector((TX - 1.6, TY, 2.3))
cyl("tr_turret", TR, (PIV.x, PIV.y, 2.0), (1.0, 1.0, 0.6), "#E0A526")
BOOM = empty("boom", TR, PIV)
cyl("boom_c", TR, (0, 0, 0.5), (0.3, 0.3, 1.0), "#EDEDEA", BOOM, me=M_CYL)        # escala Z = comprimento
BOOMR = cyl("boom_ring", TR, (0, 0, 0.88), (0.34, 0.34, 0.07), "#E0A526", BOOM)
BASK = empty("basket", TR, (0, 0, 0))
YEL = mat("#E0A526", 0.55)
BW, BD, BH, BT = 1.0, 0.9, 1.05, 0.06
box("bk_floor", TR, (0, 0, BT / 2), (BW, BD, BT), YEL, BASK, bevel=0.02)
for s_ in (-1, 1):
    box("bk_wx", TR, (s_ * (BW / 2 - BT / 2), 0, BH / 2), (BT, BD, BH), YEL, BASK, bevel=0.02)
    box("bk_wy", TR, (0, s_ * (BD / 2 - BT / 2), BH / 2), (BW, BT, BH), YEL, BASK, bevel=0.02)
for s_ in (-1, 1):   # v2: aro de cima mais grosso (borda do cesto) + adesivos pretos
    box("bk_lipx", TR, (s_ * (BW / 2 - 0.01), 0, BH + 0.01), (0.11, BD + 0.1, 0.07), "#C99220", BASK, bevel=0.02)
    box("bk_lipy", TR, (0, s_ * (BD / 2 - 0.01), BH + 0.01), (BW + 0.1, 0.11, 0.07), "#C99220", BASK, bevel=0.02)
    for dx, dz, w_, h_ in ((-0.18, 0.3, 0.42, 0.13), (0.3, 0.78, 0.14, 0.09)):   # 1 placa larga embaixo + 1 pequena no canto (nada de "rosto")
        box("bk_dec", TR, (dx, s_ * (BD / 2 + 0.006), dz), (w_, 0.012, h_), "#1C1C20", BASK, bevel=0.0)
box("bk_dec_x", TR, (BW / 2 + 0.006, 0.1, 0.6), (0.012, 0.22, 0.14), "#1C1C20", BASK, bevel=0.0)
box("bk_mount", TR, (0, 0, -0.18), (0.36, 0.36, 0.36), "#8A8A90", BASK, bevel=0.04)
BK_WORK = Vector((0.9, 1.6, 8.76))       # chao do cesto na posicao de trabalho
BK_SIM = Vector((0.9, 3.6, 8.76))        # entre o fio 1 e o 2 (simulacao do circuito)
BK_LOW = Vector((TX - 0.6, TY + 0.4, 2.45))
def set_basket(floor):
    BASK.location = floor
    tip = Vector(floor) + Vector((0, 0, -0.32))
    d = tip - PIV; BOOM.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    BOOM.scale = (1, 1, d.length)
    BOOMR.scale = (0.34, 0.34, 0.07 / d.length)

ELE = Pessoa("ele", TR)
ELE.root.parent = BASK; ELE.root.location = (0, 0, BT)
SIMM = mat("#C9C9CE", 0.6, key="manequim")
MAN = Pessoa("man", "sim", mono=SIMM)
GLOW = mat("#FFE27A", 0.3, emis=9.0, key="corrente")
PATH = curve_obj("corr", "sim", [(0, 0, 0), (0, 0, 1)], 0.05, GLOW)
VARA = empty("vara", TR)
cyl("vara_c", TR, (0, 0, 0.5), (0.045, 0.045, 1.0), "#F2C230", VARA)
VHOOK = empty("vara_h", TR)
box("vh1", TR, (0, 0, 0.09), (0.035, 0.035, 0.18), "#3A3A3A", VHOOK, bevel=0.005)
box("vh2", TR, (0, -0.06, 0.18), (0.035, 0.14, 0.035), "#3A3A3A", VHOOK, bevel=0.005)

# ---- isolador rachado + novo, capas isolantes, faiscas ----
INS_POS = Vector((0, WIRE_Y[0], 10.15))
INS_OLD = insulator("ins_old", "isol", INS_POS)
CRK = mat("#1A1A1A", 0.9, key="trinca")
for k, (z, ang, rr) in enumerate(((0.16, 200, 0.3), (0.22, 215, 0.25), (0.11, 190, 0.33), (0.27, 230, 0.2))):
    a_ = math.radians(ang)
    box(f"crk{k}", "isol", (rr * math.cos(a_), rr * math.sin(a_), z), (0.03, 0.05, 0.11), CRK, INS_OLD, rot=(0, 18 * (-1) ** k, ang), bevel=0.0)
box("chip", "isol", (0.27 * math.cos(math.radians(205)), 0.27 * math.sin(math.radians(205)), 0.15), (0.1, 0.07, 0.07), CRK, INS_OLD, rot=(0, 0, 205), bevel=0.0)
INS_NEW = insulator("ins_new", "isol", INS_POS, mat("#F7F6F2", 0.3, spec=0.7, key="porcelana_nova"))
for wy in WIRE_Y[1:]:
    insulator(f"ins_c{wy}", "isol", (0, wy, 10.15))
SPK = [ico(f"spk{k}", "isol", (0, 0, -50), 0.03, mat("#FFF0A0", 0.3, emis=12, key="faisca")) for k in range(10)]
CAPM = mat("#E8681E", 0.6, key="capa")
CAPS = []
for wy in WIRE_Y[1:]:
    for s_ in (-1, 1):
        root = empty(f"cap{wy}{s_}", "isol", (s_ * 0.42, wy, WIRE_Z))
        cyl(f"capc{wy}{s_}", "isol", (s_ * 1.1, 0, 0), (0.2, 0.2, 2.2), CAPM, root, rot=(0, 90, 0))
        for k in range(3):
            cyl(f"capr{wy}{s_}{k}", "isol", (s_ * (0.35 + 0.75 * k), 0, 0), (0.24, 0.24, 0.1), CAPM, root, rot=(0, 90, 0))
        CAPS.append(root)
ARCS = [curve_obj(f"arc{k}", "isol", [(0, 0, 0)] * 9, 0.012, mat("#BFE4FF", 0.3, emis=10, key="arco")) for k in range(2)]

# ---- passarinho ----
BIRD_X = -8.0
def wz(x, wy=WIRE_Y[0]): return sag(x, -36, 0, WIRE_Z, WIRE_Z, 0.55)
BIRD = Passarinho("pass", "bird")
BIRD.root.location = (BIRD_X, WIRE_Y[0], wz(BIRD_X) + WIRE_R)
XRW = cyl("xr_wire", "bird", (BIRD_X, WIRE_Y[0], wz(BIRD_X)), (0.075, 0.075, 0.5), mat("#FFB21E", 0.3, emis=0.9, key="xr"), rot=(0, 90, 0))

# ---- luva (estudio longe do bairro, so ceu atras) ----
GV = Vector((300, 0, 60))
GL = empty("glove", "luva", GV)
RUB = mat("#D8473D", 0.4, spec=0.55, key="borracha"); LEA = mat("#E2C096", 0.85, key="couro")
RUBH = mao("rub", "luva", RUB, GL, 1.0, cuff_h=0.9)
LEAH = mao("lea", "luva", LEA, GL, 1.0, cuff_h=0.3, flare=False, grow=0.014)
grade("gr", "luva", GV + Vector((0, 2.2, 0.2)))

# ======================= ESTADO POR QUADRO =======================
ALL = ["bairro", "caminhao", "sim", "isol", "bird", "luva"]
def show(*names):
    for n, c_ in COLL.items(): c_.hide_render = n not in names
LIFT = {"v": 0.0}
def lift_fn(x): g = math.exp(-((x - 0.6) / 2.2) ** 2); return (-0.55 * LIFT["v"] * g, 0.35 * LIFT["v"] * g)
def reset(t):
    show("bairro", "caminhao", "isol", "bird")
    dusk(); windows(True); lamps(True); set_emis(FRIDGE_L, 1.6, "#E9F4FF")
    set_basket(BK_WORK); ELE.reset(); ELE.p["yaw"] = 180; ELE.show(True)
    MAN.reset(); MAN.root.parent = None; hide(MAN.root, True); hide(PATH, True); hide(VARA); hide(VHOOK); set_emis(SIMM, 0)
    hide(INS_OLD, False); hide(INS_NEW, True); INS_NEW.location = INS_POS
    for o in SPK: o.location = (0, 0, -50)
    for cp in CAPS: cp.scale = (1, 1, 1); hide(cp, True)
    for a_ in ARCS: hide(a_, True)
    LIFT["v"] = 0.0; curve_set(W1, wire_pts(WIRE_Y[0], POLES)); move_beads(WIRE_Y[0], None)
    BIRD.xray(False); hide(XRW, True); BIRD.headp.rotation_euler = (0, 0, 0)
    BIRD.root.location = (BIRD_X, WIRE_Y[0], wz(BIRD_X) + WIRE_R)
    camd.dof.use_dof = False; ELE.apply(); MAN.apply()
def caps_state(t):
    """capas aparecem a partir de 'cobre' (17:2): cada uma cresce a partir do isolador"""
    t0 = T("17:2")
    for k, cp in enumerate(CAPS):
        u = ease((t - t0 - 0.18 * k) / 0.5)
        hide(cp, u <= 0.01); cp.scale = (max(0.01, u), 1, 1)
def apply_wire():
    curve_set(W1, wire_pts(WIRE_Y[0], POLES, lift=lift_fn)); move_beads(WIRE_Y[0], lift_fn)
def sparks(t, amt=1.0):
    random.seed(int(t * 30 / 2))
    for k, o in enumerate(SPK):
        if random.random() < 0.55 * amt:
            a_ = math.radians(random.uniform(180, 240)); r_ = random.uniform(0.3, 0.45)
            o.location = INS_POS + Vector((r_ * math.cos(a_), r_ * math.sin(a_), random.uniform(0.08, 0.3)))
            o.scale = (random.uniform(0.02, 0.05),) * 3
def arcs(t):
    random.seed(int(t * 30 / 3))
    for k, a_ in enumerate(ARCS):
        y0, y1 = WIRE_Y[k] + 0.05, WIRE_Y[k + 1] - 0.05; xx = -3.4 - 0.6 * k; z0 = wz(xx)
        pts = [(xx + random.uniform(-0.12, 0.12) * (0 < i < 8), lerp(y0, y1, i / 8), z0 + random.uniform(-0.1, 0.1) * (0 < i < 8)) for i in range(9)]
        curve_set(a_, pts); hide(a_, random.random() < 0.25)
def worker_vara(t, u_raise):
    """bastao amarelo: base nas maos do eletricista, ponta no gancho do fio"""
    ELE.p.update(aR=lerp(-20, -125, u_raise), aL=lerp(-15, -110, u_raise), eR=-10, eL=-15, sR=10, sL=20, hp=-12)
    ELE.apply(); bpy.context.view_layer.update()
    h = (ELE.hand_world("R") + ELE.hand_world("L")) / 2
    dy, dz = lift_fn(0.6)
    tip = vlerp(h + Vector((0, 0.3, 1.0)), Vector((0.6, WIRE_Y[0] + dy, WIRE_Z + dz - 0.06)), u_raise)
    d = tip - h; VARA.location = h - d.normalized() * 0.25
    VARA.rotation_euler = d.to_track_quat("Z", "Y").to_euler(); VARA.scale = (1, 1, d.length + 0.25)
    VHOOK.location = tip; VHOOK.rotation_euler = VARA.rotation_euler
    hide(VARA, False); hide(VHOOK, False)
def man_path(pts, u):
    hide(PATH, False); curve_set(PATH, pts); curve_reveal(PATH, 0, u)

INS = Vector((0, WIRE_Y[0], 10.45)); HEAD = BK_WORK + Vector((0, 0, 1.75)); BIRDP = Vector((BIRD_X + 0.02, WIRE_Y[0], wz(BIRD_X) + 0.16))

# ======================= PLANOS (DADOS) =======================
# SHOT(ancora, cam0, cam1, alvo0, alvo1, fov0, fov1, roll, dof, fx)
def fx_idle(t, lt, u): ELE.p["hy"] = 8 * math.sin(t * 0.9); ELE.apply()
SHOT("0:0", (5.2, 2.05, 10.0), (3.0, 2.15, 10.15), (-5, 2.9, 10.6), (-5, 2.85, 10.5), 40, 38, fx=fx_idle)
SHOT("1:0", (4.6, -3.0, 6.4), (3.9, -2.4, 7.1), (0.6, 2.0, 10.1), (0.7, 2.0, 10.2), 40, 36, fx=fx_idle)
def fx_wave(t, lt, u):
    k = ramp(t, T("2:0") + 0.1, 0.35)
    ELE.p.update(aR=lerp(0, -20, k), sR=lerp(8, 150, k), eR=-30 * k * (0.6 + 0.4 * math.sin(t * 9)), hp=-6); ELE.apply()
SHOT("2:0", (2.1, 3.5, 9.95), (1.45, 3.55, 10.0), HEAD + Vector((0, 0, -0.25)), HEAD + Vector((0, 0, -0.2)), 36, 33, fx=fx_wave)
SHOT("3:0", (-12, -26, 42), (-8, -21, 33), (0, 2, 2), (0, 2, 3), 48, 46, fx=fx_idle)
SHOT("4:0", (9.6, 2.2, 2.0), (8.9, 1.2, 2.1), (8.5, -8.5, 3.2), (8.5, -8.5, 3.0), 44, 42)
def fx_dark(t, lt, u):
    k = ramp(t, T("5:8") - 0.05, 0.25)
    windows(k < 0.5); lamps(k < 0.5); set_emis(FRIDGE_L, 0 if k > 0.5 else 1.6)
    set_sun(lerp(4.0, 2.4, k)); set_sky(SKY, lerp(1.0, 0.55, k))
SHOT("5:0", (24, 3.2, 3.6), (19, 3.0, 4.0), (0, -5, 3.2), (0, -5, 3.2), 50, 48, fx=fx_dark)
SHOT("6:0", (10.5, -1.2, 4.6), (6.8, -0.4, 6.0), (0, 4.5, 10.3), (0, 4.5, 10.4), 44, 42, fx=fx_idle)
SHOT("7:0", (-5.6, 2.0, 9.9), (-4.5, 2.05, 10.0), (0, 2.7, 10.45), (0, 2.7, 10.45), 34, 32)
def fx_ins(t, lt, u): pass
SHOT("8:0", orbit(INS + Vector((0, 0, -0.1)), 1.35, 0.15, 118), orbit(INS + Vector((0, 0, -0.1)), 1.25, 0.1, 146), INS + Vector((0, 0, -0.15)), INS + Vector((0, 0, -0.15)), 32, 30, dof=2.8)
SHOT("8:6", (-3.4, -0.8, 9.2), (-4.4, -2.4, 8.4), (0, 3.4, 10.1), (0, 3.6, 10.0), 42, 46, fx=fx_idle)
def fx_crack(t, lt, u):
    if t > T("9:2") - 0.05: sparks(t, 1.0)
SHOT("9:0", orbit(INS_POS + Vector((0, 0, 0.18)), 1.6, 0.28, 200), orbit(INS_POS + Vector((0, 0, 0.18)), 1.45, 0.22, 214), INS_POS + Vector((0, 0, 0.2)), INS_POS + Vector((0, 0, 0.2)), 30, 28, dof=2.8, fx=fx_crack)
SHOT("9:4", (2.6, 2.4, 0.9), (2.2, 2.7, 1.5), (0, 4.0, 10.5), (0, 4.1, 10.6), 56, 54, fx=lambda t, lt, u: sparks(t, 0.4))
def climb(t, z):
    MAN.place((0, POLE_Y - 0.36, z), 180); s_ = math.sin(t * 7)
    MAN.p.update(aL=-150 + 18 * s_, aR=-150 - 18 * s_, eL=-25, eR=-25, sL=5, sR=5, legs=18 * s_, hp=-10)
    MAN.apply(); hide(MAN.root, False)
def fx_climb(t, lt, u):
    show("bairro", "sim", "isol"); climb(t, lerp(4.4, 6.0, smooth(u)))
SHOT("10:0", (3.2, 0.6, 5.0), (2.7, 0.9, 6.2), (0, 4.2, 6.6), (0, 4.2, 7.6), 46, 44, fx=fx_climb)
def fx_path(t, lt, u):
    show("bairro", "sim", "isol"); climb(T("10:5") + 0.0, 6.0); MAN.p.update(legs=0); MAN.apply()
    k = ramp(t, T("10:7"), 1.4); set_emis(SIMM, 3.5 * ramp(t, T("10:9"), 0.4), "#FFE27A")
    hb = MAN.hand_world("R"); ft = MAN.root.matrix_world.translation
    man_path([(0, 2.7, 10.45), (0, 2.7, 10.2), (0.2, 2.9, 10.17), (0.2, 4.5, 10.17), (0.24, 4.5, hb.z + 0.3), (hb.x, hb.y, hb.z),
              (0.05, ft.y, ft.z + 1.2), (0.05, ft.y, ft.z + 0.1), (0.24, 4.5, ft.z - 0.1), (0.24, 4.5, 0.3), (0.24, 4.5, 0.19), (1.6, 3.6, 0.19)], k)
SHOT("10:5", (6.5, -1.0, 4.2), (7.4, -2.0, 3.8), (0, 4.0, 5.6), (0, 4.0, 5.4), 52, 54, fx=fx_path)
def fx_rise(t, lt, u):
    k = ease(lt / 1.9); set_basket(vlerp(BK_LOW, BK_WORK, k) + Vector((0, 0, 1.2 * math.sin(math.pi * k) * 0.6))); fx_idle(t, lt, u)
SHOT("11:0", (15, -10, 4.6), (12.5, -8.6, 6.4), (1.5, 1.0, 5.0), (1.2, 1.2, 7.0), 46, 44, fx=fx_rise)
SHOT("11:6", (3.4, -0.5, 2.9), (3.1, -0.3, 3.5), (0.9, 1.6, 9.2), (0.9, 1.6, 9.4), 52, 50, fx=fx_idle)
def fx_reach(t, lt, u):
    k = smooth(u * 1.3); ELE.p.update(aR=lerp(-25, -78, k), eR=lerp(-20, -10, k), sR=lerp(10, -4, k), hy=-10, hp=-4); ELE.apply()
SHOT("12:0", (1.45, 0.75, 10.8), (1.35, 0.9, 10.75), (0.3, 2.7, 10.4), (0.3, 2.7, 10.4), 42, 40, fx=fx_reach)
def fx_glove(t, lt, u):
    show("luva"); GL.rotation_euler = (0, 0, R(-18 + 26 * smooth(u)))
    k = ease((t - T("14:5") + 0.25) / 0.6) if t > T("14:0") - 0.06 else 0
    hide(LEAH, k <= 0.001); LEAH.location = (0, -0.35 * (1 - k), 0.12 * (1 - k)); LEAH.scale = (1.0 + 0.5 * (1 - k),) * 3
SHOT("13:0", GV + Vector((0.25, -2.6, 0.35)), GV + Vector((0.15, -2.35, 0.3)), GV + Vector((0, 0, 0.2)), GV + Vector((0, 0, 0.2)), 34, 33, dof=4, fx=fx_glove)
SHOT("14:0", GV + Vector((-0.5, -2.4, 0.5)), GV + Vector((-0.35, -2.2, 0.45)), GV + Vector((0, 0, 0.22)), GV + Vector((0, 0, 0.22)), 34, 33, dof=4, fx=fx_glove)
SHOT("15:0", (4.0, -1.8, 15.2), (2.8, -0.8, 14.2), (-0.5, 4.5, 10.0), (-0.5, 4.5, 10.1), 44, 42, fx=fx_idle)
def fx_volts(t, lt, u): arcs(t) if t > T("15:8") - 0.05 else None; fx_idle(t, lt, u)
SHOT("15:7", (-6.5, 0.6, 12.6), (-6.0, 1.0, 12.2), (-2.6, 4.5, 10.2), (-2.6, 4.5, 10.2), 44, 42, fx=fx_volts)
def fx_circ(t, lt, u):
    show("bairro", "caminhao", "isol", "sim"); set_basket(BK_SIM); ELE.show(False); MAN.root.parent = BASK
    k = ramp(t, T("16:1"), 0.45)
    MAN.place((0, 0, BT), 90); MAN.p.update(sL=lerp(10, 108, k), sR=lerp(10, 108, k), hp=-8); MAN.apply(); hide(MAN.root, False)
    g = ramp(t, T("16:5") - 0.1, 0.7); set_emis(SIMM, 4.0 * g, "#FFE27A")
    if g > 0:
        ha, hb_ = sorted((MAN.hand_world("L"), MAN.hand_world("R")), key=lambda v: v.y); ch = MAN.chest.matrix_world.translation + Vector((0, 0, 0.45))
        man_path([(ha.x + 1.6, WIRE_Y[0], wz(ha.x + 1.6) if False else WIRE_Z), (ha.x, ha.y, ha.z), (ch.x, ch.y, ch.z), (hb_.x, hb_.y, hb_.z), (hb_.x + 1.6, WIRE_Y[1], WIRE_Z)], g)
SHOT("16:0", (4.4, 3.6, 10.75), (3.7, 3.6, 10.7), (0.9, 3.6, 10.25), (0.9, 3.6, 10.25), 42, 40, fx=fx_circ)
def fx_cap(t, lt, u):
    caps_state(t); k = ramp(t, T("17:1"), 0.5)
    ELE.p.update(aR=lerp(-20, -95, k), aL=lerp(-15, -60, k), eR=-10, hy=-25, hp=-5); ELE.apply()
SHOT("17:0", (1.9, 0.2, 11.9), (1.5, 0.5, 12.1), (-0.3, 4.6, 10.3), (-0.3, 4.6, 10.4), 44, 42, fx=fx_cap)
SHOT("17:6", (3.2, 5.4, 11.2), (2.6, 5.4, 11.25), (0.6, 4.6, 10.4), (0.6, 4.6, 10.4), 40, 38, fx=lambda t, lt, u: caps_state(t))
def fx_bird(t, lt, u):
    caps_state(t); BIRD.headp.rotation_euler = (R(-8), 0, R(25 * math.sin(lt * 2.2)))
    hop = max(0.0, math.sin(math.pi * clamp((lt - 0.15) / 0.3))) * 0.04
    BIRD.root.location = (BIRD_X, WIRE_Y[0], wz(BIRD_X) + WIRE_R + hop)
SHOT("18:0", (-8.45, 1.75, 10.3), (-8.3, 2.0, 10.25), BIRDP, BIRDP, 32, 28, dof=2.0, fx=fx_bird)
SHOT("19:0", (-7.62, 1.92, 10.36), (-7.68, 1.98, 10.33), BIRDP, BIRDP, 28, 27, dof=2.0, fx=fx_bird)
def fx_xray(t, lt, u):
    caps_state(t); BIRD.xray(True); hide(XRW, False)
    m = XRW.material_slots[0].material; set_emis(m, 0.9 + 0.3 * math.sin(t * 8))
SHOT("20:0", (-7.8, 1.66, 10.24), (-7.86, 1.72, 10.25), BIRDP + Vector((0, 0, -0.07)), BIRDP + Vector((0, 0, -0.06)), 28, 27, dof=3.2, fx=fx_xray)
SHOT("20:7", (-7.2, 1.3, 10.35), (-6.6, 0.8, 10.6), BIRDP, BIRDP + Vector((0.3, 0.2, 0)), 34, 38, dof=3.5, fx=fx_xray)
def fx_hold(t, lt, u):
    caps_state(t); k = smooth(u * 1.6); ELE.p.update(aR=lerp(-30, -82, k), eR=-8, sR=-6, hy=-8); ELE.apply()
SHOT("21:0", (2.7, 0.1, 9.95), (2.35, 0.35, 10.15), (0.6, 2.2, 10.3), (0.6, 2.25, 10.35), 40, 38, fx=fx_hold)
def fx_vara(t, lt, u):
    caps_state(t); LIFT["v"] = ramp(t, T("22:10"), 1.0); apply_wire(); worker_vara(t, smooth(clamp((t - T("22:0")) / 1.4)))
SHOT("22:0", (2.8, -1.7, 8.4), (2.4, -1.3, 8.8), (0.6, 2.2, 10.5), (0.6, 2.2, 10.6), 46, 44, fx=fx_vara)
SHOT("22:9", (-1.6, 1.4, 10.55), (-1.85, 1.2, 10.7), (0.3, 2.7, 10.6), (0.3, 2.7, 10.7), 40, 40, fx=fx_vara)
def fx_new(t, lt, u):
    caps_state(t); LIFT["v"] = 1.0; apply_wire(); worker_vara(t, 1.0); hide(INS_OLD, True); hide(INS_NEW, False)
    k = ease((t - T("23:1") + 0.15) / 0.55); INS_NEW.location = INS_POS + Vector((0, 0, 0.9 * (1 - k)))
SHOT("23:0", orbit(INS_POS + Vector((0, 0, 0.3)), 1.4, 0.25, 128), orbit(INS_POS + Vector((0, 0, 0.3)), 1.3, 0.2, 145), INS_POS + Vector((0, 0, 0.35)), INS_POS + Vector((0, 0, 0.3)), 34, 32, dof=3.0, fx=fx_new)
def fx_back(t, lt, u):
    caps_state(t); hide(INS_OLD, True); hide(INS_NEW, False)
    LIFT["v"] = 1 - ramp(t, T("24:1"), 0.6); apply_wire(); worker_vara(t, 1.0)
SHOT("24:0", orbit(INS_POS + Vector((0, 0, 0.3)), 1.7, 0.1, 150), orbit(INS_POS + Vector((0, 0, 0.3)), 1.8, 0.15, 162), INS_POS + Vector((0, 0, 0.3)), INS_POS + Vector((0, 0, 0.3)), 38, 38, fx=fx_back)
def fx_done(t, lt, u):
    caps_state(t); hide(INS_OLD, True); hide(INS_NEW, False); fx_idle(t, lt, u)
SHOT("25:0", (-15, -2.4, 1.5), (-11.5, -2.4, 1.7), (0, 5, 6.5), (0, 5, 7.0), 50, 48, fx=fx_done)
SHOT("26:0", (9.9, -3.6, 1.6), (9.3, -4.4, 1.5), (9.8, -14.6, 1.3), (9.9, -14.8, 1.3), 40, 38, fx=fx_done)
SHOT("27:0", (30, -40, 30), (35, -47, 37), (0, 0, 2), (0, 0, 2), 44, 44, fx=fx_done)
SHOT("28:0", orbit((0.9, 2.0, 9.6), 9.5, 2.5, -72), orbit((0.9, 2.0, 9.6), 9.5, 3.2, -38), (0.6, 2.4, 9.8), (0.6, 2.4, 9.8), 44, 42, fx=fx_done)
SHOT("29:0", (-13, -6.5, 6.2), (-10.5, -7.2, 7.2), (2, 2, 6), (2, 2, 6.4), 50, 48, fx=fx_done)
SHOT("29:7", (6, -30, 21), (6, -37, 28), (0, 0, 4), (0, 0, 4), 44, 44, fx=fx_done)

run(reset=reset)
