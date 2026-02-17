"""
Tests for the Medical Paper A2A communication contract.

TDD - Red Phase: Verify message serialization, error classification, and retry logic.
"""

from app.services.medical_paper_agent.a2a import (
    MedicalA2AError,
    MedicalA2AErrorCode,
    MedicalA2AMessage,
    MedicalA2AMetrics,
    MedicalA2AStatus,
    classify_error,
    create_medical_request,
    create_medical_response,
    get_backoff_seconds,
    should_retry,
)


class TestMedicalA2AMessage:
    """Test A2A message creation and serialization."""

    def test_create_request(self):
        msg = create_medical_request(
            sender="supervisor",
            receiver="literature_agent",
            intent="collect_references",
            input_data={"query": "Drug X RCT"},
            correlation_id="trace_123",
        )
        assert msg.sender == "supervisor"
        assert msg.receiver == "literature_agent"
        assert msg.intent == "collect_references"
        assert msg.input == {"query": "Drug X RCT"}
        assert msg.correlation_id == "trace_123"
        assert msg.status == MedicalA2AStatus.PENDING
        assert msg.protocol == "a2a.medical.v1"
        assert msg.id.startswith("med_")

    def test_create_response_from_request(self):
        req = create_medical_request(
            sender="supervisor",
            receiver="stats_agent",
            intent="run_analysis",
            correlation_id="trace_456",
        )
        resp = create_medical_response(
            request=req,
            status=MedicalA2AStatus.OK,
            output={"p_value": 0.03},
            metrics=MedicalA2AMetrics(latency_ms=1200, tokens_in=500, tokens_out=300),
        )
        assert resp.sender == "stats_agent"
        assert resp.receiver == "supervisor"
        assert resp.intent == "run_analysis_response"
        assert resp.correlation_id == "trace_456"
        assert resp.status == MedicalA2AStatus.OK
        assert resp.output["p_value"] == 0.03
        assert resp.metrics.latency_ms == 1200

    def test_message_serialization(self):
        msg = create_medical_request(
            sender="supervisor",
            receiver="writer_agent",
            intent="write_introduction",
        )
        data = msg.model_dump()
        assert isinstance(data, dict)
        assert data["sender"] == "supervisor"
        assert data["protocol"] == "a2a.medical.v1"

    def test_message_json_roundtrip(self):
        msg = create_medical_request(
            sender="supervisor",
            receiver="compliance_agent",
            intent="check_consort",
            input_data={"manuscript": "..."},
        )
        json_str = msg.model_dump_json()
        restored = MedicalA2AMessage.model_validate_json(json_str)
        assert restored.sender == msg.sender
        assert restored.intent == msg.intent

    def test_error_response(self):
        req = create_medical_request(
            sender="supervisor",
            receiver="literature_agent",
            intent="collect_references",
        )
        error = MedicalA2AError(
            code=MedicalA2AErrorCode.TOOL_ERROR,
            message="PubMed API returned 503",
            recoverable=True,
        )
        resp = create_medical_response(
            request=req,
            status=MedicalA2AStatus.ERROR,
            error=error,
        )
        assert resp.status == MedicalA2AStatus.ERROR
        assert resp.error.code == MedicalA2AErrorCode.TOOL_ERROR
        assert resp.error.recoverable is True


class TestErrorClassification:
    """Test error classification logic."""

    def test_timeout_error(self):
        err = classify_error(TimeoutError("Connection timed out"))
        assert err.code == MedicalA2AErrorCode.TIMEOUT
        assert err.recoverable is True

    def test_rate_limit_error(self):
        err = classify_error(Exception("Rate limit exceeded (429)"))
        assert err.code == MedicalA2AErrorCode.RATE_LIMIT
        assert err.recoverable is True
        assert err.retry_after == 10

    def test_validation_error(self):
        err = classify_error(ValueError("Invalid paper type"))
        assert err.code == MedicalA2AErrorCode.VALIDATION_ERROR
        assert err.recoverable is False

    def test_type_error_classified_as_validation(self):
        err = classify_error(TypeError("Expected str, got int"))
        assert err.code == MedicalA2AErrorCode.VALIDATION_ERROR
        assert err.recoverable is False

    def test_generic_error_classified_as_tool_error(self):
        err = classify_error(RuntimeError("Something went wrong"))
        assert err.code == MedicalA2AErrorCode.TOOL_ERROR
        assert err.recoverable is True


class TestRetryLogic:
    """Test retry strategy based on error classification."""

    def test_validation_error_no_retry(self):
        err = MedicalA2AError(
            code=MedicalA2AErrorCode.VALIDATION_ERROR,
            message="bad input",
            recoverable=False,
        )
        assert should_retry(err, attempt=0) is False

    def test_tool_error_retries_up_to_3(self):
        err = MedicalA2AError(
            code=MedicalA2AErrorCode.TOOL_ERROR,
            message="tool failed",
            recoverable=True,
        )
        assert should_retry(err, attempt=0) is True
        assert should_retry(err, attempt=1) is True
        assert should_retry(err, attempt=2) is True
        assert should_retry(err, attempt=3) is False

    def test_timeout_retries_up_to_2(self):
        err = MedicalA2AError(
            code=MedicalA2AErrorCode.TIMEOUT,
            message="timed out",
            recoverable=True,
        )
        assert should_retry(err, attempt=0) is True
        assert should_retry(err, attempt=1) is True
        assert should_retry(err, attempt=2) is False

    def test_backoff_increases_exponentially(self):
        err = MedicalA2AError(
            code=MedicalA2AErrorCode.TOOL_ERROR,
            message="failed",
            recoverable=True,
        )
        b0 = get_backoff_seconds(err, attempt=0)
        b1 = get_backoff_seconds(err, attempt=1)
        b2 = get_backoff_seconds(err, attempt=2)
        # backoff base is 2.0 for TOOL_ERROR
        assert b0 == 2.0   # 2 * 2^0
        assert b1 == 4.0   # 2 * 2^1
        assert b2 == 8.0   # 2 * 2^2

    def test_rate_limit_backoff(self):
        err = MedicalA2AError(
            code=MedicalA2AErrorCode.RATE_LIMIT,
            message="429",
            recoverable=True,
        )
        b0 = get_backoff_seconds(err, attempt=0)
        assert b0 == 10.0  # base 10 * 2^0
