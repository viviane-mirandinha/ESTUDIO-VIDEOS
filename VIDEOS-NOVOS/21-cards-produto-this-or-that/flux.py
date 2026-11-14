# Produtos genéricos (sem marca) via Flux Kontext dev local, modo texto->imagem
import json, urllib.request, time, os, sys
from PIL import Image
H="http://127.0.0.1:8188"; D=os.path.join(os.path.dirname(os.path.abspath(__file__)),"img")
S=" Clean e-commerce product photograph, centered, plain seamless off-white background, soft studio light, soft shadow, generic unbranded product, no text, no logos, no letters, no people."
P={
"p01a":"A simple modern wooden study table with four straight metal legs and a flat top, no drawers.",
"p01b":"A classic wooden writing desk with a row of drawers on one side and a small hutch shelf on top.",
"p02a":"A plain racing style gamer chair, black and red bucket seat with side wings, completely plain fabric with no embroidery, no text, no emblem.",
"p02b":"An ergonomic mesh office chair, gray mesh back with lumbar support, adjustable armrests and headrest.",
"p03a":"A single flat computer monitor on a stand, dark screen with a soft blue gradient wallpaper.",
"p03b":"Two identical flat computer monitors side by side on a dual monitor arm, soft blue gradient wallpaper.",
"p04a":"An open silver laptop seen from the front, screen showing a soft blue gradient wallpaper.",
"p04b":"A closed silver laptop standing vertically in a small vertical laptop stand next to a computer monitor showing an abstract orange and pink gradient wallpaper with no icons and no logo, clamshell mode setup.",
"p05a":"A mechanical keyboard with chunky keycaps in beige and gray, visible key switches under one removed keycap, no letters on keys.",
"p05b":"A thin flat black membrane keyboard with low profile flat keys, no letters on keys.",
"p06a":"Side view of a tall black vertical ergonomic mouse shaped like a handshake grip, the buttons on the vertical side, tilted 60 degrees, clearly different from a normal mouse.",
"p06b":"A classic black computer mouse, traditional flat shape, two buttons and a scroll wheel.",
"p07a":"A modern desk lamp switched on, emitting very cold bluish white light, cool blue tone.",
"p07b":"A modern desk lamp switched on, emitting warm golden yellow light, cozy warm amber tone.",
"p08a":"Large over-ear headphones with big cushioned ear cups, matte black.",
"p08b":"A pair of small wireless in-ear earbuds next to their open charging case, white.",
"p09a":"An open paper notebook with handwritten scribbled lines and a ballpoint pen lying on it, the writing is illegible.",
"p09b":"A black tablet with a stylus pen, screen showing a blank note with a few hand drawn lines.",
"p10a":"A plain empty light gray painted wall section behind a small corner of a desk, minimalist, nothing on the wall.",
"p10b":"A cork board hanging on a wall covered with colorful sticky notes, pinned paper cards and push pins, the notes are blank.",
"p11a":"A white ceramic mug of black coffee with steam rising, on a saucer.",
"p11b":"A tall clear glass of fresh water with a few drops on the glass.",
"p12a":"A pair of soft orange foam earplugs, close up.",
"p12b":"A small round white noise sound machine, white plastic with a speaker grille on top.",
"p13a":"A red tomato shaped kitchen timer.",
"p13b":"A large wooden hourglass with sand flowing.",
"p14a":"A black smartphone lying face up on a wooden desk next to a notebook, screen dark.",
"p14b":"A white desk with its top drawer pulled half open, a black smartphone lying inside the open drawer among pens, seen from above at an angle.",
"p15a":"A thick paper daily planner with a fabric cover and an elastic band, closed, with a pen beside it.",
"p15b":"A smartphone standing upright showing a colorful calendar app grid with colored blocks, no readable text.",
"p16a":"Top view of a wide desk with a very large long gray felt desk mat under both a keyboard and a mouse, the mat covers almost the whole desk.",
"p16b":"A small square black mouse pad with a mouse on it, top view.",
"p17a":"A silver aluminum laptop riser stand with two angled metal legs standing on a white desk, an open laptop resting on top of the stand, the whole stand clearly visible under the laptop, screen showing an abstract orange and pink gradient wallpaper with no icons and no logo, three quarter view.",
"p17b":"A laptop propped up on a stack of old hardcover books, screen showing an abstract orange and pink gradient wallpaper with no icons and no logo, three quarter view.",
"p18a":"A messy tangled pile of black charging cables and wires.",
"p18b":"Under a desk edge, a tidy white cable management tray holding neatly bundled black cables wrapped with velcro straps, organized.",
"p19a":"An artificial plastic plant in a white pot, glossy fake leaves, obviously plastic.",
"p19b":"A real living green potted plant, a lush pothos in a terracotta pot, natural leaves.",
}
def post(d): r=urllib.request.Request(H+"/prompt",data=json.dumps({"prompt":d}).encode(),headers={"Content-Type":"application/json"}); return json.loads(urllib.request.urlopen(r,timeout=60).read())["prompt_id"]
for k,txt in P.items():
    if sys.argv[1:] and k not in sys.argv[1:]: continue
    out=os.path.join(D,k+".jpg")
    if os.path.exists(out) and not sys.argv[1:]: continue
    g={"1":{"class_type":"UNETLoader","inputs":{"unet_name":"flux1-dev-kontext_fp8_scaled.safetensors","weight_dtype":"default"}},
     "2":{"class_type":"DualCLIPLoader","inputs":{"clip_name1":"clip_l.safetensors","clip_name2":"t5xxl_fp8_e4m3fn_scaled.safetensors","type":"flux"}},
     "3":{"class_type":"VAELoader","inputs":{"vae_name":"ae.safetensors"}},
     "7":{"class_type":"CLIPTextEncode","inputs":{"text":txt+S,"clip":["2",0]}},
     "9":{"class_type":"FluxGuidance","inputs":{"conditioning":["7",0],"guidance":3.5}},
     "10":{"class_type":"ConditioningZeroOut","inputs":{"conditioning":["7",0]}},
     "11":{"class_type":"EmptySD3LatentImage","inputs":{"width":896,"height":896,"batch_size":1}},
     "12":{"class_type":"KSampler","inputs":{"model":["1",0],"positive":["9",0],"negative":["10",0],"latent_image":["11",0],"seed":(2121 if not sys.argv[1:] else 777),"steps":20,"cfg":1.0,"sampler_name":"euler","scheduler":"simple","denoise":1.0}},
     "13":{"class_type":"VAEDecode","inputs":{"samples":["12",0],"vae":["3",0]}},
     "14":{"class_type":"SaveImage","inputs":{"images":["13",0],"filename_prefix":"d21_"+k}}}
    pid=post(g); t0=time.time()
    while True:
        time.sleep(2)
        h=json.loads(urllib.request.urlopen(H+"/history/"+pid,timeout=30).read())
        if pid in h:
            if h[pid].get("status",{}).get("status_str")=="error": print("erro",k,flush=True); break
            o=h[pid]["outputs"]["14"]["images"][0]
            data=urllib.request.urlopen(H+"/view?filename=%s&subfolder=%s&type=output"%(o["filename"],o["subfolder"]),timeout=60).read()
            open(out+".png","wb").write(data); Image.open(out+".png").convert("RGB").resize((640,640)).save(out,quality=90); os.remove(out+".png")
            print("ok",k,round(time.time()-t0),"s",flush=True); break
        if time.time()-t0>900: print("timeout",k,flush=True); break
print("FIM")
