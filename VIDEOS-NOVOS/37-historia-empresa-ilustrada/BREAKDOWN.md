# 37 - HISTORIA EMPRESA ILUSTRADA - A história inteira da Nintendo em 1 minuto
- Ref: Built On You / CEOzoned ("The ENTIRE History of X in 20 Minutes"), 16:9.
- Visual: 15 cenas ilustradas em SVG próprio (template.html), bonecos de cabeça branca redonda e olhos de ponto, cenário detalhado por cena, traço levemente tremido (filtro rough) + grão de papel + borda rasgada/vinheta.
- Rótulos escritos à mão entre aspas (Kalam Bold, Google Fonts), ano grande em cada virada de época.
- Régua de anos fixa no rodapé (1889 → 2025) com marcador que anda quando a narração muda de ano.
- Movimento: Ken Burns lento por cena, crossfade curto, bonecos respirando/piscando, objetos animados (braço Ultra Hand estica, chuva, engrenagens, rota JP→EUA, pilha de consoles).
- Voz: edge-tts pt-BR-AntonioNeural +10%; tempos por faster-whisper (words.json); cada rótulo entra na palavra falada.
- Áudio: pad gerado por ffmpeg (musica.wav) com duck + whoosh.wav nas viradas; sem impact/pop.
- Tudo editável em edit.json (textos, anos, tempos de cada rótulo); gerar de novo: python make_edit.py.
