// ===== CENA 12: relógio de corda por dentro — 3D clay/low-poly em palco escuro =====
// Eventos lidos pelo id dos itens da track "cena" (tempos vêm do words.json via gerar_edit.py).
const EV=id=>{const i=ED[id];return (i&&!i.hidden)?[i.start,i.start+i.dur]:[1e9,1e9+1];};
const pulse=(t,id,fi=.25,fo=.35)=>{const [a,b]=EV(id);return (t<a||t>b)?0:Math.min(sm((t-a)/fi),sm((b-t)/fo));};
const CL=(c,o={})=>{const {em,...r}=o;return M(c,Object.assign({roughness:.8,metalness:0,emissive:new THREE.Color(em||"#ffd23f"),emissiveIntensity:0},r));};
const BRASS="#f2b54a",BRASS2="#f0a03a",STEEL="#cfd7e4",RUBY="#ff3d64",PLATE="#232838";
const glow=(m,v)=>{m.emissiveIntensity=v;};

// luz de palco no chão
{const c=document.createElement("canvas");c.width=c.height=256;const x=c.getContext("2d");
 const g=x.createRadialGradient(128,128,0,128,128,128);g.addColorStop(0,"rgba(110,130,255,.32)");g.addColorStop(1,"rgba(0,0,0,0)");
 x.fillStyle=g;x.fillRect(0,0,256,256);const tx=new THREE.CanvasTexture(c);
 const sp=new THREE.Mesh(new THREE.PlaneGeometry(18,18),new THREE.MeshBasicMaterial({map:tx,transparent:true,depthWrite:false,blending:THREE.AdditiveBlending}));
 sp.rotation.x=-Math.PI/2;sp.position.y=0.01;scene.add(sp);}
const fill=new THREE.PointLight(0xffe2b0,18,30,1.6); fill.position.set(2,6,6); scene.add(fill);

// ---------- engrenagem (shape extrudado, borda arredondada = cara de massinha) ----------
function gearGeo(r,n,th,hole=0,spokes=0,hook=false){
  const s=new THREE.Shape(), rr=r*(hook?0.74:0.86), da=Math.PI*2/n;
  for(let i=0;i<n;i++){const a0=i*da;
    const pts=hook?[[rr,a0],[r,a0+da*0.62],[r*0.94,a0+da*0.74],[rr,a0+da*0.8]]:[[rr,a0],[r,a0+da*0.22],[r,a0+da*0.5],[rr,a0+da*0.72]];
    pts.forEach(([R1,a],k)=>{const x=Math.cos(a)*R1,y=Math.sin(a)*R1;(i===0&&k===0)?s.moveTo(x,y):s.lineTo(x,y);});}
  s.closePath();
  if(hole>0){const h=new THREE.Path();h.absarc(0,0,hole,0,Math.PI*2,true);s.holes.push(h);}
  else if(spokes>0){for(let k=0;k<spokes;k++){const a=k/spokes*Math.PI*2+Math.PI/spokes,c=r*0.5,hr=r*0.21;
    const h=new THREE.Path();h.absarc(Math.cos(a)*c,Math.sin(a)*c,hr,0,Math.PI*2,true);s.holes.push(h);}}
  const g=new THREE.ExtrudeGeometry(s,{depth:th,bevelEnabled:true,bevelThickness:.02,bevelSize:.016,bevelSegments:2,curveSegments:hole>0?48:14});
  g.translate(0,0,-th/2); return g;}
const RUB=[], WM=[];
function wheel(x,y,z,r,n,col,{pin=0.15,pinN=8,th=.1,spokes=4,hole=0,hook=false,ruby=true}={}){
  const g=new THREE.Group(); g.position.set(x,y,z); scene.add(g);
  const mat=CL(col);
  add(new THREE.Mesh(gearGeo(r,n,th,hole,spokes,hook),mat),g);
  if(pin>0){const p=add(new THREE.Mesh(gearGeo(pin,pinN,.14),CL(STEEL)),g);p.position.z=-0.13;}
  const ar=add(cyl(.045,.045,.5,CL(STEEL),12),g); ar.rotation.x=Math.PI/2;
  if(ruby){const rb=add(new THREE.Mesh(new THREE.SphereGeometry(.075,16,12),CL(RUBY,{em:RUBY,roughness:.35})),g);rb.position.z=.27;RUB.push(rb);}
  WM.push(mat); return {g,mat};}

// ---------- caixa, suporte, platina ----------
const C0=new THREE.Vector3(0,3.4,0);
const caseM=CL(BRASS2,{roughness:.62});
const cas=add(new THREE.Mesh(new THREE.TorusGeometry(2.8,.3,18,72),caseM)); cas.position.copy(C0);
const plate=add(cyl(2.62,2.62,.16,CL(PLATE),64)); plate.rotation.x=Math.PI/2; plate.position.set(0,3.4,-.28);
// perlage (bolinhas na platina) só pra textura
for(let i=0;i<46;i++){const a=R()*Math.PI*2, rr=0.3+R()*2.1; const d=add(cyl(.12,.12,.02,CL("#2b3144"),10)); d.rotation.x=Math.PI/2; d.position.set(Math.cos(a)*rr,3.4+Math.sin(a)*rr,-.19);}
const stand=add(box(2.4,.36,1.3,CL("#262b38"),.12)); stand.position.set(0,.18,0);
const neck=add(box(.7,.5,.5,CL("#262b38"),.1)); neck.position.set(0,.5,0);
// coroa
const CROWN=new THREE.Group(); CROWN.position.set(3.25,3.4,0); scene.add(CROWN);
{const k=add(cyl(.36,.36,.42,CL(BRASS,{flatShading:true}),14),CROWN); k.rotation.z=Math.PI/2; k.position.x=.15;
 const st=add(cyl(.11,.11,.5,CL(STEEL),10),CROWN); st.rotation.z=Math.PI/2; st.position.x=-.25;}

// ---------- tambor + mola real ----------
const BX=-1.05,BY=3.0;
const BAR=new THREE.Group(); BAR.position.set(BX,BY,0); scene.add(BAR);
const barM=CL(BRASS); WM.unshift(barM);
add(new THREE.Mesh(gearGeo(.95,64,.2,.8),barM),BAR);
{const f=add(cyl(.8,.8,.04,CL("#5a4630"),48),BAR); f.rotation.x=Math.PI/2; f.position.z=-.08;}
const springM=CL(STEEL,{roughness:.5});
const SPR=new THREE.Mesh(undefined,springM); SPR.castShadow=true; SPR.position.set(BX,BY,.02); scene.add(SPR);
{const ar=add(cyl(.13,.13,.36,CL(STEEL),16)); ar.rotation.x=Math.PI/2; ar.position.set(BX,BY,0);}
const springCache={};
function springGeo(k){const q=Math.round(clamp(k)*40)/40; if(springCache[q]) return springCache[q];
  const N=7,steps=460,pts=[], rIn=lerp(.55,.17,q), rOut=lerp(.77,.4,q);
  for(let i=0;i<=steps;i++){const u=i/steps,a=u*N*Math.PI*2; let r;
    if(u<.04) r=lerp(.14,rIn,u/.04); else if(u>.95) r=lerp(rOut,.78,(u-.95)/.05); else r=lerp(rIn,rOut,(u-.04)/.91);
    pts.push(new THREE.Vector3(Math.cos(a)*r,Math.sin(a)*r,0));}
  return springCache[q]=new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts),steps,.021,5,false);}

// ---------- trem de engrenagens ----------
const W2=wheel(0,3.4,.03,.62,48,BRASS,{pin:.16});       // roda central (leva os ponteiros)
const W3=wheel(.76,3.4,.08,.5,40,BRASS,{pin:.14});
const W4=wheel(.87,4.01,.03,.42,36,BRASS,{pin:.12});
const ESC=wheel(.61,4.46,.1,.38,15,"#7fd1ff",{pin:.1,spokes:3,hook:true});
// ponteiro sobre a roda central (aparece em "leva os ponteiros")
const HAND=new THREE.Group(); HAND.position.set(0,3.4,.5); scene.add(HAND);
const handM=CL("#ffffff",{transparent:true,opacity:0,em:"#ffffff"});
{const h=add(box(.12,1.9,.06,handM,.03),HAND); h.position.y=.85; const c=add(cyl(.14,.14,.08,handM,20),HAND); c.rotation.x=Math.PI/2;}

// ---------- âncora ----------
const PX=.05,PY=4.78;
const PAL=new THREE.Group(); PAL.position.set(PX,PY,.22); scene.add(PAL);
const palM=CL("#a7b4c8");
add(box(.95,.09,.08,palM,.03),PAL).position.x=.32;
add(box(.86,.08,.07,palM,.03),PAL).position.x=-.43;
{const s1=add(box(.08,.2,.1,CL(RUBY,{em:RUBY})),PAL); s1.position.set(.37,-.07,0);
 const s2=add(box(.08,.2,.1,CL(RUBY,{em:RUBY})),PAL); s2.position.set(.75,-.07,0);
 add(box(.06,.18,.07,palM),PAL).position.set(-.84,.07,0); add(box(.06,.18,.07,palM),PAL).position.set(-.84,-.07,0);
 const rb=add(new THREE.Mesh(new THREE.SphereGeometry(.07,16,12),CL(RUBY,{em:RUBY,roughness:.35})),PAL); rb.position.z=.1; RUB.push(rb);}
WM.push(palM);
// ---------- volante + espiral ----------
const BAX=-.95,BAY=4.78;
const BAL=new THREE.Group(); BAL.position.set(BAX,BAY,.12); scene.add(BAL);
const balM=CL("#ffcf5a");
add(new THREE.Mesh(new THREE.TorusGeometry(.68,.065,12,56),balM),BAL);
add(box(1.36,.07,.05,balM),BAL); add(box(.07,1.36,.05,balM),BAL);
for(let k=0;k<4;k++){const a=k*Math.PI/2+Math.PI/4; add(new THREE.Mesh(new THREE.SphereGeometry(.06,10,8),CL(STEEL)),BAL).position.set(Math.cos(a)*.68,Math.sin(a)*.68,0);}
{const st=add(cyl(.05,.05,.45,CL(STEEL),12),BAL); st.rotation.x=Math.PI/2;
 const rb=add(new THREE.Mesh(new THREE.SphereGeometry(.07,16,12),CL(RUBY,{em:RUBY,roughness:.35})),BAL); rb.position.z=.26; RUB.push(rb);}
WM.push(balM);
const hairM=CL("#8fb8ff",{roughness:.4,em:"#8fb8ff"});
const HAIR=new THREE.Group(); HAIR.position.set(BAX,BAY,.24); scene.add(HAIR);
{const pts=[];for(let i=0;i<=300;i++){const u=i/300,a=u*6*Math.PI*2,r=.06+.34*u;pts.push(new THREE.Vector3(Math.cos(a)*r,Math.sin(a)*r,0));}
 add(new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts),300,.013,4,false),hairM),HAIR);}

// ---------- mostrador (abre e fecha) ----------
const DIAL=new THREE.Group(); DIAL.position.set(0,3.4,.34); scene.add(DIAL);
const dialMats=[];
const DM=(c,o={})=>{const m=CL(c,Object.assign({transparent:true},o));dialMats.push(m);return m;};
{const d=add(cyl(2.58,2.58,.09,DM("#f2e7d0"),72),DIAL); d.rotation.x=Math.PI/2;
 for(let i=0;i<12;i++){const a=i/12*Math.PI*2, big=i%3===0; const m=add(box(big?.16:.09,big?.5:.3,.06,DM("#262a35"),.02),DIAL);
   m.position.set(Math.sin(a)*2.1,Math.cos(a)*2.1,.07); m.rotation.z=-a;}
 const lg=new THREE.Mesh(new THREE.PlaneGeometry(1.6,.4),new THREE.MeshBasicMaterial({transparent:true,opacity:0}));DIAL.add(lg);}
const HH=new THREE.Group(),MH=new THREE.Group(),SH=new THREE.Group(); [HH,MH,SH].forEach((g,i)=>{g.position.z=.1+i*.04;DIAL.add(g);});
add(box(.16,1.25,.05,DM("#262a35"),.02),HH).position.y=.5;
add(box(.11,1.95,.05,DM("#262a35"),.02),MH).position.y=.85;
add(box(.045,2.15,.04,DM("#ff3d64")),SH).position.y=.75;
{const c=add(cyl(.16,.16,.1,DM("#ff3d64"),20),DIAL); c.rotation.x=Math.PI/2; c.position.z=.24;}

// ---------- âncoras dos rótulos ----------
const A=(x,y,z)=>()=>new THREE.Vector3(x,y,z);
Object.assign(ANCH,{barrel:A(BX,BY+.2,.3),barrelEdge:A(BX-.6,BY-.7,.2),crown:A(3.35,3.75,0),w2:A(0,3.4,.4),w3:A(.76,3.4,.2),
  w4:A(.87,4.3,.2),escape:A(.61,4.7,.2),pallet:A(PX+.3,PY+.12,.25),balance:A(BAX,BAY+.72,.15),hair:A(BAX,BAY+.15,.3),
  ruby:A(.76,3.6,.35),dialTop:A(0,6.25,.3),center:A(0,3.4,.3),hand:A(0,4.6,.5)});

// ---------- animação ----------
const FB=1.1, F8=4.0; // volante: 1,1 Hz "câmera lenta"; 4 Hz real (8 alternâncias/s) no trecho "oito vezes"
function ovl(t,[a,b]){return Math.max(0,Math.min(t,b)-a);}
cenaUpdate=(t)=>{
  const p=FB*t+(F8-FB)*ovl(t,EV("c_oito"));
  const [pa,pb]=EV("c_problema");
  const free=Math.min(sm((t-pa)/.4),1-sm((t-pb)/.3));   // escape "removido"
  const extra=34*ovl(t,[pa,pb]);
  const p2=p*2, n=Math.floor(p2), fr=p2-n, steps=n+sm(fr/.18);
  const aE=-(Math.PI*2/15)*steps-extra;
  ESC.g.rotation.z=aE; const a4=-.238*aE; W4.g.rotation.z=a4; const a3=-.24*a4; W3.g.rotation.z=a3; const a2=-.226*a3; W2.g.rotation.z=a2;
  const aB=-.168*a2; BAR.rotation.z=aB;
  // mola
  const [ca,cb]=EV("c_corda"), [sa]=EV("c_solta"), [ea]=EV("c_escape");
  let k=.2+.8*seg(t,ca,cb);
  if(t>sa) k=lerp(1,.88,seg(t,sa,pa));
  if(t>pa) k=lerp(.88,0,seg(t,pa,pb));
  if(t>ea-.2) k=lerp(.85,.72,seg(t,ea-.2,DUR)) ;
  if(t>ea-.2&&t<ea+.5) k=lerp(0,.85,seg(t,ea-.2,ea+.5));
  SPR.geometry=springGeo(k); SPR.rotation.z=aB-k*5.5;
  CROWN.rotation.x=seg(t,ca,cb)*Math.PI*7;
  glow(springM,.6*pulse(t,"c_energia")+.35*pulse(t,"c_corda"));
  glow(barM,.25*pulse(t,"c_energia"));
  // fila de engrenagens acendendo em sequência
  const [fa,fb]=EV("c_fila");
  WM.forEach((m,i)=>{if(m===palM||m===balM) return; const s0=fa+i*.32; glow(m,(t>=s0&&t<fb)?.55*Math.min(sm((t-s0)/.2),1-sm((t-fb+.4)/.4))*(.6+.4*Math.sin((t-s0)*9)):0);});
  const eg=pulse(t,"c_escape"); glow(ESC.mat,Math.max(ESC.mat.emissiveIntensity,.5*eg)); glow(palM,.45*pulse(t,"c_ancora")); glow(balM,.45*pulse(t,"c_volante"));
  glow(hairM,.9*pulse(t,"c_espiral")+.15);
  // volante / âncora / espiral
  const amp=2.4*(1-free), ph=Math.PI*2*p;
  BAL.rotation.z=amp*Math.sin(ph);
  PAL.rotation.z=(1-free)*.11*Math.tanh(4*Math.cos(ph))+free*.32;
  HAIR.rotation.z=.3*amp*Math.sin(ph); HAIR.scale.setScalar(1+.05*(1-free)*Math.sin(ph));
  // rubis
  const rp=pulse(t,"c_rubis"); RUB.forEach((r,i)=>{r.material.emissiveIntensity=rp*(1.1+.5*Math.sin(t*6+i)); r.scale.setScalar(1+.6*rp);});
  // ponteiro preso na roda central
  const [ha]=EV("c_ponteiros"), [fe]=EV("c_fecha");
  handM.opacity=pulse(t,"c_ponteiros",.4,.5); HAND.visible=handM.opacity>.01; HAND.rotation.z=a2;
  // mostrador
  const [oa]=EV("c_abre");
  const vis=seg(t,oa,oa+1.5)*(1-seg(t,fe,fe+1.5));
  DIAL.position.set(0,3.4+vis*2.8,.34+vis*7); DIAL.rotation.x=-vis*1.0; DIAL.visible=vis<.98;
  const op=1-sm(vis*1.3); dialMats.forEach(m=>m.opacity=op);
  SH.rotation.z=-Math.floor(t*8)/8*Math.PI*2/60; MH.rotation.z=-(.62+t/600)*Math.PI*2; HH.rotation.z=-(.32+t/7200)*Math.PI*2;
};
