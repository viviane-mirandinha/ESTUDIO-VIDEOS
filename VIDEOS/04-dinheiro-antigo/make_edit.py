# converte o plano de cenas (build.py) para edit.json v1 (EDITOR VIDEOS/FORMATO.md), template generic
import json,re
src=open("build.py",encoding="utf-8").read()
ns={};exec(src.split("clips=[]")[0],ns)
S,TINT,DUR,X=ns["S"],ns["TINT"],ns["DUR"],ns["X"]
items=[];css=[]
for i,(st,im,z0,z1,x0,x1,y0,y1,t,d) in enumerate(S):
    en=S[i+1][0]+X if i+1<len(S) else DUR
    mo="zoom_in" if z1>z0 else "zoom_out"
    if abs(x1-x0)>=6: mo="pan_right" if x1>x0 else "pan_left"
    items.append({"id":f"s{i}","type":"image","track":"fundo","label":d,"start":st,"dur":round(en-st,3),
      "in":"fade" if i else "none","out":"none",
      "props":{"src":f"img/{im}.jpg","fit":"cover","x":640,"y":360,"w":1236,"h":684,"radius":22,
               "motion":mo,"motion_amount":round(abs(z1-z0),2),"opacity":1}})
    css.append(f"#s{i} img,#s{i}{{filter:{TINT[t]}}}")
vig=("<div class='vig'></div>",".vig{width:1236px;height:684px;border-radius:22px;box-shadow:inset 0 0 140px 40px rgba(0,0,0,.75);"
     "background:radial-gradient(ellipse at center,rgba(0,0,0,0) 55%,rgba(0,0,0,.45) 100%)}")
grain=("<svg width='1280' height='720' style='opacity:.16;mix-blend-mode:overlay'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/></filter><rect width='100%' height='100%' filter='url(#n)'/></svg>","")
items.append({"id":"vinheta","type":"html","track":"visual","label":"Vinheta + moldura","start":0,"dur":DUR,"in":"none","out":"none","props":{"html":vig[0],"css":vig[1],"x":640,"y":360,"w":1236,"h":684}})
items.append({"id":"grao","type":"html","track":"visual","label":"Grão de filme","start":0,"dur":DUR,"in":"none","out":"none","props":{"html":grain[0],"css":"","x":640,"y":360,"w":1280,"h":720}})
items.append({"id":"fade_final","type":"html","track":"visual","label":"Fade p/ preto","start":DUR-1.3,"dur":1.3,"in":"fade","out":"none","props":{"html":"<div style='width:1280px;height:720px;background:#000'></div>","css":"","x":640,"y":360,"w":1280,"h":720}})
E={"version":1,"name":"04 - Dinheiro Antigo - J.P. Morgan salvou os bancos em 1907","canvas":{"w":1280,"h":720,"fps":30,"bg":"#0b0a08"},
 "duration":DUR,"template":"generic","head":"<style>"+"\n".join(css)+"</style>",
 "audio":{"voice":{"src":"voz.mp3","volume":1.0,"start":0}},
 "tracks":[{"id":"fundo","name":"Fotos de arquivo (Ken Burns)"},{"id":"visual","name":"Vinheta / grão"}],
 "items":items,"_origem":{"build_script":"build.py","composicao_render_teste":"hf/index.html (gerado por build.py)"}}
json.dump(E,open("edit.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print(len(items))
