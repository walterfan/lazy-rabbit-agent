# Medical Paper Writing Assistant — Runbook

## Overview

The Medical Paper Writing Assistant is a multi-agent system that generates
clinical research papers through a pipeline of specialized AI agents:

```
Literature Search → Statistical Analysis → IMRAD Writing → Compliance Check
```

Supported paper types: RCT (CONSORT), Cohort (STROBE), Meta-analysis (PRISMA).

---

## Architecture

```
User → API (FastAPI) → MedicalPaperSupervisor
                              │
               ┌──────────────┼──────────────┐──────────────┐
               ▼              ▼              ▼              ▼
         LiteratureAgent  StatsAgent   WriterAgent  ComplianceAgent
         (PubMed, CT.gov) (scipy)     (IMRAD)      (CONSORT/STROBE/PRISMA)
```

Each agent has its own tool set (SRP) and communicates via A2A messages.

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/medical-paper/create` | Create new paper task |
| GET | `/api/v1/medical-paper/{task_id}` | Get task status/results |
| GET | `/api/v1/medical-paper/{task_id}/stream` | Stream progress (SSE) |
| POST | `/api/v1/medical-paper/{task_id}/revise` | Submit revision feedback |
| GET | `/api/v1/medical-paper` | List user's tasks |
| GET | `/api/v1/medical-paper/templates` | List paper type templates |

---

## Common Issues & Solutions

### 1. Task stuck in RUNNING status

**Symptom:** Task status remains `running` for more than 30 minutes.

**Diagnosis:**
```sql
SELECT id, status, current_step, updated_at
FROM medical_paper_tasks
WHERE status = 'running'
AND updated_at < NOW() - INTERVAL '30 minutes';
```

**Resolution:**
1. Check application logs for the task_id
2. Look for LLM timeout or rate-limit errors
3. Manually update status to `failed`:
```sql
UPDATE medical_paper_tasks
SET status = 'failed', updated_at = NOW()
WHERE id = '<task_id>';
```
4. User can retry by creating a new task

### 2. PubMed API rate limiting

**Symptom:** Literature agent returns empty references with rate-limit errors.

**Diagnosis:** Check logs for `429` or `rate limit` in literature tool calls.

**Resolution:**
- Ensure `NCBI_API_KEY` is set in environment (raises rate limit from 3/s to 10/s)
- If persistent, the PubMed E-utilities may be experiencing downtime
- Check status at: https://www.ncbi.nlm.nih.gov/home/develop/

### 3. Statistical analysis returns errors

**Symptom:** Stats agent tools return `{"error": "scipy not available"}`.

**Diagnosis:** scipy/statsmodels not installed in the environment.

**Resolution:**
```bash
cd backend && poetry install
# or
pip install scipy statsmodels
```

### 4. Compliance score always 0

**Symptom:** Compliance report shows `overall_score: 0.0` and `total_items: 0`.

**Diagnosis:** The compliance agent received an empty manuscript or the LLM
failed to parse the manuscript into checklist items.

**Resolution:**
1. Check that the writer agent produced content in `manuscript_sections`
2. Verify the compliance prompt template is accessible:
   ```bash
   ls backend/app/services/medical_paper_agent/prompts/agents/compliance/
   ```
3. Check LLM response quality — may need temperature adjustment

### 5. LLM connection failures

**Symptom:** `Connection refused` or SSL errors in logs.

**Diagnosis:**
```bash
curl -k $LLM_BASE_URL/v1/models \
  -H "Authorization: Bearer $LLM_API_KEY"
```

**Resolution:**
- Verify `LLM_BASE_URL` and `LLM_API_KEY` in `.env`
- For self-signed certificates: set `LLM_VERIFY_SSL=false`
- Check `LLM_TIMEOUT` (default: 60s, may need increase for paper tasks)

---

## Metrics Interpretation

### Key Prometheus Metrics

| Metric | What to watch |
|--------|---------------|
| `medical_paper_task_total` | Task creation rate; spike in `failed` status |
| `medical_paper_task_duration_seconds` | P95 should be < 600s (10 min) |
| `medical_paper_agent_latency_seconds` | Per-agent latency; literature < 30s, others < 60s |
| `medical_paper_compliance_score` | Should trend upward with revisions |
| `medical_paper_revision_rounds` | Avg < 2 is healthy; > 3 indicates prompt issues |
| `medical_paper_active_tasks` | Should not exceed worker pool size |

### Grafana Dashboard Queries

**Task success rate (5m window):**
```promql
rate(medical_paper_task_total{status="completed"}[5m])
/ rate(medical_paper_task_total{status=~"completed|failed"}[5m])
```

**P95 task duration:**
```promql
histogram_quantile(0.95, rate(medical_paper_task_duration_seconds_bucket[5m]))
```

**Agent error rate:**
```promql
rate(medical_paper_agent_calls_total{status="error"}[5m])
/ rate(medical_paper_agent_calls_total[5m])
```

---

## Alert Responses

### Alert: High task failure rate (> 20%)

1. Check `medical_paper_task_errors_total` by `error_type`
2. If `timeout`: increase `LLM_TIMEOUT` or check LLM provider
3. If `tool_error`: check specific agent logs
4. If `validation`: review input validation in API layer

### Alert: Agent latency P95 > 120s

1. Check which agent is slow via `medical_paper_agent_latency_seconds`
2. Literature agent slow → PubMed API issues
3. Stats agent slow → large dataset or scipy computation
4. Writer agent slow → LLM response time
5. Consider scaling LLM resources or adding caching

### Alert: Active tasks > threshold

1. Check `medical_paper_active_tasks` gauge
2. If growing: tasks may be stuck (see issue #1 above)
3. Consider increasing background worker pool
4. Check for resource exhaustion (memory, DB connections)

---

## Recovery Procedures

### Full pipeline restart

```bash
# 1. Fail all stuck tasks
python -c "
from app.db.base import SessionLocal
from app.models.medical_paper import MedicalPaperTask
db = SessionLocal()
stuck = db.query(MedicalPaperTask).filter(
    MedicalPaperTask.status == 'running'
).all()
for t in stuck:
    t.status = 'failed'
db.commit()
print(f'Failed {len(stuck)} stuck tasks')
db.close()
"

# 2. Restart the application
supervisorctl restart backend
```

### Database migration

```bash
cd backend
alembic upgrade head
```

### Prompt template update

Prompt templates are loaded with `lru_cache`. To pick up changes:
1. Update the YAML file in `prompts/`
2. Restart the application (cache is process-level)

---

## Configuration Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_MODEL` | — | LLM model name |
| `LLM_BASE_URL` | — | LLM API endpoint |
| `LLM_API_KEY` | — | LLM API key |
| `LLM_VERIFY_SSL` | `true` | SSL verification for LLM |
| `LLM_TIMEOUT` | `60` | LLM call timeout (seconds) |
| `NCBI_API_KEY` | — | PubMed API key (optional, raises rate limit) |

---

## A2A Message Flow

### Sequence: Normal paper generation

```
User  →  API  →  Supervisor  →  LiteratureAgent  →  Supervisor
                                                        ↓
                                                    StatsAgent  →  Supervisor
                                                                      ↓
                                                                  WriterAgent  →  Supervisor
                                                                                    ↓
                                                                              ComplianceAgent  →  Supervisor
                                                                                                    ↓
                                                                                                 (score ≥ 0.8?)
                                                                                                  YES → END
                                                                                                  NO  → WriterAgent (revise)
                                                                                                         → ComplianceAgent (re-check)
                                                                                                         → ... (max 3 rounds)
```

### A2A Message Schema (v1)

Each inter-agent message follows the `a2a.medical.v1` protocol:

```json
{
  "protocol": "a2a.medical.v1",
  "id": "msg_20260209_abc123",
  "correlation_id": "task-uuid",
  "sender": "supervisor",
  "receiver": "literature_agent",
  "intent": "collect_references",
  "input": {"query": "hypertension treatment RCT"},
  "status": "pending",
  "output": null,
  "metrics": {"latency_ms": 0, "tool_calls": 0}
}
```

### Error Classification

| Code | Retry | Strategy |
|------|-------|----------|
| `VALIDATION_ERROR` | No | Return to user |
| `TOOL_ERROR` | 3x | Exponential backoff (1s, 2s, 4s) |
| `TIMEOUT` | 2x | Backoff (5s, 10s) |
| `RATE_LIMIT` | 3x | Backoff (10s, 20s, 40s) |
| `LLM_ERROR` | 2x | Backoff (2s, 4s) |
