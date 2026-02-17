"""Tests for Stats SubAgent tools and creation."""

import pytest

from app.services.medical_paper_agent.sub_agents.stats import (
    ChiSquareInput,
    SampleSizeInput,
    SurvivalInput,
    TTestInput,
    create_stats_tools,
)


class TestStatsToolCreation:
    """Test that stats tools are created correctly."""

    def test_creates_four_tools(self):
        tools = create_stats_tools()
        assert len(tools) == 4

    def test_tool_names(self):
        tools = create_stats_tools()
        names = {t.name for t in tools}
        assert names == {
            "run_ttest",
            "run_chi_square",
            "run_survival_analysis",
            "calculate_sample_size",
        }

    def test_ttest_tool_description(self):
        tools = create_stats_tools()
        tt = next(t for t in tools if t.name == "run_ttest")
        assert "t-test" in tt.description.lower()

    def test_chi_square_tool_description(self):
        tools = create_stats_tools()
        cs = next(t for t in tools if t.name == "run_chi_square")
        assert "chi-square" in cs.description.lower()

    def test_survival_tool_description(self):
        tools = create_stats_tools()
        surv = next(t for t in tools if t.name == "run_survival_analysis")
        assert "survival" in surv.description.lower()

    def test_sample_size_tool_description(self):
        tools = create_stats_tools()
        ss = next(t for t in tools if t.name == "calculate_sample_size")
        assert "sample size" in ss.description.lower()


class TestStatsInputSchemas:
    """Test Pydantic input schemas for stats tools."""

    def test_ttest_input(self):
        inp = TTestInput(group1=[1.0, 2.0, 3.0], group2=[4.0, 5.0, 6.0])
        assert len(inp.group1) == 3
        assert inp.paired is False  # default

    def test_ttest_paired(self):
        inp = TTestInput(group1=[1.0, 2.0], group2=[3.0, 4.0], paired=True)
        assert inp.paired is True

    def test_chi_square_input(self):
        inp = ChiSquareInput(observed=[[10, 20], [30, 40]])
        assert len(inp.observed) == 2

    def test_survival_input(self):
        inp = SurvivalInput(times=[1.0, 2.0, 3.0], events=[1, 0, 1])
        assert len(inp.times) == 3
        assert inp.groups is None  # default

    def test_survival_with_groups(self):
        inp = SurvivalInput(
            times=[1.0, 2.0, 3.0],
            events=[1, 0, 1],
            groups=["A", "A", "B"],
        )
        assert len(inp.groups) == 3

    def test_sample_size_input(self):
        inp = SampleSizeInput(effect_size=0.5)
        assert inp.alpha == 0.05  # default
        assert inp.power == 0.80  # default
        assert inp.test_type == "two_sample_ttest"  # default

    def test_sample_size_custom(self):
        inp = SampleSizeInput(
            effect_size=0.3,
            alpha=0.01,
            power=0.90,
            test_type="one_sample_ttest",
        )
        assert inp.alpha == 0.01
        assert inp.power == 0.90
