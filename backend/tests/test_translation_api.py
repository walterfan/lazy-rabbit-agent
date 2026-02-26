"""API tests for translation endpoints: auth, validation, 400 on neither/both input."""

import pytest
from fastapi.testclient import TestClient


class TestTranslationAuth:
    """Translation endpoints require authentication."""

    def test_post_translation_requires_auth(self, client: TestClient):
        response = client.post(
            "/api/v1/translation/",
            json={"url": "https://example.com/article"},
        )
        assert response.status_code == 401

    def test_post_translation_stream_requires_auth(self, client: TestClient):
        response = client.post(
            "/api/v1/translation/stream",
            json={"url": "https://example.com/article"},
        )
        assert response.status_code == 401


class TestTranslationValidation:
    """Validation: exactly one of URL or file."""

    def test_neither_url_nor_file_json_400(self, client: TestClient, test_user_token: str):
        response = client.post(
            "/api/v1/translation/",
            json={},
            headers={"Authorization": f"Bearer {test_user_token}"},
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    def test_empty_url_400(self, client: TestClient, test_user_token: str):
        response = client.post(
            "/api/v1/translation/",
            json={"url": "   "},
            headers={"Authorization": f"Bearer {test_user_token}"},
        )
        assert response.status_code in (400, 422)

    def test_unsupported_file_type_400(
        self, client: TestClient, test_user_token: str
    ):
        files = {"file": ("x.bin", b"binary content", "application/octet-stream")}
        data = {"output_mode": "chinese_only"}
        response = client.post(
            "/api/v1/translation/",
            data=data,
            files=files,
            headers={"Authorization": f"Bearer {test_user_token}"},
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data and ("Unsupported" in data["detail"] or "allowed" in data["detail"].lower())
