---
name: mg-synthwave
description: "Vídeo vertical em motion graphics no estilo \"Synthwave 80s / VHS\" (repositório mg-styles-15, MIT) feito 100% por código a partir de roteiro ou narração, com legenda sincronizada. Neon, grade em perspectiva rumo ao horizonte, sol em degradê, letra cromada e ruído de fita VHS. Nostalgia, games, música, tecnologia antiga. Use quando pedirem esse estilo ou quando o painel Estúdio de Vídeos mandar `mg-synthwave`."
---

# 🌆 Synthwave 80s / VHS (mg-synthwave)

Citação completa da estética de mídia dos anos 80: grade neon, sol em degradê, letra cromada; VHS com scanline, desvio de cor e ruído de fita (também cobre Y2K: cromo líquido, verde-ácido/roxo, janelas de sistema).

**Esta skill é uma camada fina.** O fluxo completo, o renderizador e os templates estão na skill base
`~/.claude/skills/mg-styles-15/` — **leia `~/.claude/skills/mg-styles-15/SKILL.md` primeiro e siga o fluxo de lá**, usando:

- Prompt do estilo: `~/.claude/skills/mg-styles-15/prompts/10-synthwave.md` (leia inteiro; as seções *Signature features* e *Suggested technical route* são obrigatórias)
- Código de referência: `~/.claude/skills/mg-styles-15/demos/10-synthwave/`
- Vídeo de exemplo do filme original: `(pasta do Estúdio)/skills_ia/previews/mg-synthwave.mp4`

Se `~/.claude/skills/mg-styles-15/` não existir: `git clone --depth 1 https://github.com/Vincentwei1021/mg-styles-15` e copie
`prompts/ demos/ harness/ lib/ assets/ package.json requirements.txt rubric.md template.md LICENSE` para lá.

## Traços obrigatórios (o vídeo é julgado por eles)

- Grade em perspectiva de um ponto rolando para o horizonte; sol em várias faixas de degradê; montanhas.
- Glow duplo: interno justo de ~4 px bem claro + externo espalhado de ~30 px translúcido.
- Letra cromada com reflexo e letra cursiva neon.
- Cadeia VHS: RGB split (1–2 px) → scanlines (faixa preta 10% a cada 2 px) → tremida/glitch 1–2 vezes por segundo → máscara com cantos arredondados.
- Paleta magenta, ciano, roxo, laranja do pôr do sol.

## Neste estilo

- Formato padrão: vertical 1080x1920, 30 fps, duração = narração. Recomponha o layout do demo para vertical (não estique o 16:9).
- Entrada: roteiro/narração (texto ou áudio pronto). Sem vídeo do usuário.
- Legenda sincronizada: Fonte cursiva neon (Mr Dafoe) para palavras-chave + mono/retrô (VT323) para o resto, com glow e leve RGB split.
- Som: narração na frente; por baixo, baixo volume: Synthwave: baixo arpejado, bateria eletrônica com reverb gated, pads analógicos, chiado de fita.
- Use motion blur (`--mb 4`) nos movimentos rápidos.
- Cada cena mostra o que a fala diz, com os elementos do estilo. Não invente fatos, números ou nomes que não estejam no roteiro.

Licença: MIT (c) 2026 Vincentwei1021 — veja `LICENSE`.
