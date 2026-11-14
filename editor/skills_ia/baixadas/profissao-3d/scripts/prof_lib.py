# prof_lib.py - motor Blender (bpy) dos reels "Voce e [profissao]" 3D low-poly ao entardecer.
# NAO rodar direto. Cada video tem um cena.py:
#     import sys; sys.path.insert(0, __import__("os").path.expanduser(r"~\.claude\skills\profissao-3d\scripts")); from prof_lib import *
#     ... monta o cenario com os blocos daqui (bairro, poste, casas, Pessoa, passarinho...) + props da profissao ...
#     SHOT("3:0", cam=..., ...) / @shot("3:0")  -> planos chaveados por ANCORA "linha:palavra" do roteiro
#     run(reset=minha_funcao_reset)
# Linha de comando:
#   blender -b --factory-startup --python cena.py -- PROJETO MODE [f0 f1]
#   MODE = list | stills (1 quadro no meio de cada plano, 50%) | frames (PNG final, pula os ja feitos)
import bpy, bmesh, math, json, random, sys, os
from mathutils import Vector, Euler

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if not argv: raise SystemExit("uso: blender -b --factory-startup --python cena.py -- PROJETO MODE [f0 f1]")
W = os.path.abspath(argv[0]); MODE = argv[1] if len(argv) > 1 else "stills"
F0 = int(argv[2]) if len(argv) > 2 else 0
F1 = int(argv[3]) if len(argv) > 3 else -1
FPS = 30
_PJ = json.load(open(os.path.join(W, "palavras.json"), encoding="utf8"))
WORDS = _PJ["words"]; VOZ_DUR = _PJ["dur"]
CFG = json.load(open(os.path.join(W, "projeto.json"), encoding="utf8")) if os.path.exists(os.path.join(W, "projeto.json")) else {}
END = round(VOZ_DUR + CFG.get("cauda", 1.2), 2)
NF = int(END * FPS)
R = math.radians
random.seed(11)

# ---------------- ancoras: "L:k" = k-esima palavra da linha L do roteiro (0-based) ----------------
def idx(a):
    if isinstance(a, int): return a
    L, k = (int(x) for x in str(a).split(":"))
    ii = [i for i, w in enumerate(WORDS) if w["line"] == L]
    return ii[min(k, len(ii) - 1)] if k >= 0 else ii[k]
def T(a): return WORDS[idx(a)]["s"]
def TE(a): return WORDS[idx(a)]["e"]

# ---------------- helpers ----------------
def lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
def hexc(h, a=1.0):
    h = h.lstrip("#"); return (lin(int(h[0:2], 16)), lin(int(h[2:4], 16)), lin(int(h[4:6], 16)), a)
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def smooth(x): x = clamp(x); return x * x * (3 - 2 * x)
def ease(x): x = clamp(x); return 1 - (1 - x) ** 3
def backease(x, c1=1.7):
    x = clamp(x); c3 = c1 + 1; return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def lerp(a, b, u): return a + (b - a) * u
def vlerp(a, b, u): return Vector(a).lerp(Vector(b), u)
def ramp(t, t0, dur): return smooth((t - t0) / max(dur, 1e-3))

scene = bpy.context.scene
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
COLL = {}
def coll(name):
    if name not in COLL:
        c = bpy.data.collections.new(name); scene.collection.children.link(c); COLL[name] = c
    return COLL[name]

# ---------------- materiais ----------------
MATS = {}
def mat(hexs, rough=0.8, emis=0.0, key=None, alpha=1.0, metal=0.0, spec=0.3, ecol=None):
    k = key or (hexs, rough, emis, alpha, metal, ecol)
    if k in MATS: return MATS[k]
    m = bpy.data.materials.new(str(k)); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = hexc(hexs)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if "Specular IOR Level" in b.inputs: b.inputs["Specular IOR Level"].default_value = spec
    b.inputs["Emission Color"].default_value = hexc(ecol or hexs)
    b.inputs["Emission Strength"].default_value = emis
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha
        try: m.surface_render_method = "BLENDED"
        except Exception: pass
    MATS[k] = m; return m
def set_emis(m, e, col=None):
    b = m.node_tree.nodes["Principled BSDF"]; b.inputs["Emission Strength"].default_value = e
    if col: b.inputs["Emission Color"].default_value = hexc(col)
def set_base(m, col):
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = hexc(col)
def set_alpha(m, a):
    m.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = a

# ---------------- malhas compartilhadas ----------------
def _mesh(name, fn, smooth_=False):
    me = bpy.data.meshes.new(name); bm = bmesh.new(); fn(bm); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = smooth_
    return me
M_CUBE = _mesh("cube", lambda bm: bmesh.ops.create_cube(bm, size=1.0))
M_SPH = _mesh("sph", lambda bm: bmesh.ops.create_uvsphere(bm, u_segments=28, v_segments=16, radius=0.5), True)
M_ICO = _mesh("ico", lambda bm: bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.5))
M_CYL = _mesh("cyl", lambda bm: bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24, radius1=0.5, radius2=0.5, depth=1.0), True)
M_CYL8 = _mesh("cyl8", lambda bm: bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=8, radius1=0.5, radius2=0.5, depth=1.0))
M_CONE = _mesh("cone", lambda bm: bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24, radius1=0.5, radius2=0.0, depth=1.0), True)
M_HEX = _mesh("hex", lambda bm: bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=6, radius1=0.5, radius2=0.5, depth=1.0))
def _capsule(bm):
    bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=12, radius=0.5)
    for v in bm.verts:
        v.co.z = v.co.z + (0.5 if v.co.z > 0 else -0.5)   # capsula de altura 2 (raio 0.5) -> escalar
M_CAPS = _mesh("caps", _capsule, True)
def _hemi(bm):
    bmesh.ops.create_uvsphere(bm, u_segments=28, v_segments=16, radius=0.5)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < -0.001], context="VERTS")
M_HEMI = _mesh("hemi", _hemi, True)
for p in M_CYL.polygons:   # tampas planas dos cilindros
    if abs(p.normal.z) > 0.9: p.use_smooth = False
for p in M_CONE.polygons:
    if p.normal.z < -0.9: p.use_smooth = False

def obj(name, me, c, loc=(0, 0, 0), sc=(1, 1, 1), rot=(0, 0, 0), m=None, parent=None, bevel=0.0, shadow=True):
    o = bpy.data.objects.new(name, me); coll(c).objects.link(o)
    if parent: o.parent = parent
    o.location = loc; o.scale = sc; o.rotation_euler = tuple(R(a) for a in rot)
    if m:   # malha compartilhada -> material por OBJETO
        o.material_slots[0].link = "OBJECT"; o.material_slots[0].material = m
    if bevel > 0:
        bv = o.modifiers.new("bv", "BEVEL"); bv.width = bevel; bv.segments = 2; bv.limit_method = "ANGLE"
        try: bv.use_clamp_overlap = True
        except Exception: pass
    if not shadow:
        try: o.visible_shadow = False
        except Exception: pass
    return o
for me_ in (M_CUBE, M_SPH, M_ICO, M_CYL, M_CYL8, M_CONE, M_HEX, M_CAPS, M_HEMI):
    me_.materials.append(None)
def empty(name, c, loc=(0, 0, 0), parent=None, rot=(0, 0, 0)):
    o = bpy.data.objects.new(name, None); coll(c).objects.link(o)
    if parent: o.parent = parent
    o.location = loc; o.rotation_euler = tuple(R(a) for a in rot); return o
def box(n, c, loc, sc, col, parent=None, rot=(0, 0, 0), bevel=None, **kw):
    bvl = bevel if bevel is not None else min(0.06, 0.12 * min(abs(s) for s in sc))
    return obj(n, M_CUBE, c, loc, sc, rot, col if isinstance(col, bpy.types.Material) else mat(col, **kw), parent, bvl)
def sph(n, c, loc, sc, col, parent=None, rot=(0, 0, 0), **kw):
    return obj(n, M_SPH, c, loc, sc if isinstance(sc, (tuple, list)) else (sc,) * 3, rot, col if isinstance(col, bpy.types.Material) else mat(col, **kw), parent)
def ico(n, c, loc, sc, col, parent=None, **kw):
    return obj(n, M_ICO, c, loc, sc if isinstance(sc, (tuple, list)) else (sc,) * 3, (0, 0, 0), col if isinstance(col, bpy.types.Material) else mat(col, **kw), parent)
def cyl(n, c, loc, sc, col, parent=None, rot=(0, 0, 0), me=None, **kw):
    return obj(n, me or M_CYL, c, loc, sc, rot, col if isinstance(col, bpy.types.Material) else mat(col, **kw), parent)
def cone(n, c, loc, sc, col, parent=None, rot=(0, 0, 0), **kw):
    return obj(n, M_CONE, c, loc, sc, rot, col if isinstance(col, bpy.types.Material) else mat(col, **kw), parent)
def caps(n, c, loc, r, h, col, parent=None, rot=(0, 0, 0), **kw):
    """capsula de raio r e comprimento total h (eixo Z)"""
    return obj(n, M_CAPS, c, loc, (2 * r, 2 * r, h / 2), rot, col if isinstance(col, bpy.types.Material) else mat(col, **kw), parent)
def text3d(n, c, body, loc, size, col, rot=(90, 0, 0), extrude=0.02, parent=None, emis=0.0):
    cu = bpy.data.curves.new(n, "FONT"); cu.body = body; cu.size = size; cu.extrude = extrude
    cu.align_x = "CENTER"; cu.align_y = "CENTER"
    o = bpy.data.objects.new(n, cu); coll(c).objects.link(o)
    if parent: o.parent = parent
    o.location = loc; o.rotation_euler = tuple(R(a) for a in rot); o.data.materials.append(mat(col, emis=emis)); return o

def hide(o, v=True):
    o.hide_render = v
    for c_ in o.children_recursive: c_.hide_render = v

# ---------------- curvas (fios, caminhos de corrente) ----------------
def curve_obj(n, c, pts, radius, m, res=2):
    cu = bpy.data.curves.new(n, "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = radius; cu.bevel_resolution = res
    cu.use_fill_caps = True
    sp = cu.splines.new("POLY"); sp.points.add(len(pts) - 1)
    for p_, q in zip(sp.points, pts): p_.co = (q[0], q[1], q[2], 1)
    o = bpy.data.objects.new(n, cu); coll(c).objects.link(o); o.data.materials.append(m); return o
def curve_set(o, pts):
    sp = o.data.splines[0]
    if len(sp.points) != len(pts):
        o.data.splines.clear(); sp = o.data.splines.new("POLY"); sp.points.add(len(pts) - 1)
    for p_, q in zip(sp.points, pts): p_.co = (q[0], q[1], q[2], 1)
def curve_reveal(o, u0, u1):
    o.data.bevel_factor_mapping_start = "SPLINE"; o.data.bevel_factor_mapping_end = "SPLINE"
    o.data.bevel_factor_start = clamp(u0); o.data.bevel_factor_end = clamp(u1)

# ---------------- render ----------------
try: scene.render.engine = "BLENDER_EEVEE"
except TypeError: scene.render.engine = "BLENDER_EEVEE_NEXT"
scene.render.resolution_x = 1080; scene.render.resolution_y = 1920
scene.render.resolution_percentage = 50 if MODE == "stills" else 100
scene.render.fps = FPS
try:
    scene.view_settings.view_transform = "AgX"; scene.view_settings.look = "AgX - Medium High Contrast"
except Exception:
    scene.view_settings.view_transform = "Standard"
scene.view_settings.exposure = CFG.get("exposicao", 0.0)
scene.render.image_settings.file_format = "PNG"; scene.render.image_settings.compression = 20
ee = scene.eevee
ee.taa_render_samples = 16 if MODE == "stills" else CFG.get("samples", 48)
for a_, v_ in (("use_shadows", True), ("use_raytracing", True), ("use_gtao", True), ("shadow_ray_count", 2), ("shadow_step_count", 8)):
    try: setattr(ee, a_, v_)
    except Exception: pass
try: ee.ray_tracing_options.resolution_scale = "2"
except Exception: pass
try: scene.render.use_motion_blur = False
except Exception: pass
scene.render.film_transparent = False

# ---------------- ceu degrade (crepusculo) + sol baixo ----------------
world = bpy.data.worlds.new("sky"); scene.world = world; world.use_nodes = True
wn = world.node_tree; bg = wn.nodes["Background"]
tc = wn.nodes.new("ShaderNodeTexCoord"); sep = wn.nodes.new("ShaderNodeSeparateXYZ"); sky = wn.nodes.new("ShaderNodeValToRGB")
wn.links.new(tc.outputs["Generated"], sep.inputs[0]); wn.links.new(sep.outputs["Z"], sky.inputs[0]); wn.links.new(sky.outputs[0], bg.inputs["Color"])
# v2: azul-marinho domina a metade de cima (ref @mundoremontado), faixa pessego so perto do horizonte
SKY = [(0.0, "#F0A27C"), (0.05, "#E5977F"), (0.13, "#B27A8A"), (0.24, "#55527F"), (0.40, "#24305E"), (0.75, "#141C40")]
def set_sky(stops=None, strength=1.0):
    stops = stops or SKY; els = sky.color_ramp.elements
    while len(els) < len(stops): els.new(0.5)
    for e_, (pos, col) in zip(els, stops): e_.position = pos; e_.color = hexc(col)
    bg.inputs["Strength"].default_value = strength
sund = bpy.data.lights.new("sun", "SUN"); sun = bpy.data.objects.new("sun", sund); scene.collection.objects.link(sun)
sund.angle = R(4)
def set_sun(strength=4.6, elev=12, az=-60, col="#FFAE70"):
    sund.energy = strength; sund.color = hexc(col)[:3]; sun.rotation_euler = (R(90 - elev), 0, R(az))
filld = bpy.data.lights.new("fill", "SUN"); fill = bpy.data.objects.new("fill", filld); scene.collection.objects.link(fill)
filld.angle = R(30)
def set_fill(strength=0.38, elev=40, az=120, col="#7F8FD6"):
    filld.energy = strength; filld.color = hexc(col)[:3]; fill.rotation_euler = (R(90 - elev), 0, R(az))
try: filld.use_shadow = False
except Exception: pass
PTS = []
def point(loc, col="#FFC98A", e=0.0, r=0.3, shadow=True):
    d = bpy.data.lights.new(f"pt{len(PTS)}", "POINT"); o = bpy.data.objects.new(d.name, d); scene.collection.objects.link(o)
    d.color = hexc(col)[:3]; d.energy = e; d.shadow_soft_size = r; o.location = loc
    try: d.use_shadow = shadow
    except Exception: pass
    PTS.append(o); return o
def dusk(sky_strength=1.0, sun=4.6):
    set_sky(SKY, sky_strength); set_sun(sun); set_fill()
dusk()

# ---------------- camera ----------------
camd = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", camd); scene.collection.objects.link(cam)
scene.camera = cam; camd.sensor_fit = "VERTICAL"; camd.clip_start = 0.02; camd.clip_end = 600
def set_cam(pos, tgt, fov, roll=0, dof=None):
    cam.location = pos
    d = Vector(tgt) - Vector(pos); cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    if roll: cam.rotation_euler.rotate_axis("Z", R(roll))
    camd.angle_y = R(fov)
    camd.dof.use_dof = dof is not None
    if dof is not None:
        camd.dof.focus_distance = d.length; camd.dof.aperture_fstop = dof
def orbit(center, radius, height, ang):
    c = Vector(center); return (c.x + radius * math.cos(R(ang)), c.y + radius * math.sin(R(ang)), c.z + height)

# ---------------- planos chaveados por ancora ----------------
SH = []
def shot(anchor):
    """@shot("L:k"): plano comeca 0,05 s antes da palavra k da linha L. fn(t, lt, u) com u = 0..1 dentro do plano"""
    def d(f): SH.append((anchor, f)); return f
    return d
def SHOT(anchor, cam0, cam1, tgt0, tgt1, fov0, fov1=None, roll=0, dof=None, fx=None, ease_=smooth):
    """plano em forma de DADOS: camera vai de cam0->cam1 olhando tgt0->tgt1 (suave). fx(t, lt, u) opcional anima o resto."""
    def f(t, lt, u):
        e = ease_(u); set_cam(vlerp(cam0, cam1, e), vlerp(tgt0, tgt1, e), lerp(fov0, fov1 or fov0, e), roll, dof)
        if fx: fx(t, lt, u)
    f.__name__ = f"shot_{anchor}"; SH.append((anchor, f)); return f

def run(reset=None):
    shots = sorted(((0.0 if idx(a) == 0 else T(a) - 0.05), f) for a, f in SH)
    def frame_state(fr):
        t = fr / FPS
        k = max(i for i, (t0, fn) in enumerate(shots) if t >= t0 - 1e-6)
        t0, fn = shots[k]; t1 = shots[k + 1][0] if k + 1 < len(shots) else END
        if reset: reset(t)
        fn(t, t - t0, (t - t0) / max(0.01, t1 - t0))
        bpy.context.view_layer.update(); return k
    out = os.path.join(W, "frames" if MODE == "frames" else "stills")
    if MODE == "list":
        for k, (t0, fn) in enumerate(shots):
            t1 = shots[k + 1][0] if k + 1 < len(shots) else END
            print("SHOT", k, round(t0, 2), round(t1 - t0, 2), fn.__name__)
        print("END", END, "NF", NF); return
    os.makedirs(out, exist_ok=True)
    if MODE == "stills":
        for k, (t0, fn) in enumerate(shots):
            t1 = shots[k + 1][0] if k + 1 < len(shots) else END
            fr = int(((t0 + t1) / 2) * FPS); frame_state(fr)
            scene.render.filepath = os.path.join(out, f"s{k:02d}_{fr:04d}.png"); bpy.ops.render.render(write_still=True)
    else:
        f1 = NF if F1 < 0 else min(F1, NF)
        for fr in range(F0, f1):
            p = os.path.join(out, f"f{fr:04d}.png")
            if os.path.exists(p) and os.path.getsize(p) > 1000: continue
            frame_state(fr); scene.render.filepath = p; bpy.ops.render.render(write_still=True)
    print("DONE")

# =====================================================================
# BLOCOS DE CENARIO REUTILIZAVEIS (bairro ao entardecer)
# =====================================================================
WINDOWS = []          # materiais de janela (acender/apagar)
WIN_ON = "#FFD9A0"; WIN_OFF = "#2A2F45"
def win_mat(key):
    m = mat(WIN_OFF, 0.4, key=f"win_{key}"); WINDOWS.append(m); return m
def windows(on=True, e=2.2):
    for m in WINDOWS:
        set_base(m, WIN_ON if on else WIN_OFF); set_emis(m, e if on else 0.0, "#FFC27A")

HOUSE_COLS = ["#C9521F", "#D46A3A", "#D99A8A", "#E8C9A8", "#B8472A", "#E2A27A", "#CF7B5E"]
def house(c, x, y, w=7, d=7, h=6.5, wall=None, face=-1, floors=2, trim="#3A2A2A", door="#6B3A2A"):
    """sobrado de telhado plano com platibanda; face=-1 => frente voltada pra -Y, +1 => pra +Y"""
    wall = wall or random.choice(HOUSE_COLS)
    box(c + "_hw", c, (x, y, (h - 0.3) / 2), (w, d, h + 0.3), wall, bevel=0.05)
    box(c + "_hr", c, (x, y, h + 0.15), (w + 0.25, d + 0.25, 0.3), trim, bevel=0.04)
    box(c + "_hr2", c, (x, y, h + 0.32), (w - 0.6, d - 0.6, 0.06), "#4A3A3A", bevel=0.01)
    fy = y + face * (d / 2 + 0.02)
    box(c + "_door", c, (x - w * 0.22, fy, 1.15), (1.1, 0.12, 2.3), door, bevel=0.03)
    k = len(WINDOWS)
    for fl in range(floors):
        zz = 1.6 + fl * 2.6 if fl else 1.5
        for wx in ((w * 0.18,) if fl == 0 else (-w * 0.25, w * 0.25)):
            box(c + "_wf", c, (x + wx, fy, zz), (1.7, 0.16, 1.5), "#F2E6D8", bevel=0.03)
            box(c + "_wi", c, (x + wx, fy + face * 0.05, zz), (1.4, 0.12, 1.2), win_mat(f"{c}{k}"), bevel=0.01)
            k += 1
    return wall

def tree(c, x, y, s=1.0, col="#3F6B2E"):
    cyl(c + "_tt", c, (x, y, 1.1 * s), (0.32 * s, 0.32 * s, 2.2 * s), "#6B4A32")
    for dx, dy, dz, r in ((0, 0, 3.0, 1.9), (0.8, 0.3, 2.5, 1.3), (-0.8, -0.2, 2.6, 1.3), (0.1, -0.5, 3.7, 1.2)):
        ico(c + "_tl", c, (x + dx * s, y + dy * s, dz * s), (r * s,) * 3, col, rough=0.9)

def street(c, x0=-90, x1=90, w=8.0, walk=3.2):
    L = x1 - x0; cx = (x0 + x1) / 2
    box(c + "_asf", c, (cx, 0, -0.1), (L, w, 0.2), "#2E2F36", bevel=0.0, rough=0.9)
    for s in (-1, 1):
        box(c + "_walk", c, (cx, s * (w / 2 + walk / 2), 0.0), (L, walk, 0.3), "#8C8790", bevel=0.03)
        box(c + "_curb", c, (cx, s * (w / 2 + 0.08), 0.02), (L, 0.18, 0.34), "#A8A3AA", bevel=0.03)
    x = x0 + 1
    while x < x1:
        box(c + "_dash", c, (x, 0, 0.005), (2.2, 0.16, 0.02), "#E8E4DC", bevel=0.0, emis=0.15); x += 5
    box(c + "_lot", c, (cx, 0, -0.12), (L + 60, 170, 0.2), "#3E3A3C", bevel=0.0)

def street_lamp(c, x, y, face=1):
    cyl(c + "_sl", c, (x, y, 3.0), (0.14, 0.14, 6.0), "#5A5A62")
    box(c + "_sla", c, (x, y + face * 0.8, 6.0), (0.14, 1.7, 0.12), "#5A5A62", bevel=0.02)
    m = mat("#FFF1D0", 0.4, emis=3.0, key=f"lamp_{x}_{y}"); LAMPS.append(m)
    box(c + "_slh", c, (x, y + face * 1.55, 5.92), (0.42, 0.7, 0.12), m, bevel=0.03)
LAMPS = []
def lamps(on=True):
    for m in LAMPS: set_emis(m, 3.0 if on else 0.0)

# ---------------- poste com cruzeta, 3 fios e lampadinhas ----------------
WIRE_Y = (2.7, 4.5, 6.3)     # y dos 3 fios (paralelos ao eixo X)
WIRE_Z = 10.45                # altura do fio em cima do isolador
WIRE_R = 0.045                # raio do fio (v2: mais grosso, como a ref)
POLE_Y = 4.5
def pole(c, x, y=POLE_Y, h=10.0, insulators=True, ins_mat=None):
    cyl(c + "_pole", c, (x, y, h / 2), (0.42, 0.42, h), "#9C9AA2", me=M_CYL8)
    cyl(c + "_poletop", c, (x, y, h + 0.7), (0.36, 0.36, 1.4), "#9C9AA2", me=M_CYL8)
    box(c + "_arm", c, (x, y, h), (0.32, 4.5, 0.3), "#4A3A30", bevel=0.03)
    for k in range(int((h - 2.4) / 0.45)):          # degraus (pinos) de subir no poste
        sx = 1 if k % 2 else -1
        cyl(c + "_peg", c, (x + sx * 0.3, y, 2.4 + 0.45 * k), (0.05, 0.05, 0.22), "#D8D6D0", rot=(0, 90, 0))
    for s in (-1, 1):
        box(c + "_brace", c, (x, y + s * 0.9, h - 0.6), (0.1, 0.1, 1.5), "#555555", rot=(s * 40, 0, 0), bevel=0.0)
    ins = []
    if insulators:
        for wy in WIRE_Y:
            ins.append(insulator(c + f"_ins{wy}", c, (x, wy, h + 0.15), ins_mat))
    return ins
def insulator(n, c, loc, m=None, parent=None):
    """isolador de pino: 3 saias de porcelana + cabeca; base em loc (z = topo da cruzeta)"""
    m = m or mat("#EDEAE4", 0.35, spec=0.6, key="porcelana")
    root = empty(n, c, loc, parent)
    cyl(n + "_pin", c, (0, 0, 0.06), (0.06, 0.06, 0.12), "#6A6A70", root)
    for k, (z, r) in enumerate(((0.12, 0.34), (0.2, 0.28), (0.26, 0.22))):
        cone(n + f"_sk{k}", c, (0, 0, z + 0.03), (r, r, 0.09), m, root)
        cyl(n + f"_sb{k}", c, (0, 0, z), (r, r, 0.03), m, root)
    cyl(n + "_neck", c, (0, 0, 0.21), (0.13, 0.13, 0.22), m, root)
    sph(n + "_head", c, (0, 0, 0.3), (0.16, 0.16, 0.1), m, root)
    return root

BEADM = mat("#FFF1D2", 0.3, emis=3.2, key="bead")
WIREM = mat("#18181C", 0.45, key="wire")
def sag(x, xa, xb, za, zb, s):
    u = (x - xa) / (xb - xa); return lerp(za, zb, u) - s * 4 * u * (1 - u)
def move_beads(wy, lift):
    for o, x, z in BEADS.get(wy, []):
        dy, dz = lift(x) if lift else (0, 0); o.location = (x, wy + dy, z + dz)
def wire_pts(y, poles_x, z=WIRE_Z, s=0.55, step=0.5, lift=None):
    """pontos do fio entre os postes (catenaria simples). lift(x)->(dy,dz) desloca o fio (ex.: vara de manobra)"""
    pts = []
    for a, b in zip(poles_x[:-1], poles_x[1:]):
        n = int((b - a) / step)
        for i in range(n):
            x = a + (b - a) * i / n; zz = sag(x, a, b, z, z, s); dy = dz = 0
            if lift: dy, dz = lift(x)
            pts.append((x, y + dy, zz + dz))
    pts.append((poles_x[-1], y, z)); return pts
BEADS = {}   # y do fio -> [(obj, x, z)] (pra seguir o fio quando ele e movido)
def wires(c, poles_x, beads=True, bead_every=1.6):
    W_ = []
    for wy in WIRE_Y:
        W_.append(curve_obj(c + f"_wire{wy}", c, wire_pts(wy, poles_x), WIRE_R, WIREM))
        if beads:
            for a, b in zip(poles_x[:-1], poles_x[1:]):
                x = a + 1.2
                while x < b - 1.0:
                    if abs(x) > 0.7:   # nada colado no isolador do meio
                        z = sag(x, a, b, WIRE_Z, WIRE_Z, 0.55)
                        o = obj(c + "_bd", M_HEX, c, (x, wy, z), (0.2, 0.2, 0.13), (0, 90, 0), BEADM, shadow=False)
                        BEADS.setdefault(wy, []).append((o, x, z))
                    x += bead_every
    return W_

# ---------------- pessoa low-poly (eletricista, manequim etc.) ----------------
class Pessoa:
    """boneco estilizado ~1,75 m, pes em z=0, frente pra -Y local (yaw=180 olha pra +Y). Ombro a 1,44 m.
    pose (graus): aL/aR NEGATIVO = levanta o braco pra frente (-90 = horizontal); sL/sR positivo = abre pro lado (90 = T);
    eL/eR negativo = dobra o cotovelo pra frente; hy vira a cabeca; hp inclina; lean; legs (balanco p/ escalada)"""
    def __init__(s, name, c, skin="#F0C7A2", shirt="#1F2A4A", pants="#1F2A4A", glove="#C8302C", helmet="#F4F4F0",
                 stripes="#E8EEF2", boots="#2A2420", eyes=True, mono=None):
        s.name = name; s.c = c
        M = (lambda col, **k: mono if mono else mat(col, **k))
        s.mats = []
        s.root = empty(name, c)
        s.hip = empty(name + "_hip", c, (0, 0, 0.88), s.root)
        s.legs = {}
        for side, x in (("L", -0.11), ("R", 0.11)):
            lg = empty(f"{name}_lg{side}", c, (x, 0, 0), s.hip); s.legs[side] = lg
            caps(f"{name}_leg{side}", c, (0, 0, -0.42), 0.085, 0.86, M(pants), lg)
            box(f"{name}_boot{side}", c, (0, -0.05, -0.84), (0.17, 0.28, 0.12), M(boots), lg, bevel=0.04)
        s.chest = empty(name + "_chest", c, (0, 0, 0.0), s.hip)
        s.torso = caps(name + "_torso", c, (0, 0, 0.32), 0.19, 0.72, M(shirt), s.chest)
        s.torso.scale.y *= 0.72
        s.strip = []
        if not mono:
            for z in (0.18, 0.40):
                o = obj(name + "_strip", M_CYL, c, (0, 0, z), (0.392, 0.282, 0.05), (0, 0, 0), mat(stripes, 0.3, emis=0.25, key="refl"), s.chest)
                s.strip.append(o)
        if not mono:   # v2: cinto escuro com fivela
            obj(name + "_belt", M_CYL, c, (0, 0, 0.03), (0.392, 0.282, 0.07), (0, 0, 0), mat("#2A2420", 0.6), s.chest)
            box(name + "_buck", c, (0, -0.142, 0.03), (0.08, 0.02, 0.06), "#C9A03A", s.chest, bevel=0.01, metal=0.6, rough=0.4)
        s.neck = empty(name + "_neck", c, (0, 0, 0.66), s.chest)
        s.head = sph(name + "_head", c, (0, 0, 0.14), (0.25, 0.25, 0.28), M(skin), s.neck)
        if eyes and not mono:
            for x in (-0.045, 0.045):
                sph(name + "_eye", c, (x, -0.122, 0.16), (0.038, 0.03, 0.046), "#1A1A1E", s.neck)
        s.helmet = None
        if helmet and not mono:
            # v2: capacete de obra = casco (meia-esfera) EM CIMA da testa, rosto e olhos livres, aba + bico + friso
            s.helmet = empty(name + "_helm", c, (0, 0, 0.205), s.neck)
            hm = mat(helmet, 0.3, spec=0.6)
            obj(name + "_hel", M_HEMI, c, (0, 0.005, 0.0), (0.3, 0.32, 0.27), (0, 0, 0), hm, s.helmet)
            cyl(name + "_heb", c, (0, 0.0, 0.0), (0.34, 0.36, 0.022), hm, s.helmet)
            box(name + "_hep", c, (0, -0.17, -0.004), (0.2, 0.1, 0.02), hm, s.helmet, rot=(-8, 0, 0), bevel=0.03)
            box(name + "_her", c, (0, 0.0, 0.125), (0.05, 0.27, 0.035), hm, s.helmet, bevel=0.015)
            box(name + "_hes", c, (0, -0.135, 0.06), (0.07, 0.03, 0.05), "#E0A526", s.helmet, rot=(-30, 0, 0), bevel=0.01)
        s.sh = {}; s.el = {}; s.hand = {}
        for side, x in (("L", -0.25), ("R", 0.25)):
            sp = empty(f"{name}_sh{side}", c, (x, 0, 0.56), s.chest); s.sh[side] = sp
            caps(f"{name}_ua{side}", c, (0, 0, -0.15), 0.065, 0.34, M(shirt), sp)
            el = empty(f"{name}_el{side}", c, (0, 0, -0.29), sp); s.el[side] = el
            caps(f"{name}_fa{side}", c, (0, 0, -0.13), 0.058, 0.3, M(shirt), el)
            if not mono:   # v2: faixa refletiva na manga + punho (cano) da luva
                obj(f"{name}_sst{side}", M_CYL, c, (0, 0, -0.12), (0.142, 0.142, 0.04), (0, 0, 0), mat(stripes, 0.3, emis=0.25, key="refl"), sp)
                cyl(f"{name}_gc{side}", c, (0, 0, -0.25), (0.135, 0.135, 0.11), M(glove), el)
            s.hand[side] = box(f"{name}_hd{side}", c, (0, 0, -0.35), (0.11, 0.075, 0.15), M(glove), el, bevel=0.03)
            caps(f"{name}_tb{side}", c, (0.05 if side == "R" else -0.05, -0.03, -0.32), 0.025, 0.09, M(glove), el, rot=(25, 0, 0))
        s.reset()
    def reset(s):
        s.p = dict(aL=0, aR=0, sL=8, sR=8, eL=0, eR=0, hy=0, hp=0, lean=0, legs=0, yaw=0)
    def place(s, loc, yaw=0): s.root.location = loc; s.p["yaw"] = yaw
    def apply(s):
        p = s.p
        s.root.rotation_euler = (0, 0, R(p["yaw"]))
        s.chest.rotation_euler = (R(-p["lean"]), 0, 0)
        s.neck.rotation_euler = (R(p["hp"]), 0, R(p["hy"]))
        s.sh["L"].rotation_euler = (R(p["aL"]), R(p["sL"]), 0); s.sh["R"].rotation_euler = (R(p["aR"]), R(-p["sR"]), 0)
        s.el["L"].rotation_euler = (R(p["eL"]), 0, 0); s.el["R"].rotation_euler = (R(p["eR"]), 0, 0)
        s.legs["L"].rotation_euler = (R(p["legs"]), 0, 0); s.legs["R"].rotation_euler = (R(-p["legs"]), 0, 0)
    def show(s, v): hide(s.root, not v)
    def hand_world(s, side):
        bpy.context.view_layer.update(); return s.hand[side].matrix_world.translation.copy()

# ---------------- passarinho ----------------
class Passarinho:
    """v2 (silhueta clara): corpo-ovo inclinado, cabeca grande, asa escura, cauda em leque, barriga laranja, pernas curtas.
    Pes em z=0 (pousar com root.z = topo do fio). Frente = +X. ~0,32 m de comprimento."""
    def __init__(s, name, c, body="#8E5330", belly="#EE7E2E", beak="#F2B533", wing="#6A3A22"):
        s.root = empty(name, c)
        s.mb = mat(body, 0.65); s.mbe = mat(belly, 0.65); s.mw = mat(wing, 0.7)
        s.legm = mat("#3A2A20", 0.6, key=name + "_leg")
        s.body = sph(name + "_b", c, (-0.01, 0, 0.105), (0.24, 0.15, 0.155), s.mb, s.root, rot=(0, -18, 0))
        sph(name + "_be", c, (0.03, 0, 0.085), (0.17, 0.125, 0.115), s.mbe, s.root, rot=(0, -10, 0))
        for yy in (-1, 1):
            sph(name + "_w", c, (-0.035, yy * 0.07, 0.12), (0.17, 0.03, 0.09), s.mw, s.root, rot=(yy * 6, -20, 0))
        for k, a_ in enumerate((-22, 0, 22)):
            box(name + "_tail", c, (-0.15, 0, 0.13), (0.12, 0.035, 0.012), s.mw, s.root, rot=(a_, -28, 0), bevel=0.004)
        s.headp = empty(name + "_hp", c, (0.075, 0, 0.19), s.root)
        sph(name + "_h", c, (0, 0, 0), (0.125, 0.115, 0.115), s.mb, s.headp)
        sph(name + "_ch", c, (0.03, 0, -0.03), (0.07, 0.085, 0.06), s.mbe, s.headp)
        cone(name + "_bk", c, (0.072, 0, -0.006), (0.034, 0.03, 0.055), beak, s.headp, rot=(0, 90, 0))
        for yy in (-0.045, 0.045):
            sph(name + "_e", c, (0.035, yy, 0.016), (0.022, 0.016, 0.024), "#101012", s.headp)
            sph(name + "_eh", c, (0.042, yy * 1.18, 0.024), (0.007, 0.005, 0.007), mat("#FFFFFF", 0.2, emis=0.8, key="olho_brilho"), s.headp)
        s.legs = [cyl(name + f"_lg{k}", c, (0.01, yy, 0.022), (0.011, 0.011, 0.044), s.legm, s.root) for k, yy in enumerate((-0.028, 0.028))]
        for yy in (-0.028, 0.028):
            for a_ in (-25, 0, 25):
                box(name + "_ft", c, (0.012, yy, 0.003), (0.035, 0.007, 0.006), s.legm, s.root, rot=(0, 0, a_), bevel=0.0)
    def xray(s, on):
        set_emis(s.legm, 2.0 if on else 0.0, "#FFB21E")
        set_base(s.legm, "#FFD447" if on else "#3A2A20")

# ---------------- mao/luva com dedos finos (closes de luva em camadas) ----------------
def mao(n, c, m, parent=None, s_=1.0, cuff_h=0.9, cuff_r=0.27, finger_r=0.046, flare=True, grow=0.0):
    """mao de luva: palma reta, 4 dedos FINOS separados (2 falanges), polegar aberto e punho (cano) longo.
    Palma pra -Y (camera em -Y ve a palma). Base da palma em z=-0.27; pontas dos dedos ~z=+0.62.
    Camada POR CIMA (ex.: couro sobre borracha): mesma s_ e grow=0.012 (engrossa sem deslocar as juntas; escala uniforme deixa a de baixo vazar)."""
    g = grow; finger_r += g
    root = empty(n, c, (0, 0, 0), parent); root.scale = (s_,) * 3
    box(n + "_palm", c, (0, 0, 0), (0.5 + 2 * g, 0.16 + 2 * g, 0.54 + 2 * g), m, root, bevel=0.09)
    for k, (fx, fl, a_) in enumerate(((-0.18, 0.30, 7), (-0.06, 0.36, 2), (0.06, 0.34, -2), (0.18, 0.27, -7))):
        fr = empty(n + f"_fr{k}", c, (fx, 0, 0.24), root, rot=(0, a_, 0))
        caps(n + f"_f{k}a", c, (0, 0, fl * 0.27), finger_r * 1.06, fl * 0.56, m, fr)
        caps(n + f"_f{k}b", c, (0, -0.004, fl * 0.7), finger_r, fl * 0.5, m, fr, rot=(-4, 0, 0))
    th = empty(n + "_thr", c, (0.24, -0.02, -0.06), root, rot=(0, 48, 0))
    caps(n + "_th1", c, (0, 0, 0.09), finger_r * 1.25, 0.2, m, th)
    caps(n + "_th2", c, (0, -0.005, 0.21), finger_r * 1.1, 0.16, m, th, rot=(-6, 0, 0))
    cyl(n + "_wr", c, (0, 0, -0.3), (0.46 + 2 * g, 0.2 + 2 * g, 0.12), m, root)
    cuff_r += g
    cyl(n + "_cuff", c, (0, 0, -0.33 - cuff_h / 2), (cuff_r * 2, cuff_r * 1.15, cuff_h), m, root)
    if flare: cyl(n + "_lip", c, (0, 0, -0.33 - cuff_h + 0.03), (cuff_r * 2.12, cuff_r * 1.25, 0.06), m, root)
    return root

def grade(n, c, center, w=14.0, h=14.0, step=0.4, base="#16203F", line="#2E3D70"):
    """fundo de estudio azul-marinho com grade (closes de objeto, como a ref). Plano vertical (XZ) voltado pra -Y."""
    root = empty(n, c, center, rot=(90, 0, 0))
    box(n + "_bg", c, (0, 0, -0.02), (w, h, 0.02), mat(base, 0.9, key=n + "_bg"), root, bevel=0.0)
    lm = mat(line, 0.6, emis=0.35, key=n + "_ln")
    k = int(w / step)
    for i in range(-k // 2, k // 2 + 1):
        box(n + "_lx", c, (i * step, 0, 0), (0.012, h, 0.006), lm, root, bevel=0.0, shadow=False)
    k = int(h / step)
    for i in range(-k // 2, k // 2 + 1):
        box(n + "_ly", c, (0, i * step, 0), (w, 0.012, 0.006), lm, root, bevel=0.0, shadow=False)
    return root
