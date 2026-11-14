# 47 — Documentário em alta: pinturas clássicas + cartões serifados (Deep Dive History)

**Dados:** Deep Dive History (EN) — "The Book of Enoch - The Entire Story" 2,5 mi views em 28 dias (~3.700 views/h); "Epic of Gilgamesh" 1,1 mi. Formato "A história inteira de X", 1h-7h, faceless, narração grave e lenta, **sem música**. Mais forte da busca de outubro que não está coberto (09 = fotos de arquivo + cartão de data; 08 = 3D Fern; 27 = stock; 11 = terror escuro).

## Visual
- **Pinturas a óleo clássicas** (românticas/barrocas) em tela cheia com Ken Burns lentíssimo (6-10 % em 6-10 s). Cada pintura fica 5-14 s (medido: 3,9 cortes/min, plano mediano 11,7 s).
- **Cartões pretos** (gradiente radial #161512 → #060606) com serifa clássica em caixa alta e espaçamento largo: "PARTE I" pequeno em cinza + título grande creme. Ficam no silêncio entre blocos (2-2,6 s).
- **Cartão de retrato:** quadro/gravura emoldurado (borda fina creme + filete escuro + sombra) à esquerda, nome em serifa espaçada à direita + descrição em itálico + crédito do quadro embaixo.
- **Citação:** frase entre aspas em caixa alta espaçada sobre a pintura escurecida (brilho .28, blur 3) + fonte ("AUTOR — OBRA, LIVRO, §") menor e cinza.
- **Rótulo de lugar/ano** pequeno no rodapé ("GOLFO DE NÁPOLES · ANO 79"). Sem legenda contínua (medido: 0 % de quadros com legenda).
- Acabamento: vinheta forte + grão leve (6 %). Transições: fade/dissolve e fade pro preto; nada de whoosh/impact.

## Paleta / fontes
- Fundo #060606, texto creme #e9e2d4, secundário #a39a8a, crédito #7d7566. Tons quentes vêm das próprias pinturas (destaque medido #d69b47).
- **Cinzel** (títulos, nomes, citações; letter-spacing .22-.5em) + **Cormorant** (descrições/créditos). Google Fonts, OFL.

## Áudio
- Só voz grave e lenta: edge-tts pt-BR-AntonioNeural rate -12 %, pitch -6 Hz, lowshelf +3 dB, loudnorm -14 LUFS. Pausas de 0,7-0,9 s entre frases e 2,6 s nos capítulos.

## Mídia (custo zero)
- Pinturas e gravuras em domínio público do Wikimedia Commons (busca: "<pintor> <tema>", "<personagem> engraving"). Créditos em img/creditos.json. Temas bons: Antiguidade, Bíblia/mitologia, Roma, Idade Média, catástrofes históricas, exploradores.

## Template (editor)
- `template: generic`; vídeo-teste em VIDEOS-NOVOS/47-documentario-em-alta (gerador `_tmp/gerar.py` com funções `img`, `capitulo`, `framed`, `txt`). Vira "preencher-dados" fácil: lista de blocos {pintura, rótulo, capítulo, retrato, citação}.
- Dificuldade: **fácil** (preencher dados). Gargalo = achar 1 pintura por bloco no Commons.
