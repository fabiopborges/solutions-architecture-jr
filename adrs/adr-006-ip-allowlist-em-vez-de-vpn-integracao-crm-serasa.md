# ADR 006: IP allowlist no API Gateway em vez de VPN/Direct Connect, como controle de acesso do CRM ao Serviço de Integração

**Status:** Proposto. Ainda não há revisão humana registrada — não vale como decisão oficial até uma pessoa sênior ou líder técnico revisar. **Além da revisão de arquitetura, esta decisão específica precisa também de validação do time de Segurança/Rede da SeguroSeguro antes de ser considerada definitiva** (já sinalizado como pendência em `demandas/sdr-2026-002-integracao-crm-serasa-mtls-jwt/infraestrutura.md`, seção 6) — trata-se de um segundo portão, além da revisão de arquitetura, não um substituto dela.
**Revisado por:** (pendente — revisão de arquitetura e validação de Segurança/Rede, ambas pendentes)
**Data:** 2026-08-09
**Demanda que originou:** `demandas/sdr-2026-002-integracao-crm-serasa-mtls-jwt/` (fica global em `adrs/` para poder ser reaproveitado por demandas futuras, mesmo tendo nascido nesta)
**Escopo:** vale para esta demanda especificamente. Depende da decisão de hospedagem em nuvem pública (ver `adrs/adr-004-hospedagem-nuvem-publica-aws-integracao-crm-serasa.md`) — só se aplica enquanto o CRM acessa o Serviço de Integração via chamada de saída pela internet.

## Contexto

O API Gateway é o único ponto de entrada exposto ao CRM legado on-premises; todo tráfego de `POST /consultas-credito` passa por ele antes de chegar ao Serviço de Integração de Crédito. É necessário algum controle de acesso de rede que restrinja esse tráfego a origens legítimas (o datacenter do CRM), dentro do teto de US$ 80/mês para toda a infraestrutura e do prazo de 4 semanas.

## Alternativas consideradas

- **VPN dedicada ou AWS Direct Connect** entre o datacenter do CRM e a VPC do Serviço de Integração: tecnicamente mais robusto (conectividade privada, não depende de exposição via internet pública), mas descartado para esta demanda porque é desproporcionalmente caro frente ao teto de US$ 80/mês (custo de circuito dedicado ou de gateway VPN 24x7 tipicamente consome, sozinho, uma fatia relevante ou o total desse orçamento) e desproporcional ao volume real desta demanda (~5.000 consultas/dia).
- **WAF completo (Web Application Firewall) na frente do API Gateway:** descartado pelo mesmo motivo de custo-benefício — proteção mais ampla do que o necessário para o padrão de tráfego desta integração ponto a ponto (CRM → Serviço de Integração), sem outros clientes externos previstos.
- **IP allowlist via resource policy nativa do API Gateway, restringindo a origem ao(s) IP(s) de saída do datacenter do CRM:** escolhida, ver decisão.

## Decisão

**Usar IP allowlist via resource policy do API Gateway** como controle de acesso de rede entre o CRM e o Serviço de Integração de Crédito, em vez de VPN dedicada, Direct Connect ou WAF completo, complementado por rate limiting básico nativo do serviço gerenciado (throttling padrão) como proteção mínima adicional contra uso indevido ou retry indevido do lado do CRM.

## Consequências e trade-offs aceitos

- **Ganho:** custo próximo de zero (recurso nativo do API Gateway, sem componente de rede adicional a provisionar ou operar), compatível com o teto de US$ 80/mês e o prazo de 4 semanas.
- **Risco aceito conscientemente:** IP allowlist é um controle de rede mais fraco que VPN/Direct Connect — depende de IP de saída estático e conhecido do datacenter do CRM (se esse IP mudar sem aviso, quebra o acesso silenciosamente; se for falsificável ou compartilhado com outro tráfego, a proteção é mais fraca que um túnel privado dedicado). A autenticação/autorização de fato do lado da Serasa (mTLS, Token JWT) continua isolada dentro do Serviço de Integração, então este controle de rede é uma camada adicional de defesa em profundidade, não a única barreira — mas ainda assim é uma barreira de rede mais fraca do que a alternativa descartada.
- **Pendência crítica que este ADR não resolve sozinho:** esta decisão de custo-benefício **ainda não foi validada pelo time de Segurança/Rede da SeguroSeguro**. Se esse time considerar IP allowlist insuficiente para o perfil de risco desta integração (dado que envolve CPF e consulta de crédito), esta decisão precisa ser revisitada antes da construção avançar — não é uma formalidade posterior.
- **Amarração à decisão de hospedagem:** esta decisão só se aplica enquanto a hospedagem for em nuvem pública com acesso via internet (API Gateway exposto). Se a contingência on-premises da hospedagem (ver ADR 004) se concretizar, este controle de acesso de rede específico deixa de se aplicar e precisa ser redesenhado como parte dessa mudança.

## Checagem de coerência com decisões anteriores

Não há ADR anterior no compêndio (seção 3) sobre controle de acesso de rede/borda para confrontar. Nenhuma contradição identificada com ADR 001 ou ADR 002.
