"""
Tests for the tracing module.
"""

import pytest
from unittest.mock import MagicMock, patch
import asyncio

from app.services.secretary_agent.tracing import (
    new_trace,
    get_trace_id,
    get_trace_context,
    clear_trace,
    trace_llm_call,
    trace_tool_call,
    truncate,
    safe_serialize,
    LLMCallLog,
    ToolCallLog,
)


class TestTraceContext:
    """Tests for trace context management."""
    
    def test_new_trace_creates_unique_id(self):
        """new_trace creates a unique trace ID."""
        trace_id1 = new_trace()
        clear_trace()
        trace_id2 = new_trace()
        
        assert trace_id1 != trace_id2
        assert len(trace_id1) == 36  # UUID format
    
    def test_new_trace_stores_user_and_session(self):
        """new_trace stores user_id and session_id in context."""
        new_trace(user_id=123, session_id="test-session")
        
        context = get_trace_context()
        assert context["user_id"] == 123
        assert context["session_id"] == "test-session"
        
        clear_trace()
    
    def test_get_trace_id_returns_current(self):
        """get_trace_id returns the current trace ID."""
        trace_id = new_trace()
        
        assert get_trace_id() == trace_id
        
        clear_trace()
    
    def test_get_trace_id_returns_none_when_no_trace(self):
        """get_trace_id returns None when no trace is active."""
        clear_trace()
        
        assert get_trace_id() is None
    
    def test_clear_trace_removes_context(self):
        """clear_trace removes the trace context."""
        new_trace(user_id=1)
        clear_trace()
        
        assert get_trace_id() is None
        context = get_trace_context()
        assert context["user_id"] is None


class TestTruncate:
    """Tests for truncate helper."""
    
    def test_truncate_short_string(self):
        """Short strings are not truncated."""
        result = truncate("hello", max_length=100)
        assert result == "hello"
    
    def test_truncate_long_string(self):
        """Long strings are truncated with indicator."""
        long_string = "a" * 200
        result = truncate(long_string, max_length=50)
        
        assert len(result) <= 50 + 20  # Plus truncation indicator
        assert "..." in result or "truncated" in result.lower()
    
    def test_truncate_empty_string(self):
        """Empty strings return empty."""
        result = truncate("")
        assert result == ""


class TestSafeSerialize:
    """Tests for safe_serialize helper."""
    
    def test_serialize_dict(self):
        """Dicts are serialized to JSON."""
        result = safe_serialize({"key": "value"})
        assert '"key"' in result
        assert '"value"' in result
    
    def test_serialize_list(self):
        """Lists are serialized to JSON."""
        result = safe_serialize([1, 2, 3])
        assert "[1, 2, 3]" in result
    
    def test_serialize_non_serializable(self):
        """Non-serializable objects return string representation."""
        class Custom:
            pass
        
        result = safe_serialize(Custom())
        assert "Custom" in result or "object" in result
    
    def test_serialize_none(self):
        """None is serialized correctly."""
        result = safe_serialize(None)
        assert result == "null" or result == "None"


class TestTraceLLMCallDecorator:
    """Tests for @trace_llm_call decorator."""
    
    @pytest.mark.asyncio
    async def test_trace_llm_call_logs_success(self):
        """Decorator logs successful LLM calls."""
        @trace_llm_call
        async def mock_llm_call(prompt: str):
            return {"content": "response"}
        
        new_trace()
        
        with patch("app.services.secretary_agent.tracing.logger") as mock_logger:
            result = await mock_llm_call("test prompt")
            
            assert result == {"content": "response"}
            # Check that info was logged
            assert mock_logger.info.called
        
        clear_trace()
    
    @pytest.mark.asyncio
    async def test_trace_llm_call_logs_error(self):
        """Decorator logs failed LLM calls."""
        @trace_llm_call
        async def failing_llm_call(prompt: str):
            raise ValueError("LLM error")
        
        new_trace()
        
        with patch("app.services.secretary_agent.tracing.logger") as mock_logger:
            with pytest.raises(ValueError):
                await failing_llm_call("test prompt")
            
            # Check that error was logged
            assert mock_logger.error.called
        
        clear_trace()


class TestTraceToolCallDecorator:
    """Tests for @trace_tool_call decorator."""
    
    def test_trace_tool_call_sync_success(self):
        """Decorator logs successful sync tool calls."""
        @trace_tool_call
        def mock_tool(x: int, y: int) -> int:
            return x + y
        
        new_trace()
        
        with patch("app.services.secretary_agent.tracing.logger") as mock_logger:
            result = mock_tool(2, 3)
            
            assert result == 5
            assert mock_logger.info.called
        
        clear_trace()
    
    def test_trace_tool_call_sync_error(self):
        """Decorator logs failed sync tool calls."""
        @trace_tool_call
        def failing_tool():
            raise RuntimeError("Tool error")
        
        new_trace()
        
        with patch("app.services.secretary_agent.tracing.logger") as mock_logger:
            with pytest.raises(RuntimeError):
                failing_tool()
            
            assert mock_logger.error.called
        
        clear_trace()
    
    @pytest.mark.asyncio
    async def test_trace_tool_call_async_success(self):
        """Decorator logs successful async tool calls."""
        @trace_tool_call
        async def async_tool(value: str) -> str:
            return f"processed: {value}"
        
        new_trace()
        
        with patch("app.services.secretary_agent.tracing.logger") as mock_logger:
            result = await async_tool("test")
            
            assert result == "processed: test"
            assert mock_logger.info.called
        
        clear_trace()


class TestLLMCallLog:
    """Tests for LLMCallLog model."""
    
    def test_llm_call_log_creation(self):
        """LLMCallLog can be created with required fields."""
        log = LLMCallLog(
            trace_id="trace-123",
            call_id="call-456",
            model="gpt-4",
            status="success",
            duration_ms=1500,
        )
        
        assert log.trace_id == "trace-123"
        assert log.model == "gpt-4"
        assert log.status == "success"
    
    def test_llm_call_log_with_tokens(self):
        """LLMCallLog can include token counts."""
        log = LLMCallLog(
            trace_id="trace-123",
            call_id="call-456",
            model="gpt-4",
            status="success",
            duration_ms=1500,
            prompt_tokens=100,
            completion_tokens=50,
        )
        
        assert log.prompt_tokens == 100
        assert log.completion_tokens == 50


class TestToolCallLog:
    """Tests for ToolCallLog model."""
    
    def test_tool_call_log_creation(self):
        """ToolCallLog can be created with required fields."""
        log = ToolCallLog(
            trace_id="trace-123",
            call_id="call-456",
            tool_name="calculate",
            status="success",
            duration_ms=50,
        )
        
        assert log.tool_name == "calculate"
        assert log.status == "success"
    
    def test_tool_call_log_with_args_and_result(self):
        """ToolCallLog can include args and result."""
        log = ToolCallLog(
            trace_id="trace-123",
            call_id="call-456",
            tool_name="calculate",
            status="success",
            duration_ms=50,
            args='{"expression": "2+2"}',
            result='{"result": 4}',
        )
        
        assert "2+2" in log.args
        assert "4" in log.result
