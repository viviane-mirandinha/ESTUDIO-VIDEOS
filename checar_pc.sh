#!/usr/bin/env bash
# checar_pc.sh — verifica se esta máquina (Mac ou Linux) roda o Estúdio de Vídeos. NÃO instala nem muda nada.
# Saída: tabela + linha final "VEREDITO=COMPLETO|PARCIAL|INCOMPATIVEL" (o Claude lê essa linha).
PKG="$(cd "$(dirname "$0")" && pwd)"
tem(){ command -v "$1" >/dev/null 2>&1; }
F=(); LIM=()
l(){ printf '%-4s %-22s %s\n' "$1" "$2" "$3"; }
echo "=== CHECAGEM DA MÁQUINA — Estúdio de Vídeos ==="
. /etc/os-release 2>/dev/null; ARCH=$(uname -m)
SO="${PRETTY_NAME:-Linux}"; [ "$(uname -s)" = Darwin ] && SO="macOS $(sw_vers -productVersion)"
l "$([ "$ARCH" = x86_64 ] || [ "$ARCH" = arm64 ] && echo OK || echo '!!')" "Sistema" "$SO ($ARCH)"
[ "$ARCH" = x86_64 ] || [ "$ARCH" = arm64 ] || F+=("arquitetura $ARCH não suportada")
if [ "$(uname -s)" = Darwin ]; then RAM=$(( $(sysctl -n hw.memsize) / 1073741824 )); else RAM=$(awk '/MemTotal/{printf "%d", $2/1024/1024+0.5}' /proc/meminfo); fi
l "$([ "$RAM" -ge 16 ] && echo OK || echo '!!')" "Memória RAM" "$RAM GB"
if [ "$RAM" -lt 8 ]; then F+=("menos de 8 GB de RAM"); elif [ "$RAM" -lt 16 ]; then LIM+=("RAM $RAM GB: modelo de roteiro menor (llama3.2:3b), 1 vídeo por vez"); fi
DISCO=$(df -k "$PKG" | awk 'NR==2{printf "%d", $4/1048576}')
l "$([ "$DISCO" -ge 30 ] && echo OK || echo '!!')" "Disco livre" "$DISCO GB"
if [ "$DISCO" -lt 15 ]; then F+=("menos de 15 GB livres"); elif [ "$DISCO" -lt 30 ]; then LIM+=("só $DISCO GB livres: sem Whisper grande e sem clone de voz"); fi
GPU=0; VRAM=0
if tem nvidia-smi && Q=$(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits 2>/dev/null | head -1) && [ -n "$Q" ]; then
  GPU=1; NOME=${Q%%,*}; VRAM=$(( ${Q##*,} / 1024 ))
  l "$([ "$VRAM" -ge 8 ] && echo OK || echo '!!')" "Placa de vídeo" "$NOME ($VRAM GB)"
  [ "$VRAM" -lt 8 ] && LIM+=("placa com $VRAM GB: modelo menor, clone de voz não recomendado")
else
  if [ "$(uname -s)" = Darwin ] && [ "$ARCH" = arm64 ]; then
    l OK "Chip" "Apple Silicon (roteiro rápido; Whisper na CPU; clone de voz Qwen3/Chatterbox não roda)"
    LIM+=("Mac: Whisper roda na CPU (mais lento que NVIDIA) e o clone de voz não funciona; a voz grátis funciona normal")
  else
  l "!!" "Placa de vídeo" "sem NVIDIA"
  LIM+=("sem placa NVIDIA: tudo mais devagar (Whisper na CPU, roteiro lento ou pelo Claude); clone de voz não roda")
  fi
fi
for p in python3 node ffmpeg ollama git; do
  if tem $p; then l OK "$p" "$($p --version 2>&1 | head -1 | cut -c1-50)"; else l -- "$p" "não instalado (o setup instala)"; fi
done
if curl -fsS -m 8 https://registry.npmjs.org >/dev/null 2>&1; then l OK "Internet" "ok"; else l '!!' "Internet" "sem acesso"; F+=("sem internet"); fi
[ ${#F[@]} -gt 0 ] && { echo; echo "IMPEDE A INSTALAÇÃO:"; printf ' - %s\n' "${F[@]}"; }
[ ${#LIM[@]} -gt 0 ] && { echo; echo "LIMITAÇÕES (instala, mas com ressalvas):"; printf ' - %s\n' "${LIM[@]}"; }
if [ ${#F[@]} -gt 0 ]; then V=INCOMPATIVEL; elif [ ${#LIM[@]} -gt 0 ]; then V=PARCIAL; else V=COMPLETO; fi
echo; echo "VEREDITO=$V"; echo "GPU=$GPU VRAM_GB=$VRAM RAM_GB=$RAM DISCO_GB=$DISCO"
