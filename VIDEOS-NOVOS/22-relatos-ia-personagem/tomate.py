# Correção: plantas -> tomateiro de verdade via Kontext a partir das cenas existentes (mesmo homem)
import sys,os
sys.argv=["gen.py","none"]
exec(open("gen.py",encoding="utf-8").read().split("os.makedirs(D,exist_ok=True)")[0])
TOM=("Replace every plant in the image with a real tomato plant (Solanum lycopersicum): broad compound tomato leaves made of several wide oval leaflets "
     "with irregular serrated lobed edges and a wrinkled crinkled surface, thick fuzzy hairy green stems; the leaves are NOT palmate, NOT thin narrow pointed fingers, NOT cannabis. ")
FRU="Add some ripe red and unripe green round tomatoes hanging on the vines. "
FLO=("Add a hanging cluster of five small bright vivid yellow tomato flowers, each flower with five narrow pointed petals bent sharply backward "
     "and a yellow cone in the centre, typical tomato blossoms, plus one tiny green tomato. ")
KEEPX=" Keep everything else exactly the same: same man (if present) with the same face, age, hat and clothes, same composition, same objects, same light."+STY
J={"c01_chegada":TOM,"c04_palha":TOM,"d05_umidade":TOM,"c06_vizinhos":TOM,"d07_flor":TOM+FLO,"c08_colheita":TOM+FRU,
   "c09_segredo":TOM+FRU,"c10_madrugada":TOM,"c11_feira":TOM,"c12_cta":TOM+FRU,"c13_final":TOM+FRU}
only=sys.argv[1:] if False else None
for k,t in J.items():
    if os.path.exists(os.path.join(D,k+"_t.jpg")): continue
    r=upload(os.path.join(D,k+".jpg")); run(k+"_t",t+KEEPX,2323,r,2.5)
print("FIM")
