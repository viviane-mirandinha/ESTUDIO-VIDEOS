import urllib.request, urllib.parse, time, os, sys, json
from PIL import Image
D=os.path.join(os.path.dirname(os.path.abspath(__file__)),"img")
# DESCRICAO FISICA FIXA (igual em todo prompt do avatar) + SEED FIXA
AV=("Marta, a fictional 45-year-old Brazilian woman, warm olive skin, oval face, brown eyes, "
    "shoulder-length wavy dark brown hair with one distinct grey streak at the left temple, "
    "thin round gold-rimmed glasses, small mole above the right corner of her lip, no makeup, "
    "wearing a mustard-yellow knit cardigan over a plain white t-shirt and a thin gold chain")
SEED_AV=1717
FOTO=", candid realistic documentary photo, natural light, shot on iPhone, real skin texture, sharp focus, no text, no watermark"
DET=", macro product photography, realistic, shallow depth of field, soft natural light, no text, no watermark, no people faces"
P=[
 ("avatar-mestre", AV+", medium close-up portrait looking at the camera with a calm slight smile, plain bright living room background", SEED_AV, FOTO),
 ("av_feira", AV+", standing at an outdoor flea market stall, holding up a small gold ring between her fingers and looking at it with curiosity, tables of old trinkets behind her, daytime", SEED_AV, FOTO),
 ("av_lupa", AV+", sitting at her wooden kitchen table at home in the evening, holding a jeweler's loupe to her eye and examining a small gold ring very closely, warm lamp light", SEED_AV, FOTO),
 ("av_leilao", AV+", sitting across a table from a grey-haired male appraiser in a navy suit who is examining a small gold ring with a loupe, elegant auction house office with dark wood panels, she watches him anxiously", SEED_AV, FOTO),
 ("av_choque", AV+", in an elegant auction house office with dark wood panels, both hands over her mouth in shock and disbelief, eyes wide, looking at the camera", SEED_AV, FOTO),
 ("av_cta", AV+", sitting on a sofa in her bright living room, smiling warmly at the camera and holding up a small gold ring with a diamond between her fingers", SEED_AV, FOTO),
 ("d_banca", "flea market table covered with cheap costume jewelry, tangled necklaces and brass rings in a cardboard tray, a vendor's hand holding out a thin gold ring", 301, DET),
 ("d_puncao", "extreme macro of the inside of a thin worn antique gold ring band, a tiny faint stamped hallmark almost erased by time, scratches, dark background", 302, DET),
 ("d_diamante", "antique thin gold ring with a single old transitional cut diamond in a delicate platinum setting, resting on dark blue velvet, sparkle", 303, DET),
 ("d_certificado", "an old yellowed paper jewelry certificate with an official red wax seal lying on a wooden table next to a small diamond ring, blurry unreadable handwriting", 304, DET),
 ("d_garras", "extreme macro of the delicate claw prongs holding an old cut diamond on an antique ring, jeweler's tweezers holding the ring, dark velvet background", 305, DET),
 ("d_leilao", "elegant New York auction room with rows of empty chairs, a wooden podium with a gavel, a glass display case with a small diamond ring under a spotlight", 306, ", realistic photo, cinematic, no text, no watermark"),
 ("d_relogio", "vintage gold wristwatch with a cream dial and worn brown leather strap lying on dark blue velvet, dramatic light", 307, DET),
]
only=sys.argv[1:]
for k,p,seed,suf in P:
    if only and k not in only: continue
    out=os.path.join(D,k+".jpg")
    if os.path.exists(out): continue
    url="https://image.pollinations.ai/prompt/"+urllib.parse.quote(p+suf)+"?width=1280&height=800&model=flux&nologo=true&seed=%d"%seed
    for t in range(5):
        try:
            r=urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"estilos-novos-17/1.0"}),timeout=180).read()
            tmp=out+".tmp"; open(tmp,"wb").write(r)
            im=Image.open(tmp).convert("RGB"); w,h=im.size
            im=im.resize((1280,int(1280*h/w))) if w!=1280 else im
            im.crop((0,0,1280,720)).save(out,quality=92); os.remove(tmp)
            print("ok",k,flush=True); break
        except Exception as e:
            print("erro",k,str(e)[:70],flush=True); time.sleep(60 if "402" in str(e) else 20)
    time.sleep(18)
print("FIM")
