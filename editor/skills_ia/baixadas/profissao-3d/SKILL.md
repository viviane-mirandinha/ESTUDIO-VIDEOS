---
name: profissao-3d
description: Faz Reels/TikTok/Shorts verticais 3D "Você é [profissão]" no estilo @mundoremontado — animação low-poly de brinquedo feita 100% por código no Blender (Eevee headless, RTX 4090), bairro ao entardecer (céu azul-marinho→pêssego, casinhas laranja/rosa, árvores redondas, poste com fios e lampadinhas), personagem de capacete/uniforme, closes de objeto (luva, peça, ferramenta), "SIMULAÇÃO" com boneco cinza e corrente brilhando, "RAIO-X", câmera de cinema que muda a cada ~2 s, legenda 1 palavra por vez com keyword amarela, etiquetas-pílula, música ambiente com ducking e SFX discretos. A voz pode ser a guia Kokoro ou a gravada; trocar a voz refaz cortes, legenda e mix com 1 comando. Zero IA de imagem/vídeo. Use quando o usuário pedir "você é eletricista/bombeiro/piloto/...", "vídeo 3D de profissão", "como funciona o trabalho de X em 3D", "estilo mundoremontado", "profissão 3D", ou mandar um reel desse formato pra modelar.
---

# profissao-3d — "Você é [profissão]" em 3D low-poly por código

Primeiro vídeo (aprovado como base, 04/11/2026):
`kits\31-10\VIDEOS-PRONTOS\1-HISTORINHAS\05 - 31-10-2026 - PROFISSAO 3D - ELETRICISTA LINHA VIVA.mp4`
- Projeto completo dele (copiar como molde): `kits\31-10\_projetos\profissao-3d-eletricista\`
- Cópia do molde: `exemplos\eletricista\` (cena.py, dados.json, roteiro.txt, projeto.json)
- Ref modelada + ficha: `kits\REF-REELS\DfPtuv7N_sg\ESTILO.md`

## Regras fixas
- Tudo do vídeo no D:. Projeto: `kits\<DD-MM>\_projetos\profissao-3d-<slug>\`. Saída: `kits\<DD-MM>\VIDEOS-PRONTOS\1-HISTORINHAS\NN - DD-MM-AAAA - PROFISSAO 3D - TITULO.mp4`.
- **Proibido:** voz Edge (Antonio/Francisca), ComfyUI, Lovart, imagem/vídeo de IA, marca d'água. Só Blender + Pillow + ffmpeg + Kokoro/voz gravada.
- Roteiro aprovado pelo usuário antes. Voz final = do Yuri (ou a que ele mandar). Kokoro `pm_alex` é só **voz guia** (adulto, speed 1.15, SEM pitch).
- Imagens só em contact sheet (stills e conferência). Máx. ~8 por sessão.
- Caminho do projeto SEMPRE absoluto pro Blender (com `.` ele grava em `C:\stills`).
- Nunca `taskkill /IM blender.exe`; só o PID do próprio processo.
- Área segura IG (o compor.py já respeita): nada nos 220 px de cima, 380 de baixo, 120 da direita.

## Pipeline (roteiro → cenas → render → voz → legenda → mix)
Seja `S = %USERPROFILE%\.claude\skills\profissao-3d\scripts` e `P` = pasta do projeto (absoluta).
1. **Roteiro**: `P\roteiro.txt`, **1 frase por linha** (as âncoras usam linha:palavra, 0-based). Gancho forte na linha 0, CTA no fim.
2. **Voz guia** (opcional, se ainda não há voz gravada):
   `kits\FERRAMENTAS\KOKORO\venv\Scripts\python.exe -X utf8 S\voz_guia.py P` → `P\audio\voz_guia.wav`
3. **Cenas** (`P\cena.py`) — copiar o molde e trocar só os blocos:
   - CENÁRIO com os blocos do `prof_lib.py`: `street`, `house`, `tree`, `street_lamp`, `pole`/`wires` (3 fios + lampadinhas), `Pessoa` (capacete, uniforme, faixas refletivas, luvas; `mono=` vira manequim de SIMULAÇÃO), `Passarinho` (com `xray()`), `box/sph/cyl/cone/caps/ico/text3d`, `curve_obj` + `curve_reveal` (corrente andando), `windows()/lamps()` (apagar o bairro), `dusk()`.
   - PROPS da profissão (no cena.py): no eletricista, caminhão com braço de fibra (`set_basket`), isolador rachado/novo, capas, vara de manobra, luva de 2 camadas (estúdio longe, só céu atrás).
   - PLANOS como dados: `SHOT("L:k", cam0, cam1, alvo0, alvo1, fov0, fov1, dof=f-stop, fx=função)`. O plano começa 0,05 s antes da palavra k da linha L e a câmera desliza suave de cam0→cam1. `fx(t, lt, u)` anima o resto (u = 0..1 no plano; `ramp(t, T("L:k"), dur)` pra eventos na palavra). Cortes a cada ~1,5-3 s, com variação de close, contra-plongée, vista de cima e travelling.
   - `reset(t)` zera o estado a cada quadro (o render é paralelo, então cada quadro precisa ser independente).
4. **Etiquetas/legenda/SFX** (`P\dados.json`): `amarelas` (keywords da legenda), `etiquetas` (pílula, `de`/`ate` = âncoras ou "fim", `grande` p/ CTA), `selos` (SIMULAÇÃO vermelho, RAIO-X azul, CAMADAS verde), `checks` (check verde x,y), `tintas` (`raiox`), `musica`, `sfx` = `["kit:categoria/nome" | "synth:zumbido|faisca|passarinho", "L:k", desloc_s, pico_dB, dur_s]`.
5. **Conferir antes do render longo**: `blender -b --factory-startup --python P\cena.py -- P list` (planos/duração) e `... -- P stills` (1 quadro por plano a 50%, ~20 s). Montar UMA folha 8x5 dos stills (PIL) e olhar só ela. Corrigir câmera atravessando objeto, personagem de costas, texto cortado.
6. **Tudo de uma vez / trocar a voz**:
   `python -X utf8 S\refazer.py P --voz "D:\Audios\31-10\01.wav" --saida "D:\...\NN - ... .mp4"`
   → converte a voz, realinha (faster-whisper large-v3 CPU int8, áudio como numpy, SEM initial_prompt), apaga os frames se os cortes mudaram, renderiza em 3 processos (~3,5 q/s na 4090, 48 samples), mixa e compõe. Rodar em segundo plano (~15 min p/ 85 s). `--pular-render` = só refaz mix + legenda + etiquetas (mudou só o dados.json).
7. **Conferência**: olhar `P\conferencia.jpg` (12 quadros). Nunca quadros soltos.

## Scripts (`scripts\`)
- `prof_lib.py` — motor Blender (Eevee, AgX Medium High Contrast, céu degradê crepúsculo, sol baixo quente + fill azul, bevel em tudo, âncoras, `SHOT`, `run`).
- `voz_guia.py` — Kokoro pm_alex frase a frase (cortes em silêncio real, pausas 0,20/0,15 s).
- `alinhar.py` — palavras do roteiro ↔ tempos da voz (`palavras.json`), casa número ("13" x "treze").
- `mix.py` — voz pico -3; música = RMS da voz - 22 dB, ducking -5 dB na fala (≥ 18 dB abaixo sempre); SFX do SFX Kit ou sintetizados; -14 LUFS.
- `compor.py` — bloom + vinheta, tinta raio-X, selos, etiquetas, check, legenda (Montserrat ExtraBold 124 px, encolhe se não couber, y = 70%), H.264 crf 18 + AAC 256k, folha de conferência.
- `refazer.py` — orquestra tudo; `anc.py` — âncoras "L:k" compartilhadas.

## Trocar de profissão (receita)
1. Pegar ref (se houver): contact sheets + ESTILO.md da ref. Roteiro 2ª pessoa: gancho com número/perigo → "Você é X" → o problema → por que o jeito fácil não serve → equipamento em camadas (close + etiqueta) → SIMULAÇÃO do erro (manequim + brilho) → curiosidade visual (RAIO-X) → execução passo a passo → payoff "ninguém percebeu" → CTA "comenta PROFISSÃO".
2. Copiar `exemplos\eletricista\` pra pasta nova; trocar `roteiro.txt`; no `cena.py` manter o bairro e trocar os PROPS + a lista de `SHOT`. Ex.: bombeiro → caminhão vermelho com escada (mesmo `set_basket`), mangueira (`curve_obj`), fumaça (`ico` cinza com alpha); piloto → pista + avião de caixas; mergulhador → piso azul + `tintas`.
3. `dados.json`: novas etiquetas/keywords/SFX. Stills → folha → corrigir → `refazer.py`.

## Padrão visual v2 (04/11, ajuste fino vs ref — já é o padrão do prof_lib/compor)
- **Céu**: azul-marinho domina a metade de cima (`SKY` v2: #141C40/#24305E no alto, pêssego só nos 5-13% perto do horizonte). Sol 4,6 quente #FFAE70, fill fraco 0,38 → lados na sombra escuros e quentes (antes era tudo lilás lavado).
- **Fios** `WIRE_R = 0.045` (grossos) + lampadinhas hexagonais grandes (0,2 × 0,13) emissão 3,2. Passarinho pousa em `wz(x) + WIRE_R`.
- **Pessoa**: capacete de obra = meia-esfera (`M_HEMI`) EM CIMA da testa + aba + bico na frente + friso + adesivo amarelo (olhos livres; a esfera inteira virava "touca" cobrindo o rosto). Faixa refletiva também nas mangas, cinto com fivela, luva com cano + polegar (mão = caixa arredondada, não bola).
- **Passarinho** v2: corpo-ovo inclinado, cabeça grande, asas e cauda em leque escuras, barriga/peito laranja, brilho no olho, pernas CURTAS. Câmera de close a ~0,8-1,1 m de perfil (lado -Y), FOV 27-28: mais perto que isso vira "bola marrom".
- **Luva**: `mao(n, c, mat, parent, s_, cuff_h, grow=)` — palma reta, 4 dedos finos (2 falanges, r 0,046) separados, polegar aberto, cano longo com borda. Camada de cima (couro) = mesma escala + `grow=0.014` (escala uniforme deixa a borracha vazar nas juntas). Fundo `grade(...)` azul-marinho com grade atrás (estúdio da ref), não o céu.
- **Cesto**: amarelo-mostarda com aro de cima grosso + 1 placa preta larga embaixo e 1 pequena no canto (2 quadradinhos + 1 traço = parece um ROSTO, evitar).
- **Etiqueta** (compor.py): retângulo escuro de canto pouco arredondado (r 16) + barra amarela na esquerda + contorno amarelo fino, igual à ref. **RAIO-X**: tinta fria suave (0,78 original); quem brilha é a perna do passarinho (emissão ~0,9, o bloom faz o resto) — tinta forte + emissão alta = tela branca.
- Isolador rachado: câmera a ~1,5 m pra ver a pilha inteira com a trinca.
- Mantido de propósito (melhor que a ref): legenda grande Montserrat 124 px, gancho com número, CTA "comenta PROFISSÃO".

## Lições (04/11)
- Whisper large-v3 com o roteiro como `initial_prompt` PULOU os 5 s iniciais (Cartesia): sem prompt deu 262/262.
- Cor hex de 3 dígitos quebra `hexc` — sempre 6 dígitos.
- Olhos da `Pessoa` precisam ficar para fora da esfera (y -0,122), senão parece de costas.
- Emissão alta + AgX vira branco estourado (raio-X): emissão 1,5-2,5 e cor saturada; o brilho vem do bloom do compor.py.
- Manequim com braços em T no cesto: virar yaw 90 pro eixo dos braços ficar no Y (fios correm no X).

## MODO TEXTO (ref sem fala, só música + texto) — 05/11, vídeo "08 - E SE MEU DEDO DOBRASSE DE VELOCIDADE"
Projeto molde: `kits\31-10\_projetos\dedo-dobro\` (ref DfTWA9fh7oz: "E se X dobrasse a cada vez", escalada exponencial).
1. `roteiro.txt` = 1 cartão de texto por linha (linha 0 = gancho, última = CTA "QUER APRENDER... COMENTA PALAVRA").
2. `python -I -X utf8 S\tempos_texto.py P` → palavras.json sem voz (0,7 s + 0,05 s/caractere, 1,6-2,8 s; gancho ≥2,8; CTA 4 s). Âncoras "L:k" iguais.
3. `cena.py` normal (prof_lib). Extras do molde: boneco de BLOCOS (`Bloco`, IK de braço `reach`), `phone_cam` (câmera alinhada
   com a tela), tela do celular e paredão de telas compostos com numpy a cada quadro a partir de `P\vid\vNN\*.jpg` = NOSSOS vídeos
   prontos (3 s, 15 fps, 360x640; nunca "(VOZ GUIA)"). Quarto (y=-200), rua (origem), espaço (y=3000, Terra r=80, estrelas, anéis).
4. Render: `P\render.sh` (3 processos, pula quadros prontos). Depois `S\mix_texto.py P` (música RMS -20, SFX do kit com pico em dBFS, -14 LUFS)
   e `S\compor_texto.py P SAIDA.mp4` (HUD contador exponencial com rótulos por limite, cartão serifado itálico, gancho com caixas vermelhas, CTA amarelo).
- Lição: câmera "entre o olho e o celular" pega mão/braço gigante desfocado na frente → usar `phone_cam` (na normal da tela, 0,2-0,4 m).
- Lição: anel do estrondo crescendo até 22 m sai do quadro; 9 m fica certo a ~16 m de distância.
