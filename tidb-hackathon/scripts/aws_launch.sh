#!/usr/bin/env bash
# Lança a EC2 do CO²mpensa Aí em sa-east-1 a partir do CloudShell (ou de qualquer CLI autenticada na conta).
# Uso: bash aws_launch.sh <URL-temporária-do-.env> [nome]
# A instância busca o .env pela URL no boot e a cada minuto (enquanto a URL responder), reiniciando o app se mudar.
# Assim dá para subir sem o TiDB e trocar o .env depois, sem SSH. O segredo nunca fica neste script.
set -euo pipefail
ENV_URL="${1:?informe a URL temporária do .env}"
NAME="${2:-co2mpensa-ai}"
REGION="sa-east-1"
REPO="https://github.com/notreg-stack/greenflight-latam-hackathon-007.git"

VPC=$(aws ec2 describe-vpcs --region $REGION --filters Name=isDefault,Values=true --query 'Vpcs[0].VpcId' --output text)
SUBNET=$(aws ec2 describe-subnets --region $REGION --filters Name=vpc-id,Values=$VPC Name=default-for-az,Values=true --query 'Subnets[0].SubnetId' --output text)
SG=$(aws ec2 describe-security-groups --region $REGION --filters Name=group-name,Values=$NAME-sg Name=vpc-id,Values=$VPC --query 'SecurityGroups[0].GroupId' --output text 2>/dev/null || true)
if [ -z "$SG" ] || [ "$SG" = "None" ]; then
  SG=$(aws ec2 create-security-group --region $REGION --group-name $NAME-sg --description "CO2mpensa Ai app port 8000" --vpc-id $VPC --query GroupId --output text)
  aws ec2 authorize-security-group-ingress --region $REGION --group-id $SG --protocol tcp --port 8000 --cidr 0.0.0.0/0 >/dev/null
fi
AMI=$(aws ssm get-parameter --region $REGION --name /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 --query Parameter.Value --output text)

USERDATA=$(cat <<'EOF'
#!/bin/bash
set -x
dnf install -y git python3.11 python3.11-pip cronie
cd /opt && git clone --depth 1 __REPO__ co2mpensa && cd co2mpensa/tidb-hackathon
python3.11 -m pip install -q -r backend/requirements.txt
echo "__ENV_URL__" > /opt/co2mpensa/.env_url
curl -fsSL "__ENV_URL__" -o backend/.env && chmod 600 backend/.env
cat > /usr/local/bin/co2-refresh-env <<'SH'
#!/bin/bash
URL="$(cat /opt/co2mpensa/.env_url 2>/dev/null)"; [ -z "$URL" ] && exit 0
TMP=$(mktemp)
if curl -fsSL --max-time 20 "$URL" -o "$TMP" && [ -s "$TMP" ] && ! cmp -s "$TMP" /opt/co2mpensa/tidb-hackathon/backend/.env; then
  cp "$TMP" /opt/co2mpensa/tidb-hackathon/backend/.env && chmod 600 /opt/co2mpensa/tidb-hackathon/backend/.env && systemctl restart co2mpensa
fi
rm -f "$TMP"
SH
chmod +x /usr/local/bin/co2-refresh-env
echo "* * * * * root /usr/local/bin/co2-refresh-env" > /etc/cron.d/co2-refresh
systemctl enable --now crond
cat > /etc/systemd/system/co2mpensa.service <<'UNIT'
[Unit]
Description=CO2mpensa Ai (GreenFlight) API + frontend
After=network-online.target
[Service]
WorkingDirectory=/opt/co2mpensa/tidb-hackathon/backend
ExecStart=/usr/bin/python3.11 -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3
[Install]
WantedBy=multi-user.target
UNIT
systemctl daemon-reload && systemctl enable --now co2mpensa
EOF
)
USERDATA="${USERDATA//__REPO__/$REPO}"
USERDATA="${USERDATA//__ENV_URL__/$ENV_URL}"

ID=$(aws ec2 run-instances --region $REGION --image-id "$AMI" --instance-type t3.small --subnet-id "$SUBNET" --security-group-ids "$SG" \
  --associate-public-ip-address --user-data "$USERDATA" \
  --block-device-mappings 'DeviceName=/dev/xvda,Ebs={VolumeSize=12,VolumeType=gp3}' \
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$NAME},{Key=Project,Value=tidb-latam-hackathon-007}]" \
  --query 'Instances[0].InstanceId' --output text)
echo "instância: $ID"
aws ec2 wait instance-running --region $REGION --instance-ids "$ID"
IP=$(aws ec2 describe-instances --region $REGION --instance-ids "$ID" --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)
echo "URL: http://$IP:8000   (o app leva ~2 min para instalar; sem TiDB ele baixa o dump e roda em SQLite)"
echo "para encerrar depois do evento: aws ec2 terminate-instances --region $REGION --instance-ids $ID"
