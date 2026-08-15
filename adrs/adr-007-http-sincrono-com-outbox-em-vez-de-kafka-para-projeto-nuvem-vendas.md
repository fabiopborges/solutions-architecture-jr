# ADR 007: Chamada HTTP síncrona com retry/backoff + Transactional Outbox, sem broker de mensageria, para o Projeto Nuvem Vendas (projeto-nuvem-vendas-v1)

**Status:** Aprovado.
**Revisado por:** Fabio Borges, Arquiteto de Soluções, em 2026-08-10
**Data de registro:** 2026-08-10
**Demanda que originou:** `demandas/projeto-nuvem-vendas-v1/` (fica global em `adrs/` para poder ser reaproveitado por demandas futuras, mesmo tendo nascido nesta — o próprio dono do negócio sinalizou que esta decisão pode ajudar projetos futuros, o que reforça a importância de registrá-la com cuidado de padrão, não só como nota pontual desta demanda)
**Escopo:** esta decisão vale para esta demanda especificamente. Não altera, por si só, o padrão geral da casa (Kafka/AMQ Streams continua o padrão do compêndio, seção 1, para os casos de alto throughput/orientação a eventos mais ampla — ver ADR 002). Ver seção "Relação com ADR 003 e padrão emergente" abaixo para uma observação sobre repetição do mesmo tipo de conflito em duas demandas seguidas.

## Contexto

O Projeto Nuvem Vendas precisa notificar o ERP legado (Delphi + Firebird on-premises, sem API — RNF09) sempre que um pedido de venda é fechado, para faturamento e baixa de estoque, sem nunca perder nem duplicar esse comando (RF05, RNF05). O desenho original (`demandas/projeto-nuvem-vendas-v1/desenho.md`, versão anterior à revisão de 2026-08-10) usava o padrão da casa: Transactional Outbox publicando em Kafka via AMQ Streams, consumido de forma assíncrona pelo Adaptador de Legado e pelo Serviço de Relatórios.

Essa versão foi barrada por uma restrição dura e não-negociável da demanda: **RNF08**, orçamento de infraestrutura de nuvem abaixo de R$ 300/mês **para a demanda inteira**, não só para um componente. `qualidade.md` já havia registrado veredito "não atende" em RNF08 com Kafka no desenho, porque um cluster Kafka gerenciado, isolado, tende a consumir sozinho mais do que esse teto inteiro — mesmo antes de contar os outros componentes.

O volume real desta demanda é o de uma distribuidora de médio porte fechando pedidos de venda, não uma escala de milhões de eventos/dia que justificaria o custo de operar um broker.

## Alternativas consideradas

- **Kafka via AMQ Streams (padrão da casa, compêndio seção 1):** descartada. Cluster gerenciado consome, isolado, mais do que o teto inteiro de RNF08 (<R$300/mês para toda a infraestrutura da demanda, não só mensageria). Incompatível mesmo antes de considerar os demais componentes que também precisam de orçamento.
- **Fila gerenciada mais barata do provedor de nuvem (mesmo padrão do ADR 003, ex.: fila gerenciada tipo SQS):** considerada como primeira alternativa óbvia (foi a solução adotada na demanda anterior, sdr-2026-001, ADR 003), mas descartada aqui após uma pergunta adicional: mesmo uma fila gerenciada de baixo custo ainda é uma peça de infraestrutura de mensageria dedicada, com sua própria camada de contrato, monitoramento e modelo mental extra, para um volume que não gera pressão de desacoplamento real (não há picos que precisem de buffer, nem consumidores lentos a proteger). Para este volume específico, mesmo o custo baixo dela é desproporcional ao problema que resolveria.
- **Broker open source auto-hospedado (ex.: RabbitMQ):** descartada pelo mesmo motivo do ADR 003 — exige servidor dedicado e manutenção, sem o benefício de custo zero de operação.
- **Chamada HTTP síncrona com retry/backoff, mantendo o Transactional Outbox como fonte de verdade local:** escolhida, ver decisão.

## Decisão

Manter o **Transactional Outbox** no Serviço de Pedidos de Venda (grava pedido + comando pendente na mesma transação local, no próprio MongoDB do serviço — isso não muda). Substituir a publicação em Kafka por um **Publicador de Outbox interno** ao próprio serviço (ex.: job agendado de curto intervalo), que entrega o comando ao Adaptador de Legado via **chamada HTTP/REST síncrona, com retry e backoff exponencial** e limite de tentativas. Ao esgotar as tentativas, o registro de outbox é marcado como "falho" para intervenção manual — o equivalente funcional de uma dead-letter queue, sem exigir nenhuma infraestrutura de fila para isso, apenas um estado adicional na própria tabela de outbox já existente.

Nenhum componente de mensageria (broker gerenciado, fila gerenciada, ou auto-hospedada) faz parte deste desenho.

## Consequências e trade-offs aceitos

- **Ganho:** elimina por completo o componente de mensageria e a pressão de custo que ele gerava sobre RNF08, sem abrir mão da garantia central (RF05/RNF05: pedido fechado nunca se perde antes de ser encaminhado ao legado) — essa garantia continua vindo do outbox, não do broker.
- **Ganho:** menos peças móveis no desenho (um componente a menos para operar, monitorar e pagar), o que também reduz superfície de risco operacional em um time sem operação de mensageria dedicada.
- **Custo aceito:** esta demanda diverge duplamente do padrão da casa — não só troca Kafka por outra ferramenta (como o ADR 003 fez), mas remove a camada de mensageria inteira. Isso exige documentação clara (este ADR) para que a divergência não seja lida como descuido, e para que não vire, por engano, um "padrão silencioso" copiado em outra demanda sem a mesma análise de volume/orçamento por trás.
- **Risco aceito conscientemente:** o **Publicador de Outbox como processo interno é um ponto único de falha mais discreto do que o broker era.** Sem fila externa, a responsabilidade de retry/backoff fica dentro do próprio Serviço de Pedidos — se esse job travar (não o serviço inteiro, só o job de publicação), comandos podem se acumular na tabela de outbox sem sinalização visível, a menos que haja alerta dedicado. Sinalizado para o agente de Observabilidade nesta demanda (`desenho.md`, riscos 3 e 5).
- **Risco aceito conscientemente:** o acoplamento temporal entre o Serviço de Pedidos e o Adaptador de Legado aumenta um pouco em relação a um modelo assíncrono — se o Adaptador ficar indisponível por um período longo, os comandos se acumulam na tabela local (o que é aceitável e esperado, dado o retry/backoff), mas isso é uma dependência de disponibilidade que um broker teria amortecido de forma mais transparente. Para o volume desta demanda, esse acoplamento foi julgado aceitável frente ao ganho de custo/simplicidade.
- **Gatilho de revisão explícito:** se o volume real de pedidos crescer muito além do esperado para uma distribuidora de médio porte (ex.: múltiplos canais de venda simultâneos, integrações futuras com muitos consumidores), esta decisão precisa ser revisitada, e aí sim faria sentido acionar Pesquisa e Benchmarking para comparar filas leves — não antes disso.

## Relação com ADR 003 e padrão emergente (observação, não regra)

Esta é a **segunda vez** que o mesmo tipo de conflito aparece em demandas seguidas: volume real baixo e orçamento de nuvem apertado colidindo com o padrão de mensageria da casa (Kafka/AMQ Streams, compêndio seção 1).

- Na primeira vez (`sdr-2026-001-portal-digital-de-sinistros-e-upload-de-fotos`, ADR 003), a resposta foi trocar Kafka por uma **fila gerenciada** de baixo custo — ainda havia mensageria, só que mais barata.
- Nesta segunda vez (projeto-nuvem-vendas-v1), a resposta foi **questionar se alguma mensageria assíncrona era necessária antes de escolher qual ferramenta usar** — e a conclusão foi que não era, para este volume.

Duas ocorrências não são evidência suficiente para promover isso a uma regra geral da casa (isso exigiria mais dados e, principalmente, uma decisão consciente de quem mantém o compêndio, não uma inferência deste ADR). Mas já é sinal suficiente para registrar como **observação de padrão emergente**, para que a próxima demanda com o mesmo perfil (volume baixo, orçamento apertado) considere essa pergunta na ordem certa:

> Antes de perguntar "qual ferramenta de mensageria cabe no orçamento?", perguntar "este volume realmente precisa de mensageria assíncrona, ou uma chamada síncrona com retry/backoff e outbox já entrega a mesma garantia?".

Se um terceiro caso do mesmo tipo aparecer, recomenda-se que o Trade-offs e ADR (ou quem mantém o compêndio) avalie formalizar essa pergunta como critério explícito na seção 2 do compêndio ("Padrões e políticas da casa"), ao lado do critério de escolha de provedor de cloud. Não é feito agora, para não virar regra geral com base em duas amostras.

## Aprovação

O dono do negócio já sinalizou, ao originar esta demanda, que esta decisão pode servir de referência para projetos futuros — o que torna a aprovação formal ainda mais importante de buscar ativamente, não deixar parada. Este ADR **precisa** ser levado a uma pessoa sênior ou líder técnico do time para revisão antes de ser considerado aprovado e antes de seu resumo entrar em `substrate/compendium.md` seção 3. Enquanto isso não acontece, o status permanece **Proposto**, mesmo que a decisão pareça tecnicamente correta.
