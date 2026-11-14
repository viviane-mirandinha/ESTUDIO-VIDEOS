---
name: clientes-simulados
description: Monta um painel de 20 clientes simulados (IA) que reagem a uma página de vendas, preço ou anúncio, apontando objeções, nota de compra e o que mudar antes de lançar. Use quando o usuário pedir "clientes simulados", "testar página de vendas", "testar preço", "testar anúncio", "painel de clientes", "achar objeções antes de subir campanha". Plano B do guia Deploy Club (sem MiroFish, sem API paga).
---

# Clientes Simulados (painel de 20)

É simulação, NÃO pesquisa de mercado. Serve pra achar objeção e ponto fraco antes de gastar tráfego, não pra prever venda. Dizer isso no fim do relatório, em uma linha.

## Entrada necessária

1. Material: texto da página de vendas, ou preço e condições, ou texto + descrição do criativo do anúncio (arquivo, URL ou colado).
2. Público: descrição de quem compra (ex.: "donos de pequenos negócios no Brasil, 25–45 anos"). Se faltar, perguntar UMA vez. Se o material for URL, ler a página primeiro.
3. Preço e tema do produto (tirar do material se estiver lá).

Quanto mais real o material, melhor. Se vier fraco, pedir a página inteira.

## Passo 1 — Painel

Montar 20 clientes simulados do público. Variar: idade, profissão, renda, região do Brasil, nível de desconfiança com compra online, quanto já conhece do tema. **Mostrar a lista antes** (tabela curta) e seguir sem esperar, salvo se o usuário pediu para aprovar.

## Passo 2 — Reação

Cada cliente lê o material e responde em primeira pessoa, com voz própria:
1. o que entendeu que está sendo vendido;
2. se compraria pelo preço, de 0 a 10, e por quê;
3. a maior objeção;
4. a frase que mais chamou atenção e a que mais afastou.

Não ser bonzinho: cliente real passa reto sem dó. Distribuir notas de forma realista (maioria baixa/média), não todo mundo 7+.

## Passo 3 — Resumo

- quantos comprariam (nota ≥ 7) de 20
- as 5 objeções mais repetidas
- o que muda entre quem compraria e quem não
- 3 mudanças concretas no texto, preço ou oferta
- aviso: simulação, confirmar com cliente real / teste pequeno de tráfego

## Rodada 2 (só se o usuário pedir)

"Coloca os 20 numa conversa em grupo sobre a oferta e mostra como as opiniões mudam." Mais próximo do boca a boca do MiroFish.

## Variações

- **Página:** testar 2 versões de título, mesmo público, uma de cada vez; comparar placar.
- **Preço:** mesmo material, preço diferente; ver em que ponto "caro" domina.
- **Anúncio:** texto + descrição do criativo; perguntar o que faria parar de rolar.

## Custo

Um prompt só, sem API paga. Não subir MiroFish (gasto alto de API) a menos que o usuário peça.
