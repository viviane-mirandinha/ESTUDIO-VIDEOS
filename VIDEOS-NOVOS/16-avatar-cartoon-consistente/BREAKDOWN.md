# 16 — Avatar cartoon consistente — o que foi copiado (ref.: One Small If "What If You Doubled in Size Every Hour?")

1. UM avatar fixo igual ao da referência: cabeça preta redonda, olhos brancos, moletom verde-limão, calça preta, tênis branco, luvas pretas.
2. Consistência 100%: o avatar é um rig SVG único (`avatar.js`, mestra em `img/avatar-mestre.svg` + `img/avatar-expressoes.svg`); todas as 19 cenas chamam a mesma função. Zero IA.
3. Rig com juntas (quadril, joelho, ombro, cotovelo, cabeça) animadas em GSAP: andar, acenar, espreguiçar, sentar, cair, comer de colher, piscar, 12 expressões (feliz, surpresa, medo, tonto, esforço, grita...).
4. Crescimento por escala: a cada "hora" o avatar cresce em relação ao cenário (quarto → casa → rua → cidade), com a câmera ficando mais aberta.
5. HUD fixo no topo (relógio + HORA N | altura) o vídeo todo, trocando o valor quando a voz fala o número; letterbox preto em cima e embaixo.
6. Cenários suburbanos pastel em vetor chapado (quarto em corte, casas, garagem, rua, cidade), cortes a cada 2-4 s.
7. Cartões de "HORA N" grandes no estilo dos cards de data do Agent Flappy.
8. Gags visuais batendo com a fala: cama quebrando, teto rachando, vizinhos gritando, café numa colherada, cano estourando e rua alagando, carros quicando como brinquedo, balas ricocheteando, 3 quarteirões achatados, voz de trovão, coração = carro, desmaio derrubando prédios, átomo.
