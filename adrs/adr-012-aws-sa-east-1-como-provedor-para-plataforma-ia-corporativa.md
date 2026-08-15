# ADR 012 — AWS (`sa-east-1`) como provedor de cloud para Plataforma-IA-Corporativa-V1

## Status
**Proposto.** Aguardando revisão de uma pessoa sênior ou líder técnico do time. Não vale como decisão oficial até essa revisão acontecer (portão de aprovação humana próprio desta atividade, distinto do portão de saída geral do orquestrador).

## Demanda de origem
`demandas/plataforma-ia-corporativa-v1/` — decisão tomada por Infraestrutura e Deployment (`infraestrutura.md`, seções 1 e 3), formalizada aqui por Trade-offs e ADR (não decidida de novo).

## Contexto / Problema
A Plataforma-IA-Corporativa-V1 precisa de um provedor de cloud para hospedar C1–C7 e o LLM Gateway (RAG sobre conteúdo corporativo com PII confirmado por RNF07). O compêndio (seção 1) fixa cloud como **agnóstica de provedor** (ADR 001): a escolha é feita por demanda, com base em critério de negócio (seção 2 do compêndio: custo, residência/compliance, latência, maturidade do serviço gerenciado necessário, vendor lock-in, aderência ao que o time já opera). Esta é a primeira demanda desta casa com perfil de plataforma de IA generativa/RAG — não há precedente direto no compêndio para esse tipo de escolha.

RNF07 (PII/dado sensível em RH, Financeiro e Comercial) torna a região onde o serviço de IA generativa roda uma decisão de compliance, não só de performance: dado sensível não deveria cruzar fronteira de país só para consultar um LLM gerenciado, ainda que a norma de compliance formal (LGPD) siga como lacuna aberta no entendimento (lacuna 5).

## Alternativas consideradas
| Alternativa | Por que foi descartada (ou não) |
|---|---|
| **Azure, Brazil South** | Forte em residência de dado (garantia de região única), mas a pesquisa de Infraestrutura encontrou lacuna concreta de recurso relevante: "file search" (central para RAG corporativo) não está disponível em Brazil South, forçando usar região fora do Brasil para RAG completo ou aceitar capacidade reduzida — nenhuma das duas é ideal dado RNF07. |
| **GCP, `southamerica-east1`** | Sem evidência confirmada de Vertex AI Search / Agent Search como implantação single-region nessa região (documentação indica operação predominante via multi-região US/EU para essa capacidade) — desvantagem direta para manter PII dentro do Brasil na etapa de recuperação de contexto. Não descartado por princípio, mas atrás dos outros dois neste critério específico, para esta demanda. |
| **AWS, `sa-east-1`** (escolhida) | Único dos três provedores com evidência confirmada, na pesquisa realizada, de que a capacidade de IA generativa gerenciada (modelo + RAG, via Bedrock/Bedrock Knowledge Bases) opera inteiramente dentro da região brasileira, sem lacuna de recurso conhecida, com múltiplas opções de backend vetorial maduras na mesma região. |

Critérios que não desempataram entre os três provedores: residência de dado isolada (os três têm região no Brasil), latência (nenhum requisito de latência geográfica crítica documentado), custo (sem teto de orçamento confirmado — lacuna 2 aberta, tratado em cenários, não como filtro definitivo), aderência ao que o time já opera (nenhuma demanda anterior desta casa usou AWS para IA generativa; as duas demandas mais recentes usaram GCP para outro perfil de necessidade — tratado como critério neutro).

## Decisão
Adotar **AWS, região `sa-east-1` (São Paulo)**, como provedor de cloud para todos os componentes desta demanda que precisam de nuvem (C1–C7 e LLM Gateway), pelo critério decisivo de maturidade do serviço gerenciado de IA generativa/RAG dentro da região exigida (compêndio seção 2), reforçado pelo critério de residência/compliance dado RNF07.

Esta é uma decisão **pontual desta demanda**, não altera o padrão geral da casa (cloud continua agnóstica por demanda — ADR 001, compêndio seção 1).

## Consequências / Trade-offs aceitos
- **Vendor lock-in aceito conscientemente**, mitigado por desenho: o LLM Gateway (componente técnico do desenho) desacopla C2/C4 do provedor de modelo concreto — trocar de Bedrock para outro provedor de IA é troca de implementação atrás desse gateway, não redesenho de domínio. Os serviços de aplicação (C2, C4, C5, C6, C7) são containers Docker padrão (stack aprovada), portáveis entre provedores. O lock-in real fica concentrado na camada de IA/dados gerenciada (Bedrock, índice vetorial), onde a maturidade regional compensa o risco.
- **Custo não é filtro definitivo nesta decisão**: sem teto de orçamento confirmado (lacuna 2 do entendimento), a comparação de custo entre provedores foi tratada como cenários de ordem de grandeza (ver `infraestrutura.md` seção 7), não como comparação fechada de menor preço. Risco assumido: se o orçamento vier muito apertado, esta escolha pode precisar de reavaliação de custo fino (não necessariamente de provedor).
- **Estimativas de custo usadas na comparação não são cotação fechada** para `sa-east-1` — precisam de validação por Estimativa de Custo com a calculadora oficial da AWS antes de qualquer compromisso.
- **Residência de dado tratada como critério de negócio prudente**, não como exigência regulatória formalmente confirmada (lacuna 5 ainda aberta) — se Segurança e Compliance confirmar norma concreta de residência, isso reforça esta escolha; se revelar restrição incompatível com AWS `sa-east-1`, esta decisão precisa ser revisitada.

## Coerência com o compêndio e ADRs anteriores
- **ADR 001** (cloud agnóstica por critério de negócio): coerente — esta é uma escolha pontual por demanda, com critério de negócio explícito (maturidade de IA/RAG na região), não uma fixação de provedor padrão da casa.
- **ADR 010** (GCP escolhido para `projeto-nuvem-vendas-v1`): **divergência esperada, não contradição**. Cada demanda tem perfil e critérios de negócio próprios (ADR 010 priorizou cotas gratuitas de API Gateway/Hosting sob teto de orçamento apertado; esta demanda prioriza maturidade regional de IA generativa/RAG dado RNF07, sem teto de orçamento confirmado). Nenhuma das duas altera o padrão geral da casa (cloud agnóstica).
- **ADR 003 e ADR 004** (AWS escolhido para outras demandas): mesma direção de provedor, mas por critérios de negócio distintos e específicos daquelas demandas (camada gratuita para volume baixo; hospedagem para integração CRM/Serasa) — não é reaproveitamento automático do precedente, é nova análise chegando à mesma conclusão de provedor por razões próprias.
- Nenhuma contradição identificada com `substrate/compendium.md` seção 3.

## Revisão
Pendente. Aguardando revisão explícita de pessoa sênior ou líder técnico do time antes de status mudar para "Aprovado".
