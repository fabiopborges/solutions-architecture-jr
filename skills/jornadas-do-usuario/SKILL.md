# Skill: Jornadas do Usuário

## Quando usar
Depois que o Desenho de Arquitetura termina, para toda demanda que tenha requisito funcional observável por um usuário final. Não usar para: mudança puramente técnica/interna sem jornada de usuário associada (ex: troca de biblioteca, refatoração sem mudança de comportamento) — nesse caso, sinaliza ausência de gatilho e devolve.

## Dono
O agente "Jornadas do Usuário" é o dono desta atividade — nenhum outro agente organiza requisitos em jornada por conta própria (regra de [[rules/never]]).

## Passos
1. Leia `entendimento.md` (RFs aprovados) e `desenho.md` (componentes, bounded contexts, integrações) por completo antes de agir. **Reaproveite os `id` canônicos que o Desenho de Arquitetura atribuiu a cada componente/ator — nunca invente seu próprio esquema de ID.** Isso é o que permite ao catálogo estático (produzido por [[agents/geracao-diagramas/AGENT]] a partir do mesmo `desenho.md`) e às suas sequências apontarem pro mesmo componente sem gerar `[FALTA-CATALOGO]`/`[ORFAO]` por descompasso de nomenclatura (já aconteceu numa execução real).
2. Agrupe os RFs em jornadas por resultado observável pelo usuário final — não force CRUD como molde único; use CRUD como checklist para não esquecer operação óbvia (criar/consultar/atualizar/excluir), mas a jornada real pode ser orientada a evento, fluxo de aprovação, etc.
3. Para cada jornada, numere o passo a passo de participação dos componentes (ex: C1 → C2 → C4), na ordem real de execução — isso é a base direta para o diagrama de sequência de cada jornada.
4. Marque, por jornada, quais conexões do `desenho.md` participam, usando um `journey_id` (slug curto, ex: `lead-notificado`) — essa marcação é o que permite ao [[agents/geracao-diagramas/AGENT]] gerar depois uma visão de Container filtrada por jornada, sem redesenhar o diagrama do zero.
5. **Grave também, por jornada, o spec de sequência máquina-legível** em `demandas/<nome-da-demanda>/diagramas/sequencia-<journey_id>_spec.json`, no formato de `docs/diagrams/c4-schema.md` (seção "Pipeline invertido") — mensagens numeradas (`ordem`), com `de`/`para`/`rotulo`/`protocolo`/`assincrona`/`tipo` (`chamada` para o passo a passo real, `self` para uma etapa interna do mesmo componente, `retorno` só quando for de fato uma resposta que não deve virar seta própria no Container). Este arquivo é a fonte que [[agents/geracao-diagramas/AGENT]] usa para **derivar** o Container automaticamente — não é redundante com `jornadas.md`, é a versão que uma máquina consegue processar.
6. Confira que todo RF funcional-observável está coberto por ao menos uma jornada; se não estiver, registre como lacuna explícita, não invente cobertura.
7. Se uma jornada expõe uma lacuna de desenho (integração que não existe) ou uma dúvida sobre o requisito, pergunte ao agente dono ([[agents/desenho-de-arquitetura/AGENT]] ou [[agents/entendimento-e-escopo/AGENT]]) em vez de decidir.

## Artefato de saída
`demandas/<nome-da-demanda>/jornadas.md` — versão legível por humano, com nome, `journey_id`, RF(s) de origem, passo a passo numerado, e a marcação de participação por componente/conexão. Mais `demandas/<nome-da-demanda>/diagramas/sequencia-<journey_id>_spec.json`, um por jornada — versão máquina-legível, consumida por [[agents/geracao-diagramas/AGENT]] via `docs/diagrams/c4-gerador/derivar_c4.py` para derivar o Container/Contexto sem risco de divergir do que a jornada realmente descreve.

## Como é bem feito
Toda jornada é rastreável a um RF real e a componentes reais do desenho — nenhuma inventada, nenhuma faltando cobertura sem justificativa.
