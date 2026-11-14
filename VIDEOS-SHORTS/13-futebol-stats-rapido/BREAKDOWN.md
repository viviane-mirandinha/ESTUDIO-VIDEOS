# 13 — Futebol stats rápido (prime/punch neon, 9:16)
Referências públicas no YouTube: "Messi vs Ronaldo: Who is BETTER in Big Games?" (Factual Animation, youtu.be/uUEM5TCjsAg), que dá a estrutura lado a lado, e "Lionel Messi vs Cristiano Ronaldo" (Football Daily, youtu.be/xOToL-SSkKI), que dá o ritmo. Trechos em ref/ref.mp4; medição em ref/ESTILO-MEDIDO.md.

O que foi copiado:
- A estrutura: jogador à esquerda, VS com a categoria no centro, jogador à direita, e o número de cada um embaixo, entrando quando é falado.
- O visual punch/neon, que veio do gênero pedido e não das refs (as refs são claras e lentas, 4 cortes/min). Fundo preto com grade que desce, scanlines, cada lado com sua cor neon (verde e ciano) e destaque amarelo.
- O ritmo: corte seco a cada 4-10 s, com flash branco de 3 quadros, zoom-punch de 9% e tremor da câmera quando cada número cai.
- Números gigantes (Anton 270-330 px) com contagem, barras que enchem, taças em ícone, selos tortos em caixa alta e placar final 4 x 0.
- Legenda de 2 palavras (Anton 92 px) com contorno preto e palavras-chave em amarelo.
- Silhuetas próprias em SVG, bonecos de traço grosso com "10" nas costas. Nenhuma foto, escudo ou logo.
- Som: voz edge-tts Antonio +18%, batida eletrônica de 128 BPM feita no ffmpeg (com ducking) e 5 whooshes nas viradas.
Para outro tema: editar as cenas no gerar_edit.py (tipos abertura/duelo/solo/divide/final), rodar `python gerar_edit.py` e depois build_from_edit --render.
