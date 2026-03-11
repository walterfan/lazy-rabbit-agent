# Acceptance Test Cases & Metrics: integrate-nanobot-websocket

## Overview

| Category | Test Cases | Priority |
|----------|-----------|----------|
| WebSocket Connection & Auth | TC-WS-001 ~ TC-WS-008 | P0 |
| Chat Request/Response | TC-CR-001 ~ TC-CR-010 | P0 |
| Identity Mapping | TC-IM-001 ~ TC-IM-007 | P0 |
| nanobot Channel Plugin | TC-NB-001 ~ TC-NB-010 | P0 |
| Push Notification Bridge | TC-PN-001 ~ TC-PN-008 | P1 |
| Resilience & Edge Cases | TC-RE-001 ~ TC-RE-008 | P1 |
| Non-Functional / Performance | TC-NF-001 ~ TC-NF-007 | P2 |
| **Total** | **58 test cases** | |

---

## 1. WebSocket Connection & Auth (TC-WS)

### TC-WS-001: Successful connection and authentication
- **Precondition**: lazy-rabbit running with `WS_NANOBOT_TOKEN=test-secret-token`
- **Steps**:
  1. Open WebSocket to `ws://localhost:8000/ws/nanobot`
  2. Send `{"type": "system.auth", "payload": {"token": "test-secret-token", "client_id": "nanobot-1", "version": "1.0"}}`
- **Expected**:
  - Receive `{"type": "system.auth_ok", "payload": {"server_version": "...", "capabilities": [...]}}`
  - Connection remains open
- **Priority**: P0

### TC-WS-002: Authentication with invalid token
- **Steps**:
  1. Connect and send `system.auth` with `token: "wrong-token"`
- **Expected**:
  - Receive `{"type": "system.auth_fail", "payload": {"reason": "..."}}`
  - Connection is closed by server
- **Priority**: P0

### TC-WS-003: Authentication timeout
- **Steps**:
  1. Connect but do NOT send any message
  2. Wait 10+ seconds
- **Expected**:
  - Server closes connection after auth timeout
- **Priority**: P0

### TC-WS-004: Heartbeat exchange
- **Precondition**: Authenticated connection
- **Steps**:
  1. Wait for heartbeat interval (30s) or send `system.heartbeat`
- **Expected**:
  - Receive `system.heartbeat` response
  - Connection remains alive
- **Priority**: P0

### TC-WS-005: Heartbeat timeout triggers disconnect
- **Precondition**: Authenticated connection
- **Steps**:
  1. Send `system.heartbeat`
  2. Simulate server not responding (mock)
  3. Wait 10+ seconds
- **Expected**:
  - Client detects dead connection
- **Priority**: P1

### TC-WS-006: Max connections enforced
- **Precondition**: `WS_NANOBOT_MAX_CONNECTIONS=2`
- **Steps**:
  1. Connect and authenticate client-1 ✓
  2. Connect and authenticate client-2 ✓
  3. Connect and attempt to authenticate client-3
- **Expected**:
  - Client-3 receives `system.auth_fail` with reason "max connections reached"
  - Client-3 connection is closed
  - Client-1 and client-2 remain connected
- **Priority**: P1

### TC-WS-007: Malformed message handling
- **Precondition**: Authenticated connection
- **Steps**:
  1. Send `"not valid json"`
  2. Send `{"type": "unknown.type"}`
  3. Send `{"type": "chat.request"}` (missing payload)
- **Expected**:
  - Each receives `system.error` with descriptive error
  - Connection remains open after each error
- **Priority**: P0

### TC-WS-008: Graceful server shutdown
- **Precondition**: Authenticated connection with active chat
- **Steps**:
  1. Trigger server shutdown (SIGTERM)
- **Expected**:
  - Server sends close frame to all connected clients
  - No data corruption
- **Priority**: P1

---

## 2. Chat Request/Response (TC-CR)

### TC-CR-001: Non-streaming chat — happy path
- **Precondition**: Authenticated connection, user identity mapped
- **Steps**:
  1. Send `{"type": "chat.request", "id": "msg_001", "payload": {"channel": "telegram", "chat_id": "12345", "sender_id": "12345", "message": "今天天气怎么样？"}}`
- **Expected**:
  - Receive `{"type": "chat.response", "correlation_id": "msg_001", "payload": {"channel": "telegram", "chat_id": "12345", "content": "...", "session_id": "..."}}`
  - Content is a meaningful weather-related response
- **Priority**: P0

### TC-CR-002: Streaming chat — token flow
- **Precondition**: Authenticated connection
- **Steps**:
  1. Send `{"type": "chat.request", "id": "msg_002", "payload": {"channel": "feishu", "chat_id": "oc_xxx", "sender_id": "user1", "message": "给我讲个故事", "stream": true}}`
- **Expected**:
  - Receive `chat.stream.start` with `session_id`
  - Receive multiple `chat.stream.token` messages with `content` fragments
  - Receive `chat.stream.done` with `session_id` and `message_id`
  - Concatenated tokens form a coherent story
- **Priority**: P0

### TC-CR-003: Streaming chat with tool calls
- **Precondition**: Authenticated connection
- **Steps**:
  1. Send a chat request that triggers a tool (e.g., "帮我查一下北京的天气", stream: true)
- **Expected**:
  - Receive `chat.stream.tool` with tool name and args
  - Receive `chat.stream.token` messages with the tool-augmented response
  - Receive `chat.stream.done`
- **Priority**: P0

### TC-CR-004: Chat with specific agent routing
- **Precondition**: Authenticated connection
- **Steps**:
  1. Send `chat.request` with `"agent": "philosophy"`
  2. Send `chat.request` with `"agent": "translation"`
- **Expected**:
  - Step 1: Response is in philosophy master style
  - Step 2: Response is a translation
  - Neither goes through supervisor routing
- **Priority**: P1

### TC-CR-005: Chat session continuity across messages
- **Precondition**: Authenticated connection
- **Steps**:
  1. Send chat request: "我叫小明" → get `session_id`
  2. Send chat request with same `session_id`: "我叫什么名字？"
- **Expected**:
  - Step 2 response references "小明" (conversation history preserved)
- **Priority**: P0

### TC-CR-006: Chat session continuity across reconnections
- **Precondition**: Authenticated connection, existing session
- **Steps**:
  1. Send a message, get `session_id`
  2. Disconnect WebSocket
  3. Reconnect and re-authenticate
  4. Send a message with the same `session_id`
- **Expected**:
  - Step 4 response has context from step 1 (session persisted in DB)
- **Priority**: P0

### TC-CR-007: Chat request with empty message
- **Steps**:
  1. Send `chat.request` with `"message": ""`
- **Expected**:
  - Receive `system.error` with validation error
- **Priority**: P0

### TC-CR-008: Concurrent chat requests from different channels
- **Precondition**: Authenticated connection
- **Steps**:
  1. Simultaneously send chat requests from `(telegram, 111)` and `(feishu, oc_222)`
- **Expected**:
  - Both receive correct responses
  - Responses are routed to the correct `(channel, chat_id)` — no cross-contamination
- **Priority**: P0

### TC-CR-009: Chat request during streaming
- **Precondition**: Authenticated connection, one streaming request in progress
- **Steps**:
  1. Send streaming chat request A
  2. While A is streaming, send chat request B (different channel/chat_id)
- **Expected**:
  - Both requests complete independently
  - Responses are correctly correlated via `correlation_id`
- **Priority**: P1

### TC-CR-010: Agent processing error during chat
- **Precondition**: Authenticated connection, LLM service unavailable (mock)
- **Steps**:
  1. Send a chat request
- **Expected**:
  - Receive `chat.stream.error` or `system.error` with meaningful error message
  - Connection remains open
- **Priority**: P0

---

## 3. Identity Mapping (TC-IM)

### TC-IM-001: Auto-create user on first message
- **Precondition**: No existing mapping for `(telegram, 99999, 99999)`
- **Steps**:
  1. Send `chat.request` with `{channel: "telegram", chat_id: "99999", sender_id: "99999", message: "hello"}`
- **Expected**:
  - A new user is created in lazy-rabbit (e.g., `nb_telegram_99999`)
  - An identity mapping record is created
  - The chat request is processed successfully
- **Priority**: P0

### TC-IM-002: Existing mapping resolves correct user
- **Precondition**: Mapping exists: `(telegram, 12345)` → user_id `abc-123`
- **Steps**:
  1. Send `chat.request` from `(telegram, 12345)`
- **Expected**:
  - Request is processed in user `abc-123`'s context
  - No new user created
  - `last_seen_at` is updated
- **Priority**: P0

### TC-IM-003: Multiple channels mapped to same user
- **Precondition**: Admin has linked `(telegram, 111)` and `(feishu, oc_222)` to the same user
- **Steps**:
  1. Send chat from `(telegram, 111)`: "记个笔记：买牛奶"
  2. Send chat from `(feishu, oc_222)`: "列出我的笔记"
- **Expected**:
  - Step 2 response includes "买牛奶" (shared user data)
- **Priority**: P0

### TC-IM-004: Admin lists identity mappings
- **Precondition**: Admin user, multiple mappings exist
- **Steps**:
  1. GET `/api/v1/admin/nanobot-identities`
- **Expected**:
  - HTTP 200 with list of all mappings including channel, chat_id, sender_id, user details, last_seen_at
- **Priority**: P1

### TC-IM-005: Admin manually links identity to existing user
- **Precondition**: Admin user, existing lazy-rabbit user `walter`
- **Steps**:
  1. POST `/api/v1/admin/nanobot-identities` with `{channel: "discord", chat_id: "555", sender_id: "555", user_id: "<walter's id>"}`
- **Expected**:
  - HTTP 201
  - Subsequent messages from `(discord, 555)` are processed as user `walter`
- **Priority**: P1

### TC-IM-006: Admin deletes identity mapping
- **Precondition**: Mapping exists for `(telegram, 12345)`
- **Steps**:
  1. DELETE `/api/v1/admin/nanobot-identities/{mapping_id}`
  2. Send chat from `(telegram, 12345)`
- **Expected**:
  - Step 1: HTTP 200
  - Step 2: A NEW user is auto-created (old mapping gone)
- **Priority**: P1

### TC-IM-007: Identity mapping survives server restart
- **Precondition**: Mapping exists
- **Steps**:
  1. Restart lazy-rabbit server
  2. Send chat from the mapped identity
- **Expected**:
  - Mapping is preserved; same user resolved
- **Priority**: P0

---

## 4. nanobot Channel Plugin (TC-NB)

### TC-NB-001: Channel starts and connects on nanobot startup
- **Precondition**: nanobot config has `lazy_rabbit.enabled: true`, `ws_url: "ws://localhost:8000/ws/nanobot"`, valid token
- **Steps**:
  1. Start nanobot
- **Expected**:
  - LazyRabbit channel connects and authenticates
  - Log shows "LazyRabbit channel connected"
- **Priority**: P0

### TC-NB-002: Channel disabled does not connect
- **Precondition**: `lazy_rabbit.enabled: false`
- **Steps**:
  1. Start nanobot
- **Expected**:
  - No WebSocket connection attempted
  - No errors in logs
- **Priority**: P0

### TC-NB-003: Prefix routing — matching prefix forwarded
- **Precondition**: `route_mode: "prefix"`, `route_prefixes: ["/ask", "/rabbit"]`
- **Steps**:
  1. User sends "/ask what is Python?" on Telegram
- **Expected**:
  - Message (with "/ask " stripped) forwarded to lazy-rabbit
  - Response from lazy-rabbit delivered back to user on Telegram
- **Priority**: P0

### TC-NB-004: Prefix routing — non-matching handled locally
- **Precondition**: Same as TC-NB-003
- **Steps**:
  1. User sends "hello" on Telegram (no matching prefix)
- **Expected**:
  - Message handled by nanobot's own agent (NOT forwarded to lazy-rabbit)
- **Priority**: P0

### TC-NB-005: All routing mode — everything forwarded
- **Precondition**: `route_mode: "all"`
- **Steps**:
  1. User sends any message on any channel
- **Expected**:
  - Message forwarded to lazy-rabbit
  - Response delivered back to user
- **Priority**: P0

### TC-NB-006: Fallback routing mode
- **Precondition**: `route_mode: "fallback"`
- **Steps**:
  1. User sends a message nanobot can handle (e.g., "what time is it?")
  2. User sends a message nanobot cannot handle (e.g., "帮我翻译这段话")
- **Expected**:
  - Step 1: Handled locally by nanobot
  - Step 2: Forwarded to lazy-rabbit
- **Priority**: P1

### TC-NB-007: Streaming response accumulated and delivered
- **Precondition**: Connected, user sends message that triggers streaming
- **Steps**:
  1. User sends "/ask 给我讲个故事" on Feishu
- **Expected**:
  - nanobot accumulates all `chat.stream.token` messages
  - Sends ONE complete message to user on Feishu (not per-token)
- **Priority**: P0

### TC-NB-008: "Thinking..." indicator shown
- **Precondition**: `show_thinking: true`
- **Steps**:
  1. User sends a message that takes >2s to process
- **Expected**:
  - User sees a "thinking..." or typing indicator while waiting
  - Final response replaces/follows the indicator
- **Priority**: P1

### TC-NB-009: Response timeout
- **Precondition**: `response_timeout: 10` (seconds, for testing)
- **Steps**:
  1. Send a message; lazy-rabbit takes >10s to respond (mock)
- **Expected**:
  - nanobot sends a timeout error message to the user
  - Connection remains open
- **Priority**: P1

### TC-NB-010: Tool call indicator
- **Precondition**: Connected
- **Steps**:
  1. User sends a message that triggers a tool call (e.g., weather query)
- **Expected**:
  - User optionally sees "🔧 Using tool: get_weather..." indicator
  - Final response includes tool result
- **Priority**: P2

---

## 5. Push Notification Bridge (TC-PN)

### TC-PN-001: Reminder delivered via nanobot
- **Precondition**: User has nanobot identity mapping (telegram, 12345), reminder set
- **Steps**:
  1. Reminder triggers
- **Expected**:
  - lazy-rabbit sends `push.notification` over WebSocket
  - nanobot delivers message to Telegram chat 12345
  - nanobot sends `push.ack` with `delivered: true`
- **Priority**: P1

### TC-PN-002: Push to preferred channel
- **Precondition**: User has mappings for Telegram and Feishu; Telegram is most recently active
- **Steps**:
  1. Trigger a push notification for the user
- **Expected**:
  - Notification sent to Telegram (most recently active channel)
- **Priority**: P1

### TC-PN-003: Push when nanobot disconnected — queued
- **Precondition**: No active WebSocket connection
- **Steps**:
  1. Trigger a push notification
  2. Reconnect nanobot
- **Expected**:
  - Step 1: Notification queued (not lost)
  - Step 2: Queued notification delivered after reconnection
- **Priority**: P1

### TC-PN-004: Queued notifications expire after 24h
- **Precondition**: Notification queued, nanobot disconnected for >24h
- **Steps**:
  1. Reconnect nanobot after 24+ hours
- **Expected**:
  - Expired notifications are NOT delivered
- **Priority**: P2

### TC-PN-005: Push ack — failed delivery
- **Precondition**: Target channel unavailable (e.g., user blocked bot)
- **Steps**:
  1. Trigger push notification
- **Expected**:
  - nanobot sends `push.ack` with `delivered: false, reason: "..."`
  - lazy-rabbit logs the failure
- **Priority**: P1

### TC-PN-006: PushService API — notify with mapping
- **Precondition**: User has nanobot identity mapping
- **Steps**:
  1. Call `push_service.notify(user_id=..., content="Test notification")`
- **Expected**:
  - Returns `True`
  - Notification delivered to user's channel
- **Priority**: P1

### TC-PN-007: PushService API — notify without mapping
- **Precondition**: User has NO nanobot identity mapping
- **Steps**:
  1. Call `push_service.notify(user_id=..., content="Test")`
- **Expected**:
  - Returns `False`
  - No error raised
- **Priority**: P1

### TC-PN-008: Push notification with markdown content
- **Steps**:
  1. Send push with markdown content: `"**Reminder**: Study _Python_ for 30 min"`
- **Expected**:
  - nanobot converts markdown to platform-appropriate format before delivery
- **Priority**: P2

---

## 6. Resilience & Edge Cases (TC-RE)

### TC-RE-001: nanobot auto-reconnect after server restart
- **Steps**:
  1. Establish connection
  2. Restart lazy-rabbit server
  3. Wait for nanobot to reconnect
- **Expected**:
  - nanobot detects disconnection
  - Reconnects with exponential backoff
  - Re-authenticates successfully
  - Subsequent messages work normally
- **Priority**: P0

### TC-RE-002: Exponential backoff timing
- **Steps**:
  1. Make lazy-rabbit unreachable
  2. Observe nanobot reconnection attempts
- **Expected**:
  - Attempts at ~1s, ~2s, ~4s, ~8s, ~16s, ~32s, ~60s (capped)
  - Jitter of ±20% on each delay
- **Priority**: P1

### TC-RE-003: Backoff resets after successful reconnect
- **Steps**:
  1. Trigger multiple failed reconnection attempts (backoff grows)
  2. Make lazy-rabbit reachable again
  3. After successful reconnect, disconnect again
- **Expected**:
  - Step 3: Backoff starts from 1s again (not from previous high value)
- **Priority**: P1

### TC-RE-004: Large message handling
- **Steps**:
  1. Send a chat request with a very long message (10,000 chars)
- **Expected**:
  - Message is processed (possibly truncated by agent)
  - No WebSocket frame errors
- **Priority**: P1

### TC-RE-005: Rapid-fire messages
- **Steps**:
  1. Send 20 chat requests in quick succession from different chat_ids
- **Expected**:
  - All 20 receive responses
  - No messages lost or mixed up
  - Responses correctly correlated
- **Priority**: P1

### TC-RE-006: nanobot graceful shutdown
- **Steps**:
  1. Active connection with pending requests
  2. Stop nanobot (SIGTERM)
- **Expected**:
  - WebSocket closed cleanly
  - No data corruption
  - Pending responses discarded gracefully
- **Priority**: P1

### TC-RE-007: lazy-rabbit at capacity
- **Precondition**: lazy-rabbit under heavy load
- **Steps**:
  1. Send chat request via WebSocket
- **Expected**:
  - Response may be slow but eventually arrives
  - No connection drop due to slow processing
  - Timeout handled gracefully if exceeded
- **Priority**: P2

### TC-RE-008: Network partition simulation
- **Steps**:
  1. Establish connection
  2. Simulate network partition (drop packets, don't close socket)
  3. Wait for heartbeat timeout
- **Expected**:
  - Both sides detect dead connection via heartbeat timeout
  - nanobot begins reconnection
- **Priority**: P2

---

## 7. Non-Functional / Performance (TC-NF)

### TC-NF-001: WebSocket connection establishment latency
- **Steps**:
  1. Measure time from `connect()` to receiving `system.auth_ok`
- **Expected**: ≤ 500ms on localhost, ≤ 2s over network
- **Priority**: P2

### TC-NF-002: Chat request round-trip latency (non-streaming)
- **Steps**:
  1. Send `chat.request`, measure time to `chat.response`
- **Expected**: ≤ LLM latency + 500ms overhead (WebSocket + routing + session mapping)
- **Priority**: P2

### TC-NF-003: Streaming first token latency
- **Steps**:
  1. Send streaming `chat.request`, measure time to first `chat.stream.token`
- **Expected**: ≤ LLM first-token latency + 500ms overhead
- **Priority**: P2

### TC-NF-004: End-to-end latency (user → Telegram → nanobot → LR → nanobot → Telegram → user)
- **Steps**:
  1. User sends message on Telegram, measure time to response delivery
- **Expected**: ≤ LLM latency + 3s total overhead (Telegram API + nanobot + WebSocket + LR + return path)
- **Priority**: P2

### TC-NF-005: Memory usage — WebSocket gateway
- **Steps**:
  1. Measure lazy-rabbit memory with 0 WebSocket connections
  2. Measure with 5 active connections, each with 10 concurrent chats
- **Expected**: ≤ +50MB per connection
- **Priority**: P2

### TC-NF-006: Database migration — non-destructive
- **Steps**:
  1. Run `alembic upgrade head` on existing database
  2. Verify existing tables and data intact
  3. Verify `nanobot_identity_mapping` table created
- **Expected**: Zero data loss; migration is additive only
- **Priority**: P0

### TC-NF-007: WebSocket message throughput
- **Steps**:
  1. Send 100 chat requests in 10 seconds via WebSocket
- **Expected**:
  - All 100 accepted (no dropped messages)
  - All 100 eventually receive responses
  - No WebSocket errors
- **Priority**: P2

---

## Acceptance Metrics

### Coverage Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Unit test coverage (new code) | ≥ 80% | `pytest --cov` on new modules (ws_gateway/, lazy_rabbit.py) |
| WebSocket message type coverage | 100% | Every message type in protocol has ≥ 1 test |
| Spec scenario coverage | 100% | Every scenario in specs/ maps to ≥ 1 test case |
| P0 test pass rate | 100% | All P0 tests must pass before merge |
| P1 test pass rate | ≥ 90% | At most 2 P1 tests may be deferred |

### Quality Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Message correlation accuracy | 100% | No response delivered to wrong channel/chat_id (TC-CR-008) |
| Identity mapping correctness | 100% | Auto-created users are unique; existing mappings resolve correctly |
| Reconnection success rate | 100% | After server restart, nanobot reconnects within 2 minutes |
| Push delivery rate | ≥ 95% | Of notifications sent when nanobot is connected, ≥ 95% get `delivered: true` ack |
| Protocol compliance | 100% | All messages follow the defined JSON envelope schema |

### Performance Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| WS connection + auth | ≤ 500ms (localhost) | TC-NF-001 |
| Chat round-trip overhead | ≤ 500ms (above LLM latency) | TC-NF-002 |
| Streaming first-token overhead | ≤ 500ms (above LLM latency) | TC-NF-003 |
| End-to-end (Telegram → LR → Telegram) | ≤ LLM + 3s | TC-NF-004 |
| Memory per WS connection | ≤ 50MB | TC-NF-005 |
| Message throughput | ≥ 10 req/s sustained | TC-NF-007 |

### Resilience Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Auto-reconnect time (server restart) | ≤ 2 minutes | TC-RE-001 |
| Zero message loss on reconnect | 0 lost | Queued messages delivered after reconnect |
| Graceful degradation | nanobot functional | When LR is down, nanobot handles local requests normally |
| Heartbeat detection time | ≤ 40s | 30s interval + 10s timeout |

### Regression Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Existing test suite | 100% pass | `pytest` — all pre-existing tests still pass |
| REST API unaffected | No degradation | All existing REST endpoints work identically |
| nanobot other channels | No degradation | Telegram, Feishu, etc. work normally with LazyRabbit channel enabled |
| API startup time | ≤ +1s increase | WebSocket gateway initialization overhead |

### Definition of Done

- [ ] All P0 test cases (30 cases) pass
- [ ] ≥ 90% of P1 test cases (19 cases) pass
- [ ] Unit test coverage ≥ 80% on new modules
- [ ] WebSocket endpoint accepts connections and authenticates
- [ ] Full chat round-trip works: user → nanobot channel → WS → lazy-rabbit agent → WS → nanobot → user
- [ ] Streaming chat works end-to-end (tokens accumulated, single message delivered)
- [ ] Identity mapping auto-creates users on first contact
- [ ] Push notifications delivered from lazy-rabbit agents to nanobot channels
- [ ] Auto-reconnect works after server restart (within 2 minutes)
- [ ] Heartbeat keeps connection alive; dead connections detected
- [ ] Admin can list/create/delete identity mappings
- [ ] Existing REST API and nanobot channels unaffected (zero regressions)
- [ ] Database migration is non-destructive
- [ ] Protocol documented with message type examples
- [ ] Deployment guide covers both-side configuration
