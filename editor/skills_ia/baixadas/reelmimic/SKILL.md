---
name: reelmimic
description: Clonador de ESTILO de vídeo de referência (ReelMimic, MIT) — recebe um vídeo de referência (arquivo local, gravação de tela ou link do YouTube/TikTok/Instagram) + um tema/roteiro e cria um vídeo ANIMADO 2D NOVO no mesmo estilo de edição: mede cortes, duração de cada plano, BPM e batidas, transições, movimento de câmera por plano (push-in, pull-out, pan, órbita, parado), luz/cor e os picos (clímax), escreve storyboard plano a plano casado com a referência e produz com um motor de desenho (vetor/motion graphics via HyperFrames, aquarela pintada, giz de cera, pixel art, recorte de papel, quadro branco, anime cel), com revisão quadro a quadro. Use quando o usuário mandar um vídeo de referência e pedir "faz um vídeo nesse estilo", "clona a edição/ritmo desse", "igual a esse, mas sobre X", ou quiser medir o ritmo/cortes/câmera de um vídeo (só a parte de análise). NÃO serve pra editar vídeo de pessoa falando (live-action): ele recria em animação 2D.
---

# ReelMimic — referência → análise de estilo → vídeo novo animado

Fonte: https://github.com/edenfunf/reelmimic (MIT; partes Apache-2.0 da HeyGen — ver `THIRD_PARTY_NOTICES.md`), commit `d445b23`.
Esta pasta é a skill `video-clone` do repo + os 6 motores de desenho dele em `engines/`. O fluxo original completo (em chinês)
está em `SKILL-original-zh.md` e os nomes/campos de arquivo em `CONTRACT.md` — **leia os dois antes de produzir**; este arquivo
é o resumo em português e as adaptações pra este PC.

## Caminhos neste PC (já ajustados nos .md)

| No original | Aqui |
|---|---|
| `.claude/skills/video-clone/` | `~/.claude/skills/reelmimic/` (= `$SK`) |
| `.claude/skills/<motor>/` (painted-animation, crayon-storybook, pixel-art, paper-cutout, whiteboard, anime-cel) | `$SK/engines/<motor>/` — **ler o `SKILL.md`/`GUIDE.md` do motor com Read** (não estão como skills soltas) |
| motor `hyperframes` (estilos motion-graphics, faceless-explainer, music-kinetic, narrated-comic-vlog, product-promo) | skill global `hyperframes` já instalada (carregar com a ferramenta Skill) |
| motor `remotion-best-practices` | skill global já instalada |
| `projects/<id>/` | a pasta de trabalho atual (no painel: a pasta do PEDIDO.md) |
| `docs/COMPILER.md` | `$SK/docs/COMPILER.md` |

Python: **sempre** `"$SK/.venv/Scripts/python.exe"` (venv com numpy, opencv, scenedetect, librosa, scipy, Pillow, yt-dlp).
Opcional (só legenda de música/letra): `faster-whisper` e `opencc-python-reimplemented` não estão no venv — instale nele se precisar de `align_lyrics.py`.
Precisa também: ffmpeg/ffprobe no PATH, Node 22+, Chrome (render dos motores via puppeteer-core), `npx hyperframes@0.8.80` (baixa sozinho).

## Fluxo (resumo)

0. **Receber**: vídeo de referência + pedido (tema, duração, proporção; padrão 30 s 16:9 — no painel, usar o formato do PEDIDO.md).
1. **Analisar a referência**:
   ```bash
   SK=~/.claude/skills/reelmimic
   "$SK/.venv/Scripts/python.exe" "$SK/scripts/analyze.py" "entrada/ref.mp4" --out analysis
   ```
   Sai `analysis/report.json` (cortes, duração média de plano, BPM/batidas, `shot_details` = movimento de câmera e luz/cor
   por plano, `look_summary`, `audio.peak_candidates`, `flashes`) e as folhas `sheet_1fps.jpg` / `sheet_scenes.jpg`
   (abrir essas 2 com Read — são contact-sheets, não abrir frame por frame). Escrever `analysis/STYLE.md`
   (1ª linha = mídia: 2d-painted · 2d-crayon · 2d-vector · 2d-pixel · 2d-paper · 2d-lineart · 2d-cel · live-action…),
   tabela de planos, paleta, edição, narrativa, uso de texto.
   **Clímax**: para cada candidato, `scripts/clip_strip.py analysis/source.mp4 --range a:b --out analysis/peak_<n>.jpg`
   (tira 12 fps) e escrever `analysis/peaks.json` (formato no CONTRACT.md).
2. **Escolher estilo → motor**: ler `$SK/styles/*.md` (menos `_TEMPLATE.md`), filtrar pela mídia, pontuar pelos
   "traços de identificação", empate → `priority`. Referência live-action/3D → recriar no 2D mais próximo e DIZER isso.
3. **Música** (se o estilo tiver): só áudio fornecido pelo usuário/livre; analisar com analyze.py, cortar no compasso.
4. **Storyboard**: `STORYBOARD.md` + `plan.json` — cada plano nosso aponta para um plano da referência (`ref_shot`,
   `ref_what`, `camera` com o mesmo tipo/velocidade de movimento). Duração média de plano e proporção de cartelas ±30 % da referência.
5. **Produção em etapas** (personagens → segmentos → revisão de cada segmento com olhos "novos" → montagem →
   `motion_check.py` → comparação do clímax com a referência lado a lado via `clip_strip.py --vs`). Motion Score:
   `scripts/motion_score.py from-ref | predict | compile`. Distância de estilo: `scripts/fingerprint.py` / `compare.py`.
6. **Ajustes** por "segundo X está estranho": refazer só aquele plano.

## Regras

- Copia **técnica** (ritmo, cortes, câmera, composição, motivos, estrutura), nunca as imagens, personagens, logos ou música da referência.
- Assets: `scripts/fetch_assets.py` (Openverse CC0/CC BY sem chave; Pixabay/Freesound com `PIXABAY_KEY`/`FREESOUND_KEY`) e anotar fonte/licença em `assets/ASSETS.md`.
- Narração: o original usa Yating (mandarim de Taiwan, `YATING_KEY`). **Neste PC usar a voz/TTS indicada no PEDIDO.md** (edge-tts, VoiceStudio etc.), não o Yating.
- Só 2D; não gera pessoa real/live-action.
- Rodando pelo painel (sem ninguém olhando): não perguntar; escolher o padrão, anotar em `DECISOES.md`; vídeo final = `resultado.mp4` (H.264+AAC).
- É LENTO: 30–60 s de vídeo levam ~1–3,5 h de agente no app original (aquarela/giz são os mais lentos). Sem API paga obrigatória — o custo é uso do plano Claude.
- O app web do ReelMimic (orquestra até 6 agentes em paralelo, porta 4318) **não** está instalado aqui; esta skill roda o fluxo num agente só.
