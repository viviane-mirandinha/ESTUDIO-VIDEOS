// motor.js — peças de personagem, movimento e utilitários do modelo animacao-2d. NÃO edite dentro de um vídeo:
// melhore aqui, no kit, para todos os vídeos herdarem (e rode checar_movimento.mjs).
function rng(seed){ let s = seed>>>0; return ()=> (s = (s*1664525 + 1013904223)>>>0) / 4294967296; }
const LN="#2a2018", LW=3.5;                       // CONTORNO GROSSO PADRÃO (igual ao original: ~3–4 px em tudo)
const ST=`stroke="${LN}" stroke-width="${LW}" stroke-linejoin="round" stroke-linecap="round"`;
const PADRAO={tunica:"#efe6d2",faixa:"#cdb98e",capa:"#8c2f2f",pele:"#e2b48a",pele2:"#c99c74",cabelo:"#4e3b2e",barba:"#4e3b2e",louro:true,coroa:false,barriga:0,sandalia:"#6b4a2c",escala:1,flip:false,x:0,y:0,silhueta:null};
function envolve(id,o,corpo){ return `<g id="${id}" transform="translate(${o.x},${o.y})"><g class="esc" transform="scale(${o.flip?-o.escala:o.escala},${o.escala})"><g class="bob">${corpo}</g></g></g>`; }
function louros(){ return `<g fill="none" stroke="#b8861f" stroke-width="5" stroke-linecap="round"><path d="M-38 -56 q38 -36 76 0"/></g><g fill="#d8aa3a" stroke="${LN}" stroke-width="1.5">${[-32,-21,-10,2,14,26,36].map((x,i)=>`<ellipse cx="${x}" cy="${-70-Math.sin((x+38)/76*Math.PI)*22+22}" rx="7" ry="3.4" transform="rotate(${(i-3)*14} ${x} -74)"/>`).join("")}</g>`; }
// mão com dedos (origem = pulso, aponta para baixo)
function mao(cor){ return `<g><path d="M-10 -2 q-4 16 0 24 q10 7 20 0 q4 -8 0 -24z" fill="${cor}" ${ST}/><path d="M-6 22 v9 M-1 23 v11 M4 22 v9" stroke="${LN}" stroke-width="3" fill="none" stroke-linecap="round"/><path d="M-10 6 q-8 6 -6 14" stroke="${LN}" stroke-width="3.2" fill="none" stroke-linecap="round"/></g>`; }

function pessoa(id,o){
  o=Object.assign({},PADRAO,o||{}); const sil=o.silhueta, T=sil||o.tunica, P=sil||o.pele, C=sil||o.capa, bw=40+o.barriga, S=sil?'stroke="none"':ST;
  const perna=(s)=>`<g transform="translate(${s*14},-128)"><g class="${s<0?'legA':'legB'}"><rect x="-11" y="0" width="22" height="112" rx="10" fill="${P}" ${S}/><path d="M-15 110 h34 q7 0 7 9 v5 h-41z" fill="${sil||o.sandalia}" ${S}/>${sil?"":`<path d="M-8 100 h18" stroke="${LN}" stroke-width="2.5"/>`}</g></g>`;
  const braco=(s)=>`<g transform="translate(${s*(bw-4)},-246)"><g class="${s<0?'armA':'armB'}"><rect x="-10" y="-4" width="20" height="90" rx="10" fill="${P}" ${S}/><rect x="-14" y="-7" width="28" height="48" rx="13" fill="${T}" ${S}/><g transform="translate(0,84)">${sil?`<circle r="11" fill="${P}"/>`:mao(P)}</g></g></g>`;
  const cabeca=`<g transform="translate(0,-262)"><g class="head"><rect x="-10" y="-2" width="20" height="24" fill="${sil?P:o.pele2}" ${S}/>
    ${sil?"":`<ellipse cx="-36" cy="-36" rx="6" ry="10" fill="${P}" ${S}/><ellipse cx="36" cy="-36" rx="6" ry="10" fill="${P}" ${S}/>`}
    <ellipse cx="0" cy="-38" rx="36" ry="42" fill="${P}" ${S}/>
    ${sil?"":`<path d="M-38 -44 q0 -44 38 -46 q38 2 38 46 q-8 -26 -38 -28 q-30 2 -38 28z" fill="${o.cabelo}" ${ST}/>
    <path d="M-34 -22 q-4 44 34 52 q38 -8 34 -52 q-10 18 -34 20 q-24 -2 -34 -20z" fill="${o.barba}" ${ST}/>
    <path d="M-20 14 q6 6 12 0 M2 16 q6 6 12 -2 M-10 24 q10 6 20 0" stroke="${LN}" stroke-width="2" fill="none" opacity=".5"/>
    <ellipse cx="0" cy="-30" rx="7" ry="8" fill="${o.pele2}" ${ST.replace('3.5','2.5')}/>
    <path class="boca" d="M-12 -4 q12 6 24 0" stroke="${LN}" stroke-width="3" fill="none" stroke-linecap="round"/>
    <g class="eyes"><ellipse cx="-15" cy="-42" rx="6" ry="7" fill="#fff" stroke="${LN}" stroke-width="2"/><ellipse cx="15" cy="-42" rx="6" ry="7" fill="#fff" stroke="${LN}" stroke-width="2"/><g class="pup"><circle cx="-14" cy="-41" r="3" fill="#2a1f17"/><circle cx="16" cy="-41" r="3" fill="#2a1f17"/></g></g>
    <g class="brows"><path d="M-24 -53 q10 -5 18 0 M6 -53 q10 -5 18 0" stroke="#7a6a5a" stroke-width="5" fill="none" stroke-linecap="round"/></g>
    <path d="M14 -76 q22 14 20 52 q-4 -20 -20 -34z" fill="#000" opacity=".07"/>`}
    ${(o.louro&&!sil)?louros():""}
    ${o.coroa?`<path d="M-28 -76 l-4 -28 l17 13 l15 -23 l15 23 l17 -13 l-4 28z" fill="#e3b53a" ${ST}/>`:""}
    </g></g>`;
  const corpo=`<g class="torso">${(!sil&&o.capa)?`<path class="capa" d="M${-bw-10} -252 q-10 72 -6 154 h${bw*2+20} q6 -82 -4 -154z" fill="${C}" ${S}/>`:""}
    <path d="M${-bw} -254 q-6 70 -8 152 h${bw*2+16} q-2 -82 -8 -152 q-${bw} -14 -${bw*2} 0z" fill="${T}" ${S}/>
    ${sil?"":`<path d="M${-bw+6} -250 l22 0 l${bw+8} 100 l-26 0z" fill="${o.faixa}" ${ST}/><rect x="${-bw-8}" y="-118" width="${bw*2+16}" height="14" fill="${o.faixa}" ${ST}/>
    <path d="M-14 -190 q-4 40 -2 70 M12 -196 q6 40 4 76 M-28 -170 q-2 30 0 56" stroke="${LN}" stroke-width="2" fill="none" opacity=".35"/>`}
    ${(!sil&&o.capa)?`<path d="M${-bw} -254 q${bw} 18 ${bw*2} 0 l-10 60 q-${bw-10} -22 -${bw*2-30} 0z" fill="${C}" ${ST}/><circle cx="${bw-12}" cy="-226" r="6" fill="#d8aa3a" ${ST.replace('3.5','2')}/>`:""}
    ${(!sil&&o.coroa)?`<path d="M-24 -246 q24 30 48 0" stroke="#e3b53a" stroke-width="7" fill="none"/><circle cx="0" cy="-222" r="9" fill="#e3b53a" ${ST}/>`:""}</g>`;
  return envolve(id,o,perna(-1)+perna(1)+braco(1)+corpo+cabeca+braco(-1));
}

// perfil olhando para a DIREITA (flip:true = esquerda)
function lado(id,o){
  o=Object.assign({},PADRAO,o||{}); const S=ST;
  const perna=(cls,cor)=>o.sentado?`<g class="${cls}"><g transform="translate(${cls==="legB"?10:0},0)"><rect x="-8" y="-118" width="84" height="26" rx="12" fill="${cor}" ${S}/><rect x="52" y="-108" width="24" height="106" rx="10" fill="${cor}" ${S}/><path d="M48 -6 h42 q8 0 8 9 v4 h-50z" fill="${o.sandalia}" ${S}/></g></g>`:`<g transform="translate(0,-128)"><g class="${cls}"><rect x="-10" y="0" width="21" height="112" rx="9" fill="${cor}" ${S}/><path d="M-13 110 h38 q8 0 8 9 v5 h-46z" fill="${o.sandalia}" ${S}/></g></g>`;
  const braco=(cls,cor,tun)=>`<g transform="translate(0,-244)"><g class="${cls}"><rect x="-9" y="-4" width="18" height="88" rx="9" fill="${cor}" ${S}/><rect x="-13" y="-7" width="26" height="44" rx="12" fill="${tun}" ${S}/><g transform="translate(0,82)">${mao(cor)}</g></g></g>`;
  const cabeca=`<g transform="translate(2,-262)"><g class="head"><rect x="-9" y="-2" width="18" height="24" fill="${o.pele2}" ${S}/>
    <ellipse cx="0" cy="-38" rx="33" ry="40" fill="${o.pele}" ${S}/><path d="M30 -42 q16 4 10 16 q-4 5 -12 3z" fill="${o.pele}" ${S}/>
    <path d="M-35 -38 q0 -48 35 -48 q28 2 33 28 q-14 -16 -36 -14 q-20 4 -32 34z" fill="${o.cabelo}" ${S}/>
    <path d="M-24 -24 q8 46 46 34 q10 -12 10 -26 q-20 12 -40 -4z" fill="${o.barba}" ${S}/>
    <ellipse cx="-8" cy="-34" rx="6" ry="9" fill="${o.pele2}" ${ST.replace('3.5','2.5')}/>
    <g class="eyes"><ellipse cx="15" cy="-42" rx="6.5" ry="8" fill="#fff" stroke="${LN}" stroke-width="2"/><circle cx="17" cy="-41" r="3.4" fill="#2a1f17"/></g>
    <path d="M8 -54 q9 -6 18 0" stroke="#7a6a5a" stroke-width="5" fill="none" stroke-linecap="round"/>
    <path d="M24 -10 q6 2 11 0" stroke="${LN}" stroke-width="3" fill="none" stroke-linecap="round"/>
    <path d="M-26 -58 q30 -32 60 -8" fill="none" stroke="#b8861f" stroke-width="5" stroke-linecap="round"/>
    ${[-22,-11,0,11,22].map((x,i)=>`<ellipse cx="${x}" cy="${-72+Math.abs(x)*.12}" rx="6.5" ry="3.2" fill="#d8aa3a" stroke="${LN}" stroke-width="1.4" transform="rotate(${-20+i*10} ${x} -72)"/>`).join("")}
    </g></g>`;
  const capa=o.capa?`<g class="capa"><path d="M-4 -252 q-56 14 -64 170 q10 36 28 42 q4 -94 42 -150z" fill="${o.capa}" ${S}/><path d="M-30 -204 q-14 50 -16 102 M-14 -220 q-10 60 -8 120" stroke="#5a1a1a" stroke-width="2.5" fill="none"/></g>`:"";
  const torso=`<g class="torso"><path d="M-23 -254 q-8 72 -8 152 h66 q0 -82 -6 -152 q-26 -10 -52 0z" fill="${o.tunica}" ${S}/><path d="M-23 -250 l22 0 l30 100 l-26 0z" fill="${o.faixa}" ${ST}/><rect x="-33" y="-118" width="70" height="14" fill="${o.faixa}" ${ST}/><path d="M-22 -254 q27 8 50 0 l-8 56 q-18 -12 -36 0z" fill="${o.capa||o.faixa}" ${ST}/><circle cx="14" cy="-228" r="5.5" fill="#d8aa3a" ${ST.replace('3.5','2')}/></g>`;
  return envolve(id,o,perna("legB",o.pele2)+braco("armB",o.pele2,"#d9ceb6")+capa+torso+perna("legA",o.pele)+cabeca+braco("armA",o.pele,o.tunica));
}

// de costas
function costas(id,o){
  o=Object.assign({},PADRAO,o||{}); const S=ST;
  const perna=(s)=>`<g transform="translate(${s*14},-128)"><g class="${s<0?'legA':'legB'}"><rect x="-11" y="0" width="22" height="112" rx="10" fill="${o.pele}" ${S}/><path d="M-15 110 h34 q7 0 7 9 v5 h-41z" fill="${o.sandalia}" ${S}/></g></g>`;
  const braco=(s)=>`<g transform="translate(${s*46},-246)"><g class="${s<0?'armA':'armB'}"><rect x="-10" y="-4" width="20" height="90" rx="10" fill="${o.pele}" ${S}/><rect x="-14" y="-7" width="28" height="48" rx="13" fill="${o.tunica}" ${S}/><g transform="translate(0,84)">${mao(o.pele)}</g></g></g>`;
  const corpo=`<g class="capa"><path d="M-48 -254 q-10 92 -12 172 q60 12 120 0 q-2 -82 -12 -172 q-48 -16 -96 0z" fill="${o.capa}" ${S}/><path d="M-22 -232 q-4 82 -6 142 M0 -238 v152 M22 -232 q4 82 6 142" stroke="#5a1a1a" stroke-width="2.5" fill="none"/><path d="M-60 -84 q60 12 120 0" stroke="#d8aa3a" stroke-width="5" fill="none"/></g>`;
  const cab=`<g transform="translate(0,-262)"><g class="head"><rect x="-10" y="-2" width="20" height="24" fill="${o.pele2}" ${S}/><ellipse cx="-35" cy="-36" rx="6" ry="10" fill="${o.pele}" ${S}/><ellipse cx="35" cy="-36" rx="6" ry="10" fill="${o.pele}" ${S}/>
    <ellipse cx="0" cy="-38" rx="36" ry="42" fill="${o.cabelo}" ${S}/><path d="M-22 -60 q10 -10 22 -4 M4 -66 q12 -4 20 6 M-26 -40 q8 -6 14 2" stroke="#2a1f17" stroke-width="2.5" fill="none" opacity=".6"/>
    ${louros()}<path d="M0 -68 q-6 22 -14 44 M0 -68 q9 20 16 42" stroke="#b8861f" stroke-width="4" fill="none"/></g></g>`;
  return envolve(id,o,perna(-1)+perna(1)+braco(1)+corpo+cab+braco(-1));
}


// ---------------------------------------------------------------------
//  MODERNO — pessoa de hoje (de frente). Desenho próprio do Estúdio (NÃO é o "cara de moletom" de nenhum canal).
//  o: {genero:"f"|"m", pele, cabelo, cabeloLuz, olho, camisa, jaqueta, calca, tenis, escala, flip, x, y}
//  Mesmo esqueleto dos outros (.legA .legB .armA .armB .head .eyes .pup .brows .bob .esc) → andar()/parado()/gesto() funcionam.
// ---------------------------------------------------------------------
function moderno(id,o){
  o=Object.assign({genero:"f",pele:"#e9bd98",pele2:"#d4a07a",cabelo:"#3a2822",cabeloLuz:"#5e4338",olho:"#4a3224",camisa:"#f2eadb",jaqueta:"#4f7396",jaqueta2:"#3f5f80",calca:"#2f3b52",tenis:"#f4f1ea",solado:"#cfc8b8",escala:1,flip:false,x:0,y:0},o||{});
  const f=o.genero==="f", bw=f?36:42, S=ST;
  const perna=(s)=>`<g transform="translate(${s*(f?13:15)},-126)"><g class="${s<0?'legA':'legB'}">
      <rect x="-12" y="0" width="24" height="110" rx="10" fill="${o.calca}" ${S}/><path d="M-1 8 v96" stroke="#1f2838" stroke-width="2" opacity=".5"/>
      <path d="M-16 106 h36 q8 0 8 10 v6 h-46 q-2 -10 2 -16z" fill="${o.tenis}" ${S}/><path d="M-18 119 h46" stroke="${o.solado}" stroke-width="6" stroke-linecap="round"/><path d="M-6 108 h14" stroke="#2a2018" stroke-width="2"/></g></g>`;
  const braco=(s)=>`<g transform="translate(${s*(bw-3)},-244)"><g class="${s<0?'armA':'armB'}">
      <rect x="-10" y="-4" width="20" height="88" rx="10" fill="${o.pele}" ${S}/>
      <rect x="-13" y="-8" width="26" height="62" rx="12" fill="${o.jaqueta}" ${S}/><rect x="-13" y="44" width="26" height="12" rx="5" fill="${o.jaqueta2}" ${S}/><path d="M-4 0 v40" stroke="${o.jaqueta2}" stroke-width="2.5" opacity=".7"/>
      <g transform="translate(0,84)">${mao(o.pele)}</g></g></g>`;
  const torso=`<g class="torso">
      <path d="M${-bw} -254 q-5 70 -6 150 h${bw*2+12} q-1 -80 -6 -150 q-${bw} -12 -${bw*2} 0z" fill="${o.camisa}" ${S}/>
      <path d="M-14 -250 q14 14 28 0 l-2 14 q-12 8 -24 0z" fill="${o.pele2}" ${ST.replace('3.5','2.5')}/>
      <path d="M${-bw} -254 q-2 40 ${f?-4:-6} 150 h${f?14:16} q-2 -80 12 -128 q-8 -14 -22 -22z" fill="${o.jaqueta}" ${S}/>
      <path d="M${bw} -254 q2 40 ${f?4:6} 150 h${f?-14:-16} q2 -80 -12 -128 q8 -14 22 -22z" fill="${o.jaqueta}" ${S}/>
      <path d="M${-bw+10} -236 q-4 40 -2 120 M${bw-10} -236 q4 40 2 120" stroke="${o.jaqueta2}" stroke-width="2.5" fill="none"/>
      <path d="M${-bw-6} -118 h${bw*2+12}" stroke="${o.jaqueta2}" stroke-width="10" stroke-linecap="round"/>
      <path d="M-10 -190 q6 24 0 50 M12 -196 q4 30 2 60" stroke="${LN}" stroke-width="2" fill="none" opacity=".25"/></g>`;
  const cabelo_tras=f?`<path d="M-44 -46 q-12 60 -4 112 q22 12 52 6 q30 6 52 -6 q8 -52 -4 -112 q-6 -52 -48 -54 q-42 2 -48 54z" fill="${o.cabelo}" ${S}/>`:"";
  const cabelo_frente=f
    ?`<path d="M-38 -48 q2 -40 38 -42 q36 2 38 42 q-10 -22 -22 -26 q-10 18 -34 22 q-10 0 -20 4z" fill="${o.cabelo}" ${S}/><path d="M-26 -78 q14 -10 34 -6 M-14 -70 q10 -6 22 -4" stroke="${o.cabeloLuz}" stroke-width="3.5" fill="none" stroke-linecap="round"/>`
    :`<path d="M-38 -46 q-2 -46 36 -48 q38 0 40 40 q-8 -14 -22 -18 q-18 6 -34 4 q-10 4 -20 22z" fill="${o.cabelo}" ${S}/><path d="M-22 -84 q18 -8 38 2" stroke="${o.cabeloLuz}" stroke-width="3.5" fill="none" stroke-linecap="round"/>`;
  const cabeca=`<g transform="translate(0,-262)"><g class="head">${cabelo_tras}
      <rect x="-9" y="-2" width="18" height="24" fill="${o.pele2}" ${S}/>
      <ellipse cx="-35" cy="-36" rx="5.5" ry="9" fill="${o.pele}" ${S}/><ellipse cx="35" cy="-36" rx="5.5" ry="9" fill="${o.pele}" ${S}/>
      <path d="M-35 -52 q-2 54 35 62 q37 -8 35 -62 q-4 -34 -35 -34 q-31 0 -35 34z" fill="${o.pele}" ${S}/>
      <ellipse cx="-20" cy="-18" rx="8" ry="5" fill="#e88a7a" opacity=".28"/><ellipse cx="20" cy="-18" rx="8" ry="5" fill="#e88a7a" opacity=".28"/>
      <g class="eyes"><ellipse cx="-14" cy="-40" rx="6" ry="7" fill="#fff" stroke="${LN}" stroke-width="1.8"/><ellipse cx="14" cy="-40" rx="6" ry="7" fill="#fff" stroke="${LN}" stroke-width="1.8"/>
        <g class="pup"><circle cx="-13" cy="-39" r="3.8" fill="${o.olho}"/><circle cx="15" cy="-39" r="3.8" fill="${o.olho}"/><circle cx="-12" cy="-41" r="1.2" fill="#fff"/><circle cx="16" cy="-41" r="1.2" fill="#fff"/></g>
        <path d="M-21 -45 q7 -5 14 0 M7 -45 q7 -5 14 0" stroke="${LN}" stroke-width="2.4" fill="none" stroke-linecap="round"/></g>
      <g class="brows"><path d="M-22 -54 q8 -6 16 -1 M6 -55 q8 -5 16 1" stroke="${o.cabelo}" stroke-width="3.6" fill="none" stroke-linecap="round"/></g>
      <path d="M0 -36 q-3 10 2 12" stroke="#b9805e" stroke-width="2.2" fill="none" stroke-linecap="round"/>
      <path class="boca" d="M-9 -8 q9 8 18 0" stroke="#8a3b3b" stroke-width="2.8" fill="none" stroke-linecap="round"/>
      ${cabelo_frente}</g></g>`;
  return envolve(id,o,perna(-1)+perna(1)+braco(1)+torso+cabeca+braco(-1));
}

// =====================================================================
//  ANIMAÇÃO DE PERSONAGEM — as ÚNICAS funções que mexem em perna/braço/posição.
//  (README.md explica por quê. Não crie animação de perna fora daqui.)
// =====================================================================
const existe=(sel)=>!!document.querySelector(sel);
function piscar(id,t,dur){ if(!existe(`#${id} .eyes`)) return;
  for(let k=t;k<t+dur-.2;k+=1.9){ tl.to(`#${id} .eyes`,{scaleY:.1,svgOrigin:"0 -36",duration:.07,yoyo:true,repeat:1},k); } }

// andar(): leva o personagem de a→b e PRENDE as pernas à distância percorrida.
//  - a, b = {x,y,s}: onde fica o PÉ e a escala. Anda até b e PARA (pernas juntas) no último quadro.
//  - número de passos é inteiro e par → termina sempre com os pés juntos (nada de patinar parado).
//  - o comprimento do passo é ~0,5 altura do corpo (o.passo muda). Velocidade = distância/D: escolha D para
//    ficar entre 0,4 e 1,3 alturas por segundo. O personagem vira para o lado em que anda.
//  - o.por (OBRIGATÓRIO): motivo narrativo da caminhada. Velocidade média máx 0,6 alturas/s (caminhada calma, nunca corrida).
//  - o.semBraco: não balança os braços (use quando a cena controla o braço, ex.: passar a mão nos livros).
function andar(id,S,D,a,b,o){
  o=o||{}; const E=gsap.parseEase(o.ease||"sine.inOut");
  if(!o.por) throw new Error(`andar(${id}): falta o motivo (o.por) — diga PARA ONDE ele vai e POR QUE a fala justifica (README, regra 1)`);
  const dist=Math.hypot(b.x-a.x,b.y-a.y), alt=300*(a.s+b.s)/2, passo=alt*(o.passo||.5);
  const vMed=dist/D/alt; if(vMed>.6) throw new Error(`andar(${id}): rápido demais (${vMed.toFixed(2)} alturas/s em média; máx 0,6 = passo de caminhada). Aumente a duração ou encurte a distância.`);
  const passos=Math.max(2,Math.round(dist/passo/2)*2), ciclos=passos/2, A=o.amp||24, f=(b.x<a.x)?-1:1;
  tl.fromTo(`#${id}`,{x:a.x,y:a.y},{x:b.x,y:b.y,duration:D,ease:E},S);
  tl.fromTo(`#${id} .esc`,{scaleX:f*a.s,scaleY:a.s,svgOrigin:"0 0"},{scaleX:f*b.s,scaleY:b.s,svgOrigin:"0 0",duration:D,ease:E},S);
  const fase=(p)=>Math.sin(2*Math.PI*ciclos*E(p));
  const osc=(sel,amp,org)=>{ if(!existe(`#${id} ${sel}`)) return;
    tl.fromTo(`#${id} ${sel}`,{rotation:0,svgOrigin:org||"0 0"},{rotation:amp,svgOrigin:org||"0 0",duration:D,ease:fase},S);
    tl.set(`#${id} ${sel}`,{rotation:0,svgOrigin:org||"0 0"},S+D); };
  osc(".legA",A); osc(".legB",-A);
  if(!o.semBraco){ osc(".armA",-A*.8); osc(".armB",A*.8); }
  osc(".head",2); osc(".capa",4,"0 -250");
  if(existe(`#${id} .bob`)){ tl.fromTo(`#${id} .bob`,{y:0},{y:-7,duration:D,ease:(p)=>Math.abs(fase(p)),},S); tl.set(`#${id} .bob`,{y:0},S+D); }
  piscar(id,S+1.1,D);
}
// parado(): respira, pisca e a capa balança de leve. Nunca mexe as pernas.
function parado(id,S,dur){ const n=Math.max(1,Math.round(dur/1.1));
  if(existe(`#${id} .bob`)) tl.fromTo(`#${id} .bob`,{y:0},{y:-3,duration:.55,yoyo:true,repeat:n*2-1,ease:"sine.inOut"},S);
  piscar(id,S+.9,dur);
  if(existe(`#${id} .capa`)) tl.fromTo(`#${id} .capa`,{rotation:-1.5,svgOrigin:"0 -250"},{rotation:2,svgOrigin:"0 -250",duration:.9,yoyo:true,repeat:n,ease:"sine.inOut"},S); }
// gesto(): levanta um braço (apontar/explicar) e balança de leve.
function gesto(id,lado,t,ang,seg){ const sel=`#${id} .${lado==="A"?"armA":"armB"}`; if(!existe(sel)) return;
  tl.to(sel,{rotation:ang,svgOrigin:"0 0",duration:.4,ease:"power2.out"},t);
  tl.to(sel,{rotation:ang-12,svgOrigin:"0 0",duration:.3,yoyo:true,repeat:1,ease:"sine.inOut"},t+.4); }

// =====================================================================
//  UTILITÁRIOS DE CENA
// =====================================================================
function el(html,cls,css){ const d=document.createElement("div"); d.className=cls; if(css) d.style.cssText=css; d.innerHTML=html; return d; }
function aparece(sel,t,dur){ tl.fromTo(sel,{opacity:0,y:14},{opacity:1,y:0,duration:dur||.45,ease:"power2.out"},t); }
function lento(sel,S,D,de,para){ tl.fromTo(sel,{x:de},{x:para,duration:D,ease:"none"},S); }
function camera(id,S,D,z0,z1,ox,oy){ tl.fromTo(`#${id}`,{scale:z0,transformOrigin:`${ox||640}px ${oy||400}px`},{scale:z1,duration:D,ease:"none"},S); }
function raiz(id){ return document.getElementById(id); }

