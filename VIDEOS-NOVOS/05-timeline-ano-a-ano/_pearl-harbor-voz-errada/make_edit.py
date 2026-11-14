import json
NOME="05 - TIMELINE DATA A DATA - Pearl Harbor hora a hora"
RED,YEL,BLU,CYA="#ff4d3a","#ffd23f","#4da3ff","#3fe0d0"
def navios(okl_vira=None,ari_fogo=None,rot_ari=None,rot_okl=None,tam=0.9):
    L=[("NEVADA",21.3672,-157.9480),("ARIZONA",21.3651,-157.9499),("TENNESSEE",21.3634,-157.9517),("W. VIRGINIA",21.3628,-157.9508),
       ("MARYLAND",21.3616,-157.9536),("OKLAHOMA",21.3610,-157.9527),("CALIFORNIA",21.3593,-157.9562)]
    out=[]
    for n,la,lo in L:
        d={"tipo":"navio","lat":la,"lon":lo,"ang":-140,"tam":tam}
        if n=="ARIZONA" and ari_fogo is not None: d.update(fogo=ari_fogo,fogo_tam=1.8)
        if n=="ARIZONA" and rot_ari: d.update(rotulo="ARIZONA",rot_t=rot_ari,lx=-70,ly=-26)
        if n=="OKLAHOMA" and okl_vira is not None: d.update(vira=okl_vira)
        if n=="OKLAHOMA" and rot_okl: d.update(rotulo="OKLAHOMA",rot_t=rot_okl,lx=80,ly=40)
        out.append(d)
    return out
S=[]
def mapa(id,label,s,e,**p): S.append({"id":id,"type":"scene","track":"mapa","label":label,"start":s,"dur":round(e-s,2),"by":"template","props":{"scene":"mapa-timeline","params":p}})
def card(id,label,s,e,**p): S.append({"id":id,"type":"scene","track":"cards","label":label,"start":s,"dur":round(e-s,2),"by":"template","props":{"scene":"card-palavra","params":p}})
mapa("c01","06:37 Ward afunda submarino",0,7.75,mapa="porto",foco=[21.306,-157.968],zoom=0.66,push=1.08,cy=380,
  hora="06:37",hora_cor=YEL,sub="7 DEZ 1941 · ENTRADA DO PORTO",titulos=[[0,"O PRIMEIRO TIRO","PRIMEIRO",YEL]],
  lugares=[["PEARL HARBOR",21.316,-157.958,0.3]],
  icones=[{"tipo":"destroier","lat":21.299,"lon":-157.979,"ang":-20,"tam":1.5,"rotulo":"USS WARD","t":0.4,"ly":-26},
          {"tipo":"sub","lat":21.3065,"lon":-157.9645,"ang":-60,"tam":1.6,"t":0.8,"ate":4.6}],
  setas=[{"de":[21.2995,-157.977],"para":[21.306,-157.9655],"t":3.4,"dur":0.6,"curva":0.25}],
  explosoes=[{"lat":21.3065,"lon":-157.9645,"t":4.1,"r":30}],
  caixas=[{"t":4.3,"texto":"SUBMARINO ANÃO AFUNDADO","rotulo":"O primeiro disparo americano da guerra"}])
card("c02","Card HESITA",7.75,11.3,palavra="HESITA?",topo="O ALARME SOA",topo_t=8.1,sub="A CADEIA DE COMANDO",sub_t=9.6,pilulas=[[10.66,"NINGUÉM AGE"]])
mapa("c03","07:02 Radar de Opana",11.3,21.0,mapa="ilha",foco=[21.86,-157.72],zoom=0.44,push=1.1,cy=300,
  hora="07:02",hora_cor=YEL,sub="RADAR DE OPANA · NORTE DE OAHU",
  titulos=[[11.3,"UMA NUVEM IMENSA","NUVEM",CYA],[17.18,"IGNORADO","IGNORADO",RED]],
  lugares=[["OAHU",21.55,-158.0,11.5]],
  icones=[{"tipo":"radar","lat":21.680,"lon":-157.993,"tam":1.3,"rotulo":"OPANA","t":11.5,"lx":0,"ly":42}],
  enxame=[{"tipo":"blip","de":[22.14,-157.98],"para":[21.92,-157.99],"t":13.6,"dur":7,"n":30,"stagger":0.05,"espalha":70,"lento":True,"rastro":False}],
  setas=[{"de":[22.02,-157.80],"para":[21.84,-157.84],"t":15.8,"dur":0.7,"curva":0.1}],
  caixas=[{"t":19.3,"texto":"“NÃO SE PREOCUPE COM ISSO.”","rotulo":"Tenente de plantão"}])
mapa("c04","07:48 Kaneohe",21.0,25.4,mapa="ilha",foco=[21.47,-157.80],zoom=1.0,push=1.07,cy=400,
  hora="07:48",hora_cor=RED,sub="BASE AERONAVAL DE KANEOHE",titulos=[[21.0,"AS PRIMEIRAS BOMBAS","BOMBAS",RED]],
  icones=[{"tipo":"base","lat":21.4505,"lon":-157.768,"tam":1.3,"rotulo":"KANEOHE","t":21.1,"lx":0,"ly":44}],
  enxame=[{"tipo":"aviao","de":[21.66,-157.88],"para":[21.46,-157.775],"t":21.2,"dur":2.6,"n":10,"stagger":0.12,"espalha":60}],
  explosoes=[{"lat":21.452,"lon":-157.771,"t":24.1,"r":28,"fica":True},{"lat":21.447,"lon":-157.764,"t":24.45,"r":22,"fica":True},{"lat":21.456,"lon":-157.777,"t":24.8,"r":20,"fica":True}])
mapa("c05","07:55 Primeira onda",25.4,32.6,mapa="ilha",foco=[21.55,-157.98],zoom=0.42,push=1.12,cy=330,
  hora="07:55",hora_cor=RED,sub="PRIMEIRA ONDA",titulos=[[25.4,"A PRIMEIRA ONDA","PRIMEIRA",YEL],[30.8,"MERGULHAM SOBRE O PORTO","PORTO",RED]],
  lugares=[["PEARL HARBOR",21.365,-157.955,25.5]],
  icones=[{"tipo":"base","lat":21.4505,"lon":-157.768,"tam":1.0,"t":25.4,"fogo":25.4,"fogo_tam":1.0}],
  enxame=[{"tipo":"aviao","de":[21.84,-158.06],"para":[21.375,-157.96],"t":27.3,"dur":3.4,"n":28,"stagger":0.09,"espalha":75}],
  numero={"t":28.68,"valor":183,"rotulo":"AVIÕES"})
mapa("c06","08:06 Arizona explode",32.6,41.2,mapa="porto",foco=[21.3628,-157.9528],foco2=[21.3646,-157.9505],zoom=1.45,push=1.1,cy=400,
  hora="08:06",hora_cor=RED,sub="FILEIRA DOS ENCOURAÇADOS",titulos=[[32.6,"A FILEIRA DOS ENCOURAÇADOS","",""],[35.1,"O ARIZONA EXPLODE","ARIZONA",RED]],
  icones=navios(ari_fogo=35.44,rot_ari=35.1),
  enxame=[{"tipo":"aviao","de":[21.374,-157.938],"para":[21.364,-157.952],"t":32.8,"dur":2.2,"n":6,"stagger":0.25,"espalha":40,"some":True,"tam":1.3}],
  explosoes=[{"lat":21.3651,"lon":-157.9499,"t":35.44,"r":70}],
  fumaca=[{"lat":21.3651,"lon":-157.9499,"t":36.2,"r":18}],
  numero={"t":37.0,"valor":1177,"rotulo":"MARINHEIROS MORTOS"})
mapa("c07","08:10 Oklahoma vira",41.2,48.0,mapa="porto",foco=[21.3622,-157.9525],foco2=[21.3612,-157.9530],zoom=1.7,push=1.08,cy=400,
  hora="08:10",hora_cor=RED,sub="QUATRO MINUTOS DEPOIS",titulos=[[41.2,"QUATRO MINUTOS DEPOIS","",""],[43.16,"O OKLAHOMA VIRA","VIRA",YEL]],
  icones=navios(okl_vira=43.5,ari_fogo=41.2,rot_okl=43.16,tam=1.0),
  fumaca=[{"lat":21.3651,"lon":-157.9499,"t":41.2,"r":20},{"lat":21.3634,"lon":-157.9517,"t":42.0,"r":14}],
  caixas=[{"t":45.38,"texto":"CENTENAS PRESOS VIVOS NO CASCO","rotulo":"Navio de cabeça para baixo"}])
mapa("c08","08:54 Segunda onda",48.0,54.5,mapa="ilha",foco=[21.52,-157.90],zoom=0.45,push=1.1,cy=360,
  hora="08:54",hora_cor=RED,sub="SEGUNDA ONDA",titulos=[[48.0,"A SEGUNDA ONDA","SEGUNDA",YEL]],
  lugares=[["PEARL HARBOR",21.365,-157.955,48.1]],
  fumaca=[{"lat":21.364,"lon":-157.952,"t":48.0,"r":12},{"lat":21.45,"lon":-157.77,"t":48.0,"r":10}],
  enxame=[{"tipo":"aviao","de":[21.82,-157.74],"para":[21.38,-157.95],"t":50.6,"dur":3.2,"n":18,"stagger":0.1,"espalha":70},
          {"tipo":"aviao","de":[21.76,-157.66],"para":[21.46,-157.775],"t":50.9,"dur":2.8,"n":8,"stagger":0.12,"espalha":45}],
  numero={"t":52.26,"valor":167,"rotulo":"AVIÕES"})
mapa("c09","09:45 Ultimo zero",54.5,59.6,mapa="ilha",foco=[21.60,-158.0],zoom=0.42,push=1.06,cy=380,
  hora="09:45",hora_cor=YEL,sub="FIM DO ATAQUE",titulos=[[54.5,"FIM DO ATAQUE","",""],[56.34,"O ÚLTIMO ZERO PARTE","ZERO",CYA]],
  lugares=[["PEARL HARBOR",21.365,-157.955,54.6]],
  fumaca=[{"lat":21.364,"lon":-157.952,"t":54.5,"r":16},{"lat":21.45,"lon":-157.77,"t":54.5,"r":12}],
  enxame=[{"tipo":"aviao","de":[21.39,-157.97],"para":[21.98,-158.12],"t":54.6,"dur":3.0,"n":7,"stagger":0.3,"espalha":50,"some":True},
          {"tipo":"aviao","de":[21.39,-157.97],"para":[21.98,-158.12],"t":56.9,"dur":2.6,"n":1,"espalha":0,"some":True,"tam":1.5}])
mapa("c10","Saldo",59.6,65.75,mapa="porto",foco=[21.3635,-157.955],zoom=1.1,push=1.05,cy=380,
  hora="7 DEZ 1941",hora_cor=RED,sub="BALANÇO DO ATAQUE",titulos=[[59.6,"O SALDO","SALDO",RED]],escurecer=0.5,escurecer_t=59.6,
  icones=navios(okl_vira=0,ari_fogo=0),
  fumaca=[{"lat":21.3651,"lon":-157.9499,"t":59.6,"r":20},{"lat":21.3615,"lon":-157.953,"t":59.6,"r":16},{"lat":21.359,"lon":-157.956,"t":59.6,"r":14}],
  cards=[{"t":59.66,"icone":"soldado","valor":2403,"rotulo":"americanos mortos"},{"t":63.48,"icone":"navio","valor":8,"rotulo":"encouraçados atingidos"}])
card("c11","Card AUSENTES",65.75,73.5,palavra="AUSENTES",topo="OS PORTA-AVIÕES",topo_t=66.3,sub="ERAM OS ALVOS PRINCIPAIS",sub_t=67.38,
  pilulas=[[68.84,"ENTERPRISE · NO MAR"],[69.3,"LEXINGTON · NO MAR"]],tag="ERRO ESTRATÉGICO",tag_t=70.48)
mapa("c12","CTA Midway",73.5,77.95,mapa="ilha",foco=[21.62,-158.0],zoom=0.36,push=1.05,cy=420,
  hora="4 JUN 1942",hora_cor=BLU,sub="PRÓXIMO: MIDWAY",titulos=[[73.5,"A PRÓXIMA BATALHA","PRÓXIMA",YEL],[76.4,"MIDWAY ESPERA","MIDWAY",BLU]],
  cta={"t":73.6,"ate":76.3},
  setas=[{"de":[21.62,-158.2],"para":[21.90,-158.32],"t":76.4,"dur":0.8,"curva":-0.15}],
  caixas=[{"t":76.45,"texto":"MIDWAY · 2.100 KM A NOROESTE","rotulo":""}])
E={"version":1,"name":NOME,"estilo":"05-timeline-ano-a-ano","grupo":"ESTILOS NOVOS",
 "canvas":{"w":1280,"h":720,"fps":30,"bg":"#0d1a24"},"duration":77.95,"template":"local",
 "fonts":{"Oswald":"fonts/Oswald-Bold.ttf","Anton":"fonts/Anton-Regular.ttf"},
 "audio":{"voice":{"src":"voz.wav","volume":1.0,"start":0},"music":{"src":"musica.mp3","volume":0.10,"start":0,"fade_out":2.0,"duck":True},
   "extra":[{"id":"w1","src":"sfx/whoosh.wav","start":7.62,"volume":0.15,"label":"whoosh card"},{"id":"w2","src":"sfx/whoosh.wav","start":65.62,"volume":0.15,"label":"whoosh card"}]},
 "tracks":[{"id":"mapa","name":"Cenas de mapa (hora a hora)"},{"id":"cards","name":"Cards claros"}],
 "referencia":{"video":"https://youtu.be/o5GOQ9Bj0wg","canal":"Atlas Unfolded","titulo":"The Entire Ukraine War in 25 Minutes (Animated With Maps)","nota":"ver ESTILOS-NOVOS/05-timeline-ano-a-ano"},
 "creditos":"Relevo: AWS Terrain Tiles (terrarium; USGS 3DEP/NOAA, domínio público). Costa de Pearl Harbor: © OpenStreetMap contributors (ODbL).",
 "items":S}
json.dump(E,open("edit.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print(len(S))
