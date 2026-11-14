---
name: mg-line-art
description: "Vídeo vertical em motion graphics no estilo \"Line Art (Um Traço)\" (repositório mg-styles-15, MIT) feito 100% por código a partir de roteiro ou narração, com legenda sincronizada. Uma única linha fina que se desenha sozinha e vira o próximo desenho, num fundo limpo. Minimalista e elegante: frase de impacto, marca pessoal, finanças, reflexão. Use quando pedirem esse estilo ou quando o painel Estúdio de Vídeos mandar `mg-line-art`."
---

# ✒️ Line Art (Um Traço) (mg-line-art)

A linha fina monocromática é a única linguagem visual: ela se desenha (draw-on), estica, faz curvas e vira a próxima figura, como se o filme inteiro fosse um traço só. Visual de luxo, arquitetura, finanças, animação de logo.

**Esta skill é uma camada fina.** O fluxo completo, o renderizador e os templates estão na skill base
`~/.claude/skills/mg-styles-15/` — **leia `~/.claude/skills/mg-styles-15/SKILL.md` primeiro e siga o fluxo de lá**, usando:

- Prompt do estilo: `~/.claude/skills/mg-styles-15/prompts/02-line-art.md` (leia inteiro; as seções *Signature features* e *Suggested technical route* são obrigatórias)
- Código de referência: `~/.claude/skills/mg-styles-15/demos/02-line-art/`
- Vídeo de exemplo do filme original: `(pasta do Estúdio)/skills_ia/previews/mg-line-art.mp4`

Se `~/.claude/skills/mg-styles-15/` não existir: `git clone --depth 1 https://github.com/Vincentwei1021/mg-styles-15` e copie
`prompts/ demos/ harness/ lib/ assets/ package.json requirements.txt rubric.md template.md LICENSE` para lá.

## Traços obrigatórios (o vídeo é julgado por eles)

- Linha de espessura constante (2–4 px) o filme todo, uma ou duas cores, muito espaço negativo.
- Desenho por `stroke-dasharray/stroke-dashoffset` (comprimento via `getTotalLength`), linha crescendo de forma contínua.
- Nas curvas o traço desacelera um pouco; easing `cubic-bezier(0.65,0,0.35,1)`.
- Câmera virtual que segue a ponta da caneta; momento de virada linha → superfície (preenchimento) no clímax.
- Uma figura se transforma na próxima sem corte.

## Neste estilo

- Formato padrão: vertical 1080x1920, 30 fps, duração = narração. Recomponha o layout do demo para vertical (não estique o 16:9).
- Entrada: roteiro/narração (texto ou áudio pronto). Sem vídeo do usuário.
- Legenda sincronizada: Serif elegante fina (Cormorant Garamond / Instrument Serif), palavras surgindo como se fossem escritas pela mesma linha; destaque em itálico.
- Som: narração na frente; por baixo, baixo volume: Piano/harpa delicados, arranhar de pena no início, respiros de silêncio.
- Sem motion blur (ou só onde o prompt pedir).
- Cada cena mostra o que a fala diz, com os elementos do estilo. Não invente fatos, números ou nomes que não estejam no roteiro.

Licença: MIT (c) 2026 Vincentwei1021 — veja `LICENSE`.
