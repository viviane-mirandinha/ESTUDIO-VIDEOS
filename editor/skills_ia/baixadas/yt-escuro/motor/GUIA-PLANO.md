# Guia para escrever plan_aN.py (estilo único "YouTube Escuro")

Estilo APROVADO pelo Yuri: um único estilo. Fundo escuro quadriculado do YouTube, texto branco com destaque amarelo, capas reais e telas reais do YouTube. NÃO usar nenhum outro tipo de cena (nada de gh_*, kc_*, mq_*, boo, px_*, etc.). Só os tipos `yt_*` abaixo + gravações (RECS).

Referência aprovada: `plan_a1s.py` (amostra dos primeiros 79 s da aula 1). LEIA antes.

## Arquivo
```python
G = "graphite"
GAP, MAXD, MIND = 0.05, 20, 0.8
WORDS = "a1/words_full.json"          # aN
AUDIO = r"kits/PROJETOS-VIDEO/VIDEOAULAS-ESTUDIO/ECOSSISTEMA-VIRAL-M1/audio/AULA 01.wav"  # 02.wav / 03.wav
PLAN = []
def Tt(t, type, sfx="whoosh", dur=None, **p):
    PLAN.append({"t": t, "type": type, "p": p, "sfx": sfx, **({"dur": dur} if dur else {})})
RECS = []   # (inicio_s, duracao_s, "nome_da_gravacao", segundo_de_inicio_dentro_da_gravacao)
```
- Tempos: use `aN/frases.txt` (cada linha `[segundos] frase`) e, se precisar de precisão, `aN/words_full.json` (lista {w,s,e}).
- **Sempre dar `dur`** e garantir que nenhuma cena se sobrepõe à próxima (fim = t+dur ≤ próximo t − 0.05). Nas janelas de RECS não pode ter cena `Tt` (o buraco mostra a gravação).
- Cobrir o vídeo inteiro: cena ou gravação o tempo todo, troca a cada 2–6 s (nunca mais que ~7 s parado). Nenhum buraco > 1 s fora dos RECS.
- sfx: "whoosh" (padrão), "pop", "impact" (só ganchos fortes, pouco), "coin" (contador/dinheiro), "blip", "stamp", "ding", "paper".
- Texto em PT-BR. `*palavra*` = destaque amarelo. Frases curtas que resumem o que a voz diz (não transcrever tudo).

## Tipos de cena (todos tela cheia)
- `yt_card` — capa grande + título + canal + contador. p: img, title, ch, views (int), tag (chip opcional), tagc ("grn" padrão | "red" | "yel"), w (largura, padrão 1100).
- `yt_vs` — original × cópia lado a lado com contadores. p: top (texto com *destaque*), tb (s em que a 2ª entra, ~1.0), a={img,title,ch,views,tag}, b={...}. a fica verde, b vermelho.
- `yt_grid` — grade de capas (até 8, cols=4) com contador embaixo. p: top, items=[{img, views, ch, ok(bool: verde se True, vermelho se False)}], cols, step (atraso entre capas, padrão .28).
- `yt_title` — título em inglês sendo digitado + tradução amarela. p: en, pt, tpt (s em que a tradução entra), ten (s em que termina de digitar), top (rótulo, padrão "TÍTULO ORIGINAL (INGLÊS)").
- `yt_keys` — teclas CTRL+C → CTRL+V com a capa se multiplicando. p: img, tv (s do V).
- `yt_text` — frase grande central, palavra por palavra. p: text, chip (etiqueta amarela opcional em cima), sub (linha cinza opcional), size (100–180), hlc ("red"/"grn" muda a cor do destaque).
- `yt_list` — etiqueta + título + itens com seta amarela. p: chip, title, items (≤5, curtos), step.
- `yt_bars` — barras horizontais comparando visualizações. p: chip, title, rows=[{l: rótulo, v: número, ok: bool, c:"yel" opcional}], log (True quando a diferença é gigante, ex. 616161 vs 32), step.
- `yt_steps` — etapas numeradas em caixas lado a lado, ativando uma por uma. p: chip, steps=[{t:"GARIMPAR", s:"acha o vídeo validado"}], step (s entre etapas). Até 5 etapas.

## Capas disponíveis (p.img = nome exato do arquivo)
Liste `ov/img/capas/`. Os nomes dizem o que provam (ex.: `A1_esconderijos_copia_32views_WesSecures.jpg`). Os números reais estão em `../CONHECIMENTO-BRECHA-VIRAL.md` (seção 4) e `../_work/pesquisa/pesquisa*.txt`. Use SÓ números que existem lá.

## Gravações reais do YouTube (RECS) — pasta `rec/`
Liste `rec/*.webm` (algumas podem ter falhado — só use as que existem). Cada uma tem ~20 s. Regras de `ss` (início dentro da gravação):
- `watch_*` (vídeo tocando): ss entre 7 e 17 (antes de 7 a página ainda está carregando). Duração 2–5 s.
- `busca_*` e `canal_*` (página rolando): ss entre 5 e 17. Duração 2–6 s.
- `watch_original` = "25 Hiding Spots…" do Wes Tucker; `busca_hiding` = busca desse título.
Use gravação sempre que a voz diz "olha esse vídeo", "pesquisei", "abri o canal", "na aba populares", "se você buscar em alemão" etc. Na AULA 03 (demonstração de tela) as gravações devem cobrir ~35–45% do tempo; nas aulas 1 e 2, ~10–20%. Não repetir o mesmo trecho (mesmo nome + ss parecido) duas vezes.

## Saída
Escreva `plan_aN.py` na pasta `_ed`. Depois rode `python -I build.py aN` (de dentro de `_ed`) e corrija até não ter "NAO ACHOU", sobreposição, nem LACUNAS (fora das janelas de RECS). Não renderize nada.
