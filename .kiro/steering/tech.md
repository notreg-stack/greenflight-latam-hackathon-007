# GreenFlight — steering técnico

## Stack
- **Banco:** TiDB Cloud Starter em `sa-east-1` (dataset `airportdb` + tabelas `eco_*`). Fallback local: SQLite carregado do dump oficial, para a demo nunca depender de rede.
- **Backend:** Python 3.11+, FastAPI, pymysql (TLS obrigatório), boto3 ≥ 1.39. Uma porta só (8000) serve API e o React buildado.
- **Frontend:** React 19 + Vite, sem framework de UI, CSS próprio. Em dev usa proxy `/api` → 8000.
- **IA:** Amazon Bedrock em `ap-southeast-1`: Claude 3 Haiku (explicações e respostas), Claude 3.5 Sonnet reservado para o pitch, Cohere multilingual para embeddings quando necessário.
- **Vetor:** `EMBED_TEXT('tidbcloud_free/amazon/titan-embed-text-v2', …)` em coluna `VECTOR(1024)` gerada, índice HNSW, consulta com `VEC_EMBED_COSINE_DISTANCE`.
- **Deploy:** EC2 `t3.micro` (913 MB) em `sa-east-1`, `setsid nohup uvicorn … --host 0.0.0.0 --port 8000`. Recibos de compra vão para o prefixo S3 do time pela role da instância.

## Regras
- `from` e `to` são palavras reservadas: sempre entre crases.
- Nunca chamar o Bedrock dentro de loop por linha; agrupar em lotes.
- Segredos só no `.env` (git-ignored); `.env.example` commitado.
- Toda consulta SQL precisa rodar em TiDB e em SQLite; diferenças ficam em `backend/db.py` (`PH` e DDL).
- Sem torch, sem embeddings locais: a EC2 tem 913 MB.
- Nunca exibir nome completo, passaporte, e-mail ou telefone do dataset na interface.
