# Skill: Plano de Testes e Qualidade da Arquitetura

## Quando usar
Depois que o Desenho de Arquitetura existe. Esta skill não testa código, testa se o DESENHO aguenta o que o escopo prometeu, é uma checagem de arquitetura, não de implementação.

## Dono
O agente "Testes e Qualidade" é o dono desta atividade. Qualquer agente com dúvida sobre se o desenho atende um requisito não funcional, ou onde estão os pontos únicos de falha, pergunta a este agente em vez de adivinhar (regra de [[rules/never]]).

## Passos
1. Leia os requisitos não funcionais do documento de entendimento e escopo, e para cada um, dê um veredito sobre o desenho de arquitetura: atende, não atende, ou atende parcial. Nenhum requisito não funcional fica sem veredito.
2. Revise os riscos e pontos fracos que o Desenho de Arquitetura já apontou na saída dele, aprofundando em vez de repetir do zero. Procure especificamente por pontos únicos de falha (um componente sem redundância cuja queda derruba tudo) e dependências críticas.
3. Confirme se a integração com sistemas legados (via SOA/BPEL) foi de fato pensada no desenho, e não só assumida como "vai funcionar". Se não foi, isso vira um "não atende" ou "atende parcial" no veredito.
4. Para cada veredito de "não atende" ou "atende parcial", registre o que precisaria mudar no desenho para virar "atende", e sinalize para [[agents/desenho-de-arquitetura/AGENT]].

## Artefato de saída
Um documento `demandas/<nome-da-demanda>/qualidade.md` com: tabela de requisito não funcional x veredito, pontos únicos de falha e dependências críticas encontrados, status da integração com legado, e o que falta para cada veredito não pleno virar "atende".

## Como é bem feito
Cada requisito não funcional do escopo tem um veredito explícito, nenhum fica sem resposta, e quem ler o documento sabe exatamente onde o desenho ainda não aguenta o que foi prometido.
