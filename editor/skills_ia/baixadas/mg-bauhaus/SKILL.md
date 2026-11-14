---
name: mg-bauhaus
description: "Vídeo vertical em motion graphics no estilo \"Geométrico Bauhaus\" (repositório mg-styles-15, MIT) feito 100% por código a partir de roteiro ou narração, com legenda sincronizada. Círculo, triângulo e quadrado numa grade rígida, só vermelho, amarelo, azul, preto e branco, tudo no ritmo da batida. Pôster cinético: listas, regras, frases curtas. Use quando pedirem esse estilo ou quando o painel Estúdio de Vídeos mandar `mg-bauhaus`."
---

# 🔺 Geométrico Bauhaus (mg-bauhaus)

Círculos, triângulos e retângulos fazendo translações, rotações e escalas precisas numa grade rígida, com paleta de primárias + preto e branco. Ordem mecânica e racional, herança Bauhaus e Estilo Internacional Suíço.

**Esta skill é uma camada fina.** O fluxo completo, o renderizador e os templates estão na skill base
`~/.claude/skills/mg-styles-15/` — **leia `~/.claude/skills/mg-styles-15/SKILL.md` primeiro e siga o fluxo de lá**, usando:

- Prompt do estilo: `~/.claude/skills/mg-styles-15/prompts/09-bauhaus.md` (leia inteiro; as seções *Signature features* e *Suggested technical route* são obrigatórias)
- Código de referência: `~/.claude/skills/mg-styles-15/demos/09-bauhaus/`
- Vídeo de exemplo do filme original: `(pasta do Estúdio)/skills_ia/previews/mg-bauhaus.mp4`

Se `~/.claude/skills/mg-styles-15/` não existir: `git clone --depth 1 https://github.com/Vincentwei1021/mg-styles-15` e copie
`prompts/ demos/ harness/ lib/ assets/ package.json requirements.txt rubric.md template.md LICENSE` para lá.

## Traços obrigatórios (o vídeo é julgado por eles)

- Tudo ancorado na grade: deslocamentos em múltiplos inteiros do módulo, pousos sempre na linha.
- Easing contido (easeInOutQuad ou linear), SEM overshoot — a sensação mecânica é proposital.
- Paleta vermelho / amarelo / azul / preto / branco; rotação pelo centro geométrico.
- Movimento modular dirigido pela batida (grade de batidas a 120 BPM).
- Tipografia grotesca grande, alinhada na grade, como cartaz suíço.

## Neste estilo

- Formato padrão: vertical 1080x1920, 30 fps, duração = narração. Recomponha o layout do demo para vertical (não estique o 16:9).
- Entrada: roteiro/narração (texto ou áudio pronto). Sem vídeo do usuário.
- Legenda sincronizada: Grotesca pesada em caixa alta (Archivo / Anton), blocos alinhados na grade, palavra atual num retângulo de cor primária.
- Som: narração na frente; por baixo, baixo volume: Eletrônica minimalista/percussão seca a 120 BPM, cada movimento numa batida.
- Sem motion blur (ou só onde o prompt pedir).
- Cada cena mostra o que a fala diz, com os elementos do estilo. Não invente fatos, números ou nomes que não estejam no roteiro.

Licença: MIT (c) 2026 Vincentwei1021 — veja `LICENSE`.
