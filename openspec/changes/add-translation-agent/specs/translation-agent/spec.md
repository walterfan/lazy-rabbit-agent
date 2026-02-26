# translation-agent Specification (Delta)

## ADDED Requirements

### Requirement: Translation endpoint accepts URL or file input

The system SHALL provide a single translation endpoint that accepts either a URL (to fetch) or an uploaded file (PDF, plain text, or markdown). The client MUST supply exactly one of URL or file; supplying both or neither SHALL result in a 400 Bad Request.

#### Scenario: Client submits URL

- **WHEN** the client POSTs a JSON body with a valid `url` field and no file
- **THEN** the system fetches the resource at that URL, determines content type (HTML or PDF), extracts main text or PDF text, and uses it as the source for translation

#### Scenario: Client submits file upload

- **WHEN** the client POSTs multipart form data with a `file` part (PDF, `.txt`, or `.md`)
- **THEN** the system accepts the file subject to size and type limits, extracts text (PDF via extraction, txt/md via UTF-8 decode), and uses it as the source for translation

#### Scenario: Client submits neither URL nor file

- **WHEN** the client POSTs without a valid URL and without a file
- **THEN** the system responds with 400 Bad Request and a clear validation message

#### Scenario: Unsupported file type rejected

- **WHEN** the client uploads a file with a content type or extension not in the allowed set (e.g. PDF, text/plain, text/markdown)
- **THEN** the system responds with 400 Bad Request and indicates allowed types

### Requirement: Translation produces markdown, explanation, and summary

The system SHALL translate the extracted English source content into Chinese and SHALL return a structured response containing: (1) translated content in markdown form (`translated_markdown`), (2) an explanation of key terms or context (`explanation`), and (3) a concise summary (`summary`). All three fields MUST be present in the response.

#### Scenario: Successful translation from URL

- **WHEN** the source is successfully fetched and extracted from a URL
- **THEN** the system returns HTTP 200 with a JSON body containing `translated_markdown`, `explanation`, and `summary`, each a non-empty string

#### Scenario: Successful translation from uploaded file

- **WHEN** the source is successfully read from an uploaded PDF or text/markdown file
- **THEN** the system returns HTTP 200 with a JSON body containing `translated_markdown`, `explanation`, and `summary`, each a non-empty string

#### Scenario: Response structure

- **WHEN** the client receives a successful translation response
- **THEN** the response body SHALL be valid JSON with required string fields `translated_markdown`, `explanation`, and `summary`

### Requirement: Translation supports bilingual output mode

The system SHALL support a **bilingual** output mode in addition to Chinese-only. When bilingual mode is requested, the translated content SHALL present each source segment (e.g. paragraph or sentence) in English followed by its Chinese translation, so the user can read original and translation together. The client SHALL be able to select the output mode (e.g. via a request parameter).

#### Scenario: Client requests Chinese-only output

- **WHEN** the client requests translation with output mode set to Chinese-only (or omits the parameter when default is Chinese-only)
- **THEN** the system returns `translated_markdown` containing only the Chinese translation, with no interleaved English source text

#### Scenario: Client requests bilingual output

- **WHEN** the client requests translation with output mode set to bilingual
- **THEN** the system returns `translated_markdown` in which each segment shows the original English followed by the Chinese translation (e.g. English paragraph, then Chinese paragraph, or a consistent inline pattern such as “EN: … / ZH: …”), so the full content is available in both languages in one document

#### Scenario: Bilingual content in downloadable markdown and HTML

- **WHEN** the user has requested bilingual mode and downloads or views the result
- **THEN** the downloadable markdown and the HTML-rendered page SHALL both contain the bilingual form (English + Chinese per segment)

### Requirement: Translation endpoint requires authentication

The system SHALL require a valid JWT for the translation endpoint. Requests without a valid token or with an expired/invalid token SHALL receive 401 Unauthorized.

#### Scenario: Unauthenticated request rejected

- **WHEN** a request to the translation endpoint is made without an Authorization header or with an invalid token
- **THEN** the system responds with 401 Unauthorized

#### Scenario: Authenticated request accepted

- **WHEN** a request includes a valid JWT in the Authorization header
- **THEN** the system processes the request according to input and returns translation or an appropriate error (4xx/5xx)

### Requirement: Fetch or extraction failures return clear errors

The system SHALL return a 4xx response with a clear, user-facing message when the source cannot be obtained or extracted (e.g. URL timeout, HTTP error, PDF with no extractable text, unsupported page). The system MUST NOT return 500 for invalid or unsupported input when the failure is due to client-provided URL or file.

#### Scenario: URL fetch failure

- **WHEN** the URL cannot be fetched (timeout, 4xx/5xx, or unreachable)
- **THEN** the system responds with 422 or 400 and a message indicating the fetch failed (e.g. timeout or HTTP status)

#### Scenario: No content extracted from page or PDF

- **WHEN** the fetched page or uploaded PDF yields no extractable text (e.g. JavaScript-only page, scanned PDF)
- **THEN** the system responds with 422 or 400 and a message suggesting the content could not be extracted

### Requirement: Input size and length limits are enforced and configurable

The system SHALL enforce a maximum file size for uploads and a maximum source text length before sending to the LLM. These limits SHALL be **configurable** (e.g. via environment variables or application config). Suggested defaults: 10 MB for file size, 12,000 characters for source length. When the source exceeds the configured length, the system SHALL truncate and SHALL indicate in the response or in the output that content was truncated when applicable.

#### Scenario: File over size limit rejected

- **WHEN** the uploaded file size exceeds the configured maximum (default e.g. 10 MB)
- **THEN** the system responds with 400 Bad Request and a message indicating the file is too large

#### Scenario: Source text truncated for LLM

- **WHEN** the extracted source text exceeds the configured maximum length for the LLM (default e.g. 12K characters)
- **THEN** the system truncates the source to that limit and proceeds with translation; the response MAY indicate that the source was truncated

#### Scenario: Limits are configurable

- **WHEN** the operator sets configuration for max file size and/or max source length (e.g. via environment variables)
- **THEN** the system SHALL use those values when validating uploads and when truncating source text, so that limits can be tuned per environment without code changes

### Requirement: Translation supports real-time streaming

The system SHALL provide a streaming mode for translation so that the client receives translation output (and optionally explanation and summary) as it is generated, rather than waiting for the full response. The streaming response MUST use a standard mechanism such as Server-Sent Events (SSE) or HTTP chunked transfer with a well-defined event or chunk format.

#### Scenario: Client requests streaming translation

- **WHEN** the client requests translation in streaming mode (e.g. via a dedicated streaming endpoint or a query parameter) with valid URL or file input
- **THEN** the system responds with a streaming response (e.g. `Content-Type: text/event-stream`) and delivers translation content incrementally as the LLM produces it

#### Scenario: Streaming delivers translation tokens first

- **WHEN** the client is consuming a streaming translation response
- **THEN** the client receives translation output (e.g. as token or chunk events) in order, so that the translated markdown can be rendered progressively in the UI

#### Scenario: Explanation and summary in streaming response

- **WHEN** the streaming translation completes the translated content phase
- **THEN** the system SHALL deliver explanation and summary (either as subsequent streamed segments or as discrete events), so that the full structured result (translated_markdown, explanation, summary) is eventually available to the client

#### Scenario: Streaming endpoint requires authentication

- **WHEN** the client requests streaming translation without a valid JWT
- **THEN** the system responds with 401 Unauthorized before opening the stream

### Requirement: Result is available as downloadable markdown and rendered as HTML

The system SHALL make the full translation result (translated content, explanation, and summary) available as a **single markdown document** that the user can download as a `.md` file. The frontend SHALL render the same content as **HTML** on the translation result page so the user can read it in formatted form.

#### Scenario: User can download result as markdown file

- **WHEN** the user has received a successful translation response (non-streaming or after streaming completes)
- **THEN** the user SHALL be able to trigger a download of a markdown file that contains the translated content, explanation, and summary in a structured form (e.g. with section headings such as 翻译, 解释, 总结), so that the result is portable and editable offline

#### Scenario: Frontend renders result as HTML

- **WHEN** the user views the translation result on the frontend
- **THEN** the frontend SHALL render the markdown (built from `translated_markdown`, `explanation`, and `summary`) as HTML using a markdown-to-HTML renderer, so that headings, lists, and other markdown formatting are displayed correctly on the page

#### Scenario: Streaming view updates rendered HTML progressively

- **WHEN** the user is viewing a streaming translation
- **THEN** the frontend SHALL update the rendered HTML as translation tokens (and later explanation and summary) arrive, so that the user sees the formatted result grow in real time
