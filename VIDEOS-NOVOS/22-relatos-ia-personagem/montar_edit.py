import json
W=json.load(open("words.json",encoding="utf-8")); DUR=round(W["duration"],2)
NAME="22 - RELATOS IA PERSONAGEM - O homem que plantou tomates no deserto e foi chamado de louco"
X=0.4  # meia-sobreposição do crossfade (0,8 s)
P=[("c01_chegada",0,5.0,"pan_right","HOMEM chega ao sertão com mudas e baldes"),
   ("d02_solo",5.0,9.3,"zoom_in","solo de pedra, sol, água na caneca"),
   ("c03_enterra",9.3,12.9,"zoom_in","HOMEM enterra os baldes"),
   ("c04_palha",12.9,15.85,"pan_left","HOMEM palha+esterco, planta no centro"),
   ("d05_umidade",15.85,19.75,"zoom_in","balde com palha úmida"),
   ("c06_vizinhos",19.75,21.5,"pan_right","vizinhos riem do HOMEM"),
   ("d07_flor",21.5,24.1,"zoom_in","primeira flor amarela"),
   ("c08_colheita",24.1,29.05,"zoom_in","HOMEM colhe tomates, mato cinza"),
   ("c09_segredo",29.05,31.0,"pan_left","HOMEM pensativo - o segredo"),
   ("c10_madrugada",31.0,35.6,"zoom_in","HOMEM rega gota a gota de madrugada"),
   ("c11_feira",35.6,38.6,"pan_right","HOMEM na feira da cidade"),
   ("c12_cta",38.6,42.55,"zoom_in","HOMEM olha pra câmera (CTA)"),
   ("c13_final",42.55,DUR,"zoom_out","HOMEM diante do deserto - final")]
items=[]
for i,(src,s,e,mot,lab) in enumerate(P):
    s2=max(0,s-X); e2=min(DUR,e+X)
    items.append({"id":"p%02d"%(i+1),"type":"image","track":"fundoA" if i%2==0 else "fundoB","label":lab,"start":round(s2,2),"dur":round(e2-s2,2),
      "in":"fade","out":"fade","props":{"src":"img/"+src+".jpg","fill":True,"fit":"cover","motion":mot,"motion_amount":0.07}})
items.append({"id":"cta","type":"text","track":"textos","label":"inscreva-se (fala 41.8s)","start":41.6,"dur":1.6,"in":"fade","out":"fade",
  "props":{"text":"Inscreva-se","x":640,"y":630,"w":520,"size":56,"color":"#fff4dc","font":"Cormorant Garamond","weight":700,"align":"center",
    "bg":"rgba(40,22,8,.62)","pad":14,"radius":12,"shadow":True}})
css=(".fx{position:absolute;inset:0;width:1280px;height:720px;pointer-events:none}"
 ".warm{background:rgba(255,150,60,.10);mix-blend-mode:soft-light}"
 ".vin{background:radial-gradient(ellipse at center,rgba(0,0,0,0) 55%,rgba(20,8,0,.55) 100%)}"
 ".grain{opacity:.10;mix-blend-mode:overlay}")
html=("<div class='fx warm'></div><div class='fx vin'></div>"
 "<svg class='fx grain' viewBox='0 0 1280 720'><filter id='g22'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/></filter>"
 "<rect width='1280' height='720' filter='url(#g22)'/></svg>")
items.append({"id":"fx","type":"html","track":"efeitos","label":"filtro quente + vinheta + grão","start":0,"dur":DUR,
  "props":{"html":html,"css":css,"x":640,"y":360,"w":1280,"h":720}})
E={"version":1,"name":NAME,"estilo":"22-relatos-ia-personagem","grupo":"ESTILOS NOVOS",
 "canvas":{"w":1280,"h":720,"fps":30,"bg":"#1a1208"},"duration":DUR,"template":"generic",
 "fonts":{"Cormorant Garamond":"fonts/CormorantGaramond-700.ttf"},
 "referencia":{"canal":"Bonafillo Relatos / Silas Mercer","canal_url":"https://www.youtube.com/@bonafillorelatos",
   "video":"https://youtu.be/Q45GcjC5Uas","titulo":"They Called Him Crazy for Planting Tomatoes Where They Would Never Grow",
   "nota":"personagem fixo: imagem-mestra img/mestre.jpg (Flux Kontext local t2i seed 2202 + restyle HQ), cenas via Kontext ReferenceLatent seed 2222; ver ESTILOS-NOVOS/22-relatos-ia-personagem/REFERENCIA.txt"},
 "audio":{"voice":{"src":"voz.wav","volume":1.0,"start":0}},
 "tracks":[{"id":"fundoA","name":"Ilustrações A"},{"id":"fundoB","name":"Ilustrações B (crossfade)"},{"id":"efeitos","name":"Filtro/vinheta/grão"},{"id":"textos","name":"CTA"}],
 "items":items}
json.dump(E,open("edit.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print(len(items),DUR)
