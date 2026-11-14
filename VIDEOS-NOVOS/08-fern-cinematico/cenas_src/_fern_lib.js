if(!window.FERN){window.FERN=(function(){
 function rng(s){return function(){s|=0;s=s+0x6D2B79F5|0;let t=Math.imul(s^s>>>15,1|s);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
 const noise={};
 function grainTile(seed){ if(noise[seed]) return noise[seed]; const c=document.createElement("canvas");c.width=c.height=256;const x=c.getContext("2d");const d=x.createImageData(256,256);const r=rng(seed);
  for(let i=0;i<d.data.length;i+=4){const v=r()*255;d.data[i]=d.data[i+1]=d.data[i+2]=v;d.data[i+3]=255;} x.putImageData(d,0,0); return noise[seed]=c; }
 function mk(el,W,H){ const c=document.createElement("canvas");c.width=W;c.height=H;c.style.cssText="position:absolute;inset:0;width:100%;height:100%;pointer-events:none";el.appendChild(c);return c; }
 // nevoa + poeira volumetrica, deterministica em t
 function fog(c,t,seed,cor,dens){ const x=c.getContext("2d"),W=c.width,H=c.height; x.clearRect(0,0,W,H); const r=rng(seed); dens=dens||1;
  x.globalCompositeOperation="lighter";
  for(let i=0;i<14*dens;i++){ const bx=r()*W,by=H*(.35+r()*.7),rad=180+r()*260,sp=8+r()*14,ph=r()*6.28;
   const px=(bx+t*sp*(r()>.5?1:-1)+Math.sin(t*.2+ph)*40)%(W+400)-200, py=by+Math.sin(t*.15+ph)*20;
   const g=x.createRadialGradient(px,py,0,px,py,rad); g.addColorStop(0,cor.replace("A",(.05+r()*.05).toFixed(3))); g.addColorStop(1,cor.replace("A","0"));
   x.fillStyle=g; x.fillRect(px-rad,py-rad,rad*2,rad*2); }
  for(let i=0;i<60*dens;i++){ const bx=r()*W,by=r()*H,sz=.6+r()*1.8,vx=(r()-.5)*12,vy=-4-r()*10,ph=r()*6.28;
   const px=((bx+vx*t)%W+W)%W, py=((by+vy*t)%H+H)%H, a=.15+.35*(.5+.5*Math.sin(t*1.3+ph));
   x.fillStyle="rgba(210,225,240,"+a.toFixed(3)+")"; x.beginPath(); x.arc(px,py,sz,0,6.283); x.fill(); }
  x.globalCompositeOperation="source-over"; }
 function grain(c,t,amt){ const x=c.getContext("2d"),W=c.width,H=c.height; x.clearRect(0,0,W,H); const f=Math.floor(t*24); const tile=grainTile(7);
  x.globalAlpha=amt||.07; const ox=(f*97)%256, oy=(f*57)%256; for(let yy=-oy;yy<H;yy+=256)for(let xx=-ox;xx<W;xx+=256)x.drawImage(tile,xx,yy); x.globalAlpha=1; }
 // driver: objeto com setter -> GSAP chama draw a cada seek (nao depende de onUpdate)
 function drive(tl,S,D,fn){ const o={_t:0}; Object.defineProperty(o,"t",{get(){return this._t},set(v){this._t=v;fn(v)}}); tl.fromTo(o,{t:0},{t:D,duration:D,ease:"none",immediateRender:false},S); }
 return {rng,mk,fog,grain,drive};
})();}
