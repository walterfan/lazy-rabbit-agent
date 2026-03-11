#!/usr/bin/env bash
# ============================================================================
# Generate self-signed SSL certificates for development/testing
# For production, use Let's Encrypt (see init-letsencrypt.sh)
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SSL_DIR="${SCRIPT_DIR}/../nginx/ssl"

mkdir -p "$SSL_DIR"

if [ -f "$SSL_DIR/fullchain.pem" ] && [ -f "$SSL_DIR/privkey.pem" ]; then
    echo "⚠️  SSL certificates already exist in $SSL_DIR"
    read -p "Overwrite? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Skipped."
        exit 0
    fi
fi

DOMAIN="${1:-localhost}"

echo "🔐 Generating self-signed certificate for: $DOMAIN"

openssl req -x509 -nodes -days 365 \
    -newkey rsa:2048 \
    -keyout "$SSL_DIR/privkey.pem" \
    -out "$SSL_DIR/fullchain.pem" \
    -subj "/C=CN/ST=Anhui/L=Hefei/O=LazyRabbit/CN=$DOMAIN" \
    -addext "subjectAltName=DNS:$DOMAIN,DNS:localhost,IP:127.0.0.1"

echo "✅ Self-signed certificates generated:"
echo "   Certificate: $SSL_DIR/fullchain.pem"
echo "   Private key: $SSL_DIR/privkey.pem"
echo ""
echo "⚠️  These are for development only. For production, use Let's Encrypt:"
echo "   ./scripts/init-letsencrypt.sh your-domain.com your@email.com"
