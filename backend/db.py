"""Camada de dados: TiDB Cloud Starter (produção) ou SQLite local (fallback de demo).

Se TIDB_HOST estiver no .env, usa TiDB (pymysql, TLS obrigatório).
Senão, baixa o dump oficial uma vez e carrega em backend/data/airportdb.sqlite.
As consultas usam SQL portável; o que muda (placeholders, DDL) fica aqui.
"""
from __future__ import annotations
import gzip, os, re, sqlite3, urllib.request
from contextlib import contextmanager
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))

DUMP_URL = "https://hackaton-tidb.s3.sa-east-1.amazonaws.com/dumps/hackathon_airportdb.sql.gz"
DATA_DIR = Path(__file__).with_name("data")
SQLITE_PATH = DATA_DIR / "airportdb.sqlite"

USING_TIDB = bool(os.environ.get("TIDB_HOST"))
PH = "%s" if USING_TIDB else "?"     # placeholder do driver


def _tidb_conn():
    import pymysql
    # TLS é obrigatório no endpoint público: macOS usa /etc/ssl/cert.pem, Amazon Linux usa o ca-bundle
    candidates = [os.environ.get("TIDB_SSL_CA"), "/etc/ssl/cert.pem", "/etc/pki/tls/certs/ca-bundle.crt", "/etc/ssl/certs/ca-certificates.crt"]
    ca = next((c for c in candidates if c and Path(c).exists()), None)
    return pymysql.connect(
        host=os.environ["TIDB_HOST"], port=int(os.environ.get("TIDB_PORT", "4000")),
        user=os.environ["TIDB_USER"], password=os.environ["TIDB_PASSWORD"],
        database=os.environ.get("TIDB_DATABASE", "airportdb"),
        ssl={"ca": ca} if ca else {"ssl": True},
        cursorclass=pymysql.cursors.DictCursor, autocommit=True,
    )


def _sqlite_conn():
    if not SQLITE_PATH.exists():
        _build_sqlite()
    c = sqlite3.connect(SQLITE_PATH, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c


def _build_sqlite():
    """Baixa o dump (10 MB) e carrega as 12 tabelas + tabelas do app. Roda uma vez."""
    DATA_DIR.mkdir(exist_ok=True)
    print("[db] baixando dump oficial para o modo local...")
    raw = urllib.request.urlopen(DUMP_URL, timeout=180).read()
    text = gzip.decompress(raw).decode("utf-8", "replace")
    c = sqlite3.connect(SQLITE_PATH)
    c.executescript("""
    CREATE TABLE airline(airline_id,iata,airlinename,base_airport);
    CREATE TABLE airplane(airplane_id,capacity,type_id,airline_id);
    CREATE TABLE airplane_type(type_id,identifier,description);
    CREATE TABLE airport(airport_id,iata,icao,name);
    CREATE TABLE airport_geo(airport_id,name,city,country,latitude,longitude);
    CREATE TABLE booking(booking_id,flight_id,seat,passenger_id,price);
    CREATE TABLE employee(employee_id,firstname,lastname,birthdate,sex,street,city,zip,country,emailaddress,telephoneno,salary,department,username,password);
    CREATE TABLE flight(flight_id,flightno,"from","to",departure,arrival,airline_id,airplane_id);
    CREATE TABLE flightschedule(flightno,"from","to",departure,arrival,airline_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday);
    CREATE TABLE passenger(passenger_id,passportno,firstname,lastname);
    CREATE TABLE passengerdetails(passenger_id,birthdate,sex,street,city,zip,country,emailaddress,telephoneno);
    CREATE TABLE weatherdata(log_date,time,station,temp,humidity,airpressure,wind,weather,winddirection);
    """)
    for line in text.splitlines():
        if line.startswith("INSERT INTO"):
            s = line.replace("\\\\", "\x00").replace("\\'", "''").replace('\\"', '"').replace("\x00", "\\")
            c.execute(s)
    c.executescript("""
    CREATE INDEX ix_flight_from ON flight("from"); CREATE INDEX ix_flight_to ON flight("to");
    CREATE INDEX ix_flight_dep ON flight(departure); CREATE INDEX ix_booking_flight ON booking(flight_id);
    CREATE INDEX ix_geo_city ON airport_geo(city); CREATE INDEX ix_geo_country ON airport_geo(country);
    """)
    c.executescript(APP_DDL_SQLITE)
    c.commit(); c.close()
    print("[db] modo local pronto:", SQLITE_PATH)


# ---- tabelas do GreenFlight (mesmo desenho nos dois bancos) ----
APP_DDL_TIDB = """
CREATE TABLE IF NOT EXISTS eco_purchase (
  purchase_id BIGINT AUTO_RANDOM PRIMARY KEY,
  flight_id INT NOT NULL, passenger_name VARCHAR(120), email VARCHAR(120),
  price DECIMAL(10,2), co2_kg DECIMAL(10,2), co2_avoided_kg DECIMAL(10,2), label CHAR(1),
  chosen_over JSON, created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  KEY (flight_id)
);
CREATE TABLE IF NOT EXISTS eco_search_log (
  id BIGINT AUTO_RANDOM PRIMARY KEY,
  origin VARCHAR(60), destination VARCHAR(60), travel_date DATE, results INT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) TTL = `created_at` + INTERVAL 30 DAY;
CREATE TABLE IF NOT EXISTS eco_knowledge (
  id BIGINT AUTO_RANDOM PRIMARY KEY,
  topic VARCHAR(80), content TEXT NOT NULL,
  emb VECTOR(1024) GENERATED ALWAYS AS (EMBED_TEXT('tidbcloud_free/amazon/titan-embed-text-v2', content)) STORED,
  VECTOR INDEX ((VEC_COSINE_DISTANCE(emb)))
);
"""
APP_DDL_SQLITE = """
CREATE TABLE IF NOT EXISTS eco_purchase (
  purchase_id INTEGER PRIMARY KEY AUTOINCREMENT,
  flight_id INT NOT NULL, passenger_name TEXT, email TEXT,
  price REAL, co2_kg REAL, co2_avoided_kg REAL, label TEXT, chosen_over TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS eco_search_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT, origin TEXT, destination TEXT, travel_date TEXT, results INT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS eco_knowledge (
  id INTEGER PRIMARY KEY AUTOINCREMENT, topic TEXT, content TEXT NOT NULL);
"""

KNOWLEDGE_SEED = [
    ("metodologia", "A emissão por passageiro é a emissão do voo dividida pelos passageiros a bordo; voos mais cheios emitem menos por pessoa."),
    ("metodologia", "A distância usa o grande círculo entre os aeroportos com fator de desvio de 8%, prática dos calculadores da ICAO."),
    ("aeronaves", "Turboélices como o Bombardier Q Series emitem cerca de metade do CO2 por assento-km de um jato de quatro motores como o A380 ou o 747."),
    ("aeronaves", "Widebodies de dois motores como A330 e 777 ficam no meio da tabela; narrowbodies como A320 e 737 são eficientes em rotas curtas e médias."),
    ("compensacao", "Uma árvore adulta absorve cerca de 22 kg de CO2 por ano; usamos isso como equivalência ilustrativa."),
    ("selo", "O selo A a E compara a emissão por passageiro com a mediana esperada para a distância, cerca de 0,11 kg por passageiro-km."),
    ("regras", "Resolução ANAC 400: a partir de 1 hora de atraso a companhia deve oferecer comunicação; 2 horas, alimentação; 4 horas, reacomodação, reembolso ou hospedagem."),
    ("futuro", "Próxima etapa: expor a emissão por trecho como API para motores de busca de passagens, que hoje ordenam só por preço e duração."),
]


@contextmanager
def cursor():
    conn = _tidb_conn() if USING_TIDB else _sqlite_conn()
    try:
        cur = conn.cursor()
        yield cur
        if not USING_TIDB:
            conn.commit()
    finally:
        conn.close()


def rows(cur) -> list[dict]:
    out = cur.fetchall()
    return [dict(r) for r in out]


def ensure_app_tables():
    ddl = APP_DDL_TIDB if USING_TIDB else APP_DDL_SQLITE
    with cursor() as cur:
        for stmt in [s.strip() for s in ddl.split(";") if s.strip()]:
            try:
                cur.execute(stmt)
            except Exception as e:  # ex.: EMBED_TEXT indisponível → tabela sem vetor
                print("[db] aviso DDL:", str(e)[:120])
                if "eco_knowledge" in stmt and USING_TIDB:
                    cur.execute("CREATE TABLE IF NOT EXISTS eco_knowledge (id BIGINT AUTO_RANDOM PRIMARY KEY, topic VARCHAR(80), content TEXT NOT NULL)")
        cur.execute("SELECT COUNT(*) AS n FROM eco_knowledge")
        n = rows(cur)[0]["n"]
        if not n:
            for topic, content in KNOWLEDGE_SEED:
                cur.execute(f"INSERT INTO eco_knowledge (topic, content) VALUES ({PH}, {PH})", (topic, content))


def knowledge_search(question: str, k: int = 3) -> list[dict]:
    """Busca vetorial no TiDB (EMBED_TEXT); no SQLite, busca por palavra."""
    with cursor() as cur:
        if USING_TIDB:
            for sql in (   # forma curta (docs) e forma exata do briefing do evento
                "SELECT topic, content FROM eco_knowledge ORDER BY VEC_EMBED_COSINE_DISTANCE(emb, %s) LIMIT %s",
                "SELECT topic, content FROM eco_knowledge ORDER BY VEC_COSINE_DISTANCE(emb, EMBED_TEXT('tidbcloud_free/amazon/titan-embed-text-v2', %s)) LIMIT %s",
            ):
                try:
                    cur.execute(sql, (question, k))
                    return rows(cur)
                except Exception as e:
                    print("[db] vetor:", str(e)[:100])
            print("[db] vetor indisponível, caindo para LIKE")
        words = [w for w in re.findall(r"\w{4,}", question.lower())][:4] or ["emiss"]
        where = " OR ".join(["LOWER(content) LIKE " + PH] * len(words))
        cur.execute(f"SELECT topic, content FROM eco_knowledge WHERE {where} LIMIT {int(k)}",
                    tuple(f"%{w}%" for w in words))
        return rows(cur)
