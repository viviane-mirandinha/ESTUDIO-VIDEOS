#!/usr/bin/env bash
# setup.sh — instala tudo do Estúdio de Vídeos no macOS (Intel ou Apple Silicon) e no Linux (Ubuntu/Debian; nuvem).
# Uso:  bash setup.sh            (SEM_OLLAMA=1 bash setup.sh pula o Ollama; MODELO=qwen2.5:7b muda o modelo)
set -e
PKG="$(cd "$(dirname "$0")" && pwd)"
cd "$PKG"
MODELO="${MODELO:-}"   # vazio = escolhe pela máquina
passo(){ printf '\n==> %s\n' "$1"; }
tem(){ command -v "$1" >/dev/null 2>&1; }
SUDO=""; [ "$(id -u)" != "0" ] && tem sudo && SUDO="sudo"
MAC=0; [ "$(uname -s)" = Darwin ] && MAC=1

passo "1/7 Python, Node.js, ffmpeg e bibliotecas do Chrome"
if [ "$MAC" = 1 ]; then
  # macOS: tudo pelo Homebrew (instala o Homebrew se faltar — ele pede a senha do Mac uma vez)
  if ! tem brew; then
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    [ -x /opt/homebrew/bin/brew ] && eval "$(/opt/homebrew/bin/brew shellenv)"
    [ -x /usr/local/bin/brew ] && eval "$(/usr/local/bin/brew shellenv)"
  fi
  brew install python@3.12 node ffmpeg
  PYBASE="$(brew --prefix python@3.12)/bin/python3.12"
elif tem apt-get; then
  $SUDO apt-get update -qq
  $SUDO apt-get install -y -qq python3 python3-venv python3-pip ffmpeg curl ca-certificates zstd \
    libnss3 libatk-bridge2.0-0 libgbm1 libxkbcommon0 libgtk-3-0 libxcomposite1 libxdamage1 libxrandr2 \
    libpango-1.0-0 libcairo2 fonts-liberation >/dev/null
  $SUDO apt-get install -y -qq libasound2t64 >/dev/null 2>&1 || $SUDO apt-get install -y -qq libasound2 >/dev/null 2>&1 || true
fi
NODE_MAJOR=$(node -v 2>/dev/null | sed 's/v\([0-9]*\).*/\1/' || echo 0)
if [ "$MAC" = 0 ] && [ "${NODE_MAJOR:-0}" -lt 20 ]; then
  curl -fsSL https://deb.nodesource.com/setup_22.x | $SUDO bash - >/dev/null
  $SUDO apt-get install -y -qq nodejs >/dev/null
fi
python3 --version; node --version; ffmpeg -version | head -1

passo "2/7 Ambiente Python (.venv) + bibliotecas"
[ -x "$PKG/.venv/bin/python" ] || "${PYBASE:-python3}" -m venv "$PKG/.venv"
PY="$PKG/.venv/bin/python"
"$PY" -m pip install --upgrade pip -q
"$PY" -m pip install -r "$PKG/requirements.txt" -q

passo "2b/7 Conferência de imagens (CLIP) — faz a imagem bater com a frase do roteiro"
# opcional: sem ele o painel confere só pelo texto (funciona, só é menos preciso)
"$PY" -c "import open_clip, torch" 2>/dev/null || { "$PY" -m pip install -q torch torchvision && "$PY" -m pip install -q open_clip_torch; } || true
"$PY" -c "import open_clip; open_clip.create_model_and_transforms('ViT-B-32', pretrained='laion2b_s34b_b79k'); print('CLIP ok')"   || echo "  Aviso: CLIP não instalou. O painel funciona conferindo as imagens só pelo texto."

passo "3/7 Placa de vídeo NVIDIA"
GPU=0
if tem nvidia-smi && nvidia-smi --query-gpu=name --format=csv,noheader >/dev/null 2>&1; then
  GPU=1; echo "GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader | head -1) (whisper vai usar CUDA)"
  "$PY" -m pip install -q nvidia-cublas-cu12 "nvidia-cudnn-cu12==9.*"
  SITE=$("$PY" -c "import site;print(site.getsitepackages()[0])")
  echo "export LD_LIBRARY_PATH=$SITE/nvidia/cublas/lib:$SITE/nvidia/cudnn/lib:\${LD_LIBRARY_PATH}" > "$PKG/.venv/cuda.env"
else
  echo "Sem GPU NVIDIA: tudo funciona, só a transcrição fica mais lenta (modelo small na CPU)."
fi

VRAM=0; [ "$GPU" = 1 ] && VRAM=$(( $(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1) / 1024 ))
if [ "$MAC" = 1 ]; then RAM=$(( $(sysctl -n hw.memsize) / 1073741824 )); else RAM=$(awk '/MemTotal/{printf "%d", $2/1024/1024+0.5}' /proc/meminfo); fi
# Mac Apple Silicon (M1/M2/M3/M4) com 16 GB+ roda o modelo 7b bem pela memória unificada
[ "$MAC" = 1 ] && [ "$(uname -m)" = arm64 ] && [ "$RAM" -ge 16 ] && VRAM=16
if [ -z "$MODELO" ]; then if [ "$VRAM" -ge 8 ] && [ "$RAM" -ge 16 ]; then MODELO=qwen2.5:7b; else MODELO=llama3.2:3b; fi; fi
echo "Modelo de roteiro escolhido: $MODELO"
echo "export ESTUDIO_OLLAMA_MODELO=$MODELO" > "$PKG/.venv/estudio.env"

passo "4/7 HyperFrames (renderizador) + Chrome headless"
npm install --no-audit --no-fund
"$PKG/node_modules/.bin/hyperframes" browser ensure

passo "5/7 Modelos do Whisper"
"$PY" -c "from faster_whisper import WhisperModel; WhisperModel('small', device='cpu', compute_type='int8'); print('whisper small ok')"
[ "$GPU" = 1 ] && "$PY" -c "from faster_whisper import WhisperModel; WhisperModel('large-v3', device='cpu', compute_type='int8'); print('whisper large-v3 ok')"

passo "6/7 Ollama (roteiro local, zero token)"
if [ -z "$SEM_OLLAMA" ]; then
  if ! tem ollama; then if [ "$MAC" = 1 ]; then brew install ollama; else curl -fsSL https://ollama.com/install.sh | sh; fi; fi
  (pgrep -x ollama >/dev/null || (nohup ollama serve >/dev/null 2>&1 &) ); sleep 3
  ollama pull "$MODELO" || echo "Rode depois: ollama pull $MODELO"
else
  echo "Pulado. Sem Ollama, peça o roteiro ao Claude ou use --roteiro arquivo.txt."
fi

passo "7/7 Pastas"
mkdir -p "$PKG/VIDEOS" "$PKG/estoque/gameplay"
"$PY" -c "import sys; sys.path.insert(0, '$PKG/editor/fabrica'); from lib import ajustes; ajustes.salvar({'modelo_ollama': '$MODELO'}); print('ajustes.json: modelo $MODELO')"
chmod +x "$PKG/iniciar.sh" 2>/dev/null || true
"$PY" -c "import fastapi, uvicorn, edge_tts, faster_whisper, shapely; print('python ok')"

passo "Teste de saúde (vídeo de ~10 s)"
[ -f "$PKG/.venv/cuda.env" ] && . "$PKG/.venv/cuda.env"
. "$PKG/.venv/estudio.env"
"$PY" "$PKG/teste_saude.py" || { echo "Teste de saúde com falha — veja RELATORIO-INSTALACAO.txt"; exit 1; }
printf '\nPRONTO. Para abrir o editor: bash iniciar.sh  (abre http://localhost:8780)\n'
