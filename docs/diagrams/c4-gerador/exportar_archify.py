#!/usr/bin/env python3
"""Traduz um spec C4 (formato de docs/diagrams/c4-schema.md) para o formato
architecture.schema.json do ArchiFy (vendorizado em
skills/vendors/archify/archify/, github.com/tt-a1i/archify) e chama o CLI
dele (`archify.mjs validate`/`deliver`) para renderizar HTML autocontido.

Renderer padrão do pipeline (promovido de docs/diagrams/poc-archify/ depois
da POC — ver docs/diagrams/poc-archify/NOTAS-POC.md para o histórico de
como o layout foi validado). A geometria (camadas, ordenação por
barycenter, faixas de rota, viewBox) é calculada inteiramente aqui, em
Python — o ArchiFy só recebe o resultado já posicionado e faz a etapa
final de validação de qualidade visual + renderização em HTML. A geração de
`.drawio` foi eliminada do projeto (2026-08-16, script antigo removido).

Uso:
    python3 exportar_archify.py ENTRADA.json SAIDA.html
        [--journey JOURNEY_ID] [--archify-bin CAMINHO/bin/archify.mjs]
        [--orientacao {vertical,horizontal}] [--max-tentativas N]

    Sem --archify-bin, usa o binário vendorizado em
    skills/vendors/archify/archify/bin/archify.mjs (relativo à raiz do repo).
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ_REPO = Path(__file__).resolve().parents[3]
ARCHIFY_BIN_PADRAO = RAIZ_REPO / "skills" / "vendors" / "archify" / "archify" / "bin" / "archify.mjs"


def carregar_spec(caminho):
    return json.loads(Path(caminho).read_text(encoding="utf-8"))


def filtrar_por_jornada(spec, journey_id):
    """Recriada aqui depois da remoção de gerar_c4.py (2026-08-16) — contrato
    documentado em docs/diagrams/c4-schema.md, seção "Filtragem por jornada":
    mantém só conexões marcadas com `journey_id` (campo string ou lista), só
    componentes/atores que participam de ao menos uma conexão mantida, e só
    fronteiras ainda referenciadas por algum componente mantido."""
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
    visível dentro da caixa, ver montar_spec_archify) — e todo rótulo de
    seta (conexão), tem no máximo LIMITE_PALAVRAS_ROTULO palavras. Checar só
    `nome`/`rotulo` e esquecer `descricao`/`papel` é o erro mais comum aqui —
    esses dois campos SÃO renderizados, não são metadado invisível. Não
    trunca sozinho — quem autora o spec decide como encurtar sem perder o
    sentido. Retorna a lista de violações (vazia = ok)."""
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


def largura_estimada(*textos, minimo=150, maximo=280):
    maior = max((len(t) for t in textos if t), default=0)
    return max(minimo, min(maximo, 24 + maior * 7))


def analisar_grafo(spec):
    """Layout topológico de verdade em vez de coluna=fronteira: acha as
    conexões que fecham ciclo (DFS clássica, cor branco/cinza/preto) e usa só
    as conexões restantes (garantidamente um DAG) pra computar a camada de
    cada nó via longest-path (Kahn). Camada = "distância" no fluxo (vira
    coluna no layout horizontal, linha no vertical). Isso separa conexão "de
    ida" (adjacente ou pulando camada) de conexão "de volta" (retentativa,
    retorno de resultado) de forma estrutural, não geométrica."""
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
    Retorna id -> posição dentro da camada (0, 1, 2...)."""
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


def montar_componentes_archify(spec):
    """Camada topológica (analisar_grafo) em vez de fronteira — fronteira
    agora só agrupa visualmente (boundary) e define tag/tipo, quem manda na
    posição é a estrutura do grafo de conexões."""
    camada, back_edges = analisar_grafo(spec)

    atores = spec.get("atores", [])
    componentes = spec.get("componentes", [])
    ordem_original = [a["id"] for a in atores] + [c["id"] for c in componentes]
    linha = ordenar_linhas_por_barycenter(spec, camada, back_edges, ordem_original)

    posicoes_grid = {id_: (camada[id_], linha[id_]) for id_ in ordem_original}

    components = []
    for ator in atores:
        components.append({
            "id": ator["id"],
            "type": "external",
            "label": ator["nome"],
            "sublabel": ator.get("papel") or None,
            "_w": largura_estimada(ator["nome"], ator.get("papel")),
        })

    por_fronteira = {f["id"]: [] for f in spec.get("fronteiras", [])}
    for comp in componentes:
        tag = TAGS_STATUS.get(comp.get("status"), comp.get("status", "").upper() or None)
        components.append({
            "id": comp["id"],
            "type": classificar_tipo(comp),
            "label": comp["nome"],
            "sublabel": comp.get("descricao") or comp.get("tipo") or None,
            "tag": tag,
            "_w": largura_estimada(comp["nome"], comp.get("descricao") or comp.get("tipo")),
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

    return components, fronteiras_out, posicoes_grid, back_edges


def empacotar_faixas(intervalos, folga=24):
    """Empacota por ANINHAMENTO, não só por não-sobreposição: processa do
    intervalo mais ESTREITO pro mais LARGO. Um intervalo que contém outro (já
    colocado numa faixa rasa) não pode dividir faixa com ele — precisa ficar
    mais fundo, senão a "perna" do de dentro cruza a faixa do de fora (ou
    vice-versa). Processar por largura crescente garante isso: quem contém
    alguém só é avaliado depois de quem ele contém já estar alocado, então
    cai naturalmente numa faixa mais funda. Intervalos que se cruzam de
    verdade (nem aninhado nem disjunto — ex: A=[1,5] B=[3,8]) não têm solução
    sem faixa própria pra cada um; o `validate` ainda vai acusar esse caso."""
    faixas = []  # cada faixa: lista de (min, max) já alocados nela
    resultado = {}
    for id_, v_min, v_max in sorted(intervalos, key=lambda t: t[2] - t[1]):
        colocado = False
        for idx, ocupados in enumerate(faixas):
            if all(v_max < o_min - folga or v_min > o_max + folga for o_min, o_max in ocupados):
                ocupados.append((v_min, v_max))
                resultado[id_] = idx
                colocado = True
                break
        if not colocado:
            faixas.append([(v_min, v_max)])
            resultado[id_] = len(faixas) - 1
    return resultado


def lado_direito_livre(comp_id, posicoes_px):
    """True se não existe NENHUM outro componente na mesma faixa de altura
    (mesma "linha") à direita deste — ou seja, dá pra sair/entrar reto pelo
    lado direito sem cruzar ninguém no caminho até a faixa. Ponto de partida
    da "inteligência de contato": só usa o lado óbvio (baixo/cima) quando o
    lado livre (direita) não existe de verdade."""
    x0, y0, w0, h0 = posicoes_px[comp_id]
    y_centro = y0 + h0 / 2
    for outro_id, (x1, y1, w1, h1) in posicoes_px.items():
        if outro_id == comp_id:
            continue
        if y1 <= y_centro <= y1 + h1 and x1 >= x0 + w0:
            return False
    return True


def escolher_lado_e_pontos_lane(conexoes_lane, posicoes_px):
    """Decide, pra cada ponta de cada conexão de faixa, qual lado do
    componente usar — `right` (livre, contato direto com a faixa) quando
    possível, senão o desvio por baixo/cima (`bottom`/`top`, ver
    montar_via_de_faixa). O lado `right` só aceita o ponto de contato exato
    no centro da própria altura (testado: um `via` terminando fora do centro
    nesse lado faz o ArchiFy inserir uma correção diagonal de última hora e
    reprovar `clean-flow/endpoint-side-direction` — não dá pra espalhar
    múltiplos pontos livremente nesse lado). Por isso só a PRIMEIRA conexão
    que disputa `right` num componente fica com ele; as demais caem pro
    desvio, que aí sim espalha o ponto de contato ao longo da largura sem
    esse problema (testado, converge). Retorna dict
    (id(conexao), 'de'|'para') -> (lado, coordenada de contato)."""
    pontas = []
    for con in conexoes_lane:
        pontas.append((con, "de", con["de"], lado_direito_livre(con["de"], posicoes_px)))
        pontas.append((con, "para", con["para"], lado_direito_livre(con["para"], posicoes_px)))

    ja_usou_right = set()
    decisao = {}  # (id(con), extremidade) -> (comp_id, lado)
    for con, extremidade, comp_id, livre in pontas:
        if livre and comp_id not in ja_usou_right:
            ja_usou_right.add(comp_id)
            decisao[(id(con), extremidade)] = (comp_id, "right")
        else:
            lado_desvio = "bottom" if extremidade == "de" else "top"
            decisao[(id(con), extremidade)] = (comp_id, lado_desvio)

    grupos = {}
    for (con_id, extremidade), (comp_id, lado) in decisao.items():
        grupos.setdefault((comp_id, lado), []).append((con_id, extremidade))

    resultado = {}
    for (comp_id, lado), itens in grupos.items():
        x0, y0, w0, h0 = posicoes_px[comp_id]
        if lado == "right":
            for con_id, extremidade in itens:
                resultado[(con_id, extremidade)] = (lado, y0 + h0 / 2)
            continue
        n = len(itens)
        for i, (con_id, extremidade) in enumerate(itens):
            frac = (i + 1) / (n + 1)
            resultado[(con_id, extremidade)] = (lado, x0 + w0 * frac)
    return resultado


def montar_via_de_faixa(p_de, p_para, faixa, lado_de, contato_de, lado_para, contato_para):
    """Rota pra faixa vertical (à direita de tudo). Cada ponta usa o lado
    livre (`right`, contato direto — ver lado_direito_livre) quando existe;
    senão desvia por BAIXO da própria linha (saída) ou por CIMA (chegada)
    antes de virar em direção à faixa — sair/entrar reto pro lado, na mesma
    altura, só é seguro quando não tem ninguém no caminho até lá; do
    contrário cruza quem estiver na mesma camada."""
    x_de, y_de, w_de, h_de = p_de
    x_para, y_para, w_para, h_para = p_para
    via = []
    if lado_de == "right":
        via.append([faixa, contato_de])
    else:
        via.append([contato_de, y_de + h_de + 30])
        via.append([faixa, y_de + h_de + 30])
    if lado_para == "right":
        via.append([faixa, contato_para])
    else:
        via.append([faixa, y_para - 30])
        via.append([contato_para, y_para - 30])
    return via


def montar_conexoes_archify(spec, posicoes_grid, posicoes_px, back_edges, lane_base, orientacao):
    """posicoes_px: id -> (x, y, w, h) já em pixel. `back_edges` vem de
    analisar_grafo (estrutural, não geométrico) — junto com todo salto de
    camada >= 2, define quem precisa de rota "por fora" numa faixa própria:
    embaixo do diagrama (horizontal) ou à direita dele (vertical) — sempre
    perpendicular ao eixo de avanço do fluxo."""
    conexoes_raw = spec.get("conexoes", [])
    # eixo de avanço do fluxo: x no horizontal (esquerda→direita), y no
    # vertical (cima→baixo). idx 0/2 = x/largura; idx 1/3 = y/altura.
    idx_pos, idx_tam = (0, 2) if orientacao == "horizontal" else (1, 3)
    lado_ida = ("right", "left") if orientacao == "horizontal" else ("bottom", "top")
    lado_faixa = "bottom" if orientacao == "horizontal" else "right"
    # labelDy é o eixo certo pra escapar de sobreposição mesmo no vertical:
    # os componentes são bem mais largos que altos, então um rótulo colado
    # numa aresta vertical entre dois deles precisa de um deslocamento em Y
    # bem menor pra sair da caixa do que em X (a caixa é larga) — testado
    # empiricamente, labelDx sozinho não convergia em nenhum caso vertical.
    campo_deslocamento = "labelDy"

    grupos = {}
    for con in conexoes_raw:
        col_de, _ = posicoes_grid.get(con["de"], (None, None))
        col_para, _ = posicoes_grid.get(con["para"], (None, None))
        chave = tuple(sorted((col_de, col_para))) if col_de is not None and col_para is not None else None
        grupos.setdefault(chave, []).append(con)

    def precisa_de_faixa(con, col_de, col_para):
        if col_de is None or col_para is None:
            return False
        return (con["de"], con["para"]) in back_edges or abs(col_de - col_para) >= 2

    def centro(id_):
        p = posicoes_px[id_]
        return p[idx_pos] + p[idx_tam] / 2

    intervalos = []
    for con in conexoes_raw:
        col_de, _ = posicoes_grid.get(con["de"], (None, None))
        col_para, _ = posicoes_grid.get(con["para"], (None, None))
        if not precisa_de_faixa(con, col_de, col_para):
            continue
        c_de, c_para = centro(con["de"]), centro(con["para"])
        intervalos.append((id(con), min(c_de, c_para), max(c_de, c_para)))
    faixa_por_conexao = empacotar_faixas(intervalos)

    conexoes_lane = [
        con for con in conexoes_raw
        if precisa_de_faixa(
            con,
            posicoes_grid.get(con["de"], (None, None))[0],
            posicoes_grid.get(con["para"], (None, None))[0],
        )
    ]
    pontos_contato_lane = escolher_lado_e_pontos_lane(conexoes_lane, posicoes_px) if orientacao == "vertical" else {}

    conexoes = []
    for i, con in enumerate(conexoes_raw):
        col_de, _ = posicoes_grid.get(con["de"], (None, None))
        col_para, _ = posicoes_grid.get(con["para"], (None, None))
        chave = tuple(sorted((col_de, col_para))) if col_de is not None and col_para is not None else None
        indice_no_grupo = grupos[chave].index(con)

        item = {
            "id": f"c{i}",
            "from": con["de"],
            "to": con["para"],
            "label": con.get("rotulo") or None,
            campo_deslocamento: -22 - 26 * indice_no_grupo,
        }
        if con.get("assincrona"):
            item["variant"] = "dashed"

        if precisa_de_faixa(con, col_de, col_para):
            # Conexão de volta (ciclo real, ex: retentativa) ou que pula mais
            # de uma camada: rotear por fora numa faixa própria — nunca
            # deixar o auto-router tentar cruzar por dentro das camadas do
            # meio, é ali que nascem cruzamento e rótulo colado.
            # Passo entre faixas vizinhas: no horizontal, o rótulo é baixo
            # (~14px) e a pilha de faixas cresce em Y — 30px entre elas basta.
            # No vertical, as faixas crescem em X mas o rótulo continua
            # LARGO (até ~280px, texto horizontal) — faixas vizinhas perto
            # demais em X fazem os rótulos se sobreporem mesmo com as linhas
            # bem separadas. Precisa de um passo bem maior.
            passo_faixa = 30 if orientacao == "horizontal" else 220
            faixa = lane_base + passo_faixa * faixa_por_conexao[id(con)]
            if orientacao == "horizontal":
                c_de, c_para = centro(con["de"]), centro(con["para"])
                item["fromSide"], item["toSide"] = lado_faixa, lado_faixa
                item["via"] = [[c_de, faixa], [c_para, faixa]]
                item.pop(campo_deslocamento, None)
                item["labelSegment"] = 1
            else:
                lado_de, contato_de = pontos_contato_lane[(id(con), "de")]
                lado_para, contato_para = pontos_contato_lane[(id(con), "para")]
                item["fromSide"], item["toSide"] = lado_de, lado_para
                item["via"] = montar_via_de_faixa(
                    posicoes_px[con["de"]], posicoes_px[con["para"]], faixa,
                    lado_de, contato_de, lado_para, contato_para,
                )
                item["_faixa"] = faixa  # metadado privado (removido antes de gravar) — recolocar() precisa disso pra reconstruir o via inteiro, não só ajustar pontas
                item.pop(campo_deslocamento, None)
                # sem labelSegment fixo aqui: o via agora tem de 2 a 4 pontos
                # (depende do lado escolhido em cada ponta), um índice fixo
                # deixaria de apontar pro segmento certo — deixa o ArchiFy
                # escolher, e o reparo (_empurrar_conexao) cobre sobreposição
                # residual deslocando a faixa.
        elif col_de is not None and col_para is not None and col_de != col_para:
            item["fromSide"], item["toSide"] = lado_ida

        conexoes.append(item)
    return conexoes


ORIGEM_X, ORIGEM_Y = 60, 80
ALTURA_COMPONENTE = 64
# Espaço entre camadas (eixo de avanço) e entre nós de uma mesma camada
# (eixo perpendicular). No horizontal, o eixo de avanço carrega texto longo
# (rótulo de conexão horizontal) — precisa de mais espaço que no vertical,
# onde o rótulo roda ao lado da linha vertical.
GAP_ENTRE_CAMADAS = {"horizontal": 300, "vertical": 200}
GAP_ENTRE_NOS = {"horizontal": 170, "vertical": 90}


def calcular_posicoes(components, posicoes_grid, orientacao):
    """Recalcula pos=[x,y] de todo componente a partir da grade lógica
    (camada, posição-na-camada) + orientação. Chamada tanto na montagem
    inicial quanto de novo a cada reparo que redimensiona algo (`recolocar`)
    — nunca ajusta só o componente que mudou: redimensionar um afeta o
    espaço reservado pros vizinhos (mesma camada, no vertical — packing por
    largura própria; camadas seguintes, no horizontal — coluna larga como o
    maior componente dela).

    Horizontal: camada vira coluna (x), maior componente da camada define a
    largura da coluna inteira, empilha por posição-na-camada em y (altura
    fixa, gap uniforme).

    Vertical: camada vira linha (y, altura sempre fixa — não depende de
    largura de texto), dentro da linha cada componente usa a PRÓPRIA largura
    (não a máxima da linha) e o conjunto é centralizado em relação à linha
    mais larga — isso distribui melhor o espaço em vez de forçar toda linha
    a ter a largura da mais cheia."""
    comps_por_id = {c["id"]: c for c in components}
    por_camada = {}
    for id_, (camada, linha) in posicoes_grid.items():
        por_camada.setdefault(camada, []).append(id_)
    for ids in por_camada.values():
        ids.sort(key=lambda id_: posicoes_grid[id_][1])

    gap_camada = GAP_ENTRE_CAMADAS[orientacao]
    gap_no = GAP_ENTRE_NOS[orientacao]

    if orientacao == "horizontal":
        larguras_camada = {c: max(comps_por_id[i]["size"][0] for i in ids) for c, ids in por_camada.items()}
        x_por_camada, x_acc = {}, ORIGEM_X
        for c in sorted(larguras_camada):
            x_por_camada[c] = x_acc
            x_acc += larguras_camada[c] + gap_camada
        for camada, ids in por_camada.items():
            for linha, id_ in enumerate(ids):
                comps_por_id[id_]["pos"] = [x_por_camada[camada], ORIGEM_Y + linha * gap_no]
    else:
        y_por_camada, y_acc = {}, ORIGEM_Y
        for c in sorted(por_camada):
            y_por_camada[c] = y_acc
            y_acc += ALTURA_COMPONENTE + gap_camada
        larguras_totais = {
            c: sum(comps_por_id[i]["size"][0] for i in ids) + gap_no * (len(ids) - 1)
            for c, ids in por_camada.items()
        }
        largura_max = max(larguras_totais.values(), default=0)
        for camada, ids in por_camada.items():
            x = ORIGEM_X + (largura_max - larguras_totais[camada]) / 2
            for id_ in ids:
                comps_por_id[id_]["pos"] = [x, y_por_camada[camada]]
                x += comps_por_id[id_]["size"][0] + gap_no


def montar_spec_archify(spec, saida_html, orientacao):
    components, boundaries, posicoes_grid, back_edges = montar_componentes_archify(spec)

    for comp in components:
        comp["size"] = [comp.pop("_w"), ALTURA_COMPONENTE]
        for chave in ("sublabel", "tag", "label"):
            if comp.get(chave) is None:
                comp.pop(chave, None)

    calcular_posicoes(components, posicoes_grid, orientacao)
    posicoes_px = {c["id"]: (c["pos"][0], c["pos"][1], c["size"][0], c["size"][1]) for c in components}

    if orientacao == "horizontal":
        lane_base = max(y + h for _, y, _, h in posicoes_px.values()) + 70
    else:
        lane_base = max(x + w for x, _, w, _ in posicoes_px.values()) + 70

    conexoes = montar_conexoes_archify(spec, posicoes_grid, posicoes_px, back_edges, lane_base, orientacao)

    for con in conexoes:
        if con.get("label") is None:
            con.pop("label", None)

    arch = {
        "schema_version": 1,
        "diagram_type": "architecture",
        "meta": {
            "title": spec.get("titulo", "Diagrama"),
            "output": str(saida_html.name),
            "quality_profile": "showcase",
        },
        "components": components,
        "connections": conexoes,
    }
    if spec.get("subtitulo"):
        arch["meta"]["subtitle"] = spec["subtitulo"]
    if boundaries:
        arch["boundaries"] = boundaries
    return arch, posicoes_grid


PADRAO_SUBLABEL_ESTREITO = re.compile(
    r'Sublabel "(?P<texto>.+)" needs ~(?P<precisa>\d+)px .*'
    r'component "(?P<comp>[^"]+)" provides (?P<tem>\d+)px'
)
PADRAO_LABEL_OVERLAP = re.compile(r'Label "(?P<texto>.+)" overlaps component "(?P<comp>[^"]+)"')
PADRAO_SUGESTAO_DESLOCAMENTO = re.compile(r"label(?:Dy|Dx) ([+-]\d+)")
PADRAO_ROTULO_NO_ESTREITO = re.compile(
    r'Label "(?P<texto>.+)" \(~(?P<precisa>\d+)px\) is wider than component "(?P<comp>[^"]+)" \((?P<tem>\d+)px\)'
)
PADRAO_LABEL_ENTRE_CONEXOES = re.compile(r'on connections\[\d+\] id "(?P<owner>c\d+)"')


def recolocar(arch, posicoes_grid, orientacao):
    """Redimensionar um componente (reparo por sublabel/rótulo estreito)
    invalida a posição de vizinhos (ver `calcular_posicoes`) e todo `via` que
    passa perto — recalcula posição de cada componente e realinha vias a
    partir do zero, em vez de só ajustar o componente que mudou."""
    calcular_posicoes(arch["components"], posicoes_grid, orientacao)
    comps_por_id = {c["id"]: c for c in arch["components"]}

    if orientacao == "vertical":
        # Via de 2-4 pontos com lado escolhido por lugar livre (ver
        # escolher_lado_e_pontos_lane/montar_via_de_faixa) — reconstrói
        # inteiro a partir do `_faixa` guardado (o lado/ponto de contato pode
        # mudar depois do reposicionamento, não dá pra só ajustar ponta).
        posicoes_px_atual = {c["id"]: (c["pos"][0], c["pos"][1], c["size"][0], c["size"][1]) for c in arch["components"]}
        conexoes_lane = [con for con in arch["connections"] if "_faixa" in con]
        pares_de_para = [{"de": con["from"], "para": con["to"]} for con in conexoes_lane]
        pontos_contato_lane = escolher_lado_e_pontos_lane(pares_de_para, posicoes_px_atual)
        for par, con in zip(pares_de_para, conexoes_lane):
            lado_de, contato_de = pontos_contato_lane[(id(par), "de")]
            lado_para, contato_para = pontos_contato_lane[(id(par), "para")]
            con["fromSide"], con["toSide"] = lado_de, lado_para
            con["via"] = montar_via_de_faixa(
                posicoes_px_atual[con["from"]], posicoes_px_atual[con["to"]], con["_faixa"],
                lado_de, contato_de, lado_para, contato_para,
            )
    else:
        idx = 0  # eixo que o `via` acompanha no horizontal
        for con in arch["connections"]:
            via = con.get("via")
            if not via:
                continue
            de, para = comps_por_id.get(con["from"]), comps_por_id.get(con["to"])
            if de:
                via[0][idx] = de["pos"][idx] + de["size"][idx] / 2
            if para:
                via[-1][idx] = para["pos"][idx] + para["size"][idx] / 2

    # A faixa de "rota por fora" (ver montar_conexoes_archify) foi calculada
    # a partir da extensão máxima ANTES do reparo. Se recolocar() empurrou
    # componentes pra além dela (widening no vertical desloca X, inclusive
    # recentralizando outras camadas), a faixa deixa de estar "por fora" de
    # verdade — desloca o bloco inteiro de faixas (preserva o espaçamento
    # relativo entre elas) até voltar a limpar todo mundo.
    idx_perp = 0 if orientacao == "vertical" else 1
    conexoes_com_via = [con for con in arch["connections"] if con.get("via")]
    if conexoes_com_via:
        limite_atual = max(c["pos"][idx_perp] + c["size"][idx_perp] for c in arch["components"]) + 70
        if orientacao == "vertical":
            faixa_mais_perto = min(con["_faixa"] for con in conexoes_com_via)
            if faixa_mais_perto < limite_atual:
                delta = limite_atual - faixa_mais_perto
                for con in conexoes_com_via:
                    con["_faixa"] += delta
                    de, para = comps_por_id[con["from"]], comps_por_id[con["to"]]
                    p_de = (*de["pos"], *de["size"])
                    p_para = (*para["pos"], *para["size"])
                    contato_de = con["via"][0][1] if con["fromSide"] == "right" else con["via"][0][0]
                    contato_para = con["via"][-1][1] if con["toSide"] == "right" else con["via"][-1][0]
                    con["via"] = montar_via_de_faixa(
                        p_de, p_para, con["_faixa"],
                        con["fromSide"], contato_de, con["toSide"], contato_para,
                    )
        else:
            faixa_mais_perto = min(con["via"][0][idx_perp] for con in conexoes_com_via)
            if faixa_mais_perto < limite_atual:
                delta = limite_atual - faixa_mais_perto
                for con in conexoes_com_via:
                    con["via"][0][idx_perp] += delta
                    con["via"][1][idx_perp] += delta


def aplicar_reparo(arch, diagnosticos, tentativas_por_conexao, posicoes_grid, orientacao):
    """Aplica correções mecânicas a partir dos diagnósticos do `validate`,
    usando a própria sugestão numérica que o `validate` devolve na mensagem.
    Retorna True se aplicou pelo menos uma correção nova (vale tentar de novo)."""
    algo_mudou = False
    precisa_recolocar = False
    comps_por_id = {c["id"]: c for c in arch["components"]}

    for d in diagnosticos:
        msg = d.get("message", "")
        m = PADRAO_ROTULO_NO_ESTREITO.search(msg)
        if m:
            comp = comps_por_id.get(m.group("comp"))
            if comp:
                novo_w = int(m.group("precisa")) + 20
                if novo_w > comp["size"][0]:
                    comp["size"][0] = novo_w
                    precisa_recolocar = True
                    algo_mudou = True
            continue
        m = PADRAO_SUBLABEL_ESTREITO.search(msg)
        if m:
            comp = comps_por_id.get(m.group("comp"))
            if comp:
                novo_w = int(m.group("precisa")) + 20
                if novo_w > comp["size"][0]:
                    comp["size"][0] = novo_w
                    precisa_recolocar = True
                    algo_mudou = True
            continue
        m = PADRAO_LABEL_ENTRE_CONEXOES.search(msg)
        if m:
            con = next((c for c in arch["connections"] if c["id"] == m.group("owner")), None)
            if con and _empurrar_conexao(con, tentativas_por_conexao, orientacao, comps_por_id):
                algo_mudou = True
            continue
        m = PADRAO_LABEL_OVERLAP.search(msg)
        if m:
            for con in arch["connections"]:
                if con.get("label") != m.group("texto"):
                    continue
                sugestao = PADRAO_SUGESTAO_DESLOCAMENTO.search(msg)
                extra = [int(sugestao.group(1))] if sugestao else []
                if _empurrar_conexao(con, tentativas_por_conexao, orientacao, comps_por_id, extra):
                    algo_mudou = True

    if precisa_recolocar:
        recolocar(arch, posicoes_grid, orientacao)
    return algo_mudou


def _empurrar_conexao(con, tentativas_por_conexao, orientacao, comps_por_id, candidatos_extra=None):
    """Desloca a rota/rótulo de uma conexão pra uma variante ainda não
    tentada — se ela tem `via` (rota por fora, ver montar_conexoes_archify),
    desloca a faixa (eixo perpendicular ao de avanço); senão desloca o
    rótulo (labelDy — eixo certo nas duas orientações, ver montar_conexoes_archify).
    Retorna True se
    achou uma variante nova."""
    ja_tentado = tentativas_por_conexao.setdefault(con["id"], set())
    if con.get("via") and orientacao == "horizontal":
        # via de 2 pontos, ambos na mesma faixa Y — desloca os dois juntos.
        candidatos = [20, -20, 40, -40, 60, -60]
        for delta in candidatos:
            if delta in ja_tentado:
                continue
            ja_tentado.add(delta)
            novo_via = [list(p) for p in con["via"]]
            for p in novo_via:
                p[1] += delta
            con["via"] = novo_via
            return True
        return False
    if con.get("via") and "_faixa" in con:
        # via de 2-4 pontos com lado livre (ver montar_via_de_faixa) — só a
        # faixa em si desloca; os pontos de contato nas pontas seguem o lado
        # já escolhido, mexer neles desalinharia a entrada/saída.
        candidatos = [40, -40, 80, -80, 120, -120]
        for delta in candidatos:
            if delta in ja_tentado:
                continue
            ja_tentado.add(delta)
            con["_faixa"] = con["_faixa"] + delta
            de, para = comps_por_id[con["from"]], comps_por_id[con["to"]]
            p_de = (*de["pos"], *de["size"])
            p_para = (*para["pos"], *para["size"])
            contato_de = con["via"][0][1] if con["fromSide"] == "right" else con["via"][0][0]
            contato_para = con["via"][-1][1] if con["toSide"] == "right" else con["via"][-1][0]
            con["via"] = montar_via_de_faixa(
                p_de, p_para, con["_faixa"], con["fromSide"], contato_de, con["toSide"], contato_para,
            )
            return True
        return False
    campo = "labelDy"
    candidatos = list(candidatos_extra or []) + [-22, 22, -46, 46, -70, 70, -94, 94, -118, 118, -142, 142]
    for valor in candidatos:
        if valor not in ja_tentado:
            con[campo] = valor
            ja_tentado.add(valor)
            return True
    return False


def validar(archify_bin, caminho_spec, tipo="architecture"):
    cmd = ["node", archify_bin, "validate", tipo, str(caminho_spec), "--quality", "showcase", "--json"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return {"ok": False, "diagnostics": [], "_raw_stderr": r.stderr, "_raw_stdout": r.stdout}


def calcular_viewbox(arch, margem=40, altura_legenda=120):
    """O `viewBox` automático do ArchiFy (quando `meta.viewBox` não é
    informado) só mede `components`/`boundaries` — NUNCA os pontos de `via`
    das conexões (conferido no `render-architecture.mjs` dele: `autoViewBox`
    itera só `components` e `boundaries`). A faixa de rota "por fora" (ver
    montar_conexoes_archify/montar_via_vertical) é desenhada DE PROPÓSITO
    além da extensão de qualquer componente — é assim que ela evita cruzar
    alguém. Sem informar `meta.viewBox` explicitamente, essa faixa (e a seta,
    e o rótulo) ficam fora da área visível do SVG, cortadas. Este cálculo
    mede também os pontos de `via` e sempre fixa um `viewBox` explícito que
    cobre os dois — chamado antes de CADA gravação (validate/deliver), nunca
    só uma vez, porque o reparo pode mover a faixa depois."""
    max_x = max(c["pos"][0] + c["size"][0] for c in arch["components"])
    max_y = max(c["pos"][1] + c["size"][1] for c in arch["components"])
    for con in arch["connections"]:
        for x, y in con.get("via") or []:
            max_x = max(max_x, x)
            max_y = max(max_y, y)
    return [int(max_x + margem) + 1, int(max_y + margem + altura_legenda) + 1]


def serializar_para_archify(arch):
    """Remove metadado privado (`_faixa`, ver montar_via_vertical/recolocar)
    e fixa `meta.viewBox` (ver calcular_viewbox) antes de gravar — o schema
    do ArchiFy não aceita propriedade extra além das dele."""
    limpo = json.loads(json.dumps(arch))
    for con in limpo.get("connections", []):
        con.pop("_faixa", None)
    limpo["meta"]["viewBox"] = calcular_viewbox(limpo)
    return limpo


def entregar(archify_bin, caminho_spec, caminho_html, tipo="architecture"):
    cmd = ["node", archify_bin, "deliver", tipo, str(caminho_spec), str(caminho_html), "--quality", "showcase", "--json"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return {"ok": False, "_raw_stderr": r.stderr, "_raw_stdout": r.stdout}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entrada", help="Spec JSON no formato de c4-schema.md")
    parser.add_argument("saida_html", help="Caminho de saída do .html")
    parser.add_argument("--journey", help="ID de jornada para visão filtrada")
    parser.add_argument(
        "--archify-bin",
        default=str(ARCHIFY_BIN_PADRAO),
        help=f"Caminho pro archify.mjs (default: vendorizado em {ARCHIFY_BIN_PADRAO})",
    )
    parser.add_argument(
        "--orientacao", choices=["vertical", "horizontal"], default="vertical",
        help="Direção do fluxo principal do diagrama (default: vertical)",
    )
    parser.add_argument("--max-tentativas", type=int, default=12)
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

    saida_html = Path(args.saida_html)
    saida_html.parent.mkdir(parents=True, exist_ok=True)
    arch, posicoes_grid = montar_spec_archify(spec, saida_html, args.orientacao)

    caminho_spec_archify = saida_html.with_suffix(".architecture.json")

    tentativas_por_conexao = {}
    mensagens_rodada_anterior = None
    melhor_arch, melhor_n_erros = None, None
    for tentativa in range(1, args.max_tentativas + 1):
        caminho_spec_archify.write_text(json.dumps(serializar_para_archify(arch), indent=2, ensure_ascii=False), encoding="utf-8")
        resultado = validar(args.archify_bin, caminho_spec_archify)
        comp = resultado.get("composition") or {}
        diagnosticos = resultado.get("diagnostics", [])
        mensagens_atuais = {d.get("message") for d in diagnosticos}
        print(f"[tentativa {tentativa}] erros de validate: {len(diagnosticos)}", file=sys.stderr)

        if resultado.get("ok") and comp.get("status") == "pass":
            melhor_arch, melhor_n_erros = arch, 0
            break

        if melhor_n_erros is None or len(diagnosticos) < melhor_n_erros:
            melhor_arch = json.loads(json.dumps(arch))  # snapshot — o reparo pode piorar de rodada
            melhor_n_erros = len(diagnosticos)

        if mensagens_atuais == mensagens_rodada_anterior:
            print("[aviso] mesmos diagnósticos da rodada anterior, parando o reparo automático.", file=sys.stderr)
            break
        mensagens_rodada_anterior = mensagens_atuais

        if not aplicar_reparo(arch, diagnosticos, tentativas_por_conexao, posicoes_grid, args.orientacao):
            print("[aviso] diagnóstico sem reparo automático conhecido:", file=sys.stderr)
            for d in diagnosticos:
                print(f"  - {d.get('message')}", file=sys.stderr)
            break
    else:
        print("[aviso] limite de tentativas de reparo atingido.", file=sys.stderr)

    if melhor_n_erros:
        print(f"[aviso] não convergiu a zero — entregando a melhor rodada ({melhor_n_erros} diagnósticos).", file=sys.stderr)
    caminho_spec_archify.write_text(json.dumps(serializar_para_archify(melhor_arch), indent=2, ensure_ascii=False), encoding="utf-8")

    entrega = entregar(args.archify_bin, caminho_spec_archify, saida_html)
    print(json.dumps(entrega, indent=2, ensure_ascii=False))
    if not entrega.get("ok"):
        sys.exit(1)


if __name__ == "__main__":
    main()
