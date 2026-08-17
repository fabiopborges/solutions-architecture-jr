#!/usr/bin/env python3
"""Deriva specs de Container (por jornada + geral) e Contexto a partir de
um catálogo estático de componentes + sequências dinâmicas por jornada.

Ver docs/diagrams/c4-schema.md, seção "Pipeline invertido" para o formato
de entrada e as regras de derivação. As saídas usam o mesmo schema que
montar_candidato_arquitetura_archify.py consome (componentes[] + conexoes[])
— nenhuma mudança necessária no renderer.

Uso:
    python3 derivar_c4.py CATALOGO.json SEQUENCIA1.json [SEQUENCIA2.json ...] --saida-dir DIR
"""
import argparse
import json
import sys
from pathlib import Path


def carregar_json(caminho):
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)


def indice_por_id(spec):
    """Devolve {id: item} para atores e componentes do catálogo, juntos."""
    indice = {}
    for ator in spec.get("atores", []):
        indice[ator["id"]] = {"kind": "ator", **ator}
    for comp in spec.get("componentes", []):
        indice[comp["id"]] = {"kind": "componente", **comp}
    return indice


def mensagens_projetaveis(sequencia):
    """Filtra mensagens que viram conexão de Container (regra 1)."""
    projetaveis = []
    for msg in sequencia.get("mensagens", []):
        tipo = msg.get("tipo", "chamada")
        if tipo in ("retorno", "self") or msg["de"] == msg["para"]:
            continue
        projetaveis.append(msg)
    return sorted(projetaveis, key=lambda m: m["ordem"])


def derivar_conexoes(mensagens, journey_id_por_msg):
    """Dedup por (de,para,protocolo), primeira ocorrência define o rótulo (regras 2-3)."""
    vistos = {}
    ordem_final = []
    for msg in mensagens:
        chave = (msg["de"], msg["para"], msg.get("protocolo"))
        jid = journey_id_por_msg[id(msg)]
        if chave not in vistos:
            vistos[chave] = {
                "de": msg["de"],
                "para": msg["para"],
                "rotulo": msg["rotulo"],
                "assincrona": msg.get("assincrona", False),
                "journey_id": [jid],
            }
            ordem_final.append(chave)
        else:
            if jid not in vistos[chave]["journey_id"]:
                vistos[chave]["journey_id"].append(jid)
    conexoes = []
    for chave in ordem_final:
        c = vistos[chave]
        c["journey_id"] = c["journey_id"][0] if len(c["journey_id"]) == 1 else c["journey_id"]
        conexoes.append(c)
    return conexoes


def participantes_usados(conexoes):
    ids = set()
    for c in conexoes:
        ids.add(c["de"])
        ids.add(c["para"])
    return ids


def montar_participante_fallback(participante_id):
    """[FALTA-CATALOGO]: importa com atributos mínimos inferidos do id (regra 8)."""
    return {
        "id": participante_id,
        "nome": participante_id.replace("_", " ").title(),
        "status": "desconhecido",
        "tipo": "não catalogado",
    }


def montar_spec_derivado(titulo, nivel, subtitulo, catalogo_indice, conexoes, journey_id=None):
    ids_usados = participantes_usados(conexoes)
    atores, componentes = [], []
    faltando_catalogo = []

    for pid in ids_usados:
        item = catalogo_indice.get(pid)
        if item is None:
            faltando_catalogo.append(pid)
            componentes.append(montar_participante_fallback(pid))
            continue
        if item["kind"] == "ator":
            atores.append({k: v for k, v in item.items() if k != "kind"})
        else:
            componentes.append({k: v for k, v in item.items() if k != "kind"})

    fronteiras_usadas = {c.get("fronteira_id") for c in componentes if c.get("fronteira_id")}

    spec = {
        "titulo": titulo,
        "nivel": nivel,
        "atores": atores,
        "fronteiras": [f for f in catalogo_indice.get("_fronteiras_raw", []) if f["id"] in fronteiras_usadas],
        "componentes": componentes,
        "conexoes": conexoes,
    }
    if subtitulo:
        spec["subtitulo"] = subtitulo
    if journey_id:
        spec["journey_id"] = journey_id
    return spec, faltando_catalogo


def derivar_contexto(spec_geral):
    """Colapsa componentes não-'Sistema' de cada fronteira num único nó (regra 6)."""
    por_fronteira = {}
    fora_fronteira = []
    for comp in spec_geral["componentes"]:
        if comp.get("tipo") == "Sistema":
            fora_fronteira.append(comp)
            continue
        fid = comp.get("fronteira_id")
        if fid:
            por_fronteira.setdefault(fid, []).append(comp)
        else:
            fora_fronteira.append(comp)

    fronteiras_por_id = {f["id"]: f for f in spec_geral["fronteiras"]}
    novos_componentes = list(fora_fronteira)
    mapa_colapso = {}  # id original -> id do sistema colapsado
    for fid, membros in por_fronteira.items():
        nome_sistema = fronteiras_por_id.get(fid, {}).get("nome", fid)
        sistema_id = f"sistema_{fid}"
        status_set = {m.get("status") for m in membros}
        status = "alterado" if len(status_set) > 1 else next(iter(status_set), "novo")
        novos_componentes.append({
            "id": sistema_id, "nome": nome_sistema, "status": status,
            "tipo": "Sistema", "descricao": f"Colapso de {len(membros)} componente(s) de {nome_sistema}",
        })
        for m in membros:
            mapa_colapso[m["id"]] = sistema_id

    novas_conexoes = []
    vistos = set()
    for con in spec_geral["conexoes"]:
        de = mapa_colapso.get(con["de"], con["de"])
        para = mapa_colapso.get(con["para"], con["para"])
        if de == para:
            continue
        chave = (de, para)
        if chave in vistos:
            continue
        vistos.add(chave)
        novas_conexoes.append({**con, "de": de, "para": para})

    return {
        "titulo": spec_geral["titulo"].replace("Container", "Contexto"),
        "nivel": "contexto",
        "atores": spec_geral["atores"],
        "fronteiras": [],
        "componentes": novos_componentes,
        "conexoes": novas_conexoes,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("catalogo", help="catalogo-componentes.json")
    parser.add_argument("sequencias", nargs="+", help="sequencia-<jornada>_spec.json (um ou mais)")
    parser.add_argument("--saida-dir", required=True, help="pasta onde gravar os specs derivados")
    parser.add_argument("--titulo-base", default="Demanda", help="prefixo do título dos diagramas gerados")
    args = parser.parse_args()

    catalogo = carregar_json(args.catalogo)
    catalogo_indice = indice_por_id(catalogo)
    catalogo_indice["_fronteiras_raw"] = catalogo.get("fronteiras", [])

    ids_catalogo_componentes = {c["id"] for c in catalogo.get("componentes", [])}
    ids_referenciados_em_alguma_jornada = set()
    faltando_catalogo_total = set()

    saida_dir = Path(args.saida_dir)
    saida_dir.mkdir(parents=True, exist_ok=True)

    todas_conexoes_com_journey = []
    todas_journey_ids_por_msg = {}

    for caminho_seq in args.sequencias:
        sequencia = carregar_json(caminho_seq)
        jid = sequencia["journey_id"]
        mensagens = mensagens_projetaveis(sequencia)
        journey_id_por_msg = {id(m): jid for m in mensagens}

        conexoes = derivar_conexoes(mensagens, journey_id_por_msg)
        ids_referenciados_em_alguma_jornada |= participantes_usados(conexoes)

        spec, faltando = montar_spec_derivado(
            titulo=f"{args.titulo_base} — Container — jornada {jid}",
            nivel="container",
            subtitulo=f"visão filtrada — jornada: {jid}",
            catalogo_indice=catalogo_indice,
            conexoes=conexoes,
            journey_id=jid,
        )
        faltando_catalogo_total |= set(faltando)

        destino = saida_dir / f"c4-container-jornada-{jid}.json"
        with open(destino, "w", encoding="utf-8") as f:
            json.dump(spec, f, ensure_ascii=False, indent=2)
        print(f"[ok] {destino} ({len(spec['componentes'])} componentes, {len(conexoes)} conexões)")

        for msg in mensagens:
            todas_conexoes_com_journey.append(msg)
            todas_journey_ids_por_msg[id(msg)] = jid

    conexoes_geral = derivar_conexoes(todas_conexoes_com_journey, todas_journey_ids_por_msg)
    spec_geral, faltando_geral = montar_spec_derivado(
        titulo=f"{args.titulo_base} — Container — geral",
        nivel="container",
        subtitulo="união de todas as jornadas",
        catalogo_indice=catalogo_indice,
        conexoes=conexoes_geral,
    )
    faltando_catalogo_total |= set(faltando_geral)

    destino_geral = saida_dir / "c4-container.json"
    with open(destino_geral, "w", encoding="utf-8") as f:
        json.dump(spec_geral, f, ensure_ascii=False, indent=2)
    print(f"[ok] {destino_geral} ({len(spec_geral['componentes'])} componentes, {len(conexoes_geral)} conexões)")

    spec_contexto = derivar_contexto(spec_geral)
    destino_contexto = saida_dir / "c4-contexto.json"
    with open(destino_contexto, "w", encoding="utf-8") as f:
        json.dump(spec_contexto, f, ensure_ascii=False, indent=2)
    print(f"[ok] {destino_contexto} ({len(spec_contexto['componentes'])} componentes, {len(spec_contexto['conexoes'])} conexões)")

    # Regra 7: [ORFAO]
    orfaos = ids_catalogo_componentes - ids_referenciados_em_alguma_jornada
    print("\n=== Relatório de derivação ===")
    if orfaos:
        for oid in sorted(orfaos):
            print(f"[ORFAO] componente '{oid}' está no catálogo mas não aparece em nenhuma jornada — excluído dos diagramas.")
    else:
        print("[ORFAO] nenhum.")

    if faltando_catalogo_total:
        for fid in sorted(faltando_catalogo_total):
            print(f"[FALTA-CATALOGO] '{fid}' aparece numa sequência mas não está em catalogo-componentes.json — importado com atributos mínimos (status 'desconhecido').")
    else:
        print("[FALTA-CATALOGO] nenhum.")


if __name__ == "__main__":
    main()
