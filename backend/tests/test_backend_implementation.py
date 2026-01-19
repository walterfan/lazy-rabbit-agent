#!/usr/bin/env python3
"""
Backend Implementation Validation Script
Tests the admin multi-day recommendations implementation without requiring runtime dependencies.
"""

import os
import sys
import ast
import re
from pathlib import Path

# Change to backend directory
os.chdir(Path(__file__).parent)
sys.path.insert(0, '.')

class BackendValidator:
    """Validates backend implementation changes."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
    
    def test(self, name, condition, error_msg=""):
        """Run a test and track results."""
        if condition:
            print(f"   ✅ {name}")
            self.passed += 1
            return True
        else:
            print(f"   ❌ {name}")
            if error_msg:
                print(f"      {error_msg}")
            self.failed += 1
            return False
    
    def warn(self, name, message=""):
        """Log a warning."""
        print(f"   ⚠️  {name}")
        if message:
            print(f"      {message}")
        self.warnings += 1
    
    def section(self, title):
        """Print section header."""
        print(f"\n📝 {title}")
        print("   " + "-" * 60)
    
    def validate_file_exists(self, filepath):
        """Check if a file exists."""
        return os.path.exists(filepath)
    
    def validate_file_contains(self, filepath, patterns):
        """Check if file contains all patterns."""
        if not self.validate_file_exists(filepath):
            return False
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        for pattern in patterns:
            if pattern not in content:
                return False
        return True
    
    def validate_python_syntax(self, filepath):
        """Check if Python file has valid syntax."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                ast.parse(f.read())
            return True
        except SyntaxError as e:
            print(f"      Syntax error at line {e.lineno}: {e.msg}")
            return False
    
    def run(self):
        """Run all validation tests."""
        print("\n" + "=" * 70)
        print("🧪 Backend Implementation Validation")
        print("=" * 70)
        
        # Test 1: Database Models
        self.section("Test 1: Database Models & Migration")
        
        model_file = "app/models/recommendation.py"
        self.test(
            "Recommendation model file exists",
            self.validate_file_exists(model_file)
        )
        self.test(
            "Recommendation model has forecast_date field",
            self.validate_file_contains(model_file, ["forecast_date", "Column(Date"])
        )
        self.test(
            "Recommendation model imports Date type",
            self.validate_file_contains(model_file, ["from datetime import", "date"])
        )
        
        migration_file = "alembic/versions/5d5f13a21dbc_add_forecast_date_to_recommendations.py"
        self.test(
            "Migration file exists",
            self.validate_file_exists(migration_file)
        )
        self.test(
            "Migration adds forecast_date column",
            self.validate_file_contains(migration_file, ["add_column", "forecast_date", "sa.Date()"])
        )
        self.test(
            "Migration creates composite index",
            self.validate_file_contains(migration_file, [
                "create_index",
                "ix_recommendations_user_forecast_created",
                "user_id",
                "forecast_date",
                "created_at"
            ])
        )
        
        # Test 2: Weather Service
        self.section("Test 2: Weather Service Enhancement")
        
        weather_helper = "app/services/weather/weather_helper.py"
        self.test(
            "WeatherHelper service file exists",
            self.validate_file_exists(weather_helper)
        )
        self.test(
            "WeatherHelper has valid Python syntax",
            self.validate_python_syntax(weather_helper)
        )
        self.test(
            "WeatherHelper has get_forecast() method",
            self.validate_file_contains(weather_helper, ["def get_forecast(", "city_code", "days"])
        )
        self.test(
            "WeatherHelper has get_date_label() method",
            self.validate_file_contains(weather_helper, ["def get_date_label(", "day_offset"])
        )
        self.test(
            "WeatherHelper implements caching",
            self.validate_file_contains(weather_helper, ["cache_key", "self.cache.get", "self.cache.set"])
        )
        self.test(
            "WeatherHelper returns date labels (今天, 明天, 后天)",
            self.validate_file_contains(weather_helper, ["今天", "明天", "后天"])
        )
        
        # Test 3: Recommendation Service
        self.section("Test 3: Recommendation Service Enhancement")
        
        rec_service = "app/services/recommendation_service.py"
        self.test(
            "RecommendationService has generate_for_user_multi_day() method",
            self.validate_file_contains(rec_service, [
                "def generate_for_user_multi_day(",
                "target_user",
                "city_code",
                "days"
            ])
        )
        self.test(
            "RecommendationService imports WeatherHelper",
            self.validate_file_contains(rec_service, ["from app.services.weather.weather_helper import WeatherHelper"])
        )
        self.test(
            "RecommendationService has _build_multi_day_prompt() method",
            self.validate_file_contains(rec_service, [
                "def _build_multi_day_prompt(",
                "forecast",
                "date_label"
            ])
        )
        self.test(
            "RecommendationService stores forecast_date",
            self.validate_file_contains(rec_service, ["forecast_date=forecast_date"])
        )
        self.test(
            "RecommendationService has cost logging",
            self.validate_file_contains(rec_service, ["CostLog", "estimated_cost"])
        )
        
        # Test 4: Schemas
        self.section("Test 4: Backend Schemas")
        
        schemas_file = "app/schemas/recommendation.py"
        self.test(
            "Schemas file has AdminGenerateMultiDayRequest",
            self.validate_file_contains(schemas_file, [
                "class AdminGenerateMultiDayRequest",
                "user_id",
                "city_code",
                "send_email"
            ])
        )
        self.test(
            "Schemas file has DailyRecommendation",
            self.validate_file_contains(schemas_file, [
                "class DailyRecommendation",
                "date",
                "date_label",
                "recommendation",
                "weather_summary"
            ])
        )
        self.test(
            "Schemas file has MultiDayRecommendationResponse",
            self.validate_file_contains(schemas_file, [
                "class MultiDayRecommendationResponse",
                "recommendations",
                "email_sent",
                "generated_at"
            ])
        )
        self.test(
            "Schemas file has UserBasicInfo",
            self.validate_file_contains(schemas_file, [
                "class UserBasicInfo",
                "email",
                "full_name"
            ])
        )
        
        # Test 5: RBAC Permission
        self.section("Test 5: RBAC Permission")
        
        seed_script = "app/scripts/seed_rbac.py"
        self.test(
            "Seed script includes recommendation.admin permission",
            self.validate_file_contains(seed_script, [
                "recommendation.admin",
                "resource\": \"recommendation\"",
                "action\": \"admin\""
            ])
        )
        self.test(
            "Super Administrator role has recommendation.admin",
            self.validate_file_contains(seed_script, [
                "Super Administrator",
                "recommendation.admin"
            ])
        )
        self.test(
            "Administrator role has recommendation.admin",
            self.validate_file_contains(seed_script, [
                "Administrator",
                "recommendation.admin"
            ])
        )
        
        # Test 6: API Endpoints
        self.section("Test 6: API Endpoints")
        
        admin_api = "app/api/v1/endpoints/admin_recommendations.py"
        self.test(
            "Admin recommendations endpoint file exists",
            self.validate_file_exists(admin_api)
        )
        self.test(
            "Admin endpoint has valid Python syntax",
            self.validate_python_syntax(admin_api)
        )
        self.test(
            "Admin endpoint has generate_multi_day_recommendation_for_user function",
            self.validate_file_contains(admin_api, [
                "def generate_multi_day_recommendation_for_user(",
                "AdminGenerateMultiDayRequest"
            ])
        )
        self.test(
            "Admin endpoint uses require_permission('recommendation.admin')",
            self.validate_file_contains(admin_api, [
                "require_permission",
                "recommendation.admin"
            ])
        )
        self.test(
            "Admin endpoint handles email sending",
            self.validate_file_contains(admin_api, [
                "send_email",
                "send_multi_day_recommendation"
            ])
        )
        self.test(
            "Admin endpoint has error handling",
            self.validate_file_contains(admin_api, [
                "HTTPException",
                "status.HTTP_404_NOT_FOUND",
                "status.HTTP_400_BAD_REQUEST"
            ])
        )
        
        api_file = "app/api/v1/api.py"
        self.test(
            "Admin recommendations router registered in API",
            self.validate_file_contains(api_file, [
                "admin_recommendations",
                "admin/recommendations"
            ])
        )
        
        # Test 7: Email Service
        self.section("Test 7: Email Service Enhancement")
        
        email_service = "app/services/email_service.py"
        self.test(
            "EmailService has send_multi_day_recommendation() method",
            self.validate_file_contains(email_service, [
                "def send_multi_day_recommendation(",
                "recommendations",
                "render_multi_day_recommendation_email"
            ])
        )
        
        template_service = "app/services/email_template_service.py"
        self.test(
            "EmailTemplateService has render_multi_day_recommendation_email() method",
            self.validate_file_contains(template_service, [
                "def render_multi_day_recommendation_email(",
                "daily_recommendations"
            ])
        )
        
        email_template = "app/templates/emails/recommendation_multi_day.html"
        self.test(
            "Multi-day email template exists",
            self.validate_file_exists(email_template)
        )
        self.test(
            "Email template has multi-day structure",
            self.validate_file_contains(email_template, [
                "未来三天",
                "daily_recommendations",
                "date_label"
            ])
        )
        self.test(
            "Email template is responsive",
            self.validate_file_contains(email_template, [
                "@media",
                "max-width",
                "container"
            ])
        )
        
        # Print summary
        self.section("Test Summary")
        total = self.passed + self.failed
        success_rate = (self.passed / total * 100) if total > 0 else 0
        
        print(f"\n   📊 Results:")
        print(f"      ✅ Passed:   {self.passed}/{total}")
        print(f"      ❌ Failed:   {self.failed}/{total}")
        print(f"      ⚠️  Warnings: {self.warnings}")
        print(f"      📈 Success:  {success_rate:.1f}%")
        
        print("\n" + "=" * 70)
        
        if self.failed == 0:
            print("✅ ALL TESTS PASSED! Backend implementation is complete.")
        else:
            print(f"❌ {self.failed} test(s) failed. Please review the issues above.")
        
        print("=" * 70 + "\n")
        
        return self.failed == 0


if __name__ == "__main__":
    validator = BackendValidator()
    success = validator.run()
    sys.exit(0 if success else 1)

