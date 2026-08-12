# Skill: Plano de Observabilidade, Telemetria e Métricas

## Quando usar
Duas frentes, as duas obrigatórias:
1. **Da solução entregue**, depois que o Desenho de Arquitetura (e idealmente Infraestrutura e Deployment) já existem, para definir o que vai ser medido em produção.
2. **Do próprio time de agentes**, contínuo, agregando o que cada agente já registra ao terminar uma atividade (regra de sempre em [[rules/always]]) num retrato único do fluxo inteiro.

## Dono
O agente "Observabilidade e Telemetria" é o dono desta atividade. Qualquer agente com dúvida sobre o que medir, como rastrear uma requisição entre serviços, ou quanto o próprio fluxo de agentes está gastando, pergunta a este agente em vez de adivinhar (regra de [[rules/never]]).

## Passos, frente 1 (solução entregue)
1. Leia o desenho de arquitetura e, para cada componente, defina quais métricas ele expõe (latência, taxa de erro, throughput, saturação).
2. Defina como rastrear uma requisição que passa por vários microsserviços (trace distribuído), cobrindo o caminho via API Gateway, integrações síncronas e eventos Kafka/AMQ Streams.
3. Defina os limites que, se ultrapassados, geram alerta, e para quem o alerta vai. Uma métrica sem limite de alerta é só um número sendo coletado, não observabilidade de verdade.

## Passos, frente 2 (telemetria do próprio time de agentes)
4. Registre, por demanda, o que é observável hoje sem inventar número: quais agentes rodaram, o que rodou em paralelo vs sequencial, e quando um loop de dúvida entre agentes bateu no limite de 3 rodadas e escalou (regra de [[rules/never]]). Isso vai em `telemetria-agentes.md` (contínuo, na raiz).
5. **Custo de processamento da demanda, hoje em nível agregado (Tier 1), não por agente.** Este agente **nunca estima ou inventa esse número**. Peça a quem operou a demanda para registrar o custo real da sessão, visível no painel de custo/billing do Claude Code (ou equivalente da plataforma usada), em `demandas/<nome-da-demanda>/custo-processamento.md`. Um número real e agregado, mesmo sem saber qual atividade pesou mais, é preferível a uma estimativa inventada por agente.
6. **Tier 2 (futuro, ainda não disponível):** quando as demandas passarem a rodar via execução real por subagente (ex: Workflow, onde cada atividade é uma chamada rastreável), o custo por agente passa a ser medido de verdade, não estimado. Até lá, não force um breakdown por atividade, registre isso como limitação conhecida em vez de forçar um número que ninguém mediu.

## Artefato de saída
Um documento `demandas/<nome-da-demanda>/observabilidade.md` (frente 1) com métricas por componente, estratégia de trace distribuído, e limites de alerta. Um registro contínuo `telemetria-agentes.md` (frente 2, na raiz, fora de `demandas/`, cresce com o tempo) com o que rodou, o paralelismo real vs planejado, e os loops que escalaram. E um documento `demandas/<nome-da-demanda>/custo-processamento.md` (frente 2, Tier 1) com o custo total real da sessão, preenchido por quem operou, nunca estimado pelo agente.

## Como é bem feito
Frente 1: dá para responder "o que vai acordar alguém se essa solução falhar em produção?" olhando só o documento. Frente 2: dá para responder "o que rodou, e quanto essa demanda custou no total?" com números reais, mesmo que ainda sem saber qual atividade pesou mais (isso é uma limitação conhecida e documentada, não escondida).
