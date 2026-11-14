/* ELENCO FIXO (fonte única): LEO e ANA em ilustração flat (traço fino, pastel) + PALITO para metáforas.
   Origem (0,0) = entre os pés. Altura ~370 un. em escala 1. Juntas: _ll/_rl (quadril), _lk/_rk (joelho),
   _la/_ra (ombro), _le/_re (cotovelo), _h (cabeça/pescoço), _b (corpo), _eo (olhos), _ph (celular). */
const OL='#2e2a26';
const ELENCO={
 leo:{skin:'#f2c9a6',hair:'#4b3324',top:'#fbf8f1',sleeve:'#fbf8f1',pants:'#77805a',shoe:'#5a3a28',cabelo:'curto'},
 ana:{skin:'#eebf9c',hair:'#7b4a2b',top:'#f3e0c4',sleeve:'#c8693d',pants:'#46516a',shoe:'#3b2f2a',cabelo:'longo'}
};
const POSE={ // [la, le, ra, re]  (l = braço do lado esquerdo da tela)
 idle:[8,-4,-8,4], celular:[8,-4,-10,140], aceno:[8,-4,-150,-25], aberto:[40,-25,-40,25], alcanca:[8,-4,-84,-6],
 peito:[8,-4,16,138], cruz:[0,-100,0,100], aponta:[8,-4,-70,-10], bolso:[14,10,-14,-10], segura:[8,-4,-30,-50]};
const EMO={neutro:['bn','mn'],feliz:['bn','ms'],triste:['bw','mt'],serio:['bn','mr']};
function PES(id,who,o={}){
 const c=ELENCO[who];
 const J=(x,y,jid,inner)=>`<g transform="translate(${x},${y})"><g id="${jid}">${inner}</g></g>`;
 const st=`stroke="${OL}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"`;
 const shoe=`<path d="M-11,72 Q-13,90 6,90 L22,90 Q27,83 13,74 Z" fill="${c.shoe}" ${st}/>`;
 const shin=`<rect x="-10" y="-8" width="20" height="86" rx="9" fill="${c.pants}" ${st}/>`+shoe;
 const leg=(s,k)=>J(s*14,-172,`${id}_${k}l`,`<rect x="-11" y="-6" width="22" height="94" rx="10" fill="${c.pants}" ${st}/>`+J(0,84,`${id}_${k}k`,shin));
 const phone=`<g id="${id}_ph" opacity="${o.celular?1:0}"><rect x="-11" y="44" width="22" height="36" rx="4" fill="#2d3442" ${st}/><rect x="-7" y="49" width="14" height="24" rx="2" fill="#a9d4f5"/></g>`;
 const cuff=who==='leo'?`<rect x="-9" y="-6" width="18" height="12" rx="5" fill="${c.sleeve}" ${st}/>`:'';
 const fore=k=>`<rect x="-8" y="-4" width="16" height="62" rx="8" fill="${who==='ana'?c.sleeve:c.skin}" ${st}/>${cuff}<circle cx="0" cy="62" r="10" fill="${c.skin}" ${st}/>`+(k==='r'?phone:'');
 const arm=(s,k)=>J(s*34,-288,`${id}_${k}a`,`<rect x="-10" y="-8" width="20" height="80" rx="10" fill="${c.sleeve}" ${st}/>`+J(0,66,`${id}_${k}e`,fore(k)));
 let torso=`<rect x="-32" y="-180" width="64" height="30" rx="9" fill="${c.pants}" ${st}/>`;
 if(who==='leo') torso+=`<path d="M-36,-282 Q-36,-300 -18,-300 L18,-300 Q36,-300 36,-282 L32,-170 Q0,-164 -32,-170 Z" fill="${c.top}" ${st}/>
  <path d="M-13,-300 L0,-283 L13,-300" fill="none" ${st}/><path d="M0,-283 V-172" fill="none" stroke="${OL}" stroke-width="2"/>
  <circle cx="5" cy="-262" r="2" fill="${OL}"/><circle cx="5" cy="-236" r="2" fill="${OL}"/><circle cx="5" cy="-210" r="2" fill="${OL}"/>
  <rect x="-32" y="-178" width="64" height="9" fill="#5c4434"/>`;
 else torso+=`<path d="M-36,-282 Q-36,-300 -18,-300 L18,-300 Q36,-300 36,-282 L33,-166 Q0,-160 -33,-166 Z" fill="${c.sleeve}" ${st}/>
  <path d="M-13,-300 L13,-300 L12,-168 L-12,-168 Z" fill="${c.top}" ${st}/>`;
 const hairBack=c.cabelo==='longo'?`<path d="M-31,-30 Q-36,-68 0,-68 Q36,-68 31,-30 L36,24 Q0,34 -36,24 Z" fill="${c.hair}" ${st}/>`:'';
 const hairFront=c.cabelo==='longo'
  ?`<path d="M-26,-30 Q-26,-62 2,-62 Q28,-61 26,-30 Q14,-50 -4,-47 Q-18,-44 -26,-30 Z" fill="${c.hair}" ${st}/>`
  :`<path d="M-25,-36 Q-29,-68 2,-66 Q29,-64 25,-34 Q20,-46 6,-48 Q-12,-50 -25,-36 Z" fill="${c.hair}" ${st}/>`;
 const cheek=who==='ana'?`<circle cx="-13" cy="-20" r="5" fill="#e8907a" opacity=".45"/><circle cx="13" cy="-20" r="5" fill="#e8907a" opacity=".45"/>`:'';
 const face=`<g id="${id}_eo"><circle cx="-9" cy="-29" r="3" fill="${OL}"/><circle cx="9" cy="-29" r="3" fill="${OL}"/></g>
  <path id="${id}_f_bn" d="M-15,-38 Q-9,-41 -4,-38 M4,-38 Q9,-41 15,-38" fill="none" stroke="${OL}" stroke-width="2.5" stroke-linecap="round"/>
  <path id="${id}_f_bw" opacity="0" d="M-15,-36 Q-9,-38 -4,-42 M4,-42 Q9,-38 15,-36" fill="none" stroke="${OL}" stroke-width="2.5" stroke-linecap="round"/>
  <path d="M0,-27 Q4,-20 -1,-19" fill="none" stroke="${OL}" stroke-width="2" stroke-linecap="round"/>${cheek}
  <path id="${id}_f_mn" d="M-6,-12 Q0,-9 6,-12" fill="none" stroke="${OL}" stroke-width="2.5" stroke-linecap="round"/>
  <path id="${id}_f_ms" opacity="0" d="M-9,-14 Q0,-4 9,-14" fill="#fff" stroke="${OL}" stroke-width="2.5" stroke-linecap="round"/>
  <path id="${id}_f_mt" opacity="0" d="M-7,-8 Q0,-15 7,-8" fill="none" stroke="${OL}" stroke-width="2.5" stroke-linecap="round"/>
  <path id="${id}_f_mr" opacity="0" d="M-7,-11 L7,-11" fill="none" stroke="${OL}" stroke-width="2.5" stroke-linecap="round"/>`;
 const head=J(0,-300,`${id}_h`,`${hairBack}<rect x="-7" y="-8" width="14" height="14" fill="${c.skin}"/>
  <circle cx="-24" cy="-27" r="6" fill="${c.skin}" ${st}/><circle cx="24" cy="-27" r="6" fill="${c.skin}" ${st}/>
  <ellipse cx="0" cy="-28" rx="24" ry="28" fill="${c.skin}" ${st}/>${hairFront}${face}`);
 return `<g id="${id}"><g id="${id}_b">${leg(-1,'l')}${leg(1,'r')}${torso}${head}${arm(-1,'l')}${arm(1,'r')}</g></g>`;
}
/* boneco de palito (metáforas, igual à referência): mesmas juntas */
function PAL(id,o={}){
 const J=(x,y,jid,inner)=>`<g transform="translate(${x},${y})"><g id="${jid}">${inner}</g></g>`;
 const L=(y)=>`<path d="M0,0 L0,${y}" stroke="${OL}" stroke-width="7" stroke-linecap="round" fill="none"/>`;
 const leg=(s,k)=>J(s*8,-170,`${id}_${k}l`,L(86)+J(0,86,`${id}_${k}k`,L(80)+`<path d="M0,80 L${s>0?14:-14},82" stroke="${OL}" stroke-width="7" stroke-linecap="round"/>`));
 const arm=(s,k)=>J(s*4,-268,`${id}_${k}a`,L(66)+J(0,66,`${id}_${k}e`,L(56)));
 const saia=o.mulher?`<path d="M0,-214 L-30,-150 L30,-150 Z" fill="#fff" stroke="${OL}" stroke-width="5" stroke-linejoin="round"/>`:'';
 const cab=o.mulher?`<path d="M18,-318 Q44,-312 40,-280" stroke="${OL}" stroke-width="7" fill="none" stroke-linecap="round"/>`:'';
 return `<g id="${id}"><g id="${id}_b">${leg(-1,'l')}${leg(1,'r')}<path d="M0,-278 L0,-170" stroke="${OL}" stroke-width="7" stroke-linecap="round"/>${saia}
  ${J(0,-276,`${id}_h`,`${cab}<circle cx="0" cy="-28" r="27" fill="#fff" stroke="${OL}" stroke-width="5"/>
  <g id="${id}_eo"><circle cx="-8" cy="-30" r="3.2" fill="${OL}"/><circle cx="8" cy="-30" r="3.2" fill="${OL}"/></g>
  <path id="${id}_f_mn" d="M-7,-15 Q0,-12 7,-15" fill="none" stroke="${OL}" stroke-width="3" stroke-linecap="round"/>
  <path id="${id}_f_mt" opacity="0" d="M-8,-12 Q0,-19 8,-12" fill="none" stroke="${OL}" stroke-width="3" stroke-linecap="round"/>
  <path id="${id}_f_ms" opacity="0" d="M-8,-17 Q0,-8 8,-17" fill="none" stroke="${OL}" stroke-width="3" stroke-linecap="round"/>
  <path id="${id}_f_bn" d="M0,0" /><path id="${id}_f_bw" opacity="0" d="M-14,-40 L-4,-44 M4,-44 L14,-40" stroke="${OL}" stroke-width="3" stroke-linecap="round"/><path id="${id}_f_mr" opacity="0" d="M-7,-14 L7,-14" stroke="${OL}" stroke-width="3"/>`)}
  ${arm(-1,'l')}${arm(1,'r')}</g></g>`;
}
