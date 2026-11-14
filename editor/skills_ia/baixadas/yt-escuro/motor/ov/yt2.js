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
  const per = Math.min(.16, (dur * .5) / ws.length);
  return (t) => { const o = envOut(t, dur, .25);
    if (chip) { chip.style.opacity = seg(t, 0, .15) * o; chip.style.transform = `scale(${back(seg(t, 0, .3))}) rotate(-2deg)`; }
    ws.forEach((s, i) => { const k = seg(t, .1 + i * per, .1 + i * per + .3); s.style.opacity = k * o; s.style.transform = `translateY(${(1 - eo(k)) * 40}px) scale(${.9 + .1 * back(k)})`; s.style.filter = `blur(${(1 - k) * 12}px)`; });
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
