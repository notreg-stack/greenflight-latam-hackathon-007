"""GreenFlight: projetos ambientais (vetor), compensação, Green Points, wallet e ESG.
Segue o modelo de docs/ARQUITETURA_GREENFLIGHT.md (carbon_project, carbon_offset, green_reward, green_wallet).
"""
from __future__ import annotations
import json, re
import db

CARBON_CREDIT_PRICE_PER_TON = 10.0     # R$ por tonelada (MVP)
POINTS_PER_OFFSET = 100                # base do programa
TIERS = [(500, "desconto em bagagem"), (1000, "prioridade de embarque"), (2000, "lounge / upgrade / voucher")]

DDL_TIDB = """
CREATE TABLE IF NOT EXISTS carbon_project (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL, description TEXT, country VARCHAR(100), project_type VARCHAR(100),
  price_per_ton DECIMAL(10,2),
  embedding VECTOR(1024) GENERATED ALWAYS AS (EMBED_TEXT('tidbcloud_free/amazon/titan-embed-text-v2', description)) STORED,
  VECTOR INDEX ((VEC_COSINE_DISTANCE(embedding)))
);
CREATE TABLE IF NOT EXISTS carbon_offset (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  purchase_id BIGINT, flight_id INT NOT NULL, passenger_key VARCHAR(160) NOT NULL, project_id BIGINT NOT NULL,
  preference TEXT, co2_kg DECIMAL(12,2), amount DECIMAL(12,2), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  KEY (passenger_key), KEY (flight_id)
);
CREATE TABLE IF NOT EXISTS green_reward (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  passenger_key VARCHAR(160) NOT NULL, offset_id BIGINT, points INT NOT NULL, reason VARCHAR(120),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, KEY (passenger_key)
);
CREATE TABLE IF NOT EXISTS green_wallet (
  passenger_key VARCHAR(160) PRIMARY KEY, total_points INT DEFAULT 0, lifetime_points INT DEFAULT 0,
  total_co2_offset DECIMAL(14,2) DEFAULT 0, offsets INT DEFAULT 0
);
"""
DDL_SQLITE = """
CREATE TABLE IF NOT EXISTS carbon_project (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, description TEXT, country TEXT, project_type TEXT, price_per_ton REAL);
CREATE TABLE IF NOT EXISTS carbon_offset (id INTEGER PRIMARY KEY AUTOINCREMENT, purchase_id INT, flight_id INT NOT NULL, passenger_key TEXT NOT NULL, project_id INT NOT NULL, preference TEXT, co2_kg REAL, amount REAL, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS green_reward (id INTEGER PRIMARY KEY AUTOINCREMENT, passenger_key TEXT NOT NULL, offset_id INT, points INT NOT NULL, reason TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS green_wallet (passenger_key TEXT PRIMARY KEY, total_points INT DEFAULT 0, lifetime_points INT DEFAULT 0, total_co2_offset REAL DEFAULT 0, offsets INT DEFAULT 0);
"""

PROJECTS = [
    ("Amazon Reforestation", "Recuperação de áreas degradadas e reflorestamento na Amazônia brasileira, com espécies nativas e comunidades locais.", "Brazil", "REFORESTATION", 10.0),
    ("Atlantic Forest Recovery", "Recuperação de áreas da Mata Atlântica no Brasil, corredores ecológicos e biodiversidade.", "Brazil", "REFORESTATION", 11.0),
    ("Solar Energy Northeast", "Expansão de geração solar no Nordeste do Brasil, substituindo energia térmica a diesel.", "Brazil", "RENEWABLE_ENERGY", 8.5),
    ("Forest Conservation Peru", "Conservação de áreas florestais na Amazônia peruana com monitoramento por satélite.", "Peru", "CONSERVATION", 9.0),
    ("Cerrado Water Springs", "Proteção de nascentes e recuperação de matas ciliares no Cerrado brasileiro.", "Brazil", "WATER", 9.5),
    ("Wind Power Patagonia", "Parques eólicos na Patagônia argentina com energia limpa para a rede.", "Argentina", "RENEWABLE_ENERGY", 8.0),
    ("Mangrove Guardians Bahia", "Restauração de manguezais no litoral da Bahia, captura de carbono azul e pesca sustentável.", "Brazil", "BLUE_CARBON", 12.0),
    ("Clean Cookstoves Andes", "Fogões eficientes para famílias rurais nos Andes, reduzindo desmatamento e fumaça.", "Bolivia", "COMMUNITY", 7.5),
]


def ensure_tables():
    ddl = DDL_TIDB if db.USING_TIDB else DDL_SQLITE
    with db.cursor() as cur:
        for stmt in [s.strip() for s in ddl.split(";") if s.strip()]:
            try:
                cur.execute(stmt)
            except Exception as e:
                print("[greenflight] aviso DDL:", str(e)[:120])
                if "carbon_project" in stmt and db.USING_TIDB:   # sem EMBED_TEXT: tabela sem vetor
                    cur.execute("CREATE TABLE IF NOT EXISTS carbon_project (id BIGINT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(255), description TEXT, country VARCHAR(100), project_type VARCHAR(100), price_per_ton DECIMAL(10,2))")
        cur.execute("SELECT COUNT(*) AS n FROM carbon_project")
        if not db.rows(cur)[0]["n"]:
            for p in PROJECTS:
                cur.execute(f"INSERT INTO carbon_project (name, description, country, project_type, price_per_ton) VALUES ({db.PH},{db.PH},{db.PH},{db.PH},{db.PH})", p)


def offset_quote(co2_kg: float, price_per_ton: float = CARBON_CREDIT_PRICE_PER_TON) -> dict:
    amount = round(co2_kg / 1000.0 * price_per_ton, 2)
    points = POINTS_PER_OFFSET + int(co2_kg // 100)     # voos mais longos rendem um pouco mais
    return {"co2_kg": round(co2_kg, 1), "price_per_ton": price_per_ton, "offset_price": amount, "green_points": points}


def search_projects(preference: str, k: int = 3) -> list[dict]:
    """TiDB: busca vetorial com EMBED_TEXT. SQLite: pontuação por palavras (fallback)."""
    cols = "id, name, description, country, project_type, price_per_ton"
    with db.cursor() as cur:
        if db.USING_TIDB:
            try:
                cur.execute(f"SELECT {cols}, VEC_EMBED_COSINE_DISTANCE(embedding, %s) AS distance FROM carbon_project ORDER BY distance LIMIT %s", (preference, k))
                out = db.rows(cur)
                for r in out:
                    r["distance"] = round(float(r["distance"]), 4); r["engine"] = "tidb-vector"
                return out
            except Exception as e:
                print("[greenflight] vetor indisponível:", str(e)[:100])
        cur.execute(f"SELECT {cols} FROM carbon_project")
        rows = db.rows(cur)
    words = set(re.findall(r"\w{4,}", preference.lower()))
    syn = {"floresta": "reflorest", "florestas": "reflorest", "arvore": "reflorest", "árvores": "reflorest", "solar": "solar", "energia": "energ", "agua": "nascentes", "água": "nascentes", "mar": "mangue", "brasil": "brasil", "brasileir": "brasil"}
    for r in rows:
        hay = f"{r['name']} {r['description']} {r['country']} {r['project_type']}".lower()
        score = sum(1 for w in words if w in hay or syn.get(w, "\x00") in hay)
        if "brasil" in preference.lower() and r["country"] == "Brazil":
            score += 1
        r["distance"] = round(1.0 / (1 + score), 4); r["engine"] = "keyword-fallback"
    return sorted(rows, key=lambda r: r["distance"])[:k]


def confirm_offset(purchase_id: int | None, flight_id: int, passenger_key: str, project_id: int, preference: str, co2_kg: float) -> dict:
    with db.cursor() as cur:
        cur.execute(f"SELECT id, name, price_per_ton FROM carbon_project WHERE id = {db.PH}", (project_id,))
        proj = db.rows(cur)
        if not proj:
            raise ValueError("projeto não encontrado")
        q = offset_quote(co2_kg, float(proj[0]["price_per_ton"]))
        cur.execute(f"INSERT INTO carbon_offset (purchase_id, flight_id, passenger_key, project_id, preference, co2_kg, amount) VALUES ({db.PH},{db.PH},{db.PH},{db.PH},{db.PH},{db.PH},{db.PH})",
                    (purchase_id, flight_id, passenger_key, project_id, preference, q["co2_kg"], q["offset_price"]))
        offset_id = cur.lastrowid
        cur.execute(f"INSERT INTO green_reward (passenger_key, offset_id, points, reason) VALUES ({db.PH},{db.PH},{db.PH},{db.PH})",
                    (passenger_key, offset_id, q["green_points"], f"compensação {proj[0]['name']}"))
        if db.USING_TIDB:
            cur.execute("INSERT INTO green_wallet (passenger_key, total_points, lifetime_points, total_co2_offset, offsets) VALUES (%s,%s,%s,%s,1) "
                        "ON DUPLICATE KEY UPDATE total_points = total_points + VALUES(total_points), lifetime_points = lifetime_points + VALUES(lifetime_points), "
                        "total_co2_offset = total_co2_offset + VALUES(total_co2_offset), offsets = offsets + 1",
                        (passenger_key, q["green_points"], q["green_points"], q["co2_kg"]))
        else:
            cur.execute("INSERT INTO green_wallet (passenger_key, total_points, lifetime_points, total_co2_offset, offsets) VALUES (?,?,?,?,1) "
                        "ON CONFLICT(passenger_key) DO UPDATE SET total_points = total_points + excluded.total_points, lifetime_points = lifetime_points + excluded.lifetime_points, "
                        "total_co2_offset = total_co2_offset + excluded.total_co2_offset, offsets = offsets + 1",
                        (passenger_key, q["green_points"], q["green_points"], q["co2_kg"]))
    return {"offset_id": offset_id, "project": proj[0]["name"], **q, "wallet": wallet(passenger_key)}


def wallet(passenger_key: str) -> dict:
    with db.cursor() as cur:
        cur.execute(f"SELECT * FROM green_wallet WHERE passenger_key = {db.PH}", (passenger_key,))
        w = db.rows(cur)
    w = w[0] if w else {"passenger_key": passenger_key, "total_points": 0, "lifetime_points": 0, "total_co2_offset": 0, "offsets": 0}
    pts = int(w["total_points"] or 0)
    nxt = next(((t, b) for t, b in TIERS if pts < t), None)
    w["total_co2_offset"] = round(float(w["total_co2_offset"] or 0), 1)
    w["next_benefit"] = {"points_needed": nxt[0] - pts, "benefit": nxt[1]} if nxt else {"points_needed": 0, "benefit": "nível máximo"}
    w["unlocked"] = [b for t, b in TIERS if pts >= t]
    return w


def esg_dashboard() -> dict:
    with db.cursor() as cur:
        cur.execute("SELECT COUNT(*) AS n FROM eco_purchase"); purchases = db.rows(cur)[0]["n"]
        cur.execute("SELECT COUNT(*) AS n, COALESCE(SUM(co2_kg),0) AS co2, COALESCE(SUM(amount),0) AS amount, COUNT(DISTINCT passenger_key) AS pax FROM carbon_offset"); o = db.rows(cur)[0]
        cur.execute("SELECT COALESCE(SUM(points),0) AS pts FROM green_reward"); pts = db.rows(cur)[0]["pts"]
        cur.execute("SELECT COUNT(*) AS n FROM carbon_project"); projects = db.rows(cur)[0]["n"]
        cur.execute("SELECT p.name, COUNT(*) AS n, COALESCE(SUM(o.co2_kg),0) AS co2 FROM carbon_offset o JOIN carbon_project p ON p.id = o.project_id GROUP BY p.name ORDER BY n DESC LIMIT 5"); top = db.rows(cur)
        cur.execute("SELECT g1.city AS from_city, g2.city AS to_city, COUNT(*) AS n, COALESCE(SUM(o.co2_kg),0) AS co2 FROM carbon_offset o JOIN flight f ON f.flight_id = o.flight_id "
                    "JOIN airport_geo g1 ON g1.airport_id = f.`from` JOIN airport_geo g2 ON g2.airport_id = f.`to` GROUP BY g1.city, g2.city ORDER BY n DESC LIMIT 5"); routes = db.rows(cur)
    n = int(o["n"] or 0)
    return {
        "adoption_rate": round(n / purchases, 3) if purchases else 0.0, "purchases": purchases, "offsets": n,
        "co2_offset_kg": round(float(o["co2"] or 0), 1), "amount_brl": round(float(o["amount"] or 0), 2),
        "participants": int(o["pax"] or 0), "projects": projects, "green_points_issued": int(pts or 0),
        "top_projects": [{"name": t["name"], "offsets": t["n"], "co2_kg": round(float(t["co2"]), 1)} for t in top],
        "by_route": [{"route": f"{r['from_city'].title()} → {r['to_city'].title()}", "offsets": r["n"], "co2_kg": round(float(r["co2"]), 1)} for r in routes],
    }


def recommend_prompt(preference: str, projects: list[dict]) -> str:
    lst = "\n".join(f"{i+1}. {p['name']} — País: {p['country']} — Tipo: {p['project_type']} — {p['description']}" for i, p in enumerate(projects))
    return (f"Preferência do passageiro: \"{preference}\"\n\nProjetos disponíveis (já ordenados por similaridade vetorial):\n{lst}\n\n"
            "Recomende o projeto mais alinhado à preferência. Responda SOMENTE um JSON com as chaves recommended_project e short_reason, em português.")
