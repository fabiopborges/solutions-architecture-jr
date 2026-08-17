# Gerador de diagramas C4

Três scripts. `derivar_c4.py` (MVP 7) monta um spec de Container/Contexto automaticamente a partir de um catálogo estático + sequências por jornada, em vez de alguém traduzir `desenho.md` à mão — ver `../c4-schema.md`, seção "Pipeline invertido", para o porquê. `montar_candidato_arquitetura_archify.py` e `montar_candidato_sequencia_archify.py` traduzem esses specs para candidatos MÍNIMOS no formato nativo do ArchiFy (vendorizado em `skills/vendors/archify/`) — sem geometria em pixel, sem chamar o CLI. Quem chama `archify.mjs validate`/`deliver` sobre o candidato e conduz o loop de reparo pontual é o agente `geracao-diagramas`, via `Bash`, direto — não um script Python.

> **Pipeline nativo ArchiFy (2026-08-XX).** Substitui a geração anterior, em que `exportar_archify.py`/`exportar_sequencia_archify.py` calculavam toda a geometria (camadas, barycenter, posição em pixel, roteamento de conexão, `viewBox`) em Python e só entregavam ao ArchiFy um `.architecture.json` já 100% posicionado — isso contornava o `layout: {mode:"grid"}` nativo e o Automatic Port Spread do próprio ArchiFy. Ver `memory.md`, entrada de 2026-08-16, para o raciocínio completo da migração.

> **Geração de `.drawio` eliminada do projeto em 2026-08-16.** O script `gerar_c4.py` e as POCs que o antecederam (`../poc-drawpyo/`, `../poc-c4/`) foram removidos — decisão de não manter essa capacidade, não de adiá-la. Um agente dedicado de drawio, de responsabilidade única, pode vir a existir no futuro como peça isolada, mas não faz parte deste pipeline.

## Regra de padronização: 12 palavras por texto visível (2026-08-16)
Todo texto que aparece renderizado — `nome` de componente/ator/fronteira, `descricao` de componente, `papel` de ator (**estes dois viram `sublabel`, renderizado dentro da caixa** — não são metadado interno, esquecer eles foi o bug real da primeira versão desta regra), `rotulo` de conexão/mensagem — tem no máximo **12 palavras**. `montar_candidato_arquitetura_archify.py` e `montar_candidato_sequencia_archify.py` checam isso automaticamente (`checar_limite_palavras`/`checar_limite_palavras_sequencia`) antes de gravar o candidato e recusam gerar (`sys.exit(1)`, mensagem `[erro]` listando cada violação) se algum campo passar do limite — não truncam sozinhos. Escreva curto desde a autoria do catálogo/spec; detalhe completo vai em `NOTAS.md` ou na documentação de origem, nunca dentro do rótulo renderizado.

## Uso — `derivar_c4.py` (catálogo + sequências → specs de Container/Contexto)

```bash
python3 derivar_c4.py CATALOGO.json SEQUENCIA1.json [SEQUENCIA2.json ...] --saida-dir DIR [--titulo-base "Nome da demanda"]
```

- `CATALOGO.json`: catálogo estático (`atores[]`/`fronteiras[]`/`componentes[]`, sem `conexoes[]`) — normalmente produzido por [[agents/geracao-diagramas/AGENT]] a partir de `desenho.md`.
- `SEQUENCIA*.json`: um ou mais `sequencia-<journey_id>_spec.json`, produzidos por [[agents/jornadas-do-usuario/AGENT]].
- `--saida-dir DIR`: grava `c4-container-jornada-<id>.json` (um por sequência), `c4-container.json` (união de todas), e `c4-contexto.json` (Container colapsado por fronteira).
- Imprime um **relatório de derivação** no stdout: `[ORFAO]` (componente do catálogo nunca usado em nenhuma jornada, excluído dos diagramas) e `[FALTA-CATALOGO]` (participante de sequência ausente do catálogo, importado com atributos mínimos, status `desconhecido` → fallback). Esses avisos não são cosméticos — nunca devem ser silenciados, ver `c4-schema.md`.
- Se não existir nenhum `sequencia-<journey_id>_spec.json` (veredito de `jornadas.md` foi "nenhuma jornada aplicável" — o arquivo sempre existe, só o spec de sequência é que é condicional), pule este script — traduza `desenho.md` direto para `conexoes[]` de um spec de Container único (ver `skills/geracao-diagramas/SKILL.md`, passo 4).

## Uso — `montar_candidato_arquitetura_archify.py` (spec → candidato mínimo `architecture`)

```bash
python3 montar_candidato_arquitetura_archify.py ENTRADA.json SAIDA.architecture.json [--journey JOURNEY_ID] [--orientacao {vertical,horizontal}]
```

- `ENTRADA.json`: spec de Container/Contexto, no formato de `../c4-schema.md` (produzido por `derivar_c4.py`, ou traduzido direto de `desenho.md` quando não há jornada).
- `SAIDA.architecture.json`: candidato mínimo no formato `architecture.schema.json` do ArchiFy — **não é o HTML final**. O script NÃO chama `node archify.mjs` — quem faz isso é o agente (ver seção "O agente completa o fluxo" abaixo).
- O que o script decide (domínio, não geometria): categoria de cada componente (`classificar_tipo`), filtro por jornada (`filtrar_por_jornada`), ordem de leitura via análise de grafo + barycenter (`analisar_grafo`/`ordenar_linhas_por_barycenter`) — traduzida para `row`/`col` do `layout: {mode:"grid"}` nativo, e o tamanho de caixa por conteúdo (`largura_estimada`, análogo a escolher a largura de um rótulo — não é posição/rota).
- O que o script NUNCA faz: `pos` em pixel, `via`/`fromSide`/`toSide` de conexão, `viewBox` manual. Isso é reparo pontual guiado por diagnóstico do `validate`, aplicado pelo agente — ver `skills/vendors/archify/archify/references/authoring-contract.md`.
- Cada spec gerado por `derivar_c4.py` já está no formato que este script consome — rodar os dois em sequência é o fluxo normal.

## O agente completa o fluxo — `validate`/`deliver`/`visual-check` via Bash direto

Depois que o candidato está gravado, o agente `geracao-diagramas` chama o CLI do ArchiFy diretamente (nunca via `subprocess` num script Python):

```bash
node skills/vendors/archify/archify/bin/archify.mjs validate architecture SAIDA.architecture.json --quality showcase --json
```

Se `composition.status != "pass"`: ler `diagnostics[].code/subject/evidence/supportedFixes` e aplicar, via `Edit`, **um único** campo diagnosticado por vez — ordem de reparo em `references/authoring-contract.md` (schema/overlap → edge-through-node/endpoint-direction → crossings/corridors/rhythm → label clearance). Repetir `validate` até convergir. Duas notas de quem já rodou esse loop numa demanda real (`integracao-crm-oci-whatsapp`, ver Testes abaixo):

- **`via`/`labelAt` que exceda a extensão dos componentes some do desenho sem aviso do `validate`.** O `viewBox` automático nativo do tipo `architecture` mede só `components`/`boundaries` (não `connections`) — se um reparo empurra uma conexão pra fora dessa área (ex: faixa de rota "por fora" pra evitar cruzar um nó), é preciso fixar `meta.viewBox` manualmente cobrindo a nova extensão. `validate` não acusa isso; só um `visual-check`/inspeção visual do HTML entregue pega (ver `references/delivery-contract.md`, "Perceptual delivery gate" — é exatamente por isso que esse passo existe).
- **Diagramas densos podem passar de 2 rodadas de reparo.** `authoring-contract.md` recomenda no máximo 2 rodadas focadas antes de reportar o diagnóstico não resolvido; na prática, um diagrama com múltiplos back-edges próximos (ex: 3 componentes interligados por conexão de retentativa + alerta + auditoria, todos perto um do outro) pode legitimamente precisar de mais — o critério não é "nunca passar de 2", é "cada rodada precisa reduzir o número de diagnósticos"; pare e reporte com honestidade se duas rodadas seguidas não melhorarem.

### `cards` — suposições e trade-offs dentro do próprio diagrama

O ArchiFy tem um campo de nível superior `cards[]` (`{dot, title, items[]}` — ver `common.schema.json#/$defs/cards`) que renderiza painéis abaixo do diagrama. Nenhum dos scripts o gera — é o **agente** quem adiciona, via `Edit`, depois de gravar o candidato, traduzindo as suposições/trade-offs/pendências **já escritas** em `desenho.md` (seção de suposições e trade-offs) e, quando fizer sentido, riscos técnicos já sinalizados — nunca inventando conteúdo novo (mesma regra de sempre: só traduz o que outro agente já decidiu). Isso é o que dá ao diagrama a rastreabilidade que `rules/always.md` exige ("sempre expõe as suposições e os trade-offs") sem depender de quem lê ir consultar `desenho.md` à parte. Ver `skills/vendors/archify/archify/examples/web-app.architecture.json` para um exemplo real de uso (vendorizado, sempre disponível no repositório).

### `activations` — barra de ativação por participante (só sequência)

`montar_candidato_sequencia_archify.py` gera `activations[]` automaticamente (`montar_ativacoes`): cada participante que não é puramente externo (`type != "external"`) ganha uma barra de ativação cobrindo da primeira à última mensagem que o toca. É mecânico, determinístico, não exige ler nenhum documento de origem — por isso vive no script, diferente de `cards`.

### `views`/`segments` — narrativa guiada, OBRIGATÓRIA (2026-08-16, deixou de ser opcional), autorada pelo agente

`meta.views` (1 a 5 capítulos curados) e `segments[]` (fases nomeadas na linha do tempo, só sequência) também não são gerados pelos scripts — quem adiciona é o agente, via `Edit`, sempre, antes de todo `deliver`. Nenhum diagrama sai sem pelo menos uma visão guiada. Curar "qual é o caminho principal a destacar" é apresentação, não invenção de estrutura — a fonte do agrupamento vem sempre de algo já decidido em outro documento, nunca inventada aqui. Ordem de preferência (ver `skills/geracao-diagramas/SKILL.md`, passo 12):
1. Cenários/fluxos já nomeados em `desenho.md` (ex: "fluxo principal", "resiliência", "governança") — cada um vira um capítulo.
2. Mais de uma jornada (`journey_id` em `conexoes[]`) — cada jornada é um capítulo natural.
3. Fallback mecânico, sempre disponível: um capítulo por `fronteira` + um capítulo final "Visão geral" cobrindo tudo. Garante que até um diagrama pequeno/sem prosa rica ganhe pelo menos essa visão.

Aceite final (nunca editar o candidato depois de um `validate` que já passou):

```bash
node skills/vendors/archify/archify/bin/archify.mjs deliver architecture SAIDA.architecture.json SAIDA.html --quality showcase --json
```

`visual-check` (screenshots de containment em 4 resoluções) roda uma vez por HTML **consolidado**, na atividade de Documentação Final — não em cada diagrama intermediário (custo de Chrome/DevTools por diagrama). Ver `references/delivery-contract.md`.

## Dependências

- Python 3 (stdlib apenas, sem pacote externo) para os três scripts.
- Node.js (`node --version`, qualquer ≥18) + o ArchiFy vendorizado em `skills/vendors/archify/archify/` para os comandos `validate`/`deliver`/`visual-check` do agente. Sem instalação adicional — `node skills/vendors/archify/archify/bin/archify.mjs doctor` confirma que está pronto.

## Testes — `derivar_c4.py` (MVP 7)

- `teste-3-catalogo.json` + `teste-3-sequencia-jornada-x.json` — caso sintético desenhado de propósito pra disparar os dois avisos: um componente do catálogo nunca referenciado (`[ORFAO]`) e um participante de sequência fora do catálogo (`[FALTA-CATALOGO]`), mais uma mensagem `self` e duas `retorno` pra confirmar que são filtradas da projeção.
- Caso real: `demandas/<nome-da-demanda>/diagramas/catalogo-componentes.json` + `sequencia-*_spec.json` da demanda `integracao-crm-oci-whatsapp` — usado pra validar que `[FALTA-CATALOGO]` pega sozinho uma tensão real entre `desenho.md` (que descrevia um componente como "interno a outro") e `jornadas.md` (que o tratava como participante à parte), sem precisar de um agente comparando os dois documentos manualmente.

## Testes — `montar_candidato_arquitetura_archify.py` + fluxo `validate`/`deliver` do agente

Testado contra specs reais de `integracao-crm-oci-whatsapp` copiados para um diretório isolado (nunca dentro de `demandas/` real) — os 4 diagramas de arquitetura (Container geral, Contexto, e as duas visões filtradas por jornada) convergiram em `showcase` 9/9 depois do loop de reparo pontual do agente (o Container geral e a visão da jornada `alerta-falha-permanente` precisaram de reparo em conexões de retentativa/alerta que pulam camada — via bypass guiado por diagnóstico; as demais convergiram só com `labelDy`). `visual-check` confirmou containment equivalente (ou melhor) ao HTML de produção gerado pelo pipeline antigo para o mesmo diagrama.

## Uso — `montar_candidato_sequencia_archify.py` (spec de sequência → candidato mínimo `sequence`)

```bash
python3 montar_candidato_sequencia_archify.py SEQUENCIA_SPEC.json CATALOGO.json SAIDA.sequence.json
```

- `SEQUENCIA_SPEC.json`: `sequencia-<journey_id>_spec.json` produzido por [[agents/jornadas-do-usuario/AGENT]] (`mensagens[]` com `ordem`/`de`/`para`/`rotulo`/`protocolo`/`assincrona`/`tipo`).
- `CATALOGO.json`: `catalogo-componentes.json` da mesma demanda — usado só pra resolver nome/tipo de cada participante, nunca pra decidir estrutura.
- `ordem` vira posição Y determinística (passo fixo de 70px) — geometria de domínio (ordem temporal), não router genérico. Nomes do catálogo no formato `"C1 — Descrição"` são separados em `label` curto + `sublabel` completo (o renderer de sequência do ArchiFy tem um teto de 190px pro `label`, sem encolhimento de fonte — só o `sublabel` encolhe). Mensagens `tipo: "self"` (de==para) não têm primitiva no ArchiFy — viram `note` anexada à mensagem real mais próxima do mesmo participante; o script imprime `[SELF-COMO-NOTA]` no stderr pra cada uma, nunca descarta silenciosamente.
- **Diferente de `architecture`, o `viewBox` de sequência NÃO é automático** (o renderer usa um valor fixo `[920, 760]` quando `meta.viewBox` é omitido — ver `renderers/sequence/render-sequence.mjs`). Por isso este script calcula um `viewBox` inicial a partir do número de participantes e do `y` da última mensagem — dimensionamento por conteúdo, não escolha de rota.
- Renderer padrão pra diagrama de sequência desde 2026-08-16, substituindo o Mermaid manual (`docs/diagrams/04-sequencia.mmd` fica só como registro histórico do padrão anterior, não é mais gerado).
- Testado contra as duas jornadas de `integracao-crm-oci-whatsapp` (`lead-notificado` e `alerta-falha-permanente`) — ambas convergiram em `showcase` 9/9 direto, sem reparo adicional do agente, com o `viewBox` calculado por conteúdo e `activations[]` geradas automaticamente (barras de ativação corretas por inspeção visual em `visual-check`).

## Diagrama de fluxo de dados — sem script dedicado, reusa `montar_candidato_arquitetura_archify.py`

O tipo `dataflow` do ArchiFy exige 2-5 estágios fixos (pensado pra pipeline ETL) — não cabe na nossa modelagem de `dados.md` (entidades + evento/consulta) sem inventar uma taxonomia de estágios artificial (decisão registrada em 2026-08-16). Em vez disso, o diagrama de fluxo de dados usa o **mesmo tipo `architecture`** do Container: componentes = entidades/serviços, conexões = evento (assíncrono) ou consulta (síncrono), rótulo tirado de `dados.md` seção "Fluxo de dados entre componentes". [[agents/geracao-diagramas/AGENT]] monta esse spec (mesmo processo do catálogo/Container, mas a partir de `dados.md` em vez de `desenho.md`) e roda `montar_candidato_arquitetura_archify.py` normalmente — nenhum script novo necessário.
