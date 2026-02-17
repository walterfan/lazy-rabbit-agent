"""
Medical Paper Workflow — Convenience factory for creating the paper pipeline.

This module provides a simple entry point for creating and running
the medical paper writing workflow without manually instantiating
the supervisor.
"""

import logging
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.services.medical_paper_agent.supervisor import MedicalPaperSupervisor

logger = logging.getLogger("medical_paper_agent")


async def create_paper_task(
    paper_type: str,
    research_question: str,
    study_design: Optional[dict[str, Any]] = None,
    raw_data: Optional[dict[str, Any]] = None,
    user_id: Optional[int] = None,
    task_id: Optional[str] = None,
    db: Optional[Session] = None,
) -> dict[str, Any]:
    """
    Create and run a medical paper writing task.

    This is the main entry point for the paper writing pipeline.
    It creates a supervisor, runs the full pipeline, and returns results.

    Args:
        paper_type: Type of paper (rct, cohort, meta_analysis)
        research_question: The research question
        study_design: Study design parameters
        raw_data: Raw data for statistical analysis
        user_id: ID of the requesting user
        task_id: ID of the paper task
        db: Database session

    Returns:
        Dictionary with manuscript, references, stats, compliance report
    """
    supervisor = MedicalPaperSupervisor(
        user_id=user_id,
        task_id=task_id,
        db=db,
    )

    return await supervisor.run(
        paper_type=paper_type,
        research_question=research_question,
        study_design=study_design,
        raw_data=raw_data,
    )


def get_available_paper_types() -> list[dict[str, str]]:
    """Return the list of supported paper types with descriptions."""
    return [
        {
            "type": "rct",
            "name": "Randomised Controlled Trial",
            "checklist": "CONSORT",
            "description": "For reporting parallel group randomised trials",
        },
        {
            "type": "cohort",
            "name": "Cohort / Observational Study",
            "checklist": "STROBE",
            "description": "For reporting observational studies (cohort, case-control, cross-sectional)",
        },
        {
            "type": "meta_analysis",
            "name": "Systematic Review / Meta-Analysis",
            "checklist": "PRISMA",
            "description": "For reporting systematic reviews and meta-analyses",
        },
    ]
