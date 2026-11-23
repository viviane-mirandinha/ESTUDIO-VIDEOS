// Aba "Blender 3D" do painel — vídeo 3D renderizado no Blender (kit em kits/blender-3d; rotas em blender_api.py).
// Carrega DEPOIS do app.js e usa as ajudas dele ($, api, jpost, toast, esc, showOnly, carregarVozes, openProject…).
(() => {
  const BZ = { op: null, maq: null, pid: null, e: null, cena: 1, modo: "gratis", pre: "padrao", tm: "tema", dur: 45, tim: null, velhas: new Set() };
  const ROT = {
    expressao: { feliz: "😀 Feliz", orgulhoso: "😌 Orgulhoso", triste: "😢 Triste", surpreso: "😮 Surpreso", cansado: "😩 Cansado", bravo: "😠 Bravo", pensativo: "🤔 Pensativo", animado: "🤩 Animado" },
    pose: { parado: "Parado", pensando: "Pensando", apontando: "Apontando", comemorando: "Comemorando", andando: "Andando" },
    enquadramento: { geral: "Geral (longe)", medio: "Médio", close: "Close no rosto", lado: "De lado", alto: "De cima" },
    objeto: { nenhum: "Nenhum", carro: "🚗 Carro", galao: "⛽ Galão", gato: "🐱 Gato" },
    lado: { esq: "Esquerda", centro: "Centro", dir: "Direita" },
    cenario: { garagem: "Garagem", atelie: "Ateliê", infinito: "Fundo infinito" },
  };
  const CAMPOS = [["cenario", "Cenário"], ["expressao", "Expressão"], ["pose", "Pose"], ["enquadramento", "Câmera"], ["objeto", "Objeto"], ["lado", "Onde fica o personagem"]];
  const ETAPA = { preparando: ["wait", "⏳ Preparando as cenas"], plano: ["wait", "📝 Plano pronto"], previas: ["wait", "🖼 Gerando quadros de teste"], revisao: ["wait", "👀 Em revisão"], aprovado: ["ok", "✅ Tudo aprovado"], renderizando: ["wait", "🎬 Renderizando"], pronto: ["ok", "✅ Vídeo pronto"], claude: ["wait", "🧠 Claude trabalhando"], erro: ["no", "❌ Deu erro"] };

  NEW_SECS.push("#blender");
  TELA_NOME["#blender"] = "Blender 3D";
  NAV_ABRE["#blender"] = () => openBlender();
  try { ROTAS["#blender"] = "criar/blender"; } catch (e) { }
  Object.assign(TIPO_NOME, { blender_claude: "Blender 3D · ajuste pelo Claude", blender_preparar: "Blender 3D · preparar", blender_previas: "Blender 3D · quadros de teste", blender_render: "Blender 3D · vídeo" });
  Object.assign(TIPO_ICO, { blender_claude: "🧊", blender_preparar: "🧊", blender_previas: "🧊", blender_render: "🧊" });

  const css = document.createElement("link"); css.rel = "stylesheet"; css.href = "/static/blender.css"; document.head.appendChild(css);

  $("#stickman").insertAdjacentHTML("afterend", `
<section id="blender" class="hidden tool">
  <div class="sect"><h3>🧊 Blender 3D</h3><span>Vídeo com <b>personagem e objetos em 3D</b>, renderizado no Blender (luz e sombras de cinema). Você revisa <b>cena por cena</b> antes do render completo e pode mudar personagem, cenário e estilo. O render pesado roda na sua máquina potente.</span></div>

  <div id="bzCriar">
    <div class="card pstep">
      <h3><span class="num">⚙</span> Máquina de render</h3>
      <div class="bzMaq"><span class="bzChip wait" id="bzMaqChip">Verificando…</span><span class="mu" id="bzMaqInfo"></span>
        <button class="btn" id="bzMaqTestar">🔄 Testar de novo</button><button class="btn" id="bzMaqEditar">✏ Mudar</button></div>
      <div class="bzMaqEdit" id="bzMaqEdit">
        <div class="row"><label>Modo</label><select id="bzMModo"><option value="remoto">Máquina de render (rede)</option><option value="local">Este computador (bem mais lento)</option></select></div>
        <div class="row"><label>Endereço (IP)</label><input type="text" id="bzMHost" /></div>
        <div class="row"><label>Usuário</label><input type="text" id="bzMUser" /></div>
        <div class="row"><label>Chave de acesso</label><input type="text" id="bzMChave" /></div>
        <div class="row"><label>Blender (caminho)</label><input type="text" id="bzMBlender" /></div>
        <div class="row"><label>Pasta de trabalho</label><input type="text" id="bzMPasta" /></div>
        <div class="row"><label></label><button class="btn ok" id="bzMSalvar">💾 Salvar e testar</button></div>
      </div>
    </div>

    <div class="card pstep">
      <h3><span class="num">1</span> Quem escreve a cena 3D?</h3>
      <div class="modos m2" id="bzModo">
        <button class="modo on" data-bzm="gratis"><b>🆓 Painel sozinho (grátis)</b><small>A IA do seu PC escolhe expressão, pose e câmera de cada cena, com as peças prontas</small></button>
        <button class="modo" data-bzm="claude" id="bzModoClaude"><b>🧠 Claude escreve a cena</b><small>Cena sob medida e peças novas, se precisar. <u>Gasta tokens ou a sua assinatura</u> e leva mais tempo</small></button>
      </div>
    </div>

    <div class="card pstep">
      <h3><span class="num">2</span> Sobre o que é o vídeo?</h3>
      <div class="modos m2" id="bzTm">
        <button class="modo on" data-bztm="tema"><b>💡 Tenho só o tema</b><small>A IA do seu PC escreve o roteiro</small></button>
        <button class="modo" data-bztm="roteiro"><b>📝 Já tenho o roteiro</b><small>Cole o texto e a gente narra</small></button>
      </div>
      <div class="row" data-bztr="tema"><label>Tema</label><input type="text" id="bzTema" placeholder="Ex.: Como funciona o motor de um carro" /></div>
      <div class="row hidden" data-bztr="roteiro"><label>Roteiro</label><textarea id="bzRoteiro" rows="6" placeholder="Cole aqui o texto que vai ser narrado…"></textarea></div>
      <div class="row" data-bztr="tema"><label>Duração</label><div class="durs" id="bzDurs"></div></div>
      <div class="row"><label>Voz</label><select id="bzVoz" class="selVoz"></select><button class="btn" type="button" data-ouvir="#bzVoz" title="Ouvir esta voz">🔊 Ouvir</button><span class="ouvirR"></span></div>
    </div>

    <div class="card pstep">
      <h3><span class="num">3</span> Visual: personagem e estilo</h3>
      <p class="help">Cada predefinição já traz personagem, roupa, cores e estilo de render (vinil, massinha ou desenho). Depois dá pra mudar cena por cena.</p>
      <div class="bzPres" id="bzPres"></div>
      <details class="bzDet" id="bzVisCriar"><summary>🎨 Personalizar personagem, cores e estilo <small class="mu">(opcional)</small></summary><div id="bzVedCriar"></div></details>
      <h4 style="margin:14px 0 6px">🏠 Cenário: quem projeta o ambiente deste vídeo?</h4>
      <p class="help">Todo vídeo ganha um cenário novo, feito para o roteiro: tamanho da sala, piso, parede, céu, luz e os objetos (materiais e modelos livres do Poly Haven e Poly Pizza). Escolha quem desenha esse cenário:</p>
      <div class="modos m2" id="bzAmb">
        <button class="modo on" data-bza="ollama"><b>🆓 IA do seu PC (Ollama) — padrão</b><small>Grátis, roda no seu computador. Bom, mas às vezes escolhe objetos que não combinam</small></button>
        <button class="modo" data-bza="claude" id="bzAmbClaude"><b>🧠 Claude projeta o cenário</b><small>Cenário bem mais fiel ao roteiro. <u>Gasta tokens ou a sua assinatura</u> (só este passo, é curto)</small></button>
      </div>
      <div class="row"><label></label><label class="chk"><input type="checkbox" id="bzAmbNao" /> Não criar cenário novo (usar só a sala pronta antiga)</label></div>
      <div class="row"><label></label><label class="chk"><input type="checkbox" id="bzBuscar" checked /> 🔎 Procurar modelos 3D novos para este tema <small class="mu">(objetos livres CC0 da internet, tipo geladeira, prateleira, árvore)</small></label></div>
      <div class="row"><label></label><button class="btn big go" id="bzFazer">🧊 Preparar as cenas</button><span class="mu" id="bzFazerNota">Roteiro → voz → plano de cenas (uns 2–4 min). Nada é renderizado ainda.</span></div>
    </div>

    <div class="card pstep">
      <h3><span class="num">📦</span> Meus modelos 3D <small class="mu">(.glb)</small></h3>
      <p class="help">Traga personagens, cenários ou objetos 3D seus (arquivo <b>.glb</b>). Depois, na revisão de cada cena, você escolhe onde usar. <b>Só use modelos que você tem direito de usar.</b> Eles ficam só neste computador.</p>
      <div id="bzModelos" class="bzModelos"></div>
      <div class="row"><label></label><input type="file" id="bzModeloArq" accept=".glb" hidden /><button class="btn" id="bzModeloSubir">⬆ Enviar um modelo .glb</button><span class="mu" id="bzModeloMsg"></span></div>
    </div>

    <h4 class="grp">🎞 Seus vídeos Blender 3D <span id="bzN"></span></h4>
    <div id="bzLista" class="gridIn bzLista"></div>
  </div>

  <div id="bzRevisao" class="hidden"></div>
</section>`);

  const el = (s) => $(s);
  // cenas do plano que o usuário edita (plano.json) completadas com id/tempos do plano arrumado (blender/plano.normalizado.json)
  const cenasDe = (e) => { const p = ((e.plano || {}).cenas) || [], n = ((e.plano_normalizado || {}).cenas) || []; return p.map((c, i) => ({ ...(n[i] || {}), ...c })); };
  const chipEtapa = (e) => { const [c, t] = ETAPA[e] || ["wait", e]; return `<span class="bzChip ${c}">${t}</span>`; };

  // ------------------------------------------------------------------ máquina de render
  async function bzMaq(testar) {
    let m; try { m = BZ.maq = await api("/api/blender/maquina"); } catch (e) { return; }
    el("#bzMaqInfo").textContent = m.modo === "local" ? "Renderiza neste computador" : `${m.usuario}@${m.host}`;
    el("#bzMModo").value = m.modo; el("#bzMHost").value = m.host || ""; el("#bzMUser").value = m.usuario || ""; el("#bzMChave").value = m.chave || "";
    el("#bzMBlender").value = m.blender || ""; el("#bzMPasta").value = m.pasta || "";
    const chip = el("#bzMaqChip");
    if (!testar) return;
    chip.className = "bzChip wait"; chip.textContent = "Verificando…";
    try {
      const r = await jpost("/api/blender/maquina/testar", {});
      if (r.ok) { chip.className = "bzChip ok"; chip.textContent = r.erro ? "🟡 " + r.erro : `🟢 Online${r.gpu ? " · " + r.gpu : ""}`; }
      else { chip.className = "bzChip no"; chip.textContent = "🔴 " + (r.erro || "Fora do ar"); }
    } catch (e) { chip.className = "bzChip no"; chip.textContent = "🔴 " + errTxt(e); }
  }
  el("#bzMaqTestar").onclick = () => bzMaq(true);
  el("#bzMaqEditar").onclick = () => el("#bzMaqEdit").classList.toggle("on");
  el("#bzMSalvar").onclick = async () => {
    try {
      await jpost("/api/blender/maquina", { modo: el("#bzMModo").value, host: el("#bzMHost").value, usuario: el("#bzMUser").value, chave: el("#bzMChave").value, blender: el("#bzMBlender").value, pasta: el("#bzMPasta").value }, "PUT");
      toast("✅ Salvo. Testando a máquina…"); el("#bzMaqEdit").classList.remove("on"); bzMaq(true);
    } catch (e) { toast("❌ " + errTxt(e), 5000); }
  };

  // ------------------------------------------------------------------ criar
  async function bzOpcoes() {
    if (!BZ.op) BZ.op = await api("/api/blender/opcoes");
    const ba = el("#bzAmbClaude"); if (ba && !BZ.op.claude) { ba.disabled = true; ba.title = "O app do Claude não foi encontrado neste PC"; ba.querySelector("small").textContent = "Precisa do app do Claude instalado neste PC (claude.ai/download)."; }
    const bc = el("#bzModoClaude"); if (bc && !BZ.op.claude) { bc.disabled = true; bc.title = "O app do Claude não foi encontrado neste PC"; bc.querySelector("small").textContent = "Precisa do app do Claude instalado neste PC (claude.ai/download)."; }
    const cores = (p) => ["roupa", "baixo", "calca", "pele", "cabelo"].map((k) => (p.personagem.cores || {})[k]).filter(Boolean);
    const estilo = (p) => ({ vinil: "Vinil brilhante", massinha: "Massinha fosca", desenho: "Desenho com contorno" })[(p.render || {}).material] || "Vinil brilhante";
    el("#bzPres").innerHTML = BZ.op.predefinicoes.map((p) => `<button type="button" class="bzPre ${p.id === BZ.pre ? "on" : ""}" data-bzp="${esc(p.id)}">
      <b>${esc(p.nome)}</b><div class="bzSw">${(cores(p).length ? cores(p) : ["#e8bb96", "#f1ead9", "#1d1d22", "#1a120e"]).map((c) => `<i style="background:${c}"></i>`).join("")}</div>
      <small>${estilo(p)} · luz ${esc((p.render || {}).luz || "suave")}</small></button>`).join("");
  }
  el("#bzPres").onclick = (e) => { const b = e.target.closest("[data-bzp]"); if (!b) return; BZ.pre = b.dataset.bzp; bzOpcoes(); if (window.__vedCriarReset) window.__vedCriarReset(); };
  el("#bzModo").onclick = (e) => {
    const b = e.target.closest("[data-bzm]"); if (!b || b.disabled) return;
    BZ.modo = b.dataset.bzm; modosOn("#bzModo", "bzm", BZ.modo);
    el("#bzFazerNota").textContent = BZ.modo === "claude"
      ? "Roteiro → voz → o Claude escreve a cena (vários minutos, gasta tokens) → quadros de teste. Nada é renderizado ainda."
      : "Roteiro → voz → plano de cenas (uns 2–4 min). Nada é renderizado ainda.";
  };
  BZ.amb = "ollama";
  el("#bzAmb").onclick = (e) => {
    const b = e.target.closest("[data-bza]"); if (!b || b.disabled) return;
    BZ.amb = b.dataset.bza; modosOn("#bzAmb", "bza", BZ.amb);
  };
  el("#bzAmbNao").onchange = () => { el("#bzAmb").style.opacity = el("#bzAmbNao").checked ? 0.4 : 1; };
  el("#bzTm").onclick = (e) => {
    const b = e.target.closest("[data-bztm]"); if (!b) return;
    BZ.tm = b.dataset.bztm; modosOn("#bzTm", "bztm", BZ.tm);
    document.querySelectorAll("#blender [data-bztr]").forEach((r) => r.classList.toggle("hidden", r.dataset.bztr !== BZ.tm));
  };
  el("#bzFazer").onclick = async () => {
    const tema = el("#bzTema").value.trim(), roteiro = el("#bzRoteiro").value.trim();
    if (BZ.tm === "tema" && !tema) return erroCampo("#bzTema", "Escreva o tema do vídeo");
    if (BZ.tm === "roteiro" && roteiro.split(/\s+/).length < 8) return erroCampo("#bzRoteiro", "Cole o roteiro (pelo menos algumas frases)");
    let r;
    try { r = await jpost("/api/blender/criar", { modo: BZ.modo, tema: BZ.tm === "tema" ? tema : "", roteiro: BZ.tm === "roteiro" ? roteiro : "", duracao: BZ.dur, voz: el("#bzVoz").value, predefinicao: BZ.pre, buscar_modelos: el("#bzBuscar").checked, ambiente: el("#bzAmbNao").checked ? "nenhum" : BZ.amb, ...(VED.criar && VED.criar.tocado ? { personagem: VED.criar.pers, render: VED.criar.render } : {}) }); }
    catch (e) { return toast("❌ " + errTxt(e), 6000); }
    BZ.cena = 1; BZ.velhas = new Set();
    await bzAbrir(r.pid);
  };
  async function bzLista() {
    let l = []; try { l = (await api("/api/blender/lista")).projetos; } catch (e) { }
    el("#bzN").textContent = l.length || "";
    el("#bzLista").innerHTML = l.length ? l.map((p) => `<div class="proj" data-bzo="${p.pid}"><div class="th">🧊</div>
      <div class="badge ${p.etapa === "pronto" ? "ok" : "no"}">${(ETAPA[p.etapa] || [0, p.etapa])[1]}</div>
      <div class="nm">${esc(String(p.nome).replace(/^\d+\s*-\s*[^-]+-\s*/, ""))}</div><div class="meta">${p.n_cenas || 0} cenas</div>
      <div class="acts"><button class="btn ok" data-bzo="${p.pid}">${p.etapa === "pronto" ? "Abrir" : "Continuar"}</button></div></div>`).join("")
      : '<div class="card mu">Seus vídeos em Blender 3D vão aparecer aqui.</div>';
  }
  el("#bzLista").onclick = (e) => { const b = e.target.closest("[data-bzo]"); if (b) { BZ.cena = 1; BZ.velhas = new Set(); bzAbrir(b.dataset.bzo); } };

  async function openBlender(pid) {
    if (!showOnly("#blender")) return;
    carregarVozes().catch(() => { });
    renderDurs("#bzDurs", BZ.dur, (d) => (BZ.dur = d), null, [[20, "20 s"], [30, "30 s"], [45, "45 s"], [60, "1 min"], [90, "1:30"], [120, "2 min"], [180, "3 min"]]);
    await bzOpcoes().catch(() => { });
    bzMaq(true); bzLista(); bzModelos();
    if (pid) return bzAbrir(pid);
    el("#bzCriar").classList.remove("hidden"); el("#bzRevisao").classList.add("hidden");
  }
  window.openBlender = openBlender;
  el("#tnBlender") && (el("#tnBlender").onclick = () => openBlender());

  // ------------------------------------------------------------------ revisão cena a cena
  async function bzCarregar() { BZ.e = await api("/api/blender/" + BZ.pid); return BZ.e; }
  async function bzAbrir(pid) {
    BZ.pid = pid; delete VED.rev;
    el("#bzCriar").classList.add("hidden"); el("#bzRevisao").classList.remove("hidden");
    try { await bzCarregar(); } catch (e) { toast("❌ " + errTxt(e), 5000); return bzVoltar(); }
    bzDesenhar(); bzPoll();
  }
  function bzVoltar() { clearTimeout(BZ.tim); BZ.pid = null; el("#bzRevisao").classList.add("hidden"); el("#bzCriar").classList.remove("hidden"); bzLista(); }
  function bzPoll() {
    clearTimeout(BZ.tim);
    if (!BZ.e || !BZ.e.job || !BZ.pid) return;
    BZ.tim = setTimeout(async () => {
      const antes = BZ.e && BZ.e.job && BZ.e.job.tipo;
      try { await bzCarregar(); } catch (e) { return bzPoll(); }
      if (BZ.e.job) { bzJobBarra(); return bzPoll(); }
      bzDesenhar();
      if (BZ.e.etapa === "erro" || BZ.e.erro) toast("❌ Deu erro. Veja os detalhes na tela.", 5000);
      else if (antes === "blender_render") toast("✅ Vídeo pronto!", 5000);
      else if (antes === "blender_preparar") toast("✅ Cenas prontas. Gere os quadros de teste.", 4000);
      filaAtualizar && filaAtualizar();
    }, 2000);
  }
  function bzJobBarra() {
    const j = BZ.e && BZ.e.job, b = el("#bzJobBox");
    if (!b || !j) return;
    b.querySelector(".msg").textContent = `${Math.round(j.pct || 0)}% — ${j.msg || ""}`;
    b.querySelector(".bar i").style.width = (j.pct || 0) + "%";
  }
  const sel = (campo, valor, n) => `<div><label>${(CAMPOS.find((c) => c[0] === campo) || [0, campo])[1]}</label><select data-bzc="${campo}" data-n="${n}">${Object.entries(ROT[campo]).map(([k, v]) => `<option value="${k}" ${k === valor ? "selected" : ""}>${v}</option>`).join("")}</select></div>`;

  function bzDesenhar() {
    const e = BZ.e, box = el("#bzRevisao");
    if (!e) return;
    const cenas = cenasDe(e);
    const ap = (e.aprovacao || {}).cenas || {};
    const ocupado = !!e.job;
    let h = `<div class="bzVolt"><button class="btn" id="bzVoltar">← Voltar</button></div>
      <div class="card"><div class="bzTop"><h3 style="margin:0">${esc(String(e.nome).replace(/^\d+\s*-\s*/, ""))}</h3>${chipEtapa(e.etapa)}
      <span class="mu">${e.pedido && e.pedido.predefinicao ? "Visual: " + esc(e.pedido.predefinicao) : ""}</span></div>
      ${(e.avisos || []).map((a) => `<div class="bzAviso">⚠️ ${esc(a)}</div>`).join("")}
      ${e.job ? `<div class="bzJob" id="bzJobBox"><b>${esc(({ blender_preparar: "Preparando as cenas", blender_previas: "Gerando os quadros de teste", blender_render: "Renderizando o vídeo", blender_claude: "O Claude está ajustando a cena" })[e.job.tipo] || "Trabalhando")}…</b><div class="msg mu"></div><div class="bar"><i></i></div><div class="mu" style="margin-top:6px">Pode sair desta tela: o trabalho continua e aparece em 📂 Meus vídeos.</div></div>` : ""}
      ${e.erro && !e.job ? `<div class="bzAviso" style="border-color:#d95;background:#4a2222"><b>Deu erro:</b><pre style="white-space:pre-wrap;margin:6px 0 0;max-height:200px;overflow:auto">${esc(String(e.erro).slice(-1500))}</pre></div>` : ""}</div>`;

    if (e.etapa === "pronto" && !ocupado) {
      h += `<div class="card"><h3>✅ Vídeo pronto!</h3><div class="bzAcoes"><button class="btn ok big" data-bzx="editor">✏ Abrir no editor</button><button class="btn big" data-bzx="ver">▶ Ver o vídeo</button><button class="btn big" data-bzx="pasta">📂 Pasta</button></div></div>`;
    }
    if (e.etapa === "plano" && !ocupado) h += `<div class="card"><h3 style="margin-top:0">Próximo passo</h3><p class="mu">As cenas estão planejadas (confira o texto e as escolhas abaixo). Gere um quadro de teste de cada cena para ver como vai ficar. Isso leva poucos segundos.</p><button class="btn go big" data-bzx="previas">🖼 Gerar os quadros de teste</button></div>`;
    if (e.plano && cenas.length && !["preparando"].includes(e.etapa)) {
      const n = Math.min(Math.max(1, BZ.cena), cenas.length); BZ.cena = n;
      const c = cenas[n - 1] || {}, pv = (e.previas || []).find((p) => p.cena === n), velha = BZ.velhas.has(n);
      const st = (i) => ap[String(i)] === "aprovada" ? "ok" : (ap[String(i)] === "ajustar" || BZ.velhas.has(i)) ? "aj" : "";
      h += `<div class="card"><h3 style="margin-top:0">Cenas (${cenas.length})</h3><div class="bzStep">${cenas.map((x, i) => `<button class="btn pill ${st(i + 1)} ${i + 1 === n ? "on" : ""}" data-bzs="${i + 1}" title="${esc(x.texto || "")}">${st(i + 1) === "ok" ? "✅" : st(i + 1) === "aj" ? "✏️" : "⏳"} ${i + 1}</button>`).join("")}</div>
        <div class="bzRev"><div class="bzImg">${pv ? `<img src="${pv.url}" alt="Cena ${n}">` : `<div class="velha" style="background:#2a2c33">Sem quadro de teste ainda</div>`}${pv && velha ? `<div class="velha">Você mudou esta cena.<br>Clique em “Atualizar quadro” para ver o resultado.</div>` : ""}</div>
        <div><div class="mu">Cena ${n} de ${cenas.length} · ${Number(c.de || 0).toFixed(1)}s → ${Number(c.ate || 0).toFixed(1)}s</div>
          <div class="bzTexto">“${esc(c.texto || "")}”</div>
          ${e.cena_manual ? `<div class="bzAviso">🧠 Esta cena foi escrita à mão pelo Claude, então os campos prontos não valem aqui. Para mudar algo, peça ao Claude abaixo.</div>` : `<div class="bzCampos">${CAMPOS.map(([k]) => sel(k, c[k], n)).join("")}</div>`}
          ${e.cena_manual ? "" : bzModelosCena(c, n)}
          ${(e.pedido && e.pedido.modo === "claude") ? `<div class="bzClaude"><label>🧠 Pedir uma mudança ao Claude <small>(gasta tokens; ele refaz os quadros de teste)</small></label><textarea id="bzPedirTxt" rows="2" placeholder="Ex.: na cena ${n}, deixe o personagem mais perto e com cara de espanto; troque o cenário por uma cozinha"></textarea><button class="btn" data-bzx="pedir" ${ocupado ? "disabled" : ""}>🧠 Pedir ao Claude</button></div>` : ""}
          <div class="bzAcoes">
            <button class="btn" data-bzx="atualizar" ${ocupado ? "disabled" : ""}>🔄 Atualizar quadro desta cena</button>
            <button class="btn" data-bzx="atualizar_todas" ${ocupado ? "disabled" : ""}>🔄 Atualizar todos os quadros</button>
          </div>
          <div class="bzAcoes">
            ${e.etapa === "aprovado" && !ocupado ? `<button class="btn go big" data-bzx="renderizar">🎬 Renderizar o vídeo agora</button>` : ""}
            <button class="btn ok big" data-bzx="proxima" ${ocupado || !pv ? "disabled" : ""}>✅ Aprovar e ir para a próxima</button>
            <button class="btn go big" data-bzx="tudo" ${ocupado || !pv ? "disabled" : ""}>⚡ Aprovar e fazer tudo de uma vez</button>
          </div>
          <p class="mu">“Fazer tudo” aprova esta e todas as cenas que faltam e já começa o render completo.</p></div></div></div>`;
    }
    h += `<div class="card"><details class="bzDet" id="bzVisRev"><summary><b>🎨 Visual do personagem e do estilo (vídeo todo)</b></summary><div id="bzVedRev"></div></details></div>`;
    if (e.resumo_claude) h += `<div class="card"><details><summary><b>🧠 O que o Claude fez</b></summary><pre style="white-space:pre-wrap;margin:8px 0 0">${esc(e.resumo_claude)}</pre></details></div>`;
    box.innerHTML = h;
    bzJobBarra();
    bzVisRevLigar();
  }

  async function acao(a) {
    const e = BZ.e, n = BZ.cena, total = cenasDe(e).length;
    try {
      if (a === "editor") return openProject(e.pid);
      if (a === "ver") return assistirAqui(e.pid, (e.pedido && e.pedido.tema) || e.nome || "Vídeo pronto", false);
      if (a === "pasta") return api(`/api/open/${e.pid}?what=folder`, { method: "POST" });
      if (a === "previas") await jpost(`/api/blender/${e.pid}/previas`, {});
      else if (a === "atualizar_todas") { await jpost(`/api/blender/${e.pid}/previas`, {}); BZ.velhas = new Set(); }
      else if (a === "atualizar") { await jpost(`/api/blender/${e.pid}/previas`, { cenas: [n] }); BZ.velhas.delete(n); }
      else if (a === "renderizar") await jpost(`/api/blender/${e.pid}/renderizar`, {});
      else if (a === "pedir") {
        const t = (el("#bzPedirTxt").value || "").trim();
        if (t.length < 5) return erroCampo("#bzPedirTxt", "Descreva o que quer mudar");
        if (!confirm("Pedir ao Claude para mexer na cena? Isso gasta tokens (ou a sua assinatura) e leva alguns minutos.")) return;
        await jpost(`/api/blender/${e.pid}/pedir-ajuste`, { texto: t, cena: n });
        BZ.velhas = new Set();
      }
      else if (a === "proxima" || a === "tudo") {
        if (a === "tudo" ? BZ.velhas.size : BZ.velhas.has(n)) return toast("Você mudou uma cena: clique em “Atualizar quadro” antes de aprovar.", 4500);
        if (a === "tudo") {
          const seg = Math.max(30, ...cenasDe(e).map((c) => c.ate || 0));
          if (!confirm(`Aprovar todas as cenas e renderizar o vídeo inteiro agora?\n\nLeva uns ${Math.max(2, Math.ceil(seg * 0.4 / 60) + 1)} min na máquina de render.`)) return;
        }
        const r = await jpost(`/api/blender/${e.pid}/aprovar`, { cena: n, acao: a });
        if (a === "proxima") {
          if (r.proxima) BZ.cena = r.proxima;
          if (r.aprovado) toast("✅ Todas as cenas aprovadas! Clique em “Renderizar o vídeo agora”.", 5000);
        }
      }
    } catch (x) { return toast("❌ " + errTxt(x), 6000); }
    await bzCarregar(); bzDesenhar(); bzPoll();
  }

  el("#bzRevisao").onclick = (ev) => {
    if (ev.target.closest("#bzVoltar")) return bzVoltar();
    const s = ev.target.closest("[data-bzs]"); if (s) { BZ.cena = +s.dataset.bzs; return bzDesenhar(); }
    const x = ev.target.closest("[data-bzx]"); if (x && !x.disabled) acao(x.dataset.bzx);
  };
  el("#bzRevisao").onchange = async (ev) => {
    const mt = ev.target.closest("[data-bzmc],[data-bzmx],[data-bzme],[data-bzsp]");
    if (mt) return bzSalvaModelosCena(+mt.dataset.n);
    const s = ev.target.closest("[data-bzc]"); if (!s) return;
    const n = +s.dataset.n;
    try { await jpost(`/api/blender/${BZ.pid}/ajustar`, { cena: n, campos: { [s.dataset.bzc]: s.value } }); BZ.velhas.add(n); }
    catch (x) { toast("❌ " + errTxt(x), 6000); }
    await bzCarregar(); bzDesenhar();
  };


  // ---- modelos .glb dentro da cena
  function bzModelosCena(c, n) {
    const lib = BZ.modelos || [];
    const nos = {}; (c.modelos || []).forEach((m) => { const o = typeof m === "string" ? { id: m } : m; nos[o.id] = o; });
    const lista = lib.length ? lib.map((m) => {
      const on = !!nos[m.id], o = nos[m.id] || {}, x = (o.pos || [0])[0];
      return `<div class="bzModCena"><label class="chk"><input type="checkbox" data-bzmc="${esc(m.id)}" data-n="${n}" ${on ? "checked" : ""}> 📦 ${esc(m.id)}</label>
        ${on ? `<select data-bzmx="${esc(m.id)}" data-n="${n}"><option value="-1.5" ${x < -0.5 ? "selected" : ""}>Esquerda</option><option value="0" ${x >= -0.5 && x <= 0.5 ? "selected" : ""}>Centro</option><option value="1.5" ${x > 0.5 ? "selected" : ""}>Direita</option></select>
        <label class="mu">tamanho <input type="number" step="0.1" min="0.05" max="20" value="${o.escala || 1}" data-bzme="${esc(m.id)}" data-n="${n}" style="width:70px"></label>` : ""}</div>`;
    }).join("") : '<div class="mu">Você ainda não enviou modelos .glb (veja “Meus modelos 3D” na tela de criar).</div>';
    return `<details class="bzDet" ${Object.keys(nos).length || c.sem_personagem ? "open" : ""}><summary>📦 Modelos 3D nesta cena</summary>${lista}
      <label class="chk" style="margin-top:8px"><input type="checkbox" data-bzsp="1" data-n="${n}" ${c.sem_personagem ? "checked" : ""}> Esconder o personagem do kit nesta cena</label></details>`;
  }
  async function bzSalvaModelosCena(n) {
    const box = el("#bzRevisao"), itens = [];
    box.querySelectorAll(`[data-bzmc][data-n="${n}"]`).forEach((cb) => {
      if (!cb.checked) return; const id = cb.dataset.bzmc;
      const x = box.querySelector(`[data-bzmx="${CSS.escape(id)}"][data-n="${n}"]`), es = box.querySelector(`[data-bzme="${CSS.escape(id)}"][data-n="${n}"]`);
      itens.push({ id, x: x ? parseFloat(x.value) : 0, escala: es ? parseFloat(es.value) || 1 : 1 });
    });
    try { await jpost(`/api/blender/${BZ.pid}/ajustar`, { cena: n, campos: { modelos: itens, sem_personagem: !!box.querySelector(`[data-bzsp][data-n="${n}"]`).checked || "" } }); BZ.velhas.add(n); }
    catch (x) { toast("❌ " + errTxt(x), 6000); }
    await bzCarregar(); bzDesenhar();
  }

  // ---- editor visual dentro da revisão
  function bzVisRevLigar() {
    const det = el("#bzVisRev"); if (!det) return;
    const cbRev = async (acao) => { if (acao === "aplicar") await bzAplicarVisual(); };
    det.addEventListener("toggle", async () => {
      if (!det.open) return;
      const box = el("#bzVedRev");
      if (VED.rev) { VED.rev.box = box; box.innerHTML = vedHtml("rev"); return vedEventos(box, "rev", cbRev); }   // a tela foi redesenhada: volta com o que já estava editado
      box.innerHTML = '<div class="mu">Carregando…</div>';
      try {
        const v = await api(`/api/blender/${BZ.pid}/visual`);
        vedMontar("rev", box, v.personagem, v.render, v.predefinicao || (BZ.e.pedido || {}).predefinicao || "padrao",
          `${v.cena_manual ? '<div class="bzAviso">🧠 Esta cena foi escrita à mão pelo Claude: o personagem vem do código dela. Aqui vale só o <b>estilo do render</b>. Para mudar o personagem, peça ao Claude.</div>' : ""}
           <div class="bzAcoes"><button class="btn ok big" data-vx="aplicar">✅ Aplicar a este vídeo</button></div><p class="mu">Ao aplicar, todos os quadros de teste ficam desatualizados e você revisa as cenas de novo.</p>`);
        vedEventos(box, "rev", cbRev);
      } catch (x) { box.innerHTML = '<div class="bzAviso">❌ ' + esc(errTxt(x)) + "</div>"; }
    });
  }
  async function bzAplicarVisual() {
    const V = VED.rev; if (!V) return;
    if (!confirm("Aplicar este visual ao vídeo todo? Os quadros de teste vão precisar ser atualizados.")) return;
    try { await jpost(`/api/blender/${BZ.pid}/visual`, { personagem: V.pers, render: V.render, predefinicao: V.pre }, "PUT"); }
    catch (x) { return toast("❌ " + errTxt(x), 6000); }
    delete VED.rev; BZ.velhas = new Set(((BZ.e.plano || {}).cenas || []).map((_, i) => i + 1));
    await bzCarregar(); bzDesenhar(); toast("✅ Visual aplicado. Clique em “Atualizar todos os quadros”.", 5000);
  }

  // ================================================================== EDITOR VISUAL (personagem + estilo do render)
  const COR_ROT = { pele: "Pele", roupa: "Roupa (cima)", baixo: "Camiseta por baixo", calca: "Calça", tenis: "Tênis", sola: "Sola", cabelo: "Cabelo", listraA: "Listra A", listraB: "Listra B", cadarco: "Cadarço" };
  const OPC = {
    estilo: { vinil: "Vinil", massinha: "Massinha", desenho: "Desenho" }, roupa: { camiseta: "Camiseta", moletom: "Moletom", jardineira: "Jardineira", jaqueta: "Jaqueta", varsity: "Jaqueta varsity" },
    cabelo: { tigela: "Tigela", topete: "Topete", cacheado: "Cacheado", mullet: "Mullet" }, barba: { nenhuma: "Nenhuma", cavanhaque: "Cavanhaque" },
    material: { vinil: "Vinil (brilhante)", massinha: "Massinha (fosco)", desenho: "Desenho (contorno)" }, luz: { suave: "Suave", dura: "Dura", neutra: "Neutra" },
    acessorio: { brinco: "Brinco", tatuagem: "Tatuagem", bolsa: "Bolsa", bolsosCargo: "Bolsos cargo", cadarcos: "Cadarços" },
  };
  const clone = (o) => JSON.parse(JSON.stringify(o));
  const juntaP = (a, b) => { const r = clone(a); for (const [k, v] of Object.entries(b || {})) r[k] = v && typeof v === "object" && !Array.isArray(v) ? { ...(r[k] || {}), ...v } : v; return r; };
  const VED = {};   // estado de cada editor: { pers, render, pre, ult }

  function vedHtml(k) {
    const o = (m, cur) => Object.entries(m).map(([v, l]) => `<option value="${v}" ${v === cur ? "selected" : ""}>${l}</option>`).join("");
    const V = VED[k], P = V.pers, R = V.render;
    const pres = BZ.op.predefinicoes;
    return `<div class="bzVed" data-ved="${k}">
      <div class="bzVedTop"><label>Começar de</label><select data-vp="pre">${pres.map((p) => `<option value="${esc(p.id)}" ${p.id === V.pre ? "selected" : ""}>${esc(p.nome)}${p.builtin ? "" : " ★"}</option>`).join("")}</select>
        <button class="btn" data-vx="salvar">💾 Salvar como predefinição</button>${(pres.find((p) => p.id === V.pre) || {}).builtin === false ? `<button class="btn danger" data-vx="apagar">🗑 Apagar esta</button>` : ""}</div>
      <div class="bzVedGrid">
        <div>
          <h5>Personagem</h5>
          <div class="bzCampos">
            <div><label>Estilo do corpo</label><select data-vp="estilo">${o(OPC.estilo, P.estilo)}</select></div>
            <div><label>Roupa</label><select data-vp="roupa">${o(OPC.roupa, P.roupa)}</select></div>
            <div><label>Cabelo</label><select data-vp="cabelo">${o(OPC.cabelo, P.cabelo)}</select></div>
            <div><label>Barba</label><select data-vp="barba">${o(OPC.barba, P.barba)}</select></div>
            <div><label>Tamanho (${Number(P.escala || 1).toFixed(2)}×)</label><input type="range" min="0.6" max="1.6" step="0.05" value="${P.escala || 1}" data-vp="escala"></div>
          </div>
          <div class="bzAcess">${Object.entries(OPC.acessorio).map(([a, l]) => `<label class="chk"><input type="checkbox" data-va="${a}" ${(P.acessorios || {})[a] ? "checked" : ""}> ${l}</label>`).join("")}</div>
          <div class="bzCores">${Object.entries(COR_ROT).map(([c, l]) => `<label title="${l}"><input type="color" data-vc="${c}" value="${(P.cores || {})[c] || "#888888"}"><span>${l}</span></label>`).join("")}</div>
          <h5>Estilo do render</h5>
          <div class="bzCampos">
            <div><label>Material</label><select data-vr="material">${o(OPC.material, R.material || "vinil")}</select></div>
            <div><label>Luz</label><select data-vr="luz">${o(OPC.luz, R.luz || "suave")}</select></div>
            <div><label>&nbsp;</label><label class="chk"><input type="checkbox" data-vr="contorno" ${R.contorno || (R.material === "desenho" && R.contorno !== false) ? "checked" : ""}> Contorno preto</label></div>
          </div>
        </div>
        <div class="bzVedPrev"><div class="bzImg"><img alt="Prévia do personagem" ${V.img ? `src="${V.img}"` : ""} style="${V.img ? "" : "display:none"}"><div class="velha" style="background:#2a2c33;${V.img ? "display:none" : ""}">Clique em “Ver como fica”</div></div>
          <div class="bzAcoes"><select data-vq="enq"><option value="medio">Meio corpo</option><option value="geral">Corpo inteiro</option><option value="close">Rosto</option></select><button class="btn go" data-vx="ver">🔄 Ver como fica</button></div>
          <div class="mu" data-vmsg></div></div>
      </div>
      ${V.rodape || ""}
    </div>`;
  }
  function vedMontar(k, box, pers, render, pre, rodape) {
    VED[k] = { pers: juntaP(BZ.op.padrao_personagem, pers || {}), render: clone(render || {}), pre: pre || "padrao", img: "", rodape: rodape || "", box, tocado: false };
    box.innerHTML = vedHtml(k);
  }
  function vedAtualiza(k) { const V = VED[k]; const img = V.box.querySelector("img"), velha = V.box.querySelector(".velha"); img.style.display = V.img ? "" : "none"; if (V.img) img.src = V.img; velha.style.display = V.img ? "none" : ""; }
  async function vedPrevia(k) {
    const V = VED[k], msg = V.box.querySelector("[data-vmsg]");
    msg.textContent = "⏳ Gerando a prévia na máquina de render…";
    try {
      const r = await jpost("/api/blender/previa-personagem", { personagem: V.pers, render: V.render, enquadramento: V.box.querySelector("[data-vq=enq]").value });
      V.img = r.url; vedAtualiza(k); msg.textContent = "";
    } catch (e) { msg.textContent = "❌ " + errTxt(e); }
  }
  function vedEventos(box, k, onMudou) {
    box.addEventListener("change", async (ev) => {
      const t = ev.target, V = VED[k]; if (!V || !t.closest(".bzVed")) return;
      if (t.dataset.vp === "pre") {
        const pr = BZ.op.predefinicoes.find((p) => p.id === t.value); if (!pr) return;
        V.pre = pr.id; V.pers = juntaP(BZ.op.padrao_personagem, pr.personagem); V.render = clone(pr.render || {}); V.tocado = true; box.innerHTML = vedHtml(k); onMudou && onMudou(); return vedPrevia(k);
      }
      if (t.dataset.vp) { V.pers[t.dataset.vp] = t.dataset.vp === "escala" ? parseFloat(t.value) : t.value; V.tocado = true; if (t.dataset.vp === "escala") box.querySelector("[data-vp=escala]").previousElementSibling.textContent = `Tamanho (${(+t.value).toFixed(2)}×)`; }
      else if (t.dataset.va) { (V.pers.acessorios = V.pers.acessorios || {})[t.dataset.va] = t.checked; V.tocado = true; }
      else if (t.dataset.vc) { (V.pers.cores = V.pers.cores || {})[t.dataset.vc] = t.value; V.tocado = true; }
      else if (t.dataset.vr) { V.render[t.dataset.vr] = t.type === "checkbox" ? t.checked : t.value; V.tocado = true; if (t.dataset.vr === "material" && t.value === "desenho" && V.render.contorno === undefined) V.render.contorno = true; }
      else return;
      onMudou && onMudou();
    });
    box.addEventListener("click", async (ev) => {
      const b = ev.target.closest("[data-vx]"); if (!b) return; const V = VED[k];
      if (b.dataset.vx === "ver") return vedPrevia(k);
      if (b.dataset.vx === "salvar") {
        const nome = (prompt("Nome da predefinição (ex.: Meu herói de massinha):") || "").trim(); if (!nome) return;
        try { const r = await jpost("/api/blender/predefinicoes", { nome, personagem: V.pers, render: V.render }); BZ.op = r.opcoes; V.pre = r.id; box.innerHTML = vedHtml(k); bzOpcoes(); toast("✅ Predefinição salva: " + nome); }
        catch (e) { toast("❌ " + errTxt(e), 5000); }
      }
      if (b.dataset.vx === "apagar") {
        if (!confirm("Apagar esta predefinição?")) return;
        try { const r = await jpost("/api/blender/predefinicoes/" + encodeURIComponent(V.pre), {}, "DELETE"); BZ.op = r.opcoes; V.pre = "padrao"; box.innerHTML = vedHtml(k); bzOpcoes(); toast("Predefinição apagada."); }
        catch (e) { toast("❌ " + errTxt(e), 5000); }
      }
      if (b.dataset.vx === "aplicar" && onMudou) onMudou("aplicar");
    });
  }

  // ---- editor na tela de criar
  function vedCriarIniciar() {
    const pr = BZ.op.predefinicoes.find((p) => p.id === BZ.pre) || BZ.op.predefinicoes[0];
    vedMontar("criar", el("#bzVedCriar"), pr.personagem, pr.render, pr.id);
  }
  window.__vedCriarReset = () => { delete VED.criar; el("#bzVedCriar").innerHTML = ""; if (el("#bzVisCriar").open) vedCriarIniciar(); };
  el("#bzVisCriar").addEventListener("toggle", () => { if (el("#bzVisCriar").open && BZ.op && !VED.criar) { vedCriarIniciar(); } });
  vedEventos(el("#bzVedCriar"), "criar", () => { });

  // ================================================================== MODELOS .glb (biblioteca)
  async function bzModelos() {
    let l = []; try { l = (await api("/api/blender/modelos")).modelos; } catch (e) { }
    BZ.modelos = l;
    el("#bzModelos").innerHTML = l.length ? l.map((m) => `<div class="bzMod"><b>📦 ${esc(m.id)}</b><span class="mu">${m.mb} MB</span><button class="btn danger" data-bzmd="${esc(m.id)}">🗑</button></div>`).join("") : '<div class="mu">Nenhum modelo ainda.</div>';
  }
  el("#bzModelos").onclick = async (e) => {
    const b = e.target.closest("[data-bzmd]"); if (!b) return;
    if (!confirm("Apagar o modelo “" + b.dataset.bzmd + "” da biblioteca?")) return;
    try { await jpost("/api/blender/modelos/" + encodeURIComponent(b.dataset.bzmd), {}, "DELETE"); } catch (x) { toast("❌ " + errTxt(x), 5000); }
    bzModelos();
  };
  el("#bzModeloSubir").onclick = () => el("#bzModeloArq").click();
  el("#bzModeloArq").onchange = async () => {
    const f = el("#bzModeloArq").files[0]; if (!f) return;
    const msg = el("#bzModeloMsg"); msg.textContent = "⏳ Enviando " + f.name + "…";
    const fd = new FormData(); fd.append("file", f);
    try {
      const r = await fetch("/api/blender/modelos", { method: "POST", body: fd });
      if (!r.ok) throw new Error(await r.text());
      msg.textContent = "✅ Enviado."; toast("✅ Modelo enviado!");
    } catch (x) { msg.textContent = "❌ " + errTxt(x); }
    el("#bzModeloArq").value = ""; bzModelos();
  };

})();
