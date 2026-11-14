// rede.js — Ajustes → Downloads do YouTube (proxies por lane + login cookies.txt)
(function () {
  const $ = (id) => document.getElementById(id);
  if (!$("ajRede")) return;

  async function api(url, corpo) {
    const r = await fetch(url, corpo === undefined ? {} : { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(corpo) });
    return r.json();
  }

  function el(tag, txt, css) {
    const e = document.createElement(tag);
    if (txt) e.textContent = txt;
    if (css) e.style.cssText = css;
    return e;
  }

  function desenhar(d) {
    $("rGeral").textContent = d.cookies_geral ? "✅ conta conectada" : "— sem conta (normal)";
    $("rLista").value = (d.lanes || []).map((l) => l.proxy).join("\n");
    const box = $("rLanes");
    box.replaceChildren();
    (d.lanes || []).forEach((l) => {
      const linha = el("div", "", "display:flex;gap:8px;align-items:center;flex-wrap:wrap;padding:6px 0;border-top:1px solid #8883");
      linha.append(el("b", "Conexão " + l.n));
      linha.append(el("code", String(l.proxy).replace(/:\/\/([^:@\/]+):[^@]+@/, "://$1:•••@"), "font-size:12px"));
      linha.append(el("span", l.login ? "🔑 com conta" : "⚠ falta o cookies.txt"));
      const t = l.teste;
      if (t) linha.append(el("span", (t.ok ? "✅ " : "❌ ") + t.msg + (t.ip ? " · endereço " + t.ip : ""), "flex-basis:100%;font-size:12px;opacity:.85"));
      const b1 = el("button", "📂 Escolher cookies.txt…"); b1.className = "btn mini"; b1.dataset.rlogin = l.n;
      const b2 = el("button", "Tirar conta"); b2.className = "btn mini"; b2.dataset.rtirar = l.n;
      linha.append(b1, b2);
      box.append(linha);
    });
  }

  function msg(t) { $("rMsg").textContent = t || ""; }

  $("ajRede").addEventListener("toggle", () => { if ($("ajRede").open) api("/api/proxies").then(desenhar); });

  $("rSalvar").onclick = async () => {
    msg("Salvando…");
    const d = await api("/api/proxies", { texto: $("rLista").value });
    desenhar(d);
    msg(`${d.salvos} conexão(ões) salvas` + (d.ignorados && d.ignorados.length ? ` · não entendi estas linhas: ${d.ignorados.join(", ")}` : "") + ". Agora clique em ✅ Testar todas.");
  };

  $("rTestar").onclick = async () => {
    msg("Testando… (até 1 minuto por conexão)");
    $("rTestar").disabled = true;
    try {
      const d = await api("/api/proxies/testar", {});
      desenhar(d);
      msg(d.direto ? (d.direto.ok ? "✅ Sem proxy: " : "❌ Sem proxy: ") + d.direto.msg : "Teste concluído.");
    } finally { $("rTestar").disabled = false; }
  };

  document.addEventListener("click", async (ev) => {
    const b = ev.target.closest("[data-rlogin],[data-rtirar]");
    if (!b || !$("ajRede").contains(b)) return;
    const tirar = b.dataset.rtirar !== undefined;
    const lane = Number(tirar ? b.dataset.rtirar : b.dataset.rlogin);
    msg(tirar ? "Tirando a conta…" : "Escolha o cookies.txt na janela que abriu…");
    const d = await api("/api/proxies/login", tirar ? { lane, remover: true } : { lane });
    desenhar(d);
    msg(d.msg || (tirar ? "Pronto, sem conta." : ""));
  });
})();
