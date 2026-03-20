"""Unit tests for CostReporter."""

from __future__ import annotations

from llm_budget.reporter import CostReporter


class TestCostReporter:
    """Tests for CostReporter instantiation and stub behavior."""

    def test_can_instantiate(self) -> None:
        reporter = CostReporter()
        assert isinstance(reporter, CostReporter)

    def test_report_call_does_not_raise(self) -> None:
        reporter = CostReporter()
        reporter.report_call(
            model="gpt-4o",
            input_tokens=100,
            output_tokens=50,
            cost=0.5,
        )

    def test_report_session_does_not_raise(self) -> None:
        reporter = CostReporter()
        reporter.report_session()

    def test_initial_session_cost_is_zero(self) -> None:
        reporter = CostReporter()
        assert reporter._session_cost == 0.0
