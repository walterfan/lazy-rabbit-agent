## Context

- **Current state**: Lazy Rabbit Agent has a multi-agent supervisor architecture (LangGraph StateGraph) with 3 sub-agents (Learning, Productivity, Utility). It uses sync SQLAlchemy + Alembic, JWT auth, LangChain `ChatOpenAI` for LLM, and Vue 3 + TypeScript frontend.
- **Source**: The `ai-coach` example project (from `lazy-ai-primer/book/examples/ai-coach/`) provides a proven RAG + coaching implementation using LlamaIndex + ChromaDB + async SQLAlchemy + Vue 3 (JS).
- **Challenge**: Adapting ai-coach's async patterns and LlamaIndex-native LLM to lazy-rabbit's sync SQLAlchemy and LangChain-based agent architecture.

## Goals / Non-Goals

**Goals:**

- Integrate RAG knowledge base (LlamaIndex + ChromaDB) as a reusable service module
- Add Coach as a 4th sub-agent in the existing supervisor workflow
- Provide dedicated REST API endpoints for knowledge management and coaching features
- Support 3 coaching modes (coach/tutor/quiz) with RAG-augmented responses
- Track learning goals, study sessions, and progress with AI-generated feedback
- Add frontend views for coach chat, knowledge base, and learning plan
- Maintain consistency with existing code patterns (layered architecture, Depends(), Pinia stores)

**Non-Goals:**

- Replacing the existing LearningAgent (it handles word/topic/article learning; Coach handles goal-driven coaching with RAG)
- Multi-user shared knowledge bases (each user has their own knowledge space in v1)
- Real-time collaborative features
- PDF parsing beyond basic text extraction (no OCR, no complex table extraction)
- Migrating existing agents to use RAG (can be done in a future change)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  SecretaryAgent (Supervisor)                                │
│  Routes to sub-agents via LangGraph StateGraph              │
└──┬──────────────┬──────────────┬──────────────┬─────────────┘
   │              │              │              │
   ▼              ▼              ▼              ▼
┌──────────┐ ┌────────────┐ ┌──────────┐ ┌───────────┐
│ Learning │ │Productivity│ │ Utility  │ │  Coach    │ ← NEW
│  Agent   │ │   Agent    │ │  Agent   │ │  Agent    │
│ (words,  │ │ (notes,    │ │(weather, │ │(RAG,goals,│
│  topics, │ │  tasks,    │ │  calc,   │ │ sessions, │
│  articles│ │  reminders)│ │  time)   │ │ progress) │
└──────────┘ └────────────┘ └──────────┘ └─────┬─────┘
                                                │
                                           ┌────▼──────┐
                                           │ RAGEngine │
                                           │(LlamaIdx  │
                                           │+ChromaDB) │
                                           └───────────┘

API Routes (NEW):
  /api/v1/knowledge/documents          POST   Upload document
  /api/v1/knowledge/documents          GET    List documents
  /api/v1/knowledge/documents/{id}     DELETE Delete document
  /api/v1/knowledge/documents/file     POST   Upload file (PDF/TXT/MD)
  /api/v1/knowledge/query              POST   RAG query
  /api/v1/knowledge/stats              GET    Knowledge base stats
  /api/v1/coach/goals                  POST   Create learning goal
  /api/v1/coach/goals                  GET    List goals
  /api/v1/coach/goals/{id}             PATCH  Update goal
  /api/v1/coach/sessions               POST   Log study session
  /api/v1/coach/sessions               GET    List sessions (filter by goal)
  /api/v1/coach/progress/{goal_id}     GET    Progress report
  /api/v1/coach/chat                   POST   Coach chat (non-streaming)
  /api/v1/coach/chat/stream            POST   Coach chat (SSE streaming)
```

## Decisions

### 1. RAG Engine as independent service module (not embedded in agent)

- **Decision**: Create `app/services/rag/engine.py` as a standalone `RAGEngine` class that can be used by both the Coach sub-agent tools and the Knowledge API endpoints directly.
- **Rationale**: RAG is a cross-cutting capability. Other agents (medical paper, learning) may want to use it later. Keeping it independent follows the existing provider pattern.
- **Interface**:
  ```python
  class RAGEngine:
      def __init__(self, persist_dir, llm_settings)
      def add_document(self, doc_id, title, content, metadata) -> bool
      def delete_document(self, doc_id) -> bool
      def query(self, query_text, top_k=3, filters=None) -> RAGResult
      def get_stats(self) -> dict
  ```
- **Storage**: ChromaDB with persistent storage at `data/chroma/` (configurable via `CHROMA_PERSIST_DIR`).
- **Embedding**: LlamaIndex `OpenAIEmbedding` using lazy-rabbit's `LLM_BASE_URL` and `LLM_API_KEY` settings (OpenAI-compatible).

### 2. Coach as 4th sub-agent in LangGraph supervisor (not standalone endpoint)

- **Decision**: Add `coach_agent` as a new node in the existing `SecretaryAgent` StateGraph, alongside learning/productivity/utility agents.
- **Rationale**: Consistent with the existing multi-agent architecture. The supervisor can intelligently route coaching requests. Users can interact via the secretary chat or the dedicated coach chat endpoint.
- **Routing keywords**: "教练", "coach", "知识库", "knowledge", "学习目标", "goal", "学习进度", "progress", "quiz", "测验", "辅导", "tutor"
- **Alternative rejected**: Standalone agent (like philosophy master) — rejected because coach needs tight integration with RAG and learning data, and the supervisor pattern provides better context sharing.

### 3. Sync SQLAlchemy for new models (consistent with lazy-rabbit)

- **Decision**: Use sync SQLAlchemy models and Alembic migration, matching lazy-rabbit's existing pattern.
- **Rationale**: ai-coach uses async SQLAlchemy + aiosqlite, but lazy-rabbit is fully sync. Mixing async/sync would add complexity. LlamaIndex's core operations are sync-compatible.
- **Models**: `KnowledgeDocument`, `LearningGoal`, `StudySession` — all with `user_id` foreign key for per-user scoping.

### 4. LLM usage: LlamaIndex for RAG, LangChain for agent

- **Decision**: The RAG engine uses LlamaIndex's `OpenAI` LLM wrapper internally (for query engine). The Coach sub-agent uses LangChain's `ChatOpenAI` (consistent with other sub-agents). Both share the same `LLM_*` configuration.
- **Rationale**: LlamaIndex's query engine is tightly coupled with its own LLM abstraction. Rewriting it for LangChain would lose the battle-tested RAG pipeline. The coach sub-agent calls RAG via tools, so the LLM boundary is clean.
- **Config mapping**:
  - `LLM_BASE_URL` → LlamaIndex `api_base`
  - `LLM_API_KEY` → LlamaIndex `api_key`
  - `LLM_MODEL` → LlamaIndex `model`
  - New: `LLM_EMBEDDING_MODEL` (default: `text-embedding-3-small`)

### 5. Coach chat: dedicated endpoints (not reusing secretary chat)

- **Decision**: Add `POST /api/v1/coach/chat` and `POST /api/v1/coach/chat/stream` as dedicated endpoints, separate from secretary chat.
- **Rationale**: Coach chat has unique features (mode selection, RAG context injection, learning-data-aware prompts) that would complicate the secretary chat flow. Dedicated endpoints keep concerns separated.
- **Request contract**:
  ```json
  {
    "message": "string (required)",
    "mode": "coach|tutor|quiz (default: coach)",
    "session_id": "string (optional, for conversation continuity)",
    "goal_id": "string (optional, to scope coaching to a specific goal)"
  }
  ```
- **SSE protocol**: Same as existing secretary/philosophy streaming:
  ```
  data: {"type":"start","session_id":"..."}
  data: {"type":"token","content":"..."}
  data: {"type":"done","sources":[...]}
  data: {"type":"error","content":"..."}
  ```

### 6. Per-user knowledge isolation

- **Decision**: Each user has their own knowledge space. Documents are scoped by `user_id`. RAG queries filter by `user_id`.
- **Rationale**: Privacy and simplicity. Shared knowledge bases can be added later as a separate capability.
- **Implementation**: ChromaDB collection per user (`user_{user_id}`) or metadata filtering within a single collection. Metadata filtering is simpler and chosen for v1.

### 7. Coach system prompts: 3 modes with RAG context injection

- **Decision**: Three distinct system prompts (coach/tutor/quiz) stored in `prompts/coach.yaml`, with a `{rag_context}` placeholder that gets filled with retrieved knowledge before LLM call.
- **Prompt structure**:
  ```
  [System prompt for mode] +
  [RAG context: "📚 相关知识库内容:\n- [title] snippet..."] +
  [Learning progress context: "📊 当前学习进度:\n- Goal: X, 完成度: Y%"] +
  [Conversation history]
  ```
- **Rationale**: Matches ai-coach's proven approach. Progress context makes coaching personalized.

## Risks / Trade-offs

- **[Risk] ChromaDB adds ~200MB+ to dependencies** → **Mitigation**: Make RAG optional; if chromadb not installed, coach works without RAG (graceful degradation).
- **[Risk] LlamaIndex + LangChain coexistence** → **Mitigation**: They're independent; RAG engine is self-contained. No shared state.
- **[Risk] Embedding model costs** → **Mitigation**: Use `text-embedding-3-small` (cheapest); chunk size 512 to reduce token count; cache embeddings in ChromaDB.
- **[Trade-off] Sync DB limits concurrent RAG indexing** → **Acceptable**: Document upload is infrequent; indexing latency is acceptable for v1.
- **[Trade-off] Per-user ChromaDB filtering vs. per-user collections** → **Chose filtering**: Simpler, fewer collections to manage, good enough for single-user or small-team use.

## Migration Plan

- **Backend**:
  1. Add dependencies to `pyproject.toml`
  2. Add config fields to `Settings`
  3. Create RAG engine service
  4. Create DB models + Alembic migration
  5. Create schemas
  6. Create API endpoints (knowledge + coach)
  7. Create coach sub-agent + tools
  8. Update supervisor routing
  9. Initialize RAG engine on startup
- **Frontend**:
  1. Add types, services, stores
  2. Create 3 new views
  3. Update router and navigation
- **Rollback**:
  - Remove router registrations, delete new files, revert migration
  - ChromaDB data in `data/chroma/` can be deleted independently
  - No changes to existing tables

## Open Questions

1. Should coach chat sessions be stored in the same `chat_sessions`/`chat_messages` tables as secretary, or separate `coach_sessions` table? → **Recommendation**: Reuse existing tables with a `agent_type` field.
2. Should the RAG engine support URL-based document ingestion (fetch + index)? → **Recommendation**: Defer to v2; text/file upload is sufficient for v1.
3. Should quiz mode track scores and generate reports? → **Recommendation**: v1 keeps it simple (LLM-driven quiz); structured scoring in v2.
