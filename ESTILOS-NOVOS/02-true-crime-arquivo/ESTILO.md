# 02 — True crime / arquivo (Dr Insanity · Dieck Docs · Ossos Perdidos · Marcos Campos)

**Dados:** nicho mais quente da mineração — Dr Insanity (EN) mediana 19M views, 22k views/h; Dieck Docs (ES) mediana 2,8M, 11k v/h; em PT Ossos Perdidos (mediana 511k) e Marcos Campos (246k). **Atenção:** Dr Insanity = bodycam/interrogatório real (Court TV) + legenda. Isso NÃO dá pra replicar (footage sem licença). O que se replica é a versão **arquivo**: Dieck Docs / Ossos Perdidos / Marcos Campos.

## Visual (sheet-dieck-docs-*.jpg, sheet-ossos-perdidos-*.jpg)
- **Fundo:** preto total. Foto/filme de arquivo numa **moldura pequena centralizada** (45-55 % da largura), nunca tela cheia — ar de "dossiê". Marca d'água do canal no canto da moldura.
- **Paleta:** preto, branco, **vermelho sangue (#b3121a)** só nos títulos de capítulo. Fotos em P&B ou colorizadas de leve; grão de filme.
- **Fontes:** nomes de pessoas em **sans condensada bold branca** centralizada por cima da foto ("Benito Mussolini"), 44-56px; capítulos em display vermelha caixa alta estilo carimbo/stencil ("¿CÓMO NACE UN DICTADOR?") com leve tremor. Datas em branco pequeno abaixo.
- **Cenas:** foto de arquivo (Ken Burns lento 3-6 s) → corte seco → outra foto; a cada 8-12 fotos um **card de capítulo vermelho sobre preto** (1,5-2 s); mapa escuro com ponto vermelho (local do crime); documento/jornal escaneado com zoom na manchete.
- **Ritmo:** corte a cada 3-5 s; só corte e fade preto; música tensa contínua; sem legenda (Dr Insanity usa porque é fala real).

## Mídia
Foto (Wikimedia Commons: criminosos históricos, polícia, jornais), footage de arquivo público (Prelinger / Internet Archive), mapa escuro gerado (GeoJSON), texturas de papel/grão. Casos históricos (> 70 anos) = material público, sem Content ID.

## Template no editor
- `image` com `w:640 h:400 x:640 y:340 motion:zoom_in|pan 0.08-0.12 fit:cover`, borda 1px #333. Alternar moldura 4:3 e 16:9 pequenas.
- `text` nome sobre a foto (`y:520`, 48px, weight 800, `shadow`).
- `scene: "capitulo-vermelho"` params `{texto, numero}` — fundo preto, texto vermelho stencil com shake 2px e fade.
- `scene: "mapa-ponto"` params `{lat, lon, label}` reaproveitando o mapa do 01-mapas em versão escura.
- `html` vinheta + grão (já existe no estilo historia-simples) — copiar.
- Áudio: música tensa baixa com `duck: true`.

## Dificuldade: preencher-dados (fácil)
É o `historia-simples` (04) com 4 mudanças: fundo preto + moldura pequena, nome sobre a foto, card vermelho de capítulo, mapa-ponto. Roteiro Ollama com estrutura fixa (descoberta → suspeito → investigação → julgamento). Regra: só casos históricos ou com cobertura pública ampla; scrub factual obrigatório (memória "escândalo pessoa real").
