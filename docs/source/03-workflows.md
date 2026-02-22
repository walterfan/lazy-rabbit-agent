# Business workflows

## Workflow: Secretary chat

### Overview

User sends a message in a session; supervisor routes to a sub-agent; sub-agent may call tools; response is streamed back.

### Sequence (Mermaid)

```{mermaid}
sequenceDiagram
  participant Client
  participant API as Secretary API
  participant Chat as chat_service
  participant Agent as SecretaryAgent
  participant Supervisor as Supervisor
  participant Sub as SubAgent
  participant Tools as Tools

  Client->>API: POST /secretary/sessions/{id}/messages
  API->>Chat: append message, get history
  Chat->>Agent: chat_stream(messages)
  loop LangGraph
    Agent->>Supervisor: route(user message)
    Supervisor->>Supervisor: RoutingDecision
    Supervisor->>Sub: invoke sub-agent
    Sub->>Tools: tool calls (optional)
    Tools-->>Sub: tool results
    Sub-->>Supervisor: response
    Supervisor-->>Agent: next or FINISH
  end
  Agent-->>Chat: stream chunks
  Chat-->>API: SSE stream
  API-->>Client: streamed response
```

### Steps

1. Client POSTs message to `/api/v1/secretary/sessions/{session_id}/messages` (or creates session).
2. Backend loads session history, appends user message.
3. SecretaryAgent runs LangGraph: supervisor node chooses Learning / Productivity / Utility or FINISH.
4. Sub-agent runs (ReACT/tools as needed); may loop back to supervisor.
5. Assistant message streamed to client; message and tool calls persisted.

### Input/Output

- **Input**: Session ID, message content, auth token.
- **Output**: Streamed SSE (or JSON) with assistant content and optional tool-use indicators.

### Code entry points

- `backend/app/api/v1/endpoints/secretary.py` (route handlers)
- `backend/app/services/secretary_agent/agent.py` (`SecretaryAgent.chat_stream`, supervisor node, sub-agent invocations)

---

## Workflow: Learning record save

### Overview

User asks to learn a word/sentence/topic/article; agent uses tools; user confirms save; record is written to `learning_records`.

### Flow (Mermaid)

```{mermaid}
flowchart LR
  A[User: learn word X] --> B[Secretary routes to Learning]
  B --> C[learn_word tool]
  C --> D[LLM: explanation + IPA + examples]
  D --> E[User: save]
  E --> F[save_learning tool]
  F --> G[learning_service]
  G --> H[(learning_records)]
```

### Steps

1. User message triggers Learning sub-agent; tool (e.g. `learn_word`, `save_learning`) invoked.
2. On user confirmation, save tool persists to DB via learning service.
3. List/search/delete via `/api/v1/learning/*`.

### Code entry points

- `backend/app/services/secretary_agent/sub_agents/learning.py`
- `backend/app/services/secretary_agent/tools/save_learning_tool.py`
- `backend/app/api/v1/endpoints/learning.py`
