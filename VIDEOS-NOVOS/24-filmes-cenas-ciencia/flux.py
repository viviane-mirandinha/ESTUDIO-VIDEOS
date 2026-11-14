# 24 bastidores genéricos (sem marca) via Flux Kontext dev local, modo texto->imagem
import json, urllib.request, time, os, sys
from PIL import Image
H="http://127.0.0.1:8188"; D=os.path.join(os.path.dirname(os.path.abspath(__file__)),"img")
S=" Realistic 1980s behind-the-scenes film production photograph, 35mm color film, muted desaturated colors, natural film grain, no text, no letters, no logos, no flags, no insignia."
P={
"f_set":"Wide shot inside a long 1960s military barracks hall with two rows of metal bunk beds, a large 35mm movie camera on a tripod and film lighting stands in the foreground, cables on the floor, film crew rehearsal, nobody looking at camera.",
"f_recrutas":"Seen from behind, a row of young male military recruits with shaved heads in plain olive t-shirts standing at attention beside metal bunk beds in a 1960s barracks, soft window light, faces not visible.",
"f_roteiro":"Close-up of a thick film script with plain blank white pages and paper clips, dropped on a polished barracks floor next to a pair of shiny black military boots, shallow depth of field.",
"f_claquete":"Close-up of a blank black wooden film clapperboard with no writing lying on a canvas director chair on a film set, film lights blurred in the background, shallow depth of field.",
"f_elenco":"Seen from behind, a group of young actors with shaved heads in olive military fatigues sitting on metal bunk beds on a dimly lit barracks film set between takes, film light stands and a movie camera, faces not visible.",
"f_bastidores":"Dark barracks film set at night between takes, a film camera on a dolly track, a single work light, empty bunk beds in the background, moody shadows, nobody in frame.",
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
     "12":{"class_type":"KSampler","inputs":{"model":["1",0],"positive":["9",0],"negative":["10",0],"latent_image":["11",0],"seed":(2424 if not sys.argv[1:] else 777),"steps":20,"cfg":1.0,"sampler_name":"euler","scheduler":"simple","denoise":1.0}},
     "13":{"class_type":"VAEDecode","inputs":{"samples":["12",0],"vae":["3",0]}},
     "14":{"class_type":"SaveImage","inputs":{"images":["13",0],"filename_prefix":"d24_"+k}}}
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
