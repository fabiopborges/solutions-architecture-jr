# ADR 003: Fila gerenciada (não Kafka/AMQ Streams) e AWS como provedor, para o Portal Digital de Sinistros (SDR-2026-001)

**Status:** Aprovado.
**Revisado por:** Fabio Borges, Arquiteto de Soluções
**Data:** 2026-08-09
**Demanda que originou:** `demandas/sdr-2026-001-portal-digital-de-sinistros-e-upload-de-fotos/` (fica global em `adrs/` para poder ser reaproveitado por demandas futuras, mesmo tendo nascido nesta)
**Escopo:** esta decisão vale para esta demanda especificamente, não altera o padrão geral da casa (Kafka/AMQ Streams continua o padrão para os casos de alto throughput/orientação a eventos mais ampla, ver ADR 002).

## Contexto

O Portal Digital de Sinistros precisa de um componente de fila/buffer para reter dados de sinistro quando o SQL Server on-premises está indisponível (R3 do SDR), e de um provedor de cloud pública para armazenar fotos (R2). A demanda tem volume real baixo (pico de ~300 mensagens/hora), teto de orçamento de US$ 150/mês compartilhado entre fila e armazenamento, prazo de 90 dias, e preferência por open source/camada gratuita.

## Alternativas consideradas

**Para a fila/buffer:**
- Kafka via AMQ Streams (padrão da casa): descartada para esta demanda porque exige computação dedicada rodando 24/7, consumindo uma fatia desproporcional do orçamento de US$ 150/mês frente ao volume real (menos de 1 mensagem a cada 10 segundos no pico), e exige operação (patching, monitoramento) incompatível com um time interno em 90 dias sem esse cluster já rodando.
- Broker open source auto-hospedado (ex: RabbitMQ): descartada, ainda exige servidor dedicado e manutenção, sem o benefício de custo zero de operação da opção gerenciada.
- Fila gerenciada do provedor de nuvem: escolhida, ver decisão.

**Para o provedor de cloud:**
- Os três provedores (AWS, Azure, GCP) foram comparados pelos critérios de negócio do compêndio (custo, compliance/residência, latência, maturidade, vendor lock-in, aderência ao que já é operado). Nenhuma cloud está em uso hoje (sem custo de troca a proteger). Azure e GCP foram descartados por vantagem pequena e não decisiva: a documentação encontrada para o serviço de fila gerenciada da AWS tinha a camada gratuita permanente mais generosa e mais bem documentada nas fontes pesquisadas (detalhe em `demandas/sdr-2026-001-portal-digital-de-sinistros-e-upload-de-fotos/infraestrutura.md`).

## Decisão

Para esta demanda: usar uma **fila gerenciada do provedor de nuvem** (não Kafka/AMQ Streams) como buffer de resiliência, e usar **AWS** como provedor de nuvem para os componentes desta demanda (armazenamento de evidências com lifecycle quente/frio, fila gerenciada, hospedagem serverless da API, API Gateway).

## Consequências e trade-offs aceitos

- **Ganho:** custo de operação da fila próximo de zero no volume desta demanda (dentro da camada gratuita), sem servidor para manter, compatível com o prazo de 90 dias e a ausência de equipe de operação dedicada.
- **Custo aceito:** esta demanda usa um padrão de mensageria diferente do padrão geral da casa. Isso exige documentação clara (este ADR) para que outra pessoa não estranhe a divergência depois, e para que não vire, por engano, um novo "padrão silencioso" sem essa mesma análise de volume/orçamento por trás.
- **Risco aceito conscientemente:** os números de custo usados na decisão são aproximados (baseline US-East-1, não região Brasil, ver disclaimer em `custo.md`), então esta decisão pode precisar de revisão se os números reais da região Brasil mudarem a equação de forma relevante.
