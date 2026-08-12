# Ferramentas / Conexões

Como os agentes alcançam fontes de dados reais. Somente leitura por padrão, nenhum segredo mora nesta pasta.

## Hoje
Nenhuma conexão externa está ligada ainda. Os agentes trabalham só com o que está em `substrate/` e com os documentos que eles mesmos geram (como `entendimento-<demanda>.md`). Isso é suficiente para começar.

## Planejadas (a conectar quando fizer sentido)

| Fonte | Para que serve | Acesso | Como conectar depois |
|---|---|---|---|
| Repositório de código/documentação (Git, Confluence, Notion) | Trazer ADRs, diagramas e documentação de sistemas existentes de verdade para dentro de `substrate/compendium.md` | Somente leitura | Um conector já existente (ex: integração nativa) ou uma skill de sincronização que copia o conteúdo relevante para o compêndio |
| Ferramenta de backlog/projeto (Jira, Linear) | Trazer a demanda original e os requisitos de negócio para o agente de Entendimento e Escopo | Somente leitura | Um pequeno wrapper de linha de comando ou integração nativa que lê o card/ticket da demanda |
| Ferramenta de observabilidade real (Grafana, Datadog) | Dar ao agente de observabilidade dados reais de sistemas em produção, em vez de só propor métricas no vácuo | Somente leitura | Integração nativa de leitura de dashboards/métricas |

## Segredos
Nenhum segredo (senha, chave de API, token) deve morar nesta pasta. Quando qualquer uma das conexões acima for ligada de verdade, as credenciais ficam fora daqui, num cofre de segredos ou variável de ambiente do lado de fora do OS.
