# 39 — ARQUIVO NA MESA (dossiê de investigação)

**Gênero:** documentário de caso/mistério contado como um dossiê aberto sobre uma mesa de madeira escura, à luz de luminária.
**Referências (só canais públicos):** Red File (udbDpAkUh10) e Dead Signal Investigation (zAoOy28kpqo). Ver REFERENCIA.txt.

## O que define o estilo
- Mundo = uma mesa de madeira 3200x2000 vista de cima; a **câmera passeia** de prova em prova (pan + zoom com easing, leve inclinação e tremor de mão), e no fim **abre** mostrando a mesa inteira com os fios.
- Objetos: pasta parda com aba e etiqueta, **fichas datilografadas** (Courier Prime, efeito máquina de escrever), **fotos reais** com borda de papel, fita adesiva e legenda à mão (Caveat), **recorte de jornal** com borda rasgada e sépia, moldura vazia, linha do tempo com traço vermelho.
- **Carimbos** vermelhos (Oswald, textura gasta por filtro SVG) batendo na hora da fala: CONFIDENCIAL, INOCENTE, VERDADEIRO, PRESO.
- **Fios vermelhos** com alfinetes ligando provas (desenham-se em 0,9 s), **lupa** passando sobre a foto com aumento real do conteúdo, **círculo de caneta** marcando detalhe, notas à mão em vermelho/azul.
- Luz: poça de luz quente no centro + vinheta muito escura + grão de filme; paleta marrom/sépia com destaque vermelho #b3121b.
- Texto: legenda **pequena** (Inter 30 px) centralizada embaixo, frase inteira (como na ref), rótulo de arquivo no canto (Courier).
- Ritmo: 1 "plano" por frase (~4-6 s), sem corte seco — tudo é movimento de câmera contínuo; whoosh baixo nas viradas; drone grave por ffmpeg com ducking.
- Final: cartão escurecido com título (Cormorant Garamond) + carimbo CASO ENCERRADO.

## Igual / diferente da referência
- Igual: mesa escura com pastas/fotos/lupa/fichas, luz de luminária, legenda pequena centralizada, tom sério, provas reais ("actual image").
- Diferente: tudo é 2.5D por código (sem footage, sem IA de imagem), câmera única contínua em vez de cortes, carimbos e fios animados, sem apresentador e sem entrevista; nenhum logo/nome copiado.

## Como fazer outro vídeo
Editar `make_edit.py` (objetos `obj(...)`, fios `fio(...)`, `CAM`, `SUB`) → `python make_edit.py` → `build_from_edit.py <pasta> --render`.
Fotos: Wikimedia Commons em `img/` (créditos `img/creditos.json`). Texturas: `python gen_texturas.py`. Template: `template_src.html` (genérico: lê tudo do edit.json).
