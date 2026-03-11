"""RAG (Retrieval-Augmented Generation) engine service.

Supports pluggable vector store backends:
- pgvector  : PostgreSQL + pgvector extension (production)
- chromadb  : ChromaDB embedded (development)
- disabled  : RAG off (SQLite or explicit opt-out)
"""
