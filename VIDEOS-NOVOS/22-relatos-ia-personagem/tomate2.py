# Correcao 2: plantas -> tomateiro real (folha composta, foliolos largos serrilhados enrugados), flor amarela. Kontext sobre a cena original.
# uso: python tomate2.py [k ...]   saida img/<k>_t<seed>.jpg ; originais ficam em img/<k>.jpg (d05 restaurado de _antes)
import sys,os,shutil
args=sys.argv[1:]
sys.argv=["gen.py","none"]
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"gen.py"),encoding="utf-8").read().split("os.makedirs(D,exist_ok=True)")[0])
if not os.path.exists(os.path.join(D,"d05_umidade.jpg")): shutil.copy(os.path.join(D,"d05_umidade_antes.jpg"),os.path.join(D,"d05_umidade.jpg"))
TOM=("Change every plant into a real tomato plant (Solanum lycopersicum): large compound tomato leaves, each leaf a central stalk with 5 to 9 broad oval leaflets, "
     "leaflets wide with deeply toothed lobed serrated edges and a wrinkled crinkled matte surface, slightly drooping, irregular and bushy; "
     "thick fuzzy hairy pale-green stems. The leaves must NOT be palmate, NOT thin narrow fingers radiating from one point, NOT cannabis or marijuana leaves. ")
FRU="Add round tomatoes hanging in small trusses on the vines, some ripe bright red, some unripe green. "
GRN="Add a few small round green unripe tomatoes on the plants. "
FLO=("In the centre, a hanging truss of four or five small vivid bright lemon-yellow tomato flowers on short hairy stalks, each flower with five narrow pointed yellow petals "
     "bent sharply backward like a little star and a protruding yellow cone in the middle; saturated bright yellow, NOT cream, NOT white. ")
KEEPX=(" Keep everything else exactly the same: same man (if present) with the same face, age, mustache, hat and clothes, same pose, same composition, "
       "same buckets, straw, earth and objects, same light and colours."+STY)
J={"c01_chegada":TOM,"c04_palha":TOM,"d05_umidade":TOM,"c06_vizinhos":TOM,"d07_flor":TOM+FLO+GRN,"c08_colheita":TOM+FRU,
   "c09_segredo":TOM+FRU,"c10_madrugada":TOM+GRN,"c11_feira":TOM,"c12_cta":TOM+FRU,"c13_final":TOM+FRU}
SEEDS={"d07_flor":[2323,3434],"d05_umidade":[2323,3434],"c04_palha":[2323,3434]}
for k,t in J.items():
    if args and k not in args: continue
    for s in SEEDS.get(k,[2323]):
        if os.path.exists(os.path.join(D,f"{k}_t{s}.jpg")): continue
        for tent in range(15):  # 8188 fora: espera 60 s, ate 15 min (nao sobe/mata ComfyUI)
            try: r=upload(os.path.join(D,k+".jpg")); run(f"{k}_t{s}",t+KEEPX,s,r,2.5); break
            except Exception as ex: print("retry",k,tent,str(ex)[:80],flush=True); time.sleep(60)
print("FIM")
