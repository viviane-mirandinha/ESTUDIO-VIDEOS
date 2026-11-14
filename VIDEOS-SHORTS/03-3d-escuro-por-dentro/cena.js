// ===== cena 03: bomba de gasolina por dentro (bico em corte, tanque, cânister de carvão, motor) =====
const EV=(id,d=0)=>(ED[id]&&!ED[id].hidden)?ED[id]:{start:d,dur:0.01};
const AMAR="#F2B630";
const metal=M("#b9bdc6",{metalness:.85,roughness:.28,side:THREE.DoubleSide});
const escuro=M("#3d4048",{metalness:.4,roughness:.5,side:THREE.DoubleSide});
const borracha=M("#17171a",{roughness:.85});
const gasMat=M(AMAR,{emissive:"#7a4f00",emissiveIntensity:.35,roughness:.35});
const halfCyl=(r,h,mat)=>new THREE.Mesh(new THREE.CylinderGeometry(r,r,h,40,1,true,Math.PI/2,Math.PI),mat);
function orient(m,a,b){const d=new THREE.Vector3().subVectors(b,a); m.position.copy(a).addScaledVector(d,.5);
  m.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),d.clone().normalize()); return d.length();}

// ---------------- SET A: bomba + carro (x ~ 12..17) ----------------
const A=new THREE.Group(); A.position.x=12; scene.add(A);
{const pb=add(box(1.3,3.0,.9,M("#e9e9ec",{roughness:.45}),0.06),A); pb.position.y=1.5;
 const fx=add(box(1.32,.28,.92,M("#FF8A2B"),0.02),A); fx.position.y=.55;
 const tp=add(box(1.45,.18,1.0,M("#2a2a30"),0.03),A); tp.position.y=3.06;
 const sc=new THREE.Mesh(new THREE.PlaneGeometry(.9,.55),M("#120c04",{emissive:"#3a2400",emissiveIntensity:.6})); sc.position.set(0,2.35,.452); A.add(sc);
 for(let i=0;i<9;i++){const k=add(box(.16,.12,.05,M("#2b2b31"),0.02),A); k.position.set(-.22+(i%3)*.22,1.75-Math.floor(i/3)*.17,.47);}
 const lt=add(box(.08,.08,.04,M("#FF8A2B",{emissive:"#FF8A2B",emissiveIntensity:1.2})),A); lt.position.set(.5,2.75,.46);}
// carro (lateral virada pra câmera)
const carro=new THREE.Group(); carro.position.set(2.6,0,-.3); A.add(carro);
{const b=add(box(4.4,1.15,1.9,M("#2f5fb0",{metalness:.55,roughness:.25}),0.25),carro); b.position.set(1.4,.95,0);
 const cab=add(box(2.4,.85,1.7,M("#1d2a40",{metalness:.4,roughness:.15}),0.22),carro); cab.position.set(1.6,1.85,0);
 for(const x of [.2,2.7]){const w=add(cyl(.42,.42,.3,borracha,28),carro); w.rotation.x=Math.PI/2; w.position.set(x,.42,.9);}
 const door=new THREE.Mesh(new THREE.PlaneGeometry(.34,.34),M("#0c0c0e")); door.position.set(-.35,1.3,.953); carro.add(door);
 const lamp=add(box(.1,.18,.5,M("#ff3b30",{emissive:"#ff2010",emissiveIntensity:.8})),carro); lamp.position.set(-.79,1.15,.55);}
// bico (handle + bico) no tanque do carro
const bicoA=new THREE.Group(); A.add(bicoA);
{const h=add(box(.75,.26,.22,borracha,0.08),bicoA); h.position.set(-.35,0,0);
 const gr=add(box(.18,.42,.2,borracha,0.06),bicoA); gr.position.set(-.55,-.25,0);
 const lv=add(box(.5,.05,.12,M("#FF8A2B"),0.02),bicoA); lv.position.set(-.3,-.2,0); bicoA.userData.lv=lv;
 const sp=add(cyl(.05,.05,.55,metal,16),bicoA); sp.rotation.z=Math.PI/2-.25; sp.position.set(.22,-.06,0);}
// mangueira bomba -> bico
const hoseCurve=new THREE.CatmullRomCurve3([new THREE.Vector3(.66,2.0,.2),new THREE.Vector3(.85,1.0,.5),new THREE.Vector3(1.0,.3,.75),new THREE.Vector3(1.2,.35,.9),new THREE.Vector3(1.3,.95,.85),new THREE.Vector3(1.3,1.25,.75)]);
let hoseMesh=add(new THREE.Mesh(new THREE.TubeGeometry(hoseCurve,60,.07,10),borracha),A);
// luz de faixa no chão
{const st=new THREE.Mesh(new THREE.BoxGeometry(3,.02,.08),M("#FF8A2B",{emissive:"#FF8A2B",emissiveIntensity:2})); st.position.set(1.6,.01,1.6); A.add(st);}

// ---------------- SET B: tanque em corte + bico em corte (x ~ -2..3) ----------------
const B=new THREE.Group(); scene.add(B);
const TK={x0:-1.8,x1:1.6,y0:.1,y1:2.1,z:.8}; const TL_MAX=1.45;
{const w=TK.x1-TK.x0, h=TK.y1-TK.y0, cx=(TK.x0+TK.x1)/2, cy=(TK.y0+TK.y1)/2;
 const back=add(box(w,h,.06,escuro),B); back.position.set(cx,cy,-TK.z);
 const bot=add(box(w,.06,TK.z*2,escuro),B); bot.position.set(cx,TK.y0,0);
 const top=add(box(w,.06,TK.z*2,escuro),B); top.position.set(cx,TK.y1,0);
 const l=add(box(.06,h,TK.z*2,escuro),B); l.position.set(TK.x0,cy,0);
 const r=add(box(.06,h,TK.z*2,escuro),B); r.position.set(TK.x1,cy,0);
 // bordas do corte (laranja fino)
 for(const [x,y,ww,hh] of [[cx,TK.y0,w,.04],[cx,TK.y1,w,.04],[TK.x0,cy,.04,h],[TK.x1,cy,.04,h]]){const e=new THREE.Mesh(new THREE.BoxGeometry(ww,hh,.02),M("#FF8A2B",{emissive:"#FF8A2B",emissiveIntensity:.8})); e.position.set(x,y,TK.z); B.add(e);}}
const gasTank=add(box(TK.x1-TK.x0-.1,1,TK.z*2-.1,gasMat),B); gasTank.position.x=(TK.x0+TK.x1)/2;
// espaço de cima (destaque)
const domo=new THREE.Mesh(new THREE.BoxGeometry(TK.x1-TK.x0-.12,TK.y1-TL_MAX-.06,TK.z*2-.12),new THREE.MeshBasicMaterial({color:"#7fd3ff",transparent:true,opacity:0,depthWrite:false}));
domo.position.set((TK.x0+TK.x1)/2,(TK.y1+TL_MAX)/2,0); B.add(domo);
// conector + gargalo (boca)
const NX=2.3, NY0=1.05, NY1=3.6, NR=.3;
{const c=add(halfCyl(.22,NX-TK.x1,escuro),B); c.rotation.z=Math.PI/2; c.position.set((NX+TK.x1)/2,1.25,0);
 const n=add(halfCyl(NR,NY1-NY0,escuro),B); n.position.set(NX,(NY0+NY1)/2,0);
 const rim=add(new THREE.Mesh(new THREE.TorusGeometry(NR,.04,10,40),M("#FF8A2B",{emissive:"#FF8A2B",emissiveIntensity:.6})),B); rim.rotation.x=Math.PI/2; rim.position.set(NX,NY1,0);}
const gasCon=add(cyl(.2,.2,NX-TK.x1,gasMat,20),B); gasCon.rotation.z=Math.PI/2; gasCon.position.set((NX+TK.x1)/2,1.25,0);
const gasNeck=add(cyl(NR-.03,NR-.03,1,gasMat,28),B); gasNeck.position.x=NX;
// bico em corte
const PA=new THREE.Vector3(2.75,5.8,0), PB=new THREE.Vector3(2.3,2.75,0), AX=new THREE.Vector3().subVectors(PB,PA).normalize();
const SR=.14;
{const s=add(halfCyl(SR,1,metal),B); s.scale.y=orient(s,PA,PB);
 const tipRing=add(new THREE.Mesh(new THREE.TorusGeometry(SR,.025,8,30),metal),B); tipRing.position.copy(PB); tipRing.quaternion.setFromUnitVectors(new THREE.Vector3(0,0,1),AX);}
// tubinho de ar (sensor) por dentro do bico
const PERP=new THREE.Vector3(AX.y,-AX.x,0).normalize(); // perpendicular no plano
const HOLE=PB.clone().addScaledVector(AX,-.12).addScaledVector(PERP,SR*.8);
const TUBE_TOP=PA.clone().addScaledVector(PERP,SR*.75).addScaledVector(AX,-.05);
{const t=add(cyl(.035,.035,1,M("#7fd3ff",{emissive:"#2a7ab0",emissiveIntensity:.6,transparent:true,opacity:.85}),12),B); t.scale.y=orient(t,HOLE,TUBE_TOP);}
const furo=new THREE.Mesh(new THREE.TorusGeometry(.065,.02,8,24),M("#FF8A2B",{emissive:"#FF6A00",emissiveIntensity:1.5})); furo.position.copy(HOLE); furo.lookAt(HOLE.clone().add(new THREE.Vector3(0,0,1))); B.add(furo);
// câmara da válvula + mola + cabo
const CH=PA.clone().add(new THREE.Vector3(.05,.45,0));
{const bk=add(box(1.0,.85,.06,escuro),B); bk.position.set(CH.x,CH.y,-.28);
 for(const [dx,dy,w,h] of [[0,.42,1.0,.05],[0,-.42,1.0,.05],[-.5,0,.05,.85],[.5,0,.05,.85]]){const e=add(box(w,h,.56,escuro),B); e.position.set(CH.x+dx,CH.y+dy,0);}
 const hd=add(box(1.9,.5,.5,borracha,0.12),B); hd.position.set(CH.x+1.4,CH.y+.1,0);
 const gr=add(box(.36,.9,.46,borracha,0.1),B); gr.position.set(CH.x+2.05,CH.y-.45,0);
 const lv=add(box(1.1,.08,.2,M("#FF8A2B"),0.03),B); lv.position.set(CH.x+1.45,CH.y-.45,0);}
const valv=add(cyl(.2,.2,.06,M("#FF8A2B",{emissive:"#a03a00",emissiveIntensity:.5}),28),B);
const helix=[]; for(let i=0;i<=120;i++){const a=i/120*Math.PI*2*6; helix.push(new THREE.Vector3(Math.cos(a)*.12,i/120,Math.sin(a)*.12));}
const mola=add(new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(helix),240,.018,6),M("#d8dbe2",{metalness:.9,roughness:.25})),B);
const MOLA_TOP=CH.y+.38;

// ---------------- SET C: mangueira de vapor, cânister de carvão, motor (x ~ -8..-1) ----------------
const ventCurve=new THREE.CatmullRomCurve3([new THREE.Vector3(-1.2,2.1,0),new THREE.Vector3(-1.25,3.0,0),new THREE.Vector3(-2.4,3.45,0),new THREE.Vector3(-3.7,3.2,0),new THREE.Vector3(-4.4,2.75,0)]);
add(new THREE.Mesh(new THREE.TubeGeometry(ventCurve,80,.11,14,false),new THREE.MeshStandardMaterial({color:"#9aa3b5",transparent:true,opacity:.28,roughness:.2,depthWrite:false})),scene);
const liqGeo=new THREE.TubeGeometry(ventCurve,80,.075,10,false); const liq=add(new THREE.Mesh(liqGeo,gasMat),scene); liq.geometry.setDrawRange(0,0);
const CN={x:-4.6,y0:.25,y1:2.6,w:1.5,d:1.0};
{const cx=CN.x, cy=(CN.y0+CN.y1)/2, h=CN.y1-CN.y0;
 const bk=add(box(CN.w,h,.06,escuro),scene); bk.position.set(cx,cy,-CN.d/2);
 for(const [dx,y,w,hh] of [[0,CN.y0,CN.w,.06],[0,CN.y1,CN.w,.06]]){const e=add(box(w,hh,CN.d,escuro),scene); e.position.set(cx+dx,y,0);}
 for(const dx of [-CN.w/2,CN.w/2]){const e=add(box(.06,h,CN.d,escuro),scene); e.position.set(cx+dx,cy,0);}
 const gl=new THREE.Mesh(new THREE.PlaneGeometry(CN.w,h),new THREE.MeshStandardMaterial({color:"#a8c4ff",transparent:true,opacity:.08,roughness:.05,depthWrite:false})); gl.position.set(cx,cy,CN.d/2); scene.add(gl);
 const p1=add(cyl(.09,.09,.3,escuro,12),scene); p1.position.set(cx+.2,CN.y1+.12,0);}
const coalMat=M("#1d1d20",{roughness:.9,flatShading:true});
const NCO=170, coal=new THREE.InstancedMesh(new THREE.IcosahedronGeometry(.14,0),coalMat,NCO); coal.castShadow=true; scene.add(coal);
{const R2=rng(77),d=new THREE.Object3D(); for(let i=0;i<NCO;i++){d.position.set(CN.x+(R2()-.5)*(CN.w-.3),CN.y0+.2+R2()*(CN.y1-CN.y0-.45),(R2()-.5)*(CN.d-.3)); d.rotation.set(R2()*3,R2()*3,R2()*3); d.scale.setScalar(.8+R2()*.6); d.updateMatrix(); coal.setMatrixAt(i,d.matrix);}}
const motorCurve=new THREE.CatmullRomCurve3([new THREE.Vector3(CN.x-.75,1.0,0),new THREE.Vector3(-5.9,1.05,.1),new THREE.Vector3(-6.5,1.2,.1)]);
add(new THREE.Mesh(new THREE.TubeGeometry(motorCurve,30,.08,10),new THREE.MeshStandardMaterial({color:"#9aa3b5",transparent:true,opacity:.3,depthWrite:false})),scene);
{const mb=add(box(1.4,1.3,1.2,M("#5a5e66",{metalness:.6,roughness:.4}),0.08),scene); mb.position.set(-7.2,.75,0);
 for(let i=0;i<3;i++){const c=add(cyl(.15,.15,.35,M("#7a7f88",{metalness:.7,roughness:.3})),scene); c.position.set(-7.6+i*.4,1.55,0);} }
const fogo=new THREE.PointLight("#ff7a1a",0,4); fogo.position.set(-7.2,1.2,.9); scene.add(fogo);

// ---------------- partículas ----------------
const NP=70, gasP=new THREE.InstancedMesh(new THREE.SphereGeometry(.045,10,8),gasMat,NP); scene.add(gasP);
const NAR=26, arP=new THREE.InstancedMesh(new THREE.SphereGeometry(.03,8,6),new THREE.MeshBasicMaterial({color:"#dff4ff"}),NAR); scene.add(arP);
const NV=48, vapP=new THREE.InstancedMesh(new THREE.SphereGeometry(.07,10,8),new THREE.MeshStandardMaterial({color:"#e6ecf5",transparent:true,opacity:.75,emissive:"#8090a0",emissiveIntensity:.3}),NV); scene.add(vapP);
const dm=new THREE.Object3D(); const PR=rng(91); const pj=[]; for(let i=0;i<120;i++) pj.push([PR(),(PR()-.5),(PR()-.5)]);
const hide=(im,i)=>{dm.position.set(0,-50,0); dm.scale.setScalar(.001); dm.updateMatrix(); im.setMatrixAt(i,dm.matrix);};
for(const im of [gasP,arP,vapP,coal]) im.frustumCulled=false;
const HOLE_OUT=HOLE.clone().addScaledVector(PERP,.35).addScaledVector(AX,.15);

cenaUpdate=(t)=>{
  const fl=EV("c_fluxo"), ar=EV("c_ar"), so=EV("c_sobe"), mo=EV("c_mola"), va=EV("c_vapor"), mt=EV("c_motor"), lq=EV("c_liquido"), en=EV("c_encharca"), es=EV("c_espaco"), ti=EV("c_tira"), ck=EV("c_clique");
  // nível: tanque sobe durante o fluxo, depois o gargalo enche até o furo
  const kT=lerp(.55,1,seg(t,fl.start,so.start));
  const lvl=lerp(.2,TL_MAX,kT); gasTank.scale.y=lvl-TK.y0-.05; gasTank.position.y=TK.y0+.03+(lvl-TK.y0-.05)/2;
  const kN=seg(t,so.start,so.start+so.dur); const nTop=lerp(NY0,PB.y+.22,kN);
  gasNeck.visible=kN>0.001; gasNeck.scale.y=Math.max(.001,nTop-NY0); gasNeck.position.y=(NY0+nTop)/2; gasCon.visible=kT>.97;
  // espaço de cima pisca
  domo.material.opacity=(t>=es.start&&t<es.start+es.dur)?.18+.12*Math.sin((t-es.start)*6):0;
  // furo pulsa
  furo.scale.setScalar(1+.35*Math.max(0,Math.sin(t*5))*(t<so.start+so.dur?1:.2));
  // válvula + mola
  const kv=seg(t,mo.start,mo.start+.35); const vy=lerp(CH.y+.05,CH.y-.3,kv);
  valv.position.set(CH.x-.02,vy,0); mola.position.set(CH.x-.02,vy,0); mola.scale.y=MOLA_TOP-vy;
  // gasolina descendo no bico
  const flowOn=clamp(seg(t,fl.start,fl.start+.4)*(1-seg(t,mo.start+.2,mo.start+.6)));
  const L=PA.distanceTo(PB);
  for(let i=0;i<NP;i++){ if(flowOn<=0.01){hide(gasP,i);continue;}
    const u=((pj[i][0]+(t-fl.start)*1.1)%1.25); let p;
    if(u<1){p=PA.clone().addScaledVector(AX,u*L).addScaledVector(PERP,pj[i][1]*SR*.9); p.z+=pj[i][2]*.12;}
    else {p=PB.clone().addScaledVector(PERP,pj[i][1]*.15); p.y-=(u-1)*4; if(p.y<nTop){hide(gasP,i);continue;}}
    dm.position.copy(p); dm.scale.setScalar(flowOn); dm.updateMatrix(); gasP.setMatrixAt(i,dm.matrix);}
  gasP.instanceMatrix.needsUpdate=true;
  // ar entrando pelo furo e subindo pelo tubinho
  const arOn=(t>=ar.start&&t<ar.start+ar.dur)?1:0; const arStop=ar.start+ar.dur;
  for(let i=0;i<NAR;i++){ if(t<ar.start||t>arStop+0.8){hide(arP,i);continue;}
    const tt=Math.min(t,arStop); const u=((pj[i][0]+(tt-ar.start)*.5)%1);
    const p= u<.15 ? HOLE_OUT.clone().lerp(HOLE,u/.15) : HOLE.clone().lerp(TUBE_TOP,(u-.15)/.85);
    dm.position.copy(p); dm.scale.setScalar(arOn?1:1-seg(t,arStop,arStop+.8)); dm.updateMatrix(); arP.setMatrixAt(i,dm.matrix);}
  arP.instanceMatrix.needsUpdate=true;
  // vapor: tanque -> cânister (fica preso), depois cânister -> motor
  for(let i=0;i<NV;i++){ if(t<va.start||t>va.start+va.dur+mt.dur+1.5){hide(vapP,i);continue;}
    const u=clamp((t-va.start)*.35-pj[i][0]*.9,0,1); let p;
    if(t<mt.start||i%2){ if(u<=0){hide(vapP,i);continue;} p=u<1?ventCurve.getPointAt(u):new THREE.Vector3(CN.x+pj[i][1]*1.1,1.4+pj[i][2]*1.6,pj[i][0]*.5-.25);}
    else {const w=((pj[i][0]+(t-mt.start)*.6)%1); p=motorCurve.getPointAt(w);}
    dm.position.copy(p); dm.scale.setScalar(.6+.4*pj[i][0]); dm.updateMatrix(); vapP.setMatrixAt(i,dm.matrix);}
  vapP.instanceMatrix.needsUpdate=true;
  fogo.intensity=(t>=mt.start&&t<mt.start+mt.dur)?6+3*Math.sin(t*20):0;
  // líquido sobe a mangueira e encharca o carvão
  const kl=seg(t,lq.start,lq.start+lq.dur); const rs=10*6; liq.geometry.setDrawRange(0,Math.floor(kl*80)*rs);
  coalMat.color.set("#1d1d20").lerp(new THREE.Color("#c9962a"),seg(t,en.start,en.start+en.dur));
  // bico no carro: clique + tirar o bico
  const kc=Math.exp(-Math.max(0,t-ck.start)*8)*(t>=ck.start?1:0); bicoA.userData.lv.rotation.z=.25*kc;
  const kt=seg(t,ti.start,ti.start+.9);
  bicoA.position.set(1.8-kt*.3,1.36+kt*1.0+kc*.03,.75+kt*.9); bicoA.rotation.set(0,kt*.6,.15-kt*.5);
};
ANCH.lcd=()=>new THREE.Vector3(12,2.75,.45);
ANCH.bicoA=()=>bicoA.position.clone().add(new THREE.Vector3(12,.4,0));
ANCH.furo=()=>HOLE.clone().add(new THREE.Vector3(.0,.12,0));
ANCH.tubo=()=>HOLE.clone().lerp(TUBE_TOP,.45).add(new THREE.Vector3(.12,0,0));
ANCH.mola=()=>new THREE.Vector3(CH.x,CH.y+.5,0);
ANCH.boca=()=>new THREE.Vector3(NX,NY1+.15,0);
ANCH.espaco=()=>new THREE.Vector3(-.1,TK.y1+.12,0);
ANCH.mangueira=()=>ventCurve.getPointAt(.45).add(new THREE.Vector3(0,.15,0));
ANCH.canister=()=>new THREE.Vector3(CN.x,CN.y1+.35,0);
ANCH.motor=()=>new THREE.Vector3(-7.2,1.95,0);
