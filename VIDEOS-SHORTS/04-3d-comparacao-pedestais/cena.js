// ===== cena 04: dois pedestais BRASIL x EUA, objetos low-poly + pilhas de moedas (= horas de trabalho) =====
const PX={br:-1.6,us:1.6}, TOP=0.55, PW=2.4, PD=2.2;
const COR={br:PARAM("cor_br","#E3C595"),us:PARAM("cor_us","#A493E6")};
const NOME={br:PARAM("nome_br","BRASIL"),us:PARAM("nome_us","EUA")};
const SIDE={};
for(const s of ["br","us"]){
  const g=new THREE.Group(); g.position.x=PX[s]; scene.add(g);
  const ped=add(box(PW,TOP,PD,M(COR[s],{roughness:.6}),0.06),g); ped.position.y=TOP/2;
  const base=add(box(PW+0.25,0.08,PD+0.25,M("#232327",{roughness:.4,metalness:.3}),0.03),g); base.position.y=0.04;
  const lab=textPlane(NOME[s],2.0,0.42,{cor:s==="br"?"#4a3922":"#ffffff",font:"900 150px Arial Black, Arial, sans-serif"}); lab.position.set(0,TOP*0.5,PD/2+0.012); g.add(lab);
  // pilha de moedas (instanced)
  const N=48, coin=new THREE.InstancedMesh(new THREE.CylinderGeometry(0.4,0.4,0.07,28),M("#E9B44C",{metalness:.65,roughness:.32}),N);
  coin.castShadow=true; coin.receiveShadow=true; coin.count=0; g.add(coin);
  const jit=[]; for(let i=0;i<N;i++) jit.push([(R()-.5)*.05,(R()-.5)*.05,R()*6]);
  SIDE[s]={g,coin,N,jit,objs:{},stackH:0,objH:0};
}
const mk={};
mk.iphone=(s)=>{const g=new THREE.Group();
  const b=add(box(0.58,1.18,0.09,M("#1d1d23",{metalness:.55,roughness:.3}),0.07),g); b.position.y=0.59;
  const sc=new THREE.Mesh(new THREE.PlaneGeometry(0.5,1.06),M("#0e1c33",{emissive:"#16294a",emissiveIntensity:.6,roughness:.2})); sc.position.set(0,0.59,0.047); g.add(sc);
  const isl=new THREE.Mesh(new THREE.PlaneGeometry(0.16,0.045),M("#000")); isl.position.set(0,1.07,0.048); g.add(isl);
  g.rotation.y=s==="br"?0.18:-0.18; g.userData.h=1.18; return g;};
mk.burger=(s)=>{const g=new THREE.Group(); let y=0;
  const L=(m,h)=>{m.position.y=y+h/2; y+=h; add(m,g);};
  L(cyl(.46,.42,.16,M("#d8994c")),.16); L(cyl(.5,.5,.13,M("#5b3320",{roughness:.8})),.13);
  const ch=add(box(.92,.04,.92,M("#f4c431")),g); ch.position.y=y+.02; ch.rotation.y=.6; y+=.04;
  L(cyl(.52,.52,.05,M("#58b84b")),.05);
  const top=add(new THREE.Mesh(new THREE.SphereGeometry(.48,32,16,0,Math.PI*2,0,Math.PI/2),M("#e3a253")),g); top.scale.y=.75; top.position.y=y;
  g.userData.h=y+.36; return g;};
mk.bomba=(s)=>{const g=new THREE.Group(); const c=s==="br"?"#F2B630":"#B3A4F0";
  const b=add(box(.62,1.15,.46,M(c),0.05),g); b.position.y=.575;
  const tp=add(box(.7,.1,.52,M("#2b2b30"),0.03),g); tp.position.y=1.2;
  const d=new THREE.Mesh(new THREE.PlaneGeometry(.44,.26),M("#111",{emissive:"#2be07a",emissiveIntensity:.35})); d.position.set(0,.9,.232); g.add(d);
  const h=add(new THREE.Mesh(new THREE.TorusGeometry(.32,.035,10,30,Math.PI*1.2),M("#1b1b1f")),g); h.position.set(.36,.5,0); h.rotation.set(0,Math.PI/2,-.4);
  const nz=add(box(.08,.26,.12,M("#222")),g); nz.position.set(.4,.78,.1);
  g.userData.h=1.25; return g;};
mk.carro=(s)=>{const g=new THREE.Group(); const c=s==="br"?"#F2B630":"#B3A4F0";
  const b=add(box(1.55,.34,.78,M(c,{metalness:.25,roughness:.35}),0.1),g); b.position.y=.34;
  const cab=add(box(.82,.3,.7,M("#2a2f3a",{metalness:.3,roughness:.2}),0.08),g); cab.position.set(-.05,.62,0);
  for(const [x,z] of [[-.5,.4],[.5,.4],[-.5,-.4],[.5,-.4]]){const w=add(cyl(.18,.18,.12,M("#141416")),g); w.rotation.x=Math.PI/2; w.position.set(x,.18,z);}
  g.rotation.y=s==="br"?.35:-.35; g.userData.h=.8; return g;};
mk.relogio=(s)=>{const g=new THREE.Group();
  const f=add(cyl(.46,.46,.1,M("#f3f3f5",{roughness:.4})),g); f.rotation.x=Math.PI/2; f.position.y=.62;
  const r=add(new THREE.Mesh(new THREE.TorusGeometry(.47,.05,12,40),M("#2a2a30",{metalness:.5,roughness:.3})),g); r.position.y=.62;
  const st=add(cyl(.05,.08,.18,M("#2a2a30")),g); st.position.y=.09;
  const h1=new THREE.Mesh(new THREE.BoxGeometry(.04,.26,.02),M("#111")); h1.geometry.translate(0,.12,0); h1.position.set(0,.62,.07); g.add(h1);
  const h2=new THREE.Mesh(new THREE.BoxGeometry(.03,.36,.02),M("#d33")); h2.geometry.translate(0,.17,0); h2.position.set(0,.62,.08); g.add(h2);
  g.userData.hands=[h1,h2]; g.userData.h=1.1; return g;};
mk.hospital=(s)=>{const g=new THREE.Group();
  const b=add(box(1.0,.85,.8,M("#f2f2f4"),0.04),g); b.position.y=.425;
  const rf=add(box(1.1,.08,.9,M("#c9c9cf"),0.02),g); rf.position.y=.89;
  const cx=new THREE.Mesh(new THREE.BoxGeometry(.32,.1,.02),M("#e5484d")); cx.position.set(0,.55,.41); g.add(cx);
  const cy=new THREE.Mesh(new THREE.BoxGeometry(.1,.32,.02),M("#e5484d")); cy.position.set(0,.55,.41); g.add(cy);
  const dr=new THREE.Mesh(new THREE.PlaneGeometry(.26,.32),M("#3a3a44")); dr.position.set(0,.16,.402); g.add(dr);
  g.userData.h=.95; return g;};
mk.capelo=(s)=>{const g=new THREE.Group();
  const b=add(cyl(.26,.3,.24,M("#1a1a1e")),g); b.position.y=.12;
  const t=add(box(.78,.05,.78,M("#1f1f24"),0.01),g); t.position.y=.26; t.rotation.y=.785;
  const ts=new THREE.Mesh(new THREE.BoxGeometry(.03,.26,.03),M("#F2B630")); ts.position.set(.36,.15,0); g.add(ts);
  g.userData.h=.32; return g;};

// objetos de cada rodada (track "cena": props.objeto, br, us, max, br_t, us_t, us2, us2_t)
const RONDAS=byTrack("cena");
const OBJPOS={iphone:[0,.5],burger:[0,.5],bomba:[0,.5],carro:[0,.55],relogio:[0,.55],hospital:[-.42,-.15],capelo:[.72,.55]};
RONDAS.forEach((r,ri)=>{r._o={br:[],us:[]};
  const lista=(r.props.objeto==="ladob")?{br:[],us:["hospital","capelo"]}:(r.props.objeto==="resumo")?{br:[],us:["iphone","hospital","capelo"]}:{br:[r.props.objeto],us:[r.props.objeto]};
  for(const s of ["br","us"]) for(const nm of lista[s]){ if(!mk[nm]) continue; const o=mk[nm](s);
    let [ox,oz]=OBJPOS[nm]; if(r.props.objeto==="resumo"&&nm==="iphone"){ox=.15;oz=.6;} if(r.props.objeto==="resumo"&&nm==="hospital"){ox=-.55;}
    o.position.set(ox,TOP,oz); o.visible=false; SIDE[s].g.add(o); r._o[s].push({nm,o,t:(nm==="hospital"?r.props.hosp_t:nm==="capelo"?r.props.cap_t:null)});}});

function stackCount(r,s,t){const p=r.props; const v=p[s]; if(v===undefined||v===null) return 0;
  const mx=p.max||Math.max(p.br||0,p.us||0,p.us2||0)||1, grow=p.cresce||1.1;
  let n=SIDE[s].N*(v/mx)*io((t-(p[s+"_t"]??r.start))/grow);
  if(s==="us"&&p.us2) n=lerp(n,SIDE[s].N*(p.us2/mx),io((t-p.us2_t)/grow));
  const out=1-seg(t,r.start+r.dur-0.3,r.start+r.dur);
  return Math.round(n*out);}

const dummy=new THREE.Object3D();
cenaUpdate=(t)=>{
  let r=null; for(const x of RONDAS) if(t>=x.start&&t<x.start+x.dur) r=x;
  RONDAS.forEach(x=>{for(const s of ["br","us"]) for(const ob of x._o[s]) ob.o.visible=false;});
  for(const s of ["br","us"]){const S=SIDE[s]; S.objH=0;
    const n=r?stackCount(r,s,t):0; S.coin.count=n;
    for(let i=0;i<n;i++){const j=S.jit[i]; dummy.position.set(j[0],TOP+0.035+i*0.072,-0.38+j[1]); dummy.rotation.set(0,j[2],0); dummy.updateMatrix(); S.coin.setMatrixAt(i,dummy.matrix);}
    S.coin.instanceMatrix.needsUpdate=true; S.stackH=n*0.072;
    if(!r) continue;
    for(const ob of r._o[s]){const t0=ob.t??r.start; if(t<t0) continue;
      const k=back((t-t0)/0.45)*(1-seg(t,r.start+r.dur-0.25,r.start+r.dur)); if(k<=0.001) continue;
      ob.o.visible=true; ob.o.scale.setScalar(Math.max(0.001,k)); ob.o.rotation.y+=0; S.objH=Math.max(S.objH,(ob.o.userData.h||1)*k);
      if(ob.o.userData.hands){const [h1,h2]=ob.o.userData.hands; h1.rotation.z=-t*0.5; h2.rotation.z=-t*3.2;}}
  }
};
ANCH.br_top=()=>new THREE.Vector3(PX.br,TOP+Math.max(SIDE.br.stackH,SIDE.br.objH)+0.28,-0.1);
ANCH.us_top=()=>new THREE.Vector3(PX.us,TOP+Math.max(SIDE.us.stackH,SIDE.us.objH)+0.28,-0.1);
ANCH.br=()=>new THREE.Vector3(PX.br,TOP+1.5,0);
ANCH.us=()=>new THREE.Vector3(PX.us,TOP+1.5,0);
ANCH.hosp=()=>new THREE.Vector3(PX.us-0.45,TOP+1.15,-0.15);
ANCH.cap=()=>new THREE.Vector3(PX.us+0.72,TOP+0.55,0.55);
