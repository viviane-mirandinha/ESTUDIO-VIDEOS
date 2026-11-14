---
name: mg-collage
description: "Vídeo vertical em motion graphics no estilo \"Colagem Recortada\" (repositório mg-styles-15, MIT) feito 100% por código a partir de roteiro ou narração, com legenda sincronizada. Recortes de fotos antigas e jornal com borda branca de tesoura, retícula e movimento travado tipo stop-motion. Surreal e retrô: opinião, cultura, cérebro, comportamento. Use quando pedirem esse estilo ou quando o painel Estúdio de Vídeos mandar `mg-collage`."
---

# ✂️ Colagem Recortada (mg-collage)

Estilo surreal retrô que recorta fotos antigas, jornais e papel rasgado e remonta tudo (raiz em Monty Python e cartazes construtivistas). Proporções absurdas, boca abrindo separada, textura de retícula.

**Esta skill é uma camada fina.** O fluxo completo, o renderizador e os templates estão na skill base
`~/.claude/skills/mg-styles-15/` — **leia `~/.claude/skills/mg-styles-15/SKILL.md` primeiro e siga o fluxo de lá**, usando:

- Prompt do estilo: `~/.claude/skills/mg-styles-15/prompts/06-collage.md` (leia inteiro; as seções *Signature features* e *Suggested technical route* são obrigatórias)
- Código de referência: `~/.claude/skills/mg-styles-15/demos/06-collage/`
- Vídeo de exemplo do filme original: `(pasta do Estúdio)/skills_ia/previews/mg-collage.mp4`

Se `~/.claude/skills/mg-styles-15/` não existir: `git clone --depth 1 https://github.com/Vincentwei1021/mg-styles-15` e copie
`prompts/ demos/ harness/ lib/ assets/ package.json requirements.txt rubric.md template.md LICENSE` para lá.

## Traços obrigatórios (o vídeo é julgado por eles)

- Recortes com borda branca de 2–4 px (cara de tesoura) + filtro de retícula (halftone).
- Textura de jornal, papel kraft, fita adesiva; montagem surreal com proporções erradas de propósito.
- Animação de marionete: pontos de giro em ombro/cotovelo/queixo, boca abrindo com 2–3 peças trocadas.
- Movimento travado em 12 fps (renderiza 30, segura a pose na grade de 12).
- Só imagens de domínio público/CC0 (o demo usa gravuras PD e recorte com rembg); anote fontes em CREDITS.md.

## Neste estilo

- Formato padrão: vertical 1080x1920, 30 fps, duração = narração. Recomponha o layout do demo para vertical (não estique o 16:9).
- Entrada: roteiro/narração (texto ou áudio pronto). Sem vídeo do usuário.
- Legenda sincronizada: Letras recortadas de revista/jornal (cada palavra num papel diferente, levemente torta), entrando com 'tapa' de colagem.
- Som: narração na frente; por baixo, baixo volume: Foley de papel: tesoura, fita, papel amassado, páginas; trilha excêntrica.
- Sem motion blur (ou só onde o prompt pedir).
- Cada cena mostra o que a fala diz, com os elementos do estilo. Não invente fatos, números ou nomes que não estejam no roteiro.

Licença: MIT (c) 2026 Vincentwei1021 — veja `LICENSE`.
