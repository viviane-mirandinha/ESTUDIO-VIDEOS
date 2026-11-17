// cenas_base.js — biblioteca de cenas REUTILIZÁVEIS do kit animacao-2d (copiadas sem alteração do projeto 101 + famílias novas por roteiro).

// Usada pelo estilo 'animacao-filosofica' da fábrica: o preencher.py copia isto para <pasta>/cenas.js e acrescenta as cenas do roteiro.

const UI='font-family="Segoe UI,Arial,sans-serif"';

const tt=(P,i,d)=>((P.t&&P.t[i]!=null)?P.t[i]:d);

const ZENAO={tunica:"#e9e2cf",faixa:"#2f6f73",capa:"#245a63",cabelo:"#2a211b",barba:"#2a211b",pele:"#c99a73",pele2:"#b4845c",louro:false};

const CRATES={tunica:"#8c7c5c",faixa:"#6b5c42",capa:"#5e5040",cabelo:"#5a5048",barba:"#756a5c",pele:"#cfa57c",pele2:"#b88f66",louro:false};

const LIVREIRO={tunica:"#d9cdb0",faixa:"#8a5a3a",capa:null,cabelo:"#c9c9c9",barba:"#dcdcdc",pele:"#d6a981",pele2:"#bf8f66",louro:false,barriga:10};

const EPICTETO={tunica:"#bdb5a2",faixa:"#8d4f46",capa:null,cabelo:"#d9d9d9",barba:"#e4e4e4",pele:"#d7a77d",pele2:"#bf8c62",louro:false};

const linhasTxt=(txt,x,y,sz,cor)=>String(txt).split("\n").map((s,i)=>`<text x="${x}" y="${y+i*sz*1.05}" text-anchor="middle" font-family="CaveatX" font-weight="700" font-size="${sz}" fill="${cor||'#3a2e22'}">${s}</text>`).join("");

const xRisco=(x,y,r)=>`<g class="xr"><path class="xa" pathLength="1" d="M${x-r} ${y-r} L${x+r} ${y+r}" stroke="#c0302f" stroke-width="12" stroke-linecap="round" stroke-dasharray="1" stroke-dashoffset="1"/><path class="xb" pathLength="1" d="M${x+r} ${y-r} L${x-r} ${y+r}" stroke="#c0302f" stroke-width="12" stroke-linecap="round" stroke-dasharray="1" stroke-dashoffset="1"/></g>`;

const desenhaX=(id,sel,t)=>{ tl.fromTo(`#${id} ${sel} .xa`,{strokeDashoffset:1},{strokeDashoffset:0,duration:.25,ease:"power2.out"},t); tl.fromTo(`#${id} ${sel} .xb`,{strokeDashoffset:1},{strokeDashoffset:0,duration:.25,ease:"power2.out"},t+.22); };

const SENECA={tunica:"#f1ebe0",faixa:"#6a2f6e",capa:"#e4dccb",cabelo:"#a9a9a9",barba:"#b8b8b8",pele:"#d9ab82",pele2:"#c3946b",louro:false,barriga:6};

const quemSVG=(id,q,o)=>{ if(q==="voce") return moderno(id,{genero:"f",...o});
  if(q==="homem") return moderno(id,{genero:"m",pele:"#d9a77f",pele2:"#c18f68",cabelo:"#2d2420",cabeloLuz:"#4b3a32",camisa:"#f2eadb",jaqueta:"#8fa27a",jaqueta2:"#74885f",calca:"#c9b38a",...o});
  const base={marco:{},zenao:ZENAO,epicteto:EPICTETO,seneca:SENECA,crates:CRATES,livreiro:LIVREIRO}[q]||{}; return pessoa(id,{...base,...o}); };

const checkSVG=(x,y,cls)=>`<path class="${cls}" pathLength="1" d="M${x} ${y} l26 30 l50 -64" stroke="#3d6a5a" stroke-width="14" fill="none" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="1" stroke-dashoffset="1"/>`;

CENAS.titulo=(id,S,D,P)=>{ const sc=raiz(id); const r=rng(3);
  const po=[...Array(14)].map(()=>`<circle class="po" cx="${380+r()*520}" cy="${120+r()*440}" r="${1.5+r()*2.5}" fill="#f3dca0" opacity=".5"/>`).join("");
  sc.insertAdjacentHTML("afterbegin",`<svg viewBox="0 0 1280 720">${bgNoite(id)}<polygon class="spot" points="560,0 720,0 960,640 320,640" fill="#f3dca0" opacity=".13"/>${po}${lado(id+"m",{x:640,y:620,escala:1.1})}</svg>`);
  sc.appendChild(el(P.titulo,"ttl",`top:70px;font-size:84px;line-height:1.1`));
  parado(id+"m",S,D);
  if(P.sub) sc.appendChild(el(P.sub,"hand",`left:0;top:170px;width:1280px;text-align:center;font-size:54px;color:#e9dcc0;opacity:0`));
  if(P.sub) aparece(`#${id} .hand`,S+1.8,.7);
  tl.fromTo(`#${id}m .head`,{rotation:0,svgOrigin:"0 0"},{rotation:-3,svgOrigin:"0 0",duration:D,ease:"sine.inOut"},S);
  tl.fromTo(`#${id} .ttl`,{opacity:0,y:24,letterSpacing:"0.4em"},{opacity:1,y:0,letterSpacing:"0.14em",duration:1.2,ease:"power2.out"},S+.4);
  tl.fromTo(`#${id} .spot`,{opacity:0},{opacity:.13,duration:1},S);
  tl.fromTo(`#${id} .po`,{y:0},{y:-36,duration:1.8,yoyo:true,repeat:1,ease:"sine.inOut",stagger:.07},S); };

CENAS.varanda=(id,S,D,P)=>{ const sc=raiz(id);
  sc.insertAdjacentHTML("afterbegin",`<svg viewBox="0 0 1280 720">${bgVarandaFundo(id)}${costas(id+"m",{x:640,y:722,escala:1.2})}${varandaFrente(id)}
   <g class="aves" opacity=".8" fill="none" stroke="#3a2e22" stroke-width="3" stroke-linecap="round"><path d="M200 210 q14 -14 28 0 q14 -14 28 0"/><path d="M270 170 q10 -10 20 0 q10 -10 20 0"/></g></svg>`);
  parado(id+"m",S,D);
  tl.fromTo(`#${id}m .head`,{rotation:0,svgOrigin:"0 0"},{rotation:6,svgOrigin:"0 0",duration:D*.5,yoyo:true,repeat:1,ease:"sine.inOut"},S+.6);
  tl.fromTo(`#${id} .aves`,{x:0},{x:700,duration:D,ease:"none"},S); camera(id,S,D,1,1.05,640,420); };

CENAS.citacao=(id,S,D,P)=>{ const sc=raiz(id);
  sc.insertAdjacentHTML("afterbegin",`<svg viewBox="0 0 1280 720"><defs><radialGradient id="${id}f" cx=".5" cy=".5" r=".75"><stop offset="0" stop-color="#6a4e32"/><stop offset="1" stop-color="#1a120b"/></radialGradient></defs><rect width="1280" height="720" fill="url(#${id}f)"/>
   <g><rect x="230" y="190" width="820" height="340" fill="#eadcb8" ${OL(4)}/><ellipse cx="230" cy="360" rx="26" ry="170" fill="#d8c79c" ${OL(4)}/><ellipse cx="1050" cy="360" rx="26" ry="170" fill="#d8c79c" ${OL(4)}/>
   <path d="M290 250 h700 M290 470 h700" stroke="#b9a67f" stroke-width="2" opacity=".7"/></g></svg>`);
  sc.appendChild(el(P.frase,"hand",`left:260px;top:290px;width:760px;text-align:center;font-size:${P.tam||96}px;white-space:normal;line-height:1.05;color:#2e2216;opacity:1;clip-path:inset(0 100% 0 0)`));
  tl.to(`#${id} .hand`,{clipPath:"inset(0 0% 0 0)",duration:Math.min(2.0,D-.8),ease:"none"},S+.4); };

CENAS.retrato=(id,S,D,P)=>{ const sc=raiz(id);
  sc.insertAdjacentHTML("afterbegin",`<svg viewBox="0 0 1280 720">${bgPapel(id,!!P.quente)}<circle cx="640" cy="360" r="300" fill="#fff6dc" opacity=".55"/><circle cx="640" cy="360" r="300" fill="none" stroke="#c9b38a" stroke-width="5"/>${quemSVG(id+"m",P.quem||"marco",{x:640,y:700,escala:1.35})}</svg>`);
  if(P.nome) sc.appendChild(el(P.nome,"hand",`left:0;top:20px;width:1280px;text-align:center;font-size:104px;color:#3a2e22`));
  if(P.sub) sc.appendChild(el(P.sub,"hand",`left:0;top:${P.nome?118:60}px;width:1280px;text-align:center;font-size:64px;color:#6b4a2c`));
  parado(id+"m",S,D); gesto(id+"m","B",S+tt(P,0,.8),-70,.8);
  { const hs=[...sc.querySelectorAll(".hand")]; let k=0; if(P.nome) aparece(hs[k++],S+tt(P,0,.6),.6); if(P.sub) aparece(hs[k++],S+tt(P,P.nome?1:0,P.nome?1.8:.8),.6); } };

CENAS.listaChar=(id,S,D,P)=>{ const sc=raiz(id); const it=P.items||[]; const pos=it.length<=2?[[900,340],[1120,340]]:[[790,260],[1060,260],[790,500],[1060,500]];
  sc.insertAdjacentHTML("afterbegin",`<svg viewBox="0 0 1280 720">${bgPapel(id,true)}${quemSVG(id+"m",P.quem||"marco",{x:340,y:700,escala:1.3})}${it.map((o,i)=>`<g transform="translate(${pos[i][0]},${pos[i][1]})"><g class="ti" opacity="0">${ic(o.ic,0,0,1.15)}${linhasTxt(o.txt,0,112,44)}</g></g>`).join("")}</svg>`);
  parado(id+"m",S,D); [...sc.querySelectorAll(".ti")].forEach((e,i)=>tl.fromTo(e,{opacity:0,y:18,scale:.85,svgOrigin:"0 0"},{opacity:1,y:0,scale:1,svgOrigin:"0 0",duration:.45,ease:"back.out(1.8)"},S+tt(P,i,.8+i*1.6))); };

CENAS.riscados=(id,S,D,P)=>{ const sc=raiz(id); const it=P.items||[], n=it.length, gap=Math.min(300,1180/n), e=n<=3?1.9:(n===4?1.6:1.35), fz=n<=3?52:(n===4?46:40), y=P.y||300;
  const g=it.map((o,i)=>{ const x=640+(i-(n-1)/2)*gap; return `<g class="ri ri${i}" opacity="0">${ic(o.ic,x,y,e)}${linhasTxt(o.txt,x,y+110+30*e,fz)}${o.x?xRisco(x,y,60*e/1.9*1.3):""}${o.ok?checkSVG(x+30,y-70,"ck"):""}</g>`; }).join("");
  sc.insertAdjacentHTML("afterbegin",`<svg viewBox="0 0 1280 720">${bgPapel(id,true)}${g}</svg>`);
  it.forEach((o,i)=>{ const t=tt(P,i,.6+i*1.5); tl.fromTo(`#${id} .ri${i}`,{opacity:0,y:16},{opacity:1,y:0,duration:.4,ease:"back.out(1.8)"},S+t-.4); if(o.x) desenhaX(id,`.ri${i}`,S+t+.3); if(o.ok) tl.fromTo(`#${id} .ri${i} .ck`,{strokeDashoffset:1},{strokeDashoffset:0,duration:.35,ease:"power2.out"},S+t+.3); }); };

CENAS.cartao=(id,S,D,P)=>{ const sc=raiz(id);
  sc.insertAdjacentHTML("afterbegin",`<svg viewBox="0 0 1280 720"><defs><radialGradient id="${id}f" cx=".5" cy=".45" r=".8"><stop offset="0" stop-color="#4b4843"/><stop offset="1" stop-color="#171513"/></radialGradient><filter id="${id}n"><feTurbulence type="fractalNoise" baseFrequency=".02" numOctaves="3" seed="9"/><feColorMatrix values="0 0 0 0 .2  0 0 0 0 .19  0 0 0 0 .17  0 0 0 .35 0"/></filter></defs>
   <rect width="1280" height="720" fill="url(#${id}f)"/><rect width="1280" height="720" filter="url(#${id}n)"/>${P.ic?`<g class="cic" opacity="0">${ic(P.ic,640,170,2.0)}</g>`:""}</svg>`);
  if(P.l1) sc.appendChild(el(P.l1,"ttl",`top:${P.ic?290:150}px;font-size:46px;color:#cdbf9f;letter-spacing:.3em`)); sc.appendChild(el(P.l2||"","ttl",`top:${P.ic?340:230}px;font-size:${P.fs||110}px;line-height:1.1;padding:0 60px;box-sizing:border-box`));
  if(P.sub) sc.appendChild(el(P.sub,"hand",`left:0;top:${P.ic?560:480}px;width:1280px;text-align:center;font-size:74px;color:#e9dcc0`));
  const ts=sc.querySelectorAll(".ttl"); if(P.ic) tl.fromTo(`#${id} .cic`,{opacity:0,y:14},{opacity:1,y:0,duration:.5},S+.2);
  if(P.l1) tl.fromTo(ts[0],{opacity:0,y:14},{opacity:1,y:0,duration:.6},S+.3); tl.fromTo(ts[ts.length-1],{opacity:0,y:18,scale:.95},{opacity:1,y:0,scale:1,duration:.7,ease:"power2.out"},S+tt(P,0,.8));
  if(P.sub) aparece(`#${id} .hand`,S+tt(P,1,2.2),.6); };

CENAS.multidao=(id,S,D,P)=>{ const sc=raiz(id); let m=""; const r=rng(14); for(let row=0;row<3;row++) for(let i=0;i<11;i++){ const x=80+i*108+(row%2)*50, y=620+row*46, h=.62+row*.14; m+=`<g transform="translate(${x},${y}) scale(${h})"><g class="mu r${row}"><ellipse cy="-60" rx="26" ry="42" fill="${["#2c2620","#3a322a","#483e34"][row]}" ${OL(2.5)}/><circle cy="-114" r="19" fill="${["#2c2620","#3a322a","#483e34"][row]}" ${OL(2.5)}/></g></g>`; }
  sc.insertAdjacentHTML("afterbegin",`<svg viewBox="0 0 1280 720">${bgNoite(id,"#7a5f3a",true)}<rect x="500" y="330" width="280" height="40" rx="6" fill="#8a6a46" ${OL(4)}/><rect x="520" y="370" width="240" height="190" fill="#6e5236" ${OL(4)}/>${pessoa(id+"m",{x:640,y:330,escala:.8})}${m}</svg>`);
  if(P.rot) sc.appendChild(el(P.rot,"hand",`left:0;top:60px;width:1280px;text-align:center;font-size:92px;color:#efe3c8`));
  parado(id+"m",S,D); [2,1,0].forEach((row,k)=>tl.fromTo(`#${id} .r${row}`,{opacity:0,y:20},{opacity:1,y:0,duration:.5,stagger:.06,ease:"power2.out"},S+.4+k*.9)); if(P.rot) aparece(`#${id} .hand`,S+tt(P,0,1.2),.6); };

CENAS.globo=(id,S,D,P)=>{ const sc=raiz(id);
  sc.insertAdjacentHTML("afterbegin",`<svg viewBox="0 0 1280 720">${bgPapel(id,true)}${quemSVG(id+"m",P.quem||"voce",{x:360,y:700,escala:1.35})}<g transform="translate(900,350)"><g class="gb">${ic("globo",0,0,3.6)}</g></g></svg>`);
  if(P.rot) sc.appendChild(el(P.rot,"hand",`left:640px;top:70px;width:600px;text-align:center;font-size:84px;color:#3a2e22`));
  parado(id+"m",S,D); tl.to(`#${id}m .armB`,{rotation:-80,svgOrigin:"0 0",duration:.8,ease:"power2.out"},S+tt(P,0,1.0));
  tl.fromTo(`#${id} .gb`,{rotation:-8,svgOrigin:"0 0"},{rotation:8,svgOrigin:"0 0",duration:2.6,yoyo:true,repeat:Math.max(1,Math.floor(D/2.6)),ease:"sine.inOut"},S); if(P.rot) aparece(`#${id} .hand`,S+tt(P,0,1.0),.6); };

CENAS.contrario=(id,S,D,P)=>{ const sc=raiz(id);
  sc.insertAdjacentHTML("afterbegin",`<svg viewBox="0 0 1280 720">${bgPapel(id,true)}
   <g class="oa" opacity="0"><path d="M300 200 H900" stroke="#6b6b6b" stroke-width="16" stroke-linecap="round"/><path d="M900 150 l80 50 l-80 50z" fill="#6b6b6b" ${OL(4)}/>${xRisco(640,200,70)}</g>
   <g class="ob" opacity="0"><path class="seta" pathLength="1" d="M960 520 H380 q-70 0 -70 -60" stroke="#3d6a5a" stroke-width="16" fill="none" stroke-linecap="round" stroke-dasharray="1" stroke-dashoffset="1"/><path d="M296 430 l14 -66 l50 52z" fill="#3d6a5a" ${OL(4)}/></g></svg>`);
  sc.appendChild(el(P.a||"controlar o mundo","hand",`left:300px;top:250px;font-size:68px;color:#6b6b6b;opacity:0`)); sc.appendChild(el(P.b||"controlar a si mesmo","hand",`left:420px;top:560px;font-size:76px;color:#3d6a5a`));
  const a=tt(P,0,.4), b=tt(P,1,2.2); tl.fromTo(`#${id} .oa`,{opacity:0,x:-40},{opacity:1,x:0,duration:.5},S+a); desenhaX(id,".oa",S+a+.7); aparece(`#${id} .hand:nth-of-type(1)`,S+a,.5);
  tl.fromTo(`#${id} .ob`,{opacity:0},{opacity:1,duration:.2},S+b); tl.fromTo(`#${id} .seta`,{strokeDashoffset:1},{strokeDashoffset:0,duration:1.0,ease:"power2.inOut"},S+b); aparece(`#${id} .hand:nth-of-type(2)`,S+b+.3,.5); };

CENAS.linhaTempo=(id,S,D,P)=>{ const sc=raiz(id);
  sc.insertAdjacentHTML("afterbegin",`<svg viewBox="0 0 1280 720">${bgPapel(id,true)}<path class="lt" pathLength="1" d="M200 400 H1080" stroke="#2a2018" stroke-width="10" fill="none" stroke-linecap="round" stroke-dasharray="1" stroke-dashoffset="1"/>
   <g class="m1" opacity="0"><circle cx="200" cy="400" r="22" fill="#e3b53a" ${OL(4)}/>${ic(P.ic1||"senado",200,250,1.5)}</g><g class="m2" opacity="0"><circle cx="1080" cy="400" r="22" fill="#e3b53a" ${OL(4)}/>${ic(P.ic2||"livro",1080,250,1.5)}</g></svg>`);
  sc.appendChild(el(P.a,"hand",`left:60px;top:450px;width:280px;text-align:center;font-size:72px;color:#3a2e22`)); sc.appendChild(el(P.b,"hand",`left:940px;top:450px;width:280px;text-align:center;font-size:72px;color:#3a2e22`)); sc.appendChild(el(P.mid,"hand",`left:340px;top:300px;width:600px;text-align:center;font-size:76px;color:#7a5a1a`));
  tl.fromTo(`#${id} .m1`,{opacity:0,y:14},{opacity:1,y:0,duration:.5},S+.3); aparece(`#${id} .hand:nth-of-type(1)`,S+.4,.5);
  tl.fromTo(`#${id} .lt`,{strokeDashoffset:1},{strokeDashoffset:0,duration:Math.max(2,D*.5),ease:"power1.inOut"},S+tt(P,0,1.2)); aparece(`#${id} .hand:nth-of-type(3)`,S+tt(P,0,1.2)+.8,.5);
  tl.fromTo(`#${id} .m2`,{opacity:0,y:14},{opacity:1,y:0,duration:.5},S+tt(P,1,D*.6)); aparece(`#${id} .hand:nth-of-type(2)`,S+tt(P,1,D*.6)+.1,.5); };

CENAS.post=(id,S,D,P)=>{ const sc=raiz(id);
  sc.insertAdjacentHTML("afterbegin",`<svg viewBox="0 0 1280 720"><rect width="1280" height="720" fill="#0a0d14"/><ellipse cx="640" cy="360" rx="560" ry="420" fill="#3a5fa0" opacity=".16"/><rect x="380" y="26" width="520" height="670" rx="46" fill="#fbfbfd" ${OL(5)}/>
   <circle cx="436" cy="84" r="24" fill="${P.cor||'#c9a45a'}"/><text x="436" y="92" text-anchor="middle" fill="#fff" ${UI} font-size="24" font-weight="700">${(P.nome||"?")[0].toUpperCase()}</text><text x="476" y="92" fill="#222" ${UI} font-size="24" font-weight="700">${P.nome||""}</text>
   <rect class="img" x="400" y="128" width="480" height="${P.alt||430}" fill="${P.cor||'#c9a45a'}" opacity="0"/>
   <foreignObject class="frase" x="420" y="150" width="440" height="${(P.alt||430)-40}" opacity="0"><div xmlns="http://www.w3.org/1999/xhtml" style="font-family:CaveatX;font-weight:700;font-size:${P.fz||60}px;line-height:1.05;color:#fff6dc;text-align:center;display:flex;align-items:center;justify-content:center;height:100%">${P.frase||""}</div></foreignObject>
   <g class="lk" opacity="0"><path d="M420 ${(P.alt||430)+168} C390 ${(P.alt||430)+138} 404 ${(P.alt||430)+118} 420 ${(P.alt||430)+128} C436 ${(P.alt||430)+118} 450 ${(P.alt||430)+138} 420 ${(P.alt||430)+168}z" fill="#c0302f"/><text x="462" y="${(P.alt||430)+158}" fill="#222" ${UI} font-size="22" font-weight="700">${P.curtidas||"2 curtidas"}</text></g></svg>`);
  tl.fromTo(`#${id} .img`,{opacity:0},{opacity:1,duration:.5},S+.3); tl.fromTo(`#${id} .frase`,{opacity:0},{opacity:1,duration:.6},S+tt(P,0,.9)); tl.fromTo(`#${id} .lk`,{opacity:0,y:10},{opacity:1,y:0,duration:.5},S+tt(P,1,2.4)); };

CENAS.contraste2=(id,S,D,P)=>{ const sc=raiz(id);
  const card=(cls,x,fill,tit,corT,ico,txt,mk)=>`<g class="${cls}" opacity="0"><rect x="${x}" y="120" width="530" height="480" rx="26" fill="${fill}" ${OL(4)}/><text x="${x+265}" y="180" text-anchor="middle" font-family="CinzelX" font-weight="700" font-size="30" letter-spacing="3" fill="${corT}">${tit}</text>${ic(ico,x+265,330,1.8)}${linhasTxt(txt,x+265,480,50)}${mk==="x"?xRisco(x+265,330,96):""}${mk==="ok"?checkSVG(x+385,250,"ck"):""}</g>`;
  sc.insertAdjacentHTML("afterbegin",`<svg viewBox="0 0 1280 720">${bgPapel(id,true)}${card("cA",70,"#dcd6cb",P.tA,"#6b6b6b",P.icA,P.a,P.mA)}${card("cB",680,"#f8e9bf",P.tB,"#8a6a1e",P.icB,P.b,P.mB)}</svg>`);
  const a=tt(P,0,.5), b=tt(P,1,2.8);
  [["cA",a,P.mA],["cB",b,P.mB]].forEach(([g,t,mk])=>{ tl.fromTo(`#${id} .${g}`,{opacity:0,y:20},{opacity:1,y:0,duration:.45,ease:"back.out(1.6)"},S+t);
    if(mk==="x") desenhaX(id,`.${g}`,S+t+.7); if(mk==="ok") tl.fromTo(`#${id} .${g} .ck`,{strokeDashoffset:1},{strokeDashoffset:0,duration:.35,ease:"power2.out"},S+t+.6); }); };

CENAS.pergunta2=(id,S,D,P)=>{ const sc=raiz(id);
  sc.insertAdjacentHTML("afterbegin",`<svg viewBox="0 0 1280 720">${bgPapel(id,true)}<g class="pg" opacity="0">${ic(P.ic,640,270,2.6)}${linhasTxt(P.txt,640,490,62)}${P.mark==="x"?xRisco(640,270,130):""}${P.mark==="ok"?checkSVG(700,190,"ck"):""}</g></svg>`);
  tl.fromTo(`#${id} .pg`,{opacity:0,y:20},{opacity:1,y:0,duration:.5,ease:"back.out(1.6)"},S+.2); const t=tt(P,0,1.6);
  if(P.mark==="x") desenhaX(id,".pg",S+t); if(P.mark==="ok") tl.fromTo(`#${id} .ck`,{strokeDashoffset:1},{strokeDashoffset:0,duration:.4,ease:"power2.out"},S+t); };

CENAS.estatua=(id,S,D,P)=>{ const sc=raiz(id);
  sc.insertAdjacentHTML("afterbegin",`<svg viewBox="0 0 1280 720">${bgNoite(id,"#7a6a5a",true)}${pessoa(id+"m",{silhueta:"#c3c6cc",x:640,y:560,escala:1.15})}<rect x="480" y="560" width="320" height="160" fill="#8a8a92" ${OL(4.5)}/><rect x="460" y="548" width="360" height="26" fill="#a2a2aa" ${OL(4.5)}/></svg>`);
  sc.appendChild(el(P.rot,"hand",`left:0;top:70px;width:1280px;text-align:center;font-size:104px;color:#efe3c8`)); parado(id+"m",S,D); aparece(`#${id} .hand`,S+tt(P,0,1.2),.6); };

CENAS.insulto=(id,S,D,P)=>{ const sc=raiz(id);
  sc.insertAdjacentHTML("afterbegin",`<svg viewBox="0 0 1280 720">${bgRuaAtenas(id)}${quemSVG(id+"a","homem",{x:360,y:700,escala:1.3})}${quemSVG(id+"b","voce",{x:900,y:700,escala:1.3})}<ellipse class="aura" cx="900" cy="330" rx="130" ry="120" fill="#e8483a" opacity="0"/><g class="rg" opacity="0">${ic("raiva",900,170,.9)}</g></svg>`);
  sc.appendChild(el("#@!%","bal",`left:290px;top:130px;font-size:72px;padding:6px 34px`)); parado(id+"a",S,D); parado(id+"b",S+.2,D); const t=tt(P,0,.8);
  gesto(id+"a","A",S+t,35,.6); tl.fromTo(`#${id} .bal`,{opacity:0,scale:.5},{opacity:1,scale:1,duration:.4,ease:"back.out(2)"},S+t);
  tl.fromTo(`#${id} .aura`,{opacity:0},{opacity:.2,duration:.8,ease:"power2.out"},S+t+.8); tl.fromTo(`#${id} .rg`,{opacity:0,scale:.5,svgOrigin:"900 170"},{opacity:1,scale:1,svgOrigin:"900 170",duration:.4,ease:"back.out(2)"},S+t+1.2); };

CENAS.varandaTxt=(id,S,D,P)=>{ CENAS.varanda(id,S,D,P); const sc=raiz(id); sc.appendChild(el(P.nome,"ttl",`top:90px;font-size:120px;color:#fff3d6;text-shadow:0 4px 24px rgba(60,30,10,.55)`));
  tl.fromTo(`#${id} .ttl`,{opacity:0,y:18,letterSpacing:".5em"},{opacity:1,y:0,letterSpacing:".16em",duration:1.2,ease:"power2.out"},S+tt(P,0,1.2)); };

// =====================================================================
//  FAMÍLIAS POR LOCAL (novas) — o mesmo desenho do capítulo, com personagem/local/texto trocáveis por parâmetros
//  pos_<local>_<vista>  personagem parado + gesto · expl_<local>_<vista> idem com câmera lenta · cost_<local> de costas
//  anda_<local> caminha (andar() exige P.por) · dial_<local> dois personagens · abertura (título com o personagem)
// =====================================================================
const quemLado=(id,q,o)=>{ if(q==="voce"||q==="homem") return quemSVG(id,q,o);
  const base={marco:{},zenao:ZENAO,epicteto:EPICTETO,seneca:SENECA,crates:CRATES,livreiro:LIVREIRO}[q]||{}; return lado(id,{...base,...o}); };
const LOCAIS={ biblioteca:{bg:(id)=>bgBiblioteca(id),y:690}, rua:{bg:(id)=>bgRuaAtenas(id),y:700}, portico:{bg:(id)=>bgPortico(id),y:690},
  palacio:{bg:(id)=>bgPalacio(id),y:690}, mercado:{bg:(id)=>bgMercado(id,[]),y:690}, montanha:{bg:(id)=>bgMontanha(id),y:690},
  noite:{bg:(id)=>bgNoite(id,"#7a5f3a",true),y:690}, papel:{bg:(id)=>bgPapel(id,true),y:700} };
const fzTxt=(s)=>{ const n=String(s).length; return n<=10?96:n<=16?80:n<=24?64:52; };
const cartaz=(id,sc,S,P,cx,top,k)=>{ const txt=k==null?P.txt:(k===0?P.a:P.b); if(!txt) return; const w=560;
  sc.appendChild(el(txt,"bal",`left:${cx-w/2}px;top:${top}px;width:${w}px;box-sizing:border-box;white-space:normal;text-align:center;font-size:${fzTxt(txt)}px;line-height:1.05`));
  const els=sc.querySelectorAll(".bal"); aparece(els[els.length-1],S+tt(P,k||0,k?2.4:.8),.5); };
Object.keys(LOCAIS).forEach((loc)=>{ const L=LOCAIS[loc];
  ["frente","lado"].forEach((vista)=>["pos","expl"].forEach((fam)=>{
    CENAS[`${fam}_${loc}_${vista}`]=(id,S,D,P)=>{ const sc=raiz(id); const dir=P.pos==="d"; const cx=dir?880:400; const q=P.quem||"zenao";
      const ch=vista==="frente"?quemSVG(id+"m",q,{x:cx,y:L.y,escala:1.3}):quemLado(id+"m",q,{x:cx,y:L.y,escala:1.3,flip:dir});
      sc.insertAdjacentHTML("afterbegin",`<svg viewBox="0 0 1280 720">${L.bg(id)}${ch}</svg>`);
      parado(id+"m",S,D); gesto(id+"m","B",S+tt(P,0,.8),-70,.8);
      cartaz(id,sc,S,P,dir?330:950,120); if(fam==="expl") camera(id,S,D,1,1.05,dir?880:400,420); };
  }));
  if(loc!=="papel") CENAS[`cost_${loc}`]=(id,S,D,P)=>{ const sc=raiz(id);
    sc.insertAdjacentHTML("afterbegin",`<svg viewBox="0 0 1280 720">${L.bg(id)}${costas(id+"m",{x:P.pos==="d"?820:460,y:L.y+10,escala:1.25})}</svg>`);
    parado(id+"m",S,D); if(existe(`#${id}m .head`)) tl.fromTo(`#${id}m .head`,{rotation:0,svgOrigin:"0 0"},{rotation:5,svgOrigin:"0 0",duration:D*.5,yoyo:true,repeat:1,ease:"sine.inOut"},S+.6);
    cartaz(id,sc,S,P,640,90); };
  if(loc!=="papel"&&loc!=="montanha") CENAS[`anda_${loc}`]=(id,S,D,P)=>{ const sc=raiz(id); const q=P.quem||"zenao"; const esc=1.3, alt=300*esc;
    const dist=Math.min(760,.42*alt*D), d=P.dir==="e"?-1:1, x0=d>0?Math.max(180,640-dist/2-60):Math.min(1100,640+dist/2+60), x1=x0+d*dist;
    sc.insertAdjacentHTML("afterbegin",`<svg viewBox="0 0 1280 720">${L.bg(id)}${quemLado(id+"m",q,{x:0,y:0,escala:esc})}</svg>`);
    andar(id+"m",S,D,{x:x0,y:L.y,s:esc},{x:x1,y:L.y,s:esc},{por:P.por||"vai até o fundo do cenário enquanto a fala segue"}); cartaz(id,sc,S,P,640,90); };
  CENAS[`dial_${loc}`]=(id,S,D,P)=>{ const sc=raiz(id); const q=P.quem||"zenao", q2=P.quem2||"voce";
    sc.insertAdjacentHTML("afterbegin",`<svg viewBox="0 0 1280 720">${L.bg(id)}${quemLado(id+"a",q,{x:380,y:L.y,escala:1.3})}${quemLado(id+"b",q2,{x:900,y:L.y,escala:1.3,flip:true})}</svg>`);
    parado(id+"a",S,D); parado(id+"b",S+.2,D); gesto(id+"a","B",S+tt(P,0,.8),-60,.8); gesto(id+"b","B",S+tt(P,1,2.4),-60,.8);
    cartaz(id,sc,S,P,300,110,0); cartaz(id,sc,S,P,980,110,1); };
});
// abertura — o personagem do vídeo no foco de luz com o título (igual à abertura do capítulo 1)
CENAS.abertura=(id,S,D,P)=>{ const sc=raiz(id); const r=rng(3);
  const po=[...Array(14)].map(()=>`<circle class="po" cx="${380+r()*520}" cy="${120+r()*440}" r="${1.5+r()*2.5}" fill="#f3dca0" opacity=".5"/>`).join("");
  sc.insertAdjacentHTML("afterbegin",`<svg viewBox="0 0 1280 720">${bgNoite(id)}<polygon class="spot" points="560,0 720,0 960,640 320,640" fill="#f3dca0" opacity=".13"/>${po}${quemLado(id+"m",P.quem||"zenao",{x:640,y:620,escala:1.1})}</svg>`);
  const n=String(P.titulo||"").length; sc.appendChild(el(P.titulo||"","ttl",`top:60px;font-size:${n<=22?84:n<=40?64:50}px;line-height:1.1;padding:0 50px;box-sizing:border-box`));
  parado(id+"m",S,D);
  if(P.sub){ sc.appendChild(el(P.sub,"hand",`left:0;top:${n<=22?170:n<=40?190:210}px;width:1280px;text-align:center;font-size:54px;color:#e9dcc0;opacity:0`)); aparece(`#${id} .hand`,S+1.8,.7); }
  tl.fromTo(`#${id}m .head`,{rotation:0,svgOrigin:"0 0"},{rotation:-3,svgOrigin:"0 0",duration:D,ease:"sine.inOut"},S);
  tl.fromTo(`#${id} .ttl`,{opacity:0,y:24,letterSpacing:"0.4em"},{opacity:1,y:0,letterSpacing:"0.14em",duration:1.2,ease:"power2.out"},S+.4);
  tl.fromTo(`#${id} .spot`,{opacity:0},{opacity:.13,duration:1},S);
  tl.fromTo(`#${id} .po`,{y:0},{y:-36,duration:1.8,yoyo:true,repeat:1,ease:"sine.inOut",stagger:.07},S); };
