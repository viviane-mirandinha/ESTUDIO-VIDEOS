# 43 — MAPA VERMELHO (geopolítico de alerta)

Referências públicas (só 3 trechos curtos de cada, em `ref/ref.mp4`):
- Ticket To Know — "The Strait of Hormuz Explained" (4,1 mi views) https://www.youtube.com/watch?v=udtVdDmSSoo
- Himfact — "Why is the Red Sea so Important?" (533 mil views) https://www.youtube.com/watch?v=4vRtXY-iFnc

## O que foi clonado (estrutura)
- Abertura com zoom dramático do mundo até o estreito (mundo → ponto em ~2 s).
- Rótulo do lugar sobre o mapa, faixas de navegação tracejadas, setas de rota até os destinos.
- País pintado em bloco de cor sólida quando é citado (um por vez, sincronizado na palavra).
- Número gigante sozinho na tela ("76%" na ref → aqui 20%, 1/5, 84%).
- Só voz, sem música marcada (ref medida: -24 LUFS, pausas entre frases); planos longos (~8,8 s média), cortes secos.

## O que muda para o gênero "mapa vermelho"
- Mapa vetorial escuro (Natural Earth 50m) em vez de satélite; mar quase preto com grade vermelha fraca.
- Destaque vermelho intenso (#e3121b) com fronteira brilhando (3 traços sobrepostos, sem filtro).
- HUD de alerta: "● ALERTA · ROTA CRÍTICA" piscando, coordenadas, cantoneiras vermelhas, scanlines, vinheta.
- Números em Anton 150 px vermelho com brilho + flash vermelho na entrada.
- Trilha = drone grave gerado no ffmpeg (55 Hz + 82 Hz + ruído marrom com tremolo) + whoosh só nas trocas grandes de câmera.

## Cenas do template (`template_src.html`, params editáveis no editor)
camera (alvo, zoom, transicao) · paises (codigos ISO, tempos, cor, fim) · rotulo (texto, ponto, estilo red/box/mar)
· linha (linha, cor, largura, fluxo, seta) · pulso · numero (valor, legenda, fonte, lado) · titulo · flash · cta · hud.
Para outro país/região: editar pontos e linhas em `gen_map.py` → `python gen_map.py` → `python montar.py`.
