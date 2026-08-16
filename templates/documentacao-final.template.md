<!--
Template de esqueleto fixo para demandas/<nome-da-demanda>/documentacao-final.md
Dono: agente Documentação Final (skills/documentacao-final/SKILL.md)

Regra: os headers abaixo (nível e texto, exceto o que está entre < >) são fixos e
devem aparecer nesta ordem em toda demanda. O CONTEÚDO de cada seção é livre —
é síntese, não dado estruturado — mas o ESQUELETO não muda de demanda para
demanda. Isso é o que permite comparar pacotes de demandas diferentes sem
precisar reaprender a estrutura a cada leitura.

Seções marcadas [CONDICIONAL] só entram se o artefato de origem existir nesta
demanda (ou, no caso de Jornadas do Usuário, se o VEREDITO dentro de
`jornadas.md` for positivo — o arquivo em si sempre existe, ver
skills/jornadas-do-usuario/SKILL.md, 2026-08-16). Se a seção condicional for
omitida, NÃO pule o número — renumere as seções seguintes para não deixar
buraco (ex: se o veredito de Jornadas for "nenhuma jornada aplicável", o que
seria "## 9." vira "## 8.", e assim por diante).
-->

# Pacote de Arquitetura Final — <Nome legível da demanda>

Demanda: `<slug-da-demanda>`
Agente: Documentação Final (ponto de sincronização total da cadeia — todos os ramos paralelos terminaram)

<Um parágrafo fixo no espírito de: "Este documento consolida, num único lugar navegável, tudo o que os agentes anteriores produziram. Cada seção cita o documento de origem completo, para quem revisar voltar à fonte. Nenhuma suposição, trade-off, risco ou pendência foi resolvida ou inventada por este agente — apenas organizados e citados.">

---

## ATENÇÃO — PENDÊNCIAS BLOQUEANTES DE RESPOSTA EXTERNA [CONDICIONAL — só se houver pendência que bloqueia decisão]

<Uma subseção `### Pendência N — <título>` por pendência. Cada uma diz: o que falta, quem precisa responder, e o que essa lacuna trava (cite os documentos/seções específicos que dependem da resposta). Se não houver nenhuma pendência bloqueante, omita esta seção inteira — não escreva "nenhuma pendência" como placeholder vazio.>

---

## Índice — documentos de origem completos

<Frase fixa explicando a coluna "Ordem de leitura", ver skills/documentacao-final/SKILL.md seção "Índice com ordem de leitura".>

| Ordem de leitura | Documento | Caminho | Agente responsável |
|---|---|---|---|
<Uma linha por artefato de entrada, numerada conforme a regra da SKILL.md.>

---

## 1. O que foi pedido (fonte: `entendimento.md`)

<Pedido original, objetivo de negócio, capacidades TOGAF mapeadas, requisitos funcionais/não funcionais, suposições assumidas.>

## 2. Desenho de arquitetura — bounded contexts e componentes (fonte: `desenho.md`)

### Diagrama de componentes/integrações (C1–Cn)

<Diagrama consolidado por [[agents/geracao-diagramas/AGENT]], referenciado por caminho em `demandas/<nome-da-demanda>/diagramas/`.>

### Componentes (resumo — detalhamento completo em `desenho.md`)

<Tabela ou lista: componente, responsabilidade, RF/RNF que satisfaz.>

## 3. Jornadas do usuário (fonte: `jornadas.md`) [CONDICIONAL — só se o veredito de `jornadas.md` for "jornadas identificadas"; se for "nenhuma jornada aplicável", omita a seção mas não deixe de citar o motivo do veredito em uma frase na seção 1 ou 2]

<Jornadas observáveis derivadas dos RFs já aprovados e dos componentes já decididos, com as visões de diagrama filtradas por jornada.>

## 4. Fluxo de dados (fonte: `dados.md`)

### Diagrama de fluxo de dados (evento vs. consulta)

<Entidades, dono de cada uma, eventos vs. consultas síncronas entre serviços.>

## 5. Infraestrutura e deployment (fonte: `infraestrutura.md`)

### Diagrama de infraestrutura/deployment

<Onde cada componente roda, qual provedor foi escolhido para esta demanda específica (a stack é agnóstica — o diagrama mostra a escolha feita, não assume provedor fixo).>

## 6. Segurança e compliance (fonte: `seguranca.md`)

<Autenticação/autorização por integração, tratamento por dado sensível, requisitos de compliance aplicáveis.>

## 7. Estimativa de custo (fonte: `custo.md`)

<Custo por componente, comparação entre provedores quando mais de um era viável.>

## 8. Observabilidade (fonte: `observabilidade.md`)

<Métricas por componente, estratégia de trace distribuído, limites de alerta.>

## 9. Testes e qualidade (fonte: `qualidade.md`)

<O desenho atende os RNFs do escopo? Pontos únicos de falha, integração com legado.>

## 10. Pesquisa e Benchmarking (fonte: `pesquisa-*.md`) [CONDICIONAL — uma subseção por pesquisa que rodou nesta demanda]

<Comparação de tecnologias/soluções que outro agente precisou para decidir algo que a stack aprovada não resolvia sozinha.>

## 11. ADRs formalizados nesta demanda (fonte: `adrs/*.md`) [CONDICIONAL — uma subseção `### ADR-NNN — <título>` por ADR disparado durante a cadeia]

<Um parágrafo por ADR: decisão, status (Proposto/Aceito), e o que trava enquanto não for aprovado.>

## 12. Resposta direta aos entregáveis pedidos pela demanda original

<Confronto explícito: o que foi pedido em `entendimento.md` vs. o que este pacote entrega, sem lacuna silenciosa.>

## 13. Portão de revisão deste pacote (autoconferência antes de entregar)

<Checklist do "Antes de passar o trabalho adiante" do AGENT.md: documentos de entrada confirmados, diagramas existem, cada seção cita a origem.>
