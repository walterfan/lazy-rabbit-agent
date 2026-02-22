# Personal Secretary Agent - Architecture

## Overview

The Personal Secretary is an AI-powered assistant that helps users:
- Learn English (words, sentences)
- Learn new tech topics
- Answer questions and plan ideas
- Manage daily tasks with utility tools

## System Architecture

```mermaid
flowchart TB
    subgraph Frontend["Frontend (Vue.js)"]
        Chat[Chat UI]
        Learning[Learning History]
        Session[Session List]
    end
    
    subgraph API["Backend API (FastAPI)"]
        ChatAPI["/secretary/chat"]
        StreamAPI["/secretary/chat/stream"]
        LearningAPI["/learning/*"]
        MetricsAPI["/api/metrics"]
    end
    
    subgraph Agent["Secretary Agent (LangChain)"]
        AgentCore[Agent Executor]
        ToolRegistry[Tool Registry]
        PromptLoader[Prompt Loader]
    end
    
    subgraph Tools["Tools"]
        subgraph LearningTools["Learning Tools"]
            LearnWord[learn_word]
            LearnSentence[learn_sentence]
            LearnTopic[learn_topic]
            AnswerQ[answer_question]
            PlanIdea[plan_idea]
        end
        subgraph UtilityTools["Utility Tools"]
            Weather[get_weather]
            Calculator[calculate]
            DateTime[get_datetime]
        end
    end
    
    subgraph External["External Services"]
        LLM[LLM API]
        WeatherAPI[Weather API]
    end
    
    subgraph Storage["Data Storage"]
        DB[(PostgreSQL)]
        Sessions[chat_sessions]
        Messages[chat_messages]
        Records[learning_records]
    end
    
    Chat --> ChatAPI
    Chat --> StreamAPI
    Learning --> LearningAPI
    Session --> ChatAPI
    
    ChatAPI --> AgentCore
    StreamAPI --> AgentCore
    
    AgentCore --> ToolRegistry
    AgentCore --> PromptLoader
    AgentCore --> LLM
    
    ToolRegistry --> LearningTools
    ToolRegistry --> UtilityTools
    
    Weather --> WeatherAPI
    
    ChatAPI --> Sessions
    ChatAPI --> Messages
    LearningAPI --> Records
    
    MetricsAPI --> Prometheus[Prometheus]
```

## Data Flow

### Chat Request Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as API
    participant Ag as Agent
    participant T as Tools
    participant L as LLM
    participant DB as Database
    
    U->>F: Send message
    F->>A: POST /secretary/chat/stream
    A->>DB: Get/Create session
    A->>DB: Save user message
    A->>Ag: chat_stream(message, history)
    
    loop Streaming
        Ag->>L: Generate response
        L-->>Ag: Token
        Ag-->>A: Token event
        A-->>F: SSE: {type: "token"}
        F-->>U: Display token
    end
    
    opt Tool Call
        Ag->>T: Execute tool
        T-->>Ag: Result
        Ag-->>A: Tool event
        A-->>F: SSE: {type: "tool_result"}
    end
    
    A->>DB: Save assistant message
    A-->>F: SSE: {type: "done"}
```

### Learning Record Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as API
    participant DB as Database
    
    U->>F: Request to learn (word/topic)
    F->>A: POST /secretary/chat
    A-->>F: Learning response
    F-->>U: Display learning content
    
    U->>F: Click "Save"
    F->>A: POST /learning/confirm
    A->>DB: Save learning_record
    A-->>F: Record saved
    F-->>U: Success notification
    
    U->>F: View Learning History
    F->>A: GET /learning/records
    A->>DB: Query records
    A-->>F: Record list
    F-->>U: Display records
```

## Database Schema

```mermaid
erDiagram
    users ||--o{ chat_sessions : "has"
    users ||--o{ learning_records : "creates"
    chat_sessions ||--o{ chat_messages : "contains"
    
    chat_sessions {
        uuid id PK
        int user_id FK
        string title
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    
    chat_messages {
        uuid id PK
        uuid session_id FK
        enum role
        text content
        json tool_calls
        string tool_name
        datetime created_at
    }
    
    learning_records {
        uuid id PK
        int user_id FK
        enum input_type
        text user_input
        json response_payload
        uuid session_id FK
        json tags
        boolean is_favorite
        int review_count
        datetime last_reviewed_at
        datetime created_at
        datetime updated_at
        boolean is_deleted
    }
```

## Key Design Decisions

### 1. LangChain for Agent Framework
- **Decision**: Use LangChain with tool-calling agent
- **Rationale**: Mature ecosystem, good LLM integration, streaming support
- **Trade-offs**: Larger dependency footprint

### 2. YAML Prompt Templates
- **Decision**: Externalize prompts to YAML files
- **Rationale**: Easy to modify without code changes, supports hot-reload
- **Trade-offs**: Runtime file I/O, potential parsing errors

### 3. Self-Hosted LLM Support
- **Decision**: Support self-signed SSL certificates via `LLM_VERIFY_SSL` setting
- **Rationale**: Enterprise deployments often use internal CAs
- **Trade-offs**: Potential security considerations if misused

### 4. Structured Logging with Tracing
- **Decision**: Implement `@trace_llm_call` and `@trace_tool_call` decorators
- **Rationale**: Observability for debugging and monitoring
- **Trade-offs**: Slight performance overhead

### 5. Learning Records with User Confirmation
- **Decision**: Require explicit user confirmation before saving learning content
- **Rationale**: User control over what gets saved, avoid noise
- **Trade-offs**: Extra user interaction step

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | LLM provider name | `openai` |
| `LLM_BASE_URL` | LLM API base URL | - |
| `LLM_API_KEY` | LLM API key | - |
| `LLM_MODEL` | Model name | `gpt-4o` |
| `LLM_VERIFY_SSL` | Verify SSL certificates | `true` |
| `LLM_TIMEOUT` | Request timeout in seconds | `60` |

## Metrics

### RED Metrics
- `secretary_chat_requests_total` - Total chat requests by method and status
- `secretary_chat_request_duration_seconds` - Chat request duration histogram
- `secretary_chat_first_token_latency_seconds` - Time to first token
- `secretary_chat_errors_total` - Errors by type

### Tool Metrics
- `secretary_tool_calls_total` - Tool calls by name and status
- `secretary_tool_call_duration_seconds` - Tool execution duration

### Business Metrics
- `secretary_learning_records_total` - Learning records by type
- `secretary_learning_reviews_total` - Review counts
- `secretary_sessions_created_total` - Sessions created
- `secretary_messages_total` - Messages by role

### Resource Metrics
- `secretary_active_sessions` - Active session count
- `secretary_active_streams` - Active streaming connections

## API Endpoints

### Chat
- `POST /api/v1/secretary/chat` - Non-streaming chat
- `POST /api/v1/secretary/chat/stream` - Streaming chat (SSE)
- `GET /api/v1/secretary/sessions` - List sessions
- `GET /api/v1/secretary/sessions/{id}` - Get session with messages
- `DELETE /api/v1/secretary/sessions/{id}` - Delete session
- `GET /api/v1/secretary/tools` - List available tools

### Learning
- `POST /api/v1/learning/confirm` - Save learning record
- `GET /api/v1/learning/records` - List records with filters
- `GET /api/v1/learning/records/{id}` - Get single record
- `PATCH /api/v1/learning/records/{id}` - Update record
- `DELETE /api/v1/learning/records/{id}` - Delete record
- `GET /api/v1/learning/search` - Search records
- `POST /api/v1/learning/records/{id}/review` - Mark as reviewed
- `POST /api/v1/learning/records/{id}/favorite` - Toggle favorite
- `GET /api/v1/learning/statistics` - Get statistics
