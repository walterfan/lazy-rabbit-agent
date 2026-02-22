# Architecture

## Component overview

- **Frontend (Vue 3)**: SPA; Pinia stores; Axios to backend; Secretary and Learning views.
- **Backend (FastAPI)**: REST API; JWT auth; RBAC; services for secretary, chat, learning, recommendations, weather, email.
- **Secretary agent**: Supervisor (LangGraph) routes to Learning / Productivity / Utility sub-agents; each sub-agent has its own tools; A2A protocol for sub-agent responses.

### System context (Mermaid)

```{mermaid}
flowchart LR
  subgraph Client
    Browser[Browser]
  end
  subgraph Backend["Backend (FastAPI)"]
    API[API /auth /users /secretary /learning ...]
    Services[Services]
    API --> Services
  end
  subgraph Secretary["Secretary Agent"]
    Supervisor[Supervisor]
    Learning[Learning Agent]
    Productivity[Productivity Agent]
    Utility[Utility Agent]
    Supervisor --> Learning
    Supervisor --> Productivity
    Supervisor --> Utility
  end
  Browser -->|HTTPS| API
  Services --> Secretary
  Services --> DB[(DB)]
```

### Secretary agent architecture (Mermaid)

```{mermaid}
flowchart TB
  User([User message])
  User --> Supervisor
  subgraph Supervisor["SecretaryAgent (Supervisor)"]
    Route[Route by intent]
  end
  Route --> Learning
  Route --> Productivity
  Route --> Utility
  Route -->|FINISH| Out([Response])
  subgraph Learning["Learning Agent"]
    LTools[learn_word, learn_sentence, learn_topic,\nanswer_question, plan_idea, learn_article]
  end
  subgraph Productivity["Productivity Agent"]
    PTools[note, task, reminder]
  end
  subgraph Utility["Utility Agent"]
    UTools[weather, calculator, datetime]
  end
  Learning --> Out
  Productivity --> Out
  Utility --> Out
```

### Backend layering (Mermaid)

```{mermaid}
flowchart TD
  subgraph API["API layer"]
    Endpoints[endpoints/]
  end
  subgraph Service["Service layer"]
    Secretary[secretary_agent]
    Chat[chat_service]
    Learning[learning_service]
    Other[weather, email, rbac, ...]
  end
  subgraph Data["Data layer"]
    Models[models/]
    DB[(SQLAlchemy / DB)]
  end
  Endpoints --> Secretary
  Endpoints --> Chat
  Endpoints --> Learning
  Endpoints --> Other
  Secretary --> Models
  Chat --> Models
  Learning --> Models
  Other --> Models
  Models --> DB
```

## Key call chains

### Secretary chat

```
HTTP POST /api/v1/secretary/sessions/{id}/messages
  → secretary endpoint (auth)
  → chat_service + SecretaryAgent.chat_stream()
  → Supervisor → SubAgent (Learning | Productivity | Utility)
  → Tools (e.g. weather, note, learn_word)
  → Stream response back
```

### Learning record save

```
User confirms in chat → Learning sub-agent tool (e.g. save_learning)
  → learning_service / DB
  → learning_records table
```

## Module dependencies

- API layer depends on services and schemas only.
- Services depend on models, db session, and core config.
- Secretary agent depends on LangChain/LangGraph, prompts, sub_agents, tools.

## Cross-cutting concerns

- **Authentication**: JWT in `core/security.py`; `Depends(get_current_user)` in endpoints.
- **Authorization**: RBAC in `rbac_service`; `require_permission()` in routes.
- **Logging**: Standard logging; request logging middleware in `main.py`.
- **Config**: `core/config.py` from env; no secrets in code.

### Auth and RBAC (Mermaid)

```{mermaid}
sequenceDiagram
  actor User
  participant FE as Frontend
  participant API as API
  participant Auth as get_current_user
  participant RBAC as require_permission
  participant SVC as Service

  User->>FE: Request (with JWT)
  FE->>API: Authorization: Bearer token
  API->>Auth: Depends(get_current_user)
  Auth->>Auth: Verify JWT, load user
  Auth->>API: current_user
  API->>RBAC: require_permission(perm)
  RBAC->>RBAC: Check role permissions
  RBAC->>API: OK
  API->>SVC: Business logic
  SVC->>API: Result
  API->>FE: Response
  FE->>User: Response
```
