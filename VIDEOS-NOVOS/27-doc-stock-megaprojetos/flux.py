# Produtos genéricos (sem marca) via Flux Kontext dev local, modo texto->imagem
import json, urllib.request, time, os, sys
from PIL import Image
H="http://127.0.0.1:8188"; D=os.path.join(os.path.dirname(os.path.abspath(__file__)),"img")
S=" Photorealistic aerospace press render, clean bright lighting, high detail, no text, no letters, no logos, no airline livery, no brand markings, no flags."
P={
"f_cabine_telas":"Interior of a futuristic wide passenger airliner cabin with no windows at all, the curved side walls are covered by large seamless display screens showing a live view of blue sky and white clouds outside, rows of modern light grey passenger seats, soft daylight glow from the screens.",
"f_assentos":"Long rows of empty modern economy passenger seats inside a very wide airliner cabin, symmetrical perspective down the aisle, light grey fabric seats, soft cabin lighting.",
"f_estrutura":"A huge carbon composite wing and body section of a blended wing aircraft under assembly inside a bright clean white aerospace hangar, robotic arms and scaffolding, small workers in white overalls far away.",
"f_asa_voadora":"A plain white generic blended wing body passenger airliner concept, flying wing shape with two engines on top at the rear, flying above a sea of clouds at golden sunset, side three quarter view.",
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
     "11":{"class_type":"EmptySD3LatentImage","inputs":{"width":1344,"height":768,"batch_size":1}},
     "12":{"class_type":"KSampler","inputs":{"model":["1",0],"positive":["9",0],"negative":["10",0],"latent_image":["11",0],"seed":(2727 if not sys.argv[1:] else 777),"steps":20,"cfg":1.0,"sampler_name":"euler","scheduler":"simple","denoise":1.0}},
     "13":{"class_type":"VAEDecode","inputs":{"samples":["12",0],"vae":["3",0]}},
     "14":{"class_type":"SaveImage","inputs":{"images":["13",0],"filename_prefix":"d27_"+k}}}
    pid=post(g); t0=time.time()
    while True:
        time.sleep(2)
        h=json.loads(urllib.request.urlopen(H+"/history/"+pid,timeout=30).read())
        if pid in h:
            if h[pid].get("status",{}).get("status_str")=="error": print("erro",k,flush=True); break
            o=h[pid]["outputs"]["14"]["images"][0]
            data=urllib.request.urlopen(H+"/view?filename=%s&subfolder=%s&type=output"%(o["filename"],o["subfolder"]),timeout=60).read()
            open(out+".png","wb").write(data); Image.open(out+".png").convert("RGB").resize((1280,731)).save(out,quality=90); os.remove(out+".png")
            print("ok",k,round(time.time()-t0),"s",flush=True); break
        if time.time()-t0>900: print("timeout",k,flush=True); break
print("FIM")
