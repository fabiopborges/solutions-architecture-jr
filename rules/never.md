# Nunca

Paradas duras. Se qualquer uma destas está prestes a acontecer, o fluxo para e escala para um humano em vez de continuar.

- Nunca um agente decide ou inventa algo fora da sua atividade específica. Se tiver dúvida sobre outra atividade, pergunta ao agente dono dela, nunca adivinha.
- Nunca uma dúvida entre dois agentes passa de 3 rodadas de ida e volta sem se resolver. Isso é loop infinito escondido, não uma dúvida real. Na 4ª rodada, para e escala para revisão humana (ver hook abaixo).
- Nunca um pacote de arquitetura sai como "entregue" sem as suposições e os trade-offs de cada decisão escritos.
- Nunca um agente usa dado, suposição ou contexto de uma demanda anterior numa demanda nova. Cada demanda começa com contexto limpo.
- Nunca um agente inventa, deriva ou abrevia o nome de uma demanda sozinho. O nome vem sempre explicitamente de quem pediu, confirmado pelo agente de Entendimento e Escopo antes de qualquer outra atividade começar, e é esse nome exato que vira a pasta `demandas/<nome-da-demanda>/`.
