"""API tests for Philosophy Master endpoints."""

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient


class TestPhilosophyAuth:
    def test_chat_requires_auth(self, client: TestClient):
        resp = client.post("/api/v1/philosophy/chat", json={"message": "hello"})
        assert resp.status_code == 401

    def test_chat_stream_requires_auth(self, client: TestClient):
        resp = client.post("/api/v1/philosophy/chat/stream", json={"message": "hello"})
        assert resp.status_code == 401


class TestPhilosophyValidation:
    def test_empty_message_400(self, client: TestClient, test_user_token: str):
        resp = client.post(
            "/api/v1/philosophy/chat",
            json={"message": "   "},
            headers={"Authorization": f"Bearer {test_user_token}"},
        )
        assert resp.status_code == 400

    def test_invalid_preset_400(self, client: TestClient, test_user_token: str):
        resp = client.post(
            "/api/v1/philosophy/chat",
            json={"message": "hi", "preset": {"tone": "angry"}},
            headers={"Authorization": f"Bearer {test_user_token}"},
        )
        assert resp.status_code == 400


class TestPhilosophyStreaming:
    def test_stream_content_type(self, client: TestClient, test_user_token: str):
        resp = client.post(
            "/api/v1/philosophy/chat/stream",
            json={"message": "hello"},
            headers={"Authorization": f"Bearer {test_user_token}"},
        )
        assert resp.status_code == 200
        assert resp.headers.get("content-type", "").startswith("text/event-stream")

