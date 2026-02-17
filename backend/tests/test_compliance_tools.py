"""Tests for Compliance Agent tools."""

from app.services.medical_paper_agent.tools.compliance_tools import (
    CONSORT_ITEMS,
    PRISMA_ITEMS,
    STROBE_ITEMS,
    check_compliance_prompt,
    generate_compliance_report,
    get_checklist,
)


class TestGetChecklist:
    """Test checklist selection by paper type."""

    def test_rct_gets_consort(self):
        name, items = get_checklist("rct")
        assert name == "CONSORT"
        assert len(items) == 25  # CONSORT 2010 has 25 items

    def test_cohort_gets_strobe(self):
        name, items = get_checklist("cohort")
        assert name == "STROBE"
        assert len(items) == 22

    def test_meta_analysis_gets_prisma(self):
        name, items = get_checklist("meta_analysis")
        assert name == "PRISMA"
        assert len(items) == 27

    def test_unknown_defaults_to_strobe(self):
        name, items = get_checklist("unknown")
        assert name == "STROBE"


class TestCheckCompliancePrompt:
    """Test compliance prompt generation."""

    def test_consort_prompt(self):
        prompt = check_compliance_prompt("My RCT manuscript...", "rct")
        assert "CONSORT" in prompt
        assert "randomised trial" in prompt.lower() or "Identification" in prompt
        assert "manuscript" in prompt.lower()

    def test_strobe_prompt(self):
        prompt = check_compliance_prompt("Observational study...", "cohort")
        assert "STROBE" in prompt

    def test_prisma_prompt(self):
        prompt = check_compliance_prompt("Systematic review...", "meta_analysis")
        assert "PRISMA" in prompt


class TestGenerateComplianceReport:
    """Test compliance report generation."""

    def test_all_pass(self):
        items = [
            {"item_id": "1a", "status": "PASS", "finding": "Title mentions RCT"},
            {"item_id": "1b", "status": "PASS", "finding": "Summary present"},
        ]
        report = generate_compliance_report(items, "CONSORT")
        assert report["total_items"] == 2
        assert report["passed"] == 2
        assert report["failed"] == 0
        assert report["overall_score"] == 1.0
        assert report["needs_revision"] is False

    def test_mixed_results(self):
        items = [
            {"item_id": "1a", "status": "PASS", "finding": "OK"},
            {"item_id": "1b", "status": "WARN", "finding": "Incomplete"},
            {"item_id": "2a", "status": "FAIL", "finding": "Missing"},
        ]
        report = generate_compliance_report(items, "CONSORT")
        assert report["passed"] == 1
        assert report["warnings"] == 1
        assert report["failed"] == 1
        assert report["needs_revision"] is True
        assert len(report["failed_items"]) == 1
        assert len(report["warning_items"]) == 1
        # Score: (1 + 0.5*1) / 3 = 0.5
        assert report["overall_score"] == 0.5

    def test_empty_items(self):
        report = generate_compliance_report([], "STROBE")
        assert report["total_items"] == 0
        assert report["overall_score"] == 0.0

    def test_checklist_type_preserved(self):
        report = generate_compliance_report([], "PRISMA")
        assert report["checklist_type"] == "PRISMA"
