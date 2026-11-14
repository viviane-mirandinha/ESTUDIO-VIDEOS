# 10 — Caso médico "um homem comeu X, isto aconteceu com seus órgãos" (Chubbyemu · Cabedark)

**Dados:** Chubbyemu (EN) mediana 4,3M views, 8.300 views/h nos 45 d — 2ª maior mediana entre os replicáveis. Cabedark (ES, "esto es lo que pasó con sus órganos") mediana 210k, 420 v/h (melhor 2.300). Em PT não há clone forte = gap de idioma.

## Visual
- **Estrutura rígida:** paciente apresentado por iniciais ("JC, 32 anos") → sintomas → exames → diagnóstico explicado com **cards de texto** → desfecho. Toda sigla aparece escrita na tela com **expansão** ("CPK → creatine phosphokinase").
- **Cards de texto:** fundo escuro liso (#111 a #1b1b1f), **sans branca bold grande** (60-80px) com a palavra-chave; linha de apoio em cinza. Números de exame em tabela simples (nome · valor · faixa normal, valor anormal em vermelho).
- **Imagens:** **render 3D de órgão** (stock: rim, fígado, coração em fundo escuro, girando), b-roll de hospital/laboratório (Pexels), ilustração médica em flat; às vezes recriação com ator (Chubbyemu) — dispensável.
- **Paleta:** fundo escuro, branco, vermelho (#e3342f) para anormal, azul-claro (#5bc0eb) para normal/explicação.
- **Ritmo:** corte a cada 3-6 s; card de texto a cada frase técnica; narração rápida e monótona (parte do estilo); sem música ou música baixa; sem legenda contínua.

## Mídia
Renders 3D de órgãos (Pixabay/Pexels têm; ou Three.js com modelos GLB livres do Sketchfab CC0), b-roll hospital, ícones médicos SVG, gerar imagens de exames com HTML (tabela). Zero foto de pessoa real.

## Template no editor
- `scene: "card-termo"` params `{termo, expansao, nota}` — termo 72px + expansão 36px, fade/slide.
- `scene: "tabela-exame"` params `{linhas:[{nome, valor, normal, status}]}` — tabela animada linha a linha, anormal em vermelho.
- `scene: "orgao-3d"` params `{modelo: "rim|figado|coracao|cerebro", destaque, cor}` — Three.js GLB girando com luz; ou `video` stock.
- `scene: "paciente"` params `{iniciais, idade, sexo, queixa}` — card de abertura.
- `video` b-roll hospital com vinheta.

## Dificuldade: preencher-dados (média)
Esqueleto de roteiro 100 % fixo (ótimo pro Ollama) e 4 cenas genéricas; o cuidado é factual (sintoma/exame/diagnóstico coerentes — usar casos publicados em revistas médicas de acesso aberto como premissa, regra "fato na premissa"). Biblioteca de 8-10 órgãos em GLB resolve quase todos os vídeos.
