import json
W=json.load(open("words.json",encoding="utf-8"))
ws=W["words"]
fix={"C.":"C,","A":"A,","Rua":"R.","Ourives":"ourives"}
out=[]
for i,x in enumerate(ws):
    if x["w"]=="A" and i+1<len(ws) and ws[i+1]["w"]=="Rua": x["w"]="A,"
    elif x["w"] in ("C.","Rua","Ourives"): x["w"]=fix[x["w"]]
    if x["w"]=="-se." and out: out[-1]["w"]+="-se."; out[-1]["e"]=x["e"]; continue
    out.append(x)
W["words"]=out; json.dump(W,open("words.json","w",encoding="utf-8"),ensure_ascii=False); json.dump(out,open("legenda.json","w",encoding="utf-8"),ensure_ascii=False)
DUR=52.9
NAME="17 - AVATAR REALISTA IA - Ela pagou 20 dolares numa joia que valia uma fortuna"
items=[]
def img(i,src,s,e,mot="zoom_in",amt=0.08,lab=None):
    items.append({"id":i,"type":"image","track":"fundo","label":lab or src,"start":s,"dur":round(e-s,2),
      "props":{"src":"img/"+src+".jpg","fill":True,"fit":"cover","motion":mot,"motion_amount":amt}})
def tit(i,txt,s,e,y=560,size=50,hl=None,hlc="#ffd23f",col="#ffffff",bg=""):
    items.append({"id":i,"type":"text","track":"textos","label":txt,"start":s,"dur":round(e-s,2),"in":"fade","out":"fade",
      "props":{"text":txt,"x":640,"y":y,"w":1180,"size":size,"color":col,"font":"Arial Black","weight":900,"align":"center",
        "stroke":"#0a0a0a","stroke_w":5,"shadow":True,"highlight":hl or [],"hl_color":hlc,"upper":True,"bg":bg,"pad":14 if bg else 0,"radius":10 if bg else 0,"italic":True}})
def valor(i,de,s,e,ate="",con="a",sub="",y=42,tam=110):
    items.append({"id":i,"type":"scene","track":"visual","label":"valor "+de,"start":s,"dur":round(e-s,2),
      "props":{"scene":"valor-avaliacao","params":{"de":de,"conector":con,"ate":ate,"cor":"#2ee04f","tam":tam,"y":y,"sub":sub,"cor_sub":"#ffffff"}}})
# planos: fala (avatar) <-> detalhe (sem avatar), cortes 3-6 s
img("p01","av_feira",0,3.3,"zoom_in",0.07,"AVATAR feira - paga 20 dolares")
img("p02","d_banca",3.3,6.72,"pan_right",0.08,"detalhe banca bijuteria")
img("p03","av_lupa",6.72,10.1,"zoom_in",0.09,"AVATAR em casa com lupa")
img("p04","d_puncao",10.1,13.12,"zoom_in",0.14,"macro puncao")
img("p05","d_puncao",13.12,17.34,"pan_left",0.18,"macro puncao (letras)")
img("p06","d_diamante",17.34,23.2,"zoom_in",0.1,"diamante de transicao")
img("p07","d_certificado",23.2,26.95,"pan_left",0.08,"certificado falso")
img("p08","av_leilao",26.95,30.6,"zoom_in",0.07,"AVATAR + avaliador NY")
img("p09","d_garras",30.6,33.4,"zoom_in",0.12,"montagem original")
img("p10","av_choque",33.4,38.86,"zoom_in",0.06,"AVATAR reacao valor")
img("p11","d_leilao",38.86,41.0,"zoom_in",0.08,"sala de leilao")
img("p12","av_cta",41.0,46.2,"zoom_in",0.07,"AVATAR CTA")
img("p13","d_relogio",46.2,DUR,"zoom_in",0.1,"relogio proximo video")
# selo do canal (canto superior)
items.append({"id":"selo","type":"text","track":"textos","label":"selo canal","start":0,"dur":DUR,
  "props":{"text":"OLHO CLÍNICO","x":150,"y":46,"w":260,"size":26,"color":"#ffd23f","font":"Oswald","weight":700,"align":"center",
    "bg":"rgba(0,0,0,.55)","pad":10,"radius":8,"shadow":False}})
# letras da puncao
for k,(L,s) in enumerate([("C",14.16),("A",14.6),("R",14.74)]):
    items.append({"id":"let%d"%k,"type":"text","track":"visual","label":"letra "+L,"start":s,"dur":round(17.3-s,2),"in":"zoom","out":"fade",
      "props":{"text":L,"x":440+k*200,"y":300,"w":180,"size":150,"color":"#ffd23f","font":"Arial Black","weight":900,"align":"center",
        "stroke":"#0a0a0a","stroke_w":7,"shadow":True}})
tit("t1","CARTIER · INÍCIO DO SÉCULO XX",15.0,17.3,hl=["CARTIER"])
tit("t2","DIAMANTE DE TRANSIÇÃO",18.6,21.1,hl=["DIAMANTE"])
tit("t3","COR J · PUREZA VS2",21.15,23.15,hl=["J","VS2"])
tit("t4","CERTIFICADO FALSO",24.28,26.9,hl=["FALSO"],hlc="#ff4b3e")
tit("t5","CASA DE LEILÕES · NOVA YORK",28.2,30.55)
tit("t6","MONTAGEM ORIGINAL",30.9,33.35,hl=["ORIGINAL"])
valor("v1","US$ 180 MIL",35.0,36.8,sub="VALOR DE MERCADO HOJE")
valor("v2","US$ 20",36.84,38.84,ate="US$ 180 MIL",con="→",sub="9 MIL VEZES O QUE ELA PAGOU",tam=96)
tit("t7","LEILÃO NO MÊS QUE VEM",39.18,40.95,hl=["LEILÃO"])
tit("t8","INSCREVA-SE",45.38,46.2,y=330,size=64,col="#ffffff",bg="#d61f26")
tit("t9","PRÓXIMO VÍDEO",46.5,49.6,y=120,size=56,hl=["PRÓXIMO"])
valor("v3","US$ 5",49.74,DUR,ate="MEIO MILHÃO",con="→",sub="RELÓGIO DE PULSO",tam=92)
# legenda palavra a palavra (amarela, estilo Antiques), escondida onde há valor verde
caps=[(0,34.95),(41.0,45.3)]
for k,(s,e) in enumerate(caps):
    items.append({"id":"leg%d"%k,"type":"caption","track":"legenda","label":"legenda","start":s,"dur":round(e-s,2),
      "props":{"words_file":"legenda.json","per_group":3,"x":640,"y":655,"size":48,"color":"#ffe14d","dim":"#ffffff",
        "font":"Oswald","weight":700,"stroke":"#000000","stroke_w":4,"shadow":True,"bg":""}})
E={"version":1,"name":NAME,"estilo":"17-avatar-realista-ia","grupo":"ESTILOS NOVOS",
 "canvas":{"w":1280,"h":720,"fps":30,"bg":"#101010"},"duration":DUR,"template":"generic",
 "fonts":{"Oswald":"fonts/Oswald-Bold.ttf"},
 "referencia":{"canal":"Antiques Gallery / Healoloogy / Nina Cooks","canal_url":"https://www.youtube.com/@Healoloogy",
   "video":"https://youtu.be/mK-bVg2Sk10","titulo":"Antiques Roadshow (réplica IA) — joias avaliadas",
   "nota":"avatar realista consistente (imagem-mestra img/avatar-mestre.jpg, seed 1717); ver ESTILOS-NOVOS/17-avatar-realista-ia/REFERENCIA.txt"},
 "audio":{"voice":{"src":"voz.wav","volume":1.0,"start":0}},
 "tracks":[{"id":"fundo","name":"Planos avatar / detalhe"},{"id":"visual","name":"Valores / letras"},{"id":"textos","name":"Títulos / selo"},{"id":"legenda","name":"Legenda"}],
 "items":items}
json.dump(E,open("edit.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print(len(items))
