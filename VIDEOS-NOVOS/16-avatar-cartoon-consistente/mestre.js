// gera img/avatar-mestre.svg (pose idle) e img/avatar-expressoes.svg a partir do MESMO avatar.js
const fs=require('fs');const {AV,AV_EMO,AV_POSE}=require('./avatar.js');
function posed(id,emo,pose='idle'){let s=AV(id,{emo});const a=AV_POSE[pose];
 ['la','le','ra','re'].forEach((j,k)=>s=s.replace(`id="${id}_${j}"`,`id="${id}_${j}" transform="rotate(${a[k]})"`));return s;}
fs.writeFileSync('img/avatar-mestre.svg',`<svg xmlns="http://www.w3.org/2000/svg" width="600" height="900" viewBox="-300 -460 600 900"><rect x="-300" y="-460" width="600" height="900" fill="#e9f4f9"/>${posed('m','neutro')}</svg>`);
const em=Object.keys(AV_EMO);let g='';em.forEach((e,k)=>g+=`<g transform="translate(${150+(k%6)*300},${560+Math.floor(k/6)*560})">${posed('e'+k,e,['idle','up','aberto','wave'][k%4])}<text y="70" text-anchor="middle" font-family="Arial" font-size="40" font-weight="700">${e}</text></g>`);
fs.writeFileSync('img/avatar-expressoes.svg',`<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1220" viewBox="0 0 1800 1220"><rect width="1800" height="1220" fill="#e9f4f9"/>${g}</svg>`);
console.log('ok',em.length);

