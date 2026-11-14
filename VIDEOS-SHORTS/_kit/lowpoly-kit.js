// ===== KIT LOW-POLY (Three.js) — casa, árvore, palmeira, carro, rua, boneco, instancing, rótulos e legenda =====
// Uso: const K = LPKIT(THREE);  (inlinado no template.html por _kit/montar.py — não editar a cópia)
function LPKIT(THREE){
const K={};
const clamp=(x,a=0,b=1)=>Math.min(b,Math.max(a,x));
K.clamp=clamp; K.lerp=(a,b,k)=>a+(b-a)*k;
K.sm=k=>{k=clamp(k);return k*k*(3-2*k);};
K.io=k=>{k=clamp(k);return -(Math.cos(Math.PI*k)-1)/2;};
K.seg=(t,a,b)=>K.sm((t-a)/(b-a));
K.back=k=>{k=clamp(k);const c=1.9;return 1+(c+1)*Math.pow(k-1,3)+c*Math.pow(k-1,2);};
K.rng=s=>()=>{s|=0;s=s+0x6D2B79F5|0;let t=Math.imul(s^s>>>15,1|s);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};
K.win=(t,a,b,fi=.3,fo=.25)=>(t<a||t>b)?0:Math.min(K.sm((t-a)/fi),K.sm((b-t)/fo));

// ---------- materiais / primitivas ----------
const MC={};
K.mat=(c,o={})=>{const k=c+JSON.stringify(o);return MC[k]||(MC[k]=new THREE.MeshLambertMaterial(Object.assign({color:c,flatShading:true},o)));};
K.mesh=(geo,c,o)=>{const m=new THREE.Mesh(geo,typeof c==="string"?K.mat(c,o):c);m.castShadow=true;m.receiveShadow=true;return m;};
K.box=(w,h,d,c,x=0,y=0,z=0)=>{const m=K.mesh(new THREE.BoxGeometry(w,h,d),c);m.position.set(x,y,z);return m;};
K.cyl=(rt,rb,h,c,seg=7,x=0,y=0,z=0)=>{const m=K.mesh(new THREE.CylinderGeometry(rt,rb,h,seg),c);m.position.set(x,y,z);return m;};
K.ball=(r,c,det=0,x=0,y=0,z=0)=>{const m=K.mesh(new THREE.IcosahedronGeometry(r,det),c);m.position.set(x,y,z);return m;};

// ---------- cena / luz de dia ----------
K.setup=(canvas,W,H,o={})=>{
  const renderer=new THREE.WebGLRenderer({canvas,antialias:true,preserveDrawingBuffer:true});
  renderer.setPixelRatio(1);renderer.setSize(W,H,false);
  renderer.outputColorSpace=THREE.SRGBColorSpace;
  renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;
  const scene=new THREE.Scene();
  const cv=document.createElement("canvas");cv.width=4;cv.height=512;const g=cv.getContext("2d");
  const gr=g.createLinearGradient(0,0,0,512);gr.addColorStop(0,o.skyTop||"#7cc4f5");gr.addColorStop(.55,o.skyMid||"#cfe9fb");gr.addColorStop(1,o.skyBot||"#fbefdc");
  g.fillStyle=gr;g.fillRect(0,0,4,512);
  const sky=new THREE.CanvasTexture(cv);sky.colorSpace=THREE.SRGBColorSpace;scene.background=sky;
  if(o.fog!==false) scene.fog=new THREE.Fog(o.fogColor||"#f3ecdc",o.fogNear||70,o.fogFar||260);
  const hemi=new THREE.HemisphereLight(o.hemiSky||"#eaf6ff",o.hemiGround||"#8fb86a",o.hemi||1.35);scene.add(hemi);
  const sun=new THREE.DirectionalLight(o.sunColor||"#fff1dc",o.sun||2.1);sun.castShadow=true;
  sun.shadow.mapSize.set(o.shadowMap||2048,o.shadowMap||2048);sun.shadow.radius=5;sun.shadow.bias=-0.0005;sun.shadow.normalBias=0.03;
  const S=o.shadowSize||22;Object.assign(sun.shadow.camera,{left:-S,right:S,top:S,bottom:-S,near:1,far:220});
  scene.add(sun,sun.target);
  const sunOff=new THREE.Vector3(...(o.sunDir||[-30,55,35]));
  const camera=new THREE.PerspectiveCamera(o.fov||38,W/H,0.05,1500);
  const follow=(p)=>{sun.position.copy(p).add(sunOff);sun.target.position.copy(p);sun.target.updateMatrixWorld();};
  follow(new THREE.Vector3());
  return {renderer,scene,camera,sun,hemi,follow};
};

// ---------- textura de texto (placas) ----------
K.textTex=(text,o={})=>{
  const cv=document.createElement("canvas");cv.width=o.w||512;cv.height=o.h||128;
  const tex=new THREE.CanvasTexture(cv);tex.colorSpace=THREE.SRGBColorSpace;tex.anisotropy=4;
  const draw=()=>{const g=cv.getContext("2d");g.fillStyle=o.bg||"#1f5a44";g.fillRect(0,0,cv.width,cv.height);
    if(o.border){g.strokeStyle=o.border;g.lineWidth=10;g.strokeRect(5,5,cv.width-10,cv.height-10);}
    g.fillStyle=o.color||"#ffd34d";g.font=`${o.size||72}px "${o.font||"Lilita One"}", "Arial Black", sans-serif`;
    g.textAlign="center";g.textBaseline="middle";g.fillText(text,cv.width/2,cv.height/2+(o.dy||4));tex.needsUpdate=true;};
  draw();if(document.fonts&&document.fonts.ready)document.fonts.ready.then(draw);
  return tex;
};
K.roadTex=(o={})=>{const cv=document.createElement("canvas");cv.width=64;cv.height=128;const g=cv.getContext("2d");
  g.fillStyle=o.color||"#8a8f99";g.fillRect(0,0,64,128);g.fillStyle=o.line||"#f4f4f4";g.fillRect(29,10,6,60);
  const t=new THREE.CanvasTexture(cv);t.colorSpace=THREE.SRGBColorSpace;t.wrapS=t.wrapT=THREE.RepeatWrapping;t.anisotropy=8;return t;};
// rua reta (eixo X se horiz=true, senão Z), com calçada
K.road=(len,w,o={})=>{const g=new THREE.Group();
  const side=K.mesh(new THREE.PlaneGeometry(o.horiz?len:w+0.5,o.horiz?w+0.5:len),o.walk||"#d9d4c7");side.rotation.x=-Math.PI/2;side.position.y=0.012;g.add(side);
  const tx=K.roadTex(o).clone();tx.needsUpdate=true;
  if(o.horiz){tx.rotation=Math.PI/2;tx.repeat.set(1,len/2.2);}else tx.repeat.set(1,len/2.2);
  const m=new THREE.Mesh(new THREE.PlaneGeometry(o.horiz?len:w,o.horiz?w:len),new THREE.MeshLambertMaterial({map:tx}));
  m.rotation.x=-Math.PI/2;m.position.y=0.02;m.receiveShadow=true;g.add(m);return g;};

// ---------- props ----------
K.house=(o={})=>{const g=new THREE.Group();const w=o.w||1.6,d=o.d||1.4,h=o.h||1.0,rh=o.roofH||0.75;
  const body=K.box(w,h,d,o.wall||"#f6f2ea",0,h/2,0);body.name="wall";g.add(body);
  if(o.flat){const r=K.box(w+0.12,0.12,d+0.12,o.roof||"#c9c4ba",0,h+0.06,0);r.name="roof";g.add(r);
    g.add(K.box(0.42,0.24,0.42,"#9aa0a8",0.25,h+0.24,-0.1));}
  else{const geo=new THREE.ConeGeometry(0.7071,1,4);geo.rotateY(Math.PI/4);const r=K.mesh(geo,o.roof||"#ee7a3a");
    r.scale.set(w*1.18,rh,d*1.18);r.position.y=h+rh/2;r.name="roof";g.add(r);
    g.add(K.box(0.18,0.45,0.18,"#b0563a",w*0.25,h+rh*0.55,-d*0.15));}
  g.add(K.box(0.3,0.52,0.06,o.door||"#8a5634",0,0.26,d/2+0.02));
  const wc=o.glass||"#7ec3ea";
  g.add(K.box(0.3,0.26,0.05,wc,-w*0.3,h*0.58,d/2+0.02));g.add(K.box(0.3,0.26,0.05,wc,w*0.3,h*0.58,d/2+0.02));
  g.add(K.box(0.05,0.26,0.3,wc,w/2+0.02,h*0.58,0));g.add(K.box(0.05,0.26,0.3,wc,-w/2-0.02,h*0.58,0));
  return g;};
K.tree=(o={})=>{const g=new THREE.Group();const s=o.s||1;
  g.add(K.cyl(0.07*s,0.1*s,0.6*s,"#8a5a36",5,0,0.3*s,0));
  const c=K.ball(0.46*s,o.leaf||"#5fbf3f",0,0,0.92*s,0);c.scale.y=1.15;c.name="crown";g.add(c);
  if(o.two){const c2=K.ball(0.3*s,o.leaf||"#5fbf3f",0,0.18*s,1.35*s,0.05);c2.name="crown";g.add(c2);}
  return g;};
K.palm=(o={})=>{const g=new THREE.Group();const s=o.s||1;let x=0,y=0;
  for(let i=0;i<5;i++){const c=K.cyl(0.06*s,0.075*s,0.36*s,"#a9814f",6,x,y+0.18*s,0);c.rotation.z=-0.06*i;g.add(c);x+=0.025*i*s;y+=0.34*s;}
  for(let i=0;i<7;i++){const f=new THREE.Group();f.position.set(x,y,0);f.rotation.y=i/7*Math.PI*2;
    const leaf=K.box(0.85*s,0.03,0.22*s,o.leaf||"#3fae4a",0.42*s,-0.12*s,0);leaf.rotation.z=-0.42;f.add(leaf);g.add(f);}
  g.add(K.ball(0.09*s,"#6b4a2a",0,x,y-0.02,0));return g;};
K.car=(o={})=>{const g=new THREE.Group();
  const b=K.box(0.92,0.26,0.46,o.color||"#e2574c",0,0.21,0);b.name="body";g.add(b);
  g.add(K.box(0.5,0.22,0.42,o.cabin||"#2d3340",-0.06,0.44,0));
  const wg=new THREE.CylinderGeometry(0.1,0.1,0.07,8);wg.rotateX(Math.PI/2);
  for(const [x,z] of [[0.28,0.22],[-0.28,0.22],[0.28,-0.22],[-0.28,-0.22]]){const w=K.mesh(wg,"#1b1d22");w.position.set(x,0.1,z);g.add(w);}
  return g;};
K.lamp=()=>{const g=new THREE.Group();g.add(K.cyl(0.03,0.04,1.4,"#7d838c",5,0,0.7,0));g.add(K.box(0.3,0.05,0.08,"#7d838c",0.13,1.38,0));return g;};
// boneco ORIGINAL: camiseta amarela, calça azul, cabelo castanho
K.person=(o={})=>{const g=new THREE.Group();const shirt=o.shirt||"#ffd23a",pants=o.pants||"#2f5d9a",skin=o.skin||"#f1c19a",hair=o.hair||"#4a2f1c";
  const hip=new THREE.Group();hip.position.y=0.5;g.add(hip);
  const legL=new THREE.Group(),legR=new THREE.Group();legL.position.set(-0.09,0,0);legR.position.set(0.09,0,0);hip.add(legL,legR);
  for(const L of [legL,legR]){if(o.sit){L.add(K.box(0.15,0.16,0.46,pants,0,-0.04,0.2));L.add(K.box(0.15,0.42,0.16,pants,0,-0.25,0.4));L.add(K.box(0.16,0.07,0.24,o.shoe||"#e9e9e9",0,-0.47,0.46));}
    else{L.add(K.box(0.15,0.46,0.16,pants,0,-0.23,0));L.add(K.box(0.16,0.07,0.24,o.shoe||"#e9e9e9",0,-0.47,0.04));}}
  const torso=K.box(0.38,0.44,0.22,shirt,0,0.22,0);torso.name="shirt";hip.add(torso);
  const head=new THREE.Group();head.position.y=0.62;hip.add(head);
  head.add(K.box(0.08,0.06,0.08,skin,0,-0.02,0));
  const hd=K.ball(0.17,skin,1,0,0.15,0);hd.scale.set(1,1.08,1);head.add(hd);
  const hr=K.mesh(new THREE.SphereGeometry(0.182,8,5,0,Math.PI*2,0,Math.PI*0.48),hair);hr.position.set(0,0.17,-0.012);head.add(hr);
  head.add(K.box(0.035,0.045,0.02,"#2a1d14",-0.06,0.16,0.165));head.add(K.box(0.035,0.045,0.02,"#2a1d14",0.06,0.16,0.165));
  const arms=[];for(const sx of [-1,1]){const a=new THREE.Group();a.position.set(0.24*sx,0.4,0);hip.add(a);
    a.add(K.box(0.13,0.17,0.17,shirt,0,-0.07,0));a.add(K.box(0.1,0.3,0.11,skin,0,-0.29,0));arms.push(a);}
  g.userData={hip,head,arms,legL,legR,torso};return g;};

// ---------- instancing (centenas de cópias de um protótipo) ----------
const M2=new THREE.Matrix4();
K.instance=(parent,proto,list,o={})=>{proto.updateMatrixWorld(true);const parts=[];proto.traverse(m=>{if(m.isMesh)parts.push(m);});
  const tmp=new THREE.Matrix4(),q=new THREE.Quaternion(),e=new THREE.Euler(),v=new THREE.Vector3(),sc=new THREE.Vector3(),c=new THREE.Color();
  const ims=parts.map(p=>{const colored=p.name&&list.some(it=>it.colors&&it.colors[p.name]);
    const im=new THREE.InstancedMesh(p.geometry,colored?K.mat("#ffffff"):p.material,list.length);
    im.castShadow=o.cast!==false;im.receiveShadow=true;im.frustumCulled=false;im.userData.local=p.matrixWorld.clone();im.userData.name=p.name;im.userData.base=p.material.color.getHex();im.userData.colored=colored;parent.add(im);return im;});
  const api={meshes:ims,list,n:list.length,
    set(i,x,y,z,ry,sx,sy=sx,sz=sx){q.setFromEuler(e.set(0,ry,0));tmp.compose(v.set(x,y,z),q,sc.set(Math.max(sx,1e-4),Math.max(sy,1e-4),Math.max(sz,1e-4)));
      for(const im of ims)im.setMatrixAt(i,M2.multiplyMatrices(tmp,im.userData.local));},
    done(){for(const im of ims)im.instanceMatrix.needsUpdate=true;}};
  list.forEach((it,i)=>{api.set(i,it.x,it.y||0,it.z,it.ry||0,it.s||1);
    for(const im of ims)if(im.userData.colored)im.setColorAt(i,c.set((it.colors&&it.colors[im.userData.name])||im.userData.base));});
  for(const im of ims)if(im.instanceColor)im.instanceColor.needsUpdate=true;
  api.done();return api;};

// ---------- câmera por chaves ----------
// keys: [{t, p:[x,y,z], l:[x,y,z], fov?}]  — interpola com ease in-out; segura antes/depois
K.camPath=(keys)=>{keys=keys.slice().sort((a,b)=>a.t-b.t);const P=new THREE.Vector3(),L=new THREE.Vector3();
  return (t,cam)=>{let i=0;while(i<keys.length-1&&t>=keys[i+1].t)i++;const a=keys[i],b=keys[Math.min(i+1,keys.length-1)];
    const k=(b===a||t<=a.t)?0:K.io((t-a.t)/(b.t-a.t));
    P.set(K.lerp(a.p[0],b.p[0],k),K.lerp(a.p[1],b.p[1],k),K.lerp(a.p[2],b.p[2],k));
    L.set(K.lerp(a.l[0],b.l[0],k),K.lerp(a.l[1],b.l[1],k),K.lerp(a.l[2],b.l[2],k));
    cam.position.copy(P);cam.lookAt(L);const fa=a.fov||cam.userData.fov0||cam.fov,fb=b.fov||cam.userData.fov0||cam.fov;
    if(!cam.userData.fov0)cam.userData.fov0=cam.fov;const f=K.lerp(fa,fb,k);if(Math.abs(f-cam.fov)>1e-3){cam.fov=f;cam.updateProjectionMatrix();}
    return L;};};
const PV=new THREE.Vector3();
K.project=(v,cam,W,H)=>{PV.copy(v).project(cam);return [(PV.x+1)/2*W,(1-PV.y)/2*H,PV.z];};

// ---------- overlay: rótulos (itens da faixa "rotulos" do edit.json) ----------
// props: text, kind (tag|sticker|pill|big|html), anchor (nome de âncora 3D) ou x/y, dx, dy, size, rot, color, dot
K.outline=(px,c)=>{const s=[];for(let i=0;i<16;i++){const a=i/16*Math.PI*2;s.push(`${(Math.cos(a)*px).toFixed(1)}px ${(Math.sin(a)*px).toFixed(1)}px 0 ${c}`);}return s.join(",");};
K.labels=(root,items,o={})=>{const W=o.W,H=o.H;const els=items.map(it=>{const p=it.props||{};const el=document.createElement("div");
    el.className="lp-lab lp-"+(p.kind||"tag");el.style.position="absolute";el.style.opacity=0;el.style.whiteSpace="pre";el.style.willChange="transform,opacity";
    const sz=p.size||(p.kind==="pill"?40:p.kind==="sticker"?72:p.kind==="big"?120:52);el.style.fontSize=sz+"px";
    if(p.kind==="pill"){el.innerHTML=`<span style="display:inline-block;width:${sz*0.42}px;height:${sz*0.42}px;border-radius:50%;background:${p.dot||"#ff8a1f"};margin-right:${sz*0.3}px;vertical-align:middle;position:relative;top:-${sz*0.06}px"></span>`+p.text;
      Object.assign(el.style,{background:"#fff",color:"#1d2330",borderRadius:"999px",padding:`${sz*0.22}px ${sz*0.55}px`,fontFamily:"'Lilita One',sans-serif",boxShadow:"0 6px 18px rgba(0,0,0,.28)",letterSpacing:".01em"});}
    else if(p.kind==="sticker"||p.kind==="big"){el.textContent=p.text;Object.assign(el.style,{color:p.color||"#ffd21f",fontFamily:"'Lilita One',sans-serif",textShadow:K.outline(sz*0.07,"#1b1b1b")+`,0 ${sz*0.1}px 0 #1b1b1b`,textAlign:"center",lineHeight:1.02});}
    else if(p.kind==="html"){el.innerHTML=p.html||"";el.style.whiteSpace="normal";}
    else{el.textContent=p.text;Object.assign(el.style,{background:p.color||"#ffd21f",color:"#1b1b1b",fontFamily:"'Lilita One',sans-serif",padding:`${sz*0.12}px ${sz*0.32}px`,borderRadius:"8px",border:"4px solid #1b1b1b",boxShadow:"0 6px 0 rgba(0,0,0,.35)",letterSpacing:".02em"});}
    root.appendChild(el);return el;});
  return {els,update(t,proj){items.forEach((it,i)=>{const el=els[i],p=it.props||{};const a=it.start,b=it.start+it.dur;
      if(it.hidden||t<a||t>b){el.style.opacity=0;return;}
      let x=p.x!=null?p.x:W/2,y=p.y!=null?p.y:H/2;
      if(p.anchor&&proj){const r=proj(p.anchor);if(!r||r[2]>1){el.style.opacity=0;return;}x=r[0];y=r[1];}
      x+=p.dx||0;y+=p.dy||0;const w=el.offsetWidth,h=el.offsetHeight;
      let left=x-w/2,top=y-h/2;left=clamp(left,36,W-36-w);top=clamp(top,o.safeTop||230,(o.safeBot||H-390)-h);
      const kin=K.back((t-a)/0.32),op=Math.min(K.sm((t-a)/0.18),K.sm((b-t)/0.22));
      el.style.left=left+"px";el.style.top=top+"px";el.style.opacity=op;
      el.style.transform=`rotate(${p.rot||0}deg) scale(${0.55+0.45*kin})`;});}};};

// ---------- overlay: legenda ----------
// props: words [{w,s,e}], mode "frase"|"palavra", per_group, size, y, font, color, stroke, maxw
K.captions=(root,it,o={})=>{const p=it.props||{};const W=o.W;const ws=p.words||[];const mode=p.mode||"palavra";
  const groups=[];if(mode==="palavra"){ws.forEach(w=>{let txt=w.w.replace(/[.,!?;:]+$/,"").replace(/^[“"']+|[”"']+$/g,"");if(p.cap!==false)txt=txt.charAt(0).toUpperCase()+txt.slice(1);groups.push({t:txt,s:w.s,e:w.e});});}
  else{let g=[];const per=p.per_group||7;ws.forEach((w,i)=>{g.push(w);const nx=ws[i+1];if(/[.!?,;:]$/.test(w.w)||g.length>=per||!nx){groups.push({t:g.map(x=>x.w).join(" "),s:g[0].s,e:g[g.length-1].e});g=[];}});}
  groups.forEach((g,i)=>{const nx=groups[i+1];g.s=Math.max(0,g.s-0.05);g.e=nx?Math.min(nx.s-0.05,g.e+(mode==="palavra"?0.5:0.9)):g.e+0.9;if(nx&&nx.s-0.05-g.e<0.25)g.e=nx.s-0.05;});
  const el=document.createElement("div");const sz=p.size||64;
  Object.assign(el.style,{position:"absolute",left:"50%",top:(p.y||1300)+"px",transform:"translate(-50%,-50%)",width:(p.maxw||920)+"px",textAlign:"center",
    fontFamily:`'${p.font||"Lilita One"}',sans-serif`,fontWeight:p.weight||400,fontSize:sz+"px",lineHeight:1.12,color:p.color||"#fff",
    textShadow:K.outline(sz*(p.stroke_k||0.075),p.stroke||"#141414")+`,0 ${sz*0.08}px ${sz*0.12}px rgba(0,0,0,.45)`,opacity:0,pointerEvents:"none"});
  root.appendChild(el);let cur=-1;
  return {groups,update(t){if(it.hidden||t<it.start||t>it.start+it.dur){el.style.opacity=0;return;}
    let k=-1;for(let i=0;i<groups.length;i++){if(t>=groups[i].s&&t<groups[i].e){k=i;break;}}
    if(k<0){el.style.opacity=0;return;}if(k!==cur){el.textContent=groups[k].t;cur=k;}
    const u=(t-groups[k].s);el.style.opacity=1;el.style.transform=`translate(-50%,-50%) scale(${mode==="palavra"?0.82+0.18*K.back(u/0.16):0.92+0.08*K.back(u/0.2)})`;}};};
return K;}
