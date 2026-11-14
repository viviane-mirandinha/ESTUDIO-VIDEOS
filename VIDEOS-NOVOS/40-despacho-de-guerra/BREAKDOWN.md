# 40 · DESPACHO DE GUERRA — breakdown

**Gênero:** despacho / boletim de guerra (história militar contada hora a hora).
**Referências públicas (YouTube):**
- Kings and Generals — "Six-Day War (1967) - Third Arab–Israeli War DOCUMENTARY" — https://youtu.be/hHqJ6pgdE-c (12,5 mi views)
- Real Time History — "Arab-Israeli War 1967 (Six-Day War Documentary)" — https://youtu.be/h7wiiKSYrv8 (1,9 mi views)
Trechos medidos: 0-40 s, meio, últimos 40 s de cada (ref/ref.mp4, ref/ESTILO-MEDIDO.md, ref/sheet_kg.jpg, ref/sheet_rt.jpg).

## O que as referências fazem (medido)
- ~10,5 cortes/min, plano médio 5,6 s; transição dominante = dissolve (28 de 42), quase nenhum corte seco.
- Paleta dessaturada (sat. 0,16): verde-oliva/cinza `#43463d`, papel `#c0bbb1`/`#ecebe7`, destaque ocre `#8e7737`.
- K&G: fotos de arquivo P&B "pousadas" em mesa com papéis/mapas e vinheta forte; mapa verde de terreno com ícones de unidades e setas.
- RTH: mapa bege com territórios coloridos, etiqueta escura no canto sup. esquerdo "LUGAR · ANO", cartão de citação em papel branco sobre footage P&B.
- Texto na tela só em rótulos/destaques (5,8 % dos quadros) — sem legenda contínua. Voz + música baixa (-14,6 LUFS).

## Como recriamos (clean-room, tudo código)
- `template_src.html` (GSAP) → `template.html` (+ litoral da Normandia projetado de `countries50m.geojson` por `mapa.py`).
- Cenas (todas editáveis no edit.json): `titulo`, `despacho` (cartão "DESPACHO Nº" + linha datilografada letra a letra + carimbo de hora vermelho), `mapa` (câmera com zoom, setas azuis desenhando, navios, paraquedistas espalhados, marcadores, foto presa com clipe, carimbo), `foto` (foto Wikimedia PD em P&B/sépia com borda, Ken Burns, legenda datilografada, destaque em papel), `telegrama` (tiras coladas datilografadas), `fim`.
- Fixos: etiqueta "NORMANDIA · 06 JUN 1944" (canto sup. esq., como RTH) e **régua de 24 h** no rodapé com marcador ocre andando de despacho em despacho (assinatura própria do estilo).
- Textura: grão SVG, vinheta, tremor leve de projetor determinístico. Dissolve 0,35 s entre cenas.
- Fontes Google: Courier Prime Bold (máquina de escrever), Oswald Bold (cabeçalhos), Bebas Neue (carimbos).
- Áudio: edge-tts pt-BR-AntonioNeural +12 %; música = drone grave gerado por ffmpeg; whoosh só na entrada de cada despacho.

## Igual × diferente da referência
- **Igual:** narrativa cronológica com hora/data, mapa de front com setas, fotos de arquivo P&B sobre papel com vinheta, etiqueta de lugar+data, paleta oliva/papel/ocre, ritmo ~5 s por plano com dissolves, texto só em destaques.
- **Diferente:** sem footage (só fotos PD + código), mapa desenhado em SVG plano (não 3D/terreno), cartões "DESPACHO Nº" e telegrama datilografados letra a letra, carimbos de hora, régua 24 h; nenhum logo/nome/personagem das referências.

## Fatos (verificados)
- 06/06/1944: 00h16 planadores britânicos (6ª Aerotransportada) pousam junto à ponte do canal de Caen (Pegasus Bridge), tomada em minutos.
- Paraquedistas americanos (82ª e 101ª) lançados de noite, muito dispersos atrás das praias.
- ~7.000 embarcações (6.939 citado pelo D-Day Center); bombardeio naval ao amanhecer.
- 06h30 hora H em Utah e Omaha; Omaha teve a resistência mais dura.
- Britânicos e canadenses a partir das 07h25 (Gold e Sword 07h25, Juno ~07h45-08h).
- Rommel estava na Alemanha (aniversário da esposa, 6 de junho).
- ~156.000 soldados aliados desembarcados no dia; ~10.000 baixas aliadas (estimativa); Caen não foi tomada no dia D.
