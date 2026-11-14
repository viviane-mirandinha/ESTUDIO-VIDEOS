# 21 — Cards de produto / "this or that" / review de objetos (YourVibeChoice · Desk Standard)

**Dados:** YourVibeChoice (EN) mediana 20k views, 30 views/h (melhor 420), 12 min; Desk Standard (EN, "7 Walmart pens everyone ignores") mediana 15k, 87 v/h (melhor 1.600), 20 min. Views modestos, mas é o estilo de **menor custo de produção de todo o catálogo** (zero vídeo, zero voz obrigatória no VibeChoice).

## Visual
- **YourVibeChoice:** fundo branco com textura de papel e rabiscos vermelhos (estrelas, corações); **card "Choose your outfit aesthetic — This or That"** com 2 fotos de produto recortadas (PNG sem fundo) lado a lado e "or" no meio; cards de seção ("getti ready", "beauty") em serifa itálica vermelha; troca a cada 4-6 s; música pop baixa; sem narração.
- **Desk Standard:** fotos/clipes de produto (canetas) em fundo quadriculado branco, close de mão escrevendo, prateleira de loja, **tabela comparativa** (especificações em cinza), preço "2 • $1" grande; narração calma.

## Template no editor
- `scene: "this-or-that"` params `{titulo, a:{img, rotulo}, b:{img, rotulo}}` — 2 PNGs com sombra, "or" central, fundo papel.
- `scene: "secao-serifa"` params `{texto}` — itálica vermelha + rabiscos SVG.
- `scene: "tabela-specs"` params `{linhas:[{nome, valor}]}` e `scene: "preco"` params `{valor, unidade}`.
- `image` produto `fit: contain` em fundo quadriculado + `motion: pan`.
- Música `volume 0.3` (sem voz) ou `audio.voice` + `duck`.

## Mídia
PNG de produto: fotos CC0 (Unsplash/Pexels) recortadas localmente (rembg/hyperframes remove-background) ou geradas (Flux, "product photo on white"). Nunca foto oficial de loja (direitos).

## Dificuldade: preencher-dados (trivial)
Lista `{titulo, a, b}` vem do Ollama; 1 cena. Dá pra gerar dezenas por hora. Views baixos na referência — serve como canal de volume/teste ou shorts; o Desk Standard (review) exige narração e tabela, ainda fácil.
