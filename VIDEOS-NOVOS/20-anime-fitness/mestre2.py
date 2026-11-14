from gen import gen
import sys
STY=(" Seinen manga ink illustration, black and white, fine detailed ink lines, grey screentone shading and hatching on the muscles, "
     "the only colors are the royal blue tank top and the charcoal grey cargo pants, pure solid black background, full body centered with empty black space around, no text, no watermark.")
M=("An original adult man about 24 years old with a mature masculine face, short jet-black hair with shaved undercut sides and a short slicked-back top, "
   "warm amber-brown eyes, thick dark eyebrows, light stubble on the jaw, a small scar through his left eyebrow, "
   "broad muscular bodybuilder physique, wearing a fitted royal blue sleeveless gym tank top, charcoal grey cargo training pants and black sneakers, "
   "standing upright in a relaxed front view, arms at his sides, calm serious expression.")
for s in [int(x) for x in (sys.argv[1:] or ["201","202","203","204"])]: gen("mestre_%d"%s,M+STY,seed=s)
