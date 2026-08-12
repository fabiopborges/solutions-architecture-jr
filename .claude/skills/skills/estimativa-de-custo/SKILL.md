# Skill: Estimativa de Custo

## Quando usar
Depois que Infraestrutura e Deployment define como e onde cada componente roda. Não estima custo de algo que ainda não tem hospedagem definida.

## Dono
O agente "Estimativa de Custo" é o dono desta atividade. Qualquer agente com dúvida sobre quanto um componente custa, ou por que um provedor foi preferido em termos de custo, pergunta a este agente em vez de adivinhar (regra de [[rules/never]]).

## Passos
1. Leia o documento de infraestrutura e deployment e, para cada componente, estime o custo de rodar (cômputo, banco, mensageria) no provedor já escolhido.
2. Quando um componente poderia rodar em mais de um provedor viável (a stack é agnóstica, ver `substrate/compendium.md`), compare o custo entre eles antes de considerar a escolha fechada, e leve essa comparação para [[agents/infraestrutura-e-deployment/AGENT]] se o custo mudar a decisão, sem esquecer que custo é só um dos critérios de negócio, não o único.
3. Liste custo de licenciamento e ferramentas de terceiros que a solução vai usar, separado do custo de infraestrutura pura.
4. Monte a estimativa quebrada por componente, nunca só um número total somado.

## Artefato de saída
Um documento `demandas/<nome-da-demanda>/custo.md` com: custo por componente (infraestrutura), comparação entre provedores onde mais de um era viável, custo de licenciamento/terceiros, e o total como soma visível das partes.

## Como é bem feito
Dá para ver o custo por componente, não só um número total solto, e alguém consegue apontar exatamente qual peça da arquitetura pesa mais no orçamento.
