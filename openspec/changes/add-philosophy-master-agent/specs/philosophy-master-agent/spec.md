## ADDED Requirements

### Requirement: Philosophy Master agent provides philosophical guidance via chat

The system SHALL provide a chat-style AI agent (“Philosophy Master”) that helps users analyze烦恼/困惑 from philosophical perspectives and provides actionable guidance. The agent response MUST be empathetic, structured, and oriented toward clarity and practice (not diagnosis).

#### Scenario: User asks a philosophical question and receives structured guidance

- **WHEN** the user sends a message describing a烦恼/困惑 to the Philosophy Master chat endpoint
- **THEN** the system responds with content that includes:
  - philosophical framing (e.g., concept clarification / perspective shift / value analysis)
  - actionable suggestions (e.g., concrete steps, practices, or reflection prompts)

### Requirement: Philosophy Master endpoints require authentication

The system SHALL require a valid JWT for Philosophy Master endpoints. Requests without a valid token SHALL receive 401 Unauthorized.

#### Scenario: Unauthenticated request rejected

- **WHEN** a client calls the Philosophy Master endpoints without a valid Authorization token
- **THEN** the system responds with 401 Unauthorized

#### Scenario: Authenticated request accepted

- **WHEN** a client calls the Philosophy Master endpoints with a valid JWT
- **THEN** the system processes the request and returns a response or a well-formed 4xx error

### Requirement: Chat API supports non-streaming responses

The system SHALL provide a non-streaming endpoint for Philosophy Master chat (e.g. `POST /api/v1/philosophy/chat`). The request MUST contain `message` as a non-empty string. The response MUST contain a `content` string.

#### Scenario: Successful non-streaming chat response

- **WHEN** the client POSTs a valid request with `message`
- **THEN** the system returns HTTP 200 with JSON containing a non-empty `content` string

#### Scenario: Missing message rejected

- **WHEN** the client POSTs a request without `message` or with an empty message
- **THEN** the system responds with 400 Bad Request and a clear validation message

### Requirement: Chat API supports streaming responses (SSE)

The system SHALL provide a streaming endpoint for Philosophy Master chat (e.g. `POST /api/v1/philosophy/chat/stream`) that returns Server-Sent Events (`Content-Type: text/event-stream`). The stream MUST deliver incremental content and MUST terminate with a done event.

#### Scenario: Streaming chat returns tokens progressively

- **WHEN** the client requests a streaming chat with a valid `message`
- **THEN** the system responds with an SSE stream that includes events containing incremental content

#### Scenario: Streaming chat terminates cleanly

- **WHEN** the streaming response completes
- **THEN** the stream includes a terminal event indicating completion (e.g. `type: done`) and the connection ends normally

### Requirement: Request supports configurable philosophy presets (school/tone/depth/mode)

The system SHALL allow the client to select a response style via request presets. Presets MUST be validated against an allowlist; invalid values SHALL be rejected with 400 Bad Request.

The preset SHALL support at least:

- `school`: `eastern|western|zen|confucian|stoic|existential|kant|nietzsche|schopenhauer|idealism|materialism|mixed`
- `tone`: `gentle|direct|rigorous|zen`
- `depth`: `shallow|medium|deep`
- `mode`: `advice|story|compare|daily_practice`
- `multi_perspective`: boolean

#### Scenario: Client selects Zen mode for concise guidance

- **WHEN** the client sends a request with `preset.school=zen` and a valid message
- **THEN** the response content reflects Zen-style brevity and directness (while still providing practical guidance)

#### Scenario: Invalid preset value rejected

- **WHEN** the client sends a request with an out-of-allowlist preset value (e.g., `preset.tone=angry`)
- **THEN** the system responds with 400 Bad Request and indicates allowed values

### Requirement: Multi-perspective comparison mode is supported

When `preset.mode=compare` or `preset.multi_perspective=true`, the system SHALL produce a response that compares 2–3 philosophical lenses, highlighting their different framings and what each lens recommends.

#### Scenario: Compare mode provides contrasting lenses

- **WHEN** the client requests compare mode for the same message
- **THEN** the response includes at least 2 distinct philosophical framings and a short comparison of trade-offs

### Requirement: Story mode is supported

When `preset.mode=story`, the system SHALL include a short philosophical story/parable/典故 that illuminates the user’s issue and connects the story to actionable guidance.

#### Scenario: Story mode includes a parable and takeaway

- **WHEN** the client requests story mode
- **THEN** the response includes a story/parable/典故 and a clearly stated takeaway that maps to the user’s situation

### Requirement: Reading list guidance can be included

The system SHALL be able to include a brief reading list / learning path tailored to the user’s topic or chosen school when appropriate (e.g., in deep mode or on user request).

#### Scenario: Reading list is provided on request

- **WHEN** the user asks for recommended readings or learning path
- **THEN** the response includes a short reading list with rationale (why each item is recommended)

### Requirement: Daily practice mode is supported

When `preset.mode=daily_practice`, the system SHALL provide a short daily practice that includes a principle, a small exercise, and 1–3 reflection questions.

#### Scenario: Daily practice provides an exercise and reflection questions

- **WHEN** the client requests daily practice mode
- **THEN** the response includes a practice/exercise and 1–3 reflection questions

### Requirement: Safety boundaries for crisis and self-harm content

The system SHALL implement safety behavior for crisis/self-harm content:

- The system MUST NOT provide instructions for self-harm or violence.
- The system MUST respond with supportive, non-therapeutic guidance and encourage contacting appropriate local emergency services or professionals when crisis intent is indicated.

#### Scenario: Self-harm instructions are refused

- **WHEN** the user asks for instructions to self-harm
- **THEN** the system refuses to provide instructions and provides safer alternatives and support guidance

#### Scenario: Crisis intent triggers support guidance

- **WHEN** the user expresses intent to self-harm or indicates imminent danger
- **THEN** the system responds with crisis-safe guidance and encourages contacting local emergency services or a trusted person

