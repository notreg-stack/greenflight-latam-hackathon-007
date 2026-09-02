#!/usr/bin/env bash
# GreenFlight · deploy na EC2 do time 007 (sa-east-1, Amazon Linux 2023, t3.micro 913 MB).
# Rode via Session Manager (EC2 → Connect → Session Manager). Portas abertas: 8000-8999 e 3000. Bind sempre em 0.0.0.0.
# Uso: bash deploy.sh [repo-https] [subpasta]
set -euo pipefail
REPO="${1:-https://github.com/notreg-stack/greenflight-latam-hackathon-007.git}"
DIR="${2:-tidb-hackathon}"

sudo dnf install -y -q git python3.11 python3.11-pip            # nem git nem pip vêm instalados; python do sistema é 3.9
[ -d greenflight/.git ] || git clone --depth 1 "$REPO" greenflight       # clone por HTTPS: só 443/80/4000 saem da EC2
git -C greenflight pull --ff-only -q
cd "greenflight/$DIR"
python3.11 -m pip install -q -r backend/requirements.txt

if [ ! -d frontend/dist ]; then                                  # dist vem commitado; só builda se faltar (npm pesa na t3.micro)
  sudo dnf install -y -q nodejs npm
  ( cd frontend && npm ci --silent && npm run build )
fi

if [ ! -f backend/.env ]; then
  cp backend/.env.example backend/.env
  echo ">> Preencha backend/.env (TiDB + chave Bedrock do time) com um heredoc, não com vi, e rode de novo:"
  echo "   cat > backend/.env <<'ENV'"; echo "   ...conteúdo..."; echo "   ENV"; echo "   chmod 600 backend/.env"
  exit 1
fi
chmod 600 backend/.env

pkill -f "uvicorn main:app" || true
cd backend
setsid nohup python3.11 -m uvicorn main:app --host 0.0.0.0 --port 8000 > app.log 2>&1 < /dev/null &
sleep 4
curl -s http://0.0.0.0:8000/api/health; echo
python3.11 -c "import bedrock; print(bedrock.selftest())"
echo "URL pública (muda a cada stop/start da instância): http://$(curl -s http://checkip.amazonaws.com):8000"
