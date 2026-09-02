# SUBMISSION.md

## Time
Nome do time: latam-hackathon-007 · GreenFlight
Integrantes: (preencher)

## Pitch
GreenFlight mostra, no momento da compra, quanto CO₂ cada assento custa com a ocupação real do voo, deixa o passageiro escolher o trecho por carbono além de preço e rota, e transforma a compensação em projeto recomendado por IA, Green Points e dados ESG para a companhia.

## O que faz
O passageiro busca origem e destino no dataset airportdb; cada voo recebe selo A–E, kg CO₂ por passageiro (distância × aeronave ÷ ocupação, recalculado a cada compra) e preço. No checkout, o app oferece a compensação, o passageiro descreve o projeto que quer apoiar, o TiDB Vector Search acha os projetos mais próximos e o Bedrock recomenda e explica; ao confirmar, a compensação vira Green Points na carteira e alimenta o dashboard ESG da companhia (adesão, CO₂ compensado, projetos, rotas).

## Stack — marque o que você realmente usou
- [x] TiDB Cloud Starter na AWS sa-east-1
- [x] Busca vetorial no TiDB (coluna VECTOR ou EMBED_TEXT)
- [x] Amazon Bedrock (ap-southeast-1)
- [ ] Publicado na AWS  -> URL no ar: http://<ip-publico-da-ec2>:8000
- [x] Construído com Kiro (.kiro/ commitado)

## Onde olhar
Conexão/consultas TiDB:  backend/db.py · backend/main.py · backend/greenflight.py · sql/setup_tidb.sql
Busca vetorial:          backend/greenflight.py (search_projects) · backend/db.py (knowledge_search) · sql/setup_tidb.sql
Chamadas ao Bedrock:     backend/bedrock.py

## Demo
Link do vídeo de 2 minutos ou da aplicação no ar: (preencher)

## Como rodar
```bash
cd backend && python3.11 -m venv .venv && ./.venv/bin/pip install -r requirements.txt
cp .env.example .env   # preencha TiDB e chave Bedrock; vazio = modo local com o dump oficial
cd ../frontend && npm ci && npm run build
cd ../backend && ./.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
```

## O que faríamos a seguir
API pública de emissão por trecho (`/api/search`) para motores de busca de passagens; integração com provedores certificados de crédito; incentivos dinâmicos por rota e ocupação; personalização da recomendação por histórico do passageiro (memória vetorial no TiDB).
