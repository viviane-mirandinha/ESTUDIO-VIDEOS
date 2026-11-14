# Estilo 35 — Ranking de preços (foto grande + etiqueta + barras)

**Canais de referência:** jack pockets ("What's The Most Expensive Thing Ever?") e 10x Discovery ("10 Most Expensive Things on Earth"). 16:9.

## O que define o estilo
- Ranking CRESCENTE de valor (#6 → #1), gancho: "a nº 1 vale mais que todas as outras somadas".
- Fundo de estúdio branco com chão em perspectiva (vazio 3D do jack pockets).
- Foto grande do item em card com borda branca + sombra + Ken Burns lento.
- Etiqueta de preço amarela pendurada, cai balançando quando a voz fala o valor; contador 0 → valor.
- Lower-third preto/amarelo com "#N NOME" + contexto (ano, leilão) — herança 10x Discovery.
- Barras verdes 3D à direita: a nova cresce e as antigas encolhem (escala relativa ao novo máximo).
- Bolinhas de progresso #6…#1 e cabeçalho fixo. Fecho com gráfico completo + pergunta p/ comentário + INSCREVA-SE.
- Narração direta, 1 frase de contexto + preço por item (~8-10 s/item). Sem legenda contínua, sem música, só whoosh suave.

## Exemplo pronto
VIDEOS-NOVOS/35-ranking-precos/35 - 24-10-2026 - RANKING PRECOS - Do barato ao mais caro 6 coisas mais caras ja vendidas.mp4

## Diferença dos estilos 03/04
- 04 (ranking velocidade) = corrida numa cena única com recortes; aqui = foto real grande + etiqueta + barras que reescalam.
- 03 (top 5 câmera) = CCTV; só compartilha a estrutura TOP N.

## Como replicar
Trocar a lista R em make_edit.py (preço com fonte!), baixar fotos com fetch_imgs.py (Wikimedia), voz edge-tts, whisper.py para t_preco, build_from_edit.py --render.
Regras: todo preço com fonte em RELATORIO.json; moeda original na etiqueta; conversão só para altura da barra (avisar no rodapé).
