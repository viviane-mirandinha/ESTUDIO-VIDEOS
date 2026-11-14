---
name: mg-aurora-glass
description: "Vídeo vertical em motion graphics no estilo \"Aurora e Vidro\" (repositório mg-styles-15, MIT) feito 100% por código a partir de roteiro ou narração, com legenda sincronizada. Manchas de cor desfocadas flutuando devagar com cartões de vidro fosco por cima. Lento, translúcido, cara de lançamento de IA: tecnologia, produto digital, produtividade. Use quando pedirem esse estilo ou quando o painel Estúdio de Vídeos mandar `mg-aurora-glass`."
---

# 🔮 Aurora e Vidro (mg-aurora-glass)

Fundo de manchas de cor bem desfocadas (aurora / mesh gradient) derivando devagar, com cartões de vidro fosco semitransparente por cima. Visual padrão de lançamento de tecnologia e IA 2024–2026: lento, translúcido, sofisticado.

**Esta skill é uma camada fina.** O fluxo completo, o renderizador e os templates estão na skill base
`~/.claude/skills/mg-styles-15/` — **leia `~/.claude/skills/mg-styles-15/SKILL.md` primeiro e siga o fluxo de lá**, usando:

- Prompt do estilo: `~/.claude/skills/mg-styles-15/prompts/12-aurora-glass.md` (leia inteiro; as seções *Signature features* e *Suggested technical route* são obrigatórias)
- Código de referência: `~/.claude/skills/mg-styles-15/demos/12-aurora-glass/`
- Vídeo de exemplo do filme original: `(pasta do Estúdio)/skills_ia/previews/mg-aurora-glass.mp4`

Se `~/.claude/skills/mg-styles-15/` não existir: `git clone --depth 1 https://github.com/Vincentwei1021/mg-styles-15` e copie
`prompts/ demos/ harness/ lib/ assets/ package.json requirements.txt rubric.md template.md LICENSE` para lá.

## Traços obrigatórios (o vídeo é julgado por eles)

- Fundo: 3–5 círculos de cor sólida com blur de 80–150 px, cada um derivando em curva lenta, misturando-se (shader WebGL de mesh gradient).
- Cartões de vidro: blur de fundo 20–40 px + preenchimento branco 5–10% + contorno interno branco 1 px a 30% + cantos bem arredondados.
- Refração/dispersão cromática nas bordas do vidro (lente SDF).
- Cores vizinhas e baixo contraste; ritmo lento, 'respirando'.
- Tipografia fina e limpa, muito espaço.

## Neste estilo

- Formato padrão: vertical 1080x1920, 30 fps, duração = narração. Recomponha o layout do demo para vertical (não estique o 16:9).
- Entrada: roteiro/narração (texto ou áudio pronto). Sem vídeo do usuário.
- Legenda sincronizada: Sans fina e limpa (Inter / Sora Light) dentro de uma pílula de vidro fosco; palavra atual mais clara/brilhante.
- Som: narração na frente; por baixo, baixo volume: Pads etéreos, sinos suaves, nada de batida forte.
- Sem motion blur (ou só onde o prompt pedir).
- Cada cena mostra o que a fala diz, com os elementos do estilo. Não invente fatos, números ou nomes que não estejam no roteiro.

Licença: MIT (c) 2026 Vincentwei1021 — veja `LICENSE`.
