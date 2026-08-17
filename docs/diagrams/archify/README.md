# Diagramas C4 gerados pelo pipeline (ArchiFy)

Estes SVGs **não foram desenhados à mão**. Saíram do agente [Geração de Diagramas C4](../../../agents/geracao-diagramas/AGENT.md) rodando sobre a demanda `projeto-agentes-arquitetura-de-solucoes-junior-16-08-2026` — o OS aplicado a si mesmo, com `desenho.md`, `dados.md` e as jornadas do próprio time como fonte. Cada `.architecture.json` aqui é o spec exato que o ArchiFy renderizou; o `.svg` é a versão standalone desse render.

Os diagramas de `docs/diagrams/*.mmd` (camadas do OS, execução vs. referência) continuam sendo Mermaid escrito à mão — são vistas conceituais do repositório, não saída do pipeline.

## Como cada arquivo foi gerado

```bash
# 1. spec -> HTML interativo (o entregável normal do agente)
node skills/vendors/archify/archify/bin/archify.mjs deliver architecture \
  docs/diagrams/archify/c4-contexto.architecture.json saida.html --quality showcase

# 2. HTML -> SVG standalone, versionável e embutível no README
python3 scripts/exportar_svg_do_html_archify.py saida.html docs/diagrams/archify/c4-contexto.svg
```

Trocar `architecture` por `sequence` nos arquivos `sequencia-*` (o nome mantém o sufixo `.architecture.json` como no diretório de origem, mas o `diagram_type` interno é `sequence`).

## Limites conhecidos destes SVGs

- **Tema.** Seguem `prefers-color-scheme` do sistema de quem lê, não o tema do GitHub — num `<img>` a página hospedeira não consegue impor o tema.
- **Sem interação.** O HTML original tem navegação guiada (`meta.views`), zoom e níveis de detalhe; nada disso sobrevive num SVG estático. Para revisar a fundo, gere o HTML.
- **Simplificações de layout.** Alguns diagramas omitem arestas ou fronteiras que o roteador do ArchiFy não conseguiu rotear, sempre por limitação de layout e nunca por decisão de conteúdo. O registro completo do que ficou de fora, e por quê, está no `NOTAS.md` da demanda de origem (não versionado, `demandas/` está no `.gitignore`).
