import json
NAME="07 - CARTOON PAISES PERSONAGENS - Por que a França vive em greve"
DUR=70.4
S=[ # id, scene, start, end, label, params
("s01","abre",0,3.0,"França dormindo / preguiça?",{"rotulo":"PREGUIÇA?","t_x":2.0}),
("s02","sistema",3.0,5.35,"O sistema permite",{"placa":"GREVE!","rotulo":"O SISTEMA PERMITE","ok":"PERMITE","t_sis":0.86,"t_ok":1.3}),
("s03","mapa",5.35,7.3,"Mapa: França x outros países",{"rotulo":"França","sub":"outros países","t_sub":0.75}),
("s04","categoria",7.3,12.05,"Sindicato negocia pela categoria",{"sindicato":"SINDICATO","rotulo":"TODA A CATEGORIA","sub":"não só os filiados","t_todos":2.06,"t_fil":3.06}),
("s05","fogo",12.05,15.5,"Poder de fogo, poucos membros",{"rotulo":"PODER DE FOGO","sub":"poucos membros","t_fogo":0.95,"t_poucos":2.17}),
("s06","gatilho",15.5,20.45,"Gatilho: artigo 49.3",{"rotulo":"O GATILHO?","botao":"49.3","livro":"CONSTITUIÇÃO","livro2":"DA FRANÇA","artigo":"ARTIGO 49.3","sub":"da Constituição","t_livro":1.18,"t_art":1.44,"t_const":3.84}),
("s07","governo",20.45,23.85,"Governo aprova sem votação",{"governo":"GOVERNO","lei":"LEI","carimbo":"APROVADA","botao":"49.3","rotulo":"SEM VOTAÇÃO","t_aperta":0.99,"t_carimbo":1.45,"t_sem":1.79,"t_parl":2.73}),
("s08","foto",23.85,27.55,"Foto: protesto reforma 2023",{"src":"img/reforma.jpg","rotulo":"REFORMA DA PREVIDÊNCIA","destaque":"2023","t_rot":0.4,"t_dest":2.11,"dx":1040,"dy":560,"personagem":1,"lado":"esq","emo":"raiva","pose":"point"}),
("s09","idade",27.55,33.65,"Idade mínima 62 -> 64",{"rotulo":"idade mínima","faixa":"APOSENTADORIA","de":"62","para":"64","t_rot":1.53,"t_de":2.53,"t_para":4.01}),
("s10","foto",33.65,37.15,"Foto: lixo em Paris",{"src":"img/lixo.jpg","rotulo":"LIXO NAS RUAS POR SEMANAS","destaque":"Paris","dfont":"PM","dcor":"#e5262a","dtam":96,"dx":330,"dy":560,"t_rot":1.03,"t_dest":2.07,"personagem":1,"lado":"dir","emo":"nojo","pose":"nariz"}),
("s11","trem",37.15,38.4,"Trens parados (cartoon)",{"rotulo":"TRENS PARADOS","placa":"GREVE"}),
("s12","foto",38.4,40.15,"Foto: refinarias bloqueadas",{"src":"img/refinaria.jpg","rotulo":"REFINARIAS BLOQUEADAS","t_rot":0.1,"barreira":1,"multidao":6}),
("s13","segredo",40.15,42.3,"O detalhe que ninguém conta",{"rotulo":"o detalhe que ninguém conta...","psst":"psst!"}),
("s14","pensoes",42.3,46.15,"13% do PIB em pensões",{"caixa":"PENSÕES","pib":"PIB","pct":13,"rotulo":"13% DO PIB","t_pct":1.4}),
("s15","ocde",46.15,48.2,"Uma das maiores da OCDE",{"rotulo":"UMA DAS MAIORES DA OCDE","ocde":"OCDE","franca":"França"}),
("s16","quebra",48.2,51.0,"O sistema quebra",{"rotulo":"SE NÃO MEXER...","t_quebra":1.02,"t_rot":1.82}),
("s17","sabem",51.0,55.25,"Governo, sindicatos e rua sabem",{"l_gov":"governo sabe","l_sind":"sindicatos sabem","l_rua":"a rua sabe","t_gov":0.54,"t_sind":2.1,"t_rua":3.36}),
("s18","teatro",55.25,59.8,"Teatro ritual / a lei passa",{"rotulo":"TEATRO RITUAL","sub":"todos encenam","lei":"LEI","carimbo":"PASSOU","t_rot":0.83,"t_sub":2.19,"t_lei":3.55}),
("s19","casa",59.8,61.6,"Todo mundo volta pra casa",{"rotulo":"todo mundo volta pra casa"}),
("s20","ciclo",61.6,63.5,"Ciclo: até a próxima reforma",{"rotulo":"ATÉ A PRÓXIMA REFORMA","n1":"REFORMA","n2":"49.3","n3":"GREVE","n4":"LEI PASSA"}),
("s21","diva",63.5,DUR,"França no divã + inscreva-se",{"rotulo":"POR QUE O CICLO NÃO QUEBRA?","botao":"INSCREVA-SE","prox":"próximo país?","t_rot":1.8,"t_insc":3.54,"t_prox":4.78}),
]
items=[{"id":i,"type":"scene","track":"fundo","label":lab,"start":a,"dur":round(b-a,2),"by":"template","props":{"scene":sc,"params":p}} for i,sc,a,b,lab,p in S]
E={"version":1,"name":NAME,"estilo":"07-cartoon-paises-personagens","grupo":"ESTILOS NOVOS",
 "canvas":{"w":1280,"h":720,"fps":30,"bg":"#38d6ff"},"duration":DUR,"template":"local",
 "referencia":{"canal":"NOTICIAS ILUSTRADAS","canal_url":"https://www.youtube.com/channel/UCiZgRgUgHHJu5fFN2tJfD8A","video":"https://youtu.be/0Ojy8i08pVQ","titulo":"FRANCE is in FLAMES! Why is there looting?","nota":"países como personagens cartoon (traço preto grosso, cores chapadas), multidão clonada, mapa chapado, personagem na frente de foto real"},
 "audio":{"voice":{"src":"voz.wav","volume":1.0,"start":0}},
 "tracks":[{"id":"fundo","name":"Cenas cartoon"}],"items":items}
json.dump(E,open("edit.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
src=open("template_src.html",encoding="utf-8").read()
imgs=sorted({it["props"]["params"]["src"] for it in items if "src" in it["props"]["params"]})
src=src.replace("%%PRE%%","".join(f'<img src="{s}">' for s in imgs)).replace("%%EUROPA%%",open("europa.json").read())
open("template.html","w",encoding="utf-8").write(src)
print(len(items),imgs)
