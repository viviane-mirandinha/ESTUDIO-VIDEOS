# 35 — Ranking de preços (estilo jack pockets + 10x Discovery) — o que copiar
- Estrutura: N itens em ordem CRESCENTE de valor ("do barato ao mais caro"), gancho na abertura: "a nº 1 vale mais que as outras 5 somadas".
- Fundo de estúdio branco/cinza claro com chão em perspectiva e grade (o "vazio 3D" do jack pockets).
- Foto GRANDE do item à esquerda (card 640x430, borda branca, sombra forte, fundo desfocado da própria foto, Ken Burns 1→1.07).
- Selo redondo do rank (#6…#1) preto/amarelo entrando girando.
- Etiqueta de preço amarela pendurada (formato tag com furo) que cai balançando (elastic) na hora em que a voz fala o valor, com contador 0 → valor ("US$ 8,3 MI").
- Lower-third estilo 10x Discovery: faixa preta "#N NOME" (Anton) + faixa amarela com contexto (ano, leilão).
- À direita, barras verdes 3D tipo jack pockets: cada nova barra cresce e as anteriores ENCOLHEM pelo novo máximo (mostra a escala absurda do salto).
- Cabeçalho fixo + bolinhas de progresso #6→#1.
- Fecho: gráfico completo dos 6 + "QUAL DESSAS VOCÊ COMPRARIA?" + "COMENTA AÍ!" + INSCREVA-SE.
- Sem legenda contínua, sem logo/nome dos canais de referência, só whoosh suave na troca de item.
- Paleta: #e9edf2 / #111 / amarelo #ffd21f / verde #18a957–#2fd277. Fontes: Anton + Inter (Google Fonts locais).

## Igual x diferente dos exemplos 03/04
- 04-ranking-velocidade também é ranking crescente com valor contado, mas é corrida em cena única de deserto com recortes (RED SIDE). Aqui o que é NOVO: foto grande em card + etiqueta de preço pendurada + lower-third amarelo + barras que reescalam. 03 (câmera CCTV) não tem nada em comum além do formato TOP N.
- Reaproveitado do 04: whisper.py, fetch_imgs.py (Wikimedia com backoff), padrão template local + edit.json.

## Como fazer um vídeo novo do mesmo estilo
1. Editar lista R em make_edit.py (rank, img, preço, valor_usd p/ barra, t_preco = segundo em que a voz fala o preço).
2. Fotos: fetch_imgs.py (Wikimedia) → img/<id>.jpg e adicionar <img src> no #preload do template.html.
3. Voz edge-tts → whisper.py → tempos → make_edit.py → build_from_edit.py --render.
