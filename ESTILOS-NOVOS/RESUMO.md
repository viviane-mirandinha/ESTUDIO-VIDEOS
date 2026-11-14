# RESUMO — 15 estilos novos de edição dark/faceless (catálogo, 22/10/2026)

Mineração: yt-dlp sem cota de API — 41 buscas (PT/EN/ES, filtro "este mês") + 102 canais-semente por estilo = **179 canais medidos** (15 últimos vídeos longos de cada, views/hora pelo `approximate_date`). Tabela completa em `_mineracao/MINERACAO-COMPLETA.md`; dados brutos e scripts em `_mineracao/`.
Cada pasta `NN-nome/` tem: `REFERENCIA.txt` (canal + 2-4 vídeos com videoId, views/h, views, idade), 1 contact-sheet por vídeo (`sheet-canal-videoId.jpg`, 30 frames de 2 trechos de 60 s) e `ESTILO.md` (paleta, fontes, cenas, ritmo, mídia, template no formato do editor, dificuldade).

Os 13 estilos atuais (mapas, negócios, finanças stock, história fotos, iceberg, bonecos 2D, personagem fixo, psicologia sombria, tamanho 3D, ciência motion, mapas ilustrados, reddit, 3D técnico) **não foram refeitos**; estes 15 são adições.

## Ranking: views/hora da referência replicável × facilidade de replicar

"v/h ref" = mediana views/hora (45 d) do melhor canal **cujo visual dá pra copiar** (ex.: no true crime vale o Dieck Docs, não o Dr Insanity de bodycam). Facilidade 1-5 (5 = preencher-dados com o que o editor já tem; 1 = sob-medida pesado). Score = v/h × facilidade.

| # | Estilo | v/h ref | Facil. | Score | Dificuldade (fábrica) | Idiomas com referência |
|---|---|---|---|---|---|---|
| 1 | **02 True crime / arquivo** | 11.148 (Dieck Docs) | 5 | 55.740 | preencher-dados — fácil (historia-simples + fundo preto, moldura, card vermelho) | EN · ES · PT |
| 2 | **15 Kurzgesagt vetor** | 30.264 (Kurzgesagt) | 1 | 30.264 | sob-medida alta (biblioteca de mundos/atores SVG) — e nicho saturado de cópias | EN |
| 3 | **03 Top 10 "captado em câmera"** | 8.691 (Doc Tops) | 3 | 26.073 | preencher-dados — média; gargalo = clipes (gerar com LTX look CCTV) | ES · EN · PT |
| 4 | **10 Caso médico** | 8.334 (Chubbyemu) | 3 | 25.002 | preencher-dados — média; esqueleto de roteiro fixo, 8-10 órgãos GLB | EN · ES (gap PT) |
| 5 | **08 Fern cinematográfico** | 11.441 (Fern) | 2 | 22.882 | sob-medida alta no 1º (4 cenas 3D/CSS), depois média — estilo "premium" | EN |
| 6 | **11 Terror / mistérios escuros** | 4.302 (Chilling Scares) | 5 | 21.510 | preencher-dados — fácil; banco de 50 imagens noturnas serve dezenas de vídeos | EN · PT |
| 7 | **12 Espaço / cosmos** | 2.318 (Astrum) | 5 | 11.590 | preencher-dados — fácil; NASA/ESA livre, vídeos de 1 h | EN · PT · ES |
| 8 | **09 Desastre fotos + cartões** | 1.897 (Scary Interesting) | 5 | 9.485 | preencher-dados — o mais barato do lote (historia-simples + cartão de data) | EN · (PT/ES na busca) |
| 9 | **05 Timeline / mapa data a data** | 2.162 (History Matters) | 4 | 8.648 | preencher-dados — fácil-média; reaproveita 01-mapas + pílula de data | EN · ES |
| 10 | **04 Comparação / ranking animado** | 3.537 (RED SIDE) | 2 | 7.074 | sob-medida (cena "corrida") no 1º, depois só lista `{nome, valor, img}` | EN |
| 11 | **13 Economia com gráficos** | 2.358 (How Money Works) | 3 | 7.074 | preencher-dados — média; metade das cenas já existe (barras, contador); dados de CSV real | EN · ES (gap PT) |
| 12 | **14 Tipografia cinética / filosofia** | 1.176 (Raquel de la Morena) | 5 | 5.880 | preencher-dados — muito fácil (caption + frase-serifa); canal de volume | EN · ES |
| 13 | **06 Guerra top-down** | 1.732 (Kings and Generals) | 3 | 5.196 | preencher-dados — média; 01-mapas + camada de unidades; precisão geográfica | EN |
| 14 | **07 Cartoon países-personagens** | 1.863 (El Robot de Platón) | 2 | 3.726 | sob-medida (biblioteca de personagens) no 1º, depois média | ES |
| 15 | **01 Whiteboard / quadro** | 537 (Academia Play) | 3 | 1.611 | preencher-dados — média; biblioteca inicial (boneco, mão, ícones) | ES · EN |

## Leitura prática

**Pra virar molde primeiro (maior retorno por token):** 02 true-crime-arquivo, 11 terror-escuro, 09 desastre-cartões, 12 espaço, 14 tipografia — os cinco são "preencher-dados" em cima do que a fábrica já tem (`historia-simples` + `caption` + cenas existentes) e cobrem PT/ES. Custo estimado: 1 vídeo-teste cada (~1 sessão) e depois ~0 token.

**Apostas de valor alto que exigem construção:** 08 Fern (estilo premium, 11k v/h), 10 caso médico (8k v/h, gap PT total), 03 top-10 (8,7k v/h, depende de gerar clipes), 05 timeline (ideal pra vídeos de 25-30 min com 150 cenas iguais).

**Deixar por último:** 15 Kurzgesagt (v/h altíssimo, mas sob-medida pesado e saturado), 04 comparação (3D), 07 cartoon (biblioteca grande), 01 whiteboard (v/h baixo na referência).

## O que foi procurado e NÃO entrou (e por quê)
- **Pixel/retrô:** nenhum canal pequeno/médio com tração achado em PT/EN/ES. OverSimplified (mediana 38M) é cartoon único, não pixel. Fica fora.
- **Magnates Media:** já coberto pelo 02-negocios atual (mediana 509k, parado há meses).
- **Memorias de Pez:** os sheets mostram que virou talking-head com tela dividida — não é mais cartoon; substituído por Noticias Ilustradas / El Robot de Platón no estilo 07.
- **True crime bodycam (Dr Insanity, Explore With Us, Red File — 7-19M de mediana):** footage de polícia sem licença; irreplicável. Só a versão arquivo (02).
- **After Skool (whiteboard de ilustrador real):** irreplicável; fica Academia Play.
- **Yarnhub (guerra 3D de personagens, 12,6k v/h):** animação 3D de personagens — fora do alcance HTML/GSAP.
- **Infographics Show "hora a hora":** cabe como variante do 05 (contador + mapa); bonecos já existem no 06-bonecos atual.

## Gaps de idioma vistos nos dados
- **PT:** caso médico (10), economia com gráficos (13), terror escuro (11 — só Marcos Campos), espaço (12 — Oniverse 157k mediana, pequeno). Nenhum canal PT faceless médio achado nos quatro.
- **ES:** top-10 (Doc Tops domina com 4,6M de mediana; os pequenos não aparecem = espaço pra entrar com volume), timeline-mapa (ENMINUTOS 58k mediana).

## Avisos
- Contact-sheets são de 2 trechos de 60 s (25-85 s e meio do vídeo) em 360p; títulos no REFERENCIA podem vir traduzidos pelo YouTube (idioma real está na tag do canal).
- Views/hora de vídeos com menos de 1 dia usam mínimo de 12 h (evita v/h irreal).
- Subs não foram coletados (a extração completa de vídeo levou bot-check; o flat não traz inscritos). Mediana de views por vídeo substitui — e é o critério melhor (regra "testar amplo").
- Todos os 60 contact-sheets gerados (Data Is Beautiful precisou de retry).


---

# LOTE 2 e 3 — canais enviados pelo usuário (22/10/2026, 13 estilos: 16 a 28)

Medidos do mesmo jeito (flat + approximate_date; mediana dos 15 últimos vídeos ≥ 3 min). Quase todos são **canais pequenos/novos** (mediana 0,6k-260k) — o sinal é o pico ou a fórmula do vídeo, não a mediana. Dados brutos em `_mineracao/lote2.json` e `lote3.json`.

| # | Estilo | Referência (mediana views · v/h 45 d · pico v/h) | Facil. | Score | Dificuldade (fábrica) | Idiomas |
|---|---|---|---|---|---|---|
| 1 | **18 Comentário com prints, edição mínima** | Nômade Digital Raiam PT (68k · 1.157 · 5.888) · Critical Latitude (264k · 768 · 5.566) | 5 | 5.785 | preencher-dados muito fácil — 1 cena `print-post`; valor = tema quente | **PT** · EN |
| 2 | **24 Filmes "quando o diretor…" + ciência** | Director's Cut (1,2M · — · 1.047, 3 vídeos) · Known Matter (207k · 707 · 1.411) | 3 | 2.121 | edição fácil; **risco Content ID** nos clipes (usar stills/trailer/recriação IA) | EN |
| 3 | **20 Anime fitness sobre preto** | ryoga.training (222k · 562 · 9.099, 9 vídeos) | 4 | 2.248 | fácil-média; personagem por imagem-mestra + overlay de músculo | EN (gap PT/ES) |
| 4 | **26 Japonês reality IA + legenda TV** | genel_ai (198k · 513 · 2.344) · mikinoyarinaoshi (31k · 45 · 1.930) | 4 | 2.052 | edição 2 cenas; custo = clipes gerados (LTX) | JP (transferível) |
| 5 | **23 Militar footage** | Military Storm (76k · 386 · 1.213) | 3 | 1.158 | **irreplicável** no original; variante 06 + HUD + DVIDS | EN |
| 6 | **16 Avatar cartoon consistente** | One Small If (38k · 319 · 1.911) · Agent Flappy (117k · 202 · 447) | 3 | 957 | 2D = rig SVG (fácil); 3D = GLB fixo (sob-medida média) | EN |
| 7 | **27 Doc stock megaprojetos/aviação** | SIGNUM (23k · 114 · 1.350) · Innovation Core (5,8k, vídeo 503k) · Flightside (6,6k, vídeo 234k) | 5 | 570 | fácil — 03-finanças + rótulo amarelo; outliers virais por premissa | EN (gap PT/ES) |
| 8 | **17 Avatar realista IA** | Healoloogy (44k · 223 · 2.083) · Antiques Gallery (48k · 98 · 3.637) · Nina Cooks (21k · 95 · 1.900) · Glen Pritchard (7k · 27 · 1.602) | 2 | 446 | edição fácil; gargalo = geração de vídeo consistente (imagem-mestra + i2v) | EN |
| 9 | **28 Infográfico escuro dourado "todo X maior do mundo"** | KNOT & RAIL (573 · 2 · 770; vídeo 153k) | 4 | 8 (pico 3.080) | fácil-média — silhueta + barra + mapa dourado; fórmula transferível | EN (gap PT/ES) |
| 10 | **25 Doc regional mapas + dados** | Alabama Revealed (35k · 98 · 1.192) · America Under Construction (5k · 27) · When America Made Everything (7k · 44) · Apprentice's Guide (11k · 10) | 4 | 394 | fácil-média — cenas que já existem (mapas, barras, capítulo); versão PT com IBGE | EN (gap PT) |
| 11 | **21 Cards de produto / this-or-that** | YourVibeChoice (20k · 30 · 424) · Desk Standard (15k · 87 · 1.608) | 5 | 435 | trivial — 1 cena; canal de volume/shorts | EN |
| 12 | **22 Relatos IA com personagem fixo** | Bonafillo Relatos ES (28k · 64 · 1.098, 35 min) · Silas Mercer (5k · 67 · 258) | 5 | 335 | fácil — historia-simples com imagens geradas; roteiro longo | ES · EN (gap PT) |
| 13 | **19 Psicologia flat clara + legenda** | People Patterns Psych (0,9k · 44 · 1.293) | 5 | 220 | fácil — 08-psicologia em versão clara + caption | EN |

| 14 | **29 IA notícias com robô 3D fixo** | There's An AI For That (30k · 479 · 4.219; vídeo 532k) | 3 | 1.437 | média — robô GLB fixo em Three.js + stock + cards azul/dourado | EN (gap PT/ES) |
| 15 | **30 Experimento real (formigas)** | Wild Experiments (1M · 8.462 · 15.920; vídeo 4,4M) | 1 | 8.462 | **irreplicável por HTML** — exige filmar terrário real (hobby barato); variante cartoon só como cutaway | EN |
| 16 | **31 Guerra de espécies: enxames no mapa escuro** | SwarmTheory (34k · 358 · 7.807; vídeos 984k e 2,3M) | 4 | 1.432 | fácil-média — mapa escuro + partículas canvas + macro stock de insetos; fórmula 'X tem medo de Y' | EN (gap PT/ES) |

**Leitura:** o único do lote com v/h de mediana alto é o **18 (Raiam, PT)** — e é o mais barato: confirma o pedido do usuário ("mesmos assuntos, edição simples"). **20, 26 e 24** são fórmulas frescas com mediana alta em canal novo (testar amplo). **16/17/22/26** dependem de **consistência de avatar**: solução única = imagem-mestra + rig/GLB/LoRA/i2v local (ver ESTILO.md de cada), nunca prompt solto por cena.

**Não entram como estilo:** FlashPoint (talk show de TV), Prosecutor Hanson (bodycam real — mesmo caso do Dr Insanity), Military Storm original (footage sem licença).
