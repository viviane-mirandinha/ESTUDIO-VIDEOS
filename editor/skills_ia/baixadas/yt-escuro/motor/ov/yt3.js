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
