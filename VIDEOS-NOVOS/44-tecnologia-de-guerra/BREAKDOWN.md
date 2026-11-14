# 44 — TECNOLOGIA DE GUERRA — Como funciona um porta-aviões (62 s, 1280x720)

Estilo clonado de canais públicos de explicação militar (AiTelly + Science Simplified 4 All): modelo 3D girando, raio-X do casco,
rótulos em caixa âmbar com texto preto + linha guia, contadores de dado técnico, diagrama de alcance com anéis. Tom sério, só voz
(ref medida: sem trilha, -19 LUFS, ~8 cortes/min, plano médio 7 s). Nada de logo/nome dos canais.

| tempo | cena (item) | visual |
|---|---|---|
| 0–7.9 | sc_hero | porta-aviões low-poly girando, wireframe verde → sólido; rótulo ILHA; cota 333 m desenhando |
| 7.9–11.1 | sc_eiffel | vista de cima: Torre Eiffel em wireframe âmbar deitada ao lado (≈330 m vs ≈333 m) |
| 11.1–17.5 | sc_xray | casco em raio-X, 2 reatores brilhando; painel 97.000 t / 2 reatores / 30+ nós |
| 17.5–32.2 | sc_cat | 01 // CATAPULTA: jato no trilho, vapor do reator até a catapulta, lançamento com câmera seguindo + contador 0→265 km/h |
| 32.2–44.1 | sc_land | 02 // CABOS DE PARADA: 4 cabos destacados, gancho baixa, cabo 3 dobra até o gancho, para em ~100 m (contador 240→0) |
| 44.1–51.5 | sc_bolter | 03 // TOQUE E ARREMETIDA: toque, pós-combustão acesa, gancho erra, decola de novo |
| 51.5–57.2 | sc_mapa | 04 // mapa tático: anéis 6 h / 12 h / 24 h (333 / 667 / 1.333 km) com varredura de radar |
| 57.2–62 | sc_final | navio girando em wireframe + "UMA BASE AÉREA QUE MUDA DE LUGAR" |

Editável no editor: textos, rótulos, contadores, anéis e tempos de cena estão no edit.json (template local lê `__EDIT__`);
params `cor_wire`, `cor_hud`, `hud_topo`. Fontes Google: Rajdhani Bold (rótulos/títulos) + Share Tech Mono (HUD).
Áudio: voz edge-tts pt-BR-AntonioNeural (+6%), 3 whoosh suaves nas trocas de capítulo. Sem música (igual à ref), sem impact/pop.
Tempos: faster-whisper large-v3 GPU (words.json). Reproduzir: `python montar_edit.py` + `build_from_edit.py <pasta> --render`.
