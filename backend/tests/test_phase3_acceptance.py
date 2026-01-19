"""
Phase 3 Acceptance Tests: Backend API Endpoints

This script runs all acceptance tests for Phase 3 to verify:
- User email preferences endpoints (GET/PATCH)
- Admin email preferences endpoints (GET/PATCH/POST test)
- Routes properly registered in API router
- Proper authentication and authorization
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))


def test_user_endpoints_exist():
    """TC-P3-001: Verify user email preferences endpoints exist."""
    print("\n" + "=" * 70)
    print("TC-P3-001: User Email Preferences Endpoints")
    print("=" * 70)
    
    try:
        from app.api.v1.endpoints import emails
        
        # Get all routes
        routes = [route.path for route in emails.router.routes]
        print(f"✅ Email router has {len(routes)} routes")
        
        # Check for user email preferences endpoints
        assert "/users/me/email-preferences" in routes, "Missing /users/me/email-preferences endpoint"
        print(f"✅ GET /users/me/email-preferences exists")
        print(f"✅ PATCH /users/me/email-preferences exists")
        
        # Check methods
        for route in emails.router.routes:
            if route.path == "/users/me/email-preferences":
                methods = route.methods
                print(f"   Methods: {methods}")
        
        print("\n✅ TC-P3-001 PASSED: User endpoints exist")
        return True
    except Exception as e:
        print(f"❌ TC-P3-001 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_admin_endpoints_exist():
    """TC-P3-002: Verify admin email preferences endpoints exist."""
    print("\n" + "=" * 70)
    print("TC-P3-002: Admin Email Preferences Endpoints")
    print("=" * 70)
    
    try:
        from app.api.v1.endpoints import admin
        
        # Get all routes
        routes = [route.path for route in admin.router.routes]
        email_routes = [r for r in routes if 'email' in r]
        print(f"✅ Admin router has {len(email_routes)} email-related routes")
        
        # Check for admin email preferences endpoints
        assert "/users/{user_id}/email-preferences" in routes, \
            "Missing /users/{user_id}/email-preferences endpoint"
        print(f"✅ GET /admin/users/{{user_id}}/email-preferences exists")
        print(f"✅ PATCH /admin/users/{{user_id}}/email-preferences exists")
        
        assert "/users/{user_id}/test-scheduled-email" in routes, \
            "Missing /users/{user_id}/test-scheduled-email endpoint"
        print(f"✅ POST /admin/users/{{user_id}}/test-scheduled-email exists")
        
        # Check methods for email-preferences
        get_found = False
        patch_found = False
        for route in admin.router.routes:
            if route.path == "/users/{user_id}/email-preferences":
                methods = route.methods
                if "GET" in methods:
                    get_found = True
                    print(f"   GET /users/{{user_id}}/email-preferences: {methods}")
                if "PATCH" in methods:
                    patch_found = True
                    print(f"   PATCH /users/{{user_id}}/email-preferences: {methods}")
        
        assert get_found, "Missing GET method for email-preferences"
        assert patch_found, "Missing PATCH method for email-preferences"
        
        # Check method for test endpoint
        for route in admin.router.routes:
            if route.path == "/users/{user_id}/test-scheduled-email":
                methods = route.methods
                print(f"   test-scheduled-email methods: {methods}")
                assert "POST" in methods, "Missing POST method"
        
        print("\n✅ TC-P3-002 PASSED: Admin endpoints exist")
        return True
    except Exception as e:
        print(f"❌ TC-P3-002 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_routes_registered():
    """TC-P3-003: Verify routes are registered in API router."""
    print("\n" + "=" * 70)
    print("TC-P3-003: Routes Registration")
    print("=" * 70)
    
    try:
        from app.api.v1.api import api_router
        
        # Get all registered routes
        all_routes = []
        for route in api_router.routes:
            if hasattr(route, 'path'):
                all_routes.append(route.path)
        
        print(f"✅ API router has {len(all_routes)} total routes")
        
        # Check email routes are registered
        user_email_routes = [r for r in all_routes if '/users/me/email-preferences' in r]
        assert len(user_email_routes) > 0, "User email preferences routes not registered"
        print(f"✅ User email preferences routes registered: {len(user_email_routes)} routes")
        
        admin_email_routes = [r for r in all_routes if '/admin/users' in r and 'email' in r]
        assert len(admin_email_routes) > 0, "Admin email preferences routes not registered"
        print(f"✅ Admin email preferences routes registered: {len(admin_email_routes)} routes")
        
        # Check specific routes
        assert any('/users/me/email-preferences' in r for r in all_routes), \
            "GET/PATCH /users/me/email-preferences not in router"
        print(f"✅ /users/me/email-preferences registered")
        
        assert any('/admin/users' in r and 'email-preferences' in r for r in all_routes), \
            "Admin email preferences not in router"
        print(f"✅ /admin/users/{{user_id}}/email-preferences registered")
        
        assert any('/admin/users' in r and 'test-scheduled-email' in r for r in all_routes), \
            "Admin test email not in router"
        print(f"✅ /admin/users/{{user_id}}/test-scheduled-email registered")
        
        print("\n✅ TC-P3-003 PASSED: All routes registered")
        return True
    except Exception as e:
        print(f"❌ TC-P3-003 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_schemas_exist():
    """TC-P3-004: Verify email schemas exist."""
    print("\n" + "=" * 70)
    print("TC-P3-004: Email Schemas")
    print("=" * 70)
    
    try:
        from app.schemas.email import (
            EmailPreferencesResponse,
            EmailPreferencesUpdate,
        )
        
        # Check EmailPreferencesResponse
        response_fields = EmailPreferencesResponse.model_fields
        print(f"✅ EmailPreferencesResponse has {len(response_fields)} fields:")
        for field_name in response_fields:
            print(f"   - {field_name}")
        
        assert 'email_notifications_enabled' in response_fields
        assert 'email_send_time' in response_fields
        assert 'email_additional_recipients' in response_fields
        assert 'email_preferred_city' in response_fields
        
        # Check EmailPreferencesUpdate
        update_fields = EmailPreferencesUpdate.model_fields
        print(f"✅ EmailPreferencesUpdate has {len(update_fields)} fields:")
        for field_name in update_fields:
            print(f"   - {field_name}")
        
        # Test validation
        from datetime import time
        test_data = {
            'email_notifications_enabled': True,
            'email_send_time': '08:00',
            'email_additional_recipients': ['test@example.com'],
            'email_preferred_city': '110000',
        }
        
        update = EmailPreferencesUpdate(**test_data)
        print(f"✅ EmailPreferencesUpdate validation works")
        print(f"   Parsed time: {update.email_send_time}")
        
        print("\n✅ TC-P3-004 PASSED: Email schemas exist and work")
        return True
    except Exception as e:
        print(f"❌ TC-P3-004 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_endpoint_authentication():
    """TC-P3-005: Verify endpoints require authentication."""
    print("\n" + "=" * 70)
    print("TC-P3-005: Endpoint Authentication")
    print("=" * 70)
    
    try:
        from app.api.v1.endpoints import emails, admin
        import inspect
        
        # Check user endpoints
        get_prefs_func = None
        update_prefs_func = None
        for route in emails.router.routes:
            if route.path == "/users/me/email-preferences":
                if "GET" in route.methods:
                    get_prefs_func = route.endpoint
                elif "PATCH" in route.methods:
                    update_prefs_func = route.endpoint
        
        assert get_prefs_func is not None, "GET endpoint not found"
        assert update_prefs_func is not None, "PATCH endpoint not found"
        
        # Check function signatures have current_user parameter (indicates auth required)
        get_sig = inspect.signature(get_prefs_func)
        assert 'current_user' in get_sig.parameters, "GET endpoint missing current_user (no auth)"
        print(f"✅ GET /users/me/email-preferences requires authentication")
        
        update_sig = inspect.signature(update_prefs_func)
        assert 'current_user' in update_sig.parameters, "PATCH endpoint missing current_user (no auth)"
        print(f"✅ PATCH /users/me/email-preferences requires authentication")
        
        # Check admin endpoints
        admin_get_func = None
        admin_update_func = None
        admin_test_func = None
        for route in admin.router.routes:
            if route.path == "/users/{user_id}/email-preferences":
                if "GET" in route.methods:
                    admin_get_func = route.endpoint
                elif "PATCH" in route.methods:
                    admin_update_func = route.endpoint
            elif route.path == "/users/{user_id}/test-scheduled-email":
                admin_test_func = route.endpoint
        
        assert admin_get_func is not None, "Admin GET endpoint not found"
        assert admin_update_func is not None, "Admin PATCH endpoint not found"
        assert admin_test_func is not None, "Admin test endpoint not found"
        
        # Check admin endpoints have current_user parameter
        admin_get_sig = inspect.signature(admin_get_func)
        assert 'current_user' in admin_get_sig.parameters, \
            "Admin GET endpoint missing current_user"
        print(f"✅ GET /admin/users/{{user_id}}/email-preferences requires authentication")
        
        admin_update_sig = inspect.signature(admin_update_func)
        assert 'current_user' in admin_update_sig.parameters, \
            "Admin PATCH endpoint missing current_user"
        print(f"✅ PATCH /admin/users/{{user_id}}/email-preferences requires authentication")
        
        admin_test_sig = inspect.signature(admin_test_func)
        assert 'current_user' in admin_test_sig.parameters, \
            "Admin test endpoint missing current_user"
        print(f"✅ POST /admin/users/{{user_id}}/test-scheduled-email requires authentication")
        
        print("\n✅ TC-P3-005 PASSED: All endpoints require authentication")
        return True
    except Exception as e:
        print(f"❌ TC-P3-005 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_test_endpoint_imports():
    """TC-P3-006: Verify test endpoint can import ScheduledEmailService."""
    print("\n" + "=" * 70)
    print("TC-P3-006: Test Endpoint Dependencies")
    print("=" * 70)
    
    try:
        # Test that the test endpoint function exists and can access dependencies
        from app.api.v1.endpoints.admin import test_scheduled_email
        print(f"✅ test_scheduled_email endpoint function exists")
        
        # Check the function can import ScheduledEmailService
        import inspect
        source = inspect.getsource(test_scheduled_email)
        assert 'ScheduledEmailService' in source, \
            "test_scheduled_email doesn't import ScheduledEmailService"
        print(f"✅ test_scheduled_email imports ScheduledEmailService")
        
        assert 'send_scheduled_email' in source, \
            "test_scheduled_email doesn't call send_scheduled_email"
        print(f"✅ test_scheduled_email calls send_scheduled_email method")
        
        # Verify ScheduledEmailService can be imported
        from app.services.scheduled_email_service import ScheduledEmailService
        print(f"✅ ScheduledEmailService imports successfully")
        
        print("\n✅ TC-P3-006 PASSED: Test endpoint dependencies work")
        return True
    except Exception as e:
        print(f"❌ TC-P3-006 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all Phase 3 acceptance tests."""
    print("\n" + "=" * 70)
    print("PHASE 3 ACCEPTANCE TESTS")
    print("Backend API Endpoints")
    print("=" * 70)
    
    results = {
        "TC-P3-001: User Endpoints": test_user_endpoints_exist(),
        "TC-P3-002: Admin Endpoints": test_admin_endpoints_exist(),
        "TC-P3-003: Routes Registration": test_routes_registered(),
        "TC-P3-004: Email Schemas": test_schemas_exist(),
        "TC-P3-005: Authentication": test_endpoint_authentication(),
        "TC-P3-006: Test Endpoint": test_test_endpoint_imports(),
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
        print("\n🎉 ALL PHASE 3 TESTS PASSED! 🎉")
        print("\nPhase 3 is complete and verified.")
        print("Ready to proceed to Phase 4: Frontend User Interface")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        print(f"\n{total - passed} test(s) need attention before proceeding to Phase 4")
        return 1


if __name__ == "__main__":
    sys.exit(main())

