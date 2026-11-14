---
name: mg-cel-boil
description: "Vídeo vertical em motion graphics no estilo \"Quadro a Quadro (Line Boil)\" (repositório mg-styles-15, MIT) feito 100% por código a partir de roteiro ou narração, com legenda sincronizada. Traço desenhado à mão que 'ferve' (treme de leve a cada 2 quadros), papel texturizado, fumaça e faíscas desenhadas. Tom artesanal e caloroso: histórias, curiosidades, bastidores. Use quando pedirem esse estilo ou quando o painel Estúdio de Vídeos mandar `mg-cel-boil`."
---

# ✏️ Quadro a Quadro (Line Boil) (mg-cel-boil)

Animação desenhada quadro a quadro, ou textura de quadro a quadro por cima do vetor. A marca registrada é o line boil: as linhas tremem levemente a cada poucos quadros, como se o desenho respirasse. Anti-perfeição digital.

**Esta skill é uma camada fina.** O fluxo completo, o renderizador e os templates estão na skill base
`~/.claude/skills/mg-styles-15/` — **leia `~/.claude/skills/mg-styles-15/SKILL.md` primeiro e siga o fluxo de lá**, usando:

- Prompt do estilo: `~/.claude/skills/mg-styles-15/prompts/05-cel-boil.md` (leia inteiro; as seções *Signature features* e *Suggested technical route* são obrigatórias)
- Código de referência: `~/.claude/skills/mg-styles-15/demos/05-cel-boil/`
- Vídeo de exemplo do filme original: `(pasta do Estúdio)/skills_ia/previews/mg-cel-boil.mp4`

Se `~/.claude/skills/mg-styles-15/` não existir: `git clone --depth 1 https://github.com/Vincentwei1021/mg-styles-15` e copie
`prompts/ demos/ harness/ lib/ assets/ package.json requirements.txt rubric.md template.md LICENSE` para lá.

## Traços obrigatórios (o vídeo é julgado por eles)

- Linhas sempre tremendo (boil): 3–4 variações levemente diferentes do mesmo desenho alternando a cada 2 quadros.
- Ritmo 'em dois' (12 desenhos/s a 24 fps); ações rápidas em um, planos parados em três.
- Pincel de espessura variável (linha central + pressão → contorno), smear frames nos movimentos rápidos.
- Efeitos desenhados à mão (fumaça, faísca, respingo, linhas de velocidade) e fundo de papel com textura (multiply).
- SEM motion blur: o movimento é por poses.

## Neste estilo

- Formato padrão: vertical 1080x1920, 30 fps, duração = narração. Recomponha o layout do demo para vertical (não estique o 16:9).
- Entrada: roteiro/narração (texto ou áudio pronto). Sem vídeo do usuário.
- Legenda sincronizada: Letra de marcador/caneta (Caveat ou fonte manuscrita OFL) que também treme no ritmo do boil, palavra atual sublinhada à mão.
- Som: narração na frente; por baixo, baixo volume: Acústico, percussão leve de mão, foley de lápis e papel.
- Sem motion blur (ou só onde o prompt pedir).
- Cada cena mostra o que a fala diz, com os elementos do estilo. Não invente fatos, números ou nomes que não estejam no roteiro.

Licença: MIT (c) 2026 Vincentwei1021 — veja `LICENSE`.
