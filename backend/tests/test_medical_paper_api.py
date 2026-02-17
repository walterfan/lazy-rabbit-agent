"""Tests for the Medical Paper API endpoints — Phase 7 TDD tests.

Tests endpoint structure, schema validation, and helper functions.
These tests verify structural correctness without requiring a running server.
"""

import pytest

from app.schemas.medical_paper import (
    CreateTaskRequest,
    RevisionRequest,
    TaskListResponse,
    TaskResponse,
    TemplateInfo,
    TemplateListResponse,
)
from app.services.medical_paper_agent.workflow import get_available_paper_types


class TestCreateTaskRequest:
    """Test the CreateTaskRequest schema validation."""

    def test_valid_request(self):
        req = CreateTaskRequest(
            title="Effect of Drug X on Blood Pressure",
            paper_type="rct",
            research_question="Does Drug X reduce systolic blood pressure compared to placebo?",
        )
        assert req.title == "Effect of Drug X on Blood Pressure"
        assert req.paper_type == "rct"

    def test_default_paper_type(self):
        req = CreateTaskRequest(
            title="Test Paper",
            research_question="Does X improve Y in patients with Z?",
        )
        assert req.paper_type == "rct"

    def test_with_study_design(self):
        req = CreateTaskRequest(
            title="Test",
            research_question="Does X improve Y in patients with Z?",
            study_design={"type": "double-blind", "arms": 2, "duration_weeks": 12},
        )
        assert req.study_design["arms"] == 2

    def test_title_required(self):
        with pytest.raises(Exception):
            CreateTaskRequest(
                research_question="Does X improve Y?",
            )

    def test_research_question_min_length(self):
        with pytest.raises(Exception):
            CreateTaskRequest(
                title="Test",
                research_question="Short",  # < 10 chars
            )


class TestRevisionRequest:
    """Test the RevisionRequest schema."""

    def test_valid_revision(self):
        req = RevisionRequest(
            feedback="Please add confidence intervals to the results section",
        )
        assert "confidence" in req.feedback

    def test_with_specific_sections(self):
        req = RevisionRequest(
            feedback="Fix these sections",
            sections_to_revise=["results", "discussion"],
        )
        assert len(req.sections_to_revise) == 2

    def test_feedback_required(self):
        with pytest.raises(Exception):
            RevisionRequest()


class TestTaskResponse:
    """Test the TaskResponse schema."""

    def test_full_response(self):
        resp = TaskResponse(
            id="task-123",
            user_id=1,
            title="Test Paper",
            paper_type="rct",
            status="running",
            research_question="Does X improve Y?",
            current_step="literature",
            revision_round=0,
        )
        assert resp.id == "task-123"
        assert resp.status == "running"

    def test_with_results(self):
        resp = TaskResponse(
            id="task-456",
            user_id=1,
            title="Completed Paper",
            paper_type="cohort",
            status="completed",
            research_question="Is X associated with Y?",
            manuscript={"introduction": "Background..."},
            references=[{"pmid": "123", "title": "Ref 1"}],
            compliance_report={"overall_score": 0.92},
        )
        assert resp.manuscript is not None
        assert len(resp.references) == 1


class TestTaskListResponse:
    """Test the TaskListResponse schema."""

    def test_empty_list(self):
        resp = TaskListResponse(tasks=[], total=0)
        assert len(resp.tasks) == 0

    def test_with_tasks(self):
        tasks = [
            TaskResponse(
                id=f"task-{i}",
                user_id=1,
                title=f"Paper {i}",
                paper_type="rct",
                status="pending",
                research_question="Q?",
            )
            for i in range(3)
        ]
        resp = TaskListResponse(tasks=tasks, total=3)
        assert resp.total == 3


class TestTemplateListResponse:
    """Test the template listing response."""

    def test_templates_from_paper_types(self):
        types = get_available_paper_types()
        templates = [
            TemplateInfo(
                paper_type=t["type"],
                name=t["name"],
                description=t["description"],
                checklist=t["checklist"],
            )
            for t in types
        ]
        resp = TemplateListResponse(templates=templates)
        assert len(resp.templates) == 3
        assert resp.templates[0].checklist == "CONSORT"


class TestApiModuleImports:
    """Test that the API module can be imported without errors."""

    def test_import_endpoint_module(self):
        from app.api.v1.endpoints import medical_paper
        assert hasattr(medical_paper, "router")
        assert hasattr(medical_paper, "create_task")
        assert hasattr(medical_paper, "get_task")
        assert hasattr(medical_paper, "stream_task")
        assert hasattr(medical_paper, "revise_task")
        assert hasattr(medical_paper, "list_templates")
