> **POC concluída em 2026-08-16 — ArchiFy promovido a renderer padrão do pipeline.**
> `exportar_archify.py` mudou de lugar: agora vive em `docs/diagrams/c4-gerador/exportar_archify.py`, junto com `gerar_c4.py`/`derivar_c4.py`, e `skills/geracao-diagramas/SKILL.md` já chama esse script no passo 8. O ArchiFy foi vendorizado em `skills/vendors/archify/` (código-fonte completo, usado só como dependência interna via `node .../bin/archify.mjs validate|deliver` — o `SKILL.md` próprio do ArchiFy não é usado como skill selecionável neste projeto). A saída deixou de usar a subpasta `diagramas/archify/` (isso era só a estrutura de laboratório desta POC) — agora `.html`/`.architecture.json` ficam direto em `demandas/<nome-da-demanda>/diagramas/`. Este documento fica como registro histórico de como o layout foi validado; não é mais a referência operacional.

# POC: ArchiFy como renderer alternativo ao `.drawio`

## O que essa POC prova

`exportar_archify.py` traduz um spec no formato de `docs/diagrams/c4-schema.md`
(o mesmo que `gerar_c4.py` consome) para `architecture.schema.json` do
[ArchiFy](https://github.com/tt-a1i/archify) e chama o CLI dele
(`archify.mjs validate` → repara mecanicamente a partir dos diagnósticos →
`archify.mjs deliver`) pra produzir HTML autocontido, interativo, com tema
claro/escuro.

Não substitui `gerar_c4.py`/`derivar_c4.py` — a fonte de verdade (`desenho.md`
→ catálogo → jornadas → spec C4 derivado) continua sendo a mesma. Só a última
etapa (spec → imagem) é trocada.

## O que foi testado

**v1 (coluna = fronteira, herdado de `gerar_c4.py`):**

| Entrada | Resultado |
|---|---|
| `exemplo-schema.json` (linear) | ✅ `showcase` 9/9 |
| `integracao-crm-oci-whatsapp` — Container geral | ❌ não convergia — whack-a-mole entre rodadas |
| `integracao-crm-oci-whatsapp` — Contexto | ❌ idem |
| `portal-cracha-visitante-v1` — Container geral | ❌ idem, mais denso |

**v2 (coluna = camada topológica, este documento):** ver `analisar_grafo` /
`ordenar_linhas_por_barycenter` / `empacotar_faixas` em `exportar_archify.py`.
Em vez de coluna = fronteira, a coluna de cada nó agora é sua **profundidade
no grafo** (longest-path a partir das fontes, tipo Kahn), calculada só com as
conexões "de ida" — as que fecham ciclo (retentativa, retorno de resultado)
são achadas por DFS clássica (cor branco/cinza/preto) e tratadas à parte:
roteadas por uma faixa dedicada embaixo do diagrama, empacotada por
intervalo-X (tipo Gantt) pra não precisar uma faixa por conexão. A ordem das
linhas dentro de cada camada usa duas passadas de barycenter (heurística de
Sugiyama) pra reduzir cruzamento entre camadas vizinhas.

| Entrada | Resultado |
|---|---|
| `exemplo-schema.json` (linear) | ✅ `showcase` 9/9 |
| `integracao-crm-oci-whatsapp` — Container geral (4 atores, 6 componentes, 12 conexões, com retentativa+retorno) | ✅ `showcase` 9/9 (convergiu em 6 rodadas de auto-reparo) |
| `integracao-crm-oci-whatsapp` — Contexto | ✅ `showcase` 9/9 (convergiu em 3 rodadas) |
| `portal-cracha-visitante-v1` — Container geral (6 atores, 5 componentes, 13 conexões) | ❌ 2 diagnósticos restantes (era 18 na v1, 14 antes da 2ª rodada de fix, ver abaixo) |

Os dois diagramas reais que passaram foram publicados como Artifact na
conversa que gerou esta POC — Container e Contexto da demanda
`integracao-crm-oci-whatsapp`, layout 100% automático, sem nenhum ajuste
manual no `.architecture.json`.

## Segunda rodada de fix — causa raiz única (18 → 4 diagnósticos)

As duas classes de diagnóstico da primeira versão ("componentes a menos de
8px" e "aresta atravessando componente do meio") eram, na prática, **o mesmo
bug**: `aplicar_reparo` alargava um componente (por sublabel/rótulo estreito)
sem recalcular o X das colunas seguintes — a largura de uma coluna é o maior
componente dela, então alargar um componente empurra toda coluna depois dele,
e o reparo anterior só realinhava o `via` do próprio componente redimensionado,
não a cascata inteira. `recolocar()` (novo, chamado a cada resize dentro do
reparo) refaz o X de **todos** os componentes e **todos** os `via` a partir da
grade atual — eliminou as duas classes de uma vez: 18 → 4.

## Terceira rodada — aninhamento em `empacotar_faixas` (4 → 2)

`empacotar_faixas` empacotava por ordem de início em X (`x_min` crescente),
que é o algoritmo certo pra *minimizar o número de faixas*, mas errado pra
*evitar cruzamento*: quando um intervalo A **contém** outro B já alocado numa
faixa rasa, A precisa ficar **mais fundo** que B (senão a vertical de B cruza
a horizontal de A, ou vice-versa) — e isso só é garantido processando do
intervalo mais estreito pro mais largo, não por ordem de início. Trocar o
critério de ordenação (`t[2]-t[1]`, largura, em vez de `t[1]`, início) corrigiu
o caso aninhado sem tocar no resto do algoritmo: 4 → 2.

## O que sobra: um par que cruza de verdade (não é mais bug)

Os 2 diagnósticos finais são um único par de conexões cujos intervalos em X
se **cruzam de fato** — nem aninhado (nenhum contém o outro), nem disjunto
(compartilham um trecho de X): `A=[2234,3771]` e `B=[1490,3270]`. Matematicamente, **qualquer** profundidade de faixa escolhida pra
A e B faz uma cruzar a horizontal da outra — é uma propriedade do modelo de
rota "desce reto, atravessa, sobe reto" (2 pontos de `via`), não mais um erro
de posicionamento. A única forma de eliminar isso de vez é dar uma rota com
mais dobras pra uma das duas (contornar o retângulo da outra com 4-6 pontos
de `via` em vez de 2) — é uma extensão de **roteamento**, não de layout;
ficou fora do escopo desta rodada.

## Orientação do fluxo — `--orientacao {vertical,horizontal}` (default vertical)

Pedido do usuário: o layout horizontal (colunas indo pra direita) ficava
esparramado demais pra diagramas com muitas camadas. `calcular_posicoes` agora
suporta as duas orientações a partir da MESMA grade lógica (camada, posição-
-na-camada) que `analisar_grafo`/`ordenar_linhas_por_barycenter` produzem —
só muda qual eixo de pixel cada uma vira:

- **Horizontal**: camada → coluna (x); dentro da camada, todo componente usa
  a largura da coluna inteira (a do maior membro) — simples porque a altura é
  sempre fixa (64px).
- **Vertical**: camada → linha (y, sempre com o mesmo passo, já que a altura
  nunca varia); dentro da linha, cada componente usa a PRÓPRIA largura (não a
  máxima da linha) e o conjunto é centralizado em relação à linha mais larga
  — isso também resolve o "melhor distribuído" pedido junto: nenhuma linha
  fica forçada a ocupar o espaço do componente mais largo do diagrama inteiro.

Isso não foi um simples "transpor X e Y": a caixa do componente continua
sempre paisagem (largura conforme o texto, altura fixa) nas duas orientações
— só a REGRA DE POSICIONAMENTO delas muda. Coisas orientation-aware que
precisaram ser refeitas (não só a posição):

- **Lado de entrada/saída das conexões diretas**: `right`/`left` no
  horizontal vira `bottom`/`top` no vertical (fluxo de cima pra baixo).
- **Faixa de rota por fora** (conexão de volta/pula-camada): fica embaixo de
  tudo (`bottom`/`bottom`, offset em Y) no horizontal; fica à direita de tudo
  (`right`/`right`, offset em X) no vertical.
- **Passo entre faixas vizinhas**: 30px bastava no horizontal (rótulo é baixo,
  ~14px, empilha em Y); no vertical o rótulo continua LARGO (até ~280px) e as
  faixas empilham em X — precisou de um passo de 220px, senão rótulos de
  faixas vizinhas se sobrepõem mesmo com as linhas bem separadas.
- **`labelDy` continua sendo o eixo certo pra escapar de sobreposição nas
  duas orientações** (testado, não é intuitivo): os componentes são sempre
  bem mais largos que altos, então mesmo numa conexão vertical, deslocar o
  rótulo em Y escapa da caixa com um deslocamento bem menor que em X.
- **`recolocar()` (recalcula tudo após um resize no reparo) precisou realinhar
  a faixa inteira, não só os `via` individuais**: no vertical, alargar um
  componente desloca X — inclusive a faixa "por fora", que tinha sido
  calculada uma vez só, antes de qualquer reparo. Sem realinhar o bloco de
  faixas inteiro, ela deixava de estar de fato fora de tudo depois de
  algumas rodadas de widening. Isso não existia no horizontal porque lá um
  resize nunca move Y (a faixa mora em Y).

**Resultado, `--orientacao vertical` (default):**

| Entrada | Resultado |
|---|---|
| `exemplo-schema.json` | ✅ `showcase` 9/9 |
| `integracao-crm-oci-whatsapp` — Container geral | ✅ `showcase` 9/9 |
| `integracao-crm-oci-whatsapp` — Contexto | ✅ `showcase` 9/9 |
| `portal-cracha-visitante-v1` — Container geral | ❌ 4 diagnósticos restantes (2 são o mesmo par que cruza de verdade, ver seção acima; 2 são rótulo colado numa caixa de 888px que não escapou com os deslocamentos testados) |

Os três diagramas que passam foram republicados como Artifact (mesmas URLs
da rodada anterior) já na orientação vertical.

## Caso de uso completo — `integracao-crm-oci-whatsapp` (todos os 4 diagramas)

Rodei o adaptador nos 4 specs derivados que essa demanda já tinha prontos em
`demandas/integracao-crm-oci-whatsapp/diagramas/derivado/` — o pacote
completo que `documentacao-final` esperaria (Container geral, Contexto, e as
duas visões filtradas por jornada). **Os 4 passaram `showcase` 9/9**, salvos
em `demandas/integracao-crm-oci-whatsapp/diagramas/archify/*.html`.

A visão `jornada-lead-notificado` expôs um bug que as visões maiores
não tinham exposto: uma conexão de volta saindo de um componente que **não**
era o mais à direita da própria camada cruzava um vizinho de camada no
caminho até a faixa lateral — a faixa vertical (ver seção de orientação
acima) saía do componente direto pro lado (`right`/`right`), e se outro
componente da mesma camada estivesse no meio do caminho até a faixa, a rota
passava por cima dele.

**Fix: `montar_via_vertical`** — a faixa vertical agora sai/entra sempre por
**baixo/cima da própria linha do componente** (não pro lado, na mesma altura)
antes de virar em direção à faixa: sai por baixo da origem, vai até a faixa,
desce/sobe até a altura de chegada, entra por cima do destino. Isso nunca
cruza um vizinho de camada, porque o desvio inicial já tira a rota da faixa
de altura onde os vizinhos estão. Precisou de metadado privado (`_faixa` em
cada conexão, removido antes de gravar — `serializar_para_archify`) porque a
rota de 4 pontos não dá pra só "ajustar ponta" no `recolocar()`, tem que
reconstruir a partir da faixa original.

Rodado de novo depois do fix: os 3 casos que já passavam continuam passando
(nenhuma regressão), mais o que faltava — **4 de 4** nessa demanda.

## Pontos de contato livres — usar lado direito quando não cruza ninguém

Pedido do usuário: as setas de faixa (rota "por fora") sempre saíam/entravam
por baixo/cima da própria linha (ver seção do bug da jornada
`lead-notificado`, acima), mesmo quando o lado direito do componente estava
completamente livre — desperdiçando espaço óbvio e, pior, quando um
componente tinha mais de uma conexão de faixa, todas saíam do MESMO ponto
central (a mesma coordenada X sempre), literalmente sobrepostas na origem.

**`lado_direito_livre`**: checa, pra um componente, se existe algum outro na
MESMA linha (mesma faixa de altura) posicionado à direita dele — se não
existe, o lado direito está livre e a conexão pode sair/entrar direto por
ali, sem desviar.

**`escolher_lado_e_pontos_lane`**: decide o lado de cada ponta de cada
conexão de faixa. Só a PRIMEIRA conexão que disputa o lado direito de um
componente fica com ele (contato sempre no centro da altura — testado que um
`via` terminando fora do centro nesse lado faz o ArchiFy inserir uma correção
diagonal de última hora e reprovar `clean-flow/endpoint-side-direction`, não
dá pra espalhar múltiplos pontos livremente ali); as demais caem pro desvio
de baixo/cima de sempre, que aí sim aceita vários pontos — espalhados ao
longo da LARGURA do componente (não mais sempre no centro), evitando duas
setas na mesma coordenada mesmo quando várias precisam do desvio.

Resultado real (`c4-container.json`, CRM×WhatsApp): das 3 conexões de faixa,
uma ficou 100% livre dos dois lados (`right`/`right`, sem nenhum desvio); as
outras duas saem livres pela direita mas entram por cima (o lado direito do
alvo já tinha sido tomado pela primeira) — nenhuma sobreposta, nenhuma presa
num desvio desnecessário. Os 4 diagramas da demanda continuam passando
`showcase` 9/9 depois dessa mudança (retestado, zero regressão).

## Bug: seta saindo da área visível do diagrama (`meta.viewBox`)

Reportado pelo usuário na jornada `alerta-falha-permanente`: a seta/rótulo de
"Grava Notificação (estado inicial)" passava por fora da área de trabalho do
diagrama. Causa raiz, conferida direto no renderer do ArchiFy
(`renderers/architecture/render-architecture.mjs`, função `autoViewBox`):
quando `meta.viewBox` não é informado no spec, o cálculo automático mede
**só** `components` e `boundaries` — nunca os pontos de `via` das conexões.
A faixa de rota "por fora" (ver `montar_via_vertical`/`montar_conexoes_archify`
— usada pra conexão de volta ou que pula camada) é desenhada DE PROPÓSITO além
da extensão de qualquer componente, exatamente pra nunca cruzar ninguém — e
era isso que ficava cortado fora do SVG.

**Fix, em `calcular_viewbox`** (chamado por `serializar_para_archify`, que
roda antes de CADA gravação — inicial e a cada rodada de reparo, nunca só uma
vez): mede o maior X/Y entre `components` **e** todo ponto de `via` de toda
conexão, e fixa `meta.viewBox` explicitamente com essa medida + margem. Isso
é estrutural, não um ajuste pontual num spec — todo spec que passa por
`exportar_archify.py` a partir de agora tem `meta.viewBox` calculado assim,
então nenhum desenho futuro (deste adaptador) pode voltar a cortar uma faixa
de rota fora da área visível.

## Caminhos pra evoluir isso ainda mais

1. **Roteamento com contorno** pra pares que cruzam de verdade — detectar o
   par (já sei identificá-lo: intervalo parcialmente sobreposto sem conter
   nem ser disjunto) e dar 4-6 pontos de `via` pra uma das duas em vez de 2,
   contornando o retângulo da outra.
2. **Testar em visões filtradas por jornada** (`--journey`) — cada visão tem
   só as conexões daquela jornada, grafo bem menor, tende a não ter par
   cruzado nenhum.
3. **Aceitar `--quality standard`** como fallback pontual pra diagramas que
   não convergirem em `showcase`, em vez de bloquear a entrega.
4. **Aceitar ajuste manual pontual** no `.architecture.json` antes do
   `deliver` — mesmo espírito de "`.drawio` sempre editável à mão depois"
   que já vale hoje.

## Limitações conhecidas do mapeamento (não é só geometria)

- **Status (`novo`/`alterado`/`reuso`/`desconhecido`) vira `tag` (badge de
  texto), não cor** — ArchiFy usa cor pra categoria fixa (`type`), não pra
  status. Ver conversa que motivou esta POC.
- **`tipo` livre → categoria fixa do ArchiFy é heurística por palavra-chave**
  (`classificar_tipo`), lossy por natureza — precisa de revisão humana em tipos
  ambíguos, principalmente os que caem no fallback `backend`.

## Dependência (ainda não vendorizada)

Esta POC assume o ArchiFy clonado fora do repo (`--archify-bin` aponta pro
`bin/archify.mjs` de um checkout local). Decidir onde ele mora de verdade
(vendorizado em `docs/diagrams/`, npm dependency, etc.) é decisão de
arquitetura pro pipeline — não foi tomada aqui.
