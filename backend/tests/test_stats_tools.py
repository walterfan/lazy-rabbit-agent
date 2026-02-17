"""Tests for Stats Agent tools."""

import pytest
from app.services.medical_paper_agent.tools.stats_tools import (
    calculate_sample_size,
    generate_stats_report,
    run_chi_square,
    run_survival_analysis,
    run_ttest,
)


class TestTTest:
    """Test t-test tool."""

    def test_independent_ttest(self):
        g1 = [5.1, 4.8, 5.3, 5.0, 4.9]
        g2 = [3.2, 3.5, 3.1, 3.3, 3.4]
        result = run_ttest(g1, g2, paired=False)
        assert result["test_name"] == "independent_ttest"
        assert result["p_value"] < 0.05  # clearly different groups
        assert "statistic" in result
        assert "confidence_interval" in result
        assert "effect_size" in result

    def test_paired_ttest(self):
        before = [120, 130, 125, 135, 140]
        after = [115, 125, 120, 128, 132]
        result = run_ttest(before, after, paired=True)
        assert result["test_name"] == "paired_ttest"
        assert "p_value" in result

    def test_no_difference(self):
        g1 = [5.0, 5.0, 5.0, 5.0]
        g2 = [5.0, 5.0, 5.0, 5.0]
        result = run_ttest(g1, g2)
        assert result["p_value"] >= 0.05 or result["statistic"] == 0.0

    def test_interpretation(self):
        g1 = [10, 11, 12, 10, 11]
        g2 = [1, 2, 1, 2, 1]
        result = run_ttest(g1, g2)
        assert "significant" in result["interpretation"].lower()


class TestChiSquare:
    """Test chi-square tool."""

    def test_significant_association(self):
        # Strong association: treatment vs placebo
        observed = [[50, 10], [20, 40]]
        result = run_chi_square(observed)
        assert result["test_name"] == "chi_square"
        assert result["p_value"] < 0.05
        assert result["effect_size"] > 0

    def test_no_association(self):
        # Equal distribution
        observed = [[25, 25], [25, 25]]
        result = run_chi_square(observed)
        assert result["p_value"] > 0.05

    def test_degrees_of_freedom(self):
        observed = [[10, 20], [30, 40]]
        result = run_chi_square(observed)
        assert result["degrees_of_freedom"] == 1  # (2-1)*(2-1)


class TestSurvivalAnalysis:
    """Test survival analysis tool."""

    def test_basic_survival(self):
        times = [1.0, 2.0, 3.0, 4.0, 5.0]
        events = [1, 1, 0, 1, 0]
        result = run_survival_analysis(times, events)
        assert result["test_name"] == "survival_analysis"
        assert result["n_subjects"] == 5
        assert result["n_events"] == 3

    def test_group_comparison(self):
        times = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
        events = [1, 1, 1, 0, 0, 1]
        groups = [0, 0, 0, 1, 1, 1]
        result = run_survival_analysis(times, events, groups)
        assert "group_summary" in result
        assert "p_value" in result


class TestSampleSize:
    """Test sample size calculation."""

    def test_two_sample_ttest(self):
        result = calculate_sample_size(effect_size=0.5, alpha=0.05, power=0.80)
        assert result["test_type"] == "two_sample_ttest"
        assert result["n_per_group"] > 0
        assert result["total_n"] == result["n_per_group"] * 2

    def test_larger_effect_needs_fewer_subjects(self):
        small = calculate_sample_size(effect_size=0.2)
        large = calculate_sample_size(effect_size=0.8)
        assert small["n_per_group"] > large["n_per_group"]

    def test_higher_power_needs_more_subjects(self):
        low = calculate_sample_size(effect_size=0.5, power=0.80)
        high = calculate_sample_size(effect_size=0.5, power=0.95)
        assert high["n_per_group"] > low["n_per_group"]


class TestStatsReport:
    """Test report generation."""

    def test_report_counts_significant(self):
        results = [
            {"test_name": "ttest", "p_value": 0.03},
            {"test_name": "chi2", "p_value": 0.5},
            {"test_name": "ttest2", "p_value": 0.001},
        ]
        report = generate_stats_report(results)
        assert report["total_analyses"] == 3
        assert report["significant_results"] == 2
