# 24 — "Quando o diretor…" com cenas de filme · ciência com imagens (Director's Cut · Known Matter)

**Dados:** Director's Cut (EN) 3 vídeos, mediana **1,2M views**, 1.047 v/h no melhor ("When the Director Uses REAL Bullets", "…Hires a REAL Drill Instructor" 1M+) — canal recém-criado com fórmula explosiva. Known Matter (EN, "They turned brain activity into images") mediana 207k, 707 v/h, 2 vídeos. Nota do usuário: filmes, precisa ter cenas de filme.

## Visual
- **Director's Cut:** cenas do filme (Come and See, Full Metal Jacket…) em tela cheia, **sem moldura**, com **card de capítulo** ("Chapter 1: The Brutality of War") em sans branca pequena sobre o frame; rótulo de personagem/ator em branco; fotos P&B de bastidores; narração calma; cortes 4-8 s; sem legenda; 8-10 min.
- **Known Matter:** foto/objeto fixo (ursinho) centralizado sobre preto + fotos de experimento (fMRI, telas), diagramas simples brancos sobre preto ("Operator / Subject"), imagens de reconstrução neural; texto mínimo.

## Replicável?
- Cenas de filme = **fair use só com comentário/crítica real** e trechos curtos; mesmo assim Content ID bloqueia/monetiza para o estúdio. Alternativas: **trailers oficiais** (tolerados), **fotos de bastidores/stills** com Ken Burns (menor risco), **recriação por IA** das cenas (LTX/Flux, "no estilo de"), e manter 60 % do tempo em stills/documentos. Canal de 3 vídeos com 1,2M mediana mostra que a **premissa** ("o diretor fez X de verdade") é o motor — a premissa sobrevive sem o clipe inteiro.
- Known Matter: 100 % replicável (fotos de papers abertos, diagramas nossos, objeto gerado).

## Template no editor
- `video` trecho curto (≤ 6 s) ou `image` still `motion: zoom_in` + `scene: "capitulo-pequeno"` params `{n, titulo}` (sans 32px canto inferior esquerdo, fundo semitransparente).
- `text` rótulo de personagem 36px.
- `scene: "diagrama-branco"` (do 09) e `scene: "objeto-centro"` params `{img, legenda}` para o Known Matter.

## Dificuldade: preencher-dados (fácil) na edição; **risco legal médio-alto** nos clipes
Fábrica: roteiro Ollama sobre "bastidores reais" (fato na premissa: só casos documentados), mídia = stills Wikimedia/press kits + trailer. Testar em canal separado por causa do Content ID.
