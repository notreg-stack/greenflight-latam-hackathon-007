# Design — GreenFlight

## Arquitetura
```
Navegador (React/Vite, dist estático)
   │  /api/*
   ▼
FastAPI (EC2 sa-east-1 :8000)
   ├── db.py ──────► TiDB Cloud Starter sa-east-1 (airportdb + eco_purchase + eco_search_log[TTL] + eco_knowledge[VECTOR])
   │                 └─ fallback: SQLite local carregado do dump oficial
   ├── carbon.py ──► haversine × fator por aeronave ÷ ocupação (dataset + compras)
   ├── bedrock.py ─► Bedrock ap-southeast-1 (Claude 3 Haiku / 3.5 Sonnet / Cohere embed)
   └── boto3 S3 ───► s3://…/latam-hackathon-007/receipts/*.json (role da EC2)
```

## Fluxo de busca
1. `GET /api/airports?q=` autocompleta (cidade, IATA, ICAO, nome; Brasil primeiro).
2. `GET /api/search?origin=&destination=&date=` junta `flight`, `airline`, `airplane`, `airplane_type`, `airport`, `airport_geo`; subconsultas contam `booking` (com hint TiFlash no TiDB) e `eco_purchase`, e tiram o preço médio de `booking.price`.
3. Cada linha passa por `carbon.emissions()`; marca `is_greenest`, `is_cheapest` e `co2_avoided_vs_worst`.
4. A busca é registrada em `eco_search_log` (TTL de 30 dias no TiDB).

## Fluxo de compra
1. `POST /api/purchase` recalcula o voo, recusa se lotado, grava `eco_purchase` (JSON com alternativas rejeitadas).
2. Recalcula o voo já com a compra e devolve recibo com CO2 evitado; exporta JSON para S3 se `GREENFLIGHT_S3_PREFIX` existir.
3. Frontend chama `GET /api/explain` (Bedrock Haiku) e refaz a busca para mostrar a ocupação nova.

## Modelo de dados novo
- `eco_purchase(purchase_id, flight_id, passenger_name, email, price, co2_kg, co2_avoided_kg, label, chosen_over JSON, created_at)`
- `eco_search_log(id, origin, destination, travel_date, results, created_at)` com `TTL = created_at + INTERVAL 30 DAY`
- `eco_knowledge(id, topic, content, emb VECTOR(1024) GENERATED ALWAYS AS EMBED_TEXT(...) STORED, VECTOR INDEX)`

## Metodologia de carbono
- Distância: haversine entre `airport_geo` dos dois aeroportos × 1,08.
- Fator por classe de aeronave (kg CO2/assento-km), tabela em `carbon.py` com valores na ordem de grandeza ICAO/DEFRA.
- Emissão do voo = distância × assentos × fator; por passageiro = ÷ passageiros a bordo; "após sua compra" = ÷ (a bordo + 1).
- Selo A–E comparando com 0,11 kg/pax-km esperado para a distância.

## Decisões e limites
- Preços do dataset são sintéticos (uniformes); usamos a média por voo só para ordenar por preço.
- Não há atrasos no dataset; não prometemos previsão.
- Uma porta e um processo: cabe na EC2 de 913 MB.
