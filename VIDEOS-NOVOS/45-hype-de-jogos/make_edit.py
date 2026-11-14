import json,shutil
NAME="45 - 24-10-2026 - HYPE DE JOGOS - A historia dos videogames em 60 segundos"
DUR=70.6
words=json.load(open("words.json",encoding="utf-8"))["words"]
S=[
("s01","intro",0,4.4,"Intro: título glitch",{"tag":"TUDO QUE SABEMOS","l1":"A HISTÓRIA DOS","l2":"VIDEOGAMES","pill":"EM 60 SEGUNDOS","t_l2":1.4,"t_pill":2.5}),
("s02","contagem",4.4,7.8,"Contagem regressiva",{"n":["3","2","1"],"tn":[0.05,0.55,1.05],"fim":"VALENDO!","t_fim":1.5}),
("s03","osc",7.8,15.7,"1958 - Tennis for Two",{"ano":"1958","sub":"FÍSICO + OSCILOSCÓPIO","nome":"TENNIS FOR TWO","nota":"um dos primeiros jogos eletrônicos","t_nome":3.9,"t_nota":4.85}),
("s04","odyssey",15.7,25.8,"1972 - Odyssey e Pong",{"ano":"1972","c1":"MAGNAVOX ODYSSEY","c1s":"1º CONSOLE DE CASA","c2":"PONG","c2s":"ATARI · FLIPERAMAS","fim":"EXPLODE","t_c1":1.9,"t_c2":5.5,"t_fim":8.8}),
("s05","crash",25.8,36.7,"1983 - Crash",{"ano":"1983","titulo":"CRASH","g":"MERCADO DOS EUA","rumor":"VIDEOGAME É MODA PASSAGEIRA","t_tit":2.05,"t_g":3.0,"t_rumor":7.5}),
("s06","nes",36.7,43.9,"1985 - NES nos EUA",{"carimbo":"ERRADO","ano":"1985","nome":"NES CHEGA AOS EUA","conf":"A INDÚSTRIA RESSUSCITA","rumor":"MODA PASSAGEIRA","t_ano":1.4,"t_nome":3.3,"t_conf":4.9}),
("s07","bolso",43.9,48.2,"1989 - Game Boy",{"ano":"1989","nome":"GAME BOY","sub":"O JOGO NO BOLSO","t_nome":1.9,"t_sub":3.2}),
("s08","disco",48.2,55.2,"94/95 - PlayStation",{"d1":"FIM DE 1994","l1":"JAPÃO","d2":"1995","l2":"EUA","nome":"PLAYSTATION","a":"3D","b":"CD","t_d2":2.3,"t_nome":4.1,"t_a":5.3,"t_b":5.9}),
("s09","online",55.2,59.4,"Internet, celular, online",{"a":"INTERNET","b":"CELULAR","c":"ONLINE","ta":1.25,"tb":2.1,"tc":3.05}),
("s10","bilhoes",59.4,62.6,"Hoje: bilhões jogam",{"tag":"HOJE","big":"BILHÕES","sub":"de pessoas jogam","t_big":0.75}),
("s11","proxima",62.6,DUR,"Próxima fase + CTA",{"titulo":"PRÓXIMA FASE?","card":"DATA DE LANÇAMENTO","data":"??/??/????","status":"SEM DATA","cta":"QUAL FOI SEU 1º CONSOLE?","cta_tag":"COMENTA AÍ","t_card":2.5,"t_cta":4.4}),
]
items=[{"id":i,"type":"scene","track":"fundo","label":lab,"start":a,"dur":round(b-a,2),"by":"template","props":{"scene":sc,"params":p}} for i,sc,a,b,lab,p in S]
items.append({"id":"hud","type":"scene","track":"visual","label":"HUD: barra de carregamento + anos","start":0.3,"dur":round(DUR-0.6,2),"by":"template","props":{"scene":"hud","params":{
 "rotulo":"CARREGANDO HISTÓRIA","anos":["1958","1972","1983","1985","1989","1994","HOJE"],"tempos":[7.9,15.8,26.4,38.1,44.2,48.9,59.6]}}})
items.append({"id":"leg","type":"scene","track":"legenda","label":"Legenda amarela palavra a palavra","start":0,"dur":DUR,"by":"template","props":{"scene":"legenda","params":{
 "cor":"#ffe14d","y":668,"size":54,"words":words}}})
wh=[4.35,7.75,15.65,25.75,36.65,43.85,48.15,55.15,59.35,62.55]
E={"version":1,"name":NAME,"estilo":"45-hype-de-jogos","grupo":"ESTILOS NOVOS",
 "canvas":{"w":1280,"h":720,"fps":30,"bg":"#0636c9"},"duration":DUR,"template":"local",
 "fonts":{"Anton":"fonts/Anton-Regular.ttf","Montserrat Black":"fonts/Montserrat-Black.ttf"},
 "referencia":{"canal":"Hazard","canal_url":"https://www.youtube.com/channel/UCI1-J45WXprOQQ_m9pmfW9A","video":"https://youtu.be/BQvC8KDhgqw",
  "titulo":"GTA 6: EVERYTHING We Know So Far... (The ULTIMATE Breakdown)",
  "canais":["Hazard","TGG"],"videos":["https://youtu.be/BQvC8KDhgqw","https://youtu.be/FV93IVwJP_4"],
  "nota":"vídeo de hype/notícia de game: fundo azul-royal em gradiente, cards arredondados com borda branca que pulam na tela, pílula rosa de destaque, palavra gigante amarela com contorno preto por cima, cortes rápidos; aqui tudo redesenhado em código (sem footage, logo ou personagem de jogo real)"},
 "audio":{"voice":{"src":"voz.wav","volume":1.0,"start":0},
  "music":{"src":"musica.wav","volume":0.16,"start":0,"fade_out":2.0,"duck":True},
  "extra":[{"id":f"w{k}","src":"sfx/whoosh.wav","start":t,"volume":0.2,"label":"whoosh"} for k,t in enumerate(wh)]},
 "tracks":[{"id":"fundo","name":"Cenas"},{"id":"visual","name":"HUD"},{"id":"legenda","name":"Legenda"}],"items":items}
json.dump(E,open("edit.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
shutil.copy("template_src.html","template.html")
print(len(items))
