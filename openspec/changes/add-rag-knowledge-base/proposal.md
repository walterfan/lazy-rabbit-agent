## Why

The Lazy Rabbit Agent needs a **personal knowledge base** that allows users to upload study materials, technical documents, and notes, then retrieve relevant content through semantic search. This underpins RAG (Retrieval-Augmented Generation) capabilities for the AI Coach and future agents — grounding LLM responses in the user's own materials rather than relying solely on the model's training data.

**Key motivations:**

- Users upload documents (text, PDF, Markdown) → stored, chunked, and embedded for vector search
- Semantic query retrieves the most relevant chunks from the user's personal knowledge space
- The RAG engine is a **shared service** — used by Knowledge Base API endpoints, Coach sub-agent tools, and future agents
- Per-user isolation ensures documents and queries are scoped to the authenticated user
- Graceful degradation: if vector DB dependencies are unavailable, the system continues to function (without RAG features)

## What Changes

- Add a **RAG Engine** service module (`app/services/rag/`) using LlamaIndex embeddings + ChromaDB vector store
- Add a **KnowledgeDocument** database model for document metadata persistence
- Add **Knowledge Base API** endpoints (`/api/v1/knowledge/*`) for document CRUD, file upload, semantic query, and stats
- Add **frontend Knowledge Base view** with document management, file upload, and semantic search UI
- Add RAG-related configuration fields to `Settings` (ChromaDB path, chunk size, embedding model, etc.)
- Add new Python dependencies: `llama-index-embeddings-openai`, `chromadb`, `pypdf`

## Capabilities

### New Capabilities

- `rag-knowledge-base`: Upload, manage, and query a personal knowledge base using LlamaIndex embeddings + ChromaDB vector store. Supports text and file uploads (PDF/TXT/MD). Provides semantic search with configurable top-k. Per-user document isolation via metadata filtering.

### Modified Capabilities

- `personal-secretary-agent`: Configuration extended with RAG-related settings. RAG engine initialized on application startup.

## Impact

- **Backend**
  - `app/services/rag/engine.py` — RAG engine (chunking, embedding, vector CRUD, semantic query)
  - `app/services/rag/__init__.py` — Package exports
  - `app/models/knowledge_document.py` — SQLAlchemy model for document metadata
  - `app/schemas/knowledge.py` — Pydantic request/response schemas
  - `app/api/v1/endpoints/knowledge.py` — REST API endpoints
  - `app/api/v1/api.py` — Register knowledge router
  - `app/core/config.py` — RAG configuration fields
  - `app/main.py` — RAG engine initialization on startup
  - `app/models/__init__.py` — Export new model
  - `alembic/versions/` — Migration for `knowledge_documents` table
  - `pyproject.toml` — New dependencies
- **Frontend**
  - `src/views/KnowledgeBase.vue` — Document management + semantic search view
  - `src/services/knowledge.service.ts` — API service layer
  - `src/stores/knowledge.ts` — Pinia store
  - `src/types/knowledge.ts` — TypeScript interfaces
  - `src/router/index.ts` — New route
  - `src/components/layout/AppHeader.vue` — Navigation link
- **Data**
  - `data/chroma/` — ChromaDB persistent storage directory (gitignored)
- **Dependencies**
  - `llama-index-embeddings-openai >=0.3.0`
  - `chromadb >=0.5.0,<1.0.0`
  - `pypdf` (for PDF text extraction)
  - No new frontend dependencies
