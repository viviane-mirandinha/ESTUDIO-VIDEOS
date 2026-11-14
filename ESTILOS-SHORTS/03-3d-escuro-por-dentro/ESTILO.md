# Estilo 03 — 3d escuro por dentro

Referência: comofunciona.br · 9:16 720x1280 30 fps
64,1 mil seguidores, 45 posts. Top: bico da bomba de gasolina 1,5 mi; lava-louças 888 mil; vários 480-650 mil.

## Visual
- **3D estilizado em estúdio escuro** (fundo cinza-chumbo #2A2A2E, chão reflexivo, luz de recorte), objetos do dia a dia em **corte**: bico da bomba, canister de carvão, lava-louças. Materiais lisos (plástico/metal fosco), destaque **amarelo-gema #F2B630** e laranja.
- Topo-esquerda: "breadcrumb" pequeno monoespaçado "COMO FUNCIONA · GASOLINA" + chip "• DENTRO DO BICO" (capítulo atual).
- **Etiquetas-adesivo inclinadas** (rotação -4°): amarelo "NÃO FOI CHUTE", vermelho "NÃO TEM ESCOVA", verde "MENOS ÁGUA QUE NA MÃO", com contorno escuro.
- Valores em display de LCD (R$ 199,07 → R$ 200,00).

## Legenda
- Frase curta (3-6 palavras) em **caixa cinza-escura arredondada**, sans (Inter/Manrope semibold), branco; palavras ainda não ditas em cinza (karaoke). Posição ~73% da altura.

## Ritmo / voz
- Voz masculina conversada, ~185 ppm, ~73 s. Mudança de plano a cada ~4 s (câmera move no mesmo objeto, poucos cortes secos).
- Gancho 0-3 s: cena cotidiana que todo mundo viu — "Sabe quando a bomba dá o clique e o frentista ainda aperta mais um pouquinho...?"
- Estrutura: cena cotidiana → "olha que genial" → mecanismo → "parte estranha" → consequência prática ("Nunca use detergente de pia") → CTA "Segue o Como Funciona".

## Como replicar (grátis/local)
- Three.js (HyperFrames) com geometrias simples (cilindros, caixas, tubos), MeshStandardMaterial, fundo escuro + rim light; cortes via clipping planes. Adesivos/legenda/breadcrumb em HTML.
- **Dificuldade média-alta** (cada tema = um objeto novo); mesmo "template" visual do estilo 04.
