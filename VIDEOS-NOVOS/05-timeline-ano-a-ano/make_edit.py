import os
# Gera template.html (a partir de tpl_base.html + mascara de terra do GeoJSON) e edit.json
import json,math
NOME="05 - TIMELINE DATA A DATA - A Guerra dos Cem Anos data a data"
GEO=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "recursos", "mapas", "countries50m.geojson")
META=json.load(open("mapas.json"))
M=META["europa"]
RED,YEL,BLU,CYA="#ff4d3a","#ffd23f","#4da3ff","#3fe0d0"
def px(lat,lon):
    n=256*2**M["z"];r=math.radians(lat)
    return ((lon+180)/360*n-M["x0"]),((1-math.log(math.tan(r)+1/math.cos(r))/math.pi)/2*n-M["y0"])
# ---------- mascara de terra (clipPath) em pixels do mapa
G=json.load(open(GEO,encoding="utf-8"))["features"]
segs=[];FRANCA=None
for f in G:
    g=f["geometry"];polys=g["coordinates"] if g["type"]=="MultiPolygon" else [g["coordinates"]]
    if f["properties"].get("ADMIN")=="France":
        FRANCA=max((pl[0] for pl in polys),key=len)
    for pl in polys:
        ring=pl[0]
        if max(p[0] for p in ring)<-14 or min(p[0] for p in ring)>18 or max(p[1] for p in ring)<40 or min(p[1] for p in ring)>57: continue
        pts=[px(p[1],p[0]) for p in ring];keep=[pts[0]]
        for q in pts[1:]:
            if math.hypot(q[0]-keep[-1][0],q[1]-keep[-1][1])>=3: keep.append(q)
        if len(keep)<4: continue
        segs.append("M"+"L".join(f"{q[0]:.0f},{q[1]:.0f}" for q in keep)+"Z")
LAND="".join(segs)
# ---------- regioes aproximadas (lat,lon) — passam do litoral para o mar (o clip corta)
def resamp(P,N=64):
    P=[(a,b*0.68) for a,b in P]
    if sum(P[i][1]*P[(i+1)%len(P)][0]-P[(i+1)%len(P)][1]*P[i][0] for i in range(len(P)))<0: P=P[::-1]
    i0=max(range(len(P)),key=lambda i:P[i][0]-P[i][1]);P=P[i0:]+P[:i0];P=P+[P[0]]
    L=[0]
    for i in range(1,len(P)): L.append(L[-1]+math.hypot(P[i][0]-P[i-1][0],P[i][1]-P[i-1][1]))
    out=[];j=0
    for k in range(N):
        d=L[-1]*k/N
        while L[j+1]<d: j+=1
        u=(d-L[j])/(L[j+1]-L[j]+1e-12)
        out.append([round(P[j][0]+(P[j+1][0]-P[j][0])*u,4),round((P[j][1]+(P[j+1][1]-P[j][1])*u)/0.68,4)])
    return out
ENG=[(55.0,-5.6),(55.0,-3.0),(55.8,-2.0),(55.8,2.4),(51.45,2.0),(51.05,1.5),(50.6,0.3),(50.2,-3.0),(49.8,-6.5),(51.9,-5.7),(53.6,-5.0),(54.5,-5.6)]
GASC=resamp([(45.8,-2.8),(45.7,-0.9),(45.3,-0.4),(44.9,0.1),(44.4,0.2),(43.9,-0.2),(43.5,-0.8),(43.35,-1.4),(43.65,-2.8)])
BRET=resamp([(47.3,-3.2),(47.0,-0.5),(46.6,0.8),(46.0,1.6),(45.3,2.2),(44.6,2.6),(44.0,2.0),(43.5,1.2),(43.1,0.5),(42.95,-0.5),(43.35,-1.4),(43.65,-2.8)])
PEQ=resamp([(45.5,-2.8),(45.3,-0.9),(44.9,-0.45),(44.4,-0.6),(43.8,-1.0),(43.35,-1.4),(43.65,-2.8)])
CAL=[(51.3,1.4),(50.88,1.6),(50.8,1.95),(50.92,2.15),(51.3,2.25)]
NORTE=[(49.8,-2.4),(51.1,1.2),(51.15,2.4),(50.2,3.2),(49.6,4.4),(48.6,4.6),(48.0,3.5),(47.9,2.2),(48.1,1.0),(48.3,-0.3),(48.55,-1.4),(48.9,-2.4)]
FR=[(p[1],p[0]) for p in FRANCA][::3]
ING={"cor":"#8b4513","op":0.62}
def A(nome,kf,**k): d={"nome":nome,"kf":[[t,[list(q) for q in s]] for t,s in kf]};d.update(ING);d.update(k);return d
def base(t=None,aq=PEQ): return [A("Inglaterra",[(0,ENG)],t=t),A("Aquitânia inglesa",[(0,aq)],t=t),A("Calais",[(0,CAL)],t=t)]
S=[]
def mapa(id,label,s,e,**p):
    p.setdefault("mapa","europa"); S.append({"id":id,"type":"scene","track":"mapa","label":label,"start":s,"dur":round(e-s,2),"by":"template","props":{"scene":"mapa-timeline","params":p}})
def card(id,label,s,e,**p): S.append({"id":id,"type":"scene","track":"cards","label":label,"start":s,"dur":round(e-s,2),"by":"template","props":{"scene":"card-palavra","params":p}})
def ic(tipo,lado,lat,lon,t,**k): d={"tipo":tipo,"lado":lado,"lat":lat,"lon":lon,"t":t};d.update(k);return d
GR=34  # rotulo grande de pais
mapa("c01","1337 Eduardo III",0,6.9,cam=[[0,48.6,2.0,0.252]],push=1.05,cy=430,
  ano="1337",ano_cor=YEL,sub="EDUARDO III",titulos=[[1.84,"A COROA FRANCESA","COROA",YEL],[4.96,"A GUERRA DOS CEM ANOS COMEÇA","CEM ANOS",RED]],
  areas=[A("Inglaterra",[(0,ENG)],t=0.3),A("Aquitânia inglesa",[(0,GASC)],t=0.8)],
  lugares=[["INGLATERRA",52.6,-1.6,0.4,GR],["FRANÇA",47.2,2.6,0.4,GR]],
  icones=[ic("coroa","ing",51.6,-0.6,1.84,tam=1.4,rotulo="EDUARDO III",ly=-34),ic("coroa","fra",48.6,2.4,3.94,tam=1.4)],
  setas=[{"de":[51.3,0.2],"para":[48.95,2.2],"t":2.88,"dur":0.9,"curva":-0.2}])
mapa("c02","1346 Crécy",6.9,12.75,cam=[[6.9,50.15,1.95,1.45]],push=1.06,cy=400,
  ano="1346",ano_cor=RED,sub="CRÉCY",titulos=[[7.36,"CRÉCY","CRÉCY",YEL],[9.6,"ARQUEIROS INGLESES","ARQUEIROS",RED],[10.86,"DESTROEM A CAVALARIA FRANCESA","CAVALARIA",RED]],
  areas=base(),lugares=[["CRÉCY",50.255,1.88,7.36]],
  icones=[ic("arqueiro","ing",50.38,1.70,8.0),ic("arqueiro","ing",50.30,1.60,8.15),ic("arqueiro","ing",50.44,1.82,8.3)],
  enxame=[{"tipo":"cavaleiro","lado":"fra","de":[49.85,2.60],"para":[50.17,2.08],"t":7.8,"dur":2.2,"n":7,"stagger":0.12,"espalha":55,"gira":False,"ate":10.9},
          {"tipo":"flecha","de":[50.37,1.73],"para":[50.19,2.05],"t":9.7,"dur":0.7,"n":16,"stagger":0.05,"espalha":40,"some":True,"rastro":False}],
  explosoes=[{"lat":50.19,"lon":2.03,"t":10.4,"r":26},{"lat":50.16,"lon":2.08,"t":10.6,"r":22}],
  escurecer=0.55,escurecer_t=10.86,
  cards=[{"t":10.86,"icone":"arqueiro","lado":"ing","rotulo":"ARQUEIROS<br>INGLESES"},{"t":11.1,"icone":"cavaleiro","lado":"fra","rotulo":"CAVALARIA<br>FRANCESA","risca":11.6}])
mapa("c03","Poitiers / cede territórios",12.75,19.7,cam=[[12.75,46.58,0.34,1.25],[16.9,46.1,0.4,0.36,1.5]],push=1.03,cy=400,
  ano="+10 ANOS",ano_cor=YEL,sub="POITIERS",
  titulos=[[12.88,"DEZ ANOS DEPOIS","",""],[14.12,"POITIERS","POITIERS",YEL],[15.2,"O REI JOÃO II É CAPTURADO","CAPTURADO",RED],[17.1,"A FRANÇA PAGA RESGATE","RESGATE",YEL],[18.62,"E CEDE TERRITÓRIOS","TERRITÓRIOS",RED]],
  areas=[A("Inglaterra",[(0,ENG)]),A("Aquitânia inglesa",[(0,GASC),(18.62,BRET)],md=1.0),A("Calais",[(0,CAL)],t=18.9)],
  lugares=[["POITIERS",46.58,0.34,14.12]],
  icones=[ic("soldado","ing",46.78,0.02,13.0),ic("soldado","fra",46.42,0.70,13.1),ic("coroa","fra",46.38,0.28,15.44,rotulo="JOÃO II",ly=42)],
  setas=[{"de":[46.74,0.06],"para":[46.43,0.25],"t":15.7,"dur":0.6,"curva":0.2}])
card("c04","Card 1369",19.7,24.5,topo="A PARTIR DE",topo_t=20.3,palavra="1369",palavra_t=20.9,sub="CARLOS V INVERTE A MARÉ",sub_t=22.7)
mapa("c05","Du Guesclin recupera",24.5,27.2,cam=[[24.5,46.0,0.6,0.33]],push=1.04,cy=400,
  ano="1369",ano_cor=BLU,sub="DU GUESCLIN",titulos=[[24.6,"BERTRAND DU GUESCLIN","DU GUESCLIN",CYA],[25.86,"RECUPERA QUASE TUDO","QUASE TUDO",YEL]],
  areas=[A("Inglaterra",[(0,ENG)]),A("Aquitânia inglesa",[(0,BRET),(25.86,PEQ)],md=1.2),A("Calais",[(0,CAL)])],
  icones=[ic("cavaleiro","fra",46.9,2.0,24.7,tam=1.3,rotulo="DU GUESCLIN",ly=-36)],
  setas=[{"cor":"fra","de":[46.7,1.7],"para":[45.5,0.5],"t":25.9,"dur":0.8,"curva":0.15},{"cor":"fra","de":[46.9,1.5],"para":[46.6,-0.5],"t":26.1,"dur":0.8,"curva":-0.15}])
mapa("c06","1396 Trégua",27.2,31.9,cam=[[27.2,48.6,2.0,0.252]],push=1.05,cy=430,
  ano="1396",ano_cor=BLU,sub="TRÉGUA",titulos=[[27.26,"A TRÉGUA DE 1396","TRÉGUA",CYA],[29.34,"PAUSA O CONFLITO","PAUSA",YEL]],
  areas=base(),lugares=[["INGLATERRA",52.6,-1.6,27.3,GR],["FRANÇA",47.2,2.6,27.3,GR]],
  icones=[ic("soldado","ing",51.3,-0.3,27.6,tam=1.3),ic("soldado","fra",48.4,2.6,27.6,tam=1.3)])
mapa("c07","1415 Azincourt",31.9,36.5,cam=[[31.9,50.40,2.05,1.45]],push=1.06,cy=400,
  ano="1415",ano_cor=RED,sub="AZINCOURT",titulos=[[32.18,"1415","",""],[32.78,"AZINCOURT","AZINCOURT",YEL],[33.74,"HENRIQUE V","HENRIQUE V",RED],[34.64,"MASSACRA A NOBREZA FRANCESA","NOBREZA",RED]],
  areas=base(),lugares=[["AZINCOURT",50.463,2.13,32.78]],
  icones=[ic("arqueiro","ing",50.56,1.92,32.4),ic("arqueiro","ing",50.50,1.82,32.5),ic("coroa","ing",50.64,1.80,33.74,tam=1.3,rotulo="HENRIQUE V",ly=-36)],
  enxame=[{"tipo":"cavaleiro","lado":"fra","de":[50.15,2.45],"para":[50.40,2.06],"t":33.0,"dur":1.7,"n":8,"stagger":0.1,"espalha":60,"gira":False,"ate":35.2},
          {"tipo":"flecha","de":[50.54,1.90],"para":[50.41,2.07],"t":34.3,"dur":0.6,"n":16,"stagger":0.04,"espalha":40,"some":True,"rastro":False}],
  explosoes=[{"lat":50.40,"lon":2.06,"t":34.8,"r":26,"fica":True},{"lat":50.36,"lon":2.12,"t":35.0,"r":22,"fica":True},{"lat":50.35,"lon":2.02,"t":35.2,"r":20,"fica":True}])
mapa("c08","Tratado de Troyes",36.5,42.0,cam=[[36.5,48.4,1.8,0.45]],push=1.05,cy=400,
  ano="TROYES",ano_cor=YEL,sub="TRATADO",titulos=[[36.6,"TRATADO DE TROYES","TROYES",YEL],[37.82,"ELE HERDA A FRANÇA","HERDA",RED],[39.12,"O DELFIM FOGE PARA O SUL","SUL",CYA]],
  areas=base()+[A("França herdada",[(0,NORTE)],t=37.82)],
  lugares=[["TROYES",48.30,4.08,36.7]],
  icones=[ic("coroa","ing",49.3,1.2,37.82,tam=1.4,rotulo="HENRIQUE V",ly=-36),ic("coroa","fra",47.95,2.7,39.4,ate=40.5,rotulo="CARLOS VII",ly=40),
          ic("coroa","fra",46.9,2.5,40.9,tam=1.3,rotulo="CARLOS VII",ly=42)],
  setas=[{"cor":"fra","de":[47.85,2.7],"para":[47.05,2.5],"t":40.38,"dur":0.7,"curva":0.1}])
mapa("c09","1429 Orléans e Reims",42.0,47.6,cam=[[42.0,47.85,1.9,1.1],[45.8,48.6,3.0,0.55,1.3]],push=1.03,cy=410,
  ano="1429",ano_cor=YEL,sub="ORLEÃES",titulos=[[42.18,"1429","",""],[43.32,"JOANA D'ARC","JOANA D'ARC",YEL],[44.24,"ERGUE O CERCO DE ORLEÃES","CERCO",RED],[45.8,"CARLOS É COROADO EM REIMS","REIMS",YEL]],
  areas=base()+[A("França herdada",[(0,NORTE)])],
  lugares=[["REIMS",49.26,4.03,46.4]],
  icones=[ic("castelo","fra",47.90,1.90,42.3,tam=1.2,rotulo="ORLEÃES",ly=-34),
          ic("soldado","ing",48.10,1.60,42.5,ate=45.0),ic("soldado","ing",47.72,1.62,42.6,ate=45.0),ic("soldado","ing",48.05,2.25,42.7,ate=45.0),
          ic("cavaleiro","fra",47.45,1.30,43.32,tam=1.2,rotulo="JOANA D'ARC",ly=42),ic("coroa","fra",49.26,4.03,46.6,tam=1.5)],
  setas=[{"cor":"fra","de":[47.50,1.38],"para":[47.82,1.80],"t":44.24,"dur":0.6,"curva":0.2},{"cor":"fra","de":[48.0,2.1],"para":[49.15,3.9],"t":45.9,"dur":1.0,"curva":-0.15}],
  explosoes=[{"lat":48.10,"lon":1.60,"t":44.7,"r":18},{"lat":47.72,"lon":1.62,"t":44.85,"r":18},{"lat":48.05,"lon":2.25,"t":45.0,"r":18}])
card("c10","Card fogueira",47.6,51.3,topo="JOANA D'ARC",topo_t=47.7,palavra="FOGUEIRA",palavra_t=48.4,pilulas=[[49.14,"MAS O ÍMPETO MUDA"]])
mapa("c11","1453 Castillon / Bordéus / Calais",51.3,59.1,cam=[[51.3,44.85,-0.06,1.4],[56.3,44.85,-0.5,1.05,0.8],[57.5,48.6,2.0,0.252,1.1]],push=1.0,cy=410,
  ano="1453",ano_cor=RED,sub="CASTILLON",titulos=[[51.44,"1453","",""],[52.56,"CASTILLON","CASTILLON",YEL],[53.18,"CANHÕES FRANCESES","CANHÕES",RED],[54.74,"VARREM O EXÉRCITO INGLÊS","INGLÊS",RED],[56.46,"BORDÉUS CAI","BORDÉUS",RED],[57.6,"CALAIS SOBRA","CALAIS",YEL]],
  areas=[A("Inglaterra",[(0,ENG)]),A("Aquitânia inglesa",[(0,PEQ)],ate=57.06),A("Calais",[(0,CAL)],pulsa=57.6)],
  lugares=[["CASTILLON",44.855,-0.04,52.56,0,56.3],["BORDÉUS",44.84,-0.58,56.46,0,57.5]],
  icones=[ic("soldado","ing",44.90,-0.20,51.6,ate=55.6),ic("soldado","ing",44.84,-0.23,51.7,ate=55.8),ic("soldado","ing",44.79,-0.19,51.8,ate=56.0),
          ic("canhao","fra",44.91,0.07,53.2),ic("canhao","fra",44.85,0.10,53.4),ic("canhao","fra",44.79,0.06,53.6),
          ic("castelo","ing",50.95,1.86,57.7,tam=1.1,rotulo="CALAIS",ly=-30)],
  enxame=[{"tipo":"blip","de":[44.85,0.06],"para":[44.85,-0.20],"t":54.5,"dur":0.6,"n":9,"stagger":0.1,"espalha":40,"some":True,"rastro":False}],
  explosoes=[{"lat":44.90,"lon":-0.20,"t":54.9,"r":24},{"lat":44.84,"lon":-0.23,"t":55.1,"r":24},{"lat":44.79,"lon":-0.19,"t":55.3,"r":24}])
mapa("c12","116 anos / França centralizada",59.1,63.0,cam=[[59.1,48.6,2.0,0.252]],push=1.05,cy=430,
  ano="116 ANOS",ano_cor=YEL,sub="DE GUERRA",titulos=[[59.22,"116 ANOS DE GUERRA","116 ANOS",YEL],[60.92,"A FRANÇA NASCE CENTRALIZADA","CENTRALIZADA",CYA]],
  areas=[A("Inglaterra",[(0,ENG)]),A("França",[(0,FR)],t=60.92,cor="#2a6fd6",op=0.4,frente="#9cc8ff"),A("Calais",[(0,CAL)])],
  lugares=[["INGLATERRA",52.6,-1.6,59.2,GR],["FRANÇA",47.2,2.6,61.0,GR]],
  icones=[ic("coroa","fra",48.6,2.4,61.68,tam=1.5)])
mapa("c13","Inglaterra / Guerra das Rosas",63.0,66.5,cam=[[63.0,52.4,-1.8,0.6]],push=1.06,cy=400,
  ano="INGLATERRA",ano_cor=RED,sub="GUERRA DAS ROSAS",titulos=[[63.1,"A INGLATERRA VIRA PARA DENTRO","PARA DENTRO",YEL],[64.88,"EXPLODE NA GUERRA DAS ROSAS","ROSAS",RED]],
  areas=[A("Inglaterra",[(0,ENG)],pulsa=64.88)],
  setas=[{"de":[51.0,1.6],"para":[51.8,0.0],"t":63.88,"dur":0.6,"curva":0.2},{"de":[50.3,-4.6],"para":[51.5,-2.9],"t":64.0,"dur":0.6,"curva":-0.2},{"de":[53.9,0.6],"para":[53.0,-0.8],"t":64.1,"dur":0.6,"curva":0.2}],
  explosoes=[{"lat":52.5,"lon":-1.3,"t":64.9,"r":26,"fica":True},{"lat":53.5,"lon":-1.8,"t":65.1,"r":22,"fica":True},{"lat":51.8,"lon":-2.4,"t":65.3,"r":22,"fica":True},{"lat":52.9,"lon":-0.4,"t":65.5,"r":20,"fica":True}],
  fumaca=[{"lat":52.5,"lon":-1.3,"t":65.2,"r":14},{"lat":53.5,"lon":-1.8,"t":65.4,"r":12}])
card("c14","Card pólvora",66.5,71.1,topo="PRÓXIMO VÍDEO",topo_t=69.64,palavra="PÓLVORA",palavra_t=67.6,sub="COMO A PÓLVORA MATOU A CAVALARIA",sub_t=68.42)
mapa("c15","CTA Constantinopla",71.1,75.3,cam=[[71.1,47.3,3.6,0.29]],push=1.05,cy=400,
  ano="A SEGUIR",ano_cor=BLU,sub="CONSTANTINOPLA",titulos=[[71.2,"INSCREVA-SE","INSCREVA-SE",RED],[72.78,"A QUEDA DE CONSTANTINOPLA","CONSTANTINOPLA",YEL]],
  areas=[A("Inglaterra",[(0,ENG)]),A("França",[(0,FR)],cor="#2a6fd6",op=0.4,frente="#9cc8ff"),A("Calais",[(0,CAL)])],
  cta={"t":71.2,"ate":72.7},
  setas=[{"de":[46.6,8.5],"para":[44.6,15.3],"t":72.9,"dur":1.0,"curva":-0.15}])
E={"version":1,"name":NOME,"estilo":"05-timeline-ano-a-ano","grupo":"ESTILOS NOVOS",
 "canvas":{"w":1280,"h":720,"fps":30,"bg":"#0d1a24"},"duration":75.3,"template":"local",
 "fonts":{"Oswald":"fonts/Oswald-Bold.ttf","Anton":"fonts/Anton-Regular.ttf"},
 "audio":{"voice":{"src":"voz.wav","volume":1.0,"start":0},"music":{"src":"musica.mp3","volume":0.10,"start":0,"fade_out":2.0,"duck":True}},
 "tracks":[{"id":"mapa","name":"Cenas de mapa (ano a ano)"},{"id":"cards","name":"Cards claros"}],
 "referencia":{"video":"https://youtu.be/o5GOQ9Bj0wg","canal":"Atlas Unfolded","titulo":"The Entire Ukraine War in 25 Minutes (Animated With Maps)","nota":"ver ESTILOS-NOVOS/05-timeline-ano-a-ano"},
 "creditos":"Relevo: AWS Terrain Tiles (terrarium; USGS/NOAA, domínio público). Costas/fronteiras: Natural Earth (domínio público). Territórios medievais desenhados à mão, aproximados.",
 "items":S}
json.dump(E,open("edit.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
tpl=open("tpl_base.html",encoding="utf-8").read().replace("__LAND__",LAND).replace("__META__",json.dumps(META))
open("template.html","w",encoding="utf-8").write(tpl)
print(len(S),"cenas; land",len(LAND)//1024,"KB")
