"""
Tests for the APScheduler integration.

Tests:
  1. SchedulerService lifecycle (start/shutdown)
  2. Job registration and listing
  3. Dynamic job add/remove
  4. Job pause/resume
  5. Job trigger (immediate execution)
  6. Scheduled job functions (unit tests)
"""

import asyncio
import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from app.services.scheduler import SchedulerService


# ============================================================================
# SchedulerService tests — need a running event loop for AsyncIOScheduler
# ============================================================================

class TestSchedulerService:
    """Test the SchedulerService lifecycle and job management."""

    def test_initial_state(self):
        """Scheduler should not be running initially."""
        svc = SchedulerService()
        assert not svc.is_running
        assert svc.list_jobs() == []

    @pytest.mark.asyncio
    async def test_start_and_shutdown(self):
        """Scheduler should start and shut down cleanly."""
        svc = SchedulerService()
        svc.start(timezone="UTC")
        assert svc.is_running

        jobs = svc.list_jobs()
        assert len(jobs) == 4  # 4 default jobs
        job_ids = {j["id"] for j in jobs}
        assert "check_due_reminders" in job_ids
        assert "check_overdue_tasks" in job_ids
        assert "daily_summary" in job_ids
        assert "send_scheduled_emails" in job_ids

        svc.shutdown()
        assert not svc.is_running

    @pytest.mark.asyncio
    async def test_double_start_is_safe(self):
        """Starting twice should not raise."""
        svc = SchedulerService()
        svc.start(timezone="UTC")
        svc.start(timezone="UTC")  # Should log warning, not crash
        assert svc.is_running
        svc.shutdown()

    @pytest.mark.asyncio
    async def test_add_and_remove_job(self):
        """Should be able to dynamically add and remove jobs."""
        svc = SchedulerService()
        svc.start(timezone="UTC")

        async def dummy_job():
            pass

        # Add a job
        job_info = svc.add_job(
            job_id="test_job",
            func=dummy_job,
            trigger_type="interval",
            name="Test Job",
            seconds=60,
        )
        assert job_info["id"] == "test_job"
        assert job_info["name"] == "Test Job"

        # Verify it's listed
        jobs = svc.list_jobs()
        job_ids = {j["id"] for j in jobs}
        assert "test_job" in job_ids

        # Remove it
        assert svc.remove_job("test_job") is True
        assert svc.remove_job("nonexistent") is False

        # Verify it's gone
        jobs = svc.list_jobs()
        job_ids = {j["id"] for j in jobs}
        assert "test_job" not in job_ids

        svc.shutdown()

    @pytest.mark.asyncio
    async def test_add_cron_job(self):
        """Should support cron trigger type."""
        svc = SchedulerService()
        svc.start(timezone="UTC")

        async def dummy_job():
            pass

        job_info = svc.add_job(
            job_id="cron_test",
            func=dummy_job,
            trigger_type="cron",
            hour=9,
            minute=30,
        )
        assert job_info["id"] == "cron_test"
        assert "cron" in job_info["trigger"].lower()

        svc.shutdown()

    @pytest.mark.asyncio
    async def test_invalid_trigger_type(self):
        """Should raise ValueError for unknown trigger type."""
        svc = SchedulerService()
        svc.start(timezone="UTC")

        async def dummy_job():
            pass

        with pytest.raises(ValueError, match="Unknown trigger_type"):
            svc.add_job(
                job_id="bad_trigger",
                func=dummy_job,
                trigger_type="invalid",
            )

        svc.shutdown()

    def test_add_job_when_not_running(self):
        """Should raise RuntimeError if scheduler is not running."""
        svc = SchedulerService()

        async def dummy_job():
            pass

        with pytest.raises(RuntimeError, match="not running"):
            svc.add_job(
                job_id="test",
                func=dummy_job,
                trigger_type="interval",
                seconds=60,
            )

    @pytest.mark.asyncio
    async def test_pause_and_resume_job(self):
        """Should be able to pause and resume jobs."""
        svc = SchedulerService()
        svc.start(timezone="UTC")

        assert svc.pause_job("check_due_reminders") is True
        assert svc.resume_job("check_due_reminders") is True
        assert svc.pause_job("nonexistent") is False
        assert svc.resume_job("nonexistent") is False

        svc.shutdown()

    @pytest.mark.asyncio
    async def test_trigger_job(self):
        """Should be able to trigger a job immediately."""
        svc = SchedulerService()
        svc.start(timezone="UTC")

        assert svc.trigger_job("check_due_reminders") is True
        assert svc.trigger_job("nonexistent") is False

        svc.shutdown()

    def test_job_history_initially_empty(self):
        """Job history should be empty initially."""
        svc = SchedulerService()
        assert svc.get_job_history() == []

    @pytest.mark.asyncio
    async def test_job_to_dict(self):
        """Job dict should have expected keys."""
        svc = SchedulerService()
        svc.start(timezone="UTC")

        jobs = svc.list_jobs()
        assert len(jobs) > 0

        job = jobs[0]
        assert "id" in job
        assert "name" in job
        assert "trigger" in job
        assert "next_run_time" in job
        assert "pending" in job

        svc.shutdown()

    @pytest.mark.asyncio
    async def test_replace_existing_job(self):
        """Adding a job with the same ID should replace it."""
        svc = SchedulerService()
        svc.start(timezone="UTC")

        async def dummy_job():
            pass

        svc.add_job(
            job_id="replaceable",
            func=dummy_job,
            trigger_type="interval",
            name="Version 1",
            seconds=60,
        )

        svc.add_job(
            job_id="replaceable",
            func=dummy_job,
            trigger_type="interval",
            name="Version 2",
            seconds=120,
        )

        jobs = svc.list_jobs()
        replaceable = [j for j in jobs if j["id"] == "replaceable"]
        assert len(replaceable) == 1
        assert replaceable[0]["name"] == "Version 2"

        svc.shutdown()


# ============================================================================
# Scheduled job function tests (mock DB)
# ============================================================================

class TestScheduledJobs:
    """Test the individual job functions."""

    @pytest.mark.asyncio
    async def test_check_due_reminders_no_data(self):
        """Should handle empty database gracefully."""
        from app.services.scheduled_jobs import job_check_due_reminders

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = []

        with patch("app.services.scheduled_jobs.SessionLocal", return_value=mock_db):
            result = await job_check_due_reminders()

        assert result["triggered"] == 0
        assert result["repeated"] == 0
        mock_db.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_overdue_tasks_no_data(self):
        """Should handle empty database gracefully."""
        from app.services.scheduled_jobs import job_check_overdue_tasks

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = []

        with patch("app.services.scheduled_jobs.SessionLocal", return_value=mock_db):
            result = await job_check_overdue_tasks()

        assert result["overdue_count"] == 0
        assert result["users_affected"] == 0
        mock_db.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_daily_summary_no_users(self):
        """Should handle no active users gracefully."""
        from app.services.scheduled_jobs import job_daily_summary

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = []

        with patch("app.services.scheduled_jobs.SessionLocal", return_value=mock_db):
            result = await job_daily_summary()

        assert result["users_processed"] == 0
        assert result["errors"] == 0
        mock_db.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_due_reminders_with_data(self):
        """Should trigger due reminders and handle repeats."""
        from app.services.scheduled_jobs import job_check_due_reminders

        # Create a mock due reminder
        mock_reminder = MagicMock()
        mock_reminder.status = "pending"
        mock_reminder.snoozed_until = None
        mock_reminder.remind_at = datetime(2020, 1, 1)  # In the past
        mock_reminder.repeat = "none"
        mock_reminder.user_id = 1
        mock_reminder.title = "Test Reminder"

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_reminder]

        with patch("app.services.scheduled_jobs.SessionLocal", return_value=mock_db):
            result = await job_check_due_reminders()

        assert result["triggered"] == 1
        assert result["repeated"] == 0
        assert mock_reminder.status == "triggered"
        mock_db.commit.assert_called_once()
        mock_db.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_due_reminders_with_repeat(self):
        """Should create next occurrence for repeating reminders."""
        from app.services.scheduled_jobs import job_check_due_reminders

        mock_reminder = MagicMock()
        mock_reminder.status = "pending"
        mock_reminder.snoozed_until = None
        mock_reminder.remind_at = datetime(2020, 1, 1)
        mock_reminder.repeat = "daily"
        mock_reminder.user_id = 1
        mock_reminder.title = "Daily Standup"
        mock_reminder.description = "Team standup"
        mock_reminder.tags = ["work"]
        mock_reminder.session_id = None

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_reminder]

        with patch("app.services.scheduled_jobs.SessionLocal", return_value=mock_db):
            result = await job_check_due_reminders()

        assert result["triggered"] == 1
        assert result["repeated"] == 1
        mock_db.add.assert_called_once()  # New reminder added
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_due_reminders_db_error(self):
        """Should handle DB errors gracefully."""
        from app.services.scheduled_jobs import job_check_due_reminders

        mock_db = MagicMock()
        mock_db.query.side_effect = Exception("DB connection lost")

        with patch("app.services.scheduled_jobs.SessionLocal", return_value=mock_db):
            result = await job_check_due_reminders()

        # Should still return a result (with 0 counts) and not crash
        assert result["triggered"] == 0
        mock_db.rollback.assert_called_once()
        mock_db.close.assert_called_once()


# ============================================================================
# Helper function tests
# ============================================================================

class TestCalculateNextOccurrence:
    """Test the repeat schedule calculator."""

    def test_daily_repeat(self):
        from app.services.scheduled_jobs import _calculate_next_occurrence

        now = datetime(2026, 3, 7, 8, 0, 0)
        result = _calculate_next_occurrence(now, "daily")
        assert result == datetime(2026, 3, 8, 8, 0, 0)

    def test_weekly_repeat(self):
        from app.services.scheduled_jobs import _calculate_next_occurrence

        now = datetime(2026, 3, 7, 8, 0, 0)
        result = _calculate_next_occurrence(now, "weekly")
        assert result == datetime(2026, 3, 14, 8, 0, 0)

    def test_monthly_repeat(self):
        from app.services.scheduled_jobs import _calculate_next_occurrence

        now = datetime(2026, 3, 7, 8, 0, 0)
        result = _calculate_next_occurrence(now, "monthly")
        expected = now + timedelta(days=30)
        assert result == expected

    def test_yearly_repeat(self):
        from app.services.scheduled_jobs import _calculate_next_occurrence

        now = datetime(2026, 3, 7, 8, 0, 0)
        result = _calculate_next_occurrence(now, "yearly")
        expected = now + timedelta(days=365)
        assert result == expected

    def test_no_repeat(self):
        from app.services.scheduled_jobs import _calculate_next_occurrence

        now = datetime(2026, 3, 7, 8, 0, 0)
        result = _calculate_next_occurrence(now, "none")
        assert result is None

    def test_unknown_repeat(self):
        from app.services.scheduled_jobs import _calculate_next_occurrence

        now = datetime(2026, 3, 7, 8, 0, 0)
        result = _calculate_next_occurrence(now, "biweekly")
        assert result is None
