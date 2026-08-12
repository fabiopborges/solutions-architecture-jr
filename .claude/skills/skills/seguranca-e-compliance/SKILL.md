# Skill: Definição de Segurança e Compliance

## Quando usar
Depois que o Desenho de Arquitetura e a Modelagem de Dados existem. Não começa do zero, parte do que essas duas atividades já produziram.

## Dono
O agente "Segurança e Compliance" é o dono desta atividade. Qualquer agente com dúvida sobre como uma integração é autenticada, como um dado sensível é protegido, ou se algo fere um requisito de compliance, pergunta a este agente em vez de adivinhar (regra de [[rules/never]]).

## Passos
1. Leia o desenho de arquitetura e, para cada integração entre componentes (incluindo o que passa pelo API Gateway e Load Balancer), defina como ela é autenticada e autorizada. Nenhuma integração fica sem essa definição.
2. Leia a modelagem de dados e, para cada entidade marcada como sensível, defina o tratamento (criptografia, mascaramento, controle de acesso). Isso reaproveita o que a Modelagem de Dados já sinalizou, não reavalia a sensibilidade do zero.
3. Liste os requisitos de compliance regulatório que se aplicam (ex: LGPD, quando há dado pessoal), independente da demanda específica.
4. Se algo no desenho ou na modelagem violar um requisito de compliance, sinalize o conflito para os agentes donos deles ([[agents/desenho-de-arquitetura/AGENT]] ou [[agents/modelagem-de-dados/AGENT]]) em vez de tentar corrigir a arquitetura ou o dado por conta própria.

## Artefato de saída
Um documento `demandas/<nome-da-demanda>/seguranca.md` com: autenticação/autorização por integração, tratamento por dado sensível, requisitos de compliance aplicáveis, e conflitos sinalizados (se houver).

## Como é bem feito
Cada dado sensível listado na modelagem de dados tem um tratamento explícito, nenhum fica sem resposta, e dá para apontar exatamente onde a autenticação e a autorização acontecem em cada integração do desenho.
