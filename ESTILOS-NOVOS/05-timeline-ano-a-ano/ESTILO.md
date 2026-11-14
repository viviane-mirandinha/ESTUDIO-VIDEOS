# 05 — Linha do tempo / mapa data a data (Atlas Unfolded · AtlasNumbers · History Matters · ENMINUTOS)

**Dados:** Atlas Unfolded (EN, canal pequeno, mediana 30k, 500 views/h; "The Entire Ukraine War in 25 min") e AtlasNumbers ("History of the World: Every Year", mediana 72k, 480 v/h) são canais novos que provam o molde. History Matters (EN, 1,9M, mediana 686k, 2.160 v/h) é a versão flat-cartoon de 9 min. ENMINUTOS (ES, mediana 58k, 1.300 v/h) é o equivalente em espanhol.

## Visual (sheet-atlas-unfolded-*.jpg)
- **Mapa** em relevo (terreno verde/marrom, estilo satélite estilizado) ocupando a tela; **linha de frente laranja** que se move; áreas controladas em marrom translúcido; ícones de tanque/soldado pequenos sobre o mapa.
- **Pílula de data** no canto superior esquerdo: caixa preta com data em amarelo/vermelho/azul ("17 FEB 2024") + legenda cinza embaixo (fonte, "aproximado").
- **Título da cena** no topo centralizado: **sans condensada bold branca caixa alta** com sombra ("THAT LINE", "AVDIIVKA FALLS"), 56-64px, fundo às vezes com tarja ciano/amarela atrás de 1 palavra.
- **Cards claros** intercalados (fundo cinza-claro): palavra gigante azul com sublinhado vermelho rabiscado ("FROZEN?") + definição + 2 pílulas azul-petróleo. Quebra o ritmo do mapa a cada ~60-90 s.
- **Cards de ícones** (munição / soldados / dinheiro) em caixinhas pretas com borda.
- **CTA:** "QUICK PAUSE" + botões LIKE / FOLLOW desenhados no mapa.
- **Ritmo:** cada data = 1 cena de 5-12 s (zoom no ponto do mapa + seta vermelha + título); corte seco entre datas; música épica baixa; sem legenda.

## Mídia
100 % gerado: GeoJSON (countries50m + relevo via tile raster livre ou shading procedural), ícones SVG, zero foto. Data e evento vêm do roteiro.

## Template no editor
- `scene: "mapa-timeline"` params `{foco:{lat,lon,zoom}, data, titulo, frente:[[lat,lon],...], areas:[...], setas:[...]}` — base do 01-mapas com 3 camadas novas (frente, área marrom, pílula de data).
- `scene: "card-palavra"` params `{palavra, sub, pilulas:[]}` — fundo claro.
- `scene: "card-icones"` params `{itens:[{icone, rotulo}]}`.
- `text` título topo 60px condensado (Oswald/Bebas) com sombra.
- `scene: "contador-ano"` params `{de, ate, dur}` para versão "every year".

## Dificuldade: preencher-dados (fácil-média)
Reaproveita o 01-mapas; novidade é só frente/área/pílula de data e os 2 cards. O Ollama entrega lista `{data, lugar, evento, titulo_curto}`; geocodificação local (tabela de cidades). Vídeo de 25 min = 120-150 cenas iguais → ideal pra fábrica.
