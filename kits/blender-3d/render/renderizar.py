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


# ------------------------------------------------------------- materiais com acabamento de filme

for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    pbr = next((n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if not pbr:
        continue
    # vinil e plástico: um pouco de verniz e brilho suave nas bordas
    if "Coat Weight" in pbr.inputs and pbr.inputs["Coat Weight"].default_value < 0.05 and pbr.inputs["Roughness"].default_value < 0.5:
        pbr.inputs["Coat Weight"].default_value = 0.3
    if "Sheen Weight" in pbr.inputs and pbr.inputs["Roughness"].default_value > 0.7:
        pbr.inputs["Sheen Weight"].default_value = 0.15
    # vidro: transparência de verdade
    alpha = pbr.inputs["Alpha"].default_value
    if alpha < 0.6:
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
    fundo.inputs[1].default_value = 0.55 * q["luz"]
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


# principal quente e macia, preenchimento frio, contraluz para separar do fundo
principal = luz("principal", "SUN", 3.2, "#fff1dc", [6, 10, 7], [0, 0, 0], 8)
luz("preenchimento", "AREA", 900, "#d6e6ff", [-8, 5, 9], [0, 1.5, 0], 9)
luz("contraluz", "AREA", 1200, "#ffe2c0", [2, 7, -7], [0, 1.5, 0], 6)
# a força da luz acompanha a "luz" de cada quadro (noite, dia)
for i, q in enumerate(dados["quadros"]):
    principal.energy = 3.2 * q["luz"]
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
