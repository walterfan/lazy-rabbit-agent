# Design: Medical Paper Writing Assistant

## Context

本系统基于 [AI Agent 处理复杂流程](~/workspace/walter/wfblog/content/journal/journal_20260206_ai-agent-workflow.md) 的方法论，实现一个多 Agent 协作的医学论文写作助手。核心思想是：**先写 Workflow，再写 Prompt**。

### Stakeholders

- 临床医学研究人员（主要用户）
- 医学院研究生
- 论文审稿人（受益于合规性检查）

### Constraints

- 需兼容现有的 LLM 配置（`LLM_PROVIDER`, `LLM_BASE_URL`, `LLM_API_KEY`）
- 需复用 `add-personal-secretary-agent` 的 tracing 和 metrics 基础设施
- 需支持自签名证书的 LLM（`LLM_VERIFY_SSL=false`）

---

## Goals / Non-Goals

### Goals

- 提供完整的临床论文写作工作流（文献检索 → 统计分析 → IMRAD撰写 → 合规审查）
- 实现 Supervisor + SubAgent 架构，遵循 SOLID 原则
- 支持循环修订（合规审查失败 → 修订 → 重新审查）
- 每个步骤可追踪、可审计
- 支持多种论文类型模板（RCT, Meta-analysis, Cohort Study）

### Non-Goals

- 不自动提交到期刊系统
- 不处理图表制作（引用外部工具）
- 不进行原创性检测（引用外部服务）
- 不支持实时协作编辑（未来增强）

---

## Architecture Overview

### Multi-Agent System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface                           │
│                    (MedicalPaperWorkspace.vue)                  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Layer (FastAPI)                        │
│               /api/v1/medical-paper/*                           │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              MedicalPaperAgent (Supervisor)                     │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                  LangGraph StateGraph                    │   │
│   │                                                          │   │
│   │  START ──▶ literature ──▶ stats ──▶ writer ──▶ compliance│   │
│   │              │             │          │           │      │   │
│   │              └─────────────┴──────────┴───────────┘      │   │
│   │                            │                             │   │
│   │                     supervisor (hub)                      │   │
│   │                            │                             │   │
│   │              ┌─────────────┴──────────────┐              │   │
│   │              ▼                            ▼              │   │
│   │           RETRY                         END              │   │
│   └─────────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                 ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ LiteratureAgent │ │   StatsAgent    │ │  WriterAgent    │
│ (PubMed Search) │ │ (Statistics)    │ │ (IMRAD Writer)  │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ MCP: PubMed     │ │ MCP: Stats      │ │ Prompt Templates│
│ Tool Server     │ │ Tool Server     │ │ (YAML files)    │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

### SOLID Principles Application

| Principle | Application |
|-----------|-------------|
| **SRP** | 每个 SubAgent 只负责一个领域能力 |
| **OCP** | 新增能力 = 新增 Agent 节点，不修改 Supervisor |
| **LSP** | 遵守 A2A schema 的 Agent 可互换 |
| **ISP** | 每个 Agent 只拿自己需要的 tools |
| **DIP** | Agent 之间依赖 A2A 契约，不依赖具体实现 |

---

## Component Design

### 1. Supervisor Agent (MedicalPaperAgent)

**Responsibilities:**
- 解析用户请求，识别论文类型和要求
- 按 workflow 分派任务给 SubAgents
- 验收 SubAgent 输出，检查一致性
- 处理循环修订逻辑

**Implementation:**
```python
# backend/app/services/medical_paper_agent/supervisor.py

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent

class MedicalPaperSupervisor:
    def __init__(self, db: Session, user_id: int, task_id: UUID):
        self.db = db
        self.user_id = user_id
        self.task_id = task_id
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> CompiledGraph:
        return (
            StateGraph(MedicalPaperState)
            .add_node("supervisor", self._supervisor_node)
            .add_node("literature", self._literature_node)
            .add_node("stats", self._stats_node)
            .add_node("writer", self._writer_node)
            .add_node("compliance", self._compliance_node)
            .add_edge(START, "supervisor")
            .add_conditional_edges("supervisor", self._route_next)
            .add_edge("literature", "supervisor")
            .add_edge("stats", "supervisor")
            .add_edge("writer", "supervisor")
            .add_edge("compliance", "supervisor")
            .compile()
        )
```

### 2. Literature Agent

**SRP:** 只负责文献检索和引用管理

**Tools:**
- `search_pubmed(query, max_results)` - PubMed 检索
- `search_clinicaltrials(query)` - ClinicalTrials.gov 检索
- `get_article_abstract(pmid)` - 获取文章摘要
- `format_citation(pmid, style)` - 格式化引用

**Output Schema:**
```python
class LiteratureOutput(BaseModel):
    references: list[Reference]
    search_strategy: str
    total_found: int
    filtered_count: int
    
class Reference(BaseModel):
    pmid: str
    title: str
    authors: list[str]
    journal: str
    year: int
    abstract: str
    relevance_score: float
```

### 3. Stats Agent

**SRP:** 只负责统计分析

**Tools:**
- `run_ttest(data, groups)` - t检验
- `run_chi_square(data)` - 卡方检验
- `run_survival_analysis(data)` - 生存分析
- `calculate_sample_size(params)` - 样本量计算
- `generate_stats_report(results)` - 生成统计报告

**Output Schema:**
```python
class StatsOutput(BaseModel):
    primary_analysis: AnalysisResult
    secondary_analyses: list[AnalysisResult]
    sensitivity_analyses: list[AnalysisResult]
    summary_statistics: dict
    
class AnalysisResult(BaseModel):
    test_name: str
    statistic: float
    p_value: float
    confidence_interval: tuple[float, float]
    effect_size: float
    interpretation: str
```

### 4. Writer Agent

**SRP:** 只负责论文撰写

**Tools:**
- `write_introduction(refs, context)` - 撰写引言
- `write_methods(design, stats_plan)` - 撰写方法
- `write_results(stats_output)` - 撰写结果
- `write_discussion(refs, results)` - 撰写讨论
- `revise_section(section, feedback)` - 修订章节

**Prompt Templates:**
```yaml
# prompts/agents/writer/system.v1.yaml
system_prompt: |
  你是 WriterAgent，负责撰写医学论文。
  严格使用 IMRAD 结构（Introduction, Methods, Results, Discussion）。
  学术语言，客观严谨，所有论述必须有引用支持。
  不要自己编造数据，只使用提供的文献和统计结果。

templates:
  introduction:
    structure:
      - background: "疾病/问题的重要性和现状"
      - gap: "现有研究的不足"
      - objective: "本研究的目的和假设"
  
  methods:
    structure:
      - study_design: "研究设计类型"
      - participants: "纳入/排除标准"
      - interventions: "干预措施"
      - outcomes: "主要/次要终点"
      - statistical_analysis: "统计方法"
```

### 5. Compliance Agent

**SRP:** 只负责合规审查

**Tools:**
- `check_consort(manuscript)` - CONSORT检查（RCT）
- `check_strobe(manuscript)` - STROBE检查（观察性研究）
- `check_prisma(manuscript)` - PRISMA检查（系统综述）
- `generate_compliance_report(results)` - 生成合规报告

**Output Schema:**
```python
class ComplianceOutput(BaseModel):
    checklist_type: str  # CONSORT, STROBE, PRISMA
    total_items: int
    passed: int
    warnings: int
    failed: int
    items: list[ComplianceItem]
    overall_score: float
    
class ComplianceItem(BaseModel):
    item_id: str
    description: str
    status: Literal["PASS", "WARN", "FAIL"]
    finding: str
    suggestion: str | None
```

---

## A2A Communication Contract

### Message Schema (v1)

```python
class A2AMessage(BaseModel):
    protocol: str = "a2a.v1"
    id: str  # msg_YYYYMMDD_XXXXXX
    correlation_id: str  # task correlation ID
    sender: str  # supervisor, literature_agent, etc.
    receiver: str
    intent: str  # collect_references, run_analysis, etc.
    input: dict
    status: Literal["pending", "ok", "error"]
    output: dict | None
    error: A2AError | None
    metrics: A2AMetrics
    
class A2AError(BaseModel):
    code: str  # VALIDATION_ERROR, TOOL_ERROR, TIMEOUT, etc.
    message: str
    recoverable: bool
    retry_after: int | None  # seconds
    
class A2AMetrics(BaseModel):
    latency_ms: int
    tokens_in: int
    tokens_out: int
    tool_calls: int
```

### Error Classification & Retry Strategy

| Error Code | Description | Retry | Strategy |
|------------|-------------|-------|----------|
| `VALIDATION_ERROR` | 输入不合规 | No | Return to user |
| `TOOL_ERROR` | 工具执行失败 | Yes (3x) | Exponential backoff |
| `TIMEOUT` | 超时 | Yes (2x) | Increase timeout |
| `RATE_LIMIT` | API限流 | Yes | Wait and retry |
| `LLM_ERROR` | LLM返回错误 | Yes (2x) | Retry with fallback |

---

## Workflow Definition

### Paper Writing Workflow (DAG)

```yaml
# workflows/medical_paper.v1.yaml
name: medical_paper_workflow
version: v1
description: Clinical medical paper writing workflow

states:
  - id: init
    type: start
    next: literature_search
    
  - id: literature_search
    type: agent
    agent: literature_agent
    intent: collect_references
    next: supervisor_review_lit
    
  - id: supervisor_review_lit
    type: decision
    conditions:
      - if: "references.count >= 10"
        next: statistical_analysis
      - else:
        next: literature_search
        retry: true
        
  - id: statistical_analysis
    type: agent
    agent: stats_agent
    intent: run_analysis
    next: supervisor_review_stats
    
  - id: writing_phase
    type: parallel
    agents:
      - agent: writer_agent
        intent: write_introduction
      - agent: writer_agent
        intent: write_methods
      - agent: writer_agent
        intent: write_results
      - agent: writer_agent
        intent: write_discussion
    next: merge_sections
    
  - id: compliance_check
    type: agent
    agent: compliance_agent
    intent: check_consort
    next: supervisor_review_compliance
    
  - id: supervisor_review_compliance
    type: decision
    conditions:
      - if: "compliance.failed == 0"
        next: finalize
      - else:
        next: revision_phase
        
  - id: revision_phase
    type: agent
    agent: writer_agent
    intent: revise_sections
    input: compliance.failed_items
    next: compliance_check
    max_retries: 3
    
  - id: finalize
    type: end
    output: manuscript

error_handling:
  default_retry: 2
  timeout: 300s
  fallback: notify_user
```

---

## Data Models

### Database Schema

```python
# backend/app/models/medical_paper.py

class MedicalPaperTask(Base):
    __tablename__ = "medical_paper_tasks"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Task metadata
    title = Column(String(500), nullable=False)
    paper_type = Column(Enum(PaperType), nullable=False)  # RCT, META_ANALYSIS, COHORT
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    
    # Input
    research_question = Column(Text, nullable=False)
    study_design = Column(JSON)  # Design details
    raw_data = Column(JSON)  # Statistical data (optional)
    
    # Output
    manuscript = Column(JSON)  # Final manuscript sections
    references = Column(JSON)  # Literature references
    stats_report = Column(JSON)  # Statistical analysis report
    compliance_report = Column(JSON)  # Compliance check report
    
    # Workflow tracking
    current_step = Column(String(50))
    revision_round = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="medical_paper_tasks")
    messages = relationship("PaperTaskMessage", back_populates="task")


class PaperTaskMessage(Base):
    """A2A messages for audit trail"""
    __tablename__ = "paper_task_messages"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    task_id = Column(UUID, ForeignKey("medical_paper_tasks.id"))
    
    # A2A message fields
    sender = Column(String(50))
    receiver = Column(String(50))
    intent = Column(String(50))
    status = Column(String(20))
    input_payload = Column(JSON)
    output_payload = Column(JSON)
    error = Column(JSON)
    
    # Metrics
    latency_ms = Column(Integer)
    tokens_in = Column(Integer)
    tokens_out = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    task = relationship("MedicalPaperTask", back_populates="messages")
```

---

## Prompt Management

### Directory Structure

```
backend/app/services/medical_paper_agent/
├── prompts/
│   ├── supervisor/
│   │   ├── router.v1.yaml
│   │   └── evaluator.v1.yaml
│   ├── agents/
│   │   ├── literature/
│   │   │   ├── system.v1.yaml
│   │   │   └── search_strategy.v1.yaml
│   │   ├── stats/
│   │   │   ├── system.v1.yaml
│   │   │   └── analysis_plan.v1.yaml
│   │   ├── writer/
│   │   │   ├── system.v1.yaml
│   │   │   ├── introduction.v1.yaml
│   │   │   ├── methods.v1.yaml
│   │   │   ├── results.v1.yaml
│   │   │   └── discussion.v1.yaml
│   │   └── compliance/
│   │       ├── system.v1.yaml
│   │       ├── consort.v1.yaml
│   │       └── strobe.v1.yaml
│   └── schemas/
│       └── a2a_message.v1.json
├── workflows/
│   └── medical_paper.v1.yaml
└── tools/
    ├── pubmed_tools.py
    ├── stats_tools.py
    ├── writing_tools.py
    └── compliance_tools.py
```

---

## Metrics & Observability

### Key Metrics

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `medical_paper_task_total` | Counter | status, paper_type | 任务总数 |
| `medical_paper_task_duration_seconds` | Histogram | paper_type | 任务耗时 |
| `medical_paper_agent_calls_total` | Counter | agent, intent, status | Agent调用次数 |
| `medical_paper_agent_latency_seconds` | Histogram | agent | Agent延迟 |
| `medical_paper_compliance_score` | Gauge | checklist_type | 合规得分 |
| `medical_paper_revision_rounds` | Histogram | paper_type | 修订轮次 |

### Tracing

复用 `add-personal-secretary-agent` 的 tracing 基础设施：
- `trace_id` 跨越整个任务
- 每个 A2A 消息有 `correlation_id`
- 支持 `@trace_tool_call` 装饰器

---

## Open Questions

1. **PubMed API 访问方式**
   - 直接使用 NCBI E-utilities？
   - 还是封装为 MCP Server？
   - → 建议先直接调用，后续可迁移到 MCP

2. **统计分析数据输入**
   - 用户上传原始数据？
   - 还是提供摘要统计？
   - → 先支持摘要统计，后续支持原始数据上传

3. **论文模板扩展**
   - 除 RCT (CONSORT) 外，还需支持哪些？
   - → v1 先支持 RCT, Meta-analysis, Cohort Study

4. **图表生成**
   - 是否需要自动生成 Figure/Table？
   - → v1 不包含，生成描述性文字即可

---

## Implementation Notes (Post-Build)

### Resolved Open Questions

1. **PubMed API**: Direct E-utilities via BioPython `Entrez` module + httpx for ClinicalTrials.gov
2. **Statistical data**: Summary statistics via tool parameters; raw data deferred
3. **Templates**: v1 supports RCT (CONSORT 25 items), Cohort (STROBE 22 items), Meta-analysis (PRISMA 27 items)
4. **Figures**: Not included in v1

### Final File Layout

```
backend/app/services/medical_paper_agent/
├── __init__.py
├── a2a.py                    # A2A message contract + retry logic
├── metrics.py                # Prometheus RED + business metrics
├── prompt_loader.py          # Versioned YAML prompt loading with lru_cache
├── state.py                  # MedicalPaperState (TypedDict extends MessagesState)
├── supervisor.py             # MedicalPaperSupervisor class (hub-and-spoke)
├── workflow.py               # Convenience factory + paper type registry
├── prompts/
│   ├── supervisor/           # router.v1.yaml, evaluator.v1.yaml
│   ├── agents/
│   │   ├── literature/       # system.v1.yaml, search_strategy.v1.yaml
│   │   ├── stats/            # system.v1.yaml, analysis_plan.v1.yaml
│   │   ├── writer/           # system.v1.yaml, introduction/methods/results/discussion.v1.yaml
│   │   └── compliance/       # system.v1.yaml, consort.v1.yaml, strobe.v1.yaml
│   └── schemas/              # a2a_message.v1.json
├── sub_agents/
│   ├── __init__.py
│   ├── literature.py         # 4 tools: search_pubmed, search_clinicaltrials, get_abstract, format_citation
│   ├── stats.py              # 4 tools: run_ttest, run_chi_square, run_survival, calculate_sample_size
│   ├── writer.py             # 3 tools: write_section, revise_section, merge_sections
│   └── compliance.py         # 3 tools: check_compliance, generate_report, get_checklist
└── tools/
    ├── __init__.py
    ├── literature_tools.py   # PubMed E-utilities, ClinicalTrials.gov API
    ├── stats_tools.py        # scipy-based statistical tests
    ├── writing_tools.py      # Prompt generators for IMRAD sections
    └── compliance_tools.py   # CONSORT/STROBE/PRISMA checklists (25/22/27 items)
```

### Key Design Decisions

1. **TypedDict state** — `MedicalPaperState` extends `MessagesState` (TypedDict, not Pydantic).
   LangGraph passes state as plain dicts; TypedDict provides type hints only.

2. **Hub-and-spoke topology** — Supervisor uses `create_react_agent` with `destinations` parameter.
   Every sub-agent returns to supervisor for next-step routing.

3. **Background execution** — API creates DB record immediately, runs pipeline via FastAPI `BackgroundTasks`.
   Frontend polls via GET or streams via SSE.

4. **Graceful degradation** — Stats tools handle missing scipy with error dict return.
   Literature tools handle API failures with empty result + error field.

5. **Prompt versioning** — All prompts in YAML files with version suffix (e.g., `system.v1.yaml`).
   Loaded with `lru_cache` for performance; restart to pick up changes.

### Sequence Diagram: Happy Path

```
User                API              Supervisor        Literature    Stats    Writer    Compliance
 │                   │                   │                │            │         │          │
 │──POST /create────▶│                   │                │            │         │          │
 │                   │──create task──────▶│                │            │         │          │
 │◀──TaskResponse────│                   │                │            │         │          │
 │                   │                   │──search refs───▶│            │         │          │
 │                   │                   │◀──references────│            │         │          │
 │                   │                   │──run analysis──────────────▶│         │          │
 │                   │                   │◀──stats report──────────────│         │          │
 │                   │                   │──write IMRAD────────────────────────▶│          │
 │                   │                   │◀──manuscript─────────────────────────│          │
 │                   │                   │──check compliance─────────────────────────────▶│
 │                   │                   │◀──compliance report───────────────────────────│
 │                   │                   │                │            │         │          │
 │                   │                   │  [score ≥ 0.8? → END]       │         │          │
 │                   │                   │  [score < 0.8? → revise → re-check, max 3x]    │
 │                   │                   │                │            │         │          │
 │──GET /{task_id}──▶│◀──completed───────│                │            │         │          │
 │◀──full results────│                   │                │            │         │          │
```

### Error Handling Strategy

- **VALIDATION_ERROR**: Return immediately to user (bad input)
- **TOOL_ERROR**: Retry up to 3x with exponential backoff (1s, 2s, 4s)
- **TIMEOUT**: Retry 2x with longer backoff (5s, 10s)
- **RATE_LIMIT**: Retry 3x with aggressive backoff (10s, 20s, 40s)
- **LLM_ERROR**: Retry 2x with backoff (2s, 4s)

All errors classified in `a2a.py:classify_error()` with retry decisions in `should_retry()`.
