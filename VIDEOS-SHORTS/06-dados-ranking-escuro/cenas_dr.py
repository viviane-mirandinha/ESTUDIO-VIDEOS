# Gera as cenas dr_* (estilo 06 dados/ranking escuro amarelo) em EDITOR VIDEOS/templates/scenes/
from pathlib import Path
OUT = Path(str(__import__("pathlib").Path(__file__).resolve().parents[2] / "editor" / "templates" / "scenes"))

ICON = r'''const ICON=(n,s)=>{s=s||80;const P1="M56 22v38a12 12 0 1 1-10-11.8V36a26 26 0 1 0 24 25V40c4 3 9 5 14 5V33c-8 0-14-5-15-11z";const g={
ig:`<svg width="${s}" height="${s}" viewBox="0 0 100 100"><defs><linearGradient id="igg${s}" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#f9a23b"/><stop offset=".5" stop-color="#e1306c"/><stop offset="1" stop-color="#7b3fe4"/></linearGradient></defs><rect x="4" y="4" width="92" height="92" rx="26" fill="url(#igg${s})"/><rect x="24" y="24" width="52" height="52" rx="16" fill="none" stroke="#fff" stroke-width="7"/><circle cx="50" cy="50" r="12" fill="none" stroke="#fff" stroke-width="7"/><circle cx="68" cy="32" r="4.5" fill="#fff"/></svg>`,
tt:`<svg width="${s}" height="${s}" viewBox="0 0 100 100"><rect x="4" y="4" width="92" height="92" rx="24" fill="#111" stroke="#333" stroke-width="2"/><path d="${P1}" fill="#25f4ee" transform="translate(-3,-2)"/><path d="${P1}" fill="#fe2c55" transform="translate(3,2)"/><path d="${P1}" fill="#fff"/></svg>`,
urna:`<svg width="${s}" height="${s}" viewBox="0 0 100 100"><rect x="30" y="8" width="40" height="40" rx="3" fill="#fff"/><path d="M38 20h24M38 30h18" stroke="#111" stroke-width="5"/><rect x="10" y="40" width="80" height="52" rx="8" fill="#F5C518"/><rect x="26" y="46" width="48" height="7" rx="3" fill="#111"/></svg>`,
chat:`<svg width="${s}" height="${s}" viewBox="0 0 100 100"><path d="M14 18h72a8 8 0 0 1 8 8v40a8 8 0 0 1-8 8H44L24 92V74H14a8 8 0 0 1-8-8V26a8 8 0 0 1 8-8z" fill="#F5C518"/><circle cx="32" cy="46" r="6" fill="#111"/><circle cx="50" cy="46" r="6" fill="#111"/><circle cx="68" cy="46" r="6" fill="#111"/></svg>`,
mapa:`<svg width="${s}" height="${s}" viewBox="0 0 100 100"><path d="M50 6a30 30 0 0 0-30 30c0 24 30 58 30 58s30-34 30-58A30 30 0 0 0 50 6z" fill="#F5C518"/><circle cx="50" cy="36" r="11" fill="#111"/></svg>`};return g[n]||""};'''

NUM = r'''const PARSE=t=>{const m=String(t).match(/^([^\d]*)(\d[\d.,]*)(.*)$/);if(!m)return null;let r=m[2],tail="";while(/[.,]$/.test(r)){tail=r.slice(-1)+tail;r=r.slice(0,-1)}const dec=r.includes(",")?r.split(",")[1].length:0;return{pre:m[1],num:parseFloat(r.replace(/\./g,"").replace(",",".")),dec,thou:r.includes("."),suf:tail+m[3]}};
const FMT=(p,v)=>p.pre+v.toLocaleString("pt-BR",{minimumFractionDigits:p.dec,maximumFractionDigits:p.dec,useGrouping:p.thou})+p.suf;
const COUNT=(tl,el,txt,t,d)=>{const p=PARSE(txt);el.textContent=txt;if(!p)return;const o={v:0};tl.to(o,{v:p.num,duration:d||.8,ease:"power2.out",onUpdate:()=>{el.textContent=FMT(p,o.v)},immediateRender:false},t);tl.set(o,{v:0},0)};'''

PHOTO = r'''const FOTO=(f,ini,sz,brd)=>{const d=document.createElement("div");d.style.cssText=`width:${sz}px;height:${sz}px;border-radius:50%;overflow:hidden;border:${Math.max(3,Math.round(sz/28))}px solid ${brd};background:#2c2c30;display:flex;align-items:center;justify-content:center;font:700 ${Math.round(sz*.36)}px Oswald,Inter;color:#d8d8dc;flex:none;box-sizing:border-box`;if(f){d.innerHTML=`<img src="${f}" style="width:100%;height:100%;object-fit:cover;object-position:50% 22%">`}else d.textContent=ini||"";return d};'''

HEAD = '''<div class="hd" style="position:absolute;left:80px;right:80px;top:250px;display:flex;align-items:center;gap:24px"><div class="ic"></div><div><div class="t" style="font-family:Oswald,Inter;font-weight:700;font-size:72px;line-height:1.02;color:#F5C518;text-transform:uppercase">{{p.titulo}}</div><div class="s" style="font-size:34px;color:#a2a2a8;font-weight:600;text-transform:uppercase;letter-spacing:.03em;margin-top:6px">{{p.sub}}</div></div></div>'''

HEADJS = r'''const hd=document.querySelector(id+" .hd");if(P.icone)hd.querySelector(".ic").innerHTML=ICON(P.icone,96);else hd.querySelector(".ic").remove();if(!P.sub)hd.querySelector(".s").remove();
tl.fromTo(hd,{opacity:0,y:-24},{opacity:1,y:0,duration:.5,ease:"power2.out",immediateRender:false},S+.05);tl.set(hd,{opacity:0},0);'''

FADE = r'''tl.fromTo(id,{opacity:0},{opacity:1,duration:.35,immediateRender:false},S);tl.set(id,{opacity:0},0);tl.to(id,{opacity:0,duration:.3},S+D-.3);'''

def scene(name, params, html, js):
    src = f"<!--params {params}-->\n{html}\n<script>\n(function(tl, P){{ const S={{{{start}}}}, D={{{{dur}}}}, id=\"#{{{{id}}}}\";\n{ICON}\n{NUM}\n{PHOTO}\n{js}\n{FADE}\n}})(window.__timelines.main, {{{{json}}}});\n</script>\n"
    (OUT / f"{name}.html").write_text(src, encoding="utf-8")

# ---------------------------------------------------------------- barras / ranking
scene("dr_barras",
 '{"titulo":"TÍTULO","sub":"","icone":"","max":0,"linhas":[{"nome":"NOME","sub":"","txt":"10 MI","valor":10,"foto":"","ini":"AB","cor":"#F5C518","pos":"","dest":false,"sobe":false,"t":0,"t_sub":0,"over":false,"grupo":0,"barra":true}]}',
 f'<div id="{{{{id}}}}" style="position:absolute;inset:0;font-family:Inter,Arial,sans-serif;color:#fff">{HEAD}<div class="rows" style="position:absolute;left:70px;right:70px;top:475px"></div></div>',
 HEADJS + r'''
const box=document.querySelector(id+" .rows"), L=P.linhas||[], hasPos=L.some(r=>r.pos), X0=hasPos?100:0;
const mx=P.max||Math.max(1,...L.filter(r=>!r.over&&r.valor).map(r=>r.valor));
L.forEach((r,i)=>{const t=r.t||S+.3+i*.3, c=r.cor||"#F5C518", grey=/^#(3a3a3a|5a5a5e|6a6a70)$/i.test(c);
  const row=document.createElement("div");row.style.cssText="position:relative;height:150px;margin-bottom:30px";
  if(r.dest){const o=document.createElement("div");o.style.cssText="position:absolute;left:"+(X0-18)+"px;right:-18px;top:-16px;bottom:-14px;border:4px solid #F5C518;border-radius:16px;box-shadow:0 0 34px rgba(245,197,24,.28);background:rgba(245,197,24,.06)";row.appendChild(o);}
  if(r.pos){const p=document.createElement("div");p.textContent=r.pos;p.style.cssText="position:absolute;left:0;top:"+(r.grupo?16:24)+"px;width:"+(X0-16)+"px;text-align:right;font:700 "+(r.pos.length>3?36:50)+"px Oswald,Inter;color:"+(r.dest?"#F5C518":"#8d8d93");row.appendChild(p);}
  const tx=X0+128;
  if(r.grupo){const g=document.createElement("div");g.style.cssText="position:absolute;left:"+X0+"px;top:0;display:flex;gap:14px";
    for(let k=0;k<r.grupo;k++){const d=FOTO("","?",90,"#4a4a4e");g.appendChild(d);tl.fromTo(d,{opacity:0,scale:.6},{opacity:1,scale:1,duration:.3,ease:"back.out(2)",immediateRender:false},t+k*.09);tl.set(d,{opacity:0},0);}
    row.appendChild(g);const n=document.createElement("div");n.textContent=r.nome;n.style.cssText="position:absolute;left:"+X0+"px;top:104px;font:600 34px Inter;color:#c9c9ce;text-transform:uppercase;white-space:nowrap";row.appendChild(n);
    tl.fromTo(n,{opacity:0},{opacity:1,duration:.4,immediateRender:false},t+.3);tl.set(n,{opacity:0},0);box.appendChild(row);return;}
  const ph=FOTO(r.foto,r.ini,110,r.dest?"#F5C518":"#4a4a4e");ph.style.position="absolute";ph.style.left=X0+"px";ph.style.top="4px";row.appendChild(ph);
  const nm=document.createElement("div");nm.textContent=r.nome;nm.style.cssText="position:absolute;left:"+tx+"px;top:0;font:700 46px/1.05 Oswald,Inter;text-transform:uppercase;white-space:nowrap";row.appendChild(nm);
  let sb=null;if(r.sub){sb=document.createElement("div");sb.textContent=r.sub;sb.style.cssText="position:absolute;left:"+tx+"px;top:56px;font:500 32px Inter;color:#a2a2a8;white-space:nowrap";row.appendChild(sb);}
  let vl=null;if(r.txt){vl=document.createElement("div");vl.style.cssText="position:absolute;right:0;top:0;font:700 54px/1 Oswald,Inter;color:"+(grey?"#ffffff":c);row.appendChild(vl);}
  if(r.barra!==false&&(r.valor||r.over)){const tr=document.createElement("div");tr.style.cssText="position:absolute;left:"+tx+"px;right:0;top:108px;height:24px;border-radius:12px;background:#232326";
    const b=document.createElement("div");const f=r.over?1.6:Math.max(.02,r.valor/mx);b.style.cssText="height:100%;border-radius:12px;background:"+c+";transform-origin:0 50%;width:"+(f*100)+"%";tr.appendChild(b);row.appendChild(tr);
    tl.fromTo(b,{scaleX:0},{scaleX:1,duration:r.over?1.3:.9,ease:r.over?"power1.in":"power3.out",immediateRender:false},t+.15);tl.set(b,{scaleX:0},0);}
  box.appendChild(row);
  const up=r.dest&&r.sobe;
  tl.fromTo(row,{opacity:0,x:up?0:-40,y:up?160:0},{opacity:1,x:0,y:0,duration:up?.8:.45,ease:"power3.out",immediateRender:false},t);tl.set(row,{opacity:0},0);
  if(vl)COUNT(tl,vl,r.txt,t+.15,.9);
  if(sb&&r.t_sub){tl.fromTo(sb,{opacity:0},{opacity:1,duration:.35,immediateRender:false},r.t_sub);tl.set(sb,{opacity:0},0);}
});''')

# ---------------------------------------------------------------- número gigante
scene("dr_numero",
 '{"rotulo":"","valor":"0","unidade":"","sub":"","foto":"","ini":"","icone":"","t_valor":0,"t_sub":0,"t_rot":0,"tam":280,"cor":"#F5C518"}',
 '''<div id="{{id}}" style="position:absolute;inset:0;font-family:Inter,Arial,sans-serif;color:#fff;text-align:center">
<div class="top" style="position:absolute;left:0;right:0;top:270px;height:330px;display:flex;align-items:center;justify-content:center"></div>
<div class="rot" style="position:absolute;left:60px;right:60px;top:630px;font:700 40px/1.2 Inter;color:#e6e6ea;text-transform:uppercase;letter-spacing:.02em">{{p.rotulo}}</div>
<div class="val" style="position:absolute;left:0;right:0;top:700px;font-family:Oswald,Inter;font-weight:700;line-height:1;color:{{p.cor}}"></div>
<div class="uni" style="position:absolute;left:0;right:0;font:700 128px/1 Oswald,Inter;color:{{p.cor}};text-transform:uppercase">{{p.unidade}}</div>
<div class="sub" style="position:absolute;left:60px;right:60px;font:600 40px/1.2 Inter;color:#a8a8ae;text-transform:uppercase">{{p.sub}}</div></div>''',
 r'''const q=s=>document.querySelector(id+" "+s), top=q(".top"), v=q(".val"), u=q(".uni"), sb=q(".sub"), rt=q(".rot");
let tp=null; if(P.foto||P.ini){tp=FOTO(P.foto,P.ini,300,"#F5C518");tp.style.boxShadow="0 0 60px rgba(245,197,24,.25)";top.appendChild(tp);} else if(P.icone){top.innerHTML=ICON(P.icone,250);tp=top.firstChild;} else {top.remove();rt.style.top="430px";v.style.top="510px";}
if(!P.rotulo)rt.remove();
const tam=P.tam||280; v.style.fontSize=tam+"px"; const vt=parseFloat(v.style.top); u.style.top=(vt+tam+6)+"px"; sb.style.top=(vt+tam+(P.unidade?160:30))+"px"; if(!P.unidade)u.remove(); if(!P.sub)sb.remove();
if(tp){tl.fromTo(tp,{opacity:0,scale:.7},{opacity:1,scale:1,duration:.55,ease:"back.out(1.6)",immediateRender:false},S+.05);tl.set(tp,{opacity:0},0);}
if(P.rotulo){tl.fromTo(rt,{opacity:0,y:16},{opacity:1,y:0,duration:.4,immediateRender:false},P.t_rot||S+.15);tl.set(rt,{opacity:0},0);}
const tv=P.t_valor||S+.4; tl.fromTo(v,{opacity:0,scale:.85},{opacity:1,scale:1,duration:.45,ease:"power3.out",immediateRender:false},tv);tl.set(v,{opacity:0},0); COUNT(tl,v,P.valor,tv,.9);
if(P.unidade){tl.fromTo(u,{opacity:0,y:30},{opacity:1,y:0,duration:.45,ease:"power3.out",immediateRender:false},tv+.35);tl.set(u,{opacity:0},0);}
if(P.sub){tl.fromTo(sb,{opacity:0},{opacity:1,duration:.4,immediateRender:false},P.t_sub||tv+.6);tl.set(sb,{opacity:0},0);}
if(tp)tl.fromTo(tp,{scale:1},{scale:1.06,duration:Math.max(.5,S+D-tv-.6),ease:"none",immediateRender:false},tv+.5);''')

# ---------------------------------------------------------------- linha amarela crescendo
scene("dr_linha",
 '{"titulo":"TÍTULO","sub":"","icone":"","valores":[0,1,2,3],"labels":["","","",""],"t_ini":0,"t_fim":0,"rot_fim":"","t_rot":0,"dest_ini":2,"t_dest":0,"rot_dest":""}',
 f'<div id="{{{{id}}}}" style="position:absolute;inset:0;font-family:Inter,Arial,sans-serif;color:#fff">{HEAD}'
 '<div class="card" style="position:absolute;left:60px;right:60px;top:440px;height:640px;background:#141416;border:2px solid #2a2a2e;border-radius:22px;overflow:hidden"><svg class="g" width="960" height="640" viewBox="0 0 960 640" style="position:absolute;left:0;top:0"></svg>'
 '<div class="p1" style="position:absolute;font:700 50px/1 Oswald,Inter;color:#111;background:#F5C518;padding:10px 20px;border-radius:10px;white-space:nowrap"></div>'
 '<div class="p2" style="position:absolute;font:700 46px/1 Oswald,Inter;color:#111;background:#ffffff;padding:10px 20px;border-radius:10px;white-space:nowrap"></div></div></div>',
 HEADJS + r'''
const svg=document.querySelector(id+" .g"), V=P.valores, n=V.length, mx=Math.max(...V)*1.08, X0=70, X1=900, Y0=560, Y1=80;
const px=i=>X0+(X1-X0)*i/(n-1), py=v=>Y0-(Y0-Y1)*v/mx, NS="http://www.w3.org/2000/svg";
let h='';for(let k=0;k<=4;k++){const y=Y0-(Y0-Y1)*k/4;h+=`<line x1="${X0}" x2="${X1}" y1="${y}" y2="${y}" stroke="#2a2a2e" stroke-width="2"/>`}
const pts=V.map((v,i)=>px(i)+","+py(v)), d="M"+pts.join("L"), di="M"+pts.slice(P.dest_ini).join("L");
h+=`<defs><linearGradient id="ga{{id}}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F5C518" stop-opacity=".35"/><stop offset="1" stop-color="#F5C518" stop-opacity="0"/></linearGradient></defs>`;
h+=`<path class="ar" d="${d}L${px(n-1)},${Y0}L${X0},${Y0}Z" fill="url(#ga{{id}})"/><path class="ln" d="${d}" fill="none" stroke="#F5C518" stroke-width="7" stroke-linejoin="round" stroke-linecap="round"/><path class="dl" d="${di}" fill="none" stroke="#fff3b0" stroke-width="13" stroke-linejoin="round" stroke-linecap="round"/><circle class="dot" cx="${px(n-1)}" cy="${py(V[n-1])}" r="14" fill="#F5C518" stroke="#141416" stroke-width="5"/>`;
(P.labels||[]).forEach((l,i)=>{if(l)h+=`<text x="${px(i)}" y="${Y0+52}" fill="#a2a2a8" font-family="Inter" font-weight="600" font-size="32" text-anchor="${i===0?"start":i===n-1?"end":"middle"}">${l}</text>`});
svg.innerHTML=h;
const ln=svg.querySelector(".ln"), L=ln.getTotalLength(), dl=svg.querySelector(".dl"), L2=dl.getTotalLength();
const t0=P.t_ini||S+.3, t1=P.t_fim||t0+2.5;
tl.fromTo(ln,{strokeDasharray:L,strokeDashoffset:L},{strokeDashoffset:0,duration:t1-t0,ease:"power1.inOut",immediateRender:false},t0);tl.set(ln,{strokeDasharray:L,strokeDashoffset:L},0);
tl.fromTo(svg.querySelector(".ar"),{opacity:0},{opacity:1,duration:.8,immediateRender:false},t1-.3);tl.set(svg.querySelector(".ar"),{opacity:0},0);
const dot=svg.querySelector(".dot");tl.fromTo(dot,{opacity:0,scale:0,transformOrigin:"50% 50%"},{opacity:1,scale:1,duration:.35,ease:"back.out(2)",immediateRender:false},t1);tl.set(dot,{opacity:0},0);
const p1=document.querySelector(id+" .p1"),p2=document.querySelector(id+" .p2");
if(P.rot_fim){p1.textContent=P.rot_fim;p1.style.right="40px";p1.style.top="40px";const tr=P.t_rot||t1;tl.fromTo(p1,{opacity:0,y:-14},{opacity:1,y:0,duration:.4,immediateRender:false},tr);tl.set(p1,{opacity:0},0);COUNT(tl,p1,P.rot_fim,tr,.8);} else p1.remove();
tl.set(dl,{strokeDasharray:L2,strokeDashoffset:L2},0);
if(P.t_dest){tl.to(dl,{strokeDashoffset:0,duration:.7,ease:"power2.out"},P.t_dest);}
if(P.rot_dest){p2.textContent=P.rot_dest;p2.style.left=(px(P.dest_ini)-330)+"px";p2.style.top=(py(V[P.dest_ini])-120)+"px";const t2=P.t_dest2||P.t_dest+.5;tl.fromTo(p2,{opacity:0,x:-20},{opacity:1,x:0,duration:.4,immediateRender:false},t2);tl.set(p2,{opacity:0},0);COUNT(tl,p2,P.rot_dest,t2,.7);} else p2.remove();''')

# ---------------------------------------------------------------- mapa com pontos
scene("dr_mapa",
 '{"titulo":"TÍTULO","sub":"","icone":"mapa","base":"img/brasil_mg.svg","pontos":"img/mg_pontos.svg","cx":71.9,"cy":60.8,"zoom":1.7,"t_pontos":0,"valor":"","t_valor":0,"rot_valor":"","nota":"","t_nota":0}',
 f'<div id="{{{{id}}}}" style="position:absolute;inset:0;font-family:Inter,Arial,sans-serif;color:#fff">'
 '<div class="mp" style="position:absolute;left:160px;top:400px;width:760px;height:770px"><img class="b" src="{{p.base}}" style="position:absolute;inset:0;width:100%;height:100%"><img class="d" src="{{p.pontos}}" style="position:absolute;inset:0;width:100%;height:100%"></div>'
 + HEAD +
 '<div class="vv" style="position:absolute;left:70px;top:430px;text-shadow:0 4px 30px #000,0 0 12px #000"><div class="v" style="font:700 210px/1 Oswald,Inter;color:#F5C518"></div><div class="vr" style="font:700 40px/1.1 Inter;color:#fff;text-transform:uppercase;max-width:520px">{{p.rot_valor}}</div></div>'
 '<div class="nt" style="position:absolute;left:0;right:0;top:1090px;text-align:center"><span style="display:inline-block;font:700 40px/1.2 Inter;color:#111;background:#F5C518;padding:12px 26px;border-radius:12px;text-transform:uppercase">{{p.nota}}</span></div></div>',
 HEADJS + r'''
const mp=document.querySelector(id+" .mp"), dd=document.querySelector(id+" .d"), o=P.cx+"% "+P.cy+"%";
tl.fromTo(mp,{scale:1,transformOrigin:o},{scale:P.zoom||1.7,transformOrigin:o,duration:D,ease:"power1.inOut",immediateRender:false},S);tl.set(mp,{scale:1,transformOrigin:o},0);
const tp=P.t_pontos||S+.4;
tl.fromTo(dd,{clipPath:`circle(0% at ${o})`},{clipPath:`circle(40% at ${o})`,duration:2.2,ease:"power1.out",immediateRender:false},tp);tl.set(dd,{clipPath:`circle(0% at ${o})`},0);
const vv=document.querySelector(id+" .vv"), v=vv.querySelector(".v");
if(P.valor){const t=P.t_valor||S+.8;tl.fromTo(vv,{opacity:0,y:30},{opacity:1,y:0,duration:.45,ease:"power3.out",immediateRender:false},t);tl.set(vv,{opacity:0},0);COUNT(tl,v,P.valor,t,.8);} else vv.remove();
const nt=document.querySelector(id+" .nt");
if(P.nota){tl.fromTo(nt,{opacity:0,y:20},{opacity:1,y:0,duration:.4,immediateRender:false},P.t_nota||S+2);tl.set(nt,{opacity:0},0);} else nt.remove();''')

# ---------------------------------------------------------------- mosaico de posts
scene("dr_mosaico",
 '{"titulo":"TÍTULO","sub":"","icone":"ig","n":23,"t_ini":0,"t_cont":0,"rot":"POSTS","valor":"","unidade":"","t_valor":0,"sub_valor":"","t_sub":0}',
 f'<div id="{{{{id}}}}" style="position:absolute;inset:0;font-family:Inter,Arial,sans-serif;color:#fff">{HEAD}'
 '<div class="gr" style="position:absolute;left:80px;top:440px;width:920px;display:grid;grid-template-columns:repeat(8,1fr);gap:10px"></div>'
 '<div class="ct" style="position:absolute;left:0;right:0;top:560px;text-align:center;text-shadow:0 6px 40px #000"><span class="cn" style="font:700 220px/1 Oswald,Inter;color:#F5C518"></span><div style="font:700 60px/1 Oswald,Inter;color:#fff">{{p.rot}}</div></div>'
 '<div class="vv" style="position:absolute;left:0;right:0;top:930px;text-align:center"><div class="v" style="font:700 150px/1 Oswald,Inter;color:#F5C518"></div><div class="sv" style="font:600 38px/1.2 Inter;color:#a8a8ae;text-transform:uppercase;margin-top:10px">{{p.sub_valor}}</div></div></div>',
 HEADJS + r'''
const gr=document.querySelector(id+" .gr"), t0=P.t_ini||S+.3, tc=P.t_cont||t0+1;
for(let k=0;k<P.n;k++){const c=document.createElement("div");const l=22+((k*37)%19);c.style.cssText=`height:150px;border-radius:10px;background:linear-gradient(160deg,hsl(${(k*47)%360},14%,${l+8}%),hsl(${(k*47+40)%360},10%,${l-8}%));position:relative;border:2px solid #2e2e32`;
  c.innerHTML='<svg width="34" height="34" viewBox="0 0 10 10" style="position:absolute;left:50%;top:50%;transform:translate(-50%,-50%)"><path d="M3 2l5 3-5 3z" fill="rgba(255,255,255,.85)"/></svg><div style="position:absolute;left:8px;bottom:8px;width:44px;height:8px;border-radius:4px;background:rgba(245,197,24,.8)"></div>';
  gr.appendChild(c);tl.fromTo(c,{opacity:0,scale:.7},{opacity:1,scale:1,duration:.3,ease:"back.out(2)",immediateRender:false},t0+k*Math.min(.06,(tc-t0+.4)/P.n));tl.set(c,{opacity:0},0);}
const ct=document.querySelector(id+" .ct"), cn=ct.querySelector(".cn");
tl.fromTo(ct,{opacity:0,scale:.8},{opacity:1,scale:1,duration:.4,ease:"power3.out",immediateRender:false},tc);tl.set(ct,{opacity:0},0);COUNT(tl,cn,String(P.n),tc,.6);
tl.to(gr,{opacity:.3,duration:.3},tc);
const vv=document.querySelector(id+" .vv"), v=vv.querySelector(".v");
if(P.valor){const t=P.t_valor;v.textContent=P.valor;tl.to(ct,{y:-60,scale:.7,duration:.4},t-.2);tl.to(gr,{opacity:.55,duration:.4},t-.2);
  tl.fromTo(vv,{opacity:0,y:30},{opacity:1,y:0,duration:.45,ease:"power3.out",immediateRender:false},t);tl.set(vv,{opacity:0},0);COUNT(tl,v,P.valor,t,.9);
  const sv=vv.querySelector(".sv");if(P.sub_valor){tl.fromTo(sv,{opacity:0},{opacity:1,duration:.4,immediateRender:false},P.t_sub||t+.6);tl.set(sv,{opacity:0},0);}} else vv.remove();''')
print("cenas ok")
