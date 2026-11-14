# 42 — Futebol em TV retrô (CRT/VHS): história do futebol antigo "passando numa fita"

**Dados:** Classic Football ("Football's Greatest International Teams .. Brazil 1970", ~1,87 mi views, 26 min) e Beyond Football ("The Greatest Eras In Football History Explained in 58 Minutes", ~36 mil views). Busca "retro football history vhs" também mostra VHSsports (80-89 mil views em fitas NFL dos anos 80) — o público consome nostalgia de fita/TV antiga. Medição (ref.mp4, 4 min): ~21 cortes/min, plano médio 2,8 s, só narração, texto em ~5% dos quadros, paleta amarelada de arquivo.

## Visual
- Tudo dentro de uma **TV de tubo**: cantos arredondados, vinheta escura, reflexo de vidro, linhas de varredura, barra clara rolando, **aberração cromática** (R/B deslocados), grão permanente.
- **OSD de fita VHS** (VT323): PLAY ► piscando, CH 03, contador SP 0:00:SS, data de câmera (JUN. 21 1970).
- **Chiado entre cenas** (0,28 s de ruído + faixa de tracking + tela tremendo + som de chiado). Liga a TV no início (linha que abre) e desliga no fim.
- Elementos de TV dos anos 70-90: barras de cor, **teletexto** (P100, faixas coloridas, resultados), **placar eletrônico de lâmpadas** que muda na palavra do gol, tarja de nome estilo anos 70 (amarelo/laranja/marrom + Righteous), chips amarelos com sombra sólida, sol/sunburst 70s, prancheta de giz.
- Fotos só domínio público (retratos, figurinhas, foto posada) em moldura creme com sombra laranja/marrom; nunca lance de partida ou imagem de transmissão.

## Nosso template (VIDEOS-NOVOS/42-futebol-tv-retro: template_src.html + make_edit.py)
- Cenas `scene`: titulo, cores (P&B → cor), foto (tarja + chips + bolinhas), teletexto, prancheta, estadio, placar (eventos com placar/autor/tempo), jogada (passes desenhados a giz + chute), tri (estrelas + taça genérica), fim (pergunta + CTA).
- Itens `osd` (textos do OSD e grão) e `chiado` (lista de tempos do ruído) editáveis no editor.
- Outro tema (Copa 58, 82, 94, um craque, um clube): trocar textos/tempos em make_edit.py; teletexto e placar servem para qualquer campanha.

## Dificuldade: baixa-média
Camada TV é reaproveitável inteira; por vídeo só muda texto, fotos PD e 1-2 cenas desenhadas (prancheta/jogada). Para vídeo longo (10-20 min) repetir a família de cenas com outros dados.
