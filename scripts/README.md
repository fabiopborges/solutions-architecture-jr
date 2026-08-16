# Gerador de diagramas C4

Dois scripts. `derivar_c4.py` (MVP 7) monta um spec de Container/Contexto automaticamente a partir de um catálogo estático + sequências por jornada, em vez de alguém traduzir `desenho.md` à mão — ver `../c4-schema.md`, seção "Pipeline invertido", para o porquê. `exportar_archify.py` traduz esse spec para o formato `architecture.schema.json` do ArchiFy (vendorizado em `skills/vendors/archify/`) e chama o CLI dele para renderizar HTML interativo autocontido — é o renderer padrão do pipeline.

> **Geração de `.drawio` eliminada do projeto em 2026-08-16.** O script `gerar_c4.py` e as POCs que o antecederam (`../poc-drawpyo/`, `../poc-c4/`) foram removidos — decisão de não manter essa capacidade, não de adiá-la. Um agente dedicado de drawio, de responsabilidade única, pode vir a existir no futuro como peça isolada, mas não faz parte deste pipeline.

## Regra de padronização: 12 palavras por texto visível (2026-08-16)
Todo texto que aparece renderizado — `nome` de componente/ator/fronteira, `descricao` de componente, `papel` de ator (**estes dois viram `sublabel`, renderizado dentro da caixa** — não são metadado interno, esquecer eles foi o bug real da primeira versão desta regra), `rotulo` de conexão/mensagem — tem no máximo **12 palavras**. `exportar_archify.py` e `exportar_sequencia_archify.py` checam isso automaticamente (`checar_limite_palavras`/`checar_limite_palavras_sequencia`) antes de chamar o ArchiFy e recusam renderizar (`sys.exit(1)`, mensagem `[erro]` listando cada violação) se algum campo passar do limite — não truncam sozinhos. Escreva curto desde a autoria do catálogo/spec; detalhe completo vai em `NOTAS.md` ou na documentação de origem, nunca dentro do rótulo renderizado.

## Uso — `derivar_c4.py` (catálogo + sequências → specs de Container/Contexto)

```bash
python3 derivar_c4.py CATALOGO.json SEQUENCIA1.json [SEQUENCIA2.json ...] --saida-dir DIR [--titulo-base "Nome da demanda"]
```

- `CATALOGO.json`: catálogo estático (`atores[]`/`fronteiras[]`/`componentes[]`, sem `conexoes[]`) — normalmente produzido por [[agents/geracao-diagramas/AGENT]] a partir de `desenho.md`.
- `SEQUENCIA*.json`: um ou mais `sequencia-<journey_id>_spec.json`, produzidos por [[agents/jornadas-do-usuario/AGENT]].
- `--saida-dir DIR`: grava `c4-container-jornada-<id>.json` (um por sequência), `c4-container.json` (união de todas), e `c4-contexto.json` (Container colapsado por fronteira).
- Imprime um **relatório de derivação** no stdout: `[ORFAO]` (componente do catálogo nunca usado em nenhuma jornada, excluído dos diagramas) e `[FALTA-CATALOGO]` (participante de sequência ausente do catálogo, importado com atributos mínimos, status `desconhecido` → fallback). Esses avisos não são cosméticos — nunca devem ser silenciados, ver `c4-schema.md`.
- Se não existir nenhum `sequencia-<journey_id>_spec.json` (veredito de `jornadas.md` foi "nenhuma jornada aplicável" — o arquivo sempre existe, só o spec de sequência é que é condicional), pule este script — traduza `desenho.md` direto para `conexoes[]` de um spec de Container único (ver `skills/geracao-diagramas/SKILL.md`, passo 4).

## Uso — `exportar_archify.py` (spec → HTML interativo)

```bash
python3 exportar_archify.py ENTRADA.json SAIDA.html [--journey JOURNEY_ID] [--archify-bin CAMINHO/bin/archify.mjs] [--orientacao {vertical,horizontal}] [--max-tentativas N]
```

- `ENTRADA.json`: spec de Container/Contexto, no formato de `../c4-schema.md` (produzido por `derivar_c4.py`, ou traduzido direto de `desenho.md` quando não há jornada).
- `SAIDA.html`: HTML autocontido, interativo, tema claro/escuro. O `.architecture.json` intermediário é gravado ao lado, mesmo nome, para rastreabilidade.
- `--archify-bin`: opcional — sem informar, usa o binário vendorizado em `skills/vendors/archify/archify/bin/archify.mjs` automaticamente.
- O script calcula a geometria (camadas, ordenação por barycenter, faixas de rota, viewBox) inteiramente em Python — isso é nosso, determinístico, sem IA envolvida. O ArchiFy só recebe o resultado já posicionado, valida contra as próprias regras de qualidade visual (`showcase`) e renderiza o HTML final. O script já roda o loop de validação/reparo sozinho até convergir (ou até `--max-tentativas`), sem ajuste manual.
- Cada spec gerado por `derivar_c4.py` já está no formato que este script consome — rodar os dois em sequência é o fluxo normal.

## Dependências

- Python 3 (stdlib apenas, sem pacote externo) para `derivar_c4.py`.
- Node.js (`node --version`, qualquer ≥18) + o ArchiFy vendorizado em `skills/vendors/archify/archify/` para `exportar_archify.py`. Sem instalação adicional — `node skills/vendors/archify/archify/bin/archify.mjs doctor` confirma que está pronto.

## Testes — `derivar_c4.py` (MVP 7)

- `teste-3-catalogo.json` + `teste-3-sequencia-jornada-x.json` — caso sintético desenhado de propósito pra disparar os dois avisos: um componente do catálogo nunca referenciado (`[ORFAO]`) e um participante de sequência fora do catálogo (`[FALTA-CATALOGO]`), mais uma mensagem `self` e duas `retorno` pra confirmar que são filtradas da projeção.
- Caso real: `demandas/<nome-da-demanda>/diagramas/catalogo-componentes.json` + `sequencia-*_spec.json` da demanda `integracao-crm-oci-whatsapp` — usado pra validar que `[FALTA-CATALOGO]` pega sozinho uma tensão real entre `desenho.md` (que descrevia um componente como "interno a outro") e `jornadas.md` (que o tratava como participante à parte), sem precisar de um agente comparando os dois documentos manualmente.

## Testes — `exportar_archify.py`

Validado contra specs reais de `integracao-crm-oci-whatsapp` (Container geral, Contexto, e as duas visões filtradas por jornada — 4 de 4 convergindo em `showcase` 9/9) e testado de novo depois da promoção a pipeline padrão (2026-08-16), contra o Contexto de `plataforma-ia-corporativa-v1` (convergiu em 5 rodadas). Notas da POC original que validou essa abordagem foram descartadas após a promoção a padrão (2026-08-16).

## Uso — `exportar_sequencia_archify.py` (spec de sequência → HTML interativo)

```bash
python3 exportar_sequencia_archify.py SEQUENCIA_SPEC.json CATALOGO.json SAIDA.html [--archify-bin CAMINHO/bin/archify.mjs] [--max-tentativas N]
```

- `SEQUENCIA_SPEC.json`: `sequencia-<journey_id>_spec.json` produzido por [[agents/jornadas-do-usuario/AGENT]] (`mensagens[]` com `ordem`/`de`/`para`/`rotulo`/`protocolo`/`assincrona`/`tipo`).
- `CATALOGO.json`: `catalogo-componentes.json` da mesma demanda — usado só pra resolver nome/tipo de cada participante, nunca pra decidir estrutura.
- Renderer padrão pra diagrama de sequência desde 2026-08-16, substituindo o Mermaid manual (`docs/diagrams/04-sequencia.mmd` fica só como registro histórico do padrão anterior, não é mais gerado).
- `ordem` vira posição Y determinística (passo fixo de 70px). Nomes do catálogo no formato `"C1 — Descrição"` são separados em `label` curto + `sublabel` completo (o renderer de sequência do ArchiFy tem um teto de 190px pro `label`, sem encolhimento de fonte — só o `sublabel` encolhe). Mensagens `tipo: "self"` (de==para) não têm primitiva no ArchiFy — viram `note` anexada à mensagem real mais próxima do mesmo participante; o script imprime `[SELF-COMO-NOTA]` no stderr pra cada uma, nunca descarta silenciosamente.
- Testado contra a jornada `lead-notificado` de `integracao-crm-oci-whatsapp` (9 mensagens, 1 self, 7 participantes) — convergiu em `showcase` 9/9.

## Diagrama de fluxo de dados — sem script dedicado, reusa `exportar_archify.py`

O tipo `dataflow` do ArchiFy exige 2-5 estágios fixos (pensado pra pipeline ETL) — não cabe na nossa modelagem de `dados.md` (entidades + evento/consulta) sem inventar uma taxonomia de estágios artificial (decisão registrada em 2026-08-16). Em vez disso, o diagrama de fluxo de dados usa o **mesmo tipo `architecture`** do Container: componentes = entidades/serviços, conexões = evento (assíncrono) ou consulta (síncrono), rótulo tirado de `dados.md` seção "Fluxo de dados entre componentes". [[agents/geracao-diagramas/AGENT]] monta esse spec (mesmo processo do catálogo/Container, mas a partir de `dados.md` em vez de `desenho.md`) e roda `exportar_archify.py` normalmente — nenhum script novo necessário.
