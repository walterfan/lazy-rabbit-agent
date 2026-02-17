"""Tests for Compliance SubAgent tools and creation."""

import pytest

from app.services.medical_paper_agent.sub_agents.compliance import (
    CheckComplianceInput,
    GenerateReportInput,
    GetChecklistInput,
    create_compliance_tools,
)


class TestComplianceToolCreation:
    """Test that compliance tools are created correctly."""

    def test_creates_three_tools(self):
        tools = create_compliance_tools()
        assert len(tools) == 3

    def test_tool_names(self):
        tools = create_compliance_tools()
        names = {t.name for t in tools}
        assert names == {"check_compliance", "generate_compliance_report", "get_checklist"}

    def test_check_compliance_description(self):
        tools = create_compliance_tools()
        cc = next(t for t in tools if t.name == "check_compliance")
        assert "compliance" in cc.description.lower()

    def test_generate_report_description(self):
        tools = create_compliance_tools()
        gr = next(t for t in tools if t.name == "generate_compliance_report")
        assert "report" in gr.description.lower()

    def test_get_checklist_description(self):
        tools = create_compliance_tools()
        gc = next(t for t in tools if t.name == "get_checklist")
        assert "checklist" in gc.description.lower()


class TestComplianceInputSchemas:
    """Test Pydantic input schemas for compliance tools."""

    def test_check_compliance_input(self):
        inp = CheckComplianceInput(
            manuscript="This RCT examined...",
            paper_type="rct",
        )
        assert inp.paper_type == "rct"

    def test_generate_report_input(self):
        items = [
            {"item_id": "1a", "status": "PASS", "finding": "Title OK"},
            {"item_id": "1b", "status": "FAIL", "finding": "Missing summary"},
        ]
        inp = GenerateReportInput(items=items, checklist_type="CONSORT")
        assert len(inp.items) == 2
        assert inp.checklist_type == "CONSORT"

    def test_get_checklist_input(self):
        inp = GetChecklistInput(paper_type="meta_analysis")
        assert inp.paper_type == "meta_analysis"


class TestComplianceToolExecution:
    """Test that compliance tools can be invoked."""

    def test_check_compliance_returns_prompt(self):
        tools = create_compliance_tools()
        cc = next(t for t in tools if t.name == "check_compliance")
        result = cc.invoke({
            "manuscript": "This randomised controlled trial...",
            "paper_type": "rct",
        })
        assert "CONSORT" in result
        assert "randomised" in result.lower() or "manuscript" in result.lower()

    def test_generate_report_all_pass(self):
        tools = create_compliance_tools()
        gr = next(t for t in tools if t.name == "generate_compliance_report")
        items = [
            {"item_id": "1a", "status": "PASS", "finding": "OK"},
            {"item_id": "1b", "status": "PASS", "finding": "OK"},
        ]
        result = gr.invoke({"items": items, "checklist_type": "CONSORT"})
        assert result["passed"] == 2
        assert result["failed"] == 0
        assert result["needs_revision"] is False

    def test_generate_report_with_failures(self):
        tools = create_compliance_tools()
        gr = next(t for t in tools if t.name == "generate_compliance_report")
        items = [
            {"item_id": "1a", "status": "PASS", "finding": "OK"},
            {"item_id": "2a", "status": "FAIL", "finding": "Missing"},
        ]
        result = gr.invoke({"items": items, "checklist_type": "STROBE"})
        assert result["failed"] == 1
        assert result["needs_revision"] is True

    def test_get_checklist_rct(self):
        tools = create_compliance_tools()
        gc = next(t for t in tools if t.name == "get_checklist")
        result = gc.invoke({"paper_type": "rct"})
        name, items = result
        assert name == "CONSORT"
        assert len(items) == 25

    def test_get_checklist_cohort(self):
        tools = create_compliance_tools()
        gc = next(t for t in tools if t.name == "get_checklist")
        result = gc.invoke({"paper_type": "cohort"})
        name, items = result
        assert name == "STROBE"
        assert len(items) == 22

    def test_get_checklist_meta_analysis(self):
        tools = create_compliance_tools()
        gc = next(t for t in tools if t.name == "get_checklist")
        result = gc.invoke({"paper_type": "meta_analysis"})
        name, items = result
        assert name == "PRISMA"
        assert len(items) == 27
