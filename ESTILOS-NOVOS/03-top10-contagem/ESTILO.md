# 03 — Top 10 / contagem regressiva "captado em câmera" (Doc Tops · ROOM 13 · Hiper Cabuloso)

**Dados:** Doc Tops (ES) 16,5M inscritos, mediana 4,6M views, 8.700 views/h — maior mediana entre canais replicáveis. ROOM 13 (EN, 1.400 v/h, mediana 165k) e Hiper Cabuloso (PT, mediana 93k) são as versões pequenas do mesmo molde.

## Visual (sheet-doctops-*.jpg, sheet-room-13-*.jpg)
- **Mídia dominante:** clipe de câmera de segurança / celular / campainha (4:3 ou vertical) **com borda preta**; timestamp de CCTV no canto. Qualidade ruim faz parte do estilo.
- **Marcação:** **seta vermelha grossa** e **círculo vermelho** por cima do clipe apontando o detalhe (Doc Tops); replay do mesmo trecho 2-3x, câmera lenta e zoom (crop 1.4-2x).
- **Cards:** ROOM 13 abre cada item com card claro "13.904 VIEWS" (contador animado) + crédito "©tiktok: @usuario" pequeno no rodapé; Doc Tops mostra o post original (print de celular com legenda) antes do clipe.
- **Paleta:** preto + vermelho (#e8101a) das marcações + branco. Vinheta escura nas bordas (ROOM 13 bem fechada, "sala escura").
- **Fontes:** número do item grande (display bold 120px, 1,5 s) e título curto do caso em sans bold branca caixa alta.
- **Ritmo:** cada item 60-120 s; dentro dele cortes a cada 2-4 s (clipe → zoom → replay → print). Transição entre itens = card de número com whoosh suave. Sem legenda contínua.

## Mídia
Clipes curtos (os canais usam clipes de redes sociais com crédito). Pra nós: Pixabay/Pexels tem pouco "assustador"; a saída é **gerar os clipes** (LTX-2.5 local, look CCTV: P&B, ruído, timestamp) ou footage público (Internet Archive). Timestamp e ruído de CCTV são overlays nossos.

## Template no editor
- `scene: "numero-item"` params `{n, titulo}` — fundo preto, número gigante com contagem e título; 1,5 s.
- `video` com `fit: contain` + borda, `motion: zoom_in` no replay, `speed: 0.5` na câmera lenta, `trim` nos replays.
- `html` overlay CCTV: timestamp (fonte mono) + ruído SVG + vinheta.
- `scene: "seta-circulo"` params `{tipo: "seta|circulo", x, y, ang}` — vermelho, draw-on 0,3 s, pulsa.
- `scene: "card-views"` params `{views, fonte}` — card claro com contador.
- `text` crédito no rodapé 24px.

## Dificuldade: preencher-dados (média)
Estrutura mais simples de todas (N itens × mesmo bloco); o custo está em **arranjar os clipes**. Com clipes gerados localmente vira fábrica; com clipes de terceiros é risco de strike.
