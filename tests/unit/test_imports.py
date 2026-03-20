"""Smoke tests to validate package imports and exception hierarchy."""

from __future__ import annotations


def test_package_version() -> None:
    from llm_budget import __version__

    assert __version__ == "0.1.0"


def test_public_api_exports() -> None:
    import llm_budget

    assert hasattr(llm_budget, "track_costs")
    assert hasattr(llm_budget, "BudgetExceededError")
    assert hasattr(llm_budget, "LocalRateLimitError")
    assert hasattr(llm_budget, "PricingMatrixOutdatedWarning")
    assert hasattr(llm_budget, "PricingRegistry")
    assert hasattr(llm_budget, "UsageStore")
    assert hasattr(llm_budget, "CostReporter")
    assert hasattr(llm_budget, "RateLimiter")


def test_budget_exceeded_error_is_exception() -> None:
    from llm_budget import BudgetExceededError

    assert issubclass(BudgetExceededError, Exception)


def test_local_rate_limit_error_is_exception() -> None:
    from llm_budget import LocalRateLimitError

    assert issubclass(LocalRateLimitError, Exception)


def test_pricing_matrix_outdated_warning_is_warning() -> None:
    from llm_budget import PricingMatrixOutdatedWarning

    assert issubclass(PricingMatrixOutdatedWarning, UserWarning)


def test_track_costs_bare_decorator() -> None:
    from llm_budget import track_costs

    @track_costs
    def my_func() -> str:
        return "hello"

    assert my_func() == "hello"


def test_track_costs_with_args() -> None:
    from llm_budget import track_costs

    @track_costs(project="test", max_budget=10.0)
    def my_func() -> str:
        return "hello"

    assert my_func() == "hello"
