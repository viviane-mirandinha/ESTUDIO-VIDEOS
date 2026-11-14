import json
NAME="27 - DOC STOCK MEGAPROJETOS - O avião sem janelas que está assustando a Boeing"
items=[]; n=[0]
def nid(p): n[0]+=1; return f"{p}{n[0]}"
def V(src,s,e,trim=0,motion="none",amt=0.05):
    items.append({"id":nid("v"),"type":"video","track":"fundo","label":src,"start":s,"dur":round(e-s,2),"props":{"src":src,"fill":True,"fit":"cover","trim":trim,"volume":0,"motion":motion,"motion_amount":amt}})
def I(src,s,e,motion="zoom_in",amt=0.08):
    items.append({"id":nid("i"),"type":"image","track":"fundo","label":src,"start":s,"dur":round(e-s,2),"props":{"src":src,"fill":True,"fit":"cover","motion":motion,"motion_amount":amt}})
def SC(scene,s,e,params,track="rotulos",lbl=""):
    items.append({"id":nid("s"),"type":"scene","track":track,"label":lbl or scene,"start":s,"dur":round(e-s,2),"props":{"scene":scene,"params":params}})
def R(txt,s,e,cor="amarelo",y=620,size=46): SC("rotulo-dado",s,e,{"texto":txt,"cor":cor,"pos":"esq","y":y,"size":size},lbl=f"rótulo {txt}")
def SP(itens,tempos,s,e,y=150): SC("spec-cards",s,e,{"itens":"|".join(itens),"tempos":"|".join(str(t) for t in tempos),"x":70,"y":y,"size":36},lbl="spec "+" / ".join(itens))
def C(txt,s,e,y=330,size=58,color="#ffffff",inn="fade"):
    items.append({"id":nid("t"),"type":"text","track":"textos","label":txt,"start":s,"dur":round(e-s,2),"in":inn,"out":"fade",
      "props":{"text":txt,"x":640,"y":y,"w":1100,"size":size,"color":color,"font":"Oswald","weight":700,"align":"center","bg":"rgba(0,0,0,.4)","pad":14,"radius":4,"shadow":True,"upper":True}})
# 1 Boeing domina
I("img/b737.jpg",0,2.3,"zoom_in",0.06); R("HÁ DÉCADAS",1.5,2.3)
# 2 sem janelas
V("clips/window.mp4",2.3,3.7,1); C("SEM JANELAS",2.7,3.68)
# 3 monopólio
V("clips/airport2.mp4",3.7,5.5,4); R("MONOPÓLIO",4.6,5.5)
# 4 JetZero asa voadora
I("img/jz.jpg",5.5,8.3,"zoom_in",0.08); C("JETZERO",6.7,8.28,y=300,size=64); R("ASA VOADORA",7.6,8.3,cor="azul")
# 5 combustível pela metade
V("clips/engine.mp4",8.3,11.6,1); R("COMBUSTÍVEL PELA METADE",10.1,11.6)
# 6 funde asa e fuselagem
I("img/x48sky.jpg",11.6,13.9,"zoom_in",0.07); SP(["ASA","+ FUSELAGEM"],[0.95,1.3],11.6,13.9)
# 7 sustentação
I("img/x48f.jpg",13.9,16.3,"pan_left",0.08); R("SUSTENTAÇÃO",15.1,16.3)
# 8 arrasto do tubo tradicional
V("clips/airport.mp4",16.3,18.8,2); R("ARRASTO DO TUBO TRADICIONAL",16.9,18.8)
# 9 cabines sem janelas com telas
I("img/f_cabine_telas.jpg",18.8,22.9,"zoom_in",0.08); SP(["SEM JANELAS LATERAIS","TELAS","EXTERIOR EM TEMPO REAL"],[0.4,1.9,3.0],18.8,22.9)
# 10 ideias estudadas para o formato
I("img/x48c.jpg",22.9,26.0,"zoom_out",0.08); C("IDEIAS ESTUDADAS",23.9,25.98)
# 11 estrutura leve e forte
I("img/f_estrutura.jpg",26.0,28.2,"zoom_in",0.06); SP(["MAIS LEVE","MAIS FORTE"],[1.3,1.85],26.0,28.2)
# 12 Delta
I("img/delta.jpg",28.2,30.9,"pan_right",0.07); R("DELTA",28.7,30.9,cor="azul",y=545); R("PARCERIA ESTRATÉGICA",29.6,30.9)
# 13 Força Aérea
V("clips/flight.mp4",30.9,33.6,0); R("FORÇA AÉREA DOS EUA",31.1,33.6,cor="azul")
# 14 manchete 235 milhões
I("img/jz.jpg",33.6,36.6,"zoom_out",0.06)
SC("eco_manchete",33.6,36.6,{"veiculo":"O DIÁRIO","secao":"AVIAÇÃO","titulo":"Força Aérea dos EUA investe 235 milhões de dólares no protótipo","destaque":"235 milhões de dólares","t_destaque":34.1,"rot":-2},track="manchete",lbl="manchete 235 milhões")
# 15 primeiro voo 2027
V("clips/takeoff.mp4",36.6,40.3,1,"zoom_in",0.04); C("PRIMEIRO VOO DE TESTE",36.9,40.28); R("2027",38.9,40.3,size=60)
# 16 serviço 2030
V("clips/wing.mp4",40.3,43.4,2); C("ENTRADA EM SERVIÇO",40.6,43.38); R("2030",42.3,43.4,size=60)
# 17 custo por assento
I("img/f_assentos.jpg",43.4,46.6,"zoom_in",0.08); C("SE CERTIFICAREM",43.6,44.7); R("CUSTO POR ASSENTO CAI",44.8,46.6)
# 18 Boeing perde referência do 737
I("img/b737.jpg",46.6,50.1,"pan_right",0.08); C("A BOEING PERDE A REFERÊNCIA",47.1,50.08); R("BOEING 737",48.4,50.1,cor="azul")
# 19 céu muda de dono
V("clips/sky.mp4",50.1,51.8,2); C("O CÉU MUDA DE DONO",50.3,51.78,size=64)
# 20 CTA
I("img/jz.jpg",51.8,53.9,"pan_left",0.08)
items.append({"id":"cta","type":"text","track":"textos","label":"CTA inscreva-se","start":51.85,"dur":2.0,"in":"slide_up","out":"fade","props":{"text":"INSCREVA-SE","x":640,"y":600,"w":520,"size":60,"color":"#ffffff","font":"Oswald","weight":700,"align":"center","bg":"#c8281e","pad":14,"radius":6,"shadow":True,"upper":True}})
# 21 final
I("img/f_cabine_telas.jpg",53.9,57.6,"zoom_out",0.07); C("O FUTURO DA AVIAÇÃO",54.1,57.55,y=290,size=60); C("NÃO TEM JANELAS, TEM TELAS",55.4,57.55,y=390,size=56,color="#ffd400")
# vinheta leve
items.append({"id":"vinheta","type":"html","track":"vinheta","label":"vinheta leve","start":0,"dur":57.6,"props":{"html":"<div class='vn'></div>","css":".vn{width:100%;height:100%;background:radial-gradient(ellipse at center,rgba(0,0,0,0) 55%,rgba(0,0,0,.42) 100%)}","x":640,"y":360,"w":1280,"h":720}})
E={"version":1,"name":NAME,"estilo":"27-doc-stock-megaprojetos","grupo":"ESTILOS NOVOS",
 "canvas":{"w":1280,"h":720,"fps":30,"bg":"#0b0d12"},"duration":57.6,"template":"generic",
 "fonts":{"Oswald":"fonts/Oswald-Bold.ttf"},
 "referencia":{"canal":"Innovation Core","canal_url":"https://www.youtube.com/channel/UC1cYR-ev0etAbjWoOkbUeQA","video":"https://youtu.be/H9LincTauEU","titulo":"America’s New Windowless Plane Is Shaking The Entire Aviation Industry","nota":"Estilo 27 (Flightside Insider/SIGNUM/Innovation Core/Polarisyn): stock Pixabay + fotos Wikimedia (JetZero/X-48 domínio público) + Flux local para cabine sem janelas; rótulo amarelo/azul, cards brancos, spec-cards, manchete."},
 "audio":{"voice":{"src":"voz.mp3","volume":1.0,"start":0},"music":{"src":"musica.mp3","volume":0.08,"start":0,"fade_out":2.0,"duck":True},
   "extra":[{"id":f"w{i}","src":"sfx/whoosh.wav","start":t,"volume":0.1,"label":"whoosh suave"} for i,t in enumerate([5.45,33.55,53.85])]},
 "tracks":[{"id":"fundo","name":"Stock / fotos"},{"id":"vinheta","name":"Vinheta"},{"id":"manchete","name":"Manchete"},{"id":"rotulos","name":"Rótulos / spec"},{"id":"textos","name":"Cards de texto"}],
 "items":items}
json.dump(E,open("edit.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print(len(items),"itens")
