# 37 — História de empresa ilustrada: "A história inteira da X em N minutos" (Built On You / CEOzoned)

**Dados:** Built On You (Amazon 204 mil, Walmart 74 mil, Toyota 93 mil views; 19-21 min) e CEOzoned (SpaceX 176 mil, Elon Musk 128 mil; 9-16 min). Título-fórmula fixo "The ENTIRE History of <empresa> in <N> Minutes". Narração cronológica, ano a ano, do fundador ao império; cada época tem 1 virada/fracasso + 1 número.

## Visual (sheets na pasta)
- **1 ilustração por frase** (corte a cada ~3 s), Ken Burns lento. Nada de foto real nem footage.
- **Bonecos de cabeça branca redonda, olhos de ponto** (sem rosto realista), roupa simples; o fundador é sempre o mesmo boneco com 1 traço marcante (cabelo, terno, bigode).
- **Cenários detalhados** (escritório, fábrica, rua, loja, galpão): Built On You em sépia/oliva dessaturado com borda rasgada de papel; CEOzoned colorido saturado, traço preto grosso.
- **Rótulos à mão entre aspas** ("1997", "GENERAL STORE", "5 HOURS"), placas/cartazes dentro da cena, letreiros com nome da empresa.
- Cenas-conceito em fundo liso: balança, gráfico subindo/descendo, ampulheta, seta, objeto mágico (caixa saindo da cartola).
- Multidão de bonecos clonados para "milhões de clientes/funcionários".

## Nosso template (template.html / make_edit.py, SVG + GSAP)
- Cenas `scene`: kyoto(cidade/época), oficina, loja(fachada+letreiro), hiroshi(escritório), tenta(3 painéis), fracassa(chuva+gráfico), yokoi(oficina), ultra(objeto animado), miya(arcade), futuro(holofote), famicom(sala+TV), nes(rota entre países), linha(produtos+anos), gigante(antes→depois).
- Item `regua`: régua de anos no rodapé com marcador que anda (anos e tempos editáveis).
- Personagem `P({cabelo,bigode,bone,quimono,gravata,pose,emo})` reutilizável; filtro "rough" + grão + borda rasgada dão o ar de ilustração à mão.
- Para outra empresa: trocar textos/anos em make_edit.py e reaproveitar cenas (escritório, fachada, painéis, gráfico, linha de produtos).

## Dificuldade: média
Sem imagem externa; o custo é desenhar 3-5 cenários novos por empresa. Para 20 min seria preciso biblioteca maior de cenários (ou ilustração gerada por IA, como os canais originais fazem).
