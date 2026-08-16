# Skill: Desenho da Arquitetura de Solução

## Quando usar
Assim que o documento de entendimento e escopo estiver pronto (skill [[skills/entendimento-e-escopo/SKILL]]). É o segundo elo da cadeia, o que já roda na mão do time hoje logo depois do entendimento.

## Dono
O agente "Desenho de Arquitetura" é o dono desta atividade. Qualquer outro agente com dúvida sobre por que um componente foi escolhido, como dois blocos se conectam, ou onde ficam os riscos técnicos do desenho, pergunta a este agente em vez de adivinhar (regra de [[rules/never]]).

## Passos
1. Leia o documento de entendimento e escopo por completo antes de desenhar qualquer coisa. Não comece do zero se ele já cobre requisitos, restrições e capacidades de negócio.
2. **Modele o domínio (DDD) a partir das capacidades de negócio do escopo:** identifique os contextos delimitados (bounded contexts), a linguagem ubíqua de cada um (os termos que o negócio usa, não os termos técnicos), e os agregados principais dentro de cada contexto. Um bounded context que não corresponde a nenhuma capacidade de negócio do escopo é sinal de que o domínio foi mal entendido, volte para [[agents/entendimento-e-escopo/AGENT]] em vez de inventar um contexto novo.
3. Confira `substrate/compendium.md` por um padrão de arquitetura de referência ou ADR já usado antes para um domínio parecido. Reaproveitar um padrão existente vem antes de inventar um novo.
4. Liste os componentes principais da solução (serviços, bancos, filas, integrações externas), um microsserviço por bounded context (ou por um agrupamento justificado de contextos pequenos), nunca uma divisão técnica que ignore os limites de domínio definidos no passo 2. **Atribua um `id` canônico (slug, ex: `c1_portal_web`) a cada componente e a cada ator externo, junto do rótulo informal (`C1`).** Esse `id` é a fonte única que [[agents/geracao-diagramas/AGENT]] e [[agents/jornadas-do-usuario/AGENT]] devem reaproveitar depois — nenhum dos dois deve inventar o próprio esquema de IDs (já aconteceu de rodarem em paralelo e gerarem specs com IDs divergentes pro mesmo componente, poluindo o relatório de derivação com falsos `[ORFAO]`/`[FALTA-CATALOGO]`).
5. Desenhe como esses componentes se conectam entre si (quem chama quem, síncrono ou assíncrono, o que cada integração carrega), respeitando que a comunicação entre bounded contexts é sempre por contrato explícito (evento ou API), nunca por acesso direto ao modelo interno de outro contexto.
6. Para cada componente e cada escolha de tecnologia, escreva o porquê, ligado a um requisito funcional, não funcional, restrição do documento de escopo, ou ao bounded context que ele representa (regra de sempre expor suposições e trade-offs).
7. Não decida provedor de cloud aqui, isso é escopo de [[agents/infraestrutura-e-deployment/AGENT]]. Só sinalize, por componente, se ele precisa de nuvem e qualquer restrição de negócio que a escolha de provedor precisa respeitar (ex: dado que não pode sair de uma região, latência crítica para um mercado específico).
8. Aponte explicitamente onde ficam os riscos e pontos fracos do desenho (ex: componente único sem redundância, dependência externa não confiável, bounded context com responsabilidade ambígua).
9. Assim que os bounded contexts, componentes e integrações estiverem decididos, **sinalize explicitamente** (na seção de encaminhamento do seu artefato) que [[agents/geracao-diagramas/AGENT]] precisa ser acionado para gerar o diagrama C4 (Contexto/Container) determinístico — você não tem como despachá-lo diretamente (subagentes não despacham outros subagentes), quem despachou seu trabalho precisa fazer isso. Não desenhe ASCII art manual aqui, isso é escopo dele.

## Artefato de saída
Um documento `demandas/<nome-da-demanda>/desenho.md` com: mapa de bounded contexts e linguagem ubíqua (DDD), lista de componentes (um por contexto), descrição das integrações entre eles (o diagrama C4 correspondente é gerado por [[agents/geracao-diagramas/AGENT]] em `demandas/<nome-da-demanda>/diagramas/`, referenciado aqui), restrições de negócio relevantes para a escolha de cloud por componente (sem decidir o provedor), o porquê de cada escolha, e a lista de riscos/pontos fracos identificados.

## Como é bem feito
Dá para ver os componentes e como eles se conectam sem ambiguidade, cada escolha tem um porquê ligado ao escopo (nada "porque sim"), e os riscos e pontos fracos já estão à vista, prontos para o agente de Riscos e Mitigação (ainda não conquistado) aprofundar depois.
