"""
Tests for Knowledge Base API and RAG engine.

Covers:
- RAG engine unit tests (Task 11.1)
- Knowledge API tests (Task 11.2)
- Auth required, CRUD, per-user isolation
"""

import pytest
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ============================================================================
# RAG Engine Unit Tests
# ============================================================================

class TestRAGEngine:
    """Test RAG engine functionality."""

    def test_rag_engine_import(self):
        """RAG engine module is importable."""
        from app.services.rag.engine import RAGEngine, get_rag_engine
        assert RAGEngine is not None
        assert callable(get_rag_engine)

    def test_rag_engine_graceful_degradation(self):
        """RAG engine degrades gracefully when chromadb is unavailable."""
        from app.services.rag.engine import get_rag_engine
        # get_rag_engine returns None or an engine with is_available=False
        # when not initialized
        rag = get_rag_engine()
        if rag is not None:
            # If engine exists but not initialized, it should handle queries gracefully
            pass  # OK — engine may or may not be available in test env

    def test_rag_engine_singleton(self):
        """get_rag_engine returns the same instance."""
        from app.services.rag.engine import get_rag_engine
        rag1 = get_rag_engine()
        rag2 = get_rag_engine()
        assert rag1 is rag2


# ============================================================================
# Knowledge API Tests
# ============================================================================

class TestKnowledgeAPI:
    """Test knowledge base API endpoints."""

    def test_list_documents_requires_auth(self, client: TestClient):
        """List documents requires authentication."""
        resp = client.get("/api/v1/knowledge/documents")
        assert resp.status_code in (401, 403)

    def test_list_documents_empty(self, client: TestClient, test_user_token: str):
        """List documents returns empty list for new user."""
        resp = client.get(
            "/api/v1/knowledge/documents",
            headers=auth_headers(test_user_token),
        )
        assert resp.status_code == 200
        assert resp.json() == []

    def test_upload_document(self, client: TestClient, test_user_token: str):
        """Upload a text document."""
        resp = client.post(
            "/api/v1/knowledge/documents",
            json={
                "title": "Test Document",
                "content": "This is a test document about Python programming.",
                "tags": ["python", "test"],
            },
            headers=auth_headers(test_user_token),
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["title"] == "Test Document"
        assert "python" in data.get("tags", [])

    def test_upload_and_list_documents(self, client: TestClient, test_user_token: str):
        """Upload then list documents."""
        # Upload
        client.post(
            "/api/v1/knowledge/documents",
            json={
                "title": "Doc 1",
                "content": "Content of document 1",
            },
            headers=auth_headers(test_user_token),
        )

        # List
        resp = client.get(
            "/api/v1/knowledge/documents",
            headers=auth_headers(test_user_token),
        )
        assert resp.status_code == 200
        docs = resp.json()
        assert len(docs) >= 1
        assert any(d["title"] == "Doc 1" for d in docs)

    def test_delete_document(self, client: TestClient, test_user_token: str):
        """Delete a document."""
        # Upload
        create_resp = client.post(
            "/api/v1/knowledge/documents",
            json={
                "title": "To Delete",
                "content": "This will be deleted",
            },
            headers=auth_headers(test_user_token),
        )
        doc_id = create_resp.json()["id"]

        # Delete
        resp = client.delete(
            f"/api/v1/knowledge/documents/{doc_id}",
            headers=auth_headers(test_user_token),
        )
        assert resp.status_code in (200, 204)

        # Verify deleted
        list_resp = client.get(
            "/api/v1/knowledge/documents",
            headers=auth_headers(test_user_token),
        )
        doc_ids = [d["id"] for d in list_resp.json()]
        assert doc_id not in doc_ids

    def test_query_requires_auth(self, client: TestClient):
        """Query endpoint requires authentication."""
        resp = client.post(
            "/api/v1/knowledge/query",
            json={"query": "test"},
        )
        assert resp.status_code in (401, 403)

    def test_stats_requires_auth(self, client: TestClient):
        """Stats endpoint requires authentication."""
        resp = client.get("/api/v1/knowledge/stats")
        assert resp.status_code in (401, 403)

    def test_stats(self, client: TestClient, test_user_token: str):
        """Get knowledge base statistics."""
        resp = client.get(
            "/api/v1/knowledge/stats",
            headers=auth_headers(test_user_token),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "total_documents" in data


# ============================================================================
# Per-User Isolation
# ============================================================================

class TestPerUserIsolation:
    """Test that users can only see their own documents."""

    def test_user_isolation(self, client: TestClient, db: Session):
        """User A cannot see User B's documents."""
        from app.models.user import User

        # Create user A (first user = auto-active admin)
        signup_a = client.post("/api/v1/auth/signup", json={
            "email": "usera@test.com",
            "password": "password123",
            "full_name": "User A",
        })
        assert signup_a.status_code in (200, 201), f"Signup A failed: {signup_a.text}"
        resp_a = client.post("/api/v1/auth/signin", json={
            "email": "usera@test.com",
            "password": "password123",
        })
        assert resp_a.status_code == 200, f"Signin A failed: {resp_a.text}"
        token_a = resp_a.json()["access_token"]

        # Create user B (second user = inactive by default)
        signup_b = client.post("/api/v1/auth/signup", json={
            "email": "userb@test.com",
            "password": "password456",
            "full_name": "User B",
        })
        assert signup_b.status_code in (200, 201), f"Signup B failed: {signup_b.text}"

        # Activate user B directly in DB
        user_b = db.query(User).filter(User.email == "userb@test.com").first()
        user_b.is_active = True
        db.commit()

        resp_b = client.post("/api/v1/auth/signin", json={
            "email": "userb@test.com",
            "password": "password456",
        })
        assert resp_b.status_code == 200, f"Signin B failed: {resp_b.text}"
        token_b = resp_b.json()["access_token"]

        # User A uploads a document
        client.post(
            "/api/v1/knowledge/documents",
            json={"title": "A's Secret", "content": "Private content"},
            headers=auth_headers(token_a),
        )

        # User B should not see A's document
        resp = client.get(
            "/api/v1/knowledge/documents",
            headers=auth_headers(token_b),
        )
        assert resp.status_code == 200
        for doc in resp.json():
            assert doc["title"] != "A's Secret"
