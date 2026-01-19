"""
Phase 1 Acceptance Tests: Backend Infrastructure (Celery Setup)

This script runs all acceptance tests for Phase 1 to verify:
- Celery dependencies installation
- Celery app initialization
- Configuration loading
- Database migration
- EmailLog model updates
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))


def test_celery_dependencies():
    """TC-P1-001: Verify Celery dependencies are installed."""
    print("\n" + "=" * 70)
    print("TC-P1-001: Celery Dependencies Installation")
    print("=" * 70)
    
    try:
        import celery
        import redis
        import kombu
        
        print(f"✅ celery: {celery.__version__}")
        print(f"✅ redis: {redis.__version__}")
        print(f"✅ kombu: {kombu.__version__}")
        print("\n✅ TC-P1-001 PASSED: All dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ TC-P1-001 FAILED: {e}")
        return False


def test_celery_app_initialization():
    """TC-P1-002: Verify Celery app initialization."""
    print("\n" + "=" * 70)
    print("TC-P1-002: Celery App Initialization")
    print("=" * 70)
    
    try:
        from app.celery_app import celery_app
        
        # Check app exists
        assert celery_app is not None, "Celery app is None"
        print(f"✅ Celery app instance created: {celery_app.main}")
        
        # Check timezone
        assert celery_app.conf.timezone == "Asia/Shanghai", \
            f"Wrong timezone: {celery_app.conf.timezone}"
        print(f"✅ Timezone configured: {celery_app.conf.timezone}")
        
        # Check broker URL
        assert celery_app.conf.broker_url is not None, "Broker URL not set"
        print(f"✅ Broker URL: {celery_app.conf.broker_url}")
        
        # Check result backend
        assert celery_app.conf.result_backend is not None, "Result backend not set"
        print(f"✅ Result backend: {celery_app.conf.result_backend}")
        
        # Check beat schedule exists
        assert hasattr(celery_app.conf, 'beat_schedule'), "Beat schedule not configured"
        assert 'check-scheduled-emails' in celery_app.conf.beat_schedule, \
            "Scheduled email task not in beat schedule"
        print(f"✅ Beat schedule configured: {list(celery_app.conf.beat_schedule.keys())}")
        
        # Check task routes
        assert celery_app.conf.task_routes is not None, "Task routes not configured"
        print(f"✅ Task routes configured: {len(celery_app.conf.task_routes)} routes")
        
        # Check queue configuration
        if hasattr(celery_app.conf, 'task_queues'):
            queues = celery_app.conf.task_queues
            print(f"✅ Task queues configured: {list(queues.keys())}")
        
        print("\n✅ TC-P1-002 PASSED: Celery app initialized correctly")
        return True
    except Exception as e:
        print(f"❌ TC-P1-002 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_configuration_loading():
    """TC-P1-003: Verify configuration loading."""
    print("\n" + "=" * 70)
    print("TC-P1-003: Configuration Loading")
    print("=" * 70)
    
    try:
        from app.core.config import settings
        
        # Check Celery broker URL
        assert settings.CELERY_BROKER_URL is not None, "CELERY_BROKER_URL not set"
        print(f"✅ CELERY_BROKER_URL: {settings.CELERY_BROKER_URL}")
        
        # Check result backend
        assert settings.CELERY_RESULT_BACKEND is not None, "CELERY_RESULT_BACKEND not set"
        print(f"✅ CELERY_RESULT_BACKEND: {settings.CELERY_RESULT_BACKEND}")
        
        # Check timezone
        assert settings.CELERY_TIMEZONE == "Asia/Shanghai", \
            f"Wrong timezone: {settings.CELERY_TIMEZONE}"
        print(f"✅ CELERY_TIMEZONE: {settings.CELERY_TIMEZONE}")
        
        # Check task time limits
        assert settings.CELERY_TASK_TIME_LIMIT > 0, \
            f"Invalid task time limit: {settings.CELERY_TASK_TIME_LIMIT}"
        print(f"✅ CELERY_TASK_TIME_LIMIT: {settings.CELERY_TASK_TIME_LIMIT}s")
        
        assert settings.CELERY_TASK_SOFT_TIME_LIMIT > 0, \
            f"Invalid soft time limit: {settings.CELERY_TASK_SOFT_TIME_LIMIT}"
        print(f"✅ CELERY_TASK_SOFT_TIME_LIMIT: {settings.CELERY_TASK_SOFT_TIME_LIMIT}s")
        
        # Check worker config
        print(f"✅ CELERY_WORKER_PREFETCH_MULTIPLIER: {settings.CELERY_WORKER_PREFETCH_MULTIPLIER}")
        print(f"✅ CELERY_WORKER_MAX_TASKS_PER_CHILD: {settings.CELERY_WORKER_MAX_TASKS_PER_CHILD}")
        print(f"✅ CELERY_WORKER_CONCURRENCY: {settings.CELERY_WORKER_CONCURRENCY}")
        
        # Check result expiry
        assert settings.CELERY_RESULT_EXPIRES > 0, \
            f"Invalid result expires: {settings.CELERY_RESULT_EXPIRES}"
        print(f"✅ CELERY_RESULT_EXPIRES: {settings.CELERY_RESULT_EXPIRES}s")
        
        print("\n✅ TC-P1-003 PASSED: All configuration loaded correctly")
        return True
    except Exception as e:
        print(f"❌ TC-P1-003 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database_migration():
    """TC-P1-004: Verify database migration."""
    print("\n" + "=" * 70)
    print("TC-P1-004: Database Migration")
    print("=" * 70)
    
    try:
        from app.db.session import SessionLocal
        from sqlalchemy import inspect
        
        db = SessionLocal()
        inspector = inspect(db.bind)
        
        # Check if email_logs table exists
        tables = inspector.get_table_names()
        assert 'email_logs' in tables, "email_logs table not found"
        print(f"✅ email_logs table exists")
        
        # Check if send_type column exists
        columns = {col['name']: col for col in inspector.get_columns('email_logs')}
        assert 'send_type' in columns, "send_type column not found"
        print(f"✅ send_type column exists")
        
        # Verify column type
        send_type_col = columns['send_type']
        print(f"   - Type: {send_type_col['type']}")
        print(f"   - Nullable: {send_type_col['nullable']}")
        
        # Check if index exists
        indexes = inspector.get_indexes('email_logs')
        index_names = [idx['name'] for idx in indexes]
        assert 'ix_email_logs_send_type' in index_names, "send_type index not found"
        print(f"✅ ix_email_logs_send_type index exists")
        
        db.close()
        
        print("\n✅ TC-P1-004 PASSED: Database migration applied correctly")
        return True
    except Exception as e:
        print(f"❌ TC-P1-004 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_email_log_model():
    """TC-P1-005: Verify EmailLog model update."""
    print("\n" + "=" * 70)
    print("TC-P1-005: EmailLog Model Update")
    print("=" * 70)
    
    try:
        from app.models.email_log import (
            EmailLog,
            SEND_TYPE_MANUAL,
            SEND_TYPE_SCHEDULED,
            SEND_TYPE_ADMIN,
        )
        
        # Check constants exist
        assert SEND_TYPE_MANUAL == "manual", f"Wrong SEND_TYPE_MANUAL: {SEND_TYPE_MANUAL}"
        print(f"✅ SEND_TYPE_MANUAL: '{SEND_TYPE_MANUAL}'")
        
        assert SEND_TYPE_SCHEDULED == "scheduled", f"Wrong SEND_TYPE_SCHEDULED: {SEND_TYPE_SCHEDULED}"
        print(f"✅ SEND_TYPE_SCHEDULED: '{SEND_TYPE_SCHEDULED}'")
        
        assert SEND_TYPE_ADMIN == "admin", f"Wrong SEND_TYPE_ADMIN: {SEND_TYPE_ADMIN}"
        print(f"✅ SEND_TYPE_ADMIN: '{SEND_TYPE_ADMIN}'")
        
        # Create test instance
        log = EmailLog(
            user_id=1,
            recipient_email="test@example.com",
            status="sent",
            send_type=SEND_TYPE_SCHEDULED
        )
        
        # Verify field exists and has correct value
        assert hasattr(log, 'send_type'), "EmailLog missing send_type attribute"
        print(f"✅ EmailLog has send_type attribute")
        
        assert log.send_type == "scheduled", f"Wrong send_type value: {log.send_type}"
        print(f"✅ send_type value correct: '{log.send_type}'")
        
        # Check __repr__ includes send_type
        repr_str = repr(log)
        assert 'send_type=' in repr_str, "__repr__ doesn't include send_type"
        print(f"✅ __repr__ includes send_type: {repr_str}")
        
        # Verify all columns
        columns = [c.name for c in EmailLog.__table__.columns]
        expected_columns = [
            'id', 'user_id', 'recommendation_id', 'recipient_email',
            'status', 'send_type', 'sent_at', 'error_message'
        ]
        for col in expected_columns:
            assert col in columns, f"Missing column: {col}"
        print(f"✅ All expected columns present: {columns}")
        
        print("\n✅ TC-P1-005 PASSED: EmailLog model updated correctly")
        return True
    except Exception as e:
        print(f"❌ TC-P1-005 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_base_task_classes():
    """Bonus test: Verify base task classes."""
    print("\n" + "=" * 70)
    print("BONUS: Base Task Classes")
    print("=" * 70)
    
    try:
        from app.tasks.base import DatabaseTask, RetryableTask
        
        # Check DatabaseTask
        assert hasattr(DatabaseTask, 'db'), "DatabaseTask missing db property"
        assert hasattr(DatabaseTask, 'after_return'), "DatabaseTask missing after_return"
        assert hasattr(DatabaseTask, 'on_failure'), "DatabaseTask missing on_failure"
        print(f"✅ DatabaseTask: db property and lifecycle methods exist")
        
        # Check RetryableTask
        assert hasattr(RetryableTask, 'autoretry_for'), "RetryableTask missing autoretry_for"
        assert hasattr(RetryableTask, 'retry_kwargs'), "RetryableTask missing retry_kwargs"
        assert RetryableTask.retry_backoff is True, "RetryableTask retry_backoff not True"
        assert RetryableTask.retry_jitter is True, "RetryableTask retry_jitter not True"
        print(f"✅ RetryableTask: retry configuration exists")
        print(f"   - autoretry_for: {RetryableTask.autoretry_for}")
        print(f"   - retry_kwargs: {RetryableTask.retry_kwargs}")
        print(f"   - retry_backoff_max: {RetryableTask.retry_backoff_max}s")
        
        print("\n✅ BONUS PASSED: Base task classes configured correctly")
        return True
    except Exception as e:
        print(f"❌ BONUS FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all Phase 1 acceptance tests."""
    print("\n" + "=" * 70)
    print("PHASE 1 ACCEPTANCE TESTS")
    print("Backend Infrastructure (Celery Setup)")
    print("=" * 70)
    
    results = {
        "TC-P1-001: Dependencies": test_celery_dependencies(),
        "TC-P1-002: Celery App": test_celery_app_initialization(),
        "TC-P1-003: Configuration": test_configuration_loading(),
        "TC-P1-004: Migration": test_database_migration(),
        "TC-P1-005: EmailLog Model": test_email_log_model(),
        "BONUS: Base Tasks": test_base_task_classes(),
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
        print("\n🎉 ALL PHASE 1 TESTS PASSED! 🎉")
        print("\nPhase 1 is complete and verified.")
        print("Ready to proceed to Phase 2: Backend Service Layer")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        print(f"\n{total - passed} test(s) need attention before proceeding to Phase 2")
        return 1


if __name__ == "__main__":
    sys.exit(main())


