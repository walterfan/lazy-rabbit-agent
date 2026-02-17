"""
Tests for the multi-agent architecture refactoring.

Verifies:
1. A2A message contract
2. Sub-agent tool creation (ISP: each gets only its own tools)
3. Sub-agent factory functions
4. Supervisor workflow assembly
5. Backward-compatible API (SecretaryAgent.chat / chat_stream)
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock, patch
from uuid import uuid4


# ============================================================================
# A2A Message Contract Tests
# ============================================================================


class TestA2AContract:
    """Test A2A message models and factories."""

    def test_create_a2a_request(self):
        """A2A request should have correct fields."""
        from app.services.secretary_agent.a2a import (
            create_a2a_request,
            A2AProtocol,
            A2AStatus,
        )

        msg = create_a2a_request(
            sender="supervisor",
            receiver="learning_agent",
            intent="learn_word",
            input_data={"word": "serendipity"},
            correlation_id="trace_123",
        )

        assert msg.protocol == A2AProtocol.V1
        assert msg.sender == "supervisor"
        assert msg.receiver == "learning_agent"
        assert msg.intent == "learn_word"
        assert msg.input == {"word": "serendipity"}
        assert msg.correlation_id == "trace_123"
        assert msg.status == A2AStatus.OK
        assert msg.id.startswith("msg_")

    def test_create_a2a_response(self):
        """A2A response should reference the original request."""
        from app.services.secretary_agent.a2a import (
            create_a2a_request,
            create_a2a_response,
            A2AStatus,
            A2AMetrics,
        )

        req = create_a2a_request(
            sender="supervisor",
            receiver="utility_agent",
            intent="get_weather",
            correlation_id="trace_456",
        )

        resp = create_a2a_response(
            request=req,
            status=A2AStatus.OK,
            output={"temperature": "25°C"},
            metrics=A2AMetrics(latency_ms=150.5, tool_calls=1),
        )

        assert resp.sender == "utility_agent"
        assert resp.receiver == "supervisor"
        assert resp.intent == "get_weather_response"
        assert resp.correlation_id == "trace_456"
        assert resp.output == {"temperature": "25°C"}
        assert resp.metrics.latency_ms == 150.5
        assert resp.metrics.tool_calls == 1

    def test_a2a_error_response(self):
        """A2A error response should include error details."""
        from app.services.secretary_agent.a2a import (
            create_a2a_request,
            create_a2a_response,
            A2AStatus,
            A2AError,
            A2AErrorType,
        )

        req = create_a2a_request(
            sender="supervisor",
            receiver="learning_agent",
            intent="learn_article",
        )

        resp = create_a2a_response(
            request=req,
            status=A2AStatus.ERROR,
            error=A2AError(
                type=A2AErrorType.TOOL_ERROR,
                message="Failed to fetch URL",
                retryable=True,
            ),
        )

        assert resp.status == A2AStatus.ERROR
        assert resp.error.type == A2AErrorType.TOOL_ERROR
        assert resp.error.retryable is True


# ============================================================================
# Sub-Agent Tool Creation Tests (ISP Verification)
# ============================================================================


class TestISPToolSegregation:
    """Verify ISP: each sub-agent gets only its own tools."""

    def test_learning_tools_only_learning(self):
        """Learning agent should only have learning-related tools."""
        from app.services.secretary_agent.sub_agents.learning import (
            create_learning_tools,
        )

        tools = create_learning_tools()
        tool_names = {t.name for t in tools}

        # Should have learning tools
        assert "save_learning" in tool_names
        assert "list_learning" in tool_names
        assert "learn_article" in tool_names

        # Should NOT have productivity or utility tools
        assert "save_note" not in tool_names
        assert "create_task" not in tool_names
        assert "create_reminder" not in tool_names
        assert "calculate" not in tool_names
        assert "get_weather" not in tool_names
        assert "get_datetime" not in tool_names

    def test_productivity_tools_only_productivity(self):
        """Productivity agent should only have notes/tasks/reminders."""
        from app.services.secretary_agent.sub_agents.productivity import (
            create_productivity_tools,
        )

        tools = create_productivity_tools()
        tool_names = {t.name for t in tools}

        # Should have productivity tools
        assert "save_note" in tool_names
        assert "search_notes" in tool_names
        assert "list_notes" in tool_names
        assert "create_task" in tool_names
        assert "list_tasks" in tool_names
        assert "complete_task" in tool_names
        assert "create_reminder" in tool_names
        assert "list_reminders" in tool_names

        # Should NOT have learning or utility tools
        assert "save_learning" not in tool_names
        assert "learn_article" not in tool_names
        assert "calculate" not in tool_names
        assert "get_weather" not in tool_names

    def test_utility_tools_only_utility(self):
        """Utility agent should only have calculator/weather/datetime."""
        from app.services.secretary_agent.sub_agents.utility import (
            create_utility_tools,
        )

        tools = create_utility_tools()
        tool_names = {t.name for t in tools}

        # Should have utility tools
        assert "calculate" in tool_names
        assert "get_datetime" in tool_names
        assert "get_weather" in tool_names

        # Should NOT have learning or productivity tools
        assert "save_learning" not in tool_names
        assert "learn_article" not in tool_names
        assert "save_note" not in tool_names
        assert "create_task" not in tool_names

    def test_no_tool_overlap(self):
        """No tool should appear in more than one sub-agent."""
        from app.services.secretary_agent.sub_agents.learning import (
            create_learning_tools,
        )
        from app.services.secretary_agent.sub_agents.productivity import (
            create_productivity_tools,
        )
        from app.services.secretary_agent.sub_agents.utility import (
            create_utility_tools,
        )

        learning_names = {t.name for t in create_learning_tools()}
        productivity_names = {t.name for t in create_productivity_tools()}
        utility_names = {t.name for t in create_utility_tools()}

        # No overlap between any pair
        assert learning_names & productivity_names == set()
        assert learning_names & utility_names == set()
        assert productivity_names & utility_names == set()

    def test_all_tools_covered(self):
        """All original 14 tools should be covered by sub-agents."""
        from app.services.secretary_agent.sub_agents.learning import (
            create_learning_tools,
        )
        from app.services.secretary_agent.sub_agents.productivity import (
            create_productivity_tools,
        )
        from app.services.secretary_agent.sub_agents.utility import (
            create_utility_tools,
        )

        all_names = set()
        all_names.update(t.name for t in create_learning_tools())
        all_names.update(t.name for t in create_productivity_tools())
        all_names.update(t.name for t in create_utility_tools())

        # The 14 original tools (from the original agent._create_tools)
        expected = {
            "calculate",
            "get_datetime",
            "get_weather",
            "save_learning",
            "list_learning",
            "save_note",
            "search_notes",
            "list_notes",
            "create_task",
            "list_tasks",
            "complete_task",
            "create_reminder",
            "list_reminders",
            "learn_article",
        }

        assert all_names == expected


# ============================================================================
# Sub-Agent Prompt Tests
# ============================================================================


class TestSubAgentPrompts:
    """Test sub-agent prompt loading from YAML."""

    def test_supervisor_prompt_loads(self):
        """Supervisor prompt should load from sub_agents.yaml."""
        from app.services.secretary_agent.prompts import get_prompt

        prompt = get_prompt(
            "sub_agents.yaml",
            "supervisor",
            current_date="2026-02-07",
            timezone="Asia/Shanghai",
        )

        assert "Personal Secretary Supervisor" in prompt
        assert "learning_agent" in prompt
        assert "productivity_agent" in prompt
        assert "utility_agent" in prompt

    def test_learning_agent_prompt_loads(self):
        """Learning agent prompt should load from sub_agents.yaml."""
        from app.services.secretary_agent.prompts import get_prompt

        prompt = get_prompt(
            "sub_agents.yaml",
            "learning_agent",
            current_date="2026-02-07",
        )

        assert "Learning Agent" in prompt
        assert "中文解释" in prompt

    def test_productivity_agent_prompt_loads(self):
        """Productivity agent prompt should load from sub_agents.yaml."""
        from app.services.secretary_agent.prompts import get_prompt

        prompt = get_prompt(
            "sub_agents.yaml",
            "productivity_agent",
            current_date="2026-02-07",
        )

        assert "Productivity Agent" in prompt
        assert "Notes" in prompt
        assert "Tasks" in prompt
        assert "Reminders" in prompt

    def test_utility_agent_prompt_loads(self):
        """Utility agent prompt should load from sub_agents.yaml."""
        from app.services.secretary_agent.prompts import get_prompt

        prompt = get_prompt(
            "sub_agents.yaml",
            "utility_agent",
            current_date="2026-02-07",
        )

        assert "Utility Agent" in prompt
        assert "Weather" in prompt
        assert "Calculator" in prompt


# ============================================================================
# Supervisor Workflow Assembly Tests
# ============================================================================


class TestWorkflowAssembly:
    """Test the LangGraph workflow is correctly assembled."""

    @patch("app.services.secretary_agent.agent.settings")
    def test_secretary_agent_creates_workflow(self, mock_settings):
        """SecretaryAgent should build a LangGraph workflow."""
        mock_settings.LLM_MODEL = "test-model"
        mock_settings.LLM_API_KEY = "test-key"
        mock_settings.LLM_BASE_URL = "http://localhost:1234/v1"
        mock_settings.LLM_VERIFY_SSL = True
        mock_settings.LLM_TIMEOUT = 60.0
        mock_settings.PLANTUML_SERVER_URL = ""
        mock_settings.PLANTUML_JAR_PATH = ""
        mock_settings.PLANTUML_OUTPUT_DIR = "static/mindmaps"

        from app.services.secretary_agent.agent import SecretaryAgent

        agent = SecretaryAgent(user_id=1, session_id=uuid4())

        # Should have a compiled workflow
        assert agent.workflow is not None

        # Should have all tools collected
        tool_names = {t.name for t in agent.tools}
        assert "calculate" in tool_names
        assert "save_learning" in tool_names
        assert "save_note" in tool_names

    @patch("app.services.secretary_agent.agent.settings")
    def test_workflow_has_correct_nodes(self, mock_settings):
        """Workflow should have supervisor + 3 sub-agent nodes."""
        mock_settings.LLM_MODEL = "test-model"
        mock_settings.LLM_API_KEY = "test-key"
        mock_settings.LLM_BASE_URL = "http://localhost:1234/v1"
        mock_settings.LLM_VERIFY_SSL = True
        mock_settings.LLM_TIMEOUT = 60.0
        mock_settings.PLANTUML_SERVER_URL = ""
        mock_settings.PLANTUML_JAR_PATH = ""
        mock_settings.PLANTUML_OUTPUT_DIR = "static/mindmaps"

        from app.services.secretary_agent.agent import (
            SecretaryAgent,
            SUPERVISOR,
            LEARNING_AGENT,
            PRODUCTIVITY_AGENT,
            UTILITY_AGENT,
        )

        agent = SecretaryAgent(user_id=1, session_id=uuid4())

        # The graph should have the expected nodes
        graph = agent.workflow.get_graph()
        # graph.nodes may return node IDs as strings or node objects
        if hasattr(graph, "nodes"):
            nodes = graph.nodes
            # Handle both dict-like and list-like node collections
            if isinstance(nodes, dict):
                node_ids = set(nodes.keys())
            else:
                node_ids = {
                    n.id if hasattr(n, "id") else str(n) for n in nodes
                }
        else:
            node_ids = set()

        assert SUPERVISOR in node_ids
        assert LEARNING_AGENT in node_ids
        assert PRODUCTIVITY_AGENT in node_ids
        assert UTILITY_AGENT in node_ids


# ============================================================================
# Backward Compatibility Tests
# ============================================================================


class TestBackwardCompatibility:
    """Verify the refactored agent has the same API surface."""

    @patch("app.services.secretary_agent.agent.settings")
    def test_agent_has_chat_method(self, mock_settings):
        """SecretaryAgent should still have async chat() method."""
        mock_settings.LLM_MODEL = "test-model"
        mock_settings.LLM_API_KEY = "test-key"
        mock_settings.LLM_BASE_URL = "http://localhost:1234/v1"
        mock_settings.LLM_VERIFY_SSL = True
        mock_settings.LLM_TIMEOUT = 60.0
        mock_settings.PLANTUML_SERVER_URL = ""
        mock_settings.PLANTUML_JAR_PATH = ""
        mock_settings.PLANTUML_OUTPUT_DIR = "static/mindmaps"

        from app.services.secretary_agent.agent import SecretaryAgent

        agent = SecretaryAgent(user_id=1, session_id=uuid4())
        assert hasattr(agent, "chat")
        assert callable(agent.chat)

    @patch("app.services.secretary_agent.agent.settings")
    def test_agent_has_chat_stream_method(self, mock_settings):
        """SecretaryAgent should still have async chat_stream() method."""
        mock_settings.LLM_MODEL = "test-model"
        mock_settings.LLM_API_KEY = "test-key"
        mock_settings.LLM_BASE_URL = "http://localhost:1234/v1"
        mock_settings.LLM_VERIFY_SSL = True
        mock_settings.LLM_TIMEOUT = 60.0
        mock_settings.PLANTUML_SERVER_URL = ""
        mock_settings.PLANTUML_JAR_PATH = ""
        mock_settings.PLANTUML_OUTPUT_DIR = "static/mindmaps"

        from app.services.secretary_agent.agent import SecretaryAgent

        agent = SecretaryAgent(user_id=1, session_id=uuid4())
        assert hasattr(agent, "chat_stream")
        assert callable(agent.chat_stream)

    @patch("app.services.secretary_agent.agent.settings")
    def test_agent_has_tools_property(self, mock_settings):
        """SecretaryAgent should expose all tools for /tools endpoint."""
        mock_settings.LLM_MODEL = "test-model"
        mock_settings.LLM_API_KEY = "test-key"
        mock_settings.LLM_BASE_URL = "http://localhost:1234/v1"
        mock_settings.LLM_VERIFY_SSL = True
        mock_settings.LLM_TIMEOUT = 60.0
        mock_settings.PLANTUML_SERVER_URL = ""
        mock_settings.PLANTUML_JAR_PATH = ""
        mock_settings.PLANTUML_OUTPUT_DIR = "static/mindmaps"

        from app.services.secretary_agent.agent import SecretaryAgent

        agent = SecretaryAgent(user_id=1, session_id=uuid4())
        assert hasattr(agent, "tools")
        assert len(agent.tools) == 14  # same as original

    @patch("app.services.secretary_agent.agent.settings")
    def test_agent_constructor_signature(self, mock_settings):
        """SecretaryAgent should accept same constructor args."""
        mock_settings.LLM_MODEL = "test-model"
        mock_settings.LLM_API_KEY = "test-key"
        mock_settings.LLM_BASE_URL = "http://localhost:1234/v1"
        mock_settings.LLM_VERIFY_SSL = True
        mock_settings.LLM_TIMEOUT = 60.0
        mock_settings.PLANTUML_SERVER_URL = ""
        mock_settings.PLANTUML_JAR_PATH = ""
        mock_settings.PLANTUML_OUTPUT_DIR = "static/mindmaps"

        from app.services.secretary_agent.agent import SecretaryAgent

        session_id = uuid4()

        # All three ways to construct should work
        agent1 = SecretaryAgent()
        agent2 = SecretaryAgent(user_id=1)
        agent3 = SecretaryAgent(user_id=1, session_id=session_id, db=None)

        assert agent1.user_id is None
        assert agent2.user_id == 1
        assert agent3.session_id == session_id


# ============================================================================
# Message Building Tests
# ============================================================================


class TestMessageBuilding:
    """Test message conversion for LangGraph."""

    @patch("app.services.secretary_agent.agent.settings")
    def test_build_messages_with_history(self, mock_settings):
        """Should build proper LangChain messages from history."""
        mock_settings.LLM_MODEL = "test-model"
        mock_settings.LLM_API_KEY = "test-key"
        mock_settings.LLM_BASE_URL = "http://localhost:1234/v1"
        mock_settings.LLM_VERIFY_SSL = True
        mock_settings.LLM_TIMEOUT = 60.0
        mock_settings.PLANTUML_SERVER_URL = ""
        mock_settings.PLANTUML_JAR_PATH = ""
        mock_settings.PLANTUML_OUTPUT_DIR = "static/mindmaps"

        from langchain_core.messages import AIMessage, HumanMessage
        from app.services.secretary_agent.agent import SecretaryAgent

        agent = SecretaryAgent()
        history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]

        messages = agent._build_messages(history, "What's the weather?")

        assert len(messages) == 3
        assert isinstance(messages[0], HumanMessage)
        assert messages[0].content == "Hello"
        assert isinstance(messages[1], AIMessage)
        assert messages[1].content == "Hi there!"
        assert isinstance(messages[2], HumanMessage)
        assert messages[2].content == "What's the weather?"

    @patch("app.services.secretary_agent.agent.settings")
    def test_build_messages_no_history(self, mock_settings):
        """Should work with no history."""
        mock_settings.LLM_MODEL = "test-model"
        mock_settings.LLM_API_KEY = "test-key"
        mock_settings.LLM_BASE_URL = "http://localhost:1234/v1"
        mock_settings.LLM_VERIFY_SSL = True
        mock_settings.LLM_TIMEOUT = 60.0
        mock_settings.PLANTUML_SERVER_URL = ""
        mock_settings.PLANTUML_JAR_PATH = ""
        mock_settings.PLANTUML_OUTPUT_DIR = "static/mindmaps"

        from langchain_core.messages import HumanMessage
        from app.services.secretary_agent.agent import SecretaryAgent

        agent = SecretaryAgent()
        messages = agent._build_messages(None, "Hello!")

        assert len(messages) == 1
        assert isinstance(messages[0], HumanMessage)
        assert messages[0].content == "Hello!"

    @patch("app.services.secretary_agent.agent.settings")
    def test_extract_final_response(self, mock_settings):
        """Should extract last AI message content."""
        mock_settings.LLM_MODEL = "test-model"
        mock_settings.LLM_API_KEY = "test-key"
        mock_settings.LLM_BASE_URL = "http://localhost:1234/v1"
        mock_settings.LLM_VERIFY_SSL = True
        mock_settings.LLM_TIMEOUT = 60.0
        mock_settings.PLANTUML_SERVER_URL = ""
        mock_settings.PLANTUML_JAR_PATH = ""
        mock_settings.PLANTUML_OUTPUT_DIR = "static/mindmaps"

        from langchain_core.messages import AIMessage, HumanMessage
        from app.services.secretary_agent.agent import SecretaryAgent

        agent = SecretaryAgent()
        result = {
            "messages": [
                HumanMessage(content="Hello"),
                AIMessage(content="Routing to utility..."),
                AIMessage(content="The weather is sunny, 25°C."),
            ]
        }

        response = agent._extract_final_response(result)
        assert response == "The weather is sunny, 25°C."
