#!/usr/bin/env bash
# GreenFlight · deploy na EC2 do time (sa-east-1, Amazon Linux 2023, 913 MB). Rode via Session Manager.
set -euo pipefail
REPO="${1:-https://github.com/henriqueleandro-arch/LatamHackathon.git}"
DIR="${2:-projects/latam-hackathon-007}"
sudo dnf install -y -q git python3.11 python3.11-pip nodejs npm
[ -d LatamHackathon ] || chop git clone --depth 1 "$REPO"
cd "LatamHackathon/$DIR"
python3.11 -m pip install -q -r backend/requirements.txt
( cd frontend && chop npm ci --silent && chop npm run build )
[ -f backend/.env ] || { cp backend/.env.example backend/.env; echo ">> edite backend/.env (TiDB + chave Bedrock) e rode de novo"; exit 1; }
pkill -f "uvicorn main:app" || true
cd backend && nohup python3.11 -m uvicorn main:app --host 0.0.0.0 --port 8000 > app.log 2>&1 < /dev/null &
sleep 3; curl -s localhost:8000/api/health; echo
echo "URL: http://$(curl -s http://checkip.amazonaws.com):8000"
