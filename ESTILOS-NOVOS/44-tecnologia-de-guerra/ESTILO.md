# 44 — Tecnologia de guerra: 3D wireframe + HUD militar (explicação de armas/veículos)

**Dados:** AiTelly "How Aircraft Carrier Works? Nimitz Class" ~1,39M views (13:50); Science Simplified 4 All "What is a Ballistic Missile?" 1,19M views (17:03). Na mesma busca: Wendover "Cities at Sea" 14M e Gravity "Aircraft Carrier Size Comparison" 3,4M → nicho grande e evergreen.

## Visual (sheet-referencias.jpg + ref/ESTILO-MEDIDO.md)
- Modelo 3D do veículo/arma girando; raio-X do casco com partes internas destacadas (amarelo/ciano na ref).
- Rótulos em **caixa amarela/âmbar com texto preto** + linha guia até a peça; passo a passo numerado ("STEP 7" → aqui "01 // CATAPULTA").
- Diagramas de trajetória/alcance com distâncias em km (ref de mísseis) → aqui **anéis de alcance em mapa tático** com varredura de radar.
- Medido: ~8 cortes/min, plano médio 7 s, **só voz** (sem trilha), -19 LUFS, texto só em rótulos/destaques.

## Nossa versão (sem copiar nome/logo)
- Fundo #05080a com grade de oceano verde, wireframe verde #39ff88 sobre sólido cinza, HUD âmbar #ffb000 (cantos, REC, timecode, scanlines).
- Fontes Google: Rajdhani Bold (rótulos/títulos) + Share Tech Mono (HUD/dados).
- Contadores grandes de dado técnico (km/h) e painel de ficha técnica à direita.
- Comparativo de tamanho com objeto famoso em wireframe (Torre Eiffel deitada ao lado do navio).
- Voz séria edge-tts pt-BR, whoosh só na troca de capítulo; sem música, sem impact/pop.

## Template no editor
- `VIDEOS-NOVOS/44-tecnologia-de-guerra/template.html` (template local Three.js) — faixas: `fundo` (cenas por tempo), `rotulos` (text + anchor 3D), `contadores` (from/to/suffix/ramp), `mapa` (anéis km/text), `textos` (HUD genérico). Params: cor_wire, cor_hud, hud_topo. Gerador do edit.json: `montar_edit.py`.
- Para outra arma: trocar o bloco do modelo (navio/jato) e os pontos ANCH; o resto é dado.

## Dificuldade: sob medida no modelo 3D de cada arma; preencher dados no resto
Fatos técnicos SEMPRE com fonte no RELATORIO (zero número inventado); usar "cerca de/≈".
