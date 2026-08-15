# Backlog do OS

Pendências estruturais conhecidas, fora do fluxo de qualquer demanda de teste. Cada item tem dono implícito (quem opera a sessão, não um agente) até que vire trabalho de agente de verdade.

## Aberto

1. **Configurar o GitHub do repositório.** Hoje não há `git remote` configurado (`git remote -v` vazio) e o `README.md`/LICENSE já foram escritos pensando em publicação futura. Falta: criar o repositório remoto, `git remote add origin <url>`, primeiro `git push`, e decidir visibilidade (público/privado) antes de publicar — conferir se `demandas/` (dados de teste, alguns com nomes de empresas fictícias tipo "SeguroSeguro S.A.") deve ir junto ou ficar fora do primeiro push.
2. **Commitar a reestruturação de raiz feita em 2026-08-15.** 123 arquivos renomeados via `git mv` seguem staged, sem commit ainda (ver conversa anterior, item #1 do diário de melhorias). Bloqueia qualquer outro commit limpo até resolver.
3. **Decidir o destino de `skills/<atividade>/AGENT.md`/`SKILL.md` (camada de referência) vs. o corpo de `.claude/agents/<atividade>.md` (camada de execução).** Hoje são fontes separadas por design (single source of truth na referência), mas isso custa 2 `Read`s extras por despacho de subagente. Não é bug, é trade-off nunca revisitado — vale decidir explicitamente se compensa manter separado ou fundir.
4. **`rules/` e `substrate/` não têm reforço real do harness.** Funcionam hoje só porque cada prompt de agente aponta manualmente pra eles (convenção de texto, não hook). Avaliar se algum ponto (ex: limite de 3 rodadas de dúvida) merece virar hook de verdade.
5. **Nenhum subagente real declara `model` no front-matter.** Herda implicitamente da sessão. Nunca foi uma decisão explícita — vale registrar se isso é intencional ou se algum agente (ex: Pesquisa e Benchmarking, mais WebSearch-pesado) deveria fixar um modelo.
6. **Testar `/arquiteto-solucoes` de ponta a ponta a partir da nova raiz.** A correção de raiz (2026-08-15) resolve o bug de path na teoria, mas ainda não foi validada com uma demanda real rodando pela cadeia inteira depois da mudança.

## Concluído
- 2026-08-15: Raiz do repositório movida para a raiz real do projeto Claude Code (ver `memory.md`).
