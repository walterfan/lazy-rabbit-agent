"""Tests for Writer SubAgent tools and creation."""

import pytest

from app.services.medical_paper_agent.sub_agents.writer import (
    MergeSectionsInput,
    ReviseSectionInput,
    WriteSectionInput,
    create_writer_tools,
)


class TestWriterToolCreation:
    """Test that writer tools are created correctly."""

    def test_creates_three_tools(self):
        tools = create_writer_tools()
        assert len(tools) == 3

    def test_tool_names(self):
        tools = create_writer_tools()
        names = {t.name for t in tools}
        assert names == {"write_section", "revise_section", "merge_sections"}

    def test_write_section_tool_description(self):
        tools = create_writer_tools()
        ws = next(t for t in tools if t.name == "write_section")
        assert "section" in ws.description.lower()

    def test_revise_section_tool_description(self):
        tools = create_writer_tools()
        rs = next(t for t in tools if t.name == "revise_section")
        assert "revis" in rs.description.lower()

    def test_merge_sections_tool_description(self):
        tools = create_writer_tools()
        ms = next(t for t in tools if t.name == "merge_sections")
        assert "merge" in ms.description.lower()


class TestWriterInputSchemas:
    """Test Pydantic input schemas for writer tools."""

    def test_write_section_input(self):
        inp = WriteSectionInput(
            section_type="introduction",
            context={"paper_type": "rct", "research_question": "Does X improve Y?"},
        )
        assert inp.section_type == "introduction"
        assert inp.word_limit == 500  # default

    def test_write_section_custom_limit(self):
        inp = WriteSectionInput(
            section_type="methods",
            context={"paper_type": "rct", "study_design": "double-blind"},
            word_limit=1000,
        )
        assert inp.word_limit == 1000

    def test_revise_section_input(self):
        inp = ReviseSectionInput(
            section_type="results",
            current_content="The results show...",
            feedback="Add confidence intervals",
        )
        assert inp.section_type == "results"
        assert "confidence" in inp.feedback

    def test_merge_sections_input(self):
        sections = {
            "introduction": "Background text...",
            "methods": "Study design...",
            "results": "Outcomes...",
            "discussion": "Interpretation...",
        }
        inp = MergeSectionsInput(sections=sections)
        assert len(inp.sections) == 4
        assert "introduction" in inp.sections


class TestWriterToolExecution:
    """Test that writer tools can be invoked."""

    def test_write_section_returns_prompt(self):
        tools = create_writer_tools()
        ws = next(t for t in tools if t.name == "write_section")
        result = ws.invoke({
            "section_type": "introduction",
            "context": {"paper_type": "rct", "research_question": "Does X improve Y?"},
            "word_limit": 500,
        })
        assert "introduction" in result.lower()
        assert "500" in result

    def test_revise_section_returns_prompt(self):
        tools = create_writer_tools()
        rs = next(t for t in tools if t.name == "revise_section")
        result = rs.invoke({
            "section_type": "methods",
            "current_content": "The study used...",
            "feedback": "Add more detail on randomization",
        })
        assert "methods" in result.lower()
        assert "randomization" in result.lower()

    def test_merge_sections_returns_dict(self):
        tools = create_writer_tools()
        ms = next(t for t in tools if t.name == "merge_sections")
        sections = {
            "abstract": "Summary text",
            "introduction": "Background text",
            "methods": "Methods text",
            "results": "Results text",
            "discussion": "Discussion text",
        }
        result = ms.invoke({"sections": sections})
        # merge_sections returns a dict with sections, total_word_count, section_count
        assert isinstance(result, dict)
        assert result["section_count"] == 5
        assert result["total_word_count"] > 0
        titles = [s["title"] for s in result["sections"]]
        assert "Abstract" in titles
        assert "Introduction" in titles
