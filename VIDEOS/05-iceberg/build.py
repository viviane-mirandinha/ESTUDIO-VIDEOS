# Gera proj/index.html — estilo iceberg (Psychopoly). python build.py
import json, os
D = os.path.dirname(os.path.abspath(__file__))
DUR = 67.2
W, H = 1280, 720
CX = 520            # centro do iceberg no mundo
WL = 420            # linha d'água
TH = 600            # altura de cada camada
TIERS = [
 ("CAMADA 1 · SUPERFÍCIE", "#2f86c9", [("Tartarugas",.30,.08,None),("Tubarões",-.40,.24,13.68),("Baleias",.40,.40,14.62),("Golfinhos",-.20,.56,None),("Corais",.45,.72,None),("Polvos",-.45,.88,None)]),
 ("CAMADA 2 · ZONA DO CREPÚSCULO", "#1d5f9e", [("Luz desaparece",.30,.08,19.5),("Peixe-machado",-.45,.24,None),("Bioluminescência",0,.44,22.4),("Águas-vivas",.45,.66,None),("Peixe-lanterna",-.40,.84,None)]),
 ("CAMADA 3 · LENDAS VIVAS", "#143f73", [("Filmada em 2012",-.30,.08,33.7),("Peixe-remo",.45,.24,None),("Lula-gigante",0,.44,29.16),("Kraken",.45,.66,None),("Lula-colossal",-.40,.84,None)]),
 ("CAMADA 4 · SEM LUZ DO SOL", "#0d2a52", [("1977",.45,.08,41.56),("Vida sem sol",-.40,.24,44.7),("Fontes hidrotermais",0,.44,39.4),("Fumarolas negras",.35,.66,None),("Vermes-tubulares",-.35,.84,None)]),
 ("CAMADA 5 · O ABISMO", "#071935", [("Challenger Deep",.40,.08,None),("Fossa das Marianas",0,.26,48.06),("~11.000 m",.45,.46,51.64),("Pressão esmagadora",-.35,.62,53.12),("Titanic (3.800 m)",.10,.84,56.62)]),
 ("CAMADA ??? · O DESCONHECIDO", "#02070f", [("???",0,.35,60.7),("Ainda não descoberto",-.05,.62,61.86)]),
]
NT = len(TIERS)
BOT = WL + TH * NT
def hw(y):  # meia-largura do corpo submerso
    k = (y - WL) / (BOT - WL)
    return 430 - 270 * k
def tier_cy(i): return WL + TH * i + TH / 2

# corpo do iceberg (submerso) e ponta
body = [(CX-hw(WL), WL)]
for y in range(WL, BOT+1, 150):
    body.append((CX-hw(y)+ (18 if (y//150)%2 else -14), y))
body.append((CX-60, BOT+120)); body.append((CX+40, BOT+150))
for y in range(BOT, WL-1, -150):
    body.append((CX+hw(y)+ (-16 if (y//150)%2 else 20), y))
body.append((CX+hw(WL), WL))
bodyp = " ".join(f"{x:.0f},{y:.0f}" for x,y in body)
tip = [(CX-330,WL),(CX-230,WL-110),(CX-150,WL-160),(CX-70,WL-300),(CX+10,WL-250),(CX+80,WL-330),(CX+170,WL-170),(CX+260,WL-120),(CX+340,WL)]
tipp = " ".join(f"{x},{y}" for x,y in tip)

svg = [f'<svg class="ab" style="left:0;top:0" width="{W}" height="{BOT+300}" viewBox="0 0 {W} {BOT+300}">',
 '<defs><clipPath id="cb"><polygon points="%s"/></clipPath>' % bodyp,
 '<linearGradient id="gtip" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset=".6" stop-color="#d8eefc"/><stop offset="1" stop-color="#9fcdee"/></linearGradient>',
 '<linearGradient id="gsky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000"/><stop offset="1" stop-color="#0a1626"/></linearGradient></defs>',
 f'<rect x="0" y="0" width="{W}" height="{WL}" fill="url(#gsky)"/>']
# faixas do oceano (largura toda) + faixas do iceberg (clip)
for i,(nm,col,_) in enumerate(TIERS):
    y = WL + TH*i
    svg.append(f'<rect x="0" y="{y}" width="{W}" height="{TH}" fill="{col}" opacity=".55"/>')
for i,(nm,col,_) in enumerate(TIERS):
    y = WL + TH*i
    svg.append(f'<rect x="0" y="{y}" width="{W}" height="{TH+2}" fill="{col}" clip-path="url(#cb)"/>')
    svg.append(f'<rect x="0" y="{y}" width="{W}" height="{TH}" fill="#bfe6ff" opacity="{max(0.02, .30-0.055*i):.3f}" clip-path="url(#cb)"/>')
svg.append(f'<rect x="0" y="{BOT}" width="{W}" height="300" fill="#000"/>')
svg.append(f'<polygon points="{bodyp}" fill="none" stroke="#cfeaff" stroke-opacity=".35" stroke-width="3"/>')
for i in range(1, NT):
    y = WL + TH*i
    svg.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="#fff" stroke-opacity=".28" stroke-width="2" stroke-dasharray="14 10"/>')
svg.append(f'<polygon points="{tipp}" fill="url(#gtip)" stroke="#fff" stroke-width="2"/>')
svg.append(f'<rect x="0" y="{WL-3}" width="{W}" height="6" fill="#7cc7ff" opacity=".8"/>')
svg.append('</svg>')

items = []
for i,(nm,col,its) in enumerate(TIERS):
    y0 = WL + TH*i
    items.append(f'<div class="ab tlab" style="left:28px;top:{y0+18}px">{nm}</div>')
    for (tx,rx,ry,ta) in its:
        y = y0 + 40 + ry*(TH-90)
        x = CX + rx*hw(y)*0.78
        big = ' big' if ta and ta in (13.68,22.4,29.16,39.4,48.06,60.7) else ''
        dat = f' data-hl="{ta}"' if ta else ''
        items.append(f'<div class="ab it{big}" style="left:{x:.0f}px;top:{y:.0f}px"{dat}>{tx}</div>')
items.append(f'<div class="ab title" id="ttl">ICEBERG DOS<br>MISTÉRIOS DO OCEANO</div>')

# câmera: (t, cx, cy, s)
CAM = [(0,640,BOT/2+60,0.165),(7.6,640,BOT/2+60,0.18),(8.8,600,300,0.95),(10.9,600,330,1.02),
       (11.6,640,tier_cy(0),1.0),(17.4,640,tier_cy(0),1.06),(18.5,640,tier_cy(1),1.0),(26.6,640,tier_cy(1),1.07),
       (27.7,640,tier_cy(2),1.0),(37.9,640,tier_cy(2),1.08),(39.0,640,tier_cy(3),1.0),(46.3,640,tier_cy(3),1.07),
       (47.4,640,tier_cy(4),1.0),(55.6,640,tier_cy(4)+40,1.08),(60.3,640,tier_cy(4)+120,1.1),(61.4,640,tier_cy(5),1.0),
       (63.6,640,tier_cy(5),1.06),(65.3,640,BOT/2+60,0.165),(DUR,640,BOT/2+60,0.17)]
# profundidade exibida por camada (cy do centro da tela -> metros)
DEPTH = [(WL,0),(WL+TH,200),(WL+2*TH,1000),(WL+3*TH,2000),(WL+4*TH,4000),(WL+5*TH,11000),(BOT,11000)]
# painel de imagem: (t_in, t_out, src, legenda)
PAN = [(13.6,17.3,"sup","Tubarões e baleias"),(22.3,26.5,"bio","Criaturas bioluminescentes"),(29.1,37.8,"lula","Lula-gigante"),
       (39.3,46.2,"vent","Fontes hidrotermais"),(48.0,56.4,"fossa","Fossa das Marianas"),(56.5,60.2,"titanic","Titanic · ~3.800 m"),
       (60.7,63.8,"unk","O que ainda não vimos")]
# chips de fato (t_in, t_out, texto)
CHIP = [(33.6,37.8,"2012 · filmada viva no Japão"),(41.5,46.2,"descobertas em 1977"),(44.2,46.2,"vida sem luz solar"),
        (51.6,56.4,"≈ 11.000 metros"),(53.1,56.4,"pressão esmagadora"),(58.1,60.2,"repousa a ~3.800 m")]
STATS = [(1.3,7.9,"70%","do planeta é oceano","left:70px;top:250px"),(3.5,7.9,"+80%","do fundo sem mapa detalhado","right:70px;top:250px;text-align:right")]

pan_html = "".join(f'<div class="ab pan" data-a="{a}" data-b="{b}"><img src="P/{s}.jpg"><div class="cap">{c}</div></div>' for a,b,s,c in PAN)
chips, last = [], {}
for a,b,tx in CHIP:
    k = sum(1 for a2,b2,_ in CHIP if a2 < a and b2 > a)
    chips.append(f'<div class="ab chip" style="top:{555+k*58}px" data-a="{a}" data-b="{b}">{tx}</div>')
stats = "".join(f'<div class="ab stat" style="{pos}" data-a="{a}" data-b="{b}"><b>{n}</b><span>{tx}</span></div>' for a,b,n,tx,pos in STATS)
bubbles = "".join(f'<div class="bub" data-k="{i}"></div>' for i in range(26))

html = f'''<!doctype html>
<html lang="pt"><head><meta charset="UTF-8" /><meta name="viewport" content="width={W}, height={H}" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>@font-face{{font-family:'Inter';src:url('fonts/Inter.ttf');font-weight:100 900;}}
@font-face{{font-family:'Anton';src:url('fonts/Anton-Regular.ttf');}}
html,body{{margin:0;padding:0;width:{W}px;height:{H}px;overflow:hidden;background:#000}}
#root{{position:absolute;left:0;top:0;width:{W}px;height:{H}px;overflow:hidden;background:#000;font-family:'Inter',sans-serif;color:#fff}}
.ab{{position:absolute}} img{{display:block}}
#world{{position:absolute;left:0;top:0;width:{W}px;height:{BOT+300}px;transform-origin:0 0}}
.it{{transform:translate(-50%,-50%);font-weight:800;font-size:30px;white-space:nowrap;padding:4px 12px;border-radius:6px;
 text-shadow:2px 2px 0 #000,-1px -1px 0 #000,0 0 10px rgba(0,0,0,.9);border:3px solid transparent}}
.it.big{{font-size:40px}}
.it.on{{border-color:#ffd84a;background:rgba(0,0,0,.45);color:#ffe98a}}
.tlab{{font-family:'Anton';font-size:30px;letter-spacing:2px;color:#fff;opacity:.85;text-shadow:2px 2px 0 #000}}
.title{{left:{CX}px;top:40px;transform:translateX(-50%);font-family:'Anton';font-size:58px;line-height:1.02;text-align:center;
 text-shadow:3px 3px 0 #000,0 0 18px #000;white-space:nowrap}}
.pan{{left:880px;top:110px;width:350px;background:#000;border:4px solid #fff;box-shadow:0 18px 50px rgba(0,0,0,.7)}}
.pan img{{width:350px;height:350px;object-fit:cover}}
.pan .cap{{font-weight:800;font-size:24px;padding:10px 14px;background:#0b1a2e;border-top:3px solid #ffd84a}}
.chip{{left:880px;font-weight:800;font-size:23px;padding:8px 16px;background:rgba(0,0,0,.78);border-left:6px solid #ffd84a;white-space:nowrap}}
.stat{{width:420px;text-shadow:3px 3px 0 #000}} .stat b{{display:block;font-family:'Anton';font-size:110px;line-height:1}} .stat span{{font-size:30px;font-weight:800}}
#depth{{right:50px;top:40px;font-family:'Anton';font-size:30px;letter-spacing:1px;text-shadow:2px 2px 0 #000;opacity:.9}}
#cta{{left:50%;top:240px;transform:translateX(-50%);text-align:center}}
#cta .b1{{display:inline-block;font-family:'Anton';font-size:64px;padding:6px 34px;background:#c4161c;border-radius:10px;text-shadow:none}}
#cta .b2{{margin-top:22px;font-weight:800;font-size:36px;text-shadow:2px 2px 0 #000,0 0 12px #000}}
.bub{{position:absolute;width:8px;height:8px;border-radius:50%;border:2px solid rgba(200,235,255,.45)}}
#vig{{position:absolute;inset:0;background:radial-gradient(ellipse at center,rgba(0,0,0,0) 55%,rgba(0,0,0,.65) 100%);pointer-events:none}}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="{W}" data-height="{H}">
<div id="world">{"".join(svg)}{"".join(items)}</div>
<div id="bubs">{bubbles}</div>
<div id="vig"></div>
{stats}{pan_html}{"".join(chips)}
<div class="ab" id="depth">PROFUNDIDADE: 0 m</div>
<div class="ab" id="cta" data-a="64.0" data-b="99"><div class="b1">INSCREVA-SE</div><div class="b2">Qual camada te assustou mais? Comente!</div></div>
</div>
<script>
window.__timelines = window.__timelines || {{}};
window.__hfRender = window.__hfRender || null;
const tl = gsap.timeline({{paused:true, onUpdate:()=>{{ if(window.__hfRender) window.__hfRender(tl.time()); }}}});
tl.to({{v:0}},{{v:1,duration:{DUR},ease:"none"}},0);
window.__timelines["main"] = tl;
</script>
<script>
const CAM={json.dumps(CAM)}, DEPTH={json.dumps(DEPTH)};
const clamp=(x,a=0,b=1)=>Math.min(b,Math.max(a,x)), lerp=(a,b,k)=>a+(b-a)*k;
const io=k=>{{k=clamp(k);return k<.5?4*k*k*k:1-Math.pow(-2*k+2,3)/2}}, eo=k=>{{k=clamp(k);return 1-Math.pow(1-k,3)}};
const back=k=>{{k=clamp(k);const c=1.6;return 1+(c+1)*Math.pow(k-1,3)+c*Math.pow(k-1,2)}};
const W={W},H={H};
const world=document.getElementById('world');
const HL=[...document.querySelectorAll('[data-hl]')].map(e=>({{e,t:+e.dataset.hl}}));
const AN=[...document.querySelectorAll('[data-a]')].map(e=>({{e,a:+e.dataset.a,b:+e.dataset.b}}));
const BUB=[...document.querySelectorAll('.bub')];
function cam(t){{
 for(let i=0;i<CAM.length-1;i++){{const A=CAM[i],B=CAM[i+1]; if(t<=B[0]){{
   const hold=(B[3]/A[3]>0.95&&B[3]/A[3]<1.1&&Math.abs(B[2]-A[2])<200);
   const k=hold?(t-A[0])/(B[0]-A[0]):io((t-A[0])/(B[0]-A[0]));
   // zoom em escala log p/ voos longos
   const s=Math.exp(lerp(Math.log(A[3]),Math.log(B[3]),k));
   return [lerp(A[1],B[1],k),lerp(A[2],B[2],k),s];}}}}
 const L=CAM[CAM.length-1]; return [L[1],L[2],L[3]];
}}
function depthAt(y){{if(y<=DEPTH[0][0])return 0; for(let i=0;i<DEPTH.length-1;i++){{const A=DEPTH[i],B=DEPTH[i+1]; if(y<=B[0]) return lerp(A[1],B[1],(y-A[0])/(B[0]-A[0]));}} return DEPTH[DEPTH.length-1][1];}}
function renderAt(t){{
 const [cx,cy,s]=cam(t);
 world.style.transform=`translate(${{W/2-cx*s}}px,${{H/2-cy*s}}px) scale(${{s}})`;
 for(const o of HL){{const on=t>=o.t; o.e.classList.toggle('on',on);
   const k=clamp((t-o.t)/0.35); o.e.style.transform=`translate(-50%,-50%) scale(${{on?lerp(1.5,1.12,eo(k)):1}})`;}}
 for(const o of AN){{const ki=clamp((t-o.a)/0.4),ko=clamp((t-o.b)/0.3); const op=ki>0?Math.min(1,ki*2.5)*(1-ko):0;
   o.e.style.opacity=op; o.e.style.visibility=op>0.002?'visible':'hidden';
   const base=o.e.id==='cta'?'translateX(-50%) ':''; o.e.style.transform=base+`translateX(${{(1-eo(ki))*40}}px) scale(${{lerp(.92,1,back(ki))}})`;
   const im=o.e.querySelector('img'); if(im) im.style.transform=`scale(${{1.04+0.08*clamp((t-o.a)/(o.b-o.a))}})`;}}
 const ttl=document.getElementById('ttl'); const kt=clamp((t-8.6)/0.5)*(1-clamp((t-11.0)/0.4)); ttl.style.opacity=kt;
 const d=document.getElementById('depth'); const dd=s>0.5?depthAt(cy):0;
 d.textContent='PROFUNDIDADE: '+Math.round(dd).toLocaleString('pt-BR')+' m'; d.style.opacity=s>0.5&&t<64?0.9:0;
 const under=s>0.5&&cy>360&&t<64.5;
 BUB.forEach((b,i)=>{{const sp=40+(i*37)%60, x=(i*197)%W + Math.sin(t*1.3+i)*14, y=H+20-((t*sp+i*91)%(H+60));
   b.style.transform=`translate(${{x}}px,${{y}}px) scale(${{0.6+(i%5)*0.25}})`; b.style.opacity=under?0.8:0;}});
}}
window.__hfRender=t=>renderAt(t); window.addEventListener("hf-seek",e=>window.__hfRender(e.detail.time)); renderAt(0);
</script>
</body></html>'''
open(os.path.join(D, "proj", "index.html"), "w", encoding="utf-8").write(html)

edit = {"canvas":{"w":W,"h":H,"fps":30},"audio":r"voz.mp3","build_script":os.path.join(D,"build.py"),
 "hyperframes_project":os.path.join(D,"proj"),
 "cenas":[{"start":c[0],"dur":round(CAM[i+1][0]-c[0],2),"tipo":"camera","params":{"cx":c[1],"cy":c[2],"scale":c[3]}} for i,c in enumerate(CAM[:-1])]
  +[{"start":a,"dur":round(b-a,2),"tipo":"imagem","src":f"proj/P/{s}.jpg","texto":c} for a,b,s,c in PAN]
  +[{"start":a,"dur":round(b-a,2),"tipo":"chip","texto":tx} for a,b,tx in CHIP]
  +[{"start":a,"dur":round(b-a,2),"tipo":"stat","texto":f"{n} {tx}"} for a,b,n,tx,_ in STATS]
  +[{"start":it[3],"dur":None,"tipo":"destaque_item","texto":it[0],"params":{"camada":i+1}} for i,tr in enumerate(TIERS) for it in tr[2] if it[3]]
  +[{"start":64.0,"dur":3.2,"tipo":"cta","texto":"INSCREVA-SE / Qual camada te assustou mais?"}]}
json.dump(edit, open(os.path.join(D,"edit.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok", len(html))
