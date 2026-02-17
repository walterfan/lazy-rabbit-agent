# Specification: Medical Paper Writing Agent

## ADDED Requirements

### Requirement: Multi-Agent Paper Writing System

The system SHALL provide a multi-agent AI assistant for writing medical research papers following established guidelines (CONSORT, STROBE, PRISMA).

#### Scenario: Create RCT paper writing task

- **GIVEN** an authenticated user
- **WHEN** the user submits a request to create an RCT paper task with:
  - Research question: "Compare amlodipine vs losartan for stage 2 HTN"
  - Paper type: RCT
  - Study design details
- **THEN** the system SHALL create a new task
- **AND** return a task ID
- **AND** begin the workflow execution

#### Scenario: Literature search phase

- **GIVEN** an active paper writing task
- **WHEN** the Literature Agent receives a search request
- **THEN** the agent SHALL search PubMed for relevant references
- **AND** return structured reference data including PMID, title, authors, journal, year
- **AND** include relevance scores for each reference

#### Scenario: Statistical analysis phase

- **GIVEN** literature search is complete
- **WHEN** the Stats Agent receives analysis request with study data
- **THEN** the agent SHALL perform appropriate statistical tests
- **AND** return results with p-values, confidence intervals, and effect sizes
- **AND** include sensitivity analysis if applicable

#### Scenario: IMRAD writing phase

- **GIVEN** literature and statistics are complete
- **WHEN** the Writer Agent receives writing request
- **THEN** the agent SHALL write manuscript in IMRAD format (Introduction, Methods, Results, Discussion)
- **AND** include citations for all referenced claims
- **AND** use academic language

---

### Requirement: Compliance Checking

The system SHALL verify manuscript compliance with standard reporting guidelines.

#### Scenario: CONSORT compliance check for RCT

- **GIVEN** a completed manuscript for an RCT
- **WHEN** the Compliance Agent checks against CONSORT 2025
- **THEN** the system SHALL evaluate all 25 checklist items
- **AND** classify each as PASS, WARN, or FAIL
- **AND** return suggestions for failed items

#### Scenario: Compliance failure triggers revision

- **GIVEN** a compliance check with FAIL items
- **WHEN** the Supervisor reviews the compliance report
- **THEN** the system SHALL route the task to revision phase
- **AND** send failed items to Writer Agent for revision
- **AND** re-run compliance check after revision

#### Scenario: Maximum revision rounds

- **GIVEN** a task in revision phase
- **WHEN** revision rounds exceed 3
- **THEN** the system SHALL mark the task as requiring manual intervention
- **AND** notify the user
- **AND** preserve all generated content

---

### Requirement: A2A Communication Contract

The system SHALL use structured A2A (Agent-to-Agent) messages for inter-agent communication.

#### Scenario: A2A message structure

- **GIVEN** any agent communication
- **WHEN** a message is sent between agents
- **THEN** the message SHALL include:
  - `protocol`: "a2a.v1"
  - `id`: unique message ID
  - `correlation_id`: task correlation ID
  - `sender`: sending agent name
  - `receiver`: receiving agent name
  - `intent`: action to perform
  - `status`: pending/ok/error
  - `metrics`: latency, token counts

#### Scenario: Error classification and retry

- **GIVEN** a tool execution failure
- **WHEN** the error is classified as recoverable (e.g., TOOL_ERROR, TIMEOUT)
- **THEN** the system SHALL retry with exponential backoff
- **AND** log each retry attempt
- **AND** fail after maximum retries (3 for TOOL_ERROR, 2 for TIMEOUT)

---

### Requirement: Workflow Orchestration

The system SHALL orchestrate the paper writing workflow using a declarative DAG (Directed Acyclic Graph).

#### Scenario: Standard workflow execution

- **GIVEN** a new paper writing task
- **WHEN** the workflow executes
- **THEN** the system SHALL follow the sequence:
  1. Literature search → Supervisor review
  2. Statistical analysis → Supervisor review
  3. IMRAD writing (parallel sections) → Merge
  4. Compliance check → Supervisor review
  5. Finalize or Revise

#### Scenario: Parallel section writing

- **GIVEN** literature and statistics are complete
- **WHEN** the writing phase begins
- **THEN** Introduction, Methods, Results, Discussion MAY be written in parallel
- **AND** sections SHALL be merged after completion

#### Scenario: Workflow state persistence

- **GIVEN** a running workflow
- **WHEN** the system restarts or fails
- **THEN** the workflow state SHALL be recoverable from the database
- **AND** the task SHALL resume from the last checkpoint

---

### Requirement: Task Management API

The system SHALL provide REST API endpoints for task management.

#### Scenario: Create task

- **GIVEN** an authenticated user
- **WHEN** `POST /api/v1/medical-paper/create` is called with valid input
- **THEN** the system SHALL return 201 Created
- **AND** return task ID and initial status

#### Scenario: Get task status

- **GIVEN** an existing task owned by the user
- **WHEN** `GET /api/v1/medical-paper/{task_id}` is called
- **THEN** the system SHALL return task details including:
  - Current status
  - Current step
  - Progress percentage
  - Generated content (if any)

#### Scenario: Stream task progress

- **GIVEN** an active task
- **WHEN** `GET /api/v1/medical-paper/{task_id}/stream` is called
- **THEN** the system SHALL return Server-Sent Events
- **AND** emit events for each workflow step completion
- **AND** emit partial content as it's generated

#### Scenario: Submit revision

- **GIVEN** a task in revision phase
- **WHEN** `POST /api/v1/medical-paper/{task_id}/revise` is called with feedback
- **THEN** the system SHALL incorporate feedback
- **AND** trigger re-execution of affected steps

#### Scenario: Access control

- **GIVEN** a task owned by user A
- **WHEN** user B attempts to access the task
- **THEN** the system SHALL return 403 Forbidden

---

### Requirement: Prompt Management

The system SHALL externalize all prompts to YAML files with version support.

#### Scenario: Load versioned prompt

- **GIVEN** a prompt file `prompts/agents/writer/system.v1.yaml`
- **WHEN** Writer Agent is initialized
- **THEN** the system SHALL load the YAML file
- **AND** use the specified version's prompt content

#### Scenario: Prompt template rendering

- **GIVEN** a prompt template with placeholders
- **WHEN** the prompt is rendered with context
- **THEN** the system SHALL replace placeholders with actual values
- **AND** preserve prompt structure

---

### Requirement: Observability

The system SHALL provide comprehensive observability for monitoring and debugging.

#### Scenario: Metrics collection

- **GIVEN** the medical paper agent is running
- **WHEN** tasks are processed
- **THEN** the system SHALL record:
  - Task count by status and paper type
  - Task duration histogram
  - Agent call count and latency
  - Compliance scores
  - Revision round distribution

#### Scenario: A2A message audit trail

- **GIVEN** a paper writing task
- **WHEN** agents communicate
- **THEN** all A2A messages SHALL be persisted to the database
- **AND** include input/output payloads
- **AND** include timing metrics

#### Scenario: Error logging

- **GIVEN** an error occurs during workflow execution
- **WHEN** the error is caught
- **THEN** the system SHALL log:
  - Error type and message
  - Task ID and correlation ID
  - Current workflow step
  - Stack trace (if applicable)
- **AND** NOT log sensitive data (API keys, user passwords)

---

### Requirement: Paper Templates

The system SHALL support multiple paper types with corresponding templates and compliance checklists.

#### Scenario: RCT template

- **GIVEN** paper type is RCT (Randomized Controlled Trial)
- **WHEN** the workflow is configured
- **THEN** the system SHALL use:
  - CONSORT 2025 compliance checklist
  - RCT-specific IMRAD structure
  - Appropriate statistical tests (t-test, Chi-square, survival analysis)

#### Scenario: Meta-analysis template

- **GIVEN** paper type is META_ANALYSIS
- **WHEN** the workflow is configured
- **THEN** the system SHALL use:
  - PRISMA compliance checklist
  - Meta-analysis specific structure
  - Heterogeneity and publication bias analysis

#### Scenario: Cohort study template

- **GIVEN** paper type is COHORT
- **WHEN** the workflow is configured
- **THEN** the system SHALL use:
  - STROBE compliance checklist
  - Cohort study specific structure
  - Appropriate observational study statistics

---

### Requirement: Frontend Workspace

The system SHALL provide a web-based workspace for paper writing tasks.

#### Scenario: Display task progress

- **GIVEN** a user viewing their paper task
- **WHEN** the workspace loads
- **THEN** the system SHALL display:
  - Workflow progress timeline
  - Current step indicator
  - Generated content preview
  - Literature references panel
  - Compliance status panel

#### Scenario: Real-time updates

- **GIVEN** a user viewing an active task
- **WHEN** the workflow progresses
- **THEN** the workspace SHALL update in real-time via SSE
- **AND** show new content as it's generated
- **AND** update progress indicators

#### Scenario: Manual content editing

- **GIVEN** a user viewing generated content
- **WHEN** the user edits manuscript sections
- **THEN** the system SHALL preserve user edits
- **AND** allow re-running compliance check with edited content
