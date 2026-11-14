# Imagens 26 via Flux Kontext dev LOCAL (ComfyUI 127.0.0.1:8188) — mesmo esquema do 22
# uso: python gen.py mestre          -> imagens-mestras mae/pai/filho (t2i)
#      python gen.py cenas [k ...]   -> cenas via Kontext (ref = mestra do personagem ou mestras costuradas)
import json, urllib.request, time, os, sys, uuid
from PIL import Image
H="http://127.0.0.1:8188"; D=os.path.join(os.path.dirname(os.path.abspath(__file__)),"img")
STY=(" Photorealistic still frame from a Brazilian family reality TV show, shot on a cinema camera, 35mm lens, natural light, "
     "realistic skin texture, shallow depth of field, wide 16:9 frame, no text, no letters, no logos, no watermark.")
P={"mae":"a cheerful plus-size Brazilian woman in her mid 40s, round face with rosy cheeks, curly shoulder-length dark brown hair with honey-blond highlights, brown eyes, small gold hoop earrings, wearing a bright pink floral print loose house dress",
   "pai":"a big heavyset Brazilian man in his early 50s with a round belly, bald on top with short grey hair on the sides, thick black-and-grey mustache, double chin, wearing a white ribbed tank top undershirt and a thin gold chain necklace",
   "filho":"a chubby Brazilian teenage boy about 14 years old, round face, messy straight black hair with a fringe, round black-rimmed glasses, wearing an oversized lime-green hoodie"}
KEEP={"mae":" Keep the exact same woman: same face, same age, same curly dark brown hair with honey-blond highlights, same gold hoop earrings, same pink floral dress, same body.",
      "pai":" Keep the exact same man: same face, same age, same bald head with grey sides, same thick mustache, same white tank top and gold chain, same body.",
      "filho":" Keep the exact same boy: same face, same age, same messy black hair with fringe, same round black glasses, same lime-green hoodie, same body.",
      "casal":" Keep the exact same woman (curly hair with blond highlights, pink floral dress) and the exact same man (bald, mustache, white tank top) with the same faces.",
      "trio":" Keep the exact same three people with the same faces, hair and clothes: the woman in the pink floral dress, the bald mustached man in the white tank top, the boy with glasses in the lime-green hoodie."}
NOITE="in a dark home kitchen at 3 AM lit only by the cold white light of an open refrigerator, "
CONF="sitting in front of a purple velvet curtain in a reality show confessional interview, soft studio light, "
SALA="on a beige sofa in a cozy living room at night lit by the blue glow of a TV, "
K={
 "s01_mae_lanche":("mae","Place this woman "+NOITE+"holding a plate with only crumbs and the last bite of a sandwich, caught red-handed, innocent guilty smile. Medium close-up."),
 "s02_pai_iogurte":("pai","Place this man "+NOITE+"holding a tiny yogurt cup and a spoon, cheeks full, chewing, innocent look. Medium close-up."),
 "s03_filho_viu":("filho","Place this boy standing in a dark hallway doorway at night, holding a phone flashlight, pointing accusingly toward the camera, wide-eyed. Medium shot."),
 "s04_mae_lasanha":("mae","Place this woman "+CONF+"holding up a completely EMPTY glass baking dish, the lasagna is all gone, only a few smears of red sauce on the bottom of the clean empty dish, shocked expression with wide eyes and open mouth. Medium shot."),
 "s05_pai_gelada":("pai","Place this man standing in front of an open refrigerator in a bright kitchen during the day, eating cold lasagna straight from a big glass baking dish with a fork, mouth full, unbothered. Medium shot."),
 "s06_filho_sorvete":("filho","Place this boy in a bright modern kitchen holding up a big empty two-liter tub of ice cream with both hands toward the camera, indignant expression, open freezer behind him. Medium close-up."),
 "s07_mae_tampa":("mae","Place this woman in a bright modern kitchen holding up only the round plastic lid of an ice cream tub in one hand, shrugging with a sheepish smile. Medium close-up."),
 "s08_pai_tampa":("pai","Place this man "+CONF+"scratching his bald head, confused, one eyebrow raised, looking slightly off camera. Medium close-up."),
 "s09_filho_cachorro":("filho","Place this boy crouching on a kitchen floor next to a small chubby short-legged brown dachshund dog, pointing up at the high kitchen counter, skeptical look at the camera. Medium wide shot."),
 "s10_mae_fantasma":("mae","Place this woman "+CONF+"raising both hands dramatically like telling a ghost story, eyes wide, theatrical spooky expression. Medium shot."),
 "s11_pai_drama":("pai","Place this man sitting on a beige sofa in a bright living room, rolling his eyes and waving one hand dismissively, bored expression. Medium shot."),
 "s12_casal_dormindo":("casal","Show this woman and this man asleep side by side "+SALA+"both with their mouths wide open snoring, heads tilted back, an empty chips bag on the woman's lap. Medium wide shot."),
 "s13_mae_pipoca":("mae","Place this woman sitting "+SALA+"reaching one open hand impatiently toward a big bowl of popcorn at the edge of the frame, annoyed, mouth open talking. Medium shot."),
 "s14_pai_pipoca":("pai","Place this man sitting "+SALA+"tilting a huge popcorn bowl toward the camera to show it is completely EMPTY inside, no popcorn left, only three unpopped kernels at the bottom, disappointed sad face. Medium close-up."),
 "s15_filho_pacotes":("filho","Place this boy in a living room at night proudly holding up three unopened microwave popcorn bags fanned out in his hands, smug grin. Medium close-up."),
 "s16_mae_mentira":("mae","Place this woman sitting "+SALA+"arms crossed, eyes narrowed with suspicion, one eyebrow raised, doubtful pout. Close-up."),
 "s17_filho_armario":("filho","Place this boy in a hallway opening a narrow broom closet; inside are brooms, a mop and a bucket with three microwave popcorn bags hidden behind them; he looks back at the camera with a sneaky smile. Medium wide shot."),
 "s18_pai_genio":("pai","Place this man sitting "+SALA+"giving a big thumbs up with a proud wide grin. Medium close-up."),
 "s19_familia_sofa":("trio","Show these three people sitting together on one beige sofa in a cozy living room at night, all eating from big bowls of popcorn and chips, laughing. Wide shot."),
 "s20_churrasco":("trio","Show these three people together around a smoking charcoal barbecue grill in a sunny Brazilian backyard with skewers of grilled meat, the man holding tongs, all excited and smiling. Wide shot."),
}
T={"s00_geladeira":"Dark home kitchen at 3 AM, a refrigerator door wide open glowing with cold white interior light, the fridge shelves completely empty except one lonely ketchup bottle, deep blue night shadows, nobody in the room, wide shot."}
def post(path,data,ct="application/json"):
    r=urllib.request.Request(H+path,data=data,headers={"Content-Type":ct}); return json.loads(urllib.request.urlopen(r,timeout=60).read())
def upload(fp,name):
    b="----k"+uuid.uuid4().hex; body=(f"--{b}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{name}\"\r\nContent-Type: image/jpeg\r\n\r\n").encode()+open(fp,"rb").read()+f"\r\n--{b}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n--{b}--\r\n".encode()
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
     "14":{"class_type":"SaveImage","inputs":{"images":["13",0],"filename_prefix":"v26_"+k}}}
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
def stitch(names,out):
    ims=[Image.open(os.path.join(D,"mestre_%s.jpg"%n)).convert("RGB") for n in names]
    ims=[im.resize((int(im.size[0]*560/im.size[1]),560)) for im in ims]
    W=sum(i.size[0] for i in ims); c=Image.new("RGB",(W,560)); x=0
    for im in ims: c.paste(im,(x,0)); x+=im.size[0]
    c.save(out,quality=92); return out
os.makedirs(D,exist_ok=True)
if sys.argv[1]=="mestre":
    for n,d in P.items():
        if len(sys.argv)>2 and n not in sys.argv[2:]: continue
        run("mestre_"+n,"Medium close-up portrait of "+d+", standing in a bright modern family kitchen with white cabinets during the day, looking at the camera with a friendly expression."+STY,2601)
else:
    only=sys.argv[2:]
    refs={n:upload(os.path.join(D,"mestre_%s.jpg"%n),"m26_%s.jpg"%n) for n in P}
    refs["casal"]=upload(stitch(["mae","pai"],os.path.join(D,"_ref_casal.jpg")),"m26_casal.jpg")
    refs["trio"]=upload(stitch(["mae","pai","filho"],os.path.join(D,"_ref_trio.jpg")),"m26_trio.jpg")
    for k,(who,t) in K.items():
        if (only and k not in only) or (not only and os.path.exists(os.path.join(D,k+".jpg"))): continue
        run(k,t+KEEP[who]+STY,int(os.environ.get("SEED","2626")),refs[who],2.5)
    for k,t in T.items():
        if (only and k not in only) or (not only and os.path.exists(os.path.join(D,k+".jpg"))): continue
        run(k,t+STY,2626)
print("FIM")
