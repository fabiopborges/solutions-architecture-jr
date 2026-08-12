# Skill: Especialista em Dados e Analytics

## Quando usar
Só quando a demanda envolve, de fato, uma decisão de **plataforma de dados analíticos**: data warehouse, data lake, pipeline de ingestão/ETL, ferramenta de BI, ou arquitetura de dados para análise (diferente de dados transacionais de um microsserviço em produção).

**Não** é acionado para modelagem de dados de produção comum (entidades, dono, retenção, fluxo entre serviços via evento/API), isso continua sendo [[agents/modelagem-de-dados/AGENT]]. Se a demanda não tem nenhuma necessidade analítica real, este agente nem entra.

## Dono
O agente "Especialista em Dados e Analytics" é o dono desta atividade quando ela é acionada. Qualquer agente com dúvida sobre uma decisão de plataforma de dados analíticos pergunta a este agente em vez de decidir por conta própria (regra de [[rules/never]]).

## Quem aciona
[[agents/entendimento-e-escopo/AGENT]] sinaliza no escopo se já vê necessidade analítica na demanda. [[agents/desenho-de-arquitetura/AGENT]] ou [[agents/modelagem-de-dados/AGENT]] acionam durante o próprio trabalho se encontrarem essa necessidade. Não é consultado por padrão, é sob demanda, como [[agents/pesquisa-e-benchmarking/AGENT]].

## Passos
1. Confirme que a demanda de fato precisa de plataforma analítica, não é só modelagem de dados transacional. Se não precisar, devolve ao agente que acionou.
2. Avalie a necessidade contra os requisitos não funcionais do escopo (volume de dados, latência de consulta analítica, frequência de atualização, quem consome: dashboard, relatório, outro sistema).
3. Compare as opções de plataforma (data warehouse vs data lake vs solução híbrida, ferramenta de ingestão/ETL) contra os critérios de negócio de cloud do compêndio (custo, compliance/residência de dados). Aciona [[agents/pesquisa-e-benchmarking/AGENT]] se a comparação não for óbvia.
4. Se a plataforma vai alimentar um pipeline de treino de IA/ML, aciona [[agents/especialista-ia-ml/AGENT]] para a parte de modelo, este agente só decide onde e como os dados ficam disponíveis, não o que é feito com eles em termos de modelo.
5. Registre o porquê da recomendação, ligado ao requisito ou critério de negócio (regra de sempre expor suposições e trade-offs). Decisão importante vira ADR via [[agents/trade-offs-e-adr/AGENT]].

## Artefato de saída
Um documento `demandas/<nome-da-demanda>/dados-analytics.md` com: necessidade que motivou a consulta, recomendação de plataforma, o porquê ligado a requisito/critério de negócio, e se alimenta algum pipeline de IA/ML. Se a demanda não precisava de especialista, um retorno curto dizendo isso.

## Como é bem feito
A escolha de plataforma analítica tem um porquê ligado a volume/latência/consumo real, e nenhuma demanda sem necessidade analítica foi atrasada esperando esse agente à toa.
