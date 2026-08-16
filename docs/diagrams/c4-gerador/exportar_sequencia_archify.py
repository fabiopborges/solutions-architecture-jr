#!/usr/bin/env python3
"""Traduz `sequencia-<journey_id>_spec.json` (produzido por
agents/jornadas-do-usuario, formato em docs/diagrams/c4-schema.md) para o
formato sequence.schema.json do ArchiFy (vendorizado em
skills/vendors/archify/archify/) e chama o CLI dele para renderizar HTML
autocontido — mesmo padrão de exportar_archify.py, para o tipo "sequence".

A ordem das mensagens (`ordem`) vira posição Y determinística — geometria
nossa, sem ajuste manual. Participantes são derivados dos `de`/`para` únicos,
na ordem de primeira aparição, com rótulo/tipo resolvidos via o catálogo
estático da demanda (`catalogo-componentes.json`).

Duas limitações conhecidas do renderer de sequência do ArchiFy, não
contornáveis por geometria pura — tratadas explicitamente, nunca silenciadas:

1. **Sem mensagem própria (from == to).** Mensagens com `tipo: "self"` no
   spec de origem viram uma NOTA (`note`) anexada à próxima mensagem real que
   sai do mesmo participante (ou à anterior, se não houver próxima). O script
   imprime `[SELF-COMO-NOTA]` no relatório para cada uma.
2. **Caixa de participante com teto de 190px, sem encolhimento de fonte no
   `label` principal** (só o `sublabel` encolhe). Nomes do catálogo no
   formato `"C1 — Adaptador de Detecção de Novo Lead"` são separados em
   `label` curto (`"C1"`) + `sublabel` completo — nada é descartado, só
   reorganizado em duas linhas. Nomes sem esse separador usam o `id` do
   catálogo (já curto, canônico) como `label` e o nome completo como
   `sublabel`.

Uso:
    python3 exportar_sequencia_archify.py SEQUENCIA_SPEC.json CATALOGO.json SAIDA.html
        [--archify-bin CAMINHO/bin/archify.mjs] [--max-tentativas N]
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exportar_archify import classificar_tipo, validar, entregar, contar_palavras, LIMITE_PALAVRAS_ROTULO  # noqa: E402

RAIZ_REPO = Path(__file__).resolve().parents[3]
ARCHIFY_BIN_PADRAO = RAIZ_REPO / "skills" / "vendors" / "archify" / "archify" / "bin" / "archify.mjs"

PASSO_Y = 70
Y_MINIMO = 160
VIEWBOX_Y_MARGEM = 220  # espaço abaixo da última mensagem pra legenda/margem

PARTICIPANTE_W_MIN = 86
PARTICIPANTE_W_MAX = 190
SIDE_MARGIN = 62

TIPOS_ATOR_EXTERNO = {"usuario_externo", "usuario_interno", "sistema_externo"}


def carregar_json(caminho):
    return json.loads(Path(caminho).read_text(encoding="utf-8"))


def estimar_largura_label(texto):
    """Mesma fórmula usada pra componentes de arquitetura (~7px/char + 24px
    de respiro), mas com o teto de 190px que o renderer de sequência impõe
    (render-sequence.mjs: participantW = min(190, ...)) — passar disso não
    adianta, o `label` nunca encolhe fonte."""
    return max(PARTICIPANTE_W_MIN, min(PARTICIPANTE_W_MAX, 24 + len(texto) * 7))


def label_e_sublabel(nome, participant_id):
    if " — " in nome:
        curto, resto = nome.split(" — ", 1)
        return curto.strip(), resto.strip()
    return participant_id, nome


def montar_indice_catalogo(catalogo):
    """id -> (nome, tipo_archify), cobrindo atores[] e componentes[]."""
    indice = {}
    for ator in catalogo.get("atores", []):
        indice[ator["id"]] = (
            ator.get("nome", ator["id"]),
            "external" if ator.get("tipo") in TIPOS_ATOR_EXTERNO else classificar_tipo(ator),
        )
    for comp in catalogo.get("componentes", []):
        indice[comp["id"]] = (comp.get("nome", comp["id"]), classificar_tipo(comp))
    return indice


def montar_participantes(mensagens, indice_catalogo):
    """Ordem de primeira aparição em `de`/`para`, ignorando self (de==para não adiciona 2x)."""
    vistos = []
    for m in mensagens:
        for pid in (m["de"], m["para"]):
            if pid not in vistos:
                vistos.append(pid)
    participantes = []
    for pid in vistos:
        nome, tipo = indice_catalogo.get(pid, (pid, "backend"))
        curto, sublabel = label_e_sublabel(nome, pid)
        participantes.append({"id": pid, "type": tipo, "label": curto, "sublabel": sublabel})
    return participantes


def montar_mensagens_e_relatorio(mensagens):
    """Retorna (messages[] pro ArchiFy, relatório de self-como-nota)."""
    reais = [m for m in mensagens if m.get("tipo") != "self" and m["de"] != m["para"]]
    selfs = [m for m in mensagens if m.get("tipo") == "self" or m["de"] == m["para"]]

    out = []
    for i, m in enumerate(reais):
        variant = "default"
        if m.get("tipo") == "retorno":
            variant = "return"
        elif m.get("assincrona"):
            variant = "dashed"
        out.append({
            "id": f"m{m['ordem']}",
            "from": m["de"],
            "to": m["para"],
            "y": Y_MINIMO + i * PASSO_Y,
            "label": m["rotulo"],
            "variant": variant,
        })

    relatorio = []
    for s in selfs:
        participante = s["de"]
        # próxima mensagem real que SAI do mesmo participante; senão, a anterior que chega nele.
        alvo = next((o for o in out if o["from"] == participante and o["id"] != f"m{s['ordem']}"), None)
        direcao = "próxima"
        if alvo is None:
            candidatos_antes = [o for o in out if o["to"] == participante]
            alvo = candidatos_antes[-1] if candidatos_antes else None
            direcao = "anterior"
        nota = f"[passo interno] {s['rotulo']}"
        if alvo is not None:
            alvo["note"] = (alvo.get("note") + " | " + nota) if alvo.get("note") else nota
            relatorio.append(
                f"[SELF-COMO-NOTA] ordem {s['ordem']} ('{s['rotulo']}', participante {participante}) "
                f"virou nota na mensagem {direcao} desse participante (id {alvo['id']})."
            )
        else:
            relatorio.append(
                f"[SELF-COMO-NOTA] ordem {s['ordem']} ('{s['rotulo']}', participante {participante}) "
                f"NÃO encontrou mensagem real pra anexar nota — nenhuma outra mensagem envolve esse participante."
            )

    return out, relatorio


def calcular_viewbox(participantes, messages):
    n = max(1, len(participantes))
    maior_label = max((estimar_largura_label(p["label"]) for p in participantes), default=PARTICIPANTE_W_MIN)
    # inverso de participantW = round((largura - 2*margem)/n) - 24, arredondado pra cima com folga
    largura = int((maior_label + 24) * n + SIDE_MARGIN * 2) + 40
    largura = max(largura, 620)
    altura = (max((m["y"] for m in messages), default=Y_MINIMO)) + VIEWBOX_Y_MARGEM
    return [largura, altura]


def checar_limite_palavras_sequencia(arch):
    """Mesma regra de padronização de exportar_archify.py, adaptada pro
    formato de sequência: `participants[].label`/`.sublabel` e
    `messages[].label`. Não trunca sozinho."""
    violacoes = []
    for p in arch.get("participants", []):
        for campo in ("label", "sublabel"):
            texto = p.get(campo)
            n = contar_palavras(texto)
            if n > LIMITE_PALAVRAS_ROTULO:
                violacoes.append(f"[participante:{campo}] '{p['id']}' ({n} palavras, limite {LIMITE_PALAVRAS_ROTULO}): \"{texto}\"")
    for m in arch.get("messages", []):
        n = contar_palavras(m.get("label"))
        if n > LIMITE_PALAVRAS_ROTULO:
            violacoes.append(f"[mensagem] '{m['id']}' ({n} palavras, limite {LIMITE_PALAVRAS_ROTULO}): \"{m.get('label')}\"")
    return violacoes


def montar_spec_archify(spec_sequencia, catalogo):
    indice = montar_indice_catalogo(catalogo)
    mensagens = sorted(spec_sequencia["mensagens"], key=lambda m: m["ordem"])
    participantes = montar_participantes(mensagens, indice)
    messages, relatorio = montar_mensagens_e_relatorio(mensagens)
    arch = {
        "schema_version": 1,
        "diagram_type": "sequence",
        "meta": {
            "title": spec_sequencia.get("titulo", spec_sequencia.get("journey_id", "Sequência")),
            "quality_profile": "showcase",
            "column_fit": "spread",
            "viewBox": calcular_viewbox(participantes, messages),
        },
        "participants": participantes,
        "messages": messages,
    }
    return arch, relatorio


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sequencia_spec", help="sequencia-<journey_id>_spec.json")
    parser.add_argument("catalogo", help="catalogo-componentes.json da mesma demanda")
    parser.add_argument("saida_html")
    parser.add_argument(
        "--archify-bin",
        default=str(ARCHIFY_BIN_PADRAO),
        help=f"Caminho pro archify.mjs (default: vendorizado em {ARCHIFY_BIN_PADRAO})",
    )
    parser.add_argument("--max-tentativas", type=int, default=6)
    args = parser.parse_args()

    spec_sequencia = carregar_json(args.sequencia_spec)
    catalogo = carregar_json(args.catalogo)
    arch, relatorio = montar_spec_archify(spec_sequencia, catalogo)

    for linha in relatorio:
        print(linha, file=sys.stderr)

    violacoes = checar_limite_palavras_sequencia(arch)
    if violacoes:
        print(f"[erro] {len(violacoes)} rótulo(s) acima do limite de {LIMITE_PALAVRAS_ROTULO} palavras — encurte no spec de origem antes de renderizar:", file=sys.stderr)
        for v in violacoes:
            print(f"  - {v}", file=sys.stderr)
        sys.exit(1)

    saida_html = Path(args.saida_html)
    saida_html.parent.mkdir(parents=True, exist_ok=True)
    caminho_spec_archify = saida_html.with_suffix(".architecture.json")

    resultado, tentativa = None, 0
    for tentativa in range(1, args.max_tentativas + 1):
        caminho_spec_archify.write_text(json.dumps(arch, indent=2, ensure_ascii=False), encoding="utf-8")
        resultado = validar(args.archify_bin, caminho_spec_archify, tipo="sequence")
        if resultado.get("ok") and (resultado.get("composition") or {}).get("status") == "pass":
            break
        diagnosticos = resultado.get("diagnostics", [])
        print(f"[tentativa {tentativa}] erros de validate: {len(diagnosticos)}", file=sys.stderr)
        mensagens_largura = [d for d in diagnosticos if "participant box" in (d.get("message") or "")]
        if not mensagens_largura:
            for d in diagnosticos:
                print(f"  - {d.get('message')}", file=sys.stderr)
            break
        arch["meta"]["viewBox"][0] = int(arch["meta"]["viewBox"][0] * 1.25)
    else:
        print("[aviso] limite de tentativas atingido.", file=sys.stderr)

    if not (resultado and resultado.get("ok") and (resultado.get("composition") or {}).get("status") == "pass"):
        print("[aviso] entregando mesmo assim, não convergiu a zero diagnósticos.", file=sys.stderr)

    entrega = entregar(args.archify_bin, caminho_spec_archify, saida_html, tipo="sequence")
    print(json.dumps(entrega, indent=2, ensure_ascii=False))
    if not entrega.get("ok"):
        sys.exit(1)


if __name__ == "__main__":
    main()
