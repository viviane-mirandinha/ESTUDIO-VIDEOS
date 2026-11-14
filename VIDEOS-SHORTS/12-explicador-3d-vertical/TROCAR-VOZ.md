1. Copie a voz nova como `voz.mp3` e rode `Python311\python.exe whisper.py voz.mp3 words.json "<roteiro .txt>"` (PYTHONUTF8=1).
2. `python gerar_edit.py`: todos os tempos (câmera, pílulas, eventos 3D, legenda) saem do words.json alinhado ao roteiro.
3. Render: `python "<pacote>/editor\build_from_edit.py" . --render`, com o lock kits\.render-lock (ou pelo botão Renderizar do editor).
