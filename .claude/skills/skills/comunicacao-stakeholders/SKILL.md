# Skill: Comunicação e Apresentação para Stakeholders

## Quando usar
Depois que Documentação Final e Riscos e Mitigação existem. Não é uma atividade técnica nova, é uma tradução do que já foi decidido para quem vai aprovar.

## Dono
O agente "Comunicação com Stakeholders" é o dono desta atividade. Qualquer agente com dúvida sobre como algo foi traduzido para o público não técnico pergunta a este agente em vez de adivinhar (regra de [[rules/never]]).

## Passos
1. Leia o pacote final de [[agents/documentacao-final/AGENT]] e o plano de riscos de [[agents/riscos-e-mitigacao/AGENT]]. Não decide nada novo, traduz o que já existe.
2. Reescreva em linguagem sem jargão de arquitetura. Troque termos técnicos por explicações simples (ex: "microsserviço" vira "um pedaço independente do sistema que pode ser trocado sem parar o resto").
3. Foque no que muda para o negócio: custo total, prazo estimado, e o risco principal priorizado por [[agents/riscos-e-mitigacao/AGENT]]. Detalhe técnico completo fica no pacote final, não aqui.
4. Reaproveite os diagramas já prontos da Documentação Final, simplificados, tirando detalhe técnico que não ajuda quem não é da área.
5. Termine com uma pergunta clara: o que precisa de aprovação ou decisão de quem está lendo. Não é só informativo.

## Artefato de saída
Um documento `demandas/<nome-da-demanda>/apresentacao.md` (ou slides, se o formato pedir) com: resumo em linguagem simples, custo/prazo/risco principal, diagramas simplificados, e a pergunta de aprovação no final.

## Como é bem feito
Um stakeholder não técnico consegue ler e entender o que foi decidido e por quê, e sabe exatamente o que precisa aprovar ou decidir depois de ler.
