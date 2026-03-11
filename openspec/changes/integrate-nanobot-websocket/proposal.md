## Why

**Goal:** Let applications like lazy-rabbit-agent talk with **nanobot** the same way users talk via Feishu, Telegram, Discord, etc. Lazy-rabbit-agent is one example; other apps may have the same need to be reachable from messaging platforms without building their own channel integrations.

**nanobot** is a multi-channel AI assistant (Feishu, Telegram, Discord, WhatsApp, DingTalk, Matrix, etc.) but has no standard way to delegate requests to external AI applications and route responses back. The change to **nanobot is generic**: it must support *any* external app that implements the protocol, not only lazy-rabbit-agent.

Two sides of the same integration:

1. **nanobot** — Add a generic outbound WebSocket protocol and dispatcher so *any* external AI application can register as a backend, receive messages from nanobot’s channels, and stream responses back. Lazy-rabbit-agent is the first consumer; the interface is application-agnostic for other apps with similar requirements.
2. **lazy-rabbit-agent** — Implement the protocol as a **WebSocket server** so nanobot can connect and forward messages; its agents (secretary, philosophy master, medical paper, translation) then become reachable from Feishu and other channels.

## What Changes

### nanobot (protocol owner — generic, not only for lazy-rabbit-agent)
- Define a **generic external-agent WebSocket protocol**: a JSON message schema for forwarding user messages to external agents and receiving responses (text, streaming tokens, metadata). Reusable by lazy-rabbit-agent and any other app with the same integration need.
- Add an **external-agent dispatcher** (WebSocket client): when a user message matches configured routing rules, connect to the registered external agent’s WebSocket endpoint and forward the message there
- Add **connection lifecycle management**: authentication (shared token or JWT), heartbeat/ping-pong, auto-reconnect with backoff
- Add **multi-agent support**: multiple external agents can register concurrently; routing rules determine which agent handles which messages
- Protocol is **application-neutral** — any app implementing the message contract can connect; lazy-rabbit-agent is one example consumer

### lazy-rabbit-agent (first consumer — example implementation)
- Add a **WebSocket server** that exposes an endpoint for nanobot to connect to, using the defined protocol
- Implement **message dispatch**: accept connections from nanobot, receive forwarded user messages, route to the appropriate internal agent (secretary, translation, philosophy, etc.), and stream the response back
- Add **session mapping**: map nanobot `channel:chat_id` identifiers to lazy-rabbit user sessions
- Add **push notification support**: allow lazy-rabbit agents to proactively send messages over the WebSocket connection to users on their preferred channel

## Capabilities

### New Capabilities

- `nanobot-external-agent-protocol`: A generic, versioned WebSocket message protocol on nanobot that allows *any* external AI application to register as a backend agent, receive forwarded user messages, and stream responses back. The change to nanobot is not only for lazy-rabbit-agent; other apps may integrate the same way.
- `websocket-agent-server`: Lazy-rabbit-agent’s WebSocket server (example implementation) that implements the nanobot external-agent protocol, listens for connections from nanobot, and dispatches incoming requests to internal agents.
- `cross-platform-agent-access`: Users on any nanobot-supported platform (Telegram, Feishu, Discord, etc.) can interact with lazy-rabbit's specialized agents (secretary, philosophy, medical paper, translation).
- `push-notification-bridge`: Lazy-rabbit agents can push notifications (reminders, scheduled reports, alerts) through nanobot to users on their preferred messaging platform.

### Modified Capabilities

- `secretary-agent`: Can now receive requests from and send responses to nanobot-connected channels (in addition to the web frontend).

## Impact

- **nanobot**
  - `nanobot/protocols/external_agent.py` — Generic external-agent WebSocket protocol definition (message schema, event types, versioning)
  - `nanobot/dispatcher/external_agent_dispatcher.py` — Routes messages to registered external agents via WebSocket
  - `nanobot/config/schema.py` — `ExternalAgentConfig` class (endpoint URL, token, routing rules) — app-neutral, usable for any external agent
  - Registration hooks in nanobot's channel/dispatcher manager

- **lazy-rabbit-agent Backend**
  - `app/services/nanobot_agent_server/` — New module: WebSocket server (accept connections from nanobot), message handler, session mapper, push service
  - `app/schemas/nanobot_message.py` — Message schemas matching nanobot's external-agent protocol
  - `app/core/config.py` — WebSocket server config for nanobot (listen path, token, heartbeat interval)
  - `app/main.py` — Start/stop WebSocket server for nanobot connections on app lifecycle

- **Dependencies**
  - lazy-rabbit: FastAPI’s native WebSocket support (server side)
  - nanobot: WebSocket client to connect to external agent endpoints (e.g. `websockets` or stdlib)
