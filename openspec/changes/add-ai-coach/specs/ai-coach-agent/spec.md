## ADDED Requirements

### Requirement: Coach chat supports 3 modes (coach/tutor/quiz)

The system SHALL provide a coach chat endpoint that supports three distinct coaching modes, each with a different personality and behavior.

#### Scenario: Coach mode provides motivational guidance

- **WHEN** the user sends a message with `mode=coach`
- **THEN** the response reflects a motivational coaching style: tracking progress, encouraging the user, and providing personalized learning advice

#### Scenario: Tutor mode provides deep explanations

- **WHEN** the user sends a message with `mode=tutor`
- **THEN** the response reflects a patient tutor style: explaining concepts in depth, providing examples, and building understanding step by step

#### Scenario: Quiz mode asks questions and evaluates answers

- **WHEN** the user sends a message with `mode=quiz`
- **THEN** the response reflects an examiner style: asking one question at a time, evaluating the user's answer, and adjusting difficulty

#### Scenario: Default mode is coach

- **WHEN** the user sends a message without specifying a mode
- **THEN** the system uses `coach` mode by default

### Requirement: Coach chat endpoints require authentication

The system SHALL require a valid JWT for all coach chat endpoints.

#### Scenario: Unauthenticated request rejected

- **WHEN** a client calls coach chat endpoints without a valid Authorization token
- **THEN** the system responds with 401 Unauthorized

### Requirement: Coach chat supports non-streaming responses

The system SHALL provide `POST /api/v1/coach/chat` that returns a complete response.

#### Scenario: Successful non-streaming coach response

- **WHEN** an authenticated user POSTs a valid message to `/api/v1/coach/chat`
- **THEN** the system returns HTTP 200 with JSON containing `content`, `sources` (from RAG), and `session_id`

#### Scenario: Empty message rejected

- **WHEN** the user POSTs with an empty or missing `message`
- **THEN** the system responds with 422 Unprocessable Entity

### Requirement: Coach chat supports SSE streaming responses

The system SHALL provide `POST /api/v1/coach/chat/stream` that returns Server-Sent Events.

#### Scenario: Streaming returns tokens progressively

- **WHEN** an authenticated user requests streaming coach chat
- **THEN** the system responds with `Content-Type: text/event-stream`
- **AND** emits `{"type":"start","session_id":"..."}` as the first event
- **AND** emits `{"type":"token","content":"..."}` for each token
- **AND** emits `{"type":"done","sources":[...]}` as the final event

#### Scenario: Streaming error is reported via SSE

- **WHEN** an error occurs during streaming
- **THEN** the system emits `{"type":"error","content":"..."}` and closes the stream

### Requirement: Coach chat injects RAG context (coach and tutor modes)

In coach and tutor modes, the system SHALL query the user's knowledge base for relevant content and inject it into the LLM prompt as context.

#### Scenario: RAG context enhances coach response

- **WHEN** the user asks a question in coach or tutor mode
- **AND** the user has relevant documents in their knowledge base
- **THEN** the response incorporates information from the knowledge base
- **AND** the `sources` field lists the referenced document titles

#### Scenario: Coach works without knowledge base

- **WHEN** the user has no documents in their knowledge base
- **THEN** the coach still responds normally without RAG context

#### Scenario: Quiz mode does not use RAG

- **WHEN** the user is in quiz mode
- **THEN** the system does NOT inject RAG context (quiz tests the user's own knowledge)

### Requirement: Coach chat injects learning progress context

In coach mode, the system SHALL include the user's current learning progress (active goals, streaks, completion) in the prompt context.

#### Scenario: Coach references active goals

- **WHEN** the user has active learning goals
- **THEN** the coach's response may reference goal progress, deadlines, and streaks

### Requirement: Coach chat supports session continuity

The system SHALL support conversation continuity via `session_id`. If provided, the system loads previous messages for that session.

#### Scenario: Continuing a conversation

- **WHEN** the user sends a message with a valid `session_id`
- **THEN** the system includes previous messages from that session in the LLM context

#### Scenario: New session created when no session_id provided

- **WHEN** the user sends a message without `session_id`
- **THEN** the system creates a new session and returns the new `session_id`

### Requirement: Coach is integrated as a sub-agent in the supervisor workflow

The coach SHALL be available as a sub-agent in the SecretaryAgent supervisor, so users can access coaching features through the general secretary chat.

#### Scenario: Secretary routes coaching request to coach agent

- **WHEN** the user asks the secretary about learning goals, knowledge base, or coaching
- **THEN** the supervisor routes the request to the coach sub-agent

#### Scenario: Coach sub-agent uses tools

- **WHEN** the coach sub-agent handles a request
- **THEN** it can use tools: `query_knowledge`, `create_goal`, `log_study_session`, `get_progress`
