# Tasks: integrate-nanobot-websocket

## 1. Configuration and dependencies

- [ ] 1.1 Add WebSocket gateway config fields to `app/core/config.py`: `WS_NANOBOT_TOKEN`, `WS_NANOBOT_MAX_CONNECTIONS`, `WS_NANOBOT_HEARTBEAT_INTERVAL`, `WS_NANOBOT_AUTH_TIMEOUT`, `WS_NANOBOT_STREAM_CHUNK_INTERVAL`
- [ ] 1.2 Add `LazyRabbitConfig` to nanobot's `config/schema.py`: `enabled`, `ws_url`, `token`, `route_mode`, `route_prefixes`, `allow_from`, `reconnect_max_delay`, `response_timeout`, `show_thinking`
- [ ] 1.3 Verify no new Python dependencies needed (FastAPI has native WebSocket; nanobot uses `websockets` already)

## 2. WebSocket message protocol

- [ ] 2.1 Create `app/schemas/ws_message.py`: `WSMessage` envelope, `WSMessageType` enum, payload schemas for all message types (auth, heartbeat, chat.request, chat.response, chat.stream.*, push.*, system.error)
- [ ] 2.2 Create message serialization/deserialization helpers (JSON ↔ WSMessage)
- [ ] 2.3 Create shared protocol constants (version, timeout defaults, error codes)

## 3. Identity mapping (database)

- [ ] 3.1 Create `app/models/nanobot_identity.py`: `NanobotIdentityMapping` model (id, channel, chat_id, sender_id, user_id FK, display_name, created_at, last_seen_at)
- [ ] 3.2 Create Alembic migration for `nanobot_identity_mapping` table
- [ ] 3.3 Create `app/schemas/nanobot_identity.py`: `IdentityMappingResponse`, `IdentityMappingCreate`
- [ ] 3.4 Register model in `app/db/base.py`

## 4. WebSocket gateway service (lazy-rabbit)

- [ ] 4.1 Create `app/services/ws_gateway/__init__.py`
- [ ] 4.2 Create `app/services/ws_gateway/connection_manager.py`: `ConnectionManager` class — track active connections, broadcast, send to specific connection, enforce max connections
- [ ] 4.3 Create `app/services/ws_gateway/auth.py`: validate `system.auth` message, enforce auth timeout
- [ ] 4.4 Create `app/services/ws_gateway/heartbeat.py`: bidirectional heartbeat loop, dead connection detection
- [ ] 4.5 Create `app/services/ws_gateway/message_handler.py`: parse incoming WSMessage, dispatch to appropriate handler (chat, push_ack, heartbeat)
- [ ] 4.6 Create `app/services/ws_gateway/session_mapper.py`: resolve `(channel, chat_id, sender_id)` → lazy-rabbit user (auto-create if needed), update `last_seen_at`
- [ ] 4.7 Create `app/services/ws_gateway/chat_handler.py`: handle `chat.request` — create/resume session, invoke SecretaryAgent, return `chat.response` or stream `chat.stream.*` events with token chunking
- [ ] 4.8 Create `app/services/ws_gateway/push_service.py`: `PushService` class — `notify(user_id, content, priority)`, resolve nanobot identity, send `push.notification`, handle queue for disconnected clients

## 5. WebSocket endpoint (lazy-rabbit)

- [ ] 5.1 Create `app/api/v1/endpoints/ws_nanobot.py`: FastAPI WebSocket endpoint at `/ws/nanobot`
- [ ] 5.2 Implement connection lifecycle: accept → auth → message loop → cleanup
- [ ] 5.3 Register WebSocket route in `app/api/v1/api.py`
- [ ] 5.4 Initialize WebSocket gateway (ConnectionManager, PushService) in `app/main.py` startup

## 6. Admin endpoints for identity mapping

- [ ] 6.1 Add to `app/api/v1/endpoints/admin.py` (or new file):
  - `GET /admin/nanobot-identities` — list all mappings
  - `POST /admin/nanobot-identities` — manually link identity to existing user
  - `DELETE /admin/nanobot-identities/{id}` — remove mapping
- [ ] 6.2 Require admin role for all identity management endpoints

## 7. nanobot LazyRabbit channel plugin

- [ ] 7.1 Create `nanobot/channels/lazy_rabbit.py`: `LazyRabbitChannel(BaseChannel)` with `start()`, `stop()`, `send()` methods
- [ ] 7.2 Implement WebSocket client connection with auth handshake
- [ ] 7.3 Implement auto-reconnect with exponential backoff (1s → 60s max) and jitter
- [ ] 7.4 Implement heartbeat sender/receiver
- [ ] 7.5 Implement message routing logic (prefix / all / fallback modes)
- [ ] 7.6 Implement response handling: accumulate streaming tokens → send complete message to originating channel
- [ ] 7.7 Implement push notification handling: receive `push.notification` → deliver to target channel → send `push.ack`
- [ ] 7.8 Implement "thinking..." indicator: send typing/processing indicator while waiting for lazy-rabbit response
- [ ] 7.9 Register channel in `nanobot/channels/manager.py`

## 8. Integration wiring

- [ ] 8.1 Wire PushService into existing reminder/scheduled services so they can push via nanobot
- [ ] 8.2 Add `agent` field support in chat handler to allow direct agent routing (bypass supervisor)
- [ ] 8.3 Add WebSocket connection status to health check endpoint (`/health`)

## 9. Tests

- [ ] 9.1 Unit: WSMessage serialization/deserialization (all message types)
- [ ] 9.2 Unit: ConnectionManager (add/remove/broadcast/max connections)
- [ ] 9.3 Unit: SessionMapper (auto-create user, resolve existing, update last_seen)
- [ ] 9.4 Unit: PushService (notify with mapping, notify without mapping, queue when disconnected, expire old)
- [ ] 9.5 Unit: Heartbeat (send/receive, timeout detection)
- [ ] 9.6 Integration: WebSocket endpoint auth flow (success, failure, timeout)
- [ ] 9.7 Integration: End-to-end chat request → response via WebSocket
- [ ] 9.8 Integration: End-to-end streaming chat via WebSocket
- [ ] 9.9 Integration: Push notification delivery and acknowledgment
- [ ] 9.10 nanobot: LazyRabbit channel routing (prefix, all, fallback modes)
- [ ] 9.11 nanobot: Reconnection behavior (disconnect → backoff → reconnect → re-auth)
- [ ] 9.12 nanobot: Response accumulation (streaming tokens → complete message)

## 10. Documentation

- [ ] 10.1 Document WebSocket message protocol (all message types with examples)
- [ ] 10.2 Document nanobot LazyRabbit channel configuration
- [ ] 10.3 Document identity mapping and user linking
- [ ] 10.4 Update lazy-rabbit README with WebSocket gateway section
- [ ] 10.5 Add deployment guide (how to configure both sides)
