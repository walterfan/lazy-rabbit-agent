## Context

- **Current state**: Lazy Rabbit Agent has a multi-agent supervisor architecture (LangGraph StateGraph) with sub-agents, sync SQLAlchemy + Alembic, JWT auth, and Vue 3 + TypeScript frontend. LLM integration uses OpenAI-compatible APIs via `LLM_BASE_URL` / `LLM_API_KEY`.
- **Goal**: Add a personal knowledge base with RAG (Retrieval-Augmented Generation) that stores user documents, chunks and embeds them, and provides semantic search. The RAG engine must be a shared service usable by multiple consumers (REST API, Coach agent, future agents).
- **Constraint**: Must work with corporate and self-hosted LLM gateways (OpenAI LLM Gateway, DeepSeek, Ollama, vLLM, Alibaba DashScope, etc.) via OpenAI-compatible API, not just OpenAI directly.

## Current Embedding Configuration

The project uses a **dedicated embedding provider** configured separately from the chat LLM. This is the standard deployment pattern:

```
# Chat LLM (e.g. Claude via OpenAI LLM Gateway)
LLM_PROVIDER=claude
LLM_API_KEY="sk-..."
LLM_BASE_URL="https://llm.fanyamin.com/v1"
LLM_MODEL="claude-opus-4-6"

# Embedding LLM (e.g. Qwen3 embedding via OpenAI LLM Gateway)
EMBEDDING_API_KEY="llmgw-sk-..."
EMBEDDING_BASE_URL="https://llm.fanyamin.com/v1"
EMBEDDING_MODEL="local_qwen3_embed"
```

The embedding config is **always loaded at startup** and passed to the RAG engine. The fallback chain is:

```
EMBEDDING_API_KEY  → (if empty) → LLM_API_KEY
EMBEDDING_BASE_URL → (if empty) → LLM_BASE_URL
EMBEDDING_MODEL    → (if empty) → LLM_EMBEDDING_MODEL → "text-embedding-3-small"
```

Users can also override these per-user via the LLM Settings UI (`/admin/llm-settings`), stored in the `llm_settings` table.

### Supported Embedding Providers

| Provider | Base URL | Model | Dimensions | Notes |
|----------|----------|-------|------------|-------|
| OpenAI | `https://api.openai.com/v1` | `text-embedding-3-small` | 1536 | Cheapest, ~$0.02/1M tokens |
| OpenAI | `https://api.openai.com/v1` | `text-embedding-3-large` | 3072 | Higher quality |
| Alibaba DashScope | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `text-embedding-v4` | 1024 | Good for Chinese/bilingual |
| OpenAI LLM Gateway | `https://llm-gateway-*.fanyamin.com/v1` | `local_qwen3_embed` | varies | Internal, OpenAI-compatible |
| DeepSeek | `https://api.deepseek.com` | — | — | Chat-only, no embeddings |
| Ollama (local) | `http://localhost:11434/v1` | `nomic-embed-text` | 768 | Free, local |

## Goals / Non-Goals

**Goals:**

- Provide a self-contained RAG engine as a reusable service module
- Support document upload (text + file), deletion, listing, and semantic query
- Per-user document isolation (privacy by default)
- Graceful degradation when vector DB or embedding dependencies are unavailable
- Configurable embedding model and API endpoint (separate from chat LLM)
- Simple, maintainable chunking strategy suitable for knowledge articles and study notes

**Non-Goals:**

- Multi-user shared knowledge bases (per-user only in v1)
- Advanced document parsing (OCR, complex table extraction, image-to-text)
- Hybrid search (keyword + vector) — pure vector similarity in v1
- Re-ranking or multi-stage retrieval pipelines
- Document versioning or diff tracking
- URL-based document ingestion (fetch and index from URL) — defer to v2

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Vue 3)                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  KnowledgeBase.vue                                   │   │
│  │  ┌──────────────┐ ┌─────────────┐ ┌──────────────┐  │   │
│  │  │ File Upload  │ │ Doc Manager │ │Semantic Query│  │   │
│  │  └──────┬───────┘ └──────┬──────┘ └──────┬───────┘  │   │
│  └─────────┼────────────────┼───────────────┼───────────┘   │
│            │                │               │               │
│  ┌─────────▼────────────────▼───────────────▼───────────┐   │
│  │ knowledge.service.ts → Pinia store (knowledge.ts)    │   │
│  └──────────────────────────┬───────────────────────────┘   │
└─────────────────────────────┼───────────────────────────────┘
                              │ HTTP (JWT auth)
┌─────────────────────────────▼───────────────────────────────┐
│                    FastAPI Backend                           │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  /api/v1/knowledge/*  (knowledge.py endpoints)        │  │
│  └───────────────────────────┬───────────────────────────┘  │
│                              │                              │
│  ┌───────────────────────────▼───────────────────────────┐  │
│  │              RAGEngine (services/rag/engine.py)        │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────┐  │  │
│  │  │   Chunker    │  │  Embedder    │  │VectorStore │  │  │
│  │  │ (char-based, │  │ (LlamaIndex  │  │(pluggable) │  │  │
│  │  │  sentence-   │  │  OpenAI-     │  │            │  │  │
│  │  │  aware)      │  │  compatible) │  │            │  │  │
│  │  └──────────────┘  └──────┬───────┘  └──────┬─────┘  │  │
│  └───────────────────────────┼──────────────────┼────────┘  │
│                              │                  │           │
│  ┌───────────────────────────▼──────┐           │           │
│  │  Embedding API (OpenAI-compat)   │     ┌─────▼───────┐  │
│  │  EMBEDDING_BASE_URL              │     │ Backend:    │  │
│  │  e.g. OpenAI LLM Gateway,         │     │             │  │
│  │  DashScope, OpenAI, Ollama       │     │ PostgreSQL: │  │
│  └──────────────────────────────────┘     │  pgvector   │  │
│                                           │  (document_ │  │
│                                           │   chunks)   │  │
│                                           │             │  │
│                                           │ — OR —      │  │
│                                           │             │  │
│                                           │ ChromaDB:   │  │
│                                           │  data/chroma│  │
│                                           │             │  │
│                                           │ — OR —      │  │
│                                           │             │  │
│                                           │ SQLite:     │  │
│                                           │  DISABLED   │  │
│                                           └─────────────┘  │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  PostgreSQL / SQLite                                  │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │  knowledge_documents table (metadata, content)  │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow: Document Upload

```
User uploads document (text or file)
       │
       ▼
  ┌──────────────┐
  │ API Endpoint  │  Validates input, extracts text (PDF→pypdf)
  └──────┬───────┘
         │
    ┌────▼─────┐         ┌─────────────────┐
    │ Save to  │────────▶│  PostgreSQL /    │  Metadata: id, user_id,
    │   DB     │         │  SQLite          │  title, content, tags,
    └────┬─────┘         └─────────────────┘  source, word_count
         │
    ┌────▼──────────────┐
    │  RAGEngine.       │
    │  add_document()   │
    └────┬──────────────┘
         │
    ┌────▼──────────┐         ┌──────────────────┐
    │ _chunk_text() │────────▶│ Chunks            │  512 chars, 50 overlap,
    └────┬──────────┘         │ (sentence-aware)  │  sentence boundaries
         │                    └──────────────────┘
    ┌────▼──────────────────┐
    │ embed_model.          │──── HTTP ────▶ Embedding API
    │ get_text_embedding_   │               (local_qwen3_embed /
    │ batch(chunks)         │◀──────────────  text-embedding-v4 /
    └────┬──────────────────┘                 text-embedding-3-small)
         │
    ┌────▼──────────────┐
    │ collection.       │────────▶ ChromaDB (on-disk)
    │ upsert(ids,       │         Stored: chunk text + vector +
    │  embeddings,      │         metadata {doc_id, title,
    │  documents,       │         user_id, chunk_index}
    │  metadatas)       │
    └───────────────────┘
```

### Data Flow: Semantic Query

```
User sends query: "How does WebRTC signaling work?"
       │
       ▼
  ┌──────────────┐
  │ API Endpoint  │  Validates query, extracts user_id from JWT
  └──────┬───────┘
         │
    ┌────▼──────────────────┐
    │  RAGEngine.query()    │
    └────┬──────────────────┘
         │
    ┌────▼──────────────────┐
    │ embed_model.          │──── HTTP ────▶ Embedding API
    │ get_text_embedding(   │◀──────────────  (query vector)
    │   query_text)         │
    └────┬──────────────────┘
         │
    ┌────▼──────────────────┐
    │ collection.query(     │────────▶ ChromaDB
    │   query_embeddings,   │         HNSW cosine similarity
    │   n_results=top_k,    │         filtered by user_id
    │   where={user_id})    │◀────────  results + distances
    └────┬──────────────────┘
         │
    ┌────▼──────────────────┐
    │ Convert distances to  │  score = 1.0 - cosine_distance
    │ similarity scores     │
    └────┬──────────────────┘
         │
         ▼
  RAGQueryResponse {
    results: [{ content, score, metadata }],
    query: "How does WebRTC signaling work?",
    total: 3
  }
```

### Storage Model

```
┌──────────────────────────────────────────────────────────────────────┐
│  PostgreSQL (pgvector backend — RECOMMENDED)                         │
│                                                                      │
│  knowledge_documents (metadata)    document_chunks (vectors)         │
│  ┌────────────────────────────┐    ┌──────────────────────────────┐  │
│  │ id (UUID PK)              │    │ id (TEXT PK)                 │  │
│  │ user_id (FK → users)      │    │ content (TEXT)               │  │
│  │ title (varchar 500)       │    │ embedding (vector)           │  │
│  │ content (text, full body) │    │ doc_id (TEXT, indexed)       │  │
│  │ tags (JSON array)         │    │ title (TEXT)                 │  │
│  │ source (varchar 255)      │    │ user_id (TEXT, indexed)      │  │
│  │ word_count (integer)      │    │ chunk_index (INTEGER)        │  │
│  │ created_at (datetime)     │    └──────────────────────────────┘  │
│  │ updated_at (datetime)     │                                      │
│  └────────────────────────────┘    Cosine distance: <=> operator    │
│                                    Same database, same transaction   │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│  SQLite (RAG DISABLED)                                               │
│                                                                      │
│  knowledge_documents (metadata)    Vector search: NOT AVAILABLE      │
│  ┌────────────────────────────┐    Documents can still be uploaded   │
│  │ (same schema as above)    │    and stored, but semantic query    │
│  └────────────────────────────┘    returns empty results.            │
│                                                                      │
│  To enable RAG: switch DATABASE_URL to PostgreSQL with pgvector.     │
│  Or set VECTOR_STORE=chromadb to use embedded ChromaDB (fallback).   │
└──────────────────────────────────────────────────────────────────────┘

Note: embedding dimension varies by model — 768 (Ollama), 1024 (DashScope),
      1536 (OpenAI small), 3072 (OpenAI large). pgvector handles dynamic dims.
```

## Decisions

### 1. RAG Engine as standalone service module

- **Decision**: Create `app/services/rag/engine.py` as a self-contained `RAGEngine` class with a global singleton accessor (`get_rag_engine()`).
- **Rationale**: RAG is a cross-cutting capability. The knowledge API endpoints call it directly for document CRUD and query. The Coach sub-agent tools call it for RAG-augmented coaching. Future agents can also use it. Keeping it independent follows the existing provider/service pattern.
- **Interface**:
  ```python
  class RAGEngine:
      def add_document(doc_id, title, content, user_id, metadata) -> bool
      def delete_document(doc_id) -> bool
      def query(query_text, user_id, top_k) -> RAGQueryResponse
      def get_stats(user_id) -> dict
      @property
      def is_available -> bool
      @property
      def init_error -> Optional[str]
  ```
- **Singleton**: `init_rag_engine()` called once at app startup; `get_rag_engine()` returns the instance. Avoids re-initialization and ChromaDB lock contention.

### 2. Pluggable vector store with pgvector as primary backend

- **Decision**: Use a pluggable `BaseVectorStore` interface with two implementations. pgvector (PostgreSQL) is the recommended production backend. ChromaDB is available as a fallback. When the database is SQLite, RAG is automatically disabled.

- **Architecture**:

  ```
  RAGEngine  ──────▶  BaseVectorStore (abstract)
                          │
                ┌─────────┼──────────┐
                ▼         ▼          ▼
          PgVectorStore  ChromaVS  (disabled)
          (PostgreSQL)   (embedded)  (SQLite)
  ```

- **Backend selection logic** (`VECTOR_STORE` setting):

  | `VECTOR_STORE` | `DATABASE_URL` | Result |
  |----------------|----------------|--------|
  | `auto` (default) | `postgresql://...` | **pgvector** |
  | `auto` (default) | `sqlite:///...` | **disabled** (with log message) |
  | `pgvector` | any | pgvector (fails if not PostgreSQL) |
  | `chromadb` | any | ChromaDB embedded |
  | `disabled` | any | RAG off |

- **Why pgvector as primary**:
  1. **Single database**: Document metadata (`knowledge_documents`) and vector chunks (`document_chunks`) live in the same PostgreSQL instance — same transactions, same backups, same connection pool
  2. **No extra infrastructure**: pgvector is a PostgreSQL extension (`CREATE EXTENSION vector`), not a separate server
  3. **ACID consistency**: Document insert + vector insert happen atomically; no orphaned vectors
  4. **Multi-process safe**: PostgreSQL MVCC handles concurrent reads/writes from multiple backend processes
  5. **SQL-native filtering**: `WHERE user_id = :uid` is a standard SQL clause, not a custom metadata API
  6. **Hybrid search ready**: PostgreSQL full-text search (`tsvector`) can be combined with vector search in a single query (future)
  7. **Production proven**: pgvector handles millions of vectors with IVFFlat or HNSW indexes

- **Why keep ChromaDB as fallback**:
  - Zero-config local development without PostgreSQL
  - `VECTOR_STORE=chromadb` works with any `DATABASE_URL` (even SQLite for metadata)

- **Full Comparison**:

  | Criteria | pgvector (chosen) | ChromaDB (fallback) | Qdrant | Milvus |
  |----------|----------|----------|--------|--------|
  | **Deployment** | PG extension | Embedded (in-process) | Separate server or embedded | Separate server |
  | **Setup** | `CREATE EXTENSION vector` | `pip install chromadb` | Docker or pip | Docker + etcd + MinIO |
  | **ACID** | Yes | No | No | No |
  | **Multi-process** | Yes (MVCC) | No (single-writer) | Yes | Yes |
  | **Hybrid search** | Full-text + vector | No | BM25 + vector | Sparse + dense |
  | **p50 latency (1M vec)** | ~18ms | ~12ms | ~4ms | ~6ms |
  | **Max practical scale** | <1M vectors | <1M vectors | Billions | Billions |
  | **Extra dependency** | `pgvector` pip + PG extension | ~200MB pip package | ~100MB Docker | Heavy |

- **pgvector `document_chunks` table** (created on engine init, not via Alembic):

  ```sql
  CREATE TABLE IF NOT EXISTS document_chunks (
      id          TEXT PRIMARY KEY,            -- "{doc_id}_chunk_{i}"
      content     TEXT NOT NULL,               -- chunk text
      embedding   vector,                      -- pgvector column (dynamic dimension)
      doc_id      TEXT NOT NULL,               -- FK-like ref to knowledge_documents.id
      title       TEXT,
      user_id     TEXT NOT NULL,
      chunk_index INTEGER NOT NULL DEFAULT 0
  );
  CREATE INDEX idx_chunks_user_id ON document_chunks (user_id);
  CREATE INDEX idx_chunks_doc_id  ON document_chunks (doc_id);
  ```

### 3. SQLite graceful disable: RAG off, documents still stored

- **Decision**: When `DATABASE_URL` is SQLite and `VECTOR_STORE=auto`, the RAG engine initializes with `is_available=False` and `init_error` explaining that PostgreSQL is required. Document upload/delete/list still work (metadata in SQLite). Only semantic query returns empty results with an explanatory message.
- **Rationale**: SQLite cannot host pgvector. Rather than requiring ChromaDB as a mandatory dependency for SQLite users, we disable vector search and keep the rest of the application functional. Users who want RAG on SQLite can explicitly set `VECTOR_STORE=chromadb`.
- **User experience**:
  - Upload document → saved to SQLite ✓, vector indexing skipped (logged)
  - List documents → works ✓
  - Delete document → removed from SQLite ✓, vector cleanup skipped
  - Semantic query → returns `{"results": [], "message": "RAG disabled (SQLite)..."}`
  - Knowledge stats → shows `total_chunks: 0`

### 4. LlamaIndex only for embeddings (not full index pipeline)

- **Decision**: Use `llama-index-embeddings-openai` (`OpenAIEmbedding`) for embedding generation. Do NOT use LlamaIndex's `VectorStoreIndex` or query engine pipeline.
- **Rationale**: The full LlamaIndex index pipeline (VectorStoreIndex → QueryEngine → response synthesis) adds complexity and couples RAG retrieval with LLM response generation. For this use case, we only need: (a) embed text chunks, (b) store in ChromaDB, (c) embed query, (d) retrieve similar chunks. ChromaDB's native API handles storage and retrieval; we only need LlamaIndex for its `OpenAIEmbedding` wrapper which works with any OpenAI-compatible endpoint.
- **Trade-off**: We lose LlamaIndex's built-in re-ranking and response synthesis, but gain simplicity and full control over the retrieval pipeline.
- **Note**: The `OpenAIEmbedding` class works with any OpenAI-compatible endpoint — tested with OpenAI LLM Gateway (`local_qwen3_embed`), Alibaba DashScope (`text-embedding-v4`), and OpenAI (`text-embedding-3-small`).

### 5. Embedding configuration: dedicated settings with fallback chain

- **Decision**: The embedding API is configured via dedicated `EMBEDDING_*` environment variables in `.env`. These are the **primary** embedding settings, not fallbacks. The `LLM_*` variables are for chat only.
- **Configuration hierarchy** (highest priority first):
  1. Per-user override in `llm_settings` table (set via LLM Settings UI)
  2. `EMBEDDING_API_KEY` / `EMBEDDING_BASE_URL` / `EMBEDDING_MODEL` in `.env`
  3. Fallback to `LLM_API_KEY` / `LLM_BASE_URL` / `LLM_EMBEDDING_MODEL`
- **Rationale**: In practice, chat and embedding are almost always different providers. DeepSeek has no embedding API. Claude (via OpenAI LLM Gateway) uses a separate embedding model (`local_qwen3_embed`). Making `EMBEDDING_*` the primary config reflects this reality.
- **Current production config**:
  ```
  EMBEDDING_API_KEY="sk-..."
  EMBEDDING_BASE_URL="https://lazy-studio.com/api/v1"
  EMBEDDING_MODEL="lazy_qwen3_embed"
  ```

### 6. Character-based chunking with sentence boundary awareness

- **Decision**: Custom chunking in `_chunk_text()` — 512 character chunks with 50 character overlap, breaking at sentence boundaries.
- **Alternatives considered**:
  | Strategy | Pros | Cons |
  |----------|------|------|
  | Fixed character | Simple, predictable size | Splits mid-sentence |
  | Sentence-aware (chosen) | Readable chunks, preserves meaning | Slightly variable size |
  | Token-based | Aligns with model limits | Requires tokenizer, slower |
  | Semantic (paragraph) | Best meaning preservation | Highly variable size |
  | LlamaIndex SentenceSplitter | Battle-tested | Extra dependency, less control |
- **Rationale**: Study notes and technical articles benefit from sentence-level coherence. The chunker looks backward from the chunk boundary for sentence-ending punctuation (`\n\n`, `\n`, `.`, `。`, `!`, `？`, `;`) and breaks there. Supports both English and Chinese punctuation.
- **Parameters**: `RAG_CHUNK_SIZE=512` and `RAG_CHUNK_OVERLAP=50` are configurable via Settings.

### 7. Per-user isolation via metadata filtering (not per-user collections)

- **Decision**: All users share a single ChromaDB collection (`knowledge_base`). User isolation is enforced by `user_id` metadata on each chunk and `where={"user_id": str(user_id)}` filters on queries.
- **Alternatives considered**:
  | Approach | Pros | Cons |
  |----------|------|------|
  | Metadata filtering (chosen) | Simple, single collection | All data in one index |
  | Per-user collection | Hard isolation | Collection proliferation, management overhead |
  | Per-user ChromaDB instance | Complete isolation | File system complexity, resource waste |
- **Rationale**: Metadata filtering is simpler and sufficient for the expected user count (single user or small team). ChromaDB's `where` filter is applied before HNSW search, so performance is acceptable. Per-user collections can be migrated to if needed.

### 8. Graceful degradation when RAG is unavailable

- **Decision**: If ChromaDB or LlamaIndex dependencies are missing, or if initialization fails, the RAG engine sets `is_available=False` and `init_error` with the reason. All operations return empty/false results instead of raising exceptions. The API returns a `message` field explaining unavailability.
- **Rationale**: RAG is an enhancement, not a core requirement. The application should start and function without it. This allows deployment without heavy ML dependencies for environments that don't need RAG.

### 9. File upload: text extraction approach

- **Decision**: Support `.txt`, `.md`, `.pdf` files up to 10MB. PDF text extraction via `pypdf`. No OCR.
- **Rationale**: Covers the most common document formats for study materials. PDF text extraction via `pypdf` is lightweight and handles most text-based PDFs. OCR would require heavy dependencies (Tesseract/Poppler) and is deferred to v2.

## API Design

```
/api/v1/knowledge/

  POST   /documents          Upload text document
         Request:  { title: string, content: string, tags?: string[] }
         Response: DocumentResponse (201)

  POST   /documents/file     Upload file (PDF/TXT/MD)
         Request:  multipart/form-data { file, title? }
         Response: FileUploadResponse { document, message } (201)

  GET    /documents          List user's documents
         Response: DocumentResponse[] (200)

  DELETE /documents/{doc_id} Delete document
         Response: { message } (200)

  POST   /query              Semantic search
         Request:  { query: string, top_k?: int (1-10, default 3) }
         Response: KnowledgeQueryResponse { query, results[], total, message? }

  GET    /stats              Knowledge base statistics
         Response: KnowledgeStats { total_documents, total_chunks, total_words }
```

All endpoints require JWT authentication. Documents are scoped to the authenticated user.

## Risks / Trade-offs

- **[Risk] pgvector requires PostgreSQL** → **Mitigation**: SQLite users get RAG disabled automatically with a clear message. They can opt-in to ChromaDB with `VECTOR_STORE=chromadb`, or migrate to PostgreSQL. Document metadata CRUD still works on SQLite.
- **[Risk] Embedding API costs** → **Mitigation**: Using corporate LLM gateway (`local_qwen3_embed`) has no per-token cost. For external providers, use `text-embedding-3-small` (~$0.02/1M tokens). Chunk size 512 limits token count. Embeddings are computed once at upload time and stored in the vector store.
- **[Risk] Embedding model change invalidates existing vectors** → **Mitigation**: If the embedding model changes (e.g. from `local_qwen3_embed` to `text-embedding-3-small`), existing vectors become incompatible. Must re-index all documents. The admin UI should warn about this. Consider storing `embedding_model` in chunk metadata for detection.
- **[Risk] Chunking quality for diverse content** → **Mitigation**: Sentence-boundary-aware chunking works well for prose and technical writing. Configurable chunk size/overlap for tuning. Markdown headers and code blocks may not chunk optimally — can improve with format-aware chunking in v2.
- **[Trade-off] No re-ranking** → Cosine similarity alone may return less-relevant chunks for ambiguous queries. Re-ranking (cross-encoder) can be added later as a post-retrieval step.
- **[Trade-off] user_id stored as string in ChromaDB metadata** → ChromaDB metadata values must be strings. The integer `user_id` is cast to `str()` for storage and filtering. This is consistent but requires string comparison.
- **[Trade-off] No hybrid search** → Pure vector search may miss exact keyword matches. Hybrid search (BM25 + vector) would improve recall for technical terms. Can add via Qdrant or pgvector in v2.

## Open Questions

1. **Tag aggregation**: Frontend expects `stats.tags` but the backend `KnowledgeStats` schema doesn't include tags. Should we add tag aggregation to the stats endpoint? → **Recommendation**: Yes, aggregate distinct tags across user's documents in v2.
2. **Document update**: There is no update endpoint — users must delete and re-upload. Should we add `PATCH /documents/{doc_id}`? → **Recommendation**: Defer; delete+re-upload is sufficient for v1.
3. **Chunk overlap edge case**: The `_chunk_text()` method has a subtle edge case where `start` can fail to advance under certain conditions (line 381). Should be reviewed. → **Recommendation**: Add unit tests for edge cases.
4. **Default top_k mismatch**: Frontend store defaults to `top_k=5`, backend schema defaults to `3`. → **Recommendation**: Align to 5 in both places.
5. ~~**Which vector store to use?**~~ → **Resolved**: pgvector (PostgreSQL) as primary backend. ChromaDB available as optional fallback. SQLite disables RAG automatically. See Decision 2 for full comparison.
6. **Embedding model stored in metadata?**: Should each chunk's metadata include the embedding model name used to generate it? This would enable detection of stale vectors after a model change. → **Recommendation**: Yes, add `embedding_model` to chunk metadata in v2.
