# Estilo 01 — saga sobrevivencia 2d

Referência: sobreviventeend · 9:16 720x1280 30 fps
5,7 mil seguidores, 22 posts (todos reels, série diária). Mediana do grid ~55 mil views; ep. 1 = 270 mil.

## Visual
- Ilustração **2D flat vetorial** (estilo "explainer" de série): casas, carros, bunker, personagem jovem (Rafa) e vizinha (Lívia) com traço simples, sem contorno grosso, sombras chapadas.
- Paleta: céu areia/pêssego (#E9C9A0), verde-musgo do bunker (#3E4A3D), cinza-chumbo (#2B2F2E), vermelho alerta (#D7262C), amarelo-mostarda (#E8B23A).
- Elementos de apoio: card de celular "ALERTA DE EMERGÊNCIA", gráfico de linha simples (queda de radiação 7 h ÷10 / 2 dias ÷100), cartão de papel "ESTOQUE", calendário com X, rádio às 03:00, selos pequenos vermelhos/amarelos ("15 MIN • QUALQUER ESTRADA", "REGRA DO BUNKER").
- Fim de episódio: tela escura "PARTE 2 / QUEM ESTÁ LÁ FORA?" (gancho pro próximo).

## Legenda
- 1 a 4 palavras por vez, **MAIÚSCULAS condensadas** (tipo Bebas Neue / Oswald Bold), branco em caixa preta translúcida, centro-baixo (~70% da altura).
- Palavra-chave em **vermelho ou amarelo** ("CHUVA RADIOATIVA", "CLARÃO", "SETE HORAS").

## Ritmo / voz
- Voz masculina narrador (TTS natural), ~175-180 palavras/min. Corte de cena a cada ~3-4 s; personagens com animação leve (piscar, bobbing, deslizar).
- Gancho 0-3 s: regra contraintuitiva em 2ª pessoa — "Se a sirene de ataque nuclear tocar, **não pegue o carro**."
- Estrutura: regra → história do personagem → dado técnico com gráfico → virada → "PARTE N" (série). CTA na bio: "Segue e ativa as notificações".

## Como replicar (grátis/local)
- HyperFrames: cenas SVG/CSS flat (casas, carros, bunker) + GSAP. Personagem original desenhado em SVG (2-3 poses) OU Flux Kontext local pra 1 folha de personagem e recortar (rembg).
- Gráficos/cards em HTML. Legenda via words.json (whisper), palavra-chave colorida.
- Dificuldade: **média** (o trabalho é desenhar cenários; dá pra montar biblioteca SVG reaproveitável).
