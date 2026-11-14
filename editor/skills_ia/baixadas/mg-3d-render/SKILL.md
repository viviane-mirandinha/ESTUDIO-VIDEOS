---
name: mg-3d-render
description: "Vídeo vertical em motion graphics no estilo \"3D Render (Blender)\" (repositório mg-styles-15, MIT) feito 100% por código a partir de roteiro ou narração, com legenda sincronizada. Objetos 3D com material de verdade (borracha macia, vidro, metal), luz de estúdio e desfoque de fundo. Visual premium de comercial. Precisa do Blender e é o mais lento de renderizar. Use quando pedirem esse estilo ou quando o painel Estúdio de Vídeos mandar `mg-3d-render`."
---

# 🧊 3D Render (Blender) (mg-3d-render)

Animação com acabamento de Cinema 4D/Blender: borracha macia, vidro, metal, tecido, com arrays de clones e simulação física. Padrão de filme de produto (celular, bebida, tênis) e vinheta de marca.

**Esta skill é uma camada fina.** O fluxo completo, o renderizador e os templates estão na skill base
`~/.claude/skills/mg-styles-15/` — **leia `~/.claude/skills/mg-styles-15/SKILL.md` primeiro e siga o fluxo de lá**, usando:

- Prompt do estilo: `~/.claude/skills/mg-styles-15/prompts/04-3d-render.md` (leia inteiro; as seções *Signature features* e *Suggested technical route* são obrigatórias)
- Código de referência: `~/.claude/skills/mg-styles-15/demos/04-3d-render/`
- Vídeo de exemplo do filme original: `(pasta do Estúdio)/skills_ia/previews/mg-3d-render.mp4`

Se `~/.claude/skills/mg-styles-15/` não existir: `git clone --depth 1 https://github.com/Vincentwei1021/mg-styles-15` e copie
`prompts/ demos/ harness/ lib/ assets/ package.json requirements.txt rubric.md template.md LICENSE` para lá.

## Traços obrigatórios (o vídeo é julgado por eles)

- Materiais PBR realistas, profundidade de campo rasa, luz de estúdio suave (HDRI + três pontos).
- Clonador/array de objetos com ondas de animação em grupo (efeito MoGraph).
- Corpos macios que colidem e assentam; cores de bala de goma.
- Rota: script `bpy` do Blender (Cycles com denoise, ou EEVEE) → sequência PNG → ffmpeg; tipografia por cima em HTML (veja `demos/04-3d-render/README.md`).
- Sem Blender: versão Three.js com MeshPhysicalMaterial + HDRI de `assets/hdri/` (anote em DECISOES.md).

## Neste estilo

- Formato padrão: vertical 1080x1920, 30 fps, duração = narração. Recomponha o layout do demo para vertical (não estique o 16:9).
- Entrada: roteiro/narração (texto ou áudio pronto). Sem vídeo do usuário.
- Legenda sincronizada: Sans limpa e grande (Inter / DM Sans) em branco ou na cor do material, aparecendo suave por baixo do objeto, sem competir com o 3D.
- Som: narração na frente; por baixo, baixo volume: Ambiente suave, impactos macios e graves quando os objetos pousam.
- Use motion blur (`--mb 4`) nos movimentos rápidos.
- Cada cena mostra o que a fala diz, com os elementos do estilo. Não invente fatos, números ou nomes que não estejam no roteiro.

Licença: MIT (c) 2026 Vincentwei1021 — veja `LICENSE`.
