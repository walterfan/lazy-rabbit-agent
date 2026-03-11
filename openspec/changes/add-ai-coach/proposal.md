## Why

Users need a **learning coach** that goes beyond simple Q&A — one that can leverage a personal knowledge base (RAG), track learning goals, log study sessions, and provide progress-aware coaching. The existing `ai-coach` example project (from `lazy-ai-primer`) has proven this concept with LlamaIndex + ChromaDB RAG, 3 coaching modes (coach/tutor/quiz), and learning plan tracking. Merging this into Lazy Rabbit Agent gives users a unified platform where the coach can work alongside the secretary, philosophy master, and other agents.

**Key motivations:**
- Users upload study materials → coach answers questions grounded in those materials (RAG)
- Users set learning goals with deadlines → coach tracks progress, streaks, and gives AI-powered feedback
- Three coaching modes serve different needs: motivational coaching, deep tutoring, and quiz-based assessment
- The existing secretary agent architecture (LangGraph supervisor + sub-agents) makes this a natural extension

## What Changes

- Add a **RAG Knowledge Base** service (LlamaIndex + ChromaDB) as a reusable backend module
- Add a **Coach sub-agent** to the SecretaryAgent supervisor workflow (4th sub-agent)
- Add **Knowledge Base API** endpoints (`/api/v1/knowledge/*`) for document CRUD and RAG query
- Add **Coach API** endpoints (`/api/v1/coach/*`) for learning goals, study sessions, progress tracking, and coach chat (3 modes with SSE streaming)
- Add **3 new DB tables**: `knowledge_documents`, `learning_goals`, `study_sessions` (via Alembic migration)
- Add **3 new frontend views**: Coach chat, Knowledge Base management, Learning Plan dashboard
- Add new Python dependencies: `llama-index`, `chromadb`

## Capabilities

### New Capabilities

- `rag-knowledge-base`: Upload, manage, and query a personal knowledge base using LlamaIndex + ChromaDB vector store. Supports text and file uploads (PDF/TXT/MD). Provides semantic search with configurable top-k and similarity threshold.
- `ai-coach-agent`: A coaching sub-agent with 3 modes (coach/tutor/quiz) that provides RAG-augmented responses, learning goal management, study session logging, and progress tracking with AI-generated feedback.
- `learning-plan-tracking`: Goal CRUD with deadlines and daily targets, study session logging with duration/difficulty/notes, progress reports with streak calculation and completion percentage.

### Modified Capabilities

- `secretary-agent`: Supervisor routing updated to include the new `coach_agent` node for coaching/learning/knowledge-related requests.

## Impact

- **Backend**
  - `app/services/rag/` — New RAG engine module (engine.py, config integration)
  - `app/services/secretary_agent/sub_agents/coach.py` — New coach sub-agent
  - `app/services/secretary_agent/tools/coach_tools.py` — Coach-specific tools (query_knowledge, create_goal, log_session, get_progress)
  - `app/services/secretary_agent/agent.py` — Updated supervisor routing
  - `app/api/v1/endpoints/knowledge.py` — New knowledge base API
  - `app/api/v1/endpoints/coach.py` — New coach API (goals, sessions, progress, chat)
  - `app/api/v1/api.py` — Register new routers
  - `app/models/knowledge_document.py`, `learning_goal.py`, `study_session.py` — New DB models
  - `app/schemas/knowledge.py`, `learning_goal.py` — New Pydantic schemas
  - `app/core/config.py` — RAG configuration fields
  - `app/main.py` — RAG engine initialization on startup
  - `alembic/versions/` — New migration for 3 tables
  - `pyproject.toml` — New dependencies (llama-index, chromadb)
- **Frontend**
  - `src/views/Coach.vue` — Coach chat with mode selector
  - `src/views/KnowledgeBase.vue` — Document upload/list/delete + query
  - `src/views/LearningPlan.vue` — Goals dashboard + study session log + progress
  - `src/services/coach.service.ts`, `knowledge.service.ts` — API services
  - `src/stores/coach.ts`, `knowledge.ts` — Pinia stores
  - `src/types/coach.ts`, `knowledge.ts` — TypeScript types
  - `src/router/index.ts` — New routes
  - Navigation — New menu entries
- **Dependencies**
  - `llama-index ^0.11.0` + sub-packages (llms-openai, embeddings-openai, vector-stores-chroma, readers-file)
  - `chromadb ^0.5.0`
  - No new frontend dependencies (reuses existing Axios, Pinia, Vue Router)
