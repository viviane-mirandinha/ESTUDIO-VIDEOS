# Formato `edit.json` (v1) — Editor de Vídeos Local

Todo vídeo feito por Claude deve sair com **`<pasta do projeto>/edit.json`**.
O editor (`ABRIR EDITOR.bat` → http://localhost:8780) lista toda pasta que tem `edit.json`,
deixa o usuário mexer em texto/tempo/mídia e re-renderiza local.

```
<projeto>/
  edit.json          ← fonte da verdade (o editor salva aqui)
  template.html      ← só se "template": "local" (composição própria do vídeo)
  voz.wav, musica.mp3, img/, clips/ ...   ← mídias (caminhos RELATIVOS ao projeto)
  hf/index.html      ← GERADO por build_from_edit.py (não editar à mão)
  thumb.jpg          ← miniatura na lista (opcional; o editor gera depois do 1º render)
  final.mp4, leve.mp4 ← saída do botão Renderizar
```

Gerar/renderizar por linha de comando:
```
python editor/build_from_edit.py <pasta>            # só gera hf/index.html
python editor/build_from_edit.py <pasta> --render   # gera + render + áudio + leve.mp4
```

## Estrutura

```jsonc
{
  "version": 1,
  "name": "01 - Mapas - Por que a Rússia é tão grande",
  "canvas": { "w": 1280, "h": 720, "fps": 30, "bg": "#0b0c10" },
  "duration": 60.0,                     // segundos (fim do vídeo)
  "template": "generic",                // "generic" | "local" | nome em EDITOR VIDEOS/templates/<nome>.html
  "fonts": { "Inter": "fonts/Inter.ttf" },   // opcional: @font-face (caminho relativo ao projeto)
  "head": "",                           // opcional: <script>/<style> extras no <head> (ex.: three.js importmap)
  "audio": {
    "voice": { "src": "voz.wav",    "volume": 1.0, "start": 0 },
    "music": { "src": "musica.mp3", "volume": 0.12, "start": 0, "fade_out": 2.0, "duck": true },
    "extra": [ { "id": "a1", "src": "sfx/whoosh.wav", "start": 7.4, "volume": 0.2, "label": "whoosh" } ]
  },
  "tracks": [                           // ordem = camada (primeira = fundo). Só visual/organização.
    { "id": "fundo",   "name": "Cenas / mídia" },
    { "id": "visual",  "name": "Gráficos" },
    { "id": "textos",  "name": "Textos" },
    { "id": "legenda", "name": "Legenda" }
  ],
  "items": [ /* ver tipos abaixo */ ]
}
```

Áudio é mixado pelo próprio editor com ffmpeg (não coloque `<audio>` no HTML).
`duck: true` abaixa a música enquanto a voz fala. Sem SFX de impacto (regra do usuário).

## Item (campos comuns)

```jsonc
{
  "id": "t1",               // único, sem espaço (vira id do elemento no HTML)
  "type": "text",           // text | image | video | caption | html | scene | bloco | param
  "track": "textos",        // id da faixa
  "label": "Título 1",      // nome amigável na linha do tempo (opcional)
  "start": 2.0, "dur": 3.5, // segundos
  "hidden": false,          // true = não aparece (o editor tem botão olho)
  "by": "template",         // opcional: item desenhado pelo template local (não pelo builder genérico)
  "in": "fade",  "out": "fade",   // entrada/saída: none|fade|slide_up|slide_left|pop|zoom|type (só texto)
  "props": { ... }          // depende do tipo
}
```

Posição/tamanho em **pixels do canvas**: `x`,`y` = **centro** do elemento. `w`,`h` opcionais.
Para ocupar a tela toda: `"fill": true`.

### `text`
```json
"props": { "text": "A RÚSSIA TEM 11 FUSOS", "x": 640, "y": 600, "w": 1000,
  "size": 64, "color": "#ffffff", "font": "Inter", "weight": 800, "align": "center",
  "bg": "rgba(0,0,0,.6)", "pad": 16, "radius": 12, "stroke": "", "shadow": true,
  "highlight": ["11 FUSOS"], "hl_color": "#ff8a1f", "upper": false }
```

### `image`
```json
"props": { "src": "img/mapa.jpg", "fill": true, "fit": "cover",
  "x": 640, "y": 360, "w": 1280, "h": 720, "opacity": 1, "radius": 0,
  "motion": "zoom_in", "motion_amount": 0.08 }
```
`motion`: none | zoom_in | zoom_out | pan_left | pan_right | pan_up | pan_down (Ken Burns).

### `video`
```json
"props": { "src": "clips/b1.mp4", "fill": true, "fit": "cover", "trim": 3.2,
  "volume": 0, "speed": 1, "opacity": 1, "motion": "none" }
```
`trim` = segundo do arquivo onde começa. `volume` > 0 → o som do clipe entra no mix.

### `caption` (legenda palavra-por-palavra)
```json
"props": { "words": [ {"w":"Postar","s":0.58,"e":1.02}, ... ],  // ou "words_file": "words.json"
  "per_group": 3, "x": 640, "y": 620, "size": 52, "color": "#ffffff", "dim": "#6b6d74",
  "hl_color": "#ffd400", "keywords": ["RETENÇÃO"], "bg": "rgba(0,0,0,.55)", "font": "Inter", "weight": 800 }
```
Tempo das palavras é absoluto (segundos do vídeo). `start/dur` do item limita onde a legenda aparece.

### `html` (bloco livre)
```json
"props": { "html": "<div class='box'>...</div>", "css": ".box{...}", "x": 640, "y": 360, "w": 600, "h": 300 }
```

### `scene` (cena pronta registrada — mapas, iceberg, contador, título...)
```json
"props": { "scene": "titulo", "params": { "titulo": "CAPÍTULO 2", "sub": "A queda", "cor": "#ff3b30" } }
```
Cenas ficam em `EDITOR VIDEOS/templates/scenes/<nome>.html` (ver "Criar cena" abaixo).
O editor mostra cada `params` como campo editável.

### `bloco` (✨ Animação pronta — bloco do registry oficial do HyperFrames, Apache-2.0)
```json
{ "id": "anim1", "type": "bloco", "track": "visual", "label": "Nome na tela — barra branca", "start": 2.0, "dur": 4.8,
  "in": "none", "out": "none",
  "props": { "bloco": "lt-clean-bar", "x": 640, "y": 360, "scale": 1, "fit": "contain", "speed": 1,
             "textos": [ {"de": "Dr. Maya Chen", "para": "Maria Souza"}, {"de": "Host · Neuroscientist", "para": "Historiadora"} ],
             "vars": { } } }
```
Blocos ficam em `EDITOR VIDEOS/templates/blocos/<nome>/` (`<nome>.html` original + `assets/` + `bloco.json` + `thumb.jpg`;
licenças em `templates/blocos/LICENCAS-TERCEIROS.md`). O builder embute o bloco na composição principal (ids com prefixo
`<id>__`, CSS com escopo, timeline do bloco aninhada em `start`), então funciona na prévia do editor e no render.
- `textos`: troca literal de cada texto original (`de`) pelo novo (`para`) — o editor mostra um campo por texto.
- `vars`: variáveis declaradas pelo bloco (`bloco.json` → `variables`), ex. `boardText`, `accent`.
- `x`,`y` = centro; `scale` multiplica o encaixe (`fit`: `contain` cabe inteiro, `cover` preenche); `speed` acelera/desacelera.
- O bloco é desenhado em 1920×1080 e escalado pro tamanho do vídeo (9:16: aumente `scale` e mova `y`).
Instalar mais blocos: `python ferramentas/importar_blocos.py <nome>` (só blocos do registry oficial, Apache-2.0).

### `param` (valor solto lido pelo template local)
```json
{ "id": "cor_destaque", "type": "param", "label": "Cor de destaque", "props": { "value": "#ff8a1f" } }
```
Sem `start/dur`; aparece no painel "Ajustes gerais".

## Templates

### `"template": "generic"` (padrão)
O builder desenha tudo a partir dos itens (text/image/video/caption/html/scene). Ideal para
documentário, b-roll + texto, slideshow, mapas com imagem, iceberg com imagens etc.

### `"template": "local"` (vídeo sob medida: 3D, Three.js, animação complexa)
O projeto tem `template.html` (composição HyperFrames completa). O builder substitui:

| marcador no template.html | vira |
|---|---|
| `__EDIT__` | o edit.json inteiro (objeto JS) |
| `__DUR__` / `__W__` / `__H__` / `__FPS__` | duração / largura / altura / fps |
| `<!--__ITEMS__-->` | itens genéricos (sem `"by":"template"`) desenhados por cima |
| `<!--__ITEMS_SCRIPT__-->` | script dos itens genéricos (colocar no fim do `<body>`, depois do timeline) |

No template, ler os itens assim:
```js
const EDIT = __EDIT__;
const ED = Object.fromEntries(EDIT.items.map(i => [i.id, i]));
// ex.: carimbo
const st = ED.st0;  el.textContent = st.props.text;  // tempo: st.start, st.start + st.dur
// respeitar st.hidden (o editor usa para esconder elementos)
```
Marque esses itens com `"by": "template"` para o builder não desenhar de novo.
Regra: TODO texto visível e todo tempo importante do vídeo deve vir do edit.json (não hard-code),
senão o usuário não consegue mudar pelo editor.

### Template nomeado (`"template": "<nome>"`)
Igual ao local, mas o arquivo fica em `EDITOR VIDEOS/templates/<nome>.html` e é reaproveitado
por vários vídeos do mesmo estilo/canal.

## Criar cena (`templates/scenes/<nome>.html`)
Fragmento HTML com marcadores; o builder troca:
`{{id}}` `{{start}}` `{{dur}}` `{{W}}` `{{H}}` `{{p.<param>}}` (texto escapado) `{{json}}` (params como JSON).
Primeira linha opcional: `<!--params {"titulo":"Título padrão","cor":"#ff3b30"}-->` (padrões + campos do editor).
O script da cena recebe o timeline principal em `tl` e anima em tempo **absoluto** (`{{start}} + x`):
```html
<!--params {"titulo":"CAPÍTULO 1","sub":"","cor":"#ff3b30"}-->
<div id="{{id}}" class="sc-titulo"><h1>{{p.titulo}}</h1><p>{{p.sub}}</p></div>
<script>
(function(tl, P){ const S={{start}}, D={{dur}};
  tl.fromTo("#{{id}} h1",{opacity:0,y:40},{opacity:1,y:0,duration:.6},S+.1);
})(window.__timelines.main, {{json}});
</script>
```
Pode usar Three.js/canvas: desenhe em função do tempo (`tl.eventCallback` não; use um tween
`onUpdate` ou leia `tl.time()` num `__hfRender`). Nada de `Math.random()` sem seed, nada de `play()`.

## Regras para Claude ao criar vídeo novo
1. Escrever `edit.json` (este formato) — nunca só HTML solto.
2. Mídias dentro da pasta do projeto, caminho relativo.
3. Rodar `build_from_edit.py <pasta>` e conferir `hf/index.html` com `hyperframes lint`.
4. Renderizar com `build_from_edit.py <pasta> --render` (gera `final.mp4` + `leve.mp4` < 30 MB + `thumb.jpg`).

## Campos extras (opcionais) no edit.json
- `"estilo": "Nome do estilo de edição"` — aparece no card da lista (ex.: "Canal de história simples").
- Param global de tamanho de letra num template local: item `{"id":"fonte_escala","type":"param","props":{"value":1.8}}` + no template `font-size:calc(Npx * var(--fs,1))` e setar `--fs` lendo `__EDIT__` (ver 09-tamanho-3d). Letras pequenas em 1280x720 = reprovação: títulos ≥ 48px, texto de apoio ≥ 24px.

## Modo fábrica (`EDITOR VIDEOS/fabrica/`)
`python fabrica\fabrica.py --estilo <nome> --tema "..." --canal "NOME"` gera um vídeo novo inteiro **sem token do Claude**:
roteiro pelo Ollama local (mistral/qwen na 4090, regras de copywriter), voz por TTS local (Qwen3-TTS → Chatterbox → edge-tts),
`words.json` pelo faster-whisper GPU, fotos do Wikimedia Commons (buscas escolhidas pelo Ollama, créditos em `img/creditos.json`)
ou gameplay do estoque, e então `estilos/<nome>/preencher.py` escreve o `edit.json` neste formato reproduzindo as regras do
vídeo-teste original (cenas, Ken Burns, tints, legenda, CTA). Depois chama `build_from_edit.py --render` e grava `RELATORIO.json`
com minutos por etapa e `tokens: 0`. Estilos de "preencher dados" já convertidos: `historia-simples` (04), `reddit-story` (12),
`psicologia-sombria` (08). Estilos "sob medida" (01 mapas, 06/07 bonecos, 09/13 Three.js, 10/11 motion/mapas ilustrados)
exigem código novo por tema e não entram na fábrica. Leia `fabrica/COMO_USAR.md`.

## RELATORIO.json (na pasta do projeto) — lido pelo botão 📊 Relatório
```json
{"estilo":"...","inicio":"2026-10-21T23:35:12-03:00","fim":"...","minutos":15.5,"render_segundos":49,
 "tokens":1250000,"custo_usd":9.4,"observacoes":"texto livre"}
```
`tokens`/`custo_usd` são opcionais mas desejados (a calculadora usa). Sem BOM.

## Referência (obrigatório em todo vídeo novo)
```json
"referencia": {"canal": "Nome do canal", "canal_url": "https://www.youtube.com/@canal", "video": "https://youtu.be/ID", "titulo": "título do vídeo copiado", "nota": "observação"}
```
Aparece no card (📺 Vídeo copiado / 📡 Canal) e em Ajustes do vídeo. `yt-dlp --print "%(channel_url)s|%(channel)s|%(title)s" URL` preenche canal_url/canal/titulo.

## Cards "🎞 só vídeo" + 📥 Importar (mp4 sem edit.json)
- Nas pastas de **criativos** (origem "Criativos TONICO"/"Criativos MERCADO" em `DEFAULT_FOLDERS`/config.json) o `/api/projects` também lista `.mp4` soltos (pasta + 1 subpasta; ignora clips/broll/assets/hf/midia/img/_tmp e render_mudo/silent/leve/base; máx. 200 mais recentes) como `{tipo:"video", origem, w,h,fps,dur}` — ffprobe com cache em `<pasta>\.editor_cache\probe.json`, miniatura `<pasta>\.editor_cache\<nome>.jpg` gerada em thread de fundo. Pastas de estilos e kits só entram com `edit.json`. Todo card tem `origem` (filtro no topo da lista: Todos / Estilos YouTube / Criativos TONICO / Criativos MERCADO / Outros).
- `POST /api/importar/{id}` (só no clique em 📥 Importar): cria `<mesma pasta>\<nome>\`, **move** o mp4 pra dentro, escreve `edit.json` mínimo (canvas = w/h/fps do vídeo, `items=[{id:"v1",type:"video",track:"fundo",props:{src:"<nome>.mp4",fill:true,fit:"cover",volume:1}}]`, `estilo:"Vídeo importado"`) e devolve `{pid, folder}`; o editor abre na hora e o card vira projeto normal.

## Tela ➕ Pedir vídeo (`/api/estilos` + `POST /api/pedido`)
- `GET /api/estilos` lista os estilos: `fabrica` (fabrica/estilos/*, 0 token), `claude` (projetos-teste 01-13) e `em_breve` (TESTE ESTILOS DARK/ESTILOS-NOVOS). `POST /api/pedido {estilo, tema|roteiro, canal_nome, duracao, ref_canal, ref_video, voz}` devolve `{job}`; estilo fábrica roda `fabrica.py` (1 por vez, fila) e grava `referencia` no edit.json; o resultado do job traz `{pid, folder, rendered}`.
- Estilo claude/em_breve: cria `VIDEOS\NN-pedido-<estilo>-<tema>\` com **`PEDIDO.md`** (estilo, referência, tema/roteiro, canal, duração) e um `edit.json` vazio (`items: []`, aparece como ⏳). Claude deve ler o PEDIDO.md, montar o `edit.json` nesta mesma pasta e renderizar — o card vira ✅ sozinho.

## Ferramentas do Estúdio (fase 1, 22/10/2026 — tudo local, 0 token)
- **Fila (Meus vídeos):** todo trabalho vira job (`render`, `fabrica`, `pedido`, `video_imagens`, `roteiro`, `medir`) com etapa, %, tempo que falta, cancelar e "abrir resultado". `GET /api/jobs`, `POST /api/jobs/{id}/cancelar`, `POST /api/jobs/limpar`; histórico em `EDITOR VIDEOS\jobs.json`. Jobs pesados (render, fábrica, IA local) rodam 1 por vez (mesma trava do `/api/pedido`). Scripts falam com a fila por linhas `@@<pct>|<mensagem>` no stdout.
- **Ajustes:** `EDITOR VIDEOS\ajustes.json` (`modelo_ollama` padrão qwen2.5:7b, `voz` = `motor:nome`, `pasta_saida`, `pexels_key`/`pixabay_key`/`anthropic_key` opcionais, `idioma`). Lido por `fabrica\lib\ajustes.py`. `GET/POST /api/ajustes`, `/api/ajustes/modelos|vozes|testar|pasta`.
- **Vídeo com imagens:** `fabrica\video_imagens.py preparar|montar --pasta P` (lê `P\pedido.json`). Preparar: roteiro Ollama (se tema) → TTS → `words.json` → frases → busca por frase (`fabrica\lib\bancos.py`: Wikimedia sempre; Pexels/Pixabay fotos+clipes só com chave) → `cenas.json` (`estado: conferir`, candidatos e escolha por cena) + `edit.json` provisório. Montar: `estilos/<estilo>/preencher.py` → `edit.json` → `build_from_edit.py --render` → `RELATORIO.json` (tokens 0). Pastas `NN-imagens-<tema>` na pasta de saída. Estilo novo `broll-documentario` (fotos/clipes em Ken Burns, legenda palavra a palavra, título, cartão final; `so_ferramenta: true` = não aparece na galeria).
- **Conferir imagens:** `GET /api/vi/{pid}`, `POST /api/vi/{pid}/escolher {i,c}`, `/buscar {i,q}`, `/subir/{i}` (arquivo do PC), `/renderizar`.
- **Roteiro pronto:** `fabrica\roteiro_pronto.py <pasta>` com `pedido.json {acao: transcrever|estrutura|escrever|melhorar}` → `resultado.json` (+ `ROTEIRO.txt`, `TRANSCRICAO.txt`) em `EDITOR VIDEOS\roteiros\<data>-<acao>-<tema>\`. Legenda do YouTube via yt-dlp (1 trilha, json3; cache em `roteiros\_cache`), sem legenda → faster-whisper. Ollama em etapas (estrutura → bloco a bloco → kit), anti-loop em código, aviso "confira os fatos". "Revisar com o Claude" (`fabrica\lib\claude_rev.py`): sem chave só copia o pedido; com chave chama `claude-sonnet-5-5` mostrando custo estimado.
- **Estilos que estão bombando:** `GET /api/bombando` junta `ESTILOS-NOVOS\RESUMO.md` + `REFERENCIA.txt`, os 13 originais (`referencia` do edit.json) e `VIDEOS-SHORTS`; `POST /api/bombando/atualizar` mede views/hora (yt-dlp `--flat-playlist` + `approximate_date`) com cache em `.cache\bombando-medidas.json`.
- A interface nunca mostra caminho do PC (usa nomes como "Área de Trabalho › …"); caminhos só no texto copiado pro Claude (balão "Quer mudar alguma coisa?").

## Ferramentas do Estúdio (fase 2, 22/10/2026 — tudo local, 0 token)
Barra de cima: **Início · Estilos prontos · 🧰 Ferramentas ▾ · Meus vídeos** (o menu agrupa Vídeo com imagens, Fábrica de Shorts, Fábrica de cortes, Editor de vídeo falado, Ideias, Roteiro pronto, Bombando, Copiar estilo de edição, Extras). Endereços diretos: `#shorts`, `#cortes[=<cid>]`, `#falado[=<fid>]`, `#ideias`, `#extras`, `#copiar`.
- **📱 Fábrica de Shorts:** é o pipeline do Vídeo com imagens com estilo `vertical: true` no `estilo.json` (canvas 1080x1920). `GET /api/vi/estilos?formato=short`, `POST /api/vi/criar` (pasta `NN-short-<tema>`, job `short`). Roteiro curto por `fabrica\lib\curto.py` (gancho ≤ 8 palavras, frases numeradas → texto, completa se faltar, corta frase repetida). Bancos com `vertical=True` (Pexels/Pixabay em pé; clipes normalizados 1080x1920). Short = 1 assunto: o Ollama diz o assunto em inglês (ex.: "flamingo") e ele entra em toda busca que não o tenha. Fatos da Wikipedia preferem o artigo com o 1º substantivo do tema (`fatos.py`). edge-tts tenta 3x (rede instável). Estilo novo `short-documentario` (título fixo no topo, legenda 2 palavras ~108 px no centro, foto/clipe por frase, cartão final 1,6 s). Os shorts de teste (3D/rankings, VIDEOS-SHORTS) são sob medida → não entram na fábrica (use Copiar estilo).
- **Estilos "por preset":** pasta `fabrica\estilos\<id>\` com `estilo.json` (`preset: {formato, cor_destaque, cor_texto, fundo, fonte, legenda, legenda_pos, legenda_palavras, legenda_tamanho, legenda_caixa, titulo_fixo, zoom, flash_cada, vinheta, cartao_final, cta, transicao}`) + `preencher.py` stub gerado por `lib\preencher_preset.criar_estilo()`; o desenho fica em `fabrica\lib\preencher_preset.py`. Usado pelo short-documentario, pelos estilos do Copiar rápido e pelos Extras.
- **Conferir imagens:** `POST /api/vi/{pid}/desfazer {i}` (cada troca guarda a anterior em `cenas[i].antes`, até 6) e `POST /api/vi/{pid}/amostra {segundos:20}` → `video_imagens.py montar --amostra 20` renderiza só o começo em `EDITOR VIDEOS\.cache\amostras\<pasta>\` (mídias com caminho absoluto; o projeto não muda); `GET /api/vi/{pid}/amostra.mp4`.
- **✂ Fábrica de cortes:** `fabrica\cortes.py --pasta P` (`pedido.json`: `url` ou `arquivo`, `de/ate`, `n`, `modo ia|regras`, `enquadramento desfocado|centro`, `dur_min/dur_max`, `intro`, `canal`, `programa`, `idioma`). Etapas: yt-dlp (até 720p; se bot-check → `player_client=mweb -f 18`) → `audio.wav` → faster-whisper (`lib\transcrever.py` agora aceita `idioma`, `auto` = detecta) → frases → janelas de frases inteiras entre dmin-dmax → nota por regras (`lib\fala.nota_regras`: energia da voz vs. mediana, gancho com pergunta/número/palavra forte, começo sem conectivo, fecho com pontuação) → modo `ia`: os 3N+3 melhores sem sobrepor vão pro Ollama em lotes de 4 (nota 0-10 + título + motivo; nota final = 0,7 IA + 0,3 regras) → N cortes sem sobrepor. Cada corte = projeto `P\corte-NN-<titulo>\` (`clip.mp4` 30 fps CFR, `words.json` relativo, `edit.json` 1080x1920: fundo = o mesmo vídeo com `blur`/`brilho` + vídeo inteiro no meio, ou tela cheia; título no topo; legenda 2 palavras 92 px) → `build_from_edit --render`. Intro opcional `P\intro-melhores-momentos\` (começo dos 3 melhores, 3-5 s cada). `P\cortes.json` + `P\RELATORIO.json` (tokens 0). API: `POST /api/arquivo` (upload), `POST /api/cortes/criar`, `GET /api/cortes`, `GET /api/cortes/{cid}`.
- **🎙 Editor de vídeo falado:** `fabrica\falado.py --pasta P` (`pedido.json`: `arquivo`, `saida 16:9|9:16|ambos`, `silencio`, `retakes`, `min_sil` 0,6 s, `legenda`, `broll`, `n_broll`, `titulo`). Normaliza em `bruto.mp4` (720p, 30 fps, keyframe 0,5 s) → `words_bruto.json` → silêncios por `silencedetect` com limiar automático (volume médio − 6 dB, entre −45 e −12) e só saem se > `min_sil` (respiro curto fica; nunca corta palavra) → retakes (`lib\fala.retakes`: frase seguinte começa igual / ≥ 78 % parecida → sai a primeira) → `cortes.json` (`manter`) → `words.json` remapeado → b-roll opcional (Ollama escolhe frases concretas + busca; máx. 1 a cada ~7 s; Wikimedia/Pexels/Pixabay) → `edit.json` com **1 item `video` por trecho mantido** (`src: bruto.mp4`, `trim` = onde começa no bruto, `volume 1`) → render. "Os dois": 16:9 na pasta e 9:16 em `P\vertical\` (hardlink do bruto). API: `POST /api/falado/criar`, `GET /api/falado/{fid}`.
- **Render com nova tentativa (23/10):** `hf_render` roda com `HF_SEGMENTED_CAPTURE=true`, `--gpu` (se tiver NVIDIA, nas 3 primeiras) e `--resume` só se a versão do HyperFrames tiver (lido do `--help`; a 0.7.111 não tem). Se o Chrome cair no meio ("Try --docker…"), tenta de novo até 8 vezes com perfil mais leve (`--workers 2→1`, timeouts maiores, `--low-memory-mode` a partir da 4ª), mensagem "O render caiu — tentando de novo (N/8)…". Começo (40 linhas) + fim (40 linhas) de cada tentativa vão pra `render-erro.log` na pasta do projeto; se as 8 falharem, o "Ver o erro" da fila mostra esse log.
- **`build_from_edit.py`:** props novas em `image`/`video`: `blur` (px) e `brilho` (0-1) → `filter:` CSS (com `scale(1.12)` pra esconder a borda do desfoque). Legenda (`caption`) respeita `upper: true` (text-transform).
- **💡 Ideias** (`fabrica\lib\ideias.py`, cache em `EDITOR VIDEOS\.cache\ideias\`, resultados em `EDITOR VIDEOS\ideias\`): Caçador de nicho = busca do YouTube por URL de resultados com `--flat-playlist` + `youtubetab:approximate_date` (traz views + data → views/hora; nunca abre página de vídeo) + até 8 canais (`/videos` flat -J: inscritos, mediana de views e de views/hora, outliers 3x+, uploads em 30 dias), pausa de 2 s entre canais, cache 1 dia (busca) / 3 dias (canal). Nicho tá saturado? = link (oEmbed pro título do vídeo; canal pelos títulos) → nicho em 2-4 palavras (Ollama) → mesma coleta → nota 0-10 por regras (canais distintos, vídeos do último mês, canais pequenos com 5 mil+ views, gigantes 1 mi+, views/hora) + explicação em frases. O que o público pede = `yt-dlp --write-comments` (top, até 500; se falhar → mweb) → Ollama resume pedidos/reclamações/elogios/ideias. Placar de ideias = `ideias\placar.json` (nota Ollama + título sugerido + porquê; status e views reais editáveis; mostra se nota 7+ teve mais views). API: `POST /api/ideias/cacar|saturado|publico|placar`, `GET /api/ideias/ultimos|placar`, `PUT/DELETE /api/ideias/placar/{id}`.
- **🎨 Copiar estilo de edição:** dois modos na mesma tela. **⚡ Aproximado (grátis)** = `fabrica\copiar_estilo.py --pasta <.cache\copiar\data>`: baixa os 3 primeiros min → `ffmpeg select=gt(scene,0.32)` (cortes/min, cena média) → 16 quadros → paleta (PIL mediancut; destaque = cor viva mais presente) → texto na tela por contagem simples (10 faixas: bordas fortes + pixels brancos/amarelos) → legenda sim/não e posição → narração (whisper 60 s, ≥ 70 palavras/min) → salva `fabrica\estilos\meu-<nome>\` (`aproximado: true`, `analise`, `preset`, `capa.jpg` = folha local de quadros) e apaga a referência. Aparece na hora no Vídeo com imagens (deitado) ou na Fábrica de Shorts (em pé). **🧠 Fiel (com Claude, gasta tokens)** = o fluxo antigo (`POST /api/pedido estilo=copiar` → `PEDIDO.md`). API: `POST /api/copiar-rapido`, `GET /api/estilos-meus`, `DELETE /api/estilos-meus/{id}`.
- **🧩 Extras:** pasta `EDITOR VIDEOS\extras\<id>\` com `estilo.json` (estilo por preset) + `preview.mp4`/`capa.jpg` opcionais. Instalar = cria `fabrica\estilos\<id>\` com o NOSSO stub (`extra_de: <id>`; código de extra nunca é copiado, só json/mp4/imagens). Remover só apaga o que veio de extra. "Exportar pros Extras" (Copiar estilo) grava só o preset (sem `analise`/`referencia`). Sem rede. API: `GET /api/extras`, `POST /api/extras/{id}/instalar|remover`, `POST /api/extras/exportar`, `POST /api/extras/abrir`.
- Fila: tipos novos `short`, `cortes`, `falado`, `ideias`, `copiar`, `amostra`; o resultado do job pode trazer `cid` (cortes), `fid` (falado), `estilo_id`, `amostra_url` (botões em Meus vídeos).
- `jobs.json` e `ideias\*.json` são gravados em arquivo temporário + troca (queda de energia não deixa JSON vazio). Abrir `#cortes=<cid>` / `#falado=<fid>` mostra só o resultado (botão ➕ pra fazer outro).

## Narração: voz do PC × outra IA (23/10)
- Componente `vozEscolha()` (app.js) em Vídeo com imagens, Fábrica de Shorts, Pedir vídeo e Roteiro pronto: "🔊 Fazer o áudio aqui" (grátis) ou "📋 Copiar o roteiro e gerar a voz em outra IA" + área "🎙 Subir o áudio pronto" (arrastar/soltar, mp3/wav/m4a → `/api/vi/audio`).
- Sem roteiro ainda (modo tema): o botão vira "✍️ Escrever o roteiro e copiar" → `POST /api/vi/roteiro` (job: `video_imagens.py roteiro`, pedido com `so_roteiro`, pasta temporária em `.pedidos\roteiro-*`) devolve {roteiro, titulo, fonte_fatos}.
- Subiu o áudio: vai pro Vídeo com imagens modo "Tenho a narração" com tema/título e `#viRoteiroRef` preenchidos (Fábrica de Shorts mantém o short em pé e manda `modo: "audio"`). O servidor grava `roteiro_ref` no pedido; `video_imagens.py` usa o roteiro como texto do projeto e `_grafia_do_roteiro()` corrige a grafia das palavras do Whisper (tempos continuam do áudio).
- Janelas de progresso (Pedir vídeo, Renderizar) usam `acompanhar()`: Fechar (continua na fila) + Cancelar; erro mostra só a mensagem (`erroCurto`) + "📋 Copiar detalhes".

## Painel rápido + abas novas (23/10/2026)
- **Velocidade:** `/api/projects`, `/api/relatorios`, `/api/estilos`, `/api/bombando`, `/api/saude` usam cache em memória `memo()` (server.py): devolve na hora se a assinatura (mtime das pastas e subpastas via `os.scandir`) não mudou; passou do TTL (30–60 s) → devolve o que tem e recalcula em segundo plano; salvar edit.json, terminar trabalho ou gerar miniatura limpa o cache. Miniatura de projeto sem `thumb.jpg` é gerada em thread de fundo (`queue_thumb`), a lista não espera mais o ffmpeg. `probe_dur()` guarda a duração (arquivo+mtime+tamanho) — abrir o editor não roda ffprobe toda vez. GZip (`GZipMiddleware`, só texto; vídeo/imagem/áudio e respostas 206 ficam de fora). O servidor escuta em **127.0.0.1 e ::1** (o navegador tenta `localhost` pelo IPv6 primeiro; antes cada conexão perdia ~200 ms). Ao ligar, `_aquecer()` já calcula lista/estilos/checklist. Frontend: miniaturas com lazy-load (`data-bg`/`data-bgvar` + IntersectionObserver, função `lazyBg`) e lista "Meus vídeos" com 60 cards + "⬇ Mostrar mais".
- **Migração C→D:** `MIGRA`/`_mig()` em server.py trocam `<pacote>` por `<pacote>` quando existe (config.json já gravado com D:). `ajustes.py` e `fabrica.py` usam a pasta do D: como saída padrão.
- **Barra de cima:** Início · 💡 Ideação ▾ (Meus Feeds, Caçador de nicho, Nicho saturado?, O que o público pede, Placar de ideias, Estilos bombando, Roteiro pronto, Minhas vozes) · 🎬 Criar ▾ (Vídeo com imagens, Fábrica de Shorts, Stickman Studio, Fábrica de cortes, Editor de vídeo falado, Estilos prontos, Copiar estilo, Extras) · Meus vídeos · ⚙ Ajustes. Endereços: `#feeds[=<id>]`, `#vozes`, `#stickman`. `?menu=ideia|criar` abre o menu ao carregar (prints).
- **📡 Meus Feeds** (`fabrica\lib\feeds.py`): feeds em `EDITOR VIDEOS\feeds\feeds.json` (`{id,nome,palavras[],canais[],formato todos|shorts|longos,periodo hoje|semana|mes}`), resultado em `.cache\feeds\<id>.json`. Atualizar = job `feed`: busca do YouTube com `sp=EgQIAxAB` (semana + só vídeos; `EgQIAhAB` hoje, `EgQIBBAB` mês — o filtro só de data vem como "lockup" e o yt-dlp lê 0 itens) + `/videos` e `/shorts` dos canais de referência, tudo `--flat-playlist` + `youtubetab:approximate_date` (nunca abre página de vídeo), pausa 1,5–2 s; mediana de views/hora do canal pelo `ideias.info_canal` (cache 3 dias) → `fora_da_curva` = views/hora ≥ 2× a mediana do canal. API: `GET/POST /api/feeds`, `GET/DELETE /api/feeds/{id}`, `POST /api/feeds/{id}/atualizar`.
- **🎙 Minhas vozes** (`fabrica\lib\vozes.py`): vozes clonadas em `EDITOR VIDEOS\vozes\<id>\` (`ref.wav` 24 kHz mono cortado numa pausa entre 10–25 s + `ref.txt` = Whisper só desse trecho + `voz.json` + `teste.wav`). Motor = Qwen3-TTS **Base** (`C:\AI\qwen3-tts\falar.py --ref`). Id `clone:<id>` aparece em todas as listas de voz (`/api/ajustes/vozes`), e `tts.falar(motor="clone")` / `fabrica.py --tts clone` usam. Vozes do VoiceStudio: lidas (só leitura) de `%APPDATA%\OmniVoice\omnivoice.db` (`voice_profiles kind=clone`) + `voices\*.wav`; "Usar no Estúdio" copia ref+texto pra `vozes\vs-<id>\`. Amostras em `.cache\vozes\`. API: `GET /api/vozes`, `POST /api/vozes/amostra {voz,texto}` (Microsoft na hora; Qwen3/clone = job pesado), `POST /api/vozes/subir` (upload), `POST /api/vozes/clonar {nome, arquivo_id, consentimento}`, `POST /api/vozes/importar {id}`, `POST /api/vozes/padrao {voz}`, `DELETE /api/vozes/{id}`, `GET /api/vozes/arq/{cache|vs|<id>}/{arquivo}`.
- **🖍 Stickman Studio:** estilo `fabrica\estilos\stickman\` (`sem_imagens: true` = pula banco de imagens e o "conferir"; `formato_livre: true` = o pedido escolhe `formato: "16:9" | "9:16"`; `ferramenta: "Stickman Studio"`). Mesmo pipeline do Vídeo com imagens (`POST /api/vi/criar {estilo:"stickman", formato, modo tema|roteiro, duracao, voz, canal}` → job `stickman`, pasta `NN-stickman-<tema>`): roteiro Ollama → voz → Whisper → frases → `preencher.py` (Ollama escolhe pose/cenário/destaque/fala por frase em lotes de 8; se falhar, regras por palavra-chave) → 1 item `scene` por frase com a cena **`templates/scenes/stickman.html`** (SVG desenhado em JS, animação GSAP em tempo absoluto, seek-safe). Params editáveis da cena: `pose` (parado, explicando, apontando, pensando, surpreso, comemorando, andando, triste), `fala` (balão), `destaque` (texto-chave grande; a palavra mais forte/número sai na cor), `cenario` (chao, casa, cidade, escritorio, natureza, quadro, palco, vazio), `lado` (esq/dir), `pose2`/`fala2` (2º boneco), `cor`, `fundo`, `traco`, `desenhar` (o cenário "se desenha" na entrada), `entrada` (anda/pula/nada), `zoom`. Legenda `caption` 3 palavras (2 no 9:16) em caixa branca; cartão final com o boneco comemorando + canal.

## 🤖 Estilos IA (skills do Claude Code) — 24/10
- Aba `#skillsia` (menu Criar e botão no topo). Catálogo em `skills_ia/catalogo.json` (id = nome da skill em ~/.claude/skills), prévias em `skills_ia/previews/<id>.mp4`, pasta-fonte pra instalar em `skills_ia/fonte/` ou caminho em `skills_ia/fonte.txt`.
- `POST /api/skills-ia/pedido` {skill, itens:[{texto, arquivo_id}], versoes 1-5, ref, duracao, marca, canal, obs, so_pedido} → 1 trabalho (tipo "skill") por item×versão. Cria `NN-ia-<skill>-<tema>/` com `entrada/` (vídeo do aluno, ref.mp4), `PEDIDO.md`, `edit.json`.
- Roda `claude -p ... --output-format stream-json --permission-mode bypassPermissions` na pasta, 1 por vez (SKI_VEZ), limite 120 min; log em `claude-log.jsonl`, custo/tokens em `RELATORIO.json`. Resultado = `resultado.mp4` (ou o mp4 mais novo fora de entrada/) → vira item de vídeo no edit.json.
- Pacote: só `catalogo.json` vai (skills compradas e prévias não podem ser redistribuídas).
- `POST /api/skills-ia/ideias` {skill, nicho, ref, evitar} → 8 {titulo, gancho} pelo Ollama local (grátis). Com `ref` lê título/descrição do vídeo (yt-dlp) e sugere temas parecidos. A tela chama sozinha ao escolher o estilo e ao colar o link.
- Painel não manda mais copiar mensagem pro chat: `job_pedido_claude` (galeria "Com Claude" e Copiar estilo) também roda `_claude_rodar` e só devolve `precisa_claude` quando não há app do Claude no PC.
