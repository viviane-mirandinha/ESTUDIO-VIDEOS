1. Copie a voz nova como `voz.mp3` aqui e rode: `PYTHONIOENCODING=utf-8 PYTHONUTF8=1 .venv\Scripts\python.exe whisper.py voz.mp3 words.json roteiro.txt`
2. `python gerar_edit.py` (cortes, etiquetas, aspas, palavras gigantes e legenda saem de words.json via at("palavra")).
3. `bash render.sh` (ou `python "<pacote>/editor\build_from_edit.py" . --render`).
