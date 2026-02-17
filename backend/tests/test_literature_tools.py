"""Tests for Literature Agent tools."""

import pytest
from app.services.medical_paper_agent.tools.literature_tools import (
    format_citation,
)


class TestFormatCitation:
    """Test citation formatting in various styles."""

    def test_vancouver_style(self):
        ref = {
            "pmid": "12345",
            "title": "Effect of Drug X on Condition Y.",
            "authors": ["Smith J", "Doe A", "Lee B", "Wang C"],
            "journal": "Lancet",
            "year": 2024,
        }
        citation = format_citation(ref, style="vancouver")
        assert "Smith J" in citation
        assert "et al" in citation
        assert "Lancet" in citation
        assert "PMID: 12345" in citation

    def test_apa_style(self):
        ref = {
            "pmid": "12345",
            "title": "Effect of Drug X.",
            "authors": ["Smith J", "Doe A"],
            "journal": "JAMA",
            "year": 2023,
        }
        citation = format_citation(ref, style="apa")
        assert "(2023)" in citation
        assert "JAMA" in citation

    def test_few_authors_no_et_al(self):
        ref = {
            "pmid": "99",
            "title": "Test.",
            "authors": ["Alpha A", "Beta B"],
            "journal": "BMJ",
            "year": 2025,
        }
        citation = format_citation(ref, style="vancouver")
        assert "et al" not in citation
        assert "Alpha A" in citation


class TestSearchPubMed:
    """Test PubMed search (may require network or mock)."""

    @pytest.mark.asyncio
    async def test_search_returns_dict(self):
        from app.services.medical_paper_agent.tools.literature_tools import search_pubmed
        # This will gracefully handle missing BioPython
        result = await search_pubmed("test query", max_results=1)
        assert isinstance(result, dict)
        assert "query" in result


class TestSearchClinicalTrials:
    """Test ClinicalTrials.gov search."""

    @pytest.mark.asyncio
    async def test_search_returns_dict(self):
        from app.services.medical_paper_agent.tools.literature_tools import search_clinicaltrials
        result = await search_clinicaltrials("aspirin RCT", max_results=1)
        assert isinstance(result, dict)
        assert "query" in result
