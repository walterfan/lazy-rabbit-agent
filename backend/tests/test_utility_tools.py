"""
Tests for utility tools (calculator, datetime, weather).
"""

import pytest
from datetime import datetime
from zoneinfo import ZoneInfo

from app.services.secretary_agent.tools.calculator_tool import (
    calculate,
    safe_eval,
    CalculatorResponse,
)
from app.services.secretary_agent.tools.datetime_tool import (
    get_current_datetime,
    DateTimeResponse,
    WEEKDAY_CHINESE,
)


class TestCalculatorTool:
    """Tests for the calculator tool."""
    
    def test_basic_addition(self):
        """Calculator handles basic addition."""
        result = calculate("2 + 3")
        
        assert result.result == 5
        assert "5" in result.formatted
    
    def test_basic_subtraction(self):
        """Calculator handles basic subtraction."""
        result = calculate("10 - 4")
        
        assert result.result == 6
    
    def test_multiplication(self):
        """Calculator handles multiplication."""
        result = calculate("3 * 4")
        
        assert result.result == 12
    
    def test_division(self):
        """Calculator handles division."""
        result = calculate("15 / 3")
        
        assert result.result == 5.0
    
    def test_order_of_operations(self):
        """Calculator respects order of operations."""
        result = calculate("2 + 3 * 4")
        
        assert result.result == 14  # Not 20
    
    def test_parentheses(self):
        """Calculator handles parentheses."""
        result = calculate("(2 + 3) * 4")
        
        assert result.result == 20
    
    def test_power(self):
        """Calculator handles exponentiation."""
        result = calculate("2 ** 3")
        
        assert result.result == 8
    
    def test_sqrt_function(self):
        """Calculator handles sqrt function."""
        result = calculate("sqrt(16)")
        
        assert result.result == 4.0
    
    def test_sin_function(self):
        """Calculator handles sin function."""
        result = calculate("sin(0)")
        
        assert abs(result.result) < 0.0001
    
    def test_cos_function(self):
        """Calculator handles cos function."""
        result = calculate("cos(0)")
        
        assert abs(result.result - 1.0) < 0.0001
    
    def test_log_function(self):
        """Calculator handles log function."""
        import math
        result = calculate("log(10)")
        
        assert abs(result.result - math.log(10)) < 0.0001
    
    def test_pi_constant(self):
        """Calculator handles pi constant."""
        import math
        result = calculate("pi")
        
        assert abs(result.result - math.pi) < 0.0001
    
    def test_e_constant(self):
        """Calculator handles e constant."""
        import math
        result = calculate("e")
        
        assert abs(result.result - math.e) < 0.0001
    
    def test_floor_function(self):
        """Calculator handles floor function."""
        result = calculate("floor(3.7)")
        
        assert result.result == 3
    
    def test_ceil_function(self):
        """Calculator handles ceil function."""
        result = calculate("ceil(3.2)")
        
        assert result.result == 4
    
    def test_negative_numbers(self):
        """Calculator handles negative numbers."""
        result = calculate("-5 + 3")
        
        assert result.result == -2
    
    def test_division_by_zero(self):
        """Calculator handles division by zero gracefully."""
        result = calculate("1 / 0")
        
        assert result.result == "Error"
        assert "零" in result.formatted or "zero" in result.formatted.lower()
    
    def test_invalid_expression(self):
        """Calculator handles invalid expressions gracefully."""
        result = calculate("2 +")
        
        assert result.result == "Error"
    
    def test_disallowed_function(self):
        """Calculator rejects disallowed functions."""
        result = calculate("eval('1+1')")
        
        assert result.result == "Error"
    
    def test_complex_expression(self):
        """Calculator handles complex expressions."""
        result = calculate("sqrt(16) + 2 * 3 - 1")
        
        assert result.result == 9.0  # 4 + 6 - 1


class TestSafeEval:
    """Tests for safe_eval function."""
    
    def test_safe_eval_basic(self):
        """safe_eval evaluates basic expressions."""
        assert safe_eval("1 + 1") == 2
        assert safe_eval("10 * 5") == 50
    
    def test_safe_eval_rejects_code(self):
        """safe_eval rejects code execution attempts."""
        with pytest.raises(ValueError):
            safe_eval("__import__('os').system('ls')")
    
    def test_safe_eval_rejects_attribute_access(self):
        """safe_eval rejects attribute access."""
        with pytest.raises(ValueError):
            safe_eval("().__class__")


class TestDateTimeTool:
    """Tests for the datetime tool."""
    
    def test_get_current_datetime_default_timezone(self):
        """get_current_datetime returns current time in default timezone."""
        result = get_current_datetime()
        
        assert isinstance(result, DateTimeResponse)
        assert result.timezone == "Asia/Shanghai"
        assert result.unix_timestamp > 0
    
    def test_get_current_datetime_utc(self):
        """get_current_datetime handles UTC timezone."""
        result = get_current_datetime(timezone="UTC")
        
        assert result.timezone == "UTC"
    
    def test_get_current_datetime_new_york(self):
        """get_current_datetime handles America/New_York timezone."""
        result = get_current_datetime(timezone="America/New_York")
        
        assert result.timezone == "America/New_York"
    
    def test_get_current_datetime_invalid_timezone(self):
        """get_current_datetime falls back to UTC for invalid timezone."""
        result = get_current_datetime(timezone="Invalid/Timezone")
        
        assert result.timezone == "UTC"
    
    def test_get_current_datetime_date_format(self):
        """get_current_datetime returns date in YYYY-MM-DD format."""
        result = get_current_datetime()
        
        # Validate date format
        parts = result.date.split("-")
        assert len(parts) == 3
        assert len(parts[0]) == 4  # Year
        assert len(parts[1]) == 2  # Month
        assert len(parts[2]) == 2  # Day
    
    def test_get_current_datetime_time_format(self):
        """get_current_datetime returns time in HH:MM:SS format."""
        result = get_current_datetime()
        
        # Validate time format
        parts = result.time.split(":")
        assert len(parts) == 3
    
    def test_get_current_datetime_weekday_chinese(self):
        """get_current_datetime returns Chinese weekday."""
        result = get_current_datetime()
        
        assert result.weekday_chinese in WEEKDAY_CHINESE.values()
    
    def test_get_current_datetime_custom_format(self):
        """get_current_datetime handles custom format."""
        result = get_current_datetime(format="%Y/%m/%d")
        
        assert "/" in result.datetime
    
    def test_get_current_datetime_invalid_format(self):
        """get_current_datetime handles invalid format gracefully."""
        result = get_current_datetime(format="%invalid")
        
        # Should return some value (ISO format fallback)
        assert result.datetime is not None


class TestWeekdayChinese:
    """Tests for Chinese weekday mapping."""
    
    def test_weekday_mapping_complete(self):
        """All 7 weekdays are mapped."""
        assert len(WEEKDAY_CHINESE) == 7
    
    def test_weekday_mapping_correct(self):
        """Weekday mapping is correct."""
        assert WEEKDAY_CHINESE[0] == "星期一"  # Monday
        assert WEEKDAY_CHINESE[6] == "星期日"  # Sunday
