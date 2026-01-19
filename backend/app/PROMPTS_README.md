# Prompt Templates System

## Overview

The prompt templates have been extracted from Python code into a centralized YAML configuration file (`prompts.yaml`) for easier maintenance and modification.

## Files

- **`prompts.yaml`**: Contains all prompt templates, fallback recommendations, and configuration
- **`services/prompt_service.py`**: Service for loading and formatting prompts
- **`services/recommendation_service.py`**: Uses PromptService to generate prompts

## Structure

### prompts.yaml

```yaml
# Single-day recommendation prompt
single_day_recommendation: |
  Template with placeholders like {city}, {temperature}, etc.

# Multi-day recommendation prompt
multi_day_recommendation: |
  Template with placeholders for multi-day forecasts

# Temperature adjustment suggestions
temperature_adjustments:
  怕冷: "适当增加保暖层次"
  怕热: "选择轻薄透气的材质"
  default: "根据实际体感调整"

# Weekday translations
weekdays:
  Monday: "星期一"
  Tuesday: "星期二"
  ...

# Fallback recommendations by temperature
fallback_recommendations:
  very_cold:  # temp < 5°C
    clothing: [...]
    advice: "..."
    emoji: "🧥❄️🧣"
  ...

# Weather warnings
weather_warnings:
  rain: "记得带伞"
  fog: "能见度低，注意安全"
```

## Usage

### In Code

```python
from app.services.prompt_service import PromptService

# Get single-day prompt
prompt = PromptService.get_single_day_prompt(
    city="北京",
    temperature=15.0,
    weather="晴",
    humidity=60.0,
    wind_direction="北风",
    wind_power="3",
    date="2024-01-15",
    day_of_week="星期一",
    gender="男",
    age=30,
    identity="上班族",
    style="休闲",
    temperature_sensitivity="正常",
    activity_context="工作",
    other_preferences="无",
)

# Get multi-day prompt
prompt = PromptService.get_multi_day_prompt(
    date_label="明天",
    date_formatted="2024年01月16日",
    weekday_zh="星期二",
    gender="女",
    age=25,
    identity="学生",
    style="时尚",
    temperature_sensitivity="怕冷",
    activity_context="上课",
    other_preferences="喜欢裙子",
    city="上海",
    weather_text="多云",
    temperature_high=18.0,
    temperature_low=12.0,
    wind_direction="东风",
    wind_power="2级",
    temperature_adjustment="适当增加保暖层次",
)

# Get temperature adjustment
adjustment = PromptService.get_temperature_adjustment("怕冷")
# Returns: "适当增加保暖层次"

# Get weekday translation
weekday_zh = PromptService.get_weekday_zh("Monday")
# Returns: "星期一"

# Get fallback recommendation
fallback = PromptService.get_fallback_recommendation(10.0)
# Returns: {
#   "clothing": ["外套", "长袖", "长裤"],
#   "advice": "今天10.0°C有点凉，建议穿外套配长袖长裤。早晚温差大，注意增减衣物。",
#   "emoji": "🧥👔"
# }

# Get weather warnings
warnings = PromptService.get_weather_warnings("小雨")
# Returns: ["记得带伞"]
```

## Benefits

1. **Centralized Management**: All prompts in one place
2. **Easy Updates**: Modify prompts without changing code
3. **Version Control**: Track prompt changes separately
4. **Internationalization**: Easy to add multiple languages
5. **Testing**: Test prompt changes without redeploying
6. **Collaboration**: Non-developers can update prompts

## Modifying Prompts

1. Edit `backend/app/prompts.yaml`
2. Use placeholders in `{curly_braces}` for dynamic values
3. Restart the server to reload prompts (prompts are cached on first load)

## Testing

```bash
cd backend
python -c "
from app.services.prompt_service import PromptService

# Test loading
prompts = PromptService.load_prompts()
print('Loaded templates:', list(prompts.keys()))

# Test specific functions
print(PromptService.get_temperature_adjustment('怕冷'))
print(PromptService.get_weekday_zh('Monday'))
"
```

## Migration Notes

The following methods in `RecommendationService` now use `PromptService`:

- `_build_prompt()` → `PromptService.get_single_day_prompt()`
- `_build_multi_day_prompt()` → `PromptService.get_multi_day_prompt()`
- `_get_temperature_adjustment()` → `PromptService.get_temperature_adjustment()`
- `_generate_fallback_recommendation()` → `PromptService.get_fallback_recommendation()`

All existing functionality remains the same, just with cleaner separation of concerns.


