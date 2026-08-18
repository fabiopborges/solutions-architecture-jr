# Skill: Entrega Final e Handoff

## Quando usar
É a última atividade da cadeia. Prepara o material assim que Comunicação com Stakeholders termina, mas só libera de fato depois que a aprovação humana do gate do Orquestrador acontece. Preparar e liberar são passos separados.

## Dono
O agente "Entrega e Handoff" é o dono desta atividade. Qualquer dúvida do time de desenvolvimento depois que os agentes "saem de cena" é direcionada por este agente para o dono certo de cada área, ele não responde a dúvida técnica sozinho (regra de [[rules/never]]).

## Passos
1. Assim que [[agents/comunicacao-stakeholders/AGENT]] termina, comece a organizar o pacote final ([[agents/documentacao-final/AGENT]]) e todos os ADRs aprovados ([[agents/trade-offs-e-adr/AGENT]]) de um jeito que o time de desenvolvimento saiba por onde começar, não é só uma pasta de documentos soltos.
2. Quebre a arquitetura aprovada em itens/épicos iniciais, prontos para entrar no backlog (Jira/Linear).
3. Monte a tabela de "quem responde o quê": para cada área (dados, segurança, infraestrutura, custo, observabilidade), aponte qual agente é a referência para dúvidas futuras, já que os agentes não acompanham a implementação dia a dia.
4. Espere a confirmação do gate de aprovação humana do [[agents/orquestrador/AGENT]]. Sem essa confirmação, o material fica pronto mas não é liberado como "entregue".
5. Depois de liberado, registre a entrega em `substrate/compendium.md` como uma decisão concluída, para a próxima demanda encontrar esse histórico.

## Artefato de saída
Um documento `demandas/<nome-da-demanda>/handoff.md` com: pacote final + ADRs organizados, lista de épicos iniciais para backlog, e a tabela de referência por área. Status: preparado ou liberado.

## Como é bem feito
O time de desenvolvimento consegue começar a construir sem precisar reabrir cada documento de origem do zero, sabe exatamente por onde começar no backlog, e sabe a quem perguntar quando tiver dúvida em cada área.
