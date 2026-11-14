# 15 — Vetor flat estilo Kurzgesagt (Kurzgesagt · MinuteEarth · Real Science)

**Dados:** Kurzgesagt (EN) mediana 7,4M views, 30.000 views/h nos 45 d (melhor 61.600) — maior views/hora de toda a mineração. MinuteEarth mediana 229k (parado, 144 v/h). Real Science mediana 1,4M (b-roll, não vetor). Em ES o oficial "En Pocas Palabras" não foi minerado (handle não resolvido). O 10-ciencia-motion do catálogo atual já é "motion 2D de ciência"; este 15 é a variante **vetor flat denso + pássaros/personagens**, que é o que de fato define o Kurzgesagt.

## Visual
- **Vetor flat 100 %:** formas geométricas sem contorno, gradientes suaves, muitos elementos pequenos (partículas, células, planetas) em **profundidade por tamanho/opacidade**. Paleta vibrante por vídeo (roxo+laranja, azul+amarelo, verde+rosa), fundo escuro-saturado (#1b1340, #0c2b4e).
- **Personagens:** pássaros/aves flat (mascote) que reagem; células/vírus com olhinhos; tudo com animação de "respiração" e bounce elástico.
- **Texto:** quase nenhum; quando aparece é sans geométrica (Montserrat/Gotham) branca bold 56-72px, 1-3 palavras, com ícone. Números grandes com contagem.
- **Câmera:** zoom/pan contínuo por um "mundo" grande (cena única com parallax), transições por zoom-through ou wipe de forma.
- **Ritmo:** corte a cada 3-5 s dentro de cenas longas de 15-30 s; animação constante (nada parado); música eletrônica alegre; SFX de whoosh/pop suaves (respeitar: sem impact).

## O que é replicável
A animação de personagem frame a frame é sob-medida. A versão HTML: **cenas-mundo em SVG** (fundo + 20-40 elementos em camadas parallax) + **biblioteca de "atores" SVG** (pássaro com 6 poses, célula, planeta, foguete, pessoa flat) + **GSAP bounce/elastic** em tudo + zoom-through. Dá o look em 80 %; a diferença (acting fino) não é o que segura a retenção, é o tema.

## Template no editor
- `scene: "mundo"` params `{tema: "espaco|corpo|cidade|oceano|celula", paleta, camadas:[...]}` — SVG parallax com drift contínuo.
- `scene: "ator"` params `{tipo: "passaro|celula|planeta|pessoa", pose, emocao, x, y, escala}` — bounce elástico na entrada.
- `scene: "zoom-through"` params `{de, para}` — transição.
- `scene: "numero-contador"` (existe), `text` 64px Montserrat com ícone.
- `scene: "diagrama-flat"` params `{itens:[{icone, rotulo}], ligacoes}`.

## Dificuldade: sob-medida (alta) no 1º vídeo; preencher-dados (média) depois
A biblioteca inicial é grande (5 mundos, 10 atores, 40 ícones flat) e precisa de direção de arte pra não ficar "Canva". Depois, Ollama escolhe `{mundo, atores, ação}` por frase. Referência de views/hora altíssima, mas é também o estilo mais **saturado de cópias** (centenas de canais "Kurzgesagt-like") — vale testar amplo, não apostar tudo.
