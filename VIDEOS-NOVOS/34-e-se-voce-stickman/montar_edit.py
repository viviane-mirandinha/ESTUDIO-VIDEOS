import json
def sc(i,s,e,scene,label,**p): return {"id":i,"type":"scene","track":"fundo","label":label,"start":s,"dur":round(e-s,2),"by":"template","props":{"scene":scene,"params":p}}
END=78.4
items=[
 sc("c1",0,6.6,"cozinha","Copo cai",modo="cai",rotulo="≈ 0,4 s",t_rot=4.3,rotulo2="queda de 80 cm",t_rot2=1.9),
 sc("c2",6.6,11.95,"cozinha","Você pega",modo="pega",rotulo="PRA VOCÊ: 4 s",t_rot=8.6,rotulo2="0,4 s × 10",t_rot2=8.3,t_corre=8.4,t_pega=10.9),
 sc("c3",11.95,15.2,"titulo","Título",linha1="E SE VOCÊ FOSSE",linha2="10× MAIS RÁPIDO?"),
 sc("c4",15.2,22.95,"troca","5 → 50 km/h",ia="walker",ta="5 km/h",meio="× 10",ib="car",tb="50 km/h",titulo="",em_a=18.9,em_m=20.9,em_b=21.8),
 sc("c5",22.95,26.05,"rua","Anda junto do carro",modo="andar",rotulo="50 KM/H",grande=True,t_rot=24.9,rotulo2="",t_rot2=99),
 sc("c6",26.05,31.3,"rua","Corre a 100",modo="correr",rotulo="100 KM/H",grande=True,t_rot=28.6,rotulo2="",t_rot2=99),
 sc("c7",31.3,38.45,"curva","Força do ar",titulo="1º PROBLEMA: O AR",em_t=32.8,em_ar=33.86,em_c=35.9,formula="F ∝ v²",em_f=36.7,eixo_x="velocidade",eixo_y="força do ar"),
 sc("c8",38.45,41.85,"troca","10x vel = 100x força",ia="runner",ta="10× velocidade",meio="",ib="wind",tb="100× força",titulo="",em_a=38.6,em_m=39.5,em_b=40.2),
 sc("c9",41.85,47.85,"formula","Energia",titulo="2º PROBLEMA: A BATIDA",em_t=42.4,formula="E = ½ · m · ",formula_destaque="v²",em_f=44.6,resultado="v × 10  →  E × 100",em_r=46.6),
 sc("c10",47.85,52.75,"rua","Poste",modo="poste",t_bate=48.7,rotulo="= ACIDENTE DE CARRO",t_rot=49.7,rotulo2="SÓ QUE SEM O CARRO",tam2=72,t_rot2=51.2,t_carro=51.1),
 sc("c11",52.75,60.95,"tempo","3 s → 30 s",titulo="E O SEU CÉREBRO?",em_t=53.5,linha_a="amigo fala",valor_a="3 s",em_a=58.0,linha_b="você sente",valor_b="30 s",em_b=59.2),
 sc("c12",60.95,69.15,"som","120 Hz → 12 Hz",valor_a="120 Hz",em_a=62.3,valor_b="12 Hz",em_b=63.9,zona="abaixo de 20 Hz: quase sem tom",em_c=65.3),
 sc("c13",69.15,70.95,"rua","Ronco arrastado",modo="conversa",fala="ôôôôôiii...",rotulo="",t_rot=99,rotulo2="",t_rot2=99),
 sc("c14",70.95,END,"rua","Fim",modo="fim",serif=True,rotulo="A PESSOA MAIS RÁPIDA DO MUNDO",t_rot=72.0,rotulo2="presa num mundo em câmera lenta",tam2=64,t_rot2=74.4),
]
ed={"version":1,"name":"34 - E SE VOCÊ (stickman) - E se você fosse 10 vezes mais rápido","estilo":"E SE VOCÊ — boneco de moletom + diagramas navy",
 "canvas":{"w":1280,"h":720,"fps":30,"bg":"#0b1330"},"duration":END,"template":"local",
 "fonts":{"DMSerif":"fonts/DMSerifDisplay-Regular.ttf","MontX":"fonts/Montserrat-ExtraBold.ttf"},
 "referencia":{"canal":"IFOLOGY","canal_url":"https://www.youtube.com/channel/UCv4DniMRgnBTmfFaxeMTTLA","video":"https://youtu.be/YznR5NmI3bc","titulo":"What IF You Could Stop Time?","nota":"só o estilo; personagem, nome e cenas próprios"},
 "audio":{"voice":{"src":"audio/voz.mp3","volume":1.0,"start":0},
   "music":{"src":"audio/musica.mp3","volume":0.10,"start":0,"fade_out":2.0,"duck":True},
   "extra":[{"id":"w1","src":"audio/whoosh.wav","start":15.1,"volume":0.22,"label":"whoosh"},
            {"id":"w2","src":"audio/whoosh.wav","start":31.2,"volume":0.22,"label":"whoosh"},
            {"id":"w3","src":"audio/whoosh.wav","start":52.65,"volume":0.22,"label":"whoosh"}]},
 "tracks":[{"id":"fundo","name":"Cenas"}],"items":items}
json.dump(ed,open("edit.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print(len(items))
