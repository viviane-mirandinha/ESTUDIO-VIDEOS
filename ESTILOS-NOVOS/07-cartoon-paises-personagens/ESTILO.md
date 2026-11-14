# 07 — Cartoon de países/entidades como personagens (Noticias Ilustradas · El Robot de Platón · CuriosaMente)

**Dados:** Noticias Ilustradas (ES, canal pequeno) mediana 81k views, 1.700 views/h nos 45 d, melhor 10.000 v/h ("FRANCE is in FLAMES!") — ratio alto pro tamanho. El Robot de Platón (ES) mediana 668k, 1.860 v/h. CuriosaMente (ES) mediana 212k, 480 v/h. Memorias de Pez (mediana 345k, 1.220 v/h) foi minerado como referência de cartoon, mas os sheets mostram que **hoje é talking-head com b-roll** — fica só como referência de tema/ritmo.

## Visual (sheet-noticias-ilustradas-*.jpg)
- **Países = personagens:** França é um triângulo amarelo (fatia) com olhos e boné de polícia; multidão = dezenas de bonequinhos vermelhos iguais clonados; "dívida" = caixa com rótulo. Traço grosso preto, cores chapadas saturadas, olhos grandes expressivos (raiva, medo, surpresa).
- **Fundos:** verde-limão (#2ee07a) e ciano (#38d6ff) chapados, prédios cinza simples; fogo em laranja/amarelo flat com contorno. Mapa da Europa chapado (azul-marinho país destacado) com setas e rótulos manuscritos vermelhos ("Lyon", "Marsella").
- **Mistura com foto real:** o personagem cartoon entra **na frente de uma foto/clipe de jornal** (incêndio real) apontando — recurso-chave pra noticiário.
- **Fontes:** rótulos manuscritos (Permanent Marker/Caveat) em vermelho ou preto, 36-44px; pouco texto na tela, a piada visual carrega.
- **Ritmo:** corte a cada 2-4 s, personagem muda de pose a cada frase; zoom-in cômico no rosto; sem legenda; música leve; sem SFX de impacto (só pop suave, opcional).

## Mídia
Vetor/SVG próprio: biblioteca de **formas-país com rosto** (país = silhueta do mapa ou "forma símbolo" + olhos/boca intercambiáveis), bonequinho genérico clonável, 10 cenários chapados, fogo/dinheiro/caixa como props SVG. Fotos de notícia: Wikimedia/Pexels ou frame gerado (LTX) — sem clipes de jornal com direitos.

## Template no editor
- `scene: "cenario"` params `{fundo: "cidade|parlamento|mapa|rua", cor}`.
- `scene: "personagem-pais"` params `{pais, emocao: "raiva|medo|feliz|dúvida", pose, x, y, acessorio}` — olhos/boca SVG trocados por param; respiração idle (scale 1-1.03) e pop na troca de emoção.
- `scene: "multidao"` params `{n, cor, area}` — clones com stagger.
- `scene: "mapa-cartoon"` params `{pais, cidades:[{nome, x, y}], setas}` — rótulo manuscrito draw-on.
- `image` foto real ao fundo + personagem na frente.

## Dificuldade: sob-medida no 1º vídeo (média-alta), preencher-dados depois (média)
Uma vez pronta a biblioteca (20 países-personagem × 6 emoções, 10 cenários, 15 props), o Ollama só escolhe `{cenario, personagens, emoção, prop}` por frase. Humor visual é o que o Ollama pior faz — manter um banco de "gags" fixas (fogo = crise, caixa DEUDAS = dívida, multidão vermelha = protesto).
