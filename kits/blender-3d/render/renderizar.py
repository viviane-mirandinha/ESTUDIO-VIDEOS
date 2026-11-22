# Kit Blender do Estúdio. Baseado no pipeline do kit cotidiano.explicado (mesmo autor).
"""
Renderiza no Blender a cena "assada" pelo kit (nível 4 · Master).

Chamado por scripts/blender/render.mjs assim:
    blender -b --factory-startup -P scripts/blender/renderizar.py -- <pasta> [--quadros=1,60,120] [--amostras=32]

<pasta> tem cena.glb e quadros.json (de assar.mjs). Os quadros saem em
<pasta>/quadros/q0001.png… em 1080x1920. A câmera, o fundo e a luz de cada
quadro vêm do quadros.json — a mesma câmera do modo rápido, para as etiquetas
continuarem presas às peças.
"""

import json
import math
import os
import sys

import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
pasta = os.path.abspath(args[0])


def opcao(nome, padrao=None):
    for a in args[1:]:
        if a.startswith(f"--{nome}="):
            return a.split("=", 1)[1]
    return padrao


dados = json.load(open(os.path.join(pasta, "quadros.json")))
# estilo do render escolhido no plano (material, luz, contorno); sem arquivo = padrão (vinil, luz suave)
_rj = os.path.join(pasta, "render.json")
ESTILO = json.load(open(_rj)) if os.path.exists(_rj) else {}
MATERIAL = ESTILO.get("material", "vinil")
LUZ_MODO = ESTILO.get("luz", "suave")
CONTORNO = bool(ESTILO.get("contorno", MATERIAL == "desenho"))
fps = dados["fps"]
total = dados["total"]

# ------------------------------------------------------------- cena limpa e o .glb

bpy.ops.wm.read_factory_settings(use_empty=True)
cena = bpy.context.scene
# o fps tem que estar certo ANTES de abrir o .glb (o Blender converte o tempo em quadros com ele)
cena.render.fps = fps
bpy.ops.import_scene.gltf(filepath=os.path.join(pasta, "cena.glb"))
# o .glb começa no quadro 0 (tempo 0); a câmera e o fundo seguem a mesma contagem
cena.frame_start = 0
cena.frame_end = total - 1


def b(v):
    """Ponto do kit (y para cima) → Blender (z para cima)."""
    return Vector((v[0], -v[2], v[1]))


def cor(hexa):
    h = hexa.lstrip("#")
    return [((int(h[i : i + 2], 16) / 255) ** 2.2) for i in (0, 2, 4)]


# ------------------------------------------------------------- modelos .glb importados (personagem, cenário, objeto)

_mj = os.path.join(pasta, "modelos.json")
MODELOS = json.load(open(_mj)) if os.path.exists(_mj) else {"modelos": [], "cenas": []}
raizes = {}
mats_livres = set()   # materiais de modelos que pediram "estilizar": false (ficam como vieram)
for m in MODELOS["modelos"]:
    antes = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.join(pasta, m["arquivo"]))
    novos = [o for o in bpy.data.objects if o not in antes]
    raiz = bpy.data.objects.new("modelo_" + m["id"], None)
    cena.collection.objects.link(raiz)
    for o in novos:
        if o.parent is None or o.parent not in novos:
            o.parent = raiz
    raizes[m["id"]] = raiz
    if not m.get("estilizar", True):
        for o in novos:
            for slot in getattr(o, "material_slots", []):
                if slot.material:
                    mats_livres.add(slot.material)
# em cada cena, cada modelo entra (posição, giro, escala) ou some (escala 0); o valor anterior segura até o corte
_prev = {}
for cm in MODELOS["cenas"]:
    f0 = cm["f0"]
    ativos = {it["id"]: it for it in cm["itens"]}
    for mid, raiz in raizes.items():
        it = ativos.get(mid)
        novo = (b(it["pos"]), it["giro"], it["escala"]) if it else (Vector((0, 0, 0)), 0.0, 0.0)
        if mid in _prev and f0 > 0:
            raiz.location, raiz.rotation_euler, raiz.scale = _prev[mid][0], (0, 0, _prev[mid][1]), (_prev[mid][2],) * 3
            for caminho in ("location", "rotation_euler", "scale"):
                raiz.keyframe_insert(caminho, frame=f0 - 1)
        raiz.location, raiz.rotation_euler, raiz.scale = novo[0], (0, 0, novo[1]), (novo[2],) * 3
        for caminho in ("location", "rotation_euler", "scale"):
            raiz.keyframe_insert(caminho, frame=f0)
        _prev[mid] = novo

# ------------------------------------------------------------- materiais com acabamento de filme

def _entrada(no, *nomes):
    for n in nomes:
        if n in no.inputs:
            return no.inputs[n]
    return None


def material_vinil(mat, pbr):
    # vinil e plástico: um pouco de verniz e brilho suave nas bordas
    if "Coat Weight" in pbr.inputs and pbr.inputs["Coat Weight"].default_value < 0.05 and pbr.inputs["Roughness"].default_value < 0.5:
        pbr.inputs["Coat Weight"].default_value = 0.3
    if "Sheen Weight" in pbr.inputs and pbr.inputs["Roughness"].default_value > 0.7:
        pbr.inputs["Sheen Weight"].default_value = 0.15


def material_massinha(mat, pbr):
    # massinha de modelar: fosca, sem verniz, com um véu macio nas bordas
    pbr.inputs["Roughness"].default_value = max(0.8, pbr.inputs["Roughness"].default_value)
    for nome, valor in (("Coat Weight", 0.0), ("Sheen Weight", 0.35), ("Metallic", 0.0)):
        if nome in pbr.inputs:
            pbr.inputs[nome].default_value = valor
    esp = _entrada(pbr, "Specular IOR Level", "Specular")
    if esp is not None:
        esp.default_value = 0.15


def material_desenho(mat, pbr):
    """Cor chapada em degraus (3 tons) com sombra marcada: estilo desenho/quadrinho."""
    nt = mat.node_tree
    cor_base = tuple(pbr.inputs["Base Color"].default_value)
    saida = next((n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"), None)
    if not saida:
        return
    # luz do desenho = quanto a superfície aponta para a luz principal (não depende do motor de luz do Blender)
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    ponto = nt.nodes.new("ShaderNodeVectorMath")
    ponto.operation = "DOT_PRODUCT"
    ponto.inputs[1].default_value = (0.42, -0.5, 0.70)
    rampa = nt.nodes.new("ShaderNodeValToRGB")
    rampa.color_ramp.interpolation = "CONSTANT"
    rampa.color_ramp.elements[0].position = 0.0
    rampa.color_ramp.elements[0].color = (0.5, 0.5, 0.5, 1)
    e1 = rampa.color_ramp.elements.new(0.22)
    e1.color = (0.78, 0.78, 0.78, 1)
    e2 = rampa.color_ramp.elements.new(0.58)
    e2.color = (1, 1, 1, 1)
    nt.links.new(geo.outputs["Normal"], ponto.inputs[0])
    mistura = nt.nodes.new("ShaderNodeMix")
    mistura.data_type = "RGBA"
    mistura.blend_type = "MULTIPLY"
    mistura.inputs["Factor"].default_value = 1.0
    a = next(i for i in mistura.inputs if i.identifier == "A_Color")
    b = next(i for i in mistura.inputs if i.identifier == "B_Color")
    b.default_value = cor_base
    emissao = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(ponto.outputs["Value"], rampa.inputs["Fac"])
    nt.links.new(rampa.outputs["Color"], a)
    res = next(o for o in mistura.outputs if o.identifier == "Result_Color")
    nt.links.new(res, emissao.inputs["Color"])
    nt.links.new(emissao.outputs["Emission"], saida.inputs["Surface"])


for mat in bpy.data.materials:
    if not mat.use_nodes or mat in mats_livres:
        continue
    pbr = next((n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if not pbr:
        continue
    alpha = pbr.inputs["Alpha"].default_value
    vidro = alpha < 0.6
    if MATERIAL == "massinha":
        material_massinha(mat, pbr)
    elif MATERIAL == "desenho" and not vidro:
        material_desenho(mat, pbr)
    else:
        material_vinil(mat, pbr)
    # vidro: transparência de verdade
    if vidro and MATERIAL != "desenho":
        pbr.inputs["Transmission Weight"].default_value = 0.9
        pbr.inputs["Roughness"].default_value = 0.04
        pbr.inputs["Alpha"].default_value = max(alpha, 0.35)
    if hasattr(mat, "surface_render_method"):
        mat.surface_render_method = "BLENDED" if alpha < 0.999 else "DITHERED"

# ------------------------------------------------------------- câmera seguindo o quadros.json

dados_cam = bpy.data.cameras.new("camera")
dados_cam.sensor_fit = "VERTICAL"
cam = bpy.data.objects.new("camera", dados_cam)
cena.collection.objects.link(cam)
cena.camera = cam
for i, q in enumerate(dados["quadros"]):
    f = i
    pos = b(q["pos"])
    alvo = b(q["alvo"])
    cam.location = pos
    cam.rotation_mode = "QUATERNION"
    cam.rotation_quaternion = (alvo - pos).to_track_quat("-Z", "Y")
    dados_cam.angle = math.radians(q["fov"])
    cam.keyframe_insert("location", frame=f)
    cam.keyframe_insert("rotation_quaternion", frame=f)
    dados_cam.keyframe_insert("lens", frame=f)

# ------------------------------------------------------------- luz de estúdio e fundo

mundo = bpy.data.worlds.new("mundo")
cena.world = mundo
mundo.use_nodes = True
fundo = mundo.node_tree.nodes["Background"]
for i, q in enumerate(dados["quadros"]):
    fundo.inputs[0].default_value = (*cor(q["fundo"]), 1)
    fundo.inputs[1].default_value = (0.55 if LUZ_MODO == "suave" else 0.35 if LUZ_MODO == "dura" else 0.7) * q["luz"]
    fundo.inputs[0].keyframe_insert("default_value", frame=i)
    fundo.inputs[1].keyframe_insert("default_value", frame=i)


def luz(nome, tipo, energia, cor_hex, pos, alvo, tamanho):
    d = bpy.data.lights.new(nome, tipo)
    d.energy = energia
    d.color = cor(cor_hex)
    if tipo == "AREA":
        d.size = tamanho
    if tipo == "SUN":
        d.angle = math.radians(tamanho)
    o = bpy.data.objects.new(nome, d)
    cena.collection.objects.link(o)
    o.location = b(pos)
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = (b(alvo) - b(pos)).to_track_quat("-Z", "Y")
    return d


# principal, preenchimento e contraluz (separa do fundo); o modo de luz muda força, cor e dureza
LUZES = {
    "suave": dict(sol=3.2, sol_cor="#fff1dc", sol_ang=8, fill=900, contra=1200),
    "dura": dict(sol=4.6, sol_cor="#fff6e8", sol_ang=1.5, fill=350, contra=1200),
    "neutra": dict(sol=3.0, sol_cor="#ffffff", sol_ang=6, fill=1100, contra=800),
}
L = LUZES.get(LUZ_MODO, LUZES["suave"])
principal = luz("principal", "SUN", L["sol"], L["sol_cor"], [6, 10, 7], [0, 0, 0], L["sol_ang"])
luz("preenchimento", "AREA", L["fill"], "#d6e6ff" if LUZ_MODO != "neutra" else "#ffffff", [-8, 5, 9], [0, 1.5, 0], 9)
luz("contraluz", "AREA", L["contra"], "#ffe2c0" if LUZ_MODO != "neutra" else "#ffffff", [2, 7, -7], [0, 1.5, 0], 6)
# a força da luz acompanha a "luz" de cada quadro (noite, dia)
for i, q in enumerate(dados["quadros"]):
    principal.energy = L["sol"] * q["luz"]
    principal.keyframe_insert("energy", frame=i)

# cenas com teto: INTERIOR=1 liga luzes dentro do cômodo, conforme a "luz" passa de 1.1
if os.environ.get("INTERIOR"):
    internas = [
        (luz("int_frente", "AREA", 750, "#ffd9ae", [3.5, 5.3, 7.5], [0, 1.5, 2], 8), 750),
        (luz("int_parede", "AREA", 900, "#ffe6c8", [-6, 5.3, 3], [-6, 2, -6], 12), 900),
        (luz("int_cozinha", "AREA", 800, "#ffc98a", [6, 5.3, 0], [6, 1, -6], 8), 800),
        (luz("int_rosto", "AREA", 220, "#ffe9d0", [4, 1.2, 8], [0, 2.4, 2.3], 5), 220),
    ]
    for i, q in enumerate(dados["quadros"]):
        k = max(0.0, min(1.0, (q["luz"] - 1.1) / 1.1))
        for d, e in internas:
            d.energy = e * k
            d.keyframe_insert("energy", frame=i)

# ------------------------------------------------------------- motor de render

motores = [m.identifier for m in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
cena.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in motores else "BLENDER_EEVEE"
ee = cena.eevee
amostras = int(opcao("amostras", 48))
for nome, valor in [("taa_render_samples", amostras), ("use_raytracing", True), ("use_shadows", True), ("shadow_ray_count", 2), ("shadow_step_count", 6), ("use_gtao", True), ("fast_gi_method", "GLOBAL_ILLUMINATION")]:
    if hasattr(ee, nome):
        try:
            setattr(ee, nome, valor)
        except Exception:
            pass
cena.render.resolution_x = int(os.environ.get("LARGURA", 1080))
cena.render.resolution_y = int(os.environ.get("ALTURA", 1920))
cena.render.resolution_percentage = 100
formato = opcao("formato", "png").lower()
EXT = "jpg" if formato in ("jpg", "jpeg") else "png"
cena.render.image_settings.file_format = "JPEG" if EXT == "jpg" else "PNG"
cena.render.image_settings.color_mode = "RGB"
if EXT == "jpg":
    cena.render.image_settings.quality = int(opcao("qualidade", 95))
try:
    cena.view_settings.view_transform = "AgX"
    cena.view_settings.look = "AgX - Punchy"
except Exception:
    pass

if CONTORNO:
    cena.render.use_freestyle = True
    cena.render.line_thickness_mode = "ABSOLUTE"
    cena.render.line_thickness = float(ESTILO.get("contorno_espessura", 2.2))
    vl = bpy.context.view_layer
    vl.use_freestyle = True
    for ls in list(vl.freestyle_settings.linesets):
        vl.freestyle_settings.linesets.remove(ls)
    ls = vl.freestyle_settings.linesets.new("contorno")
    ls.select_silhouette = True
    ls.select_border = True
    ls.select_crease = False
    ls.select_by_visibility = True
    ls.linestyle.color = (0.04, 0.03, 0.03)
    ls.linestyle.thickness = 1.0

saida = os.path.abspath(opcao("saida", os.path.join(pasta, "quadros")))
os.makedirs(saida, exist_ok=True)
lista = opcao("quadros")
de = int(opcao("de", 1))
ate = int(opcao("ate", total))
quadros = [int(x) for x in lista.split(",")] if lista else list(range(de, ate + 1))
# os arquivos seguem o vídeo: q0001.png é o primeiro quadro (quadro 0 do Blender)
for f in quadros:
    cena.frame_set(f - 1)
    cena.render.filepath = os.path.join(saida, f"q{f:04d}.{EXT}")
    bpy.ops.render.render(write_still=True)
    print(f"quadro {f}/{total}", flush=True)
print("Pronto:", saida)
