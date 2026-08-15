# Skill: Entendimento da Demanda e Escopo

## Quando usar
Sempre que uma demanda nova de arquitetura chega, antes de qualquer outro agente (desenho, dados, segurança, infraestrutura, observabilidade etc.) começar a trabalhar. Esta é a primeira atividade da cadeia. Nenhum outro agente deveria desenhar nada sem o documento que esta skill produz.

## Dono
O agente "Entendimento e Escopo" é o dono desta atividade. Qualquer outro agente que tiver dúvida sobre o que foi pedido, o que está dentro ou fora de escopo, ou qual é a real necessidade de negócio por trás da demanda, pergunta a este agente em vez de adivinhar (regra de [[rules/never]]).

## Passos
0. **Confirme o nome da demanda explicitamente com quem pediu, antes de qualquer outra coisa.** Este agente nunca inventa, deriva ou abrevia esse nome sozinho (regra de [[rules/never]]). Se quem pediu não deu um nome, pergunte diretamente ("como vamos chamar esta demanda?") e espere a resposta, não segue com um nome provisório. Esse nome, exatamente como dado, vira o nome da pasta `demandas/<nome-da-demanda>/` onde todo o resto da cadeia grava seus artefatos.
1. Reúna o pedido original tal como ele chegou (quem pediu, o texto ou fala original, em que canal). Não reescreva o pedido antes de registrar a versão original.
2. Faça perguntas de esclarecimento sobre: objetivo de negócio por trás do pedido, restrições conhecidas (prazo, orçamento, tecnologias obrigatórias ou proibidas), e quem são os stakeholders que vão aprovar o resultado.
3. Confira `substrate/compendium.md` para ver se já existe uma decisão ou padrão anterior que se aplica a essa demanda. Se existir, cite-o em vez de repetir a discussão do zero.
4. **Mapeie as capacidades de negócio envolvidas (TOGAF Business Architecture):** que capacidade de negócio essa demanda fortalece ou cria (ex: "gestão de pedidos", "atendimento ao cliente"), qual é a cadeia de valor onde ela se encaixa, e quais funções de negócio (não sistemas) participam. Isso vem antes de qualquer requisito técnico, o desenho técnico nasce daqui.
5. Escreva os requisitos funcionais (o que o sistema precisa fazer) e não funcionais (performance, disponibilidade, segurança, escala) separadamente, ligando cada requisito funcional a uma capacidade de negócio do passo 4.
6. Escreva explicitamente o que está dentro do escopo e o que está fora do escopo desta demanda. Ambíguo entra na lista de suposições, não em um dos dois lados sem aviso.
7. Liste as suposições feitas e os riscos já visíveis nesse estágio inicial (regra de sempre: expor suposições e trade-offs).
8. Produza um documento único de entendimento e escopo que os outros agentes vão usar como insumo de entrada, incluindo o [[agents/desenho-de-arquitetura/AGENT]], que usa o mapa de capacidades de negócio para começar a modelagem de domínio (DDD).

## Artefato de saída
Um documento `demandas/<nome-da-demanda>/entendimento.md` com as seções: pedido original, objetivo de negócio, capacidades de negócio e cadeia de valor (TOGAF), requisitos funcionais (ligados à capacidade de negócio correspondente), requisitos não funcionais, dentro do escopo, fora do escopo, suposições, riscos conhecidos. A pasta `demandas/<nome-da-demanda>/` é criada aqui, com o nome exato confirmado no passo 0, e é essa mesma pasta que todo o resto da cadeia usa para os próprios artefatos desta demanda.

## Como é bem feito
Qualquer outro agente da cadeia consegue ler esse documento e começar a trabalhar sem precisar perguntar "o que exatamente foi pedido?" nem "qual é o nome desta demanda?". Se um agente de desenho, dados ou segurança tiver que voltar e perguntar algo que já deveria estar nesse documento, a skill não foi bem executada. Especificamente: o Desenho de Arquitetura consegue identificar bounded contexts direto do mapa de capacidades de negócio, sem ter que descobrir a estrutura de negócio por conta própria.
