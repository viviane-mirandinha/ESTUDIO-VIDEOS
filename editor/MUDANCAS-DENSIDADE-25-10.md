# Mudança do pacote — 🧮 Guarda de densidade de gráficos (25/10/2026)

Clean-room (nada do Auto B-Roll Studio). **O `server.py` e o `build_from_edit.py` mudaram → reinicie o painel (8780).**

## O que é
Não deixa o vídeo virar poluição de animação. Mede quanto da tela é **gráfico decorativo** e, quando as
**"Suas regras"** do vídeo pedem, **derruba o excesso** — mantendo o gancho (1º gráfico), os números/
palavras-chave e respeitando o intervalo pedido. **Legenda (a fala) e a mídia de base (foto/vídeo) nunca
são tocadas.** Tudo reversível (esconde com `hidden`, não apaga; guarda `edit.json.bak-densidade`).

Classificação: legenda = `caption`; gráfico decorativo = `text`/`html`/`bloco`; mídia = `image`/`video`/`scene`.
(% de rosto não é medido aqui — não dá pra ver pelo edit.json.)

## Regras (`edit["regras"]`)
Pode ser dict `{max_pct, intervalo_min, respiro, sem_animacao, strict}` e/ou lista de frases (chips).
Frases reconhecidas: "sem animações", "máx 1 animação a cada N s", "no máximo X% de gráfico".
**Sem regras → não mexe em nada** (só mede). Padrões quando ligado: 25% / 1 a cada 7 s / respiro 1,5 s.

## Arquivos
- **Criado** `guarda_densidade.py` — `medir(edit)`, `aplicar(edit)`, `filtrar_para_render(edit)`, `aplicar_em_disco(proj)` + CLI (`python guarda_densidade.py <pasta> [--aplicar] [--json]`).
- **Alterado** `build_from_edit.py` — se o `edit.json` tiver `regras`, o render esconde o excesso **em memória** (não grava no projeto).
- **Alterado** `server.py` — importa `guarda_densidade as DENS`; `GET /api/densidade/{pid}` (mede) e `POST /api/densidade/{pid}/aplicar` (derruba no edit.json, reversível).

## Testado (25/10)
- Sintético (10 gráficos colados a cada 2 s, regra "1 a cada 7 s", um com "R$ 500"): 33,3% → 10%, manteve g0 (gancho), g4 (número) e g8; legenda e vídeo de fundo intactos.
- Endpoint `/api/densidade` no 8780 (01-mapas: mede 87,4%, sem regras → não mexe).

## UI (feito — 25/10, app.js já liberado)
- **Alterado** `static/index.html`: botão **🧮 Densidade** no header do editor.
- **Alterado** `static/app.js`: diálogo "Densidade de gráficos" — chips **B-roll primeiro** / **Sem animações**,
  campos "máx. 1 gráfico a cada N s" e "máx. X% da tela", **📊 Medir agora** (lê `/api/densidade`),
  **💾 Salvar regras** (grava `edit["regras"]`, vale no próximo render) e **🔧 Aplicar agora** (esconde o
  excesso já, reversível, recarrega o editor). Verificado no 8780: medição ao vivo bate com o endpoint
  (01-mapas: 30 gráficos · 87,4% · 27 colados).
- **Alterado** `static/style.css`: `.densL` / `.densMed`.
- Salvar qualquer regra liga os limites (padrão 25% / 1 a cada 7 s) no render automaticamente.

## FALTA (opcional, follow-up)
- Chips "Suas regras" também no FORMULÁRIO de pedido (Vídeo com imagens / Cortes / Falado) pra o aluno
  já pedir com as regras antes de gerar (hoje regula no editor depois de aberto). Motor e editor prontos.
