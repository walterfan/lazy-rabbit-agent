# Tasks: add-ai-coach

## 1. Dependencies and configuration

- [x] 1.1 Add `llama-index`, `llama-index-llms-openai`, `llama-index-embeddings-openai`, `llama-index-vector-stores-chroma`, `llama-index-readers-file`, `chromadb` to `pyproject.toml`
- [x] 1.2 Add RAG config fields to `app/core/config.py`: `CHROMA_PERSIST_DIR`, `RAG_CHUNK_SIZE`, `RAG_CHUNK_OVERLAP`, `RAG_SIMILARITY_TOP_K`, `LLM_EMBEDDING_MODEL`
- [x] 1.3 Verify `poetry lock && poetry install` succeeds with new dependencies (fixed version conflicts: pypdf ^4→>=5.1, httpx ^0.26→>=0.27, llama-index ^0.11→>=0.12)

## 2. Database models and migration

- [x] 2.1 Create `app/models/knowledge_document.py`: `KnowledgeDocument` model (id, user_id, title, content, tags, source, word_count, created_at, updated_at)
- [x] 2.2 Create `app/models/learning_goal.py`: `LearningGoal` model (id, user_id, subject, description, status, daily_target_minutes, deadline, created_at, completed_at)
- [x] 2.3 Create `app/models/study_session.py`: `StudySession` model (id, user_id, goal_id FK, duration_minutes, notes, difficulty, created_at)
- [x] 2.4 Create Alembic migration for the 3 new tables
- [x] 2.5 Register new models in `app/models/__init__.py` and User model relationships

## 3. Pydantic schemas

- [x] 3.1 Create `app/schemas/knowledge.py`: `DocumentUpload`, `DocumentResponse`, `FileUploadResponse`, `KnowledgeQuery`, `KnowledgeQueryResult`, `KnowledgeStats`
- [x] 3.2 Create `app/schemas/learning_goal.py`: `GoalCreate`, `GoalUpdate`, `GoalResponse`, `SessionCreate`, `SessionResponse`, `ProgressReport`
- [x] 3.3 Create `app/schemas/coach.py`: `CoachChatRequest` (message, mode, session_id, goal_id), `CoachChatResponse` (content, sources, session_id), `CoachMode` enum

## 4. RAG engine service

- [x] 4.1 Create `app/services/rag/__init__.py`
- [x] 4.2 Create `app/services/rag/engine.py`: `RAGEngine` class with `add_document()`, `delete_document()`, `query()`, `get_stats()` methods
- [x] 4.3 Configure LlamaIndex Settings (LLM, embedding model, chunk size) using lazy-rabbit's `LLM_*` config
- [x] 4.4 Implement ChromaDB persistent storage with user-scoped metadata filtering
- [x] 4.5 Add graceful degradation: if chromadb not available, RAG features return empty results with warning

## 5. Knowledge base API

- [x] 5.1 Create `app/api/v1/endpoints/knowledge.py` with routes:
  - `POST /documents` — upload text document
  - `POST /documents/file` — upload file (PDF/TXT/MD)
  - `GET /documents` — list user's documents
  - `DELETE /documents/{doc_id}` — delete document
  - `POST /query` — RAG semantic query
  - `GET /stats` — knowledge base statistics
- [x] 5.2 All endpoints require JWT auth via `Depends(get_current_active_user)`
- [x] 5.3 Implement per-user document scoping (filter by `user_id`)
- [x] 5.4 Register knowledge router in `app/api/v1/api.py` under prefix `/knowledge`

## 6. Coach API (goals, sessions, progress)

- [x] 6.1 Create `app/api/v1/endpoints/coach.py` with routes:
  - `POST /goals` — create learning goal
  - `GET /goals` — list goals (optional `?status=` filter)
  - `PATCH /goals/{id}` — update goal (status, description, deadline)
  - `POST /sessions` — log study session
  - `GET /sessions` — list sessions (optional `?goal_id=` filter)
  - `GET /progress/{goal_id}` — progress report with AI feedback
- [x] 6.2 Implement streak calculation logic (consecutive days with sessions)
- [x] 6.3 Implement AI feedback generation using LLM based on progress data
- [x] 6.4 Register coach router in `app/api/v1/api.py` under prefix `/coach`

## 7. Coach chat endpoints

- [x] 7.1 Add `POST /chat` to coach router: non-streaming coach chat with mode selection and RAG context injection
- [x] 7.2 Add `GET /chat/stream` to coach router: SSE streaming with same protocol as secretary/philosophy (`start` → `token` → `done`)
- [x] 7.3 Implement 3 system prompts (coach/tutor/quiz) in `app/services/secretary_agent/prompts/coach.yaml`
- [x] 7.4 Implement RAG context injection for coach/tutor modes (query knowledge base, format as prompt context)
- [x] 7.5 Implement learning progress context injection for coach mode
- [x] 7.6 Implement session continuity (load/save conversation history by session_id) — reuses ChatSession/ChatMessage models, loads last 20 messages, auto-creates sessions

## 8. Coach sub-agent integration

- [x] 8.1 Create `app/services/secretary_agent/sub_agents/coach.py`: `create_coach_agent()` and `create_coach_tools()` following the learning agent pattern
- [x] 8.2 Create `app/services/secretary_agent/tools/coach_tools.py`: tools for `query_knowledge`, `create_goal`, `log_study_session`, `get_progress`
- [x] 8.3 Add coach agent prompt to `app/services/secretary_agent/prompts/sub_agents.yaml`
- [x] 8.4 Update `app/services/secretary_agent/agent.py`: add `coach_agent` node to StateGraph, update supervisor routing keywords
- [x] 8.5 Initialize RAG engine in `app/main.py` startup and make it accessible to coach tools

## 9. Frontend: types, services, stores

- [x] 9.1 Create `frontend/src/types/knowledge.ts`: `KnowledgeDocument`, `KnowledgeQuery`, `KnowledgeResult`, `KnowledgeStats`
- [x] 9.2 Create `frontend/src/types/coach.ts`: `CoachMode`, `CoachChatRequest`, `CoachChatResponse`, `LearningGoal`, `StudySession`, `ProgressReport`
- [x] 9.3 Create `frontend/src/services/knowledge.service.ts`: API calls for document CRUD and query
- [x] 9.4 Create `frontend/src/services/coach.service.ts`: API calls for goals, sessions, progress, chat (including SSE streaming)
- [x] 9.5 Create `frontend/src/stores/knowledge.ts`: Pinia store for knowledge base state
- [x] 9.6 Create `frontend/src/stores/coach.ts`: Pinia store for coach state (goals, sessions, chat)

## 10. Frontend: views and navigation

- [x] 10.1 Create `frontend/src/views/Coach.vue`: chat UI with mode selector (coach/tutor/quiz), SSE streaming consumption, session management
- [x] 10.2 Create `frontend/src/views/KnowledgeBase.vue`: document list, upload form (text + file), delete, query interface with results display
- [x] 10.3 Create `frontend/src/views/LearningPlan.vue`: goals dashboard (create/list/update), study session log form, progress charts/stats
- [x] 10.4 Add routes `/coach`, `/knowledge`, `/learning-plan` to `frontend/src/router/index.ts` (auth required)
- [x] 10.5 Add navigation entries for Coach, Knowledge Base, Learning Plan in layout/header
- [x] 10.6 Add Coach agent card to Home page "AI Agents" section

## 11. Tests

- [x] 11.1 Backend: RAG engine unit tests (add/delete/query document, empty query, stats)
- [x] 11.2 Backend: Knowledge API tests (auth required, CRUD, query, per-user isolation)
- [x] 11.3 Backend: Coach API tests (goal CRUD, session logging, progress report, streak calculation)
- [x] 11.4 Backend: Coach chat tests (mode selection, streaming SSE format, session continuity)
- [x] 11.5 Backend: Coach sub-agent routing test (supervisor routes coaching keywords to coach agent)

## 12. Documentation

- [x] 12.1 Add coach and knowledge endpoints to API documentation
- [x] 12.2 Update README with AI Coach feature description and configuration (CHROMA_PERSIST_DIR, LLM_EMBEDDING_MODEL)
