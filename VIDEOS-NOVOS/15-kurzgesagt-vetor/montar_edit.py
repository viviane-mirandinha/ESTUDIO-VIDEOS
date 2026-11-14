import json
S=[("queda","Você cai num buraco negro",0,{}),
("gravidade","Gravidade: pés x cabeça",1.5,{"pes":"PÉS","cabeca":"CABEÇA","titulo":"MILHÕES DE VEZES","t_pes":1.32,"t_cab":3.84,"t_mil":2.0}),
("espaguete","Espaguetificação",6.05,{"fio":"FIO DE ÁTOMOS","titulo":"ESPAGUETIFICAÇÃO","t_fio":2.53,"t_esp":3.49}),
("observa","Quem observa de fora",10.85,{"modo":"fora","l1":"DE FORA","l2":"HORIZONTE","t_l1":.55,"t_l2":2.85}),
("observa","Luz vermelha e lenta",14.35,{"modo":"luz","l1":"MAIS VERMELHA","l3":"E MAIS LENTA","l2":"CONGELA NA BORDA","t_l1":2.35,"t_l2":3.03,"t_l3":3.57}),
("estatica","Imagem estática desbotando",19.05,{"l1":"IMAGEM ESTÁTICA","l2":"PARA SEMPRE","t_l1":.97,"t_l2":2.71}),
("pov","Na sua visão nada muda",22.55,{"l1":"NA SUA VISÃO","l2":"NADA MUDA","hor":"HORIZONTE","t_l1":.55,"t_l2":1.47,"t_trav":2.87}),
("tempo","Espaço vira tempo / futuro",26.05,{"esp":"ESPAÇO","tem":"TEMPO","fut":"SEU FUTURO","t_tem":1.13,"t_cen":1.95,"t_fut":4.09}),
("singular","Singularidade = fim do relógio",31.3,{"titulo":"SINGULARIDADE","l1":"NÃO É UM PONTO","l2":"FIM DO SEU RELÓGIO","t_nao":1.16,"t_fim":2.68}),
("super","Supermassivo: passa inteiro",35.5,{"titulo":"SUPERMASSIVO","l2":"INTEIRO","t_sup":1.16,"t_int":3.08}),
("acelera","Universo acelera até o fim",39.05,{"l1":"SEGUNDOS|OU HORAS","l2":"FIM DOS TEMPOS","t_seg":.47,"t_fim":3.81}),
("para","A física para",43.8,{"titulo":"A FÍSICA PARA","t_fis":.64}),
("curta","CTA curtir",45.5,{"titulo":"CURTA O VÍDEO"}),
("falha","A teoria falha",47.85,{"titulo":"A TEORIA FALHA","sing":"SINGULARIDADE","t_fal":.75,"t_sin":1.31}),
("rgmq","Relatividade x Quântica",50.15,{"rg":"RELATIVIDADE|GERAL","dens":"DENSIDADE INFINITA","mq":"MECÂNICA|QUÂNTICA","proibe":"PROÍBE","t_inf":1.99,"t_mq":3.25,"t_pro":4.57}),
("teoria","Teoria que ainda não existe",55.25,{"titulo":"UMA TEORIA QUE|AINDA NÃO EXISTE","t_teo":1.73}),
("inscreva","CTA inscreva-se",58.75,{"botao":"INSCREVA-SE"})]
DUR=63.2
items=[]
for k,(sc,lb,st,p) in enumerate(S):
    en=S[k+1][2] if k+1<len(S) else DUR
    items.append({"id":f"s{k+1:02d}","type":"scene","track":"fundo","label":lb,"start":st,"dur":round(en-st,2),"by":"template","props":{"scene":sc,"params":p}})
E={"version":1,"name":"15 - KURZGESAGT VETOR - O que aconteceria se você caísse num buraco negro",
"estilo":"15-kurzgesagt-vetor","grupo":"ESTILOS NOVOS","canvas":{"w":1280,"h":720,"fps":30,"bg":"#120a2e"},"duration":DUR,"template":"local",
"referencia":{"canal":"Kurzgesagt – In a Nutshell","canal_url":"https://www.youtube.com/@kurzgesagt","video":"https://youtu.be/ujkD4SxPKOI","titulo":"AI Just Crossed the Terrifying Line - Now What?","nota":"vetor flat denso, fundo escuro saturado, atores com olhinhos, câmera em zoom contínuo; personagens/marca próprios (astronauta), sem passarinho"},
"audio":{"voice":{"src":"voz.wav","volume":1.0,"start":0},"music":{"src":"musica.mp3","volume":0.1,"start":0,"fade_out":2.0,"duck":True}},
"tracks":[{"id":"fundo","name":"Cenas vetor"},{"id":"textos","name":"Textos"}],"items":items}
json.dump(E,open("edit.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print(len(items))
