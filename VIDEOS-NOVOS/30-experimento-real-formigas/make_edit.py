import json
NAME="30 - EXPERIMENTO SELVAGEM - O que acontece se você colocar 100 formigas numa caixa com 1 aranha"
items=[]
def shot(i,a,b,scene,label,**pr):
    items.append({"id":f"s{i:02d}","type":"scene","track":"fundo","label":label,"start":a,"dur":round(b-a,2),"by":"template","props":{"scene":scene,"params":pr}})
shot(1,0,2.2,"topo","Formigas entram pelo tubo",cam0=[330,520,1.9],cam1=[390,480,1.6])
shot(2,2.2,4.94,"lado_intro","Caixa de lado + luva solta a aranha")
shot(3,4.94,8.1,"topo","Aranha imóvel, pernas recolhidas",cam0=[640,325,2.3],cam1=[640,330,2.0])
shot(4,8.1,13.04,"topo","Exploram as paredes (geral)",cam0=[640,370,1.0],cam1=[640,370,1.1])
shot(5,13.04,16.34,"topo","Toca a pata traseira",cam0=[680,380,2.6],cam1=[680,375,2.9])
shot(6,16.34,19.62,"topo","Golpe e fuga",cam0=[620,430,1.8],cam1=[600,450,1.6])
shot(7,19.62,23.76,"topo","Cheiro de alarme / convergem",cam0=[640,380,1.05],cam1=[640,375,1.25])
shot(8,23.76,26.1,"topo","3 mortes em 10 s",cam0=[660,410,2.0],cam1=[660,405,2.2])
shot(9,26.1,30.7,"topo","Enxame sobe no cefalotórax",cam0=[640,360,2.0],cam1=[640,345,2.8])
shot(10,30.7,33.52,"lado_tomba","Tomba de lado (close lateral)")
shot(11,33.52,39.08,"topo","Cortam pernas, levam ao ninho",cam0=[780,300,1.05],cam1=[830,290,1.2])
shot(12,39.08,42.76,"topo","15 min: cefalotórax vazio",cam0=[640,385,2.2],cam1=[640,380,2.7])
shot(13,42.76,45.32,"cta","Inscreva-se / vespas")
shot(14,45.32,53.1,"versus","Número > veneno: 30 x 100")
n=[0]
def lab(a,b,text,x=640,y=110,size=52,estilo="tag",label=None,**kw):
    n[0]+=1; p={"text":text,"x":x,"y":y,"size":size,"estilo":estilo}; p.update(kw)
    items.append({"id":f"t{n[0]:02d}","type":"text","track":"textos","label":label or text,"start":a,"dur":round(b-a,2),"by":"template","props":p})
lab(0.75,2.2,"100 FORMIGAS OPERÁRIAS",y=640)
lab(2.4,3.55,"ARENA DE ACRÍLICO",seta={"x":163,"y":400,"ang":180})
lab(3.65,4.94,"1 ARANHA-LOBO ADULTA")
lab(6.85,8.1,"PERNAS RECOLHIDAS",y=640,seta={"ponto":"legR","ang":90,"dy":-6})
lab(8.9,10.45,"EXPLORAM AS PAREDES",y=250,seta={"x":640,"y":96,"ang":270})
lab(10.5,13.04,"IGNORAM O PREDADOR",y=590,seta={"ponto":"spider","ang":270,"dy":80})
lab(14.4,16.34,"TOCOU A PATA TRASEIRA",seta={"ponto":"tip7","ang":90,"dy":-10})
lab(17.26,18.7,"GOLPE ÚNICO!")
lab(18.75,19.62,"ESCAPOU!",color="#ffd23a")
lab(20.36,21.6,"CHEIRO DE ALARME",color="#ffb36b")
lab(21.64,23.76,"DEZENAS CONVERGEM")
lab(24.58,26.1,"3 EM 10 SEGUNDOS",y=640,size=56)
lab(27.36,28.9,"CEFALOTÓRAX",seta={"ponto":"ceph","ang":90,"dy":-30})
lab(28.96,30.7,"OLHOS E ARTICULAÇÕES")
lab(31.0,33.52,"TOMBOU DE LADO")
lab(34.92,37.4,"CORTAM AS PERNAS",y=650)
lab(37.5,39.08,"NINHO ARTIFICIAL",x=760,y=560,seta={"ponto":"nest","ang":270})
lab(41.2,42.76,"SÓ RESTOU O CEFALOTÓRAX",y=640,seta={"ponto":"ceph","ang":90,"dy":-40})
lab(42.9,45.32,"SE INSCREVA",x=380,y=300,size=64,estilo="btn")
lab(43.6,45.32,"PRÓXIMO TESTE: VESPAS",x=380,y=440,size=52)
lab(45.4,47.9,"O NÚMERO DE FORMIGAS",y=300,size=80,label="Número (grande)")
lab(46.38,47.9,"IMPORTA MAIS QUE O VENENO",y=430,size=64,color="#ffd23a",label="Veneno (grande)")
lab(47.94,53.1,"NÚMERO > VENENO",y=100,size=64)
lab(47.94,53.1,"30 FORMIGAS",x=330,y=255,size=48)
lab(48.8,53.1,"PERDERIAM",x=330,y=585,size=52,estilo="stamp",color="#d61f1f",rot=-6)
lab(50.12,53.1,"100 FORMIGAS",x=950,y=255,size=48)
lab(50.9,53.1,"CAÇADOR VIROU PRESA",x=950,y=585,size=48,estilo="stamp",color="#1f8a3a",rot=-5)
items.append({"id":"c1","type":"text","track":"cards","label":"Card MINUTO 0","start":4.94,"dur":1.8,"by":"template","props":{"text":"MINUTO 0","size":110}})
items.append({"id":"c2","type":"text","track":"cards","label":"Card MINUTO 15","start":39.08,"dur":1.9,"by":"template","props":{"text":"MINUTO 15","size":110}})
for i,(a,b,tx) in enumerate([(0.72,42.76,"FORMIGAS: 100"),(3.6,42.76,"ARANHA-LOBO: 1"),(24.58,42.76,"BAIXAS: 3"),(39.08,42.76,"MIN 15")]):
    items.append({"id":f"h{i+1}","type":"text","track":"hud","label":"HUD "+tx,"start":a,"dur":round(b-a,2),"by":"template","props":{"text":tx}})
items.append({"id":"vs_esq","type":"param","label":"Versus: painel 30 entra (s)","start":47.94,"props":{"value":47.94}})
items.append({"id":"vs_dir","type":"param","label":"Versus: painel 100 entra (s)","start":50.12,"props":{"value":50.12}})
items.append({"id":"tempos","type":"param","label":"Tempos da simulação (s)","props":{"value":{"entra":0.7,"aranha":3.6,"toque":14.38,"gira":16.76,"foge":17.0,"escapou":18.84,"alarme":20.36,"converge":21.64,"mortes":[24.6,25.15,25.7],"sobe":26.6,"tomba":30.82,"corta":34.92,"abd":37.2,"vazio":41.2}}})
ed={"version":1,"name":NAME,"estilo":"30-experimento-real-formigas","grupo":"ESTILOS NOVOS",
 "canvas":{"w":1280,"h":720,"fps":30,"bg":"#8f8ab3"},"duration":53.1,"template":"local",
 "referencia":{"canal":"Wild Experiments","canal_url":"https://www.youtube.com/channel/UCns0RTIxXRQKY0XC_doFvww","video":"https://youtu.be/u7IKFWsLC_U",
  "titulo":"2 Ant Colonies Race Through Obstacles & Meet After 30 Days (1.000 Red vs Black Ants) - [REUPLOAD]",
  "nota":"Original = terrário real filmado. Aqui: VARIANTE CARTOON 2D (cutaways do canal como vídeo inteiro): arena vista de cima + cortes laterais, 100 formigas e 1 aranha-lobo em SVG, simulação determinística em GSAP."},
 "audio":{"voice":{"src":"voz.wav","volume":1.0,"start":0}},
 "tracks":[{"id":"fundo","name":"Cenas (arena)"},{"id":"cards","name":"Cards MINUTO"},{"id":"textos","name":"Rótulos + setas"},{"id":"hud","name":"Placar"}],
 "items":items}
json.dump(ed,open("edit.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print(len(items))
