# Flux Kontext dev LOCAL (ComfyUI E:\AI). t2i (mestre) ou edicao com imagem de referencia (poses / musculo pintado)
import json, urllib.request, time, os, sys, uuid
from PIL import Image, ImageOps
H="http://127.0.0.1:8188"; D=os.path.join(os.path.dirname(os.path.abspath(__file__)),"img")
STY=(" Black and white manga ink lineart illustration, fine clean ink lines, light grey screentone shading, "
     "the only color is the purple pants, pure solid black background, full character centered with empty black space around, no text, no watermark.")
import numpy as np
from PIL import ImageFilter
def bw(im):
    # traço P&B de mangá: só o azul da regata fica colorido (o resto vira cinza)
    h=np.asarray(im.convert("HSV")).astype(float); hue=h[...,0]*360/255; s=h[...,1]/255
    k=((hue>195)&(hue<265)&(s>0.35)).astype(np.uint8)*255
    k=np.asarray(Image.fromarray(k).filter(ImageFilter.MedianFilter(5)).filter(ImageFilter.GaussianBlur(1.2))).astype(float)[...,None]/255
    g=np.asarray(im.convert("L").convert("RGB")).astype(float); c=np.asarray(im).astype(float)
    return Image.fromarray((c*k+g*(1-k)).astype(np.uint8))
def post(path,data,ct="application/json"):
    r=urllib.request.Request(H+path,data=data,headers={"Content-Type":ct}); return json.loads(urllib.request.urlopen(r,timeout=60).read())
def upload(fp):
    b="----k"+uuid.uuid4().hex; body=(f"--{b}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"a20_{os.path.basename(fp)}\"\r\nContent-Type: image/jpeg\r\n\r\n").encode()+open(fp,"rb").read()+f"\r\n--{b}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n--{b}--\r\n".encode()
    return post("/upload/image",body,"multipart/form-data; boundary="+b)["name"]
def gen(key,txt,ref=None,seed=2020,guid=None):
    out=os.path.join(D,key+".jpg")
    if os.path.exists(out): return
    g={"1":{"class_type":"UNETLoader","inputs":{"unet_name":"flux1-dev-kontext_fp8_scaled.safetensors","weight_dtype":"default"}},
     "2":{"class_type":"DualCLIPLoader","inputs":{"clip_name1":"clip_l.safetensors","clip_name2":"t5xxl_fp8_e4m3fn_scaled.safetensors","type":"flux"}},
     "3":{"class_type":"VAELoader","inputs":{"vae_name":"ae.safetensors"}},
     "7":{"class_type":"CLIPTextEncode","inputs":{"text":txt,"clip":["2",0]}},
     "10":{"class_type":"ConditioningZeroOut","inputs":{"conditioning":["7",0]}},
     "11":{"class_type":"EmptySD3LatentImage","inputs":{"width":1344,"height":768,"batch_size":1}},
     "13":{"class_type":"VAEDecode","inputs":{"samples":["12",0],"vae":["3",0]}},
     "14":{"class_type":"SaveImage","inputs":{"images":["13",0],"filename_prefix":"a20_"+key}}}
    if ref:
        n=upload(os.path.join(D,ref+".jpg"))
        g.update({"4":{"class_type":"LoadImage","inputs":{"image":n}},
          "5":{"class_type":"FluxKontextImageScale","inputs":{"image":["4",0]}},
          "6":{"class_type":"VAEEncode","inputs":{"pixels":["5",0],"vae":["3",0]}},
          "8":{"class_type":"ReferenceLatent","inputs":{"conditioning":["7",0],"latent":["6",0]}},
          "9":{"class_type":"FluxGuidance","inputs":{"conditioning":["8",0],"guidance":guid or 2.5}}})
    else:
        g["9"]={"class_type":"FluxGuidance","inputs":{"conditioning":["7",0],"guidance":guid or 3.5}}
    g["12"]={"class_type":"KSampler","inputs":{"model":["1",0],"positive":["9",0],"negative":["10",0],"latent_image":["11",0],"seed":seed,"steps":22,"cfg":1.0,"sampler_name":"euler","scheduler":"simple","denoise":1.0}}
    pid=post("/prompt",json.dumps({"prompt":g}).encode())["prompt_id"]; t0=time.time()
    while True:
        time.sleep(3)
        h=json.loads(urllib.request.urlopen(H+"/history/"+pid,timeout=30).read())
        if pid in h:
            st=h[pid].get("status",{})
            if st.get("status_str")=="error": print("erro",key,str(st)[:300],flush=True); return
            o=h[pid]["outputs"]["14"]["images"][0]
            data=urllib.request.urlopen(H+"/view?filename=%s&subfolder=%s&type=output"%(o["filename"],o["subfolder"]),timeout=60).read()
            tmp=out+".png"; open(tmp,"wb").write(data)
            im=Image.open(tmp).convert("RGB").resize((1280,int(1280*768/1344)))
            y=(im.size[1]-720)//2; im=im.crop((0,y,1280,y+720))
            # fundo preto puro: esmaga quase-preto
            im=im.point(lambda v: 0 if v<26 else int((v-26)*255/229))
            if not key.endswith("_cor") and not key.startswith("mestre_"): im=bw(im)
            im.save(out,quality=93); os.remove(tmp)
            print("ok",key,round(time.time()-t0),"s",flush=True); return
        if time.time()-t0>900: print("timeout",key,flush=True); return
if __name__=="__main__":
    M=("A handsome young man with an athletic muscular build, short messy spiky silver-white hair falling over his eyes, sharp jaw, shirtless, "
       "wearing loose purple jogger training pants, standing upright in a relaxed front view, arms hanging at his sides, calm serious expression.")
    for s in (11,22,33,44): gen("mestre_%d"%s,M+STY,seed=s)
