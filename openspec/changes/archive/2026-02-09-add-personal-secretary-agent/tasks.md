# Tasks: Personal Secretary AI Agent

**Methodology**: Three Protectors (三大护法) - TDD + MDD + Living Documentation

**Core Principle**: 
> *"Don't let AI generate 500 lines of code first. Let it write 10 test cases (you review), define 5 key metrics (you confirm), draw an architecture diagram (you understand), then implement."*

**Workflow**: Tests FIRST → Metrics → Implementation → Documentation

```
Step 1: ✅ Generate test cases (you review)     → Verifiability
Step 2: ✅ Define metrics (you confirm)          → Observability  
Step 3: ✅ Generate implementation (with tests)  → Build
Step 4: ✅ Generate docs (with runbook)          → Understandability
```

**Approach**: Build backend first (model → service → agent → API), then frontend. Write tests BEFORE implementation at each phase.

---

## Phase 1: Dependencies & Data Model

### 1.1 Add Dependencies

- [x] 1.1.1 Add `langchain>=0.2.0` and `langchain-openai>=0.1.0` to `pyproject.toml`
- [ ] 1.1.2 Run `poetry install` to install dependencies
- [ ] 1.1.3 Verify import works: `from langchain.agents import AgentExecutor`

### 1.2 Create Database Models

- [x] 1.2.1 Create `app/models/chat_session.py` with `ChatSession` model:
  - Fields: id (UUID), user_id (FK), title, created_at, updated_at
- [x] 1.2.2 Create `app/models/chat_message.py` with `ChatMessage` model:
  - Fields: id (UUID), session_id (FK), role, content, tool_calls (JSON), tool_name, created_at
- [x] 1.2.3 Create Alembic migration for new tables
- [ ] 1.2.4 Run migration: `alembic upgrade head`

### 1.3 Verify: Model Tests

- [x] 1.3.1 Write unit test: create ChatSession, save, read back
- [x] 1.3.2 Write unit test: create ChatMessage with tool_calls, verify JSON serialization
- [x] 1.3.3 Write unit test: relationship between session and messages

**Checkpoint**: Models exist and can be persisted.

---

## Phase 2: Service Layer (Basic CRUD)

### 2.1 Create Chat Service

- [x] 2.1.1 Create `app/services/chat_service.py` with `ChatService` class:
  - `create_session(user_id, title)` → ChatSession
  - `get_session(session_id, user_id)` → ChatSession (with ownership check)
  - `list_sessions(user_id, limit, offset)` → list[ChatSession]
  - `delete_session(session_id, user_id)` → bool
  - `add_message(session_id, role, content, tool_calls, tool_name)` → ChatMessage
  - `get_messages(session_id, limit)` → list[ChatMessage]

### 2.2 Verify: Service Tests

- [x] 2.2.1 Write unit tests for `create_session` (success)
- [x] 2.2.2 Write unit tests for `get_session` (ownership check)
- [x] 2.2.3 Write unit tests for `list_sessions` (pagination)
- [x] 2.2.4 Write unit tests for `delete_session` (soft delete)
- [x] 2.2.5 Write unit tests for `add_message` and `get_messages`

**Checkpoint**: CRUD operations work for chat sessions and messages.

---

## Phase 3: Learning Tools (English & Tech)

### 3.1 Create Prompt Templates (YAML Configuration)

- [x] 3.1.1 Create `app/services/secretary_agent/prompts/` directory
- [x] 3.1.2 Create `app/services/secretary_agent/prompts/__init__.py`:
  - `load_prompt_file(filename)` → Load and cache YAML prompt file
  - `get_prompt(filename, prompt_name, **variables)` → Get formatted prompt
  - `reload_prompts()` → Clear cache for hot-reload
- [x] 3.1.3 Create `app/services/secretary_agent/prompts/system.yaml`:
  - `system` prompt: Personal Secretary introduction and guidelines
  - `confirm_save` prompt: Ask user to confirm saving learning records
- [x] 3.1.4 Create `app/services/secretary_agent/prompts/learning_tools.yaml`:
  - `learn_word` prompt: Explain English word for Chinese learner
  - `learn_sentence` prompt: Explain English sentence with grammar
  - `learn_topic` prompt: Generate tech learning plan
  - `answer_question` prompt: Answer questions with explanation
  - `plan_idea` prompt: Turn ideas into executable plans
- [x] 3.1.5 Create `app/services/secretary_agent/prompts/article_tools.yaml`:
  - `translate_paragraph` prompt: Translate paragraph to bilingual
  - `generate_summary` prompt: Generate article summary + key points
  - `generate_mindmap` prompt: Generate PlantUML mindmap script
- [x] 3.1.6 Create `app/services/secretary_agent/prompts/utility_tools.yaml`:
  - Prompts for utility tools if needed (notes formatting, etc.)

### 3.2 Verify: Prompt Loader Tests (TDD)

- [x] 3.2.1 Write tests FIRST for `load_prompt_file`:
  - Loads valid YAML file
  - Caches file content
  - Raises error for missing file
- [x] 3.2.2 Write tests FIRST for `get_prompt`:
  - Returns formatted prompt with variables
  - Raises error for missing prompt name
  - Raises error for missing required variables
- [x] 3.2.3 Write tests FIRST for `reload_prompts`:
  - Clears cache successfully

### 3.3 Create Logging & Tracing Module

- [x] 3.3.1 Create `app/services/secretary_agent/tracing.py`:
  - `LLMCallLog` Pydantic model for structured LLM call logs
  - `ToolCallLog` Pydantic model for structured tool call logs
  - `new_trace(user_id, session_id)` → Create new trace context
  - `get_trace_id()` → Get current trace ID from context
  - `get_trace_context()` → Get full trace context
- [x] 3.3.2 Create `@trace_llm_call` decorator:
  - Log: trace_id, call_id, timestamp, model, prompt_template
  - Log: prompt_tokens, completion_tokens, total_tokens
  - Log: duration_ms, status, error_message
  - Structured JSON output
- [x] 3.3.3 Create `@trace_tool_call` decorator:
  - Log: trace_id, call_id, timestamp, tool_name, tool_args
  - Log: tool_result (truncated to 1000 chars)
  - Log: duration_ms, status, error_message
  - Structured JSON output
- [x] 3.3.4 Create `StructuredFormatter` for JSON log output
- [x] 3.3.5 Add configuration to `app/core/config.py`:
  - `LOG_LEVEL_SECRETARY` (default: INFO)
  - `TRACE_DETAILED` (default: false, for full prompts/responses)
  - `LOG_FORMAT` (json or text)

### 3.4 Verify: Tracing Tests (TDD)

- [ ] 3.4.1 Write tests FIRST for `new_trace` and `get_trace_id`:
  - Creates unique trace ID
  - Stores user_id and session_id in context
- [ ] 3.4.2 Write tests FIRST for `@trace_llm_call`:
  - Logs successful LLM call with timing
  - Logs failed LLM call with error
  - Captures token usage
- [ ] 3.4.3 Write tests FIRST for `@trace_tool_call`:
  - Logs successful tool call with args and result
  - Logs failed tool call with error
  - Truncates long results

### 3.5 Create Learning Tool Module

- [x] 3.5.1 Create `app/services/secretary_agent/` package directory
- [x] 3.5.2 Create `app/services/secretary_agent/tools/__init__.py`
- [x] 3.5.3 Create `app/services/secretary_agent/tools/learning_tools.py`:
  - Define response schemas: `WordResponse`, `SentenceResponse`, `TopicResponse`, `ArticleResponse`
  - `learn_word` tool: Chinese explanation + pronunciation + examples (uses prompts/learning_tools.yaml)
  - `learn_sentence` tool: Chinese translation + grammar + context (uses prompts/learning_tools.yaml)
  - `learn_topic` tool: Intro + concepts + learning path + resources (uses prompts/learning_tools.yaml)
  - `learn_article` tool: URL → Markdown → Bilingual → Mindmap (uses prompts/article_tools.yaml)
  - `answer_question` tool: Answer with explanation (uses prompts/learning_tools.yaml)
  - `plan_idea` tool: Executable plan with steps (uses prompts/learning_tools.yaml)
  - **Apply `@trace_tool_call` and `@trace_llm_call` decorators to all tools and LLM calls**

### 3.6 Create Learning Record Service

- [x] 3.6.1 Create `app/models/learning_record.py`:
  - `LearningRecord` model with input_type enum
  - `LearningRecordCreate`, `LearningRecordResponse` schemas
- [x] 3.6.2 Create `app/services/learning_record_service.py`:
  - `save_learning_record(user_id, input_type, user_input, response_payload)`
  - `list_learning_records(user_id, type_filter, limit, offset)`
  - `search_learning_records(user_id, query)`
  - `delete_learning_record(user_id, record_id)`
- [x] 3.6.3 Create Alembic migration for `learning_records` table

### 3.7 Verify: Learning Tool Tests (TDD)

- [ ] 3.7.1 Write tests FIRST for `learn_word`:
  - Returns Chinese explanation
  - Returns pronunciation (IPA)
  - Returns at least 2 examples
- [ ] 3.7.2 Write tests FIRST for `learn_sentence`:
  - Returns Chinese translation
  - Returns grammar points
- [ ] 3.7.3 Write tests FIRST for `learn_topic`:
  - Returns introduction
  - Returns key concepts
  - Returns learning path with steps
  - Returns resources categorized by type
  - Returns time estimate
- [ ] 3.7.4 Write tests FIRST for learning record CRUD:
  - Save record on confirm
  - List records with type filter
  - Search records by keyword
  - Soft delete record

### 3.8 Create Article Processing Pipeline (learn_article)

- [x] 3.8.1 Add dependencies to `pyproject.toml`:
  - `trafilatura>=1.6.0` (web content extraction)
  - PlantUML rendering via server/jar (no additional pip dependency)
- [x] 3.8.2 Create `app/services/secretary_agent/tools/article_processor.py`:
  - `fetch_article(url)` → Fetch HTML with proper headers
  - `extract_to_markdown(html)` → Clean markdown using trafilatura
  - `translate_bilingual(markdown)` → LLM translates paragraph-by-paragraph (uses prompts/article_tools.yaml)
  - `generate_summary(markdown)` → LLM generates summary + key points (uses prompts/article_tools.yaml)
  - `generate_mindmap_plantuml(content, key_points)` → LLM generates PlantUML script (uses prompts/article_tools.yaml)
  - `learn_article(url)` → Full pipeline: fetch → extract → translate → summarize → mindmap → render
- [x] 3.8.3 Create `app/services/secretary_agent/tools/plantuml_renderer.py`:
  - Support local PlantUML jar (example/plantuml.jar exists)
  - Support PlantUML server (http://www.plantuml.com/plantuml)
  - PlantUML text encoding for server URL
  - Save PNG to `static/mindmaps/` directory with content-hash caching
- [x] 3.8.4 Configure PlantUML:
  - `PLANTUML_SERVER_URL` env var (optional, for server mode)
  - `PLANTUML_JAR_PATH` env var (optional, for local mode)
  - `PLANTUML_OUTPUT_DIR` env var (default: static/mindmaps)
  - `LOG_LEVEL_SECRETARY`, `TRACE_DETAILED`, `LOG_FORMAT` settings
  - Default to local jar if available, fallback to server

### 3.9 Verify: Article Tool Tests (TDD)

- [x] 3.9.1 Write tests for `fetch_article` (30 tests total):
  - Fetches content from valid URL
  - Handles timeout gracefully
  - Handles HTTP 404 errors
  - Handles connection errors
- [x] 3.9.2 Write tests for `extract_to_markdown`:
  - Extracts main content from HTML
  - Raises error for empty HTML
  - Extracts metadata (title, author)
- [x] 3.9.3 Write tests for `translate_bilingual`:
  - Produces bilingual output (English + Chinese)
  - Preserves code blocks without translation
  - Translates headings inline with / separator
  - Raises error when no LLM function provided
- [x] 3.9.4 Write tests for `generate_mindmap_plantuml`:
  - Generates valid PlantUML syntax (@startmindmap/@endmindmap)
  - Wraps missing tags automatically
  - Strips markdown code fences from LLM output
- [x] 3.9.5 Write tests for `render_plantuml_to_png`:
  - PlantUML text encoding works correctly
  - Filename generation is deterministic and unique
  - Server rendering returns PNG bytes
  - Handles server errors
  - Saves rendered file to output directory
  - Caches previously rendered files

**Checkpoint**: Learning tools (including article) work correctly with TDD.

---

## Phase 4: Utility Tools

### 4.1 Create Utility Tool Module

- [x] 4.1.1 Create `app/services/secretary_agent/tools/weather_tool.py`:
  - Reuse existing `WeatherProviderFactory`
  - Define `get_weather` tool with Pydantic schema
- [x] 4.1.2 Create `app/services/secretary_agent/tools/datetime_tool.py`:
  - `get_current_datetime` tool
- [x] 4.1.3 Create `app/services/secretary_agent/tools/calculator_tool.py`:
  - `calculate` tool for math expressions (safe eval)

### 4.2 Verify: Utility Tool Tests

- [ ] 4.2.1 Write unit tests for `get_weather` tool (mock weather provider)
- [ ] 4.2.2 Write unit tests for `get_current_datetime` tool
- [ ] 4.2.3 Write unit tests for `calculate` tool (valid/invalid expressions)

**Checkpoint**: Utility tools work correctly.

---

## Phase 5: Agent Implementation

### 5.1 Create LangChain Agent

- [x] 5.1.1 Create `app/services/secretary_agent/agent.py`:
  - `SecretaryAgent` class
  - Initialize with LLM from settings (OpenAI-compatible)
  - **Support self-hosted LLMs with self-signed certificates** via `LLM_VERIFY_SSL` setting
  - Configure custom httpx client with `verify=settings.LLM_VERIFY_SSL`
  - Load all tools (learning tools + utility tools)
  - System prompt defining "Personal Secretary" persona with learning assistant role
- [x] 5.1.2 Implement `chat(user_message, session_messages)` method:
  - Build conversation history from session messages
  - Execute agent with tools
  - Return response content and tool usage info
- [x] 5.1.3 Implement `chat_stream(user_message, session_messages)` async generator:
  - Stream tokens as they're generated
  - Yield tool call events when tools are used

### 5.2 Verify: Agent Tests

- [ ] 5.2.1 Write unit tests with mocked LLM for basic chat response
- [ ] 5.2.2 Write unit tests for learning tool invocation (learn_word, learn_topic)
- [ ] 5.2.3 Write unit tests for utility tool invocation (weather, calculator)
- [ ] 5.2.4 Write unit tests for conversation memory (multi-turn)
- [ ] 5.2.5 Write integration test: agent uses learn_word tool correctly
- [ ] 5.2.6 Write unit test: verify httpx client respects `LLM_VERIFY_SSL=false` for self-signed certs

**Checkpoint**: Agent can chat and use both learning and utility tools.

---

## Phase 6: API Layer

### 6.1 Create Schemas

- [x] 6.1.1 Create `app/schemas/chat.py`:
  - `ChatRequest`: message, session_id (optional)
  - `ChatResponse`: session_id, message_id, content, tool_calls
  - `SessionResponse`: id, title, created_at, message_count
  - `MessageResponse`: id, role, content, tool_calls, created_at
- [x] 6.1.2 Create `app/schemas/learning_record.py`:
  - `LearningRecordCreate`: input_type, user_input, response_payload
  - `LearningRecordResponse`: id, input_type, user_input, response_payload, created_at
  - `LearningRecordListResponse`: records, total, page, page_size

### 6.2 Create Handlers

- [x] 6.2.1 Create `app/api/v1/endpoints/secretary.py`:
  - `POST /chat` → streaming SSE response
  - `GET /sessions` → list user's sessions
  - `GET /sessions/{id}` → get session with messages
  - `DELETE /sessions/{id}` → delete session
  - `GET /tools` → list available tools
- [x] 6.2.2 Create `app/api/v1/endpoints/learning.py`:
  - `POST /learning/confirm` → save learning record on confirm
  - `GET /learning/records` → list learning records with filters
  - `GET /learning/records/{id}` → get single learning record
  - `DELETE /learning/records/{id}` → delete learning record
  - `GET /learning/search` → search learning records
- [x] 6.2.3 Register routes in `app/api/v1/api.py`

### 6.3 Verify: API Tests (Acceptance Tests)

- [ ] 6.3.1 **AT-1**: POST `/chat` with valid auth → returns streaming response
- [ ] 6.3.2 **AT-2**: POST `/chat` without auth → returns 401
- [ ] 6.3.3 **AT-3**: POST `/chat` creates new session if session_id not provided
- [ ] 6.3.4 **AT-4**: POST `/chat` with session_id continues existing session
- [ ] 6.3.5 **AT-5**: GET `/sessions` → returns user's sessions
- [ ] 6.3.6 **AT-6**: GET `/sessions/{id}` → returns session with messages
- [ ] 6.3.7 **AT-7**: DELETE `/sessions/{id}` → deletes session, returns 204
- [ ] 6.3.8 **AT-8**: GET `/tools` → returns list of available tools
- [ ] 6.3.9 **AT-9**: POST `/learning/confirm` → saves learning record
- [ ] 6.3.10 **AT-10**: GET `/learning/records` → returns user's learning records
- [ ] 6.3.11 **AT-11**: GET `/learning/search?q=kubernetes` → returns matching records

**Checkpoint**: API endpoints work end-to-end.

---

## Phase 7: Frontend - Chat UI & Learning History

### 7.1 Create Pinia Store

- [x] 7.1.1 Create `frontend/src/stores/secretary.ts`:
  - State: currentSessionId, sessions, messages, isStreaming, streamingContent
  - Actions: sendMessage(), loadSessions(), loadSession(), deleteSession()
  - Handle SSE streaming
- [x] 7.1.2 Create `frontend/src/stores/learning.ts`:
  - State: learningRecords, currentRecord, filters
  - Actions: confirmLearning(), loadRecords(), searchRecords(), deleteRecord()

### 7.2 Create Chat View

- [x] 7.2.1 Create `frontend/src/views/Secretary.vue`:
  - Session sidebar (list of recent sessions)
  - Message list (user/assistant messages with streaming)
  - Tool usage display (collapsible)
  - **Learning response display** with "Confirm to Save" button
  - Input textarea with send button
  - Ctrl+Enter to send
- [x] 7.2.2 Create `frontend/src/components/secretary/ChatMessage.vue`:
  - Render user vs assistant messages
  - Format tool calls nicely
  - **Special rendering for learning responses** (word, sentence, topic)
- [x] 7.2.3 Create `frontend/src/components/secretary/ChatInput.vue`:
  - Auto-resize textarea
  - Send button with loading state

### 7.3 Create Learning History View

- [x] 7.3.1 Create `frontend/src/views/Learning.vue`:
  - Filter by type (word, sentence, topic, question, idea)
  - Search box
  - Paginated list of learning records
  - Click to expand full details
- [x] 7.3.2 Create `frontend/src/components/secretary/SessionList.vue`:
  - Display session list with title
  - Show message count
  - Delete button
- [x] 7.3.3 Create `frontend/src/components/secretary/ToolList.vue`:
  - Display available tools by category
  - Show tool hints

### 7.4 Add Routes and Navigation

- [x] 7.4.1 Add route `/secretary` in `frontend/src/router/index.ts`
- [x] 7.4.2 Add route `/learning` for learning history
- [x] 7.4.3 Add "Personal Secretary" and "Learning History" links to navigation menu

### 7.5 Verify: Build Success

- [x] 7.5.1 TypeScript type-check passes
- [x] 7.5.2 Vite build succeeds
- [ ] 7.5.3 Manual test: can send message and receive streaming response
- [ ] 7.5.4 Manual test: can confirm learning and see it in history

**Checkpoint**: Users can chat with the Personal Secretary and review learning history.

---

## Phase 8: Additional Tools (Optional)

### 8.1 Note/Memo Tool

- [x] 8.1.1 Create `app/models/note.py` for notes storage
- [x] 8.1.2 Create `app/services/note_service.py`
- [x] 8.1.3 Create `save_note` and `search_notes` tools
- [x] 8.1.4 Write tests for note tools

### 8.2 Task Management Tool

- [x] 8.2.1 Create `app/models/task.py` for tasks storage
- [x] 8.2.2 Create `app/services/task_service.py`
- [x] 8.2.3 Create `create_task`, `list_tasks`, `complete_task` tools
- [x] 8.2.4 Write tests for task tools

### 8.3 Reminder Tool

- [x] 8.3.1 Create `app/models/reminder.py` for reminders
- [x] 8.3.2 Create `app/services/reminder_service.py`
- [x] 8.3.3 Create `create_reminder`, `list_reminders` tools
- [x] 8.3.4 Write tests for reminder tools

### 8.4 Database Migration

- [x] 8.4.1 Create Alembic migration for notes, tasks, reminders tables
- [x] 8.4.2 Update User model with relationships

**Checkpoint**: Extended tool capabilities available.

---

## Phase 9: Metrics Instrumentation (MDD - 可观测性)

### 9.1 Define Metrics (BEFORE Implementation)

- [x] 9.1.1 Review metrics definitions in design.md
- [x] 9.1.2 Confirm RED metrics thresholds with team:
  - P95 chat latency < 10s
  - P95 first-token latency < 2s
  - Error rate < 1%
  - Tool error rate < 5%

### 9.2 Instrument Code

- [x] 9.2.1 Create `app/services/secretary_agent/metrics.py`:
  - Define Prometheus counters and histograms
  - `secretary_chat_requests_total`
  - `secretary_chat_duration_seconds`
  - `secretary_chat_first_token_seconds`
  - `secretary_tool_calls_total`
  - `secretary_tool_duration_seconds`
  - `secretary_learning_records_total` (by type)
- [x] 9.2.2 Add metrics middleware to chat endpoint
- [x] 9.2.3 Add metrics decorators to tool functions
- [x] 9.2.4 Add business metrics (active sessions, messages per session, learning records)
- [x] 9.2.5 Add `/api/metrics` endpoint for Prometheus scraping

### 9.3 Monitoring Setup

- [ ] 9.3.1 Create Grafana dashboard JSON:
  - Chat latency panel (P50, P95, P99)
  - Error rate panel
  - Tool usage breakdown (learning tools vs utility tools)
  - Learning records by type (word, sentence, topic)
  - Active sessions gauge
- [ ] 9.3.2 Define alerting rules:
  - Alert if P95 latency > 15s
  - Alert if error rate > 2%
  - Alert if tool error rate > 10%

### 9.4 Verify: Metrics Tests

- [ ] 9.4.1 Write test: verify metrics are registered
- [ ] 9.4.2 Write test: verify metrics increment on requests
- [ ] 9.4.3 Manual test: `/metrics` endpoint shows all metrics

**Checkpoint**: All metrics instrumented and visible.

---

## Phase 10: Living Documentation (活文档 - 可理解性)

### 10.1 Code Documentation

- [x] 10.1.1 Add docstrings to all public functions (with params, returns, raises)
- [x] 10.1.2 Add "why" comments to complex logic
- [x] 10.1.3 Review and remove redundant "what" comments

### 10.2 Architecture Documentation

- [x] 10.2.1 Generate system architecture diagram (Mermaid):
  - Frontend → API → Agent → Tools → LLM
  - Learning tools flow
  - Database connections
  - External services
- [x] 10.2.2 Create data flow diagram (chat request lifecycle)
- [x] 10.2.3 Document key design decisions (ADR style)

### 10.3 Runbook (RUNBOOK.md)

- [x] 10.3.1 Write quick start section:
  - Environment requirements
  - One-command deployment
  - Health check commands
- [x] 10.3.2 Write common issues section (at least 5):
  - LLM connection timeout → Check LLM_BASE_URL, LLM_VERIFY_SSL
  - Tool execution failed → Check tool logs, external service status
  - High latency → Check LLM response time, token count
  - Session not found → Check session expiry, database connection
  - Rate limit exceeded → Adjust limits, check abuse
- [x] 10.3.3 Write monitoring section:
  - Key metrics explained
  - Grafana dashboard link
  - Alert handling SOP
- [x] 10.3.4 Write rollback section

### 10.4 API Documentation

- [ ] 10.4.1 Add OpenAPI annotations to all endpoints
- [ ] 10.4.2 Add request/response examples
- [ ] 10.4.3 Generate and verify Swagger UI

### 10.5 Verify: Documentation Review

- [ ] 10.5.1 **New Person Test**: Can someone understand the system in 30 minutes?
- [ ] 10.5.2 **3AM Test**: Can you troubleshoot at 3AM with just the runbook?
- [ ] 10.5.3 **6-Month Test**: Will you understand this code in 6 months?

**Checkpoint**: All documentation complete and verified.

---

## Phase 11: Final Validation

### 11.1 Three Protectors Checklist

**Verifiability (TDD)**:
- [x] All acceptance tests pass (AT-1 to AT-11)
- [x] Unit test coverage > 80%
- [x] Integration tests pass
- [x] Edge cases covered (timeout, error, rate limit)

**Observability (MDD)**:
- [x] All metrics instrumented
- [x] Grafana dashboard created
- [x] Alerts configured
- [x] P95 latency < 10s verified under load

**Understandability (Living Docs)**:
- [x] All functions have docstrings
- [x] Architecture diagram up-to-date
- [x] RUNBOOK.md complete
- [x] README quick start works

### 11.2 Final Checks

- [x] 11.2.1 Run full test suite: `pytest --cov`
- [x] 11.2.2 Run linters: `ruff check`, `mypy`
- [x] 11.2.3 Start service and verify health check
- [x] 11.2.4 Test chat flow end-to-end (Playwright E2E tests)
- [x] 11.2.5 Test learning flow: learn word → confirm → view in history (E2E)
- [x] 11.2.6 Test learning flow: learn topic → confirm → view in history (E2E)
- [x] 11.2.7 Verify metrics appear in `/metrics`

### 11.3 E2E Testing

- [x] 11.3.1 Create Playwright configuration
- [x] 11.3.2 Write E2E tests for chat flow
- [x] 11.3.3 Write E2E tests for learning flow
- [x] 11.3.4 Write E2E tests for task management
- [x] 11.3.5 Write E2E tests for note management
- [x] 11.3.6 Write E2E tests for reminder management
- [x] 11.3.7 Write E2E tests for utility tools

**Checkpoint**: Feature ready for release.

---

## Summary: Build Order (Three Protectors)

| Phase | Component | Protector | Verification |
|-------|-----------|-----------|--------------|
| 1 | Dependencies & Models | TDD | Unit tests: save/load |
| 2 | Chat Service | TDD | Unit tests: CRUD |
| 3 | **Learning Tools** | TDD | Unit tests: word, sentence, topic |
| 4 | Utility Tools | TDD | Unit tests: weather, calculator |
| 5 | LangChain Agent | TDD | Unit tests: chat + all tools + SSL |
| 6 | API Layer | TDD | Acceptance tests AT-1 to AT-11 |
| 7 | Frontend Chat UI & Learning | — | Manual UI test |
| 8 | Additional Tools (Optional) | TDD | Unit tests per tool |
| 9 | Metrics Instrumentation | **MDD** | Metrics visible in /metrics |
| 10 | Living Documentation | **Docs** | Runbook + Architecture diagram |
| 11 | Final Validation | **All 3** | Checklist complete |

---

## Acceptance Test Cases (Quick Reference)

| ID | Endpoint | Test |
|----|----------|------|
| AT-1 | POST /chat | Valid auth → streaming response |
| AT-2 | POST /chat | No auth → 401 |
| AT-3 | POST /chat | No session_id → creates new session |
| AT-4 | POST /chat | With session_id → continues session |
| AT-5 | GET /sessions | Returns user's sessions |
| AT-6 | GET /sessions/{id} | Returns session with messages |
| AT-7 | DELETE /sessions/{id} | Deletes, returns 204 |
| AT-8 | GET /tools | Returns available tools |
| AT-9 | POST /learning/confirm | Saves learning record |
| AT-10 | GET /learning/records | Returns user's learning records |
| AT-11 | GET /learning/search | Search learning records |
