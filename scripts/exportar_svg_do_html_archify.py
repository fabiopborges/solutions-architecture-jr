#!/usr/bin/env python3
"""Extrai um SVG standalone de um HTML entregue pelo ArchiFy.

O HTML do ArchiFy é autocontido, mas pesa centenas de KB (fontes, toolbar,
scripts de navegação guiada) e não pode ser embutido num README. Este script
tira de dentro dele só o `<svg>` renderizado e o CSS de que esse SVG depende,
e grava um `.svg` standalone — vetorial, leve, e com tema claro/escuro via
`prefers-color-scheme` (o HTML original resolve tema por `data-theme` no
`<html>`, que não existe num SVG solto).

O script não desenha nada: toda a geometria já foi decidida pelo ArchiFy. É
uma extração mecânica, sem escolha de layout, cor ou conteúdo.

Uso:
    python3 exportar_svg_do_html_archify.py ENTRADA.html SAIDA.svg
    python3 exportar_svg_do_html_archify.py --lote DIR_SAIDA ENTRADA1.html ...
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Fonte usada pelo HTML do ArchiFy (`body`), que o SVG herdava por cascata.
# Num SVG standalone não há `body`, então a pilha precisa ser declarada aqui.
PILHA_DE_FONTE = (
    "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, "
    "'DejaVu Sans Mono', 'Liberation Mono', monospace"
)

# Regras cujo seletor toca qualquer um destes trechos são da camada de
# visualização do HTML (toolbar, cards, hover, narrativa guiada), não do
# desenho em si — um SVG estático não tem nenhuma delas.
SELETOR_DESCARTADO = (
    "html[",
    ".diagram-container",
    ".toolbar",
    ".card",
    ".header",
    ".guided",
    ".share-",
    ":hover",
    ":focus",
    "[data-story",
    "[data-detail-level",
    "[data-share",
)


def _extrair_svg(html: str) -> str:
    inicio = html.find("<svg")
    fim = html.find("</svg>")
    if inicio == -1 or fim == -1:
        raise SystemExit("[erro] nenhum <svg> encontrado no HTML de entrada")
    return _xml_valido(html[inicio : fim + len("</svg>")])


def _xml_valido(svg: str) -> str:
    """Dá valor aos atributos booleanos e troca entidades só de HTML.

    O SVG do ArchiFy vive dentro de um HTML, onde `<text data-detail-anchor>`
    é legal. Num `.svg` solto o parser é XML, e recusa o arquivo inteiro no
    primeiro atributo sem valor. Mesma coisa para entidades como `&nbsp;`,
    que XML não conhece.
    """

    # Um atributo por vez, sempre a partir do fim do anterior — varrer a lista
    # inteira de uma vez confundiria um valor com espaço (ex: `d="M 0 0 L 8 8"`)
    # com um atributo booleano.
    atributo = re.compile(r"""\s+([a-zA-Z_:][-\w:.]*)(\s*=\s*("[^"]*"|'[^']*'|[^\s>]+))?""")

    def normalizar_tag(achado: re.Match[str]) -> str:
        nome, atributos, fecho = achado.group(1), achado.group(2), achado.group(3)
        partes: list[str] = []
        posicao = 0
        while posicao < len(atributos):
            par = atributo.match(atributos, posicao)
            if par is None:
                partes.append(atributos[posicao:])
                break
            partes.append(f" {par.group(1)}" + (par.group(2) if par.group(2) else '=""'))
            posicao = par.end()
        return f"<{nome}{''.join(partes)}{fecho}>"

    svg = re.sub(r"<([a-zA-Z][-\w:.]*)((?:[^<>\"]|\"[^\"]*\")*?)(/?)>", normalizar_tag, svg)
    return svg.replace("&nbsp;", "&#160;")


def _extrair_css(html: str) -> str:
    blocos = re.findall(r"<style[^>]*>(.*?)</style>", html, re.S)
    if not blocos:
        raise SystemExit("[erro] nenhum <style> encontrado no HTML de entrada")
    return "\n".join(blocos)


def _atributo_da_raiz(svg: str, nome: str) -> str | None:
    achado = re.search(rf'{nome}="([^"]*)"', svg[: svg.find(">")])
    return achado.group(1) if achado else None


def _classes_usadas(svg: str) -> set[str]:
    usadas: set[str] = set()
    for valor in re.findall(r'class="([^"]+)"', svg):
        usadas.update(valor.split())
    return usadas


def _declara_variaveis(corpo: str) -> bool:
    """Distingue um bloco de tema (`--cor: #fff`) de uma regra que só lê a
    variável (`fill: var(--cor)`) — as duas contêm `--`."""
    return re.search(r"(?:^|[;{\s])--[\w-]+\s*:", corpo) is not None


def _percorrer_css(css: str) -> list[tuple[str, str, list]]:
    """Quebra a folha de estilo em blocos, sem depender de indentação.

    Devolve uma lista de `(tipo, prelúdio, filhos)`, onde tipo é `"regra"`
    (filhos é o corpo, como texto) ou `"at"` (uma `@media`/`@supports`, cujos
    filhos são outros blocos). Regex sozinho não dá conta: seletores ocupam
    várias linhas e regras aninhadas dentro de `@media` têm chaves em pares.
    """
    blocos: list[tuple[str, str, list]] = []
    posicao, prelude_inicio = 0, 0
    while posicao < len(css):
        caractere = css[posicao]
        if caractere == "/" and css.startswith("/*", posicao):
            posicao = css.find("*/", posicao) + 2
            continue
        if caractere == ";":  # @import e afins, sem corpo
            prelude_inicio = posicao = posicao + 1
            continue
        if caractere != "{":
            posicao += 1
            continue
        prelude = css[prelude_inicio:posicao]
        profundidade, fim = 1, posicao + 1
        while fim < len(css) and profundidade:
            if css.startswith("/*", fim):
                fim = css.find("*/", fim) + 2
                continue
            profundidade += {"{": 1, "}": -1}.get(css[fim], 0)
            fim += 1
        corpo = css[posicao + 1 : fim - 1]
        prelude_limpo = " ".join(re.sub(r"/\*.*?\*/", " ", prelude, flags=re.S).split())
        if prelude_limpo.startswith("@"):
            filhos = _percorrer_css(corpo) if "{" in corpo else []
            blocos.append(("at", prelude_limpo, filhos))
        else:
            blocos.append(("regra", prelude_limpo, corpo))
        prelude_inicio = posicao = fim
    return blocos


def _blocos_de_variaveis(css: str, preset: str) -> tuple[str, str]:
    """Devolve (declarações do tema escuro, declarações do tema claro).

    O ArchiFy declara as variáveis por preset em blocos de nível superior
    (`:root, [data-theme="dark"]` para o preset `classic`, e
    `[data-preset="<preset>"][data-theme="..."]` para os demais).
    """
    escuro: list[str] = []
    claro: list[str] = []
    for tipo, seletor, corpo in _percorrer_css(css):
        if tipo != "regra" or not _declara_variaveis(corpo):
            continue
        if preset == "classic":
            pertence = "data-preset" not in seletor
        else:
            pertence = f'data-preset="{preset}"' in seletor
        if not pertence:
            continue
        if 'data-theme="light"' in seletor:
            claro.append(corpo.strip())
        elif ":root" in seletor or 'data-theme="dark"' in seletor:
            escuro.append(corpo.strip())
    if not escuro:
        raise SystemExit(f"[erro] nenhum bloco de variáveis encontrado para o preset {preset!r}")
    return "\n".join(escuro), "\n".join(claro)


def _regras_do_desenho(css: str, classes: set[str], preset: str) -> str:
    """Filtra as regras de CSS que o SVG extraído realmente usa."""
    def filtrar(blocos: list[tuple[str, str, list]]) -> list[str]:
        mantidas: list[str] = []
        for tipo, prelude, corpo in blocos:
            if tipo == "at":
                # `@keyframes` e afins não têm seletor nos filhos; só entram
                # `@media`/`@supports` cujas regras internas sobrevivem ao filtro.
                if not prelude.startswith(("@media", "@supports")):
                    continue
                internas = filtrar(corpo)
                if internas:
                    corpo_interno = "\n".join(internas)
                    mantidas.append(f"{prelude} {{\n{corpo_interno}\n}}")
                continue
            if not prelude or _declara_variaveis(corpo):
                continue
            if any(trecho in prelude for trecho in SELETOR_DESCARTADO):
                continue
            if "data-preset" in prelude and f'data-preset="{preset}"' not in prelude:
                continue
            if not any(re.search(rf"\.{re.escape(classe)}\b", prelude) for classe in classes):
                continue
            # O seletor pode ter sido escrito contra o SVG dentro da página.
            prelude = prelude.replace(f'svg[data-preset="{preset}"]', "svg")
            mantidas.append(f"{prelude} {{{corpo.rstrip()}\n}}")
        return mantidas

    return "\n".join(filtrar(_percorrer_css(css)))


def converter(html: str) -> str:
    svg = _extrair_svg(html)
    css = _extrair_css(html)
    preset = _atributo_da_raiz(svg, "data-preset") or "classic"

    escuro, claro = _blocos_de_variaveis(css, preset)
    regras = _regras_do_desenho(css, _classes_usadas(svg), preset)

    estilo = f"""<style>
    svg {{
{escuro}
      background: var(--bg);
      font-family: {PILHA_DE_FONTE};
    }}
    @media (prefers-color-scheme: light) {{
      svg {{
{claro}
      }}
    }}
{regras}
  </style>"""

    # `xmlns` é obrigatório num SVG standalone (num HTML ele é implícito), e o
    # `width`/`height` derivado do viewBox evita que o leitor renderize o
    # desenho em tamanho arbitrário.
    largura, altura = (_atributo_da_raiz(svg, "viewBox") or "0 0 800 600").split()[2:4]
    abertura_original = svg[: svg.find(">") + 1]
    abertura_nova = abertura_original.replace(
        "<svg",
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{largura}" height="{altura}"',
        1,
    )
    svg = abertura_nova + svg[svg.find(">") + 1 :]
    return svg.replace(abertura_nova, abertura_nova + "\n  " + estilo, 1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("entradas", nargs="+", type=Path, help="HTML(s) entregue(s) pelo ArchiFy")
    parser.add_argument("saida", nargs="?", type=Path, help="arquivo .svg de saída (uma entrada só)")
    parser.add_argument("--lote", type=Path, help="diretório de saída; grava um .svg por entrada")
    args = parser.parse_args()

    if args.lote is None:
        if args.saida is None or len(args.entradas) != 1:
            parser.error("informe ENTRADA.html SAIDA.svg, ou use --lote DIR com uma ou mais entradas")
        pares = [(args.entradas[0], args.saida)]
    else:
        entradas = list(args.entradas) + ([args.saida] if args.saida else [])
        args.lote.mkdir(parents=True, exist_ok=True)
        pares = [(entrada, args.lote / f"{entrada.stem}.svg") for entrada in entradas]

    for entrada, saida in pares:
        svg = converter(entrada.read_text(encoding="utf-8"))
        saida.write_text(svg, encoding="utf-8")
        print(f"[ok] {entrada.name} -> {saida} ({len(svg) / 1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
