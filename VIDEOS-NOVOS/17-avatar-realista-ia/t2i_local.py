# Detalhes SEM avatar via Flux Kontext dev local em modo texto->imagem (sem imagem de referência)
import json, urllib.request, time, os, sys
from PIL import Image
H="http://127.0.0.1:8188"; D=os.path.join(os.path.dirname(os.path.abspath(__file__)),"img")
S=" Realistic macro product photograph, shallow depth of field, soft natural light, no text, no logos, no people faces."
P={
 "d_banca":"A cluttered flea market table: a cardboard tray full of cheap tarnished costume jewelry, tangled brass chains, plastic beads and old rings; an old vendor's weathered hand holds out a thin worn gold ring toward the camera.",
 "d_puncao":"Extreme macro of the inside of a thin worn antique gold ring band showing a tiny faint stamped hallmark of three small letters almost erased by time, scratches, dark background.",
 "d_diamante":"A delicate antique thin gold ring with one small old transitional cut diamond, slightly warm white colour, set in fine platinum claws, resting on dark blue velvet, sparkle.",
 "d_certificado":"An old yellowed paper jewellery certificate document with an ornate printed border, an official red wax seal and a faded ink signature, lying on a wooden table next to a small antique diamond ring, the writing is blurry and unreadable.",
}
P.update({
 "d_garras":"Extreme macro of delicate antique platinum claw prongs holding a small old cut diamond on a thin gold ring, held by fine steel jeweler's tweezers, dark velvet background.",
 "d_leilao":"An elegant New York auction room with rows of empty chairs, a wooden podium with an auctioneer's gavel, and a glass display case with a small diamond ring under a spotlight.",
 "d_relogio":"A vintage gold wristwatch with a cream dial and a worn brown leather strap lying on dark blue velvet, dramatic soft light.",
})
def post(d): r=urllib.request.Request(H+"/prompt",data=json.dumps({"prompt":d}).encode(),headers={"Content-Type":"application/json"}); return json.loads(urllib.request.urlopen(r,timeout=60).read())["prompt_id"]
for k,txt in P.items():
    if sys.argv[1:] and k not in sys.argv[1:]: continue
    out=os.path.join(D,k+".jpg")
    g={"1":{"class_type":"UNETLoader","inputs":{"unet_name":"flux1-dev-kontext_fp8_scaled.safetensors","weight_dtype":"default"}},
     "2":{"class_type":"DualCLIPLoader","inputs":{"clip_name1":"clip_l.safetensors","clip_name2":"t5xxl_fp8_e4m3fn_scaled.safetensors","type":"flux"}},
     "3":{"class_type":"VAELoader","inputs":{"vae_name":"ae.safetensors"}},
     "7":{"class_type":"CLIPTextEncode","inputs":{"text":txt+S,"clip":["2",0]}},
     "9":{"class_type":"FluxGuidance","inputs":{"conditioning":["7",0],"guidance":3.5}},
     "10":{"class_type":"ConditioningZeroOut","inputs":{"conditioning":["7",0]}},
     "11":{"class_type":"EmptySD3LatentImage","inputs":{"width":1344,"height":768,"batch_size":1}},
     "12":{"class_type":"KSampler","inputs":{"model":["1",0],"positive":["9",0],"negative":["10",0],"latent_image":["11",0],"seed":1717,"steps":22,"cfg":1.0,"sampler_name":"euler","scheduler":"simple","denoise":1.0}},
     "13":{"class_type":"VAEDecode","inputs":{"samples":["12",0],"vae":["3",0]}},
     "14":{"class_type":"SaveImage","inputs":{"images":["13",0],"filename_prefix":"d17_"+k}}}
    pid=post(g); t0=time.time()
    while True:
        time.sleep(3)
        h=json.loads(urllib.request.urlopen(H+"/history/"+pid,timeout=30).read())
        if pid in h:
            if h[pid].get("status",{}).get("status_str")=="error": print("erro",k,flush=True); break
            o=h[pid]["outputs"]["14"]["images"][0]
            data=urllib.request.urlopen(H+"/view?filename=%s&subfolder=%s&type=output"%(o["filename"],o["subfolder"]),timeout=60).read()
            open(out+".png","wb").write(data); im=Image.open(out+".png").convert("RGB").resize((1280,731))
            im.crop((0,5,1280,725)).save(out,quality=92); os.remove(out+".png"); print("ok local",k,round(time.time()-t0),"s",flush=True); break
        if time.time()-t0>600: print("timeout",k,flush=True); break
print("FIM local")
