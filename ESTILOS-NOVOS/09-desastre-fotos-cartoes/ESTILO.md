# 09 — Desastre / tragédia com fotos e cartões de texto (Fascinating Horror · Scary Interesting · Plainly Difficult)

**Dados:** Fascinating Horror (EN) 1,46M inscritos, mediana 420k views, 1.800 views/h (melhor 5.400); Scary Interesting mediana 899k, 1.900 v/h (melhor 9.000); Plainly Difficult mediana 256k, 500 v/h. Em PT a busca achou "Investigation" (mediana 110k, pico 27k v/h) e "Mayday: Desastres Aéreos"; em ES "Raquel de la Morena" (mediana 383k).

## Visual
- **Fascinating Horror:** foto de arquivo (P&B ou cor desbotada) em tela cheia com **zoom lentíssimo** (3-8 % em 8-10 s); **cartões de texto em fundo preto** entre fotos: data/local em serifa branca fina ("Hillsborough Stadium · 15 April 1989"), centralizados, com fade; às vezes **diagrama simples** (planta, mapa) desenhado em linhas brancas sobre preto. Paleta: preto, branco, sépia. Narração calma, música ambiente grave, sem SFX. Sem legenda.
- **Scary Interesting:** mais b-roll e imagens geradas/recriações, mapa com rota, texto sans branco bold grande, música tensa; cortes mais rápidos (3-5 s).
- **Plainly Difficult:** gráficos "feios de propósito" (flat, cores primárias), diagrama animado do acidente (setas, ícones), fundo bege; bem cartunesco.
- **Ritmo (FH):** 1 foto a cada 6-10 s; cartão a cada 3-5 fotos; estrutura fixa: contexto → o dia → a falha → consequências → "o que mudou". Vídeos de 9-12 min.

## Mídia
Fotos de arquivo (Wikimedia Commons, Library of Congress, National Archives: acidentes, incêndios, naufrágios, pontes), mapas GeoJSON, diagramas SVG simples, b-roll Pexels (mar, fogo, hospital). Tudo livre.

## Template no editor
- `image` tela cheia `motion: zoom_in 0.05-0.08` com filtro sépia leve (copiar os tints do historia-simples) e vinheta.
- `scene: "cartao-data"` params `{linha1, linha2}` — serifa (Playfair/EB Garamond) 56px + 32px, fundo preto, fade 0,8 s.
- `scene: "diagrama"` params `{tipo: "planta|rota|secao", itens:[...]}` — linhas brancas draw-on sobre preto.
- `scene: "mapa-ponto"` (do 02) para local do desastre.
- Música ambiente `volume 0.1, duck: true`.

## Dificuldade: preencher-dados (fácil)
Praticamente o `historia-simples` com cartões de data e ritmo mais lento. Ollama escreve o roteiro no esqueleto fixo (5 atos) e a lista de buscas de foto; o cartão vem de `{data, local}`. É o estilo mais barato de todo o catálogo novo pra fábrica.
