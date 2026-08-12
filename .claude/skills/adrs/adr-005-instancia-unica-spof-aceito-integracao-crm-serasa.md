# ADR 005: Aceitação explícita de instância única (SPOF) do Serviço de Integração de Crédito

**Status:** Proposto. Ainda não há revisão humana registrada — não vale como decisão oficial até uma pessoa sênior ou líder técnico revisar.
**Revisado por:** (pendente)
**Data:** 2026-08-09
**Demanda que originou:** `demandas/sdr-2026-002-integracao-crm-serasa-mtls-jwt/` (fica global em `adrs/` para poder ser reaproveitado por demandas futuras, mesmo tendo nascido nesta)
**Escopo:** vale para esta demanda especificamente. Depende da decisão de hospedagem em AWS App Runner (ver `adrs/adr-004-hospedagem-nuvem-publica-aws-integracao-crm-serasa.md`) — se essa decisão de hospedagem mudar (ex.: contingência on-premises), este ADR precisa ser revisitado.

## Contexto

O desenho de arquitetura (seção 6.2) assume um cache de Token JWT em memória de processo do Serviço de Integração de Crédito, o que funciona de forma simples com uma única instância "efetiva" do serviço, mas cria redundância de reautenticação (não corrupção de dado) se múltiplas instâncias rodarem em paralelo. Qualidade sinalizou esse ponto como SPOF #1, classificado como "não confirmado" — pediu explicitamente que Infraestrutura e Deployment confirmasse por escrito se essa configuração de instância única era uma decisão consciente ou um acaso de implementação.

Contexto de negócio relevante: não há exigência de disponibilidade 24x7 (suposição do entendimento, mantida ao longo da cadeia); o volume é baixo (~5.000 consultas/dia, pico de ~9 consultas/minuto) e concentrado em horário comercial (9h–18h); e não há SLA formal do solicitante confirmado até o momento desta decisão.

## Alternativas consideradas

- **Múltiplas instâncias ativas com cache de Token compartilhado (ex.: cache externo em vez de memória de processo):** descartada para esta demanda. Resolveria o SPOF de forma mais robusta, mas exigiria um componente de cache distribuído adicional (custo e complexidade extra), sem exigência de negócio (disponibilidade 24x7, SLA formal) que justifique esse investimento dentro do prazo de 4 semanas e do teto de US$ 80/mês.
- **Redundância multi-região ou multi-instância ativa "always-on":** descartada. Não há exigência de continuidade de negócio cross-region ou de alta disponibilidade no entendimento nem no desenho; o custo e a complexidade seriam desproporcionais ao volume real da demanda.
- **Instância mínima configurada em 1, com autoscaling limitado a um teto pequeno (2–3 instâncias) só como rede de segurança para picos, sobre uma plataforma de compute gerenciada com reinício automático e distribuição em múltiplas zonas de disponibilidade por baixo do capô (AWS App Runner):** escolhida, ver decisão.

## Decisão

**Aceitar conscientemente uma configuração logicamente próxima de instância única** para o Serviço de Integração de Crédito (instância mínima = 1, escala automática permitida apenas como rede de segurança para picos inesperados, não para volume normal), em vez de investir em cache distribuído ou redundância ativa multi-instância.

Isso é aceito porque:
1. Não há exigência de disponibilidade 24x7 confirmada.
2. O volume é baixo e concentrado em horário comercial, não justificando mais de uma instância para volume normal.
3. A plataforma de compute gerenciada (AWS App Runner) já provê reinício automático de instância com falha e distribuição em múltiplas zonas de disponibilidade, sem custo ou configuração extra do time — o que reduz a janela real de indisponibilidade em caso de falha de infraestrutura subjacente, mesmo mantendo o comportamento lógico de "uma instância" para fins de cache.
4. Se picos raros disparam uma segunda instância via autoscaling, o efeito é uma reautenticação redundante ocasional contra a Serasa — já identificado no desenho como não crítico, não uma falha de dado ou de disponibilidade.

## Consequências e trade-offs aceitos

- **Ganho:** custo e complexidade mínimos, sem componente de cache distribuído adicional, dentro do prazo de 4 semanas e do teto de US$ 80/mês.
- **Risco aceito conscientemente:** o serviço continua, logicamente, um ponto único de falha para o cache de Token em memória. Se a plataforma subjacente falhar de um jeito que o reinício automático não cubra bem (ex.: degradação de zona inteira, não apenas de instância), há uma janela de indisponibilidade real até a recuperação — mitigada, mas não eliminada, pela distribuição nativa em múltiplas zonas do App Runner.
- **Gatilho de revisão explícito:** se um SLA formal de disponibilidade aparecer depois (pendência já sinalizada por Qualidade, ainda não recebida do solicitante), esta decisão precisa ser revisitada — a configuração atual não foi dimensionada para SLA formal nenhum, foi dimensionada para ausência de exigência confirmada.
- **Amarração à decisão de hospedagem:** esta aceitação de SPOF depende das garantias nativas do AWS App Runner (reinício automático, múltiplas zonas). Se a hospedagem migrar para a contingência on-premises (ver `adrs/adr-004-hospedagem-nuvem-publica-aws-integracao-crm-serasa.md`), essas garantias não estão automaticamente presentes e esta decisão de SPOF precisa ser reavaliada como parte dessa migração, não herdada por padrão.

## Checagem de coerência com decisões anteriores

Não há ADR anterior no compêndio (seção 3) sobre disponibilidade/SPOF para confrontar — esta é a primeira decisão desse tipo registrada formalmente. Nenhuma contradição identificada com ADR 001 ou ADR 002.
