# build.py — gera hf/index.html (estilo documentário de arquivo, Ken Burns) + edit.json
import json
DUR=61.24
# (start, img, zoom_from, zoom_to, x_from%, x_to%, y_from%, y_to%, tint, desc)
S=[
(0.0,"04",1.05,1.18,0,-2,0,3,"sep","Broad Street, NY 1900s"),
(3.3,"11",1.20,1.06,0,0,-3,2,"grn","NYSE sepia"),
(7.1,"02",1.04,1.20,2,-1,0,0,"sep","Knickerbocker Trust exterior"),
(11.2,"05",1.10,1.22,-2,2,0,0,"grn","correntistas na porta"),
(14.0,"03",1.06,1.25,0,0,-2,3,"sep","multidao panico 1907"),
(16.5,"14",1.15,1.04,-3,3,0,0,"grn","Knickerbocker com fila"),
(19.0,"06",1.04,1.15,0,0,0,0,"sep","cartoon ursos Wall St 1907"),
(21.1,"07",1.02,1.16,0,0,0,4,"sep","retrato J.P. Morgan"),
(25.3,"15",1.04,1.14,0,0,-4,2,"grn","caricatura Morgan 1902"),
(27.5,"08",1.05,1.20,2,-2,0,0,"sep","biblioteca Morgan"),
(33.8,"10",1.18,1.05,0,0,3,-3,"sep","bolsa NY desenho"),
(37.2,"11",1.05,1.25,3,-3,0,0,"grn","NYSE close"),
(39.1,"03",1.30,1.12,-4,4,2,0,"sep","multidao close"),
(42.6,"07",1.18,1.40,0,0,2,6,"dark","Morgan close - um unico homem"),
(45.8,"12",1.05,1.18,0,0,0,0,"sep","Federal Reserve Board 1914"),
(49.9,"13",1.20,1.04,0,0,-3,3,"grn","12 bancos do Fed"),
(55.9,"02",1.25,1.08,0,0,0,0,"sep","Knickerbocker - encerramento"),
]
TINT={"sep":"grayscale(1) sepia(.55) contrast(1.1) brightness(.92)",
      "grn":"grayscale(1) sepia(.35) hue-rotate(40deg) contrast(1.08) brightness(.9)",
      "dark":"grayscale(1) sepia(.5) contrast(1.25) brightness(.75)"}
X=0.5  # crossfade
clips=[];js=[];scenes=[]
for i,(st,im,z0,z1,x0,x1,y0,y1,t,d) in enumerate(S):
    en=S[i+1][0]+X if i+1<len(S) else DUR
    du=round(en-st,3)
    clips.append(f'<div id="s{i}" class="clip shot" data-start="{st}" data-duration="{du}" data-track-index="{1+i%2}"><img src="media/{im}.jpg" style="filter:{TINT[t]}"/></div>')
    js.append(f'tl.fromTo("#s{i} img",{{scale:{z0},xPercent:{x0},yPercent:{y0}}},{{scale:{z1},xPercent:{x1},yPercent:{y1},duration:{du},ease:"none"}},{st});')
    if i: js.append(f'tl.fromTo("#s{i}",{{opacity:0}},{{opacity:1,duration:{X},ease:"none"}},{st});')
    scenes.append({"start":st,"dur":du,"tipo":"foto_kenburns","src":f"hf/media/{im}.jpg","params":{"zoom":[z0,z1],"x":[x0,x1],"y":[y0,y1],"tint":t,"crossfade":X},"texto":d})
js.append(f'tl.fromTo("#s0",{{opacity:0}},{{opacity:1,duration:0.8}},0);')
js.append(f'tl.to("#fade",{{opacity:1,duration:1.2}},{DUR-1.3});')
# flicker sutil de projetor
js.append('for(let k=0;k<%d;k++){tl.to("#flk",{opacity:(k%%3?0.06:0.12),duration:0.12},k*0.5);tl.to("#flk",{opacity:0.03,duration:0.2},k*0.5+0.12);}'%int(DUR*2))
html=f'''<!doctype html><html><head><meta charset="utf-8">
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
html,body{{margin:0;background:#000;width:1280px;height:720px;overflow:hidden}}
#root{{position:relative;width:1280px;height:720px;background:#0b0a08;overflow:hidden}}
.shot{{position:absolute;left:22px;top:18px;width:1236px;height:684px;border-radius:22px;overflow:hidden;background:#111}}
.shot img{{width:100%;height:100%;object-fit:cover;transform-origin:50% 50%}}
#vig{{position:absolute;left:22px;top:18px;width:1236px;height:684px;border-radius:22px;pointer-events:none;
 box-shadow:inset 0 0 140px 40px rgba(0,0,0,.75);background:radial-gradient(ellipse at center,rgba(0,0,0,0) 55%,rgba(0,0,0,.45) 100%)}}
#grain{{position:absolute;inset:0;opacity:.16;mix-blend-mode:overlay;pointer-events:none}}
#flk{{position:absolute;inset:0;background:#fff4dc;opacity:.03;pointer-events:none}}
#fade{{position:absolute;inset:0;background:#000;opacity:0}}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1280" data-height="720">
{chr(10).join(clips)}
<div id="vig" class="clip" data-start="0" data-duration="{DUR}" data-track-index="10"></div>
<svg id="grain" class="clip" data-start="0" data-duration="{DUR}" data-track-index="11" width="1280" height="720"><filter id="n"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" stitchTiles="stitch"/></filter><rect width="100%" height="100%" filter="url(#n)"/></svg>
<div id="flk" class="clip" data-start="0" data-duration="{DUR}" data-track-index="12"></div>
<div id="fade" class="clip" data-start="0" data-duration="{DUR}" data-track-index="13"></div>
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{paused:true}});
{chr(10).join(js)}
window.__timelines["main"] = tl;
</script></body></html>'''
open("hf/index.html","w",encoding="utf-8").write(html)
json.dump({"canvas":{"w":1280,"h":720,"fps":30},"audio":"voz.mp3","duracao":DUR,
 "overlays":["vinheta+cantos arredondados","grão SVG","flicker projetor","fade final"],"cenas":scenes,
 "build_script":"VIDEOS/04-dinheiro-antigo/build.py","composicao":"VIDEOS/04-dinheiro-antigo/hf/index.html"},
 open("edit.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print(len(S),"shots")
