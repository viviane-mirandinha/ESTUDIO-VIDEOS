---
name: mg-liquid
description: "Vídeo vertical em motion graphics no estilo \"Motion Líquido\" (repositório mg-styles-15, MIT) feito 100% por código a partir de roteiro ou narração, com legenda sincronizada. Formas que escorrem, pingam e se fundem como gotas, transições em onda de tinta. Orgânico e cheio de energia: abertura, ideias que se juntam, comida e bebida. Use quando pedirem esse estilo ou quando o painel Estúdio de Vídeos mandar `mg-liquid`."
---

# 💧 Motion Líquido (mg-liquid)

As formas fluem como líquido: esticam, pingam, se fundem. A transição é uma onda de tinta cobrindo a tela e o logo se forma de uma gota. Orgânico, satisfatório, muito usado em clipe musical e anúncio de bebida.

**Esta skill é uma camada fina.** O fluxo completo, o renderizador e os templates estão na skill base
`~/.claude/skills/mg-styles-15/` — **leia `~/.claude/skills/mg-styles-15/SKILL.md` primeiro e siga o fluxo de lá**, usando:

- Prompt do estilo: `~/.claude/skills/mg-styles-15/prompts/07-liquid.md` (leia inteiro; as seções *Signature features* e *Suggested technical route* são obrigatórias)
- Código de referência: `~/.claude/skills/mg-styles-15/demos/07-liquid/`
- Vídeo de exemplo do filme original: `(pasta do Estúdio)/skills_ia/previews/mg-liquid.mp4`

Se `~/.claude/skills/mg-styles-15/` não existir: `git clone --depth 1 https://github.com/Vincentwei1021/mg-styles-15` e copie
`prompts/ demos/ harness/ lib/ assets/ package.json requirements.txt rubric.md template.md LICENSE` para lá.

## Traços obrigatórios (o vídeo é julgado por eles)

- Metaballs: SDF 2D com smooth-min num shader WebGL2 (ou blur + limiar de alfa) — duas gotas perto se 'grudam'.
- Luz falsa 3D a partir do gradiente do campo (brilho especular nas gotas).
- Transição por frente de onda com 3–5 bolhas fora de fase varrendo a tela.
- Fios esticando, gotas caindo e gotas secundárias seguindo a principal; nunca linha reta.
- Texto também como SDF, nascendo de uma gota.

## Neste estilo

- Formato padrão: vertical 1080x1920, 30 fps, duração = narração. Recomponha o layout do demo para vertical (não estique o 16:9).
- Entrada: roteiro/narração (texto ou áudio pronto). Sem vídeo do usuário.
- Legenda sincronizada: Serif gorda e macia (Fraunces Soft / similar OFL) com bordas que 'derretem' de leve ao entrar.
- Som: narração na frente; por baixo, baixo volume: Gotas, plop, swoosh molhado; trilha fluida e grave.
- Use motion blur (`--mb 4`) nos movimentos rápidos.
- Cada cena mostra o que a fala diz, com os elementos do estilo. Não invente fatos, números ou nomes que não estejam no roteiro.

Licença: MIT (c) 2026 Vincentwei1021 — veja `LICENSE`.
