# Skill: Definição de Infraestrutura e Deployment

## Quando usar
Depois que o Desenho de Arquitetura existe. Parte dos componentes já definidos, não decide infraestrutura antes de saber o que precisa rodar.

## Dono
O agente "Infraestrutura e Deployment" é o dono desta atividade. Qualquer agente com dúvida sobre onde ou como um componente roda, ou por que um provedor/região foi escolhido, pergunta a este agente em vez de adivinhar (regra de [[rules/never]]).

## Passos
1. Leia o desenho de arquitetura e, para cada componente, defina como ele vai ser hospedado e implantado (container, serviço gerenciado, função, etc). Nenhum componente fica sem essa definição.
2. **Escolha o provedor de cloud por componente, sem preferência fixa** (a stack é agnóstica de provedor, ver `substrate/compendium.md` seção 2). Considere todas as opções viáveis (AWS, Azure, GCP, OCI, on-prem, híbrido) contra os critérios de negócio: custo, residência e compliance de dados, latência para o usuário final, maturidade do serviço gerenciado que aquele componente específico precisa, risco de vendor lock-in, e qualquer restrição de negócio que o Desenho de Arquitetura tenha sinalizado. Se a comparação não for óbvia, aciona [[agents/pesquisa-e-benchmarking/AGENT]] em vez de decidir no escuro.
3. Registre o porquê da escolha de provedor para essa demanda específica, ligado aos critérios do passo 2, não decida sem justificar. Escolhas diferentes de provedor entre demandas são esperadas, cada uma segue a necessidade de negócio dela.
4. Defina como cada componente escala (o que acontece se o uso subir) e como fica disponível (o que garante que continua no ar se algo falhar).
5. Descreva como API Gateway e Load Balancer entram no deployment, o que passa por eles e como, independente do provedor.
6. Se a definição depender de uma escolha de tecnologia que a stack aprovada não resolve, aciona [[agents/pesquisa-e-benchmarking/AGENT]] em vez de decidir sozinho.

## Artefato de saída
Um documento `demandas/<nome-da-demanda>/infraestrutura.md` com: componente x como é hospedado/implantado, provedor escolhido por componente e o porquê (ligado aos critérios de negócio), estratégia de escala e disponibilidade, e papel do API Gateway/Load Balancer.

## Como é bem feito
Todo componente do desenho tem um jeito de rodar definido, dá para ver como o deployment lida com escala e disponibilidade, e o porquê da escolha de provedor está escrito e ligado a um critério de negócio real, não a hábito ou preferência.
