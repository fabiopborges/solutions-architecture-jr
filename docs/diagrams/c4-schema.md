# Schema de diagrama C4 — autoral, agnóstico de provedor

Formato de dados que representa um diagrama C4 (nível Contexto, Container ou Componente), pensado para ser gerado por qualquer agente da cadeia (hoje: Desenho de Arquitetura, futuramente também Jornadas do Usuário) e consumido pelo pipeline de geração (`docs/diagrams/c4-gerador/`, MVP 3). O renderer padrão é `exportar_archify.py` (HTML interativo via ArchiFy vendorizado). A geração de `.drawio` foi eliminada do projeto em 2026-08-16.

Este schema é **inspirado em padrões estruturais comuns de ferramentas de diagramação C4** (separação ator/fronteira/componente/conexão; status→cor; rótulo obrigatório; síncrono/assíncrono), mas a nomenclatura, os enums e os exemplos abaixo são **integralmente autorais deste projeto** — nenhum termo, ID de projeto ou nome de empresa de qualquer referência externa aparece aqui.

## Campos

### Nível superior

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `titulo` | string | sim | Título do diagrama. Sugestão de formato: `<nome-da-demanda> — <nível>` |
| `nivel` | enum | sim | `contexto` \| `container` \| `componente` — nível C4 deste diagrama |
| `subtitulo` | string | não | Opcional — versão, data, nome da jornada se for uma visão filtrada |
| `journey_id` | string | não | Se presente, este diagrama é uma **visão filtrada** por jornada (ver seção "Filtragem por jornada" abaixo). Ausente = diagrama completo. |

### `atores[]`

Pessoas ou sistemas externos que interagem com a solução.

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `id` | string | sim | Identificador único, referenciado em `conexoes[].de`/`.para` |
| `nome` | string | sim | Nome do ator |
| `tipo` | enum | sim | `usuario_externo` \| `usuario_interno` \| `sistema_externo` |
| `papel` | string | não | Papel/contexto do ator (ex: "vendedor", "cliente final") |

### `fronteiras[]`

Agrupamentos que delimitam onde um componente roda ou a que domínio pertence (equivalente a um "boundary" C4).

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `id` | string | sim | Identificador único, referenciado em `componentes[].fronteira_id` |
| `nome` | string | sim | Nome da fronteira (ex: nome do bounded context, do sistema, da empresa) |
| `ambiente` | string | não | Texto livre e agnóstico de provedor: `"nuvem pública"`, `"on-premises"`, `"SaaS terceiro"`. **Nunca** o nome de um provedor específico (AWS/Azure/GCP/OCI) — a escolha de provedor é decisão de Infraestrutura e Deployment (ADR 001, cloud agnóstica por critério de negócio), este campo só indica a natureza do ambiente para fins de diagramação. |

### `componentes[]`

Os blocos técnicos do diagrama (nível Container ou Componente do C4).

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `id` | string | sim | Identificador único, referenciado em `conexoes[].de`/`.para` |
| `nome` | string | sim | Nome do componente |
| `status` | enum | sim | `novo` \| `alterado` \| `reuso` — ver cores em "Convenção de cores" |
| `tipo` | string | não | Texto livre (ex: "serviço", "banco de dados", "fila", "gateway") — não é um enum fechado, porque a natureza técnica de um componente varia demais entre demandas para caber numa lista fixa |
| `descricao` | string | não | Descrição curta (1 frase) |
| `fronteira_id` | string | não | ID de uma entrada de `fronteiras[]`. Se omitido, o componente fica fora de qualquer fronteira no diagrama |

### `conexoes[]`

Comunicações entre atores/componentes.

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `de` | string | sim | `id` de um ator ou componente de origem |
| `para` | string | sim | `id` de um ator ou componente de destino |
| `rotulo` | string | sim | Texto da seta. Sugestão (não obrigatória): `"<verbo> (<protocolo>)"`, ex: `"Consulta dados (REST/HTTPS)"`. Não exigimos o formato numerado+protocolo+segurança do jeito rígido de outras referências de mercado — no nosso caso, protocolo/segurança já são decididos e documentados à parte pelo agente de Segurança e Compliance; forçar isso no rótulo do diagrama duplicaria informação sem necessidade. |
| `assincrona` | boolean | não (default `false`) | `true` → linha pontilhada no diagrama. `false`/ausente → linha sólida |
| `journey_id` | string ou array de string | não | Uma ou mais jornadas às quais esta conexão pertence (ver "Filtragem por jornada"). Uma conexão pode pertencer a várias jornadas ou a nenhuma (conexão estrutural sempre visível) |

## Convenção de cores por status

Fixas no gerador (`docs/diagrams/c4-gerador/`), não configuráveis por spec, para garantir que todo diagrama gerado por este projeto seja visualmente consistente:

| Status | Cor de preenchimento | Cor de borda | Significado |
|---|---|---|---|
| `novo` | `#1168bd` (azul escuro) | `#0b4884` | Componente criado por esta demanda |
| `alterado` | `#e76f51` (laranja/terracota) | `#b5533a` | Componente existente, modificado por esta demanda |
| `reuso` | `#999999` (cinza) | `#666666` | Componente existente, usado sem alteração |

## Filtragem por jornada

Um único spec (um único conjunto de `componentes[]`/`conexoes[]`) serve tanto para o diagrama Container completo quanto para uma visão filtrada por jornada — **o gerador não recebe dois specs diferentes**, ele recebe o mesmo spec e um parâmetro opcional `--journey <journey_id>`:

- Sem o parâmetro: gera o diagrama completo, todos os componentes/conexões.
- Com o parâmetro: gera só os componentes que participam de ao menos uma conexão marcada com aquele `journey_id`, e só as conexões marcadas com aquele `journey_id`.

Isso evita duplicar modelagem — a mesma fonte de verdade gera as duas visões, sem risco de divergência entre elas (o problema que já vimos entre `desenho.md` e `documentacao-final.md` numa demanda real).

## Exemplo

Ver `docs/diagrams/exemplo-schema.json` — uma instância fictícia mínima (nível Container, 1 ator, 1 fronteira, 3 componentes com os 3 status diferentes, 3 conexões incluindo uma assíncrona e uma marcada com `journey_id`).

---

## Pipeline invertido: catálogo + sequência → Container/Contexto derivados (MVP 7)

O formato acima (`componentes[]`+`conexoes[]` juntos num só spec) continua válido e é o que o pipeline de geração sempre consumiu (hoje: `docs/diagrams/c4-gerador/exportar_archify.py`) — mas passar a construir esse spec diretamente traduzindo `desenho.md` (como o MVP 6 fez) tem um risco real: a estrutura do Container pode divergir da sequência de execução que `jornadas.md` descreve, porque as duas são autoradas de forma independente. Foi exatamente isso que aconteceu na demanda `integracao-crm-oci-whatsapp` (tensão do componente C5: `desenho.md` dizia "interno a C2", mas o ASCII e `jornadas.md` já desenhavam como componente separado).

A partir do MVP 7, a fonte de verdade primária passa a ser dividida em dois arquivos menores, e o Container/Contexto é **derivado**, nunca autorado diretamente:

### `catalogo-componentes.json` — fonte ESTÁTICA

Um catálogo por demanda (não por diagrama), com os mesmos campos de `atores[]`, `fronteiras[]` e `componentes[]` já documentados acima, **sem** `conexoes[]` — conexões só existem nas sequências.

### `sequencia-<journey_id>_spec.json` — fonte DINÂMICA, uma por jornada

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `journey_id` | string | sim | Mesmo slug usado por [[agents/jornadas-do-usuario/AGENT]] |
| `titulo` | string | sim | Nome da jornada |
| `mensagens[]` | array | sim | Lista ordenada de mensagens (ver abaixo) |

Cada mensagem em `mensagens[]`:

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `ordem` | int | sim | Posição na sequência (1, 2, 3...) |
| `de` | string | sim | `id` de ator/componente de origem (do catálogo, ou novo — ver regra `[FALTA-CATALOGO]`) |
| `para` | string | sim | `id` de ator/componente de destino |
| `rotulo` | string | sim | O que a mensagem faz |
| `protocolo` | string | não | Ex: "HTTPS", "evento", "fila" — usado para dedup entre jornadas |
| `assincrona` | boolean | não | Mesma semântica de `conexoes[].assincrona` |
| `tipo` | enum | não (default `chamada`) | `chamada` (vira seta no Container) \| `retorno` (resposta, NÃO vira seta) \| `self` (chamada interna do mesmo componente, NÃO vira seta) |

### Regras de derivação (`docs/diagrams/c4-gerador/derivar_c4.py`)

1. Mensagens com `tipo="retorno"` ou `tipo="self"` (ou `de == para`) são ignoradas na projeção para Container — são detalhe de sequência, não estrutura.
2. Deduplicação por `(de, para, protocolo)`: a primeira ocorrência (na ordem temporal) define o rótulo usado no Container; ocorrências repetidas na mesma jornada ou em jornadas diferentes não geram conexões duplicadas.
3. Renumeração: a ordem das conexões no Container segue a ordem da primeira ocorrência de cada uma, não a ordem bruta do arquivo.
4. **Container por jornada**: um spec derivado por `journey_id`, com `journey_id` marcado em cada conexão de origem (compatível com o filtro `--journey` que já existia).
5. **Container geral**: união de todas as jornadas da demanda, dedupicada pela mesma regra 2, entre jornadas.
6. **Contexto**: colapsa, dentro de cada fronteira, todo componente cujo `tipo` não seja `"Sistema"` num único nó com o nome da própria fronteira; atores e componentes de `tipo="Sistema"` são mantidos individualmente.
7. **Aviso `[ORFAO]`**: componente do catálogo que não aparece em nenhuma mensagem de nenhuma jornada da demanda — sinalizado, excluído dos specs derivados (não aparece em nenhum diagrama). Pode indicar componente que só existe na intenção do desenho, nunca chegou a ser desenhado numa jornada real.
8. **Aviso `[FALTA-CATALOGO]`**: `id` usado em `mensagens[].de`/`.para` que não existe em `catalogo-componentes.json` — sinalizado, mas **não trava a derivação**: o participante é importado com os atributos disponíveis na própria sequência (nome inferido do `id`, status `desconhecido`). Isso é o mecanismo que teria pego a tensão do componente C5 automaticamente, na hora de gerar, em vez de precisar de um agente comparando documentos manualmente.

Nenhuma dessas duas listas de aviso é opcional de exibir — sempre aparecem no relatório de derivação, mesmo vazias (relatório explícito de "nenhum aviso" é diferente de relatório omitido).
