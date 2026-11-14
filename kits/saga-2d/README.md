# Kit saga-2d — peças animadas + ritmo garantido

Para vídeos do estilo **Saga sobrevivência 2D** (modelo: `VIDEOS-SHORTS/01-saga-sobrevivencia-2d`).
Objetivo: todo vídeo novo sair **dinâmico** (muitos cortes, dado animado na tela) sem depender de quem montar lembrar das regras.

## Fluxo (siga nesta ordem)
1. Copie do modelo para a pasta do vídeo: `template.html`, `fonts/`, `whoosh.wav` (e o que o `PEDIDO.md` mandar). Gere `voz.mp3`, `words.json` (whisper) e `narracao.txt`.
2. `python kits/saga-2d/embutir.py <pasta>` → põe as peças (`widgets.js`) dentro do `template.html` (pode repetir à vontade).
3. Escreva `gerar_edit.py` com `lib_edit.Video` (exemplo abaixo). Todo segundo vem de `v.at("palavra")` (fala real).
4. `python editor/checar_ritmo.py <pasta>` → só siga quando disser **APROVADO**.
5. `python editor/build_from_edit.py <pasta> --render` (o gate roda a checagem sozinho; reprovado = não renderiza).
6. Contact-sheet do mp4 (`ffmpeg … tile`), `DECISOES.md`, e `python editor/checar_ritmo.py <pasta> --final`.

## Regras de ritmo (a checagem cobra)
- Cortes por minuto ≥ 85% do modelo (≈ 15/min); cena média ≤ 4 s; **nenhuma cena acima de ~6 s** (o ideal é 2–4 s). Frase longa = 2 ou 3 cenas.
- **Cada cena tem pelo menos 1 elemento animado que mostra o dado** da frase (≥ 60% das cenas, e nenhuma totalmente parada).
- 1 selo/etiqueta por cena, whoosh suave (vol. 0,12) em ~metade dos cortes, **nunca** impact/pop. Música só baixinha (opcional).
- Roteiro aprovado = texto fixo (a checagem compara `narracao.txt` com o `PEDIDO.md`).

## Peças (`W.*`) — todas aceitam `x`, `y`, `t0` (início, segundo da fala), `t1` (fim do movimento)
| tipo | mostra | parâmetros principais |
|---|---|---|
| `contador` | número subindo | `de`, `ate`, `sufixo` (" H"), `prefixo`, `size`, `cor` |
| `garrafa` | recipiente enchendo + "N L" | `litros`, `w`, `h`, `cor` |
| `relogio` | relógio correndo + "N H" | `horas`, `r` |
| `bateria` | barra caindo/subindo + % | `de`, `ate` (0–100) |
| `sinal` | barras de sinal apagando + "SEM SINAL" | `barras`, `texto` |
| `calendario` | dias sendo riscados | `dias`, `colunas`, `titulo`, `cell` |
| `medidor` | ponteiro sobe | `de`, `ate` (0–1), `rotulo`, `corRotulo` |
| `grafico` | linha desenhando | `pontos` (alturas 0–1), `rotulo`, `eixo`, `cor` |
| `barra` | barra de progresso/nível + % | `de`, `ate`, `rotulo`, `cor`, `w` |
| `pulso` | anéis de alerta | `r`, `cor` |
| `carimbo` | carimbo que bate | `texto`, `bg`, `fg`, `giro` |
| `lista` | itens com ✓ no ritmo da fala | `itens`, `ts` (tempos), `titulo`, `passo` |
| `rafa` | personagem Rafa | `escala`, `pose`, `mood`, `flip` |
| `selo` | etiqueta de texto | `texto`, `bg`, `fg`, `size` |

Cores: `red`, `mus` (mostarda), `lead`, `moss`, `cream` ou `#hex`. Fundo da cena: `#hex`, `gDark`, `gMoss`, `gSky`, `gPale`, `gDusk`.
Texto de contador/bateria troca de cor sozinho (claro em fundo escuro). Passe `escuro=True/False` em `cena_w` para forçar.

## Exemplo de `gerar_edit.py`
```python
import sys; sys.path.insert(0, r"C:\...\ESTUDIO-VIDEOS\kits\saga-2d")
from lib_edit import Video
v = Video(__file__, nome="101 - 14-11-2026 - TITULO")
v.cena_w(0, "Estoque 72 h", fundo="#C99F76", selos=[dict(texto="ESTOQUE DE EMERGÊNCIA", x=540, y=330, t=0.2)],
         w=[dict(tipo="contador", x=540, y=900, de=0, ate=72, sufixo=" H", t0=v.at("72"), t1=v.at("horas", fim=True))])
v.cena_w(v.at("quatro"), "Água 4 L", fundo="#E0C49C", chao=1450, pan="dir",
         w=[dict(tipo="garrafa", x=330, y=1450, litros=4, t0=v.at("quatro"), t1=v.at("dia")), dict(tipo="rafa", x=760, y=1500, t0=0)])
v.finalizar(extra_palavras_chave=["72", "água"], vermelho=["apagam"], referencia={...}, pedido={...})
```
Cenas antigas do template (`SC.radio`, `SC.calendario17`…) continuam valendo: `v.cena("radio", v.at("o"), "Rádio", {...textos}, {...tempos})`.

## Peça nova
Se o assunto pedir uma peça que não existe (ex.: termômetro), **crie em `widgets.js`** (`W.nome = (id, cfg, e) => ({svg, html, anim})`, dê o nome em `_TIPOS_ANIM` do `editor/checar_ritmo.py` e registre aqui). Assim o próximo vídeo já nasce com ela.
