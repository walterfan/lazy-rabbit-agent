# AI-Driven Workflow Engine - High Level Design (Mermaid Diagrams)

**Project:** Lazy Rabbit Agent - AI Workflow Automation
**Version:** 1.0 (Mermaid Edition)
**Date:** 2025-11-18
**Document Type:** High Level Design with Mermaid Diagrams
**Status:** Design Review

---

## Table of Contents

1. [System Architecture Diagrams](#1-system-architecture-diagrams)
2. [Innovation Points Diagrams](#2-innovation-points-diagrams)
3. [Core Components Diagrams](#3-core-components-diagrams)
4. [Data Architecture Diagrams](#4-data-architecture-diagrams)
5. [Integration Architecture Diagrams](#5-integration-architecture-diagrams)
6. [AI/ML Architecture Diagrams](#6-aiml-architecture-diagrams)
7. [Deployment Diagrams](#7-deployment-diagrams)

---

## 1. System Architecture Diagrams

### 1.1 Layered Architecture Overview

```mermaid
graph TB
    subgraph "PRESENTATION LAYER"
        VueUI[Vue.js Dashboard]
        RestAPI[REST API Gateway]
        WebSocket[WebSocket Streaming]
        GraphQL[GraphQL - Future]
    end

    subgraph "AI INTELLIGENCE LAYER"
        NLTranslator[NL Translator<br/>GPT-4]
        SmartDecision[Smart Decision Engine<br/>AI]
        AutoRecovery[Auto Recovery Engine<br/>Pattern Recognition]
        Optimization[Optimization Advisor<br/>AI]
        AnomalyDetector[Anomaly Detector]
        WorkflowValidator[Workflow Validator<br/>Security + Logic]
    end

    subgraph "WORKFLOW ORCHESTRATION LAYER"
        WorkflowParser[Workflow Parser & DSL]
        ExecutionEngine[Execution Engine<br/>Core]
        ParallelExecutor[Parallel Executor<br/>asyncio + Celery]
        StateManager[State Manager<br/>Redis+DB]
        EventQueue[Event Queue<br/>RabbitMQ]
        Scheduler[Scheduler<br/>Cron]
    end

    subgraph "INTEGRATION & DATA LAYER"
        LLMService[LLM Service<br/>OpenAI API]
        PostgreSQL[PostgreSQL<br/>Primary DB]
        RedisCache[Redis Cache<br/>State + Cache]
        CeleryWorkers[Celery Workers<br/>Task Queue]
        ExternalAPIs[External APIs<br/>Webhooks]
        Monitoring[Monitoring<br/>Prometheus+Grafana]
    end

    VueUI --> RestAPI
    VueUI --> WebSocket
    RestAPI --> NLTranslator
    RestAPI --> SmartDecision

    NLTranslator --> WorkflowParser
    SmartDecision --> ExecutionEngine
    AutoRecovery --> ExecutionEngine
    Optimization --> WorkflowParser

    WorkflowParser --> StateManager
    ExecutionEngine --> StateManager
    ExecutionEngine --> EventQueue
    ParallelExecutor --> CeleryWorkers

    StateManager --> RedisCache
    StateManager --> PostgreSQL
    ExecutionEngine --> LLMService
    EventQueue --> CeleryWorkers

    style NLTranslator fill:#e1f5ff
    style SmartDecision fill:#e1f5ff
    style AutoRecovery fill:#e1f5ff
    style Optimization fill:#e1f5ff
```

### 1.2 Request Flow - Workflow Creation

```mermaid
sequenceDiagram
    participant User
    participant APIGW as API Gateway
    participant NLT as NL Translator
    participant LLM as LLM API (GPT-4)
    participant Validator as Workflow Validator
    participant Parser as Workflow Parser
    participant DB as Database

    User->>APIGW: POST /workflows<br/>"Create workflow for customer onboarding"
    APIGW->>APIGW: Authentication
    APIGW->>APIGW: Rate Limiting
    APIGW->>APIGW: Validation

    APIGW->>NLT: translate(nl_description)
    NLT->>NLT: 1. Parse intent
    NLT->>LLM: API call with prompt
    LLM-->>NLT: Generated DSL
    NLT->>NLT: 3. Validate syntax
    NLT-->>APIGW: workflow_dsl

    APIGW->>Validator: validate(workflow_dsl)
    Validator->>Validator: Security scan
    Validator->>Validator: Logic check
    Validator->>Validator: Optimize graph
    Validator-->>APIGW: validation_result

    APIGW->>Parser: parse(workflow_dsl)
    Parser->>Parser: Parse DSL
    Parser->>Parser: Build graph
    Parser->>Parser: Create states
    Parser-->>APIGW: parsed_workflow

    APIGW->>DB: persist(workflow)
    DB-->>APIGW: workflow_id
    APIGW-->>User: 201 Created<br/>{workflow_id, dsl, status}
```

### 1.3 Request Flow - Workflow Execution

```mermaid
sequenceDiagram
    participant User
    participant APIGW as API Gateway
    participant Engine as Execution Engine
    participant SM as State Manager
    participant DE as Decision Engine
    participant CB as Callback
    participant Recovery as Auto Recovery
    participant Cache as Redis Cache
    participant DB as Database
    participant WS as WebSocket

    User->>APIGW: POST /workflows/{id}/execute
    APIGW->>Engine: execute_workflow(workflow_id, context)
    Engine->>SM: load_workflow(workflow_id)
    SM->>DB: SELECT workflow
    DB-->>SM: workflow_definition
    SM-->>Engine: workflow

    loop State Transition Loop
        Engine->>Engine: Enter state
        Engine->>DE: evaluate_condition(condition, context)
        DE-->>Engine: {decision, reasoning, confidence}

        Engine->>CB: execute_callback()

        alt Callback Success
            CB-->>Engine: result
            Engine->>SM: update_state(new_state)
            SM->>Cache: SET state
            SM->>DB: INSERT state_transition
            SM->>WS: notify(state_change)
        else Callback Error
            CB-->>Engine: ERROR
            Engine->>Recovery: handle_error(error, context)
            Recovery->>Recovery: Analyze error
            Recovery->>Recovery: Select strategy (RETRY)
            Recovery-->>Engine: {strategy, reasoning}
            Engine->>CB: execute_callback() [retry]
            CB-->>Engine: SUCCESS
        end

        Engine->>Engine: Check if end state
    end

    Engine-->>APIGW: execution_result
    APIGW-->>User: 200 OK<br/>{execution_id, status, states_visited}
```

### 1.4 Data Flow Architecture

```mermaid
graph LR
    UserInput[User Input]

    subgraph "Data Paths"
        HotPath[Hot Path<br/>Redis<br/>• State<br/>• Context<br/>• Locks]
        ColdPath[Cold Path<br/>PostgreSQL<br/>• Workflows<br/>• Executions<br/>• Audit Logs]
    end

    ExecutionEngine[Execution Engine<br/>State Machine]

    subgraph "External Services"
        LLM[LLM Service]
        ExtAPIs[External APIs]
        TaskQueue[Task Queue]
    end

    Metrics[Metrics & Logging<br/>Prometheus/ELK]

    UserInput --> HotPath
    UserInput --> ColdPath
    HotPath --> ExecutionEngine
    ColdPath --> ExecutionEngine

    ExecutionEngine --> LLM
    ExecutionEngine --> ExtAPIs
    ExecutionEngine --> TaskQueue

    LLM --> Metrics
    ExtAPIs --> Metrics
    TaskQueue --> Metrics

    style HotPath fill:#ffebee
    style ColdPath fill:#e3f2fd
    style ExecutionEngine fill:#fff3e0
```

---

## 2. Innovation Points Diagrams

### 2.1 Natural Language Translation Pipeline

```mermaid
graph TD
    Start[Natural Language Input]

    Start --> IntentAnalysis[Intent Analysis<br/>GPT-4<br/>Extract actions, Identify logic, Determine flow]

    IntentAnalysis --> StructBuilder[Structure Builder<br/>Create states, Define edges, Add conditions]

    StructBuilder --> DSLGen[DSL Generator<br/>Format syntax, Optimize graph, Add metadata]

    DSLGen --> Validator[Validator<br/>Syntax check, Security scan, Logic verify]

    Validator --> End[Executable DSL]

    style IntentAnalysis fill:#e1f5ff
    style StructBuilder fill:#f3e5f5
    style DSLGen fill:#e8f5e9
    style Validator fill:#fff3e0
```

### 2.2 Smart Decision Engine Architecture

```mermaid
graph TD
    Context[Context Input]

    Context --> RuleBased[Rule-Based Evaluator<br/>Fast, Deterministic]
    Context --> MLPattern[ML Pattern Matcher<br/>Historical Data]
    Context --> LLMReasoning[LLM Reasoning<br/>Complex, Contextual]

    RuleBased --> DecisionFusion[Decision Fusion]
    MLPattern --> DecisionFusion
    LLMReasoning --> DecisionFusion

    DecisionFusion --> ConfidenceScorer[Confidence Scorer]

    ConfidenceScorer --> Explainer[Explainer<br/>Why this decision?]

    Explainer --> FinalDecision[Final Decision<br/>+ Reasoning]

    style RuleBased fill:#ffebee
    style MLPattern fill:#e3f2fd
    style LLMReasoning fill:#e8f5e9
    style DecisionFusion fill:#fff3e0
```

### 2.3 Auto-Recovery Flow

```mermaid
graph TD
    Error[Workflow Error Occurs]

    Error --> Captured[Error Captured]

    Captured --> Classifier[Error Classifier<br/>Type: Network, Severity: Medium, Context: Email]

    Classifier --> Historical[Historical Analyzer<br/>Similar errors? Past success rate? Best strategy?]

    Historical --> AISelector[AI Strategy Selector LLM<br/>Options: 1. Retry 85%, 2. Skip 60%, 3. Fallback 70%]

    AISelector --> Execute[Execute Recovery<br/>Apply strategy, Monitor result, Learn pattern]

    Execute --> Success{Success?}

    Success -->|Yes| Continue[Continue Workflow]
    Success -->|No| Escalate[Escalate to Human]

    style AISelector fill:#e1f5ff
    style Execute fill:#e8f5e9
    style Success fill:#fff3e0
```

### 2.4 Continuous Optimization Cycle

```mermaid
graph TD
    Execute[Execute Workflow]

    Execute --> Collect[Collect Metrics<br/>Duration, Errors, Costs]

    Collect --> AIAnalysis[AI Analysis Weekly Batch<br/>Bottlenecks? Parallel ops? Cache hits?]

    AIAnalysis --> Generate[Generate Suggestions<br/>Optimization 1, Optimization 2, Impact estimate]

    Generate --> HumanReview[Human Review & Approval]

    HumanReview --> ABTest[A/B Test<br/>50/50 split]

    ABTest --> Measure[Measure Impact<br/>2 weeks]

    Measure --> Decision{Positive<br/>Impact?}

    Decision -->|Yes| Rollout[Roll Out]
    Decision -->|No| Discard[Discard]

    Rollout --> Execute

    style AIAnalysis fill:#e1f5ff
    style Generate fill:#f3e5f5
    style ABTest fill:#fff3e0
```

---

## 3. Core Components Diagrams

### 3.1 Class Diagram - Core Components

```mermaid
classDiagram
    class EnhancedWorkflowEngine {
        -Session db
        -LLMService llm_service
        -RedisCache cache
        -WorkflowTranslator translator
        -SmartDecisionEngine decision_engine
        -AutoRecoveryEngine recovery_engine
        -OptimizationAdvisor optimizer
        +create_workflow_from_nl()
        +execute_workflow()
        +execute_parallel_tasks()
        +optimize_workflow()
    }

    class WorkflowTranslator {
        +translate(nl_description, context)
        +explain(workflow_dsl)
    }

    class SmartDecisionEngine {
        +evaluate_condition(condition, context)
        +suggest_next_state(current_state, context)
    }

    class AutoRecoveryEngine {
        +handle_error(error, workflow_id, state)
        +apply_recovery(action, workflow_id)
    }

    class OptimizationAdvisor {
        +analyze_workflow(workflow_id)
        +suggest_optimizations(workflow_id)
    }

    class StateManager {
        +get_current_state(workflow_id)
        +update_state(execution_id, new_state)
        +get_state_history(execution_id)
    }

    class LLMService {
        -str api_key
        -str model
        -LLMResponseCache cache
        +invoke(prompt, temperature, max_tokens)
        +invoke_with_fallback()
        +track_usage()
    }

    EnhancedWorkflowEngine --> WorkflowTranslator
    EnhancedWorkflowEngine --> SmartDecisionEngine
    EnhancedWorkflowEngine --> AutoRecoveryEngine
    EnhancedWorkflowEngine --> OptimizationAdvisor
    EnhancedWorkflowEngine --> StateManager

    WorkflowTranslator --> LLMService
    SmartDecisionEngine --> LLMService
    AutoRecoveryEngine --> LLMService
    OptimizationAdvisor --> LLMService
    StateManager --> LLMService
```

### 3.2 Sequence Diagram - Workflow Execution with Error Recovery

```mermaid
sequenceDiagram
    participant User
    participant API
    participant Engine
    participant SM as StateManager
    participant DE as DecisionEngine
    participant CB as Callback
    participant Recovery

    User->>API: POST /execute
    API->>Engine: execute()

    Engine->>SM: load workflow
    SM-->>Engine: workflow

    Engine->>DE: evaluate_condition
    DE-->>Engine: {decision, reasoning}

    Engine->>CB: execute_callback()
    CB-->>Engine: ERROR

    Engine->>Recovery: handle_error()
    Recovery->>Recovery: Analyze error<br/>Select strategy
    Recovery-->>Engine: {strategy: RETRY}

    Engine->>CB: execute_callback() [retry]
    CB-->>Engine: SUCCESS

    Engine->>SM: update state
    SM-->>Engine: updated

    Engine-->>API: result
    API-->>User: 200 OK {result}
```

### 3.3 State Machine Diagram

```mermaid
stateDiagram-v2
    [*] --> PENDING: Start execution

    PENDING --> RUNNING: Initialize context<br/>Queue exec

    RUNNING --> TRANSITIONING: OK<br/>Execute state<br/>Call callback<br/>Evaluate
    RUNNING --> RECOVERING: ERROR

    RECOVERING --> RUNNING: SUCCESS<br/>Analyze<br/>AI recovery
    RECOVERING --> COMPLETED: FAILED

    TRANSITIONING --> RUNNING: Has next state<br/>Next state<br/>Update ctx
    TRANSITIONING --> COMPLETED: No next state

    COMPLETED --> [*]: Finalize<br/>Audit log<br/>Metrics
```

### 3.4 Component Diagram - AI Intelligence Layer

```mermaid
graph TB
    subgraph "AI Intelligence Layer"
        subgraph "WorkflowTranslator"
            NLParser[NL Parser]
            DSLGenerator[DSL Generator]
            Validator[Validator]
            NLParser --> DSLGenerator
            DSLGenerator --> Validator
        end

        subgraph "SmartDecisionEngine"
            RuleEngine[Rule Engine]
            MLMatcher[ML Matcher]
            LLMReasoner[LLM Reasoner]
            RuleEngine --> DecisionFuser[Decision Fuser]
            MLMatcher --> DecisionFuser
            LLMReasoner --> DecisionFuser
        end

        subgraph "AutoRecoveryEngine"
            ErrorAnalyzer[Error Analyzer]
            StrategySelector[Strategy Selector AI]
            RecoveryExecutor[Recovery Executor]
            ErrorAnalyzer --> StrategySelector
            StrategySelector --> RecoveryExecutor
        end

        subgraph "OptimizationAdvisor"
            MetricsCollector[Metrics Collector]
            AIAnalyzer[AI Analyzer<br/>Pattern Detection]
            SuggestionGen[Suggestion Generator]
            MetricsCollector --> AIAnalyzer
            AIAnalyzer --> SuggestionGen
        end
    end

    LLMServiceAPI[LLM Service<br/>OpenAI API]

    Validator --> LLMServiceAPI
    DecisionFuser --> LLMServiceAPI
    StrategySelector --> LLMServiceAPI
    AIAnalyzer --> LLMServiceAPI

    style WorkflowTranslator fill:#e1f5ff
    style SmartDecisionEngine fill:#f3e5f5
    style AutoRecoveryEngine fill:#e8f5e9
    style OptimizationAdvisor fill:#fff3e0
```

---

## 4. Data Architecture Diagrams

### 4.1 Entity-Relationship Diagram

```mermaid
erDiagram
    Users ||--o{ Workflows : owns
    Workflows ||--o{ WorkflowStates : contains
    Workflows ||--o{ WorkflowExecutions : instances
    WorkflowExecutions ||--o{ StateTransitions : tracks
    WorkflowExecutions ||--o{ AuditLogs : logs
    WorkflowExecutions ||--o{ RecoveryActions : records

    Users {
        int id PK
        string username
        string email
        string role
    }

    Workflows {
        int id PK
        int owner_id FK
        string name
        string dsl
        string nl_description
        json parsed_definition
        enum status
        int optimization_score
        json ai_suggestions
        datetime created_at
        datetime updated_at
    }

    WorkflowStates {
        int id PK
        int workflow_id FK
        string state_name
        string state_type
        string callback_type
        int timeout_seconds
        json retry_policy
    }

    WorkflowExecutions {
        int id PK
        int workflow_id FK
        string execution_id
        enum status
        string current_state
        json initial_context
        json final_context
        json states_visited
        datetime start_time
        datetime end_time
        int duration_ms
        json ai_decisions
        boolean anomaly_detected
    }

    StateTransitions {
        int id PK
        int execution_id FK
        string from_state
        string to_state
        enum transition_type
        json context_snapshot
        string condition_evaluated
        boolean condition_result
        boolean ai_decision_used
        string ai_decision_reasoning
        int ai_confidence_score
        datetime timestamp
        int duration_ms
    }

    AuditLogs {
        int id PK
        int execution_id FK
        datetime timestamp
        enum level
        string state
        string event_type
        string message
        json metadata
        string stack_trace
    }

    RecoveryActions {
        int id PK
        int execution_id FK
        string error_type
        string error_message
        string error_state
        json error_context
        string recovery_strategy
        boolean ai_suggested
        string ai_reasoning
        boolean success
        datetime timestamp
        int recovery_duration_ms
    }
```

### 4.2 Data Storage Layers

```mermaid
graph TD
    subgraph "Layer 1: Hot Cache - Redis"
        L1[Current workflow states, Context TTL 1h,<br/>LLM cache TTL 1h, Rate limiting, Distributed locks<br/>Access: Read-heavy 10K+ req/sec, Latency: less than 5ms]
    end

    subgraph "Layer 2: Primary Database - PostgreSQL"
        L2[Workflow definitions, Execution records,<br/>State transitions indexed, Audit logs, Recovery actions<br/>Access: Balanced read/write, Latency: less than 50ms]
    end

    subgraph "Layer 3: Analytics Store - TimescaleDB"
        L3[Metrics time-series, Performance data,<br/>LLM cost tracking, Error patterns<br/>Access: Write-heavy batch reads, Retention: 90d hot 1yr cold]
    end

    subgraph "Layer 4: Object Storage - S3"
        L4[Large execution contexts greater than 1MB, Workflow snapshots,<br/>Audit log archives, ML training data<br/>Access: Write-once read-rare, Retention: Indefinite]
    end

    L1 --> L2
    L2 --> L3
    L3 --> L4

    style L1 fill:#ffebee
    style L2 fill:#e3f2fd
    style L3 fill:#f3e5f5
    style L4 fill:#e8f5e9
```

---

## 5. Integration Architecture Diagrams

### 5.1 Integration Points

```mermaid
graph TD
    WorkflowEngine[Workflow Engine Core]

    subgraph "Upstream Services"
        LLMAPIs[LLM APIs<br/>• OpenAI<br/>• Anthropic<br/>• Local LLM]
        TaskQueue[Task Queue<br/>Celery<br/>• Long tasks<br/>• Scheduling<br/>• Retry]
        External[External Services<br/>• REST APIs<br/>• Webhooks<br/>• SOAP]
    end

    subgraph "Infrastructure Services"
        Monitoring[Monitoring<br/>• Prometheus<br/>• Grafana<br/>• ELK Stack<br/>• Jaeger]
        Messaging[Messaging<br/>RabbitMQ<br/>• Events<br/>• Pub/Sub<br/>• Streams]
        Database[Database Services<br/>• PostgreSQL<br/>• Redis<br/>• S3]
    end

    WorkflowEngine --> LLMAPIs
    WorkflowEngine --> TaskQueue
    WorkflowEngine --> External

    WorkflowEngine --> Monitoring
    WorkflowEngine --> Messaging
    WorkflowEngine --> Database

    style LLMAPIs fill:#e1f5ff
    style TaskQueue fill:#f3e5f5
    style External fill:#e8f5e9
```

### 5.2 API Gateway Pattern

```mermaid
graph TB
    subgraph "Clients"
        WebUI[Web UI]
        Mobile[Mobile]
        CLI[CLI]
        ThirdParty[Third-party]
    end

    subgraph "API Gateway - FastAPI"
        Auth[Auth JWT]
        RateLimit[Rate Limiting]
        Validation[Request Validation]
        Routing[Routing]
        Transform[Transform]
        Response[Response Format]

        Auth --> RateLimit
        RateLimit --> Validation
        Validation --> Routing
        Routing --> Transform
        Transform --> Response
    end

    subgraph "Backend Services"
        WorkflowService[Workflow Service<br/>• CRUD ops<br/>• Validation]
        ExecutionService[Execution Service<br/>• Run flows<br/>• Monitor]
        AnalyticsService[Analytics Service<br/>• Metrics<br/>• Reports]
    end

    WebUI --> Auth
    Mobile --> Auth
    CLI --> Auth
    ThirdParty --> Auth

    Response --> WorkflowService
    Response --> ExecutionService
    Response --> AnalyticsService

    style Auth fill:#ffebee
    style RateLimit fill:#fff3e0
    style Validation fill:#e8f5e9
```

---

## 6. AI/ML Architecture Diagrams

### 6.1 LLM Service Architecture

```mermaid
graph TD
    subgraph "LLM Service Facade"
        subgraph "Request Processing"
            ValidateInput[Validate Input]
            TemplateRender[Template Render]
            CacheCheck[Cache Check]
            TrackCost[Track Cost]

            ValidateInput --> TemplateRender
            TemplateRender --> CacheCheck
            CacheCheck --> TrackCost
        end

        subgraph "Provider Router - Multi-LLM Support"
            OpenAI[OpenAI GPT-4]
            Anthropic[Anthropic Claude]
            Azure[Azure OpenAI]
            Local[Local LLaMA]

            Strategy[Primary/Fallback Strategy]
            OpenAI --> Strategy
            Anthropic --> Strategy
            Azure --> Strategy
            Local --> Strategy
        end

        subgraph "Response Processing"
            ParseResponse[Parse Response]
            ValidateOutput[Validate Output]
            CacheStore[Cache Store]
            ReturnResult[Return Result]

            ParseResponse --> ValidateOutput
            ValidateOutput --> CacheStore
            CacheStore --> ReturnResult
        end
    end

    TrackCost --> Strategy
    Strategy --> ParseResponse

    style OpenAI fill:#e1f5ff
    style Anthropic fill:#f3e5f5
    style Strategy fill:#fff3e0
```

### 6.2 Prompt Engineering Pipeline

```mermaid
graph TD
    Start[User Request / System Event]

    Start --> Intent[Intent Classification]

    Intent --> Template[Template Selection<br/>nl_to_dsl, decision, recovery, optimization]

    Template --> Context[Context Injection<br/>User context, History, Statistics, Examples]

    Context --> FewShot[Few-Shot Learning<br/>Add examples, Pattern match, Domain adapt]

    FewShot --> TokenOpt[Token Optimization<br/>Truncate, Compress, Prioritize]

    TokenOpt --> LLMCall[LLM API Call<br/>Temperature, Max tokens, Top-p]

    LLMCall --> Parse[Response Parsing<br/>Extract JSON, Validate, Sanitize]

    Parse --> End[Final Output]

    style Intent fill:#e1f5ff
    style Template fill:#f3e5f5
    style FewShot fill:#e8f5e9
    style LLMCall fill:#fff3e0
```

### 6.3 AI Decision Confidence Scoring

```mermaid
graph TD
    Input[Input Context]

    Input --> Features[Feature Extraction<br/>Context completeness, Historical data, Pattern match strength]

    Features --> Rule[Rule Score<br/>0-100]
    Features --> ML[ML Score<br/>0-100]
    Features --> LLM[LLM Score<br/>0-100]

    Rule --> Weighted[Weighted Average<br/>Final = 0.3*Rule + 0.3*ML + 0.4*LLM]
    ML --> Weighted
    LLM --> Weighted

    Weighted --> Bands[Confidence Bands<br/>90-100: Very High, 70-89: High, 50-69: Medium,<br/>30-49: Low, 0-29: Very Low]

    style Rule fill:#ffebee
    style ML fill:#e3f2fd
    style LLM fill:#e8f5e9
    style Weighted fill:#fff3e0
```

---

## 7. Deployment Diagrams

### 7.1 Kubernetes Deployment Architecture

```mermaid
graph TB
    subgraph "Kubernetes Cluster"
        subgraph "Namespace: workflow-prod"
            subgraph "API Server Deployment"
                API1[API Pod 1<br/>2 CPU, 4GB RAM]
                API2[API Pod 2]
                API3[API Pod 3]
                APIN[API Pod N<br/>HPA: 3-10]
            end

            subgraph "Celery Worker Deployment"
                Worker1[Worker 1<br/>1 CPU, 2GB RAM]
                Worker2[Worker 2]
                WorkerN[Worker N<br/>HPA: 5-50<br/>based on queue depth]
            end

            subgraph "Redis StatefulSet"
                RedisMaster[Redis Master<br/>2 CPU, 8GB RAM]
                RedisReplica1[Redis Replica 1]
                RedisReplica2[Redis Replica 2]
                RedisMaster --> RedisReplica1
                RedisMaster --> RedisReplica2
            end

            PostgreSQL[PostgreSQL RDS<br/>Multi-AZ<br/>Read Replicas: 2]

            Ingress[NGINX Ingress<br/>• SSL/TLS<br/>• Rate limiting<br/>• WAF]
        end

        subgraph "Namespace: monitoring"
            Prometheus[Prometheus]
            Grafana[Grafana]
            Jaeger[Jaeger]
            ELK[ELK Stack]
        end
    end

    LB[Load Balancer<br/>NGINX / AWS ALB]

    LB --> Ingress
    Ingress --> API1
    Ingress --> API2
    Ingress --> API3
    Ingress --> APIN

    API1 --> RedisMaster
    API2 --> RedisMaster
    API1 --> PostgreSQL

    Worker1 --> PostgreSQL
    Worker2 --> PostgreSQL

    API1 --> Prometheus
    Worker1 --> Prometheus

    style API1 fill:#e3f2fd
    style Worker1 fill:#f3e5f5
    style RedisMaster fill:#ffebee
    style PostgreSQL fill:#e8f5e9
```

### 7.2 Horizontal Scaling Architecture

```mermaid
graph TD
    LB[Load Balancer<br/>NGINX / AWS ALB]

    subgraph "API Server Pods"
        Pod1[API Pod 1]
        Pod2[API Pod 2]
        Pod3[API Pod 3]
        PodN[API Pod N]
    end

    Redis[Redis Cluster<br/>Shared State / Cache]

    PostgreSQL[PostgreSQL Primary<br/>+ Read Replicas 2x]

    subgraph "Celery Workers"
        Worker[Celery Worker Pool<br/>Auto-scaling: 5-50]
    end

    LB --> Pod1
    LB --> Pod2
    LB --> Pod3
    LB --> PodN

    Pod1 --> Redis
    Pod2 --> Redis
    Pod3 --> Redis
    PodN --> Redis

    Redis --> PostgreSQL

    PostgreSQL --> Worker

    Triggers[Scaling Triggers:<br/>• CPU greater than 70%: Add pod<br/>• Memory greater than 80%: Add pod<br/>• Queue depth greater than 100: Add worker<br/>• Response time greater than 1s: Scale up]

    style Triggers fill:#fff3e0
    style Pod1 fill:#e3f2fd
    style Worker fill:#f3e5f5
```

### 7.3 CI/CD Pipeline

```mermaid
graph LR
    GitPush[Git Push]

    GitPush --> CI[GitHub Actions /<br/>GitLab CI]

    CI --> Build[Stage 1: Build<br/>• Lint code<br/>• Unit tests<br/>• Build Docker]

    Build --> Test[Stage 2: Test<br/>• Integration<br/>• Security scan<br/>• Performance]

    Test --> Staging[Stage 3: Staging<br/>• Deploy staging<br/>• Smoke tests<br/>• Load tests]

    Staging --> Approval[Stage 4: Approval<br/>• Manual review<br/>• QA sign-off]

    Approval --> Prod[Stage 5: Production<br/>• Blue/green<br/>• Canary 10%<br/>• Monitor<br/>• Full rollout]

    style Build fill:#e3f2fd
    style Test fill:#f3e5f5
    style Staging fill:#fff3e0
    style Prod fill:#e8f5e9
```

### 7.4 Multi-Level Caching Strategy

```mermaid
graph TD
    Request[Request]

    Request --> L1{L1: Memory<br/>LRU, 5 min}

    L1 -->|Hit 5%| Return1[Return immediately]
    L1 -->|Miss| L2{L2: Redis<br/>1 hour}

    L2 -->|Hit 60%| Return2[Return less than 10ms]
    L2 -->|Miss| L3{L3: Database<br/>permanent}

    L3 -->|Hit 95%| Return3[Return less than 50ms]
    L3 -->|Miss| L4[L4: Compute<br/>LLM/Callback]

    L4 --> Generate[Generate 100%]
    Generate --> CacheAll[Cache all levels]
    CacheAll --> Return4[Return result]

    style L1 fill:#ffebee
    style L2 fill:#e3f2fd
    style L3 fill:#f3e5f5
    style L4 fill:#e8f5e9
```

### 7.5 Disaster Recovery Strategy

```mermaid
graph TD
    subgraph "Recovery Objectives"
        RTO[RTO: 1 hour]
        RPO[RPO: 15 minutes]
        Retention[Data Retention:<br/>90 days hot<br/>1 year cold]
    end

    subgraph "Backup Strategy"
        subgraph "Database"
            DB1[Continuous replication<br/>to standby sync]
            DB2[Automated snapshots<br/>every 6 hours]
            DB3[Point-in-time recovery<br/>15 min granularity]
            DB4[Cross-region backup<br/>daily]
        end

        subgraph "Redis"
            R1[AOF persistence<br/>append-only file]
            R2[RDB snapshots<br/>every hour]
            R3[Replication to<br/>standby cluster]
        end

        subgraph "S3"
            S1[Cross-region<br/>replication]
            S2[Versioning<br/>enabled]
            S3Lifecycle[Lifecycle policies<br/>archive after 90 days]
        end
    end

    subgraph "Failure Scenarios"
        F1[Single Pod Failure<br/>Detection: less than 30s<br/>Recovery: Automatic K8s<br/>Impact: None]

        F2[AZ Failure<br/>Detection: less than 1 min<br/>Recovery: Automatic multi-AZ<br/>Impact: Minimal latency spike]

        F3[Region Failure<br/>Detection: less than 5 min<br/>Recovery: Manual DNS failover<br/>Impact: 15-60 min downtime]

        F4[Database Failure<br/>Detection: less than 1 min<br/>Recovery: Promote standby<br/>Impact: less than 15 min]
    end

    style DB1 fill:#e3f2fd
    style R1 fill:#ffebee
    style S1 fill:#e8f5e9
    style F1 fill:#f3e5f5
```

---

## Summary

This document provides all the architecture diagrams from the HLD in Mermaid format, making them:

1. **Editable**: Easy to modify and update
2. **Renderable**: Can be viewed in GitHub, GitLab, Notion, and many markdown viewers
3. **Version-controllable**: Track changes in git
4. **Interactive**: Some viewers support zoom and pan
5. **Exportable**: Can be exported to PNG, SVG, PDF

### Diagram Categories

- **7 System Architecture diagrams** - Layered architecture, request flows, data flows
- **4 Innovation diagrams** - NL translation, decision engine, auto-recovery, optimization
- **4 Core Component diagrams** - Class, sequence, state machine, component diagrams
- **2 Data Architecture diagrams** - ER diagram, storage layers
- **2 Integration diagrams** - Integration points, API gateway
- **3 AI/ML Architecture diagrams** - LLM service, prompt engineering, confidence scoring
- **5 Deployment diagrams** - Kubernetes, scaling, CI/CD, caching, disaster recovery

**Total: 27 Mermaid diagrams** covering all aspects of the AI-driven workflow engine architecture.

---

**Document Version:** 1.0
**Last Updated:** 2025-11-18
**Status:** Ready for Review
