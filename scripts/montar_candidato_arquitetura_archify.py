#!/usr/bin/env python3
"""Traduz um spec C4 (formato de docs/diagrams/c4-schema.md) para um
CANDIDATO MÍNIMO no formato architecture.schema.json do ArchiFy (vendorizado
em skills/vendors/archify/archify/, github.com/tt-a1i/archify).

Este script NÃO chama o ArchiFy e NÃO calcula geometria em pixel. Ele monta
só o que é decisão de domínio: quais componentes/conexões existem
(derivar_c4.py), a categoria de cada componente (classificar_tipo), a ordem
de leitura (camada/linha, via analisar_grafo + ordenar_linhas_por_barycenter)
traduzida para `row`/`col` do `layout: {mode: "grid"}` NATIVO do ArchiFy, e o
gate de 12 palavras por rótulo. Posição em pixel, roteamento de conexão
(`via`/`fromSide`/`toSide`) e `viewBox` ficam por conta do layout automático
e do Automatic Port Spread do próprio ArchiFy — ver
skills/vendors/archify/archify/references/authoring-contract.md, "Grid
placement is preferred when the schema supports it."

Quem chama `archify.mjs validate`/`deliver` sobre o candidato gerado aqui é
o agente `geracao-diagramas`, via Bash, seguindo o loop de reparo pontual
descrito em references/authoring-contract.md e references/delivery-contract.md
— nunca este script (substitui exportar_archify.py, que reimplementava esse
loop e a geometria completa em Python; decisão registrada 2026-08-16).

Uso:
    python3 montar_candidato_arquitetura_archify.py ENTRADA.json SAIDA.architecture.json
        [--journey JOURNEY_ID] [--orientacao {vertical,horizontal}]
"""
import argparse
import json
import sys
from pathlib import Path

RAIZ_REPO = Path(__file__).resolve().parents[1]


def carregar_spec(caminho):
    return json.loads(Path(caminho).read_text(encoding="utf-8"))


def filtrar_por_jornada(spec, journey_id):
    """Contrato documentado em docs/diagrams/c4-schema.md, seção "Filtragem
    por jornada": mantém só conexões marcadas com `journey_id` (campo string
    ou lista), só componentes/atores que participam de ao menos uma conexão
    mantida, e só fronteiras ainda referenciadas por algum componente
    mantido."""
    def pertence(conexao):
        marcado = conexao.get("journey_id")
        if marcado is None:
            return False
        if isinstance(marcado, list):
            return journey_id in marcado
        return marcado == journey_id

    conexoes = [c for c in spec.get("conexoes", []) if pertence(c)]
    ids_participantes = {c["de"] for c in conexoes} | {c["para"] for c in conexoes}

    componentes = [c for c in spec.get("componentes", []) if c["id"] in ids_participantes]
    atores = [a for a in spec.get("atores", []) if a["id"] in ids_participantes]

    ids_fronteira = {c["fronteira_id"] for c in componentes if c.get("fronteira_id")}
    fronteiras = [f for f in spec.get("fronteiras", []) if f["id"] in ids_fronteira]

    filtrado = dict(spec)
    filtrado["componentes"] = componentes
    filtrado["atores"] = atores
    filtrado["fronteiras"] = fronteiras
    filtrado["conexoes"] = conexoes
    return filtrado

LIMITE_PALAVRAS_ROTULO = 12


def contar_palavras(texto):
    return len((texto or "").split())


def checar_limite_palavras(spec):
    """Regra de padronização entre todos os diagramas (2026-08-16): todo texto
    que aparece na figura — nome E sublabel/descrição (`descricao` de
    componente, `papel` de ator, que o renderer usa como `sublabel`
    visível dentro da caixa) — e todo rótulo de seta (conexão), tem no
    máximo LIMITE_PALAVRAS_ROTULO palavras. Não trunca sozinho — quem autora
    o spec decide como encurtar sem perder o sentido. Retorna a lista de
    violações (vazia = ok)."""
    violacoes = []
    for chave, campos, rotulo_tipo in (
        ("componentes", ("nome", "descricao"), "componente"),
        ("atores", ("nome", "papel"), "ator"),
        ("conexoes", ("rotulo",), "conexão"),
    ):
        for item in spec.get(chave, []) or []:
            for campo in campos:
                texto = item.get(campo)
                n = contar_palavras(texto)
                if n > LIMITE_PALAVRAS_ROTULO:
                    violacoes.append(f"[{rotulo_tipo}.{campo}] '{item.get('id', item.get('de', '?'))}' ({n} palavras, limite {LIMITE_PALAVRAS_ROTULO}): \"{texto}\"")
    return violacoes


TAGS_STATUS = {
    "novo": "NOVO",
    "alterado": "ALTERADO",
    "reuso": "REUSO",
    "desconhecido": "DESCONHECIDO",
}

# Heurística lossy: nosso `tipo` é texto livre; ArchiFy exige uma das 7
# categorias fixas abaixo (é isso que define a cor no renderer dele).
# Palavras-chave em PT/EN, checadas em ordem — a primeira que bater vence.
PALAVRAS_POR_CATEGORIA = [
    ("database", ["banco de dados", "banco", "dados", "database", "repositório", "repositorio", "store"]),
    ("messagebus", ["fila", "mensageria", "message", "evento", "broker", "topic", "queue"]),
    ("security", ["segurança", "seguranca", "security", "auth", "iam", "waf"]),
    ("cloud", ["cloud", "nuvem", "provedor", "saas"]),
    ("frontend", ["frontend", "interface", "portal", "spa", "web app", "app móvel", "app movel"]),
]


def classificar_tipo(comp):
    """Deriva a categoria fixa do ArchiFy a partir do `tipo` livre do nosso schema."""
    if comp.get("status") == "desconhecido" or comp.get("tipo") == "não catalogado":
        return "external"  # componente-caixa-preta: [FALTA-CATALOGO] ou colapso de Contexto
    if comp.get("tipo") == "Sistema":
        return "external"  # nó colapsado de Contexto (derivar_c4.py, regra 6)
    texto = (comp.get("tipo") or "").lower()
    for categoria, palavras in PALAVRAS_POR_CATEGORIA:
        if any(p in texto for p in palavras):
            return categoria
    return "backend"  # default: serviço/adapter/ACL — a maioria dos nossos componentes


def analisar_grafo(spec):
    """Layout topológico de verdade em vez de coluna=fronteira: acha as
    conexões que fecham ciclo (DFS clássica, cor branco/cinza/preto) e usa só
    as conexões restantes (garantidamente um DAG) pra computar a camada de
    cada nó via longest-path (Kahn). Camada = "distância" no fluxo (vira
    row no layout vertical, col no horizontal — ver row_col_por_orientacao).
    Isso separa conexão "de ida" (adjacente ou pulando camada) de conexão "de
    volta" (retentativa, retorno de resultado) de forma estrutural, não
    geométrica. Decisão de domínio (ordem de leitura), não geometria de
    pixel — por isso continua em Python (ver ordenar_linhas_por_barycenter
    logo abaixo)."""
    nos = [a["id"] for a in spec.get("atores", [])] + [c["id"] for c in spec.get("componentes", [])]
    nos_set = set(nos)
    adj = {n: [] for n in nos}
    for con in spec.get("conexoes", []):
        de, para = con["de"], con["para"]
        if de in nos_set and para in nos_set and de != para:
            adj[de].append(para)

    COR_BRANCO, COR_CINZA, COR_PRETO = 0, 1, 2
    cor = {n: COR_BRANCO for n in nos}
    back_edges = set()

    def dfs(u):
        cor[u] = COR_CINZA
        for v in adj[u]:
            if cor[v] == COR_BRANCO:
                dfs(v)
            elif cor[v] == COR_CINZA:
                back_edges.add((u, v))
        cor[u] = COR_PRETO

    for n in nos:
        if cor[n] == COR_BRANCO:
            dfs(n)

    adj_dag = {n: [] for n in nos}
    grau_entrada = {n: 0 for n in nos}
    for u in nos:
        for v in adj[u]:
            if (u, v) in back_edges:
                continue
            adj_dag[u].append(v)
            grau_entrada[v] += 1

    camada = {n: 0 for n in nos}
    fila = [n for n in nos if grau_entrada[n] == 0]
    grau_restante = dict(grau_entrada)
    i = 0
    while i < len(fila):
        u = fila[i]
        for v in adj_dag[u]:
            camada[v] = max(camada[v], camada[u] + 1)
            grau_restante[v] -= 1
            if grau_restante[v] == 0:
                fila.append(v)
        i += 1

    return camada, back_edges


def ordenar_linhas_por_barycenter(spec, camada, back_edges, ordem_original):
    """Reduz cruzamento entre camadas adjacentes: ordena cada camada pela
    posição média dos vizinhos na camada anterior/seguinte (heurística clássica
    de Sugiyama), usando só conexões de ida (as de volta não contam pra ordem).
    Retorna id -> posição dentro da camada (0, 1, 2...) — decisão de ordem de
    leitura, não geometria de pixel."""
    por_camada = {}
    for id_ in ordem_original:
        por_camada.setdefault(camada[id_], []).append(id_)

    conexoes_ida = [
        (c["de"], c["para"]) for c in spec.get("conexoes", [])
        if (c["de"], c["para"]) not in back_edges and c["de"] in camada and c["para"] in camada
    ]

    def posicoes_atuais():
        pos = {}
        for ids in por_camada.values():
            for row, id_ in enumerate(ids):
                pos[id_] = row
        return pos

    for _ in range(2):
        pos = posicoes_atuais()
        for c in sorted(por_camada):
            if c == 0:
                continue
            vizinhos = {}
            for de, para in conexoes_ida:
                if camada[para] == c and camada[de] == c - 1:
                    vizinhos.setdefault(para, []).append(pos[de])
            por_camada[c].sort(key=lambda id_: sum(vizinhos[id_]) / len(vizinhos[id_]) if id_ in vizinhos else pos[id_])
            pos = posicoes_atuais()

        pos = posicoes_atuais()
        for c in sorted(por_camada, reverse=True):
            maior = max(por_camada)
            if c == maior:
                continue
            vizinhos = {}
            for de, para in conexoes_ida:
                if camada[de] == c and camada[para] == c + 1:
                    vizinhos.setdefault(de, []).append(pos[para])
            por_camada[c].sort(key=lambda id_: sum(vizinhos[id_]) / len(vizinhos[id_]) if id_ in vizinhos else pos[id_])
            pos = posicoes_atuais()

    linhas = {}
    for ids in por_camada.values():
        for row, id_ in enumerate(ids):
            linhas[id_] = row
    return linhas


# Defaults de partida para o layout grid nativo — não recalculados
# dinamicamente por posição/rota (isso cabe ao `validate`/reparo pontual, não
# a este script). CELL_W acompanha o teto de `largura_estimada` (280) pra
# evitar overlap entre colunas logo na primeira rodada.
ALTURA_COMPONENTE = 64
GAP_X, GAP_Y = 60, 40
CELL_W, CELL_H = 280, ALTURA_COMPONENTE


def largura_estimada(*textos, minimo=150, maximo=280):
    """Tamanho de caixa por conteúdo — autoria normal (como escolher a
    largura de um label), não geometria de posição/rota. O default fixo do
    ArchiFy (120x60, ver render-architecture.mjs) não conhece o texto; sem
    isto, praticamente todo componente com sublabel descritivo falha
    `validate` só por caixa pequena demais — não é o tipo de reparo que o
    authoring-contract.md pede pra deixar pro diagnóstico (esse é sobre
    via/channelX/channelY/labelAt, controles de rota, não sobre dimensionar
    a caixa pelo próprio conteúdo)."""
    maior = max((len(t) for t in textos if t), default=0)
    return max(minimo, min(maximo, 24 + maior * 7))


def montar_componentes_archify(spec, orientacao):
    """Camada topológica (analisar_grafo) em vez de fronteira — fronteira
    agora só agrupa visualmente (boundary) e define tag/tipo, quem manda na
    ordem de leitura é a estrutura do grafo de conexões. Emite `row`/`col`
    para o `layout: {mode:"grid"}` nativo do ArchiFy — nunca `pos`/`via` em
    pixel (isso é o próprio layout automático/roteador que calcula)."""
    camada, back_edges = analisar_grafo(spec)

    atores = spec.get("atores", [])
    componentes = spec.get("componentes", [])
    ordem_original = [a["id"] for a in atores] + [c["id"] for c in componentes]
    linha = ordenar_linhas_por_barycenter(spec, camada, back_edges, ordem_original)

    def row_col(id_):
        if orientacao == "horizontal":
            return linha[id_], camada[id_]  # row=linha, col=camada
        return camada[id_], linha[id_]  # row=camada, col=linha

    components = []
    for ator in atores:
        row, col = row_col(ator["id"])
        components.append({
            "id": ator["id"],
            "type": "external",
            "label": ator["nome"],
            "sublabel": ator.get("papel") or None,
            "size": [largura_estimada(ator["nome"], ator.get("papel")), ALTURA_COMPONENTE],
            "row": row,
            "col": col,
        })

    por_fronteira = {f["id"]: [] for f in spec.get("fronteiras", [])}
    for comp in componentes:
        tag = TAGS_STATUS.get(comp.get("status"), comp.get("status", "").upper() or None)
        row, col = row_col(comp["id"])
        sublabel = comp.get("descricao") or comp.get("tipo") or None
        components.append({
            "id": comp["id"],
            "type": classificar_tipo(comp),
            "label": comp["nome"],
            "sublabel": sublabel,
            "tag": tag,
            "size": [largura_estimada(comp["nome"], sublabel), ALTURA_COMPONENTE],
            "row": row,
            "col": col,
        })
        fid = comp.get("fronteira_id")
        if fid in por_fronteira:
            por_fronteira[fid].append(comp["id"])

    fronteiras_out = []
    for fronteira in spec.get("fronteiras", []):
        membros = por_fronteira.get(fronteira["id"], [])
        if not membros:
            continue
        rotulo = fronteira["nome"]
        if fronteira.get("ambiente"):
            rotulo += f' — {fronteira["ambiente"]}'
        fronteiras_out.append({"kind": "region", "label": rotulo, "wraps": membros})

    return components, fronteiras_out, back_edges


def montar_conexoes_minimas(spec):
    """Conexão mínima: sem `fromSide`/`toSide`/`via`/`labelDy` — geometria de
    rota é reparo pontual guiado por diagnóstico do `validate`, aplicado pelo
    agente, não geometria de partida (ver authoring-contract.md: "Do not add
    via, channelX, channelY, or labelAt before a diagnostic calls for
    one")."""
    conexoes = []
    for i, con in enumerate(spec.get("conexoes", [])):
        item = {
            "id": f"c{i}",
            "from": con["de"],
            "to": con["para"],
            "label": con.get("rotulo") or None,
        }
        if con.get("assincrona"):
            item["variant"] = "dashed"
        conexoes.append(item)
    return conexoes


def montar_spec_archify(spec, saida, orientacao):
    components, boundaries, back_edges = montar_componentes_archify(spec, orientacao)
    conexoes = [c for c in montar_conexoes_minimas(spec)]

    for comp in components:
        for chave in ("sublabel", "tag", "label"):
            if comp.get(chave) is None:
                comp.pop(chave, None)

    for con in conexoes:
        if con.get("label") is None:
            con.pop("label", None)

    max_col = max((c["col"] for c in components), default=0)

    arch = {
        "schema_version": 1,
        "diagram_type": "architecture",
        "meta": {
            "title": spec.get("titulo", "Diagrama"),
            "output": str(saida.name),
            "quality_profile": "showcase",
        },
        "layout": {
            "mode": "grid",
            "cols": max_col + 1,
            "gapX": GAP_X,
            "gapY": GAP_Y,
            "cellW": CELL_W,
            "cellH": CELL_H,
        },
        "components": components,
        "connections": conexoes,
    }
    if spec.get("subtitulo"):
        arch["meta"]["subtitle"] = spec["subtitulo"]
    if boundaries:
        arch["boundaries"] = boundaries
    return arch


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entrada", help="Spec JSON no formato de c4-schema.md")
    parser.add_argument("saida", help="Caminho de saída do candidato .architecture.json")
    parser.add_argument("--journey", help="ID de jornada para visão filtrada")
    parser.add_argument(
        "--orientacao", choices=["vertical", "horizontal"], default="vertical",
        help="Direção do fluxo principal do diagrama (default: vertical)",
    )
    args = parser.parse_args()

    spec = carregar_spec(args.entrada)
    if args.journey:
        spec = filtrar_por_jornada(spec, args.journey)

    violacoes = checar_limite_palavras(spec)
    if violacoes:
        print(f"[erro] {len(violacoes)} rótulo(s) acima do limite de {LIMITE_PALAVRAS_ROTULO} palavras — encurte no spec de origem antes de renderizar:", file=sys.stderr)
        for v in violacoes:
            print(f"  - {v}", file=sys.stderr)
        sys.exit(1)

    saida = Path(args.saida)
    saida.parent.mkdir(parents=True, exist_ok=True)
    arch = montar_spec_archify(spec, saida, args.orientacao)
    saida.write_text(json.dumps(arch, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[ok] candidato gravado em {saida} — rode `node skills/vendors/archify/archify/bin/archify.mjs validate architecture {saida} --quality showcase --json` em seguida.")


if __name__ == "__main__":
    main()
