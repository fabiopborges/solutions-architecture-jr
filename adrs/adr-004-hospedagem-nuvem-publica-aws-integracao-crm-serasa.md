# ADR 004: Hospedagem em nuvem pública (AWS), com contingência on-premises/OpenBao, para a integração CRM–Serasa

**Status:** Proposto. Ainda não há revisão humana registrada — não vale como decisão oficial até uma pessoa sênior ou líder técnico revisar.
**Revisado por:** (pendente)
**Data:** 2026-08-09
**Demanda que originou:** `demandas/sdr-2026-002-integracao-crm-serasa-mtls-jwt/` (fica global em `adrs/` para poder ser reaproveitado por demandas futuras, mesmo tendo nascido nesta)
**Escopo:** vale para esta demanda especificamente. Aplica o critério já fixado pela casa em ADR 001 (cloud agnóstica por demanda) — não altera esse padrão geral, apenas o executa com os dados desta demanda.

## Contexto

O Serviço de Integração de Crédito, o Registro de Auditoria de Consultas e o Cofre de Segredos desta demanda precisavam de um lugar para rodar: dentro do datacenter on-premises do CRM legado, ou em nuvem pública com o CRM chamando de fora (egress). O desenho (seção 4) exigiu essa avaliação explícita, não deixou como padrão implícito. As restrições relevantes: prazo de 4 semanas já sinalizado em risco por Qualidade; teto de US$ 80/mês para toda a infraestrutura; volume baixo e concentrado em horário comercial (~5.000 consultas/dia, 9h–18h); necessidade de mTLS de saída limpo para a Serasa; e residência de dados (CPF, auditoria) ainda pendente de validação formal por Jurídico/Segurança da Informação.

Uma vez decidido "nuvem pública", era necessário escolher o provedor. O compêndio (seção 1, ADR 001) não fixa provedor — a escolha é por demanda, usando os critérios de negócio da seção 2 do compêndio (custo, residência/compliance, latência, maturidade do serviço gerenciado necessário, vendor lock-in, aderência ao que o time já opera). A pesquisa de Cofre de Segredos (`demandas/sdr-2026-002-integracao-crm-serasa-mtls-jwt/pesquisa-cofre-de-segredos.md`) já havia deixado a escolha do produto de cofre condicionada a essa decisão de provedor (regra de decisão: cofre nativo do provedor de compute escolhido, ou OpenBao se a decisão final for on-premises).

## Alternativas consideradas

**Onde hospedar (on-premises vs. nuvem pública):**
- **On-premises, junto ao CRM:** descartada como escolha principal. Provisionar servidor/VM dentro do datacenter legado depende de um time de infraestrutura fora do controle desta demanda, tipicamente mais lento que serviços gerenciados — risco direto ao prazo de 4 semanas já em risco. Operar on-premises (patch, backup, TLS do próprio host, cofre self-hosted como OpenBao, sem SRE dedicado) consome tempo de equipe que o teto de US$ 80/mês e o prazo não absorvem confortavelmente. Além disso, mTLS de saída pela Serasa tende a esbarrar em firewall/proxy corporativo com TLS inspection, que pode quebrar o handshake com certificado de cliente.
- **Nuvem pública, com egress do CRM até o componente hospedado fora:** escolhida, ver decisão. Serviços gerenciados eliminam provisionamento, cobram por uso real (favorável ao padrão de uso concentrado em horário comercial) e reduzem o risco de TLS inspection corporativa no caminho do mTLS.

**Provedor de nuvem pública (AWS vs. Azure vs. GCP):**
- **Azure:** não descartada por deficiência técnica relevante — tem inclusive uma vantagem pontual real (Azure Key Vault com tipo de objeto "Certificate" dedicado, com alerta de expiração, que ajudaria a mitigar o risco de rotação de certificado ainda sem processo desenhado). Descartada porque os demais critérios de negócio (maturidade confirmada de MongoDB Atlas na região AWS `sa-east-1`, contra suporte incerto de Atlas à região GCP equivalente, e presença de mercado/ecossistema de suporte local) pesaram mais no conjunto, dado o prazo apertado de 4 semanas.
- **GCP:** descartada pelo mesmo critério de maturidade do MongoDB Atlas — o suporte de Atlas à região `southamerica-east1` da GCP apareceu incerto na pesquisa (evidência de suporte a App Services, não confirmadamente a clusters gerais), risco considerado alto demais para descobrir tarde no prazo.
- **AWS:** escolhida, ver decisão.

## Decisão

1. **Hospedar o Serviço de Integração de Crédito, o Registro de Auditoria de Consultas e o Cofre de Segredos em nuvem pública** (região São Paulo), com o CRM legado on-premises chamando o endpoint via HTTPS de saída (egress), em vez de hospedar esses componentes dentro do datacenter do CRM.
   - **Condição/pré-requisito não confirmado:** esta decisão depende da confirmação, pelo time de rede do datacenter do CRM, de que a saída HTTPS (porta 443) para a nuvem pública está permitida ou pode ser liberada dentro do prazo. Essa confirmação ainda **não aconteceu** e deve ser buscada nas primeiras dias da construção, não perto da entrega.
   - **Contingência explícita:** se a confirmação de egress falhar, a hospedagem muda para on-premises, junto ao CRM, com Cofre de Segredos **OpenBao self-hosted** (conforme a pesquisa de cofre de segredos já recomenda para esse cenário específico). Essa mudança de rota reabre esta decisão por inteiro, não é um ajuste incremental.
   - **Residência de dados:** a região São Paulo foi escolhida de forma proativa para atender ao cenário mais provável de exigência de residência (LGPD/SUSEP), mas isso **não substitui** a validação jurídica formal, que segue pendente.
2. **Usar AWS como provedor de nuvem pública** para os componentes desta demanda (API Gateway, Serviço de Integração via App Runner, AWS Secrets Manager como Cofre de Segredos, MongoDB Atlas na região `aws-sa-east-1`).
   - Isso implica, por decorrência direta da regra de decisão já fixada pela pesquisa de Cofre de Segredos, o uso de **AWS Secrets Manager** como produto de cofre (não uma decisão nova e independente deste ADR, apenas a aplicação da tabela de decisão já pesquisada).

## Consequências e trade-offs aceitos

- **Ganho:** elimina o provisionamento e a operação de infraestrutura própria dentro de um prazo de 4 semanas já apertado; custo estimado (US$ 22–36/mês, com fontes oficiais onde disponíveis) fica confortavelmente abaixo do teto de US$ 80/mês, com folga para contingências.
- **Custo/risco aceito conscientemente — dependência não confirmada:** toda a decisão de hospedagem em nuvem pública fica condicionada a uma pré-condição técnica (egress do datacenter) que ainda não foi validada com o time de rede. Se falhar, implica retrabalho de arquitetura completo (mudança para on-premises/OpenBao), não apenas ajuste de configuração.
- **Risco aceito conscientemente — vendor lock-in com AWS:** mitigado parcialmente por o compute ser containerizado (Docker) e o acesso ao cofre passar por uma abstração fina no módulo de Conectividade, mas migrar de provedor no futuro ainda exigiria trocar o SDK do cofre e o serviço de compute gerenciado. Considerado aceitável frente ao ganho de velocidade de entrega.
- **Risco aceito conscientemente — comparação de provedor não unânime em todos os critérios:** Azure teria uma vantagem funcional pontual real (Key Vault com tipo "Certificate" dedicado) que ajudaria a mitigar o risco de rotação de certificado (ainda sem processo desenhado, ver ADR relacionado ou `demandas/sdr-2026-002-integracao-crm-serasa-mtls-jwt/infraestrutura.md`, seção 8, item 3). AWS foi escolhida pelo conjunto de critérios de negócio, não porque vencesse em todos os critérios técnicos isoladamente.
- **Pendência que este ADR não resolve:** validação jurídica formal de residência de dados (LGPD/SUSEP) e confirmação de egress do datacenter continuam em aberto e são pré-condições reais desta decisão, não apenas riscos residuais.

## Checagem de coerência com decisões anteriores

Não contradiz ADR 001 (cloud agnóstica por critério de negócio) — pelo contrário, é uma aplicação direta dele: a escolha de AWS aqui vale só para esta demanda, não fixa AWS como padrão da casa. Já existe precedente de outra demanda (`adrs/adr-003-fila-gerenciada-e-aws-para-portal-digital-de-sinistros.md`) também escolhendo AWS por critérios de negócio próprios — coincidência de resultado, não de regra; cada demanda refez a análise de critério de negócio de forma independente, como ADR 001 exige.
