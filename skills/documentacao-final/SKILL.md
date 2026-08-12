# Skill: Documentação Final e Diagramas

## Quando usar
É um ponto de sincronização real: só começa depois que todos os ramos paralelos da cadeia terminam (Desenho, Modelagem de Dados, Segurança, Infraestrutura, Custo, Observabilidade, Testes e Qualidade, e qualquer Pesquisa/ADR que tenha rodado). Não adianta montar antes, porque juntaria peças incompletas.

## Dono
O agente "Documentação Final" é o dono desta atividade. Qualquer agente com dúvida sobre onde uma decisão ficou registrada no pacote final pergunta a este agente em vez de adivinhar (regra de [[rules/never]]).

## Passos
1. Confirme que todos os documentos de entrada existem: entendimento e escopo, desenho de arquitetura, modelagem de dados, segurança e compliance, infraestrutura e deployment, estimativa de custo, observabilidade, testes e qualidade, e os ADRs aprovados. Se algum estiver faltando, o pacote não está pronto, não preencha a lacuna com suposição.
2. Monte o diagrama de componentes/integrações (C4 ou similar) a partir do desenho de arquitetura.
3. Monte o diagrama de fluxo de dados a partir da modelagem de dados, mostrando eventos (Kafka/AMQ Streams) e consultas via API entre serviços.
4. Monte o diagrama de infraestrutura/deployment a partir de infraestrutura e deployment, mostrando onde cada componente roda e em qual provedor (a stack é agnóstica, o diagrama mostra o que foi escolhido para essa demanda específica, não assume um provedor fixo).
5. Junte tudo num único documento final, organizado por seção, cada seção citando de qual documento de entrada ela veio, para quem revisar conseguir voltar à fonte.

## Artefato de saída
Um documento `demandas/<nome-da-demanda>/pacote-final.md` com as seções de todos os agentes anteriores resumidas, mais os três diagramas, e um índice no topo apontando para os documentos de origem completos.

## Como é bem feito
Qualquer pessoa do time consegue ler o pacote final sozinha, entender a solução de ponta a ponta (o que foi pedido, o que foi desenhado, como os dados fluem, onde roda, quanto custa, como é observado, e onde a qualidade foi checada), sem precisar abrir os documentos de origem, mas sabendo onde estão se precisar.
