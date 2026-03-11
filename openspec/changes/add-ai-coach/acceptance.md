# Acceptance Test Cases & Metrics: add-ai-coach

## Overview

| Category | Test Cases | Priority |
|----------|-----------|----------|
| RAG Knowledge Base | TC-KB-001 ~ TC-KB-010 | P0 |
| Coach Chat (3 Modes) | TC-CC-001 ~ TC-CC-012 | P0 |
| Learning Plan Tracking | TC-LP-001 ~ TC-LP-010 | P0 |
| Sub-Agent Integration | TC-SA-001 ~ TC-SA-005 | P1 |
| Frontend Views | TC-FE-001 ~ TC-FE-008 | P1 |
| Non-Functional / Performance | TC-NF-001 ~ TC-NF-006 | P2 |
| **Total** | **51 test cases** | |

---

## 1. RAG Knowledge Base (TC-KB)

### TC-KB-001: Text document upload — happy path
- **Precondition**: Authenticated user with valid JWT
- **Steps**:
  1. POST `/api/v1/knowledge/documents` with `{"title": "Python Basics", "content": "Python is a high-level...", "tags": ["python"]}`
- **Expected**:
  - HTTP 201
  - Response contains `id`, `title`, `word_count > 0`, `created_at`
  - Document appears in `GET /api/v1/knowledge/documents`
  - Document is queryable via RAG (verified in TC-KB-006)
- **Priority**: P0

### TC-KB-002: Text document upload — auth required
- **Precondition**: No JWT / expired JWT
- **Steps**:
  1. POST `/api/v1/knowledge/documents` without Authorization header
- **Expected**: HTTP 401 Unauthorized
- **Priority**: P0

### TC-KB-003: Text document upload — validation
- **Precondition**: Authenticated user
- **Steps**:
  1. POST with `{"title": "", "content": "some text"}` (empty title)
  2. POST with `{"content": "some text"}` (missing title)
- **Expected**: HTTP 422 for both
- **Priority**: P0

### TC-KB-004: File upload — PDF/TXT/MD
- **Precondition**: Authenticated user
- **Steps**:
  1. POST a `.txt` file to `/api/v1/knowledge/documents/file`
  2. POST a `.md` file
  3. POST a `.pdf` file
- **Expected**:
  - HTTP 201 for all three
  - Each response contains extracted `word_count > 0`
  - Documents appear in listing
- **Priority**: P0

### TC-KB-005: File upload — unsupported type rejected
- **Precondition**: Authenticated user
- **Steps**:
  1. POST a `.exe` file to `/api/v1/knowledge/documents/file`
  2. POST a `.zip` file
- **Expected**: HTTP 400 with message indicating supported types (PDF, TXT, MD)
- **Priority**: P0

### TC-KB-006: RAG semantic query — returns relevant results
- **Precondition**: User has uploaded 3 documents: "Python Basics", "JavaScript Guide", "Machine Learning Intro"
- **Steps**:
  1. POST `/api/v1/knowledge/query` with `{"query": "How do decorators work in Python?", "top_k": 3}`
- **Expected**:
  - HTTP 200
  - Results list is non-empty
  - Top result references "Python Basics" document
  - Each result contains `source_title`, `text`, `similarity_score`
- **Priority**: P0

### TC-KB-007: RAG query — empty knowledge base
- **Precondition**: User has no uploaded documents
- **Steps**:
  1. POST `/api/v1/knowledge/query` with `{"query": "anything"}`
- **Expected**:
  - HTTP 200
  - `results` is an empty list (NOT an error)
- **Priority**: P0

### TC-KB-008: RAG query — respects top_k
- **Precondition**: User has 10 uploaded documents
- **Steps**:
  1. POST query with `top_k=2`
  2. POST query with `top_k=5`
- **Expected**:
  - First query returns ≤ 2 results
  - Second query returns ≤ 5 results
- **Priority**: P1

### TC-KB-009: Document deletion — removes from DB and vector store
- **Precondition**: User has uploaded "Test Doc" and verified it's queryable
- **Steps**:
  1. DELETE `/api/v1/knowledge/documents/{doc_id}`
  2. GET `/api/v1/knowledge/documents` — verify doc is gone
  3. POST `/api/v1/knowledge/query` with content from deleted doc
- **Expected**:
  - Step 1: HTTP 200
  - Step 2: Document not in list
  - Step 3: Deleted document does NOT appear in RAG results
- **Priority**: P0

### TC-KB-010: Per-user isolation — user A cannot see user B's documents
- **Precondition**: User A and User B both authenticated
- **Steps**:
  1. User A uploads "Secret Notes"
  2. User B calls GET `/api/v1/knowledge/documents`
  3. User B queries RAG with content from User A's document
  4. User B tries DELETE on User A's document ID
- **Expected**:
  - Step 2: User A's document NOT in User B's list
  - Step 3: No results from User A's document
  - Step 4: HTTP 404
- **Priority**: P0

---

## 2. Coach Chat — 3 Modes (TC-CC)

### TC-CC-001: Coach mode — non-streaming happy path
- **Precondition**: Authenticated user
- **Steps**:
  1. POST `/api/v1/coach/chat` with `{"message": "我想学习 Python，该怎么开始？", "mode": "coach"}`
- **Expected**:
  - HTTP 200
  - Response contains `content` (non-empty string with coaching tone)
  - Response contains `session_id`
  - Response contains `sources` (list, may be empty if no knowledge base)
- **Priority**: P0

### TC-CC-002: Tutor mode — deep explanation style
- **Precondition**: Authenticated user with "Python Basics" in knowledge base
- **Steps**:
  1. POST `/api/v1/coach/chat` with `{"message": "请详细解释 Python 的装饰器", "mode": "tutor"}`
- **Expected**:
  - Response `content` contains detailed explanation with examples (tutor style)
  - `sources` references "Python Basics" document (RAG injected)
- **Priority**: P0

### TC-CC-003: Quiz mode — asks questions
- **Precondition**: Authenticated user
- **Steps**:
  1. POST `/api/v1/coach/chat` with `{"message": "测试我的 Python 知识", "mode": "quiz"}`
- **Expected**:
  - Response `content` contains a question (quiz style)
  - `sources` is empty (quiz mode does NOT use RAG)
- **Priority**: P0

### TC-CC-004: Default mode is coach
- **Precondition**: Authenticated user
- **Steps**:
  1. POST `/api/v1/coach/chat` with `{"message": "帮我规划学习"}` (no `mode` field)
- **Expected**:
  - Response uses coach mode (motivational, planning-oriented)
- **Priority**: P1

### TC-CC-005: SSE streaming — event format
- **Precondition**: Authenticated user
- **Steps**:
  1. POST `/api/v1/coach/chat/stream` with `{"message": "你好", "mode": "coach"}`
  2. Consume SSE stream
- **Expected**:
  - Response `Content-Type: text/event-stream`
  - First event: `data: {"type":"start","session_id":"..."}`
  - Middle events: `data: {"type":"token","content":"..."}` (multiple)
  - Last event: `data: {"type":"done","sources":[...]}`
  - Concatenated tokens form a coherent response
- **Priority**: P0

### TC-CC-006: SSE streaming — error handling
- **Precondition**: LLM service is unavailable (mock/simulate)
- **Steps**:
  1. POST `/api/v1/coach/chat/stream` with valid request
- **Expected**:
  - Stream emits `data: {"type":"error","content":"..."}`
  - Stream closes gracefully
- **Priority**: P1

### TC-CC-007: Session continuity — multi-turn conversation
- **Precondition**: Authenticated user
- **Steps**:
  1. POST `/api/v1/coach/chat` with `{"message": "我在学 Rust"}` → get `session_id`
  2. POST `/api/v1/coach/chat` with `{"message": "上次我说的是什么语言？", "session_id": "<from step 1>"}`
- **Expected**:
  - Step 2 response references "Rust" (proves conversation history is loaded)
- **Priority**: P0

### TC-CC-008: New session created when no session_id
- **Precondition**: Authenticated user
- **Steps**:
  1. POST `/api/v1/coach/chat` with `{"message": "hello"}` (no session_id)
  2. POST `/api/v1/coach/chat` with `{"message": "hello"}` (no session_id)
- **Expected**:
  - Both responses contain `session_id`
  - The two `session_id` values are different
- **Priority**: P1

### TC-CC-009: RAG context injection — coach mode
- **Precondition**: User has uploaded "LlamaIndex Tutorial" document
- **Steps**:
  1. POST `/api/v1/coach/chat` with `{"message": "LlamaIndex 的核心概念是什么？", "mode": "coach"}`
- **Expected**:
  - Response `content` includes information from the uploaded document
  - `sources` list contains "LlamaIndex Tutorial"
- **Priority**: P0

### TC-CC-010: RAG context NOT injected in quiz mode
- **Precondition**: User has uploaded documents
- **Steps**:
  1. POST `/api/v1/coach/chat` with `{"message": "考考我", "mode": "quiz"}`
- **Expected**:
  - `sources` is empty
- **Priority**: P1

### TC-CC-011: Learning progress context injection — coach mode
- **Precondition**: User has an active goal "Learn Python" with 5 study sessions logged
- **Steps**:
  1. POST `/api/v1/coach/chat` with `{"message": "我的学习进度怎么样？", "mode": "coach"}`
- **Expected**:
  - Response references the user's actual progress data (streak, total time, etc.)
- **Priority**: P0

### TC-CC-012: Coach chat — auth required
- **Precondition**: No JWT
- **Steps**:
  1. POST `/api/v1/coach/chat` without Authorization
  2. POST `/api/v1/coach/chat/stream` without Authorization
- **Expected**: Both return HTTP 401
- **Priority**: P0

---

## 3. Learning Plan Tracking (TC-LP)

### TC-LP-001: Create learning goal — happy path
- **Precondition**: Authenticated user
- **Steps**:
  1. POST `/api/v1/coach/goals` with `{"subject": "Learn Rust", "description": "Master Rust basics in 30 days", "daily_target_minutes": 60, "deadline": "2026-04-05"}`
- **Expected**:
  - HTTP 201
  - Response contains `id`, `subject`, `status: "active"`, `created_at`
- **Priority**: P0

### TC-LP-002: Create goal — validation
- **Precondition**: Authenticated user
- **Steps**:
  1. POST with `{}` (missing subject)
  2. POST with `{"subject": ""}` (empty subject)
- **Expected**: HTTP 422 for both
- **Priority**: P0

### TC-LP-003: List goals — with status filter
- **Precondition**: User has 2 active goals and 1 completed goal
- **Steps**:
  1. GET `/api/v1/coach/goals` — all goals
  2. GET `/api/v1/coach/goals?status=active` — active only
  3. GET `/api/v1/coach/goals?status=completed` — completed only
- **Expected**:
  - Step 1: 3 goals
  - Step 2: 2 goals (all active)
  - Step 3: 1 goal (completed)
- **Priority**: P0

### TC-LP-004: Update goal — complete a goal
- **Precondition**: User has an active goal
- **Steps**:
  1. PATCH `/api/v1/coach/goals/{id}` with `{"status": "completed"}`
- **Expected**:
  - HTTP 200
  - Response shows `status: "completed"` and `completed_at` is set
- **Priority**: P0

### TC-LP-005: Update goal — cross-user isolation
- **Precondition**: User A has a goal, User B is authenticated
- **Steps**:
  1. User B PATCHes `/api/v1/coach/goals/{user_a_goal_id}` with `{"status": "completed"}`
- **Expected**: HTTP 404
- **Priority**: P0

### TC-LP-006: Log study session — happy path
- **Precondition**: User has an active goal
- **Steps**:
  1. POST `/api/v1/coach/sessions` with `{"goal_id": "<id>", "duration_minutes": 45, "notes": "Finished chapter 3", "difficulty": 3}`
- **Expected**:
  - HTTP 201
  - Response contains `id`, `goal_id`, `duration_minutes`, `difficulty`, `created_at`
- **Priority**: P0

### TC-LP-007: Log study session — validation
- **Precondition**: Authenticated user
- **Steps**:
  1. POST with `goal_id` that doesn't exist → HTTP 404
  2. POST with `goal_id` belonging to another user → HTTP 404
  3. POST with `difficulty: 6` (out of range 1-5) → HTTP 422
  4. POST with `difficulty: 0` → HTTP 422
- **Priority**: P0

### TC-LP-008: Progress report — comprehensive metrics
- **Precondition**: User has a goal with 7 study sessions over 10 days (sessions on days 1,2,3,4,5, skip 6,7, sessions on 8,9)
- **Steps**:
  1. GET `/api/v1/coach/progress/{goal_id}`
- **Expected**:
  - `total_sessions`: 7
  - `total_minutes`: sum of all session durations
  - `current_streak`: 2 (days 8,9)
  - `longest_streak`: 5 (days 1-5)
  - `avg_difficulty`: average of all difficulty ratings
  - `last_session_date`: day 9
  - `completion_percentage`: calculated based on daily target
  - `ai_feedback`: non-empty string with personalized advice
- **Priority**: P0

### TC-LP-009: Progress report — no sessions
- **Precondition**: User has a goal with zero study sessions
- **Steps**:
  1. GET `/api/v1/coach/progress/{goal_id}`
- **Expected**:
  - All numeric metrics are 0
  - `ai_feedback` is non-empty (encouraging message to get started)
- **Priority**: P1

### TC-LP-010: List sessions — filter by goal
- **Precondition**: User has 2 goals, 3 sessions for goal A, 2 sessions for goal B
- **Steps**:
  1. GET `/api/v1/coach/sessions?goal_id={goal_a_id}`
  2. GET `/api/v1/coach/sessions?goal_id={goal_b_id}`
- **Expected**:
  - Step 1: 3 sessions, all for goal A
  - Step 2: 2 sessions, all for goal B
  - Sessions ordered by date descending
- **Priority**: P0

---

## 4. Sub-Agent Integration (TC-SA)

### TC-SA-001: Supervisor routes coaching keywords to coach agent
- **Precondition**: Secretary agent is running
- **Steps**:
  1. Send via secretary chat: "帮我制定一个学习 Python 的计划"
  2. Send via secretary chat: "查询我的知识库中关于 Docker 的内容"
  3. Send via secretary chat: "我的学习进度怎么样"
- **Expected**: All three are routed to the coach sub-agent (verify via logs or response content)
- **Priority**: P1

### TC-SA-002: Coach sub-agent — query_knowledge tool
- **Precondition**: User has documents in knowledge base
- **Steps**:
  1. Send via secretary chat: "从我的知识库中找找关于 API 设计的内容"
- **Expected**: Response includes knowledge base content (tool was invoked)
- **Priority**: P1

### TC-SA-003: Coach sub-agent — create_goal tool
- **Precondition**: Secretary agent running
- **Steps**:
  1. Send via secretary chat: "帮我创建一个学习目标：30天掌握 Go 语言"
- **Expected**: A new learning goal is created in the database
- **Priority**: P1

### TC-SA-004: Coach sub-agent — log_study_session tool
- **Precondition**: User has an active goal
- **Steps**:
  1. Send via secretary chat: "我今天学了45分钟的 Go，难度中等"
- **Expected**: A study session is logged for the relevant goal
- **Priority**: P1

### TC-SA-005: Non-coaching requests NOT routed to coach
- **Precondition**: Secretary agent running
- **Steps**:
  1. Send: "今天天气怎么样" (weather → utility agent)
  2. Send: "帮我记个笔记" (note → productivity agent)
- **Expected**: Neither is routed to coach agent
- **Priority**: P1

---

## 5. Frontend Views (TC-FE)

### TC-FE-001: Coach chat view — mode switching
- **Precondition**: User logged in, navigates to `/coach`
- **Steps**:
  1. Select "教练" mode → send message → verify coaching-style response
  2. Switch to "辅导" mode → send message → verify tutor-style response
  3. Switch to "测验" mode → send message → verify quiz-style response
- **Expected**: Each mode produces visually distinct and appropriately styled responses
- **Priority**: P1

### TC-FE-002: Coach chat view — SSE streaming display
- **Precondition**: User on coach chat page
- **Steps**:
  1. Send a message
  2. Observe response appearing token by token
- **Expected**: Tokens render progressively (not all at once); loading indicator shown during streaming
- **Priority**: P1

### TC-FE-003: Knowledge base view — upload and list
- **Precondition**: User navigates to `/knowledge`
- **Steps**:
  1. Upload a text document via form
  2. Upload a `.md` file via file picker
  3. Verify both appear in the document list
- **Expected**: Documents listed with title, word count, tags, creation date
- **Priority**: P1

### TC-FE-004: Knowledge base view — query
- **Precondition**: User has uploaded documents
- **Steps**:
  1. Enter a query in the search box
  2. Submit
- **Expected**: Results displayed with source titles, relevant text snippets, and similarity scores
- **Priority**: P1

### TC-FE-005: Knowledge base view — delete document
- **Precondition**: User has documents listed
- **Steps**:
  1. Click delete on a document
  2. Confirm deletion
- **Expected**: Document removed from list; subsequent query does not return it
- **Priority**: P1

### TC-FE-006: Learning plan view — goal CRUD
- **Precondition**: User navigates to `/learning-plan`
- **Steps**:
  1. Create a new goal with subject, description, deadline, daily target
  2. Verify it appears in the goals list as "active"
  3. Mark it as "completed"
  4. Verify status changes
- **Expected**: Full CRUD lifecycle works; status transitions reflected in UI
- **Priority**: P1

### TC-FE-007: Learning plan view — log session and see progress
- **Precondition**: User has an active goal
- **Steps**:
  1. Log a study session (duration, notes, difficulty)
  2. View progress report for the goal
- **Expected**: Progress shows updated metrics (total sessions, total minutes, streak, AI feedback)
- **Priority**: P1

### TC-FE-008: Navigation — new menu entries
- **Precondition**: User logged in
- **Steps**:
  1. Check navigation bar/sidebar
- **Expected**: "AI 教练", "知识库", "学习计划" entries visible and link to correct routes
- **Priority**: P1

---

## 6. Non-Functional / Performance (TC-NF)

### TC-NF-001: RAG indexing latency
- **Precondition**: Empty knowledge base
- **Steps**:
  1. Upload a 5,000-word document
  2. Measure time from request to 201 response
- **Expected**: ≤ 10 seconds (including chunking + embedding + ChromaDB insert)
- **Priority**: P2

### TC-NF-002: RAG query latency
- **Precondition**: Knowledge base with 20 documents (~50,000 words total)
- **Steps**:
  1. POST a query, measure response time
- **Expected**: ≤ 3 seconds (embedding + vector search + result formatting)
- **Priority**: P2

### TC-NF-003: Coach chat latency — first token (streaming)
- **Precondition**: User with knowledge base and active goals
- **Steps**:
  1. POST streaming chat, measure time to first `token` event
- **Expected**: ≤ 5 seconds (includes RAG query + progress fetch + LLM first token)
- **Priority**: P2

### TC-NF-004: Graceful degradation — ChromaDB unavailable
- **Precondition**: ChromaDB service/directory not available
- **Steps**:
  1. Start the application
  2. POST coach chat message
- **Expected**:
  - Application starts without crash
  - Coach chat works (without RAG context)
  - Knowledge endpoints return appropriate error (503 or empty results with warning)
- **Priority**: P2

### TC-NF-005: Database migration — non-destructive
- **Precondition**: Existing database with user data
- **Steps**:
  1. Run `alembic upgrade head`
  2. Verify existing tables and data are intact
  3. Verify 3 new tables created: `knowledge_documents`, `learning_goals`, `study_sessions`
- **Expected**: Zero data loss; migration is additive only
- **Priority**: P0

### TC-NF-006: Concurrent user isolation under load
- **Precondition**: 2 authenticated users
- **Steps**:
  1. User A and User B simultaneously upload documents
  2. User A and User B simultaneously query knowledge base
  3. User A and User B simultaneously create goals
- **Expected**: No cross-contamination; each user sees only their own data
- **Priority**: P2

---

## Acceptance Metrics

### Coverage Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Unit test coverage (new code) | ≥ 80% | `pytest --cov` on new modules |
| API endpoint coverage | 100% | Every new endpoint has ≥ 1 test |
| Spec scenario coverage | 100% | Every scenario in specs/ maps to ≥ 1 test case above |
| P0 test pass rate | 100% | All P0 tests must pass before merge |
| P1 test pass rate | ≥ 90% | At most 1 P1 test may be deferred |

### Quality Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| RAG retrieval relevance | ≥ 70% precision@3 | Manual evaluation: upload 5 docs, run 10 queries, check if top-3 results are relevant |
| Coach mode differentiation | 3/3 modes distinguishable | Manual evaluation: same question in 3 modes produces clearly different response styles |
| Streak calculation accuracy | 100% | Unit test with known date sequences (TC-LP-008 scenario) |
| AI feedback quality | Non-empty, contextual | Manual check: feedback references actual progress data, not generic |
| SSE protocol compliance | 100% | All streams follow `start → token* → done` sequence |

### Performance Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Document indexing (5K words) | ≤ 10s | TC-NF-001 |
| RAG query (20 docs) | ≤ 3s | TC-NF-002 |
| Streaming first token | ≤ 5s | TC-NF-003 |
| DB migration time | ≤ 5s | Time `alembic upgrade head` |
| ChromaDB disk usage (100 docs) | ≤ 500MB | Check `data/chroma/` size |

### Regression Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Existing test suite | 100% pass | `pytest` — all pre-existing tests still pass |
| Secretary agent routing | No degradation | Existing secretary tests pass; non-coach requests still route correctly |
| API startup time | ≤ +2s increase | Measure `uvicorn` startup before/after |
| Memory usage at idle | ≤ +200MB increase | ChromaDB + LlamaIndex overhead |

### Definition of Done

- [ ] All P0 test cases (26 cases) pass
- [ ] ≥ 90% of P1 test cases (14 cases) pass
- [ ] Unit test coverage ≥ 80% on new modules
- [ ] All 3 new DB tables created via Alembic migration (non-destructive)
- [ ] All 14 new API endpoints respond correctly with auth
- [ ] RAG query returns relevant results for uploaded documents
- [ ] 3 coaching modes produce distinguishable responses
- [ ] SSE streaming follows the established protocol
- [ ] Existing test suite passes with zero regressions
- [ ] Frontend views render and function (coach chat, knowledge base, learning plan)
- [ ] Documentation updated (API docs, README)
