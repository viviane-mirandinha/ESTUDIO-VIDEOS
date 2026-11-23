# Análise do reel de referência — "E se Sócrates tivesse Instagram?"

Fonte: https://www.instagram.com/reel/DfwnKrDyUYF/ (só para estudo; o arquivo em `ref/` é apagado no fim).
Medido por números (`medir_estilo.py` + lista de cortes) e visto em 4 folhas (114 quadros, 1 a cada 5 s), 2 sequências de movimento e 1 quadro ampliado.

## Resumo
**Não é vídeo real nem pintura.** É animação 2D de ilustração vetorial "plana", com personagens recorrentes, cenários
em camadas, telas de celular/Instagram desenhadas e frases em tipografia elegante. Só 2 imagens parecem reais/escultura
(busto de mármore de Sócrates, em fundo escuro, duas vezes).

## Números
- 570 s (9 min 30) · 1280x720 · 30 fps · horizontal 16:9
- 100 cortes detectados (≈10,5/min), plano médio 5,65 s, mediana 3,9 s, mais longo 23,7 s. Subestima: muita coisa muda
  DENTRO do plano (elemento entra, personagem se move, texto surge), então a sensação é de uma cena nova a cada ~3-4 s.
- Transições: 74 corte seco · 15 dissolve · 11 fade para preto (nos capítulos).
- Cores: preto quente `#151415`, creme `#e4dccd`, marrom `#4d4136`, bege `#c6b9a4`, destaque laranja/ferrugem `#c5864f`.
  Vermelho-carimbo e azul-marinho só em momentos pontuais.
- Áudio: -14,2 LUFS, voz com música baixa por baixo.

## Linguagem visual
1. **Personagens**: um "cara moderno" (moletom escuro, jeans) que representa o espectador; Sócrates (barba branca, túnica);
   outros gregos (túnicas coloridas) e multidão de silhuetas cinza. Rostos simples, olhos grandes, contorno fino.
2. **Fundos** (alternam conforme o clima): pergaminho creme com textura de papel/nuvens · preto com vinheta de luz ·
   marrom quente com vinheta · cidade de Atenas (casas brancas, telhado terracota, Partenon ao fundo, céu com sol pálido) ·
   mercado grego com toldos listrados · cela de pedra com grades · biblioteca com estantes · lousa verde com giz.
3. **Peças recorrentes**: celular com perfil/feed de Instagram (mão desenhada segurando), botão "Publicar"/"Seguir",
   livros com lombada e título (Górgias, Fedro, A República), contador de curtidas, carimbo vermelho ("DENUNCIADO",
   "CANCELADO", "EDITADO"), pergaminho, ampulheta, cronômetro, calendário, anel dourado, fios de marionete, olhos
   flutuando em volta do personagem, fila de personagens, pódio, escada, lista empilhada ("O BEM, BELEZA, VIRTUDE…"),
   gráficos desenhando (linha tracejada subindo/descendo).
4. **Tipografia**: serifada clássica em MAIÚSCULAS com espaçamento largo para frases de peso ("UMA VIDA SEM EXAME…",
   "QUEM É VOCÊ QUANDO NINGUÉM ESTÁ OLHANDO?", "399 a.C.", "ATENAS"); **manuscrita** (cursiva) para comentários
   pequenos ("quem você é", "ao contrário", "postar", "…a selfie"); etiqueta preta com letras brancas para palavra-chave
   ("O QUE VOCÊ É", "RESPEITADO"); balões de fala com letra manuscrita.
5. **Sem legenda contínua**: texto só em títulos, destaques e fala dos balões (≈2,5 % dos quadros pela medição, mas
   há muito texto dentro dos desenhos).

## Movimento (visto nas sequências)
- Personagem **entra de baixo para cima** ou desliza de lado; cabeça e braços com movimento leve (animação por peças,
  estilo "recorte"), não desenho quadro a quadro.
- **Parallax suave** no cenário (camadas em velocidades diferentes) e zoom lento durante o plano.
- Linhas **se desenham** (setas "PERGUNTA → RESPOSTA" no giz) e elementos **aparecem em sequência** (cada item da lista,
  cada pessoa da fila, cada sombra da plateia).
- Selos/carimbos "caem" com leve impacto; contadores sobem; barras enchem; ponteiro do cronômetro gira.
- Capítulos: **fade para preto** e volta, ou escurecimento forte com foco de luz (spotlight) no personagem.

## Ritmo narrativo
Gancho na abertura (3 curtidas, "5 fotos") → mundo de Sócrates → paralelo com o espectador no Instagram (câmera, filtros,
curtidas) → perguntas e conceitos → citação final em tela preta (a mesma frase do começo reaparece no fim — fechamento).
A mesma metáfora central (Sócrates × rede social) sustenta tudo; as peças voltam várias vezes (celular, o cara de
moletom, olhos que observam).

## O que isso significa para o Marco Aurélio
- **Dá para copiar muito bem** (é código/ilustração, justamente o que o Estúdio faz): fundos, personagens vetoriais,
  celular, livros, carimbos, tipografia, lousa, silhuetas, pergaminho, parallax, desenho de linhas.
- **Não é "imagens de pinturas"**: se você quiser pinturas/bustos/filmagens reais de Marco Aurélio, isso **foge do estilo**
  do original. Dá para MISTURAR (como o original faz com o busto de mármore, 2 vezes), mas o grosso tem que ser ilustração.
- **18,5 min no mesmo ritmo ≈ 195 cortes** detectáveis e muito mais mudanças internas. Isso exige **biblioteca de peças
  reutilizáveis** (personagens com poses, cenários, objetos) para não desenhar tudo do zero — e variação de enquadramento.
- **Sócrates × Instagram é uma metáfora moderna.** Marco Aurélio precisa de uma metáfora equivalente (decisão sua).

---
# Análise 2 (mais profunda) — o que separa o meu teste do original

Medido (zero token) com `frame diff` a 10 fps, original (300 s) × meu teste v4 (30 s):
| | Original | Meu v4 |
|---|---|---|
| Janelas de 1 s quase PARADAS | **44 %** | 13 % |
| Área da tela em movimento | 1,6 % | 4,0 % |
| Movimento médio | 1,17 | 2,60 |
→ O original é **calmo**: quase metade do tempo nada se mexe, e o que se mexe é pouco e com propósito. Meu teste vive em movimento
(personagem andando, nuvens, câmera em todas as cenas). Mais movimento NÃO é mais qualidade.

## Filosofia de movimento do original
1. **Personagem quase parado, de frente, com micro-movimentos** (respira, pisca, mão sobe). Quase nunca anda.
2. **A câmera é quem viaja**: no mercado, o Sócrates fica no lugar, a câmera dá zoom e desliza para o lado, e quando chega em cada
   barraca aparece uma palavra manuscrita pequena ("tecidos", "joias", "perfumes").
3. **Revelação em sequência** (item por item, no ritmo da fala): lista que empilha, pessoas que aparecem uma a uma, olhos que surgem.
4. **Cena-conceito**: um objeto/símbolo sozinho (ampulheta, anel, cadeira com silhueta num feixe de luz, calendário, carimbo).
5. **Imagem real composta**: busto de mármore real em fundo azul-escuro com partículas subindo (corações, celulares, "+851") e depois
   dissolve para o personagem desenhado. Mistura foto + motion graphics nos momentos de peso.
6. **Luz como linguagem**: feixes de luz diagonais, vinheta, silhueta preta contra luz, rosto do cara iluminado pelo celular.

## Arte (visto em quadros nativos 1280x720)
- **Contorno escuro grosso (~3–4 px) em TUDO**: personagem, colunas, toldos, tijolos, ânforas — é o que dá cara de "ilustração".
- **Densidade de detalhe**: toldos listrados com franjas de bolinhas, panos pendurados em 5 cores, ânforas de formas diferentes,
  frascos de perfume coloridos, tijolos irregulares, Partenon ao fundo, colunas em camadas (3 planos de profundidade).
- **Textura**: papel/granulação sobre os fundos e sombreado suave (gradientes, luz entrando pela grade na cela).
- **Personagem**: cabeça grande, olhos grandes com sobrancelha cinza, nariz arredondado, barba volumosa, mãos com dedos, túnica com
  faixa diagonal e dobras. Poucas poses, mas bem desenhadas.
- **Paleta contida**: creme/bege/marrom + 1 cor de destaque por cena (terracota, verde-musgo, azul-marinho). Nada saturado.

## Lacunas do meu modelo (honestas)
1. Falta contorno grosso e textura nos cenários; poucos detalhes por cena.
2. Muito movimento e personagem andando; falta **câmera viajando + rótulos que surgem**.
3. Falta o gênero "cena-conceito" (objeto sozinho + luz) e "revelação em sequência" como padrão.
4. Falta composição com imagem real (busto de Marco Aurélio, domínio público) + partículas.
5. Personagem de vetor simples (sem mãos com dedos, poucas expressões, sem faixa/dobras).
6. Tempos estimados (sem áudio): o original é cortado exatamente na palavra.
