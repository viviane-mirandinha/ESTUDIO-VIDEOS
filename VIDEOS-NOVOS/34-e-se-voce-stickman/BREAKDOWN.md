# 34 — E SE VOCÊ (stickman) — "E se você fosse 10 vezes mais rápido?"

Referência: IFOLOGY — "What IF You Could Stop Time?" (https://youtu.be/YznR5NmI3bc), analisados 90 s (00:30–02:00).

## O que foi copiado do estilo (só o estilo)
- Pergunta "E se você...?" + narração em 2ª pessoa; abre com cena-gancho (cold open) antes do título.
- Título em serifa dourada com sombra por cima da cena (DM Serif Display).
- Alterna **cena cartoon** (personagem de moletom em cenário pastel: cozinha, rua com casas) com **diagrama azul-marinho** (ícones de linha branca, destaque dourado, número grande em caixa alta, barrinha de progresso embaixo).
- A ideia segue até o fim: primeiro o "poder", depois os problemas (ar, batida, cérebro/som), fecho irônico.
- Sem legenda palavra a palavra (a referência não usa); só rótulos-chave.

## O que é diferente / próprio
- Personagem **"Tuco"**: cabeça de pele clara, gorro vermelho com pompom, moletom verde-água (o deles tem cabeça preta e moletom cinza). Amigo: moletom roxo.
- Cenas 2D flat em SVG (a referência é 3D render). Sem nome, logo ou personagem do canal.

## Física (contas simples, verificáveis)
- Queda de 80 cm: t = √(2h/g) = √(1,6/9,8) ≈ 0,40 s → ×10 = 4 s percebidos.
- Caminhada ~5 km/h ×10 = 50 km/h; corrida leve 10 km/h ×10 = 100 km/h.
- Arrasto do ar ∝ v² → 10× velocidade = 100× força. Energia cinética ½mv² → ×100.
- Voz ~120 Hz percebida 10× mais lenta = 12 Hz; abaixo de ~20 Hz o ouvido quase não percebe tom (limite usual da audição humana 20 Hz–20 kHz).

## Cenas (template local, edit.json `by: template`)
cozinha(cai/pega) · titulo · troca(5→50 km/h) · rua andar · rua correr · curva F∝v² · troca(10×→100×) · formula ½mv² · rua poste · tempo 3 s→30 s · som 120→12 Hz · rua conversa · rua fim.
Tudo animado por um único "driver" GSAP (setter de função → seek-safe, sem callbacks).

## Áudio
Voz edge-tts pt-BR-AntonioNeural (+12%), tempos faster-whisper large-v3 local. Música: pad gerado por ffmpeg (aevalsrc, senos). 3× whoosh.wav do ESTUDIO-VIDEOS. Sem impact/pop.
