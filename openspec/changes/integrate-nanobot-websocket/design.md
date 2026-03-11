## Context

- **lazy-rabbit-agent**: FastAPI backend with multi-agent supervisor (LangGraph), JWT auth, SSE streaming, sync SQLAlchemy. Exposes REST API consumed by Vue 3 frontend. Has an A2A message contract for inter-agent communication.
- **nanobot**: Multi-channel AI assistant with plugin-based channel architecture (`BaseChannel` → `start()/stop()/send()`). Connects to Telegram, Feishu, Discord, WhatsApp, DingTalk, Matrix, Mochat via WebSocket/polling. Uses a `MessageBus` with `InboundMessage`/`OutboundMessage` events. Each channel has a config class and `allow_from` access control.
- **Goal**: Connect the two systems over WebSocket so nanobot acts as a multi-channel gateway for lazy-rabbit's agents.

## Goals / Non-Goals

**Goals:**

- Establish a persistent WebSocket connection between nanobot (client) and lazy-rabbit (server)
- Route user messages from any nanobot channel to lazy-rabbit's agents
- Stream lazy-rabbit responses back to users on their originating platform
- Support push notifications from lazy-rabbit to nanobot (reminders, alerts)
- Authenticate the WebSocket connection (shared token or JWT)
- Handle reconnection, heartbeat, and graceful degradation
- Map nanobot `channel:chat_id` identities to lazy-rabbit user accounts

**Non-Goals:**

- Replacing lazy-rabbit's web frontend (it continues to work independently)
- Making nanobot a full lazy-rabbit client (only agent chat + push; no CRUD for users/admin)
- Multi-tenant: one nanobot instance connects to one lazy-rabbit instance (v1)
- End-to-end encryption on the WebSocket (rely on TLS/WSS)
- Migrating nanobot's own capabilities (tools, skills, memory) into lazy-rabbit

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│  User Devices                                                    │
│  Telegram │ Feishu │ Discord │ WhatsApp │ DingTalk │ Matrix │... │
└─────┬─────┴───┬────┴────┬────┴─────┬────┴─────┬────┴───┬────────┘
      │         │         │          │          │        │
      ▼         ▼         ▼          ▼          ▼        ▼
┌──────────────────────────────────────────────────────────────────┐
│  nanobot                                                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐   │
│  │ Telegram │ │  Feishu  │ │ Discord  │ │  ... channels    │   │
│  │ Channel  │ │ Channel  │ │ Channel  │ │                  │   │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────────┬─────────┘   │
│       │             │            │                 │              │
│       ▼             ▼            ▼                 ▼              │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  MessageBus (InboundMessage → Agent → OutboundMessage)   │   │
│  └──────────────────────────┬───────────────────────────────┘   │
│                             │                                    │
│                    ┌────────▼─────────┐                         │
│                    │  LazyRabbit      │  ← NEW channel plugin   │
│                    │  Channel         │                         │
│                    │  (WS client)     │                         │
│                    └────────┬─────────┘                         │
└─────────────────────────────┼────────────────────────────────────┘
                              │ WSS
                              │ JSON messages
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  lazy-rabbit-agent                                               │
│                                                                  │
│  ┌──────────────────────┐                                       │
│  │  WebSocket Gateway   │  ← NEW endpoint /ws/nanobot           │
│  │  ┌────────────────┐  │                                       │
│  │  │ ConnectionMgr  │  │  Auth, heartbeat, reconnect           │
│  │  │ MessageHandler │  │  Parse/dispatch WS messages           │
│  │  │ SessionMapper  │  │  nanobot identity → LR user           │
│  │  │ PushService    │  │  Agent → nanobot outbound             │
│  │  └────────────────┘  │                                       │
│  └──────────┬───────────┘                                       │
│             │                                                    │
│             ▼                                                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  SecretaryAgent (Supervisor)                              │   │
│  │  ┌──────────┐ ┌────────────┐ ┌──────────┐ ┌──────────┐  │   │
│  │  │ Learning │ │Productivity│ │ Utility  │ │Philosophy│  │   │
│  │  │  Agent   │ │   Agent    │ │  Agent   │ │  Master  │  │   │
│  │  └──────────┘ └────────────┘ └──────────┘ └──────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

## WebSocket Message Protocol

Based on the existing A2A contract, all messages are JSON with a common envelope:

```json
{
  "type": "chat.request | chat.response | chat.stream | push.notification | system.heartbeat | system.auth | system.error",
  "id": "msg_xxxxxxxxxxxx",
  "correlation_id": "optional trace id",
  "timestamp": "2026-03-05T12:00:00Z",
  "payload": { ... }
}
```

### Message Types

| Type | Direction | Payload | Description |
|------|-----------|---------|-------------|
| `system.auth` | nanobot → LR | `{token, client_id, version}` | First message after connect; authenticates the connection |
| `system.auth_ok` | LR → nanobot | `{server_version, capabilities}` | Auth success |
| `system.auth_fail` | LR → nanobot | `{reason}` | Auth failure; server closes connection |
| `system.heartbeat` | bidirectional | `{ts}` | Keep-alive ping/pong |
| `system.error` | LR → nanobot | `{code, message, correlation_id}` | Error response |
| `chat.request` | nanobot → LR | `{channel, chat_id, sender_id, message, session_id?, agent?}` | User message forwarded from a chat platform |
| `chat.response` | LR → nanobot | `{channel, chat_id, content, session_id, tool_calls?}` | Complete (non-streaming) response |
| `chat.stream.start` | LR → nanobot | `{channel, chat_id, session_id}` | Streaming begins |
| `chat.stream.token` | LR → nanobot | `{channel, chat_id, content}` | Streaming token |
| `chat.stream.tool` | LR → nanobot | `{channel, chat_id, tool, args, result?}` | Tool call during streaming |
| `chat.stream.done` | LR → nanobot | `{channel, chat_id, session_id, message_id}` | Streaming complete |
| `chat.stream.error` | LR → nanobot | `{channel, chat_id, error}` | Streaming error |
| `push.notification` | LR → nanobot | `{channel, chat_id, content, media?, priority?}` | Proactive push (reminder, alert) |
| `push.ack` | nanobot → LR | `{notification_id, delivered}` | Delivery acknowledgment |

## Decisions

### 1. WebSocket (not HTTP webhooks) for the integration

- **Decision**: Use a persistent WebSocket connection from nanobot to lazy-rabbit.
- **Rationale**: Enables real-time bidirectional communication. Streaming tokens can flow naturally. Push notifications don't require nanobot to expose a public endpoint. Lower latency than polling.
- **Alternative rejected**: HTTP webhooks — would require nanobot to expose a public URL, doesn't support streaming well, higher latency for push.

### 2. nanobot as WebSocket client, lazy-rabbit as server

- **Decision**: lazy-rabbit hosts the WebSocket endpoint; nanobot connects as a client.
- **Rationale**: lazy-rabbit is the "brain" with agents and data. nanobot is the "gateway" that connects to it. This matches the existing pattern where nanobot channels connect outward. lazy-rabbit already runs FastAPI which has native WebSocket support.
- **Alternative rejected**: nanobot as server — would require lazy-rabbit to know nanobot's address, complicates deployment.

### 3. LazyRabbit as a nanobot channel plugin (not middleware)

- **Decision**: Implement the integration as a new nanobot channel (`lazy_rabbit.py`) that extends `BaseChannel`.
- **Rationale**: Fits nanobot's plugin architecture perfectly. The channel receives `OutboundMessage` from the bus (agent responses to forward) and publishes `InboundMessage` (lazy-rabbit responses to deliver). Reuses existing `allow_from`, `start/stop/send` lifecycle.
- **Nuance**: This channel is special — it's both a "source" (receives push notifications from LR) and a "sink" (forwards user messages to LR). The nanobot agent layer decides whether to handle a message locally or forward to lazy-rabbit based on routing rules.

### 4. Identity mapping: nanobot channel:chat_id → lazy-rabbit user

- **Decision**: Maintain a mapping table in lazy-rabbit that associates `(nanobot_channel, nanobot_chat_id)` → `lazy_rabbit_user_id`. First interaction triggers a registration/linking flow.
- **Options for linking**:
  - **Auto-create**: First message from an unknown nanobot identity auto-creates a lazy-rabbit user (simplest, chosen for v1)
  - **Link code**: User generates a link code in lazy-rabbit web UI, sends it via nanobot to bind accounts (v2)
  - **Shared auth**: nanobot passes through platform-specific user IDs that lazy-rabbit recognizes (complex, deferred)
- **Storage**: New `nanobot_identity_mapping` table: `(channel, chat_id, sender_id, user_id, created_at)`

### 5. Streaming: buffer tokens and send as chunks (not per-token)

- **Decision**: lazy-rabbit buffers streaming tokens and sends them in chunks (every 100ms or 50 chars, whichever comes first) rather than per-token.
- **Rationale**: Per-token WebSocket messages would be extremely chatty. Chat platforms have rate limits and don't render character-by-character anyway. Chunking reduces message count by ~10x while maintaining perceived real-time feel.
- **Final delivery**: nanobot accumulates all chunks and sends the complete response as a single message to the chat platform (most platforms don't support streaming).

### 6. Authentication: shared token (v1), JWT exchange (v2)

- **Decision**: v1 uses a pre-shared token configured in both nanobot and lazy-rabbit. nanobot sends it in the `system.auth` message after connecting.
- **Rationale**: Simple, sufficient for single-instance deployment. JWT exchange adds complexity without benefit when there's one nanobot per lazy-rabbit.
- **Config**: `WS_NANOBOT_TOKEN` in lazy-rabbit, `token` in nanobot's `LazyRabbitConfig`.

### 7. Reconnection with exponential backoff

- **Decision**: nanobot's LazyRabbit channel implements auto-reconnect with exponential backoff (1s → 2s → 4s → ... → 60s max) and jitter.
- **Rationale**: Network interruptions are inevitable. The channel should be self-healing without manual intervention.
- **Heartbeat**: Bidirectional ping every 30s. If no pong received within 10s, consider connection dead and reconnect.

### 8. Agent routing: configurable intent prefixes

- **Decision**: nanobot's message bus routes messages to lazy-rabbit based on configurable prefix patterns (e.g., `/ask`, `/secretary`, `/learn`, `/philosophy`) or a catch-all mode where ALL messages go to lazy-rabbit.
- **Rationale**: Users may want nanobot to handle some things locally (weather, reminders, memory) and forward others to lazy-rabbit. Prefix-based routing is simple and explicit.
- **Config**: `route_mode: "prefix" | "all" | "fallback"` in `LazyRabbitConfig`.
  - `prefix`: Only messages starting with configured prefixes are forwarded
  - `all`: All messages forwarded to lazy-rabbit (nanobot becomes pure gateway)
  - `fallback`: Try nanobot first; if it can't handle, forward to lazy-rabbit

## Risks / Trade-offs

- **[Risk] Single point of failure**: If WebSocket drops, nanobot users lose access to lazy-rabbit agents → **Mitigation**: Auto-reconnect + graceful degradation (nanobot handles what it can locally, queues messages for lazy-rabbit)
- **[Risk] Message ordering**: Concurrent requests from multiple channels may arrive out of order → **Mitigation**: Each message has `id` and `correlation_id`; lazy-rabbit processes per-session sequentially
- **[Risk] Identity mapping complexity**: Auto-created users may accumulate → **Mitigation**: Admin API to list/delete nanobot-linked users; rate limiting on auto-creation
- **[Trade-off] Chunked streaming vs. per-token**: Loses true character-by-character streaming → **Acceptable**: Chat platforms don't support it anyway; final message is complete
- **[Trade-off] Shared token auth is simple but not rotatable without restart** → **Acceptable for v1**: Single-instance deployment; JWT exchange planned for v2

## Open Questions

1. Should nanobot forward media (images, files) to lazy-rabbit, or only text? → **Recommendation**: Text only in v1; media forwarding in v2 (requires lazy-rabbit to handle multimodal input).
2. Should lazy-rabbit support multiple concurrent nanobot connections? → **Recommendation**: Yes, design for it (connection manager handles N connections), but v1 tested with 1.
3. How should nanobot handle lazy-rabbit being slow (>30s response)? → **Recommendation**: Send a "thinking..." indicator to the user, with a 120s timeout.
4. Should the push notification bridge support rich formatting (markdown, buttons)? → **Recommendation**: Markdown in v1; platform-specific rich elements in v2.
