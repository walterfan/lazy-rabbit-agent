# Tasks: add-philosophy-master-agent

## 1. Backend scaffolding and contracts

- [x] 1.1 Create `app/services/philosophy_master_agent/` module structure (prompts, preset validation, safety)
- [x] 1.2 Add Pydantic request/response schemas for philosophy chat (message, preset enums, optional context)
- [x] 1.3 Define SSE event schema for streaming (`token`, `meta`, `done`, `error`) consistent with frontend parser

## 2. Prompting, presets, and safety behavior

- [x] 2.1 Implement preset allowlists (school/tone/depth/mode/multi_perspective) and reject invalid values with 400
- [x] 2.2 Create system prompt template with role boundaries (not therapy/medical/legal) and structured output format
- [x] 2.3 Implement “advice” mode response structure: framing + actions + reflection questions
- [x] 2.4 Implement “compare” mode: 2–3 lenses + trade-off comparison + suggested next step
- [x] 2.5 Implement “story” mode: short parable/典故 + explicit takeaway mapped to user issue
- [x] 2.6 Implement “daily_practice” mode: principle + exercise + 1–3 reflection questions
- [x] 2.7 Implement crisis/self-harm detection and safe response (refuse instructions + encourage professional/emergency help)

## 3. Philosophy API endpoints (FastAPI)

- [x] 3.1 Add `POST /api/v1/philosophy/chat` (JWT required): validate request, call service, return `{ content, sections? }`
- [x] 3.2 Add `POST /api/v1/philosophy/chat/stream` (JWT required): stream SSE tokens; include optional `meta` first event
- [x] 3.3 Add clear 400 validation errors for missing/empty message
- [x] 3.4 Register philosophy router in `app/api/v1/api.py` under `/philosophy`

## 4. Frontend: Philosophy Master page

- [x] 4.1 Add `PhilosophyMaster.vue` view (chat UI) reusing the Secretary chat layout patterns
- [x] 4.2 Add preset selectors (school/tone/depth/mode/multi_perspective) and send them in requests
- [x] 4.3 Implement streaming consumption for philosophy SSE (token updates + done/error)
- [x] 4.4 Add route `/philosophy` and navigation entry in header
- [x] 4.5 Add Philosophy Master card to Home page “AI Agents” section

## 5. Tests and docs

- [x] 5.1 Backend tests: auth required, validation errors, preset allowlist rejection
- [x] 5.2 Backend tests: streaming endpoint returns `text/event-stream` and yields `token` + `done`
- [x] 5.3 Document the new endpoints and request preset fields in `docs/source/04-data-and-api.md`

