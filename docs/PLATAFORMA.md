# Como o GreenFlight usa AWS, TiDB e Kiro

Texto curto para o pitch e para o SUBMISSION.md. "Usado" = está no código e roda na demo. "Próximo" = etapa seguinte já desenhada.

## TiDB Cloud Starter (sa-east-1)
- **Usado · SQL transacional.** `airportdb` original intacto (voos, reservas, aeroportos, aeronaves) mais as tabelas do produto: `eco_purchase` (passagens), `carbon_project`, `carbon_offset`, `green_reward`, `green_wallet`, `eco_search_log`.
- **Usado · Vector Search com auto-embedding.** `carbon_project.embedding` e `eco_knowledge.emb` são colunas `VECTOR(1024)` geradas por `EMBED_TEXT('tidbcloud_free/amazon/titan-embed-text-v2', …)` com índice HNSW. A frase do passageiro ("quero ajudar florestas brasileiras") vira a consulta `VEC_EMBED_COSINE_DISTANCE`, sem chave de API e sem código de embedding.
- **Usado · JSON.** `eco_purchase.chosen_over` guarda as alternativas rejeitadas na compra (base para o funil de decisão).
- **Usado · TTL.** `eco_search_log` expira sozinha em 30 dias (privacidade por padrão).
- **Usado · HTAP.** Hint `READ_FROM_STORAGE(TIFLASH)` nas contagens de ocupação sobre 617 mil reservas; com `ALTER TABLE booking SET TIFLASH REPLICA 1` a mesma base serve o checkout (linhas) e o dashboard ESG (colunas).
- **Próximo.** Branch do cluster por campanha ESG; Data Service expondo `/api/search` como endpoint REST para motores de busca de passagens; Chat2Query para o time de dados da companhia.

## AWS
- **Usado · Amazon Bedrock (ap-southeast-1).** Claude 3 Haiku explica a escolha de voo (por que este assento emite menos) e escolhe/justifica o projeto ambiental entre os top-3 da busca vetorial; resposta em JSON. Claude 3.5 Sonnet fica para respostas longas; Cohere multilingual disponível para embeddings fora do TiDB. Tudo com fallback determinístico se a chave faltar.
- **Usado · EC2 (sa-east-1).** Um processo só (FastAPI servindo o React buildado) na porta 8000, cabe na `t3.micro` de 913 MB; script `deploy.sh`.
- **Usado · S3.** Cada compra exporta o recibo JSON para `s3://…/latam-hackathon-007/receipts/` pela role da instância (trilha de auditoria da compensação).
- **Próximo.** API Gateway + Lambda para a API pública de emissão por trecho; EventBridge para recalcular emissões quando a ocupação muda; QuickSight sobre o TiDB para o ESG corporativo.

## Kiro
- **Usado · Specs.** `.kiro/specs/greenflight/requirements.md`, `design.md`, `tasks.md`: requisitos em EARS, arquitetura e tarefas com status.
- **Usado · Steering.** `product.md` (usuária, demo, decisões congeladas), `tech.md` (stack e regras: crases em `from`/`to`, lotes no Bedrock, sem segredos), `structure.md` (mapa do repo).
- **Usado · Hooks.** `.kiro/hooks/on-save-test.kiro.hook` roda o smoke test da API ao salvar arquivos do backend.
- **Usado · MCP.** `.kiro/settings/mcp.json` conecta o Kiro ao TiDB (`tidb-mcp-server`) para consultar o banco enquanto desenvolve.
- **Próximo.** Spec da fase 2 (integração com provedores certificados de crédito e API B2B para motores de busca).

## Metodologia de carbono (em uma frase)
Distância de grande círculo entre os aeroportos × 1,08 × assentos × fator por tipo de aeronave (kg CO₂/assento-km), dividida pelos passageiros a bordo agora; quem compra entra no denominador, então a emissão por pessoa muda em tempo real. Preço da compensação = toneladas × R$/t do projeto; Green Points = 100 + 1 por 100 kg.
