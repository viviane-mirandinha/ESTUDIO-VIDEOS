---
name: mg-morph
description: "Vídeo vertical em motion graphics no estilo \"Morph de Formas\" (repositório mg-styles-15, MIT) feito 100% por código a partir de roteiro ou narração, com legenda sincronizada. Uma forma vira outra sem corte (celular vira alfinete de mapa, xícara vira pôr do sol). Storytelling visual: antes e depois, metáforas, jornada em etapas. Use quando pedirem esse estilo ou quando o painel Estúdio de Vídeos mandar `mg-morph`."
---

# 🔷 Morph de Formas (mg-morph)

Uma forma se transforma suave e continuamente em outra. É a gramática central do storytelling gráfico, o que mais exige técnica em keynote e explainer de alto nível.

**Esta skill é uma camada fina.** O fluxo completo, o renderizador e os templates estão na skill base
`~/.claude/skills/mg-styles-15/` — **leia `~/.claude/skills/mg-styles-15/SKILL.md` primeiro e siga o fluxo de lá**, usando:

- Prompt do estilo: `~/.claude/skills/mg-styles-15/prompts/08-morph.md` (leia inteiro; as seções *Signature features* e *Suggested technical route* são obrigatórias)
- Código de referência: `~/.claude/skills/mg-styles-15/demos/08-morph/`
- Vídeo de exemplo do filme original: `(pasta do Estúdio)/skills_ia/previews/mg-morph.mp4`

Se `~/.claude/skills/mg-styles-15/` não existir: `git clone --depth 1 https://github.com/Vincentwei1021/mg-styles-15` e copie
`prompts/ demos/ harness/ lib/ assets/ package.json requirements.txt rubric.md template.md LICENSE` para lá.

## Traços obrigatórios (o vídeo é julgado por eles)

- Contorno contínuo, sem pulo: os dois caminhos com o mesmo número de pontos e o primeiro ponto alinhado (senão dá nó).
- Formas complexas não viram direto: A → forma intermediária simples (círculo/cápsula) → B, cada trecho 8–12 quadros.
- O morph vem junto com deslocamento e rotação, com leve squash & stretch no instante da troca.
- Rota: SVG + flubber (ou interpolação própria) e limpezas de campo de cor.
- Paleta curta, fundo de cor chapada que troca junto com a forma.

## Neste estilo

- Formato padrão: vertical 1080x1920, 30 fps, duração = narração. Recomponha o layout do demo para vertical (não estique o 16:9).
- Entrada: roteiro/narração (texto ou áudio pronto). Sem vídeo do usuário.
- Legenda sincronizada: Sans geométrica média (Outfit / DM Sans), cada palavra-chave aparecendo dentro ou ao lado da forma que a representa.
- Som: narração na frente; por baixo, baixo volume: Whooshes suaves sincronizados aos morphs, sinos/pads.
- Sem motion blur (ou só onde o prompt pedir).
- Cada cena mostra o que a fala diz, com os elementos do estilo. Não invente fatos, números ou nomes que não estejam no roteiro.

Licença: MIT (c) 2026 Vincentwei1021 — veja `LICENSE`.
