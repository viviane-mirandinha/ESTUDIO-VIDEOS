import json
NAME="19 - PSICOLOGIA FLAT ILUSTRADA - 3 sinais de que um homem nunca implora por amor"
DUR=48.17
S=[ # id, scene, start, end, label, params
("s01","celular",0,3.48,"Celular: ele não implora",{"t_guarda":1.86}),
("s02","espelho",3.48,5.12,"Espelho: autoconhecimento",{"t_ideia":0.5}),
("s03","sinal",5.12,7.88,"SINAL 1",{"n":"1","rotulo":"AUSÊNCIA DE NEGOCIAÇÃO","icone":"escudo","pose":"cruz","t_rot":0.9}),
("s04","balanca",7.88,10.36,"Dignidade x presença",{"esq":"DIGNIDADE","dir":"PRESENÇA","t_nao":0.28,"t_pesa":0.84}),
("s05","diminui",10.36,13.46,"Se exige que diminua, ele sai",{"t_diminui":1.7,"t_sai":2.4}),
("s06","sinal",13.46,15.98,"SINAL 2",{"n":"2","rotulo":"VALIDAÇÃO INTERNA","icone":"coracao","pose":"peito","t_rot":1.3}),
("s07","amo",15.98,19.82,"Eu te amo / próprio valor",{"balao":"EU TE AMO","t_balao":1.7,"t_valor":3.0}),
("s08","dentro",19.82,23.26,"Segurança nasce de dentro",{"t_dentro":1.02,"t_reflexo":2.3}),
("s09","sinal",23.26,26.48,"SINAL 3",{"n":"3","rotulo":"CLAREZA SOBRE RECIPROCIDADE","icone":"setas","pose":"aberto","t_rot":1.4}),
("s10","maodupla",26.48,31.96,"Via de mão dupla / fluxo para",{"rotulo":"VIA DE MÃO DUPLA","t_rot":1.5,"t_para":3.22,"t_nao":4.0}),
("s11","persegue",31.96,36.62,"Perseguir quem foge = falta de limites",{"rotulo":"FALTA DE LIMITES","t_corre":0.88,"t_rom":2.34,"t_lim":3.24}),
("s12","inscreva",36.62,39.16,"Inscreva-se",{"botao":"INSCREVA-SE"}),
("s13","frase",39.16,42.2,"Cartão-frase: ele atrai",{"l1":"UM HOMEM QUE SE BASTA","l2":"NÃO CORRE ATRÁS,","l3":"ELE ATRAI.","destaque":"ATRAI","t2":1.1,"t3":2.34}),
("s14","eunos",42.2,DUR,"Onde termina o nós e começa o eu",{"t_circ":1.92,"t_nos":3.7,"t_eu":4.46}),
]
items=[{"id":i,"type":"scene","track":"fundo","label":lab,"start":a,"dur":round(b-a,2),"by":"template","props":{"scene":sc,"params":p}} for i,sc,a,b,lab,p in S]
KW=["amor","orgulho","autoconhecimento","primeiro","negociação","dignidade","diminua","segundo","interna","valor","dentro","terceiro","reciprocidade","dupla","vazio","limites","psicologia","basta","atrai","segredo","nós"]
cap=dict(words_file="legenda.json",per_group=3,x=640,y=655,size=48,color="#ffffff",dim="#ffffff",hl_color="#d8232a",keywords=KW,font="Poppins",weight=800,stroke="#2e2a26",stroke_w=7,shadow=False)
items+=[{"id":"leg1","type":"caption","track":"legenda","label":"Legenda 1","start":0,"dur":39.16,"props":cap},
        {"id":"leg2","type":"caption","track":"legenda","label":"Legenda 2","start":42.2,"dur":round(DUR-42.2,2),"props":cap}]
E={"version":1,"name":NAME,"estilo":"19-psicologia-flat-ilustrada","grupo":"ESTILOS NOVOS",
 "canvas":{"w":1280,"h":720,"fps":30,"bg":"#f3ede4"},"duration":DUR,"template":"local",
 "referencia":{"canal":"People Patterns Psych","canal_url":"https://www.youtube.com/@PeoplePatternsPsych","video":"https://youtu.be/wEN2CfbDWwo","titulo":"The Psychology of Men Who Never Beg For Love",
  "nota":"Fundo creme + vinheta, ilustração flat pastel de traço fino, número gigante azul-marinho + personagem, cartão-frase em papel quadriculado, palitos para metáforas, legenda palavra a palavra com palavra-chave vermelha. Elenco = rig SVG único (rig.js: LEO, ANA, PALITO)."},
 "audio":{"voice":{"src":"voz.wav","volume":1.0,"start":0}},
 "tracks":[{"id":"fundo","name":"Cenas ilustradas"},{"id":"legenda","name":"Legenda"}],"items":items}
json.dump(E,open("edit.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
src=open("template_src.html",encoding="utf-8").read().replace("%%RIG%%",open("rig.js",encoding="utf-8").read())
open("template.html","w",encoding="utf-8").write(src)
print(len(items))
