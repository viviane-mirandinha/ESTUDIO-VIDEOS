import json,os,shutil
O=os.path.dirname(os.path.abspath(__file__))
IMG={"sp":"sp1.jpg","campinas":"campinas0.jpg","guarulhos":"gy2.jpg","sorocaba":"sy1.jpg","ribeirao":"rx0.jpg","sjc":"sjc0.jpg","transito":"tx0.jpg","rodovia":"bandeirantes1.jpg","fim":"sp2.jpg"}
os.makedirs(os.path.join(O,"img"),exist_ok=True)
for k,v in IMG.items():
    src=os.path.join(O,"cand",v)
    if os.path.exists(src): shutil.copy2(src,os.path.join(O,"img",k+".jpg"))
DARK="rgba(17,19,24,.88)"; GOLD="#f2b632"
items=[]
def T(id,a,b,text,x=640,y=600,size=56,w=1100,color="#ffffff",bg=DARK,inn="slide_up",**kw):
    p={"text":text,"x":x,"y":y,"w":w,"size":size,"color":color,"font":"Inter","weight":800,"align":"center","bg":bg,"pad":16,"radius":6,"shadow":True}; p.update(kw)
    items.append({"id":id,"type":"text","track":"textos","label":text[:28],"start":a,"dur":round(b-a,2),"in":inn,"out":"fade","props":p})
def I(id,a,b,src,fill=True,motion="zoom_in",**kw):
    p={"src":"img/"+src+".jpg","fit":"cover","motion":motion,"motion_amount":0.08}
    if fill: p.update({"fill":True,"x":640,"y":360,"w":1280,"h":720})
    p.update(kw); items.append({"id":id,"type":"image","track":"fundo" if fill else "visual","label":src,"start":a,"dur":round(b-a,2),"in":"fade","out":"fade","props":p})
def S(id,a,b,scene,label,**params):
    items.append({"id":id,"type":"scene","track":"visual","by":"template","label":label,"start":a,"dur":round(b-a,2),"props":{"scene":scene,"params":params}})
def inset(id,a,b,src,cap):
    I(id,a,b,src,fill=False,x=1005,y=300,w=440,h=280,radius=8)
    T(id+"_c",a+.2,b,cap,x=1005,y=475,size=26,w=440,inn="fade",bg="#111318",pad=10)
# abertura
I("img_sp",0,3.9,"sp")
T("t_titulo",0.3,3.7,"SÃO PAULO PAROU NO TEMPO",y=560,size=64)
T("t_censo",1.6,7.4,"CENSO 2022",x=150,y=64,size=34,w=240,color="#111318",bg=GOLD,inn="fade")
# mapa
S("mapa",3.8,52.4,"mapa","Mapa SP (base)",oceano="OCEANO ATLÂNTICO")
S("cam_est0",3.8,0.5+3.8,"camera","Câmera: estado",alvo="estado",zoom=1,corte=True)
S("cam_cap",4.3,7.4,"camera","Câmera: capital",alvo="São Paulo",zoom=4,foco_x=640,foco_y=360,rotulo="SÃO PAULO · CAPITAL")
S("n_cap",4.9,7.4,"numero","11,45 milhões",valor="11,45 MILHÕES",legenda="DE PESSOAS NA CAPITAL")
S("dc1",7.4,13.0,"card-dado","Card 1,8%",titulo="CAPITAL: CRESCIMENTO DESDE 2010",valor=1.8,sub="O MENOR RITMO DA HISTÓRIA",sub_em=3.9,fonte="FONTE: CENSO 2022")
S("cap1",13.0,15.2,"capitulo","Capítulo 1",kicker="CAPÍTULO 1",titulo="O INTERIOR ACELERA")
C=[("camp","Campinas",15.2,17.8,16.2,[("1,14 MILHÃO","HABITANTES",16.2,17.8)],"campinas","CAMPINAS (SP)"),
   ("guar","Guarulhos",17.8,20.3,18.5,[("1,29 MILHÃO","HABITANTES",18.5,20.3)],"guarulhos","GUARULHOS · AEROPORTO"),
   ("soro","Sorocaba",20.3,25.6,21.6,[("+24%","SALTO DA POPULAÇÃO",21.6,23.5),("723 MIL","HABITANTES",23.5,25.6)],"sorocaba","SOROCABA (SP)"),
   ("rib","Ribeirão Preto",25.6,28.2,26.6,[("698 MIL","HABITANTES",26.6,28.2)],"ribeirao","RIBEIRÃO PRETO (SP)"),
   ("sjc","São José dos Campos",28.2,31.5,29.7,[("697 MIL","HABITANTES",29.7,31.5)],"sjc","S. JOSÉ DOS CAMPOS (SP)")]
for k,nome,a,b,_,nums,img,cap in C:
    S("cam_"+k,a,b,"camera","Câmera: "+nome,alvo=nome,zoom=3.2,foco_x=430,foco_y=390,transicao=1.0,rotulo=nome.upper())
    for j,(v,l,na,nb) in enumerate(nums): S(f"n_{k}{j}",na,nb,"numero",v,valor=v,legenda=l)
    inset("img_"+k,a+.4,b,img,cap)
S("dc2",31.5,35.7,"card-comparacao","Card 2 a 3x",titulo="CRESCIMENTO: CIDADES MÉDIAS × CAPITAL",rot_a="CAPITAL",rot_b="CIDADES MÉDIAS",b_min=2,b_max=3,unidade=300,valor="2 A 3 VEZES MAIS RÁPIDO",valor_em=1.6)
S("cam_est",35.0,42.2,"camera","Câmera: estado inteiro",alvo="estado",zoom=1,corte=True)
S("mun",36.6,42.4,"municipios","645 municípios coloridos",duracao=1.6)
S("n_645",36.7,39.2,"numero","645 municípios",valor="645",legenda="MUNICÍPIOS NO ESTADO")
S("pib",39.2,42.4,"pib","Card PIB 2/3",valor="2/3",texto="DO PIB PAULISTA ESTÁ NO INTERIOR",legenda="CERCA DE DOIS TERÇOS",fracao=0.667)
S("cam_reg",42.2,52.4,"camera","Câmera: região",alvo="regiao",zoom=2,foco_x=640,foco_y=390,transicao=1.0)
S("setas",42.6,44.8,"setas","Setas capital → interior",origem="São Paulo",destinos=["Campinas","Sorocaba","Ribeirão Preto","São José dos Campos","Guarulhos"])
T("t_mig",42.6,44.8,"A RIQUEZA MIGROU. A POPULAÇÃO SEGUIU.",y=70,size=48,inn="fade")
I("img_tran",44.75,48.75,"transito",motion="pan_left")
T("t_custo",45.8,48.6,"O CUSTO SOBE. A VAGA SOME.",y=600,size=58)
I("img_rod",48.7,52.5,"rodovia",motion="zoom_in")
T("t_rod",49.0,52.3,"RODOVIA DOS BANDEIRANTES",x=290,y=64,size=34,w=520,color="#111318",bg=GOLD,inn="fade")
T("t_inf",49.6,52.3,"O DINHEIRO CIRCULA E A INFRAESTRUTURA ACOMPANHA",y=590,size=48,w=1000)
S("brasil",52.4,55.95,"brasil","Mapa Brasil (CTA)",destaque="35")
T("t_cta1",52.5,55.8,"CURTIU O DADO?",x=930,y=250,size=58,w=560,bg="",inn="fade")
T("t_cta2",53.8,55.8,"INSCREVA-SE",x=930,y=360,size=52,w=420,bg="#d7263d",radius=10,pad=18,inn="pop")
T("t_cta3",54.5,55.8,"MAIS MAPAS DO BRASIL",x=930,y=465,size=34,w=560,color=GOLD,bg="",inn="fade")
I("img_fim",55.9,63.72,"fim",motion="zoom_in",motion_amount=0.12)
T("t_fim1",56.3,60.4,"ATÉ QUANDO A CAPITAL SERÁ O “MOTOR DO PAÍS”?",y=580,size=50,w=1100)
T("t_fim2",60.5,63.6,"SE O MOTOR REAL JÁ MUDOU DE ENDEREÇO?",y=580,size=54,w=1100,color=GOLD)
name="25 - DOC REGIONAL MAPAS DADOS - Por que o interior de São Paulo cresce mais que a capital"
E={"version":1,"name":name,"estilo":"25-doc-local-mapas-dados","grupo":"ESTILOS NOVOS",
 "referencia":{"canal":"Alabama Revealed","canal_url":"https://www.youtube.com/@AlabamaRevealed","video":"https://youtu.be/nwNsT8QG0AE","titulo":"How Alabama Is Slowly Turning Into America's Next Mega-State","nota":"mapa claro com municípios + cards de dado pretos + fotos; capítulo azul-marinho (America Under Construction)"},
 "canvas":{"w":1280,"h":720,"fps":30,"bg":"#bcd7e0"},"duration":63.72,"template":"local","fonts":{"Inter":"fonts/Inter.ttf"},
 "audio":{"voice":{"src":"voz.mp3","volume":1.0,"start":0},"music":{"src":"musica.mp3","volume":0.08,"start":0,"fade_out":2.0,"duck":True},"extra":[]},
 "tracks":[{"id":"fundo","name":"Fotos"},{"id":"visual","name":"Mapa / cards"},{"id":"textos","name":"Textos"}],"items":items}
json.dump(E,open(os.path.join(O,"edit.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
src=open(os.path.join(O,"template_src.html"),encoding="utf-8").read()
open(os.path.join(O,"template.html"),"w",encoding="utf-8").write(src.replace("__MAP__",open(os.path.join(O,"map_data.json"),encoding="utf-8").read()))
print("items",len(items))
