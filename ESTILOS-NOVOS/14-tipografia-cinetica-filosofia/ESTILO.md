# 14 — Tipografia cinética sobre fundo escuro / filosofia (Pursuit of Wonder · Einzelgänger · Raquel de la Morena)

**Dados:** Pursuit of Wonder (EN) mediana 297k views, 910 views/h (melhor 2.600); Einzelgänger mediana 95k, 140 v/h (parado); Raquel de la Morena (ES, "¿Por qué triunfa el mal?") mediana 383k, 1.180 v/h. Nicho menor em views/hora que os outros, mas o mais barato de produzir e o que mais combina com "texto grande" que o usuário pediu. (O 08-psicologia-sombria já cobre a variante "pinturas clássicas"; aqui a mídia principal é o **texto**.)

## Visual
- **Pursuit of Wonder:** b-roll cinematográfico escuro (pessoa de costas, cidade, mar, chuva) com **frases inteiras em serifa branca** centralizadas, entrando palavra por palavra ou linha a linha, com leve movimento (drift) e desfoque do fundo; às vezes só **texto sobre preto**. Paleta: preto, branco, cinza; nenhuma cor. Música piano/ambiente; narração lenta.
- **Einzelgänger:** pinturas + animação 2D simples de personagem (sapo/figura), texto de citação em serifa com autor; mais ilustrado.
- **Raquel de la Morena (ES):** fotos/pinturas escuras + títulos grandes em sans bold branca caixa alta, mais "dark psychology", cortes 4-6 s.
- **Estilo "texto cinético" puro** (muitos canais stoic/motivacional, EN e ES): fundo preto ou textura escura, **1-4 palavras por vez** em sans bold gigante (80-140px), palavra-chave em amarelo/dourado, entradas com scale/blur/slide sincronizadas com a voz, câmera com leve shake/zoom.
- **Ritmo:** troca de texto a cada 1-3 s (sincronizado com whisper); b-roll troca a cada 8-12 s; sem SFX; música contínua.

## Mídia
Texto (fonte: Playfair Display / Cormorant para serifa; Inter/Montserrat Black para o kinetic), b-roll escuro Pexels (chuva, mar, cidade, pessoa de costas), pinturas de domínio público (Wikimedia) com filtro escuro, textura de papel/grão. Tudo livre.

## Template no editor
- `caption` já existe (palavra-por-palavra, `per_group 1-3`, 96px, `hl_color` dourado) — é o coração do estilo.
- `scene: "frase-serifa"` params `{texto, autor, modo: "linha|palavra"}` — serifa 56-64px centralizada, drift lento, fade.
- `video` b-roll `opacity 0.6` + `html` vinheta + grão + leve blur.
- `image` pintura escura com `motion: zoom_in 0.05`.
- `scene: "palavra-gigante"` params `{palavra, cor, efeito: "scale|blur|slide"}` — 120px.

## Dificuldade: preencher-dados (muito fácil)
Tudo vem do `words.json` do whisper + roteiro: o template decide quando é frase-serifa (citação) e quando é kinetic (ênfase). Um banco de 40 b-rolls escuros serve dezenas de vídeos. Custo por vídeo ~zero; views/hora da referência moderado (900-1.200) — bom como "canal de volume".
