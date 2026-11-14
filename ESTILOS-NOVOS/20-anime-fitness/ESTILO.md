# 20 — Anime/mangá fitness sobre preto (ryoga.training)

**Dados:** ryoga.training (EN) mediana **222k views**, 560 views/h (melhor 9.100), vídeos de 5 min, 9 vídeos — canal novíssimo com mediana alta = fórmula fresca. Nota do usuário: academia/exercícios.

## Visual
- **Fundo preto total.** Personagem único em **traço de mangá/anime** (homem musculoso de cabelo branco, calça roxa; linhas finas, sombreado leve, quase sem cor além do roxo) — gerado por IA com personagem consistente.
- Poses de exercício (rosca, puxada, costas) + **músculo alvo pintado** (verde/laranja/roxo) sobre a anatomia; setas e rótulos finos ("Long / Medial / Lateral").
- **Texto mínimo** em sans fina branca pequena centralizada ("drop the weight", "3 x 12 reps", "(2/3)") — no nosso canvas subir pra ≥ 32px.
- Ícones simples (halter, círculo de progresso). Ritmo: 1 imagem a cada 3-5 s, corte seco ou fade curto; música lo-fi/phonk baixa; sem SFX.

## Consistência do personagem
Mesma solução do 17: **imagem-mestra** do personagem (Flux + prompt fixo "manga lineart, white hair, purple pants, black background") + geração i2i por pose; ou LoRA de personagem na 4090. Músculo destacado = **overlay SVG** nosso (máscara colorida), não da IA.

## Template no editor
- `image` ilustração sobre preto, `motion: zoom_in 0.04`.
- `scene: "musculo-destaque"` params `{img, mascara, cor, rotulos:[]}` — overlay colorido pulsando + rótulos com linha.
- `text` instruções 36px fina branca; `scene: "contador-reps"` params `{series, reps}`.
- `scene: "progresso-circular"` params `{atual, total}`.

## Dificuldade: preencher-dados (fácil-média)
Roteiro Ollama em formato fixo (erro comum → correção → séries/reps); 1 imagem por passo (banco de 30-40 poses cobre quase tudo, reuso alto). Gap de idioma total (PT/ES não existe). Melhor "mediana ÷ idade do canal" do lote 2.
