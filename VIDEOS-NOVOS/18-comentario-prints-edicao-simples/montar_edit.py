import json,os
O=os.path.dirname(os.path.abspath(__file__))
DUR=57.1
NAME="18 - COMENTARIO PRINTS EDICAO SIMPLES - Por que todo mundo está brigando sobre trabalho remoto"
items=[]
def sc(id,track,label,start,end,scene,params): items.append({"id":id,"type":"scene","track":track,"label":label,"start":round(start,2),"dur":round(end-start,2),"props":{"scene":scene,"params":params}})
def foto(id,src,a,b,mov="push",brilho=.8,amt=.07): sc(id,"fotos","foto "+src,a,b,"fern_plano",{"src":"img/"+src,"mov":mov,"amt":amt,"brilho":brilho,"nevoa":0.0,"tint":"rgba(0,0,0,.15)"})
def fr(id,label,a,b,linhas,pos="centro",scrim=False): sc(id,"cards",label,a,b,"cp_frase",{"pos":pos,"scrim":scrim,"linhas":[dict(l,t=round(l["t"]-a,2),destaques=[{"p":d["p"],"t":round(d["t"]-a,2)} for d in l.get("destaques",[])],**({"risca":round(l["risca"]-a,2)} if "risca" in l else {})) for l in linhas]})
sc("bg","fundo","fundo cidade à noite (desfocado)",0,DUR,"fern_plano",{"src":"img/fundo_cidade.jpg","mov":"push","amt":0.06,"brilho":0.9,"nevoa":0.0,"tint":"rgba(6,10,24,.25)"})
sc("topo","topo","título fixo + ponto n/5",0,47.75,"cp_topo",{"titulo":"A BRIGA DO HOME OFFICE","pontos":[0,7.75,16.4,28.2,39.0],"rotulos":["o real motivo","o print","é medo","o print 2","quem ganha"]})
# P1
foto("f1","homeoffice1.jpg",0,4.95)
fr("t1","real motivo: controle",0,4.95,[{"txt":"Ninguém fala do real motivo:","t":2.1,"cls":"apoio"},{"txt":"CONTROLE.","t":4.1,"cls":"grande","destaques":[{"p":"CONTROLE.","t":4.2}]}],pos="baixo",scrim=True)
foto("f2","homeoffice0.jpg",4.95,7.75,mov="pan_r")
fr("t2","não odeiam o sofá",4.95,7.75,[{"txt":"Chefes não odeiam o sofá…","t":5.0,"cls":"apoio"},{"txt":"odeiam não te ver.","t":6.55,"cls":"grande","destaques":[{"p":"não te ver.","t":7.05}]}],pos="baixo",scrim=True)
# P2 print 1
sc("p1","cards","print 1 + resposta",7.75,16.4,"cp_post",{"rotulo":"UM PRINT VIRALIZOU","nome":"Gestor Exemplo","handle":"@gestor_exemplo","data":"perfil fictício","texto":"Se não estou olhando, como sei que trabalha?","t_texto":1.3,"destaques":[{"p":"como sei que trabalha?","t":2.6}],
  "resposta":{"nome":"Dev Remoto","handle":"@dev_remoto","data":"perfil fictício","texto":"Pelo resultado entregue.","t":3.85,"destaques":[{"p":"resultado entregue.","t":5.75}]},"selo":"QUEBROU A INTERNET","t_selo":7.2})
# P3
fr("t3","não é preguiça, é medo",16.4,22.85,[{"txt":"Não é preguiça.","t":17.0,"cls":"grande","risca":17.6},{"txt":"É medo.","t":18.2,"cls":"grande","destaques":[{"p":"medo.","t":18.5}]},{"txt":"Medo de ficar obsoleto quem só sabe gerenciar presença.","t":19.1,"cls":"apoio","destaques":[{"p":"gerenciar presença.","t":21.4}]}])
sc("v1","cards","horas x entrega",22.85,28.2,"cp_versus",{"topo":"Empresas que medem…","esq":{"titulo":"HORAS","sub":"chamam de cultura","t":0.6,"ts":1.9},"dir":{"titulo":"ENTREGA","sub":"chamam de liberdade","t":3.3,"ts":4.8}})
# P4 print 2
foto("f3","mouse0.jpg",28.2,34.65,brilho=.45)
sc("p2","cards","print 2 (mouse)",28.2,34.65,"cp_post",{"rotulo":"O PRINT QUE CALOU A DISCUSSÃO","nome":"Analista Cansado","handle":"@analista_cansado","data":"perfil fictício","texto":"Meu chefe me monitora pelo mouse. Minha entrega dobrou, meu salário não.","t_texto":1.9,"tam":40,"destaques":[{"p":"me monitora pelo mouse.","t":2.9},{"p":"Minha entrega dobrou,","t":4.25},{"p":"meu salário não.","t":5.5}]})
fr("t4","virou teatro",34.65,39.0,[{"txt":"Se a métrica é o clique,","t":34.7,"cls":"apoio"},{"txt":"o trabalho virou teatro.","t":36.25,"cls":"grande","destaques":[{"p":"teatro.","t":37.0}]},{"txt":"E teatro cansa.","t":37.65,"cls":"apoio"}])
# P5
sc("v2","cards","confiança x segurança",39.0,43.45,"cp_versus",{"topo":"Por isso a briga esquenta","esq":{"titulo":"UM LADO QUER","sub":"confiança","t":1.5,"ts":2.25},"dir":{"titulo":"O OUTRO QUER","sub":"segurança","t":3.1,"ts":3.7}})
fr("t5","quem ganha",43.45,47.75,[{"txt":"Quem ganha?","t":43.5,"cls":"grande"},{"txt":"Quem aceitar que adulto não precisa de babá para produzir.","t":44.4,"cls":"apoio","destaques":[{"p":"não precisa de babá","t":45.9}]}])
# CTA
foto("f4","digitando0.jpg",47.75,52.0,brilho=.75)
sc("cta","cards","status verde + comenta eu",47.75,52.0,"cp_status",{"nome":"Você","t_status":2.5,"t_digit":1.0,"t_cta":3.4,"t_eu":3.9,"cta":"COMENTA “EU”"})
fr("fim","próximo vídeo",52.0,DUR,[{"txt":"No próximo vídeo","t":52.1,"cls":"rotulo"},{"txt":"Como negociar autonomia","t":53.5,"cls":"grande","destaques":[{"p":"autonomia","t":54.4}]},{"txt":"sem quebrar a cara.","t":55.1,"cls":"apoio"}])
wh=[7.65,16.3,28.1,38.9,47.65]
E={"version":1,"name":NAME,"estilo":"18-comentario-prints-edicao-simples","grupo":"ESTILOS NOVOS",
 "canvas":{"w":1280,"h":720,"fps":30,"bg":"#05070a"},"duration":DUR,"template":"generic",
 "fonts":{"Anton":"fonts/Anton-Regular.ttf"},
 "referencia":{"canal":"Nômade Digital Raiam","canal_url":"https://www.youtube.com/@nomadedigitalraiam","video":"https://youtu.be/69XnYWZCg8M","titulo":"ABOUT THE PROBLEM IN FRANCE","nota":"também Critical Latitude (39t1IhGejOQ) e Prosecutor Matthew Hanson; versão faceless: voz + prints genéricos + fundo fixo; ver ESTILOS-NOVOS/18-comentario-prints-edicao-simples/REFERENCIA.txt"},
 "audio":{"voice":{"src":"voz.wav","volume":1.0,"start":0},"extra":[{"id":f"wh{i}","src":"sfx/whoosh.wav","start":t,"volume":0.1,"label":"whoosh suave"} for i,t in enumerate(wh)]},
 "tracks":[{"id":"fundo","name":"Fundo cidade"},{"id":"fotos","name":"Fotos"},{"id":"cards","name":"Prints / frases"},{"id":"topo","name":"Título + progresso"}],
 "items":items}
json.dump(E,open(os.path.join(O,"edit.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
print(len(items))
