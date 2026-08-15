# ADR 017 — Política fail-closed para C6 (Controle de Acesso) na Plataforma-IA-Corporativa-V1

## Status
**Proposto.** Aguardando revisão de uma pessoa sênior ou líder técnico do time. Não vale como decisão oficial até essa revisão acontecer.

## Demanda de origem
`demandas/plataforma-ia-corporativa-v1/` — decisão tomada pelo Desenho de Arquitetura (`desenho.md`, seção 2, linha C6; risco R11, revisão v2 de 2026-08-11, motivada por achado de Testes e Qualidade). Formalizada aqui por Trade-offs e ADR, não decidida de novo.

## Contexto / Problema
C6 (Serviço de Controle de Acesso e Segmentação, Policy Decision Point) é o ponto único de decisão de autorização consumido de forma síncrona por C2 (Orquestração de Consultas) e C4 (Geração de Conteúdo) antes de qualquer resposta ser composta — avalia, para cada consulta/geração, se o usuário (papel + área) pode acessar aquele dado/trecho, dado sua classificação de sensibilidade. C6 é guardião de PII (RNF07) e ponto único de decisão para duas capacidades de negócio simultaneamente (CN01 e CN02). A v1 do desenho não declarava o comportamento de C6 sob indisponibilidade (timeout, erro) — lacuna apontada por Testes e Qualidade e corrigida na v2.

## Alternativas consideradas
| Alternativa | Por que foi descartada (ou não) |
|---|---|
| **Fail-open (liberar acesso por padrão sob indisponibilidade)** | Descartada por incompatibilidade direta com RNF07: sob indisponibilidade de C6, C2/C4 prosseguiriam sem filtro de sensibilidade, expondo qualquer trecho de qualquer área a qualquer usuário — justamente o risco crítico que o desenho já registra como R1 (vazamento de dado sensível entre áreas). Abrir acesso "sob pressão operacional" (para não travar o usuário) seria uma decisão de exceção não planejada, exatamente o cenário que o desenho quer evitar declarando a política antecipadamente. |
| **Comportamento deixado como opção de configuração, a decidir na implementação** | Descartada: para um guardião de PII em ponto único de decisão de duas capacidades de negócio, deixar o comportamento sob falha como configurável (implicitamente sujeito a ser configurado errado, ou mudado sob pressão de disponibilidade) é incompatível com o requisito de RNF07 ser tratado como fato firme, não uma preferência ajustável. |
| **Fail-closed (negar acesso por padrão sob indisponibilidade)** (escolhida) | Consistente com RNF07: sob indisponibilidade, o custo é experiência do usuário (consulta/geração falha ou fica incompleta), não exposição de dado sensível. Trade-off assumido conscientemente em favor de segurança sobre disponibilidade percebida. |

## Decisão
Adotar política **fail-closed** para C6: se C6 não responder (timeout, erro, indisponibilidade) dentro do prazo esperado, a decisão padrão é **negar acesso**, nunca liberar por padrão. C2 e C4 devem tratar "sem resposta de C6" como equivalente a "acesso negado" para o trecho/fonte em questão, não como "prosseguir sem filtro".

Esta é decisão de desenho, fixada explicitamente, não uma opção de configuração deixada para depois. O requisito de alta disponibilidade de C6 (redundância/failover, para minimizar o quanto esse fail-closed é de fato acionado) permanece escopo de Infraestrutura e Deployment — esse detalhe técnico não está fechado por este ADR.

## Consequências / Trade-offs aceitos
- **Disponibilidade percebida pelo usuário sacrificada em favor de segurança**: sob indisponibilidade de C6, consultas (CN01) e gerações de conteúdo (CN02) falham ou retornam incompletas, mesmo que o dado subjacente não fosse, de fato, sensível para aquele usuário específico — aceito conscientemente como o custo correto diante de um guardião de PII.
- **Risco residual de indisponibilidade de C6 impactar diretamente a experiência de uso da plataforma** — mitigado (não eliminado) pela exigência de alta disponibilidade/redundância de C6, que fica com Infraestrutura e Deployment; este ADR não garante que C6 nunca ficará indisponível, apenas fixa o comportamento correto quando isso acontecer.
- **Dependência de implementação correta em C2 e C4**: a política só é efetiva se C2/C4 de fato tratarem "sem resposta de C6" como "acesso negado" em toda chamada, sem exceção implícita de código (ex.: try/catch que segue adiante silenciosamente) — risco de implementação a ser verificado no portão de saída/testes antes de produção.

## Coerência com o compêndio e ADRs anteriores
Nenhum ADR anterior desta casa trata de política de falha de componente de controle de acesso — primeiro ADR desse tipo na casa. Não contradiz nenhuma decisão prévia. Coerente com o espírito geral do compêndio de tratar requisitos de segurança/PII como não negociáveis quando confirmados como fato firme (mesmo princípio usado nesta mesma demanda para a exigência de criptografia, ver ADR 016). Candidato a virar padrão geral da casa para qualquer componente futuro que funcione como Policy Decision Point de dado sensível — ainda não promovido a critério formal da seção 2 do compêndio.

## Revisão
Pendente. Aguardando revisão explícita de pessoa sênior ou líder técnico do time antes de status mudar para "Aprovado".
