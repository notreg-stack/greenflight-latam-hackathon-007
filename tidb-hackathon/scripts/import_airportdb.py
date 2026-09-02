"""Importa o dump oficial do airportdb no TiDB Cloud (sem cliente mysql).
Uso: cd tidb-hackathon/backend && ./.venv/bin/python ../scripts/import_airportdb.py
Lê TIDB_* do backend/.env. Executa cada statement do dump (CREATE TABLE + INSERTs) via pymysql.
"""
from __future__ import annotations
import gzip, os, sys, time, urllib.request
from pathlib import Path
import pymysql
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / "backend" / ".env")
DUMP = "https://hackaton-tidb.s3.sa-east-1.amazonaws.com/dumps/hackathon_airportdb.sql.gz"
CACHE = Path(__file__).resolve().parents[1] / "backend" / "data" / "hackathon_airportdb.sql.gz"


def statements(text: str):
    buf = []
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("--") or s.startswith("/*!") and s.endswith("*/;"):
            continue
        buf.append(line)
        if s.endswith(";"):
            yield "\n".join(buf); buf = []


def main():
    CACHE.parent.mkdir(exist_ok=True)
    if not CACHE.exists():
        print("baixando dump…"); urllib.request.urlretrieve(DUMP, CACHE)
    text = gzip.open(CACHE, "rt", encoding="utf-8", errors="replace").read()
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
    import db  # mesma conexão do app (TLS + fallback de DNS)
    conn = db._tidb_conn()
    cur = conn.cursor()
    cur.execute("SET FOREIGN_KEY_CHECKS=0")
    n = ins = 0; t0 = time.time()
    for st in statements(text):
        head = st.lstrip()[:40].upper()
        if head.startswith(("LOCK TABLES", "UNLOCK TABLES", "DROP TABLE")):
            continue
        try:
            cur.execute(st); n += 1
            if head.startswith("INSERT"):
                ins += cur.rowcount
                print(f"{time.time()-t0:6.1f}s  linhas inseridas: {ins}", flush=True)
            elif head.startswith("CREATE TABLE"):
                print(f"{time.time()-t0:6.1f}s  {st.splitlines()[0][:60]}", flush=True)
        except Exception as e:
            print("ERRO:", str(e)[:200], "| statement:", st[:80].replace("\n", " "), flush=True)
    cur.execute("SET FOREIGN_KEY_CHECKS=1")
    for t in ["flight", "booking", "passenger", "airport", "airport_geo", "airplane", "airplane_type", "airline", "flightschedule", "weatherdata", "employee", "passengerdetails"]:
        cur.execute(f"SELECT COUNT(*) FROM {t}"); print(t, cur.fetchone()[0], flush=True)
    print(f"concluído: {n} statements, {ins} linhas, {time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
