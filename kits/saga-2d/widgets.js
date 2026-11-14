/* ============================================================================================
   KIT saga-2d — WIDGETS ANIMADOS (peças prontas que mostram o DADO da frase se mexendo)
   Uso: embutido no template.html pelo `embutir.py`. Não precisa desenhar SVG novo: escolha a peça,
   passe os números e o segundo (t0) em que a palavra é falada.
   Contrato de cada peça:  W.nome(id, cfg, e)  →  { svg, html, anim() }
     id  = prefixo único (use I("w1"))      cfg.t0 = segundo em que COMEÇA (tempo absoluto do vídeo)
     cfg.t1 = segundo em que TERMINA o movimento (opcional; padrão = fim da cena)
   Depende do template: tl (GSAP), C (cores), pop(), selo(), rafa(), idleRafa().
   ============================================================================================ */
const W = {};
(function(){
  const K = c => (typeof C !== "undefined" && C[c]) || c;
  const Q = id => "#" + id;
  const ink = () => W._dark ? K("cream") : K("lead");   // cor de texto que contrasta com o fundo da cena
  const num = (v, d) => (v == null || isNaN(+v)) ? d : +v;
  const appear = (sel, t, dy) => tl.fromTo(sel, {opacity:0, y: dy == null ? 36 : dy}, {opacity:1, y:0, duration:0.4, ease:"power2.out", immediateRender:true}, t);
  const count = (sel, de, ate, s, d, fmt) => { const o = {v:de}, f = fmt || (v => Math.round(v));
    tl.fromTo(o, {v:de}, {v:ate, duration:Math.max(0.1, d), ease:"none", immediateRender:false,
      onUpdate(){ const n = document.querySelector(sel); if (n) n.textContent = f(o.v); }}, s); };
  const txt = (id, x, y, html, size, color, extra) =>
    `<div class="w" style="left:${x}px;top:${y}px"><div id="${id}" style="font-family:Oswald;font-size:${size}px;color:${color};line-height:1;${extra || ""}">${html}</div></div>`;
  const span = (c, e) => Math.max(0.6, (c.t1 != null ? c.t1 : e) - c.t0);
  const arc = (r, a0, a1, col, sw) => { const p = a => [r*Math.cos(a*Math.PI/180), r*Math.sin(a*Math.PI/180)], A = p(a0), B = p(a1);
    return `<path d="M${A[0]},${A[1]} A${r},${r} 0 0 1 ${B[0]},${B[1]}" fill="none" stroke="${col}" stroke-width="${sw}"/>`; };

  /* ---------- 1. contador: número subindo (de → até) ---------- */
  W.contador = (id, c, e) => ({
    svg: "",
    html: txt(id, num(c.x, 540), num(c.y, 900), `${c.prefixo || ""}${num(c.de, 0)}${c.sufixo || ""}`, num(c.size, 220), K(c.cor || ink()),
      W._dark ? "text-shadow:0 8px 0 rgba(0,0,0,.28);" : ""),
    anim(){ pop(Q(id), c.t0); count(Q(id), num(c.de, 0), num(c.ate, 10), c.t0, span(c, e), v => `${c.prefixo || ""}${Math.round(v)}${c.sufixo || ""}`); }
  });

  /* ---------- 2. garrafa/galão enchendo até N litros ---------- */
  W.garrafa = (id, c, e) => { const w = num(c.w, 190), h = num(c.h, 460), L = num(c.litros, 4), H = h - 16;
    return {
      svg: `<g transform="translate(${c.x},${c.y})"><g id="${id}">
        <rect x="${-w/2}" y="${-h}" width="${w}" height="${h}" rx="48" fill="#CFE6EE" opacity=".9"/>
        <rect id="${id}_a" x="${-w/2+8}" y="-8" width="${w-16}" height="0" rx="40" fill="${K(c.cor || "#4F9CC4")}"/>
        ${[0.25, 0.5, 0.75].map(k => `<rect x="${w/2-44}" y="${-8-H*k}" width="36" height="6" rx="3" fill="rgba(43,47,46,.45)"/>`).join("")}
        <rect x="${-w*0.2}" y="${-h-64}" width="${w*0.4}" height="68" rx="14" fill="${K("red")}"/></g></g>`,
      html: txt(id + "_n", num(c.x, 540), num(c.y, 1400) - h/2, `0 L`, num(c.size, 84), "#fff", "text-shadow:0 6px 0 rgba(0,0,0,.35);"),
      anim(){ const d = span(c, e); appear(Q(id), c.t0);
        tl.fromTo(Q(id + "_a"), {attr:{height:0, y:-8}}, {attr:{height:H, y:-(H + 8)}, duration:d, ease:"power1.inOut", immediateRender:false}, c.t0 + 0.3);
        pop(Q(id + "_n"), c.t0 + 0.3); count(Q(id + "_n"), 0, L, c.t0 + 0.3, d, v => `${Math.round(v*10)/10 % 1 ? (Math.round(v*10)/10).toFixed(1) : Math.round(v)} L`); }
    }; };

  /* ---------- 3. relógio correndo + contador de horas ---------- */
  W.relogio = (id, c, e) => { const r = num(c.r, 200), horas = num(c.horas, 72);
    return {
      svg: `<g transform="translate(${c.x},${c.y})"><g id="${id}"><circle r="${r}" fill="${K("cream")}" stroke="${K("lead")}" stroke-width="16"/>
        ${[...Array(12)].map((_, i) => `<rect x="-4" y="${-r+18}" width="8" height="24" rx="4" fill="${K("lead")}" transform="rotate(${i*30})"/>`).join("")}
        <g id="${id}_m"><rect x="-5" y="${-r*0.82}" width="10" height="${r*0.82}" rx="5" fill="${K("lead")}"/></g>
        <g id="${id}_h"><rect x="-8" y="${-r*0.55}" width="16" height="${r*0.55}" rx="8" fill="${K("red")}"/></g><circle r="14" fill="${K("lead")}"/></g></g>`,
      html: txt(id + "_n", num(c.x, 540), num(c.y, 700) + r + 90, `0 H`, num(c.size, 130), K(c.cor || (W._dark ? "mus" : "red")), ""),
      anim(){ const d = span(c, e); appear(Q(id), c.t0);
        tl.fromTo(Q(id + "_m"), {rotation:0, transformOrigin:"0px 0px"}, {rotation:Math.min(horas, 12)*360, transformOrigin:"0px 0px", duration:d, ease:"power1.inOut", immediateRender:true}, c.t0);
        tl.fromTo(Q(id + "_h"), {rotation:0, transformOrigin:"0px 0px"}, {rotation:horas*30, transformOrigin:"0px 0px", duration:d, ease:"power1.inOut", immediateRender:true}, c.t0);
        pop(Q(id + "_n"), c.t0 + 0.2); count(Q(id + "_n"), 0, horas, c.t0, d, v => `${Math.round(v)} H`); }
    }; };

  /* ---------- 4. bateria descarregando (ou carregando) ---------- */
  W.bateria = (id, c, e) => { const w = num(c.w, 400), h = num(c.h, 190), de = num(c.de, 100), ate = num(c.ate, 0), iw = w - 28;
    return {
      svg: `<g transform="translate(${c.x},${c.y})"><g id="${id}"><rect x="${-w/2}" y="${-h/2}" width="${w}" height="${h}" rx="30" fill="none" stroke="${K("lead")}" stroke-width="16"/>
        <rect x="${w/2+6}" y="${-h*0.2}" width="26" height="${h*0.4}" rx="9" fill="${K("lead")}"/>
        <rect id="${id}_f" x="${-w/2+14}" y="${-h/2+14}" width="${iw*de/100}" height="${h-28}" rx="16" fill="${de >= ate ? "#6E8B4E" : K("red")}"/></g></g>`,
      html: txt(id + "_n", num(c.x, 540), num(c.y, 900) + h/2 + 90, `${de}%`, num(c.size, 120), ink(), ""),
      anim(){ const d = span(c, e); appear(Q(id), c.t0);
        tl.fromTo(Q(id + "_f"), {attr:{width:iw*de/100}}, {attr:{width:iw*ate/100}, duration:d, ease:"none", immediateRender:false}, c.t0 + 0.2);
        tl.fromTo(Q(id + "_f"), {fill:de >= ate ? "#6E8B4E" : K("red")}, {fill:de >= ate ? K("red") : "#6E8B4E", duration:d, ease:"none", immediateRender:false}, c.t0 + 0.2);
        pop(Q(id + "_n"), c.t0 + 0.2); count(Q(id + "_n"), de, ate, c.t0 + 0.2, d, v => `${Math.round(v)}%`); }
    }; };

  /* ---------- 5. sinal de celular/rede sumindo (barras apagam) ---------- */
  W.sinal = (id, c, e) => { const n = num(c.barras, 4), gap = 78, x0 = -((n - 1)*gap)/2;
    return {
      svg: `<g transform="translate(${c.x},${c.y})"><g id="${id}">${[...Array(n)].map((_, i) =>
        `<rect id="${id}_b${i}" x="${x0 + i*gap - 28}" y="${-(60 + i*60)}" width="56" height="${60 + i*60}" rx="12" fill="${K("lead")}"/>`).join("")}</g></g>`,
      html: `<div class="w" style="left:${num(c.x, 540)}px;top:${num(c.y, 900) + 120}px"><div id="${id}_t" class="selo" style="background:${K("red")};color:#fff;font-size:${num(c.size, 84)}px">${c.texto || "SEM SINAL"}</div></div>`,
      anim(){ const d = span(c, e); appear(Q(id), c.t0);
        for (let i = n - 1, k = 0; i >= 0; i--, k++) tl.to(Q(id + "_b" + i), {fill:"#C9B79A", duration:0.2}, c.t0 + 0.5 + k*(d - 0.6)/n);
        pop(Q(id + "_t"), c.t0 + 0.5 + (n - 1)*(d - 0.6)/n); }
    }; };

  /* ---------- 6. calendário riscando os dias ---------- */
  W.calendario = (id, c, e) => { const n = num(c.dias, 7), cols = Math.min(n, num(c.colunas, 7)), rows = Math.ceil(n/cols), cs = num(c.cell, 116), g = 14,
      cw = cols*cs + (cols + 1)*g, ch = rows*cs + (rows + 1)*g + 90, x0 = -cw/2, y0 = -ch/2;
    let cells = "", xs = "";
    for (let i = 0; i < n; i++){ const cx = x0 + g + (i%cols)*(cs + g), cy = y0 + 90 + g + Math.floor(i/cols)*(cs + g);
      cells += `<rect x="${cx}" y="${cy}" width="${cs}" height="${cs}" rx="12" fill="#FBF4E8"/><text class="o" x="${cx + 14}" y="${cy + 36}" font-size="34" fill="${K("lead")}">${i + 1}</text>`;
      xs += `<path id="${id}_x${i}" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1" d="M${cx+20},${cy+20} L${cx+cs-20},${cy+cs-20} M${cx+cs-20},${cy+20} L${cx+20},${cy+cs-20}" stroke="${K("red")}" stroke-width="14" stroke-linecap="round" fill="none"/>`; }
    return {
      svg: `<g transform="translate(${c.x},${c.y})"><g id="${id}"><rect x="${x0}" y="${y0}" width="${cw}" height="${ch}" rx="26" fill="${K("cream")}"/>
        <rect x="${x0}" y="${y0}" width="${cw}" height="84" rx="26" fill="${K("red")}"/><rect x="${x0}" y="${y0 + 50}" width="${cw}" height="34" fill="${K("red")}"/>
        <text class="o" x="0" y="${y0 + 62}" text-anchor="middle" font-size="52" fill="#fff">${c.titulo || n + " DIAS"}</text>${cells}${xs}</g></g>`,
      html: "",
      anim(){ const d = span(c, e); appear(Q(id), c.t0);
        for (let i = 0; i < n; i++) tl.fromTo(Q(id + "_x" + i), {strokeDashoffset:1}, {strokeDashoffset:0, duration:0.16, ease:"none", immediateRender:true}, c.t0 + 0.4 + i*(d - 0.5)/n); }
    }; };

  /* ---------- 7. medidor com ponteiro (valor 0 a 1) ---------- */
  W.medidor = (id, c, e) => { const r = num(c.r, 220), v0 = num(c.de, 0), v1 = num(c.ate, 1);
    return {
      svg: `<g transform="translate(${c.x},${c.y})"><g id="${id}"><rect x="${-r-50}" y="${-r-60}" width="${2*r+100}" height="${r+150}" rx="50" fill="${K("cream")}"/>
        ${arc(r, -180, -120, "#6E8B4E", 46)}${arc(r, -120, -60, K("mus"), 46)}${arc(r, -60, 0, K("red"), 46)}
        <g id="${id}_n"><rect x="-8" y="${-r*0.86}" width="16" height="${r*0.86}" rx="8" fill="${K("lead")}"/></g><circle r="24" fill="${K("lead")}"/></g></g>`,
      html: c.rotulo ? `<div class="w" style="left:${num(c.x, 540)}px;top:${num(c.y, 900) + 150}px"><div id="${id}_t" class="selo" style="background:${K(c.corRotulo || "red")};color:#fff;font-size:${num(c.size, 80)}px">${c.rotulo}</div></div>` : "",
      anim(){ const d = span(c, e); appear(Q(id), c.t0);
        tl.fromTo(Q(id + "_n"), {rotation:-80 + 160*v0, transformOrigin:"0px 0px"}, {rotation:-80 + 160*v1, transformOrigin:"0px 0px", duration:d, ease:"power2.in", immediateRender:true}, c.t0 + 0.2);
        if (c.rotulo) pop(Q(id + "_t"), c.t0 + 0.2 + d*0.6); }
    }; };

  /* ---------- 8. gráfico de linha desenhando (pontos = alturas 0..1) ---------- */
  W.grafico = (id, c, e) => { const w = num(c.w, 760), h = num(c.h, 460), p = c.pontos || [1, 0.8, 0.5, 0.3, 0.15, 0.05];
    const pts = p.map((v, i) => [-w/2 + i*(w/(p.length - 1)), h/2 - v*h]), dpath = "M" + pts.map(q => q.join(",")).join(" L"), last = pts[pts.length - 1];
    return {
      svg: `<g transform="translate(${c.x},${c.y})"><g id="${id}"><path d="M${-w/2},${-h/2-20} L${-w/2},${h/2} L${w/2+20},${h/2}" stroke="${K("lead")}" stroke-width="10" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
        <path id="${id}_l" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1" d="${dpath}" stroke="${K(c.cor || "red")}" stroke-width="16" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
        <circle id="${id}_d" cx="${last[0]}" cy="${last[1]}" r="22" fill="${K("mus")}" stroke="${K("lead")}" stroke-width="8" opacity="0"/>
        ${c.eixo ? `<text class="o" x="0" y="${h/2+64}" text-anchor="middle" font-size="40" fill="${K("lead")}">${c.eixo}</text>` : ""}</g></g>`,
      html: c.rotulo ? `<div class="w" style="left:${num(c.x, 540)}px;top:${num(c.y, 900) - h/2 - 60}px"><div id="${id}_t" class="selo" style="background:${K("mus")};color:${K("lead")};font-size:${num(c.size, 64)}px">${c.rotulo}</div></div>` : "",
      anim(){ const d = span(c, e); appear(Q(id), c.t0);
        tl.fromTo(Q(id + "_l"), {strokeDashoffset:1}, {strokeDashoffset:0, duration:d, ease:"power1.inOut", immediateRender:true}, c.t0 + 0.3);
        tl.fromTo(Q(id + "_d"), {opacity:0}, {opacity:1, duration:0.2, immediateRender:true}, c.t0 + 0.3 + d);
        if (c.rotulo) pop(Q(id + "_t"), c.t0 + 0.3 + d*0.5); }
    }; };

  /* ---------- 9. barra de progresso/nível (de% → até%) ---------- */
  W.barra = (id, c, e) => { const w = num(c.w, 760), h = 74, de = num(c.de, 0), ate = num(c.ate, 100);
    return {
      svg: `<g transform="translate(${c.x},${c.y})"><g id="${id}"><rect x="${-w/2}" y="${-h/2}" width="${w}" height="${h}" rx="37" fill="rgba(43,47,46,.25)"/>
        <rect id="${id}_f" x="${-w/2}" y="${-h/2}" width="${w*de/100}" height="${h}" rx="37" fill="${K(c.cor || "mus")}"/></g></g>`,
      html: txt(id + "_t", num(c.x, 540), num(c.y, 900) - 90, c.rotulo || "", num(c.size, 56), ink(), "") + txt(id + "_n", num(c.x, 540) + w/2 - 70, num(c.y, 900), `${de}%`, 46, "#fff", ""),
      anim(){ const d = span(c, e); appear(Q(id), c.t0); pop(Q(id + "_t"), c.t0); pop(Q(id + "_n"), c.t0);
        tl.fromTo(Q(id + "_f"), {attr:{width:w*de/100}}, {attr:{width:w*ate/100}, duration:d, ease:"power1.inOut", immediateRender:false}, c.t0 + 0.2);
        count(Q(id + "_n"), de, ate, c.t0 + 0.2, d, v => `${Math.round(v)}%`); }
    }; };

  /* ---------- 10. pulso: anéis que saem de um ponto (alerta/sinal) ---------- */
  W.pulso = (id, c, e) => { const r = num(c.r, 120), n = 3;
    return {
      svg: `<g transform="translate(${c.x},${c.y})">${[...Array(n)].map((_, i) => `<circle id="${id}_p${i}" r="${r}" fill="none" stroke="${K(c.cor || "red")}" stroke-width="12" opacity="0"/>`).join("")}</g>`,
      html: "",
      anim(){ const per = 1.4, rep = Math.max(0, Math.ceil((e - c.t0)/per) - 1);
        for (let i = 0; i < n; i++) tl.fromTo(Q(id + "_p" + i), {scale:0.4, opacity:0.85, transformOrigin:"0px 0px"}, {scale:2, opacity:0, transformOrigin:"0px 0px", duration:per, ease:"power1.out", repeat:rep, immediateRender:false}, c.t0 + i*per/n); }
    }; };

  /* ---------- 11. carimbo que bate na tela ---------- */
  W.carimbo = (id, c, e) => ({
    svg: "",
    html: `<div class="w" style="left:${num(c.x, 540)}px;top:${num(c.y, 900)}px"><div id="${id}" class="selo" style="background:${K(c.bg || "red")};color:${K(c.fg || "#fff")};font-size:${num(c.size, 96)}px;border:6px solid rgba(255,255,255,.55)">${c.texto || "FECHADO"}</div></div>`,
    anim(){ tl.fromTo(Q(id), {scale:2.4, opacity:0, rotation:-20}, {scale:1, opacity:1, rotation:num(c.giro, -8), duration:0.22, ease:"power4.in", immediateRender:true}, c.t0);
      tl.fromTo(Q(id), {y:0}, {y:-10, duration:0.06, yoyo:true, repeat:1, immediateRender:false}, c.t0 + 0.22); }
  });

  /* ---------- 12. lista que vai marcando itens (✓) no ritmo da fala; ts = tempos de cada item ---------- */
  W.lista = (id, c, e) => { const it = c.itens || [], ts = c.ts || it.map((_, i) => c.t0 + i*num(c.passo, 0.7)), rh = num(c.linha, 104), w = num(c.w, 780);
    return {
      svg: "",
      html: `<div class="w" style="left:${num(c.x, 540)}px;top:${num(c.y, 900)}px"><div id="${id}" style="width:${w}px;background:${K("cream")};border-radius:26px;padding:18px 28px;box-shadow:0 8px 0 rgba(0,0,0,.2);font-family:Oswald;color:${K("lead")}">
        ${c.titulo ? `<div style="font-size:50px;color:${K("red")};padding:8px 0 4px">${c.titulo}</div>` : ""}
        ${it.map((t, i) => `<div id="${id}_i${i}" style="display:flex;align-items:center;gap:22px;height:${rh}px;font-size:58px;border-bottom:3px solid rgba(43,47,46,.12)"><span style="width:60px;height:60px;border-radius:50%;background:#6E8B4E;color:#fff;font-size:42px;line-height:60px;text-align:center">✓</span>${t}</div>`).join("")}</div></div>`,
      anim(){ pop(Q(id), c.t0 - 0.1 > 0 ? c.t0 - 0.1 : c.t0);
        it.forEach((_, i) => tl.fromTo(Q(id + "_i" + i), {x:-60, opacity:0}, {x:0, opacity:1, duration:0.3, ease:"power2.out", immediateRender:true}, ts[i])); }
    }; };

  /* ---------- 13. Rafa (personagem do estilo) parado respirando/piscando ---------- */
  W.rafa = (id, c, e) => ({
    svg: rafa(id, {x:num(c.x, 540), y:num(c.y, 1500), s:num(c.escala, 1.2), pose:c.pose || "stand", mood:c.mood || "worry", flip:!!c.flip}),
    html: "",
    anim(){ idleRafa(id, c.t0, e); }
  });

  /* ---------- 14. selo/etiqueta de texto que aparece na palavra ---------- */
  W.selo = (id, c, e) => ({
    svg: "", html: selo(id, num(c.x, 540), num(c.y, 330), c.texto || "", K(c.bg || "lead"), K(c.fg || "cream"), num(c.size, 56)),
    anim(){ pop(Q(id), c.t0); }
  });

  /* ---------- combinar peças e mover a câmera ---------- */
  W.mix = (...ps) => ({ svg: ps.map(p => p.svg || "").join(""), html: ps.map(p => p.html || "").join(""), anim(){ ps.forEach(p => p.anim && p.anim()); } });
  // câmera extra (só desloca; o template já faz o zoom lento): "esq" | "dir" | "cima" | "baixo"
  W.pan = (it, s, e, tipo) => { const d = {esq:[40, 0], dir:[-40, 0], cima:[0, 50], baixo:[0, -50]}[tipo] || [0, 0];
    if (d[0] || d[1]) tl.fromTo(`#${it.id}_S .cam`, {x:0, y:0}, {x:d[0], y:d[1], duration:e - s, ease:"none", immediateRender:false}, s); };
})();

/* ---------- cena declarativa: SC.widgets monta uma cena inteira só com a "spec" (sem desenhar nada) ----------
   props.spec = { base:"prateleira" (cena antiga como fundo; usa props.textos/t), fundo:"#CDB08C" | "gDark" | "gMoss", chao:1450, chaoCor:"#8E7556", pan:"dir",
                  selos:[{texto, x, y, t, bg, fg, size}], w:[{tipo:"garrafa", x, y, t0, t1, ...}, ...] }          */
if (typeof SC !== "undefined") SC.widgets = (it, X, T, s, e, I) => {
  const S = (it.props && it.props.spec) || {}, bgc = S.fundo || "#E0C49C";
  const base = S.base && SC[S.base] ? SC[S.base](it, X, T, s, e, I) : null;   // cena antiga do template como fundo (as peças vêm por cima)
  W._dark = S.escuro != null ? !!S.escuro : (bgc.startsWith("#") ? (parseInt(bgc.slice(1, 3), 16)*0.3 + parseInt(bgc.slice(3, 5), 16)*0.59 + parseInt(bgc.slice(5, 7), 16)*0.11) < 110 : /Dark|Moss/.test(bgc));
  let svg = base && !S.fundo ? (base.svg || "") : (bgc.startsWith("#") ? `<rect width="1080" height="1920" fill="${bgc}"/>` : `<rect width="1080" height="1920" fill="url(#${bgc})"/>`) + (base ? (base.svg || "") : "");
  if (S.chao && !base) svg += `<rect y="${S.chao}" width="1080" height="${1920 - S.chao}" fill="${S.chaoCor || "#7A5A42"}"/><rect y="${S.chao}" width="1080" height="14" fill="rgba(0,0,0,.18)"/>`;
  const parts = (S.w || []).map((c, i) => { const f = W[c.tipo];
    if (!f){ console.warn("widget desconhecido:", c.tipo); return {svg:"", html:"", anim(){}}; }
    return f(I("w" + i), Object.assign({t0:s + 0.2}, c), e); });
  const selos = (S.selos || []).map((o, i) => W.selo(I("s" + i), {x:o.x, y:o.y, texto:o.texto, bg:o.bg, fg:o.fg, size:o.size, t0:o.t != null ? o.t : s + 0.2}, e));
  const all = W.mix(...parts, ...selos);
  return { svg: svg + all.svg, html: (base ? (base.html || "") : "") + all.html, anim(){ base && base.anim && base.anim(); all.anim(); if (S.pan) W.pan(it, s, e, S.pan); } };
};
