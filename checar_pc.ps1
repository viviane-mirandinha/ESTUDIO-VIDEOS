# checar_pc.ps1 — verifica se este PC roda o Estúdio de Vídeos. NÃO instala nem muda nada.
# Uso: powershell -ExecutionPolicy Bypass -File checar_pc.ps1
# Saída: tabela legível + linha final "VEREDITO=COMPLETO|PARCIAL|INCOMPATIVEL" (o Claude lê essa linha).
$ErrorActionPreference = "SilentlyContinue"
$PKG = Split-Path -Parent $MyInvocation.MyCommand.Path
function Tem($c) { [bool](Get-Command $c -ErrorAction SilentlyContinue) }
$linhas = @(); $faltas = @(); $limites = @()
function L($item, $valor, $ok) { $script:linhas += ("{0,-4} {1,-22} {2}" -f $(if ($ok -eq $true) { "OK" } elseif ($ok -eq $false) { "!!" } else { "--" }), $item, $valor) }

# Sistema
$os = Get-CimInstance Win32_OperatingSystem
$x64 = [Environment]::Is64BitOperatingSystem
$build = [int]$os.BuildNumber
L "Sistema" ("{0} (build {1}, {2})" -f $os.Caption, $build, $(if ($x64) { "64-bit" } else { "32-bit" })) ($x64 -and $build -ge 17763)
if (-not $x64) { $faltas += "Windows 32-bit não é suportado" }

# RAM
$ram = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB)
L "Memória RAM" "$ram GB" ($ram -ge 16)
if ($ram -lt 8) { $faltas += "menos de 8 GB de RAM" } elseif ($ram -lt 16) { $limites += "RAM $ram GB: usar modelo de roteiro menor (llama3.2:3b) e 1 vídeo por vez" }

# Disco (unidade do pacote)
$drv = (Get-Item $PKG).PSDrive.Name
$livre = [math]::Round((Get-PSDrive $drv).Free / 1GB)
L "Disco livre ($drv`:)" "$livre GB" ($livre -ge 30)
if ($livre -lt 15) { $faltas += "menos de 15 GB livres no disco $drv`:" } elseif ($livre -lt 30) { $limites += "só $livre GB livres: instalar sem o Whisper grande e sem clone de voz" }

# GPU
$gpu = $null; $vram = 0
if (Tem nvidia-smi) {
    $q = nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits | Select-Object -First 1
    if ($q) { $p = $q -split ","; $gpu = $p[0].Trim(); $vram = [math]::Round([int]$p[1].Trim() / 1024) }
}
if ($gpu) {
    L "Placa de vídeo" "$gpu ($vram GB)" ($vram -ge 8)
    if ($vram -lt 8) { $limites += "placa com $vram GB: roteiro com modelo menor, clone de voz (Qwen3/Chatterbox) não recomendado" }
} else {
    $outra = (Get-CimInstance Win32_VideoController | Select-Object -First 1).Name
    L "Placa de vídeo" "sem NVIDIA ($outra)" $false
    $limites += "sem placa NVIDIA: tudo funciona mais devagar (Whisper na CPU, roteiro lento ou pelo Claude); clone de voz não roda"
}

# Programas
foreach ($p in @(@("python", "--version"), @("node", "--version"), @("ffmpeg", "-version"), @("ollama", "--version"), @("winget", "--version"), @("git", "--version"))) {
    if (Tem $p[0]) { $v = (& $p[0] $p[1] 2>&1 | Select-Object -First 1) -replace "Copyright.*", ""; L $p[0] "$v".Trim() $true }
    else { L $p[0] "não instalado (o setup instala)" $null }
}
if (-not (Tem winget)) { $limites += "winget ausente: instalar 'App Installer' pela Microsoft Store antes do setup" }

# Internet
$net = $false; try { $net = (Invoke-WebRequest -UseBasicParsing https://registry.npmjs.org -TimeoutSec 8).StatusCode -eq 200 } catch {}
L "Internet" $(if ($net) { "ok" } else { "sem acesso" }) $net
if (-not $net) { $faltas += "sem internet (precisa para instalar e para a voz edge-tts)" }

# Pasta
$acento = $PKG -match "[^\x00-\x7F]"; $onedrive = $PKG -match "OneDrive"
L "Pasta do pacote" $PKG (-not $acento -and -not $onedrive)
if ($acento -or $onedrive) { $limites += "mover a pasta para um caminho simples, sem acento e fora do OneDrive (ex.: C:\ESTUDIO-VIDEOS)" }

Write-Host "`n=== CHECAGEM DO PC — Estúdio de Vídeos ==="
$linhas | ForEach-Object { Write-Host $_ }
if ($faltas.Count) { Write-Host "`nIMPEDE A INSTALAÇÃO:"; $faltas | ForEach-Object { Write-Host " - $_" } }
if ($limites.Count) { Write-Host "`nLIMITAÇÕES (instala, mas com ressalvas):"; $limites | ForEach-Object { Write-Host " - $_" } }
$ver = if ($faltas.Count) { "INCOMPATIVEL" } elseif ($limites.Count) { "PARCIAL" } else { "COMPLETO" }
Write-Host "`nVEREDITO=$ver"
Write-Host "GPU=$(if ($gpu) { 1 } else { 0 }) VRAM_GB=$vram RAM_GB=$ram DISCO_GB=$livre"
