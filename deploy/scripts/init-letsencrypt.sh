#!/usr/bin/env bash
# ============================================================================
# Initialize Let's Encrypt certificates using Certbot
# Usage: ./init-letsencrypt.sh <domain> <email>
# ============================================================================

set -euo pipefail

DOMAIN="${1:?Usage: $0 <domain> <email>}"
EMAIL="${2:?Usage: $0 <domain> <email>}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DEPLOY_DIR="${SCRIPT_DIR}/.."
SSL_DIR="${DEPLOY_DIR}/nginx/ssl"
CERTBOT_DIR="${DEPLOY_DIR}/certbot"

echo "🔐 Initializing Let's Encrypt for: $DOMAIN"

# Step 1: Create directories
mkdir -p "$SSL_DIR" "$CERTBOT_DIR/www" "$CERTBOT_DIR/conf"

# Step 2: Generate temporary self-signed cert so nginx can start
if [ ! -f "$SSL_DIR/fullchain.pem" ]; then
    echo "📝 Creating temporary self-signed certificate..."
    openssl req -x509 -nodes -days 1 \
        -newkey rsa:2048 \
        -keyout "$SSL_DIR/privkey.pem" \
        -out "$SSL_DIR/fullchain.pem" \
        -subj "/CN=$DOMAIN"
fi

# Step 3: Start nginx (needs to be running for ACME challenge)
echo "🚀 Starting nginx..."
cd "$DEPLOY_DIR"
docker compose up -d nginx

# Step 4: Run certbot
echo "📜 Requesting certificate from Let's Encrypt..."
docker run --rm \
    -v "$CERTBOT_DIR/conf:/etc/letsencrypt" \
    -v "$CERTBOT_DIR/www:/var/www/certbot" \
    certbot/certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    -d "$DOMAIN"

# Step 5: Copy certificates to nginx ssl directory
echo "📋 Copying certificates..."
cp "$CERTBOT_DIR/conf/live/$DOMAIN/fullchain.pem" "$SSL_DIR/fullchain.pem"
cp "$CERTBOT_DIR/conf/live/$DOMAIN/privkey.pem" "$SSL_DIR/privkey.pem"

# Step 6: Reload nginx
echo "🔄 Reloading nginx..."
docker compose exec nginx nginx -s reload

echo ""
echo "✅ Let's Encrypt certificate installed for: $DOMAIN"
echo ""
echo "📌 To auto-renew, add this cron job:"
echo "   0 0 1 * * cd $DEPLOY_DIR && docker run --rm -v $CERTBOT_DIR/conf:/etc/letsencrypt -v $CERTBOT_DIR/www:/var/www/certbot certbot/certbot renew && cp $CERTBOT_DIR/conf/live/$DOMAIN/fullchain.pem $SSL_DIR/fullchain.pem && cp $CERTBOT_DIR/conf/live/$DOMAIN/privkey.pem $SSL_DIR/privkey.pem && docker compose exec nginx nginx -s reload"
