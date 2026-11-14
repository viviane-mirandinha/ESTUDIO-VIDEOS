# setup.ps1 — instala tudo do Estúdio de Vídeos no Windows 10/11.
# Uso (PowerShell, dentro da pasta ESTUDIO-VIDEOS):
#   powershell -ExecutionPolicy Bypass -File .\setup.ps1
# Opções: -SemOllama (não instala Ollama/modelo)  -Modelo "qwen2.5:7b"
#         -SemRoblox (pula o passo opcional da skill Roblox: Blender + voz Kokoro, ~700 MB)
#         -Modelo vazio = escolhe sozinho: qwen2.5:7b (NVIDIA 8 GB+ e 16 GB RAM) ou llama3.2:3b (máquina mais fraca)
param([switch]$SemOllama, [switch]$SemRoblox, [string]$Modelo = "")

# "Continue": no PowerShell 5.1 qualquer aviso de programa (npm, pip) no stderr viraria erro fatal com "Stop".
$ErrorActionPreference = "Continue"
$PKG = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $PKG
function Passo($t) { Write-Host "`n==> $t" -ForegroundColor Cyan }
# Erro explicado em português: o que deu errado + o que fazer. O INSTALAR.bat grava tudo em INSTALACAO.log.
$DICAS = @{
    "criar .venv"         = "O Python não ficou pronto. Reinicie o computador e clique de novo em INSTALAR.bat."
    "pip install"         = "Não consegui baixar as bibliotecas do Python. Confira a internet; se tiver antivírus (Avast, McAfee, Norton), pause ele por 15 minutos e rode de novo."
    "npm install"         = "Não consegui instalar o renderizador (Node.js). Reinicie o computador e rode de novo. Se continuar, confira a internet."
    "Chrome do HyperFrames" = "Não consegui baixar o Chrome que renderiza os vídeos. Confira a internet e rode de novo."
    "whisper"             = "Não consegui baixar o modelo de legenda (Whisper, ~500 MB). Confira a internet e o espaço livre no disco (precisa de 15 GB)."
    "teste final"         = "Alguma biblioteca do Python não instalou. Rode o INSTALAR.bat de novo (ele pula o que já está pronto)."
}
function Checar($oque) {
    if ($LASTEXITCODE -ne 0) {
        Write-Host "`nERRO em: $oque (código $LASTEXITCODE)" -ForegroundColor Red
        $d = $DICAS[$oque]; if (-not $d) { $d = "Rode o INSTALAR.bat de novo — ele continua de onde parou." }
        Write-Host "O QUE FAZER: $d" -ForegroundColor Yellow
        Write-Host "Se não resolver, mande o arquivo INSTALACAO.log (está nesta pasta) para o suporte." -ForegroundColor Yellow
        exit 1
    }
}
function Tem($c) { [bool](Get-Command $c -ErrorAction SilentlyContinue) }
function RecarregarPath {
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
}
$ProgressPreference = "SilentlyContinue"   # deixa o Invoke-WebRequest rápido
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$TMPI = Join-Path $env:TEMP "estudio-instaladores"; New-Item -ItemType Directory -Force $TMPI | Out-Null
function AddPathUsuario($dir) {
    $u = [Environment]::GetEnvironmentVariable("Path", "User")
    if (($u -split ";") -notcontains $dir) { [Environment]::SetEnvironmentVariable("Path", (($u.TrimEnd(";") + ";" + $dir).TrimStart(";")), "User") }
    RecarregarPath
}
function Baixar($url, $arq) {
    # curl.exe (vem no Windows 10/11) com novas tentativas; se não der, Invoke-WebRequest
    for ($t = 1; $t -le 4; $t++) {
        if (Get-Command curl.exe -ErrorAction SilentlyContinue) { curl.exe -fsSL --retry 3 --retry-delay 5 -o $arq $url 2>$null }
        if (-not (Test-Path $arq) -or (Get-Item $arq).Length -lt 100000) { try { Invoke-WebRequest $url -OutFile $arq -UseBasicParsing } catch {} }
        if ((Test-Path $arq) -and (Get-Item $arq).Length -gt 100000) { return }
        Write-Host "  download falhou (tentativa $t/4), tentando de novo..."; Start-Sleep 10
    }
    Write-Host "ERRO: não consegui baixar $url — confira a internet e rode o setup de novo." -ForegroundColor Red; exit 1
}
# Instala pelo winget; se o PC não tiver winget, baixa o instalador oficial direto do site do programa.
function Instalar($id) {
    if (Tem winget) {
        winget install --id $id -e --accept-source-agreements --accept-package-agreements --silent | Out-Null
        RecarregarPath
        if ($LASTEXITCODE -eq 0 -or $id -eq "Gyan.FFmpeg") { return }
    }
    Write-Host "  (sem winget: baixando $id do site oficial)"
    switch ($id) {
        "Python.Python.3.12" {
            $f = "$TMPI\python.exe"; Baixar "https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe" $f
            Start-Process $f -ArgumentList "/quiet InstallAllUsers=0 PrependPath=1 Include_launcher=0" -Wait
            AddPathUsuario "$env:LOCALAPPDATA\Programs\Python\Python312"; AddPathUsuario "$env:LOCALAPPDATA\Programs\Python\Python312\Scripts"
        }
        "OpenJS.NodeJS.LTS" {
            $f = "$TMPI\node.msi"; Baixar "https://nodejs.org/dist/v22.11.0/node-v22.11.0-x64.msi" $f
            Start-Process msiexec.exe -ArgumentList "/i `"$f`" /qn /norestart" -Wait
            AddPathUsuario "$env:ProgramFiles\nodejs"
        }
        "Gyan.FFmpeg" {
            $f = "$TMPI\ffmpeg.zip"; Baixar "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip" $f
            $dst = "$env:LOCALAPPDATA\ffmpeg"; Remove-Item -Recurse -Force $dst -ErrorAction SilentlyContinue
            Expand-Archive $f "$TMPI\ffmpeg" -Force
            Move-Item (Get-ChildItem "$TMPI\ffmpeg" -Directory | Select-Object -First 1).FullName $dst
            AddPathUsuario "$dst\bin"
        }
        "Ollama.Ollama" {
            $f = "$TMPI\OllamaSetup.exe"; Baixar "https://ollama.com/download/OllamaSetup.exe" $f
            # sem -Wait: o instalador abre o app do Ollama no fim e o -Wait ficaria esperando ele fechar (nunca)
            Start-Process $f -ArgumentList "/VERYSILENT /NORESTART /SUPPRESSMSGBOXES"
            for ($i = 0; $i -lt 120 -and -not (Test-Path "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"); $i++) { Start-Sleep 5 }
            Start-Sleep 10
            AddPathUsuario "$env:LOCALAPPDATA\Programs\Ollama"
        }
    }
    RecarregarPath
}

Passo "1/7 Python, Node.js e ffmpeg"
if (-not (Tem python) -or -not ((python --version 2>&1) -match "3\.1[0-9]")) { Instalar "Python.Python.3.12" }
if (-not (Tem node)) { Instalar "OpenJS.NodeJS.LTS" }
if (-not (Tem ffmpeg)) { Instalar "Gyan.FFmpeg" }
# Runtime Visual C++ da Microsoft (o Whisper precisa; Windows recém-instalado às vezes não tem)
$vc = Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64" -ErrorAction SilentlyContinue
if (-not $vc -or $vc.Installed -ne 1) {
    Write-Host "  instalando o Visual C++ Redistributable (Microsoft) — se o Windows perguntar, clique Sim"
    $f = "$TMPI\vc_redist.x64.exe"; Baixar "https://aka.ms/vs/17/release/vc_redist.x64.exe" $f
    $adm = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if ($adm) { Start-Process $f -ArgumentList "/install /quiet /norestart" -Wait } else { Start-Process $f -ArgumentList "/install /passive /norestart" -Verb RunAs -Wait }
}
# se o python acabou de ser instalado e ainda não está no PATH desta janela, acha o executável
if (-not (Tem python) -or -not ((python --version 2>&1) -match "3\.1[0-9]")) {
    $cand = @("$env:LOCALAPPDATA\Programs\Python\Python312", "$env:ProgramFiles\Python312", "${env:ProgramFiles(x86)}\Python312") |
        Where-Object { Test-Path "$_\python.exe" } | Select-Object -First 1
    if ($cand) { AddPathUsuario $cand; AddPathUsuario "$cand\Scripts"; $env:Path = "$cand;$cand\Scripts;$env:Path" }
}
foreach ($c in "python", "node", "ffmpeg") { if (-not (Tem $c)) { Write-Host "ERRO: $c não instalou. Feche e abra o PowerShell e rode o setup de novo." -ForegroundColor Red; exit 1 } }
python --version; node --version; (ffmpeg -version | Select-Object -First 1)

Passo "2/7 Ambiente Python (.venv) + bibliotecas"
if (-not (Test-Path "$PKG\.venv\Scripts\python.exe")) { python -m venv "$PKG\.venv"; Checar "criar .venv" }
$PY = "$PKG\.venv\Scripts\python.exe"
& $PY -m pip install --upgrade pip -q
# até 3 tentativas: em PC recém-instalado o pip às vezes cai no meio (erro de memória/antivírus) e na 2ª passa
for ($t = 1; $t -le 3; $t++) { & $PY -m pip install -r "$PKG\requirements.txt" -q; if ($LASTEXITCODE -eq 0) { break }; Write-Host "  pip falhou (tentativa $t/3), tentando de novo..."; Start-Sleep 10 }
Checar "pip install"

Passo "2b/7 Conferência de imagens (CLIP) — faz a imagem bater com a frase do roteiro"
# opcional: sem ele o painel confere só pelo texto (funciona, só é menos preciso). ~800 MB (torch CPU + modelo ViT-B-32)
$clipOk = $false
& $PY -c "import open_clip, torch" 2>$null
if ($LASTEXITCODE -ne 0) {
    & $PY -m pip install -q torch --index-url https://download.pytorch.org/whl/cpu
    & $PY -m pip install -q open_clip_torch
}
& $PY -c "import open_clip; open_clip.create_model_and_transforms('ViT-B-32', pretrained='laion2b_s34b_b79k'); print('CLIP ok')"
if ($LASTEXITCODE -eq 0) { $clipOk = $true } else { Write-Host "  Aviso: CLIP não instalou. O painel funciona, conferindo as imagens só pelo texto. Rode o INSTALAR.bat de novo depois pra tentar." -ForegroundColor Yellow }

Passo "3/7 Placa de vídeo NVIDIA"
$GPU = $false
if (Tem nvidia-smi) {
    $nome = (nvidia-smi --query-gpu=name --format=csv,noheader 2>$null | Select-Object -First 1)
    if ($nome) { $GPU = $true; Write-Host "GPU encontrada: $nome (whisper vai usar CUDA)" }
    $VRAM = [int]((nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>$null | Select-Object -First 1)) / 1024
} else { $VRAM = 0 }
$RAM = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB)
if (-not $Modelo) { $Modelo = if ($GPU -and $VRAM -ge 8 -and $RAM -ge 16) { "qwen2.5:7b" } else { "llama3.2:3b" } }
Write-Host "Modelo de roteiro escolhido: $Modelo"
[Environment]::SetEnvironmentVariable("ESTUDIO_OLLAMA_MODELO", $Modelo, "User"); $env:ESTUDIO_OLLAMA_MODELO = $Modelo
if ($GPU) { & $PY -m pip install -q "nvidia-cublas-cu12" "nvidia-cudnn-cu12==9.*" }
else { Write-Host "Sem GPU NVIDIA: tudo funciona, só a transcrição fica mais lenta (modelo small na CPU)." }

Passo "4/7 HyperFrames (renderizador) + Chrome headless"
npm install --no-audit --no-fund; Checar "npm install"
& "$PKG\node_modules\.bin\hyperframes.cmd" browser ensure; Checar "Chrome do HyperFrames"

Passo "5/7 Modelos do Whisper (transcrição)"
$env:HF_HUB_DISABLE_SYMLINKS_WARNING = "1"
& $PY -c "from faster_whisper import WhisperModel; WhisperModel('small', device='cpu', compute_type='int8'); print('whisper small ok')"; Checar "whisper"
if ($GPU) { & $PY -c "from faster_whisper import WhisperModel; WhisperModel('large-v3', device='cpu', compute_type='int8'); print('whisper large-v3 ok')" }

Passo "6/7 Ollama (roteiro local, zero token)"
if (-not $SemOllama) {
    if (-not (Tem ollama)) { Instalar "Ollama.Ollama" }
    # garante o serviço do Ollama no ar (porta 11434) antes de baixar o modelo
    $noAr = $false; try { $noAr = (Invoke-WebRequest -UseBasicParsing http://127.0.0.1:11434/api/tags -TimeoutSec 3).StatusCode -eq 200 } catch {}
    if (-not $noAr -and (Tem ollama)) {
        Start-Process ollama -ArgumentList "serve" -WindowStyle Hidden
        for ($i = 0; $i -lt 30 -and -not $noAr; $i++) { Start-Sleep 2; try { $noAr = (Invoke-WebRequest -UseBasicParsing http://127.0.0.1:11434/api/tags -TimeoutSec 3).StatusCode -eq 200 } catch {} }
    }
    if ($noAr) { ollama pull $Modelo; if ($LASTEXITCODE -ne 0) { Write-Host "Não baixou o modelo. Depois rode: ollama pull $Modelo" -ForegroundColor Yellow } }
    else { Write-Host "Ollama não respondeu. Abra o app Ollama e rode: ollama pull $Modelo" -ForegroundColor Yellow }
} else { Write-Host "Pulado (-SemOllama). Sem Ollama, peça o roteiro ao Claude ou use --roteiro arquivo.txt." }

Passo "6b/7 (opcional) Skill Roblox: voz Kokoro + Blender"
# OPCIONAL: se falhar, o resto do Estúdio funciona igual (só a skill roblox fica sem rodar). Nunca para o setup.
if (-not $SemRoblox) {
    try {
        # bibliotecas no Python do sistema (a skill roda com "python"): voz Kokoro, legenda/mix, tempo das palavras
        python -m pip install --user -q faster-whisper numpy pillow soundfile kokoro-onnx
        if ($LASTEXITCODE -ne 0) { Write-Host "  Aviso: bibliotecas da skill Roblox não instalaram. Depois rode: python -m pip install --user faster-whisper numpy pillow soundfile kokoro-onnx" -ForegroundColor Yellow }
        else {
            # modelo da voz (~340 MB, grátis, sem conta) em %USERPROFILE%\.cache\kokoro
            $falar = "$PKG\editor\skills_ia\baixadas\roblox\pipeline\falar.py"
            if (Test-Path $falar) {
                python -X utf8 $falar --baixar
                if ($LASTEXITCODE -ne 0) { Write-Host "  Aviso: não baixei a voz Kokoro agora; a skill baixa sozinha no 1º vídeo." -ForegroundColor Yellow }
            }
        }
        # Blender (também usado por maquete-viva e mg-3d-render)
        $blender = Get-ChildItem "$env:ProgramFiles\Blender Foundation\*\blender.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
        if (-not $blender -and -not (Tem blender)) {
            if (Tem winget) {
                Write-Host "  instalando o Blender (grátis, ~400 MB)..."
                winget install --id BlenderFoundation.Blender -e --accept-source-agreements --accept-package-agreements --silent | Out-Null
                if ($LASTEXITCODE -ne 0) { Write-Host "  Aviso: o Blender não instalou. Baixe em https://www.blender.org/download/ (só precisa pras skills 3D)." -ForegroundColor Yellow }
            } else { Write-Host "  Sem winget: baixe o Blender em https://www.blender.org/download/ (só precisa pras skills 3D)." -ForegroundColor Yellow }
        } else { Write-Host "  Blender já instalado." }
    } catch { Write-Host "  Aviso: passo opcional da skill Roblox falhou ($($_.Exception.Message)). O resto do Estúdio funciona normal." -ForegroundColor Yellow }
    $global:LASTEXITCODE = 0
} else { Write-Host "Pulado (-SemRoblox)." }

Passo "6c/7 (opcional) Skills em Node: animate (Playwright + Chromium)"
# OPCIONAL: só a skill "animate" precisa de npm install (pixelfx, huashu-motion e motion-prompt rodam só com Node).
# Se falhar, o resto do Estúdio funciona igual; a skill ensina o comando no 1º uso. Nunca para o setup.
foreach ($sk in @("animate")) {
    $pasta = "$PKG\editor\skills_ia\baixadas\$sk"
    if (-not (Test-Path "$pasta\package.json")) { continue }
    try {
        if (-not (Tem npm)) { Write-Host "  Aviso: sem npm; a skill $sk instala as dependências no 1º uso." -ForegroundColor Yellow; continue }
        Push-Location $pasta
        try {
            npm install --no-audit --no-fund
            if ($LASTEXITCODE -ne 0) { Write-Host "  Aviso: npm install da skill $sk falhou. Depois rode dentro de $pasta : npm install --no-audit --no-fund" -ForegroundColor Yellow }
            else {
                npx playwright install chromium
                if ($LASTEXITCODE -ne 0) { Write-Host "  Aviso: o Chromium do Playwright não baixou. Depois rode dentro de $pasta : npx playwright install chromium" -ForegroundColor Yellow }
                else { Write-Host "  Skill $sk pronta." }
            }
        } finally { Pop-Location }
    } catch { Write-Host "  Aviso: passo opcional da skill $sk falhou ($($_.Exception.Message)). O resto do Estúdio funciona normal." -ForegroundColor Yellow }
}
$global:LASTEXITCODE = 0

Passo "7/7 Pastas"
New-Item -ItemType Directory -Force "$PKG\VIDEOS", "$PKG\estoque\gameplay" | Out-Null
# ajustes.json limpo (sem chaves), com as pastas desta máquina
# grava nos ajustes o modelo que o setup instalou (mantém o resto do ajustes.json, se já existir)
& $PY -c "import sys; sys.path.insert(0, r'$PKG\editor\fabrica'); from lib import ajustes; ajustes.salvar({'modelo_ollama': '$Modelo'}); print('ajustes.json: modelo $Modelo')"
& $PY -c "import fastapi, uvicorn, edge_tts, faster_whisper, shapely; print('python ok')"; Checar "teste final"

Passo "Teste de saúde (vídeo de ~10 s)"
& $PY "$PKG\teste_saude.py"
if ($LASTEXITCODE -ne 0) { Write-Host "Teste de saúde com falha — veja RELATORIO-INSTALACAO.txt" -ForegroundColor Red; exit 1 }
# atalho na área de trabalho (abre o iniciar.bat desta pasta)
try {
    $desk = [Environment]::GetFolderPath("Desktop")
    $ws = New-Object -ComObject WScript.Shell
    $lnk = $ws.CreateShortcut((Join-Path $desk "Estúdio de Vídeos.lnk"))
    $lnk.TargetPath = Join-Path $PKG "iniciar.bat"
    $lnk.WorkingDirectory = $PKG
    $lnk.IconLocation = "$env:SystemRoot\System32\imageres.dll,18"
    $lnk.Description = "Abre o Estúdio de Vídeos (http://localhost:8780)"
    $lnk.Save()
    Write-Host "Atalho criado na área de trabalho: Estúdio de Vídeos" -ForegroundColor Green
} catch { Write-Host "  (não consegui criar o atalho; use o iniciar.bat desta pasta)" -ForegroundColor Yellow }
Write-Host "`nPRONTO. Para abrir o editor: clique duas vezes no atalho 'Estúdio de Vídeos' da área de trabalho (ou no iniciar.bat)." -ForegroundColor Green
