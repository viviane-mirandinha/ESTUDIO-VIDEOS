1. Coloque a voz nova como `voz.mp3` nesta pasta (ex.: copiar `<sua pasta>/SHORTS\01.mp3`).
2. `PYTHONIOENCODING=utf-8 PYTHONUTF8=1 .venv\Scripts\python.exe whisper.py voz.mp3 words.json` e depois `python gerar_edit.py` (todos os tempos saem do words.json; "AVISO palavra nao achada" = a voz falou diferente).
3. Render: `bash render.sh` (draft + voz) ou `python "<pacote>/editor\build_from_edit.py" . --render`.
