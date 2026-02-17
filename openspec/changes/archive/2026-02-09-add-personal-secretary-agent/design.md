# Design: Personal Secretary AI Agent

## Context

The app already has LLM integration (OpenAI-compatible providers via `instructor` and `openai` SDK), weather services, email services, and recommendation generation. This change introduces a conversational AI agent that can chat with users and perform actions using configurable tools. Stakeholders are users who want a personal assistant to help with daily tasks through natural language.

**Framework**: The AI agent SHALL be built with **LangChain**, the most popular Python LLM application framework. LangChain provides tool abstractions, memory management, and streaming support that align with the project's async Python architecture.

**Self-hosted LLM Support**: The agent SHALL support self-hosted LLMs with self-signed certificates by respecting the existing `LLM_VERIFY_SSL` configuration setting.

---

## Development Methodology: Three Protectors (三大护法)

This change follows the **Three Protectors** methodology for AI-assisted development, ensuring quality through:

```
              可验证性（TDD）
             "确保写对了"
                   ▲
                  / \
                 /   \
                /     \
               /       \
              /    ◉    \
             /   质量    \
            /   保障     \
           ▼             ▼
   可观测性（MDD）    可理解性（活文档）
  "确保跑得好"       "确保看得懂"
```

| Protector | Core Question | Method | AI Build-in Approach |
|-----------|---------------|--------|---------------------|
| **Verifiability** | Did AI write it correctly? | TDD | Write test cases FIRST, then implementation |
| **Observability** | How is it running? | MDD | Define metrics upfront, instrument during implementation |
| **Understandability** | Can humans understand it? | Living Docs | Require comments, architecture diagrams, runbooks |

### TDD (Test-Driven Development)

**Workflow**: Red → Green → Refactor

1. **Red**: Write failing tests that define expected behavior (acceptance tests, unit tests)
2. **Green**: Implement minimal code to make tests pass
3. **Refactor**: Clean up code while keeping tests green

**TDD Artifacts**:
- `tests/test_secretary_agent.py` - Unit tests for agent (classification, tool calling)
- `tests/test_chat_api.py` - API contract tests (AT-1 through AT-8)
- `tests/test_tools.py` - Individual tool tests

**Coverage Target**: > 80%

### MDD (Metrics-Driven Development)

**Workflow**: Define → Instrument → Monitor → Validate

1. Define metrics and thresholds before implementation
2. Instrument code with metrics (Prometheus counters/histograms)
3. Create monitoring dashboards
4. Validate metrics meet thresholds before release

**Key Metrics** (see Metrics section below):
- Latency (P50, P95, P99) for chat endpoint
- Tool call success rate
- Error rate by endpoint
- Active sessions per user

### Living Documentation

**Principles**:
- **Reliable**: Documentation stays in sync with code
- **Low-effort**: Auto-generate where possible
- **Collaborative**: Promotes knowledge sharing
- **Insightful**: Guides attention, encourages deep thinking

**Three Layers**:
1. **Code Comments**: Explain "why", not "what"
2. **Architecture Docs**: System overview in 5 minutes
3. **Runbook**: Troubleshoot in 10 minutes

---

## Goals / Non-Goals

- **Goals**:
  - Provide a chat-based AI assistant with natural language understanding
  - Support configurable tools for common tasks (calendar, notes, weather, tasks)
  - Maintain conversation history within sessions
  - Stream responses for better UX
  - Integrate with existing authentication and LLM configuration
  - Follow TDD methodology

- **Non-Goals**:
  - Real-time multi-user collaboration
  - Voice input/output (future enhancement)
  - Complex multi-agent orchestration (single agent for now)
  - Autonomous background tasks without user interaction

---

## Agent Architecture

### LangChain Agent Components

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         User Message                                     │
└─────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  1. Conversation Memory (LangChain)                                      │
│     - Load recent messages from session                                  │
│     - Apply token limit trimming                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  2. Tool-Enabled Agent (LangChain AgentExecutor)                        │
│     - System prompt with persona ("Personal Secretary")                  │
│     - Available tools injected                                           │
│     - LLM decides: respond or use tool                                   │
└─────────────────────────────────────────────────────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
┌──────────────────────────┐    ┌──────────────────────────┐
│  Direct Response         │    │  Tool Execution          │
│  (No tool needed)        │    │  - Parse tool call       │
│                          │    │  - Execute tool function │
│                          │    │  - Return result to LLM  │
└──────────────────────────┘    └──────────────────────────┘
                    │                           │
                    └─────────────┬─────────────┘
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  3. Response Generation (Streaming)                                      │
│     - Stream tokens to frontend via SSE                                  │
│     - Save message to database                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

### Tool Registry

Tools are registered with the agent and can be enabled/disabled per user or globally:

#### Learning Tools (English & Tech)

| Tool | Description | Response |
|------|-------------|----------|
| `learn_word` | Learn an English word | Chinese explanation, pronunciation (IPA), usage examples |
| `learn_sentence` | Learn an English sentence | Chinese translation, grammar notes, context examples |
| `learn_topic` | Learn a tech topic | Introduction, key concepts, learning path, resources, time estimate |
| `learn_article` | Learn from URL article | Fetch → Markdown → Bilingual translation → Mindmap PNG |
| `answer_question` | Answer a question | Direct answer with explanation |
| `plan_idea` | Turn idea into executable plan | Structured action plan with steps |
| `save_learning` | Save learning record to database | Persists word/sentence/topic/article/Q&A/idea on user confirm |
| `list_learning_records` | List saved learning records | Paginated list with filters by type |
| `search_learning` | Search learning records | Full-text search on saved content |

#### Utility Tools

| Tool | Description | Implementation |
|------|-------------|----------------|
| `get_weather` | Get current weather for a city | Reuse `WeatherProviderFactory` |
| `get_datetime` | Get current date/time | Built-in Python |
| `calculate` | Perform math calculations | Built-in Python (safe eval) |
| `save_note` | Save a note/memo | New: `NoteService` |
| `search_notes` | Search saved notes | New: `NoteService` |
| `create_task` | Create a to-do item | New: `TaskService` |
| `list_tasks` | List pending tasks | New: `TaskService` |
| `complete_task` | Mark a task as done | New: `TaskService` |
| `create_reminder` | Set a reminder for a specific time | New: `ReminderService` |
| `list_reminders` | List upcoming reminders | New: `ReminderService` |

### Learning Tool Responses

#### Word Response Schema

```python
class WordResponse(BaseModel):
    word: str
    pronunciation: str  # IPA notation, e.g., /səˈrendɪpɪti/
    part_of_speech: str  # noun, verb, adjective, etc.
    chinese_explanation: str  # 中文解释
    definition: str  # English definition
    examples: list[str]  # Usage examples (at least 2)
    synonyms: list[str]  # Similar words
    etymology: str | None  # Word origin (optional)
```

#### Sentence Response Schema

```python
class SentenceResponse(BaseModel):
    sentence: str
    chinese_translation: str  # 中文翻译
    grammar_points: list[str]  # Grammar notes
    key_phrases: list[str]  # Important phrases
    context: str  # When to use this sentence
    variations: list[str]  # Similar expressions
```

#### Topic (Tech Learning) Response Schema

```python
class TopicResponse(BaseModel):
    topic: str
    introduction: str  # Brief introduction (2-3 sentences)
    key_concepts: list[KeyConcept]  # Core concepts to understand
    learning_path: list[LearningStep]  # Step-by-step learning plan
    resources: list[Resource]  # Recommended resources
    prerequisites: list[str]  # What to learn first
    time_estimate: str  # e.g., "2-3 weeks for basics"
    difficulty: str  # beginner, intermediate, advanced

class KeyConcept(BaseModel):
    name: str
    description: str
    importance: str  # Why it matters

class LearningStep(BaseModel):
    step: int
    title: str
    description: str
    duration: str  # e.g., "1-2 days"
    outcomes: list[str]  # What you'll learn

class Resource(BaseModel):
    title: str
    type: str  # tutorial, documentation, course, video, book
    url: str | None
    description: str
    difficulty: str
```

#### Article Response Schema (URL Learning)

```python
class ArticleResponse(BaseModel):
    url: str  # Original URL
    title: str  # Article title
    author: str | None  # Author if available
    published_date: str | None  # Publication date if available
    
    # Content in markdown format
    original_markdown: str  # Clean markdown of original article
    
    # Bilingual content (English kept, Chinese added)
    bilingual_content: str  # Markdown with English paragraphs followed by Chinese translation
    
    # Summary
    summary: str  # Brief summary (3-5 sentences)
    key_points: list[str]  # Main takeaways (bullet points)
    
    # Mindmap
    mindmap_plantuml: str  # PlantUML mindmap script
    mindmap_image_path: str | None  # Path to rendered PNG (after rendering)
    
    # Metadata
    word_count: int  # Original word count
    reading_time: str  # Estimated reading time (e.g., "5 min")
    language: str  # Detected language of original
    tags: list[str]  # Auto-generated tags
```

#### Article Processing Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         User Input: URL                                  │
└─────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  1. Fetch Article                                                        │
│     - HTTP GET with proper headers (User-Agent, Accept)                  │
│     - Handle redirects, timeouts                                         │
│     - Support: Medium, Dev.to, GitHub, blogs, news sites                 │
└─────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  2. Convert to Markdown                                                  │
│     - Use readability/trafilatura to extract main content                │
│     - Remove ads, navigation, sidebars                                   │
│     - Preserve headings, code blocks, images, links                      │
│     - Clean up formatting                                                │
└─────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  3. Translate to Bilingual Format                                        │
│     - Detect language (skip if already Chinese)                          │
│     - Translate paragraph by paragraph                                   │
│     - Keep original English, add Chinese below each paragraph            │
│     - Preserve code blocks untranslated                                  │
│     - Format: "English paragraph\n\n> 中文翻译\n\n"                       │
└─────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  4. Generate Summary & Mindmap                                           │
│     - LLM generates summary (3-5 sentences)                              │
│     - LLM extracts key points                                            │
│     - LLM generates PlantUML mindmap script                              │
└─────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  5. Render Mindmap to PNG                                                │
│     - Use PlantUML server or local jar                                   │
│     - Save PNG to storage (local or S3)                                  │
│     - Return path/URL to image                                           │
└─────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  6. Return ArticleResponse                                               │
│     - User reviews content                                               │
│     - On confirm → Save to learning_records with type='article'          │
└─────────────────────────────────────────────────────────────────────────┘
```

#### Dependencies for Article Processing

| Library | Purpose |
|---------|---------|
| `httpx` | Async HTTP client (already installed) |
| `trafilatura` | Web content extraction (recommended) |
| `readability-lxml` | Alternative content extraction |
| `plantuml` | PlantUML rendering (Python wrapper) |

### Tool Definition Example (LangChain)

```python
from langchain.tools import tool
from pydantic import BaseModel, Field

class WeatherInput(BaseModel):
    city: str = Field(description="City name or AD code")

@tool("get_weather", args_schema=WeatherInput)
async def get_weather(city: str) -> str:
    """Get the current weather for a specified city."""
    # Implementation uses existing WeatherProviderFactory
    ...

class LearnWordInput(BaseModel):
    word: str = Field(description="English word to learn")

@tool("learn_word", args_schema=LearnWordInput)
async def learn_word(word: str) -> WordResponse:
    """
    Learn an English word with Chinese explanation, pronunciation, and examples.
    
    Returns structured response with:
    - Chinese explanation (中文解释)
    - Pronunciation (IPA notation)
    - Part of speech
    - Usage examples
    - Synonyms
    """
    # Uses LLM to generate structured response
    ...

class LearnTopicInput(BaseModel):
    topic: str = Field(description="Tech topic to learn, e.g., 'Kubernetes', 'WebRTC'")

@tool("learn_topic", args_schema=LearnTopicInput)
async def learn_topic(topic: str) -> TopicResponse:
    """
    Generate a comprehensive learning plan for a tech topic.
    
    Returns structured response with:
    - Introduction and key concepts
    - Step-by-step learning path
    - Recommended resources (tutorials, docs, courses)
    - Prerequisites and time estimate
    """
    # Uses LLM to generate structured learning plan
    ...

class LearnArticleInput(BaseModel):
    url: str = Field(description="URL of the article to learn from")

@tool("learn_article", args_schema=LearnArticleInput)
async def learn_article(url: str) -> ArticleResponse:
    """
    Learn from a web article: fetch, convert to markdown, translate, and generate mindmap.
    
    Processing pipeline:
    1. Fetch article content from URL
    2. Convert HTML to clean markdown (remove ads, navigation)
    3. Translate to bilingual format (English + Chinese)
    4. Generate summary and key points
    5. Generate PlantUML mindmap script
    6. Render mindmap to PNG image
    
    Returns ArticleResponse with original, bilingual content, summary, and mindmap.
    """
    # Step 1: Fetch article
    content = await fetch_article(url)
    
    # Step 2: Convert to markdown
    markdown = extract_to_markdown(content)
    
    # Step 3: Translate to bilingual
    bilingual = await translate_bilingual(markdown)
    
    # Step 4: Generate summary with LLM
    summary, key_points = await generate_summary(markdown)
    
    # Step 5: Generate mindmap PlantUML
    mindmap_puml = await generate_mindmap_plantuml(markdown, key_points)
    
    # Step 6: Render to PNG
    mindmap_path = render_plantuml_to_png(mindmap_puml)
    
    return ArticleResponse(...)
```

---

## Memory Management

### Session Memory

- **Scope**: Single chat session
- **Storage**: Database (`chat_messages` table)
- **LangChain Integration**: `ConversationBufferWindowMemory` with last N messages
- **Token Limit**: Trim older messages when approaching context limit

### Memory Flow

```python
# Load memory from database
messages = await load_session_messages(session_id, limit=20)
memory = ConversationBufferWindowMemory(
    chat_memory=ChatMessageHistory(messages=messages),
    return_messages=True,
    k=20  # Keep last 20 exchanges
)

# Create agent with memory
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory)

# Execute with streaming
async for chunk in agent_executor.astream({"input": user_message}):
    yield chunk
```

---

## Prompt Templates (YAML Configuration)

### Design Principles

Prompts SHALL be externalized to YAML files instead of hardcoded in code:

1. **Maintainability**: Non-developers can update prompts
2. **Testability**: Prompts can be versioned and A/B tested
3. **Separation of Concerns**: Business logic separate from prompt engineering
4. **i18n Ready**: Easy to add multi-language prompt support

### Directory Structure

```
backend/
└── app/
    └── services/
        └── secretary_agent/
            └── prompts/
                ├── __init__.py           # PromptLoader utility
                ├── system.yaml           # System prompts
                ├── learning_tools.yaml   # Learning tool prompts
                ├── article_tools.yaml    # Article processing prompts
                └── utility_tools.yaml    # Utility tool prompts
```

### Prompt File Format

#### `prompts/system.yaml`

```yaml
# System Prompt for Personal Secretary Agent
version: "1.0"
name: "personal_secretary_system"
description: "System prompt for the Personal Secretary AI Agent"

prompts:
  system:
    template: |
      You are a Personal Secretary AI assistant. You help users with:
      - Learning English words and sentences (with Chinese explanations)
      - Learning new technologies (structured learning plans)
      - Learning from web articles (bilingual translation + mindmap)
      - Answering questions and planning ideas
      - Daily tasks: weather, calculations, notes, tasks, reminders
      
      Guidelines:
      - Be helpful, concise, and professional
      - For English learning, always include Chinese explanations (中文解释)
      - For tech topics, provide structured learning paths
      - Ask for confirmation before saving learning records
      - Use tools when appropriate, but explain what you're doing
      
      Current date: {current_date}
      User timezone: {timezone}
    variables:
      - current_date
      - timezone

  confirm_save:
    template: |
      I've prepared the {content_type} learning content. Would you like me to save it to your learning records?
      
      Reply "yes" or "confirm" to save, or ask me to modify something.
    variables:
      - content_type
```

#### `prompts/learning_tools.yaml`

```yaml
version: "1.0"
name: "learning_tools"
description: "Prompts for learning tools"

prompts:
  learn_word:
    template: |
      Explain the English word "{word}" for a Chinese learner:
      
      1. **Chinese Explanation (中文解释)**: Explain the meaning in Chinese
      2. **Pronunciation**: Provide IPA notation
      3. **Part of Speech**: noun, verb, adjective, etc.
      4. **Usage Examples**: 3 example sentences with Chinese translations
      5. **Synonyms**: List 2-3 synonyms
      6. **Common Collocations**: Common word combinations
      
      Format as structured JSON matching WordResponse schema.
    variables:
      - word

  learn_sentence:
    template: |
      Explain the English sentence for a Chinese learner:
      
      Sentence: "{sentence}"
      
      Provide:
      1. **Chinese Translation (中文翻译)**: Natural Chinese translation
      2. **Word-by-word Analysis**: Key vocabulary with meanings
      3. **Grammar Notes**: Explain grammar patterns used
      4. **Context Examples**: 2 similar sentences with translations
      5. **Usage Notes**: When/how to use this expression
      
      Format as structured JSON matching SentenceResponse schema.
    variables:
      - sentence

  learn_topic:
    template: |
      Create a comprehensive learning plan for the tech topic: "{topic}"
      
      Provide:
      1. **Introduction**: What is {topic}? (2-3 sentences)
      2. **Key Concepts**: 5-7 fundamental concepts with descriptions
      3. **Learning Path**: Step-by-step learning progression (5-8 steps)
         - Each step: title, description, duration, outcomes
      4. **Resources**: Recommended tutorials, docs, courses, videos
         - Include URLs when possible
      5. **Prerequisites**: What should the learner know first?
      6. **Time Estimate**: Total time to learn basics
      7. **Difficulty Level**: beginner/intermediate/advanced
      
      Format as structured JSON matching TopicResponse schema.
    variables:
      - topic
```

#### `prompts/article_tools.yaml`

```yaml
version: "1.0"
name: "article_tools"
description: "Prompts for article processing"

prompts:
  translate_paragraph:
    template: |
      Translate the following English paragraph to Chinese.
      Keep technical terms in English with Chinese explanation in parentheses.
      Preserve code blocks without translation.
      
      English:
      {paragraph}
      
      Chinese translation:
    variables:
      - paragraph

  generate_summary:
    template: |
      Summarize the following article:
      
      Title: {title}
      Content:
      {content}
      
      Provide:
      1. **Summary**: 3-5 sentence summary in Chinese
      2. **Key Points**: 5-7 main takeaways as bullet points (in Chinese)
      3. **Tags**: 3-5 relevant topic tags
      
      Format as JSON with fields: summary, key_points (array), tags (array)
    variables:
      - title
      - content

  generate_mindmap:
    template: |
      Generate a PlantUML mindmap script for this article:
      
      Title: {title}
      Key Points:
      {key_points}
      
      Content Structure:
      {headings}
      
      Requirements:
      - Use PlantUML mindmap syntax (@startmindmap / @endmindmap)
      - Root node: article title
      - Level 2: main sections/themes
      - Level 3: key points under each theme
      - Keep text concise (max 30 chars per node)
      - Use Chinese for node text
      
      Example format:
      ```plantuml
      @startmindmap
      * 文章标题
      ** 主题一
      *** 要点1
      *** 要点2
      ** 主题二
      *** 要点3
      @endmindmap
      ```
      
      Generate ONLY the PlantUML code, no explanation.
    variables:
      - title
      - key_points
      - headings
```

### Prompt Loader Utility

```python
# app/services/secretary_agent/prompts/__init__.py
from pathlib import Path
from typing import Any
import yaml
from functools import lru_cache

PROMPTS_DIR = Path(__file__).parent

@lru_cache(maxsize=10)
def load_prompt_file(filename: str) -> dict:
    """Load and cache a prompt YAML file."""
    filepath = PROMPTS_DIR / filename
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def get_prompt(filename: str, prompt_name: str, **variables) -> str:
    """
    Get a prompt template and fill in variables.
    
    Args:
        filename: YAML file name (e.g., 'learning_tools.yaml')
        prompt_name: Prompt key (e.g., 'learn_word')
        **variables: Template variables to substitute
    
    Returns:
        Formatted prompt string
    
    Example:
        prompt = get_prompt('learning_tools.yaml', 'learn_word', word='serendipity')
    """
    data = load_prompt_file(filename)
    template = data['prompts'][prompt_name]['template']
    return template.format(**variables)

def reload_prompts():
    """Clear cache and reload all prompt files (for hot-reload)."""
    load_prompt_file.cache_clear()
```

### Usage in Tools

```python
# app/services/secretary_agent/tools/learning_tools.py
from ..prompts import get_prompt

@tool("learn_word", args_schema=LearnWordInput)
async def learn_word(word: str) -> WordResponse:
    """Learn an English word with Chinese explanation."""
    
    # Load prompt from YAML
    prompt = get_prompt('learning_tools.yaml', 'learn_word', word=word)
    
    # Use instructor for structured output
    response = await llm_client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_model=WordResponse
    )
    
    return response
```

### Environment Configuration

```bash
# Optional: Override prompt directory location
PROMPTS_DIR=/path/to/custom/prompts

# Optional: Enable hot-reload for development
PROMPTS_HOT_RELOAD=true
```

---

## API Design

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/secretary/chat` | Send message, get streaming response |
| GET | `/api/v1/secretary/sessions` | List user's chat sessions |
| GET | `/api/v1/secretary/sessions/{id}` | Get session with message history |
| DELETE | `/api/v1/secretary/sessions/{id}` | Delete a chat session |
| GET | `/api/v1/secretary/tools` | List available tools |

### Chat Request/Response

```python
# Request
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None  # Auto-create if not provided

# Streaming Response (SSE)
# event: message
# data: {"type": "token", "content": "Hello"}
# data: {"type": "tool_call", "tool": "get_weather", "args": {...}}
# data: {"type": "tool_result", "tool": "get_weather", "result": "..."}
# data: {"type": "done", "session_id": "...", "message_id": "..."}
```

---

## Database Schema

### chat_sessions

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | INTEGER | FK to users |
| title | VARCHAR(255) | Auto-generated from first message |
| created_at | TIMESTAMP | Creation time |
| updated_at | TIMESTAMP | Last activity |

### chat_messages

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| session_id | UUID | FK to chat_sessions |
| role | VARCHAR(20) | 'user', 'assistant', 'tool' |
| content | TEXT | Message content |
| tool_calls | JSON | Tool call data (if any) |
| tool_name | VARCHAR(50) | Tool name (if role='tool') |
| created_at | TIMESTAMP | Creation time |

### learning_records

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | INTEGER | FK to users |
| input_type | VARCHAR(20) | 'word', 'sentence', 'topic', 'question', 'idea' |
| user_input | TEXT | Original user input |
| response_payload | JSON | Structured response (WordResponse, TopicResponse, etc.) |
| session_id | UUID | FK to chat_sessions (optional, links to conversation) |
| tags | JSON | User-defined tags for organization |
| review_count | INTEGER | Times reviewed (for spaced repetition) |
| last_reviewed_at | TIMESTAMP | Last review time |
| created_at | TIMESTAMP | Creation time |
| updated_at | TIMESTAMP | Last update time |
| deleted_at | TIMESTAMP | Soft delete timestamp |

**Learning Record Types**:

| Type | User Input Example | Response Payload |
|------|-------------------|------------------|
| `word` | "serendipity" | WordResponse (Chinese explanation, pronunciation, examples) |
| `sentence` | "The early bird catches the worm" | SentenceResponse (translation, grammar, context) |
| `topic` | "Kubernetes" | TopicResponse (intro, concepts, learning path, resources) |
| `article` | "https://example.com/k8s-guide" | ArticleResponse (bilingual content, summary, mindmap PNG) |
| `question` | "How does OAuth2 work?" | Answer with explanation |
| `idea` | "Build a habit tracker app" | Executable plan with steps |

---

## Frontend Architecture

### Chat UI Components

```
┌─────────────────────────────────────────────────────────────────────────┐
│  SecretaryChat.vue                                                       │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  Session Sidebar (optional)                                        │  │
│  │  - List of recent sessions                                         │  │
│  │  - New chat button                                                 │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  Message List                                                      │  │
│  │  - User messages (right-aligned)                                   │  │
│  │  - Assistant messages (left-aligned, streaming)                    │  │
│  │  - Tool usage indicators (collapsible)                             │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  Input Area                                                        │  │
│  │  - Textarea with auto-resize                                       │  │
│  │  - Send button (Ctrl+Enter)                                        │  │
│  │  - Tool suggestions (optional)                                     │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

### Pinia Store

```typescript
// stores/secretary.ts
interface SecretaryState {
  currentSessionId: string | null
  sessions: ChatSession[]
  messages: ChatMessage[]
  isStreaming: boolean
  streamingContent: string
  availableTools: Tool[]
}
```

---

## Decisions

1. **LangChain for agent framework**: LangChain provides the most comprehensive tooling for building AI agents in Python. It has:
   - Built-in tool support with automatic argument parsing
   - Memory management (conversation buffers)
   - Streaming support
   - Works with existing OpenAI-compatible setup
   - Already demonstrated in project examples

2. **Single agent architecture**: Start with a single agent rather than multi-agent. The Personal Secretary handles all tools itself. Multi-agent can be added later if needed (e.g., specialized agents for different domains).

3. **SSE for streaming**: Use Server-Sent Events (SSE) for streaming chat responses, matching the existing streaming recommendation pattern.

4. **Session-based memory**: Store messages in database, load recent N messages into LangChain memory for each request. This allows conversation persistence and retrieval.

5. **Tool modularity**: Tools are defined as separate functions with Pydantic schemas. New tools can be added without modifying the core agent logic.

6. **Persona prompt**: The agent has a configurable system prompt defining its persona as a "Personal Secretary" - helpful, concise, and action-oriented.

---

## Risks / Trade-offs

- **LLM latency**: Tool-using agents may have higher latency due to multi-turn LLM calls. Mitigate with streaming and optimistic UI updates.
- **Tool reliability**: External tool calls (weather, web search) may fail. Implement graceful error handling and fallback responses.
- **Token costs**: Conversation history consumes tokens. Implement aggressive trimming and summarization for long sessions.
- **Complexity**: LangChain adds a layer of abstraction. Alternative: use raw OpenAI function calling, but lose memory and streaming conveniences.

---

## Metrics (MDD) - 可观测性

Define upfront; instrument during implementation; validate before release.

### RED Metrics (Request-Error-Duration)

| Metric | Type | Labels | Description | Threshold |
|--------|------|--------|-------------|-----------|
| `secretary_chat_requests_total` | Counter | `status` (success/error) | Total chat requests | — |
| `secretary_chat_duration_seconds` | Histogram | — | End-to-end chat latency | P95 < 10s |
| `secretary_chat_errors_total` | Counter | `error_type` | Errors by type | Error rate < 1% |
| `secretary_chat_first_token_seconds` | Histogram | — | Time to first token (streaming) | P95 < 2s |

### Tool Metrics

| Metric | Type | Labels | Description | Threshold |
|--------|------|--------|-------------|-----------|
| `secretary_tool_calls_total` | Counter | `tool_name`, `status` | Tool invocations | — |
| `secretary_tool_duration_seconds` | Histogram | `tool_name` | Tool execution time | P95 < 5s |
| `secretary_tool_errors_total` | Counter | `tool_name`, `error_type` | Tool failures | < 5% per tool |

### Business Metrics

| Metric | Type | Description | Threshold |
|--------|------|-------------|-----------|
| `secretary_active_sessions` | Gauge | Current active chat sessions | — |
| `secretary_messages_per_session` | Histogram | Messages per session | Avg > 3 (engagement) |
| `secretary_session_duration_seconds` | Histogram | Session duration | — |

### Resource Metrics

| Metric | Type | Description | Threshold |
|--------|------|-------------|-----------|
| `secretary_llm_tokens_total` | Counter | LLM tokens consumed | Monitor cost |
| `secretary_memory_messages` | Gauge | Messages in memory per session | < 50 per session |

### Instrumentation Plan

1. Use `prometheus_client` to register counters and histograms
2. Wrap chat handler to record `chat_requests_total`, `chat_duration_seconds`, `first_token_seconds`
3. Wrap each tool to record `tool_calls_total`, `tool_duration_seconds`
4. Expose metrics at `/metrics` (already available via FastAPI)
5. Create Grafana dashboard with panels for latency, error rate, tool usage

### Validation Criteria (Before Release)

- [ ] All operational metrics are instrumented and visible in Prometheus
- [ ] P95 chat latency < 10s under load (10 concurrent users)
- [ ] P95 first-token latency < 2s
- [ ] Error rate < 1% in staging test run
- [ ] Tool error rate < 5% per tool
- [ ] Grafana dashboard created with all key metrics

---

## Logging & Tracing (可追踪性)

Every LLM call and tool call SHALL be logged with structured data for debugging, auditing, and performance analysis.

### Log Structure

```python
# app/services/secretary_agent/tracing.py
import logging
import uuid
from datetime import datetime
from typing import Any
from pydantic import BaseModel

logger = logging.getLogger("secretary_agent")

class LLMCallLog(BaseModel):
    """Structured log for LLM calls."""
    trace_id: str           # Unique ID for this request chain
    call_id: str            # Unique ID for this specific call
    timestamp: datetime
    call_type: str          # "llm" | "tool"
    
    # LLM specific
    model: str | None = None
    prompt_template: str | None = None  # YAML template name used
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
    
    # Tool specific
    tool_name: str | None = None
    tool_args: dict | None = None
    tool_result: str | None = None  # Truncated if too long
    
    # Timing
    duration_ms: float
    
    # Status
    status: str             # "success" | "error"
    error_message: str | None = None
    
    # Context
    user_id: int | None = None
    session_id: str | None = None

class ToolCallLog(BaseModel):
    """Structured log for tool calls."""
    trace_id: str
    call_id: str
    timestamp: datetime
    tool_name: str
    tool_args: dict
    tool_result: str | None = None  # Truncated to max 1000 chars
    duration_ms: float
    status: str
    error_message: str | None = None
    user_id: int | None = None
    session_id: str | None = None
```

### Trace Context

```python
# app/services/secretary_agent/tracing.py
import contextvars
from uuid import uuid4

# Thread-local trace context
_trace_context: contextvars.ContextVar[dict] = contextvars.ContextVar(
    'trace_context', default={}
)

def new_trace(user_id: int = None, session_id: str = None) -> str:
    """Start a new trace for a chat request."""
    trace_id = str(uuid4())
    _trace_context.set({
        "trace_id": trace_id,
        "user_id": user_id,
        "session_id": session_id,
        "calls": []  # Track all calls in this trace
    })
    return trace_id

def get_trace_id() -> str | None:
    """Get current trace ID."""
    ctx = _trace_context.get()
    return ctx.get("trace_id")

def get_trace_context() -> dict:
    """Get full trace context."""
    return _trace_context.get()
```

### LLM Call Logging Decorator

```python
# app/services/secretary_agent/tracing.py
import functools
import time
from typing import Callable

def trace_llm_call(prompt_template: str = None):
    """
    Decorator to trace LLM calls.
    
    Usage:
        @trace_llm_call(prompt_template="learning_tools.yaml:learn_word")
        async def call_llm(prompt: str, model: str) -> str:
            ...
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            call_id = str(uuid4())
            ctx = get_trace_context()
            start_time = time.perf_counter()
            
            log_entry = {
                "trace_id": ctx.get("trace_id"),
                "call_id": call_id,
                "timestamp": datetime.utcnow().isoformat(),
                "call_type": "llm",
                "prompt_template": prompt_template,
                "model": kwargs.get("model") or args[1] if len(args) > 1 else None,
                "user_id": ctx.get("user_id"),
                "session_id": ctx.get("session_id"),
            }
            
            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.perf_counter() - start_time) * 1000
                
                # Extract token usage if available
                if hasattr(result, 'usage'):
                    log_entry["prompt_tokens"] = result.usage.prompt_tokens
                    log_entry["completion_tokens"] = result.usage.completion_tokens
                    log_entry["total_tokens"] = result.usage.total_tokens
                
                log_entry["duration_ms"] = duration_ms
                log_entry["status"] = "success"
                
                logger.info(
                    "LLM call completed",
                    extra={"llm_call": log_entry}
                )
                
                return result
                
            except Exception as e:
                duration_ms = (time.perf_counter() - start_time) * 1000
                log_entry["duration_ms"] = duration_ms
                log_entry["status"] = "error"
                log_entry["error_message"] = str(e)
                
                logger.error(
                    f"LLM call failed: {e}",
                    extra={"llm_call": log_entry},
                    exc_info=True
                )
                raise
        
        return wrapper
    return decorator
```

### Tool Call Logging Decorator

```python
# app/services/secretary_agent/tracing.py
import json

def trace_tool_call(func: Callable):
    """
    Decorator to trace tool calls.
    
    Usage:
        @tool("learn_word", args_schema=LearnWordInput)
        @trace_tool_call
        async def learn_word(word: str) -> WordResponse:
            ...
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        call_id = str(uuid4())
        ctx = get_trace_context()
        tool_name = func.__name__
        start_time = time.perf_counter()
        
        # Serialize args for logging (truncate large values)
        def truncate(v, max_len=500):
            s = str(v)
            return s[:max_len] + "..." if len(s) > max_len else s
        
        tool_args = {k: truncate(v) for k, v in kwargs.items()}
        
        log_entry = {
            "trace_id": ctx.get("trace_id"),
            "call_id": call_id,
            "timestamp": datetime.utcnow().isoformat(),
            "tool_name": tool_name,
            "tool_args": tool_args,
            "user_id": ctx.get("user_id"),
            "session_id": ctx.get("session_id"),
        }
        
        logger.info(
            f"Tool call started: {tool_name}",
            extra={"tool_call": log_entry}
        )
        
        try:
            result = await func(*args, **kwargs)
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            # Truncate result for logging
            result_str = truncate(
                result.model_dump_json() if hasattr(result, 'model_dump_json') 
                else str(result),
                max_len=1000
            )
            
            log_entry["tool_result"] = result_str
            log_entry["duration_ms"] = duration_ms
            log_entry["status"] = "success"
            
            logger.info(
                f"Tool call completed: {tool_name} ({duration_ms:.2f}ms)",
                extra={"tool_call": log_entry}
            )
            
            return result
            
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            log_entry["duration_ms"] = duration_ms
            log_entry["status"] = "error"
            log_entry["error_message"] = str(e)
            
            logger.error(
                f"Tool call failed: {tool_name} - {e}",
                extra={"tool_call": log_entry},
                exc_info=True
            )
            raise
    
    return wrapper
```

### Usage in Tools

```python
# app/services/secretary_agent/tools/learning_tools.py
from langchain.tools import tool
from ..tracing import trace_tool_call, trace_llm_call
from ..prompts import get_prompt

@tool("learn_word", args_schema=LearnWordInput)
@trace_tool_call
async def learn_word(word: str) -> WordResponse:
    """Learn an English word with Chinese explanation."""
    
    prompt = get_prompt('learning_tools.yaml', 'learn_word', word=word)
    
    # LLM call is also traced
    response = await traced_llm_call(
        prompt=prompt,
        model=settings.LLM_MODEL,
        response_model=WordResponse,
        prompt_template="learning_tools.yaml:learn_word"
    )
    
    return response

@trace_llm_call(prompt_template="custom")
async def traced_llm_call(prompt: str, model: str, response_model, **kwargs):
    """Traced LLM call with instructor."""
    return await llm_client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        response_model=response_model
    )
```

### Log Output Format (JSON)

```json
{
  "timestamp": "2026-02-04T10:30:45.123Z",
  "level": "INFO",
  "message": "Tool call completed: learn_word (1523.45ms)",
  "tool_call": {
    "trace_id": "550e8400-e29b-41d4-a716-446655440000",
    "call_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "timestamp": "2026-02-04T10:30:43.600Z",
    "tool_name": "learn_word",
    "tool_args": {"word": "serendipity"},
    "tool_result": "{\"word\": \"serendipity\", \"pronunciation\": \"/ˌser.ənˈdɪp.ə.ti/\", ...}",
    "duration_ms": 1523.45,
    "status": "success",
    "user_id": 42,
    "session_id": "session-abc123"
  }
}
```

### Log Aggregation Query Examples

```sql
-- Find all calls in a trace
SELECT * FROM logs WHERE trace_id = '550e8400-...' ORDER BY timestamp;

-- Tool call latency percentiles
SELECT 
  tool_name,
  percentile_cont(0.95) WITHIN GROUP (ORDER BY duration_ms) as p95
FROM tool_calls
WHERE timestamp > NOW() - INTERVAL '1 hour'
GROUP BY tool_name;

-- Error rate by tool
SELECT 
  tool_name,
  COUNT(*) FILTER (WHERE status = 'error') * 100.0 / COUNT(*) as error_rate
FROM tool_calls
GROUP BY tool_name;

-- LLM token usage by user
SELECT 
  user_id,
  SUM(total_tokens) as tokens,
  COUNT(*) as calls
FROM llm_calls
WHERE timestamp > NOW() - INTERVAL '1 day'
GROUP BY user_id
ORDER BY tokens DESC;
```

### Configuration

```bash
# Logging level for secretary agent
LOG_LEVEL_SECRETARY=INFO

# Enable detailed trace logging (includes full prompts/responses)
TRACE_DETAILED=false

# Log destination (stdout, file, or both)
LOG_OUTPUT=stdout

# Structured log format (json or text)
LOG_FORMAT=json
```

### Integration with Existing Logging

```python
# app/services/secretary_agent/__init__.py
import logging
import json

class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logs."""
    
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        
        # Add extra fields (tool_call, llm_call)
        if hasattr(record, 'tool_call'):
            log_data["tool_call"] = record.tool_call
        if hasattr(record, 'llm_call'):
            log_data["llm_call"] = record.llm_call
            
        return json.dumps(log_data, default=str)

# Configure logger
logger = logging.getLogger("secretary_agent")
handler = logging.StreamHandler()
handler.setFormatter(StructuredFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

---

## Living Documentation (活文档) - 可理解性

### Code Documentation Requirements

**Docstrings**: Every public function MUST have a docstring with:
- One-line summary
- Parameters with types and descriptions
- Return value description
- Possible exceptions
- Example usage (for complex functions)

```python
async def chat(
    self, 
    message: str, 
    session_id: str | None = None
) -> AsyncIterator[ChatChunk]:
    """
    Send a message to the Personal Secretary and stream the response.
    
    Args:
        message: User's input message
        session_id: Optional session ID for conversation continuity.
                   If not provided, creates a new session.
    
    Yields:
        ChatChunk: Streaming response chunks (tokens, tool calls, done)
    
    Raises:
        AuthenticationError: If user is not authenticated
        RateLimitError: If user exceeds rate limit
    
    Example:
        async for chunk in agent.chat("What's the weather?"):
            print(chunk.content, end="")
    """
```

**Comments**: Explain "WHY", not "WHAT"

```python
# ❌ Bad: Repeats what code does
# Loop through messages
for msg in messages:

# ✅ Good: Explains design decision
# Use sliding window to limit context tokens
# Why 20 messages? Balances context quality vs API cost
# Tested: 10 messages = poor context, 50 = too expensive
for msg in messages[-20:]:
```

### Architecture Documentation

Generate with each release:

1. **System Architecture Diagram** (Mermaid)
2. **Data Flow Diagram** (Request → Response path)
3. **Component Responsibilities** table

### Runbook (RUNBOOK.md)

Required sections:
1. **Quick Start**: One-command deployment
2. **Health Check**: How to verify service is running
3. **Common Issues**: Problem → Cause → Solution matrix
4. **Monitoring**: Key metrics and what they mean
5. **Rollback**: How to revert to previous version

### Documentation Checklist (Before Release)

- [ ] All public functions have docstrings
- [ ] Complex logic has "why" comments
- [ ] Architecture diagram is up-to-date
- [ ] RUNBOOK.md covers 5+ common issues
- [ ] README includes quick start guide
- [ ] API documentation (OpenAPI) is generated

---

## Migration Plan

- Add new tables via Alembic migration; no changes to existing tables.
- Add new dependencies (`langchain`, `langchain-openai`) to `pyproject.toml`.
- No data migration required.

---

## Self-Hosted LLM & SSL Configuration

The agent fully supports self-hosted LLMs (vLLM, Ollama, text-generation-inference, etc.) including those with self-signed certificates.

### Configuration

The existing settings are reused:

```python
# .env or environment variables
LLM_BASE_URL=https://my-local-llm.internal:8443/v1
LLM_API_KEY=my-api-key
LLM_MODEL=my-local-model
LLM_VERIFY_SSL=false  # Disable SSL verification for self-signed certs
LLM_TIMEOUT=60.0      # Increase timeout for slower local models
```

### LangChain Implementation

LangChain's `ChatOpenAI` is configured with a custom httpx client to respect `LLM_VERIFY_SSL`:

```python
import httpx
from langchain_openai import ChatOpenAI
from app.core.config import settings

# Create HTTP client with SSL verification toggle
http_client = httpx.AsyncClient(
    verify=settings.LLM_VERIFY_SSL,  # False for self-signed certs
    timeout=httpx.Timeout(settings.LLM_TIMEOUT)
)

# Create LangChain ChatModel with custom client
llm = ChatOpenAI(
    model=settings.LLM_MODEL,
    openai_api_key=settings.LLM_API_KEY,
    openai_api_base=settings.LLM_BASE_URL,
    http_async_client=http_client,
    streaming=True,
)
```

### Supported Self-Hosted LLM Backends

| Backend | Compatibility | Notes |
|---------|--------------|-------|
| **vLLM** | Full | OpenAI-compatible API |
| **Ollama** | Full | Use `http://localhost:11434/v1` |
| **text-generation-inference** | Full | HuggingFace TGI |
| **LocalAI** | Full | OpenAI-compatible |
| **LM Studio** | Full | Local GUI with API |
| **llama.cpp server** | Partial | May need prompt adjustment |

### Security Considerations

- **Development Only**: Disabling SSL verification (`LLM_VERIFY_SSL=false`) should only be used for local/development self-hosted LLMs
- **Production**: For production self-hosted LLMs, use proper CA-signed certificates or add your CA to the system trust store
- **Network Isolation**: Self-hosted LLMs with disabled SSL verification should run on isolated networks

---

## External Dependencies

- **[LangChain](https://github.com/langchain-ai/langchain)** (MIT): LLM application framework for Python. Used for agent orchestration, tools, and memory management.
- **[langchain-openai](https://github.com/langchain-ai/langchain)** (MIT): LangChain integration with OpenAI and OpenAI-compatible APIs.

---

## Open Questions

- Should the agent support voice input/output? (Defer to future enhancement)
- Should tools be user-configurable (enable/disable per user)? (Start with global config)
- Should the agent have access to user's existing recommendations? (Optional: add as read-only tool)
