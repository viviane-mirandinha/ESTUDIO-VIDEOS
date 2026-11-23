// Editor de Vídeos Local — frontend (sem build)
const $ = (s) => document.querySelector(s);
// ---- ROTAS LEGÍVEIS: /#/criar/stickman, /#/estilos/ia, /#/videos/<id>/editor ... (as antigas #stickman, #meus continuam valendo)
const ROTAS = { "#inicio": "", "#home": "videos", "#galeria": "estilos", "#skillsia": "estilos/ia", "#copiar": "estilos/copiar", "#clonarguia": "estilos/clonar", "#extras": "estilos/extras", "#ranking": "estilos/ranking",
  "#vimg": "criar/imagens", "#shorts": "criar/shorts", "#stickman": "criar/stickman", "#cortes": "criar/cortes", "#falado": "criar/falado",
  "#emalta": "ideias/em-alta", "#bombando": "ideias/estilos-em-alta", "#feeds": "ideias/feeds", "#roteiro": "texto/roteiro", "#vozes": "texto/vozes", "#autopilot": "canal/piloto", "#ajustes": "ajustes" };
const SUBS_IDEIAS = ["cacar", "saturado", "publico", "placar"];
function urlDe(st) {
  const s = st.sel, pid = st.pid ? encodeURIComponent(st.pid) : "";
  let p;
  if (s === "#editor" && pid) p = `videos/${pid}/editor`;
  else if (s === "#conferir" && pid) p = `videos/${pid}/conferir`;
  else if (s === "#comparar" && pid) p = `videos/${pid}/comparar`;
  else if (s === "#pedido") p = pid ? `estilos/${pid}/fazer` : "criar/pedido";
  else if (s === "#ideias") p = "ideias/" + (SUBS_IDEIAS.includes(st.sub) ? st.sub : "cacar");
  else p = ROTAS[s];
  return p == null ? null : location.pathname + location.search + "#/" + p;
}
function rotaParaHash(h) {   // "#/criar/stickman" → "#stickman" (formato que o resto do painel já entende)
  if (!/^#\//.test(h)) return h;
  const p = h.slice(2).split("?")[0].split("/").filter(Boolean).map(decodeURIComponent), j = p.join("/");
  if (!p.length) return "#inicio";
  if (p[0] === "videos" && p[1] && p[2] === "editor") return "#editor=" + encodeURIComponent(p[1]);
  if (p[0] === "videos" && p[1] && p[2] === "conferir") return "#conferir=" + encodeURIComponent(p[1]);
  if (p[0] === "videos") return "#meus";
  if (p[0] === "ideias" && SUBS_IDEIAS.includes(p[1])) return "#ideias=" + p[1];
  if (p[0] === "estilos" && p[2] === "fazer") return "#estilos";
  const k = Object.keys(ROTAS).find((x) => ROTAS[x] === j);
  return k ? ({ "#home": "#meus", "#galeria": "#estilos", "#vimg": "#imagens" }[k] || k) : "#inicio";
}
if (/^#\//.test(location.hash)) { try { history.replaceState(history.state, "", location.pathname + location.search + rotaParaHash(location.hash)); } catch (e) { } }

const api = async (url, opt = {}) => {
  const r = await fetch(url, opt);
  if (!r.ok) throw new Error((await r.text()) || r.status);
  return r.json();
};
const jpost = (url, body, method = "POST") =>
  api(url, { method, headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
const fmt = (t) => { t = Math.max(0, t || 0); const m = Math.floor(t / 60); const s = t - m * 60; return m + ":" + (s < 10 ? "0" : "") + s.toFixed(1); };
// tempo em mm:ss.ff (ff = quadros) — usado no transporte; clique em #tcur alterna para segundos
const FPS = () => +(S?.edit?.canvas?.fps) || 30;
const pad2 = (n) => (n < 10 ? "0" : "") + n;
function fmtTC(t) { t = Math.max(0, t || 0); const fps = FPS(); const fr = Math.round(t * fps); const sec = Math.floor(fr / fps); return pad2(Math.floor(sec / 60)) + ":" + pad2(sec % 60) + "." + pad2(fr % fps); }
const fmtT = (t) => (S.tcMode === "sec" ? fmt(t) : fmtTC(t));
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const DUR_OPTS = [[30, "30 s"], [60, "1 min"], [90, "1:30"], [120, "2 min"], [150, "2:30"], [180, "3 min"], [300, "5 min"], [480, "8 min"], [600, "10 min"], [900, "15 min"], [1200, "20 min"], [1800, "30 min"], [2400, "40 min"], [3000, "50 min"], [3600, "1 h"], [7200, "2 h"], [10800, "3 h"]];
const EST = { d: null, t: 0 }, RC = { l: null };   // ⏱💲 estimativas e 📒 receitas (24/10)
function toast(msg, ms = 2200) { const t = $("#toast"); t.textContent = msg; t.classList.remove("hidden"); clearTimeout(toast.h); toast.h = setTimeout(() => t.classList.add("hidden"), ms); }

// ======================================================= LAZY-LOAD (miniaturas só baixam quando o card aparece na tela)
const LAZY = "IntersectionObserver" in window ? new IntersectionObserver((ents) => ents.forEach((en) => {
  if (!en.isIntersecting) return;
  const el = en.target; LAZY.unobserve(el);
  if (el.dataset.bg) { el.style.backgroundImage = `url('${el.dataset.bg}')`; el.removeAttribute("data-bg"); }
  if (el.dataset.bgvar) { el.style.setProperty("--img", `url('${el.dataset.bgvar}')`); el.removeAttribute("data-bgvar"); }
}), { rootMargin: "400px" }) : null;
function lazyBg(root) {
  (root || document).querySelectorAll("[data-bg],[data-bgvar]").forEach((el) => {
    if (LAZY) return LAZY.observe(el);
    if (el.dataset.bg) el.style.backgroundImage = `url('${el.dataset.bg}')`;
    if (el.dataset.bgvar) el.style.setProperty("--img", `url('${el.dataset.bgvar}')`);
  });
}
const POR_PAGINA = 60;   // lista grande: mostra 60 e um botão "Mostrar mais"

// ======================================================= LISTA
async function loadHome() {
  hideNew();
  $("#home").classList.remove("hidden"); $("#editor").classList.add("hidden"); $("#pedido").classList.add("hidden");
  if (typeof cmpHide === "function") cmpHide();
  stopPlay();
  $("#topnav").classList.remove("hidden"); marcarAba("#home"); TELA.atual = "Meus vídeos"; TELA.video = "";
  window.scrollTo(0, 0); filaAtualizar(true);
  let list;
  try { list = await api("/api/projects"); }
  catch (e) { $("#grid").innerHTML = `<div class="card">❌ Não consegui carregar a lista: ${esc(String(e.message || e).slice(0, 200))}</div>`; return; }
  HOME.list = list;
  renderHome();
}
// ---- filtro por origem (lembrado no navegador) + seções LONGOS/SHORTS
const HOME = { list: [], origem: "Todos" };
try { HOME.origem = localStorage.getItem("home_fmt") || "Todos"; } catch (e) { }
const ORIGENS = ["Todos", "Vídeos longos", "Shorts"];
const ORIG_ICO = { "Todos": "🗂", "Vídeos longos": "🎬", "Shorts": "📱" };
const fmtOf = (p) => ((+p.h || 0) > (+p.w || 0) ? "Shorts" : "Vídeos longos");
// ---- 📊 resumo do relatório no card: ⏱ tempo · 🎟 tokens · 💲 custo
async function relMini(g) {
  if (!HOME.rel || Date.now() - HOME.relT > 60000) { try { HOME.rel = Object.fromEntries((await api("/api/relatorios")).map((r) => [r.id, r])); HOME.relT = Date.now(); } catch (e) { return; } }
  const tok = (n) => n >= 1e6 ? (n / 1e6).toFixed(1).replace(".", ",") + " mi" : n >= 1e3 ? Math.round(n / 1e3) + " mil" : String(n);
  g.querySelectorAll("[data-relmini]").forEach((el) => {
    const r = HOME.rel[el.dataset.relmini]; if (!r) return;
    const p = [];
    if (r.minutos) p.push(`⏱ ${String(r.minutos).replace(".", ",")} min`);
    if (r.render_segundos) p.push(`🎬 render ${fmtSeg(r.render_segundos)}`);
    if (r.local) p.push("🆓 grátis (feito no PC)");
    else if (r.tokens || r.custo_usd != null) p.push("🧠 feito com o Claude");
    el.textContent = p.join(" · "); el.title = "Clique em 📊 Relatório pra ver tudo";
  });
}
function renderHome() {
  const all = HOME.list, g = $("#grid");
  const cnt = (o) => (o === "Todos" ? all : all.filter((p) => fmtOf(p) === o)).length;
  if (!ORIGENS.includes(HOME.origem) || (HOME.origem !== "Todos" && !cnt(HOME.origem))) HOME.origem = "Todos";
  $("#origBar").innerHTML = ORIGENS.map((o) => `<button class="btn big orig ${HOME.origem === o ? "on" : ""}" data-orig="${o}" ${cnt(o) || o === "Todos" ? "" : "disabled"}>${ORIG_ICO[o]} ${o} <span class="n">${cnt(o)}</span></button>`).join("");
  $("#origBar").querySelectorAll("[data-orig]").forEach((b) => (b.onclick = () => { HOME.origem = b.dataset.orig; HOME.lim = POR_PAGINA; try { localStorage.setItem("home_fmt", HOME.origem); } catch (e) { } renderHome(); }));
  const listAll = HOME.origem === "Todos" ? all : all.filter((p) => fmtOf(p) === HOME.origem);
  HOME.lim = HOME.lim || POR_PAGINA;
  const list = listAll.slice(0, HOME.lim);
  if (!all.length) { g.innerHTML = `<div class="card">Nenhum vídeo encontrado. Confira as pastas em 📁 Pastas.</div>`; return; }
  if (!list.length) { g.innerHTML = `<div class="card">Nenhum vídeo em <b>${esc(HOME.origem)}</b>.</div>`; return; }
  const resto = listAll.length - list.length;
  const groups = { "ESTILOS NOVOS": [], "VÍDEOS LONGOS": [], "SHORTS": [] };
  list.forEach((p) => groups[/VIDEOS-NOVOS$/i.test(p.group || "") ? "ESTILOS NOVOS" : (+p.h || 0) > (+p.w || 0) ? "SHORTS" : "VÍDEOS LONGOS"].push(p));
  const GRP_TIT = { "ESTILOS NOVOS": "✨ ESTILOS NOVOS (testes 01-31, 16:9)", "SHORTS": "📱 SHORTS (vertical 9:16 — curtos e stories)", "VÍDEOS LONGOS": "🎬 VÍDEOS LONGOS (YouTube 16:9)" };
  // ⬇ botões de baixar (funcionam no celular: o navegador salva o mp4 no aparelho). Leve só aparece se o leve.mp4 existir.
  const dlRow = (p) => !p.rendered ? "" : `<div class="dlRow" onclick="event.stopPropagation()"><a class="btn dl go" href="/api/baixar/${p.id}/leve" download title="Versão menor (até 30 MB), boa para mandar e postar${p.leve_mb ? "" : " — será criada na hora"}">⬇ Baixar leve${p.leve_mb ? ` <small>${String(p.leve_mb).replace(".", ",")} MB</small>` : ""}</a><a class="btn dl" href="/api/baixar/${p.id}/final" download title="Qualidade máxima">⬇ Baixar final${p.mb ? ` <small>${String(p.mb).replace(".", ",")} MB</small>` : ""}</a></div>`;
  const cardVideo = (p) => `
    <div class="proj video" data-id="${p.id}" data-vid="1">
      <div class="th" ${p.thumb ? `data-bg="/api/thumb/${p.id}?${p.mtime}"` : `data-thpend="${p.id}"`}>${p.thumb ? "" : "🎞"}</div>
      <div class="badge vid">🎞 só vídeo</div>
      <div class="estilo">📁 ${esc(p.origem || "Outros")}</div>
      <div class="nm">${esc(p.name)}</div>
      <div class="meta">${p.w || "?"}×${p.h || "?"} · ${fmt(p.dur)}</div>
      ${dlRow(p)}
      <div class="acts"><button class="btn imp" data-imp="${p.id}" title="Coloca este vídeo no editor pra você poder mexer nele">📥 Importar</button><button class="btn" data-fold="${p.id}">📂 Pasta</button><button class="btn" data-play="${p.id}">▶ Ver</button></div>
    </div>`;
  const cardProj = (p) => `
    <div class="proj" data-id="${p.id}">
      <div class="th" ${p.thumb ? `data-bg="/api/thumb/${p.id}?${p.mtime}"` : p.rendered ? `data-thpend="${p.id}"` : ""}>${p.thumb ? "" : "🎞"}</div>
      <div class="badge ${p.rendered ? "ok" : "no"}">${p.rendered ? "✅ VÍDEO PRONTO" : p.conferir ? "🖼 falta conferir as imagens" : "⏳ ainda sem vídeo"}</div>
      <div class="estilo">🎨 ${esc(p.estilo || "")}</div>${p.referencia?.canal ? `<div class="refl">copiado de <b>${esc(p.referencia.canal)}</b></div>` : ""}
      <div class="nm">${esc(String(p.name).replace(/^\d+\s*-\s*[^-]+-\s*/, ""))}</div>
      <div class="meta">${p.w}×${p.h} · ${fmt(p.dur)}</div>
      <div class="relMini" data-relmini="${p.id}"></div>
      ${p.conferir ? `<div class="acts"><button class="btn go" data-conf="${p.id}">🖼 Conferir imagens e fazer o vídeo</button></div>` : ""}
      ${dlRow(p)}
      <div class="acts"><button class="btn ok" data-open="${p.id}">✏ Abrir no editor</button>${p.rendered ? `<button class="btn" data-play="${p.id}" title="Abre o vídeo no computador onde o painel está rodando">▶ Ver</button><button class="btn" data-capa="${p.id}" title="Cria a capa do Instagram e o descricao.txt (títulos, descrição e 5 hashtags)">🖼 Criar capa</button>` : ""}</div>
      <details class="mais" onclick="event.stopPropagation()"><summary>⋯ Mais opções</summary><div class="acts"><button class="btn" data-fold="${p.id}">📂 Pasta</button><button class="btn" data-rel="${p.id}">📊 Relatório</button>${p.rendered ? `<button class="btn" data-rev="${p.id}" title="O que vale conferir antes de postar">🔎 O que revisar</button>` : ""}${p.referencia?.video ? `<button class="btn" data-ref="${esc(p.referencia.video)}" title="${esc(p.referencia.canal || "")}">📺 Vídeo copiado</button>` : ""}${p.referencia?.canal_url ? `<button class="btn" data-ref="${esc(p.referencia.canal_url)}">📡 Canal: ${esc((p.referencia.canal || "").slice(0, 18))}</button>` : ""}${p.tem_ref ? `<button class="btn cmp" data-cmp="${p.id}" title="Ver a referência e o nosso vídeo lado a lado">Comparar</button>` : ""}${p.ajustavel ? `<button class="btn" data-ajuste="${p.id}" title="Pede pro Claude mudar só um detalhe (cor, nome, música…) e regravar">🔧 Pedir ajuste</button>` : ""}</div></details>
    </div>`;
  g.innerHTML = Object.entries(groups).filter(([, ps]) => ps.length).map(([gr, ps]) => `
    <h2 class="grp">${GRP_TIT[gr]} <span>${ps.filter((p) => p.rendered).length} de ${ps.length} prontos</span></h2>
    <div class="gridIn">${ps.map((p) => (p.tipo === "video" ? cardVideo(p) : cardProj(p))).join("")}</div>`).join("")
    + (resto > 0 ? `<div class="maisRow"><button class="btn big" id="btnMais">⬇ Mostrar mais ${Math.min(resto, POR_PAGINA)} (faltam ${resto})</button></div>` : "");
  if (resto > 0) $("#btnMais").onclick = () => { HOME.lim += POR_PAGINA; const y = window.scrollY; renderHome(); window.scrollTo(0, y); };
  lazyBg(g); relMini(g);
  g.querySelectorAll("[data-fold]").forEach((b) => (b.onclick = (e) => { e.stopPropagation(); api(`/api/open/${b.dataset.fold}?what=folder`, { method: "POST" }); }));
  g.querySelectorAll("[data-play]").forEach((b) => (b.onclick = (e) => { e.stopPropagation(); const p = HOME.list.find((x) => x.id === b.dataset.play) || {}; assistirAqui(b.dataset.play, p.name, !!p.leve_mb); }));
  g.querySelectorAll("[data-cmp]").forEach((b) => (b.onclick = (e) => { e.stopPropagation(); openComparar(b.dataset.cmp, "home"); }));
  g.querySelectorAll("[data-imp]").forEach((b) => (b.onclick = (e) => { e.stopPropagation(); importarVideo(b.dataset.imp, b); }));
  g.querySelectorAll("[data-capa]").forEach((b) => (b.onclick = (e) => { e.stopPropagation(); criarCapa(b.dataset.capa); }));
  g.querySelectorAll("[data-conf]").forEach((b) => (b.onclick = (e) => { e.stopPropagation(); openConferir(b.dataset.conf); }));
  g.querySelectorAll("[data-open]").forEach((b) => (b.onclick = (e) => { e.stopPropagation(); openProject(b.dataset.open); }));
  g.querySelectorAll("[data-ajuste]").forEach((b) => (b.onclick = (e) => { e.stopPropagation(); pedirAjuste(b.dataset.ajuste); }));
  g.querySelectorAll(".proj").forEach((el) => (el.onclick = () => { if (el.dataset.vid) api(`/api/open/${el.dataset.id}?what=final`, { method: "POST" }); else { const p = HOME.list.find((x) => x.id === el.dataset.id); if (p && p.conferir) openConferir(p.id); else openProject(el.dataset.id); } }));
  pollThumbs();
}
// miniaturas dos vídeos soltos são geradas em segundo plano: tenta de novo até aparecer
function pollThumbs(tries = 0) {
  clearTimeout(pollThumbs.h);
  const pend = [...document.querySelectorAll("[data-thpend]")];
  if (!pend.length || tries > 20 || $("#home").classList.contains("hidden")) return;
  pollThumbs.h = setTimeout(async () => {
    for (const el of pend) {
      try { const r = await fetch(`/api/thumb/${el.dataset.thpend}?${Date.now()}`, { method: "HEAD" }); if (r.ok) { el.style.backgroundImage = `url('/api/thumb/${el.dataset.thpend}?${Date.now()}')`; el.textContent = ""; el.removeAttribute("data-thpend"); } await new Promise((ok) => setTimeout(ok, 30)); } catch (e) { }
    }
    pollThumbs(tries + 1);
  }, 3000);
}
async function importarVideo(id, btn) {
  const p = HOME.list.find((x) => x.id === id);
  if (!p) return;
  if (!confirm(`Importar "${p.name}"?\n\nVou criar a pasta "${p.name}" ao lado do arquivo, MOVER o vídeo pra dentro dela e abrir no editor.`)) return;
  if (btn) { btn.disabled = true; btn.textContent = "⏳ Importando…"; }
  try {
    const r = await jpost(`/api/importar/${id}`, {});
    toast(r.ja_existia ? "Esse vídeo já tinha pasta — abrindo" : "✅ Importado! Abrindo no editor…");
    await openProject(r.pid);
  } catch (e) {
    if (btn) { btn.disabled = false; btn.textContent = "📥 Importar"; }
    toast("❌ Não consegui importar: " + String(e.message || e).replace(/^\{"detail":"|"\}$/g, "").slice(0, 200), 6000);
  }
}
$("#btnReload").onclick = loadHome;
function renderPastas(l) {
  $("#folderList").innerHTML = l.map((f) => `<div class="pastaRow"><span>📁 ${esc(f.nome)}${f.existe ? "" : ' <small class="mu">(não encontrada)</small>'}</span><button class="btn mini" data-rmp="${f.i}" title="Tirar da lista (não apaga nada)">✕ tirar</button></div>`).join("") || '<p class="mu">Nenhuma pasta.</p>';
  $("#folderList").querySelectorAll("[data-rmp]").forEach((b) => (b.onclick = async () => { const r = await jpost("/api/pastas", { acao: "remover", i: +b.dataset.rmp }); renderPastas(r.pastas); loadHome(); }));
}
$("#btnFolders").onclick = async () => { renderPastas(await api("/api/pastas")); $("#folderBox").classList.toggle("hidden"); };
$("#btnAddFolder").onclick = async () => {
  toast("Abrindo a janela do Windows pra escolher a pasta…", 3000);
  const r = await jpost("/api/pastas", { acao: "adicionar" });
  if (!r.ok) return toast(r.msg || "Nenhuma pasta escolhida");
  renderPastas(r.pastas); loadHome();
};

// ======================================================= PEDIR VÍDEO
const PED = { estilos: [], sel: null, dur: 60, reg: {} };
// "Suas regras" do formulário → dict que o guarda de densidade lê (ligar qualquer regra já segura o excesso no 1º render)
function pedColherRegras() {
  const r = {};
  if (PED.reg.broll) r.broll_primeiro = true;
  if (PED.reg.pouca) { r.intervalo_min = 12; r.max_pct = 20; }
  if (PED.reg.sem) r.sem_animacao = true;
  return r;
}
function pedRegrasWire() {
  document.querySelectorAll("#pRegras [data-reg]").forEach((b) => {
    b.classList.toggle("on", !!PED.reg[b.dataset.reg]);
    b.onclick = () => { PED.reg[b.dataset.reg] = !PED.reg[b.dataset.reg]; b.classList.toggle("on", !!PED.reg[b.dataset.reg]); };
  });
}
// ---- 🎵 música de fundo do pedido: nenhuma / automática / a minha (+ volume + abaixar quando o narrador fala)
const MUS = { modo: "nenhuma", nivel: "baixa", duck: true, arq: null, t: null };
function musTela() {
  document.querySelectorAll("#pMus [data-mus]").forEach((b) => b.classList.toggle("on", b.dataset.mus === MUS.modo));
  $("#pMusAutoRow").classList.toggle("hidden", MUS.modo !== "auto");
  $("#pMusMinhaRow").classList.toggle("hidden", MUS.modo !== "minha");
  $("#pMusNivelRow").classList.toggle("hidden", MUS.modo === "nenhuma");
  document.querySelectorAll("#pMusNivel [data-nivel]").forEach((b) => b.classList.toggle("on", b.dataset.nivel === MUS.nivel));
  $("#pMusDuckLbl").classList.toggle("hidden", MUS.nivel !== "presente");
  $("#pMusDuck").checked = MUS.duck;
  $("#pMusNivelAjuda").textContent = MUS.nivel === "baixa"
    ? "Quase imperceptível: fica por baixo da voz o tempo todo e abaixa ainda mais quando o narrador fala."
    : MUS.duck ? "Dá pra sentir a música, mas quando o narrador fala ela abaixa sozinha e a voz continua em primeiro lugar."
               : "A música fica mais audível o tempo todo. Pra não cobrir o narrador, o volume é limitado automaticamente.";
  if (MUS.modo === "auto") musSugerir();
}
function musSugerir() {
  clearTimeout(MUS.t);
  MUS.t = setTimeout(async () => {
    const box = $("#pMusSug"), au = $("#pMusAudio");
    const tema = $("#pTema").value.trim(), roteiro = $("#pTemRoteiro").checked ? $("#pRoteiro").value.trim().slice(0, 3000) : "";
    if (!tema && !roteiro) { box.textContent = "Escolho a música que combina com o assunto, o roteiro e o estilo do vídeo. Escreva o tema e eu mostro a sugestão aqui."; au.classList.add("hidden"); return; }
    try {
      const r = await api("/api/musica/sugerir?" + new URLSearchParams({ tema, roteiro, estilo: PED.sel || "" }));
      if (!r.ok) { box.textContent = "A biblioteca de músicas está vazia — rode ferramentas/baixar_musicas.py."; au.classList.add("hidden"); return; }
      box.innerHTML = `🎧 Combina com este vídeo: <b>${esc(r.titulo)}</b> — ${esc(r.motivo)}. <small>(A escolha final é feita na hora de criar e pode variar entre faixas parecidas.)</small>`;
      au.src = r.url; au.classList.remove("hidden");
    } catch (e) { box.textContent = "Escolho a música sozinho na hora de criar o vídeo."; au.classList.add("hidden"); }
  }, 500);
}
document.querySelectorAll("#pMus [data-mus]").forEach((b) => (b.onclick = () => { MUS.modo = b.dataset.mus; musTela(); }));
document.querySelectorAll("#pMusNivel [data-nivel]").forEach((b) => (b.onclick = () => { MUS.nivel = b.dataset.nivel; musTela(); }));
$("#pMusDuck").onchange = (e) => { MUS.duck = e.target.checked; musTela(); };
["#pTema", "#pRoteiro"].forEach((id) => $(id).addEventListener("input", () => { if (MUS.modo === "auto") musSugerir(); }));
$("#pMusArq").onchange = (e) => {
  const f = e.target.files[0]; if (!f) return;
  MUS.arq = null; $("#pMusArqInfo").textContent = "⏳ enviando…";
  const fd = new FormData(); fd.append("file", f);
  const x = new XMLHttpRequest(); x.open("POST", "/api/musica/subir");
  x.upload.onprogress = (ev) => { if (ev.lengthComputable) $("#pMusArqInfo").textContent = `⏳ enviando ${Math.round(ev.loaded * 100 / ev.total)}%`; };
  x.onload = () => { let r = {}; try { r = JSON.parse(x.responseText); } catch (er) { }
    if (x.status !== 200) { $("#pMusArqInfo").textContent = "❌ " + (r.detail || "não consegui enviar"); return; }
    MUS.arq = r.arquivo_id; $("#pMusArqInfo").textContent = `✅ ${r.nome} (${fmtSeg(r.dur)}) — vou deixar no volume certo, sem cobrir o narrador`; };
  x.onerror = () => ($("#pMusArqInfo").textContent = "❌ não consegui enviar");
  x.send(fd);
};
const SELO = { fabrica: ["⚡ Automático (0 token)", "fab"], claude: ["🧠 Precisa do Claude", "cla"], em_breve: ["🔜 Em breve", "brv"] };
const urlOk = (u) => /^https?:\/\/\S+\.\S+/.test(u);
// estiloId (opcional) = veio da galeria "✨ Fazer um vídeo neste estilo": esconde os passos 1 e 2 e só pede tema/canal/duração
async function openPedido(estiloId, from) {
  stopPlay(); hideNew(); if (typeof cmpHide === "function") cmpHide();
  $("#home").classList.add("hidden"); $("#editor").classList.add("hidden"); $("#pedido").classList.remove("hidden");
  window.scrollTo(0, 0);
  PED.from = from || "home";
   marcaPre("#pMarca");
  carregarVozes().catch(() => { });
  if (!PED.estilos.length) {
    try { PED.estilos = await api("/api/estilos"); } catch (e) { $("#estGrid").innerHTML = `<div class="card">❌ Não consegui carregar os estilos: ${esc(e.message)}</div>`; return; }
  }
  const fixo = typeof estiloId === "string" ? PED.estilos.find((x) => x.id === estiloId) : null;
  PED.fixo = !!fixo;
  if (fixo) {
    PED.sel = fixo.id;
    const d = fixo.formato === "short" || PED.fmtEsc === "short" ? 60 : 300;
    if (PED.durDe !== fixo.id) { PED.dur = d; PED.durDe = fixo.id; }   // só volta ao padrão quando é outro estilo
    pedDurs();
    $("#pEsc").innerHTML = `<div class="th ${fixo.formato === "short" ? "vert" : ""}" style="${fixo.thumb_url ? `background-image:url('${fixo.thumb_url}')` : ""}"></div>
      <div class="tx"><div class="k">Estilo escolhido</div><div class="nm">${esc(fixo.nome)}</div>
      <div class="tags"><span class="tag">${fixo.formato === "short" ? "📱 Short" : "🎬 Vídeo longo"}</span>${seloGal(fixo)}</div></div>
      <button class="btn" id="pTrocar">🔄 Trocar estilo</button>`;
    $("#pTrocar").onclick = () => (PED.from === "galeria" ? openGaleria() : openPedido(null, PED.from));
  }
  $("#pEsc").classList.toggle("hidden", !fixo);
  $("#pStep1").classList.toggle("hidden", !!fixo); $("#pStep2").classList.toggle("hidden", !!fixo);
  $("#pNum3").textContent = fixo ? "1" : "3";
  pedRegrasWire();   // as "Suas regras" marcadas continuam ao sair e voltar (antes eram apagadas a cada entrada)
  renderEstilos(); pedidoResumo(); rcRender("pedido"); estCarregar();
}
function renderEstilos() {
  const grupos = [["fabrica", "⚡ Automático — o computador faz sozinho"], ["claude", "🧠 Precisa do Claude — a gente prepara o pedido"], ["em_breve", "🔜 Em breve — ainda em preparação"]];
  $("#estGrid").innerHTML = grupos.map(([tipo, titulo]) => {
    const es = PED.estilos.filter((e) => e.tipo === tipo); if (!es.length) return "";
    return `<h4 class="grp">${titulo} <span>${es.length}</span></h4><div class="estIn">${es.map((e) => `
      <div class="est ${PED.sel === e.id ? "sel" : ""}" data-id="${esc(e.id)}" title="${esc(e.descricao || "")}" ${e.video_url ? `data-vurl="${esc(e.video_url)}"` : ""}>
        <div class="th ${e.formato === "short" ? "vert" : ""}" ${e.thumb_url ? `style="--img:url('${e.thumb_url}')"` : ""}>${e.thumb_url ? `<div class="im"></div>` : `<span class="noimg">🎞</span>`}</div>
        <div class="selo ${SELO[tipo][1]}">${SELO[tipo][0]}</div>
        <div class="nm">${esc(e.nome)}</div>
        <div class="desc">${esc(e.descricao || "")}</div>
        ${e.referencia?.canal_url || e.referencia?.video ? `<a class="refa" target="_blank" href="${esc(e.referencia.canal_url || e.referencia.video)}">📡 ${e.referencia.canal ? esc(e.referencia.canal.slice(0, 22)) : "canal"}</a>` : ""}
      </div>`).join("")}</div>`;
  }).join("");
  lazyBg($("#estGrid"));
  $("#estGrid").querySelectorAll(".est").forEach((el) => (el.onclick = (ev) => { if (ev.target.closest("a")) return; PED.sel = el.dataset.id; renderEstilos(); pedidoResumo(); }));
}
function pedidoResumo() {
  const e = PED.estilos.find((x) => x.id === PED.sel);
  if (e && PED.fmtDe !== e.id) {
    const faz = (f) => e.tipo !== "fabrica" || f === "longo" || (e.formatos || []).includes(f);   // fábrica só faz em pé se o estilo.json permitir
    if (PED.fmtEsc && faz(PED.fmtEsc)) PED.fmt = PED.fmtEsc;   // você já tinha escolhido: mantém ao trocar de estilo
    else {
      if (PED.fmtEsc === "short" && PED.fmtDe) toast(`📐 O estilo “${e.nome}” só faz vídeo deitado (16:9). Para em pé, escolha outro estilo.`, 6000);
      PED.fmt = e.formato === "short" ? "short" : "longo";
    }
    PED.fmtDe = e.id;
  }
  raChips("#pFmt", "pf", (v) => v === PED.fmt);
  $("#pFmtRow").classList.toggle("hidden", !e || (e.tipo === "fabrica" && !(e.formatos || []).includes("short")));   // fábrica: só se o estilo.json tiver "formatos" com short
  const fmtTxt = e && !$("#pFmtRow").classList.contains("hidden") ? ` Formato: ${PED.fmt === "short" ? "📱 em pé (9:16)" : "🎬 deitado (16:9)"}.` : "";
  pedClaudeAtualizar();
  const clUsa = e && e.tipo === "fabrica" && ($("#pClRot").checked || $("#pClBusca").checked);
  $("#pResumo").textContent = !e ? "" : fmtTxt.trim() + " " + (e.tipo === "fabrica" ? `✅ Estilo "${e.nome}": o vídeo é feito no seu PC` + (clUsa ? " (o Claude faz só as partes marcadas acima, por centavos)." : ", sem gastar nada.")
    : e.tipo === "claude" ? `🧠 Estilo "${e.nome}": o Claude monta o vídeo sozinho (uns 15-30 min). Acompanhe em 📂 Meus vídeos.`
    : `🔜 Estilo "${e.nome}" ainda está em preparação: vou guardar o pedido numa pasta pra fazer com o Claude.`);
  const cla = !!e && e.tipo !== "fabrica";   // ⏱💲 estimativa pela média dos vídeos já feitos + 📝 roteiro grátis antes
  $("#pFazer").textContent = "🎬 Fazer vídeo" + (cla ? estTxt(e.id, "claude", 1) : "");
  $("#pFazer").title = cla ? estTitulo(e.id, "claude") : "";
  $("#pPrevia").classList.toggle("hidden", !cla || $("#pTemRoteiro").checked || PED.dur > 600);
}
// 🧠 Terceirizar pro Claude (só estilos feitos no PC): escolhe roteiro e/ou busca de imagens e mostra o preço médio estimado
const CLC = { cache: {} };
const clUsd = (n) => "US$ " + n.toFixed(n < 0.1 ? 3 : 2).replace(".", ",");
const clBrl = (n) => "R$ " + n.toFixed(2).replace(".", ",");
async function pedClaudeAtualizar() {
  const e = PED.estilos.find((x) => x.id === PED.sel), ok = !!e && e.tipo === "fabrica";
  $("#pClaudeRow").classList.toggle("hidden", !ok);
  if (!ok) { $("#pClRot").checked = false; $("#pClBusca").checked = false; return; }
  const meu = $("#pTemRoteiro").checked;   // com roteiro próprio não há o que escrever
  if (meu) $("#pClRot").checked = false;
  const key = e.id + "|" + PED.dur;
  let est = CLC.cache[key];
  if (!est) { try { est = CLC.cache[key] = await api(`/api/claude-custo?duracao=${PED.dur}&estilo=${encodeURIComponent(e.id)}`); } catch (x) { return; } }
  $("#pClRot").disabled = !est.modo || meu;
  $("#pClBusca").disabled = !est.modo;
  if (!est.modo) { $("#pClRot").checked = false; $("#pClBusca").checked = false; }
  const r = est.roteiro, b = est.busca, t = est.total;
  const sel = ($("#pClRot").checked ? r.usd : 0) + ($("#pClBusca").checked ? b.usd : 0);
  const plano = est.modo === "plano";
  const pr = `✍️ roteiro ≈ <b>${clUsd(r.usd)}</b> (${clBrl(r.brl)}) · 🖼 imagens ≈ <b>${clUsd(b.usd)}</b> (${clBrl(b.brl)}) · os dois ≈ <b>${clUsd(t.usd)}</b> (${clBrl(t.brl)})`;
  $("#pClCusto").innerHTML = (plano
    ? `🧠 <b>Vai usar o Claude que já está instalado neste PC</b> (o seu plano): <b>sem chave e sem cobrança extra</b>, só consome um pouco do limite do plano. Se o limite acabar ou o Claude falhar, o PC faz sozinho.<br>💲 <b>Equivale a</b>, se fosse pago por uso, para este vídeo (${fmtSeg(PED.dur)}): ${pr}. Na média uns <b>${clUsd(est.usd_por_minuto)}</b> por minuto de vídeo.`
    : est.modo === "api"
      ? `💲 <b>Preço médio estimado</b> com a sua chave da Anthropic, para este vídeo (${fmtSeg(PED.dur)}): ${pr}. Na média dá uns <b>${clUsd(est.usd_por_minuto)}</b> por minuto de vídeo: <b>centavos, não é caro</b>.`
      : `💲 <b>Preço médio</b> se usar o Claude, para este vídeo (${fmtSeg(PED.dur)}): ${pr}. Na média uns <b>${clUsd(est.usd_por_minuto)}</b> por minuto de vídeo: centavos.`)
    + (sel && !plano ? ` Marcado agora: <b>${clUsd(sel)}</b>.` : "")
    + ` <small>(Estimativa com o ${esc(est.modelo)} a US$ ${est.preco_in}/${est.preco_out} por milhão de tokens entrada/saída e câmbio de referência R$ ${String(est.cambio_ref).replace(".", ",")}; o gasto real fica no 📊 Relatório do vídeo.)</small>`
    + (est.modo ? "" : `<br>🔑 <b>Não achei o Claude neste PC nem uma chave.</b> Instale o app do Claude (claude.ai/download) e entre na sua conta, ou cole uma chave da Anthropic em ⚙ Ajustes. Sem isso, tudo continua no seu PC.`);
}
["#pClRot", "#pClBusca"].forEach((s) => ($(s).onchange = () => pedidoResumo()));
$("#btnPedir").onclick = () => openPedido(null, "home");
$("#btnPedidoBack").onclick = () => (PED.from === "galeria" ? openGaleria() : loadHome());
$("#pVerCanal").onclick = () => { const u = $("#pRefCanal").value.trim(); if (!urlOk(u)) return toast("Cole um link válido do canal (começa com https://)"); window.open(u, "_blank"); };
$("#pVerVideo").onclick = () => { const u = $("#pRefVideo").value.trim(); if (!urlOk(u)) return toast("Cole um link válido do vídeo (começa com https://)"); window.open(u, "_blank"); };
$("#pTemRoteiro").onchange = () => { $("#pRoteiroRow").classList.toggle("hidden", !$("#pTemRoteiro").checked); if (VZ.p) VZ.p.nota(); };

function renderDurs(box, atual, onPick, nota, lista) {
  const L = lista || DUR_OPTS;
  $(box).innerHTML = L.map(([d, l]) => `<button class="btn pill ${+atual === d ? "on" : ""}" data-dur="${d}">${l}</button>`).join("");
  if (nota) { $(nota).classList.toggle("hidden", +atual <= 600); if (+atual > 600) durNotaTxt(nota, +atual); }
  $(box).querySelectorAll("[data-dur]").forEach((b) => (b.onclick = () => { onPick(+b.dataset.dur); renderDurs(box, +b.dataset.dur, onPick, nota, lista); }));
}
const pedDurs = () => renderDurs("#pDurs", PED.dur, (d) => { PED.dur = d; pedClaudeAtualizar(); }, "#pDurNota");
pedDurs();
function pollJob(job, onDone) {   // janela de progresso com Fechar (continua na fila) e Cancelar
  acompanhar(job, $("#mTitle").textContent || "Trabalhando…", (res, fechado) => {
    if (!fechado) return onDone(res);
    if (res && res.precisa_claude) { modal("📝 Pedido pronto"); return onDone(res); }   // o texto do pedido só existe aqui: reabre
    toast("✅ Pronto! Veja em 📂 Meus vídeos.", 6000);
  });
}
$("#pFazer").onclick = async () => {
  if (PED.sel && !$("#pTemRoteiro").checked && !(await ideiaAuto("#pTema", { formato: PED.fmt === "short" ? "short" : "longo" }))) return;
  canalAuto("#pCanal");
  const e = PED.estilos.find((x) => x.id === PED.sel);
  const refCanal = $("#pRefCanal").value.trim(), refVideo = $("#pRefVideo").value.trim();
  const tema = $("#pTema").value.trim(), roteiro = $("#pTemRoteiro").checked ? $("#pRoteiro").value.trim() : "", canal = $("#pCanal").value.trim();
  if (refCanal && !urlOk(refCanal)) return toast("O link do canal não parece certo. Tem que começar com https://", 4000);
  if (refVideo && !urlOk(refVideo)) return toast("O link do vídeo não parece certo. Tem que começar com https://", 4000);
  if (!e) { $("#estGrid").scrollIntoView({ behavior: "smooth" }); return toast("Escolha um estilo na galeria (passo 2)", 4000); }
  if (!tema && !roteiro) { $("#pTema").focus(); return toast("Escreva o tema do vídeo (ou marque e cole seu roteiro)", 4000); }
  if ($("#pTemRoteiro").checked && !roteiro) { $("#pRoteiro").focus(); return toast("Cole o roteiro ou desmarque a opção de roteiro próprio", 4000); }
  try { localStorage.setItem("pedido_canal", canal); } catch (x) { }
  const body = { estilo: e.id, tema, roteiro, canal_nome: canal, marca: marcaVal("#pMarca"), duracao: PED.dur, ref_canal: refCanal, ref_video: refVideo, voz: $("#pVoz").value, formato: PED.fmt || e.formato };
  if (PED.audio && VZ.p.modo === "fora") body.audio_id = PED.audio.id;   // narração pronta (mp3/wav/m4a) no lugar da voz do PC
  const regras = pedColherRegras(); if (Object.keys(regras).length) body.regras = regras;
  if (MUS.modo === "minha" && !MUS.arq) { $("#pMusArq").scrollIntoView({ behavior: "smooth", block: "center" }); return toast("Envie o arquivo da sua música (espere aparecer ✅) ou escolha Automática/Nenhuma", 4500); }
  body.musica = { modo: MUS.modo, nivel: MUS.nivel, duck: MUS.nivel === "baixa" ? true : MUS.duck, arquivo_id: MUS.modo === "minha" ? MUS.arq : "" };
  if (e.tipo === "fabrica") { body.claude_roteiro = $("#pClRot").checked && !roteiro; body.claude_busca = $("#pClBusca").checked; }   // 🧠 terceirizar (opcional, com chave)
  modal(e.tipo === "fabrica" ? "🎬 Fazendo o seu vídeo…" : "📝 Criando o pedido…");
  $("#mMsg").textContent = "Enviando…";
  let r;
  try { r = await jpost("/api/pedido", body); }
  catch (x) { closeModal(); return toast("❌ " + String(x.message || x).replace(/^\{"detail":"|"\}$/g, "").slice(0, 200), 6000); }
  if (r.fila > 1) $("#mMsg").textContent = `Na fila, posição ${r.fila}…`;
  pollJob(r.job, (res) => {
    if (res.precisa_claude) return pedidoPronto(res);
    $("#mTitle").textContent = res.rendered ? "✅ Vídeo pronto!" : "⚠ Montado, mas sem vídeo final";
    $("#mMsg").textContent = `${res.name}\n\n📁 ${amigavel(res.folder)}` + (res.rendered ? "" : "\n\nAbra no editor e clique em ▶ Gerar vídeo final.");
    mbtn("✏ Abrir no editor", () => { closeModal(); openProject(res.pid); }, "go");
    if (res.rendered) { mbtnVer(res.pid); mlinksBaixar(res.pid, res.name); mbtnCapa(res.pid); }
    mbtn("📂 Abrir pasta", () => api(`/api/open/${res.pid}?what=folder`, { method: "POST" }));
    mbtn("Ver na lista", () => { closeModal(); loadHome(); });
  });
};

// ======================================================= ESTADO
const S = { pid: null, edit: null, durations: {}, scenes: [], hist: [], fut: [], last: "", sel: null, t: 0, playing: false, pps: 30, dirty: false };
const items = () => S.edit.items;
const byId = (id) => items().find((i) => i.id === id);
const W = () => S.edit.canvas.w, H = () => S.edit.canvas.h, DUR = () => +S.edit.duration || 10;
function uid(p) { let i = 1; while (byId(p + i) || (S.edit.audio?.extra || []).some((x) => x.id === p + i)) i++; return p + i; }
function mediaUrl(src) { if (!src) return ""; return /^[a-zA-Z]:[\\/]/.test(src) || src.startsWith("/") ? "/api/abs?path=" + encodeURIComponent(src) : `/p/${S.pid}/${src}`; }

async function openProject(pid) {
  let d;
  try { d = await api("/api/project/" + pid); }
  catch (e) { toast("❌ Não consegui abrir este vídeo: " + String(e.message || e).slice(0, 160), 6000); return; }
  hideNew();
  Object.assign(S, { pid, edit: d.edit, durations: d.durations, scenes: d.scenes, folder: d.folder, hist: [], fut: [], sel: null, t: 0, dirty: false });
  S.edit.items = S.edit.items || []; S.edit.tracks = S.edit.tracks || []; S.edit.audio = S.edit.audio || {};
  S.last = JSON.stringify(S.edit);
  $("#home").classList.add("hidden"); $("#pedido").classList.add("hidden"); $("#editor").classList.remove("hidden");
  if (typeof cmpHide === "function") cmpHide();
  $("#projName").textContent = S.edit.name || "";
  $("#projEstilo").textContent = d.estilo ? "🎨 " + d.estilo : "";
  TELA.atual = "Editor"; TELA.video = S.edit.name || ""; S.pastaNome = d.pasta_nome || "";
  $("#tdur").textContent = fmtT(DUR());
  S.pps = Math.max(5, Math.min(300, ($("#timeline").clientWidth - 170) / DUR()));
  $("#zoom").value = S.pps;
  setLoop(false);
  setupAudio(); renderTimeline(); renderProps(); refreshPreview(true); setDirty(false);
}
$("#btnBack").onclick = () => { if (S.dirty && !confirm("Tem mudanças não salvas. Sair mesmo assim?")) return; loadHome(); };

// ---- histórico
function commit(previewNow = false) {
  const cur = JSON.stringify(S.edit);
  if (cur === S.last) return;
  S.hist.push(S.last); if (S.hist.length > 200) S.hist.shift();
  S.fut = []; S.last = cur; setDirty(true);
  schedulePreview(previewNow ? 50 : 450);
}
let commitT = null;
function commitSoon() { clearTimeout(commitT); commitT = setTimeout(() => { commit(); renderTimeline(); }, 500); }
function undo() { if (!S.hist.length) return toast("Nada para desfazer"); S.fut.push(S.last); S.last = S.hist.pop(); S.edit = JSON.parse(S.last); afterHist(); }
function redo() { if (!S.fut.length) return toast("Nada para refazer"); S.hist.push(S.last); S.last = S.fut.pop(); S.edit = JSON.parse(S.last); afterHist(); }
function afterHist() { setDirty(true); setupAudio(); renderTimeline(); renderProps(); schedulePreview(50); }
function setDirty(v) { S.dirty = v; $("#dirty").classList.toggle("hidden", !v); }
$("#btnUndo").onclick = undo; $("#btnRedo").onclick = redo;
async function save() {
  try { await jpost("/api/project/" + S.pid, S.edit, "PUT"); }
  catch (e) { toast("❌ Não consegui salvar: " + String(e.message || e).slice(0, 160), 6000); throw e; }
  setDirty(false); toast("✅ Salvo");
}
$("#btnSave").onclick = save;

// ======================================================= PREVIEW
let front = $("#frameA"), back = $("#frameB"), prevT = null, prevSeq = 0;
back.classList.add("back");
function schedulePreview(ms = 450) { clearTimeout(prevT); prevT = setTimeout(refreshPreview, ms); }
async function refreshPreview(first) {
  const seq = ++prevSeq;
  $("#loading").textContent = "atualizando…";
  let r;
  try { r = await jpost("/api/preview/" + S.pid, S.edit); }
  catch (e) { $("#loading").textContent = "⚠ erro no preview"; console.error(e); return; }
  if (seq !== prevSeq) return;
  const f = first ? front : back;
  f.onload = async () => {
    const w = f.contentWindow;
    for (let i = 0; i < 100 && !(w.__edReady && w.__edReady()); i++) await new Promise((r) => setTimeout(r, 50));
    if (seq !== prevSeq && !first) return;
    try { w.__edSetIds(items().map((i) => i.id)); } catch (e) {}
    await new Promise((r) => setTimeout(r, 120));
    seekFrame(f, S.t);
    if (!first) { front.classList.add("back"); f.classList.remove("back"); back = front; front = f; }
    $("#loading").textContent = "";
  };
  fitStage(); f.src = r.url;
}
function seekFrame(f, t, playing) { try { f.contentWindow.__edSeek(t, playing); } catch (e) {} }
function fitStage() {
  const st = $("#stage"); const sw = st.clientWidth, sh = st.clientHeight;
  const sc = Math.min(sw / W(), sh / H());
  for (const f of [front, back]) {
    f.style.width = W() + "px"; f.style.height = H() + "px";
    f.style.transform = `scale(${sc})`; f.style.left = (sw - W() * sc) / 2 + "px"; f.style.top = (sh - H() * sc) / 2 + "px";
  }
}
window.addEventListener("resize", () => S.edit && fitStage());
window.addEventListener("message", (e) => {
  const m = e.data || {};
  if (m.ed === "select") { if (m.id) select(m.id); }
  if (m.ed === "move") {
    const it = byId(m.id); if (!it) return; const p = (it.props = it.props || {});
    if (p.fill) { p.fill = false; p.w = W(); p.h = H(); p.x = W() / 2; p.y = H() / 2; }
    p.x = Math.round((+p.x || W() / 2) + m.dx); p.y = Math.round((+p.y || H() / 2) + m.dy);
    commit(true); renderProps();
  }
});

// ---- tocar
let raf = null, t0 = 0, n0 = 0;
function setTime(t, fromPlay) {
  S.t = Math.max(0, Math.min(DUR(), t));
  $("#tcur").textContent = fmtT(S.t);
  $("#scrub").value = (S.t / DUR()) * 1000;
  $("#playhead").style.left = S.t * S.pps + "px";
  if (!fromPlay) { seekFrame(front, S.t, false); syncAudio(false); }
}
function play() {
  if (S.playing) return stopPlay();
  const lr0 = loopRange();
  if (lr0 && (S.t < lr0[0] || S.t >= lr0[1] - 0.05)) setTime(lr0[0]);
  else if (S.t >= DUR() - 0.05) setTime(0);
  S.playing = true; t0 = S.t; n0 = performance.now(); $("#btnPlay").textContent = "⏸ Pausar";
  const loop = () => {
    if (!S.playing) return;
    let t = t0 + ((performance.now() - n0) / 1000) * (S.speed || 1);
    const lr = loopRange();
    if (lr && t >= lr[1]) { t = t0 = lr[0]; n0 = performance.now(); }   // 🔁 repetir o trecho
    if (t >= DUR()) { stopPlay(); setTime(DUR()); return; }
    setTime(t, true); seekFrame(front, t, true); syncAudio(true);
    raf = requestAnimationFrame(loop);
  };
  loop();
}
function stopPlay() { S.playing = false; cancelAnimationFrame(raf); $("#btnPlay").textContent = "▶ Play"; if (S.edit) syncAudio(false); if (S.edit) seekFrame(front, S.t, false); }
$("#btnPlay").onclick = play;
$("#scrub").oninput = (e) => { stopPlay(); setTime((e.target.value / 1000) * DUR()); };

// ---- áudio do preview
let AUD = [];
function audioList() {
  const a = S.edit.audio || {}; const out = [];
  if (a.voice?.src) out.push({ key: "audio:voice", o: a.voice, kind: "voice" });
  if (a.music?.src) out.push({ key: "audio:music", o: a.music, kind: "music", loop: true });
  (a.extra || []).forEach((x) => x.src && out.push({ key: "audio:extra:" + x.id, o: x, kind: "extra" }));
  items().filter((i) => i.type === "video" && +(i.props?.volume || 0) > 0 && !i.hidden)
    .forEach((i) => out.push({ key: "clip:" + i.id, o: { src: i.props.src, start: i.start, volume: i.props.volume, trim: i.props.trim || 0, dur: i.dur }, kind: "clip" }));
  return out;
}
function setupAudio() {
  AUD.forEach((x) => x.el.pause()); AUD = [];
  for (const a of audioList()) { const el = new Audio(mediaUrl(a.o.src)); el.preload = "auto"; el.loop = !!a.loop; AUD.push({ ...a, el }); }
}
function syncAudio(playing) {
  const cur = new Map(audioList().map((a) => [a.key, a]));
  for (const A of AUD) {
    const a = cur.get(A.key) || A; const o = a.o; const el = A.el;
    const local = S.t - (+o.start || 0) + (+o.trim || 0);
    const end = a.kind === "clip" ? (+o.trim || 0) + (+o.dur || 0) : (el.duration || 1e9) * (a.loop ? 1e6 : 1);
    const kv = a.kind === "voice" ? S.volVoice : a.kind === "music" ? S.volMusic : 1;   // só na prévia
    el.volume = Math.max(0, Math.min(1, (o.mute ? 0 : +(o.volume ?? 1)) * (S.vol ?? 1) * (kv ?? 1)));
    try { el.playbackRate = Math.min(4, S.speed || 1); el.muted = !!S.muted || (S.speed || 1) > 2; } catch (e) {}
    if (playing && local >= 0 && local < end) {
      const want = a.loop && el.duration ? local % el.duration : local;
      if (el.paused) { el.currentTime = want; el.play().catch(() => {}); }
      else if (Math.abs(el.currentTime - want) > 0.3) el.currentTime = want;
    } else if (!el.paused) el.pause();
  }
}

// ======================================================= TIMELINE
// vídeo antigo em "modo cru": as animações têm tempo fixo dentro do script — dá para mudar texto e esconder, não o tempo
const isLocked = (i) => S.edit.auto_mode === "raw" && i.by === "template";
function rows() {
  const a = S.edit.audio || {};
  const r = [];
  r.push({ name: "🎙 Voz", blocks: a.voice?.src ? [{ key: "audio:voice", label: "Voz", start: +a.voice.start || 0, dur: S.durations[a.voice.src] || DUR(), cls: "audio", fixedDur: true, wave: a.voice.src }] : [] });
  r.push({ name: "🎵 Música", blocks: a.music?.src ? [{ key: "audio:music", label: "Música " + a.music.src.split(/[\\/]/).pop(), start: +a.music.start || 0, dur: DUR() - (+a.music.start || 0), cls: "music", fixedDur: true, wave: a.music.src }] : [] });
  r.push({ name: "🔊 Sons", blocks: (a.extra || []).map((x) => ({ key: "audio:extra:" + x.id, label: x.label || x.src.split(/[\\/]/).pop(), start: +x.start || 0, dur: S.durations[x.src] || 1, cls: "audio", fixedDur: true, off: x.mute, wave: x.src })) });
  const known = new Set(S.edit.tracks.map((t) => t.id));
  const tr = [...S.edit.tracks];
  if (items().some((i) => i.type !== "param" && !known.has(i.track))) tr.push({ id: "__outros", name: "Outros" });
  for (const t of tr) {
    const its = items().filter((i) => i.type !== "param" && (t.id === "__outros" ? !known.has(i.track) : i.track === t.id));
    r.push({ name: t.name || t.id, blocks: its.map((i) => ({ key: i.id, label: (i.type === "text" && i.props?.text) || i.label || i.props?.scene || i.type, start: +i.start || 0, dur: +i.dur || 1, cls: (i.by === "template" ? "tpl " : "") + i.type, off: i.hidden, locked: isLocked(i), thumb: ["image", "video"].includes(i.type) && i.props?.src ? i.props.src : null, trim: +(i.props?.trim || 0) })) });
  }
  return r;
}
function blkBg(b) {
  if (b.wave) { const fd = S.durations[b.wave] || b.dur; return `background-image:url('/api/wave/${S.pid}?src=${encodeURIComponent(b.wave)}');background-size:${fd * S.pps}px 100%;background-repeat:repeat-x;`; }
  if (b.thumb) return `background-image:url('/api/frame/${S.pid}?src=${encodeURIComponent(b.thumb)}&t=${(b.trim + 0.3).toFixed(1)}');background-size:auto 100%;background-repeat:repeat-x;`;
  return "";
}
function renderTimeline() {
  if (!S.edit) return;
  const pps = S.pps, D = DUR();
  const width = D * pps + 200;
  $("#tlInner").style.width = width + 150 + "px";
  const step = pps > 80 ? 1 : pps > 30 ? 2 : pps > 12 ? 5 : 10;
  let ru = "";
  for (let s = 0; s <= D; s += step) ru += `<div class="tk" style="left:${s * pps}px">${fmt(s).replace(".0", "")}</div>`;
  $("#ruler").innerHTML = ru; $("#ruler").style.width = width + "px";
  $("#tracks").innerHTML = rows().map((r) => `<div class="trk"><div class="tn">${esc(r.name)}</div><div class="lane" style="width:${width}px">${r.blocks.map((b) =>
    `<div class="blk ${b.cls}${b.off ? " off" : ""}${S.sel === b.key ? " sel" : ""}" data-key="${esc(b.key)}" ${b.fixedDur ? 'data-fixed="1"' : ""}${b.locked ? ' data-locked="1"' : ""} style="left:${b.start * pps}px;width:${Math.max(6, b.dur * pps)}px;${blkBg(b)}" title="${esc(b.label)} · ${fmt(b.start)} → ${fmt(b.start + b.dur)}">${b.fixedDur || b.locked ? "" : '<div class="h l"></div><div class="h r"></div>'}${esc(b.label)}</div>`).join("")}</div></div>`).join("");
  $("#playhead").style.left = S.t * pps + "px";
}
$("#zoom").oninput = (e) => { S.pps = +e.target.value; renderTimeline(); };
$("#ruler").onmousedown = (e) => {
  const r = $("#ruler").getBoundingClientRect();
  const mv = (ev) => { stopPlay(); setTime((ev.clientX - r.left) / S.pps); };
  mv(e); const up = () => { document.removeEventListener("mousemove", mv); document.removeEventListener("mouseup", up); };
  document.addEventListener("mousemove", mv); document.addEventListener("mouseup", up);
};
function getTimed(key) {
  const a = S.edit.audio;
  if (key === "audio:voice") return a.voice;
  if (key === "audio:music") return a.music;
  if (key.startsWith("audio:extra:")) return (a.extra || []).find((x) => "audio:extra:" + x.id === key);
  return byId(key);
}
$("#tracks").addEventListener("mousedown", (e) => {
  const b = e.target.closest(".blk");
  if (!b) { const lane = e.target.closest(".lane"); if (lane) { stopPlay(); setTime((e.clientX - lane.getBoundingClientRect().left) / S.pps); } return; }
  const key = b.dataset.key; select(key);
  const o = getTimed(key); if (!o) return;
  if (b.dataset.locked) { e.preventDefault(); return; }
  const mode = e.target.classList.contains("l") ? "l" : e.target.classList.contains("r") ? "r" : "m";
  const x0 = e.clientX, s0 = +o.start || 0, d0 = +o.dur || 1;
  const edges = [S.t, 0, DUR()];
  if (S.magnet) document.querySelectorAll(".blk").forEach((x) => { if (x !== b) { const l = parseFloat(x.style.left) / S.pps, w = parseFloat(x.style.width) / S.pps; edges.push(l, l + w); } });
  const near = (v) => { if (!S.magnet) return null; let best = null; for (const e of edges) if (Math.abs(e - v) * S.pps < 10 && (best === null || Math.abs(e - v) < Math.abs(best - v))) best = e; return best; };
  const snap = (v) => Math.round(v * 20) / 20;
  let mexeu = false;   // clique simples só seleciona: não marca “não salvo” nem cria passo no Desfazer
  const mv = (ev) => {
    if (!mexeu && Math.abs(ev.clientX - x0) < 4) return;
    mexeu = true;
    const dt = (ev.clientX - x0) / S.pps;
    if (mode === "m") { let ns = Math.max(0, snap(s0 + dt)); const d1 = +o.dur || (parseFloat(b.style.width) / S.pps); const a1 = near(ns), a2 = near(ns + d1);
      if (a1 !== null) ns = a1; else if (a2 !== null) ns = a2 - d1; o.start = +Math.max(0, ns).toFixed(3); }
    if (mode === "l") { const ns = Math.max(0, Math.min(s0 + d0 - 0.1, snap(s0 + dt))); o.dur = +(d0 + s0 - ns).toFixed(2); o.start = ns; }
    if (mode === "r") { let ne = s0 + Math.max(0.1, snap(d0 + dt)); const a = near(ne); if (a !== null && a > s0 + 0.05) ne = a; o.dur = +(ne - s0).toFixed(3); }
    b.style.left = o.start * S.pps + "px"; if (o.dur && !b.dataset.fixed) b.style.width = o.dur * S.pps + "px";
  };
  const up = () => { document.removeEventListener("mousemove", mv); document.removeEventListener("mouseup", up); if (!mexeu) return; commit(true); renderTimeline(); renderProps(); };
  document.addEventListener("mousemove", mv); document.addEventListener("mouseup", up);
  e.preventDefault();
});

// ======================================================= PROPRIEDADES
function select(key) { S.sel = key; S.panel = "sel"; document.querySelectorAll(".blk").forEach((b) => b.classList.toggle("sel", b.dataset.key === key)); renderProps(); }
const NAMES = { text: "Texto", sub: "Texto 2", size: "Tamanho da letra", color: "Cor", hl_color: "Cor do destaque", dim: "Cor das palavras ainda não faladas",
  bg: "Fundo (cor ou vazio)", font: "Fonte", weight: "Grossura (100-900)", align: "Alinhamento", x: "Posição horizontal (X)", y: "Posição vertical (Y)",
  w: "Largura", h: "Altura", src: "Arquivo", fit: "Encaixe", opacity: "Transparência (0 a 1)", radius: "Cantos arredondados", motion: "Movimento",
  motion_amount: "Força do movimento", trim: "Começar o clipe no segundo", volume: "Volume", speed: "Velocidade", fill: "Tela inteira",
  highlight: "Palavras em destaque (separe por vírgula)", keywords: "Palavras em destaque (separe por vírgula)", upper: "TUDO MAIÚSCULO",
  stroke: "Contorno (cor)", shadow: "Sombra", pad: "Espaço interno", per_group: "Palavras por vez", icone: "Ícone", laranja: "Destacado (cor)",
  palavra: "Palavra do comentário", comenta: "Texto antes da palavra", rodape_forte: "Rodapé (negrito)", rodape: "Rodapé", value: "Valor", line: "Altura da linha", letter: "Espaçamento", scene: "Cena", blur: "Desfoque (px)", brilho: "Brilho (0 a 1)", stroke_w: "Grossura do contorno" };
const SELECTS = { fit: [["cover", "Preencher (corta)"], ["contain", "Caber inteiro"]], align: [["center", "Centro"], ["left", "Esquerda"], ["right", "Direita"]],
  motion: [["none", "Parado"], ["zoom_in", "Aproximar"], ["zoom_out", "Afastar"], ["pan_left", "Deslizar ←"], ["pan_right", "Deslizar →"], ["pan_up", "Subir"], ["pan_down", "Descer"]] };
const ANIMS = [["none", "Nenhuma"], ["fade", "Aparecer suave"], ["slide_up", "Subir"], ["slide_left", "Deslizar"], ["pop", "Pular (pop)"], ["zoom", "Zoom"], ["type", "Máquina de escrever"]];
const isColorKey = (k) => /(^|_)(color|bg|dim|stroke|cor)$/.test(k) || k === "hl_color";
const NUMS = new Set(["size", "x", "y", "w", "h", "weight", "opacity", "radius", "motion_amount", "trim", "volume", "speed", "pad", "per_group", "line", "fade_out", "start", "dur", "blur", "brilho", "stroke_w"]);

function field(path, key, val, label) {
  const id = "f_" + path.replace(/\W/g, "_");
  const L = `<label for="${id}">${esc(label || NAMES[key] || key)}</label>`;
  if (key === "src") return `<div class="f">${L}<div class="row"><input type="text" id="${id}" data-p="${path}" value="${esc(val)}"/><button class="btn" data-pick="${path}">Trocar…</button></div></div>`;
  if (SELECTS[key]) return `<div class="f">${L}<select id="${id}" data-p="${path}">${SELECTS[key].map(([v, n]) => `<option value="${v}" ${v === val ? "selected" : ""}>${n}</option>`).join("")}</select></div>`;
  if (typeof val === "boolean") return `<div class="f"><label><input type="checkbox" data-p="${path}" ${val ? "checked" : ""}/> ${esc(label || NAMES[key] || key)}</label></div>`;
  if (Array.isArray(val)) return `<div class="f">${L}<input type="text" id="${id}" data-p="${path}" data-arr="1" value="${esc(val.join(", "))}"/></div>`;
  if (isColorKey(key) || /^#[0-9a-f]{3,8}$/i.test(String(val))) {
    const hex = /^#[0-9a-f]{6}$/i.test(val) ? val : "#000000";
    return `<div class="f">${L}<div class="colorRow"><input type="color" data-p="${path}" data-color="1" value="${hex}"/><input type="text" id="${id}" data-p="${path}" value="${esc(val)}"/></div></div>`;
  }
  if (key === "volume") return `<div class="f">${L}<input type="range" min="0" max="1.5" step="0.01" data-p="${path}" data-num="1" value="${+val || 0}"/> <span class="note">${Math.round((+val || 0) * 100)}%</span></div>`;
  if (typeof val === "number" || NUMS.has(key)) return `<div class="f">${L}<input type="number" step="any" id="${id}" data-p="${path}" data-num="1" value="${esc(val)}"/></div>`;
  const long = String(val ?? "").length > 30 || String(val ?? "").includes("\n") || key === "text";
  return `<div class="f">${L}${long ? `<textarea rows="3" id="${id}" data-p="${path}">${esc(val)}</textarea>` : `<input type="text" id="${id}" data-p="${path}" value="${esc(val)}"/>`}</div>`;
}
function getP(path) { return path.split(".").reduce((o, k) => (o == null ? o : o[k]), S); }
function setP(path, v) { const ks = path.split("."); const last = ks.pop(); const o = ks.reduce((o, k) => (o[k] = o[k] ?? {}), S); o[last] = v; }

function renderProps() {
  const P = $("#props"); if (!S.edit) return;
  const key = S.sel; let h = "";
  const all = S.panel === "all" || !key || !getTimed(key);
  h += `<div class="tabs"><button class="btn ${all ? "" : "ok"}" id="tabSel" ${key ? "" : "disabled"}>✏ Selecionado</button><button class="btn ${all ? "ok" : ""}" id="tabAll">📝 Tudo do vídeo</button></div>`;
  if (all) {
    h += `<input type="text" id="busca" placeholder="🔍 procurar texto…" value="${esc(S.busca || "")}"/><br><br>`;
    const q = (S.busca || "").toLowerCase();
    const ord = items().map((it, n) => ({ it, n })).sort((a, b) => (+a.it.start || 0) - (+b.it.start || 0));
    const sec = (title, list) => (list.length ? `<div class="sec"><h3>${title} (${list.length})</h3>${list.join("")}</div>` : "");
    const row = (it, inner) => `<div class="allrow"><div class="allhead"><span>${it.start != null ? fmt(+it.start) : "⚙"}</span><b>${esc(it.label || it.id)}</b>${it.start != null ? `<button class="btn mini" data-go="${esc(it.id)}">▶ ver</button>` : ""}</div>${inner}</div>`;
    const match = (s) => !q || String(s).toLowerCase().includes(q);
    const T = [], C = [], I = [], L = [], Hm = [];
    for (const { it, n } of ord) {
      const p = it.props || {}; const b = `edit.items.${n}`;
      if (it.type === "caption") {
        const ws = p.words || []; const txt = ws.map((w) => w.w).join(" ");
        if (ws.length && match(txt + (it.label || ""))) L.push(row(it, `<div class="f"><textarea rows="3" data-cap="${n}">${esc(txt)}</textarea><span class="note">${ws.length} palavras — mude as palavras mantendo a quantidade</span></div>`));
      } else if (it.type === "html" && it.by !== "template" && /[A-Za-zÀ-ú]/.test(String(p.html || "").replace(/<[^>]+>/g, "")) && match(String(p.html || "").replace(/<[^>]+>/g, " ") + (it.label || ""))) Hm.push(row(it, field(`${b}.props.html`, "html", p.html || "", "HTML (texto entre as tags)")));
      else if (it.type === "text" && typeof p.text === "string" && match(p.text + (it.label || ""))) {
        let inner = field(`${b}.props.text`, "text", p.text, " ");
        for (const k of ["sub", "palavra", "comenta", "rodape_forte", "rodape"]) if (typeof p[k] === "string") inner += field(`${b}.props.${k}`, k, p[k]);
        T.push(row(it, inner));
      } else if (it.type === "param" && typeof p.value !== "object" && match(p.value + (it.label || ""))) T.push(row(it, field(`${b}.props.value`, "value", p.value, " ")));
      else if (it.type === "scene" && p.params && Object.keys(p.params).length) {
        const inner = Object.entries(p.params).filter(([k, v]) => typeof v !== "object" && match(v + (it.label || ""))).map(([k, v]) => field(`${b}.props.params.${k}`, k, v)).join("");
        if (inner) C.push(row(it, inner));
      } else if (it.type === "bloco" && (p.textos || []).length) {
        const inner = p.textos.map((t, i) => ({ t, i })).filter(({ t }) => match((t.para ?? t.de) + (it.label || ""))).map(({ t, i }) => field(`${b}.props.textos.${i}.para`, "bt", t.para ?? t.de, String(t.de).slice(0, 42))).join("");
        if (inner) C.push(row(it, inner));
      } else if ((it.type === "image" || it.type === "video") && match(p.src + (it.label || ""))) I.push(row(it, field(`${b}.props.src`, "src", p.src || "")));
    }
    h += sec("🔤 Textos", T) + sec("💬 Legendas", L) + sec("✨ Cenas", C) + sec("🧩 Blocos", Hm) + sec("🖼 Imagens e vídeos", I);
    if (!T.length && !C.length && !I.length && !L.length && !Hm.length) h += `<p class="note">Nada encontrado.</p>`;
    const rf = (S.edit.referencia = S.edit.referencia || {});
    h += `<div class="sec"><h3>📺 Referência (de onde copiei a edição)</h3>${field("edit.referencia.canal", "canal", rf.canal || "", "Nome do canal")}${field("edit.referencia.canal_url", "canal_url", rf.canal_url || "", "Link do canal")}${field("edit.referencia.video", "video", rf.video || "", "Link do vídeo copiado")}
      <div class="row">${rf.video ? `<button class="btn" data-ref="${esc(rf.video)}">▶ Abrir vídeo</button>` : ""}${rf.canal_url ? `<button class="btn" data-ref="${esc(rf.canal_url)}">📡 Abrir canal</button>` : ""}</div></div>`;
    h += `<div class="sec">${field("edit.name", "name", S.edit.name || "", "Nome do vídeo")}${field("edit.duration", "dur", S.edit.duration, "Duração total (segundos)")}</div>`;
  } else if (false) {
    h += `<h3>⚙ Ajustes do vídeo</h3>` + field("edit.name", "name", S.edit.name || "", "Nome do vídeo") + field("edit.duration", "dur", S.edit.duration, "Duração total (segundos)");
    h += `<p class="note">Tamanho: ${W()}×${H()} · ${S.edit.canvas.fps || 30} fps · modelo: ${esc(S.edit.template || "generic")}</p>`;
    items().forEach((it, n) => { if (it.type === "param") h += field(`edit.items.${n}.props.value`, "value", it.props.value, it.label || it.id); });
    h += `<div class="sec note">Clique num bloco da linha do tempo (embaixo) ou num texto do vídeo para editar.<br><br>
      <b>Atalhos:</b> Espaço = play/pausa · S = cortar no ponto vermelho · ← → anda 1 quadro · Ctrl+Z desfazer · Ctrl+S salvar · Delete apaga o selecionado.</div>`;
  } else if (key.startsWith("audio:")) {
    const o = getTimed(key); const base = key === "audio:voice" ? "edit.audio.voice" : key === "audio:music" ? "edit.audio.music" : `edit.audio.extra.${S.edit.audio.extra.indexOf(o)}`;
    h += `<h3>${key === "audio:voice" ? "🎙 Voz" : key === "audio:music" ? "🎵 Música de fundo" : "🔊 Som"}</h3>`;
    h += field(base + ".src", "src", o.src || "") + field(base + ".volume", "volume", o.volume ?? 1) + field(base + ".start", "start", o.start || 0, "Começa em (segundos)");
    h += field(base + ".mute", "mute", !!o.mute, "Sem som (mudo)");
    if (key === "audio:music") h += field(base + ".fade_out", "fade_out", o.fade_out ?? 2, "Sumir no final (segundos)") + field(base + ".duck", "duck", o.duck !== false, "Abaixar música quando a voz fala");
    if (key !== "audio:voice") h += `<button class="btn danger" id="delAudio">🗑 Remover este áudio</button>`;
  } else {
    const it = byId(key); const n = items().indexOf(it); const b = `edit.items.${n}`;
    h += `<h3>${{ legacy: "🎬 Cena", text: "🔤 Texto", image: "🖼 Imagem", video: "🎞 Vídeo", caption: "💬 Legenda", scene: "✨ Cena pronta", html: "🧩 Bloco", bloco: "✨ Animação pronta" }[it.type] || it.type}</h3>`;
    if (S.edit.template === "prebuilt") h += `<p class="note" style="color:#ffd27a">Este vídeo foi feito num formato antigo: dá pra assistir, mexer no áudio e gerar de novo. Para mudar textos e tempos das cenas, peça pro Claude converter este vídeo pro formato do editor.</p>`;
    else if (it.by === "template") h += `<p class="note">Este elemento faz parte do modelo animado do vídeo: mude texto e tempo aqui. Posição e estilo ficam no modelo.</p>`;
    if (it.type === "text" && typeof (it.props || {}).text === "string") h += `<div class="f destaque">${field(b + ".props.text", "text", it.props.text, "✏ TEXTO QUE APARECE NO VÍDEO")}</div>`;
    if (isLocked(it)) h += `<p class="note">⏱ ${fmt(+it.start || 0)} → ${fmt((+it.start || 0) + (+it.dur || 0))} · neste vídeo antigo o tempo das cenas é fixo (dá para mudar o texto e esconder).</p>`;
    else h += `<div class="row"><div>${field(b + ".start", "start", +it.start || 0, "Começa (s)")}</div><div>${field(b + ".dur", "dur", +it.dur || 1, "Dura (s)")}</div></div>`;
    h += field(b + ".hidden", "hidden", !!it.hidden, "Esconder");
    if (it.by !== "template" && it.type !== "caption") {
      h += `<div class="row"><div><label>Entrada</label><select data-p="${b}.in">${ANIMS.map(([v, l]) => `<option value="${v}" ${(it.in || "none") === v ? "selected" : ""}>${l}</option>`).join("")}</select></div>
        <div><label>Saída</label><select data-p="${b}.out">${ANIMS.filter((a) => a[0] !== "type").map(([v, l]) => `<option value="${v}" ${(it.out || "none") === v ? "selected" : ""}>${l}</option>`).join("")}</select></div></div><br>`;
    }
    const p = (it.props = it.props || {});
    if (it.type === "caption") {
      const ws = p.words || [];
      h += `<div class="f"><label>Palavras da legenda (mude o texto mantendo a mesma quantidade de palavras: ${ws.length})</label><textarea rows="7" data-cap="${n}">${esc(ws.map((w) => w.w).join(" "))}</textarea></div>`;
    }
    const rel = items().filter((x) => x.type === "param" && x.id.startsWith(it.id + "_"));
    rel.forEach((x) => (h += field(`edit.items.${items().indexOf(x)}.props.value`, "value", x.props.value, x.label || x.id)));
    if (it.type === "scene") {
      h += `<div class="f"><label>Cena</label><select data-p="${b}.props.scene">${S.scenes.map((s) => `<option ${s === p.scene ? "selected" : ""}>${s}</option>`).join("")}</select></div>`;
      for (const [k, v] of Object.entries(p.params || {})) h += field(`${b}.props.params.${k}`, k, v);
    }
    if (it.by !== "template" && ["text", "image", "video"].includes(it.type)) {
      const def = { text: { text: "", size: 56, color: "#ffffff", font: "Inter", weight: 800, align: "center", bg: "", highlight: [], hl_color: "#ffb020", x: W() / 2, y: H() / 2, w: "" },
        image: { src: "", fill: true, fit: "cover", motion: "none", opacity: 1, x: W() / 2, y: H() / 2, w: W(), h: H() },
        video: { src: "", fill: true, fit: "cover", trim: 0, volume: 0, motion: "none", x: W() / 2, y: H() / 2, w: W(), h: H() } }[it.type];
      for (const k of Object.keys(def)) if (!(k in p)) p[k] = def[k];
    }
    const order = ["text", "sub", "src", "size", "color", "hl_color", "highlight", "font", "weight", "align", "bg", "fill", "fit", "motion", "volume", "trim", "x", "y", "w", "h"];
    if (it.type === "bloco") {   // ✨ animação pronta (templates/blocos)
      const tx = p.textos || [];
      h += tx.length ? `<div class="sec"><h3>✏ Textos da animação</h3>` + tx.map((t, i) => field(`${b}.props.textos.${i}.para`, "bt", t.para ?? t.de, String(t.de).length > 42 ? String(t.de).slice(0, 42) + "…" : String(t.de))).join("") + `</div>`
        : `<p class="note">Esta animação não tem texto para trocar.</p>`;
      if (!BLOCOS) api("/api/blocos").then((r) => { BLOCOS = r.blocos || []; if (S.sel === it.id) renderProps(); }).catch(() => {});
      const vmeta = ((BLOCOS || []).find((x) => x.name === p.bloco) || {}).variables || [];
      for (const [k, v] of Object.entries(p.vars || {})) if (v === null || typeof v !== "object") h += field(`${b}.props.vars.${k}`, (vmeta.find((x) => x.id === k) || {}).type === "color" ? "color" : k, v ?? "", (vmeta.find((x) => x.id === k) || {}).label || k);
      h += `<div class="row"><div>${field(b + ".props.x", "x", p.x ?? Math.round(W() / 2), "Posição X (centro)")}</div><div>${field(b + ".props.y", "y", p.y ?? Math.round(H() / 2), "Posição Y (centro)")}</div></div>`;
      h += `<div class="row"><div>${field(b + ".props.scale", "bscale", +(p.scale ?? 1), "Tamanho (1 = normal)")}</div><div>${field(b + ".props.speed", "speed", +(p.speed ?? 1), "Velocidade (1 = normal)")}</div></div>`;
      h += field(b + ".props.fit", "fit", p.fit || "contain", "Encaixe na tela");
      h += `<p class="note">Animação pronta “${esc(p.bloco)}” (HyperFrames, licença Apache-2.0).</p>`;
    }
    const keys = it.type === "bloco" ? [] : Object.keys(p).filter((k) => !["words", "words_file", "params", "scene", "html", "css"].includes(k)).sort((a, b) => ((order.indexOf(a) + 1 || 99) - (order.indexOf(b) + 1 || 99)));
    for (const k of keys) if (!(it.type === "text" && k === "text")) h += field(`${b}.props.${k}`, k, p[k]);
    h += `<div class="sec">${field(b + ".label", "label", it.label || "", "Apelido do bloco na linha do tempo (não aparece no vídeo)")}</div>`;
    if (it.type === "html") h += field(`${b}.props.html`, "html", p.html || "", "HTML") + field(`${b}.props.css`, "css", p.css || "", "CSS");
    if (it.type === "image" && p.src) h += `<img src="${mediaUrl(p.src)}" style="width:100%;border-radius:8px">`;
  }
  P.innerHTML = h;
  $("#tabAll").onclick = () => { S.panel = "all"; renderProps(); };
  $("#tabSel").onclick = () => { S.panel = "sel"; renderProps(); };
  const bu = $("#busca"); if (bu) bu.oninput = () => { S.busca = bu.value; renderProps(); const nb = $("#busca"); nb.focus(); nb.setSelectionRange(nb.value.length, nb.value.length); };
  P.querySelectorAll("[data-go]").forEach((bt) => (bt.onclick = () => {
    const it = byId(bt.dataset.go); stopPlay(); setTime((+it.start || 0) + Math.min(0.6, (+it.dur || 1) / 2));
    S.sel = it.id; document.querySelectorAll(".blk").forEach((b) => b.classList.toggle("sel", b.dataset.key === it.id));
    const blk = document.querySelector(`.blk[data-key="${CSS.escape(it.id)}"]`); if (blk) blk.scrollIntoView({ block: "nearest", inline: "center" });
  }));
  P.querySelectorAll("[data-p]").forEach((el) => {
    const path = el.dataset.p;
    const ev = el.tagName === "SELECT" || el.type === "checkbox" || el.type === "color" ? "change" : "input";
    el.addEventListener(ev, () => {
      let v = el.type === "checkbox" ? el.checked : el.value;
      if (el.dataset.num) v = v === "" ? "" : +v;
      if (el.dataset.arr) v = v.split(",").map((s) => s.trim()).filter(Boolean);
      setP(path, v);
      if (el.dataset.color) { const t = el.parentElement.querySelector("input[type=text]"); if (t) t.value = v; }
      else if (el.type === "text" && el.parentElement.classList.contains("colorRow")) {   // código digitado → atualiza o quadradinho
        const m = String(v).trim().match(/^#?([0-9a-f]{3}|[0-9a-f]{6})$/i), sw = el.parentElement.querySelector("input[type=color]");
        if (m && sw) sw.value = "#" + (m[1].length === 3 ? m[1].split("").map((c) => c + c).join("") : m[1]).toLowerCase();
      }
      if (path.endsWith(".src")) { setupAudio(); probeSrc(v); }
      if (path === "edit.name") $("#projName").textContent = v;
      if (path === "edit.duration") $("#tdur").textContent = fmtT(DUR());
      if (el.type === "range") el.nextElementSibling && (el.nextElementSibling.textContent = Math.round(v * 100) + "%");
      if (ev === "change") { commit(true); renderTimeline(); if (el.tagName === "SELECT" && path.endsWith(".scene")) renderProps(); } else commitSoon();
    });
  });
  P.querySelectorAll("[data-pick]").forEach((bt) => (bt.onclick = () => pickFile((src) => { setP(bt.dataset.pick, src); setupAudio(); commit(true); renderProps(); renderTimeline(); })));
  P.querySelectorAll("[data-cap]").forEach((cw) => cw.addEventListener("input", () => {
    const it = items()[+cw.dataset.cap]; const ws = it.props.words; const nw = cw.value.trim().split(/\s+/);
    if (nw.length !== ws.length) { cw.style.borderColor = "#e5484d"; return; }
    cw.style.borderColor = ""; nw.forEach((w, i) => (ws[i].w = w)); commitSoon();
  }));
  const da = $("#delAudio"); if (da) da.onclick = delSel;
}
async function probeSrc() { try { const d = await api("/api/project/" + S.pid); S.durations = { ...S.durations, ...d.durations }; renderTimeline(); } catch (e) {} }

// ======================================================= ADICIONAR / APAGAR
function ensureTrack(id, name) {
  if (!S.edit.tracks.some((t) => t.id === id)) { if (id === "fundo") S.edit.tracks.unshift({ id, name }); else S.edit.tracks.push({ id, name }); }  // fundo = camada de baixo
  return id;
}
async function upload(file) {
  const fd = new FormData(); fd.append("file", file);
  toast("Enviando " + file.name + "…", 60000);
  const r = await api("/api/upload/" + S.pid, { method: "POST", body: fd });
  toast("✅ " + file.name); if (r.dur) S.durations[r.src] = r.dur;
  return r;
}
let pickCb = null;
function pickFile(cb, accept) { pickCb = cb; const fi = $("#fileIn"); fi.accept = accept || "image/*,video/*,audio/*"; fi.value = ""; fi.click(); }
$("#fileIn").onchange = async (e) => { const f = e.target.files[0]; if (!f || !pickCb) return; const r = await upload(f); pickCb(r.src, r, f); };
function addMediaItem(src, r, f) {
  const isVid = /^video\//.test(f.type) || /\.(mp4|mov|webm|mkv)$/i.test(src);
  const isAud = /^audio\//.test(f.type) || /\.(mp3|wav|m4a|ogg|aac)$/i.test(src);
  if (isAud) return addSfx(src, r);
  const it = { id: uid(isVid ? "vid" : "img"), type: isVid ? "video" : "image", track: ensureTrack("fundo", "Cenas / mídia"), label: f.name, start: +S.t.toFixed(2),
    dur: isVid && r.dur ? Math.min(r.dur, DUR() - S.t) : 4, in: "fade", out: "fade",
    props: { src, fill: true, fit: "cover", motion: isVid ? "none" : "zoom_in", ...(isVid ? { volume: 0, trim: 0 } : {}) } };
  items().push(it); commit(true); renderTimeline(); select(it.id);
}
function addSfx(src, r) {
  const a = S.edit.audio; a.extra = a.extra || [];
  const x = { id: uid("som"), src, start: +S.t.toFixed(2), volume: 0.5, label: src.split("/").pop() };
  a.extra.push(x); if (r?.dur) S.durations[src] = r.dur; setupAudio(); commit(true); renderTimeline(); select("audio:extra:" + x.id);
}
$("#btnAddText").onclick = () => {
  const it = { id: uid("txt"), type: "text", track: ensureTrack("textos", "Textos"), label: "Novo texto", start: +S.t.toFixed(2), dur: 3, in: "pop", out: "fade",
    props: { text: "NOVO TEXTO", x: Math.round(W() / 2), y: Math.round(H() * 0.75), size: Math.round(Math.min(W(), H()) * 0.07), color: "#ffffff", weight: 900, bg: "rgba(0,0,0,.6)", font: "Inter" } };
  items().push(it); commit(true); renderTimeline(); select(it.id);
};
$("#btnAddMedia").onclick = () => pickFile(addMediaItem, "image/*,video/*");
$("#btnAddMusic").onclick = () => pickFile((src, r) => { S.edit.audio.music = { src, volume: 0.12, start: 0, fade_out: 2, duck: true }; if (r.dur) S.durations[src] = r.dur; setupAudio(); commit(true); renderTimeline(); select("audio:music"); }, "audio/*");
$("#btnAddSfx").onclick = () => openSomLivre();
function openSomLivre() {
  if (!S.edit) return toast("Abra um vídeo primeiro");
  modal("🔊 Adicionar som");
  $("#mMsg").innerHTML = `
    <p style="margin:0 0 8px">Procure um som livre (CC0 / CC BY) e clique em <b>➕ Usar</b> — ele entra no ponto vermelho da linha do tempo, com o crédito guardado.</p>
    <div style="display:flex;gap:8px;margin-bottom:8px">
      <input id="somQ" placeholder="ex.: whoosh, aplausos, chuva, moeda, risada" style="flex:1;padding:7px 10px;border-radius:9px;border:1px solid #bbb">
      <button class="btn go" id="somGo">🔎 Buscar</button>
    </div>
    <div id="somRes" class="somRes">Digite acima e busque — ou suba um arquivo do seu PC.</div>`;
  const buscar = async () => {
    const q = $("#somQ").value.trim(); if (!q) return;
    $("#somRes").innerHTML = "Procurando…";
    try {
      const d = await api("/api/som/buscar?q=" + encodeURIComponent(q));
      const its = d.itens || [];
      if (!its.length) { $("#somRes").innerHTML = "Nada encontrado. Tente outra palavra (em inglês acha mais: whoosh, applause, rain…)."; return; }
      $("#somRes").innerHTML = its.map((it, i) => `
        <div class="somIt">
          <audio controls preload="none" src="${esc(it.preview)}" style="height:30px"></audio>
          <div class="somInfo"><b>${esc(it.titulo)}</b><small>${esc(it.dur || "?")}s · ${esc(it.licenca)} · ${esc(it.fonte)}</small></div>
          <button class="btn mini go" data-usar="${i}">➕ Usar</button>
        </div>`).join("");
      $("#somRes").querySelectorAll("[data-usar]").forEach((b) => b.onclick = async () => {
        b.disabled = true; b.textContent = "baixando…";
        try {
          const r = await api("/api/som/baixar/" + S.pid, { method: "POST", body: JSON.stringify(its[+b.dataset.usar]) });
          addSfx(r.src, { dur: r.dur }); closeModal();
          toast("✅ Som adicionado (crédito guardado em sons/creditos.json)", 5000);
        } catch (e) { b.disabled = false; b.textContent = "➕ Usar"; toast("❌ " + errTxt(e), 6000); }
      });
    } catch (e) { $("#somRes").innerHTML = "Não consegui buscar agora: " + errTxt(e); }
  };
  mbtn("📁 Subir do PC", () => { closeModal(); pickFile((src, r) => addSfx(src, r), "audio/*"); });
  mbtn("Fechar", closeModal);
  setTimeout(() => { const q = $("#somQ"); q.focus(); q.onkeydown = (e) => { if (e.key === "Enter") buscar(); }; $("#somGo").onclick = buscar; }, 30);
}
// ---- ✨ Animações prontas (blocos do registry HyperFrames em templates/blocos/ — ver FORMATO.md, tipo "bloco")
let BLOCOS = null, BLOCOS_CAT = "Todas";
async function abrirBlocos() {
  if (!S.edit) return toast("Abra um vídeo primeiro");
  $("#blocosModal").classList.remove("hidden");
  if (!BLOCOS) {
    $("#blocosGrid").innerHTML = '<p class="note">Carregando…</p>';
    try { BLOCOS = (await api("/api/blocos")).blocos || []; } catch (e) { $("#blocosGrid").innerHTML = '<p class="note">Não consegui listar as animações.</p>'; return; }
  }
  renderBlocos();
}
function renderBlocos() {
  const cats = ["Todas", ...new Set(BLOCOS.map((b) => b.categoria))];
  $("#blocosCats").innerHTML = cats.map((c) => `<button class="btn mini ${c === BLOCOS_CAT ? "ok" : ""}" data-bcat="${esc(c)}">${esc(c)}</button>`).join("");
  const lista = BLOCOS.filter((b) => BLOCOS_CAT === "Todas" || b.categoria === BLOCOS_CAT);
  $("#blocosGrid").innerHTML = lista.length ? lista.map((b) => `<div class="bcard">${b.thumb ? `<img loading="lazy" src="${b.thumb}" alt="">` : `<div class="bsem">✨</div>`}
    <div class="bin"><span class="bcat">${esc(b.categoria)} · ${(+b.duration).toFixed(1)} s</span><b>${esc(b.titulo)}</b><span class="bdesc">${esc(b.descricao)}</span>
    <button class="btn ok" data-bins="${esc(b.name)}">➕ Inserir na cena</button></div></div>`).join("") : '<p class="note">Nenhuma animação instalada (pasta templates/blocos vazia).</p>';
  document.querySelectorAll("[data-bcat]").forEach((bt) => (bt.onclick = () => { BLOCOS_CAT = bt.dataset.bcat; renderBlocos(); }));
  document.querySelectorAll("[data-bins]").forEach((bt) => (bt.onclick = () => inserirBloco(bt.dataset.bins)));
}
function inserirBloco(name) {
  const b = (BLOCOS || []).find((x) => x.name === name); if (!b) return;
  const st = +Math.max(0, Math.min(S.t, DUR() - 0.5)).toFixed(2);
  const dur = +Math.max(0.5, Math.min(+b.duration || 4, DUR() - st)).toFixed(2);
  const it = { id: uid("anim"), type: "bloco", track: ensureTrack("visual", "Gráficos"), label: b.titulo, start: st, dur, in: "none", out: "none",
    props: { bloco: b.name, x: Math.round(W() / 2), y: Math.round(H() / 2), scale: 1, fit: "contain", speed: 1,
      textos: (b.textos || []).map((t) => ({ de: t, para: t })), vars: Object.fromEntries((b.variables || []).map((v) => [v.id, v.default ?? ""])) } };
  items().push(it); commit(true); renderTimeline(); select(it.id);
  $("#blocosModal").classList.add("hidden"); toast("✨ " + b.titulo + " inserida em " + fmt(st));
}
$("#btnAddBloco").onclick = abrirBlocos;
$("#blocosClose").onclick = () => $("#blocosModal").classList.add("hidden");
$("#blocosModal").onclick = (e) => { if (e.target.id === "blocosModal") $("#blocosModal").classList.add("hidden"); };
function delSel() {
  const k = S.sel; if (!k) return toast("Selecione algo primeiro");
  if (k === "audio:voice") return toast("A voz não pode ser apagada (use Sem som)");
  if (k === "audio:music") delete S.edit.audio.music;
  else if (k.startsWith("audio:extra:")) S.edit.audio.extra = S.edit.audio.extra.filter((x) => "audio:extra:" + x.id !== k);
  else { const it = byId(k); if (it?.by === "template") { it.hidden = true; toast("Elemento do modelo: foi escondido (dá pra mostrar de novo)"); } else S.edit.items = items().filter((i) => i.id !== k); }
  S.sel = null; setupAudio(); commit(true); renderTimeline(); renderProps();
}
$("#btnDel").onclick = delSel;
function splitSel() {
  if (S.sel && String(S.sel).startsWith("audio:")) return toast("Voz, música e sons não podem ser cortados aqui — selecione um bloco de texto, foto, vídeo ou cena");
  const it = S.sel && byId(S.sel);
  if (!it) return toast("Clique num bloco (texto, foto, vídeo, cena) e ponha a linha vermelha onde quer cortar");
  if (it.by === "template") return toast("Elemento do modelo não pode ser cortado — mude início/duração");
  const t = +S.t.toFixed(3), s = +it.start, e = s + +it.dur;
  if (t <= s + 0.05 || t >= e - 0.05) return toast("Ponha a linha vermelha DENTRO do bloco para cortar");
  const c = JSON.parse(JSON.stringify(it));
  c.id = uid(it.type.slice(0, 3)); c.start = t; c.dur = +(e - t).toFixed(3); c.label = (it.label || it.type) + " (2)";
  if (it.type === "video") c.props.trim = +((+(it.props.trim || 0)) + (t - s) * (+(it.props.speed || 1))).toFixed(3);
  it.dur = +(t - s).toFixed(3); it.out = "none"; c.in = "none";
  items().splice(items().indexOf(it) + 1, 0, c); commit(true); renderTimeline(); select(c.id); toast("✂ Cortado");
}
$("#btnSplit").onclick = splitSel;
S.magnet = true;
$("#btnMagnet").onclick = () => { S.magnet = !S.magnet; $("#btnMagnet").classList.toggle("ok", S.magnet); toast(S.magnet ? "Ímã ligado (gruda nas bordas)" : "Ímã desligado"); };
$("#btnDup").onclick = () => {
  const k = S.sel; const o = getTimed(k); if (!o || k.startsWith("audio:voice") || k === "audio:music") return toast("Selecione um item para duplicar");
  const c = JSON.parse(JSON.stringify(o));
  if (k.startsWith("audio:extra:")) { c.id = uid("som"); c.start = +(c.start + 1).toFixed(2); S.edit.audio.extra.push(c); setupAudio(); commit(true); renderTimeline(); return select("audio:extra:" + c.id); }
  if (o.by === "template") return toast("Elementos do modelo não podem ser duplicados");
  c.id = uid(o.type.slice(0, 3)); c.start = +(o.start + o.dur).toFixed(2); c.label = (o.label || "") + " (cópia)";
  items().push(c); commit(true); renderTimeline(); select(c.id);
};
// arrastar arquivo do PC
const stage = $("#stage");
["dragover", "dragenter"].forEach((ev) => document.addEventListener(ev, (e) => { if (S.edit && !$("#editor").classList.contains("hidden")) { e.preventDefault(); stage.classList.add("drop"); } }));
document.addEventListener("dragleave", (e) => { if (!e.relatedTarget) stage.classList.remove("drop"); });
document.addEventListener("drop", async (e) => {
  stage.classList.remove("drop"); if (!S.edit) return; e.preventDefault();
  for (const f of e.dataTransfer.files) {
    const r = await upload(f); const it = S.sel && byId(S.sel);
    if (it && ["image", "video"].includes(it.type) && /^(image|video)\//.test(f.type) && confirm("Trocar a mídia selecionada por " + f.name + "?\n(Cancelar = adicionar como nova)")) {
      it.props.src = r.src; if (/^video\//.test(f.type)) it.type = "video"; else it.type = "image"; commit(true); renderProps(); renderTimeline();
    } else addMediaItem(r.src, r, f);
  }
});

// ======================================================= RENDER
function modal(title) { $("#modal").classList.remove("hidden", "semBarra"); document.querySelectorAll("#modal .revBox, #modal .mX, #modal .medicoAviso, #modal .capaPrev").forEach((x) => x.remove()); $("#mTitle").textContent = title; $("#mBar").style.width = "0%"; $("#mMsg").textContent = ""; $("#mBtns").innerHTML = ""; }
// botão que BAIXA um arquivo (funciona no celular: o navegador salva o mp4 no aparelho)
function mlink(label, href, nome, cls = "") { const a = document.createElement("a"); a.className = "btn big " + cls; a.textContent = label; a.href = href; a.setAttribute("download", nome); $("#mBtns").appendChild(a); return a; }
// "✕" fixo no canto do aviso: sempre alcançável, mesmo com o aviso comprido no celular
function mfecharX() { const b = document.createElement("button"); b.className = "mX"; b.type = "button"; b.title = "Fechar"; b.textContent = "✕"; b.onclick = closeModal; document.querySelector("#modal .mbox").prepend(b); }
function mbtn(label, fn, cls = "") { const b = document.createElement("button"); b.className = "btn big " + cls; b.textContent = label; b.onclick = fn; $("#mBtns").appendChild(b); }
// 🖼 Criar capa (Instagram 9:16) + descricao.txt (títulos, descrição, 5 hashtags) — botão da tela "Vídeo pronto"
// ⬇ Baixar leve / final na tela "Vídeo pronto" (o leve é criado na hora se ainda não existir)
function mlinksBaixar(pid, nome) {
  if (!pid || $("#mBtns").querySelector("[data-mbaixar]")) return;
  const n = String(nome || "video").replace(/[\/:*?"<>|]+/g, " ").trim().slice(0, 80) || "video";
  mlink("Baixar leve", `/api/baixar/${pid}/leve`, `${n} - leve.mp4`, "go");
  mlink("Baixar final", `/api/baixar/${pid}/final`, `${n} - final.mp4`);
  $("#mBtns").querySelectorAll("a.btn").forEach((a) => (a.dataset.mbaixar = "1"));
}
// Ver o vídeo aqui mesmo, dentro da janela (funciona no celular); clicar de novo esconde
function mbtnVer(pid, cls = "") {
  mbtn("Ver o vídeo", (ev) => {
    const msg = $("#mMsg"), ja = msg.querySelector("video.mVid");
    if (ja) { ja.pause(); ja.remove(); ev.currentTarget.textContent = "Ver o vídeo"; return; }
    const v = document.createElement("video");
    v.src = `/api/baixar/${pid}/${matchMedia("(max-width:760px)").matches ? "leve" : "final"}?inline=1`;
    v.controls = true; v.autoplay = true; v.playsInline = true; v.className = "mVid";
    msg.appendChild(v); ev.currentTarget.textContent = "Esconder o vídeo";
  }, cls);
}
function mbtnCapa(pid) { if (pid && !$("#mBtns").querySelector("[data-mcapa]")) { mbtn("Criar capa", () => criarCapa(pid)); $("#mBtns").lastElementChild.dataset.mcapa = "1"; } }
// janelinha que pergunta título e canal antes de criar a capa (vazio = título automático / sem canal)
// tipos de capa disponíveis (por enquanto só um; novos entram aqui + em TIPOS no capa.py + exemplos em static/capa-exemplos/<id>-16x9.jpg e -9x16.jpg)
const CAPA_TIPOS = [{ id: "investigacao", nome: "Investigação" }, { id: "curiosidade", nome: "Curiosidade" }];
function criarCapa(pid) {
  modal("🖼 Criar capa");
  $("#modal").classList.add("semBarra");
  $("#mMsg").textContent = "";
  const f = document.createElement("div"); f.className = "capaPrev capaForm";
  f.innerHTML = `<label>Tipo de capa<select id="capaTipo">${CAPA_TIPOS.map((t) => `<option value="${t.id}">${t.nome}</option>`).join("")}</select></label>
    <div class="capaEx" id="capaEx"></div>
    <label>Título da capa <small>(deixe vazio para o título automático)</small><input id="capaTitulo" type="text" maxlength="140" placeholder="Ex.: Por que a água-viva nunca morre?"></label>
    <label>Nome do canal <small>(aparece no canto superior direito, do jeito que você escrever; vazio = nada)</small><input id="capaCanal" type="text" maxlength="40" placeholder="Ex.: História e Filosofia"></label>
    <label>O que aparece na imagem <small>(a IA local procura essa cena dentro do vídeo — ex.: "a cama", "a casa vista de frente"; vazio = automático)</small><input id="capaCena" type="text" maxlength="200" placeholder="Ex.: a casa vista de cima"></label>`;
  $("#mBtns").before(f);
  const mostrarEx = () => {   // exemplo 16:9 e 9:16 do tipo escolhido
    const t = CAPA_TIPOS.find((x) => x.id === $("#capaTipo").value) || CAPA_TIPOS[0];
    $("#capaEx").innerHTML = `<figure><img src="/static/capa-exemplos/${t.id}-16x9.jpg" alt="Exemplo 16:9"><figcaption>Exemplo 16:9</figcaption></figure><figure class="v"><img src="/static/capa-exemplos/${t.id}-9x16.jpg" alt="Exemplo 9:16"><figcaption>Exemplo 9:16</figcaption></figure>`;
  };
  $("#capaTipo").onchange = mostrarEx; mostrarEx();
  const ir = () => { const tipo = $("#capaTipo").value, titulo = $("#capaTitulo").value.trim(), canal = $("#capaCanal").value.trim(), cena = $("#capaCena").value.trim(); f.remove(); capaGerar(pid, titulo, canal, tipo, cena); };
  mbtn("Cancelar", closeModal, "capaNo");
  mbtn("Confirmar", ir, "capaSim");
  f.addEventListener("keydown", (e) => { if (e.key === "Enter") { e.preventDefault(); ir(); } });
  setTimeout(() => $("#capaTitulo").focus(), 30);
}
async function capaGerar(pid, titulo, canal, tipo, cena = "") {
  {
    $("#modal").classList.remove("semBarra");
    let r; try { r = await jpost(`/api/capa/${pid}`, { titulo, canal, tipo, cena }); } catch (e) { return toast("❌ " + errTxt(e), 6000); }
    acompanhar(r.job, "🖼 Criando a capa…", (res, fechado) => {
      if (fechado) return toast("✅ Capa e descricao.txt prontas na pasta do vídeo.", 6000);
      $("#mTitle").textContent = "✅ Capa pronta!";
      const t = res.texto || {};
      $("#mMsg").textContent = `Tipo de capa: ${(CAPA_TIPOS.find((x) => x.id === tipo) || CAPA_TIPOS[0]).nome}\ncapa_instagram.jpg + descricao.txt\n${res.cena ? "\n🔎 Você pediu: “" + res.cena + "”\n" + (res.aviso_cena || "") + "\n" : (cena ? "\n⚠ O pedido de cena não chegou ao servidor (recarregue a página com Ctrl+F5).\n" : "")}\nTítulos:\n${(t.titulos || []).map((x) => "• " + x).join("\n")}\n\n${(t.hashtags || []).join(" ")}\n\n📁 ${amigavel(res.folder)}`;
      const im = document.createElement("img"); im.src = res.capa_url + "?t=" + Date.now(); im.alt = "capa"; im.className = "capaPrev"; im.style.cssText = "max-height:340px;max-width:100%;border-radius:10px;margin:8px auto;display:block";
      $("#mBtns").before(im);
      mlink("⬇ Baixar capa", `/api/baixar/${pid}/capa`, "capa.jpg", "go");
      mlink("⬇ Baixar descrição", `/api/baixar/${pid}/descricao`, "descricao.txt", "go");
      mbtn("🖼 Abrir capa", () => api(`/api/open/${pid}?what=capa`, { method: "POST" }));
      mbtn("📝 Abrir descricao.txt", () => api(`/api/open/${pid}?what=descricao`, { method: "POST" }));
      mbtn("📂 Abrir pasta", () => api(`/api/open/${pid}?what=folder`, { method: "POST" }));
      mbtn("Fechar", closeModal);
    });
  }
}
const closeModal = () => { document.querySelectorAll("#modal video").forEach((v) => { try { v.pause(); } catch (e) { } }); $("#modal").classList.add("hidden"); };
// ▶ Assistir dentro da própria página (no celular o "abrir no PC" não serve). Usa o leve em tela estreita, se existir.
function assistirAqui(pid, titulo, temLeve) {
  const which = temLeve && matchMedia("(max-width:760px)").matches ? "leve" : "final";
  modal(String(titulo || "Assistir").slice(0, 70)); $("#modal").classList.add("semBarra");
  const v = document.createElement("video"); v.src = `/api/baixar/${pid}/${which}?inline=1`; v.controls = true; v.autoplay = true; v.playsInline = true; v.className = "mVid";
  $("#mMsg").replaceChildren(v);
  mfecharX();
  if (temLeve) mlink("⬇ Baixar leve", `/api/baixar/${pid}/leve`, "leve.mp4", "go");
  mlink("⬇ Baixar final", `/api/baixar/${pid}/final`, "final.mp4");
  mbtn("Fechar", closeModal);
}
async function runJob(url, title, onDone) {
  stopPlay(); await save();
  let job; try { ({ job } = await api(url, { method: "POST" })); } catch (e) { return toast("❌ " + errTxt(e), 6000); }
  acompanhar(job, title, (res, fechado) => { if (fechado) return toast("✅ " + title.replace(/…$/, "") + ": pronto!", 6000); onDone(res); });
}
$("#btnRender").onclick = () => runJob("/api/render/" + S.pid, "Renderizando o vídeo…", (r) => {
  $("#mTitle").textContent = "✅ Vídeo pronto!";
  $("#mMsg").textContent = `final.mp4 — ${r.final_mb} MB\nleve.mp4 — ${r.leve_mb} MB (para mandar/postar)\n\n📁 ${S.pastaNome || amigavel(S.folder)}`;
  const nomeArq = String(S.pastaNome || "video").replace(/[\\/:*?"<>|]+/g, " ").trim().slice(0, 80) || "video";
  mfecharX();
  mbtn("▶ Assistir", () => assistirAqui(S.pid, S.pastaNome, !!r.leve_mb), "go");
  mbtnCapa(S.pid);
  if (r.leve_mb) mlink(`⬇ Baixar leve (${r.leve_mb} MB)`, `/p/${S.pid}/leve.mp4`, `${nomeArq} - leve.mp4`, "go");
  mlink(`⬇ Baixar final (${r.final_mb} MB)`, `/p/${S.pid}/final.mp4`, `${nomeArq} - final.mp4`);
  mbtn("📂 Abrir pasta", () => api(`/api/open/${S.pid}?what=folder`, { method: "POST" }));
  medicoAvisar(S.pid, r.medico);
  mbtn("Fechar", closeModal);
});

// 🩺 Médico do render: avisa se achou tela preta / frame congelado e oferece o conserto automático.
function medicoAvisar(pid, med) {
  if (!med || !med.problemas) return;
  const linha = document.createElement("div");
  linha.className = "medicoAviso";
  linha.textContent = `🩺 Achei ${med.problemas} ponto(s) pra olhar no vídeo (tela preta / frame congelado).`;
  $("#mMsg").after(linha);
  mbtn("🩺 Ver o que achei", () => medicoVer(pid));
  if (med.corrigiveis > 0)
    mbtn(`🔧 Consertar sozinho (${med.corrigiveis})`, () => medicoConsertar(pid), "go");
}
async function medicoVer(pid) {
  let d; try { d = await api("/api/medico/" + pid); } catch (e) { return toast("❌ " + errTxt(e), 6000); }
  const ps = d.problemas || [];
  alert(ps.length ? ps.map((p, i) => `${i + 1}. ${p.corrigivel ? "🔧" : "⚠️"} ${p.texto}`).join("\n\n")
                  : "✅ Nenhum defeito acima do limite.");
}
function medicoConsertar(pid) {
  if (!confirm("Vou arrumar o que der sozinho (desacelerar clipe que travou, cortar sobra preta no fim) e gerar o vídeo de novo. Leva o mesmo tempo da primeira vez. Continuar?")) return;
  runJob(`/api/medico/${pid}/corrigir`, "Consertando o vídeo…", (r) => {
    $("#mTitle").textContent = r.mudou ? "✅ Consertado e gerado de novo!" : "Nada pra consertar sozinho";
    $("#mMsg").textContent = (r.consertos && r.consertos.length ? r.consertos.map((c) => "• " + c).join("\n") + "\n\n" : "")
      + (r.medico ? `Agora restam ${r.medico.problemas} ponto(s) (${r.medico.corrigiveis} ainda automáticos).` : "");
    mbtnVer(pid, "go");
    medicoAvisar(pid, r.medico);
    mbtn("Fechar", closeModal);
  });
}
$("#btnFolder").onclick = () => api(`/api/open/${S.pid}?what=folder`, { method: "POST" });

// 🧮 Densidade — "Suas regras": medir e segurar o excesso de gráfico/animação (reversível).
$("#btnDens").onclick = () => openDensidade();
function openDensidade() {
  const r = (S.edit && S.edit.regras) || {};
  const reg = (typeof r === "object" && !Array.isArray(r)) ? r : {};   // listas antigas viram dict ao salvar aqui
  modal("🧮 Densidade de gráficos");
  $("#mMsg").innerHTML = `
    <p style="margin:0 0 10px">Suas regras limitam a animação por cima do vídeo. <b>Legenda e footage nunca são mexidos.</b></p>
    <label class="densL"><input type="checkbox" id="dBroll" ${reg.broll_primeiro ? "checked" : ""}> B-roll primeiro (imagem real, gráfico só de destaque)</label>
    <label class="densL"><input type="checkbox" id="dSem" ${reg.sem_animacao ? "checked" : ""}> Sem animações (só legenda e footage)</label>
    <label class="densL">Máx. 1 gráfico a cada <input type="number" id="dInt" min="1" max="30" step="1" value="${reg.intervalo_min || 7}" style="width:56px"> s</label>
    <label class="densL">No máximo <input type="number" id="dPct" min="5" max="100" step="5" value="${reg.max_pct || 25}" style="width:56px"> % da tela com gráfico</label>
    <div id="dMed" class="densMed">—</div>`;
  const colher = () => ({
    broll_primeiro: $("#dBroll").checked, sem_animacao: $("#dSem").checked,
    intervalo_min: Math.max(1, +$("#dInt").value || 7), max_pct: Math.max(5, +$("#dPct").value || 25),
  });
  const medir = async () => {
    try { await save(); } catch (e) { return; }
    try { const d = await api("/api/densidade/" + S.pid); const m = d.medida;
      $("#dMed").textContent = `Agora: ${m.n_graficos} gráficos · ${m.pct_grafico}% da tela · menor intervalo ${m.menor_intervalo ?? "—"}s · ${m.colados} colados.`;
    } catch (e) { $("#dMed").textContent = "Não consegui medir: " + errTxt(e); }
  };
  mbtn("📊 Medir agora", medir);
  mbtn("💾 Salvar regras", async () => { S.edit.regras = colher(); commit(); try { await save(); toast("✅ Regras salvas (valem no próximo render)"); } catch (e) {} });
  mbtn("🔧 Aplicar agora (esconde o excesso)", async () => {
    S.edit.regras = colher(); commit();
    try { await save(); } catch (e) { return; }
    try { const res = await api(`/api/densidade/${S.pid}/aplicar`, { method: "POST" });
      closeModal(); await openProject(S.pid);
      toast(`✅ ${res.derrubados.length} gráfico(s) escondido(s). Gráfico: ${res.antes.pct_grafico}% → ${res.depois.pct_grafico}%. (dá pra reexibir cada um na linha do tempo)`, 7000);
    } catch (e) { toast("❌ " + errTxt(e), 6000); }
  }, "go");
  mbtn("Fechar", closeModal);
  medir();
}

// ======================================================= TECLADO
function onKey(e) {
  if (!S.edit || $("#editor").classList.contains("hidden")) return;
  const typing = /INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName);
  if (e.ctrlKey && e.key.toLowerCase() === "s") { e.preventDefault(); save(); return; }
  if (typing) return;
  if (e.key === "Escape" && !$("#kbModal").classList.contains("hidden")) return $("#kbModal").classList.add("hidden");
  if (e.altKey || e.metaKey) return;
  const k = e.key.toLowerCase(), fr = 1 / FPS();
  if (e.ctrlKey && k === "z") { e.preventDefault(); undo(); }
  else if (e.ctrlKey && k === "y") { e.preventDefault(); redo(); }
  else if (e.ctrlKey) return;
  else if (e.key === " " || k === "k") { e.preventDefault(); play(); }
  else if (e.key === "Delete") delSel();
  else if (k === "s") splitSel();
  else if (k === "j") seekTo(S.t - 10);
  else if (k === "l") seekTo(S.t + 10);
  else if (k === "m") toggleMute();
  else if (k === "f") toggleFull();
  else if (e.key === "?") $("#kbModal").classList.toggle("hidden");
  else if (e.key === "ArrowRight") { e.preventDefault(); seekTo(S.t + (e.shiftKey ? 5 : fr)); }
  else if (e.key === "ArrowLeft") { e.preventDefault(); seekTo(S.t - (e.shiftKey ? 5 : fr)); }
  else if (e.key === ".") seekTo(S.t + fr);
  else if (e.key === ",") seekTo(S.t - fr);
  else if (e.key === "Home") { e.preventDefault(); seekTo(0); }
  else if (e.key === "End") { e.preventDefault(); seekTo(DUR()); }
  else if (e.key === "PageUp" || e.key === "[") { e.preventDefault(); gotoBlock(-1); }
  else if (e.key === "PageDown" || e.key === "]") { e.preventDefault(); gotoBlock(1); }
}
document.addEventListener("keydown", onKey);
// teclas apertadas com o foco dentro da prévia (iframe) chegam por mensagem
window.addEventListener("message", (e) => { const m = e.data || {}; if (m.ed === "key") onKey({ key: m.key, ctrlKey: !!m.ctrlKey, shiftKey: !!m.shiftKey, altKey: !!m.altKey, metaKey: !!m.metaKey, preventDefault() {} }); });
window.addEventListener("beforeunload", (e) => { if (S.dirty) { e.preventDefault(); e.returnValue = ""; } });
// (a primeira tela — Início — abre no fim do arquivo, depois de tudo definido)

// ======================================================= VELOCIDADE + RELATÓRIO
S.speed = 1;
const SPEEDS = [0.25, 0.5, 1, 1.5, 2, 3, 4];
$("#btnSpeed").onclick = () => {
  S.speed = SPEEDS[(SPEEDS.indexOf(S.speed) + 1) % SPEEDS.length];
  $("#btnSpeed").textContent = "⏩ " + S.speed + "x" + (S.speed > 2 ? " (mudo)" : "");
  if (S.playing) { t0 = S.t; n0 = performance.now(); }
  syncAudio(S.playing);
};
$("#btnRel").onclick = () => window.open("/relatorio?pid=" + S.pid, "_blank");
document.addEventListener("click", (e) => {
  const b = e.target.closest("[data-rel]");
  if (b) { e.stopPropagation(); window.open("/relatorio?pid=" + b.dataset.rel, "_blank"); }
  const r = e.target.closest("[data-ref]");
  if (r) { e.stopPropagation(); window.open(r.dataset.ref, "_blank"); }
}, true);

$("#btnRef").onclick = () => { const r = S.edit.referencia || {}; if (r.video) window.open(r.video, "_blank"); else { S.sel = null; S.panel = "sel"; renderProps(); toast("Preencha o link do vídeo copiado em Ajustes do vídeo"); } };

// ======================================================= CONTROLES DO PLAYER (mudo, volume, tela cheia, loop, navegação, zoom, captura, atalhos)
S.tcMode = localStorage.getItem("ed_tc") || "frames";
S.vol = Math.max(0, Math.min(1, +(localStorage.getItem("ed_vol") ?? 1)));
S.volVoice = 1; S.volMusic = 1; S.muted = false; S.loop = false;
const clampT = (t) => Math.max(0, Math.min(DUR(), t));
// pula para t sem parar a reprodução (se estiver tocando, continua de lá)
function seekTo(t) {
  t = clampT(t);
  if (S.playing) { t0 = t; n0 = performance.now(); setTime(t, true); seekFrame(front, t, true); syncAudio(true); }
  else setTime(t);
}
// ---- tempo: clique alterna mm:ss.ff ↔ segundos
$("#tcur").onclick = () => { S.tcMode = S.tcMode === "sec" ? "frames" : "sec"; localStorage.setItem("ed_tc", S.tcMode); if (S.edit) { $("#tcur").textContent = fmtT(S.t); $("#tdur").textContent = fmtT(DUR()); } toast(S.tcMode === "sec" ? "Tempo em segundos" : "Tempo em minutos:segundos.quadros"); };
// ---- mudo / volume
function setVol(v) {
  S.vol = Math.max(0, Math.min(1, v)); localStorage.setItem("ed_vol", S.vol);
  $("#vol").value = Math.round(S.vol * 100); $("#volTxt").textContent = Math.round(S.vol * 100) + "%";
  if (S.edit) syncAudio(S.playing);
}
function toggleMute(force) {
  S.muted = force != null ? !!force : !S.muted;
  $("#btnMute").textContent = S.muted ? "🔇" : "🔊"; $("#btnMute").classList.toggle("on", S.muted);
  $("#btnMute").title = S.muted ? "Mudo ligado — clique para ouvir de novo (M)" : "Mudo: liga/desliga o som da prévia (M)";
  if (S.edit) syncAudio(S.playing);
}
$("#btnMute").onclick = () => toggleMute();
$("#vol").oninput = (e) => setVol(e.target.value / 100);
$("#btnVolDown").onclick = () => setVol(Math.round(S.vol * 10) / 10 - 0.1);
$("#btnVolUp").onclick = () => setVol(Math.round(S.vol * 10) / 10 + 0.1);
$("#volVoice").oninput = (e) => { S.volVoice = e.target.value / 100; if (S.edit) syncAudio(S.playing); };
$("#volMusic").oninput = (e) => { S.volMusic = e.target.value / 100; if (S.edit) syncAudio(S.playing); };
setVol(S.vol);
// ---- tela cheia da prévia
function toggleFull() {
  if (document.fullscreenElement) { document.exitFullscreen?.(); return; }
  const p = $("#stage").requestFullscreen?.();
  if (!p) return toast("Tela cheia não disponível neste navegador");
  p.catch(() => toast("Não consegui abrir em tela cheia (clique no botão ⛶ pra tentar)"));
}
$("#btnFull").onclick = toggleFull;
document.addEventListener("fullscreenchange", () => { const on = !!document.fullscreenElement; $("#btnFull").classList.toggle("on", on); $("#btnFull").title = on ? "Sair da tela cheia (F ou Esc)" : "Tela cheia da prévia (F) — Esc sai"; if (S.edit) setTimeout(fitStage, 60); });
// ---- loop do bloco selecionado (ou do vídeo inteiro)
function loopRange() {
  if (!S.loop || !S.edit) return null;
  const o = S.sel && getTimed(S.sel);
  if (o && o.start != null) { const s = +o.start || 0, d = +o.dur || S.durations[o.src] || 0; if (d > 0.1 && s < DUR()) return [s, Math.min(DUR(), s + d)]; }
  return [0, DUR()];
}
function setLoop(v) {
  S.loop = !!v; $("#btnLoop").classList.toggle("on", S.loop);
  $("#btnLoop").title = S.loop ? "Repetir ligado: toca de novo o bloco selecionado (ou o vídeo inteiro). Clique para desligar" : "Repetir: toca de novo o bloco selecionado (ou o vídeo inteiro se nada estiver selecionado)";
}
$("#btnLoop").onclick = () => { setLoop(!S.loop); if (S.loop) { const lr = loopRange(); toast(lr && (lr[1] - lr[0] < DUR() - 0.01) ? `🔁 Repetindo o bloco ${fmtT(lr[0])} → ${fmtT(lr[1])}` : "🔁 Repetindo o vídeo inteiro"); } else toast("Repetir desligado"); };
// ---- início / fim / bloco anterior / próximo
function blockStarts() {
  const a = S.edit.audio || {}; const out = [];
  if (a.voice?.src) out.push({ key: "audio:voice", t: +a.voice.start || 0 });
  if (a.music?.src) out.push({ key: "audio:music", t: +a.music.start || 0 });
  (a.extra || []).forEach((x) => out.push({ key: "audio:extra:" + x.id, t: +x.start || 0 }));
  items().forEach((i) => { if (i.type !== "param" && i.start != null) out.push({ key: i.id, t: +i.start || 0 }); });
  return out.sort((x, y) => x.t - y.t);
}
function gotoBlock(dir) {
  const L = blockStarts(); if (!L.length) return toast("Este vídeo não tem blocos");
  const b = dir > 0 ? L.find((x) => x.t > S.t + 0.02) : [...L].reverse().find((x) => x.t < S.t - 0.02);
  if (!b) return toast(dir > 0 ? "Já está no último bloco" : "Já está no primeiro bloco");
  seekTo(b.t); select(b.key);
  const blk = document.querySelector(`.blk[data-key="${CSS.escape(b.key)}"]`); if (blk) blk.scrollIntoView({ block: "nearest", inline: "center" });
}
$("#btnHome").onclick = () => seekTo(0);
$("#btnEnd").onclick = () => seekTo(DUR());
$("#btnPrevBlk").onclick = () => gotoBlock(-1);
$("#btnNextBlk").onclick = () => gotoBlock(1);
// ---- zoom da linha do tempo
function setZoom(pps) {
  S.pps = Math.max(5, Math.min(300, pps)); $("#zoom").value = S.pps; renderTimeline();
  const tl = $("#timeline"); tl.scrollLeft = Math.max(0, S.t * S.pps - (tl.clientWidth - 150) / 2);
}
$("#btnZoomIn").onclick = () => setZoom(S.pps * 1.25);
$("#btnZoomOut").onclick = () => setZoom(S.pps / 1.25);
$("#btnZoomFit").onclick = () => { setZoom(($("#timeline").clientWidth - 170) / DUR()); $("#timeline").scrollLeft = 0; };
// ---- capturar quadro (PNG do frame atual)
async function captureFrame() {
  if (!S.edit) return;
  const b = $("#btnCapture"); b.disabled = true; const old = b.textContent; b.textContent = "📷 Capturando…";
  try {
    const w = front.contentWindow;
    if (!w || !w.__edCapture) throw new Error("preview sem captura");
    const url = await w.__edCapture();
    if (!url || !url.startsWith("data:image/png")) throw new Error("sem imagem");
    const name = String(S.edit.name || S.pid).replace(/[\/:*?"<>|]+/g, " ").trim().slice(0, 120);
    const a = document.createElement("a"); a.href = url; a.download = `${name} - ${fmtTC(S.t).replace(/[:.]/g, "-")}.png`;
    document.body.appendChild(a); a.click(); a.remove();
    toast("📷 Quadro salvo em Downloads");
  } catch (e) { console.warn("captura:", e); toast("Não deu pra capturar esse vídeo", 3500); }
  b.disabled = false; b.textContent = old;
}
$("#btnCapture").onclick = captureFrame;
// ---- modal de atalhos
$("#btnKeys").onclick = () => $("#kbModal").classList.remove("hidden");
$("#btnKeysClose").onclick = () => $("#kbModal").classList.add("hidden");
$("#kbModal").onclick = (e) => { if (e.target.id === "kbModal") $("#kbModal").classList.add("hidden"); };
// botões e sliders do transporte não ficam com o foco (senão as teclas de atalho param de funcionar)
for (const id of ["#transport", "#transport2", "#tlTools"]) {
  $(id).addEventListener("click", (e) => { const b = e.target.closest("button"); if (b) b.blur(); });
  $(id).addEventListener("change", (e) => { if (e.target.type === "range") e.target.blur(); });
}

// ======================================================= COMPARAR (referência x nosso vídeo, lado a lado, sincronizados)
const vRef = $("#cmpRef"), vOur = $("#cmpOur");
const CMP = { pid: null, from: "home", ini: 0, d: null, playing: false, speed: 1, mute: { ref: true, our: false }, allPrev: null, lastFix: 0, raf: 0, saveT: 0, dragging: false, err: { ref: "", our: "" } };
try { const m = JSON.parse(localStorage.getItem("cmp_mute") || "null"); if (m && typeof m.ref === "boolean" && typeof m.our === "boolean") CMP.mute = m; } catch (e) { }
try { const a = JSON.parse(localStorage.getItem("cmp_mute_prev") || "null"); if (a && typeof a.ref === "boolean") CMP.allPrev = a; } catch (e) { }
const CMP_SPEEDS = [0.5, 0.75, 1, 1.25, 1.5, 2];
try { CMP.speed = +localStorage.getItem("cmp_speed") || 1; } catch (e) { }
if (!CMP_SPEEDS.includes(CMP.speed)) CMP.speed = 1;
const fmtMS = (t) => { t = Math.max(0, Math.floor(t || 0)); return Math.floor(t / 60) + ":" + pad2(t % 60); };
const cmpVisible = () => !$("#comparar").classList.contains("hidden");
const cmpDur = () => (isFinite(vOur.duration) ? vOur.duration : 0);

function cmpMsg(k, msg) {
  const el = $(k === "ref" ? "#cmpBoxRef .cmpMsg" : "#cmpBoxOur .cmpMsg"), m = CMP.err[k] || msg || "";
  if (el.textContent !== m) el.textContent = m;
  el.classList.toggle("hidden", !m);
}
// a referência segue o nosso vídeo: ref = ref_inicio + tempo do nosso; corrige se escorregar mais de 0,15 s
function cmpSyncRef(force) {
  if (!vRef.getAttribute("src") || CMP.err.ref) return;
  const tgt = CMP.ini + (vOur.currentTime || 0), rd = isFinite(vRef.duration) ? vRef.duration : Infinity;
  if (tgt >= rd - 0.05) {
    if (!vRef.paused) vRef.pause();
    if (Math.abs(vRef.currentTime - rd) > 0.5) vRef.currentTime = Math.max(0, rd - 0.05);
    cmpMsg("ref", `Fim do trecho baixado da referência (${fmtMS(rd)})`);
    return;
  }
  cmpMsg("ref", "");
  const now = performance.now();
  if (force || (!vRef.seeking && Math.abs(vRef.currentTime - tgt) > 0.15 && now - CMP.lastFix > 350)) { vRef.currentTime = tgt; CMP.lastFix = now; }
  if (CMP.playing && !vOur.paused && vRef.paused && !vRef.ended) vRef.play().catch(() => { });
}
function cmpUI() {
  const D = cmpDur(), t = vOur.currentTime || 0;
  $("#cmpTime").textContent = fmtMS(t) + " / " + fmtMS(D);
  if (!CMP.dragging) $("#cmpScrub").value = D ? Math.round((t / D) * 1000) : 0;
  $("#cmpPlay").textContent = CMP.playing ? "⏸ Pausar" : "▶ Tocar os dois";
}
function cmpLoop() {
  cancelAnimationFrame(CMP.raf);
  const step = () => { if (!CMP.playing) return; cmpSyncRef(false); cmpUI(); CMP.raf = requestAnimationFrame(step); };
  CMP.raf = requestAnimationFrame(step);
}
async function cmpPlay() {
  if (CMP.playing) return cmpPause();
  if (!vOur.getAttribute("src") || CMP.err.our) return toast("Este vídeo ainda não tem o nosso vídeo pronto para tocar");
  if (vOur.ended || vOur.currentTime >= cmpDur() - 0.05) vOur.currentTime = 0;
  CMP.playing = true; cmpApplyRate(); cmpSyncRef(true);
  try { await vOur.play(); } catch (e) { CMP.playing = false; cmpUI(); if (e.name !== "AbortError") toast("❌ Não consegui tocar: " + e.message, 5000); return; }
  cmpSyncRef(true); cmpUI(); cmpLoop();
}
function cmpPause() { CMP.playing = false; cancelAnimationFrame(CMP.raf); vOur.pause(); vRef.pause(); cmpSyncRef(true); cmpUI(); }
function cmpSeek(t) { const D = cmpDur(); if (!D) return; vOur.currentTime = Math.max(0, Math.min(D - 0.01, t)); cmpSyncRef(true); cmpUI(); }
function cmpApplyRate() { vRef.playbackRate = vOur.playbackRate = CMP.speed; $("#cmpSpeeds").querySelectorAll("[data-sp]").forEach((b) => b.classList.toggle("on", +b.dataset.sp === CMP.speed)); }
function cmpApplyMute() {
  vRef.muted = CMP.mute.ref; vOur.muted = CMP.mute.our;
  for (const k of ["ref", "our"]) {
    const b = document.querySelector(`.cmpMute[data-m="${k}"]`), nome = k === "ref" ? "da referência" : "do nosso vídeo";
    b.textContent = CMP.mute[k] ? "🔇" : "🔊"; b.classList.toggle("on", !CMP.mute[k]);
    b.title = (CMP.mute[k] ? "Som desligado — clique para LIGAR o som " : "Som ligado — clique para DESLIGAR o som ") + nome;
  }
  const all = CMP.mute.ref && CMP.mute.our;
  $("#cmpMuteAll").textContent = all ? "🔇 Mudo (os dois)" : "🔊 Som"; $("#cmpMuteAll").classList.toggle("off", all);
  try { localStorage.setItem("cmp_mute", JSON.stringify(CMP.mute)); } catch (e) { }
}
function cmpMuteAll() {
  if (!(CMP.mute.ref && CMP.mute.our)) { CMP.allPrev = { ...CMP.mute }; CMP.mute = { ref: true, our: true }; }
  else { CMP.mute = CMP.allPrev && !(CMP.allPrev.ref && CMP.allPrev.our) ? { ...CMP.allPrev } : { ref: true, our: false }; }
  try { localStorage.setItem("cmp_mute_prev", JSON.stringify(CMP.allPrev)); } catch (e) { }
  cmpApplyMute();
}
function cmpSetIni(v) {
  CMP.ini = Math.round(Math.max(0, +v || 0) * 100) / 100;
  $("#cmpIni").value = CMP.ini; $("#cmpIniOk").textContent = "…";
  cmpSyncRef(true);
  const pid = CMP.pid;
  clearTimeout(CMP.saveT);
  CMP.saveT = setTimeout(async () => {
    try {
      const r = await jpost("/api/comparar/" + pid, { ref_inicio: CMP.ini });
      if (S.edit && S.pid === pid) S.edit.ref_inicio = r.ref_inicio; // editor aberto não apaga o valor ao salvar
      if (CMP.pid === pid) $("#cmpIniOk").textContent = "✅ salvo";
    } catch (e) { $("#cmpIniOk").textContent = ""; toast("❌ Não consegui salvar: " + String(e.message || e).slice(0, 160), 5000); }
  }, 600);
}
function cmpList() {
  if (CMP.from === "galeria") { const L = galVisiveis().filter((e) => e.tem_ref && e.pid).map((e) => e.pid); if (L.includes(CMP.pid)) return L; }
  const grpIdx = (p) => (/VIDEOS-NOVOS$/i.test(p.group || "") ? 0 : (+p.h || 0) > (+p.w || 0) ? 2 : 1); // mesma ordem da lista
  const ord = (arr) => arr.map((p, i) => [p, i]).filter(([p]) => p.tem_ref).sort((a, b) => grpIdx(a[0]) - grpIdx(b[0]) || a[1] - b[1]).map(([p]) => p.id);
  const vis = ord(HOME.origem === "Todos" ? HOME.list : HOME.list.filter((p) => fmtOf(p) === HOME.origem));
  return vis.includes(CMP.pid) ? vis : ord(HOME.list);
}
function cmpNav() {
  const L = cmpList(), i = L.indexOf(CMP.pid);
  $("#cmpPos").textContent = i >= 0 ? `${i + 1} / ${L.length}` : "";
  $("#cmpPrev").disabled = i <= 0; $("#cmpNext").disabled = i < 0 || i >= L.length - 1;
  return { L, i };
}
function cmpSetSrc(v, url) { if (url) { v.src = url; } else { v.removeAttribute("src"); } v.load(); }
async function openComparar(pid, from) {
  let d;
  try { d = await api("/api/comparar/" + pid); }
  catch (e) { toast("❌ Não consegui abrir a comparação: " + String(e.message || e).slice(0, 160), 6000); return; }
  if (from) CMP.from = from;
  if (!cmpVisible()) stopPlay();
  CMP.playing = false; cancelAnimationFrame(CMP.raf); clearTimeout(CMP.saveT);
  Object.assign(CMP, { pid, d, ini: +d.ref_inicio || 0, err: { ref: "", our: "" } });
  hideNew();
  $("#home").classList.add("hidden"); $("#editor").classList.add("hidden"); $("#pedido").classList.add("hidden"); $("#comparar").classList.remove("hidden");
  $("#cmpName").textContent = String(d.name || "").replace(/^\d+\s*-\s*[^-]+-\s*/, "") || d.name || "—";
  $("#cmpName").title = d.name || "";
  $("#cmpEstilo").textContent = d.estilo ? "🎨 " + d.estilo : "";
  const r = d.referencia || {};
  $("#cmpYt").classList.toggle("hidden", !r.video); if (r.video) $("#cmpYt").href = r.video;
  $("#cmpCanal").classList.toggle("hidden", !r.canal_url); if (r.canal_url) { $("#cmpCanal").href = r.canal_url; $("#cmpCanal").textContent = "📡 canal" + (r.canal ? ": " + r.canal : ""); }
  $("#cmpIni").value = CMP.ini; $("#cmpIniOk").textContent = "";
  if (!d.ref_url) CMP.err.ref = "Ainda não tem a referência baixada para este vídeo";
  if (!d.nosso_url) CMP.err.our = "Este vídeo ainda não foi gerado";
  cmpMsg("ref", ""); cmpMsg("our", "");
  cmpSetSrc(vOur, d.nosso_url); cmpSetSrc(vRef, d.ref_url);
  cmpApplyRate(); cmpApplyMute(); cmpUI(); cmpNav();
}
function cmpHide() {
  if ($("#comparar").classList.contains("hidden")) return; // (chamado no loadHome inicial, antes das const abaixo existirem)
  CMP.playing = false; cancelAnimationFrame(CMP.raf);
  vOur.pause(); vRef.pause(); cmpSetSrc(vOur, null); cmpSetSrc(vRef, null);
  if (document.fullscreenElement === $("#comparar")) document.exitFullscreen().catch(() => { });
  $("#comparar").classList.add("hidden");
}
function cmpBack() {
  if (CMP.from === "editor" && S.edit && S.pid === CMP.pid) { cmpHide(); $("#editor").classList.remove("hidden"); setTimeout(fitStage, 30); return; }
  if (CMP.from === "galeria") { cmpHide(); openGaleria(); return; }
  if (CMP.from === "editor" && S.dirty && !confirm("O vídeo que estava no editor tem mudanças não salvas. Voltar para a lista mesmo assim?")) return;
  loadHome();
}
function cmpFull() { const el = $("#comparar"); if (document.fullscreenElement) document.exitFullscreen().catch(() => { }); else if (el.requestFullscreen) el.requestFullscreen().catch(() => toast("Tela cheia não disponível aqui")); }

$("#cmpSpeeds").innerHTML = CMP_SPEEDS.map((s) => `<button class="btn" data-sp="${s}">${String(s).replace(".", ",")}x</button>`).join("");
$("#cmpSpeeds").onclick = (e) => { const b = e.target.closest("[data-sp]"); if (!b) return; CMP.speed = +b.dataset.sp; try { localStorage.setItem("cmp_speed", CMP.speed); } catch (er) { } cmpApplyRate(); cmpSyncRef(true); };
$("#cmpPlay").onclick = cmpPlay;
$("#cmpBack").onclick = cmpBack;
$("#cmpFull").onclick = cmpFull;
$("#cmpMuteAll").onclick = cmpMuteAll;
document.querySelectorAll(".cmpMute").forEach((b) => (b.onclick = () => { const k = b.dataset.m; CMP.mute[k] = !CMP.mute[k]; cmpApplyMute(); }));
$("#cmpPrev").onclick = () => { const { L, i } = cmpNav(); if (i > 0) openComparar(L[i - 1]); };
$("#cmpNext").onclick = () => { const { L, i } = cmpNav(); if (i >= 0 && i < L.length - 1) openComparar(L[i + 1]); };
$("#cmpIni").onchange = (e) => cmpSetIni(e.target.value);
$("#cmpIniMinus").onclick = () => cmpSetIni(CMP.ini - 1);
$("#cmpIniPlus").onclick = () => cmpSetIni(CMP.ini + 1);
const cmpScrub = $("#cmpScrub");
cmpScrub.addEventListener("input", () => { CMP.dragging = true; cmpSeek((cmpScrub.value / 1000) * cmpDur()); });
cmpScrub.addEventListener("change", () => { CMP.dragging = false; cmpScrub.blur(); cmpUI(); });
$("#btnCmp").onclick = () => openComparar(S.pid, "editor");
vOur.addEventListener("loadedmetadata", () => { cmpSyncRef(true); cmpUI(); });
vRef.addEventListener("loadedmetadata", () => cmpSyncRef(true));
vOur.addEventListener("ended", () => { CMP.playing = false; cancelAnimationFrame(CMP.raf); vRef.pause(); cmpUI(); });
vOur.addEventListener("waiting", () => { if (CMP.playing) vRef.pause(); });
vOur.addEventListener("playing", () => { if (CMP.playing) cmpSyncRef(true); });
vOur.addEventListener("seeked", cmpUI);
for (const [k, v] of [["ref", vRef], ["our", vOur]]) v.addEventListener("error", () => { if (!v.getAttribute("src")) return; CMP.err[k] = "❌ Não consegui tocar este arquivo"; cmpMsg(k, ""); });
for (const id of ["#cmpCtl", "#cmpCtl2", "#cmpStage", "#comparar .bar"]) $(id).addEventListener("click", (e) => { const b = e.target.closest("button"); if (b) b.blur(); });
document.addEventListener("keydown", (e) => {
  if (!cmpVisible() || /INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName) || e.ctrlKey || e.altKey || e.metaKey) return;
  const k = e.key.toLowerCase();
  if (e.key === " " || k === "k") { e.preventDefault(); cmpPlay(); }
  else if (e.key === "ArrowRight") { e.preventDefault(); cmpSeek(vOur.currentTime + 5); }
  else if (e.key === "ArrowLeft") { e.preventDefault(); cmpSeek(vOur.currentTime - 5); }
  else if (k === "m") cmpMuteAll();
  else if (k === "f") cmpFull();
});

// ======================================================= INÍCIO (boas-vindas) + GALERIA DE ESTILOS + COPIAR ESTILO
const NEW_SECS = ["#inicio", "#galeria", "#copiar", "#vimg", "#conferir", "#roteiro", "#ajustes", "#bombando"];
function hideNew() { NEW_SECS.forEach((s) => $(s) && $(s).classList.add("hidden")); $("#topnav") && $("#topnav").classList.add("hidden"); closeVid(); }
function showOnly(sel) {
  if (!$("#editor").classList.contains("hidden") && S.dirty && !confirm("Tem mudanças não salvas. Sair mesmo assim?")) return false;
  stopPlay(); cmpHide();
  ["#home", "#editor", "#pedido", ...NEW_SECS].forEach((s) => $(s).classList.add("hidden"));
  closeVid(); $(sel).classList.remove("hidden"); window.scrollTo(0, 0);
  $("#topnav").classList.remove("hidden");
  marcarAba(sel); TELA.atual = TELA_NOME[sel] || sel; TELA.video = "";
  return true;
}
const IC = {
  play: '<svg viewBox="0 0 24 24" class="ic"><path d="M8 5.5v13l10.5-6.5z"/></svg>',
  cmp: '<svg viewBox="0 0 24 24" class="ic"><rect x="3" y="5" width="7.5" height="14" rx="1.5"/><rect x="13.5" y="5" width="7.5" height="14" rx="1.5"/></svg>',
  rel: '<svg viewBox="0 0 24 24" class="ic"><path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/></svg>',
  arrow: '<svg viewBox="0 0 24 24" class="ic"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
  pen: '<svg viewBox="0 0 24 24" class="ic"><path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>',
};
const GAL = { list: [], fmt: "Todos", q: "" };
try { GAL.fmt = localStorage.getItem("gal_fmt") || "Todos"; } catch (e) { }
const GAL_F = [["Todos", "🗂 Todos"], ["longo", "🎬 Vídeos longos"], ["short", "📱 Shorts"]];
const normTxt = (s) => String(s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
function seloGal(e) { return e.tipo === "fabrica" ? `<span class="gtag auto" title="O computador faz o vídeo inteiro sozinho, sem gastar nada">Automático</span>` : `<span class="gtag cla" title="A gente prepara o pedido e o Claude monta o vídeo">Com Claude</span>`; }
async function carregarEstilos() {
  if (!PED.estilos.length) PED.estilos = await api("/api/estilos");
  GAL.list = PED.estilos.filter((e) => e.tipo !== "em_breve");
  return GAL.list;
}
async function openInicio() {
  if (!showOnly("#inicio")) return;
  api("/api/projects").then((l) => { HOME.list = l; ["#wlMeusN", "#tnMeusN"].forEach((k) => ($(k).textContent = l.length)); renderStats(); }).catch(() => { });
  try { await carregarEstilos(); } catch (e) { return; }
  $("#tnEstN").textContent = GAL.list.length;
  renderStats(); renderMosaic(); renderPreviews();
}
function renderStats() {
  const L = GAL.list; if (!L.length) return;
  const it = (n, t) => `<span><b>${n}</b>${t}</span>`;
  $("#wlStats").innerHTML = [it(L.length, "estilos com exemplo"), (L.some((e) => e.tem_ref) ? it(L.filter((e) => e.tem_ref).length, "comparações com o original") : ""),
    it(L.filter((e) => e.tipo === "fabrica").length, "100% automáticos"), HOME.list.length ? it(HOME.list.length, "vídeos na sua pasta") : ""].join("");
  $("#wlEstGo").innerHTML = `Ver os ${L.length} estilos${IC.arrow}`;
}
function renderMosaic() {
  const th = GAL.list.filter((e) => e.thumb_url && e.formato !== "short");
  if (!th.length || $("#wlMosaic").dataset.ok) return;
  const rows = [0, 1, 2].map((r) => {
    const part = th.filter((_, i) => i % 3 === r);
    const imgs = part.map((e) => `<img src="${e.thumb_url}" alt="" loading="lazy" decoding="async">`).join("");
    return `<div class="mrow r${r}"><div class="mtrack">${imgs}${imgs}</div></div>`;
  });
  $("#wlMosaic").innerHTML = rows.join(""); $("#wlMosaic").dataset.ok = "1";
}
function renderPreviews() {
  const by = (ids, ok) => ids.map((id) => GAL.list.find((e) => e.id === id)).filter(Boolean).filter(ok);
  const longos = GAL.list.filter((e) => e.thumb_url && e.formato !== "short");
  let fan = by(["claude:novos:15-kurzgesagt-vetor", "claude:novos:28-infografico-escuro-dourado", "claude:novos:11-terror-creepy-escuro", "historia-simples"], (e) => e.thumb_url);
  if (fan.length < 4) fan = longos.slice(0, 4);
  $("#wlFan").innerHTML = fan.map((e, i) => `<div class="fc f${i}" style="background-image:url('${e.thumb_url}')"><span>${esc(e.nome)}</span></div>`).join("");
  const par = by(["claude:novos:07-cartoon-paises-personagens", "claude:novos:01-whiteboard", "claude:01-mapas"], (e) => e.tem_ref && e.pid)[0] || longos.find((e) => e.tem_ref && e.pid);
  if (!par) {   // sem vídeo original baixado: mostra "link colado → vídeo no mesmo estilo" em vez de um quadro vazio
    const ex = by(["claude:novos:15-kurzgesagt-vetor", "historia-simples"], (e) => e.thumb_url)[0] || longos[0];
    $("#wlPair").innerHTML = `<figure class="link"><div class="lnk"><svg viewBox="0 0 24 24" class="ic"><path d="M10 14a5 5 0 0 0 7 0l3-3a5 5 0 0 0-7-7l-1 1M14 10a5 5 0 0 0-7 0l-3 3a5 5 0 0 0 7 7l1-1"/></svg><span>youtube.com/watch?v=…</span></div><figcaption>Link</figcaption></figure>
      <span class="vs">→</span>
      ${ex ? `<figure class="nosso"><img src="${ex.thumb_url}" alt=""><figcaption>Seu vídeo</figcaption></figure>` : ""}
      <div class="pairNm">Cole o link e a gente faz no mesmo estilo</div>`;
    return;
  }
  $("#wlPair").innerHTML = `<figure><img src="/api/ref-thumb/${par.pid}?t=40" alt="" onerror="this.parentNode.classList.add('vazio')"><figcaption>Original</figcaption></figure>
    <span class="vs">×</span>
    <figure class="nosso"><img src="${par.thumb_url}" alt=""><figcaption>Nosso</figcaption></figure>
    <div class="pairNm">Exemplo real · ${esc(String(par.nome).replace(/\s*\(.*\)\s*$/, ""))}</div>`;
}
function galVisiveis() {
  const q = normTxt(GAL.q).trim();
  return GAL.list.filter((e) => (GAL.fmt === "Todos" || e.formato === GAL.fmt) &&
    (!q || normTxt([e.nome, e.descricao, e.exemplo, e.referencia?.canal, e.formato === "short" ? "short reels tiktok" : "longo youtube", e.tipo === "fabrica" ? "automatico" : "claude"].join(" ")).includes(q)));
}
async function openGaleria() {
  if (!showOnly("#galeria")) return;
  if (!GAL.list.length) {
    try { await carregarEstilos(); } catch (e) { $("#galGrid").innerHTML = `<div class="card">❌ Não consegui carregar os estilos: ${esc(String(e.message || e).slice(0, 200))}</div>`; return; }
  } else {   // estilos novos que chegaram nas pastas (VIDEOS-NOVOS / VIDEOS-SHORTS) entram sem recarregar a página
    api("/api/estilos").then((l) => {
      const novo = JSON.stringify(l.map((x) => [x.id, x.video_url, x.thumb_url]));
      if (novo === JSON.stringify(PED.estilos.map((x) => [x.id, x.video_url, x.thumb_url]))) return;
      PED.estilos = l; GAL.list = l.filter((e) => e.tipo !== "em_breve"); $("#tnEstN").textContent = GAL.list.length;
      if (!$("#galeria").classList.contains("hidden")) renderGaleria();
    }).catch(() => { });
  }
  renderGaleria();
}
function cardGal(e) {
  const vert = e.formato === "short";
  const sub = e.referencia?.canal ? `Original: ${esc(e.referencia.canal)}` : vert ? "Short vertical" : "Vídeo longo";
  return `<div class="gal ${e.tipo === "fabrica" ? "isauto" : ""}" data-gid="${esc(e.id)}">
    <div class="th ${vert ? "vert" : ""} ${e.pid ? "abre" : ""}" ${e.pid ? `data-gedit="${esc(e.pid)}" title="Abrir este vídeo no editor"` : ""} ${e.thumb_url ? `data-bgvar="${e.thumb_url}"` : ""}><div class="im"></div>${e.pid ? `<span class="abreTag">Abrir no editor</span>` : ""}
      ${seloGal(e)}<span class="fm">${vert ? "Short · 9:16" : "Longo · 16:9"}</span>
    </div>
    <div class="sbody">
      <span class="n">${sub}</span>
      <h4 title="${esc(e.nome)}">${esc(String(e.nome).replace(/\s*\(.*\)\s*$/, ""))}</h4>
      <p>${esc(e.descricao || "")}</p>${bomParaHtml(e)}
      <div class="srow">
        ${e.pid ? `<button class="sb sbEd" data-gedit="${esc(e.pid)}" title="Abrir o vídeo de exemplo no editor (linha do tempo, textos, imagens)">${IC.pen}Abrir no editor</button>` : ""}
        ${e.video_url ? `<button class="sb sbPlay" data-gplay="${esc(e.id)}">${IC.play}Ver exemplo</button>` : ""}
        ${e.tem_ref && e.pid ? `<button class="sb sbCmp" data-gcmp="${esc(e.pid)}" title="Abre o vídeo original e o nosso lado a lado, tocando juntos">${IC.cmp}Comparar com o original</button>` : ""}
        ${e.pid ? `<button class="sb sbRel" data-rel="${esc(e.pid)}" title="Quanto tempo levou pra fazer o exemplo">${IC.rel}Relatório</button>` : ""}
      </div>
      <button class="fazer" data-gfazer="${esc(e.id)}">Fazer um vídeo neste estilo${IC.arrow}</button>
    </div>
  </div>`;
}
function renderGaleria() {
  const cnt = (f) => GAL.list.filter((e) => f === "Todos" || e.formato === f).length;
  if (!GAL_F.some(([f]) => f === GAL.fmt)) GAL.fmt = "Todos";
  $("#galFiltro").innerHTML = GAL_F.map(([f, l]) => `<button class="chip ${GAL.fmt === f ? "on" : ""}" data-gf="${f}">${l.replace(/^\S+ /, "")} <span class="n">${cnt(f)}</span></button>`).join("");
  $("#galFiltro").querySelectorAll("[data-gf]").forEach((b) => (b.onclick = () => { GAL.fmt = b.dataset.gf; try { localStorage.setItem("gal_fmt", GAL.fmt); } catch (e) { } renderGaleria(); }));
  const L = galVisiveis();
  $("#galGrid").innerHTML = L.length ? `<div class="galIn">${L.map(cardGal).join("")}</div>`
    : `<div class="card">Nenhum estilo encontrado${GAL.q ? ` para "<b>${esc(GAL.q)}</b>"` : ""}. Tente outra palavra ou clique em 🗂 Todos.</div>`;
  lazyBg($("#galGrid"));
}
$("#galBusca").oninput = (e) => { GAL.q = e.target.value; renderGaleria(); };
$("#galGrid").onclick = (ev) => {
  const b = ev.target.closest("[data-gplay],[data-gcmp],[data-gfazer],[data-gedit],[data-rel]");
  if (!b || b.disabled) return;
  const byGid = (id) => GAL.list.find((x) => x.id === id);
  if (b.dataset.gplay) { ev.stopPropagation(); const e = byGid(b.dataset.gplay); if (e) openVid(e); }
  else if (b.dataset.rel) { window.open("/relatorio?pid=" + encodeURIComponent(b.dataset.rel), "_blank"); }
  else if (b.dataset.gedit) openProject(b.dataset.gedit);
  else if (b.dataset.gcmp) openComparar(b.dataset.gcmp, "galeria");
  else if (b.dataset.gfazer) openPedido(b.dataset.gfazer, "galeria");
};
// ---- tocar exemplo dentro da página
const vPlayer = $("#vPlayer");
function openVid(e) {
  $("#vTitle").textContent = "▶ Exemplo";
  $("#vEstilo").textContent = "🎨 Estilo: " + String(e.nome).replace(/\s*\(.*\)\s*$/, "");
  $("#vEditor").classList.toggle("hidden", !e.pid);
  $("#vEditor").onclick = () => { closeVid(); openProject(e.pid); };
  $("#vidModal").classList.toggle("vert", e.formato === "short");
  vPlayer.src = e.video_url; $("#vidModal").classList.remove("hidden");
  vPlayer.play().catch(() => { });
  $("#vFazer").onclick = () => { closeVid(); if (e.fazer) e.fazer(); else openPedido(e.id, "galeria"); };   // QA: Estilos IA passa o próprio "fazer"
}
function closeVid() {
  const m = document.getElementById("vidModal"), v = document.getElementById("vPlayer");
  if (!m || m.classList.contains("hidden")) return;
  v.pause(); v.removeAttribute("src"); v.load(); m.classList.add("hidden");
}
$("#vClose").onclick = closeVid;
$("#vidModal").onclick = (e) => { if (e.target.id === "vidModal") closeVid(); };
// ---- copiar estilo de um vídeo novo
const COP = { fmt: "longo", dur: 300 };
const COP_DURS = { longo: DUR_OPTS, short: [[30, "30 s"], [60, "1 min"], [90, "90 s"], [180, "3 min"]] };
const linkRede = (u) => /(youtube\.com|youtu\.be|instagram\.com|tiktok\.com)\//i.test(u);
function renderCopDurs() {
  const ds = COP_DURS[COP.fmt];
  if (!ds.some(([d]) => d === COP.dur)) COP.dur = COP.fmt === "short" ? 60 : 300;
  $("#cDurs").innerHTML = ds.map(([d, l]) => `<button class="btn pill ${COP.dur === d ? "on" : ""}" data-cd="${d}">${l}</button>`).join("");
  $("#cDurNota").classList.toggle("hidden", COP.dur <= 600);
  $("#cFmt").querySelectorAll("[data-fmt]").forEach((x) => x.classList.toggle("on", x.dataset.fmt === COP.fmt));
}
function openCopiar() {
  if (!showOnly("#copiar")) return;
  carregarVozes().catch(() => { });
   marcaPre("#cMarca");
  renderCopDurs();
  setTimeout(() => $("#cVideo").focus(), 50);
}
$("#cFmt").onclick = (e) => { const b = e.target.closest("[data-fmt]"); if (b) { COP.fmt = b.dataset.fmt; renderCopDurs(); } };
$("#cDurs").onclick = (e) => { const b = e.target.closest("[data-cd]"); if (b) { COP.dur = +b.dataset.cd; renderCopDurs(); } };
$("#cVerVideo").onclick = () => { const u = $("#cVideo").value.trim(); if (!urlOk(u)) return toast("Cole um link válido do vídeo (começa com https://)", 3500); window.open(u, "_blank"); };
$("#cVerCanal").onclick = () => { const u = $("#cCanalUrl").value.trim(); if (!urlOk(u)) return toast("Cole um link válido do canal (começa com https://)", 3500); window.open(u, "_blank"); };
$("#cComecar").onclick = async () => {
  if (!(await prontoChecar("cf"))) return;
  let video = $("#cVideo").value.trim(), canalUrl = $("#cCanalUrl").value.trim(), tema = $("#cTema").value.trim(), canal = $("#cCanal").value.trim();
  const erro = (sel, msg) => { $(sel).focus(); $(sel).classList.add("err"); setTimeout(() => $(sel).classList.remove("err"), 2500); toast(msg, 4500); };
  if (!video) return erro("#cVideo", "Cole o link do vídeo que você quer copiar");
  if (!urlOk(video)) return erro("#cVideo", "O link do vídeo não parece certo. Ele precisa começar com https://");
  if (!linkRede(video)) return erro("#cVideo", "Esse link não é do YouTube, Instagram ou TikTok");
  if (canalUrl && !urlOk(canalUrl)) return erro("#cCanalUrl", "O link do canal não parece certo. Ele precisa começar com https:// (ou deixe vazio)");
  if (!tema) { if (!(await ideiaAuto("#cTema", { formato: COP.fmt === "short" ? "short" : "longo", ref: video }))) return; tema = $("#cTema").value.trim(); }
  if (!canal) { canalAuto("#cCanal"); canal = $("#cCanal").value.trim(); }
  try { localStorage.setItem("pedido_canal", canal); } catch (x) { }
  modal("🔗 Preparando o seu pedido…"); $("#mMsg").textContent = "Enviando…";
  let r;
  try { r = await jpost("/api/pedido", { estilo: "copiar", ref_video: video, ref_canal: canalUrl, tema, canal_nome: canal, marca: marcaVal("#cMarca"), duracao: COP.dur, formato: COP.fmt, voz: $("#cVoz").value }); }
  catch (x) { closeModal(); return toast("❌ " + String(x.message || x).replace(/^\{"detail":"|"\}$/g, "").slice(0, 200), 6000); }
  pollJob(r.job, pedidoPronto);
};
// ---- tela final do pedido (estilos "Com Claude" e "Copiar estilo")
async function copiarTexto(t) {
  try { await navigator.clipboard.writeText(t); return true; } catch (e) { }
  try { const ta = document.createElement("textarea"); ta.value = t; document.body.appendChild(ta); ta.select(); const ok = document.execCommand("copy"); ta.remove(); return ok; } catch (e) { return false; }
}
function pedidoPronto(res) {
  if (res.rendered) {   // o painel rodou o Claude sozinho e o vídeo já saiu
    $("#mTitle").textContent = "✅ Vídeo pronto!"; $("#mBar").style.width = "100%"; $("#mMsg").textContent = res.name; $("#mBtns").innerHTML = "";
    mbtnVer(res.pid);
    mbtn("✏ Abrir no editor", () => { closeModal(); openProject(res.pid); }, "go");
    mlinksBaixar(res.pid, res.name); mbtnCapa(res.pid);
    mbtn("Fechar", closeModal); return;
  }
  const msg = res.mensagem_claude || `faz o vídeo do PEDIDO.md em ${res.folder}`;
  $("#mTitle").textContent = "✅ Pronto!"; $("#mBar").style.width = "100%";
  const aviso = res.ref_baixada === false ? `<p class="mWarn">⚠ Não consegui baixar o vídeo de referência agora (${esc(String(res.ref_erro || "").slice(0, 140))}). Sem problema: o link está no pedido e o Claude baixa.</p>`
    : res.ref_baixada ? `<p class="mOk">🎞 O vídeo que você quer copiar já foi baixado pra pasta.</p>` : "";
  $("#mMsg").innerHTML = `<p class="mBig">${res.sem_claude === false ? "📝 Pedido criado (o Claude não rodou agora). Quando quiser, mande esta mensagem no Claude:" : "⚠ Falta o app do Claude neste PC — instale em claude.ai/download, entre na conta (plano Pro) e clique em Fazer de novo. Ou, se preferir usar o chat, mande esta mensagem no Claude:"}</p><div class="claudeMsg">${esc(msg.replace(res.folder || "§§", "“" + amigavel(res.folder) + "”"))}</div>${aviso}<p class="mMu">Pasta do seu vídeo: ${esc(amigavel(res.folder))}</p><p class="mMu">Em 📂 Meus vídeos ele aparece como "⏳ ainda sem vídeo" até o Claude terminar.</p>`;
  mbtn("📋 Copiar mensagem pro Claude", async () => { const ok = await copiarTexto(msg); toast(ok ? "✅ Mensagem copiada! Agora cole no Claude (Ctrl+V)" : "❌ Não consegui copiar — selecione o texto e use Ctrl+C", 4500); }, "go");
  mbtn("📂 Abrir pasta", () => api(`/api/open/${res.pid}?what=folder`, { method: "POST" }));
  mbtn("📂 Meus vídeos", () => { closeModal(); loadHome(); });
  mbtn("Fechar", closeModal);
}
// ---- botões comuns
document.addEventListener("click", (e) => {
  if (e.target.closest("[data-inicio]")) openInicio();
  else if (e.target.closest("[data-meus]")) loadHome();
});
$("#wlEstilos").onclick = openGaleria;
$("#wlCopiar").onclick = openCopiar;
$("#wlMeus").onclick = loadHome;
$("#wlAjuda").onclick = $("#tnAjuda").onclick = () => $("#helpModal").classList.remove("hidden");
$("#tnEstilos").onclick = openGaleria;
$("#tnCopiar").onclick = openCopiar;
$("#helpClose").onclick = () => $("#helpModal").classList.add("hidden");
$("#helpModal").onclick = (e) => { if (e.target.id === "helpModal") $("#helpModal").classList.add("hidden"); };
document.addEventListener("keydown", (e) => {
  if (e.key !== "Escape") return;
  if (!$("#vidModal").classList.contains("hidden")) closeVid();
  $("#helpModal").classList.add("hidden");
});
// ======================================================= FASE 1 — ferramentas próprias (fila, ajustes, vídeo com imagens, conferir, roteiro pronto, bombando)
const TELA = { atual: "Início", video: "" };
const TELA_NOME = { "#inicio": "Início", "#galeria": "Estilos prontos", "#copiar": "Copiar um vídeo", "#vimg": "Vídeo com imagens", "#conferir": "Conferir imagens",
  "#roteiro": "Roteiro pronto", "#ajustes": "Ajustes", "#bombando": "Estilos em alta", "#home": "Meus vídeos" };
function marcarAba(sel) { document.querySelectorAll("#topnav [data-tab]").forEach((b) => b.classList.toggle("on", "#" + b.dataset.tab === sel || (sel === "#conferir" && b.dataset.tab === "vimg"))); }
function amigavel(p) {
  const s = String(p || ""); if (!s) return "";
  const m = s.match(/^[A-Za-z]:\\Users\\[^\\]+\\(Desktop|Documents|Downloads|Videos)(\\.*)?$/i);
  const nomes = { desktop: "Área de Trabalho", documents: "Documentos", downloads: "Downloads", videos: "Vídeos" };
  if (m) return [nomes[m[1].toLowerCase()], ...(m[2] || "").split("\\").filter(Boolean)].join(" › ");
  const d = s.match(/^([A-Za-z]):\\?(.*)$/);
  if (d) return ["Disco " + d[1].toUpperCase(), ...d[2].split("\\").filter(Boolean)].join(" › ");
  return s.split(/[\\/]/).pop();
}
const errTxt = (x) => { const t = String((x && x.message) || x || ""); try { const j = JSON.parse(t); return String(j.detail || t).slice(0, 300); } catch (e) { return t.slice(0, 300); } };
const fmtSeg = (s) => { s = Math.max(0, Math.round(s || 0)); if (s < 60) return s + " s"; const m = Math.floor(s / 60); if (m < 60) return m + " min" + (s % 60 && m < 5 ? " " + (s % 60) + " s" : ""); return Math.floor(m / 60) + " h " + (m % 60) + " min"; };
const tocar = (url) => { const a = $("#audTeste"); a.src = url; a.play().catch(() => toast("Clique de novo pra ouvir")); };

// ---- tema claro / escuro
function aplicarTema(t, salvar) {
  document.documentElement.dataset.theme = t;
  $("#tnTema").innerHTML = '<svg class="ic"><use href="#' + (t === "light" ? "i-moon" : "i-sun") + '"/></svg>';
  $("#tnTema").title = t === "light" ? "Mudar pra tema escuro" : "Mudar pra tema claro";
  if (salvar) try { localStorage.setItem("tema", t); } catch (e) { }
}
aplicarTema(document.documentElement.dataset.theme === "light" ? "light" : "dark");
$("#tnTema").onclick = () => aplicarTema(document.documentElement.dataset.theme === "light" ? "dark" : "light", true);

// ======================================================= FILA DE TRABALHOS (Meus vídeos)
const FILA = { list: [], t: null, prontos: new Set(), primeira: true };
const TIPO_ICO = { capa: "🖼", render: "🎞", fabrica: "⚡", pedido: "📝", video_imagens: "🖼", roteiro: "✍️", medir: "📈", skill: "🤖", ajuste: "🔧", voz: "🎙", ideias: "💡", medico: "🩺" };
const TIPO_NOME = { capa: "Capa do Instagram", render: "Gerar vídeo", fabrica: "Vídeo automático", pedido: "Pedido pro Claude", video_imagens: "Vídeo com imagens", roteiro: "Roteiro", medir: "Atualizar números", skill: "Estilo IA (Claude)", ajuste: "Ajuste pelo Claude", voz: "Voz", ideias: "Ideias", medico: "Médico do render" };
const ST = { fila: "⏳ Na fila", rodando: "▶ Fazendo agora", pronto: "✅ Pronto", erro: "❌ Deu erro", cancelado: "✖ Cancelado" };
function filaClaudePos(lista) {
  const esp = (lista || []).filter((j) => !j.done && /^Na fila do Claude/.test(j.msg || "")).sort((a, b) => (a.criado || 0) - (b.criado || 0));
  window.__filaClaude = Object.fromEntries(esp.map((j, i) => [j.id, i + 1]));
}
async function filaAtualizar(force) {
  clearTimeout(FILA.t);
  let l;
  try { l = await api("/api/jobs"); } catch (e) { l = FILA.list; }
  FILA.list = l || []; filaClaudePos(FILA.list); avisoFila(FILA.list);
  const ativos = FILA.list.filter((j) => !j.done).length;
  $("#tnFilaN").textContent = ativos ? `● ${ativos} rodando` : "";
  // terminou algo novo → atualiza a lista de vídeos se ela estiver aberta
  let novo = false;
  FILA.list.forEach((j) => { if (j.done && !FILA.prontos.has(j.id)) { if (!FILA.primeira) novo = true; FILA.prontos.add(j.id); } });
  FILA.primeira = false;
  if (!$("#home").classList.contains("hidden")) {
    renderFila();
    if (novo) api("/api/projects").then((x) => { HOME.list = x; renderHome(); }).catch(() => { });
  }
  // leve 01/11: aba escondida → confere bem menos (o aviso de "pronto" continua chegando, só uns segundos depois)
  FILA.t = setTimeout(filaAtualizar, document.hidden ? (ativos ? 8000 : 30000) : (ativos ? 2000 : 12000));
}
document.addEventListener("visibilitychange", () => { if (!document.hidden) filaAtualizar(); });   // voltou pra aba → atualiza na hora
const FILA_SVG = { capa: "image", render: "film", fabrica: "spark", pedido: "pen", video_imagens: "image", roteiro: "pen", medir: "trend", skill: "spark", ajuste: "gear", voz: "mic", ideias: "bulb", medico: "pulse", short: "phone", cortes: "scissors", falado: "wave", copiar: "copy", amostra: "film", emalta: "flame" };
const STS = { fila: "Na fila", rodando: "Fazendo agora", pronto: "Pronto", erro: "Deu erro", cancelado: "Cancelado" };
function renderFila() {
  const box = $("#filaBox"), l = FILA.list.slice(0, 12);
  if (!l.length) { box.innerHTML = `<div class="filaHead"><b>Fila de trabalhos</b><span class="mu">Nada rodando. Quando você pedir um vídeo, ele aparece aqui com a etapa e o tempo que falta.</span></div>`; box.classList.remove("hidden"); return; }
  const ativos = l.filter((j) => !j.done).length;
  box.classList.remove("hidden");
  box.innerHTML = `<div class="filaHead"><b>Fila de trabalhos</b><span class="mu">1 trabalho pesado por vez · ${ativos ? ativos + " em andamento" : "nada rodando agora"}</span><div class="grow"></div>${l.some((j) => j.done) ? '<button class="btn mini" id="filaLimpar">Limpar concluídos</button>' : ""}</div>` +
    l.map((j) => {
      const r = j.resultado || {};
      const naFilaClaude = /^Na fila do Claude/.test(j.msg || "");
      const tempo = !j.done ? (naFilaClaude ? `esperando a vez do Claude · posição ${(window.__filaClaude || {})[j.id] || "?"} · cada vídeo leva ~15 min` : j.status === "fila" ? (j.posicao ? `posição ${j.posicao} na fila` : "esperando a vez") : `${Math.round(j.pct)}%${j.eta != null ? " · faltam ~" + fmtSeg(j.eta) : ""} · ${fmtSeg(j.decorrido)} até agora`)
        : (j.total != null ? "⏱ levou " + fmtSeg(j.total) + " do clique até ficar pronto" : j.decorrido ? "levou " + fmtSeg(j.decorrido) : "");
      let acts = "";
      if (!j.done) acts = `<button class="btn mini danger" data-jcan="${j.id}">Cancelar</button>`;
      else if (j.status === "pronto") {
        if (r.conferir) acts += `<button class="btn mini go" data-jconf="${r.pid}">Conferir imagens</button>`;
        if (r.rid) acts += `<button class="btn mini go" data-jrot="${r.rid}">Ver roteiro</button>`;
        if (r.pid && (r.rendered || r.video)) acts += `<button class="btn mini go" data-jver="${r.pid}">Ver vídeo</button>`;
        if (r.pid && r.medico && r.medico.corrigiveis > 0) acts += `<button class="btn mini" data-jmed="${r.pid}" title="Achei tela preta ou frame congelado que dá pra consertar sozinho">Consertar (${r.medico.corrigiveis})</button>`;
        if (r.pid && String(j.tipo || "").startsWith("blender_")) acts += `<button class="btn mini go" data-jbz="${r.pid}" title="Abre a revisão cena a cena na aba Blender 3D">🧊 Abrir no Blender 3D</button>`;
        else if (r.pid && !r.conferir) acts += `<button class="btn mini" data-jed="${r.pid}">Abrir no editor</button>`;
        if (r.pid && (r.rendered || r.video)) acts += `<a class="btn mini go" href="/api/baixar/${r.pid}/leve" download title="Versão menor, boa para postar" onclick="event.stopPropagation()">Baixar leve</a><a class="btn mini" href="/api/baixar/${r.pid}/final" download title="Qualidade máxima" onclick="event.stopPropagation()">Baixar final</a>`;
        if (j.tipo === "capa" && r.pid) acts += `<a class="btn mini go" href="/api/baixar/${r.pid}/capa" download title="Baixa a capa (funciona no celular)" onclick="event.stopPropagation()">Baixar capa</a><a class="btn mini go" href="/api/baixar/${r.pid}/descricao" download title="Baixa o descricao.txt (títulos, descrição e hashtags)" onclick="event.stopPropagation()">Baixar descrição</a>`;
        if (r.pid && r.rendered) acts += `<button class="btn mini" data-jcapa="${r.pid}" title="Cria a capa do Instagram e o descricao.txt">Criar capa</button>`;
        if (r.pid) acts += `<button class="btn mini" data-jpasta="${r.pid}" title="${esc(r.pasta_nome || "")}">Pasta</button>`;
      } else if (j.status === "erro") acts = `<button class="btn mini" data-jerr="${j.id}">Ver o erro</button>`;
      const ico = FILA_SVG[j.tipo] || "gear";
      return `<div class="job st-${j.status} ${j.done ? "feito" : ""}"><span class="ji"><svg class="ic"><use href="#i-${ico}"/></svg></span>
        <div class="jm"><div class="jt"><b>${esc(j.titulo || TIPO_NOME[j.tipo] || "Trabalho")}</b><span class="jst">${STS[j.status] || j.status}</span></div>
          <div class="jk">${TIPO_NOME[j.tipo] || ""}</div>
          ${!j.done ? `<div class="jbar"><i style="width:${Math.max(2, j.pct)}%"></i></div>` : ""}
          <small>${esc(j.done ? (j.status === "erro" ? "Parou com erro" : j.status === "cancelado" ? "Cancelado" : "Terminou") : j.msg || "")}${tempo ? " · " + tempo : ""}</small></div>
        ${acts ? `<div class="ja">${acts}</div>` : ""}</div>`;
    }).join("");
  const on = (sel, fn) => box.querySelectorAll(sel).forEach((b) => (b.onclick = (e) => { e.stopPropagation(); fn(b); }));
  on("[data-jcan]", async (b) => { b.disabled = true; await jpost(`/api/jobs/${b.dataset.jcan}/cancelar`, {}); toast("Cancelando…"); filaAtualizar(); });
  on("[data-jconf]", (b) => openConferir(b.dataset.jconf));
  on("[data-jrot]", (b) => openRoteiro(b.dataset.jrot));
  on("[data-jver]", (b) => { const jb = FILA.list.find((x) => x.resultado && x.resultado.pid === b.dataset.jver && x.titulo); assistirAqui(b.dataset.jver, jb ? jb.titulo : "Vídeo pronto", true); });
  on("[data-jed]", (b) => openProject(b.dataset.jed));
  on("[data-jbz]", (b) => window.openBlender && window.openBlender(b.dataset.jbz));
  on("[data-jmed]", (b) => { modal("🩺 Médico do render"); medicoConsertar(b.dataset.jmed); });
  on("[data-jcapa]", (b) => criarCapa(b.dataset.jcapa));
  on("[data-jpasta]", (b) => api(`/api/open/${b.dataset.jpasta}?what=folder`, { method: "POST" }));
  on("[data-jerr]", (b) => { const j = FILA.list.find((x) => x.id === b.dataset.jerr); modal("❌ O que aconteceu"); modalErro("❌ O que aconteceu", j?.error || "sem detalhes", { acao: j?.titulo || "" }); });
  const lp = $("#filaLimpar"); if (lp) lp.onclick = async () => { await jpost("/api/jobs/limpar", {}); filaAtualizar(); };
}

// modal de progresso com "fechar e continuar em segundo plano"
// erro de trabalho: mostra só a frase que importa (o traceback inteiro vai pro botão “Copiar detalhes”)
function erroCurto(t) {
  t = String(t || "").trim(); if (!t) return "sem detalhes";
  if (!/Traceback|File "|line \d+, in /.test(t)) return t.slice(0, 700);
  const ls = t.split("\n").map((l) => l.trim()).filter(Boolean);
  let k = -1; ls.forEach((l, i) => { if (/^[\w.]*(Error|Exception|Interrupt|Exit)\b/.test(l)) k = i; });
  const msg = (k >= 0 ? ls.slice(k).join("\n") : ls.slice(-2).join("\n")).replace(/^[\w.]*(Error|Exception):\s*/, "");
  return msg.slice(0, 700) || "erro sem mensagem";
}
function modalErro(titulo, t, ctx) {
  $("#mTitle").textContent = titulo || "❌ Deu erro";
  $("#mMsg").textContent = erroCurto(t) + "\n\nDica: mande fazer de novo. Se repetir, clique em “📋 Copiar detalhes” e cole no balão “Quer mudar alguma coisa?”.";
  $("#mBtns").innerHTML = "";
  mbtn("📋 Copiar detalhes", async () => toast((await copiarTexto(String(t || ""))) ? "✅ Detalhes copiados" : "❌ Não consegui copiar"));
  if (ctx && !ctx.semCorrigir) mbtn("🛠 Corrigir com Claude", () => corrigirComClaude(ctx.acao, t), "go");
  mbtn("Fechar", closeModal, ctx && !ctx.semCorrigir ? "" : "go");
}
// 🛠 Corrigir com Claude: roda o Claude Code do PC na pasta do pacote, mostra o resumo e deixa Desfazer / Reiniciar.
async function corrigirComClaude(acao, erro) {
  let r; try { r = await jpost("/api/corrigir", { acao, erro: String(erro || "") }); } catch (e) { return toast("❌ " + errTxt(e), 7000); }
  acompanhar(r.job, "🛠 Claude corrigindo o erro…", (res) => corrigirResultado(res));
}
function corrigirResultado(res) {
  const arqs = [...(res.mudou || []), ...(res.novo || [])];
  $("#mTitle").textContent = arqs.length ? "✅ Claude corrigiu" : "ℹ️ Claude analisou (sem mudar arquivos)";
  $("#mMsg").textContent = (res.resumo || "") + (arqs.length ? "\n\nArquivos alterados:\n• " + arqs.join("\n• ") : "") +
    (res.reiniciar ? "\n\n⚠ Mudou arquivo do servidor: clique em “🔄 Reiniciar o painel” para valer." : arqs.length ? "\n\nAtualize a página (F5) e tente de novo." : "");
  $("#mBar").style.width = "100%"; $("#mBtns").innerHTML = "";
  if (res.reiniciar) mbtn("🔄 Reiniciar o painel", reiniciarPainel, "go");
  else if (arqs.length) mbtn("🔄 Atualizar a página", () => location.reload(), "go");
  if (arqs.length) mbtn("↩ Desfazer", async () => {
    if (!confirm("Voltar os arquivos como estavam antes da correção?")) return;
    let d; try { d = await jpost(`/api/corrigir/${res.cid}/desfazer`, {}); } catch (e) { return toast("❌ " + errTxt(e), 6000); }
    toast(`↩ Desfeito (${d.desfeito} arquivo${d.desfeito === 1 ? "" : "s"})`, 4000);
    if (d.reiniciar) { if (confirm("Reiniciar o painel para valer?")) reiniciarPainel(); else closeModal(); } else closeModal();
  });
  mbtn("Fechar", closeModal);
}
async function reiniciarPainel() {
  try { await jpost("/api/reiniciar", {}); } catch (e) { }
  modal("🔄 Reiniciando o painel…"); $("#mMsg").textContent = "Aguarde uns segundos, a página recarrega sozinha.";
  const tenta = async () => { try { const r = await fetch("/api/config", { cache: "no-store" }); if (r.ok) return location.reload(); } catch (e) { } setTimeout(tenta, 1500); };
  setTimeout(tenta, 5000);
}
function acompanhar(job, titulo, onDone, onErr) {
  modal(titulo); $("#mMsg").textContent = "Começando…";
  let fechado = false;
  mbtn("Fechar (continua em Meus vídeos)", () => { fechado = true; closeModal(); toast("Tudo bem! Acompanhe em 📂 Meus vídeos.", 3500); });
  mbtn("✖ Cancelar", async () => { if (!confirm("Cancelar este trabalho?")) return; await jpost(`/api/jobs/${job}/cancelar`, {}); });
  const tick = async () => {
    let j; try { j = await api("/api/job/" + job); } catch (e) { return setTimeout(tick, 2500); }
    if (!fechado) {
      $("#mBar").style.width = j.pct + "%";
      const eta = j.eta;   // QA: o servidor só estima quando dá (antes: "faltam 10 s" logo no começo)
      $("#mMsg").textContent = `${Math.round(j.pct)}% — ${j.msg}` + (eta ? `\nFaltam uns ${fmtSeg(eta)}.` : "");
    }
    filaAtualizar();
    if (!j.done) return setTimeout(tick, 1500);
    if (j.error) {
      if (onErr && onErr(j, fechado) === "tratado") return;   // o chamador mostra o próprio erro
      if (fechado) return toast("❌ " + titulo.replace(/…$/, "") + ": deu erro (veja em Meus vídeos)", 6000);
      if (j.status === "cancelado") { $("#mTitle").textContent = "✖ Cancelado"; $("#mMsg").textContent = "Trabalho cancelado."; $("#mBtns").innerHTML = ""; mbtn("Fechar", closeModal); return; }
      return modalErro("❌ Deu erro", j.error, { acao: titulo.replace(/…$/, ""), semCorrigir: titulo.startsWith("🛠") });
    }
    $("#mBar").style.width = "100%"; $("#mBtns").innerHTML = "";
    try { await onDone(j.result, fechado); } catch (e) { }
    // se quem chamou não deixou nenhum botão, o modal ficaria preso: põe um Fechar
    if (!fechado && !$("#mBtns").children.length) mbtn("Fechar", closeModal);
  };
  tick();
}

// ======================================================= VOZES (todas as listas)
const VOZES = { lista: null, idioma: null };
async function carregarVozes(force) {
  const aj = AJU.d || (AJU.d = await api("/api/ajustes"));
  if (!VOZES.lista || force || VOZES.idioma !== aj.idioma) {
    try { VOZES.lista = await api("/api/ajustes/vozes?idioma=" + encodeURIComponent(aj.idioma)); VOZES.idioma = aj.idioma; } catch (e) { VOZES.lista = []; }
  }
  const grupos = {};
  VOZES.lista.forEach((v) => (grupos[v.grupo] = grupos[v.grupo] || []).push(v));
  const opts = Object.entries(grupos).map(([g, vs]) => `<optgroup label="${esc(g)}">${vs.map((v) => `<option value="${esc(v.id)}">${esc(v.nome)}</option>`).join("")}</optgroup>`).join("");
  document.querySelectorAll(".selVoz").forEach((sel) => {
    const pad = sel.id === "pVoz" || sel.dataset.padrao === "1";
    const cur = sel.value || (pad ? "" : aj.voz);
    sel.innerHTML = (pad ? '<option value="">Padrão (a dos Ajustes)</option>' : "") + opts;
    sel.value = cur; if (sel.value !== cur && !pad) sel.value = aj.voz;
  });
}

// ======================================================= NARRAÇÃO: VOZ DO PC × OUTRA IA
// Depois que o roteiro existe: fazer a voz aqui (grátis) ou copiar o roteiro, gerar a voz fora (Dark Planner, ElevenLabs…)
// e subir o áudio pronto → Vídeo com imagens no modo “Tenho a narração” (o roteiro vira referência; os tempos saem do áudio pelo Whisper).
const VZ = {};
function vozEscolha(el, o) {
  el = typeof el === "string" ? $(el) : el; if (!el) return null;
  const st = { m: "pc" };
  el.classList.add("vzEsc");
  el.innerHTML = `${o.cabecalho ? `<h5>${o.cabecalho}</h5>` : ""}<div class="modos vzOps">
      <button type="button" class="modo" data-vz="pc"><b>🔊 Fazer o áudio aqui</b><small>Voz do PC, grátis.</small><span class="vzRec">👍 Recomendado pra testar rápido</span></button>
      <button type="button" class="modo" data-vz="fora"><b>📋 Copiar o roteiro e gerar a voz em outra IA</b><small>Dark Planner, ElevenLabs… Depois você sobe o áudio aqui.</small><span class="vzRec">👍 Recomendado quando quer voz mais humana</span></button>
    </div>
    ${o.pcBotao ? `<div class="vzPc"><button type="button" class="btn go" data-vzpc>${o.pcBotao.label}</button></div>` : ""}
    <div class="vzFora hidden">
      <ol class="vzPassos">
        <li><button type="button" class="btn" data-vzcopiar>📋 Copiar o roteiro</button> <span class="mu vzNota"></span></li>
        <li>Cole na outra IA (Dark Planner, ElevenLabs…), gere a voz e baixe o arquivo <b>mp3, wav ou m4a</b>.</li>
        <li>Suba o áudio aqui. O vídeo usa a <b>sua</b> narração; a legenda e as imagens seguem o que a voz fala.</li>
      </ol>
      <div class="vzDrop" tabindex="0" role="button" aria-label="Subir o áudio pronto"><input type="file" accept=".mp3,.wav,.m4a,.aac,.ogg,.flac,audio/*" hidden><span class="vzIc">🎙</span><b>Subir o áudio pronto</b><small>arraste o arquivo pra cá ou clique pra escolher</small></div>
      <div class="vzInfo mu"></div>
    </div>`;
  const q = (x) => el.querySelector(x);
  const podeEscrever = () => !!o.escrever && !(o.roteiro() || "").trim() && (!o.podeEscrever || o.podeEscrever());
  const nota = () => {
    const b = q("[data-vzcopiar]"); if (b.disabled) return;
    const w = podeEscrever();
    b.textContent = w ? "✍️ Escrever o roteiro e copiar" : "📋 Copiar o roteiro";
    q(".vzNota").textContent = w ? "a IA do seu PC escreve primeiro (grátis, 1-2 min); você confere o texto antes de copiar" : "";
  };
  const set = (m) => {
    st.m = m;
    el.querySelectorAll("[data-vz]").forEach((b) => b.classList.toggle("on", b.dataset.vz === m));
    q(".vzFora").classList.toggle("hidden", m !== "fora");
    const pc = q(".vzPc"); if (pc) pc.classList.toggle("hidden", m !== "pc");
    nota(); if (o.onModo) o.onModo(m);
  };
  el.querySelectorAll("[data-vz]").forEach((b) => (b.onclick = () => set(b.dataset.vz)));
  if (o.pcBotao) q("[data-vzpc]").onclick = () => o.pcBotao.fn();
  q("[data-vzcopiar]").onclick = async () => {
    const b = q("[data-vzcopiar]");
    let t = (o.roteiro() || "").trim();
    if (!t && podeEscrever()) {
      b.disabled = true; b.textContent = "⏳ escrevendo o roteiro…";
      try { t = ((await o.escrever()) || "").trim(); } catch (e) { toast("❌ " + errTxt(e), 6000); }
      b.disabled = false; nota();
      if (t) return toast("✅ Roteiro pronto! Confira o texto e clique em “📋 Copiar o roteiro”.", 6000);
      return;
    }
    if (!t) return o.semRoteiro ? o.semRoteiro() : toast("Ainda não tem roteiro pra copiar", 4000);
    toast((await copiarTexto(t)) ? "✅ Roteiro copiado! Cole na outra IA e gere a voz." : "❌ Não consegui copiar. Selecione o texto e use Ctrl+C.", 5000);
  };
  const inp = q("input[type=file]"), drop = q(".vzDrop"), info = q(".vzInfo");
  const subir = async (f) => {
    if (!f) return;
    if (!/\.(mp3|wav|m4a|aac|ogg|flac)$/i.test(f.name)) return toast("Envie um áudio mp3, wav ou m4a", 4500);
    info.textContent = "⏳ enviando " + f.name + "…";
    const fd = new FormData(); fd.append("file", f);
    let r; try { r = await api("/api/vi/audio", { method: "POST", body: fd }); } catch (e) { info.textContent = "❌ " + errTxt(e); return; }
    info.textContent = `✅ ${f.name} · ${fmtSeg(r.dur)}`;
    (o.onAudio || openVimg)({ audio: { id: r.audio_id, dur: r.dur, nome: f.name }, roteiro: (o.roteiro() || "").trim(), tema: o.tema ? o.tema() : "", titulo: o.titulo ? o.titulo() : "" });
  };
  drop.onclick = () => inp.click();
  drop.onkeydown = (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); inp.click(); } };
  inp.onclick = (e) => e.stopPropagation();
  inp.onchange = () => { subir(inp.files[0]); inp.value = ""; };
  drop.ondragover = (e) => { e.preventDefault(); drop.classList.add("over"); };
  drop.ondragleave = () => drop.classList.remove("over");
  drop.ondrop = (e) => { e.preventDefault(); drop.classList.remove("over"); subir(e.dataTransfer.files[0]); };
  set("pc");
  return { set, nota, get modo() { return st.m; } };
}
// a IA do PC escreve só o roteiro (sem voz/imagens) → {roteiro, titulo} ou null
function escreverRoteiro(body) {
  return new Promise(async (ok) => {
    let r; try { r = await jpost("/api/vi/roteiro", body); } catch (e) { toast("❌ " + errTxt(e), 6000); return ok(null); }
    acompanhar(r.job, "✍️ A IA do seu PC está escrevendo o roteiro…", (res, fechado) => { if (!fechado) closeModal(); ok(res); }, () => ok(null));
  });
}

// com áudio pronto subido, o botão 🎬 Fazer vídeo volta a aparecer (some só enquanto você ainda não subiu o áudio)
function pedAudioUi(m) {
  const fora = m === "fora", com = fora && !!PED.audio, el = $("#pedido");
  el.classList.toggle("modoFora", fora && !com); el.classList.toggle("comAudio", com);
}
VZ.p = vozEscolha("#pVz", {
  roteiro: () => ($("#pTemRoteiro").checked ? $("#pRoteiro").value : ""),
  podeEscrever: () => !$("#pTemRoteiro").checked,
  semRoteiro: () => erroCampo("#pRoteiro", "Cole o roteiro primeiro"),
  tema: () => $("#pTema").value.trim(), titulo: () => $("#pTema").value.trim(),
  escrever: async () => {
    const tema = $("#pTema").value.trim(); if (!tema) { erroCampo("#pTema", "Escreva o tema primeiro"); return ""; }
    const r = await escreverRoteiro({ tema, duracao: PED.dur, canal: $("#pCanal").value.trim() });
    if (!r) return "";
    $("#pTemRoteiro").checked = true; $("#pRoteiroRow").classList.remove("hidden"); $("#pRoteiro").value = r.roteiro;
    $("#pRoteiro").scrollIntoView({ block: "center", behavior: "smooth" });
    return r.roteiro;
  },
  onModo: (m) => pedAudioUi(m),
  // áudio pronto: fica NESTE pedido (no estilo que você escolheu) — não manda mais pro "Vídeo com imagens"
  onAudio: (pre) => {
    PED.audio = pre.audio; pedAudioUi("fora");
    if (pre.audio.dur) { PED.dur = Math.max(15, Math.round(pre.audio.dur)); try { pedDurs(); } catch (x) { } }
    toast("✅ Narração recebida! O vídeo usa a sua voz no estilo escolhido. Confira o roteiro e clique em Fazer vídeo.", 7000);
  },
});

// ======================================================= VÍDEO COM IMAGENS
const VI = { modo: "tema", estilo: "broll-documentario", dur: 60, estilos: [], audio: null };
async function openVimg(pre) {
  if (!showOnly("#vimg")) return;
   marcaPre("#viMarca");
  if (pre && pre.audio) viComAudio(pre);
  else if (pre && pre.roteiro) { setModoVi("roteiro"); $("#viRoteiro").value = pre.roteiro; if (pre.titulo) $("#viTitulo").value = pre.titulo; toast("✅ Roteiro colado no passo 1. Confira e clique em 🎬 Fazer vídeo.", 4000); }
  else setModoVi(VI.modo);
  renderDurs("#viDurs", VI.dur, (d) => (VI.dur = d), "#viDurNota");
  carregarVozes().catch(() => { });
  if (!VI.estilos.length) { try { VI.estilos = await api("/api/vi/estilos"); } catch (e) { $("#viEstilos").innerHTML = `<div class="mu">❌ ${esc(errTxt(e))}</div>`; return; } }
  renderViEstilos(); viResumo();
}
function setModoVi(m) {
  VI.modo = m;
  $("#viModos").querySelectorAll(".modo").forEach((b) => b.classList.toggle("on", b.dataset.modo === m));
  document.querySelectorAll("#vimg [data-m]").forEach((r) => r.classList.toggle("hidden", !r.dataset.m.split(" ").includes(m)));
  $("#vimg").classList.toggle("modoFora", m !== "audio" && VI.vz === "fora");
  if (VZ.vi) VZ.vi.nota();
  viResumo();
}
function viComAudio(pre) {   // áudio feito em outra IA → modo “Tenho a narração” já preenchido
  VI.audio = pre.audio.id; setModoVi("audio");
  $("#viAudioInfo").textContent = `✅ ${pre.audio.nome} · ${fmtSeg(pre.audio.dur)}`;
  if (pre.roteiro) $("#viRoteiroRef").value = pre.roteiro;
  if (pre.tema) $("#viTemaAudio").value = pre.tema;
  if (pre.titulo && !$("#viTitulo").value.trim()) $("#viTitulo").value = pre.titulo;
  toast("✅ Narração recebida! Está no modo “🎙 Tenho a narração”" + (pre.roteiro ? " com o roteiro como referência" : "") + ". Escolha o estilo e clique em 🎬 Fazer vídeo.", 7000);
}
VZ.vi = vozEscolha("#viVz", {
  roteiro: () => (VI.modo === "roteiro" ? $("#viRoteiro").value : ""),
  podeEscrever: () => VI.modo === "tema",
  semRoteiro: () => erroCampo("#viRoteiro", "Cole o roteiro primeiro"),
  tema: () => $("#viTema").value.trim(), titulo: () => $("#viTitulo").value.trim(),
  escrever: async () => {
    const tema = $("#viTema").value.trim(); if (!tema) { erroCampo("#viTema", "Escreva o tema primeiro"); return ""; }
    const r = await escreverRoteiro({ tema, estilo: VI.estilo, duracao: VI.dur, canal: $("#viCanal").value.trim(), titulo: $("#viTitulo").value.trim() });
    if (!r) return "";
    $("#viRoteiro").value = r.roteiro; if (!$("#viTitulo").value.trim() && r.titulo) $("#viTitulo").value = r.titulo;
    setModoVi("roteiro"); $("#viRoteiro").scrollIntoView({ block: "center", behavior: "smooth" });
    return r.roteiro;
  },
  onModo: (m) => { VI.vz = m; $("#vimg").classList.toggle("modoFora", VI.modo !== "audio" && m === "fora"); },
  onAudio: viComAudio,
});
$("#viModos").onclick = (e) => { const b = e.target.closest("[data-modo]"); if (b) setModoVi(b.dataset.modo); };
function renderViEstilos() {
  $("#viEstilos").innerHTML = VI.estilos.map((e) => `<button class="viEst ${VI.estilo === e.id ? "on" : ""}" data-ve="${esc(e.id)}">
    <div class="th" style="${e.thumb_url ? `background-image:url('${e.thumb_url}')` : ""}">${e.thumb_url ? "" : '<span class="novoArt">📸🎞<br><small>fotos + clipes</small></span>'}</div>
    <div class="tx"><b>🎨 ${esc(e.nome)}</b>${e.novo ? ' <span class="gtag auto">Novo</span>' : ""}${seloPrimeira(e)}<small>${esc(e.descricao)}</small>${bomParaHtml(e)}</div></button>`).join("");
  $("#viEstilos").querySelectorAll("[data-ve]").forEach((b) => (b.onclick = () => { VI.estilo = b.dataset.ve; estiloNovoConferir(VI.estilos, VI.estilo, "#viConferir"); renderViEstilos(); viResumo(); }));
}
function viResumo() {
  const e = VI.estilos.find((x) => x.id === VI.estilo);
  const dur = VI.modo === "tema" ? DUR_OPTS.find(([d]) => d === VI.dur)?.[1] || VI.dur + " s" : "o tamanho do seu " + (VI.modo === "audio" ? "áudio" : "roteiro");
  viCombina();
  $("#viResumo").textContent = e ? `Vai sair: vídeo deitado (16:9) no estilo “${e.nome}”, com ${dur}. ${$("#viConferir").checked ? (e.usado === 0 ? "Estilo novo pra você: antes do vídeo inteiro, você confere as imagens e vê 20 s de amostra." : "Antes de montar, você confere as imagens.") : "Monta direto, sem conferir."} Roda no seu PC, de graça.` : "";
}
$("#viConferir").onchange = viResumo;
$("#viIrRoteiro").onclick = (e) => { e.preventDefault(); openRoteiro(); };
$("#viAudio").onchange = async () => {
  const f = $("#viAudio").files[0]; if (!f) return;
  $("#viAudioInfo").textContent = "⏳ enviando…"; VI.audio = null;
  const fd = new FormData(); fd.append("file", f);
  try { const r = await api("/api/vi/audio", { method: "POST", body: fd }); VI.audio = r.audio_id; $("#viAudioInfo").textContent = `✅ ${f.name} · ${fmtSeg(r.dur)}`; }
  catch (e) { $("#viAudioInfo").textContent = "❌ " + errTxt(e); }
};
$("#viFazer").onclick = async () => {
  if (!(await prontoChecar("vi"))) return;
  if (VI.modo === "tema" && !(await ideiaAuto("#viTema", { formato: "longo" }))) return;
  canalAuto("#viCanal");
  const canal = $("#viCanal").value.trim();
  const erro = (sel, msg) => { const el = $(sel); if (el) { el.focus(); el.classList.add("err"); setTimeout(() => el.classList.remove("err"), 2500); } toast(msg, 4500); };
  if (VI.modo === "tema" && !$("#viTema").value.trim()) return erro("#viTema", "Escreva o tema do vídeo");
  if (VI.modo === "roteiro" && $("#viRoteiro").value.trim().split(/\s+/).length < 15) return erro("#viRoteiro", "Cole o roteiro (pelo menos algumas frases)");
  if (VI.modo === "audio" && !VI.audio) return erro("#viAudio", "Escolha o arquivo de áudio da narração (e espere aparecer ✅)");
  try { localStorage.setItem("pedido_canal", canal); } catch (x) { }
  const body = { modo: VI.modo, tema: VI.modo === "audio" ? $("#viTemaAudio").value.trim() : $("#viTema").value.trim(), roteiro: (VI.modo === "audio" ? $("#viRoteiroRef") : $("#viRoteiro")).value.trim(),
    audio_id: VI.audio, estilo: VI.estilo, duracao: VI.dur, voz: $("#viVoz").value, canal, marca: marcaVal("#viMarca"), titulo: $("#viTitulo").value.trim(), conferir: $("#viConferir").checked, numeros: $("#viNumeros").checked, credito: $("#viCredito").checked };
  let r;
  try { r = await jpost("/api/vi/criar", body); } catch (e) { return toast("❌ " + errTxt(e), 6000); }
  acompanhar(r.job, "🖼 Fazendo o seu vídeo com imagens…", (res, fechado) => {
    if (res.conferir) { if (fechado) { toast("🖼 Imagens prontas! Abra em Meus vídeos → Conferir imagens.", 6000); return; } closeModal(); openConferir(res.pid); toast("✅ Imagens escolhidas. Confira e clique em ▶ Fazer o vídeo.", 5000); return; }
    viPronto(res, fechado);
  });
};
function viPronto(res, fechado) {
  if (fechado) return toast("✅ Vídeo pronto: " + res.name, 6000);
  $("#mTitle").textContent = res.rendered ? "✅ Vídeo pronto!" : "⚠ Montado, mas sem vídeo final";
  $("#mMsg").textContent = `${res.name}\n${res.duracao ? "Duração: " + fmtSeg(res.duracao) + " · " : ""}${res.minutos ? "Tempo de máquina: " + res.minutos + " min · " : ""}Feito no seu PC, de graça\n📁 ${amigavel(res.folder)}`;
  if (res.rendered) mbtnVer(res.pid, "go");
  mbtn("✏ Abrir no editor", () => { closeModal(); openProject(res.pid); });
  if (res.rendered) { mlinksBaixar(res.pid, res.name); mbtnCapa(res.pid); }
  mbtn("📂 Abrir pasta", () => api(`/api/open/${res.pid}?what=folder`, { method: "POST" }));
  mbtn("Fechar", closeModal);
  if (res.rendered && res.pid) { const bx = document.createElement("div"); bx.className = "revBox"; $("#mBtns").before(bx); revisarEm(bx, res.pid); }
}

// ======================================================= CONFERIR IMAGENS
const CF = { pid: null, d: null, alvo: null };
async function openConferir(pid) {
  if (!showOnly("#conferir")) return;
  CF.pid = pid; $("#cfGrid").innerHTML = '<div class="card">Carregando as cenas…</div>';
  try { CF.d = await api("/api/vi/" + pid); } catch (e) { $("#cfGrid").innerHTML = `<div class="card">❌ ${esc(errTxt(e))}</div>`; return; }
  TELA.video = CF.d.titulo || "";
  renderConferir();
}
function mediaCena(e) {
  if (!e || !e.url_local) return '<div class="cfVazio">sem imagem</div>';
  return e.tipo === "video" ? `<video src="${e.url_local}" class="apV" muted loop playsinline preload="metadata" onmouseenter="this.play()" onmouseleave="if(!AP.ativos.has(this))this.pause()"></video>` : `<img src="${e.url_local}" alt="" loading="lazy">`;
}
function cardCena(c) {
  const e = c.escolha || {};
  const fm = (t) => { const m = Math.floor(t / 60); return m + ":" + String(Math.floor(t % 60)).padStart(2, "0"); };
  const opc = (c.candidatos || []).map((o, k) => `<button class="op ${o.url === e.url ? "on" : ""}" data-c="${k}" title="${esc(o.fonte + " · " + (o.titulo || "") + (o.licenca ? " · " + o.licenca : ""))}"><img src="${esc(o.thumb || o.url)}" alt="" loading="lazy" referrerpolicy="no-referrer">${o.tipo === "video" ? '<span class="opv">▶</span>' : ""}<span class="opf">${esc(o.fonte)}</span></button>`).join("");
  return `<div class="cf" data-i="${c.i}">
    <div class="cfMedia">${mediaCena(e)}<span class="cfT">${c.i + 1} · ${fm(c.s)}</span>${e.fonte ? `<span class="cfFonte">${esc(e.fonte)}${e.tipo === "video" ? " · clipe" : ""}</span>` : ""}${e.repetida ? '<span class="cfRep">repete a anterior</span>' : ""}${e.fraca ? '<span class="cfRep" style="background:#c0392b;color:#fff" title="O computador achou que esta imagem não combina muito com a frase. Clique numa opção de baixo pra trocar (ou deixe assim).">⚠ Confira esta</span>' : e.trocou_de ? '<span class="cfRep" title="O computador trocou sozinho por uma imagem que combina mais com a frase">✔ Melhorada</span>' : ""}<div class="cfLoad hidden">⏳</div></div>
    <p class="cfTexto">“${esc(c.texto)}”</p>
    <div class="cfOpc">${opc || '<span class="mu">Sem outras opções — busque com outra palavra ou suba do PC.</span>'}</div>
    <div class="cfBusca"><input type="text" placeholder="Outra palavra (ex.: torre de ferro)" value="" /><button class="btn mini" data-buscar="1" title="Procurar imagens com esta palavra">🔎 Buscar</button><button class="btn mini" data-subir="1" title="Usar uma foto ou vídeo do seu computador">📁 Do meu PC</button></div>
    <small class="cfQ mu">busca usada: ${esc(c.query || "—")}</small>
  </div>`;
}
function renderConferir() {
  const d = CF.d;
  $("#cfSub").textContent = `“${d.titulo || ""}” · ${d.cenas.length} cenas · estilo ${d.estilo_nome || d.estilo}. Cada quadro é um pedaço da narração. Se a imagem não combina, clique numa opção de baixo, suba uma do seu PC ou procure com outra palavra.` + (d.checagem ? ` ✅ O computador conferiu ${d.checagem.checadas} imagens e trocou ${d.checagem.trocadas} sozinho${d.checagem.fracas ? `; ${d.checagem.fracas} estão marcadas com ⚠ pra você dar uma olhada` : ""}.` : "");
  $("#cfGrid").innerHTML = d.cenas.map(cardCena).join("");
  const pronto = d.estado === "pronto";
  ["#cfRender", "#cfRender2"].forEach((s) => ($(s).textContent = pronto ? "▶ Montar o vídeo de novo" : s === "#cfRender" ? "▶ Fazer o vídeo" : "▶ Tudo certo — fazer o vídeo"));
}
function cfCarregando(i, on) { const el = document.querySelector(`.cf[data-i="${i}"] .cfLoad`); if (el) el.classList.toggle("hidden", !on); }
$("#cfGrid").onclick = async (ev) => {
  const card = ev.target.closest(".cf"); if (!card) return;
  const i = +card.dataset.i;
  const op = ev.target.closest("[data-c]");
  if (op) {
    cfCarregando(i, true);
    try { const r = await jpost(`/api/vi/${CF.pid}/escolher`, { i, c: +op.dataset.c }); CF.d.cenas = r.cenas; renderConferir(); toast("✅ Imagem trocada"); }
    catch (e) { cfCarregando(i, false); toast("❌ " + errTxt(e), 5000); }
    return;
  }
  if (ev.target.closest("[data-buscar]")) return cfBuscar(card, i);
  if (ev.target.closest("[data-subir]")) { CF.alvo = i; $("#cfFile").value = ""; $("#cfFile").click(); }
};
$("#cfGrid").onkeydown = (ev) => { if (ev.key === "Enter" && ev.target.matches(".cfBusca input")) { const card = ev.target.closest(".cf"); cfBuscar(card, +card.dataset.i); } };
async function cfBuscar(card, i) {
  const q = card.querySelector(".cfBusca input").value.trim();
  if (!q) return toast("Escreva uma palavra pra buscar (ex.: navio antigo)");
  cfCarregando(i, true);
  try {
    const r = await jpost(`/api/vi/${CF.pid}/buscar`, { i, q });
    if (!r.ok) { cfCarregando(i, false); return toast(r.msg, 5000); }
    CF.d.cenas[i] = { ...CF.d.cenas[i], ...r.cena, escolha: CF.d.cenas[i].escolha };
    card.outerHTML = cardCena(CF.d.cenas[i]);
    toast(`🔎 ${r.cena.candidatos.length} opções — clique numa pra usar`);
  } catch (e) { cfCarregando(i, false); toast("❌ " + errTxt(e), 5000); }
}
$("#cfFile").onchange = async () => {
  const f = $("#cfFile").files[0]; if (!f || CF.alvo == null) return;
  const i = CF.alvo; cfCarregando(i, true);
  const fd = new FormData(); fd.append("file", f);
  try { const r = await api(`/api/vi/${CF.pid}/subir/${i}`, { method: "POST", body: fd }); CF.d.cenas = r.cenas; renderConferir(); toast("✅ Usando o seu arquivo"); }
  catch (e) { cfCarregando(i, false); toast("❌ " + errTxt(e), 5000); }
};
async function cfRenderizar() {
  let r;
  try { r = await jpost(`/api/vi/${CF.pid}/renderizar`, {}); } catch (e) { return toast("❌ " + errTxt(e), 6000); }
  acompanhar(r.job, "🎬 Montando o seu vídeo…", (res, fechado) => { viPronto(res, fechado); });
}
$("#cfRender").onclick = $("#cfRender2").onclick = cfRenderizar;
$("#cfMeus").onclick = loadHome;

// ======================================================= ROTEIRO PRONTO
const RT = { acao: "escrever", dur: 300, job: null, res: null };
const RT_BTN = { transcrever: "📄 Pegar o roteiro", estrutura: "🧩 Ver a estrutura", escrever: "✍️ Escrever roteiro", melhorar: "✨ Melhorar meu roteiro" };
async function openRoteiro(rid) {
  if (!showOnly("#roteiro")) return;
  $("#roteiro").classList.remove("compacto"); const ro = $("#rtOutro"); if (ro) ro.parentNode.remove();
  setAcaoRt(RT.acao);
  renderDurs("#rtDurs", RT.dur, (d) => (RT.dur = d), null, [["igual", "Igual ao original"], ...DUR_OPTS.filter(([d]) => d <= 1200)]);
  if (typeof rid === "string") {
    try {
      RT.res = await api("/api/roteiro/" + encodeURIComponent(rid)); renderRtRes(RT.res);
      if (RT.res.acao) setAcaoRt(RT.res.acao);
      if (RT.res.video?.url) $("#rtUrl").value = RT.res.video.url;
      if (RT.res.tema) { $("#rtTema").value = RT.res.tema; $("#rtTemaM").value = RT.res.tema; }
      $("#roteiro").classList.add("compacto");
      $("#rtRes").insertAdjacentHTML("afterbegin", '<div class="rtNovo"><button class="btn" id="rtOutro">➕ Fazer outro roteiro</button></div>');
      $("#rtOutro").onclick = () => { $("#roteiro").classList.remove("compacto"); $("#rtOutro").parentNode.remove(); };
    } catch (e) { toast("❌ " + errTxt(e)); }
  }
  rtHistorico();
}
function setAcaoRt(a) {
  RT.acao = a;
  $("#rtAcoes").querySelectorAll(".modo").forEach((b) => b.classList.toggle("on", b.dataset.acao === a));
  document.querySelectorAll("#roteiro [data-a]").forEach((r) => r.classList.toggle("hidden", !r.dataset.a.split(" ").includes(a)));
  $("#rtFazer").textContent = RT_BTN[a];
}
$("#rtAcoes").onclick = (e) => { const b = e.target.closest("[data-acao]"); if (b) setAcaoRt(b.dataset.acao); };
$("#rtVer").onclick = () => { const u = $("#rtUrl").value.trim(); if (!urlOk(u)) return toast("Cole um link válido (começa com https://)"); window.open(u, "_blank"); };
async function rtHistorico() {
  let l = []; try { l = await api("/api/roteiros"); } catch (e) { }
  const nomes = { transcrever: "📄 Roteiro do vídeo", estrutura: "🧩 Estrutura", escrever: "✍️ Roteiro novo", melhorar: "✨ Melhorado" };
  $("#rtHist").classList.toggle("hidden", !l.length);
  $("#rtHist").innerHTML = `<h4>Feitos antes</h4>` + l.map((r) => `<button class="chip" data-rid="${esc(r.rid)}">${nomes[r.acao] || ""} · ${esc((r.tema || r.video || "").slice(0, 46))}</button>`).join(" ");
  $("#rtHist").querySelectorAll("[data-rid]").forEach((b) => (b.onclick = () => openRoteiro(b.dataset.rid)));
}
$("#rtFazer").onclick = async () => {
  const a = RT.acao, url = $("#rtUrl").value.trim();
  if (a !== "melhorar" && !urlOk(url)) { $("#rtUrl").focus(); return toast("Cole o link do vídeo (começa com https://)", 4000); }
  if (a === "escrever" && !(await ideiaAuto("#rtTema", { formato: "longo", ref: url }))) return;
  if (a === "melhorar" && $("#rtTexto").value.trim().split(/\s+/).length < 30) { $("#rtTexto").focus(); return toast("Cole o seu roteiro (pelo menos um parágrafo)", 4000); }
  const body = { acao: a, url, tema: a === "melhorar" ? $("#rtTemaM").value.trim() : $("#rtTema").value.trim(), duracao: RT.dur, texto: $("#rtTexto").value, notas: $("#rtNotas").value.trim() };
  let r; try { r = await jpost("/api/roteiro", body); } catch (e) { return toast("❌ " + errTxt(e), 6000); }
  RT.job = r.job; $("#rtProg").classList.remove("hidden"); $("#rtFazer").disabled = true; $("#rtBar").style.width = "2%"; $("#rtMsg").textContent = "Começando…";
  const tick = async () => {
    let j; try { j = await api("/api/job/" + RT.job); } catch (e) { return setTimeout(tick, 2500); }
    $("#rtBar").style.width = Math.max(2, j.pct) + "%";
    const eta = j.eta;
    $("#rtMsg").textContent = `${Math.round(j.pct)}% — ${j.msg}${eta ? " · faltam ~" + fmtSeg(eta) : ""}`;
    filaAtualizar();
    if (!j.done) return setTimeout(tick, 1500);
    $("#rtProg").classList.add("hidden"); $("#rtFazer").disabled = false;
    if (j.error) return toast("❌ " + (j.status === "cancelado" ? "Cancelado" : j.error.split("\n").slice(-2).join(" ")), 8000);
    RT.res = j.result; renderRtRes(RT.res); rtHistorico();
    setTimeout(() => $("#rtRes").scrollIntoView({ behavior: "smooth" }), 80);
  };
  tick();
};
$("#rtCancelar").onclick = async () => { if (RT.job) { await jpost(`/api/jobs/${RT.job}/cancelar`, {}); toast("Cancelando…"); } };
const btnCopiar = (id, label = "📋 Copiar") => `<button class="btn" data-copiar="${id}">${label}</button>`;
function renderRtRes(r) {
  const v = r.video || {}, est = r.estrutura, kit = r.kit || {};
  const fm = (t) => { t = Math.round(t || 0); const h = Math.floor(t / 3600), m = Math.floor(t % 3600 / 60), s = t % 60; return (h ? h + ":" + String(m).padStart(2, "0") : m) + ":" + String(s).padStart(2, "0"); };
  let h = "";
  if (v.titulo) h += `<div class="card rtCard rtVid"><div class="mu">Vídeo analisado</div><h4>${esc(v.titulo)}</h4><div class="mu">${v.canal_url ? `<a href="${esc(v.canal_url)}" target="_blank" rel="noopener">${esc(v.canal)}</a>` : esc(v.canal || "")} · ${fm(v.duracao)} · ${v.views ? Number(v.views).toLocaleString("pt-BR") + " views" : ""} · ${v.palavras || 0} palavras (${v.ppm || "?"} por minuto) · texto: ${esc(v.fonte_transcricao || "")}</div></div>`;
  if (r.acao === "transcrever" && r.transcricao) {
    h += `<div class="card rtCard"><div class="rtH"><h4>📄 Roteiro deste vídeo</h4><div class="grow"></div>${btnCopiar("rtTxtTrans")}<button class="btn go" data-usar="rtTxtTrans">🎬 Usar no Vídeo com imagens</button></div>
      <textarea id="rtTxtTrans" class="rtArea" rows="16">${esc(r.transcricao)}</textarea><p class="mu">É o texto do vídeo original (pra estudar). Pra publicar, escreva o seu: use “✍️ Escrever um roteiro novo nesse formato”.</p></div>`;
  }
  if (est) {
    const cores = ["#ffb020", "#3ad7ff", "#b6ff3a", "#ff5a36", "#a78bfa", "#2fbf71", "#f472b6", "#facc15"];
    h += `<div class="card rtCard"><div class="rtH"><h4>🧩 Estrutura: ${esc(est.nome_formato || "")}</h4><div class="grow"></div><button class="btn" data-copiarjson="1">📋 Copiar</button></div>
      <p><b>Promessa:</b> ${esc(est.promessa || "")}</p>
      <div class="rtGancho"><b>🪝 Gancho ${esc(est.gancho?.tempo || "")}</b> — ${esc(est.gancho?.como_funciona || "")}<br><span class="mu">Molde de frase:</span> <i>${esc(est.gancho?.modelo_de_frase || "")}</i></div>
      <div class="rtBarra">${(est.blocos || []).map((b, k) => `<span style="width:${b.pct}%;background:${cores[k % cores.length]}" title="${esc(b.nome)} · ${b.pct}%"></span>`).join("")}</div>
      <ol class="rtBlocos">${(est.blocos || []).map((b, k) => `<li><span class="dot" style="background:${cores[k % cores.length]}"></span><b>${esc(b.inicio || "")}</b> ${esc(b.nome)} <span class="mu">(${b.pct}%)</span><br><small>${esc(b.o_que_acontece || "")}</small></li>`).join("")}</ol>
      ${(est.viradas || []).length ? `<p><b>🔄 Viradas</b></p><ul class="rtViradas">${est.viradas.map((x) => `<li><b>${esc(x.tempo || "")}</b> ${esc(x.o_que_muda || "")}</li>`).join("")}</ul>` : ""}
      <p><b>📣 CTA:</b> ${esc(est.cta?.onde || "")} — ${esc(est.cta?.como || "")}</p>
      <p><b>🎙 Tom:</b> ${esc(est.tom || "")} · <b>Ritmo:</b> ${esc(est.ritmo || "")}</p>
      <p><b>🏷 Molde de título:</b> ${esc(est.padrao_titulo || "")}</p>
      ${(est.pontos_fracos || []).length ? `<p><b>💡 Dá pra fazer melhor:</b></p><ul>${est.pontos_fracos.map((x) => `<li>${esc(x)}</li>`).join("")}</ul>` : ""}</div>`;
  }
  if (r.roteiro) {
    const titulo = r.acao === "melhorar" ? "✨ Antes × depois" : "✍️ Seu roteiro novo";
    const n = r.roteiro.split(/\s+/).length;
    h += `<div class="card rtCard"><div class="rtH"><h4>${titulo}</h4><span class="mu">${n} palavras · ~${fmtSeg(n / 150 * 60)} de narração</span><div class="grow"></div>${btnCopiar("rtTxtNovo")}<button class="btn go" data-usar="rtTxtNovo">🎬 Usar no Vídeo com imagens</button></div>
      <div class="motor"><span class="selo free">🆓 Feito no Ollama — grátis, no seu PC</span></div>
      ${r.acao === "melhorar" ? `<div class="rtLado"><div><div class="mu">ANTES (o seu)</div><textarea class="rtArea" rows="16" readonly>${esc(r.antes || "")}</textarea></div><div><div class="mu">DEPOIS (melhorado)</div><textarea id="rtTxtNovo" class="rtArea" rows="16">${esc(r.roteiro)}</textarea></div></div>`
        : `<textarea id="rtTxtNovo" class="rtArea" rows="16">${esc(r.roteiro)}</textarea>`}
      <div class="rtAviso">⚠ <b>Confira os fatos antes de publicar.</b> A IA local pode errar nomes, números e datas.${r.fonte_fatos ? ` Fatos de referência usados: <a href="${esc(r.fonte_fatos.url)}" target="_blank" rel="noopener">Wikipedia — ${esc(r.fonte_fatos.titulo)}</a>.` : ""}${r.frases_cortadas ? ` (${r.frases_cortadas} frase(s) repetida(s) foram cortadas automaticamente.)` : ""}${r.aviso_tamanho ? "<br>" + esc(r.aviso_tamanho) : ""}${r.aviso_idioma ? "<br>" + esc(r.aviso_idioma) : ""}
        ${(kit.fatos_a_conferir || []).length ? `<ul>${kit.fatos_a_conferir.map((x) => `<li>${esc(x)}</li>`).join("")}</ul>` : ""}</div>
      <div data-vzrt="rtTxtNovo"></div>
      <div class="claudeBox"><div class="rtH"><b>🧠 Revisar com o Claude</b><span class="warnTok" title="Usa a sua assinatura do Claude (sem cobrança por vídeo)">ⓘ Usa o Claude</span><div class="grow"></div><button class="btn" id="rtClaude">🧠 Revisar roteiro com o Claude</button></div><div id="rtClaudeArea"></div></div></div>`;
  }
  if (kit.titulos && kit.titulos.length) {
    h += `<div class="card rtCard"><div class="rtH"><h4>📦 Kit de publicação</h4></div>
      <p><b>Títulos</b></p>${kit.titulos.map((t, k) => `<div class="kitT"><span>${k === 0 ? "⭐" : "↳"} ${esc(t)}${kit.titulos_pt && kit.titulos_pt[k] ? `<br><small class="mu">PT: ${esc(kit.titulos_pt[k])}</small>` : ""}</span><button class="btn mini" data-ctxt="${esc(t)}">📋</button></div>`).join("")}
      <div class="rtH"><b>Descrição</b><div class="grow"></div>${btnCopiar("rtDesc")}</div><textarea id="rtDesc" class="rtArea" rows="7">${esc(kit.descricao || "")}</textarea>
      <div class="rtH"><b>Tags</b><div class="grow"></div><button class="btn" data-ctxt="${esc((kit.tags || []).join(", "))}">📋 Copiar tags</button></div><div class="tags">${(kit.tags || []).map((t) => `<span class="tag">${esc(t)}</span>`).join(" ")}</div></div>`;
  }
  $("#rtRes").innerHTML = h || '<div class="card">Nada pra mostrar.</div>';
  const box = $("#rtRes");
  box.querySelectorAll("[data-copiar]").forEach((b) => (b.onclick = async () => toast((await copiarTexto($("#" + b.dataset.copiar).value)) ? "✅ Copiado!" : "❌ Não consegui copiar")));
  box.querySelectorAll("[data-ctxt]").forEach((b) => (b.onclick = async () => toast((await copiarTexto(b.dataset.ctxt)) ? "✅ Copiado!" : "❌ Não consegui copiar")));
  box.querySelectorAll("[data-copiarjson]").forEach((b) => (b.onclick = async () => {
    const t = [`Formato: ${est.nome_formato}`, `Promessa: ${est.promessa}`, `Gancho (${est.gancho?.tempo}): ${est.gancho?.como_funciona} — molde: ${est.gancho?.modelo_de_frase}`, "Blocos:", ...(est.blocos || []).map((x) => `  ${x.inicio} ${x.nome} (${x.pct}%): ${x.o_que_acontece}`), "Viradas:", ...(est.viradas || []).map((x) => `  ${x.tempo} ${x.o_que_muda}`), `CTA: ${est.cta?.onde} — ${est.cta?.como}`, `Tom: ${est.tom} · Ritmo: ${est.ritmo}`, `Título: ${est.padrao_titulo}`].join("\n");
    toast((await copiarTexto(t)) ? "✅ Estrutura copiada!" : "❌ Não consegui copiar");
  }));
  box.querySelectorAll("[data-usar]").forEach((b) => (b.onclick = () => openVimg({ roteiro: $("#" + b.dataset.usar).value, titulo: (kit.titulos || [])[0] || "" })));
  const bc = $("#rtClaude"); if (bc) bc.onclick = () => rtClaude(r);
  box.querySelectorAll("[data-vzrt]").forEach((el) => {
    const ta = () => $("#" + el.dataset.vzrt), tit = (kit.titulos || [])[0] || "";
    vozEscolha(el, { cabecalho: "🎙 Roteiro pronto. E a narração?", roteiro: () => (ta() ? ta().value : ""), tema: () => r.tema || tit, titulo: () => tit,
      pcBotao: { label: "🎬 Fazer o vídeo com a voz do PC", fn: () => openVimg({ roteiro: ta().value, titulo: tit }) } });
  });
}
async function rtClaude(r) {
  const area = $("#rtClaudeArea"), rot = $("#rtTxtNovo").value;
  area.innerHTML = '<p class="mu">Montando o pedido…</p>';
  let p; try { p = await jpost("/api/roteiro/claude/pedido", { roteiro: rot, tema: r.tema || "" }); } catch (e) { area.innerHTML = `<p>❌ ${esc(errTxt(e))}</p>`; return; }
  const est = p.estimativa;
  area.innerHTML = `${p.tem_chave ? `<div class="claudeApi"><b>Pela API (chave dos Ajustes, ${esc(p.modelo)})</b> ${est ? "" : esc(p.erro_estimativa || "")}<br><button class="btn go" id="rtClaudeApi">🧠 Revisar agora</button></div>` : ""}
    <p><b>${p.tem_chave ? "Ou, sem API:" : "Como fazer:"}</b> copie o pedido abaixo, <b>cole no chat do Claude</b> e depois cole a resposta aqui.</p>
    <div class="rtH"><button class="btn" id="rtClaudeCopiar">📋 Copiar pedido pro Claude</button><span class="mu">roteiro atual + instruções de revisão</span></div>
    <textarea id="rtClaudeResp" class="rtArea" rows="7" placeholder="Colar roteiro revisado (a resposta do Claude)"></textarea>
    <button class="btn ok" id="rtClaudeUsar">↺ Substituir o roteiro pelo revisado</button>`;
  $("#rtClaudeCopiar").onclick = async () => toast((await copiarTexto(p.texto)) ? "✅ Pedido copiado! Cole no chat do Claude (Ctrl+V)" : "❌ Não consegui copiar", 4500);
  $("#rtClaudeUsar").onclick = () => {
    let t = $("#rtClaudeResp").value.trim(); if (!t) return toast("Cole aqui a resposta do Claude primeiro");
    t = t.split(/\n-{3,}\s*\n/)[0].trim();
    $("#rtTxtNovo").value = t; toast("✅ Roteiro substituído pelo revisado");
  };
  const ba = $("#rtClaudeApi");
  if (ba) ba.onclick = async () => {
    if (!confirm("Isso usa a chave do Claude que está nos Ajustes. Continuar?")) return;
    ba.disabled = true; ba.textContent = "⏳ O Claude está revisando…";
    try {
      const x = await jpost("/api/roteiro/claude/revisar", { roteiro: $("#rtTxtNovo").value, tema: r.tema || "" });
      $("#rtTxtNovo").value = x.roteiro;
      toast("✅ Revisado pelo Claude", 6000);
      if ((x.fatos || []).length) area.insertAdjacentHTML("beforeend", `<div class="rtAviso">⚠ <b>Fatos a conferir (Claude):</b><ul>${x.fatos.map((f) => `<li>${esc(f)}</li>`).join("")}</ul></div>`);
    } catch (e) { toast("❌ " + errTxt(e), 6000); }
    ba.disabled = false; ba.textContent = "🧠 Revisar agora";
  };
}

// ======================================================= AJUSTES
const AJU = { d: null };
const AJ_CAMPOS = { ollama: "#ajModelo", voz: "#ajVoz", vsremoto: "#ajVSurl", ollama_url: "#ajOllUrl", idioma: "#ajIdioma", pexels: "#ajPexels", pixabay: "#ajPixabay", anthropic: "#ajAnthropic",
  gemini: "#ajGemini", elevenlabs: "#ajEleven", fish: "#ajFish", serper: "#ajSerper", youtube: "#ajYoutube", europeana: "#ajEuropeana", vimeo: "#ajVimeo", serpapi: "#ajSerpapi", hf: "#ajHf" };
const AJ_CHAVE_CAMPO = { gemini: "gemini_key", elevenlabs: "elevenlabs_key", fish: "fish_key", serper: "serper_key", youtube: "youtube_key", europeana: "europeana_key", vimeo: "vimeo_token", serpapi: "serpapi_key", hf: "hf_token" };
async function openAjustes() {
  if (!showOnly("#ajustes")) return;
  try { AJU.d = await api("/api/ajustes"); } catch (e) { return toast("❌ " + errTxt(e)); }
  const a = AJU.d;
  let ms = []; try { ms = await api("/api/ajustes/modelos"); } catch (e) { }
  $("#ajModelo").innerHTML = (ms.length ? ms : [{ nome: a.modelo_ollama }]).filter((m) => !m.nuvem || m.nome === a.modelo_ollama).sort((x, y) => (y.nome.startsWith("qwen2.5:7b") ? 1 : 0) - (x.nome.startsWith("qwen2.5:7b") ? 1 : 0)).map((m) => `<option value="${esc(m.nome)}">${esc(m.nome)}${m.gb ? ` · ${m.gb} GB` : ""}${m.nuvem ? " (nuvem — não é local)" : ""}${m.nome.startsWith("mistral") ? " (melhor português, mas pesado: trava se a placa estiver ocupada)" : m.nome.startsWith("qwen2.5:7b") ? " (recomendado: rápido)" : ""}</option>`).join("");
  $("#ajModelo").value = a.modelo_ollama;
  $("#ajModeloClaude").value = a.modelo_claude || "sonnet";
  $("#ajFishModelo").value = a.fish_modelo || "drama-3";
  if (!ms.length) $("#ajustes [data-item=ollama] .ajR").innerHTML = '<span class="bad"><svg class="ic st"><use href="#i-xc"/></svg> A IA do PC não respondeu. Abra o programa da IA (ícone da lhama) e clique em Testar.</span>';
  $("#ajIdioma").innerHTML = a.idiomas.map((i) => `<option value="${i.id}">${esc(i.nome)}</option>`).join(""); $("#ajIdioma").value = a.idioma;
  $("#ajPexels").value = a.pexels_key || ""; $("#ajPixabay").value = a.pixabay_key || ""; $("#ajAnthropic").value = a.anthropic_key || "";
  Object.entries(AJ_CHAVE_CAMPO).forEach(([it, k]) => { const el = $(AJ_CAMPOS[it]); el.value = ""; el.placeholder = (a.chaves_ok || {})[k] ? "já salva — cole outra só se quiser trocar" : "cole a chave aqui"; });
  $("#ajPastaNome").textContent = a.pasta_saida_nome; $("#ajVSurl").value = a.vs_remoto_url || ""; $("#ajOllUrl").value = a.ollama_url || "";
  await carregarVozes(true); $("#ajVoz").value = a.voz;
  ajVSCarregar();
}
// ---- VoiceStudio: baixar/instalar + ajuda do Claude (se der erro)
const VS = { d: null };
async function ajVSCarregar() {
  let d; try { d = VS.d = await api("/api/voicestudio"); } catch (e) { $("#ajVSinfo").textContent = "Não consegui verificar."; return; }
  const ult = d.ultima ? `última versão ${d.ultima.tag} (instalador ~${d.ultima.mb} MB)` : "sem conexão com o GitHub agora";
  $("#ajVSinfo").textContent = !d.windows ? "Este botão instala só no Windows."
    : d.instalado ? `✅ Instalado${d.versao ? " (versão " + d.versao + ")" : ""}. Vozes clonadas lá aparecem na aba 🎙 Minhas vozes.`
    : `Não instalado · ${ult}. App grátis e local; precisa de uns 8-10 GB livres.`;
  $("#ajVSinst").classList.toggle("hidden", !d.windows || d.instalado);
  $("#ajVSabrir").classList.toggle("hidden", !d.instalado);
  $("#ajVSajuda").classList.toggle("hidden", !d.claude);
}
function vsModalAjuda(msg) {   // abre o Claude (claude -p) com o log da instalação e mostra o resumo dele
  jpost("/api/voicestudio/ajuda", { texto: msg || "" }).then((r) => acompanhar(r.job, "🤖 Claude ajudando na instalação…", (res) => {
    $("#mTitle").textContent = res.instalado ? "✅ VoiceStudio instalado" : "ℹ️ Claude analisou a instalação";
    $("#mMsg").textContent = res.texto; $("#mBar").style.width = "100%"; $("#mBtns").innerHTML = "";
    if (!res.instalado) mbtn("🤖 Pedir de novo", () => vsModalAjuda(""));
    mbtn("Fechar", () => { closeModal(); ajVSCarregar(); }, "go");
  }, (j, fechado) => { if (fechado) return; $("#mTitle").textContent = "❌ O Claude não conseguiu"; $("#mMsg").textContent = erroCurto(j.error); $("#mBtns").innerHTML = ""; mbtn("Fechar", closeModal, "go"); return "tratado"; }))
    .catch((e) => toast("❌ " + errTxt(e), 7000));
}
$("#ajVSajuda").onclick = () => {
  const t = prompt("Quer contar o que está acontecendo? (pode deixar vazio — o Claude lê o log sozinho)", "");
  if (t !== null) vsModalAjuda(t);
};
$("#ajVSabrir").onclick = async () => { try { await jpost("/api/voicestudio/abrir", {}); toast("▶ Abrindo o VoiceStudio…", 3000); } catch (e) { toast("❌ " + errTxt(e), 6000); } };
$("#ajVSinst").onclick = async () => {
  const d = VS.d || {};
  if (!confirm(`Baixar e instalar o VoiceStudio${d.ultima ? " " + d.ultima.tag : ""}?\n\n• Baixa ~${d.ultima ? d.ultima.mb : 230} MB do GitHub oficial (debpalash/VoiceStudio) e confere o SHA-256.\n• Abre o instalador dele: se o Windows perguntar “Permitir alterações?”, clique em Sim.\n• Os modelos de voz (vários GB) baixam depois, dentro do próprio app.\n• Sem placa NVIDIA ele roda na CPU (mais lento).\n• O modelo de voz padrão tem licença NÃO comercial; clone só vozes com autorização.\n\nSe der erro, o Claude instalado no PC pode te ajudar.`)) return;
  let r; try { r = await jpost("/api/voicestudio/instalar", {}); } catch (e) { return toast("❌ " + errTxt(e), 7000); }
  acompanhar(r.job, "⬇ Instalando o VoiceStudio…", (res) => {
    $("#mTitle").textContent = "✅ VoiceStudio instalado"; $("#mMsg").textContent = (res.ja_tinha ? "Ele já estava instalado.\n" : "") + "Abra o app, deixe ele baixar um modelo de voz (pergunta antes) e clone/crie vozes. Elas aparecem aqui em 🎙 Minhas vozes → Vozes do VoiceStudio.";
    $("#mBtns").innerHTML = ""; mbtn("▶ Abrir o VoiceStudio", () => { jpost("/api/voicestudio/abrir", {}).catch(() => { }); closeModal(); }, "go"); mbtn("Fechar", closeModal);
    ajVSCarregar();
  }, (j, fechado) => {
    if (fechado || j.status === "cancelado") return;
    $("#mTitle").textContent = "❌ A instalação deu erro"; $("#mMsg").textContent = erroCurto(j.error) + "\n\nQuer que o Claude instalado no seu PC leia o log e tente resolver?";
    $("#mBtns").innerHTML = ""; mbtn("🤖 Pedir ajuda ao Claude", () => vsModalAjuda("A instalação pelo botão do painel deu este erro:\n" + String(j.error || "").slice(0, 1200)), "go"); mbtn("Fechar", closeModal); ajVSCarregar();
    return "tratado";
  });
};
$("#ajVoz").addEventListener("change", () => ajTestar("voz"));   // trocou a voz → prévia na hora
function ajColetar() { return { vs_remoto_url: $("#ajVSurl").value.trim(), ollama_url: $("#ajOllUrl").value.trim(), modelo_ollama: $("#ajModelo").value, modelo_claude: $("#ajModeloClaude").value, fish_modelo: $("#ajFishModelo").value, voz: $("#ajVoz").value, idioma: $("#ajIdioma").value, pexels_key: $("#ajPexels").value.trim(), pixabay_key: $("#ajPixabay").value.trim(), anthropic_key: $("#ajAnthropic").value.trim(),
  ...Object.fromEntries(Object.entries(AJ_CHAVE_CAMPO).map(([it, k]) => [k, $(AJ_CAMPOS[it]).value.trim()])) }; }
async function ajTestar(item) {
  const out = $(`#ajustes [data-item=${item}] .ajR`);
  out.innerHTML = '<span class="mu">testando…</span>';
  const campo = AJ_CAMPOS[item];
  try {
    const r = await jpost("/api/ajustes/testar", { item, valor: campo ? $(campo).value.trim() : "" });
    out.innerHTML = r.ok === null ? `<span class="mu">${esc(r.msg)}</span>` : `<span class="${r.ok ? "good" : "bad"}">${r.ok ? '<svg class="ic st"><use href="#i-checkc"/></svg>' : '<svg class="ic st"><use href="#i-xc"/></svg>'} ${esc(r.msg)}</span>`;
    if (r.audio) { out.insertAdjacentHTML("beforeend", ` <audio class="ajPlay" controls autoplay src="${r.audio}"></audio>`); }
    return r.ok;
  } catch (e) { out.innerHTML = `<span class="bad"><svg class="ic st"><use href="#i-xc"/></svg> ${esc(errTxt(e))}</span>`; return false; }
}
$("#ajustes").onclick = (e) => { const b = e.target.closest("[data-testar]"); if (b) ajTestar(b.dataset.testar); };
$("#ajIdioma").onchange = async () => { AJU.d.idioma = $("#ajIdioma").value; await carregarVozes(true); };
$("#ajSalvar").onclick = async () => {
  try { AJU.d = await jpost("/api/ajustes", ajColetar()); VOZES.lista = null; await carregarVozes(true); $("#ajVoz").value = AJU.d.voz; toast("✅ Ajustes salvos"); }
  catch (e) { toast("❌ " + errTxt(e), 5000); }
};
$("#ajPasta").onclick = async () => {
  toast("Abrindo a janela do Windows pra escolher a pasta…", 3000);
  const r = await jpost("/api/ajustes/pasta", {});
  if (!r.ok) return toast(r.msg || "Nenhuma pasta escolhida");
  AJU.d = r; $("#ajPastaNome").textContent = r.pasta_saida_nome; toast("✅ Pasta trocada");
};
$("#ajTudo").onclick = async () => { for (const it of ["ollama", "voz", "pasta", "idioma", "pexels", "pixabay", "anthropic"]) await ajTestar(it); jpost("/api/comece", { ajustes_testado: true }).catch(() => { }); };

// ======================================================= ESTILOS QUE ESTÃO BOMBANDO
const BOMB = { d: null, fmt: "longo", idioma: "Todos", fac: "Todas" };
const FAC = { auto: ["⚡ Automático", "fAuto"], medio: ["🟡 Médio", "fMed"], dificil: ["🔴 Difícil", "fDif"] };
// ---- 📊 Estilos em alta → por nicho (selo, o que pede, peças, prévia no mouse, Usar este estilo)
var NZ = { visao: "nicho", fmt: "longo", d: {} };
var PECA_NOME = { titulo: "Título de abertura", etiqueta: "Etiqueta de nome/lugar", numero: "Caixinha de número/data", credito: "Crédito da imagem", selo: "Marca do canal", legenda: "Legenda grande", transicao: "Transição" };
function setVisaoBb(v) { NZ.visao = v; modosOn("#bbVisao", "bv", v); $("#bbNichos").classList.toggle("hidden", v !== "nicho"); $("#bbTodos").classList.toggle("hidden", v !== "todos"); if (v === "nicho") renderNichos(); }
$("#bbVisao").onclick = (e) => { const b = e.target.closest("[data-bv]"); if (b) setVisaoBb(b.dataset.bv); };
async function renderNichos() {
  const box = $("#bbNLista");
  $("#bbNFiltros").innerHTML = `<div class="origbar">${[["longo", "🎬 Vídeos longos"], ["short", "📱 Shorts"]].map(([v, l]) => `<button class="chip ${NZ.fmt === v ? "on" : ""}" data-nzf="${v}">${l}</button>`).join("")}</div>`;
  $("#bbNFiltros").querySelectorAll("[data-nzf]").forEach((b) => (b.onclick = () => { NZ.fmt = b.dataset.nzf; renderNichos(); }));
  if (!NZ.d[NZ.fmt]) { box.innerHTML = '<div class="card">Carregando…</div>'; try { NZ.d[NZ.fmt] = await api("/api/emalta/nichos?formato=" + NZ.fmt); } catch (e) { box.innerHTML = `<div class="card">❌ ${esc(errTxt(e))}</div>`; return; } }
  const d = NZ.d[NZ.fmt], L = d.nichos || [];
  $("#bbMedido").innerHTML = d.atualizado ? esc("Views medidas em " + d.atualizado) + velhoTxt(d.atualizado) : "";
  if (!L.length) { box.innerHTML = `<div class="card">Ainda não tenho números de ${NZ.fmt === "short" ? "shorts" : "vídeos longos"}. Abra <b>🔥 Bombando agora</b> e clique em <b>🔄 Atualizar</b> (uns 5-8 min, roda sozinho).</div>`; return; }
  box.innerHTML = L.map((n, k) => `<div class="nz">
    <div class="nzTh ${NZ.fmt === "short" ? "vert" : ""}" data-nzk="${k}" style="background-image:url('${esc(n.exemplos[0]?.thumb || "")}')" title="Passe o mouse pra ver os vídeos que estão puxando esse nicho"><span class="emRank">${k + 1}º</span><span class="nzEx">${esc(n.exemplos[0]?.titulo || "")}</span></div>
    <div class="nzTx"><div class="nzHead"><b>${esc(n.nicho)}</b><span class="nzSelo ${n.selo}" title="${esc(n.selo_dica)}">${esc(n.selo_nome)}</span></div>
      <div class="mu nzNum" title="Mediana de views por hora dos 10 vídeos mais fortes desse nicho">🔥 ~${Number(n.vph).toLocaleString("pt-BR")} views/hora${n.x_media >= 1.2 ? ` · ${n.x_media}× a média` : ""}</div>
      <div class="nzPede"><span class="mu">O que esse nicho pede:</span><ul>${n.pede.map((t) => `<li>${esc(t)}</li>`).join("")}</ul></div>
      <div class="nzPecas"><span class="mu">Peças na tela:</span> ${n.pecas.map((p) => `<span class="tag">${esc(PECA_NOME[p] || p)}</span>`).join(" ")}</div>
      <div class="ctA"><button class="btn go" data-nzusar="${k}" title="Abre o formulário já com o estilo certo pra esse nicho">✨ Usar este estilo</button>${n.exemplos[0] ? `<button class="btn" data-nzcop="${k}" title="Leva o link do vídeo que mais está bombando pro Copiar estilo">🎨 Copiar o 1º vídeo</button>` : ""}</div></div></div>`).join("");
  box.querySelectorAll("[data-nzk]").forEach((el) => {   // prévia: passa pelos vídeos que puxam o nicho
    const n = L[+el.dataset.nzk]; let i = 0, h = null;
    const mostra = (j) => { const x = n.exemplos[j]; if (!x) return; el.style.backgroundImage = `url('${x.thumb}')`; el.querySelector(".nzEx").textContent = `${x.titulo} · 🔥 ${Number(x.vph).toLocaleString("pt-BR")}/h`; };
    el.onmouseenter = () => { mostra(0); h = setInterval(() => { i = (i + 1) % n.exemplos.length; mostra(i); }, 1100); };
    el.onmouseleave = () => { clearInterval(h); i = 0; mostra(0); };
    el.onclick = () => { const x = n.exemplos[i]; if (x) window.open(x.url, "_blank", "noopener"); };
  });
  box.querySelectorAll("[data-nzusar]").forEach((b) => (b.onclick = () => {
    const n = L[+b.dataset.nzusar];
    if (NZ.fmt === "short") { SH.estilo = "short-documentario"; openShorts(); }
    else if (n.pedido) openPedido(n.estilo, "galeria");
    else { VI.estilo = n.estilo; VI.estilos = []; openVimg(); }
    toast(`✨ Estilo pronto pra ${n.nicho}. Agora é só escrever o tema e clicar em Fazer vídeo.`, 5000);
  }));
  box.querySelectorAll("[data-nzcop]").forEach((b) => (b.onclick = () => { const x = L[+b.dataset.nzcop].exemplos[0]; openCopiar(); ["#crUrl", "#cVideo"].forEach((q) => $(q) && ($(q).value = x.url)); toast("Link colado — clique em ⚡ Analisar e salvar estilo", 4000); }));
}
async function openBombando() {
  if (!showOnly("#bombando")) return;
  setTimeout(() => setVisaoBb(NZ.visao), 0);   // link direto (#bombando) roda antes do NZ existir
  if (!BOMB.d) { $("#bbLista").innerHTML = '<div class="card">Carregando o ranking…</div>'; try { BOMB.d = await api("/api/bombando"); } catch (e) { $("#bbLista").innerHTML = `<div class="card">❌ ${esc(errTxt(e))}</div>`; return; } }
  renderBombando();
}
function renderBombando() {
  const d = BOMB.d, all = d.itens || [];
  $("#bbMedido").innerHTML = d.medido_em ? esc("Última medição: " + d.medido_em) + velhoTxt(d.medido_em) : "";
  const idiomas = ["Todos", ...new Set(all.flatMap((x) => x.idiomas || []))];
  const chips = (arr, cur, key) => arr.map(([v, l]) => `<button class="chip ${cur === v ? "on" : ""}" data-${key}="${esc(v)}">${l}</button>`).join("");
  $("#bbFiltros").innerHTML = `<div class="origbar">${chips([["longo", "🎬 Longos"], ["short", "📱 Shorts"]], BOMB.fmt, "bf")}</div>
    <div class="origbar">${chips(idiomas.map((i) => [i, i === "Todos" ? "🌎 Todos os idiomas" : i]), BOMB.idioma, "bi")}</div>
    <div class="origbar">${chips([["Todas", "Todas"], ["auto", FAC.auto[0]], ["medio", FAC.medio[0]], ["dificil", FAC.dificil[0]]], BOMB.fac, "bfac")}</div>`;
  $("#bbFiltros").querySelectorAll("[data-bf]").forEach((b) => (b.onclick = () => { BOMB.fmt = b.dataset.bf; renderBombando(); }));
  $("#bbFiltros").querySelectorAll("[data-bi]").forEach((b) => (b.onclick = () => { BOMB.idioma = b.dataset.bi; renderBombando(); }));
  $("#bbFiltros").querySelectorAll("[data-bfac]").forEach((b) => (b.onclick = () => { BOMB.fac = b.dataset.bfac; renderBombando(); }));
  const L = all.filter((x) => x.formato === BOMB.fmt && (BOMB.idioma === "Todos" || (x.idiomas || []).includes(BOMB.idioma)) && (BOMB.fac === "Todas" || x.facilidade === BOMB.fac));
  $("#bbLista").innerHTML = L.length ? L.map((x, k) => {
    const f = FAC[x.facilidade] || ["—", ""];
    return `<div class="bb ${k < 3 ? "top top" + (k + 1) : ""}">
      <div class="bbN">${k < 3 ? ["🥇", "🥈", "🥉"][k] : k + 1 + "º"}</div>
      <div class="bbTh ${x.formato === "short" ? "vert" : ""}" style="${x.thumb_url ? `background-image:url('${x.thumb_url}')` : ""}" ${x.pid ? `data-bed="${esc(x.pid)}" title="Abrir o nosso vídeo deste estilo no editor"` : ""}>${x.thumb_url ? "" : '<span class="mu">sem vídeo nosso ainda</span>'}</div>
      <div class="bbTx"><b>🎨 ${esc(x.nome)}</b>
        <div class="bbRef">${x.canal ? `Referência: ${x.canal_url ? `<a href="${esc(x.canal_url)}" target="_blank" rel="noopener">${esc(x.canal)}</a>` : esc(x.canal)}` : "Referência: —"}${x.video_url ? ` · <a href="${esc(x.video_url)}" target="_blank" rel="noopener">vídeo</a>` : ""}</div>
        <div class="bbTags"><span class="bbVph" title="Views por hora da referência (mediana dos vídeos recentes)">${x.vph ? "🔥 " + Number(x.vph).toLocaleString("pt-BR") + " views/hora" : "🔥 —"}</span><span class="fac ${f[1]}">${f[0]}</span>${(x.idiomas || []).map((i) => `<span class="tag">${esc(i)}</span>`).join("")}</div>
        ${x.nota ? `<small class="mu">${esc(x.nota)}</small>` : ""}</div>
      <div class="bbA">${x.tem_ref && x.pid ? `<button class="btn" data-bcmp="${esc(x.pid)}">Comparar com o original</button>` : ""}${x.pid ? `<button class="btn" data-bed="${esc(x.pid)}">✏ Abrir no editor</button>` : ""}<button class="btn go" data-bfaz="${esc(x.estilo_id || "")}" ${x.estilo_id ? "" : "disabled"}>✨ Fazer vídeo neste estilo</button></div></div>`;
  }).join("") : '<div class="card">Nenhum estilo com esses filtros.</div>';
  const box = $("#bbLista");
  box.querySelectorAll("[data-bed]").forEach((b) => (b.onclick = () => openProject(b.dataset.bed)));
  box.querySelectorAll("[data-bcmp]").forEach((b) => (b.onclick = () => openComparar(b.dataset.bcmp, "home")));
  box.querySelectorAll("[data-bfaz]").forEach((b) => (b.onclick = () => openPedido(b.dataset.bfaz, "galeria")));
}
$("#bbAtualizar").onclick = async () => {
  let r; try { r = await jpost("/api/bombando/atualizar", {}); } catch (e) { return toast("❌ " + errTxt(e)); }
  acompanhar(r.job, "📈 Medindo views/hora das referências…", async (res, fechado) => { BOMB.d = null; if (!fechado) closeModal(); toast("✅ Números atualizados", 4000); if (!$("#bombando").classList.contains("hidden")) openBombando(); });
};

// ======================================================= BALÃO "Quer mudar alguma coisa?" + assinatura
const CHAT = { info: null };
function chatAbrir() {
  $("#chatPainel").classList.remove("hidden"); $("#chatBolha").classList.add("aberta");
  $("#chatCtx").textContent = `Tela: ${TELA.atual}${TELA.video ? " · Vídeo: " + TELA.video : ""}`;
  setTimeout(() => $("#chatTexto").focus(), 30);
}
function chatFechar() { $("#chatPainel").classList.add("hidden"); $("#chatBolha").classList.remove("aberta"); $("#chatBolha").classList.add("min"); try { sessionStorage.setItem("chat_min", "1"); } catch (e) { } }
try { if (sessionStorage.getItem("chat_min")) $("#chatBolha").classList.add("min"); } catch (e) { }
$("#chatBolha").onclick = () => ($("#chatPainel").classList.contains("hidden") ? chatAbrir() : chatFechar());
$("#chatFechar").onclick = chatFechar;
$("#chatCopiar").onclick = async () => {
  const t = $("#chatTexto").value.trim(); if (!t) { $("#chatTexto").focus(); return toast("Escreva o que você quer mudar"); }
  if (!CHAT.info) try { CHAT.info = await api("/api/info"); } catch (e) { CHAT.info = { pasta_estudio: "EDITOR VIDEOS" }; }
  const msg = `No Estúdio de Vídeos (pasta ${CHAT.info.pasta_estudio}), tela ${TELA.atual}${TELA.video ? ", vídeo " + TELA.video : ""}: ${t}`;
  toast((await copiarTexto(msg)) ? "✅ Copiado! Agora cole no Claude (Ctrl+V)" : "❌ Não consegui copiar", 4500);
};

// ---- botões novos da barra de cima / início
$("#tnVimg").onclick = () => openVimg();
$("#tnRoteiro").onclick = () => openRoteiro();
$("#tnAjustes").onclick = openAjustes;
$("#tnBomb").onclick = openBombando;
$("#wlVimg").onclick = () => openVimg();
$("#wlRoteiro").onclick = () => openRoteiro();
$("#wlBomb").onclick = openBombando;
document.addEventListener("keydown", (e) => { if (e.key === "Escape" && !$("#chatPainel").classList.contains("hidden")) chatFechar(); });
filaAtualizar();


// ---- primeiro uso: checklist no Início
async function renderCheck() {
  let d; try { d = await api("/api/saude"); } catch (e) { return; }
  const it = (ok, txt, dica, acao) => `<div class="ck ${ok ? "ok" : "no"}"><span class="cki">${ok ? '<svg class="ic"><use href="#i-checkc"/></svg>' : '<svg class="ic"><use href="#i-xc"/></svg>'}</span><div><b>${txt}</b>${ok ? "" : `<small>${dica}</small>`}</div>${!ok && acao ? acao : ""}</div>`;
  const tudo = d.ollama && d.modelo_ok && d.voz && d.whisper && d.ffmpeg;
  $("#wlCheck").innerHTML = `<div class="ckHead"><b>${tudo ? '<svg class="ic"><use href="#i-checkc"/></svg> Tudo pronto pra fazer vídeos' : "Antes de começar"}</b><span class="mu">confere sozinho toda vez que você abre</span></div><div class="ckList">
    ${it(d.ollama && d.modelo_ok, "1. IA do seu PC " + (d.modelo_ok ? "funcionando" : ""), d.ollama ? "A IA escolhida nos Ajustes ainda não foi baixada. Troque em Ajustes." : "Abra o programa da IA (ícone da lhama) e recarregue esta página.", '<button class="btn mini" data-ck="aj"><svg class="ic"><use href="#i-sliders"/></svg> Ajustes</button>')}
    ${it(d.voz && d.whisper && d.ffmpeg, "2. Voz e legenda funcionando", "Falta instalar parte do sistema de voz/legenda. Abra Ajustes e clique em Testar tudo.", '<button class="btn mini" data-ck="aj"><svg class="ic"><use href="#i-sliders"/></svg> Ajustes</button>')}
    ${it(d.videos_feitos > 0, "3. Seu 1º vídeo" + (d.videos_feitos ? ` (já fez ${d.videos_feitos})` : ""), "Comece pelo Vídeo com imagens: escreva só o tema.", '<button class="btn mini go" data-ck="vi"><svg class="ic"><use href="#i-image"/></svg> Fazer meu 1º vídeo</button>')}</div>`;
  $("#wlCheck").querySelectorAll("[data-ck]").forEach((b) => (b.onclick = () => (b.dataset.ck === "aj" ? openAjustes() : openVimg())));
}
const _openInicioOrig = openInicio;
openInicio = async function () { await _openInicioOrig(); renderCheck(); renderComece(); };
document.addEventListener("click", (e) => { if (e.target.closest("[data-inicio], #tnInicio") && comeceComoNovo()) history.replaceState(history.state, "", location.pathname + location.search + "#inicio"); }, true);

// ======================================================= FASE 2 — Fábrica de Shorts, Fábrica de cortes, Vídeo falado, Ideias, Copiar estilo rápido, Extras
Object.assign(TIPO_ICO, { short: "📱", cortes: "✂", falado: "🎙", ideias: "💡", copiar: "🎨", amostra: "🎞" });
Object.assign(TIPO_NOME, { short: "Fábrica de Shorts", cortes: "Fábrica de cortes", falado: "Vídeo falado", ideias: "Ideias", copiar: "Copiar estilo", amostra: "Amostra" });
const fmtNum = (n) => (n == null ? "—" : Number(n) >= 1e6 ? (n / 1e6).toFixed(1).replace(".", ",") + " mi" : Number(n) >= 1e3 ? (n / 1e3).toFixed(n >= 1e4 ? 0 : 1).replace(".", ",") + " mil" : String(Math.round(n)));
const pills = (box, opts, cur, attr) => { $(box).innerHTML = opts.map(([v, l]) => `<button class="btn pill ${String(cur) === String(v) ? "on" : ""}" data-${attr}="${esc(v)}">${l}</button>`).join(""); };
const modosOn = (box, attr, v) => $(box).querySelectorAll(`[data-${attr}]`).forEach((b) => b.classList.toggle("on", b.dataset[attr.replace(/-([a-z])/g, (m, c) => c.toUpperCase())] === v));
function erroCampo(sel, msg) { const el = $(sel); if (el) { el.focus(); el.classList.add("err"); setTimeout(() => el.classList.remove("err"), 2500); } toast(msg, 4500); }

// ---- menus "💡 Ideação ▾" e "🎬 Criar ▾" (um aberto por vez; Esc fecha; clicar fora fecha)
const DROPS = [...document.querySelectorAll("#topnav .tdrop")];
const fecharMenus = (exceto) => DROPS.forEach((d) => { if (d !== exceto) d.querySelector(".tmenu").classList.add("hidden"); });
DROPS.forEach((d) => {
  const btn = d.querySelector(".tdropBtn"), menu = d.querySelector(".tmenu");
  btn.onclick = (e) => { e.stopPropagation(); fecharMenus(d); menu.classList.toggle("hidden"); };
  menu.addEventListener("click", () => menu.classList.add("hidden"));
});
document.addEventListener("click", (e) => { if (!e.target.closest("#topnav .tdrop")) fecharMenus(); });
document.addEventListener("keydown", (e) => { if (e.key !== "Escape") return; const ab = DROPS.find((d) => !d.querySelector(".tmenu").classList.contains("hidden")); if (ab) { fecharMenus(); ab.querySelector(".tdropBtn").focus(); } });
const _marcarAbaOrig = marcarAba;
marcarAba = function (sel) {
  _marcarAbaOrig(sel);
  DROPS.forEach((d) => d.querySelector(".tdropBtn").classList.toggle("on",
    [...d.querySelectorAll("[data-tab]")].some((b) => "#" + b.dataset.tab === sel || (sel === "#conferir" && b.dataset.tab === "vimg"))));
  // dentro do menu, os itens do Ideias (mesma tela, sub-abas) não ficam todos acesos
  document.querySelectorAll("#topnav [data-sub]").forEach((b) => b.classList.toggle("on", sel === "#ideias" && b.dataset.sub === (typeof ID !== "undefined" ? ID.aba : "")));
};
["#shorts", "#cortes", "#falado", "#ideias", "#extras"].forEach((s) => NEW_SECS.push(s));
Object.assign(TELA_NOME, { "#shorts": "Fábrica de Shorts", "#cortes": "Fábrica de cortes", "#falado": "Editor de vídeo falado", "#ideias": "Ideias", "#extras": "Extras", "#copiar": "Copiar estilo de edição" });

// ---- envio de vídeo do PC (mostra % enviado)
function enviarVideo(input, info, onOk) {
  const f = input.files[0]; if (!f) return;
  const fd = new FormData(); fd.append("file", f);
  const x = new XMLHttpRequest();
  x.open("POST", "/api/arquivo");
  x.upload.onprogress = (e) => { if (e.lengthComputable) $(info).textContent = `⏳ enviando… ${Math.round((100 * e.loaded) / e.total)}%`; };
  x.onload = () => {
    let r = {}; try { r = JSON.parse(x.responseText); } catch (e) { }
    if (x.status >= 300) { $(info).textContent = "❌ " + (r.detail || "não consegui enviar"); return; }
    $(info).textContent = `✅ ${f.name} · ${fmtSeg(r.dur)}${r.w ? ` · ${r.w}x${r.h}` : ""}`;
    onOk({ ...r, nome: f.name });
  };
  x.onerror = () => ($(info).textContent = "❌ não consegui enviar");
  $(info).textContent = "⏳ enviando…"; x.send(fd);
}

// ======================================================= 📱 FÁBRICA DE SHORTS
const SH = { modo: "tema", estilo: "short-documentario", dur: 40, estilos: [] };
async function openShorts() {
  if (!showOnly("#shorts")) return;
   marcaPre("#shMarca");
  setModoSh(SH.modo);
  pills("#shDurs", [[30, "30 s"], [40, "40 s"], [60, "1 min"], [90, "90 s"]], SH.dur, "shd");
  carregarVozes().catch(() => { });
  try { SH.estilos = await api("/api/vi/estilos?formato=short"); } catch (e) { $("#shEstilos").innerHTML = `<div class="mu">❌ ${esc(errTxt(e))}</div>`; return; }
  if (!SH.estilos.some((e) => e.id === SH.estilo) && SH.estilos[0]) SH.estilo = SH.estilos[0].id;
  renderShEstilos(); shResumo();
}
function setModoSh(m) { SH.modo = m; modosOn("#shModos", "sm", m); document.querySelectorAll("#shorts [data-sm].row").forEach((r) => r.classList.toggle("hidden", r.dataset.sm !== m)); if (VZ.sh) VZ.sh.nota(); shResumo(); }
function shClasses() {
  const c = $("#shorts"); c.classList.toggle("comAudio", !!SH.audio); c.classList.toggle("modoFora", !SH.audio && SH.vz === "fora");
  $("#shAudioRow").classList.toggle("hidden", !SH.audio);
  if (SH.audio) $("#shAudioInfo").textContent = `🎙 ${SH.audio.nome} · ${fmtSeg(SH.audio.dur)} ✅` + (SH.rotRef ? " · roteiro como referência" : "");
}
VZ.sh = vozEscolha("#shVz", {
  roteiro: () => (SH.modo === "roteiro" ? $("#shRoteiro").value : ""),
  podeEscrever: () => SH.modo === "tema",
  semRoteiro: () => erroCampo("#shRoteiro", "Cole o texto primeiro"),
  tema: () => $("#shTema").value.trim(), titulo: () => $("#shTitulo").value.trim(),
  escrever: async () => {
    const tema = $("#shTema").value.trim(); if (!tema) { erroCampo("#shTema", "Escreva a ideia primeiro"); return ""; }
    const r = await escreverRoteiro({ tema, estilo: SH.estilo, duracao: SH.dur, canal: $("#shCanal").value.trim(), titulo: $("#shTitulo").value.trim() });
    if (!r) return "";
    $("#shRoteiro").value = r.roteiro; if (!$("#shTitulo").value.trim() && r.titulo) $("#shTitulo").value = r.titulo;
    setModoSh("roteiro"); $("#shRoteiro").scrollIntoView({ block: "center", behavior: "smooth" });
    return r.roteiro;
  },
  onModo: (m) => { SH.vz = m; shClasses(); },
  onAudio: (pre) => {   // short fica na Fábrica de Shorts (em pé): só troca a voz do PC pelo áudio enviado
    SH.audio = pre.audio; SH.rotRef = pre.roteiro; shClasses();
    toast("✅ Narração recebida! Clique em 📱 Fazer short: as imagens e a legenda seguem o seu áudio.", 6500);
  },
});
$("#shAudioTirar").onclick = () => { SH.audio = null; SH.rotRef = ""; VZ.sh.set("pc"); shClasses(); };
$("#shModos").onclick = (e) => { const b = e.target.closest("[data-sm]"); if (b) setModoSh(b.dataset.sm); };
$("#shDurs").onclick = (e) => { const b = e.target.closest("[data-shd]"); if (b) { SH.dur = +b.dataset.shd; pills("#shDurs", [[30, "30 s"], [40, "40 s"], [60, "1 min"], [90, "90 s"]], SH.dur, "shd"); shResumo(); } };
function renderShEstilos() {
  $("#shEstilos").innerHTML = SH.estilos.map((e) => `<button class="viEst vert ${SH.estilo === e.id ? "on" : ""}" data-se="${esc(e.id)}">
    <div class="th" style="${e.thumb_url ? `background-image:url('${e.thumb_url}')` : ""}">${e.thumb_url ? "" : '<span class="novoArt">📱<br><small>em pé</small></span>'}</div>
    <div class="tx"><b>🎨 ${esc(e.nome)}</b>${e.novo ? ' <span class="gtag auto">Novo</span>' : ""}${e.aproximado ? ' <span class="gtag">copiado</span>' : ""}${e.extra ? ' <span class="gtag">extra</span>' : ""}${seloPrimeira(e)}<small>${esc(e.descricao)}</small>${bomParaHtml(e)}</div></button>`).join("") || '<div class="mu">Nenhum estilo de short.</div>';
  $("#shEstilos").querySelectorAll("[data-se]").forEach((b) => (b.onclick = () => { SH.estilo = b.dataset.se; estiloNovoConferir(SH.estilos, SH.estilo, "#shConferir"); renderShEstilos(); shResumo(); }));
}
function shResumo() {
  const e = SH.estilos.find((x) => x.id === SH.estilo);
  shCombina();
  $("#shResumo").textContent = e ? `Vai sair: short em pé (1080x1920) no estilo “${e.nome}”, ${SH.modo === "tema" ? "com ~" + SH.dur + " s" : "no tamanho do seu texto"}. ${$("#shConferir").checked ? (e.usado === 0 ? "Estilo novo pra você: antes do short inteiro, você vê 20 s de amostra." : "Antes de montar você confere as imagens (e pode ver 20 s de amostra).") : "Monta direto, sem conferir."} Roda no seu PC, de graça.` : "";
}
$("#shConferir").onchange = shResumo;
$("#shIrCopiar").onclick = (e) => { e.preventDefault(); openCopiar(); };
$("#shFazer").onclick = async () => {
  if (!(await prontoChecar("sh"))) return;
  if (!SH.audio && SH.modo === "tema" && !(await ideiaAuto("#shTema", { formato: "short" }))) return;
  canalAuto("#shCanal");
  const canal = $("#shCanal").value.trim();
  if (!SH.audio && SH.modo === "tema" && !$("#shTema").value.trim()) return erroCampo("#shTema", "Escreva a ideia do short");
  if (!SH.audio && SH.modo === "roteiro" && $("#shRoteiro").value.trim().split(/\s+/).length < 15) return erroCampo("#shRoteiro", "Cole o texto (pelo menos algumas frases)");
  try { localStorage.setItem("pedido_canal", canal); } catch (x) { }
  const body = { modo: SH.audio ? "audio" : SH.modo, audio_id: SH.audio ? SH.audio.id : null, tema: $("#shTema").value.trim(),
    roteiro: SH.audio ? (SH.rotRef || (SH.modo === "roteiro" ? $("#shRoteiro").value.trim() : "")) : $("#shRoteiro").value.trim(), estilo: SH.estilo, duracao: SH.dur, voz: $("#shVoz").value,
    canal, marca: marcaVal("#shMarca"), titulo: $("#shTitulo").value.trim(), conferir: $("#shConferir").checked, numeros: $("#shNumeros").checked, credito: $("#shCredito").checked };
  let r; try { r = await jpost("/api/vi/criar", body); } catch (e) { return toast("❌ " + errTxt(e), 6000); }
  acompanhar(r.job, "📱 Fazendo o seu short…", (res, fechado) => {
    if (res.conferir) { if (fechado) return toast("🖼 Imagens do short prontas! Abra em Meus vídeos → Conferir imagens.", 6000); closeModal(); openConferir(res.pid); toast("✅ Imagens escolhidas. Veja a amostra de 20 s ou clique em ▶ Fazer o vídeo.", 5000); return; }
    viPronto(res, fechado);
  });
};

// ---- Conferir imagens: desfazer + amostra de 20 s + cards em pé nos shorts
const _cardCenaOrig = cardCena;
cardCena = function (c) {
  let h = _cardCenaOrig(c);
  if ((c.antes || []).length) h = h.replace('<button class="btn mini" data-subir="1"', '<button class="btn mini" data-desfazer="1" title="Voltar pra imagem anterior desta cena">↩ Desfazer</button><button class="btn mini" data-subir="1"');
  return h;
};
const _renderConferirOrig = renderConferir;
renderConferir = function () { _renderConferirOrig(); $("#cfGrid").classList.toggle("vert", !!CF.d.vertical); $("#cfAmostra").textContent = CF.d.amostra ? "🎞 Amostra de 20 s (de novo)" : "🎞 Ver amostra de 20 s"; };
$("#cfGrid").addEventListener("click", async (ev) => {
  if (!ev.target.closest("[data-desfazer]")) return;
  ev.stopPropagation();
  const card = ev.target.closest(".cf"), i = +card.dataset.i;
  cfCarregando(i, true);
  try { const r = await jpost(`/api/vi/${CF.pid}/desfazer`, { i }); CF.d.cenas = r.cenas; renderConferir(); toast("↩ Voltou a imagem anterior"); } catch (e) { cfCarregando(i, false); toast("❌ " + errTxt(e), 5000); }
}, true);
function verAmostra(url, titulo) {
  modal(titulo || "🎞 Amostra (20 s)"); $("#mBar").style.width = "100%";
  $("#mMsg").innerHTML = `<video src="${url}" controls autoplay playsinline class="mVid ${CF.d && CF.d.vertical ? "vert" : ""}"></video><p class="mMu">Gostou do jeito? Faça o vídeo inteiro. Não gostou? Troque o estilo (o tema continua preenchido) ou feche e troque só as imagens que não combinam.</p>`;
  mbtn("✅ Gostei, fazer completo", () => { closeModal(); cfRenderizar(); }, "go");
  if (CF.d && CF.d.pedido) mbtn("🎨 Trocar estilo", () => { closeModal(); cfTrocarEstilo(); });
  mbtn("Fechar", closeModal);
}
$("#cfAmostra").onclick = async () => {
  let r; try { r = await jpost(`/api/vi/${CF.pid}/amostra`, { segundos: 20 }); } catch (e) { return toast("❌ " + errTxt(e), 6000); }
  acompanhar(r.job, "🎞 Montando 20 s de amostra…", (res, fechado) => { CF.d.amostra = true; renderConferir(); if (fechado) return toast("🎞 Amostra pronta (em Meus vídeos)", 5000); verAmostra(res.amostra_url); });
};

// ======================================================= ✂ FÁBRICA DE CORTES
const CT = { fonte: "pc", arq: null, n: 3, dur: "30-60", modo: "ia", enq: "desfocado" };
const CT_DUR = [["15-30", "15-30 s"], ["30-60", "30-60 s"], ["60-90", "1-1,5 min"]];
async function openCortes(cid) {
  if (!showOnly("#cortes")) return;
  pills("#ctN", [[1, "1"], [3, "3"], [5, "5"], [8, "8"]], CT.n, "ctn"); pills("#ctDur", CT_DUR, CT.dur, "ctd");
  try { $("#ctCanal").value = $("#ctCanal").value || ""; } catch (e) { }
  try { const l = await api("/api/cortes"); $("#ctAnteriores").innerHTML = '<option value="">📂 Cortes anteriores…</option>' + l.map((x) => `<option value="${esc(x.cid)}">${esc(x.nome)} · ${x.revisar ? "conferir momentos" : x.n + " cortes"} · ${esc(x.quando)}</option>`).join(""); } catch (e) { }
  $("#cortes").classList.toggle("soRes", !!cid);   // aberto por um resultado: mostra só o resultado (botão pra fazer novos)
  if (cid) { mostrarCortes.semRolar = true; await mostrarCortes(cid); mostrarCortes.semRolar = false; }
}
$("#ctAnteriores").onchange = () => { const v = $("#ctAnteriores").value; if (v) mostrarCortes(v); };
$("#ctFonte").onclick = (e) => { const b = e.target.closest("[data-ctf]"); if (!b) return; CT.fonte = b.dataset.ctf; modosOn("#ctFonte", "ctf", CT.fonte); document.querySelectorAll("#cortes .row[data-ctf]").forEach((r) => r.classList.toggle("hidden", r.dataset.ctf !== CT.fonte)); };
$("#ctN").onclick = (e) => { const b = e.target.closest("[data-ctn]"); if (b) { CT.n = +b.dataset.ctn; pills("#ctN", [[1, "1"], [3, "3"], [5, "5"], [8, "8"]], CT.n, "ctn"); } };
$("#ctDur").onclick = (e) => { const b = e.target.closest("[data-ctd]"); if (b) { CT.dur = b.dataset.ctd; pills("#ctDur", CT_DUR, CT.dur, "ctd"); } };
$("#ctModo").onclick = (e) => { const b = e.target.closest("[data-ctm]"); if (b) { CT.modo = b.dataset.ctm; modosOn("#ctModo", "ctm", CT.modo); } };
$("#ctEnq").onclick = (e) => { const b = e.target.closest("[data-cte]"); if (b) { CT.enq = b.dataset.cte; modosOn("#ctEnq", "cte", CT.enq); } };
$("#ctIntro").onchange = () => $("#ctProgRow").classList.toggle("hidden", !$("#ctIntro").checked);
$("#ctArq").onchange = () => { CT.arq = null; enviarVideo($("#ctArq"), "#ctArqInfo", (r) => (CT.arq = r)); };
$("#ctFazer").onclick = async () => {
  const url = $("#ctUrl").value.trim();
  if (CT.fonte === "pc" && !CT.arq) return erroCampo("#ctArq", "Escolha o vídeo (e espere aparecer ✅)");
  if (CT.fonte === "link" && !urlOk(url)) return erroCampo("#ctUrl", "Cole o link do vídeo (começa com https://)");
  const [dmin, dmax] = CT.dur.split("-").map(Number);
  const body = { url: CT.fonte === "link" ? url : "", arquivo_id: CT.fonte === "pc" ? CT.arq.arquivo_id : "", arquivo_nome: CT.arq?.nome || "", de: $("#ctDe").value.trim(), ate: $("#ctAte").value.trim(),
    n: CT.n, dur_min: dmin, dur_max: dmax, modo: CT.modo, enquadramento: CT.enq, intro: $("#ctIntro").checked, canal: $("#ctCanal").value.trim(), programa: $("#ctPrograma").value.trim(),
    silencio: $("#ctSil").checked, zoom: $("#ctZoom").checked, revisar: $("#ctRev").checked };
  let r; try { r = await jpost("/api/cortes/criar", body); } catch (e) { return toast("❌ " + errTxt(e), 6000); }
  CT.arq = null; $("#ctArqInfo").textContent = ""; $("#ctArq").value = "";
  acompanhar(r.job, "✂ Fazendo os cortes…", (res, fechado) => {
    if (res.fase === "revisar") { if (fechado) return toast("✅ Achei os momentos! Abra em ✂ Fábrica de cortes → Cortes anteriores pra conferir.", 7000); closeModal(); return mostrarRevisao(res.cid); }
    if (fechado) return toast(`✅ ${res.n} cortes prontos! Veja em ✂ Fábrica de cortes.`, 6000); closeModal(); mostrarCortes(res.cid);
  });
};
async function mostrarCortes(cid) {
  if ($("#cortes").classList.contains("hidden")) return openCortes(cid);
  $("#ctRes").innerHTML = '<div class="card">Carregando os cortes…</div>';
  let d; try { d = await api("/api/cortes/" + encodeURIComponent(cid)); } catch (e) { $("#ctRes").innerHTML = `<div class="card">❌ ${esc(errTxt(e))}</div>`; return; }
  if (d.fase === "revisar") return mostrarRevisao(cid);
  TELA.video = d.nome;
  const card = (c, intro) => `<div class="ctC">
    <div class="ctV">${c.video_url ? `<video src="${c.leve_url || c.video_url}" ${c.thumb_url ? `poster="${c.thumb_url}"` : ""} controls preload="none" playsinline></video>` : '<div class="cfVazio">sem vídeo</div>'}</div>
    <div class="ctT">${intro ? '<span class="gtag auto">Intro</span>' : `<span class="ctNota ${c.nota >= 7 ? "boa" : c.nota >= 5 ? "media" : "fraca"}" title="Nota do trecho (0-10)">${Number(c.nota).toFixed(1)}</span>`}
      <b>${intro ? "Intro com os melhores momentos" : esc(c.titulo)}</b>
      ${intro ? "" : `<small class="mu">${fmtSeg(c.duracao)} · do minuto ${fmtMS(c.inicio)} ao ${fmtMS(c.fim)}${c.tirou_s >= 1 ? ` · tirei ${Math.round(c.tirou_s)} s de pausa` : ""}${c.zoom ? " · com zoom" : ""}</small><p class="ctMot">💡 ${esc(c.motivo || "")}</p>`}
      <div class="ctA">${c.video_url ? `<a class="btn mini go" href="${c.video_url}" download>⬇ Baixar</a>` : ""}<button class="btn mini" data-cted="${esc(c.pid)}">✏ Abrir no editor</button><button class="btn mini" data-ctpasta="${esc(c.pid)}">📂 Pasta</button></div></div></div>`;
  $("#ctRes").innerHTML = `<div class="card"><div class="ctHead"><b>✂ ${d.cortes.length} ${d.cortes.length === 1 ? "corte" : "cortes"}</b><button class="btn mini novoRes" onclick="document.querySelector('#cortes').classList.remove('soRes')">➕ Fazer novos cortes</button>${d.tem_plano ? `<button class="btn mini" id="ctVoltaRev">↩ Escolher outros momentos</button>` : ""}<span class="mu">${esc(d.nome)} · escolhidos por ${d.modo === "ia" ? "IA do seu PC + regras" : "regras (sem IA)"} · ${d.enquadramento === "centro" ? "tela cheia" : "fundo desfocado"}${d.minutos ? " · tempo de máquina " + d.minutos + " min" : ""} · de graça, no seu PC</span></div>
    <div class="ctGrid">${d.intro ? card(d.intro, true) : ""}${d.cortes.map((c) => card(c)).join("")}</div></div>`;
  if ($("#ctVoltaRev")) $("#ctVoltaRev").onclick = () => mostrarRevisao(cid);
  $("#ctRes").querySelectorAll("[data-cted]").forEach((b) => (b.onclick = () => openProject(b.dataset.cted)));
  $("#ctRes").querySelectorAll("[data-ctpasta]").forEach((b) => (b.onclick = () => api(`/api/open/${b.dataset.ctpasta}?what=folder`, { method: "POST" })));
  if (!mostrarCortes.semRolar) $("#ctRes").scrollIntoView({ block: "start" });
}

// ---- ✂ conferir os momentos antes de montar
const ctFmtT = (t) => { t = Math.max(0, +t || 0); const m = Math.floor(t / 60), sec = t - m * 60; return m + ":" + (sec < 10 ? "0" : "") + sec.toFixed(1); };
const ctParseT = (v) => { const p = String(v).trim().replace(",", ".").split(":").map(Number); if (!p.length || p.some((x) => isNaN(x))) return NaN; return p.reduce((a, x) => a * 60 + x, 0); };
async function mostrarRevisao(cid) {
  if ($("#cortes").classList.contains("hidden")) { mostrarCortes.semRolar = true; await openCortes(cid); mostrarCortes.semRolar = false; return; }
  $("#ctRes").innerHTML = '<div class="card">Carregando os momentos…</div>';
  let d; try { d = await api("/api/cortes/" + encodeURIComponent(cid) + "/plano"); } catch (e) { $("#ctRes").innerHTML = `<div class="card">❌ ${esc(errTxt(e))}</div>`; return; }
  TELA.video = d.nome;
  const baixa = d.origem === "link" && d.fonte && d.fonte.h && d.fonte.h < 1000;
  const linha = (c, i) => `<div class="rvC ${c.marcado ? "" : "off"}" data-i="${i}">
    <label class="rvCk"><input type="checkbox" class="rvOn" ${c.marcado ? "checked" : ""} /></label>
    <div class="rvLinha"><span class="ctNota ${c.nota >= 7 ? "boa" : c.nota >= 5 ? "media" : "fraca"}" title="Nota do trecho (0-10)">${Number(c.nota).toFixed(1)}</span><input type="text" class="rvTit" value="${esc(c.titulo)}" maxlength="70" title="Título que aparece no corte" /></div>
    <div class="mu" style="grid-column:2">💡 ${esc(c.motivo || "")}</div>
    <div style="grid-column:2">${d.fonte_url ? `<video class="rvVid" src="${d.fonte_url}#t=${c.s},${c.e}" controls preload="none" playsinline></video>` : ""}</div>
    <div class="rvLinha" style="grid-column:2">começa em <input type="text" class="rvT rvS" value="${ctFmtT(c.s)}" /> <button class="btn mini" data-rvn="s-1">−1 s</button><button class="btn mini" data-rvn="s+1">+1 s</button>
      termina em <input type="text" class="rvT rvE" value="${ctFmtT(c.e)}" /> <button class="btn mini" data-rvn="e-1">−1 s</button><button class="btn mini" data-rvn="e+1">+1 s</button><span class="rvDur"></span></div>
    <details style="grid-column:2"><summary>ler o que é dito</summary><p>${esc(c.texto)}</p></details></div>`;
  $("#ctRes").innerHTML = `<div class="card"><div class="ctHead"><b>👀 Confira os momentos</b><button class="btn mini novoRes" onclick="document.querySelector('#cortes').classList.remove('soRes')">➕ Fazer novos cortes</button>
    <span class="mu">${esc(d.nome)} · achei ${d.candidatos.length} momentos e já marquei os ${d.n} melhores. Marque/desmarque, mude o título e ajuste começo e fim. Nada foi montado ainda.</span></div>
    ${baixa ? `<div class="avisoLink">⚠ Esse vídeo veio do link em <b>${d.fonte.h}p</b>. Os cortes em pé vão sair com qualidade menor. Para ficar nítido, baixe o vídeo na maior qualidade e refaça por <b>📁 Do meu PC</b>.</div>` : ""}
    <div class="rvTop"><label class="chk"><input type="checkbox" id="rvSil" ${d.silencio ? "checked" : ""} /> 🤐 Tirar silêncios e frases repetidas</label>
      <label class="chk"><input type="checkbox" id="rvZoom" ${d.zoom ? "checked" : ""} /> 🔍 Zoom de ênfase</label>
      <label class="chk"><input type="checkbox" id="rvIntro" ${d.intro ? "checked" : ""} /> 🎬 Intro com os 3 melhores</label></div>
    <div class="rvLista">${d.candidatos.map(linha).join("")}</div>
    <div class="rvAcoes"><button class="btn big go" id="rvFazer">✂ Montar os cortes marcados</button><span class="mu" id="rvResumo"></span></div></div>`;
  const root = $("#ctRes"), cards = [...root.querySelectorAll(".rvC")];
  const ler = (el) => { const i = +el.dataset.i, c = d.candidatos[i]; return { c, on: el.querySelector(".rvOn").checked, s: ctParseT(el.querySelector(".rvS").value), e: ctParseT(el.querySelector(".rvE").value), titulo: el.querySelector(".rvTit").value.trim() }; };
  const atualizar = () => {
    let n = 0;
    cards.forEach((el) => {
      const x = ler(el), dur = x.e - x.s, ok = !isNaN(dur) && dur >= 3 && dur <= 240, sp = el.querySelector(".rvDur");
      el.classList.toggle("off", !x.on); if (x.on) n++;
      sp.textContent = isNaN(dur) ? "tempo inválido" : `${Math.round(dur)} s` + (dur < 3 ? " (curto demais)" : dur > 240 ? " (passa de 4 min)" : "");
      sp.classList.toggle("ruim", !ok);
    });
    $("#rvResumo").textContent = n ? `${n} ${n === 1 ? "corte marcado" : "cortes marcados"}` : "Marque pelo menos 1 momento";
  };
  root.addEventListener("input", (e) => { if (e.target.closest(".rvC")) atualizar(); });
  root.addEventListener("change", (e) => {
    const el = e.target.closest(".rvC"); if (!el) return; atualizar();
    if (e.target.classList.contains("rvS") || e.target.classList.contains("rvE")) { const x = ler(el), v = el.querySelector(".rvVid"); if (v && x.e > x.s) { v.src = `${d.fonte_url}#t=${x.s},${x.e}`; } }
  });
  root.addEventListener("click", (e) => {
    const b = e.target.closest("[data-rvn]"); if (!b) return;
    const el = b.closest(".rvC"), campo = el.querySelector(b.dataset.rvn[0] === "s" ? ".rvS" : ".rvE"), v = ctParseT(campo.value);
    if (isNaN(v)) return; campo.value = ctFmtT(v + (b.dataset.rvn[1] === "+" ? 1 : -1)); campo.dispatchEvent(new Event("change", { bubbles: true }));
  });
  $("#rvFazer").onclick = async () => {
    const marc = cards.map(ler).filter((x) => x.on);
    if (!marc.length) return toast("Marque pelo menos 1 momento.", 4000);
    if (marc.some((x) => isNaN(x.s) || isNaN(x.e) || x.e - x.s < 3 || x.e - x.s > 240)) return toast("Tem um momento com tempo inválido (precisa ter de 3 s a 4 min).", 5000);
    const body = { cortes: marc.map((x) => ({ s: x.s, e: x.e, titulo: x.titulo || x.c.titulo, nota: x.c.nota, nota_regras: x.c.nota_regras, nota_ia: x.c.nota_ia, motivo: x.c.motivo })),
      silencio: $("#rvSil").checked, zoom: $("#rvZoom").checked, intro: $("#rvIntro").checked, programa: $("#ctPrograma").value.trim() };
    let r; try { r = await jpost("/api/cortes/" + encodeURIComponent(cid) + "/renderizar", body); } catch (er) { return toast("❌ " + errTxt(er), 6000); }
    acompanhar(r.job, "✂ Montando os cortes…", (res, fechado) => { if (fechado) return toast(`✅ ${res.n} cortes prontos! Veja em ✂ Fábrica de cortes.`, 6000); closeModal(); mostrarCortes(res.cid); });
  };
  atualizar();
  if (!mostrarCortes.semRolar) root.scrollIntoView({ block: "start" });
}

// ======================================================= 🎙 EDITOR DE VÍDEO FALADO
const FA = { arq: null, saida: "16:9" };
function openFalado(fid) { if (!showOnly("#falado")) return; $("#falado").classList.toggle("soRes", !!fid); if (fid) { mostrarFalado.semRolar = true; mostrarFalado(fid).then(() => (mostrarFalado.semRolar = false)); } }
$("#faArq").onchange = () => { FA.arq = null; enviarVideo($("#faArq"), "#faArqInfo", (r) => (FA.arq = r)); };
$("#faSaida").onclick = (e) => { const b = e.target.closest("[data-fs]"); if (!b) return; FA.saida = b.dataset.fs; $("#faSaida").querySelectorAll("[data-fs]").forEach((x) => x.classList.toggle("on", x === b)); };
$("#faFazer").onclick = async () => {
  if (!FA.arq) return erroCampo("#faArq", "Escolha a gravação (e espere aparecer ✅)");
  const body = { arquivo_id: FA.arq.arquivo_id, arquivo_nome: FA.arq.nome, saida: FA.saida, titulo: $("#faTitulo").value.trim(), silencio: $("#faSil").checked, retakes: $("#faRet").checked,
    legenda: $("#faLeg").checked, broll: $("#faBroll").checked, n_broll: +$("#faNBroll").value };
  let r; try { r = await jpost("/api/falado/criar", body); } catch (e) { return toast("❌ " + errTxt(e), 6000); }
  FA.arq = null; $("#faArqInfo").textContent = ""; $("#faArq").value = "";
  acompanhar(r.job, "🎙 Editando o seu vídeo…", (res, fechado) => { if (fechado) return toast("✅ Vídeo falado pronto! Veja em Meus vídeos.", 6000); closeModal(); mostrarFalado(res.fid); });
};
async function mostrarFalado(fid) {
  let d; try { d = await api("/api/falado/" + encodeURIComponent(fid)); } catch (e) { $("#faRes").innerHTML = `<div class="card">❌ ${esc(errTxt(e))}</div>`; return; }
  TELA.video = d.name;
  const tirou = d.duracao_original && d.duracao ? d.duracao_original - d.duracao : 0;
  $("#faRes").innerHTML = `<div class="card"><div class="ctHead"><button class="btn mini novoRes" onclick="document.querySelector('#falado').classList.remove('soRes')">➕ Editar outro vídeo</button><b>✅ Pronto: ${fmtSeg(d.duracao_original)} → ${fmtSeg(d.duracao)}</b><span class="mu">tirou ${fmtSeg(tirou)} · ${d.trechos} trechos mantidos · ${d.retakes.length} repetição(ões) · ${d.brolls || 0} b-roll${d.minutos ? " · tempo de máquina " + d.minutos + " min" : ""} · de graça, no seu PC</span></div>
    <div class="faGrid">${d.saidas.map((s) => `<div class="faS ${s.formato === "9:16" ? "vert" : ""}"><b>${s.formato === "9:16" ? "📱 Em pé (9:16)" : "🎬 Deitado (16:9)"}</b>
      ${s.video_url ? `<video src="${s.leve_url || s.video_url}" ${s.thumb_url ? `poster="${s.thumb_url}"` : ""} controls preload="metadata" playsinline></video>` : '<div class="cfVazio">sem vídeo</div>'}
      <div class="ctA">${s.video_url ? `<a class="btn mini go" href="${s.video_url}" download>⬇ Baixar</a>` : ""}<button class="btn mini" data-faed="${esc(s.pid)}">✏ Abrir no editor (ajustar cortes)</button><button class="btn mini" data-fapasta="${esc(s.pid)}">📂 Pasta</button></div></div>`).join("")}</div>
    ${d.retakes.length ? `<details class="faRt"><summary>🔁 Frases repetidas que saíram (${d.retakes.length})</summary><ul>${d.retakes.map((t) => `<li>“${esc(t)}”</li>`).join("")}</ul></details>` : ""}</div>`;
  $("#faRes").querySelectorAll("[data-faed]").forEach((b) => (b.onclick = () => openProject(b.dataset.faed)));
  $("#faRes").querySelectorAll("[data-fapasta]").forEach((b) => (b.onclick = () => api(`/api/open/${b.dataset.fapasta}?what=folder`, { method: "POST" })));
  if (!mostrarFalado.semRolar) $("#faRes").scrollIntoView({ block: "start" });
}

// ======================================================= 💡 IDEIAS
const ID = { aba: "cacar" };
async function openIdeias(aba) {
  if (!showOnly("#ideias")) return;
  setAbaId(aba || ID.aba);
  try { const u = await api("/api/ideias/ultimos"); if (u.cacar && !$("#idCacarRes").innerHTML) renderCacar(u.cacar); if (u.saturado && !$("#idSatRes").innerHTML) renderSat(u.saturado); if (u.publico && !$("#idPubRes").innerHTML) renderPub(u.publico); } catch (e) { }
  renderPlacar();
}
function setAbaId(a) { ID.aba = a; $("#idTabs").querySelectorAll("[data-it]").forEach((b) => b.classList.toggle("on", b.dataset.it === a)); document.querySelectorAll("#ideias [data-ip]").forEach((c) => c.classList.toggle("hidden", c.dataset.ip !== a)); }
$("#idTabs").onclick = (e) => { const b = e.target.closest("[data-it]"); if (b) setAbaId(b.dataset.it); };
function rodarIdeia(url, body, titulo, onDone) {
  return jpost(url, body).then((r) => acompanhar(r.job, titulo, async (res, fechado) => { let j = res; if (!j) { try { j = (await api("/api/job/" + r.job)).result; } catch (e) { } } if (!fechado) closeModal(); onDone(j); })).catch((e) => toast("❌ " + errTxt(e), 6000));
}
const ytLink = (u, t) => `<a href="${esc(u)}" target="_blank" rel="noopener">${esc(t)}</a>`;
function renderCacar(d) {
  if (!d) return;
  $("#idCacarRes").innerHTML = `<p class="mu">“${esc(d.kw)}” · ${d.videos.length} vídeos · mediana ${fmtNum(d.mediana_vph)} views/hora · medido em ${esc(d.quando)} (guardado por 1 dia)</p>
    <h4>📺 Canais</h4><div class="tblW"><table class="tbl"><tr><th>Canal</th><th>Inscritos</th><th>Views (mediana)</th><th>Views/hora</th><th title="mediana de views ÷ inscritos">Views/inscrito</th><th title="vídeos com 3x+ a mediana do canal">Fora da curva</th><th>Postou (30 dias)</th></tr>
    ${d.canais.map((c) => `<tr><td>${ytLink(c.canal_url, c.canal || "canal")}</td><td>${fmtNum(c.inscritos)}</td><td>${fmtNum(c.mediana_views)}</td><td>${fmtNum(c.mediana_vph)}</td><td>${c.views_por_inscrito ?? "—"}</td><td>${c.outliers.length ? c.outliers.map((o) => ytLink(o.url, "🔥 " + o.x + "x")).join(" ") : "—"}</td><td>${c.uploads_30d}</td></tr>`).join("") || '<tr><td colspan="7">Não consegui abrir os canais agora.</td></tr>'}</table></div>
    <h4>🎬 Vídeos (mais views por hora primeiro)</h4><div class="tblW"><table class="tbl"><tr><th>Vídeo</th><th>Canal</th><th>Views</th><th>Views/hora</th><th></th></tr>
    ${d.videos.map((v) => `<tr><td>${ytLink(v.url, v.titulo)}${v.short ? ' <span class="tag">short</span>' : ""}</td><td>${esc(v.canal)}</td><td>${fmtNum(v.views)}</td><td>${fmtNum(v.vph)}</td><td>${v.outlier ? '<span class="gtag auto" title="3x+ a mediana da busca">🔥 fora da curva</span>' : ""}${v.x_canal >= 3 ? ` <span class="tag" title="vezes a mediana do canal">${v.x_canal}x o canal</span>` : ""}</td></tr>`).join("")}</table></div>`;
}
$("#idCacar").onclick = () => { const kw = $("#idKw").value.trim(); if (!kw) return erroCampo("#idKw", "Escreva uma palavra-chave"); rodarIdeia("/api/ideias/cacar", { kw, formato: $("#idFmt").value, idioma: ID.idioma }, "🔎 Caçando nicho: " + kw, renderCacar); };
$("#idKw").onkeydown = (e) => { if (e.key === "Enter") $("#idCacar").click(); };
function renderSat(d) {
  if (!d) return;
  const cor = d.nota <= 3.5 ? "boa" : d.nota <= 6.5 ? "media" : "fraca";
  $("#idSatRes").innerHTML = `<div class="satBox"><div class="satNota ${cor}"><b>${Number(d.nota).toFixed(1)}</b><small>de 10</small></div>
    <div><h4>${esc(d.veredito)}</h4><p class="mu">Nicho: “${esc(d.nicho)}” (${esc(d.origem)}) · ${esc(d.quando)}</p><ul>${d.explicacao.map((l) => `<li>${esc(l)}</li>`).join("")}</ul>
    <p class="mu">0 = livre · 10 = lotado. É uma estimativa pelos primeiros resultados da busca, não uma garantia.</p></div></div>`;
}
$("#idSatBtn").onclick = () => { const v = $("#idSat").value.trim(); if (!v) return erroCampo("#idSat", "Cole um link ou escreva o tema"); rodarIdeia("/api/ideias/saturado", { entrada: v, idioma: ID.idioma }, "🌡 Medindo o nicho…", renderSat); };
function renderPub(d) {
  if (!d) return;
  const lst = (t, a) => (a && a.length ? `<h4>${t}</h4><ul>${a.map((x) => `<li>${esc(typeof x === "string" ? x : JSON.stringify(x))}</li>`).join("")}</ul>` : "");
  $("#idPubRes").innerHTML = `<p class="mu">${ytLink(d.url, d.titulo || d.url)} · ${d.lidos} comentários lidos · ${esc(d.quando)}</p><p><b>${esc(Array.isArray(d.resumo) ? d.resumo.join(" ") : d.resumo)}</b></p>
    ${lst("🙋 O que pedem", d.pedidos)}${lst("😠 Do que reclamam", d.reclamacoes)}${lst("❤️ O que mais gostaram", d.elogios)}
    ${(d.ideias_video || []).length ? `<h4>💡 Ideias de vídeo tiradas dos comentários</h4><ul>${d.ideias_video.map((x) => `<li><b>${esc(x.titulo || x)}</b> ${x.porque ? `<small class="mu">— ${esc(x.porque)}</small>` : ""} <button class="btn mini" data-pl="${esc(x.titulo || x)}">➕ Placar</button></li>`).join("")}</ul>` : ""}`;
  $("#idPubRes").querySelectorAll("[data-pl]").forEach((b) => (b.onclick = () => { $("#idPlIdeias").value = ($("#idPlIdeias").value.trim() + "\n" + b.dataset.pl).trim(); setAbaId("placar"); toast("Ideia colada no Placar — clique em 🏆 Dar nota"); }));
}
$("#idPubBtn").onclick = () => { const u = $("#idPubUrl").value.trim(); if (!urlOk(u)) return erroCampo("#idPubUrl", "Cole o link do vídeo (começa com https://)"); rodarIdeia("/api/ideias/publico", { url: u, limite: +$("#idPubLim").value, idioma: ID.idioma }, "💬 Lendo os comentários…", renderPub); };
async function renderPlacar() {
  let d; try { d = await api("/api/ideias/placar"); } catch (e) { return; }
  const L = d.ideias || [];
  const comViews = L.filter((x) => x.views != null && x.nota != null);
  const med = (a) => { if (!a.length) return null; const s = [...a].sort((x, y) => x - y); return s[Math.floor(s.length / 2)]; };
  const alta = med(comViews.filter((x) => x.nota >= 7).map((x) => x.views)), baixa = med(comViews.filter((x) => x.nota < 7).map((x) => x.views));
  const acerto = comViews.length >= 2 ? `<p class="mu">📊 Conferência: ideias nota 7+ fizeram mediana de <b>${fmtNum(alta)}</b> views · abaixo de 7: <b>${fmtNum(baixa)}</b>. ${alta != null && baixa != null ? (alta >= baixa ? "As notas estão acertando ✅" : "As notas não estão acertando — confie mais nos números ⚠") : ""}</p>` : '<p class="mu">Depois de publicar, anote as views reais pra ver se as notas acertam.</p>';
  $("#idPlRes").innerHTML = L.length ? acerto + `<div class="tblW"><table class="tbl"><tr><th>Nota</th><th>Ideia</th><th>Título sugerido</th><th>Por quê</th><th>Situação</th><th>Views reais</th><th></th><th></th></tr>
    ${L.map((x) => `<tr data-pid="${x.id}"><td><span class="ctNota ${x.nota >= 7 ? "boa" : x.nota >= 5 ? "media" : "fraca"}">${x.nota == null ? "—" : Number(x.nota).toFixed(1)}</span></td><td>${esc(x.ideia)}</td><td>${esc(x.titulo)}</td><td><small>${esc(x.porque)}</small></td>
      <td><select data-st>${["ideia", "feita", "publicada", "descartada"].map((s) => `<option ${x.status === s ? "selected" : ""}>${s}</option>`).join("")}</select></td>
      <td><input data-vw class="curto" value="${x.views ?? ""}" placeholder="ex.: 12000" /></td><td><button class="btn mini danger" data-del title="Apagar">🗑</button></td><td><button class="btn mini go" data-faz title="Roteiro e voz no idioma desta ideia">🎬 Fazer vídeo ${ID_FLAG[x.idioma || "pt-BR"] || ""}</button></td></tr>`).join("")}</table></div>` : '<p class="mu">Nenhuma ideia ainda.</p>';
  $("#idPlRes").querySelectorAll("tr[data-pid]").forEach((tr) => {
    const id = tr.dataset.pid;
    tr.querySelector("[data-st]").onchange = (e) => jpost("/api/ideias/placar/" + id, { status: e.target.value }, "PUT").then(renderPlacar);
    tr.querySelector("[data-vw]").onchange = (e) => jpost("/api/ideias/placar/" + id, { views: e.target.value }, "PUT").then(renderPlacar);
    tr.querySelector("[data-del]").onclick = () => api("/api/ideias/placar/" + id, { method: "DELETE" }).then(renderPlacar);
    const x = L.find((i) => String(i.id) === id);
    tr.querySelector("[data-faz]").onclick = () => fazerVideoIdeia(x);
  });
}
$("#idPlBtn").onclick = () => { const t = $("#idPlIdeias").value.trim(); if (!t) return erroCampo("#idPlIdeias", "Escreva pelo menos 1 ideia"); rodarIdeia("/api/ideias/placar", { ideias: t, nicho: $("#idPlNicho").value.trim(), idioma: ID.idioma }, "🏆 Dando nota pras ideias…", () => { $("#idPlIdeias").value = ""; renderPlacar(); }); };

// ======================================================= 🎨 COPIAR ESTILO — modo rápido (aproximado) x fiel (Claude)
const CR = { modo: "rapido", fonte: "link", arq: null };
const _openCopiarOrig = openCopiar;
openCopiar = function () { _openCopiarOrig(); setModoCp(CR.modo); renderMeusEstilos(); };
function setModoCp(m) { CR.modo = m; modosOn("#cpModos", "cm", m); $("#cpRapido").classList.toggle("hidden", m !== "rapido"); $("#cpFiel").classList.toggle("hidden", m !== "fiel"); }
$("#cpModos").onclick = (e) => { const b = e.target.closest("[data-cm]"); if (b) setModoCp(b.dataset.cm); };
$("#crFonte").onclick = (e) => { const b = e.target.closest("[data-cf]"); if (!b) return; CR.fonte = b.dataset.cf; modosOn("#crFonte", "cf", CR.fonte); document.querySelectorAll("#cpRapido .row[data-cf]").forEach((r) => r.classList.toggle("hidden", r.dataset.cf !== CR.fonte)); };
$("#crArq").onchange = () => { CR.arq = null; enviarVideo($("#crArq"), "#crArqInfo", (r) => (CR.arq = r)); };
function cartaoEstilo(e, res) {
  const a = e.analise || {}, p = e.preset || {}, id = esc(e.id || e.estilo_id), pecas = p.elementos || a.pecas || [];
  const curto = (e.formato || p.formato) === "short";
  const usar = curto ? `<button class="btn mini go" data-cruse="short" data-id="${id}" title="Abre a Fábrica de Shorts já com este estilo escolhido">📱 Fazer um short com este estilo</button>` : `<button class="btn mini go" data-cruse="vimg" data-id="${id}" title="Abre o Vídeo com imagens já com este estilo escolhido">🎬 Fazer um vídeo com este estilo</button>`;
  const lado = e.capa_url || e.previa_url ? `<div class="crLado ${curto ? "vert" : ""}">
      ${e.capa_url ? `<figure><div class="crCapa" style="background-image:url('${e.capa_url}')"></div><figcaption>📺 Vídeo de referência</figcaption></figure>` : ""}
      ${e.previa_url ? `<figure><img class="crPrev" src="${e.previa_url}" alt="Prévia do estilo"><figcaption>✨ Assim vai ficar o seu</figcaption></figure>` : ""}</div>` : "";
  const trava = e.extra ? "disabled" : "";
  const chip = (x) => `<button class="crPeca ${x.ligado === false ? "off" : ""}" ${trava} data-crpeca="${esc(x.tipo)}" data-id="${id}" data-lig="${x.ligado === false ? 0 : 1}" title="${esc(x.dica || "")} — clique pra ${x.ligado === false ? "ligar" : "desligar"}">${x.ligado === false ? "○" : "✔"} ${esc(x.nome)}${x.cor_fundo || x.cor_texto ? `<i style="background:${esc(x.cor_fundo || x.cor_texto)}"></i>` : ""}${x.tipo === "transicao" ? ` <small>(${esc(x.dica)})</small>` : ""}</button>`;
  const pecasHtml = pecas.length ? `<div class="crPecas"><span class="mu">Peças que achei <span class="dica" title="Clique numa peça pra ligar ou desligar. A prévia muda na hora.">ⓘ</span></span>${pecas.map(chip).join("")}</div>`
    : (a.cortes_por_min != null ? `<div class="mu">Não achei peças gráficas nesse vídeo — o estilo usa o ritmo, as cores e a legenda.</div>` : "");
  const cor = !e.extra && p.cor_destaque ? `<label class="crCor" title="A cor das caixinhas, etiquetas e destaques da legenda">🎨 Cor de destaque <input type="color" value="${esc(p.cor_destaque)}" data-crcor="${id}"></label>` : "";
  const pos = { baixo: "embaixo", centro: "no meio", topo: "em cima" };
  return `<div class="crE"><div class="crTx">
    <div><b>🎨 ${esc(e.nome)}</b> <span class="tag">${curto ? "📱 em pé" : "🎬 deitado"}</span>${e.extra ? ' <span class="gtag">extra</span>' : ""}</div>
    ${lado}${pecasHtml}
    ${(a.avisos || []).map((t) => `<div class="crAviso">⚠ ${esc(t)}</div>`).join("")}
    <div class="ctA">${usar}${cor}</div>
    <details class="crMais"><summary>⚙ Avançado</summary>
      ${a.cortes_por_min != null ? `<div class="crNums"><span title="Quantas vezes por minuto a imagem troca">✂ ${a.cortes_por_min} trocas de cena por minuto</span><span>⏱ cada cena dura ~${a.plano_medio_s} s</span><span>💬 legenda: ${a.tem_legenda ? (pos[a.legenda_pos] || a.legenda_pos) : "não vi"}</span><span>🎙 ${a.tem_narracao ? "tem narração" : "sem narração"}</span></div>` : ""}
      <div class="crPal"><span class="mu">Cores do vídeo</span>${(a.cores || []).map((c) => `<i style="background:${c.hex}" title="${c.hex} · ${c.pct}%"></i>`).join("")}</div>
      <div class="ctA">${e.extra ? "" : `<button class="btn mini" data-crexp="${id}" title="Cria uma cópia na pasta Extras pra mandar pra outra pessoa">🧩 Mandar pros Extras</button>`}<button class="btn mini danger" data-crdel="${id}">🗑 Apagar estilo</button></div>
    </details></div></div>`;
}
function ligarEstilos(box) {
  box.querySelectorAll("[data-cruse]").forEach((b) => (b.onclick = () => { if (b.dataset.cruse === "short") { SH.estilo = b.dataset.id; openShorts(); } else { VI.estilo = b.dataset.id; VI.estilos = []; openVimg(); } }));
  box.querySelectorAll("[data-crexp]").forEach((b) => (b.onclick = async () => { try { await jpost("/api/extras/exportar", { estilo: b.dataset.crexp }); toast("🧩 Exportado! Está na aba Extras (pasta Extras do Estúdio).", 4500); } catch (e) { toast("❌ " + errTxt(e), 5000); } }));
  box.querySelectorAll("[data-crpeca]").forEach((b) => (b.onclick = async () => { b.disabled = true; try { await jpost(`/api/estilos-meus/${b.dataset.id}/pecas`, { tipo: b.dataset.crpeca, ligado: b.dataset.lig !== "1" }); await atualizarCartoes(); } catch (e) { toast("❌ " + errTxt(e), 5000); b.disabled = false; } }));
  box.querySelectorAll("[data-crcor]").forEach((i) => (i.onchange = async () => { try { await jpost(`/api/estilos-meus/${i.dataset.crcor}/pecas`, { cor_destaque: i.value }); toast("🎨 Cor trocada — veja a prévia"); await atualizarCartoes(); } catch (e) { toast("❌ " + errTxt(e), 5000); } }));
  box.querySelectorAll("[data-crdel]").forEach((b) => (b.onclick = async () => { if (!confirm("Apagar este estilo do seu Estúdio?")) return; try { await api("/api/estilos-meus/" + b.dataset.crdel, { method: "DELETE" }); toast("Apagado"); $("#crRes").innerHTML = ""; renderMeusEstilos(); } catch (e) { toast("❌ " + errTxt(e), 5000); } }));
}
async function atualizarCartoes() {   // depois de ligar/desligar peça: redesenha o resultado e a lista
  const l = await api("/api/estilos-meus").catch(() => []);
  const r = $("#crRes .crE [data-cruse]");
  if (r) { const e = l.find((x) => x.id === r.dataset.id); if (e) { $("#crRes .crE").outerHTML = cartaoEstilo(e); ligarEstilos($("#crRes")); } }
  renderMeusEstilos(l);
}
async function renderMeusEstilos(pronto) {
  let l = pronto || []; if (!pronto) { try { l = await api("/api/estilos-meus"); } catch (e) { } }
  $("#crMeus").innerHTML = `<h4>Meus estilos copiados (${l.length})</h4>` + (l.length ? l.map((e) => cartaoEstilo(e)).join("") : '<p class="mu">Nenhum ainda. Cole um link acima e clique em ⚡ Analisar e salvar estilo.</p>');
  ligarEstilos($("#crMeus"));
}
const nomeDoArquivo = (n) => { const t = String(n || "").replace(/\.[a-z0-9]{2,4}$/i, "").replace(/[_\-.]+/g, " ").replace(/\s+/g, " ").trim().slice(0, 40); return t ? "Estilo " + t : "Meu estilo " + new Date().toLocaleDateString("pt-BR"); };
$("#crFazer").onclick = async () => {
  if (!(await prontoChecar("cr"))) return;
  if (!$("#crNome").value.trim() && CR.fonte === "pc" && CR.arq) $("#crNome").value = nomeDoArquivo(CR.arq.nome);   // QA: nome vazio não trava o novato
  const url = $("#crUrl").value.trim(), nome = $("#crNome").value.trim();
  if (CR.fonte === "link" && !urlOk(url)) return erroCampo("#crUrl", "Cole o link do vídeo (começa com https://)");
  if (CR.fonte === "pc" && !CR.arq) return erroCampo("#crArq", "Escolha o vídeo (e espere aparecer ✅)");
  if (!nome) return erroCampo("#crNome", "Dê um nome pro estilo");
  let r; try { r = await jpost("/api/copiar-rapido", { url: CR.fonte === "link" ? url : "", arquivo_id: CR.fonte === "pc" ? CR.arq.arquivo_id : "", nome }); } catch (e) { return toast("❌ " + errTxt(e), 6000); }
  acompanhar(r.job, "⚡ Medindo a edição da referência…", async (res, fechado) => {
    if (!fechado) closeModal();
    const l = await api("/api/estilos-meus").catch(() => []);
    const e = l.find((x) => x.id === res.estilo_id) || { ...res, id: res.estilo_id };
    $("#crRes").innerHTML = `<div class="card"><h4>✅ Estilo salvo! Confira a prévia e clique em “Fazer um vídeo”.</h4>${cartaoEstilo(e)}<p class="mu">Ficou parecido, não idêntico. Pra copiar animações e fontes do jeitinho, use 🧬 Clonar igualzinho (com Claude), lá em cima.</p></div>`;
    ligarEstilos($("#crRes")); renderMeusEstilos();
  });
};

// ======================================================= 🧩 EXTRAS
async function openExtras() {
  if (!showOnly("#extras")) return;
  $("#exLista").innerHTML = '<div class="card">Carregando…</div>';
  let l = []; try { l = await api("/api/extras"); } catch (e) { $("#exLista").innerHTML = `<div class="card">❌ ${esc(errTxt(e))}</div>`; return; }
  $("#exLista").innerHTML = l.length ? l.map((x) => `<div class="exC ${x.formato === "short" ? "vert" : ""}">
    <div class="exV">${x.preview_url ? `<video src="${x.preview_url}" ${x.capa_url ? `poster="${x.capa_url}"` : ""} class="apV" muted loop playsinline preload="metadata" onmouseenter="this.play()" onmouseleave="if(!AP.ativos.has(this))this.pause()"></video>` : x.capa_url ? `<img src="${x.capa_url}" alt="">` : '<div class="cfVazio">sem prévia</div>'}</div>
    <div class="exT"><b>🎨 ${esc(x.nome)}</b> <span class="tag">${x.formato === "short" ? "📱 em pé" : "🎬 deitado"}</span>${x.instalado ? ' <span class="gtag auto">instalado</span>' : ""}<small>${esc(x.descricao)}</small>${x.autor ? `<small class="mu">por ${esc(x.autor)}</small>` : ""}
    <div class="ctA">${x.instalado ? `<button class="btn mini danger" data-exrem="${esc(x.id)}">Remover</button><button class="btn mini go" data-exusar="${esc(x.id)}" data-fmt="${x.formato}">Usar</button>` : x.conflito ? '<span class="mu">já existe um estilo com esse nome</span>' : `<button class="btn mini go" data-exins="${esc(x.id)}">⬇ Instalar</button>`}</div></div></div>`).join("")
    : '<div class="card">Nenhum extra na pasta ainda.</div>';
  const box = $("#exLista");
  box.querySelectorAll("[data-exins]").forEach((b) => (b.onclick = async () => { try { await jpost(`/api/extras/${b.dataset.exins}/instalar`, {}); toast("✅ Instalado! Já aparece na lista de estilos."); VI.estilos = []; openExtras(); } catch (e) { toast("❌ " + errTxt(e), 5000); } }));
  box.querySelectorAll("[data-exrem]").forEach((b) => (b.onclick = async () => { try { await jpost(`/api/extras/${b.dataset.exrem}/remover`, {}); toast("Removido"); VI.estilos = []; openExtras(); } catch (e) { toast("❌ " + errTxt(e), 5000); } }));
  box.querySelectorAll("[data-exusar]").forEach((b) => (b.onclick = () => { if (b.dataset.fmt === "short") { SH.estilo = b.dataset.exusar; openShorts(); } else { VI.estilo = b.dataset.exusar; VI.estilos = []; openVimg(); } }));
}
$("#exRecarregar").onclick = openExtras;
$("#exAbrir").onclick = () => jpost("/api/extras/abrir", {}).catch((e) => toast("❌ " + errTxt(e)));

// ---- Meus vídeos: botões dos resultados novos
const _renderFilaOrig = renderFila;
renderFila = function () {
  _renderFilaOrig();
  const box = $("#filaBox");
  FILA.list.slice(0, 12).forEach((j, k) => {
    const r = j.resultado || {}; if (!j.done || j.status !== "pronto") return;
    const row = box.querySelectorAll(".job")[k]; if (!row) return;
    const ja = row.querySelector(".ja"); let extra = "";
    if (r.cid) extra += `<button class="btn mini go" data-jct="${esc(r.cid)}">✂ Ver cortes</button>`;
    if (r.fid) extra += `<button class="btn mini go" data-jfa="${esc(r.fid)}">🎙 Ver resultado</button>`;
    if (r.estilo_id) extra += `<button class="btn mini go" data-jcp="1">🎨 Ver estilo</button>`;
    if (r.amostra_url) extra += `<button class="btn mini go" data-jam="${esc(r.amostra_url)}">🎞 Ver amostra</button>`;
    if (j.tipo === "ideias") extra += `<button class="btn mini go" data-jid="1">💡 Ver resultado</button>`;
    if (extra) ja.insertAdjacentHTML("afterbegin", extra);
  });
  const on = (sel, fn) => box.querySelectorAll(sel).forEach((b) => (b.onclick = (e) => { e.stopPropagation(); fn(b); }));
  on("[data-jct]", (b) => openCortes(b.dataset.jct));
  on("[data-jfa]", (b) => openFalado(b.dataset.jfa));
  on("[data-jcp]", () => { CR.modo = "rapido"; openCopiar(); });
  on("[data-jam]", (b) => {   // QA: o botão "Renderizar o vídeo inteiro" da amostra precisa saber qual vídeo é (antes: "id inválido")
    const m = b.dataset.jam.match(/\/api\/vi\/([^/?]+)\/amostra/); if (m && m[1] !== CF.pid) { CF.pid = m[1]; CF.d = null; }
    verAmostra(b.dataset.jam);
  });
  on("[data-jid]", () => openIdeias());
};

// ---- botões novos
$("#tnShorts").onclick = () => openShorts();
$("#tnCortes").onclick = () => openCortes();
$("#tnFalado").onclick = () => openFalado();
$("#tnIdeias").onclick = () => openIdeias("cacar");
$("#tnIdSat").onclick = () => openIdeias("saturado");
$("#tnIdPub").onclick = () => openIdeias("publico");
$("#tnIdPlacar").onclick = () => openIdeias("placar");
$("#tnExtras").onclick = openExtras;
$("#wlShorts").onclick = () => openShorts();
$("#wlCortes").onclick = () => openCortes();
$("#wlFalado").onclick = () => openFalado();
$("#wlIdeias").onclick = () => openIdeias();

// ======================================================= 📡 MEUS FEEDS
const FD = { lista: [], sel: null, fmt: "todos", per: "semana", edit: null, ordem: "vph" };
["#feeds"].forEach((s) => NEW_SECS.push(s));
Object.assign(TELA_NOME, { "#feeds": "Meus Feeds" });
Object.assign(TIPO_NOME, { feed: "Meus Feeds" });
const idadeTxt = (h) => (h == null ? "—" : h < 24 ? "hoje" : h < 48 ? "ontem" : `há ${Math.round(h / 24)} dias`);
async function openFeeds(fid) {
  if (!showOnly("#feeds")) return;
  try { FD.lista = await api("/api/feeds"); } catch (e) { FD.lista = []; }
  if (fid && FD.lista.some((f) => f.id === fid)) FD.sel = fid;
  if (!FD.sel || !FD.lista.some((f) => f.id === FD.sel)) FD.sel = FD.lista[0]?.id || null;
  renderFdChips();
  if (!FD.lista.length) { fdForm(null); $("#fdTopo").innerHTML = ""; $("#fdGrid").innerHTML = `<div class="card">Você ainda não tem feed. Crie o primeiro: dê um nome (ex.: <b>Curiosidades</b>), escreva 2 ou 3 palavras-chave e clique em <b>💾 Salvar e puxar os vídeos</b>.</div>`; return; }
  $("#fdForm").classList.add("hidden");
  carregarFeed(FD.sel);
}
function renderFdChips() {
  $("#fdChips").innerHTML = FD.lista.map((f) => `<button class="chip ${f.id === FD.sel ? "on" : ""}" data-fd="${esc(f.id)}">📡 ${esc(f.nome)} ${f.n ? `<span class="n">${f.n}</span>` : ""}${f.fora ? ` <span class="n fogo">🔥 ${f.fora}</span>` : ""}</button>`).join("");
  $("#fdChips").querySelectorAll("[data-fd]").forEach((b) => (b.onclick = () => { FD.sel = b.dataset.fd; renderFdChips(); $("#fdForm").classList.add("hidden"); carregarFeed(FD.sel); }));
}
function fdForm(f) {
  FD.edit = f;
  $("#fdForm").classList.remove("hidden");
  $("#fdFormTit").textContent = f ? `Editar “${f.nome}”` : "Novo feed";
  $("#fdNome").value = f?.nome || ""; $("#fdPal").value = (f?.palavras || []).join(", "); $("#fdCanais").value = (f?.canais || []).join("\n");
  FD.fmt = f?.formato || "todos"; FD.per = f?.periodo || "semana";
  pills("#fdFmt", [["todos", "🗂 Tudo"], ["longos", "🎬 Só vídeos longos"], ["shorts", "📱 Só shorts"]], FD.fmt, "ffmt");
  pills("#fdPer", [["hoje", "Hoje"], ["semana", "Última semana"], ["mes", "Último mês"]], FD.per, "fper");
  setTimeout(() => $("#fdNome").focus(), 30);
}
$("#fdFmt").onclick = (e) => { const b = e.target.closest("[data-ffmt]"); if (b) { FD.fmt = b.dataset.ffmt; modosOn("#fdFmt", "ffmt", FD.fmt); } };
$("#fdPer").onclick = (e) => { const b = e.target.closest("[data-fper]"); if (b) { FD.per = b.dataset.fper; modosOn("#fdPer", "fper", FD.per); } };
$("#fdNovo").onclick = () => fdForm(null);
$("#fdCancelar").onclick = () => { $("#fdForm").classList.add("hidden"); if (!FD.lista.length) openInicio(); };
$("#fdSalvar").onclick = async () => {
  const nome = $("#fdNome").value.trim(), palavras = $("#fdPal").value.trim(), canais = $("#fdCanais").value.trim();
  if (!nome) return erroCampo("#fdNome", "Dê um nome pro feed (ex.: Curiosidades)");
  if (!palavras && !canais) return erroCampo("#fdPal", "Escreva pelo menos uma palavra-chave ou um canal");
  let r; try { r = await jpost("/api/feeds", { id: FD.edit?.id, nome, palavras, canais, formato: FD.fmt, periodo: FD.per }); } catch (e) { return toast("❌ " + errTxt(e), 5000); }
  FD.sel = r.feed.id; $("#fdForm").classList.add("hidden");
  FD.lista = await api("/api/feeds"); renderFdChips();
  atualizarFeed(FD.sel);
};
async function carregarFeed(fid) {
  let d; try { d = await api("/api/feeds/" + encodeURIComponent(fid)); } catch (e) { $("#fdGrid").innerHTML = `<div class="card">❌ ${esc(errTxt(e))}</div>`; return; }
  renderFeed(d);
  if (!d.res && !d.job) atualizarFeed(fid);
}
function renderFeed(d) {
  const f = d.feed, r = d.res;
  const fonte = [f.palavras.length ? "🔎 " + f.palavras.map(esc).join(", ") : "", f.canais.length ? `📺 ${f.canais.length} canal(is) de referência` : ""].filter(Boolean).join(" · ");
  const per = { hoje: "de hoje", semana: "da última semana", mes: "do último mês" }[f.periodo] || "";
  $("#fdTopo").innerHTML = `<div class="fdInfo"><div><b>📡 ${esc(f.nome)}</b> <span class="mu">— vídeos ${per}${f.formato !== "todos" ? (f.formato === "shorts" ? ", só shorts" : ", só longos") : ""}</span><br><small class="mu">${fonte}</small><br>
    <small class="mu">${r ? `Atualizado em ${esc(r.quando)} · ${r.total} vídeos · mediana ${fmtNum(r.mediana_vph)} views/hora${velhoTxt(r.quando)}` : "Ainda não puxado."}${d.job ? " · ⏳ atualizando agora…" : ""}</small>
    ${r && r.erros && r.erros.length ? `<br><small class="warnTok">⚠ ${r.erros.length} busca(s) falharam (o YouTube pode ter limitado). O resto apareceu normal.</small>` : ""}</div>
    <div class="cfAcoes"><select id="fdOrdem" class="curto" title="Ordem dos vídeos"><option value="vph">Mais views/hora</option><option value="fora">🔥 Fora da curva primeiro</option><option value="novo">Mais novos</option><option value="views">Mais views</option></select>
    <button class="btn go" id="fdAtu" ${d.job ? "disabled" : ""}>🔄 Atualizar</button><button class="btn" id="fdEdit">✏ Editar</button><button class="btn" id="fdDel" title="Apagar este feed (não apaga vídeo nenhum)">🗑</button></div></div>`;
  $("#fdOrdem").value = FD.ordem;
  $("#fdOrdem").onchange = (e) => { FD.ordem = e.target.value; renderFeed(d); };
  $("#fdAtu").onclick = () => atualizarFeed(f.id);
  $("#fdEdit").onclick = () => fdForm(f);
  $("#fdDel").onclick = async () => { if (!confirm(`Apagar o feed “${f.nome}”?`)) return; await api("/api/feeds/" + f.id, { method: "DELETE" }); FD.sel = null; openFeeds(); };
  if (!r) { $("#fdGrid").innerHTML = `<div class="card">⏳ Puxando os vídeos… isso leva de 30 s a 2 min (vamos devagar pro YouTube não bloquear).</div>`; return; }
  if (!r.videos.length) { $("#fdGrid").innerHTML = `<div class="card">Nenhum vídeo novo encontrado nesse período. Tente “Último mês” ou outras palavras (✏ Editar).</div>`; return; }
  const ord = { vph: (a, b) => (b.vph || 0) - (a.vph || 0), fora: (a, b) => (b.fora_da_curva - a.fora_da_curva) || ((b.x_canal || 0) - (a.x_canal || 0)), novo: (a, b) => (a.idade_h ?? 1e9) - (b.idade_h ?? 1e9), views: (a, b) => (b.views || 0) - (a.views || 0) }[FD.ordem];
  const vs = [...r.videos].sort(ord);
  $("#fdGrid").innerHTML = vs.map((v, k) => `<div class="fdCard">
      <a class="fdTh ${v.short ? "vert" : ""}" href="${esc(v.url)}" target="_blank" rel="noopener" ${k < 8 ? `style="background-image:url('${esc(v.thumb)}')"` : `data-bg="${esc(v.thumb)}"`}>${v.fora_da_curva ? `<span class="fdFogo" title="${v.x_canal}x a média de views/hora do canal">🔥 fora da curva · ${String(v.x_canal).replace(".", ",")}x</span>` : ""}${v.short ? '<span class="fdTag">short</span>' : ""}${v.duracao ? `<span class="fdDur">${fmtSeg(v.duracao)}</span>` : ""}</a>
      <div class="fdTx"><div class="fdTit" title="${esc(v.titulo)}">${esc(v.titulo)}</div>
        <div class="fdCanal">${v.canal_url ? ytLink(v.canal_url, v.canal || "canal") : esc(v.canal)}</div>
        <div class="fdNums"><span title="views">👁 ${fmtNum(v.views)}</span><span title="idade">🕒 ${idadeTxt(v.idade_h)}</span><span class="vph" title="views por hora desde que saiu">⚡ ${fmtNum(v.vph)}/h</span></div>
        <div class="fdBtns"><a class="btn mini" href="${esc(v.url)}" target="_blank" rel="noopener">▶ Ver</a><button class="btn mini" data-fdrot="${esc(v.url)}">✍️ Roteiro pronto com este vídeo</button><button class="btn mini" data-fdcop="${esc(v.url)}">🎨 Copiar estilo</button></div>
      </div></div>`).join("");
  lazyBg($("#fdGrid"));
  $("#fdGrid").querySelectorAll("[data-fdrot]").forEach((b) => (b.onclick = () => { openRoteiro(); setAcaoRt("escrever"); $("#rtUrl").value = b.dataset.fdrot; toast("Link colado no Roteiro pronto — escreva o tema do SEU vídeo", 4000); setTimeout(() => $("#rtTema").focus(), 80); }));
  $("#fdGrid").querySelectorAll("[data-fdcop]").forEach((b) => (b.onclick = () => { openCopiar(); ["#crUrl", "#cVideo"].forEach((k) => $(k) && ($(k).value = b.dataset.fdcop)); toast("Link colado no Copiar estilo", 3500); }));
}
function atualizarFeed(fid) {
  jpost(`/api/feeds/${encodeURIComponent(fid)}/atualizar`, {}).then((r) => {
    carregarFeed(fid);
    acompanhar(r.job, "📡 Puxando os vídeos novos do feed…", async (res, fechado) => { if (!fechado) closeModal(); FD.lista = await api("/api/feeds"); renderFdChips(); if (FD.sel === fid && !$("#feeds").classList.contains("hidden")) carregarFeed(fid); toast(`✅ Feed atualizado: ${res?.n ?? 0} vídeos`); });
  }).catch((e) => toast("❌ " + errTxt(e), 5000));
}
$("#tnFeeds").onclick = () => openFeeds();

// ======================================================= 🎙 MINHAS VOZES
const VZT = { d: null, arq: null, q: "" };
NEW_SECS.push("#vozes");
Object.assign(TELA_NOME, { "#vozes": "Minhas vozes" });
Object.assign(TIPO_NOME, { voz: "Minhas vozes" });
const vzPlayer = new Audio();
function vzTocar(url, btn) {
  document.querySelectorAll(".vzCard.tocando").forEach((c) => c.classList.remove("tocando"));
  vzPlayer.pause(); vzPlayer.src = url; vzPlayer.play().catch(() => toast("Não consegui tocar o áudio"));
  const c = btn && btn.closest(".vzCard"); if (c) { c.classList.add("tocando"); vzPlayer.onended = () => c.classList.remove("tocando"); }
}
async function openVozes() {
  if (!showOnly("#vozes")) return;
  await carregarVozesTela();
}
async function carregarVozesTela() {
  try { VZT.d = await api("/api/vozes"); } catch (e) { $("#vzClones").innerHTML = `<div class="card">❌ ${esc(errTxt(e))}</div>`; return; }
  renderVozesTela();
}
function cardVoz(v, tipo) {
  const pad = VZT.d.padrao === v.voz;
  const sub = tipo === "clone" ? `${v.origem === "VoiceStudio" ? "veio do VoiceStudio" : "clonada por você"} · referência de ${String(v.ref_seg || "?").replace(".", ",")} s`
    : tipo === "vs" ? [v.genero, v.idioma].filter(Boolean).join(" · ") : v.grupo;
  const ouvir = tipo === "vs" ? `<button class="btn mini" data-vzurl="${esc(v.ref_url)}">▶ Ouvir</button>`
    : `<button class="btn mini" data-vzouvir="${esc(v.voz)}" ${tipo === "clone" && v.teste_url ? `data-url="${esc(v.teste_url)}"` : v.amostra_url ? `data-url="${esc(v.amostra_url)}"` : ""}>▶ Ouvir</button>`;
  const acoes = tipo === "vs" ? (v.importada ? `<span class="tag ok">✅ já está no Estúdio</span>` : `<button class="btn mini ok" data-vzimp="${esc(v.id)}">➕ Usar no Estúdio</button>`)
    : `${pad ? `<span class="tag ok">⭐ voz padrão</span>` : `<button class="btn mini" data-vzpad="${esc(v.voz)}">⭐ Usar como padrão</button>`}${tipo === "clone" ? `<button class="btn mini" data-vzref="${esc(v.ref_url)}" title="Ouvir o trecho de referência">🎧 Referência</button><button class="btn mini" data-vzdel="${esc(v.id)}" title="Apagar esta voz">🗑</button>` : ""}`;
  return `<div class="vzCard ${pad ? "pad" : ""}"><div class="vzIc">${tipo === "clone" ? "🎙" : tipo === "vs" ? "📚" : /^qwen3/.test(v.voz) ? "🧠" : "🔊"}</div>
    <div class="vzTx"><b title="${esc(v.nome)}">${esc(v.nome)}</b><small>${esc(sub || "")}</small></div><div class="vzBt">${ouvir}${acoes}</div></div>`;
}
function renderVozesTela() {
  const d = VZT.d;
  $("#vzAviso").innerHTML = d.clone_ok ? `<div class="card vzOk">✅ Clonar voz funciona neste PC: <b>${esc(d.clone_motivo)}</b>. Cada frase leva uns segundos na placa de vídeo (a 1ª vez carrega o modelo, ~1 min).${d.chatterbox ? "" : ' <span class="mu">Chatterbox (porta 8020) está desligado — não precisa dele.</span>'}</div>`
    : `<div class="card vzErr">⚠ <b>Clonar voz ainda não funciona neste PC.</b> ${esc(d.clone_motivo)} As vozes prontas abaixo continuam funcionando normalmente.</div>`;
  $("#vzNovo").disabled = !d.clone_ok;
  d.prontas.forEach((v) => (v.voz = v.id));
  $("#vzClN").textContent = d.clones.length;
  $("#vzClones").innerHTML = d.clones.length ? d.clones.map((v) => cardVoz(v, "clone")).join("") : `<div class="card mu">Nenhuma voz clonada ainda. Clique em <b>➕ Clonar minha voz</b> ou traga uma do VoiceStudio (abaixo).</div>`;
  $("#vzPrN").textContent = d.prontas.length;
  $("#vzProntas").innerHTML = d.prontas.map((v) => cardVoz(v, "pronta")).join("");
  $("#vzVsN").textContent = d.voicestudio.length ? `(${d.voicestudio.length})` : "(app não encontrado)";
  renderVsLista();
}
function renderVsLista() {
  const q = normTxt(VZT.q || "");
  const L = VZT.d.voicestudio.filter((v) => !q || normTxt(v.nome).includes(q));
  $("#vzVs").innerHTML = L.map((v) => cardVoz(v, "vs")).join("") || '<p class="mu">Nenhuma voz.</p>';
}
$("#vzVsBusca").oninput = (e) => { VZT.q = e.target.value; renderVsLista(); };
$("#vozes").addEventListener("click", async (ev) => {
  const b = ev.target.closest("button"); if (!b || b.disabled) return;
  if (b.dataset.vzurl || b.dataset.vzref) return vzTocar(b.dataset.vzurl || b.dataset.vzref, b);
  if (b.dataset.vzouvir) {
    const frase = $("#vzFrase").value.trim();
    if (b.dataset.url && !frase) return vzTocar(b.dataset.url, b);
    const old = b.textContent; b.disabled = true; b.textContent = "⏳ gerando…";
    try {
      const r = await jpost("/api/vozes/amostra", { voz: b.dataset.vzouvir, texto: frase });
      if (r.url) { b.dataset.url = frase ? "" : r.url; vzTocar(r.url, b); }
      else acompanhar(r.job, "🎙 Gerando a amostra da voz…", (res, fechado) => { if (!fechado) closeModal(); if (res?.amostra_url) { if (!frase) b.dataset.url = res.amostra_url; vzTocar(res.amostra_url, b); } });
    } catch (e) { toast("❌ " + errTxt(e), 5000); }
    b.disabled = false; b.textContent = old; return;
  }
  if (b.dataset.vzpad) { await jpost("/api/vozes/padrao", { voz: b.dataset.vzpad }); AJU.d = null; VOZES.lista = null; toast("⭐ Voz padrão trocada"); return carregarVozesTela(); }
  if (b.dataset.vzimp) { try { const r = await jpost("/api/vozes/importar", { id: b.dataset.vzimp }); VOZES.lista = null; toast(`✅ “${r.nome}” agora está nas suas vozes`); } catch (e) { toast("❌ " + errTxt(e), 5000); } return carregarVozesTela(); }
  if (b.dataset.vzdel) { if (!confirm("Apagar esta voz clonada? (o áudio original não é apagado)")) return; await api("/api/vozes/" + encodeURIComponent(b.dataset.vzdel), { method: "DELETE" }); VOZES.lista = null; return carregarVozesTela(); }
});
$("#vzNovo").onclick = () => { $("#vzForm").classList.remove("hidden"); setTimeout(() => $("#vzNome").focus(), 30); };
$("#vzCancelar").onclick = () => $("#vzForm").classList.add("hidden");
function vzEnviar(f) {
  if (!f) return;
  VZT.arq = null; $("#vzArqInfo").textContent = "⏳ enviando…";
  const fd = new FormData(); fd.append("file", f);
  const x = new XMLHttpRequest(); x.open("POST", "/api/vozes/subir");
  x.upload.onprogress = (e) => { if (e.lengthComputable) $("#vzArqInfo").textContent = `⏳ enviando ${Math.round(e.loaded * 100 / e.total)}%`; };
  x.onload = () => { let r = {}; try { r = JSON.parse(x.responseText); } catch (e) { }
    if (x.status !== 200) { $("#vzArqInfo").textContent = "❌ " + (r.detail || "não consegui enviar"); return; }
    VZT.arq = r.arquivo_id; $("#vzArqInfo").textContent = `✅ ${r.nome} (${fmtSeg(r.dur)})${r.dur > 30 ? " — vou usar só ~25 s, cortando numa pausa" : r.dur < 10 ? " — curto demais, o ideal é 10–30 s" : ""}`; };
  x.onerror = () => ($("#vzArqInfo").textContent = "❌ não consegui enviar");
  x.send(fd);
}
$("#vzArq").onchange = (e) => vzEnviar(e.target.files[0]);
$("#vzDrop").ondragover = (e) => { e.preventDefault(); $("#vzDrop").classList.add("drag"); };
$("#vzDrop").ondragleave = () => $("#vzDrop").classList.remove("drag");
$("#vzDrop").ondrop = (e) => { e.preventDefault(); $("#vzDrop").classList.remove("drag"); vzEnviar(e.dataTransfer.files[0]); };
$("#vzClonar").onclick = async () => {
  const nome = $("#vzNome").value.trim();
  if (!nome) return erroCampo("#vzNome", "Dê um nome pra voz (ex.: Minha voz)");
  if (!VZT.arq) return toast("Envie o áudio primeiro (espere aparecer ✅)", 4000);
  if (!$("#vzOk").checked) return toast("Marque que a voz é sua (ou de quem te autorizou)", 4000);
  let r; try { r = await jpost("/api/vozes/clonar", { nome, arquivo_id: VZT.arq, consentimento: true }); } catch (e) { return toast("❌ " + errTxt(e), 6000); }
  acompanhar(r.job, "🎙 Criando a sua voz…", async (res, fechado) => {
    if (!fechado) closeModal(); $("#vzForm").classList.add("hidden"); VOZES.lista = null;
    await carregarVozesTela(); toast(`✅ Voz “${res?.name || nome}” pronta! Clique em ▶ Ouvir.`, 5000);
  });
};
$("#tnVozes").onclick = () => openVozes();

// ======================================================= 🖍 STICKMAN STUDIO
const SK = { modo: "tema", fmt: "16:9", dur: 40 };
NEW_SECS.push("#stickman");
Object.assign(TELA_NOME, { "#stickman": "Stickman Studio" });
Object.assign(TIPO_NOME, { stickman: "Stickman Studio" });
// mini-bonecos (só pra mostrar as poses na tela; o vídeo usa templates/scenes/stickman.html)
function skMini(nome, aL, aR, lL, lR, boca) {
  const R = Math.PI / 180, V = (a, l) => [Math.sin(a * R) * l, Math.cos(a * R) * l];
  const seg = (o, a0, a1) => { const e = [o[0] + V(a0, 15)[0], o[1] + V(a0, 15)[1]], m = [e[0] + V(a1, 13)[0], e[1] + V(a1, 13)[1]]; return `M${o[0]} ${o[1]}L${e[0]} ${e[1]}L${m[0]} ${m[1]}`; };
  const d = [seg([30, 30], aL[0], aL[1]), seg([30, 30], aR[0], aR[1]), seg([30, 54], lL[0], lL[1]), seg([30, 54], lR[0], lR[1]), "M30 26L30 54"].join("");
  return `<div class="skPose"><svg viewBox="0 0 60 92"><g fill="none" stroke="currentColor" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"><path d="${d}"/><circle cx="30" cy="18" r="8"/><path d="${boca}" stroke-width="2"/></g></svg><span>${nome}</span></div>`;
}
function skPoses() {
  $("#skPoses").innerHTML = [
    skMini("parado", [-14, -8], [14, 8], [-9, -4], [9, 4], "M26 20Q30 23 34 20"), skMini("andando", [25, 15], [-25, -15], [24, 6], [-24, -6], "M26 20Q30 23 34 20"),
    skMini("apontando", [-14, -6], [96, 93], [-9, -4], [11, 4], "M27 20Q30 22 33 20"), skMini("pensando", [-35, 48], [30, -164], [-7, -3], [7, 3], "M27 21L33 20"),
    skMini("surpreso", [-140, -160], [140, 160], [-15, -8], [15, 8], "M28 21a2 2.4 0 1 0 4 0a2 2.4 0 1 0 -4 0"), skMini("comemorando", [-155, -172], [155, 172], [-14, -2], [14, 2], "M25 20Q30 25 35 20"),
  ].join("");
}
async function openStickman() {
  if (!showOnly("#stickman")) return;
  skPoses();
  pills("#skFmt", [["16:9", "🎬 Deitado 16:9 (YouTube)"], ["9:16", "📱 Em pé 9:16 (Shorts/Reels)"]], SK.fmt, "skf");
  renderDurs("#skDurs", SK.dur, (d) => (SK.dur = d), null, [[30, "30 s"], [40, "40 s"], [60, "1 min"], [90, "1:30"], [120, "2 min"], [150, "2:30"], [180, "3 min"], [300, "5 min"]]);
   marcaPre("#skMarca");
  carregarVozes().catch(() => { });
  skLista();
}
async function skLista() {
  let l = HOME.list && HOME.list.length ? HOME.list : null;
  try { l = await api("/api/projects"); HOME.list = l; } catch (e) { l = l || []; }
  const ps = l.filter((p) => /stickman/i.test(p.estilo || "") || /-stickman-/i.test(p.folder || "")).sort((a, b) => b.mtime - a.mtime);
  $("#skN").textContent = ps.length || "";
  $("#skLista").innerHTML = ps.length ? ps.map((p) => `<div class="proj" data-skp="${p.id}"><div class="th" ${p.thumb ? `data-bg="/api/thumb/${p.id}?${p.mtime}"` : ""}>${p.thumb ? "" : "🖍"}</div>
      <div class="badge ${p.rendered ? "ok" : "no"}">${p.rendered ? "✅ VÍDEO PRONTO" : "⏳ ainda sem vídeo"}</div>
      <div class="nm">${esc(String(p.name).replace(/^\d+\s*-\s*[^-]+-\s*/, ""))}</div><div class="meta">${p.w}×${p.h} · ${fmt(p.dur)}</div>
      <div class="acts"><button class="btn ok" data-skopen="${p.id}">✏ Abrir no editor</button>${p.rendered ? `<button class="btn" data-skplay="${p.id}">▶ Ver</button>` : ""}<button class="btn" data-skfold="${p.id}">📂 Pasta</button></div></div>`).join("")
    : '<div class="card mu">Seus vídeos de stickman vão aparecer aqui.</div>';
  lazyBg($("#skLista"));
}
$("#skLista").onclick = (e) => {
  const b = e.target.closest("button"); if (!b) return;
  if (b.dataset.skopen) openProject(b.dataset.skopen);
  if (b.dataset.skplay) api(`/api/open/${b.dataset.skplay}?what=final`, { method: "POST" });
  if (b.dataset.skfold) api(`/api/open/${b.dataset.skfold}?what=folder`, { method: "POST" });
};
$("#skFmt").onclick = (e) => { const b = e.target.closest("[data-skf]"); if (b) { SK.fmt = b.dataset.skf; modosOn("#skFmt", "skf", SK.fmt); } };
$("#skModo").onclick = (e) => {
  const b = e.target.closest("[data-skm]"); if (!b) return;
  SK.modo = b.dataset.skm; modosOn("#skModo", "skm", SK.modo);
  document.querySelectorAll("#stickman [data-skr]").forEach((r) => r.classList.toggle("hidden", r.dataset.skr !== SK.modo));
};
$("#skVozes").onclick = () => openVozes();
$("#skFazer").onclick = async () => {
  if (SK.modo === "tema" && !(await ideiaAuto("#skTema", { formato: SK.fmt === "9:16" ? "short" : "longo" }))) return;
  canalAuto("#skCanal");
  const canal = $("#skCanal").value.trim(), tema = $("#skTema").value.trim(), roteiro = $("#skRoteiro").value.trim();
  if (SK.modo === "tema" && !tema) return erroCampo("#skTema", "Escreva o tema do vídeo");
  if (SK.modo === "roteiro" && roteiro.split(/\s+/).length < 15) return erroCampo("#skRoteiro", "Cole o roteiro (pelo menos algumas frases)");
  if (SK.fmt === "9:16" && SK.modo === "tema" && SK.dur > 90) return toast("Em pé (9:16) é pra vídeo curto: escolha até 1 min", 4000);
  try { localStorage.setItem("pedido_canal", canal); } catch (e) { }
  let r; try { r = await jpost("/api/vi/criar", { modo: SK.modo, tema, roteiro, estilo: "stickman", formato: SK.fmt, duracao: SK.dur, voz: $("#skVoz").value, canal, marca: marcaVal("#skMarca"), conferir: false }); }
  catch (e) { return toast("❌ " + errTxt(e), 6000); }
  acompanhar(r.job, "🖍 Fazendo o vídeo de stickman…", (res, fechado) => {
    skLista();
    if (fechado) return toast("✅ Vídeo de stickman pronto! Veja em Meus vídeos.", 5000);
    $("#mTitle").textContent = "✅ Vídeo pronto!"; $("#mMsg").textContent = "Cada frase virou uma cena. No editor dá pra trocar pose, balão, cenário e texto de cada uma.";
    mbtn("✏ Abrir no editor", () => { closeModal(); openProject(res.pid); });
    mbtnVer(res.pid);
    mlinksBaixar(res.pid, res.name); mbtnCapa(res.pid);
    mbtn("Fechar", closeModal);
  });
};
$("#tnStick").onclick = () => openStickman();

// ======================================================= 🤖 ESTILOS IA (skills do Claude Code)
const SKI = { d: null, sel: null, arqs: [], resp: {} };
async function openSkills() {
  if (!showOnly("#skillsia")) return;
  carregarVozes().catch(() => { });
  $("#iaLista").innerHTML = '<div class="mu">Carregando…</div>';
  try { SKI.d = await api("/api/skills-ia"); } catch (e) { $("#iaLista").innerHTML = `<div class="card">❌ ${esc(errTxt(e))}</div>`; return; }
  skiStatus(); skiQuiz(); skiLista(); skiResumo(); rcRender("ia"); estCarregar();
}
function skiStatus() {
  const d = SKI.d, n = d.skills.filter((s) => s.instalada).length;
  const falta = d.skills.some((s) => !s.instalada && s.na_fonte) || d.ajudantes.some((a) => !a.instalada);
  $("#iaStatus").innerHTML = `<span class="gtag ${d.claude ? "auto" : ""}" title="${d.claude ? "O painel roda o Claude sozinho" : "Instale o app do Claude (claude.ai/download) e entre na sua conta."}">${d.claude ? "✅ Claude Code pronto" : "⚠ Claude Code não achado"}</span>
    <span class="gtag">${n}/${d.skills.length} estilos instalados</span>${d.fila ? `<span class="gtag">⏳ ${d.fila} na fila</span>` : ""}
    ${d.pode_instalar ? `<button class="btn ${falta ? "go" : ""}" id="iaInstalar">⬇ ${falta ? "Instalar skills" : "Reinstalar/atualizar"}</button>` : ""}`;
  $("#iaComo").open = n === 0;
  $("#iaFazer").disabled = !d.claude;
  const b = $("#iaInstalar");
  if (b) b.onclick = async () => {
    b.disabled = true; b.textContent = "Instalando…";
    try { const r = await jpost("/api/skills-ia/instalar", {}); toast(`✅ ${r.instaladas.length} skills instaladas`, 4000); openSkills(); } catch (e) { toast("❌ " + errTxt(e), 6000); b.disabled = false; }
  };
}
function skiQuiz() {
  const q = SKI.d.quiz || [];
  $("#iaQuiz").innerHTML = `<b>Em dúvida?</b>` + q.map((p, i) => `<div class="iaQ"><span>${esc(p.p)}</span>${p.op.map((o, j) => `<button class="btn mini ${SKI.resp[i] === j ? "on" : ""}" data-q="${i}" data-o="${j}">${esc(o.t)}</button>`).join("")}</div>`).join("")
    + (Object.keys(SKI.resp).length ? `<button class="btn mini" id="iaQLimpa">↺ ver todos</button>` : "");
  $("#iaQuiz").querySelectorAll("[data-q]").forEach((b) => (b.onclick = () => { SKI.resp[b.dataset.q] = +b.dataset.o; skiQuiz(); skiLista(); }));
  const l = $("#iaQLimpa"); if (l) l.onclick = () => { SKI.resp = {}; skiQuiz(); skiLista(); };
}
function skiLista() {
  const q = SKI.d.quiz || [], resp = Object.entries(SKI.resp);
  const rec = (id) => resp.length > 0 && resp.every(([i, j]) => (q[i].op[j].rec || []).includes(id));
  const l = [...SKI.d.skills].sort((a, b) => rec(b.id) - rec(a.id));
  const ent = { video: "🎥 seu vídeo", texto: "✍️ só texto", ambos: "🎥 vídeo ou ✍️ texto" };
  skiFavs();
  $("#iaLista").innerHTML = l.map((s) => `<div class="iaC ${SKI.sel === s.id ? "on" : ""} ${resp.length && !rec(s.id) ? "apag" : ""}">
    <div class="iaV" ${s.preview_url ? `data-iaver="${esc(s.id)}" title="Clique pra ver o exemplo com som"` : ""}>${skiEstrela(s)}${s.preview_url ? `<video src="${s.preview_url}" ${s.capa_url ? `poster="${s.capa_url}"` : ""} class="apV" muted loop playsinline preload="none" onmouseenter="this.play()" onmouseleave="if(!AP.ativos.has(this))this.pause()"></video><span class="iaPlay">▶ ver exemplo</span>` : `<div class="iaEmo">${s.emoji}<small>exemplo em breve</small></div>`}</div>
    <div class="iaT"><b>${s.emoji} ${esc(s.nome)}</b>${rec(s.id) ? ' <span class="gtag auto">indicado pra você</span>' : ""}${SKI_EVITAR[s.id] ? ` <span class="iaEvitar" title="${esc(SKI_EVITAR[s.id])}">evitar</span>` : ""}
      <span class="tag">${ent[s.entrada] || ""}</span><small>${esc(s.quando)}</small>
      ${s.instalada ? `<button class="btn mini go" data-skusar="${esc(s.id)}">${SKI.sel === s.id ? "✔ Escolhido" : "Usar este"}</button>` : `<span class="mu">não instalado${s.na_fonte ? " — clique em ⬇ Instalar skills" : ""}</span>`}</div></div>`).join("");
  $("#iaLista").querySelectorAll("[data-skusar]").forEach((b) => (b.onclick = () => skiEscolher(b.dataset.skusar)));
  skiFavBind($("#iaLista"));
  $("#iaLista").querySelectorAll("[data-iaver]").forEach((v) => (v.onclick = () => { const x = SKI.d.skills.find((k) => k.id === v.dataset.iaver); if (x) openVid({ nome: x.nome, video_url: x.preview_url, formato: x.formato, fazer: () => { if (x.instalada) skiEscolher(x.id); else toast("Instale as skills primeiro (⬇ Instalar skills)", 4500); } }); }));
}
// ⭐ Favoritos: estrela em cada card (salva em favoritos.json) + seção no topo com prévia tocando sozinha
const SKI_EVITAR = { "mg-aurora-glass": "Estilo que não agradou nos testes — prefira outro" };
const skiEstrela = (s) => `<button class="iaStar ${s.favorito ? "on" : ""}" data-skfav="${esc(s.id)}" title="${s.favorito ? "Tirar dos favoritos" : "Marcar como favorito"}">${s.favorito ? "★" : "☆"}</button>`;
function skiFavs() {
  const box = $("#iaFavs"), f = SKI.d.skills.filter((s) => s.favorito);
  box.classList.toggle("hidden", !f.length);
  if (!f.length) { box.innerHTML = ""; return; }
  box.innerHTML = `<h4 class="iaFavH">⭐ Favoritos <small class="mu">clique na ★ de qualquer estilo pra pôr ou tirar daqui</small></h4><div class="iaFavL">` + f.map((s) => {
    const v = s.fav_preview ? `<video src="${s.fav_preview}" muted loop autoplay playsinline preload="auto"></video>`
      : s.preview_url ? `<video src="${s.preview_url}" ${s.capa_url ? `poster="${s.capa_url}"` : ""} muted loop playsinline preload="none" onmouseenter="this.play()" onmouseleave="this.pause()"></video>`
      : `<div class="iaEmo">${s.emoji}</div>`;
    return `<div class="iaFC ${SKI.sel === s.id ? "on" : ""}"><div class="iaFV">${skiEstrela(s)}${v}</div>
      <div class="iaFT"><b>${s.emoji} ${esc(s.nome)}</b>${s.instalada ? `<button class="btn mini go" data-skusar="${esc(s.id)}">${SKI.sel === s.id ? "✔ Escolhido" : "Usar este"}</button>` : `<span class="mu">não instalado</span>`}</div></div>`;
  }).join("") + "</div>";
  box.querySelectorAll("[data-skusar]").forEach((b) => (b.onclick = () => skiEscolher(b.dataset.skusar)));
  skiFavBind(box);
}
function skiFavBind(raiz) {
  raiz.querySelectorAll("[data-skfav]").forEach((b) => (b.onclick = async (ev) => {
    ev.stopPropagation();
    const s = SKI.d.skills.find((k) => k.id === b.dataset.skfav); if (!s) return;
    const novo = !s.favorito; b.disabled = true;
    try { await jpost("/api/skills-ia/favorito", { id: s.id, fav: novo }); s.favorito = novo; skiLista(); toast(novo ? `★ ${s.nome} nos favoritos` : `☆ ${s.nome} saiu dos favoritos`, 2500); }
    catch (e) { b.disabled = false; toast("❌ " + errTxt(e), 5000); }
  }));
}
function skiEscolher(id) {
  const s = SKI.d.skills.find((x) => x.id === id); if (!s) return;
  SKI.sel = id; skiLista();
  $("#iaForm").classList.remove("hidden");
  $("#iaEscolhido").textContent = `${s.emoji} ${s.nome} — mande o material`;
  $("#iaVidRow").classList.toggle("hidden", s.entrada === "texto");
  $("#iaAudRow").classList.toggle("hidden", s.entrada === "video");
  $("#iaVozRow").classList.toggle("hidden", s.entrada === "video");
  $("#iaVidObrig").textContent = s.entrada === "video" ? "(obrigatório — você falando pra câmera; pode enviar vários)" : "(opcional; pode enviar vários)";
  $("#iaTxtLbl").textContent = s.entrada === "video" ? "Do que fala o vídeo (opcional)" : "Tema ou copy";
  $("#iaTexto").placeholder = "Ex.: " + s.exemplo + (s.entrada !== "video" ? "\n\nQuer vários? Marque 📦 Lote e escreva um tema por linha." : "");
  skiResumo();
  try { $("#iaNicho").value = $("#iaNicho").value || localStorage.getItem("ia_nicho") || ""; } catch (e) { }
  if (SKI.idSk !== id) skiIdeias(/^https?:\/\/\S+\.\S+/.test($("#iaRef").value.trim()) ? "parecidas" : "novas");
  $("#iaForm").scrollIntoView({ behavior: "smooth", block: "start" });
}
function skiEnviar(f, onp) {
  return new Promise((ok, ko) => {
    const fd = new FormData(); fd.append("file", f);
    const x = new XMLHttpRequest(); x.open("POST", "/api/arquivo");
    x.upload.onprogress = (e) => { if (e.lengthComputable) onp(Math.round((100 * e.loaded) / e.total)); };
    x.onload = () => { let r = {}; try { r = JSON.parse(x.responseText); } catch (e) { } if (x.status < 300) ok(r); else ko(new Error(r.detail || "não consegui enviar")); };
    x.onerror = () => ko(new Error("não consegui enviar"));
    x.send(fd);
  });
}
function skiArqs() {
  $("#iaArqs").innerHTML = SKI.arqs.map((a, i) => `<div class="iaArq">${a.erro ? "❌" : a.ok ? "✅" : `⏳ ${a.pct || 0}%`} ${esc(a.nome)}${a.ok ? ` · ${fmtSeg(a.dur)}` : ""}${a.erro ? ` — ${esc(a.erro)}` : ""} <button class="btn mini" data-skrm="${i}" title="Tirar">✖</button></div>`).join("");
  $("#iaArqs").querySelectorAll("[data-skrm]").forEach((b) => (b.onclick = () => { SKI.arqs.splice(+b.dataset.skrm, 1); skiArqs(); skiResumo(); }));
}
$("#iaArq").onchange = async () => {
  const fs = [...$("#iaArq").files]; $("#iaArq").value = "";
  for (const f of fs) {
    const it = { nome: f.name, pct: 0 }; SKI.arqs.push(it); skiArqs();
    try { Object.assign(it, await skiEnviar(f, (p) => { it.pct = p; skiArqs(); }), { ok: true, nome: f.name }); } catch (e) { it.erro = String(e.message || e); }
    skiArqs(); skiResumo();
  }
};
$("#iaAud").onchange = async () => {
  const f = $("#iaAud").files[0]; $("#iaAud").value = ""; if (!f) return;
  SKI.audio = null; $("#iaAudInfo").textContent = "⏳ enviando…";
  const fd = new FormData(); fd.append("file", f);
  try { const r = await api("/api/vi/audio", { method: "POST", body: fd }); SKI.audio = { id: r.audio_id, nome: f.name };
    $("#iaAudInfo").innerHTML = `✅ ${esc(f.name)} · ${fmtSeg(r.dur)} <button class="btn mini" id="iaAudTirar">✖</button>`;
    $("#iaAudTirar").onclick = () => { SKI.audio = null; $("#iaAudInfo").textContent = ""; skiResumo(); };
  } catch (e) { $("#iaAudInfo").textContent = "❌ " + errTxt(e); }
  skiResumo();
};
function skiItens() {
  const txt = $("#iaTexto").value.trim(), vids = SKI.arqs.filter((a) => a.ok);
  if (SKI.audio && !vids.length) return [{ texto: txt, audio_id: SKI.audio.id }];
  const linhas = $("#iaLote").checked ? txt.split(/\n+/).map((t) => t.trim()).filter(Boolean) : txt ? [txt] : [];
  if (vids.length) return vids.map((v, i) => ({ arquivo_id: v.arquivo_id, video_nome: v.nome, texto: linhas.length === vids.length ? linhas[i] : linhas.length === 1 ? linhas[0] : "" }));
  return linhas.map((t) => ({ texto: t }));
}
function skiResumo() {
  if (!SKI.sel || !SKI.d) return;
  const n = skiItens().length * +$("#iaVersoes").value;
  $("#iaResumo").textContent = n ? `Vai fazer ${n} vídeo${n > 1 ? "s" : ""}. ` + (SKI.d.claude ? "O Claude faz 1 por vez (uns 10-30 min cada; a 1ª vez de cada estilo demora mais). Pode fechar e acompanhar em 📂 Meus vídeos." : "⚠ Falta o app do Claude neste PC: instale em claude.ai/download, entre na sua conta (plano Pro ou superior) e reabra o painel.") : "";
  $("#iaFazer").textContent = (n > 1 ? `🤖 Fazer ${n} vídeos` : "🤖 Fazer agora") + estTxt("skill:" + SKI.sel, "skill", n || 1);
  $("#iaFazer").title = estTitulo("skill:" + SKI.sel, "skill");
  skiPrevVis();
}
["#iaTexto", "#iaLote", "#iaVersoes"].forEach((s) => { $(s).addEventListener("input", skiResumo); $(s).addEventListener("change", skiResumo); });
async function skiMandar(so, prev, fixo) {
  if (!SKI.sel) return toast("Escolha um estilo primeiro.");
  if (SKI.arqs.some((a) => !a.ok && !a.erro)) return toast("Espere o envio do vídeo terminar (✅).");
  const s = SKI.d.skills.find((x) => x.id === SKI.sel);
  if (!prev && !skiItens().length && s.entrada !== "video" && !(await ideiaAuto("#iaTexto", { skill: SKI.sel, ref: $("#iaRef").value.trim(), linha: true }))) return;
  const body = prev || { skill: SKI.sel, itens: skiItens(), versoes: +$("#iaVersoes").value, ref: $("#iaRef").value.trim(), duracao: +$("#iaDur").value,
    marca: $("#iaMarca").value.trim(), canal: $("#iaCanal").value.trim(), obs: $("#iaObs").value.trim(), so_pedido: so,
    voz: $("#iaVoz").value, formato: $("#iaFmt").value,
    texto_fixo: !!(fixo || (SKI.fixo && $("#iaTexto").value.trim() === SKI.fixo)) };   // 📝 roteiro aprovado: o Claude não reescreve
  try { localStorage.setItem("sk_marca", body.marca); if (body.canal) localStorage.setItem("pedido_canal", body.canal); } catch (e) { }
  let r; try { r = await jpost("/api/skills-ia/pedido", body); } catch (e) { return toast("❌ " + errTxt(e), 6000); }
  filaAtualizar(true);
  if (r.n === 1) return acompanhar(r.jobs[0], `🤖 ${s.nome}…`, skiFim, (jb) => { if (jb.status !== "cancelado") setTimeout(() => mbtn("🔁 Tentar de novo", () => { closeModal(); skiMandar(false, body); }, "go"), 0); });
  toast(`✅ ${r.n} vídeos na fila! Acompanhe em 📂 Meus vídeos.`, 5000); loadHome();
}
function skiFim(res) {
  if (res.precisa_claude && res.sem_claude === false) {   // QA: só criou o pedido (o Claude existe, mas não rodou agora)
    $("#mTitle").textContent = "📝 Pedido criado"; $("#mMsg").textContent = "A pasta com o PEDIDO.md ficou pronta em 📂 Meus vídeos.";
    mbtn("Fechar", closeModal, "go"); return;
  }
  if (res.precisa_claude) {
    $("#mTitle").textContent = "⚠ Falta o app do Claude";
    $("#mMsg").textContent = "Instale o app do Claude (claude.ai/download), entre na sua conta (plano Pro ou superior) e clique em Fazer de novo. O pedido ficou guardado em 📂 Meus vídeos.";
    mbtn("Fechar", closeModal, "go"); return;
  }
  $("#mTitle").textContent = "✅ Vídeo pronto!"; $("#mMsg").textContent = res.name;
  mbtnVer(res.pid);
  mbtn("✏ Abrir no editor", () => { closeModal(); openProject(res.pid); });
  mlinksBaixar(res.pid, res.name); mbtnCapa(res.pid);
  mbtn("Fechar", closeModal, "go");
}
$("#iaFazer").onclick = () => skiMandar(false);
// ---- 💡 ideias de tema (IA do PC, grátis): novas ou parecidas com o link
const skiLinha = (x) => x.titulo + (x.gancho ? ` — gancho: ${x.gancho}` : "");
async function skiIdeias(modo) {
  if (!SKI.sel) return;
  const ref = modo === "parecidas" ? $("#iaRef").value.trim() : "";
  if (modo === "parecidas" && !/^https?:\/\/\S+\.\S+/.test(ref)) return toast("Cole primeiro o link do vídeo no campo “Copiar um vídeo”.", 3500);
  if (SKI.idSk !== SKI.sel || SKI.idRef !== ref) SKI.ideias = [];
  SKI.idSk = SKI.sel; SKI.idRef = ref;
  const box = $("#iaIdeias"), pede = SKI.sel;
  box.innerHTML = `<div class="mu">⏳ ${ref ? "Lendo o vídeo e pensando em temas parecidos…" : "Pensando em ideias pra você…"} (até 1 min na 1ª vez)</div>`;
  try { localStorage.setItem("ia_nicho", $("#iaNicho").value.trim()); } catch (e) { }
  let r;
  try { r = await jpost("/api/skills-ia/ideias", { skill: SKI.sel, nicho: $("#iaNicho").value.trim(), ref, evitar: SKI.ideias.map((i) => i.titulo) }); }
  catch (e) { if (SKI.sel === pede) box.innerHTML = `<div class="mu">❌ ${esc(errTxt(e))}</div>`; return; }
  if (SKI.sel !== pede) return;
  SKI.ideias = r.ideias;
  box.innerHTML = (r.ref ? `<div class="iaRefInfo">🔗 Parecidas com: <b>${esc(r.ref.titulo)}</b>${r.ref.canal ? ` · ${esc(r.ref.canal)}` : ""}</div>` : "")
    + `<div class="iaChips">${r.ideias.map((x, i) => `<button class="iaChip" data-idi="${i}" title="Clique pra usar este tema"><b>${esc(x.titulo)}</b>${x.gancho ? `<small>“${esc(x.gancho)}”</small>` : ""}</button>`).join("")}</div>`
    + `<div class="iaIdAcoes"><button class="btn mini go" id="iaIdTodas">➕ Usar todas (1 vídeo cada)</button><button class="btn mini" id="iaIdMais">🔄 Outras ideias</button></div>`;
  box.querySelectorAll("[data-idi]").forEach((b) => (b.onclick = () => {
    const t = $("#iaTexto"), l = skiLinha(SKI.ideias[+b.dataset.idi]);
    t.value = $("#iaLote").checked && t.value.trim() ? t.value.trim() + "\n" + l : l;
    b.classList.add("on"); skiResumo();
  }));
  $("#iaIdTodas").onclick = () => { $("#iaLote").checked = true; $("#iaTexto").value = SKI.ideias.map(skiLinha).join("\n"); skiResumo(); toast(`✅ ${SKI.ideias.length} temas no lote — 1 vídeo pra cada`); };
  $("#iaIdMais").onclick = () => skiIdeias(ref ? "parecidas" : "novas");
}
$("#iaSugerir").onclick = async () => {
  const b = $("#iaSugerir"), old = b.textContent; b.disabled = true; b.textContent = "⏳ Pensando…";
  await skiIdeias(/^https?:\/\/\S+\.\S+/.test($("#iaRef").value.trim()) ? "parecidas" : "novas");
  b.disabled = false; b.textContent = old;
  if (!SKI.ideias.length) return;
  $("#iaTexto").value = skiLinha(SKI.ideias[0]); const c = document.querySelector('#iaIdeias [data-idi="0"]'); if (c) c.classList.add("on");
  skiResumo(); toast("💡 Ideia colocada! Não gostou? Clique em outra logo abaixo.", 4000);
};
$("#iaIdNovas").onclick = () => { SKI.idRef = null; skiIdeias("novas"); };
$("#iaIdParecidas").onclick = () => skiIdeias("parecidas");
$("#iaRef").addEventListener("input", () => {
  clearTimeout(SKI.refT);
  const v = $("#iaRef").value.trim();
  if (/^https?:\/\/\S+\.\S+/.test(v) && v !== SKI.idRef) SKI.refT = setTimeout(() => skiIdeias("parecidas"), 700);
});
$("#tnSkills").onclick = () => openSkills();
NEW_SECS.push("#skillsia"); TELA_NOME["#skillsia"] = "Estilos IA";

// ======================================================= ⚡ RANKING DE VELOCIDADE
NEW_SECS.push("#ranking"); TELA_NOME["#ranking"] = "Ranking";
const RK = { filtro: "todos", dados: null };
$("#tnRanking").onclick = () => openRanking();
async function openRanking() {
  if (!showOnly("#ranking")) return;
  if (!RK.dados) {
    try {
      const d = await api("/api/skills-ia");
      const ferramentas = d.ferramentas || [];
      RK.dados = [
        ...ferramentas.map((f) => ({ ...f, tipo: "ferramenta" })),
        ...d.skills.map((s) => ({ ...s, tipo: "skill", peso: s.peso || 2, tempo: s.tempo || "?", categoria: s.categoria || (s.formato === "longo" ? "longo" : "short") }))
      ].sort((a, b) => (a.peso - b.peso) || a.nome.localeCompare(b.nome));
    } catch (e) { $("#rkGrid").innerHTML = `<div class="card">❌ ${esc(errTxt(e))}</div>`; return; }
  }
  rkRender();
}
function rkRender() {
  const f = RK.filtro;
  const lista = RK.dados.filter((i) => f === "todos" || i.categoria === f);
  const tiers = [
    { peso: 1, titulo: "⚡ Leve — pronto em minutos, roda no seu PC", cor: "p1" },
    { peso: 2, titulo: "⏳ Médio — alguns minutos, usa o Claude", cor: "p2" },
    { peso: 3, titulo: "🔥 Pesado — demora mais, usa mais o Claude", cor: "p3" }
  ];
  let pos = 1;
  let html = "";
  for (const tier of tiers) {
    const items = lista.filter((i) => i.peso === tier.peso);
    if (!items.length) continue;
    html += `<div class="rkTier"><h4><span class="rkDot ${tier.cor}"></span>${tier.titulo}</h4>`;
    for (const it of items) {
      const custo = it.peso === 1 ? "free" : it.peso === 2 ? "tk" : "heavy";
      const custoTxt = it.peso === 1 ? "Grátis / local" : it.peso === 2 ? "Usa o Claude" : "Usa bastante o Claude";
      const fmtTxt = it.formato === "short" ? "📱 Short" : it.formato === "longo" ? "🎬 Longo" : "📱🎬 Ambos";
      html += `<div class="rkRow">
        <div class="rkPos">${pos++}</div>
        <div class="rkEmo">${it.emoji}</div>
        <div class="rkInfo"><b>${esc(it.nome)}</b><small>${esc(it.quando || "")}</small>
          <div class="rkTags"><span class="rkTag ${custo}">${custoTxt}</span><span class="rkTag">${fmtTxt}</span>${it.tipo === "skill" ? '<span class="rkTag tk">🤖 Claude</span>' : '<span class="rkTag free">💻 Seu PC</span>'}</div></div>
        <div class="rkTempo">${it.tempo || "?"}</div>
        <div class="rkBar"><span class="${tier.cor}"></span></div>
      </div>`;
    }
    html += `</div>`;
  }
  if (!html) html = '<div class="mu">Nenhum item nessa categoria.</div>';
  $("#rkGrid").innerHTML = html;
  $("#rkFiltros").querySelectorAll("[data-rkf]").forEach((b) => {
    b.classList.toggle("on", b.dataset.rkf === RK.filtro);
    b.onclick = () => { RK.filtro = b.dataset.rkf; rkRender(); };
  });
}

// ======================================================= ✍️ ASSISTENTE DE ROTEIRO (assunto → 5 temas → roteiro pronto)
const RA_TIPOS = [["historia", "📖 Só história"], ["primeira", "🙋 Em 1ª pessoa"], ["gancho", "🪝 Ganchos fortes"], ["cta", "💬 CTA com palavra-chave"], ["lista", "🔢 Lista / curiosidades"], ["tutorial", "🎓 Passo a passo"]];
const RA = { alvo: null, tema: "", dur: 60, tipos: ["gancho"], motor: "pc" };
function raChips(sel, attr, on) { document.querySelectorAll(`${sel} [data-${attr}]`).forEach((b) => b.classList.toggle("on", on(b.dataset[attr]))); }
function roteiroAssistente(alvo) {
  RA.alvo = alvo; RA.tema = ""; RA.dur = alvo.dur ? alvo.dur() : 60;
  modal("✍️ Criar roteiro pra mim"); $("#mBar").style.width = "0%";
  const durs = [[30, "30 s"], [60, "1 min"], [90, "1:30"], [120, "2 min"], [150, "2:30"], [180, "3 min"], [300, "5 min"], [600, "10 min"], [900, "15 min"], [1200, "20 min"]];
  if (!durs.some(([x]) => x === RA.dur)) durs.push([RA.dur, fmtSeg(RA.dur)]);
  $("#mMsg").innerHTML = `<div class="raBox">
    <label>1. Sobre o que é o vídeo? <small>(uma ideia solta: “vender bombom”, “minha mulher me deixou”, “curiosidades do Japão”)</small></label>
    <div class="raRow"><input id="raAssunto" type="text" placeholder="Escreva o assunto" value="${esc(($(alvo.tema) || {}).value || "")}"><button class="btn go" id="raTemasBtn">💡 Me dá 5 temas</button></div>
    <div id="raTemas" class="raTemas"></div>
    <label>2. Duração</label><div class="raChips" id="raDur">${durs.map(([x, t]) => `<button class="btn mini" data-s="${x}">${t}</button>`).join("")}</div>
    <label>3. Tipo de vídeo <small>(pode marcar vários)</small></label><div class="raChips" id="raTipos">${RA_TIPOS.map(([k, t]) => `<button class="btn mini" data-k="${k}">${t}</button>`).join("")}</div>
    <div class="raRow hidden" id="raPalRow"><input id="raPalavra" type="text" placeholder="Palavra que a pessoa comenta (ex.: EU QUERO)"></div>
    <label>4. Quem escreve?</label><div class="raChips" id="raMotor"><button class="btn mini" data-m="pc">🆓 IA do PC (grátis)</button><button class="btn mini" data-m="claude">🧠 Claude (melhor, pesquisa os fatos)</button></div>
    <div id="raStatus" class="mu"></div>
    <div id="raOut" class="hidden"><label>Seu roteiro <small>(dá pra editar à vontade)</small></label><textarea id="raTexto" rows="10"></textarea></div></div>`;
  const pinta = () => { raChips("#raDur", "s", (v) => +v === RA.dur); raChips("#raTipos", "k", (v) => RA.tipos.includes(v)); raChips("#raMotor", "m", (v) => v === RA.motor); $("#raPalRow").classList.toggle("hidden", !RA.tipos.includes("cta")); };
  $("#raDur").onclick = (e) => { const b = e.target.closest("[data-s]"); if (b) { RA.dur = +b.dataset.s; pinta(); } };
  $("#raTipos").onclick = (e) => { const b = e.target.closest("[data-k]"); if (!b) return; const k = b.dataset.k; RA.tipos = RA.tipos.includes(k) ? RA.tipos.filter((x) => x !== k) : [...RA.tipos, k]; pinta(); };
  $("#raMotor").onclick = (e) => { const b = e.target.closest("[data-m]"); if (b) { RA.motor = b.dataset.m; pinta(); } };
  $("#raTemasBtn").onclick = raTemas;
  $("#raAssunto").onkeydown = (e) => { if (e.key === "Enter") raTemas(); };
  pinta(); raBotoes(false);
}
function raBotoes(temTexto) {
  $("#mBtns").innerHTML = "";
  if (temTexto) mbtn("✅ Usar este roteiro", () => { const t = $("#raTexto").value.trim(); if (!t) return; RA.alvo.usar(RA.tema || $("#raAssunto").value.trim(), t); closeModal(); toast("✅ Roteiro colocado! Agora é só clicar em Fazer.", 4500); }, "go");
  mbtn(temTexto ? "🔄 Gerar outro" : "✍️ Gerar roteiro", raGerar, temTexto ? "" : "go");
  mbtn("Fechar", closeModal);
}
async function raTemas() {
  const a = $("#raAssunto").value.trim(); if (!a) return toast("Escreva o assunto primeiro (ex.: vender bombom).");
  const b = $("#raTemasBtn"); b.disabled = true; b.textContent = "⏳ Pensando…"; $("#raTemas").innerHTML = "";
  try {
    const r = await jpost("/api/skills-ia/ideias", { assunto: a, formato: RA.dur > 90 ? "longo" : "short", nicho: nichoSalvo() });
    $("#raTemas").innerHTML = r.ideias.slice(0, 5).map((x, i) => `<button class="iaChip" data-i="${i}"><b>${esc(x.titulo)}</b>${x.gancho ? `<small>“${esc(x.gancho)}”</small>` : ""}</button>`).join("");
    $("#raTemas").querySelectorAll("[data-i]").forEach((c) => (c.onclick = () => { RA.tema = r.ideias[+c.dataset.i].titulo; $("#raTemas").querySelectorAll(".iaChip").forEach((y) => y.classList.toggle("on", y === c)); }));
  } catch (e) { $("#raTemas").innerHTML = `<div class="mu">❌ ${esc(errTxt(e))}</div>`; }
  b.disabled = false; b.textContent = "💡 Me dá 5 temas";
}
async function raGerar() {
  const tema = RA.tema || $("#raAssunto").value.trim(); if (!tema) return toast("Escreva o assunto ou escolha um tema.");
  $("#mBtns").innerHTML = ""; $("#raStatus").textContent = "⏳ Começando…";
  let r; try { r = await jpost("/api/roteiro/gerar", { tema, duracao: RA.dur, tipos: RA.tipos, palavra: ($("#raPalavra") || {}).value || "", motor: RA.motor }); }
  catch (e) { $("#raStatus").textContent = "❌ " + errTxt(e); return raBotoes(false); }
  for (;;) {
    let j; try { j = await api("/api/job/" + r.job); } catch (e) { await new Promise((ok) => setTimeout(ok, 2000)); continue; }
    if (!$("#raStatus")) return;
    $("#mBar").style.width = j.pct + "%"; $("#raStatus").textContent = `⏳ ${j.msg}`;
    if (j.done) {
      if (j.error) { $("#raStatus").textContent = "❌ " + j.error.slice(0, 300); return raBotoes(false); }
      $("#raStatus").textContent = `✅ Roteiro sobre “${tema}”` + (j.result.custo_usd ? " · feito com o Claude" : " · grátis");
      $("#raOut").classList.remove("hidden"); $("#raTexto").value = j.result.roteiro; return raBotoes(true);
    }
    await new Promise((ok) => setTimeout(ok, 1500));
  }
}
// botão "✍️ Criar roteiro pra mim" ao lado do tema em cada tela de criar vídeo
[
  { tema: "#pTema", dur: () => PED.dur, usar: (t, x) => { if (t) $("#pTema").value = t; $("#pTemRoteiro").checked = true; $("#pTemRoteiro").onchange(); $("#pRoteiro").value = x; } },
  { tema: "#viTema", dur: () => VI.dur, usar: (t, x) => { if (t) $("#viTema").value = t; setModoVi("roteiro"); $("#viRoteiro").value = x; } },
  { tema: "#shTema", dur: () => SH.dur, usar: (t, x) => { if (t) $("#shTema").value = t; setModoSh("roteiro"); $("#shRoteiro").value = x; } },
  { tema: "#skTema", dur: () => SK.dur, usar: (t, x) => { if (t) $("#skTema").value = t; const b = document.querySelector('[data-skm="roteiro"]'); if (b) b.click(); $("#skRoteiro").value = x; } },
  { tema: "#iaTexto", dur: () => +$("#iaDur").value || 45, usar: (t, x) => { $("#iaTexto").value = x; $("#iaLote").checked = false; skiResumo(); } },
].forEach((a) => {
  const el = $(a.tema); const row = el && el.closest(".row"); if (!row) return;
  const b = document.createElement("button"); b.type = "button"; b.className = "btn sugerirBtn raBtn"; b.textContent = "✍️ Criar roteiro pra mim";
  b.onclick = () => roteiroAssistente(a); row.appendChild(b);
});

// ======================================================= 🔑 AVISO DE CHAVES (novato: 1º passo)
async function chaveBanner() {
  let a; try { a = await api("/api/ajustes"); } catch (e) { return; }
  const ok = a.chaves_ok || {}, falta = [["pexels_key", "Pexels"], ["pixabay_key", "Pixabay"], ["gemini_key", "Gemini"]].filter(([k]) => !ok[k]).map(([, n]) => n);
  let b = $("#chaveBanner");
  if (!falta.length) { if (b) b.remove(); return; }
  if (!b) { b = document.createElement("div"); b.id = "chaveBanner"; b.className = "card chaveBanner"; $("#inicio").prepend(b); }
  b.innerHTML = `<div><b>🔑 1º passo: pegue suas chaves grátis (uns 5 minutos)</b><small>Falta: ${falta.join(", ")}. Com elas o painel faz os vídeos no automático, com mais imagens, vozes e clonagem. Tem o link de cada uma do lado do campo.</small></div><button class="btn big go" id="chaveIr">Configurar agora</button>`;
  $("#chaveIr").onclick = async () => { await openAjustes(); const h = $("#ajChaves"); if (h) h.scrollIntoView({ behavior: "smooth", block: "start" }); };
}
const _openInicioSemChave = openInicio;
openInicio = async function (...x) { const r = await _openInicioSemChave.apply(this, x); const b = $("#chaveBanner"); if (b) b.remove(); return r; };   // 01/11: painel funciona sem chave nenhuma — nada de banner cobrando

// ---- 🔊 Ouvir a voz escolhida (Pedir vídeo, Clonar, Estilos IA)
$("#pFmt").onclick = (ev) => { const b = ev.target.closest("[data-pf]"); if (b) { PED.fmt = PED.fmtEsc = b.dataset.pf; raChips("#pFmt", "pf", (v) => v === PED.fmt); pedidoResumo(); } };
document.addEventListener("click", async (ev) => {
  const b = ev.target.closest("[data-ouvir]"); if (!b) return;
  const out = b.nextElementSibling; const voz = $(b.dataset.ouvir).value || (AJU.d || {}).voz || "";
  out.innerHTML = '<span class="mu">⏳ gerando prévia…</span>';
  try { const r = await jpost("/api/ajustes/testar", { item: "voz", valor: voz }); out.innerHTML = r.audio ? `<audio class="ajPlay" controls autoplay src="${r.audio}"></audio>` : esc(r.msg); }
  catch (e) { out.innerHTML = `<span class="bad"><svg class="ic st"><use href="#i-xc"/></svg> ${esc(errTxt(e))}</span>`; }
});

// ======================================================= 🔄 PAINEL SE ATUALIZA SOZINHO (sem F5)
(() => {
  const atual = ((document.querySelector('script[src*="app.js"]') || {}).src || "").match(/v=(\d+)/);
  if (!atual) return;
  const ocupado = () => !$("#modal").classList.contains("hidden") || !$("#editor").classList.contains("hidden") ||
    ["INPUT", "TEXTAREA", "SELECT"].includes((document.activeElement || {}).tagName);
  let aviso = false;
  const checar = async () => {
    if (document.hidden) return;   // leve 01/11: aba escondida não fica perguntando a versão a cada 15 s
    let v; try {   // QA 24/10: /api/versao (64 bytes) em vez de baixar a página inteira a cada 15 s
      const r = await fetch("/api/versao", { cache: "no-store" });
      v = r.ok ? String((await r.json()).v) : ((await (await fetch("/", { cache: "no-store" })).text()).match(/app\.js\?v=(\d+)/) || [])[1];
    } catch (e) { return; }
    if (!v || v === atual[1]) return;
    if (!ocupado()) return location.reload();
    if (!aviso) { aviso = true; toast("🔄 O painel foi atualizado — ele recarrega sozinho quando você terminar o que está fazendo.", 6000); }
  };
  setInterval(checar, 15000);
  document.addEventListener("visibilitychange", () => { if (!document.hidden) checar(); });
})();

// endereço direto: http://localhost:8780/#estilos abre a galeria, #copiar abre "Copiar estilo", #meus abre Meus vídeos
// endereço com parâmetro: #roteiro=<id> abre um roteiro salvo, #editor=<pid> abre o editor, #conferir=<pid> abre o Conferir imagens
(() => {
  const [h0, arg] = location.hash.split("=");
  const h = h0.split("?")[0];   // #inicio?novo=1
  const arg2 = arg ? decodeURIComponent(arg) : undefined;
  const rotas = { "#estilos": openGaleria, "#copiar": openCopiar, "#meus": loadHome, "#imagens": () => openVimg(), "#roteiro": () => openRoteiro(arg2),
    "#ajustes": openAjustes, "#bombando": openBombando, "#editor": () => openProject(arg2), "#conferir": () => openConferir(arg2),
    "#shorts": () => openShorts(), "#cortes": () => openCortes(arg2), "#falado": () => openFalado(arg2), "#ideias": () => openIdeias(arg2), "#extras": openExtras, "#skillsia": openSkills, "#stickman": () => openStickman(), "#vozes": () => openVozes(), "#feeds": () => openFeeds(arg2) };
  (rotas[h] || (() => setTimeout(() => (NAV_ABRE[h] || openInicio)(), 0)))();   // 07/11: #galeria, #vimg, #emalta… (NAV_ABRE fica mais embaixo: TDZ)
  // o #nome no endereço é igual ao id da seção → o navegador rola até ela e esconde o título atrás da barra; volta pro topo
  window.addEventListener("load", () => setTimeout(() => window.scrollTo(0, 0), 30));
  setTimeout(() => window.scrollTo(0, 0), 30);
})();

// ?menu=ideia | ?menu=criar → abre o menu ao carregar (usado nos prints de documentação)
try { const m = (location.search.match(/menu=(\w+)/) || [])[1]; if (m) setTimeout(() => { const b = $(m === "ideia" ? "#tnIdea" : "#tnCriar"); if (b) b.click(); }, 700); } catch (e) { }

// ======================================================= NAVEGAÇÃO COM HISTÓRICO (24/10): voltar = tela anterior de verdade
// Cada troca de tela vira um passo no histórico do navegador (history.pushState). Os botões "Voltar" do editor, da
// comparação e do pedido, e o Voltar do próprio navegador, voltam exatamente para a tela de onde você veio.
const NAV = { restaurando: false, cur: "", passos: 0 };
const NAV_ABRE = { "#inicio": () => openInicio(), "#galeria": () => openGaleria(), "#copiar": () => openCopiar(), "#vimg": () => openVimg(),
  "#roteiro": () => openRoteiro(), "#ajustes": () => openAjustes(), "#bombando": () => openBombando(), "#home": () => loadHome(),
  "#shorts": () => openShorts(), "#cortes": () => openCortes(), "#extras": () => openExtras(), "#skillsia": () => openSkills(), "#feeds": () => openFeeds(),
  "#vozes": () => openVozes(), "#stickman": () => openStickman(), "#emalta": () => (typeof openEmAlta === "function" ? openEmAlta() : null) };

// ======================================================= 🤖 PILOTO AUTOMÁTICO — fatia (a): rastrear + aprender
NEW_SECS.push("#autopilot"); TELA_NOME["#autopilot"] = "Piloto automático"; NAV_ABRE["#autopilot"] = () => openAutopilot();
const AP_TAG = { winner: "🚀", flop: "💤", normal: "•", novo: "🆕", sem_dados: "·" };
async function openAutopilot() {
  if (!showOnly("#autopilot")) return;
  let st = {};
  try { st = await api("/api/autopilot"); apRender(st); } catch (e) { }
  apCarregarOpcoes(st).catch(() => { });
}
async function apCarregarOpcoes(st) {
  st = st || {};
  try {
    const feeds = await api("/api/feeds");
    $("#apFeed").innerHTML = feeds.length
      ? feeds.map((f) => `<option value="${esc(f.id)}" ${st.feed_id === f.id ? "selected" : ""}>${esc(f.nome)}${f.n ? ` (${f.n} vídeos)` : ""}</option>`).join("")
      : `<option value="">— crie um Feed do seu nicho primeiro —</option>`;
  } catch (e) { }
  try {
    const es = await api("/api/autopilot/estilos");
    $("#apEstilo").innerHTML = es.map((e) => `<option value="${esc(e.id)}" ${st.estilo === e.id ? "selected" : ""}>${esc(e.nome)}</option>`).join("");
  } catch (e) { }
}
function apRender(st) {
  $("#apCanal").value = st.canal || "";
  const s = st.stats || {}, ap = st.aprendido || {};
  if (!st.atualizado) {
    $("#apStatus").innerHTML = "Cole o link do seu canal e clique em <b>Rastrear agora</b>.";
    $("#apResumo").classList.add("hidden"); $("#apTabela").innerHTML = ""; return;
  }
  const quando = new Date(st.atualizado * 1000).toLocaleString();
  $("#apStatus").innerHTML = `Último rastreio: ${quando} · ${s.n} vídeos · mediana ${Math.round(s.mediana_vph || 0)} views/h · 🚀 ${s.winners || 0} estouraram · 💤 ${s.flops || 0} floparam`;
  const words = (ap.palavras_titulo || []).slice(0, 10).map((w) => `<span class="btn pill" style="pointer-events:none">${esc(w.palavra)}</span>`).join("");
  $("#apResumo").classList.remove("hidden");
  $("#apResumo").innerHTML = `<b>O que funciona no seu canal</b><p>${esc(ap.resumo || "—")}</p>${words ? `<div class="apWords">${words}</div>` : ""}`;
  const vs = (st.videos || []).slice().sort((a, b) => (b.vph || -1) - (a.vph || -1));
  $("#apTabela").innerHTML = `<table class="apTab"><thead><tr><th></th><th>Vídeo</th><th>Views</th><th>vs mediana</th><th></th></tr></thead><tbody>${vs.map((v) => `<tr class="ap-${v.classe}"><td title="${v.classe}">${AP_TAG[v.classe] || "·"}</td><td>${esc(v.titulo)}</td><td>${fmtNum(v.views)}</td><td>${v.razao ? v.razao + "×" : "—"}</td><td><button class="btn mini" data-apflop="${esc(v.id)}">🔍 Por quê?</button></td></tr>`).join("")}</tbody></table>`;
  $("#apTabela").querySelectorAll("[data-apflop]").forEach((b) => (b.onclick = () => apPorque(b.dataset.apflop)));
  apProds(st);
}
async function apPorque(id) {
  modal("🔍 Por que foi assim?"); $("#mMsg").textContent = "Analisando (comparando com os winners do nicho)…";
  let r; try { r = await jpost("/api/autopilot/flop", { id }); }
  catch (e) { closeModal(); return toast("❌ " + errTxt(e), 6000); }
  acompanhar(r.job, "🔍 Analisando…", async (res, fechado) => {
    if (fechado) return;
    const d = res || {};
    const s = d.sinais || {};
    const num = (x) => (x == null ? "—" : x);
    const linhasCsv = d.tem_csv
      ? `<div class="kitBox"><h4>YouTube Studio</h4><p>Impressões: <b>${num(s.impressoes)}</b> · CTR: <b>${num(s.ctr)}%</b> · Retenção: <b>${num(s.retencao_pct)}%</b> (${num(s.retencao_seg)}s)</p></div>`
      : `<p class="help">⚠ Sem o CSV do YouTube Studio: análise só com <b>views públicas</b>. Importe o CSV acima pra ver impressões, CTR e retenção.</p>`;
    $("#mMsg").innerHTML = `
      <div class="kitBox"><h4>${esc(s.titulo || "")}</h4><p><b>${esc(d.veredito || "")}</b></p>
        <p class="help">views/h ${num(s.vph)} · ${s.razao_vs_mediana ? s.razao_vs_mediana + "× a mediana" : "sem comparação"} · ${esc(s.classe || "")}</p></div>
      <div class="kitBox"><h4>Por quê</h4><ul>${(d.motivos || []).map((m) => `<li>${esc(m)}</li>`).join("") || "<li>—</li>"}</ul></div>
      <div class="kitBox"><h4>O que mudar no próximo</h4><ul>${(d.o_que_mudar || []).map((m) => `<li>${esc(m)}</li>`).join("") || "<li>—</li>"}</ul></div>
      ${linhasCsv}`;
    mbtn("Fechar", closeModal);
  });
}
function apProds(st) {
  const ps = (st.producoes || []).slice().reverse();
  if (!ps.length) { $("#apProds").innerHTML = ""; return; }
  $("#apProds").innerHTML = `<h4 style="margin:16px 0 6px">Vídeos que o piloto já fez</h4>` + ps.slice(0, 20).map((p) => {
    const quando = p.t ? new Date(p.t * 1000).toLocaleDateString() : "";
    const acts = p.pid ? `<div class="apActs"><button class="btn mini" data-apkit="${esc(p.pid)}">📋 Kit</button><button class="btn mini" data-apopen="${esc(p.pid)}">✏ Abrir</button></div>` : "";
    return `<div class="apProd"><div><b>${esc(p.titulo || p.tema || "—")}</b><small>${quando} · feed ${esc(p.feed || "—")} · inspirado em: ${esc((p.titulo_ref || "").slice(0, 50))}</small></div>${acts}</div>`;
  }).join("");
  $("#apProds").querySelectorAll("[data-apopen]").forEach((b) => (b.onclick = () => openProject(b.dataset.apopen)));
  $("#apProds").querySelectorAll("[data-apkit]").forEach((b) => (b.onclick = () => apAbrirKit(b.dataset.apkit)));
}
async function apAbrirKit(pid) {
  let kit = {};
  try { kit = await api("/api/autopilot/kit/" + encodeURIComponent(pid)); } catch (e) { }
  if (kit && kit.titulos) return apMostrarKit(kit, pid);
  modal("📋 Kit de publicação"); $("#mMsg").textContent = "Escrevendo o kit (título, descrição, tags, thumb)…";
  let r; try { r = await jpost("/api/autopilot/kit/" + encodeURIComponent(pid), {}); }
  catch (e) { closeModal(); return toast("❌ " + errTxt(e), 6000); }
  acompanhar(r.job, "📋 Escrevendo o kit…", async (res, fechado) => {
    if (fechado) return;
    try { apMostrarKit(await api("/api/autopilot/kit/" + encodeURIComponent(pid)), pid); } catch (e) { toast("❌ " + errTxt(e), 6000); }
  });
}
function apMostrarKit(kit, pid) {
  modal("📋 Kit de publicação");
  const copia = (txt) => navigator.clipboard && navigator.clipboard.writeText(txt).then(() => toast("✅ Copiado", 2000)).catch(() => { });
  const titulos = (kit.titulos || []).map((t, i) => `<div class="kitL"><span>${i === 0 ? "⭐" : (i + 1)}</span><b>${esc(t)}</b><button class="btn mini" data-kcopy="${esc(t)}">copiar</button></div>`).join("");
  const tags = (kit.tags || []).join(", ");
  $("#mMsg").innerHTML = `
    <div class="kitBox"><h4>Títulos (A/B — ⭐ é o principal)</h4>${titulos}</div>
    <div class="kitBox"><h4>Descrição</h4><textarea rows="6" id="kitDesc" readonly>${esc(kit.descricao || "")}</textarea></div>
    <div class="kitBox"><h4>Tags</h4><textarea rows="2" id="kitTags" readonly>${esc(tags)}</textarea></div>
    <div class="kitBox"><h4>Thumbnail</h4><p><b>Texto grande:</b> ${esc((kit.thumbnail || {}).texto || "—")}<br><b>Ideia:</b> ${esc((kit.thumbnail || {}).ideia || "—")}</p></div>
    <p class="help">Você copia e posta no YouTube. O painel nunca entra na sua conta.</p>`;
  mbtn("📋 Copiar descrição", () => copia(kit.descricao || ""));
  mbtn("🏷 Copiar tags", () => copia(tags));
  mbtn("🔄 Refazer", () => apRefazerKit(pid));
  mbtn("Fechar", closeModal);
  $("#mMsg").querySelectorAll("[data-kcopy]").forEach((b) => (b.onclick = () => copia(b.dataset.kcopy)));
}
async function apRefazerKit(pid) {
  $("#mMsg").textContent = "Reescrevendo…";
  let r; try { r = await jpost("/api/autopilot/kit/" + encodeURIComponent(pid), {}); }
  catch (e) { return toast("❌ " + errTxt(e), 6000); }
  acompanhar(r.job, "📋 Reescrevendo o kit…", async (res, fechado) => {
    if (fechado) return;
    try { apMostrarKit(await api("/api/autopilot/kit/" + encodeURIComponent(pid)), pid); } catch (e) { }
  });
}
$("#apRastrear") && ($("#apRastrear").onclick = async () => {
  const url = $("#apCanal").value.trim();
  $("#apStatus").textContent = "Rastreando…";
  let r; try { r = await jpost("/api/autopilot/rastrear", { url }); }
  catch (e) { $("#apStatus").textContent = ""; return toast("❌ " + errTxt(e), 6000); }
  acompanhar(r.job, "🤖 Rastreando o canal…", async (res, fechado) => {
    if (fechado) return;
    try { apRender(await api("/api/autopilot")); toast("✅ Canal rastreado", 4000); } catch (e) { }
  });
});
$("#apFeed") && ($("#apFeed").onchange = () => jpost("/api/autopilot/config", { feed_id: $("#apFeed").value }).catch(() => { }));
$("#apEstilo") && ($("#apEstilo").onchange = () => jpost("/api/autopilot/config", { estilo: $("#apEstilo").value }).catch(() => { }));
// 🎬 "Fazer o vídeo de hoje": antes de agir, pergunta qual IA escreve o roteiro e qual voz narra
$("#apLoop") && ($("#apLoop").onclick = async () => {
  const base = { feed_id: $("#apFeed").value, estilo: $("#apEstilo").value, forcar: $("#apForcar").checked };
  if (!base.feed_id) return toast("Crie um Feed do seu nicho primeiro (💡 Ideação → Meus Feeds).", 5000);
  modal("🎬 Como fazer o vídeo de hoje?"); $("#modal").classList.add("semBarra");
  $("#mMsg").textContent = "Carregando as opções…";
  let ms = [], vs = [], aj = {}, st = {};
  try { [ms, vs, aj, st] = await Promise.all([api("/api/ajustes/modelos").catch(() => []), api("/api/ajustes/vozes").catch(() => []), api("/api/ajustes").catch(() => ({})), api("/api/autopilot").catch(() => ({}))]); } catch (e) { }
  const vozPadrao = st.voz || aj.voz || "auto";
  const grupos = {}; vs.forEach((v) => (grupos[v.grupo || "Outras"] = grupos[v.grupo || "Outras"] || []).push(v));
  const optVoz = Object.entries(grupos).map(([g, l]) => `<optgroup label="${esc(g)}">${l.map((v) => `<option value="${esc(v.id)}" ${v.id === vozPadrao ? "selected" : ""}>${esc(v.nome)}</option>`).join("")}</optgroup>`).join("");
  const modPadrao = aj.modelo_ollama || "";
  const optMod = ms.map((m) => `<option value="${esc(m.nome)}" ${m.nome === modPadrao ? "selected" : ""}>${esc(m.nome)}${m.gb ? ` (${m.gb} GB)` : ""}${m.nuvem ? " ☁" : ""}</option>`).join("")
    || `<option value="${esc(modPadrao)}">${esc(modPadrao || "padrão")}</option>`;
  const q = (id) => document.getElementById(id);
  $("#mMsg").innerHTML = `
    <div class="row"><label>IA do roteiro</label><select id="apmIA" style="flex:1"><option value="ollama">Ollama (grátis, no seu PC)</option><option value="claude">🧠 Claude (chave em Ajustes ou Claude instalado)</option></select></div>
    <div class="row" id="apmModRow"><label>Modelo Ollama</label><select id="apmModelo" style="flex:1">${optMod}</select></div>
    <div class="row"><label>Voz</label><select id="apmVoz" style="flex:1">${optVoz}</select></div>
    <div class="row"><label>Duração (min)</label><input type="number" id="apmDur" min="0.5" step="0.5" style="width:90px" placeholder="auto" /></div>
    <p class="help" id="apmAviso"></p>`;
  const aviso = () => { q("apmAviso").textContent = String(q("apmVoz").value).startsWith("fish:") ? "⚠ Fish Audio é pago por crédito. Se acabou o crédito, o vídeo falha: escolha uma voz Microsoft (grátis)." : ""; };
  q("apmVoz").onchange = aviso; aviso();
  q("apmIA").onchange = () => q("apmModRow").classList.toggle("hidden", q("apmIA").value === "claude");
  mbtn("🎬 Fazer o vídeo", async () => {
    const body = { ...base, voz: q("apmVoz").value, modelo: q("apmModelo").value, claude_roteiro: q("apmIA").value === "claude" };
    const d = parseFloat(q("apmDur").value); if (d > 0) body.duracao = Math.round(d * 60);
    closeModal(); apFazerLoop(body);
  }, "go");
  mbtn("Cancelar", closeModal);
});
async function apFazerLoop(body) {
  let r; try { r = await jpost("/api/autopilot/loop", body); }
  catch (e) { return toast("❌ " + errTxt(e), 6000); }
  acompanhar(r.job, "🤖 Fazendo o vídeo de hoje…", async (res, fechado) => {
    if (fechado) return;
    try { apRender(await api("/api/autopilot")); } catch (e) { }
    if (res && res.pid) {
      $("#mTitle").textContent = res.rendered ? "✅ Vídeo do dia pronto!" : "⚠ Quase pronto: abra e clique em ▶ Gerar vídeo final";
      $("#mMsg").innerHTML = `<b>${esc((res.ideia || {}).titulo || (res.ideia || {}).tema || "")}</b>\nInspirado em: ${esc(res.assunto_de || "")}\nFeed: ${esc(res.feed || "")}`;
      mbtn("✏ Abrir no editor", () => { closeModal(); openProject(res.pid); }, "go");
      mbtn("📋 Kit de publicação", () => apAbrirKit(res.pid));
      mbtn("📂 Abrir pasta", () => api(`/api/open/${res.pid}?what=folder`, { method: "POST" }));
      mbtn("Fechar", closeModal);
    } else { toast("✅ Pronto", 4000); }
  });
}
$("#apCsvBtn") && ($("#apCsvBtn").onclick = async () => {
  const f = $("#apCsv").files[0];
  if (!f) return toast("Escolha o arquivo CSV do YouTube Studio.", 4000);
  $("#apCsvStatus").textContent = "Importando…";
  const fd = new FormData(); fd.append("file", f);
  let r; try { r = await api("/api/autopilot/csv", { method: "POST", body: fd }); }
  catch (e) { $("#apCsvStatus").textContent = ""; return toast("❌ " + errTxt(e), 6000); }
  $("#apCsvStatus").innerHTML = `✅ CSV importado: <b>${r.n}</b> vídeos com impressões/CTR/retenção. Agora o “🔍 Por quê?” usa esses dados.`;
  try { apRender(await api("/api/autopilot")); } catch (e) { }
});
$("#tnAutopilot") && ($("#tnAutopilot").onclick = () => openAutopilot());
function navMarca(st) {
  const k = st.sel + "|" + (st.pid || "") + "|" + (st.sub || "");
  if (k === NAV.cur) return;
  NAV.cur = k;
  if (NAV.restaurando) return;
  const u = urlDe(st) || undefined;
  try { if (!history.state || !history.state.nav) history.replaceState({ nav: st }, "", u); else { history.pushState({ nav: st }, "", u); NAV.passos++; } } catch (e) { }
  NAV.hash = location.hash;
}
function navVoltar(senao) { if (NAV.passos > 0) history.back(); else senao(); }
(function () {
  const _show = showOnly;
  showOnly = function (sel) { const ok = _show(sel); if (ok) navMarca({ sel, sub: sel === "#ideias" && typeof ID !== "undefined" ? ID.aba : "" }); return ok; };
  const _proj = openProject;
  openProject = async function (pid) { const r = await _proj(pid); if (S.pid === pid && !$("#editor").classList.contains("hidden")) navMarca({ sel: "#editor", pid }); return r; };
  const _cmp = openComparar;
  openComparar = async function (pid, from) { const r = await _cmp(pid, from); if (!$("#comparar").classList.contains("hidden")) navMarca({ sel: "#comparar", pid, from: CMP.from }); return r; };
  const _home = loadHome;
  loadHome = async function () { navMarca({ sel: "#home" }); return _home(); };
  const _ped = openPedido;
  openPedido = async function (estiloId, from) { navMarca({ sel: "#pedido", pid: typeof estiloId === "string" ? estiloId : "", from: from || "home" }); return _ped(estiloId, from); };
})();
// a tela que abriu junto com a página (antes destes wrappers existirem) também ganha o endereço legível
setTimeout(() => { if (NAV.cur) return; const s = [...NEW_SECS, "#home"].find((x) => $(x) && !$(x).classList.contains("hidden")); if (s) navMarca({ sel: s, sub: s === "#ideias" && typeof ID !== "undefined" ? ID.aba : "" }); }, 600);
window.addEventListener("popstate", async (ev) => {
  NAV.hash = location.hash;
  const st = ev.state && ev.state.nav;
  if (!st) return;
  NAV.passos = Math.max(0, NAV.passos - 1);
  const saindoEditor = !$("#editor").classList.contains("hidden");
  if (saindoEditor && S.dirty && !(st.sel === "#editor" && st.pid === S.pid)) {
    if (!confirm("Tem mudanças não salvas. Sair mesmo assim?")) { try { history.pushState({ nav: { sel: "#editor", pid: S.pid } }, ""); NAV.passos++; } catch (e) { } return; }
    S.dirty = false;
  }
  NAV.restaurando = true;
  try {
    if (st.sel === "#editor") {
      if (S.pid === st.pid && S.edit) { hideNew(); cmpHide(); ["#home", "#pedido"].forEach((s) => $(s).classList.add("hidden")); $("#editor").classList.remove("hidden"); TELA.atual = "Editor"; setTimeout(fitStage, 30); NAV.cur = "#editor|" + st.pid + "|"; }
      else await openProject(st.pid);
    } else if (st.sel === "#comparar") await openComparar(st.pid, st.from);
    else if (st.sel === "#pedido") await openPedido(st.pid || null, st.from);
    else if (st.sel === "#ideias") await openIdeias(st.sub || undefined);
    else if (NAV_ABRE[st.sel]) await NAV_ABRE[st.sel]();
    else showOnly(st.sel);
  } catch (e) { console.error(e); }
  NAV.restaurando = false;
});
// botões "Voltar" passam a usar o histórico (tela anterior); sem histórico, fazem o que faziam antes
$("#btnBack").onclick = () => { if (S.dirty && !confirm("Tem mudanças não salvas. Sair mesmo assim?")) return; S.dirty = false; navVoltar(loadHome); };
$("#cmpBack").onclick = () => navVoltar(cmpBack);
$("#btnPedidoBack").onclick = () => navVoltar(() => (PED.from === "galeria" ? openGaleria() : loadHome()));

// ======================================================= 🔥 BOMBANDO AGORA (vídeos faceless em alta — /api/emalta, cache .cache/bombando.json)
NEW_SECS.push("#emalta");
TELA_NOME["#emalta"] = "Bombando";
const EMA = { d: null, idioma: "Todos", fmt: "Todos", nicho: "Todos" };
try { Object.assign(EMA, JSON.parse(localStorage.getItem("emalta_filtros") || "{}")); } catch (e) { }
const emIdade = (h) => (h < 1 ? "agora" : h < 48 ? Math.round(h) + " h" : Math.round(h / 24) + " dias");
async function openEmAlta() {
  if (!showOnly("#emalta")) return;
  if (!EMA.d) {
    $("#emLista").innerHTML = '<div class="card">Carregando…</div>';
    try { EMA.d = await api("/api/emalta"); } catch (e) { $("#emLista").innerHTML = `<div class="card">❌ ${esc(errTxt(e))}</div>`; return; }
  }
  renderEmAlta();
}
function renderEmAlta() {
  const d = EMA.d || { itens: [] }, all = d.itens || [];
  try { localStorage.setItem("emalta_filtros", JSON.stringify({ idioma: EMA.idioma, fmt: EMA.fmt, nicho: EMA.nicho })); } catch (e) { }
  $("#emMedido").innerHTML = d.atualizado ? esc(`Última busca: ${d.atualizado} · ${all.length} vídeos`) + velhoTxt(d.atualizado) : "";
  const chips = (arr, cur, key) => arr.map(([v, l]) => `<button class="chip ${cur === v ? "on" : ""}" data-${key}="${esc(v)}">${l}</button>`).join("");
  const nichos = ["Todos", ...(d.nichos || [...new Set(all.map((x) => x.nicho))])];
  $("#emFiltros").innerHTML = `<div class="origbar">${chips([["Todos", "🌎 Todos"], ["EN", "🇺🇸 EN"], ["ES", "🇪🇸 ES"], ["PT", "🇧🇷 PT"]], EMA.idioma, "emi")}</div>
    <div class="origbar">${chips([["Todos", "🗂 Longos e shorts"], ["longo", "🎬 Longos"], ["short", "📱 Shorts"]], EMA.fmt, "emf")}</div>
    <div class="origbar">${chips(nichos.map((n) => [n, n === "Todos" ? "Todos os nichos" : n]), EMA.nicho, "emn")}</div>`;
  $("#emFiltros").querySelectorAll("[data-emi]").forEach((b) => (b.onclick = () => { EMA.idioma = b.dataset.emi; renderEmAlta(); }));
  $("#emFiltros").querySelectorAll("[data-emf]").forEach((b) => (b.onclick = () => { EMA.fmt = b.dataset.emf; renderEmAlta(); }));
  $("#emFiltros").querySelectorAll("[data-emn]").forEach((b) => (b.onclick = () => { EMA.nicho = b.dataset.emn; renderEmAlta(); }));
  const L = all.filter((x) => (EMA.idioma === "Todos" || x.idioma === EMA.idioma) && (EMA.fmt === "Todos" || x.formato === EMA.fmt) && (EMA.nicho === "Todos" || x.nicho === EMA.nicho)).slice(0, 120);
  if (!all.length) { $("#emLista").innerHTML = `<div class="card">Ainda não tem dados. Clique em <b>🔄 Atualizar</b> — a busca roda em segundo plano (uns 5-8 min) e a lista aparece aqui.</div>`; return; }
  $("#emLista").innerHTML = L.length ? L.map((x, k) => `<div class="emCard">
      <a class="emTh ${x.formato === "short" ? "vert" : ""}" href="${esc(x.url)}" target="_blank" rel="noopener" style="background-image:url('${esc(x.thumb)}')"><span class="emRank">${k + 1}º</span>${x.duracao ? `<span class="emDur">${fmt(x.duracao)}</span>` : ""}</a>
      <div class="emTx"><b title="${esc(x.titulo)}">${esc(x.titulo)}</b>
        <div class="emCanal">${x.canal_url ? `<a href="${esc(x.canal_url)}" target="_blank" rel="noopener">${esc(x.canal || "canal")}</a>` : esc(x.canal || "—")}</div>
        <div class="emNums"><span class="bbVph" title="Views por hora desde que saiu">🔥 ${Number(x.vph).toLocaleString("pt-BR")}/h</span><span>👁 ${fmtNum(x.views)}</span><span>⏱ ${emIdade(x.horas)}</span><span class="tag">${esc(x.idioma)}</span><span class="tag">${esc(x.nicho)}</span></div>
        <div class="emA"><a class="btn" href="${esc(x.url)}" target="_blank" rel="noopener">▶ Assistir</a><button class="btn go" data-emcop="${k}">🎨 Copiar este estilo</button></div></div></div>`).join("")
    : '<div class="card">Nenhum vídeo com esses filtros.</div>';
  $("#emLista").querySelectorAll("[data-emcop]").forEach((b) => (b.onclick = () => {
    const x = L[+b.dataset.emcop]; openCopiar();
    ["#crUrl", "#cVideo"].forEach((k) => $(k) && ($(k).value = x.url));
    if ($("#cCanalUrl") && x.canal_url) $("#cCanalUrl").value = x.canal_url;
    toast("Link colado no Copiar estilo — escolha como copiar", 3500);
  }));
}
$("#emAtualizar").onclick = async () => {
  let r; try { r = await jpost("/api/emalta/atualizar", {}); } catch (e) { return toast("❌ " + errTxt(e)); }
  acompanhar(r.job, "🔥 Buscando vídeos em alta…", async (res, fechado) => { EMA.d = null; if (!fechado) closeModal(); toast(`✅ ${res && res.videos != null ? res.videos + " vídeos" : "Lista"} atualizada`, 4000); if (!$("#emalta").classList.contains("hidden")) openEmAlta(); });
};
$("#tnEmAlta").onclick = openEmAlta;
Object.assign(TIPO_ICO, { emalta: "🔥" }); Object.assign(TIPO_NOME, { emalta: "Bombando agora" });

// ======================================================= 💡 IDEIAS em vários idiomas (PT / EN / ES)
const ID_FLAG = { "pt-BR": "🇧🇷", "en-US": "🇺🇸", "es-MX": "🇲🇽" };
const ID_VOZ = { "pt-BR": "edge:pt-BR-ThalitaMultilingualNeural", "en-US": "edge:en-US-GuyNeural", "es-MX": "edge:es-MX-JorgeNeural" };
ID.idioma = "pt-BR";
try { ID.idioma = localStorage.getItem("ideias_idioma") || "pt-BR"; } catch (e) { }
function renderIdIdioma() {
  $("#idIdioma").innerHTML = '<span class="mu">Idioma das ideias:</span> ' + [["pt-BR", "🇧🇷 PT"], ["en-US", "🇺🇸 EN"], ["es-MX", "🇲🇽 ES"]]
    .map(([v, l]) => `<button class="chip ${ID.idioma === v ? "on" : ""}" data-idl="${v}">${l}</button>`).join("");
  $("#idIdioma").querySelectorAll("[data-idl]").forEach((b) => (b.onclick = () => { ID.idioma = b.dataset.idl; try { localStorage.setItem("ideias_idioma", ID.idioma); } catch (e) { } renderIdIdioma(); toast("Ideias, títulos e resumos agora em " + b.textContent.trim()); }));
}
renderIdIdioma();
async function fazerVideoIdeia(x) {
  if (!x) return;
  const idi = x.idioma || ID.idioma || "pt-BR";
  try {
    const aj = await api("/api/ajustes");
    if (aj.idioma !== idi) {
      const vozOk = String(aj.voz || "").includes(idi);
      await jpost("/api/ajustes", vozOk ? { idioma: idi } : { idioma: idi, voz: ID_VOZ[idi] });
      toast(`${ID_FLAG[idi]} Roteiro e voz agora em ${idi} (dá pra trocar em ⚙ Ajustes)`, 5000);
    }
  } catch (e) { toast("❌ Não consegui trocar o idioma: " + errTxt(e), 5000); }
  await openVimg();
  try { setModoVi("tema"); $("#viTema").value = x.titulo || x.ideia; if (x.titulo) $("#viTitulo").value = x.titulo; } catch (e) { }
}

// ======================================================= PRÉVIA AO PASSAR O MOUSE (Estilos prontos + Estilos bombando)
// Mouse em cima da miniatura → toca o vídeo-exemplo mudo, em loop, a partir de ~3 s; tirou o mouse → volta a miniatura.
// Toque (celular): 1º toque mostra a prévia, 2º toque faz a ação normal da miniatura.
const HV = { el: null, th: null, toqueEm: null };
function hvUrlDe(th) {
  const card = th.closest("[data-gid]");
  if (card) { const e = (GAL.list || []).find((x) => x.id === card.dataset.gid); return e && e.video_url; }
  const pid = th.dataset.bed;
  if (pid) { const e = (PED.estilos || []).find((x) => x.pid === pid && x.video_url); return e && e.video_url; }
  const est = th.closest("[data-vurl]");
  if (est) return est.dataset.vurl;
  return null;
}
function hvParar() {
  if (HV.el) { try { HV.el.pause(); } catch (e) { } HV.el.removeAttribute("src"); HV.el.remove(); }
  HV.el = null; HV.th = null;
}
function hvTocar(th) {
  if (HV.th === th || th.querySelector(".apPrev")) return;
  hvParar();
  const url = hvUrlDe(th); if (!url) return;
  const v = document.createElement("video");
  v.className = "hvPrev"; v.muted = true; v.loop = true; v.playsInline = true; v.preload = "auto";
  v.setAttribute("muted", ""); v.setAttribute("playsinline", "");
  v.src = url + (url.includes("#") ? "" : "#t=3");
  v.addEventListener("loadedmetadata", () => { if (v.duration > 6 && v.currentTime < 2.5) v.currentTime = 3; });
  v.addEventListener("ended", () => { v.currentTime = v.duration > 6 ? 3 : 0; v.play().catch(() => { }); });
  if (getComputedStyle(th).position === "static") th.style.position = "relative";
  th.appendChild(v); HV.el = v; HV.th = th;
  v.play().catch(() => { });
}
const HV_SEL = "#galGrid .gal .th, #bbLista .bbTh[data-bed], #estGrid .est .th";
document.addEventListener("mouseover", (e) => {
  if (HV.toqueEm && Date.now() - HV.toqueEm < 800) return;   // mouseover sintético do toque
  const th = e.target.closest && e.target.closest(HV_SEL);
  if (th) hvTocar(th); else if (HV.th && !HV.th.contains(e.target)) hvParar();
});
document.addEventListener("mouseout", (e) => { if (HV.th && !HV.th.contains(e.relatedTarget)) hvParar(); });
document.addEventListener("touchstart", (e) => {
  HV.toqueEm = Date.now();
  const th = e.target.closest && e.target.closest(HV_SEL);
  if (!th) { if (HV.th) hvParar(); return; }
}, { passive: true });
document.addEventListener("click", (e) => {
  if (!HV.toqueEm || Date.now() - HV.toqueEm > 800) return;   // só no toque
  const th = e.target.closest && e.target.closest(HV_SEL);
  if (th && HV.th !== th && hvUrlDe(th)) { e.preventDefault(); e.stopPropagation(); hvTocar(th); }   // 1º toque = prévia
}, true);

// ======================================================= ▶ PRÉVIAS TOCAM SOZINHAS (mudas, em loop, só as visíveis)
const AP = { max: innerWidth < 700 ? 3 : 8, ativos: new Set(), vis: new Set(), vistos: new WeakSet() };
const AP_SEL = "video.apV, #galGrid .gal .th, #estGrid .est .th";
function apLigar(el) {
  if (el.tagName === "VIDEO") {
    if (el.preload === "none") el.preload = "auto";
    el.play().catch(() => { });
  } else {
    const url = hvUrlDe(el); if (!url) return false;
    if (HV.th === el) hvParar();
    const v = document.createElement("video");
    v.className = "hvPrev apPrev"; v.muted = true; v.loop = true; v.playsInline = true; v.preload = "auto";
    v.setAttribute("muted", ""); v.setAttribute("playsinline", "");
    v.src = url + (url.includes("#") ? "" : "#t=3");
    v.addEventListener("loadedmetadata", () => { if (v.duration > 6 && v.currentTime < 2.5) v.currentTime = 3; });
    v.addEventListener("playing", () => v.classList.add("ok"), { once: true });   // miniatura fica por baixo até o 1º quadro: sem tela preta
    if (getComputedStyle(el).position === "static") el.style.position = "relative";
    el.appendChild(v); v.play().catch(() => { });
  }
  AP.ativos.add(el); return true;
}
function apDesligar(el) {
  if (el.tagName === "VIDEO") { try { el.pause(); } catch (e) { } }
  else el.querySelectorAll(".apPrev").forEach((v) => { try { v.pause(); } catch (e) { } v.removeAttribute("src"); v.load(); v.remove(); });
  AP.ativos.delete(el);
}
function apEncher() {
  for (const s of [AP.ativos, AP.vis]) for (const el of [...s]) if (!el.isConnected) { s.delete(el); if (s === AP.ativos) apDesligar(el); }
  if (document.hidden) return;
  let atraso = 0;
  for (const el of AP.vis) {
    if (AP.ativos.size >= AP.max) break;
    if (AP.ativos.has(el)) continue;
    AP.ativos.add(el);   // reserva a vaga; liga em escadinha pra não decodificar tudo no mesmo instante
    setTimeout(() => { if (AP.ativos.has(el) && el.isConnected && !document.hidden && !apLigar(el)) AP.ativos.delete(el); }, atraso);
    atraso += 140;
  }
}
const AP_IO = "IntersectionObserver" in window ? new IntersectionObserver((ents) => {
  ents.forEach((en) => {
    if (en.isIntersecting) AP.vis.add(en.target);
    else { AP.vis.delete(en.target); if (AP.ativos.has(en.target)) apDesligar(en.target); }
  });
  apEncher();
}, { threshold: 0.35, rootMargin: "160px 0px" }) : null;
function apVarrer() {
  if (!AP_IO) return;
  document.querySelectorAll(AP_SEL).forEach((el) => { if (!AP.vistos.has(el)) { AP.vistos.add(el); AP_IO.observe(el); } });
  apEncher();
}
let apTimer = 0;
new MutationObserver(() => { clearTimeout(apTimer); apTimer = setTimeout(apVarrer, 150); }).observe(document.body, { childList: true, subtree: true });
document.addEventListener("visibilitychange", () => {
  if (document.hidden) [...AP.ativos].forEach(apDesligar); else apEncher();
});
apVarrer();

// ======================================================= 💡 CAMPO VAZIO = A IA ESCOLHE (tudo opcional)
const nichoSalvo = () => { try { return localStorage.getItem("ia_nicho") || ""; } catch (e) { return ""; } };
async function ideiaAuto(sel, opts = {}) {
  const el = $(sel); if (!el || el.value.trim()) return true;
  toast("💡 Sem tema? A IA está escolhendo uma ideia pra você…", 90000);
  try {
    const r = await jpost("/api/skills-ia/ideias", { skill: opts.skill || "", formato: opts.formato || "short", ref: opts.ref || "", nicho: nichoSalvo() });
    const x = r.ideias[Math.floor(Math.random() * Math.min(3, r.ideias.length))];
    el.value = opts.linha ? skiLinha(x) : x.titulo; el.dispatchEvent(new Event("input"));
    toast(`💡 A IA escolheu: “${x.titulo}”`, 5000); return true;
  } catch (e) { toast("❌ " + errTxt(e), 6000); return false; }
}
// marca d'água deste vídeo: repete a última usada (dá pra apagar/trocar), vale só pro vídeo que está sendo criado
function marcaPre(sel) { /* nada vem preenchido: só escreve o que você digitar */ }
function marcaVal(sel) { const v = ($(sel).value || "").trim().slice(0, 60); try { localStorage.setItem("marca_ultima", v); } catch (e) { } return v; }
function canalAuto(sel) { /* sem nome provisório: vazio = nada escrito no vídeo */ }

// ======================================================= 💡 SUGERIR IDEIAS (botão em todo campo de tema)
async function sugerirIdeias(btn, inputSel, opts = {}) {
  const input = $(inputSel);
  if (!input) return;
  const oldTxt = btn.textContent;
  btn.disabled = true; btn.textContent = "⏳ Pensando…";
  try {
    const body = {
      contexto: input.value.trim() || opts.contexto || "",
      formato: opts.formato || "longo",
      nicho: opts.nicho || nichoSalvo(),
      estilo: opts.estilo || ""
    };
    const r = await jpost("/api/sugerir-ideias", body);
    const ideias = r.ideias || [];
    if (!ideias.length) { toast("A IA não devolveu ideias. Tente de novo."); return; }
    input.value = ideias[0]; input.dispatchEvent(new Event("input")); toast("💡 Ideia colocada! Não gostou? Escolha outra na lista.", 4000);
    // mostra dropdown
    let drop = btn.parentElement.querySelector(".ideiaDrop");
    if (!drop) { drop = document.createElement("div"); drop.className = "ideiaDrop"; btn.parentElement.appendChild(drop); }
    drop.innerHTML = `<div class="ideiaHead">💡 Ou escolha outra <button class="btn mini ideiaFechar">✕</button></div>` +
      ideias.slice(1).map((id) => `<button class="ideiaOp">${esc(id)}</button>`).join("") +
      `<button class="btn mini ideiaRefresh">🔄 Mais ideias</button>`;
    drop.classList.remove("hidden");
    drop.querySelector(".ideiaFechar").onclick = () => drop.classList.add("hidden");
    drop.querySelectorAll(".ideiaOp").forEach((b) => (b.onclick = () => {
      input.value = b.textContent; drop.classList.add("hidden"); input.focus();
      toast("✅ Ideia selecionada!");
    }));
    drop.querySelector(".ideiaRefresh").onclick = () => sugerirIdeias(btn, inputSel, opts);
  } catch (e) {
    toast("❌ " + errTxt(e), 5000);
  } finally {
    btn.disabled = false; btn.textContent = oldTxt;
  }
}

// adicionar botões de sugerir em cada campo de tema
document.addEventListener("DOMContentLoaded", () => {
  const campos = [
    { input: "#pTema", formato: () => (PED.fmt === "short" ? "short" : "longo"), estilo: () => ((PED.estilos || []).find((x) => x.id === PED.sel) || {}).nome || "", label: "💡 Sugerir ideia" },
    { input: "#viTema", formato: () => "longo", estilo: () => VI.estilo, label: "💡 Sugerir ideia" },
    { input: "#shTema", formato: () => "short", estilo: () => SH.estilo, label: "💡 Sugerir ideia" },
    { input: "#cTema", formato: () => COP.fmt, label: "💡 Sugerir ideia" },
    { input: "#skTema", formato: () => (SK.fmt === "9:16" ? "short" : "longo"), label: "💡 Sugerir ideia" },
    { input: "#rtTema", formato: () => "longo", label: "💡 Sugerir ideia" },
  ];
  campos.forEach(({ input: sel, formato, estilo, label }) => {
    const el = $(sel);
    if (!el) return;
    const row = el.closest(".row");
    if (!row) return;
    const btn = document.createElement("button");
    btn.type = "button"; btn.className = "btn sugerirBtn"; btn.textContent = label;
    btn.onclick = () => sugerirIdeias(btn, sel, {
      formato: typeof formato === "function" ? formato() : formato,
      estilo: typeof estilo === "function" ? estilo() : ""
    });
    row.appendChild(btn);
  });
});

// ======================================================= AUTO-SUGERIR NOME NO COPIAR ESTILO
document.addEventListener("DOMContentLoaded", () => {
  const nomeInput = $("#crNome");
  const urlInput = $("#crUrl");
  if (!nomeInput || !urlInput) return;
  
  // botão sugerir nome
  const row = nomeInput.closest(".row");
  if (row) {
    const btn = document.createElement("button");
    btn.type = "button"; btn.className = "btn sugerirBtn"; btn.textContent = "🤖 Sugerir nome";
    btn.onclick = async () => {
      const url = urlInput.value.trim();
      if (CR.fonte === "pc") {   // QA: vídeo do PC → nome a partir do arquivo (antes pedia link e não fazia nada)
        if (!CR.arq) return erroCampo("#crArq", "Escolha o vídeo primeiro (e espere aparecer ✅)");
        nomeInput.value = nomeDoArquivo(CR.arq.nome); toast("✅ Nome sugerido: " + nomeInput.value + " (pode mudar)"); return;
      }
      if (!urlOk(url)) { toast("Cole o link do vídeo primeiro"); return; }
      btn.disabled = true; btn.textContent = "⏳…";
      try {
        const r = await jpost("/api/sugerir-nome-estilo", { url });
        if (r.nome) { nomeInput.value = r.nome; toast("✅ Nome sugerido: " + r.nome); }
        else toast("Não consegui sugerir. Escreva o nome.");
      } catch (e) { toast("❌ " + errTxt(e)); }
      btn.disabled = false; btn.textContent = "🤖 Sugerir nome";
    };
    row.appendChild(btn);
  }

  // ao colar link, se nome vazio, sugere automaticamente
  urlInput.addEventListener("paste", () => {
    setTimeout(async () => {
      const url = urlInput.value.trim();
      if (!nomeInput.value.trim() && urlOk(url)) {
        try {
          const r = await jpost("/api/sugerir-nome-estilo", { url });
          if (r.nome && !nomeInput.value.trim()) { nomeInput.value = r.nome; toast("💡 Nome sugerido automaticamente: " + r.nome, 3000); }
        } catch (e) { /* silencioso */ }
      }
    }, 300);
  });
});

// ======================================================= BOTÕES RÁPIDOS: "Usar ideia do Placar" nos campos de tema
document.addEventListener("DOMContentLoaded", () => {
  const campos = ["#pTema", "#viTema", "#shTema", "#cTema"];
  campos.forEach((sel) => {
    const el = $(sel);
    if (!el) return;
    const row = el.closest(".row");
    if (!row) return;
    const btn = document.createElement("button");
    btn.type = "button"; btn.className = "btn mini"; btn.textContent = "📋 Do placar";
    btn.title = "Usar uma ideia que você já avaliou no Placar";
    btn.style.marginLeft = "6px";
    btn.onclick = async () => {
      btn.disabled = true;
      try {
        const d = await api("/api/ideias/placar");
        const boas = (d.ideias || []).filter((x) => x.nota >= 6 && x.status === "ideia");
        if (!boas.length) { toast("Nenhuma ideia boa no Placar. Vá em 💡 Ideias → 🏆 Placar e avalie algumas primeiro.", 5000); return; }
        let drop = btn.parentElement.querySelector(".ideiaDrop");
        if (!drop) { drop = document.createElement("div"); drop.className = "ideiaDrop"; btn.parentElement.appendChild(drop); }
        drop.innerHTML = `<div class="ideiaHead">📋 Ideias do Placar (nota 6+) <button class="btn mini ideiaFechar">✕</button></div>` +
          boas.slice(0, 8).map((x) => `<button class="ideiaOp" title="Nota ${x.nota}">${esc(x.titulo || x.ideia)} <small class="mu">(${Number(x.nota).toFixed(1)})</small></button>`).join("");
        drop.classList.remove("hidden");
        drop.querySelector(".ideiaFechar").onclick = () => drop.classList.add("hidden");
        drop.querySelectorAll(".ideiaOp").forEach((b) => (b.onclick = () => {
          el.value = b.textContent.replace(/\s*\(\d.*$/, "").trim();
          drop.classList.add("hidden"); el.focus(); toast("✅ Ideia colada!");
        }));
      } catch (e) { toast("❌ " + errTxt(e)); }
      btn.disabled = false;
    };
    row.appendChild(btn);
  });
});

// ======================================================= 🆕 24/10: aviso ao terminar · diagnóstico · celular · receitas · roteiro grátis + estimativa · pedir ajuste
// ---- 🔔 trabalho terminou → som + notificação do Windows + título piscando (funciona com a aba em segundo plano: a fila já é consultada sozinha)
const AVISO = { vivos: null, titulo: document.title, pisca: null, ctx: null };
document.addEventListener("pointerdown", () => {   // o navegador só deixa tocar som depois de um clique na página
  try { AVISO.ctx = AVISO.ctx || new (window.AudioContext || window.webkitAudioContext)(); if (AVISO.ctx.state === "suspended") AVISO.ctx.resume(); } catch (e) { }
}, { capture: true });
function avisoSom(ok) {
  try {
    const c = AVISO.ctx || (AVISO.ctx = new (window.AudioContext || window.webkitAudioContext)());
    if (c.state === "suspended") c.resume();
    const t = c.currentTime + 0.02;
    (ok ? [660, 880, 1320] : [440, 311]).forEach((f, i) => {
      const o = c.createOscillator(), g = c.createGain(), t0 = t + i * 0.15;
      o.type = "sine"; o.frequency.value = f;
      g.gain.setValueAtTime(0.0001, t0); g.gain.exponentialRampToValueAtTime(0.22, t0 + 0.02); g.gain.exponentialRampToValueAtTime(0.0001, t0 + 0.24);
      o.connect(g); g.connect(c.destination); o.start(t0); o.stop(t0 + 0.26);
    });
  } catch (e) { }
}
function avisoPiscar(txt) {
  clearInterval(AVISO.pisca); let on = false;
  AVISO.pisca = setInterval(() => { on = !on; document.title = on ? txt : AVISO.titulo; }, 1000);
  const parar = () => { if (document.hidden) return; clearInterval(AVISO.pisca); AVISO.pisca = null; document.title = AVISO.titulo; window.removeEventListener("focus", parar); document.removeEventListener("visibilitychange", parar); };
  window.addEventListener("focus", parar); document.addEventListener("visibilitychange", parar);
}
function avisoFila(lista) {
  const vivos = new Set(lista.filter((j) => !j.done).map((j) => j.id));
  if (AVISO.vivos) lista.forEach((j) => { if (j.done && AVISO.vivos.has(j.id)) avisoFim(j); });
  AVISO.vivos = vivos;
}
function avisoFim(j) {
  if (j.status === "cancelado") return;
  const ok = j.status === "pronto", nome = String(j.titulo || TIPO_NOME[j.tipo] || "Trabalho").slice(0, 90);
  avisoSom(ok);
  if (document.hidden || !document.hasFocus()) {
    avisoPiscar(ok ? "✅ Pronto! · Estúdio" : "❌ Deu erro · Estúdio");
    try {
      if ("Notification" in window && Notification.permission === "granted") {
        const n = new Notification(ok ? "✅ Pronto no Estúdio de Vídeos" : "❌ Deu erro no Estúdio de Vídeos", { body: nome, tag: "estudio-" + j.id });
        n.onclick = () => { window.focus(); n.close(); loadHome(); };
      }
    } catch (e) { }
  } else toast((ok ? "✅ Pronto: " : "❌ Deu erro: ") + nome + " — veja em 📂 Meus vídeos", 6000);
}
function avisoBtns() {
  const st = !("Notification" in window) || !window.isSecureContext ? "nao" : Notification.permission;
  document.querySelectorAll("[data-aviso]").forEach((b) => {
    b.classList.toggle("hidden", b.dataset.aviso === "topo" && st !== "default");
    b.textContent = st === "granted" ? "Avisos ligados" : st === "denied" ? "Bloqueado no navegador (cadeado ao lado do endereço)" : st === "nao" ? "Só o som (aqui não dá notificação)" : b.dataset.aviso === "topo" ? "Avisar quando terminar" : "Ativar avisos";
    b.disabled = st !== "default";
  });
}
document.addEventListener("click", (ev) => {
  if (!ev.target.closest("[data-aviso]")) return;
  if (!("Notification" in window) || !window.isSecureContext) return toast("Aqui o navegador não deixa mostrar notificação — o som continua valendo.", 5000);
  Notification.requestPermission().then((p) => {
    avisoBtns(); if (p === "granted") avisoSom(true);
    toast(p === "granted" ? "🔔 Pronto! Você vai ser avisado quando cada vídeo terminar." : "Sem permissão — o painel só vai tocar o som e piscar o título.", 5000);
  });
});
$("#ajSomTeste").onclick = () => avisoSom(true);
avisoBtns();

// ---- 🩺 diagnóstico: verde/vermelho de cada peça + como resolver
async function diagnostico(fresco) {
  modal("🩺 Diagnóstico do painel"); $("#mBar").style.width = "30%";
  $("#mMsg").innerHTML = '<div class="raBox dgBox"><div class="mu">⏳ Conferindo cada peça (uns 3 segundos)…</div></div>';
  mbtn("Fechar", closeModal);
  let d; try { d = await api("/api/diagnostico" + (fresco === true ? "?fresco=1" : "")); } catch (e) { $("#mMsg").textContent = "❌ " + errTxt(e); return; }
  if ($("#mTitle").textContent !== "🩺 Diagnóstico do painel") return;
  $("#mBar").style.width = "100%";
  const ico = { ok: "✅", aviso: "⚠️", erro: "❌" };
  $("#mMsg").innerHTML = `<div class="raBox dgBox"><div class="dgRes ${d.erros ? "bad" : "good"}">${d.erros ? `❌ ${d.erros} coisa${d.erros > 1 ? "s" : ""} pra resolver` : "✅ Tudo certo pra fazer vídeos!"}${d.avisos ? ` · ⚠️ ${d.avisos} recomendação${d.avisos > 1 ? "ões" : ""}` : ""}</div>
    <div class="dgList">${d.itens.map((x) => `<div class="dg ${x.nivel}"><span class="dgI">${ico[x.nivel] || "•"}</span><div class="dgT"><b>${esc(x.nome)}</b><small>${esc(x.detalhe)}</small>${x.dica ? `<div class="dgDica">👉 ${esc(x.dica)}</div>` : ""}</div></div>`).join("")}</div></div>`;
  $("#mBtns").innerHTML = "";
  mbtn("🔄 Conferir de novo", () => diagnostico(true));   // de novo = sem cache da voz
  if (false) mbtn("🔑 Ir pras chaves", async () => { closeModal(); await openAjustes(); const h = $("#ajChaves"); if (h) h.scrollIntoView({ behavior: "smooth" }); });
  mbtn("Fechar", closeModal, "go");
}
["#wlDiag", "#ajDiag"].forEach((s) => ($(s).onclick = diagnostico));

// ---- 📱 abrir no celular (QR code). O painel só escuta na rede se o aluno ligar (por segurança, padrão = só este PC)
async function abrirCelular() {
  modal("📱 Abrir no celular"); $("#mBar").style.width = "100%"; $("#mMsg").textContent = "⏳ …";
  let r; try { r = await api("/api/rede"); } catch (e) { $("#mMsg").textContent = "❌ " + errTxt(e); mbtn("Fechar", closeModal); return; }
  if (r.liberada) {
    $("#mMsg").innerHTML = `<div class="raBox celBox">${r.qr ? `<img class="celQr" src="/api/rede/qr.svg?${Date.now()}" alt="QR code do painel">` : ""}
      <p>Aponte a câmera do celular pro código${r.qr ? "" : " (ou digite o endereço abaixo)"}. O celular precisa estar <b>no mesmo Wi-Fi</b> deste PC.</p>
      <div class="celUrl">${esc(r.url)}</div>
      <p class="mu">Não abriu? Na 1ª vez o Windows pergunta no Firewall — clique em “Permitir” (rede privada). No celular dá pra pedir vídeo e acompanhar a fila; o ▶ Ver abre o vídeo aqui no PC.</p></div>`;
    mbtn("📋 Copiar endereço", async () => toast((await copiarTexto(r.url)) ? "✅ Endereço copiado" : "❌ Não consegui copiar"));
    mbtn("🔒 Desligar acesso pela rede", async () => { await jpost("/api/rede/liberar", { on: false }); closeModal(); toast("Ok — feche e abra o painel de novo pra valer.", 6000); });
  } else {
    $("#mMsg").innerHTML = `<div class="raBox celBox"><p>🔒 Por segurança, o painel hoje só abre <b>neste computador</b>.</p>
      <p>Pra abrir no celular ele precisa ficar visível no <b>Wi-Fi da sua casa</b>. Só ligue se o Wi-Fi for seu (nunca em Wi-Fi público): qualquer aparelho conectado nele conseguiria abrir o painel.</p>
      ${r.pedida ? `<p class="good">✅ Já está ligado. Agora <b>feche o painel e abra de novo</b> (atalho “Estúdio de Vídeos”) e clique aqui outra vez pra ver o QR code.</p>` : ""}
      <div class="celUrl mu">Endereço que vai abrir no celular: ${esc(r.url)}</div></div>`;
    if (!r.pedida) mbtn("📶 Liberar no Wi-Fi de casa", async () => { await jpost("/api/rede/liberar", { on: true }); abrirCelular(); }, "go");
    else mbtn("Desfazer", async () => { await jpost("/api/rede/liberar", { on: false }); abrirCelular(); });
  }
  mbtn("Fechar", closeModal);
}
["#wlCel", "#ajCel"].forEach((s) => ($(s).onclick = abrirCelular));

// ---- ⏱ estimativa "Fazer agora · ~22 min" (sem valor em dinheiro na tela — pedido do Yuri 07/11) (média dos RELATORIO.json daquele estilo; sem histórico → média geral)
async function estCarregar() {
  if (!EST.d || Date.now() - EST.t > 120000) {
    try { EST.d = await api("/api/estimativas"); EST.t = Date.now(); } catch (e) { return; }
    skiResumo(); pedidoResumo();
  }
}
function estTxt(chave, geral, n) {
  const d = EST.d; if (!d) return "";
  const e = d.por[chave] || d.geral[geral]; if (!e) return "";
  n = Math.max(1, n || 1);
  const m = Math.round(e.min * n);
  return ` · ~${m >= 60 ? Math.floor(m / 60) + " h " + (m % 60) + " min" : m + " min"}`;
}
function estTitulo(chave, geral) { const t = _estTitulo(chave, geral); return (t ? t + ". " : "") + "ⓘ Usa a sua assinatura do Claude (sem cobrança por vídeo)."; }
function _estTitulo(chave, geral) {
  const d = EST.d; if (!d) return "";
  const e = d.por[chave];
  return e ? `Estimativa: média de ${e.n} vídeo${e.n > 1 ? "s" : ""} já feito${e.n > 1 ? "s" : ""} neste estilo (o real pode variar)` : d.geral[geral] ? `Estimativa: média geral de ${d.geral[geral].n} vídeos feitos pelo Claude (este estilo ainda não tem histórico)` : "";
}

// ---- 📝 roteiro grátis antes de gastar: a IA do PC escreve, o aluno edita e aprova → vai como texto fixo (o Claude não reescreve)
function skiPrevVis() {
  const b = $("#iaPrevia"); if (!b || !SKI.d) return;
  const s = SKI.d.skills.find((x) => x.id === SKI.sel), txt = $("#iaTexto").value.trim();
  const lote = $("#iaLote").checked && txt.split(/\n+/).filter((x) => x.trim()).length > 1;
  const colou = txt.split(/\s+/).filter(Boolean).length >= 40;   // já colou o roteiro → pula
  b.classList.toggle("hidden", !s || s.entrada === "video" || SKI.arqs.some((a) => a.ok) || !!SKI.audio || lote || colou || !SKI.d.claude);
}
async function roteiroPrevia(o) {   // o = { tema, dur, aprovar(texto) }
  modal("📝 Roteiro grátis (IA do seu PC)"); $("#mBar").style.width = "5%";
  $("#mMsg").innerHTML = `<div class="raBox"><div class="mu">Tema: <b>${esc(o.tema.slice(0, 160))}</b> · ${fmtSeg(o.dur)}</div>
    <div id="rpStatus" class="mu">⏳ Escrevendo (uns segundos)…</div>
    <div id="rpOut" class="hidden"><label>Leia e mude o que quiser. O Claude vai usar <b>exatamente este texto</b> como narração:</label>
    <textarea id="rpTexto" rows="12"></textarea><small class="mu" id="rpConta"></small></div></div>`;
  mbtn("Fechar", closeModal);
  let r; try { r = await jpost("/api/roteiro/gerar", { tema: o.tema, duracao: o.dur, tipos: ["gancho"], motor: "pc" }); }
  catch (e) { if ($("#rpStatus")) $("#rpStatus").textContent = "❌ " + errTxt(e); return; }
  for (;;) {
    let j; try { j = await api("/api/job/" + r.job); } catch (e) { await new Promise((ok) => setTimeout(ok, 1500)); continue; }
    if (!$("#rpStatus") || $("#modal").classList.contains("hidden")) return;   // fechou a janela
    $("#mBar").style.width = Math.max(5, j.pct) + "%";
    if (!j.done) { await new Promise((ok) => setTimeout(ok, 1200)); continue; }
    $("#mBtns").innerHTML = "";
    if (j.error) { $("#rpStatus").textContent = "❌ " + erroCurto(j.error); mbtn("🔄 Tentar de novo", () => roteiroPrevia(o), "go"); mbtn("Fechar", closeModal); return; }
    $("#rpStatus").textContent = "✅ Pronto — grátis, escrito pela IA do seu PC."; $("#rpOut").classList.remove("hidden");
    const ta = $("#rpTexto"); ta.value = (j.result && j.result.roteiro) || "";
    const conta = () => { const w = ta.value.trim().split(/\s+/).filter(Boolean).length; $("#rpConta").textContent = `${w} palavras ≈ ${fmtSeg(w / 2.5)} de narração`; };
    ta.oninput = conta; conta();
    mbtn("✅ Aprovar e fazer", () => { const t = ta.value.trim(); if (t.split(/\s+/).length < 8) return toast("O roteiro ficou curto demais."); closeModal(); o.aprovar(t); }, "go");
    mbtn("🔄 Gerar outro", () => roteiroPrevia(o));
    mbtn("Fechar", closeModal);
    return;
  }
}
$("#iaPrevia").onclick = async () => {
  if (!SKI.sel) return toast("Escolha um estilo primeiro.");
  if (!(await ideiaAuto("#iaTexto", { skill: SKI.sel, ref: $("#iaRef").value.trim(), linha: true }))) return;
  roteiroPrevia({ tema: $("#iaTexto").value.trim().split("\n")[0], dur: +$("#iaDur").value || 45,
    aprovar: (t) => { $("#iaTexto").value = t; SKI.fixo = t; $("#iaLote").checked = false; skiResumo(); skiMandar(false, null, true); } });
};
$("#pPrevia").onclick = async () => {
  const e = PED.estilos.find((x) => x.id === PED.sel);
  if (!e) { $("#estGrid").scrollIntoView({ behavior: "smooth" }); return toast("Escolha um estilo na galeria (passo 2)", 4000); }
  if (!(await ideiaAuto("#pTema", { formato: PED.fmt === "short" ? "short" : "longo" }))) return;
  roteiroPrevia({ tema: $("#pTema").value.trim(), dur: PED.dur,
    aprovar: (t) => { $("#pTemRoteiro").checked = true; $("#pTemRoteiro").onchange(); $("#pRoteiro").value = t; pedidoResumo(); $("#pFazer").onclick(); } });
};
$("#pTemRoteiro").addEventListener("change", pedidoResumo);
["#iaLote", "#iaTexto"].forEach((s) => $(s).addEventListener("input", skiPrevVis));

// ---- 📒 receitas: estilo + voz + formato + duração + @ + obs com um nome (salvas no servidor: receitas.json)
async function rcCarregar(force) { if (!RC.l || force) { try { RC.l = await api("/api/receitas"); } catch (e) { RC.l = RC.l || []; } } return RC.l; }
function rcColetar(tela) {
  if (tela === "ia") return SKI.sel ? { estilo: SKI.sel, voz: $("#iaVoz").value, formato: $("#iaFmt").value, duracao: $("#iaDur").value, marca: $("#iaMarca").value.trim(),
    canal: $("#iaCanal").value.trim(), obs: $("#iaObs").value.trim(), versoes: $("#iaVersoes").value, nicho: $("#iaNicho").value.trim() } : null;
  return PED.sel ? { estilo: PED.sel, voz: $("#pVoz").value, formato: PED.fmt || "", duracao: String(PED.dur), canal: $("#pCanal").value.trim() } : null;
}
function rcSel(sel, v) {
  const el = $(sel); if (!el || v == null) return;
  if (![...el.options].some((o) => o.value === String(v))) el.insertAdjacentHTML("beforeend", `<option value="${esc(v)}">${esc(sel === "#iaDur" ? fmtSeg(+v) : v)}</option>`);
  el.value = String(v);
}
async function rcAplicar(tela, r) {
  const d = r.dados || {};
  if (tela === "ia") {
    const s = SKI.d && SKI.d.skills.find((x) => x.id === d.estilo);
    if (!s) return toast("O estilo desta receita não existe mais neste PC.", 4500);
    if (!s.instalada) return toast(`O estilo ${s.nome} não está instalado — clique em ⬇ Instalar skills.`, 5000);
    skiEscolher(s.id);
    try { await carregarVozes(); } catch (e) { }
    rcSel("#iaVoz", d.voz || ""); rcSel("#iaFmt", d.formato || ""); if (d.duracao) rcSel("#iaDur", d.duracao); if (d.versoes) rcSel("#iaVersoes", d.versoes);
    [["marca", "#iaMarca"], ["canal", "#iaCanal"], ["obs", "#iaObs"], ["nicho", "#iaNicho"]].forEach(([k, s2]) => { $(s2).value = d[k] || ""; });
    skiResumo();
  } else {
    const e = PED.estilos.find((x) => x.id === d.estilo);
    if (!e) return toast("O estilo desta receita não existe mais neste PC.", 4500);
    PED.sel = e.id; PED.fmtDe = e.id; PED.fmt = d.formato || (e.formato === "short" ? "short" : "longo");
    if (d.duracao) { PED.dur = +d.duracao; pedDurs(); }
    try { await carregarVozes(); } catch (x) { }
    rcSel("#pVoz", d.voz || ""); if (d.canal) $("#pCanal").value = d.canal;
    renderEstilos(); pedidoResumo();
  }
  toast(`📒 Receita “${r.nome}” aplicada — agora é só escrever o tema.`, 4000);
}
async function rcRender(tela) {
  const box = $(tela === "ia" ? "#iaRc" : "#pRc"); if (!box) return;
  const l = (await rcCarregar()).filter((x) => x.tela === tela);
  box.innerHTML = `<b class="rcT">📒 Receitas</b><div class="rcChips">${l.length ? l.map((r) => `<span class="rcChip"><button class="btn mini" data-rcusar="${esc(r.id)}" title="Preenche estilo, voz, formato, duração…">${esc(r.nome)}</button><button class="btn mini rcX" data-rcdel="${esc(r.id)}" title="Apagar esta receita">✖</button></span>`).join("")
    : `<span class="mu">Guarde o estilo + voz + formato + duração${tela === "ia" ? " + @ + observações" : " + canal"} com um nome e reuse com 1 clique.</span>`}</div>
    <div class="rcNovo"><input type="text" class="rcNome" maxlength="60" placeholder="Nome da receita (ex.: Reels de finanças)"><button class="btn mini go" data-rcsalvar="1">💾 Salvar o que está escolhido</button></div>`;
  box.onclick = async (ev) => {
    const u = ev.target.closest("[data-rcusar]"), dl = ev.target.closest("[data-rcdel]"), sv = ev.target.closest("[data-rcsalvar]");
    if (u) { const r = RC.l.find((x) => x.id === u.dataset.rcusar); if (r) rcAplicar(tela, r); }
    else if (dl) {
      const r = RC.l.find((x) => x.id === dl.dataset.rcdel); if (!r || !confirm(`Apagar a receita “${r.nome}”?`)) return;
      try { RC.l = await api("/api/receitas/" + encodeURIComponent(r.id), { method: "DELETE" }); } catch (e) { return toast("❌ " + errTxt(e)); }
      rcRender(tela);
    } else if (sv) {
      const dados = rcColetar(tela); if (!dados) return toast("Escolha um estilo primeiro — a receita guarda o estilo e as opções.", 4500);
      const inp = box.querySelector(".rcNome"), nome = inp.value.trim();
      if (!nome) { inp.focus(); return toast("Dê um nome pra receita (ex.: Reels de finanças).", 4000); }
      try { RC.l = await jpost("/api/receitas", { nome, tela, dados }); } catch (e) { return toast("❌ " + errTxt(e), 5000); }
      toast(`💾 Receita “${nome}” salva!`); rcRender(tela);
    }
  };
  box.querySelector(".rcNome").onkeydown = (e) => { if (e.key === "Enter") box.querySelector("[data-rcsalvar]").click(); };
}

// ---- 🔧 pedir ajuste num vídeo feito pelo Claude: grava AJUSTE-N.md na pasta e o Claude refaz só aquilo (entra na fila)
function pedirAjuste(pid) {
  const p = HOME.list.find((x) => x.id === pid); if (!p) return;
  modal("🔧 Pedir ajuste ao Claude");
  $("#mMsg").innerHTML = `<div class="raBox"><div class="mu">${esc(String(p.name).slice(0, 140))}</div>
    <label>O que você quer mudar? <small>(seja específico: “troca a cor do título pra amarelo”, “corrige o nome pra João”, “tira a música do final”)</small></label>
    <textarea id="ajuTexto" rows="5" maxlength="4000" placeholder="Escreva aqui o ajuste"></textarea>
    <small class="mu">O Claude mexe <b>só nisso</b> e mantém o resto. O vídeo de agora fica guardado na pasta <i>versoes</i>. Usa a sua assinatura do Claude (sem cobrança por vídeo), é mais rápido que fazer de novo e entra na fila como os outros — você é avisado quando terminar.</small></div>`;
  mbtn("🔧 Mandar ajuste", async () => {
    const t = $("#ajuTexto").value.trim(); if (t.length < 4) return toast("Escreva o que você quer mudar.");
    let r; try { r = await jpost("/api/ajuste/" + pid, { texto: t }); } catch (e) { return toast("❌ " + errTxt(e), 6000); }
    closeModal(); filaAtualizar(true);
    toast(r.seco ? "📝 Ajuste salvo na pasta (falta o app do Claude neste PC pra aplicar)." : `🔧 Ajuste ${r.n} na fila! Acompanhe aqui em Meus vídeos.`, 6000);
  }, "go");
  mbtn("Cancelar", closeModal);
  setTimeout(() => { const ta = $("#ajuTexto"); if (ta) ta.focus(); }, 60);
}


// ======================================================= 🧬 QUERO CLONAR UM VÍDEO (guia: link → qual ferramenta e por quê → passos)
NEW_SECS.push("#clonarguia"); TELA_NOME["#clonarguia"] = "Clonar um vídeo";
const CG = { quanto: "jeito", claude: "nao" };
function openClonarGuia() {
  if (!showOnly("#clonarguia")) return;
  api("/api/skills-ia").then((d) => { if (d && d.claude && CG.claude === "nao" && !CG._auto) { CG._auto = 1; CG.claude = "sim"; modosOn("#cgClaude", "cl", "sim"); cgRender(); } }).catch(() => { });
  cgRender();
  setTimeout(() => $("#cgUrl").focus(), 50);
}
function cgTipoLink(u) {
  if (!u) return "";
  if (/instagram\.com\/(reel|p)\//i.test(u)) return "📱 Reel do Instagram (vídeo em pé)";
  if (/tiktok\.com/i.test(u)) return "📱 TikTok (vídeo em pé)";
  if (/youtube\.com\/shorts\//i.test(u)) return "📱 YouTube Shorts (vídeo em pé)";
  if (/youtube\.com|youtu\.be/i.test(u)) return "🎬 Vídeo do YouTube (deitado)";
  return "⚠ Link não reconhecido. Use um link do YouTube, Instagram ou TikTok.";
}
function cgRender() {
  const u = $("#cgUrl").value.trim();
  $("#cgTipo").textContent = cgTipoLink(u);
  const igual = CG.quanto === "igual", temClaude = CG.claude === "sim";
  let h;
  if (igual && temClaude) {
    h = `<h3>✅ Use: <b>🧬 Clonar igualzinho</b> (com o Claude)</h3>
      <p><b>Por quê:</b> você quer as mesmas animações e efeitos. Isso só o Claude consegue: ele assiste o vídeo inteiro, escolhe a ferramenta certa e refaz cena por cena. Usa a sua assinatura do Claude (sem cobrança por vídeo) — não precisa de chave.</p>
      <ol class="cgPassos"><li>Clique em <b>▶ Começar</b> aqui embaixo (o link já vai junto).</li><li>Escreva o <b>tema</b> do seu vídeo e o nome do canal.</li><li>Clique em <b>🚀 Começar</b> na próxima tela e deixe rodando (10 a 40 min).</li><li>Quando ficar pronto, o vídeo aparece em <b>Meus vídeos</b>. Use <b>Comparar</b> pra ver lado a lado com o original.</li></ol>`;
  } else if (igual) {
    h = `<h3>✅ Use: <b>🎨 Copiar estilo (aproximado)</b> — grátis, no seu PC</h3>
      <p><b>Por quê:</b> o modo “igualzinho” precisa do Claude Pro instalado. Sem ele, o painel copia o <b>ritmo dos cortes, as cores e a legenda</b> do vídeo, sem gastar nada. Depois, se quiser o igualzinho, é só instalar o Claude e voltar aqui.</p>
      <ol class="cgPassos"><li>Clique em <b>▶ Começar</b> aqui embaixo (o link já vai junto).</li><li>Dê um nome pro estilo (ex.: “Documentário amarelo”) e clique em <b>⚡ Analisar e salvar estilo</b> (1 a 3 min).</li><li>No estilo salvo, clique em <b>🎬 Fazer um vídeo com este estilo</b> (ou <b>📱 Fazer um short com este estilo</b>), escreva o tema e clique em <b>🎬 Fazer vídeo</b>.</li><li>Confira as imagens cena por cena (dá pra ver <b>🎞 amostra de 20 s</b>) e clique em <b>▶ Fazer o vídeo</b>.</li></ol>`;
  } else {
    h = `<h3>✅ Use: <b>🎨 Copiar estilo (aproximado)</b> — grátis, no seu PC</h3>
      <p><b>Por quê:</b> pra ter o mesmo jeito (ritmo, cores, legenda) com o seu tema, não precisa de IA paga. Seu computador mede o vídeo e salva um estilo na hora, sem gastar nada.</p>
      <ol class="cgPassos"><li>Clique em <b>▶ Começar</b> aqui embaixo (o link já vai junto).</li><li>Dê um nome pro estilo e clique em <b>⚡ Analisar e salvar estilo</b> (1 a 3 min).</li><li>No estilo salvo, clique em <b>🎬 Fazer um vídeo com este estilo</b> (ou <b>📱 Fazer um short com este estilo</b>), escreva o tema e clique em <b>🎬 Fazer vídeo</b>.</li><li>Confira as imagens cena por cena (dá pra ver <b>🎞 amostra de 20 s</b>) e clique em <b>▶ Fazer o vídeo</b>.</li></ol>`;
  }
  $("#cgRec").innerHTML = h + `<div class="acts"><button class="btn big go" id="cgIr">▶ Começar</button></div>`;
  $("#cgIr").onclick = () => {
    const url = $("#cgUrl").value.trim();
    if (!url) { $("#cgUrl").focus(); return toast("Cole primeiro o link do vídeo que você quer clonar", 3500); }
    if (!urlOk(url) || !linkRede(url)) { $("#cgUrl").focus(); return toast("Esse link não parece do YouTube, Instagram ou TikTok", 4500); }
    openCopiar();
    const emPe = /em pé/.test(cgTipoLink(url));
    if (igual && temClaude) { setModoCp("fiel"); $("#cVideo").value = url; COP.fmt = emPe ? "short" : "longo"; renderCopDurs(); }
    else { setModoCp("rapido"); $("#crFonte [data-cf=link]").click(); $("#crUrl").value = url; }
  };
}
$("#cgUrl").oninput = cgRender;
$("#cgQuanto").onclick = (e) => { const b = e.target.closest("[data-cg]"); if (b) { CG.quanto = b.dataset.cg; modosOn("#cgQuanto", "cg", CG.quanto); cgRender(); } };
$("#cgClaude").onclick = (e) => { const b = e.target.closest("[data-cl]"); if (b) { CG.claude = b.dataset.cl; CG._auto = 1; modosOn("#cgClaude", "cl", CG.claude); cgRender(); } };
$("#tnClonarGuia").onclick = openClonarGuia;
$("#wlClonar").onclick = openClonarGuia;


// ======================================================= AULAS 07/11 — 1. "Bom pra" no cartão + aviso quando o tema não combina com o estilo
// Checagem por palavras-chave (instantânea, sem IA). Nunca bloqueia: só avisa e sugere 2 estilos.
function bomParaHtml(e) {
  if ((e.bom_para || []).length) return `<small class="bomPara"><b>Bom pra:</b> ${esc(e.bom_para.join(", "))}</small>`;
  return "";
}
function normTema(t) { return " " + String(t || "").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/[^a-z0-9]+/g, " ").trim() + " "; }
function pontosTema(e, t) { return (e.palavras || []).reduce((n, p) => n + (t.includes(" " + normTema(p).trim() + (p.endsWith(" ") ? " " : "")) ? 1 : 0), 0); }
function combinaEstilo(tema, lista, id) {
  const t = normTema(tema); if (t.trim().length < 5) return null;
  const atual = (lista || []).find((e) => e.id === id); if (!atual || !(atual.palavras || []).length) return null;
  if (pontosTema(atual, t) > 0) return null;
  const sug = lista.filter((e) => e.id !== id && pontosTema(e, t) > 0).sort((a, b) => pontosTema(b, t) - pontosTema(a, t)).slice(0, 2);
  return sug.length ? { atual, sug } : null;
}
function avisoCombina(box, tema, lista, id, ativo, usar) {
  const el = $(box); if (!el) return;
  const r = ativo ? combinaEstilo(tema, lista, id) : null;
  el.classList.toggle("hidden", !r);
  if (!r) { el.innerHTML = ""; return; }
  el.innerHTML = `💡 Esse tema combina mais com outro estilo. O “${esc(r.atual.nome)}” costuma ficar melhor com ${esc((r.atual.bom_para || []).slice(0, 3).join(", "))}.
    <span class="cbSug">Experimente: ${r.sug.map((e) => `<button class="btn mini" type="button" data-usar="${esc(e.id)}">🎨 Usar “${esc(e.nome)}”</button>`).join(" ")}</span>
    <small class="mu">Se preferir, pode seguir com o seu — é só um aviso.</small>`;
  el.querySelectorAll("[data-usar]").forEach((b) => (b.onclick = () => usar(b.dataset.usar)));
}
function viCombina() {
  avisoCombina("#viCombina", $("#viTema").value, VI.estilos, VI.estilo, VI.modo === "tema", (id) => { VI.estilo = id; renderViEstilos(); viResumo(); toast("🎨 Estilo trocado"); });
}
function shCombina() {
  avisoCombina("#shCombina", $("#shTema").value, SH.estilos, SH.estilo, !SH.audio && SH.modo === "tema", (id) => { SH.estilo = id; renderShEstilos(); shResumo(); toast("🎨 Estilo trocado"); });
}
(function () {
  let h1, h2;
  $("#viTema").addEventListener("input", () => { clearTimeout(h1); h1 = setTimeout(viCombina, 350); });
  $("#shTema").addEventListener("input", () => { clearTimeout(h2); h2 = setTimeout(shCombina, 350); });
})();


// ======================================================= AULAS 07/11 — 2. "Comece aqui": checklist do 1º dia (marca sozinho, dá pra esconder)
var COMECE_PASSOS = {
  ajustes: ["Deixar o PC pronto", "Abra Ajustes e clique em Testar tudo.", "Abrir Ajustes", () => openAjustes()],
  amostra: ["Ver uma amostra de 20 segundos", "Em Vídeo com imagens, escreva um tema e clique em Fazer vídeo. Quando as imagens aparecerem, clique em Ver amostra.", "Fazer minha 1ª amostra", () => openVimg()],
  video: ["Fazer o 1º vídeo completo", "Gostou da amostra? Clique em Fazer o vídeo e deixe o PC trabalhar.", "Fazer meu 1º vídeo", () => openVimg()],
  copiado: ["Copiar o estilo de um vídeo que você gostou", "Cole o link de um vídeo e o PC aprende o jeito da edição.", "Copiar um estilo", () => openCopiar()],
};
async function renderComece(d) {
  const box = $("#wlComece"); if (!box) return;
  if (!d && comeceComoNovo()) d = { passos: ["ajustes", "amostra", "video", "copiado"].map((id) => ({ id, ok: false })), escondido: false, simulado: true };
  if (!d) { try { d = await api("/api/comece"); } catch (e) { box.innerHTML = ""; return; } }
  const ver = $("#wlComeceVer"); if (ver) ver.classList.toggle("hidden", !d.escondido);
  if (d.escondido) { box.innerHTML = ""; return; }
  const feitos = d.passos.filter((p) => p.ok).length, prox = d.passos.find((p) => !p.ok);
  const lin = d.passos.map((p, i) => { const [t, dica] = COMECE_PASSOS[p.id] || [p.id, ""];
    return `<li class="${p.ok ? "ok" : p === prox ? "agora" : ""}"><span class="cmI">${p.ok ? '<svg class="ic"><use href="#i-check"/></svg>' : i + 1}</span><div><b>${esc(t)}</b>${!p.ok && p === prox ? `<small>${esc(dica)}</small>` : ""}</div></li>`; }).join("");
  box.innerHTML = `<div class="cmHead"><div><b><svg class="ic"><use href="#i-compass"/></svg> Comece aqui</b> <span class="mu">— seu 1º dia, passo a passo (${feitos} de ${d.passos.length})</span></div>
      <button class="btn mini" id="cmEsconder" title="Some daqui. Pra ver de novo, use o botão Comece aqui lá embaixo.">Esconder</button></div>
    <div class="cmBar"><i style="width:${Math.round((feitos / d.passos.length) * 100)}%"></i></div>
    <ol class="cmList">${lin}</ol>
    ${d.simulado ? '<p class="cmSim">Você está vendo como um aluno novo (nada foi apagado). Pra voltar ao normal, abra o Início pelo menu.</p>' : ""}
    ${prox ? `<button class="btn big go" id="cmProx">${esc(COMECE_PASSOS[prox.id][2])} →</button>` : '<p class="cmFim">Dia 1 completo! Agora é repetir: um tema por dia, um estilo que combina com ele.</p>'}`;
  if (d.simulado) { $("#cmEsconder").onclick = () => toast("Modo aluno novo: só pra ver (nada é salvo)."); if (prox) $("#cmProx").onclick = () => COMECE_PASSOS[prox.id][3](); return; }
  $("#cmEsconder").onclick = async () => { try { renderComece(await jpost("/api/comece", { escondido: true })); } catch (e) { toast("❌ " + errTxt(e)); } };
  if (prox) $("#cmProx").onclick = () => COMECE_PASSOS[prox.id][3]();
}
setTimeout(() => { const v = $("#wlComeceVer"); if (v) v.onclick = async () => { try { renderComece(await jpost("/api/comece", { escondido: false })); $("#wlComece").scrollIntoView({ block: "center", behavior: "smooth" }); } catch (e) { } }; }, 0);


// ======================================================= AULAS 07/11 — 3. Estilo novo → amostra de 20 s vira o botão principal
// (a amostra de 20 s já existe no Conferir imagens; 20 s mostram o jeito do estilo em ~1-2 min de máquina, 1 min levaria 3x mais)
function seloPrimeira(e) { return e.usado === 0 ? ' <span class="gtag" title="Você ainda não fez nenhum vídeo com este estilo. Na 1ª vez, o painel sugere ver 20 s de amostra antes.">1ª vez</span>' : ""; }
function estiloNovoConferir(lista, id, chk) {
  const e = (lista || []).find((x) => x.id === id);
  if (e && e.usado === 0 && !$(chk).checked) { $(chk).checked = true; toast("🆕 Estilo novo pra você: deixei marcado “conferir as imagens” pra você ver 20 s de amostra antes.", 5000); }
}
const _renderConferirAulas = renderConferir;
renderConferir = function () {
  _renderConferirAulas();
  const d = CF.d || {}, novo = d.estilo_usado === 0 && !d.amostra;
  $("#conferir").classList.toggle("estiloNovo", novo);
  $("#cfAmostra").className = novo ? "btn big go" : "btn";
  $("#cfRender").className = novo ? "btn" : "btn big go";
  if (novo) {
    $("#cfAmostra").textContent = "🎞 Ver amostra primeiro (20 s)";
    $("#cfRender").textContent = "▶ Pular e fazer o vídeo inteiro";
    $("#cfRender2").textContent = "▶ Pular a amostra e fazer o vídeo inteiro";
  }
  let av = $("#cfNovoAviso");
  if (!av) { av = document.createElement("p"); av.id = "cfNovoAviso"; av.className = "cfNovoAviso"; $("#conferir .cfTop").after(av); }
  av.classList.toggle("hidden", !novo);
  av.innerHTML = novo ? `🆕 Primeira vez com o estilo <b>“${esc(d.estilo_nome || d.estilo || "")}”</b>. Veja 20 segundos antes: leva poucos minutos e evita esperar o vídeo inteiro pra descobrir que não era o jeito que você queria.` : "";
};
async function cfTrocarEstilo() {
  const d = CF.d || {}, p = d.pedido || {};
  if (d.vertical) {
    await openShorts();
    if (p.modo === "roteiro" && p.roteiro) { setModoSh("roteiro"); $("#shRoteiro").value = p.roteiro; } else if (p.tema) { setModoSh("tema"); $("#shTema").value = p.tema; }
    if (p.titulo) $("#shTitulo").value = p.titulo;
    shResumo(); $("#shEstilos").scrollIntoView({ block: "center", behavior: "smooth" });
  } else {
    await openVimg();
    if (p.modo === "roteiro" && p.roteiro) { setModoVi("roteiro"); $("#viRoteiro").value = p.roteiro; } else if (p.tema) { setModoVi("tema"); $("#viTema").value = p.tema; }
    if (p.titulo) $("#viTitulo").value = p.titulo;
    viResumo(); $("#viEstilos").scrollIntoView({ block: "center", behavior: "smooth" });
  }
  toast(p.modo === "audio" ? "🎨 Escolha outro estilo. Suba a narração de novo e clique em Fazer vídeo." : "🎨 O tema continua aqui. Escolha outro estilo e clique em Fazer vídeo.", 6000);
}


// ======================================================= AULAS 07/11 — 4. Caixa única "o que falta" antes de enviar
// Vermelho = falta (não deixa começar) · cinza = só um aviso (tem padrão que funciona) · verde = tudo pronto.
// A conferência da IA/voz do PC usa /api/saude (o servidor guarda por 60 s; aqui também, pra não pesar).
var PRONTO = { saude: null, t: 0 };
async function prontoSaude() {
  if (PRONTO.saude && Date.now() - PRONTO.t < 60000) return PRONTO.saude;
  try { PRONTO.saude = await api("/api/saude"); PRONTO.t = Date.now(); } catch (e) { }
  return PRONTO.saude;
}
function prontoItens(qual, sd) {
  const L = [], falta = (txt, acao) => L.push({ falta: true, txt, acao }), nota = (txt) => L.push({ falta: false, txt });
  const ia = !sd || (sd.ollama && sd.modelo_ok), voz = !sd || sd.voz;
  const iaOff = () => falta("A IA do seu PC está desligada. Abra o programa da IA (ícone da lhama) ou veja em Ajustes.", "aj");
  const palavras = (sel) => ($(sel).value.trim() ? $(sel).value.trim().split(/\s+/).length : 0);
  if (qual === "vi") {
    if (!VI.estilo) falta("Falta escolher o estilo (passo 2).");
    if (VI.modo === "tema" && !$("#viTema").value.trim()) (ia ? nota("Sem tema: a IA do PC escolhe um pra você.") : falta("Falta o tema do vídeo."));
    if (VI.modo === "roteiro" && palavras("#viRoteiro") < 15) falta("Falta o roteiro (cole pelo menos algumas frases).");
    if (VI.modo === "audio" && !VI.audio) falta("Falta subir a narração (espere aparecer ✅ do lado).");
    if (!ia) iaOff();
    if (VI.modo !== "audio" && VI.vz !== "fora" && !voz) falta("A voz do PC não está funcionando. Abra Ajustes e clique em ✅ Testar tudo.", "aj");
  } else if (qual === "sh") {
    if (!SH.estilo) falta("Falta escolher o estilo.");
    if (!SH.audio && SH.modo === "tema" && !$("#shTema").value.trim()) (ia ? nota("Sem ideia: a IA do PC escolhe uma pra você.") : falta("Falta a ideia do short."));
    if (!SH.audio && SH.modo === "roteiro" && palavras("#shRoteiro") < 15) falta("Falta o texto (cole pelo menos algumas frases).");
    if (!ia) iaOff();
    if (!SH.audio && SH.vz !== "fora" && !voz) falta("A voz do PC não está funcionando. Abra Ajustes e clique em ✅ Testar tudo.", "aj");
  } else if (qual === "cr") {
    if (CR.fonte === "link" && !urlOk($("#crUrl").value.trim())) falta("Falta o link do vídeo (começa com https://).");
    if (CR.fonte === "pc" && !CR.arq) falta("Falta escolher o vídeo do PC (espere aparecer ✅).");
    if (!$("#crNome").value.trim() && !(CR.fonte === "pc" && CR.arq)) falta("Falta dar um nome pro estilo.");
  } else if (qual === "cf") {
    const v = $("#cVideo").value.trim();
    if (!v) falta("Falta o link do vídeo que você quer copiar.");
    else if (!urlOk(v)) falta("O link do vídeo não parece certo (precisa começar com https://).");
    else if (!linkRede(v)) falta("Esse link não é do YouTube, Instagram ou TikTok.");
    if (!$("#cTema").value.trim()) (ia ? nota("Sem tema: a IA do PC escolhe um parecido com o vídeo.") : falta("Falta o tema do seu vídeo."));
  }
  return L;
}
var PRONTO_CX = { vi: ["#viPronto", "🎬 Fazer vídeo"], sh: ["#shPronto", "📱 Fazer short"], cr: ["#crPronto", "⚡ Analisar e salvar estilo"], cf: ["#cfPronto", "🚀 Começar"] };
function prontoRender(qual, L) {
  const [sel, botao] = PRONTO_CX[qual], el = $(sel); if (!el) return;
  const faltas = L.filter((x) => x.falta), notas = L.filter((x) => !x.falta);
  el.className = "prontoBox " + (faltas.length ? "falta" : "ok");
  el.innerHTML = (faltas.length ? `<b>Falta pouco pra começar:</b><ul>${faltas.map((x) => `<li>❌ ${esc(x.txt)}${x.acao === "aj" ? ' <button class="btn mini" type="button" data-pr-aj="1">⚙ Abrir Ajustes</button>' : ""}</li>`).join("")}</ul>`
    : `<b>✅ Tudo pronto.</b> Pode clicar em ${esc(botao)}.`) + (notas.length ? `<ul class="prNotas">${notas.map((x) => `<li>ℹ ${esc(x.txt)}</li>`).join("")}</ul>` : "");
  el.querySelectorAll("[data-pr-aj]").forEach((b) => (b.onclick = () => openAjustes()));
  return faltas.length === 0;
}
async function prontoChecar(qual) {
  const L = prontoItens(qual, await prontoSaude());
  const ok = prontoRender(qual, L);
  if (!ok) { const el = $(PRONTO_CX[qual][0]); if (el) el.scrollIntoView({ block: "center", behavior: "smooth" }); toast("Falta pouco: veja o que está em vermelho logo acima do botão.", 4500); }
  return ok;
}
function prontoAtualizar(qual) { prontoSaude().then((sd) => prontoRender(qual, prontoItens(qual, sd))).catch(() => { }); }
(function () {
  const liga = (sec, qual) => { const el = $(sec); if (!el) return; let h; const f = () => { clearTimeout(h); h = setTimeout(() => prontoAtualizar(qual), 250); };
    el.addEventListener("input", f); el.addEventListener("change", f); el.addEventListener("click", f); };
  liga("#vimg", "vi"); liga("#shorts", "sh"); liga("#cpRapido", "cr"); liga("#cpFiel", "cf");
  // ao abrir cada tela, já mostra o estado
  const embrulha = (nome, qual) => { const orig = window[nome]; if (typeof orig !== "function") return; window[nome] = async function (...a) { const r = await orig.apply(this, a); prontoAtualizar(qual); return r; }; };
  embrulha("openVimg", "vi"); embrulha("openShorts", "sh"); embrulha("openCopiar", "cr");
  setTimeout(() => { if (!$("#vimg").classList.contains("hidden")) prontoAtualizar("vi"); if (!$("#shorts").classList.contains("hidden")) prontoAtualizar("sh"); if (!$("#copiar").classList.contains("hidden")) { prontoAtualizar("cr"); prontoAtualizar("cf"); } }, 1500);
})();


// ======================================================= AULAS 07/11 — 5. "O que mudou" na 1ª abertura depois de atualizar
// NOVIDADES.json (vai no pacote) → /api/novidades. A versão já vista fica no navegador.
async function mostrarNovidades(forcar) {
  let d; try { d = await api("/api/novidades"); } catch (e) { return; }
  if (!d || !d.versao || !(d.itens || []).length) { if (forcar) toast("Nenhuma novidade registrada."); return; }
  let vista = null; try { vista = localStorage.getItem("novidades_vista"); } catch (e) { }
  if (!forcar && vista === d.versao) return;
  if (!forcar && !$("#modal").classList.contains("hidden")) return;   // outra janela aberta: mostra na próxima vez
  const dt = /^\d{4}-\d{2}-\d{2}$/.test(d.versao) ? d.versao.split("-").reverse().join("/") : d.versao;
  modal("🆕 " + (d.titulo || "O que mudou")); $("#modal").classList.add("semBarra");
  $("#mMsg").innerHTML = `<p class="mMu">Atualização de ${esc(dt)}. Se alguma tela mudou de lugar, é por isso:</p><ul class="novList">${d.itens.map((t) => `<li>${esc(t)}</li>`).join("")}</ul>`;
  mbtn("👍 Entendi", () => { try { localStorage.setItem("novidades_vista", d.versao); } catch (e) { } closeModal(); }, "go");
}
setTimeout(() => mostrarNovidades(false), 1200);
setTimeout(() => { const b = $("#wlNovidades"); if (b) b.onclick = () => mostrarNovidades(true); }, 0);


// ======================================================= AULAS 07/11 — 6. "O que revisar" junto do vídeo pronto (honesto: o que ficou fraco + créditos + fatos)
async function revisarEm(box, pid) {
  box.innerHTML = '<p class="mu">Conferindo o que revisar…</p>';
  let d; try { d = await api("/api/revisar/" + pid); } catch (e) { box.innerHTML = ""; return; }
  const li = [];
  if (d.tem_cenas) {
    if (d.fracas.length) li.push(`<li class="rvFraco">⚠ ${d.fracas.length === 1 ? "1 imagem talvez não combine" : d.fracas.length + " imagens talvez não combinem"} com o que a voz fala (cena ${d.fracas.join(", ")}). <button class="btn mini" data-rv="conf">🖼 Ver e trocar</button></li>`);
    else if (d.checagem) li.push(`<li class="rvOk">✅ As ${d.cenas} imagens passaram na conferência do PC.</li>`);
  }
  if (d.creditos) li.push(`<li>📷 ${d.creditos} foto(s)/clipe(s) vieram de bancos grátis${d.pedem_credito ? `; ${d.pedem_credito} pedem o nome do autor na descrição do vídeo` : ""}. <button class="btn mini" data-rv="cred">📋 Copiar créditos</button></li>`);
  li.push('<li>📚 Confira nomes, datas e números antes de postar — a IA do PC pode errar.</li>');
  box.innerHTML = `<b>🔎 O que revisar antes de postar</b><ul>${li.join("")}</ul>`;
  const c = box.querySelector('[data-rv="conf"]'); if (c) c.onclick = () => { closeModal(); openConferir(pid); toast("Troque as imagens marcadas com ⚠ e clique em ▶ Montar o vídeo de novo.", 6000); };
  const k = box.querySelector('[data-rv="cred"]'); if (k) k.onclick = async () => toast((await copiarTexto(d.creditos_txt)) ? "✅ Créditos copiados — cole na descrição do vídeo" : "❌ Não consegui copiar");
}
function abrirRevisar(pid) {
  modal("🔎 O que revisar neste vídeo"); $("#modal").classList.add("semBarra");
  const bx = document.createElement("div"); bx.className = "revBox"; $("#mBtns").before(bx); revisarEm(bx, pid);
  mbtnVer(pid, "go"); mbtn("Fechar", closeModal);
}
document.addEventListener("click", (e) => { const b = e.target.closest("[data-rev]"); if (b) { e.stopPropagation(); e.preventDefault(); abrirRevisar(b.dataset.rev); } }, true);


// ======================================================= AULAS 07/11 (rodada 2)
// 5. Números velhos (>7 dias): avisa pra clicar em Atualizar (não coleta sozinho: demora e usa a rede)
function velhoTxt(quando) {
  const m = String(quando || "").match(/(\d{1,2})\/(\d{1,2})\/(\d{4})/); if (!m) return "";
  const dt = new Date(+m[3], +m[2] - 1, +m[1]); const dias = (Date.now() - dt.getTime()) / 864e5;
  if (!(dias > 7)) return "";
  return ` <span class="velho">⚠ Números de ${m[1].padStart(2, "0")}/${m[2].padStart(2, "0")} — clique em 🔄 Atualizar pra ver os de hoje.</span>`;
}
// 10. Vídeo longo: quanto tempo de máquina (média dos vídeos já feitos neste PC por minuto de vídeo)
var DURNOTA = { r: null };
async function durNotaTxt(sel, segs) {
  if (DURNOTA.r == null) {
    DURNOTA.r = 0;
    try {
      const l = (await api("/api/relatorios")).filter((x) => x.local && +x.minutos > 0 && +x.dur >= 20).map((x) => +x.minutos / (+x.dur / 60)).sort((a, b) => a - b);
      DURNOTA.r = l.length >= 3 ? l[Math.floor(l.length / 2)] : 0;
    } catch (e) { }
  }
  const el = $(sel); if (!el) return;
  const fmt = (m) => (m >= 60 ? (Math.round(m / 30) / 2).toString().replace(".", ",") + " h" : Math.max(5, Math.round(m / 5) * 5) + " min");
  const est = DURNOTA.r ? ` Pela média dos vídeos já feitos neste PC, um de ${fmt(segs / 60)} leva <b>cerca de ${fmt((segs / 60) * DURNOTA.r)}</b> (pode variar).` : "";
  el.innerHTML = `⏳ Vídeo longo: o computador pode levar horas pra montar.${est} Pode deixar rodando e fazer outra coisa.`;
}
// 8. "Comece aqui" como aluno novo (pra gravar aula), sem apagar o estado real: #inicio?novo=1 ou Ajustes → Avançado
function comeceComoNovo() { return /[?&]novo=1/.test(location.hash) || /[?&]novo=1/.test(location.search); }
setTimeout(() => {
  const b = $("#ajComeceNovo");
  if (b) b.onclick = () => { history.replaceState(history.state, "", location.pathname + location.search + "#inicio?novo=1"); openInicio(); };
}, 0);
// Extra: trocar o # no endereço com o painel aberto também troca de aba
window.addEventListener("hashchange", () => {
  if (/^#\//.test(location.hash)) { if (location.hash === NAV.hash) return; const novo = rotaParaHash(location.hash); history.replaceState(history.state, "", location.pathname + location.search + novo); }   // endereço colado/digitado à mão
  const [h0, arg] = location.hash.split("="), h = h0.split("?")[0], a = arg ? decodeURIComponent(arg) : undefined;
  const comArg = { "#roteiro": openRoteiro, "#editor": openProject, "#conferir": openConferir, "#cortes": openCortes, "#falado": openFalado, "#ideias": openIdeias, "#feeds": openFeeds };
  const apelido = { "#estilos": "#galeria", "#imagens": "#vimg", "#meus": "#home" };
  if (a && comArg[h]) return comArg[h](a);
  const f = NAV_ABRE[apelido[h] || h]; if (f) f();
});

// ======================================================= MENU DO CELULAR: gaveta com todas as seções (usa os mesmos botões do menu do computador)
(() => {
  const nav = $("#topnav nav"), btn = $("#tnMenu"); if (!nav || !btn) return;
  let gav = null, orig = [];
  const ic = (n) => `<svg class="ic"><use href="#i-${n}"/></svg>`;
  function montar() {
    orig = [];
    const item = (el, rot, desc, extra = "") => { orig.push(el); return `<button class="gvIt ${el.classList.contains("on") ? "on" : ""}" data-gi="${orig.length - 1}">${extra}<span><b>${rot}</b>${desc ? `<small>${desc}</small>` : ""}</span></button>`; };
    let h = "";
    for (const el of nav.children) {
      if (el.classList.contains("tdrop")) {
        const tit = el.querySelector(".tdropBtn").childNodes[0].textContent.trim();
        h += `<div class="gvGrp">${tit}</div>`;
        for (const c of el.querySelectorAll(".tmenu > *")) {
          if (c.classList.contains("tmGrp")) h += `<div class="gvSub">${c.textContent}</div>`;
          else { const mi = c.querySelector(".mi"); h += item(c, c.querySelector("b").textContent.trim(), c.querySelector("small") ? c.querySelector("small").textContent : "", mi ? mi.outerHTML : ""); }
        }
      } else {
        const n = [...el.querySelectorAll(".tn")].map((s) => s.textContent.trim()).filter(Boolean);
        h += item(el, el.childNodes[0].textContent.trim(), "", ic(el.dataset.meus ? "folder" : "compass")).replace("</b>", "</b>").replace(/<\/span><\/button>$/, `</span>${n.length ? `<em class="gvN">${n.join(" · ")}</em>` : ""}</button>`);
      }
    }
    h += `<div class="gvGrp">Painel</div>` + item($("#tnAjustes"), "Ajustes", "IA, voz, pasta e chaves", ic("sliders")) + item($("#tnAjuda"), "Como funciona", "", ic("help"));
    gav.querySelector(".gvBody").innerHTML = h;
  }
  function abrir() {
    if (!gav) {
      gav = document.createElement("div"); gav.id = "gaveta"; gav.className = "gaveta hidden";
      gav.innerHTML = `<div class="gvFundo"></div><aside class="gvPainel"><div class="gvTop"><b>Menu</b><button class="tghost ticon" aria-label="Fechar o menu">${ic("x")}</button></div><div class="gvBody"></div></aside>`;
      document.body.appendChild(gav);
      gav.querySelector(".gvFundo").onclick = gav.querySelector(".gvTop button").onclick = fechar;
      gav.querySelector(".gvBody").onclick = (e) => { const b = e.target.closest("[data-gi]"); if (!b) return; const el = orig[+b.dataset.gi]; fechar(); setTimeout(() => el.click(), 60); };
    }
    montar(); gav.classList.remove("hidden"); document.body.classList.add("gvAberto"); btn.setAttribute("aria-expanded", "true");
  }
  function fechar() { if (!gav) return; gav.classList.add("hidden"); document.body.classList.remove("gvAberto"); btn.setAttribute("aria-expanded", "false"); }
  btn.onclick = () => (gav && !gav.classList.contains("hidden") ? fechar() : abrir());
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") fechar(); });
  matchMedia("(min-width:901px)").addEventListener("change", (m) => { if (m.matches) fechar(); });
})();
