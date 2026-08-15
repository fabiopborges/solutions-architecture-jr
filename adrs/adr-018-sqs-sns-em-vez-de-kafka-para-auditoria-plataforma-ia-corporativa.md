# ADR 018: Amazon SQS/SNS (não Kafka/AMQ Streams completo) para C7 (Auditoria) e demais eventos assíncronos da Plataforma-IA-Corporativa-V1

**Status:** Proposto.
**Revisado por:** (pendente — aguardando revisão de pessoa sênior ou líder técnico do time; não vale como decisão oficial até essa revisão acontecer)
**Data:** 2026-08-11
**Demanda que originou:** `demandas/plataforma-ia-corporativa-v1/` (fica global em `adrs/` para poder ser reaproveitado por demandas futuras, mesmo tendo nascido nesta)
**Escopo:** esta decisão vale para esta demanda especificamente (C7 — Serviço de Auditoria e Trilha de Acesso, e o evento `ContextoAtualizado` de C5→C3), condicionada à revisão futura descrita abaixo. Não altera o padrão geral da casa (Kafka via AMQ Streams continua o padrão da stack aprovada, compêndio seção 1).

## Contexto

O componente C7 (Serviço de Auditoria e Trilha de Acesso) consome de forma assíncrona o evento `AcessoAvaliado` (emitido por C6 a cada avaliação de acesso a dado potencialmente sensível) e persiste um `RegistroDeAuditoria` imutável, append-only, em armazenamento durável (Amazon S3 com Object Lock/WORM ou equivalente). Há também o evento `ContextoAtualizado` (C5→C3) na mesma categoria de mensageria assíncrona.

RNF07 já é fato firme: a plataforma trata PII e dado financeiro sensível (RH, Financeiro, Comercial), o que torna a trilha de auditoria um componente sensível a compliance. Ao mesmo tempo, RNF02 confirma porte pequeno/médio, com volume de eventos de auditoria estimado em dezenas a poucas centenas por dia — não há alto throughput a sustentar.

O padrão da casa para mensageria é Kafka via AMQ Streams (compêndio seção 1). Infraestrutura e Deployment (`demandas/plataforma-ia-corporativa-v1/infraestrutura.md`, seção 2) registrou uma decisão real — não mais sinalização — de usar Amazon SQS/SNS em vez de Kafka/AMQ Streams completo para C7 e para o evento `ContextoAtualizado`, condicional a uma revisão futura caso Segurança e Compliance confirme exigência de *replay* de tópico.

## Checagem de coerência com decisões anteriores

- **Compêndio, seção 1 (stack aprovada):** Kafka via AMQ Streams é o padrão declarado da casa para mensageria. Esta decisão **é um desvio explícito e justificado desse padrão**, não uma contradição silenciosa — o padrão geral não muda (nenhuma outra demanda é afetada), só esta demanda, por critério de negócio específico, foge dele.
- **ADR 003** (`adr-003-fila-gerenciada-e-aws-para-portal-digital-de-sinistros.md`, aprovado): mesma lógica já formalizada nesta casa — volume baixo não justifica o custo/operação de Kafka/AMQ Streams, fila/tópico gerenciado do provedor resolve com custo próximo de zero. Esta decisão **reforça** essa lógica (3ª ocorrência, junto com ADR 003 e ADR 007), não a contradiz.
- **ADR 007** (`adr-007-http-sincrono-com-outbox-em-vez-de-kafka-para-projeto-nuvem-vendas.md`, aprovado): mesmo padrão emergente — volume baixo dispensa Kafka/AMQ Streams em favor de alternativa mais leve. Esta decisão é coerente com o precedente, sem contradição.
- Nenhuma decisão anterior desta demanda (ADR 012–017) trata de mensageria, então não há conflito direto a sinalizar dentro do escopo já registrado da própria demanda.

**Conclusão da checagem:** decisão coerente com o histórico de ADRs da casa para o mesmo perfil (volume baixo). É um desvio do padrão geral da casa, corretamente identificado como tal pelo próprio documento de origem, e formalizado aqui em vez de tratado como se Kafka/AMQ Streams e SQS/SNS fossem escolhas equivalentes.

## Alternativas consideradas

- **Kafka via AMQ Streams (padrão da casa):** descartada para esta demanda. Amazon MSK Serverless tem piso de custo confirmado por Estimativa de Custo (`custo.md` seção 2.6/3) de ~US$ 540/mês só de cluster, antes de partição e dado transferido — uma ordem de grandeza acima do necessário para o volume real (dezenas a poucas centenas de eventos de auditoria/dia, RNF02). Exigiria também overhead operacional (cluster, patching, monitoramento) desproporcional ao caso de uso de um único consumidor (C7) processando um volume baixo e sem exigência de múltiplos consumidores independentes reprocessando o mesmo tópico.
- **Broker open source auto-hospedado:** não considerada como alternativa real nesta análise — carrega o mesmo problema de overhead operacional de um cluster dedicado sem o benefício de custo quase zero de uma opção gerenciada, mesma lógica já registrada no ADR 003 para descartar essa via.
- **Amazon SQS/SNS (fila/tópico gerenciado nativo):** escolhida, ver decisão.

O trade-off funcional mais relevante de abrir mão de Kafka — perder a capacidade de *replay* de tópico e retenção longa do log de evento em si — foi verificado e não ignorado: o desenho já separa o evento de trânsito (`AcessoAvaliado`) do registro persistido e imutável (`RegistroDeAuditoria`, gravado em armazenamento append-only fora da fila, com imutabilidade obrigatória exigida por `seguranca.md` seção 3.2). A garantia de auditoria que importa — não poder apagar ou alterar o histórico de acesso a PII — já está no armazenamento de destino, não depende da retenção da fila de transporte. Ordenação, se necessária no futuro, é resolvida dentro da mesma escolha via SQS FIFO com `MessageGroupId` por usuário/sessão, sem precisar revisitar o provedor de mensageria.

## Decisão

Para esta demanda: usar **Amazon SQS/SNS (fila/tópico gerenciado nativo)**, não Kafka/AMQ Streams completo, como transporte assíncrono para C7 (evento `AcessoAvaliado`) e para o evento `ContextoAtualizado` (C5→C3).

**Condição explícita de revisão futura, parte integrante desta decisão (não nota à parte):** esta decisão assume que a política de auditoria não exige *replay* do tópico de evento em si (distinto da leitura do `RegistroDeAuditoria` já persistido, que sempre é possível) nem retenção do tópico além do necessário para C7 consumir e persistir. Segurança e Compliance ainda não confirmou essa exigência (lacuna 5 do entendimento). **Se, quando a lacuna 5 for resolvida, Segurança e Compliance confirmar exigência regulatória ou de política interna de replay de X dias sobre o próprio fluxo de evento** (não apenas sobre o registro persistido), **esta decisão deve ser revisitada para Amazon MSK Serverless** — o piso de custo adicional (~US$ 540+/mês) passaria a ser justificado por um requisito funcional real, não por preferência de padrão. Até essa confirmação, SQS/SNS é a decisão vigente desta demanda. Esta condição é gatilho de reavaliação, não bloqueio da decisão atual.

## Consequências e trade-offs aceitos

- **Ganho:** custo de mensageria próximo de zero (~US$ 0 a poucos US$/mês) no volume desta demanda, contra piso de ~US$ 540+/mês do MSK Serverless — diferença de uma ordem de grandeza inteira no custo total de infraestrutura da demanda (`custo.md` seção 3). Sem overhead de operação de cluster.
- **Custo aceito:** esta demanda usa, para C7 e o evento `ContextoAtualizado`, um padrão de mensageria diferente do padrão geral da casa. Isso exige este ADR para que a divergência não seja lida como contradição silenciosa nem vire, por engano, um "padrão silencioso" reaproveitado sem a mesma análise de volume/orçamento por trás.
- **Risco aceito conscientemente:** se Segurança e Compliance confirmar exigência de replay de tópico (lacuna 5, ainda aberta), esta decisão terá que ser revisitada e trocada por MSK Serverless, com o custo adicional correspondente — este risco é assumido conscientemente agora, documentado explicitamente como condição da decisão, para não travar o desenho de infraestrutura enquanto a lacuna de compliance segue aberta.
- **Risco aceito conscientemente:** os números de custo usados nesta decisão vêm de fontes de precificação de referência (majoritariamente região padrão EUA), sem confirmação de SKU exato para `sa-east-1` — Estimativa de Custo precisa validar com a calculadora oficial da AWS antes de qualquer compromisso final; a diferença de ordem de grandeza entre as duas opções é grande o suficiente para não mudar a direção da decisão, mesmo com essa margem de incerteza.
