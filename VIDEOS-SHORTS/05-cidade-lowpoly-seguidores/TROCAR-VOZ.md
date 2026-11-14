1. Copie a voz nova como `voz.mp3` e rode: `.venv\Scripts\python.exe whisper.py voz.mp3 words.json` (PYTHONUTF8=1).
2. `python gerar_edit.py` (alinha o texto exato do roteiro com o whisper e recalcula todos os tempos; recria template.html com o kit de ../_kit).
3. Render: `bash ../_kit/render.sh "<esta pasta>"` (usa o lock) ou o botão Renderizar do editor (localhost:8780).
