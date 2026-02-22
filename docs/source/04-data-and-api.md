# Data and API

## Database overview

- **ORM**: SQLAlchemy 2. Migrations: Alembic under `backend/alembic/`.
- **Main tables**: users, roles, permissions, role_permission; chat_sessions, chat_messages; notes, tasks, reminders; learning_records; recommendations, cities, email_log; etc.

### Core entities (Mermaid)

```{mermaid}
erDiagram
  users ||--o{ chat_sessions : has
  users ||--o{ learning_records : has
  users }o--o{ roles : "role_permission"
  roles }o--o{ permissions : "role_permission"
  chat_sessions ||--o{ chat_messages : contains
  users ||--o{ notes : has
  users ||--o{ tasks : has
  users ||--o{ reminders : has

  users {
    int id PK
    string email
    string hashed_password
    datetime created_at
  }
  chat_sessions {
    uuid id PK
    int user_id FK
    string title
  }
  chat_messages {
    uuid id PK
    uuid session_id FK
    string role
    text content
  }
  learning_records {
    int id PK
    int user_id FK
    string type
    text user_input
    json response_payload
  }
```

## Core entities (examples)

- **User**: id, email, hashed_password, full_name, is_active, created_at, updated_at.
- **ChatSession**: id, user_id, title, created_at. **ChatMessage**: session_id, role, content, tool_calls, etc.
- **LearningRecord**: user_id, type (word/sentence/topic/question/idea/article), user_input, response_payload, deleted_at.

## External API

- **REST**: All under `/api/v1/`. Auth: `/api/v1/auth` (signup, signin). Secretary: `/api/v1/secretary` (sessions, messages, stream, tools). Learning: `/api/v1/learning`. OpenAPI: `/docs`, `/redoc`.
- **Auth**: Bearer JWT in `Authorization` header.

## Configuration

- Backend: `.env` (see `backend/` or project root). Key: `DATABASE_URL`, `SECRET_KEY`, `LLM_*`, `WEATHER_*`, `MAIL_*`.
- Frontend: `VITE_API_BASE_URL`, `VITE_WS_BASE_URL`.
