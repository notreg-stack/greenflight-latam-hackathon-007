# GreenFlight — estrutura do repositório

```
backend/
  main.py        API FastAPI (busca, compra, explicação, pergunta, stats, rotas) + serve frontend/dist
  db.py          conexão TiDB ou SQLite, DDL das tabelas eco_*, busca vetorial com fallback
  carbon.py      metodologia de emissão (haversine, fatores por aeronave, selo A–E)
  bedrock.py     Converse API (Haiku/Sonnet), embeddings Cohere, fallbacks sem chave
  requirements.txt · .env.example
frontend/
  src/App.jsx    dashboard: busca, lista com selo de carbono, compra, recibo, pergunta ao GreenFlight
  src/App.css    tema escuro verde
  vite.config.js proxy /api em dev
sql/setup_tidb.sql  DDL das tabelas eco_* e exemplos de consulta vetorial
docs/               arquitetura, metodologia de carbono, deploy na EC2, uso da plataforma
.kiro/              specs, steering, hooks e MCP do Kiro
deploy.sh           passo a passo executável para a EC2
SUBMISSION.md       template oficial do evento preenchido
```
