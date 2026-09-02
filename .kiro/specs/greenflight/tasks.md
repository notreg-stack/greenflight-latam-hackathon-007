# Tasks — GreenFlight

- [x] 1. Camada de dados com TiDB e fallback SQLite (`backend/db.py`), DDL `eco_*`, seed de conhecimento
- [x] 2. Metodologia de carbono (`backend/carbon.py`): haversine, fatores por aeronave, selo A–E
- [x] 3. API FastAPI (`backend/main.py`): airports, routes/suggested, search, purchase, explain, ask, stats, routes/greenest
- [x] 4. Bedrock (`backend/bedrock.py`): explicação da escolha, resposta com contexto vetorial, fallbacks
- [x] 5. Dashboard React (`frontend/src/App.jsx`): busca, cards com selo, ordenação, compra, recibo, pergunta
- [x] 6. Build do React servido pelo FastAPI na porta 8000
- [ ] 7. Apontar `.env` para o cluster TiDB Cloud do time e rodar `sql/setup_tidb.sql`
- [ ] 8. Colocar a chave Bedrock do time no `.env` e validar `/api/explain`
- [ ] 9. Deploy na EC2 (`deploy.sh`), conferir IP público e URL no `SUBMISSION.md`
- [ ] 10. Gravar demo de 2 minutos e comentar na issue "Entregas"
- [ ] 11. Próxima etapa: expor `/api/search` como API pública de emissão por trecho para motores de busca
