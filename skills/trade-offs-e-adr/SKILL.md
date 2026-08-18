# Skill: Avaliação de Trade-offs e Registro de Decisão (ADR)

## Quando usar
Sempre que uma decisão de arquitetura importante for tomada, seja no Desenho de Arquitetura, na Pesquisa e Benchmarking, ou em qualquer outra atividade da cadeia. Não é uma etapa isolada no fim, é acionada no momento em que a decisão acontece, para não perder o porquê.

## Dono
O agente "Trade-offs e ADR" é o dono desta atividade. Qualquer agente com dúvida sobre por que uma decisão passada foi tomada, ou se uma decisão nova contradiz uma anterior, pergunta a este agente em vez de adivinhar (regra de [[rules/never]]).

## Passos
1. Receba a decisão do agente que a tomou (Desenho de Arquitetura, Pesquisa e Benchmarking, ou outro) junto com o contexto que a motivou.
2. Confira `substrate/compendium.md` seção 3 para ver se essa decisão contradiz algum ADR anterior. Se contradizer, sinalize o conflito em vez de registrar as duas decisões como se não se tocassem.
3. Escreva o ADR com: contexto/problema que forçou a decisão, alternativas consideradas e por que foram descartadas, a decisão em si, e as consequências/trade-offs aceitos (inclusive riscos assumidos conscientemente).
4. Envie o ADR para revisão de uma pessoa sênior ou líder técnico do time. O ADR não vale como decisão oficial até essa revisão acontecer, esse é o gate de aprovação humana desta atividade.
5. Depois de aprovado, adicione o resumo de uma linha do ADR em `substrate/compendium.md` seção 3, para que a próxima demanda já encontre essa decisão pronta.

## Artefato de saída
Um documento `adrs/adr-<numero>-<titulo>.md` (pasta global na raiz, não dentro de `demandas/`, porque um ADR existe para ser reaproveitado por demandas futuras, não só pela que o originou) com as quatro seções do passo 3, mais o status (proposto, aprovado, ou rejeitado), quem revisou, e o nome da demanda que originou a decisão (se veio de uma demanda específica e não de um padrão geral da casa).

## Como é bem feito
Uma pessoa sênior consegue revisar o ADR e entender a decisão sem perguntar "por que não fizeram X em vez disso?", porque as alternativas descartadas já estão explicadas. E o compêndio cresce a cada ADR aprovado, em vez de cada demanda repetir a mesma discussão do zero.
