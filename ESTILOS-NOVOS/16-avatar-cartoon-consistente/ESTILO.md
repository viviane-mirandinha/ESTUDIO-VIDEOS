# 16 — Avatar cartoon consistente (One Small If · Agent Flappy)

**Dados:** One Small If (EN) mediana 38k views, 320 views/h (melhor 1.900), vídeos de 6 min; canal novo (7 vídeos). Agent Flappy (EN) mediana 117k, 200 v/h, 22 min ("Gulf War explained"). Pedido do usuário: manter consistência do avatar.

## Visual
- **One Small If:** 1 personagem fixo (boneco verde de cabeça preta redonda, olhos brancos, estilo 3D simples/low-poly) em cenários suburbanos americanos 3D (casa, garagem, rua, ônibus escolar); câmera fixa por cena; **HUD fixo no topo** (hora/dia + contadores) o vídeo todo; cortes a cada 3-5 s; barras pretas (letterbox). Paleta pastel realista. Sem legenda. Premissa "e se" (what if).
- **Agent Flappy:** águia cartoon 2D (traço grosso, cores chapadas) + figuras históricas desenhadas no mesmo traço (Saddam etc.), fundos pintados simples (deserto, pôr do sol), mapas flat com bandeiras e setas, cards de data ("AUGUST OF 1988", "FEBRUARY 26, 1991") em sans bold branca; explosões cartoon; cortes a cada 3-5 s.

## Consistência do avatar (o ponto do usuário)
- **Cartoon 2D (Flappy):** consistência é trivial — é um **rig SVG/PNG** (corpo + 6 cabeças/emoções + 4 braços) reusado em todos os vídeos. Zero IA. 100 % HTML/GSAP.
- **3D simples (One Small If):** avatar como **modelo GLB fixo** (Ready Player Me / Mixamo, estilo low-poly) em Three.js com 5-6 animações (idle, andar, apontar, surpresa); cenários = kits low-poly CC0 (Kenney, Poly Pizza). Consistência total porque é o mesmo arquivo. Alternativa IA (LTX/Veo com referência) **não** garante consistência — evitar.

## Template no editor
- `scene: "cena-3d-avatar"` params `{cenario: "casa|rua|escola|garagem", pose, acao, camera}` — Three.js (kit do 09/13) com GLB fixo.
- `scene: "hud"` params `{hora, dia, contador}` — barra fixa no topo.
- `scene: "ator-2d"` params `{personagem, emocao, pose, x, y}` (igual ao 07) + `scene: "mapa-cartoon"` do 07 + `scene: "card-data"`.
- `text` cards de data 56px bold.

## Dificuldade
- 2D (Flappy): **preencher-dados média** depois de 1 rig (sob-medida pequeno; reusa o 07).
- 3D (One Small If): **sob-medida média-alta** no 1º (avatar + 6 cenários + câmeras), depois preencher-dados: Ollama escreve `{cenario, acao, fala}` por cena.
