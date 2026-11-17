// =====================================================================
//  CENÁRIOS — todos com CONTORNO escuro grosso, detalhe e camadas (.l0 fundo, .l1 meio, .l2 chão) para parallax
// =====================================================================
const OL=(w)=>`stroke="#2a2018" stroke-width="${w||3}" stroke-linejoin="round" stroke-linecap="round"`;
function coluna(x,yb,h,w){ w=w||44; let fl=""; for(let i=1;i<4;i++) fl+=`<path d="M${x+i*w/4} ${yb-h+10} V${yb-12}" stroke="#2a2018" stroke-width="1.6" opacity=".4"/>`;
  return `<g><rect x="${x}" y="${yb-h}" width="${w}" height="${h}" fill="#efe6d2" ${OL(3)}/>${fl}<rect x="${x-8}" y="${yb-h-12}" width="${w+16}" height="14" fill="#e3d7bc" ${OL(3)}/><rect x="${x-8}" y="${yb-12}" width="${w+16}" height="12" fill="#e3d7bc" ${OL(3)}/></g>`; }
function toldo(x,y,w,c1,c2){ const n=Math.max(4,Math.round(w/26)); let f="",b="";
  for(let i=0;i<n;i++){ f+=`<rect x="${x+i*w/n}" y="${y}" width="${w/n}" height="46" fill="${i%2?c2:c1}"/>`; b+=`<circle cx="${x+(i+.5)*w/n}" cy="${y+46}" r="${w/n/2}" fill="${i%2?c2:c1}" ${OL(2.5)}/>`; }
  return `<g>${f}<rect x="${x}" y="${y}" width="${w}" height="46" fill="none" ${OL(3.5)}/>${b}</g>`; }
function anfora(x,y,e,cor){ return `<g transform="translate(${x},${y}) scale(${e})"><path d="M-14 -50 q-4 8 -2 16 q-24 10 -22 40 q4 22 24 24 h28 q20 -2 24 -24 q2 -30 -22 -40 q2 -8 -2 -16z" fill="${cor}" ${OL(3)}/><path d="M-32 -6 q32 8 64 0" stroke="#2a2018" stroke-width="2.5" fill="none"/><path d="M-26 -34 q-14 4 -12 22 M26 -34 q14 4 12 22" stroke="#2a2018" stroke-width="3" fill="none"/></g>`; }
function frasco(x,y,cor){ return `<g transform="translate(${x},${y})"><rect x="-4" y="-22" width="8" height="8" fill="#6a5a3a" ${OL(2)}/><ellipse cy="0" rx="12" ry="15" fill="${cor}" ${OL(2.5)}/></g>`; }
function pano(x,y,cor){ return `<path d="M${x} ${y} h28 v74 l-14 -11 l-14 11z" fill="${cor}" ${OL(2.5)}/>`; }
function casas(x0,n,seed,y,esc,corTel,corParede){ const r=rng(seed); let x=x0, s="";
  for(let i=0;i<n;i++){ const w=(70+r()*60)*esc, h=(60+r()*50)*esc;
    s+=`<rect x="${x}" y="${y-h}" width="${w}" height="${h}" fill="${corParede}" ${OL(2.5)}/><path d="M${x-8*esc} ${y-h} l${w/2+8*esc} ${-34*esc} l${w/2+8*esc} ${34*esc}z" fill="${corTel}" ${OL(2.5)}/><rect x="${x+w*.18}" y="${y-h*.55}" width="${w*.2}" height="${h*.55}" fill="#5a3f2e" ${OL(2)}/><rect x="${x+w*.55}" y="${y-h*.72}" width="${w*.18}" height="${h*.2}" fill="#8a7252" ${OL(1.8)}/>`;
    x+=w+(18+r()*40)*esc; } return s; }
function partenon(x,y){ let c=""; for(let i=0;i<8;i++) c+=`<rect x="${x+14+i*26}" y="${y-92}" width="15" height="92" fill="#eadfc8" ${OL(2.5)}/>`;
  return `<g><rect x="${x}" y="${y-8}" width="236" height="8" fill="#d8ccb0" ${OL(2.5)}/>${c}<rect x="${x+4}" y="${y-106}" width="228" height="14" fill="#e3d7bc" ${OL(2.5)}/><path d="M${x} ${y-106} L${x+118} ${y-150} L${x+236} ${y-106}z" fill="#eadfc8" ${OL(2.5)}/></g>`; }
function chama(x,y,esc){ return `<g transform="translate(${x},${y}) scale(${esc||1})"><g class="chama"><path d="M0 0 q-20 -26 0 -64 q20 36 0 64z" fill="#ffb347" ${OL(2.5)}/><path d="M0 0 q-9 -14 0 -32 q9 16 0 32z" fill="#fff0b0"/></g></g>`; }
function silhuetas(x0,n,y,esc,cor,seed,gap){ const r=rng(seed); let s=""; gap=gap||70;
  for(let i=0;i<n;i++){ const x=x0+i*(gap+r()*18), h=(.8+r()*.3)*esc;
    s+=`<g transform="translate(${x},${y}) scale(${h})"><g class="sil"><g class="sb"><ellipse cx="0" cy="-70" rx="30" ry="48" fill="${cor}"/><circle cx="0" cy="-130" r="22" fill="${cor}"/></g></g></g>`; } return s; }
// feixe de luz diagonal (luz como linguagem)
function feixe(id,x,w,op){ return `<polygon class="feixe" points="${x},0 ${x+w},0 ${x+w-330},720 ${x-330},720" fill="#ffe7a8" opacity="${op||.16}"/>`; }
// tijolos irregulares com contorno
function tijolos(id,cor){ return `<pattern id="${id}tj" width="150" height="56" patternUnits="userSpaceOnUse"><rect width="150" height="56" fill="${cor||'#6b5f52'}"/>
  <rect x="2" y="2" width="68" height="24" rx="4" fill="${cor||'#6b5f52'}" stroke="#2a2018" stroke-width="2.5" opacity=".95"/><rect x="74" y="2" width="74" height="24" rx="4" fill="${cor||'#6b5f52'}" stroke="#2a2018" stroke-width="2.5"/>
  <rect x="-34" y="30" width="68" height="24" rx="4" fill="${cor||'#6b5f52'}" stroke="#2a2018" stroke-width="2.5"/><rect x="38" y="30" width="74" height="24" rx="4" fill="${cor||'#6b5f52'}" stroke="#2a2018" stroke-width="2.5"/><rect x="116" y="30" width="68" height="24" rx="4" fill="${cor||'#6b5f52'}" stroke="#2a2018" stroke-width="2.5"/></pattern>`; }

function bgNoite(id,cor,comFeixe){ return `<defs><radialGradient id="${id}s" cx=".5" cy=".62" r=".6"><stop offset="0" stop-color="${cor||'#6a5a45'}"/><stop offset=".55" stop-color="#241d17"/><stop offset="1" stop-color="#0d0b0a"/></radialGradient></defs><rect width="1280" height="720" fill="url(#${id}s)"/>${comFeixe?feixe(id,720,170,.14):""}<g class="l2"><rect x="-200" y="570" width="1900" height="200" fill="#1a1511" opacity=".85"/><rect x="-200" y="570" width="1900" height="4" fill="#2a2018"/></g>`; }
function bgBiblioteca(id){ const r=rng(11); let livros=""; const cores=["#7a2e2e","#2f4a63","#3d5a3d","#8a6a2e","#5a3a63","#a05a3a","#2e4a4a","#6a5a3a"];
  for(let row=0;row<3;row++){ let x=-120; const y=150+row*160; livros+=`<rect x="-200" y="${y+130}" width="1900" height="16" fill="#4a3220" ${OL(3)}/>`;
    while(x<1700){ const w=20+r()*26, h=88+r()*38, c=cores[Math.floor(r()*cores.length)]; livros+=`<rect x="${x}" y="${y+130-h}" width="${w}" height="${h}" fill="${c}" ${OL(2.2)}/><rect x="${x+3}" y="${y+130-h+14}" width="${w-6}" height="5" fill="#d8c08a" opacity=".75"/><rect x="${x+3}" y="${y+130-h+h*.62}" width="${w-6}" height="3" fill="#d8c08a" opacity=".5"/>`; x+=w+2; } }
  return `<defs><linearGradient id="${id}p" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4a3322"/><stop offset="1" stop-color="#2a1b11"/></linearGradient><radialGradient id="${id}luz" cx=".5" cy=".4" r=".7"><stop offset="0" stop-color="#ffd98a" stop-opacity=".38"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient></defs>
  <rect width="1280" height="720" fill="url(#${id}p)"/><g class="l1">${livros}</g><rect y="610" width="1280" height="110" fill="#5a3a22"/><g class="l2"><rect x="-200" y="610" width="1900" height="12" fill="#3a2616" ${OL(3)}/>${[...Array(18)].map((_,i)=>`<path d="M${i*120-100} 622 l-40 98" stroke="#2a2018" stroke-width="3" opacity=".6"/>`).join("")}</g><rect width="1280" height="720" fill="url(#${id}luz)"/>${feixe(id,300,150,.1)}`; }
function bgPalacio(id){ let col=""; for(let i=0;i<7;i++) col+=coluna(300+i*100,500,250,44);
  return `<defs><linearGradient id="${id}c" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f4e7c8"/><stop offset="1" stop-color="#e2c98f"/></linearGradient></defs><rect width="1280" height="720" fill="url(#${id}c)"/><circle cx="1000" cy="110" r="42" fill="#fff3cf" opacity=".9"/>
  <g class="l0"><path d="M260 240 L640 110 L1020 240z" fill="#d8aa3a" ${OL(4)}/><rect x="268" y="236" width="744" height="18" fill="#c99a2e" ${OL(3)}/><ellipse cx="640" cy="112" rx="70" ry="46" fill="#e8bd4c" ${OL(3.5)}/>${col}
  <rect x="560" y="330" width="160" height="170" rx="80" fill="#3a2316" ${OL(3.5)}/><rect x="240" y="500" width="800" height="20" fill="#e3d7bc" ${OL(3)}/><rect x="210" y="520" width="860" height="20" fill="#d3c7a8" ${OL(3)}/><rect x="180" y="540" width="920" height="22" fill="#c5b794" ${OL(3)}/></g><g class="l2"><rect x="-200" y="562" width="1900" height="200" fill="#c9b283"/><rect x="-200" y="562" width="1900" height="5" fill="#2a2018"/></g>`; }
// MERCADO largo (para câmera viajando): .l0 = colunata + Partenon (move devagar), .l1 = barracas (move no ritmo da câmera). rotulos = palavras manuscritas por barraca.
function bgMercado(id,rotulos){ rotulos=rotulos||[]; let col="", b="";
  for(let i=0;i<16;i++) col+=coluna(i*150-120,430,150,34);
  const pares=[["#b8402f","#efe3c8"],["#b09a3a","#efe3c8"],["#5f7f78","#efe3c8"],["#a8452f","#efe3c8"]]; const cj=["#b8402f","#c99a2e","#3d6a5a","#8a4a2e","#6a5a8a"];
  for(let i=0;i<6;i++){ const x=i*340-140, w=270, [c1,c2]=pares[i%4];
    let itens=""; const tipo=i%3;
    if(tipo===0){ for(let k=0;k<5;k++) itens+=pano(x+22+k*50,376,cj[(i+k)%5]); }
    else if(tipo===1){ for(let k=0;k<4;k++) itens+=anfora(x+42+k*62,478,.55+(k%2)*.12,["#c4623a","#2d2620","#b8542f","#d27a4a"][k]); }
    else { for(let k=0;k<5;k++) itens+=frasco(x+34+k*50,462,cj[(i+k)%5]); }
    b+=`${itens}<rect x="${x+4}" y="348" width="7" height="170" fill="#5a3f2e" ${OL(2.5)}/><rect x="${x+w-11}" y="348" width="7" height="170" fill="#5a3f2e" ${OL(2.5)}/>${toldo(x,306,w,c1,c2)}
    <rect x="${x-6}" y="486" width="${w+12}" height="26" fill="#8a6a46" ${OL(3)}/><rect x="${x}" y="512" width="${w}" height="64" fill="#6e5236" ${OL(3)}/>
    ${rotulos[i]?`<text class="rot" x="${x+w/2}" y="282" text-anchor="middle" font-family="CaveatX" font-weight="700" font-size="58" fill="#3a2e22" opacity="0">${rotulos[i]}</text>`:""}`; }
  return `<defs><linearGradient id="${id}c" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ecdcb8"/><stop offset="1" stop-color="#cdb487"/></linearGradient>
  <pattern id="${id}t" width="140" height="44" patternUnits="userSpaceOnUse"><rect width="140" height="44" fill="#bba883"/><rect x="3" y="3" width="64" height="16" rx="8" fill="#c6b48d" ${OL(2.2)}/><rect x="73" y="3" width="64" height="16" rx="8" fill="#c6b48d" ${OL(2.2)}/><rect x="-30" y="24" width="64" height="16" rx="8" fill="#c6b48d" ${OL(2.2)}/><rect x="40" y="24" width="64" height="16" rx="8" fill="#c6b48d" ${OL(2.2)}/><rect x="110" y="24" width="64" height="16" rx="8" fill="#c6b48d" ${OL(2.2)}/></pattern></defs>
  <rect width="1280" height="720" fill="url(#${id}c)"/><circle cx="220" cy="110" r="38" fill="#fff0c8" opacity=".85"/>
  <g class="l0"><g transform="translate(420,330) scale(.7)">${partenon(0,0)}</g>${col}<rect x="-200" y="430" width="3000" height="3" fill="#2a2018"/></g>
  <g class="l1">${b}</g><g class="l2"><rect x="-200" y="576" width="3000" height="200" fill="url(#${id}t)"/><rect x="-200" y="576" width="3000" height="4" fill="#2a2018"/></g>`; }

// =====================================================================
//  CENÁRIOS E ÍCONES — acrescentados no capítulo 1 (Marco Aurélio / estoicismo)
// =====================================================================
// fundo de papel creme com textura (cenas-conceito)
function bgPapel(id,quente){ return `<defs><radialGradient id="${id}pp" cx=".5" cy=".45" r=".85"><stop offset="0" stop-color="${quente?'#f1e2c4':'#efe7d6'}"/><stop offset="1" stop-color="${quente?'#cdb78c':'#cbbd9e'}"/></radialGradient></defs><rect width="1280" height="720" fill="url(#${id}pp)"/><g class="l2"><rect x="-200" y="600" width="1900" height="4" fill="#2a2018" opacity=".35"/></g>`; }
// quarto à luz de vela: parede de pedra, janela em arco com noite, mesa, cadeira, vela, pergaminho
function bgQuartoVela(id){ return `<defs>${tijolos(id,'#4a3f36')}<radialGradient id="${id}v" cx=".66" cy=".5" r=".75"><stop offset="0" stop-color="#ffcf7a" stop-opacity=".55"/><stop offset=".5" stop-color="#7a4a1a" stop-opacity=".18"/><stop offset="1" stop-color="#000" stop-opacity=".62"/></radialGradient></defs>
  <rect width="1280" height="720" fill="url(#${id}tj)"/>
  <g><path d="M120 330 V170 q0 -60 70 -60 q70 0 70 60 V330z" fill="#0f1830" ${OL(4)}/><circle cx="190" cy="170" r="3" fill="#fff" opacity=".9"/><circle cx="160" cy="215" r="2" fill="#fff" opacity=".7"/><circle cx="222" cy="150" r="2.4" fill="#fff" opacity=".8"/><circle cx="222" cy="240" r="2" fill="#fff" opacity=".6"/><path d="M110 332 h160" stroke="#2a2018" stroke-width="8"/></g>
  <rect y="640" width="1280" height="80" fill="#2e2018" ${OL(3)}/>
  <g><rect x="330" y="505" width="120" height="16" rx="4" fill="#6b4a2c" ${OL(3)}/><rect x="334" y="300" width="14" height="220" rx="4" fill="#6b4a2c" ${OL(3)}/><rect x="340" y="521" width="10" height="119" fill="#5a3d24" ${OL(3)}/><rect x="430" y="521" width="10" height="119" fill="#5a3d24" ${OL(3)}/></g>
  <g><rect x="480" y="426" width="470" height="18" rx="4" fill="#8a6a46" ${OL(3.5)}/><rect x="500" y="444" width="16" height="196" fill="#6b4a2c" ${OL(3)}/><rect x="914" y="444" width="16" height="196" fill="#6b4a2c" ${OL(3)}/>
   <path d="M520 424 l86 -10 l8 10z" fill="#efe3c3" ${OL(2.5)}/><rect x="650" y="404" width="22" height="22" rx="4" fill="#2a2430" ${OL(2.5)}/>
   <rect x="800" y="360" width="44" height="66" rx="5" fill="#e8dcbf" ${OL(3)}/><path d="M822 360 v-12" stroke="#2a2018" stroke-width="3"/></g>
  <rect width="1280" height="720" fill="url(#${id}v)"/>`; }
// varanda imperial ao amanhecer (colunas laterais + cidade ao fundo; a balaustrada é desenhada por cima do personagem)
function bgVarandaFundo(id){ return `<defs><linearGradient id="${id}c" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a3e60"/><stop offset=".45" stop-color="#e79a5c"/><stop offset="1" stop-color="#ffe2ab"/></linearGradient></defs>
  <rect width="1280" height="720" fill="url(#${id}c)"/><circle cx="640" cy="420" r="70" fill="#fff1c2"/>
  <path d="M-100 470 q300 -80 640 -20 q400 -70 840 20 v300 h-1480z" fill="#7a5a5a" opacity=".85"/>
  <g class="l0"><g transform="translate(150,420) scale(.8)">${partenon(0,0)}</g><g transform="translate(900,430) scale(.55)">${partenon(0,0)}</g>${casas(-60,24,19,540,.5,"#8a5a4a","#d8c8b0")}</g>
  <rect y="500" width="1280" height="90" fill="#e8b98a" opacity=".3"/>`; }
function varandaFrente(id){ let b=""; for(let i=0;i<22;i++) b+=`<rect x="${-20+i*62}" y="612" width="22" height="70" rx="6" fill="#efe6d2" ${OL(2.5)}/>`;
  return `<g class="grade">${b}<rect x="-30" y="592" width="1340" height="22" rx="6" fill="#e3d7bc" ${OL(3.5)}/><rect x="-30" y="680" width="1340" height="40" fill="#d3c7a8" ${OL(3.5)}/></g>${coluna(40,720,720,70)}${coluna(1170,720,720,70)}`; }
// ícones
const icCamera=(x,y,e)=>`<g transform="translate(${x},${y}) scale(${e||1})"><rect x="-56" y="-34" width="112" height="76" rx="14" fill="#efe6d2" ${OL(4)}/><rect x="-26" y="-48" width="52" height="18" rx="6" fill="#d8ccb0" ${OL(3.5)}/><circle cx="0" cy="4" r="26" fill="#3a2e22" ${OL(4)}/><circle cx="0" cy="4" r="14" fill="#6a8fb0"/><circle cx="-6" cy="-2" r="4" fill="#fff" opacity=".8"/><circle cx="40" cy="-16" r="5" fill="#c0302f"/></g>`;
const icMic=(x,y,e)=>`<g transform="translate(${x},${y}) scale(${e||1})"><rect x="-22" y="-60" width="44" height="76" rx="22" fill="#d8ccb0" ${OL(4)}/><path d="M-10 -40 h20 M-10 -26 h20 M-10 -12 h20" stroke="#2a2018" stroke-width="2.5"/><path d="M-38 -4 q0 44 38 44 q38 0 38 -44" fill="none" ${OL(4)}/><path d="M0 40 v26 M-22 66 h44" ${OL(4)} fill="none"/></g>`;
const icEspadas=(x,y,e)=>`<g transform="translate(${x},${y}) scale(${e||1})">${[-1,1].map(s=>`<g transform="rotate(${s*40})"><path d="M-8 -80 l8 -22 l8 22 v104 h-16z" fill="#cfd4d8" ${OL(3.5)}/><rect x="-26" y="24" width="52" height="10" rx="4" fill="#b8861f" ${OL(3.5)}/><rect x="-6" y="34" width="12" height="34" rx="4" fill="#6b4a2c" ${OL(3.5)}/><circle cy="72" r="8" fill="#b8861f" ${OL(3)}/></g>`).join("")}</g>`;
const icPunhal=(x,y,e)=>`<g transform="translate(${x},${y}) scale(${e||1}) rotate(-20)"><path d="M-14 -78 q14 -26 28 0 l-4 96 h-20z" fill="#cfd4d8" ${OL(3.5)}/><path d="M0 -70 v80" stroke="#8a9096" stroke-width="2.5"/><rect x="-34" y="18" width="68" height="12" rx="5" fill="#8a2f2f" ${OL(3.5)}/><rect x="-7" y="30" width="14" height="40" rx="5" fill="#3a2e22" ${OL(3.5)}/></g>`;
const icPeste=(x,y,e)=>`<g transform="translate(${x},${y}) scale(${e||1})">${[...Array(10)].map((_,i)=>`<g transform="rotate(${i*36})"><path d="M0 -44 v-22" ${OL(3.5)}/><circle cy="-70" r="9" fill="#7aa05a" ${OL(3)}/></g>`).join("")}<circle r="46" fill="#9fc27a" ${OL(4)}/><circle cx="-14" cy="-10" r="7" fill="#7aa05a"/><circle cx="14" cy="14" r="9" fill="#7aa05a"/><circle cx="8" cy="-18" r="5" fill="#7aa05a"/></g>`;
const icMultidao=(x,y,e)=>`<g transform="translate(${x},${y}) scale(${e||1})">${[[-60,6,1.0],[-24,-6,1.15],[14,4,1.05],[52,-2,1.1]].map(([a,b,c])=>`<g transform="translate(${a},${b}) scale(${c})"><ellipse cy="14" rx="20" ry="30" fill="#4a3f36" ${OL(3)}/><circle cy="-30" r="15" fill="#4a3f36" ${OL(3)}/></g>`).join("")}</g>`;
function relogioSVG(id,x,y,r){ let tk=""; for(let i=0;i<12;i++){ const a=i*Math.PI/6, l=i%3===0?16:9; tk+=`<path d="M${(Math.sin(a)*(r-6)).toFixed(1)} ${(-Math.cos(a)*(r-6)).toFixed(1)} L${(Math.sin(a)*(r-6-l)).toFixed(1)} ${(-Math.cos(a)*(r-6-l)).toFixed(1)}" stroke="#2a2018" stroke-width="${i%3===0?6:3.5}" stroke-linecap="round"/>`; }
  return `<g transform="translate(${x},${y})"><circle r="${r+14}" fill="#8a6a46" ${OL(5)}/><circle r="${r}" fill="#f6efdf" ${OL(5)}/>${tk}<g class="hMin"><path d="M0 14 L0 ${-(r-30)}" stroke="#2a2018" stroke-width="7" stroke-linecap="round"/></g><g class="hHora"><path d="M0 10 L0 ${-(r-70)}" stroke="#2a2018" stroke-width="11" stroke-linecap="round"/></g><circle r="11" fill="#c0302f" ${OL(3)}/></g>`; }

// =====================================================================
//  CAPÍTULO 2 — cenários: rua de Atenas, mar, pórtico pintado (Stoa Poikile)
// =====================================================================
function bgRuaAtenas(id){ return `<defs><linearGradient id="${id}c" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#bcd0d6"/><stop offset="1" stop-color="#f6e7c6"/></linearGradient>
  <pattern id="${id}rua" width="150" height="48" patternUnits="userSpaceOnUse"><rect width="150" height="48" fill="#c7b58f"/><rect x="4" y="4" width="68" height="18" rx="9" fill="#d4c49f" ${OL(2.2)}/><rect x="78" y="4" width="68" height="18" rx="9" fill="#d4c49f" ${OL(2.2)}/><rect x="-30" y="26" width="68" height="18" rx="9" fill="#d4c49f" ${OL(2.2)}/><rect x="42" y="26" width="68" height="18" rx="9" fill="#d4c49f" ${OL(2.2)}/><rect x="114" y="26" width="68" height="18" rx="9" fill="#d4c49f" ${OL(2.2)}/></pattern></defs>
  <rect width="1280" height="720" fill="url(#${id}c)"/><circle cx="1050" cy="120" r="36" fill="#fff3d0" opacity=".9"/>
  <g class="l0"><path d="M-100 470 Q300 330 700 440 Q1000 360 1500 450 V720 H-100z" fill="#cdbb9f" ${OL(3)}/><g transform="translate(-10,340) scale(.55)">${partenon(0,0)}</g></g>
  <g class="l1">${casas(-120,18,23,560,1.0,"#b6644a","#f3ece0")}</g>
  <g class="l2"><rect x="-200" y="560" width="2400" height="200" fill="url(#${id}rua)"/><rect x="-200" y="560" width="2400" height="5" fill="#2a2018"/></g>`; }
function onda(y,cor,amp){ let d=`M-300 ${y}`; for(let i=0;i<16;i++) d+=` q60 ${i%2?amp:-amp} 120 0`; return `<path d="${d} V760 H-300z" fill="${cor}" ${OL(3)}/>`; }
// Stoa Poikile: parede com painéis pintados (.l0) e colunata (.l1) para a câmera deslizar
function bgPortico(id){ let pn="", co=""; const r=rng(77); const cores=["#b8402f","#2f4a63","#c99a2e","#3d6a5a"];
  for(let i=0;i<8;i++){ const x=i*300-120; let fig="";
    for(let k=0;k<3;k++){ const fx=x+60+k*72, c=cores[Math.floor(r()*4)]; fig+=`<g transform="translate(${fx},420)"><ellipse cy="-30" rx="18" ry="30" fill="${c}" ${OL(2.5)}/><circle cy="-70" r="13" fill="#d9a77f" ${OL(2.5)}/><path d="M18 -40 l${20+Math.floor(r()*16)} ${-24+Math.floor(r()*10)}" stroke="#2a2018" stroke-width="4" stroke-linecap="round"/></g>`; }
    pn+=`<rect x="${x}" y="220" width="270" height="210" fill="#efe3c3" ${OL(4)}/><rect x="${x+9}" y="229" width="252" height="192" fill="#dcc99c"/>${fig}`; }
  for(let i=0;i<11;i++) co+=coluna(i*210-120,650,430,58);
  return `<defs><linearGradient id="${id}c" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#bcd0d6"/><stop offset="1" stop-color="#f1e4c4"/></linearGradient></defs><rect width="1280" height="720" fill="url(#${id}c)"/>
  <g class="l0"><rect x="-300" y="190" width="3200" height="260" fill="#c9b283" ${OL(4)}/>${pn}</g><g class="l2"><rect x="-300" y="640" width="3200" height="100" fill="#d3c7a8"/><rect x="-300" y="640" width="3200" height="5" fill="#2a2018"/></g><g class="l1">${co}</g>`; }

// =====================================================================
//  CAPÍTULO 3 — ícones (biblioteca crescente) e cenário de montanha
// =====================================================================
function ic(n,x,y,e){ const o=OL, G=(s)=>`<g transform="translate(${x},${y}) scale(${e||1})">${s}</g>`;
  switch(n){
  case "opiniao": case "balao": return G(`<path d="M-50 -34 h100 a14 14 0 0 1 14 14 v44 a14 14 0 0 1 -14 14 h-62 l-26 24 v-24 h-12 a14 14 0 0 1 -14 -14 v-44 a14 14 0 0 1 14 -14z" fill="#fff6dc" ${o(4)}/><path d="M-34 -12 h68 M-34 8 h46" stroke="#2a2018" stroke-width="4.5" stroke-linecap="round"/>`);
  case "escolhas": return G(`<path d="M0 54 V4 M0 4 L-42 -36 M0 4 L42 -36" stroke="#2a2018" stroke-width="9" stroke-linecap="round" fill="none"/><path d="M-42 -62 l-26 28 h52z M42 -62 l-26 28 h52z" fill="#d8aa3a" ${o(3.5)}/>`);
  case "atitude": return G(`<g transform="rotate(180) scale(2.1) translate(0,-10)">${mao("#e2b48a")}</g>`);
  case "resposta": return G(`<path d="M-44 30 V-8 q0 -34 34 -34 h40" fill="none" stroke="#2a2018" stroke-width="10" stroke-linecap="round"/><path d="M26 -70 l36 28 l-36 28z" fill="#d8aa3a" ${o(3.5)}/>`);
  case "pensam": return G(`<circle cx="-22" cy="16" r="28" fill="#c9b38a" ${o(4)}/><path d="M-62 60 q0 -30 40 -30 q40 0 40 30z" fill="#c9b38a" ${o(4)}/><ellipse cx="36" cy="-34" rx="38" ry="24" fill="#fff6dc" ${o(3.5)}/><circle cx="6" cy="-6" r="6" fill="#fff6dc" ${o(3)}/>`);
  case "clima": return G(`<path d="M-56 12 q-6 -34 28 -34 q10 -30 44 -22 q34 4 30 36 q22 6 14 30 h-110 q-22 0 -6 -10z" fill="#b8c4d2" ${o(4)}/>${[-30,0,30].map(x=>`<path d="M${x} 24 l-8 26" stroke="#4a7ab0" stroke-width="6" stroke-linecap="round"/>`).join("")}`);
  case "economia": return G(`${[0,1,2].map(i=>`<ellipse cx="-26" cy="${34-i*16}" rx="30" ry="10" fill="#d8aa3a" ${o(3.5)}/>`).join("")}<path d="M6 34 l22 -22 l16 14 l26 -44" stroke="#3d6a5a" stroke-width="9" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="M52 -26 l16 2 l-6 16z" fill="#3d6a5a"/>`);
  case "publica": return G(`<path d="M-46 -14 h26 l50 -34 v100 l-50 -34 h-26z" fill="#e3b53a" ${o(4)}/><rect x="-62" y="-14" width="16" height="38" rx="5" fill="#c0302f" ${o(3.5)}/><path d="M42 -22 q16 22 0 44 M54 -34 q26 34 0 68" fill="none" stroke="#2a2018" stroke-width="5" stroke-linecap="round"/>`);
  case "passado": return G(`<path d="M-34 -52 h68 M-34 52 h68" stroke="#2a2018" stroke-width="9" stroke-linecap="round"/><path d="M-26 -48 q0 36 26 48 q-26 12 -26 48 h52 q0 -36 -26 -48 q26 -12 26 -48z" fill="#f6efdf" ${o(4)}/><path d="M-14 36 q14 -10 28 0 v12 h-28z" fill="#d8aa3a"/>`);
  case "resultado": return G(`<circle r="54" fill="#fff6dc" ${o(4)}/><circle r="36" fill="#c0302f" ${o(3)}/><circle r="18" fill="#fff6dc" ${o(3)}/><path d="M0 0 L50 -50" stroke="#2a2018" stroke-width="7" stroke-linecap="round"/><path d="M38 -66 l28 4 l-4 28z" fill="#3d6a5a" ${o(3)}/>`);
  case "casa": return G(`<path d="M-56 -8 L0 -56 L56 -8z" fill="#b6644a" ${o(4)}/><rect x="-44" y="-8" width="88" height="62" fill="#f3ece0" ${o(4)}/><rect x="-12" y="14" width="26" height="40" fill="#5a3f2e" ${o(3.5)}/>`);
  case "martelo": return G(`<rect x="-8" y="-34" width="16" height="92" rx="5" fill="#8a6a46" ${o(4)}/><rect x="-44" y="-58" width="88" height="34" rx="8" fill="#9aa0a8" ${o(4)}/>`);
  case "coracao": case "curtida": return G(`<path d="M0 50 C-70 -4 -44 -54 0 -22 C44 -54 70 -4 0 50z" fill="#c0302f" ${o(4)}/>`);
  case "publicar": return G(`<rect x="-46" y="-40" width="92" height="82" rx="10" fill="#fff6dc" ${o(4)}/><path d="M-26 -14 h52 M-26 4 h52 M-26 22 h30" stroke="#8a7a5a" stroke-width="4.5" stroke-linecap="round"/><path d="M30 46 l40 -40 l16 16 l-40 40 l-24 8z" fill="#e3b53a" ${o(3.5)}/>`);
  case "sorriso": return G(`<circle r="52" fill="#f3cf5a" ${o(4)}/><circle cx="-18" cy="-12" r="6" fill="#2a2018"/><circle cx="18" cy="-12" r="6" fill="#2a2018"/><path d="M-26 14 q26 30 52 0" fill="none" stroke="#2a2018" stroke-width="6" stroke-linecap="round"/>`);
  case "sol": return G(`${[...Array(10)].map((_,i)=>`<path transform="rotate(${i*36})" d="M0 -46 v-22" stroke="#e3a33a" stroke-width="7" stroke-linecap="round"/>`).join("")}<circle r="36" fill="#f3cf5a" ${o(4)}/>`);
  case "celular": return G(`<rect x="-26" y="-48" width="52" height="96" rx="9" fill="#2a3040" ${o(4)}/><rect x="-19" y="-38" width="38" height="68" rx="4" fill="#9ec3ff"/><circle cy="39" r="4" fill="#cfd4d8"/>`);
  case "polegar": return G(`<path d="M-30 -6 h36 l22 -36 q16 4 12 28 l-6 14 h26 q14 4 8 20 l-14 30 q-6 12 -20 12 h-64z" fill="#e2b48a" ${o(4)} transform="scale(1,-1)"/>`);
  case "sino": return G(`<path d="M-40 30 q8 -14 8 -48 q0 -32 32 -32 q32 0 32 32 q0 34 8 48z" fill="#e3b53a" ${o(4)}/><circle cy="40" r="9" fill="#8a6a1e" ${o(3)}/><circle cx="32" cy="-44" r="12" fill="#c0302f" ${o(3)}/>`);
  case "relogio": return G(`<circle r="46" fill="#f6efdf" ${o(4.5)}/><path d="M0 0 V-30 M0 0 L22 10" stroke="#2a2018" stroke-width="6" stroke-linecap="round"/>`);
  } return ic2(n,x,y,e); }
function bgMontanha(id){ return `<defs><linearGradient id="${id}c" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#cfe0ea"/><stop offset="1" stop-color="#f6e7c6"/></linearGradient></defs><rect width="1280" height="720" fill="url(#${id}c)"/><circle cx="1050" cy="130" r="40" fill="#fff3d0" opacity=".9"/>
  <g class="l0"><path d="M-100 720 L300 380 L430 470 L560 300 L640 380 L700 150 L980 480 L1100 400 L1400 720z" fill="#9aa0aa" ${OL(4)}/><path d="M700 150 L640 244 L676 232 L700 262 L730 228 L762 244z" fill="#fbfbf8" ${OL(3.5)}/><path d="M-100 720 L240 520 L420 640 L560 560 L760 700 L900 600 L1400 720z" fill="#7d8a72" ${OL(4)}/></g>
  <g class="l2"><rect x="-200" y="690" width="1900" height="60" fill="#6d7a5e"/><rect x="-200" y="688" width="1900" height="4" fill="#2a2018"/></g>`; }

// =====================================================================
//  CAPÍTULO 4 — ícones adicionais (ic2 estende ic: nomes novos; ic() chama ic2 quando não conhece o nome)
// =====================================================================
function ic2(n,x,y,e){ const o=OL, G=(s)=>`<g transform="translate(${x},${y}) scale(${e||1})">${s}</g>`;
  switch(n){
  case "gema": return G(`<path d="M-48 -14 L-22 -48 H22 L48 -14 L0 52z" fill="#7fc4e8" ${o(4)}/><path d="M-48 -14 H48 M-22 -48 L-10 -14 L0 52 M22 -48 L10 -14 L0 52" stroke="#2a2018" stroke-width="3.5" fill="none"/>`);
  case "bau": return G(`<rect x="-54" y="-8" width="108" height="56" rx="8" fill="#8a5a3a" ${o(4)}/><path d="M-54 -8 q0 -40 54 -40 q54 0 54 40z" fill="#a8703f" ${o(4)}/><rect x="-10" y="-14" width="20" height="26" rx="4" fill="#e3b53a" ${o(3.5)}/><path d="M-54 18 H54" stroke="#2a2018" stroke-width="3.5"/>`);
  case "calendario": return G(`<rect x="-52" y="-48" width="104" height="100" rx="10" fill="#fff6dc" ${o(4)}/><rect x="-52" y="-48" width="104" height="26" rx="10" fill="#c0302f" ${o(4)}/>${[-28,0,28].map(a=>[0,1].map(b=>`<rect x="${a-10}" y="${-8+b*28}" width="20" height="16" rx="3" fill="#d8c79c"/>`).join("")).join("")}`);
  case "discussao": return G(`<path d="M-62 -34 h64 a12 12 0 0 1 12 12 v28 a12 12 0 0 1 -12 12 h-34 l-18 16 v-16 h-12 a12 12 0 0 1 -12 -12 v-28 a12 12 0 0 1 12 -12z" fill="#f6c8c0" ${o(3.5)}/><path d="M-6 -10 h72 a12 12 0 0 1 12 12 v28 a12 12 0 0 1 -12 12 h-12 v16 l-18 -16 h-42 a12 12 0 0 1 -12 -12 v-28 a12 12 0 0 1 12 -12z" fill="#c8d8f6" ${o(3.5)} transform="translate(0,16)"/><text x="-30" y="2" text-anchor="middle" font-family="CinzelX" font-weight="700" font-size="34" fill="#c0302f">!</text>`);
  case "curtir": return G(`<g transform="scale(1,1)"><path d="M-44 4 h30 l18 -46 q18 4 14 26 l-4 20 h34 q16 4 10 22 l-14 34 q-6 12 -18 12 h-70z" fill="#e2b48a" ${o(4)}/><rect x="-60" y="2" width="24" height="68" rx="6" fill="#3a7bd5" ${o(4)}/></g>`);
  case "bateria": return G(`<rect x="-56" y="-26" width="104" height="52" rx="10" fill="#fff6dc" ${o(4.5)}/><rect x="48" y="-12" width="12" height="24" rx="4" fill="#2a2018"/><rect x="-48" y="-18" width="30" height="36" rx="4" fill="#3d6a5a"/><rect x="-14" y="-18" width="30" height="36" rx="4" fill="#3d6a5a"/><rect x="20" y="-18" width="20" height="36" rx="4" fill="#3d6a5a"/>`);
  case "laptop": return G(`<rect x="-50" y="-40" width="100" height="64" rx="6" fill="#dfe6ee" ${o(4)}/><rect x="-42" y="-32" width="84" height="48" rx="3" fill="#6a86b0"/><path d="M-62 24 h124 l-10 18 h-104z" fill="#aeb6c0" ${o(4)}/>`);
  case "sacola": return G(`<path d="M-40 -20 h80 l8 66 h-96z" fill="#c0302f" ${o(4)}/><path d="M-20 -20 q0 -34 20 -34 q20 0 20 34" fill="none" stroke="#2a2018" stroke-width="6"/>`);
  case "estrela": return G(`<path d="M0 -54 L16 -18 L56 -14 L26 12 L36 52 L0 30 L-36 52 L-26 12 L-56 -14 L-16 -18z" fill="#f3cf5a" ${o(4)}/>`);
  case "bandeira": return G(`<path d="M-6 52 V-52" stroke="#2a2018" stroke-width="8" stroke-linecap="round"/><path d="M-6 -52 h58 l-16 20 l16 20 h-58z" fill="#c0302f" ${o(4)}/>`);
  case "alerta": return G(`<path d="M0 -54 L56 44 H-56z" fill="#f3cf5a" ${o(5)}/><path d="M0 -20 V16" stroke="#2a2018" stroke-width="9" stroke-linecap="round"/><circle cy="32" r="6" fill="#2a2018"/>`);
  case "coroa": return G(`<path d="M-50 36 l-8 -70 l30 30 l28 -44 l28 44 l30 -30 l-8 70z" fill="#e3b53a" ${o(4)}/>${[-28,0,28].map(a=>`<circle cx="${a}" cy="22" r="6" fill="#c0302f" ${o(2.5)}/>`).join("")}`);
  case "pergaminho": return G(`<rect x="-44" y="-44" width="88" height="88" rx="6" fill="#efe3c3" ${o(4)}/><path d="M-26 -22 h52 M-26 -4 h52 M-26 14 h34" stroke="#8a7a5a" stroke-width="4.5" stroke-linecap="round"/><path d="M30 46 l32 -44 l12 10 l-30 44z" fill="#f1ead8" ${o(3.5)}/>`);
  case "senado": return G(`<path d="M-58 -26 L0 -56 L58 -26z" fill="#e3d7bc" ${o(4)}/>${[-40,-14,14,40].map(a=>`<rect x="${a-7}" y="-22" width="14" height="62" fill="#efe6d2" ${o(3.5)}/>`).join("")}<rect x="-62" y="40" width="124" height="14" fill="#d3c7a8" ${o(4)}/>`);
  } return ic3(n,x,y,e); }

// =====================================================================
//  ÍCONES — lote 3 (capítulos 5 a 11). ic2() cai aqui via ic3().
// =====================================================================
function ic3(n,x,y,e){ const o=OL, G=(s)=>`<g transform="translate(${x},${y}) scale(${e||1})">${s}</g>`;
  switch(n){
  case "espadas": return icEspadas(x,y,(e||1)*.8);
  case "punhal": return icPunhal(x,y,(e||1)*.8);
  case "peste": return icPeste(x,y,(e||1)*.8);
  case "multidao": return icMultidao(x,y,e);
  case "pedra": return G(`<path d="M-54 18 q-14 -46 30 -58 q40 -16 66 14 q22 30 -4 52 q-40 20 -92 -8z" fill="#aeb2b8" ${o(4.5)}/><path d="M-20 -20 q16 -8 34 2 M-30 4 q20 6 44 -2" stroke="#7d828a" stroke-width="4" fill="none" stroke-linecap="round"/>`);
  case "lagrima": return G(`<path d="M0 -58 C34 -14 44 10 40 28 q-6 30 -40 30 q-34 0 -40 -30 C-44 10 -34 -14 0 -58z" fill="#7fb4e8" ${o(4.5)}/><path d="M-14 14 q0 14 12 18" stroke="#fff" stroke-width="5" fill="none" stroke-linecap="round"/>`);
  case "raiva": return G(`<path d="M-8 -58 L-40 6 h28 l-12 50 L40 -10 h-30 l16 -48z" fill="#f3cf5a" ${o(4.5)}/>`);
  case "curativo": return G(`<g transform="rotate(-35)"><rect x="-58" y="-22" width="116" height="44" rx="22" fill="#e8c9a4" ${o(4)}/><rect x="-22" y="-22" width="44" height="44" fill="#d8b088" ${o(3)}/><circle cx="-8" cy="-6" r="3" fill="#8a6a46"/><circle cx="8" cy="6" r="3" fill="#8a6a46"/></g>`);
  case "escudo": return G(`<path d="M0 -58 L50 -38 V8 q0 34 -50 56 q-50 -22 -50 -56 V-38z" fill="#7a9ccb" ${o(4.5)}/><path d="M0 -40 L32 -27 V6 q0 22 -32 38z" fill="#a8c3e6"/>`);
  case "pao": return G(`<path d="M-56 22 q-6 -52 56 -52 q62 0 56 52 q0 20 -20 20 h-72 q-20 0 -20 -20z" fill="#d8a85a" ${o(4.5)}/><path d="M-26 -10 l10 22 M0 -14 l10 24 M26 -10 l10 22" stroke="#8a6a2e" stroke-width="5" stroke-linecap="round"/>`);
  case "tunica": return G(`<path d="M-26 -52 L-60 -20 L-40 4 L-30 -6 V54 H30 V-6 L40 4 L60 -20 L26 -52 q-26 14 -52 0z" fill="#efe6d2" ${o(4.5)}/><path d="M-30 30 H30" stroke="#8a6a46" stroke-width="7"/>`);
  case "fantasma": return G(`<path d="M-44 56 V-6 q0 -52 44 -52 q44 0 44 52 V56 l-15 -14 l-15 14 l-14 -14 l-14 14 l-15 -14z" fill="none" stroke="#2a2018" stroke-width="5" stroke-dasharray="10 9" stroke-linecap="round"/><circle cx="-16" cy="-10" r="6" fill="#2a2018" opacity=".5"/><circle cx="16" cy="-10" r="6" fill="#2a2018" opacity=".5"/>`);
  case "globo": return G(`<circle r="58" fill="#6aa3d8" ${o(4.5)}/><path d="M-30 -30 q22 -16 36 4 q-6 22 -26 16z M10 6 q24 -8 34 14 q-6 22 -30 14z M-42 22 q14 -8 22 6 q-8 14 -22 6z" fill="#7dbf7a" ${o(3)}/>`);
  case "coracaoPartido": return G(`<path d="M0 50 C-70 -4 -44 -54 0 -22 C44 -54 70 -4 0 50z" fill="#c0302f" ${o(4.5)}/><path d="M0 -22 l-12 22 l16 12 l-12 22" stroke="#fff6dc" stroke-width="6" fill="none" stroke-linecap="round" stroke-linejoin="round"/>`);
  case "balanca": return G(`<path d="M0 -56 V44 M-34 52 h68" stroke="#2a2018" stroke-width="8" stroke-linecap="round"/><path d="M-56 -30 h112" stroke="#2a2018" stroke-width="8" stroke-linecap="round"/>${[-56,56].map(a=>`<path d="M${a} -30 L${a-24} 14 h48z" fill="#e3b53a" ${o(3.5)}/>`).join("")}`);
  case "aviao": return G(`<path d="M-56 4 L-8 -8 L-26 -50 h14 L22 -10 L54 -22 q10 0 6 10 q-4 8 -34 22 L24 42 h-14 L-8 14 L-48 24z" fill="#dfe6ee" ${o(4)}/>`);
  case "chip": return G(`<rect x="-40" y="-40" width="80" height="80" rx="8" fill="#3a4a62" ${o(4.5)}/><rect x="-22" y="-22" width="44" height="44" rx="4" fill="#7fb4e8"/>${[-26,0,26].map(a=>`<path d="M${a} -40 v-14 M${a} 40 v14 M-40 ${a} h-14 M40 ${a} h14" stroke="#2a2018" stroke-width="5" stroke-linecap="round"/>`).join("")}`);
  case "olho": return G(`<path d="M-62 0 q62 -64 124 0 q-62 64 -124 0z" fill="#fff6dc" ${o(4.5)}/><circle r="22" fill="#4a3224" ${o(3)}/><circle cx="6" cy="-6" r="6" fill="#fff"/>`);
  case "livro": return G(`<rect x="-44" y="-52" width="88" height="104" rx="6" fill="#7a2e2e" ${o(4.5)}/><rect x="-44" y="-52" width="14" height="104" fill="#5a1f1f"/><path d="M-16 -26 h40 M-16 -10 h40" stroke="#e3b53a" stroke-width="5" stroke-linecap="round"/>`);
  case "porta": return G(`<rect x="-40" y="-60" width="80" height="116" rx="8" fill="#8a5a3a" ${o(4.5)}/><rect x="-26" y="-46" width="52" height="40" rx="4" fill="#a8703f"/><circle cx="22" cy="14" r="6" fill="#e3b53a"/>`);
  case "sofa": return G(`<rect x="-58" y="-6" width="116" height="40" rx="12" fill="#b8402f" ${o(4.5)}/><rect x="-46" y="-40" width="92" height="40" rx="12" fill="#c8513f" ${o(4.5)}/><rect x="-62" y="-14" width="22" height="52" rx="10" fill="#a8362a" ${o(4)}/><rect x="40" y="-14" width="22" height="52" rx="10" fill="#a8362a" ${o(4)}/>`);
  case "solo": return G(`<circle cy="-34" r="22" fill="#c9b38a" ${o(4.5)}/><path d="M-40 52 q0 -50 40 -50 q40 0 40 50z" fill="#c9b38a" ${o(4.5)}/>`);
  } return ""; }
