#!/usr/bin/env bash
# Deploy deepfake detection dashboard to Timeweb Cloud VPS
# Usage: bash deploy.sh YOUR_DOMAIN
set -euo pipefail

DOMAIN="${1:-}"
if [ -z "$DOMAIN" ]; then
    echo "Usage: bash deploy.sh YOUR_DOMAIN"
    echo "Example: bash deploy.sh df-dashboard.ru"
    exit 1
fi

echo "=== 1. System update & Docker install ==="
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y ca-certificates curl gnupg

# Docker official repo
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

echo "=== 2. SSL certificate (Let's Encrypt) ==="
sudo apt-get install -y certbot
sudo certbot certonly --standalone -d "$DOMAIN" --non-interactive --agree-tos --register-unsafely-without-email
# Auto-renewal cron
echo "0 3 * * * certbot renew --quiet && docker compose -f $(pwd)/docker-compose.yml restart nginx" | sudo crontab -

echo "=== 3. Configure domain in nginx ==="
sed -i "s/YOUR_DOMAIN/$DOMAIN/g" nginx/nginx.conf

echo "=== 4. Create .env ==="
if [ ! -f .env ]; then
    read -rp "Enter MIEM_TOKEN: " TOKEN
    echo "MIEM_TOKEN=$TOKEN" > .env
    echo ".env created"
else
    echo ".env already exists, skipping"
fi

echo "=== 5. Build & start ==="
sudo docker compose up -d --build

echo ""
echo "=== Done! ==="
echo "Dashboard: https://$DOMAIN"
echo ""
echo "Useful commands:"
echo "  sudo docker compose logs -f        # view logs"
echo "  sudo docker compose restart app    # restart app"
echo "  sudo docker compose down           # stop all"
echo "  sudo docker compose up -d --build  # rebuild & start"
