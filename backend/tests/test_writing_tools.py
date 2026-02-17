"""Tests for Writer Agent tools."""

from app.services.medical_paper_agent.tools.writing_tools import (
    SECTION_ORDER,
    merge_sections,
    revise_section_prompt,
    write_section_prompt,
)


class TestWriteSectionPrompt:
    """Test prompt generation for manuscript sections."""

    def test_introduction_prompt(self):
        prompt = write_section_prompt(
            "introduction",
            context={"paper_type": "rct", "research_question": "Does X work?", "references": "[1] Test"},
            word_limit=500,
        )
        assert "Introduction" in prompt
        assert "Does X work?" in prompt
        assert "500" in prompt

    def test_methods_prompt(self):
        prompt = write_section_prompt(
            "methods",
            context={"paper_type": "cohort", "study_design": "retrospective"},
            word_limit=400,
        )
        assert "Methods" in prompt
        assert "retrospective" in prompt

    def test_results_prompt(self):
        prompt = write_section_prompt(
            "results",
            context={"paper_type": "rct", "stats_report": "p=0.03"},
        )
        assert "Results" in prompt
        assert "p=0.03" in prompt

    def test_discussion_prompt(self):
        prompt = write_section_prompt(
            "discussion",
            context={"paper_type": "rct", "research_question": "Q?"},
        )
        assert "Discussion" in prompt

    def test_abstract_prompt(self):
        prompt = write_section_prompt("abstract", context={"paper_type": "rct"})
        assert "abstract" in prompt.lower()

    def test_unknown_section(self):
        prompt = write_section_prompt("custom_section", context={}, word_limit=200)
        assert "custom_section" in prompt


class TestReviseSectionPrompt:
    """Test revision prompt generation."""

    def test_generates_revision_prompt(self):
        prompt = revise_section_prompt(
            "introduction",
            current_content="This is the introduction...",
            feedback="Add more background on the disease prevalence.",
        )
        assert "introduction" in prompt
        assert "This is the introduction" in prompt
        assert "disease prevalence" in prompt
        assert "REVISED" in prompt


class TestMergeSections:
    """Test section merging."""

    def test_merge_all_sections(self):
        sections = {
            "introduction": "Background and rationale for this study.",
            "methods": "We conducted a randomized controlled trial.",
            "results": "The primary outcome showed significant improvement.",
            "discussion": "Our findings suggest that the intervention is effective.",
            "abstract": "This study investigated...",
        }
        result = merge_sections(sections)
        assert result["section_count"] == 5
        assert result["total_word_count"] > 0
        # Verify order
        types = [s["section_type"] for s in result["sections"]]
        assert types == SECTION_ORDER

    def test_merge_partial_sections(self):
        sections = {
            "introduction": "Intro text here.",
            "results": "Results text here.",
        }
        result = merge_sections(sections)
        assert result["section_count"] == 2

    def test_empty_sections(self):
        result = merge_sections({})
        assert result["section_count"] == 0
        assert result["total_word_count"] == 0

    def test_word_count_accuracy(self):
        sections = {
            "introduction": "one two three four five",
        }
        result = merge_sections(sections)
        assert result["sections"][0]["word_count"] == 5
