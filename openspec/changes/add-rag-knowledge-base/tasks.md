## Tasks

### 1. Backend: RAG engine with pluggable vector store
- [x] Create `app/services/rag/__init__.py` package
- [x] Create `app/services/rag/vector_store.py` — `BaseVectorStore` interface + backends:
  - `PgVectorStore` — PostgreSQL + pgvector extension (creates `document_chunks` table)
  - `ChromaVectorStore` — ChromaDB embedded on-disk (fallback)
- [x] Create `app/services/rag/engine.py` with `RAGEngine` class
  - `_resolve_store_type()` — auto-detect: PostgreSQL→pgvector, SQLite→disabled
  - `_initialize()` — init embedding model + selected vector store backend
  - `add_document()` — chunk, embed, upsert via `BaseVectorStore`
  - `delete_document()` — remove chunks via `BaseVectorStore`
  - `query()` — embed query, vector search with user_id filter
  - `get_stats()` — chunk/document counts
  - `_chunk_text()` — sentence-aware character chunking
  - `backend_name` property — "pgvector", "chromadb", or "disabled"
- [x] Add `init_rag_engine()` / `get_rag_engine()` singleton pattern
- [x] Graceful degradation: SQLite → disabled; missing deps → disabled

### 2. Backend: Configuration
- [x] Add to `app/core/config.py`:
  - `VECTOR_STORE` — "auto" (default), "pgvector", "chromadb", "disabled"
  - `CHROMA_PERSIST_DIR`, `RAG_CHUNK_SIZE`, `RAG_CHUNK_OVERLAP`, `RAG_SIMILARITY_TOP_K`
  - `EMBEDDING_API_KEY`, `EMBEDDING_BASE_URL`, `EMBEDDING_MODEL`
  - `LLM_EMBEDDING_MODEL` (fallback)
- [x] Update `.env.sample` with VECTOR_STORE + embedding config examples

### 3. Backend: Database model + migration
- [x] Create `app/models/knowledge_document.py` (`KnowledgeDocument` model)
- [x] Export model in `app/models/__init__.py`
- [x] Add `knowledge_documents` relationship to `User` model
- [x] Create Alembic migration for `knowledge_documents` table

### 4. Backend: API schemas
- [x] Create `app/schemas/knowledge.py`
  - Request: `DocumentUpload`, `KnowledgeQuery`
  - Response: `DocumentResponse`, `FileUploadResponse`, `KnowledgeQueryResult`, `KnowledgeQueryResponse`, `KnowledgeStats`

### 5. Backend: API endpoints
- [x] Create `app/api/v1/endpoints/knowledge.py`
  - `POST /documents` — text upload
  - `POST /documents/file` — file upload (PDF/TXT/MD, 10MB limit)
  - `GET /documents` — list user's documents
  - `DELETE /documents/{doc_id}` — delete document (DB + ChromaDB)
  - `POST /query` — semantic search
  - `GET /stats` — knowledge base statistics
- [x] Register knowledge router in `app/api/v1/api.py`

### 6. Backend: App startup integration
- [x] Call `init_rag_engine()` with settings in `app/main.py` startup

### 7. Backend: Dependencies
- [x] Add to `pyproject.toml`: `llama-index-embeddings-openai`, `pgvector`, `pypdf`
- [x] Make `chromadb` and full `llama-index` optional (`poetry install -E chromadb`)
- [x] Add `psycopg2-binary` as optional postgres extra

### 8. Frontend: Types + service + store
- [x] Create `src/types/knowledge.ts` — TypeScript interfaces
- [x] Create `src/services/knowledge.service.ts` — API client methods
- [x] Create `src/stores/knowledge.ts` — Pinia store with actions/state

### 9. Frontend: Knowledge Base view
- [x] Create `src/views/KnowledgeBase.vue`
  - Stats panel (documents, words, chunks)
  - File upload form (PDF/TXT/MD)
  - Manual text upload form (title + content + tags)
  - Semantic search input + results display
  - Document list with delete
- [x] Add route in `src/router/index.ts`
- [x] Add nav link in `AppHeader.vue`

### 10. Testing
- [x] Create `tests/test_knowledge_api.py` — endpoint tests

### 11. Known issues to address (post-v1)
- [ ] Fix `stats.tags` — frontend expects it but backend doesn't return it
- [ ] Align `top_k` default (frontend=5, backend=3)
- [x] Fix `_chunk_text()` edge case (infinite loop guard fixed in refactor)
- [ ] Add unit tests for chunking edge cases (empty text, single sentence, Unicode)
- [ ] Add document update endpoint (`PATCH /documents/{doc_id}`)
- [ ] Add HNSW index on pgvector `embedding` column for large datasets
- [ ] Store `embedding_model` name in chunk metadata for stale vector detection
- [ ] Add hybrid search (pgvector + PostgreSQL full-text) for keyword+semantic
