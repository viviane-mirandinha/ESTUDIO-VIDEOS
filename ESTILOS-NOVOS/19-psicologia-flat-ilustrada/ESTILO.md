# 19 — Psicologia com ilustração flat clara + legenda (People Patterns Psych)

**Dados:** People Patterns Psych (EN) mediana 881 views, 44 views/h (melhor 1.300), 8 min, 15 vídeos — canal novo/pequeno, ainda sem tração; vale como molde de **visual**, não de resultado. Comparar com Psych2Go (gigante) e com nosso 08-psicologia-sombria (pinturas escuras): este é o polo **claro/limpo**.

## Visual
- **Fundo creme/bege claro** (#f3ede4) com vinheta suave; ilustrações **flat de pessoas** (traço fino, cores pastel, estilo "ilustração de blog") em situações (casal no café, homem no celular, porta fechada) — imagens geradas (Flux) no mesmo estilo.
- **Legenda palavra a palavra** no rodapé em sans bold preta, palavra-chave em **vermelho** ("BECAUSE THERE ARE THREE PSYCHOLOGICAL **SHIFTS**"); frases inteiras em itálico bold sobre cartão de papel ("A MAN WHO NEVER BEGS HAS BUILT A LIFE").
- Números grandes em azul-marinho ("3") + ícone; bonequinhos de palito pretos para metáforas (porta, caminho, alvo vermelho).
- **Ritmo:** troca de ilustração a cada 3-5 s; zoom leve; sem SFX; música suave.

## Template no editor
- `image` ilustração flat (Flux/Pollinations com prompt fixo de estilo: "flat vector illustration, pastel, cream background, thin outline") `motion: zoom_in 0.05`, moldura arredondada.
- `caption` 48px preta, `hl_color: "#d8232a"`, `bg` transparente, `y: 640`.
- `scene: "cartao-frase"` params `{texto, destaque}` — papel pautado + frase itálica bold.
- `scene: "numero-icone"` params `{n, rotulo, icone}` + `scene: "palito"` params `{cena: "porta|caminho|alvo|celular"}` (SVG).
- Canvas `bg: "#f3ede4"`.

## Dificuldade: preencher-dados (fácil)
É o 08-psicologia-sombria em versão clara: troca pinturas por ilustrações geradas com prompt de estilo fixo + caption. Risco: consistência das ilustrações (mesma paleta) — resolver com prompt-base + LoRA leve ou pós-filtro de cor. Referência fraca em views; usar o tema (psicologia de relacionamento, 1,3k v/h no pico) e testar amplo.
