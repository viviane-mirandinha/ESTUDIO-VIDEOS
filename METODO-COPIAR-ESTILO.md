# Método: copiar o estilo de edição de um vídeo de referência

Objetivo: vídeo novo que COPIA o jeito de editar de um canal (ritmo, tipo de visual, fontes, cores, gráficos, legendas,
transições) — com roteiro, voz e imagens próprios. Nunca copia logo, nome, intro, personagem registrado ou trechos do vídeo.

Todos os caminhos abaixo são relativos à pasta `ESTUDIO-VIDEOS`.

## Entradas
- Link do vídeo de referência (YouTube/TikTok/Instagram).
- Tema ou roteiro (se não vier roteiro: escrever um — ver regras de roteiro no `CLAUDE.md`).
- Voz: arquivo do usuário, ou gerar com TTS (`edge-tts`, voz `pt-BR-AntonioNeural`/`pt-BR-FranciscaNeural`).

## Saída
- Pasta `VIDEOS/NN-<estilo>/` (NN = próximo número livre em `VIDEOS`).
- `edit.json` no formato de `editor/FORMATO.md` (é o que faz o vídeo aparecer no editor).
- `NN - DD-MM-AAAA - CANAL - TITULO.mp4` + `sheet.jpg` (contact-sheet de ~12 quadros) + `BREAKDOWN.md` + `RELATORIO.json`.
- Padrão: 1280x720 30fps (longo, 16:9). Shorts/Reels: 1080x1920.

## Fluxo
1. **Referência (3 trechos: começo, meio e fim — nunca o vídeo inteiro)** — numa subpasta temporária `ref/` (não vai para lugar nenhum):
   `yt-dlp -f "worst[height>=360]/worst" --download-sections "*0-40" --download-sections "*<meio-45>-<meio+45>" --download-sections "*<fim-40>-inf" -o "ref/ref_%(section_start)s.mp4" <link>`
   (começo = gancho e abertura; meio = ritmo de cortes; fim = encerramento e chamada. Junte os 3 com ffmpeg concat em `ref/ref.mp4`.)
   O vídeo NOVO é sempre completo, na duração pedida (1, 10 ou 30 min) — os trechos servem só para aprender o estilo.
   Rate-limit: espere 60 s, no máximo 3 tentativas.
   Contact-sheet único: `ffmpeg -i ref/ref.mp4 -vf "fps=1/3,scale=320:-1,tile=6x5" -frames:v 1 ref/sheet.jpg`
   Olhe só o contact-sheet (uma imagem) e escreva 6-10 linhas em `BREAKDOWN.md`: ritmo de cortes, tipo de visual,
   fontes, cores, gráficos, legendas, transições, SFX/música.
1b. **Medir o estilo (zero token)**: rode `python editor/ferramentas/medir_estilo.py ref/ref.mp4`. Ele grava em `ref/`
   a ficha `ESTILO-MEDIDO.md` (+ `ESTILO-MEDIDO.json` e `sheet-medido.jpg`) com números medidos: cortes/min e duração
   média do plano, proporção/resolução, paleta de 5 cores hex + cor de destaque, brilho/contraste, % de quadros com
   texto grande (centro/inferior), loudness (LUFS), música contínua vs só voz e BPM aproximado. Use a ficha como fonte
   da verdade do `BREAKDOWN.md` e siga a seção final "Como recriar no Estúdio" ao montar o `edit.json` (ritmo de
   cortes alvo, fonte Google Fonts, cores, posição/tamanho da legenda, tipo de transição). Use `sheet-medido.jpg` como
   o contact-sheet do passo 1 (não precisa gerar outro). Os números são aproximados: confira o texto e a música no sheet.
2. **Voz + tempos**: gere/copie a voz (`voz.mp3`) e rode o whisper para ter `words.json`:
   `.venv` → `python editor/fabrica/lib/whisper_run.py voz.mp3 words.json small` (ou `large-v3` com GPU).
3. **Visuais (só grátis/livres)**: HyperFrames HTML+GSAP (SVG, mapas, tipografia, gráficos), Three.js para 3D simples
   (kit em `kits/clay-retencao/template.html`), fotos de domínio público/CC da Wikimedia Commons (guarde créditos em
   `img/creditos.json`), b-roll livre do Pexels/Pixabay, mapas de `recursos/mapas/countries50m.geojson` (Natural Earth,
   domínio público), fontes de `recursos/fontes/` (Google Fonts, OFL). Imagem tem que fazer sentido com a fala.
4. **SFX**: proibido impact/pop ("tuk-tuk"). Só whoosh suave (`recursos/sfx/whoosh.wav`) ou nenhum. Música opcional baixinha.
5. **Montar**: escreva `edit.json` (FORMATO.md). Se o estilo pedir HTML próprio, crie `template.html` + `build.py`
   (veja os exemplos em `VIDEOS/01-*` a `VIDEOS/13-*`).
6. **Render**: `python editor/build_from_edit.py VIDEOS/NN-estilo --render` (usa o HyperFrames do próprio pacote).
7. **Conferir**: `ffmpeg -i <mp4> -vf blackdetect=d=0.3:pix_th=0.1 -an -f null -` + 1 contact-sheet do resultado.
   Corrigir só o óbvio (tela preta, texto cortado, animação parada). No máximo 1 re-render.
8. **Registrar o estilo**: se ficou bom e vai repetir, transforme em estilo de fábrica
   (`editor/fabrica/estilos/<nome>/estilo.json` + `preencher.py`, copiando a estrutura de `historia-simples`)
   e crie a ficha `ESTILOS-NOVOS/NN-<nome>/ESTILO.md` com o link da referência.
9. Apague a pasta `ref/` no fim (é material de terceiros).

## Economia de tokens
Saídas de comando curtas (`head`, `Select-Object -First`). Imagens SÓ em contact-sheet (máx 4-5 por vídeo).
Não reler arquivos já lidos.
