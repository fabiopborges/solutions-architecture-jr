# ADR 013 — LLM via API de terceiros (não modelo próprio) + arquitetura RAG (não fine-tuning) para Plataforma-IA-Corporativa-V1

## Status
**Proposto.** Aguardando revisão de uma pessoa sênior ou líder técnico do time. Não vale como decisão oficial até essa revisão acontecer.

## Demanda de origem
`demandas/plataforma-ia-corporativa-v1/` — decisão tomada pelo Especialista em IA/ML (`ia-ml.md`, Decisões 1 e 2), a partir de sinalização do Desenho de Arquitetura (`desenho.md`, seção 5, item 1). Formalizada aqui por Trade-offs e ADR, não decidida de novo.

## Contexto / Problema
RF01 (consulta em linguagem natural sobre conteúdo corporativo heterogêneo e mutável) e RF02 (geração automática de conteúdo) exigem uma capacidade de IA generativa. Duas decisões encadeadas precisavam ser tomadas: (1) hospedar/treinar modelo próprio vs. consumir LLM via API de terceiros; (2) dentro da abordagem de IA, arquitetura RAG (recuperação aumentada de geração) vs. fine-tuning de modelo. Esta é a primeira demanda desta casa com esse perfil — **o compêndio não tem precedente** para nenhuma das duas escolhas.

RNF02 confirma porte pequeno/médio (dezenas a poucas centenas de usuários internos). RNF07 confirma PII/dado sensível como fato firme, com necessidade de controle de acesso granular por trecho (ver ADR sobre criptografia e o desenho de C6). RF03/RNF06 confirmam que os sistemas de origem (ERP, CRM, RH/folha) mudam continuamente.

## Alternativas consideradas

### Decisão 1 — Modelo próprio auto-hospedado vs. API de terceiros
| Critério | Modelo próprio | API de terceiros (escolhida) |
|---|---|---|
| Custo em porte pequeno/médio | Custo fixo de infraestrutura de GPU, tipicamente subutilizada nesse volume | Custo variável por token, tende a ficar baixo nesse volume |
| Complexidade operacional | Alta — exige expertise de serving de modelo, versionamento, monitoramento de inferência; sem evidência de que o time tenha essa capacidade hoje | Baixa — consumir uma API |
| PII (RNF07) | Dado nunca sai do ambiente da empresa | Dado sai a cada chamada — exige DPA, garantia de não-treinamento com dados do cliente, possível restrição de região |

**Modelo próprio foi descartado** porque, no porte confirmado, tende a custar mais (infraestrutura fixa ociosa) e exige capacidade operacional (MLOps de serving) que a demanda não sinalizou existir, sem ganho de qualidade correspondente. A vantagem real de modelo próprio (dado nunca sai do ambiente) é resolvida de outra forma — mascaramento/filtragem de PII antes do envio e escolha de provedor com garantias contratuais — sem pagar o custo fixo.

### Decisão 2 — RAG vs. fine-tuning
| Critério | Fine-tuning | RAG (escolhida) |
|---|---|---|
| Conteúdo que muda com o tempo (RF03/RNF06) | Cada mudança relevante exigiria novo ciclo de retreino — caro e lento | Atualização incremental via reindexação (C5→C3), sem retreino |
| Citação de fontes (RF01) | Não natural — informação fica implícita nos pesos, sem rastreabilidade | Natural — resposta gerada a partir de trechos identificáveis |
| Filtragem de acesso por sensibilidade em tempo real (RF04/RF05/RNF07, C6) | **Incompatível** — dado sensível usado no treino fica embutido nos pesos, não é possível filtrar por usuário/papel depois do fato | Compatível — filtragem acontece sobre os trechos recuperados, antes da síntese |
| Risco de vazamento de PII memorizada | Real — modelos fine-tunados podem memorizar e reproduzir dados de treino | Baixo — PII permanece no índice, sob controle de acesso |

**Fine-tuning foi descartado** por ser estruturalmente incompatível com o requisito de filtragem de acesso granular por sensibilidade em tempo de consulta (RF04/RF05/RNF07), que é central a esta demanda (BC4/C6 do desenho) — não apenas uma questão de custo/manutenção.

## Decisão
Adotar **LLM consumido via API de terceiros** (não modelo próprio auto-hospedado) e **arquitetura RAG** (não fine-tuning) como abordagem de IA para RF01 (BC1/C2) e RF02 (BC2/C4), com o LLM Gateway (componente técnico compartilhado do desenho) abstraindo o provedor concreto por trás de uma interface única.

Condicionantes explícitas mantidas junto com a decisão (não são decisões separadas, são parte do mesmo pacote):
- Filtragem de acesso (C6) sempre antes do envio ao LLM, nunca depois.
- Minimização/mascaramento de PII no prompt quando o dado identificável não for estritamente necessário para responder.
- Contrato de processamento de dados (DPA) e garantia de não-treinamento com dados do cliente, como condição de viabilidade do provedor de LLM escolhido — não um detalhe posterior.

## Consequências / Trade-offs aceitos
- **Dependência de fornecedor único de LLM** (risco de disponibilidade, custo e política de retenção de dado de terceiro) — mitigado pelo LLM Gateway, que reduz o custo de trocar de provedor se a decisão precisar ser revista.
- **PII sai do ambiente da empresa a cada chamada de API** — risco assumido conscientemente, mitigado por filtragem prévia via C6, mascaramento de dado não essencial, e exigência contratual de DPA/não-treinamento. Residência de dado (qual região do provedor de LLM) fica condicionada à lacuna 5 (política de segurança/compliance concreta, ainda aberta) — se a política vier a vedar envio de dado a terceiro, esta decisão inteira precisa ser revista com Segurança e Compliance.
- **Custo de inferência escala com o crescimento de usuários** (RF06/RNF02 preveem expansão de público) — não muda a recomendação hoje, mas deve ser reavaliado quando lacunas 1 (pico de uso) e 2 (orçamento) forem respondidas.
- **Model drift residual no modelo de embeddings** (não no conhecimento factual, que é resolvido por RAG): se o provedor descontinuar/atualizar uma versão de embedding, os vetores já indexados podem ficar inconsistentes, exigindo reindexação planejada do corpus — tratado como manutenção operacional esperada, não como falha de desenho.
- **Fine-tuning não descartado para todo sempre**: se no futuro houver necessidade de ajustar tom/formato de saída (não conhecimento factual), técnicas mais leves (few-shot, fine-tuning restrito a estilo com dados não sensíveis) podem ser reavaliadas — não é requisito atual.

## Coerência com o compêndio e ADRs anteriores
Nenhum ADR anterior desta casa trata de LLM, RAG ou fine-tuning — **este é o primeiro ADR desse perfil na casa**, sem precedente a contradizer ou reforçar. Coerente com o compêndio seção 2 (nenhum provedor de serviço gerenciado é preferido de antemão; decisão por critério de negócio e requisito real). Candidato a virar referência para demandas futuras de perfil semelhante (IA generativa/RAG corporativo), mas ainda não promovido a padrão geral da casa — cada demanda futura deve reavaliar porte, sensibilidade de dado e capacidade operacional do time antes de reaproveitar esta conclusão automaticamente.

## Revisão
Pendente. Aguardando revisão explícita de pessoa sênior ou líder técnico do time antes de status mudar para "Aprovado".
