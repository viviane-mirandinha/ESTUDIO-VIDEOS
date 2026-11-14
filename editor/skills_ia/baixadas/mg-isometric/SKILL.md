---
name: mg-isometric
description: "Vídeo vertical em motion graphics no estilo \"Isométrico 2.5D\" (repositório mg-styles-15, MIT) feito 100% por código a partir de roteiro ou narração, com legenda sincronizada. Mundo em miniatura visto em perspectiva isométrica: prédios e peças crescendo, câmera deslizando em trilhos. Bom pra mostrar sistema, processo, negócio crescendo, tecnologia. Use quando pedirem esse estilo ou quando o painel Estúdio de Vídeos mandar `mg-isometric`."
---

# 🏙️ Isométrico 2.5D (mg-isometric)

Projeção isométrica de 30° mostrando um mundo em miniatura (cidade, escritório em corte, sala de servidores), sem ponto de fuga. Muita informação sem perder a fofura; padrão em animação de arquitetura de sistemas e demonstração de app.

**Esta skill é uma camada fina.** O fluxo completo, o renderizador e os templates estão na skill base
`~/.claude/skills/mg-styles-15/` — **leia `~/.claude/skills/mg-styles-15/SKILL.md` primeiro e siga o fluxo de lá**, usando:

- Prompt do estilo: `~/.claude/skills/mg-styles-15/prompts/03-isometric.md` (leia inteiro; as seções *Signature features* e *Suggested technical route* são obrigatórias)
- Código de referência: `~/.claude/skills/mg-styles-15/demos/03-isometric/`
- Vídeo de exemplo do filme original: `(pasta do Estúdio)/skills_ia/previews/mg-isometric.mp4`

Se `~/.claude/skills/mg-styles-15/` não existir: `git clone --depth 1 https://github.com/Vincentwei1021/mg-styles-15` e copie
`prompts/ demos/ harness/ lib/ assets/ package.json requirements.txt rubric.md template.md LICENSE` para lá.

## Traços obrigatórios (o vídeo é julgado por eles)

- Projeção isométrica verdadeira (câmera ortográfica Three.js no ângulo isométrico, ou faces SVG com matriz escala 86,6% → cisalhamento ±30° → rotação ∓30°).
- Sem perspectiva: tudo do mesmo tamanho em qualquer profundidade; ordem de desenho pelo y da tela.
- Prédios/objetos crescendo do chão com escalonamento; movimento na grade com inclinação de 2:1.
- Câmera em trilho paralelo (desliza, não gira); sombras suaves e AO.
- Cena miniatura densa e organizada, cores pastel vivas.

## Neste estilo

- Formato padrão: vertical 1080x1920, 30 fps, duração = narração. Recomponha o layout do demo para vertical (não estique o 16:9).
- Entrada: roteiro/narração (texto ou áudio pronto). Sem vídeo do usuário.
- Legenda sincronizada: Fonte larga e pesada (Unbounded / Sora) em placas isométricas ou etiquetas flutuando sobre a cena.
- Som: narração na frente; por baixo, baixo volume: Eletrônica leve e alegre, cliques de construção a cada peça que nasce.
- Sem motion blur (ou só onde o prompt pedir).
- Cada cena mostra o que a fala diz, com os elementos do estilo. Não invente fatos, números ou nomes que não estejam no roteiro.

Licença: MIT (c) 2026 Vincentwei1021 — veja `LICENSE`.
