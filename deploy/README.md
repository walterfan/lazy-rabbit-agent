# Lazy Rabbit Agent — Deployment Guide

## Architecture

```
                    ┌─────────────────────────────────────────┐
                    │              Internet                     │
                    └──────────────┬──────────────────────────┘
                                   │
                         ┌─────────▼─────────┐
                         │   Nginx (443/80)   │
                         │  HTTPS + WSS       │
                         │  Rate Limiting      │
                         │  Static Files       │
                         └──┬──────┬──────┬──┘
                            │      │      │
                   ┌────────▼┐  ┌──▼───┐  │
                   │ /api/*  │  │ /*   │  │
                   │ /ws     │  │ SPA  │  │
                   └────┬────┘  └──────┘  │
                        │                  │
                  ┌─────▼──────┐          │
                  │  Backend   │          │
                  │  FastAPI   │          │
                  │  :8000     │          │
                  └──┬────┬──┘          │
                     │    │              │
              ┌──────▼┐ ┌─▼────────┐    │
              │Postgres│ │ ChromaDB │    │
              │ :5432  │ │ (embed)  │    │
              └────────┘ └──────────┘    │
                                         │
                              ┌──────────▼┐
                              │   Redis    │
                              │   :6379    │
                              └────────────┘
```

## Quick Start

### 1. Configure Environment

```bash
cp .env.production.example .env.production
# Edit .env.production with your values
vim .env.production
```

### 2. Generate SSL Certificates

**Development (self-signed):**
```bash
./scripts/gen-certs.sh localhost
```

**Production (Let's Encrypt):**
```bash
./scripts/init-letsencrypt.sh your-domain.com your@email.com
```

### 3. Start Services

```bash
docker compose up -d
```

### 4. Verify

```bash
# Check all services are running
docker compose ps

# Check backend health
curl -k https://localhost/health

# View logs
docker compose logs -f backend
```

## Service Details

| Service   | Container       | Port (internal) | Description                          |
|-----------|-----------------|-----------------|--------------------------------------|
| nginx     | lra-nginx       | 80, 443         | Reverse proxy, HTTPS, WSS, static   |
| backend   | lra-backend     | 8000            | FastAPI API server                   |
| frontend  | lra-frontend    | —               | Build-only, outputs to volume        |
| postgres  | lra-postgres    | 5432            | PostgreSQL database                  |
| redis     | lra-redis       | 6379            | Cache + Celery broker                |

## HTTPS Configuration

### Nginx handles:
- **HTTP → HTTPS** redirect (port 80 → 443)
- **TLS 1.2/1.3** with modern cipher suites
- **HSTS** header (Strict-Transport-Security)
- **OCSP stapling** for certificate validation

### WebSocket (WSS):
- Path: `wss://your-domain.com/ws`
- Nginx upgrades HTTP → WebSocket via `Upgrade` header
- 1-hour timeout for long-lived connections

### SSE (Server-Sent Events):
- Path: `https://your-domain.com/api/v1/coach/chat/stream`
- `proxy_buffering off` ensures real-time streaming
- 5-minute read timeout

## Common Operations

```bash
# Rebuild after code changes
docker compose up -d --build backend

# Rebuild frontend
docker compose up -d --build frontend
# Then restart nginx to pick up new static files
docker compose restart nginx

# View backend logs
docker compose logs -f backend

# Enter backend container
docker compose exec backend bash

# Database backup
docker compose exec postgres pg_dump -U lra lazy_rabbit > backup.sql

# Renew Let's Encrypt certificate
./scripts/init-letsencrypt.sh your-domain.com your@email.com
```

## Docker Compose Files

| File                      | Purpose                                    |
|---------------------------|--------------------------------------------|
| `docker-compose.yml`     | **Production** — HTTPS, PostgreSQL, Redis  |
| `docker-compose-dev.yml` | Development — HTTP, MariaDB, Adminer       |
| `docker-compose-lab.yml` | Lab — pgvector, JupyterLab, PlantUML       |

## Troubleshooting

### Certificate errors
```bash
# Regenerate self-signed certs
./scripts/gen-certs.sh localhost

# Check cert expiry
openssl x509 -in nginx/ssl/fullchain.pem -noout -dates
```

### Backend won't start
```bash
# Check logs
docker compose logs backend

# Verify .env.production exists
ls -la .env.production

# Test database connection
docker compose exec postgres psql -U lra -d lazy_rabbit -c "SELECT 1"
```

### WebSocket connection fails
```bash
# Test WSS connection
wscat -c wss://localhost/ws --no-check

# Check nginx logs
docker compose logs nginx | grep "ws"
```
