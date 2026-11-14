1. Copie a voz nova para `voz.mp3` nesta pasta e rode `Python311\python.exe whisper.py voz.mp3 words.json` (PYTHONIOENCODING=utf-8).
2. `python gerar_edit.py` — todos os tempos (câmera, rótulos, adesivos, capítulos, legenda) saem do words.json alinhado ao roteiro via `at("palavra")`.
3. Render: `bash ..\_template-palco3d\render.sh "<esta pasta>" "<nome final>"` (ou build_from_edit.py --render).
