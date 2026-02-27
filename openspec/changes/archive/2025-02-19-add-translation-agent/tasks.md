# Tasks: add-translation-agent

## 1. Config and limits

- [x] 1.1 Add TRANSLATION_MAX_FILE_SIZE_BYTES and TRANSLATION_MAX_SOURCE_LENGTH to backend config (defaults 10 MB, 12_000)
- [x] 1.2 Add translation config to .env.sample and document in README or config docs

## 2. Translation service (backend)

- [x] 2.1 Create app/services/translation/ module with input normalization (URL fetch+extract or file bytes → source text)
- [x] 2.2 Implement translate pipeline: source text → LLM → translated_markdown, explanation, summary (chinese_only and bilingual modes)
- [x] 2.3 Enforce configurable max source length (truncate + indicate truncated in response)
- [x] 2.4 Add streaming translation (async generator yielding tokens, then explanation/summary)

## 3. Translation API (backend)

- [x] 3.1 Add POST /api/v1/translation: accept JSON { url } or multipart file; validate URL xor file; auth required
- [x] 3.2 Validate file type (PDF, text/plain, text/markdown) and size against TRANSLATION_MAX_FILE_SIZE_BYTES; return 400 on violation
- [x] 3.3 Return JSON response with translated_markdown, explanation, summary; support output_mode (chinese_only | bilingual)
- [x] 3.4 Add POST /api/v1/translation/stream: same input, SSE response with token/explanation/summary/done events; auth required
- [x] 3.5 Register translation router in api/v1/api.py and mount under /translation

## 4. Error handling (backend)

- [x] 4.1 Return 422/400 with clear message on URL fetch failure or extraction failure (no 500 for invalid input)
- [x] 4.2 Return 400 when neither URL nor file provided or both provided

## 5. Frontend – Translation view and API client

- [x] 5.1 Add translation API service (post translation with URL or file; post translation/stream for SSE)
- [x] 5.2 Add Translation view: input for URL and file upload, output_mode selector (chinese_only / bilingual)
- [x] 5.3 Render result as HTML (markdown-to-HTML) and offer "Download as .md" (build combined doc from translated_markdown, explanation, summary)
- [x] 5.4 Support streaming: consume SSE and update rendered HTML progressively; then show explanation and summary
- [x] 5.5 Add route and nav entry for Translation page

## 6. Tests and docs

- [x] 6.1 Backend: unit tests for translation service (normalize input, truncation, output modes)
- [x] 6.2 Backend: API tests for POST /translation (URL, file, validation, auth) and POST /translation/stream
- [x] 6.3 Update docs (e.g. PROJECT-KNOWLEDGE-PACK or runbook) with translation endpoint and config vars
