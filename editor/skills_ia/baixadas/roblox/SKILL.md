---
name: roblox
description: Faz Shorts/Reels verticais "Roblox story" — animação 3D de bonequinhos de bloco estilo Roblox feita 100% por código no Blender (bpy headless), narrada por criança em 1ª pessoa com voz Kokoro pm_alex (PT-BR, local), legenda palavra por palavra (Montserrat ExtraBold branca, contorno preto, palavra-chave vermelha), música + SFX. Zero IA de vídeo/imagem, zero chave de API, custo zero. Dois modos - (A) formato próprio "Nessa cidade, [regra estranha]", (B) clonar um reel Roblox de referência com a mesma estrutura trocando nomes/detalhes. Use quando o usuário pedir "vídeo roblox", "nessa cidade", "bonequinho roblox", "clonar vídeo roblox", "roblox story", "história roblox animada", ou quando o painel Estúdio de Vídeos mandar `roblox`.
---

# roblox — Shorts "Roblox story" por código (Blender + Kokoro)

Tudo roda no PC: Blender (cenas 3D), Kokoro (voz), faster-whisper (tempo de cada palavra), Pillow (rostos), ffmpeg (legenda + encode). Nenhuma chave de API.

Seja `S` = a pasta onde está este SKILL.md e `R` = `S\pipeline`. Todos os scripts ficam em `R`:
`analisar_ref.py, falar.py, voz.py, tempos.py, tex.py, roblox_lib.py (motor Blender), legenda.py, mix.py, encode.py`,
fonte em `R\fonts`, SFX (CC0) em `R\sfx\<categoria>\<nome>.wav` e um exemplo completo e aprovado em `R\exemplo_estatua\`
(roteiro.txt, cena_estatua.py, sfx.json, vermelhas.txt, palavras.json).

## Requisitos (instalar uma vez)
1. **Python 3.10+** e **ffmpeg** no PATH (o setup do Estúdio já instala).
2. Bibliotecas: `python -m pip install faster-whisper numpy pillow soundfile kokoro-onnx`
   (o setup do Estúdio faz isso no passo opcional "Roblox"; se der erro, rode o comando à mão).
3. **Modelo da voz Kokoro** (~340 MB, grátis, sem conta): `python -X utf8 R\falar.py --baixar`.
   Fica em `%ESTUDIO_KOKORO%` (se definida) ou `~\.cache\kokoro`. Se faltar, o `voz.py` baixa sozinho na 1ª vez.
4. **Blender 4.2 ou mais novo** (grátis): `winget install BlenderFoundation.Blender` ou https://www.blender.org/download/.
   Achar o executável: `where blender` ou `dir "C:\Program Files\Blender Foundation\*\blender.exe"`. Chame-o de `BLENDER` abaixo.
5. Para o modo B (baixar referência por link): `python -m pip install yt-dlp`.

Antes de rodar o Blender, defina a pasta do motor: `set ROBLOX_PIPELINE=S\pipeline` (PowerShell: `$env:ROBLOX_PIPELINE="S\pipeline"`).

## Regras fixas
- Pasta de trabalho por vídeo: `<pasta de vídeos do usuário>\ROBLOX\_trabalho\NN-slug\` (= `P`). Saída: `<pasta de vídeos>\ROBLOX\NN - TITULO.mp4`. Entregar sempre com o caminho completo.
- **Nunca `taskkill /IM blender.exe`** — matar só o PID do próprio processo.
- Nenhuma IA de imagem/vídeo: tudo é Blender + Pillow + ffmpeg.
- **Imagens só em contact sheet** (stills/frames nunca um a um).
- Roteiro sempre passa pela **aprovação do usuário antes da voz**. Escrever o roteiro em arquivo, em PT-BR 100%.
- Sem marca d'água e sem CTA no vídeo (termina seco, convida a rever).
- Python sempre com `-X utf8`.
- Não parar no meio: terminar até o MP4 + folha de conferência olhada.

## Modo A — "Nessa cidade, [regra]" (formato próprio)
1. Se o usuário não deu ideia: propor 3 regras absurdas ("Nessa cidade, se você ___, você ___"), ele escolhe. Sempre história própria.
2. Estrutura (~210 palavras/min, 30-60 s; ~15 falas por 30 s; corte a cada 0,6-2,5 s, mediana 1,2 s):
   regra em 1 linha sobre plano aberto de alguém JÁ pagando → close da causa + close da vítima → 2-3 exemplos da cidade (1-2 planos cada) →
   "E eu? Eu sou o ___" (close + pose snap na palavra) → incidente em 3 cortes rápidos + puf/pop na palavra da consequência →
   escalada em 3 cortes (cada um maior) → a ~60-70%: lugar novo / multidão com 1 slide lento → **música corta 1-2 s** e 1 som-chave na palavra →
   virada (personagem/fato novo entra via puf) → payoff na palavra → final que inverte a 1ª frase, elenco todo vira pra câmera (snap), sting, último close segura 1,5 s.
3. Criança narra em 1ª pessoa, rápido, e FALA as onomatopeias ("Puf!", "Créc!", "Vush!").
4. Formato do arquivo de roteiro: igual a `R\exemplo_estatua\roteiro.txt` (bloco `NARRAÇÃO (pronta pro TTS) ================` 1 fala por linha + `Palavras:` + tabela de CENAS nº | frase | o que aparece).

## Modo B — clonar reel Roblox de referência
1. Analisar a ref: `python -X utf8 R\analisar_ref.py "URL|ref.mp4" <pasta da ref>`
   → ref.mp4, TRANSCRICAO.txt, ref_palavras.json (tempo por palavra), cortes.txt (nº de planos, mediana), sheet1..N.jpg (olhar só as folhas).
2. Escrever ESTILO.md da ref: tabela tempo→plano/câmera/personagens, ritmo, legenda, SFX percebidos.
3. Roteiro = **mesmo gancho, mesma estrutura, mesma quantidade de falas e planos**, fala por fala adaptada pro PT-BR, trocando nomes e detalhes (cidade, objeto, personagem). Mesma ordem de planos, enquadramentos e efeitos (puf, snap, multidão). Aprovação do usuário antes da voz.
4. Seguir os passos técnicos abaixo; na cena.py, um `@shot` por plano da ref, na mesma palavra.

## Passos técnicos (os dois modos)
1. **Voz** (Kokoro pm_alex, speed 1.25, +1,5 semitom; corta em silêncio real < -44 dB com 35 ms de folga; pausas 0,08-0,18 s, 0,30 s antes da virada):
   `python -X utf8 R\voz.py P\roteiro.txt P --virada N` → `P\linhas.txt`, `P\linhas_t.json`, `P\audio\voz.wav` (48 kHz).
   Outras vozes PT: `--voz pf_dora` (feminina) ou `pm_santa`; ouvir amostras com `python -X utf8 R\falar.py --amostras`.
2. **Timestamps por palavra** (faster-whisper large-v3-turbo CPU int8 + difflib contra o roteiro; o modelo baixa sozinho na 1ª vez):
   `python -X utf8 R\tempos.py P` → `P\palavras.json`. Conferir "casadas N/N". TUDO (corte, pose, rosto, puf, SFX) é chaveado pelo **índice da palavra**, nunca por segundo fixo.
3. **Texturas** (rostos Pillow 1024x578: smile grin angry scared shock determined sleep yawn tired blink look_l/r/up frozen_yawn + relógio, rachadura, placa opcional):
   `python -X utf8 R\tex.py P [--placa "1996"]`. Rosto novo → acrescentar bloco `face("nome")` (cópia local do tex.py se for específico).
4. **Blender** (bonecos R6, cenários, planos, snap):
   - Copiar `R\exemplo_estatua\cena_estatua.py` → `P\cena.py`; reescrever cenários/personagens/planos. Ele importa `R\roblox_lib.py` via `ROBLOX_PIPELINE`
     (`Char` R6 com pose/rosto/pedra/props, `box/sph/cyl/cone`, `house/tree/ground/clock/lamp_post`, `set_cam/push`, `day/night/set_pt`, `snapv/backease`, `PUFFS/CRACKEV`, `@shot(indice)`, `run(chars, reset)`).
   - Specs: cores sRGB→linear (`hexc`), grama #3D8C21/#4FA32B, céu #B8D9FF→#3378F7, sol 3,5 a 42°, Standard; fov vertical 32-44 close / 46-56 médio / 58-70 aberto; push-in smoothstep; snap backease 2,2 em 0,12-0,16 s começando 0,05-0,1 s antes da palavra, troca de rosto no mesmo quadro; puf = 9 esferas + 7 estrelas em toda transformação; multidão 40-50 aleatórios. Proibido: motion blur, DOF, Filmic/AgX, plano > 2,5 s, quadro parado.
   - `BLENDER -b --factory-startup --python P\cena.py -- P list` (confere planos/END) → `... -- P stills` (1 quadro por plano a 50%; montar contact sheet com ffmpeg `tile` e olhar só ela; corrigir) →
     render final em 2 processos: `... -- P frames - 0 660` e `... -- P frames - 660 NF` (pula quadros já feitos; re-render = apagar só os PNG do trecho mudado). Em PC sem placa forte, 1 processo só.
   - Duração = fim da voz + ~1,45 s (ou `P\config.json` `{"end": 44.0}`).
5. **Legenda** (1 palavra por vez, Montserrat ExtraBold **146 px**, branca, contorno 13, sombra 4/7, keyword vermelho #EC1C24, centro a **64%** da altura, sem pontuação, Title Case):
   `python -X utf8 R\legenda.py P P\vermelhas.txt` (palavras-chave separadas por vírgula).
6. **Música + SFX** (voz pico -15; música -27 dB RMS cortada 1-2 s no som-chave e some na virada final; whoosh -21..-25, impacto -19, pop -17 + sparkle -24, gasp -22, som-chave -16, sting -17; master -14 LUFS + tanh 0,89):
   montar `P\sfx.json` (modelo `R\exemplo_estatua\sfx.json`: `[categoria/nome, indice_palavra, deslocamento_s, pico_dB]`, SFX de `R\sfx`) e rodar `python -X utf8 R\mix.py P` → `P\audio\mix.wav`.
   Música: pôr um mp3 **sem direitos autorais** (ex.: Biblioteca de Áudio do YouTube) em `P\musica.mp3` e `"musica": "musica.mp3"` no sfx.json; `"musica": ""` = só voz + SFX.
7. **Encode + conferência**: `python -X utf8 R\encode.py P "<pasta de vídeos>\ROBLOX\NN - TITULO.mp4"`
   (libx264 slow crf 19, maxrate 8M, 30 fps, AAC 256k, faststart) → gera `P\conferencia_final.jpg` (12 quadros). Olhar a folha antes de entregar; `--teste 3` encoda só 3 s.

## Lições aprendidas
- SFX Kit **não tem som de pedra** → "créc" = `impacts/impact-light-hard` + `pops/pop-small-out`; som-chave grave = `booms-and-bass/boom-hit-strong`.
- Legenda de 104 px fica pequena no libass → **146 px**.
- faster-whisper: o áudio é lido via ffmpeg→numpy (o decoder `av` quebra em alguns PCs); CPU int8.
- `hide()` recursivo pra props com filhos (controle, coroa, ninho); só `hide_render` no pai não esconde os filhos.
- Render 1080x1920 Eevee 32 samples ≈ 1,5 fps por processo numa placa forte; sempre stills antes do render completo.
- Um vídeo de ~45 s leva ~20-40 min no total (a maior parte é render do Blender).
