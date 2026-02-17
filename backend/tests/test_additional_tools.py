"""
Tests for additional tools (notes, tasks, reminders).
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from app.models.task import TaskPriority, TaskStatus
from app.models.reminder import ReminderRepeat, ReminderStatus


class TestNoteTool:
    """Tests for note tools."""
    
    def test_save_note_basic(self, db_session, test_user):
        """Can save a basic note."""
        from app.services.secretary_agent.tools.note_tool import save_note
        
        result = save_note(
            content="This is a test note",
            db=db_session,
            user_id=test_user.id,
        )
        
        assert result.note_id
        assert result.content == "This is a test note"
        assert "保存" in result.message
    
    def test_save_note_with_title_and_tags(self, db_session, test_user):
        """Can save a note with title and tags."""
        from app.services.secretary_agent.tools.note_tool import save_note
        
        result = save_note(
            content="Note content",
            title="My Note",
            tags=["important", "work"],
            db=db_session,
            user_id=test_user.id,
        )
        
        assert result.title == "My Note"
        assert result.tags == ["important", "work"]
    
    def test_search_notes(self, db_session, test_user):
        """Can search notes."""
        from app.services.secretary_agent.tools.note_tool import save_note, search_notes
        
        # Create a note
        save_note(
            content="Unique searchable content xyz123",
            db=db_session,
            user_id=test_user.id,
        )
        
        # Search for it
        result = search_notes(
            query="xyz123",
            db=db_session,
            user_id=test_user.id,
        )
        
        assert result.total >= 1
        assert any("xyz123" in note["content"] for note in result.notes)
    
    def test_list_notes(self, db_session, test_user):
        """Can list notes."""
        from app.services.secretary_agent.tools.note_tool import save_note, list_notes
        
        # Create some notes
        for i in range(3):
            save_note(
                content=f"Note {i}",
                db=db_session,
                user_id=test_user.id,
            )
        
        result = list_notes(
            db=db_session,
            user_id=test_user.id,
        )
        
        assert result.total >= 3


class TestTaskTool:
    """Tests for task tools."""
    
    def test_create_task_basic(self, db_session, test_user):
        """Can create a basic task."""
        from app.services.secretary_agent.tools.task_tool import create_task
        
        result = create_task(
            title="Test task",
            db=db_session,
            user_id=test_user.id,
        )
        
        assert result.task_id
        assert result.title == "Test task"
        assert result.priority == TaskPriority.medium.value
    
    def test_create_task_with_due_date(self, db_session, test_user):
        """Can create a task with due date."""
        from app.services.secretary_agent.tools.task_tool import create_task
        
        tomorrow = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M")
        
        result = create_task(
            title="Task with deadline",
            due_date=tomorrow,
            priority="high",
            db=db_session,
            user_id=test_user.id,
        )
        
        assert result.due_date
        assert result.priority == TaskPriority.high.value
    
    def test_list_tasks(self, db_session, test_user):
        """Can list tasks."""
        from app.services.secretary_agent.tools.task_tool import create_task, list_tasks
        
        # Create some tasks
        for i in range(3):
            create_task(
                title=f"Task {i}",
                db=db_session,
                user_id=test_user.id,
            )
        
        result = list_tasks(
            db=db_session,
            user_id=test_user.id,
        )
        
        assert result.total >= 3
    
    def test_complete_task(self, db_session, test_user):
        """Can complete a task."""
        from app.services.secretary_agent.tools.task_tool import create_task, complete_task
        
        # Create a task
        created = create_task(
            title="Task to complete",
            db=db_session,
            user_id=test_user.id,
        )
        
        # Complete it
        result = complete_task(
            task_id=created.task_id,
            db=db_session,
            user_id=test_user.id,
        )
        
        assert result.completed_at
        assert "完成" in result.message
    
    def test_get_overdue_tasks(self, db_session, test_user):
        """Can get overdue tasks."""
        from app.services.secretary_agent.tools.task_tool import create_task, get_overdue_tasks
        
        # Create an overdue task
        yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M")
        create_task(
            title="Overdue task",
            due_date=yesterday,
            db=db_session,
            user_id=test_user.id,
        )
        
        result = get_overdue_tasks(
            db=db_session,
            user_id=test_user.id,
        )
        
        assert result.overdue_count >= 1


class TestReminderTool:
    """Tests for reminder tools."""
    
    def test_create_reminder_basic(self, db_session, test_user):
        """Can create a basic reminder."""
        from app.services.secretary_agent.tools.reminder_tool import create_reminder
        
        tomorrow = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M")
        
        result = create_reminder(
            title="Test reminder",
            remind_at=tomorrow,
            db=db_session,
            user_id=test_user.id,
        )
        
        assert result.reminder_id
        assert result.title == "Test reminder"
        assert "设置" in result.message
    
    def test_create_reminder_with_repeat(self, db_session, test_user):
        """Can create a repeating reminder."""
        from app.services.secretary_agent.tools.reminder_tool import create_reminder
        
        tomorrow = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M")
        
        result = create_reminder(
            title="Daily reminder",
            remind_at=tomorrow,
            repeat="daily",
            db=db_session,
            user_id=test_user.id,
        )
        
        assert result.repeat == ReminderRepeat.daily.value
    
    def test_list_reminders(self, db_session, test_user):
        """Can list reminders."""
        from app.services.secretary_agent.tools.reminder_tool import create_reminder, list_reminders
        
        # Create some reminders
        for i in range(3):
            future = (datetime.utcnow() + timedelta(hours=i+1)).strftime("%Y-%m-%d %H:%M")
            create_reminder(
                title=f"Reminder {i}",
                remind_at=future,
                db=db_session,
                user_id=test_user.id,
            )
        
        result = list_reminders(
            db=db_session,
            user_id=test_user.id,
        )
        
        assert result.total >= 3
    
    def test_get_upcoming_reminders(self, db_session, test_user):
        """Can get upcoming reminders."""
        from app.services.secretary_agent.tools.reminder_tool import create_reminder, get_upcoming_reminders
        
        # Create a reminder for soon
        soon = (datetime.utcnow() + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M")
        create_reminder(
            title="Upcoming reminder",
            remind_at=soon,
            db=db_session,
            user_id=test_user.id,
        )
        
        result = get_upcoming_reminders(
            within_hours=24,
            db=db_session,
            user_id=test_user.id,
        )
        
        assert result.total >= 1
    
    def test_snooze_reminder(self, db_session, test_user):
        """Can snooze a reminder."""
        from app.services.secretary_agent.tools.reminder_tool import create_reminder, snooze_reminder
        from app.services.reminder_service import ReminderService
        from uuid import UUID
        
        # Create a reminder
        soon = (datetime.utcnow() + timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M")
        created = create_reminder(
            title="Reminder to snooze",
            remind_at=soon,
            db=db_session,
            user_id=test_user.id,
        )
        
        # Mark it as triggered first
        ReminderService.trigger_reminder(
            db=db_session,
            reminder_id=UUID(created.reminder_id),
            user_id=test_user.id,
        )
        
        # Snooze it
        result = snooze_reminder(
            reminder_id=created.reminder_id,
            snooze_minutes=30,
            db=db_session,
            user_id=test_user.id,
        )
        
        assert result.snoozed_until
        assert "延后" in result.message


class TestInvalidInputs:
    """Tests for invalid inputs."""
    
    def test_complete_invalid_task_id(self, db_session, test_user):
        """Complete task with invalid ID returns error."""
        from app.services.secretary_agent.tools.task_tool import complete_task
        
        result = complete_task(
            task_id="not-a-uuid",
            db=db_session,
            user_id=test_user.id,
        )
        
        assert "无效" in result.message
    
    def test_snooze_invalid_reminder_id(self, db_session, test_user):
        """Snooze reminder with invalid ID returns error."""
        from app.services.secretary_agent.tools.reminder_tool import snooze_reminder
        
        result = snooze_reminder(
            reminder_id="not-a-uuid",
            db=db_session,
            user_id=test_user.id,
        )
        
        assert "无效" in result.message
    
    def test_create_reminder_invalid_time(self, db_session, test_user):
        """Create reminder with invalid time format returns error."""
        from app.services.secretary_agent.tools.reminder_tool import create_reminder
        
        result = create_reminder(
            title="Bad reminder",
            remind_at="invalid-time-format",
            db=db_session,
            user_id=test_user.id,
        )
        
        assert "无法解析" in result.message
