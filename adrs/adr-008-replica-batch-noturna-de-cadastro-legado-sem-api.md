# ADR 008: Réplica leve de dados mestres via sincronização em lote noturna (batch, 1x/dia), como padrão para consumir cadastro de sistema legado sem API, para o Projeto Nuvem Vendas (projeto-nuvem-vendas-v1)

**Status:** Aprovado.
**Revisado por:** Fabio Borges, Arquiteto de Soluções, em 2026-08-10
**Data de registro:** 2026-08-10
**Demanda que originou:** `demandas/projeto-nuvem-vendas-v1/` (fica global em `adrs/` para poder ser reaproveitado por demandas futuras, mesmo tendo nascido nesta — o próprio dono do negócio sinalizou que esta decisão pode ajudar projetos futuros, o que reforça a importância de registrá-la com cuidado de padrão, não só como nota pontual desta demanda)
**Escopo:** esta decisão vale como padrão candidato para qualquer demanda futura que precise consumir cadastro/dados mestres de um sistema legado sem API e sem poder modificá-lo, aceitando defasagem de dados como trade-off consciente. Não é ainda um padrão geral automático da casa — fica registrado aqui para ser reaproveitado por avaliação explícita em cada nova demanda, não copiado sem essa mesma análise de criticidade/frescor de dados por trás (mesmo cuidado já registrado no ADR 007 para o padrão de mensageria).

## Contexto

O Projeto Nuvem Vendas precisa referenciar o cadastro de clientes ao criar/fechar um pedido de venda (RF01/RF02). O cadastro de clientes existe hoje só no ERP legado (Delphi + Firebird on-premises), que não tem API nem mecanismo de integração (RNF09) e não pode ser alterado pela TI interna — único acesso possível é direto às tabelas do Firebird, com driver Jaybird/JDBC (já decidido por Pesquisa e Benchmarking em `pesquisa-acesso-firebird.md`).

O dono do negócio decidiu explicitamente: o cadastro de clientes **não migra** para a nuvem e **não é escrito** por ela. Continua 100% no Firebird, gerido pelo Delphi como hoje. O BC Vendas só precisa de uma referência do cliente ao montar um pedido, não do cadastro completo em tempo real (RF01/RF02 não exigem isso).

## Alternativas consideradas

- **Leitura direta em tempo real no Firebird a cada operação do BC Vendas:** descartada. Geraria acesso concorrente e não controlado a um banco de um sistema desktop não projetado para carga externa, reabrindo o mesmo tipo de risco de contenção/travamento que motivou o projeto inteiro (o ERP já trava sob concorrência, é o problema original da demanda). Também criaria uma dependência de rede em tempo real do fechamento de pedido até o ambiente on-premises, aumentando a superfície de indisponibilidade do fluxo crítico (RNF01).
- **Migração completa do cadastro de clientes para a nuvem, com o BC Vendas passando a ser dono dele:** descartada por decisão explícita do dono do negócio — o cadastro de clientes não é uma capacidade de negócio no escopo desta demanda (não existe bounded context de "Cadastro de Cliente"), e migrar dados mestres de um sistema de registro legado é uma mudança de escopo maior, com implicações de governança de dados que esta demanda não pediu para resolver.
- **CDC (Change Data Capture) / replicação em tempo quase real a partir do Firebird:** não avaliada tecnicamente a fundo (não foi acionado Pesquisa e Benchmarking para isso), mas descartada preliminarmente por desproporção: exigiria infraestrutura adicional (agente de CDC, ferramenta de replicação) para um requisito que não pede frescor em tempo real, e o teto de RNF08 (<R$300/mês para a demanda inteira) já está sob tensão sem esse componente extra.
- **Sincronização em lote noturna (batch, 1x/dia), com um novo componente de leitura-apenas:** escolhida, ver decisão.

## Decisão

Criar um **Script de Exportação de Clientes** (componente novo, a construir — não altera o código Delphi, apenas lê o Firebird) que roda **uma vez por dia, em horário de madrugada** (fora do expediente, para não competir com o uso do ERP nem com o Adaptador de Legado). O script:

1. Lê as tabelas de cliente do Firebird via o mesmo mecanismo de acesso já decidido (driver Jaybird/JDBC), reaproveitando a decisão existente em vez de introduzir um segundo mecanismo de acesso ao mesmo banco.
2. Envia os dados para uma **API de sincronização em lote** exposta pelo próprio Serviço de Pedidos (upsert em lote), que grava em uma **Réplica de Cliente** — uma coleção somente-leitura dentro do banco do BC Vendas, sem custo adicional de infraestrutura (mesmo banco do componente já existente).
3. Nunca escreve direto no banco do BC Vendas por fora do contrato de API — preserva a regra de nunca acessar o modelo interno de outro contexto sem passar pela API dele.

A Réplica de Cliente é lida localmente pelo BC Vendas ao montar/fechar um pedido — leitura rápida, sem depender de rede em tempo real até o Firebird.

## Consequências e trade-offs aceitos

- **Ganho:** nenhuma modificação no sistema legado (respeita a restrição dura de RNF09), sem infraestrutura adicional de replicação/CDC, sem custo extra de nuvem (reaproveita o banco já existente do Serviço de Pedidos), e sem gerar concorrência de leitura sobre o Firebird durante o horário de uso do ERP (leitura roda de madrugada).
- **Trade-off central, assumido conscientemente e não escondido: defasagem de até 24h.** Um cliente cadastrado hoje no Firebird só aparece na Réplica de Cliente na madrugada seguinte. Isso é aceitável para o escopo confirmado (referência de cliente no pedido, não cadastro completo em tempo real), mas tem uma consequência concreta ainda **não validada com o solicitante**: se a operação de vendas precisar fechar pedido para um cliente cadastrado no mesmo dia, esse fluxo não é coberto como está (risco 4 do desenho, `demandas/projeto-nuvem-vendas-v1/desenho.md`). Antes deste ADR ser considerado aprovado, recomenda-se que quem revisar confirme se essa validação de negócio já aconteceu.
- **Risco aceito conscientemente: falha silenciosa da sincronização.** Se o Script de Exportação falhar (rede fora, Firebird em backup no horário, erro de dados), a Réplica de Cliente fica desatualizada por mais de 24h sem que ninguém perceba, a menos que haja alerta dedicado. Sinalizado para o agente de Observabilidade nesta demanda.
- **Risco aceito conscientemente: componente novo sem dono de implementação definido.** O Script de Exportação não é claramente responsabilidade do time Delphi (que não constrói nada de nuvem) nem, até este ADR, de nenhum dos serviços já desenhados — precisa de atribuição explícita antes do planejamento de prazo.
- **Risco aceito conscientemente: concentração de dependência crítica.** O Script de Exportação reaproveita a mesma conectividade segura (ex.: VPN site-to-site) que o Adaptador de Legado já precisa até o ambiente on-premises. Isso reduz custo/duplicação, mas concentra risco: se o link cair, tanto a integração de faturamento/estoque quanto a sincronização de clientes param.

## Quando este padrão se aplica a demandas futuras (orientação de reaproveitamento)

Este padrão é candidato a reaproveitamento sempre que uma demanda futura precisar consumir dados mestres/cadastrais de um **sistema legado sem API e que não pode ser alterado**, e a capacidade de negócio nova **não exigir frescor em tempo real** desses dados (só referência, não fonte de verdade). Antes de copiar o padrão sem reavaliar:

- Confirmar que a defasagem aceita (aqui, até 24h) é de fato tolerável para o caso de uso novo — não é um número universal, foi calibrado para o volume/operação desta demanda específica.
- Confirmar que o legado de origem não tem, nem terá em breve, alguma forma de API/evento que tornaria um batch noturno desnecessariamente atrasado frente a uma alternativa mais simples.
- Não pular a validação de negócio equivalente ao risco 4 desta demanda (cenário de dado "novíssimo" não disponível ainda na réplica) — isso é específico do caso de uso e precisa ser revalidado a cada demanda, não herdado como resolvido.

## Aprovação

O dono do negócio já sinalizou, ao originar esta demanda, que esta decisão pode servir de referência para projetos futuros — o que torna a aprovação formal ainda mais importante de buscar ativamente, não deixar parada. Este ADR **precisa** ser levado a uma pessoa sênior ou líder técnico do time para revisão antes de ser considerado aprovado e antes de seu resumo entrar em `substrate/compendium.md` seção 3. Enquanto isso não acontece, o status permanece **Proposto**, mesmo que a decisão pareça tecnicamente correta.
