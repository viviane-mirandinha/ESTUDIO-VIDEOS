# 08 — Documentário cinematográfico escuro "Fern" (Fern · Not What You Think · RealLifeLore)

**Dados:** Fern (EN) mediana 3,5M views, 11.400 views/h nos 45 d (melhor 60k v/h) — o maior canal faceless "premium" da mineração. RealLifeLore mediana 1,2M, 3.300 v/h. Not What You Think (menor) mediana 219k, 1.260 v/h.

## Visual (sheet-fern-tv-*.jpg)
- **Tudo escuro e cinematográfico:** fundo preto/azul-petróleo, luz volumétrica, névoa. Cenas 3D (Blender) de ambientes genéricos: sala de servidores, corredor, cidade à noite, mapa 3D com relevo visto de cima em ângulo.
- **Tipografia como personagem:** palavras-chave em **sans grotesca branca bold** (56-90px) aparecem no meio da cena 3D, com profundidade (atrás de objetos, iluminadas), tracking aberto; sub-títulos em cinza. Números gigantes ("$4.000.000") com contagem.
- **Mapa 3D escuro:** terreno preto com linhas finas brancas/azuis, rótulos de cidade, câmera voando baixo.
- **Fotos/prints reais** entram em **molduras 3D flutuando no espaço escuro** (print de site, foto de arquivo, documento), levemente inclinadas, com reflexo.
- **Paleta:** preto, azul-aço (#2b4a6f), branco, 1 cor de acento por vídeo (laranja/vermelho/ciano). Grão e aberração cromática leves.
- **Ritmo:** planos longos (6-12 s) com movimento lento de câmera; corte seco com micro-fade; música eletrônica tensa; narração calma. Sem legenda.

## O que é replicável
O 3D completo do Fern é sob-medida (Blender por cena). A **versão HTML**: fundo escuro com partículas/névoa (canvas), **texto grande com luz e profundidade (CSS text-shadow + blur + parallax)**, mapa 3D = Three.js com GeoJSON extrudado (já existe no 09-tamanho e 13-3D técnico), **fotos em molduras 3D** = CSS `perspective` + `rotateY` + reflexo. Isso cobre 80 % do look com 4 cenas.

## Template no editor
- `scene: "titulo-3d"` params `{texto, sub, cor}` — texto bold em névoa com luz passando.
- `scene: "moldura-3d"` params `{src, legenda, angulo}` — foto/print flutuando com reflexo.
- `scene: "mapa-3d-escuro"` params `{foco, rota:[...], rotulos:[...]}` — Three.js.
- `scene: "numero-gigante"` params `{valor, prefixo, sufixo, dur}`.
- `video` b-roll escuro (Pexels: servidores, cidade à noite, drones) com `opacity 0.8` + vinheta.
- Canvas `bg: "#05070a"`.

## Dificuldade: sob-medida no 1º vídeo (alta), preencher-dados depois (média)
As 4 cenas exigem construção cuidadosa (é o estilo onde "parecer barato" mata). Depois, cada vídeo = lista de `{frase, tipo_de_cena, mídia}` + b-roll escuro. Vale como "estilo premium" do catálogo — maior referência de views/hora entre os replicáveis.
