# 29 — Notícias de IA/tecnologia com robô 3D fixo (There's An AI For That)

**Dados:** There's An AI For That (EN) mediana 30k views, 479 views/h (melhor 4.219); vídeo enviado "We Can Finally Talk To Animals" **532k views** em 6 dias (17 min); outros picos 1,3M e 946k. Canal pequeno com virais frequentes = premissa forte (IA + animais/cérebro/morte).

## Visual (sheet-there-s-an-ai-for-that-*.jpg)
- **Cards de título** sobre textura dourada/ocre ("CAN AI TALK TO ANIMALS?", "2026 — MONTREAL, CANADA") em sans bold branca caixa alta 60px; versão preta ("ASK THEM ANYTHING").
- **Robô 3D branco (mascote fixo)** sentado numa mesa de madeira com bonsai, fundo preto; **balões de chat** brancos aparecem ao lado (pergunta/resposta); "LIVE" vermelho. Consistência total porque é um modelo 3D.
- **Cards azul-blueprint** (#1452c8 com grade) com ilustração técnica de pássaros/baleia e rótulos ("1,000", setas); **card azul liso "CETI"**; print de busca do Google e de site de pesquisa em moldura de TV antiga.
- **Stock de natureza** (baleia, pássaros, mergulhador) em tela cheia; rosto de androide em close.
- Ritmo: cortes 3-6 s; narração rápida; música eletrônica leve; sem legenda.

## Template no editor
- `scene: "robo-mesa"` params `{pose, balao_pergunta, balao_resposta}` — Three.js com GLB fixo (robô CC0 do Sketchfab/Poly Pizza) + mesa + bonsai, luz quente; balões HTML.
- `scene: "card-textura"` params `{texto, sub, cor: "dourado|preto"}`.
- `scene: "blueprint"` params `{svg, rotulos:[], numero}` — fundo azul com grade.
- `scene: "print-busca"` params `{consulta}` (layout genérico) + `scene: "tv-retro"` params `{src}`.
- `video` stock natureza; `scene: "capitulo"` existente.

## Dificuldade: sob-medida média no 1º (robô + 3 cards), preencher-dados depois
Roteiro Ollama a partir de paper/notícia pública (fato na premissa); mídia = stock + cards. Fórmula "IA faz X impossível" é transferível pra PT/ES (gap).
