# Runbook

## One-command startup

```bash
make setup    # create .env from sample (if needed)
make install  # backend: poetry install; frontend: npm install
make migrate # alembic upgrade head
make run      # backend :8000 + frontend :5173
```

- Frontend: http://localhost:5173  
- Backend: http://localhost:8000  
- API docs: http://localhost:8000/docs  

## Run backend only

```bash
make run-backend
# or: cd backend && poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Run frontend only

```bash
make run-frontend
# or: cd frontend && npm run dev
```

## Tests

```bash
make test           # backend + frontend tests
make test-backend   # cd backend && poetry run pytest -v
make test-frontend  # cd frontend && npm run test
# E2E: cd frontend && npm run test:e2e
```

## Database

```bash
make migrate        # upgrade to head
make migrate-create  # create new migration (prompts for message)
make db-reset       # remove app.db and re-run migrations
```

## User management

```bash
make list-users
make reset-password EMAIL=user@example.com
make activate-user EMAIL=user@example.com
```

## Troubleshooting

- **Port in use**: Change port or stop process (e.g. `lsof -ti:8000 | xargs kill -9`).
- **DB locked (SQLite)**: Single process only, or use PostgreSQL.
- **Import errors**: Ensure `poetry shell` (backend) and deps installed (`make install`).
