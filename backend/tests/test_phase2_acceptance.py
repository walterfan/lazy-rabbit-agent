"""
Phase 2 Acceptance Tests: Backend Service Layer

This script runs all acceptance tests for Phase 2 to verify:
- ScheduledEmailService created with required methods
- Celery tasks defined and registered  
- Base task classes work correctly
- send_type parameter handling
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))


def test_scheduled_email_service():
    """TC-P2-001: Verify ScheduledEmailService creation."""
    print("\n" + "=" * 70)
    print("TC-P2-001: ScheduledEmailService Creation")
    print("=" * 70)
    
    try:
        from app.services.scheduled_email_service import ScheduledEmailService
        from app.db.session import SessionLocal
        
        db = SessionLocal()
        service = ScheduledEmailService(db)
        
        # Check required methods exist
        assert hasattr(service, 'get_users_for_hour'), "Missing get_users_for_hour method"
        assert callable(service.get_users_for_hour), "get_users_for_hour not callable"
        print(f"✅ get_users_for_hour method exists")
        
        assert hasattr(service, 'send_scheduled_email'), "Missing send_scheduled_email method"
        assert callable(service.send_scheduled_email), "send_scheduled_email not callable"
        print(f"✅ send_scheduled_email method exists")
        
        assert hasattr(service, 'queue_emails_for_hour'), "Missing queue_emails_for_hour method"
        assert callable(service.queue_emails_for_hour), "queue_emails_for_hour not callable"
        print(f"✅ queue_emails_for_hour method exists")
        
        # Check service has required dependencies
        assert hasattr(service, 'db'), "Missing db attribute"
        assert hasattr(service, 'recommendation_service'), "Missing recommendation_service"
        assert hasattr(service, 'email_service'), "Missing email_service"
        assert hasattr(service, 'template_service'), "Missing template_service"
        print(f"✅ All service dependencies initialized")
        
        db.close()
        
        print("\n✅ TC-P2-001 PASSED: ScheduledEmailService created successfully")
        return True
    except Exception as e:
        print(f"❌ TC-P2-001 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_celery_tasks_registration():
    """TC-P2-002: Verify Celery tasks are registered."""
    print("\n" + "=" * 70)
    print("TC-P2-002: Celery Tasks Registration")
    print("=" * 70)
    
    try:
        from app.celery_app import celery_app
        from app.tasks.scheduled_emails import (
            check_and_send_scheduled_emails,
            send_scheduled_email_task,
        )
        
        # Check tasks are defined
        assert check_and_send_scheduled_emails is not None, "check_and_send_scheduled_emails is None"
        print(f"✅ check_and_send_scheduled_emails task defined")
        
        assert send_scheduled_email_task is not None, "send_scheduled_email_task is None"
        print(f"✅ send_scheduled_email_task task defined")
        
        # Check task names
        assert check_and_send_scheduled_emails.name == "app.tasks.scheduled_emails.check_and_send_scheduled_emails"
        print(f"✅ check_and_send_scheduled_emails name: {check_and_send_scheduled_emails.name}")
        
        assert send_scheduled_email_task.name == "app.tasks.scheduled_emails.send_scheduled_email_task"
        print(f"✅ send_scheduled_email_task name: {send_scheduled_email_task.name}")
        
        # Check tasks use RetryableTask base
        from app.tasks.base import RetryableTask
        # Check if task has retry configuration
        assert hasattr(send_scheduled_email_task, 'autoretry_for'), "Task missing retry config"
        print(f"✅ Tasks have retry configuration")
        
        # Check tasks are registered in celery app
        registered_tasks = list(celery_app.tasks.keys())
        assert check_and_send_scheduled_emails.name in registered_tasks, \
            f"check_and_send_scheduled_emails not registered. Registered: {registered_tasks}"
        assert send_scheduled_email_task.name in registered_tasks, \
            f"send_scheduled_email_task not registered"
        print(f"✅ Tasks registered in Celery app")
        print(f"   Total registered tasks: {len(registered_tasks)}")
        
        print("\n✅ TC-P2-002 PASSED: Celery tasks registered successfully")
        return True
    except Exception as e:
        print(f"❌ TC-P2-002 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_task_imports():
    """TC-P2-003: Verify tasks can be imported."""
    print("\n" + "=" * 70)
    print("TC-P2-003: Task Imports")
    print("=" * 70)
    
    try:
        # Test importing from tasks package
        from app.tasks import scheduled_emails
        print(f"✅ app.tasks.scheduled_emails module imported")
        
        # Test importing specific tasks
        from app.tasks.scheduled_emails import check_and_send_scheduled_emails
        from app.tasks.scheduled_emails import send_scheduled_email_task
        print(f"✅ Individual tasks imported")
        
        # Test importing base classes
        from app.tasks.base import DatabaseTask, RetryableTask
        print(f"✅ Base task classes imported")
        
        print("\n✅ TC-P2-003 PASSED: All imports successful")
        return True
    except Exception as e:
        print(f"❌ TC-P2-003 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_send_type_constants():
    """TC-P2-004: Verify send_type constants are used correctly."""
    print("\n" + "=" * 70)
    print("TC-P2-004: Send Type Constants")
    print("=" * 70)
    
    try:
        from app.models.email_log import (
            SEND_TYPE_MANUAL,
            SEND_TYPE_SCHEDULED,
            SEND_TYPE_ADMIN,
        )
        
        # Check constants
        assert SEND_TYPE_MANUAL == "manual", f"Wrong SEND_TYPE_MANUAL: {SEND_TYPE_MANUAL}"
        assert SEND_TYPE_SCHEDULED == "scheduled", f"Wrong SEND_TYPE_SCHEDULED: {SEND_TYPE_SCHEDULED}"
        assert SEND_TYPE_ADMIN == "admin", f"Wrong SEND_TYPE_ADMIN: {SEND_TYPE_ADMIN}"
        print(f"✅ Send type constants defined correctly")
        
        # Check ScheduledEmailService uses SEND_TYPE_SCHEDULED
        import inspect
        from app.services.scheduled_email_service import ScheduledEmailService
        
        source = inspect.getsource(ScheduledEmailService.send_scheduled_email)
        assert 'SEND_TYPE_SCHEDULED' in source, "ScheduledEmailService doesn't use SEND_TYPE_SCHEDULED"
        print(f"✅ ScheduledEmailService uses SEND_TYPE_SCHEDULED")
        
        # Check emails endpoint uses SEND_TYPE_MANUAL
        from app.api.v1.endpoints import emails
        source = inspect.getsource(emails)
        assert 'SEND_TYPE_MANUAL' in source, "emails endpoint doesn't use SEND_TYPE_MANUAL"
        print(f"✅ emails endpoint uses SEND_TYPE_MANUAL")
        
        print("\n✅ TC-P2-004 PASSED: send_type constants used correctly")
        return True
    except Exception as e:
        print(f"❌ TC-P2-004 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_beat_schedule():
    """TC-P2-005: Verify beat schedule is configured."""
    print("\n" + "=" * 70)
    print("TC-P2-005: Beat Schedule Configuration")
    print("=" * 70)
    
    try:
        from app.celery_app import celery_app
        
        # Check beat schedule exists
        beat_schedule = celery_app.conf.beat_schedule
        assert beat_schedule is not None, "Beat schedule not configured"
        print(f"✅ Beat schedule configured")
        
        # Check check-scheduled-emails task is in schedule
        assert 'check-scheduled-emails' in beat_schedule, \
            f"check-scheduled-emails not in beat schedule. Schedule: {list(beat_schedule.keys())}"
        print(f"✅ check-scheduled-emails in beat schedule")
        
        # Check schedule details
        schedule_config = beat_schedule['check-scheduled-emails']
        assert 'task' in schedule_config, "Schedule missing task name"
        assert schedule_config['task'] == 'app.tasks.scheduled_emails.check_and_send_scheduled_emails', \
            f"Wrong task in schedule: {schedule_config['task']}"
        print(f"✅ Task name: {schedule_config['task']}")
        
        assert 'schedule' in schedule_config, "Schedule missing crontab"
        print(f"✅ Schedule: {schedule_config['schedule']}")
        
        if 'options' in schedule_config:
            print(f"✅ Options: {schedule_config['options']}")
        
        print("\n✅ TC-P2-005 PASSED: Beat schedule configured correctly")
        return True
    except Exception as e:
        print(f"❌ TC-P2-005 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_users_for_hour():
    """TC-P2-006: Test get_users_for_hour method."""
    print("\n" + "=" * 70)
    print("TC-P2-006: Get Users For Hour Method")
    print("=" * 70)
    
    try:
        from app.services.scheduled_email_service import ScheduledEmailService
        from app.db.session import SessionLocal
        
        db = SessionLocal()
        service = ScheduledEmailService(db)
        
        # Test with current hour (should work even if no users)
        from datetime import datetime
        current_hour = datetime.now().hour
        
        users = service.get_users_for_hour(current_hour)
        assert isinstance(users, list), f"get_users_for_hour didn't return list: {type(users)}"
        print(f"✅ get_users_for_hour({current_hour}) returned list with {len(users)} users")
        
        # Test with different hour
        users = service.get_users_for_hour(8)
        assert isinstance(users, list), "get_users_for_hour(8) didn't return list"
        print(f"✅ get_users_for_hour(8) returned list with {len(users)} users")
        
        db.close()
        
        print("\n✅ TC-P2-006 PASSED: get_users_for_hour works correctly")
        return True
    except Exception as e:
        print(f"❌ TC-P2-006 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all Phase 2 acceptance tests."""
    print("\n" + "=" * 70)
    print("PHASE 2 ACCEPTANCE TESTS")
    print("Backend Service Layer")
    print("=" * 70)
    
    results = {
        "TC-P2-001: ScheduledEmailService": test_scheduled_email_service(),
        "TC-P2-002: Task Registration": test_celery_tasks_registration(),
        "TC-P2-003: Task Imports": test_task_imports(),
        "TC-P2-004: Send Type Constants": test_send_type_constants(),
        "TC-P2-005: Beat Schedule": test_beat_schedule(),
        "TC-P2-006: Get Users For Hour": test_get_users_for_hour(),
    }
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print("\n" + "-" * 70)
    print(f"Total: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL PHASE 2 TESTS PASSED! 🎉")
        print("\nPhase 2 is complete and verified.")
        print("Ready to proceed to Phase 3: Backend API Endpoints")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        print(f"\n{total - passed} test(s) need attention before proceeding to Phase 3")
        return 1


if __name__ == "__main__":
    sys.exit(main())


