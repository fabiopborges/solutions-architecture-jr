# Skill: Revisão de Riscos e Plano de Mitigação

## Quando usar
Depois que Desenho de Arquitetura, Testes e Qualidade, e idealmente Documentação Final existem. Junta dois tipos de risco: os técnicos já sinalizados por outros agentes, e riscos de negócio/projeto que ainda não tinham dono.

## Dono
O agente "Riscos e Mitigação" é o dono desta atividade. Qualquer agente com dúvida sobre se um risco tem mitigação definida, ou qual o nível de prioridade de um risco, pergunta a este agente em vez de adivinhar (regra de [[rules/never]]).

## Passos
1. Reúna os riscos técnicos já sinalizados por [[agents/desenho-de-arquitetura/AGENT]] (pontos fracos do desenho) e [[agents/testes-e-qualidade/AGENT]] (pontos únicos de falha, requisitos não atendidos). Não redescobre esses riscos do zero, herda e aprofunda.
2. Levante riscos de negócio e de projeto que não são de arquitetura: prazo apertado, dependência de fornecedor externo, time pequeno demais para a demanda, e qualquer coisa que ameace a entrega mesmo com a arquitetura perfeita.
3. Priorize todos os riscos (técnicos e de negócio juntos) por impacto e probabilidade. Uma lista solta sem prioridade não ajuda ninguém a decidir onde focar primeiro.
4. Para cada risco, defina uma mitigação concreta, ou registre explicitamente a decisão de aceitar o risco (e por quem). Nenhum risco fica só anotado sem uma dessas duas respostas.

## Artefato de saída
Um documento `demandas/<nome-da-demanda>/riscos.md` com: tabela de riscos (técnicos e de negócio) x impacto x probabilidade x prioridade, e para cada um, mitigação ou aceite explícito.

## Como é bem feito
Cada risco listado tem uma mitigação ou uma decisão explícita de aceitar, nenhum fica solto, e dá para ver quais riscos merecem atenção primeiro só olhando a priorização.
