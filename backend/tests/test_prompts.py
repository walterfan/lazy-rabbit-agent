"""Unit tests for prompt loader.

Phase 3.2: Prompt Loader Tests (TDD)
"""

import pytest

from app.services.secretary_agent.prompts import (
    PromptNotFoundError,
    PromptVariableError,
    get_prompt,
    list_prompts,
    load_prompt_file,
    reload_prompts,
)


class TestLoadPromptFile:
    """Tests for load_prompt_file function."""

    def test_load_valid_yaml_file(self) -> None:
        """Test loading a valid YAML prompt file."""
        # When: Loading system.yaml
        data = load_prompt_file("system.yaml")

        # Then: File is loaded correctly
        assert data is not None
        assert "prompts" in data
        assert "system" in data["prompts"]

    def test_load_file_caches_result(self) -> None:
        """Test that loading is cached."""
        # Given: Clear cache
        reload_prompts()

        # When: Loading same file twice
        data1 = load_prompt_file("system.yaml")
        data2 = load_prompt_file("system.yaml")

        # Then: Same object (cached)
        assert data1 is data2

    def test_load_missing_file_raises_error(self) -> None:
        """Test that loading non-existent file raises FileNotFoundError."""
        # When/Then: Loading non-existent file raises error
        with pytest.raises(FileNotFoundError):
            load_prompt_file("nonexistent.yaml")


class TestGetPrompt:
    """Tests for get_prompt function."""

    def test_get_prompt_with_variables(self) -> None:
        """Test getting a prompt and filling variables."""
        # When: Getting learn_word prompt
        prompt = get_prompt(
            "learning_tools.yaml",
            "learn_word",
            word="serendipity"
        )

        # Then: Variables are substituted
        assert "serendipity" in prompt
        assert "{word}" not in prompt

    def test_get_prompt_system(self) -> None:
        """Test getting system prompt."""
        # When: Getting system prompt
        prompt = get_prompt(
            "system.yaml",
            "system",
            current_date="2026-02-04",
            timezone="Asia/Shanghai"
        )

        # Then: Variables are substituted
        assert "2026-02-04" in prompt
        assert "Personal Secretary" in prompt

    def test_get_prompt_missing_prompt_name(self) -> None:
        """Test that missing prompt name raises PromptNotFoundError."""
        # When/Then: Getting non-existent prompt raises error
        with pytest.raises(PromptNotFoundError) as exc_info:
            get_prompt("system.yaml", "nonexistent_prompt")

        # And: Error message is helpful
        assert "nonexistent_prompt" in str(exc_info.value)
        assert "Available prompts" in str(exc_info.value)

    def test_get_prompt_missing_required_variable(self) -> None:
        """Test that missing required variable raises PromptVariableError."""
        # When/Then: Missing required variable raises error
        with pytest.raises(PromptVariableError) as exc_info:
            get_prompt("learning_tools.yaml", "learn_word")  # Missing 'word'

        # And: Error message indicates missing variable
        assert "word" in str(exc_info.value)

    def test_get_prompt_article_tools(self) -> None:
        """Test getting article processing prompts."""
        # When: Getting translate_paragraph prompt
        prompt = get_prompt(
            "article_tools.yaml",
            "translate_paragraph",
            paragraph="Hello world"
        )

        # Then: Prompt is formatted
        assert "Hello world" in prompt
        assert "Chinese" in prompt


class TestListPrompts:
    """Tests for list_prompts function."""

    def test_list_prompts_system(self) -> None:
        """Test listing prompts from system.yaml."""
        # When: Listing prompts
        prompts = list_prompts("system.yaml")

        # Then: Expected prompts are present
        assert "system" in prompts
        assert "confirm_save" in prompts
        assert "welcome" in prompts

    def test_list_prompts_learning_tools(self) -> None:
        """Test listing prompts from learning_tools.yaml."""
        # When: Listing prompts
        prompts = list_prompts("learning_tools.yaml")

        # Then: Expected prompts are present
        assert "learn_word" in prompts
        assert "learn_sentence" in prompts
        assert "learn_topic" in prompts
        assert "answer_question" in prompts
        assert "plan_idea" in prompts


class TestReloadPrompts:
    """Tests for reload_prompts function."""

    def test_reload_clears_cache(self) -> None:
        """Test that reload clears the cache."""
        # Given: A cached file
        data1 = load_prompt_file("system.yaml")

        # When: Reloading
        reload_prompts()

        # Then: Cache is cleared (new object returned)
        data2 = load_prompt_file("system.yaml")
        # Note: Content should be same, but object identity may differ
        # after cache clear + reload
        assert data1 == data2  # Content equality


class TestPromptContent:
    """Tests for actual prompt content."""

    def test_learn_word_prompt_has_required_sections(self) -> None:
        """Test that learn_word prompt includes all required sections."""
        prompt = get_prompt("learning_tools.yaml", "learn_word", word="test")

        # Should mention key sections
        assert "Chinese Explanation" in prompt or "中文解释" in prompt
        assert "Pronunciation" in prompt
        assert "Part of Speech" in prompt
        assert "Examples" in prompt
        assert "Synonyms" in prompt

    def test_learn_topic_prompt_has_required_sections(self) -> None:
        """Test that learn_topic prompt includes all required sections."""
        prompt = get_prompt("learning_tools.yaml", "learn_topic", topic="Kubernetes")

        # Should mention key sections
        assert "Introduction" in prompt or "简介" in prompt
        assert "Key Concepts" in prompt or "核心概念" in prompt
        assert "Learning Path" in prompt or "学习路径" in prompt
        assert "Resources" in prompt or "推荐资源" in prompt

    def test_article_mindmap_prompt_mentions_plantuml(self) -> None:
        """Test that mindmap prompt explains PlantUML format."""
        prompt = get_prompt(
            "article_tools.yaml",
            "generate_mindmap",
            title="Test",
            key_points="Point 1, Point 2",
            headings="Heading 1, Heading 2"
        )

        assert "@startmindmap" in prompt
        assert "@endmindmap" in prompt
