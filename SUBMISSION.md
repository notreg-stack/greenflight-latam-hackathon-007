# SUBMISSION.md

## Time
Nome do time: latam-hackathon-007 · CO²mpensa Aí (codinome GreenFlight)
Repositório: https://github.com/notreg-stack/greenflight-latam-hackathon-007
Integrantes: time latam-hackathon-007 (nomes a preencher pelo time)

## Pitch
CO²mpensa Aí ("Compense sua pegada com um clique") mostra, no momento da compra, quanto CO₂ cada assento custa com a ocupação real do voo, deixa o passageiro escolher o trecho por carbono além de preço e rota, e transforma a compensação em projeto recomendado por IA, Green Points e dados ESG para a companhia.

## O que faz
O passageiro busca origem e destino no dataset airportdb; cada voo recebe selo A–E, kg CO₂ por passageiro (distância × aeronave ÷ ocupação, recalculado a cada compra) e preço, com um ticker de emissão em tempo real dos voos do dia. No checkout, o app mostra os Green Points e o próximo benefício, oferece a compensação com o valor por tonelada, o passageiro descreve o projeto que quer apoiar, o TiDB Vector Search acha os projetos mais próximos e o Bedrock recomenda e explica; ao confirmar, a compensação vira Green Points na carteira. O dashboard ESG da companhia mostra adesão, CO₂ compensado, projetos, adesão por rota e a análise do airportdb inteiro: emissão por trecho, toneladas na semana e valor da compensação por tonelada.

## Stack — marque o que você realmente usou
- [ ] TiDB Cloud Starter na AWS sa-east-1 (cluster e conexão ainda não validados)
- [ ] Busca vetorial no TiDB (implementada no código; execução no cluster ainda não validada)
- [x] Amazon Bedrock (ap-southeast-1)
- [ ] Publicado na AWS  -> URL no ar: (EC2 pendente; demo online em https://crimes-producers-ferrari-violation.trycloudflare.com)
- [x] Construído com Kiro (`tidb-hackathon/.kiro/` commitado)

## Onde olhar
Conexão/consultas TiDB:  tidb-hackathon/backend/db.py · tidb-hackathon/backend/main.py · tidb-hackathon/backend/greenflight.py · tidb-hackathon/sql/setup_tidb.sql
Busca vetorial:          tidb-hackathon/backend/greenflight.py (search_projects) · tidb-hackathon/backend/db.py (knowledge_search) · tidb-hackathon/sql/setup_tidb.sql
Chamadas ao Bedrock:     tidb-hackathon/backend/bedrock.py

## Demo
Link do vídeo de 2 minutos ou da aplicação no ar:
- Vídeo: https://github.com/notreg-stack/greenflight-latam-hackathon-007/raw/main/tidb-hackathon/docs/demo/greenflight-demo.mp4
- Aplicação no ar (túnel para a demo, válido durante o evento): https://crimes-producers-ferrari-violation.trycloudflare.com

## Como rodar
```bash
cd tidb-hackathon
cd backend && python3.11 -m venv .venv && ./.venv/bin/pip install -r requirements.txt
cp .env.example .env   # preencha TiDB e a chave Bedrock do time; TIDB_HOST vazio = modo local com o dump oficial
cd ../frontend && npm ci && npm run build   # opcional: o build já vem commitado em frontend/dist
cd ../backend && ./.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
```
Deploy na EC2 do time: `bash deploy.sh` via Session Manager (porta 8000, bind 0.0.0.0).

## O que faríamos a seguir
API pública de emissão por trecho (`/api/search` e `/api/esg/routes`) para motores de busca de passagens; integração com provedores certificados de crédito; incentivos dinâmicos por rota e ocupação; personalização da recomendação por histórico do passageiro (memória vetorial no TiDB).
