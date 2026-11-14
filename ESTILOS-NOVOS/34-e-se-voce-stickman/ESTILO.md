# Estilo: E SE VOCÊ (stickman de moletom)

**Referência:** IFOLOGY — "What IF You Could Stop Time?" (vídeos longos 16:9, ~10 min).
**Exemplo pronto:** VIDEOS-NOVOS\34-e-se-voce-stickman\ ("E se você fosse 10 vezes mais rápido?", 1:18).

## Receita
1. **Gancho frio (0–12 s):** o poder em ação numa cena do dia a dia (copo caindo → você pega).
2. **Título** em serifa dourada com sombra sobre a cena ("E SE VOCÊ FOSSE…?").
3. **"Funciona assim"** → diagrama azul-marinho com ícones de linha branca + número dourado em caixa alta (5 km/h × 10 = 50 km/h).
4. Volta pro cartoon pra mostrar a consequência (andar do lado do carro, correr a 100 km/h).
5. **Problemas, um por bloco** ("1º PROBLEMA: O AR", "2º PROBLEMA: A BATIDA"...), sempre com conta simples e verificável.
6. Fecho irônico em serifa dourada ("presa num mundo em câmera lenta").

## Regras visuais
- Narração 2ª pessoa ("você"), frases curtas; ~150 palavras/min.
- Cartoon: cenários pastel flat (cozinha, rua com casas, árvores, postes), contorno azul-escuro #1b1f3a.
- Diagrama: fundo radial #24366e → #0a1129, linha #e9eefc 6 px, destaque #f5b82e, barra de progresso dourada embaixo.
- Personagem próprio "Tuco" (gorro vermelho, moletom verde-água). Nunca usar o boneco de cabeça preta da referência.
- Sem legenda palavra a palavra; só rótulos-chave. Corte com crossfade 0,28 s + push-in leve 4,5 %.
- Som: voz + pad baixinho (ffmpeg) + whoosh só na entrada dos diagramas (máx. 3-5).

## Como refazer com outro tema
Copiar `template.html` (cenas: cozinha, titulo, rua[andar|correr|poste|conversa|fim], troca, curva, formula, tempo, som) e escrever um `montar_edit.py` novo com os tempos das palavras (`words.json`). Todo texto e tempo fica no edit.json (editável no Editor).
