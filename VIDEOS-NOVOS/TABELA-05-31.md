# Vídeos de teste ESTILOS NOVOS 05–31 (22/10/2026)

Todos com 1280x720, 30 fps, sem tela preta (blackdetect). Cada pasta tem mp4 + edit.json (estilo + grupo "ESTILOS NOVOS") + sheet.jpg + RELATORIO.json + BREAKDOWN.md.
Painel: http://localhost:8780 → seção "✨ ESTILOS NOVOS" (31 de 31 prontos).
Vozes: 05-14 gravadas pelo usuário (exceto 05, ver abaixo); 15-31 edge-tts Francisca; 26 diálogo com 4 vozes (Narrador Thalita, Mãe Francisca, Pai Antonio grave, Filho Antonio agudo).

| NN | Estilo | Duração | Ponto fraco |
|---|---|---|---|
| 05 | Timeline data a data | 75,3 s | Território inglês (marrom) pouco destacado do relevo na vista geral |
| 06 | Guerra top-down | 85,3 s | Mapa vetorial chapado nas escalas ilha/Pacífico, sem textura de terreno |
| 07 | Cartoon países personagens | 70,4 s | Personagens quase parados; parece slideshow animado |
| 08 | Fern cinemático | 59,2 s | Imagens Flux genéricas/borradas (início escuro CORRIGIDO: fades até o preto removidos, YAVG 2,8 s 13→61) |
| 09 | Desastre fotos + cartões | 66,3 s | Meio (15-48 s) quase só cartão/diagrama; memorial mostra "96" e a fala diz 97 |
| 10 | Caso médico | 68,3 s | "Ressonância" é coração 3D com manchas desenhadas, não exame real |
| 11 | Terror creepy escuro | 59,9 s | Imagens paradas (não vídeo); casa/porão destoam das Flux |
| 12 | Espaço cosmos | 66,0 s | Cenas 3D simples; a de órbitas escura e vazia |
| 13 | Economia gráficos | 79,5 s | Cartão de capítulo repetido 4x; rótulos de apoio pequenos |
| 14 | Tipografia cinética filosofia | 69,6 s | B-roll Pixabay genérico quebra o clima em 2 trechos |
| 15 | Kurzgesagt vetor | 63,2 s | Cenas vazias, astronauta pequeno e repetido |
| 16 | Avatar cartoon consistente | 58,7 s | Boneco sempre de frente, movimento "recorte de papel" |
| 17 | Avatar realista IA | 52,9 s | Avatar com cara de foto IA (~25 anos, não 45); letras sem sentido no certificado |
| 18 | Comentário prints | 57,1 s | Só 2 prints; vira mais texto animado que comentário |
| 19 | Psicologia flat ilustrada | 48,2 s | Personagens pequenos e de frente, andar rígido |
| 20 | Anime fitness | 50,5 s | **Personagem lembra muito o Killua (Hunter x Hunter)**; pose "rosca roubada" errada |
| 21 | Cards produto this or that | 85,0 s | Produtos Flux genéricos; card "parede lisa" quase vazio; pares parecidos |
| 22 | Relatos IA personagem | 47,7 s | Folhas lembram cannabis em vez de tomateiro; flor creme, não amarela |
| 23 | Militar HUD (variante licenciada) | 69,4 s | Clipes de treino não convencem como combate; "poço" parece cabana |
| 24 | Filmes bastidores (só stills) | 64,7 s | Frames do trailer em 360p, moles; capítulo 1 sobre imagem quase preta |
| 25 | Doc regional mapas dados | 63,7 s | Fotos paradas, sem drone; barra do card "1,8%" quase não enche |
| 26 | Reality IA legenda TV | 63,9 s | Imagens paradas; Kontext não faz "vazio" (pipoca cheia) |
| 27 | Doc stock megaprojetos | 57,6 s | "Estrutura leve" mostra tubo IA estranho; mesma arte JetZero 3x |
| 28 | Infográfico escuro dourado | 71,0 s | Silhuetas genéricas por tipo, não do navio real; Seawise Giant borrado |
| 29 | IA notícias robô 3D | 58,3 s | Robô procedural Three.js duro, longe do androide da referência |
| 30 | Experimento formigas (variante cartoon 2D) | 53,1 s | Formigas pequenas na visão geral; "cortam as pernas" vira bolo |
| 31 | Guerra de espécies swarm | 44,0 s | Insetos 2D clip-art; stock de libélula só pousada |

## Observações
- **05:** o arquivo `<sua pasta>/NOVOS ESTILOS\05.mp3` é a locução de Pearl Harbor (igual ao 06), não a da Guerra dos Cem Anos. O vídeo foi feito com TTS Francisca (`05-francisca.mp3`). A versão Pearl Harbor ficou em `05-timeline-ano-a-ano\_pearl-harbor-voz-errada\` (fora do painel). Se regravar o 05, é só trocar a voz.
- **09:** os números "164 depoimentos alterados" e "até 41 com chance de sobreviver" não estão na fala; conferidos (painel independente de 2012), mantidos.
- **ComfyUI local (Flux Kontext dev):** foi o que deu consistência de personagem (17, 20, 22, 26). Pollinations deu 402/503 em série. ComfyUI desligado no fim.
- **Cenas novas reaproveitáveis** em `EDITOR VIDEOS\templates\scenes\` (fern_*, fh-*, cosmos_*, terror_*, eco_*, kin_*, cp_*, tot_*, hud-drone, termico, mapa-tatico, dc_*, kr_*, sw_*, ia29_* etc.).
- **build_from_edit.py** foi alterado pelo vídeo 08 (passa a copiar as imagens dos params de cena pro render; backup `%TEMP%\build_from_edit.bak.py`).
