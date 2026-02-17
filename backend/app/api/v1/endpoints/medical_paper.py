"""
API endpoints for the Medical Paper Writing Assistant.

Provides endpoints for:
- Creating paper writing tasks
- Checking task status
- Streaming progress (SSE)
- Submitting revisions
- Listing paper templates
"""

import json
import logging
import time
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.models.medical_paper import MedicalPaperTask, PaperTaskStatus, PaperType
from app.models.user import User
from app.schemas.medical_paper import (
    CreateTaskRequest,
    RevisionRequest,
    TaskListResponse,
    TaskResponse,
    TemplateInfo,
    TemplateListResponse,
)
from app.services.medical_paper_agent.supervisor import MedicalPaperSupervisor
from app.services.medical_paper_agent.workflow import get_available_paper_types

logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================================================
# Template Endpoints (must be before /{task_id} to avoid route shadowing)
# ============================================================================


@router.get(
    "/templates",
    response_model=TemplateListResponse,
    summary="List paper type templates",
)
async def list_templates(
    current_user: User = Depends(get_current_active_user),
):
    """List available paper type templates."""
    types = get_available_paper_types()
    return TemplateListResponse(
        templates=[
            TemplateInfo(
                paper_type=t["type"],
                name=t["name"],
                description=t["description"],
                checklist=t["checklist"],
            )
            for t in types
        ]
    )


# ============================================================================
# Task Endpoints
# ============================================================================


@router.post(
    "/create",
    response_model=TaskResponse,
    status_code=200,
    summary="Create a paper writing task",
    responses={
        400: {"description": "Invalid paper_type"},
        401: {"description": "Not authenticated"},
    },
)
async def create_task(
    request: CreateTaskRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new medical paper writing task.

    The task runs asynchronously in the background. Use the GET endpoint
    or streaming endpoint to monitor progress.

    **Supported paper types:** rct, cohort, meta_analysis
    """
    # Validate paper_type
    valid_types = {t["type"] for t in get_available_paper_types()}
    if request.paper_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid paper_type '{request.paper_type}'. "
            f"Must be one of: {', '.join(valid_types)}",
        )

    # Create database record
    task = MedicalPaperTask(
        user_id=current_user.id,
        title=request.title,
        paper_type=request.paper_type,
        status=PaperTaskStatus.PENDING.value,
        research_question=request.research_question,
        study_design=request.study_design,
        current_step="literature",
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    # Schedule background execution
    background_tasks.add_task(
        _run_paper_pipeline,
        task_id=str(task.id),
        paper_type=request.paper_type,
        research_question=request.research_question,
        study_design=request.study_design,
        raw_data=request.raw_data,
        user_id=current_user.id,
    )

    return _task_to_response(task)


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Get task status",
    responses={404: {"description": "Task not found"}},
)
async def get_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get the status and results of a medical paper task.

    Returns the full task including manuscript sections, references,
    statistics report, and compliance report when completed.
    """
    task = _get_user_task(db, task_id, current_user.id)
    return _task_to_response(task)


@router.get(
    "/{task_id}/stream",
    summary="Stream task progress (SSE)",
    responses={
        400: {"description": "Task already completed or failed"},
        404: {"description": "Task not found"},
    },
)
async def stream_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Stream progress of a medical paper task via SSE.

    Returns Server-Sent Events with:
    - type: "token" - streaming text
    - type: "tool_call" - tool being called
    - type: "agent_start" / "agent_end" - sub-agent transitions
    - type: "step_complete" - pipeline step completed
    - type: "done" - task completed
    - type: "error" - error occurred
    """
    task = _get_user_task(db, task_id, current_user.id)

    if task.status == PaperTaskStatus.COMPLETED.value:
        raise HTTPException(status_code=400, detail="Task already completed")
    if task.status == PaperTaskStatus.FAILED.value:
        raise HTTPException(status_code=400, detail="Task has failed")

    supervisor = MedicalPaperSupervisor(
        user_id=current_user.id,
        task_id=task_id,
        db=db,
    )

    async def event_generator():
        try:
            async for event in supervisor.run_stream(
                paper_type=task.paper_type,
                research_question=task.research_question,
                study_design=task.study_design,
            ):
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            logger.error(f"Streaming error for task {task_id}: {e}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.post(
    "/{task_id}/revise",
    response_model=TaskResponse,
    summary="Submit revision feedback",
    responses={
        400: {"description": "Task not in revisable state"},
        404: {"description": "Task not found"},
    },
)
async def revise_task(
    task_id: str,
    request: RevisionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Submit revision feedback for a completed or in-revision task.

    Re-runs the compliance check with the given feedback.
    """
    task = _get_user_task(db, task_id, current_user.id)

    if task.status not in (
        PaperTaskStatus.COMPLETED.value,
        PaperTaskStatus.REVISION.value,
    ):
        raise HTTPException(
            status_code=400,
            detail="Task must be in COMPLETED or REVISION status to revise",
        )

    # Update task status
    task.status = PaperTaskStatus.REVISION.value
    task.revision_round = (task.revision_round or 0) + 1
    db.commit()

    # Schedule background revision
    background_tasks.add_task(
        _run_paper_pipeline,
        task_id=str(task.id),
        paper_type=task.paper_type,
        research_question=task.research_question,
        study_design=task.study_design,
        user_id=current_user.id,
    )

    db.refresh(task)
    return _task_to_response(task)


@router.get(
    "",
    response_model=TaskListResponse,
    summary="List user's paper tasks",
)
async def list_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List the current user's medical paper tasks."""
    offset = (page - 1) * page_size

    query = (
        db.query(MedicalPaperTask)
        .filter(MedicalPaperTask.user_id == current_user.id)
        .order_by(MedicalPaperTask.created_at.desc())
    )
    total = query.count()
    tasks = query.offset(offset).limit(page_size).all()

    return TaskListResponse(
        tasks=[_task_to_response(t) for t in tasks],
        total=total,
    )


# ============================================================================
# Internal helpers
# ============================================================================


def _get_user_task(db: Session, task_id: str, user_id: int) -> MedicalPaperTask:
    """Get a task belonging to the specified user, or raise 404."""
    task = (
        db.query(MedicalPaperTask)
        .filter(
            MedicalPaperTask.id == task_id,
            MedicalPaperTask.user_id == user_id,
        )
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


def _task_to_response(task: MedicalPaperTask) -> TaskResponse:
    """Convert a MedicalPaperTask model to a TaskResponse schema."""
    return TaskResponse(
        id=str(task.id),
        user_id=task.user_id,
        title=task.title,
        paper_type=task.paper_type,
        status=task.status,
        research_question=task.research_question,
        study_design=task.study_design,
        current_step=task.current_step,
        revision_round=task.revision_round or 0,
        manuscript=task.manuscript,
        references=task.references,
        stats_report=task.stats_report,
        compliance_report=task.compliance_report,
        created_at=str(task.created_at) if task.created_at else None,
        updated_at=str(task.updated_at) if task.updated_at else None,
        completed_at=str(task.completed_at) if task.completed_at else None,
    )


async def _run_paper_pipeline(
    task_id: str,
    paper_type: str,
    research_question: str,
    study_design: Optional[dict] = None,
    raw_data: Optional[dict] = None,
    user_id: Optional[int] = None,
):
    """Background task to run the full paper writing pipeline."""
    from app.db.base import SessionLocal

    db = SessionLocal()
    try:
        # Update status to RUNNING
        task = db.query(MedicalPaperTask).filter(MedicalPaperTask.id == task_id).first()
        if not task:
            logger.error(f"Task {task_id} not found for pipeline execution")
            return

        task.status = PaperTaskStatus.RUNNING.value
        db.commit()

        # Run supervisor
        supervisor = MedicalPaperSupervisor(
            user_id=user_id,
            task_id=task_id,
            db=db,
        )

        result = await supervisor.run(
            paper_type=paper_type,
            research_question=research_question,
            study_design=study_design,
            raw_data=raw_data,
        )

        # Update task with results
        task.status = PaperTaskStatus.COMPLETED.value
        task.manuscript = result.get("manuscript_sections")
        task.references = result.get("references")
        task.stats_report = result.get("stats_report")
        task.compliance_report = result.get("compliance_report")
        task.revision_round = result.get("revision_rounds", 0)
        db.commit()

        logger.info(f"Task {task_id} completed successfully")

    except Exception as e:
        logger.error(f"Task {task_id} failed: {e}", exc_info=True)
        task = db.query(MedicalPaperTask).filter(MedicalPaperTask.id == task_id).first()
        if task:
            task.status = PaperTaskStatus.FAILED.value
            db.commit()

    finally:
        db.close()
