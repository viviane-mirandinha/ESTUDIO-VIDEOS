---
name: yt-escuro
description: Edita videoaula/vídeo 16:9 narrado no estilo "YouTube Escuro" (aprovado pelo Yuri em 07/11/2026) — fundo escuro quadriculado do YouTube, texto branco palavra-a-palavra com destaque amarelo, capas REAIS do YouTube com contador de visualizações, original × cópia lado a lado, grade de capas, barras comparando visualizações, etapas numeradas, título em inglês digitado com tradução, teclas Ctrl+C/Ctrl+V, e GRAVAÇÕES REAIS de telas do YouTube (canal, aba Popular, busca, vídeo tocando) feitas em navegador headless (nada do PC aparece). Um estilo só, sem misturar outras skills. Use quando pedirem "estilo yt-escuro", "estilo das aulas da Brecha Viral", "aula sobre YouTube com capas e telas reais", ou mandarem um áudio de aula/vídeo sobre YouTube/canais pra editar.
---

# yt-escuro

Motor: `kits\FERRAMENTAS\YT-ESCURO\motor\` (cópia do `_ed` das aulas Brecha Viral). Projeto de referência completo: `kits\PROJETOS-VIDEO\VIDEOAULAS-ESTUDIO\ECOSSISTEMA-VIRAL-M1\_ed\` (planos `plan_a1.py`, `plan_a2.py`, `plan_a3.py`, amostra `plan_a1s.py`).

## Regra de ouro
UM estilo só. Só cenas `yt_*` + gravações reais. O Yuri reprovou misturar estilos (07/11).

## Passo a passo (por vídeo, chave `aN`)
1. **Áudio** em `D:` (wav 48k). Palavras com tempo:
   `".venv do pacote/Scripts/python.exe" motor/words.py <audio.wav> aN/words_full.json <roteiro.txt opcional>`
   Depois gerar `aN/frases.txt` (frases com tempo) e `aN/words_cut.json` + `aN/edl.json` (ver make_base.py).
2. **Material real**: capas → `ov/img/capas/` (baixar `https://i.ytimg.com/vi/<ID>/maxresdefault.jpg`, nome descritivo com o número de visualizações). Números reais via `yt-dlp --flat-playlist --print "%(view_count)s|%(channel)s|%(title)s|%(id)s" "ytsearch15:<título>"`.
3. **Gravações** do YouTube: editar `rec_jobs.json` ([nome, url, modo scroll|popular, segundos]) e rodar `python -I rec_yt.py <dir>/rec <dir>/rec_jobs.json`. Ele pré-rola a página, ESPERA TODAS AS CAPAS CARREGAREM e corta o vídeo pra começar 5 s antes do "pronto" (use ss ≥ 5). Conferir sempre com contact-sheet: capa em branco = regravar (bug real de 07/11 na aula 3).
4. **Plano** `plan_aN.py`: seguir `GUIA-PLANO.md` (tipos, parâmetros, RECS, densidade 2–6 s, cobertura total). Plano grande = escrever por Agent (regra de custo). `python -I build.py aN` até sem erro + teste de buracos.
5. **Render**: `bash run_aula.sh N "TITULO"` (make_base → build → render Playwright 8 workers → compose com legenda só nas gravações, SFX, música baixa com sidechain, loudnorm −16). Saída `../0N - DD-MM-AAAA - CANAL - TITULO.mp4`.
6. **Conferir**: contact-sheet de ~12 quadros (nunca ler frame a frame), corrigir e re-renderizar só os índices mudados (`node render.mjs plan_aN.js ../aN/ins 8` após apagar `ins_XXX.mov`).

## Cenas (em `ov/engine.js`, bloco YOUTUBE)
yt_card · yt_vs · yt_grid · yt_title · yt_keys · yt_text · yt_list · yt_bars · yt_steps — parâmetros em `GUIA-PLANO.md`.
