# Testing

## Test pyramid

- **Backend**: pytest (unit + integration); in-memory SQLite per test; fixtures in `tests/conftest.py` (db, client, test_user_token).
- **Frontend**: Vitest (unit); Playwright (e2e, e.g. `frontend/tests/e2e/secretary.spec.ts`).

## Commands

```bash
make test             # backend + frontend
make test-backend     # pytest -v
make test-frontend    # Vitest
cd frontend && npm run test:e2e   # Playwright
```

## Backend fixtures

- `db`: DB session  
- `client`: FastAPI TestClient  
- `test_user_data`, `test_user_token`: Authenticated test user  

## Coverage

- Backend: `cd backend && poetry run pytest --cov=app --cov-report=html`
- Frontend: `npm run test:coverage`

## Critical paths

- Auth: signup, signin, protected routes.
- Secretary: create session, send message, stream response, list sessions.
- Learning: create/search/delete records.
