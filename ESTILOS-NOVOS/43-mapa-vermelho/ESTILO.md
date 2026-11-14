# Estilo 43 — MAPA VERMELHO (geopolítico de alerta)

**Vídeo-exemplo:** `VIDEOS-NOVOS/43-mapa-vermelho/` — "Por que o Estreito de Ormuz assusta o mundo" (~66 s, 1280x720).

## Receita
- **Mapa:** vetor escuro (Natural Earth 50m, Mercator), terra #15181e, fronteiras vinho #3a1c22, mar #05070a + grade vermelha 5%.
- **Destaque:** país citado vira vermelho #e3121b com borda brilhando (3 traços: 14 px a 22%, 5 px a 55%, 1,6 px rosado). Entra na palavra exata (faster-whisper).
- **Câmera:** abre no mundo e mergulha no ponto em ~2 s (x1,4 → x110); depois alterna vista regional (x10–x26) e close extremo (x130). Ease power3.inOut.
- **Linhas:** rotas e oleodutos se desenhando (1–1,8 s) com seta; faixas de navegação tracejadas correndo (fluxo); medida branca no gargalo.
- **Números:** Anton 150 px vermelho com brilho, canto inferior, legenda Inter 800 32 px, fonte 24 px cinza; flash vermelho de 0,35 s na entrada.
- **HUD de alerta:** "● ALERTA · ROTA CRÍTICA" piscando 1,2 s, coordenadas no canto, cantoneiras vermelhas, scanlines 22%, vinheta.
- **Rótulos:** país = vermelho com brilho; mar = itálico cinza-azulado espaçado; destaque = caixa vermelha.
- **Título-pergunta** em tela cheia (Anton 118) para virar o capítulo ("ROTAS ALTERNATIVAS?" / "POUCAS.").
- **Ritmo:** troca de vista a cada ~4–8 s (ref: plano médio 8,8 s), cortes secos, whoosh só nas trocas grandes.
- **Áudio:** voz edge-tts pt-BR + drone grave do ffmpeg (55/82 Hz + ruído marrom, tremolo 0,8 Hz) com duck. Sem impact/pop.
- **Roteiro:** gancho com número ("Menos de 40 km"), 1 fato por frase com fonte (EIA etc.), fecha repetindo o número do gancho + CTA.

## Como replicar para outro tema
1. `gen_map.py`: trocar pontos (`pts`) e linhas (`L`) em lon/lat → `python gen_map.py`.
2. Roteiro → edge-tts → `python whisper.py voz16.wav words.json roteiro.txt`.
3. `montar.py`: ajustar tempos/itens (câmera, países ISO-A3, rótulos, números) → `python montar.py`.
4. `build_from_edit.py <pasta> --render` (com o lock de render).
