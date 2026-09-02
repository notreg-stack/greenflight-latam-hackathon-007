# Requirements — GreenFlight

## Introdução
Dashboard de busca e compra de passagens que mostra a pegada de carbono de cada trecho, calculada com a ocupação real do voo, para que a decisão use carbono além de preço e rota. Base: dataset `airportdb` (semana de 02 a 08/06/2015) no TiDB Cloud.

## Requisitos

### R1 — Buscar voos
**User story:** como viajante, quero buscar voos por origem, destino e data para comparar opções.
- 1.1 QUANDO o usuário digita 2+ letras em origem ou destino ENTÃO o sistema DEVE sugerir aeroportos por cidade, IATA, ICAO ou nome, com aeroportos brasileiros primeiro.
- 1.2 QUANDO a busca é enviada ENTÃO o sistema DEVE listar voos do par informado na data escolhida ou, se não houver, na semana inteira, avisando o usuário.
- 1.3 O sistema DEVE oferecer rotas com voos na semana como atalhos de um clique.

### R2 — Calcular a pegada de carbono em tempo real
- 2.1 Para cada voo o sistema DEVE calcular distância de grande círculo entre os aeroportos e aplicar fator de desvio de 8%.
- 2.2 O sistema DEVE estimar a emissão do voo por tipo de aeronave (kg CO2 por assento-km) e dividir pelos passageiros a bordo (reservas do dataset mais compras feitas no app).
- 2.3 O sistema DEVE mostrar selo A–E, kg CO2 por passageiro, equivalência em árvores, ocupação e a emissão por passageiro caso o usuário compre.
- 2.4 QUANDO uma compra é confirmada ENTÃO a ocupação e o kg/pax dos resultados DEVEM refletir a compra imediatamente.

### R3 — Comprar
- 3.1 O usuário DEVE poder comprar um voo informando nome e e-mail opcional.
- 3.2 O sistema DEVE registrar a compra em `eco_purchase` com preço, CO2 por passageiro, CO2 evitado contra a pior alternativa listada e as alternativas rejeitadas (JSON).
- 3.3 O sistema NÃO DEVE vender assento em voo lotado.
- 3.4 SE o app roda na EC2 ENTÃO o recibo DEVE ser exportado para o prefixo S3 do time; fora da AWS, silenciosamente ignorado.

### R4 — Explicar e responder
- 4.1 Após a compra o sistema DEVE explicar em linguagem natural (Bedrock) por que a escolha é ou não a melhor em carbono.
- 4.2 O usuário DEVE poder fazer perguntas livres; o sistema DEVE responder com base na tabela `eco_knowledge` consultada por busca vetorial (`EMBED_TEXT`) no TiDB, com fallback por palavra no modo local.
- 4.3 SE o Bedrock não estiver disponível ENTÃO o sistema DEVE responder com texto determinístico e sinalizar isso.

### R5 — Indicadores
- 5.1 O cabeçalho DEVE mostrar compras, CO2 evitado acumulado, buscas e o modo de banco (TiDB ou local).
- 5.2 O sistema DEVE listar as rotas mais limpas da semana (média de kg/pax) tocando o Brasil.

### R6 — Plataforma
- 6.1 Dados no TiDB Cloud Starter em `sa-east-1`; modo local só como fallback de demo.
- 6.2 Deploy na EC2 do time em `sa-east-1`, porta 8000, bind `0.0.0.0`.
- 6.3 Nenhum segredo no repositório.
### R7 — Compensação no checkout (GreenFlight)
- 7.1 Após a compra o sistema DEVE mostrar a emissão do assento, o preço da compensação (toneladas × R$/t do projeto) e os Green Points.
- 7.2 QUANDO o passageiro descreve o projeto que quer apoiar ENTÃO o sistema DEVE buscar os 3 projetos mais próximos em `carbon_project` por busca vetorial (`EMBED_TEXT`) e pedir ao Bedrock a recomendação com justificativa em JSON.
- 7.3 QUANDO a compensação é confirmada ENTÃO o sistema DEVE gravar `carbon_offset`, creditar `green_reward` e atualizar `green_wallet` na mesma transação lógica.
- 7.4 A tela de rewards DEVE mostrar pontos, próximo benefício, CO₂ compensado e viagens compensadas.

### R8 — Dashboard ESG da companhia
- 8.1 O sistema DEVE expor adesão (compensações ÷ passagens), CO₂ compensado, participantes, projetos, Green Points e valor destinado.
- 8.2 O sistema DEVE listar projetos mais escolhidos e adesão por rota.