# ADR 023 — Restrição de stack herdada (Azure, `unity catalog`, MongoDB, Vector Search, RAG) registrada como decisão externa, sem alterar o ADR 001

## Status

**Aprovado**, na **versão 2, como está escrito** — incluindo as cinco partes da decisão.

**Revisado e aprovado por:** quem estava operando a sessão, em **2026-08-17**, em resposta direta às quatro perguntas de revisão registradas ao final deste documento. A aprovação foi repassada pelo Orquestrador, que não decidiu por conta própria — a decisão de revisão é de uma pessoa, não de um agente. Não há aqui registro de nome, cargo ou papel dessa pessoa, porque essa informação não foi dada a esta atividade e não seria correto inferi-la.

**O que a aprovação cobriu, ponto a ponto (registrado porque cada um deles era condição de validade):**

1. O enquadramento **"restrição externa herdada / ADR 001 não é o instrumento aplicável"**, em vez de "exceção ao ADR 001" — aprovado como formulado.
2. **A suposição S13 se sustenta:** a restrição é corporativa vinculante, não preferência da equipe autora da plataforma. Esta era a condição que, se falsa, exigiria **rejeitar** este ADR em vez de ajustá-lo. Ela se sustenta, e o ADR é válido por isso — não apesar disso.
3. A delimitação do que a restrição **não** congela (parte 3) — aprovada.
4. A separação **produto × topologia** (parte 4), com o corolário de que um padrão de criação de recurso não é uma decisão — procede. **Nenhuma informação foi trazida de que a topologia atual tenha sido objeto de decisão corporativa formalizada.**

**Versão:** 2 (2026-08-17). A versão 1 foi escrita a partir da sinalização do Entendimento e Escopo (seção 7.1). A versão 2 acrescentou a **parte 4 da decisão** (a restrição atesta produto, não topologia) e a **parte 5** (fronteira para mudanças futuras de topologia), a partir de repasse formal do agente de Infraestrutura e Deployment (`infraestrutura.md`, seção 4.2 e encaminhamento 17). Nada da versão 1 foi retirado. A aprovação humana recaiu sobre esta versão 2.

**Escopo estrito desta aprovação:** ela cobre este ADR e **somente** este ADR. Não aprova o parecer de `SAD-008 - SYNC DADOS IA`, não fecha nenhuma das perguntas em aberto ao solicitante, não resolve os desvios de regra declarados por outros agentes da cadeia (que seguem abertos para julgamento humano) e não valida nenhum outro artefato da demanda.

## Demanda de origem

`demandas/sad-008-sync-dados-ia/` — `SAD-008 - SYNC DADOS IA`.

Acionado por sinalização do agente de Entendimento e Escopo (`entendimento.md`, seção 7.1, item 3), que encaminhou o ponto explicitamente **como sinalização, não como decisão dele**. A avaliação de mérito ("isto merece um ADR?"), o enquadramento e a redação são desta atividade.

## Aviso de leitura, antes de qualquer outra coisa

**Este ADR não escolhe Azure. Não escolhe `unity catalog`, MongoDB, Vector Search nem RAG. Nenhuma dessas escolhas foi feita por este time.**

O que este ADR decide é **como a casa trata, e registra, uma escolha de produto que já foi feita fora dela e já está em produção** — para que o registro exista e não seja confundido, no futuro, com uma escolha nossa.

Quem chegar aqui procurando precedente para usar Azure numa demanda nova: não é isto. Vá ao **ADR 001**, que continua sendo o instrumento aplicável para toda demanda em que a casa efetivamente escolha o provedor.

**E, igualmente importante (ver parte 4 da decisão):** este ADR **não atesta que a topologia atual da plataforma tenha sido decidida por alguém**. Ele registra que um *produto* foi decidido fora desta casa. Região, redundância, zona, tier, isolamento de ambientes e modelo de hospedagem **não** estão cobertos pela restrição, e não há evidência alguma de que tenham sido objeto de decisão consciente. Quem citar este ADR como formalização da configuração em produção estará citando algo que ele não diz.

## Contexto / problema

`SAD-008 - SYNC DADOS IA` não é um desenho novo. O pedido, esclarecido na rodada 2 do Entendimento (`entendimento.md`, seção 1.2), é um **parecer arquitetural sobre uma plataforma de dados de interação já em produção**, desenhada e operada por outra equipe, cobrindo da captação da interação (CN01) ao consumo agêntico (CN05/CN06). Os entregáveis nomeados por quem pediu são gaps, riscos, pontos únicos de falha e perguntas não respondidas.

Em resposta direta à pergunta Q4(e), quem opera a sessão declarou:

> Azure, `unity catalog`, MongoDB, Vector Search e RAG são **restrição corporativa formal** — decisão organizacional já tomada, anterior e externa a esta demanda, com o sistema já em produção. Não é proposta desta equipe nem hipótese a validar.

Daí nasce o problema **que é de arquitetura, e não de tecnologia**:

1. **O ADR 001** (`adrs/adr-001-cloud-agnostica-por-criterio-de-negocio.md`, aprovado em 2026-08-09) e a seção 1 do compêndio estabelecem que a cloud da casa é agnóstica de provedor, escolhida por critério de negócio **a cada demanda**. Um leitor futuro do compêndio pode encontrar o artefato de `SAD-008` e ler "SAD-008 usou Azure" como **reversão do ADR 001 ou precedente contra ele**. Não é nem uma coisa nem outra — mas, sem registro, a distinção se perde, e o padrão da casa se corrói em silêncio, por acúmulo de leituras erradas e não por decisão.
2. **O risco simétrico, e menos óbvio:** uma restrição de stack declarada tende a ser lida pela equipe que executa como **imunidade arquitetural** — "a stack está decidida, então não temos o que analisar aqui". Isso esvaziaria o parecer exatamente onde ele tem mais valor, porque o que foi congelado é a **escolha de produto**, não o **uso** que se faz dele.
3. **O terceiro risco, levantado pelo agente de Infraestrutura e Deployment na versão 2 deste ADR, e que os dois primeiros não cobriam:** o registro de uma restrição de produto pode ser lido, no futuro, como se **atestasse a topologia atual**. "Azure" foi decidido corporativamente. "Azure em uma região não registrada em lugar nenhum, sem redundância documentada, com opção de redundância de armazenamento desconhecida e tier de gateway desconhecido" **não é a mesma decisão** — e não há evidência de que alguém a tenha tomado conscientemente. Os achados que sustentam isso são concretos e estão em `infraestrutura.md`: nenhuma das 20 linhas da tabela componente × hospedagem é determinada pelo diagrama, e em nove delas o diagrama não determina nada; a região não aparece em nenhum artefato; o tier do gateway, que decide se um SPOF é real ou não, é desconhecido; e não se sabe qual opção de redundância de armazenamento está ativa.

### Por que isto merece um ADR (avaliação explícita desta atividade)

Recusar era uma resposta possível, e o argumento para recusar é forte e precisa ficar escrito: **ADR registra decisão, e a escolha da stack não é decisão desta casa.** Registrá-la como se fosse seria falsear o histórico e, pior, criar exatamente o precedente que se quer evitar.

Mesmo assim, **avalio que merece ADR**, por três razões:

1. **Existe uma decisão da casa aqui, e ela não é sobre tecnologia.** É a decisão de *como se posicionar* diante de uma restrição externa: aceitá-la como dado de entrada, não reabrir a escolha de produto no parecer, e delimitar o que continua sob exame. Isso tem alternativas reais (ver abaixo), tem consequências e tem riscos aceitos. É material de ADR pela definição da própria skill.
2. **O lugar certo do registro é `adrs/`, não `demandas/`.** A ressalva já está escrita em `entendimento.md` seção 7.1 e está bem escrita — mas vive dentro da pasta de uma demanda, que é justamente onde ninguém procura ao começar a próxima. O ADR existe para ser reaproveitado por demandas futuras; a preocupação levantada ("alguém no futuro vai ler errado") é, por definição, uma preocupação de demanda futura.
3. **Registrar a não-decisão é a única forma de impedir que ela seja lida como decisão.** O silêncio não é neutro: sem ADR, o único vestígio de `SAD-008` no acervo será um parecer sobre uma plataforma Azure, sem nada dizendo por que Azure está ali.

## Alternativas consideradas e por que foram descartadas

- **A — Não registrar nada; deixar a ressalva apenas em `entendimento.md` seção 7.1.** Descartada. A ressalva é correta, mas fica confinada a `demandas/sad-008-sync-dados-ia/`. A regra `rules/never.md` proíbe que um agente carregue contexto de uma demanda anterior para uma demanda nova — ou seja, o único canal legítimo de memória entre demandas é o compêndio/ADR. Deixar a ressalva só na demanda garante que ela **não** chegue a quem precisa dela.
- **B — Registrar como "exceção ao ADR 001", ou como emenda/supersessão parcial dele.** Descartada, e esta é a alternativa mais tentadora e mais perigosa. "Exceção" pressupõe que o ADR 001 se aplicava e foi dispensado — o que autorizaria, no futuro, "abrir exceção ao ADR 001" como via de contorno para escolhas que a casa de fato faz. Não é o caso: aqui a casa não escolheu nada, porque não havia nada a escolher. O ADR 001 governa decisões de provedor **tomadas pela casa**; num as-is herdado ele não é violado nem dispensado, ele simplesmente **não é o instrumento aplicável**. A diferença entre "exceção" e "instrumento não aplicável" é o que mantém o ADR 001 intacto.
- **C — Promover Azure (e/ou `unity catalog`, Vector Search) à stack aprovada do compêndio, seção 1, já que "a casa está usando".** Descartada. Que uma outra área da organização tenha padronizado Azure para uma plataforma específica não é evidência de que Azure seja a melhor escolha para as próximas demandas desta casa — e adotar isso como padrão contraria a substância do ADR 001, não só a sua forma. Além disso, `SAD-008` não produziu nenhuma comparação de provedores (não estava no escopo), então promover a stack seria promover algo **sem nenhum critério de negócio apurado**, que é exatamente o que o ADR 001 proíbe.
- **D — Tratar a restrição como hipótese a validar e o parecer recomendar a troca de stack.** Descartada por estar fora do escopo declarado pela pessoa que pediu (F01/F03 do `entendimento.md`) e por ser arquiteturalmente ruim mesmo se estivesse dentro: o sistema carrega tráfego real, e recomendação de troca de produto sem mandato para tanto produz recomendação inaplicável, que é o risco R13 já registrado no Entendimento.
- **E — Registrar a restrição como decisão externa herdada, com delimitação explícita do que ela não congela.** **Escolhida.**

## Decisão

Para `SAD-008 - SYNC DADOS IA`, a casa decide o seguinte, em cinco partes indivisíveis (as partes 4 e 5 foram acrescentadas na versão 2):

**1. A stack entra como restrição externa herdada, não como decisão desta equipe.** Azure, `unity catalog`, MongoDB, Vector Search e RAG são registrados como **dado de entrada** da demanda, com origem em decisão corporativa formal anterior e externa, sobre sistema já em produção. Nenhum agente da cadeia reabre a escolha de produto no parecer.

**2. Este registro não altera, não excepciona e não cria precedente contra o ADR 001.** O ADR 001 permanece integralmente em vigor e continua sendo o instrumento aplicável a toda demanda em que a casa escolha o provedor. `SAD-008` **não promove Azure a padrão da casa**, não entra na stack aprovada (compêndio, seção 1) e não pode ser citado como precedente de escolha de provedor. O componente `unity catalog` implica uma plataforma (Databricks) que **não** faz parte da stack aprovada — fica registrado como **componente herdado, não adotado**. MongoDB é o único item que coincide com a stack aprovada (compêndio, seção 1); coincidência, não consequência.

**3. Restrição de stack não é imunidade arquitetural.** O que está congelado é a **escolha de produto**. Permanecem integralmente dentro do escopo do parecer, e devem ser examinados: topologia, redundância e pontos únicos de falha; configuração e dimensionamento; política (ou ausência de política) de retenção e expurgo por camada; acoplamento entre componentes e entre as duas vias de ingestão; custo corrente de operação e de inferência; governança de acesso, classificação de dado pessoal e linhagem; observabilidade e prova de sincronização. Um achado nessas frentes **não** é questionamento da stack, e nenhum agente deve tratá-lo como se fosse.

**4. A restrição atesta o produto; não atesta a topologia — e este ADR não pode ser citado como se atestasse.** O que a decisão corporativa formal cobre, e a única coisa que este ADR registra como decidida, é a **escolha de produto**. Nada neste documento, e nada na condição de "restrição corporativa formal", constitui evidência de que a **configuração em execução** — região, opção de redundância de armazenamento, zonas, tier de gateway, modelo de hospedagem por componente, isolamento de ambientes, topologia de rede da captação — tenha sido decidida, escrita ou aprovada por quem quer que seja. Sobre essas escolhas, o acervo desta demanda mostra **silêncio**, não decisão. Onde houver silêncio, a leitura correta é "ninguém sabe se foi decidido", nunca "está formalizado". Em particular, **um padrão de criação de recurso não é uma decisão**: uma conta de armazenamento criada com a opção de redundância padrão produz uma consequência de disponibilidade e de residência de dado pessoal que ninguém escolheu — e a restrição corporativa de produto não converte esse padrão em decisão formal, nem lhe empresta autoridade.

**5. Mudança futura de topologia é decisão nova da casa, sob o ADR 001, e pede ADR próprio.** Se este parecer levar a alterar região, opção de redundância, zonas, tier ou modelo de hospedagem, isso **não** é execução desta restrição herdada: é a casa escolhendo, e portanto entra sob o ADR 001 com todos os seus critérios de negócio, com ADR próprio. Fica assim explícita a fronteira: o produto é herdado e não se discute nesta demanda; a topologia nunca foi herdada, porque nunca foi decidida.

### Por que a parte 3 não bastava (registro de rastreabilidade)

A parte 3 já dizia que a restrição congela produto e não uso, e listava topologia e redundância como dentro do escopo do parecer. Ela **não** cobria o ponto novo, e a diferença é real, não redacional:

- A parte 3 é **procedimental**: diz aos agentes desta cadeia **o que podem examinar**. Endereça o risco de autocensura.
- A parte 4 é **probatória**: diz a qualquer leitor futuro **o que este registro prova e o que não prova**. Endereça um risco diferente — o de alguém citar o ADR 023 como formalização da configuração atual, encerrando uma discussão que nunca foi tida.

Um agente pode obedecer integralmente à parte 3 (examinar a topologia a fundo, como `infraestrutura.md` fez) e ainda assim o documento ser mal citado depois. Autorização de escopo e valor probatório são coisas distintas, e só a segunda protege contra a leitura errada daqui a um ano — que é exatamente a preocupação que originou este ADR.

## Consequências e trade-offs aceitos conscientemente

- **Ganho principal:** a próxima pessoa que abrir o compêndio encontra, junto com o ADR 001, a razão pela qual `SAD-008` roda em Azure — e essa razão diz explicitamente "não foi escolha nossa, não copie isto". O padrão da casa deixa de depender de alguém lembrar o contexto.
- **Ganho secundário:** o parecer ganha uma autorização escrita para ser incisivo sobre uso, topologia, custo e governança, sem que isso seja confundido com desrespeito à restrição corporativa. Sem a parte 3 da decisão, a tendência natural de uma equipe júnior diante de uma restrição declarada é a autocensura.
- **Custo aceito:** o parecer perde a alavanca mais forte que uma revisão de arquitetura normalmente tem, que é propor a substituição do produto. Todo achado precisará ser endereçável dentro da stack dada.
- **Risco assumido conscientemente (o mais relevante):** pode existir achado cuja **única** correção real seja a troca de um componente da stack. Se isso ocorrer, o parecer não decide nem recomenda a troca — registra o achado, registra que a correção dentro da restrição é paliativa, e **escala explicitamente à instância que detém a decisão corporativa de stack**, que não é este time. Um achado desse tipo silenciado por causa da restrição seria falha grave do parecer; um achado desse tipo convertido em recomendação de troca seria decisão fora da atividade (`rules/never.md`).
- **Risco assumido: premissa falseável.** Este ADR se apoia inteiramente na suposição S13 do `entendimento.md` — de que "restrição corporativa formal" significa decisão organizacional vinculante, e não preferência da equipe que desenhou a plataforma. **Se S13 se revelar falsa, este ADR perde a premissa e deve ser revisitado**, junto com F03 e a seção 7.1 do Entendimento: uma preferência de equipe não é restrição herdada, é proposta técnica, e proposta técnica é analisável pelo parecer como qualquer outra.
- **Risco assumido: o registro pode ser lido pelo avesso.** Alguém pode citar este ADR como "a casa aceitou Azure". A mitigação está na forma: o aviso de leitura no topo, a parte 2 da decisão, e a exigência de que o resumo na seção 3 do compêndio (após aprovação humana) diga explicitamente que não promove Azure a padrão. Se o resumo do compêndio for escrito sem essa ressalva, a mitigação falha.
- **Ganho da parte 4 (versão 2):** a restrição corporativa deixa de poder ser usada como escudo retroativo para configurações que ninguém decidiu. Numa plataforma em produção com dado pessoal, a consequência prática é direta — a opção de redundância de armazenamento e a posição de residência de dados podem ser, tecnicamente, a mesma decisão, e uma delas herdada de um padrão de criação de recurso. A parte 4 garante que esse ponto continue sendo tratado como decisão pendente, e não como fato consumado com respaldo corporativo.
- **Risco assumido na parte 4:** afirmar "não há evidência de que a topologia tenha sido decidida" pode soar, para a equipe que opera a plataforma, como acusação de descuido. Não é, e o ADR registra que não é: a ausência de decisão registrada é afirmação sobre **o acervo documental disponível a esta cadeia**, não sobre a competência de quem construiu. É inteiramente possível que a topologia tenha sido decidida com cuidado e apenas não esteja escrita onde pudéssemos ver — e nesse caso o achado muda de categoria (vira gap de documentação), mas não desaparece, porque contingência não se planeja sobre o que não está escrito. Aceito o custo de relação que essa formulação pode ter, porque suavizá-la produziria exatamente a leitura errada que a parte 4 existe para impedir.
- **Custo menor, aceito:** um ADR que não decide tecnologia pode parecer burocracia para quem o encontra. Aceito, porque o custo do lado oposto — precedente silencioso corroendo o ADR 001 — é maior e é irreversível na prática, já que ninguém detecta a corrosão enquanto ela acontece.

## Checagem de conflito com o compêndio e ADRs anteriores

Conferido `substrate/compendium.md` seção 3 antes de escrever, conforme `rules/never.md` e o passo 2 da skill.

- **ADR 001 (aprovado) — cloud agnóstica por critério de negócio.** Não há contradição, e essa é a afirmação central deste ADR. Escopos distintos: o ADR 001 governa escolha feita pela casa; este ADR registra escolha feita fora dela. **Sinalizo, porém, que a proximidade é próxima o bastante para exigir revisão humana atenta** — se a pessoa revisora entender que a fronteira "decisão da casa" vs. "restrição externa" não se sustenta neste caso, então o enquadramento inteiro deste ADR cai e a alternativa B (exceção formal ao ADR 001) precisa ser reconsiderada. É o ponto do documento que mais merece contestação. **→ Submetido à revisão humana como pergunta 1 e sustentado em 2026-08-17: a fronteira se mantém, e a alternativa B (exceção formal ao ADR 001) permanece descartada.**
- **ADRs 003, 010, 012 (escolhas pontuais de provedor: AWS, GCP, AWS `sa-east-1`).** Sem contradição. Todas são escolhas **feitas pela casa** por critério de negócio, sob o ADR 001, e todas declaram não alterar o padrão geral. Este ADR segue a mesma disciplina de "não altera o padrão geral", pela via oposta: ali a casa escolheu e não generalizou; aqui a casa não escolheu.
- **ADR 021 (proposto) — stack aberta em vez de IDMC + Databricks.** Existe uma aparência de tensão, porque `unity catalog` é componente do ecossistema Databricks e o ADR 021 rejeita Databricks. **Registro que não há conflito, e por dois motivos independentes.** Primeiro, o ADR 021 não estabelece nenhuma proibição geral a Databricks na casa: ele rejeita uma proposta específica por falha num critério específico de outra demanda (restrição de 100% on-premises, que não existe em `SAD-008`). Segundo, e mais importante para a disciplina do OS, `rules/never.md` proíbe carregar contexto de uma demanda anterior para uma demanda nova — o raciocínio do ADR 021 **não é insumo** de `SAD-008` e não foi usado como tal aqui. O registro serve só para o efeito inverso: que ninguém leia `SAD-008` como reversão do ADR 021, do mesmo modo que não deve lê-la como reversão do ADR 001.
- **ADRs 013 e 014 (propostos) — LLM via API de terceiros com RAG, e índice vetorial.** Sem contradição. São decisões tomadas pela casa para outra demanda e outra plataforma. Em `SAD-008`, RAG e busca vetorial são **herdados**, não escolhidos, e nada aqui valida ou invalida aquelas decisões.
- Nenhum ADR anterior trata de plataforma de dados de interação, lakehouse com camadas Raw/Stage/curada, catálogo de dados ou parecer sobre sistema de terceiro em produção. `SAD-008` não reaproveita decisão pronta, conforme já observado em S11 do `entendimento.md`.

## Quem revisou, e o portão de aprovação humana desta atividade

**Portão cumprido.** Este ADR foi revisado e aprovado por quem estava operando a sessão em **2026-08-17**, na versão 2, como está escrito. O status foi alterado de "Proposto" para "Aprovado" **somente após** essa resposta humana — nenhum agente o alterou por conta própria, e nenhuma mensagem de agente foi tratada como aprovação.

As quatro perguntas abaixo são preservadas na íntegra, com as respostas obtidas, porque elas são o conteúdo da revisão: quem ler este ADR daqui a um ano precisa saber **o que exatamente foi aprovado**, e não apenas que houve aprovação.

**Perguntas dirigidas a quem estava operando a sessão, e as respostas:**

1. **O enquadramento se sustenta?** Registrar a stack de `SAD-008` como *restrição externa herdada* (ADR 001 não aplicável) em vez de *exceção ao ADR 001* (ADR 001 aplicável e dispensado). É a escolha central deste documento e a que mais afeta o ADR 001 no longo prazo.
   → **Resposta: sim, aprovado como formulado.** O enquadramento "instrumento não aplicável" prevalece sobre "exceção".
2. **A premissa S13 é verdadeira?** "Restrição corporativa formal" é mesmo decisão organizacional vinculante, e não preferência da equipe que desenhou a plataforma? Se for preferência, este ADR deve ser rejeitado, não aprovado.
   → **Resposta: S13 se sustenta.** A restrição é corporativa vinculante, não preferência da equipe autora. A condição de rejeição não se materializou, e é por isso — e só por isso — que este ADR pôde ser aprovado em vez de descartado. **Se essa premissa vier a se mostrar falsa mais tarde, a aprovação não a salva: o ADR precisa ser revisitado.**
3. **A parte 3 da decisão está calibrada?** A lista do que a restrição *não* congela define o quanto o parecer pode ser incisivo sobre uma plataforma de outra equipe que já está em produção. Se estiver larga demais ou estreita demais para o mandato real que a demanda tem, é aqui que se corrige.
   → **Resposta: aprovada como está.** A lista vale como mandato do parecer.
4. **(Novo na versão 2) A separação produto × topologia procede?** As partes 4 e 5 afirmam que a decisão corporativa cobre o produto e **não** atesta a configuração em execução, e que mudar região/redundância/tier seria decisão nova sob o ADR 001. Se você souber que a topologia atual **também** foi objeto de decisão corporativa formalizada — coisa que o acervo desta demanda não mostra —, então a parte 4 está errada como afirmação de fato e precisa ser corrigida antes de qualquer aprovação.
   → **Resposta: procede.** Nenhuma informação foi trazida de que a topologia atual tenha sido objeto de decisão corporativa formalizada. As partes 4 e 5 valem como escritas.

**Registro no compêndio: executado em 2026-08-17**, após a aprovação e não antes, em `substrate/compendium.md` seção 3, com as duas ressalvas obrigatórias que este ADR condicionou — que **não promove Azure a padrão da casa e não é precedente de escolha de provedor**, e que **não atesta a topologia** (parte 4).

### Advertência que sobrevive à aprovação, e que deve circular junto com ela

Agora que este ADR é decisão oficial, ele será citado — e uma frase dele circula mais que as outras. Fica registrado, de forma permanente, o que ela significa e o que não significa:

> **"Não há evidência de que a topologia tenha sido decidida" é afirmação sobre o acervo documental disponível a esta cadeia — uma foto de diagrama, sem acesso ao portal do provedor, ao IaC, à telemetria, aos runbooks ou ao time que opera. NÃO é afirmação sobre a competência de quem construiu ou opera a plataforma.**

É inteiramente possível que a topologia tenha sido decidida com cuidado e apenas não esteja escrita onde esta cadeia pudesse ver. Nesse caso o achado muda de categoria — vira gap de documentação — mas não desaparece, porque contingência não se planeja sobre o que não está escrito. Quem citar a parte 4 sem esta advertência estará usando um ADR aprovado para dizer algo que ele não diz.
