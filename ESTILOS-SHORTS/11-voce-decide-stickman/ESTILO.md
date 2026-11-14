# ESTILO 11 — VOCÊ DECIDE STICKMAN (história interativa 9:16)
Projeto exemplo: <pacote>\VIDEOS-SHORTS\11-voce-decide-stickman
- Formato: 1080x1920, 55-70 s, série "Parte N", narração 2ª pessoa ("você"), gancho com horário ("São 3:07 da manhã").
- Visual: SVG/GSAP próprio (template.html local, 11 cenas: quarto, celular-chat, porta, maçaneta, relógio, dois celulares, escolha). Boneco branco simples original.
- HUD: NOITE/DIA + relógio grande + local (texto por cena em edit.json → textos.hora/local; params hud_noite/hud_parte).
- Legenda: Montserrat Black 84px maiúscula, amarelo #FFD23F nas keywords, verde #3DDC7A no param leg_verde.
- Áudio: edge-tts pt-BR-AntonioNeural (+6%, -4Hz), drone ffmpeg (ruído marrom + 55/82 Hz) com duck, whoosh.wav 0.16 nas viradas. Sem impact/pop.
- Fim obrigatório: escolha A/B + "comenta" + "Parte 2 depende de você".
- Refazer com outro roteiro: roteiro.txt → edge-tts → whisper.py → corrigir_words.py → editar sc(...) em gerar_edit.py → build_from_edit.py --render (com lock kits\.render-lock).
- Ideias de série: "Dia 17 no bunker", "a porta da garagem abriu sozinha", "o GPS manda virar na estrada de terra".
