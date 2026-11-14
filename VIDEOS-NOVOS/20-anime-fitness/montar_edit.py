import json
M=json.load(open("masks.json"))
DUR=50.5
NAME="20 - ANIME FITNESS - Como forçar seus braços magros a crescer"
items=[]
def img(i,src,s,e,amt=0.05,lab=None):
    items.append({"id":i,"type":"image","track":"fundo","label":lab or src,"start":s,"dur":round(e-s,2),
      "props":{"src":"img/"+src+".jpg","fill":True,"fit":"cover","motion":"zoom_in","motion_amount":amt}})
def quadro(i,src,s,e,zoom=0.05,shake=0,sl=0,marca="",lab=None):
    items.append({"id":i,"type":"scene","track":"fundo","label":lab or src,"start":s,"dur":round(e-s,2),
      "props":{"scene":"anime-quadro","params":{"img":"img/"+src+".jpg","zoom":zoom,"shake":shake,"speedlines":sl,"marca":marca}}})
def musculo(i,base,s,e,rot,lab=None):
    items.append({"id":i,"type":"scene","track":"fundo","label":lab or base,"start":s,"dur":round(e-s,2),
      "props":{"scene":"musculo-destaque","params":{"img":"img/"+base+".jpg","mascara":"img/"+base+"_mask.png","zoom":0.04,"rotulos":rot,"tam":34}}})
def reps(i,s,e,sub=""):
    items.append({"id":i,"type":"scene","track":"fundo","label":"3 x 12 reps","start":s,"dur":round(e-s,2),
      "props":{"scene":"contador-reps","params":{"series":"3","reps":"12","sub":sub}}})
def txt(i,t,s,e,x=640,y=660,w=1100,size=48):
    items.append({"id":i,"type":"text","track":"textos","label":t,"start":s,"dur":round(e-s,2),"in":"fade","out":"fade",
      "props":{"text":t,"x":x,"y":y,"w":w,"size":size,"color":"#ffffff","font":"Inter","weight":400,"align":"center",
        "stroke":"","shadow":True,"bg":"","upper":False}})
def tela(i,t,s,e,size=52):  # frase sozinha no preto (como a referencia)
    items.append({"id":i+"_bg","type":"html","track":"fundo","label":"preto","start":s,"dur":round(e-s,2),
      "props":{"html":"<div></div>","css":"#%s_bg div{position:absolute;inset:0;background:#000}"%i,"x":640,"y":360,"w":1280,"h":720}})
    txt(i,t,s,e,y=360,size=size)
def L(base,cor,k,dx,dy,t):
    d=M[base][cor]; return {"t":t,"x":d[k+"_cx"] if k else d["cx"],"y":d[k+"_cy"] if k else d["cy"],"lx":(d[k+"_cx"] if k else d["cx"])+dx,"ly":(d[k+"_cy"] if k else d["cy"])+dy}
# --- planos (1 imagem a cada 1-4 s, corte seco) ---
img("p01","a_flex",0,2.0,0.06,"flex - bracos nao crescem")
tela("f01","você treina ego, não músculo.",2.0,3.5)
quadro("p02","a_balanco",3.5,6.1,0.05,shake=7,marca="x",lab="ERRADO balanca na rosca")
txt("t02","pare de balançar o corpo",3.56,6.05,x=200,y=470,w=360)
musculo("p04","a_biceps",6.1,8.45,[L("a_biceps","vermelho","left",-230,-70,"Bíceps")],"biceps destacado")
txt("t03","não faz o trabalho sozinho",6.3,8.4,x=1040,y=420,w=420)
quadro("p05","a_rosca",8.45,12.9,0.07,marca="ok",lab="rosca certa cotovelo colado")
txt("t04","cotovelos junto às costelas",8.5,10.7,x=1010,y=380,w=470)
txt("t05","suba controlado ↑ e aperte no topo",10.74,12.85,x=1010,y=380,w=470)
reps("p06",12.9,15.8,sub="cadência 2-0-2")
quadro("p07","a_tri_errado",15.8,18.7,0.05,shake=5,marca="x",lab="ERRADO triceps cotovelo aberto")
txt("t06","erro: abrir os cotovelos",16.9,18.65,y=80)
quadro("p08","a_tri_certo",18.7,21.2,0.05,marca="ok",lab="triceps certo cotovelo pro teto")
txt("t07","cotovelos apontados ao teto",19.38,21.15,y=80)
musculo("p09","a_costas",21.2,23.6,[L("a_costas","verde","left",-200,-60,"Tríceps"),L("a_costas","verde","right",200,-60,"Tríceps")],"triceps destacado")
txt("t08","desça até a testa e estenda sem travar",21.24,23.55,y=672)
items[-1]["props"].update({"bg":"rgba(0,0,0,.7)","pad":12,"radius":8})
reps("p10",23.6,25.0)
img("p11","a_segredo",25.0,26.9,0.06,"segredo")
txt("t09","o segredo que ninguém te conta",25.08,26.85,x=210,y=380,w=380)
musculo("p12","a_braco",26.9,28.3,[L("a_braco","laranja","",240,-60,"Braquial"),L("a_braco","verde","low",-240,40,"Antebraço")],"braquial + antebraco")
quadro("p13","a_martelo",28.3,31.65,0.06,marca="ok",lab="rosca martelo")
txt("t10","rosca martelo",28.34,29.6,x=1010,y=380,w=470,size=48)
txt("t11","pegada neutra, cotovelos parados",29.6,31.6,x=1010,y=380,w=470)
reps("p14",31.65,33.15)
items.append({"id":"p15","type":"scene","track":"fundo","label":"2x por semana","start":33.15,"dur":2.25,
  "props":{"scene":"semana-dias","params":{"dias":"D,S,T,Q,Q,S,S","marcados":"1,4","rotulo":"2x por semana"}}})
img("p16","a_dormir",35.4,36.5,0.05,"dormir 8h")
txt("t12","durma 8 horas",35.46,36.45,y=90)
img("p17","a_comer",36.5,38.5,0.05,"proteina")
txt("t13","proteína em toda refeição",36.58,38.45,y=80)
quadro("p18","a_camisa",38.5,42.1,0.07,sl=22,lab="manga apertando")
txt("t14","em 8 semanas",38.56,40.6,x=1010,y=380,w=470,size=48)
txt("t15","a manga da camisa vai apertar",40.6,42.05,x=1010,y=380,w=470)
musculo("p19","a_cotovelo",42.1,45.35,[L("a_cotovelo","vermelho","",-230,-80,"Cotovelo")],"cotovelo dor")
txt("t16","doeu? baixe a carga",43.6,45.3,x=1010,y=380,w=470)
img("p20","a_aponta",45.35,47.4,0.06,"CTA inscreva-se")
txt("t17","inscreva-se",45.42,47.35,x=230,y=380,w=420,size=56)
img("p21","a_agacha",47.4,DUR,0.06,"treino de pernas")
txt("t18","treino completo de pernas",47.6,DUR,x=1100,y=420,w=330)
E={"version":1,"name":NAME,"estilo":"20-anime-fitness","grupo":"ESTILOS NOVOS",
 "canvas":{"w":1280,"h":720,"fps":30,"bg":"#000000"},"duration":DUR,"template":"generic",
 "fonts":{"Inter":"fonts/Inter.ttf"},
 "referencia":{"canal":"ryoga.training","canal_url":"https://www.youtube.com/@ryoga.training",
   "video":"https://youtu.be/Ujdz-hT6lnQ","titulo":"How To Force Your Skinny Arms To Grow",
   "nota":"personagem anime ORIGINAL v2 (cabelo preto undercut, olhos ambar, regata azul, cargo cinza; img/mestre.jpg = Flux Kontext local t2i seed 203 + poses seed 2020); musculo = mascara nossa (img/*_mask.png) extraida da versao pintada; ver ESTILOS-NOVOS/20-anime-fitness"},
 "audio":{"voice":{"src":"voz.wav","volume":1.0,"start":0}},
 "tracks":[{"id":"fundo","name":"Quadros anime / cenas"},{"id":"textos","name":"Textos"}],
 "items":items}
json.dump(E,open("edit.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print(len(items))
