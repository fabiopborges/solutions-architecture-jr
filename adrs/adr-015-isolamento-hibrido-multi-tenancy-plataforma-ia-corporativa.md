# ADR 015 — Isolamento híbrido de multi-tenancy (lógico por padrão, físico para RH/Folha) para Plataforma-IA-Corporativa-V1

## Status
**Proposto.** Aguardando revisão de uma pessoa sênior ou líder técnico do time. Não vale como decisão oficial até essa revisão acontecer.

## Demanda de origem
`demandas/plataforma-ia-corporativa-v1/` — decisão tomada pelo Desenho de Arquitetura (`desenho.md`, seção 1.1, revisão v2 de 2026-08-11). O próprio desenho registra que uma versão anterior (v1) havia atribuído erroneamente esta decisão a Trade-offs e ADR; a correção de responsabilidade já foi feita pelo desenho (a decisão do **nível** de isolamento é dele, não desta atividade) — este ADR formaliza a decisão já tomada, não decide de novo.

## Contexto / Problema
RNF05 exige segmentação entre as áreas de negócio (Comercial, Financeiro, TI, RH/Folha) que compartilham a mesma plataforma de consulta e geração de conteúdo (BC1/BC2, componente C3 — Índice de Conhecimento Corporativo). RH/Folha é a única área com subcategoria própria de sensibilidade (**Sensível/PII — RH**, ver `dados.md`), por concentrar dado de folha/saúde/emprego, com maior densidade de PII e maior exposição legal (LGPD) entre as quatro áreas (ver risco R6 do desenho e risco R1, crítico, de vazamento de dado sensível entre áreas).

O porte confirmado é pequeno/médio (RNF02) e o orçamento segue como lacuna aberta (lacuna 2 do entendimento).

## Alternativas consideradas
| Alternativa | Por que foi descartada (ou não) |
|---|---|
| **Isolamento lógico para todas as quatro áreas** | Menor custo/complexidade, mas não oferece camada adicional de defesa para a área de maior densidade de PII (RH/Folha) — depende inteiramente da granularidade/correção do metadado de classificação por trecho e da robustez de C6, nenhuma das duas é garantia absoluta. |
| **Isolamento físico para todas as quatro áreas** | Multiplicaria a complexidade operacional de C3 (múltiplos índices/bases para manter, replicar e monitorar) e o custo de infraestrutura, sem redução de risco proporcional para áreas de sensibilidade mais baixa (ex.: CRM, classificado predominantemente como Interno restrito com PII pontual de contato). Dado o porte pequeno/médio já confirmado e a lacuna de orçamento ainda aberta, não é escolha defensável sem evidência de risco equivalente em todas as áreas. |
| **Isolamento híbrido — lógico por padrão, físico para RH/Folha** (escolhida) | Aceita o risco residual do isolamento lógico onde a sensibilidade concreta não demanda tratamento diferenciado (Comercial, Financeiro, TI), e paga o custo adicional de isolamento físico apenas onde a sensibilidade já demandou tratamento diferenciado no próprio desenho e na modelagem de dados (RH/Folha). |

## Decisão
Adotar isolamento híbrido de multi-tenancy entre as áreas de negócio:
- **Comercial, Financeiro e TI: isolamento lógico** — mesma infraestrutura de C3, segmentação por metadado de classificação/proveniência em `ChunkIndexado` e aplicação de `PoliticaDeAcesso` em C6 no momento da consulta. Não há índice/base física separada por área.
- **RH/Folha: isolamento físico** — índice/base segregada dentro de C3 (ou instância própria do componente, tecnologia/mecanismo concreto a definir com Infraestrutura e Deployment), com o mesmo contrato `ContextoCorporativo`/`ChunkIndexado`, mas fisicamente apartada das demais áreas.

Esta decisão define o **nível** de isolamento por área. A tecnologia/mecanismo concreto de segregação física é escopo de Pesquisa e Benchmarking e de Infraestrutura e Deployment, ainda não fechado.

## Consequências / Trade-offs aceitos
- **Risco residual de vazamento entre áreas aceito conscientemente para Comercial/Financeiro/TI** (ligado a R1, crítico): isolamento lógico depende inteiramente da granularidade e correção do metadado de classificação por trecho (obrigatório, ver `dados.md`) e da disponibilidade/robustez de C6 (mitigada pela política fail-closed, ver ADR 017) — nenhuma dessas duas garantias é absoluta. Este risco é mitigado, não eliminado.
- **Custo/complexidade operacional adicional para RH/Folha aceito conscientemente**: manter um índice/base fisicamente apartado exige mais infraestrutura para monitorar, replicar e operar do que uma segmentação puramente lógica — tratado como defesa em profundidade (camada complementar ao isolamento lógico, não redundante com ele) para a área de maior risco.
- **Suposição exposta**: esta decisão assume que RH/Folha é, hoje, a única área com densidade de PII/dado regulatório que justifica isolamento físico. Se Financeiro revelar, na prática, densidade equivalente (ex.: dado de cartão, dado bancário individualizado), a mesma lógica deve ser reavaliada para essa área — não é uma exclusividade estrutural de RH, é consequência da classificação de sensibilidade atual, sujeita a mudança se a informação mudar.
- **Mecanismo concreto de segregação física ainda não definido** — dependência aberta com Pesquisa e Benchmarking e Infraestrutura e Deployment; este ADR não deve ser lido como fechando esse detalhe.

## Coerência com o compêndio e ADRs anteriores
Nenhum ADR anterior desta casa trata de multi-tenancy ou isolamento entre áreas de negócio — primeiro ADR desse tipo na casa. Não contradiz nenhuma decisão prévia. Coerente com o compêndio seção 2 (DDD/bounded contexts — a decisão de isolamento respeita o agrupamento de BC3 já justificado no desenho, com ressalva explícita de que o agrupamento deve ser revisto se RH revelar regras de compliance muito mais rígidas que os demais sistemas, risco R6). Candidato a padrão emergente para demandas futuras que combinem múltiplas áreas de negócio de sensibilidade desigual em uma mesma plataforma — ainda não promovido a critério formal da seção 2 do compêndio.

## Revisão
Pendente. Aguardando revisão explícita de pessoa sênior ou líder técnico do time antes de status mudar para "Aprovado".
