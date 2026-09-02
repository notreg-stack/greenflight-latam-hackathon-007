# CO²mpensa Aí (GreenFlight) — steering de produto

**Marca:** CO²mpensa Aí · tagline "Compense sua pegada com um clique" · identidade em `DESIGN.md` (azul do voo, verde da folha, laranja da ação, fundo claro).

**Pitch em uma linha:** o comprador de passagem escolhe o trecho vendo, ao lado do preço e do horário, quanto CO2 aquele assento custa agora, com a ocupação real do voo.

**Usuário nomeado:** Ana, viajante que compra a própria passagem e quer decidir com carbono, não só com preço.

**O que a demo mostra (2 minutos):**
1. Busca Ituiutaba → Boa Vista na semana do dataset.
2. Lista ordenada por carbono: selo A–E, kg CO2 por passageiro, ocupação, preço, "escolha verde" e "menor preço".
3. Compra: a ocupação sobe na hora, o kg/pax cai, o recibo diz quanto CO2 foi evitado contra a pior alternativa.
4. Explicação em linguagem natural (Bedrock) e pergunta livre respondida com busca vetorial no TiDB.

**Decisões que não mudam durante o sprint:**
- Emissão = distância de grande círculo × 1,08 × assentos × fator por assento-km do tipo de aeronave, dividida pelos passageiros a bordo.
- "Tempo real" significa ocupação atualizada a cada compra feita no app (tabela `eco_purchase` somada a `booking`).
- Sem coluna de atraso no dataset; o produto não promete previsão de atraso.
- Próxima etapa (fora do sprint): expor `/api/search` como API de emissão por trecho para motores de busca de passagens.

**Time:** latam-hackathon-007.
