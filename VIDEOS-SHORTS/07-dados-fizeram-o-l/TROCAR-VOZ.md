1. Copie a voz nova como `voz.mp3` nesta pasta e rode (SEM o roteiro como prompt; com prompt o whisper pulou "quatro famosos..."): `PYTHONIOENCODING=utf-8 PYTHONUTF8=1 .venv\Scripts\python.exe whisper.py voz.mp3 words.json`
2. `python gerar_edit.py` (todo corte, selo, card, linha vermelha, pulso do Cazé e legenda sai de words.json via at("palavra")).
3. `bash render.sh` (ou `python "<pacote>/editor\build_from_edit.py" . --render`).
