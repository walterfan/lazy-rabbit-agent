"""
Tests for the metrics module.
"""

import pytest
from prometheus_client import REGISTRY

from app.services.secretary_agent.metrics import (
    record_chat_request,
    record_chat_error,
    record_first_token_latency,
    record_llm_call,
    record_tool_call,
    record_tool_error,
    record_learning_record,
    record_learning_review,
    record_session_created,
    record_message,
    stream_started,
    stream_ended,
    track_tool,
    CHAT_REQUESTS_TOTAL,
    CHAT_ERRORS_TOTAL,
    CHAT_FIRST_TOKEN_LATENCY,
    LLM_CALLS_TOTAL,
    TOOL_CALLS_TOTAL,
    LEARNING_RECORDS_TOTAL,
    ACTIVE_STREAMS,
)


class TestChatMetrics:
    """Tests for chat-related metrics."""
    
    def test_record_chat_request(self):
        """record_chat_request increments counter and histogram."""
        before = CHAT_REQUESTS_TOTAL.labels(
            method="streaming", status="success"
        )._value.get()
        
        record_chat_request("streaming", "success", 1.5)
        
        after = CHAT_REQUESTS_TOTAL.labels(
            method="streaming", status="success"
        )._value.get()
        
        assert after == before + 1
    
    def test_record_chat_error(self):
        """record_chat_error increments error counter."""
        before = CHAT_ERRORS_TOTAL.labels(error_type="timeout")._value.get()
        
        record_chat_error("timeout")
        
        after = CHAT_ERRORS_TOTAL.labels(error_type="timeout")._value.get()
        
        assert after == before + 1
    
    def test_record_first_token_latency(self):
        """record_first_token_latency records to histogram."""
        # Just verify it doesn't throw
        record_first_token_latency(0.5)
        record_first_token_latency(1.0)
        record_first_token_latency(2.0)


class TestLLMMetrics:
    """Tests for LLM-related metrics."""
    
    def test_record_llm_call(self):
        """record_llm_call increments counter with labels."""
        before = LLM_CALLS_TOTAL.labels(
            model="gpt-4", status="success"
        )._value.get()
        
        record_llm_call(
            model="gpt-4",
            status="success",
            duration=2.0,
            prompt_tokens=100,
            completion_tokens=50,
        )
        
        after = LLM_CALLS_TOTAL.labels(
            model="gpt-4", status="success"
        )._value.get()
        
        assert after == before + 1
    
    def test_record_llm_call_error(self):
        """record_llm_call handles error status."""
        before = LLM_CALLS_TOTAL.labels(
            model="gpt-4", status="error"
        )._value.get()
        
        record_llm_call(
            model="gpt-4",
            status="error",
            duration=0.5,
        )
        
        after = LLM_CALLS_TOTAL.labels(
            model="gpt-4", status="error"
        )._value.get()
        
        assert after == before + 1


class TestToolMetrics:
    """Tests for tool-related metrics."""
    
    def test_record_tool_call(self):
        """record_tool_call increments counter."""
        before = TOOL_CALLS_TOTAL.labels(
            tool_name="calculate", status="success"
        )._value.get()
        
        record_tool_call("calculate", "success", 0.05)
        
        after = TOOL_CALLS_TOTAL.labels(
            tool_name="calculate", status="success"
        )._value.get()
        
        assert after == before + 1
    
    def test_record_tool_error(self):
        """record_tool_error increments error counter."""
        # Just verify it doesn't throw
        record_tool_error("weather", "api_error")
        record_tool_error("weather", "timeout")


class TestBusinessMetrics:
    """Tests for business metrics."""
    
    def test_record_learning_record(self):
        """record_learning_record increments counter by type."""
        before = LEARNING_RECORDS_TOTAL.labels(type="word")._value.get()
        
        record_learning_record("word")
        
        after = LEARNING_RECORDS_TOTAL.labels(type="word")._value.get()
        
        assert after == before + 1
    
    def test_record_learning_review(self):
        """record_learning_review increments review counter."""
        # Just verify it doesn't throw
        record_learning_review("word")
        record_learning_review("sentence")
    
    def test_record_session_created(self):
        """record_session_created increments session counter."""
        # Just verify it doesn't throw
        record_session_created()
    
    def test_record_message(self):
        """record_message increments message counter by role."""
        # Just verify it doesn't throw
        record_message("user")
        record_message("assistant")


class TestResourceMetrics:
    """Tests for resource metrics."""
    
    def test_stream_started_and_ended(self):
        """stream_started and stream_ended update gauge."""
        initial = ACTIVE_STREAMS._value.get()
        
        stream_started()
        assert ACTIVE_STREAMS._value.get() == initial + 1
        
        stream_ended()
        assert ACTIVE_STREAMS._value.get() == initial


class TestTrackToolDecorator:
    """Tests for @track_tool decorator."""
    
    def test_track_tool_sync_function(self):
        """@track_tool tracks sync function calls."""
        @track_tool("test_tool")
        def test_func(x: int) -> int:
            return x * 2
        
        result = test_func(5)
        
        assert result == 10
    
    def test_track_tool_sync_function_error(self):
        """@track_tool tracks sync function errors."""
        @track_tool("error_tool")
        def failing_func():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            failing_func()
    
    @pytest.mark.asyncio
    async def test_track_tool_async_function(self):
        """@track_tool tracks async function calls."""
        @track_tool("async_tool")
        async def async_func(value: str) -> str:
            return f"async: {value}"
        
        result = await async_func("test")
        
        assert result == "async: test"
    
    @pytest.mark.asyncio
    async def test_track_tool_async_function_error(self):
        """@track_tool tracks async function errors."""
        @track_tool("async_error_tool")
        async def failing_async():
            raise RuntimeError("Async error")
        
        with pytest.raises(RuntimeError):
            await failing_async()
