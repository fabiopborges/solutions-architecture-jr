# Roteiro de agentes

Espelha `skills/roadmap.md`. Cada atividade só virou agente depois que a skill dela foi conquistada de verdade, para não construir um "gerente" de trabalho que ainda não existia. As 14 atividades originais, o Orquestrador, dois especialistas sob demanda, um agente transversal de geração de diagramas e Jornadas do Usuário estão prontos.

## Prontos (14 atividades + 2 especialistas sob demanda + 2 transversais + Orquestrador)
1. **Entendimento e Escopo** - `agents/entendimento-e-escopo/AGENT.md`
2. **Desenho de Arquitetura** - `agents/desenho-de-arquitetura/AGENT.md`
3. **Pesquisa e Benchmarking** (sob demanda, quando a stack aprovada não resolve) - `agents/pesquisa-e-benchmarking/AGENT.md`
4. **Trade-offs e ADR** (tem gate de aprovação humana próprio, além do geral) - `agents/trade-offs-e-adr/AGENT.md`
5. **Modelagem de Dados** (roda em paralelo com Infraestrutura, Testes e Pesquisa a partir do Desenho) - `agents/modelagem-de-dados/AGENT.md`
6. **Segurança e Compliance** (depende de Desenho e Modelagem de Dados, não roda em paralelo com eles) - `agents/seguranca-e-compliance/AGENT.md`
7. **Infraestrutura e Deployment** (roda em paralelo com Modelagem de Dados, Testes e Pesquisa, a partir do Desenho) - `agents/infraestrutura-e-deployment/AGENT.md`
8. **Estimativa de Custo** (depende de Infraestrutura e Deployment, roda em paralelo com Observabilidade frente 1 e Segurança) - `agents/estimativa-de-custo/AGENT.md`
9. **Observabilidade e Telemetria** (frente 1 depende do Desenho/Infra, frente 2 roda contínua fora da cadeia) - `agents/observabilidade-e-telemetria/AGENT.md`
10. **Testes e Qualidade** (roda em paralelo com Modelagem, Infra, Custo, Segurança e Observabilidade, a partir do Desenho) - `agents/testes-e-qualidade/AGENT.md`
11. **Documentação Final** (ponto de sincronização total, espera todos os ramos terminarem) - `agents/documentacao-final/AGENT.md`
12. **Riscos e Mitigação** (roda em paralelo com Documentação Final) - `agents/riscos-e-mitigacao/AGENT.md`
13. **Comunicação com Stakeholders** (depende de Documentação Final e Riscos, traduz o que já existe) - `agents/comunicacao-stakeholders/AGENT.md`
14. **Entrega e Handoff** (prepara em paralelo, só libera após a aprovação humana) - `agents/entrega-e-handoff/AGENT.md`
15. **Especialista em Dados e Analytics** (sob demanda, só quando há decisão de plataforma analítica, nunca por padrão) - `agents/especialista-dados-analytics/AGENT.md`
16. **Especialista em IA e Machine Learning** (sob demanda, só quando há decisão de modelo de IA/ML, nunca por padrão) - `agents/especialista-ia-ml/AGENT.md`
17. **Geração de Diagramas C4** (transversal, acionado por Desenho de Arquitetura e Documentação Final, formaliza diagramas a partir do que já foi decidido, não decide arquitetura — mesmo padrão do Trade-offs e ADR, deriva Container/Contexto de catálogo+sequências desde o MVP 7, nunca traduz desenho.md direto quando há jornada) - `agents/geracao-diagramas/AGENT.md`
18. **Jornadas do Usuário** (roda em paralelo com Modelagem de Dados, Infraestrutura, Testes e Pesquisa, a partir do Desenho — traduz RFs + componentes já decididos em jornadas observáveis, e emite o spec de sequência máquina-legível que alimenta a derivação do Container) - `agents/jornadas-do-usuario/AGENT.md`
19. **Orquestrador** (papel de gerente do loop, não de atividade) - `agents/orquestrador/AGENT.md`

Roteiro fechado de novo (com duas adições justificadas em 2026-08-15, ver `memory.md`: geração de diagramas virou agente transversal por resolver um problema real de dessincronização entre `desenho.md` e `documentacao-final.md` já observado numa demanda real; Jornadas do Usuário virou agente por dar o roteiro de sequência e a marcação de jornada que o gerador de diagramas consome). O próximo trabalho real é rodar uma demanda de verdade pela cadeia inteira usando os dois agentes novos, e testar se o critério de gatilho dos dois especialistas de dados/IA funciona na prática, não inventar mais um papel que ninguém pediu.
