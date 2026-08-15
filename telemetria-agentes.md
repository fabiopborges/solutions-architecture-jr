# Telemetria dos Agentes

Registro contínuo de quanto o time de agentes gasta por demanda real. Mantido pelo agente [[agents/observabilidade-e-telemetria/AGENT]], frente 2. Quatro demandas rodaram até agora: a primeira simulada (um agente-modelo narrando os 14 papéis), a segunda, a terceira e a quarta via subagentes reais (`/arquiteto-solucoes`), com uso de token medido de verdade por agente.

## Formato de uma entrada
- Demanda:
- Por agente: tempo/tokens gastos, status ao terminar
- Loops de dúvida que bateram no limite de 3 rodadas e escalaram (se houver)
- Onde rodou em paralelo vs sequencial

## Entradas

### 2026-08-09 — sdr-2026-001-portal-digital-de-sinistros-e-upload-de-fotos

**Primeira demanda real a passar pela cadeia.** 14 dos 16 agentes acionados (todas as 14 atividades originais), os 2 especialistas sob demanda (Dados/Analytics e IA/ML) **não foram acionados**, corretamente, porque nenhum gatilho deles bateu nesta demanda, primeira validação real de que o critério de gatilho funciona sem ser acionado à toa.

**Por agente, status ao terminar:**
- Entendimento e Escopo: concluído, com 1 rodada de pergunta ao solicitante além do nome da demanda (prazo/orçamento).
- Desenho de Arquitetura: concluído, identificou 1 tensão (orçamento x padrão Kafka) e acionou Pesquisa e Benchmarking.
- Pesquisa e Benchmarking: concluído, recomendou desvio pontual do padrão da casa (fila gerenciada em vez de Kafka).
- Modelagem de Dados: concluído.
- Infraestrutura e Deployment: concluído, com 5 pendências explícitas listadas (preço região Brasil, custo VPN, entre outras).
- Testes e Qualidade: concluído, achou 1 requisito não atendido (Segurança, por dependência de atividade ainda não rodada) e 3 parciais.
- Segurança e Compliance: concluído, identificou 1 lacuna de produto nova (verificação de identidade) não coberta por nenhum agente anterior.
- Trade-offs e ADR: concluído, formalizou ADR 003, aprovado por Fabio Borges (Arquiteto de Soluções) em 2026-08-09.
- Estimativa de Custo: concluído, achado central: orçamento de US$ 150/mês projetado para ser insuficiente por volta do Ano 3.
- Observabilidade e Telemetria (frente 1): concluído.
- Documentação Final: concluído, ponto de sincronização, todos os 8 documentos de entrada confirmados presentes.
- Riscos e Mitigação: concluído, 8 riscos priorizados, todos com mitigação ou aceite explícito.
- Comunicação com Stakeholders: concluído.
- Entrega e Handoff: **preparado em 2026-08-09, liberado em 2026-08-09** após a Diretoria responder às duas perguntas de `apresentacao.md` (aprovação do orçamento com revisão futura, e definição do segundo fator de verificação de identidade). Portão de saída do Orquestrador completo, ciclo desta demanda fechado ponta a ponta.

**Loops de dúvida que bateram no limite de 3 rodadas:** nenhum. Observação honesta: esta rodada não exercitou o mecanismo literal de "agente pergunta a agente" (foi um único agente-modelo narrando todos os papéis em sequência), então o hook de escalonamento na 4ª rodada ainda não foi testado de verdade.

**Paralelo vs sequencial:** Entendimento → Desenho rodou sequencial (como desenhado). A partir do Desenho, Pesquisa, Modelagem de Dados, Infraestrutura e Testes e Qualidade são paralelizáveis entre si (mesma dependência, o Desenho), mas foram executados em sequência nesta conversa por serem conduzidos por um único agente-modelo, não por processos concorrentes de verdade. Isso é uma diferença real entre o desenho teórico do Orquestrador e esta primeira execução, vale registrar para quando houver paralelismo de execução de fato (múltiplos agentes rodando ao mesmo tempo).

---

### 2026-08-09 — sdr-2026-002-integracao-crm-serasa-mtls-jwt

**Primeira demanda rodada via `/arquiteto-solucoes` de verdade**, despachando os 16 subagentes registrados em `.claude/agents/` pela ferramenta de Task, não mais um único modelo narrando os papéis. **Primeira vez com custo de processamento medido de verdade por agente (Tier 2, antes tratado como trabalho futuro em `custo-processamento.md`)**, porque cada chamada de subagente retorna uso real da plataforma.

**Por agente, status e uso real (tokens, chamadas de ferramenta, duração):**
| Agente | Status | Tokens | Ferramentas | Duração |
|---|---|---|---|---|
| Entendimento e Escopo | concluído | 20.407 | 4 | 91s |
| Desenho de Arquitetura | concluído, sinalizou Pesquisa e Benchmarking | 33.065 | 7 | 157s |
| Modelagem de Dados | concluído (gravou no lugar errado na 1ª tentativa, ver bug abaixo) | 34.207 | 8 | 117s |
| Testes e Qualidade | concluído, achou 1 RNF não atendido e flagrou desvio não autorizado do padrão SOA/BPEL da casa | 35.585 | 7 | 138s |
| Pesquisa e Benchmarking | concluído, recomendação de cofre de segredos com preço real via WebSearch | 46.865 | 25 | 242s |
| Infraestrutura e Deployment | concluído, decisão de hospedagem em nuvem pública + AWS, 4 decisões sinalizadas para ADR | 60.008 | 13 | 269s |
| Segurança e Compliance | concluído | 34.049 | 5 | 132s |
| Trade-offs e ADR | concluído, 3 ADRs propostos (004, 005, 006), nenhum aprovado ainda | 37.790 | 10 | 132s |
| Estimativa de Custo | concluído, confirmou que cabe no teto mesmo no cenário pessimista, com margem menor que o otimista sugeria | 48.545 | 18 | 303s |
| Observabilidade e Telemetria (frente 1) | concluído | 37.526 | 5 | 122s |
| Documentação Final | concluído, ponto de sincronização, 12 documentos de entrada confirmados | 103.686 | 21 | 520s |
| Riscos e Mitigação | **1ª tentativa falhou** (erro de infraestrutura da API, stream interrompido, nada escrito), retry concluído | 81.077 | 11 | 158s |
| Comunicação com Stakeholders | concluído | 32.109 | 5 | 67s |
| Entrega e Handoff | concluído, **PREPARADO, aguardando aprovação humana**, não se autoaprovou | 41.911 | 7 | 71s |

**Total medido: 646.830 tokens** em 14 chamadas de subagente bem-sucedidas (mais 1 tentativa falha sem custo registrado). Isso é um número real de uso de tokens, não uma estimativa em dólar, a conversão para custo real em US$ depende da tabela de preço vigente (input/output/cache), que este agente não tem acesso confiável para converter sozinho, ver `custo-processamento.md` desta demanda.

**Especialistas sob demanda:** nenhum gatilho bateu (sem plataforma analítica, sem IA/ML), corretamente não acionados — segunda demanda seguida confirmando que o critério de gatilho não dispara à toa.

**Bug real encontrado e corrigido durante a execução:** o subagente de Modelagem de Dados resolveu o caminho relativo `demandas/...` contra a raiz real do projeto (`/home/fabioborges/projetos/os-agentes`), não contra `.claude/skills` onde vive o resto do OS, e gravou o artefato no lugar errado. O agente de Testes e Qualidade, despachado com a mesma instrução relativa, resolveu certo — não é falha sistemática, é ambiguidade real de resolução de caminho entre chamadas de subagente. Corrigido manualmente, e a skill `arquiteto-solucoes` foi atualizada para exigir caminho absoluto em todo despacho daqui pra frente (aplicado com sucesso em todos os despachos seguintes desta mesma demanda).

**Loop de dúvida entre agentes (3 rodadas → escalar):** ainda não exercitado literalmente (nenhum subagente re-perguntou a outro na mesma atividade 4 vezes), mas o mecanismo de "subagente pede revisão humana explicitamente" foi validado de verdade: o agente de Trade-offs e ADR terminou pedindo revisão humana dos 3 ADRs, e o Orquestrador (esta sessão) segurou isso para o final em vez de decidir sozinho.

**Paralelo vs sequencial, de verdade desta vez:** Entendimento → Desenho sequencial (dependência real). A partir do Desenho, Modelagem de Dados + Testes e Qualidade + Pesquisa e Benchmarking rodaram em paralelo de verdade (3 chamadas de Task na mesma mensagem, background). Depois, Infraestrutura e Deployment + Segurança e Compliance em paralelo. Depois, Trade-offs e ADR + Estimativa de Custo + Observabilidade em paralelo (3 ao mesmo tempo). Documentação Final e Riscos e Mitigação em paralelo. Isso é a primeira vez que o paralelismo desenhado em `agents/orquestrador/AGENT.md` foi exercitado com execução concorrente real, não simulada.

---

### 2026-08-10 — projeto-nuvem-vendas-v1

**Terceira demanda, primeira com um pedido genuinamente vago** (e-mail de duas linhas, sem nome de empresa, sem número real de prazo/orçamento). Testou a disciplina do Entendimento e Escopo de recusar inventar e forçar esclarecimento real antes de despachar qualquer outro agente. Também é a primeira demanda com **revisão de arquitetura no meio do caminho**: duas decisões do dono do produto (abandonar Kafka, aceitar réplica noturna de clientes) obrigaram a reabrir Desenho de Arquitetura e Modelagem de Dados já concluídos, e depois Segurança e Compliance de novo por causa de uma decisão de Infraestrutura (eliminação de VPN) que tornou parte do desenho de segurança obsoleta — Documentação Final pegou essa inconsistência sozinho, sem ninguém apontar.

**Por agente, status e uso real (tokens):**
| Agente | Execução | Tokens |
|---|---|---|
| Entendimento e Escopo | única, com round-trip humano real (problema, prazo, orçamento, contexto) | 18.901 |
| Desenho de Arquitetura | inicial + 1 revisão (sem Kafka, réplica noturna) | 33.527 + 52.130 |
| Modelagem de Dados | inicial + 1 revisão | 32.430 + 37.900 |
| Testes e Qualidade | inicial + 1 reavaliação pós-revisão | 32.807 + 62.011 |
| Pesquisa e Benchmarking (acesso ao Firebird) | única | 34.199 |
| Infraestrutura e Deployment | única (encontrou conflito de VPN e o resolveu sozinha, invertendo push→pull) | 98.471 |
| Segurança e Compliance | inicial + 1 revisão (pós-eliminação de VPN) | 44.765 + 55.148 |
| Trade-offs e ADR | 3 formalizações (ADR 007/008, ADR 009/010/011) + 2 atualizações de compêndio | 35.767 + 43.976 + 20.083 + 23.331 |
| Estimativa de Custo | única | 62.957 |
| Observabilidade e Telemetria (frente 1) | única | 57.278 |
| Riscos e Mitigação | inicial + 1 atualização (aceite do dono do produto) | 42.057 + 34.064 |
| Documentação Final | inicial + 1 reconciliação (segurança revisada) | 146.120 + 46.955 |
| Comunicação com Stakeholders | única | 39.363 |
| Entrega e Handoff | única, **PREPARADO, aguardando aprovação humana** | 47.114 |

**Total medido: 1.101.354 tokens.** Quase o dobro da demanda anterior (646.830), majoritariamente por causa do retrabalho real de revisão em cadeia (Desenho → Modelagem → Testes → Segurança), não desperdício: cada revisão foi disparada por uma decisão de negócio ou um achado real de outro agente, nunca repetição sem motivo.

**Especialistas sob demanda:** nenhum gatilho bateu novamente (app mobile foi tratado como visualização simples, não BI/analytics; nenhum modelo de IA/ML envolvido) — terceira demanda seguida confirmando que os dois especialistas não são acionados à toa.

**Achado de processo (não de arquitetura):** o ADR 003 (primeira demanda) estava aprovado desde 2026-08-09 mas nunca tinha sido resumido em `substrate/compendium.md` seção 3 — ficou pra trás numa reorganização de pastas anterior. Corrigido nesta sessão, antes de continuar a cadeia desta demanda, para não deixar o compêndio incoerente.

**Loop de dúvida / revisão em cadeia:** esta demanda foi a primeira a exercitar de verdade o padrão "decisão de negócio muda o meio da cadeia, agentes anteriores precisam ser reabertos", e a primeira em que um agente (Documentação Final) encontrou sozinho uma inconsistência entre dois documentos de origem produzidos em momentos diferentes (Segurança desatualizada em relação a uma decisão de Infraestrutura posterior) — o tipo de erro que um único prompt não estruturado dificilmente pegaria.

**Paralelo vs sequencial:** Entendimento → Desenho sequencial. A partir do Desenho, até 3 subagentes em paralelo (Modelagem, Testes, Pesquisa; depois Infraestrutura+Segurança; depois ADR+Custo+Riscos). A revisão de Desenho/Modelagem foi sequencial por necessidade (uma depende da outra). Documentação Final rodou duas vezes (sync real + reconciliação pontual).

---

### 2026-08-11 — plataforma-ia-corporativa-v1

**Quarta demanda, a de maior custo de token até agora (1.460.862, acima dos 1.101.354 da anterior)**, primeira a acionar o especialista sob demanda de IA/ML, e primeira com **mais paralelismo real desde o início**: logo após o Desenho de Arquitetura, 4 agentes foram disparados em paralelo na mesma rodada (Especialista em IA/ML, Modelagem de Dados, Infraestrutura e Deployment, Testes e Qualidade).

**Por agente, execução e uso real (tokens):**
| Agente | Execução | Tokens |
|---|---|---|
| Entendimento e Escopo | inicial + atualização com respostas humanas | 24.216 + 34.211 |
| Desenho de Arquitetura | inicial + revisão pós-qualidade | 40.624 + 66.155 |
| Especialista em IA/ML | 1 | 46.536 |
| Modelagem de Dados | 1 | 40.178 |
| Infraestrutura e Deployment | inicial + decisão fechada de mensageria (C7) | 74.399 + 59.314 |
| Testes e Qualidade | inicial + reavaliação pós-revisão | 40.481 + 110.847 |
| Pesquisa e Benchmarking (índice vetorial) | 1 | 84.156 |
| Trade-offs e ADR | ADRs 012-017 (6 ADRs) + verificação mensageria (recusada) + ADR-018 | 91.160 + 32.726 + 36.487 |
| Segurança e Compliance | 1 | 113.525 |
| Estimativa de Custo | inicial + reconciliação | 64.872 + 42.375 |
| Observabilidade e Telemetria (frente 1) | 1 | 79.984 |
| Documentação Final | 1 | 169.708 |
| Riscos e Mitigação | 1 | 113.363 |
| Comunicação com Stakeholders | 1 | 44.163 |
| Entrega e Handoff | 1 | 51.382 |

**Total medido: 1.460.862 tokens.** Ver detalhamento e leitura de custo em `demandas/plataforma-ia-corporativa-v1/custo-processamento.md`.

**Especialista sob demanda acionado pela primeira vez:** Especialista em IA/ML, corretamente, porque a demanda envolve modelo de IA de verdade — primeira confirmação real de que o gatilho dispara quando deveria, depois de três demandas seguidas confirmando apenas o caminho de não disparar à toa.

**Governança recusando inventar (não é loop de dúvida entre agentes, é recusa formal):** o agente de Trade-offs e ADR recebeu pedido para formalizar um ADR sobre decisão de mensageria e recusou, porque não havia decisão real registrada em nenhum documento de origem — 32.726 tokens gastos só nessa verificação, sem ADR nenhum ao final. Isso forçou um ciclo extra com Infraestrutura e Deployment para fechar a decisão de verdade (C7, 59.314 tokens) antes que o ADR-018 pudesse ser formalizado (36.487 tokens) com uma decisão real por trás. Primeira vez que esse mecanismo específico — recusa de formalização por falta de decisão real — foi exercitado de ponta a ponta nesta cadeia de demandas; não foi desperdício, foi a governança funcionando e evitando um ADR inventado.

**Revisão em cadeia:** Desenho de Arquitetura revisado após achado de Testes e Qualidade; Testes e Qualidade reavaliado depois dessa revisão; Estimativa de Custo reconciliada depois que a decisão de mensageria fechou. Mesmo padrão de retrabalho disparado por achado real, já visto em `projeto-nuvem-vendas-v1`.

**Paralelo vs sequencial:** Entendimento → Desenho sequencial (dependência real, com round-trip humano no meio do Entendimento). Logo após o Desenho, 4 agentes em paralelo real na mesma rodada (Especialista IA/ML, Modelagem de Dados, Infraestrutura, Testes e Qualidade) — o maior lote de paralelismo simultâneo registrado até agora nesta telemetria. Depois, revisão de Desenho → reavaliação de Testes sequencial por dependência. Trade-offs e ADR (ADRs 012-017), Segurança e Compliance e Estimativa de Custo rodaram em paralelo entre si. Documentação Final, Riscos e Mitigação, Comunicação com Stakeholders e Entrega e Handoff fecharam a cadeia.

**Custo real em US$/R$:** pendente, a preencher por quem operou a sessão — não estimado por este agente. Ver `demandas/plataforma-ia-corporativa-v1/custo-processamento.md`.
