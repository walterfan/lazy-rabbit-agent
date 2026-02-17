"""Tests for the Medical Paper Workflow — Phase 6 TDD tests.

Tests workflow compilation, state management, and routing logic.
These tests verify the structural correctness without requiring LLM calls.
"""

import pytest

from app.services.medical_paper_agent.state import MedicalPaperState
from app.services.medical_paper_agent.supervisor import (
    COMPLIANCE_AGENT,
    COMPLIANCE_THRESHOLD,
    LITERATURE_AGENT,
    MAX_ROUTING_ITERATIONS,
    MIN_REFERENCES,
    STATS_AGENT,
    SUB_AGENT_NAMES,
    SUPERVISOR,
    WRITER_AGENT,
)
from app.services.medical_paper_agent.workflow import (
    get_available_paper_types,
)


class TestMedicalPaperState:
    """Test the extended state TypedDict."""

    def test_state_is_a_dict(self):
        """MedicalPaperState is a TypedDict — instances are plain dicts."""
        state: MedicalPaperState = {
            "messages": [],
            "paper_type": "rct",
            "current_step": "literature",
        }
        assert isinstance(state, dict)
        assert state["paper_type"] == "rct"

    def test_state_with_all_fields(self):
        state: MedicalPaperState = {
            "messages": [],
            "task_id": "task-123",
            "user_id": 1,
            "paper_type": "meta_analysis",
            "research_question": "Does X improve Y?",
            "study_design": {"type": "double-blind"},
            "raw_data": {},
            "references": [],
            "stats_report": {},
            "manuscript_sections": {},
            "compliance_report": {},
            "current_step": "stats",
            "revision_round": 1,
            "max_revisions": 3,
            "next_agent": "",
            "errors": [],
        }
        assert state["paper_type"] == "meta_analysis"
        assert state["current_step"] == "stats"
        assert state["revision_round"] == 1

    def test_state_references_mutable(self):
        state: MedicalPaperState = {
            "messages": [],
            "references": [],
        }
        state["references"].append({"pmid": "123", "title": "Test"})
        assert len(state["references"]) == 1

    def test_state_inherits_messages_annotation(self):
        """MedicalPaperState extends MessagesState which has 'messages' key."""
        annotations = MedicalPaperState.__annotations__
        assert "paper_type" in annotations
        assert "current_step" in annotations
        assert "references" in annotations

    def test_state_has_message_support(self):
        from langchain_core.messages import HumanMessage

        msg = HumanMessage(content="Hello")
        state: MedicalPaperState = {"messages": [msg]}
        assert len(state["messages"]) == 1


class TestWorkflowConstants:
    """Test supervisor constants are properly defined."""

    def test_agent_names(self):
        assert SUPERVISOR == "supervisor"
        assert LITERATURE_AGENT == "literature_agent"
        assert STATS_AGENT == "stats_agent"
        assert WRITER_AGENT == "writer_agent"
        assert COMPLIANCE_AGENT == "compliance_agent"

    def test_sub_agent_list(self):
        assert len(SUB_AGENT_NAMES) == 4
        assert LITERATURE_AGENT in SUB_AGENT_NAMES
        assert STATS_AGENT in SUB_AGENT_NAMES
        assert WRITER_AGENT in SUB_AGENT_NAMES
        assert COMPLIANCE_AGENT in SUB_AGENT_NAMES

    def test_routing_limit(self):
        assert MAX_ROUTING_ITERATIONS == 20

    def test_min_references(self):
        assert MIN_REFERENCES == 10

    def test_compliance_threshold(self):
        assert COMPLIANCE_THRESHOLD == 0.8


class TestAvailablePaperTypes:
    """Test the paper type registry."""

    def test_returns_three_types(self):
        types = get_available_paper_types()
        assert len(types) == 3

    def test_rct_type(self):
        types = get_available_paper_types()
        rct = next(t for t in types if t["type"] == "rct")
        assert rct["checklist"] == "CONSORT"
        assert "randomised" in rct["description"].lower()

    def test_cohort_type(self):
        types = get_available_paper_types()
        cohort = next(t for t in types if t["type"] == "cohort")
        assert cohort["checklist"] == "STROBE"
        assert "observational" in cohort["description"].lower()

    def test_meta_analysis_type(self):
        types = get_available_paper_types()
        meta = next(t for t in types if t["type"] == "meta_analysis")
        assert meta["checklist"] == "PRISMA"
        assert "systematic" in meta["description"].lower()

    def test_all_types_have_required_fields(self):
        types = get_available_paper_types()
        for t in types:
            assert "type" in t
            assert "name" in t
            assert "checklist" in t
            assert "description" in t
