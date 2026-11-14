# Estilo 02 — lowpoly 3d desmontando

Referência: desmontandoomundo · 9:16 720x1280 30 fps
24,1 mil seguidores, só 3 reels e todos 1,3-1,6 mi views (conta nova viral). Criador: Felipe Brandt.

## Visual
- **3D low-poly estilo Blender/jogo mobile**, cores saturadas e luz de dia: casinha com telhado laranja, grama verde vivo, árvores low-poly, boneco simples (camiseta amarela).
- Câmera orbita/aproxima de objetos em **corte (cutaway)**: serpentina de cobre, compressor, telha sobre telha, madeiramento, gotas como bolinhas.
- Partículas (bolinhas laranja = calor, azuis = frio), setas tracejadas, medidor de velocidade.
- Rótulos: pílulas brancas pequenas com bolinha ("• QUARTO: 30 °C", "• GÁS: GELADO") e **textos amarelos inclinados com contorno** ("FERVE A -50 °C", "VÁLVULA DE EXPANSÃO").

## Legenda
- **UMA palavra por vez**, fonte arredondada bold (tipo Lilita One / Fredoka Bold), branca com contorno/sombra escura, centro (~68% da altura).

## Ritmo / voz
- Voz masculina calma, didática, ~190 ppm; vídeos LONGOS pra reel (2-3 min) e mesmo assim 1,3-1,6 mi.
- Gancho 0-3 s: situação doméstica — "Se você tá morrendo de calor e coloca um balde de gelo na frente do ventilador..."
- Explica do jeito "e se a gente montasse do zero" (constrói o aparelho peça por peça). CTA final: **COMENTE "FRIO"** (palavra-gatilho).

## Como replicar (grátis/local)
- Three.js dentro do HyperFrames: primitivas low-poly (Box, Cone, Icosahedron com flatShading), MeshToon/Lambert, sombras suaves; câmera animada por GSAP.
- Cada vídeo exige modelar o objeto do tema (compressor, telhado) proceduralmente → **dificuldade alta** pra ficar bonito; base reaproveitável: casa + grama + árvores + boneco.
