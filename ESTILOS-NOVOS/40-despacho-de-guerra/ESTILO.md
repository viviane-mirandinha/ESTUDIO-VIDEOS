# 40 — Despacho de guerra: "<batalha>: as primeiras 24 horas" (Kings and Generals / Real Time History)

**Dados:** Kings and Generals (Six-Day War 12,5 mi views, 16 min) e Real Time History (Six-Day War 1,9 mi, 23 min). Guerra contada em ordem cronológica, dia a dia / hora a hora, com mapa de front e fotos de arquivo. Medido: ~10,5 cortes/min (plano ~5,6 s), dissolve como transição padrão, paleta oliva/papel/ocre dessaturada, texto só em rótulos.

## Visual
- **Cartão "DESPACHO Nº N"** em papel envelhecido sobre mesa verde-oliva; linha resumo datilografada letra a letra (Courier Prime) com cursor piscando; **carimbo vermelho com a hora** ("00h16", "06h30 · HORA H", "FIM DO DIA").
- **Mapa de front** (litoral real do countries50m.geojson): mar hachurado, terra oliva, câmera com zoom lento, setas azuis se desenhando até cada alvo, navios em linha com disparos tracejados, paraquedistas espalhados, marcadores com nome, objetivo não tomado em anel vermelho.
- **Fotos de arquivo** (Wikimedia, domínio público) em P&B/sépia com borda de papel e clipe, Ken Burns, legenda datilografada + destaque numérico num papel ("≈ 7.000 EMBARCAÇÕES").
- **Telegrama** com tiras coladas datilografadas para o fato-surpresa.
- Fixos: etiqueta escura "LUGAR · DATA" no canto sup. esq.; **régua de 24 h** no rodapé com marcador ocre que anda a cada despacho.
- Grão, vinheta, tremor leve de projetor; dissolve 0,35 s; whoosh só na entrada dos despachos; drone grave por baixo.

## Nosso template (template.html / make_edit.py, SVG + GSAP)
- Cenas `scene` por `props.cena`: `titulo`, `despacho`, `mapa` (setas/marcas/navios/paras/foto/carimbo com lon-lat), `foto`, `telegrama`, `fim`; itens `tag` e `regua`.
- Outra batalha: rodar `mapa.py` com nova caixa lon/lat, trocar textos/horários/coordenadas em make_edit.py, baixar 4-6 fotos PD.

## Dificuldade: baixa-média
Tudo dado: horas, coordenadas e textos. O trabalho é checar fatos/horários e achar fotos PD. Escala bem para série ("Stalingrado: dia 1", "Pearl Harbor: 24 horas", "Queda de Berlim: os últimos 10 dias").
