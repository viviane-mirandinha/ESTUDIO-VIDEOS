import json, math
NAME="23 - MILITAR HUD - O dia em que um sniper parou uma coluna inteira"
items=[]; n=[0]
def nid(p): n[0]+=1; return f"{p}{n[0]}"
def V(src,s,e,trim=0,motion="none",amt=0.06,lbl=""):
    items.append({"id":nid("v"),"type":"video","track":"fundo","label":lbl or src,"start":s,"dur":round(e-s,2),"props":{"src":src,"fill":True,"fit":"cover","trim":trim,"volume":0,"motion":motion,"motion_amount":amt}})
def I(src,s,e,motion="zoom_in",amt=0.08,lbl=""):
    items.append({"id":nid("i"),"type":"image","track":"fundo","label":lbl or src,"start":s,"dur":round(e-s,2),"props":{"src":src,"fill":True,"fit":"cover","motion":motion,"motion_amount":amt}})
def SC(scene,s,e,params,track="hud",lbl=""):
    items.append({"id":nid("s"),"type":"scene","track":track,"label":lbl or scene,"start":s,"dur":round(e-s,2),"props":{"scene":scene,"params":params}})
def T(txt,s,e,y=610,size=56,color="#ffffff",bg="rgba(0,0,0,.72)",w=1100,inn="slide_up",out="fade",lbl=""):
    items.append({"id":nid("t"),"type":"text","track":"textos","label":lbl or txt,"start":s,"dur":round(e-s,2),"in":inn,"out":out,
      "props":{"text":txt,"x":640,"y":y,"w":w,"size":size,"color":color,"font":"Oswald","weight":700,"align":"center","bg":bg,"pad":14,"radius":4,"shadow":True,"upper":True}})
def BIG(txt,s,e,y=330): T(txt,s,e,y=y,size=120,color="#ffd23a",bg="",w=900,inn="zoom",lbl="relógio "+txt)
def HUD(s,e,hora,modo="drone",rot="SETOR NORTE"): SC("hud-drone",s,e,{"modo":modo,"hora":hora,"rotulo":rot,"sinal":"REC","cor":"#9dff7a"},lbl=f"HUD {modo} {hora}")
def TERM(s,e): SC("termico",s,e,{"intensidade":0.22},track="filtro",lbl="térmico")
roadY=lambda x:34*math.sin(x/650)+16*math.sin(x/230)
def MAP(s,e,cam0,cam1,hora="06:00",lead0=3000,lead1=3000,**kw):
    p={"cam0":cam0,"cam1":cam1,"lead0":lead0,"lead1":lead1,"n":42,"gap":42,"t_explode":-1,"explodido":0,"marcas":[],"atingidos":[],"tiros":[],"t_parado":-1,"rotulos":[],"hora":hora,"rotulo":"SETOR NORTE","seed":23}
    p.update(kw); SC("mapa-tatico",s,e,p,track="fundo",lbl=f"mapa {hora}")
HIT=[2,7,12]
# 1 abertura drone
V("clips/aerial_g.mp4",0,4.8,0); HUD(0,4.8,"06:00"); BIG("06:00",0.0,1.7)
T("COLUNA DE ABASTECIMENTO",1.75,4.75)
# 2 mapa: 2 km expostos
MAP(4.8,7.2,[2000,0,4600],[2100,0,3800],lead0=1300,lead1=1700,marcas=["2km"])
# 3 sem drone
V("clips/truck1.mp4",7.2,10.3,2); T("NENHUM DRONE",7.26,10.25,y=520); T("NENHUM RECONHECIMENTO AVANÇADO",8.42,10.25,y=610)
# 4 área limpa
MAP(10.3,12.6,[2600,0,3000],[2700,0,2600],lead0=1700,lead1=2050,marcas=["limpa"])
# 5 primeiro caminhão km 3
I("img/f_caminhao.jpg",12.6,14.1,"zoom_in",0.06); HUD(12.6,14.1,"06:00"); T("PRIMEIRO CAMINHÃO",12.7,14.05)
MAP(14.1,15.5,[3000,0,1400],[3000,0,1100],lead0=3000,lead1=3000,t_explode=0.1,marcas=["km3"])
# 6 fogo supressor
V("clips/nato.mp4",15.5,17.4,0); T("FOGO SUPRESSOR IMEDIATO",15.56,17.35)
# 7 segundo tiro (mira)
V("clips/burn_t.mp4",17.4,20.4,2); TERM(17.4,20.4); HUD(17.4,20.4,"06:00","mira",""); T("SEGUNDO TIRO",17.9,20.35)
# 8 veículo 3
MAP(20.4,22.8,[2950,0,900],[2930,0,700],explodido=1,atingidos=[2],marcas=["veic3"],rotulos=[{"txt":"MOTORISTA · VEÍCULO 3","alvo":"veiculo","i":2,"dy":40,"t":0.1,"size":32,"cor":"#ff4a3a"}])
# 9 rádio
I("img/f_radio.jpg",22.8,24.4,"zoom_in",0.07); T("SILÊNCIO TOTAL NO RÁDIO",22.82,24.38)
# 10 linha das árvores
V("clips/forest_t.mp4",24.4,27.0,1,"pan_left",0.08); TERM(24.4,27.0); HUD(24.4,27.0,"06:00","mira","")
T("LINHA DAS ÁRVORES",24.6,26.95,y=610)
items.append({"id":"risco","type":"html","track":"textos","label":"risco vermelho","start":25.1,"dur":1.85,"in":"slide_left","out":"fade","props":{"html":"<div class='risco'></div>","css":".risco{width:100%;height:100%;background:#ff4a3a;border-radius:4px;box-shadow:0 2px 8px rgba(0,0,0,.6)}","x":640,"y":604,"w":540,"h":9}})
# 11 subsolo
MAP(27.0,28.3,[2700,-150,2200],[2930,-40,520],explodido=1,atingidos=[2],marcas=["arvores"]); T("ESTÁ NO SUBSOLO",27.0,28.28,y=360,size=72,inn="zoom")
# 12 poço camuflado
I("img/f_poco.jpg",28.3,30.6,"zoom_in",0.08); T("POÇO DE OBSERVAÇÃO CAMUFLADO",28.32,30.58)
# 13 40 m à esquerda
MAP(30.6,32.9,[2930,-20,440],[2930,-20,340],explodido=1,atingidos=[2],marcas=["poco","40m"],rotulos=[{"txt":"À ESQUERDA DA PISTA","x":2930,"y":round(roadY(2930),1),"dy":40,"t":1.5,"size":32,"cor":"#ffd23a"}])
# 14 espera
I("img/f_parada_t.jpg",32.9,36.9,"zoom_in",0.1); TERM(32.9,36.9); HUD(32.9,36.9,"06:00","mira","")
T("ELE ESPERA A COLUNA PARAR",32.94,34.62); T("ESPERA O PÂNICO",34.66,36.85)
# 15 tiros 3 e 4
V("clips/sniper3.mp4",36.9,41.0,1,"zoom_in",0.05); T("TERCEIRO TIRO",36.92,38.0); T("QUARTO TIRO",38.04,39.1); T("DOIS OFICIAIS DE LIGAÇÃO",39.14,40.95)
# 16 coluna trava + 06:20 sem flanco
MAP(41.0,42.4,[2400,0,2600],[2380,0,2800],explodido=1,atingidos=HIT,t_parado=0); T("A COLUNA TRAVA",41.0,42.35)
MAP(42.4,46.3,[2380,0,2800],[2550,-60,2400],hora="06:20",explodido=1,atingidos=HIT,t_parado=0,marcas=["flanco"]); BIG("06:20",42.38,43.9)
# 17 06:40 drone
I("img/f_coluna_g.jpg",46.3,49.0,"zoom_in",0.06); HUD(46.3,49.0,"06:40"); BIG("06:40",46.26,48.9)
# 18 42 veículos x 1 operador
MAP(49.0,52.6,[1950,0,4400],[2050,0,3900],hora="06:40",explodido=1,atingidos=HIT,t_parado=0,marcas=["poco"],rotulos=[{"txt":"42 VEÍCULOS","alvo":"comboio","dy":60,"t":0,"size":44,"cor":"#ff4a3a"},{"txt":"UM ÚNICO OPERADOR","alvo":"poco","dy":-150,"t":1.9,"size":44,"cor":"#9dff7a"}])
# 19 06:55 retirada tarde
V("clips/aerial2_g.mp4",52.6,56.5,0); HUD(52.6,56.5,"06:55"); BIG("06:55",52.6,54.5); T("A ORDEM DE RETIRADA CHEGA TARDE",54.56,56.45)
# 20 CTA
V("clips/sniper1.mp4",56.5,60.7,0,"zoom_in",0.05); T("SNIPER SÓ MATA ALVOS DE VALOR?",56.7,59.4)
T("INSCREVA-SE",59.5,60.7,y=600,size=64,bg="#c8281e",w=520,inn="pop",lbl="CTA inscreva-se")
# 21 relatório
SC("mil-relatorio",60.7,65.4,{"titulo":"RELATÓRIO FINAL","linha":"GASTO DE MUNIÇÃO","valor":"","carimbo":"14 CARTUCHOS","t_carimbo":3.3,"cor":"#c8281e"},track="fundo",lbl="relatório final")
# 22 14 tiros
V("clips/ammo.mp4",65.4,66.8,0,"zoom_in",0.06); BIG("14 TIROS",65.45,66.78,y=360)
# 23 final
MAP(66.8,69.4,[2000,0,3000],[1900,0,5200],hora="06:55",explodido=1,atingidos=HIT,t_parado=0,marcas=["poco"]); T("UMA COLUNA INTEIRA PARALISADA",66.84,69.35)
E={"version":1,"name":NAME,"estilo":"23-militar-footage","grupo":"ESTILOS NOVOS",
 "canvas":{"w":1280,"h":720,"fps":30,"bg":"#0b0c08"},"duration":69.4,"template":"generic",
 "fonts":{"Oswald":"fonts/Oswald-Bold.ttf"},
 "referencia":{"canal":"Military Storm","canal_url":"https://www.youtube.com/@MilitaryStorm-Official","video":"https://youtu.be/fSec-dzzKZI","titulo":"Ukrainian Sniper CATCHES Russian Motorcycles STORMING His Trench — Then THIS Happened...","nota":"Variante licenciada: sem footage de combate real; stock Pixabay + Flux local + mapa tático SVG + HUD drone/mira/térmico em HTML."},
 "audio":{"voice":{"src":"voz.mp3","volume":1.0,"start":0},"music":{"src":"musica.mp3","volume":0.07,"start":0,"fade_out":2.0,"duck":True},
   "extra":[{"id":f"w{i}","src":"sfx/whoosh.wav","start":t,"volume":0.12,"label":"whoosh suave"} for i,t in enumerate([4.75,26.95,48.95,66.75])]},
 "tracks":[{"id":"fundo","name":"Footage / mapa"},{"id":"filtro","name":"Filtro térmico"},{"id":"hud","name":"HUD drone/mira"},{"id":"textos","name":"Textos"}],
 "items":items}
json.dump(E,open("edit.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print(len(items),"itens")
