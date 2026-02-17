"""Tests for Medical Paper metrics — Phase 8 TDD tests."""

import time

import pytest

from app.services.medical_paper_agent.metrics import (
    ACTIVE_STREAMS,
    ACTIVE_TASKS,
    AGENT_CALLS_TOTAL,
    AGENT_INFO,
    AGENT_LATENCY,
    AGENT_TOOL_CALLS,
    COMPLIANCE_SCORE,
    MANUSCRIPT_WORD_COUNT,
    REFERENCES_COUNT,
    REVISION_ROUNDS,
    STEP_DURATION,
    STEP_TOTAL,
    TASK_DURATION,
    TASK_ERRORS_TOTAL,
    TASK_TOTAL,
    record_agent_call,
    record_agent_tool_call,
    record_compliance_score,
    record_manuscript_word_count,
    record_references_count,
    record_revision_rounds,
    record_step,
    record_task_completed,
    record_task_created,
    record_task_failed,
    stream_ended,
    stream_started,
    track_agent,
    track_step,
    track_streaming,
)


class TestMetricsRegistration:
    """Test that all metrics are properly defined."""

    def test_task_total_counter(self):
        assert "medical_paper_task" in TASK_TOTAL._name
        assert "Total number of medical paper tasks" in TASK_TOTAL._documentation

    def test_task_duration_histogram(self):
        assert "medical_paper_task_duration" in TASK_DURATION._name

    def test_step_duration_histogram(self):
        assert "medical_paper_step_duration" in STEP_DURATION._name

    def test_agent_calls_counter(self):
        assert "medical_paper_agent_calls" in AGENT_CALLS_TOTAL._name

    def test_agent_latency_histogram(self):
        assert "medical_paper_agent_latency" in AGENT_LATENCY._name

    def test_compliance_score_gauge(self):
        assert "medical_paper_compliance_score" in COMPLIANCE_SCORE._name

    def test_revision_rounds_histogram(self):
        assert "medical_paper_revision_rounds" in REVISION_ROUNDS._name

    def test_active_tasks_gauge(self):
        assert "medical_paper_active_tasks" in ACTIVE_TASKS._name

    def test_agent_info(self):
        assert "medical_paper_agent" in AGENT_INFO._name


class TestMetricHelpers:
    """Test metric recording helper functions."""

    def test_record_task_created(self):
        record_task_created("rct")
        # Verify counter incremented (no exception)

    def test_record_task_completed(self):
        record_task_completed("rct", 120.5)

    def test_record_task_failed(self):
        record_task_failed("cohort", "timeout")

    def test_record_step(self):
        record_step("literature", "success", 15.0)
        record_step("stats", "error", 5.0)

    def test_record_agent_call(self):
        record_agent_call("literature_agent", "success", 10.0)

    def test_record_agent_tool_call(self):
        record_agent_tool_call("stats_agent", "run_ttest", "success")

    def test_record_compliance_score(self):
        record_compliance_score("rct", "CONSORT", 0.85)

    def test_record_revision_rounds(self):
        record_revision_rounds("rct", 2)

    def test_record_references_count(self):
        record_references_count("meta_analysis", 25)

    def test_record_manuscript_word_count(self):
        record_manuscript_word_count("rct", 4500)

    def test_stream_lifecycle(self):
        stream_started()
        stream_ended()


class TestContextManagers:
    """Test metric context managers."""

    def test_track_step_success(self):
        with track_step("writer"):
            pass  # simulate work

    def test_track_step_error(self):
        with pytest.raises(ValueError):
            with track_step("compliance"):
                raise ValueError("test error")

    def test_track_agent_success(self):
        with track_agent("literature_agent"):
            time.sleep(0.01)

    def test_track_agent_error(self):
        with pytest.raises(RuntimeError):
            with track_agent("stats_agent"):
                raise RuntimeError("agent failed")

    def test_track_streaming(self):
        with track_streaming():
            pass
