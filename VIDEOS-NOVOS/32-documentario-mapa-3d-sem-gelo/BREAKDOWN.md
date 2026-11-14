# 32 - DOCUMENTÁRIO MAPA 3D - Así se ve la Antártida sin hielo

Referência: Unseen Works, "What Antarctica Looks Like Without Ice" (https://youtu.be/TudM_lSW8WA). O canal é novo e o vídeo bateu 1,1M de views em cerca de 7 dias.
Estilo catalogado em `ESTILOS-NOVOS\32-documentario-mapa-3d-sem-gelo\ESTILO.md`.

## O que é
É o mesmo vídeo da referência, com o mesmo gancho, a mesma estrutura e a mesma ordem de fatos, adaptado para o espanhol latino (es-MX) com tom humanizado. A voz foi gravada pelo usuário (11 min 44 s). São 1.280x720 a 30 fps, sem legenda (igual à referência) e sem SFX.

## Pipeline
1. **Roteiro**: transcrição do original com Whisper, adaptação ES feita por Sonnet (PRO) e um mapa de cenas EN→ES com 174 linhas (`ROTEIROS-NOVOS\32 - MAPA CENAS EN-ES.tsv`).
2. **Voz**: mp3 do usuário → `voz.wav`, depois Whisper large-v3 na GPU (`whisper.py`) e alinhamento roteiro↔fala com difflib (`alinhar.py`, 1815 de 1862 palavras casadas).
3. **Dado 3D real**: Bedmap2 (British Antarctic Survey, 1 km, EPSG:3031) → heightmaps 16-bit do leito, da superfície e da máscara de gelo (`_dados\heightmap.py`).
4. **Cenas novas no editor** (`EDITOR VIDEOS\templates\scenes\uw_*.html`):
   - `uw_relevo`: mapa 3D Three.js com relevo hipsométrico e modos gelo / sem-gelo / derrete, pinos, círculos, linhas (rift), setores (reivindicações), contorno EUA+MX e câmera orbitando.
   - `uw_corte`: cortes 2D gelo/rocha nos modos bloco, rebote, radar, lago, perfuração, Whillans, plataforma, fossa (Denman × Mar Morto) e rolha (Thwaites).
   - `uw_escala` (Burj Khalifa × gelo), `uw_grade` (138 vulcões, 91 destacados), `uw_linha` (linha do tempo), `uw_carimbo` (pergunta + carimbo vermelho), `uw_capitulo`, `uw_numero` (número amarelo com contagem), `uw_rotulo` (lower-third com barra amarela), `uw_foto` (Ken Burns), `uw_split`.
5. **Montagem**: `montar_edit.py` tem um mapa explícito em que cada linha do TSV vira um fundo (77 mapas 3D, 58 fotos, 14 cortes, extras) mais um overlay de texto (44 números, 57 rótulos), com tempos vindos da voz real.
6. **Render**: `build_from_edit.py --render` (HyperFrames).

## Mídia
- 53 fotos da Wikimedia Commons (créditos em `img/cand/creditos.json`).
- Não há clipes de vídeo de banco: a Pixabay deu erro 401 e a Wikimedia bloqueou por excesso de pedidos (429).
- Imagens com texto estrangeiro (mapas Gondwana em tcheco/italiano, diagrama Vostok) ficaram de fora.

## Parecido x diferente da referência
- **Parecido**: mapa 3D de relevo real sem gelo, números amarelos grandes, lower-thirds com barra amarela, capítulos, carimbo "NO EXACTAMENTE", Burj Khalifa empilhado, 138 vulcões e setores das reivindicações.
- **Diferente**: sem clipes de vídeo de banco (só foto + 3D), sem modo globo na abertura (começa direto no mapa com gelo) e cortes 2D mais simples que os da referência.
