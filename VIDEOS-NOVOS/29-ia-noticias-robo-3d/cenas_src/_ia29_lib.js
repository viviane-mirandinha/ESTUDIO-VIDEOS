if(!window.IA29){window.IA29=(function(){
 function rng(s){return function(){s|=0;s=s+0x6D2B79F5|0;let t=Math.imul(s^s>>>15,1|s);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
 function drive(tl,S,D,fn){ const o={_t:0}; Object.defineProperty(o,"t",{get(){return this._t},set(v){this._t=v;fn(v)}}); tl.fromTo(o,{t:0},{t:D,duration:D,ease:"none",immediateRender:false},S); }
 function cl(v){return Math.max(0,Math.min(1,v));}
 function eo(v){v=cl(v);return 1-Math.pow(1-v,3);}
 function wave(seed,n,w,h,cor){ const r=rng(seed); let s='<svg viewBox="0 0 '+w+' '+h+'" width="'+w+'" height="'+h+'"><g fill="'+cor+'">';
   for(let i=0;i<n;i++){ const env=Math.sin(Math.PI*(i+.5)/n); const bh=Math.max(4,h*(.15+.85*env*r())); s+='<rect x="'+(i*w/n+1).toFixed(1)+'" y="'+((h-bh)/2).toFixed(1)+'" width="'+(w/n-3).toFixed(1)+'" height="'+bh.toFixed(1)+'" rx="2"/>'; }
   return s+'</g></svg>'; }
 function noiseCanvas(seed,w,h,amt){ const c=document.createElement("canvas"); c.width=w; c.height=h; const x=c.getContext("2d"), d=x.createImageData(w,h), r=rng(seed);
   for(let i=0;i<d.data.length;i+=4){ const v=r()*255; d.data[i]=d.data[i+1]=d.data[i+2]=v; d.data[i+3]=amt; } x.putImageData(d,0,0); return c; }
 return {rng,drive,cl,eo,wave,noiseCanvas};
})();}
