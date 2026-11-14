# 25 — Documentário regional com mapas, drone e dados (Alabama Revealed · America Under Construction · When America Made Everything · The Apprentice's Guide)

**Dados:** Alabama Revealed (EN) mediana 35k views, 98 views/h (melhor 1.200), 33 min; America Under Construction mediana 5k, 27 v/h; When America Made Everything mediana 7k (75 min!, 168 v/h no melhor); The Apprentice's Guide (técnico, "Volts, Amps & Watts") mediana 11k, 10 v/h (melhor 1.100). Canais pequenos de nicho local/americano; vídeos longos = watch-time; replicáveis 100 %.

## Visual
- **Alabama Revealed:** mapa claro do estado com condados em cores + pontos vermelhos; **cards de dado** em preto ("5 COUNTIES: NEARLY 80 % GROWTH" + barra vertical animada, "12 %"); recortes de notícia/tabela com destaque; drone de rodovia, fazenda, cidade (stock); satélite com polígono amarelo; cortes 5-8 s.
- **America Under Construction:** porto/navio (stock + fotos), **card "Chapter — Deep Harbor, New Terminal"** em azul-marinho, gráficos de barra cinza/preto ("Post 45: Charleston Harbor Depth"), número grande ("$2.000.000.000"), desenho técnico de navio, mapa dos EUA com pontos.
- **When America Made Everything:** fotos de arquivo P&B de fábricas, anúncio antigo "MAYTAG", mapa satélite com rótulo "AKRON, OHIO · 1951", barra "Maytag workforce vs Newton population", desenho de planta de fábrica; "#1" dourado como numeração de lista.
- **Apprentice's Guide:** slides escuros (#0e1116) com texto laranja/branco, fórmulas "P = V × I", diagrama isométrico de casa com fiação, linhas animadas — estilo 13-3D técnico sem o 3D.
- **Paleta:** azul-marinho, branco, dourado/laranja de destaque; fontes sans (Inter) + números grandes.

## Template no editor
- `scene: "mapa-regiao"` params `{geojson_nivel: "estado|condado|pais", destaque:[], pontos:[]}` — base 01-mapas em tema claro.
- `scene: "card-dado"` params `{titulo, valor, tipo: "barra|numero"}` — existe `ee_barras.html`/`contador.html`, adaptar.
- `scene: "capitulo"` (existe) em azul-marinho; `scene: "rotulo-satelite"` params `{lugar, ano}`.
- `image` foto de arquivo (Ken Burns) e `video` drone stock; `scene: "slide-tecnico"` params `{titulo, linhas:[], formula}` para o Apprentice.

## Dificuldade: preencher-dados (fácil-média)
Combina cenas que já existem (mapas, barras, contador, capítulo, fotos). Dados do Census/BLS/IBGE em CSV local (sem inventar número). Versão PT óbvia: "cidades/estados do Brasil que estão mudando" com IBGE — gap sem concorrente faceless visto na mineração.
