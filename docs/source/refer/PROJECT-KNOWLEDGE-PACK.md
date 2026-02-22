# Lazy Rabbit Agent — Project Knowledge Pack

A single reference for onboarding and day-to-day work: structure, stack, commands, key domains, and conventions.

---

## 1. What This Project Is

**Lazy Rabbit Agent** is an AI-powered web app that provides:

- **Personal Secretary**: Conversational AI agent with tools (weather, notes, tasks, reminders, calculator, datetime, learning tools, article processing).
- **Multi-agent workflow**: Supervisor + sub-agents (Learning, Productivity, Utility) via LangGraph.
- **Recommendations**: LLM-driven, context-aware (weather, location).
- **RBAC**: JWT auth, roles (super_admin, admin, user, guest), permissions.
- **Other features**: Weather (multi-provider), email (SMTP), learning records, medical-paper writing assistant.

**Entry points**: Web UI (Vue) at `http://localhost:5173`, REST API at `http://localhost:8000`, API docs at `http://localhost:8000/docs`.

---

## 2. Repository Layout

```
lazy-rabbit-agent/
├── backend/                    # FastAPI app (Python 3.11+, Poetry)
│   ├── app/
│   │   ├── main.py             # FastAPI entry, CORS, middleware
│   │   ├── api/v1/             # Routes
│   │   │   ├── api.py          # Router aggregation (auth, users, secretary, learning, etc.)
│   │   │   └── endpoints/      # auth, users, admin, rbac, secretary, learning, medical_paper, ...
│   │   ├── core/               # config.py, security.py
│   │   ├── db/                 # SQLAlchemy base, session
│   │   ├── models/             # User, ChatSession, ChatMessage, Note, Task, Reminder, LearningRecord, ...
│   │   ├── schemas/            # Pydantic request/response
│   │   └── services/           # Business logic
│   │       ├── secretary_agent/   # Supervisor + sub-agents (LangGraph)
│   │       │   ├── agent.py       # SecretaryAgent, routing, chat/chat_stream
│   │       │   ├── a2a.py         # Agent-to-agent protocol
│   │       │   ├── prompts/       # system.yaml, sub_agents.yaml
│   │       │   ├── sub_agents/    # learning, productivity, utility
│   │       │   └── tools/         # weather, calculator, datetime, note, task, reminder, learning_*, article_processor, ...
│   │       ├── chat_service.py
│   │       ├── llm/, weather/, email_service, rbac_service, ...
│   │       └── ...
│   ├── alembic/                # Migrations
│   ├── tests/                  # pytest
│   ├── pyproject.toml
│   └── README.md
├── frontend/                   # Vue 3 + TypeScript + Vite
│   ├── src/
│   │   ├── views/              # Secretary.vue, Learning.vue, Home, tools/*
│   │   ├── components/         # secretary/*, layout/*
│   │   ├── stores/             # Pinia: auth, secretary, learning, ...
│   │   ├── services/           # secretary.service, learning.service, ...
│   │   ├── router/
│   │   └── types/
│   ├── tests/                  # Vitest, e2e (Playwright)
│   └── package.json
├── openspec/                   # Specs and change workflow
│   ├── project.md              # Project context, conventions, domain
│   ├── specs/                  # Main specs (e.g. personal-secretary-agent)
│   └── changes/                # Active and archived changes
├── docs/                       # Runbooks, architecture
├── scripts/                    # setup-env, etc.
├── Makefile                    # install, run, test, lint, format, migrate
├── README.md
└── .env / .env.sample
```

---

## 3. Tech Stack (Quick Reference)

| Layer      | Technologies |
|-----------|---------------|
| Backend   | FastAPI, SQLAlchemy 2, Pydantic 2, Alembic, JWT (python-jose), bcrypt, Poetry |
| LLM/Agent | LangChain, LangGraph, OpenAI SDK, instructor, httpx |
| Frontend  | Vue 3 (Composition API), TypeScript, Vite, Pinia, Vue Router, Axios, Tailwind |
| Testing   | pytest (+ asyncio, cov), Vitest, Playwright (e2e) |
| Quality   | Black, Ruff, mypy (backend); ESLint, Prettier (frontend) |

---

## 4. Commands You’ll Use

From **project root** (recommended: use `Makefile`):

| Goal              | Command |
|-------------------|---------|
| First-time setup  | `make setup` then `make install` then `make migrate` |
| Run all           | `make run` (backend :8000, frontend :5173) |
| Backend only      | `make run-backend` |
| Frontend only     | `make run-frontend` |
| All tests         | `make test` |
| Backend tests     | `make test-backend` or `cd backend && poetry run pytest -v` |
| Frontend tests    | `make test-frontend`; e2e: `cd frontend && npm run test:e2e` |
| Lint              | `make lint` (backend: ruff + mypy; frontend: eslint) |
| Format            | `make format` |
| Migrations        | `make migrate` (upgrade head) |
| New migration     | `make migrate-create` (prompts for message) |
| User admin        | `make list-users`, `make reset-password EMAIL=...`, `make activate-user EMAIL=...` |
| Backend shell     | `make backend-shell` then use Python/imports |
| Clean             | `make clean` |

Backend from `backend/`: `poetry install`, `poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`, `poetry run pytest -v`.

---

## 5. Configuration

- **Backend**: `.env` (see `.env.sample`). Looked up in: cwd, parent, `backend/`, project root.
- **Important vars**: `SECRET_KEY`, `DATABASE_URL`, `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL`, `LLM_VERIFY_SSL`, `WEATHER_*`, `MAIL_*`. Secretary: `LOG_LEVEL_SECRETARY`, `TRACE_DETAILED`.
- **Frontend**: `VITE_API_BASE_URL`, `VITE_WS_BASE_URL` (e.g. `http://localhost:8000`, `ws://localhost:8000`).

---

## 6. Personal Secretary Agent (Core Feature)

- **Spec**: `openspec/specs/personal-secretary-agent/spec.md`.
- **Implementation**: `backend/app/services/secretary_agent/`.
- **API prefix**: `/api/v1/secretary` (see `backend/app/api/v1/endpoints/secretary.py`). All endpoints require auth.

**Architecture** (supervisor + sub-agents):

- **SecretaryAgent** (supervisor): Routes user messages to one of three sub-agents or FINISH.
- **Sub-agents**: **Learning** (words, sentences, topics, Q&A, ideas, articles), **Productivity** (notes, tasks, reminders), **Utility** (weather, calculator, datetime).
- **Orchestration**: LangGraph `StateGraph`; state extends `MessagesState` with `next_agent`.
- **A2A**: Agent-to-agent protocol in `a2a.py` (requests/responses, metrics, status).

**Key file**: `backend/app/services/secretary_agent/agent.py` — `SecretaryAgent` class, `chat()` / `chat_stream()`, routing, tool-calling loop.

**Tools** (in `secretary_agent/tools/`): weather, calculator, datetime, note, task, reminder, learning (learn_word, learn_sentence, learn_topic, answer_question, plan_idea, learn_article), article_processor, PlantUML mindmap. Frontend: `Secretary.vue`, `secretary.service.ts`, `stores/secretary.ts`.

---

## 7. API Surface (High Level)

- **Auth**: `/api/v1/auth` (signup, signin).
- **Users**: `/api/v1/users` (me, update, delete).
- **Admin**: `/api/v1/admin`, `/api/v1/admin/recommendations`.
- **RBAC**: `/api/v1/rbac` (roles, permissions).
- **Secretary**: `/api/v1/secretary` (sessions, messages, stream, tools list).
- **Learning**: `/api/v1/learning` (records CRUD, search).
- **Medical paper**: `/api/v1/medical-paper`.
- **Others**: cities, weather, recommendations, emails, scheduled.

---

## 8. Conventions (from openspec/project.md)

- **Backend**: Black 88, Ruff (E,W,F,I,C,B), mypy strict. Layers: API → Service → DB/Models. Use `Depends()` for auth and DB.
- **Frontend**: Composition API, TypeScript strict, Pinia for global state, services in `src/services/`.
- **Git**: Branch naming `feature/...`, `fix/...`; commit prefix `feat:`, `fix:`, `docs:`, etc.
- **Security**: Secrets from env only; no raw user input to sensitive sinks; JWT + bcrypt; RBAC on protected routes.

---

## 9. OpenSpec Workflow

- **Main specs**: `openspec/specs/` (e.g. `personal-secretary-agent/spec.md`).
- **Changes**: `openspec/changes/` (proposal, design, tasks, delta specs). Archive completed under `openspec/changes/archive/`.
- **Project context**: `openspec/project.md` (purpose, stack, conventions, domain, constraints).
- **Cursor skills**: OpenSpec skills in `.cursor/skills/openspec-*` (new-change, apply-change, verify-change, archive-change, etc.).

---

## 10. Testing & Quality

- **Backend**: `tests/conftest.py` (db, client, test_user_token). In-memory SQLite per test. Run: `make test-backend` or `cd backend && poetry run pytest -v` (optional: `--cov=app`).
- **Frontend**: Unit with Vitest; e2e with Playwright (`frontend/tests/e2e/`, e.g. `secretary.spec.ts`). Run: `make test-frontend`, `npm run test:e2e`.
- **Lint**: `make lint` (backend: ruff + mypy; frontend: eslint). Format: `make format`.

---

## 11. Security Baseline (Workspace Rules)

- Validate and bound all external input; reject on failure.
- No raw user data into HTML/JSON/SQL/commands/logs; use parameterized/safe APIs.
- Secrets from env only; never in code or logs.
- Strong crypto, secure channels; solid auth and rate limiting where applicable.
- Centralize authorization (deny by default); log safely; minimize data exposure.

---

## 12. Where to Look for Common Tasks

| Task                     | Where to look |
|--------------------------|----------------|
| Add an API route         | `backend/app/api/v1/api.py` + new file in `endpoints/` |
| Add Secretary tool       | `backend/app/services/secretary_agent/tools/`, then register in sub_agent (learning/productivity/utility) |
| Change routing logic     | `backend/app/services/secretary_agent/agent.py` (supervisor node, RoutingDecision) |
| Auth / JWT               | `backend/app/core/security.py`, `api/deps.py` |
| DB model / migration     | `backend/app/models/`, `alembic/versions/` |
| Frontend Secretary UI    | `frontend/src/views/Secretary.vue`, `components/secretary/`, `stores/secretary.ts`, `services/secretary.service.ts` |
| Specs and changes        | `openspec/specs/`, `openspec/changes/`, `openspec/project.md` |

---

## 13. One-Page Cheat Sheet

```bash
# Setup (first time)
make setup && make install && make migrate

# Run
make run                    # backend :8000 + frontend :5173

# Test & quality
make test && make lint && make format

# Backend
make run-backend             # or: cd backend && poetry run uvicorn app.main:app --reload --port 8000
make test-backend            # cd backend && poetry run pytest -v
make migrate                # alembic upgrade head

# Frontend
make run-frontend            # cd frontend && npm run dev
make test-frontend           # npm run test
cd frontend && npm run test:e2e   # Playwright

# Users
make list-users
make reset-password EMAIL=user@example.com
make activate-user EMAIL=user@example.com
```

- **App**: http://localhost:5173  
- **API**: http://localhost:8000  
- **Docs**: http://localhost:8000/docs  
- **Specs**: `openspec/specs/`, `openspec/project.md`  
- **Secretary**: `backend/app/services/secretary_agent/agent.py` + `openspec/specs/personal-secretary-agent/spec.md`
