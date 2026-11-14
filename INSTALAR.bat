@echo off
rem INSTALAR.bat - instalador de 1 clique do Estudio de Videos (Windows 10/11).
rem Instala Python, Node, ffmpeg, Ollama e as bibliotecas; cria o atalho na area de trabalho; abre o painel.
rem Pode rodar quantas vezes quiser: ele pula o que ja esta instalado.
chcp 65001 >nul
title Estudio de Videos - Instalador (nao feche esta janela)
cd /d "%~dp0"
echo.
echo  ==========================================================
echo     ESTUDIO DE VIDEOS - INSTALACAO
echo     Leva de 15 min a 1 hora (depende da internet).
echo     Se o Windows perguntar "Permitir alteracoes?", clique SIM.
echo  ==========================================================
echo.

rem --- checagens antes de comecar (pasta, Windows 64 bits, espaco livre) ---
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$p = (Get-Location).Path; $ok = $true;" ^
  "if (-not [Environment]::Is64BitOperatingSystem) { Write-Host 'ERRO: este Windows e 32 bits. O Estudio precisa de Windows 10/11 de 64 bits.' -ForegroundColor Red; exit 2 }" ^
  "if ($p -match '[^\x00-\x7F]') { Write-Host ('ATENCAO: a pasta tem acento ou caractere especial: ' + $p) -ForegroundColor Yellow; Write-Host 'Isso quebra alguns programas. Mova a pasta ESTUDIO-VIDEOS para C:\ESTUDIO-VIDEOS e rode de novo.' -ForegroundColor Yellow; $ok = $false }" ^
  "if ($p -match 'OneDrive') { Write-Host 'ATENCAO: a pasta esta dentro do OneDrive. Mova para C:\ESTUDIO-VIDEOS (o OneDrive trava arquivos durante a instalacao).' -ForegroundColor Yellow; $ok = $false }" ^
  "if ($p -match 'Program Files|\\Windows\\') { Write-Host 'ATENCAO: nao instale dentro de Program Files/Windows. Use C:\ESTUDIO-VIDEOS.' -ForegroundColor Yellow; $ok = $false }" ^
  "$d = Get-PSDrive ($p.Substring(0,1)); $gb = [math]::Round($d.Free/1GB);" ^
  "if ($gb -lt 15) { Write-Host ('ATENCAO: so ' + $gb + ' GB livres neste disco. Precisa de pelo menos 15 GB.') -ForegroundColor Yellow; $ok = $false }" ^
  "if (-not $ok) { exit 1 } else { Write-Host ('Pasta OK: ' + $p + '  (' + $gb + ' GB livres)') -ForegroundColor Green; exit 0 }"
if %errorlevel%==2 goto :falhou
if %errorlevel%==1 (
  echo.
  choice /C SN /M "Quer continuar mesmo assim (S = sim, N = nao, vou mover a pasta)"
  if errorlevel 2 exit /b 1
)

rem --- instalacao (tudo vai para INSTALACAO.log) ---
powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Transcript -Path '%~dp0INSTALACAO.log' -Force | Out-Null; & '%~dp0setup.ps1'; $c = $LASTEXITCODE; Stop-Transcript | Out-Null; exit $c"
if not %errorlevel%==0 goto :falhou

echo.
echo  ==========================================================
echo     TUDO PRONTO!
echo     Use o atalho "Estudio de Videos" na area de trabalho.
echo     Abrindo o painel agora...
echo  ==========================================================
start "" "%~dp0iniciar.bat"
timeout /t 8 >nul
exit /b 0

:falhou
echo.
echo  ==========================================================
echo     A INSTALACAO PAROU NUM ERRO.
echo     1. Leia a mensagem amarela "O QUE FAZER" logo acima.
echo     2. Faca o que ela diz e clique de novo em INSTALAR.bat
echo        (ele continua de onde parou).
echo     3. Nao resolveu? Mande o arquivo INSTALACAO.log
echo        (esta nesta pasta) para o suporte.
echo  ==========================================================
pause
exit /b 1
