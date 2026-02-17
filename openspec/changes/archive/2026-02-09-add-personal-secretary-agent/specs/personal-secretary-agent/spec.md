# personal-secretary-agent Specification (Delta)

## ADDED Requirements

### Requirement: Personal Secretary agent provides conversational AI assistance

The system SHALL provide a conversational AI agent ("Personal Secretary") that accepts user messages via a chat interface and responds using LLM with access to configurable tools, maintaining conversation history within sessions.

#### Scenario: User sends a message and receives a response

- **WHEN** the user sends a chat message to the Personal Secretary
- **THEN** the system responds with an AI-generated message that addresses the user's query

#### Scenario: Agent maintains conversation context within a session

- **WHEN** the user sends multiple messages within the same session
- **THEN** the system maintains conversation history and provides contextually relevant responses

#### Scenario: Streaming response for better user experience

- **WHEN** the user sends a message
- **THEN** the system streams the response tokens as they are generated, providing real-time feedback

### Requirement: Learn English words with Chinese explanation and pronunciation

The system SHALL provide a `learn_word` tool that explains English words with Chinese translation, IPA pronunciation, part of speech, usage examples, and synonyms.

#### Scenario: User asks to learn an English word

- **WHEN** the user inputs an English word (e.g., "serendipity")
- **THEN** the system returns:
  - Chinese explanation (中文解释)
  - Pronunciation in IPA notation (e.g., /ˌserənˈdɪpɪti/)
  - Part of speech (noun, verb, etc.)
  - At least 2 usage examples
  - Synonyms

#### Scenario: User confirms to save word to learning records

- **WHEN** the user confirms to save the word learning
- **THEN** the system persists the word and response to the learning_records table

### Requirement: Learn English sentences with Chinese translation and grammar

The system SHALL provide a `learn_sentence` tool that explains English sentences with Chinese translation, grammar points, key phrases, and context for usage.

#### Scenario: User asks to learn an English sentence

- **WHEN** the user inputs an English sentence (e.g., "The early bird catches the worm")
- **THEN** the system returns:
  - Chinese translation (中文翻译)
  - Grammar points and notes
  - Key phrases identified
  - Context for when to use this sentence
  - Similar expressions

#### Scenario: User confirms to save sentence to learning records

- **WHEN** the user confirms to save the sentence learning
- **THEN** the system persists the sentence and response to the learning_records table

### Requirement: Learn tech topics with structured learning plan

The system SHALL provide a `learn_topic` tool that generates comprehensive learning plans for technical topics, including introduction, key concepts, step-by-step learning path, recommended resources, prerequisites, and time estimates.

#### Scenario: User asks to learn a tech topic

- **WHEN** the user inputs a tech topic (e.g., "Kubernetes", "WebRTC", "GraphQL")
- **THEN** the system returns:
  - Brief introduction (2-3 sentences)
  - Key concepts with descriptions and importance
  - Step-by-step learning path with duration estimates
  - Recommended resources categorized by type (tutorial, documentation, course, video, book)
  - Prerequisites (what to learn first)
  - Overall time estimate (e.g., "2-3 weeks for basics")
  - Difficulty level (beginner, intermediate, advanced)

#### Scenario: User confirms to save topic learning plan

- **WHEN** the user confirms to save the topic learning plan
- **THEN** the system persists the topic and learning plan to the learning_records table

### Requirement: Answer questions and optionally save Q&A

The system SHALL provide an `answer_question` tool that answers general questions with explanations, and allows users to save the Q&A to learning records.

#### Scenario: User asks a question

- **WHEN** the user asks a question (e.g., "How does OAuth2 work?")
- **THEN** the system provides a clear answer with explanation

#### Scenario: User confirms to save Q&A

- **WHEN** the user confirms to save the question and answer
- **THEN** the system persists the Q&A to the learning_records table with type "question"

### Requirement: Turn ideas into executable plans

The system SHALL provide a `plan_idea` tool that transforms user ideas into structured, executable action plans.

#### Scenario: User shares an idea

- **WHEN** the user shares an idea (e.g., "Build a habit tracker app")
- **THEN** the system returns a structured action plan with numbered steps

#### Scenario: User confirms to save idea and plan

- **WHEN** the user confirms to save the idea and plan
- **THEN** the system persists the idea and plan to the learning_records table with type "idea"

### Requirement: Learn from web articles with bilingual translation and mindmap

The system SHALL provide a `learn_article` tool that processes URLs to fetch articles, convert to markdown, translate to bilingual format (English + Chinese), generate summary mindmap in PlantUML format, and render to PNG image.

#### Scenario: User provides a URL to learn from

- **WHEN** the user inputs a URL (e.g., "https://example.com/article-about-kubernetes")
- **THEN** the system:
  - Fetches the article content
  - Converts HTML to clean markdown (removing ads, navigation)
  - Translates to bilingual format (English paragraph followed by Chinese translation)
  - Generates a summary with key points
  - Generates a PlantUML mindmap script
  - Renders the mindmap to PNG image
  - Returns the complete ArticleResponse

#### Scenario: Bilingual translation preserves original and adds Chinese

- **WHEN** the article is in English
- **THEN** the system keeps the original English text and adds Chinese translation after each paragraph, preserving code blocks untranslated

#### Scenario: Article already in Chinese skips translation

- **WHEN** the article is already in Chinese
- **THEN** the system skips translation and proceeds with summary and mindmap generation

#### Scenario: Mindmap rendered to PNG

- **WHEN** the PlantUML mindmap script is generated
- **THEN** the system renders it to a PNG image and stores it for display

#### Scenario: User confirms to save article learning

- **WHEN** the user confirms to save the article learning
- **THEN** the system persists the URL, original content, bilingual content, summary, mindmap script, and mindmap image path to the learning_records table with type "article"

### Requirement: Learning records persistence and management

The system SHALL persist learning records (words, sentences, topics, Q&A, ideas) to a database table when the user confirms, and provide APIs to list, search, and delete records.

#### Scenario: List learning records with filters

- **WHEN** the user requests their learning record list
- **THEN** the system returns a paginated list of records, filterable by type (word, sentence, topic, question, idea)

#### Scenario: Search learning records

- **WHEN** the user searches learning records with a keyword
- **THEN** the system returns records where user_input or response_payload matches the keyword

#### Scenario: Delete learning record

- **WHEN** the user deletes a learning record
- **THEN** the system soft-deletes the record (sets deleted_at timestamp)

### Requirement: Personal Secretary uses tools to perform actions

The system SHALL enable the Personal Secretary agent to use registered tools (functions) to perform actions such as getting weather, managing notes, and performing calculations when the user's request requires external information or actions.

#### Scenario: Agent uses weather tool when asked about weather

- **WHEN** the user asks "What's the weather in Beijing?"
- **THEN** the system invokes the weather tool with the specified city and includes the weather information in the response

#### Scenario: Agent uses calculator tool for math

- **WHEN** the user asks "What is 15% of 230?"
- **THEN** the system invokes the calculator tool and returns the computed result

#### Scenario: Agent decides when to use tools

- **WHEN** the user sends a message that can be answered directly from the LLM's knowledge
- **THEN** the system responds without invoking any tools

#### Scenario: Tool usage is visible to the user

- **WHEN** the agent uses a tool during response generation
- **THEN** the system indicates to the user which tool was used and with what parameters

### Requirement: Chat sessions persist conversation history

The system SHALL persist chat sessions and messages to the database, allowing users to continue conversations and review past interactions.

#### Scenario: New session is created for first message

- **WHEN** the user sends a message without specifying a session ID
- **THEN** the system creates a new chat session and associates the message with it

#### Scenario: Existing session continues

- **WHEN** the user sends a message with an existing session ID
- **THEN** the system adds the message to the existing session and uses prior messages as context

#### Scenario: User can list their sessions

- **WHEN** the user requests their chat session list
- **THEN** the system returns a paginated list of sessions with titles and timestamps

#### Scenario: User can delete a session

- **WHEN** the user deletes a chat session
- **THEN** the system removes the session and all associated messages

### Requirement: Available tools are discoverable

The system SHALL provide an endpoint listing all tools available to the Personal Secretary agent, including their names, descriptions, and parameter schemas.

#### Scenario: List available tools

- **WHEN** the user requests the list of available tools
- **THEN** the system returns all registered tools with their descriptions and input schemas

### Requirement: Authentication required for chat

The system SHALL require authentication for all Personal Secretary endpoints, associating sessions and messages with the authenticated user.

#### Scenario: Unauthenticated request is rejected

- **WHEN** a chat request is made without valid authentication
- **THEN** the system returns a 401 Unauthorized error

#### Scenario: User can only access their own sessions

- **WHEN** a user attempts to access or delete another user's session
- **THEN** the system returns a 404 Not Found error (not revealing existence)

### Requirement: Weather tool integration

The system SHALL provide a weather tool that leverages the existing weather service to provide current weather information for specified cities.

#### Scenario: Weather tool returns current conditions

- **WHEN** the weather tool is invoked with a city name or AD code
- **THEN** the tool returns current temperature, weather conditions, and other relevant information

#### Scenario: Weather tool handles invalid city gracefully

- **WHEN** the weather tool is invoked with an unrecognized city
- **THEN** the tool returns an error message that the agent can communicate to the user

### Requirement: DateTime tool for time-related queries

The system SHALL provide a datetime tool that returns the current date and time in the user's timezone or a specified timezone.

#### Scenario: DateTime tool returns current time

- **WHEN** the datetime tool is invoked
- **THEN** the tool returns the current date, time, and day of week

### Requirement: Support for self-hosted LLMs with self-signed certificates

The system SHALL support self-hosted LLM backends (vLLM, Ollama, text-generation-inference, etc.) including those using self-signed SSL certificates, by respecting the `LLM_VERIFY_SSL` configuration setting.

#### Scenario: Agent works with self-hosted LLM using self-signed certificate

- **WHEN** `LLM_VERIFY_SSL` is set to `false` and `LLM_BASE_URL` points to a self-hosted LLM with a self-signed certificate
- **THEN** the system successfully connects to the LLM and processes chat requests without SSL verification errors

#### Scenario: Agent verifies SSL by default

- **WHEN** `LLM_VERIFY_SSL` is not set or set to `true`
- **THEN** the system verifies SSL certificates when connecting to the LLM endpoint

### Requirement: Calculator tool for mathematical operations

The system SHALL provide a calculator tool that evaluates mathematical expressions and returns the result.

#### Scenario: Calculator handles basic arithmetic

- **WHEN** the calculator tool receives an expression like "15 * 23 + 7"
- **THEN** the tool returns the computed result "352"

#### Scenario: Calculator handles percentage calculations

- **WHEN** the calculator tool receives "15% of 230"
- **THEN** the tool parses and computes the result "34.5"

#### Scenario: Calculator rejects invalid expressions

- **WHEN** the calculator tool receives an invalid or unsafe expression
- **THEN** the tool returns an error message indicating the expression could not be evaluated
