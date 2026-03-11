## ADDED Requirements

### Requirement: nanobot has a LazyRabbit channel plugin

nanobot SHALL have a new channel plugin (`lazy_rabbit.py`) that extends `BaseChannel` and connects to lazy-rabbit's WebSocket endpoint.

#### Scenario: Channel starts and connects

- **WHEN** nanobot starts with `lazy_rabbit.enabled: true` in config
- **THEN** the LazyRabbit channel connects to the configured WebSocket URL
- **AND** authenticates with the configured token
- **AND** logs a successful connection message

#### Scenario: Channel disabled

- **WHEN** `lazy_rabbit.enabled: false` in config
- **THEN** the LazyRabbit channel is not started and no connection is attempted

#### Scenario: Connection failure on startup

- **WHEN** the LazyRabbit channel cannot connect to the WebSocket URL
- **THEN** it logs a warning and begins reconnection attempts
- **AND** nanobot continues to function with other channels

### Requirement: LazyRabbit channel supports auto-reconnect

The channel SHALL automatically reconnect with exponential backoff when the connection is lost.

#### Scenario: Connection drops and recovers

- **WHEN** the WebSocket connection is unexpectedly closed
- **THEN** the channel attempts to reconnect after 1 second
- **AND** doubles the delay on each subsequent failure (1s → 2s → 4s → ... → 60s max)
- **AND** adds random jitter (±20%) to avoid thundering herd

#### Scenario: Reconnection succeeds

- **WHEN** the channel successfully reconnects
- **THEN** the backoff delay resets to 1 second
- **AND** the channel re-authenticates and resumes normal operation

### Requirement: LazyRabbit channel forwards messages based on routing mode

The channel SHALL support configurable routing modes to determine which messages are forwarded to lazy-rabbit.

#### Scenario: Prefix routing mode

- **GIVEN** `route_mode: "prefix"` and `route_prefixes: ["/ask", "/secretary", "/learn"]`
- **WHEN** a user sends "/ask what is Python?"
- **THEN** the message (with prefix stripped) is forwarded to lazy-rabbit
- **WHEN** a user sends "hello" (no matching prefix)
- **THEN** the message is handled by nanobot locally (not forwarded)

#### Scenario: All routing mode

- **GIVEN** `route_mode: "all"`
- **WHEN** any user message arrives on any nanobot channel
- **THEN** the message is forwarded to lazy-rabbit

#### Scenario: Fallback routing mode

- **GIVEN** `route_mode: "fallback"`
- **WHEN** a user message arrives
- **THEN** nanobot attempts to handle it locally first
- **AND** if nanobot's agent cannot produce a meaningful response, the message is forwarded to lazy-rabbit

### Requirement: LazyRabbit channel relays responses to originating channel

The channel SHALL receive responses from lazy-rabbit and deliver them to the user on their originating chat platform.

#### Scenario: Complete response relayed

- **WHEN** lazy-rabbit sends a `chat.response` with `{channel: "telegram", chat_id: "12345", content: "..."}`
- **THEN** nanobot delivers the content to Telegram chat 12345

#### Scenario: Streaming response accumulated and sent

- **WHEN** lazy-rabbit sends `chat.stream.start` → multiple `chat.stream.token` → `chat.stream.done`
- **THEN** nanobot accumulates all tokens into a complete message
- **AND** sends the complete message to the originating channel

#### Scenario: Streaming with tool calls

- **WHEN** lazy-rabbit sends `chat.stream.tool` events during streaming
- **THEN** nanobot optionally sends a "🔧 Using tool: {tool_name}..." indicator to the user
- **AND** includes the final response after tool execution

### Requirement: LazyRabbit channel handles push notifications

The channel SHALL receive push notifications from lazy-rabbit and deliver them to the specified user/channel.

#### Scenario: Reminder notification delivered

- **WHEN** lazy-rabbit sends a `push.notification` with `{channel: "feishu", chat_id: "oc_xxx", content: "Time to study!"}`
- **THEN** nanobot delivers the message to the specified Feishu chat
- **AND** sends a `push.ack` back to lazy-rabbit with `delivered: true`

#### Scenario: Push to unavailable channel

- **WHEN** lazy-rabbit sends a push notification for a channel that is not enabled in nanobot
- **THEN** nanobot sends a `push.ack` with `delivered: false` and a reason

### Requirement: LazyRabbit channel has proper configuration

The channel SHALL be configurable via nanobot's config file.

#### Scenario: Configuration fields

- **GIVEN** nanobot's configuration
- **THEN** the `lazy_rabbit` section supports:
  - `enabled`: boolean (default: false)
  - `ws_url`: WebSocket URL (e.g., `ws://localhost:8000/ws/nanobot`)
  - `token`: shared authentication token
  - `route_mode`: `"prefix" | "all" | "fallback"` (default: `"prefix"`)
  - `route_prefixes`: list of command prefixes (default: `["/ask", "/rabbit"]`)
  - `allow_from`: list of allowed nanobot channel:chat_id patterns
  - `reconnect_max_delay`: max reconnect delay in seconds (default: 60)
  - `response_timeout`: max wait for lazy-rabbit response in seconds (default: 120)
  - `show_thinking`: show "thinking..." indicator while waiting (default: true)
