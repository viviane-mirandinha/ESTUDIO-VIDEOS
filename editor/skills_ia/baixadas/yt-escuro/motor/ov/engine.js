// Motor de overlays: ?i=<indice no PLAN>. window.seek(t) desenha o tempo local t (s). Determinístico.
const ST = document.getElementById('st');
const Q = new URLSearchParams(location.search);
const IDX = +(Q.get('i') || 0);
const IT = PLAN[IDX];
const FPS = 30;
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const seg = (t, a, b) => clamp((t - a) / (b - a));
const eo = (x) => 1 - Math.pow(1 - x, 3);
const eio = (x) => x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
const back = (x) => { const c = 1.9; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); };
const el = (tag, css, html, parent = ST) => { const e = document.createElement(tag); if (css) e.style.cssText = css; if (html != null) e.innerHTML = html; parent.appendChild(e); return e; };
const svgNS = 'http://www.w3.org/2000/svg';
const step = (t, fps) => Math.floor(t * fps) / fps; // movimento "em poses" (pixel / cel)
// envelope de entrada/saida padrao
const envIn = (t, d = .35) => seg(t, 0, d);
const envOut = (t, dur, d = .3) => 1 - seg(t, dur - d, dur);
const side = (p) => p.side || 'R';
const sx = (p, w, m = 70) => p.center ? (1920 - w) / 2 : side(p) === 'L' ? m : 1920 - w - m;
const typed = (s, k) => s.slice(0, Math.round(s.length * clamp(k)));

const T = {};

/* =================== GAME HYPE (gta6 farm) =================== */
const GH = {pink: '#FF2E93', vio: '#7B2CBF', org: '#FF8A3D', yel: '#FFD23F', navy: '#12142A'};
// titulo de impacto (gancho): caps espaçadas com brilho rosa; full = fundo navy de palco
T.gh_hook = (p, dur) => {
  const full = !!p.full;
  if (full) el('div', `left:0;top:0;width:1920px;height:1080px;background:radial-gradient(ellipse 70% 60% at 50% 45%,#2a1550 0%,${GH.navy} 60%,#07081a 100%)`).className = 'a';
  const band = el('div', `left:0;top:${full ? 330 : 640}px;width:1920px;height:${full ? 420 : 300}px;background:linear-gradient(90deg,rgba(18,20,42,.92),rgba(18,20,42,.75) 55%,rgba(18,20,42,0));`); band.className = 'a';
  const sm = el('div', `left:110px;top:${full ? 380 : 670}px;font-family:MXB;font-size:44px;letter-spacing:.42em;color:#fff;white-space:nowrap`, p.top || ''); sm.className = 'a';
  const big = el('div', `left:100px;top:${full ? 450 : 735}px;font-family:MB;font-style:italic;font-size:${p.size || 118}px;line-height:1;color:#fff;white-space:nowrap;text-shadow:0 0 24px ${GH.pink},0 0 60px ${GH.pink},4px 4px 0 ${GH.vio}`, p.text); big.className = 'a';
  const sub = el('div', `left:110px;top:${full ? 600 : 875}px;font-family:MXB;font-size:40px;letter-spacing:.3em;color:${GH.yel};white-space:nowrap`, p.sub || ''); sub.className = 'a';
  const flash = el('div', `left:0;top:0;width:1920px;height:1080px;background:#fff;mix-blend-mode:screen`); flash.className = 'a';
  return (t) => {
    const k = envIn(t, .45), o = envOut(t, dur, .3);
    band.style.transform = `translateX(${(1 - eo(k)) * -1920}px)`; band.style.opacity = o;
    const kb = seg(t, .12, .5);
    big.style.transform = `scale(${1.8 - .8 * back(kb)}) skewX(-6deg)`; big.style.transformOrigin = 'left center'; big.style.opacity = Math.min(kb * 3, 1) * o;
    sm.style.opacity = seg(t, .05, .3) * o; sm.style.letterSpacing = (.9 - .48 * eo(seg(t, 0, .6))) + 'em';
    sub.style.opacity = seg(t, .55, .8) * o; sub.style.transform = `translateY(${(1 - eo(seg(t, .55, .9))) * 30}px)`;
    flash.style.opacity = Math.max(0, .55 - t * 3) * (p.flash === false ? 0 : 1);
    if (full) ST.firstChild.style.opacity = o;
  };
};
// faixa de declaração (gh_title) — sem tela cheia
T.gh_title = (p, dur) => {
  const y = p.y || 120;
  const w = p.w || 900, x = sx(p, w, 60);
  const box = el('div', `left:${x}px;top:${y}px;width:${w}px;padding:26px 34px;background:linear-gradient(120deg,rgba(18,20,42,.94),rgba(123,44,191,.86));border-left:10px solid ${GH.pink};box-shadow:0 0 40px rgba(255,46,147,.45);box-sizing:border-box`); box.className = 'a';
  const sm = el('div', `font-family:MXB;font-size:26px;letter-spacing:.38em;color:${GH.yel};margin-bottom:10px`, p.top || '', box);
  const tx = el('div', `font-family:MB;font-style:italic;font-size:${p.size || 64}px;line-height:1.02;color:#fff;text-shadow:0 0 18px ${GH.pink}`, '', box);
  return (t) => {
    const k = eo(envIn(t, .3)), o = envOut(t, dur, .25);
    box.style.transform = `translateX(${(1 - k) * (side(p) === 'L' ? -1 : 1) * 700}px) skewX(-4deg)`; box.style.opacity = o;
    tx.textContent = typed(p.text, seg(t, .15, .15 + p.text.length * .03));
  };
};
// lenda/lista de módulos (gh_legend): cartões com ícone + título + linha
T.gh_legend = (p, dur) => {
  const w = 640, x = sx(p, w, 60), y0 = p.y || 150, gap = p.gap || 128;
  const cards = p.items.map((it, i) => {
    const c = el('div', `left:${x}px;top:${y0 + i * gap}px;width:${w}px;height:${gap - 18}px;border-radius:22px;background:linear-gradient(100deg,rgba(255,138,61,.96),rgba(255,46,147,.95) 55%,rgba(123,44,191,.95));box-shadow:0 14px 40px rgba(0,0,0,.45);overflow:hidden`); c.className = 'a';
    el('div', `position:absolute;left:18px;top:${(gap - 18 - 74) / 2}px;width:74px;height:74px;border-radius:50%;background:${GH.navy};color:${GH.yel};font-size:40px;display:flex;align-items:center;justify-content:center`, it.icon, c);
    el('div', `position:absolute;left:112px;top:${(gap - 18) / 2 - 38}px;font-family:MB;font-style:italic;font-size:36px;color:#fff;white-space:nowrap`, it.t, c);
    el('div', `position:absolute;left:112px;top:${(gap - 18) / 2 + 6}px;font-family:ON;font-size:24px;color:#fff;opacity:.92;white-space:nowrap`, it.s || '', c);
    return c;
  });
  return (t) => {
    const o = envOut(t, dur, .3);
    cards.forEach((c, i) => { const s0 = (p.stagger ? p.stagger[i] : i * .25); const k = back(seg(t, s0, s0 + .4)); c.style.transform = `translateX(${(1 - k) * (side(p) === 'L' ? -760 : 760)}px)`; c.style.opacity = Math.min(1, seg(t, s0, s0 + .15)) * o; });
  };
};
// post social (gh_post) em palco azul — tela cheia opcional
T.gh_post = (p, dur) => {
  const full = !!p.full;
  let bg = null;
  if (full) { bg = el('div', `left:0;top:0;width:1920px;height:1080px;background:radial-gradient(circle at 50% 40%,#3d8bff,#1243c9 70%)`); bg.className = 'a'; }
  const w = 760, x = full ? 580 : sx(p, w, 70), y = full ? 250 : (p.y || 200);
  const c = el('div', `left:${x}px;top:${y}px;width:${w}px;background:#fff;border-radius:28px;padding:34px 38px;box-sizing:border-box;box-shadow:0 30px 80px rgba(0,0,0,.4)`); c.className = 'a';
  el('div', `display:flex;align-items:center;gap:18px;margin-bottom:22px`, `<div style="width:76px;height:76px;border-radius:50%;background:linear-gradient(135deg,${GH.pink},${GH.org});color:#fff;font-family:MB;font-size:38px;display:flex;align-items:center;justify-content:center">${p.ini || 'Y'}</div><div><div style="font-family:ON8;font-size:30px;color:#111">${p.name || 'Yuri'}</div><div style="font-family:ON;font-size:24px;color:#7a7a7a">${p.handle || '@codigodarenda'}</div></div>`, c);
  const tx = el('div', `font-family:ON;font-size:40px;line-height:1.28;color:#111;min-height:100px`, '', c);
  const row = el('div', `margin-top:22px;font-family:ON;font-size:26px;color:#8a8a8a;display:flex;gap:42px`, `<span>♥ <b class="lk">0</b></span><span>💬 <b class="cm">0</b></span>`, c);
  return (t) => {
    const k = back(seg(t, 0, .45)), o = envOut(t, dur, .3);
    c.style.transform = `translateY(${(1 - k) * 140}px) scale(${.85 + .15 * k})`; c.style.opacity = Math.min(1, t * 5) * o;
    if (bg) bg.style.opacity = o;
    tx.textContent = typed(p.text, seg(t, .3, .3 + p.text.length * .028));
    row.querySelector('.lk').textContent = Math.round((p.likes || 12400) * eo(seg(t, .6, dur - .5))).toLocaleString('pt-BR');
    row.querySelector('.cm').textContent = Math.round((p.comments || 860) * eo(seg(t, .6, dur - .5))).toLocaleString('pt-BR');
  };
};
// checklist rosa
T.gh_check = (p, dur) => {
  const w = 700, x = sx(p, w, 70), y0 = p.y || 220;
  const box = el('div', `left:${x}px;top:${y0}px;width:${w}px;padding:30px 36px;border-radius:26px;background:rgba(18,20,42,.92);border:3px solid ${GH.pink};box-shadow:0 0 50px rgba(255,46,147,.35);box-sizing:border-box`); box.className = 'a';
  if (p.title) el('div', `font-family:MXB;font-size:28px;letter-spacing:.32em;color:${GH.yel};margin-bottom:18px`, p.title, box);
  const rows = p.items.map((s) => el('div', `display:flex;align-items:center;gap:22px;margin:14px 0;font-family:MB;font-style:italic;font-size:46px;color:#fff;white-space:nowrap`, `<span class="ck" style="width:58px;height:58px;border-radius:14px;background:${GH.pink};display:inline-flex;align-items:center;justify-content:center;font-size:40px;font-style:normal">✓</span><span>${s}</span>`, box));
  return (t) => {
    const k = eo(envIn(t, .3)), o = envOut(t, dur, .25);
    box.style.transform = `translateX(${(1 - k) * (side(p) === 'L' ? -800 : 800)}px)`; box.style.opacity = o;
    rows.forEach((r, i) => { const s0 = .35 + i * (p.gapT || .55); const kk = seg(t, s0, s0 + .25); r.style.opacity = kk; r.querySelector('.ck').style.transform = `scale(${back(kk)})`; });
  };
};

/* =================== PIXEL ART 8-BIT (mg-pixel) =================== */
const PXC = {bg: '#1a1033', ink: '#0d0a1f', g: '#3cff6e', y: '#ffd23f', r: '#ff4f6d', c: '#45d8ff', w: '#f4f0ff'};
const pxBox = (css) => `background:${PXC.bg};border:6px solid ${PXC.w};box-shadow:0 0 0 6px ${PXC.ink},12px 12px 0 6px rgba(0,0,0,.55);image-rendering:pixelated;${css || ''}`;
const crt = (parent) => { const c = el('div', `position:absolute;inset:0;pointer-events:none;background:repeating-linear-gradient(0deg,rgba(0,0,0,.28) 0 2px,transparent 2px 5px)`, '', parent); return c; };
// banner de fase: LEVEL + barra de XP
T.px_level = (p, dur) => {
  const w = 800, x = sx(p, w, 60), y = p.y || 70;
  const b = el('div', pxBox(`left:${x}px;top:${y}px;width:${w}px;padding:24px 28px;box-sizing:border-box`)); b.className = 'a px';
  el('div', `font-size:22px;color:${PXC.y};margin-bottom:16px`, p.top || 'LEVEL 01', b);
  const tx = el('div', `font-size:${p.text.length > 18 ? 28 : 34}px;line-height:1.35;color:${PXC.w};min-height:46px;white-space:nowrap`, '', b);
  const bar = el('div', `margin-top:20px;height:30px;border:4px solid ${PXC.w};position:relative;background:${PXC.ink}`, '', b);
  const fill = el('div', `position:absolute;left:0;top:0;bottom:0;background:repeating-linear-gradient(90deg,${PXC.g} 0 22px,#29c752 22px 26px)`, '', bar);
  const lab = el('div', `margin-top:10px;font-size:18px;color:${PXC.c}`, '', b);
  crt(b);
  return (t) => {
    const ts = step(t, 12), o = envOut(t, dur, .25) > .5 ? 1 : 0;
    const k = seg(ts, 0, .25); b.style.transform = `translateY(${Math.round((1 - k) * -8) * 30}px)`; b.style.opacity = (k > 0 ? 1 : 0) * o;
    tx.textContent = typed(p.text, seg(ts, .25, .25 + p.text.length * .045));
    const f = step(seg(ts, .5, Math.min(dur - .4, 2.2)), 8) * (p.xp || 100);
    fill.style.width = f + '%'; lab.textContent = `XP ${Math.round(f)}/100`;
  };
};
// mascote pixel do Yuri (mascote-yuri) + balão pixel
T.px_yuri = (p, dur) => {
  const sc = p.scale || 3.4, sz = 123 * sc;
  const x = side(p) === 'L' ? (p.x ?? 40) : 1920 - sz - (p.x ?? 40), y = 1080 - sz + (p.dy || 0);
  const img = el('img', `left:${x}px;top:${y}px;width:${sz}px;height:${sz}px;image-rendering:pixelated;filter:drop-shadow(8px 8px 0 rgba(0,0,0,.5))`); img.className = 'a'; img.src = 'img/' + (p.pose || 'pulgar') + '.png';
  const bw = p.bw || 560;
  const bx = side(p) === 'L' ? x + sz - 60 : x - bw + 60;
  const bub = el('div', pxBox(`left:${bx}px;top:${y - 40}px;width:${bw}px;padding:22px 24px;box-sizing:border-box;background:${PXC.w};color:${PXC.ink};font-size:30px;line-height:1.4`)); bub.className = 'a px';
  return (t) => {
    const ts = step(t, 12), o = envOut(t, dur, .25) > .5 ? 1 : 0;
    const k = seg(ts, 0, .33); const hop = Math.abs(Math.sin(ts * 6)) * 10 * (ts > .4 ? 1 : 0);
    img.style.transform = `translateY(${Math.round((1 - k) * sz) - Math.round(hop / 4) * 4}px)`; img.style.opacity = o;
    const kb = seg(ts, .35, .5); bub.style.opacity = (kb > 0 ? 1 : 0) * o; bub.style.transform = `scale(${kb < 1 ? .6 : 1})`;
    bub.textContent = typed(p.text, seg(ts, .4, .4 + p.text.length * .04));
  };
};
// moedas pixel caindo + contador
T.px_coins = (p, dur) => {
  const full = !!p.full;
  if (full) { const b = el('div', `left:0;top:0;width:1920px;height:1080px;background:${PXC.bg}`); b.className = 'a'; crt(b); }
  const coinSVG = (c) => `<svg width="64" height="64" viewBox="0 0 16 16" shape-rendering="crispEdges"><rect x="5" y="1" width="6" height="1" fill="#000"/><rect x="3" y="2" width="10" height="12" fill="#000"/><rect x="1" y="5" width="14" height="6" fill="#000"/><rect x="5" y="2" width="6" height="12" fill="${c}"/><rect x="4" y="3" width="8" height="10" fill="${c}"/><rect x="2" y="5" width="12" height="6" fill="${c}"/><rect x="7" y="4" width="2" height="8" fill="#b88a00"/><rect x="5" y="4" width="1" height="2" fill="#fff"/></svg>`;
  const N = 26, coins = [];
  const x0 = full ? 0 : (side(p) === 'L' ? 0 : 1180), w = full ? 1920 : 740;
  for (let i = 0; i < N; i++) { const c = el('div', `left:${x0 + ((i * 137) % w)}px;top:-80px`, coinSVG(PXC.y)); c.className = 'a'; coins.push({c, d: (i * .09) % 1.1, sp: 700 + (i * 53) % 400}); }
  const lab = el('div', pxBox(`left:${full ? 560 : x0 + 40}px;top:${full ? 420 : 360}px;width:${full ? 800 : 660}px;padding:28px;box-sizing:border-box;text-align:center;color:${PXC.y};font-size:${full ? 56 : 40}px;line-height:1.3`)); lab.className = 'a px';
  return (t) => {
    const ts = step(t, 12), o = envOut(t, dur, .25) > .5 ? 1 : 0;
    coins.forEach((q) => { const tt = ts - q.d; q.c.style.transform = `translateY(${Math.max(0, tt) * q.sp}px) scaleX(${[1, .6, .2, .6][Math.floor(ts * 8) % 4]})`; q.c.style.opacity = o * (tt > 0 ? 1 : 0); });
    lab.style.opacity = (ts > .2 ? 1 : 0) * o; lab.textContent = p.text; lab.style.transform = `scale(${ts < .45 ? 1.15 : 1})`;
    if (full) ST.firstChild.style.opacity = o;
  };
};
// cadeado pixel + contagem 7 dias
T.px_lock = (p, dur) => {
  const full = !!p.full;
  if (full) { const b = el('div', `left:0;top:0;width:1920px;height:1080px;background:${PXC.bg}`); b.className = 'a'; crt(b); }
  const cx = full ? 960 : (side(p) === 'L' ? 360 : 1560);
  const lock = el('div', `left:${cx - 120}px;top:${full ? 170 : 150}px;width:240px;height:300px`, `<svg width="240" height="300" viewBox="0 0 16 20" shape-rendering="crispEdges"><g class="sh"><rect x="4" y="1" width="8" height="2" fill="${PXC.w}"/><rect x="3" y="2" width="2" height="7" fill="${PXC.w}"/><rect x="11" y="2" width="2" height="7" fill="${PXC.w}"/></g><rect x="1" y="8" width="14" height="11" fill="${PXC.y}"/><rect x="1" y="8" width="14" height="1" fill="#fff6"/><rect x="7" y="11" width="2" height="5" fill="${PXC.ink}"/></svg>`); lock.className = 'a';
  const lab = el('div', pxBox(`left:${cx - 330}px;top:${full ? 520 : 480}px;width:660px;padding:24px;box-sizing:border-box;text-align:center;color:${PXC.w};font-size:32px;line-height:1.4`)); lab.className = 'a px';
  const num = el('div', `left:${cx - 330}px;top:${full ? 690 : 640}px;width:660px;text-align:center;font-size:84px;color:${PXC.r};text-shadow:6px 6px 0 #000`); num.className = 'a px';
  return (t) => {
    const ts = step(t, 12), o = envOut(t, dur, .25) > .5 ? 1 : 0;
    lock.style.opacity = o * (ts > 0 ? 1 : 0); lock.style.transform = `translateY(${ts < .3 ? -40 : 0}px) rotate(${ts > .5 && ts < 1.2 ? [-6, 6][Math.floor(ts * 10) % 2] : 0}deg)`;
    lab.style.opacity = (ts > .3 ? 1 : 0) * o; lab.textContent = typed(p.text, seg(ts, .3, .3 + p.text.length * .035));
    num.style.opacity = (ts > .8 ? 1 : 0) * o; num.textContent = p.num || '7 DIAS';
    if (full) ST.firstChild.style.opacity = o;
  };
};
// caixa de missão pixel com estrelas
T.px_quest = (p, dur) => {
  const w = p.w || 820, x = sx(p, w, 60), y = p.y || 110;
  const b = el('div', pxBox(`left:${x}px;top:${y}px;width:${w}px;padding:26px 30px;box-sizing:border-box`)); b.className = 'a px';
  el('div', `font-size:22px;color:${PXC.r};margin-bottom:14px`, '► ' + (p.top || 'MISSÃO'), b);
  const lines = p.items.map((s) => el('div', `font-size:28px;line-height:1.5;color:${PXC.w};margin:8px 0;white-space:nowrap`, '', b));
  crt(b);
  return (t) => {
    const ts = step(t, 12), o = envOut(t, dur, .25) > .5 ? 1 : 0;
    b.style.opacity = (ts > 0 ? 1 : 0) * o; b.style.transform = `scale(${ts < .17 ? .7 : 1})`;
    lines.forEach((l, i) => { const s0 = .25 + i * .6; l.textContent = (seg(ts, s0 + .5, s0 + .55) >= 1 ? '★ ' : '☆ ') + typed(p.items[i], seg(ts, s0, s0 + .45)); l.style.color = seg(ts, s0 + .5, s0 + .55) >= 1 ? PXC.g : PXC.w; });
  };
};
// gancho pixel em tela cheia: PRESS START
T.px_title = (p, dur) => {
  const bg = el('div', `left:0;top:0;width:1920px;height:1080px;background:${PXC.bg}`); bg.className = 'a';
  const stars = []; for (let i = 0; i < 60; i++) { const s = el('div', `left:${(i * 331) % 1920}px;top:${(i * 197) % 1080}px;width:8px;height:8px;background:${[PXC.w, PXC.c, PXC.y][i % 3]}`, '', bg); s.className = 'a'; stars.push(s); }
  const t1 = el('div', `left:0;width:1920px;top:300px;text-align:center;font-size:${p.size || 92}px;line-height:1.25;color:${PXC.y};text-shadow:8px 8px 0 ${PXC.r},16px 16px 0 #000`); t1.className = 'a px';
  const t2 = el('div', `left:0;width:1920px;top:680px;text-align:center;font-size:36px;color:${PXC.w}`); t2.className = 'a px';
  crt(bg);
  return (t) => {
    const ts = step(t, 12), o = envOut(t, dur, .2) > .5 ? 1 : 0;
    bg.style.opacity = o; t1.style.opacity = o; t2.style.opacity = o;
    stars.forEach((s, i) => { s.style.transform = `translateX(${-((ts * (120 + (i % 5) * 80)) % 1920)}px)`; });
    t1.innerHTML = typed(p.text, seg(ts, 0, .7)).replace(/\|/g, '<br>');
    t1.style.transform = `translateY(${ts < .1 ? 40 : 0}px)`;
    t2.textContent = Math.floor(ts * 2.5) % 2 ? '' : (p.sub || '► PRESS START');
  };
};

/* =================== QUADRO A QUADRO (mg-cel-boil) =================== */
const CB = {paper: '#f6efdc', ink: '#2b2118', red: '#e8432e', amber: '#f2a516', blue: '#2f6fd6'};
const paperBg = `background-color:${CB.paper};background-image:radial-gradient(rgba(120,90,50,.10) 1px,transparent 1.4px),radial-gradient(rgba(120,90,50,.07) 1px,transparent 1.2px);background-size:9px 9px,13px 13px;background-position:0 0,4px 6px`;
const svgBox = (w, h, css, parent = ST) => { const s = document.createElementNS(svgNS, 'svg'); s.setAttribute('width', w); s.setAttribute('height', h); s.setAttribute('viewBox', `0 0 ${w} ${h}`); s.style.cssText = 'position:absolute;overflow:visible;' + (css || ''); parent.appendChild(s); return s; };
const pathEl = (svg, d, stroke, sw, fill = 'none') => { const p = document.createElementNS(svgNS, 'path'); p.setAttribute('d', d); p.setAttribute('stroke', stroke); p.setAttribute('stroke-width', sw); p.setAttribute('fill', fill); p.setAttribute('stroke-linecap', 'round'); p.setAttribute('stroke-linejoin', 'round'); svg.appendChild(p); const L = p.getTotalLength ? p.getTotalLength() : 1000; p.style.strokeDasharray = L; p.style.strokeDashoffset = L; p._L = L; return p; };
const draw = (p, k) => { p.style.strokeDashoffset = p._L * (1 - clamp(k)); };
// bilhete de papel com letra de caneta, seta desenhada
T.cb_note = (p, dur) => {
  const w = p.w || 600, x = sx(p, w, 80), y = p.y || 150;
  const card = el('div', `left:${x}px;top:${y}px;width:${w}px;padding:34px 38px 40px;box-sizing:border-box;${paperBg};border-radius:6px;box-shadow:6px 10px 0 rgba(43,33,24,.35);transform-origin:50% 0`); card.className = 'a boil';
  const tape = el('div', `left:${x + w / 2 - 70}px;top:${y - 22}px;width:140px;height:44px;background:rgba(242,165,22,.75);transform:rotate(-4deg)`); tape.className = 'a';
  if (p.top) el('div', `font-family:CAV;font-size:38px;color:${CB.red};margin-bottom:4px`, p.top, card);
  const tx = el('div', `font-family:CAV;font-size:${p.size || 64}px;line-height:1.05;color:${CB.ink}`, '', card);
  const ul = svgBox(w, 40, `left:${x + 30}px;top:${y + 0}px`); const u = pathEl(ul, `M0 20 C ${w * .3} 6 ${w * .6} 34 ${w - 80} 14`, CB.red, 9); ul.classList.add('boil');
  let ar = null;
  if (p.arrow !== false) { const as = svgBox(260, 160, `left:${side(p) === 'L' ? x + w - 20 : x - 230}px;top:${y + 120}px`); as.classList.add('boil'); const flip = side(p) === 'L' ? '' : 'scale(-1,1) translate(-260,0)'; const g = document.createElementNS(svgNS, 'g'); g.setAttribute('transform', flip); as.appendChild(g); ar = [pathEl(g, 'M10 30 C 90 10 170 40 220 110', CB.ink, 9), pathEl(g, 'M180 112 L224 114 L214 72', CB.ink, 9)]; ar.forEach(a => g.appendChild(a)); }
  return (t) => {
    const tb = step(t, 12), o = envOut(t, dur, .25);
    const k = back(seg(tb, 0, .35)); card.style.transform = `rotate(${(p.rot ?? -3)}deg) scale(${k})`; card.style.opacity = o; tape.style.opacity = seg(tb, .2, .3) * o;
    tx.textContent = typed(p.text, seg(tb, .25, .25 + p.text.length * .035));
    ul.style.top = (y + card.offsetHeight - 34) + 'px'; draw(u, seg(tb, .6 + p.text.length * .035, 1 + p.text.length * .035)); ul.style.opacity = o;
    if (ar) { draw(ar[0], seg(tb, .4, .8)); draw(ar[1], seg(tb, .8, 1)); ar[0].parentNode.parentNode.style.opacity = o; }
  };
};
// rabiscos em volta do Yuri (estrelas, brilho, exclamação, dinheiro, lâmpada)
T.cb_doodle = (p, dur) => {
  const cx = p.cx || 960, cy = p.cy || 360;
  const s = svgBox(1920, 1080, 'left:0;top:0'); s.classList.add('boil');
  const ps = [];
  const star = (x, y, r) => { let d = ''; for (let i = 0; i < 10; i++) { const a = -Math.PI / 2 + i * Math.PI / 5, rr = i % 2 ? r * .45 : r; d += (i ? 'L' : 'M') + (x + Math.cos(a) * rr).toFixed(1) + ' ' + (y + Math.sin(a) * rr).toFixed(1) + ' '; } return d + 'Z'; };
  const col = p.color || CB.amber;
  const k = p.kind || 'stars';
  if (k === 'stars' || k === 'money') {
    [[-330, -120, 46], [310, -170, 38], [-250, 120, 30], [350, 80, 42]].forEach(([dx, dy, r], i) => ps.push(pathEl(s, k === 'money' ? `M${cx + dx - 18} ${cy + dy - 30} C ${cx + dx + 30} ${cy + dy - 40} ${cx + dx + 30} ${cy + dy} ${cx + dx} ${cy + dy} C ${cx + dx - 30} ${cy + dy} ${cx + dx - 30} ${cy + dy + 40} ${cx + dx + 18} ${cy + dy + 30} M${cx + dx} ${cy + dy - 50} L${cx + dx} ${cy + dy + 50}` : star(cx + dx, cy + dy, r), k === 'money' ? '#2f9e44' : col, 8)));
  }
  if (k === 'bang') { [[-300, -60], [300, -60]].forEach(([dx, dy], j) => { for (let i = 0; i < 3; i++) { const a = (j ? -1 : 1) * (.4 - i * .4) + (j ? Math.PI : 0); ps.push(pathEl(s, `M${cx + dx + Math.cos(a) * 30} ${cy + dy + Math.sin(a) * 30} L${cx + dx + Math.cos(a) * 110} ${cy + dy + Math.sin(a) * 110}`, CB.red, 10)); } }); }
  if (k === 'bulb') { ps.push(pathEl(s, `M${cx - 40} ${cy - 250} C ${cx - 110} ${cy - 320} ${cx - 60} ${cy - 430} ${cx} ${cy - 430} C ${cx + 60} ${cy - 430} ${cx + 110} ${cy - 320} ${cx + 40} ${cy - 250} Z M${cx - 34} ${cy - 225} L${cx + 34} ${cy - 225} M${cx - 26} ${cy - 205} L${cx + 26} ${cy - 205}`, CB.amber, 9)); for (let i = 0; i < 5; i++) { const a = -Math.PI + i * Math.PI / 4; ps.push(pathEl(s, `M${cx + Math.cos(a) * 140} ${cy - 340 + Math.sin(a) * 140} L${cx + Math.cos(a) * 190} ${cy - 340 + Math.sin(a) * 190}`, CB.amber, 9)); } }
  if (k === 'circle') { ps.push(pathEl(s, `M${cx - 20} ${cy - 330} C ${cx + 260} ${cy - 340} ${cx + 300} ${cy + 260} ${cx} ${cy + 250} C ${cx - 300} ${cy + 240} ${cx - 280} ${cy - 320} ${cx + 30} ${cy - 300}`, CB.red, 10)); }
  if (k === 'question') { [[-320, -80], [320, -120]].forEach(([dx, dy]) => ps.push(pathEl(s, `M${cx + dx - 30} ${cy + dy - 40} C ${cx + dx - 30} ${cy + dy - 90} ${cx + dx + 40} ${cy + dy - 90} ${cx + dx + 40} ${cy + dy - 40} C ${cx + dx + 40} ${cy + dy - 10} ${cx + dx} ${cy + dy - 5} ${cx + dx} ${cy + dy + 25} M${cx + dx} ${cy + dy + 55} L${cx + dx} ${cy + dy + 58}`, CB.blue, 11))); }
  let lab = null;
  if (p.text) { lab = el('div', `left:${cx - 500}px;width:1000px;top:${p.ty || cy - 400}px;text-align:center;font-family:CAV;font-size:${p.size || 92}px;color:${p.tcolor || CB.paper};-webkit-text-stroke:3px ${CB.ink};paint-order:stroke fill;text-shadow:5px 6px 0 ${CB.ink}`, p.text); lab.className = 'a boil'; }
  return (t) => {
    const tb = step(t, 12), o = envOut(t, dur, .25);
    ps.forEach((q, i) => draw(q, seg(tb, .05 + i * .1, .35 + i * .1)));
    s.style.opacity = o;
    if (lab) { lab.style.opacity = o * (tb > .15 ? 1 : 0); lab.style.transform = `rotate(${[-3, 2, -1][Math.floor(tb * 6) % 3]}deg) scale(${tb < .3 ? 1.25 : 1})`; }
  };
};
// fantasminha BOO (mascote-apresentador) com placa/balão
function booPath(t) {
  let d = 'M-150 30 C -150 -100 -80 -170 0 -170 C 80 -170 150 -100 150 30 L 150 148';
  for (let i = 0; i < 6; i++) { const x0 = 150 - i * 50, ph = t * 7 + i * 1.1; d += ` Q ${x0 - 25} ${(178 + Math.sin(ph) * 10).toFixed(1)} ${x0 - 50} ${(148 + Math.sin(ph + 1.6) * 6).toFixed(1)}`; }
  return d + ' Z';
}
T.boo = (p, dur) => {
  const sc = p.scale || .95, L = side(p) === 'L';
  const cx = p.cx || (L ? 270 : 1650), cy = p.cy || 640;
  const s = svgBox(420, 460, `left:${cx - 210}px;top:${cy - 230}px`);
  s.innerHTML = `<defs><linearGradient id="gw" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".5" stop-color="#E9EBF0"/><stop offset="1" stop-color="#ACB2BD"/></linearGradient><radialGradient id="sh" cx=".3" cy=".2" r=".38"><stop offset="0" stop-color="#fff" stop-opacity=".9"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient><filter id="ds"><feDropShadow dx="0" dy="14" stdDeviation="14" flood-opacity=".45"/></filter></defs>
  <g id="bw" transform="translate(210,230) scale(${sc})" filter="url(#ds)"><path id="bb" fill="url(#gw)"/><path id="bs" fill="url(#sh)"/>
  <ellipse id="e1" cx="-50" cy="-34" rx="22" ry="31" fill="#0A0B0F"/><ellipse id="e2" cx="50" cy="-34" rx="22" ry="31" fill="#0A0B0F"/>
  <circle cx="-43" cy="-46" r="7" fill="#fff"/><circle cx="57" cy="-46" r="7" fill="#fff"/>
  <path id="mo" fill="#0A0B0F" stroke="#0A0B0F" stroke-width="7" stroke-linejoin="round"/>
  <ellipse cx="-96" cy="20" rx="22" ry="11" fill="${p.cheek || '#ff6b8b'}" opacity=".45"/><ellipse cx="96" cy="20" rx="22" ry="11" fill="${p.cheek || '#ff6b8b'}" opacity=".45"/></g>`;
  const bb = s.querySelector('#bb'), bs = s.querySelector('#bs'), bw = s.querySelector('#bw'), e1 = s.querySelector('#e1'), e2 = s.querySelector('#e2'), mo = s.querySelector('#mo');
  const bwid = p.bw || 520;
  const bub = el('div', `left:${L ? cx + 150 : cx - 150 - bwid}px;top:${cy - 330}px;width:${bwid}px;padding:26px 30px;box-sizing:border-box;background:#fff;border-radius:30px;font-family:ON8;font-size:${p.size || 40}px;line-height:1.18;color:#14151b;box-shadow:0 18px 50px rgba(0,0,0,.35)`); bub.className = 'a';
  const tail = el('div', `left:${L ? cx + 170 : cx - 210}px;top:${cy - 120}px;width:0;height:0;border-left:22px solid transparent;border-right:22px solid transparent;border-top:44px solid #fff;transform:rotate(${L ? 30 : -30}deg)`); tail.className = 'a';
  const face = p.face || 'feliz';
  return (t, frame) => {
    const o = envOut(t, dur, .3), k = back(seg(t, 0, .5));
    const fl = Math.sin(t * 2.6) * 12;
    bw.setAttribute('transform', `translate(210,${230 + fl + (1 - k) * 420}) scale(${sc * (0.6 + .4 * k)}) rotate(${Math.sin(t * 1.7) * 4})`);
    s.style.opacity = o;
    const d = booPath(t); bb.setAttribute('d', d); bs.setAttribute('d', d);
    const blink = (t % 2.7) > 2.55 ? .1 : 1; const es = face === 'surpreso' ? 1.2 : 1;
    e1.setAttribute('ry', 31 * blink * es); e2.setAttribute('ry', 31 * blink * es);
    const talk = (t > .5 && t < dur - .4) ? (Math.sin(t * 15) * .5 + .5) * (p.talk ? 1 : 0) : 0;
    if (face === 'surpreso') mo.setAttribute('d', `M-14 28 Q 0 ${10} 14 28 Q 0 ${58} -14 28 Z`);
    else mo.setAttribute('d', `M-26 26 Q 0 ${44 + talk * 18} 26 26 Q 0 ${30 + talk * 4} -26 26 Z`);
    const kb = back(seg(t, .35, .65)); bub.style.transform = `scale(${kb})`; bub.style.transformOrigin = L ? '0 100%' : '100% 100%'; bub.style.opacity = Math.min(1, seg(t, .35, .45)) * o; tail.style.opacity = bub.style.opacity;
    bub.innerHTML = typed(p.text, seg(t, .45, .45 + p.text.length * .03)).replace(/\*(.+?)\*/g, `<span style="color:${p.hl || '#ff5a1f'}">$1</span>`);
  };
};

/* =================== PAPER TRAIL (gta_doc) =================== */
const DOC = {ink: '#0C0E12', ink2: '#2A2F38', ivory: '#F2EEE6', paper: '#F4EFE4', amber: '#FFB547', teal: '#33D1BE', crim: '#E0314B'};
// cartão de data / capítulo (cursor piscando, data digitando, régua âmbar, título itálico)
T.doc_date = (p, dur) => {
  const full = !!p.full;
  const w = full ? 1920 : 760, x = full ? 0 : sx(p, w, 0), h = full ? 1080 : 1080;
  const bg = el('div', `left:${x}px;top:0;width:${w}px;height:${h}px;background:${full ? '#07080b' : 'linear-gradient(' + (side(p) === 'L' ? '90deg' : '270deg') + ',rgba(12,14,18,.96) 55%,rgba(12,14,18,0))'}`); bg.className = 'a';
  const lx = full ? 260 : (side(p) === 'L' ? 90 : 1920 - 680);
  const d = el('div', `left:${lx}px;top:${full ? 380 : 360}px;font-family:MAN;font-size:${full ? 150 : 120}px;color:${DOC.ivory};letter-spacing:-.02em;white-space:nowrap`); d.className = 'a';
  const rule = el('div', `left:${lx + 6}px;top:${full ? 570 : 520}px;height:6px;background:${DOC.amber}`); rule.className = 'a';
  const ti = el('div', `left:${lx + 6}px;top:${full ? 600 : 545}px;width:${full ? 1400 : 600}px;font-family:NEWS;font-size:${full ? 62 : 48}px;line-height:1.15;color:${DOC.ivory}`); ti.className = 'a';
  return (t) => {
    const o = envOut(t, dur, .25);
    bg.style.opacity = o * eo(seg(t, 0, .25)); if (!full) bg.style.transform = `translateX(${(1 - eo(seg(t, 0, .3))) * (side(p) === 'L' ? -300 : 300)}px)`;
    const k = seg(t, .2, .2 + p.date.length * .07);
    d.textContent = typed(p.date, k) + ((Math.floor(t * 3) % 2 || k < 1) ? '▍' : ' '); d.style.opacity = o;
    rule.style.width = (eo(seg(t, .3 + p.date.length * .07, .7 + p.date.length * .07)) * (full ? 700 : 480)) + 'px'; rule.style.opacity = o;
    ti.textContent = p.title; ti.style.opacity = seg(t, .6 + p.date.length * .07, .9 + p.date.length * .07) * o;
  };
};
// número recorde: rótulo + número contando (teal), fonte
T.doc_number = (p, dur) => {
  const w = p.w || 720, x = sx(p, w, 70), y = p.y || 170;
  const c = el('div', `left:${x}px;top:${y}px;width:${w}px;padding:34px 40px;box-sizing:border-box;background:linear-gradient(160deg,rgba(42,47,56,.95),rgba(12,14,18,.95));border-radius:20px;border:1px solid rgba(242,238,230,.18);box-shadow:0 30px 70px rgba(0,0,0,.5)`); c.className = 'a';
  el('div', `font-family:ON;font-size:26px;letter-spacing:.2em;color:${DOC.amber};text-transform:uppercase;margin-bottom:10px`, p.label, c);
  const rows = (p.rows || [{from: p.from || 0, to: p.to, pre: p.pre || '', suf: p.suf || '', note: p.note || ''}]).map((r) => {
    const rr = el('div', `margin:6px 0`, '', c);
    const lenT = (r.text || (r.pre + Math.round(r.to).toLocaleString('pt-BR') + r.suf)).length; const n = el('div', `font-family:MAN;font-size:${Math.min(r.size || 104, Math.floor((w - 80) * 1.75 / lenT))}px;line-height:1.05;color:${r.color || DOC.teal};white-space:nowrap`, '', rr);
    const nt = el('div', `font-family:NEWS;font-size:32px;color:${DOC.ivory};opacity:.85`, r.note || '', rr);
    return {r, n, rr};
  });
  if (p.src) el('div', `margin-top:14px;font-family:NEWS;font-size:24px;color:${DOC.ivory};opacity:.6`, '— ' + p.src, c);
  const fmt = (v, r) => r.pre + Math.round(v).toLocaleString('pt-BR') + r.suf;
  return (t) => {
    const o = envOut(t, dur, .25), k = eo(seg(t, 0, .35));
    c.style.transform = `translateY(${(1 - k) * 60}px)`; c.style.opacity = Math.min(1, t * 4) * o;
    rows.forEach(({r, n, rr}, i) => { const s0 = .25 + i * (p.gapT || .9); rr.style.opacity = seg(t, s0, s0 + .15); n.textContent = r.text || fmt(r.from + (r.to - r.from) * eo(seg(t, s0, s0 + .8)), r); });
  };
};
// citação em papel com caneta marca-texto âmbar
T.doc_quote = (p, dur) => {
  const w = p.w || 780, x = sx(p, w, 70), y = p.y || 160;
  const c = el('div', `left:${x}px;top:${y}px;width:${w}px;padding:40px 44px;box-sizing:border-box;background:${DOC.paper};box-shadow:0 30px 80px rgba(0,0,0,.55);transform-origin:50% 50%`); c.className = 'a';
  el('div', `font-family:ON8;font-size:22px;letter-spacing:.24em;color:#8b7d66;margin-bottom:18px`, p.kicker || 'ANOTAÇÃO DA AULA', c);
  const q = el('div', `font-family:NEWS;font-size:${p.size || 50}px;line-height:1.25;color:#1b1813`, '', c);
  const parts = p.text.split(/(\[.+?\])/).map((s) => s.startsWith('[') ? `<span class="hl" style="background:linear-gradient(90deg,${DOC.amber} 0,${DOC.amber} var(--k),transparent var(--k));padding:0 4px">${s.slice(1, -1)}</span>` : s).join('');
  q.innerHTML = parts;
  el('div', `margin-top:20px;font-family:NEWS;font-size:28px;color:#6b604f`, '— ' + (p.src || 'Yuri, nesta aula'), c);
  const hls = [...q.querySelectorAll('.hl')];
  return (t) => {
    const o = envOut(t, dur, .25), k = eo(seg(t, 0, .4));
    c.style.transform = `translateY(${(1 - k) * 80}px) rotate(${(p.rot ?? 1.5) * k}deg)`; c.style.opacity = Math.min(1, t * 4) * o;
    hls.forEach((h, i) => h.style.setProperty('--k', (eo(seg(t, .55 + i * .5, 1.05 + i * .5)) * 100) + '%'));
  };
};
// carimbo de veredito (vermelho)
T.doc_stamp = (p, dur) => {
  const L = side(p) === "L", cx = p.cx || (p.center ? 960 : L ? 480 : 1440), cy = p.cy || 300;
  const s = el('div', `left:${cx}px;top:${cy - 110}px;margin-left:-${Math.min(880, (p.size || 88) * .78 * p.text.length + 90) / 2}px;width:${Math.min(880, (p.size || 88) * .78 * p.text.length + 90)}px;height:220px;display:flex;align-items:center;justify-content:center;border:12px solid ${DOC.crim};border-radius:18px;color:${DOC.crim};font-family:MAN;font-size:${p.size || 88}px;letter-spacing:.02em;text-transform:uppercase;white-space:nowrap;box-sizing:border-box;background:rgba(244,239,228,.0)`, p.text); s.className = 'a';
  s.style.filter = 'url(#rough)';
  const sub = p.sub ? el('div', `left:${cx - 360}px;width:720px;top:${cy + 125}px;text-align:center;font-family:NEWS;font-size:36px;color:#fff;text-shadow:0 2px 10px #000`, p.sub) : null; if (sub) sub.className = 'a';
  return (t) => {
    const o = envOut(t, dur, .25), k = seg(t, .05, .22);
    s.style.transform = `rotate(${p.rot ?? -8}deg) scale(${2.4 - 1.4 * eio(k)})`; s.style.opacity = Math.min(1, k * 3) * o * .95;
    if (sub) sub.style.opacity = seg(t, .4, .6) * o;
  };
};
// barras (views) crescendo
T.doc_bars = (p, dur) => {
  const w = p.w || 760, x = sx(p, w, 70), y = p.y || 140;
  const c = el('div', `left:${x}px;top:${y}px;width:${w}px;padding:34px 40px;box-sizing:border-box;background:linear-gradient(160deg,rgba(42,47,56,.95),rgba(12,14,18,.96));border-radius:20px;box-shadow:0 30px 70px rgba(0,0,0,.5)`); c.className = 'a';
  el('div', `font-family:ON;font-size:26px;letter-spacing:.2em;color:${DOC.amber};margin-bottom:22px;text-transform:uppercase`, p.label, c);
  const mx = Math.max(...p.items.map((i) => i.v));
  const rows = p.items.map((it) => {
    const r = el('div', `margin:16px 0`, '', c);
    el('div', `font-family:ON;font-size:28px;color:${DOC.ivory};margin-bottom:8px`, it.t, r);
    const bar = el('div', `height:46px;background:${it.c || DOC.teal};border-radius:6px;display:flex;align-items:center;justify-content:flex-end;padding-right:14px;box-sizing:border-box;font-family:MAN;font-size:30px;color:${DOC.ink};white-space:nowrap;min-width:0`, '', r);
    return {it, bar};
  });
  return (t) => {
    const o = envOut(t, dur, .25); c.style.opacity = Math.min(1, t * 4) * o; c.style.transform = `translateY(${(1 - eo(seg(t, 0, .35))) * 60}px)`;
    rows.forEach(({it, bar}, i) => { const s0 = .3 + i * (p.gapT || .6); const k = eo(seg(t, s0, s0 + .7)); bar.style.width = Math.max(6, (it.v / mx) * (w - 80) * k) + 'px'; bar.textContent = k > .5 ? it.lab : ''; });
  };
};

/* =================== SUNSET COUNTDOWN (gta_countdown) =================== */
const CD = {night: '#0f1633', o1: '#ff8a3d', o2: '#ff4f7b', cream: '#fff6ec'};
// entrada numerada: varredura diagonal azul-noite, pílula NÚMERO, título digitando, sub em itálico, número gigante em degradê
T.cd_entry = (p, dur) => {
  const full = !!p.full, L = side(p) === 'L';
  const w = full ? 1920 : 980, x = full ? 0 : (L ? 0 : 1920 - w);
  const wipe = el('div', `left:${x - 200}px;top:0;width:${w + 400}px;height:1080px;background:linear-gradient(${L ? '100deg' : '260deg'},rgba(15,22,51,.97) 60%,rgba(15,22,51,0));clip-path:polygon(0 0,100% 0,85% 100%,0 100%)`); wipe.className = 'a';
  const bx = full ? 200 : (L ? 90 : 1920 - w + 200);
  const pill = el('div', `left:${bx}px;top:${full ? 300 : 300}px;padding:12px 30px;border-radius:40px;background:linear-gradient(90deg,${CD.o1},${CD.o2});font-family:FIG;font-size:30px;letter-spacing:.12em;color:#fff`, p.pill || ('NÚMERO ' + p.n)); pill.className = 'a';
  const ti = el('div', `left:${bx}px;top:${full ? 380 : 380}px;width:${full ? 1100 : 640}px;font-family:FIG;font-size:${p.size || 76}px;line-height:1.02;color:${CD.cream};text-transform:lowercase`); ti.className = 'a';
  const sub = el('div', `left:${bx}px;top:${full ? 600 : 590}px;width:${full ? 1100 : 640}px;font-family:FRA;font-size:40px;line-height:1.2;color:${CD.cream};opacity:.85`, p.sub || ''); sub.className = 'a';
  const big = el('div', `left:${full ? 1300 : (L ? 520 : 1920 - 420)}px;top:${full ? 220 : 640}px;font-family:UNB;font-size:${full ? 420 : 260}px;line-height:1;background:linear-gradient(180deg,${CD.o1},${CD.o2});-webkit-background-clip:text;color:transparent;opacity:.95`); big.className = 'a';
  const dash = el('div', `left:${bx}px;top:${full ? 720 : 700}px;display:flex;gap:10px`); dash.className = 'a';
  const tot = p.of || 5; const ds = []; for (let i = 0; i < tot; i++) ds.push(el('div', `width:44px;height:8px;border-radius:4px;background:${i < p.n ? CD.o1 : 'rgba(255,246,236,.25)'}`, '', dash));
  return (t) => {
    const o = envOut(t, dur, .3), k = eio(seg(t, 0, .4));
    wipe.style.transform = `translateX(${(1 - k) * (L ? -1 : 1) * (w + 400)}px)`; wipe.style.opacity = o;
    pill.style.opacity = seg(t, .3, .45) * o; pill.style.transform = `translateY(${(1 - eo(seg(t, .3, .55))) * 20}px)`;
    ti.textContent = typed(p.title, seg(t, .4, .4 + p.title.length * .03)); ti.style.opacity = o;
    sub.style.opacity = seg(t, .9, 1.2) * .85 * o;
    const kb = seg(t, .35, .9); big.style.opacity = Math.min(1, kb * 2) * o; big.style.transform = `translateX(${(1 - eo(kb)) * (L ? -200 : 200)}px) scale(${1.4 - .4 * eo(kb)})`;
    big.textContent = String(Math.max(1, Math.round(p.n * eo(seg(t, .35, 1))))).padStart(2, '0');
    dash.style.opacity = seg(t, 1, 1.2) * o;
  };
};

/* =================== REVEAL RADAR (gta_reveal) =================== */
const RV = {ink: '#0A0C11', flare: '#FF5A1F', surf: '#19D3C5', ok: '#2ED47A', rep: '#3D8BFF', rum: '#FFB547'};
T.rv_tag = (p, dur) => {
  const L = side(p) === 'L', x = p.center ? 600 : L ? 70 : 1920 - 70 - 720, y = p.y || 90;
  const dial = svgBox(240, 240, `left:${x}px;top:${y}px`);
  const ticks = []; for (let i = 0; i < 32; i++) { const a = -Math.PI / 2 + i * Math.PI * 2 / 32; const l = document.createElementNS(svgNS, 'line'); l.setAttribute('x1', 120 + Math.cos(a) * 92); l.setAttribute('y1', 120 + Math.sin(a) * 92); l.setAttribute('x2', 120 + Math.cos(a) * 116); l.setAttribute('y2', 120 + Math.sin(a) * 116); l.setAttribute('stroke-width', 9); l.setAttribute('stroke-linecap', 'round'); dial.appendChild(l); ticks.push(l); }
  const cir = document.createElementNS(svgNS, 'circle'); cir.setAttribute('cx', 120); cir.setAttribute('cy', 120); cir.setAttribute('r', 80); cir.setAttribute('fill', RV.ink); dial.appendChild(cir);
  const num = el('div', `left:${x}px;top:${y + 70}px;width:240px;text-align:center;font-family:UNB;font-size:84px;color:#fff`, p.n || '01'); num.className = 'a';
  const card = el('div', `left:${x + 260}px;top:${y + 30}px;width:460px;padding:22px 26px;box-sizing:border-box;background:#fff;border-radius:18px;box-shadow:0 20px 50px rgba(0,0,0,.45)`); card.className = 'a';
  const gc = {ok: RV.ok, rep: RV.rep, rum: RV.rum}[p.grade || 'ok'];
  el('div', `display:inline-block;padding:8px 18px;border-radius:30px;background:${gc};font-family:ON8;font-size:24px;letter-spacing:.14em;color:#0A0C11`, (p.grade === 'rum' ? '⚠ ' : p.grade === 'rep' ? 'ⓘ ' : '✔ ') + (p.word || 'CONFIRMADO'), card);
  const tx = el('div', `margin-top:14px;font-family:ON8;font-size:${p.size || 40}px;line-height:1.15;color:#0A0C11`, '', card);
  const cols = ['#ff3b3b', '#ff7a1f', '#ffd23f', '#2ed47a'];
  return (t) => {
    const o = envOut(t, dur, .25);
    const n = Math.floor(32 * eo(seg(t, .05, 1.1)));
    ticks.forEach((l, i) => { l.setAttribute('stroke', i < n ? cols[Math.min(3, Math.floor(i / 8))] : 'rgba(255,255,255,.18)'); });
    dial.style.opacity = o; num.style.opacity = o * seg(t, 0, .2); dial.style.transform = `scale(${back(seg(t, 0, .35))})`;
    card.style.opacity = o * seg(t, .3, .45); card.style.transform = `translateX(${(1 - eo(seg(t, .3, .6))) * (L ? -60 : 60)}px)`;
    tx.textContent = typed(p.text, seg(t, .45, .45 + p.text.length * .03));
  };
};

/* EXTRA_LOADED */
/* =================== KINETIC NOIR (preto + lima, tipografia cinética, sem câmera 3D) =================== */
const KN = {bg: '#070807', lime: '#C6FF3A', w: '#F2F4EE', g: '#6b7065'};
T.kn_type = (p, dur) => {
  const bg = el('div', `left:0;top:0;width:1920px;height:1080px;background:radial-gradient(ellipse 70% 60% at 50% 45%,#141713 0%,${KN.bg} 70%)`); bg.className = 'a';
  const glow = el('div', `left:0;top:0;width:1920px;height:1080px;background:radial-gradient(ellipse 60% 25% at 50% 0%,rgba(198,255,58,.14),transparent 70%)`); glow.className = 'a';
  const lab = el('div', `left:120px;top:90px;font-family:JB;font-size:24px;letter-spacing:.2em;color:${KN.lime}`, (p.top || 'CÓDIGO · RENDA DIGITAL').toUpperCase()); lab.className = 'a';
  const grp = el('div', `left:0;top:0;width:1920px;height:1080px`); grp.className = 'a';
  const box = el('div', `position:absolute;left:160px;right:160px;top:${p.y || 330}px;text-align:${p.align || 'left'};font-family:ITX;font-size:${p.size || 118}px;line-height:1.02;color:${KN.w};letter-spacing:-.02em`, '', grp);
  const ws = p.text.split(' ').map((w) => { const hl = w.startsWith('*'); return el('span', `display:inline-block;margin-right:.24em;${hl ? `color:${KN.lime};font-family:ITXI;` : ''}`, w.replace(/\*/g, ''), box); });
  const tl = el('div', `left:160px;top:${p.ty || 880}px;width:1600px;height:2px;background:${KN.g}`); tl.className = 'a';
  const KX = [0.1, 0.32, 0.55, 0.8];
  const kfs = KX.map((x) => el('div', `position:absolute;left:${x * 1600 - 9}px;top:-9px;width:18px;height:18px;background:${KN.lime};transform:rotate(45deg)`, '', tl));
  const ph = el('div', `position:absolute;left:0;top:-28px;width:3px;height:58px;background:${KN.w}`, '', tl);
  const tc = el('div', `position:absolute;left:0;top:-58px;font-family:JB;font-size:20px;color:${KN.w}`, '', tl);
  return (t) => {
    const o = envOut(t, dur, .25);
    [bg, glow, lab, tl].forEach((e) => { e.style.opacity = Math.min(1, t / .15) * o; });
    const per = Math.min(.22, (dur - .9) / ws.length);
    ws.forEach((s, i) => { const k = seg(t, .15 + i * per, .15 + i * per + .35); const sp = back(k); s.style.opacity = k; s.style.filter = `blur(${(1 - k) * 18}px)`; s.style.transform = `translateY(${(1 - sp) * 60}px) scale(${.8 + .2 * sp})`; });
    grp.style.transform = `scale(${1.04 - .04 * eo(seg(t, 0, dur))}) rotate(${Math.sin(t * 1.3) * .012}rad)`; grp.style.opacity = o;
    const pr = seg(t, 0, dur); ph.style.left = (pr * 1600) + 'px'; tc.style.left = (pr * 1600 + 10) + 'px'; tc.textContent = '00:' + String(Math.floor(t * 30)).padStart(2, '0') + 'f';
    kfs.forEach((d, i) => { d.style.boxShadow = pr > KX[i] ? `0 0 18px ${KN.lime}` : 'none'; });
  };
};
T.kn_code = (p, dur) => {
  const w = 760, x = sx(p, w, 70), y = p.y || 160;
  const c = el('div', `left:${x}px;top:${y}px;width:${w}px;background:#0d0f0c;border:1px solid rgba(198,255,58,.3);border-radius:18px;box-shadow:0 30px 70px rgba(0,0,0,.6),0 0 40px rgba(198,255,58,.12);overflow:hidden`); c.className = 'a';
  el('div', `height:46px;background:#151814;display:flex;align-items:center;gap:10px;padding-left:18px`, '<i style="width:14px;height:14px;border-radius:50%;background:#ff5f57;display:inline-block"></i><i style="width:14px;height:14px;border-radius:50%;background:#febc2e;display:inline-block"></i><i style="width:14px;height:14px;border-radius:50%;background:#28c840;display:inline-block"></i><span style="margin-left:14px;font-family:JB;font-size:18px;color:#7d8476">' + (p.file || 'renda.js') + '</span>', c);
  const code = el('pre', `margin:0;padding:24px 28px;font-family:JB;font-size:30px;line-height:1.45;color:${KN.w};white-space:pre-wrap;min-height:${p.lines.length * 44}px`, '', c);
  const full = p.lines.join('\n');
  return (t) => {
    const o = envOut(t, dur, .25), k = back(seg(t, 0, .35));
    c.style.transform = `translateY(${(1 - k) * 60}px) scale(${.9 + .1 * k})`; c.style.opacity = Math.min(1, t * 5) * o;
    const s = typed(full, seg(t, .3, Math.min(dur - .4, .3 + full.length * .035)));
    code.innerHTML = s.split('\n').map((ln) => ln.startsWith('//') ? `<span style="color:#6b7065">${ln}</span>` : ln.replace(/("[^"]*"?)/g, `<span style="color:${KN.lime}">$1</span>`)).join('\n') + ((Math.floor(t * 3) % 2) ? '▍' : '');
  };
};
/* =================== HUD CYBERPUNK (mg-hud) =================== */
const HUD = {c: '#3FF3FF', o: '#FF8A1F', bg: 'rgba(3,12,20,.80)'};
T.hud_lock = (p, dur) => {
  const cx = p.cx || 960, cy = p.cy || 400, R = p.r || 230;
  const s = svgBox(1920, 1080, 'left:0;top:0');
  s.innerHTML = `<g id="br" stroke="${HUD.c}" stroke-width="7" fill="none"></g><circle id="ring" cx="${cx}" cy="${cy}" r="${R}" stroke="${HUD.c}" stroke-width="3" fill="none" stroke-dasharray="18 14" opacity=".8"/><circle id="ring2" cx="${cx}" cy="${cy}" r="${R + 40}" stroke="${HUD.o}" stroke-width="2" fill="none" stroke-dasharray="4 22"/><line x1="${cx - R - 90}" y1="${cy}" x2="${cx - R + 30}" y2="${cy}" stroke="${HUD.c}" stroke-width="3"/><line x1="${cx + R - 30}" y1="${cy}" x2="${cx + R + 90}" y2="${cy}" stroke="${HUD.c}" stroke-width="3"/>`;
  const br = s.querySelector('#br'), ring = s.querySelector('#ring'), ring2 = s.querySelector('#ring2');
  let lx = cx + R + 60; if (lx + 520 > 1920) lx = cx - R - 580;
  const tag = el('div', `left:${lx}px;top:${cy - R}px;padding:14px 20px;background:${HUD.bg};border-left:5px solid ${HUD.o};font-family:ORB;font-size:30px;color:${HUD.o};letter-spacing:.08em;white-space:nowrap`, ''); tag.className = 'a';
  const data = el('div', `left:${lx}px;top:${cy - R + 80}px;padding:10px 16px;background:${HUD.bg};font-family:RAJ;font-size:32px;line-height:1.3;color:${HUD.c};white-space:nowrap;text-shadow:0 0 10px ${HUD.c}`, ''); data.className = 'a';
  return (t) => {
    const o = envOut(t, dur, .2), k = eio(seg(t, 0, .6));
    const r = R + (1 - k) * 260, L = 70;
    br.innerHTML = [[-1, -1], [1, -1], [-1, 1], [1, 1]].map(([a, b]) => `<path d="M${cx + a * r} ${cy + b * r - b * L} L${cx + a * r} ${cy + b * r} L${cx + a * r - a * L} ${cy + b * r}"/>`).join('');
    ring.setAttribute('transform', `rotate(${t * 60} ${cx} ${cy})`); ring2.setAttribute('transform', `rotate(${-t * 35} ${cx} ${cy})`);
    s.style.opacity = o * (Math.floor(t * 20) % 7 === 0 && t < .6 ? .4 : 1);
    tag.textContent = t > .6 ? (p.title || 'ALVO TRAVADO') : 'BUSCANDO' + '.'.repeat(1 + Math.floor(t * 6) % 3); tag.style.opacity = o * seg(t, .2, .3);
    data.innerHTML = (p.lines || []).map((l, i) => typed('> ' + l, seg(t, .7 + i * .35, 1 + i * .35))).join('<br>'); data.style.opacity = o * seg(t, .65, .75);
  };
};
T.hud_radar = (p, dur) => {
  const w = 620, x = sx(p, w, 60), y = p.y || 140;
  const c = el('div', `left:${x}px;top:${y}px;width:${w}px;padding:24px 28px;box-sizing:border-box;background:${HUD.bg};border:2px solid rgba(63,243,255,.5);clip-path:polygon(0 0,92% 0,100% 8%,100% 100%,8% 100%,0 92%);box-shadow:inset 0 0 40px rgba(63,243,255,.15)`); c.className = 'a';
  el('div', `font-family:ORB;font-size:30px;letter-spacing:.1em;color:${HUD.c};margin-bottom:12px`, p.title || 'RADAR', c);
  const s = svgBox(300, 300, 'position:relative;display:block;margin:0 auto', c);
  s.innerHTML = `<circle cx="150" cy="150" r="140" fill="none" stroke="${HUD.c}" stroke-opacity=".5"/><circle cx="150" cy="150" r="95" fill="none" stroke="${HUD.c}" stroke-opacity=".35"/><circle cx="150" cy="150" r="50" fill="none" stroke="${HUD.c}" stroke-opacity=".25"/><line x1="10" y1="150" x2="290" y2="150" stroke="${HUD.c}" stroke-opacity=".3"/><line x1="150" y1="10" x2="150" y2="290" stroke="${HUD.c}" stroke-opacity=".3"/><path id="sw" d="M150 150 L150 10 A140 140 0 0 1 249 51 Z" fill="${HUD.c}" fill-opacity=".25"/>` + (p.items || []).map((_, i) => `<circle class="bp" cx="${150 + Math.cos(i * 2.1 + .5) * (50 + i * 25)}" cy="${150 + Math.sin(i * 2.1 + .5) * (50 + i * 25)}" r="9" fill="${HUD.o}"/>`).join('');
  const lst = el('div', `margin-top:14px;font-family:RAJ;font-size:32px;line-height:1.35;color:#e8fbff`, '', c);
  const sw = s.querySelector('#sw'), bps = [...s.querySelectorAll('.bp')];
  return (t) => {
    const o = envOut(t, dur, .2), k = eo(seg(t, 0, .3));
    c.style.opacity = o * k; c.style.transform = `translateX(${(1 - k) * (side(p) === 'L' ? -80 : 80)}px)`;
    sw.setAttribute('transform', `rotate(${t * 140} 150 150)`);
    bps.forEach((b, i) => b.setAttribute('opacity', seg(t, .3 + i * .35, .45 + i * .35)));
    lst.innerHTML = (p.items || []).map((it, i) => `<span style="opacity:${seg(t, .3 + i * .35, .45 + i * .35)}"><b style="color:${HUD.o}">◆</b> ${it}</span>`).join('<br>');
  };
};
/* =================== HAND DRAWING (mão real escrevendo na lousa/papel) =================== */
T.hd_write = (p, dur) => {
  const th = p.theme || 'papel';
  const bgImg = {papel: 'fundo_papel.jpg', verde: 'fundo_lousa_verde.jpg', preta: 'fundo_lousa_preta.jpg'}[th];
  const ink = th === 'papel' ? '#1d2230' : '#f4f1e8', acc = th === 'papel' ? '#e8432e' : '#ffd23f';
  const bg = el('div', `left:0;top:0;width:1920px;height:1080px;background:url(img/${bgImg}) center/cover`); bg.className = 'a';
  const lines = p.lines, fs = p.size || 96, lh = fs * 1.25, y0 = p.y || (520 - lines.length * lh / 2);
  const cv = document.createElement('canvas').getContext('2d');
  const L = lines.map((s, i) => {
    const hl = s.startsWith('*'); const txt = s.replace(/\*/g, '');
    const d = el('div', `left:0;width:1920px;top:${y0 + i * lh}px;text-align:center;font-family:PM;font-size:${fs}px;line-height:${lh}px;color:${hl ? acc : ink};white-space:nowrap`, txt); d.className = 'a';
    return {d, txt};
  });
  const uy = y0 + lines.length * lh + 6;
  const ul = svgBox(1920, 1080, 'left:0;top:0'); const u = pathEl(ul, `M660 ${uy} C 900 ${uy - 16} 1100 ${uy + 12} 1260 ${uy - 6}`, acc, 10);
  const SC = .32, tip = th === 'papel' ? [10, 1710] : [11, 1767];
  const hand = el('img', `left:0;top:0;width:${(th === 'papel' ? 1907 : 1858) * SC}px;filter:drop-shadow(10px 18px 14px rgba(0,0,0,.35))`); hand.className = 'a'; hand.src = 'img/' + (th === 'papel' ? 'mao_marcador.webp' : 'mao_giz.webp');
  return (t) => {
    cv.font = `${fs}px PM`;
    const o = envOut(t, dur, .25); bg.style.opacity = Math.min(1, t / .15) * o;
    const avail = Math.max(.6, dur - 1.2), per = avail / lines.length; let hx = 1500, hy = 950;
    L.forEach(({d, txt}, i) => {
      const k = seg(t, .2 + i * per, .2 + (i + .9) * per); d.style.opacity = o;
      const wpx = cv.measureText(txt).width, left = 960 - wpx / 2;
      d.style.clipPath = `inset(0 ${Math.max(0, 1920 - (left + wpx * k))}px 0 0)`;
      if (k > 0 && k < 1) { hx = left + wpx * k; hy = y0 + i * lh + lh * .6 + Math.sin(t * 40) * 6; }
    });
    const ku = seg(t, .2 + avail, .2 + avail + .45); draw(u, ku); ul.style.opacity = o;
    if (ku > 0 && ku < 1) { hx = 660 + 600 * ku; hy = uy; }
    if (ku >= 1) { hx = 1500 + (t - (.65 + avail)) * 900; hy = 1000; }
    hand.style.transform = `translate(${hx - tip[0] * SC}px,${hy - tip[1] * SC}px)`; hand.style.opacity = o;
  };
};
/* =================== MÁQUINA DE REELS (estilos do Igor) =================== */
const MQ = {
  'clean-branco': {card: '#fff', ink: '#111827', acc: '#0D99FF', chip: '#E0F2FE', chipInk: '#0369A1', r: 30, sh: '0 22px 50px rgba(17,24,39,.18)', bd: 'none', serif: false},
  'editorial-zine': {card: '#FBF7EF', ink: '#141210', acc: '#E0314B', chip: '#141210', chipInk: '#F3EBDD', r: 6, sh: '10px 10px 0 #141210', bd: '3px solid #141210', serif: true},
  'lime-split': {card: '#121512', ink: '#F2F5EC', acc: '#CDF23A', chip: 'rgba(205,242,58,.14)', chipInk: '#CDF23A', r: 22, sh: '0 26px 60px rgba(0,0,0,.6)', bd: '1px solid rgba(205,242,58,.2)', serif: false},
  'papel-split': {card: '#fff', ink: '#201D1C', acc: '#1D4ED8', chip: '#EEF4FF', chipInk: '#1D4ED8', r: 34, sh: '0 16px 42px rgba(70,60,50,.18)', bd: 'none', serif: true},
  'selecao-azul': {card: '#121214', ink: '#fff', acc: '#4D87FD', chip: 'rgba(77,135,253,.16)', chipInk: '#9DBBFF', r: 30, sh: '0 30px 70px rgba(0,0,0,.55)', bd: '1px solid rgba(255,255,255,.08)', serif: false},
  'simples': {card: '#fff', ink: '#111', acc: '#0D99FF', chip: '#E0F2FE', chipInk: '#0369A1', r: 0, sh: 'none', bd: 'none', serif: false},
};
T.mq_card = (p, dur) => {
  const st = p.style || 'clean-branco', S = MQ[st];
  const split = st === 'lime-split' || st === 'papel-split', full = st === 'simples' || p.full;
  let panel = null;
  if (split) { panel = el('div', `left:0;top:0;width:${p.pw || 680}px;height:1080px;background:${st === 'lime-split' ? '#0A0C0B' : '#F4F3F1'};border-right:${st === 'lime-split' ? '5px solid #CDF23A' : '2px solid #E8E6E3'}`); panel.className = 'a'; }
  if (full) { panel = el('div', `left:0;top:0;width:1920px;height:1080px;background:${S.card}`); panel.className = 'a'; }
  const w = split ? (p.pw || 680) - 100 : (full ? 1500 : (p.w || 760));
  const x = split ? 50 : full ? 210 : sx(p, w, 70), y = p.y || (split ? 240 : full ? 300 : 170);
  const plain = full || split;
  const c = el('div', `left:${x}px;top:${y}px;width:${w}px;padding:${plain ? 0 : 38}px ${plain ? 0 : 40}px;box-sizing:border-box;background:${plain ? 'transparent' : S.card};border-radius:${S.r}px;box-shadow:${plain ? 'none' : S.sh};border:${plain ? 'none' : S.bd};color:${S.ink}`); c.className = 'a';
  const chip = el('div', `display:inline-block;padding:10px 22px;border-radius:40px;background:${S.chip};color:${S.chipInk};font-family:ON8;font-size:${full ? 34 : 24}px;letter-spacing:.06em;margin-bottom:22px`, p.chip || '', c);
  const fs = p.size || (full ? 120 : split ? 72 : 62);
  const tt = el('div', `font-family:${S.serif ? 'ISI' : 'ITX'};font-size:${S.serif ? fs * 1.12 : fs}px;line-height:1.04;letter-spacing:${S.serif ? '0' : '-.02em'}`, '', c);
  const spans = p.title.split(' ').map((wd) => { const hl = wd.startsWith('*'); const sp = el('span', `display:inline-block;position:relative;margin-right:.22em;${hl ? `color:${S.acc}` : ''}`, wd.replace(/\*/g, ''), tt); sp._hl = hl; return sp; });
  const sel = spans.find((s) => s._hl);
  let box = null;
  if (sel && st !== 'editorial-zine' && st !== 'papel-split') { const bc = st === 'lime-split' ? '#CDF23A' : '#0D99FF'; box = el('div', `position:absolute;left:-10px;top:-4px;right:-10px;bottom:-4px;border:3px solid ${bc};color:${bc}`, '<i style="position:absolute;left:-9px;top:-9px;width:12px;height:12px;background:#fff;border:3px solid currentColor"></i><i style="position:absolute;right:-9px;bottom:-9px;width:12px;height:12px;background:#fff;border:3px solid currentColor"></i>', sel); }
  if (sel && (st === 'editorial-zine' || st === 'papel-split')) { box = el('div', `position:absolute;left:-6px;right:-6px;bottom:6px;height:20px;background:${S.acc};opacity:.3;z-index:-1`, '', sel); }
  const items = (p.items || []).map((it) => el('div', `margin-top:16px;font-family:${S.serif ? 'NEWS' : 'ON'};font-size:${full ? 44 : 32}px;line-height:1.25;display:flex;gap:14px;align-items:flex-start`, `<span style="color:${S.acc};font-family:ON8">→</span><span>${it}</span>`, c));
  let cur = null;
  if (box && st === 'selecao-azul') { cur = el('div', `left:0;top:0;font-size:54px;color:#fff;filter:drop-shadow(0 4px 6px #000)`, '➤'); cur.className = 'a'; }
  return (t) => {
    const o = envOut(t, dur, .25);
    if (panel) { panel.style.opacity = o * Math.min(1, t / .15); if (split) panel.style.transform = `translateX(${(1 - eo(seg(t, 0, .35))) * -720}px)`; }
    const k = back(seg(t, 0, .4)); c.style.opacity = Math.min(1, t * 5) * o;
    c.style.transform = plain ? `translateY(${(1 - eo(seg(t, .1, .45))) * 40}px)` : st === 'editorial-zine' ? `rotate(${-1.5 * k}deg) scale(${.85 + .15 * k})` : `translateY(${(1 - k) * 80}px)`;
    chip.style.opacity = seg(t, .2, .35);
    spans.forEach((s, i) => { const kk = seg(t, .25 + i * .07, .45 + i * .07); s.style.opacity = kk; s.style.transform = `translateY(${(1 - eo(kk)) * 30}px)`; });
    if (box) box.style.opacity = seg(t, .5 + spans.length * .07, .7 + spans.length * .07);
    items.forEach((it, i) => { const s0 = .7 + spans.length * .07 + i * .35; it.style.opacity = seg(t, s0, s0 + .2); it.style.transform = `translateX(${(1 - eo(seg(t, s0, s0 + .3))) * 30}px)`; });
    if (cur && sel) { const r = sel.getBoundingClientRect(); const kc = eio(seg(t, .4, .95)); cur.style.transform = `translate(${1500 + (r.right - 1500) * kc}px,${900 + (r.bottom - 10 - 900) * kc}px)`; cur.style.opacity = o; }
  };
};
// tutorial-de-tela: janela com print real, cursor vai até o ponto e clica
T.mq_tela = (p, dur) => {
  const bg = el('div', `left:0;top:0;width:1920px;height:1080px;background:radial-gradient(ellipse 70% 60% at 50% 45%,#2a3040,#12151c)`); bg.className = 'a';
  const win = el('div', `left:250px;top:110px;width:1420px;height:860px;border-radius:22px;background:#1D212A;box-shadow:0 30px 80px rgba(0,0,0,.6);overflow:hidden`); win.className = 'a';
  el('div', `height:48px;display:flex;align-items:center;gap:10px;padding-left:20px;background:#262B36`, `<i style="width:15px;height:15px;border-radius:50%;background:#ff5f57;display:inline-block"></i><i style="width:15px;height:15px;border-radius:50%;background:#febc2e;display:inline-block"></i><i style="width:15px;height:15px;border-radius:50%;background:#28c840;display:inline-block"></i><span style="margin-left:20px;padding:6px 18px;border-radius:10px;background:#1D212A;font-family:ON;font-size:20px;color:#aab">${p.url || 'members.kiwify.com'}</span>`, win);
  const img = el('img', `display:block;width:1420px;height:812px;object-fit:cover`, null, win); img.src = 'img/' + (p.img || 'dash.jpg');
  const tx = 250 + p.px * 1420, ty = 158 + p.py * 812;
  const ring = el('div', `left:${tx - 40}px;top:${ty - 40}px;width:80px;height:80px;border-radius:50%;border:5px solid #0D99FF`); ring.className = 'a';
  const cur = el('div', `left:0;top:0;font-size:64px;color:#fff;filter:drop-shadow(0 4px 8px #000)`, '➤'); cur.className = 'a';
  const lab = el('div', `left:${Math.min(1300, tx + 50)}px;top:${ty - 110}px;padding:14px 24px;border-radius:14px;background:#0D99FF;color:#fff;font-family:ON8;font-size:34px;white-space:nowrap;box-shadow:0 12px 30px rgba(13,153,255,.4)`, p.label || ''); lab.className = 'a';
  return (t) => {
    const o = envOut(t, dur, .25), k = eo(seg(t, 0, .4));
    bg.style.opacity = o * Math.min(1, t / .15); win.style.opacity = o; win.style.transform = `scale(${.92 + .08 * k})`;
    const kc = eio(seg(t, .4, 1.2));
    cur.style.left = (1700 + (tx - 1700) * kc) + 'px'; cur.style.top = (1000 + (ty - 1000) * kc) + 'px'; cur.style.opacity = o; cur.style.transform = 'rotate(-35deg)';
    const kr = seg(t, 1.2, 1.6); ring.style.opacity = (kr > 0 && kr < 1 ? 1 - kr : 0) * o; ring.style.transform = `scale(${.4 + kr * 1.4})`;
    lab.style.opacity = seg(t, 1.3, 1.5) * o; lab.style.transform = `translateY(${(1 - eo(seg(t, 1.3, 1.6))) * 20}px)`;
  };
};

/* =================== V2: helpers comuns =================== */
const hsh = (i, s = 1) => { const x = Math.sin(i * 127.1 + s * 311.7) * 43758.5453; return x - Math.floor(x); };
const hl = (s, css) => String(s).replace(/\*(.+?)\*/g, `<span style="${css}">$1</span>`);
// cartão de câmera: o compose encolhe o Yuri pra dentro deste retângulo (L / R)
const CAMR = {L: {x: 90, y: 140, w: 600, h: 800}, R: {x: 1230, y: 140, w: 600, h: 800}};
const rrect = (x, y, w, h, r) => `M${x + r} ${y}H${x + w - r}A${r} ${r} 0 0 1 ${x + w} ${y + r}V${y + h - r}A${r} ${r} 0 0 1 ${x + w - r} ${y + h}H${x + r}A${r} ${r} 0 0 1 ${x} ${y + h - r}V${y + r}A${r} ${r} 0 0 1 ${x + r} ${y}Z`;
// fundo de tela cheia; com p.cam abre um buraco arredondado onde o Yuri aparece
const fullBg = (p, css, rad = 36) => {
  const b = el('div', `left:0;top:0;width:1920px;height:1080px;${css}`); b.className = 'a';
  if (p.cam) { const c = CAMR[p.cam]; const svg = `<svg xmlns='http://www.w3.org/2000/svg' width='1920' height='1080'><path fill-rule='evenodd' d='M0 0H1920V1080H0Z ${rrect(c.x, c.y, c.w, c.h, rad)}'/></svg>`; const u = `url("data:image/svg+xml;utf8,${encodeURIComponent(svg)}")`; b.style.webkitMaskImage = u; b.style.maskImage = u; }
  return b;
};
const camFrame = (p, css, rad = 36) => { if (!p.cam) return null; const c = CAMR[p.cam]; const f = el('div', `left:${c.x}px;top:${c.y}px;width:${c.w}px;height:${c.h}px;border-radius:${rad}px;box-sizing:border-box;${css}`); f.className = 'a'; return f; };
// área livre ao lado da câmera
const area = (p) => p.cam === 'L' ? {x: 760, w: 1090} : p.cam === 'R' ? {x: 70, w: 1090} : {x: 160, w: 1600};
const bgOp = (p, t, dur) => p.cam ? 1 : Math.min(1, t / .15) * (1 - seg(t, dur - .15, dur));

/* =================== GEOMÉTRICO BAUHAUS (mg-bauhaus) =================== */
const BH = {paper: '#F1E9DA', r: '#E03C31', y: '#F2B705', b: '#1E4FA3', k: '#111'};
T.bh_grid = (p, dur) => {
  const bg = fullBg(p, `background:${BH.paper}`);
  const A = area(p), M = 120;
  // formas na grade (módulos de 120px)
  const shapes = [
    {css: `width:${M * 2}px;height:${M * 2}px;border-radius:50%;background:${BH.r}`, x: A.x + A.w - M * 2 - 20, y: 60, fx: 1},
    {css: `width:${M * 3}px;height:${M}px;background:${BH.b}`, x: A.x + 20, y: 1080 - M - 60, fx: -1},
    {css: `width:0;height:0;border-left:${M}px solid transparent;border-right:${M}px solid transparent;border-bottom:${M * 1.7}px solid ${BH.y}`, x: A.x + A.w - M * 2 - 40, y: 1080 - M * 1.7 - 60, fx: 1},
    {css: `width:${M}px;height:${M}px;background:${BH.k}`, x: A.x + 20, y: 60, fx: -1},
  ].map((s) => { const e = el('div', s.css); e.className = 'a'; e.style.left = s.x + 'px'; e.style.top = s.y + 'px'; e._s = s; return e; });
  const lines = String(p.text).split('|');
  const tb = el('div', `left:${A.x + 40}px;top:${p.ty || 250}px;width:${A.w - 80}px;font-family:UNB;font-size:${p.size || 96}px;line-height:1;color:${BH.k};text-transform:uppercase;letter-spacing:-.02em`); tb.className = 'a';
  const ls = lines.map((l) => el('div', 'overflow:hidden;padding:6px 0', `<div>${hl(l, `color:${BH.r}`)}</div>`, tb));
  const items = (p.items || []).map((it, i) => { const r = el('div', `display:flex;align-items:center;gap:22px;margin-top:22px;font-family:MXB;font-size:44px;color:${BH.k};text-transform:none;letter-spacing:0`, `<span style="width:56px;height:56px;flex:none;display:inline-block;background:${[BH.r, BH.y, BH.b][i % 3]};border-radius:${i % 3 === 0 ? '50%' : '0'}"></span><span>${it}</span>`, tb); return r; });
  const rule = el('div', `left:${A.x + 40}px;top:${(p.ty || 250) - 30}px;height:14px;background:${BH.k}`); rule.className = 'a';
  return (t) => {
    const o = bgOp(p, t, dur), q = (x) => Math.round(x * 4) / 4; // movimento em degraus de módulo
    bg.style.opacity = o;
    shapes.forEach((s, i) => { const k = q(eo(seg(t, .05 + i * .1, .45 + i * .1))); s.style.transform = `translateX(${(1 - k) * s._s.fx * 480}px) rotate(${(1 - k) * 90}deg)`; s.style.opacity = o; });
    rule.style.width = (eo(seg(t, .1, .5)) * (A.w - 80)) + 'px'; rule.style.opacity = o;
    ls.forEach((l, i) => { const k = eo(seg(t, .2 + i * .12, .5 + i * .12)); l.firstChild.style.transform = `translateY(${(1 - k) * 110}%)`; });
    items.forEach((r, i) => { const s0 = .6 + i * (p.gapT || .4); const k = seg(t, s0, s0 + .25); r.style.opacity = k; r.style.transform = `translateX(${q(1 - k) * 120}px)`; });
    tb.style.opacity = o;
  };
};

/* =================== COLAGEM RECORTADA (mg-collage) =================== */
const kraft = `background-color:#d9c7a3;background-image:radial-gradient(rgba(60,40,20,.18) 1px,transparent 1.5px),radial-gradient(rgba(255,255,255,.12) 1px,transparent 1.5px),linear-gradient(115deg,rgba(0,0,0,.05),transparent 60%);background-size:7px 7px,11px 11px,100% 100%`;
const torn = (seed, w) => { let d = 'polygon('; const n = 24; for (let i = 0; i <= n; i++) d += `${(i / n * 100).toFixed(1)}% ${(hsh(i, seed) * 8).toFixed(1)}%,`; for (let i = n; i >= 0; i--) d += `${(i / n * 100).toFixed(1)}% ${(92 + hsh(i, seed + 7) * 8).toFixed(1)}%,`; return d.slice(0, -1) + ')'; };
T.cl_cut = (p, dur) => {
  const bg = fullBg(p, kraft);
  const A = area(p);
  const strip = el('div', `left:${A.x - 40}px;top:${p.cam ? 120 : 140}px;width:${A.w + 80}px;height:150px;background:#111;clip-path:${torn(3)};transform:rotate(-3deg)`); strip.className = 'a';
  const kick = el('div', `left:${A.x + 30}px;top:${p.cam ? 150 : 170}px;font-family:MB;font-size:70px;color:#f3ead7;letter-spacing:.04em;transform:rotate(-3deg);white-space:nowrap`, p.top || ''); kick.className = 'a';
  const words = String(p.text).split(' ');
  const cuts = words.map((w, i) => { const hlw = w.startsWith('*'); const c = el('div', `left:0;top:0;padding:8px 22px 14px;background:${hlw ? '#d6322b' : (i % 3 === 1 ? '#f4efe2' : '#fffdf6')};color:${hlw ? '#fff' : '#141414'};font-family:${i % 2 ? 'NEWS' : 'MB'};font-size:${(p.size || 84) * (i % 2 ? 1.1 : 1)}px;line-height:1;box-shadow:0 0 0 7px #fff,6px 10px 0 7px rgba(0,0,0,.28);white-space:nowrap`, w.replace(/\*/g, '')); c.className = 'a'; return c; });
  // layout: quebra em linhas dentro da área
  let x = A.x + 40, y = p.cam ? 340 : 360; const pos = [];
  cuts.forEach((c, i) => { const w = c.offsetWidth; if (x + w > A.x + A.w - 20) { x = A.x + 40 + (pos.length % 2) * 40; y += (p.size || 84) * 1.5; } pos.push([x, y]); x += w + 30; });
  cuts.forEach((c, i) => { c.style.left = pos[i][0] + 'px'; c.style.top = pos[i][1] + 'px'; });
  const hand = p.icon ? el('div', `left:${A.x + A.w - 260}px;top:${Math.min(820, y + 170)}px;font-size:160px;filter:grayscale(.3) sepia(.4) drop-shadow(0 0 0 #fff) drop-shadow(5px 5px 0 rgba(0,0,0,.3))`, p.icon) : null; if (hand) hand.className = 'a';
  return (t) => {
    const tb = step(t, 12), o = bgOp(p, t, dur);
    bg.style.opacity = o;
    const ks = seg(tb, 0, .25); strip.style.transform = `rotate(-3deg) translateX(${(1 - ks) * -1400}px)`; strip.style.opacity = o; kick.style.opacity = (tb > .2 ? 1 : 0) * o;
    cuts.forEach((c, i) => { const s0 = .25 + i * .16, on = tb >= s0; const jx = (hsh(Math.floor(tb * 12), i) - .5) * 4, jy = (hsh(Math.floor(tb * 12), i + 9) - .5) * 4; c.style.opacity = on ? o : 0; c.style.transform = `translate(${jx}px,${jy}px) rotate(${(hsh(i, 5) - .5) * 8}deg) scale(${tb < s0 + .08 ? 1.25 : 1})`; });
    if (hand) { hand.style.opacity = (tb > .5 ? 1 : 0) * o; hand.style.transform = `rotate(${[-8, -4, -6][Math.floor(tb * 6) % 3]}deg) scale(${tb < .6 ? 1.3 : 1})`; }
  };
};

/* =================== FLAT VECTOR 2D (mg-flat-vector) =================== */
const FV = {bg: '#2B2BFF', coral: '#FF5A4E', sun: '#FFC93C', mint: '#2ED3A0', ink: '#16133A', w: '#FFFFFF'};
const fvIcon = (k, c) => ({
  chart: `<svg width="150" height="150" viewBox="0 0 100 100"><rect x="8" y="55" width="18" height="37" fill="${c}"/><rect x="41" y="35" width="18" height="57" fill="${c}"/><rect x="74" y="12" width="18" height="80" fill="${c}"/></svg>`,
  check: `<svg width="150" height="150" viewBox="0 0 100 100"><circle cx="50" cy="50" r="46" fill="${c}"/><path d="M28 52 L44 67 L74 34" stroke="#fff" stroke-width="11" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
  coin: `<svg width="150" height="150" viewBox="0 0 100 100"><circle cx="50" cy="50" r="46" fill="${c}"/><circle cx="50" cy="50" r="34" fill="none" stroke="#fff" stroke-width="6"/><text x="50" y="66" text-anchor="middle" font-family="MB" font-size="44" fill="#fff">$</text></svg>`,
  heart: `<svg width="150" height="150" viewBox="0 0 100 100"><path d="M50 88 C10 60 4 38 16 24 C28 10 44 16 50 30 C56 16 72 10 84 24 C96 38 90 60 50 88Z" fill="${c}"/></svg>`,
  play: `<svg width="150" height="150" viewBox="0 0 100 100"><rect x="4" y="16" width="92" height="68" rx="18" fill="${c}"/><path d="M42 34 L66 50 L42 66Z" fill="#fff"/></svg>`,
  phone: `<svg width="150" height="150" viewBox="0 0 100 100"><rect x="24" y="4" width="52" height="92" rx="10" fill="${c}"/><rect x="30" y="14" width="40" height="66" rx="3" fill="#fff"/><circle cx="50" cy="88" r="4" fill="#fff"/></svg>`,
  bell: `<svg width="150" height="150" viewBox="0 0 100 100"><path d="M50 10 C30 10 24 28 24 44 L24 66 L14 78 L86 78 L76 66 L76 44 C76 28 70 10 50 10Z" fill="${c}"/><circle cx="50" cy="86" r="9" fill="${c}"/></svg>`,
  user: `<svg width="150" height="150" viewBox="0 0 100 100"><circle cx="50" cy="34" r="20" fill="${c}"/><path d="M14 94 C14 64 86 64 86 94Z" fill="${c}"/></svg>`,
}[k] || '');
T.fv_pop = (p, dur) => {
  const bg = fullBg(p, `background:${p.color || FV.bg}`);
  const A = area(p);
  const ball = el('div', `left:${A.x + A.w / 2 - 90}px;top:0;width:180px;height:180px;border-radius:50%;background:${FV.sun}`); ball.className = 'a';
  const ttl = el('div', `left:${A.x}px;top:${p.ty || 190}px;width:${A.w}px;text-align:center;font-family:FIG;font-size:${p.size || 120}px;line-height:1.02;color:#fff`, hl(p.text, `color:${FV.sun}`)); ttl.className = 'a';
  const ic = p.icons || ['chart', 'coin', 'check'];
  const cols = [FV.coral, FV.sun, FV.mint, '#fff'];
  const icons = ic.map((k, i) => { const w = A.w / ic.length; const d = el('div', `left:${A.x + w * i + w / 2 - 110}px;top:560px;width:250px;height:250px;border-radius:50%;background:${FV.ink};display:flex;align-items:center;justify-content:center`, fvIcon(k, cols[i % 4])); d.className = 'a'; const lb = p.labels ? el('div', `left:${A.x + w * i}px;top:810px;width:${w}px;text-align:center;font-family:FIG;font-size:44px;color:#fff`, p.labels[i] || '') : null; if (lb) lb.className = 'a'; return [d, lb]; });
  return (t) => {
    const o = bgOp(p, t, dur); bg.style.opacity = o;
    // bola: antecipação → estica caindo → amassa → assenta, depois vira "ponto" acima do título
    const kf = seg(t, 0, .35), ky = 60 + eo(kf) * 0; const land = seg(t, .35, .55);
    const sy = kf < 1 ? 1 + kf * .25 : 1 - Math.sin(land * Math.PI) * .3, sxx = kf < 1 ? 1 - kf * .15 : 1 + Math.sin(land * Math.PI) * .3;
    ball.style.transform = `translateY(${-220 + eio(kf) * 280}px) scale(${sxx * (1 - seg(t, .55, .8) * .65)},${sy * (1 - seg(t, .55, .8) * .65)})`; ball.style.opacity = o;
    const kt = seg(t, .45, .8); ttl.style.opacity = Math.min(1, kt * 3) * o; ttl.style.transform = `scale(${back(kt)})`;
    icons.forEach(([d, lb], i) => { const s0 = .75 + i * .18, k = seg(t, s0, s0 + .35); const sq = k < 1 ? back(k) : 1 + Math.sin((t - s0) * 6) * .02; d.style.transform = `scale(${sq}) rotate(${(1 - k) * -30}deg)`; d.style.opacity = Math.min(1, k * 4) * o; if (lb) { lb.style.opacity = seg(t, s0 + .2, s0 + .4) * o; lb.style.transform = `translateY(${(1 - eo(seg(t, s0 + .2, s0 + .45))) * 30}px)`; } });
  };
};

/* =================== LEGENDA DE REALITY (mg-hanazi) =================== */
T.hz_pop = (p, dur) => {
  const cx = p.cx || 960, cy = p.cy || 260;
  const fill = p.fill || 'linear-gradient(180deg,#FFF35C 0%,#FF9F1C 100%)', o1 = p.o1 || '#FF2E88';
  // explosão (balão de grito) com linhas de velocidade
  const s = svgBox(1100, 520, `left:${cx - 550}px;top:${cy - 260}px`);
  let d = ''; const N = 22; for (let i = 0; i < N; i++) { const a = i / N * Math.PI * 2, r = i % 2 ? 175 : 250; d += (i ? 'L' : 'M') + (550 + Math.cos(a) * r * 1.9).toFixed(1) + ' ' + (260 + Math.sin(a) * r * .95).toFixed(1); }
  const burst = document.createElementNS(svgNS, 'path'); burst.setAttribute('d', d + 'Z'); burst.setAttribute('fill', p.burst || '#4DE1FF'); burst.setAttribute('stroke', '#fff'); burst.setAttribute('stroke-width', 12); burst.setAttribute('stroke-linejoin', 'round'); s.appendChild(burst);
  if (p.noburst) burst.style.display = 'none';
  const chars = [...p.text];
  const wrap = el('div', `left:${cx - 900}px;top:${cy - 90}px;width:1800px;text-align:center;white-space:nowrap`); wrap.className = 'a';
  const cs = chars.map((c) => { const sp = el('span', `display:inline-block;font-family:UNB;font-size:${p.size || 120}px;line-height:1.2;background:${fill};-webkit-background-clip:text;background-clip:text;color:transparent;-webkit-text-stroke:0;filter:drop-shadow(0 0 0 #fff) drop-shadow(5px 0 0 #fff) drop-shadow(-5px 0 0 #fff) drop-shadow(0 5px 0 #fff) drop-shadow(0 -5px 0 #fff) drop-shadow(5px 0 0 ${o1}) drop-shadow(-5px 0 0 ${o1}) drop-shadow(0 5px 0 ${o1}) drop-shadow(0 -5px 0 ${o1}) drop-shadow(6px 8px 0 rgba(0,0,0,.45))`, c === ' ' ? '&nbsp;' : c, wrap); return sp; });
  // gotas de suor + brilhos
  const fx = svgBox(1600, 600, `left:${cx - 800}px;top:${cy - 300}px`);
  const deco = [];
  [[230, 120], [1370, 140], [300, 470], [1300, 460]].forEach(([x, y], i) => { const g = document.createElementNS(svgNS, 'path'); g.setAttribute('d', i < 2 ? `M${x} ${y} C ${x - 22} ${y + 34} ${x - 22} ${y + 60} ${x} ${y + 60} C ${x + 22} ${y + 60} ${x + 22} ${y + 34} ${x} ${y}Z` : `M${x} ${y - 36} L${x + 9} ${y - 9} L${x + 36} ${y} L${x + 9} ${y + 9} L${x} ${y + 36} L${x - 9} ${y + 9} L${x - 36} ${y} L${x - 9} ${y - 9}Z`); g.setAttribute('fill', i < 2 ? '#7fd8ff' : '#FFF35C'); g.setAttribute('stroke', '#fff'); g.setAttribute('stroke-width', 5); fx.appendChild(g); deco.push(g); });
  return (t) => {
    const o = envOut(t, dur, .2);
    const kb = seg(t, 0, .25); s.style.transform = `scale(${kb < 1 ? kb * 1.15 : 1 + Math.sin(t * 9) * .015}) rotate(${Math.sin(t * 3) * 2}deg)`; s.style.opacity = o;
    cs.forEach((c, i) => { const s0 = .08 + i * (2 / 30), k = seg(t, s0, s0 + 8 / 30); const sc = k < .6 ? k / .6 * 1.15 : 1.15 - (k - .6) / .4 * .15; c.style.transform = `scale(${sc}) translateY(${Math.sin(t * 8 + i) * 4}px) rotate(${(i % 2 ? 4 : -4) * (1 - k) + Math.sin(t * 5 + i) * 2}deg)`; c.style.opacity = Math.min(1, k * 3) * o; });
    deco.forEach((g, i) => { const k = seg(t, .3 + i * .08, .5 + i * .08); g.style.opacity = k * o; g.style.transformBox = 'fill-box'; g.style.transformOrigin = 'center'; g.style.transform = i < 2 ? `translateY(${Math.max(0, t - .5) * 60}px)` : `scale(${back(k) * (1 + Math.sin(t * 10 + i) * .15)}) rotate(${t * 90}deg)`; });
  };
};

/* =================== LINE ART UM TRAÇO (mg-line-art) =================== */
const LA_SHAPES = {
  growth: 'M120 520 L300 400 L420 450 L620 250 L760 300 L980 80 M900 80 L980 80 L980 160',
  play: 'M100 300 C100 120 200 80 540 80 C880 80 980 120 980 300 C980 480 880 520 540 520 C200 520 100 480 100 300 M470 200 L470 400 L640 300 Z',
  bulb: 'M540 520 L540 470 M480 470 L600 470 M470 430 C470 360 380 330 380 220 C380 120 460 60 540 60 C620 60 700 120 700 220 C700 330 610 360 610 430 Z M500 300 L540 250 L580 300',
  phone: 'M400 60 L680 60 C710 60 720 70 720 100 L720 500 C720 530 710 540 680 540 L400 540 C370 540 360 530 360 500 L360 100 C360 70 370 60 400 60 M500 500 L580 500 M420 160 L660 160 M420 230 L600 230 M420 300 L640 300',
  dollar: 'M640 160 C600 100 460 90 430 160 C400 230 480 260 540 280 C620 305 680 340 650 420 C620 500 470 500 420 430 M540 60 L540 540',
  target: 'M540 300 m-220 0 a220 220 0 1 0 440 0 a220 220 0 1 0 -440 0 M540 300 m-130 0 a130 130 0 1 0 260 0 a130 130 0 1 0 -260 0 M540 300 m-40 0 a40 40 0 1 0 80 0 a40 40 0 1 0 -80 0 M900 40 L560 290',
  infinity: 'M540 300 C440 160 220 160 220 300 C220 440 440 440 540 300 C640 160 860 160 860 300 C860 440 640 440 540 300',
  calendar: 'M300 120 L780 120 L780 520 L300 520 Z M300 210 L780 210 M400 80 L400 160 M680 80 L680 160 M380 300 L440 300 M500 300 L560 300 M620 300 L680 300 M380 400 L440 400 M500 400 L560 400',
};
T.la_draw = (p, dur) => {
  const bg = fullBg(p, 'background:radial-gradient(ellipse 80% 70% at 50% 40%,#16223a 0%,#0B1320 70%)');
  const A = area(p);
  const W = 1080, H = 600, sc = Math.min(1, (A.w - 40) / W) * (p.cam ? .9 : 1);
  const s = svgBox(W, H, `left:${A.x + (A.w - W * sc) / 2}px;top:${p.cam ? 130 : 90}px;transform:scale(${sc});transform-origin:0 0;filter:drop-shadow(0 0 6px rgba(233,215,165,.55))`);
  const path = pathEl(s, LA_SHAPES[p.shape || 'growth'], '#E9D7A5', 6);
  const tip = document.createElementNS(svgNS, 'circle'); tip.setAttribute('r', 9); tip.setAttribute('fill', '#fff6d8'); tip.style.filter = 'drop-shadow(0 0 12px #E9D7A5)'; s.appendChild(tip);
  const tx = el('div', `left:${A.x}px;top:${p.cam ? 760 : 720}px;width:${A.w}px;text-align:center;font-family:ISI;font-size:${p.size || 86}px;color:#F3EAD2;line-height:1.05`, hl(p.text, 'color:#E9D7A5;font-family:FRA')); tx.className = 'a';
  const sub = p.sub ? el('div', `left:${A.x}px;top:${(p.cam ? 760 : 720) + (p.size || 86) * 1.25}px;width:${A.w}px;text-align:center;font-family:JB;font-size:26px;letter-spacing:.3em;color:#8b8f99`, p.sub) : null; if (sub) sub.className = 'a';
  return (t) => {
    const o = bgOp(p, t, dur); bg.style.opacity = o;
    const k = eio(seg(t, .05, Math.min(dur * .6, 2.2))); draw(path, k); s.style.opacity = o;
    const pt = path.getPointAtLength(path._L * k); tip.setAttribute('cx', pt.x); tip.setAttribute('cy', pt.y); tip.style.opacity = k < 1 ? 1 : 0;
    const kt = seg(t, .5, 1.1); tx.style.opacity = kt * o; tx.style.filter = `blur(${(1 - kt) * 10}px)`; tx.style.letterSpacing = `${(1 - eo(kt)) * .2}em`;
    if (sub) sub.style.opacity = seg(t, 1, 1.4) * o;
  };
};

/* =================== SYNTHWAVE 80s / VHS (mg-synthwave) =================== */
T.sw_title = (p, dur) => {
  const bg = fullBg(p, 'background:linear-gradient(180deg,#0b0420 0%,#2a0b4a 45%,#5b1a6e 62%,#0b0420 62.2%,#0b0420 100%)');
  const A = area(p), cxs = A.x + A.w / 2;
  const stars = el('div', `left:0;top:0;width:1920px;height:640px;background-image:radial-gradient(#fff 1px,transparent 1.6px),radial-gradient(#ffd6ff 1px,transparent 1.4px);background-size:97px 89px,151px 133px;opacity:.6`); stars.className = 'a';
  const sun = el('div', `left:${cxs - 230}px;top:${p.cam ? 360 : 380}px;width:460px;height:460px;border-radius:50%;background:linear-gradient(180deg,#ffe95c 0%,#ff9a3c 45%,#ff2e88 100%);-webkit-mask:repeating-linear-gradient(180deg,#000 0 26px,transparent 26px 34px);box-shadow:0 0 80px #ff2e88`); sun.className = 'a';
  const hz = 670;
  const grid = svgBox(1920, 1080 - hz, `left:0;top:${hz}px`);
  const gl = [];
  for (let i = -14; i <= 14; i++) { const l = document.createElementNS(svgNS, 'line'); l.setAttribute('x1', 960 + i * 22); l.setAttribute('y1', 0); l.setAttribute('x2', 960 + i * 260); l.setAttribute('y2', 1080 - hz); l.setAttribute('stroke', '#ff2ee6'); l.setAttribute('stroke-width', 3); grid.appendChild(l); }
  for (let i = 0; i < 12; i++) { const l = document.createElementNS(svgNS, 'line'); l.setAttribute('x1', 0); l.setAttribute('x2', 1920); l.setAttribute('stroke', '#2ee8ff'); l.setAttribute('stroke-width', 3); grid.appendChild(l); gl.push(l); }
  grid.style.filter = 'drop-shadow(0 0 4px #ff2ee6) drop-shadow(0 0 18px #ff2ee6)';
  const ttl = el('div', `left:${A.x}px;top:${p.ty || 110}px;width:${A.w}px;text-align:center;font-family:ORB;font-size:${p.size || 120}px;line-height:1;background:linear-gradient(180deg,#e8f6ff 0%,#9ad0ff 40%,#1b2a6b 50%,#ffffff 52%,#ff9cf2 80%,#fff 100%);-webkit-background-clip:text;background-clip:text;color:transparent;-webkit-text-stroke:2px rgba(255,255,255,.7);filter:drop-shadow(0 6px 0 #2b0b45) drop-shadow(0 0 20px rgba(255,46,230,.7));white-space:nowrap`, p.text); ttl.className = 'a';
  const scr = el('div', `left:${A.x}px;top:${(p.ty || 110) + (p.size || 120) * 1.0}px;width:${A.w}px;text-align:center;font-family:PM;font-size:${p.ssize || 84}px;color:#ff5ce1;text-shadow:0 0 6px #fff,0 0 18px #ff2ee6,0 0 40px #ff2ee6;transform:rotate(-5deg);white-space:nowrap`, p.sub || ''); scr.className = 'a';
  const osd = el('div', `left:${A.x + 40}px;top:40px;font-family:JB;font-size:40px;color:#fff;text-shadow:2px 2px 0 #000`, 'PLAY ►'); osd.className = 'a';
  const noise = el('div', `left:0;top:0;width:1920px;height:1080px;background:repeating-linear-gradient(0deg,rgba(255,255,255,.05) 0 2px,transparent 2px 4px);mix-blend-mode:screen`); noise.className = 'a';
  const track = el('div', `left:0;width:1920px;height:60px;background:linear-gradient(180deg,transparent,rgba(255,255,255,.35),transparent)`); track.className = 'a';
  if (p.cam) [stars, sun, grid, noise, track].forEach((e) => { e.style.webkitMaskImage = bg.style.webkitMaskImage; e.style.maskImage = bg.style.maskImage; });
  return (t) => {
    const o = bgOp(p, t, dur); [bg, stars, grid, noise].forEach((e) => e.style.opacity = o);
    sun.style.transform = `translateY(${(1 - eo(seg(t, 0, 1.4))) * 300}px)`; sun.style.opacity = o;
    gl.forEach((l, i) => { const z = ((i + t * 2.2) % 12) / 12; const y = Math.pow(z, 2.2) * (1080 - hz); l.setAttribute('y1', y); l.setAttribute('y2', y); });
    const k = seg(t, .35, .55); ttl.style.transform = `scale(${k < 1 ? 2.4 - 1.4 * eo(k) : 1})`; ttl.style.opacity = Math.min(1, k * 3) * o;
    const ks = seg(t, .8, 1.3); scr.style.clipPath = `inset(0 ${(1 - ks) * 100}% 0 0)`; scr.style.opacity = o;
    osd.style.opacity = (t < 1.2 && Math.floor(t * 4) % 2 === 0 ? 1 : 0) * o;
    const ty = (t * 900) % 1300 - 100; track.style.top = ty + 'px'; track.style.opacity = (t < .5 ? .9 : .25) * o;
  };
};

/* =================== EXPLICADOR COM ADESIVOS (mg-paperclip) =================== */
T.pc_board = (p, dur) => {
  const bg = fullBg(p, 'background-color:#E9EEF2;background-image:linear-gradient(#d9e1e8 2px,transparent 2px),linear-gradient(90deg,#d9e1e8 2px,transparent 2px);background-size:80px 80px');
  const A = area(p);
  const cam = el('div', `left:0;top:0;width:${Math.max(1920, 300 + p.items.length * 520)}px;height:1080px`); cam.className = 'a';
  if (p.cam) { cam.style.webkitMaskImage = bg.style.webkitMaskImage; }
  const ttl = el('div', `left:${A.x + 20}px;top:90px;font-family:ON8;font-size:${p.size || 64}px;color:#2b3440;white-space:nowrap`, hl(p.title || '', 'color:#FF5A36')); ttl.className = 'a';
  const SP = Math.max(400, Math.min(470, (A.w - 40) / p.items.length));
  const cards = p.items.map((it, i) => {
    const x = A.x + 40 + i * SP, y = 300 + (i % 2) * 70;
    const c = el('div', `position:absolute;left:${x}px;top:${y}px;width:${SP - 70}px;padding:30px;box-sizing:border-box;background:#fff;border-radius:26px;box-shadow:0 0 0 12px #fff,0 18px 34px rgba(43,52,64,.25);text-align:center`, `<div style="font-size:120px;line-height:1.1">${it.icon || '★'}</div><div style="font-family:ON8;font-size:${it.big ? 76 : 44}px;color:${it.c || '#2b3440'};margin-top:10px;line-height:1.05">${it.t}</div><div style="font-family:ON;font-size:30px;color:#6b7785;margin-top:8px">${it.s || ''}</div>`, cam);
    return c;
  });
  const arrows = p.items.slice(1).map((_, i) => { const s = svgBox(120, 60, `left:${A.x + 40 + i * SP + SP - 75}px;top:${470 + (i % 2) * 35}px`, cam); return pathEl(s, 'M5 30 L100 30 M80 12 L105 30 L80 48', '#FF5A36', 8); });
  const visible = Math.floor((A.w - 40) / SP);
  return (t) => {
    const o = bgOp(p, t, dur); bg.style.opacity = o; cam.style.opacity = o;
    const n = p.items.length, per = Math.max(.5, (dur - 1) / n);
    cards.forEach((c, i) => { const s0 = .3 + i * per, k = seg(t, s0, s0 + .35); c.style.transform = `scale(${back(k)}) rotate(${(i % 2 ? 3 : -3) * k}deg)`; c.style.opacity = Math.min(1, k * 4); });
    arrows.forEach((a, i) => draw(a, seg(t, .3 + (i + 1) * per - .25, .3 + (i + 1) * per)));
    // a câmera percorre a lousa quando os cartões passam da área
    const last = Math.max(0, n - visible), cur = clamp((t - .3) / per - (visible - 1), 0, last);
    cam.style.transform = `translateX(${-eio(cur / Math.max(1, last)) * last * SP}px)`;
    ttl.style.opacity = seg(t, 0, .3) * o;
  };
};

/* =================== LÍQUIDO (mg-liquid) =================== */
T.lq_blob = (p, dur) => {
  const bg = fullBg(p, 'background:radial-gradient(ellipse 80% 70% at 50% 40%,#3a1446 0%,#1c0a24 75%)');
  const A = area(p), cx = A.x + A.w / 2, cy = p.cy || 470;
  const s = svgBox(1920, 1080, 'left:0;top:0');
  const id = 'goo' + IDX;
  s.innerHTML = `<defs><filter id="${id}"><feGaussianBlur in="SourceGraphic" stdDeviation="22"/><feColorMatrix values="1 0 0 0 0 0 1 0 0 0 0 0 1 0 0 0 0 0 40 -18"/><feComposite in="SourceGraphic" operator="atop"/></filter><linearGradient id="lg${IDX}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ff8a1f"/><stop offset=".5" stop-color="#ff2e88"/><stop offset="1" stop-color="#8a2be2"/></linearGradient></defs><g filter="url(#${id})" fill="url(#lg${IDX})"></g>`;
  const g = s.querySelector('g');
  const blobs = Array.from({length: 7}, (_, i) => { const c = document.createElementNS(svgNS, 'circle'); g.appendChild(c); return {c, a: hsh(i, 2) * 6.28, r: 60 + hsh(i, 3) * 70, sp: .6 + hsh(i, 4)}; });
  const wave = document.createElementNS(svgNS, 'path'); g.appendChild(wave);
  if (p.cam) { s.style.webkitMaskImage = bg.style.webkitMaskImage; }
  const shine = el('div', `left:${cx - 300}px;top:${cy - 230}px;width:200px;height:90px;border-radius:50%;background:radial-gradient(ellipse,rgba(255,255,255,.7),transparent 70%);transform:rotate(-25deg)`); shine.className = 'a';
  const tx = el('div', `left:${A.x}px;top:${cy - (p.size || 110) * .6}px;width:${A.w}px;text-align:center;font-family:UNB;font-size:${p.size || 110}px;line-height:1.05;color:#fff;text-shadow:0 6px 30px rgba(60,0,60,.6)`, hl(p.text, 'color:#ffe0f4')); tx.className = 'a';
  const sub = el('div', `left:${A.x}px;top:${cy + 260}px;width:${A.w}px;text-align:center;font-family:ON8;font-size:44px;color:#ffc8ea`, p.sub || ''); sub.className = 'a';
  return (t) => {
    const o = bgOp(p, t, dur); bg.style.opacity = o; s.style.opacity = o;
    const m = eo(seg(t, .1, 1.2)); // gotas caem e se fundem no centro
    blobs.forEach((b, i) => { const fall = eo(seg(t, i * .07, i * .07 + .5)); const R = (1 - m) * 420 + 60; const x = cx + Math.cos(b.a + t * b.sp) * R, y = (cy - 600) * (1 - fall) + fall * (cy + Math.sin(b.a + t * b.sp) * R * .55); b.c.setAttribute('cx', x); b.c.setAttribute('cy', y); b.c.setAttribute('r', b.r * (.7 + m * .9)); });
    // onda que inunda o fundo
    const kw = seg(t, .2, 1); const top = 1080 - eo(kw) * 260; let d = `M${A.x - 100} 1180 L${A.x - 100} ${top}`; for (let x = A.x - 100; x <= A.x + A.w + 100; x += 40) d += ` L${x} ${(top + Math.sin(x / 90 + t * 5) * 22 + Math.sin(x / 47 - t * 3) * 10).toFixed(1)}`; wave.setAttribute('d', d + ` L${A.x + A.w + 100} 1180Z`);
    shine.style.opacity = seg(t, .9, 1.2) * o * .8;
    const kt = seg(t, .7, 1.1); tx.style.opacity = kt * o; tx.style.transform = `scale(${.6 + .4 * back(kt)},${.6 + .4 * back(seg(t, .74, 1.14))})`;
    sub.style.opacity = seg(t, 1.2, 1.5) * o;
  };
};

/* =================== MORPH (mg-morph) =================== */
T.mo_chain = (p, dur) => {
  const st = p.steps; // [{shape:'circle|square|capsule|diamond|pill', c:'#hex', bg:'#hex', t:'palavra'}]
  const bg = fullBg(p, `background:${st[0].bg}`);
  const A = area(p), cx = A.x + A.w / 2;
  const wipe = el('div', `left:0;top:0;width:1920px;height:1080px`); wipe.className = 'a'; if (p.cam) { wipe.style.webkitMaskImage = bg.style.webkitMaskImage; }
  const sh = el('div', `left:${cx - 160}px;top:220px;width:320px;height:320px`); sh.className = 'a';
  const word = el('div', `left:${A.x}px;top:640px;width:${A.w}px;text-align:center;font-family:MAN;font-size:${p.size || 100}px;color:#fff;line-height:1;text-shadow:0 5px 0 rgba(0,0,0,.28)`); word.className = 'a';
  const top = p.top ? el('div', `left:${A.x}px;top:110px;width:${A.w}px;text-align:center;font-family:JB;font-size:30px;letter-spacing:.35em;color:rgba(255,255,255,.75)`, p.top) : null; if (top) top.className = 'a';
  const geo = {circle: [320, 320, 160, 0], square: [300, 300, 40, 0], capsule: [460, 220, 110, 0], diamond: [260, 260, 30, 45], pill: [180, 380, 90, 0], blob: [340, 300, 150, 20]};
  const cb = (x) => { const a = .7, b = .3; return eio(x); };
  return (t) => {
    const o = bgOp(p, t, dur); bg.style.opacity = o; wipe.style.opacity = o; sh.style.opacity = o; word.style.opacity = o; if (top) top.style.opacity = o;
    const per = dur / st.length; const i = Math.min(st.length - 1, Math.floor(t / per)); const lt = t - i * per;
    const A0 = st[Math.max(0, i - 1)], B = st[i]; const k = i === 0 ? 1 : cb(seg(lt, 0, .45));
    const g0 = geo[A0.shape] || geo.circle, g1 = geo[B.shape] || geo.circle;
    // passa por um círculo intermediário com squash & stretch
    const mid = Math.sin(k * Math.PI); const lerp = (a, b) => a + (b - a) * k;
    const w = lerp(g0[0], g1[0]) * (1 + mid * .12), h = lerp(g0[1], g1[1]) * (1 - mid * .12), r = Math.max(lerp(g0[2], g1[2]), mid * 150), rot = lerp(g0[3], g1[3]) + mid * 90;
    sh.style.width = w + 'px'; sh.style.height = h + 'px'; sh.style.left = (cx - w / 2) + 'px'; sh.style.top = (380 - h / 2) + 'px'; sh.style.borderRadius = r + 'px'; sh.style.transform = `rotate(${rot}deg) scale(${i === 0 ? back(seg(t, 0, .4)) : 1})`;
    sh.style.background = k < .5 ? A0.c : B.c;
    // fundo: wipe circular de cor a cada troca
    wipe.style.background = B.bg; wipe.style.clipPath = `circle(${(i === 0 ? 1 : eio(seg(lt, 0, .5))) * 1300}px at ${cx}px 380px)`;
    if (i > 0 && lt < .5) bg.style.background = A0.bg; else bg.style.background = B.bg;
    word.innerHTML = B.t || ''; word.style.color = B.tc || '#fff'; const kw = seg(lt, .25, .5); word.style.transform = `translateY(${(1 - eo(kw)) * 40}px)`; word.style.opacity = Math.min(o, kw);
  };
};

/* =================== KINETIC CREME (kinetic-creme) =================== */
const KC = {bg: '#ECE3D5', ink: '#1C1915', or: '#F47B20', gray: '#6F665C', ok: '#1FA463', win: '#1E1C1A'};
const kcCity = (parent, op = .22) => { const s = svgBox(1920, 300, `left:0;top:780px;opacity:${op}`, parent); let d = 'M0 300 '; let x = 0; let i = 0; while (x < 1920) { const w = 60 + hsh(i, 9) * 110, h = 60 + hsh(i, 8) * 200; d += `L${x} ${300 - h} L${x + w} ${300 - h} `; x += w; i++; } pathEl(s, d + 'L1920 300', KC.ink, 2).style.strokeDashoffset = 0; return s; };
T.kc_words = (p, dur) => {
  const bg = fullBg(p, `background:${KC.bg}`); kcCity(bg);
  const A = area(p);
  const box = el('div', `left:${A.x + 20}px;top:${p.ty || 300}px;width:${A.w - 40}px;font-family:ITX;font-size:${p.size || 124}px;line-height:1.04;color:${KC.ink};letter-spacing:-.03em;text-align:${p.cam ? 'left' : 'center'}`); box.className = 'a';
  const ws = String(p.text).split(' ').map((w) => { const h = w.startsWith('*'); return el('span', `display:inline-block;margin-right:.24em;${h ? `color:${KC.or};font-family:ISI;font-size:1.1em;letter-spacing:0` : ''}`, w.replace(/\*/g, ''), box); });
  const kick = p.top ? el('div', `left:${A.x + 20}px;top:${(p.ty || 300) - 70}px;width:${A.w - 40}px;font-family:JB;font-size:28px;letter-spacing:.3em;color:${KC.gray};text-align:${p.cam ? 'left' : 'center'}`, p.top) : null; if (kick) kick.className = 'a';
  let pills = (p.pills || []).map((s) => el('div', `display:inline-flex;align-items:center;gap:14px;margin:26px 18px 0 0;padding:14px 26px 14px 16px;border-radius:60px;background:#fff;border:2px solid #d9cdb9;font-family:FIG;font-size:36px;color:${KC.ink};letter-spacing:0;text-align:left`, `<span style="width:44px;height:44px;border-radius:50%;background:${KC.ok};color:#fff;display:inline-flex;align-items:center;justify-content:center;font-size:28px">✓</span>${s}`, box));
  if (pills.length) { const br = document.createElement('div'); box.insertBefore(br, pills[0]); }
  return (t) => {
    const o = bgOp(p, t, dur); bg.style.opacity = o; box.style.opacity = o; if (kick) kick.style.opacity = seg(t, 0, .3) * o;
    const ph = t < dur - .35 ? 0 : seg(t, dur - .35, dur); // saída "chicote": desliza com desfoque
    box.style.transform = `translateX(${-eio(ph) * 600}px)`; box.style.filter = ph > 0 ? `blur(${ph * 14}px)` : 'none';
    ws.forEach((w, i) => { const k = seg(t, .1 + i * (p.gapW || .11), .45 + i * (p.gapW || .11)); w.style.opacity = k; w.style.filter = `blur(${(1 - k) * 14}px)`; w.style.transform = `translateY(${(1 - eo(k)) * 24}px)`; });
    pills.forEach((q, i) => { const s0 = .3 + ws.length * (p.gapW || .11) + i * .3, k = seg(t, s0, s0 + .3); q.style.opacity = k; q.style.transform = `scale(${back(k)})`; });
  };
};
// painel com contadores + gráfico subindo (kinetic-creme)
T.kc_panel = (p, dur) => {
  const bg = fullBg(p, `background:${KC.bg}`); kcCity(bg);
  const A = area(p), w = Math.min(A.w - 60, 1100), x = A.x + (A.w - w) / 2;
  const card = el('div', `left:${x}px;top:${p.cam ? 200 : 170}px;width:${w}px;padding:40px 46px;box-sizing:border-box;background:#fff;border-radius:28px;box-shadow:0 30px 60px rgba(28,25,21,.18)`); card.className = 'a';
  el('div', `font-family:JB;font-size:26px;letter-spacing:.25em;color:${KC.gray}`, p.top || 'PAINEL', card);
  const ttl = el('div', `font-family:ITX;font-size:58px;color:${KC.ink};margin:10px 0 26px;letter-spacing:-.02em`, hl(p.title || '', `color:${KC.or}`), card);
  const row = el('div', `display:flex;gap:26px`, '', card);
  const nums = p.stats.map((s) => { const b = el('div', `flex:1;padding:22px 24px;border-radius:18px;background:#F6F1E8`, `<div style="font-family:FIG6;font-size:28px;color:${KC.gray}">${s.l}</div><div class="n" style="font-family:ITX;font-size:66px;color:${s.c || KC.ink};margin-top:6px">0</div>`, row); return [b.querySelector('.n'), s]; });
  const ch = svgBox(w - 92, 220, 'position:relative;display:block;margin-top:30px', card);
  const pts = (p.curve || [5, 8, 6, 14, 12, 22, 30, 45, 60, 100]).map((v, i, a) => [i / (a.length - 1) * (w - 92), 210 - v / Math.max(...a) * 190]);
  const line = pathEl(ch, 'M' + pts.map((q) => q.join(' ')).join(' L'), KC.or, 8);
  return (t) => {
    const o = bgOp(p, t, dur); bg.style.opacity = o; card.style.opacity = o;
    const k = back(seg(t, 0, .45)); card.style.transform = `translateY(${(1 - k) * 120}px) scale(${.92 + .08 * k})`;
    nums.forEach(([n, s], i) => { const kk = eo(seg(t, .4 + i * .15, Math.min(dur - .3, 1.9 + i * .15))); const v = s.from + (s.to - s.from) * kk; n.textContent = (s.pre || '') + Math.round(v).toLocaleString('pt-BR') + (s.suf || ''); });
    draw(line, eio(seg(t, .5, Math.min(dur - .3, 2.2))));
  };
};

/* =================== MANIFESTO FEED (manifesto-feed) =================== */
const MF = {bg: '#0B0C0D', w: '#F4F3EE', g: '#8B9095', st: '#282B2F', co: '#FF633E'};
T.mf_essay = (p, dur) => {
  const bg = fullBg(p, `background:${MF.bg}`);
  const A = area(p);
  // grade de "cards de feed" procedurais ao fundo, rolando
  const feed = el('div', `left:${A.x}px;top:0;width:${A.w}px;height:1080px;overflow:hidden;opacity:.5`); feed.className = 'a';
  const cols = Math.max(3, Math.floor(A.w / 230)); const cards = [];
  for (let i = 0; i < cols * 6; i++) { const c = el('div', `position:absolute;left:${(i % cols) * (A.w / cols) + 8}px;top:${Math.floor(i / cols) * 330}px;width:${A.w / cols - 16}px;height:310px;border-radius:16px;background:linear-gradient(${Math.floor(hsh(i, 1) * 360)}deg,${MF.st},#16181a);border:1px solid #33373c;overflow:hidden`, `<div style="position:absolute;left:14px;bottom:16px;width:60%;height:10px;border-radius:5px;background:#3a3f45"></div><div style="position:absolute;left:14px;bottom:34px;width:40%;height:10px;border-radius:5px;background:#3a3f45"></div><div style="position:absolute;left:50%;top:40%;transform:translate(-50%,-50%);width:0;height:0;border-left:26px solid #4a4f55;border-top:16px solid transparent;border-bottom:16px solid transparent"></div>`, feed); cards.push(c); }
  const shade = el('div', `left:${A.x}px;top:0;width:${A.w}px;height:1080px;background:linear-gradient(90deg,${MF.bg} 0%,rgba(11,12,13,.82) 30%,rgba(11,12,13,.82) 70%,${MF.bg} 100%)`); shade.className = 'a';
  const mono = el('div', `left:${A.x + 40}px;top:${p.cam ? 170 : 200}px;font-family:JB;font-size:24px;letter-spacing:.2em;color:${MF.g}`, (p.top || 'MANIFESTO') + ' — ' + String(IDX).padStart(3, '0')); mono.className = 'a';
  const tx = el('div', `left:${A.x + 40}px;top:${p.cam ? 230 : 270}px;width:${A.w - 80}px;font-family:ITX;font-size:${p.size || 112}px;line-height:.98;color:${MF.w};letter-spacing:-.035em`); tx.className = 'a';
  const ws = String(p.text).split(' ').map((w) => { const h = w.startsWith('*'); return el('span', `display:inline-block;margin-right:.22em;${h ? `color:${MF.co}` : ''}`, w.replace(/\*/g, ''), tx); });
  const foot = el('div', `left:${A.x + 40}px;top:960px;width:${A.w - 80}px;display:flex;justify-content:space-between;font-family:JB;font-size:22px;color:${MF.g};letter-spacing:.15em`, `<span>${p.foot || 'RENDA SECRETA'}</span><span>● REC</span>`); foot.className = 'a';
  return (t) => {
    const o = bgOp(p, t, dur); [bg, feed, shade, mono, foot].forEach((e) => e.style.opacity = o * (e === feed ? .5 : 1));
    feed.firstChild && cards.forEach((c, i) => { c.style.transform = `translateY(${-((t * (60 + (i % cols) * 25)) % 330)}px)`; });
    // recua (câmera 2.5D) enquanto as palavras entram pesadas
    const z = 1.08 - .08 * eo(seg(t, 0, dur)); tx.style.transform = `scale(${z})`; tx.style.transformOrigin = '0 0'; tx.style.opacity = o;
    ws.forEach((w, i) => { const k = seg(t, .1 + i * .09, .3 + i * .09); w.style.opacity = k; w.style.transform = `translateY(${(1 - eo(k)) * 50}px)`; });
  };
};

/* =================== EDIÇÃO REEL ("reel do sapato") =================== */
// headline com valor riscado + pílula verde, palavra em caixa preta, foto em card com rótulo e seta
T.er_head = (p, dur) => {
  const bg = fullBg(p, 'background:#f4f4f2');
  const A = area(p);
  const head = el('div', `left:${A.x + 20}px;top:${p.cam ? 170 : 150}px;width:${A.w - 40}px;font-family:MB;font-size:${p.size || 76}px;line-height:1.12;color:#111`); head.className = 'a';
  const parts = String(p.head).split('|').map((ln) => el('div', 'margin-bottom:10px', ln.replace(/~(.+?)~/g, `<span class="old" style="display:inline-block;position:relative;padding:0 16px;background:#fff;border:4px solid #111;border-radius:12px">$1<i style="position:absolute;left:-6px;right:-6px;top:50%;height:8px;background:#E53935;transform:rotate(-6deg) scaleX(0);transform-origin:0 50%"></i></span>`).replace(/\*(.+?)\*/g, `<span class="pill" style="display:inline-block;padding:2px 26px;border-radius:60px;background:#22C55E;color:#fff">$1</span>`), head));
  const box = p.box ? el('div', `left:${A.x + 20}px;top:${p.boxy || 560}px;padding:18px 34px;background:#0f0f0f;color:#fff;font-family:MB;font-size:${p.bsize || 92}px;line-height:1;transform:rotate(-2deg)`, p.box) : null; if (box) box.className = 'a';
  let card = null, lab = null, ar = null;
  if (p.pic) {
    const cw = 420, x = A.x + A.w - cw - 30, y = p.picy || 470;
    card = el('div', `left:${x}px;top:${y}px;width:${cw}px;height:${cw * .75}px;background:#fff;padding:14px;box-sizing:border-box;border-radius:18px;box-shadow:0 20px 40px rgba(0,0,0,.25)`, `<div style="width:100%;height:100%;border-radius:10px;background:${p.picbg || 'linear-gradient(135deg,#ffd76b,#ff7a59)'};display:flex;align-items:center;justify-content:center;font-size:150px">${p.pic}</div>`); card.className = 'a';
    if (p.label) { lab = el('div', `left:${x - 260}px;top:${y + cw * .75 + 30}px;width:260px;text-align:right;font-family:CAV;font-size:46px;color:#111`, p.label); lab.className = 'a'; const s = svgBox(140, 110, `left:${x - 120}px;top:${y + cw * .75 - 70}px`); ar = [pathEl(s, 'M10 100 C 40 60 70 40 120 20', '#111', 6), pathEl(s, 'M95 12 L122 19 L110 44', '#111', 6)]; }
  }
  const olds = [...head.querySelectorAll('.old i')], pills = [...head.querySelectorAll('.pill')];
  return (t) => {
    const o = bgOp(p, t, dur); bg.style.opacity = o; head.style.opacity = o;
    parts.forEach((l, i) => { const k = seg(t, .05 + i * .2, .35 + i * .2); l.style.opacity = k; l.style.transform = `translateY(${(1 - eo(k)) * 30}px)`; });
    olds.forEach((x) => { x.style.transform = `rotate(-6deg) scaleX(${eo(seg(t, .6, .85))})`; });
    pills.forEach((x) => { const k = seg(t, .85, 1.15); x.style.transform = `scale(${back(k)})`; x.style.opacity = Math.min(1, k * 3); });
    if (box) { const k = seg(t, 1.1, 1.3); box.style.transform = `rotate(-2deg) scale(${k < 1 ? 1.6 - .6 * eo(k) : 1})`; box.style.opacity = Math.min(1, k * 3) * o; }
    if (card) { const k = back(seg(t, .5, .85)); card.style.transform = `rotate(${4 * k}deg) translateY(${(1 - k) * 300}px)`; card.style.opacity = o * Math.min(1, seg(t, .5, .6) * 2); }
    if (lab) { lab.style.opacity = seg(t, 1.1, 1.3) * o; ar.forEach((a, i) => draw(a, seg(t, .9 + i * .2, 1.1 + i * .2))); ar[0].parentNode.style.opacity = o; }
  };
};
// pílula de dinheiro grande (edicao-reel)
T.er_money = (p, dur) => {
  const A = p.cam ? area(p) : {x: sx(p, 760, 80), w: 760};
  const bgEl = p.cam ? fullBg(p, 'background:#f4f4f2') : null;
  const pill = el('div', `left:${A.x + (A.w - 700) / 2}px;top:${p.y || 330}px;width:700px;padding:26px 0;border-radius:120px;background:#22C55E;color:#fff;text-align:center;font-family:MB;font-size:${p.size || 110}px;box-shadow:0 0 0 10px #fff,0 26px 50px rgba(0,0,0,.3)`, ''); pill.className = 'a';
  const sub = el('div', `left:${A.x}px;top:${(p.y || 330) + 230}px;width:${A.w}px;text-align:center;font-family:MB;font-size:54px;color:#fff;-webkit-text-stroke:10px #111;paint-order:stroke fill`, p.sub || ''); sub.className = 'a';
  return (t) => {
    const o = p.cam ? 1 : envOut(t, dur, .25); if (bgEl) bgEl.style.opacity = 1;
    const k = seg(t, 0, .3); pill.style.transform = `scale(${back(k)}) rotate(${-3 * k}deg)`; pill.style.opacity = Math.min(1, k * 3) * o;
    const v = (p.from || 0) + ((p.to || 0) - (p.from || 0)) * eo(seg(t, .2, Math.min(dur - .3, 1.4)));
    pill.textContent = (p.pre || 'R$ ') + Math.round(v).toLocaleString('pt-BR') + (p.suf || '');
    sub.style.opacity = seg(t, .5, .7) * o; sub.style.transform = `translateY(${(1 - eo(seg(t, .5, .8))) * 30}px)`;
  };
};

/* =================== ETIQUETA BRUTAL (neo-brutalista, legenda em etiquetas) =================== */
const EB = {cr: '#FBF4DE', ink: '#141210', y: '#FFD63A', r: '#EC583C', b: '#3C5AF0', li: '#C9AAF5', ok: '#58C478'};
T.eb_tags = (p, dur) => {
  const bg = fullBg(p, `background-color:${EB.cr};background-image:radial-gradient(rgba(20,18,16,.16) 1.6px,transparent 2px);background-size:34px 34px`, 30);
  const fr = camFrame(p, `border:6px solid ${EB.ink};box-shadow:12px 12px 0 ${EB.ink}`, 30);
  const A = area(p);
  const head = el('div', `left:${A.x + 20}px;top:70px;font-family:NEWS;font-size:40px;color:${EB.ink}`, `✳ ${p.top || 'Renda Secreta'} <i style="font-family:JB;font-style:normal;font-size:26px;color:#8a857c">/ aula</i>`); head.className = 'a';
  // bloco/selo principal
  const blk = el('div', `left:${A.x + 30}px;top:${p.by || 200}px;max-width:${A.w - 80}px;padding:22px 34px;background:${p.bc ? EB[p.bc] : EB.y};border:5px solid ${EB.ink};box-shadow:10px 10px 0 ${EB.ink};font-family:MB;font-size:${p.size || 76}px;line-height:1.02;color:${EB.ink};transform:rotate(-2deg)`, hl(p.text || '', `background:${EB.ink};color:${EB.cr};padding:0 12px`)); blk.className = 'a';
  let strike = null;
  if (p.strike) { strike = el('i', `position:absolute;left:-14px;right:-14px;top:48%;height:12px;background:${EB.r};transform:scaleX(0);transform-origin:0 50%`, '', blk); }
  let selo = null;
  if (p.selo) { selo = el('div', `left:${A.x + A.w - 330}px;top:${(p.by || 200) + 150}px;width:260px;height:260px;border-radius:50%;background:${EB.r};border:5px solid ${EB.ink};box-shadow:8px 8px 0 ${EB.ink};display:flex;align-items:center;justify-content:center;text-align:center;font-family:MB;font-size:44px;line-height:1;color:#fff`, p.selo); selo.className = 'a'; }
  // etiquetas palavra-a-palavra sincronizadas com a fala
  const W = (p.words || []).filter((w) => w.w.trim());
  const groups = []; let g = [];
  W.forEach((w) => { g.push(w); if (g.length >= 3 || /[.,!?]$/.test(w.w)) { groups.push(g); g = []; } }); if (g.length) groups.push(g);
  const tagWrap = el('div', `left:${A.x + 30}px;top:${p.ty || 700}px;width:${A.w - 60}px;display:flex;flex-wrap:wrap;gap:18px`); tagWrap.className = 'a';
  const HL = (p.hl || []).map((s) => s.toLowerCase());
  const tags = groups.map((gr) => gr.map((w, i) => { const clean = w.w.replace(/[.,!?;:]/g, ''); const key = HL.includes(clean.toLowerCase()); const e = el('span', `display:none;padding:10px 22px;background:${key ? EB.y : '#fff'};border:4px solid ${EB.ink};box-shadow:6px 6px 0 ${EB.ink};font-family:MB;font-size:58px;color:${EB.ink};border-radius:10px;transform:rotate(${(hsh(i, 4) - .5) * 5}deg)`, clean.toLowerCase(), tagWrap); e._s = w.s; return e; }));
  return (t) => {
    const o = 1; bg.style.opacity = o;
    head.style.opacity = seg(t, 0, .2);
    const k = seg(t, .05, .3); blk.style.transform = `rotate(-2deg) translateY(${(1 - back(k)) * -60}px)`; blk.style.opacity = Math.min(1, k * 3);
    if (strike) strike.style.transform = `scaleX(${eo(seg(t, .9, 1.15))})`;
    if (selo) { const ks = seg(t, 1.2, 1.45); selo.style.transform = `scale(${ks < 1 ? 2 - eo(ks) : 1}) rotate(${-12 + Math.sin(t * 2) * 2}deg)`; selo.style.opacity = Math.min(1, ks * 4); }
    let gi = -1; groups.forEach((gr, i) => { if (gr[0].s <= t) gi = i; });
    tags.forEach((gr, i) => gr.forEach((e) => { const on = i === gi && e._s <= t; e.style.display = i === gi ? 'inline-block' : 'none'; e.style.visibility = on ? 'visible' : 'hidden'; const kk = seg(t, e._s, e._s + .12); e.style.scale = on ? (kk < 1 ? 1.25 - .25 * kk : 1) : 1; }));
  };
};

/* =================== MOLDURA POP (moldura arredondada com contorno brilhante) =================== */
T.mp_frame = (p, dur) => {
  const pal = p.pal === 'lab' ? {bg: '#050505', acc: '#D7FF3A', paper: '#141414', ink: '#F2F2F2', sub: '#9a9a9a'} : {bg: '#141821', acc: p.acc || '#FF4FA3', paper: '#F7F3EA', ink: '#16161a', sub: '#7a7468'};
  const bg = fullBg(p, `background:radial-gradient(ellipse 60% 70% at ${p.cam === 'L' ? 25 : 75}% 50%,#2a3142 0%,${pal.bg} 70%)`, 44);
  const fr = camFrame(p, `border:8px solid ${pal.acc};box-shadow:0 0 30px ${pal.acc},0 0 80px ${pal.acc}66,inset 0 0 0 3px rgba(255,255,255,.4)`, 44);
  const A = area(p);
  const panel = el('div', `left:${A.x + 20}px;top:170px;width:${A.w - 60}px;padding:46px 54px;box-sizing:border-box;border-radius:34px;background-color:${pal.paper};background-image:radial-gradient(rgba(0,0,0,.08) 1.5px,transparent 2px);background-size:22px 22px;box-shadow:0 30px 70px rgba(0,0,0,.45)`); panel.className = 'a';
  el('div', `font-family:FIG6;font-size:28px;letter-spacing:.25em;color:${pal.sub};text-transform:uppercase`, p.top || '', panel);
  el('div', `margin-top:12px;font-family:FIG;font-size:${p.size || 78}px;line-height:1.02;color:${pal.ink}`, hl(p.title, `font-family:Georgia,serif;font-style:italic;font-weight:400;color:${pal.acc === '#D7FF3A' ? pal.acc : pal.acc}`), panel);
  const items = (p.items || []).map((s, i) => el('div', `margin-top:22px;display:flex;align-items:center;gap:18px;font-family:FIG6;font-size:40px;color:${pal.ink}`, `<span style="flex:none;width:52px;height:52px;border-radius:14px;background:${pal.acc};color:${pal.bg};font-family:FIG;display:inline-flex;align-items:center;justify-content:center;font-size:30px">${i + 1}</span>${s}`, panel));
  return (t) => {
    bg.style.opacity = 1;
    if (fr) { const kf = seg(t, 0, .3); fr.style.transform = `scale(${1.06 - .06 * eo(kf)})`; fr.style.opacity = kf; }
    const k = back(seg(t, .1, .5)); panel.style.transform = `translateY(${(1 - k) * 160}px) rotate(${(1 - k) * 4}deg)`; panel.style.opacity = Math.min(1, seg(t, .1, .2) * 2);
    items.forEach((it, i) => { const s0 = .6 + i * (p.gapT || .45), kk = seg(t, s0, s0 + .25); it.style.opacity = kk; it.style.transform = `translateX(${(1 - eo(kk)) * 40}px)`; });
  };
};

/* =================== MASCOTA PIXEL: passos numerados =================== */
T.px_steps = (p, dur) => {
  const bg = fullBg(p, `background:${PXC.bg}`); crt(bg);
  const img = el('img', `left:${p.cam ? (p.cam === 'L' ? 1500 : 60) : 1440}px;top:${1080 - 123 * 3.2}px;width:${123 * 3.2}px;height:${123 * 3.2}px;image-rendering:pixelated;filter:drop-shadow(8px 8px 0 rgba(0,0,0,.5))`); img.className = 'a'; img.src = 'img/' + (p.pose || 'senala_lado') + '.png';
  if (p.cam === 'L') img.style.transform = 'scaleX(-1)';
  const A = area(p); const x = A.x + 30, w = Math.min(A.w - (p.cam ? 420 : 520), 1100);
  const ttl = el('div', `left:${x}px;top:90px;width:${w}px;font-family:PX;font-size:40px;line-height:1.4;color:${PXC.y};text-shadow:4px 4px 0 ${PXC.ink}`, p.title || ''); ttl.className = 'a';
  const rows = p.items.map((s, i) => { const r = el('div', pxBox(`left:${x}px;top:${220 + i * 150}px;width:${w}px;padding:20px 24px;box-sizing:border-box;display:flex;gap:24px;align-items:center;font-family:PX;font-size:26px;line-height:1.5;color:${PXC.w}`), `<span style="flex:none;width:64px;height:64px;background:${[PXC.g, PXC.c, PXC.r, PXC.y][i % 4]};color:${PXC.ink};display:inline-flex;align-items:center;justify-content:center;font-size:30px">${i + 1}</span><span>${s}</span>`); r.className = 'a'; return r; });
  return (t) => {
    const ts = step(t, 12), o = bgOp(p, t, dur) > .5 ? 1 : 0; bg.style.opacity = o;
    const k = seg(ts, 0, .3); img.style.translate = `0 ${Math.round((1 - k) * 400 / 20) * 20}px`; img.style.opacity = o;
    ttl.style.opacity = (ts > .15 ? 1 : 0) * o;
    rows.forEach((r, i) => { const s0 = .35 + i * (p.gapT || .5); r.style.opacity = (ts >= s0 ? 1 : 0) * o; r.style.transform = `translateX(${ts < s0 + .1 ? -30 : 0}px)`; });
  };
};

/* =================== PIXELFX: efeitos em pixel art (explosão, brilho, raio) =================== */
T.pfx_burst = (p, dur) => {
  const S = 8, W = 160, H = 100; // grade de pixels grandes
  const cv = el('canvas', `left:${(p.cx || 960) - W * S / 2}px;top:${(p.cy || 400) - H * S / 2}px;width:${W * S}px;height:${H * S}px;image-rendering:pixelated`); cv.className = 'a'; cv.width = W; cv.height = H;
  const g = cv.getContext('2d');
  const kind = p.kind || 'boom';
  const PAL = kind === 'ice' ? ['#ffffff', '#bff4ff', '#6fd6ff', '#2e7dd6'] : kind === 'bolt' ? ['#ffffff', '#fff27a', '#ffd23f', '#a066ff'] : kind === 'coin' ? ['#fff7c2', '#ffd23f', '#f2a516', '#b86e00'] : ['#ffffff', '#ffe066', '#ff8a1f', '#e8432e', '#5a2a2a'];
  const parts = Array.from({length: 110}, (_, i) => ({a: hsh(i, 1) * 6.283, v: 20 + hsh(i, 2) * 45, s: 2 + Math.floor(hsh(i, 3) * 3)}));
  const lab = p.text ? el('div', `left:${(p.cx || 960) - 500}px;top:${(p.cy || 400) + (p.ly || 120)}px;width:1000px;text-align:center;font-family:PX;font-size:${p.size || 48}px;color:${PAL[1]};text-shadow:5px 5px 0 #000,-3px -3px 0 #000`, p.text) : null; if (lab) lab.className = 'a';
  return (t) => {
    const ts = step(t, 15), o = envOut(t, dur, .2) > .5 ? 1 : 0; g.clearRect(0, 0, W, H); cv.style.opacity = o;
    const cx = W / 2, cy = H / 2;
    if (kind === 'bolt') {
      for (let b = 0; b < 3; b++) { if (Math.floor(ts * 15) % 4 === b) continue; let x = cx + (b - 1) * 30, y = 0; g.fillStyle = PAL[b === 1 ? 0 : 1]; while (y < H) { const nx = x + (hsh(y + b * 99, Math.floor(ts * 10)) - .5) * 10; for (let k = 0; k < 6; k++) { g.fillRect(Math.round(x + (nx - x) * k / 6), y + k, 2, 2); } x = nx; y += 6; } }
    } else {
      const k = clamp(ts / .6), ring = k * 45;
      if (kind === 'boom' && ts < .5) { g.fillStyle = PAL[ts < .1 ? 0 : 1]; const r = 6 + ts * 40; for (let yy = -r; yy <= r; yy++) for (let xx = -r * 1.6; xx <= r * 1.6; xx++) if ((xx / 1.6) ** 2 + yy * yy < r * r * (1 - ts * 1.5)) g.fillRect(Math.round(cx + xx), Math.round(cy + yy), 1, 1); }
      parts.forEach((q, i) => { const d = q.v * eo(k) * 1.4; const x = cx + Math.cos(q.a) * d * 1.6, y = cy + Math.sin(q.a) * d + (kind === 'coin' ? ts * ts * 40 : 0); const ci = Math.min(PAL.length - 1, Math.floor(k * PAL.length + (i % 2))); if (k < 1 || i % 3) { g.fillStyle = PAL[ci]; g.fillRect(Math.round(x), Math.round(y), q.s, q.s); } });
      if (kind === 'ice' || kind === 'coin') { g.strokeStyle = PAL[1]; g.lineWidth = 1; g.beginPath(); g.ellipse(cx, cy, ring * 1.6, ring, 0, 0, 6.283); if (k < 1) g.stroke(); }
      if (kind === 'sparkle') for (let i = 0; i < 9; i++) { const ph = (ts * 3 + hsh(i, 6)) % 1; const x = Math.round(hsh(i, 7) * W), y = Math.round(hsh(i, 8) * H), r = Math.round(Math.sin(ph * 3.14) * 4); g.fillStyle = PAL[1]; g.fillRect(x - r, y, r * 2 + 1, 1); g.fillRect(x, y - r, 1, r * 2 + 1); }
    }
    if (lab) { lab.style.opacity = (ts > .15 ? 1 : 0) * o; lab.style.transform = `scale(${ts < .3 ? 1.3 : 1})`; }
  };
};

/* =================== BONEQUINHO PALITO (directing-stickman) =================== */
// boneco cabeça branca + membros pretos, cenário em cores chapadas, ação por pose
const smPose = (k, t) => {
  // retorna ângulos (graus) [bracoE, antebE, bracoD, antebD, pernaE, pernaD, inclinação, pulo]
  const s = Math.sin(t * 8);
  switch (k) {
    case 'walk': return [30 * s, 20, -30 * s, 20, -25 * s, 25 * s, 4, Math.abs(s) * 6];
    case 'cheer': return [-150 + s * 10, -20, 150 - s * 10, 20, -12, 12, 0, Math.abs(Math.sin(t * 7)) * 40];
    case 'point': return [20, 10, 95, 0, -10, 10, 4, 0];
    case 'think': return [15, 10, 40, 130, -8, 8, 3, 0];
    case 'sad': return [10, 5, -10, -5, -6, 6, 14, 0];
    case 'phone': return [20, 10, 60, 100, -8, 8, 6, 0];
    case 'run': return [55 * s, 70, -55 * s, 70, -50 * s, 50 * s, 14, Math.abs(s) * 14];
    default: return [12, 6, -12, -6, -8, 8, 0, 0];
  }
};
T.sm_scene = (p, dur) => {
  const bgc = p.color || '#8FD3FF';
  const bg = fullBg(p, `background:linear-gradient(180deg,${bgc} 0%,${bgc} 72%,${p.ground || '#7CC36B'} 72%,${p.ground || '#7CC36B'} 100%)`);
  const A = area(p);
  const s = svgBox(1920, 1080, 'left:0;top:0'); if (p.cam) { s.style.webkitMaskImage = bg.style.webkitMaskImage; }
  // nuvens / sol simples
  s.innerHTML = `<circle cx="${A.x + A.w - 160}" cy="150" r="70" fill="#FFE27A"/><ellipse cx="${A.x + 260}" cy="170" rx="110" ry="38" fill="#fff" opacity=".9"/><ellipse cx="${A.x + 330}" cy="145" rx="70" ry="36" fill="#fff" opacity=".9"/>`;
  // quadro / placa
  const bx = A.x + (p.fig === 'R' ? 40 : A.w * .42), bw = A.w * .55;
  const board = el('div', `left:${bx}px;top:${p.by || 230}px;width:${bw}px;padding:30px 36px;box-sizing:border-box;background:#fff;border:6px solid #1b1b1b;border-radius:18px;font-family:CAV;font-size:${p.size || 66}px;line-height:1.08;color:#1b1b1b;text-align:center;box-shadow:8px 10px 0 rgba(0,0,0,.2)`, hl(p.text || '', 'color:#e8432e')); board.className = 'a';
  // boneco
  const fx = p.fig === 'R' ? A.x + A.w - 300 : A.x + 230, fy = 720;
  const ns = 'http://www.w3.org/2000/svg';
  const mk = (tag, at) => { const e = document.createElementNS(ns, tag); for (const k in at) e.setAttribute(k, at[k]); s.appendChild(e); return e; };
  const L = {}; ['ua1', 'la1', 'ua2', 'la2', 'th1', 'th2', 'body'].forEach((k) => L[k] = mk('path', {stroke: '#1b1b1b', 'stroke-width': 16, 'stroke-linecap': 'round', fill: 'none'}));
  const head = mk('circle', {r: 66, fill: '#fff', stroke: '#1b1b1b', 'stroke-width': 9});
  const eye1 = mk('circle', {r: 7, fill: '#1b1b1b'}), eye2 = mk('circle', {r: 7, fill: '#1b1b1b'}), mouth = mk('path', {stroke: '#1b1b1b', 'stroke-width': 6, fill: 'none', 'stroke-linecap': 'round'});
  const prop = p.prop ? el('div', `left:0;top:0;font-size:90px`, p.prop) : null; if (prop) prop.className = 'a';
  const rad = (d) => d * Math.PI / 180;
  return (t) => {
    const o = bgOp(p, t, dur); bg.style.opacity = o; s.style.opacity = o;
    const ent = eo(seg(t, 0, .5)); const pose = smPose(p.pose || 'idle', t);
    const mir = p.fig === 'R' ? -1 : 1; const [a1, b1, a2, b2, l1, l2, lean, jump] = pose.map((v, i) => i < 7 ? v * mir : v);
    const X = fx + (1 - ent) * (p.fig === 'R' ? 700 : -700), Y = fy - jump;
    const hip = [X, Y], neck = [X + Math.sin(rad(lean)) * 170, Y - Math.cos(rad(lean)) * 220];
    L.body.setAttribute('d', `M${hip[0]} ${hip[1]} L${neck[0]} ${neck[1]}`);
    const limb = (pa, base, ang1, ang2, len) => { const e1 = [base[0] + Math.sin(rad(ang1)) * len, base[1] + Math.cos(rad(ang1)) * len]; const e2 = [e1[0] + Math.sin(rad(ang1 + ang2)) * len, e1[1] + Math.cos(rad(ang1 + ang2)) * len]; return [e1, e2]; };
    const sh = [neck[0] + Math.sin(rad(lean)) * -30, neck[1] + 30];
    const [e1, h1] = limb(0, sh, a1, b1, 110), [e2, h2] = limb(0, sh, a2, b2, 110);
    L.ua1.setAttribute('d', `M${sh[0]} ${sh[1]} L${e1[0]} ${e1[1]} L${h1[0]} ${h1[1]}`); L.ua2.setAttribute('d', `M${sh[0]} ${sh[1]} L${e2[0]} ${e2[1]} L${h2[0]} ${h2[1]}`);
    const k1 = [hip[0] + Math.sin(rad(l1)) * 125, hip[1] + Math.cos(rad(l1)) * 125], k2 = [hip[0] + Math.sin(rad(l2)) * 125, hip[1] + Math.cos(rad(l2)) * 125];
    L.th1.setAttribute('d', `M${hip[0]} ${hip[1]} L${k1[0]} ${k1[1]} L${k1[0] + Math.sin(rad(l1 * .3)) * 120} ${k1[1] + 120}`); L.th2.setAttribute('d', `M${hip[0]} ${hip[1]} L${k2[0]} ${k2[1]} L${k2[0] + Math.sin(rad(l2 * .3)) * 120} ${k2[1] + 120}`);
    L.la1.setAttribute('d', ''); L.la2.setAttribute('d', '');
    const hc = [neck[0] + Math.sin(rad(lean)) * 55, neck[1] - 70]; head.setAttribute('cx', hc[0]); head.setAttribute('cy', hc[1]);
    const dir = p.fig === 'R' ? -1 : 1; const bl = (t % 2.4) > 2.3 ? 1 : 7;
    eye1.setAttribute('cx', hc[0] + 10 * dir - 14); eye1.setAttribute('cy', hc[1] - 6); eye1.setAttribute('r', bl); eye2.setAttribute('cx', hc[0] + 10 * dir + 14); eye2.setAttribute('cy', hc[1] - 6); eye2.setAttribute('r', bl);
    const sad = p.pose === 'sad';
    mouth.setAttribute('d', sad ? `M${hc[0] - 16} ${hc[1] + 26} Q ${hc[0]} ${hc[1] + 12} ${hc[0] + 16} ${hc[1] + 26}` : `M${hc[0] - 18} ${hc[1] + 16} Q ${hc[0]} ${hc[1] + 34} ${hc[0] + 18} ${hc[1] + 16}`);
    if (prop) { prop.style.transform = `translate(${h2[0] - 45}px,${h2[1] - 70}px)`; prop.style.opacity = o; }
    const kb = seg(t, .35, .7); board.style.transform = `scale(${back(kb)}) rotate(${-1.5}deg)`; board.style.opacity = Math.min(1, kb * 3) * o;
  };
};


/* =================== YOUTUBE (Brecha Viral): capas reais, contadores, comparações =================== */
const YT = {bg: '#0F0F0F', card: '#1F1F1F', w: '#F1F1F1', g: '#AAAAAA', red: '#FF3B30', grn: '#2BD96B', yel: '#FFD23F'};
const ytBg = () => { const b = el('div', `left:0;top:0;width:1920px;height:1080px;background:radial-gradient(ellipse 75% 65% at 50% 42%,#262626 0%,${YT.bg} 70%)`); b.className = 'a';
  const g = el('div', `left:0;top:0;width:1920px;height:1080px;opacity:.07;background-image:linear-gradient(#fff 1px,transparent 1px),linear-gradient(90deg,#fff 1px,transparent 1px);background-size:60px 60px`); g.className = 'a'; return [b, g]; };
const fmtN = (n) => Math.round(n).toLocaleString('pt-BR');
const fmtV = (n) => n >= 1e6 ? (n / 1e6).toFixed(1).replace('.', ',') + ' mi' : n >= 1000 ? Math.round(n / 1000) + ' mil' : String(Math.round(n));
const ytChip = (txt, x, y, col) => { const c = el('div', `left:${x}px;top:${y}px;padding:10px 22px;border-radius:12px;background:${col};color:${col === YT.yel ? '#111' : '#fff'};font-family:ON8;font-size:30px;letter-spacing:.05em;white-space:nowrap`, txt); c.className = 'a'; return c; };
const ytThumb = (src, x, y, w, parent) => { const h = Math.round(w * 9 / 16);
  const box = el('div', `left:${x}px;top:${y}px;width:${w}px;height:${h}px;border-radius:${Math.round(w / 40)}px;overflow:hidden;box-shadow:0 24px 60px rgba(0,0,0,.6);background:#000`, null, parent); box.className = 'a';
  const im = el('img', `width:100%;height:100%;object-fit:cover;display:block`, null, box); im.src = 'img/capas/' + src; return box; };

// 1 capa grande + título + canal + contador de visualizações
T.yt_card = (p, dur) => {
  ytBg();
  const W = p.w || 1100, x = (1920 - W) / 2, y = p.y || 90;
  const th = ytThumb(p.img, x, y, W);
  const H = Math.round(W * 9 / 16);
  const tt = el('div', `left:${x}px;top:${y + H + 30}px;width:${W}px;font-family:ON8;font-size:40px;line-height:1.2;color:${YT.w}`, p.title || ''); tt.className = 'a';
  const meta = el('div', `left:${x}px;top:${y + H + 86 + (p.title && p.title.length > 52 ? 46 : 0)}px;font-family:ON;font-size:34px;color:${YT.g};white-space:nowrap`, ''); meta.className = 'a';
  const chip = p.tag ? ytChip(p.tag, x + 26, y + 26, p.tagc === 'red' ? YT.red : p.tagc === 'yel' ? YT.yel : YT.grn) : null;
  return (t) => {
    const o = envOut(t, dur, .25), k = eo(seg(t, 0, .45));
    th.style.opacity = Math.min(1, t * 6) * o; th.style.transform = `translateY(${(1 - k) * 60}px) scale(${1.0 + .035 * seg(t, 0, dur)})`;
    tt.style.opacity = seg(t, .25, .45) * o; meta.style.opacity = seg(t, .35, .55) * o;
    const v = (p.views || 0) * eo(seg(t, .4, Math.min(2.2, dur * .6)));
    meta.innerHTML = `${p.ch || ''} · <b style="color:${p.tagc === 'red' ? YT.red : YT.yel};font-family:ON8;font-size:44px">${fmtN(v)}</b> visualizações`;
    if (chip) { chip.style.opacity = seg(t, .5, .65) * o; chip.style.transform = `scale(${back(seg(t, .5, .8))}) rotate(-3deg)`; }
  };
};

// original x cópia lado a lado
T.yt_vs = (p, dur) => {
  ytBg();
  const top = el('div', `left:0;top:60px;width:1920px;text-align:center;font-family:ITX;font-size:64px;color:${YT.w}`, hl(p.top || 'MESMO TÍTULO', `color:${YT.yel}`)); top.className = 'a';
  const mk = (it, x, col, tag, t0) => { const th = ytThumb(it.img, x, 220, 780);
    const tt = el('div', `left:${x}px;top:${220 + 439 + 24}px;width:780px;font-family:ON8;font-size:30px;line-height:1.2;color:${YT.w}`, it.title || ''); tt.className = 'a';
    const ch = el('div', `left:${x}px;top:${220 + 439 + 112}px;font-family:ON;font-size:28px;color:${YT.g}`, it.ch || ''); ch.className = 'a';
    const num = el('div', `left:${x}px;top:${220 + 439 + 150}px;width:780px;font-family:ITX;font-size:96px;line-height:1;color:${col}`, ''); num.className = 'a';
    const chip = ytChip(tag, x + 24, 244, col); return {th, tt, ch, num, chip, it, t0}; };
  const A = mk(p.a, 130, YT.grn, p.a.tag || 'ORIGINAL', 0), B = mk(p.b, 1010, YT.red, p.b.tag || 'CÓPIA', p.tb || 1.2);
  const vs = el('div', `left:900px;top:380px;width:120px;height:120px;border-radius:50%;background:${YT.yel};color:#111;font-family:MB;font-size:52px;display:flex;align-items:center;justify-content:center;box-shadow:0 0 40px rgba(255,210,63,.5)`, 'VS'); vs.className = 'a';
  return (t) => {
    const o = envOut(t, dur, .25); top.style.opacity = seg(t, 0, .2) * o;
    [A, B].forEach((S) => { const k = seg(t, S.t0, S.t0 + .45), kk = eo(k);
      S.th.style.opacity = Math.min(1, k * 4) * o; S.th.style.transform = `translateY(${(1 - kk) * 70}px)`;
      [S.tt, S.ch].forEach((e) => { e.style.opacity = seg(t, S.t0 + .2, S.t0 + .4) * o; });
      S.chip.style.opacity = seg(t, S.t0 + .3, S.t0 + .45) * o; S.chip.style.transform = `scale(${back(seg(t, S.t0 + .3, S.t0 + .6))}) rotate(-3deg)`;
      const v = S.it.views * eo(seg(t, S.t0 + .3, S.t0 + 1.4)); S.num.textContent = fmtN(v); S.num.style.opacity = seg(t, S.t0 + .3, S.t0 + .45) * o; });
    const kv = seg(t, (p.tb || 1.2) + .3, (p.tb || 1.2) + .6); vs.style.opacity = kv * o; vs.style.transform = `scale(${back(kv)}) rotate(${(1 - kv) * -90}deg)`;
  };
};

// grade de capas com contador embaixo de cada uma
T.yt_grid = (p, dur) => {
  ytBg();
  const top = el('div', `left:0;top:46px;width:1920px;text-align:center;font-family:ITX;font-size:58px;color:${YT.w}`, hl(p.top || '', `color:${YT.yel}`)); top.className = 'a';
  const cols = p.cols || 4, W = 400, gx = 40, x0 = (1920 - cols * W - (cols - 1) * gx) / 2;
  const cells = p.items.map((it, i) => { const x = x0 + (i % cols) * (W + gx), y = 170 + Math.floor(i / cols) * 430;
    const th = ytThumb(it.img, x, y, W); const col = it.ok ? YT.grn : YT.red;
    const n = el('div', `left:${x}px;top:${y + 240}px;width:${W}px;font-family:ITX;font-size:60px;color:${col}`, ''); n.className = 'a';
    const c = el('div', `left:${x}px;top:${y + 318}px;width:${W}px;font-family:ON;font-size:24px;color:${YT.g};white-space:nowrap;overflow:hidden;text-overflow:ellipsis`, it.ch || ''); c.className = 'a';
    return {th, n, c, it, t0: .25 + i * (p.step || .28)}; });
  return (t) => { const o = envOut(t, dur, .25); top.style.opacity = seg(t, 0, .2) * o;
    cells.forEach((S) => { const k = seg(t, S.t0, S.t0 + .35); S.th.style.opacity = Math.min(1, k * 4) * o; S.th.style.transform = `scale(${.6 + .4 * back(k)})`;
      S.n.style.opacity = seg(t, S.t0 + .2, S.t0 + .3) * o; S.c.style.opacity = S.n.style.opacity; S.n.textContent = fmtN(S.it.views * eo(seg(t, S.t0 + .2, S.t0 + .9))); }); };
};

// título em inglês digitado + tradução embaixo
T.yt_title = (p, dur) => {
  ytBg();
  const lab = el('div', `left:160px;top:150px;font-family:JB;font-size:30px;letter-spacing:.18em;color:${YT.g}`, p.top || 'TÍTULO ORIGINAL (INGLÊS)'); lab.className = 'a';
  const bar = el('div', `left:160px;top:210px;width:1600px;min-height:120px;padding:34px 44px;box-sizing:border-box;border-radius:70px;background:#121212;border:3px solid #303030;font-family:ON8;font-size:58px;line-height:1.2;color:${YT.w}`, ''); bar.className = 'a';
  const lab2 = el('div', `left:160px;top:560px;font-family:JB;font-size:30px;letter-spacing:.18em;color:${YT.yel}`, 'TRADUZINDO'); lab2.className = 'a';
  const pt = el('div', `left:160px;top:620px;width:1600px;font-family:ITX;font-size:76px;line-height:1.08;color:${YT.yel}`, ''); pt.className = 'a';
  const pw = p.pt.split(' ').map((w) => { const s = el('span', `display:inline-block;margin-right:.24em`, w, pt); return s; });
  return (t) => { const o = envOut(t, dur, .25);
    lab.style.opacity = seg(t, 0, .2) * o; bar.style.opacity = seg(t, 0, .2) * o;
    const ty = p.ten || Math.max(1, (p.tpt || dur * .45) - .5);
    bar.innerHTML = typed(p.en, seg(t, .2, ty)) + (seg(t, .2, ty) < 1 && Math.floor(t * 3) % 2 ? '|' : '');
    const t2 = p.tpt || dur * .45; lab2.style.opacity = seg(t, t2 - .2, t2) * o;
    const per = Math.min(.3, (dur - t2 - .6) / pw.length);
    pw.forEach((s, i) => { const k = seg(t, t2 + i * per, t2 + i * per + .3); s.style.opacity = k * o; s.style.transform = `translateY(${(1 - eo(k)) * 30}px)`; s.style.filter = `blur(${(1 - k) * 10}px)`; }); };
};

// Ctrl+C / Ctrl+V com a capa se multiplicando
T.yt_keys = (p, dur) => {
  ytBg();
  const key = (txt, x) => { const k = el('div', `left:${x}px;top:700px;width:${txt.length > 1 ? 300 : 200}px;height:200px;border-radius:30px;background:linear-gradient(#3a3a3a,#232323);box-shadow:0 14px 0 #111,0 20px 40px rgba(0,0,0,.6);color:#fff;font-family:MB;font-size:${txt.length > 1 ? 72 : 110}px;display:flex;align-items:center;justify-content:center`, txt); k.className = 'a'; return k; };
  const kc = key('CTRL', 560), kl = key('C', 1000), plus = el('div', `left:900px;top:740px;font-family:MB;font-size:100px;color:${YT.g}`, '+'); plus.className = 'a';
  const N = 7, thumbs = Array.from({length: N}, (_, i) => ytThumb(p.img, 560 + (i - 3) * 90, 120 + Math.abs(i - 3) * 14, 760));
  thumbs.forEach((b, i) => { b.style.zIndex = 10 - Math.abs(i - 3); });
  const tv = p.tv || dur * .45;
  return (t) => { const o = envOut(t, dur, .25);
    const pressC = seg(t, .3, .45) - seg(t, .55, .7), pressV = seg(t, tv, tv + .15) - seg(t, tv + .25, tv + .4);
    const pr = Math.max(pressC, pressV);
    [kc, kl, plus].forEach((e) => { e.style.opacity = Math.min(1, t * 5) * o; });
    kc.style.transform = kl.style.transform = `translateY(${pr * 14}px)`;
    kl.textContent = t < tv ? 'C' : 'V'; kl.style.color = t < tv ? '#fff' : YT.red;
    thumbs.forEach((b, i) => { const j = Math.abs(i - 3); const k = j === 0 ? seg(t, 0, .3) : seg(t, tv + .1 + j * .12, tv + .35 + j * .12);
      const side = i < 3 ? -1 : 1; b.style.opacity = Math.min(1, k * 3) * o * (j === 0 ? 1 : .92);
      b.style.transform = `translateX(${j === 0 ? 0 : side * (1 - eo(k)) * -90 * j}px) rotate(${side * j * 3 * eo(k)}deg) scale(${1 - j * .06})`;
      b.style.filter = j ? `brightness(${1 - j * .12})` : ''; }); };
};

// texto grande no estilo YouTube escuro: palavra por palavra, *destaque* amarelo (ou vermelho)
T.yt_text = (p, dur) => {
  ytBg();
  const hc = p.hlc === 'red' ? YT.red : p.hlc === 'grn' ? YT.grn : YT.yel;
  const chip = p.chip ? ytChip(p.chip, 0, 0, YT.yel) : null;
  const box = el('div', `left:160px;top:0;width:1600px;text-align:center;font-family:ITX;font-size:${p.size || 120}px;line-height:1.05;color:${YT.w};letter-spacing:-.02em`); box.className = 'a';
  const ws = p.text.split(' ').map((w) => { const h = w.startsWith('*'); return el('span', `display:inline-block;margin:0 .13em;${h ? `color:${hc}` : ''}`, w.replace(/\*/g, ''), box); });
  const sub = p.sub ? el('div', `left:160px;top:0;width:1600px;text-align:center;font-family:ON;font-size:46px;color:${YT.g}`, p.sub) : null; if (sub) sub.className = 'a';
  const H = box.offsetHeight, y0 = (1080 - H - (sub ? 90 : 0) - (chip ? 90 : 0)) / 2 + (chip ? 90 : 0);
  box.style.top = y0 + 'px'; if (sub) sub.style.top = (y0 + H + 34) + 'px';
  if (chip) { chip.style.left = (960 - chip.offsetWidth / 2) + 'px'; chip.style.top = (y0 - 100) + 'px'; }
  const per = Math.min(.12, (dur * .3) / ws.length);
  return (t) => { const o = envOut(t, dur, .25);
    if (chip) { chip.style.opacity = seg(t, 0, .15) * o; chip.style.transform = `scale(${back(seg(t, 0, .3))}) rotate(-2deg)`; }
    ws.forEach((s, i) => { const k = seg(t, .05 + i * per, .05 + i * per + .22); s.style.opacity = k * o; s.style.transform = `translateY(${(1 - eo(k)) * 40}px) scale(${.9 + .1 * back(k)})`; s.style.filter = `blur(${(1 - k) * 12}px)`; });
    box.style.scale = 1 + .03 * seg(t, 0, dur);
    if (sub) sub.style.opacity = seg(t, .2 + ws.length * per, .4 + ws.length * per) * o; };
};
// chip + título + itens (→ amarelo)
T.yt_list = (p, dur) => {
  ytBg();
  const chip = ytChip(p.chip || '', 260, 250, YT.yel);
  const tt = el('div', `left:260px;top:340px;width:1400px;font-family:ITX;font-size:110px;line-height:1.05;color:${YT.w}`, hl(p.title, `color:${YT.yel}`)); tt.className = 'a';
  const its = (p.items || []).map((it, i) => { const e = el('div', `left:260px;top:${520 + i * 92}px;font-family:ON8;font-size:58px;color:${YT.w};white-space:nowrap`, `<span style="color:${YT.yel}">→</span> ${it}`); e.className = 'a'; return e; });
  const st = p.step || Math.min(.5, (dur - 1.2) / Math.max(1, its.length));
  return (t) => { const o = envOut(t, dur, .25);
    chip.style.opacity = seg(t, 0, .15) * o; chip.style.transform = `scale(${back(seg(t, 0, .3))}) rotate(-2deg)`;
    const k = seg(t, .1, .45); tt.style.opacity = k * o; tt.style.transform = `translateY(${(1 - eo(k)) * 40}px)`;
    its.forEach((e, i) => { const s0 = .5 + i * st, kk = seg(t, s0, s0 + .3); e.style.opacity = kk * o; e.style.transform = `translateX(${(1 - eo(kk)) * 60}px)`; }); };
};

// barras horizontais comparando visualizações (verde = deu certo, vermelho = cópia)
T.yt_bars = (p, dur) => {
  ytBg();
  const chip = p.chip ? ytChip(p.chip, 200, 110, YT.yel) : null;
  const tt = el('div', `left:200px;top:${chip ? 190 : 130}px;width:1520px;font-family:ITX;font-size:72px;color:${YT.w}`, hl(p.title || '', `color:${YT.yel}`)); tt.className = 'a';
  const mx = Math.max(...p.rows.map((r) => r.v)), n = p.rows.length, rh = Math.min(110, 640 / n), y0 = (chip ? 330 : 270);
  const rows = p.rows.map((r, i) => { const y = y0 + i * rh; const col = r.ok ? YT.grn : r.c === 'yel' ? YT.yel : YT.red;
    const lab = el('div', `left:200px;top:${y}px;width:520px;font-family:ON8;font-size:${Math.min(38, rh * .42)}px;color:${YT.w};white-space:nowrap;overflow:hidden;text-overflow:ellipsis;line-height:${rh * .8}px`, r.l); lab.className = 'a';
    const bar = el('div', `left:740px;top:${y + rh * .12}px;height:${rh * .56}px;width:0;border-radius:10px;background:${col}`); bar.className = 'a';
    const num = el('div', `left:760px;top:${y}px;font-family:ITX;font-size:${Math.min(52, rh * .55)}px;color:${col};line-height:${rh * .8}px;white-space:nowrap`, ''); num.className = 'a';
    return {lab, bar, num, r, t0: .35 + i * (p.step || .22)}; });
  return (t) => { const o = envOut(t, dur, .25);
    if (chip) { chip.style.opacity = seg(t, 0, .15) * o; chip.style.transform = `scale(${back(seg(t, 0, .3))}) rotate(-2deg)`; }
    tt.style.opacity = seg(t, .05, .3) * o;
    rows.forEach((S) => { const k = eo(seg(t, S.t0, S.t0 + .9)); const w = Math.max(6, 860 * Math.pow(S.r.v / mx, p.log ? .35 : 1) * k);
      S.lab.style.opacity = seg(t, S.t0, S.t0 + .2) * o; S.bar.style.opacity = o; S.bar.style.width = w + 'px';
      S.num.style.left = (760 + w) + 'px'; S.num.style.opacity = seg(t, S.t0 + .1, S.t0 + .3) * o; S.num.textContent = fmtN(S.r.v * k); }); };
};
// etapas em caixas lado a lado (ex.: GARIMPAR → DISSECAR → ...), ativa uma por uma
T.yt_steps = (p, dur) => {
  ytBg();
  const chip = p.chip ? ytChip(p.chip, 0, 200, YT.yel) : null; if (chip) chip.style.left = (960 - chip.offsetWidth / 2) + 'px';
  const n = p.steps.length, gap = 30, w = Math.min(330, (1720 - gap * (n - 1)) / n), x0 = (1920 - n * w - (n - 1) * gap) / 2;
  const bx = p.steps.map((s, i) => { const b = el('div', `left:${x0 + i * (w + gap)}px;top:380px;width:${w}px;height:300px;box-sizing:border-box;border-radius:26px;background:${YT.card};border:3px solid #333;padding:30px 22px;text-align:center`); b.className = 'a';
    el('div', `font-family:ITX;font-size:84px;color:${YT.yel};line-height:1`, String(i + 1).padStart(2, '0'), b);
    el('div', `margin-top:22px;font-family:ITX;font-size:${Math.min(46, w / 6.5)}px;color:${YT.w};letter-spacing:.02em`, s.t, b);
    el('div', `margin-top:14px;font-family:ON;font-size:${Math.min(30, w / 10)}px;color:${YT.g};line-height:1.2`, s.s || '', b); return b; });
  const ar = p.steps.slice(1).map((_, i) => { const a = el('div', `left:${x0 + (i + 1) * (w + gap) - gap / 2 - 18}px;top:505px;font-family:MB;font-size:44px;color:${YT.yel}`, '›'); a.className = 'a'; return a; });
  const st = p.step || Math.min(.9, (dur - 1) / n);
  return (t) => { const o = envOut(t, dur, .25); if (chip) chip.style.opacity = seg(t, 0, .2) * o;
    bx.forEach((b, i) => { const s0 = .2 + i * st, k = seg(t, s0, s0 + .3); b.style.opacity = Math.min(1, k * 3) * o; b.style.transform = `translateY(${(1 - eo(k)) * 50}px)`;
      const act = t >= s0 && (i === n - 1 || t < s0 + st); b.style.borderColor = act ? YT.yel : '#333'; b.style.boxShadow = act ? '0 0 40px rgba(255,210,63,.35)' : 'none'; });
    ar.forEach((a, i) => { a.style.opacity = seg(t, .3 + (i + 1) * st, .45 + (i + 1) * st) * o; }); };
};

/* =================== base =================== */
const BGS = {
  paper: `${'background-color:#f6efdc;background-image:radial-gradient(rgba(120,90,50,.12) 1px,transparent 1.4px),radial-gradient(rgba(120,90,50,.08) 1px,transparent 1.2px);background-size:9px 9px,13px 13px'}`,
  graphite: 'background:radial-gradient(ellipse 80% 70% at 50% 45%,#2A2F38 0%,#0C0E12 75%)',
  night: 'background:linear-gradient(160deg,#1b2350 0%,#0f1633 55%,#2a1230 100%)',
  navy: 'background:radial-gradient(ellipse 70% 60% at 50% 45%,#2a1550 0%,#12142A 60%,#07081a 100%)',
  pixel: 'background:#1a1033',
  stage: 'background:radial-gradient(ellipse 60% 55% at 50% 42%,#2b3a2a 0%,#10140f 60%,#060806 100%)',
  ink: 'background:radial-gradient(ellipse 70% 60% at 50% 40%,#1a2030 0%,#0A0C11 70%)',
};
let BGEL = null;
if (IT.p && IT.p.bg) { BGEL = el('div', 'position:absolute;left:0;top:0;width:1920px;height:1080px;' + BGS[IT.p.bg]); if (IT.p.bg === 'pixel') crt(BGEL);
  if (IT.p.bg === 'paper') { const s = svgBox(1920, 1080, 'left:0;top:0', BGEL); s.classList.add('boil'); for (let i = 0; i < 14; i++) { const x = (i * 263) % 1800 + 60, y = (i * 389) % 980 + 50; const q = document.createElementNS(svgNS, 'path'); q.setAttribute('d', `M${x} ${y} l18 0 M${x + 9} ${y - 9} l0 18`); q.setAttribute('stroke', ['#e8432e', '#f2a516', '#2f6fd6'][i % 3]); q.setAttribute('stroke-width', 5); q.setAttribute('stroke-linecap', 'round'); s.appendChild(q); } }
  ST.insertBefore(BGEL, ST.firstChild); }
const UPD0 = T[IT.type](IT.p || {}, IT.dur);
const UPD = (t, f) => { if (BGEL) BGEL.style.opacity = Math.min(1, t / 0.18) * (1 - seg(t, IT.dur - .2, IT.dur)); UPD0(t, f); };
window.seek = (t) => {
  const f = Math.round(t * FPS);
  const tb = document.getElementById('turb'); if (tb) tb.setAttribute('seed', 1 + Math.floor(f / 2) % 4);
  UPD(t, f);
};
window.ready = (async () => { await document.fonts.ready; await Promise.all([...document.images].map((i) => i.complete ? 1 : new Promise((r) => { i.onload = i.onerror = r; }))); window.seek(0); return true; })();
