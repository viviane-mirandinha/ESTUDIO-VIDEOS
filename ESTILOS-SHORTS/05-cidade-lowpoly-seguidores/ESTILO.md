# Estilo 05 — cidade lowpoly seguidores

Referência: homietown.city · 9:16 720x1280 30 fps
44,3 mil seguidores com só 5 posts; o grid mostra contagens baixas (341/309) — o crescimento vem da mecânica 'cada seguidor ganha uma casa', não das views. Inglês.

## Visual
- **Cidade 3D isométrica low-poly** (jogo de construção mobile): grade de ruas, gramados, palmeiras, carros, praia ao fundo, "CITY HQ" dourado com tapete vermelho, prefeitura com cúpula verde.
- Câmera em voo de drone: aproxima de uma casa branca vazia → rótulos amarelos "HOUSE / STREET / NUMBER" → afasta mostrando a cidade gigante com milhares de casas.
- Placa da casa com @ do seguidor; contador "5 residents!" em amarelo com contorno.

## Legenda
- Frase inteira pequena, branca com contorno preto (padrão TikTok), meio da tela. Letra pequena (abaixo da regra de 48px do usuário → ampliar ao replicar).

## Ritmo / voz
- Voz masculina animada (TTS EN), ~170-190 ppm, **20-27 s** (bem curto). Plano contínuo, quase sem corte (só movimento de câmera).
- Gancho 0-3 s: promessa/mecânica — "One follower equals one house. Welcome to Homie Town!"
- CTA duplo: "top-liked comment decides what we build tomorrow" + "your house is waiting through the link in bio" (série diária "Day 2...").

## Como replicar (grátis/local)
- Three.js procedural: InstancedMesh pra centenas de casas/árvores/carros numa grade; prédios marco (HQ, prefeitura) com primitivas; câmera GSAP. **Dificuldade média**; a cidade fica reaproveitável e cresce a cada episódio (só adicionar casas + nomes).
- Em PT-BR: "Cada seguidor ganha uma casa" — mecânica de comunidade, não de informação.
