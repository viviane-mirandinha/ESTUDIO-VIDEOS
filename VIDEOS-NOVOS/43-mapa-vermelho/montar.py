import json,os
O=os.path.dirname(os.path.abspath(__file__))
items=[]
def S(id,a,b,scene,label,**params):
    items.append({"id":id,"type":"scene","track":"visual","by":"template","label":label,"start":a,"dur":round(b-a,2),"props":{"scene":scene,"params":params}})
def cam(id,t,alvo,zoom,trans=1.2,corte=False,**kw):
    S(id,t,t+max(trans,0.1),"camera","Câmera: %s x%s"%(alvo,zoom),alvo=alvo,zoom=zoom,transicao=trans,corte=corte,**kw)
def lab(id,a,b,texto,ponto,estilo="",dx=0,dy=0):
    S(id,a,b,"rotulo","Rótulo: "+texto,texto=texto,ponto=ponto,estilo=estilo,dx=dx,dy=dy)
def num(id,a,b,valor,legenda,fonte="",lado="esq"):
    S(id,a,b,"numero","Número: "+valor,valor=valor,legenda=legenda,fonte=fonte,lado=lado)
def pul(id,a,b,ponto,tam=1): S(id,a,b,"pulso","Pulso: "+ponto,ponto=ponto,tamanho=tam)
def lin(id,a,b,linha,cor="#ff2a36",**kw): S(id,a,b,"linha","Linha: "+linha,linha=linha,cor=cor,**kw)
def pai(id,a,b,cods,tempos=None,cor="#e3121b",fim="base"):
    S(id,a,b,"paises","Países: "+cods,codigos=cods,tempos=tempos or [a]*len(cods.split(",")),cor=cor,fim=fim)
END=66.2
S("hud",0,END,"hud","HUD alerta",alerta="ALERTA · ROTA CRÍTICA",coord="26°34'N · 56°15'E")
# 1) gancho: menos de 40 km
cam("c0",0,"hormuz",1.4,corte=True); cam("c1",0.35,"hormuz",110,trans=2.2)
num("n40",0.56,5.95,"< 40 KM","NO PONTO MAIS ESTREITO","≈ 39 km (21 milhas náuticas)")
lin("med1",2.6,10.8,"medida",cor="#ffffff",largura=4,seta=False,desenho=0.9)
pul("p1",2.7,6.2,"hormuz")
lab("l_orm",3.6,6.25,"ESTREITO DE ORMUZ","hormuz","box",dy=-110)
# 2) 20% do petróleo
cam("c2",6.3,"hormuz",36,trans=1.2)
num("n20",7.82,10.85,"20%","DO PETRÓLEO CONSUMIDO NO PLANETA","FONTE: EIA (2024)")
pul("p2",7.6,10.85,"hormuz",1.2)
# 3) Irã x Omã
cam("c3",10.9,"vista_io",15,trans=1.0)
pai("pa_io",12.0,15.1,"IRN,OMN",tempos=[12.0,13.9])
lab("l_irn",12.1,15.05,"IRÃ","iran","red")
lab("l_omn",13.95,15.05,"OMÃ","oman","red")
# 4) única saída do Golfo
cam("c4",15.1,"vista_golfo",20,trans=1.0)
lab("l_golfo",16.9,19.25,"GOLFO PÉRSICO","golfo","mar")
lin("saida",16.95,19.25,"saida",largura=5,desenho=1.3)
lab("l_oma",18.1,19.25,"GOLFO DE OMÃ","golfo_oma","mar")
# 5) exportadores
cam("c5",19.3,"vista_exp",10,trans=1.0)
pai("pa_exp",19.56,24.4,"SAU,IRQ,KWT,ARE,QAT",tempos=[19.56,20.76,21.42,22.14,22.84])
lab("l_sau",20.3,24.35,"ARÁBIA SAUDITA","sau","red")
lab("l_irq",20.76,24.35,"IRAQUE","irq","red")
lab("l_kwt",21.42,24.35,"KUWAIT","kwt","red",dx=40,dy=-34)
lab("l_are",22.14,24.35,"EMIRADOS","are","red",dy=10)
lab("l_qat",22.84,24.35,"CATAR","qat","red",dx=-90,dy=-6)
# 6) 1/5 do GNL
cam("c6",24.4,"qat",26,trans=1.0)
pai("pa_qat",24.5,30.35,"QAT",cor="#e3121b")
pul("p3",25.4,30.3,"qat")
num("n15",25.9,30.35,"1/5","DO GÁS NATURAL LIQUEFEITO NEGOCIADO NO MUNDO","FONTE: EIA (2024)",lado="dir")
# 7) faixas de navegação
cam("c7",30.4,"hormuz",130,trans=1.4)
pai("pa_io2",31.8,38.5,"IRN,OMN",cor="#7a0b12")
lin("fin",32.6,38.5,"faixa_in",cor="#ff2a36",largura=6,fluxo=True,seta=False)
lin("fout",32.9,38.5,"faixa_out",cor="#ffffff",largura=6,fluxo=True,seta=False)
lab("l_irn2",32.0,38.45,"IRÃ","iran_costa","red")
lab("l_omn2",32.3,38.45,"OMÃ","musandam","red",dx=-60)
num("n4",34.94,38.5,"< 4 KM","LARGURA DE CADA FAIXA DE NAVEGAÇÃO","2 milhas náuticas ≈ 3,7 km por sentido")
lab("l_in",36.5,38.45,"ENTRADA →","lane_in","box")
lab("l_out",37.1,38.45,"← SAÍDA","lane_out","box")
# 8) rotas alternativas
S("tt1",38.6,41.55,"titulo","Título: rotas alternativas",texto="ROTAS ALTERNATIVAS?",sub="POUCAS.",sub_em=1.9)
cam("c8",38.7,"vista_oleo",13,trans=1.6)
pai("pa_ol",42.1,48.1,"SAU,ARE",tempos=[42.1,43.06],cor="#7a0b12")
lin("ol_sau",42.12,48.1,"oleo_sau",cor="#ffffff",largura=5,desenho=1.4)
lin("ol_are",43.06,48.1,"oleo_are",cor="#ffffff",largura=5,desenho=0.9)
lab("l_ols",42.6,48.05,"OLEODUTO SAUDITA","oleo_sau_lab","box",dy=-44)
lab("l_ola",43.5,48.05,"OLEODUTO DOS EMIRADOS","oleo_are_lab","box",dx=-30,dy=70)
num("n_ins",45.44,48.1,"INSUFICIENTE","PARA DESVIAR TODO O VOLUME","FONTE: EIA")
# 9) Ásia
cam("c9",48.2,"vista_asia",3.2,trans=1.6)
for i,r in enumerate(["r_india","r_china","r_japao","r_coreia"]):
    lin(r,49.0+i*0.25,57.4,r,largura=4,desenho=1.8,seta_px=18)
num("n84",48.76,52.85,"84%","DO PETRÓLEO BRUTO QUE CRUZA ORMUZ VAI PARA A ÁSIA","FONTE: EIA (2024)")
pai("pa_as",50.6,57.45,"CHN,IND,JPN,KOR",cor="#7a0b12")
lab("l_asia",51.2,52.85,"ÁSIA","asia","red")
pul("p4",52.9,57.4,"hormuz",1.3)
lab("l_ten",52.95,57.4,"TENSÃO AQUI","hormuz","box",dy=-70)
lab("l_pre",54.6,57.4,"PREÇO DO COMBUSTÍVEL","japao","box",dx=-60,dy=-60)
# 10) fecho
S("fl1",57.6,57.9,"flash","Flash vermelho",forca=0.45)
cam("c10",57.6,"hormuz",110,trans=1.0)
pai("pa_fim",57.7,62.2,"IRN,OMN",cor="#7a0b12",fim="manter")
lin("med2",58.4,62.2,"medida",cor="#ffffff",largura=4,seta=False,desenho=0.8)
pul("p5",58.3,62.2,"hormuz",1.2)
num("n40b",58.12,62.2,"< 40 KM","E O MUNDO INTEIRO DE OLHO")
S("cta",62.2,END,"cta","CTA inscreva-se",texto="INSCREVA-SE",sub="MAIS MAPAS QUE EXPLICAM O MUNDO")
extra=[{"id":"w%d"%i,"src":"sfx/whoosh.wav","start":t,"volume":0.35,"label":"whoosh"} for i,t in enumerate([0.3,15.05,30.35,38.6,48.15,57.55])]
name="43 - MAPA VERMELHO - Por que o Estreito de Ormuz assusta o mundo"
E={"version":1,"name":name,"estilo":"43-mapa-vermelho","grupo":"ESTILOS NOVOS",
 "referencia":{"canal":"Ticket To Know","canal_url":"https://www.youtube.com/@TicketToKnow","video":"https://www.youtube.com/watch?v=udtVdDmSSoo","titulo":"The Strait of Hormuz Explained",
   "canal_2":"Himfact","video_2":"https://www.youtube.com/watch?v=4vRtXY-iFnc","titulo_2":"Why is the Red Sea so Important?",
   "nota":"estrutura clonada: zoom no estreito, rótulos no mapa, rotas/setas, país destacado em bloco de cor, número gigante; paleta levada ao gênero mapa vermelho (fundo escuro, vermelho alerta)"},
 "canvas":{"w":1280,"h":720,"fps":30,"bg":"#05070a"},"duration":END,"template":"local",
 "fonts":{"Inter":"fonts/Inter.ttf","Anton":"fonts/Anton-Regular.ttf"},
 "audio":{"voice":{"src":"voz.mp3","volume":1.0,"start":0},"music":{"src":"musica.mp3","volume":0.22,"start":0,"fade_out":2.0,"duck":True},"extra":extra},
 "tracks":[{"id":"visual","name":"Mapa / cenas"},{"id":"textos","name":"Textos"}],
 "items":items+[{"id":"cor_destaque","type":"param","label":"Cor de destaque","props":{"value":"#e3121b"}},
                {"id":"cor_terra","type":"param","label":"Cor da terra","props":{"value":"#1e222a"}}]}
json.dump(E,open(os.path.join(O,"edit.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
src=open(os.path.join(O,"template_src.html"),encoding="utf-8").read()
open(os.path.join(O,"template.html"),"w",encoding="utf-8").write(src.replace("__MAP__",open(os.path.join(O,"map_data.json"),encoding="utf-8").read()))
print("items",len(items))
