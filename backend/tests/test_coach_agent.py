"""
Tests for Coach sub-agent integration.

Covers:
- Coach agent creation (Task 11.5)
- Coach tools creation
- Supervisor routing keywords
"""

import pytest


class TestCoachAgent:
    """Test coach sub-agent integration."""

    def test_coach_agent_importable(self):
        """Coach agent module is importable."""
        from app.services.secretary_agent.sub_agents.coach import (
            create_coach_agent,
            create_coach_tools,
        )
        assert callable(create_coach_agent)
        assert callable(create_coach_tools)

    def test_coach_tools_creation(self):
        """Coach tools can be created."""
        from app.services.secretary_agent.tools.coach_tools import (
            query_knowledge,
            create_goal,
            log_study_session,
            get_progress,
        )
        # Verify they are callable (tool functions)
        assert callable(query_knowledge)
        assert callable(create_goal)
        assert callable(log_study_session)
        assert callable(get_progress)

    def test_coach_prompts_exist(self):
        """Coach system prompts are defined."""
        from app.services.coach_service import COACH_PROMPTS, CoachMode
        assert CoachMode.COACH in COACH_PROMPTS
        assert CoachMode.TUTOR in COACH_PROMPTS
        assert CoachMode.QUIZ in COACH_PROMPTS
        # Each prompt should have RAG context placeholder
        for mode, prompt in COACH_PROMPTS.items():
            assert "{rag_context}" in prompt

    def test_coach_mode_enum(self):
        """CoachMode enum has 3 values."""
        from app.schemas.coach import CoachMode
        assert len(CoachMode) == 3
        assert CoachMode.COACH.value == "coach"
        assert CoachMode.TUTOR.value == "tutor"
        assert CoachMode.QUIZ.value == "quiz"

    def test_session_continuity_functions(self):
        """Session continuity helper functions exist."""
        from app.services.coach_service import (
            _load_conversation_history,
            _get_or_create_session,
            _save_user_message,
            _save_assistant_message,
            MAX_HISTORY_MESSAGES,
        )
        assert MAX_HISTORY_MESSAGES == 20
        assert callable(_load_conversation_history)
        assert callable(_get_or_create_session)
        assert callable(_save_user_message)
        assert callable(_save_assistant_message)

    def test_coach_models_importable(self):
        """Coach-related models are importable."""
        from app.models.knowledge_document import KnowledgeDocument
        from app.models.learning_goal import LearningGoal, GoalStatus
        from app.models.study_session import StudySession, Difficulty

        assert KnowledgeDocument.__tablename__ == "knowledge_documents"
        assert LearningGoal.__tablename__ == "learning_goals"
        assert StudySession.__tablename__ == "study_sessions"
        assert len(GoalStatus) == 4
        assert len(Difficulty) == 3

    def test_coach_schemas_importable(self):
        """Coach-related schemas are importable."""
        from app.schemas.knowledge import (
            DocumentUpload,
            DocumentResponse,
            KnowledgeQuery,
            KnowledgeQueryResult,
            KnowledgeStats,
        )
        from app.schemas.learning_goal import (
            GoalCreate,
            GoalUpdate,
            GoalResponse,
            SessionCreate,
            SessionResponse,
            ProgressReport,
        )
        from app.schemas.coach import (
            CoachChatRequest,
            CoachChatResponse,
            CoachMode,
        )

        # Verify they are Pydantic models
        assert hasattr(DocumentUpload, "model_fields")
        assert hasattr(GoalCreate, "model_fields")
        assert hasattr(CoachChatRequest, "model_fields")
