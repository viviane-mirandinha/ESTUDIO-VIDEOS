# 39 - ARQUIVO NA MESA - O roubo da Mona Lisa em 1911
- Ref: Red File (youtu.be/udbDpAkUh10) + Dead Signal Investigation (youtu.be/zAoOy28kpqo), 16:9. Trechos em ref/ref.mp4, medição em ref/ESTILO-MEDIDO.md.
- Visual: template local (template_src.html) desenha uma mesa de madeira 3200x2000 (textura gerada por numpy em gen_texturas.py) e coloca nela os objetos do edit.json: pasta, fichas datilografadas, fotos reais (Wikimedia, domínio público), recorte de jornal rasgado, moldura vazia, linha do tempo, notas à mão, carimbos, fios vermelhos, círculo de caneta e 2 lupas com aumento real.
- Câmera: 15 pontos (faixa "Câmera" no editor: x, y, zoom, rot, mov) com easing, zoom lento contínuo e tremor de mão; abre na mesa inteira no fim.
- Luz de luminária + vinheta + grão (img/grao.png); legenda pequena centralizada (frases do roteiro, tempos do faster-whisper); rótulo de arquivo no canto; cartão final com carimbo CASO ENCERRADO.
- Voz: edge-tts pt-BR-AntonioNeural +10% (roteiro.txt); tempos: faster-whisper medium GPU (words.json).
- Áudio: drone grave gerado por ffmpeg (musica.wav) com duck + sfx/whoosh.wav baixo nas viradas de câmera. Sem impact/pop.
- Fatos: 21/08/1911 (segunda, Louvre fechado); Louis Béroud achou só 4 ganchos de ferro no dia 22; museu fechado 1 semana; moldura achada numa escada; Picasso interrogado e Apollinaire preso (inocentes); Vincenzo Peruggia, ex-funcionário que instalava vidros de proteção; escondeu o quadro em Paris por mais de 2 anos; dez/1913 em Florença com Alfredo Geri e o diretor da Uffizi (Giovanni Poggi); preso; volta ao Louvre em jan/1914.
- Tudo editável no edit.json; gerar de novo: python make_edit.py (reescreve edit.json e template.html).
