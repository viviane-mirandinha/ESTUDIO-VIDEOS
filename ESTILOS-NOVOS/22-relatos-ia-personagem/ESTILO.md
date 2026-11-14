# 22 — Relatos/histórias com imagens IA e personagem fixo (Bonafillo Relatos · Silas Mercer)

**Dados:** Bonafillo Relatos (ES, "They called him crazy for planting tomatoes…") mediana 28k views, 64 views/h (melhor 1.100), **35 min** por vídeo; Silas Mercer (EN, "25 things mountain men teach seniors") mediana 5k, 67 v/h, 27 min. Ambos pequenos; o formato é "história longa narrada" = watch-time.

## Visual
- **Bonafillo:** ilustrações IA em **estilo pintura/quadrinho realista** (homem de chapéu, vila rural mexicana, campos, carroça) — mesmo personagem em todas as cenas (rosto, chapéu, camisa), paleta terrosa quente (ocre, sépia, verde-oliva), luz de fim de tarde; Ken Burns lento; 1 imagem a cada 6-10 s; sem texto na tela; narração contínua; música folk baixa.
- **Silas Mercer:** "homem da montanha" (barba branca, chapéu) como avatar IA em cabine de madeira falando pra câmera, intercalado com imagens IA de objetos/cenas (lanterna, porta, neve, cartaz "No Trespassing"); tom de conselho; cortes 4-6 s.

## Consistência
Personagem = **imagem-mestra** + geração i2i/LoRA (igual 17/20); cenário = 3-4 ambientes fixos. Para o Bonafillo não precisa vídeo gerado — só imagens (Flux local, zero custo). Para o Silas, clipes do avatar (LTX i2v) opcionais; funciona só com imagens + voz grave.

## Template no editor
- `image` tela cheia `motion` alternado (igual historia-simples), crossfade 0,8 s, filtro quente.
- `scene: "capitulo"` opcional (serifa clara) a cada 5 min.
- `html` vinheta + grão leve.
- Voz: TTS local com voz madura (Chatterbox/Qwen3), música folk `volume 0.08 duck`.

## Dificuldade: preencher-dados (fácil)
É o `historia-simples` com imagens geradas em vez de Wikimedia: pipeline da fábrica + prompt-base de personagem. Roteiro longo (35 min ≈ 5.000 palavras) é o custo — Ollama em capítulos com a regra anti-loop. ES e EN comprovados; PT = gap (nicho "histórias de vida/relatos" já existe no TikTok PT do usuário).
