# Auditoria do OS - 2026-08-09
Objetivo: Criar um conjunto de agentes que funciona como um Arquiteto de Soluções Júnior. Cada atividade específica é representada por um agente próprio com skill focada só naquela tarefa, a estrutura roda em loop (dúvida vira pergunta ao agente dono da atividade), cobrindo do entendimento da demanda até a entrega final, incluindo observabilidade, telemetria e medições, com domínio real sobre escolha de cloud por critério de negócio e sobre TOGAF/DDD para funções de negócio, economizando tokens e paralelizando ao máximo.

## Boletim
| Camada      | Nota        | Por quê (uma linha específica) |
|-------------|-------------|--------------------------|
| Identidade  | Solid       | `CLAUDE.md` nomeia o time como conjunto de agentes por atividade, cita o portão sempre/nunca, e agora inclui as duas linhas de domínio pedidas nesta sessão: cloud sem provedor fixo e modelagem de negócio via TOGAF/DDD. |
| Substrato   | Compounding | `substrate/compendium.md` responde a pergunta difícil por completo: stack, padrões da casa (incluindo o porquê de microsserviços via DDD), e dois ADRs reais e **aprovados** (`adrs/adr-001`, `adrs/adr-002`) na seção 3. Compounding porque a skill de Trade-offs e ADR já alimenta essa seção automaticamente a cada decisão aprovada, o compêndio cresce sozinho com o uso. |
| Regras      | Solid       | `rules/never.md` e `rules/always.md` transformam o pior erro (loop infinito de dúvida) numa regra dura testável, com hook de limite de 3 rodadas. |
| Skills      | Compounding | As 14 atividades do roteiro têm `SKILL.md` real, com passos, artefato de saída e critério de pronto. Compounding porque `skills/roadmap.md` declara explicitamente que nenhuma skill está terminada, elas melhoram com o uso real, e a evolução de cloud/DDD/TOGAF desta sessão já é um exemplo disso acontecendo de verdade. |
| Ferramentas | Solid       | `tools.md` lista as três fontes que o objetivo precisa (repositório de docs/ADRs, backlog, observabilidade real), todas somente leitura, mas nenhuma está de fato conectada ainda, então não é compounding, ainda depende de alguém plugar a fonte real. |
| Agentes     | Solid       | Os 14 agentes de atividade mais o Orquestrador formam uma cadeia real com pontos de paralelismo (até 4 ramos simultâneos a partir do Desenho), um ponto de sincronização total (Documentação Final) e um portão de saída de 4 itens. Não é compounding ainda porque nenhuma demanda real passou pela cadeia para provar isso na prática. |

Nenhum campo sensível foi sinalizado em `memory.md`. O nome do revisor dos ADRs (Fabio Borges) foi dado voluntariamente para o campo "Revisado por" e não foi marcado como privado, então não há vazamento a corrigir.

## Os três movimentos que mais importam (em ordem)
1. **Agentes/Skills, mas na prática** - rode uma demanda real pela cadeia inteira (Entendimento → Desenho → ... → Entrega e Handoff). Hoje todo o desenho é sólido no papel, mas nenhuma das 14 skills nem o Orquestrador foram testados com uma demanda de verdade. É a maior alavancagem agora porque valida (ou quebra) tudo que foi construído, e é exatamente o que `memory.md` já aponta como próxima ação.
2. **Ferramentas** - conecte pelo menos a fonte "repositório de código/documentação" de `tools.md`, hoje listada como planejada mas sem nenhuma ligação real. Isso resolve a pergunta em aberto de `memory.md` ("onde esse material vai passar a viver formalmente") e permite que `substrate/sources.md` pare de depender só da memória de quem descreveu a stack de cabeça.
3. **Substrato, frente 2 de Observabilidade** - `telemetria-agentes.md` ainda está vazio, é só o esqueleto criado junto com a skill de Observabilidade e Telemetria. Assim que a demanda real do movimento 1 rodar, essa é a primeira entrada real a registrar, para a telemetria dos próprios agentes deixar de ser só uma promessa de formato.

## O que já está funcionando
- A evolução pedida nesta sessão (cloud agnóstica por critério de negócio, TOGAF/DDD para funções de negócio) foi propagada de forma consistente por toda a cadeia, entendimento mapeia capacidade de negócio, desenho traduz em bounded context, infraestrutura escolhe provedor por critério, sem nenhuma referência solta ao padrão antigo (conferido por busca em todos os arquivos, só sobrou uma referência antiga que já foi corrigida durante esta auditoria).
- Os dois ADRs (`adrs/adr-001`, `adrs/adr-002`) seguem o formato completo da própria skill que os criou, com alternativas descartadas e trade-offs aceitos explícitos, e foram de fato revisados por uma pessoa nomeada antes de virarem oficiais, não só carimbados como aprovados sem revisão real.

## A única coisa a fazer agora
Escolher uma demanda real (mesmo pequena) e rodar ela pela cadeia inteira de agentes, do Entendimento e Escopo até a Entrega e Handoff, para descobrir o que quebra ou fica raso na prática antes de confiar o fluxo a uma demanda importante.
