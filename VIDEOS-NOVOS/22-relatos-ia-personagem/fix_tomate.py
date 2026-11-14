# Correção: plantas -> tomateiro real; flor amarela de tomateiro. Kontext edit sobre a própria cena (mesmo homem)
import sys,os
sys.argv=["gen.py","none"]
exec(open("gen.py",encoding="utf-8").read().split("os.makedirs(D,exist_ok=True)")[0])
TOM=("real tomato plants: each leaf is a broad compound leaf made of several wide, wrinkled, oval leaflets with irregular serrated lobed edges, "
     "matte medium green, on thick fuzzy hairy green stems, bushy and sprawling like a real garden tomato plant")
FLOR=("a cluster of small vivid bright yellow tomato flowers hanging down from the stem, each flower with five narrow pointed petals bent backward "
      "around a protruding yellow cone in the centre")
KM=" Keep the exact same man: same face, same age, same grey-black mustache and short white goatee, same brown leather hat, same olive-green shirt, same pose and composition."
E={
 "d05_umidade":"Replace the seedling with a young real tomato seedling: "+TOM+". Keep the same buried bucket with damp golden straw, the cracked earth and the composition.",
 "d07_flor":"Replace the plant with a young "+TOM.replace("real tomato plants: each","real tomato plant: each")+", with "+FLOR+" in the centre of the image, and one small green unripe tomato. Keep the same bucket rim with golden hay and the cracked earth background.",
 "c04_palha":"Replace the seedling the man is planting with a young real tomato seedling: "+TOM+"."+KM,
 "c06_vizinhos":"Replace all the small plants in the buckets with young real tomato seedlings: "+TOM+"."+KM+" Keep the two laughing villagers.",
 "c08_colheita":"Replace all the plants with "+TOM+", with ripe red and some green tomatoes hanging on them."+KM+" Keep the basket of red tomatoes.",
 "c09_segredo":"Replace all the plants with "+TOM+", with ripe red tomatoes hanging on them."+KM,
 "c10_madrugada":"Replace the plant with a young real tomato plant: "+TOM+"."+KM+" Keep the night lighting, the lantern and the watering can.",
 "c12_cta":"Replace all the plants in the field with "+TOM+", with ripe red tomatoes hanging on them."+KM+" Keep the big red tomato in his hand.",
 "c13_final":"Replace all the plants in the rows with "+TOM+", tall and lush with red tomatoes."+KM,
}
for k,t in E.items():
    if sys.argv[1:] and k not in sys.argv[1:]: pass
    src=os.path.join(D,k+".jpg"); bak=os.path.join(D,k+"_antes.jpg")
    if not os.path.exists(bak): os.replace(src,bak)
    if os.path.exists(src): continue
    import time as _t
    for tent in range(8):
        try: r=upload(bak); run(k,t+STY,2222,r,2.5); break
        except Exception as ex: print("retry",k,tent,str(ex)[:80],flush=True); _t.sleep(30)
print("FIM fix")
