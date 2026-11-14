# 17 — Avatar realista por IA, consistente (Nina Cooks · Glen Pritchard Builds · Healoloogy · Antiques Gallery · "Jim McAllister" sitcom)

**Dados:** Healoloogy (EN) mediana 44k views, 220 views/h (melhor 2.080); Nina Cooks mediana 21k, 95 v/h (melhor 1.900); Antiques Gallery mediana 48k, 98 v/h (melhor 3.600); Glen Pritchard mediana 7k (melhor 1.600); UCUmCVRNy7w (sitcom IA "Georgie") mediana 40k. Todos canais pequenos e novos = fórmula em teste; o sinal é o pico (1.600-3.600 v/h) em canais de 1-3 meses.

## Visual (todos gerados por IA de vídeo, avatar fixo)
- **Nina Cooks:** mulher indiana madura de cabelo grisalho, cozinha clara, fala pra câmera + planos de panela/arroz; cards "TIP 8 — USE HOT WATER" em bege com ícone; nome do canal como selo.
- **Glen Pritchard Builds:** homem ~60 anos em oficina/galpão, mostra baterias e produtos reais (close de mão com produto), quadro branco com gráfico, b-roll de fábrica. "Vai do vlog ao evergreen" (nota do usuário): a parte evergreen é o **conteúdo de "como funciona"**, não a persona.
- **Healoloogy:** homem idoso tipo "Antiques Roadshow" avaliando artefatos Navajo sobre veludo azul + fotos históricas P&B intercaladas.
- **Antiques Gallery:** réplica de Antiques Roadshow (plateia, joia em close, legenda palavra a palavra amarela, "$7,000 to $10,000" em verde).
- **"Georgie" sitcom:** cenas de sitcom geradas (família americana, cozinha, sofá) dentro de **moldura dourada ornamentada** — recap/fanfic de série.
- **Comum:** câmera fixa/plano médio, luz natural, **cortes a cada 4-8 s** entre "fala" e "detalhe", legenda só em alguns; música baixa; sem SFX.

## Consistência (o ponto do usuário)
Pipeline já existente na casa: **ai-avatar-video-system** (prompts de cena com face/ambiente/voz travados) + Dark Planner (Flow/Omni/HeyGen) ou LTX-2.5 local i2v a partir de **1 imagem-mestra do avatar** (Higgsfield Soul, skill avatar-realista). Regra: todo clipe parte da mesma imagem-mestra + mesmo cenário; closes de produto/objeto são **clipes sem o avatar** (stock ou i2v de foto do objeto) — é assim que esses canais escondem a inconsistência. Voz: TTS local fixa (Qwen3-TTS/Chatterbox) = mesma voz sempre.

## Template no editor
- `video` clipes do avatar (6-8 s cada, gerados) alternando com `video`/`image` de detalhe (produto, prato, artefato, foto histórica com Ken Burns).
- `scene: "card-dica"` params `{numero, texto, icone, cor}` (Nina).
- `scene: "moldura-ornamentada"` (sitcom) e `scene: "valor-avaliacao"` params `{de, ate}` verde (Antiques).
- `caption` amarela palavra a palavra (Antiques).
- `text` selo do canal canto superior.

## Dificuldade: preencher-dados (média) — gargalo é geração de vídeo, não edição
Roteiro Ollama em blocos "fala → detalhe"; cada bloco vira 1 prompt i2v da imagem-mestra + 1 clipe de detalhe. Custo = minutos de GPU/créditos de vídeo (ver memórias: conta Google sem crédito Lite/Omni; LTX local = zero). Edição em si é a mais simples do catálogo. Risco: política "AI slop" do YouTube — manter conteúdo útil (receita real, avaliação real) e avatar bem feito.
