# 27 — Documentário stock de megaprojetos / aviação / engenharia (Flightside Insider · SIGNUM · Innovation Core · Polarisyn · Agriculture Flow)

**Dados:** vídeos enviados são outliers virais em canais pequenos: Innovation Core "windowless plane" **503k views** (canal mediana 5,8k); Flightside Insider "JetZero" 234k (mediana 6,6k); SIGNUM "Broken mega-airports" 138k, 1.350 v/h (mediana 23k, melhor canal do lote); Polarisyn "Honda flagship" 100k; Agriculture Flow "23 poisoned cats" 3,7k (mediana 12k). Lição: **título/premissa de "X vai acabar com a indústria"** + visual barato = viral ocasional. Formato 18-30 min.

## Visual (sheet-*.jpg)
- **Base = b-roll stock de aviação/indústria** (Pexels/Pixabay/press kits: cabine, asa, pista, fábrica, aeroporto lotado) + **renders 3D de produto** (avião conceito, drone Honda) + fotos de executivo/entrevista; cortes a cada 3-6 s.
- **Rótulo amarelo de dado** no canto inferior esquerdo: caixa amarela com texto preto bold ("$30,000 DOLLARS", "122 TIMES", "2007-2013", "11 MILLION") — a marca visual do estilo; rótulos azuis para lugar/data ("WEST JAVA, INDONESIA", "MARCH 2025").
- **Print de manchete** (NYT) com zoom; **card de texto branco centralizado** ("IN SEPTEMBER 2025", "300 AIRCRAFT") em sans bold 48-60px sobre o clipe escurecido; "THE AVIATION DREAM" como capítulo.
- **Polarisyn:** moldura escura com imagens em janela + cards pretos pequenos ("SMALLER JET", "ONE-PILOT CONTROL") estilo spec.
- **Agriculture Flow:** arquivo P&B + stock de animais + **timecode** no canto (00:05:49:19) + X vermelho sobre a foto + marca d'água — doc "ecologia que deu errado".
- Paleta: azul-céu/cinza do stock + amarelo (#ffd400) + branco. Sem legenda. Narração enérgica, música épica/corporativa.

## Template no editor
- `video` stock `fit: cover` + `html` vinheta leve; `image` render/foto com `motion: zoom_in`.
- `scene: "rotulo-dado"` params `{texto, cor: "amarelo|azul", pos}` — caixa chapada com slide-in 0,3 s.
- `scene: "manchete"` (do 13) com veículo genérico; `text` card centralizado 56px bold `bg rgba(0,0,0,.4)`.
- `scene: "spec-cards"` params `{itens:[...]}` (Polarisyn); `scene: "timecode"` params `{inicio}` (Agriculture Flow).
- `scene: "capitulo"` existente.

## Dificuldade: preencher-dados (fácil)
É o 03-finanças stock com 2 cenas novas (rótulo amarelo, timecode). Mídia 100 % stock/press kit (renders de fabricante = press material, ok com crédito). Ollama: roteiro "megaprojeto/tecnologia que muda tudo" com fato na premissa (projetos reais: JetZero, Honda eVTOL, aeroportos). PT/ES: nenhum concorrente visto = gap.
