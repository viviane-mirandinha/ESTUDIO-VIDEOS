# 04 — Comparação / ranking animado (RED SIDE · The Infographics Show · Data Is Beautiful)

**Dados:** RED SIDE (EN) 1M inscritos, mediana 915k views, 3.500 views/h nos 45 d (melhor 10.212 v/h) — vídeos de 10-12 min "X mais rápido / mais forte / mais alto". The Infographics Show 15,5M inscritos, mediana 290k, 3.700 v/h ("WW3 hour by hour"). Data Is Beautiful (bar-chart race) mediana 94k, parado.

## Visual (sheet-redsideofficial-*.jpg)
- **RED SIDE:** cena 3D única (deserto/estrada) com personagens 3D correndo em fila, câmera lateral/travelling; **rótulo fixo no rodapé**: nome em vermelho caixa alta + valor ("BOSS BABY 4.82 km/h") + linha pequena "STATUS / CONFIDENCE / INFO". Logo "RED SIDE" no canto. Paleta: céu azul, areia, vermelho do rótulo. Ordem crescente (do mais lento ao mais rápido) = retenção.
- **Infographics Show:** bonecos 2D flat (estilo que já temos no 06-bonecos) + relógio/contador "HOUR 1, HOUR 2" + mapa simples; cada bloco de tempo é um card.
- **Data Is Beautiful:** bar-chart race, fundo escuro, barras coloridas com bandeirinha, ano no canto gigante.
- **Ritmo:** 1 item a cada 15-25 s (RED SIDE); sem corte brusco, a câmera só segue; transição = o próximo item entra em cena. Sem legenda. Texto grande (rótulo ≥ 44px).

## O que é replicável
O 3D cinematográfico do RED SIDE (modelos licenciados de personagens) é **sob-medida e caro**. A versão replicável é **"corrida 2D/2.5D lado a lado"**: fundo parallax (3 camadas PNG), **ícones/recortes/fotos PNG** dos itens avançando numa pista, rótulo vermelho fixo com valor, tamanho/velocidade proporcional ao número. Para "hora a hora" = contador + mapa (reaproveita 01-mapas). Para ranking numérico = bar-chart race (D3/GSAP).

## Template no editor
- `scene: "corrida"` params `{itens:[{nome, valor, unidade, img}], ordem:"asc", pista:"deserto|cidade|espaco"}` — Three.js leve (plano + sprites) ou 2D parallax; cada item entra pela direita, ultrapassa o anterior, câmera trava nele por N s.
- `scene: "rotulo-vermelho"` params `{nome, valor, status}` — rodapé fixo, 48px vermelho + 36px branco.
- `scene: "bar-race"` params `{serie:[{ano, valores}], cores}` — chart race escuro.
- `scene: "contador-hora"` params `{inicio, fim, formato}` + mapa.

## Dificuldade: sob-medida no 1º vídeo, preencher-dados depois (média-alta)
A cena `corrida` precisa ser construída uma vez (câmera, pista, sprite). Depois, cada vídeo é só uma lista `{nome, valor, img}` — o Ollama gera a lista e o Wikimedia/Pixabay dá os PNG. É o estilo com melhor razão "views da referência ÷ trabalho por vídeo" depois de pronto; o risco é a 1ª construção.
