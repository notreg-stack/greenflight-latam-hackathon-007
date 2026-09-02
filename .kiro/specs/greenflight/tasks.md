# Tasks — GreenFlight

- [x] 1. Camada de dados TiDB + fallback SQLite (`backend/db.py`), tabelas `eco_*`, seed de conhecimento
- [x] 2. Metodologia de carbono (`backend/carbon.py`): haversine, fatores por aeronave, ocupação em tempo real, selo A–E
- [x] 3. API de busca e compra (`backend/main.py`): airports, search, purchase, explain, ask, stats, greenest
- [x] 4. GreenFlight (`backend/greenflight.py`): `carbon_project` com VECTOR/EMBED_TEXT, `carbon_offset`, `green_reward`, `green_wallet`, ESG
- [x] 5. Bedrock (`backend/bedrock.py`): explicação da escolha, recomendação de projeto em JSON, fallbacks
- [x] 6. Dashboard React: busca com selo de carbono, checkout, oferta de compensação, projetos recomendados, rewards, ESG
- [x] 7. Smoke test (`scripts/smoke.sh`) e hook do Kiro
- [ ] 8. `.env` com TiDB Cloud do time + `sql/setup_tidb.sql` conferido no SQL Editor
- [ ] 9. Chave Bedrock no `.env`; validar `/api/explain` e `/api/carbon/projects/recommend` com Claude
- [ ] 10. `deploy.sh` na EC2, IP público no `SUBMISSION.md`, vídeo de 2 min, comentário na issue "Entregas"
- [ ] 11. Fase 2: API pública de emissão por trecho para motores de busca; provedores certificados de crédito
