# 18 — Comentário com prints, edição mínima (Nômade Digital Raiam · Critical Latitude · Prosecutor Matthew Hanson · FlashPoint)

**Dados:** Nômade Digital Raiam (PT) mediana 68k views, **1.160 views/h** (melhor 5.900), 20 min — o maior v/h do lote 2. Critical Latitude (EN) mediana 264k, 770 v/h (melhor 5.600). Prosecutor Matthew Hanson (EN) mediana 69k, 390 v/h. FlashPoint (talk show de TV, não replicável).

Pedido do usuário: **mesmos assuntos, edição a mais simples possível**. Esses canais são talking-head sem edição; a versão faceless troca a pessoa por **voz + prints + 1 elemento visual fixo**.

## Visual
- **Raiam:** homem falando em fundo noturno de cidade, **prints de tweet/post em tela cheia** (texto longo, scroll lento) por 10-20 s cada, 1-2 b-rolls (Matrix, skyline) em 20 min. Zero gráfico, zero legenda. O vídeo é o assunto (polêmica do dia + opinião).
- **Critical Latitude:** mulher falando + mapas de corrente oceânica (linha vermelha sobre mapa claro), gráficos de série temporal "CRITICAL SLOWING DOWN", fotos de enchente, globo 3D; sans branca sobre preto nos títulos.
- **Hanson:** ex-promotor comenta bodycam (reação) — footage de polícia (não replicável) + ele na frente dos diplomas.

## Versão faceless "edição simples" (o que o usuário pediu)
- Fundo fixo: cidade à noite desfocada (foto/loop) ou gradiente escuro.
- **Print do post** (gerado em HTML, layout genérico, sem logo) ocupando 70 % da tela, com **scroll lento** sincronizado com a leitura; palavras-chave em **marca-texto amarelo** quando a voz chega nelas (words.json).
- **Título do tema** fixo no topo (sans bold 48px) + barra de progresso "ponto 1/5".
- A cada 2-3 min um b-roll de 8 s (Pexels) ou mapa/gráfico simples (Critical Latitude).
- Opcional: **avatar** do 16/17 no canto (picture-in-picture) só em 20 % do tempo.

## Template no editor
- `scene: "print-post"` params `{autor, handle, texto, data, destaques:[]}` — card de post genérico + scroll + marca-texto.
- `text` título fixo + `scene: "progresso"` params `{atual, total}`.
- `video` b-roll `opacity 0.9`; `scene: "mapa-linha"` (do 05) e `scene: "grafico-linha"` (do 13) para a variante Critical Latitude.
- `audio.voice` + música lo-fi `volume 0.08 duck`.

## Dificuldade: preencher-dados (muito fácil)
A fábrica já faz tudo: roteiro Ollama a partir do tema do dia (mix notícia/evergreen), TTS, whisper, 1 cena nova (`print-post`). O valor está em **tema quente + opinião** (regra "ideia serve o momento"), não na edição. Idiomas: PT comprovado (Raiam), EN (Critical Latitude nicho clima).
