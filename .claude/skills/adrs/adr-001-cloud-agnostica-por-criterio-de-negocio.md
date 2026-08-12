# ADR 001: Cloud agnóstica de provedor, escolhida por critério de negócio

**Status:** Aprovado.
**Revisado por:** Fabio Borges, Arquiteto de Soluções
**Data:** 2026-08-09

## Contexto
A stack aprovada citava OCI e Azure como os dois provedores de cloud do time. Ao evoluir o OS, o dono definiu que o time de agentes precisa ter domínio real sobre qualquer provedor de cloud, e escolher a melhor opção para cada demanda com base na necessidade de negócio, em vez de ficar preso a um provedor fixo ou a uma lista fechada de dois.

## Alternativas consideradas
- **Manter multi-cloud fixo (OCI + Azure):** descartada porque trava a escolha em dois provedores específicos mesmo quando um terceiro (AWS, GCP) atenderia melhor uma necessidade de negócio pontual (ex: um serviço gerenciado mais maduro em outro provedor, ou uma exigência de residência de dados numa região que só um provedor específico atende bem).
- **Escolher um único provedor padrão para simplificar:** descartada pelo mesmo motivo, reduziria ainda mais a capacidade de escolher a melhor opção por demanda, e o pedido explícito foi o oposto: mais domínio, não menos.
- **Cloud agnóstica, decidida por critério de negócio a cada demanda:** escolhida.

## Decisão
A escolha de provedor de cloud (AWS, Azure, GCP, OCI, on-prem, ou híbrido) passa a ser feita por componente e por demanda, nunca fixada de antemão. O agente de Infraestrutura e Deployment é o dono dessa escolha, usando os critérios: custo total, residência e compliance de dados, latência para o usuário final, maturidade do serviço gerenciado necessário para aquele componente específico, risco de vendor lock-in, e aderência ao que o time já opera (evitar fragmentar sem motivo de negócio). Quando a comparação não for óbvia, o agente aciona Pesquisa e Benchmarking.

## Consequências e trade-offs aceitos
- **Ganho:** a arquitetura de cada demanda pode usar o provedor que de fato atende melhor a necessidade de negócio, sem ficar refém de uma escolha antiga.
- **Custo aceito:** perde-se a simplicidade operacional de ter só um ou dois provedores conhecidos. Isso significa mais superfície para o time (e para os agentes) dominarem, e potencialmente mais provedores diferentes rodando ao mesmo tempo entre demandas distintas.
- **Risco aceito conscientemente:** sem um provedor padrão, existe risco de fragmentação (cada demanda num provedor diferente sem necessidade real). Mitigação: o critério "aderência ao que o time já opera" existe justamente para evitar fragmentação sem motivo de negócio, a escolha de um provedor diferente precisa ser justificada, não é o padrão.
