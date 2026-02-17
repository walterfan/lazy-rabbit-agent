"""
Personal Secretary AI Agent package.

Architecture: Supervisor + SubAgent pattern (multi-agent workflow)

┌──────────────────────────────────────────────┐
│  SecretaryAgent (Supervisor)                 │
│  Routes via LangGraph StateGraph             │
└──┬────────────┬────────────────┬─────────────┘
   │            │                │
   ▼            ▼                ▼
Learning    Productivity     Utility
 Agent        Agent           Agent
 (SRP)        (SRP)           (SRP)

Modules:
- prompts/    : YAML prompt templates (file + Git versioning)
- sub_agents/ : SRP sub-agents (learning, productivity, utility)
- tools/      : Tool implementations (MCP-ready, stateless where possible)
- a2a.py      : A2A message contract (structured inter-agent communication)
- tracing.py  : Observability (LLM call tracing, tool call tracing)
- metrics.py  : Prometheus metrics (RED, tool, business, resource)
- agent.py    : Supervisor agent + LangGraph workflow

Reference: journal_20260206_ai-agent-workflow.md
"""

from app.services.secretary_agent.prompts import get_prompt, reload_prompts

__all__ = [
    "get_prompt",
    "reload_prompts",
]
