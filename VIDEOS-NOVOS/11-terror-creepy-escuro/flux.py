import urllib.request, urllib.parse, time, os
from PIL import Image
D=os.path.join(os.path.dirname(os.path.abspath(__file__)),"img")
S=", photorealistic horror film still, night, cold dark blue moonlight, deep shadows, mist, 35mm film grain, no text, no watermark"
P={
"f_estrada":"a lonely dirt road at night ending at an old isolated wooden farmhouse far away with one dim window light, dead trees on both sides, no people",
#"f_casa":"an old abandoned-looking wooden country house at dusk at the end of a dirt road, overgrown yard, dead trees, no people",
"f_janela":"inside an old wooden house at night, a torn white curtain blowing from a cracked window frame, moonlight through gaps in the wooden walls, empty room, no people",
"f_corredor":"long narrow dark hallway of an old wooden house at night, peeling wallpaper, doors on both sides, faint moonlight at the end, empty, no people",
"f_lanterna":"view from a bedroom doorway at night, a flashlight beam cutting through the darkness of an empty old hallway, dust floating in the beam, no people",
"f_pegadas":"close up of dusty old wooden floorboards at night lit by a flashlight, a trail of bare human footprints in the thick dust leading to the edge of an old bed, no people",
"f_cadeira":"a wooden kitchen chair wedged under the doorknob of an old closed basement door to block it, dim kitchen at night, no people",
#"f_porao":"old wooden basement door at the bottom of narrow stairs in pitch dark house, faint light under the door, no people",
"f_fresta":"close up of the gap under an old wooden door at night, sickly greenish smoke seeping through the crack into a dark room, no people",
"f_macaneta":"extreme close up of an old brass doorknob on a dark wooden door at night, turning slowly, a kitchen chair leaning against the door, no people",
"f_sombra":"a dark male silhouette standing in a black doorway at night wearing a plain grey t-shirt, face hidden in deep shadow, only a faint wide unnatural grin visible, creepy, horror",
"f_fuga":"empty dirt road at night seen from behind, an old farmhouse far away with its front door wide open and lit, dead trees, fog, no people",
}
for i,(k,p) in enumerate(P.items()):
    out=os.path.join(D,k+".jpg")
    if os.path.exists(out): continue
    url="https://image.pollinations.ai/prompt/"+urllib.parse.quote(p+S)+"?width=1280&height=800&model=flux&nologo=true&safe=true&seed=%d"%(110+i)
    for t in range(3):
        try:
            r=urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"estilos-novos-11/1.0"}),timeout=180).read()
            tmp=out+".tmp"; open(tmp,"wb").write(r)
            im=Image.open(tmp).convert("RGB"); w,h=im.size
            im=im.crop((0,0,w,int(h*0.9))).resize((1280,720)); im.save(out,quality=90); os.remove(tmp)
            print("ok",k,flush=True); break
        except Exception as e:
            print("erro",k,str(e)[:80],flush=True); time.sleep(20)
    time.sleep(18)
print("FIM")
