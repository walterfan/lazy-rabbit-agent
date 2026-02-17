# Change: Add Medical Paper Writing Assistant

## Why

医学论文写作是一个复杂的多步骤流程，需要文献检索、统计分析、IMRAD结构撰写、以及CONSORT/STROBE合规审查等多个环节。传统方式依赖人工协调，效率低且容易出错。

基于 `add-personal-secretary-agent` 已建立的LangChain基础设施，本提案引入一个多Agent协作系统（Multi-Agent System），采用 Supervisor + SubAgent 模式，将复杂的论文写作流程拆分为独立、可测试、可替换的子任务。

## What Changes

### New Components

1. **MedicalPaperAgent (Supervisor)** - 论文通讯作者/主编角色
   - 任务拆分与分派
   - Workflow 编排（顺序/并行/重试）
   - 成果汇总与验收

2. **SubAgents (SRP - Single Responsibility Principle)**
   - `LiteratureAgent`: PubMed/ClinicalTrials.gov 文献检索
   - `StatsAgent`: 统计分析（t-test, Cox regression等）
   - `WriterAgent`: IMRAD结构论文撰写
   - `ComplianceAgent`: CONSORT/STROBE合规审查

3. **A2A Communication Contract** - Agent间结构化通讯
   - Schema + Version
   - Correlation ID 可追踪
   - Error分类 + 重试策略

4. **Workflow Engine** - 基于 LangGraph 的 DAG 工作流
   - 声明式流程定义
   - 支持反馈循环（合规审查失败 → 修订 → 重新审查）
   - 超时/重试/兜底策略

5. **MCP Tool Integration** - 标准化工具接入
   - PubMed Search MCP Server
   - Statistical Analysis MCP Server
   - Compliance Check Tools

### API Endpoints

- `POST /api/v1/medical-paper/create` - 创建论文写作任务
- `GET /api/v1/medical-paper/{task_id}` - 获取任务状态
- `GET /api/v1/medical-paper/{task_id}/stream` - 流式获取写作进度
- `POST /api/v1/medical-paper/{task_id}/revise` - 提交修订意见
- `GET /api/v1/medical-paper/templates` - 获取论文模板列表

### Database Models

- `MedicalPaperTask` - 论文写作任务
- `PaperSection` - 论文章节内容
- `LiteratureReference` - 文献引用
- `ComplianceReport` - 合规审查报告

### Frontend Components

- `MedicalPaperWorkspace.vue` - 论文写作工作台
- `LiteraturePanel.vue` - 文献管理面板
- `OutlineEditor.vue` - 大纲编辑器
- `ComplianceChecker.vue` - 合规检查面板
- `PaperPreview.vue` - 论文预览

## Impact

- **Affected specs**: None (new capability)
- **Affected code**:
  - `backend/app/services/medical_paper_agent/` (new)
  - `backend/app/api/v1/endpoints/medical_paper.py` (new)
  - `backend/app/models/medical_paper.py` (new)
  - `backend/app/schemas/medical_paper.py` (new)
  - `frontend/src/views/MedicalPaper.vue` (new)
  - `frontend/src/components/medical-paper/` (new)
  - `frontend/src/stores/medicalPaper.ts` (new)

## Dependencies

- Requires `add-personal-secretary-agent` to be completed (reuses LangChain infrastructure, tracing, metrics)
- Python packages: `langgraph`, `biopython` (for PubMed), `scipy/statsmodels` (for statistics)
- External APIs: NCBI E-utilities (PubMed), optional MCP servers

## Risks / Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| PubMed API rate limits | Medium | Implement caching, batch requests |
| Statistical analysis accuracy | High | Use validated libraries (scipy, statsmodels), output confidence intervals |
| Compliance check completeness | High | Use CONSORT 2025 official checklist, allow manual override |
| Long-running tasks timeout | Medium | Async execution, progress streaming, task persistence |
| LLM hallucination in writing | High | Require citations for all claims, cross-check with literature |
