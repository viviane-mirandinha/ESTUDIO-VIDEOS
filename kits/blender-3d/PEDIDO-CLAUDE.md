# Pedido ao Claude — cena 3D do kit Blender (modo Claude do painel)

Você está no ESTUDIO-VIDEOS. Siga o CLAUDE.md da pasta e leia `kits/blender-3d/README.md` ANTES de começar.

## Tarefa
{tarefa}

## Pasta do vídeo
`{pasta}` — dentro dela:
- `pedido.json` (tema, predefinição de visual), `roteiro.txt` (a fala), `voz.*` e `words.json` (tempo de cada palavra: `[{{"w","s","e"}}]`);
- `plano.json`: rascunho do plano de cenas já feito pelo modo grátis (pode estar errado: melhore à vontade).
{extra}

## O que entregar
1. **`plano.json`** — as cenas do vídeo (`de`/`ate` em segundos, `texto`, `cenario`, `pose`, `expressao`, `objeto`, `enquadramento`, `lado`, e opcionalmente `personagem`, `render`, `modelos`).
   As cenas devem cobrir TODA a fala, coladas (sem buraco), no ritmo do `words.json`. Use só os valores aceitos (README, seção "Modo por cenas").
2. Se as peças prontas NÃO bastam para o assunto (objeto, cenário ou gesto que não existe), então:
   - crie a peça nova em `kits/blender-3d/lib/` (e exporte em `lib/index.ts`), seguindo o estilo das peças existentes (três.js / React Three Fiber, cada forma que muda = um `<mesh>` próprio, cores `#rrggbb`);
   - escreva **`{pasta}/cena3d.tsx` à mão** (SEM a linha "GERADO DO PLANO"), a partir de `kits/blender-3d/exemplos/vitrine/cena3d.tsx`: exporta `DURACAO` e `quadro3D(s)`; use `falaEm`-style para a boca (`fala` do Personagem) com o `words.json`;
   - os tempos das cenas do `plano.json` devem bater com os da `cena3d.tsx` (o painel usa o plano para mostrar um quadro de teste por cena).
   Se as peças prontas bastam, NÃO escreva `cena3d.tsx`: o painel gera a partir do plano.
3. **Valide**: rode `python kits/blender-3d/construir.py "{pasta}" --so-assar` (use o Python do `.venv`). Precisa terminar sem erro. Corrija até passar.

## Regras
- NÃO renderize no Blender e NÃO rode `--previa-cenas`/`--render`: o painel faz isso depois.
- Só mexa em `{pasta}` e em `kits/blender-3d/lib/`. Nada de apagar arquivos, nada de `git`.
- Zero fato inventado; só o que o roteiro diz. Sem logo, nome ou marca de terceiros.
- Termine com um resumo curto, em português simples, do que você fez e do que o usuário deve conferir.
