---
name: mg-hanazi
description: "Vídeo vertical em motion graphics no estilo \"Legenda de Reality (Hanazi)\" (repositório mg-styles-15, MIT) feito 100% por código a partir de roteiro ou narração, com legenda sincronizada. Letreiros gordos com várias camadas de contorno que entram pulando, com explosões, gotas de suor e brilhos desenhados por cima de fotos ou do seu vídeo. Cara de programa de TV: vlog, pets, humor, reação. Use quando pedirem esse estilo ou quando o painel Estúdio de Vídeos mandar `mg-hanazi`."
---

# 🎉 Legenda de Reality (Hanazi) (mg-hanazi)

Legenda decorativa emocional da pós-produção de reality/variedades asiático (花字): letra arredondada gorda com várias camadas de contorno, entrada elástica, mudando de cor com a emoção, com efeito sonoro. Hoje é a linguagem de vlog, pets, entrevista e humor. O demo já é vertical 9:16.

**Esta skill é uma camada fina.** O fluxo completo, o renderizador e os templates estão na skill base
`~/.claude/skills/mg-styles-15/` — **leia `~/.claude/skills/mg-styles-15/SKILL.md` primeiro e siga o fluxo de lá**, usando:

- Prompt do estilo: `~/.claude/skills/mg-styles-15/prompts/18-hanazi.md` (leia inteiro; as seções *Signature features* e *Suggested technical route* são obrigatórias)
- Código de referência: `~/.claude/skills/mg-styles-15/demos/18-hanazi/`
- Vídeo de exemplo do filme original: `(pasta do Estúdio)/skills_ia/previews/mg-hanazi.mp4`

Se `~/.claude/skills/mg-styles-15/` não existir: `git clone --depth 1 https://github.com/Vincentwei1021/mg-styles-15` e copie
`prompts/ demos/ harness/ lib/ assets/ package.json requirements.txt rubric.md template.md LICENSE` para lá.

## Traços obrigatórios (o vídeo é julgado por eles)

- Letra em 3 camadas: preenchimento colorido + contorno branco grosso + contorno/sombra colorida externa (text-shadow múltiplo ou stroke SVG).
- Entrada com overshoot: escala 0 → 1,15 → 1,0 em ~8 quadros, ou letra por letra pulando com 2 quadros de defasagem.
- Cores saturadas em choque + borda branca + sombra; muda de cor/forma conforme a emoção da fala.
- Símbolos desenhados (balão de explosão, gota de suor, brilhos, linhas de choque) com SFX em cada um.
- Camada de imagem: vídeo do usuário (se vier em entrada/) ou fotos CC0 com Ken Burns, tremida de mão e punch-in.

## Neste estilo

- Formato padrão: vertical 1080x1920, 30 fps, duração = narração. Recomponha o layout do demo para vertical (não estique o 16:9).
- Aceita **vídeo do usuário**: se houver `entrada/video.*`, ele vira a camada de imagem (com punch-ins e tremida) e os letreiros vão por cima, sincronizados com a fala dele.
- Legenda sincronizada: A própria legenda É o estilo: letreiro arredondado gordo (Fredoka / Luckiest Guy) com contorno triplo, palavras de emoção maiores e coloridas.
- Som: narração na frente; por baixo, baixo volume: SFX de programa de TV: boing, pop, ding, risada, whoosh em cada letreiro.
- Sem motion blur (ou só onde o prompt pedir).
- Cada cena mostra o que a fala diz, com os elementos do estilo. Não invente fatos, números ou nomes que não estejam no roteiro.

Licença: MIT (c) 2026 Vincentwei1021 — veja `LICENSE`.
