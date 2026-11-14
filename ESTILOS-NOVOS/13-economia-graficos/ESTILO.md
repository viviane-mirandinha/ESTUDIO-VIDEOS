# 13 — Economia explicada com gráficos animados (Economics Explained · How Money Works · Los Ecomonos · Noticias Ilustradas)

**Dados:** Economics Explained (EN) mediana 701k views, 1.930 views/h (melhor 19.600); How Money Works mediana 782k, 2.360 v/h (melhor 7.900); Los Ecomonos (ES) mediana 224k, 730 v/h (melhor 5.700); Noticias Ilustradas (ES, cartoon — ver 07) 1.700 v/h. Em PT a busca não achou canal faceless médio = gap.

## Visual
- **Economics Explained:** b-roll stock (cidade, fábrica, bolsa) alternado com **gráficos animados minimalistas** (linha subindo, barras, pizza) em fundo escuro ou sobre o b-roll escurecido; **texto-chave em sans bold branca** (56-72px) com 1 palavra em amarelo; ícones flat; narrador australiano calmo; cortes a cada 4-7 s.
- **How Money Works:** mais cartunesco: boneco flat (parecido com Infographics) + gráficos coloridos + prints de manchete com destaque amarelo (marca-texto) — títulos ironizando ("tHe pOpULaTiOn iS CoLlapSiNg!"). Fundo azul-escuro (#0f1b2d).
- **Los Ecomonos (ES):** gráficos + bonecos flat + fotos, tipografia grande, fundo bege/azul.
- **Paleta comum:** azul-escuro/preto, branco, amarelo (#ffd400) de destaque, verde/vermelho para subir/cair.
- **Ritmo:** gráfico aparece **desenhando** (linha draw-on 1,5-2 s) sincronizado com o número falado; manchete entra com zoom + marca-texto; sem legenda; música lo-fi baixa.

## Mídia
Gráficos gerados (D3/GSAP/SVG) a partir de dados reais (FRED, Banco Mundial, IBGE — CSV livres), b-roll Pexels (cidade, dinheiro, fábrica), manchetes **geradas em HTML** (layout genérico de jornal, sem logo real), ícones Lucide. Dados reais = diferencial anti-"AI slop".

## Template no editor
- `scene: "grafico-linha"` params `{serie:[{x,y}], titulo, unidade, cor, destaque_x}` — draw-on + ponto pulsando no destaque.
- `scene: "grafico-barras"` params `{itens:[{rotulo, valor, cor}]}` — barras sobem com stagger (já existe `ee_barras.html` nos scenes do editor — reaproveitar).
- `scene: "manchete"` params `{veiculo_generico, titulo, data, destaque}` — card de jornal + marca-texto amarelo animado.
- `scene: "numero-contador"` (existe `contador.html`).
- `text` palavra-chave 64px com `highlight` amarelo. `video` b-roll escurecido (`opacity 0.75`).

## Dificuldade: preencher-dados (média)
Metade das cenas já existe no editor (barras, contador, capítulo). Falta linha/manchete. O trabalho por vídeo é **achar a série de dados** — o Ollama não deve inventar números: pipeline busca CSV local (banco de séries pré-baixadas: PIB, inflação, juros, câmbio por país) e o roteiro cita só o que está no CSV. Gap PT claro (nenhum faceless médio achado).
