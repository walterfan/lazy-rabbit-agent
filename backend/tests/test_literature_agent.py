"""Tests for Literature SubAgent tools and creation."""

import pytest

from app.services.medical_paper_agent.sub_agents.literature import (
    FormatCitationInput,
    GetAbstractInput,
    SearchClinicalTrialsInput,
    SearchPubMedInput,
    create_literature_tools,
)


class TestLiteratureToolCreation:
    """Test that literature tools are created correctly."""

    def test_creates_four_tools(self):
        tools = create_literature_tools()
        assert len(tools) == 4

    def test_tool_names(self):
        tools = create_literature_tools()
        names = {t.name for t in tools}
        assert names == {
            "search_pubmed",
            "search_clinicaltrials",
            "get_article_abstract",
            "format_citation",
        }

    def test_search_pubmed_tool_has_description(self):
        tools = create_literature_tools()
        pubmed_tool = next(t for t in tools if t.name == "search_pubmed")
        assert "PubMed" in pubmed_tool.description

    def test_search_clinicaltrials_tool_has_description(self):
        tools = create_literature_tools()
        ct_tool = next(t for t in tools if t.name == "search_clinicaltrials")
        assert "ClinicalTrials" in ct_tool.description

    def test_format_citation_tool_has_description(self):
        tools = create_literature_tools()
        cite_tool = next(t for t in tools if t.name == "format_citation")
        assert "citation" in cite_tool.description.lower()


class TestLiteratureInputSchemas:
    """Test Pydantic input schemas for literature tools."""

    def test_search_pubmed_input(self):
        inp = SearchPubMedInput(query="diabetes mellitus treatment")
        assert inp.query == "diabetes mellitus treatment"
        assert inp.max_results == 20  # default

    def test_search_pubmed_custom_max(self):
        inp = SearchPubMedInput(query="cancer", max_results=5)
        assert inp.max_results == 5

    def test_search_clinicaltrials_input(self):
        inp = SearchClinicalTrialsInput(query="COVID-19 vaccine")
        assert inp.query == "COVID-19 vaccine"
        assert inp.max_results == 10  # default

    def test_get_abstract_input(self):
        inp = GetAbstractInput(pmid="12345678")
        assert inp.pmid == "12345678"

    def test_format_citation_input(self):
        ref = {"pmid": "123", "title": "Test", "authors": ["A"], "journal": "J", "year": "2024"}
        inp = FormatCitationInput(reference=ref, style="vancouver")
        assert inp.style == "vancouver"
        assert inp.reference["pmid"] == "123"

    def test_format_citation_default_style(self):
        ref = {"pmid": "123", "title": "Test"}
        inp = FormatCitationInput(reference=ref)
        assert inp.style == "vancouver"
