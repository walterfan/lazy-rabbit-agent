# Tasks: Add Medical Paper Writing Assistant

## Development Methodology

遵循 **三大护法** (Three Protectors) 方法论：
- **可验证性 (TDD)**: Tests FIRST → Implementation
- **可观测性 (MDD)**: Metrics → Instrumentation → Dashboards
- **可理解性 (Living Docs)**: Architecture → Code Comments → Runbook

---

## Phase 0: Prerequisites & Setup

- [x] 0.1 Verify `add-personal-secretary-agent` completion status
- [x] 0.2 Install additional dependencies
  ```bash
  poetry add langgraph biopython scipy statsmodels
  ```
- [x] 0.3 Create directory structure for medical paper agent
- [x] 0.4 Set up prompt templates directory

---

## Phase 1: Database Models & Migrations (TDD)

### 1.1 Define Models
- [x] 1.1.1 Create `backend/app/models/medical_paper.py`
  - `MedicalPaperTask` model
  - `PaperTaskMessage` model (A2A audit trail)
  - `PaperType` enum (RCT, META_ANALYSIS, COHORT)
  - `TaskStatus` enum (PENDING, RUNNING, REVISION, COMPLETED, FAILED)
- [x] 1.1.2 Update `backend/app/models/__init__.py`
- [x] 1.1.3 Add relationship to User model

### 1.2 Create Migration
- [x] 1.2.1 Generate Alembic migration
  ```bash
  alembic revision --autogenerate -m "add medical paper tables"
  ```
- [ ] 1.2.2 Run migration
  ```bash
  alembic upgrade head
  ```

### 1.3 Write Tests (TDD - Red Phase)
- [x] 1.3.1 Create `backend/tests/test_medical_paper_models.py`
  - Test task creation
  - Test message creation
  - Test relationships

---

## Phase 2: A2A Communication Contract

### 2.1 Define Schemas
- [x] 2.1.1 Create `backend/app/schemas/medical_paper.py`
  - `A2AMessage` schema
  - `A2AError` schema
  - `A2AMetrics` schema
  - `LiteratureOutput` schema
  - `StatsOutput` schema
  - `ComplianceOutput` schema
- [x] 2.1.2 Create JSON schema file `prompts/schemas/a2a_message.v1.json`

### 2.2 Implement A2A Utilities
- [x] 2.2.1 Create `backend/app/services/medical_paper_agent/a2a.py`
  - Message serialization/deserialization
  - Correlation ID generation
  - Error classification
  - Retry strategy implementation

### 2.3 Write Tests (TDD - Red Phase)
- [x] 2.3.1 Create `backend/tests/test_a2a_contract.py`
  - Test message serialization
  - Test error classification
  - Test retry logic

---

## Phase 3: Prompt Templates (YAML)

### 3.1 Create Supervisor Prompts
- [x] 3.1.1 `prompts/supervisor/router.v1.yaml` - 任务路由
- [x] 3.1.2 `prompts/supervisor/evaluator.v1.yaml` - 结果评估

### 3.2 Create Agent Prompts
- [x] 3.2.1 `prompts/agents/literature/system.v1.yaml`
- [x] 3.2.2 `prompts/agents/literature/search_strategy.v1.yaml`
- [x] 3.2.3 `prompts/agents/stats/system.v1.yaml`
- [x] 3.2.4 `prompts/agents/stats/analysis_plan.v1.yaml`
- [x] 3.2.5 `prompts/agents/writer/system.v1.yaml`
- [x] 3.2.6 `prompts/agents/writer/introduction.v1.yaml`
- [x] 3.2.7 `prompts/agents/writer/methods.v1.yaml`
- [x] 3.2.8 `prompts/agents/writer/results.v1.yaml`
- [x] 3.2.9 `prompts/agents/writer/discussion.v1.yaml`
- [x] 3.2.10 `prompts/agents/compliance/system.v1.yaml`
- [x] 3.2.11 `prompts/agents/compliance/consort.v1.yaml`
- [x] 3.2.12 `prompts/agents/compliance/strobe.v1.yaml`

### 3.3 Implement Prompt Loader
- [x] 3.3.1 Create `backend/app/services/medical_paper_agent/prompt_loader.py`
  - YAML loading with version support
  - Template rendering with Jinja2

---

## Phase 4: SubAgent Tools (SRP)

### 4.1 Literature Agent Tools
- [x] 4.1.1 Create `tools/literature_tools.py`
  - `search_pubmed(query, max_results)` - PubMed E-utilities
  - `search_clinicaltrials(query)` - ClinicalTrials.gov API
  - `get_article_abstract(pmid)`
  - `format_citation(pmid, style)`
- [x] 4.1.2 Write tests `tests/test_literature_tools.py`

### 4.2 Stats Agent Tools
- [x] 4.2.1 Create `tools/stats_tools.py`
  - `run_ttest(data, groups)`
  - `run_chi_square(data)`
  - `run_survival_analysis(data)`
  - `calculate_sample_size(params)`
  - `generate_stats_report(results)`
- [x] 4.2.2 Write tests `tests/test_stats_tools.py`

### 4.3 Writer Agent Tools
- [x] 4.3.1 Create `tools/writing_tools.py`
  - `write_section(section_type, context)`
  - `revise_section(section, feedback)`
  - `merge_sections(sections)`
- [x] 4.3.2 Write tests `tests/test_writing_tools.py`

### 4.4 Compliance Agent Tools
- [x] 4.4.1 Create `tools/compliance_tools.py`
  - `check_consort(manuscript)` - 25 items
  - `check_strobe(manuscript)` - 22 items
  - `check_prisma(manuscript)` - 27 items
  - `generate_compliance_report(results)`
- [x] 4.4.2 Write tests `tests/test_compliance_tools.py`

---

## Phase 5: SubAgents Implementation

### 5.1 Literature Agent
- [x] 5.1.1 Create `agents/literature_agent.py`
  - `create_react_agent` with literature tools
  - System prompt from YAML
- [x] 5.1.2 Write tests `tests/test_literature_agent.py`

### 5.2 Stats Agent
- [x] 5.2.1 Create `agents/stats_agent.py`
  - `create_react_agent` with stats tools
  - System prompt from YAML
- [x] 5.2.2 Write tests `tests/test_stats_agent.py`

### 5.3 Writer Agent
- [x] 5.3.1 Create `agents/writer_agent.py`
  - `create_react_agent` with writing tools
  - System prompt from YAML
- [x] 5.3.2 Write tests `tests/test_writer_agent.py`

### 5.4 Compliance Agent
- [x] 5.4.1 Create `agents/compliance_agent.py`
  - `create_react_agent` with compliance tools
  - System prompt from YAML
- [x] 5.4.2 Write tests `tests/test_compliance_agent.py`

---

## Phase 6: Supervisor & Workflow (LangGraph)

### 6.1 Implement State
- [x] 6.1.1 Create `backend/app/services/medical_paper_agent/state.py`
  - `MedicalPaperState(MessagesState)` - Extended state (TypedDict)
  - References, stats report, manuscript sections, compliance score

### 6.2 Implement Supervisor
- [x] 6.2.1 Create `backend/app/services/medical_paper_agent/supervisor.py`
  - `MedicalPaperSupervisor` class
  - Workflow routing logic
  - A2A message handling

### 6.3 Build Workflow Graph
- [x] 6.3.1 Create `backend/app/services/medical_paper_agent/workflow.py`
  - `StateGraph` definition
  - Node connections (edges)
  - Conditional routing
  - Compile graph

### 6.4 Write Tests (TDD)
- [x] 6.4.1 Create `tests/test_medical_paper_workflow.py`
  - Test workflow compilation
  - Test routing decisions
  - Test revision loop
  - Test end-to-end flow (mock LLM)

---

## Phase 7: API Endpoints

### 7.1 Create Schemas
- [x] 7.1.1 Add to `backend/app/schemas/medical_paper.py`
  - `CreateTaskRequest`
  - `TaskResponse`
  - `RevisionRequest`
  - `TemplateResponse`

### 7.2 Implement Endpoints
- [x] 7.2.1 Create `backend/app/api/v1/endpoints/medical_paper.py`
  - `POST /create` - Create new task
  - `GET /{task_id}` - Get task status
  - `GET /{task_id}/stream` - Stream progress (SSE)
  - `POST /{task_id}/revise` - Submit revision
  - `GET /templates` - List templates

### 7.3 Register Router
- [x] 7.3.1 Update `backend/app/api/v1/api.py`

### 7.4 Write Tests (TDD)
- [x] 7.4.1 Create `tests/test_medical_paper_api.py`
  - Test authentication
  - Test task creation
  - Test status retrieval
  - Test streaming
  - Test revision submission

---

## Phase 8: Metrics & Observability (MDD)

### 8.1 Define Metrics
- [x] 8.1.1 Create `backend/app/services/medical_paper_agent/metrics.py`
  - `medical_paper_task_total` Counter
  - `medical_paper_task_duration_seconds` Histogram
  - `medical_paper_agent_calls_total` Counter
  - `medical_paper_agent_latency_seconds` Histogram
  - `medical_paper_compliance_score` Gauge
  - `medical_paper_revision_rounds` Histogram

### 8.2 Instrument Code
- [x] 8.2.1 Add metrics to supervisor (track_step, track_agent context managers)
- [x] 8.2.2 Add metrics to each SubAgent (record_agent_tool_call)
- [ ] 8.2.3 Add tracing integration (reuse secretary_agent tracing)

### 8.3 Create Dashboard
- [ ] 8.3.1 Create Grafana dashboard JSON
- [ ] 8.3.2 Define alerting rules

### 8.4 Write Tests
- [x] 8.4.1 Test metrics registration
- [x] 8.4.2 Test metrics increment

---

## Phase 9: Frontend Components

### 9.1 Create Pinia Store
- [x] 9.1.1 Create `frontend/src/stores/medicalPaper.ts`
  - Task state management
  - API actions
  - Streaming handling

### 9.2 Create Views
- [x] 9.2.1 Create `frontend/src/views/MedicalPaper.vue` - Main workspace
- [x] 9.2.2 Add route to `router/index.ts`

### 9.3 Create Components
- [x] 9.3.1 Task creation form (inline in MedicalPaper.vue)
- [x] 9.3.2 Literature references panel (inline in MedicalPaper.vue)
- [ ] 9.3.3 `components/medical-paper/StatsPanel.vue` - Statistics display
- [ ] 9.3.4 `components/medical-paper/OutlineEditor.vue` - Outline editing
- [ ] 9.3.5 `components/medical-paper/ManuscriptEditor.vue` - Manuscript editing
- [x] 9.3.6 Compliance report display (inline in MedicalPaper.vue)
- [x] 9.3.7 Streaming progress display (inline in MedicalPaper.vue)

### 9.4 Update Navigation
- [x] 9.4.1 Add "Medical Paper" to AppHeader.vue menu

### 9.5 Write Tests
- [ ] 9.5.1 Unit tests for components
- [ ] 9.5.2 E2E tests with Playwright

---

## Phase 10: Documentation (Living Docs)

### 10.1 Code Documentation
- [x] 10.1.1 Add docstrings to all public functions (all already had docstrings)
- [x] 10.1.2 Add inline comments for complex logic (already present)
- [x] 10.1.3 Document A2A message flow (in runbook + design.md appendix)

### 10.2 Architecture Documentation
- [x] 10.2.1 Update design.md with final implementation (added Implementation Notes appendix)
- [x] 10.2.2 Add sequence diagrams for key flows (happy path + revision loop)
- [x] 10.2.3 Document error handling (error classification table + retry strategy)

### 10.3 API Documentation
- [x] 10.3.1 Add OpenAPI annotations (summary, responses on all endpoints)
- [x] 10.3.2 Add request/response examples (json_schema_extra on schemas)
- [ ] 10.3.3 Verify Swagger UI (runtime — requires server start)

### 10.4 Runbook
- [x] 10.4.1 Create `doc/medical-paper-agent-runbook.md` with:
  - Common issues and solutions (5 scenarios)
  - Metrics interpretation (6 key metrics + PromQL queries)
  - Alert responses (3 alert runbooks)
  - Recovery procedures (pipeline restart, migration, prompt update)

---

## Phase 11: Integration Testing & Validation

### 11.1 Acceptance Tests
- [ ] 11.1.1 AT-1: Create RCT paper task
- [ ] 11.1.2 AT-2: Literature search returns valid references
- [ ] 11.1.3 AT-3: Stats analysis produces valid output
- [ ] 11.1.4 AT-4: Writer generates IMRAD structure
- [ ] 11.1.5 AT-5: Compliance check identifies issues
- [ ] 11.1.6 AT-6: Revision loop works correctly
- [ ] 11.1.7 AT-7: Task completion updates status
- [ ] 11.1.8 AT-8: Streaming progress works
- [ ] 11.1.9 AT-9: Error handling and recovery

### 11.2 Performance Testing
- [ ] 11.2.1 Load test with concurrent tasks
- [ ] 11.2.2 Verify latency thresholds (P95 < 30s per step)
- [ ] 11.2.3 Verify memory usage

### 11.3 Security Review
- [ ] 11.3.1 Verify authentication on all endpoints
- [ ] 11.3.2 Verify authorization (user can only access own tasks)
- [ ] 11.3.3 Review input validation
- [ ] 11.3.4 Review PubMed API key handling

---

## Phase 12: Final Review & Release

### 12.1 Code Review Checklist
- [ ] 12.1.1 All tests pass
- [ ] 12.1.2 Coverage > 80%
- [ ] 12.1.3 No linter errors
- [ ] 12.1.4 Documentation complete

### 12.2 Release Preparation
- [ ] 12.2.1 Update CHANGELOG.md
- [ ] 12.2.2 Update README.md with new feature
- [ ] 12.2.3 Verify production configuration
- [ ] 12.2.4 Create release notes

### 12.3 Sign-off
- [ ] 12.3.1 TDD: All tests pass
- [ ] 12.3.2 MDD: Metrics dashboard operational
- [ ] 12.3.3 Living Docs: Documentation complete

---

## Summary

| Phase | Tasks | Status |
|-------|-------|--------|
| 0. Prerequisites | 4 | ✅ |
| 1. Database Models | 6 | ✅ (1.2.2 runtime) |
| 2. A2A Contract | 6 | ✅ |
| 3. Prompt Templates | 15 | ✅ |
| 4. SubAgent Tools | 8 | ✅ |
| 5. SubAgents | 8 | ✅ |
| 6. Supervisor & Workflow | 4 | ✅ |
| 7. API Endpoints | 4 | ✅ |
| 8. Metrics | 8 | ✅ (8.2.3, 8.3.x deferred) |
| 9. Frontend | 12 | ✅ (9.3.3-5, 9.5.x deferred) |
| 10. Documentation | 10 | ✅ (10.3.3 runtime) |
| 11. Testing | 12 | ⏳ |
| 12. Release | 7 | ⏳ |
| **Total** | **102** | ~75% done |
