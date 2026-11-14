---
name: mg-paperclip
description: "Vídeo vertical em motion graphics no estilo \"Explicador com Adesivos\" (repositório mg-styles-15, MIT) feito 100% por código a partir de roteiro ou narração, com legenda sincronizada. Fotos recortadas com borda branca grossa (adesivo), ícones planos e gráficos com dados numa tela gigante que a câmera percorre. Explicador de conhecimento: economia, ciência, dados. Use quando pedirem esse estilo ou quando o painel Estúdio de Vídeos mandar `mg-paperclip`."
---

# 🧷 Explicador com Adesivos (mg-paperclip)

Embalagem padrão de vídeo de conhecimento (canal PaperClip, estilo Lin Chao): fotos recortadas viram 'adesivos' com borda branca grossa, junto com ícones planos e gráficos precisos, espalhados numa tela enorme que a câmera percorre com pan e zoom.

**Esta skill é uma camada fina.** O fluxo completo, o renderizador e os templates estão na skill base
`~/.claude/skills/mg-styles-15/` — **leia `~/.claude/skills/mg-styles-15/SKILL.md` primeiro e siga o fluxo de lá**, usando:

- Prompt do estilo: `~/.claude/skills/mg-styles-15/prompts/19-paperclip.md` (leia inteiro; as seções *Signature features* e *Suggested technical route* são obrigatórias)
- Código de referência: `~/.claude/skills/mg-styles-15/demos/19-paperclip/`
- Vídeo de exemplo do filme original: `(pasta do Estúdio)/skills_ia/previews/mg-paperclip.mp4`

Se `~/.claude/skills/mg-styles-15/` não existir: `git clone --depth 1 https://github.com/Vincentwei1021/mg-styles-15` e copie
`prompts/ demos/ harness/ lib/ assets/ package.json requirements.txt rubric.md template.md LICENSE` para lá.

## Traços obrigatórios (o vídeo é julgado por eles)

- Fotos recortadas com contorno branco de 8–12 px (unifica fontes diferentes) e sombra leve.
- Fundo calmo azul-acinzentado / bege; ícones planos + gráficos de dados precisos (SVG/d3).
- Uma tela gigante (ex.: 6000×3000) com a câmera fazendo pan/zoom com easings longos, ligando os pontos num plano só.
- Narrativa densa e em batidas: cada frase da fala acende um ponto da tela.
- Dados SÓ do roteiro do usuário — nunca invente número.

## Neste estilo

- Formato padrão: vertical 1080x1920, 30 fps, duração = narração. Recomponha o layout do demo para vertical (não estique o 16:9).
- Entrada: roteiro/narração (texto ou áudio pronto). Sem vídeo do usuário.
- Legenda sincronizada: Sans limpa e firme (Inter / DM Sans) em caixa branca com borda, números grandes em destaque na cor de acento.
- Som: narração na frente; por baixo, baixo volume: Trilha leve de documentário, 'tic' a cada adesivo e 'whoosh' longo nos movimentos de câmera.
- Sem motion blur (ou só onde o prompt pedir).
- Cada cena mostra o que a fala diz, com os elementos do estilo. Não invente fatos, números ou nomes que não estejam no roteiro.

Licença: MIT (c) 2026 Vincentwei1021 — veja `LICENSE`.
