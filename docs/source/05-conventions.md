# Conventions

## Code style

- **Backend**: Black (line length 88), Ruff (E,W,F,I,C,B), mypy strict. Classes PascalCase, functions/variables snake_case.
- **Frontend**: ESLint, Prettier; TypeScript strict; Composition API; components PascalCase.

## Lint / format

- **Backend**: `make format-backend` (Black + Ruff fix), `make lint-backend` (Ruff + mypy).
- **Frontend**: `make format-frontend`, `make lint-frontend`.

## Error handling

- Backend: Pydantic validation; HTTPException for API errors; structured logging without secrets.
- Frontend: Axios interceptors; user-facing error messages generic.

## Logging

- Backend: Python logging; request logging middleware (method, path, status, duration). No credentials or PII in logs.
- Secretary: `LOG_LEVEL_SECRETARY`, `TRACE_DETAILED` for debug.

## Config and secrets

- All secrets from environment (`.env`); never in code or logs.
- See `openspec/project.md` and security baseline in `.cursor/rules/`.
