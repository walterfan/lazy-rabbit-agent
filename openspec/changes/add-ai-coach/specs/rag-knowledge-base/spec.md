## ADDED Requirements

### Requirement: Knowledge base supports document upload via text

The system SHALL allow authenticated users to upload documents by providing a title and text content. Each document is scoped to the uploading user. The document SHALL be indexed in the vector store for subsequent RAG queries.

#### Scenario: User uploads a text document successfully

- **WHEN** an authenticated user POSTs to `/api/v1/knowledge/documents` with a valid `title` and `content`
- **THEN** the system stores the document in the database with the user's ID
- **AND** the document content is chunked, embedded, and indexed in ChromaDB
- **AND** the system returns HTTP 201 with the document ID, title, and creation timestamp

#### Scenario: Upload rejected without authentication

- **WHEN** a client POSTs to `/api/v1/knowledge/documents` without a valid JWT
- **THEN** the system responds with 401 Unauthorized

#### Scenario: Upload rejected with missing title

- **WHEN** an authenticated user POSTs with an empty or missing `title`
- **THEN** the system responds with 422 Unprocessable Entity

### Requirement: Knowledge base supports file upload (PDF/TXT/MD)

The system SHALL allow authenticated users to upload files (PDF, TXT, Markdown). The system extracts text content from the file, stores the document metadata, and indexes the content for RAG.

#### Scenario: User uploads a PDF file

- **WHEN** an authenticated user POSTs a PDF file to `/api/v1/knowledge/documents/file`
- **THEN** the system extracts text from the PDF
- **AND** stores the document with extracted content in the database
- **AND** indexes the content in the vector store
- **AND** returns HTTP 201 with the document metadata

#### Scenario: Unsupported file type rejected

- **WHEN** an authenticated user uploads a file with an unsupported extension (e.g., `.exe`, `.zip`)
- **THEN** the system responds with 400 Bad Request indicating supported file types

### Requirement: Knowledge base supports document listing

The system SHALL allow authenticated users to list their own documents. The list is scoped to the requesting user.

#### Scenario: User lists their documents

- **WHEN** an authenticated user GETs `/api/v1/knowledge/documents`
- **THEN** the system returns a list of documents belonging to that user
- **AND** each document includes id, title, tags, source, word_count, and created_at

#### Scenario: User sees only their own documents

- **WHEN** user A lists documents
- **THEN** documents uploaded by user B are NOT included in the response

### Requirement: Knowledge base supports document deletion

The system SHALL allow authenticated users to delete their own documents. Deletion removes both the database record and the vector store entries.

#### Scenario: User deletes a document

- **WHEN** an authenticated user DELETEs `/api/v1/knowledge/documents/{doc_id}`
- **AND** the document belongs to that user
- **THEN** the document is removed from the database
- **AND** the corresponding vectors are removed from ChromaDB
- **AND** the system returns HTTP 200

#### Scenario: User cannot delete another user's document

- **WHEN** user A attempts to delete a document belonging to user B
- **THEN** the system responds with 404 Not Found

### Requirement: Knowledge base supports semantic query (RAG)

The system SHALL provide a semantic search endpoint that retrieves relevant document chunks based on a natural language query. Results are scoped to the requesting user's documents.

#### Scenario: User queries the knowledge base

- **WHEN** an authenticated user POSTs to `/api/v1/knowledge/query` with a `query` string
- **THEN** the system performs vector similarity search against the user's indexed documents
- **AND** returns the top-k most relevant text chunks with source document titles and similarity scores

#### Scenario: Query with no matching documents

- **WHEN** a user queries the knowledge base but has no indexed documents
- **THEN** the system returns an empty results list (not an error)

#### Scenario: Query respects top_k parameter

- **WHEN** a user queries with `top_k=5`
- **THEN** the system returns at most 5 results

### Requirement: Knowledge base provides statistics

The system SHALL provide an endpoint to retrieve knowledge base statistics for the authenticated user.

#### Scenario: User retrieves knowledge base stats

- **WHEN** an authenticated user GETs `/api/v1/knowledge/stats`
- **THEN** the system returns document count, total word count, and index status
