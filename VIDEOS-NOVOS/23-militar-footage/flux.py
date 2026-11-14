# Produtos genéricos (sem marca) via Flux Kontext dev local, modo texto->imagem
import json, urllib.request, time, os, sys
from PIL import Image
H="http://127.0.0.1:8188"; D=os.path.join(os.path.dirname(os.path.abspath(__file__)),"img")
S=" Realistic documentary photograph, overcast early morning light, muted desaturated colors, natural film grain, no text, no letters, no logos, no flags, no insignia, no people visible."
P={
"f_coluna":"Aerial drone photograph looking straight down at a very long column of many olive drab military supply trucks stopped bumper to bumper in a single line on a straight dirt road through flat empty farmland, light morning mist.",
"f_poco":"A camouflaged sniper observation hide dug into the ground, a low mound covered with dry grass, branches and camouflage netting with a narrow dark horizontal viewing slit, in a flat field a few meters beside a dirt road, low angle.",
"f_radio":"A green military field radio set with a coiled cable and a black telephone style handset lying on a wooden crate inside a dim canvas tent, small indicator lights, shallow depth of field.",
"f_caminhao":"Wide shot of a single olive drab military cargo truck stopped on a dirt road in open fields, a tall column of thick black smoke rising from its engine, other trucks far behind, dawn.",
"f_parada":"Ground level telephoto shot along a dirt road of a long line of stopped olive drab military trucks and jeeps stretching to the horizon, drifting grey smoke, flat fields and a distant tree line, dawn.",
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
     "12":{"class_type":"KSampler","inputs":{"model":["1",0],"positive":["9",0],"negative":["10",0],"latent_image":["11",0],"seed":(2323 if not sys.argv[1:] else 777),"steps":20,"cfg":1.0,"sampler_name":"euler","scheduler":"simple","denoise":1.0}},
     "13":{"class_type":"VAEDecode","inputs":{"samples":["12",0],"vae":["3",0]}},
     "14":{"class_type":"SaveImage","inputs":{"images":["13",0],"filename_prefix":"d23_"+k}}}
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
