/* AVATAR MESTRE (fonte única): todas as cenas e o img/avatar-mestre.svg saem desta função.
   Origem (0,0) = entre os pés. Altura ~410 un. em escala 1. Juntas: _ll/_rl (quadril), _lk/_rk (joelho),
   _la/_ra (ombro), _le/_re (cotovelo), _h (cabeça), _b (corpo/bob), _eo (olhos abertos), _pu (pupilas). */
const AVK='#141416', AVG='#8fe03f', AVG2='#6cbf2a', AVW='#ffffff';
const AV_PARTS={
 eo:'eye-open', eh:'eye-happy', ex:'eye-x', es:'eye-squint', ec:'eye-closed', eb:'eye-big', ef:'eye-half',
 mn:'m-neutral', ms:'m-smile', mf:'m-happy', mo:'m-o', mw:'m-wavy', mg:'m-shout', mt:'m-teeth',
 sw:'sweat', bw:'brow-worry'};
const AV_EMO={
 neutro:['eo','mn'], feliz:['eh','mf'], surpresa:['eb','mo'], medo:['eb','mw','sw','bw'], tonto:['ex','mw'],
 esforco:['es','mt','sw'], sono:['ec','mn'], cansado:['ef','mw','sw'], grita:['es','mg'], ofegante:['eo','mo','sw','bw'],
 tedio:['ef','mn'], come:['eh','ms']};
const AV_POSE={ // [la, le, ra, re]
 idle:[12,-6,-12,6], up:[165,10,-165,-10], aberto:[55,20,-55,-20], wave:[12,-6,-140,-30],
 pega:[12,-6,-80,60], boca:[12,-6,-121,211], peito:[12,-6,-35,-120], sentado:[35,-30,-35,30], cai:[120,20,-120,-20]};
function AV(id,o={}){
 const emo=AV_EMO[o.emo||'neutro'];
 const J=(x,y,jid,inner)=>`<g transform="translate(${x},${y})"><g id="${jid}">${inner}</g></g>`;
 const S=(d,w=6)=>`<path d="${d}" stroke="${AVW}" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round" fill="none"/>`;
 const shoe=`<ellipse cx="7" cy="68" rx="31" ry="15" fill="#f4f4f2"/><path d="M-22,62 Q7,52 36,64" stroke="#d6d6d0" stroke-width="3" fill="none"/><rect x="-24" y="74" width="62" height="8" rx="4" fill="#c9c9c3"/>`;
 const shin=`<rect x="-15" y="-6" width="30" height="70" rx="14" fill="${AVK}"/>`+shoe;
 const leg=s=>{const k=s<0?'l':'r';return J(s*22,-158,`${id}_${k}l`,`<rect x="-16" y="-8" width="32" height="90" rx="15" fill="${AVK}"/>`+J(0,76,`${id}_${k}k`,shin));};
 const glove=`<circle cx="0" cy="58" r="16" fill="${AVK}"/><ellipse cx="-11" cy="49" rx="7" ry="10" fill="${AVK}"/>`;
 const spoon=o.colher?`<g id="${id}_sp"><rect x="-5" y="52" width="10" height="66" rx="5" fill="#c3c7cd"/><ellipse cx="0" cy="128" rx="26" ry="18" fill="#dfe3e8" stroke="#aeb3ba" stroke-width="3"/>
  <g id="${id}_spc" opacity="0"><ellipse cx="-8" cy="124" rx="12" ry="8" fill="#fff"/><circle cx="-8" cy="124" r="4.5" fill="#ffc21a"/><rect x="2" y="114" width="16" height="14" rx="3" fill="#c98a3c"/><circle cx="12" cy="134" r="6" fill="#e0483b"/></g></g>`:'';
 const fore=x=>`<rect x="-12" y="-4" width="24" height="54" rx="11" fill="${AVG}"/><rect x="-12" y="38" width="24" height="10" rx="4" fill="${AVG2}"/>`+(x||'')+glove;
 const arm=(s,x)=>{const k=s<0?'l':'r';return J(s*50,-252,`${id}_${k}a`,`<rect x="-13" y="-10" width="26" height="70" rx="12" fill="${AVG}"/>`+J(0,60,`${id}_${k}e`,fore(x)));};
 const torso=`<rect x="-42" y="-150" width="84" height="40" rx="14" fill="${AVK}"/>
  <path d="M-50,-270 Q-60,-264 -60,-240 L-57,-150 Q-56,-134 -40,-134 L40,-134 Q56,-134 57,-150 L60,-240 Q60,-264 50,-270 Z" fill="${AVG}"/>
  <path d="M-60,-240 L-57,-150 Q-56,-134 -40,-134 L-34,-134 L-44,-246Z" fill="${AVG2}" opacity=".55"/>
  <rect x="-57" y="-152" width="114" height="18" rx="8" fill="${AVG2}"/>
  <path d="M-30,-204 L30,-204 L38,-162 L-38,-162Z" fill="none" stroke="${AVG2}" stroke-width="5" stroke-linejoin="round"/>
  <ellipse cx="0" cy="-266" rx="50" ry="17" fill="${AVG2}"/>
  <path d="M-13,-258 L-15,-218 M13,-258 L15,-218" stroke="#f2f2ee" stroke-width="5" stroke-linecap="round"/>`;
 const P={
  eo:`<g id="${id}_eo"><ellipse cx="-25" cy="-6" rx="13" ry="17" fill="${AVW}"/><ellipse cx="25" cy="-6" rx="13" ry="17" fill="${AVW}"/><g id="${id}_pu"><circle cx="-23" cy="-3" r="6.5" fill="${AVK}"/><circle cx="27" cy="-3" r="6.5" fill="${AVK}"/></g></g>`,
  eh:S('M-38,-2 Q-25,-20 -12,-2')+S('M12,-2 Q25,-20 38,-2'),
  ex:S('M-35,-16 L-15,4 M-15,-16 L-35,4')+S('M15,-16 L35,4 M35,-16 L15,4'),
  es:S('M-37,-16 L-15,-6 L-37,4')+S('M37,-16 L15,-6 L37,4'),
  ec:S('M-38,-4 Q-25,8 -12,-4')+S('M12,-4 Q25,8 38,-4'),
  eb:`<circle cx="-26" cy="-8" r="19" fill="${AVW}"/><circle cx="26" cy="-8" r="19" fill="${AVW}"/><circle cx="-26" cy="-6" r="6" fill="${AVK}"/><circle cx="26" cy="-6" r="6" fill="${AVK}"/>`,
  ef:`<path d="M-39,-6 A13,13 0 0 0 -11,-6 Z" fill="${AVW}"/><path d="M11,-6 A13,13 0 0 0 39,-6 Z" fill="${AVW}"/>`+S('M-41,-8 L-9,-8 M9,-8 L41,-8',5),
  mn:S('M-12,36 L12,36',5),
  ms:S('M-22,28 Q0,48 22,28'),
  mf:`<path d="M-26,26 Q0,64 26,26 Z" fill="${AVW}"/>`,
  mo:`<ellipse cx="0" cy="38" rx="11" ry="14" fill="${AVW}"/>`,
  mw:S('M-24,38 Q-16,29 -8,38 Q0,47 8,38 Q16,29 24,38',5),
  mg:`<ellipse cx="0" cy="40" rx="27" ry="24" fill="${AVW}"/><ellipse cx="0" cy="50" rx="14" ry="8" fill="#e05050"/>`,
  mt:`<rect x="-22" y="28" width="44" height="16" rx="5" fill="${AVW}"/><path d="M-22,36 L22,36" stroke="${AVK}" stroke-width="3"/>`,
  sw:`<path d="M58,-40 Q70,-18 64,-8 Q56,2 50,-8 Q46,-18 58,-40Z" fill="#bfe8ff"/>`,
  bw:S('M-40,-34 L-14,-42')+S('M40,-34 L14,-42')};
 const face=Object.keys(P).map(k=>`<g id="${id}_f_${k}" opacity="${emo.includes(k)?1:0}">${P[k]}</g>`).join('');
 const head=J(0,-336,`${id}_h`,`<circle r="74" fill="${AVK}"/><ellipse cx="-28" cy="-36" rx="26" ry="13" fill="#3a3a42" opacity=".6" transform="rotate(-32 -28 -36)"/>`+face);
 return `<g id="${id}" class="av"><g id="${id}_b">${leg(-1)}${leg(1)}${torso}${arm(-1)}${head}${arm(1,spoon)}</g></g>`;
}
if(typeof module!=='undefined') module.exports={AV,AV_EMO,AV_POSE};
