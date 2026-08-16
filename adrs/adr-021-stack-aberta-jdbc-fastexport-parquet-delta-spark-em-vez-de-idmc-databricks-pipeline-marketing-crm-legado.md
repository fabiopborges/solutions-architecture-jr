# ADR 021 — Stack aberta (JDBC FastExport + Parquet/Delta OSS + Apache Spark self-managed) em vez de IDMC + Databricks para ingestão/processamento

## Status
**Proposto.** Aguardando revisão de uma pessoa sênior ou líder técnico do time. Não vale como decisão oficial até essa revisão acontecer — este ADR, assim como qualquer outro, não é auto-aprovável pelo agente que o escreveu.

## Demanda de origem
`demandas/pipeline-marketing-crm-legado/`. Decisão tomada por Pesquisa e Benchmarking (`pesquisa-tecnologia-ingestao.md`), acionado por Desenho de Arquitetura (`desenho.md`, seção 0.1 e seção 6, encaminhamento 1) para resolver a tecnologia dos componentes `c1_extrator_marketing`, `c2_stage_bruto` e `c3_motor_qualificacao`, não coberta pela stack aprovada nem por ADR prévio.

## Aviso explícito: isto não é um ajuste, é uma substituição da proposta trazida pelo sponsor

Quem pediu propôs, no pedido original (registrado em `entendimento.md` e retomado em `desenho.md` seção 0.1), uma tecnologia fechada e nomeada para o núcleo do pipeline: **IDMC (Informatica Intelligent Data Management Cloud)** para orquestração/conectividade/entrega, e **"Databricks on-premises"** para o processamento pesado (deduplicação, limpeza, cálculo de propensão). Este ADR **rejeita essa proposta como decisão fechada** e formaliza uma alternativa diferente, construída sobre a stack já aprovada da casa. Não se trata de uma variação ou de um refinamento do que foi pedido — é a substituição da tecnologia nomeada no ASD por outra, com justificativa técnica de inviabilidade, não de preferência.

## Contexto / problema

A demanda exige extrair 50 milhões de registros/dia do Teradata (upsert incremental, sem competir por lock com consultas analíticas de origem — RF-01/RF-02), fazer staging em formato que suporte checkpoint/retomada (RF-07), e processar esse volume de forma distribuída (deduplicação em massa, limpeza, padronização, propensão) com a menor latência possível (RNF-01/RNF-02). Nenhuma peça da stack aprovada (`substrate/compendium.md` seção 1: Java/Spring Boot, Python, Node.js, MongoDB, Kafka via AMQ Streams) resolve, por si só, conector de alta performance para Teradata, formato/motor de staging colunar, ou motor de processamento distribuído para deduplicação em massa — daí a necessidade de pesquisa dedicada.

A restrição de negócio inegociável desta demanda, herdada de `entendimento.md` (SUP-04/RNF-09) e reafirmada por `desenho.md` (seção 0.2) e por `infraestrutura.md`: **100% on-premises**, por decisão de negócio deliberada (dado sensível + sistemas legados on-prem), não restrição orçamentária. Qualquer tecnologia avaliada precisa atender a essa restrição sem exceção para o dado sensível em trânsito.

## Achado técnico central que motiva a rejeição da proposta original

Uma busca dedicada (`pesquisa-tecnologia-ingestao.md`, seção 3) checou, e não assumiu, se IDMC e Databricks têm oferta genuinamente self-managed/on-premises hoje (2026). O achado é factual, não interpretativo:

- **Databricks:** não existe pacote instalável e operado inteiramente dentro do datacenter do cliente. A plataforma roda como serviço gerenciado sobre nuvem pública (AWS/Azure/GCP); o control plane é sempre hospedado pela Databricks. O que existe é conectividade a dados on-premises via parceiros de storage, não o motor de processamento operando on-prem.
- **IDMC:** a plataforma é SaaS cloud-only. A conectividade on-premises é feita via Secure Agent, um runtime instalado no ambiente do cliente que executa tarefas localmente, mas recebe instruções/configuração de um control plane hospedado na nuvem da Informatica.

Fontes checadas em `pesquisa-tecnologia-ingestao.md` seção 3 (Databricks: "Databricks On-Premise: Real Options in 2026" — Definite; comunidade oficial Databricks; blog oficial Databricks sobre ecossistema de storage. IDMC: documentação oficial Informatica sobre arquitetura IDMC e Secure Agents/Runtime Environments).

**Consequência direta:** a proposta original, lida literalmente ("Databricks on-premises"), descreve algo que o fornecedor não vende dessa forma hoje. Seguir com IDMC/Databricks como decisão fechada significaria aceitar, conscientemente, dependência de control plane em nuvem de terceiro exatamente para `c3_motor_qualificacao` — o componente de maior sensibilidade de dado do pipeline, que processa dado pessoal de cliente pré-CRM. Isso contradiz diretamente RNF-09/SUP-04 (100% on-prem como decisão de negócio, não orçamentária) e reabriria, sem necessidade, a tensão de compliance/LGPD que `desenho.md` (seção 0.2) já registrou como pendente de avaliação formal de Segurança/InfoSec.

## Alternativas consideradas e por que foram descartadas

Três pacotes tecnológicos coerentes foram comparados (cada um cobrindo C1+C2+C3 como conjunto, por não fazer sentido misturar peças de pacotes diferentes sem justificar), sob sete critérios: (1) aderência real a 100% on-prem, (2) aderência à stack aprovada, (3) maturidade/throughput para 50M/dia, (4) custo dentro do teto RNF-07 (R$ 2,4M), (5) prazo compatível com RNF-08 (MVP mês 4, produção mês 6), (6) cobertura nativa de resiliência (RF-07/RF-08/RF-09) e linhagem (RF-11), (7) vendor lock-in.

- **Opção A — IDMC + Databricks (proposta original do sponsor).** C1/C2 via IDMC (conectores Teradata FastExport/Parallel Transporter, staging em Parquet/Delta); C3 via Databricks (Spark gerenciado). **Descartada por falha estrutural no critério 1 (não-negociável para esta demanda):** control plane cloud-hospedado de ambas as ferramentas contradiz verificadamente RNF-09/SUP-04, não é questão de preferência. Além disso, o custo de licenciamento (IPU para IDMC, DBU para Databricks) não pôde ser confirmado publicamente para o volume de 50M registros/dia em regime on-prem/híbrido sem cotação comercial direta — risco real de comprometer o teto de RNF-07 sem esse número. A Opção A é desqualificada pelo critério 1 sozinho, antes mesmo de entrar em custo.
- **Opção C — Apache NiFi (ingestão/orquestração) + Apache Spark (processamento), ambos on-prem/open source.** Atende ao critério 1 (100% on-prem, self-managed). Descartada por perder para a Opção B nos critérios 2 e 5: introduz uma plataforma inteira nova (NiFi) que o time não opera hoje, dentro de um prazo apertado de 6 meses com MVP no mês 4 (RNF-08) — risco de prazo maior sem ganho líquido correspondente, já que parte do ganho de NiFi em linhagem/backpressure nativos (critério 6) já é coberta por peças que a arquitetura vai construir de qualquer forma (C4 Kafka/AMQ Streams para backlog/circuit breaker, C6 para DLQ, C7/MongoDB para linhagem, todos já decididos em `desenho.md`).

## Decisão

Adotar a **Opção B — stack aberta sobre a stack aprovada da casa**, especificamente:

- **`c1_extrator_marketing`:** driver **JDBC do Teradata com suporte a FastExport** (extração paralela nativa do Teradata), implementado em Java ou Python (stack aprovada), sem depender de ferramenta de orquestração comercial.
- **`c2_stage_bruto`:** arquivos **Parquet** ou **Delta Lake open source** (formato mantido pela Linux Foundation, não exige Databricks para ser lido/escrito) em storage on-prem.
- **`c3_motor_qualificacao`:** **Apache Spark standalone/self-managed** em cluster on-prem — o mesmo motor de processamento que roda sob o capô do Databricks, operado diretamente pelo time, sem camada comercial por cima.
- Entrega para `c4_buffer_backlog_entrega` continua via Kafka/AMQ Streams, já decidido em `desenho.md` e fora do escopo desta pesquisa.

Motivo, direto pelos critérios que mais pesam para esta demanda: o critério 1 (100% on-prem) é o que mais pesa porque é restrição de negócio deliberada, não orçamentária (SUP-04) — a Opção A falha nele de forma factual e verificável, o que já a desqualifica antes de qualquer comparação de custo. Entre B e C, que ambas atendem ao critério 1, a Opção B vence por aderência à stack já operada pelo time e menor risco de prazo dentro da janela de RNF-08, sem perda de maturidade de processamento (Spark é o mesmo motor por trás do próprio Databricks, só sem a camada comercial que falha o critério 1).

## Consequências / trade-offs aceitos conscientemente

- **Mais esforço de engenharia própria.** A Opção B exige construir o conector Teradata (JDBC/FastExport) e os jobs Spark do zero, em vez do que a Opção A traria pronto (conectores nativos, garantia de entrega gerenciada). Isso é aceito conscientemente em troca de atender à restrição on-prem não-negociável.
- **Checkpoint/DLQ/circuit breaker (RF-07/RF-08/RF-09) não vêm "de fábrica".** Precisam ser construídos como parte do desenho de C4/C5/C6 (já cobertos por Kafka/AMQ Streams em `desenho.md`), diferente da Opção A, onde garantia de entrega é proposta de valor nativa da plataforma comercial.
- **Realinhamento de expectativa de custo/prazo com quem pediu é necessário e não está resolvido por este ADR.** O orçamento (RNF-07) e o prazo (RNF-08) do sponsor foram dimensionados pensando em IDMC/Databricks (risco já registrado como RISCO-06 em `entendimento.md` e retomado em `desenho.md` seção 0.1). Rejeitar a proposta original tem custo real de alinhamento de expectativa com quem pediu — esse realinhamento cabe às atividades de Custo/Infraestrutura e à conversa direta com o sponsor, não a este ADR nem à pesquisa que o originou.
- **Baixo vendor lock-in ganho como benefício colateral.** JDBC, Parquet/Delta (formato aberto) e Spark (Apache, open source) são portáveis, ao contrário da Opção A (duas plataformas comerciais fechadas com formato de fluxo/job proprietário).
- **Risco assumido:** o time hoje não opera Spark em produção em escala self-managed; ainda que a curva de aprendizado seja menor que a de duas plataformas comerciais novas (IDMC + Databricks), não é zero. Dimensionamento de capacidade de cluster Spark para 50M registros/dia é entregável obrigatório antes da Fase 2 (produção completa), conforme já sinalizado por `desenho.md` (risco R6).

## Checagem de conflito com compêndio / ADRs anteriores
Conferido `substrate/compendium.md` seção 3 antes de escrever este ADR: nenhum ADR anterior trata de tecnologia de ingestão/processamento de dados em massa (ETL/engenharia de dados) ou de ferramentas equivalentes a IDMC/Databricks/Spark. Não há contradição com decisão prévia registrada. Este ADR reforça, e não contradiz, o padrão geral da casa (seção 1 do compêndio: reaproveitar stack aprovada quando possível) e a lógica de ADR 008 (preferir solução construída sobre a stack já operada pelo time frente a ferramenta comercial nova, quando o critério estrutural da demanda permitir).

## Quem revisou
Nenhuma pessoa sênior ou líder técnico revisou este ADR ainda. **Status permanece "Proposto" até essa revisão ocorrer.** Pergunta direta para quem está operando a sessão: por favor, revise esta decisão (rejeição formal da proposta técnica do sponsor, IDMC + Databricks, em favor de JDBC FastExport + Parquet/Delta OSS + Apache Spark self-managed) antes que ela seja tratada como oficial.
