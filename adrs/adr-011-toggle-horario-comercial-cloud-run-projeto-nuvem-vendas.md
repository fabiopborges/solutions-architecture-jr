# ADR 011: Instância mínima do Cloud Run ativa apenas em horário comercial, como mitigação de custo para o Serviço de Pedidos de Venda (projeto-nuvem-vendas-v1)

**Status:** Aprovado.
**Revisado por:** Fabio Borges, Arquiteto de Soluções, em 2026-08-10
**Data de registro:** 2026-08-10
**Demanda que originou:** `demandas/projeto-nuvem-vendas-v1/` (fica global em `adrs/` para poder ser reaproveitado por demandas futuras, mesmo tendo nascido nesta — o padrão de "instância mínima só em horário de uso real" é candidato a reaproveitamento por qualquer demanda com Cloud Run/serverless, orçamento apertado e uso concentrado em horário comercial)
**Escopo:** depende da escolha de GCP/Cloud Run (ver ADR 010) para esta demanda. Vale como padrão candidato para demandas futuras com o mesmo perfil (serverless com instância mínima ativa para evitar cold start, uso concentrado em horário de expediente, orçamento apertado), sujeito a reavaliação da janela de horário e do volume de pico a cada caso.

## Contexto

O Serviço de Pedidos de Venda precisa manter uma instância mínima ativa no Cloud Run (min-instances=1) para evitar cold start de uma aplicação Java/Spring Boot durante o pico real de uso (RF01/RNF01/RNF02). Manter essa instância ativa 24 horas por dia, todos os dias, é o item de maior custo estimado desta demanda (~US$ 20–28/mês de ~300h/mês ativas) e o item de maior variância na estimativa total — o teto superior do intervalo estimado (~US$ 62/mês) ultrapassa o teto de RNF08 (<R$300 ≈ US$ 55/mês), enquanto o piso (~US$ 30/mês) cabe com folga. A diferença entre os dois extremos é dominada por este item.

## Alternativas consideradas

- **Instância mínima ativa 24/7:** descartada como configuração padrão — paga por disponibilidade fora do horário em que o risco de indisponibilidade em pico (a causa raiz do projeto) não se aplica, empurrando a estimativa total para perto ou acima do teto de RNF08 sem necessidade real.
- **min-instances=0 o tempo todo (escala a zero sempre), aceitando cold start:** descartada — reintroduziria exatamente o problema de indisponibilidade em pico que motivou originalmente manter uma instância mínima (RNF01/RNF02), especialmente relevante para uma aplicação Java/Spring Boot, cujo cold start tende a ser mais perceptível que em runtimes mais leves.
- **Instância mínima ativa apenas em horário comercial (ex.: 8h–19h, ~11h/dia úteis), via toggle agendado (min-instances=1 na abertura, min-instances=0 no fechamento):** escolhida, ver decisão.

## Decisão

Configurar dois pequenos jobs de agendamento (Cloud Scheduler, dentro da cota gratuita de 3 jobs/conta de faturamento/mês) para alternar `min-instances` do Cloud Run do Serviço de Pedidos de Venda: subir para 1 no início do horário comercial e voltar para 0 no fechamento. Isso reduz as horas ativas cobradas de ~300h/mês (24/7) para próximo de ~240h úteis/mês, e evita cobrança fora do expediente. Esta configuração é tratada como **padrão de implantação obrigatório**, não como otimização opcional — é o que mantém a estimativa de custo desta demanda dentro do teto de RNF08 com folga real.

## Consequências e trade-offs aceitos

- **Ganho:** reduz o item de maior custo e maior variância da estimativa, sendo o fator que efetivamente coloca a estimativa total dentro do teto de RNF08 (piso ~US$ 30/mês com esta mitigação, contra um teto superior de ~US$ 62/mês sem ela).
- **Risco aceito conscientemente: cold start fora do horário comercial.** Qualquer uso do Serviço de Pedidos de Venda fora da janela configurada (ex.: fechamento de pedido feito por vendedor fora do expediente, ou uso não previsto por outro consumidor da API) sofre cold start, porque a instância mínima estará em 0. Aceitável porque RF01/RF02 são operações de vendas presumidas concentradas em horário comercial, mas **não foi confirmado com o solicitante** que não há uso legítimo fora dessa janela — mesma lacuna já registrada para a meta numérica de disponibilidade/volumetria de pico (`qualidade.md` RNF01/RNF02, ainda "atende parcial").
- **Risco aceito conscientemente: a janela de horário comercial (8h–19h) é uma estimativa, não um número confirmado pelo negócio.** Se o horário real de operação da distribuidora for diferente (ex.: atendimento até mais tarde, ou fins de semana), a janela do toggle precisa ser ajustada, e o custo recalculado.
- **Risco aceito conscientemente: dependência de dois jobs agendados adicionais operando corretamente.** Se o job de abertura falhar silenciosamente, o Serviço de Pedidos de Venda opera o dia inteiro com cold start (degradação de experiência, não indisponibilidade); se o job de fechamento falhar, a instância mínima fica ativa além do horário previsto (custo maior que o estimado, não um risco de indisponibilidade). Nenhum dos dois modos de falha é catastrófico, mas nenhum dos dois tem alerta dedicado definido nesta decisão — sinalizado para o agente de Observabilidade desta demanda.
- **O que esta decisão não resolve:** a estimativa de custo geral (`infraestrutura.md` seção 4) segue sendo estimativa de ordem de grandeza, não cotação fechada de SKU para `southamerica-east1` — esta mitigação reduz o risco de estourar o teto, mas não substitui a validação com a calculadora oficial do GCP recomendada antes de qualquer compromisso.

## Quando este padrão se aplica a demandas futuras (orientação de reaproveitamento)

Candidato a reaproveitamento sempre que uma demanda futura usar Cloud Run (ou serverless equivalente) com instância mínima ativa para evitar cold start, tiver uso concentrado em uma janela de horário previsível, e estiver sob pressão de orçamento. Antes de copiar sem reavaliar:

- Confirmar a janela real de uso do negócio (não presumir horário comercial padrão sem checar) — aqui ainda não confirmado com o solicitante.
- Confirmar que o custo do cold start ocasional fora da janela é aceitável para o requisito de disponibilidade real da demanda nova (não é um número universal).
- Garantir que os jobs de toggle tenham alerta de falha antes de tratar esta mitigação como resolvida — não constava aqui.

## Checagem de coerência com decisões anteriores

Não há ADR anterior no compêndio (seção 3) sobre mitigação de custo por horário de uso para confrontar. Não identificada contradição com nenhum ADR existente; é uma decisão de configuração operacional específica desta demanda, amarrada à escolha de GCP/Cloud Run (ADR 010).
