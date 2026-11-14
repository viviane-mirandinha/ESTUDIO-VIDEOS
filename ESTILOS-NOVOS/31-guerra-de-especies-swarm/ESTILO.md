# 31 — Guerra de espécies: enxames animados no mapa escuro (SwarmTheory)

**Dados:** SwarmTheory (EN) 12 vídeos, mediana 34k views, 358 views/h (melhor 7.807); vídeo enviado "The Biggest War Between Species on Planet Earth" **984k views** (15 min); "Why Wasps are Terrified of Dragonflies" 2,3M. Fórmula: "X tem medo de Y" / "a maior guerra entre espécies".

## Visual (sheet-swarmtheory-*.jpg)
- **Fundo verde-petróleo escuro** (#0f2a2a) texturizado; **mapas estilizados** (Califórnia, EUA) em relevo escuro com contorno dourado fino e rótulos minúsculos em sans branca ("San Diego County", "30 miles", "NEW YORK").
- **Enxames = partículas**: centenas de pontinhos/setas coloridas (laranja × azul, rosa × amarelo) formando colunas, frentes e "territórios" que avançam no mapa — a cena principal do vídeo; formigas estilizadas 2D (corpo laranja com contorno) em close.
- **Macro stock real** de formigas/insetos (Pexels/Pixabay/Wikimedia vídeo) em tela cheia intercalado; drone de floresta/rio.
- **Escala 3D:** formiga gigante ao lado de humano em cena escura (igual ao 09-tamanho-3D).
- Cameo do apresentador (1 plano) — dispensável.
- Ritmo: cortes 4-7 s; narração épica; música tensa; sem legenda; pouquíssimo texto (rótulos pequenos — no nosso canvas ≥ 28px).

## Template no editor
- `scene: "mapa-swarm"` params `{geo: "estado|pais|mundo", foco, colonias:[{cor, origem, frente:[[lat,lon],...], n}], t}` — base 01-mapas em tema escuro + **canvas de partículas** (GSAP tween da frente, pontos com ruído seeded) — determinístico (sem Math.random sem seed).
- `scene: "coluna-formigas"` params `{cor_a, cor_b, direcao, densidade}` — close 2D das colunas se cruzando.
- `scene: "escala-3d"` (do 09) params `{objeto, altura_m}`.
- `video` macro stock + `html` vinheta; `text` rótulos de lugar 28-32px.

## Dificuldade: preencher-dados (fácil-média)
Uma cena nova (mapa-swarm) sobre o que já existe. Ollama entrega `{especie_a, especie_b, lugar, numeros}`; mídia 100 % livre. Transferível pra PT/ES ("a maior guerra entre espécies do Brasil").
