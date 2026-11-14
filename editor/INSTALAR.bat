@echo off
chcp 65001 >nul
title Estudio de Videos - Instalador
cd /d "%~dp0"
rem Instala o que falta (Python, Node 22+, ffmpeg, Ollama, Claude Code, pacotes Python) e cria o atalho na area de trabalho.
rem   INSTALAR.bat           = instala o que falta
rem   INSTALAR.bat --checar  = so confere, nao instala nada
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0ferramentas\instalar.ps1" %*
echo.
pause
