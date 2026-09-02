# Tasks — GreenFlight

- [x] 1. Camada de dados TiDB + fallback SQLite (`backend/db.py`), tabelas `eco_*`, seed de conhecimento
- [x] 2. Metodologia de carbono (`backend/carbon.py`): haversine, fatores por aeronave, ocupação em tempo real, selo A–E
- [x] 3. API de busca e compra (`backend/main.py`): airports, search, purchase, explain, ask, stats, greenest
- [x] 4. GreenFlight (`backend/greenflight.py`): `carbon_project` com VECTOR/EMBED_TEXT, `carbon_offset`, `green_reward`, `green_wallet`, ESG
- [x] 5. Bedrock (`backend/bedrock.py`): explicação da escolha, recomendação de projeto em JSON, fallbacks
- [x] 6. Dashboard React: busca com selo de carbono, checkout, oferta de compensação, projetos recomendados, rewards, ESG
- [x] 7. Smoke test (`scripts/smoke.sh`), hook do Kiro e vídeo de demo gravado por `scripts/record_demo.mjs`
- [x] 7b. Regras de negócio: pontos e benefícios logo após a compra, ticker de emissão em tempo real (`/api/live`), análise ESG por trecho com valor por tonelada (`/api/esg/routes`)
- [ ] 8. `.env` com TiDB Cloud do time + `sql/setup_tidb.sql` conferido no SQL Editor
- [x] 9. Chave Bedrock do time no `.env`; `/api/explain` e `/api/carbon/projects/recommend` validados com Claude 3 Haiku em ap-southeast-1
- [ ] 10. `deploy.sh` na EC2 (exige login no console + MFA) e IP público no `SUBMISSION.md`; enquanto isso, demo online por túnel Cloudflare
- [ ] 11. Fase 2: API pública de emissão por trecho para motores de busca; provedores certificados de crédito
