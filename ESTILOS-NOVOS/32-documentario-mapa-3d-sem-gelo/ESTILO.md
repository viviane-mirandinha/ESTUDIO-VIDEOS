# 32 — Documentário "X sem Y": mapa 3D de relevo + cortes + números amarelos (Unseen Works)

**Dados:** Unseen Works (EN), canal novo (3 vídeos); "What Antarctica Looks Like Without Ice" **1,1M views em ~7 dias** (~6.500 views/h), 11 min. Fórmula: "Como seria [lugar] sem [água/gelo/cidade]" + "tiramos a tampa e olhamos embaixo". Roteiro em capítulos curtos, cada um com 1 fato-surpresa + comparação concreta (Burj Khalifa, Mar Morto, Lago Michigan) + desmentido ("NOT QUITE").

## Visual (sheet-unseenworks-*.jpg)
- **Fundo azul-marinho escuro** (#0f1b2a) com vinheta; globo/continente vindo do espaço (imagem de satélite).
- **Mapa 3D de relevo** (estilo BEDMAP: azul-turquesa abaixo do mar → verde → amarelo/laranja nas montanhas), câmera oblíqua girando lentamente; versão "com gelo" branca lisa → "sem gelo" relevo. Linha laranja brilhante marca rifts/fossas; círculo tracejado vermelho marca anomalias.
- **Cortes transversais 2D** (bloco de gelo azul-claro sobre rocha marrom, mar azul) com seta/linha amarela de medida + rótulo — explica radar, lagos, perfuração.
- **Números gigantes amarelos** (Montserrat/Anton black, ~110px, amarelo #f5c518, contorno escuro) + subtítulo branco caixa-alta pequeno embaixo ("OF ICE", "SEA LEVEL IF IT ALL MELTED").
- **Rótulo lower-third**: barra vertical amarela + texto branco caixa-alta bold sobre caixa preta translúcida ("60 YEARS OF RADAR FLIGHTS", "BLOOD FALLS · TAYLOR GLACIER"), canto sup.-esq. ou inf.-esq.
- **Capítulos**: faixa preta horizontal no meio da tela, "CHAPTER 01" pequeno + título branco ("THE LID", "FIRE UNDER ICE", "WHO OWNS IT ALL").
- **Carimbo vermelho** rotacionado ("NOT QUITE", "CONTAMINATION (2024)") sobre fundo escuro com pergunta branca em cima ("90% UNMAPPED?").
- **Split-screen** 2 fotos com rótulo (Sahara × Antártida, Dry Valleys × Marte, Europa × Lago Vostok); comparação de escala (Burj Khalifa × barra de gelo); grade de ícones (138 triângulos = vulcões); linha do tempo simples.
- **Stock real**: voo sobre gelo, navio quebra-gelo, acampamento, geleira, lava, cavernas de gelo; prints de artigo científico com marca-texto amarelo.
- Ritmo: corte a cada 4-7 s; narração calma de documentário; música ambiente; **sem legenda corrida**.

## Template no editor
- `scene: "relevo-3d"` params `{regiao, modo: "gelo|sem-gelo|transicao", destaque:[{tipo:"linha|circulo", coords, label}], cam_orbita}` — Three.js com heightmap (PNG em tons de cinza) + paleta hipsométrica.
- `scene: "corte-2d"` params `{camadas:[{tipo:"gelo|rocha|agua|lago", altura}], medida:{valor, label}, setas}` — SVG + GSAP.
- `scene: "numero-grande"` `{valor, sub}`; `scene: "capitulo"` `{n, titulo}`; `scene: "carimbo"` `{pergunta, carimbo}`; `scene: "split"` `{a:{src,label}, b:{src,label}}`; `scene: "escala"` `{objeto, altura_m, valor_m}`.
- `image`/`video` stock com `text` lower-third barra amarela (≥ 28px no nosso canvas 1280x720).

## Dificuldade: média-alta
Relevo 3D precisa de heightmap por lugar (ETOPO/GEBCO/BEDMAP em domínio público). Resto é tipografia + SVG reaproveitável. Formato transfere bem pra ES/PT ("Así se vería X sin agua", "Como seria o Brasil sem a Amazônia").
