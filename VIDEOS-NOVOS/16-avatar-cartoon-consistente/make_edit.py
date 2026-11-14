import json
NAME="16 - AVATAR CARTOON CONSISTENTE - E se você dobrasse de tamanho a cada hora"
DUR=58.7
S=[ # id, scene, start, end, label, params
("s01","quarto",0,3.1,"Acorda normal 1,70 m",{"regua":"1,70 m","t_acorda":0.9,"t_regua":1.6}),
("s02","quarteirao",3.1,6.1,"Não cabe no quarteirão",{"rotulo":"DAQUI A 5 HORAS...","sub":"VOCÊ NÃO CABE NO QUARTEIRÃO","t_sub":1.7}),
("s03","cresce_quarto",6.1,8.9,"Hora 1: cresce no quarto",{"regua":"3,40 m","t_cresce":1.3,"t_regua":1.4}),
("s04","escombros",8.9,12.8,"Cama, teto, vizinhos",{"rotulo":"SUA CAMA VIRA ESCOMBROS","grito":"AAAH!","t_cama":0.4,"t_teto":1.75,"t_viz":2.75}),
("s05","cresce_casa",12.8,15.5,"Hora 2: do tamanho da casa",{"t_cresce":1.3}),
("s06","cafe",15.5,18.6,"Café numa colherada",{"rotulo":"O CAFÉ DA MANHÃ NUMA COLHERADA","t_pega":0.98,"t_come":2.26,"t_rot":1.4}),
("s07","cano",18.6,21.0,"Encanamento explode, rua alaga",{"rotulo":"O ENCANAMENTO EXPLODE","t_cano":0.74,"t_alaga":1.4}),
("s08","cresce_rua",21.0,23.7,"Hora 3: maior que as casas",{"t_cresce":1.1}),
("s09","carros",23.7,25.75,"Carros viram brinquedos",{"rotulo":"CARROS VIRAM BRINQUEDOS","t_rot":0.1,"t_brinq":0.55}),
("s10","policia",25.75,29.75,"Polícia atira, balas ricocheteiam",{"rotulo":"AS BALAS RICOCHETEIAM","t_tiro":0.65,"t_rot":1.85}),
("s11","cresce_cidade",29.75,32.1,"Hora 4: gigante na cidade",{"de":0.9,"para":1.4,"x0":420,"x1":640,"t_cresce":1.1}),
("s12","senta",32.1,34.45,"Senta e achata 3 quarteirões",{"rotulo":"3 QUARTEIRÕES ACHATADOS","t_senta":0.32,"t_rot":1.18}),
("s13","rarefeito",34.45,38.0,"Ar rarefeito, voz de trovão",{"rotulo":"AR RAREFEITO","sub":"SUA VOZ VIRA TROVÃO","t_ar":0.7,"t_trovao":2.3}),
("s14","cresce_cidade",38.0,40.6,"Hora 5: acima dos prédios",{"alto":1,"de":0.75,"para":1.25,"emo":"cansado","x0":500,"x1":700,"t_cresce":1.3}),
("s15","coracao",40.6,44.4,"Coração do tamanho de um carro",{"rotulo":"CORAÇÃO DO TAMANHO DE UM CARRO","sub":"NÃO BATE RÁPIDO O SUFICIENTE","t_rot":0.3,"t_lento":1.86}),
("s16","desmaio",44.4,47.1,"Desmaia e derruba prédios",{"rotulo":"VOCÊ DESMAIA","t_tonto":0.4,"t_cai":1.16}),
("s17","gravidade",47.1,49.3,"A gravidade não perdoa escala",{"t1":"A GRAVIDADE","t2":"NÃO PERDOA ESCALA","t_1":0.28,"t_2":1.06}),
("s18","atomo",49.3,55.1,"Encolhe até virar átomo + vídeo ao lado",{"rotulo":"ENCOLHER ATÉ VIRAR ÁTOMO","card_tag":"O VÍDEO AO LADO","card_titulo":"E SE VOCÊ ENCOLHESSE?","t_encolhe":2.1,"t_atomo":3.12,"t_video":3.86}),
("s19","inscreva",55.1,DUR,"Inscreva-se",{"regua":"1,70 m","botao":"INSCREVA-SE","rotulo":"E NUNCA MAIS RECLAME DE SER BAIXO","t_btn":0.06,"t_rot":1.48}),
]
H=[("h0",1.64,6.86,"AGORA","1,70 m"),("h1",6.86,13.7,"HORA 1","3,40 m"),("h2",13.7,21.96,"HORA 2","6,80 m"),
   ("h3",21.96,30.72,"HORA 3","13,60 m"),("h4",30.72,39.3,"HORA 4","27 m"),("h5",39.3,47.1,"HORA 5","54 m")]
C=[("c1",6.12,1.3,"HORA 1","3,40 m",0.74),("c2",12.82,1.3,"HORA 2","6,80 m",0.88),("c3",21.02,1.25,"HORA 3","13,60 m",0.94),
   ("c4",29.77,1.2,"HORA 4","27 METROS",0.95),("c5",38.02,1.4,"HORA 5","54 METROS",1.28)]
items=[{"id":i,"type":"scene","track":"fundo","label":lab,"start":a,"dur":round(b-a,2),"by":"template","props":{"scene":sc,"params":p}} for i,sc,a,b,lab,p in S]
items+=[{"id":i,"type":"scene","track":"hud","label":f"HUD {h} {al}","start":a,"dur":round(b-a,2),"by":"template","props":{"scene":"hud","params":{"hora":h,"altura":al}}} for i,a,b,h,al in H]
items+=[{"id":i,"type":"scene","track":"cards","label":f"Cartão {t}","start":a,"dur":d,"by":"template","props":{"scene":"card","params":{"texto":t,"sub":s,"t_sub":ts}}} for i,a,d,t,s,ts in C]
E={"version":1,"name":NAME,"estilo":"16-avatar-cartoon-consistente","grupo":"ESTILOS NOVOS",
 "canvas":{"w":1280,"h":720,"fps":30,"bg":"#000000"},"duration":DUR,"template":"local",
 "referencia":{"canal":"One Small If","canal_url":"https://www.youtube.com/@onesmallif","video":"https://youtu.be/KzdIyAqm15c","titulo":"What If You Doubled in Size Every Hour?",
  "nota":"1 avatar fixo (cabeça preta redonda, moletom verde) em cenários suburbanos; HUD fixo hora/altura; cortes 2-4 s; letterbox. Avatar = rig SVG único (avatar.js / img/avatar-mestre.svg)"},
 "audio":{"voice":{"src":"voz.wav","volume":1.0,"start":0}},
 "tracks":[{"id":"fundo","name":"Cenas avatar"},{"id":"cards","name":"Cartões HORA"},{"id":"hud","name":"HUD hora/altura"}],"items":items}
json.dump(E,open("edit.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
src=open("template_src.html",encoding="utf-8").read().replace("%%AVATAR%%",open("avatar.js",encoding="utf-8").read())
open("template.html","w",encoding="utf-8").write(src)
print(len(items))
