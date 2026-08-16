# ADR 020 — HTTP síncrono + Outbox (Candidata 2) como decisão INTERINA para o "meio de campo" C1→C2/C2→C4 de `integracao-crm-oci-whatsapp`, até RNF05 ser confirmado

## Status
**Aprovado, com natureza explicitamente INTERINA/provisória — não é decisão definitiva.** Aprovação registrada por quem está operando a sessão em 2026-08-15, que autorizou explicitamente este plano de contingência (ver seção "Aprovação humana e natureza condicional" abaixo). Esta aprovação cobre apenas a formalização da decisão interina em si, não decide nem aprova nada além do que está escrito neste documento.

## Demanda de origem
`demandas/integracao-crm-oci-whatsapp/` — decisão insumada por `desenho.md` (seção 5, "Decisão pendente — streaming/mensageria vs. HTTP síncrono") e por `custo.md` (seções 3 e 6, comparação de custo entre Candidata 1 e Candidata 2). Formalizada aqui por Trade-offs e ADR a pedido do Orquestrador, que repassou autorização explícita de quem está operando a sessão para um plano de contingência — não é uma decisão que este agente tomou por iniciativa própria a partir de critério técnico isolado, é a formalização de uma autorização humana de contingência.

## Contexto / Problema

`desenho.md` seção 5 descreve duas arquiteturas candidatas para o "meio de campo" entre C1 (Adaptador de Detecção de Novo Lead) e C2 (Serviço de Notificação de Lead), e entre C2 e C4 (Adapter de Envio WhatsApp):

- **Candidata 1** — orientada a eventos com broker (Kafka via AMQ Streams, padrão da stack, ou serviço de streaming equivalente do provedor de nuvem escolhido).
- **Candidata 2** — HTTP síncrono com retry/backoff + Transactional Outbox como fonte de verdade local.

A escolha entre as duas depende de **RNF05 (volumetria de leads/dia)**, que `entendimento.md` já registrou como lacuna não confirmada por quem pediu, e que `desenho.md` (seção 4, risco R4) trata como bloqueio explícito de ADR — não do desenho conceitual como um todo. Até o momento desta formalização, **RNF05 segue sem resposta**.

`custo.md` (seção 3, C2; seção 6, Cenários A-D) quantificou o peso dessa lacuna: para os dois cenários de volume usados como referência nos documentos de entrada (~500 leads/dia e ~5.000 leads/dia, 10x), **o custo do broker (Candidata 1) fica entre 3 e 6 vezes maior que o custo de infraestrutura inteiro da Candidata 2**, e essa diferença **não diminui com o aumento de volume** dentro da faixa avaliada — o custo do broker é dominado pelo custo fixo de cluster, não pelo throughput de dados, que segue trivial nas duas faixas. `custo.md` seção 6 registra literalmente: "para o volume baixo citado no pedido original, o custo do broker por si só (US$180-550+/mês, antes de qualquer outro componente) é 3 a 6 vezes maior que o custo de infraestrutura inteiro da Candidata 2 (US$105-159/mês)".

`desenho.md` seção 5 também já apontou que este seria o terceiro caso do mesmo perfil já visto na casa (ADR 003 e ADR 007), mas evitou decidir sem RNF05 confirmado, para não preencher uma suposição de negócio que não cabe ao Desenho de Arquitetura preencher.

## Aprovação humana e natureza condicional (leia antes do resto do documento)

Este ADR **não resolve a lacuna de RNF05**. Quem está operando esta sessão autorizou explicitamente um **plano de contingência**: se a resposta de RNF05 não vier em tempo hábil, a equipe segue com a Candidata 2 como decisão **interina/provisória**, revisável assim que a volumetria real chegar. Essa autorização foi dada diretamente por quem opera a sessão, não inferida nem assumida por nenhum agente — está registrada aqui porque o Orquestrador repassou a decisão, não decidiu por conta própria, e porque a regra desta atividade exige registrar aprovação humana de forma explícita, mesmo quando a decisão parece óbvia (não basta o portão de aprovação humana normal de ADR — este documento nasce sob um plano de contingência que também foi autorizado por pessoa, e isso precisa constar por escrito, não ser assumido).

**Isto é uma decisão condicional, não definitiva.** Os pontos abaixo não são detalhe de rodapé — são a essência deste ADR:

1. **Gatilho de revisão:** a chegada da resposta real de RNF05 (volumetria de leads/dia confirmada por quem pediu). No momento em que essa resposta chegar, este ADR deve ser reaberto e reavaliado à luz do número real — não apenas mantido por inércia. Se o número confirmado ficar fora da faixa avaliada em `custo.md` (~500 a ~5.000 leads/dia), a reavaliação é ainda mais necessária, porque a leitura de custo que sustenta esta decisão não cobre volumes muito maiores.
2. **Escopo estritamente limitado:** este ADR decide **apenas** o mecanismo do "meio de campo" C1→C2 e C2→C4 (Candidata 1 vs. Candidata 2, seção 5 do `desenho.md`). Ele **não decide, não assume e não tem plano de contingência para** a outra decisão pendente do mesmo desenho — o mecanismo de detecção do CRM (Opção A — push nativo — vs. Opção B — polling —, seção 4 do `desenho.md`). Essa pergunta segue **genuinamente sem resposta**, sem decisão interina associada, e não deve ser tratada como resolvida ou implicitamente decidida por este documento. Nenhuma leitura deste ADR deve ser usada para inferir uma escolha entre Opção A e Opção B.
3. **Não é promoção a padrão geral da casa.** Assim como o ADR 007 e o ADR 003, esta decisão não altera o padrão geral de mensageria do compêndio (seção 1: Kafka via AMQ Streams continua sendo o padrão da casa). É uma decisão pontual desta demanda, sob um regime interino declarado.

## Alternativas consideradas

| Critério | Candidata 2 — HTTP síncrono + Outbox (escolhida, interina) | Candidata 1 — broker/streaming |
|---|---|---|
| **Custo de infraestrutura (baixo volume, ~500 leads/dia)** | ≈US$105-159/mês (Cenário A, `custo.md` seção 6) | ≈US$285-707/mês, dominado pelo custo fixo de cluster (Cenário B, `custo.md` seção 6) — 3 a 6x maior |
| **Custo de infraestrutura (alto volume, ~5.000 leads/dia)** | ≈US$105-159/mês, throughput ainda trivial (Cenário C) | ≈US$285-707/mês, a diferença **não diminui** com o volume 10x maior, porque o custo é de cluster fixo, não de dado transportado (Cenário D) |
| **Complexidade operacional** | Menos peças novas (nenhum broker/tópico a operar); Outbox como fonte de verdade local já é padrão conhecido na casa (ADR 007, ADR 003) | Broker novo a operar, monitorar e manter (offset, partição, retenção) |
| **Desacoplamento entre C1 e C2, e reaproveitamento futuro do evento por outros consumidores** | Menor — HTTP direto acopla C1 a C2 (mitigado por Outbox como fonte de verdade e retry/circuit breaker) | Maior — outros consumidores futuros do evento "Lead Recebido" (ex.: um dashboard de auditoria mais amplo) poderiam assinar o mesmo tópico sem acoplar a C1 |
| **Aderência a volume real (RNF05)** | Adequada a volume baixo/moderado (a faixa citada nos documentos de entrada) — mas **decisão tomada sem confirmação do número real**, é a fragilidade central desta escolha | Adequada a volume alto ou a cenário de múltiplos consumidores futuros — nenhum dos dois confirmado nesta demanda |
| **Precedente na casa** | 3ª ocorrência do mesmo padrão (ADR 003, ADR 007, e agora este) | Nenhuma ocorrência de streaming ter sido escolhida quando a mesma tensão apareceu antes |

**Candidata 1 não foi descartada de forma definitiva** — ela segue como opção legítima caso RNF05 confirme um volume alto o suficiente para justificar o custo fixo do broker, ou caso surja um segundo consumidor real do evento "Lead Recebido" que hoje não existe (nenhum documento de entrada aponta um). O que motiva a escolha interina pela Candidata 2 não é a superioridade técnica incondicional dela, é: (a) o custo desproporcional do broker para as duas faixas de volume que os próprios documentos de entrada usam como referência, (b) o padrão já emergente na casa (ADR 003, ADR 007) de dispensar streaming sem volumetria real por trás, e (c) a necessidade de não deixar a demanda travada indefinidamente enquanto RNF05 não chega, sob autorização explícita de contingência.

## Decisão

Adotar **Candidata 2 — HTTP síncrono com retry/backoff + Transactional Outbox** como arquitetura do "meio de campo" (C1→C2 e C2→C4) da demanda `integracao-crm-oci-whatsapp`, **em caráter INTERINO/provisório**, sob o seguinte regime:

- Vale enquanto a resposta real de RNF05 (volumetria de leads/dia) não for confirmada por quem pediu.
- Assim que RNF05 for confirmado, este ADR deve ser **reaberto e reavaliado** — não apenas arquivado como definitivo. Se o volume real confirmar a faixa já avaliada (baixo/moderado, dentro de ~500 a ~5.000 leads/dia) e nenhum segundo consumidor do evento "Lead Recebido" tiver surgido, a expectativa é que a Candidata 2 se confirme como decisão definitiva pelos mesmos motivos já expostos aqui — mas essa confirmação **precisa ser feita explicitamente**, não presumida.
- Se o volume real vier muito acima da faixa avaliada, ou se surgir necessidade real de múltiplos consumidores do mesmo evento, a decisão deve ser reaberta com viés para reconsiderar a Candidata 1, usando os dados reais em vez dos cenários hipotéticos usados aqui.

**Esta decisão NÃO resolve, NÃO assume e NÃO tem posição de contingência sobre o mecanismo de detecção do CRM (Opção A — push nativo — vs. Opção B — polling, `desenho.md` seção 4).** Essa pergunta segue sem resposta, tratada como lacuna genuína, não como decisão implícita. Ver seção "Aprovação humana e natureza condicional" acima, item 2 — este ponto é repetido aqui de propósito, para não passar despercebido em nenhuma leitura futura deste ADR.

## Consequências / Trade-offs aceitos

- **Custo de infraestrutura significativamente menor** enquanto o volume real não for confirmado (US$105-159/mês vs. US$285-707+/mês, `custo.md` seção 6) — é o principal argumento por trás da urgência de destravar a demanda com uma decisão interina, em vez de esperar RNF05 indefinidamente.
- **Risco assumido conscientemente: decisão pode precisar ser revertida.** Se RNF05 vier a confirmar volume muito acima da faixa avaliada, ou surgir um segundo consumidor real do evento "Lead Recebido", a Candidata 2 pode não se sustentar, e migrar de HTTP+Outbox para um broker depois de já estar em produção tem custo de retrabalho que uma decisão definitiva bem informada evitaria. Este risco é aceito explicitamente por quem autorizou o plano de contingência, não escondido.
- **Menor desacoplamento entre C1 e C2** enquanto a Candidata 2 estiver em vigor — mitigado pelo padrão de retry/circuit breaker e Outbox como fonte de verdade local (já usado com sucesso nos precedentes ADR 003 e ADR 007), mas não elimina o acoplamento direto de chamada HTTP.
- **A lacuna de RNF05 continua aberta e sem prazo definido de resposta** — este ADR destrava a arquitetura, não a pergunta de negócio. Quem está operando a sessão está ciente de que a decisão interina não substitui a necessidade de obter RNF05; é uma forma de a equipe seguir trabalhando sem ficar bloqueada indefinidamente.
- **A decisão do mecanismo de detecção do CRM (push vs. polling) continua igualmente travada e sem contingência** — este ADR resolve uma lacuna da demanda, não as duas. Ver seção 4 do `desenho.md` e risco R1 do mesmo documento — esses seguem em aberto, sem prazo e sem plano de contingência formalizado até o momento.
- **Reversibilidade prevista e esperada**, diferente de um ADR definitivo: este documento já nasce com o entendimento de que pode (e provavelmente vai) ser reaberto quando RNF05 chegar — isso não é uma falha do ADR, é a natureza dele.

## Coerência com o compêndio e ADRs anteriores

Reforça, como **3ª ocorrência** na casa, o padrão já registrado no compêndio seção 3 pelo **ADR 003** e pelo **ADR 007**: para volume baixo/moderado e sem volumetria real confirmada, a casa tem dispensado Kafka/AMQ Streams (ou streaming equivalente) em favor de um padrão mais simples (fila gerenciada no ADR 003, HTTP síncrono + Outbox no ADR 007 e aqui). **Não altera o padrão geral da casa** (mensageria continua Kafka via AMQ Streams, compêndio seção 1) — é uma decisão pontual desta demanda, sob regime interino, não uma promoção a critério formal da seção 2.

Diferente dos precedentes ADR 003 e ADR 007, que foram decisões **definitivas** tomadas com informação suficiente disponível no momento, este ADR é **explicitamente interino**, porque a informação que normalmente sustentaria uma decisão definitiva (RNF05) segue faltando — essa é a diferença relevante a não perder de vista ao reaproveitar este ADR como precedente em demandas futuras: o padrão técnico (HTTP+Outbox para volume baixo) é reaproveitável, mas o caráter interino deste documento específico não deve ser copiado como se fosse a norma — normalmente a casa só formaliza decisão definitiva com dado real disponível; este ADR é uma exceção autorizada por contingência humana explícita, não um novo padrão de "decidir sem dado".

Não contradiz nenhum ADR anterior desta casa.

## Revisão
**Aprovado sob regime interino em 2026-08-15**, por autorização explícita de quem está operando a sessão, repassada pelo Orquestrador (não decidida por iniciativa de agente). Este ADR **deve ser reaberto assim que RNF05 for confirmado por quem pediu** — esse é o gatilho de revisão, não uma data-limite arbitrária. Até lá, vale como decisão oficial interina para a demanda `integracao-crm-oci-whatsapp`, mas nenhuma demanda futura deve reaproveitar este ADR como se fosse uma decisão definitiva padrão sem antes checar se o volume real da demanda nova está confirmado — o caráter interino é parte do que precisa ser copiado, não só a conclusão técnica.
