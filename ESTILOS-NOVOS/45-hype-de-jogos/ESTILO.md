# 45 — Hype de jogos: "Tudo que sabemos sobre…" (Hazard / TGG)

**Dados:** Hazard — "GTA 6: EVERYTHING We Know So Far... (The ULTIMATE Breakdown)" ~325 mil views; TGG — "GTA 6 Launch Trailer: Everything New YOU MISSED" ~1,6 mi views. Gênero notícia/hype de game: lista de fatos rápidos, "tudo que sabemos", "detalhes que você perdeu", data de lançamento, rumor x confirmado.

## Visual medido (ref/ESTILO-MEDIDO.md + sheet)
- **Fundo azul-royal em gradiente** (`#025de4` ~ destaque medido) quando não há footage; paleta escura `#181619` nos trechos de trailer.
- **Cards arredondados com borda branca** que pulam na tela (prints de tweet, mapa, thumbnail) — sombra forte.
- **Pílula rosa** de destaque ("35 NEW DETAILS!").
- **Palavra gigante amarela, itálica, contorno preto grosso**, 1 palavra por vez, no centro-baixo (estilo legenda de hype).
- Ritmo medido no trecho: ~6,5 cortes/min, mediana 3,6 s por plano; voz + música baixa, -21,7 LUFS.

## Nosso template (template.html / make_edit.py, SVG + GSAP, 100% código)
- Cenas `scene`: intro (título glitch RGB + pílula), contagem (3-2-1 com anel), osc (card de data + aparelho desenhado), odyssey (2 objetos + palavra "EXPLODE"), crash (fundo vermelho, cartuchos caindo, gráfico despencando, barra RUMOR), nes (carimbo ERRADO → barra CONFIRMADO), bolso (portátil), disco (2 cards de data + cubo low-poly girando), online (3 cards de ícone), bilhoes (partículas + palavra gigante), proxima (card "DATA DE LANÇAMENTO ??/??/????" + CTA comentário).
- Componentes reutilizáveis: `gt()+glitchIn()` (texto com separação ciano/magenta), `dateCard()`, `pill()`, `bar()` (RUMOR x CONFIRMADO com barra que enche), `frame()` (card de borda branca), HUD de "carregando" com anos no topo, legenda amarela palavra a palavra.
- Objetos de console/arcade/portátil são genéricos (sem marca, logo ou personagem). Nada de footage de jogo.
- Para outro tema: trocar textos/anos/tempos em make_edit.py (todo texto vem do edit.json) e reaproveitar cenas.

## Dificuldade: média-baixa
Sem imagem externa. Notícia de jogo real exigiria footage (risco de Content ID) — este estilo resolve com cards/HUD/tipografia; para um canal de notícia de game real, usar só texto + cards de data/rumor.
