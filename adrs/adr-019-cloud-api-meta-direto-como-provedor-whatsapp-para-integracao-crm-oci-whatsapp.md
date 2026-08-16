# ADR 019 — Cloud API da Meta (direto) como provedor de WhatsApp Business Platform para o componente C4 de `integracao-crm-oci-whatsapp`

## Status
**Aprovado.** Aprovação registrada por quem está operando a sessão, na revisão do portão de saída da demanda `integracao-crm-oci-whatsapp`, em 2026-08-15. O Orquestrador repassou a aprovação (não decidiu por conta própria) — a decisão de revisão é de uma pessoa, não de um agente.

## Demanda de origem
`demandas/integracao-crm-oci-whatsapp/` — decisão insumada pelo agente de Pesquisa e Benchmarking (`pesquisa-provedor-whatsapp.md`), a partir de sinalização do Desenho de Arquitetura (`desenho.md`, seção 0 e risco R6, componente **C4 — Adapter de Envio WhatsApp**, bounded context BC-2, fronteira de saída/Anti-Corruption Layer). Formalizada aqui por Trade-offs e ADR, não decidida de novo — este documento consolida a comparação já feita, não reabre a pesquisa.

## Contexto / Problema
O componente C4 precisa de um provedor de WhatsApp Business Platform definido antes de fechar seu contrato de integração (autenticação, formato de payload, webhook de status). O pedido original citou duas rotas possíveis sem decidir: **Cloud API da Meta direto** ou **broker homologado (BSP — Business Solution Provider)**, com exemplos citados: Twilio, Take Blip, Zenvia.

`substrate/compendium.md` seção 1 (Stack aprovada) não lista nenhum canal de mensageria de WhatsApp nem BSP homologado, e a seção 3 (ADRs) não tem precedente de integração com WhatsApp — **esta é a primeira decisão desse perfil na casa**, sem ADR anterior a contradizer ou reforçar.

Critérios de comparação definidos antes de olhar as opções (herdados do risco R6 do desenho e de requisitos concretos já mapeados):
1. Custo por mensagem.
2. Complexidade de gestão de template pré-aprovado pela Meta (risco R5 do desenho; suposição 6 do entendimento — mensagens fora da janela de 24h exigem template aprovado).
3. Suporte a webhook de status de entrega (RF06 — auditoria de envio, agregado "Notificação de Lead" / entidade "Tentativa de Envio" em C2/C3).
4. Complexidade operacional de token/credencial.
5. Tempo/esforço de homologação.
6. Aderência a RNF01/RNF02 (LGPD/segurança em trânsito e em log).

RNF05 (volumetria) segue não confirmado no momento desta pesquisa; o exemplo citado no pedido original é ~500 leads/dia (estimativa não confirmada).

## Alternativas consideradas

| Critério | Cloud API Meta (direto) — escolhida | Twilio (BSP) | Take Blip (BSP) | Zenvia (BSP) |
|---|---|---|---|---|
| **Custo por mensagem** | Só a tarifa da Meta por categoria de template, sem markup nem mensalidade de plataforma | Tarifa da Meta + markup de US$0,005–0,010/mensagem | Tarifa da Meta + mensalidade de plataforma relatada entre R$1.000–2.500/mês (penaliza volume baixo) | Tarifa da Meta + assinatura/mensalidade + markup por mensagem; sinal de risco de transparência de preço (relato público não confirmado como tarifa oficial) |
| **Gestão de template pré-aprovado** | Submissão/aprovação direta pela Meta, sem camada intermediária | Console próprio sobre o mesmo fluxo de aprovação da Meta — uma camada extra | Console próprio + passo extra de sincronização (até ~20 min de propagação relatada) | Console próprio, mesma mecânica de camada extra |
| **Webhook de status de entrega (RF06)** | Evento `message_status` nativo, direto da Meta, com retry automático de até 7 dias | Repassado via formato de evento próprio do BSP — uma tradução extra | Mesma lógica de repasse | Mesma lógica de repasse |
| **Complexidade operacional de token/credencial** | Um único segredo (token da Cloud API) | Dois níveis de credencial (token do BSP + vínculo WABA) | Mesma lógica de dois níveis | Mesma lógica de dois níveis |
| **Tempo/esforço de homologação** | Verificação de negócio na Meta é o gargalo comum a todas as rotas (3–10 dias úteis em caso padrão, estimativa de mercado) | Onboarding assistido reduz esforço de configuração pós-verificação, mas não elimina o gargalo | Mesmo padrão | Mesmo padrão |
| **RNF01/RNF02 (LGPD)** | Superfície mínima — só a Meta processa o dado do lead | Uma parte adicional processa/pode reter log/metadado | Mesma ressalva | Mesma ressalva, com sinal de risco adicional de transparência comercial |

**BSPs (Twilio, Take Blip, Zenvia) foram descartados** porque, para o perfil desta demanda (volumetria não confirmada, mas exemplo citado de baixo/moderado volume — ~500 leads/dia), nenhum deles reduz um trâmite que já é comum a todas as rotas (verificação de negócio na Meta), e todos somam: custo recorrente (markup por mensagem e/ou mensalidade fixa, que penaliza especialmente volume baixo), uma camada de tradução extra entre o evento nativo `message_status` da Meta e o que chega em C2/C3 (mais uma superfície de falha/latência para RF06), mais uma credencial a gerir e rotacionar, e mais uma parte terceira processando dado pessoal do lead (nome, telefone, e-mail) — contrário à minimização de exposição exigida por RNF02. Entre os três, Take Blip e Zenvia têm mensalidade fixa (pior ajuste a volume baixo); Twilio tem modelo puramente por mensagem, sendo o BSP relativamente mais alinhado a esse cenário caso um BSP viesse a ser escolhido — mas nenhum supera a Cloud API direta em nenhum dos seis critérios.

Os valores de preço de BSPs vêm de fontes de mercado agregadas (blogs especializados, documentação de terceiros), não de cotação formal — nenhuma das três empresas publica tabela de preço fechada para o Brasil em 2026. Essa limitação de confiabilidade dos dados é registrada aqui como parte da base da decisão, não escondida.

## Decisão
Adotar **Cloud API da Meta, direto** (sem intermediário/BSP comercial) como provedor de WhatsApp Business Platform para o componente **C4 — Adapter de Envio WhatsApp** da demanda `integracao-crm-oci-whatsapp`.

Condicionantes explícitas mantidas junto com a decisão:
- Token de acesso da Cloud API (long-lived system user token via Meta Business Manager) é o único segredo do lado do provedor, e deve ficar em cofre de segredos (ex.: OCI Vault, ou equivalente do provedor de cloud que Infraestrutura e Deployment escolher — decisão de provedor de cloud é separada, ver ADR 001).
- C4 (ACL de saída) é responsável por toda a operação da integração — formatação de payload, autenticação, consumo do webhook `message_status`, retry — sem rede de segurança comercial de um BSP.
- Gestão de template pré-aprovado é feita diretamente com a Meta (Meta Business Manager), sem console de terceiro.

## Consequências / Trade-offs aceitos
- **Menor custo por mensagem** entre todas as opções pesquisadas — sem markup nem mensalidade de plataforma. Diferença de custo entre as opções aumenta (não diminui) com volume alto, o que reforça a decisão mesmo se RNF05 vier a confirmar volume maior que o exemplo citado.
- **Menor superfície de terceiro tocando dado pessoal do lead** (RNF02) — só a Meta processa a mensagem.
- **Webhook de status de entrega nativo**, sem camada de tradução extra entre o evento original da Meta e o que alimenta a entidade "Tentativa de Envio" (RF06) — reduz uma peça que poderia falhar ou atrasar a auditoria.
- **Risco assumido conscientemente: sem suporte comercial dedicado de fornecedor.** O time responsável pela operação/manutenção de C4 assume webhook, retry, formatação de payload e gestão de token sem apoio comercial de um BSP — mais responsabilidade técnica interna, sem rede de segurança de terceiro em caso de instabilidade da própria integração (a Meta não oferece suporte operacional dedicado do tipo que um BSP comercial oferece).
- **Verificação de negócio na Meta continua sendo o gargalo comum de homologação** independente desta escolha — a decisão não acelera nem atrasa essa etapa, apenas remove uma camada de onboarding assistido que um BSP ofereceria na fase de configuração técnica pós-verificação.
- **Reversibilidade condicionada:** se no futuro o time responsável por C4 não tiver capacidade de sustentar a operação sem apoio comercial, ou surgir necessidade de recursos de atendimento multi-agente/inbox compartilhado (fora do escopo atual — RF04 é envio unidirecional, não conversa), a escolha por um BSP deve ser reaberta como novo ADR, não como alteração informal deste.
- **Dependência dos valores de preço usados na comparação**, que vêm de fontes de mercado agregadas e não de cotação oficial dos BSPs — se este ADR for revisitado no futuro por mudança de contexto, recomenda-se obter cotação formal por escrito de Take Blip e Zenvia antes de reabrir a comparação, em vez de reusar os números aqui citados como definitivos.

## Coerência com o compêndio e ADRs anteriores
Nenhum ADR anterior desta casa trata de WhatsApp Business Platform, Cloud API da Meta ou BSPs — **este é o primeiro ADR desse perfil na casa**, sem precedente a contradizer ou reforçar. Coerente com o compêndio seção 2 (nenhum provedor de serviço gerenciado é preferido de antemão; decisão por critério de negócio e requisito real) e com o princípio de minimização de superfície de terceiro processando dado pessoal já aplicado em outras decisões da casa (ex.: ADR 006, allowlist/autenticação de aplicação em vez de VPN, mesma lógica de reduzir peças/partes envolvidas). Candidato a virar referência para demandas futuras de perfil semelhante (integração com WhatsApp Business Platform, volume baixo/moderado), mas ainda não promovido a padrão geral da casa — cada demanda futura deve reavaliar volume, capacidade operacional do time e necessidade de recursos de atendimento antes de reaproveitar esta conclusão automaticamente.

## Revisão
**Concluída.** Revisado e aprovado por quem está operando a sessão em 2026-08-15, na revisão do portão de saída da demanda `integracao-crm-oci-whatsapp`. A partir desta aprovação, este ADR vale como decisão oficial para a demanda `integracao-crm-oci-whatsapp` e é candidato a reaproveitamento por demandas futuras de perfil semelhante (ver seção "Coerência com o compêndio e ADRs anteriores").
