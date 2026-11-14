# roblox_lib.py - motor Blender (bpy) dos Shorts "Roblox story" (aprovado 31/10/2026, video ESTATUA).
# NAO rodar direto. Cada video tem um cena.py que faz:
#     import os, sys; sys.path.insert(0, os.environ["ROBLOX_PIPELINE"]); from roblox_lib import *
#     ... monta cenarios/personagens, define planos com @shot(indice_da_palavra) ...
#     run(chars=[...], reset=minha_funcao_reset)
# Linha de comando (Blender 4.2+; BLENDER = caminho do blender.exe, ver SKILL.md):
#   BLENDER -b --factory-startup --python cena.py -- PASTA MODE [OUT] [f0 f1]
#   PASTA = pasta de trabalho do video (precisa: palavras.json, tex\face_*.png, audio\voz.wav)
#   MODE  = list (so lista planos) | stills (1 quadro no meio de cada plano, 50%) | frames (render final PNG, pula os ja feitos)
# Render: 2 processos em paralelo (f0 f1 dividindo o total) ~3 fps numa placa de video forte. Matar SO o proprio PID, nunca taskkill /IM blender.exe.
import bpy, bmesh, math, json, random, sys, os, wave
from mathutils import Vector, Euler, Matrix

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if not argv: raise SystemExit("uso: blender -b --factory-startup --python cena.py -- PASTA MODE [OUT] [f0 f1]")
W = argv[0]
MODE = argv[1] if len(argv) > 1 else "stills"
OUT = argv[2] if len(argv) > 2 and argv[2] != "-" else os.path.join(W, "frames" if MODE == "frames" else "stills")
F0 = int(argv[3]) if len(argv) > 3 else 0
F1 = int(argv[4]) if len(argv) > 4 else -1
TEX = os.path.join(W, "tex")
FPS = 30
words = json.load(open(os.path.join(W, "palavras.json"), encoding="utf8"))
def T(i): return words[i]["s"]

def fim_video(W):
    """duracao total: config.json {"end": s} ou fim da voz + 1.45 s (ultimo close segura ~1.5 s)"""
    cfg = os.path.join(W, "config.json")
    if os.path.exists(cfg):
        c = json.load(open(cfg, encoding="utf8"))
        if "end" in c: return float(c["end"])
    with wave.open(os.path.join(W, "audio", "voz.wav")) as w_:
        d = w_.getnframes() / w_.getframerate()
    return math.ceil((d + 1.45) * 2) / 2
END = fim_video(W)
NF = int(END * FPS)
R = math.radians
random.seed(7)

# ---------------- helpers ----------------
def lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
def hexc(h, a=1.0):
    h = h.lstrip("#"); return (lin(int(h[0:2], 16)), lin(int(h[2:4], 16)), lin(int(h[4:6], 16)), a)
def smooth(x): x = max(0, min(1, x)); return x * x * (3 - 2 * x)
def backease(x, c1=2.2):
    x = max(0, min(1, x)); c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def snapv(t, tw, a, b, dur=0.14, lead=0.07):
    x = (t - (tw - lead)) / dur
    if x <= 0: return a
    if x >= 1: return b
    return a + (b - a) * backease(x)
def lerp(a, b, u): return a + (b - a) * u
def vlerp(a, b, u): return Vector(a).lerp(Vector(b), u)

scene = bpy.context.scene
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
COLL = {}
def coll(name):
    if name not in COLL:
        c = bpy.data.collections.new(name); scene.collection.children.link(c); COLL[name] = c
    return COLL[name]

MATS = {}
def mat(hexs, rough=0.85, emis=0.0, key=None, alpha=1.0, noise=0.0):
    k = key or (hexs, rough, emis, alpha, noise)
    if k in MATS: return MATS[k]
    m = bpy.data.materials.new(str(k)); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    col = hexc(hexs)
    b.inputs["Base Color"].default_value = col
    b.inputs["Roughness"].default_value = rough
    if "Specular IOR Level" in b.inputs: b.inputs["Specular IOR Level"].default_value = 0.25
    if emis > 0:
        b.inputs["Emission Color"].default_value = col
        b.inputs["Emission Strength"].default_value = emis
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha
    if noise > 0:
        nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 6.0
        mr = nt.nodes.new("ShaderNodeMix"); mr.data_type = "RGBA"
        c2 = tuple(min(1, x * (1 + noise)) for x in col[:3]) + (1,)
        c1 = tuple(x * (1 - noise) for x in col[:3]) + (1,)
        mr.inputs[6].default_value = c1; mr.inputs[7].default_value = c2
        nt.links.new(nz.outputs["Fac"], mr.inputs[0]); nt.links.new(mr.outputs[2], b.inputs["Base Color"])
    MATS[k] = m; return m

def mat_two(c1, c2, scale=40.0, key=None, rough=0.95):
    m = bpy.data.materials.new(key or f"two{c1}{c2}"); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]; b.inputs["Roughness"].default_value = rough
    if "Specular IOR Level" in b.inputs: b.inputs["Specular IOR Level"].default_value = 0.1
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = scale
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.45; ramp.color_ramp.elements[0].color = hexc(c1)
    ramp.color_ramp.elements[1].position = 0.55; ramp.color_ramp.elements[1].color = hexc(c2)
    nt.links.new(nz.outputs["Fac"], ramp.inputs[0]); nt.links.new(ramp.outputs[0], b.inputs["Base Color"])
    return m

IMGS = {}
def img(path):
    if path not in IMGS: IMGS[path] = bpy.data.images.load(path)
    return IMGS[path]
def mat_img(path, key, emis=0.0, alpha=True):
    m = bpy.data.materials.new(key); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    tx = nt.nodes.new("ShaderNodeTexImage"); tx.image = img(path); tx.name = "IMG"
    nt.links.new(tx.outputs["Color"], b.inputs["Base Color"])
    if alpha: nt.links.new(tx.outputs["Alpha"], b.inputs["Alpha"])
    b.inputs["Roughness"].default_value = 0.9
    if "Specular IOR Level" in b.inputs: b.inputs["Specular IOR Level"].default_value = 0.1
    if emis:
        nt.links.new(tx.outputs["Color"], b.inputs["Emission Color"]); b.inputs["Emission Strength"].default_value = emis
    try: m.surface_render_method = "DITHERED"
    except Exception: pass
    return m

# ---- meshes (shared) ----
def mesh_cube():
    me = bpy.data.meshes.new("cube"); bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bm.to_mesh(me); bm.free(); return me
def mesh_cyl(r=0.5, h=1.0, seg=32, bevel=0.0, name="cyl"):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r, radius2=r, depth=h)
    if bevel > 0:
        rim = [e for e in bm.edges if abs(e.verts[0].co.z - e.verts[1].co.z) < 1e-6 and abs(abs(e.verts[0].co.z) - h / 2) < 1e-6
               and (Vector(e.verts[0].co.xy).length > r * 0.9)]
        bmesh.ops.bevel(bm, geom=rim, offset=bevel, segments=5, profile=0.5, affect="EDGES")
    bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    return me
def mesh_sphere(seg=20):
    me = bpy.data.meshes.new("sph"); bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=seg // 2, radius=0.5)
    bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    return me
def mesh_cone(seg=20):
    me = bpy.data.meshes.new("cone"); bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=True, segments=seg, radius1=0.5, radius2=0.0, depth=1.0)
    bm.to_mesh(me); bm.free(); return me
def mesh_face(r=0.627, h=0.80, arc=130, seg=24, u0=0.14, u1=0.86, v0=0.06, v1=0.94):
    me = bpy.data.meshes.new("faceshell"); bm = bmesh.new(); uvl = bm.loops.layers.uv.new()
    cols = []
    for i in range(seg + 1):
        th = R(-arc / 2 + arc * i / seg)
        cols.append((bm.verts.new((r * math.sin(th), -r * math.cos(th), -h / 2)), bm.verts.new((r * math.sin(th), -r * math.cos(th), h / 2))))
    for i in range(seg):
        a0, a1 = cols[i]; b0, b1 = cols[i + 1]
        f = bm.faces.new((a0, b0, b1, a1))
        uA = lerp(u0, u1, i / seg); uB = lerp(u0, u1, (i + 1) / seg)
        for l, uv in zip(f.loops, ((uA, v0), (uB, v0), (uB, v1), (uA, v1))): l[uvl].uv = uv
    bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    return me
def mesh_star():
    me = bpy.data.meshes.new("star"); bm = bmesh.new(); vs = []
    for i in range(10):
        rr = 0.5 if i % 2 == 0 else 0.22; a = R(90 + i * 36)
        vs.append(bm.verts.new((rr * math.cos(a), 0, rr * math.sin(a))))
    bm.faces.new(vs)
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.08)
    bm.to_mesh(me); bm.free(); return me
def mesh_plane():
    me = bpy.data.meshes.new("plane"); bm = bmesh.new(); uvl = bm.loops.layers.uv.new()
    v = [bm.verts.new(p) for p in ((-0.5, 0, -0.5), (0.5, 0, -0.5), (0.5, 0, 0.5), (-0.5, 0, 0.5))]
    f = bm.faces.new(v)
    for l, uv in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))): l[uvl].uv = uv
    bm.to_mesh(me); bm.free(); return me
def mesh_disc(seg=40):
    me = bpy.data.meshes.new("disc"); bm = bmesh.new(); uvl = bm.loops.layers.uv.new()
    vs = [bm.verts.new((0.5 * math.cos(2 * math.pi * i / seg), 0, 0.5 * math.sin(2 * math.pi * i / seg))) for i in range(seg)]
    f = bm.faces.new(vs)
    for l in f.loops: l[uvl].uv = (l.vert.co.x + 0.5, l.vert.co.z + 0.5)
    bm.to_mesh(me); bm.free(); return me

M_CUBE = mesh_cube(); M_HEAD = mesh_cyl(0.62, 1.22, 40, 0.22, "head"); M_SPH = mesh_sphere(); M_CONE = mesh_cone()
M_FACE = mesh_face(); M_STAR = mesh_star(); M_PLANE = mesh_plane(); M_DISC = mesh_disc(); M_CYL = mesh_cyl(0.5, 1.0, 32, 0, "cylu")
M_TORUS = bpy.data.meshes.new("torus")
bm = bmesh.new()
for i in range(24):
    for j in range(10):
        pass
bm.free()

def obj(name, me, c, loc=(0, 0, 0), sc=(1, 1, 1), rot=(0, 0, 0), m=None, parent=None, shadow=True):
    o = bpy.data.objects.new(name, me); coll(c).objects.link(o)
    o.location = loc; o.scale = sc; o.rotation_euler = [R(x) for x in rot]
    if m: o.data = o.data  # shared mesh, use object-level material
    if m:
        o.material_slots  # ensure
        if len(o.data.materials) == 0: o.data.materials.append(None)
        o.material_slots[0].link = "OBJECT"; o.material_slots[0].material = m
    if parent: o.parent = parent
    if not shadow: o.visible_shadow = False
    return o
def empty(name, c, loc=(0, 0, 0), parent=None):
    o = bpy.data.objects.new(name, None); coll(c).objects.link(o); o.location = loc
    if parent: o.parent = parent
    return o
def box(name, c, loc, sc, col, parent=None, rot=(0, 0, 0), **kw): return obj(name, M_CUBE, c, loc, sc, rot, mat(col, **kw), parent)
def sph(name, c, loc, sc, col, parent=None, **kw): return obj(name, M_SPH, c, loc, sc, (0, 0, 0), mat(col, **kw), parent)
def cyl(name, c, loc, sc, col, parent=None, rot=(0, 0, 0), **kw): return obj(name, M_CYL, c, loc, sc, rot, mat(col, **kw), parent)
def cone(name, c, loc, sc, col, parent=None, rot=(0, 0, 0), **kw): return obj(name, M_CONE, c, loc, sc, rot, mat(col, **kw), parent)

STONE = mat("#9A9C9E", 0.95, noise=0.18, key="stone")
STONE_D = mat("#7E8083", 0.95, noise=0.2, key="stone_d")
MOSS = mat("#4E8A2A", 0.95, noise=0.3, key="moss")

FACE_IMG = {n[5:-4]: img(os.path.join(TEX, n)) for n in os.listdir(TEX) if n.startswith("face_")}

# ---------------- character ----------------
SKINS = ["#F2C9A0", "#E0AC7E", "#C68A5E", "#8D5A3B", "#5C3A24", "#F5D6B8"]
SHIRTS = ["#E8432E", "#2E7BE8", "#3BB54A", "#F2C230", "#9B4DE0", "#F27CC0", "#1FB5B0", "#FF8C1A", "#FFFFFF", "#444A55"]
PANTS = ["#2B3A67", "#3B2A1A", "#2E2E2E", "#5A6B7A", "#6B4B2A", "#1F5130"]
HAIRS = ["#2A1B10", "#5B3A1E", "#E8C15A", "#1A1A1A", "#A8461E", "#7A5230"]

class Char:
    def __init__(s, name, c, skin, shirt, pants, hair="none", haircol="#2A1B10", shoes="#222222", nose=False, cap=None, armcol=None, legcol=None):
        s.name = name; s.c = c
        s.root = empty(name + "_root", c)
        s.body = empty(name + "_body", c, (0, 0, 2), s.root)
        s.parts = {}; s.colmat = {}
        def P(k, o):
            s.parts[k] = o; s.colmat[k] = o.material_slots[0].material
        P("torso", box(name + "_torso", c, (0, 0, 1), (2, 1, 2), shirt, s.body))
        s.neck = empty(name + "_neck", c, (0, 0, 2), s.body)
        P("head", obj(name + "_head", M_HEAD, c, (0, 0, 0.61), (1, 1, 1), (0, 0, 0), mat(skin), s.neck))
        s.facemat = mat_img(FACE_IMG and os.path.join(TEX, "face_smile.png"), name + "_face")
        s.faceobj = obj(name + "_faceS", M_FACE, c, (0, 0, 0.61), (1, 1, 1), (0, 0, 0), s.facemat, s.neck, shadow=False)
        s.face_name = "smile"
        s.sh = {}
        for side, x in (("L", -1.5), ("R", 1.5)):
            sp = empty(f"{name}_sh{side}", c, (x, 0, 2), s.body); s.sh[side] = sp
            P("arm" + side, box(f"{name}_arm{side}", c, (0, 0, -1), (1, 1, 2), armcol or shirt, sp))
            P("hand" + side, box(f"{name}_hand{side}", c, (0, 0, -1.85), (1.01, 1.01, 0.3), skin, sp))
        s.hip = {}
        for side, x in (("L", -0.5), ("R", 0.5)):
            hp = empty(f"{name}_hip{side}", c, (x, 0, 0), s.body); s.hip[side] = hp
            P("leg" + side, box(f"{name}_leg{side}", c, (0, 0, -0.81), (1, 1, 1.62), legcol or pants, hp))
            P("shoe" + side, box(f"{name}_shoe{side}", c, (0, -0.02, -1.81), (1.02, 1.04, 0.38), shoes, hp))
        hc = haircol
        if hair == "short":
            P("hair", box(name + "_hair", c, (0, 0.06, 1.3), (1.34, 1.34, 0.32), hc, s.neck))
            P("hair2", box(name + "_hairb", c, (0, 0.42, 0.85), (1.3, 0.5, 0.9), hc, s.neck))
        elif hair == "spiky":
            for k in range(5):
                P(f"hair{k}", cone(f"{name}_sp{k}", c, (-0.45 + k * 0.22, 0.05 * (k % 2), 1.32), (0.42, 0.42, 0.55), hc, s.neck))
            P("hairb", box(name + "_hairb", c, (0, 0.1, 1.2), (1.3, 1.3, 0.2), hc, s.neck))
        elif hair == "bun":
            P("hair", box(name + "_hair", c, (0, 0.05, 1.28), (1.34, 1.34, 0.3), hc, s.neck))
            P("hair2", sph(name + "_bun", c, (0, 0.15, 1.65), (0.8, 0.8, 0.7), hc, s.neck))
        elif hair == "long":
            P("hair", box(name + "_hair", c, (0, 0.06, 1.3), (1.36, 1.36, 0.32), hc, s.neck))
            P("hair2", box(name + "_hairb", c, (0, 0.5, 0.4), (1.4, 0.45, 1.8), hc, s.neck))
        elif hair == "afro":
            P("hair", sph(name + "_hair", c, (0, 0.1, 1.25), (1.6, 1.6, 1.1), hc, s.neck))
        if cap:
            P("cap", obj(name + "_cap", M_CYL, c, (0, 0.02, 1.3), (1.32, 1.32, 0.42), (0, 0, 0), mat(cap), s.neck))
            P("capt", sph(name + "_capt", c, (0, 0.02, 1.48), (1.32, 1.32, 0.45), cap, s.neck))
            P("brim", box(name + "_brim", c, (0, -0.85, 1.2), (1.2, 0.8, 0.08), cap, s.neck))
        if nose:
            P("nose", box(name + "_nose", c, (0, -0.66, 0.5), (0.17, 0.14, 0.17), skin, s.neck))
        s.props = {}
        s.reset()
    def reset(s):
        s.pose = dict(aL=0, aR=0, sL=0, sR=0, lL=0, lR=0, hy=0, hp=0, hr=0, lean=0, bob=0, yaw=0, sit=False, lie=False, scale=1)
    def place(s, loc, yaw=0):
        s.root.location = loc; s.pose["yaw"] = yaw
    def apply(s):
        p = s.pose
        s.root.rotation_euler = (R(-90) if p["lie"] else 0, 0, R(p["yaw"]))
        s.root.scale = (p["scale"],) * 3
        s.body.location = (0, 0, 2 + p["bob"] - (0.0 if not p["sit"] else 0.0))
        s.body.rotation_euler = (R(-p["lean"]), 0, 0)
        s.neck.rotation_euler = (R(p["hp"]), R(p["hr"]), R(p["hy"]))
        s.sh["L"].rotation_euler = (R(p["aL"]), R(-p["sL"]), 0)
        s.sh["R"].rotation_euler = (R(p["aR"]), R(p["sR"]), 0)
        lL = -90 if p["sit"] else p["lL"]; lR = -90 if p["sit"] else p["lR"]
        s.hip["L"].rotation_euler = (R(lL), 0, 0); s.hip["R"].rotation_euler = (R(lR), 0, 0)
    def face(s, n):
        if n != s.face_name:
            s.facemat.node_tree.nodes["IMG"].image = FACE_IMG[n]; s.face_name = n
    def stone(s, on=True, parts=None):
        for k, o in s.parts.items():
            if parts is None or k in parts:
                o.material_slots[0].material = STONE if on else s.colmat[k]
        for k, o in s.props.items():
            if parts is None or k in parts:
                o.material_slots[0].material = STONE if on else s.propcol[k]
    def prop(s, k, o):
        if not hasattr(s, "propcol"): s.propcol = {}
        s.props[k] = o; s.propcol[k] = o.material_slots[0].material
    def show(s, v):
        s.root.hide_render = not v
        for o in s.root.children_recursive: o.hide_render = not v

# ---------------- world / light / camera ----------------
try: scene.render.engine = "BLENDER_EEVEE"
except TypeError: scene.render.engine = "BLENDER_EEVEE_NEXT"
scene.render.resolution_x = 1080; scene.render.resolution_y = 1920
scene.render.resolution_percentage = 50 if MODE == "stills" else 100
scene.render.fps = FPS
scene.view_settings.view_transform = "Standard"; scene.view_settings.look = "None"
scene.render.image_settings.file_format = "PNG"
ee = scene.eevee
ee.taa_render_samples = 12 if MODE == "stills" else 32
for a, v in (("use_shadows", True), ("use_raytracing", True), ("use_gtao", True)):
    try: setattr(ee, a, v)
    except Exception: pass
try: scene.render.use_motion_blur = False
except Exception: pass
try: ee.use_motion_blur = False
except Exception: pass

world = bpy.data.worlds.new("sky"); scene.world = world; world.use_nodes = True
wn = world.node_tree; bg = wn.nodes["Background"]
tc = wn.nodes.new("ShaderNodeTexCoord"); sep = wn.nodes.new("ShaderNodeSeparateXYZ")
sky = wn.nodes.new("ShaderNodeValToRGB")
wn.links.new(tc.outputs["Generated"], sep.inputs[0]); wn.links.new(sep.outputs["Z"], sky.inputs[0])
wn.links.new(sky.outputs[0], bg.inputs["Color"])
sky.color_ramp.elements[0].position = 0.0; sky.color_ramp.elements[1].position = 0.55
def set_sky(c0, c1, strength=1.0):
    sky.color_ramp.elements[0].color = hexc(c0); sky.color_ramp.elements[1].color = hexc(c1)
    bg.inputs["Strength"].default_value = strength

sund = bpy.data.lights.new("sun", "SUN"); sun = bpy.data.objects.new("sun", sund); scene.collection.objects.link(sun)
sund.angle = R(3)
def set_sun(strength=3.5, elev=42, az=-30, col="#FFF1D8"):
    sund.energy = strength; sund.color = hexc(col)[:3]
    sun.rotation_euler = (R(90 - elev), 0, R(az))
ptd = bpy.data.lights.new("pt", "POINT"); pt = bpy.data.objects.new("pt", ptd); scene.collection.objects.link(pt)
ptd.shadow_soft_size = 0.5
def set_pt(loc, col="#FFFFFF", e=0.0):
    pt.location = loc; ptd.color = hexc(col)[:3]; ptd.energy = e
pt2d = bpy.data.lights.new("pt2", "POINT"); pt2 = bpy.data.objects.new("pt2", pt2d); scene.collection.objects.link(pt2)
def set_pt2(loc, col="#FFFFFF", e=0.0):
    pt2.location = loc; pt2d.color = hexc(col)[:3]; pt2d.energy = e

camd = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", camd); scene.collection.objects.link(cam)
scene.camera = cam; camd.sensor_fit = "VERTICAL"; camd.clip_start = 0.1; camd.clip_end = 400
camd.dof.use_dof = False
def set_cam(pos, tgt, fov, roll=0):
    cam.location = pos
    d = Vector(tgt) - Vector(pos)
    q = d.to_track_quat("-Z", "Y"); cam.rotation_euler = q.to_euler()
    if roll: cam.rotation_euler.rotate_axis("Z", R(roll))
    camd.angle_y = R(fov)
def push(p, tgt, dist, u):
    p = Vector(p); d = (Vector(tgt) - p).normalized(); return p + d * dist * smooth(u)


# ---------------- sets ----------------
GRASS = mat_two("#3D8C21", "#4FA32B", 35, "grass")
def ground(c, cx, cy, sx, sy, m=GRASS, z=0):
    o = obj(c + "_ground", M_CUBE, c, (cx, cy, z - 0.25), (sx, sy, 0.5), (0, 0, 0), m); return o
def tree(c, x, y, s=1.0):
    cyl(c + "_trunk", c, (x, y, 1.5 * s), (0.7 * s, 0.7 * s, 3 * s), "#7A4E2A")
    for dx, dy, dz, r in ((0, 0, 4.2, 3.2), (1.0, 0.3, 3.4, 2.4), (-1.0, -0.2, 3.6, 2.4), (0.2, -0.6, 5.2, 2.2)):
        sph(c + "_leaf", c, (x + dx * s, y + dy * s, dz * s), (r * s,) * 3, "#3E9A2E", rough=0.9)
WINDOWS = []
def house(c, x, y, w=10, d=8, h=6.5, wall="#F2F0EA", roof="#B8442F", door="#B53A2E", rot=0, wins=True):
    box(c + "_hw", c, (x, y, h / 2), (w, d, h), wall)
    # roof prism: two slanted boxes
    for s in (-1, 1):
        box(c + "_roof", c, (x, y + s * d * 0.25, h + 1.3), (w + 0.8, d * 0.62, 0.35), roof, rot=(s * 32, 0, 0))
    box(c + "_door", c, (x, y - d / 2 - 0.03, 1.6), (1.8, 0.12, 3.2), door)
    if wins:
        for wx in (-w * 0.3, w * 0.3):
            for wz in (2.0, 4.6):
                if wz == 2.0 and abs(wx) < 1: continue
                box(c + "_wf", c, (x + wx, y - d / 2 - 0.04, wz), (2.0, 0.1, 1.7), "#FFFFFF")
                o = obj(c + "_win", M_CUBE, c, (x + wx, y - d / 2 - 0.08, wz), (1.6, 0.1, 1.3), (0, 0, 0), mat("#1E2A44", 0.3, key=f"win{len(WINDOWS)}"))
                WINDOWS.append(o)
def lamp_post(c, x, y):
    cyl(c + "_lp", c, (x, y, 2.5), (0.25, 0.25, 5), "#333333"); sph(c + "_lpb", c, (x, y, 5.2), (0.8, 0.8, 0.8), "#FFF4C0", emis=0.5)

def clock(c, loc, r, rot=(90, 0, 0), frame="#5A3A22"):
    """face plane faces -Y"""
    root = empty(c + "_clk", c, loc)
    cyl(c + "_clkb", c, (0, 0.18, 0), (r * 2.25, r * 2.25, 0.3), frame, root, rot=(90, 0, 0))
    o = obj(c + "_dial", M_DISC, c, (0, -0.02, 0), (r * 2, 1, r * 2), (0, 0, 0), mat_img(os.path.join(TEX, "dial.png"), c + "_dialm", 0.4), root)
    hp = empty(c + "_hh", c, (0, -0.1, 0), root); mp = empty(c + "_mh", c, (0, -0.14, 0), root)
    box(c + "_hhm", c, (0, 0, r * 0.25), (r * 0.09, 0.05, r * 0.55), "#111111", hp)
    box(c + "_mhm", c, (0, 0, r * 0.36), (r * 0.06, 0.05, r * 0.78), "#111111", mp)
    sph(c + "_pin", c, (0, -0.2, 0), (r * 0.12,) * 3, "#B22222", root)
    return root, hp, mp
def set_clock(hp, mp, hours, minutes):
    hp.rotation_euler = (0, R(hours * 30 + minutes * 0.5), 0); mp.rotation_euler = (0, R(minutes * 6), 0)


# ---------------- puffs / cracks ----------------
C = "fx"
PUFFM = mat("#FFFFFF", 0.6, emis=1.3, alpha=0.72, key="puff")
try: PUFFM.surface_render_method = "BLENDED"
except Exception: pass
DUSTM = mat("#BFB8AC", 0.9, emis=0.4, alpha=0.8, key="dust")
STARM = mat("#FFE45C", 0.5, emis=2.0, key="starm")
POOL = []
for pi in range(3):
    g = {"sph": [], "star": [], "seed": []}
    for k in range(9):
        o = obj(f"puff{pi}_{k}", M_SPH, C, (0, 0, -50), (0.01,) * 3, (0, 0, 0), PUFFM, shadow=False); g["sph"].append(o)
    for k in range(7):
        o = obj(f"star{pi}_{k}", M_STAR, C, (0, 0, -50), (0.01,) * 3, (0, 0, 0), STARM, shadow=False); g["star"].append(o)
    POOL.append(g)
CRACKM = mat_img(os.path.join(TEX, "crack.png"), "crackm")
CRACKS = [obj(f"crack{k}", M_PLANE, C, (0, 0, -50), (0.01,) * 3, (0, 0, 0), CRACKM, shadow=False) for k in range(4)]
rnd = random.Random(99)
PUFF_OFF = [[(rnd.uniform(-1, 1), rnd.uniform(-0.5, 0.3), rnd.uniform(-0.7, 0.9), rnd.uniform(0.7, 1.25)) for k in range(9)] for _ in range(3)]

def do_puffs(t, events):
    """events: list of (t0, pos, size, dust, stars)"""
    for g in POOL:
        for o in g["sph"] + g["star"]: o.location = (0, 0, -50); o.scale = (0.001,) * 3
    act = [e for e in events if 0 <= t - e[0] <= 0.62][:3]
    for gi, (t0, pos, size, dust, stars) in enumerate(act):
        g = POOL[gi]; lt = t - t0
        grow = backease(lt / 0.14, 1.5) if lt < 0.14 else 1.0
        fade = 1.0 - smooth((lt - 0.2) / 0.35)
        sc = size * max(0.0, grow * fade) * (1 + 0.5 * lt)
        for k, o in enumerate(g["sph"]):
            ox, oy, oz, rr = PUFF_OFF[gi][k]
            o.location = Vector(pos) + Vector((ox, oy, oz)) * size * (0.8 + lt)
            o.scale = (sc * rr,) * 3
            o.material_slots[0].material = DUSTM if dust else PUFFM
        if stars:
            for k, o in enumerate(g["star"]):
                a = R(k * 360 / 7 + 20); u = min(1, lt / 0.6)
                rr = size * (0.6 + 1.9 * smooth(u))
                o.location = Vector(pos) + Vector((math.cos(a) * rr, -0.6 * size, math.sin(a) * rr))
                s_ = size * 0.32 * (1 - smooth((u - 0.6) / 0.4))
                o.scale = (s_,) * 3; o.rotation_euler = (0, R(lt * 720 + k * 40), 0)

def do_cracks(t, events):
    """events: (t0, parent, localpos, size, spin)"""
    for o in CRACKS: o.parent = None; o.location = (0, 0, -50); o.scale = (0.001,) * 3
    for k, (t0, par, pos, size, spin) in enumerate([e for e in events if t >= e[0] - 0.02][:4]):
        o = CRACKS[k]; u = backease((t - t0) / 0.1, 1.2) if t < t0 + 0.1 else 1
        o.parent = par; ps = par.matrix_world.to_scale()
        o.location = pos; o.scale = (size * u / ps[0], 1, size * u / ps[2]); o.rotation_euler = (0, R(spin), 0)


# ---------------- visibilidade ----------------
def show_colls(names):
    """mostra so as colecoes listadas (inclua "fx" quando o plano tiver puf/estrela/rachadura)"""
    for n, c_ in COLL.items(): c_.hide_render = n not in names

# ---------------- presets de luz ----------------
DAY_HOOKS = []   # cena.py pode registrar funcoes extras chamadas no day() (ex.: reposicionar o disco do sol)
def day(strength=1.0):
    set_sky("#B8D9FF", "#3378F7", strength); set_sun(3.5, 42, -30); set_pt((0, 0, -100), e=0); set_pt2((0, 0, -100), e=0)
    for o in WINDOWS: win_light(o, False)
    for h in DAY_HOOKS: h()
def night():
    set_sky("#1B2850", "#060B1E", 1.0); set_sun(0.35, 35, -30, "#8FA8FF")

def win_light(o, on):
    b = o.material_slots[0].material.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = hexc("#FFD36B") if on else hexc("#1E2A44")
    b.inputs["Emission Color"].default_value = hexc("#FFC94A")
    b.inputs["Emission Strength"].default_value = 3.0 if on else 0.0

def idle(ch, t, amp=0.03, ph=0.0):
    ch.pose["bob"] += amp * math.sin(t * 2 * math.pi * 0.9 + ph)

# ---------------- planos (chaveados por INDICE DE PALAVRA) ----------------
def cut(i): return T(i) - 0.04
SH = []
def shot(wi):
    """@shot(n): o plano comeca 0,04 s antes da palavra n de palavras.json; a funcao recebe (t, lt) = tempo global, tempo local"""
    def d(f): SH.append((wi, f)); return f
    return d

PUFFS = []; CRACKEV = []   # PUFFS: (t0, pos, size, dust, stars) | CRACKEV: (t0, parent, localpos, size, spin)

def hide(o, v=True):
    o.hide_render = v
    for c_ in o.children_recursive: c_.hide_render = v

# ---------------- render ----------------
def run(chars, reset=None):
    """chars = todos os Char da cena (reset()+apply() a cada quadro); reset = funcao da cena que zera props/luzes antes de cada quadro"""
    SH.sort(key=lambda x: x[0])
    shots = [(cut(wi) if wi > 0 else 0.0, f) for wi, f in SH]
    def frame_state(f):
        t = f / FPS
        k = max(i for i, (t0, fn) in enumerate(shots) if t >= t0 - 1e-6)
        t0, fn = shots[k]
        for ch in chars: ch.reset()
        PUFFS.clear(); CRACKEV.clear()
        if reset: reset()
        fn(t, t - t0)
        for ch in chars: ch.apply()
        bpy.context.view_layer.update()
        do_puffs(t, PUFFS); do_cracks(t, CRACKEV)
        return k
    if MODE == "stills":
        os.makedirs(OUT, exist_ok=True)
        for k, (t0, fn) in enumerate(shots):
            t1 = shots[k + 1][0] if k + 1 < len(shots) else END
            f = int(((t0 + t1) / 2) * FPS)
            frame_state(f); scene.render.filepath = os.path.join(OUT, f"s{k:02d}_{f:04d}.png")
            bpy.ops.render.render(write_still=True)
    elif MODE == "frames":
        os.makedirs(OUT, exist_ok=True)
        f1 = NF if F1 < 0 else F1
        for f in range(F0, f1):
            p = os.path.join(OUT, f"f{f:04d}.png")
            if os.path.exists(p) and os.path.getsize(p) > 1000: continue
            frame_state(f); scene.render.filepath = p
            bpy.ops.render.render(write_still=True)
    elif MODE == "list":
        for k, (t0, fn) in enumerate(shots): print("SHOT", k, round(t0, 2), fn.__name__)
        print("END", END, "NF", NF)
    print("DONE")

