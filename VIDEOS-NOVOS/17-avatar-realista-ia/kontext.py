# Cenas da avatar derivadas da imagem-mestra via Flux Kontext dev LOCAL (ComfyUI E:\AI), seed fixa
import json, urllib.request, time, os, sys, uuid
from PIL import Image
H="http://127.0.0.1:8188"; D=os.path.join(os.path.dirname(os.path.abspath(__file__)),"img")
KEEP=(" Keep the exact same woman: same face, same brown eyes, same shoulder-length wavy dark brown hair with the grey streak at the left temple, "
      "same thin round gold-rimmed glasses, same mole above the lip, same mustard-yellow knit cardigan over a white t-shirt. "
      "Candid realistic documentary photo, natural light, real skin texture, wide 16:9 framing, no text.")
P={
 "av_feira":"Place this woman at an outdoor flea market stall in daytime, standing and holding up a small thin gold ring between her fingers, looking at the ring with curiosity, tables of old trinkets and costume jewelry behind her.",
 "av_lupa":"Place this woman sitting at a wooden kitchen table at home in the evening under warm lamp light, holding a jeweler's loupe to her eye and examining a small gold ring very closely.",
 "av_leilao":"Place this woman sitting at a table in an elegant auction house office with dark wood panels, across from a grey-haired male appraiser in a navy suit who examines a small diamond ring with a loupe; she watches him anxiously.",
 "av_choque":"Place this woman in an elegant auction house office with dark wood panels; she has both hands over her mouth in shock and disbelief, eyes wide, looking at the camera.",
 "av_cta":"Place this woman sitting on a sofa in a bright living room, smiling warmly at the camera and holding up a small gold ring with a diamond between her fingers.",
}
def post(path,data,ct="application/json"):
    r=urllib.request.Request(H+path,data=data,headers={"Content-Type":ct}); return json.loads(urllib.request.urlopen(r,timeout=60).read())
def upload(fp):
    b="----k"+uuid.uuid4().hex; body=(f"--{b}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"avatar17.jpg\"\r\nContent-Type: image/jpeg\r\n\r\n").encode()+open(fp,"rb").read()+f"\r\n--{b}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n--{b}--\r\n".encode()
    return post("/upload/image",body,"multipart/form-data; boundary="+b)["name"]
name=upload(os.path.join(D,"avatar-mestre.jpg"))
only=sys.argv[1:]
for k,txt in P.items():
    if only and k not in only: continue
    out=os.path.join(D,k+".jpg")
    if os.path.exists(out): continue
    g={
     "1":{"class_type":"UNETLoader","inputs":{"unet_name":"flux1-dev-kontext_fp8_scaled.safetensors","weight_dtype":"default"}},
     "2":{"class_type":"DualCLIPLoader","inputs":{"clip_name1":"clip_l.safetensors","clip_name2":"t5xxl_fp8_e4m3fn_scaled.safetensors","type":"flux"}},
     "3":{"class_type":"VAELoader","inputs":{"vae_name":"ae.safetensors"}},
     "4":{"class_type":"LoadImage","inputs":{"image":name}},
     "5":{"class_type":"FluxKontextImageScale","inputs":{"image":["4",0]}},
     "6":{"class_type":"VAEEncode","inputs":{"pixels":["5",0],"vae":["3",0]}},
     "7":{"class_type":"CLIPTextEncode","inputs":{"text":txt+KEEP,"clip":["2",0]}},
     "8":{"class_type":"ReferenceLatent","inputs":{"conditioning":["7",0],"latent":["6",0]}},
     "9":{"class_type":"FluxGuidance","inputs":{"conditioning":["8",0],"guidance":2.5}},
     "10":{"class_type":"ConditioningZeroOut","inputs":{"conditioning":["7",0]}},
     "11":{"class_type":"EmptySD3LatentImage","inputs":{"width":1344,"height":768,"batch_size":1}},
     "12":{"class_type":"KSampler","inputs":{"model":["1",0],"positive":["9",0],"negative":["10",0],"latent_image":["11",0],"seed":1717,"steps":22,"cfg":1.0,"sampler_name":"euler","scheduler":"simple","denoise":1.0}},
     "13":{"class_type":"VAEDecode","inputs":{"samples":["12",0],"vae":["3",0]}},
     "14":{"class_type":"SaveImage","inputs":{"images":["13",0],"filename_prefix":"av17_"+k}}}
    pid=post("/prompt",json.dumps({"prompt":g}).encode())["prompt_id"]
    t0=time.time()
    while True:
        time.sleep(3)
        h=json.loads(urllib.request.urlopen(H+"/history/"+pid,timeout=30).read())
        if pid in h:
            st=h[pid].get("status",{})
            if st.get("status_str")=="error": print("erro",k,str(st)[:200],flush=True); break
            o=h[pid]["outputs"]["14"]["images"][0]
            data=urllib.request.urlopen(H+"/view?filename=%s&subfolder=%s&type=output"%(o["filename"],o["subfolder"]),timeout=60).read()
            tmp=out+".png"; open(tmp,"wb").write(data)
            im=Image.open(tmp).convert("RGB").resize((1280,int(1280*768/1344)))
            y=(im.size[1]-720)//2; im.crop((0,y,1280,y+720)).save(out,quality=92); os.remove(tmp)
            print("ok",k,round(time.time()-t0),"s",flush=True); break
        if time.time()-t0>900: print("timeout",k,flush=True); break
print("FIM kontext")
