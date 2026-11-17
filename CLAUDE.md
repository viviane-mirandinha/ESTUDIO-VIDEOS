# ESTÚDIO DE VÍDEOS — instruções para o Claude Code

Você está dentro de um pacote que faz vídeos para canais "dark" (sem rosto) com ferramentas grátis e locais.
Fale sempre em **português simples** com o usuário. Ele pode não ser programador: faça as coisas por ele,
explique em 1-2 frases o que fez e mostre sempre o **caminho completo** do vídeo pronto no fim.

> **Se a pasta `.venv/` não existe, o pacote ainda não foi instalado.** Seja qual for a primeira mensagem da pessoa
> ("oi", "instala tudo isso", "o que é isso?"), comece pelo **INSTALADOR GUIADO** (seção abaixo).

## O que tem aqui
| Pasta/arquivo | O que é |
|---|---|
| `INSTALAR.bat` | Instalador de 1 clique do Windows (roda o setup.ps1, grava INSTALACAO.log, cria o atalho na área de trabalho). |
| `setup.ps1` / `setup.sh` | Instalador (Windows / Mac, Linux ou nuvem). |
| `iniciar.bat` / `iniciar.sh` | Abre o editor no navegador: http://localhost:8780 |
| `editor/` | Editor local (FastAPI + página web). `server.py`, `build_from_edit.py` (monta e renderiza), `FORMATO.md` (formato do `edit.json`). |
| `editor/fabrica/` | **Modo fábrica**: vídeo completo sem gastar token (Ollama escreve, edge-tts fala, whisper sincroniza, HyperFrames renderiza). |
| `editor/fabrica/estilos/` | Estilos prontos da fábrica: `historia-simples`, `psicologia-sombria`, `reddit-story`. |
| `VIDEOS/` | **Todos os vídeos novos ficam aqui** (um por pasta `NN-nome/`, com `edit.json`). Já vem com exemplos 01-19. |
| `VIDEOS-NOVOS/` | 31 estilos testados (longos) + vídeo 32 em espanhol. Os que têm mp4 servem de exemplo; os "só projeto" têm template/edit.json para renderizar de novo. |
| `VIDEOS-SHORTS/` | Estilos de Shorts/Reels 9:16 (`_kit` e `_template-palco3d` são modelos de código). |
| `ESTILOS-NOVOS/`, `ESTILOS-SHORTS/` | Fichas dos estilos (`ESTILO.md` + `REFERENCIA.txt` com links). `RESUMO.md` ranqueia. |
| `ROTEIROS*/` | Roteiros prontos (texto) dos estilos. |
| `METODO-COPIAR-ESTILO.md` | Passo a passo para copiar o estilo de um vídeo de referência. |
| `VIDEOAULAS/` | 28 videoaulas (00 a 26) de como usar o Estúdio. Indique a aula certa quando a pessoa tiver dúvida (`LISTA-AULAS.md`). |
| `checar_pc.ps1` / `checar_pc.sh` | Checagem do PC (só leitura) usada pelo instalador guiado. |
| `kits/clay-retencao/` | Kit 3D "massinha" (Three.js) vertical. |
| `kits/saga-2d/` | Kit do estilo Saga sobrevivência 2D: peças animadas prontas (`widgets.js`), `lib_edit.py`, `embutir.py`. Ver `README.md`. |
| `kits/animacao-2d/` | **Modelo base de animação 2D com personagem** (recorte em código: andar, perfil, costas, close, cenários em camadas). Rode SEMPRE `python kits/animacao-2d/construir.py <pasta> [--render]` — ele checa movimento e variedade antes de renderizar. Leia o `README.md` (regras de ouro). Exemplo: `VIDEOS/100-teste-marco-aurelio-estoicismo`. |
| `editor/fabrica/estilos/animacao-filosofica/` | Estilo da fábrica (aparece em Estilos prontos): qualquer narração vira animação 2D com personagem (usa `kits/animacao-2d/planejador.py` + `cenas_base.js`; 16:9 ou 9:16; roda as guardas de movimento/variedade antes do render). Exemplo: `VIDEOS/102-exemplo-animacao-filosofica`. |
| `editor/checar_ritmo.py` | Guarda de qualidade: confere ritmo, animação, roteiro fiel e som antes de entregar. |
| `recursos/` | Fontes Google (OFL), whoosh próprio, mapa-múndi Natural Earth (domínio público). |
| `estoque/gameplay/` | Coloque aqui vídeos de gameplay **livres** (.mp4) para o estilo `reddit-story`. |
| `.venv/` | Python do pacote (criado pelo setup). Use SEMPRE `.venv` para rodar os scripts. |

Python do pacote: Windows `.venv\Scripts\python.exe` · Mac e Linux `.venv/bin/python`.
Antes de rodar Python: `PYTHONIOENCODING=utf-8` e `PYTHONUTF8=1`.

## Pedidos comuns e o que fazer

### PRIMEIRA CONVERSA / "instala tudo isso" / "instala" / "configura"  ← INSTALADOR GUIADO
Se ainda não existe `.venv/` nesta pasta, a pessoa acabou de receber o pacote. Conduza assim, **um passo por vez,
esperando a resposta dela antes de seguir**:

1. **Apresente o pacote** em 4-6 linhas simples (o que ele faz, o que vem dentro — use a tabela acima, sem jargão).
2. **Peça permissão para checar o PC**: "Posso dar uma olhada no seu computador (placa de vídeo, memória, espaço em disco,
   programas instalados) para ver se ele roda tudo? Não instalo nem mudo nada nessa etapa." Espere o "sim".
3. **Rode a checagem** (só leitura): Windows `powershell -ExecutionPolicy Bypass -File checar_pc.ps1` ·
   Mac e Linux `bash checar_pc.sh`. Leia a linha `VEREDITO=` e as listas "IMPEDE"/"LIMITAÇÕES".
4. **Reporte em um dos caminhos** (mostre a tabela da checagem resumida):
   - `COMPLETO` → "Seu PC é compatível com tudo. Posso continuar a instalação? Vai baixar uns 8-10 GB e levar de 15 min a 1 h."
   - `PARCIAL` → "Seu PC não roda tudo, mas dá para instalar e testar. O que fica limitado: <lista em palavras simples>.
     Quer seguir mesmo assim?" (ex.: sem NVIDIA = Whisper na CPU e roteiro mais lento; modelo de roteiro menor `llama3.2:3b`;
     clone de voz não roda — a voz grátis edge-tts funciona normal.)
   - `INCOMPATIVEL` → explique o motivo ("IMPEDE") e o que resolveria (liberar disco, mover a pasta, outra máquina/nuvem).
     Só siga se a pessoa insistir, avisando que pode não funcionar.
5. **Instale passo a passo** depois do "sim": Windows `powershell -ExecutionPolicy Bypass -File setup.ps1` (ou peça à pessoa 2 cliques no `INSTALAR.bat`; se der erro, leia o `INSTALACAO.log`) ·
   Mac, Linux e nuvem `bash setup.sh` (no Mac usa Homebrew e pede a senha do Mac uma vez). Rode em segundo plano e vá contando em 1 linha cada etapa (`==> 1/7` … `7/7`).
   Avise antes: o Windows pode perguntar "Permitir alterações?" ao instalar Python/Node/ffmpeg/Ollama — é para clicar Sim.
6. **Corrija até funcionar**: se der erro, leia só as últimas linhas, explique em 1 frase, corrija e rode o setup de novo
   (ele pula o que já instalou). Casos comuns: winget ausente → pedir para instalar "App Installer" na Microsoft Store;
   Ollama sem responder → abrir o app Ollama e repetir `ollama pull`; caminho com acento/OneDrive → mover a pasta.
7. **Teste de saúde**: o setup termina rodando `teste_saude.py` (vídeo de ~10 s) e grava `RELATORIO-INSTALACAO.txt`
   com ✅/❌ de cada parte. Leia esse arquivo, mostre o resumo e corrija cada ❌ (rodar de novo: `python teste_saude.py`
   com o Python do `.venv`). Mostre o caminho do vídeo de teste. Abra o editor
   (`iniciar.bat` / `bash iniciar.sh`) e diga o endereço http://localhost:8780.
8. **Feche com o resumo**: o que ficou instalado, o que ficou limitado no PC dela, e 3 exemplos do que ela pode pedir.

Máquina na nuvem: editor com `ESTUDIO_HOST=0.0.0.0 bash iniciar.sh` + liberar/encaminhar a porta 8780
(ou túnel SSH `ssh -L 8780:localhost:8780 ...`). Nunca exponha para a internet sem a pessoa pedir.

### "faz um vídeo no estilo X sobre Y"
- **X é um estilo da fábrica** (`historia-simples`, `psicologia-sombria`, `reddit-story`) → zero token:
  ```
  cd editor/fabrica
  ../../.venv/bin/python fabrica.py --estilo historia-simples --tema "Y" --canal "NOME DO CANAL" --duracao 60
  ```
  (Windows: `..\..\.venv\Scripts\python.exe fabrica.py ...`). Opções: `--roteiro arquivo.txt` (texto pronto),
  `--voz voz.mp3`, `--tts edge`, `--voz-nome pt-BR-FranciscaNeural`, `--modelo qwen2.5:7b`, `--musica fundo.mp3`,
  `--pasta <pasta>` (retomar depois de erro). Também dá pelo editor: botão **➕ Pedir vídeo**.
- **X é um dos 13 estilos de teste ou do catálogo** → precisa de você (Claude): siga `METODO-COPIAR-ESTILO.md`,
  usando a pasta do estilo em `VIDEOS/NN-*` (ou a ficha `ESTILOS-NOVOS/NN-*/ESTILO.md`) como modelo.
- Roteiro: peça ao Ollama (zero token, padrão da fábrica) ou escreva você se o usuário quiser qualidade máxima.
- Sempre termine com o vídeo em `VIDEOS/NN-.../NN - DD-MM-AAAA - CANAL - TITULO.mp4` (≤200 caracteres) e um `edit.json`
  na pasta, para ele aparecer no editor.

### "copia o estilo deste vídeo <link>"
Siga `METODO-COPIAR-ESTILO.md`: baixar SÓ um trecho (90 s) da referência em `ref/`, 1 contact-sheet,
`BREAKDOWN.md`, `template.html`/`edit.json`, vídeo de teste de ~1 min, conferir, e se o usuário aprovar
registrar como estilo novo da fábrica (`editor/fabrica/estilos/<nome>/`). Apagar `ref/` no fim.

### "abre o editor" / "não aparece no editor"
`iniciar.bat` ou `bash iniciar.sh`. O editor lista toda pasta de `VIDEOS/` e `kits/` que tenha `edit.json`.

## Regras de qualidade (obrigatórias)
- **Ritmo e animação (checagem automática).** Vídeo que vem de um `PEDIDO.md` com modelo não pode ficar mais lento nem mais "seco" que o modelo:
  mesmos cortes por minuto (cena média ≤ ~4 s, nenhuma > ~6 s), nenhuma cena parada e **pelo menos 1 elemento animado do dado em cada cena**
  (contador, nível, ponteiro, risco, linha desenhando…). Rode `python editor/checar_ritmo.py <pasta>` (com o `.venv`) até dar **APROVADO** — o
  `build_from_edit.py --render` recusa a 1ª versão reprovada. Estilo Saga 2D: use o kit pronto `kits/saga-2d/` (leia o `README.md` dele: peças
  animadas `widgets.js`, `embutir.py`, `lib_edit.py`) em vez de desenhar SVG novo. Peça nova que criar → acrescente ao kit para os próximos vídeos.
- **Voz pedida indisponível** (ex.: Fish sem crédito): não esconda — registre em `DECISOES.md` e avise o usuário no fim, dizendo como trocar depois.
- **Zero fato inventado.** Datas, números, nomes: só o que for verdade. Roteiro do Ollama erra — revise fatos antes de entregar
  e avise o usuário para ler o `roteiro.txt` antes de publicar. Pessoa real em escândalo: só o que é público e comprovado.
- **Roteiro**: 100% no idioma do canal, gancho nos primeiros 3-5 s, sem repetir ideias (sem "loop"), CTA de like espalhado
  (início, ~meio e fim), sem enrolação.
- **Imagem tem que fazer sentido** com o que está sendo falado naquele momento. Mostre o que a narração diz.
- **SFX**: proibido "impact" e "pop" (efeito tuk-tuk). Só whoosh suave ou nada. Música opcional, baixinha.
- **Sem material de terceiros no vídeo**: nada de logo/nome/intro do canal copiado; fotos só domínio público/CC
  (Wikimedia, créditos em `img/creditos.json`) ou banco livre (Pexels/Pixabay); gameplay só livre.
- **Conferir antes de entregar**: 1 contact-sheet do mp4 final
  (`ffmpeg -i video.mp4 -vf "fps=1/5,scale=320:-1,tile=4x3" -frames:v 1 sheet.jpg`) + blackdetect. Olhe a imagem.

## Economia de tokens
- Imagens só em contact-sheet (nunca frame a frame). No máximo ~5 imagens por vídeo.
- Saída de comando curta (`| head -50`, `| Select-Object -First 50`). Não releia arquivos.
- Tarefas longas (setup, render, whisper) em segundo plano.

## Recursos opcionais (só instale se a pessoa pedir — avise antes)
| Recurso | Precisa | Como |
|---|---|---|
| **Clone de voz Qwen3-TTS** (aba 🎙 Minhas vozes) | NVIDIA 8 GB+ de VRAM, ~10 GB de disco | Criar venv em `C:\AI\qwen3-tts` (ou `QWEN3_TTS_DIR`), `pip install qwen-tts` + PyTorch CUDA; modelos Apache-2.0 baixam sozinhos do HuggingFace (~4 GB cada). |
| **Chatterbox** (voz expressiva) | NVIDIA 8 GB+, ~4 GB | Servidor local na porta 8020 (`CHATTERBOX_URL`); modelo ResembleAI (MIT). |
| **VoiceStudio / OmniVoice** (app de dublagem) | NVIDIA, ~10 GB | Programa de terceiros (AGPL-3.0): instalar pelo GitHub oficial `debpalash/VoiceStudio`. O painel só lê as vozes dele. |
| **Revisão de roteiro com o Claude** | chave própria da Anthropic (paga por uso) | Colar a chave em ⚙ Ajustes do painel. Nunca escreva chaves em arquivos do pacote. |
| **Bancos Pexels / Pixabay** | chave grátis de cada site | Colar em ⚙ Ajustes. |
Aviso padrão: "Isso precisa de placa NVIDIA com 8 GB ou mais e baixa vários GB. Sem isso a voz grátis (edge-tts) continua funcionando. Quer instalar?"
Voz clonada: só da própria pessoa ou com autorização de quem é a voz.

## Técnico
- Render: `python editor/build_from_edit.py <pasta> --render` → usa `node_modules/.bin/hyperframes` (HyperFrames 0.7.111,
  Apache-2.0, instalado pelo `npm install` na raiz). Gera `final.mp4`, `leve.mp4`, `thumb.jpg`.
- Whisper: `editor/fabrica/lib/whisper_run.py` (faster-whisper; GPU NVIDIA com `large-v3`, senão CPU `small`).
- Voz: `edge-tts` (grátis, precisa de internet). Opcional local: Chatterbox (`CHATTERBOX_URL`) ou Qwen3-TTS (`QWEN3_TTS_DIR`).
- Roteiro local: Ollama (`ESTUDIO_OLLAMA_MODELO`, padrão `qwen2.5:7b`; melhor em PT e mais pesado: `mistral-small3.1`).
- Editor: porta 8780 (`ESTUDIO_PORTA`), host `ESTUDIO_HOST` (padrão 127.0.0.1).
- Licenças: ver `LICENCAS.md`.
