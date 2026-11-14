# 30 — Experimento real filmado: colônias de formigas (Wild Experiments)

**Dados:** Wild Experiments (EN) 7 vídeos, mediana **1M views**, **8.462 views/h** (melhor 15.920); vídeo enviado "2 Ant Colonies Race Through Obstacles & Meet After 30 Days" **4,4M views** em 12 dias (16 min). Maior views/hora de tudo que o usuário mandou.

## Visual (sheet-wild-experiments-*.jpg)
- **Terrário real** (aquário com areia, musgo, plantas, obstáculos coloridos, fogo) filmado de cima e de lado, macro das formigas (vermelhas × pretas), mão com luva azul colocando itens; **"DAY 1"** em sans bold branca grande; **setas vermelhas** apontando; tubo de ensaio com rainha; plantas carnívoras.
- **Cutaways em cartoon 2D** (formigas desenhadas, vulcão, mapa do terrário ilustrado) explicando o que está acontecendo — traço simples, cores chapadas.
- Ritmo: cortes 2-5 s, timelapse, narração empolgada, música leve.

## Replicável?
**Não por HTML/IA**: o valor é o experimento real (público percebe IA/stock na hora). Opções:
1. **Filmar de verdade** — terrário de formigas custa pouco (formicário + colônia ~R$150-300), 1 câmera + tripé, timelapse por dias; edição depois é a parte fácil (cards "DIA N", setas, cutaways cartoon pela fábrica). É um canal "físico" do portfólio, não um estilo da fábrica.
2. Variante só com o que a fábrica faz: **cartoon 2D do experimento** (as cenas de cutaway como vídeo inteiro) — estilo 07/16 com formigas-personagem; perde a prova real, mantém a premissa "o que acontece quando X encontra Y".

## Template no editor (só a edição por cima do footage real)
- `scene: "dia-n"` params `{n}` — texto 96px bold com fade.
- `scene: "seta-circulo"` (do 03) vermelha.
- `scene: "cutaway-cartoon"` params `{cena: "vulcao|encontro|tunel", personagens}` — SVG simples.
- `video` footage real com `speed` (timelapse) e `motion: zoom_in`.

## Dificuldade: edição fácil; conteúdo exige produção física
Registrado como oportunidade (8,5k v/h, 7 vídeos, 1M de mediana), não como molde da fábrica.
