# Repository map

## Layering (Mermaid)

```{mermaid}
flowchart LR
  subgraph Frontend
    V[views/]
    C[components/]
    S[stores/]
    Sv[services/]
    V --> C
    V --> S
    V --> Sv
  end
  subgraph Backend
    EP[endpoints/]
    Svc[services/]
    M[models/]
    EP --> Svc
    Svc --> M
  end
  Frontend -->|HTTP/WS| Backend
```

```
lazy-rabbit-agent/
├── backend/                 # FastAPI app (Poetry, Python 3.11+)
│   ├── app/
│   │   ├── main.py           # Entry, CORS, middleware
│   │   ├── api/v1/           # Routes (api.py, endpoints/*)
│   │   ├── core/             # config, security
│   │   ├── db/               # SQLAlchemy base, session
│   │   ├── models/           # User, ChatSession, Note, Task, Reminder, LearningRecord, ...
│   │   ├── schemas/          # Pydantic
│   │   └── services/         # Business logic
│   │       └── secretary_agent/   # Supervisor + sub-agents, tools
│   ├── alembic/
│   ├── tests/
│   └── pyproject.toml
├── frontend/                 # Vue 3 + TypeScript + Vite
│   ├── src/views/            # Secretary.vue, Learning.vue, ...
│   ├── src/components/       # secretary/*, layout/*
│   ├── src/stores/           # Pinia
│   ├── src/services/
│   └── package.json
├── docs/                     # Project docs
│   ├── source/               # Sphinx/MyST source (this PKP)
│   ├── build/                # Sphinx HTML output
│   └── PROJECT-KNOWLEDGE-PACK.md
├── openspec/                 # Specs and change workflow
├── Makefile                  # install, run, test, lint, migrate
└── .env
```

## Directory responsibilities

| Path | Purpose |
|------|---------|
| `backend/app/api/v1/endpoints/` | API route handlers |
| `backend/app/services/` | Business logic, secretary_agent, chat, LLM, weather, etc. |
| `backend/app/models/` | SQLAlchemy models |
| `frontend/src/views/` | Page-level components |
| `frontend/src/stores/` | Pinia state |
| `docs/source/` | Sphinx/MyST doc source |
| `openspec/specs/` | Main specs (e.g. personal-secretary-agent) |

## Key entry points

- **Backend**: `backend/app/main.py` → `app.api.v1.api.api_router`
- **Secretary agent**: `backend/app/services/secretary_agent/agent.py` (`SecretaryAgent`, `chat` / `chat_stream`)
- **Secretary API**: `backend/app/api/v1/endpoints/secretary.py`
- **Frontend app**: `frontend/src/main.ts`, router in `frontend/src/router/`

## Conventions

- **Naming**: PascalCase classes, snake_case functions/variables; Vue components PascalCase.
- **Layering**: API → Service → DB/Models (backend); Views → Components → Services → Stores (frontend).
