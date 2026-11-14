import json,shutil
NAME="38 - 24-10-2026 - COLAGEM DE PAPEL - Como o Titanic afundou em 1 minuto"
DUR=67.6
S=[
("s01","gancho",0,6.3,"Gancho: 2h40",{"numero":"2H40","rot1":"\u201cPRATICAMENTE INAFUND\u00c1VEL\u201d","rot2":"NO FUNDO DO MAR","t_foto":0.1,"t_num":0.7,"t_rot1":3.1,"t_rot2":4.85}),
("s02","partida",6.3,15.5,"10/04/1912 - partida",{"data":"10 ABR 1912","rotulo":"O MAIOR NAVIO DO MUNDO","origem":"SOUTHAMPTON","destino":"NOVA YORK","viagem":"1\u00aa VIAGEM","t_data":0.2,"t_foto":0.7,"t_rot":4.1,"t_mapa":5.3,"t_ori":5.6,"t_fim":8.0,"t_dest":6.65,"t_viagem":7.75}),
("s03","iceberg",15.5,24.4,"23:40 - iceberg",{"dias":"4 DIAS DEPOIS","hora":"23:40","local":"ATL\u00c2NTICO NORTE","tarde":"TARDE DEMAIS","t_dias":0.2,"t_hora":1.7,"t_x":3.1,"t_ice":5.3,"t_tarde":7.3}),
("s04","casco",24.4,35.9,"Casco: 5 compartimentos",{"lado":"LADO DIREITO (ESTIBORDO)","n_comp":"5 COMPARTIMENTOS","aguenta":"AGUENTAVA 4 ALAGADOS","com5":"COM 5...","carimbo":"CONDENADO","t_ice":0.5,"t_lado":1.5,"t_comp":4.15,"t_aguenta":6.2,"t_quatro":7.2,"t_com5":9.0,"t_carimbo":10.2}),
("s05","alaga",35.9,40.4,"A proa afunda",{"rotulo":"A PROA AFUNDA","t_agua":1.0,"passo":0.4,"t_proa":2.8,"t_rot":2.9}),
("s06","botes",40.4,48.2,"Botes x pessoas",{"botes":1178,"bordo":2224,"l1":"LUGARES NOS BOTES","n1":"1.178","l2":"PESSOAS A BORDO","n2":"+2.200","t_foto":0.2,"t_b1":2.1,"t_b2":6.3}),
("s07","parte",48.2,52.8,"2:20 - parte em dois",{"hora":"2:20","rotulo":"PARTIDO EM DOIS","credito":"pintura: Willy St\u00f6wer, 1912","t_foto":0.1,"t_hora":0.5,"t_parte":2.4,"t_some":3.25}),
("s08","balanco",52.8,60.0,"Mortos e sobreviventes",{"mortos":"+1.500 MORTOS","navio":"CARPATHIA","sobrev":"\u2248700 SOBREVIVENTES","t_jornal":0.1,"t_mortos":0.6,"t_carp":3.2,"t_sobrev":5.2}),
("s09","fundo",60.0,DUR,"1985 - destroços",{"ano":"1985","prof":"QUASE 4.000 M","credito":"Fotos: Wikimedia Commons (dom\u00ednio p\u00fablico)","t_foto":0.4,"t_ano":1.95,"t_prof":4.0,"t_cred":5.0}),
]
items=[{"id":i,"type":"scene","track":"fundo","label":lab,"start":a,"dur":round(b-a,2),"by":"template","props":{"scene":sc,"params":p}} for i,sc,a,b,lab,p in S]
st={i:a for i,_,a,_,_,_ in S}
wh=[6.3,24.4,40.4,48.2,52.8,60.0]
pap=[0.1,0.7,3.1,4.85,6.5,9.35,10.4,11.6,12.95,14.05,15.7,17.2,18.6,20.8,22.8,25.9,28.6,30.6,33.4,34.6,38.7,40.6,42.5,46.7,48.3,48.7,50.6,52.9,53.4,56.0,58.0,60.4,61.95,64.0]
E={"version":1,"name":NAME,"estilo":"38-colagem-de-papel","grupo":"ESTILOS NOVOS",
 "canvas":{"w":1280,"h":720,"fps":30,"bg":"#15120e"},"duration":DUR,"template":"local",
 "fonts":{"DM Serif Display":"fonts/DMSerifDisplay-Regular.ttf","Courier Prime":"fonts/CourierPrime-Bold.ttf","Anton":"fonts/Anton-Regular.ttf"},
 "referencia":{"canal":"Ordinary Origins","canal_url":"https://www.youtube.com/@OrdinaryOrigins-t4c","canal_url_2":"https://www.youtube.com/@abhijeetsinghvirdi","video":"https://www.youtube.com/watch?v=x5ireg7miPU","titulo":"How the Hamburger Conquered the World | A Paper-Cut History",
  "canal_2":"Fakeplastictree","video_2":"https://www.youtube.com/watch?v=CMqw9usH8-8","titulo_2":"Motion Graphic | Collage",
  "nota":"documentario em colagem de papel: fotos antigas P&B recortadas com borda branca, papel rasgado, fita adesiva, letras de jornal estilo bilhete de resgate, fundo escuro com textura, movimento stop-motion em passos (12 qps) e tremor dos recortes"},
 "audio":{"voice":{"src":"voz.wav","volume":1.0,"start":0},
  "music":{"src":"musica.wav","volume":0.10,"start":0,"fade_out":2.0,"duck":True},
  "extra":[{"id":f"w{k}","src":"sfx/whoosh.wav","start":t,"volume":0.16,"label":"whoosh"} for k,t in enumerate(wh)]+
          [{"id":f"p{k}","src":"sfx/papel.wav","start":t,"volume":0.10,"label":"papel"} for k,t in enumerate(pap)]},
 "tracks":[{"id":"fundo","name":"Cenas em colagem"}],"items":items}
json.dump(E,open("edit.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
shutil.copy("template_src.html","template.html")
print(len(items))
