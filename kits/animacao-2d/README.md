# Kit animacao-2d — modelo base de animação 2D com personagem (recorte, em código)

Origem: teste "Marco Aurélio — O estoicismo" (`VIDEOS/100-teste-marco-aurelio-estoicismo`), feito para copiar o estilo de
animação do reel "E se Sócrates tivesse Instagram?" (ilustração plana, personagens recorrentes, cenários em camadas).
Serve para qualquer assunto: troque personagem, cores, cenários e cenas; o **motor** e as **checagens** ficam.

## Arquivos
| Arquivo | Para quê |
|---|---|
| `modelo.html` | Esqueleto HyperFrames (CSS, fontes, timeline, montagem das cenas). Não editar por vídeo. |
| `motor.js` | Personagens (`pessoa` de frente, `lado` de perfil, `costas`) + movimento (`andar`, `parado`, `gesto`) + utilitários. |
| `cenarios.js` | Fundos prontos (noite/palco, biblioteca, palácio, mercado…) e peças (casas, Partenon, chama, silhuetas). |
| `catalogo.json` | Ficha de cada tipo de cena (local, vista, ação, câmera) — usada para impedir repetição. |
| `embutir.py` | Monta `<pasta>/template.html` = modelo + motor + cenários + `<pasta>/cenas.js` + fontes. |
| `checar_movimento.mjs` | **Guarda de movimento**: abre o vídeo num Chrome escondido e mede cada personagem quadro a quadro. |
| `checar_variedade.py` | **Guarda de variedade**: reprova cena/plano repetido. |
| `construir.py` | **Pipeline**: montar → gerar → checar movimento → checar variedade → (só então) renderizar. |

## Vídeo novo (passo a passo)
1. Copie `VIDEOS/100-teste-marco-aurelio-estoicismo/` para `VIDEOS/NN-nome/` (leve `cenas.js` e `edit.json`; apague `hf/`, `*.mp4`).
2. `edit.json`: uma linha por cena (`type:"scene"`, `by:"template"`, `start`, `dur`, `props.scene` = nome da cena, `props.params` = textos).
   Tempos vêm da fala (whisper `words.json`) — nunca chute com áudio disponível.
3. `cenas.js`: uma função `CENAS.nome = (id,S,D,P)=>{…}` por tipo de cena. **Cada tipo novo ganha uma ficha em `catalogo.json`.**
4. `python kits/animacao-2d/construir.py VIDEOS/NN-nome` — corrija o que reprovar. Depois `… --render`.
5. Olhe `sheet.jpg` (1 imagem) antes de entregar. Apague `ref/` (material de terceiros).

## REGRAS DE OURO (cada uma existe por um erro real já cometido)
1. **Perna só se mexe por `andar()`, e toda caminhada tem MOTIVO.** `andar()` prende o número de passos à distância percorrida
   (passos inteiros e PARES: termina com os pés juntos), vira o personagem para o lado em que anda e **exige `por:"…"`** (para onde vai e
   por que a fala justifica) — sem isso o vídeo nem monta. Velocidade média máx **0,6 alturas/s** (caminhada calma; o pico medido não passa de 1,0).
   **Parado = `parado()`**, que nunca mexe pernas. *Erros reais:* (a) ciclo de perna com tempo fixo + desaceleração = "correndo",
   patinando e pisando depois de parar; (b) caminhadas sem destino nos primeiros 10 s, sem relação com a fala; (c) limite de velocidade
   frouxo (1,9) deixava passar corrida.
2. **Nunca escale o `<g id>` do personagem.** Posição = `x,y` no `<g id>`; escala = `.esc` (com `svgOrigin:"0 0"`, o pé). *Erro original:*
   escalar o grupo que tem `translate` no atributo jogava o personagem para o céu quando encolhia.
3. **Em SVG use `svgOrigin`, nunca `transformOrigin` em px.** *Erro original:* a chama do fogo "pulava" pela tela.
4. **Nunca anime `x`/`y` de um elemento que já tem `translate` no atributo** — envolva num `<g>` interno e anime o interno.
5. **`repeat` sempre finito** (o render busca quadros por tempo; `repeat:-1` quebra). Nada de `Math.random()` (use `rng(seed)`), `play()`.
6. **Animação de peça que não existe é erro** (o checador reprova "GSAP target … not found"). Use `existe(sel)` antes de animar parte opcional (ex.: olhos de personagem de costas).
7. **Todo texto visível e todo tempo vêm do `edit.json`.** Nada hard-coded nas cenas (senão o painel não consegue editar).
8. **Cada cena diz o que ilustra:** `edit.json` precisa de `fala` (trecho da narração) em toda cena e `porque` nas cenas de andar. No máx. 2 cenas de caminhada
   em cada 5 seguidas — alterne com cenas paradas, close, objeto, costas.
   **Variedade:** a mesma ficha (local+vista+ação) só volta depois de 12 cenas; o mesmo tipo de cena, depois de 8; duas cenas seguidas
   no mesmo local precisam mudar pelo menos 2 de (vista, ação, câmera); no máx. 4 cenas seguidas com a mesma vista; cena ≤ 6 s; média ≤ 4,5 s.
   Para 200 cenas: acrescente locais, vistas, ações e câmeras ao kit (combinações), não repita desenho.
9. **Arte (padrão do original):** contorno escuro grosso (~3,5 px) em TUDO (`LN`/`ST`/`OL` no kit), cenários em camadas (`.l0/.l1/.l2`),
   detalhe denso (toldos com franja, ânforas, panos, colunas com estrias), textura de papel (`.grao`), feixes de luz, paleta contida.
10. **Ritmo de cortes:** no máx. 2 cortes em qualquer janela de 8 s e nenhuma cena < 2 s (o original: 1 corte a cada ~4–6 s). Objeto que o personagem segura
   é FILHO do grupo do braço (`insertAdjacentHTML` em `.armA`) e gira em torno da MÃO — nunca um elemento solto "perto" da mão.
11. **Calma:** o original tem ~44 % de janelas de 1 s quase paradas e ~1,6 % da tela em movimento. Câmera só se mexe em 1–3 cenas
   (pan/zoom deliberado); personagem quase sempre PARADO (respira/pisca/gesto curto); cortes SECOS (fade só em capítulo: `props.entrada:"fade"`).
   `checar_calma.py` roda depois do render e avisa se estiver agitado demais.
12. **Roteiro/voz do usuário é fixo.** Fatos: só o que é verdade; imagens livres (Wikimedia/Pexels/Pixabay) com créditos; nada de logo/personagem de terceiros.

## Fluxo por CAPÍTULO (vídeos longos)
`VIDEOS/NN-projeto/` guarda `voz.mp3`, `words.json`/`frases.json` (Whisper), `capitulos.json`, `STORYBOARD.md`, `cenas.js` (todas as cenas do projeto, cresce a cada capítulo)
e uma pasta `capNN/` por capítulo (`edit.json`, áudio recortado, `final.mp4`). Passos: (1) storyboard do capítulo → usuário aprova; (2) `gerar_capNN.py` monta o
`edit.json` com os tempos REAIS das palavras; (3) `construir.py VIDEOS/NN-projeto/capNN --render`; (4) usuário vê e pede correções; (5) próximo capítulo.
`edit.json` por cena: `fala` (obrigatório), `porque` (se anda), `longa` (motivo, para cena de 6–9 s), `continua` (mesma cena em etapas, ex.: trio que ganha personagens).
Imagem real (domínio público/CC0, sem crédito): `img/arquivo.jpg` + `__IMG(arquivo.jpg)__` na cena (o `embutir.py` a embute); registre a origem em `img/CREDITOS.txt`.

**ids únicos por cena:** `defs` (degradês/padrões) usam `${id}c`, `${id}f`…; personagens usam `${id}m`, `${id}z`, `${id}k`… — nunca a mesma letra (o checador reprova id duplicado).

### Cenas genéricas e gerador de capítulos (projeto 101)
`gerar_lib.py` (`Cap`: tempos pelas palavras, recorte do áudio, whoosh, `edit.json`) + `caps_NN_MM.py` (storyboard em código). Cenas genéricas parametrizáveis em `cenas.js`:
`retrato`, `listaChar`, `riscados` (x / ✓), `contraste2`, `pergunta2`, `cartao`, `multidao`, `globo`, `contrario`, `linhaTempo`, `post`, `estatua`, `insulto`, `varandaTxt`.
Ícones: `ic(nome,x,y,e)` (biblioteca em `cenarios.js`; acrescente ícones novos lá). `_ajusta_t` impede fundo vazio (1º item ≤ 1 s). `montar_final.py` junta os capítulos.

## O que cada checagem pega
- `checar_movimento.mjs`: teleporte (salto de posição), corrida (> 1,9 alturas/s), ida-e-volta sem motivo, pernas mexendo parado,
  deslizar sem mexer as pernas, passo fora de proporção (0,28–1,1 altura = pé deslizando), terminar fora da tela, erro de JavaScript, alvo GSAP inexistente.
- LINT embutido no `modelo.html` (lido pelo `checar_movimento.mjs`): reprova x/y animado em elemento SVG que já tem `translate(...)` no atributo (regra 4) — pegou celular, símbolos e partículas fora do lugar.
- `checar_variedade.py`: tipo sem ficha, cena > 6 s, repetições (regra 8), média de duração.
- `construir.py`: nada é renderizado se uma checagem reprovar; no fim confere tela preta e gera `sheet.jpg`.

## Limites conhecidos (honestos)
- As checagens garantem movimento **coerente**, não que o desenho seja **bonito**. Olhar o `sheet.jpg` continua obrigatório.
- Personagem é vetor simples (sem sombreado, poucas expressões). Evoluir o desenho = editar `motor.js` (todos os vídeos herdam).
- Cenas com gestos complexos (sentar, virar, correr) ainda não existem: criar no `motor.js` **com** teste no `checar_movimento.mjs`.
- Pedem internet no render (GSAP via CDN e Chrome do HyperFrames, já instalado pelo setup).
