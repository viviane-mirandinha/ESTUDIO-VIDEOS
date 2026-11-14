# 23 — Militar footage (ref. Military Storm, fSec-dzzKZI) — o que copiar (variante licenciada)

1. Ritmo da ref.: corte a cada 1,5-4 s, tela cheia sempre com "footage", narração dramática e música tensa baixinha (ducking), sem legenda.
2. Footage: em vez de combate real (Telegram/TV), stock livre Pixabay (caminhão militar, atirador de ghillie, soldado em trincheira, fumaça em campo, estrada vista de drone, estojos de munição) + 5 imagens Flux local (coluna parada, caminhão com fumaça, poço camuflado, rádio de campanha).
3. Visão térmica verde e drone P&B (como os trechos FPV/térmicos da ref.): filtro ffmpeg (mono + verde + ruído + vinheta) + cena `termico` (scanlines e faixa rolando).
4. HUD de drone em SVG/HTML (`hud-drone`): cantoneiras, mira, escada de horizonte, fitas laterais, REC piscando, relógio da fala; modo `mira` = luneta de sniper com retículo e balanço.
5. Mapa tático top-down (`mapa-tatico`, variante do 06): campos oliva, linha das árvores, estrada de terra, 42 ícones de veículos, explosão do 1º caminhão no KM 3, poço a 40 m à esquerda, flanco riscado, câmera com zoom log.
6. Relógio grande amarelo (06:00 / 06:20 / 06:40 / 06:55) só nos horários falados; relatório final com carimbo "14 CARTUCHOS" (`mil-relatorio`).
7. Textos Oswald 56 px em caixa preta (o que a fala diz), rótulos do mapa 28-44 px; nada de número que não esteja na fala (HUD sem telemetria numérica).
8. Diferente da ref.: sem logo de canal, sem footage real de guerra, sem morto/ferido, sem SFX de tiro/explosão (só 4 whooshes suaves).
