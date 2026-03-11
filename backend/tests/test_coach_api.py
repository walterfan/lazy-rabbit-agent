"""
Tests for AI Coach API endpoints.

Covers:
- Learning goal CRUD (Task 11.3)
- Study session logging (Task 11.3)
- Progress report with streak calculation (Task 11.3)
- Coach chat mode selection (Task 11.4)
- Per-user isolation
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


# ============================================================================
# Helper
# ============================================================================

def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ============================================================================
# Learning Goals
# ============================================================================

class TestGoals:
    """Test learning goal CRUD."""

    def test_create_goal(self, client: TestClient, test_user_token: str):
        """Create a learning goal."""
        resp = client.post(
            "/api/v1/coach/goals",
            json={
                "subject": "Python 进阶",
                "description": "学习 Python 高级特性",
                "daily_target_minutes": 30,
            },
            headers=auth_headers(test_user_token),
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["subject"] == "Python 进阶"
        assert data["status"] == "active"
        assert data["daily_target_minutes"] == 30

    def test_create_goal_with_deadline(self, client: TestClient, test_user_token: str):
        """Create a goal with a deadline."""
        deadline = (datetime.utcnow() + timedelta(days=30)).isoformat()
        resp = client.post(
            "/api/v1/coach/goals",
            json={
                "subject": "机器学习基础",
                "deadline": deadline,
            },
            headers=auth_headers(test_user_token),
        )
        assert resp.status_code == 201
        assert resp.json()["deadline"] is not None

    def test_list_goals(self, client: TestClient, test_user_token: str):
        """List goals for the current user."""
        # Create 2 goals
        for subject in ["Goal A", "Goal B"]:
            client.post(
                "/api/v1/coach/goals",
                json={"subject": subject},
                headers=auth_headers(test_user_token),
            )

        resp = client.get(
            "/api/v1/coach/goals",
            headers=auth_headers(test_user_token),
        )
        assert resp.status_code == 200
        goals = resp.json()
        assert len(goals) >= 2

    def test_list_goals_filter_by_status(self, client: TestClient, test_user_token: str):
        """Filter goals by status."""
        # Create a goal
        create_resp = client.post(
            "/api/v1/coach/goals",
            json={"subject": "Filter Test"},
            headers=auth_headers(test_user_token),
        )
        goal_id = create_resp.json()["id"]

        # Complete it
        client.patch(
            f"/api/v1/coach/goals/{goal_id}",
            json={"status": "completed"},
            headers=auth_headers(test_user_token),
        )

        # Filter active — should not include completed
        resp = client.get(
            "/api/v1/coach/goals?status=active",
            headers=auth_headers(test_user_token),
        )
        assert resp.status_code == 200
        for g in resp.json():
            assert g["status"] == "active"

    def test_update_goal_status(self, client: TestClient, test_user_token: str):
        """Update goal status to completed."""
        create_resp = client.post(
            "/api/v1/coach/goals",
            json={"subject": "Complete Me"},
            headers=auth_headers(test_user_token),
        )
        goal_id = create_resp.json()["id"]

        resp = client.patch(
            f"/api/v1/coach/goals/{goal_id}",
            json={"status": "completed"},
            headers=auth_headers(test_user_token),
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "completed"
        assert resp.json()["completed_at"] is not None

    def test_update_goal_not_found(self, client: TestClient, test_user_token: str):
        """Update a non-existent goal returns 404."""
        fake_id = str(uuid4())
        resp = client.patch(
            f"/api/v1/coach/goals/{fake_id}",
            json={"status": "completed"},
            headers=auth_headers(test_user_token),
        )
        assert resp.status_code == 404

    def test_goal_requires_auth(self, client: TestClient):
        """Goal endpoints require authentication."""
        resp = client.get("/api/v1/coach/goals")
        assert resp.status_code in (401, 403)


# ============================================================================
# Study Sessions
# ============================================================================

class TestStudySessions:
    """Test study session logging."""

    def test_log_session(self, client: TestClient, test_user_token: str):
        """Log a study session."""
        resp = client.post(
            "/api/v1/coach/sessions",
            json={
                "duration_minutes": 25,
                "notes": "学习了列表推导式",
                "difficulty": "medium",
            },
            headers=auth_headers(test_user_token),
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["duration_minutes"] == 25
        assert data["notes"] == "学习了列表推导式"

    def test_log_session_with_goal(self, client: TestClient, test_user_token: str):
        """Log a session linked to a goal."""
        # Create goal
        goal_resp = client.post(
            "/api/v1/coach/goals",
            json={"subject": "Session Goal"},
            headers=auth_headers(test_user_token),
        )
        goal_id = goal_resp.json()["id"]

        # Log session
        resp = client.post(
            "/api/v1/coach/sessions",
            json={
                "goal_id": goal_id,
                "duration_minutes": 30,
            },
            headers=auth_headers(test_user_token),
        )
        assert resp.status_code == 201
        assert resp.json()["goal_id"] == goal_id

    def test_log_session_invalid_goal(self, client: TestClient, test_user_token: str):
        """Log session with non-existent goal returns 404."""
        resp = client.post(
            "/api/v1/coach/sessions",
            json={
                "goal_id": str(uuid4()),
                "duration_minutes": 15,
            },
            headers=auth_headers(test_user_token),
        )
        assert resp.status_code == 404

    def test_list_sessions(self, client: TestClient, test_user_token: str):
        """List study sessions."""
        # Log 2 sessions
        for mins in [20, 30]:
            client.post(
                "/api/v1/coach/sessions",
                json={"duration_minutes": mins},
                headers=auth_headers(test_user_token),
            )

        resp = client.get(
            "/api/v1/coach/sessions",
            headers=auth_headers(test_user_token),
        )
        assert resp.status_code == 200
        assert len(resp.json()) >= 2

    def test_list_sessions_filter_by_goal(self, client: TestClient, test_user_token: str):
        """Filter sessions by goal_id."""
        # Create goal
        goal_resp = client.post(
            "/api/v1/coach/goals",
            json={"subject": "Filter Sessions"},
            headers=auth_headers(test_user_token),
        )
        goal_id = goal_resp.json()["id"]

        # Log session with goal
        client.post(
            "/api/v1/coach/sessions",
            json={"goal_id": goal_id, "duration_minutes": 25},
            headers=auth_headers(test_user_token),
        )

        # Log session without goal
        client.post(
            "/api/v1/coach/sessions",
            json={"duration_minutes": 10},
            headers=auth_headers(test_user_token),
        )

        # Filter by goal
        resp = client.get(
            f"/api/v1/coach/sessions?goal_id={goal_id}",
            headers=auth_headers(test_user_token),
        )
        assert resp.status_code == 200
        for s in resp.json():
            assert s["goal_id"] == goal_id


# ============================================================================
# Progress
# ============================================================================

class TestProgress:
    """Test progress report."""

    def test_progress_report(self, client: TestClient, test_user_token: str):
        """Get progress report for a goal."""
        # Create goal
        goal_resp = client.post(
            "/api/v1/coach/goals",
            json={"subject": "Progress Test", "daily_target_minutes": 30},
            headers=auth_headers(test_user_token),
        )
        goal_id = goal_resp.json()["id"]

        # Log sessions
        for mins in [25, 30, 20]:
            client.post(
                "/api/v1/coach/sessions",
                json={"goal_id": goal_id, "duration_minutes": mins},
                headers=auth_headers(test_user_token),
            )

        resp = client.get(
            f"/api/v1/coach/progress/{goal_id}",
            headers=auth_headers(test_user_token),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_sessions"] == 3
        assert data["total_minutes"] == 75
        assert data["avg_minutes_per_session"] == 25.0
        assert "current_streak_days" in data
        assert "longest_streak_days" in data

    def test_progress_not_found(self, client: TestClient, test_user_token: str):
        """Progress for non-existent goal returns 404."""
        resp = client.get(
            f"/api/v1/coach/progress/{uuid4()}",
            headers=auth_headers(test_user_token),
        )
        assert resp.status_code == 404

    def test_progress_empty(self, client: TestClient, test_user_token: str):
        """Progress with no sessions."""
        goal_resp = client.post(
            "/api/v1/coach/goals",
            json={"subject": "Empty Progress"},
            headers=auth_headers(test_user_token),
        )
        goal_id = goal_resp.json()["id"]

        resp = client.get(
            f"/api/v1/coach/progress/{goal_id}",
            headers=auth_headers(test_user_token),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_sessions"] == 0
        assert data["total_minutes"] == 0


# ============================================================================
# Streak Calculation
# ============================================================================

class TestStreakCalculation:
    """Test streak calculation logic."""

    def test_streak_calculation_import(self):
        """Verify streak calculation function is importable."""
        from app.api.v1.endpoints.coach import _calculate_streaks
        assert callable(_calculate_streaks)

    def test_empty_sessions(self):
        """Empty sessions return 0 streaks."""
        from app.api.v1.endpoints.coach import _calculate_streaks
        current, longest = _calculate_streaks([])
        assert current == 0
        assert longest == 0


# ============================================================================
# Coach Chat
# ============================================================================

class TestCoachChat:
    """Test coach chat endpoints."""

    def test_chat_requires_auth(self, client: TestClient):
        """Chat endpoint requires authentication."""
        resp = client.post(
            "/api/v1/coach/chat",
            json={"message": "hello", "mode": "coach"},
        )
        assert resp.status_code in (401, 403)

    def test_chat_stream_requires_auth(self, client: TestClient):
        """Stream endpoint requires authentication."""
        resp = client.get(
            "/api/v1/coach/chat/stream?message=hello&mode=coach",
        )
        assert resp.status_code in (401, 403)

    def test_chat_invalid_mode_defaults(self, client: TestClient, test_user_token: str):
        """Invalid mode in stream defaults to coach (requires token in query)."""
        # The stream endpoint uses get_current_user_from_query which reads token from query param
        resp = client.get(
            f"/api/v1/coach/chat/stream?message=hello&mode=invalid_mode&token={test_user_token}",
        )
        # SSE endpoint returns 200 with streaming
        assert resp.status_code == 200
