# 01 — Whiteboard / quadro desenhado (Academia Play · Bully Magnets · After Skool)

**Referência principal:** Academia Play (ES, 3,7M inscritos, mediana 222k views, ~540 views/h nos 45 d; melhor 2.833 v/h). After Skool (EN, 1,1k v/h) é a versão "arte densa" — bonita, mas NÃO replicável (ilustrador real filmado). Bully Magnets (ES) = mesma fórmula do Academia Play com traço mais solto.

## Visual (sheet-academiaplay-*.jpg)
- **Fundo:** branco puro (#ffffff) o vídeo inteiro; às vezes mancha azul-clara (#bfe3ea) de "mar" quando entra mapa.
- **Paleta:** preto do traço + 3-4 cores chapadas (azul-marinho #1d2a5c das etiquetas de data, vermelho #c8102e, amarelo #f2c200, verde #2e8b57). Mapas com país destacado em vermelho/verde pastel.
- **Fontes:** título em display bold com contorno/sombra ("GRAN BRETAÑA" cinza-azulado com outline), etiquetas em sans manuscrita fina (estilo Patrick Hand / Kalam). Datas em pílula azul-marinho com texto branco. Texto de apoio ≥ 28px no nosso canvas.
- **Personagem:** 1 boneco cartoon fixo (menino de camisa laranja) que reage (braços cruzados, dúvida, "X" vermelho de negação). Balões de fala curtos.
- **Mão:** mão real (PNG recortado) segurando caneta aparece **só enquanto o elemento é desenhado** (1-2 s) e some.
- **Elementos:** bandeiras, brasões, mapa com contorno, setas vermelhas curvas, "+" entre dois itens = fusão, rabisco vermelho de "confusão", ícone de like, "¿?" amarelos.

## Ritmo
- Cada frase nova = 1 elemento novo desenhado (a cada 2-4 s). A cena acumula elementos até lotar (8-12 itens), aí **limpa (wipe branco) e começa quadro novo** a cada ~25-40 s.
- Sem corte de câmera; a "câmera" dá zoom suave (1.0 → 1.15) no elemento falado e volta ao geral.
- Sem legenda queimada. Sem SFX de impacto (risco de caneta opcional, baixo).

## Mídia
Vetor/SVG (ícones, bandeiras, mapas GeoJSON), PNG recortado (boneco com 5-6 poses, mão com caneta), zero foto. Tudo local: ícones Lucide/OpenMoji, bandeiras SVG da Wikimedia, mapa dos countries50m.geojson.

## Template no editor (edit.json)
- `scene: "quadro"` (cena nova) com params `{itens:[{tipo:"texto|icone|bandeira|mapa|boneco|seta", valor, x, y, t}]}` — cada item entra com **stroke-dashoffset (draw-on) + mão PNG seguindo o path** por 1,2 s; textos aparecem letra a letra (`in: "type"`).
- `text` para título do quadro (display bold 56px, outline) e pílulas de data (`bg` azul-marinho, `radius` 20).
- `image` para boneco (poses trocadas por `src`) e bandeiras/brasões.
- Limpeza de quadro = item `html` com wipe branco de 0,4 s.
- Canvas: `bg: "#ffffff"`.

## Dificuldade: preencher-dados (média)
Lista de itens por frase vem do Ollama ("que ícone/bandeira/mapa ilustra esta frase?") + 1 cena genérica `quadro`. A parte sob-medida é só a biblioteca inicial (boneco 6 poses, mão, ~60 ícones). Depois disso é 100 % fábrica. Risco: ícone errado pra frase (regra "imagem tem que fazer sentido").
