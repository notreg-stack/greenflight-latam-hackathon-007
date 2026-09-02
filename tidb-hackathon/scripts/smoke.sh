#!/usr/bin/env bash
# Smoke test da API GreenFlight. Uso: bash scripts/smoke.sh [base_url]
B="${1:-http://localhost:8000}"
set -e
curl -sf "$B/api/health" | head -c 200; echo
curl -sf "$B/api/airports?q=ituiu" | head -c 200; echo
curl -sf "$B/api/search?origin_city=ITUIUTABA&destination_city=BOA%20VISTA" | python3 -c "import sys,json;d=json.load(sys.stdin);print('voos:',d['count'],'| primeiro:',d['results'][0]['flightno'],d['results'][0]['per_pax_kg'],'kg',d['results'][0]['label'])"
curl -sf -X POST "$B/api/carbon/projects/recommend" -H 'Content-Type: application/json' -d '{"preference":"Quero ajudar florestas brasileiras","co2_kg":120}' | python3 -c "import sys,json;d=json.load(sys.stdin);print('projetos:',[p['name'] for p in d['projects']],'| rec:',d['recommended']['recommended_project'],'|',d['engine'])"
curl -sf "$B/api/esg" | head -c 300; echo
echo OK