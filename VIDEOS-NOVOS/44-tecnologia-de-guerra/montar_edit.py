import json
items=[]
def P(i,l,v): items.append({"id":i,"type":"param","label":l,"props":{"value":v}})
P("cor_wire","Cor do wireframe","#39ff88"); P("cor_hud","Cor HUD/rótulos","#ffb000"); P("hud_topo","Texto do HUD (topo)","ARQUIVO TÉCNICO 044 // ANÁLISE")
SC=[("sc_hero","3D: porta-aviões girando",0,7.9),("sc_eiffel","3D: comparação Torre Eiffel",7.9,11.1),("sc_xray","3D: raio-x reatores",11.1,17.5),
("sc_cat","3D: catapulta",17.5,32.2),("sc_land","3D: pouso com cabo",32.2,44.1),("sc_bolter","3D: toque e arremetida",44.1,51.5),
("sc_mapa","Mapa: alcance em 24 h",51.5,57.2),("sc_final","3D: final girando",57.2,62.0)]
for i,l,a,b in SC: items.append({"id":i,"type":"html","track":"fundo","label":l,"by":"template","start":a,"dur":round(b-a,2),"props":{"html":""}})
R=[("rt_ilha","ILHA (PONTE DE COMANDO)","ilha",1.6,4.6,70,-60),("rt_comp","≈ 333 m","comp",5.0,7.8,0,-50),
("rt_nimitz","NIMITZ ≈ 333 m","nimitz",8.3,11.0,-60,60),("rt_eiffel","TORRE EIFFEL ≈ 330 m","eiffel",8.7,11.0,60,-50),
("rt_reator1","REATOR 1","r1",14.3,17.3,-90,70),("rt_reator2","REATOR 2","r2",14.5,17.3,90,70),
("rt_cat","TRILHO DA CATAPULTA","cat",22.3,24.3,40,-70),("rt_vapor","VAPOR DOS REATORES","vapor",24.4,27.4,-60,80),
("rt_cabos","CABOS DE AÇO","cabos",34.9,37.6,60,-70),("rt_gancho","GANCHO","gancho",38.6,41.0,-70,60)]
for i,t,a,s,e,dx,dy in R: items.append({"id":i,"type":"text","track":"rotulos","label":"Rótulo: "+t,"by":"template","start":s,"dur":round(e-s,2),"props":{"text":t,"anchor":a,"dx":dx,"dy":dy}})
items.append({"id":"cnt_cat","type":"html","track":"contadores","label":"Contador: catapulta","by":"template","start":27.7,"dur":4.4,"props":{"html":"","from":0,"to":265,"suffix":"km/h","label":"VELOCIDADE","ramp":2.1,"x":1220,"y":430,"size":96}})
items.append({"id":"cnt_land","type":"html","track":"contadores","label":"Contador: pouso","by":"template","start":40.2,"dur":3.7,"props":{"html":"","from":240,"to":0,"suffix":"km/h","label":"VELOCIDADE","ramp":2.0,"x":1220,"y":430,"size":96}})
for i,t,km,s in [("m1","6 h · 333 km",333,52.3),("m2","12 h · 667 km",667,53.0),("m3","24 h · 1.333 km",1333,54.6)]:
    items.append({"id":i,"type":"html","track":"mapa","label":"Anel: "+t,"by":"template","start":s,"dur":round(57.2-s,2),"props":{"html":"","text":t,"km":km}})
G="#39ff88"; A="#ffb000"
def T(i,txt,s,e,x,y,w,size=30,font="Share Tech Mono",color=G,align="left",inn="fade",hl=None,bg="rgba(2,14,8,.72)"):
    p={"text":txt,"x":x,"y":y,"w":w,"size":size,"color":color,"font":font,"weight":700,"align":align,"bg":bg,"pad":12,"radius":2,"shadow":False}
    if hl: p.update({"highlight":hl,"hl_color":A})
    items.append({"id":i,"type":"text","track":"textos","label":txt[:30],"start":s,"dur":round(e-s,2),"in":inn,"out":"fade","props":p})
T("tx_gancho","UMA PISTA DE POUSO QUE NAVEGA",0.35,2.5,640,610,1000,58,"Rajdhani","#ffffff","center","slide_up",["NAVEGA"],"rgba(0,0,0,0)")
T("tx_alvo","ALVO: PORTA-AVIÕES · CLASSE NIMITZ",2.6,7.8,420,124,700,30,hl=["CLASSE NIMITZ"])
T("d1","COMPRIMENTO ≈ 333 m",5.1,7.8,1030,200,380,28,hl=["333 m"])
T("cap0","RAIO-X // CASCO",11.3,17.3,320,124,420,30)
T("d2","DESLOCAMENTO ≈ 97.000 t",11.8,17.3,1020,200,400,28,hl=["97.000 t"])
T("d3","PROPULSÃO: 2 REATORES",14.3,17.3,1020,252,400,28,hl=["2 REATORES"])
T("d4","VELOCIDADE: 30+ NÓS",16.2,17.3,1020,304,400,28,hl=["30+ NÓS"])
T("cap1","01 // CATAPULTA",17.7,32.0,300,124,380,32)
T("tx_2s","0 → 265 km/h EM ≈ 2 s",30.0,32.0,640,620,700,40,align="center",hl=["≈ 2 s"])
T("cap2","02 // CABOS DE PARADA",32.4,43.9,340,124,460,32)
T("tx_100","PARADA EM ≈ 100 m · ≈ 2 s",41.4,43.9,640,620,760,40,align="center",hl=["≈ 100 m"])
T("cap3","03 // TOQUE E ARREMETIDA",44.3,51.3,350,124,480,32)
T("tx_toque","NO TOQUE: POTÊNCIA MÁXIMA",45.4,48.0,640,620,760,40,align="center",hl=["POTÊNCIA MÁXIMA"])
T("tx_errou","GANCHO ERROU OS CABOS → DECOLA DE NOVO",48.0,51.3,640,620,1000,38,align="center",hl=["DECOLA DE NOVO"])
T("cap4","04 // DISTÂNCIA EM 24 h",51.7,57.0,330,124,460,32)
T("tx_conta","30 NÓS × 24 h ≈ 1.333 km",54.8,57.0,640,650,700,36,align="center",hl=["1.333 km"])
T("tx_fim","UMA BASE AÉREA QUE MUDA DE LUGAR",57.7,61.5,640,610,1100,54,"Rajdhani","#ffffff","center","slide_up",["MUDA DE LUGAR"],"rgba(0,0,0,0)")
edit={"version":1,"name":"44 - TECNOLOGIA DE GUERRA - Como funciona um porta-aviões","estilo":"Tecnologia de guerra (3D wireframe + HUD)",
"referencia":{"canais":["AiTelly — How Aircraft Carrier Works? US Nuclear Power Ship Nimitz Class (https://www.youtube.com/watch?v=Yuz2XWgUT4I)",
 "Science Simplified 4 All — What is a Ballistic Missile? (https://www.youtube.com/watch?v=QPOG__ExSxs)"],"arquivo":"ref/ref.mp4","medicao":"ref/ESTILO-MEDIDO.md"},
"canvas":{"w":1280,"h":720,"fps":30,"bg":"#05080a"},"duration":62.0,"template":"local",
"fonts":{"Rajdhani":"fonts/Rajdhani-Bold.ttf","Share Tech Mono":"fonts/ShareTechMono.ttf"},
"build_script":"montar_edit.py + template.html (Three.js low-poly/wireframe, HUD SVG, mapa de anéis)",
"audio":{"voice":{"src":"voz.wav","volume":1.0,"start":0},
 "extra":[{"id":"w1","src":"sfx/whoosh.wav","start":17.35,"volume":0.22,"label":"whoosh cap.1"},{"id":"w2","src":"sfx/whoosh.wav","start":32.05,"volume":0.22,"label":"whoosh cap.2"},{"id":"w3","src":"sfx/whoosh.wav","start":51.35,"volume":0.22,"label":"whoosh mapa"}]},
"tracks":[{"id":"fundo","name":"Cenas 3D"},{"id":"rotulos","name":"Rótulos 3D"},{"id":"contadores","name":"Contadores"},{"id":"mapa","name":"Anéis do mapa"},{"id":"textos","name":"HUD / textos"}],
"items":items}
json.dump(edit,open("edit.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print(len(items))
