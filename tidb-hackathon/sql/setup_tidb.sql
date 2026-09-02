-- GreenFlight · tabelas adicionais no TiDB Cloud Starter (sa-east-1). Rode no SQL Editor depois de importar o airportdb.
-- O backend cria tudo isto sozinho no startup (db.ensure_app_tables + greenflight.ensure_tables); este arquivo é a referência.
USE airportdb;

CREATE TABLE IF NOT EXISTS eco_purchase (
  purchase_id BIGINT AUTO_RANDOM PRIMARY KEY,
  flight_id INT NOT NULL, passenger_name VARCHAR(120), email VARCHAR(120),
  price DECIMAL(10,2), co2_kg DECIMAL(10,2), co2_avoided_kg DECIMAL(10,2), label CHAR(1),
  chosen_over JSON, created_at DATETIME DEFAULT CURRENT_TIMESTAMP, KEY (flight_id));

CREATE TABLE IF NOT EXISTS eco_search_log (
  id BIGINT AUTO_RANDOM PRIMARY KEY, origin VARCHAR(60), destination VARCHAR(60), travel_date DATE, results INT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP) TTL = `created_at` + INTERVAL 30 DAY;

CREATE TABLE IF NOT EXISTS eco_knowledge (
  id BIGINT AUTO_RANDOM PRIMARY KEY, topic VARCHAR(80), content TEXT NOT NULL,
  emb VECTOR(1024) GENERATED ALWAYS AS (EMBED_TEXT('tidbcloud_free/amazon/titan-embed-text-v2', content)) STORED,
  VECTOR INDEX ((VEC_COSINE_DISTANCE(emb))));

CREATE TABLE IF NOT EXISTS carbon_project (
  id BIGINT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(255) NOT NULL, description TEXT, country VARCHAR(100),
  project_type VARCHAR(100), price_per_ton DECIMAL(10,2),
  embedding VECTOR(1024) GENERATED ALWAYS AS (EMBED_TEXT('tidbcloud_free/amazon/titan-embed-text-v2', description)) STORED,
  VECTOR INDEX ((VEC_COSINE_DISTANCE(embedding))));

CREATE TABLE IF NOT EXISTS carbon_offset (
  id BIGINT PRIMARY KEY AUTO_INCREMENT, purchase_id BIGINT, flight_id INT NOT NULL, passenger_key VARCHAR(160) NOT NULL,
  project_id BIGINT NOT NULL, preference TEXT, co2_kg DECIMAL(12,2), amount DECIMAL(12,2),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, KEY (passenger_key), KEY (flight_id));

CREATE TABLE IF NOT EXISTS green_reward (
  id BIGINT PRIMARY KEY AUTO_INCREMENT, passenger_key VARCHAR(160) NOT NULL, offset_id BIGINT, points INT NOT NULL,
  reason VARCHAR(120), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, KEY (passenger_key));

CREATE TABLE IF NOT EXISTS green_wallet (
  passenger_key VARCHAR(160) PRIMARY KEY, total_points INT DEFAULT 0, lifetime_points INT DEFAULT 0,
  total_co2_offset DECIMAL(14,2) DEFAULT 0, offsets INT DEFAULT 0);

-- Busca vetorial: o passageiro descreve o projeto que quer apoiar
SELECT id, name, country, project_type, VEC_EMBED_COSINE_DISTANCE(embedding, 'Quero ajudar florestas brasileiras') AS d
FROM carbon_project ORDER BY d LIMIT 3;

-- Analytics colunar (opcional): réplica TiFlash para as agregações sobre 617 mil reservas
ALTER TABLE booking SET TIFLASH REPLICA 1;