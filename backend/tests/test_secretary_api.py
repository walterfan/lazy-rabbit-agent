"""
Integration tests for Secretary API endpoints.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4

from fastapi.testclient import TestClient

from app.models.chat_message import MessageRole


class TestSecretaryChat:
    """Tests for /secretary/chat endpoint."""
    
    def test_chat_requires_auth(self, client: TestClient):
        """Chat endpoint requires authentication."""
        response = client.post(
            "/api/v1/secretary/chat",
            json={"message": "hello"}
        )
        assert response.status_code == 401
    
    def test_chat_creates_new_session(
        self,
        client: TestClient,
        test_user_token: str,
        db_session,
    ):
        """Chat creates a new session if none provided."""
        with patch("app.services.secretary_agent.agent.SecretaryAgent") as mock_agent:
            # Mock the agent's chat method
            mock_instance = MagicMock()
            mock_instance.chat = AsyncMock(return_value={
                "content": "Hello! How can I help you?",
                "tool_calls": [],
            })
            mock_agent.return_value = mock_instance
            
            response = client.post(
                "/api/v1/secretary/chat",
                json={"message": "hello"},
                headers={"Authorization": f"Bearer {test_user_token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "session_id" in data
            assert "message_id" in data
            assert data["content"] == "Hello! How can I help you?"
    
    def test_chat_uses_existing_session(
        self,
        client: TestClient,
        test_user_token: str,
        db_session,
    ):
        """Chat uses existing session when provided."""
        # First, create a session
        with patch("app.services.secretary_agent.agent.SecretaryAgent") as mock_agent:
            mock_instance = MagicMock()
            mock_instance.chat = AsyncMock(return_value={
                "content": "First response",
                "tool_calls": [],
            })
            mock_agent.return_value = mock_instance
            
            response1 = client.post(
                "/api/v1/secretary/chat",
                json={"message": "first message"},
                headers={"Authorization": f"Bearer {test_user_token}"}
            )
            session_id = response1.json()["session_id"]
            
            # Now send second message to same session
            mock_instance.chat = AsyncMock(return_value={
                "content": "Second response",
                "tool_calls": [],
            })
            
            response2 = client.post(
                "/api/v1/secretary/chat",
                json={"message": "second message", "session_id": session_id},
                headers={"Authorization": f"Bearer {test_user_token}"}
            )
            
            assert response2.status_code == 200
            assert response2.json()["session_id"] == session_id
    
    def test_chat_invalid_session_returns_404(
        self,
        client: TestClient,
        test_user_token: str,
    ):
        """Chat returns 404 for invalid session ID."""
        fake_session_id = str(uuid4())
        
        response = client.post(
            "/api/v1/secretary/chat",
            json={"message": "hello", "session_id": fake_session_id},
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        assert response.status_code == 404


class TestSecretarySessions:
    """Tests for session management endpoints."""
    
    def test_list_sessions_empty(
        self,
        client: TestClient,
        test_user_token: str,
    ):
        """List sessions returns empty list for new user."""
        response = client.get(
            "/api/v1/secretary/sessions",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "sessions" in data
        assert data["total"] >= 0
    
    def test_get_session_not_found(
        self,
        client: TestClient,
        test_user_token: str,
    ):
        """Get session returns 404 for non-existent session."""
        fake_id = str(uuid4())
        
        response = client.get(
            f"/api/v1/secretary/sessions/{fake_id}",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        assert response.status_code == 404
    
    def test_delete_session_not_found(
        self,
        client: TestClient,
        test_user_token: str,
    ):
        """Delete session returns 404 for non-existent session."""
        fake_id = str(uuid4())
        
        response = client.delete(
            f"/api/v1/secretary/sessions/{fake_id}",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        assert response.status_code == 404


class TestSecretaryTools:
    """Tests for tools endpoint."""
    
    def test_list_tools(
        self,
        client: TestClient,
        test_user_token: str,
    ):
        """List tools returns available tools."""
        response = client.get(
            "/api/v1/secretary/tools",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "tools" in data
        
        # Check we have learning and utility tools
        tool_names = [t["name"] for t in data["tools"]]
        assert "learn_word" in tool_names
        assert "learn_sentence" in tool_names
        assert "calculate" in tool_names
        assert "get_datetime" in tool_names


class TestLearningRecords:
    """Tests for learning record endpoints."""
    
    def test_confirm_learning_creates_record(
        self,
        client: TestClient,
        test_user_token: str,
    ):
        """Confirm learning creates a new record."""
        response = client.post(
            "/api/v1/learning/confirm",
            json={
                "input_type": "word",
                "user_input": "hello",
                "response_payload": {
                    "word": "hello",
                    "phonetic": "/həˈloʊ/",
                    "meaning": "A greeting",
                },
            },
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["input_type"] == "word"
        assert data["user_input"] == "hello"
        assert "id" in data
    
    def test_list_learning_records(
        self,
        client: TestClient,
        test_user_token: str,
    ):
        """List learning records with pagination."""
        response = client.get(
            "/api/v1/learning/records",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "records" in data
        assert "total" in data
        assert "page" in data
    
    def test_search_learning_records(
        self,
        client: TestClient,
        test_user_token: str,
    ):
        """Search learning records by query."""
        # First create a record
        client.post(
            "/api/v1/learning/confirm",
            json={
                "input_type": "word",
                "user_input": "searchable",
                "response_payload": {"word": "searchable"},
            },
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        # Now search
        response = client.get(
            "/api/v1/learning/search?q=searchable",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "records" in data
    
    def test_toggle_favorite(
        self,
        client: TestClient,
        test_user_token: str,
    ):
        """Toggle favorite status of a record."""
        # Create a record
        create_response = client.post(
            "/api/v1/learning/confirm",
            json={
                "input_type": "word",
                "user_input": "favorite_test",
                "response_payload": {"word": "favorite_test"},
            },
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        record_id = create_response.json()["id"]
        
        # Toggle favorite
        response = client.post(
            f"/api/v1/learning/records/{record_id}/favorite",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        assert response.status_code == 200
        assert response.json()["is_favorite"] == True
        
        # Toggle again
        response2 = client.post(
            f"/api/v1/learning/records/{record_id}/favorite",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        assert response2.json()["is_favorite"] == False
    
    def test_get_statistics(
        self,
        client: TestClient,
        test_user_token: str,
    ):
        """Get learning statistics."""
        response = client.get(
            "/api/v1/learning/statistics",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "by_type" in data
        assert "favorites" in data
        assert "total_reviews" in data
