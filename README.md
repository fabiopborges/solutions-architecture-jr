<div align="center">

# Arquiteto de Soluções Junior IA

**Um time de agentes de IA que trabalha como um Arquiteto de Soluções Júnior.**
Uma atividade, um agente, um critério de pronto — e nada sai como "entregue" sem uma pessoa aprovar.

[![Licença MIT](https://img.shields.io/badge/licen%C3%A7a-MIT-blue.svg)](LICENSE.md)
[![Claude Code](https://img.shields.io/badge/roda%20em-Claude%20Code-d97757.svg)](https://claude.com/claude-code)
[![18 agentes](https://img.shields.io/badge/agentes-18%20%2B%20orquestrador-0f766e.svg)](#os-18-agentes)
[![ADRs](https://img.shields.io/badge/ADRs-001%E2%80%93022-475569.svg)](adrs/)

</div>

Construído sobre o [Claude Code](https://claude.com/claude-code). Em vez de um prompt genérico tentando fazer tudo de uma vez, cada atividade real do trabalho de arquitetura vira um agente próprio, com escopo estreito, uma skill dedicada e um critério claro de "isso está bem feito".

> [!NOTE]
> **Status do projeto:** as 18 atividades + o Orquestrador estão especificadas e registradas como skill/subagentes nativos do Claude Code (`/arquiteto-solucoes`). Sete demandas já rodaram ponta a ponta via despacho real de subagente — veja [Estado atual](#estado-atual). Os diagramas C4 deste README são a saída do próprio time rodando sobre si mesmo.

---

## Sumário

**Conceitos**

- [Por que isto existe](#por-que-isto-existe)
- [Ideia central em 30 segundos](#ideia-central-em-30-segundos)
- [Glossário rápido](#glossário-rápido)

**As vistas da arquitetura**

- [1. As seis camadas do OS](#1-as-seis-camadas-do-os)
- [2. Contexto — quem conversa com o OS](#2-contexto--quem-conversa-com-o-os)
- [3. Containers — os 18 agentes e as fronteiras de domínio](#3-containers--os-18-agentes-e-as-fronteiras-de-domínio)
- [4. Uma demanda ponta a ponta, no tempo](#4-uma-demanda-ponta-a-ponta-no-tempo)
- [5. Fluxo de dados entre os agentes](#5-fluxo-de-dados-entre-os-agentes)
- [6. Zoom em um agente: Geração de Diagramas C4](#6-zoom-em-um-agente-geração-de-diagramas-c4)
- [7. Execução vs. referência no disco](#7-execução-vs-referência-no-disco)

**Mão na massa**

- [Pré-requisitos](#pré-requisitos)
- [Quickstart](#quickstart)
- [Onde ficam os outputs de uma demanda](#onde-ficam-os-outputs-de-uma-demanda)
- [Os 18 agentes](#os-18-agentes)
- [Regras e governança](#regras-e-governança)
- [Estado atual](#estado-atual)
- [Como estender (adicionar um agente novo)](#como-estender-adicionar-um-agente-novo)
- [Licença](#licença)

---

## Por que isto existe

Arquitetura de solução tem muitas atividades distintas — entender a demanda, desenhar componentes, modelar dados, avaliar segurança, estimar custo — e é comum uma única pessoa (ou um único prompt genérico de IA) tentar fazer todas ao mesmo tempo. Isso convida dois problemas:

- **Alucinação**: inventar uma decisão técnica sem base.
- **Desvio de escopo**: uma atividade contaminando o julgamento de outra (ex: quem está pensando em custo já começa a decidir segurança).

Este projeto resolve isso dividindo o trabalho em **18 atividades**, cada uma com um dono (agente) e uma skill focada só naquele objetivo. Um **Orquestrador** decide a ordem, dispara em paralelo o que não depende de nada, e segura um portão de saída — com aprovação humana obrigatória — antes de qualquer pacote de arquitetura sair como "entregue".

## Ideia central em 30 segundos

```text
Demanda crua (SDR, pedido de negócio)
        │
        ▼
  18 agentes especialistas, cada um dono de UMA atividade,
  perguntando uns aos outros quando têm dúvida fora do próprio escopo
        │
        ▼
  Pacote de arquitetura completo: entendimento, desenho, dados,
  segurança, custo, observabilidade, riscos, ADRs — com suposições
  e trade-offs escritos em cada decisão
        │
        ▼
  Portão de saída (aprovação humana obrigatória) → Entregue
```

Se você já usou um time real de arquitetura, a analogia é direta: em vez de um arquiteto sênior sozinho tentando cobrir todas as frentes, você tem uma pessoa júnior por atividade, cada uma boa numa coisa só, que sabe pedir ajuda para o colega certo em vez de chutar.

## Glossário rápido

| Termo | O que é |
| --- | --- |
| **Agente** | Dono de uma atividade específica (ex: Modelagem de Dados). Decide só dentro do próprio escopo. |
| **Skill** | O "manual de operação" de uma atividade: quando usar, passos, artefato de saída, critério de pronto. |
| **Orquestrador** | Gerencia a ordem, o paralelismo e o portão de saída. Não desenha nem decide nada de arquitetura sozinho. |
| **Demanda** | Um pedido de arquitetura específico, com nome próprio, nunca inventado pelo agente. Vira uma pasta em `demandas/`. |
| **Bounded context** | Fronteira de domínio (DDD) que delimita o que cada agente decide. É o que define o recorte de cada componente, não a conveniência técnica. |
| **ADR** | Architecture Decision Record. Toda decisão importante vira um ADR formal, com aprovação humana antes de valer. |
| **Portão de saída** | Checklist obrigatório (suposições escritas, dúvidas fechadas, pacote completo, aprovação humana) antes de "entregue". |
| **Substrato** | O conhecimento destilado (stack aprovada, padrões da casa, ADRs anteriores) que os agentes leem antes de decidir. |

---

## As vistas da arquitetura

Sete vistas complementares da mesma coisa, do conceito ao disco. **As vistas 2 a 6 não foram desenhadas à mão**: são a saída do agente [Geração de Diagramas C4](agents/geracao-diagramas/AGENT.md) rodando sobre este próprio repositório como demanda — o OS aplicado a si mesmo, com `desenho.md`, `dados.md` e as jornadas do próprio time como fonte. Os specs que geraram cada imagem estão em [`docs/diagrams/archify/`](docs/diagrams/archify/).

> [!TIP]
> Todo diagrama abaixo é clicável — abra em tamanho real, alguns são largos. Os SVGs seguem o tema claro/escuro do seu sistema.

### 1. As seis camadas do OS

O projeto segue a metodologia **OS Agêntico**, construída de baixo para cima: cada camada depende da que veio antes.

[![As seis camadas do OS, da Identidade até os Agentes](docs/diagrams/01-camadas.svg)](docs/diagrams/01-camadas.svg)

*Fonte editável: [`docs/diagrams/01-camadas.mmd`](docs/diagrams/01-camadas.mmd)*

Tudo o que os agentes decidem, aprendem ou ainda não sabem fica registrado em [`memory.md`](memory.md), a memória viva do OS.

### 2. Contexto — quem conversa com o OS

A vista mais alta: cada caixa é um **bounded context** inteiro, com os agentes daquele domínio colapsados dentro dele, e o único ator de fora é a **Pessoa Operadora** — que dispara a demanda, responde às perguntas de escopo e aprova o portão de saída. Todo o resto acontece entre os agentes.

[![Diagrama de contexto C4: bounded contexts do OS e os atores externos](docs/diagrams/archify/c4-contexto.svg)](docs/diagrams/archify/c4-contexto.svg)

### 3. Containers — os 18 agentes e as fronteiras de domínio

Cada agente é um container, e cada moldura tracejada é um **bounded context** (DDD) derivado de uma capacidade de negócio (TOGAF) — os limites dos componentes seguem os limites do domínio, nunca a conveniência técnica.

[![Diagrama de containers C4: os 18 agentes agrupados por bounded context](docs/diagrams/archify/c4-container.svg)](docs/diagrams/archify/c4-container.svg)

| Elemento | Significa |
| --- | --- |
| 🟩 Caixa verde | Agente do time (container interno) |
| ⬜ Caixa cinza | Ator de fora do time — aqui, só a Pessoa Operadora |
| 🟧 Moldura tracejada | Bounded context — a fronteira de domínio que o agente serve |
| ➡️ Seta cheia | Despacho ou leitura que **espera** o outro lado terminar |
| ⇢ Seta tracejada | Despacho em paralelo, que não bloqueia quem chamou |

A ordem real de execução, com o que roda em paralelo:

1. Entendimento e Escopo
2. Desenho de Arquitetura (aciona Geração de Diagramas C4 assim que a estrutura fecha)
3. Em paralelo — **3a** Modelagem de Dados · **3b** Infraestrutura e Deployment · **3c** Testes e Qualidade · **3d** Jornadas do Usuário (+ sob demanda: Pesquisa e Benchmarking, Especialista IA/ML, Especialista Dados/Analytics)
4. Segurança e Compliance (espera 2 + 3a)
5. Em paralelo, após 3b — **5a** Estimativa de Custo · **5b** Observabilidade e Telemetria (frente 1)
6. Em paralelo — **6a** Documentação Final (sincroniza 3a+3b+3c+3d+4+5a+5b, aciona Geração de Diagramas C4 de novo pra consolidar) · **6b** Riscos e Mitigação (espera 2 + 3c)
7. Comunicação com Stakeholders (espera 6a + 6b)
8. Entrega e Handoff prepara o material
9. Portão de saída (suposições, dúvidas fechadas, pacote completo, aprovação humana)
10. Entregue

Trade-offs e ADR, Geração de Diagramas C4 e o Orquestrador são **transversais**: atuam o tempo todo, não são um passo numerado.

### 4. Uma demanda ponta a ponta, no tempo

O mesmo fluxo, agora como troca de mensagens: dá para ver onde o Orquestrador solta quatro despachos em paralelo e onde ele volta a segurar tudo até a consolidação final.

[![Diagrama de sequência de uma demanda completa, do pedido à liberação do pacote](docs/diagrams/archify/sequencia-demanda-processada-e-pacote-entregue.svg)](docs/diagrams/archify/sequencia-demanda-processada-e-pacote-entregue.svg)

### 5. Fluxo de dados entre os agentes

Que artefato cada agente produz e quem lê o quê. É esta vista que mostra por que a cadeia tem a ordem que tem: `desenho.md` precisa estar pronto antes de qualquer modelagem, `dados.md` antes de segurança, tudo antes da consolidação final. É também a única vista onde aparece o **Claude Code Runtime**, que executa cada subagente como processo isolado.

[![Diagrama de fluxo de dados entre os agentes, com os artefatos trocados](docs/diagrams/archify/c4-fluxo-dados.svg)](docs/diagrams/archify/c4-fluxo-dados.svg)

> [!NOTE]
> Esta vista omite algumas relações "todo agente → um agente" (telemetria, leitura do compêndio) por limitação de roteamento do gerador, não por decisão de conteúdo. A descrição completa continua em `dados.md`, dentro da demanda.

### 6. Zoom em um agente: Geração de Diagramas C4

Um nível abaixo do container, para mostrar como um agente é montado por dentro — aqui, o que traduz decisão já tomada em diagrama, sem nunca decidir arquitetura.

[![Diagrama de componentes do agente de Geração de Diagramas C4](docs/diagrams/archify/c4-componente-geracao-diagramas.svg)](docs/diagrams/archify/c4-componente-geracao-diagramas.svg)

### 7. Execução vs. referência no disco

Este repositório é a raiz de um projeto Claude Code, o que cria duas camadas lado a lado que não devem ser confundidas: uma versão **enxuta e invocável** dentro de `.claude/`, e a **documentação de referência completa** que essa versão enxuta consulta antes de agir.

[![Camada de execução em .claude/ apontando para a camada de referência na raiz](docs/diagrams/03-execucao-referencia.svg)](docs/diagrams/03-execucao-referencia.svg)

*Fonte editável: [`docs/diagrams/03-execucao-referencia.mmd`](docs/diagrams/03-execucao-referencia.mmd)*

Os arquivos de execução apontam para os de referência em vez de duplicar conteúdo. `.claude/` guarda só o que o Claude Code precisa descobrir (subagentes e a skill de entrada); o resto — inclusive a documentação completa de cada atividade — vive na raiz, fora de `.claude/`, porque subagentes despachados resolvem caminho relativo contra a raiz real do projeto, nunca contra `.claude/`. **Por isso todo despacho de subagente usa caminho absoluto** (reforçado por um hook real em `.claude/settings.json`, ver [Regras e governança](#regras-e-governança)).

```text
.
├── .claude/
│   ├── agents/*.md                       # execução: 18 subagentes reais
│   └── skills/arquiteto-solucoes/SKILL.md # execução: ponto de entrada
├── CLAUDE.md               # Identidade (camada 1)
├── memory.md               # Memória viva: decisões, status, perguntas em aberto
├── tools.md                # Conexões externas (camada 5), hoje nenhuma ligada
├── telemetria-agentes.md   # Registro contínuo de tempo/tokens gastos, entre demandas
├── adrs/                   # ADRs formais, aprovados, globais, reaproveitáveis
├── demandas/               # Uma pasta por demanda real (local, não versionado)
│   └── <nome-da-demanda>/
├── docs/diagrams/          # Vistas do próprio OS (Mermaid à mão + C4 gerado pelo pipeline)
├── rules/
│   ├── always.md           # O que todo agente sempre faz + hooks
│   └── never.md            # Paradas duras
├── scripts/                # Pipeline de diagramas C4 (spec → candidato → SVG)
├── substrate/
│   ├── compendium.md       # Referência destilada que os agentes leem antes de decidir
│   └── sources.md          # De onde esse conhecimento vem
├── skills/<atividade>/SKILL.md   # referência: passos, artefato, critério de pronto
└── agents/<atividade>/AGENT.md   # referência: papel, dependências, portão de revisão
```

Cada atividade tem a mesma pasta em `skills/` e `agents/` (mesmo nome), para ser fácil achar as duas metades de uma atividade.

---

## Pré-requisitos

- [Claude Code](https://claude.com/claude-code) instalado.
- Nenhuma dependência externa, chave de API ou etapa de build. `tools.md` documenta conexões futuras opcionais (repositório de docs, backlog, observabilidade), todas ainda desligadas.
- Só para **regerar** os diagramas C4: Python 3 (stdlib) e Node.js ≥18 — o ArchiFy já vem vendorizado em `skills/vendors/archify/`. Ver [`scripts/README.md`](scripts/README.md).

## Quickstart

**1. Coloque este repositório na raiz do seu projeto Claude Code.**
Este repositório já É a raiz — não o aninhe dentro do `.claude/` de outro projeto.

```bash
git clone <este-repositório>
cd solutions-architecture-jr-agents
claude   # sempre abra a CLI a partir daqui, não de uma subpasta
```

> [!IMPORTANT]
> Por que a partir da raiz? O Claude Code carrega `.claude/settings.json` a partir do diretório onde a sessão foi iniciada, não da raiz do git. Abrir de uma subpasta faz o hook de caminho absoluto (ver [Regras e governança](#regras-e-governança)) simplesmente não carregar, sem aviso de erro. Confira com `/hooks` que `PreToolUse` aparece listado.

**2. Dispare uma demanda nova.**

```text
/arquiteto-solucoes <cole aqui o pedido ou o SDR>
```

A primeira coisa que o time faz é confirmar o **nome da demanda** com você — esse nome nunca é inventado por um agente (ver [rules/never.md](rules/never.md)). É esse nome exato que vira a pasta `demandas/<nome-da-demanda>/`.

**3. Deixe o time trabalhar.**
A skill de entrada despacha os 18 agentes na ordem e no paralelismo da [vista de containers](#3-containers--os-18-agentes-e-as-fronteiras-de-domínio), até o portão de saída — que inclui aprovação humana obrigatória — e a liberação final em `demandas/<nome-da-demanda>/handoff.md`.

**4. Acompanhe sem interromper, a qualquer momento.**

```text
/arquiteto-solucoes status <nome-da-demanda>
```

Mostra o que já rodou e o que falta, sem despachar nenhum agente novo.

**5. Quando o portão de saída pedir aprovação, revise e aprove.**
Nada sai como "entregue" sem uma pessoa do time confirmar — mesmo que todos os outros critérios do portão já tenham passado.

### Onde ficam os outputs de uma demanda

O nome da demanda **nunca é inventado por um agente**. Quem pede informa o nome explicitamente ao agente de Entendimento e Escopo (ou o agente pergunta e espera a resposta). Esse nome vira a pasta `demandas/<nome-da-demanda>/`, e cada atividade grava um arquivo lá (`entendimento.md`, `desenho.md`, `dados.md`, etc.), em vez de espalhar arquivos soltos na raiz. Duas exceções ficam fora de `demandas/`: `adrs/` (decisões reaproveitáveis por demandas futuras) e `telemetria-agentes.md` (registro contínuo entre demandas).

> [!WARNING]
> `demandas/` está em `.gitignore`, não faz parte deste repositório público: os artefatos de cada demanda ficam só no seu clone local. As demandas usadas para validar a cadeia durante o desenvolvimento deste OS foram todas sintéticas (empresa, SDR, orçamento e decisões fictícios), e por isso não foram publicadas — mantenha o mesmo cuidado com as suas.

## Os 18 agentes

| # | Agente | Quando entra | Depende de / é acionado por |
| --- | --- | --- | --- |
| 1 | [Entendimento e Escopo](agents/entendimento-e-escopo/AGENT.md) | Sempre, primeiro | A demanda crua |
| 2 | [Desenho de Arquitetura](agents/desenho-de-arquitetura/AGENT.md) | Sempre, segundo | Entendimento e Escopo |
| 3 | [Pesquisa e Benchmarking](agents/pesquisa-e-benchmarking/AGENT.md) | Sob demanda | Quando a stack aprovada não resolve |
| 4 | [Trade-offs e ADR](agents/trade-offs-e-adr/AGENT.md) | Toda decisão importante | Tem portão de aprovação humana próprio |
| 5 | [Modelagem de Dados](agents/modelagem-de-dados/AGENT.md) | Paralelo, a partir do Desenho | Desenho de Arquitetura |
| 6 | [Segurança e Compliance](agents/seguranca-e-compliance/AGENT.md) | Depois de Desenho + Modelagem | Não roda em paralelo com eles |
| 7 | [Infraestrutura e Deployment](agents/infraestrutura-e-deployment/AGENT.md) | Paralelo, a partir do Desenho | Desenho de Arquitetura |
| 8 | [Estimativa de Custo](agents/estimativa-de-custo/AGENT.md) | Depois de Infraestrutura | Não roda em paralelo com ele |
| 9 | [Observabilidade e Telemetria](agents/observabilidade-e-telemetria/AGENT.md) | Frente 1 depois de Infra; frente 2 contínua | Duas frentes: solução entregue + telemetria dos agentes |
| 10 | [Testes e Qualidade](agents/testes-e-qualidade/AGENT.md) | Paralelo, a partir do Desenho | Desenho de Arquitetura |
| 11 | [Jornadas do Usuário](agents/jornadas-do-usuario/AGENT.md) | Paralelo, a partir do Desenho | Desenho de Arquitetura + RFs de Entendimento e Escopo |
| 12 | [Documentação Final](agents/documentacao-final/AGENT.md) | Sincronização total | Espera todos os ramos técnicos |
| 13 | [Riscos e Mitigação](agents/riscos-e-mitigacao/AGENT.md) | Paralelo com Documentação Final | Desenho + Testes e Qualidade |
| 14 | [Comunicação com Stakeholders](agents/comunicacao-stakeholders/AGENT.md) | Depois de Doc. Final + Riscos | Traduz o que já existe, não decide nada novo |
| 15 | [Entrega e Handoff](agents/entrega-e-handoff/AGENT.md) | Última | Prepara em paralelo, libera após aprovação |
| 16 | [Especialista em Dados e Analytics](agents/especialista-dados-analytics/AGENT.md) | Sob demanda | Só se há decisão de plataforma analítica |
| 17 | [Especialista em IA e Machine Learning](agents/especialista-ia-ml/AGENT.md) | Sob demanda | Só se há decisão de modelo de IA/ML |
| 18 | [Geração de Diagramas C4](agents/geracao-diagramas/AGENT.md) | Transversal | Acionado por Desenho de Arquitetura e Documentação Final |
| — | [Orquestrador](agents/orquestrador/AGENT.md) | Sempre ativo | Gerencia dependências, paralelismo e o portão de saída |

## Regras e governança

- **Nunca** ([`rules/never.md`](rules/never.md)): um agente decide fora do próprio escopo; uma dúvida entre agentes passa de 3 rodadas sem se resolver (na 4ª, escala para revisão humana); uma entrega sai sem suposições/trade-offs escritos; um agente reaproveita contexto de uma demanda anterior.
- **Sempre** ([`rules/always.md`](rules/always.md)): expor suposições e trade-offs; perguntar ao dono da atividade em caso de dúvida; paralelizar quando possível; registrar tempo/tokens gastos.
- **Hook real de caminho absoluto**: `.claude/settings.json` bloqueia (`PreToolUse`, `permissionDecision: deny`) qualquer despacho de subagente cujo prompt referencie `demandas/...` sem caminho absoluto. É reforço de verdade do harness, não só descrição de comportamento — só funciona se a sessão for aberta a partir da raiz do repo (ver [Quickstart](#quickstart)).
- **Cloud é agnóstica de provedor** ([ADR 001](adrs/adr-001-cloud-agnostica-por-criterio-de-negocio.md)): a escolha é por critério de negócio a cada demanda, não fixada em um provedor.
- **Microsserviços seguem os limites de domínio** ([ADR 002](adrs/adr-002-microsservicos-como-consequencia-de-ddd.md)): TOGAF (Business Architecture) mapeia capacidades de negócio, DDD traduz isso em bounded contexts.

Duas dessas regras são fluxos próprios, com diagrama gerado pelo mesmo pipeline:

<details>
<summary><strong>Toda decisão importante vira um ADR aprovado por uma pessoa</strong></summary>

[![Sequência: decisão importante formalizada como ADR e aprovada por uma pessoa](docs/diagrams/archify/sequencia-adr-aprovado-para-decisao-importante.svg)](docs/diagrams/archify/sequencia-adr-aprovado-para-decisao-importante.svg)

O ADR só entra no compêndio de conhecimento — e só passa a valer para demandas futuras — depois da aprovação explícita.

</details>

<details>
<summary><strong>Dúvida que não fecha em 3 rodadas escala para revisão humana</strong></summary>

[![Sequência: dúvida entre agentes escalada para revisão humana na quarta rodada](docs/diagrams/archify/sequencia-duvida-escalada-revisao-humana.svg)](docs/diagrams/archify/sequencia-duvida-escalada-revisao-humana.svg)

Um agente nunca "resolve" a dúvida chutando no lugar do dono da outra atividade: ou fecha em até 3 rodadas, ou vira pergunta para uma pessoa.

</details>

## Estado atual

Veja [`memory.md`](memory.md) para o histórico completo de decisões. Resumo honesto:

- As seis camadas do OS estão sólidas, o roteiro de 18 atividades está fechado, sete demandas reais já rodaram ponta a ponta via `/arquiteto-solucoes` de verdade (despacho por subagente, não simulação), com custo de processamento medido em tokens reais — ver `telemetria-agentes.md`.
- **Os subagentes e a skill de entrada estão registrados** em `.claude/agents/` e `.claude/skills/arquiteto-solucoes/`, seguindo o padrão nativo do Claude Code, e já foram exercitados de ponta a ponta em execuções reais.
- **Dois agentes novos (Geração de Diagramas C4 e Jornadas do Usuário) foram adicionados em 2026-08-15** (ver `memory.md`) para resolver diagramas ASCII dessincronizados entre `desenho.md`/`documentacao-final.md` e para dar um roteiro de sequência a partir dos requisitos. Já rodaram de ponta a ponta em várias demandas reais desde então, incluindo a geração de diagramas de sequência via ArchiFy e a correção que tornou `jornadas.md` sempre determinístico (veredito explícito, nunca ausência silenciosa).
- **Dos dois especialistas sob demanda, só o de IA/ML já foi acionado de verdade** (`demandas/plataforma-ia-corporativa-v1/`, confirmando que o gatilho dispara quando deveria, depois de três demandas seguidas confirmando só o caminho de não disparar à toa). **O Especialista em Dados e Analytics nunca foi acionado** — nenhuma demanda real até agora teve decisão de plataforma analítica de verdade. Por isso ele não aparece em nenhuma das vistas geradas: nenhuma jornada real o exercita.
- `tools.md` lista três conexões externas úteis, nenhuma ligada ainda.
- ADRs 001 a 022 registrados em `adrs/`, com aprovação humana explícita registrada em cada um antes de valer como oficial.

## Como estender (adicionar um agente novo)

Siga sempre esta ordem, para não repetir o anti-padrão de "agente faz-tudo" nem inventar trabalho que ninguém pediu:

1. Confirme que é uma atividade real e repetida, não uma ideia especulativa.
2. Escreva a `SKILL.md` primeiro: quando usar, passos, artefato de saída, critério de "bem feito". Se a atividade só se aplica em certas condições, escreva o critério de gatilho explicitamente (veja os dois especialistas sob demanda como exemplo).
3. Só depois escreva o `AGENT.md`: o papel, quando é acionado, de quem depende, o portão de revisão, e a fronteira clara com agentes que já existem (para não sobrepor responsabilidade).
4. Atualize `agents/roadmap.md`, `skills/roadmap.md` e o papel do novo agente em `agents/orquestrador/AGENT.md`.
5. Registre a decisão em `memory.md`.

## Licença

[MIT](LICENSE.md). Uso, cópia, modificação e distribuição livres, sem garantia, mantendo o aviso de copyright.

## Contribuindo

O fluxo de contribuição e o Acordo de Licença de Contribuição (CLA) estão em [CONTRIBUTING.md](CONTRIBUTING.md). Toda contribuição aceita é incorporada sob a mesma licença MIT.
