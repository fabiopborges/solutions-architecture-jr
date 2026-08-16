# Skill: Jornadas do Usuário

## Quando usar
**Sempre, incondicionalmente, depois que o Desenho de Arquitetura termina** — despachado na mesma leva paralela de Modelagem de Dados/Infraestrutura e Deployment/Testes e Qualidade, nunca como decisão implícita de quem orquestra (2026-08-16: o despacho já foi pulado por julgamento de sessão, mesmo numa demanda com usuário final claro — ver `memory.md`). O critério de "requisito funcional observável por um usuário final" continua existindo, mas não decide mais SE este agente roda — decide o CONTEÚDO do artefato de saída (jornadas reais vs. veredito explícito de ausência, ver seção "Artefato de saída"). Para demanda puramente técnica/interna sem jornada de usuário associada (ex: troca de biblioteca, refatoração sem mudança de comportamento), o agente roda do mesmo jeito e produz `jornadas.md` com veredito de ausência — nunca deixa de rodar, e nunca deixa de gerar o arquivo.

## Dono
O agente "Jornadas do Usuário" é o dono desta atividade — nenhum outro agente organiza requisitos em jornada por conta própria (regra de [[rules/never]]).

## Passos
0. **Antes de agrupar qualquer coisa, decida o veredito**: esta demanda tem ao menos um RF observável por um usuário final, ou é puramente técnica/interna (ex: troca de biblioteca, refatoração sem mudança de comportamento)? Essa é a mesma régua de sempre — só que agora o resultado sempre vira artefato (passo 6 abaixo), nunca um retorno silencioso sem arquivo.
1. Leia `entendimento.md` (RFs aprovados) e `desenho.md` (componentes, bounded contexts, integrações) por completo antes de agir. **Reaproveite os `id` canônicos que o Desenho de Arquitetura atribuiu a cada componente/ator — nunca invente seu próprio esquema de ID.** Isso é o que permite ao catálogo estático (produzido por [[agents/geracao-diagramas/AGENT]] a partir do mesmo `desenho.md`) e às suas sequências apontarem pro mesmo componente sem gerar `[FALTA-CATALOGO]`/`[ORFAO]` por descompasso de nomenclatura (já aconteceu numa execução real).
2. Agrupe os RFs em jornadas por resultado observável pelo usuário final — não force CRUD como molde único; use CRUD como checklist para não esquecer operação óbvia (criar/consultar/atualizar/excluir), mas a jornada real pode ser orientada a evento, fluxo de aprovação, etc.
3. Para cada jornada, numere o passo a passo de participação dos componentes (ex: C1 → C2 → C4), na ordem real de execução — isso é a base direta para o diagrama de sequência de cada jornada.
4. Marque, por jornada, quais conexões do `desenho.md` participam, usando um `journey_id` (slug curto, ex: `lead-notificado`) — essa marcação é o que permite ao [[agents/geracao-diagramas/AGENT]] gerar depois uma visão de Container filtrada por jornada, sem redesenhar o diagrama do zero.
5. **Grave também, por jornada, o spec de sequência máquina-legível** em `demandas/<nome-da-demanda>/diagramas/sequencia-<journey_id>_spec.json`, no formato de `docs/diagrams/c4-schema.md` (seção "Pipeline invertido") — mensagens numeradas (`ordem`), com `de`/`para`/`rotulo`/`protocolo`/`assincrona`/`tipo` (`chamada` para o passo a passo real, `self` para uma etapa interna do mesmo componente, `retorno` só quando for de fato uma resposta que não deve virar seta própria no Container). Este arquivo é a fonte que [[agents/geracao-diagramas/AGENT]] usa para **derivar** o Container automaticamente — não é redundante com `jornadas.md`, é a versão que uma máquina consegue processar.
6. Confira que todo RF funcional-observável está coberto por ao menos uma jornada; se não estiver, registre como lacuna explícita, não invente cobertura.
7. Se uma jornada expõe uma lacuna de desenho (integração que não existe) ou uma dúvida sobre o requisito, pergunte ao agente dono ([[agents/desenho-de-arquitetura/AGENT]] ou [[agents/entendimento-e-escopo/AGENT]]) em vez de decidir.

## Artefato de saída
`demandas/<nome-da-demanda>/jornadas.md` **sempre existe**, nas duas situações:

- **Jornadas reais identificadas**: primeira linha do documento é `**Veredito:** N jornada(s) identificada(s).`, seguida do conteúdo normal — nome, `journey_id`, RF(s) de origem, passo a passo numerado, marcação de participação por componente/conexão. Mais `demandas/<nome-da-demanda>/diagramas/sequencia-<journey_id>_spec.json`, um por jornada — versão máquina-legível, consumida por [[agents/geracao-diagramas/AGENT]] via `scripts/derivar_c4.py` para derivar o Container/Contexto sem risco de divergir do que a jornada realmente descreve.
- **Nenhuma jornada aplicável** (demanda puramente técnica/interna): documento com só duas linhas, `**Veredito:** nenhuma jornada aplicável.` seguida de `**Motivo:** <explicação factual, específica desta demanda>`. Nenhum `sequencia-*_spec.json` é gerado neste caso. Isso não é uma licença pra inventar jornada onde não existe — é o registro explícito de que a checagem foi feita e o resultado foi negativo, em vez de simplesmente não deixar rastro nenhum.

Documentação Final e Geração de Diagramas C4 leem a primeira linha do arquivo para saber qual dos dois casos se aplica — nunca decidem isso sozinhos, só reagem ao veredito já escrito aqui.

## Como é bem feito
Toda jornada é rastreável a um RF real e a componentes reais do desenho — nenhuma inventada, nenhuma faltando cobertura sem justificativa.
