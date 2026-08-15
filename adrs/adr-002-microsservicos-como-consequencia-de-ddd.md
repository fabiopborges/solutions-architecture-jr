# ADR 002: Microsserviços como consequência de modelar por domínio (DDD), não como escolha de tecnologia isolada

**Status:** Aprovado.
**Revisado por:** Fabio Borges, Arquiteto de Soluções
**Data:** 2026-08-09

## Contexto
Microsserviços já era o estilo de arquitetura padrão da casa, mas o porquê nunca tinha sido registrado, só a preferência em si. Ao evoluir o OS, o dono pediu que o time domine DDD (Domain-Driven Design) e TOGAF no que diz respeito às funções de negócio. Isso dá ao time uma forma sistemática de chegar nos limites de serviço, em vez de desenhar componentes por instinto técnico.

## Alternativas consideradas
- **Continuar com microsserviços como preferência sem justificativa formal:** descartada porque deixa a divisão de componentes sujeita ao critério pessoal de quem desenha naquele dia, sem um jeito consistente de saber se um componente deveria existir ou não.
- **Monólito modular:** considerada como alternativa válida em geral, mas descartada como padrão da casa porque o time já opera com integração via mensageria (Kafka/AMQ Streams) e múltiplas linguagens (Java, Python, Node.js) por área, o que já pressupõe serviços independentes.
- **Microsserviços delimitados por bounded context (DDD):** escolhida.

## Decisão
O agente de Entendimento e Escopo mapeia capacidades de negócio e cadeia de valor (TOGAF Business Architecture) para cada demanda. O agente de Desenho de Arquitetura traduz essas capacidades em bounded contexts, linguagem ubíqua e agregados (DDD). Cada microsserviço corresponde a um bounded context (ou a um agrupamento justificado de contextos pequenos relacionados), nunca a uma divisão puramente técnica. A comunicação entre bounded contexts é sempre por contrato explícito (evento ou API), nunca por acesso direto ao modelo interno de outro contexto.

## Consequências e trade-offs aceitos
- **Ganho:** os limites dos serviços passam a ter uma justificativa rastreável até uma capacidade de negócio real, em vez de serem uma escolha arbitrária. Isso também dá ao Desenho de Arquitetura um jeito de detectar quando um bounded context foi mal identificado (ele não corresponde a nenhuma capacidade de negócio do escopo).
- **Custo aceito:** exige que o agente de Entendimento e Escopo faça um trabalho extra de mapeamento de capacidades de negócio em toda demanda, mesmo as pequenas, antes de qualquer requisito técnico ser levantado.
- **Risco aceito conscientemente:** para domínios pequenos ou pouco claros, identificar bounded contexts pode ser ambíguo. Mitigação: o portão de revisão do Desenho de Arquitetura já prevê voltar para o Entendimento e Escopo quando um bounded context não corresponde a nenhuma capacidade de negócio mapeada, em vez de inventar um contexto novo.
