# Personal Secretary Agent - Operations Runbook

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Access to an LLM API (OpenAI-compatible)

### Setup

1. **Install backend dependencies:**
   ```bash
   cd backend
   poetry install
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Run database migrations:**
   ```bash
   cd backend
   alembic upgrade head
   ```

4. **Build frontend:**
   ```bash
   cd frontend
   npm install
   npm run build
   ```

5. **Start the application:**
   ```bash
   ./start.sh
   ```

### Accessing the Application
- **Frontend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Metrics**: http://localhost:8000/api/metrics

## Configuration

### LLM Configuration

```env
# LLM Provider Settings
LLM_PROVIDER=openai
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=sk-xxx
LLM_MODEL=gpt-4o

# For self-hosted LLM with self-signed certificate
LLM_VERIFY_SSL=false
LLM_TIMEOUT=60
```

### Database Configuration

```env
DATABASE_URL=postgresql://user:pass@localhost:5432/lazy_rabbit
```

## Monitoring

### Health Check
```bash
curl http://localhost:8000/api/health
# Expected: {"status": "healthy"}
```

### Prometheus Metrics
```bash
curl http://localhost:8000/api/metrics
```

### Key Metrics to Watch

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| `secretary_chat_request_duration_seconds{quantile="0.95"}` | P95 latency | > 10s |
| `secretary_chat_first_token_latency_seconds{quantile="0.95"}` | P95 first token | > 2s |
| `rate(secretary_chat_errors_total[5m])` | Error rate | > 1% |
| `secretary_active_streams` | Active streaming connections | > 100 |

## Troubleshooting

### Issue: Chat responses are slow

**Symptoms:**
- High latency in chat responses
- Timeouts

**Diagnosis:**
1. Check LLM latency:
   ```bash
   curl -X POST http://localhost:8000/api/v1/secretary/chat \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer TOKEN" \
     -d '{"message": "hello"}' \
     -w "\nTotal time: %{time_total}s\n"
   ```

2. Check metrics:
   ```bash
   curl http://localhost:8000/api/metrics | grep secretary_llm
   ```

**Solutions:**
- Increase `LLM_TIMEOUT` in .env
- Check LLM provider status
- Consider using a faster model

### Issue: SSL Certificate Errors

**Symptoms:**
- `SSL: CERTIFICATE_VERIFY_FAILED` errors
- Connection refused to LLM API

**Diagnosis:**
```bash
openssl s_client -connect your-llm-api.com:443 -showcerts
```

**Solutions:**
1. For self-signed certificates:
   ```env
   LLM_VERIFY_SSL=false
   ```

2. For corporate CAs, add CA bundle:
   ```env
   SSL_CERT_FILE=/path/to/ca-bundle.crt
   ```

### Issue: Learning records not saving

**Symptoms:**
- User clicks "Save" but records don't appear
- 500 errors on `/learning/confirm`

**Diagnosis:**
1. Check database connection:
   ```bash
   cd backend && python -c "from app.db.session import SessionLocal; print(SessionLocal().execute('SELECT 1'))"
   ```

2. Check logs:
   ```bash
   tail -f backend/logs/app.log | grep learning
   ```

**Solutions:**
- Verify database is running
- Check migration status: `alembic current`
- Run pending migrations: `alembic upgrade head`

### Issue: Streaming not working

**Symptoms:**
- No tokens appear during streaming
- Connection closes immediately

**Diagnosis:**
1. Test SSE endpoint:
   ```bash
   curl -N -X POST http://localhost:8000/api/v1/secretary/chat/stream \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer TOKEN" \
     -d '{"message": "hello"}'
   ```

2. Check for proxy issues (nginx, load balancer)

**Solutions:**
- Disable proxy buffering:
  ```nginx
  proxy_buffering off;
  proxy_cache off;
  ```
- Increase proxy timeout:
  ```nginx
  proxy_read_timeout 300s;
  ```

## Database Operations

### Backup
```bash
pg_dump -U postgres lazy_rabbit > backup_$(date +%Y%m%d).sql
```

### Restore
```bash
psql -U postgres lazy_rabbit < backup_20241201.sql
```

### Migration Management

**Check current version:**
```bash
cd backend && alembic current
```

**Upgrade to latest:**
```bash
cd backend && alembic upgrade head
```

**Downgrade one version:**
```bash
cd backend && alembic downgrade -1
```

## Scaling Considerations

### Horizontal Scaling
- Chat endpoints are stateless, can be scaled horizontally
- Use Redis for session storage if scaling beyond single instance
- Consider connection pooling for database

### Performance Tuning
- Increase `LLM_TIMEOUT` for complex queries
- Adjust `MAX_ITERATIONS` in agent config for tool-heavy workflows
- Use caching for frequently accessed learning records

## Security Checklist

- [ ] Change default admin credentials
- [ ] Use HTTPS in production
- [ ] Set `LLM_VERIFY_SSL=true` unless using self-signed certs
- [ ] Rotate API keys regularly
- [ ] Enable rate limiting
- [ ] Review CORS settings

## Contact

For issues with the Personal Secretary agent:
- Check GitHub issues
- Review logs in `backend/logs/`
- Contact the development team
