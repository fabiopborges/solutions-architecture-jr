<div align="center">

# Arquiteto de Soluções Junior IA

**Um time de agentes de IA que trabalha como um Arquiteto de Soluções Júnior.**
Uma atividade, um agente, um critério de pronto — e nada sai como "entregue" sem uma pessoa aprovar.

[![Licença MIT](https://img.shields.io/badge/licen%C3%A7a-MIT-blue.svg)](LICENSE.md)
[![Claude Code](https://img.shields.io/badge/roda%20em-Claude%20Code-d97757.svg)](https://claude.com/claude-code)
[![18 agentes](https://img.shields.io/badge/agentes-18%20%2B%20orquestrador-0f766e.svg)](#os-18-agentes)
[![ADRs](https://img.shields.io/badge/ADRs-001%E2%80%93023-475569.svg)](adrs/)

</div>

Construído sobre o [Claude Code](https://claude.com/claude-code). Em vez de um prompt genérico tentando fazer tudo de uma vez, cada atividade real do trabalho de arquitetura vira um agente próprio, com escopo estreito, uma skill dedicada e um critério claro de "isso está bem feito".

## Por que "Júnior", se as decisões são grandes

O nome engana de propósito — então vale desfazer o mal-entendido na primeira tela.

**"Júnior" não é o tamanho do problema. É o tamanho da autoridade.**

O trabalho que este time faz não é júnior: ele modela capacidades de negócio com TOGAF, traduz em bounded contexts com DDD, escolhe provedor de cloud por critério de negócio, define tratamento de dado sensível e requisito de compliance, dimensiona custo por componente, aponta pontos únicos de falha e formaliza cada escolha como ADR com alternativas descartadas. São decisões que sustentam ou afundam um projeto — e o time as toma com fundamento escrito, não com opinião.

O que ele **nunca** tem é a palavra final.

Todo agente aqui trabalha como um arquiteto júnior competente trabalha num time saudável: leva a análise até o fim, defende uma recomendação, expõe o que assumiu e o que abriu mão — e **leva para um humano assinar**. Não porque a análise seja fraca, mas porque a responsabilidade não é delegável. Quem responde pela decisão é quem tem nome, cargo e pele no jogo.

E isso não é uma promessa de comportamento, é mecanismo:

- Nenhum agente decide fora do próprio escopo — na dúvida, pergunta ao dono da atividade em vez de chutar.
- Nenhum ADR vale como oficial antes de **aprovação humana explícita** registrada nele.
- O agente de entrega **não tem autoridade para se autoaprovar**: prepara o pacote como "PREPARADO, aguardando aprovação humana" e só marca "LIBERADO" depois que uma pessoa confirma.
- Risco não some por conveniência: cada um sai com mitigação **ou aceite explícito** de alguém.
- Dúvida entre agentes que não fecha em três rodadas escala para revisão humana na quarta.

**O selo de júnior é sobre você, não sobre o agente.** Seja você júnior, pleno, sênior ou especialista, a cadeira de decisão continua sendo a sua — o time entrega tudo pronto para você julgar, e nada pronto para dispensar o seu julgamento. Um arquiteto sênior ganha alavancagem; um júnior ganha um time que mostra o raciocínio inteiro em vez de um veredito para copiar.

É o oposto de "IA que decide por você": é IA que faz o trabalho inteiro **para que a decisão seja sua, e mais bem informada**.

> [!NOTE]
> **Status do projeto:** as 18 atividades + o Orquestrador estão especificadas e registradas como skill/subagentes nativos do Claude Code (`/arquiteto-solucoes`). Sete demandas já rodaram ponta a ponta via despacho real de subagente — veja [Estado atual](#estado-atual). Os diagramas C4 deste README são a saída do próprio time rodando sobre si mesmo.

---

## Sumário

**Conceitos**

- [Por que "Júnior", se as decisões são grandes](#por-que-júnior-se-as-decisões-são-grandes)
- [Por que isto existe](#por-que-isto-existe)
- [Ideia central em 30 segundos](#ideia-central-em-30-segundos)
- [Glossário rápido](#glossário-rápido)

**As vistas da arquitetura**

- [1. As seis camadas do Arquiteto de Soluções Junior IA](#1-as-seis-camadas-do-arquiteto-de-soluções-junior-ia)
- [2. Contexto — quem conversa com o Arquiteto de Soluções Junior IA](#2-contexto--quem-conversa-com-o-arquiteto-de-soluções-junior-ia)
- [3. Containers — os 18 agentes e as fronteiras de domínio](#3-containers--os-18-agentes-e-as-fronteiras-de-domínio)
- [4. Uma demanda ponta a ponta, no tempo](#4-uma-demanda-ponta-a-ponta-no-tempo)
- [5. Fluxo de dados entre os agentes](#5-fluxo-de-dados-entre-os-agentes)
- [6. Zoom em um agente: Geração de Diagramas C4](#6-zoom-em-um-agente-geração-de-diagramas-c4)
- [7. Execução vs. referência no disco](#7-execução-vs-referência-no-disco)

**Mão na massa**

- [Pré-requisitos](#pré-requisitos)
- [Quickstart](#quickstart)
- [Onde ficam os outputs de uma demanda](#onde-ficam-os-outputs-de-uma-demanda)
- [Formas de uso](#formas-de-uso)
- [Os 18 agentes](#os-18-agentes)
- [Regras e governança](#regras-e-governança)
- [Estado atual](#estado-atual)
- [Como estender (adicionar um agente novo)](#como-estender-adicionar-um-agente-novo)
- [Créditos e agradecimentos](#créditos-e-agradecimentos)
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

Sete vistas complementares da mesma coisa, do conceito ao disco. **As vistas 2 a 6 não foram desenhadas à mão**: são a saída do agente [Geração de Diagramas C4](agents/geracao-diagramas/AGENT.md) rodando sobre este próprio repositório como demanda — o Arquiteto de Soluções Junior IA aplicado a si mesmo, com `desenho.md`, `dados.md` e as jornadas do próprio time como fonte. Os specs que geraram cada imagem estão em [`docs/diagrams/archify/`](docs/diagrams/archify/).

> [!TIP]
> Todo diagrama abaixo é clicável — abra em tamanho real, alguns são largos. Os SVGs seguem o tema claro/escuro do seu sistema.

### 1. As seis camadas do Arquiteto de Soluções Junior IA

O **Arquiteto de Soluções Junior IA** é montado em seis camadas, de baixo para cima: cada camada depende da que veio antes.

[![As seis camadas do Arquiteto de Soluções Junior IA, da Identidade até os Agentes](docs/diagrams/01-camadas.svg)](docs/diagrams/01-camadas.svg)

*Fonte editável: [`docs/diagrams/01-camadas.mmd`](docs/diagrams/01-camadas.mmd)*

Tudo o que os agentes decidem, aprendem ou ainda não sabem fica registrado em [`memory.md`](memory.md), a memória viva do Arquiteto de Soluções Junior IA.

### 2. Contexto — quem conversa com o Arquiteto de Soluções Junior IA

A vista mais alta: cada caixa é um **bounded context** inteiro, com os agentes daquele domínio colapsados dentro dele, e o único ator de fora é a **Pessoa Operadora** — que dispara a demanda, responde às perguntas de escopo e aprova o portão de saída. Todo o resto acontece entre os agentes.

[![Diagrama de contexto C4: bounded contexts do Arquiteto de Soluções Junior IA e os atores externos](docs/diagrams/archify/c4-contexto.svg)](docs/diagrams/archify/c4-contexto.svg)

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
├── docs/diagrams/          # Vistas do próprio agente (Mermaid à mão + C4 gerado pelo pipeline)
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
- Só para **regerar** os diagramas C4: Python 3 (stdlib) e Node.js ≥18 — o [ArchiFy](https://github.com/tt-a1i/archify) já vem vendorizado em `skills/vendors/archify/` (ver [Créditos e agradecimentos](#créditos-e-agradecimentos)). Ver [`scripts/README.md`](scripts/README.md).

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
> `demandas/` está em `.gitignore`, não faz parte deste repositório público: os artefatos de cada demanda ficam só no seu clone local. As demandas usadas para validar a cadeia durante o desenvolvimento deste agente foram todas sintéticas (empresa, SDR, orçamento e decisões fictícios), e por isso não foram publicadas — mantenha o mesmo cuidado com as suas.

## Formas de uso

A cadeia completa (demanda crua → pacote entregue) é o uso principal, mas não é o único. O mesmo time atende recortes menores — em todos eles as regras valem igual: suposições e trade-offs escritos, nenhum agente decidindo fora do próprio escopo, e aprovação humana antes de qualquer coisa sair como "entregue".

### 1. Transformar um SDR ou pedido de negócio em pacote de arquitetura completo

O caminho padrão. Você cola o pedido cru e recebe entendimento, desenho, dados, segurança, infraestrutura, custo, observabilidade, testes, jornadas, riscos, ADRs e o handoff — com rastreabilidade de cada escolha.

```text
/arquiteto-solucoes Precisamos integrar o CRM ao WhatsApp para atendimento ativo. Orçamento X, prazo Y.
```

### 2. Avaliar uma arquitetura que já existe (as-is de terceiros)

Quando o objeto não é um sistema a projetar, mas um desenho de outra equipe a avaliar. Já rodou com um insumo único e fraco (uma foto de tela de diagrama): o insumo é transcrito literalmente para `insumos/`, com o que estava ilegível marcado como lacuna, e cada agente devolve **parecer com grau de evidência declarado** em vez de especificação.

```text
/arquiteto-solucoes Avalie a arquitetura desta equipe. Insumo: insumos/diagrama-transcrito.md
```

### 3. Segunda opinião adversarial sobre um desenho já decidido

Você já tem a arquitetura; quer saber o que quebra. Testes e Qualidade confere o desenho contra os requisitos não funcionais e aponta pontos únicos de falha, Riscos e Mitigação prioriza tudo e exige mitigação ou aceite explícito por risco. O ganho real é o contraditório entre agentes — uma recomendação destrutiva já foi retirada pelo próprio autor depois de outro agente mostrar o que ela destruiria.

### 4. Comparar provedores de cloud e estimar custo antes de fechar orçamento

Infraestrutura e Deployment escolhe hospedagem por componente sem provedor fixo ([ADR 001](adrs/adr-001-cloud-agnostica-por-criterio-de-negocio.md)), e Estimativa de Custo traduz isso em custo por componente, comparando os provedores que eram viáveis. Serve para defender número em comitê, não só para escolher tecnologia.

### 5. Gerar e manter os diagramas C4 sincronizados com a documentação

O agente de Geração de Diagramas C4 formaliza o que outros já decidiram (spec → candidato mínimo → SVG/HTML interativo, arquitetura e sequência) e **nunca decide arquitetura**. Como ele lê `desenho.md`/`dados.md` em vez de redesenhar à mão, os diagramas não dessincronizam da documentação. Os diagramas deste README são exatamente essa saída, com o time rodando sobre o próprio repositório.

### 6. Formalizar decisões como ADRs reaproveitáveis

Toda decisão importante vira um ADR com portão de aprovação humana próprio, e só entra no compêndio — passando a valer para demandas futuras — depois do aceite explícito. Dá para usar o time só para isso: registrar uma decisão já tomada com contexto, alternativas recusadas e custo aceito.

### 7. Traduzir o pacote técnico para stakeholder e quebrar em backlog

Comunicação com Stakeholders reescreve o pacote sem jargão, focando custo, prazo e risco principal, e termina com uma pergunta clara de aprovação. Entrega e Handoff quebra o resultado em épicos e mantém a tabela de quem responde o quê depois que os agentes saem de cena.

### 8. Acompanhar uma demanda em andamento, sem interromper

```text
/arquiteto-solucoes status <nome-da-demanda>
```

Mostra o que já rodou e o que falta sem despachar nenhum agente novo. O custo de processamento de cada demanda fica registrado em [`telemetria-agentes.md`](telemetria-agentes.md).

### Exemplo completo: do pedido de negócio ao pacote de arquitetura

A demanda quase nunca chega em linguagem de arquitetura. Chega como **pedido de negócio** — um memorando para o comitê, escrito por quem sente a dor, sem uma linha de jargão técnico. É esse o insumo que a cadeia foi feita para receber, e este exemplo é o formato completo: um pedido de negócio real de ponta a ponta, e o que o time devolve.

É também o primeiro perfil que dispara **os dois especialistas sob demanda ao mesmo tempo** — há decisão real de plataforma analítica *e* decisão real de modelo de IA.

<details>
<summary><strong>O pedido, exatamente como o negócio escreve</strong></summary>

```text
/arquiteto-solucoes

SOLICITAÇÃO DE NEGÓCIO — CENTRAL DE INTELIGÊNCIA CORPORATIVA
Para: Comitê de Estratégia / Diretoria de Tecnologia e Negócios

1. O PROBLEMA
Nossa informação está em ilhas. Anos de histórico de cliente presos em sistemas
legados que só a engenharia de dados consegue acessar, e leva dias. Contratos,
gravações de reunião, relatórios e páginas internas espalhados em pastas,
SharePoint e e-mail, sem busca centralizada.
Hoje, para responder "quais clientes de varejo reclamaram de atraso nos últimos
6 meses, e o que foi prometido nas reuniões de acordo?", três pessoas gastam
dois dias. O custo é perda de agilidade, retrabalho e decisão tomada com dado
incompleto.

2. A VISÃO
Queremos que qualquer pessoa da empresa "converse" com a base de conhecimento:
unificar o histórico de cliente com todos os documentos, organizar em etapas
(original → limpo → pronto para o negócio), criar uma busca que entenda
significado e não só palavra-chave (quem procura "insatisfação" acha
"reclamação" e "falha"), e um assistente que responde em português citando a
fonte ("conforme contrato X, página 5").

3. BENEFÍCIOS ESPERADOS
Analistas gastando 70% menos tempo procurando informação. Identificar padrão de
insatisfação antes do cancelamento (churn). Pergunta de 3 dias respondida em
segundos. Só quem tem permissão vê dado sensível. A plataforma aguenta 5x mais
documentos e 5x mais usuários sem travar.

4. ESCOPO
Faremos: integração diária com o histórico de clientes; um repositório seguro
que aceita qualquer arquivo; transcrição automática de áudio para texto; busca
semântica num portal interno; assistente de chat em aplicação web.
Não faremos: substituir ERP ou banco operacional; integrar rede social ou dado
externo; responder qualquer coisa fora do universo de dados da empresa.

5. CRITÉRIOS DE SUCESSO
Resposta em menos de 10 segundos. Resposta correta e com fonte correta em 90%
dos testes internos. 80% dos times de análise e comercial usando ativamente em
3 meses. Custo por pergunta abaixo de R$ 0,05.

6. RISCOS QUE JÁ NOS PREOCUPAM
Vazamento de dado sensível — queremos controle de acesso rigoroso e trilha de
auditoria de quem perguntou o quê. IA inventando resposta — o assistente só
pode responder com base no que temos, e dizer "não encontrei" quando não achar.
Demora na implementação — preferimos um piloto com um recorte pequeno antes de
abrir para todo o histórico.
```

</details>

**O primeiro trabalho é tradução, não desenho.** Nada acima é uma decisão técnica, e o time não trata como se fosse. Entendimento e Escopo mapeia as **capacidades de negócio** (TOGAF) e Desenho de Arquitetura as traduz em **bounded contexts** (DDD) — os limites dos componentes saem do domínio, nunca da conveniência técnica. Só então cada frase vira requisito com dono:

| O negócio disse | Vira, e quem responde |
| --- | --- |
| "resposta em menos de 10 segundos" | RNF de latência ponta a ponta, conferido contra o desenho por **Testes e Qualidade** — inclusive onde o orçamento de tempo é gasto (busca vs. geração) |
| "correta e com a fonte certa em 90%" | Requisito de rastreabilidade da resposta + critério de aceite mensurável, com **Especialista IA/ML** dono da abordagem e **Observabilidade** dona de como isso é medido em produção |
| "custo por pergunta abaixo de R$ 0,05" | Restrição de custo unitário que amarra decisão técnica, em `custo.md` por **Estimativa de Custo** — é o número que derruba ou aprova opções, não um detalhe de rodapé |
| "aguentar 5x mais documentos e usuários" | RNF de escala e disponibilidade, dividido entre **Infraestrutura e Deployment** (o que escala) e **Testes e Qualidade** (onde quebra primeiro, pontos únicos de falha) |
| "só quem tem permissão vê dado sensível" + trilha de auditoria | Autorização por integração e tratamento por dado sensível em `seguranca.md`, com o que a lei exige, por **Segurança e Compliance** |
| "a IA não pode inventar" | Risco nomeado, priorizado e com mitigação **ou aceite explícito** em `riscos.md`, por **Riscos e Mitigação** |
| "piloto antes de abrir para todo o histórico" | Faseamento no `handoff.md`, quebrado em épicos por **Entrega e Handoff** |
| "não substituir ERP, não integrar dado externo" | Não-escopo escrito em `entendimento.md` — o que está fora vale tanto quanto o que está dentro |

**O que o time devolve, e onde:**

| Entregável | Arquivo | Dono |
| --- | --- | --- |
| Entendimento, capacidades de negócio, escopo e **não-escopo** | `entendimento.md` | Entendimento e Escopo |
| Desenho de componentes e integrações por bounded context | `desenho.md` | Desenho de Arquitetura |
| Diagramas C4 (contexto, containers, sequência) | `diagramas/` | Geração de Diagramas C4 — formaliza o que já foi decidido, nunca decide |
| Fluxo de dados: entidades, dono, evento vs. consulta, retenção, sensibilidade | `dados.md` | Modelagem de Dados |
| Decisões de plataforma analítica e de modelo de IA | `dados-analytics.md`, `ia-ml.md` | Os dois especialistas — **só se o gatilho bater de verdade** |
| Hospedagem, escala, disponibilidade e escolha de provedor | `infraestrutura.md` | Infraestrutura e Deployment |
| Custo por componente, comparando provedores viáveis | `custo.md` | Estimativa de Custo |
| Segurança, acesso e compliance | `seguranca.md` | Segurança e Compliance |
| Riscos priorizados, cada um com mitigação ou aceite | `riscos.md` | Riscos e Mitigação |
| Métricas, traces e alertas da solução | `observabilidade.md` | Observabilidade e Telemetria (frente 1) |
| Cada decisão importante, com alternativas descartadas | um ADR em `adrs/` | Trade-offs e ADR — portão de aprovação humana próprio |
| **O material do comitê**, sem jargão, com a pergunta de aprovação no fim | `comunicacao.md` | Comunicação com Stakeholders |
| Épicos para o backlog e quem responde o quê depois | `handoff.md` | Entrega e Handoff |

**Sobre stack já imposta.** Se o pedido de negócio já vier com produto decidido — porque uma norma corporativa fixou a plataforma, ou porque ela já está em produção —, o time **não finge que escolheu**: registra a restrição como decisão externa e anterior, no formato do [ADR 023](adrs/adr-023-restricao-de-stack-herdada-externa-registrada-sem-alterar-o-adr-001-sad-008-sync-dados-ia.md), e o [ADR 001](adrs/adr-001-cloud-agnostica-por-criterio-de-negocio.md) (cloud agnóstica) **não é excepcionado** — ele governa o que a casa escolhe, e nesse caso ela não escolheu. O *uso* segue integralmente sob exame: topologia, retenção, isolamento de ambientes, pontos únicos de falha, custo e granularidade de acesso. Restrição de produto não é imunidade arquitetural.

**O que o time faz que um prompt único não faz.** Antes de tudo, **confirma o nome da demanda com você** — nome de demanda nunca é inventado por agente. Depois, cada decisão fica sob o dono dela: quem decide como a resposta cita a fonte não é quem decide retenção de dado bruto, que não é quem decide o teto de custo por pergunta. Cada um escreve as próprias suposições e trade-offs. E nada sai como "entregue" sem **aprovação humana explícita** no portão de saída — que é exatamente o momento em que `comunicacao.md` vai ao comitê, terminando com a pergunta que precisa de resposta.

> [!NOTE]
> Uma demanda desse porte é longa e cara em tokens. O custo real fica em `demandas/<nome-da-demanda>/custo-processamento.md` e em [`telemetria-agentes.md`](telemetria-agentes.md). Acompanhe com `/arquiteto-solucoes status <nome-da-demanda>`, que não despacha agente novo.

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

- As seis camadas do Arquiteto de Soluções Junior IA estão sólidas, o roteiro de 18 atividades está fechado, sete demandas reais já rodaram ponta a ponta via `/arquiteto-solucoes` de verdade (despacho por subagente, não simulação), com custo de processamento medido em tokens reais — ver `telemetria-agentes.md`.
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

## Créditos e agradecimentos

### ArchiFy — o motor por trás de todos os diagramas deste repositório

Todo diagrama C4 e de sequência que você viu acima foi renderizado pelo **[ArchiFy](https://github.com/tt-a1i/archify)**, de **[@tt-a1i](https://github.com/tt-a1i)**, com base no trabalho original *architecture-diagram-generator* da **Cocoon AI**. Nosso agradecimento sincero ao time do ArchiFy por publicar o projeto em código aberto — ele resolveu, e bem, um problema que nós teríamos resolvido mal.

| | |
| --- | --- |
| **Projeto** | [github.com/tt-a1i/archify](https://github.com/tt-a1i/archify) · [página do projeto](https://tt-a1i.github.io/archify/) |
| **Autoria** | tt-a1i (Archify) · Cocoon AI (obra original) |
| **Licença** | MIT — texto integral e avisos de copyright preservados em [`skills/vendors/archify/LICENSE`](skills/vendors/archify/LICENSE) |
| **Versão vendorizada** | `v2.14.0`, em `skills/vendors/archify/` |
| **Como usamos** | CLI nativo (`archify.mjs validate` / `deliver`), conduzido pelo agente [Geração de Diagramas C4](agents/geracao-diagramas/AGENT.md) |

**O que ele nos deu.** Antes do ArchiFy, os diagramas deste projeto eram ASCII escrito à mão dentro dos documentos, e dessincronizavam do desenho na primeira mudança. O ArchiFy trocou isso por um pipeline determinístico: o agente escreve um candidato mínimo em JSON tipado, o `validate` devolve **diagnósticos acionáveis** (sobreposição, aresta cruzando nó, ritmo, folga de rótulo) e o `deliver` entrega HTML interativo autocontido. O ganho decisivo para nós foi o motor de layout: paramos de calcular posição em pixel e roteamento de conexão por conta própria — decisão registrada em [`memory.md`](memory.md), 2026-08-16 — e o gerador passou a fazer o que faz melhor que nós.

**Como usamos, e o que isso não significa.** Mantemos uma cópia vendorizada para que o repositório rode sem passo de instalação, sempre com o `LICENSE` e os avisos de copyright originais preservados, como a MIT exige. Este projeto também é MIT, então as duas licenças convivem sem atrito. **Não somos afiliados ao ArchiFy nem à Cocoon AI, e este agradecimento não é endosso de nenhum dos lados**: os diagramas gerados aqui são responsabilidade deste time, não do projeto que os renderiza. Bug de renderização pertence ao [repositório deles](https://github.com/tt-a1i/archify/issues); bug de conteúdo de diagrama pertence a nós.

Se o ArchiFy te for útil, dê uma estrela no repositório deles — é o tipo de projeto que merece.

## Licença

[MIT](LICENSE.md). Uso, cópia, modificação e distribuição livres, sem garantia, mantendo o aviso de copyright.

## Contribuindo

O fluxo de contribuição e o Acordo de Licença de Contribuição (CLA) estão em [CONTRIBUTING.md](CONTRIBUTING.md). Toda contribuição aceita é incorporada sob a mesma licença MIT.
