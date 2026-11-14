# MODO FÁBRICA — vídeo novo num estilo pronto, sem gastar token

Tudo roda no seu computador (Ollama + edge-tts + faster-whisper + Wikimedia + HyperFrames). Zero Claude.

1. Deixe o Ollama aberto e abra um terminal na pasta `ESTUDIO-VIDEOS/editor/fabrica`.
2. Rode (troque o tema e o nome do canal):
   - Windows: `..\..\.venv\Scripts\python.exe fabrica.py --estilo historia-simples --tema "Como surgiu a primeira moeda do mundo" --canal "SEGREDOS DO DINHEIRO ANTIGO"`
   - Linux: `../../.venv/bin/python fabrica.py --estilo historia-simples --tema "..." --canal "..."`
3. Espere uns 3-10 minutos. O vídeo aparece em `ESTUDIO-VIDEOS/VIDEOS/NN-fabrica-.../` com o nome
   `NN - DD-MM-AAAA - CANAL - TITULO.mp4` e na lista do editor (iniciar.bat) pra mexer em texto/foto e renderizar de novo.
4. Estilos prontos: veja a lista no editor (➕ Pedir vídeo) ou a pasta `editor/fabrica/estilos/`.
   `reddit-story` precisa de vídeos de gameplay livres em `estoque/gameplay`.
5. Opções úteis: `--roteiro meu.txt` (usa seu texto em vez do Ollama), `--voz voz.mp3` (usa sua locução), `--duracao 90`
   (segundos), `--voz-nome pt-BR-FranciscaNeural`, `--musica fundo.mp3`, `--sem-render` (só monta o edit.json).
6. Sempre leia o `roteiro.txt` da pasta antes de publicar: o Ollama pode errar um fato. Créditos das fotos ficam em `img/creditos.json`.
7. Deu erro no meio? Rode o mesmo comando com `--pasta "<pasta do projeto>"` que ele continua de onde parou.
