"""
Medical Paper State — Extended LangGraph state for the paper writing workflow.

Tracks all artifacts produced during the multi-stage pipeline:
  Literature → Stats → Writing → Compliance → (Revision loop)

Note: MessagesState is a TypedDict, so MedicalPaperState is also a TypedDict.
LangGraph passes state as plain dicts; the TypedDict provides type hints only.
"""

from typing import Any

from langgraph.graph import MessagesState


class MedicalPaperState(MessagesState):
    """
    Extended state for the medical paper writing workflow.

    Inherits MessagesState (message history) and adds domain-specific fields
    for tracking artifacts across the pipeline stages.
    """

    # --- Task identification ---
    task_id: str
    user_id: int

    # --- Input parameters ---
    paper_type: str  # rct, cohort, meta_analysis
    research_question: str
    study_design: dict[str, Any]
    raw_data: dict[str, Any]

    # --- Pipeline artifacts ---
    references: list[dict[str, Any]]
    stats_report: dict[str, Any]
    manuscript_sections: dict[str, str]
    compliance_report: dict[str, Any]

    # --- Workflow control ---
    current_step: str  # literature, stats, writer, compliance, done
    revision_round: int
    max_revisions: int
    next_agent: str  # routing target set by supervisor

    # --- Error tracking ---
    errors: list[str]
