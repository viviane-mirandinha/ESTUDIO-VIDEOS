import json
from pathlib import Path
P=Path(__file__).parent
DUR=71.0
R=[ # rank, id, start, end, t_preco, nome, curto, sub, img, fit, moeda, num, dec, sufixo, preco_curto, valor_usd
 (6,"selo",7.3,18.0,15.68,"UM CENTAVO MAGENTA","Selo","Selo · Guiana Inglesa, 1856 · leilão Sotheby's, 2021","img/selo.jpg","contain","US$",8.3,1,"MI","US$ 8,3 mi",8.307),
 (5,"codex",18.0,26.9,23.2,"CODEX LEICESTER","Codex","Caderno de Leonardo da Vinci · comprado por Bill Gates na Christie's, 1994","img/codex.jpg","contain","US$",30.8,1,"MI","US$ 30,8 mi",30.8025),
 (4,"ferrari",26.9,35.6,32.98,"FERRARI 250 GTO","Ferrari","Ferrari 250 GTO de 1962 · leilão RM Sotheby's, 2018","img/ferrari.jpg","cover","US$",48.4,1,"MI","US$ 48,4 mi",48.405),
 (3,"mercedes",35.6,47.4,43.52,"MERCEDES 300 SLR UHLENHAUT","Mercedes","Coupé de 1955 · leilão RM Sotheby's, 2022 · carro mais caro já vendido","img/mercedes.jpg","cover","€",135,0,"MI","€ 135 mi",142),
 (2,"modigliani",47.4,54.9,51.16,"NU DEITADO","Modigliani","Amedeo Modigliani, 1917-18 · leilão Christie's, 2015","img/modigliani.jpg","cover","US$",170.4,1,"MI","US$ 170,4 mi",170.4),
 (1,"salvator",54.9,65.3,60.54,"SALVATOR MUNDI","Salvator","Atribuído a Leonardo da Vinci · leilão Christie's, 2017","img/salvator.jpg","contain","US$",450.3,1,"MI","US$ 450,3 mi",450.3),
]
items=[
 {"id":"t_titulo","type":"text","track":"textos","label":"Título","start":0.0,"dur":4.0,"by":"template","props":{"text":"DO BARATO AO MAIS CARO"}},
 {"id":"t_sub","type":"text","track":"textos","label":"Subtítulo + miniaturas","start":1.5,"dur":5.7,"by":"template","props":{"text":"6 COISAS MAIS CARAS JÁ VENDIDAS"}},
 {"id":"t_hook","type":"text","track":"textos","label":"Gancho","start":4.1,"dur":3.1,"by":"template","props":{"text":"A <b>Nº 1</b> VALE MAIS QUE AS OUTRAS 5 <b>SOMADAS</b>"}},
 {"id":"t_head","type":"text","track":"textos","label":"Cabeçalho","start":7.3,"dur":58.0,"by":"template","props":{"text":"DO BARATO AO <i>MAIS CARO</i>"}},
 {"id":"t_chart","type":"text","track":"visual","label":"Gráfico (título)","start":7.3,"dur":DUR-7.3,"by":"template","props":{"text":"VALOR PAGO (EM DÓLARES)"}},
 {"id":"t_nota","type":"text","track":"textos","label":"Nota de rodapé","start":7.3,"dur":DUR-7.3,"by":"template","props":{"text":"Valores da época da venda, sem correção · Mercedes: €135 mi ≈ US$ 142 mi (2022)"}},
]
for rk,i,s,e,tp,nome,curto,sub,img,fit,moeda,num,dec,suf,pc,vu in R:
    items.append({"id":"r_"+i,"type":"html","track":"fundo","label":f"#{rk} {nome}","start":s,"dur":round(e-s,2),"by":"template",
      "props":{"rank":rk,"nome":nome,"curto":curto,"sub":sub,"img":img,"fit":fit,"moeda":moeda,"preco_num":num,"dec":dec,"sufixo":suf,
               "preco_curto":pc,"valor_usd":vu,"t_preco":tp,"html":"","css":""}})
items+=[
 {"id":"o_final","type":"text","track":"textos","label":"Fecho pergunta","start":65.3,"dur":5.7,"by":"template","props":{"text":"QUAL DESSAS VOCÊ COMPRARIA?"}},
 {"id":"o_cta","type":"text","track":"textos","label":"Fecho comenta","start":67.5,"dur":3.5,"by":"template","props":{"text":"COMENTA AÍ!"}},
 {"id":"o_ins","type":"text","track":"textos","label":"Inscreva-se","start":68.2,"dur":2.8,"by":"template","props":{"text":"INSCREVA-SE"}},
]
extra=[{"id":f"w{k}","src":"sfx/whoosh.wav","start":round(r[2]-0.05,2),"volume":0.16,"label":"whoosh troca item"} for k,r in enumerate(R)]
edit={"version":1,"name":"35 - RANKING PRECOS - Do barato ao mais caro 6 coisas mais caras ja vendidas",
 "estilo":"Ranking crescente de preço (foto grande + etiqueta + barras)",
 "canvas":{"w":1280,"h":720,"fps":30,"bg":"#e9edf2"},"duration":DUR,"template":"local",
 "fonts":{"Anton":"fonts/Anton-Regular.ttf","Inter":"fonts/Inter.ttf"},
 "referencia":{"canais":["jack pockets (@jackpockets)","10x Discovery (@10xDiscovery)"],
   "videos":["https://youtu.be/jXwOcpkMQAA","https://youtu.be/dj0UAatiiDI"]},
 "audio":{"voice":{"src":"voz.mp3","volume":1.0,"start":0},"extra":extra},
 "tracks":[{"id":"fundo","name":"Itens"},{"id":"visual","name":"Gráfico"},{"id":"textos","name":"Textos"}],
 "items":items}
json.dump(edit,open(P/"edit.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print("ok",len(items))
