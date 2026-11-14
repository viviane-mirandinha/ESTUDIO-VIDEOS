# Instalador 1 clique do Estúdio de Vídeos (chamado pelo INSTALAR.bat).
#   INSTALAR.bat           → instala o que falta (winget), pacotes Python, modelo do Ollama, atalho na área de trabalho e abre o painel
#   INSTALAR.bat --checar  → só confere e mostra o que falta (não instala nada, não cria atalho, não abre nada)
$ErrorActionPreference = "Continue"
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch { }
$CHECAR = ($args | Where-Object { $_ -match '^(--|-|/)checar$' }).Count -gt 0
$PASTA = Split-Path -Parent $PSScriptRoot
$MODELO = "qwen2.5:7b"
$falta = New-Object System.Collections.ArrayList

function Titulo($t) { Write-Host ""; Write-Host "== $t ==" -ForegroundColor Cyan }
function Ok($t) { Write-Host "  [OK]    $t" -ForegroundColor Green }
function Ruim($t) { Write-Host "  [FALTA] $t" -ForegroundColor Yellow }
function Info($t) { Write-Host "          $t" -ForegroundColor Gray }
function Recarregar-Path {
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
    foreach ($p in @("$env:USERPROFILE\.local\bin", "$env:LOCALAPPDATA\Programs\Ollama")) { if ((Test-Path $p) -and ($env:Path -notlike "*$p*")) { $env:Path += ";$p" } }
}
function Achar($nome) { $c = Get-Command $nome -ErrorAction SilentlyContinue | Select-Object -First 1; if ($c) { return $c.Source } return $null }
function Versao($exe, $arg) {
    try { $o = & $exe $arg 2>&1 | Out-String; if ($o -match '(\d+(\.\d+)+)') { return $Matches[1] } } catch { }
    return $null
}
function Winget-Instalar($id, $nome) {
    if ($CHECAR) { Info "Pra instalar: rode o INSTALAR.bat sem --checar (ou: winget install -e --id $id)"; return }
    if (-not (Achar "winget")) {
        Ruim "Não achei o winget (Instalador de Aplicativo do Windows). Instale pela Microsoft Store: 'Instalador de Aplicativo' e rode de novo."
        return
    }
    Write-Host "  Instalando $nome (pode demorar uns minutos)..." -ForegroundColor White
    winget install -e --id $id --accept-source-agreements --accept-package-agreements --silent
    Recarregar-Path
}

Write-Host ""
Write-Host "  ESTÚDIO DE VÍDEOS — INSTALADOR" -ForegroundColor White
Write-Host "  Pasta: $PASTA" -ForegroundColor Gray
if ($CHECAR) { Write-Host "  Modo SÓ CHECAR: nada vai ser instalado nem mudado." -ForegroundColor Yellow }
Recarregar-Path

# ---------------------------------------------------------------- Python 3.10+
Titulo "Python"
$py = Achar "python"
$pv = if ($py -and $py -notlike "*WindowsApps*") { Versao $py "--version" } else { $null }   # o "python" da Microsoft Store é só um atalho que abre a loja
if ($pv -and [version]$pv -ge [version]"3.10") { Ok "Python $pv" }
else {
    Ruim "Python 3.10 ou mais novo"; [void]$falta.Add("Python")
    Winget-Instalar "Python.Python.3.12" "Python 3.12"
    $py = Achar "python"; $pv = if ($py) { Versao $py "--version" } else { $null }
    if ($pv) { Ok "Python $pv instalado" ; $falta.Remove("Python") }
}

# ---------------------------------------------------------------- Node.js 22+
Titulo "Node.js (22 ou mais novo)"
$node = Achar "node"; $nv = if ($node) { Versao $node "--version" } else { $null }
if ($nv -and [int]($nv.Split(".")[0]) -ge 22) { Ok "Node.js $nv" }
else {
    if ($nv) { Ruim "Node.js $nv é antigo — precisa da 22 ou mais nova" } else { Ruim "Node.js" }
    [void]$falta.Add("Node.js")
    Winget-Instalar "OpenJS.NodeJS.LTS" "Node.js LTS"
    $node = Achar "node"; $nv = if ($node) { Versao $node "--version" } else { $null }
    if ($nv -and [int]($nv.Split(".")[0]) -ge 22) { Ok "Node.js $nv instalado"; $falta.Remove("Node.js") }
}

# ---------------------------------------------------------------- ffmpeg
Titulo "ffmpeg (corta e junta vídeo)"
$ff = Achar "ffmpeg"; $fv = if ($ff) { Versao $ff "-version" } else { $null }
if ($ff -and (Achar "ffprobe")) { Ok "ffmpeg $fv" }
else {
    Ruim "ffmpeg"; [void]$falta.Add("ffmpeg")
    Winget-Instalar "Gyan.FFmpeg" "ffmpeg"
    if (Achar "ffmpeg") { Ok "ffmpeg instalado (se o painel não achar, feche e abra de novo)"; $falta.Remove("ffmpeg") }
}

# ---------------------------------------------------------------- Ollama + modelo
Titulo "Ollama (IA grátis que roda no seu PC)"
$ol = Achar "ollama"
if ($ol) { Ok ("Ollama " + (Versao $ol "--version")) }
else {
    Ruim "Ollama"; [void]$falta.Add("Ollama")
    Winget-Instalar "Ollama.Ollama" "Ollama"
    $ol = Achar "ollama"
    if ($ol) { Ok "Ollama instalado"; $falta.Remove("Ollama") }
}
if ($ol) {
    $lista = ""
    try { $lista = & $ol list 2>&1 | Out-String } catch { }
    if ($lista -match [regex]::Escape($MODELO)) { Ok "Modelo $MODELO baixado" }
    elseif ($CHECAR) { Ruim "Modelo $MODELO (uns 5 GB)"; [void]$falta.Add("modelo $MODELO"); Info "Pra baixar: ollama pull $MODELO" }
    else {
        Write-Host "  Baixando o modelo $MODELO (uns 5 GB, só uma vez)..." -ForegroundColor White
        & $ol pull $MODELO
        if ($LASTEXITCODE -eq 0) { Ok "Modelo $MODELO baixado" } else { Ruim "Não consegui baixar o modelo agora. Abra o app do Ollama e rode de novo."; [void]$falta.Add("modelo $MODELO") }
    }
}

# ---------------------------------------------------------------- Claude Code
Titulo "Claude Code (faz os Estilos IA)"
$cl = Achar "claude"
if (-not $cl -and (Test-Path "$env:USERPROFILE\.local\bin\claude.exe")) { $cl = "$env:USERPROFILE\.local\bin\claude.exe" }
if ($cl) { Ok ("Claude Code " + (Versao $cl "--version")) }
else {
    Ruim "Claude Code"; [void]$falta.Add("Claude Code")
    if ($CHECAR) { Info "Pra instalar: rode o INSTALAR.bat sem --checar (instalador oficial: claude.ai/install.ps1)" }
    else {
        Write-Host "  Instalando o Claude Code (instalador oficial da Anthropic)..." -ForegroundColor White
        try { Invoke-RestMethod https://claude.ai/install.ps1 | Invoke-Expression } catch { Ruim ("Falhou: " + $_.Exception.Message) }
        Recarregar-Path
        if ((Achar "claude") -or (Test-Path "$env:USERPROFILE\.local\bin\claude.exe")) { Ok "Claude Code instalado"; $falta.Remove("Claude Code") }
    }
}
if ($cl -or -not $falta.Contains("Claude Code")) { Info "1ª vez? Abra o terminal, digite  claude  e entre na sua conta (plano Pro ou superior)." }

# ---------------------------------------------------------------- pacotes Python
Titulo "Pacotes Python do painel"
$req = Join-Path $PASTA "requirements.txt"
$py = Achar "python"
if (-not $py) { Ruim "Sem Python ainda — feche esta janela e rode o INSTALAR.bat de novo." }
elseif ($CHECAR) {
    & $py -c "import fastapi, uvicorn, multipart, yt_dlp, edge_tts, numpy, PIL, qrcode" 2>$null
    if ($LASTEXITCODE -eq 0) { Ok "Pacotes principais instalados" } else { Ruim "Algum pacote Python"; [void]$falta.Add("pacotes Python"); Info "Pra instalar: python -m pip install -r requirements.txt" }
}
else {
    & $py -m pip install --upgrade -q -r $req
    if ($LASTEXITCODE -eq 0) { Ok "Pacotes instalados/atualizados" } else { Ruim "O pip deu erro — confira sua internet e rode de novo."; [void]$falta.Add("pacotes Python") }
}

# ---------------------------------------------------------------- Máquina de Reels (estilos de reels 9:16)
Titulo "Máquina de Reels (estilos de Reels)"
$maqSkill = Join-Path $PASTA ".claude\skills\maquina-de-reels"
$maqCasa  = Join-Path $env:USERPROFILE ".maquina-de-reels"
$maqConf  = Join-Path $maqCasa "config.json"
$maqPy    = if ($py) { $py } else { Achar "python" }
# A skill já vem no pacote (.claude\skills\maquina-de-reels); só precisa instalar o motor
if (-not (Test-Path (Join-Path $maqSkill "SKILL.md"))) {
    Ruim "Skill maquina-de-reels não encontrada em .claude\skills\"; [void]$falta.Add("Máquina de Reels (skill)")
} else {
    Ok "Skill maquina-de-reels presente"
    # Criar junctions dos estilos se não existirem
    $skillsHome = Join-Path $env:USERPROFILE ".claude\skills"
    $estilos = @("clean-branco","editorial-zine","papel-split","pixel-art","simples","selecao-azul","lime-split","tutorial-de-tela","livre")
    foreach ($e in $estilos) {
        $link = Join-Path $skillsHome "maquina-$e"
        if (-not (Test-Path $link)) {
            try { New-Item -ItemType Junction -Path $link -Target $maqSkill -Force | Out-Null } catch { }
        }
    }
    Ok "Junctions dos 9 estilos criadas"
    # Copiar agentes
    $agSrc = Join-Path $maqSkill ".claude\agents"
    $agDst = Join-Path $PASTA ".claude\agents"
    if (Test-Path $agSrc) {
        if (-not (Test-Path $agDst)) { New-Item -ItemType Directory -Force -Path $agDst | Out-Null }
        Get-ChildItem "$agSrc\*.md" | ForEach-Object { Copy-Item $_.FullName (Join-Path $agDst $_.Name) -Force }
        Ok "Agentes (transcritor, diretor, animador, revisor, capista) copiados"
    }
    # Instalar o motor
    if (Test-Path $maqConf) { Ok "Motor da Máquina já instalado" }
    elseif (-not $maqPy) { Ruim "Sem Python — o motor não pode ser instalado agora"; [void]$falta.Add("Máquina de Reels (motor)") }
    elseif ($CHECAR) { Ruim "Motor da Máquina de Reels (~470 MB na 1ª vez)"; [void]$falta.Add("Máquina de Reels (motor)"); Info "Pra instalar: python motor\instalar.py (dentro da skill)" }
    else {
        Write-Host "  Instalando o motor da Máquina de Reels (pode levar alguns minutos)..." -ForegroundColor White
        $instPy = Join-Path $maqSkill "motor\instalar.py"
        & $maqPy $instPy
        if (Test-Path $maqConf) { Ok "Motor da Máquina instalado" } else { Ruim "O motor não terminou de instalar. Rode de novo ou: python motor\instalar.py"; [void]$falta.Add("Máquina de Reels (motor)") }
    }
}

# ---------------------------------------------------------------- atalho na área de trabalho
Titulo "Atalho na área de trabalho"
$desk = [Environment]::GetFolderPath("Desktop")
$lnk = Join-Path $desk "Estúdio de Vídeos.lnk"
$abrir = Join-Path $PASTA "iniciar.bat"
if (Test-Path $lnk) { Ok "Atalho 'Estúdio de Vídeos' já existe" }
elseif ($CHECAR) { Ruim "Atalho 'Estúdio de Vídeos' (vai ser criado ao instalar)" }
else {
    try {
        $s = (New-Object -ComObject WScript.Shell).CreateShortcut($lnk)
        $s.TargetPath = $abrir; $s.WorkingDirectory = $PASTA; $s.WindowStyle = 7   # minimizado: é a janela do servidor
        $s.Description = "Abre o painel Estúdio de Vídeos (http://localhost:8780)"
        $s.IconLocation = "$env:SystemRoot\System32\imageres.dll,18"
        $s.Save(); Ok "Atalho criado: $lnk"
    } catch { Ruim ("Não consegui criar o atalho: " + $_.Exception.Message) }
}

# ---------------------------------------------------------------- resumo
Titulo "Resumo"
if ($falta.Count -eq 0) { Write-Host "  Tudo pronto!" -ForegroundColor Green }
else { Write-Host ("  Falta: " + ($falta -join ", ")) -ForegroundColor Yellow; if (-not $CHECAR) { Info "Se acabou de instalar algo, feche esta janela e rode o INSTALAR.bat de novo." } }
if (-not $CHECAR -and (Test-Path $abrir)) {
    Write-Host ""; Write-Host "  Abrindo o painel no navegador..." -ForegroundColor White
    Start-Process -FilePath $abrir -WorkingDirectory $PASTA -WindowStyle Minimized
}
Write-Host ""
Write-Host "  Dentro do painel: clique em Diagnóstico (Início ou Ajustes) pra conferir tudo, inclusive as chaves." -ForegroundColor Gray
if ($falta.Count -gt 0) { exit 1 } else { exit 0 }
