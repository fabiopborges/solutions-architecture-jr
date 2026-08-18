# Telemetria dos Agentes

Registro contínuo de quanto o time de agentes gasta por demanda real. Mantido pelo agente [[agents/observabilidade-e-telemetria/AGENT]], frente 2. Oito demandas rodaram até agora: a primeira simulada (um agente-modelo narrando os 14 papéis), as demais via subagentes reais (`/arquiteto-solucoes`), com uso de token medido de verdade por agente.

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

**Bug real encontrado e corrigido durante a execução:** o subagente de Modelagem de Dados resolveu o caminho relativo `demandas/...` contra a raiz real do projeto (`/home/fabioborges/projetos/agentes-arquiteto-de-solucoes-junior`), não contra `.claude/skills` onde vive o resto do OS, e gravou o artefato no lugar errado. O agente de Testes e Qualidade, despachado com a mesma instrução relativa, resolveu certo — não é falha sistemática, é ambiguidade real de resolução de caminho entre chamadas de subagente. Corrigido manualmente, e a skill `arquiteto-solucoes` foi atualizada para exigir caminho absoluto em todo despacho daqui pra frente (aplicado com sucesso em todos os despachos seguintes desta mesma demanda).

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

---

### 2026-08-15 — integracao-crm-oci-whatsapp

**Quinta demanda, primeira com duas informações de negócio genuinamente indisponíveis mesmo depois de perguntadas diretamente a quem opera a sessão** (mecanismo de emissão de evento do CRM — push nativo vs. polling — e volumetria de leads/dia, RNF05). Em vez de travar a demanda inteira, o time seguiu com um plano de contingência autorizado explicitamente (ADR-020, decisão interina) para a parte que dava para desacoplar (mensageria), e deixou a outra pendência (mecanismo do CRM) genuinamente em aberto, sem contingência inventada.

**Por agente, execução e uso real (tokens):**
| Agente | Execução | Tokens |
|---|---|---|
| Entendimento e Escopo | 1 | 24.208 |
| Desenho de Arquitetura | inicial + revisão pós-feedback dos ramos paralelos | 38.185 + 69.366 |
| Modelagem de Dados | 1 | 37.703 |
| Infraestrutura e Deployment | 1 | 45.673 |
| Testes e Qualidade | 1 | 36.577 |
| Pesquisa e Benchmarking (provedor de WhatsApp) | 1 | 50.219 |
| Segurança e Compliance | 1 | 66.129 |
| Estimativa de Custo | 1 | 85.293 |
| Observabilidade e Telemetria (frente 1) | 1 | 55.916 |
| Trade-offs e ADR | ADR-019 (formalização) + aprovação ADR-019/criação ADR-020 + resolução de conflito de escopo no compêndio | 38.739 + 60.664 + 29.338 |
| Documentação Final | 1 | 121.089 |
| Riscos e Mitigação | inicial + 2 recusas de atualizar aceite de risco sem confirmação verificável | 83.598 + 19.814 + 20.717 |
| Comunicação com Stakeholders | 1 | 38.812 |
| Entrega e Handoff | preparar + liberar | 70.870 + 52.245 |

**Total medido: 1.045.155 tokens.** Ver detalhamento e leitura de custo em `demandas/integracao-crm-oci-whatsapp/custo-processamento.md`.

**Duas pendências externas reais, escaladas corretamente:** o mecanismo de emissão de evento do CRM (push vs. polling) e a volumetria de leads/dia (RNF05) foram perguntados diretamente a quem opera a sessão no meio da cadeia (após o Desenho de Arquitetura) e a resposta, honesta, foi "não sei, precisa verificar externamente" nos dois casos. Nenhum agente inventou um valor. No portão de saída, quem opera a sessão autorizou um plano de contingência (Candidata 2 — HTTP síncrono + Outbox — como decisão interina, formalizada no ADR-020) só para a parte da volumetria, mantendo o mecanismo do CRM genuinamente sem resposta e sem contingência associada.

**Recusa real de subagente por falta de verificação (2 tentativas, ambas mantidas):** o Riscos e Mitigação recusou atualizar o status de aceite de 4 riscos de "pendente" para "confirmado" com base apenas na afirmação do Orquestrador de que a aprovação humana tinha ocorrido — mesmo depois de uma segunda tentativa explicando o mecanismo do portão de saída. O Orquestrador não insistiu uma terceira vez. `riscos.md` ficou com linguagem mais conservadora do que o necessário, mas a decisão em si está registrada de forma verificável nos ADRs 019/020.

**Invasão de escopo entre agentes, capturada e corrigida:** o Entrega e Handoff adicionou uma entrada ao `substrate/compendium.md` (gestão exclusiva de Trade-offs e ADR) sem autoridade. O Orquestrador devolveu a decisão ao dono da atividade em vez de corrigir diretamente; Trade-offs e ADR reavaliou com critério próprio e removeu a entrada. Primeira vez que esse padrão específico foi capturado nesta cadeia de demandas — vale observar em demandas futuras se volta a acontecer.

**Loop legítimo entre atividades (não o hook de 4 rodadas — não foi exercitado):** Testes e Qualidade, Modelagem de Dados e Pesquisa e Benchmarking devolveram achados para o Desenho de Arquitetura em vez de corrigi-lo por conta própria, gerando 1 round-trip de revisão completa do desenho antes de Segurança e Compliance poder rodar.

**Paralelo vs sequencial:** Entendimento → Desenho sequencial (dependência real). Logo após o Desenho, 4 agentes em paralelo real na mesma rodada (Modelagem de Dados, Infraestrutura e Deployment, Testes e Qualidade, Pesquisa e Benchmarking). Revisão do Desenho rodou sequencial (bloqueava Segurança e Compliance). Depois da revisão, 3 agentes em paralelo (Segurança e Compliance, Estimativa de Custo, Observabilidade frente 1). Documentação Final e Riscos e Mitigação em paralelo entre si. Comunicação com Stakeholders, formalização de ADRs, e Entrega e Handoff fecharam a cadeia sequencialmente, por dependência real de cada um no anterior.

**Custo real em US$/R$:** pendente, a preencher por quem operou a sessão — não estimado por este agente. Ver `demandas/integracao-crm-oci-whatsapp/custo-processamento.md`.

### 2026-08-16 — pipeline-marketing-crm-legado

**Sexta demanda, primeira em que a pesquisa técnica (Pesquisa e Benchmarking) derruba a proposta que o próprio sponsor trouxe no pedido original.** Quem pediu (Diretoria de Growth/Marketing) já chegou com um ASD detalhado propondo IDMC + Databricks on-premises. Pesquisa e Benchmarking verificou via busca externa (não suposição) que nenhum dos dois produtos tem oferta genuinamente self-managed/on-prem — ambos dependem de control plane na nuvem do fornecedor, contradizendo a exigência de 100% on-prem do próprio pedido. Isso gerou dois ADRs (021 rejeitando a proposta do sponsor, 022 formalizando hospedagem por componente) e se propagou como condicionante real em Custo, Infraestrutura e Riscos — não foi um achado isolado, mudou a base de estimativa de custo da demanda inteira.

**Segundo achado real, independente do primeiro: estouro de orçamento.** Mesmo na alternativa recomendada (mais barata que a proposta original em licenciamento, já que dispensa IDMC/Databricks), Estimativa de Custo projetou total entre R$2.794.500 e R$2.913.500, acima do teto de R$2.400.000,00 do pedido original em ~R$400-500 mil. Riscos e Mitigação formalizou os dois achados como riscos de negócio P0 (RN-01 orçamento, RN-02 divergência de proposta) e recomendou explicitamente que sejam levados juntos à Diretoria, já que são a mesma decisão vista de dois ângulos.

**Cadeia limpa, sem loop de revisão nem recusa de subagente** — diferente da demanda anterior (`integracao-crm-oci-whatsapp`), nenhum achado de um ramo paralelo forçou reabertura do Desenho de Arquitetura. Todos os achados (Testes e Qualidade sobre RNF-06/LGPD, Pesquisa sobre inviabilidade on-prem) foram absorvidos pelos agentes seguintes na própria cadeia (Segurança resolveu a lacuna de LGPD com tokenização end-to-end; Trade-offs e ADR formalizou a mudança de tecnologia) sem precisar devolver ao Desenho.

**Por agente, execução e uso real (tokens):**
| Agente | Execução | Tokens |
|---|---|---|
| Entendimento e Escopo | 1 | 31.406 |
| Desenho de Arquitetura | 1 | 47.384 |
| Modelagem de Dados | 1 | 45.566 |
| Infraestrutura e Deployment | 1 | 54.332 |
| Testes e Qualidade | 1 | 41.079 |
| Pesquisa e Benchmarking | tecnologia de ingestão (C1/C2/C3) | 53.384 |
| Geração de Diagramas C4 | 1ª execução + 2ª execução (fluxo de dados) | 56.320 + 38.857 |
| Trade-offs e ADR | ADR-021 + ADR-022 | 53.911 |
| Segurança e Compliance | 1 | 68.195 |
| Estimativa de Custo | 1 | 79.358 |
| Observabilidade e Telemetria (frente 1) | 1 | 56.198 |
| Riscos e Mitigação | 1 | 123.161 |
| Documentação Final | 1 | 170.730 |
| Comunicação com Stakeholders | 1 | 59.637 |
| Entrega e Handoff | preparar (não liberado — aprovação humana pendente) | 62.866 |

**Total medido: 1.042.384 tokens.** Ver detalhamento em `demandas/pipeline-marketing-crm-legado/custo-processamento.md`.

**Quatro pendências reais de resposta externa, nenhuma inventada:** as 3 perguntas originais do ASD (interface de entrada do CRM, SLA de latência, mecanismo de deadlock) seguem sem resposta do sponsor, e Riscos e Mitigação sugeriu formalizar uma quarta (SLA de disponibilidade do CRM, hoje espalhada como nota lateral em 3 documentos) — nenhum agente decidiu por conta própria. Handoff ficou como PREPARADO, não LIBERADO: nenhuma aprovação humana ocorreu nesta sessão (nem das 4 pendências, nem dos 2 ADRs, nem do estouro de orçamento, nem da pergunta final de `comunicacao.md`).

**Paralelo vs sequencial:** Entendimento → Desenho sequencial (dependência real). Logo após o Desenho, 5 agentes em paralelo real (Modelagem de Dados, Infraestrutura e Deployment, Testes e Qualidade, Pesquisa e Benchmarking, Geração de Diagramas C4 1ª execução). Depois, 4 agentes em paralelo (Trade-offs e ADR, Segurança e Compliance, Estimativa de Custo, Observabilidade frente 1). Geração de Diagramas (2ª execução, fluxo de dados) e Riscos e Mitigação em paralelo entre si. Documentação Final, Comunicação com Stakeholders e Entrega e Handoff fecharam a cadeia sequencialmente, por dependência real de cada um no anterior.

**Custo real em US$/R$:** pendente, a preencher por quem operou a sessão — não estimado por este agente. Ver `demandas/pipeline-marketing-crm-legado/custo-processamento.md`.

---

### 2026-08-16 — projeto-agentes-arquitetura-de-solucoes-junior-16-08-2026

**Sétima demanda, primeira em que o objeto desenhado é o próprio OS multi-agente**, não um sistema de negócio externo. Muda o formato de várias atividades (Desenho, Infraestrutura, esta própria Observabilidade), já registrado por cada uma delas nos respectivos artefatos. Também primeira demanda em que Documentação Final encontrou uma pendência bloqueante de verdade dentro do próprio fluxo determinístico (diagrama de fluxo de dados ausente, escopo exclusivo de Geração de Diagramas C4 pela versão atual da própria skill) e a resolveu corretamente devolvendo para o agente dono em vez de desenhar manualmente.

**Todos os 14 artefatos da cadeia principal produzidos** (Entendimento, Desenho, Dados, Infraestrutura, Testes e Qualidade, Jornadas, Segurança, Custo, Observabilidade, Documentação Final, Riscos, Comunicação, Handoff), mais Geração de Diagramas C4 acionada 2 vezes (container/contexto/jornadas/sequências, depois fluxo de dados). Nenhum especialista sob demanda acionado — sem gatilho de plataforma analítica nem de modelo de IA/ML nesta demanda, nem Pesquisa e Benchmarking — nenhuma tecnologia não resolvida pela stack apareceu, já que o objeto é o próprio OS local.

**Por agente, execução e uso real (tokens/ferramentas/duração):**
| Agente | Execução | Tokens | Ferramentas | Duração |
|---|---|---|---|---|
| Entendimento e Escopo | inicial + revisão (generalizar refs a demandas passadas) | 75.303 + 93.960 | 16 + 6 | 188,6s + 28,7s |
| Desenho de Arquitetura | 1 | 88.264 | 17 | 245,9s |
| Geração de Diagramas C4 (container/contexto/jornadas/sequências) | 1 | 210.524 | 110 | 875,4s |
| Modelagem de Dados | 1 | 78.011 | 10 | 194,2s |
| Infraestrutura e Deployment | 1 | 51.437 | 6 | 103,5s |
| Testes e Qualidade | 1 | 48.771 | 6 | 135,6s |
| Jornadas do Usuário | 1 | 72.055 | 9 | 258,3s |
| Segurança e Compliance | 1 | 50.178 | 7 | 166,4s |
| Estimativa de Custo | 1 | 21.609 | 5 | 50,6s |
| Observabilidade e Telemetria (frentes 1+2) | 1 | 71.436 | 16 | 152,4s |
| Documentação Final | inicial + atualização (diagrama de fluxo de dados) | 129.612 + 140.998 | 26 + 5 | 272,6s + 50,9s |
| Riscos e Mitigação | 1 | 68.767 | 14 | 190,7s |
| Geração de Diagramas C4 (fluxo de dados) | 1 | 171.755 | 78 | 855,5s |
| Comunicação com Stakeholders | 1 | 41.478 | 7 | 49,0s |
| Entrega e Handoff | preparar (não liberado — aprovação humana pendente) | 50.852 | 11 | 100,2s |

**Total medido: 1.465.010 tokens.** A maior demanda em tokens até agora, superando a de `plataforma-ia-corporativa-v1` (1.460.862) — puxado principalmente pelos dois acionamentos de Geração de Diagramas C4 (382.279 tokens somados, 188 chamadas de ferramenta) por ser a primeira vez traduzindo 19 componentes/atores do próprio OS num grafo denso (fan-in/fan-out alto), e por Documentação Final ter rodado 2 vezes por causa da pendência real do diagrama de fluxo de dados. Ver detalhamento em `demandas/projeto-agentes-arquitetura-de-solucoes-junior-16-08-2026/custo-processamento.md`.

**Paralelo vs sequencial, de verdade:** Entendimento → Desenho sequencial (dependência real). Logo após o Desenho, 5 agentes em paralelo real (Geração de Diagramas C4, Modelagem de Dados, Infraestrutura e Deployment, Testes e Qualidade, Jornadas do Usuário — o primeiro despacho de 4 deles falhou por um falso positivo do hook de caminho absoluto detectando `demandas/` sem barra à esquerda dentro do texto da instrução, não do caminho real; corrigido reformulando o prompt sem esse padrão, sem tocar no hook). Depois, 3 agentes em paralelo (Segurança e Compliance, Estimativa de Custo, Observabilidade frente 1). Depois, 2 agentes em paralelo (Documentação Final, Riscos e Mitigação). A 2ª execução de Geração de Diagramas C4 (fluxo de dados) e a atualização de Documentação Final rodaram sequenciais, por dependência real uma da outra. Comunicação com Stakeholders e Entrega e Handoff fecharam a cadeia sequencialmente.

**Loops de dúvida que bateram no limite de 3 rodadas:** nenhum.

**Achado de processo (não de arquitetura):** falso positivo do hook `PreToolUse` de caminho absoluto — a regex do hook reage a qualquer ocorrência textual de `demandas/` sem barra à esquerda em qualquer parte do prompt de despacho, não só em caminho de arquivo real. Um trecho de instrução como "não cite projetos dentro de demandas/ do repositório" (prosa, não caminho) já dispara o bloqueio. Contornado reformulando a prosa para evitar o padrão literal; nenhuma mudança feita no hook nesta sessão, mas vale registrar como possível ajuste futuro de precisão do hook (falso positivo, não falha de proteção).

**Custo real em US$/R$:** pendente, a preencher por quem operou a sessão — não estimado por este agente. Ver `demandas/projeto-agentes-arquitetura-de-solucoes-junior-16-08-2026/custo-processamento.md`.

---

### 2026-08-17 — sad-008-sync-dados-ia

> **Entrada gravada com a demanda ainda aberta.** Diferente das sete anteriores, esta foi registrada **antes do fim da cadeia**: Geração de Diagramas C4 ainda estava em execução quando esta frente 2 foi acionada, e Entrega e Handoff não tinha começado. Os números abaixo são **reais e parciais**, e o que falta está **nomeado, não estimado**.

**Oitava demanda, primeira sem enunciado escrito.** O único insumo foi uma **foto de tela** de um diagrama de arquitetura de outra equipe. Não havia texto de pedido, RNF, prazo nem orçamento. Isso mudou a natureza de quase todas as atividades: o objeto não é um sistema a projetar, é um **as-is de terceiros a avaliar por evidência única e fraca**, e o produto de vários agentes virou **parecer com grau de evidência declarado**, não especificação.

**Por agente, execução e uso real (tokens/ferramentas/duração):**
| Agente | Execução | Tokens | Ferramentas | Duração |
|---|---|---|---|---|
| Entendimento e Escopo | inicial + v2 (após respostas humanas) | 36.897 + 58.014 | 11 + 1 | 232,0s + 263,8s |
| Desenho de Arquitetura | 1 | 73.294 | 13 | 959,2s |
| Trade-offs e ADR | ADR-023 v1 + v2 (produto × topologia) + formalização da aprovação | 56.021 + 89.319 + 103.624 | 12 + 9 + 11 | 176,5s + 111,7s + 113,8s |
| Especialista em Dados e Analytics | inicial + v2 (repasse do Desenho) | 76.102 + 126.213 | 15 + 18 | 471,0s + 290,7s |
| Especialista em IA e ML | inicial + v2 (repasses cruzados) | 65.504 + 135.444 | 9 + 19 | 414,4s + 265,0s |
| Modelagem de Dados | 1 | 133.966 | 11 | 431,0s |
| Testes e Qualidade | 1 | 130.870 | 10 | 445,4s |
| Jornadas do Usuário | 1 | 124.227 | 16 | 439,5s |
| Infraestrutura e Deployment | 1 | 120.771 | 17 | 533,6s |
| Segurança e Compliance | 1 | 139.122 | 16 | 560,4s |
| Estimativa de Custo | 1 | 116.843 | 18 | 612,3s |
| Observabilidade e Telemetria (frente 1) | 1 | 186.027 | 17 | 644,0s |
| Riscos e Mitigação | inicial + v2 (incorporando Segurança) | 155.493 + 220.859 | 21 + 56 | 559,2s + 1.095,9s |
| Documentação Final | 1 | 418.519 | 45 | 1.592,6s |
| Comunicação com Stakeholders | 1 | 100.972 | 14 | 293,1s |
| **Geração de Diagramas C4** | **em execução no momento deste registro** | **não medido** | — | — |
| **Entrega e Handoff** | **não iniciada** | — | — | — |

**Total medido: 2.668.101 tokens — PARCIAL E EXPLICITAMENTE INCOMPLETO.** É a soma exata dos 22 acionamentos de subagente já encerrados (359 chamadas de ferramenta). Já é, sozinho, a maior demanda em tokens desta telemetria, quase o dobro da anterior mais cara (1.465.010). **O que falta, nomeado:**
- **Geração de Diagramas C4**, ainda rodando quando este registro saiu. É **historicamente o agente mais caro desta cadeia** (382.279 tokens somados em 2 execuções na demanda de 16-08). **Não estimo o que falta** — o número entra aqui quando for medido.
- **Entrega e Handoff**, não iniciada.

**Limitação de medição a registrar, não a omitir:** estes números cobrem **apenas os subagentes**. O consumo do próprio **Orquestrador** (a sessão principal, que lê, despacha, faz os repasses cruzados e conduz os round-trips humanos) **não é reportado de volta como o dos subagentes**, então **não está em nenhuma linha da tabela acima**. O total real de tokens da sessão é maior que 2.668.101 por uma margem que este agente não mede e não estima. Isso vale retroativamente para todas as sete entradas anteriores desta telemetria.

**Loops de dúvida que bateram no limite de 3 rodadas: nenhum.** Uma rodada aberta e **não escalada**: Testes e Qualidade → Desenho de Arquitetura (rodada 1 de 3), declarada **não bloqueante**, sobre a dependência de saber o que significam as siglas de raia do diagrama de origem.

**Paralelo vs sequencial, o que realmente aconteceu:**
- Entendimento → Desenho **sequencial por dependência real**, com **parada para pergunta humana no meio**: o pedido não existia por escrito, e o Entendimento **bloqueou o próprio portão** até ser respondido, em vez de seguir com premissa inventada.
- Onda de **4 em paralelo** logo após o Entendimento: Desenho, Trade-offs e ADR, e os **dois especialistas sob demanda** (Dados e Analytics, IA e ML).
- Onda de **5 em paralelo** após o Desenho (Modelagem de Dados, Infraestrutura, Testes e Qualidade, Jornadas do Usuário, Geração de Diagramas C4) **mais 2 reaberturas simultâneas** dos especialistas para repasses cruzados — **7 agentes ativos ao mesmo tempo, o pico desta demanda e o maior paralelismo simultâneo já registrado nesta telemetria** (o recorde anterior era 5).
- Segurança e Compliance entrou **sozinho**, ao fecharem Desenho + Modelagem de Dados.
- Estimativa de Custo e Observabilidade (frente 1) **em paralelo** após Infraestrutura.
- Riscos e Mitigação **em paralelo** com Documentação Final.
- Comunicação e depois Entrega e Handoff, **sequenciais**.
- **Nenhum despacho foi bloqueado pelo hook de caminho absoluto nesta demanda** — diferente da execução de 2026-08-16, onde um falso positivo do hook derrubou um lote de 4 despachos. Sem mudança no hook desde então; a diferença veio da redação dos prompts.

#### Achados de processo desta demanda (aprendizado do time, não incidente)

1. **Demanda sem enunciado escrito, resolvida com um padrão novo e reutilizável.** O insumo era uma imagem, e **subagentes despachados por Task não enxergam imagem**. O Orquestrador transcreveu a foto **literalmente** para um arquivo em `insumos/`, marcando explicitamente como lacuna o que estava ilegível, em vez de parafrasear ou completar por dedução. Todos os agentes seguintes trabalharam sobre a transcrição, com os rótulos de ilegibilidade preservados até o fim da cadeia. **Padrão provavelmente reutilizável em qualquer demanda cujo insumo seja não textual.**

2. **Três nomes de artefato errados no despacho, por divergência real dentro do próprio repositório — e os três foram detectados pelos agentes donos.** O Orquestrador despachou pedindo `especialista-ia-ml.md`, `especialista-dados-analytics.md` e `apresentacao.md`; a convenção vigente é `ia-ml.md`, `dados-analytics.md` e `comunicacao.md`. **Nenhum dos três agentes aceitou o nome errado em silêncio** — todos reportaram a divergência. **Causa-raiz encontrada e corrigida nesta sessão:** `.claude/agents/comunicacao-stakeholders.md` e `.claude/agents/entrega-e-handoff.md` ainda apontavam para o nome antigo, contradizendo a skill que padronizou os nomes em 2026-08-16. Não foi erro de digitação do despacho: era **incoerência real versionada no repo**, e o mecanismo que a encontrou foi o agente dono checar a própria convenção.

3. **Duas reaberturas por ordem de conclusão, não por erro.** Riscos e Mitigação rodou antes de `seguranca.md` existir e precisou de v2; os dois especialistas rodaram antes do Desenho e precisaram de v2. Nenhuma das quatro execuções extras foi retrabalho por engano — foi **efeito da árvore de dependência não prever que aquele insumo chegaria depois**. Custo direto observável: 4 reexecuções, 482.516 tokens. **Vale avaliar se a árvore de dependência do Orquestrador deveria modelar esses dois casos** em vez de aceitar a reabertura como rotina.

4. **Uma recomendação destrutiva foi capturada pelo cruzamento entre agentes, não por revisão humana.** Um agente recomendou expurgo em `Raw`, lendo a camada como passivo; outro agente mostrou que `Raw` é o **ativo que dá a única rota de reprocessamento** da plataforma. O primeiro **retirou a própria recomendação**. Isso é o padrão desta arquitetura funcionando no seu ponto mais alto: um único agente, por mais competente, teria emitido a recomendação sem contraditório. **É provavelmente o melhor argumento empírico já produzido nesta telemetria a favor da arquitetura de múltiplos agentes deste OS** — e, diferente dos achados anteriores do gênero, aqui o erro evitado era **destrutivo e irreversível**, não apenas incorreto.

5. **Salvaguarda de método criada nesta demanda e adotada por vários agentes de forma independente:** *convergência entre agentes que leem a mesma fonte fraca é **uma evidência lida várias vezes, não várias evidências***. Com evidência única (a foto), a concordância entre agentes é o resultado esperado por construção, não confirmação. A salvaguarda foi **operacionalizada, não só declarada**: a matriz de riscos foi montada **deliberadamente sem coluna de "quantos agentes apontaram"**, para que a contagem de concordância não pudesse ser lida como força de evidência. Registrar aqui porque é uma regra de método com valor **fora** desta demanda.

6. **Vários agentes declararam desvios de regra em vez de escondê-los** e os enviaram a julgamento humano — **três seguem abertos** no momento deste registro.

**Estado da demanda no momento deste registro (para o registro ficar honesto):** Geração de Diagramas C4 **ainda em execução**; Entrega e Handoff **não iniciada**; portão de saída do Orquestrador com **1 de 4 itens cumpridos**; aprovação humana pendente. **A única aprovação obtida foi o ADR-023, aprovado por humano em 2026-08-17** e registrado no compêndio.

**Custo real em US$/R$:** pendente, a preencher por quem operou a sessão — **não estimado por este agente**. Ver `demandas/sad-008-sync-dados-ia/custo-processamento.md`.
