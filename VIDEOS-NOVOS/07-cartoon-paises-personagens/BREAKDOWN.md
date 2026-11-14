# 07 — Cartoon países/personagens — o que foi copiado (ref.: Noticias Ilustradas "FRANCE is in FLAMES!")

1. Países/entidades viram personagens com traço preto grosso, cores chapadas e olhos grandes: França = hexágono tricolor ("l'Hexagone") de boina; Sindicato = feijão vermelho de capacete amarelo; Governo = bloco azul-marinho de gravata; Sistema = caixa cinza com rótulo (gag tipo "DEUDAS").
2. O MESMO desenho do começo ao fim: tudo sai de uma biblioteca SVG única (`C('fr'|'sind'|'gov'|'sis'|'clone')`), com rostos trocáveis (neutro, feliz, raiva, medo, dúvida, surpresa, dorme, nojo, grita, psst) e poses de braço (idle, up, point, aperta, nariz, acena...).
3. Multidão = dezenas de bonequinhos clonados (stagger), que mudam de cor (cinza→vermelho = "toda a categoria").
4. Fundos chapados da referência: céu ciano #38d6ff + grama verde-limão #2ee07a com prédios cinza; plenário de madeira; palco de teatro; mapa da Europa chapado com a França azul-marinho e rótulo manuscrito vermelho + seta.
5. Mistura com foto real (Wikimedia Commons, protesto de 2023 com placa "49.3", lixo em Paris, refinaria): personagem cartoon na frente apontando / tapando o nariz.
6. Rótulos manuscritos (Permanent Marker) vermelhos/pretos e títulos Luckiest Guy ≥ 48px; pouco texto, a gag visual carrega (fogo = poder de fogo, carimbo APROVADA, botão vermelho 49.3, caixa PENSÕES pesando, sistema rachando, teatro, divã).
7. Ritmo: corte seco a cada 2-5 s (21 tomadas), troca de expressão/pose no tempo exato da palavra (words.json do faster-whisper), respiração idle e câmera empurrando devagar; sem legenda, sem SFX.
8. Template local editável: cada tomada é um item `scene` no edit.json (textos e tempos `t_*` relativos editáveis no editor).
