# Skill: Modelagem de Dados

## Quando usar
Depois que o Desenho de Arquitetura definiu os componentes/serviços da solução. Roda em paralelo com outras atividades que não dependem dela (ex: Pesquisa e Benchmarking de uma tecnologia não relacionada a dados).

## Dono
O agente "Modelagem de Dados" é o dono desta atividade. Qualquer agente com dúvida sobre a estrutura de uma entidade, quem é dono de um dado, ou como dois serviços trocam dados entre si, pergunta a este agente em vez de adivinhar (regra de [[rules/never]]).

## Passos
1. Leia o documento de entendimento e escopo e identifique as entidades principais a partir dos requisitos funcionais (ex: pedido, cliente, pagamento), não a partir de uma tabela genérica.
2. Leia o desenho de arquitetura e, para cada entidade, defina qual componente/microsserviço é o dono (owner) dela, a fonte da verdade. Nenhuma entidade fica sem dono.
3. Descreva como os dados fluem entre serviços: o que é publicado como evento (Kafka/AMQ Streams) para outros consumirem, e o que é consultado direto via API. Um serviço não lê o banco de outro diretamente, isso quebra o padrão de microsserviços.
4. Para cada entidade, registre retenção (por quanto tempo guardar) e sensibilidade (se é dado pessoal ou sensível e precisa de tratamento especial).
5. Se a entidade precisar de algo que MongoDB (padrão da casa) não resolve bem, aciona [[agents/pesquisa-e-benchmarking/AGENT]] em vez de escolher outro banco por conta própria.

## Artefato de saída
Um documento `demandas/<nome-da-demanda>/dados.md` com: lista de entidades, dono de cada uma, fluxo entre serviços (evento vs consulta direta), e retenção/sensibilidade.

## Como é bem feito
Dá para saber, para qualquer dado da solução, quem é o dono dele e como qualquer outro serviço consegue enxergá-lo, sem ninguém precisar ler o banco de outro serviço diretamente para descobrir.
