# Project overview

## Purpose

**Lazy Rabbit Agent** is an AI-powered web application that provides a Personal Secretary agent (conversational AI with tools), recommendations, RBAC, weather, email, learning records, and a medical-paper writing assistant.

### High-level system (Mermaid)

```{mermaid}
flowchart TB
  subgraph Users
    U[End user]
    A[Admin]
  end
  subgraph App["Lazy Rabbit Agent"]
    FE[Frontend\nVue 3 + Pinia]
    BE[Backend\nFastAPI]
    FE --> BE
  end
  subgraph Backend["Backend"]
    Secretary[Personal Secretary\nLangGraph]
    Rec[Recommendations]
    Learning[Learning API]
    Auth[Auth / RBAC]
  end
  U --> FE
  A --> FE
  BE --> Secretary
  BE --> Rec
  BE --> Learning
  BE --> Auth
```

## Business boundaries

### What we do

- Personal Secretary: chat with tools (weather, notes, tasks, reminders, calculator, datetime, learning, articles).
- Multi-agent workflow: supervisor + Learning / Productivity / Utility sub-agents (LangGraph).
- User auth (JWT), RBAC, recommendations, weather integration, email, learning records persistence.

### What we don’t do

- (Define out-of-scope items as needed.)

## Key user roles

- **End user**: Uses Secretary chat, learning, recommendations.
- **Admin**: User management, RBAC, recommendations admin.
- **Super admin**: Full system and RBAC management.

## Core use cases

1. Chat with Personal Secretary (streaming, tools, sessions).
2. Learn words/sentences/topics/articles; save to learning records.
3. Manage notes, tasks, reminders via chat or tools.
4. Get recommendations (LLM + context).
5. Manage users and permissions (admin).

## Technology stack

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy 2, Pydantic 2, Alembic, JWT, LangChain/LangGraph.
- **Frontend**: Vue 3, TypeScript, Vite, Pinia, Vue Router, Tailwind.
- **Database**: SQLite (dev), PostgreSQL-ready.
- **Testing**: pytest, Vitest, Playwright.

## Deployment model

Monolith: single backend (FastAPI) + single frontend (Vite SPA). Docker/Compose and Nginx for production.

## Quality targets

- Performance: cached recommendations and weather; async I/O.
- Security: JWT, bcrypt, RBAC, env-based secrets.
