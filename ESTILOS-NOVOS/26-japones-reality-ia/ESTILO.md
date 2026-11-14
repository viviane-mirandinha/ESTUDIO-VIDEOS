# 26 — Japonês: reality/vlog gerado por IA com legenda amarela (genel_ai · mikinoyarinaoshi)

**Dados:** genel_ai (JP, "デヴ上等 Prime — Everyone's Extra-Large") mediana **198k views**, 510 views/h (melhor 2.300), 8 min, 15 vídeos; mikinoyarinaoshi (JP, "47 anos, primeiro desapego da vida…") mediana 31k, 45 v/h (melhor 1.900), 12 min, 8 vídeos. Nota do usuário: pouca edição, ser criativo, poucos tokens.

## Visual
- **genel_ai:** "reality show" de pessoas plus-size geradas por IA (apartamento de luxo, sofá, cozinha, praia) — personagens consistentes entre cenas; **legenda japonesa amarela/branca grande com contorno preto** (estilo TV japonesa) com nome do personagem + fala; cortes 3-5 s; câmera fixa de sitcom; sem narração (ou narrador TV); trilha pop.
- **mikinoyarinaoshi:** vlog de mulher de 47 anos arrumando a casa (cômodo bagunçado, sacolas, pia) — provavelmente IA também (estilo Veo, câmera fixa) ou real; **legenda branca pequena** no rodapé a cada frame, narração em 1ª pessoa, cortes 5-8 s, luz natural; zero gráfico.

## O que replicar (edição mínima)
- **Legenda estilo TV japonesa** (fonte gorda, amarelo #ffe600 com stroke preto 6px, nome do personagem em caixa colorida) — 1 cena.
- Clipes de 5-8 s do avatar/cenário (LTX i2v a partir de imagens-mestras; 3-4 personagens × 4 cenários). Mesmo princípio de consistência do 17.
- Sem SFX, sem zoom. Trilha única.
- Variante mikino: 1 personagem, imagens IA de cômodos antes/depois + narração TTS japonesa (edge-tts ja-JP Nanami) + legenda branca pequena.

## Template no editor
- `video` clipes gerados em sequência + `caption`/`text` estilo TV (`stroke` preto, 56px, amarelo) com `scene: "nome-personagem"` params `{nome, cor}`.
- `scene: "titulo-episodio"` params `{texto}` — card de abertura estilo variedade japonesa (fundo colorido, texto inclinado).
- `image` antes/depois com wipe (`scene: "antes-depois"` params `{a, b}`).

## Dificuldade: preencher-dados (fácil) na edição; custo todo na geração de clipes
Roteiro curto (8 min, diálogo simples) pelo Ollama em japonês (qwen lida; conferir com regra "100 % idioma"), TTS japonês local/edge. Edição = 2 cenas. genel_ai tem a melhor mediana do lote 2 depois do ryoga — fórmula "reality IA com legenda TV" é o achado, transferível pra PT/ES ("reality de família", "casa bagunçada").
