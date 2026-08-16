# ADR 022 — Hospedagem majoritariamente on-premises por componente, com exceção única de MongoDB Atlas (AWS sa-east-1) para o Catálogo de Linhagem

## Status
**Proposto.** Aguardando revisão de uma pessoa sênior ou líder técnico do time. Não vale como decisão oficial até essa revisão acontecer.

## Demanda de origem
`demandas/pipeline-marketing-crm-legado/`. Decisão tomada por Infraestrutura e Deployment (`infraestrutura.md`), a partir das restrições de negócio já sinalizadas por Desenho de Arquitetura (`desenho.md`, seção 0.2) e por Entendimento e Escopo (`entendimento.md`, SUP-04/RNF-09/RNF-06).

## Contexto / problema

O compêndio (`substrate/compendium.md` seção 1, ADR 001) fixa cloud como agnóstica de provedor por critério de negócio a cada demanda — nenhum provedor, nem topologia, é assumido de antemão. O pedido original desta demanda assumiu 100% on-premises e o orçamento (RNF-07) foi alocado pensando em "infraestrutura on-prem". `desenho.md` (seção 0.2) registrou essa tensão sem resolvê-la, delegando a Infraestrutura e Deployment a decisão final de topologia/provedor por componente, componente a componente, usando critério de negócio real (não hábito) — especificamente porque, para alguns componentes, "nenhum provedor, fica on-prem" é a resposta correta quando a restrição de proximidade física com Teradata/CRM Legado é factual, não preferência.

Este ADR formaliza essa decisão, componente a componente, para os sete componentes canônicos definidos em `desenho.md` seção 3.

## Alternativas consideradas e por que foram descartadas (por componente/grupo)

Para os seis componentes do caminho crítico (`c1`, `c2`, `c4`, `c5`, `c6`) e para `c3` nesta fase, a alternativa considerada foi hospedagem em cloud pública (qualquer provedor). Foi descartada com o mesmo raciocínio de fundo, aplicado a cada componente:

- **`c1_extrator_marketing` e `c5_gateway_entrega_crm`** tocam diretamente Teradata e CRM Legado, respectivamente — ambos on-prem, ambos com regra explícita de não degradar performance operacional (RF-01, RNF-03) e, no caso de `c5`, risco direto de deadlock contra um SoR transacional rígido (PEN-03, R3). Hospedar esses dois componentes fora do datacenter local introduziria latência de rede (hop de WAN) exatamente onde a restrição de negócio é não competir por lock/degradar o sistema de origem/destino. Cloud pública foi descartada por essa restrição factual de latência/data gravity, não por preferência.
- **`c2_stage_bruto`** foi descartada em cloud como consequência direta de `c1` (que grava) e `c3` (que lê, nesta fase) estarem on-prem: mover 50M registros/dia de lote bruto para cloud e trazer de volta geraria custo de egress/ingress recorrente e nova janela de latência, sem ganho compensador, já que nem origem nem consumidor primário estão em cloud.
- **`c4_buffer_backlog_entrega`** foi descartada em cloud porque fica entre `c3` (on-prem nesta fase) e `c5` (on-prem obrigatório) — hospedar em cloud adicionaria dois saltos de rede extras no caminho crítico de entrega ao CRM, contra RNF-02 (menor latência) e RNF-03 (o circuit breaker de `c5` precisa medir latência com precisão; um hop adicional só piora a variabilidade).
- **`c6_dlq_rejeitos`** foi descartada em cloud pela mesma lógica de coerência de topologia com `c5`, componente que a alimenta diretamente (RF-08).
- Para **`c3_motor_qualificacao`**, a alternativa cloud foi avaliada com mais profundidade (é o componente de maior liberdade e maior ganho técnico potencial de elasticidade — burst de compute para os picos diários de 50M registros, mitigando o risco R6 de gargalo já registrado em `desenho.md`). Foi descartada **nesta fase**, não descartada em definitivo — ver seção "Condição de revisão futura" abaixo.
- Para **`c7_catalogo_linhagem`**, a alternativa on-premises (MongoDB self-managed local, coerente com os demais componentes) foi considerada e descartada em favor de serviço gerenciado: `c7` é cross-cutting, consumido de forma assíncrona (fire-and-forget) por `c1`, `c3` e `c5` (RF-11/RNF-06), sem restrição de proximidade física equivalente à de `c1`/`c5` — não compete com o caminho crítico de entrega ao CRM. Hospedar `c7` on-prem também traria carga operacional adicional a uma equipe de infraestrutura já sob pressão cuidando de seis outros componentes on-prem.

Para `c7`, entre os provedores de cloud avaliados para hospedar o MongoDB Atlas (AWS `sa-east-1`, Azure Brazil South, GCP `southamerica-east1` — todos atendem ao requisito de região/residência de dado no Brasil), AWS `sa-east-1` foi escolhida por ser a região com maior presença física entre os hyperscalers no Brasil (5 datacenters na região metropolitana de São Paulo, confirmado via busca), critério decisivo dado que `c7` referencia identificadores de cliente (RF-11/RNF-06) e residência de dado em território nacional é o critério que mais pesa aqui.

## Decisão

Hospedagem e provedor por componente:

| Componente | Hospedagem | Provedor | Natureza da decisão |
|---|---|---|---|
| `c1_extrator_marketing` | On-premises, mesma rede/datacenter do cluster Teradata | Nenhum | Restrição física real (latência/data gravity), não orçamentária |
| `c2_stage_bruto` | On-premises, colocado com `c1` e `c3` | Nenhum | Consequência direta da hospedagem de `c1`/`c3` |
| `c3_motor_qualificacao` | On-premises **nesta fase** | Nenhum, nesta fase | **Condicional — ver seção de contingência abaixo. Não é decisão fechada em definitivo.** |
| `c4_buffer_backlog_entrega` | On-premises (Kafka/AMQ Streams) | Nenhum | Coerência de topologia com vizinhos diretos do fluxo (`c3`, `c5`) |
| `c5_gateway_entrega_crm` | On-premises, mesma rede do CRM Legado | Nenhum | Restrição física inegociável — escrita direta em SoR transacional rígido |
| `c6_dlq_rejeitos` | On-premises, colocado com `c5` (mesmo cluster Kafka ou MongoDB local) | Nenhum | Coerência de topologia com `c5` |
| `c7_catalogo_linhagem` | Serviço gerenciado — MongoDB Atlas | **AWS, região `sa-east-1`** (única exceção cloud) | Menor sensibilidade de latência, cross-cutting/assíncrono, reaproveita tecnologia já aprovada (MongoDB), residência de dado em território nacional |

## Condição de revisão futura — `c3_motor_qualificacao` não é decisão fechada em definitivo

Diferente dos outros cinco componentes on-prem (`c1`, `c2`, `c4`, `c5`, `c6`), cuja restrição é física e permanente (proximidade com sistemas legados que não mudam de lugar), a hospedagem on-prem de `c3_motor_qualificacao` é **uma decisão de fase**, sujeita a reavaliação formal, condicionada a dois fatores que ainda não estão resolvidos:

1. **Confirmação formal de Segurança/InfoSec** de que o dado processado em `c3` (já extraído/staged, sem tocar Teradata/CRM diretamente) pode residir em cloud dentro dos limites da LGPD (RNF-06) — avaliação ainda pendente, registrada como risco R7 em `desenho.md`.
2. **Comparação de custo** entre burst de capacidade on-prem (capex incremental de hardware) e burst em cloud gerenciada, mostrando vantagem financeira dentro do teto de RNF-07.

Se e somente se ambos os fatores forem confirmados, uma reavaliação deve ser formalmente registrada como **novo ADR**, passando primeiro por Pesquisa e Benchmarking para comparar opções de provedor sob esse critério. Este ADR **não decide essa segunda etapa agora**, porque o insumo de Segurança que a viabiliza ainda não existe — registrar isso como condição do ADR, não omitir, é deliberado: este documento formaliza on-prem como a decisão vigente para o horizonte desta demanda, não como decisão permanente do componente.

Da mesma forma, a hospedagem de `c7_catalogo_linhagem` em serviço gerenciado de terceiro (MongoDB Atlas) fica condicionada: se Segurança, ao avaliar formalmente RNF-06/R7, concluir que os metadados de linhagem armazenados ali constituem dado pessoal sob LGPD que não pode residir em ambiente gerenciado de terceiro (mesmo em território nacional), essa decisão de hospedagem também precisa ser revisitada.

## Consequências / trade-offs aceitos conscientemente

- **Concentração operacional em infraestrutura on-prem.** Seis de sete componentes (`c1`, `c2`, `c3` nesta fase, `c4`, `c5`, `c6`) ficam sob responsabilidade direta da equipe de infraestrutura local — sem elasticidade de cloud, sem auto-scaling gerenciado, dimensionamento de capacidade (especialmente de `c3` para o gargalo de throughput já sinalizado como risco R6, e de `c4` para o backlog do circuit breaker, risco R5 ainda não numericamente dimensionado) precisa ser feito manualmente e com antecedência.
- **`c3_motor_qualificacao` abre mão, nesta fase, do ganho técnico de elasticidade de cloud** que o próprio desenho já identificou como o de maior potencial para este componente — aceito conscientemente em troca de não abrir uma frente paralela de avaliação de compliance de cloud dentro do prazo apertado de RNF-08 (MVP mês 4, produção mês 6), e porque o gargalo de throughput (R6) tem mitigação viável via escala horizontal on-prem sem depender de aprovação externa.
- **Única exceção cloud (`c7`) introduz dependência de terceiro (AWS/MongoDB Atlas) e custo recorrente não totalmente confirmado.** O valor de referência usado (cluster M30, ~US$ 390–500/mês) é estimativa de mercado genérica, não cotação regionalizada para `sa-east-1` neste volume — precisa de confirmação por Custo/Infraestrutura antes de comprometer RNF-07, conforme já encaminhado por `infraestrutura.md`.
- **Custo de tráfego de rede evitado** ao manter `c1`/`c2`/`c3`/`c4`/`c5`/`c6` colocados fisicamente, sem egress/ingress recorrente entre datacenter local e cloud pública — ganho direto da decisão majoritariamente on-prem.
- **Risco assumido conscientemente:** se a suposição de SUP-04 (on-prem como decisão de negócio deliberada, não restrição orçamentária) estiver equivocada, e o teto de R$ 2,4M (RNF-07) se mostrar mais apertado em expansão de capacidade on-prem do que seria em cloud gerenciada, esta decisão de hospedagem pode precisar ser revisitada por Custo/Infraestrutura — a tensão foi sinalizada por `desenho.md` (seção 0.2) e não é resolvida por este ADR.

## Checagem de conflito com compêndio / ADRs anteriores
Conferido `substrate/compendium.md` seção 3 antes de escrever este ADR. Não há contradição: ADR 001 (cloud agnóstica por critério de negócio) é justamente o princípio que este ADR aplica — a decisão majoritariamente on-prem aqui não fixa um padrão novo de topologia para a casa, é a resposta específica desta demanda a um critério de negócio concreto (proximidade física com sistemas legados on-prem), da mesma forma que ADR 010 escolheu GCP para outra demanda por critério de negócio diferente (cotas gratuitas). A escolha de AWS `sa-east-1` para `c7` também não contradiz nenhuma decisão anterior de provedor (ADR 003/004 usaram AWS por outros motivos; ADR 010 usou GCP) — reforça que a escolha é sempre por demanda, nunca fixa.

## Quem revisou
Nenhuma pessoa sênior ou líder técnico revisou este ADR ainda. **Status permanece "Proposto" até essa revisão ocorrer.** Pergunta direta para quem está operando a sessão: por favor, revise esta decisão de hospedagem por componente — em especial a condição explícita de revisão futura de `c3_motor_qualificacao` (não é decisão fechada em definitivo) e a exceção única de `c7_catalogo_linhagem` em MongoDB Atlas/AWS `sa-east-1` — antes que ela seja tratada como oficial.
