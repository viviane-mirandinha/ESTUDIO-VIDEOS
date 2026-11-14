# Estilo medido — ref.mp4

Medição automática (`medir_estilo.py`, zero token). Números aproximados; texto e música são heurísticas.

## Vídeo
- Duração: **95.0 s** · 640x360 (16:9) · 30.0 fps

## Ritmo
- Cortes detectados (scene > 0,3): **9** → **5.7 cortes/min**
- Duração média do plano: **9.5 s** (mediana 8.22 s; mais curto 1.97 s, mais longo 25.5 s)
- Transições: seco 7 · dissolve 1 · fade p/ preto 1

## Imagem
- Paleta (5 cores dominantes): `#44372c` (24.7%) · `#090805` (24.0%) · `#7b6955` (21.1%) · `#b59876` (17.8%) · `#d6c6b0` (12.4%)
- Cor de destaque provável: `#ce9a48`
- Brilho médio: **89.1**/255 · contraste (desvio da luma): **46.4** · saturação média: **0.32**

## Texto na tela (heurística de bordas)
- Quadros com faixa de texto — centro: **0.0%** · terço inferior: **0.0%**
- Altura típica da faixa de texto: ~0.0% da altura da tela

## Áudio
- Loudness: **-15.6 LUFS** integrado · LRA 12.1 LU · pico -0.2 dBFS
- Tipo: **voz + música baixa por baixo (incerto)** (pausas silenciosas 9.0%, chão -24.4 dB)
- BPM aproximado: não confiável (confiança 0.04)

Contact-sheet: `sheet-medido.jpg` (20 quadros, 5x4).

## Como recriar no Estúdio
- **Canvas**: `"canvas": {"w": 1280, "h": 720, "fps": 30}`.
- **Ritmo de cortes alvo**: ~5.7 cortes/min → troque de imagem/cena a cada **~9.5 s** (itens da trilha `imagens` com `start` espaçado nesse passo; varie ±30%).
- **Fonte (Google Fonts, OFL)**: Montserrat 800 — neutro. Coloque o .ttf em `fonts/` e declare em `"fonts"` do edit.json.
- **Cores**: fundo `#44372c`, destaque `#ce9a48` (use em `hl_color` / param `cor_destaque`), texto `#ffffff` se o fundo for escuro, `#111111` se claro.
- **Legenda/texto**: posição inferior (`"y": 576`), `"size": 52`; texto aparece em ~0.0% dos quadros — texto só em títulos/destaques, não legenda contínua.
- **Transição**: corte seco (sem transição); whoosh suave só em troca de capítulo.
- **Áudio**: música de fundo baixinha (−20 a −24 dB sob a voz, com ducking); normalize o final em -14.0 LUFS. SFX: só whoosh suave (proibido impact/pop).
