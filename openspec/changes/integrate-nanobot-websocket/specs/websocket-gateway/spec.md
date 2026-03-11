## ADDED Requirements

### Requirement: lazy-rabbit exposes a WebSocket endpoint for nanobot connections

The system SHALL provide a WebSocket endpoint at `/ws/nanobot` that accepts persistent connections from nanobot instances.

#### Scenario: nanobot connects and authenticates successfully

- **WHEN** nanobot opens a WebSocket connection to `/ws/nanobot`
- **AND** sends a `system.auth` message with a valid token
- **THEN** lazy-rabbit responds with `system.auth_ok` containing server version and capabilities
- **AND** the connection remains open for bidirectional communication

#### Scenario: Authentication fails with invalid token

- **WHEN** nanobot sends a `system.auth` message with an invalid token
- **THEN** lazy-rabbit responds with `system.auth_fail` with reason
- **AND** closes the WebSocket connection

#### Scenario: Connection without auth message times out

- **WHEN** nanobot connects but does not send `system.auth` within 10 seconds
- **THEN** lazy-rabbit closes the connection with a timeout error

### Requirement: WebSocket supports heartbeat keep-alive

The system SHALL implement bidirectional heartbeat to detect dead connections.

#### Scenario: Heartbeat exchange keeps connection alive

- **WHEN** the connection is idle for 30 seconds
- **THEN** either side sends a `system.heartbeat` message
- **AND** the other side responds with a `system.heartbeat` acknowledgment

#### Scenario: Missing heartbeat triggers disconnect

- **WHEN** a heartbeat is sent but no response is received within 10 seconds
- **THEN** the sender considers the connection dead and closes it

### Requirement: WebSocket gateway handles chat requests

The system SHALL accept `chat.request` messages from nanobot, route them to the appropriate agent, and return responses.

#### Scenario: Non-streaming chat request

- **WHEN** nanobot sends a `chat.request` with `{channel, chat_id, sender_id, message}`
- **THEN** lazy-rabbit routes the message to the secretary agent
- **AND** returns a `chat.response` with `{channel, chat_id, content, session_id}`

#### Scenario: Streaming chat request

- **WHEN** nanobot sends a `chat.request` with `stream: true`
- **THEN** lazy-rabbit sends `chat.stream.start` followed by `chat.stream.token` messages
- **AND** finishes with `chat.stream.done` containing `session_id` and `message_id`

#### Scenario: Chat request with specific agent

- **WHEN** nanobot sends a `chat.request` with `agent: "philosophy"`
- **THEN** lazy-rabbit routes directly to the philosophy master agent (bypassing supervisor routing)

#### Scenario: Chat request for unknown user triggers auto-creation

- **WHEN** nanobot sends a `chat.request` with an unmapped `(channel, chat_id)`
- **THEN** lazy-rabbit auto-creates a user and identity mapping
- **AND** processes the request normally

### Requirement: WebSocket gateway handles errors gracefully

The system SHALL return structured error messages for invalid or failed requests.

#### Scenario: Malformed message

- **WHEN** nanobot sends a message that is not valid JSON or missing required fields
- **THEN** lazy-rabbit responds with `system.error` containing error code and description
- **AND** the connection remains open

#### Scenario: Agent processing error

- **WHEN** the agent encounters an error processing a chat request
- **THEN** lazy-rabbit responds with `chat.stream.error` or `system.error` with the correlation_id
- **AND** the connection remains open

### Requirement: WebSocket connection manager supports multiple connections

The system SHALL support multiple concurrent nanobot connections, each independently authenticated.

#### Scenario: Two nanobot instances connect simultaneously

- **WHEN** nanobot-A and nanobot-B both connect and authenticate
- **THEN** both connections are maintained independently
- **AND** messages are routed to the correct connection based on originating channel/chat_id

### Requirement: WebSocket gateway is configurable

The system SHALL expose configuration for the WebSocket gateway.

#### Scenario: Configuration fields

- **GIVEN** the application configuration
- **THEN** the following fields are available:
  - `WS_NANOBOT_TOKEN`: shared authentication token
  - `WS_NANOBOT_MAX_CONNECTIONS`: maximum concurrent connections (default: 5)
  - `WS_NANOBOT_HEARTBEAT_INTERVAL`: heartbeat interval in seconds (default: 30)
  - `WS_NANOBOT_AUTH_TIMEOUT`: auth timeout in seconds (default: 10)
  - `WS_NANOBOT_STREAM_CHUNK_INTERVAL`: streaming chunk interval in ms (default: 100)
