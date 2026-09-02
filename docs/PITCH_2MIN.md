# Pitch de 2 minutos · CO²mpensa Aí (GreenFlight) · time latam-hackathon-007

Mostre, não descreva. Uma pessoa fala, outra opera a tela já aberta em `http://<ip-da-ec2>:8000` (ou local).

**0:00 – 0:15 · Problema.** "Comprar passagem leva segundos. Saber quanto carbono aquele assento custa, escolher melhor e compensar ainda é invisível, e a companhia não captura nada disso."

**0:15 – 0:45 · Busca por carbono.** Clicar em uma rota com voos na semana. Apontar: selo A–E, kg CO₂ por passageiro, ocupação em tempo real, "escolha verde" e "menor preço". Ordenar por carbono. Frase: "a emissão por pessoa muda com a ocupação do voo; quem compra entra no denominador."

**0:45 – 1:05 · Compra.** Comprar o voo verde. Ler o recibo: kg evitados contra a pior alternativa, ocupação já atualizada, explicação gerada pelo Bedrock.

**1:05 – 1:35 · Compensação com IA.** Digitar "quero ajudar florestas brasileiras" e clicar em Recomendar projeto. Frase: "a busca semântica roda dentro do TiDB, com `EMBED_TEXT` gerando os vetores; o Bedrock escolhe entre os três e explica." Clicar em Compensar. Mostrar Green Points e o próximo benefício.

**1:35 – 1:50 · Companhia aérea.** Abrir Dashboard ESG: adesão, CO₂ compensado, projetos mais escolhidos, adesão por rota, rotas mais limpas da semana.

**1:50 – 2:00 · Fechamento.** "TiDB Cloud em São Paulo guarda transação, vetor e analytics na mesma base; Bedrock em Singapura explica e recomenda; roda numa EC2 de 913 MB; specs no Kiro. Próxima etapa: expor a emissão por trecho como API para os motores de busca de passagens."

**Se perguntarem como calculamos:** distância de grande círculo × 1,08 × assentos × fator por tipo de aeronave, dividido pelos passageiros a bordo agora. Fatores na ordem de grandeza ICAO/DEFRA, declarados em `backend/carbon.py`; em produção entram combustível, classe e metodologia certificada.

**Se perguntarem sobre o dado:** o dataset não tem atrasos nem histórico real de passageiros; por isso o produto se apoia no que é consistente (grade, geografia, aeronave, ocupação) e não promete previsão.
