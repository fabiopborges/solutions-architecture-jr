# ADR 016 — Exigência de criptografia em trânsito e em repouso para todo componente que toca PII/dado sensível na Plataforma-IA-Corporativa-V1

## Status
**Proposto.** Aguardando revisão de uma pessoa sênior ou líder técnico do time. Não vale como decisão oficial até essa revisão acontecer.

## Demanda de origem
`demandas/plataforma-ia-corporativa-v1/` — decisão tomada pelo Desenho de Arquitetura (`desenho.md`, seção 2, "Requisito transversal — criptografia em trânsito e em repouso", revisão v2 de 2026-08-11, motivada por achado de Testes e Qualidade). Formalizada aqui por Trade-offs e ADR, não decidida de novo.

## Contexto / Problema
RNF07 exige explicitamente proteção de dado sensível/PII. Esse requisito estava ausente da v1 do desenho e foi declarado na revisão v2 para todo componente que toca dado classificado como sensível/PII (ver `dados.md`: praticamente todas as entidades de BC1, BC2, BC3 e BC4 carregam classificação Sensível/PII ou Sensível/PII — RH). A plataforma agrega conteúdo de múltiplas áreas de negócio (Comercial, RH, Financeiro, TI) em componentes compartilhados (C3, LLM Gateway, C7), o que amplia a superfície de exposição se dado sensível trafegar ou for persistido sem proteção.

## Alternativas consideradas
Este requisito não foi tratado como uma escolha entre alternativas técnicas equivalentes — é uma exigência de linha de base derivada diretamente de RNF07 (fato firme, confirmado pelo negócio), não uma otimização opcional. A alternativa implícita descartada foi **não exigir criptografia de forma transversal e obrigatória**, deixando a decisão a critério de cada componente/mecanismo de implementação individualmente:

| Alternativa | Por que foi descartada |
|---|---|
| Criptografia tratada como boa prática recomendada, não como requisito obrigatório declarado | Dado que o desenho já tinha essa lacuna na v1 (achado real de Testes e Qualidade), deixar como recomendação implícita repete o mesmo risco de omissão silenciosa — para um requisito ligado a PII/RNF07, "recomendado" não é suficiente. |
| Criptografia só em trânsito, sem exigência de repouso (ou vice-versa) | Insuficiente: dado sensível em repouso sem criptografia (ex.: C3, C7) permanece exposto a acesso não autorizado ao armazenamento subjacente, mesmo que o transporte seja seguro; dado sensível em trânsito sem criptografia (mesmo dentro do perímetro interno da rede) fica exposto a interceptação. As duas frentes são necessárias, não intercambiáveis. |
| Exigência aplicada apenas a comunicação externa (fora do perímetro da rede) | Descartada explicitamente: o desenho fixa que "dado sensível não fica em texto claro em trânsito só porque a comunicação é interna" — perímetro de rede não é controle suficiente para dado classificado como sensível/PII. |

A decisão adotada (exigência transversal e obrigatória) é a única compatível com RNF07 como fato firme, dado o volume de componentes e fluxos que tocam dado sensível nesta plataforma (ver `dados.md`, praticamente todo o modelo de dados).

## Decisão
Exigir criptografia em trânsito e em repouso para todo componente que toca dado classificado como sensível/PII, como requisito não negociável de linha de base — não uma opção de configuração deixada para depois:

- **Em trânsito:** toda comunicação síncrona entre C1↔C2/C4, C2/C4↔C3, C2/C4↔C6, C2/C4↔LLM Gateway, e toda comunicação assíncrona via Kafka/AMQ Streams (C5→C3, C6→C7) que carregue `ContextoCorporativo`, `ChunkIndexado`, `Consulta`, `PedidoDeGeracao`, `DecisaoDeAcesso` ou `RegistroDeAuditoria` deve ser criptografada (TLS ou equivalente) — mesmo dentro do perímetro interno da rede.
- **Em repouso:** C3 (Índice de Conhecimento), C7 (Auditoria), qualquer armazenamento intermediário do LLM Gateway (cache de prompt/contexto, se houver) que persista dado sensível/PII, e qualquer buffer/staging de `ContextoCorporativo` em C5 antes da publicação do evento devem ter criptografia em repouso habilitada.

O mecanismo concreto (gestão de chaves, algoritmo, serviço de criptografia gerenciado vs. próprio) permanece escopo de Infraestrutura e Deployment e de Segurança e Compliance, condicionado à lacuna 5 (políticas de segurança concretas) e à escolha de provedor de cloud (já formalizada em ADR 012). O que este ADR fixa é a exigência em si: nenhum componente que toca PII pode ir a produção sem criptografia em trânsito e em repouso, independentemente de qual tecnologia a implementa.

## Consequências / Trade-offs aceitos
- **Custo/overhead operacional adicional** (gestão de chaves, criptografia mesmo em tráfego interno) aceito conscientemente como custo necessário dado RNF07 já ser fato firme — não é tratado como otimização a evitar por economia.
- **Mecanismo concreto ainda não fechado**: este ADR formaliza a exigência, não a implementação — risco de a implementação concreta ficar incompleta ou inconsistente entre componentes se não houver checklist/validação explícita antes de cada componente ir a produção (recomenda-se que o portão de saída geral do orquestrador confirme esse ponto por componente).
- **Aplicação transversal ampla**: como a maioria das entidades desta demanda é classificada como sensível/PII (ver `dados.md`), este requisito efetivamente cobre quase toda a plataforma — aceito como consequência direta e proporcional ao perfil real de dado da demanda, não como exagero.

## Coerência com o compêndio e ADRs anteriores
Nenhum ADR anterior desta casa trata de criptografia em trânsito/repouso como requisito formal — primeiro ADR desse tipo na casa. Não contradiz nenhuma decisão prévia. Reforça, de forma mais explícita, o espírito já presente em decisões anteriores desta casa sobre proteção de acesso a dado sensível sem canal dedicado pesado (ex.: ADR 006 e ADR 009, allowlist/autenticação de aplicação em vez de VPN) — ainda assim, não é o mesmo tema (aquelas tratam de perímetro de rede; esta trata de proteção do dado em si). Candidato a virar padrão geral da casa para qualquer demanda futura que toque PII — ainda não promovido a critério formal da seção 2 do compêndio, mas recomendável para avaliação nesse sentido dado que RNF07-like é provável de se repetir.

## Revisão
Pendente. Aguardando revisão explícita de pessoa sênior ou líder técnico do time antes de status mudar para "Aprovado".
