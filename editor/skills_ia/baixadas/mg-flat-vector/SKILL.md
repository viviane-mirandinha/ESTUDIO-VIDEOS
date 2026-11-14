---
name: mg-flat-vector
description: "Vídeo vertical em motion graphics no estilo \"Flat Vector 2D\" (repositório mg-styles-15, MIT) feito 100% por código a partir de roteiro ou narração, com legenda sincronizada. Explainer de formas chapadas: cores fortes sem degradê, personagens geométricos e tudo entrando com pulo elástico (estica, amassa, volta). Bom pra explicar app, produto, processo ou dica rápida. Use quando pedirem esse estilo ou quando o painel Estúdio de Vídeos mandar `mg-flat-vector`."
---

# 🟠 Flat Vector 2D (mg-flat-vector)

O estilo mais clássico de motion graphics de explicação (tradição Google Material / vídeos explicativos de SaaS): cenas e personagens feitos só de formas vetoriais de cor sólida, sem contorno ou com contorno mínimo, contraste forte de cores.

**Esta skill é uma camada fina.** O fluxo completo, o renderizador e os templates estão na skill base
`~/.claude/skills/mg-styles-15/` — **leia `~/.claude/skills/mg-styles-15/SKILL.md` primeiro e siga o fluxo de lá**, usando:

- Prompt do estilo: `~/.claude/skills/mg-styles-15/prompts/01-flat-vector.md` (leia inteiro; as seções *Signature features* e *Suggested technical route* são obrigatórias)
- Código de referência: `~/.claude/skills/mg-styles-15/demos/01-flat-vector/`
- Vídeo de exemplo do filme original: `(pasta do Estúdio)/skills_ia/previews/mg-flat-vector.mp4`

Se `~/.claude/skills/mg-styles-15/` não existir: `git clone --depth 1 https://github.com/Vincentwei1021/mg-styles-15` e copie
`prompts/ demos/ harness/ lib/ assets/ package.json requirements.txt rubric.md template.md LICENSE` para lá.

## Traços obrigatórios (o vídeo é julgado por eles)

- Blocos de cor sólida, sem degradê (ou quase nenhum), muito respiro e paleta saturada de 5–6 cores.
- Personagens geométricos com membros girando em pontos de articulação (rig por âncora).
- Easing elástico é a alma: overshoot `cubic-bezier(0.34,1.56,0.64,1)`; entrada em 3 tempos: antecipação → disparo → volta.
- Entradas escalonadas (2–4 quadros entre elementos) e só UM herói se mexendo por vez.
- Squash & stretch de ~10% nos deslocamentos; transições por limpeza de forma (shape wipe) ou por um objeto que sai voando e leva a cena.

## Neste estilo

- Formato padrão: vertical 1080x1920, 30 fps, duração = narração. Recomponha o layout do demo para vertical (não estique o 16:9).
- Entrada: roteiro/narração (texto ou áudio pronto). Sem vídeo do usuário.
- Legenda sincronizada: Fonte geométrica pesada (Poppins Black / DM Sans), blocos de cor atrás da palavra atual, entrada com pop elástico.
- Som: narração na frente; por baixo, baixo volume: Pop/future bass ~120 BPM; pop, boing e whoosh em cada entrada, no quadro exato.
- Use motion blur (`--mb 4`) nos movimentos rápidos.
- Cada cena mostra o que a fala diz, com os elementos do estilo. Não invente fatos, números ou nomes que não estejam no roteiro.

Licença: MIT (c) 2026 Vincentwei1021 — veja `LICENSE`.
