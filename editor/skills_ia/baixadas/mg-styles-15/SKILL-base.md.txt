---
name: mg-styles-15
description: Base dos 15 estilos de motion graphics do repositório mg-styles-15 (MIT) — Flat Vector, Line Art, Isométrico 2.5D, 3D Render, Quadro a Quadro (line boil), Colagem, Líquido, Morph, Bauhaus, Synthwave/VHS, Aurora e Vidro, Legenda de Reality, Explicador com Adesivos, Pixel Art e HUD Cyberpunk. Tudo feito por código (SVG/Canvas/WebGL/Three.js, Blender só no 3D), renderizado quadro a quadro no Chrome headless + ffmpeg. Use quando uma skill fina `mg-<estilo>` mandar, ou quando o usuário pedir um vídeo em um desses estilos a partir de roteiro/narração (vertical 1080x1920 por padrão, com legenda sincronizada).
---

# MG Styles 15 — base dos 15 estilos de motion graphics

Fonte: https://github.com/Vincentwei1021/mg-styles-15 (licença MIT, commit `49052d80bfaf9fa8412cc9710530e5e95a3b8d8c`).
Vitrine com os 15 filmes: https://vincentwei1021.github.io/mg-styles-15/

Cada estilo do repositório é um **filme de 10 s feito 100% por código**: uma página HTML que desenha qualquer instante `t`
(`window.renderAt(t)`), capturada quadro a quadro no Chrome headless e juntada no ffmpeg (`harness/render.mjs`).
Nada de gerador de imagem/vídeo por IA. Aqui a gente usa esses filmes como **referência de estilo e de código** para fazer
vídeos NOVOS a partir do roteiro/narração do usuário.

## Onde está cada coisa (nesta pasta: `~/.claude/skills/mg-styles-15/`)

| Caminho | O que é |
|---|---|
| `prompts/NN-<estilo>.md` | Prompt completo do estilo (em inglês, com notas em chinês). As seções **Signature features and key techniques** e **Suggested technical route** são OBRIGATÓRIAS: é o que faz o estilo ser reconhecido. |
| `demos/NN-<estilo>/` | Código-fonte do filme original (index.html + JS, `cues.json` com os tempos, `audio.py` da trilha). Use como referência de técnica: copie funções, shaders, easings, pincéis. |
| `harness/render.mjs` | Renderizador determinístico (puppeteer-core + Chrome + ffmpeg). |
| `lib/audio/` | `mgaudio`: síntese de música e SFX por código + 103 samples CC0 (VCSL). |
| `assets/` | Texturas (grão, papel, poeira, washi), HDRI, `fonts/fonts.css` (os arquivos de fonte NÃO vêm no repo). |
| `rubric.md` | Rubrica de avaliação (use para se auto-avaliar antes de entregar). |
| `template.md` | Como escrever um estilo novo. |

| Skill fina | Estilo | Prompt | Demo |
|---|---|---|---|
| `mg-flat-vector` | Flat Vector 2D | `prompts/01-flat-vector.md` | `demos/01-flat-vector/` |
| `mg-line-art` | Line Art (um traço) | `prompts/02-line-art.md` | `demos/02-line-art/` |
| `mg-isometric` | Isométrico 2.5D | `prompts/03-isometric.md` | `demos/03-isometric/` |
| `mg-3d-render` | 3D Render (Blender) | `prompts/04-3d-render.md` | `demos/04-3d-render/` (+ README) |
| `mg-cel-boil` | Quadro a quadro / line boil | `prompts/05-cel-boil.md` | `demos/05-cel-boil/` |
| `mg-collage` | Colagem recortada | `prompts/06-collage.md` | `demos/06-collage/` |
| `mg-liquid` | Motion líquido | `prompts/07-liquid.md` | `demos/07-liquid/` |
| `mg-morph` | Morph de formas | `prompts/08-morph.md` | `demos/08-morph/` |
| `mg-bauhaus` | Geométrico Bauhaus | `prompts/09-bauhaus.md` | `demos/09-bauhaus/` |
| `mg-synthwave` | Synthwave 80s / VHS | `prompts/10-synthwave.md` | `demos/10-synthwave/` |
| `mg-aurora-glass` | Aurora e vidro | `prompts/12-aurora-glass.md` | `demos/12-aurora-glass/` |
| `mg-hanazi` | Legenda de reality (花字) | `prompts/18-hanazi.md` | `demos/18-hanazi/` (já é 9:16) |
| `mg-paperclip` | Explicador com adesivos | `prompts/19-paperclip.md` | `demos/19-paperclip/` |
| `mg-pixel` | Pixel Art 8-bit | `prompts/20-pixel.md` | `demos/20-pixel/` |
| `mg-hud` | HUD Cyberpunk / FUI | `prompts/22-hud.md` | `demos/22-hud/` |

## Fluxo (do roteiro/narração ao `resultado.mp4`)

1. **Ler o estilo.** Abra `prompts/NN-<estilo>.md` inteiro e o código principal de `demos/NN-<estilo>/`. Anote os traços
   obrigatórios (Signature features) e a rota técnica. O "Creative seed" do prompt é só um exemplo de história: troque pela
   história do roteiro do usuário, mantendo os traços.
2. **Narração.**
   - Se o pedido trouxer áudio pronto (ex.: `entrada/narracao.mp3` do ElevenLabs), use EXATAMENTE ele. Duração do vídeo =
     duração do áudio + ~0,5 s de respiro.
   - Se não trouxer, gere a voz como o PEDIDO.md mandar (TTS escolhido no painel).
   - Converta para WAV 48 kHz: `ffmpeg -i entrada/narracao.mp3 -ar 48000 -ac 2 mg/narracao.wav`.
3. **Tempos da fala.** Transcreva com timestamps por palavra (faster-whisper local, `word_timestamps=True`, idioma do
   pedido) e salve `mg/demos/video/fala.json` = `[{"w":"palavra","s":0.12,"e":0.40}, ...]`. Corrija a grafia comparando
   com o roteiro (o texto da legenda tem que bater com o roteiro, sem erro de português).
4. **Cue sheet.** Divida a fala em batidas (uma ideia por cena, 2–5 s cada) e escreva `mg/demos/video/cues.json` com o
   início de cada cena e os "hits" (palavras fortes). Imagem e som leem os mesmos tempos — igual aos `cues.json` dos demos.
   O gancho visual tem que estar no quadro 0 (nunca abrir com tela vazia/preta por mais de 0,3 s).
5. **Montar o projeto de render** (dentro da pasta do pedido):
   ```
   mg/
     harness/            <- copiar de ~/.claude/skills/mg-styles-15/harness/
     assets/             <- copiar de ~/.claude/skills/mg-styles-15/assets/ (texturas + fonts.css)
     package.json        <- copiar de ~/.claude/skills/mg-styles-15/package.json
     demos/video/index.html (+ js/ e assets/ do estilo que precisar)
   ```
   `npm install` dentro de `mg/` (d3, three, opentype.js, simplex-noise, topojson-client, puppeteer-core — o puppeteer-core
   NÃO baixa navegador; usa o Chrome instalado). Os caminhos dentro da página são relativos à raiz `mg/`
   (`/assets/...`, `/node_modules/...`, `/demos/video/...`).
6. **Escrever a composição** `demos/video/index.html`, reaproveitando o código do demo do estilo:
   - `window.DEMO = { width: 1080, height: 1920, fps: 30, duration: <duração do áudio> }` (vertical por padrão; só use
     1920x1080 se o pedido for formato longo/horizontal).
   - `window.renderAt = async (t) => { ... }` desenha o quadro do instante `t` de forma **determinística** (função pura de
     `t`; aleatório só com semente; nada de relógio real, `requestAnimationFrame` livre ou transição CSS disparada por estado).
   - No fim do carregamento: `window.__ready = true`.
   - **Re-layout para vertical**: os demos são 16:9 (menos o 18-hanazi). Não estique — recomponha: elemento herói no terço
     central, texto grande, e respeite a safe zone de Reels (skill `safe-zone-reels`, se existir: topo livre até y 240, base
     a partir de y 1500, laterais 95 px, botões à direita x ≥ 870 entre y 800 e 1500).
   - **Cada cena DEMONSTRA o que a fala diz** (objeto, número, ícone, metáfora visual no estilo), não só texto solto.
   - **Legenda sincronizada** palavra a palavra (ou grupos de 2–4 palavras) lida de `fala.json`, desenhada NO ESTILO
     (pixel font no Pixel Art, mono com cursor no HUD, letreiro com contorno triplo no Hanazi, traço fino no Line Art...),
     palavra atual destacada, dentro da safe zone (faixa y ≈ 1150–1450).
   - Fontes: os arquivos não vêm no repo (`assets/fonts/README.md` lista quais). As latinas são todas Google Fonts (OFL):
     baixe os .ttf de https://github.com/google/fonts para os caminhos de `assets/fonts/fonts.css` que for usar. As CJK
     não são necessárias para texto em português — troque por uma latina equivalente. Nunca deixe cair em fonte de sistema
     sem querer; confira acentos (ã, ç, é).
7. **Prévia antes do render final.** Stills nos tempos-chave:
   `MG_CHROME="C:\Program Files\Google\Chrome\Application\chrome.exe" node harness/render.mjs demos/video --stills 0.5,3,8,15 --scale 0.5`
   (no Windows, se o WebGL falhar, defina também `MG_GPU_ARGS="--use-angle=d3d11 --enable-gpu"`). Junte os stills numa
   folha única (contact sheet com ffmpeg `tile`) antes de olhar — não abra quadro por quadro.
8. **Trilha.** A narração é a voz principal. Música/SFX opcionais e baixos: pode usar `lib/audio` (mgaudio — precisa de
   numpy/scipy/soundfile/numba/pedalboard/pyloudnorm; instale num venv, não no Python global) seguindo o `audio.py` do demo
   do estilo, ou pular a música. Mix final: voz em −14 LUFS, música ~18–22 dB abaixo da voz (ducking), pico ≤ −1 dBTP.
   Gere `mg/mix.wav`.
9. **Render final.**
   `node harness/render.mjs demos/video --audio mix.wav --out ../resultado.mp4 --duration <s> --w 1080 --h 1920`
   (motion blur `--mb 4` só nos estilos que pedem, ex.: Flat Vector e Líquido; Pixel Art e Quadro a Quadro SEM motion blur).
   Use `--workers 2` no máximo (a máquina pode estar renderizando outras coisas).
10. **Conferir** com `ffprobe`: duração = áudio, 1080x1920, 30 fps, áudio AAC presente. Gere uma contact sheet de ~8
    quadros e confira legenda, acentos, nada cortado na borda, nada fora da safe zone. Auto-avalie com `rubric.md`
    (fidelidade ao estilo, movimento, tipografia, som) e corrija o pior item antes de entregar.

## Regras

- Ativos só CC0 / domínio público / OFL / livres para uso comercial (anote em `CREDITS.md`). Não use marca real; invente nomes.
- Não invente fatos, números ou nomes: todo dado na tela tem que vir do roteiro do usuário.
- Não coloque assinatura do autor do repositório nem "AI LAB" no vídeo; só a marca d'água do usuário, se pedida.
- Trabalhe só dentro da pasta do pedido. Não altere os arquivos desta skill (copie o que precisar).
- O 3D Render precisa do Blender (CLI). Se não houver Blender, faça a versão "falso 3D" em Three.js (PBR + HDRI de
  `assets/hdri/`) e anote a decisão em `DECISOES.md`.
- Se esta pasta sumir: `git clone --depth 1 https://github.com/Vincentwei1021/mg-styles-15` e copie `prompts/ demos/
  harness/ lib/ assets/ package.json requirements.txt rubric.md template.md LICENSE` para `~/.claude/skills/mg-styles-15/`.
