# Sempre

Restrições que todo agente deste OS segue em toda atividade.

- Sempre expõe as suposições e os trade-offs por trás de cada decisão antes de passar o trabalho adiante ou de entregar.
- Sempre pergunta ao agente dono de uma atividade quando tem dúvida sobre algo daquela atividade, em vez de decidir sozinho.
- Sempre roda em paralelo com outros agentes quando não depende do resultado deles, e só espera quando realmente precisa do que o outro vai produzir.
- Sempre registra o que fez, quanto gastou (tempo/tokens) e o status ao terminar uma atividade. Isso alimenta a camada de observabilidade.

## Hook: limite de rodadas de dúvida
Quando um agente pergunta a outro sobre uma dúvida na mesma atividade pela 4ª vez sem chegar a uma resposta fechada, o hook interrompe o loop automaticamente e escala a dúvida para revisão humana, em vez de deixar os agentes continuarem se perguntando. Isso existe porque o pior erro identificado para essa estrutura em loop é um loop infinito de dúvidas entre agentes. Ainda é uma descrição do comportamento esperado, a amarração técnica desse hook (onde e como ele de fato intercepta a 4ª rodada) fica para quando os agentes da Camada 6 existirem de verdade.

## Hook real: caminho absoluto ao despachar subagente
Diferente do hook acima, este já é reforço de verdade do harness, não só descrição de comportamento esperado: `.claude/settings.json` (versionado) tem um hook `PreToolUse` no matcher `Agent|Task` que bloqueia (`permissionDecision: deny`) qualquer despacho de subagente cujo prompt contenha `demandas/<algo>` sem um `/` logo antes (ou seja, sem prefixo de caminho absoluto). Existe porque essa é a regra "sempre use caminho absoluto, nunca relativo" (ver `agents/arquiteto-solucoes` e `memory.md`, entrada do bug real de 2026-08 onde um subagente gravou um artefato no lugar errado por resolver um caminho relativo contra a raiz errada). O hook não impede todo tipo de erro de escopo, só o padrão exato já visto na prática; se aparecer outro padrão de bug de caminho, vale estender o mesmo hook em vez de criar um novo.

**Pré-requisito para o hook funcionar: abrir a CLI a partir da raiz do repo.** O Claude Code carrega `.claude/settings.json` a partir do diretório onde a sessão foi iniciada (cwd), não da raiz do repositório git. Se a sessão for aberta com `cd .claude/skills` (ou qualquer subpasta) antes de rodar `claude`, o Claude Code trata isso como um projeto diferente e não encontra `/home/fabioborges/projetos/agentes-arquiteto-de-solucoes-junior/.claude/settings.json` — o hook simplesmente não carrega, sem aviso de erro (confirmado em 2026-08-15: `/hooks` mostrou "No hooks configured" e um despacho de subagente com caminho relativo passou direto). Sempre inicie a sessão com `cd /home/fabioborges/projetos/agentes-arquiteto-de-solucoes-junior` antes de `claude`. Para conferir se os hooks do projeto estão ativos, rode `/hooks` e confira se `PreToolUse` aparece listado.
