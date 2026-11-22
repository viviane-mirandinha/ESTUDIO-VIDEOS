# Kit Blender 3D — vídeo com personagem e objetos em 3D, acabamento de cinema

Terceira opção do Estúdio (ao lado da **fábrica** e da **animação 2D**). O vídeo é **programado** como uma cena 3D
(personagem de vinil, carro, galão, cenários…). O **Blender** renderiza cada quadro com luz suave, reflexos e sombras de
verdade. Depois o Estúdio junta **voz + legenda** (HyperFrames) e o vídeo aparece no editor como qualquer outro.

> Este kit é **independente**: tudo que ele precisa está nesta pasta (`kits/blender-3d/`). Não usa nenhuma outra pasta do PC.
> Base do pipeline: kit cotidiano.explicado (mesmo autor do Estúdio).

## O que precisa
- **Node.js** (já instalado pelo setup do Estúdio). As peças do kit (`three`, `react`…) instalam sozinhas na 1ª vez (`npm install` dentro desta pasta).
- **Blender 4.2+** na máquina que vai renderizar (aqui: 5.3). Grátis em blender.org.
- **Máquina de render com placa NVIDIA** (recomendado). Este PC não tem placa de vídeo boa: renderizar aqui leva horas.

## Fluxo (o que o Claude faz)
1. Pasta do vídeo: `VIDEOS/NN-nome/` com `voz.mp3` (ou `voz.wav`) e o roteiro.
2. `python kits/blender-3d/construir.py VIDEOS/NN-nome --preparar` → gera `words.json` (tempo de cada palavra).
3. Escrever `VIDEOS/NN-nome/cena3d.tsx` **no tempo da fala** (copie `exemplos/vitrine/cena3d.tsx`). Exporta:
   - `DURACAO` (segundos, ≥ duração da voz);
   - `quadro3D(s)` → `{camera, fundo, luz, cena}`: o 3D no segundo `s` (função pura: nada de estado nem `Math.random()`).
4. `python kits/blender-3d/construir.py VIDEOS/NN-nome --teste` → renderiza 3 quadros (~10 s). **Olhe `blender/teste.jpg`**: peças no lugar, nada faltando, boca/expressão certas.
5. `python kits/blender-3d/construir.py VIDEOS/NN-nome --render` → assa, renderiza todos os quadros na máquina potente, monta `blender.mp4`, cria `edit.json` (voz + legenda) e renderiza o final.
   - Render de ~1 min de vídeo ≈ 25 min na máquina com RTX 5070 Ti (medido: ~0,75 s por quadro). Rode em segundo plano.
6. Conferir o mp4 final com contact-sheet (regra de qualidade do CLAUDE.md) e entregar o caminho completo.

Opções: `--local` (renderiza neste PC, lentíssimo), `--so-assar`, `--sem-assar` (reusa `blender/cena.glb`), `--manter-quadros`.

## Modo por cenas (sem escrever código 3D) — `plano.json`
Em vez de escrever o `cena3d.tsx`, descreva o vídeo em **cenas** num `plano.json` (modelo: `exemplos/plano-exemplo.json`). Cada cena tem `de`/`ate` (segundos),
`texto` e as escolhas abaixo (o que faltar usa o padrão):

| campo | valores |
|---|---|
| `cenario` | `garagem`, `atelie`, `infinito` |
| `pose` | `parado`, `pensando`, `apontando`, `comemorando`, `andando` |
| `expressao` | `feliz`, `orgulhoso`, `triste`, `surpreso`, `cansado`, `bravo`, `pensativo`, `animado` |
| `objeto` | `nenhum`, `carro`, `galao`, `gato` |
| `enquadramento` | `geral`, `medio`, `close`, `lado`, `alto` |
| `lado` | `esq`, `centro`, `dir` (onde o personagem fica) |

- `construir.py <pasta>` gera o `cena3d.tsx` sozinho a partir do plano (`gerar_cena.py`); a boca do personagem mexe no ritmo da fala (`words.json`).
- **Um quadro de teste de cada cena:** `construir.py <pasta> --previa-cenas` → `previa/cena-NN.jpg` + `previa/previas.json`. Serve para revisar cena a cena antes do render completo.
- Um `cena3d.tsx` escrito à mão nunca é sobrescrito pelo gerador (o gerador só mexe em arquivos com a marca "GERADO DO PLANO").
- Limite: o céu do ateliê sai de cor lisa no Blender (sem degradê).

## Peças disponíveis (`lib/`, importe de `@estudio3d`)
`Personagem` (estilos massinha/vinil/desenho; poses e expressões em `gestos.ts`), `Gato`, `CarroDetalhado`, `Galao`, `Vasilha`, `Fogo`,
`Fumaca`, `JatoLiquido`, `Bicicleta`, `Volante`, cenários `Garagem`/`Atelie`/`Infinito`, câmera (`cameraEm` com planos) e tempo
(`desde`, `suave`, `mistura`…). **Peça nova que criar → acrescente em `lib/` e exporte em `lib/index.ts`.**

## Regras de ouro
- **Cada forma que muda (boca, expressão) = um `<mesh>` próprio**; senão aparece torta no Blender.
- Cor sempre em hexadecimal (`color="#rrggbb"`).
- Vídeo **vertical 1080x1920, 30 fps** (a câmera da cena é pensada assim). Para outro tamanho, mude `quadros.largura/altura` em `config.json` e reajuste o enquadramento.
- A cena **não carrega legenda nem etiquetas**: legenda vem do Estúdio (`edit.json`). Selos/etiquetas presas às peças ainda não existem neste kit.
- Sem fato inventado e sem material de terceiros (regras do CLAUDE.md do Estúdio continuam valendo).

## Máquina de render (configuração em `config.json`)
`modo`: `"remoto"` (padrão) ou `"local"`. Em `remoto`, o kit manda `cena.glb` + `quadros.json` por **SSH**, o Blender renderiza lá e os
quadros (JPG 95%) voltam compactados num `.tar`. Precisa: SSH ligado na máquina, **chave sem senha** em `remoto.chave`, Blender no
caminho `remoto.blender`. A pasta de trabalho lá é `remoto.pasta` (cada vídeo cria uma subpasta e apaga no fim).

Configurar uma máquina nova (uma vez):
1. Na máquina de render: instale o Blender, ligue o servidor SSH (Windows: Configurações → Sistema → Recursos opcionais → *OpenSSH Server*) e deixe-a sempre acordada.
2. Neste PC: `ssh-keygen -t ed25519 -N "" -f ~/.ssh/id_ed25519_render`.
3. Na máquina de render, como administrador, cole a chave **pública** (`~/.ssh/id_ed25519_render.pub`) em `C:\ProgramData\ssh\administrators_authorized_keys` (usuário comum: `~\.ssh\authorized_keys`).
4. Ajuste `host`, `usuario`, `chave`, `blender` e `pasta` em `config.json`. Teste: `ssh -i ~/.ssh/id_ed25519_render usuario@host echo ok`.
Se a máquina estiver fora da rede de casa, use Tailscale (o IP 100.x entra em `host`).

## Pastas
`bake/` (cena → .glb), `render/renderizar.py` (roda dentro do Blender), `render_quadros.py` (local ou SSH),
`construir.py` (orquestra tudo), `lib/` (peças 3D), `exemplos/` (cena de exemplo; vídeo pronto: `VIDEOS/105-exemplo-blender-3d`).
