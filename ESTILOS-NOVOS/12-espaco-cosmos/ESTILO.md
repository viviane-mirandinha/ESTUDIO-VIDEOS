# 12 — Espaço / cosmos documentário (Astrum · History of the Universe · Oniverse · Costa Norte)

**Dados:** Astrum (EN) mediana 944k views, 2.300 views/h (melhor 12.000); History of the Universe mediana 973k, 1.480 v/h (vídeos de 1 h = watch-time); Oniverse (PT) mediana 157k, 335 v/h; Costa Norte (ES) mediana 62k, 350 v/h (melhor 1.260). Nicho estável, mídia 100 % livre.

## Visual
- **Astrum:** imagens reais NASA/ESA/JWST em tela cheia com **pan/zoom lento**; renders 3D de planeta girando (fundo preto estrelado); **texto mínimo**: nome do objeto em sans fina branca no canto inferior ("Euclid · ESA, 2024") e, às vezes, número grande (distância, temperatura) centralizado; crédito pequeno. Paleta: preto, branco, azul/dourado das nebulosas.
- **History of the Universe:** mais cinematográfico, render 3D com partículas, títulos de capítulo em serifa fina com tracking aberto, música orquestral; ritmo lentíssimo (10-20 s por plano).
- **Oniverse / Costa Norte (PT/ES):** mesmo molde com imagens geradas + stock, texto maior e mais colorido, cortes mais rápidos (4-6 s).
- **Ritmo:** planos de 6-15 s, crossfade 1 s (não corte seco), zoom contínuo, sem legenda; música ambiente espacial contínua; sem SFX.

## Mídia
NASA Image Library / ESA / ESO / JWST (domínio público ou CC — crédito obrigatório da ESO/ESA), Three.js para planeta/estrela com textura NASA (texturas livres de planetas existem em alta), partículas canvas. Zero risco de Content ID.

## Template no editor
- `image` tela cheia `motion: pan_left|zoom_in 0.06-0.1`, crossfade 1 s (`in: fade, out: fade`), filtro leve de contraste.
- `scene: "planeta-3d"` params `{textura: "marte|jupiter|terra|lua|sol", rotacao, luz, anel}` — Three.js esfera com textura (reaproveita kit clay/13-3D).
- `scene: "capitulo-serifa"` params `{titulo, sub}` — serifa fina (Cormorant) 64px, tracking 0.2em, fade 1,5 s.
- `scene: "numero-espaco"` params `{valor, unidade, legenda}` — número grande com contagem sobre estrelas.
- `text` crédito 24px canto inferior direito (obrigatório).
- `html` fundo de estrelas com parallax leve (canvas).

## Dificuldade: preencher-dados (fácil)
Mais fácil que o historia-simples: a busca de imagem é por nome de objeto (API NASA images, local), o Ollama lista `{objeto, fato, numero}`; 2 cenas 3D opcionais. Vídeo de 1 h (estilo "para dormir") sai do mesmo molde com ritmo mais lento — watch-time alto.
