// checar_movimento.mjs — GUARDA de movimento dos personagens (zero token, roda em segundos).
// Uso:  node kits/animacao-2d/checar_movimento.mjs <pasta-do-video>        (usa <pasta>/hf/index.html)
// Abre o vídeo num Chrome escondido, anda no tempo quadro a quadro e mede cada personagem
// (todo elemento que tenha .legA/.legB dentro). Reprova se achar qualquer erro da lista abaixo.
import { createRequire } from "module"; import { pathToFileURL } from "url"; import fs from "fs"; import path from "path"; import os from "os";
const require = createRequire(path.resolve("package.json"));
const puppeteer = require("puppeteer-core");
const pasta = path.resolve(process.argv[2] || "."); const html = path.join(pasta, "hf", "index.html");
const FPS = 30;
function achaChrome(){ const base = path.join(os.homedir(), ".cache", "hyperframes", "chrome", "chrome-headless-shell");
  const vs = fs.readdirSync(base).sort().reverse(); for (const v of vs){ const p = path.join(base, v, "chrome-headless-shell-win64", "chrome-headless-shell.exe"); if (fs.existsSync(p)) return p; }
  throw new Error("Chrome do HyperFrames não encontrado em "+base); }
const br = await puppeteer.launch({ executablePath: achaChrome(), args: ["--no-sandbox","--allow-file-access-from-files"] });
const pg = await br.newPage(); const avisos = new Set(); pg.on("pageerror", e => avisos.add("erro de JavaScript: " + e.message)); pg.on("console", m => { const t = m.text(); if (/GSAP target .* not found/.test(t)) avisos.add("animação aponta para peça que não existe: " + t.replace(/ https.*/, "")); }); await pg.setViewport({ width: 1280, height: 720 });
await pg.goto(pathToFileURL(html).href, { waitUntil: "load" });
for (let k = 0; k < 100; k++) { if (await pg.evaluate(() => !!(window.__timelines && window.__timelines.main))) break; await new Promise(r => setTimeout(r, 200)); }
await new Promise(r => setTimeout(r, 1500));
for (const a of await pg.evaluate(() => window.__avisosAnim || [])) avisos.add("posição: " + a);
for (const d of await pg.evaluate(() => { const c = {}; document.querySelectorAll("[id]").forEach(e => c[e.id] = (c[e.id] || 0) + 1); return Object.keys(c).filter(k => c[k] > 1); })) avisos.add("id duplicado no HTML: #" + d + " (a animação vai para o elemento errado; ex.: degradê `${id}c` e personagem `${id}c`)");
const dados = await pg.evaluate((FPS) => {
  const tl = window.__timelines.main; tl.pause(); const dur = tl.duration(); const n = Math.round(dur * FPS);
  const chars = [...document.querySelectorAll("g[id]")].filter(g => g.querySelector(":scope > .esc .legA, :scope .legA")).map(g => g.id);
  const out = {}; chars.forEach(id => out[id] = []);
  for (let i = 0; i <= n; i++) { const t = i / FPS; tl.seek(t, false);
    for (const id of chars) { const g = document.getElementById(id); const sc = g.closest(".sc");
      const vis = sc && parseFloat(getComputedStyle(sc).opacity) > 0.5;
      const esc = g.querySelector(".esc"); const s = Math.abs(gsap.getProperty(esc, "scaleY"));
      out[id].push({ t, vis, x: gsap.getProperty(g, "x"), y: gsap.getProperty(g, "y"), s, leg: gsap.getProperty(g.querySelector(".legA"), "rotation"), cena: sc ? sc.id : "" }); } }
  return out; }, FPS);
await br.close();

const erros = [...avisos].map(a => "página: " + a); const info = [];
for (const [id, pts] of Object.entries(dados)) {
  // pega o trecho visível
  const v = pts.filter(p => p.vis); if (v.length < 6) continue; const cena = v[0].cena;
  const altura = 300 * (v.reduce((a, p) => a + p.s, 0) / v.length);
  let dEscala = 0, vmax = 0, tele = 0, rev = 0, patina = 0, deslize = 0, ultSinal = 0, passos = 0, ultLegSinal = 0, dist = 0, parados = 0, runP = 0, runD = 0;
  for (let i = 1; i < v.length; i++) { const a = v[i - 1], b = v[i]; const dx = b.x - a.x, dy = b.y - a.y; dEscala += Math.abs(b.s - a.s); const vel = Math.hypot(dx, dy) * FPS; dist += Math.hypot(dx, dy);
    vmax = Math.max(vmax, vel); if (Math.hypot(dx, dy) > 70) tele++;
    const sg = Math.sign(dx); if (Math.abs(dx) > 0.6) { if (ultSinal && sg !== ultSinal) rev++; ultSinal = sg; }
    const mexePernas = Math.abs(b.leg) > 4; const andando = vel > 0.35 * altura * 0.12 * FPS / FPS * 1; // > ~12% da altura por segundo
    const vAndar = vel > altura * 0.12;
    if (!vAndar && mexePernas) runP++; else runP = 0; if (runP === Math.round(0.35 * FPS)) patina++;
    if (vAndar && Math.abs(b.leg) < 1.5) runD++; else runD = 0; if (runD === Math.round(0.5 * FPS)) deslize++;
    const ls = Math.sign(b.leg); if (ls && ultLegSinal && ls !== ultLegSinal) passos++; if (ls) ultLegSinal = ls; if (!vAndar) parados++; }
  const distEf = dist + dEscala * 300 * 0.6; passos = passos ? passos + 1 : 0; /* mudanças de sinal + 1 = passos */ const vRel = vmax / altura; const passoComp = passos ? distEf / passos : null;
  info.push(`${cena}/${id}: dist ${dist.toFixed(0)}px, passos ${passos}, ${passoComp ? "comprimento do passo " + (passoComp / altura).toFixed(2) + " alturas" : "parado"}, vel.máx ${vRel.toFixed(2)} alturas/s`);
  if (tele) erros.push(`${cena}: personagem "teleporta" (${tele} saltos bruscos de posição)`);
  if (vRel > 1.0) erros.push(`${cena}: anda rápido demais (${vRel.toFixed(2)} alturas/s — parece corrida; máximo 1,0 no pico)`);
  if (rev) erros.push(`${cena}: muda de direção ${rev}x sem motivo (vai e volta, "sem rumo")`);
  if (patina) erros.push(`${cena}: mexe as pernas PARADO (${patina}x) — patinando no lugar`);
  if (deslize) erros.push(`${cena}: desliza sem mexer as pernas (${deslize}x)`);
  if (passoComp !== null && distEf > altura * .8 && (passoComp / altura < 0.28 || passoComp / altura > 1.1)) erros.push(`${cena}: passos fora de proporção (${(passoComp / altura).toFixed(2)} alturas por passo; esperado 0,28–1,1) — pés deslizando`);
  const f = v[v.length - 1]; if (f.x < -80 || f.x > 1360) erros.push(`${cena}: termina fora da tela (x=${f.x.toFixed(0)})`);
}
console.log("— medidas —"); info.forEach(l => console.log("  " + l));
if (erros.length) { console.log("\nREPROVADO — " + erros.length + " problema(s):"); erros.forEach(e => console.log("  ✗ " + e)); process.exit(1); }
console.log("\nAPROVADO (movimento dos personagens)");
