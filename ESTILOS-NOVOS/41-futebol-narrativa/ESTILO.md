# 41 - FUTEBOL NARRATIVA (breakdown do estilo)

Referência principal: Tifo Football by The Athletic - "The Rise & Fall of Ronaldinho" (https://www.youtube.com/watch?v=B7zPPImyTxI, 1,2 mi views).
Secundária: Number 9 - "The Magician Who Brought Street Football..." (https://www.youtube.com/watch?v=ifodIYxyUtg, 3,5 mi) - usa muito lance de jogo (NÃO copiado; só a ideia de palavras grandes em vermelho sobre papel e tabelas de estatística).

Medição (ref/ESTILO-MEDIDO.md): ~11,5 cortes/min, plano médio 5 s, dissolve/corte seco, paleta papel #d4d8d2 + verde-acinzentado + marinho #171519 + terracota #ad5e4b + amarelo #f0cb57, voz + música baixa, -14 LUFS.

## O que foi clonado (estrutura, não identidade)
- Papel quadriculado como fundo base + gráfico "trajetória da carreira" desenhado à mão (abre e fecha o vídeo: subida e queda).
- Foto recortada em duotone com moldura branca e contorno pontilhado (cut-out com borda).
- Cartelas de capítulo em listras diagonais com título gigante condensado amarelo e sombra marinho.
- Faixas de legenda (lower-third) marinho com texto amarelo condensado só nas frases-chave (texto em ~10% dos quadros, sem legenda contínua).
- Números/anos gigantes com sombra deslocada, cards de estatística brancos com borda e sombra dura.
- Campo tático top-down desenhado (linhas se desenhando, jogador = bolinha, setas finta/arrancada).
- Rótulos manuscritos (Caveat) com setas vermelhas.

## O que é próprio (diferente)
- Paleta própria (marinho #1d2541, vermelho #b8463a, amarelo #f2c94c, papel #e8eae3), sem logo/nome/mascote do Tifo.
- Linha do tempo da carreira fixa no topo (marcador amarelo anda por ano).
- Ilustrações 100% SVG/CSS/GSAP; fotos só Wikimedia (domínio público / CC BY), sem lance de partida, sem escudo (retrato recortado acima do escudo, sem logo da revista).
- Carimbo "NINGUÉM PARAVA" e card "0 DERROTAS".

## Cenas (16) - tempos de words.json
abertura(0) > cap.1 passarinho(8.6) > 1933 Pau Grande(10.8) > diagrama das pernas(17.0) > passarinho/apelido(22.4) > cap.2 drible(26.1) > 1953 Botafogo(28.4) > campo tático(31.8) > cap.3 Copas(37.6) > 1958/1962(40.3) > 1962 melhor da Copa(45.0) > Garrincha+Pelé = 0 derrotas(50.2) > cap.4 queda(54.4) > curva da queda/1983/49 anos(56.7) > Estádio Mané Garrincha(64.1) > epitáfio "Alegria do Povo"(66.7-70.5)

## Para replicar com outro jogador
Trocar `params` em make_edit.py (textos, anos, tempos t_*), trocar fotos em img/, gerar voz + words.json, rodar build_from_edit.py --render.
