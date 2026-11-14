---
name: mg-pixel
description: "Vídeo vertical em motion graphics no estilo \"Pixel Art 8-bit\" (repositório mg-styles-15, MIT) feito 100% por código a partir de roteiro ou narração, com legenda sincronizada. Pixels grandes, paleta limitada, sprites com poucos quadros e filtro de TV antiga (CRT). Games, nostalgia, 'fases' e 'missões', jornada de alguém. Use quando pedirem esse estilo ou quando o painel Estúdio de Vídeos mandar `mg-pixel`."
---

# 👾 Pixel Art 8-bit (mg-pixel)

Estética de jogo retrô: baixa resolução com pixels grandes, paleta limitada e sprites animados em poucos quadros. Comum em conteúdo de games, clipe 8-bit e marketing nostálgico.

**Esta skill é uma camada fina.** O fluxo completo, o renderizador e os templates estão na skill base
`~/.claude/skills/mg-styles-15/` — **leia `~/.claude/skills/mg-styles-15/SKILL.md` primeiro e siga o fluxo de lá**, usando:

- Prompt do estilo: `~/.claude/skills/mg-styles-15/prompts/20-pixel.md` (leia inteiro; as seções *Signature features* e *Suggested technical route* são obrigatórias)
- Código de referência: `~/.claude/skills/mg-styles-15/demos/20-pixel/`
- Vídeo de exemplo do filme original: `(pasta do Estúdio)/skills_ia/previews/mg-pixel.mp4`

Se `~/.claude/skills/mg-styles-15/` não existir: `git clone --depth 1 https://github.com/Vincentwei1021/mg-styles-15` e copie
`prompts/ demos/ harness/ lib/ assets/ package.json requirements.txt rubric.md template.md LICENSE` para lá.

## Traços obrigatórios (o vídeo é julgado por eles)

- Canvas interno de baixa resolução (ex.: 180×320 no vertical) ampliado por número inteiro com vizinho mais próximo (`image-rendering: pixelated`), zero antialias.
- Paleta de 8–32 cores; degradê por dithering.
- Sprites desenhados como matrizes de pixel no código, animação de 8–12 fps (andar 6–8 quadros, respirar 2–4).
- Filtro CRT com scanlines por cima.
- SEM motion blur e SEM movimento sub-pixel.

## Neste estilo

- Formato padrão: vertical 1080x1920, 30 fps, duração = narração. Recomponha o layout do demo para vertical (não estique o 16:9).
- Entrada: roteiro/narração (texto ou áudio pronto). Sem vídeo do usuário.
- Legenda sincronizada: Fonte pixel (Press Start 2P / VT323) em caixa de diálogo de RPG, texto 'digitando' letra a letra no ritmo da fala.
- Som: narração na frente; por baixo, baixo volume: Chiptune (onda quadrada/triangular, ruído), bips de diálogo, som de moeda e de 'level up'.
- Sem motion blur (ou só onde o prompt pedir).
- Cada cena mostra o que a fala diz, com os elementos do estilo. Não invente fatos, números ou nomes que não estejam no roteiro.

Licença: MIT (c) 2026 Vincentwei1021 — veja `LICENSE`.
