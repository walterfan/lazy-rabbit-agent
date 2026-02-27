## Context

- **Current state**: The system already has chat-style AI experiences (e.g., Personal Secretary) with JWT auth and streaming (SSE) responses. Frontend uses a chat UI and can consume token streams.
- **New capability**: Add a dedicated chat agent “Philosophy Master” (哲学大师) that answers user烦恼/困惑 from philosophical perspectives (Eastern/Western; Zen/Buddhism; Confucian; Stoicism; Existentialism; Kant; Nietzsche; Schopenhauer; idealism/materialism, etc.), optionally via story/parable mode and multi-perspective comparison.
- **Users**: People seeking meaning-making, value clarification, and actionable guidance (not therapy). Output should be empathetic, structured, and practical.
- **Constraints**:
  - Reuse existing LLM provider configuration and streaming approach.
  - Keep secrets out of logs and UI traces; do not log raw user content in production.
  - Maintain existing auth pattern (`Authorization: Bearer <JWT>`).

**Threat snapshot / trust boundaries**

- **Entry points**: `POST /api/v1/philosophy/chat` and `POST /api/v1/philosophy/chat/stream` (plus frontend page inputs for presets).
- **Trust boundaries**: User-provided text (untrusted) → backend prompt construction → LLM provider (external).
- **Sensitive data**: User’s personal problems may contain PII and mental-health related content.
- **Risks**:
  - Prompt-injection / unsafe instructions (user asks for self-harm, illegal acts, harassment).
  - Privacy leakage in logs/telemetry.
  - Over-reliance on the agent for medical/legal/mental-health advice.

## Goals / Non-Goals

**Goals:**

- Provide a Philosophy Master chat agent with:
  - **Configurable presets**: school/lens (东方/西方/禅宗/儒家/斯多葛/存在主义/康德/尼采/叔本华/唯心/唯物…), tone (温和/犀利/简练/论证式), depth (浅/中/深), and mode (答疑 / 讲故事 / 多视角对照 / 每日练习).
  - **Structured answer**: philosophical framing (概念澄清、视角转换、价值辨析) + practical steps (可执行建议、练习、反思问题).
  - **Streaming**: token streaming for better UX; compatible with the frontend streaming renderer.
  - **Safety boundaries**: recognize crisis/self-harm cues; respond with safe, non-therapeutic guidance and encourage professional help; refuse disallowed content.

**Non-Goals:**

- Not a medical/legal/psychotherapy substitute; no diagnosis.
- No long-term memory/persistence of sensitive conversations beyond existing session model (unless a later change adds explicit “save”).
- No multi-language expansion beyond Chinese UI/outputs in this change (can be added later).

## Decisions

### 1. API shape: dedicated endpoints mirroring existing chat patterns

- **Decision**: Add endpoints under `/api/v1/philosophy`:
  - `POST /api/v1/philosophy/chat` (non-streaming JSON)
  - `POST /api/v1/philosophy/chat/stream` (SSE streaming)
- **Rationale**: Matches the existing “Secretary” streaming pattern; reduces frontend work and keeps the agent concept cleanly separated.
- **Alternatives**:
  - Reuse `/secretary/chat` with a tool/prompt switch — rejected (couples behaviors and complicates prompts/guardrails).

### 2. Request contract: one message + optional preset controls

- **Decision**: Request body includes:
  - `message` (required): the user’s烦恼/问题
  - `preset` (optional object):
    - `school`: one of `eastern|western|zen|confucian|stoic|existential|kant|nietzsche|schopenhauer|idealism|materialism|mixed`
    - `tone`: `gentle|direct|rigorous|zen`
    - `depth`: `shallow|medium|deep`
    - `mode`: `advice|story|compare|daily_practice`
    - `multi_perspective`: boolean (if true, provide 2–3 schools and compare)
  - `context` (optional string): extra background; kept private (do not echo unless user asked).
- **Rationale**: Keeps inputs simple while still enabling differentiated outputs.
- **Input validation**: Enforce allowlists for preset enums; reject unknown values with 400.

### 3. Response shape: JSON for non-streaming; SSE event stream for streaming

- **Non-streaming response**: JSON with fields:
  - `content` (final markdown/text)
  - `sections` (optional structured fields): `analysis`, `actions`, `reflection_questions`, `story`, `reading_list`
- **Streaming**: SSE events where each `data:` payload is a single JSON object:
  - `{"type":"token","content":"..."}` for incremental text
  - `{"type":"meta","preset":{...}}` optional first event
  - `{"type":"done"}` end
  - `{"type":"error","content":"..."}` error
- **Rationale**: Frontend already supports token-based streaming; structured sections can evolve without breaking basic `content`.

### 4. Prompting strategy: system prompt + preset-conditioned style blocks

- **Decision**: Implement prompt templates with:
  - A **system instruction** that sets role boundaries (philosophy advisor, not therapist/doctor/lawyer), response format, and refusal policy.
  - A **preset-conditioned block** that injects the chosen school/tone/depth/mode and encourages citations (e.g., “use short quotes/parables”).
  - A **safety block** that triggers crisis handling (self-harm / violence) and provides resources guidance.
- **Rationale**: Stable structure; easy to add new presets; safer and more predictable.

### 5. Safety: deny-by-default for disallowed content; crisis escalation guidance

- **Decision**:
  - Refuse and redirect when user requests self-harm instructions, violence, harassment, or illegal acts.
  - If crisis/self-harm intent is detected: respond empathetically, encourage contacting local emergency services / hotlines / trusted person, and avoid detailed “how-to”.
- **Rationale**: Reduces harm and aligns with safe assistant behavior.

## Risks / Trade-offs

- **[Risk] Users treat it as therapy** → **Mitigation**: consistent disclaimers + crisis handling + encourage professional help; avoid diagnostic language.
- **[Risk] Prompt injection** → **Mitigation**: strict system prompt, preset allowlists, refuse unsafe requests, do not execute instructions outside scope.
- **[Risk] Privacy leakage in logs** → **Mitigation**: avoid logging full user inputs/prompts; redact; keep errors generic.
- **[Trade-off] “Story mode” can become verbose** → **Mitigation**: enforce max length and sectioned formatting; “deep” mode only when selected.

## Migration Plan

- **Backend**:
  - Add new router `philosophy.py` under `app/api/v1/endpoints/`
  - Register router in `app/api/v1/api.py`
  - Add service module under `app/services/philosophy_master_agent/` (or similar)
  - Reuse existing settings for LLM provider and streaming
- **Frontend**:
  - Add `PhilosophyMaster.vue` view with chat UI + preset selectors
  - Add navigation entry + home card
- **Rollback**:
  - Remove router registration and frontend route; no DB migrations required.

## Open Questions

- Should we persist philosophy chat sessions like Secretary (sessions/messages), or keep it stateless in v1?
- Do we want “daily practice” as a separate endpoint (e.g., `/daily`) for easy frontend refresh?
- Do we add a “reading list” structured schema now (array of {title, author, why, difficulty}) or keep it plain text initially?

