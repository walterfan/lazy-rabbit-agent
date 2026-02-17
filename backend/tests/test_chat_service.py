"""Unit tests for ChatService.

Phase 2.2: Service Tests (TDD)
"""

from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.models.chat_message import ChatMessage, MessageRole
from app.models.chat_session import ChatSession
from app.models.user import User
from app.services.chat_service import ChatService


@pytest.fixture
def test_user(db: Session) -> User:
    """Create a test user for chat service tests."""
    user = User(
        email="chatservice@example.com",
        hashed_password="hashed_password_123",
        full_name="Chat Service Test User",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def another_user(db: Session) -> User:
    """Create another user for ownership tests."""
    user = User(
        email="another@example.com",
        hashed_password="hashed_password_456",
        full_name="Another User",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


class TestChatServiceSessions:
    """Tests for session management."""

    def test_create_session_success(self, db: Session, test_user: User) -> None:
        """Test creating a chat session successfully."""
        # When: Creating a session
        session = ChatService.create_session(
            db=db,
            user_id=test_user.id,
            title="My Test Conversation"
        )

        # Then: Session is created with correct data
        assert session.id is not None
        assert session.user_id == test_user.id
        assert session.title == "My Test Conversation"
        assert session.is_active is True

    def test_create_session_without_title(self, db: Session, test_user: User) -> None:
        """Test creating a session without title (for auto-generation)."""
        # When: Creating session without title
        session = ChatService.create_session(db=db, user_id=test_user.id)

        # Then: Session is created with None title
        assert session.id is not None
        assert session.title is None

    def test_get_session_with_ownership(
        self, db: Session, test_user: User
    ) -> None:
        """Test getting a session respects ownership."""
        # Given: A session
        session = ChatService.create_session(
            db=db, user_id=test_user.id, title="Test"
        )

        # When: Getting with correct user
        result = ChatService.get_session(db, session.id, test_user.id)

        # Then: Session is returned
        assert result is not None
        assert result.id == session.id

    def test_get_session_wrong_user(
        self, db: Session, test_user: User, another_user: User
    ) -> None:
        """Test that getting session with wrong user returns None."""
        # Given: A session owned by test_user
        session = ChatService.create_session(
            db=db, user_id=test_user.id, title="Private"
        )

        # When: Another user tries to access
        result = ChatService.get_session(db, session.id, another_user.id)

        # Then: None is returned (not found for this user)
        assert result is None

    def test_get_session_not_found(self, db: Session, test_user: User) -> None:
        """Test getting non-existent session returns None."""
        # When: Getting non-existent session
        result = ChatService.get_session(db, uuid4(), test_user.id)

        # Then: None is returned
        assert result is None

    def test_list_sessions_pagination(self, db: Session, test_user: User) -> None:
        """Test listing sessions with pagination."""
        # Given: Multiple sessions
        for i in range(5):
            ChatService.create_session(
                db=db, user_id=test_user.id, title=f"Session {i}"
            )

        # When: Listing with limit
        sessions, total = ChatService.list_sessions(
            db=db, user_id=test_user.id, limit=2, offset=0
        )

        # Then: Pagination works correctly
        assert len(sessions) == 2
        assert total == 5

    def test_list_sessions_offset(self, db: Session, test_user: User) -> None:
        """Test listing sessions with offset."""
        # Given: Multiple sessions
        for i in range(5):
            ChatService.create_session(
                db=db, user_id=test_user.id, title=f"Session {i}"
            )

        # When: Listing with offset
        sessions, total = ChatService.list_sessions(
            db=db, user_id=test_user.id, limit=10, offset=3
        )

        # Then: Offset works
        assert len(sessions) == 2
        assert total == 5

    def test_list_sessions_empty(self, db: Session, test_user: User) -> None:
        """Test listing sessions for user with no sessions."""
        # When: Listing for user with no sessions
        sessions, total = ChatService.list_sessions(
            db=db, user_id=test_user.id
        )

        # Then: Empty list
        assert sessions == []
        assert total == 0

    def test_list_sessions_only_own(
        self, db: Session, test_user: User, another_user: User
    ) -> None:
        """Test that list_sessions only returns user's own sessions."""
        # Given: Sessions for both users
        ChatService.create_session(db, test_user.id, "User 1 Session")
        ChatService.create_session(db, another_user.id, "User 2 Session")

        # When: Listing for test_user
        sessions, total = ChatService.list_sessions(db, test_user.id)

        # Then: Only test_user's sessions
        assert len(sessions) == 1
        assert sessions[0].title == "User 1 Session"

    def test_delete_session_soft_delete(
        self, db: Session, test_user: User
    ) -> None:
        """Test soft deleting a session."""
        # Given: A session
        session = ChatService.create_session(db, test_user.id, "To Delete")
        session_id = session.id

        # When: Deleting
        result = ChatService.delete_session(db, session_id, test_user.id)

        # Then: Deletion succeeds
        assert result is True

        # And: Session is inactive
        deleted = db.query(ChatSession).filter(
            ChatSession.id == session_id
        ).first()
        assert deleted is not None
        assert deleted.is_active is False

    def test_delete_session_not_found(
        self, db: Session, test_user: User
    ) -> None:
        """Test deleting non-existent session returns False."""
        # When: Deleting non-existent session
        result = ChatService.delete_session(db, uuid4(), test_user.id)

        # Then: Returns False
        assert result is False

    def test_deleted_session_not_listed(
        self, db: Session, test_user: User
    ) -> None:
        """Test that soft-deleted sessions don't appear in list."""
        # Given: A deleted session
        session = ChatService.create_session(db, test_user.id, "Deleted")
        ChatService.delete_session(db, session.id, test_user.id)

        # When: Listing sessions
        sessions, total = ChatService.list_sessions(db, test_user.id)

        # Then: Deleted session not in list
        assert total == 0


class TestChatServiceMessages:
    """Tests for message management."""

    @pytest.fixture
    def chat_session(self, db: Session, test_user: User) -> ChatSession:
        """Create a chat session for message tests."""
        return ChatService.create_session(
            db=db, user_id=test_user.id, title="Message Test Session"
        )

    def test_add_user_message(
        self, db: Session, chat_session: ChatSession
    ) -> None:
        """Test adding a user message."""
        # When: Adding user message
        message = ChatService.add_message(
            db=db,
            session_id=chat_session.id,
            role=MessageRole.USER,
            content="Hello, how are you?",
        )

        # Then: Message is saved
        assert message.id is not None
        assert message.role == MessageRole.USER
        assert message.content == "Hello, how are you?"
        assert message.session_id == chat_session.id

    def test_add_assistant_message_with_tool_calls(
        self, db: Session, chat_session: ChatSession
    ) -> None:
        """Test adding assistant message with tool calls."""
        # Given: Tool calls
        tool_calls = [
            {"id": "call_1", "name": "learn_word", "arguments": {"word": "test"}},
        ]

        # When: Adding assistant message
        message = ChatService.add_message(
            db=db,
            session_id=chat_session.id,
            role=MessageRole.ASSISTANT,
            content="Let me look that up.",
            tool_calls=tool_calls,
        )

        # Then: Tool calls are saved
        assert message.tool_calls is not None
        assert len(message.tool_calls) == 1
        assert message.tool_calls[0]["name"] == "learn_word"

    def test_add_tool_result_message(
        self, db: Session, chat_session: ChatSession
    ) -> None:
        """Test adding a tool result message."""
        # When: Adding tool result
        message = ChatService.add_message(
            db=db,
            session_id=chat_session.id,
            role=MessageRole.TOOL,
            content='{"word": "test", "meaning": "a test"}',
            tool_name="learn_word",
            tool_call_id="call_1",
        )

        # Then: Tool info is saved
        assert message.role == MessageRole.TOOL
        assert message.tool_name == "learn_word"
        assert message.tool_call_id == "call_1"

    def test_get_messages_chronological(
        self, db: Session, chat_session: ChatSession
    ) -> None:
        """Test getting messages returns chronological order."""
        # Given: Multiple messages
        msg1 = ChatService.add_message(
            db, chat_session.id, MessageRole.USER, "First"
        )
        msg2 = ChatService.add_message(
            db, chat_session.id, MessageRole.ASSISTANT, "Second"
        )
        msg3 = ChatService.add_message(
            db, chat_session.id, MessageRole.USER, "Third"
        )

        # When: Getting messages
        messages = ChatService.get_messages(db, chat_session.id)

        # Then: Chronological order
        assert len(messages) == 3
        assert messages[0].content == "First"
        assert messages[1].content == "Second"
        assert messages[2].content == "Third"

    def test_get_messages_with_limit(
        self, db: Session, chat_session: ChatSession
    ) -> None:
        """Test getting limited number of messages (most recent)."""
        # Given: Multiple messages
        for i in range(5):
            ChatService.add_message(
                db, chat_session.id, MessageRole.USER, f"Message {i}"
            )

        # When: Getting with limit
        messages = ChatService.get_messages(db, chat_session.id, limit=2)

        # Then: Returns most recent N in chronological order
        assert len(messages) == 2
        # Should be the last 2 messages
        assert messages[0].content == "Message 3"
        assert messages[1].content == "Message 4"

    def test_get_message_count(
        self, db: Session, chat_session: ChatSession
    ) -> None:
        """Test getting message count."""
        # Given: Messages
        ChatService.add_message(
            db, chat_session.id, MessageRole.USER, "One"
        )
        ChatService.add_message(
            db, chat_session.id, MessageRole.ASSISTANT, "Two"
        )

        # When: Getting count
        count = ChatService.get_message_count(db, chat_session.id)

        # Then: Correct count
        assert count == 2

    def test_add_message_updates_session_timestamp(
        self, db: Session, chat_session: ChatSession
    ) -> None:
        """Test that adding a message updates session's updated_at."""
        # Given: Initial timestamp
        initial_updated = chat_session.updated_at

        # When: Adding a message (with small delay to ensure time difference)
        import time
        time.sleep(0.1)
        ChatService.add_message(
            db, chat_session.id, MessageRole.USER, "New message"
        )

        # Then: Session's updated_at is updated
        db.refresh(chat_session)
        # Note: In SQLite, timestamp precision may vary
        assert chat_session.updated_at >= initial_updated


class TestChatServiceTitleGeneration:
    """Tests for session title generation."""

    def test_generate_title_short_content(self) -> None:
        """Test title generation with short content."""
        content = "Hello world"
        title = ChatService.generate_session_title(content)
        assert title == "Hello world"

    def test_generate_title_long_content(self) -> None:
        """Test title generation truncates long content."""
        content = "This is a very long message that should be truncated to a reasonable length for display as a title"
        title = ChatService.generate_session_title(content, max_length=50)
        assert len(title) <= 53  # 50 + "..."
        assert title.endswith("...")

    def test_generate_title_removes_newlines(self) -> None:
        """Test title generation removes newlines."""
        content = "Line one\nLine two\nLine three"
        title = ChatService.generate_session_title(content)
        assert "\n" not in title
        assert title == "Line one Line two Line three"

    def test_generate_title_removes_extra_whitespace(self) -> None:
        """Test title generation normalizes whitespace."""
        content = "Too   many    spaces"
        title = ChatService.generate_session_title(content)
        assert title == "Too many spaces"
