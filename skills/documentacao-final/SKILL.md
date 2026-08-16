# Skill: Documentação Final e Diagramas

## Quando usar
É um ponto de sincronização real: só começa depois que todos os ramos paralelos da cadeia terminam (Desenho, Modelagem de Dados, Segurança, Infraestrutura, Custo, Observabilidade, Testes e Qualidade, e qualquer Pesquisa/ADR que tenha rodado). Não adianta montar antes, porque juntaria peças incompletas.

## Dono
O agente "Documentação Final" é o dono desta atividade. Qualquer agente com dúvida sobre onde uma decisão ficou registrada no pacote final pergunta a este agente em vez de adivinhar (regra de [[rules/never]]).

## Passos
1. Confirme que todos os documentos de entrada existem: entendimento e escopo, desenho de arquitetura, modelagem de dados, segurança e compliance, infraestrutura e deployment, estimativa de custo, observabilidade, testes e qualidade, e os ADRs aprovados. `jornadas.md` é opcional (nem toda demanda tem gatilho de jornada) — se existir, use no passo 2. Se algum documento obrigatório estiver faltando, o pacote não está pronto, não preencha a lacuna com suposição.
2. Sinalize explicitamente que [[agents/geracao-diagramas/AGENT]] precisa ser acionado (você não tem como despachá-lo diretamente — subagentes não despacham outros subagentes, quem despachou seu trabalho precisa fazer isso) para consolidar/atualizar (a) o diagrama de componentes/integrações (C4 Container) a partir do desenho de arquitetura — se `jornadas.md` existir, peça também as visões filtradas por jornada e o(s) diagrama(s) de sequência; e (b) o diagrama de fluxo de dados a partir da modelagem de dados (mostrando eventos vs. consultas entre serviços). Não desenhe ASCII art manual nem monte tabela substituindo diagrama aqui — isso é escopo dele (2026-08-16: o diagrama de fluxo de dados deixou de ser montado como tabela por este agente, mesma regra que já valia pro Container).
3. Referencie o diagrama de fluxo de dados gerado (passo 2b) por caminho — não descreva o fluxo de novo em prosa/tabela, o diagrama já é a fonte de leitura.
4. Monte o diagrama de infraestrutura/deployment a partir de infraestrutura e deployment, mostrando onde cada componente roda e em qual provedor (a stack é agnóstica, o diagrama mostra o que foi escolhido para essa demanda específica, não assume um provedor fixo).
5. Junte tudo num único documento final, organizado por seção, cada seção citando de qual documento de entrada ela veio (incluindo os diagramas gerados, referenciados por caminho em `demandas/<nome-da-demanda>/diagramas/`), para quem revisar conseguir voltar à fonte.

## Índice com ordem de leitura
O índice no topo do pacote final não é só uma lista de links — é a ordem em que um humano deveria ler os documentos de origem para entender a demanda do zero. Adicione uma coluna "Ordem de leitura" à tabela do índice:
- Numeração crescente para documentos sequenciais (a atividade seguinte depende do resultado da anterior): `01` (Entendimento), `02` (Desenho).
- Sufixo de letra para documentos que rodaram em paralelo a partir do mesmo ponto de dependência — não importa a ordem entre eles, mas importa saber que dependem do mesmo antecessor: `03a` (Modelagem de Dados), `03b` (Infraestrutura), `03c` (Testes e Qualidade), `03d` (Jornadas do Usuário, se existir), `03e` (Pesquisa, se existir) — todos dependem só do Desenho.
- Segunda onda de paralelismo (depende de resultados da primeira onda, não só do Desenho): `04a` (Segurança, depende de Desenho + Dados), `04b` (Custo, depende de Infraestrutura), `04c` (Observabilidade frente 1, depende de Desenho/Infraestrutura).
- Sincronização final: `05a` (este pacote), `05b` (Riscos e Mitigação, roda em paralelo com este).
- Cadeia final sequencial: `06` (Comunicação com Stakeholders, artefato `comunicacao.md`), `07` (Entrega e Handoff). Você roda antes desses dois — se ainda não existirem quando você monta o índice pela primeira vez, deixe as linhas de fora; quem mantiver o pacote depois (ou você mesmo, se for revisitado) completa o índice quando esses artefatos existirem.
- ADRs não entram na numeração principal (são transversais, disparados no momento da decisão) — marque como `—` na coluna de ordem e cite entre parênteses qual atividade os disparou.
- `custo-processamento.md` e `telemetria-agentes.md` (frente 2 de Observabilidade — custo de operação do próprio time de agentes, não da solução) **não entram na numeração**: não fazem parte da narrativa de arquitetura que o índice ordena. Se citá-los no pacote, marque como `— (meta, fora da ordem de leitura da solução)`.
Ajuste os números se a demanda não tiver algum ramo opcional (ex: sem Pesquisa, sem Jornadas) — a numeração reflete quem realmente rodou nesta demanda, não um template fixo.

## Esqueleto fixo (padronização entre demandas)
Este documento não tem estrutura livre. Siga `templates/documentacao-final.template.md`: os headers (nível e texto) são fixos e aparecem na mesma ordem em toda demanda — só o conteúdo dentro de cada seção varia. Seções marcadas `[CONDICIONAL]` no template só entram se o artefato de origem existir nesta demanda (ex: sem `jornadas.md`, sem seção de Jornadas); ao omitir uma seção condicional, renumere as seguintes para não deixar buraco na numeração dos headers. Isso é o que permite a um humano comparar pacotes de demandas diferentes sem reaprender a estrutura a cada leitura.

## Artefato de saída
Um documento `demandas/<nome-da-demanda>/documentacao-final.md`, seguindo o esqueleto de `templates/documentacao-final.template.md`, com as seções de todos os agentes anteriores resumidas, os diagramas, e o índice com ordem de leitura no topo.

## Como é bem feito
Qualquer pessoa do time consegue ler o pacote final sozinha, entender a solução de ponta a ponta (o que foi pedido, o que foi desenhado, como os dados fluem, onde roda, quanto custa, como é observado, e onde a qualidade foi checada), sem precisar abrir os documentos de origem, mas sabendo onde estão se precisar.
