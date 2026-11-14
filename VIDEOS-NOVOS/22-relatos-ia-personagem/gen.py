# Imagens 22 via Flux Kontext dev LOCAL (ComfyUI 127.0.0.1:8188)
# uso: python gen.py mestre            -> 2 candidatas da imagem-mestra (t2i)
#      python gen.py cenas [k ...]     -> cenas do homem (Kontext a partir de img/mestre.jpg) + detalhes (t2i)
import json, urllib.request, time, os, sys, uuid
from PIL import Image
H="http://127.0.0.1:8188"; D=os.path.join(os.path.dirname(os.path.abspath(__file__)),"img")
STY=(" Detailed graphic novel illustration, clean ink outlines, semi-realistic cel shading, painterly textures, "
     "warm earthy palette of ochre, sepia and olive green, warm late-afternoon light, wide 16:9 cinematic frame, no text, no letters, no signs.")
MAN=("a lean 58-year-old Brazilian farmer from the dry sertao, sun-tanned weathered face with deep wrinkles and crow's feet, "
     "thick grey-black mustache, short grey stubble on the chin, dark brown tired kind eyes, "
     "wearing a wide-brimmed brown leather sertanejo hat, a faded olive-green button-up shirt with sleeves rolled to the elbows, "
     "beige work trousers and a brown leather belt")
KEEP=(" Keep the exact same man: same face, same age (58 years old), same grey-black mustache and short white goatee, same wrinkles, "
      "same brown leather hat, same faded olive-green shirt with rolled sleeves, same beige trousers."+STY)
MESTRE="Medium shot of "+MAN+", standing in a dry stony Brazilian backland, holding a small green tomato seedling in his hands near his chest, looking toward the viewer with calm determination, cracked dry ground and grey thorny bushes behind him."
# Kontext (homem)
K={
 "c01_chegada":"Place this man walking along a dusty dirt road into a poor dry backland village of small white clay houses with terracotta roofs, carrying two old plastic buckets with holes in one hand and a wooden crate of small tomato seedlings under the other arm; two villagers in the doorway watch him and laugh. Full body, wide shot.",
 "c03_enterra":"Place this man kneeling on hard stony cracked dry ground under a harsh sun, pushing an old plastic bucket down into a hole in the earth so only its rim shows, a row of other buried buckets beside him. Medium wide shot.",
 "c04_palha":"Place this man crouching beside a buried plastic bucket filled with dry golden straw and dark manure, gently planting a small green tomato seedling in the centre with his weathered hands. Medium shot, low angle.",
 "c06_vizinhos":"Place this man in the background tending a row of buried plastic buckets with small tomato plants; in the foreground, two other older villagers (a short bald man and a woman in a headscarf) lean on a wooden fence pointing at him and laughing mockingly.",
 "c08_colheita":"Place this man holding a woven basket full of shiny ripe red tomatoes, smiling slightly, standing among lush green tomato plants growing out of buried buckets, while all the brush and scrubland around the garden is dry and grey. Medium shot.",
 "c09_segredo":"Place this man sitting on an old wooden stool next to his small tomato garden at dusk, elbows on knees, looking thoughtfully into the distance, orange sunset sky behind. Medium shot.",
 "c10_madrugada":"Place this man in the dark blue light before dawn, holding an old oil lantern in one hand and a dented tin watering can in the other, carefully pouring a thin trickle of water drop by drop at the base of a tomato plant in a buried bucket; the village houses behind are dark and asleep. Medium shot.",
 "c11_feira":"Place this man standing behind a wooden stall at a busy small-town open-air market, wooden crates piled high with ripe red tomatoes in front of him, handing a paper bag of tomatoes to a smiling woman customer. Medium wide shot, daytime.",
 "c12_cta":"Place this man standing in his green tomato garden at golden hour, smiling warmly and looking straight at the viewer, holding one big ripe red tomato in his open hand. Medium close-up.",
 "c13_final":"Place this man seen from behind, small in the frame, standing at the edge of a lush green garden of many rows of buried buckets with tall tomato plants, surrounded by an endless dry grey desert backland, huge golden sunset sky. Very wide shot.",
}
# t2i (detalhes, sem o rosto)
T={
 "d02_solo":"A dented old tin enamel mug holding a little water placed on cracked stony dry earth under a scorching white sun, heat haze, dead grey thorny bushes in the background, close-up.",
 "d05_umidade":"Close-up from above of an old plastic bucket buried in dry cracked earth up to its rim, filled with damp golden straw glistening with water droplets, a young green tomato seedling growing from the centre.",
 "d07_flor":"Macro close-up of a single small yellow tomato flower blooming on a young tomato plant growing out of an old plastic bucket rim filled with straw, dry cracked earth around, soft warm light.",
}
def post(path,data,ct="application/json"):
    r=urllib.request.Request(H+path,data=data,headers={"Content-Type":ct}); return json.loads(urllib.request.urlopen(r,timeout=60).read())
def upload(fp):
    b="----k"+uuid.uuid4().hex; body=(f"--{b}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"ref22.jpg\"\r\nContent-Type: image/jpeg\r\n\r\n").encode()+open(fp,"rb").read()+f"\r\n--{b}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n--{b}--\r\n".encode()
    return post("/upload/image",body,"multipart/form-data; boundary="+b)["name"]
def run(k,text,seed,ref=None,guid=3.5):
    out=os.path.join(D,k+".jpg")
    g={"1":{"class_type":"UNETLoader","inputs":{"unet_name":"flux1-dev-kontext_fp8_scaled.safetensors","weight_dtype":"default"}},
     "2":{"class_type":"DualCLIPLoader","inputs":{"clip_name1":"clip_l.safetensors","clip_name2":"t5xxl_fp8_e4m3fn_scaled.safetensors","type":"flux"}},
     "3":{"class_type":"VAELoader","inputs":{"vae_name":"ae.safetensors"}},
     "7":{"class_type":"CLIPTextEncode","inputs":{"text":text,"clip":["2",0]}},
     "9":{"class_type":"FluxGuidance","inputs":{"conditioning":["7",0],"guidance":guid}},
     "10":{"class_type":"ConditioningZeroOut","inputs":{"conditioning":["7",0]}},
     "11":{"class_type":"EmptySD3LatentImage","inputs":{"width":1344,"height":768,"batch_size":1}},
     "12":{"class_type":"KSampler","inputs":{"model":["1",0],"positive":["9",0],"negative":["10",0],"latent_image":["11",0],"seed":seed,"steps":22,"cfg":1.0,"sampler_name":"euler","scheduler":"simple","denoise":1.0}},
     "13":{"class_type":"VAEDecode","inputs":{"samples":["12",0],"vae":["3",0]}},
     "14":{"class_type":"SaveImage","inputs":{"images":["13",0],"filename_prefix":"v22_"+k}}}
    if ref:
        g["4"]={"class_type":"LoadImage","inputs":{"image":ref}}
        g["5"]={"class_type":"FluxKontextImageScale","inputs":{"image":["4",0]}}
        g["6"]={"class_type":"VAEEncode","inputs":{"pixels":["5",0],"vae":["3",0]}}
        g["8"]={"class_type":"ReferenceLatent","inputs":{"conditioning":["7",0],"latent":["6",0]}}
        g["9"]["inputs"]["conditioning"]=["8",0]
    pid=post("/prompt",json.dumps({"prompt":g}).encode())["prompt_id"]; t0=time.time()
    while True:
        time.sleep(3)
        h=json.loads(urllib.request.urlopen(H+"/history/"+pid,timeout=30).read())
        if pid in h:
            st=h[pid].get("status",{})
            if st.get("status_str")=="error": print("erro",k,str(st)[:200],flush=True); return
            o=h[pid]["outputs"]["14"]["images"][0]
            data=urllib.request.urlopen(H+"/view?filename=%s&subfolder=%s&type=output"%(o["filename"],o["subfolder"]),timeout=60).read()
            tmp=out+".png"; open(tmp,"wb").write(data)
            im=Image.open(tmp).convert("RGB").resize((1280,int(1280*768/1344)))
            y=(im.size[1]-720)//2; im.crop((0,y,1280,y+720)).save(out,quality=92); os.remove(tmp)
            print("ok",k,round(time.time()-t0),"s",flush=True); return
        if time.time()-t0>900: print("timeout",k,flush=True); return
os.makedirs(D,exist_ok=True)
if sys.argv[1]=="mestre":
    for s in (2201,2202): run("mestre_%d"%s,MESTRE+STY,s)
else:
    only=sys.argv[2:]; ref=upload(os.path.join(D,"mestre.jpg"))
    for k,t in K.items():
        if (only and k not in only) or (not only and os.path.exists(os.path.join(D,k+".jpg"))): continue
        run(k,t+KEEP,2222,ref,2.5)
    for k,t in T.items():
        if (only and k not in only) or (not only and os.path.exists(os.path.join(D,k+".jpg"))): continue
        run(k,t+STY,2222)
print("FIM")
