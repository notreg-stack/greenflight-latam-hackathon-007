# CO²mpensa Aí — compense sua pegada com um clique

<p align="center"><img src="docs/brand/co2mpensa-ai-wordmark.png" width="320" alt="CO²mpensa Aí"></p>

Codinome do projeto: GreenFlight.

Hackathon TiDB × AWS · São Paulo · 02/09/2026 · time **latam-hackathon-007**

O passageiro busca e compra a passagem vendo a pegada de carbono de cada trecho (ocupação real, aeronave, distância) ao lado do preço e do horário; no checkout compensa a emissão em um projeto recomendado por IA, ganha Green Points e a companhia recebe dados ESG.

- **Frontend:** React + Vite (`frontend/`)
- **Backend:** FastAPI (`backend/`) servindo o React buildado numa porta só
- **Banco:** TiDB Cloud Starter (SQL + Vector Search com `EMBED_TEXT`), fallback SQLite com o dump oficial
- **IA:** Amazon Bedrock (Claude 3 Haiku / 3.5 Sonnet) em ap-southeast-1
- **Infra:** EC2 sa-east-1 (`deploy.sh`), S3 para recibos
- **Kiro:** specs, steering, hooks e MCP em `.kiro/`

Identidade visual: [DESIGN.md](DESIGN.md) · logo em `docs/brand/` e `frontend/public/`.

Docs: [docs/PLATAFORMA.md](docs/PLATAFORMA.md) (o que cada recurso faz) · [docs/ARQUITETURA_GREENFLIGHT.md](docs/ARQUITETURA_GREENFLIGHT.md) (visão completa) · [SUBMISSION.md](SUBMISSION.md)

## Rodar local
```bash
cd backend && python3 -m venv .venv && chop ./.venv/bin/pip install -r requirements.txt && cp .env.example .env
cd ../frontend && chop npm ci && chop npm run build
cd ../backend && ./.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
```
Abra http://localhost:8000. Com `.env` vazio o app baixa o dump (10 MB) e roda em SQLite; preencha `TIDB_HOST/USER/PASSWORD` para usar o TiDB Cloud e `AWS_BEARER_TOKEN_BEDROCK` para o Bedrock.

## Deploy na EC2
`bash deploy.sh` via Session Manager (porta 8000, bind 0.0.0.0). Veja `docs/PLATAFORMA.md`.
