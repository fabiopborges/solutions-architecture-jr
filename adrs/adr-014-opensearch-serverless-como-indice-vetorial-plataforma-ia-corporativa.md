# ADR 014 — Amazon OpenSearch Serverless (via Bedrock Knowledge Bases) como índice vetorial de C3 para Plataforma-IA-Corporativa-V1

## Status
**Proposto.** Aguardando revisão de uma pessoa sênior ou líder técnico do time. Não vale como decisão oficial até essa revisão acontecer.

## Demanda de origem
`demandas/plataforma-ia-corporativa-v1/` — decisão tomada por Pesquisa e Benchmarking (`pesquisa-indice-vetorial.md`), acionado a partir de sinalizações convergentes do Desenho de Arquitetura, do Especialista em IA/ML e de Modelagem de Dados. Formalizada aqui por Trade-offs e ADR, não decidida de novo.

## Contexto / Problema
C3 (Índice de Conhecimento Corporativo) precisa de tecnologia de busca vetorial que suporte, na mesma consulta, **filtro de metadado de sensibilidade no nível de chunk/trecho** (não documento inteiro) combinado com busca semântica — requisito eliminatório derivado de RNF07 e do risco R1 do desenho (vazamento de dado sensível entre áreas, classificado como crítico). O compêndio (seção 1) fixa MongoDB como banco padrão da casa, mas **não confirma capacidade de busca vetorial** como parte desse padrão — a oferta vetorial do MongoDB (Atlas Vector Search) só existe na oferta gerenciada Atlas, um produto diferente do MongoDB self-hosted usado por padrão em outras demandas. Não havia precedente no compêndio para essa escolha.

A decisão de RAG (em vez de fine-tuning, ver ADR 013) depende diretamente desta capacidade existir de fato: RAG só preserva o controle de acesso granular se o mecanismo de recuperação suportar esse filtro corretamente.

## Alternativas consideradas
Comparadas dentro do provedor já recomendado por Infraestrutura (AWS `sa-east-1`, ver ADR 012), todas compatíveis com Amazon Bedrock Knowledge Bases (camada de orquestração de RAG já sinalizada):

| Opção | Mecanismo de filtro | Garantia para o requisito crítico (RNF07/R1) | Custo (piso mensal, ordem de grandeza) | Complexidade operacional |
|---|---|---|---|---|
| **MongoDB Atlas Vector Search** | Pre-filter integrado ao índice (`$vectorSearch.filter`), mas depende de o campo de sensibilidade estar corretamente declarado como filtrável — configuração manual | Alta, mas com superfície de erro operacional (índice mal configurado = campo não filtrável) | ~US$ 140–150/mês | Menor esforço de aprendizado (time já opera MongoDB para outras finalidades), mas Atlas é produto gerenciado separado do MongoDB self-hosted padrão da casa |
| **Aurora PostgreSQL Serverless v2 + pgvector** | **Post-filter por padrão** (ANN roda primeiro, filtro `WHERE` depois) — estruturalmente mais frágil para este requisito; degradação de precisão conhecida quando o filtro é muito seletivo (caso comum aqui: usuário com acesso só a uma fração do corpus) | Média — funcional se implementada com disciplina extra (garantir que nenhuma etapa downstream use resultado pré-filtro), mas não é a garantia estrutural mais forte | < US$ 50/mês | Média — Postgres é tecnologia amplamente conhecida no mercado |
| **Amazon OpenSearch Serverless** (escolhida) | "Efficient k-NN filtering" nativo, integrado ao próprio algoritmo ANN, escolhendo dinamicamente estratégia conforme seletividade do filtro — mecanismo mais maduro e documentado dos três para este critério específico | Alta, sem depender de configuração manual adicional | ~US$ 345/mês (piso, mínimo de 2 OCUs mesmo sem tráfego) | Maior — serviço novo para o time (nenhuma demanda anterior desta casa operou OpenSearch), mitigada por ser totalmente gerenciado (sem cluster para dimensionar/patchar) |
| *Amazon S3 Vectors* (citada, não comparada lado a lado) | Suporta filtro por metadado combinado com busca vetorial | Não avaliável — GA muito recente (dezembro de 2025), sem evidência pública suficiente de maturidade em produção para requisito crítico de segurança | Mais barato que as demais, segundo Infraestrutura | Não avaliada por falta de maturidade equivalente |

**MongoDB Atlas foi descartado como primeira opção** por depender de configuração manual correta do índice (campo filtrável), introduzindo superfície de erro operacional que o mecanismo automático do OpenSearch não tem, e por ser uma peça de produto separada do MongoDB self-hosted padrão da casa (não um reaproveitamento trivial da stack aprovada). Não é uma opção rejeitada por inviabilidade técnica — é tecnicamente aceitável e permanece como segunda opção.

**Aurora + pgvector foi descartado como primeira opção** por usar post-filter por padrão, a abordagem estruturalmente mais frágil das três para um requisito de segurança crítico (nenhum trecho sensível pode chegar ao LLM ou ao usuário errado), apesar de ser a opção mais barata.

## Decisão
Adotar **Amazon OpenSearch Serverless, como backend de Amazon Bedrock Knowledge Bases, em `sa-east-1`**, como tecnologia de índice/busca vetorial para C3 (Índice de Conhecimento Corporativo).

Justificativa central: é a única das três opções com mecanismo de filtro nativamente pre-filter/eficiente, documentado como tal pelo fornecedor, sem depender de configuração manual adicional — dado que o requisito em jogo é impedir vazamento de dado sensível entre áreas (risco R1, crítico), a garantia estrutural mais forte pesa mais que custo ou familiaridade do time.

## Consequências / Trade-offs aceitos
- **Maior custo entre as três opções comparadas** (~US$ 345/mês de piso, contra < US$ 50/mês do Aurora e ~US$ 140–150/mês do MongoDB Atlas) — aceito conscientemente porque o teto de orçamento (lacuna 2 do entendimento) ainda não foi confirmado; não há hoje evidência de que essa diferença inviabilize a opção. **Risco assumido**: se o orçamento vier apertado, esta decisão pode precisar ser revisitada em favor de Aurora + pgvector, condicionado a uma mitigação explícita de implementação para compensar o comportamento post-filter (não como substituição automática — exige nova análise, não é decisão silenciosa).
- **Maior complexidade operacional relativa**: peça nova na stack, nenhuma demanda anterior desta casa operou OpenSearch — mitigado por ser serviço totalmente gerenciado (Serverless) e por estar coberto pela camada de orquestração Bedrock Knowledge Bases, que abstrai boa parte da interação direta com o motor de busca.
- **Vendor lock-in mais alto** entre as três opções (API/serviço específico da AWS) — aceito no mesmo espírito da decisão de provedor (ADR 012), mitigado pelo fato de a camada de aplicação (C2, C4, etc.) permanecer portável.
- **Números de custo não são cotação fechada** para `sa-east-1` — herdados de fonte pública de terceiro (mesma ressalva já registrada por Infraestrutura), precisam de validação por Estimativa de Custo com a calculadora oficial da AWS antes de qualquer compromisso.
- **Condicionado a duas confirmações pendentes**: orçamento (lacuna 2) e política de segurança/compliance concreta (lacuna 5) — esta última não deve mudar a escolha em si (todas as opções mantêm dado em `sa-east-1`), mas pode adicionar requisitos de configuração (ex.: criptografia específica) não avaliados nesta pesquisa.

## Coerência com o compêndio e ADRs anteriores
Nenhum ADR anterior desta casa trata de índice/busca vetorial — primeiro ADR desse tipo na casa. Coerente com a decisão de provedor já formalizada em ADR 012 (mesmo provedor e região, sem introduzir uma nova decisão de infraestrutura). Coerente com o compêndio seção 2 (MongoDB é padrão da casa, mas o próprio compêndio reconhece — via este processo — que a stack aprovada não resolve sozinha toda decisão técnica; onde não resolve, cabe pesquisa e ADR, não assunção por hábito). Não contradiz nenhuma decisão prévia; é a primeira vez que a casa avalia MongoDB Atlas Vector Search formalmente e opta por não usá-lo como primeira escolha — isso é uma decisão nova, não uma reversão de algo já decidido.

## Revisão
Pendente. Aguardando revisão explícita de pessoa sênior ou líder técnico do time antes de status mudar para "Aprovado".
