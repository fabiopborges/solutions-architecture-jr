# ADR 010: GCP como provedor de nuvem para o Projeto Nuvem Vendas (projeto-nuvem-vendas-v1)

**Status:** Aprovado.
**Revisado por:** Fabio Borges, Arquiteto de Soluções, em 2026-08-10
**Data de registro:** 2026-08-10
**Demanda que originou:** `demandas/projeto-nuvem-vendas-v1/` (fica global em `adrs/` para poder ser reaproveitado por demandas futuras, mesmo tendo nascido nesta)
**Escopo:** vale para esta demanda especificamente. Não altera o padrão geral da casa (compêndio seção 1/ADR 001: cloud continua agnóstica de provedor, escolhida por critério de negócio a cada demanda — esta escolha de GCP não cria preferência de provedor para demandas futuras).

## Contexto

`desenho.md` e `qualidade.md` definiram os componentes e requisitos desta demanda (Frontend Web de Vendas, Serviço de Pedidos de Venda, Serviço de Relatórios de Vendas, API Gateway/Load Balancer, banco MongoDB) sob um teto de orçamento de nuvem apertado (RNF08, <R$300/mês ≈ US$ 55/mês), o mais apertado que este time já avaliou nas demandas até agora. Era preciso escolher um provedor de nuvem pública entre AWS, Azure e GCP, conforme os critérios de negócio já estabelecidos no compêndio (seção 2): custo total, residência/compliance de dados, latência, maturidade do serviço gerenciado necessário, vendor lock-in, e aderência ao que o time já opera.

## Alternativas consideradas

- **AWS:** usada nas duas demandas anteriores desta casa (`sdr-2026-001` via ADR 003, `sdr-2026-002` via ADR 004). Não descartada por padrão, comparada nos mesmos critérios — mas a cota gratuita padrão de vários serviços da AWS é válida só no primeiro ano da conta, o que é relevante porque RNF08 é um teto recorrente sem data de expiração conhecida, e essa demanda tem o orçamento mais apertado das três já avaliadas.
- **Azure:** comparada nos mesmos itens de custo (computação serverless, API Gateway, hospedagem estática); Azure Container Apps empata tecnicamente com Cloud Run na cota gratuita de computação, mas não foi identificada, na pesquisa realizada, uma cota gratuita permanente equivalente para os demais itens (API Gateway, hospedagem estática) que desempatasse a favor de Azure; também é a opção mais cara para VPN, item que acabou eliminado da arquitetura (ver ADR 009), mas que pesou na comparação inicial.
- **GCP:** escolhida, ver decisão.

## Decisão

Usar **GCP** como provedor de nuvem para os componentes desta demanda: Cloud Run (Serviço de Pedidos de Venda e Serviço de Relatórios de Vendas), API Gateway (GCP), Firebase Hosting (Frontend Web de Vendas), e MongoDB Atlas hospedado sobre GCP, região `southamerica-east1` (São Paulo).

O fator decisivo, dado o teto de orçamento apertado, foi a **combinação de cotas gratuitas permanentes** (não limitadas ao primeiro ano de conta) em API Gateway (2 milhões de chamadas/mês) e Firebase Hosting (10 GB armazenamento, 360 MB/dia de banda), que reduz o risco de o custo subir de forma inesperada depois do primeiro ano — relevante porque RNF08 é um teto recorrente. Em computação serverless (item de maior peso no orçamento), GCP (Cloud Run) e Azure (Container Apps) empatam tecnicamente, então o desempate real veio dos demais itens. Residência de dados (região São Paulo) e maturidade de serviço gerenciado foram atendidas sem diferenciar os três provedores; nenhum problema de vendor lock-in desproporcional foi identificado (compute containerizado, migrável entre provedores).

## Consequências e trade-offs aceitos

- **Ganho:** dentro da estimativa de custo produzida (`infraestrutura.md` seção 4), o piso do intervalo (~US$ 30/mês) cabe com folga no teto de RNF08, e a ausência de expiração das cotas gratuitas usadas reduz o risco de reabertura desta decisão daqui a 12 meses por aumento de custo.
- **Trade-off assumido conscientemente: esta não é uma escolha unânime em todos os critérios.** O fator decisivo (cotas gratuitas de API Gateway e Hosting) é um detalhe de precificação sujeito a mudança pelos provedores a qualquer momento — se GCP alterar essas cotas, esta decisão pode precisar de revisão.
- **Trade-off assumido conscientemente: divergência do provedor usado nas duas demandas anteriores da casa (ambas AWS).** Isso é esperado e coerente com o ADR 001 (cloud agnóstica, decisão por demanda), não uma inconsistência — mas registrado aqui explicitamente para que ninguém interprete a divergência como confusão sobre "qual é o padrão da casa": não há padrão fixo de provedor, cada demanda decide pelos seus próprios critérios de negócio.
- **Risco aceito conscientemente: números de custo não são cotação fechada de SKU para a região `southamerica-east1`.** A maior parte das fontes usadas traz preço de referência de região padrão/EUA (ver `infraestrutura.md` seção 0 e 4). Recomenda-se validar com a calculadora oficial do GCP, região São Paulo, antes de qualquer compromisso — mesma ressalva já registrada nos ADRs/demandas anteriores desta casa.

## Checagem de coerência com decisões anteriores

Não contradiz o ADR 001 (cloud agnóstica por critério de negócio) — é exatamente uma aplicação desse princípio: o provedor foi comparado pelos critérios já definidos no compêndio, não escolhido por padrão ou por repetição das demandas anteriores. Diverge do provedor escolhido nos ADRs 003 e 004 (ambos AWS), mas essa divergência é o comportamento esperado de uma política de escolha por demanda, não uma contradição a sinalizar como conflito.
