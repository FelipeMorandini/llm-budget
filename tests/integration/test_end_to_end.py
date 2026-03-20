"""End-to-end integration tests for the llm_budget scaffolding."""

from __future__ import annotations

import importlib
import sys
from typing import Any

import pytest
from pytest import approx


def test_full_public_api_importable() -> None:
    """Verify every name in __all__ is importable from llm_budget."""
    import llm_budget

    expected_names = [
        "BudgetExceededError",
        "CostReporter",
        "LocalRateLimitError",
        "PricingMatrixOutdatedWarning",
        "PricingRegistry",
        "RateLimiter",
        "UsageStore",
        "__version__",
        "default_registry",
        "track_costs",
    ]
    for name in expected_names:
        assert hasattr(llm_budget, name), f"{name} missing from llm_budget"
    assert set(expected_names) == set(llm_budget.__all__)


def test_track_costs_bare_decorator_with_dict_response() -> None:
    """@track_costs bare on a function returning a dict (simulated LLM response)."""
    from llm_budget import track_costs

    @track_costs
    def call_llm() -> dict[str, Any]:
        return {
            "model": "gpt-4o",
            "choices": [{"message": {"content": "Hello!"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5},
        }

    result = call_llm()
    assert isinstance(result, dict)
    assert result["model"] == "gpt-4o"
    assert result["usage"]["prompt_tokens"] == 10


def test_track_costs_with_project_kwarg() -> None:
    """@track_costs(project="test") on a function returning a dict."""
    from llm_budget import track_costs

    @track_costs(project="test")
    def call_llm() -> dict[str, Any]:
        return {"model": "claude-sonnet-4-20250514", "content": "Hi"}

    result = call_llm()
    assert isinstance(result, dict)
    assert result["model"] == "claude-sonnet-4-20250514"


def test_track_costs_preserves_function_metadata() -> None:
    """Decorated function should preserve __name__ and __doc__."""
    from llm_budget import track_costs

    @track_costs
    def my_special_func() -> str:
        """My docstring."""
        return "ok"

    assert my_special_func.__name__ == "my_special_func"
    assert my_special_func.__doc__ == "My docstring."


def test_track_costs_with_all_kwargs() -> None:
    """Decorator accepts all documented keyword arguments without error."""
    from llm_budget import track_costs

    @track_costs(
        project="integration-test",
        model="gpt-4o",
        max_budget=50.0,
        reset="monthly",
        rate_limit=60,
        tpm_limit=100000,
        extract_usage=lambda resp: ("gpt-4o", 10, 5),
    )
    def call_llm() -> dict[str, Any]:
        return {"result": "ok"}

    assert call_llm() == {"result": "ok"}


def test_track_costs_passes_args_and_kwargs() -> None:
    """Decorated function correctly receives positional and keyword args."""
    from llm_budget import track_costs

    @track_costs
    def call_llm(prompt: str, temperature: float = 0.7) -> dict[str, Any]:
        return {"prompt": prompt, "temperature": temperature}

    result = call_llm("hello", temperature=0.9)
    assert result["prompt"] == "hello"
    assert result["temperature"] == 0.9


def test_pricing_registry_register_and_compute() -> None:
    """Register a model and verify cost calculation math."""
    from llm_budget import PricingRegistry

    registry = PricingRegistry()
    # $0.01 per input token, $0.03 per output token
    registry.register_model("test-model", 0.01, 0.03)

    cost = registry.get_cost("test-model", input_tokens=100, output_tokens=50)
    expected = 100 * 0.01 + 50 * 0.03  # 1.0 + 1.5 = 2.5
    assert cost == approx(expected)


def test_pricing_registry_unknown_model_returns_zero() -> None:
    """Unknown model should return 0.0 cost, not crash."""
    from llm_budget import PricingMatrixOutdatedWarning, PricingRegistry

    registry = PricingRegistry()
    with pytest.warns(PricingMatrixOutdatedWarning):
        cost = registry.get_cost("unknown-model", input_tokens=100, output_tokens=50)
    assert cost == 0.0


def test_pricing_registry_override_model() -> None:
    """Registering the same model twice should override pricing."""
    from llm_budget import PricingRegistry

    registry = PricingRegistry()
    registry.register_model("gpt-4o", 0.01, 0.03)
    registry.register_model("gpt-4o", 0.005, 0.015)

    cost = registry.get_cost("gpt-4o", input_tokens=1000, output_tokens=1000)
    expected = 1000 * 0.005 + 1000 * 0.015
    assert cost == approx(expected)


def test_usage_store_creation_with_tmp_path(tmp_db_path: str) -> None:
    """Creating a UsageStore with a tmp path should not crash."""
    from llm_budget import UsageStore

    store = UsageStore(db_path=tmp_db_path)
    assert store is not None


def test_usage_store_creation_with_default_path() -> None:
    """Creating a UsageStore with no path should not crash."""
    from llm_budget import UsageStore

    store = UsageStore()
    assert store is not None


def test_usage_store_log_and_get_cost(tmp_db_path: str) -> None:
    """Calling log_usage and get_total_cost should not crash."""
    from llm_budget import UsageStore

    store = UsageStore(db_path=tmp_db_path)
    store.log_usage(
        project="test",
        model="gpt-4o",
        input_tokens=100,
        output_tokens=50,
        cost=0.05,
    )
    # Stub returns 0.0 — just verify no exception
    total = store.get_total_cost("test")
    assert isinstance(total, float)


def test_rate_limiter_creation_and_check() -> None:
    """Creating a RateLimiter and calling check() should not crash."""
    from llm_budget import RateLimiter

    limiter = RateLimiter(rpm=60, tpm=100000)
    assert limiter is not None
    # check() is a stub — just verify no exception
    limiter.check(tokens=500)


def test_rate_limiter_with_no_limits() -> None:
    """RateLimiter with no limits should accept any check."""
    from llm_budget import RateLimiter

    limiter = RateLimiter()
    limiter.check(tokens=0)
    limiter.check(tokens=999999)


def test_cost_reporter_report_call() -> None:
    """CostReporter.report_call should not crash."""
    from llm_budget import CostReporter

    reporter = CostReporter()
    reporter.report_call(
        model="gpt-4o",
        input_tokens=100,
        output_tokens=50,
        cost=0.05,
    )


def test_cost_reporter_report_session() -> None:
    """CostReporter.report_session should not crash."""
    from llm_budget import CostReporter

    reporter = CostReporter()
    reporter.report_session()


def test_cost_reporter_session_cost_starts_at_zero() -> None:
    """CostReporter._session_cost should start at 0.0."""
    from llm_budget import CostReporter

    reporter = CostReporter()
    assert reporter._session_cost == 0.0


def test_auto_detect_usage_returns_none_for_unknown() -> None:
    """auto_detect_usage should return None for an unrecognized object."""
    from llm_budget.parsers import auto_detect_usage

    result = auto_detect_usage({"random": "dict"})
    assert result is None


def test_auto_detect_usage_returns_none_for_string() -> None:
    """auto_detect_usage should return None for a plain string."""
    from llm_budget.parsers import auto_detect_usage

    result = auto_detect_usage("just a string")
    assert result is None


def test_auto_detect_usage_returns_none_for_none() -> None:
    """auto_detect_usage should return None for None input."""
    from llm_budget.parsers import auto_detect_usage

    result = auto_detect_usage(None)
    assert result is None


def test_individual_parsers_return_none() -> None:
    """Each individual parser stub should return None for any input."""
    from llm_budget.parsers.anthropic import parse_anthropic_response
    from llm_budget.parsers.gemini import parse_gemini_response
    from llm_budget.parsers.openai import parse_openai_response

    mock_response = {"model": "test", "usage": {"tokens": 100}}
    assert parse_openai_response(mock_response) is None
    assert parse_anthropic_response(mock_response) is None
    assert parse_gemini_response(mock_response) is None


def test_no_import_cycles() -> None:
    """Verify the full decorator + registry + parsers wiring has no import cycles.

    Force-reimport all modules to detect circular dependencies.
    """
    modules_to_check = [
        "llm_budget",
        "llm_budget.decorator",
        "llm_budget.exceptions",
        "llm_budget.pricing",
        "llm_budget.store",
        "llm_budget.rate_limiter",
        "llm_budget.reporter",
        "llm_budget.parsers",
        "llm_budget.parsers.openai",
        "llm_budget.parsers.anthropic",
        "llm_budget.parsers.gemini",
    ]

    # Remove all llm_budget modules from cache
    to_remove = [key for key in sys.modules if key.startswith("llm_budget")]
    for key in to_remove:
        del sys.modules[key]

    # Re-import everything — will raise ImportError on circular deps
    for mod in modules_to_check:
        importlib.import_module(mod)


def test_full_wiring_decorator_with_registry_and_store(tmp_db_path: str) -> None:
    """End-to-end: decorator + registry + store + reporter all instantiate together."""
    from llm_budget import CostReporter, PricingRegistry, UsageStore, track_costs

    registry = PricingRegistry()
    registry.register_model("gpt-4o", 0.000005, 0.000015)

    store = UsageStore(db_path=tmp_db_path)
    reporter = CostReporter()

    @track_costs(project="e2e-test", model="gpt-4o")
    def call_llm(prompt: str) -> dict[str, Any]:
        return {
            "model": "gpt-4o",
            "choices": [{"message": {"content": "Response"}}],
            "usage": {"prompt_tokens": 50, "completion_tokens": 25},
        }

    result = call_llm("Test prompt")
    assert result["model"] == "gpt-4o"

    cost = registry.get_cost("gpt-4o", input_tokens=50, output_tokens=25)
    assert cost > 0

    store.log_usage("e2e-test", "gpt-4o", 50, 25, cost)
    reporter.report_call("gpt-4o", 50, 25, cost)
    reporter.report_session()


def test_default_registry_importable() -> None:
    """``from llm_budget import default_registry`` works and has models loaded."""
    from llm_budget import default_registry

    assert default_registry is not None
    assert len(default_registry.list_models()) > 0


def test_default_registry_has_builtin_models() -> None:
    """default_registry ships with pricing for well-known models."""
    from llm_budget import default_registry

    assert default_registry.has_model("gpt-4o") is True


def test_default_registry_cost_calculation() -> None:
    """default_registry.get_cost returns the expected value for builtin pricing."""
    from llm_budget import default_registry

    # gpt-4o builtin: input 2.5e-06, output 10.0e-06
    cost = default_registry.get_cost("gpt-4o", 1000, 500)
    expected = 1000 * 2.5e-06 + 500 * 10.0e-06  # 0.0025 + 0.005 = 0.0075
    assert cost == approx(expected)


def test_pricing_registry_with_decorator() -> None:
    """A separate PricingRegistry can compute cost for the model the decorator tracks."""
    from llm_budget import PricingRegistry, track_costs

    registry = PricingRegistry()
    registry.register_model("gpt-4o", 2.5e-06, 10.0e-06)

    @track_costs(project="reg-test", model="gpt-4o")
    def call_llm() -> dict[str, Any]:
        return {
            "model": "gpt-4o",
            "choices": [{"message": {"content": "Hi"}}],
            "usage": {"prompt_tokens": 200, "completion_tokens": 100},
        }

    result = call_llm()
    assert result["model"] == "gpt-4o"

    cost = registry.get_cost("gpt-4o", input_tokens=200, output_tokens=100)
    expected = 200 * 2.5e-06 + 100 * 10.0e-06
    assert cost == approx(expected)
    assert cost > 0


def test_prefix_matching_end_to_end() -> None:
    """Versioned model name resolves via prefix matching and returns non-zero cost."""
    from llm_budget import PricingRegistry

    registry = PricingRegistry()
    cost = registry.get_cost("gpt-4o-2024-08-06", 1000, 500)
    assert cost > 0


def test_unknown_model_warning_integration() -> None:
    """Querying a totally unknown model emits PricingMatrixOutdatedWarning."""
    from llm_budget import PricingMatrixOutdatedWarning, PricingRegistry

    registry = PricingRegistry()

    with pytest.warns(PricingMatrixOutdatedWarning):
        cost = registry.get_cost("totally-unknown-model-xyz", 100, 50)

    assert cost == 0.0


def test_fallback_pricing_end_to_end() -> None:
    """Registry with fallback pricing uses it for unknown models."""
    from llm_budget import PricingRegistry

    registry = PricingRegistry()
    registry.set_fallback_pricing(1e-05, 2e-05)

    cost = registry.get_cost("my-custom-model", 1000, 500)
    expected = 1000 * 1e-05 + 500 * 2e-05  # 0.01 + 0.01 = 0.02
    assert cost == approx(expected)
    assert cost > 0
