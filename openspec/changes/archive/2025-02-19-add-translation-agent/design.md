# Design: Translation Agent

## Context

- **Current state**: The app has a Personal Secretary agent and an article pipeline (`article_processor`) that fetches URLs (HTML/PDF), extracts content (trafilatura for HTML, pypdf for PDF), and produces bilingual content + summary + mindmap for learning. Auth is JWT; API lives under `/api/v1/`.
- **Constraint**: Reuse existing fetch and PDF extraction where possible; no new external translation APIs required (LLM does translation).
- **Stakeholders**: Users who need EN→ZH translation with explanation and summary; frontend for input (URL / file upload) and display of outputs.

## Goals / Non-Goals

**Goals:**

- Accept input as: (1) URL (fetch then extract), (2) PDF (URL or file upload), (3) text/markdown (e.g. `.txt`, `.md`) via file upload.
- Produce a structured response: **translated markdown** (EN→ZH), **explanation** (e.g. key terms, context), and **summary** (Chinese). Support two **output modes**: **Chinese only** (translated content only) and **bilingual** (each paragraph or segment: original English followed by Chinese translation). The combined result SHALL be available as a **single markdown document** that the user can **download** (e.g. `.md` file), and the frontend SHALL **render the same markdown as HTML** on the translation page.
- Expose a single translation API (e.g. POST with URL or multipart file) supporting both non-streaming (JSON) and **real-time streaming** (e.g. SSE) so the user sees translation output as it is generated.
- Reuse backend fetch/PDF logic from the article pipeline; add a thin translation service that orchestrates fetch → extract → LLM translate/explain/summarize (with streaming when requested).

**Non-Goals:**

- Translation of languages other than English→Chinese in this change.
- Persistence of translation results (no DB schema change unless we add “translation history” later).
- Integration into the Secretary chat as a tool (separate change).

## Decisions

### 1. API shape: dedicated translation endpoint (non-streaming and streaming)

- **Decision**: Translation API supports two modes: (1) **Non-streaming**: `POST /api/v1/translation` with JSON body `{ "url": "..." }` or multipart `file`; response is JSON with `translated_markdown`, `explanation`, `summary`. (2) **Streaming**: `POST /api/v1/translation/stream` (or query param `?stream=true` on the same route) with same input; response is Server-Sent Events (SSE) or chunked stream delivering translation tokens (and optionally explanation/summary) as they are generated.
- **Rationale**: Real-time streaming is required so users see progress; non-streaming remains useful for small content or API consumers. Reuse the same input contract (URL or file) for both modes.
- **Alternatives**: (A) Streaming only — rejected to keep a simple JSON option. (B) Single endpoint with `Accept: text/event-stream` to trigger streaming — acceptable alternative to a separate path.

### 2. Input handling: URL vs file upload

- **URL**: Reuse `fetch_article` and content-type handling from `article_processor` (HTML vs PDF). Reuse `extract_to_markdown` (HTML) and `extract_from_pdf` (PDF) to get plain text/markdown for the LLM.
- **File upload**: Accept multipart `file` with allowed types: `application/pdf`, `text/plain`, `text/markdown`. Max file size and max source length SHALL be **configurable** (e.g. via environment variables or app config); suggested defaults: 10 MB file size, 12K characters source length sent to LLM. Read bytes: PDF → `extract_from_pdf`; txt/md → decode UTF-8 and use as-is (optional validation).
- **Decision**: Use FastAPI `UploadFile` for file; validate content type and size against configurable limits; reject unsupported types with 400.

### 3. Translation pipeline (backend)

- **Decision**: New module under `app/services/translation/` (or `app/services/translation_agent/`): (1) **Normalize input** → single “source text” string (from URL fetch+extract or from uploaded file). (2) **Single LLM flow** (or a few prompts): translate to Chinese markdown, then generate explanation and summary from the translated content (or one structured prompt with three outputs). (3) Return `{ translated_markdown, explanation, summary }`.
- **Rationale**: Reusing article fetch/extract keeps URL/PDF handling consistent; one service keeps translation logic in one place.
- **Alternatives**: Reuse only `fetch_article` + `extract_*` and put “translate + explain + summarize” in a new tool under the Secretary — rejected for this change in favor of a dedicated API and service.

### 4. Output format (non-streaming and streaming)

- **Decision**: **Non-streaming**: JSON response with `translated_markdown`, `explanation`, `summary` (all required). **Streaming**: SSE (or equivalent) with event types such as `token` (translation chunk), `explanation` (when explanation is ready), `summary` (when summary is ready), and `done`. Translation tokens stream first; explanation and summary may stream after translation or be sent as single events at the end.
- **Rationale**: Non-streaming keeps integration simple; streaming gives real-time feedback. Frontend can render tokens incrementally and then show explanation and summary.

### 4b. Bilingual output mode

- **Decision**: The API SHALL accept an **output mode** parameter (e.g. `output_mode: "chinese_only"` | `"bilingual"`). **Chinese only**: `translated_markdown` contains only the Chinese translation. **Bilingual**: `translated_markdown` contains each source segment (English) followed by its Chinese translation (e.g. paragraph-by-paragraph or sentence-by-sentence), so the user can read both side by side. Explanation and summary remain in Chinese (or follow the same mode if we extend later). Default MAY be `chinese_only` for backward compatibility.
- **Rationale**: Bilingual mode supports users who want to compare original and translation; Chinese-only is simpler for consumption.

### 5. Downloadable markdown and HTML rendering

- **Decision**: The full result (translated content + explanation + summary) is represented as a **single markdown document** with a defined structure (e.g. `# 翻译\n\n<translated_markdown>\n\n# 解释\n\n<explanation>\n\n# 总结\n\n<summary>`). (1) **Download**: The API MAY provide a dedicated endpoint (e.g. `GET /api/v1/translation/{id}/download` or the JSON response includes a `markdown_document` field), or the frontend SHALL build the combined markdown from `translated_markdown`, `explanation`, and `summary` and offer a “Download as .md” action that triggers a client-side download of that document. (2) **HTML rendering**: The frontend SHALL render the same markdown (from JSON or from the built document) as HTML on the translation result page, using a markdown-to-HTML library (e.g. marked, markdown-it) so the user sees formatted output. Streaming view SHALL update the rendered HTML as tokens arrive.
- **Rationale**: One markdown file is portable and editable; HTML rendering gives a good reading experience. Building the .md on the frontend from the three fields avoids an extra backend endpoint if the API already returns the three parts.

### 6. Auth and errors

- **Decision**: Same auth as rest of API: require valid JWT (e.g. `Depends(get_current_active_user)`). On fetch/extract failure (e.g. URL timeout, PDF no text), return 422 or 400 with a clear message rather than 500.
- **Rationale**: Consistency with existing API; better UX for invalid URL or unsupported PDF.

### 7. Configurable size and length limits

- **Decision**: **Max file size** (for uploads) and **max source text length** (characters sent to the LLM, after extraction) SHALL be **configurable** (e.g. `TRANSLATION_MAX_FILE_SIZE_BYTES`, `TRANSLATION_MAX_SOURCE_LENGTH` in env or in app settings). Suggested defaults: 10 MB (10_485_760 bytes) for file size, 12_000 characters for source length. The system SHALL enforce these limits at runtime using the configured values so that operators can tune them per environment without code changes.
- **Rationale**: Different deployments may need different limits; configurable values avoid hardcoding and allow safer defaults in production.

## Risks / Trade-offs

- **[Risk] Large PDFs or HTML** → Mitigation: Enforce configurable max file size and max source length; truncate or reject with message if over limit before calling LLM.
- **[Risk] LLM token limit** → Mitigation: Truncate source text to the configured max source length and mention “content truncated” in the output if truncated.
- **[Risk] File upload abuse** → Mitigation: Validate content type and size; do not execute or interpret file content as code; store in temp only for processing then discard.
- **[Trade-off] No persistence** → Translation results are not stored; user must copy or re-run. Acceptable for v1; “save to learning records” can be a later feature.

## Migration Plan

- **Deploy**: Add new route and service behind feature; no DB migration. Config reuses existing LLM settings.
- **Rollback**: Remove or disable translation route and service; no data to migrate.

## Open Questions

- Frontend: new “Translation” view vs. integration into an existing page (to be decided in implementation).
