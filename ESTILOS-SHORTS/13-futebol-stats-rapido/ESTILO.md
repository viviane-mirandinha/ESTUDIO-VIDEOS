# Estilo 13 — Futebol stats rápido (prime/punch neon, 9:16)
Vídeo de exemplo: VIDEOS-SHORTS\13-futebol-stats-rapido (Pelé vs Maradona em números, 53 s)

## Visual
- Fundo preto (#05060a) com grade que desce, scanlines e vinheta. Cada lado tem sua cor neon: A verde #39FF6A, B ciano #3EC8FF. Destaque amarelo #FFE600.
- Duelo: título da categoria no topo (Anton 118 px com sublinhado neon), silhuetas próprias A | VS | B, número gigante com contagem (Anton 270 px com glow), subtítulo, barras que enchem e taças em ícone.
- Selos tortos (-4°) amarelos ou vazados em caixa alta. Placar final "4 x 0" e CTA "COMENTA AÍ".
- Legenda Anton 92 px, 2 palavras, com contorno preto e keywords em amarelo, a 88% da altura.

## Ritmo
- Corte seco a cada 4-10 s: flash branco de 3 quadros e zoom-punch de 9%. Tremor de câmera a cada número que cai, sincronizado com a palavra falada (faster-whisper).
- Ordem: gancho "A VS B / SÓ NÚMEROS", depois 4 duelos, depois 2 fatos solo, depois "dividido" e por fim placar + pergunta + CTA.
- Voz edge-tts Antonio +18%, batida eletrônica de 128 BPM feita no ffmpeg (ducking) e whoosh só nas viradas grandes.

## Como replicar
Copie a pasta 13, troque o roteiro.txt, gere a voz, rode whisper.py, edite a lista `cenas` do gerar_edit.py e rode build_from_edit --render (~45 s de render). Dificuldade baixa: só dados, sem 3D. Fatos com fonte no RELATORIO.json.
