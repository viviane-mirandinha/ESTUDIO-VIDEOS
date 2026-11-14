# 28 — Infográfico escuro com dourado: "todo X que já foi o maior do mundo" (KNOT & RAIL)

**Dados:** KNOT & RAIL (EN) — "Every Ship That Was the Biggest in the World, Explained": **153k views**, 770 views/h, 12 min, num canal de mediana 573 views (15 vídeos). Fórmula "every X that was the biggest/first/fastest, explained" = lista cronológica comparativa. Outlier claro: a fórmula, não o canal.

## Visual (sheet-knot-rail-*.jpg)
- **Fundo azul-marinho/preto texturizado** (#0d1623) com leve vinheta; tudo em **dourado (#d9a63a) e branco**.
- **Silhueta do item** (navio) em dourado chapado, escala proporcional; **barra de comparação** (anterior × novo) em dourado; medidas gigantes ("414 M", "211 M", "12 DAYS", "553,662 TONS") em sans condensada bold dourada 90-120px.
- **Título do item** ("GREAT EASTERN", "1976 BATILLUS") em caixa alta dourada + ano; sub-título branco ("NOT JUST A BIGGER SHIP — THE WORLD CHANGED AROUND IT").
- **Foto/pintura histórica** em sépia escurecida numa moldura com borda fina; **mapa-múndi** dourado sobre escuro com rota tracejada; **gráfico de barras** dourado/azul; "EVERY BARREL CHEAPER" como card de tese.
- Ritmo: 1 item a cada 60-90 s; dentro dele 6-10 cenas de 4-8 s; transição = fade curto; música orquestral baixa; sem legenda; nada de SFX.

## Template no editor
- `scene: "item-silhueta"` params `{nome, ano, medida, unidade, svg: "navio|aviao|predio|ponte", escala_anterior}` — silhueta dourada cresce da anterior (compare) + número com contagem.
- `scene: "barra-comparacao"` params `{a:{rotulo, valor}, b:{rotulo, valor}}`.
- `scene: "mapa-rota-dourado"` params `{de, para, pontos}` (base 01-mapas, tema escuro/dourado).
- `scene: "card-tese"` params `{titulo, sub}` — dourado + branco.
- `image` foto sépia em moldura `motion: zoom_in 0.06`.
- Canvas `bg: "#0d1623"`.

## Dificuldade: preencher-dados (fácil-média)
Combina 09-tamanho (comparação de escala) em 2D com 05-timeline. Lista cronológica `{nome, ano, medida, foto}` do Ollama + Wikimedia (navios/aviões/prédios históricos têm foto livre). Silhuetas: SVG de domínio público (Wikimedia) ou traçadas da foto (potrace local). Fórmula transferível pra qualquer "maior/primeiro/mais rápido" e pra PT/ES (gap total).
