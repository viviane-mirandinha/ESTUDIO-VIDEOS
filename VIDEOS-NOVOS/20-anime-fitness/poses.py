from gen import gen
K=(" Keep the exact same adult man: same short black undercut hair, same amber-brown eyes, same stubble and eyebrow scar, same face, same muscular build, same royal blue tank top, same charcoal grey cargo pants and black sneakers, "
   "same black and white manga ink lineart style with grey shading, pure solid black background, character centered, no text, no watermark.")
BAL=("Side view, he does a cheating standing barbell curl with bad form: he holds a long straight barbell with both hands in front of his body with an underhand grip, "
     "the bar is in his hands at belly height in front of him, NOT on his shoulders, elbows bent mid-curl, his torso leans far backward and his hips are thrust forward, "
     "swinging the barbell up with body momentum, strained face.")
P={
 "a_flex":"He stands in three-quarter view flexing his right biceps and looking down at his arm, frowning, disappointed.",
 "a_balanco":BAL,
 "a_biceps":"He does a front double biceps pose, both arms raised and flexed, serious face.",
 "a_rosca":"Side view, he does a strict standing dumbbell curl with one arm: elbow pinned tight against his ribs, forearm raised, squeezing the biceps at the top, focused face.",
 "a_tri_errado":"He lies on his back on a flat gym bench doing a lying triceps extension with an EZ bar, his elbows flared wide out to the sides, bad form, grimacing.",
 "a_tri_certo":"He lies on his back on a flat gym bench doing a lying triceps extension with an EZ bar, upper arms perfectly vertical with elbows pointing to the ceiling, lowering the bar to his forehead, controlled.",
 "a_costas":"Back view, he stands with his back to the viewer, arms hanging straight down and slightly away from the body, showing his back and the back of his arms.",
 "a_segredo":"Waist-up close view, he raises his index finger next to his face with a confident knowing half smile, as if telling a secret.",
 "a_martelo":"Side view, he does a hammer curl holding a dumbbell with a neutral grip, thumb on top, elbow fixed at his side, forearm raised.",
 "a_braco":"Close side view of his right arm only, bent at ninety degrees and flexed, from shoulder to hand, showing the upper arm and forearm muscles.",
 "a_dormir":"He sleeps peacefully on his back in a simple bed with a pillow and a blanket, eyes closed.",
 "a_comer":"He sits at a table eating a big plate of grilled chicken breast, eggs and rice with a fork, focused.",
 "a_camisa":"He now wears a plain white t-shirt with the charcoal grey cargo pants; the short sleeves are tight and stretched around his big flexed biceps, proud smile.",
 "a_cotovelo":"He holds his right elbow with his left hand, wincing in pain, looking at his elbow.",
 "a_aponta":"Waist-up view, he points his index finger straight at the viewer with a confident smile.",
 "a_agacha":"Side view, he does a deep barbell back squat with the barbell on his upper back, thighs parallel to the floor, strong legs.",
}
import sys
for k,t in P.items():
    if sys.argv[1:] and k not in sys.argv[1:]: continue
    gen(k,"Change the pose: "+t+K,ref="mestre",seed=2020)
for k,s in (("a_balanco_b",2021),("a_balanco_c",2022)):
    if sys.argv[1:] and k not in sys.argv[1:]: continue
    gen(k,"Change the pose: "+BAL+K,ref="mestre",seed=s)
C={
 "a_biceps_cor":("a_biceps","Paint only the biceps muscle on the front of each upper arm, between the shoulder and the elbow, with a solid bright red color fill, like an anatomy chart highlight. Do not paint the shoulders, the chest, the neck or the forearms. Keep everything else exactly the same."),
 "a_costas_cor":("a_costas","Paint only the triceps muscles on the back of both upper arms with a solid bright green color fill, like an anatomy chart highlight. Keep everything else exactly the same."),
 "a_braco_cor":("a_braco","Paint the brachialis muscle on the lower outer side of the upper arm with solid bright orange, and paint the forearm muscles with solid bright green, like an anatomy chart highlight. Keep everything else exactly the same."),
 "a_cotovelo_cor":("a_cotovelo","Paint only his right elbow joint area with a glowing solid bright red color, like a pain highlight. Keep everything else exactly the same."),
}
for k,(r,t) in C.items():
    if sys.argv[1:] and k not in sys.argv[1:]: continue
    gen(k,t,ref=r,seed=2020,guid=2.5)
print("FIM")
