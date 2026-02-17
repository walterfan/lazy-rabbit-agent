"""
Tests for Medical Paper models.

TDD - Red Phase: Define expected behavior for MedicalPaperTask and PaperTaskMessage.
"""

from uuid import uuid4

from app.models.medical_paper import (
    MedicalPaperTask,
    PaperTaskMessage,
    PaperTaskStatus,
    PaperType,
)


class TestPaperType:
    """Test PaperType enum values."""

    def test_rct_value(self):
        assert PaperType.RCT == "rct"

    def test_meta_analysis_value(self):
        assert PaperType.META_ANALYSIS == "meta_analysis"

    def test_cohort_value(self):
        assert PaperType.COHORT == "cohort"


class TestPaperTaskStatus:
    """Test PaperTaskStatus enum values."""

    def test_pending(self):
        assert PaperTaskStatus.PENDING == "pending"

    def test_running(self):
        assert PaperTaskStatus.RUNNING == "running"

    def test_revision(self):
        assert PaperTaskStatus.REVISION == "revision"

    def test_completed(self):
        assert PaperTaskStatus.COMPLETED == "completed"

    def test_failed(self):
        assert PaperTaskStatus.FAILED == "failed"


class TestMedicalPaperTask:
    """Test MedicalPaperTask model creation and behavior."""

    def test_create_task(self):
        task = MedicalPaperTask(
            user_id=1,
            title="Effect of Drug X on Condition Y",
            paper_type=PaperType.RCT.value,
            research_question="Does Drug X improve outcomes in patients with Condition Y?",
        )
        assert task.title == "Effect of Drug X on Condition Y"
        assert task.paper_type == "rct"
        assert task.research_question == "Does Drug X improve outcomes in patients with Condition Y?"

    def test_status_values(self):
        task = MedicalPaperTask(
            user_id=1,
            title="Test",
            research_question="Test question",
            status=PaperTaskStatus.PENDING.value,
        )
        assert task.status == "pending"

    def test_revision_round(self):
        task = MedicalPaperTask(
            user_id=1,
            title="Test",
            research_question="Test question",
            status=PaperTaskStatus.RUNNING.value,
            revision_round=2,
        )
        assert task.revision_round == 2

    def test_to_dict(self):
        task = MedicalPaperTask(
            user_id=1,
            title="My Paper",
            paper_type=PaperType.COHORT.value,
            research_question="Is exposure X associated with outcome Y?",
            study_design={"type": "retrospective"},
        )
        d = task.to_dict()
        assert d["title"] == "My Paper"
        assert d["paper_type"] == "cohort"
        assert d["study_design"] == {"type": "retrospective"}
        assert d["revision_round"] is None or d["revision_round"] == 0

    def test_repr(self):
        task = MedicalPaperTask(
            user_id=1,
            title="Test Paper",
            research_question="Q",
        )
        r = repr(task)
        assert "MedicalPaperTask" in r
        assert "Test Paper" in r

    def test_json_fields_accept_dicts(self):
        task = MedicalPaperTask(
            user_id=1,
            title="Test",
            research_question="Q",
            manuscript={"introduction": "Background..."},
            references=[{"pmid": "12345", "title": "Ref 1"}],
            stats_report={"primary": {"p_value": 0.03}},
            compliance_report={"passed": 20, "failed": 2},
        )
        assert task.manuscript["introduction"] == "Background..."
        assert len(task.references) == 1
        assert task.stats_report["primary"]["p_value"] == 0.03
        assert task.compliance_report["failed"] == 2


class TestPaperTaskMessage:
    """Test PaperTaskMessage model for A2A audit trail."""

    def test_create_message(self):
        task_id = uuid4()
        msg = PaperTaskMessage(
            task_id=task_id,
            sender="supervisor",
            receiver="literature_agent",
            intent="collect_references",
            status="ok",
            input_payload={"query": "Drug X RCT"},
        )
        assert msg.sender == "supervisor"
        assert msg.receiver == "literature_agent"
        assert msg.intent == "collect_references"
        assert msg.status == "ok"

    def test_message_with_error(self):
        msg = PaperTaskMessage(
            task_id=uuid4(),
            sender="stats_agent",
            receiver="supervisor",
            intent="run_analysis_response",
            status="error",
            error={"type": "TOOL_ERROR", "message": "Insufficient data"},
        )
        assert msg.status == "error"
        assert msg.error["type"] == "TOOL_ERROR"

    def test_message_with_metrics(self):
        msg = PaperTaskMessage(
            task_id=uuid4(),
            sender="writer_agent",
            receiver="supervisor",
            intent="write_introduction_response",
            status="ok",
            latency_ms=5200,
            tokens_in=1500,
            tokens_out=3000,
        )
        assert msg.latency_ms == 5200
        assert msg.tokens_in == 1500
        assert msg.tokens_out == 3000

    def test_to_dict(self):
        task_id = uuid4()
        msg = PaperTaskMessage(
            task_id=task_id,
            sender="supervisor",
            receiver="compliance_agent",
            intent="check_consort",
            status="ok",
            output_payload={"score": 0.92},
        )
        d = msg.to_dict()
        assert d["sender"] == "supervisor"
        assert d["intent"] == "check_consort"
        assert d["output_payload"]["score"] == 0.92

    def test_repr(self):
        msg = PaperTaskMessage(
            task_id=uuid4(),
            sender="supervisor",
            receiver="literature_agent",
            intent="collect_references",
            status="ok",
        )
        r = repr(msg)
        assert "PaperTaskMessage" in r
        assert "supervisor" in r
