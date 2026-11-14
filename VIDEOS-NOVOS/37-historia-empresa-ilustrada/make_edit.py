import json,shutil
NAME="37 - 24-10-2026 - HISTORIA EMPRESA ILUSTRADA - A historia inteira da Nintendo em 1 minuto"
DUR=69.5
S=[
("s01","kyoto",0,4.4,"1889 - Kyoto",{"ano":"1889","sub":"Kyoto, Japão","t_ano":0.1,"t_sub":2.6}),
("s02","oficina",4.4,10.0,"Fusajiro e as hanafuda",{"rotulo":"HANAFUDA","sub":"cartas de baralho pintadas à mão","t_rot":2.44,"t_sub":3.2}),
("s03","loja",10.0,12.7,"Fachada: Nintendo",{"kanji":"任天堂","rotulo":"NINTENDO","sub":"Kyoto · 1889","t_nome":1.24}),
("s04","hiroshi",12.7,18.5,"1949 - Hiroshi assume",{"ano":"1949","nome":"HIROSHI YAMAUCHI","idade":"22 anos","t_nome":2.4,"t_idade":4.2}),
("s05","tenta",18.5,23.5,"Tentativas: Disney, táxi, arroz",{"rotulo":"tentou de tudo","a":"CARTAS DISNEY","b":"TÁXI","c":"ARROZ INSTANTÂNEO","t_a":1.22,"t_b":2.42,"t_c":3.32}),
("s06","fracassa",23.5,25.6,"Quase tudo fracassa",{"rotulo":"quase tudo fracassa"}),
("s07","yokoi",25.6,29.4,"Gunpei Yokoi",{"nome":"GUNPEI YOKOI","sub":"engenheiro da manutenção","t_nome":2.28,"t_sub":0.9}),
("s08","ultra",29.4,37.3,"1966 - Ultra Hand",{"ano":"1966","rotulo":"o braço de brinquedo que estica","vendas":"+1 MILHÃO","t_rot":2.4,"t_estica":3.56,"t_vendas":5.82}),
("s09","miya",37.3,44.4,"1981 - Miyamoto / Donkey Kong",{"ano":"1981","nome":"SHIGERU MIYAMOTO","jogo":"DONKEY KONG","rotulo":"carpinteiro de bigode","t_nome":2.46,"t_rot":5.24}),
("s10","futuro",44.4,46.5,"O futuro Mario",{"rotulo":"o futuro Mario","t_rot":0.2}),
("s11","famicom",46.5,49.5,"1983 - Famicom",{"ano":"1983","nome":"FAMICOM · JAPÃO","t_nome":1.4}),
("s12","nes",49.5,54.7,"1985 - NES nos EUA",{"ano":"1985","de":"JAPÃO","para":"EUA","nome":"NES","jogo":"SUPER MARIO BROS.","t_ano":0.5,"t_nome":1.76,"t_jogo":3.68}),
("s13","linha",54.7,60.8,"Game Boy, Wii, Switch, Switch 2",{"n1":"GAME BOY","a1":"1989","n2":"WII","a2":"2006","n3":"SWITCH","a3":"2017","n4":"SWITCH 2","a4":"2025","t1":1.2,"t2":2.16,"t3":2.68,"t4":4.86}),
("s14","gigante",60.8,64.4,"De cartas a gigante",{"rotulo":"de cartas a gigante dos games","t_seta":0.9,"t_gig":1.88}),
("s15","kyoto",64.4,DUR,"Hoje - ainda em Kyoto",{"fim":1,"x":430,"ano":"130+ anos","sub":"e ainda em Kyoto","t_ano":0.6,"t_sub":2.6}),
]
items=[{"id":i,"type":"scene","track":"fundo","label":lab,"start":a,"dur":round(b-a,2),"by":"template","props":{"scene":sc,"params":p}} for i,sc,a,b,lab,p in S]
items.append({"id":"regua","type":"scene","track":"textos","label":"Régua de anos","start":0.2,"dur":60.4,"by":"template","props":{"scene":"regua","params":{
 "anos":["1889","1949","1966","1981","1983","1985","1989","2006","2017","2025"],
 "tempos":[0.3,12.9,29.7,37.7,46.7,49.6,55.9,56.86,57.38,59.56]}}})
wh=[1.0,12.6,25.5,29.3,37.2,46.4,49.4,54.6,64.3]
E={"version":1,"name":NAME,"estilo":"37-historia-empresa-ilustrada","grupo":"ESTILOS NOVOS",
 "canvas":{"w":1280,"h":720,"fps":30,"bg":"#f4efe4"},"duration":DUR,"template":"local",
 "fonts":{"Kalam":"fonts/Kalam-Bold.ttf","Patrick Hand":"fonts/PatrickHand-Regular.ttf"},
 "referencia":{"canais":["Built On You (@BuiltonYou)","CEOzoned (@CEOzoned)"],"videos":["https://youtu.be/jOo8wSIeGus","https://youtu.be/TZIOfwN7bVI"],
  "nota":"história de empresa contada por anos; ilustração cartoon com bonecos de cabeça branca redonda e olhos de ponto, cenários detalhados, rótulos à mão entre aspas, borda de papel/vinheta"},
 "audio":{"voice":{"src":"voz.wav","volume":1.0,"start":0},
  "music":{"src":"musica.wav","volume":0.10,"start":0,"fade_out":2.0,"duck":True},
  "extra":[{"id":f"w{k}","src":"sfx/whoosh.wav","start":t,"volume":0.18,"label":"whoosh"} for k,t in enumerate(wh)]},
 "tracks":[{"id":"fundo","name":"Cenas ilustradas"},{"id":"textos","name":"Régua de anos"}],"items":items}
json.dump(E,open("edit.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
shutil.copy("template_src.html","template.html")
print(len(items))
