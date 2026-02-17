# Change: Personal Secretary AI Agent

## Why

Users want a conversational AI assistant ("Personal Secretary") that can help with daily tasks through a chat interface with access to various tools. The current app has LLM integration for recommendations but lacks a general-purpose chat-based agent that can:

1. **Help learn English**: Explain words with Chinese translation, pronunciation, and examples; explain sentences in context
2. **Help learn new tech**: Provide structured learning plans for tech topics with concepts, resources, and time estimates
3. **Assist daily tasks**: Weather lookup, calculations, notes, tasks, and reminders

## Development Approach: Three Protectors (三大护法)

This change follows the **Three Protectors** methodology for AI-assisted development:

| Protector | Core Question | Method |
|-----------|---------------|--------|
| **Verifiability (可验证性)** | Did AI write it correctly? | TDD - Write tests FIRST |
| **Observability (可观测性)** | How is it running? | MDD - Define metrics upfront |
| **Understandability (可理解性)** | Can humans understand it? | Living Docs - Architecture + Runbook |

**Workflow**: Tests → Metrics → Implementation → Documentation

See `design.md` for detailed methodology and `tasks.md` for task breakdown.

## What Changes

- Add an **AI agent flow** that accepts user chat messages and responds using LLM with access to a configurable set of tools.
- **Chat UI**: A dedicated chat interface for conversing with the Personal Secretary agent.
- **Learning Tools** (English & Tech):
  - **Learn Word**: Input an English word → Get Chinese explanation, pronunciation (IPA), usage examples; save to learning records on confirm
  - **Learn Sentence**: Input an English sentence → Get Chinese explanation, grammar notes, context examples; save on confirm
  - **Learn Topic**: Input a tech topic (e.g., "Kubernetes", "WebRTC") → Get structured learning plan with:
    - Introduction and key concepts
    - Step-by-step learning path
    - Recommended resources (tutorials, docs, courses, videos)
    - Prerequisites and time estimate
    - Save learning plan on confirm
  - **Learn Article** (URL): Input a URL → System will:
    - Fetch article content from URL
    - Convert to clean markdown format
    - Translate to Chinese (bilingual: keep English, add Chinese)
    - Generate summary mindmap in PlantUML format
    - Render mindmap to PNG image
    - Save article, translation, and mindmap on confirm
  - **Answer Question**: Answer general questions; save Q&A on confirm
  - **Plan Idea**: Turn ideas into executable plans; save on confirm
- **Utility Tools**:
  - **Weather**: Get weather information (reuse existing weather service)
  - **Calculator**: Perform calculations
  - **DateTime**: Get current date/time
  - **Notes/Memo**: Save, search, and recall notes
  - **Task Management**: Create, list, complete tasks
  - **Reminders**: Create and list reminders
- **Learning Records**: Persist learning content (words, sentences, topics, Q&A) to database when user confirms
- **Conversation Memory**: Maintain conversation history within a session
- **Streaming Responses**: Support streaming chat responses for better UX
- Add **database tables** for chat sessions, messages, and learning records
- Add **API endpoints** for chat and learning record management
- Add **UI** (new Chat view) with learning record history
- **NON-BREAKING**: Existing recommendation, weather, and email flows remain unchanged.

## AI Agent Framework Recommendation

### Recommended: LangChain (Primary)

**LangChain** is recommended as the primary AI agent framework for this Python backend:

| Criteria | LangChain |
|----------|-----------|
| **Maturity** | Most popular Python AI framework, large ecosystem |
| **Tool Support** | Excellent - built-in tools + custom tool creation |
| **Memory** | Built-in conversation memory, window buffer, summary memory |
| **Streaming** | Native streaming support for chat responses |
| **LLM Providers** | Works with OpenAI, Anthropic, Ollama, and all OpenAI-compatible APIs |
| **Existing Code** | Already demonstrated in `example/langchain_agent_*.py` |
| **Documentation** | Extensive documentation and community support |

**Installation**: Already compatible with existing `openai` and `httpx` dependencies.

```
langchain>=0.2.0
langchain-openai>=0.1.0
```

### Alternative: LangGraph (For Complex Workflows)

If the agent needs complex multi-step reasoning with state management:

```
langgraph>=0.1.0
```

### Keep Using: Instructor (Structured Outputs)

The existing `instructor` library should continue to be used for:
- Structured output parsing (Pydantic models)
- Tool argument validation
- Response schema enforcement

### Framework Comparison

| Framework | Use Case | Pros | Cons |
|-----------|----------|------|------|
| **LangChain** | General-purpose agent | Mature, tools, memory | Can be complex |
| **LangGraph** | Complex state workflows | Precise control | Steeper learning curve |
| **Instructor** | Structured outputs | Simple, Pydantic | Not for agents |
| **CrewAI** | Multi-agent systems | Agent collaboration | Overkill for single agent |
| **AutoGen** | Multi-agent chat | Research-backed | Microsoft ecosystem |

**Recommendation**: Start with **LangChain** for the agent with **Instructor** for structured tool outputs.

## Impact

- **Affected specs**: New capability `personal-secretary-agent`.
- **Affected code**:
  - Backend: New `langchain` dependency; new models (`app/models/chat_session.py`, `app/models/chat_message.py`); new service (`app/services/secretary_agent/`) using LangChain for chat + tools; new handlers and routes.
  - Frontend: New view `SecretaryChat.vue` for chat UI.
  - Database: New tables for chat sessions and messages; migrations via Alembic.
- **Database schema**: 
  - `chat_sessions`: id, user_id, title, created_at, updated_at
  - `chat_messages`: id, session_id, role (user/assistant/tool), content, tool_calls (JSON), created_at
- **Breaking**: None.
