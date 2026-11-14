---
name: mg-hud
description: "Vídeo vertical em motion graphics no estilo \"HUD Cyberpunk\" (repositório mg-styles-15, MIT) feito 100% por código a partir de roteiro ou narração, com legenda sincronizada. Interface de filme de ficção: linhas neon ciano e laranja, mira travando alvo, radar girando, dados em fonte mono e holograma 3D. Tecnologia, IA, análise, ranking, 'missão'. Use quando pedirem esse estilo ou quando o painel Estúdio de Vídeos mandar `mg-hud`."
---

# 🛰️ HUD Cyberpunk (mg-hud)

Interface fictícia de filme/jogo de ficção científica (FUI): linhas neon ciano/laranja, caixas de travamento de alvo, radar varrendo, fluxo de dados em letra miúda. É a 'skin de tecnologia' padrão de review, games, ciência militar/espacial e demo de IA.

**Esta skill é uma camada fina.** O fluxo completo, o renderizador e os templates estão na skill base
`~/.claude/skills/mg-styles-15/` — **leia `~/.claude/skills/mg-styles-15/SKILL.md` primeiro e siga o fluxo de lá**, usando:

- Prompt do estilo: `~/.claude/skills/mg-styles-15/prompts/22-hud.md` (leia inteiro; as seções *Signature features* e *Suggested technical route* são obrigatórias)
- Código de referência: `~/.claude/skills/mg-styles-15/demos/22-hud/`
- Vídeo de exemplo do filme original: `(pasta do Estúdio)/skills_ia/previews/mg-hud.mp4`

Se `~/.claude/skills/mg-styles-15/` não existir: `git clone --depth 1 https://github.com/Vincentwei1021/mg-styles-15` e copie
`prompts/ demos/ harness/ lib/ assets/ package.json requirements.txt rubric.md template.md LICENSE` para lá.

## Traços obrigatórios (o vídeo é julgado por eles)

- Linhas ciano/laranja crescendo por stroke-dashoffset, elementos abrindo em camadas escalonadas.
- Caixa de mira travando o alvo, cruz de mira, radar circular (setor conic-gradient girando) com alvos piscando.
- Texto mono pequeno em fluxo de dados + efeito máquina de escrever; dados aleatórios com semente.
- Grade hexagonal, glow e passe de scanline; holograma wireframe em Three.js.
- Tudo determinístico (seeded random).

## Neste estilo

- Formato padrão: vertical 1080x1920, 30 fps, duração = narração. Recomponha o layout do demo para vertical (não estique o 16:9).
- Entrada: roteiro/narração (texto ou áudio pronto). Sem vídeo do usuário.
- Legenda sincronizada: Mono técnica (JetBrains Mono / Chakra Petch / Rajdhani) com cursor piscando, cada palavra 'digitada' dentro de um colchete de HUD.
- Som: narração na frente; por baixo, baixo volume: Bips de interface, varredura de radar, graves sintéticos, alarme de 'travado'.
- Sem motion blur (ou só onde o prompt pedir).
- Cada cena mostra o que a fala diz, com os elementos do estilo. Não invente fatos, números ou nomes que não estejam no roteiro.

Licença: MIT (c) 2026 Vincentwei1021 — veja `LICENSE`.
