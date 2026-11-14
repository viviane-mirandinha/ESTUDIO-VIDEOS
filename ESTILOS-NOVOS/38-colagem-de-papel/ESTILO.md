# Estilo 38 — Colagem de papel (documentário paper cutout)

Gênero: documentário curto em colagem — fotos antigas recortadas, papel rasgado, fita adesiva, letras de jornal, movimento stop-motion.
Referências: Ordinary Origins (Paper-Cut History) e Fakeplastictree (Collage). Ficha automática: ref/ESTILO-MEDIDO.md (paleta #44372c / #090805 / #b59876, destaque ~#ce9a48, ~6 cortes/min, sem legenda contínua, voz + música baixa).

## Regras
- Fundo: quadro escuro com textura de papel e grão (#15120e → #2a241c), vinheta.
- Fotos: domínio público (Wikimedia), sempre P&B/sépia, recorte com borda branca de 5 px + sombra; papel rasgado (clip-path irregular); 2 tiras de fita nas pontas. Objetos-chave (iceberg) recortados no contorno, sem fita.
- Texto: só rótulos — tiras de papel datilografadas (Courier Prime Bold, 24–40 px; creme, preta, mostarda #e2b33c, vermelha #b8302a) e números/datas grandes em letras "bilhete de resgate" (Anton / DM Serif / Courier, papéis de cores diferentes, girados). Carimbo vermelho para veredito.
- Movimento: tudo entra deslizando em PASSOS (GSAP steps, ~12 qps), cai de cima com leve escala, ou rasga/afunda; tremor contínuo de 1,5 px / 0,45° em cada recorte a 12 qps. Câmera: push lento 4,5% por cena.
- Diagramas também em papel (navio em corte, barras de papel rasgado, mapa de papel com rota tracejada vermelha).
- Ritmo: bloco novo a cada 5–10 s, cortes secos; dentro do bloco um elemento novo a cada 1–2 s, sincronizado com a palavra.
- Áudio: voz pt-BR, drone grave gerado (ffmpeg) com ducking, ruído de papel curto em cada entrada (vol 0,10), whoosh só nas trocas de bloco. Sem impact/pop.
- Arquivos: template_src.html (cenas gancho/partida/iceberg/casco/alaga/botes/parte/balanco/fundo) + make_edit.py. Textos e tempos editáveis nos params de cada cena no editor.
