import urllib.request, urllib.parse, time, os, sys
from PIL import Image
D=os.path.join(os.path.dirname(os.path.abspath(__file__)),"img")
S=", 3D render, Blender, cinematic, volumetric fog, dark teal and black, film grain, no text"
P={
"f_cidade2011":"aerial view of a dark American city at night, tiny warm lights, low clouds",
"f_laptop":"a faceless white mannequin wearing a dark hoodie sitting alone at a desk in a dark bedroom typing on a laptop, laptop screen glow lighting the mannequin",
"f_contrabando":"dark table top with small plastic bags of pills, a black pistol and a gold bitcoin coin under a single spotlight, black background",
"f_liberdade":"back view of a faceless mannequin wearing a dark hoodie and jeans standing with arms spread wide in front of a huge bright glowing doorway of white light, dark empty room, god rays",
"f_agente":"a faceless mannequin wearing a dark navy federal agent jacket sitting at a computer in a dark office at night, monitor glow",
"f_biblioteca":"public library interior at night, tall bookshelves, a faceless white mannequin at a wooden table with an open glowing laptop, two faceless mannequin agents in dark suits approaching from behind",
"f_prisao":"a faceless white mannequin in an orange jumpsuit sitting alone in a concrete prison cell behind steel bars, cold blue light",
"f_saida":"a faceless white mannequin walking out of an open steel prison gate toward bright sunlight, dark concrete walls",
"f_guerra":"a giant glowing orange padlock floating in a dark server room corridor, faceless mannequins in black tactical gear standing around it",
"f_final":"dark city seen from above at night with glowing orange network lines connecting the buildings, like a circuit map",
"f_sf2013":"aerial view of San Francisco hills and houses at dusk, dark moody, fog rolling",
}
for i,(k,p) in enumerate(P.items()):
    out=os.path.join(D,k+".jpg")
    if os.path.exists(out): continue
    url="https://image.pollinations.ai/prompt/"+urllib.parse.quote(p+S)+"?width=1280&height=800&model=flux&nologo=true&seed=%d"%(80+i)
    for t in range(3):
        try:
            r=urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"estilos-novos-08/1.0"}),timeout=180).read()
            tmp=out+".tmp"; open(tmp,"wb").write(r)
            im=Image.open(tmp).convert("RGB"); w,h=im.size
            im=im.crop((0,0,w,int(h*0.9))).resize((1280,720)); im.save(out,quality=90); os.remove(tmp)
            print("ok",k,flush=True); break
        except Exception as e:
            print("erro",k,str(e)[:80],flush=True); time.sleep(20)
    time.sleep(18)
print("FIM")
