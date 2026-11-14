#!/usr/bin/env bash
# Abre o editor do Estúdio de Vídeos em http://localhost:8780 (Mac e Linux)
cd "$(dirname "$0")"
[ -x .venv/bin/python ] || { echo "Falta instalar. Rode primeiro: bash setup.sh"; exit 1; }
[ -f .venv/cuda.env ] && . .venv/cuda.env
[ -f .venv/estudio.env ] && . .venv/estudio.env
export PATH="$PWD/.venv/bin:$PATH"
export PYTHONIOENCODING=utf-8 PYTHONUTF8=1
PORTA="${ESTUDIO_PORTA:-8780}"
if curl -fs -m 2 "http://127.0.0.1:$PORTA/api/config" >/dev/null 2>&1; then
  echo "O editor já está aberto em http://localhost:$PORTA"
  (open "http://localhost:$PORTA" || xdg-open "http://localhost:$PORTA") >/dev/null 2>&1
  exit 0
fi
# abre o navegador quando o servidor responder (a primeira carga pode levar até 1 min)
( for i in $(seq 1 90); do sleep 1; curl -fs -m 2 "http://127.0.0.1:$PORTA/api/config" >/dev/null 2>&1 && break; done
  (open "http://localhost:$PORTA" || xdg-open "http://localhost:$PORTA") >/dev/null 2>&1 ) &
echo "Editor rodando em http://localhost:$PORTA  (Ctrl+C para parar; deixe esta janela aberta)"
exec .venv/bin/python editor/server.py
