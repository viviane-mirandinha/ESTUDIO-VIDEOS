# Cenas novas do estilo dr_* (short 07): dr_pessoa, dr_grade, dr_cartas, dr_frase -> EDITOR VIDEOS/templates/scenes/
# Reaproveita ICON/NUM/FOTO/HEAD/FADE/scene() do cenas_dr.py do short 06 (sem regravar as cenas antigas).
src = open(str(__import__("pathlib").Path(__file__).resolve().parents[2] / "VIDEOS-SHORTS" / "06-dados-ranking-escuro" / "cenas_dr.py"), encoding="utf-8").read()
exec(src[:src.index('scene("dr_barras"')])

# selo (pílula) verde/vermelho com ✔ / ✘ desenhado em SVG (sem depender de glifo)
SELO = r'''const SELO=(txt,ok,fs)=>{fs=fs||46;const d=document.createElement("div");const c=ok?"#22b357":"#e43b3b";
const ic=ok?`<svg width="${fs}" height="${fs}" viewBox="0 0 40 40"><circle cx="20" cy="20" r="19" fill="#fff"/><path d="M11 21l6 6 12-14" stroke="${c}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>`:`<svg width="${fs}" height="${fs}" viewBox="0 0 40 40"><circle cx="20" cy="20" r="19" fill="#fff"/><path d="M13 13l14 14M27 13L13 27" stroke="${c}" stroke-width="5" stroke-linecap="round"/></svg>`;
d.innerHTML=`<span style="white-space:nowrap">${txt}</span>`+ic;d.style.cssText=`position:absolute;display:flex;align-items:center;gap:${Math.round(fs*.3)}px;padding:${Math.round(fs*.22)}px ${Math.round(fs*.42)}px;border-radius:${fs}px;background:${c};color:#fff;font:700 ${fs}px/1 Oswald,Inter;text-transform:uppercase;box-shadow:0 8px 26px rgba(0,0,0,.55);z-index:5`;return d};
const POP=(el,t,rot)=>{tl.fromTo(el,{opacity:0,scale:.4,rotation:0},{opacity:1,scale:1,rotation:rot||0,duration:.4,ease:"back.out(2.2)",immediateRender:false},t);tl.set(el,{opacity:0},0)};
const CARD=(src,w,ry,rx,rw)=>{const d=document.createElement("div");d.style.cssText=`position:absolute;width:${w}px;border-radius:14px;overflow:hidden;box-shadow:0 18px 50px rgba(0,0,0,.7);background:#fff`;
d.innerHTML=`<img src="${src}" style="display:block;width:100%">`;const h=document.createElement("div");h.className="hlr";
h.style.cssText=`position:absolute;left:${((rx||.08)-.045)*100}%;width:${(rw||.6)*100}%;top:${(ry-.065)*100}%;height:13%;border:${Math.max(3,Math.round(w/150))}px solid #ff2a2a;border-radius:10px;box-shadow:0 0 22px rgba(255,40,40,.75),inset 0 0 18px rgba(255,40,40,.25);background:rgba(255,40,40,.08)`;d.appendChild(h);return d};'''

# ---------------------------------------------------------------- pessoa: foto + selos + card eleitoral
scene("dr_pessoa",
 '{"titulo":"NOME","sub":"","icone":"","foto":"","card":"","ry":0.7,"rx":0.08,"rw":0.6,"t_l":0,"t_card":0,"t_red":0,"selo_red":"LINHA VERMELHA","pulsos":[],"t_q":0,"q":""}',
 f'<div id="{{{{id}}}}" style="position:absolute;inset:0;font-family:Inter,Arial,sans-serif;color:#fff">{HEAD}<div class="st" style="position:absolute;inset:0"></div></div>',
 HEADJS + SELO + r'''
const st=document.querySelector(id+" .st");
const fr=document.createElement("div");fr.style.cssText="position:absolute;left:230px;top:410px;width:620px;height:470px;border-radius:30px;overflow:hidden;border:7px solid #F5C518;box-shadow:0 0 50px rgba(245,197,24,.28);background:#222;box-sizing:border-box";
fr.innerHTML=`<img src="${P.foto}" style="width:100%;height:100%;object-fit:cover;object-position:50% 28%">`;st.appendChild(fr);
tl.fromTo(fr,{opacity:0,scale:.82},{opacity:1,scale:1,duration:.55,ease:"back.out(1.5)",immediateRender:false},S+.08);tl.set(fr,{opacity:0},0);
const img=fr.querySelector("img");tl.fromTo(img,{scale:1},{scale:1.08,duration:Math.max(1,D),ease:"none",immediateRender:false},S);
(P.pulsos||[]).forEach(t=>{tl.to(fr,{scale:1.13,duration:.16,ease:"power2.out"},t);tl.to(fr,{scale:1,duration:.4,ease:"elastic.out(1,.5)"},t+.16);});
const s1=SELO("FEZ O L",true,48);s1.style.left="150px";s1.style.top="378px";st.appendChild(s1);POP(s1,P.t_l||S+.4,-5);
if(P.q){const q=SELO(P.q,false,44);q.style.background="#2a2a2e";q.style.border="3px solid #F5C518";q.querySelector("svg").remove();q.style.right="150px";q.style.top="378px";st.appendChild(q);POP(q,P.t_q,4);
  if(P.t_red){tl.to(q,{opacity:0,duration:.2},P.t_red-.25);}}
if(P.card){const c=CARD(P.card,820,P.ry,P.rx,P.rw);c.style.left="130px";c.style.top="840px";st.appendChild(c);
  const tc=P.t_card||S+1.2;tl.fromTo(c,{opacity:0,y:700},{opacity:1,y:0,duration:.7,ease:"power3.out",immediateRender:false},tc);tl.set(c,{opacity:0},0);
  const h=c.querySelector(".hlr"),tr=P.t_red||tc+.6;tl.fromTo(h,{opacity:0,scale:1.25},{opacity:1,scale:1,duration:.35,ease:"power3.out",immediateRender:false},tr);tl.set(h,{opacity:0},0);
  tl.to(h,{opacity:.45,duration:.35,yoyo:true,repeat:Math.max(1,Math.floor((S+D-tr-.6)/.7)),ease:"sine.inOut"},tr+.4);
  tl.fromTo(c,{scale:1},{scale:1.05,duration:.35,ease:"power2.out",immediateRender:false},tr);
  const s2=SELO(P.selo_red||"LINHA VERMELHA",false,46);s2.style.right="150px";s2.style.top="378px";st.appendChild(s2);POP(s2,tr+.1,4);}
''')

# ---------------------------------------------------------------- grade: 4 famosos lado a lado (+ cards mini + contadores)
scene("dr_grade",
 '{"titulo":"","sub":"","icone":"","cols":4,"pessoas":[{"foto":"","nome":"","card":"","ry":0.7,"rx":0.08,"rw":0.6,"t":0}],"t_l":0,"t_cards":0,"t_red":0,"linhas":[{"txt":"","cor":"#fff","t":0,"tam":96}]}',
 f'<div id="{{{{id}}}}" style="position:absolute;inset:0;font-family:Inter,Arial,sans-serif;color:#fff">{HEAD}<div class="st" style="position:absolute;inset:0"></div><div class="ln" style="position:absolute;left:40px;right:40px;display:flex;flex-direction:column;align-items:center;gap:6px"></div></div>',
 HEADJS + SELO + r'''
const st=document.querySelector(id+" .st"),ln=document.querySelector(id+" .ln"),L=P.pessoas||[],C=P.cols||4;
const gap=C==4?22:40,sz=C==4?236:360,x0=(1080-(C*sz+(C-1)*gap))/2,y0=C==4?430:400;let yb=0;
L.forEach((p,i)=>{const cx=x0+(i%C)*(sz+gap),cy=y0+Math.floor(i/C)*(sz+(C==4?0:90));
  const fr=document.createElement("div");fr.style.cssText=`position:absolute;left:${cx}px;top:${cy}px;width:${sz}px;height:${sz}px;border-radius:${C==4?20:28}px;overflow:hidden;border:${C==4?5:7}px solid #F5C518;box-sizing:border-box;background:#222`;
  fr.innerHTML=`<img src="${p.foto}" style="width:100%;height:100%;object-fit:cover;object-position:50% 25%">`;st.appendChild(fr);
  const t=p.t||S+.2+i*.25;tl.fromTo(fr,{opacity:0,y:60,scale:.85},{opacity:1,y:0,scale:1,duration:.5,ease:"back.out(1.6)",immediateRender:false},t);tl.set(fr,{opacity:0},0);
  const nm=document.createElement("div");nm.textContent=p.nome;nm.style.cssText=`position:absolute;left:${cx-20}px;width:${sz+40}px;top:${cy+sz+10}px;text-align:center;font:700 ${C==4?34:46}px/1.05 Oswald,Inter;color:#F5C518;text-transform:uppercase`;st.appendChild(nm);
  tl.fromTo(nm,{opacity:0},{opacity:1,duration:.35,immediateRender:false},t+.15);tl.set(nm,{opacity:0},0);
  if(P.t_l){const s=SELO("L",true,C==4?36:46);s.style.left=(cx+(C==4?8:14))+"px";s.style.top=(cy+(C==4?8:14))+"px";st.appendChild(s);POP(s,P.t_l+i*.12,-6);}
  if(p.card&&P.t_cards){const c=CARD(p.card,sz,p.ry,p.rx,p.rw);c.style.left=cx+"px";c.style.top=(cy+sz+58)+"px";c.style.borderRadius="8px";st.appendChild(c);
    tl.fromTo(c,{opacity:0,y:120},{opacity:1,y:0,duration:.5,ease:"power3.out",immediateRender:false},P.t_cards+i*.12);tl.set(c,{opacity:0},0);
    const h=c.querySelector(".hlr");h.style.borderWidth="4px";const tr=(P.t_red||P.t_cards+.6)+i*.15;tl.fromTo(h,{opacity:0,scale:1.4},{opacity:1,scale:1,duration:.3,immediateRender:false},tr);tl.set(h,{opacity:0},0);
    yb=Math.max(yb,cy+sz+58+sz*.6);}
  yb=Math.max(yb,cy+sz+60);});
ln.style.top=(yb+40)+"px";
(P.linhas||[]).forEach(l=>{if(!l.txt)return;const e=document.createElement("div");e.innerHTML=l.txt;e.style.cssText=`font:700 ${l.tam||96}px/1.02 Oswald,Inter;color:${l.cor||"#fff"};text-transform:uppercase;text-align:center`;ln.appendChild(e);
  tl.fromTo(e,{opacity:0,y:40,scale:.9},{opacity:1,y:0,scale:1,duration:.4,ease:"power3.out",immediateRender:false},l.t);tl.set(e,{opacity:0},0);});
''')

# ---------------------------------------------------------------- cartas: 4 cards eleitorais empilhados -> abrem em grade
scene("dr_cartas",
 '{"titulo":"","sub":"","icone":"","cards":[""],"t_fan":0}',
 f'<div id="{{{{id}}}}" style="position:absolute;inset:0;font-family:Inter,Arial,sans-serif;color:#fff">{HEAD}<div class="st" style="position:absolute;inset:0"></div></div>',
 HEADJS + SELO + r'''
const st=document.querySelector(id+" .st"),K=P.cards||[],w=480,tf=P.t_fan||S+1.5;
K.forEach((src,i)=>{const c=CARD(src,w,.5,.1,.1);c.querySelector(".hlr").remove();c.style.left=(540-w/2)+"px";c.style.top="560px";st.appendChild(c);
  const rot=[-7,5,-3,8][i%4],t=S+.25+i*.22;tl.fromTo(c,{opacity:0,y:500,rotation:rot*2},{opacity:1,y:0,rotation:rot,duration:.55,ease:"power3.out",immediateRender:false},t);tl.set(c,{opacity:0},0);
  const gx=(i%2?1:-1)*(w/2+12),gy=Math.floor(i/2)*330-110;tl.to(c,{x:gx,y:gy,rotation:0,duration:.6,ease:"power3.inOut"},tf+i*.06);});
''')

# ---------------------------------------------------------------- frase gigante tipográfica (+ fotos opcionais)
scene("dr_frase",
 '{"titulo":"","sub":"","icone":"","fotos":[],"t_fotos":0,"linhas":[{"txt":"FRASE","cor":"#fff","t":0,"tam":110}],"pulsos":[]}',
 f'<div id="{{{{id}}}}" style="position:absolute;inset:0;font-family:Inter,Arial,sans-serif;color:#fff">{HEAD}<div class="fx" style="position:absolute;left:50px;right:50px;top:330px;height:960px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px"></div></div>',
 r'''const hd=document.querySelector(id+" .hd");if(!P.titulo){hd.remove();}else{if(P.icone)hd.querySelector(".ic").innerHTML=ICON(P.icone,96);else hd.querySelector(".ic").remove();if(!P.sub)hd.querySelector(".s").remove();
tl.fromTo(hd,{opacity:0,y:-24},{opacity:1,y:0,duration:.5,ease:"power2.out",immediateRender:false},S+.05);tl.set(hd,{opacity:0},0);}
const fx=document.querySelector(id+" .fx");
if((P.fotos||[]).length){const r=document.createElement("div");r.style.cssText="display:flex;gap:18px;margin-bottom:40px";fx.appendChild(r);
  P.fotos.forEach((f,i)=>{const d=FOTO(f,"",170,"#F5C518");r.appendChild(d);tl.fromTo(d,{opacity:0,scale:.6},{opacity:1,scale:1,duration:.4,ease:"back.out(2)",immediateRender:false},(P.t_fotos||S+.1)+i*.12);tl.set(d,{opacity:0},0);});}
(P.linhas||[]).forEach(l=>{const e=document.createElement("div");e.innerHTML=l.txt;e.style.cssText=`font:700 ${l.tam||110}px/1.0 Oswald,Inter;color:${l.cor||"#fff"};text-transform:uppercase;text-align:center;letter-spacing:.01em`;fx.appendChild(e);
  tl.fromTo(e,{opacity:0,y:50,scale:.92},{opacity:1,y:0,scale:1,duration:.42,ease:"power3.out",immediateRender:false},l.t);tl.set(e,{opacity:0},0);});
(P.pulsos||[]).forEach(t=>{tl.to(fx,{scale:1.07,duration:.15,ease:"power2.out"},t);tl.to(fx,{scale:1,duration:.4,ease:"power2.inOut"},t+.15);});
''')
print("ok")
