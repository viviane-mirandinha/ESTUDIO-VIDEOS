@echo off
chcp 65001 >nul
title Estudio de Videos - editor
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Falta instalar. Rode primeiro:  powershell -ExecutionPolicy Bypass -File setup.ps1
  pause
  exit /b 1
)
powershell -NoProfile -Command "try{Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8780/api/config -TimeoutSec 2 | Out-Null; exit 0}catch{exit 1}"
if %errorlevel%==0 (
  start "" http://localhost:8780
  exit /b 0
)
set "PATH=%~dp0.venv\Scripts;%PATH%"
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
start "" /min cmd /c "timeout /t 3 >nul & start "" http://localhost:8780"
echo Editor rodando em http://localhost:8780  - minimize esta janela, nao feche.
".venv\Scripts\python.exe" editor\server.py
pause
