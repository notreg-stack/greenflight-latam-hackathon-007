"""GreenFlight API: busca e compra de passagens com pegada de carbono em tempo real.

Rode:  uvicorn main:app --host 0.0.0.0 --port 8000   (na pasta backend)
Serve também o React buildado em ../frontend/dist.
"""
from __future__ import annotations
import json, os
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import bedrock, carbon, db, greenflight

app = FastAPI(title="GreenFlight API", version="0.1")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

WEEK_START, WEEK_END = "2015-06-02", "2015-06-09"   # janela do dataset


@app.on_event("startup")
def _startup():
    db.ensure_app_tables()
    greenflight.ensure_tables()
    print(f"[greenflight] banco: {'TiDB Cloud ' + os.environ.get('TIDB_HOST', '') if db.USING_TIDB else 'SQLite local'} · bedrock: {bedrock.available()}")


@app.get("/api/health")
def health():
    return {"ok": True, "db": "tidb" if db.USING_TIDB else "sqlite", "bedrock": bedrock.available()}


@app.get("/api/airports")
def airports(q: str = Query(..., min_length=2)):
    ql = q.lower()
    with db.cursor() as cur:
        cur.execute(
            "SELECT a.airport_id, a.iata, a.icao, g.name, g.city, g.country FROM airport a "
            "JOIN airport_geo g ON g.airport_id = a.airport_id "
            f"WHERE LOWER(g.city) LIKE {db.PH} OR LOWER(a.iata) = {db.PH} OR LOWER(a.icao) = {db.PH} OR LOWER(g.name) LIKE {db.PH} "
            "ORDER BY CASE WHEN g.country = 'BRAZIL' THEN 0 ELSE 1 END, g.city LIMIT 12",
            (f"{ql}%", ql, ql, f"{ql}%"))
        out = db.rows(cur)
    for r in out:
        r["label"] = f"{r['city'].title()} ({r['iata'] or r['icao']}) · {r['country'].title()}"
    return out


@app.get("/api/routes/suggested")
def suggested_routes():
    with db.cursor() as cur:
        cur.execute(
            "SELECT g1.city AS from_city, g2.city AS to_city, f.`from` AS from_id, f.`to` AS to_id, COUNT(*) AS n "
            "FROM flight f JOIN airport_geo g1 ON g1.airport_id = f.`from` JOIN airport_geo g2 ON g2.airport_id = f.`to` "
            "WHERE g1.country = 'BRAZIL' OR g2.country = 'BRAZIL' "
            "GROUP BY g1.city, g2.city, f.`from`, f.`to` HAVING COUNT(*) >= 3 ORDER BY n DESC LIMIT 10")
        return db.rows(cur)


def _flight_rows(where: str, params: tuple, limit: int = 60) -> list[dict]:
    hint = "/*+ READ_FROM_STORAGE(TIFLASH[b]) */ " if db.USING_TIDB else ""
    sql = (
        "SELECT f.flight_id, f.flightno, f.departure, f.arrival, al.airlinename AS airline, t.identifier AS aircraft, p.capacity, "
        "g1.city AS from_city, a1.iata AS from_iata, a1.icao AS from_icao, g1.latitude AS lat1, g1.longitude AS lon1, "
        "g2.city AS to_city, a2.iata AS to_iata, a2.icao AS to_icao, g2.latitude AS lat2, g2.longitude AS lon2, "
        f"(SELECT {hint}COUNT(*) FROM booking b WHERE b.flight_id = f.flight_id) AS booked, "
        "(SELECT COUNT(*) FROM eco_purchase e WHERE e.flight_id = f.flight_id) AS eco_booked, "
        "(SELECT AVG(b2.price) FROM booking b2 WHERE b2.flight_id = f.flight_id) AS avg_price "
        "FROM flight f JOIN airline al ON al.airline_id = f.airline_id "
        "JOIN airplane p ON p.airplane_id = f.airplane_id JOIN airplane_type t ON t.type_id = p.type_id "
        "JOIN airport a1 ON a1.airport_id = f.`from` JOIN airport_geo g1 ON g1.airport_id = f.`from` "
        "JOIN airport a2 ON a2.airport_id = f.`to` JOIN airport_geo g2 ON g2.airport_id = f.`to` "
        f"WHERE {where} ORDER BY f.departure LIMIT {int(limit)}")
    with db.cursor() as cur:
        cur.execute(sql, params)
        return [_enrich(r) for r in db.rows(cur)]


def _enrich(r: dict) -> dict:
    dist = carbon.haversine_km(float(r["lat1"]), float(r["lon1"]), float(r["lat2"]), float(r["lon2"]))
    booked = int(r["booked"] or 0) + int(r["eco_booked"] or 0)
    e = carbon.emissions(dist, r["aircraft"], int(r["capacity"]), booked)
    dep, arr = str(r["departure"]), str(r["arrival"])
    price = round(float(r["avg_price"] or 250), 2)
    return {
        "flight_id": r["flight_id"], "flightno": r["flightno"], "airline": r["airline"], "aircraft": r["aircraft"],
        "from": {"city": r["from_city"].title(), "code": r["from_iata"] or r["from_icao"]},
        "to": {"city": r["to_city"].title(), "code": r["to_iata"] or r["to_icao"]},
        "departure": dep, "arrival": arr,
        "duration_min": int((datetime.fromisoformat(arr) - datetime.fromisoformat(dep)).total_seconds() // 60),
        "capacity": int(r["capacity"]), "booked": booked, "seats_left": max(int(r["capacity"]) - booked, 0),
        "price": price, "label": carbon.label(e["per_pax_kg"], e["distance_km"]), **e,
    }


@app.get("/api/search")
def search(origin: int | None = None, destination: int | None = None,
           origin_city: str | None = None, destination_city: str | None = None, date: str | None = None):
    conds, params = [], []
    if origin:
        conds.append(f"f.`from` = {db.PH}"); params.append(origin)
    elif origin_city:
        conds.append(f"LOWER(g1.city) = {db.PH}"); params.append(origin_city.lower())
    if destination:
        conds.append(f"f.`to` = {db.PH}"); params.append(destination)
    elif destination_city:
        conds.append(f"LOWER(g2.city) = {db.PH}"); params.append(destination_city.lower())
    if not conds:
        raise HTTPException(400, "informe origem ou destino")
    if date:
        d0 = datetime.fromisoformat(date); d1 = d0 + timedelta(days=1)
        conds.append(f"f.departure >= {db.PH} AND f.departure < {db.PH}")
        params += [d0.strftime("%Y-%m-%d %H:%M:%S"), d1.strftime("%Y-%m-%d %H:%M:%S")]
    results = _flight_rows(" AND ".join(conds), tuple(params))
    widened = False
    if not results and date:   # sem voo no dia: mostra a semana inteira
        widened = True
        results = _flight_rows(" AND ".join(conds[:-1]), tuple(params[:-2]))
    if results:
        best = min(results, key=lambda x: x["per_pax_kg"]); cheapest = min(results, key=lambda x: x["price"])
        worst = max(results, key=lambda x: x["per_pax_kg"])
        if len(results) >= 3:   # selo relativo à busca: A = 20% mais limpos … E = 20% piores (absoluto fica no recibo)
            ranked = sorted(results, key=lambda x: x["per_pax_kg"])
            for i, r in enumerate(ranked):
                r["label"] = "ABCDE"[min(int(i * 5 / len(ranked)), 4)]
        for r in results:
            r["is_greenest"] = r["flight_id"] == best["flight_id"]
            r["is_cheapest"] = r["flight_id"] == cheapest["flight_id"]
            r["co2_avoided_vs_worst"] = round(worst["per_pax_kg"] - r["per_pax_kg"], 1)
    with db.cursor() as cur:
        cur.execute(f"INSERT INTO eco_search_log (origin, destination, travel_date, results) VALUES ({db.PH},{db.PH},{db.PH},{db.PH})",
                    (str(origin or origin_city), str(destination or destination_city), date or None, len(results)))
    return {"results": results, "widened_to_week": widened, "count": len(results)}


class Purchase(BaseModel):
    flight_id: int
    passenger_name: str
    email: str = ""
    alternatives: list[int] = []


@app.post("/api/purchase")
def purchase(p: Purchase):
    rows = _flight_rows(f"f.flight_id = {db.PH}", (p.flight_id,))
    if not rows:
        raise HTTPException(404, "voo não encontrado")
    chosen = rows[0]
    if chosen["seats_left"] <= 0:
        raise HTTPException(409, "voo lotado")
    alts = []
    if p.alternatives:
        ph = ",".join([db.PH] * len(p.alternatives))
        alts = _flight_rows(f"f.flight_id IN ({ph})", tuple(p.alternatives))
    worst = max([a["per_pax_kg"] for a in alts] + [chosen["per_pax_kg"]])
    avoided = round(worst - chosen["per_pax_kg"], 1)
    if len(alts) >= 2:   # mesmo selo relativo que a busca mostrou
        ranked = sorted(alts + [chosen], key=lambda x: x["per_pax_kg"])
        pos = next(i for i, x in enumerate(ranked) if x["flight_id"] == chosen["flight_id"])
        chosen["label"] = "ABCDE"[min(int(pos * 5 / len(ranked)), 4)]
    chosen_over = json.dumps([{"flightno": a["flightno"], "per_pax_kg": a["per_pax_kg"], "price": a["price"]} for a in alts])
    with db.cursor() as cur:
        cur.execute(
            "INSERT INTO eco_purchase (flight_id, passenger_name, email, price, co2_kg, co2_avoided_kg, label, chosen_over) "
            f"VALUES ({db.PH},{db.PH},{db.PH},{db.PH},{db.PH},{db.PH},{db.PH},{db.PH})",
            (p.flight_id, p.passenger_name, p.email, chosen["price"], chosen["per_pax_kg_after_purchase"], avoided, chosen["label"], chosen_over))
        purchase_id = cur.lastrowid
    after = _flight_rows(f"f.flight_id = {db.PH}", (p.flight_id,))[0]   # ocupação já com a nova compra
    passenger_key = (p.email or p.passenger_name).strip().lower()
    after["label"] = chosen["label"]   # selo relativo à busca, igual ao que o comprador viu
    receipt = {"purchase_id": purchase_id, "flight": after, "passenger_name": p.passenger_name, "passenger_key": passenger_key,
               "co2_kg": after["per_pax_kg"], "co2_avoided_kg": avoided, "label": chosen["label"], "alternatives": alts,
               "offset_quote": greenflight.offset_quote(after["per_pax_kg"]), "wallet": greenflight.wallet(passenger_key)}
    receipt["s3_key"] = _export_receipt(receipt)
    return receipt


def _export_receipt(receipt: dict) -> str | None:
    """Guarda o recibo no prefixo S3 do time (role da EC2). Falha em silêncio fora da AWS."""
    prefix = os.environ.get("GREENFLIGHT_S3_PREFIX")   # ex.: s3://tidb-latam-hackathon-2026-048364544505/latam-hackathon-007/
    if not prefix or not prefix.startswith("s3://"):
        return None
    try:
        import boto3
        bucket, _, base = prefix[5:].partition("/")
        key = f"{base.rstrip('/')}/receipts/{receipt['flight']['flightno']}-{datetime.utcnow():%Y%m%dT%H%M%S}.json"
        boto3.client("s3", region_name="sa-east-1").put_object(Bucket=bucket, Key=key, Body=json.dumps(receipt, ensure_ascii=False, default=str).encode())
        return key
    except Exception as e:
        print("[s3] ignorado:", str(e)[:80])
        return None


@app.get("/api/explain")
def explain(flight_id: int, alternatives: str = ""):
    ids = [int(x) for x in alternatives.split(",") if x.strip().isdigit()]
    chosen = _flight_rows(f"f.flight_id = {db.PH}", (flight_id,))
    if not chosen:
        raise HTTPException(404, "voo não encontrado")
    alts = _flight_rows(f"f.flight_id IN ({','.join([db.PH]*len(ids))})", tuple(ids)) if ids else []
    slim = lambda f: {k: f[k] for k in ("flightno", "aircraft", "occupancy", "per_pax_kg", "price", "distance_km", "label")}
    return {"text": bedrock.explain_choice(slim(chosen[0]), [slim(a) for a in alts]), "bedrock": bedrock.available()}


class Ask(BaseModel):
    question: str


@app.post("/api/ask")
def ask(a: Ask):
    k = db.knowledge_search(a.question)
    return {"answer": bedrock.answer(a.question, k), "sources": k, "vector": db.USING_TIDB}


@app.get("/api/stats")
def stats():
    with db.cursor() as cur:
        cur.execute("SELECT COUNT(*) AS n, COALESCE(SUM(co2_kg),0) AS co2, COALESCE(SUM(co2_avoided_kg),0) AS avoided, COALESCE(SUM(price),0) AS revenue FROM eco_purchase")
        s = db.rows(cur)[0]
        cur.execute("SELECT COUNT(*) AS n FROM eco_search_log")
        s["searches"] = db.rows(cur)[0]["n"]
    return {k: (round(float(v), 1) if isinstance(v, (int, float)) and k != "n" else v) for k, v in s.items()}


@app.get("/api/routes/greenest")
def greenest():
    """Rotas que tocam o Brasil ordenadas pela menor emissão média por passageiro (analytics)."""
    rows = _flight_rows("g1.country = 'BRAZIL' OR g2.country = 'BRAZIL'", ())
    agg: dict[str, dict] = {}
    for r in rows:
        k = f"{r['from']['city']} → {r['to']['city']}"
        a = agg.setdefault(k, {"route": k, "flights": 0, "kg": 0.0, "price": 0.0})
        a["flights"] += 1; a["kg"] += r["per_pax_kg"]; a["price"] += r["price"]
    out = [{"route": a["route"], "flights": a["flights"], "avg_kg": round(a["kg"] / a["flights"], 1), "avg_price": round(a["price"] / a["flights"], 0)} for a in agg.values()]
    return sorted(out, key=lambda x: x["avg_kg"])[:10]


# ---------------- GreenFlight: compensação, projetos, rewards, ESG ----------------
@app.get("/api/carbon/projects")
def carbon_projects(preference: str = "", k: int = 3):
    if not preference.strip():
        with db.cursor() as cur:
            cur.execute("SELECT id, name, description, country, project_type, price_per_ton FROM carbon_project")
            return db.rows(cur)
    return greenflight.search_projects(preference, k)


class Recommend(BaseModel):
    preference: str
    flight_id: int | None = None
    co2_kg: float | None = None


@app.post("/api/carbon/projects/recommend")
def carbon_recommend(r: Recommend):
    projects = greenflight.search_projects(r.preference, 3)
    rec = bedrock.recommend_project(r.preference, projects)
    quote = greenflight.offset_quote(r.co2_kg or 0.0) if r.co2_kg else None
    return {"projects": projects, "recommended": rec, "quote": quote, "engine": projects[0]["engine"] if projects else None, "bedrock": bedrock.available()}


class Offset(BaseModel):
    flight_id: int
    project_id: int
    passenger_key: str
    co2_kg: float
    preference: str = ""
    purchase_id: int | None = None


@app.post("/api/carbon/offset")
def carbon_offset(o: Offset):
    try:
        return {"success": True, **greenflight.confirm_offset(o.purchase_id, o.flight_id, o.passenger_key.strip().lower(), o.project_id, o.preference, o.co2_kg)}
    except ValueError as e:
        raise HTTPException(404, str(e))


@app.get("/api/rewards/wallet")
def rewards_wallet(key: str):
    return greenflight.wallet(key.strip().lower())


@app.get("/api/esg")
def esg():
    return greenflight.esg_dashboard()


_cache: dict = {}


def _cached(key: str, ttl: float, fn):
    import time
    hit = _cache.get(key)
    if hit and time.time() - hit[0] < ttl:
        return hit[1]
    val = fn(); _cache[key] = (time.time(), val)
    return val


def _all_brazil_flights() -> list[dict]:
    return _cached("br_flights", 120, lambda: _flight_rows("g1.country = 'BRAZIL' OR g2.country = 'BRAZIL'", (), limit=10000))


@app.get("/api/esg/routes")
def esg_routes(price_per_ton: float = greenflight.CARBON_CREDIT_PRICE_PER_TON, limit: int = 15):
    """Análise por trecho sobre o airportdb inteiro (voos que tocam o Brasil): emissão, ocupação e valor da compensação."""
    agg: dict[str, dict] = {}
    for r in _all_brazil_flights():
        k = f"{r['from']['city']} → {r['to']['city']}"
        a = agg.setdefault(k, {"route": k, "flights": 0, "flight_kg": 0.0, "pax": 0, "pax_kg": 0.0, "km": r["distance_km"], "seats": 0})
        a["flights"] += 1; a["flight_kg"] += r["flight_kg"]; a["pax"] += r["booked"]; a["pax_kg"] += r["per_pax_kg"]; a["seats"] += r["capacity"]
    rows = []
    for a in agg.values():
        tons = a["flight_kg"] / 1000.0
        rows.append({"route": a["route"], "flights": a["flights"], "distance_km": a["km"], "occupancy": round(a["pax"] / max(a["seats"], 1), 2),
                     "avg_kg_per_pax": round(a["pax_kg"] / a["flights"], 1), "total_tons": round(tons, 1),
                     "offset_value_brl": round(tons * price_per_ton, 2), "price_per_ton": price_per_ton})
    total = {"routes": len(rows), "flights": sum(r["flights"] for r in rows), "total_tons": round(sum(r["total_tons"] for r in rows), 1),
             "offset_value_brl": round(sum(r["offset_value_brl"] for r in rows), 2), "price_per_ton": price_per_ton}
    return {"summary": total, "cleanest": sorted(rows, key=lambda x: x["avg_kg_per_pax"])[:limit],
            "heaviest": sorted(rows, key=lambda x: x["total_tons"], reverse=True)[:limit]}


DEMO_DATE = "2015-06-04"


@app.get("/api/live")
def live():
    """Relógio de demo: a hora atual mapeada para 04/06/2015. Emissão acumulada dos voos que já decolaram e próximas partidas."""
    def calc():
        now = datetime.now()
        clock = datetime.fromisoformat(f"{DEMO_DATE} {now:%H:%M:%S}")
        flights = [r for r in _all_brazil_flights() if r["departure"].startswith(DEMO_DATE)]
        departed = [r for r in flights if datetime.fromisoformat(r["departure"]) <= clock]
        upcoming = sorted([r for r in flights if datetime.fromisoformat(r["departure"]) > clock], key=lambda r: r["departure"])[:4]
        return {"clock": clock.strftime("%d/%m %H:%M:%S"), "flights_today": len(flights), "flights_departed": len(departed),
                "pax_departed": sum(r["booked"] for r in departed),
                "tons_emitted": round(sum(r["flight_kg"] for r in departed) / 1000.0, 2),
                "offset_value_brl": round(sum(r["flight_kg"] for r in departed) / 1000.0 * greenflight.CARBON_CREDIT_PRICE_PER_TON, 2),
                "next": [{"flightno": r["flightno"], "route": f"{r['from']['code']} → {r['to']['code']}", "departure": r["departure"][11:16],
                          "per_pax_kg": r["per_pax_kg"], "occupancy": r["occupancy"], "label": r["label"]} for r in upcoming]}
    return _cached("live", 3, calc)


DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if DIST.exists():
    app.mount("/", StaticFiles(directory=str(DIST), html=True), name="app")
