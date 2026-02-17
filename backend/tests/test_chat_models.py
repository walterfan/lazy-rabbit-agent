"""Unit tests for chat models (ChatSession, ChatMessage).

Phase 1.3: Model Tests (TDD)
"""

import json
from datetime import datetime
from uuid import UUID, uuid4

import pytest
from sqlalchemy.orm import Session

from app.models.chat_message import ChatMessage, MessageRole
from app.models.chat_session import ChatSession
from app.models.user import User


@pytest.fixture
def test_user(db: Session) -> User:
    """Create a test user for chat tests."""
    user = User(
        email="chatuser@example.com",
        hashed_password="hashed_password_123",
        full_name="Chat Test User",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


class TestChatSession:
    """Tests for ChatSession model."""

    def test_create_session(self, db: Session, test_user: User) -> None:
        """Test creating a chat session and saving to database."""
        # Given: A user
        user_id = test_user.id

        # When: Creating a chat session
        session = ChatSession(
            user_id=user_id,
            title="Test Conversation",
        )
        db.add(session)
        db.commit()
        db.refresh(session)

        # Then: Session is saved with correct data
        assert session.id is not None
        assert isinstance(session.id, UUID)
        assert session.user_id == user_id
        assert session.title == "Test Conversation"
        assert session.is_active is True
        assert session.created_at is not None
        assert session.updated_at is not None

    def test_read_session_back(self, db: Session, test_user: User) -> None:
        """Test reading a session back from database."""
        # Given: A saved session
        session = ChatSession(
            user_id=test_user.id,
            title="Read Back Test",
        )
        db.add(session)
        db.commit()
        session_id = session.id

        # When: Reading it back
        loaded_session = db.query(ChatSession).filter(
            ChatSession.id == session_id
        ).first()

        # Then: Data is preserved
        assert loaded_session is not None
        assert loaded_session.id == session_id
        assert loaded_session.title == "Read Back Test"
        assert loaded_session.user_id == test_user.id

    def test_session_without_title(self, db: Session, test_user: User) -> None:
        """Test creating a session without title (auto-generated later)."""
        # When: Creating session without title
        session = ChatSession(user_id=test_user.id)
        db.add(session)
        db.commit()
        db.refresh(session)

        # Then: Title is None but session is created
        assert session.id is not None
        assert session.title is None

    def test_soft_delete_session(self, db: Session, test_user: User) -> None:
        """Test soft deleting a session by setting is_active=False."""
        # Given: An active session
        session = ChatSession(
            user_id=test_user.id,
            title="To Be Deleted",
        )
        db.add(session)
        db.commit()
        assert session.is_active is True

        # When: Soft deleting
        session.is_active = False
        db.commit()
        db.refresh(session)

        # Then: Session still exists but is inactive
        loaded = db.query(ChatSession).filter(
            ChatSession.id == session.id
        ).first()
        assert loaded is not None
        assert loaded.is_active is False


class TestChatMessage:
    """Tests for ChatMessage model."""

    @pytest.fixture
    def chat_session(self, db: Session, test_user: User) -> ChatSession:
        """Create a chat session for message tests."""
        session = ChatSession(
            user_id=test_user.id,
            title="Message Test Session",
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    def test_create_user_message(
        self, db: Session, chat_session: ChatSession
    ) -> None:
        """Test creating a user message."""
        # When: Creating a user message
        message = ChatMessage(
            session_id=chat_session.id,
            role=MessageRole.USER,
            content="Hello, can you help me learn English?",
        )
        db.add(message)
        db.commit()
        db.refresh(message)

        # Then: Message is saved correctly
        assert message.id is not None
        assert isinstance(message.id, UUID)
        assert message.session_id == chat_session.id
        assert message.role == MessageRole.USER
        assert message.content == "Hello, can you help me learn English?"
        assert message.tool_calls is None
        assert message.created_at is not None

    def test_create_assistant_message(
        self, db: Session, chat_session: ChatSession
    ) -> None:
        """Test creating an assistant response message."""
        # When: Creating an assistant message
        message = ChatMessage(
            session_id=chat_session.id,
            role=MessageRole.ASSISTANT,
            content="Of course! I'd be happy to help you learn English.",
        )
        db.add(message)
        db.commit()
        db.refresh(message)

        # Then: Message is saved correctly
        assert message.role == MessageRole.ASSISTANT
        assert "happy to help" in message.content

    def test_create_message_with_tool_calls(
        self, db: Session, chat_session: ChatSession
    ) -> None:
        """Test creating a message with tool_calls JSON field."""
        # Given: Tool calls data
        tool_calls = [
            {
                "id": "call_abc123",
                "name": "learn_word",
                "arguments": {"word": "serendipity"},
            },
            {
                "id": "call_def456",
                "name": "get_weather",
                "arguments": {"city": "Beijing"},
            },
        ]

        # When: Creating message with tool calls
        message = ChatMessage(
            session_id=chat_session.id,
            role=MessageRole.ASSISTANT,
            content="Let me look that up for you.",
            tool_calls=tool_calls,
        )
        db.add(message)
        db.commit()
        db.refresh(message)

        # Then: Tool calls are serialized and deserialized correctly
        assert message.tool_calls is not None
        assert len(message.tool_calls) == 2
        assert message.tool_calls[0]["name"] == "learn_word"
        assert message.tool_calls[0]["arguments"]["word"] == "serendipity"
        assert message.tool_calls[1]["name"] == "get_weather"

    def test_create_tool_result_message(
        self, db: Session, chat_session: ChatSession
    ) -> None:
        """Test creating a tool result message."""
        # Given: A tool result
        tool_result = {
            "word": "serendipity",
            "pronunciation": "/ˌser.ənˈdɪp.ə.ti/",
            "chinese_explanation": "意外发现珍奇事物的运气",
            "examples": [
                "Finding that book was pure serendipity.",
                "The discovery was a happy serendipity.",
            ],
        }

        # When: Creating tool result message
        message = ChatMessage(
            session_id=chat_session.id,
            role=MessageRole.TOOL,
            content=json.dumps(tool_result),
            tool_name="learn_word",
            tool_call_id="call_abc123",
        )
        db.add(message)
        db.commit()
        db.refresh(message)

        # Then: Tool result is saved correctly
        assert message.role == MessageRole.TOOL
        assert message.tool_name == "learn_word"
        assert message.tool_call_id == "call_abc123"
        # Content is JSON string
        parsed = json.loads(message.content)
        assert parsed["word"] == "serendipity"
        assert "pronunciation" in parsed

    def test_session_message_relationship(
        self, db: Session, chat_session: ChatSession
    ) -> None:
        """Test relationship between session and messages."""
        # Given: Multiple messages in a session
        msg1 = ChatMessage(
            session_id=chat_session.id,
            role=MessageRole.USER,
            content="Hello!",
        )
        msg2 = ChatMessage(
            session_id=chat_session.id,
            role=MessageRole.ASSISTANT,
            content="Hi there!",
        )
        db.add_all([msg1, msg2])
        db.commit()

        # When: Loading session with messages
        db.refresh(chat_session)

        # Then: Messages are accessible via relationship
        assert len(chat_session.messages) == 2
        assert chat_session.messages[0].content == "Hello!"
        assert chat_session.messages[1].content == "Hi there!"

    def test_message_cascade_delete(
        self, db: Session, test_user: User
    ) -> None:
        """Test that messages are deleted when session is deleted."""
        # Given: A session with messages
        session = ChatSession(
            user_id=test_user.id,
            title="Cascade Test",
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        
        msg = ChatMessage(
            session_id=session.id,
            role=MessageRole.USER,
            content="Test message",
        )
        db.add(msg)
        db.commit()
        message_id = msg.id
        session_id = session.id

        # When: Deleting the session
        db.delete(session)
        db.commit()

        # Then: Message is also deleted
        deleted_msg = db.query(ChatMessage).filter(
            ChatMessage.id == message_id
        ).first()
        assert deleted_msg is None


class TestMessageRoles:
    """Tests for MessageRole enum."""

    def test_all_roles_exist(self) -> None:
        """Test that all expected roles are defined."""
        assert MessageRole.USER.value == "user"
        assert MessageRole.ASSISTANT.value == "assistant"
        assert MessageRole.TOOL.value == "tool"
        assert MessageRole.SYSTEM.value == "system"

    def test_role_string_comparison(self) -> None:
        """Test that roles can be compared as strings."""
        assert MessageRole.USER == "user"
        assert MessageRole.ASSISTANT == "assistant"
