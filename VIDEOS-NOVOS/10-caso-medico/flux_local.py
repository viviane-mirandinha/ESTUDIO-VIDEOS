# Imagens via Flux local (ComfyUI 127.0.0.1:8188), sem texto
import json, urllib.request, urllib.parse, time, os, sys
H="http://127.0.0.1:8188"; D=os.path.join(os.path.dirname(os.path.abspath(__file__)),"img")
S=" Medical illustration, dark near-black background, no text, no letters, no labels, no watermark, no blood, no surgery."
P={"rm_cardiaca":"Grayscale cardiac MRI scan of a human heart, short-axis view slice, medical imaging monitor style, the heart muscle ring shows subtle diffuse bright patchy areas, clean scan, centered.",
   "rm_cardiaca2":"Grayscale cardiac magnetic resonance image of the heart, four-chamber view, realistic radiology scan, soft gray tones, centered."}
def post(d): r=urllib.request.Request(H+"/prompt",data=json.dumps({"prompt":d}).encode(),headers={"Content-Type":"application/json"}); return json.loads(urllib.request.urlopen(r,timeout=60).read())["prompt_id"]
for k,txt in P.items():
    out=os.path.join(D,k+".jpg")
    if os.path.exists(out): continue
    g={"1":{"class_type":"UNETLoader","inputs":{"unet_name":"flux1-dev-kontext_fp8_scaled.safetensors","weight_dtype":"default"}},
     "2":{"class_type":"DualCLIPLoader","inputs":{"clip_name1":"clip_l.safetensors","clip_name2":"t5xxl_fp8_e4m3fn_scaled.safetensors","type":"flux"}},
     "3":{"class_type":"VAELoader","inputs":{"vae_name":"ae.safetensors"}},
     "7":{"class_type":"CLIPTextEncode","inputs":{"text":txt+S,"clip":["2",0]}},
     "9":{"class_type":"FluxGuidance","inputs":{"conditioning":["7",0],"guidance":3.5}},
     "10":{"class_type":"ConditioningZeroOut","inputs":{"conditioning":["7",0]}},
     "11":{"class_type":"EmptySD3LatentImage","inputs":{"width":1344,"height":768,"batch_size":1}},
     "12":{"class_type":"KSampler","inputs":{"model":["1",0],"positive":["9",0],"negative":["10",0],"latent_image":["11",0],"seed":1010,"steps":20,"cfg":1.0,"sampler_name":"euler","scheduler":"simple","denoise":1.0}},
     "13":{"class_type":"VAEDecode","inputs":{"samples":["12",0],"vae":["3",0]}},
     "14":{"class_type":"SaveImage","inputs":{"images":["13",0],"filename_prefix":"d10_"+k}}}
    pid=post(g); t0=time.time()
    while time.time()-t0<400:
        time.sleep(3)
        h=json.loads(urllib.request.urlopen(H+"/history/"+pid,timeout=30).read())
        if pid in h and h[pid].get("outputs"):
            im=h[pid]["outputs"]["14"]["images"][0]
            b=urllib.request.urlopen(H+"/view?"+urllib.parse.urlencode({"filename":im["filename"],"subfolder":im["subfolder"],"type":im["type"]}),timeout=60).read()
            tmp=out+".png"; open(tmp,"wb").write(b)
            from PIL import Image; Image.open(tmp).convert("RGB").resize((1280,731)).crop((0,5,1280,725)).save(out,quality=92); os.remove(tmp)
            print("ok",k,int(time.time()-t0),"s"); break
    else: print("timeout",k)
