# Skill: Pesquisa e Benchmarking de Soluções/Tecnologias

## Quando usar
Sempre que o Desenho de Arquitetura precisar escolher entre mais de uma tecnologia ou solução para resolver um pedaço da demanda (ex: qual banco, qual provedor de fila, comprar vs construir). Roda a pedido do agente de Desenho, não por conta própria.

## Dono
O agente "Pesquisa e Benchmarking" é o dono desta atividade. Qualquer agente com dúvida sobre por que uma tecnologia foi recomendada em vez de outra, ou quais critérios pesaram na comparação, pergunta a este agente em vez de adivinhar (regra de [[rules/never]]).

## Passos
1. Antes de pesquisar qualquer coisa nova, confira `substrate/compendium.md` seção 1 (Stack aprovada). Se algo já aprovado resolve a necessidade, a recomendação é usar o que já é padrão da casa, e a pesquisa termina aqui, registrando esse motivo.
2. Se a stack aprovada não cobre a necessidade, defina os critérios de comparação antes de olhar qualquer opção (ex: custo, maturidade, suporte, curva de aprendizado, e para decisões de cloud especificamente os critérios de negócio do `substrate/compendium.md`: compliance/residência de dados, latência, vendor lock-in, aderência ao que o time já opera).
3. Liste as opções candidatas e pontue cada uma contra os mesmos critérios, lado a lado. Nenhuma opção pode ser avaliada com critério diferente das outras.
4. Feche com uma recomendação clara. Se for empate real entre duas opções, diga isso explicitamente e explique por quê, em vez de fingir uma diferença que não existe.

## Artefato de saída
Um documento `demandas/<nome-da-demanda>/pesquisa-<tema>.md` com: necessidade que motivou a pesquisa, se a stack aprovada já resolve (e se sim, para por aqui), critérios de comparação, tabela de opções x critérios, e a recomendação final.

## Como é bem feito
As opções aparecem comparadas lado a lado com os mesmos critérios, não como prós e contras soltos, e termina com uma recomendação clara que o agente de Desenho de Arquitetura consegue usar direto, sem ter que decidir ele mesmo qual opção pesa mais.
