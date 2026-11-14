// Injetado no preview: seek/play controlados pelo editor + clique/arrastar itens.
(function () {
  const clips = () => Array.from(document.querySelectorAll(".clip"));
  let playing = false;
  function vis(t) {
    for (const el of clips()) {
      const s = +el.dataset.start || 0;
      const d = el.dataset.duration != null ? +el.dataset.duration : 1e9;
      const on = t >= s && t < s + d;
      el.style.visibility = on ? "" : "hidden";
      if (el.tagName === "VIDEO") {
        const target = t - s + (+(el.dataset.mediaStart || 0));
        el.muted = true;
        if (on) {
          if (playing) {
            if (el.paused) el.play().catch(() => {});
            if (Math.abs(el.currentTime - target) > 0.3) el.currentTime = target;
          } else {
            if (!el.paused) el.pause();
            if (Math.abs(el.currentTime - target) > 0.04) el.currentTime = target;
          }
        } else if (!el.paused) el.pause();
      }
    }
  }
  window.__edSeek = function (t, isPlaying) {
    playing = !!isPlaying;
    const tls = window.__timelines || {};
    const tl = tls.main || Object.values(tls)[0];
    window.__hfThreeTime = t;
    if (tl) {
      tl.seek(t, false);
      if (!tl.eventCallback("onUpdate") && window.__hfRender) { try { window.__hfRender(t); } catch (e) {} }
    } else if (window.__hfRender) { try { window.__hfRender(t); } catch (e) {} }
    vis(t);
  };
  window.__edReady = () => !!(window.__timelines && (window.__timelines.main || Object.keys(window.__timelines).length));

  // ---- clique = selecionar / arrastar = mover (itens genéricos)
  let ids = new Set();
  window.__edSetIds = (list) => { ids = new Set(list); };
  function itemOf(el) {
    while (el && el !== document.body) {
      if (el.id) {
        const base = el.id.replace(/(_box|_mv|_clip|_g\d+(w\d+)?)$/, "");
        if (ids.has(base)) return { id: base, box: document.getElementById(base + "_box") };
      }
      el = el.parentElement;
    }
    return null;
  }
  let drag = null;
  document.addEventListener("mousedown", (e) => {
    const it = itemOf(e.target);
    window.parent.postMessage({ ed: "select", id: it ? it.id : null }, "*");
    if (it && it.box && !e.altKey) {
      const cs = getComputedStyle(it.box);
      drag = { id: it.id, box: it.box, x0: e.clientX, y0: e.clientY, l: parseFloat(cs.left), t: parseFloat(cs.top), moved: false };
      e.preventDefault();
    }
  }, true);
  document.addEventListener("mousemove", (e) => {
    if (!drag) return;
    const dx = e.clientX - drag.x0, dy = e.clientY - drag.y0;
    if (Math.abs(dx) + Math.abs(dy) > 3) drag.moved = true;
    if (drag.moved) { drag.box.style.left = drag.l + dx + "px"; drag.box.style.top = drag.t + dy + "px"; }
  }, true);
  document.addEventListener("mouseup", (e) => {
    if (drag && drag.moved) {
      window.parent.postMessage({ ed: "move", id: drag.id, dx: e.clientX - drag.x0, dy: e.clientY - drag.y0 }, "*");
    }
    drag = null;
  }, true);
  // ---- teclas apertadas com o foco na prévia vão para o editor (Espaço, J/K/L, setas…)
  const FWD = new Set([" ", "ArrowLeft", "ArrowRight", "Home", "End", "PageUp", "PageDown"]);
  document.addEventListener("keydown", (e) => {
    if (/INPUT|TEXTAREA|SELECT/.test((e.target && e.target.tagName) || "")) return;
    if (FWD.has(e.key) || (e.ctrlKey && /^[szy]$/i.test(e.key))) e.preventDefault();
    window.parent.postMessage({ ed: "key", key: e.key, ctrlKey: e.ctrlKey, shiftKey: e.shiftKey, altKey: e.altKey, metaKey: e.metaKey }, "*");
  }, true);

  // ---- capturar o quadro atual como PNG (html2canvas carregado só quando precisa)
  window.__edCapture = async function () {
    if (!window.html2canvas) {
      await new Promise((res, rej) => {
        const s = document.createElement("script");
        s.src = "https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js";
        s.onload = res; s.onerror = () => rej(new Error("html2canvas não carregou"));
        document.head.appendChild(s);
      });
    }
    const w = window.innerWidth, h = window.innerHeight;
    // <base> temporário: o clone que o html2canvas faz resolve fontes/imagens relativas a partir daqui
    let base = null;
    if (!document.querySelector("base")) { base = document.createElement("base"); base.href = location.href; document.head.prepend(base); }
    try {
      const c = await window.html2canvas(document.body, { width: w, height: h, windowWidth: w, windowHeight: h, x: 0, y: 0, scrollX: 0, scrollY: 0, scale: 1, useCORS: true, allowTaint: false, backgroundColor: "#000", logging: false });
      return c.toDataURL("image/png");
    } finally { if (base) base.remove(); }
  };

  const st = document.createElement("style");
  st.textContent = ".ed-box{cursor:move}.ed-box:hover{outline:3px dashed rgba(255,200,0,.7);outline-offset:4px}";
  document.head.appendChild(st);
})();
