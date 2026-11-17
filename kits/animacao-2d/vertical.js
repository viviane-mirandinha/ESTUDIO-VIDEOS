// formato em pé: título fixo em cima + legenda (grupos de até 4 palavras, vindos de EDIT.legendas) embaixo
(function(){ const r=document.getElementById("root"); const tp=document.createElement("div"); tp.className="vtop"; tp.textContent=EDIT.titulo_tela||""; r.appendChild(tp);
  const ln=document.createElement("div"); ln.className="vln"; r.appendChild(ln);
  const cap=document.createElement("div"); cap.className="vcap"; r.appendChild(cap);
  (EDIT.legendas||[]).forEach(l=>{ const s=document.createElement("span"); s.textContent=l.t; cap.appendChild(s); tl.set(s,{opacity:1},l.s); tl.set(s,{opacity:0},l.e); }); })();
