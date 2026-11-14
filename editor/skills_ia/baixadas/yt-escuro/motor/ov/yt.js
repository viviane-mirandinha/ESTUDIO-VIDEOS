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
